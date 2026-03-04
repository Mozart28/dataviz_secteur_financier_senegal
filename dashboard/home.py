# ============================================================
#  home.py — Page d'accueil multi-secteur
# ============================================================

from dash import html, dcc, Input, Output, callback
from config import get_theme, SECTOR_META, MONO, SERIF, SANS, get_theme


def get_layout():
    T = get_theme()  # neutre — pas de secteur actif

    def _sector_card(sector_key):
        meta   = SECTOR_META[sector_key]
        accent = meta["accent"]
        rgb    = _hex_to_rgb(accent)

        return dcc.Link(
            html.Div([

                # Icône + badge "En ligne" / "Bientôt"
                html.Div([
                    html.Div(meta["icon"], style={
                        "fontSize": "32px", "lineHeight": "1",
                        "marginBottom": "16px",
                    }),
                    html.Div(
                        "● EN LIGNE" if meta["pages"] > 0 else "● BIENTÔT",
                        style={
                            "fontSize": "8px", "fontFamily": MONO,
                            "letterSpacing": "1.5px", "fontWeight": "600",
                            "color": accent if meta["pages"] > 0 else T["muted"],
                            "marginBottom": "12px",
                        }
                    ),
                ]),

                # Titre
                html.H2(meta["label"], style={
                    "color": T["text"], "fontFamily": SERIF,
                    "fontWeight": "300", "fontSize": "20px",
                    "margin": "0 0 6px", "letterSpacing": "0.3px",
                }),

                # Sous-titre
                html.P(meta["sublabel"], style={
                    "color": T["muted"], "fontFamily": MONO,
                    "fontSize": "10px", "margin": "0 0 20px",
                    "letterSpacing": "0.5px",
                }),

                # Séparateur
                html.Div(style={
                    "height": "1px",
                    "background": f"linear-gradient(90deg, {accent}, transparent)",
                    "marginBottom": "20px",
                }),

                # Stats
                html.Div([
                    html.Div([
                        html.Div(str(meta["pages"]) if meta["pages"] > 0 else "—",
                            style={"color": accent, "fontSize": "28px",
                                   "fontWeight": "700", "fontFamily": MONO,
                                   "lineHeight": "1"}),
                        html.Div("pages", style={"color": T["muted"],
                            "fontSize": "9px", "fontFamily": MONO,
                            "letterSpacing": "1px", "marginTop": "4px"}),
                    ]),
                    html.Div(style={"width": "1px", "background": T["border"],
                                    "margin": "0 20px", "alignSelf": "stretch"}),
                    html.Div([
                        html.Div(
                            "BCEAO" if sector_key == "bancaire" else
                            "SENELEC" if sector_key == "energie" else "CIMA",
                            style={"color": accent, "fontSize": "14px",
                                   "fontWeight": "700", "fontFamily": MONO}),
                        html.Div("source", style={"color": T["muted"],
                            "fontSize": "9px", "fontFamily": MONO,
                            "letterSpacing": "1px", "marginTop": "4px"}),
                    ]),
                ], style={"display": "flex", "alignItems": "center",
                          "marginBottom": "20px"}),

                # Bouton
                html.Div(
                    "Accéder →" if meta["pages"] > 0 else "Données en attente",
                    style={
                        "background": f"rgba({rgb},0.12)" if meta["pages"] > 0
                                      else "transparent",
                        "border": f"1px solid {accent if meta['pages'] > 0 else T['border']}",
                        "color": accent if meta["pages"] > 0 else T["muted"],
                        "padding": "10px 20px", "borderRadius": "6px",
                        "fontFamily": MONO, "fontSize": "11px",
                        "fontWeight": "600", "textAlign": "center",
                        "letterSpacing": "1px",
                    }
                ),

            ], style={
                "background": T["card"],
                "border": f"1px solid {T['border']}",
                "borderRadius": "12px",
                "padding": "32px 28px",
                "cursor": "pointer" if meta["pages"] > 0 else "default",
                "transition": "all 0.2s ease",
                "position": "relative",
                "overflow": "hidden",
                # Accent bar en haut
                "borderTop": f"3px solid {accent}",
            }, className="sector-card"),
            href=f"/{sector_key}" if meta["pages"] > 0 else "#",
            style={"textDecoration": "none", "flex": "1"},
        )

    return html.Div([

        # ── Hero ──────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div("OBSERVATOIRE ÉCONOMIQUE · SÉNÉGAL", style={
                    "color": T["muted"], "fontSize": "10px",
                    "fontFamily": MONO, "letterSpacing": "3px",
                    "fontWeight": "600", "marginBottom": "16px",
                }),
                html.H1([
                    "Dashboard ",
                    html.Span("Multi-Secteur", style={
                        "background": "linear-gradient(135deg, #F0B429, #3FB950, #58A6FF)",
                        "WebkitBackgroundClip": "text",
                        "WebkitTextFillColor": "transparent",
                        "backgroundClip": "text",
                    }),
                ], style={
                    "fontFamily": SERIF, "fontWeight": "300",
                    "fontSize": "42px", "margin": "0 0 16px",
                    "lineHeight": "1.1", "color": T["text"],
                }),
                html.P(
                    "Analyse intégrée des secteurs bancaire, énergétique et assurantiel "
                    "du Sénégal. Données BCEAO · SENELEC · CIMA.",
                    style={"color": T["muted"], "fontFamily": SANS,
                           "fontSize": "14px", "maxWidth": "520px",
                           "lineHeight": "1.7", "margin": "0"}
                ),
            ], style={"flex": "1"}),

            # Stats globales
            html.Div([
                _hero_stat("3", "Secteurs"),
                _hero_stat("15+", "Pages"),
                _hero_stat("2015–2022", "Période"),
            ], style={"display": "flex", "gap": "32px",
                      "alignItems": "center"}),

        ], style={
            "display": "flex", "alignItems": "center",
            "justifyContent": "space-between",
            "padding": "52px 60px 48px",
            "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)",
            "flexWrap": "wrap", "gap": "32px",
        }),

        # ── Cartes secteur ────────────────────────────────────
        html.Div([
            html.Div("CHOISISSEZ UN SECTEUR", style={
                "color": T["muted"], "fontSize": "9px",
                "fontFamily": MONO, "letterSpacing": "3px",
                "fontWeight": "600", "marginBottom": "28px",
            }),
            html.Div([
                _sector_card("bancaire"),
                _sector_card("energie"),
                _sector_card("assurance"),
            ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
        ], style={"padding": "48px 60px"}),

        # ── Footer ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("Données sources officielles · ", style={
                    "color": T["muted"], "fontFamily": MONO, "fontSize": "9px"}),
                html.Span("BCEAO · SENELEC · CIMA · CRCA", style={
                    "color": T["muted"], "fontFamily": MONO,
                    "fontSize": "9px", "opacity": "0.6"}),
            ]),
        ], style={
            "padding": "20px 60px",
            "borderTop": f"1px solid {T['border']}",
            "marginTop": "auto",
        }),

    ], style={
        "minHeight": "100vh", "background": T["bg"],
        "color": T["text"], "display": "flex", "flexDirection": "column",
    })


def _hero_stat(value, label):
    T = get_theme()
    return html.Div([
        html.Div(value, style={
            "color": T["text"], "fontSize": "28px",
            "fontWeight": "700", "fontFamily": MONO,
        }),
        html.Div(label, style={
            "color": T["muted"], "fontSize": "9px",
            "fontFamily": MONO, "letterSpacing": "1.5px",
            "marginTop": "4px",
        }),
    ], style={"textAlign": "center"})


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"
