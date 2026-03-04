# ============================================================
#  pages/carte/layout.py — Carte & Réseau Bancaire Senegal
# ============================================================

from dash import html, dcc
from config import T, MONO, SERIF
from components.tooltip_info import card_with_tooltip
from data import get_dataframe
from data.tooltips import TOOLTIPS

ACCENT = T["accent"]


def _card(children, extra=None):
    s = {"background": T["card"], "border": f"1px solid {T['border']}",
         "borderRadius": "8px", "padding": "18px"}
    if extra: s.update(extra)
    return html.Div(children, style=s)


def _graph(gid, height="420px"):
    return dcc.Loading(
        dcc.Graph(id=gid, style={"height": height},
                  config={"displayModeBar": True,
                          "modeBarButtonsToRemove": ["select2d","lasso2d"],
                          "displaylogo": False}),
        type="dot", color=ACCENT, style={"minHeight": height},
    )


def get_layout():
    df      = get_dataframe()
    annees  = sorted(df["ANNEE"].dropna().unique().tolist())
    groupes = sorted(df["Goupe_Bancaire"].dropna().unique().tolist())

    return html.Div([

        html.Div([
            html.Div([
                html.Span("BCEAO · Geographie bancaire", style={"color": ACCENT,
                    "fontSize": "10px", "letterSpacing": "2px",
                    "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Carte & Reseau Bancaire", style={"margin": "6px 0 0",
                    "fontSize": "20px", "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF, "letterSpacing": "0.3px"}),
                html.P("Localisation des sieges - Presence regionale - Bancarisation",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),
        ], style={"padding": "20px 28px", "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)"}),

        # Filtres
        html.Div([
            _card([
                html.Div([
                    html.Div([
                        html.Div("ANNEE", style={"color": T["muted"], "fontSize": "9px",
                            "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "8px"}),
                        dcc.Dropdown(id="carte-dropdown-annee",
                            options=[{"label": str(y), "value": y} for y in annees],
                            value=int(df["ANNEE"].max()), clearable=False,
                            style={"width": "120px", "fontSize": "12px"}),
                    ]),
                    html.Div([
                        html.Div("GROUPE BANCAIRE", style={"color": T["muted"],
                            "fontSize": "9px", "fontFamily": MONO,
                            "letterSpacing": "1.5px", "marginBottom": "8px"}),
                        dcc.Dropdown(id="carte-dropdown-groupe",
                            options=[{"label": "Tous les groupes", "value": "all"}] +
                                    [{"label": g.replace("Groupes ", ""), "value": g}
                                     for g in groupes],
                            value="all", clearable=False,
                            style={"width": "200px", "fontSize": "12px"}),
                    ], style={"marginLeft": "20px"}),
                    html.Div([
                        html.Div("TAILLE DES BULLES", style={"color": T["muted"],
                            "fontSize": "9px", "fontFamily": MONO,
                            "letterSpacing": "1.5px", "marginBottom": "8px"}),
                        dcc.Dropdown(id="carte-dropdown-metric",
                            options=[
                                {"label": "PNB",              "value": "PRODUIT.NET.BANCAIRE"},
                                {"label": "Total Bilan",       "value": "BILAN"},
                                {"label": "Resultat Net",      "value": "RESULTAT.NET"},
                                {"label": "Agences estimees",  "value": "agences_est"},
                            ],
                            value="PRODUIT.NET.BANCAIRE", clearable=False,
                            style={"width": "180px", "fontSize": "12px"}),
                    ], style={"marginLeft": "20px"}),
                    html.Div([
                        html.Div("VUE", style={"color": T["muted"], "fontSize": "9px",
                            "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "8px"}),
                        dcc.RadioItems(id="carte-radio-vue",
                            options=[{"label": " Sieges", "value": "sieges"},
                                     {"label": " Regions", "value": "regions"}],
                            value="sieges", inline=True,
                            inputStyle={"marginRight": "4px"},
                            labelStyle={"color": T["muted"], "fontFamily": MONO,
                                "fontSize": "11px", "marginRight": "14px", "cursor": "pointer"}),
                    ], style={"marginLeft": "20px"}),
                ], style={"display": "flex", "alignItems": "flex-end",
                          "flexWrap": "wrap", "gap": "0"}),
            ]),
        ], style={"padding": "14px 24px 0"}),

        # Corps
        html.Div([

            # Ligne 1 : Carte + Stats reseau
            html.Div([
                card_with_tooltip(
                    "Carte interactive du Senegal", "carte-map",
                    "carte-map", TOOLTIPS["carte-map"],
                    "460px", ACCENT,
                    extra_style={"flex": "1.6", "marginRight": "14px",
                        "background": T["card"], "border": f"1px solid {T['border']}"},
                ),
                html.Div([
                    _card([
                        html.Div("RESEAU NATIONAL", style={"color": ACCENT,
                            "fontSize": "9px", "letterSpacing": "2.5px",
                            "fontFamily": MONO, "fontWeight": "600",
                            "marginBottom": "14px", "textTransform": "uppercase"}),
                        html.Div(id="carte-kpis-reseau"),
                    ], {"marginBottom": "14px"}),
                    card_with_tooltip(
                        "Classement presence reseau", "carte-bar-reseau",
                        "carte-reseau", TOOLTIPS["carte-reseau"],
                        "200px", ACCENT,
                        extra_style={"background": T["card"],
                            "border": f"1px solid {T['border']}"},
                    ),
                ], style={"flex": "1", "display": "flex", "flexDirection": "column"}),
            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 2 : Bancarisation + Concentration
            html.Div([
                card_with_tooltip(
                    "Taux de bancarisation par region", "carte-bar-bancarisation",
                    "carte-bancarisation", TOOLTIPS["carte-bancarisation"],
                    "220px", ACCENT,
                    extra_style={"flex": "1", "marginRight": "14px",
                        "background": T["card"], "border": f"1px solid {T['border']}"},
                ),
                card_with_tooltip(
                    "Concentration geographique PNB", "carte-pie-concentration",
                    "carte-concentration", TOOLTIPS["carte-concentration"],
                    "220px", ACCENT,
                    extra_style={"flex": "1",
                        "background": T["card"], "border": f"1px solid {T['border']}"},
                ),
            ], style={"display": "flex"}),

        ], style={"padding": "14px 24px", "overflow": "auto"}),

    ], style={"display": "flex", "flexDirection": "column", "minHeight": "100vh",
        "background": T["bg"], "color": T["text"]})
