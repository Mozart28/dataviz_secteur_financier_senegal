import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback
from config import get_theme, plotly_base, MONO
from sectors.energie.data.loader import get_dataframe

T      = get_theme("energie")
ACCENT = T["accent"]
MONTHS = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]
COUNTRY_COLORS = {
    "Norway":"#58A6FF","Brazil":"#3FB950","India":"#F0B429","Australia":"#F85149"
}
SEASON_ORDER = ["Printemps","Été","Automne","Hiver"]
SEASON_COLORS = {
    "Printemps":"#3FB950","Été":"#F0B429","Automne":"#F85149","Hiver":"#58A6FF"
}

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


@callback(Output("eng-tmp-graph-heatmap","figure"),
          Input("eng-tmp-dropdown-pays","value"),
          Input("eng-tmp-dropdown-mois","value"))
def cb_heatmap(pays, mois):
    df  = _filtered(pays, mois)
    pvt = df.pivot_table(index="Hour", columns="Month",
                         values="DC_Power", aggfunc="mean").fillna(0)
    z = pvt.values
    fig = go.Figure(go.Heatmap(
        z=z, x=MONTHS, y=[f"{h:02d}h" for h in range(24)],
        colorscale=[[0,"#0D1117"],[0.2,"#1a3a5c"],[0.5,"#F0B429"],[1.0,"#F85149"]],
        showscale=True,
        colorbar=dict(thickness=10, len=0.8,
            tickfont=dict(size=8, color=T["muted"], family=MONO),
            title=dict(text="W", font=dict(size=9, color=T["muted"]))),
        hovertemplate="<b>%{y} · %{x}</b><br>DC : %{z:.1f} W<extra></extra>",
    ))
    layout = _base(showlegend=False)
    layout["yaxis"].update(tickfont=dict(size=8, family=MONO), autorange="reversed")
    layout["xaxis"].update(tickfont=dict(size=9, family=MONO))
    layout["margin"] = dict(l=36, r=60, t=10, b=30)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-tmp-graph-courbe-journaliere","figure"),
          Input("eng-tmp-dropdown-pays","value"),
          Input("eng-tmp-dropdown-mois","value"))
def cb_courbe(pays, mois):
    df  = get_dataframe()
    if mois != "all":
        df = df[df["Month"] == int(mois)]
    agg = df.groupby(["Country","Hour"])["DC_Power"].mean().reset_index()
    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())

    fig = go.Figure()
    for country in pays_list:
        d   = agg[agg["Country"]==country].sort_values("Hour")
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Scatter(
            x=d["Hour"], y=d["DC_Power"], name=country,
            mode="lines", line=dict(color=col, width=2.5),
            fill="tozeroy", fillcolor=f"rgba({_hex_rgb(col)},0.08)",
            hovertemplate=f"<b>{country}</b> %{{x}}h : %{{y:.1f}} W<extra></extra>",
        ))

    layout = _base(xaxis_title="Heure", yaxis_title="DC Power moy. (W)", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["xaxis"].update(tickvals=list(range(0,24,3)),
        ticktext=[f"{h:02d}h" for h in range(0,24,3)])
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-tmp-graph-saisonnalite","figure"),
          Input("eng-tmp-dropdown-pays","value"),
          Input("eng-tmp-dropdown-mois","value"))
def cb_saison(pays, mois):
    df  = get_dataframe()
    agg = df.groupby(["Country","season"])["DC_Power"].mean().reset_index()
    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())
    agg = agg[agg["Country"].isin(pays_list)]

    fig = go.Figure()
    for country in pays_list:
        d = agg[agg["Country"]==country]
        # Réordonner saisons
        d = d.set_index("season").reindex(
            [s for s in SEASON_ORDER if s in d["season"].values]
        ).reset_index()
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Bar(
            x=d["season"], y=d["DC_Power"], name=country,
            marker=dict(color=col, opacity=0.8),
            hovertemplate=f"<b>{country}</b> %{{x}} : %{{y:.1f}} W<extra></extra>",
        ))

    layout = _base(yaxis_title="DC Power moy. (W)", showlegend=True, bargap=0.2, barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


@callback(Output("eng-tmp-graph-daily-yield","figure"),
          Input("eng-tmp-dropdown-pays","value"),
          Input("eng-tmp-dropdown-mois","value"))
def cb_daily_yield(pays, mois):
    df = get_dataframe()
    # Daily yield unique par jour et par pays
    daily = df[df["DC_Power"] > 0].groupby(
        ["Country","Date"])["Daily_Yield"].max().reset_index()
    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())

    fig = go.Figure()
    for country in pays_list:
        d   = daily[daily["Country"]==country]["Daily_Yield"]
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Histogram(
            x=d, name=country, nbinsx=40,
            marker=dict(color=col, opacity=0.6, line=dict(width=0)),
            hovertemplate=f"<b>{country}</b> %{{x:.0f}} kWh : %{{y}} jours<extra></extra>",
        ))

    layout = _base(xaxis_title="Daily Yield (kWh)", yaxis_title="Nb jours",
                   showlegend=True, barmode="overlay",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Yield cumulé jour par jour ────────────────────────────────

@callback(
    Output("eng-tmp-graph-yield-cumul", "figure"),
    Input("eng-tmp-dropdown-pays", "value"),
    Input("eng-tmp-dropdown-mois", "value"),
)
def cb_yield_cumul(pays, mois):
    df = get_dataframe()
    daily = df.groupby(["Country", "Date"])["Daily_Yield"].max().reset_index()
    daily = daily.sort_values("Date")
    daily["yield_cum"] = daily.groupby("Country")["Daily_Yield"].cumsum()

    if mois != "all":
        daily = daily[daily["Date"].dt.month <= int(mois)]

    pays_list = [pays] if pays != "all" else list(COUNTRY_COLORS.keys())

    fig = go.Figure()
    for country in pays_list:
        d   = daily[daily["Country"] == country]
        col = COUNTRY_COLORS.get(country, ACCENT)
        fig.add_trace(go.Scatter(
            x=d["Date"], y=d["yield_cum"] / 1e3,
            mode="lines", name=country,
            line=dict(color=col, width=2.5),
            fill="tozeroy",
            fillcolor=f"rgba({_hex_rgb(col)},0.06)",
            hovertemplate=f"<b>{country}</b> %{{x|%d %b}}: %{{y:.1f}} k kWh cumulés<extra></extra>",
        ))

    layout = _base(yaxis_title="Yield cumulé (k kWh)", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["xaxis"]["type"] = "date"
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig
