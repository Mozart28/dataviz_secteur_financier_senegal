# ============================================================
#  pages/structure/callbacks.py — Structure & Opérationnel
#  Objectifs : A2, A3, B4, C1, C2, C3
# ============================================================

import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, callback

from config import T, MONO, GROUPE_COLORS, plotly_base, empty_fig
from data import get_dataframe, agg
from components.kpi_card import kpi_card


def gc(g): return GROUPE_COLORS.get(g, T["muted"])


def _filtered(df, groupe):
    if groupe and groupe != "tous":
        return df[df["Goupe_Bancaire"] == groupe]
    return df


# ── KPI Row ──────────────────────────────────────────────────

@callback(
    Output("str-kpis", "children"),
    Input("str-dropdown-annee", "value"),
    Input("str-dropdown-groupe", "value"),
)
def cb_kpis(annee, groupe):
    df  = get_dataframe()
    d   = _filtered(df[df["ANNEE"] == annee], groupe)
    d_all = _filtered(df, groupe)

    nb_banques  = d["Sigle"].nunique()
    tot_agences = d["AGENCE"].sum() if "AGENCE" in d.columns else None
    tot_comptes = d["COMPTE"].sum() if "COMPTE" in d.columns else None
    tot_eff     = d["EFFECTIF"].sum() if "EFFECTIF" in d.columns else None
    tot_emploi  = d["EMPLOI"].sum() if "EMPLOI" in d.columns else None

    prod = None
    if tot_comptes and tot_eff and tot_eff > 0:
        prod = tot_comptes / tot_eff

    return [
        kpi_card("Banques",          nb_banques,      highlight=True),
        kpi_card("Agences totales",  tot_agences or 0),
        kpi_card("Comptes gérés",    tot_comptes or 0),
        kpi_card("Effectif total",   tot_eff or 0),
        kpi_card("Productivité",     prod or 0,       unit="cptes/emp"),
    ]


# ── A2 : Évolution réseau & personnel ────────────────────────

@callback(
    Output("str-graph-reseau-evol", "figure"),
    Input("str-dropdown-groupe", "value"),
)
def cb_reseau_evol(groupe):
    df = get_dataframe()
    d  = _filtered(df, groupe).copy()

    annees = sorted(d["ANNEE"].dropna().unique().tolist())
    agences  = []
    effectifs = []

    for y in annees:
        dy = d[d["ANNEE"] == y]
        agences.append(dy["AGENCE"].sum() if "AGENCE" in dy.columns else np.nan)
        effectifs.append(dy["EFFECTIF"].sum() if "EFFECTIF" in dy.columns else np.nan)

    if not any(not np.isnan(v) for v in agences):
        return empty_fig("Données AGENCE non disponibles")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=annees, y=agences, name="Agences",
        marker_color=T["accent"], opacity=0.85,
        yaxis="y1",
        hovertemplate="<b>Agences</b> %{x}<br>%{y:.0f}<extra></extra>",
    ))

    if any(not np.isnan(v) for v in effectifs):
        fig.add_trace(go.Scatter(
            x=annees, y=effectifs, name="Effectif",
            mode="lines+markers",
            line=dict(color=T["green"], width=2.5),
            marker=dict(size=8, color=T["green"], line=dict(color=T["bg"], width=1.5)),
            yaxis="y2",
            hovertemplate="<b>Effectif</b> %{x}<br>%{y:.0f} employés<extra></extra>",
        ))

    fig.update_layout(**plotly_base(
        yaxis_title="Nombre d'agences",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=9, color=T["muted"]), bgcolor="rgba(0,0,0,0)"),
    ))
    fig.update_layout(
        yaxis=dict(title=dict(text="Agences", font=dict(size=9, color=T["accent"]))),
        yaxis2=dict(
            title=dict(text="Effectif", font=dict(size=9, color=T["green"])),
            overlaying="y", side="right", showgrid=False,
            tickfont=dict(size=9, color=T["green"]),
        ),
        bargap=0.3,
    )
    return fig


# ── A3 : Comptes par groupe bancaire ─────────────────────────

@callback(
    Output("str-graph-comptes-groupe", "figure"),
    Input("str-dropdown-annee", "value"),
)
def cb_comptes_groupe(annee):
    df = get_dataframe()
    d  = df[df["ANNEE"] == annee]

    if "COMPTE" not in d.columns:
        return empty_fig("Colonne COMPTE non disponible")

    grp = d.groupby("Goupe_Bancaire")["COMPTE"].sum().reset_index()
    grp = grp[grp["COMPTE"] > 0].sort_values("COMPTE", ascending=True)

    if grp.empty:
        return empty_fig()

    colors = [gc(g) for g in grp["Goupe_Bancaire"]]
    total  = grp["COMPTE"].sum()
    pcts   = (grp["COMPTE"] / total * 100).round(1)

    fig = go.Figure(go.Bar(
        x=grp["COMPTE"] / 1e6,
        y=grp["Goupe_Bancaire"],
        orientation="h",
        marker=dict(color=colors, line=dict(color=T["bg"], width=1)),
        text=[f"{v:.1f}M  ({p}%)" for v, p in zip(grp["COMPTE"] / 1e6, pcts)],
        textposition="outside",
        textfont=dict(size=9, color=T["muted"], family=MONO),
        hovertemplate="<b>%{y}</b><br>%{x:.2f}M comptes (%{text})<extra></extra>",
    ))

    fig.update_layout(**plotly_base(xaxis_title="Millions de comptes"))
    fig.update_layout(
        xaxis=dict(title=dict(text="Millions de comptes",
                              font=dict(size=9, color=T["muted"]))),
        yaxis=dict(tickfont=dict(size=9, color=T["muted"], family=MONO)),
        margin=dict(r=120),
    )
    return fig


# ── B4 : Capitalisation Continentaux vs Régionaux ────────────

@callback(
    Output("str-graph-capitalisation", "figure"),
    Input("str-dropdown-annee", "value"),
)
def cb_capitalisation(annee):
    df = get_dataframe()

    annees = sorted(df["ANNEE"].dropna().unique().tolist())
    fig = go.Figure()

    for grp in df["Goupe_Bancaire"].dropna().unique():
        dg = df[df["Goupe_Bancaire"] == grp].groupby("ANNEE")

        fp_vals   = []
        bil_vals  = []
        ratio_vals = []

        for y in annees:
            if y in dg.groups:
                dy = dg.get_group(y)
                fp  = dy["FONDS.PROPRE"].sum() if "FONDS.PROPRE" in dy.columns else 0
                bil = dy["BILAN"].sum()         if "BILAN"       in dy.columns else 0
                ratio_vals.append(fp / bil * 100 if bil > 0 else np.nan)
            else:
                ratio_vals.append(np.nan)

        fig.add_trace(go.Scatter(
            x=annees, y=ratio_vals,
            name=grp.replace("Groupes ", ""),
            mode="lines+markers",
            line=dict(color=gc(grp), width=2.5),
            marker=dict(size=8, color=gc(grp), line=dict(color=T["bg"], width=1.5)),
            hovertemplate=f"<b>{grp}</b> %{{x}}<br>FP/Bilan : %{{y:.1f}}%<extra></extra>",
        ))

    # Ligne référence BCEAO 8%
    fig.add_hline(y=8, line_dash="dot", line_color=T["red"], line_width=1,
                  annotation_text="Seuil BCEAO 8%",
                  annotation_font=dict(size=8, color=T["red"], family=MONO),
                  annotation_position="right")

    fig.update_layout(**plotly_base(yaxis_title="Fonds Propres / Bilan (%)"))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=9, color=T["muted"]), bgcolor="rgba(0,0,0,0)"),
    )
    return fig


# ── C1 : Évolution EMPLOI ─────────────────────────────────────

@callback(
    Output("str-graph-emploi", "figure"),
    Input("str-dropdown-groupe", "value"),
)
def cb_emploi(groupe):
    df = get_dataframe()
    d  = _filtered(df, groupe)

    if "EMPLOI" not in d.columns:
        return empty_fig("Colonne EMPLOI non disponible")

    annees = sorted(d["ANNEE"].dropna().unique().tolist())

    # EMPLOI = dépôts engagés / crédits accordés (ratio)
    # Ici on trace le total EMPLOI par année (agrégé secteur)
    emploi_vals = []
    ressources_vals = []
    for y in annees:
        dy = d[d["ANNEE"] == y]
        emploi_vals.append(dy["EMPLOI"].sum() if dy["EMPLOI"].notna().any() else np.nan)
        if "RESSOURCES" in dy.columns:
            ressources_vals.append(dy["RESSOURCES"].sum() if dy["RESSOURCES"].notna().any() else np.nan)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=annees, y=[v / 1e9 if not np.isnan(v) else np.nan for v in emploi_vals],
        name="Emplois (crédits)", mode="lines+markers",
        line=dict(color=T["accent"], width=2.5),
        marker=dict(size=8, color=T["accent"], line=dict(color=T["bg"], width=1.5)),
        hovertemplate="<b>Emplois</b> %{x}<br>%{y:.2f} Mds FCFA<extra></extra>",
        fill="tozeroy", fillcolor=f"rgba(88,166,255,0.08)",
    ))

    if any(not np.isnan(v) for v in ressources_vals):
        fig.add_trace(go.Scatter(
            x=annees, y=[v / 1e9 if not np.isnan(v) else np.nan for v in ressources_vals],
            name="Ressources (dépôts)", mode="lines+markers",
            line=dict(color=T["green"], width=2.5, dash="dot"),
            marker=dict(size=8, color=T["green"], line=dict(color=T["bg"], width=1.5)),
            hovertemplate="<b>Ressources</b> %{x}<br>%{y:.2f} Mds FCFA<extra></extra>",
        ))

    fig.update_layout(**plotly_base(yaxis_title="Milliards FCFA"))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=9, color=T["muted"]), bgcolor="rgba(0,0,0,0)"),
    )
    return fig


# ── C2 : Productivité du personnel ───────────────────────────

@callback(
    Output("str-graph-productivite", "figure"),
    Input("str-dropdown-annee", "value"),
    Input("str-dropdown-groupe", "value"),
    Input("str-dropdown-productivite", "value"),
)
def cb_productivite(annee, groupe, metrique):
    df = get_dataframe()
    d  = _filtered(df[df["ANNEE"] == annee], groupe).copy()

    if "EFFECTIF" not in d.columns or d["EFFECTIF"].sum() == 0:
        return empty_fig("Données EFFECTIF non disponibles")

    if metrique == "compte_eff":
        if "COMPTE" not in d.columns:
            return empty_fig("Colonne COMPTE non disponible")
        d["RATIO"] = d["COMPTE"] / d["EFFECTIF"].replace(0, np.nan)
        titre_y    = "Comptes par employé"
        fmt        = ".0f"
    else:
        d["RATIO"] = d["BILAN"] / d["EFFECTIF"].replace(0, np.nan) / 1e6
        titre_y    = "Bilan par employé (M FCFA)"
        fmt        = ".1f"

    d = d.dropna(subset=["RATIO"]).sort_values("RATIO", ascending=True)
    if d.empty:
        return empty_fig()

    mediane = d["RATIO"].median()
    colors  = [T["green"] if v >= mediane else T["accent"]
               for v in d["RATIO"]]

    fig = go.Figure(go.Bar(
        x=d["RATIO"], y=d["Sigle"],
        orientation="h",
        marker=dict(color=colors, line=dict(color=T["bg"], width=0.5)),
        text=[f"{v:{fmt}}" for v in d["RATIO"]],
        textposition="outside",
        textfont=dict(size=9, color=T["muted"], family=MONO),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}<extra></extra>",
    ))

    fig.add_vline(x=mediane, line_dash="dot", line_color=T["red"], line_width=1.5,
                  annotation_text=f"Médiane {mediane:{fmt}}",
                  annotation_font=dict(size=8, color=T["red"], family=MONO),
                  annotation_position="top right")

    fig.update_layout(**plotly_base(xaxis_title=titre_y))
    fig.update_layout(
        yaxis=dict(tickfont=dict(size=9, color=T["muted"], family=MONO)),
        margin=dict(r=80),
    )
    return fig


# ── C3 / E4 : Scatter Agences vs Bilan + régression ──────────

@callback(
    Output("str-graph-scatter-agences", "figure"),
    Input("str-dropdown-annee", "value"),
    Input("str-dropdown-groupe", "value"),
)
def cb_scatter_agences(annee, groupe):
    df = get_dataframe()
    d  = _filtered(df[df["ANNEE"] == annee], groupe).copy()

    if "AGENCE" not in d.columns:
        return empty_fig("Colonne AGENCE non disponible")

    d = d[["Sigle", "Goupe_Bancaire", "AGENCE", "BILAN"]].dropna()
    d = d[(d["AGENCE"] > 0) & (d["BILAN"] > 0)]
    if d.empty:
        return empty_fig()

    xs = d["AGENCE"].values
    ys = d["BILAN"].values / 1e9   # Mds FCFA

    # Régression linéaire
    coeffs   = np.polyfit(xs, ys, 1)
    x_line   = np.linspace(xs.min(), xs.max(), 100)
    y_line   = np.polyval(coeffs, x_line)
    r2       = np.corrcoef(xs, ys)[0, 1] ** 2

    colors = [gc(g) for g in d["Goupe_Bancaire"]]

    fig = go.Figure()

    # Points
    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="markers+text",
        text=d["Sigle"],
        textposition="top center",
        textfont=dict(size=8, color=T["muted"], family=MONO),
        marker=dict(size=10, color=colors,
                    line=dict(color=T["bg"], width=1.5), opacity=0.85),
        hovertemplate="<b>%{text}</b><br>Agences : %{x}<br>Bilan : %{y:.1f} Mds<extra></extra>",
        name="Banques",
    ))

    # Droite de régression
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode="lines",
        line=dict(color=T["accent"], width=2, dash="dash"),
        name=f"Régression (R²={r2:.2f})",
        hoverinfo="skip",
    ))

    # Annotation R²
    fig.add_annotation(
        x=0.02, y=0.97, xref="paper", yref="paper",
        text=f"R² = {r2:.3f}",
        showarrow=False,
        font=dict(size=11, color=T["accent"], family=MONO),
        bgcolor=T["card2"], bordercolor=T["accent"], borderwidth=1,
        borderpad=6,
    )

    fig.update_layout(**plotly_base(
        xaxis_title="Nombre d'agences",
        yaxis_title="Total Bilan (Mds FCFA)",
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=9, color=T["muted"]), bgcolor="rgba(0,0,0,0)"),
    )
    return fig
