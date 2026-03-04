# ============================================================
#  sectors/assurance/pages/rentabilite/callbacks.py
# ============================================================

import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, callback

from config import get_theme, plotly_base, MONO
from sectors.assurance.data.loader import get_dataframe

T      = get_theme("assurance")
ACCENT = T["accent"]
EXPENSE_RATIO = 30.0

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


def _base(**kw):
    return plotly_base("assurance", **kw)


def _filtered(branche):
    df = get_dataframe()
    return df if branche == "all" else df[df["type_assurance"] == branche]


def _lr_color(lr):
    if lr > 150: return T["red"]
    if lr > 100: return "#F97316"
    if lr > 70:  return T["accent"]
    return T["green"]


# ── Waterfall Combined Ratio ──────────────────────────────────

@callback(
    Output("ass-rent-graph-waterfall", "figure"),
    Input("ass-rent-dropdown-branche", "value"),
)
def cb_waterfall(branche):
    df        = _filtered(branche)
    primes    = df['montant_prime'].sum()
    sinistres = df['montant_sinistres'].sum()
    charges   = primes * EXPENSE_RATIO / 100
    lr        = sinistres / primes * 100
    er        = EXPENSE_RATIO
    combined  = lr + er
    marge     = 100 - combined

    labels = ["Primes (base 100%)", "Loss Ratio", "Expense Ratio",
              "Combined Ratio", "Marge technique"]
    values = [100, -lr, -er, 0, marge]
    measures = ["absolute", "relative", "relative", "total", "total"]
    colors_w = [ACCENT, T["red"], T["muted"],
                T["red"] if combined > 100 else T["green"],
                T["red"] if marge < 0 else T["green"]]

    text = ["100%", f"−{lr:.1f}%", f"−{er:.1f}%",
            f"{combined:.1f}%", f"{marge:+.1f}%"]

    fig = go.Figure(go.Waterfall(
        x=labels, y=values, measure=measures,
        text=text, textposition="outside",
        textfont=dict(size=10, color=T["text"], family=MONO),
        connector=dict(line=dict(color=T["border"], width=1, dash="dot")),
        increasing=dict(marker=dict(color="rgba(63,185,80,0.85)")),
        decreasing=dict(marker=dict(color="rgba(248,81,73,0.85)")),
        totals=dict(marker=dict(
            color="rgba(248,81,73,0.85)" if combined > 100
                  else "rgba(63,185,80,0.85)")),
    ))

    # Ligne seuil 100%
    fig.add_hline(y=0, line_color=T["border"], line_width=1)
    fig.add_hline(y=-100 + 100, line_dash="dot",
        line_color=T["muted"], line_width=1,
        annotation_text="Seuil équilibre",
        annotation_font=dict(size=8, color=T["muted"], family=MONO))

    layout = _base(showlegend=False, yaxis_title="% des primes")
    layout["margin"] = dict(l=12, r=12, t=28, b=60)
    layout["xaxis"]["tickfont"] = dict(size=9, family=MONO)
    fig.update_layout(**layout)
    return fig


# ── Loss Ratio par branche ────────────────────────────────────

@callback(
    Output("ass-rent-graph-lr-branche", "figure"),
    Input("ass-rent-dropdown-branche", "value"),
)
def cb_lr_branche(branche):
    df  = get_dataframe()
    agg = df.groupby("type_assurance").agg(
        primes    =("montant_prime",    "sum"),
        sinistres =("montant_sinistres","sum"),
    ).reset_index()
    agg["lr"] = agg["sinistres"] / agg["primes"] * 100
    agg["cr"] = agg["lr"] + EXPENSE_RATIO
    agg = agg.sort_values("lr", ascending=True)

    fig = go.Figure()

    # Barres Loss Ratio
    fig.add_trace(go.Bar(
        y=agg["type_assurance"],
        x=agg["lr"],
        name="Loss Ratio",
        orientation="h",
        marker=dict(
            color=[_lr_color(lr) for lr in agg["lr"]],
            opacity=0.85, line=dict(width=0),
        ),
        text=[f"{v:.1f}%" for v in agg["lr"]],
        textposition="outside",
        textfont=dict(size=10, family=MONO, color=T["text"]),
        hovertemplate="<b>%{y}</b> LR : %{x:.1f}%<extra></extra>",
    ))

    # Marqueur Combined Ratio
    fig.add_trace(go.Scatter(
        y=agg["type_assurance"],
        x=agg["cr"],
        name="Combined Ratio",
        mode="markers",
        marker=dict(symbol="diamond", size=10,
                    color="white", line=dict(color=T["muted"], width=1.5)),
        hovertemplate="<b>%{y}</b> CR : %{x:.1f}%<extra></extra>",
    ))

    # Ligne seuil 100%
    fig.add_vline(x=100, line_dash="dot", line_color=T["muted"],
        line_width=1.5,
        annotation_text="LR 100%",
        annotation_font=dict(size=8, color=T["muted"], family=MONO))

    # Highlight branche sélectionnée
    if branche != "all" and branche in agg["type_assurance"].values:
        idx  = agg[agg["type_assurance"] == branche].index[0]
        pos  = agg.index.get_loc(idx)
        lr_v = float(agg[agg["type_assurance"] == branche]["lr"].iloc[0])
        fig.add_annotation(
            x=lr_v, y=branche,
            text="◀ sélection",
            showarrow=False, xshift=60,
            font=dict(size=8, color=ACCENT, family=MONO),
        )

    layout = _base(xaxis_title="Ratio (%)", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
        bargap=0.3)
    layout["yaxis"] = dict(tickfont=dict(size=10, family=MONO),
                           gridcolor=T["border"], showline=False)
    layout["margin"] = dict(l=10, r=70, t=28, b=30)
    fig.update_layout(**layout)
    return fig


# ── Combined Ratio par région ─────────────────────────────────

@callback(
    Output("ass-rent-graph-cr-region", "figure"),
    Input("ass-rent-dropdown-branche", "value"),
)
def cb_cr_region(branche):
    df  = _filtered(branche)
    agg = df.groupby("region").agg(
        primes    =("montant_prime",    "sum"),
        sinistres =("montant_sinistres","sum"),
        contrats  =("id_assure",        "count"),
    ).reset_index()
    agg["lr"] = agg["sinistres"] / agg["primes"] * 100
    agg["cr"] = agg["lr"] + EXPENSE_RATIO
    agg["marge"] = 100 - agg["cr"]
    agg = agg.sort_values("cr")

    colors = [REGION_COLORS.get(r, T["muted"]) for r in agg["region"]]

    fig = go.Figure()

    # Barres empilées LR + ER
    fig.add_trace(go.Bar(
        y=agg["region"], x=agg["lr"],
        name="Loss Ratio", orientation="h",
        marker=dict(color=T["red"], opacity=0.75, line=dict(width=0)),
        hovertemplate="<b>%{y}</b> LR : %{x:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=agg["region"], x=[EXPENSE_RATIO] * len(agg),
        name=f"Expense Ratio ({EXPENSE_RATIO:.0f}%)", orientation="h",
        marker=dict(color=T["muted"], opacity=0.45, line=dict(width=0)),
        hovertemplate=f"<b>%{{y}}</b> ER : {EXPENSE_RATIO:.0f}%<extra></extra>",
    ))

    # Annotation marge
    for _, row in agg.iterrows():
        fig.add_annotation(
            x=row["cr"] + 8, y=row["region"],
            text=f"CR={row['cr']:.0f}%",
            showarrow=False,
            font=dict(size=9, color=T["text"], family=MONO),
        )

    # Ligne seuil 100%
    fig.add_vline(x=100, line_dash="dot", line_color=ACCENT,
        line_width=1.5,
        annotation_text="Équilibre 100%",
        annotation_font=dict(size=8, color=ACCENT, family=MONO))

    layout = _base(barmode="stack", xaxis_title="% des primes",
        showlegend=True, bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["yaxis"] = dict(tickfont=dict(size=10, family=MONO),
                           gridcolor=T["border"], showline=False)
    layout["margin"] = dict(l=10, r=80, t=28, b=30)
    fig.update_layout(**layout)
    return fig


# ── Évolution LR & CR annuels ─────────────────────────────────

@callback(
    Output("ass-rent-graph-evolution", "figure"),
    Input("ass-rent-dropdown-branche", "value"),
)
def cb_evolution(branche):
    df  = _filtered(branche)
    agg = df[df["annee"] >= 2021].groupby("annee").agg(
        primes    =("montant_prime",    "sum"),
        sinistres =("montant_sinistres","sum"),
    ).reset_index()
    agg["lr"] = agg["sinistres"] / agg["primes"] * 100
    agg["cr"] = agg["lr"] + EXPENSE_RATIO
    agg["marge"] = 100 - agg["cr"]

    fig = go.Figure()

    # Zone remplie entre LR et CR (= expense ratio)
    fig.add_trace(go.Scatter(
        x=agg["annee"].tolist() + agg["annee"].tolist()[::-1],
        y=agg["cr"].tolist() + agg["lr"].tolist()[::-1],
        fill="toself",
        fillcolor="rgba(139,148,158,0.10)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Expense Ratio", hoverinfo="skip",
    ))

    # Courbe LR
    fig.add_trace(go.Scatter(
        x=agg["annee"], y=agg["lr"],
        name="Loss Ratio",
        mode="lines+markers",
        line=dict(color=T["red"], width=2.5),
        marker=dict(size=8, color=T["red"],
                    line=dict(color=T["bg"], width=1.5)),
        hovertemplate="<b>LR %{x}</b> : %{y:.1f}%<extra></extra>",
    ))

    # Courbe CR
    fig.add_trace(go.Scatter(
        x=agg["annee"], y=agg["cr"],
        name="Combined Ratio",
        mode="lines+markers",
        line=dict(color=T["accent"], width=2.5),
        marker=dict(size=8, color=T["accent"], symbol="diamond",
                    line=dict(color=T["bg"], width=1.5)),
        hovertemplate="<b>CR %{x}</b> : %{y:.1f}%<extra></extra>",
    ))

    # Zone marge (si positive)
    fig.add_hline(y=100, line_dash="dash", line_color=ACCENT,
        line_width=1.5,
        annotation_text="Seuil 100%",
        annotation_font=dict(size=8, color=ACCENT, family=MONO),
        annotation_position="top left")

    # Annotations tendance
    if len(agg) >= 2:
        trend = agg["lr"].iloc[-1] - agg["lr"].iloc[0]
        arrow = "↓" if trend < 0 else "↑"
        col   = T["green"] if trend < 0 else T["red"]
        fig.add_annotation(
            x=agg["annee"].iloc[-1], y=agg["lr"].iloc[-1],
            text=f"{arrow} {abs(trend):.1f}pts",
            showarrow=False, xshift=40,
            font=dict(size=9, color=col, family=MONO, weight="bold"),
        )

    layout = _base(yaxis_title="Ratio (%)", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified")
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Scatter prime vs sinistre ─────────────────────────────────

@callback(
    Output("ass-rent-graph-scatter", "figure"),
    Input("ass-rent-dropdown-branche", "value"),
)
def cb_scatter(branche):
    df = _filtered(branche)

    fig = go.Figure()
    for b, col in BRANCH_COLORS.items():
        d = df[df["type_assurance"] == b]
        if branche != "all" and b != branche:
            continue
        fig.add_trace(go.Scatter(
            x=d["montant_prime"],
            y=d["montant_sinistres"],
            mode="markers",
            name=b,
            marker=dict(
                color=col, size=5, opacity=0.55,
                line=dict(width=0),
            ),
            hovertemplate=(
                f"<b>{b}</b><br>"
                "Prime : %{x:,.0f}<br>"
                "Sinistre : %{y:,.0f}<extra></extra>"
            ),
        ))

    # Ligne d'équilibre prime = sinistre
    max_v = max(df["montant_prime"].max(), df["montant_sinistres"].max())
    fig.add_trace(go.Scatter(
        x=[0, max_v], y=[0, max_v],
        mode="lines", name="Équilibre (P=S)",
        line=dict(color=T["muted"], width=1.5, dash="dot"),
        hoverinfo="skip",
    ))

    # Zone rentable
    fig.add_annotation(
        x=max_v * 0.75, y=max_v * 0.15,
        text="✓ Contrat rentable",
        showarrow=False,
        font=dict(size=9, color=T["green"], family=MONO),
    )
    fig.add_annotation(
        x=max_v * 0.2, y=max_v * 0.85,
        text="✗ Contrat déficitaire",
        showarrow=False,
        font=dict(size=9, color=T["red"], family=MONO),
    )

    layout = _base(xaxis_title="Prime collectée",
                   yaxis_title="Sinistre payé", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Bonus-malus vs Loss Ratio ─────────────────────────────────

@callback(
    Output("ass-rent-graph-bm-lr", "figure"),
    Input("ass-rent-dropdown-branche", "value"),
)
def cb_bm_lr(branche):
    import pandas as pd
    df = _filtered(branche)
    df = df.copy()
    df["bm_grp"] = pd.cut(df["bonus_malus"],
        bins=[0.49, 0.75, 1.0, 1.25, 1.51],
        labels=["0.5–0.75", "0.75–1.0", "1.0–1.25", "1.25–1.5"])

    agg = df.groupby("bm_grp", observed=True).agg(
        primes    =("montant_prime",    "sum"),
        sinistres =("montant_sinistres","sum"),
        nb        =("id_assure",        "count"),
        freq      =("sinistre",         "mean"),
    ).reset_index()
    agg["lr"] = agg["sinistres"] / agg["primes"] * 100

    grps   = agg["bm_grp"].astype(str).tolist()
    colors = [T["green"], ACCENT, "#F97316", T["red"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grps, y=agg["lr"],
        marker=dict(color=colors[:len(grps)], opacity=0.82, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in agg["lr"]],
        textposition="outside",
        textfont=dict(size=10, family=MONO, color=T["text"]),
        customdata=agg[["nb", "freq"]].values,
        hovertemplate=(
            "<b>BM %{x}</b><br>"
            "Loss Ratio : %{y:.1f}%<br>"
            "Contrats : %{customdata[0]}<br>"
            "Fréq. sin : %{customdata[1]:.1%}<extra></extra>"
        ),
        name="Loss Ratio",
    ))

    fig.add_hline(y=100, line_dash="dot", line_color=T["muted"],
        line_width=1,
        annotation_text="100%",
        annotation_font=dict(size=8, color=T["muted"], family=MONO))

    layout = _base(xaxis_title="Tranche bonus-malus",
                   yaxis_title="Loss Ratio (%)", showlegend=False, bargap=0.3)
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Prime pure vs prime commerciale ──────────────────────────

@callback(
    Output("ass-rent-graph-prime-pure", "figure"),
    Input("ass-rent-dropdown-branche", "value"),
)
def cb_prime_pure(branche):
    df  = get_dataframe()
    agg = df.groupby("type_assurance").agg(
        prime_comm=("montant_prime",     "mean"),
        freq      =("sinistre",          "mean"),
        sev       =("montant_sinistres", lambda x:
                    x[df.loc[x.index, "sinistre"]].mean()
                    if df.loc[x.index, "sinistre"].sum() > 0 else 0),
    ).reset_index()
    agg["prime_pure"]   = agg["freq"] * agg["sev"]
    agg["chargement"]   = agg["prime_comm"] - agg["prime_pure"]
    agg["taux_charge"]  = agg["chargement"] / agg["prime_comm"] * 100
    agg = agg.sort_values("prime_comm", ascending=True)

    branches = agg["type_assurance"].tolist()
    colors_b = [BRANCH_COLORS.get(b, T["muted"]) for b in branches]

    fig = go.Figure()

    # Prime pure
    fig.add_trace(go.Bar(
        y=branches, x=agg["prime_pure"],
        name="Prime pure", orientation="h",
        marker=dict(color=T["red"], opacity=0.75, line=dict(width=0)),
        hovertemplate="<b>%{y}</b> Prime pure : %{x:.0f}<extra></extra>",
    ))

    # Chargement
    fig.add_trace(go.Bar(
        y=branches, x=agg["chargement"],
        name="Chargement", orientation="h",
        marker=dict(color=T["green"], opacity=0.65, line=dict(width=0)),
        hovertemplate="<b>%{y}</b> Chargement : %{x:.0f}<extra></extra>",
    ))

    # Annotation taux de chargement
    for _, row in agg.iterrows():
        fig.add_annotation(
            x=row["prime_comm"] + 30, y=row["type_assurance"],
            text=f"{row['taux_charge']:.1f}% charge",
            showarrow=False,
            font=dict(size=9, color=T["muted"], family=MONO),
        )

    layout = _base(barmode="stack", xaxis_title="Montant prime",
        showlegend=True, bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["yaxis"] = dict(tickfont=dict(size=10, family=MONO),
                           gridcolor=T["border"], showline=False)
    layout["margin"] = dict(l=10, r=110, t=28, b=30)
    fig.update_layout(**layout)
    return fig
