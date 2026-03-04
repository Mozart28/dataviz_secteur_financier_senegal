# ============================================================
#  sectors/energie/pages/anomalies/callbacks.py
# ============================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback
from config import get_theme, plotly_base, MONO
from sectors.energie.data.loader import get_dataframe

T      = get_theme("energie")
ACCENT = T["accent"]
MONTHS = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]

COUNTRY_COLORS = {
    "Norway":    "#58A6FF", "Brazil":    "#3FB950",
    "India":     "#F0B429", "Australia": "#F85149",
}
MONTH_COLORS = [
    "#58A6FF","#79B8FF","#3FB950","#56D364","#F0B429","#FFA500",
    "#F85149","#FF6B6B","#A78BFA","#C084FC","#34D399","#6EE7B7"
]

IRR_SEUIL = 0.05
COEF_M    = 62.07
COEF_B    = -0.67


def _base(**kw):
    return plotly_base("energie", **kw)


def _hex_rgb(h):
    h = h.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


def _prepare(pays, mois):
    df = get_dataframe().copy()
    if pays != "all":
        df = df[df["Country"] == pays]
    if mois != "all":
        df = df[df["Month"] == int(mois)]
    df["DC_theorique"] = (COEF_M * df["Irradiation"] + COEF_B).clip(lower=0)
    df["ecart_pct"]    = np.where(
        df["DC_theorique"] > 1,
        (df["DC_Power"] - df["DC_theorique"]) / df["DC_theorique"] * 100,
        np.nan
    )
    heures_sol = df["Hour"].between(6, 18)
    df["anomalie"] = (df["DC_Power"] == 0) & (df["Irradiation"] > IRR_SEUIL) & heures_sol
    return df


# ── Série temporelle avec zones anormales ─────────────────────

@callback(
    Output("eng-ano-graph-serie", "figure"),
    Input("eng-ano-dropdown-pays", "value"),
    Input("eng-ano-dropdown-mois", "value"),
)
def cb_serie(pays, mois):
    df = _prepare(pays, mois)

    # Agréger par heure sur toute la période
    agg  = df.groupby("DateTime").agg(
        DC_Power=("DC_Power", "mean"),
        anomalie=("anomalie", "max"),
    ).reset_index().sort_values("DateTime")

    col = COUNTRY_COLORS.get(pays, ACCENT) if pays != "all" else ACCENT

    fig = go.Figure()

    # Courbe DC principale
    fig.add_trace(go.Scatter(
        x=agg["DateTime"], y=agg["DC_Power"],
        mode="lines", name="DC Power réel",
        line=dict(color=col, width=1),
        hovertemplate="%{x|%d/%m %Hh} : %{y:.1f} W<extra></extra>",
    ))

    # Surligner les anomalies
    anom = agg[agg["anomalie"]]
    if len(anom):
        fig.add_trace(go.Scatter(
            x=anom["DateTime"], y=anom["DC_Power"],
            mode="markers", name=f"Anomalies ({len(anom)})",
            marker=dict(color=T["red"], size=6, symbol="x",
                        line=dict(color=T["red"], width=2)),
            hovertemplate="%{x|%d/%m %Hh} : DC=0 (Irr>0.05)<extra></extra>",
        ))

    # Zones rouges pour anomalies (shapes)
    shapes = []
    for _, row in anom.iterrows():
        shapes.append(dict(
            type="rect",
            x0=row["DateTime"], x1=row["DateTime"],
            y0=0, y1=1, yref="paper",
            fillcolor=T["red"], opacity=0.3,
            line=dict(width=0),
        ))

    layout = _base(
        yaxis_title="DC Power (W)", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
    )
    layout["shapes"] = shapes[:200]  # limiter pour performance
    layout["xaxis"].update(
        rangeslider=dict(visible=True, thickness=0.04,
                         bgcolor=T["card2"], bordercolor=T["border"]),
        rangeselector=dict(
            buttons=[
                dict(count=7,  label="7j",  step="day",  stepmode="backward"),
                dict(count=1,  label="1m",  step="month",stepmode="backward"),
                dict(count=3,  label="3m",  step="month",stepmode="backward"),
                dict(step="all", label="Tout"),
            ],
            bgcolor=T["card2"], activecolor=ACCENT,
            font=dict(size=9, family=MONO, color=T["text"]),
            x=0, y=1.08,
        ),
        type="date",
    )
    layout["margin"] = dict(l=12, r=12, t=40, b=50)
    fig.update_layout(**layout)
    return fig


# ── Écart DC réel vs théorique ────────────────────────────────

@callback(
    Output("eng-ano-graph-ecart", "figure"),
    Input("eng-ano-dropdown-pays", "value"),
    Input("eng-ano-dropdown-mois", "value"),
)
def cb_ecart(pays, mois):
    df   = _prepare(pays, mois)
    prod = df[df["DC_theorique"] > 1].dropna(subset=["ecart_pct"])
    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())

    fig = go.Figure()
    for country in pays_list:
        d   = prod[prod["Country"] == country]["ecart_pct"]
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Violin(
            y=d, name=country,
            box_visible=True, meanline_visible=True,
            fillcolor=f"rgba({_hex_rgb(col)},0.2)",
            line=dict(color=col, width=1.5),
            marker=dict(size=2, color=col),
            hovertemplate=f"<b>{country}</b><br>Écart: %{{y:.1f}}%<extra></extra>",
        ))

    # Ligne 0
    fig.add_hline(y=0, line_dash="dot", line_color="white",
        line_width=1.5,
        annotation_text="Théorique",
        annotation_font=dict(size=8, color=T["muted"], family=MONO),
        annotation_position="right")
    # Zones seuils
    fig.add_hrect(y0=-20, y1=0, fillcolor=T["red"],
                  opacity=0.04, line_width=0)
    fig.add_hrect(y0=0, y1=20, fillcolor=T["green"],
                  opacity=0.04, line_width=0)

    layout = _base(yaxis_title="Écart DC (%)", showlegend=False, violingap=0.3)
    layout["margin"] = dict(l=12, r=50, t=10, b=36)
    fig.update_layout(**layout)
    return fig


# ── Heatmap anomalies Heure × Mois ───────────────────────────

@callback(
    Output("eng-ano-graph-heatmap", "figure"),
    Input("eng-ano-dropdown-pays", "value"),
    Input("eng-ano-dropdown-mois", "value"),
)
def cb_heatmap(pays, mois):
    df   = _prepare(pays, mois)
    anom = df[df["anomalie"]]

    pvt = anom.pivot_table(
        index="Hour", columns="Month",
        values="anomalie", aggfunc="sum"
    ).reindex(index=range(24), columns=range(1,13)).fillna(0)

    z = pvt.values
    fig = go.Figure(go.Heatmap(
        z=z, x=MONTHS, y=[f"{h:02d}h" for h in range(24)],
        text=[[str(int(v)) if v > 0 else "" for v in row] for row in z],
        texttemplate="%{text}",
        textfont=dict(size=8, family=MONO),
        colorscale=[
            [0.0,  T["card2"]],
            [0.01, "#3a1a1a"],
            [0.3,  "#7a2020"],
            [0.7,  "#c73030"],
            [1.0,  T["red"]],
        ],
        showscale=True,
        colorbar=dict(thickness=10, len=0.8,
            tickfont=dict(size=8, color=T["muted"], family=MONO),
            title=dict(text="nb", font=dict(size=9, color=T["muted"]))),
        hovertemplate="<b>%{y} · %{x}</b><br>Anomalies : %{z:.0f}<extra></extra>",
    ))

    # Rectangle heures solaires
    fig.add_shape(type="rect", x0=-0.5, x1=11.5,
        y0=5.5, y1=18.5,
        line=dict(color=T["muted"], width=1, dash="dot"),
        fillcolor="rgba(0,0,0,0)")

    layout = _base(showlegend=False)
    layout["yaxis"].update(tickfont=dict(size=8, family=MONO), autorange="reversed")
    layout["xaxis"].update(tickfont=dict(size=9, family=MONO))
    layout["margin"] = dict(l=36, r=60, t=10, b=30)
    fig.update_layout(**layout)
    return fig


# ── Heures perdues par pays et mois ──────────────────────────

@callback(
    Output("eng-ano-graph-top", "figure"),
    Input("eng-ano-dropdown-pays", "value"),
    Input("eng-ano-dropdown-mois", "value"),
)
def cb_top(pays, mois):
    df   = get_dataframe().copy()
    heures_sol = df["Hour"].between(6, 18)
    df["anomalie"] = (df["DC_Power"] == 0) & (df["Irradiation"] > IRR_SEUIL) & heures_sol

    if pays != "all":
        df = df[df["Country"] == pays]
    if mois != "all":
        df = df[df["Month"] == int(mois)]

    agg = df[df["anomalie"]].groupby(["Country","Month"]).size().reset_index(name="nb")
    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())
    agg = agg[agg["Country"].isin(pays_list)]

    fig = go.Figure()
    for m_idx in range(1, 13):
        d = agg[agg["Month"] == m_idx]
        if len(d) == 0:
            continue
        fig.add_trace(go.Bar(
            x=d["Country"], y=d["nb"],
            name=MONTHS[m_idx-1],
            marker=dict(color=MONTH_COLORS[m_idx-1], opacity=0.85),
            hovertemplate=f"<b>%{{x}}</b> {MONTHS[m_idx-1]}: %{{y}} anomalies<extra></extra>",
        ))

    layout = _base(yaxis_title="Nb heures perdues", showlegend=True,
                   barmode="stack", bargap=0.25,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=8), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig
