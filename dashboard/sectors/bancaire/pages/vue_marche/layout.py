# ============================================================
#  pages/vue_marche/layout.py
# ============================================================

from dash import html, dcc
from config import T, MONO, SERIF
from components.tooltip_info import card_with_tooltip
from data import get_annees
from data.tooltips import TOOLTIPS

ACCENT = T["accent"]


def _card(children, extra=None):
    s = {"background": T["card"], "border": f"1px solid {T['border']}",
         "borderRadius": "8px", "padding": "20px"}
    if extra: s.update(extra)
    return html.Div(children, style=s)


def get_layout():
    annees = get_annees()

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("BCEAO · Rapport Sectoriel", style={"color": ACCENT,
                    "fontSize": "10px", "letterSpacing": "2px", "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Vue d'ensemble du marché bancaire", style={"margin": "6px 0 0",
                    "fontSize": "20px", "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF, "letterSpacing": "0.3px"}),
            ]),
            html.Div([
                html.Div("PÉRIODE D'ANALYSE", style={"color": T["muted"], "fontSize": "9px",
                    "letterSpacing": "1.5px", "fontFamily": MONO, "marginBottom": "10px"}),
                dcc.RangeSlider(
                    id="vm-slider",
                    min=min(annees), max=max(annees), step=1,
                    value=[2015, 2022], allowCross=False, pushable=1,
                    marks={y: {"label": str(y), "style": {
                        "color": ACCENT if y in [2017,2018,2019,2021,2022] else T["muted"],
                        "fontSize": "10px", "fontFamily": MONO,
                        "fontWeight": "600" if y in [2017,2018,2019,2021,2022] else "400",
                    }} for y in annees},
                    tooltip={"placement": "top", "always_visible": True},
                ),
            ], style={"width": "420px"}),
        ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
            "padding": "20px 28px", "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)"}),

        # ── KPI Row ───────────────────────────────────────────
        dcc.Loading(
            html.Div(id="vm-kpis", style={"display": "grid", "gridTemplateColumns": "repeat(5,1fr)",
                "gap": "1px", "background": T["border"], "borderBottom": f"1px solid {T['border']}"}),
            type="dot", color=ACCENT,
        ),

        # ── Corps ─────────────────────────────────────────────
        html.Div([
            # Colonne gauche
            html.Div([
                card_with_tooltip(
                    "Évolution sectorielle", "vm-evolution",
                    "vm-evolution", TOOLTIPS["vm-evolution"],
                    "220px", ACCENT,
                    extra_style={"marginBottom": "14px",
                        "background": T["card"], "border": f"1px solid {T['border']}"},
                ),
                card_with_tooltip(
                    "Classement des banques", "vm-top",
                    "vm-classement", TOOLTIPS["vm-classement"],
                    "260px", ACCENT,
                    extra_style={"background": T["card"], "border": f"1px solid {T['border']}"},
                ),
            ], style={"flex": "1.55", "display": "flex", "flexDirection": "column"}),

            # Colonne droite
            html.Div([
                card_with_tooltip(
                    "Répartition par groupe bancaire", "vm-groupes",
                    "vm-repartition", TOOLTIPS["vm-repartition"],
                    "210px", ACCENT,
                    extra_style={"marginBottom": "14px",
                        "background": T["card"], "border": f"1px solid {T['border']}"},
                ),
                card_with_tooltip(
                    "Agences vs Bilan (régression)", "vm-scatter",
                    "vm-pnb-rn", TOOLTIPS["vm-pnb-rn"],
                    "228px", ACCENT,
                    extra_style={"background": T["card"], "border": f"1px solid {T['border']}"},
                ),
            ], style={"flex": "1", "display": "flex", "flexDirection": "column"}),

        ], style={"display": "flex", "gap": "14px", "padding": "16px 24px",
            "flex": "1", "overflow": "auto"}),

        # Dropdowns hors card (vm-indic reste fonctionnel)
        html.Div([
            dcc.Dropdown(id="vm-indic",
                options=[
                    {"label": "Produit Net Bancaire", "value": "pnb"},
                    {"label": "Total Bilan",          "value": "bilan"},
                    {"label": "Résultat Net",         "value": "rn"},
                ],
                value="pnb", clearable=False,
                style={"display": "none"}),
            html.Div(id="vm-top-label", style={"display": "none"}),
        ]),

    ], style={"display": "flex", "flexDirection": "column", "minHeight": "100vh",
        "background": T["bg"], "color": T["text"]})
