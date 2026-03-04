# ============================================================
#  sectors/assurance/pages/sinistres/callbacks.py
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


def _base(**kw):
    return plotly_base("assurance", **kw)


def _filtered(branche, region):
    df = get_dataframe()
    if branche != "all":
        df = df[df["type_assurance"] == branche]
    if region != "all":
        df = df[df["region"] == region]
    return df


# ── Fréquence vs Sévérité (bubble chart) ─────────────────────

@callback(
    Output("ass-sin-graph-freq-sev", "figure"),
    Input("ass-sin-dropdown-branche", "value"),
    Input("ass-sin-dropdown-region",  "value"),
)
def cb_freq_sev(branche, region):
    df = _filtered(branche, region)

    rows = []
    for b in df["type_assurance"].unique():
        d    = df[df["type_assurance"] == b]
        sin  = d[d["sinistre"]]
        freq = d["sinistre"].mean() * 100
        sev  = sin["montant_sinistres"].mean() if len(sin) else 0
        cout = d["montant_sinistres"].sum()
        rows.append({"branche": b, "freq": freq, "sev": sev, "cout": cout})

    fig = go.Figure()
    for r in rows:
        col = BRANCH_COLORS.get(r["branche"], T["muted"])
        fig.add_trace(go.Scatter(
            x=[r["freq"]], y=[r["sev"]],
            mode="markers+text",
            name=r["branche"],
            marker=dict(
                size=max(20, r["cout"] / df["montant_sinistres"].sum() * 120),
                color=col, opacity=0.8,
                line=dict(color=T["bg"], width=2),
            ),
            text=[r["branche"]],
            textposition="top center",
            textfont=dict(size=9, color=col, family=MONO),
            hovertemplate=(
                f"<b>{r['branche']}</b><br>"
                f"Fréquence : {r['freq']:.1f}%<br>"
                f"Sévérité : {r['sev']:,.0f}<br>"
                f"Coût total : {r['cout']:,.0f}<extra></extra>"
            ),
        ))

    # Lignes de référence (médianes)
    all_freq = df.groupby("type_assurance")["sinistre"].mean().mean() * 100
    all_sev  = df[df["sinistre"]]["montant_sinistres"].mean()
    fig.add_hline(y=all_sev,  line_dash="dot", line_color=T["border"], line_width=1)
    fig.add_vline(x=all_freq, line_dash="dot", line_color=T["border"], line_width=1)

    # Annotations quadrants
    for txt, x, y in [
        ("Fréq. faible\nSév. élevée", all_freq * 0.6, all_sev * 1.15),
        ("Fréq. élevée\nSév. élevée", all_freq * 1.3, all_sev * 1.15),
        ("Fréq. faible\nSév. faible", all_freq * 0.6, all_sev * 0.8),
        ("Fréq. élevée\nSév. faible", all_freq * 1.3, all_sev * 0.8),
    ]:
        fig.add_annotation(x=x, y=y, text=txt, showarrow=False,
            font=dict(size=8, color=T["border"], family=MONO),
            align="center")

    layout = _base(xaxis_title="Fréquence (%)", yaxis_title="Sévérité moyenne",
                   showlegend=False)
    layout["margin"] = dict(l=12, r=12, t=12, b=36)
    fig.update_layout(**layout)
    return fig


# ── Distribution des montants ─────────────────────────────────

@callback(
    Output("ass-sin-graph-distrib", "figure"),
    Input("ass-sin-dropdown-branche", "value"),
    Input("ass-sin-dropdown-region",  "value"),
)
def cb_distrib(branche, region):
    import pandas as pd
    df  = _filtered(branche, region)
    sin = df[df["sinistre"]]["montant_sinistres"]

    fig = go.Figure()

    # Histogramme global
    fig.add_trace(go.Histogram(
        x=sin, nbinsx=30, name="Tous",
        marker_color=ACCENT, opacity=0.6,
        hovertemplate="[%{x:.0f}] : %{y} contrats<extra></extra>",
    ))

    # Courbe KDE simulée via histogram avec ligne
    if branche == "all":
        for b, col in BRANCH_COLORS.items():
            d = df[df["type_assurance"] == b]
            d = d[d["sinistre"]]["montant_sinistres"]
            if len(d) < 5:
                continue
            fig.add_trace(go.Histogram(
                x=d, nbinsx=20, name=b,
                marker_color=col, opacity=0.4,
                visible="legendonly",
            ))

    # Lignes percentiles
    for pct, label, col in [
        (0.5,  "Médiane",   T["green"]),
        (0.75, "P75",       T["accent"]),
        (0.9,  "P90",       T["red"]),
    ]:
        val = sin.quantile(pct)
        fig.add_vline(x=val, line_dash="dot", line_color=col, line_width=1.5,
            annotation_text=f"{label}: {val:,.0f}",
            annotation_font=dict(size=8, color=col, family=MONO),
            annotation_position="top right")

    layout = _base(xaxis_title="Montant sinistre",
                   yaxis_title="Nombre de contrats",
                   showlegend=branche == "all",
                   barmode="overlay")
    layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)")
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Répartition par nb sinistres ──────────────────────────────

@callback(
    Output("ass-sin-graph-nb-sin", "figure"),
    Input("ass-sin-dropdown-branche", "value"),
    Input("ass-sin-dropdown-region",  "value"),
)
def cb_nb_sin(branche, region):
    df  = _filtered(branche, region)
    cnt = df["nb_sinistres"].value_counts().sort_index()

    colors = [T["green"], ACCENT, T["accent"], T["red"], T["red"]]

    fig = go.Figure(go.Bar(
        x=[str(int(i)) for i in cnt.index],
        y=cnt.values,
        marker=dict(
            color=[colors[min(int(i), 4)] for i in cnt.index],
            opacity=0.85, line=dict(width=0),
        ),
        text=[f"{v}<br>{v/len(df)*100:.1f}%" for v in cnt.values],
        textposition="outside",
        textfont=dict(size=9, color=T["muted"], family=MONO),
        hovertemplate="<b>%{x} sinistre(s)</b> : %{y} contrats<extra></extra>",
    ))

    layout = _base(xaxis_title="Nb sinistres",
                   yaxis_title="Contrats", showlegend=False, bargap=0.25)
    layout["margin"] = dict(l=10, r=10, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Par tranche d'âge ─────────────────────────────────────────

@callback(
    Output("ass-sin-graph-age", "figure"),
    Input("ass-sin-dropdown-branche", "value"),
    Input("ass-sin-dropdown-region",  "value"),
)
def cb_age(branche, region):
    df     = _filtered(branche, region)
    tranches = ['18–30', '31–45', '46–60', '61–79']

    freqs, sevs, ns = [], [], []
    for t in tranches:
        d   = df[df["tranche_age"] == t]
        sin = d[d["sinistre"]]
        freqs.append(d["sinistre"].mean() * 100 if len(d) else 0)
        sevs.append(sin["montant_sinistres"].mean() if len(sin) else 0)
        ns.append(len(d))

    fig = go.Figure()

    # Barres fréquence
    fig.add_trace(go.Bar(
        x=tranches, y=freqs, name="Fréquence (%)",
        marker=dict(color=ACCENT, opacity=0.75, line=dict(width=0)),
        yaxis="y",
        hovertemplate="<b>%{x}</b> Fréq : %{y:.1f}%<extra></extra>",
    ))

    # Courbe sévérité
    fig.add_trace(go.Scatter(
        x=tranches, y=sevs, name="Sévérité moy.",
        mode="lines+markers",
        line=dict(color=T["red"], width=2.5),
        marker=dict(size=8, color=T["red"],
                    line=dict(color=T["bg"], width=1.5)),
        yaxis="y2",
        hovertemplate="<b>%{x}</b> Sév : %{y:,.0f}<extra></extra>",
    ))

    layout = _base(showlegend=True, bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["xaxis"]["title"] = dict(text="Tranche d'âge",
                                    font=dict(size=9))
    layout["yaxis"]["title"] = dict(text="Fréquence (%)",
                                    font=dict(size=9, color=ACCENT))
    layout["yaxis2"] = dict(
        title=dict(text="Sévérité", font=dict(size=9, color=T["red"])),
        overlaying="y", side="right",
        tickfont=dict(size=9, color=T["red"]),
        gridcolor="rgba(0,0,0,0)", showline=False, zeroline=False,
    )
    layout["margin"] = dict(l=12, r=50, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Coût par région et branche (stacked bars) ─────────────────

@callback(
    Output("ass-sin-graph-region-branche", "figure"),
    Input("ass-sin-dropdown-branche", "value"),
    Input("ass-sin-dropdown-region",  "value"),
)
def cb_region_branche(branche, region):
    import pandas as pd
    df = get_dataframe()   # pas de filtre branche ici pour voir toutes les branches
    if region != "all":
        df = df[df["region"] == region]

    pvt = df.pivot_table(
        index="region", columns="type_assurance",
        values="montant_sinistres", aggfunc="sum", fill_value=0
    ).reset_index()

    regions   = pvt["region"].tolist()
    branches  = [c for c in pvt.columns if c != "region"]

    fig = go.Figure()
    for b in branches:
        col = BRANCH_COLORS.get(b, T["muted"])
        fig.add_trace(go.Bar(
            name=b, x=regions, y=pvt[b],
            marker=dict(color=col, opacity=0.82, line=dict(width=0)),
            hovertemplate=f"<b>{b}</b> %{{x}} : %{{y:,.0f}}<extra></extra>",
        ))

    # Taux de sinistralité en overlay
    freq_reg = df.groupby("region")["sinistre"].mean() * 100
    fig.add_trace(go.Scatter(
        x=freq_reg.index.tolist(), y=freq_reg.values,
        name="Fréq. (%)", mode="lines+markers",
        line=dict(color="white", width=1.5, dash="dot"),
        marker=dict(size=6, color="white"),
        yaxis="y2",
        hovertemplate="<b>Fréq. %{x}</b> : %{y:.1f}%<extra></extra>",
    ))

    layout = _base(barmode="stack", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["yaxis"]["title"] = dict(text="Coût sinistres",
                                    font=dict(size=9))
    layout["yaxis2"] = dict(
        title=dict(text="Fréquence (%)", font=dict(size=9, color="white")),
        overlaying="y", side="right",
        tickfont=dict(size=9, color="white"),
        gridcolor="rgba(0,0,0,0)", showline=False, zeroline=False,
        range=[0, 60],
    )
    layout["margin"] = dict(l=12, r=50, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Top contrats à risque ─────────────────────────────────────

@callback(
    Output("ass-sin-graph-top-contrats", "figure"),
    Input("ass-sin-dropdown-branche", "value"),
    Input("ass-sin-dropdown-region",  "value"),
)
def cb_top_contrats(branche, region):
    df  = _filtered(branche, region)
    top = df.nlargest(15, "montant_sinistres").sort_values("montant_sinistres")

    colors = [BRANCH_COLORS.get(b, T["muted"]) for b in top["type_assurance"]]

    fig = go.Figure(go.Bar(
        x=top["montant_sinistres"],
        y=[f"#{int(r['id_assure'])} · {r['type_assurance']} · {r['region']}"
           for _, r in top.iterrows()],
        orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        customdata=top[["age", "bonus_malus", "nb_sinistres",
                        "montant_prime", "duree_contrat"]].values,
        hovertemplate=(
            "<b>Contrat %{y}</b><br>"
            "Sinistre : %{x:,.0f}<br>"
            "Âge : %{customdata[0]} ans<br>"
            "Bonus-malus : %{customdata[1]:.2f}<br>"
            "Nb sinistres : %{customdata[2]}<br>"
            "Prime : %{customdata[3]:,.0f}<br>"
            "Durée : %{customdata[4]} ans<extra></extra>"
        ),
    ))

    layout = _base(xaxis_title="Montant sinistre", showlegend=False, bargap=0.2)
    layout["yaxis"] = dict(tickfont=dict(size=9, family=MONO),
                           gridcolor=T["border"], showline=False)
    layout["margin"] = dict(l=10, r=20, t=10, b=36)
    fig.update_layout(**layout)
    return fig
