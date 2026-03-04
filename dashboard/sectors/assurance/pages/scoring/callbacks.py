# ============================================================
#  sectors/assurance/pages/scoring/callbacks.py
#  ML embarqué — Random Forest entraîné au démarrage
# ============================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, html

from config import get_theme, plotly_base, MONO
from sectors.assurance.data.loader import get_dataframe

# Sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve

T      = get_theme("assurance")
ACCENT = T["accent"]

SEGMENT_COLORS = {
    "Très faible": T["green"],
    "Faible":      "#86EFAC",
    "Modéré":      T["accent"],
    "Élevé":       "#F97316",
    "Très élevé":  T["red"],
}
SEGMENTS = ["Très faible", "Faible", "Modéré", "Élevé", "Très élevé"]
FEAT_COLS = ['age', 'duree_contrat', 'montant_prime', 'bonus_malus',
             'sexe_enc', 'type_assurance_enc', 'region_enc', 'tranche_enc']
FEAT_LABELS = {
    'montant_prime':        'Prime',
    'bonus_malus':          'Bonus-malus',
    'age':                  'Âge',
    'duree_contrat':        'Durée contrat',
    'region_enc':           'Région',
    'type_assurance_enc':   'Branche',
    'tranche_enc':          'Tranche âge',
    'sexe_enc':             'Sexe',
}

# ── Encodeurs ─────────────────────────────────────────────────
_le_sexe    = LabelEncoder().fit(['feminin', 'masculin'])
_le_branche = LabelEncoder().fit(['Auto', 'Habitation', 'Santé', 'Vie'])
_le_region  = LabelEncoder().fit(['Dakar', 'Kaolack', 'Saint-Louis', 'Thiès'])
_TRANCHE_MAP = {'18–30': 0, '31–45': 1, '46–60': 2, '61–79': 3}


def _prepare_X(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d['sexe_enc']             = _le_sexe.transform(d['sexe'].astype(str))
    d['type_assurance_enc']   = _le_branche.transform(d['type_assurance'].astype(str))
    d['region_enc']           = _le_region.transform(d['region'].astype(str))
    d['tranche_enc']          = d['tranche_age'].astype(str).map(_TRANCHE_MAP).fillna(0)
    return d[FEAT_COLS].fillna(0)


# ── Entraînement du modèle (une seule fois au import) ─────────
_MODEL    = None
_DF_SCORED = None
_AUC       = None
_Y_TEST    = None
_Y_PROB    = None


def _get_model():
    global _MODEL, _DF_SCORED, _AUC, _Y_TEST, _Y_PROB
    if _MODEL is not None:
        return _MODEL, _DF_SCORED, _AUC

    df = get_dataframe()
    X  = _prepare_X(df)
    y  = df['sinistre'].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(
        n_estimators=100, random_state=42,
        max_depth=6, min_samples_leaf=10, n_jobs=-1)
    model.fit(X_train, y_train)

    _Y_TEST  = y_test
    _Y_PROB  = model.predict_proba(X_test)[:, 1]
    _AUC     = roc_auc_score(y_test, _Y_PROB)

    # Scorer tout le portefeuille
    df_s = df.copy()
    df_s['score'] = model.predict_proba(X)[:, 1]
    df_s['segment'] = pd.qcut(df_s['score'], q=5, labels=SEGMENTS)

    _MODEL     = model
    _DF_SCORED = df_s
    return _MODEL, _DF_SCORED, _AUC


def _base(**kw):
    return plotly_base("assurance", **kw)


# ── Badge AUC ─────────────────────────────────────────────────

@callback(
    Output("ass-scor-badge-auc", "children"),
    Input("ass-scor-badge-auc",  "id"),
)
def cb_badge(_):
    _, _, auc = _get_model()
    qual  = "Bon" if auc > 0.7 else "Modéré" if auc > 0.55 else "Faible"
    color = T["green"] if auc > 0.7 else T["accent"] if auc > 0.55 else T["muted"]
    return html.Span(
        f"AUC = {auc:.3f} · {qual}",
        style={"color": color, "fontFamily": MONO,
               "fontSize": "10px", "fontWeight": "600"},
    )


# ── KPIs segments ─────────────────────────────────────────────

@callback(
    Output("ass-scor-kpis", "children"),
    Input("ass-scor-badge-auc", "id"),
)
def cb_kpis(_):
    _, df_s, auc = _get_model()

    cards = []
    for seg in SEGMENTS:
        d     = df_s[df_s['segment'] == seg]
        freq  = d['sinistre'].mean() * 100
        n     = len(d)
        pm    = d['montant_prime'].mean()
        color = SEGMENT_COLORS[seg]

        cards.append(html.Div([
            html.Div(seg, style={"color": color, "fontSize": "9px",
                "fontFamily": MONO, "letterSpacing": "1.2px",
                "textTransform": "uppercase", "marginBottom": "8px",
                "fontWeight": "600"}),
            html.Div(f"{freq:.0f}%", style={"color": T["text"],
                "fontSize": "22px", "fontWeight": "700",
                "fontFamily": MONO, "lineHeight": "1"}),
            html.Div("fréq. sinistres", style={"color": T["muted"],
                "fontSize": "9px", "fontFamily": MONO, "marginTop": "4px"}),
            html.Div(f"{n} contrats · prime moy {pm:.0f}",
                style={"color": T["muted"], "fontSize": "9px",
                       "fontFamily": MONO, "marginTop": "4px",
                       "opacity": "0.7"}),
        ], style={
            "background": T["card2"],
            "border": f"1px solid {T['border']}",
            "borderTop": f"3px solid {color}",
            "borderRadius": "8px", "padding": "16px", "flex": "1",
        }))

    return cards


# ── Distribution scores ────────────────────────────────────────

@callback(
    Output("ass-scor-graph-distrib", "figure"),
    Input("ass-scor-badge-auc", "id"),
)
def cb_distrib(_):
    _, df_s, _ = _get_model()

    fig = go.Figure()

    # Histogramme global
    fig.add_trace(go.Histogram(
        x=df_s['score'], nbinsx=40,
        name="Tous", marker_color=ACCENT, opacity=0.4,
        hovertemplate="Score [%{x:.2f}] : %{y} contrats<extra></extra>",
    ))

    # Par segment couleur
    for seg in SEGMENTS:
        d = df_s[df_s['segment'] == seg]
        fig.add_trace(go.Histogram(
            x=d['score'], nbinsx=20,
            name=seg, marker_color=SEGMENT_COLORS[seg], opacity=0.7,
            visible="legendonly",
            hovertemplate=f"<b>{seg}</b> [%{{x:.2f}}] : %{{y}}<extra></extra>",
        ))

    # Lignes de coupure des quintiles
    for i, (pct, label) in enumerate(zip(
        [0.2, 0.4, 0.6, 0.8],
        ["Q1", "Q2", "Q3", "Q4"]
    )):
        cut = df_s['score'].quantile(pct)
        fig.add_vline(x=cut, line_dash="dot",
            line_color=T["border"], line_width=1,
            annotation_text=label,
            annotation_font=dict(size=8, color=T["muted"], family=MONO),
            annotation_position="top")

    layout = _base(xaxis_title="Score de risque",
                   yaxis_title="Nb contrats", showlegend=True,
                   barmode="overlay",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Feature importance ────────────────────────────────────────

@callback(
    Output("ass-scor-graph-importance", "figure"),
    Input("ass-scor-badge-auc", "id"),
)
def cb_importance(_):
    model, _, _ = _get_model()

    fi = pd.Series(model.feature_importances_,
                   index=FEAT_COLS).sort_values()
    labels = [FEAT_LABELS.get(f, f) for f in fi.index]

    # Gradient de couleur selon importance
    max_fi  = fi.max()
    colors  = [f"rgba(88,166,255,{0.3 + 0.7 * v / max_fi})"
               for v in fi.values]

    fig = go.Figure(go.Bar(
        x=fi.values, y=labels,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.3f}" for v in fi.values],
        textposition="outside",
        textfont=dict(size=9, family=MONO, color=T["text"]),
        hovertemplate="<b>%{y}</b> : %{x:.4f}<extra></extra>",
    ))

    layout = _base(xaxis_title="Importance Gini", showlegend=False, bargap=0.25)
    layout["yaxis"] = dict(tickfont=dict(size=10, family=MONO),
                           gridcolor=T["border"], showline=False)
    layout["margin"] = dict(l=10, r=50, t=10, b=36)
    fig.update_layout(**layout)
    return fig


# ── Courbe ROC ────────────────────────────────────────────────

@callback(
    Output("ass-scor-graph-roc", "figure"),
    Input("ass-scor-badge-auc", "id"),
)
def cb_roc(_):
    _, _, auc = _get_model()
    fpr, tpr, _ = roc_curve(_Y_TEST, _Y_PROB)

    fig = go.Figure()

    # Zone sous la courbe
    fig.add_trace(go.Scatter(
        x=fpr.tolist() + [0],
        y=tpr.tolist() + [0],
        fill="toself",
        fillcolor=f"rgba(88,166,255,0.10)",
        line=dict(color="rgba(0,0,0,0)"),
        hoverinfo="skip", showlegend=False,
    ))

    # Courbe ROC
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr,
        mode="lines", name=f"ROC (AUC={auc:.3f})",
        line=dict(color=ACCENT, width=2.5),
        hovertemplate="FPR=%{x:.2f}  TPR=%{y:.2f}<extra></extra>",
    ))

    # Diagonale aléatoire
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines",
        name="Aléatoire (AUC=0.5)",
        line=dict(color=T["muted"], width=1, dash="dot"),
        hoverinfo="skip",
    ))

    # Annotation AUC
    fig.add_annotation(
        x=0.6, y=0.3,
        text=f"AUC = {auc:.3f}",
        showarrow=False,
        font=dict(size=12, color=ACCENT, family=MONO, weight="bold"),
        bgcolor=T["card2"],
        bordercolor=T["border"],
        borderwidth=1,
        borderpad=6,
    )

    layout = _base(xaxis_title="Taux faux positifs",
                   yaxis_title="Taux vrais positifs", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
    layout["xaxis"]["range"] = [0, 1]
    layout["yaxis"]["range"] = [0, 1]
    layout["margin"] = dict(l=12, r=12, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Sinistralité réelle vs prédite par segment ────────────────

@callback(
    Output("ass-scor-graph-segments", "figure"),
    Input("ass-scor-badge-auc", "id"),
)
def cb_segments(_):
    _, df_s, _ = _get_model()

    agg = df_s.groupby("segment", observed=True).agg(
        freq_reelle =("sinistre",  "mean"),
        score_moy   =("score",     "mean"),
        n           =("id_assure", "count"),
        prime_moy   =("montant_prime", "mean"),
    ).reset_index()
    agg["freq_reelle"] *= 100
    agg["score_pred"]   = agg["score_moy"] * 100

    segs   = agg["segment"].astype(str).tolist()
    colors = [SEGMENT_COLORS[s] for s in segs]

    fig = go.Figure()

    # Barres fréquence réelle
    fig.add_trace(go.Bar(
        x=segs, y=agg["freq_reelle"],
        name="Fréq. réelle (%)",
        marker=dict(color=colors, opacity=0.8, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in agg["freq_reelle"]],
        textposition="outside",
        textfont=dict(size=10, family=MONO, color=T["text"]),
        yaxis="y",
        hovertemplate="<b>%{x}</b> fréq réelle : %{y:.1f}%<extra></extra>",
    ))

    # Courbe score prédit
    fig.add_trace(go.Scatter(
        x=segs, y=agg["score_pred"],
        name="Score prédit (%)",
        mode="lines+markers",
        line=dict(color="white", width=2, dash="dot"),
        marker=dict(size=8, color="white", symbol="diamond",
                    line=dict(color=T["bg"], width=1.5)),
        yaxis="y2",
        hovertemplate="<b>%{x}</b> score prédit : %{y:.1f}%<extra></extra>",
    ))

    layout = _base(showlegend=True, bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
        xaxis_title="Segment de risque")
    layout["yaxis"]["title"] = dict(text="Fréq. réelle (%)", font=dict(size=9))
    layout["yaxis2"] = dict(
        title=dict(text="Score prédit (%)", font=dict(size=9, color="white")),
        overlaying="y", side="right",
        tickfont=dict(size=9, color="white"),
        gridcolor="rgba(0,0,0,0)", showline=False, zeroline=False,
    )
    layout["margin"] = dict(l=12, r=50, t=28, b=36)
    fig.update_layout(**layout)
    return fig


# ── Heatmap score moyen branche × région ─────────────────────

@callback(
    Output("ass-scor-graph-heatmap", "figure"),
    Input("ass-scor-badge-auc", "id"),
)
def cb_heatmap(_):
    _, df_s, _ = _get_model()

    pvt = df_s.pivot_table(
        index="type_assurance", columns="region",
        values="score", aggfunc="mean",
    )
    branches = pvt.index.tolist()
    regions  = pvt.columns.tolist()
    z        = pvt.values

    text = [[f"{z[i,j]:.3f}" for j in range(len(regions))]
            for i in range(len(branches))]

    fig = go.Figure(go.Heatmap(
        z=z, x=regions, y=branches,
        text=text, texttemplate="%{text}",
        textfont=dict(size=11, family=MONO),
        colorscale=[
            [0.0, T["green"]],
            [0.4, T["accent"]],
            [0.7, "#F97316"],
            [1.0, T["red"]],
        ],
        showscale=True,
        colorbar=dict(
            thickness=10, len=0.8,
            tickfont=dict(size=8, color=T["muted"], family=MONO),
            title=dict(text="Score", font=dict(size=9, color=T["muted"])),
        ),
        hovertemplate=(
            "<b>%{y} · %{x}</b><br>"
            "Score moyen : %{z:.3f}<extra></extra>"
        ),
    ))

    layout = _base(showlegend=False)
    layout["xaxis"].update(tickfont=dict(size=10, family=MONO))
    layout["yaxis"].update(tickfont=dict(size=10, family=MONO))
    layout["margin"] = dict(l=10, r=60, t=10, b=30)
    fig.update_layout(**layout)
    return fig


# ── Simulateur individuel ─────────────────────────────────────

@callback(
    Output("ass-scor-sim-result", "children"),
    Input("ass-scor-sim-age",     "value"),
    Input("ass-scor-sim-duree",   "value"),
    Input("ass-scor-sim-bm",      "value"),
    Input("ass-scor-sim-prime",   "value"),
    Input("ass-scor-sim-sexe",    "value"),
    Input("ass-scor-sim-branche", "value"),
    Input("ass-scor-sim-region",  "value"),
)
def cb_simulateur(age, duree, bm, prime, sexe, branche, region):
    model, df_s, _ = _get_model()

    # Encoder les inputs
    try:
        sexe_enc    = int(_le_sexe.transform([sexe])[0])
        branche_enc = int(_le_branche.transform([branche])[0])
        region_enc  = int(_le_region.transform([region])[0])
    except Exception:
        sexe_enc = branche_enc = region_enc = 0

    age   = age   or 40
    duree = duree or 5
    bm    = bm    or 1.0
    prime = prime or 1000

    if age < 30:      tranche_enc = 0
    elif age < 45:    tranche_enc = 1
    elif age < 60:    tranche_enc = 2
    else:             tranche_enc = 3

    X_sim = np.array([[age, duree, prime, bm,
                        sexe_enc, branche_enc, region_enc, tranche_enc]])
    score = float(model.predict_proba(X_sim)[0, 1])

    # Segment
    q = df_s['score'].quantile([0.2, 0.4, 0.6, 0.8]).values
    if   score <= q[0]: seg = "Très faible"
    elif score <= q[1]: seg = "Faible"
    elif score <= q[2]: seg = "Modéré"
    elif score <= q[3]: seg = "Élevé"
    else:               seg = "Très élevé"

    color = SEGMENT_COLORS[seg]

    # Jauge visuelle
    pct   = int(score * 100)
    width = max(4, pct)

    return html.Div([
        html.Div("SCORE DE RISQUE", style={"color": T["muted"],
            "fontSize": "9px", "fontFamily": MONO,
            "letterSpacing": "1.5px", "marginBottom": "10px"}),

        # Valeur principale
        html.Div([
            html.Span(f"{score:.3f}", style={"color": color,
                "fontSize": "36px", "fontWeight": "700",
                "fontFamily": MONO, "lineHeight": "1"}),
            html.Span(f"  {seg}", style={"color": color,
                "fontSize": "12px", "fontFamily": MONO,
                "fontWeight": "600", "marginLeft": "8px"}),
        ]),

        # Barre de progression
        html.Div([
            html.Div(style={
                "height": "6px",
                "width": f"{width}%",
                "background": f"linear-gradient(90deg, {T['green']}, {color})",
                "borderRadius": "3px",
                "transition": "width 0.3s ease",
            }),
        ], style={
            "background": T["border"],
            "borderRadius": "3px",
            "marginTop": "10px",
            "marginBottom": "8px",
            "overflow": "hidden",
        }),

        # Percentile dans le portefeuille
        html.Div([
            pct_rank := (df_s['score'] <= score).mean() * 100,
            html.Span(
                f"Percentile {pct_rank:.0f}e du portefeuille",
                style={"color": T["muted"], "fontSize": "10px",
                       "fontFamily": MONO}
            ),
        ]),
    ], style={
        "background": T["card2"],
        "border": f"1px solid {color}",
        "borderRadius": "8px",
        "padding": "18px 24px",
        "minWidth": "260px",
    })
