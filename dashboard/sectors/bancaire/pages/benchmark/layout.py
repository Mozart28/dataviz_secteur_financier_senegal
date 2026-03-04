# ============================================================
#  pages/benchmark/layout.py — Benchmark & Positionnement
#  Outil pour une nouvelle banque entrant sur le marché
# ============================================================

from dash import html, dcc
from config import T, MONO, SERIF
from components.tooltip_info import card_with_tooltip
from data.tooltips import TOOLTIPS
from data import get_dataframe


def _section_title(text):
    return html.Div(text, style={"color": T["accent"], "fontSize": "9px",
        "letterSpacing": "2.5px", "fontFamily": MONO, "fontWeight": "600",
        "marginBottom": "14px", "textTransform": "uppercase"})


def _card(children, extra=None):
    s = {"background": T["card"], "border": f"1px solid {T['border']}",
         "borderRadius": "8px", "padding": "20px"}
    if extra: s.update(extra)
    return html.Div(children, style=s)


def _graph(gid, height="220px"):
    return dcc.Loading(
        dcc.Graph(id=gid, style={"height": height}, config={"displayModeBar": False}),
        type="dot", color=T["accent"], style={"minHeight": height},
    )


def get_layout():
    df = get_dataframe()
    groupes = sorted(df["Goupe_Bancaire"].dropna().unique().tolist())

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("BCEAO · Outil d'entrée de marché", style={"color": T["accent"],
                    "fontSize": "10px", "letterSpacing": "2px",
                    "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Benchmark & Positionnement", style={"margin": "6px 0 0",
                    "fontSize": "20px", "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF, "letterSpacing": "0.3px"}),
                html.P("Simulez votre positionnement dans le secteur bancaire sénégalais",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),
        ], style={"padding": "20px 28px", "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)"}),

        # ── Formulaire de simulation ──────────────────────────
        html.Div([
            _card([
                html.Div("PARAMÈTRES DE VOTRE BANQUE", style={"color": T["accent"],
                    "fontSize": "9px", "letterSpacing": "2.5px", "fontFamily": MONO,
                    "fontWeight": "600", "marginBottom": "20px"}),
                html.Div([
                    # Capital initial
                    html.Div([
                        html.Div("Capital initial (M FCFA)", style={"color": T["muted"],
                            "fontSize": "10px", "fontFamily": MONO, "marginBottom": "8px"}),
                        dcc.Input(
                            id="bm-input-capital",
                            type="number", value=15000, min=0, step=500,
                            placeholder="Ex: 15000",
                            style={"background": T["card2"], "border": f"1px solid {T['border']}",
                                "color": T["text"], "fontFamily": MONO, "fontSize": "14px",
                                "padding": "10px 14px", "borderRadius": "6px", "width": "180px"},
                        ),
                    ]),
                    # PNB cible
                    html.Div([
                        html.Div("PNB cible annuel (M FCFA)", style={"color": T["muted"],
                            "fontSize": "10px", "fontFamily": MONO, "marginBottom": "8px"}),
                        dcc.Input(
                            id="bm-input-pnb",
                            type="number", value=10000, min=0, step=500,
                            placeholder="Ex: 10000",
                            style={"background": T["card2"], "border": f"1px solid {T['border']}",
                                "color": T["text"], "fontFamily": MONO, "fontSize": "14px",
                                "padding": "10px 14px", "borderRadius": "6px", "width": "180px"},
                        ),
                    ], style={"marginLeft": "24px"}),
                    # Groupe cible
                    html.Div([
                        html.Div("Groupe bancaire visé", style={"color": T["muted"],
                            "fontSize": "10px", "fontFamily": MONO, "marginBottom": "8px"}),
                        dcc.Dropdown(
                            id="bm-dropdown-groupe",
                            options=[{"label": g.replace("Groupes ",""), "value": g}
                                     for g in groupes],
                            value=groupes[0] if groupes else None,
                            clearable=False,
                            style={"width": "200px", "fontSize": "12px"},
                        ),
                    ], style={"marginLeft": "24px"}),
                    # Année de référence
                    html.Div([
                        html.Div("Année de référence", style={"color": T["muted"],
                            "fontSize": "10px", "fontFamily": MONO, "marginBottom": "8px"}),
                        dcc.Dropdown(
                            id="bm-dropdown-annee",
                            options=[{"label": str(y), "value": y}
                                     for y in sorted(df["ANNEE"].dropna().unique())],
                            value=int(df["ANNEE"].max()),
                            clearable=False,
                            style={"width": "110px", "fontSize": "12px"},
                        ),
                    ], style={"marginLeft": "24px"}),
                ], style={"display": "flex", "alignItems": "flex-end", "flexWrap": "wrap", "gap": "0"}),
            ]),
        ], style={"padding": "16px 24px 0"}),

        # ── Résultats de positionnement ───────────────────────
        dcc.Loading(
            html.Div(id="bm-position-cards", style={
                "display": "grid", "gridTemplateColumns": "repeat(4,1fr)",
                "gap": "1px", "background": T["border"],
                "margin": "16px 24px 0",
                "borderRadius": "8px", "overflow": "hidden",
            }),
            type="dot", color=T["accent"],
        ),

        # ── Corps principal ───────────────────────────────────
        html.Div([

            # Ligne 1 : Positionnement PNB + Allocation bilan
            html.Div([
                card_with_tooltip(
                    "Votre positionnement dans le classement PNB", "bm-graph-rang",
                    "bm-classement", TOOLTIPS["bm-classement"],
                    "220px", T["accent"],
                    extra_style={"flex": "1.4", "marginRight": "14px",
                        "background": T["card"], "border": f"1px solid {T['border']}"},
                ),
                card_with_tooltip(
                    "Allocation du bilan — groupe de reference", "bm-graph-alloc",
                    "bm-allocation", TOOLTIPS["bm-allocation"],
                    "220px", T["accent"],
                    extra_style={"flex": "1",
                        "background": T["card"], "border": f"1px solid {T['border']}"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),
            html.Div(id="bm-rang-label", style={"display": "none"}),
            html.Div(id="bm-alloc-label", style={"display": "none"}),

            # Ligne 2 : Ratios cibles + Écart à combler
            html.Div([
                _card([
                    _section_title("Ratios à viser — top quartile du secteur"),
                    html.Div(id="bm-ratios-cibles"),
                ], {"flex": "1", "marginRight": "14px"}),

                _card([
                    _section_title("Capital minimum par niveau de marché"),
                    html.Div(id="bm-seuils-label", style={"color": T["muted"],
                        "fontSize": "9px", "fontFamily": MONO, "marginBottom": "8px"}),
                    _graph("bm-graph-seuils", "220px"),
                ], {"flex": "1.4"}),

            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 3 : Stratégie recommandée
            _card([
                _section_title("Analyse stratégique — recommandations"),
                html.Div(id="bm-recommandations"),
            ]),

            # ── Séparateur ────────────────────────────────────
            html.Div([
                html.Div(style={"height": "1px", "background":
                    f"linear-gradient(90deg, transparent, {T['accent']}, transparent)",
                    "margin": "8px 0"}),
                html.Div("MODULE PRÉDICTIF N+1 · N+2 · N+3", style={
                    "color": T["accent"], "fontSize": "9px", "letterSpacing": "3px",
                    "fontFamily": MONO, "textAlign": "center", "fontWeight": "600",
                    "padding": "4px 0 12px",
                }),
            ]),

            # Ligne 4 : Sélecteur banque à prédire
            _card([
                html.Div([
                    html.Div([
                        html.Div("BANQUE À ANALYSER", style={"color": T["muted"],
                            "fontSize": "9px", "fontFamily": MONO,
                            "letterSpacing": "1.5px", "marginBottom": "8px"}),
                        dcc.Dropdown(
                            id="bm-pred-dropdown-banque",
                            options=[{"label": b, "value": b}
                                     for b in sorted(df["Sigle"].dropna().unique())],
                            value=sorted(df["Sigle"].dropna().unique())[0],
                            clearable=False,
                            style={"width": "160px", "fontSize": "12px"},
                        ),
                    ]),
                    html.Div([
                        html.Div("SCÉNARIO AFFICHÉ", style={"color": T["muted"],
                            "fontSize": "9px", "fontFamily": MONO,
                            "letterSpacing": "1.5px", "marginBottom": "8px"}),
                        dcc.RadioItems(
                            id="bm-pred-scenario",
                            options=[
                                {"label": " Pessimiste", "value": "pessimiste"},
                                {"label": " Central",    "value": "central"},
                                {"label": " Optimiste",  "value": "optimiste"},
                                {"label": " Tous",       "value": "all"},
                            ],
                            value="all", inline=True,
                            inputStyle={"marginRight": "4px"},
                            labelStyle={"color": T["muted"], "fontFamily": MONO,
                                "fontSize": "11px", "marginRight": "16px",
                                "cursor": "pointer"},
                        ),
                    ], style={"marginLeft": "28px"}),
                    # Fiabilité
                    html.Div(id="bm-pred-fiabilite", style={"marginLeft": "auto",
                        "alignSelf": "flex-end"}),
                ], style={"display": "flex", "alignItems": "flex-end",
                          "flexWrap": "wrap"}),
            ], {"marginBottom": "14px"}),

            # Ligne 5 : Cards résumé prédictions
            html.Div(id="bm-pred-cards", style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "1px", "background": T["border"],
                "borderRadius": "8px", "overflow": "hidden",
                "marginBottom": "14px",
            }),

            # Ligne 6 : Graphiques prédictifs
            html.Div([
                _card([
                    _section_title("Projection PNB — 3 scénarios"),
                    dcc.Loading(
                        dcc.Graph(id="bm-pred-graph-pnb",
                            style={"height": "240px"},
                            config={"displayModeBar": False}),
                        type="dot", color=T["accent"],
                    ),
                ], {"flex": "1", "marginRight": "14px"}),

                _card([
                    _section_title("Projection Résultat Net"),
                    dcc.Loading(
                        dcc.Graph(id="bm-pred-graph-rn",
                            style={"height": "240px"},
                            config={"displayModeBar": False}),
                        type="dot", color=T["accent"],
                    ),
                ], {"flex": "1"}),

            ], style={"display": "flex", "marginBottom": "14px"}),

            html.Div([
                _card([
                    _section_title("Évolution part de marché projetée"),
                    dcc.Loading(
                        dcc.Graph(id="bm-pred-graph-pdm",
                            style={"height": "240px"},
                            config={"displayModeBar": False}),
                        type="dot", color=T["accent"],
                    ),
                ], {"flex": "1", "marginRight": "14px"}),

                _card([
                    _section_title("Trajectoire de rang sectoriel"),
                    dcc.Loading(
                        dcc.Graph(id="bm-pred-graph-rang",
                            style={"height": "240px"},
                            config={"displayModeBar": False}),
                        type="dot", color=T["accent"],
                    ),
                ], {"flex": "1"}),

            ], style={"display": "flex"}),

        ], style={"padding": "14px 24px", "flex": "1", "overflow": "auto"}),

    ], style={"display": "flex", "flexDirection": "column", "minHeight": "100vh",
        "background": T["bg"], "color": T["text"]})
