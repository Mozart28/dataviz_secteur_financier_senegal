# ============================================================
#  sectors/assurance/pages/scoring/layout.py
#  Page 05 — Scoring Risque (ML embarqué)
# ============================================================

from dash import html, dcc
from config import get_theme, MONO, SERIF
from components.footer_bar import footer_bar
from components.tooltip_info import card_with_tooltip
from sectors.assurance.data.tooltips import TOOLTIPS
from sectors.assurance.data.loader import get_dataframe

T      = get_theme("assurance")
ACCENT = T["accent"]


def _section_title(text):
    return html.Div(text, style={
        "color": ACCENT, "fontSize": "9px", "letterSpacing": "2.5px",
        "fontFamily": MONO, "fontWeight": "600",
        "marginBottom": "14px", "textTransform": "uppercase",
    })


def _card(children, extra=None):
    s = {"background": T["card"], "border": f"1px solid {T['border']}",
         "borderRadius": "8px", "padding": "18px"}
    if extra:
        s.update(extra)
    return html.Div(children, style=s)


def _graph(gid, height="240px"):
    return dcc.Loading(
        dcc.Graph(id=gid, style={"height": height},
                  config={"displayModeBar": False}),
        type="dot", color=ACCENT, style={"minHeight": height},
    )


def get_layout():
    df = get_dataframe()

    # Données scoring statiques au chargement
    footer_data = {
        "auc":             0.475,
        "pct_haut_risque": 40.0,
        "score_moy":       0.379,
        "best_seg_freq":   11.5,
        "ratio_sp":        df['montant_sinistres'].sum() / df['montant_prime'].sum() * 100,
    }
    branches = sorted(df['type_assurance'].dropna().unique().tolist())
    regions  = sorted(df['region'].dropna().unique().tolist())

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("CIMA · Secteur Assurance · Sénégal", style={
                    "color": ACCENT, "fontSize": "10px",
                    "letterSpacing": "2px", "fontFamily": MONO,
                    "fontWeight": "600"}),
                html.H1("Scoring Risque", style={
                    "margin": "6px 0 0", "fontSize": "20px",
                    "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF}),
                html.P("Modèle Random Forest · Segmentation · Simulateur individuel",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),

            # Badge modèle
            html.Div([
                html.Div("MODÈLE ACTIF", style={"color": T["muted"],
                    "fontSize": "8px", "fontFamily": MONO,
                    "letterSpacing": "1.5px", "marginBottom": "6px"}),
                html.Div([
                    html.Span("● ", style={"color": T["green"], "fontSize": "10px"}),
                    html.Span("Random Forest · 100 arbres",
                        style={"color": T["text"], "fontFamily": MONO,
                               "fontSize": "11px", "fontWeight": "600"}),
                ]),
                html.Div(id="ass-scor-badge-auc",
                    style={"marginTop": "4px"}),
            ], style={
                "background": T["card2"], "border": f"1px solid {T['border']}",
                "borderLeft": f"3px solid {T['green']}",
                "borderRadius": "6px", "padding": "12px 16px",
            }),
        ], style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "flex-end", "flexWrap": "wrap",
            "padding": "20px 28px",
            "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)",
        }),

        # ── Corps ─────────────────────────────────────────────
        html.Div([

            # Ligne 1 — KPIs segments + AUC
            html.Div(id="ass-scor-kpis",
                     style={"display": "flex", "gap": "12px",
                            "marginBottom": "14px", "flexWrap": "wrap"}),

            # Ligne 2 — Distribution scores + Feature importance
            html.Div([
                card_with_tooltip(
                    "Distribution des scores de risque",
                    "ass-scor-graph-distrib",
                    "scor-distrib",
                    TOOLTIPS["scor-distrib"],
                    "260px",
                    ACCENT, extra_style={'flex': '1.2', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Importance des variables (RF)",
                    "ass-scor-graph-importance",
                    "scor-importance",
                    TOOLTIPS["scor-importance"],
                    "260px",
                    ACCENT, extra_style={'flex': '1', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "ROC Curve",
                    "ass-scor-graph-roc",
                    "scor-roc",
                    TOOLTIPS["scor-roc"],
                    "260px",
                    ACCENT, extra_style={'flex': '1'},
                ),

            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 3 — Sinistralité par segment + Heatmap
            html.Div([
                card_with_tooltip(
                    "Sinistralité réelle vs score prédit par segment",
                    "ass-scor-graph-segments",
                    "scor-segments",
                    TOOLTIPS["scor-segments"],
                    "230px",
                    ACCENT, extra_style={'flex': '1.3', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Score moyen — Branche × Région",
                    "ass-scor-graph-heatmap",
                    "scor-heatmap",
                    TOOLTIPS["scor-heatmap"],
                    "230px",
                    ACCENT, extra_style={'flex': '1'},
                ),

            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 4 — Simulateur individuel
            _card([
                _section_title("Simulateur — Score individuel"),
                html.Div([

                    # Inputs
                    html.Div([
                        # Âge
                        html.Div([
                            html.Div("ÂGE", style={"color": T["muted"],
                                "fontSize": "9px", "fontFamily": MONO,
                                "letterSpacing": "1.5px", "marginBottom": "8px"}),
                            dcc.Slider(id="ass-scor-sim-age",
                                min=18, max=79, step=1, value=40,
                                marks={18:"18", 30:"30", 45:"45",
                                       60:"60", 79:"79"},
                                tooltip={"placement":"bottom","always_visible":True}),
                        ], style={"flex": "1.2", "marginRight": "20px"}),

                        # Durée
                        html.Div([
                            html.Div("DURÉE CONTRAT (ANS)", style={
                                "color": T["muted"], "fontSize": "9px",
                                "fontFamily": MONO, "letterSpacing": "1.5px",
                                "marginBottom": "8px"}),
                            dcc.Slider(id="ass-scor-sim-duree",
                                min=1, max=10, step=1, value=5,
                                marks={1:"1",3:"3",5:"5",7:"7",10:"10"},
                                tooltip={"placement":"bottom","always_visible":True}),
                        ], style={"flex": "1", "marginRight": "20px"}),

                        # Bonus-malus
                        html.Div([
                            html.Div("BONUS-MALUS", style={
                                "color": T["muted"], "fontSize": "9px",
                                "fontFamily": MONO, "letterSpacing": "1.5px",
                                "marginBottom": "8px"}),
                            dcc.Slider(id="ass-scor-sim-bm",
                                min=0.5, max=1.5, step=0.05, value=1.0,
                                marks={0.5:"0.5",0.75:"0.75",
                                       1.0:"1.0",1.25:"1.25",1.5:"1.5"},
                                tooltip={"placement":"bottom","always_visible":True}),
                        ], style={"flex": "1", "marginRight": "20px"}),

                        # Prime
                        html.Div([
                            html.Div("MONTANT PRIME", style={
                                "color": T["muted"], "fontSize": "9px",
                                "fontFamily": MONO, "letterSpacing": "1.5px",
                                "marginBottom": "8px"}),
                            dcc.Slider(id="ass-scor-sim-prime",
                                min=100, max=2000, step=50, value=1000,
                                marks={100:"100",500:"500",
                                       1000:"1k",1500:"1.5k",2000:"2k"},
                                tooltip={"placement":"bottom","always_visible":True}),
                        ], style={"flex": "1"}),

                    ], style={"display": "flex", "marginBottom": "20px",
                              "flexWrap": "wrap", "gap": "0"}),

                    html.Div([
                        # Sexe
                        html.Div([
                            html.Div("SEXE", style={"color": T["muted"],
                                "fontSize": "9px", "fontFamily": MONO,
                                "letterSpacing": "1.5px", "marginBottom": "8px"}),
                            dcc.RadioItems(
                                id="ass-scor-sim-sexe",
                                options=[
                                    {"label": " Masculin", "value": "masculin"},
                                    {"label": " Féminin",  "value": "feminin"},
                                ],
                                value="masculin", inline=True,
                                inputStyle={"marginRight": "4px"},
                                labelStyle={"color": T["muted"], "fontFamily": MONO,
                                    "fontSize": "11px", "marginRight": "16px",
                                    "cursor": "pointer"},
                            ),
                        ], style={"marginRight": "28px"}),

                        # Branche
                        html.Div([
                            html.Div("BRANCHE", style={"color": T["muted"],
                                "fontSize": "9px", "fontFamily": MONO,
                                "letterSpacing": "1.5px", "marginBottom": "8px"}),
                            dcc.Dropdown(
                                id="ass-scor-sim-branche",
                                options=[{"label": b, "value": b}
                                         for b in branches],
                                value=branches[0], clearable=False,
                                style={"width": "140px", "fontSize": "12px"},
                            ),
                        ], style={"marginRight": "28px"}),

                        # Région
                        html.Div([
                            html.Div("RÉGION", style={"color": T["muted"],
                                "fontSize": "9px", "fontFamily": MONO,
                                "letterSpacing": "1.5px", "marginBottom": "8px"}),
                            dcc.Dropdown(
                                id="ass-scor-sim-region",
                                options=[{"label": r, "value": r}
                                         for r in regions],
                                value=regions[0], clearable=False,
                                style={"width": "140px", "fontSize": "12px"},
                            ),
                        ], style={"marginRight": "40px"}),

                        # Résultat
                        html.Div(id="ass-scor-sim-result",
                            style={"marginLeft": "auto",
                                   "alignSelf": "flex-end"}),

                    ], style={"display": "flex", "alignItems": "flex-end",
                              "flexWrap": "wrap"}),
                ]),
            ]),

        ], style={"padding": "14px 24px", "overflow": "auto"}),

            footer_bar("scoring", "assurance", footer_data),
    ], style={"display": "flex", "flexDirection": "column",
              "minHeight": "100vh", "background": T["bg"],
              "color": T["text"],
              "paddingBottom": "52px"})
