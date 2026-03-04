# ============================================================
#  sectors/energie/pages/vue_globale/callbacks.py
# ============================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback

from config import get_theme, plotly_base, MONO
from sectors.energie.data.loader import get_dataframe

T      = get_theme("energie")
ACCENT = T["accent"]
MONTHS = ["Jan","Fév","Mar","Avr","Mai","Jun",
          "Jul","Aoû","Sep","Oct","Nov","Déc"]

COUNTRY_COLORS = {
    "Norway":    "#58A6FF",
    "Brazil":    "#3FB950",
    "India":     "#F0B429",
    "Australia": "#F85149",
}


def _base(**kw):
    return plotly_base("energie", **kw)


def _filtered(pays, mois):
    df = get_dataframe()
    if pays != "all":
        df = df[df['Country'] == pays]
    return df


# ── Production totale par pays ────────────────────────────────

@callback(
    Output("eng-vg-graph-yield-pays", "figure"),
    Input("eng-vg-dropdown-pays", "value"),
    Input("eng-vg-dropdown-mois", "value"),
)
def cb_yield_pays(pays, mois):
    df  = get_dataframe()
    agg = df.groupby("Country")["Daily_Yield"].sum().sort_values()

    colors = [COUNTRY_COLORS.get(c, ACCENT) for c in agg.index]

    fig = go.Figure(go.Bar(
        x=agg.values / 1e6,
        y=agg.index,
        orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"{v/1e6:.2f} M" for v in agg.values],
        textposition="outside",
        textfont=dict(size=10, family=MONO, color=T["text"]),
        hovertemplate="<b>%{y}</b><br>Production : %{x:.2f} M kWh<extra></extra>",
    ))

    layout = _base(xaxis_title="Production (M kWh)", showlegend=False, bargap=0.3)
    layout["xaxis"]["range"] = [0, agg.values.max() / 1e6 * 1.2]
    layout["yaxis"] = dict(tickfont=dict(size=11, family=MONO, color=T["text"]),
                           gridcolor=T["border"])
    layout["margin"] = dict(l=10, r=60, t=10, b=36)
    fig.update_layout(**layout)
    return fig


# ── Évolution mensuelle ───────────────────────────────────────

@callback(
    Output("eng-vg-graph-evolution", "figure"),
    Input("eng-vg-dropdown-pays", "value"),
    Input("eng-vg-dropdown-mois", "value"),
)
def cb_evolution(pays, mois):
    df  = get_dataframe()
    if mois != "all":
        df = df[df["Month"] == int(mois)]
    agg = df.groupby(["Country", "Month"])["DC_Power"].mean().reset_index()

    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())

    fig = go.Figure()
    for country in pays_list:
        d = agg[agg["Country"] == country].sort_values("Month")
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Scatter(
            x=[MONTHS[m-1] for m in d["Month"]],
            y=d["DC_Power"],
            name=country,
            mode="lines+markers",
            line=dict(color=col, width=2.5),
            marker=dict(size=6, color=col),
            fill="tozeroy",
            fillcolor=f"rgba({_hex_rgb(col)},0.05)",
            hovertemplate=f"<b>{country}</b> %{{x}} : %{{y:.1f}} W<extra></extra>",
        ))

    layout = _base(yaxis_title="Puissance DC moy. (W)", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Rendement DC→AC ───────────────────────────────────────────

@callback(
    Output("eng-vg-graph-efficacite", "figure"),
    Input("eng-vg-dropdown-pays", "value"),
    Input("eng-vg-dropdown-mois", "value"),
)
def cb_efficacite(pays, mois):
    df   = get_dataframe()
    prod = df[df["DC_Power"] > 0]
    agg  = prod.groupby("Country")["efficiency"].agg(
        moy="mean", p25=lambda x: x.quantile(0.25),
        p75=lambda x: x.quantile(0.75)
    ).reset_index().sort_values("moy")

    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())
    agg = agg[agg["Country"].isin(pays_list)]

    fig = go.Figure()
    for _, row in agg.iterrows():
        col = COUNTRY_COLORS.get(row["Country"], ACCENT)
        # Barre
        fig.add_trace(go.Bar(
            x=[row["Country"]], y=[row["moy"]],
            name=row["Country"],
            marker=dict(color=col, opacity=0.8),
            text=f"{row['moy']:.1f}%",
            textposition="outside",
            textfont=dict(size=10, family=MONO, color=T["text"]),
            hovertemplate=(
                f"<b>{row['Country']}</b><br>"
                f"Moy : {row['moy']:.1f}%<br>"
                f"P25–P75 : {row['p25']:.1f}% – {row['p75']:.1f}%<extra></extra>"
            ),
        ))

    # Ligne référence 90%
    fig.add_hline(y=90, line_dash="dot", line_color=T["muted"], line_width=1,
        annotation_text="90% référence",
        annotation_font=dict(size=8, color=T["muted"], family=MONO),
        annotation_position="right")

    layout = _base(yaxis_title="Rendement (%)", showlegend=False, bargap=0.35)
    layout["yaxis"]["range"] = [85, 95]
    layout["margin"] = dict(l=12, r=60, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Heatmap irradiation pays × mois ──────────────────────────

@callback(
    Output("eng-vg-graph-irradiation", "figure"),
    Input("eng-vg-dropdown-pays", "value"),
    Input("eng-vg-dropdown-mois", "value"),
)
def cb_irradiation(pays, mois):
    df  = get_dataframe()
    pvt = df.pivot_table(
        index="Country", columns="Month",
        values="Irradiation", aggfunc="mean"
    )
    pays   = pvt.index.tolist()
    z      = pvt.values
    text   = [[f"{z[i,j]:.3f}" for j in range(12)] for i in range(len(pays))]

    fig = go.Figure(go.Heatmap(
        z=z, x=MONTHS, y=pays,
        text=text, texttemplate="%{text}",
        textfont=dict(size=9, family=MONO),
        colorscale=[
            [0.0, T["card2"]],
            [0.3, "#1a3a5c"],
            [0.6, "#F0B429"],
            [1.0, "#F85149"],
        ],
        showscale=True,
        colorbar=dict(thickness=10, len=0.8,
            tickfont=dict(size=8, color=T["muted"], family=MONO),
            title=dict(text="W/m²", font=dict(size=9, color=T["muted"]))),
        hovertemplate="<b>%{y} — %{x}</b><br>Irradiation : %{z:.3f} W/m²<extra></extra>",
    ))

    layout = _base(showlegend=False)
    layout["xaxis"].update(tickfont=dict(size=9, family=MONO))
    layout["yaxis"].update(tickfont=dict(size=10, family=MONO))
    layout["margin"] = dict(l=10, r=60, t=10, b=30)
    fig.update_layout(**layout)
    return fig


def _hex_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
