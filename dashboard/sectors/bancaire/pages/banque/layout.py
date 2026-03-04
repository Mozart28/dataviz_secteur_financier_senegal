# ============================================================
#  pages/banque/layout.py — Profil Banque
# ============================================================

from dash import html, dcc
from config import T, MONO, SERIF
from components.tooltip_info import card_with_tooltip
from data import get_dataframe
from data.tooltips import TOOLTIPS

ACCENT = T["accent"]


def _card(children, extra=None):
    s = {"background": T["card"], "border": f"1px solid {T['border']}",
         "borderRadius": "8px", "padding": "20px"}
    if extra: s.update(extra)
    return html.Div(children, style=s)


def _ratio_gauge(ratio_id, label, unit="%", color=None):
    c = color or ACCENT
    return html.Div([
        html.Div(label, style={"color": T["muted"], "fontSize": "9px",
            "letterSpacing": "1.5px", "fontFamily": MONO, "fontWeight": "600",
            "marginBottom": "8px", "textTransform": "uppercase"}),
        html.Div(id=ratio_id, style={"color": c, "fontSize": "26px",
            "fontWeight": "700", "fontFamily": MONO, "lineHeight": "1"}),
        html.Div(unit, style={"color": T["muted"], "fontSize": "10px",
            "fontFamily": MONO, "marginTop": "4px"}),
    ], style={"background": T["card2"], "padding": "16px 20px",
              "borderRadius": "8px", "borderTop": f"2px solid {c}"})


def get_layout():
    df      = get_dataframe()
    banques = sorted(df["Sigle"].dropna().unique().tolist())

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("BCEAO · Analyse individuelle", style={"color": ACCENT,
                    "fontSize": "10px", "letterSpacing": "2px",
                    "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Profil d'une banque", style={"margin": "6px 0 0",
                    "fontSize": "20px", "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF, "letterSpacing": "0.3px"}),
            ]),
            html.Div([
                html.Div("SÉLECTIONNER UNE BANQUE", style={"color": T["muted"],
                    "fontSize": "9px", "letterSpacing": "1.5px",
                    "fontFamily": MONO, "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="pb-dropdown-banque",
                    options=[{"label": b, "value": b} for b in banques],
                    value="CBAO", clearable=False,
                    style={"width": "200px", "fontSize": "13px"},
                ),
            ]),
        ], style={"display": "flex", "alignItems": "center",
            "justifyContent": "space-between", "padding": "20px 28px",
            "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)"}),

        # ── Bandeau identité ─────────────────────────────────
        html.Div(id="pb-identity-bar", style={"display": "flex",
            "alignItems": "center", "gap": "32px", "padding": "16px 28px",
            "borderBottom": f"1px solid {T['border']}", "background": T["card2"]}),

        # ── KPI Row ───────────────────────────────────────────
        dcc.Loading(
            html.Div(id="pb-kpis", style={"display": "grid",
                "gridTemplateColumns": "repeat(4,1fr)", "gap": "1px",
                "background": T["border"], "borderBottom": f"1px solid {T['border']}"}),
            type="dot", color=ACCENT,
        ),

        # ── Corps ─────────────────────────────────────────────
        html.Div([

            # Colonne gauche (60%)
            html.Div([

                # Évolution — avec tooltip + dropdown intégré dans card
                html.Div([
                    html.Div([
                        html.Div("ÉVOLUTION SUR LA PÉRIODE", style={"color": ACCENT,
                            "fontSize": "9px", "letterSpacing": "2.5px",
                            "fontFamily": MONO, "fontWeight": "600", "textTransform": "uppercase"}),
                        dcc.Dropdown(id="pb-dropdown-indicateur",
                            options=[
                                {"label": "Bilan + PNB + Résultat Net", "value": "all"},
                                {"label": "Total Bilan",                 "value": "bilan"},
                                {"label": "Produit Net Bancaire",        "value": "pnb"},
                                {"label": "Résultat Net",                "value": "rn"},
                                {"label": "Fonds Propres",               "value": "fp"},
                                {"label": "Ressources",                  "value": "ressources"},
                            ],
                            value="all", clearable=False,
                            style={"width": "230px", "fontSize": "12px"}),
                    ], style={"display": "flex", "alignItems": "center",
                        "justifyContent": "space-between", "marginBottom": "14px"}),
                    dcc.Loading(
                        dcc.Graph(id="pb-graph-evolution",
                            style={"height": "220px"}, config={"displayModeBar": False}),
                        type="dot", color=ACCENT, style={"minHeight": "220px"},
                    ),
                ], style={"background": T["card"], "border": f"1px solid {T['border']}",
                    "borderRadius": "8px", "padding": "20px", "marginBottom": "14px",
                    "position": "relative"}),

                # Ratios avec tooltip
                card_with_tooltip(
                    "Ratios financiers clés", "pb-graph-ratios",
                    "pb-ratios", TOOLTIPS["pb-ratios"],
                    "180px", ACCENT,
                    extra_style={"marginBottom": "14px",
                        "background": T["card"], "border": f"1px solid {T['border']}"},
                ),

                # Part de marché avec tooltip
                card_with_tooltip(
                    "Part de marché sectorielle", "pb-graph-pdm",
                    "pb-pdm", TOOLTIPS["pb-pdm"],
                    "180px", ACCENT,
                    extra_style={"background": T["card"], "border": f"1px solid {T['border']}"},
                ),

            ], style={"flex": "1.55", "display": "flex", "flexDirection": "column"}),

            # Colonne droite (40%)
            html.Div([

                # Radar avec tooltip
                card_with_tooltip(
                    "Positionnement vs secteur", "pb-graph-radar",
                    "pb-radar", TOOLTIPS["pb-radar"],
                    "250px", ACCENT,
                    extra_style={"marginBottom": "14px",
                        "background": T["card"], "border": f"1px solid {T['border']}"},
                ),

                # Export (pas de graphe — pas de tooltip)
                _card([
                    html.Div("EXPORT", style={"color": ACCENT, "fontSize": "9px",
                        "letterSpacing": "2.5px", "fontFamily": MONO,
                        "fontWeight": "600", "marginBottom": "14px", "textTransform": "uppercase"}),
                    html.Button(
                        [html.Span("↓", style={"marginRight": "8px"}),
                         "Télécharger rapport PDF"],
                        id="pb-btn-export",
                        style={"background": ACCENT, "color": T["bg"],
                            "border": "none", "borderRadius": "6px",
                            "padding": "10px 20px", "fontFamily": MONO,
                            "fontSize": "11px", "fontWeight": "600",
                            "letterSpacing": "1px", "cursor": "pointer",
                            "width": "100%", "textTransform": "uppercase"},
                    ),
                    dcc.Download(id="pb-download-pdf"),
                    html.Div(id="pb-export-status", style={"color": T["muted"],
                        "fontSize": "10px", "fontFamily": MONO,
                        "marginTop": "10px", "textAlign": "center"}),
                ]),

            ], style={"flex": "1", "display": "flex", "flexDirection": "column"}),

        ], style={"display": "flex", "gap": "14px", "padding": "16px 24px",
            "flex": "1", "overflow": "auto"}),

        # Éléments cachés nécessaires aux callbacks
        html.Div([
            html.Div(id="pb-radar-year-label", style={"display": "none"}),
            html.Div([
                _ratio_gauge("pb-ratio-roa",   "ROA",           "%", ACCENT),
                _ratio_gauge("pb-ratio-roe",   "ROE",           "%", T["blue"]),
                _ratio_gauge("pb-ratio-risk",  "Coût du risque","%", T["red"]),
                _ratio_gauge("pb-ratio-marge", "Marge nette",   "%", T["green"]),
            ], style={"display": "none"}),
        ]),

    ], style={"display": "flex", "flexDirection": "column", "minHeight": "100vh",
        "background": T["bg"], "color": T["text"]})
