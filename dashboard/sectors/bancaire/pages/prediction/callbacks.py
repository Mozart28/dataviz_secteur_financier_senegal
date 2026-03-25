# ============================================================
#  sectors/bancaire/pages/prediction/callbacks.py
#  Calcul positionnement marché — régression linéaire
# ============================================================
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import callback, Input, Output, State, html, no_update
from config import get_theme, MONO, SERIF, SANS

# ── Données de référence 2019 (22 banques, données complètes) ─
REF_DATA = {
    "BAS":      {"BILAN": 372383,  "RESSOURCES": 189126,  "FONDS_PROPRE": 30994,  "EMPLOI": 247812,  "EFFECTIF": 236,  "AGENCE": 21, "COMPTE": 73209},
    "BCIM":     {"BILAN": 25730,   "RESSOURCES": 18088,   "FONDS_PROPRE": 5502,   "EMPLOI": 9911,    "EFFECTIF": 25,   "AGENCE": 2,  "COMPTE": 542},
    "BDK":      {"BILAN": 170663,  "RESSOURCES": 98657,   "FONDS_PROPRE": 23242,  "EMPLOI": 99558,   "EFFECTIF": 115,  "AGENCE": 7,  "COMPTE": 5412},
    "BGFI":     {"BILAN": 87985,   "RESSOURCES": 59855,   "FONDS_PROPRE": 3530,   "EMPLOI": 53944,   "EFFECTIF": 63,   "AGENCE": 2,  "COMPTE": 1534},
    "BICIS":    {"BILAN": 499528,  "RESSOURCES": 385663,  "FONDS_PROPRE": 55884,  "EMPLOI": 346428,  "EFFECTIF": 483,  "AGENCE": 33, "COMPTE": 86775},
    "BIS":      {"BILAN": 369275,  "RESSOURCES": 280335,  "FONDS_PROPRE": 43767,  "EMPLOI": 292192,  "EFFECTIF": 206,  "AGENCE": 28, "COMPTE": 82281},
    "BNDE":     {"BILAN": 216335,  "RESSOURCES": 111204,  "FONDS_PROPRE": 33681,  "EMPLOI": 91839,   "EFFECTIF": 182,  "AGENCE": 13, "COMPTE": 14095},
    "BOA":      {"BILAN": 534863,  "RESSOURCES": 342478,  "FONDS_PROPRE": 43184,  "EMPLOI": 267184,  "EFFECTIF": 347,  "AGENCE": 60, "COMPTE": 358471},
    "BSIC":     {"BILAN": 120203,  "RESSOURCES": 62521,   "FONDS_PROPRE": 4230,   "EMPLOI": 48202,   "EFFECTIF": 154,  "AGENCE": 14, "COMPTE": 36539},
    "CBAO":     {"BILAN": 1033330, "RESSOURCES": 866397,  "FONDS_PROPRE": 109639, "EMPLOI": 700259,  "EFFECTIF": 1037, "AGENCE": 88, "COMPTE": 406914},
    "CBI":      {"BILAN": 185634,  "RESSOURCES": 128012,  "FONDS_PROPRE": 23078,  "EMPLOI": 130097,  "EFFECTIF": 53,   "AGENCE": 5,  "COMPTE": 5705},
    "CDS":      {"BILAN": 230294,  "RESSOURCES": 164921,  "FONDS_PROPRE": 27073,  "EMPLOI": 127188,  "EFFECTIF": 143,  "AGENCE": 8,  "COMPTE": 22943},
    "CISA":     {"BILAN": 57663,   "RESSOURCES": 35645,   "FONDS_PROPRE": 13166,  "EMPLOI": 24122,   "EFFECTIF": 52,   "AGENCE": 2,  "COMPTE": 1430},
    "CITIBANK": {"BILAN": 114862,  "RESSOURCES": 83403,   "FONDS_PROPRE": 21350,  "EMPLOI": 55997,   "EFFECTIF": 29,   "AGENCE": 1,  "COMPTE": 203},
    "ECOBANK":  {"BILAN": 654760,  "RESSOURCES": 526114,  "FONDS_PROPRE": 43391,  "EMPLOI": 319764,  "EFFECTIF": 411,  "AGENCE": 34, "COMPTE": 219924},
    "FBNBANK":  {"BILAN": 29930,   "RESSOURCES": 17386,   "FONDS_PROPRE": 10909,  "EMPLOI": 6338,    "EFFECTIF": 107,  "AGENCE": 3,  "COMPTE": 4050},
    "LBA":      {"BILAN": 328595,  "RESSOURCES": 232700,  "FONDS_PROPRE": 30311,  "EMPLOI": 270554,  "EFFECTIF": 350,  "AGENCE": 38, "COMPTE": 176386},
    "LBO":      {"BILAN": 22941,   "RESSOURCES": 11222,   "FONDS_PROPRE": 11129,  "EMPLOI": 10681,   "EFFECTIF": 37,   "AGENCE": 1,  "COMPTE": 251},
    "NSIA":     {"BILAN": 273646,  "RESSOURCES": 191680,  "FONDS_PROPRE": 14634,  "EMPLOI": 136612,  "EFFECTIF": 140,  "AGENCE": 12, "COMPTE": 35361},
    "ORABANK":  {"BILAN": 312677,  "RESSOURCES": 240227,  "FONDS_PROPRE": 15360,  "EMPLOI": 187420,  "EFFECTIF": 138,  "AGENCE": 11, "COMPTE": 13439},
    "SGBS":     {"BILAN": 975391,  "RESSOURCES": 801792,  "FONDS_PROPRE": 94662,  "EMPLOI": 673354,  "EFFECTIF": 914,  "AGENCE": 40, "COMPTE": 251670},
    "UBA":      {"BILAN": 221723,  "RESSOURCES": 174720,  "FONDS_PROPRE": 30113,  "EMPLOI": 124559,  "EFFECTIF": 243,  "AGENCE": 10, "COMPTE": 59906},
}

FEATURES = ["BILAN", "RESSOURCES", "FONDS_PROPRE", "EMPLOI", "EFFECTIF", "AGENCE", "COMPTE"]
LABELS = {
    "BILAN": "Total Bilan",
    "RESSOURCES": "Ressources",
    "FONDS_PROPRE": "Fonds Propres",
    "EMPLOI": "Emplois",
    "EFFECTIF": "Effectif",
    "AGENCE": "Agences",
    "COMPTE": "Comptes",
}


def _get_ref_df():
    return pd.DataFrame(REF_DATA).T.reset_index().rename(columns={"index": "Sigle"})


def _percentile_rank(value, series):
    return round((series < value).sum() / len(series) * 100, 1)


def _quartile(pct):
    if pct >= 75: return "Q4 — Top 25%"
    if pct >= 50: return "Q3"
    if pct >= 25: return "Q2"
    return "Q1 — Bas de marché"


def _distance(row, new_bank):
    ref_df = _get_ref_df()
    scores = []
    for f in FEATURES:
        col = ref_df[f]
        col_range = col.max() - col.min()
        if col_range == 0:
            continue
        d = abs(row[f] - new_bank.get(f, 0)) / col_range
        scores.append(d)
    return np.mean(scores)


# ── Callback principal ────────────────────────────────────────
@callback(
    Output("pred-placeholder", "style"),
    Output("pred-results",     "style"),
    Output("pred-kpis",        "children"),
    Output("pred-radar",       "figure"),
    Output("pred-classement",  "figure"),
    Output("pred-similaires",  "children"),
    Input("pred-submit", "n_clicks"),
    State("pred-bilan",     "value"),
    State("pred-ressources","value"),
    State("pred-fonds",     "value"),
    State("pred-emplois",   "value"),
    State("pred-effectif",  "value"),
    State("pred-agences",   "value"),
    State("pred-comptes",   "value"),
    prevent_initial_call=True,
)
def compute_position(n, bilan, ressources, fonds, emplois, effectif, agences, comptes):
    T = get_theme()
    accent = "#F0B429"
    hidden  = {"display": "none"}
    visible = {"display": "block"}

    values = [bilan, ressources, fonds, emplois, effectif, agences, comptes]
    if not n or any(v is None for v in values):
        return visible, hidden, [], {}, {}, []

    new_bank = {
        "BILAN": bilan, "RESSOURCES": ressources, "FONDS_PROPRE": fonds,
        "EMPLOI": emplois, "EFFECTIF": effectif, "AGENCE": agences, "COMPTE": comptes,
    }

    ref_df = _get_ref_df()

    # Rangs percentiles
    pcts = {f: _percentile_rank(new_bank[f], ref_df[f]) for f in FEATURES}
    rang_bilan = int((ref_df["BILAN"] > bilan).sum()) + 1
    total = len(ref_df)
    pct_global = _percentile_rank(bilan, ref_df["BILAN"])
    quartile = _quartile(pct_global)

    # ── KPI cards ────────────────────────────────────────────
    def _kpi(label, value, sub, color=accent):
        return html.Div([
            html.Div(label, style={
                "color": T["muted"], "fontFamily": MONO,
                "fontSize": "8px", "letterSpacing": "1.5px",
                "fontWeight": "600", "marginBottom": "8px",
            }),
            html.Div(value, style={
                "color": color, "fontFamily": MONO,
                "fontSize": "26px", "fontWeight": "700", "lineHeight": "1",
            }),
            html.Div(sub, style={
                "color": T["muted"], "fontFamily": MONO,
                "fontSize": "9px", "marginTop": "6px",
            }),
        ], style={
            "background": T["card"],
            "border": f"1px solid {T['border']}",
            "borderTop": f"3px solid {color}",
            "borderRadius": "10px",
            "padding": "16px",
        })

    kpis = [
        _kpi("RANG BILAN", f"{rang_bilan}e / {total}", "par total bilan"),
        _kpi("PERCENTILE", f"{pct_global:.0f}%", quartile,
             "#3FB950" if pct_global >= 50 else "#F85149"),
        _kpi("SCORE GLOBAL", f"{np.mean(list(pcts.values())):.0f}%",
             "moyenne des indicateurs", "#58A6FF"),
    ]

    # ── Radar chart ───────────────────────────────────────────
    cats = [LABELS[f] for f in FEATURES]
    vals_new = [pcts[f] for f in FEATURES]
    vals_med = [50] * len(FEATURES)

    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=vals_med + [vals_med[0]],
        theta=cats + [cats[0]],
        fill="toself",
        name="Médiane secteur",
        line=dict(color=T["border"], width=1),
        fillcolor="rgba(48,54,61,0.3)",
    ))
    radar_fig.add_trace(go.Scatterpolar(
        r=vals_new + [vals_new[0]],
        theta=cats + [cats[0]],
        fill="toself",
        name="Votre banque",
        line=dict(color=accent, width=2),
        fillcolor="rgba(240,180,41,0.15)",
    ))
    radar_fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",          # ← fix: rgba au lieu de 'transparent'
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color=T["muted"], size=8, family=MONO),
                gridcolor=T["border"], linecolor=T["border"],
            ),
            angularaxis=dict(
                tickfont=dict(color=T["muted"], size=9, family=MONO),
                gridcolor=T["border"], linecolor=T["border"],
            ),
        ),
        showlegend=True,
        legend=dict(font=dict(color=T["muted"], size=9, family=MONO), bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=20),
        height=280,
    )

    # ── Classement bilan ──────────────────────────────────────
    new_row = pd.DataFrame([{"Sigle": "Votre banque", "BILAN": float(bilan)}])
    df_plot = pd.concat([ref_df[["Sigle", "BILAN"]], new_row]).sort_values("BILAN", ascending=True).reset_index(drop=True)

    bar_colors = [
        accent if s == "Votre banque" else
        "rgba(63,185,80,0.5)" if float(ref_df[ref_df.Sigle == s]["BILAN"].values[0]) > bilan
        else "rgba(48,54,61,0.6)"
        for s in df_plot["Sigle"]
    ]

    # Couleur du tick "Votre banque" — on colore via marker, pas tickfont
    classement_fig = go.Figure(go.Bar(
        x=df_plot["BILAN"] / 1000,
        y=df_plot["Sigle"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{v/1000:.0f} Md" for v in df_plot["BILAN"]],
        textposition="outside",
        textfont=dict(color=T["muted"], size=9, family=MONO),
    ))
    classement_fig.update_layout(
        xaxis=dict(
            title="Total Bilan (Milliards FCFA)",
            titlefont=dict(color=T["muted"], size=9, family=MONO),
            tickfont=dict(color=T["muted"], size=9, family=MONO),
            gridcolor=T["border"], linecolor=T["border"],
        ),
        yaxis=dict(
            tickfont=dict(color=T["muted"], size=9, family=MONO),  # ← fix: une seule couleur
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=60, t=10, b=30),
        height=520,
        showlegend=False,
    )

    # ── Banques similaires ────────────────────────────────────
    distances = ref_df.apply(lambda row: _distance(row, new_bank), axis=1)
    ref_df["dist"] = distances
    top3 = ref_df.nsmallest(3, "dist")

    similaires = []
    for i, (_, row) in enumerate(top3.iterrows()):
        score_sim = round((1 - row["dist"]) * 100, 0)
        similaires.append(html.Div([
            html.Div([
                html.Div(f"#{i+1}", style={
                    "color": accent, "fontFamily": MONO,
                    "fontSize": "10px", "fontWeight": "700",
                    "marginRight": "10px", "minWidth": "20px",
                }),
                html.Div([
                    html.Div(row["Sigle"], style={
                        "color": T["text"], "fontFamily": MONO,
                        "fontSize": "12px", "fontWeight": "600",
                    }),
                    html.Div(f"Similarité {score_sim:.0f}%", style={
                        "color": T["muted"], "fontFamily": MONO, "fontSize": "9px",
                    }),
                ]),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div(style={
                "height": "3px",
                "background": f"linear-gradient(90deg, {accent}, transparent)",
                "borderRadius": "2px", "marginTop": "8px",
                "width": f"{score_sim}%", "opacity": "0.5",
            }),
        ], style={
            "padding": "12px", "marginBottom": "8px",
            "background": T["bg"],
            "border": f"1px solid {T['border']}",
            "borderRadius": "8px",
        }))

    return hidden, visible, kpis, radar_fig, classement_fig, similaires
