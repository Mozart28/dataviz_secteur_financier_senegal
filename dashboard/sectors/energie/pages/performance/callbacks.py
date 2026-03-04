import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback
from config import get_theme, plotly_base, MONO
from sectors.energie.data.loader import get_dataframe

T = get_theme("energie"); ACCENT = T["accent"]
COUNTRY_COLORS = {"Norway":"#58A6FF","Brazil":"#3FB950","India":"#F0B429","Australia":"#F85149"}

def _base(**kw): return plotly_base("energie", **kw)
def _filtered(pays, mois="all"):
    df = get_dataframe()
    if pays != "all":
        df = df[df["Country"] == pays]
    if mois != "all":
        df = df[df["Month"] == int(mois)]
    return df


@callback(Output("eng-perf-graph-scatter","figure"),
    Input("eng-perf-dropdown-pays","value"),
    Input("eng-perf-dropdown-mois","value"))
def cb_scatter(pays, mois):
    df   = _filtered(pays, mois)
    prod = df[df["DC_Power"] > 0].sample(min(2000, len(df[df["DC_Power"] > 0])), random_state=42)
    pays_list = prod["Country"].unique().tolist()

    fig = go.Figure()
    for country in pays_list:
        d   = prod[prod["Country"] == country]
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Scattergl(
            x=d["Irradiation"], y=d["DC_Power"],
            mode="markers", name=country,
            marker=dict(color=col, size=3, opacity=0.5),
            hovertemplate=f"<b>{country}</b><br>Irr: %{{x:.3f}} · DC: %{{y:.1f}} W<extra></extra>",
        ))

    # Ligne de régression globale
    p = prod[prod["Irradiation"] > 0]
    m, b = np.polyfit(p["Irradiation"], p["DC_Power"], 1)
    x_line = np.linspace(0, p["Irradiation"].max(), 100)
    fig.add_trace(go.Scatter(
        x=x_line, y=m * x_line + b,
        mode="lines", name="Régression",
        line=dict(color="white", width=1.5, dash="dot"),
        hoverinfo="skip",
    ))

    layout = _base(xaxis_title="Irradiation (W/m²)", yaxis_title="DC Power (W)",
                   showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-perf-graph-rendement-heure","figure"),
    Input("eng-perf-dropdown-pays","value"),
    Input("eng-perf-dropdown-mois","value"))
def cb_rendement_heure(pays, mois):
    df   = _filtered(pays, mois)
    prod = df[(df["DC_Power"] > 5) & (df["Hour"].between(6,18))]
    agg  = prod.groupby("Hour")["efficiency"].mean().reset_index()

    colors = ["#3FB950" if v >= 90 else "#F0B429" if v >= 85 else "#F85149"
              for v in agg["efficiency"]]

    fig = go.Figure(go.Bar(
        x=agg["Hour"], y=agg["efficiency"],
        marker=dict(color=colors, opacity=0.85),
        text=[f"{v:.1f}%" for v in agg["efficiency"]],
        textposition="outside",
        textfont=dict(size=8, family=MONO, color=T["text"]),
        hovertemplate="<b>%{x}h</b> : %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=90, line_dash="dot", line_color=T["muted"], line_width=1,
        annotation_text="90%", annotation_font=dict(size=8, color=T["muted"], family=MONO))

    layout = _base(xaxis_title="Heure", yaxis_title="Rendement (%)", showlegend=False, bargap=0.15)
    layout["yaxis"]["range"] = [80, 96]
    layout["xaxis"].update(tickvals=list(range(6,19)),
        ticktext=[f"{h}h" for h in range(6,19)])
    layout["margin"] = dict(l=12, r=40, t=28, b=36)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-perf-graph-pertes","figure"),
    Input("eng-perf-dropdown-pays","value"),
    Input("eng-perf-dropdown-mois","value"))
def cb_pertes(pays, mois):
    df  = get_dataframe()
    if mois != "all":
        df = df[df["Month"] == int(mois)]
    agg = df.groupby("Country").agg(dc=("DC_Power","sum"), ac=("AC_Power","sum")).reset_index()
    agg["perte"]     = agg["dc"] - agg["ac"]
    agg["taux_perte"] = agg["perte"] / agg["dc"] * 100

    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())
    agg = agg[agg["Country"].isin(pays_list)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["Country"], y=agg["ac"] / 1e6, name="AC (utilisable)",
        marker=dict(color=T["green"], opacity=0.85),
        hovertemplate="<b>%{x}</b> AC : %{y:.1f} M W<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=agg["Country"], y=agg["perte"] / 1e6, name="Pertes onduleur",
        marker=dict(color=T["red"], opacity=0.75),
        text=[f"-{v:.1f}%" for v in agg["taux_perte"]],
        textposition="outside",
        textfont=dict(size=9, family=MONO, color=T["red"]),
        hovertemplate="<b>%{x}</b> Pertes : %{y:.2f} M W (%{text})<extra></extra>",
    ))

    layout = _base(yaxis_title="Puissance cumulée (M W)", showlegend=True,
                   barmode="stack", bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-perf-graph-pic-production","figure"),
          Input("eng-perf-dropdown-pays","value"),
          Input("eng-perf-dropdown-mois","value"))
def cb_pic(pays, mois):
    df   = get_dataframe()
    prod = df[df["DC_Power"] > 0]
    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())

    fig = go.Figure()
    for country in pays_list:
        d   = prod[prod["Country"] == country]["DC_Power"]
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Box(
            y=d, name=country, boxmean=True,
            marker=dict(color=col, size=3),
            line=dict(color=col, width=1.5),
            fillcolor=f"rgba({_hex_rgb(col)},0.15)",
            hovertemplate=f"<b>{country}</b><br>%{{y:.1f}} W<extra></extra>",
        ))

    layout = _base(yaxis_title="DC Power (W)", showlegend=False, boxgap=0.3)
    layout["margin"] = dict(l=12, r=12, t=10, b=36)
    fig.update_layout(**layout)
    return fig


def _hex_rgb(h):
    h = h.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


# ── Évolution DC vs AC sur l'année ────────────────────────────

@callback(
    Output("eng-perf-graph-dc-vs-ac", "figure"),
    Input("eng-perf-dropdown-pays", "value"),
    Input("eng-perf-dropdown-mois", "value"),
)
def cb_dc_vs_ac(pays, mois):
    df  = _filtered(pays, mois)
    agg = df.groupby("Month").agg(
        DC=("DC_Power", "mean"),
        AC=("AC_Power", "mean"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"][m-1]
           for m in agg["Month"]],
        y=agg["DC"],
        name="DC Power",
        marker=dict(color=ACCENT, opacity=0.85),
        hovertemplate="%{x} DC : %{y:.1f} W<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=[["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"][m-1]
           for m in agg["Month"]],
        y=agg["AC"],
        name="AC Power",
        marker=dict(color=T["green"], opacity=0.85),
        hovertemplate="%{x} AC : %{y:.1f} W<extra></extra>",
    ))
    # Courbe d'écart
    fig.add_trace(go.Scatter(
        x=[["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"][m-1]
           for m in agg["Month"]],
        y=(agg["DC"] - agg["AC"]),
        name="Pertes (DC−AC)",
        mode="lines+markers",
        yaxis="y2",
        line=dict(color=T["red"], width=2, dash="dot"),
        marker=dict(size=5),
        hovertemplate="%{x} Pertes : %{y:.1f} W<extra></extra>",
    ))

    layout = _base(yaxis_title="Puissance moy. (W)", showlegend=True,
                   barmode="group", bargap=0.2,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
        yaxis2=dict(
            title=dict(text="Pertes (W)", font=dict(color=T["red"], size=10, family=MONO)),
            overlaying="y", side="right",
            showgrid=False,
            tickfont=dict(size=9, family=MONO, color=T["red"]))
    )
    layout["margin"] = dict(l=12, r=50, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Rendement mensuel DC→AC ───────────────────────────────────

@callback(
    Output("eng-perf-graph-rendement-mensuel", "figure"),
    Input("eng-perf-dropdown-pays", "value"),
    Input("eng-perf-dropdown-mois", "value"),
)
def cb_rendement_mensuel(pays, mois):
    df   = get_dataframe()
    prod = df[df["DC_Power"] > 0]
    if mois != "all":
        prod = prod[prod["Month"] == int(mois)]

    agg = prod.groupby(["Country", "Month"])["efficiency"].mean().reset_index()
    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())
    agg = agg[agg["Country"].isin(pays_list)]

    MONTHS = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]

    fig = go.Figure()
    for country in pays_list:
        d   = agg[agg["Country"] == country].sort_values("Month")
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Scatter(
            x=[MONTHS[m-1] for m in d["Month"]],
            y=d["efficiency"],
            name=country, mode="lines+markers",
            line=dict(color=col, width=2.5),
            marker=dict(size=7, color=col,
                        line=dict(width=1.5, color=T["bg"])),
            hovertemplate=f"<b>{country}</b> %{{x}}: %{{y:.2f}}%<extra></extra>",
        ))

    fig.add_hline(y=90, line_dash="dot", line_color=T["muted"], line_width=1,
        annotation_text="90%",
        annotation_font=dict(size=8, color=T["muted"], family=MONO))

    layout = _base(yaxis_title="Rendement DC→AC (%)", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["yaxis"]["range"] = [86, 95]
    layout["margin"] = dict(l=12, r=40, t=28, b=36)
    fig.update_layout(**layout)
    return fig
