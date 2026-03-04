# ============================================================
#  sectors/assurance/pages/vue_portefeuille/callbacks.py
# ============================================================

import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, callback

from config import get_theme, plotly_base, empty_fig, MONO
from sectors.assurance.data.loader import get_dataframe

T      = get_theme("assurance")
ACCENT = T["accent"]

BRANCH_COLORS = {
    "Auto":       "#F0B429",
    "Santé":      "#58A6FF",
    "Vie":        "#3FB950",
    "Habitation": "#A78BFA",
}
REGION_COLORS = {
    "Dakar":       ACCENT,
    "Thiès":       T["green"],
    "Saint-Louis": T["blue"],
    "Kaolack":     "#A78BFA",
}


def _base(sector="assurance", **kw):
    return plotly_base(sector, **kw)


# ── Évolution annuelle ────────────────────────────────────────

@callback(
    Output("ass-vm-graph-evolution", "figure"),
    Input("ass-vm-dropdown-branche", "value"),
)
def cb_evolution(branche):
    import pandas as pd
    df = get_dataframe()
    if branche != "all":
        df = df[df["type_assurance"] == branche]

    agg = df.groupby("annee").agg(
        primes    =("montant_prime",    "sum"),
        sinistres =("montant_sinistres","sum"),
        contrats  =("id_assure",        "count"),
    ).reset_index()
    agg = agg[agg["annee"] >= 2021]   # exclure 2020 (3 contrats)

    fig = go.Figure()

    # Barres primes
    fig.add_trace(go.Bar(
        x=agg["annee"], y=agg["primes"],
        name="Primes", marker_color=T["green"],
        opacity=0.8, yaxis="y",
        hovertemplate="<b>Primes %{x}</b> : %{y:,.0f}<extra></extra>",
    ))

    # Barres sinistres
    fig.add_trace(go.Bar(
        x=agg["annee"], y=agg["sinistres"],
        name="Sinistres", marker_color=T["red"],
        opacity=0.8, yaxis="y",
        hovertemplate="<b>Sinistres %{x}</b> : %{y:,.0f}<extra></extra>",
    ))

    # Courbe ratio S/P
    ratio = (agg["sinistres"] / agg["primes"] * 100).round(1)
    fig.add_trace(go.Scatter(
        x=agg["annee"], y=ratio,
        name="Ratio S/P (%)", mode="lines+markers",
        line=dict(color=ACCENT, width=2.5),
        marker=dict(size=7, color=ACCENT, line=dict(color=T["bg"], width=1.5)),
        yaxis="y2",
        hovertemplate="<b>S/P %{x}</b> : %{y:.1f}%<extra></extra>",
    ))

    # Ligne de seuil 100%
    fig.add_hline(y=100, line_dash="dot", line_color=T["muted"],
        line_width=1, yref="y2",
        annotation_text="Seuil 100%",
        annotation_font=dict(size=8, color=T["muted"], family=MONO),
        annotation_position="top left")

    layout = _base(
        barmode="group",
        yaxis_title="Montant",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
    )
    layout["yaxis2"] = dict(
        title=dict(text="Ratio S/P (%)", font=dict(size=9, color=ACCENT)),
        overlaying="y", side="right",
        tickfont=dict(size=9, color=ACCENT),
        gridcolor="rgba(0,0,0,0)", showline=False, zeroline=False,
    )
    fig.update_layout(**layout)
    return fig


# ── Donut répartition primes ──────────────────────────────────

@callback(
    Output("ass-vm-graph-donut-branche", "figure"),
    Input("ass-vm-dropdown-branche", "value"),
)
def cb_donut(branche):
    df  = get_dataframe()
    agg = df.groupby("type_assurance")["montant_prime"].sum().reset_index()
    agg.columns = ["branche", "primes"]
    agg = agg.sort_values("primes", ascending=False)

    colors = [BRANCH_COLORS.get(b, T["muted"]) for b in agg["branche"]]
    active = None if branche == "all" else \
             agg.index[agg["branche"] == branche].tolist()

    pull = [0.08 if (branche != "all" and b == branche) else 0
            for b in agg["branche"]]

    fig = go.Figure(go.Pie(
        labels=agg["branche"],
        values=agg["primes"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=T["bg"], width=2)),
        pull=pull,
        textinfo="percent+label",
        textfont=dict(size=10, family=MONO),
        direction="clockwise", sort=False,
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
    ))

    top_b  = agg.iloc[0]["branche"]
    top_p  = agg.iloc[0]["primes"]
    total  = agg["primes"].sum()

    base = {k: v for k, v in _base().items() if k not in ("xaxis", "yaxis")}
    base.update(
        showlegend=False,
        margin=dict(l=8, r=8, t=8, b=8),
        annotations=[dict(
            text=(f'<span style="font-size:13px;font-weight:700;'
                  f'color:{T["text"]}">{top_p/total*100:.0f}%</span>'
                  f'<br><span style="font-size:9px;color:{T["muted"]}">{top_b}</span>'),
            x=0.5, y=0.5, showarrow=False, font=dict(family=MONO),
        )],
    )
    fig.update_layout(**base)
    return fig


# ── Ratio S/P par branche ─────────────────────────────────────

@callback(
    Output("ass-vm-graph-sp-branche", "figure"),
    Input("ass-vm-dropdown-branche", "value"),
)
def cb_sp_branche(branche):
    df  = get_dataframe()
    agg = df.groupby("type_assurance").agg(
        primes    =("montant_prime",    "sum"),
        sinistres =("montant_sinistres","sum"),
    ).reset_index()
    agg["ratio_sp"] = agg["sinistres"] / agg["primes"] * 100
    agg = agg.sort_values("ratio_sp")

    colors = []
    for _, row in agg.iterrows():
        sp = row["ratio_sp"]
        if sp > 100:   colors.append(T["red"])
        elif sp > 70:  colors.append(T["accent"])
        else:          colors.append(T["green"])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["ratio_sp"], y=agg["type_assurance"],
        orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in agg["ratio_sp"]],
        textposition="outside",
        textfont=dict(size=10, color=T["text"], family=MONO),
        hovertemplate="<b>%{y}</b> : %{x:.1f}%<extra></extra>",
    ))

    # Ligne seuil 100%
    fig.add_vline(x=100, line_dash="dot", line_color=T["muted"],
        line_width=1,
        annotation_text="100%",
        annotation_font=dict(size=8, color=T["muted"], family=MONO))

    layout = _base(xaxis_title="Ratio S/P (%)", showlegend=False, bargap=0.3)
    layout["xaxis"]["range"] = [0, agg["ratio_sp"].max() * 1.15]
    layout["yaxis"] = dict(gridcolor=T["border"], tickfont=dict(size=10),
                           showline=False)
    layout["margin"] = dict(l=10, r=50, t=10, b=30)
    fig.update_layout(**layout)
    return fig


# ── Taux de sinistralité par région ───────────────────────────

@callback(
    Output("ass-vm-graph-sin-region", "figure"),
    Input("ass-vm-dropdown-branche", "value"),
)
def cb_sin_region(branche):
    df = get_dataframe()
    if branche != "all":
        df = df[df["type_assurance"] == branche]

    agg = df.groupby("region").agg(
        total     =("id_assure",    "count"),
        sinistrés =("sinistre",     "sum"),
        primes    =("montant_prime","sum"),
        sinistres =("montant_sinistres","sum"),
    ).reset_index()
    agg["taux"] = agg["sinistrés"] / agg["total"] * 100
    agg["sp"]   = agg["sinistres"] / agg["primes"] * 100
    agg = agg.sort_values("taux", ascending=True)

    colors = [REGION_COLORS.get(r, T["muted"]) for r in agg["region"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["taux"], y=agg["region"],
        orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in agg["taux"]],
        textposition="outside",
        textfont=dict(size=10, color=T["text"], family=MONO),
        customdata=agg[["total","sp"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Taux sinistralité : %{x:.1f}%<br>"
            "Contrats : %{customdata[0]}<br>"
            "Ratio S/P : %{customdata[1]:.1f}%<extra></extra>"
        ),
    ))

    layout = _base(xaxis_title="Taux de sinistralité (%)",
                   showlegend=False, bargap=0.35)
    layout["xaxis"]["range"] = [0, agg["taux"].max() * 1.2]
    layout["yaxis"] = dict(gridcolor=T["border"], tickfont=dict(size=10),
                           showline=False)
    layout["margin"] = dict(l=10, r=50, t=10, b=30)
    fig.update_layout(**layout)
    return fig


# ── Distribution bonus-malus ──────────────────────────────────

@callback(
    Output("ass-vm-graph-bonus", "figure"),
    Input("ass-vm-dropdown-branche", "value"),
)
def cb_bonus(branche):
    df = get_dataframe()
    if branche != "all":
        df = df[df["type_assurance"] == branche]

    fig = go.Figure()
    for b, color in BRANCH_COLORS.items():
        d = df[df["type_assurance"] == b]["bonus_malus"]
        fig.add_trace(go.Violin(
            x=d, name=b,
            line_color=color, fillcolor=color.replace("FF","33") if "#" not in color[-2:] else color + "33",
            opacity=0.7, box_visible=True, meanline_visible=True,
            side="positive", width=1.5,
            hovertemplate=f"<b>{b}</b><br>B/M : %{{x:.2f}}<extra></extra>",
        ))

    fig.add_vline(x=1.0, line_dash="dot", line_color=T["muted"],
        line_width=1,
        annotation_text="Référence 1.0",
        annotation_font=dict(size=8, color=T["muted"], family=MONO))

    layout = _base(xaxis_title="Coefficient bonus-malus", showlegend=False)
    layout["margin"] = dict(l=10, r=10, t=10, b=30)
    layout["yaxis"] = dict(visible=False)
    fig.update_layout(**layout)
    return fig


# ── Heatmap branche × région ──────────────────────────────────

@callback(
    Output("ass-vm-graph-heatmap", "figure"),
    Input("ass-vm-dropdown-branche", "value"),
)
def cb_heatmap(branche):
    import pandas as pd
    import numpy as np
    df  = get_dataframe()   # toujours tout le portefeuille
    pvt = df.pivot_table(
        index="type_assurance", columns="region",
        values="montant_sinistres", aggfunc="sum",
        fill_value=0,
    )

    branches = pvt.index.tolist()
    regions  = pvt.columns.tolist()
    z        = pvt.values.astype(float)

    # Normaliser par ligne — éviter division par zéro
    row_sums = z.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1, row_sums)
    z_norm   = z / row_sums * 100

    text = [[f"{z_norm[i,j]:.1f}%<br>({z[i,j]:,.0f})"
             for j in range(len(regions))]
            for i in range(len(branches))]

    fig = go.Figure(go.Heatmap(
        z=z_norm, x=regions, y=branches,
        text=text, texttemplate="%{text}",
        textfont=dict(size=10, family=MONO),
        colorscale=[
            [0.0, T["card2"]],
            [0.3, "#1e3a5f"],
            [0.6, "#1a5276"],
            [1.0, ACCENT],
        ],
        showscale=True,
        colorbar=dict(
            thickness=10, len=0.8,
            tickfont=dict(size=8, color=T["muted"], family=MONO),
            title=dict(text="%", font=dict(size=9, color=T["muted"])),
        ),
        hovertemplate=(
            "<b>%{y} × %{x}</b><br>"
            "Part : %{z:.1f}%<extra></extra>"
        ),
    ))

    layout = _base(showlegend=False)
    layout["margin"] = dict(l=10, r=60, t=10, b=30)
    layout["xaxis"] = dict(tickfont=dict(size=10, family=MONO),
                           gridcolor=T["border"])
    layout["yaxis"] = dict(tickfont=dict(size=10, family=MONO),
                           gridcolor=T["border"])
    fig.update_layout(**layout)
    return fig
