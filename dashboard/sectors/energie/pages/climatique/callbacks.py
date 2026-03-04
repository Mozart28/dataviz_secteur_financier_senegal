import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback
from config import get_theme, plotly_base, MONO
from sectors.energie.data.loader import get_dataframe

T = get_theme("energie"); ACCENT = T["accent"]
COUNTRY_COLORS = {"Norway":"#58A6FF","Brazil":"#3FB950","India":"#F0B429","Australia":"#F85149"}
MONTHS = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]

def _base(**kw): return plotly_base("energie", **kw)
def _hex_rgb(h):
    h = h.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
def _filtered(pays, mois="all"):
    df = get_dataframe()
    if pays != "all":
        df = df[df["Country"] == pays]
    if mois != "all":
        df = df[df["Month"] == int(mois)]
    return df


@callback(Output("eng-clim-graph-temp-rendement","figure"),
    Input("eng-clim-dropdown-pays","value"),
    Input("eng-clim-dropdown-mois","value"))
def cb_temp_rendement(pays, mois):
    df   = _filtered(pays, mois)
    prod = df[df["DC_Power"] > 5].sample(min(3000, len(df[df["DC_Power"] > 5])), random_state=42)
    pays_list = prod["Country"].unique().tolist()

    fig = go.Figure()
    for country in pays_list:
        d   = prod[prod["Country"] == country].dropna(subset=["efficiency"])
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Scattergl(
            x=d["Module_Temperature"], y=d["efficiency"],
            mode="markers", name=country,
            marker=dict(color=col, size=3, opacity=0.4),
            hovertemplate=f"<b>{country}</b><br>T°: %{{x:.1f}}°C · Rend: %{{y:.1f}}%<extra></extra>",
        ))

    # Tendance linéaire globale
    p = prod.dropna(subset=["efficiency"])
    if len(p) > 10:
        m, b = np.polyfit(p["Module_Temperature"], p["efficiency"], 1)
        x_r  = np.linspace(p["Module_Temperature"].min(), p["Module_Temperature"].max(), 100)
        fig.add_trace(go.Scatter(
            x=x_r, y=m*x_r+b, mode="lines", name=f"Tendance ({m:.3f}%/°C)",
            line=dict(color="white", width=2, dash="dot"), hoverinfo="skip",
        ))

    layout = _base(xaxis_title="Température module (°C)", yaxis_title="Rendement DC→AC (%)",
                   showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-clim-graph-distribution-temp","figure"),
          Input("eng-clim-dropdown-pays","value"),
          Input("eng-clim-dropdown-mois","value"))
def cb_distrib_temp(pays, mois):
    df = get_dataframe()
    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())

    fig = go.Figure()
    for country in pays_list:
        d   = df[df["Country"] == country]
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Box(
            y=d["Ambient_Temperature"], name=f"{country} Amb.",
            marker=dict(color=col, size=2), line=dict(color=col, width=1.5),
            fillcolor=f"rgba({_hex_rgb(col)},0.15)",
            legendgroup=country,
            hovertemplate=f"<b>{country}</b> Ambiante: %{{y:.1f}}°C<extra></extra>",
        ))
        fig.add_trace(go.Box(
            y=d["Module_Temperature"], name=f"{country} Mod.",
            marker=dict(color=col, size=2, symbol="diamond"),
            line=dict(color=col, width=1.5),
            fillcolor=f"rgba({_hex_rgb(col)},0.05)",
            legendgroup=country, legendgrouptitle_text=country if country == pays_list[0] else "",
            hovertemplate=f"<b>{country}</b> Module: %{{y:.1f}}°C<extra></extra>",
        ))

    layout = _base(yaxis_title="Température (°C)", showlegend=True, boxgap=0.2,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=8), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-clim-graph-heatmap-temp","figure"),
    Input("eng-clim-dropdown-pays","value"),
    Input("eng-clim-dropdown-mois","value"))
def cb_heatmap_temp(pays, mois):
    df  = _filtered(pays, mois)
    pvt = df.pivot_table(index="Hour", columns="Month",
                         values="Ambient_Temperature", aggfunc="mean")
    z = pvt.values
    fig = go.Figure(go.Heatmap(
        z=z, x=MONTHS, y=[f"{h:02d}h" for h in range(24)],
        colorscale=[[0,"#58A6FF"],[0.4,"#161B22"],[0.7,"#F0B429"],[1.0,"#F85149"]],
        showscale=True,
        colorbar=dict(thickness=10, len=0.8,
            tickfont=dict(size=8, color=T["muted"], family=MONO),
            title=dict(text="°C", font=dict(size=9, color=T["muted"]))),
        hovertemplate="<b>%{y} · %{x}</b><br>T° amb. : %{z:.1f}°C<extra></extra>",
    ))
    layout = _base(showlegend=False)
    layout["yaxis"].update(tickfont=dict(size=8, family=MONO), autorange="reversed")
    layout["xaxis"].update(tickfont=dict(size=9, family=MONO))
    layout["margin"] = dict(l=36, r=60, t=10, b=30)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-clim-graph-irr-temp","figure"),
    Input("eng-clim-dropdown-pays","value"),
    Input("eng-clim-dropdown-mois","value"))
def cb_irr_temp(pays, mois):
    df   = _filtered(pays, mois)
    prod = df[df["Irradiation"] > 0].sample(min(2000, len(df[df["Irradiation"] > 0])), random_state=42)
    pays_list = prod["Country"].unique().tolist()

    fig = go.Figure()
    for country in pays_list:
        d   = prod[prod["Country"] == country]
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Scattergl(
            x=d["Irradiation"], y=d["Module_Temperature"],
            mode="markers", name=country,
            marker=dict(color=col, size=3, opacity=0.45),
            hovertemplate=f"<b>{country}</b><br>Irr: %{{x:.3f}} · T°mod: %{{y:.1f}}°C<extra></extra>",
        ))

    layout = _base(xaxis_title="Irradiation (W/m²)", yaxis_title="Température module (°C)",
                   showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig
