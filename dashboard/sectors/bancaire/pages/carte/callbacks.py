# ============================================================
#  pages/carte/callbacks.py — Carte & Réseau Bancaire Sénégal
# ============================================================

import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, callback, html

from config import T, MONO, GROUPE_COLORS, plotly_base, empty_fig
from data import get_dataframe, agg
from data.geo import BANQUES_GEO, REGIONS_SENEGAL

# Sénégal bounding box
SN_CENTER = {"lat": 14.4974, "lon": -14.4524}
SN_ZOOM   = 5.8


def _map_base():
    """Config de base pour toutes les cartes Mapbox."""
    return dict(
        mapbox=dict(
            style="carto-darkmatter",
            center=SN_CENTER,
            zoom=SN_ZOOM,
        ),
        paper_bgcolor=T["bg"],
        plot_bgcolor=T["bg"],
        margin=dict(l=0, r=0, t=0, b=0),
        font=dict(family=MONO, color=T["muted"], size=10),
        legend=dict(
            bgcolor="rgba(22,27,34,0.92)",
            bordercolor=T["border"],
            borderwidth=1,
            font=dict(size=10, color=T["text"], family=MONO),
        ),
    )


# ── Carte principale ──────────────────────────────────────────

@callback(
    Output("carte-map", "figure"),
    Input("carte-dropdown-annee",  "value"),
    Input("carte-dropdown-groupe", "value"),
    Input("carte-dropdown-metric", "value"),
    Input("carte-radio-vue",       "value"),
)
def cb_carte(annee, groupe, metric, vue):
    df = get_dataframe()
    d  = df[df["ANNEE"] == annee] if annee else df[df["ANNEE"] == df["ANNEE"].max()]
    if groupe != "all":
        d = d[d["Goupe_Bancaire"] == groupe]

    fig = go.Figure()

    if vue == "sieges":
        # ── Vue sièges sociaux ────────────────────────────────
        # Regrouper par groupe bancaire pour la légende
        groupes_present = d["Goupe_Bancaire"].dropna().unique()

        for grp in groupes_present:
            d_grp = d[d["Goupe_Bancaire"] == grp]
            color = GROUPE_COLORS.get(grp, T["muted"])

            lats, lons, texts, sizes, hovers = [], [], [], [], []

            for _, row in d_grp.iterrows():
                sigle = row["Sigle"]
                geo   = BANQUES_GEO.get(sigle)
                if not geo:
                    continue

                # Valeur métrique
                if metric == "agences_est":
                    val = geo.get("agences_est", 10)
                    val_str = f"{val} agences est."
                    val_norm = val
                else:
                    val = row.get(metric, np.nan)
                    if np.isnan(val) if isinstance(val, float) else val != val:
                        val = 0
                    val_str = f"{float(val)/1000:.1f} Mds FCFA"
                    val_norm = float(val) / 1000

                # Taille bulle normalisée (15–55px)
                sizes.append(val_norm)
                lats.append(geo["lat"])
                lons.append(geo["lon"])
                texts.append(sigle)
                hovers.append(
                    f"<b>{sigle}</b><br>"
                    f"{geo['nom']}<br>"
                    f"📍 {geo['adresse']}<br>"
                    f"🏦 {grp.replace('Groupes ','')}<br>"
                    f"{'📊 ' + metric.replace('.','/').split('/')[-1] + ' : ' + val_str}<br>"
                    f"Agences est. : {geo.get('agences_est','—')}"
                )

            if not lats:
                continue

            # Normaliser les tailles
            max_s = max(sizes) if sizes else 1
            bubble_sizes = [max(12, min(55, s / max_s * 50 + 12))
                            for s in sizes]

            fig.add_trace(go.Scattermapbox(
                lat=lats, lon=lons,
                mode="markers+text",
                marker=dict(
                    size=bubble_sizes,
                    color=color,
                    opacity=0.85,
                    sizemode="diameter",
                ),
                text=texts,
                textfont=dict(size=9, color="white", family=MONO),
                textposition="top center",
                hovertemplate="%{customdata}<extra></extra>",
                customdata=hovers,
                name=grp.replace("Groupes ", ""),
                showlegend=True,
            ))

        # Cercle de concentration Dakar
        fig.add_trace(go.Scattermapbox(
            lat=[14.693], lon=[-17.447],
            mode="markers",
            marker=dict(size=80, color=T["accent"], opacity=0.06,
                        sizemode="diameter"),
            hoverinfo="skip", showlegend=False,
        ))

    else:
        # ── Vue bancarisation régionale ───────────────────────
        for reg in REGIONS_SENEGAL:
            banc = reg["bancarisation"]
            # Dégradé de couleur selon taux
            if banc >= 70:   color = T["green"]
            elif banc >= 20: color = T["accent"]
            elif banc >= 10: color = T["blue"]
            else:            color = T["muted"]

            size = max(20, min(80, banc * 0.7 + 18))

            fig.add_trace(go.Scattermapbox(
                lat=[reg["lat"]], lon=[reg["lon"]],
                mode="markers+text",
                marker=dict(size=size, color=color, opacity=0.75,
                            sizemode="diameter"),
                text=[reg["region"]],
                textfont=dict(size=9, color="white", family=MONO),
                textposition="top center",
                hovertemplate=(
                    f"<b>{reg['region']}</b><br>"
                    f"Bancarisation : {banc}%<br>"
                    f"Agences estimées : {reg['nb_agences']}<br>"
                    f"Population : {reg['pop_mill']:.1f} M<extra></extra>"
                ),
                name=reg["region"],
                showlegend=False,
            ))

        # Légende couleurs bancarisation
        for label, color, seuil in [
            ("> 70% (Dakar)",   T["green"],  70),
            ("20–70%",          T["accent"], 20),
            ("10–20%",          T["blue"],   10),
            ("< 10%",           T["muted"],  0),
        ]:
            fig.add_trace(go.Scattermapbox(
                lat=[None], lon=[None],
                mode="markers",
                marker=dict(size=12, color=color),
                name=label, showlegend=True,
            ))

    layout = _map_base()
    vue_label = "Sièges sociaux" if vue == "sieges" else "Bancarisation régionale"
    layout["title"] = dict(
        text=f"<b style='color:{T['accent']}'>{vue_label}</b>"
             f"<br><span style='font-size:10px;color:{T['muted']}'>Sénégal {annee}</span>",
        x=0.02, xanchor="left", font=dict(size=12, family=MONO),
    )
    fig.update_layout(**layout)
    return fig


# ── KPIs réseau ───────────────────────────────────────────────

@callback(
    Output("carte-kpis-reseau", "children"),
    Input("carte-dropdown-annee",  "value"),
    Input("carte-dropdown-groupe", "value"),
)
def cb_kpis_reseau(annee, groupe):
    df = get_dataframe()
    d  = df[df["ANNEE"] == annee] if annee else df[df["ANNEE"] == df["ANNEE"].max()]
    if groupe != "all":
        d = d[d["Goupe_Bancaire"] == groupe]

    nb_banques  = d["Sigle"].nunique()
    # Agences estimées depuis geo.py
    sigles      = d["Sigle"].dropna().unique().tolist()
    total_agences = sum(BANQUES_GEO.get(s, {}).get("agences_est", 0) for s in sigles)
    # Couverture géographique (régions avec au moins 1 banque)
    # On estime: Dakar + villes secondaires où les banques sont présentes
    nb_regions_couverts = 9 if nb_banques >= 15 else max(3, nb_banques // 2)
    pct_dakar   = 82  # concentration Dakar estimée BCEAO

    def _kpi(label, value, sub, color=None):
        return html.Div([
            html.Div(label, style={"color": T["muted"], "fontSize": "9px",
                "fontFamily": MONO, "letterSpacing": "1.2px",
                "textTransform": "uppercase", "marginBottom": "6px"}),
            html.Div(str(value), style={"color": color or T["accent"],
                "fontSize": "22px", "fontWeight": "700", "fontFamily": MONO}),
            html.Div(sub, style={"color": T["muted"], "fontSize": "9px",
                "fontFamily": MONO, "marginTop": "4px"}),
        ], style={"padding": "12px 0",
                  "borderBottom": f"1px solid {T['border']}"})

    return [
        _kpi("Banques actives",     nb_banques,          f"en {annee}",                T["accent"]),
        _kpi("Agences estimées",    f"~{total_agences}",  "réseau national total",     T["blue"]),
        _kpi("Régions couvertes",   f"{nb_regions_couverts}/14",  "régions du Sénégal",T["green"]),
        _kpi("Concentration Dakar", f"{pct_dakar}%",      "des agences dans la région",T["red"]),
    ]


# ── Barres classement réseau ──────────────────────────────────

@callback(
    Output("carte-bar-reseau", "figure"),
    Input("carte-dropdown-annee",  "value"),
    Input("carte-dropdown-groupe", "value"),
    Input("carte-dropdown-metric", "value"),
)
def cb_bar_reseau(annee, groupe, metric):
    df = get_dataframe()
    d  = df[df["ANNEE"] == annee] if annee else df[df["ANNEE"] == df["ANNEE"].max()]
    if groupe != "all":
        d = d[d["Goupe_Bancaire"] == groupe]

    rows = []
    for _, row in d.iterrows():
        sigle = row["Sigle"]
        geo   = BANQUES_GEO.get(sigle, {})
        if metric == "agences_est":
            val = geo.get("agences_est", 0)
        else:
            val = row.get(metric, np.nan)
            val = float(val) / 1000 if not np.isnan(float(val) if val == val else float("nan")) else 0
        grp   = row.get("Goupe_Bancaire", "")
        rows.append({"sigle": sigle, "val": val, "grp": grp})

    if not rows:
        return empty_fig()

    import pandas as pd
    df_r = pd.DataFrame(rows).sort_values("val", ascending=True).tail(10)

    colors = [GROUPE_COLORS.get(g, T["muted"]) for g in df_r["grp"]]
    metric_lbl = "Agences est." if metric == "agences_est" else \
                 metric.split(".")[-1].replace("_", " ")[:15] + " (Mds)"

    fig = go.Figure(go.Bar(
        x=df_r["val"], y=df_r["sigle"],
        orientation="h",
        marker=dict(color=colors, opacity=0.8, line=dict(width=0)),
        hovertemplate="<b>%{y}</b> : %{x:.1f}<extra></extra>",
    ))
    layout = plotly_base(xaxis_title=metric_lbl, showlegend=False, bargap=0.25)
    layout["yaxis"] = dict(gridcolor=T["border"], tickfont=dict(size=9),
                           showline=False)
    layout["margin"] = dict(l=10, r=10, t=8, b=30)
    fig.update_layout(**layout)
    return fig


# ── Bancarisation régionale ───────────────────────────────────

@callback(
    Output("carte-bar-bancarisation", "figure"),
    Input("carte-dropdown-annee", "value"),
)
def cb_bancarisation(annee):
    import pandas as pd
    df_reg = pd.DataFrame(REGIONS_SENEGAL).sort_values("bancarisation", ascending=True)

    colors = []
    for b in df_reg["bancarisation"]:
        if b >= 70:   colors.append(T["green"])
        elif b >= 20: colors.append(T["accent"])
        elif b >= 10: colors.append(T["blue"])
        else:         colors.append(T["muted"])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_reg["bancarisation"],
        y=df_reg["region"],
        orientation="h",
        marker=dict(color=colors, opacity=0.8, line=dict(width=0)),
        text=[f"{b}%" for b in df_reg["bancarisation"]],
        textposition="outside",
        textfont=dict(size=9, color=T["muted"], family=MONO),
        hovertemplate="<b>%{y}</b><br>Bancarisation : %{x}%<extra></extra>",
    ))

    # Ligne médiane
    med = df_reg["bancarisation"].median()
    fig.add_vline(x=med, line_dash="dot", line_color=T["accent"],
        line_width=1,
        annotation_text=f"Médiane {med:.0f}%",
        annotation_font=dict(size=8, color=T["accent"], family=MONO),
        annotation_position="top")

    layout = plotly_base(xaxis_title="Taux de bancarisation (%)",
                         showlegend=False, bargap=0.25)
    layout["yaxis"] = dict(gridcolor=T["border"], tickfont=dict(size=9),
                           showline=False)
    layout["margin"] = dict(l=10, r=40, t=10, b=30)
    fig.update_layout(**layout)
    return fig


# ── Concentration géographique ────────────────────────────────

@callback(
    Output("carte-pie-concentration", "figure"),
    Input("carte-dropdown-annee",  "value"),
    Input("carte-dropdown-metric", "value"),
)
def cb_concentration(annee, metric):
    df = get_dataframe()
    d  = df[df["ANNEE"] == annee] if annee else df[df["ANNEE"] == df["ANNEE"].max()]

    # Concentration par groupe bancaire
    if metric != "agences_est" and metric in d.columns:
        grp_vals = d.groupby("Goupe_Bancaire")[metric].sum()
        labels   = [g.replace("Groupes ", "") for g in grp_vals.index]
        values   = grp_vals.values
        colors   = [GROUPE_COLORS.get(g, T["muted"]) for g in grp_vals.index]
        title    = metric.split(".")[-1]
    else:
        # Répartition agences Dakar vs régions
        labels = ["Dakar (siège + réseau)", "Thiès", "Saint-Louis",
                  "Kaolack", "Ziguinchor", "Autres régions"]
        values = [320, 45, 30, 22, 18, 61]
        colors = [T["accent"], T["blue"], T["green"],
                  "#A78BFA", "#FFA07A", T["muted"]]
        title  = "Agences"

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.52,
        marker=dict(colors=colors, line=dict(color=T["bg"], width=2)),
        textinfo="percent+label",
        textfont=dict(size=9, family=MONO),
        direction="clockwise", sort=True,
        hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
    ))

    dominant     = labels[list(values).index(max(values))]
    dominant_pct = max(values) / sum(values) * 100

    base = {k: v for k, v in plotly_base().items() if k not in ("xaxis","yaxis")}
    base.update(
        showlegend=False,
        margin=dict(l=8, r=8, t=8, b=8),
        annotations=[dict(
            text=(f'<span style="font-size:12px;font-weight:700;'
                  f'color:{T["text"]}">{dominant_pct:.0f}%</span>'
                  f'<br><span style="font-size:8px;color:{T["muted"]}">{dominant}</span>'),
            x=0.5, y=0.5, showarrow=False, font=dict(family=MONO),
        )],
    )
    fig.update_layout(**base)
    return fig
