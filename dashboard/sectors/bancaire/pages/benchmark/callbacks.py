# ============================================================
#  pages/benchmark/callbacks.py — Benchmark & Positionnement
# ============================================================

import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, callback, html

from config import T, MONO, GROUPE_COLORS, plotly_base, empty_fig
from data import get_dataframe, compute_ratios, agg

ACTIF_COLS = {
    "CRÉANCES.SUR.LA.CLIENTÈLE":                         "Créances clients",
    "EFFETS.PUBLICS.ET.VALEURS.ASSIMILÉES":               "Titres publics",
    "CAISSE.BANQUE.CENTRALE.CCP":                         "Caisse & BC",
    "CRÉANCES.INTERBANCAIRES.ET.ASSIMILÉES":              "Interbancaire",
    "PARTICIPATIONS.ET.AUTRES.TITRES.DÉTENUS.À.LONG.TERME": "Participations",
    "IMMOBILISATIONS.CORPORELLES":                        "Immobilisations",
    "ACTIONS.ET.AUTRES.TITRES.À.REVENU.VARIABLE":        "Actions",
    "OBLIGATIONS.ET.AUTRES.TITRES.À.REVENU.FIXE":        "Obligations",
}

ALLOC_COLORS = [
    "#F0B429", "#58A6FF", "#3FB950", "#F85149",
    "#A78BFA", "#FFA07A", "#20B2AA", "#DDA0DD",
]


def _position_card(label, value, sub, color=None, highlight=False):
    c = color or T["accent"]
    return html.Div([
        html.Div(label.upper(), style={"color": T["muted"], "fontSize": "9px",
            "letterSpacing": "1.5px", "fontFamily": MONO, "fontWeight": "600",
            "marginBottom": "10px"}),
        html.Div(str(value), style={"color": c, "fontSize": "26px",
            "fontWeight": "700", "fontFamily": MONO, "lineHeight": "1"}),
        html.Div(sub, style={"color": T["muted"], "fontSize": "10px",
            "fontFamily": MONO, "marginTop": "6px"}),
    ], style={
        "background": T["card2"], "padding": "20px 24px",
        "borderTop": f"2px solid {c}" if highlight else "2px solid transparent",
    })


# ── Cartes de positionnement ──────────────────────────────────

@callback(
    Output("bm-position-cards", "children"),
    Input("bm-input-capital",    "value"),
    Input("bm-input-pnb",        "value"),
    Input("bm-dropdown-groupe",  "value"),
    Input("bm-dropdown-annee",   "value"),
)
def cb_position_cards(capital, pnb_cible, groupe, annee):
    if not annee:
        return []

    df = get_dataframe()
    d  = df[df["ANNEE"] == annee]

    nb_total  = d["Sigle"].nunique()
    pnb_vals  = d.groupby("Sigle")["PRODUIT.NET.BANCAIRE"].sum().dropna().sort_values()
    cap_vals  = d.groupby("Sigle")["CAPITAUX.PROPRES.ET.RESSOURCES.ASSIMILÉES"].sum().dropna()

    # Rang estimé par PNB
    rang_pnb = "—"
    quartile  = "—"
    if pnb_cible and len(pnb_vals) > 0:
        rang = int((pnb_vals < pnb_cible).sum()) + 1
        rang_pnb = f"#{nb_total - rang + 1} / {nb_total}"
        pct = (pnb_vals < pnb_cible).mean() * 100
        if pct >= 75:   quartile = "Top 25% (Q4)"
        elif pct >= 50: quartile = "Q3 (50-75%)"
        elif pct >= 25: quartile = "Q2 (25-50%)"
        else:           quartile = "Q1 — Entrée de marché"

    # Part de marché estimée
    pdm = "—"
    total_pnb_secteur = pnb_vals.sum()
    if pnb_cible and total_pnb_secteur > 0:
        pdm = f"{pnb_cible / (total_pnb_secteur + pnb_cible) * 100:.2f}%"

    # Écart vs médiane
    ecart = "—"
    color_ecart = T["muted"]
    if pnb_cible and len(pnb_vals) > 0:
        med = pnb_vals.median()
        diff = pnb_cible - med
        pct_diff = diff / med * 100 if med else 0
        arrow = "▲" if diff >= 0 else "▼"
        ecart = f"{arrow} {abs(pct_diff):.0f}% vs médiane"
        color_ecart = T["green"] if diff >= 0 else T["red"]

    return [
        _position_card("Rang estimé (PNB)",   rang_pnb,  f"sur {nb_total} banques · {annee}", T["accent"], True),
        _position_card("Quartile de marché",  quartile,  "positionnement sectoriel",           T["blue"],   True),
        _position_card("Part de marché est.", pdm,       "PNB / total sectoriel",              T["green"],  True),
        _position_card("Écart vs médiane",    ecart,     f"PNB médian : {pnb_vals.median()/1000:.0f} Mds", color_ecart),
    ]


# ── Graphe positionnement dans le classement ─────────────────

@callback(
    Output("bm-graph-rang",  "figure"),
    Output("bm-rang-label",  "children"),
    Input("bm-input-pnb",       "value"),
    Input("bm-dropdown-groupe", "value"),
    Input("bm-dropdown-annee",  "value"),
)
def cb_rang(pnb_cible, groupe, annee):
    if not annee:
        return empty_fig(), ""

    df = get_dataframe()
    d  = df[df["ANNEE"] == annee]

    pnb_by_bank = (
        d.groupby(["Sigle", "Goupe_Bancaire"])["PRODUIT.NET.BANCAIRE"]
        .sum().reset_index().dropna()
        .sort_values("PRODUIT.NET.BANCAIRE", ascending=True)
    )
    if pnb_by_bank.empty:
        return empty_fig(), ""

    colors = []
    for _, row in pnb_by_bank.iterrows():
        colors.append(GROUPE_COLORS.get(row["Goupe_Bancaire"], T["muted"]))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=pnb_by_bank["PRODUIT.NET.BANCAIRE"] / 1000,
        y=pnb_by_bank["Sigle"],
        orientation="h",
        marker=dict(color=colors, opacity=0.6, line=dict(width=0)),
        name="Banques existantes",
        hovertemplate="<b>%{y}</b><br>PNB : %{x:.1f} Mds<extra></extra>",
    ))

    # Barre de la nouvelle banque
    if pnb_cible:
        fig.add_trace(go.Bar(
            x=[pnb_cible / 1000],
            y=["▶ VOTRE BANQUE"],
            orientation="h",
            marker=dict(color=T["accent"], opacity=1,
                        line=dict(color=T["accent"], width=1)),
            name="Votre banque",
            hovertemplate=f"<b>Votre banque</b><br>PNB cible : {pnb_cible/1000:.1f} Mds<extra></extra>",
        ))

    layout = plotly_base(
        xaxis_title="PNB (Mds FCFA)", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9, color=T["muted"]),
            bgcolor="rgba(0,0,0,0)"),
        bargap=0.2,
    )
    layout["yaxis"] = dict(gridcolor=T["border"], tickfont=dict(size=9),
                           showline=False, autorange="reversed")
    fig.update_layout(**layout)

    nb = len(pnb_by_bank)
    return fig, f"Marché {annee} · {nb} banques actives"


# ── Allocation bilan du groupe de référence ───────────────────

@callback(
    Output("bm-graph-alloc", "figure"),
    Output("bm-alloc-label", "children"),
    Input("bm-dropdown-groupe", "value"),
    Input("bm-dropdown-annee",  "value"),
)
def cb_alloc(groupe, annee):
    if not annee or not groupe:
        return empty_fig(), ""

    df = get_dataframe()
    d  = df[(df["ANNEE"] == annee) & (df["Goupe_Bancaire"] == groupe)]

    vals, labels = [], []
    total = 0
    for col, lbl in ACTIF_COLS.items():
        if col in df.columns:
            v = d[col].sum()
            if v > 0:
                vals.append(v)
                labels.append(lbl)
                total += v

    if not vals:
        return empty_fig("Données de bilan non disponibles"), ""

    fig = go.Figure(go.Pie(
        labels=labels,
        values=vals,
        hole=0.55,
        marker=dict(colors=ALLOC_COLORS[:len(vals)],
                    line=dict(color=T["bg"], width=2)),
        textinfo="percent+label",
        textfont=dict(size=9, family=MONO),
        direction="clockwise", sort=True,
        hovertemplate="<b>%{label}</b><br>%{percent}<br>%{value:,.0f} M FCFA<extra></extra>",
    ))

    # Annotation centre : poste dominant
    dominant_lbl = labels[vals.index(max(vals))]
    dominant_pct = max(vals) / total * 100

    base = {k: v for k, v in plotly_base().items() if k not in ("xaxis","yaxis")}
    base.update(
        showlegend=False,
        margin=dict(l=8, r=8, t=8, b=8),
        annotations=[dict(
            text=(f'<span style="font-size:13px;font-weight:700;color:{T["text"]}">'
                  f'{dominant_pct:.0f}%</span>'
                  f'<br><span style="font-size:8px;color:{T["muted"]}">{dominant_lbl}</span>'),
            x=0.5, y=0.5, showarrow=False, font=dict(family=MONO),
        )],
    )
    fig.update_layout(**base)

    grp_label = groupe.replace("Groupes ", "")
    return fig, f"Allocation moyenne · {grp_label} · {annee}"


# ── Ratios cibles (top quartile) ──────────────────────────────

@callback(
    Output("bm-ratios-cibles", "children"),
    Input("bm-dropdown-groupe", "value"),
    Input("bm-dropdown-annee",  "value"),
    Input("bm-input-capital",   "value"),
    Input("bm-input-pnb",       "value"),
)
def cb_ratios_cibles(groupe, annee, capital, pnb_cible):
    if not annee:
        return []

    df = compute_ratios(get_dataframe())
    d  = df[df["ANNEE"] == annee]

    # Ratios du groupe de référence (Q1 = top 25%)
    d_grp = d[d["Goupe_Bancaire"] == groupe] if groupe else d

    ratios = [
        ("ROA",            "ROA (%)",            "> 1%",   T["accent"], True),
        ("ROE",            "ROE (%)",             "> 15%",  T["blue"],   True),
        ("MARGE_NETTE",    "Marge nette (%)",     "> 30%",  T["green"],  True),
        ("COUT_RISQUE_PCT","Coût du risque (%)",  "< 20%",  T["red"],    False),
    ]

    items = []
    for col, label, bench, color, higher in ratios:
        if col not in d_grp.columns:
            continue
        vals = d_grp[col].dropna()
        if vals.empty:
            continue

        # Valeurs de référence
        top_q  = float(vals.quantile(0.75) if higher else vals.quantile(0.25))
        median = float(vals.median())
        sect_q = float(d[col].dropna().quantile(0.75) if higher else d[col].dropna().quantile(0.25))

        # Valeur simulée si capital et PNB fournis
        sim_val = None
        sim_txt = ""
        if capital and pnb_cible:
            if col == "ROE" and capital > 0:
                # Hypothèse : marge nette sectorielle appliquée au PNB
                mn = float(d["MARGE_NETTE"].dropna().median()) / 100 if "MARGE_NETTE" in d.columns else 0.35
                rn_sim = pnb_cible * mn
                sim_val = rn_sim / capital * 100
                sim_txt = f"Votre estimation : {sim_val:.1f}%"
            elif col == "ROA" and capital > 0:
                mn = float(d["MARGE_NETTE"].dropna().median()) / 100 if "MARGE_NETTE" in d.columns else 0.35
                rn_sim = pnb_cible * mn
                actif_sim = capital * 8  # Levier typique
                sim_val = rn_sim / actif_sim * 100
                sim_txt = f"Votre estimation : {sim_val:.1f}%"

        ok_color = T["green"] if (sim_val and ((higher and sim_val >= top_q) or (not higher and sim_val <= top_q))) else T["red"] if sim_val else T["muted"]

        items.append(html.Div([
            # Label + bench
            html.Div([
                html.Span(label, style={"color": T["text"], "fontFamily": MONO,
                    "fontSize": "12px", "fontWeight": "600"}),
                html.Span(f" · Seuil : {bench}", style={"color": T["muted"],
                    "fontFamily": MONO, "fontSize": "10px"}),
            ], style={"marginBottom": "8px"}),

            # Barre comparative
            html.Div([
                # Médiane
                html.Div([
                    html.Div("Médiane secteur", style={"color": T["muted"],
                        "fontSize": "9px", "fontFamily": MONO, "marginBottom": "3px"}),
                    html.Div(style={"height": "6px", "borderRadius": "3px", "width": "100%",
                        "background": f"linear-gradient(90deg, {T['border']} {min(abs(median)/max(abs(top_q),1)*100,100):.0f}%, transparent 0%)"}),
                    html.Div(f"{median:.1f}%", style={"color": T["muted"],
                        "fontSize": "9px", "fontFamily": MONO, "marginTop": "3px"}),
                ], style={"flex": "1"}),
                html.Div(style={"width": "16px"}),
                # Top groupe
                html.Div([
                    html.Div(f"Top 25% · {groupe.replace('Groupes ','') if groupe else 'secteur'}",
                        style={"color": color, "fontSize": "9px", "fontFamily": MONO, "marginBottom": "3px"}),
                    html.Div(style={"height": "6px", "borderRadius": "3px", "width": "100%",
                        "background": color}),
                    html.Div(f"{top_q:.1f}%", style={"color": color,
                        "fontSize": "10px", "fontFamily": MONO, "fontWeight": "600", "marginTop": "3px"}),
                ], style={"flex": "1"}),
            ], style={"display": "flex", "marginBottom": "6px"}),

            # Estimation simulée
            html.Div(sim_txt, style={"color": ok_color, "fontSize": "10px",
                "fontFamily": MONO, "fontStyle": "italic"}) if sim_txt else html.Div(),

        ], style={"padding": "12px 0", "borderBottom": f"1px solid {T['border']}"}))

    return items


# ── Seuils capital par niveau ─────────────────────────────────

@callback(
    Output("bm-graph-seuils",  "figure"),
    Output("bm-seuils-label",  "children"),
    Input("bm-input-capital",   "value"),
    Input("bm-dropdown-annee",  "value"),
)
def cb_seuils(capital, annee):
    if not annee:
        return empty_fig(), ""

    df = get_dataframe()
    d  = df[df["ANNEE"] == annee]

    # Capital souscrit par banque trié
    cap_data = []
    for _, row in d.iterrows():
        cap = row.get("CAPITAL.SOUSCRIT")
        pnb = row.get("PRODUIT.NET.BANCAIRE")
        grp = row.get("Goupe_Bancaire", "")
        if cap and cap > 0 and pnb and pnb > 0:
            cap_data.append({"banque": row["Sigle"], "capital": cap, "pnb": pnb, "groupe": grp})

    if not cap_data:
        return empty_fig("Données capital non disponibles"), ""

    import pandas as pd
    cap_df = pd.DataFrame(cap_data).sort_values("capital", ascending=True)

    colors = [GROUPE_COLORS.get(g, T["muted"]) for g in cap_df["groupe"]]

    # Surligner la banque utilisateur
    bar_colors = []
    for _, row in cap_df.iterrows():
        bar_colors.append(T["accent"] if capital and abs(row["capital"] - capital) < 1000
                          else GROUPE_COLORS.get(row["groupe"], T["muted"]))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cap_df["capital"] / 1000,
        y=cap_df["banque"],
        orientation="h",
        marker=dict(color=bar_colors, opacity=0.75, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>Capital : %{x:.0f} Mds<extra></extra>",
    ))

    # Ligne capital utilisateur
    if capital:
        fig.add_vline(x=capital/1000, line_dash="solid",
            line_color=T["accent"], line_width=2,
            annotation_text=f"Votre capital : {capital/1000:.0f} Mds",
            annotation_font=dict(size=9, color=T["accent"], family=MONO),
            annotation_position="top")

    # Quartiles
    q1 = cap_df["capital"].quantile(0.25) / 1000
    q3 = cap_df["capital"].quantile(0.75) / 1000
    for qv, ql, qc in [(q1, "Q1", T["muted"]), (q3, "Q3", T["blue"])]:
        fig.add_vline(x=qv, line_dash="dot", line_color=qc, line_width=1,
            annotation_text=ql, annotation_font=dict(size=8, color=qc, family=MONO),
            annotation_position="bottom")

    layout = plotly_base(xaxis_title="Capital souscrit (Mds FCFA)", showlegend=False, bargap=0.2)
    layout["yaxis"] = dict(gridcolor=T["border"], tickfont=dict(size=9),
                           showline=False, autorange="reversed")
    fig.update_layout(**layout)

    return fig, f"Capital souscrit des {len(cap_df)} banques · {annee}"


# ── Recommandations stratégiques ─────────────────────────────

@callback(
    Output("bm-recommandations", "children"),
    Input("bm-input-capital",    "value"),
    Input("bm-input-pnb",        "value"),
    Input("bm-dropdown-groupe",  "value"),
    Input("bm-dropdown-annee",   "value"),
)
def cb_recommandations(capital, pnb_cible, groupe, annee):
    if not annee:
        return []

    df = compute_ratios(get_dataframe())
    d  = df[df["ANNEE"] == annee]
    d_grp = d[d["Goupe_Bancaire"] == groupe] if groupe else d

    recs = []

    # Analyse du positionnement
    pnb_vals = d["PRODUIT.NET.BANCAIRE"].dropna()
    if pnb_cible and len(pnb_vals) > 0:
        pct = (pnb_vals < pnb_cible).mean() * 100
        if pct < 25:
            recs.append(("⚠", T["red"],
                "Positionnement bas",
                f"Avec un PNB cible de {pnb_cible/1000:.0f} Mds, vous vous situez dans le bas du marché. "
                f"Le PNB médian sectoriel est de {pnb_vals.median()/1000:.0f} Mds. "
                "Concentrez-vous sur les créances clientèle et le développement du réseau."))
        elif pct < 50:
            recs.append(("✓", T["accent"],
                "Positionnement intermédiaire",
                f"Vous vous situez dans le second quartile. "
                f"Pour atteindre la médiane ({pnb_vals.median()/1000:.0f} Mds), "
                f"il vous faudrait générer {(pnb_vals.median()-pnb_cible)/1000:.0f} Mds de PNB supplémentaires."))
        else:
            recs.append(("★", T["green"],
                "Positionnement compétitif",
                f"Votre PNB cible vous place dans le top {100-pct:.0f}% du marché. "
                "Focalisez-vous sur l'optimisation des ratios plutôt que la croissance brute."))

    # Analyse capital
    cap_vals = d["CAPITAL.SOUSCRIT"].dropna()
    if capital and len(cap_vals) > 0:
        if capital < cap_vals.quantile(0.25):
            recs.append(("⚠", T["red"],
                "Capital en dessous du Q1",
                f"Votre capital ({capital/1000:.0f} Mds) est inférieur au premier quartile "
                f"({cap_vals.quantile(0.25)/1000:.0f} Mds). "
                "Envisagez une augmentation de capital avant le lancement pour respecter les ratios prudentiels BCEAO."))
        elif capital >= cap_vals.quantile(0.75):
            recs.append(("★", T["green"],
                "Capital solide",
                f"Votre capital ({capital/1000:.0f} Mds) vous place dans le top 25% du secteur. "
                "Vous avez la capacité de soutenir une croissance rapide du bilan."))

    # Allocation recommandée
    grp_label = groupe.replace("Groupes ","") if groupe else "secteur"
    actif_alloc = {}
    total_alloc = 0
    for col, lbl in {
        "CRÉANCES.SUR.LA.CLIENTÈLE": "Créances clients",
        "EFFETS.PUBLICS.ET.VALEURS.ASSIMILÉES": "Titres publics",
        "CAISSE.BANQUE.CENTRALE.CCP": "Caisse & BC",
    }.items():
        if col in d_grp.columns:
            v = d_grp[col].sum()
            if v > 0:
                actif_alloc[lbl] = v
                total_alloc += v
    if actif_alloc and total_alloc > 0:
        alloc_txt = " · ".join([f"{lbl} {v/total_alloc*100:.0f}%"
                                for lbl, v in sorted(actif_alloc.items(), key=lambda x:-x[1])[:3]])
        recs.append(("→", T["blue"],
            f"Allocation bilan type · {grp_label}",
            f"Les banques du groupe {grp_label} allouent en moyenne : {alloc_txt}. "
            "Les créances clients sont le principal moteur de PNB — "
            "priorité au développement commercial dès la première année."))

    # ROE recommandé
    if "ROE" in d_grp.columns:
        roe_q3 = d_grp["ROE"].dropna().quantile(0.75)
        if not np.isnan(roe_q3):
            recs.append(("→", T["accent"],
                "Objectif ROE",
                f"Le top 25% des banques {grp_label} atteint un ROE de {roe_q3:.1f}%. "
                f"La médiane sectorielle est de {d['ROE'].dropna().median():.1f}%. "
                "Un ROE > 15% est le seuil de rentabilité attractive pour les investisseurs."))

    if not recs:
        return html.Div("Renseignez vos paramètres pour obtenir des recommandations.",
            style={"color": T["muted"], "fontFamily": MONO, "fontSize": "12px"})

    return [html.Div([
        html.Div([
            html.Span(icon, style={"fontSize": "16px", "marginRight": "10px"}),
            html.Span(titre, style={"color": color, "fontFamily": MONO,
                "fontSize": "12px", "fontWeight": "600"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
        html.P(texte, style={"color": T["muted"], "fontFamily": MONO,
            "fontSize": "11px", "lineHeight": "1.6", "margin": "0 0 0 26px"}),
    ], style={"padding": "14px 0", "borderBottom": f"1px solid {T['border']}"})
    for icon, color, titre, texte in recs]


# ══════════════════════════════════════════════════════════════
#  MODULE PRÉDICTIF — N+1 · N+2 · N+3
# ══════════════════════════════════════════════════════════════

from data.predictor import predict_banque, SCENARIOS

PRED_COLORS = {
    "pessimiste": "#F85149",
    "central":    "#F0B429",
    "optimiste":  "#3FB950",
}


def _pred_card(label, values_by_scen, future_years, unit="Mds", invert=False):
    """Card résumé avec valeur centrale N+3 et fourchette."""
    central = values_by_scen.get("central", [])
    pess    = values_by_scen.get("pessimiste", [])
    opti    = values_by_scen.get("optimiste", [])
    if not central:
        return html.Div()

    v_c = central[-1]
    v_p = pess[-1]
    v_o = opti[-1]
    scale = 1/1000 if unit == "Mds" else 1

    arrow = "▲" if (v_c > central[0] if len(central) > 1 else True) else "▼"
    a_col = T["green"] if arrow == "▲" else T["red"]
    if invert:
        a_col = T["red"] if arrow == "▲" else T["green"]

    return html.Div([
        html.Div(label, style={"color": T["muted"], "fontSize": "9px",
            "fontFamily": MONO, "letterSpacing": "1.5px",
            "textTransform": "uppercase", "marginBottom": "8px"}),
        html.Div([
            html.Span(f"{v_c*scale:.1f}", style={"color": T["accent"],
                "fontSize": "22px", "fontWeight": "700", "fontFamily": MONO}),
            html.Span(f" {unit}", style={"color": T["muted"], "fontSize": "11px",
                "fontFamily": MONO}),
            html.Span(f" {arrow}", style={"color": a_col, "fontSize": "14px",
                "marginLeft": "6px"}),
        ]),
        html.Div(f"N+3 · {future_years[-1]}", style={"color": T["muted"],
            "fontSize": "9px", "fontFamily": MONO, "marginTop": "4px"}),
        html.Div(
            f"Fourchette : {v_p*scale:.1f} – {v_o*scale:.1f} {unit}",
            style={"color": T["muted"], "fontSize": "9px",
                   "fontFamily": MONO, "marginTop": "2px", "opacity": "0.7"}),
    ], style={"background": T["card2"], "padding": "18px 20px"})


def _pred_graph(res_data, label, unit, scenario, color_hist, future_years,
                invert_trend=False):
    """Graphique historique + projection 3 scénarios avec IC."""
    if not res_data:
        return empty_fig("Données insuffisantes (< 2 points)")

    fig = go.Figure()
    hist_x = res_data["hist_years"]
    hist_y = [v / 1000 if unit == "Mds" else v for v in res_data["hist_values"]]
    scale  = 1/1000 if unit == "Mds" else 1

    # Historique
    fig.add_trace(go.Scatter(
        x=hist_x, y=hist_y,
        mode="lines+markers", name="Historique",
        line=dict(color=color_hist, width=2),
        marker=dict(size=6, color=color_hist, line=dict(color=T["bg"], width=1.5)),
        hovertemplate=f"<b>%{{x}}</b> : %{{y:.2f}} {unit}<extra></extra>",
    ))

    # Ligne de connexion historique → prédiction
    last_hist_y = hist_y[-1] if hist_y else 0
    connect_x   = [hist_x[-1]] if hist_x else []

    scenarios_to_show = (list(SCENARIOS.keys()) if scenario == "all"
                         else [scenario] if scenario in SCENARIOS else ["central"])

    for scen_key in scenarios_to_show:
        scen_vals = [v * scale for v in res_data["scenarios"][scen_key]]
        col       = PRED_COLORS[scen_key]
        lbl       = SCENARIOS[scen_key]["label"]
        dash      = "dot" if scen_key == "pessimiste" else \
                    "solid" if scen_key == "central" else "dash"

        # Connecter depuis le dernier point historique
        fig.add_trace(go.Scatter(
            x=connect_x + future_years,
            y=[last_hist_y] + scen_vals,
            mode="lines+markers", name=lbl,
            line=dict(color=col, width=2, dash=dash),
            marker=dict(size=7, color=col, symbol="diamond",
                        line=dict(color=T["bg"], width=1)),
            hovertemplate=f"<b>{lbl}</b> %{{x}} : %{{y:.2f}} {unit}<extra></extra>",
        ))

        # Annotations valeur N+3
        if scen_vals:
            fig.add_annotation(
                x=future_years[-1], y=scen_vals[-1],
                text=f"{scen_vals[-1]:.1f}",
                showarrow=False, xshift=28,
                font=dict(size=8, color=col, family=MONO),
            )

    # Zone IC (seulement si "all" ou "central")
    if "ci_lower" in res_data and scenario in ("all", "central"):
        ci_lo = [v * scale for v in res_data["ci_lower"]]
        ci_hi = [v * scale for v in res_data["ci_upper"]]
        fig.add_trace(go.Scatter(
            x=future_years + future_years[::-1],
            y=ci_hi + ci_lo[::-1],
            fill="toself",
            fillcolor="rgba(240,180,41,0.07)",
            line=dict(color="rgba(0,0,0,0)"),
            hoverinfo="skip", showlegend=False,
            name="IC 80%",
        ))

    # Ligne verticale séparant historique / prédiction
    if hist_x:
        fig.add_vline(x=hist_x[-1] + 0.5, line_dash="dot",
            line_color=T["border"], line_width=1,
            annotation_text="Prévision →",
            annotation_font=dict(size=8, color=T["muted"], family=MONO),
            annotation_position="top right")

    r2 = res_data["fit"]["r2"]
    fig.update_layout(**plotly_base(
        yaxis_title=unit, showlegend=True, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9, color=T["muted"]),
            bgcolor="rgba(0,0,0,0)"),
        title=dict(
            text=f'<span style="font-size:8px;color:{T["muted"]}">'
                 f'R² = {r2:.2f} · {"Bon" if r2 > 0.7 else "Modéré" if r2 > 0.4 else "Faible"}'
                 f'</span>',
            x=0.99, xanchor="right", y=0.98, yanchor="top",
        ),
    ))
    return fig


# ── Callback : cards résumé ───────────────────────────────────

@callback(
    Output("bm-pred-cards",      "children"),
    Output("bm-pred-fiabilite",  "children"),
    Input("bm-pred-dropdown-banque", "value"),
    Input("bm-pred-scenario",        "value"),
)
def cb_pred_cards(banque, scenario):
    if not banque:
        return [], html.Div()

    df  = get_dataframe()
    res = predict_banque(df, banque, horizon=3)
    fys = res["future_years"]

    cards = []
    if res["pnb"]:
        cards.append(_pred_card("PNB projeté",        res["pnb"]["scenarios"], fys, "Mds"))
    if res["rn"]:
        cards.append(_pred_card("Résultat Net projeté", res["rn"]["scenarios"],  fys, "Mds"))
    if res["pdm"]:
        cards.append(_pred_card("Part de marché",     res["pdm"]["scenarios"],  fys, "%"))
    if res["rang"]:
        cards.append(_pred_card("Rang sectoriel est.", res["rang"]["scenarios"], fys, "",
                                invert=True))

    # Badge fiabilité basé sur R² moyen
    r2_vals = [v["fit"]["r2"] for v in [res["pnb"], res["rn"]]
               if v and "fit" in v]
    r2_avg  = sum(r2_vals) / len(r2_vals) if r2_vals else 0
    r2_col  = T["green"] if r2_avg > 0.7 else T["accent"] if r2_avg > 0.4 else T["red"]
    r2_lbl  = "Fiable" if r2_avg > 0.7 else "Modéré" if r2_avg > 0.4 else "Incertain"
    fiab = html.Div([
        html.Span("FIABILITÉ ", style={"color": T["muted"], "fontSize": "9px",
            "fontFamily": MONO, "letterSpacing": "1px"}),
        html.Span(f"R²={r2_avg:.2f} · {r2_lbl}",
            style={"color": r2_col, "fontSize": "10px",
                   "fontFamily": MONO, "fontWeight": "600"}),
    ])

    return cards, fiab


# ── Callback : graphique PNB ──────────────────────────────────

@callback(
    Output("bm-pred-graph-pnb", "figure"),
    Input("bm-pred-dropdown-banque", "value"),
    Input("bm-pred-scenario",        "value"),
)
def cb_pred_pnb(banque, scenario):
    if not banque: return empty_fig()
    df  = get_dataframe()
    res = predict_banque(df, banque, horizon=3)
    return _pred_graph(res["pnb"], "PNB", "Mds", scenario,
                       T["accent"], res["future_years"])


# ── Callback : graphique RN ───────────────────────────────────

@callback(
    Output("bm-pred-graph-rn", "figure"),
    Input("bm-pred-dropdown-banque", "value"),
    Input("bm-pred-scenario",        "value"),
)
def cb_pred_rn(banque, scenario):
    if not banque: return empty_fig()
    df  = get_dataframe()
    res = predict_banque(df, banque, horizon=3)
    return _pred_graph(res["rn"], "Résultat Net", "Mds", scenario,
                       T["green"], res["future_years"])


# ── Callback : graphique Part de marché ──────────────────────

@callback(
    Output("bm-pred-graph-pdm", "figure"),
    Input("bm-pred-dropdown-banque", "value"),
    Input("bm-pred-scenario",        "value"),
)
def cb_pred_pdm(banque, scenario):
    if not banque: return empty_fig()
    df  = get_dataframe()
    res = predict_banque(df, banque, horizon=3)
    return _pred_graph(res["pdm"], "Part de marché", "%", scenario,
                       T["blue"], res["future_years"])


# ── Callback : graphique Rang ─────────────────────────────────

@callback(
    Output("bm-pred-graph-rang", "figure"),
    Input("bm-pred-dropdown-banque", "value"),
    Input("bm-pred-scenario",        "value"),
)
def cb_pred_rang(banque, scenario):
    if not banque: return empty_fig()
    df  = get_dataframe()
    res = predict_banque(df, banque, horizon=3)
    if not res["rang"]:
        return empty_fig("Données insuffisantes")

    rang_res = res["rang"]
    fys      = res["future_years"]

    fig = go.Figure()

    # Historique rang
    fig.add_trace(go.Scatter(
        x=rang_res["hist_years"], y=rang_res["hist_values"],
        mode="lines+markers", name="Historique",
        line=dict(color=T["muted"], width=2),
        marker=dict(size=6, color=T["muted"]),
        hovertemplate="<b>%{x}</b> : Rang #%{y}<extra></extra>",
    ))

    last_rang = rang_res["hist_values"][-1] if rang_res["hist_values"] else 5
    scenarios_to_show = (list(SCENARIOS.keys()) if scenario == "all"
                         else [scenario] if scenario in SCENARIOS else ["central"])

    for scen_key in scenarios_to_show:
        rangs = rang_res["scenarios"][scen_key]
        col   = PRED_COLORS[scen_key]
        lbl   = SCENARIOS[scen_key]["label"]
        dash  = "dot" if scen_key == "pessimiste" else \
                "solid" if scen_key == "central" else "dash"

        fig.add_trace(go.Scatter(
            x=[rang_res["hist_years"][-1]] + fys if rang_res["hist_years"] else fys,
            y=[last_rang] + rangs,
            mode="lines+markers", name=lbl,
            line=dict(color=col, width=2, dash=dash),
            marker=dict(size=7, color=col, symbol="diamond",
                        line=dict(color=T["bg"], width=1)),
            hovertemplate=f"<b>{lbl}</b> %{{x}} : Rang #%{{y}}<extra></extra>",
        ))
        if rangs:
            fig.add_annotation(x=fys[-1], y=rangs[-1],
                text=f"#{rangs[-1]}", showarrow=False, xshift=22,
                font=dict(size=9, color=col, family=MONO, weight="bold"))

    # Axe Y inversé (rang 1 = meilleur = haut)
    nb_banques = df["Sigle"].nunique()
    layout = plotly_base(yaxis_title="Rang", showlegend=True, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9, color=T["muted"]),
            bgcolor="rgba(0,0,0,0)"))
    layout["yaxis"].update(autorange="reversed",
        tickvals=list(range(1, nb_banques+1, 3)),
        ticktext=[f"#{i}" for i in range(1, nb_banques+1, 3)])

    if rang_res["hist_years"]:
        fig.add_vline(x=rang_res["hist_years"][-1] + 0.5,
            line_dash="dot", line_color=T["border"], line_width=1)

    fig.update_layout(**layout)
    return fig
