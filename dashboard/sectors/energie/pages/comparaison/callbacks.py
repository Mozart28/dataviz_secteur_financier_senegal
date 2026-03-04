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


@callback(Output("eng-cmp-graph-radar","figure"), Input("eng-cmp-graph-radar","id"))
def cb_radar(_):
    df = get_dataframe()
    prod = df[df["DC_Power"] > 0]

    # 5 critères normalisés 0-100
    metrics = {}
    for country in COUNTRY_COLORS.keys():
        d  = df[df["Country"] == country]
        dp = prod[prod["Country"] == country]
        metrics[country] = {
            "Production":  d["Daily_Yield"].sum(),
            "Rendement":   dp["efficiency"].mean(),
            "Irradiation": d["Irradiation"].mean(),
            "Stabilité":   1 / (d["DC_Power"].std() + 1) * 1000,
            "Température": 50 - abs(d["Module_Temperature"].mean() - 25),
        }

    # Normaliser 0-100
    df_m = pd.DataFrame(metrics).T
    df_n = (df_m - df_m.min()) / (df_m.max() - df_m.min()) * 100

    axes = df_n.columns.tolist()
    fig  = go.Figure()
    for country, col in COUNTRY_COLORS.items():
        vals = df_n.loc[country].tolist()
        vals.append(vals[0])  # fermer le polygone
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=axes + [axes[0]],
            name=country, fill="toself",
            line=dict(color=col, width=2),
            fillcolor=f"rgba({_hex_rgb(col)},0.1)",
            hovertemplate=f"<b>{country}</b> %{{theta}}: %{{r:.0f}}/100<extra></extra>",
        ))

    layout = _base(showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15,
            xanchor="center", x=0.5, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["polar"] = dict(
        bgcolor=T["card"],
        radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=7,family=MONO),
                        gridcolor=T["border"]),
        angularaxis=dict(tickfont=dict(size=9, family=MONO, color=T["text"]),
                         gridcolor=T["border"]),
    )
    layout.pop("xaxis", None); layout.pop("yaxis", None)
    layout["margin"] = dict(l=40, r=40, t=20, b=60)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-cmp-graph-classement","figure"), Input("eng-cmp-graph-classement","id"))
def cb_classement(_):
    df   = get_dataframe()
    prod = df[df["DC_Power"] > 0]
    agg  = df.groupby("Country").agg(
        production =("Daily_Yield",          "sum"),
        irradiation=("Irradiation",          "mean"),
        temp_mod   =("Module_Temperature",   "mean"),
    ).reset_index()
    agg["rendement"] = prod.groupby("Country")["efficiency"].mean().values

    fig = go.Figure()
    kpis_list = [
        ("production",  "Production (M kWh)", 1e6),
        ("rendement",   "Rendement (%)",       1),
        ("irradiation", "Irradiation (W/m²)",  1),
        ("temp_mod",    "Temp. module (°C)",   1),
    ]
    for i, (col_name, label, div) in enumerate(kpis_list):
        vals    = agg[col_name] / div
        max_val = vals.max()
        colors  = [COUNTRY_COLORS.get(c, ACCENT) for c in agg["Country"]]
        fig.add_trace(go.Bar(
            x=vals, y=agg["Country"],
            orientation="h",
            name=label,
            marker=dict(color=colors, opacity=0.85),
            text=[f"{v:.2f}" if div > 1 else f"{v:.1f}" for v in vals],
            textposition="outside",
            textfont=dict(size=9, family=MONO, color=T["text"]),
            visible=(i == 0),
            hovertemplate="<b>%{y}</b> : %{x}<extra></extra>",
        ))

    steps = []
    for i, (_, label, _) in enumerate(kpis_list):
        vis = [j == i for j in range(len(kpis_list))]
        steps.append(dict(args=[{"visible": vis}], label=label, method="update"))

    layout = _base(showlegend=False,
        updatemenus=[dict(
            buttons=steps, direction="down", showactive=True,
            x=0, xanchor="left", y=1.15, yanchor="top",
            bgcolor=T["card2"], bordercolor=T["border"],
            font=dict(size=10, family=MONO, color=T["text"]),
        )])
    layout["xaxis"]["range"] = [0, agg["production"].max() / 1e6 * 1.2]
    layout["yaxis"] = dict(tickfont=dict(size=10, family=MONO), gridcolor=T["border"])
    layout["margin"] = dict(l=10, r=60, t=40, b=36)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-cmp-graph-profils","figure"), Input("eng-cmp-graph-profils","id"))
def cb_profils(_):
    df  = get_dataframe()
    agg = df.groupby(["Country","Hour"])["DC_Power"].mean().reset_index()

    fig = go.Figure()
    for country, col in COUNTRY_COLORS.items():
        d    = agg[agg["Country"] == country].sort_values("Hour")
        norm = (d["DC_Power"] - d["DC_Power"].min()) / (d["DC_Power"].max() - d["DC_Power"].min() + 1e-9) * 100
        fig.add_trace(go.Scatter(
            x=d["Hour"], y=norm, name=country, mode="lines",
            line=dict(color=col, width=2.5),
            hovertemplate=f"<b>{country}</b> %{{x}}h : %{{y:.0f}}%<extra></extra>",
        ))

    layout = _base(xaxis_title="Heure", yaxis_title="Production normalisée (%)",
                   showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["xaxis"].update(tickvals=list(range(0,24,3)),
        ticktext=[f"{h:02d}h" for h in range(0,24,3)])
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-cmp-graph-mensuel","figure"), Input("eng-cmp-graph-mensuel","id"))
def cb_mensuel(_):
    df  = get_dataframe()
    agg = df.groupby(["Country","Month"])["DC_Power"].mean().reset_index()

    fig = go.Figure()
    for country, col in COUNTRY_COLORS.items():
        d = agg[agg["Country"] == country].sort_values("Month")
        fig.add_trace(go.Bar(
            x=[MONTHS[m-1] for m in d["Month"]], y=d["DC_Power"],
            name=country, marker=dict(color=col, opacity=0.8),
            hovertemplate=f"<b>{country}</b> %{{x}}: %{{y:.1f}} W<extra></extra>",
        ))

    layout = _base(yaxis_title="DC Power moy. (W)", showlegend=True,
                   barmode="group", bargap=0.15, bargroupgap=0.05,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig
