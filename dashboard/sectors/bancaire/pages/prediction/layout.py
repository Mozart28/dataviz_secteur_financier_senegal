# ============================================================
#  sectors/bancaire/pages/prediction/layout.py
#  Module de positionnement marché — nouvelle banque
# ============================================================
from dash import html, dcc
from config import get_theme, MONO, SERIF, SANS

def get_layout():
    T = get_theme()
    accent = "#F0B429"

    def _input_field(label, field_id, placeholder, unit="M FCFA", hint=""):
        return html.Div([
            html.Label(label, style={
                "fontFamily": MONO, "fontSize": "9px",
                "color": T["muted"], "letterSpacing": "1.5px",
                "fontWeight": "600", "textTransform": "uppercase",
                "marginBottom": "6px", "display": "block",
            }),
            html.Div([
                dcc.Input(
                    id=field_id,
                    type="number",
                    placeholder=placeholder,
                    min=0,
                    style={
                        "width": "100%",
                        "background": T["bg"],
                        "border": f"1px solid {T['border']}",
                        "borderRadius": "6px",
                        "color": T["text"],
                        "fontFamily": MONO,
                        "fontSize": "13px",
                        "padding": "10px 14px",
                        "outline": "none",
                        "transition": "border-color 0.2s",
                    },
                    className="pred-input",
                ),
                html.Span(unit, style={
                    "position": "absolute", "right": "12px", "top": "50%",
                    "transform": "translateY(-50%)",
                    "color": T["muted"], "fontFamily": MONO, "fontSize": "9px",
                    "letterSpacing": "1px", "pointerEvents": "none",
                }),
            ], style={"position": "relative"}),
            html.Div(hint, style={
                "fontFamily": MONO, "fontSize": "9px",
                "color": T["muted"], "marginTop": "4px",
                "opacity": "0.6",
            }) if hint else html.Div(),
        ], style={"marginBottom": "20px"})

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div("SECTEUR BANCAIRE · SÉNÉGAL", style={
                "color": T["muted"], "fontFamily": MONO,
                "fontSize": "9px", "letterSpacing": "3px",
                "fontWeight": "600", "marginBottom": "12px",
            }),
            html.H1([
                "Positionnement ",
                html.Span("Marché", style={
                    "background": f"linear-gradient(135deg, {accent}, #F5D87A)",
                    "WebkitBackgroundClip": "text",
                    "WebkitTextFillColor": "transparent",
                    "backgroundClip": "text",
                }),
            ], style={
                "fontFamily": SERIF, "fontWeight": "300",
                "fontSize": "32px", "margin": "0 0 10px",
                "color": T["text"],
            }),
            html.P(
                "Entrez les indicateurs d'une nouvelle banque pour estimer sa position "
                "dans le secteur bancaire sénégalais — rang, quartile et banques similaires.",
                style={
                    "color": T["muted"], "fontFamily": SANS,
                    "fontSize": "13px", "maxWidth": "600px",
                    "lineHeight": "1.7", "margin": "0",
                }
            ),
        ], style={
            "padding": "40px 48px 32px",
            "borderBottom": f"1px solid {T['border']}",
        }),

        # ── Corps ─────────────────────────────────────────────
        html.Div([

            # Colonne gauche — formulaire
            html.Div([
                html.Div("INDICATEURS DE LA BANQUE", style={
                    "color": accent, "fontFamily": MONO,
                    "fontSize": "9px", "letterSpacing": "2px",
                    "fontWeight": "700", "marginBottom": "24px",
                }),

                # Groupe 1 — Bilan
                html.Div("Bilan & Ressources", style={
                    "color": T["muted"], "fontFamily": MONO,
                    "fontSize": "9px", "letterSpacing": "1px",
                    "marginBottom": "16px", "paddingBottom": "8px",
                    "borderBottom": f"1px solid {T['border']}",
                }),
                _input_field("Total Bilan", "pred-bilan", "ex: 200 000",
                    hint="Médiane secteur : 226 000 M FCFA"),
                _input_field("Ressources collectées", "pred-ressources", "ex: 150 000",
                    hint="Médiane secteur : 169 820 M FCFA"),
                _input_field("Fonds Propres", "pred-fonds", "ex: 25 000",
                    hint="Médiane secteur : 25 158 M FCFA"),
                _input_field("Total Emplois", "pred-emplois", "ex: 130 000",
                    hint="Médiane secteur : 128 642 M FCFA"),

                # Groupe 2 — Opérationnel
                html.Div("Indicateurs Opérationnels", style={
                    "color": T["muted"], "fontFamily": MONO,
                    "fontSize": "9px", "letterSpacing": "1px",
                    "marginBottom": "16px", "marginTop": "8px",
                    "paddingBottom": "8px",
                    "borderBottom": f"1px solid {T['border']}",
                }),
                _input_field("Effectif", "pred-effectif", "ex: 150",
                    unit="employés", hint="Médiane secteur : 148"),
                _input_field("Nombre d'agences", "pred-agences", "ex: 12",
                    unit="agences", hint="Médiane secteur : 12"),
                _input_field("Nombre de comptes", "pred-comptes", "ex: 30 000",
                    unit="comptes", hint="Médiane secteur : 29 152"),

                # Bouton
                html.Button([
                    "Analyser ma position →"
                ], id="pred-submit", n_clicks=0, style={
                    "width": "100%",
                    "background": f"linear-gradient(135deg, rgba(240,180,41,0.2), rgba(240,180,41,0.05))",
                    "border": f"1px solid {accent}",
                    "borderRadius": "8px",
                    "color": accent,
                    "fontFamily": MONO,
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "letterSpacing": "1.5px",
                    "padding": "14px",
                    "cursor": "pointer",
                    "marginTop": "8px",
                    "transition": "all 0.2s",
                }),

            ], style={
                "width": "320px", "minWidth": "320px",
                "background": T["card"],
                "border": f"1px solid {T['border']}",
                "borderRadius": "12px",
                "padding": "28px",
                "height": "fit-content",
            }),

            # Colonne droite — résultats
            html.Div([
                # État initial
                html.Div([
                    html.Div("◈", style={
                        "fontSize": "32px",
                        "background": f"linear-gradient(135deg, {accent}, #3FB950)",
                        "WebkitBackgroundClip": "text",
                        "WebkitTextFillColor": "transparent",
                        "backgroundClip": "text",
                        "marginBottom": "16px",
                    }),
                    html.Div("Entrez vos indicateurs", style={
                        "color": T["text"], "fontFamily": SERIF,
                        "fontWeight": "300", "fontSize": "18px",
                        "marginBottom": "8px",
                    }),
                    html.Div(
                        "Remplissez le formulaire et cliquez sur Analyser pour voir votre positionnement dans le secteur.",
                        style={
                            "color": T["muted"], "fontFamily": MONO,
                            "fontSize": "10px", "lineHeight": "1.8",
                            "maxWidth": "360px", "textAlign": "center",
                        }
                    ),
                ], id="pred-placeholder", style={
                    "display": "flex", "flexDirection": "column",
                    "alignItems": "center", "justifyContent": "center",
                    "height": "300px",
                }),

                # Résultats (cachés au départ)
                html.Div(id="pred-results", style={"display": "none"}, children=[

                    # ── KPIs rang ────────────────────────────
                    html.Div(id="pred-kpis", style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(3, 1fr)",
                        "gap": "16px",
                        "marginBottom": "24px",
                    }),

                    # ── Radar / scores ────────────────────────
                    html.Div([
                        html.Div([
                            html.Div("POSITIONNEMENT PAR INDICATEUR", style={
                                "color": T["muted"], "fontFamily": MONO,
                                "fontSize": "9px", "letterSpacing": "2px",
                                "fontWeight": "600", "marginBottom": "16px",
                            }),
                            dcc.Graph(id="pred-radar", config={"displayModeBar": False}),
                        ], style={
                            "background": T["card"],
                            "border": f"1px solid {T['border']}",
                            "borderRadius": "12px",
                            "padding": "20px",
                            "flex": "1",
                        }),

                        html.Div([
                            html.Div("BANQUES LES PLUS SIMILAIRES", style={
                                "color": T["muted"], "fontFamily": MONO,
                                "fontSize": "9px", "letterSpacing": "2px",
                                "fontWeight": "600", "marginBottom": "16px",
                            }),
                            html.Div(id="pred-similaires"),
                        ], style={
                            "background": T["card"],
                            "border": f"1px solid {T['border']}",
                            "borderRadius": "12px",
                            "padding": "20px",
                            "width": "240px",
                        }),
                    ], style={"display": "flex", "gap": "16px", "marginBottom": "20px"}),

                    # ── Classement bilan ──────────────────────
                    html.Div([
                        html.Div("CLASSEMENT TOTAL BILAN — SECTEUR 2019", style={
                            "color": T["muted"], "fontFamily": MONO,
                            "fontSize": "9px", "letterSpacing": "2px",
                            "fontWeight": "600", "marginBottom": "16px",
                        }),
                        dcc.Graph(id="pred-classement", config={"displayModeBar": False}),
                    ], style={
                        "background": T["card"],
                        "border": f"1px solid {T['border']}",
                        "borderRadius": "12px",
                        "padding": "20px",
                    }),

                ]),

            ], style={"flex": "1", "minWidth": "0"}),

        ], style={
            "display": "flex", "gap": "24px",
            "padding": "32px 48px",
            "alignItems": "flex-start",
        }),

    ], style={
        "background": T["bg"], "minHeight": "100vh",
        "color": T["text"],
    })
