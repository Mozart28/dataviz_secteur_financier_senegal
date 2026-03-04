# ============================================================
#  sectors/assurance/pages/profil_assure/callbacks.py
# ============================================================

import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, callback

from config import get_theme, plotly_base, MONO
from sectors.assurance.data.loader import get_dataframe

T      = get_theme("assurance")
ACCENT = T["accent"]

BRANCH_COLORS = {
    "Auto":       "#F0B429",
    "Santé":      "#58A6FF",
    "Vie":        "#3FB950",
    "Habitation": "#A78BFA",
}
TRANCHES = ['18–30', '31–45', '46–60', '61–79']


def _base(**kw):
    return plotly_base("assurance", **kw)


def _filtered(branche):
    df = get_dataframe()
    return df if branche == "all" else df[df["type_assurance"] == branche]


# ── Pyramide des âges ─────────────────────────────────────────

@callback(
    Output("ass-profil-graph-pyramide", "figure"),
    Input("ass-profil-dropdown-branche", "value"),
)
def cb_pyramide(branche):
    import pandas as pd
    df = _filtered(branche)

    bins   = list(range(18, 85, 5))
    labels = [f"{b}–{b+4}" for b in bins[:-1]]
    df["grp5"] = pd.cut(df["age"], bins=bins, labels=labels, right=False)

    m_counts = df[df["sexe"]=="masculin"]["grp5"].value_counts().reindex(labels, fill_value=0)
    f_counts = df[df["sexe"]=="feminin"]["grp5"].value_counts().reindex(labels, fill_value=0)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels, x=-m_counts.values,
        orientation="h", name="Hommes",
        marker=dict(color=T["blue"], opacity=0.8, line=dict(width=0)),
        hovertemplate="<b>Hommes %{y}</b> : %{customdata}<extra></extra>",
        customdata=m_counts.values,
    ))
    fig.add_trace(go.Bar(
        y=labels, x=f_counts.values,
        orientation="h", name="Femmes",
        marker=dict(color="#F472B6", opacity=0.8, line=dict(width=0)),
        hovertemplate="<b>Femmes %{y}</b> : %{x}<extra></extra>",
    ))

    max_v = max(m_counts.max(), f_counts.max()) + 5
    layout = _base(barmode="relative", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["xaxis"].update(
        range=[-max_v, max_v],
        tickvals=[-max_v, -max_v//2, 0, max_v//2, max_v],
        ticktext=[str(abs(v)) for v in [-max_v, -max_v//2, 0, max_v//2, max_v]],
        title=dict(text="← Hommes   |   Femmes →",
                   font=dict(size=9, color=T["muted"])),
    )
    layout["yaxis"].update(tickfont=dict(size=9), gridcolor=T["border"])
    layout["margin"] = dict(l=10, r=10, t=10, b=36)
    fig.update_layout(**layout)
    return fig


# ── Portefeuille branche × sexe ───────────────────────────────

@callback(
    Output("ass-profil-graph-branche-sexe", "figure"),
    Input("ass-profil-dropdown-branche", "value"),
)
def cb_branche_sexe(branche):
    import pandas as pd
    df  = _filtered(branche)
    pvt = df.groupby(["type_assurance", "sexe"]).agg(
        nb       =("id_assure",        "count"),
        prime_moy=("montant_prime",    "mean"),
        freq_sin =("sinistre",         "mean"),
    ).reset_index()

    branches = pvt["type_assurance"].unique().tolist()
    fig = go.Figure()

    for sexe, col, pattern in [
        ("masculin", T["blue"],   ""),
        ("feminin",  "#F472B6",   "/"),
    ]:
        d = pvt[pvt["sexe"] == sexe]
        d = d.set_index("type_assurance").reindex(branches).fillna(0).reset_index()

        fig.add_trace(go.Bar(
            x=d["type_assurance"], y=d["nb"],
            name=sexe.capitalize(),
            marker=dict(color=col, opacity=0.8, line=dict(width=0),
                        pattern_shape=pattern),
            customdata=d[["prime_moy", "freq_sin"]].values,
            hovertemplate=(
                f"<b>{sexe.capitalize()} %{{x}}</b><br>"
                "Contrats : %{y}<br>"
                "Prime moy : %{customdata[0]:.0f}<br>"
                "Fréq. sin : %{customdata[1]:.1%}<extra></extra>"
            ),
        ))

    layout = _base(barmode="group", showlegend=True, bargap=0.25,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["yaxis"]["title"] = dict(text="Nb contrats", font=dict(size=9))
    layout["margin"] = dict(l=10, r=10, t=10, b=36)
    fig.update_layout(**layout)
    return fig


# ── Répartition géographique ──────────────────────────────────

@callback(
    Output("ass-profil-graph-region", "figure"),
    Input("ass-profil-dropdown-branche", "value"),
)
def cb_region(branche):
    df  = _filtered(branche)
    agg = df.groupby("region").agg(
        nb       =("id_assure",        "count"),
        prime_moy=("montant_prime",    "mean"),
        freq_sin =("sinistre",         "mean"),
        age_moy  =("age",              "mean"),
    ).reset_index().sort_values("nb", ascending=False)

    REGION_COLORS = {
        "Dakar":       ACCENT,
        "Thiès":       T["green"],
        "Saint-Louis": T["blue"],
        "Kaolack":     "#A78BFA",
    }
    colors = [REGION_COLORS.get(r, T["muted"]) for r in agg["region"]]

    fig = go.Figure(go.Pie(
        labels=agg["region"],
        values=agg["nb"],
        hole=0.52,
        marker=dict(colors=colors, line=dict(color=T["bg"], width=2)),
        textinfo="percent+label",
        textfont=dict(size=10, family=MONO),
        customdata=agg[["prime_moy", "freq_sin", "age_moy"]].values,
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Contrats : %{value}<br>"
            "Part : %{percent}<br>"
            "Prime moy : %{customdata[0]:.0f}<br>"
            "Fréq. sin : %{customdata[1]:.1%}<br>"
            "Âge moy : %{customdata[2]:.0f} ans<extra></extra>"
        ),
        direction="clockwise", sort=True,
    ))

    top_r   = agg.iloc[0]["region"]
    top_pct = agg.iloc[0]["nb"] / agg["nb"].sum() * 100

    base = {k: v for k, v in _base().items() if k not in ("xaxis", "yaxis")}
    base.update(
        showlegend=False,
        margin=dict(l=8, r=8, t=8, b=8),
        annotations=[dict(
            text=(f'<span style="font-size:13px;font-weight:700;'
                  f'color:{T["text"]}">{top_pct:.0f}%</span>'
                  f'<br><span style="font-size:9px;color:{T["muted"]}">{top_r}</span>'),
            x=0.5, y=0.5, showarrow=False, font=dict(family=MONO),
        )],
    )
    fig.update_layout(**base)
    return fig


# ── Fidélité (durée × sinistralité) ──────────────────────────

@callback(
    Output("ass-profil-graph-fidelite", "figure"),
    Input("ass-profil-dropdown-branche", "value"),
)
def cb_fidelite(branche):
    df  = _filtered(branche)
    agg = df.groupby("duree_contrat").agg(
        nb       =("id_assure",        "count"),
        freq_sin =("sinistre",         "mean"),
        prime_moy=("montant_prime",    "mean"),
        bm_moy   =("bonus_malus",      "mean"),
    ).reset_index().sort_values("duree_contrat")

    fig = go.Figure()

    # Barres : nb contrats
    fig.add_trace(go.Bar(
        x=agg["duree_contrat"], y=agg["nb"],
        name="Nb contrats",
        marker=dict(
            color=ACCENT, opacity=0.35,
            line=dict(width=0),
        ),
        yaxis="y",
        hovertemplate="<b>%{x} ans</b> : %{y} contrats<extra></extra>",
    ))

    # Courbe fréquence sinistralité
    fig.add_trace(go.Scatter(
        x=agg["duree_contrat"], y=agg["freq_sin"] * 100,
        name="Fréq. sinistre (%)",
        mode="lines+markers",
        line=dict(color=T["red"], width=2.5),
        marker=dict(size=7, color=T["red"],
                    line=dict(color=T["bg"], width=1.5)),
        yaxis="y2",
        hovertemplate="<b>%{x} ans</b> fréq : %{y:.1f}%<extra></extra>",
    ))

    # Courbe bonus-malus
    fig.add_trace(go.Scatter(
        x=agg["duree_contrat"], y=agg["bm_moy"],
        name="Bonus-malus moy.",
        mode="lines+markers",
        line=dict(color=T["green"], width=2, dash="dot"),
        marker=dict(size=6, color=T["green"]),
        yaxis="y3",
        hovertemplate="<b>%{x} ans</b> B/M : %{y:.3f}<extra></extra>",
    ))

    layout = _base(showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
        bargap=0.2)
    layout["xaxis"].update(title=dict(text="Durée contrat (années)",
                                       font=dict(size=9)),
                           dtick=1)
    layout["yaxis"].update(title=dict(text="Nb contrats", font=dict(size=9)),
                           showgrid=True)
    layout["yaxis2"] = dict(
        title=dict(text="Fréq. (%)", font=dict(size=9, color=T["red"])),
        overlaying="y", side="right",
        tickfont=dict(size=9, color=T["red"]),
        gridcolor="rgba(0,0,0,0)", showline=False, zeroline=False,
        range=[0, 65],
    )
    layout["yaxis3"] = dict(
        overlaying="y", side="right",
        tickfont=dict(size=8, color=T["green"]),
        gridcolor="rgba(0,0,0,0)", showline=False, zeroline=False,
        range=[0.85, 1.15], showticklabels=False,
    )
    layout["margin"] = dict(l=12, r=55, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Bonus-malus par tranche d'âge ────────────────────────────

@callback(
    Output("ass-profil-graph-bm-age", "figure"),
    Input("ass-profil-dropdown-branche", "value"),
)
def cb_bm_age(branche):
    df = _filtered(branche)

    fig = go.Figure()
    def _to_rgba(hex_col, alpha=0.2):
        h = hex_col.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return f"rgba({r},{g},{b},{alpha})"

    for sexe, col in [("masculin", T["blue"]), ("feminin", "#F472B6")]:
        d = df[df["sexe"] == sexe]
        bm_vals = [d[d["tranche_age"] == t]["bonus_malus"].values
                   for t in TRANCHES]
        fig.add_trace(go.Box(
            y=[v for vals in bm_vals for v in vals],
            x=[t for t, vals in zip(TRANCHES, bm_vals) for _ in vals],
            name=sexe.capitalize(),
            marker_color=col,
            boxmean="sd",
            line=dict(color=col, width=1.5),
            fillcolor=_to_rgba(col, 0.2),
            hovertemplate=(
                f"<b>{sexe.capitalize()} %{{x}}</b><br>"
                "B/M : %{y:.3f}<extra></extra>"
            ),
        ))

    # Ligne de référence 1.0
    fig.add_hline(y=1.0, line_dash="dot", line_color=T["muted"],
        line_width=1,
        annotation_text="Référence 1.0",
        annotation_font=dict(size=8, color=T["muted"], family=MONO),
        annotation_position="top left")

    layout = _base(showlegend=True, boxmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["yaxis"].update(title=dict(text="Bonus-malus", font=dict(size=9)),
                           range=[0.4, 1.65])
    layout["xaxis"].update(title=dict(text="Tranche d'âge", font=dict(size=9)))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Heatmap âge × région ─────────────────────────────────────

@callback(
    Output("ass-profil-graph-heatmap", "figure"),
    Input("ass-profil-dropdown-branche", "value"),
)
def cb_heatmap(branche):
    import pandas as pd
    import numpy as np
    df = _filtered(branche)

    # Convertir tranche_age en str pour éviter les problèmes Categorical
    df = df.copy()
    df["tranche_age"] = df["tranche_age"].astype(str)

    pvt = df.pivot_table(
        index="tranche_age", columns="region",
        values="id_assure", aggfunc="count", fill_value=0,
    ).reindex(TRANCHES).fillna(0)

    regions = pvt.columns.tolist()
    z       = pvt.values.astype(float)

    # % sur le total général — protéger contre division par zéro
    total   = z.sum()
    z_pct   = z / (total if total > 0 else 1) * 100

    text = [[f"{int(z[i,j])}<br>({z_pct[i,j]:.1f}%)"
             for j in range(len(regions))]
            for i in range(len(TRANCHES))]

    fig = go.Figure(go.Heatmap(
        z=z_pct, x=regions, y=TRANCHES,
        text=text, texttemplate="%{text}",
        textfont=dict(size=10, family=MONO),
        colorscale=[
            [0.0, T["card2"]],
            [0.4, "#1a3a5c"],
            [1.0, ACCENT],
        ],
        showscale=True,
        colorbar=dict(
            thickness=10, len=0.8,
            tickfont=dict(size=8, color=T["muted"], family=MONO),
            title=dict(text="%", font=dict(size=9, color=T["muted"])),
        ),
        hovertemplate=(
            "<b>%{y} · %{x}</b><br>"
            "Contrats : %{text}<extra></extra>"
        ),
    ))

    layout = _base(showlegend=False)
    layout["xaxis"].update(tickfont=dict(size=10, family=MONO))
    layout["yaxis"].update(tickfont=dict(size=10, family=MONO))
    layout["margin"] = dict(l=10, r=60, t=10, b=30)
    fig.update_layout(**layout)
    return fig
