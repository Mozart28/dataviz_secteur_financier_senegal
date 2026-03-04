# ============================================================
#  pages/vue_marche/callbacks.py — Callbacks Vue Marché
#  Avec annotations intelligentes sur tous les graphiques.
# ============================================================

import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, callback

from config import T, MONO, GROUPE_COLORS, plotly_base, empty_fig
from data import get_dataframe, agg, best_col
from components.kpi_card import kpi_card


def gc(g): return GROUPE_COLORS.get(g, T["muted"])


# ── KPI Cards ─────────────────────────────────────────────────

@callback(Output("vm-kpis", "children"), Input("vm-slider", "value"))
def cb_kpis(range_val):
    start, end = range_val
    df = get_dataframe()
    d  = df[df["ANNEE"] == end]
    dp = df[df["ANNEE"] == end - 1] if (end - 1) in df["ANNEE"].values else None
    def p(*c): return agg(dp, *c) if dp is not None else None
    return [
        kpi_card("Total Bilan",          agg(d, "BILAN"),                       p("BILAN"),                highlight=True),
        kpi_card("Produit Net Bancaire",  agg(d, "PRODUIT.NET.BANCAIRE"),        p("PRODUIT.NET.BANCAIRE"), highlight=True),
        kpi_card("Résultat Net",          agg(d, "RESULTAT.NET"),                p("RESULTAT.NET"),         highlight=True),
        kpi_card("Fonds Propres",         agg(d, "FONDS.PROPRE", "CAPITAUX.PROPRES.ET.RESSOURCES.ASSIMILÉES"), p("FONDS.PROPRE")),
        kpi_card("Banques Actives",       float(d["Sigle"].nunique()), None, unit="établissements"),
    ]


# ── Évolution sectorielle ─────────────────────────────────────

@callback(
    Output("vm-evolution", "figure"),
    Input("vm-slider",     "value"),
    Input("vm-indic",      "value"),
)
def cb_evolution(range_val, indic):
    start, end = range_val
    df   = get_dataframe()
    cols = {"pnb": ["PRODUIT.NET.BANCAIRE"], "bilan": ["BILAN"], "rn": ["RESULTAT.NET"]}.get(indic, ["PRODUIT.NET.BANCAIRE"])
    annees = sorted(df["ANNEE"].dropna().unique().tolist())

    all_rows = [(int(y), agg(df[df["ANNEE"] == y], *cols)) for y in annees]
    all_rows = [(y, v) for y, v in all_rows if v]
    if not all_rows:
        return empty_fig()

    xs_all = [r[0] for r in all_rows]
    ys_all = [r[1] / 1000 for r in all_rows]
    sel    = [(y, v) for y, v in zip(xs_all, ys_all) if start <= y <= end]

    fig = go.Figure()

    # Courbe complète grise
    fig.add_trace(go.Scatter(
        x=xs_all, y=ys_all, mode="lines",
        line=dict(color=T["border"], width=1.5, dash="dot"),
        showlegend=False, hoverinfo="skip",
    ))

    # Zone sélectionnée
    if sel:
        xs_s = [r[0] for r in sel]
        ys_s = [r[1] for r in sel]
        fig.add_trace(go.Scatter(
            x=xs_s, y=ys_s, fill="tozeroy",
            fillcolor="rgba(240,180,41,0.12)",
            line=dict(color=T["accent"], width=2.5),
            mode="lines+markers",
            marker=dict(size=8, color=T["accent"], line=dict(color=T["bg"], width=2)),
            hovertemplate="<b>%{x}</b><br>%{y:,.1f} Mds FCFA<extra></extra>",
        ))

    # ── Annotations intelligentes ─────────────────────────────
    if len(ys_all) >= 2:
        # 1. Pic historique
        max_y   = max(ys_all)
        max_x   = xs_all[ys_all.index(max_y)]
        fig.add_annotation(
            x=max_x, y=max_y,
            text=f"▲ Pic : {max_y:.0f} Mds",
            showarrow=True, arrowhead=2, arrowcolor=T["accent"],
            arrowwidth=1.5, ax=0, ay=-32,
            font=dict(size=9, color=T["accent"], family=MONO),
            bgcolor="rgba(240,180,41,0.12)", bordercolor=T["accent"],
            borderwidth=1, borderpad=4,
        )

        # 2. Année COVID 2020 si présente
        if 2020 in xs_all:
            y_covid = ys_all[xs_all.index(2020)]
            fig.add_annotation(
                x=2020, y=y_covid,
                text="COVID-19",
                showarrow=True, arrowhead=2, arrowcolor=T["red"],
                arrowwidth=1.5, ax=30, ay=-30,
                font=dict(size=8, color=T["red"], family=MONO),
                bgcolor=f"rgba({int(T['red'][1:3],16)},{int(T['red'][3:5],16)},{int(T['red'][5:7],16)},0.10)",
                bordercolor=T["red"], borderwidth=1, borderpad=3,
            )

        # 3. Plus forte progression YoY
        if len(ys_all) > 1:
            growths = [(xs_all[i], (ys_all[i]-ys_all[i-1])/ys_all[i-1]*100)
                       for i in range(1, len(ys_all)) if ys_all[i-1] > 0]
            if growths:
                best_growth = max(growths, key=lambda x: x[1])
                if best_growth[1] > 5:  # n'annoter que si > 5%
                    bx = best_growth[0]
                    by = ys_all[xs_all.index(bx)]
                    fig.add_annotation(
                        x=bx, y=by,
                        text=f"+{best_growth[1]:.0f}%",
                        showarrow=False, ax=0, ay=0,
                        font=dict(size=9, color=T["green"], family=MONO),
                        bgcolor="rgba(63,185,80,0.12)",
                        bordercolor=T["green"], borderwidth=1, borderpad=3,
                        yshift=20,
                    )

    # Délimiteurs plage
    fig.add_vline(x=start, line_dash="dot", line_color=T["blue"], line_width=1.5)
    if end != start:
        fig.add_vline(x=end, line_dash="dot", line_color=T["blue"], line_width=1.5)

    fig.update_layout(**plotly_base(
        yaxis_title="Milliards FCFA", showlegend=False, hovermode="x unified",
    ))
    return fig


# ── Classement Top 8 ─────────────────────────────────────────

@callback(
    Output("vm-top",       "figure"),
    Output("vm-top-label", "children"),
    Input("vm-slider",     "value"),
)
def cb_top(range_val):
    start, end = range_val
    df  = get_dataframe()
    d   = df[(df["ANNEE"] >= start) & (df["ANNEE"] <= end)]
    col = best_col(d)
    if not col:
        return empty_fig("Aucune donnée sur cette période"), ""

    top8 = (
        d.groupby(["Sigle", "Goupe_Bancaire"])[col]
        .sum().reset_index()
        .query(f"`{col}` > 0")
        .nlargest(8, col)
        .sort_values(col, ascending=False)
    )
    if top8.empty:
        return empty_fig("Aucune donnée"), ""

    vals   = top8[col] / 1000
    max_v  = vals.max()

    # ── Couleurs avec dégradé selon le rang ───────────────────
    base_colors = [gc(g) for g in top8["Goupe_Bancaire"]]
    # Opacité décroissante du 1er au 8e
    opacities = [1.0, 0.88, 0.78, 0.68, 0.60, 0.52, 0.46, 0.40]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=vals, y=top8["Sigle"],
        orientation="h",
        marker=dict(
            color=base_colors,
            opacity=opacities[:len(top8)],
            line=dict(width=0),
        ),
        text=[f"{v:.1f}" for v in vals],
        textposition="outside",
        textfont=dict(size=10, color=T["muted"], family=MONO),
        hovertemplate="<b>%{y}</b><br>%{x:,.1f} Mds FCFA<extra></extra>",
    ))

    # ── Annotation N°1 ────────────────────────────────────────
    top_banque = top8["Sigle"].iloc[0]
    top_val    = vals.iloc[0]
    fig.add_annotation(
        x=top_val, y=top_banque,
        text="🏆 N°1",
        showarrow=False,
        xanchor="left", xshift=6,
        font=dict(size=10, color=T["accent"], family=MONO),
    )

    # ── Part relative annotée sur la barre du leader ──────────
    total = vals.sum()
    if total > 0:
        pct_leader = top_val / total * 100
        fig.add_annotation(
            x=top_val / 2, y=top_banque,
            text=f"{pct_leader:.0f}% du total",
            showarrow=False,
            font=dict(size=8, color=T["bg"], family=MONO),
            bgcolor="rgba(0,0,0,0)",
        )

    # Légende groupes
    for g, c in GROUPE_COLORS.items():
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
            marker=dict(size=8, color=c, symbol="square"),
            name=g.replace("Groupes ", ""), showlegend=True))

    lbl    = "PNB" if "BANCAIRE" in col else "Bilan"
    period = f"{start}–{end}" if start != end else str(end)

    layout = plotly_base(
        xaxis_title=f"{lbl} (Mds FCFA)", bargap=0.25, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=9, color=T["muted"]), bgcolor="rgba(0,0,0,0)"),
    )
    layout["yaxis"] = dict(
        gridcolor=T["border"], tickfont=dict(size=11),
        showline=False, autorange="reversed",
    )
    fig.update_layout(**layout)
    return fig, f"Indicateur : {lbl} · Top 8 · {period}"


# ── Répartition par groupe ────────────────────────────────────

@callback(Output("vm-groupes", "figure"), Input("vm-slider", "value"))
def cb_groupes(range_val):
    start, end = range_val
    df  = get_dataframe()
    d   = df[(df["ANNEE"] >= start) & (df["ANNEE"] <= end)]
    col = best_col(d)
    if not col:
        return empty_fig()

    grp = d.groupby("Goupe_Bancaire")[col].sum().reset_index().query(f"`{col}` > 0")
    if grp.empty:
        return empty_fig()

    labels = [g.replace("Groupes ", "") for g in grp["Goupe_Bancaire"]]
    colors = [gc(g) for g in grp["Goupe_Bancaire"]]

    fig = go.Figure(go.Pie(
        labels=labels, values=grp[col], hole=0.62,
        marker=dict(colors=colors, line=dict(color=T["bg"], width=3)),
        textinfo="percent+label",
        textfont=dict(size=10, family=MONO),
        direction="clockwise", sort=True,
        hovertemplate="<b>%{label}</b><br>%{percent}<br>%{value:,.0f} M FCFA<extra></extra>",
    ))

    # Groupe dominant annoté au centre
    dominant = grp.loc[grp[col].idxmax(), "Goupe_Bancaire"].replace("Groupes ", "")
    pct_dom  = grp[col].max() / grp[col].sum() * 100

    base = {k: v for k, v in plotly_base().items() if k not in ("xaxis", "yaxis")}
    base.update(
        showlegend=False,
        annotations=[dict(
            text=(
                f'<span style="font-size:14px;font-weight:700;color:{T["text"]}">{dominant}</span>'
                f'<br><span style="font-size:11px;color:{T["accent"]};font-weight:600">{pct_dom:.0f}%</span>'
                f'<br><span style="font-size:8px;color:{T["muted"]}">DOMINANT</span>'
            ),
            x=0.5, y=0.5, showarrow=False, font=dict(family=MONO),
        )],
    )
    fig.update_layout(**base)
    return fig


# ── Scatter PNB vs Résultat Net ───────────────────────────────

@callback(Output("vm-scatter", "figure"), Input("vm-slider", "value"))
def cb_scatter(range_val):
    start, end = range_val
    df   = get_dataframe()
    d    = df[df["ANNEE"] == end]

    if "AGENCE" not in d.columns or "BILAN" not in d.columns:
        return empty_fig("Données AGENCE / BILAN non disponibles")

    data = d[["Sigle", "Goupe_Bancaire", "AGENCE", "BILAN"]].dropna()
    data = data[(data["AGENCE"] > 0) & (data["BILAN"] > 0)]
    if data.empty:
        return empty_fig()

    xs     = data["AGENCE"].values.astype(float)
    ys     = data["BILAN"].values / 1e9
    colors = [gc(g) for g in data["Goupe_Bancaire"]]

    # Régression linéaire
    coeffs = np.polyfit(xs, ys, 1)
    x_line = np.linspace(xs.min(), xs.max(), 100)
    y_line = np.polyval(coeffs, x_line)
    r2     = float(np.corrcoef(xs, ys)[0, 1] ** 2)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="markers+text", text=data["Sigle"].tolist(),
        textposition="top center",
        textfont=dict(size=8, color=T["muted"], family=MONO),
        marker=dict(size=11, color=colors,
                    line=dict(color=T["bg"], width=1.5), opacity=0.85),
        hovertemplate="<b>%{text}</b><br>Agences : %{x:.0f}<br>Bilan : %{y:.1f} Mds<extra></extra>",
        name="Banques",
    ))

    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode="lines",
        line=dict(color=T["accent"], width=2, dash="dash"),
        name=f"Régression (R²={r2:.2f})",
        hoverinfo="skip",
    ))

    fig.add_annotation(
        x=0.02, y=0.97, xref="paper", yref="paper",
        text=f"R² = {r2:.3f}",
        showarrow=False,
        font=dict(size=11, color=T["accent"], family=MONO),
        bgcolor=T["card2"], bordercolor=T["accent"], borderwidth=1, borderpad=6,
    )

    best_idx = data["BILAN"].idxmax()
    fig.add_annotation(
        x=float(data.loc[best_idx, "AGENCE"]),
        y=float(data.loc[best_idx, "BILAN"]) / 1e9,
        text="Plus grand bilan",
        showarrow=True, arrowhead=2, arrowcolor=T["green"],
        font=dict(size=8, color=T["green"], family=MONO),
        bgcolor=T["card2"], bordercolor=T["green"], borderwidth=1, borderpad=4,
        ax=30, ay=-30,
    )

    fig.update_layout(**plotly_base(
        xaxis_title="Nombre d'agences",
        yaxis_title="Total Bilan (Mds FCFA)",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=9, color=T["muted"]), bgcolor="rgba(0,0,0,0)"),
    ))
    return fig
