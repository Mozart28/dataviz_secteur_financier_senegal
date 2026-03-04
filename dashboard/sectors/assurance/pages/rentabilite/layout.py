# ============================================================
#  sectors/assurance/pages/rentabilite/layout.py
#  Page 04 — Rentabilité & Ratios
# ============================================================

from dash import html, dcc
from config import get_theme, MONO, SERIF
from components.footer_bar import footer_bar
from components.tooltip_info import card_with_tooltip
from sectors.assurance.data.tooltips import TOOLTIPS
from sectors.assurance.data.loader import get_dataframe

T      = get_theme("assurance")
ACCENT = T["accent"]

# Expense ratio technique (estimation standard)
EXPENSE_RATIO = 30.0


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

    primes = df['montant_prime'].sum()
    sins   = df['montant_sinistres'].sum()
    lr     = sins / primes * 100 if primes else 0
    cr     = lr + 30.0
    footer_data = {
        "loss_ratio":     lr,
        "combined_ratio": cr,
        "pct_rentable":   (df['montant_prime'] > df['montant_sinistres']).mean() * 100,
        "ratio_sp":       lr,
    }

    # KPIs globaux
    primes    = df['montant_prime'].sum()
    sinistres = df['montant_sinistres'].sum()
    charges   = primes * EXPENSE_RATIO / 100
    loss_r    = sinistres / primes * 100
    exp_r     = EXPENSE_RATIO
    combined  = loss_r + exp_r
    marge     = 100 - combined
    rentables = (df['montant_prime'] > df['montant_sinistres']).mean() * 100

    branches = sorted(df['type_assurance'].dropna().unique().tolist())

    def _kpi(label, value, sub, color=None, border_color=None):
        bc = border_color or color or ACCENT
        return html.Div([
            html.Div(label, style={"color": T["muted"], "fontSize": "9px",
                "fontFamily": MONO, "letterSpacing": "1.5px",
                "textTransform": "uppercase", "marginBottom": "8px"}),
            html.Div(value, style={"color": color or ACCENT,
                "fontSize": "24px", "fontWeight": "700",
                "fontFamily": MONO, "lineHeight": "1"}),
            html.Div(sub, style={"color": T["muted"], "fontSize": "9px",
                "fontFamily": MONO, "marginTop": "6px"}),
        ], style={
            "background": T["card2"],
            "border": f"1px solid {T['border']}",
            "borderTop": f"3px solid {bc}",
            "borderRadius": "8px", "padding": "18px", "flex": "1",
        })

    lr_color = T["red"] if loss_r > 100 else \
               T["accent"] if loss_r > 70 else T["green"]
    cr_color = T["red"] if combined > 100 else T["green"]
    mg_color = T["green"] if marge > 0 else T["red"]

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("CIMA · Secteur Assurance · Sénégal", style={
                    "color": ACCENT, "fontSize": "10px",
                    "letterSpacing": "2px", "fontFamily": MONO,
                    "fontWeight": "600"}),
                html.H1("Rentabilité & Ratios", style={
                    "margin": "6px 0 0", "fontSize": "20px",
                    "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF}),
                html.P("Loss Ratio · Combined Ratio · Marge technique · Prime pure",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),
            html.Div([
                html.Div("BRANCHE", style={"color": T["muted"], "fontSize": "9px",
                    "fontFamily": MONO, "letterSpacing": "1.5px",
                    "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="ass-rent-dropdown-branche",
                    options=[{"label": "Toutes", "value": "all"}] +
                            [{"label": b, "value": b} for b in branches],
                    value="all", clearable=False,
                    style={"width": "170px", "fontSize": "12px"},
                ),
            ]),
        ], style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "flex-end", "flexWrap": "wrap",
            "padding": "20px 28px",
            "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)",
        }),

        # ── Corps ─────────────────────────────────────────────
        html.Div([

            # Ligne 1 — KPIs ratios
            html.Div([
                _kpi("Loss Ratio",
                     f"{loss_r:.1f}%",
                     "sinistres / primes",
                     lr_color),
                _kpi("Expense Ratio",
                     f"{exp_r:.1f}%",
                     "charges / primes (est.)",
                     T["muted"]),
                _kpi("Combined Ratio",
                     f"{combined:.1f}%",
                     "LR + ER — seuil critique 100%",
                     cr_color),
                _kpi("Marge technique",
                     f"{marge:.1f}%",
                     "100% − Combined Ratio",
                     mg_color),
                _kpi("Contrats rentables",
                     f"{rentables:.1f}%",
                     "prime > sinistre individuel",
                     T["blue"]),
            ], style={"display": "flex", "gap": "12px",
                      "marginBottom": "14px", "flexWrap": "wrap"}),

            # Ligne 2 — Combined Ratio gauge + Waterfall
            html.Div([
                card_with_tooltip(
                    "Combined ratio — décomposition",
                    "ass-rent-graph-waterfall",
                    "rent-waterfall",
                    TOOLTIPS["rent-waterfall"],
                    "280px",
                    ACCENT, extra_style={'flex': '1.2', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Comparaison Loss Ratio par branche",
                    "ass-rent-graph-lr-branche",
                    "rent-lr-branche",
                    TOOLTIPS["rent-lr-branche"],
                    "280px",
                    ACCENT, extra_style={'flex': '1', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Combined ratio par région",
                    "ass-rent-graph-cr-region",
                    "rent-cr-region",
                    TOOLTIPS["rent-cr-region"],
                    "280px",
                    ACCENT, extra_style={'flex': '1'},
                ),

            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 3 — Évolution + Scatter prime vs sinistre
            html.Div([
                card_with_tooltip(
                    "Évolution LR & CR annuels",
                    "ass-rent-graph-evolution",
                    "rent-evolution",
                    TOOLTIPS["rent-evolution"],
                    "240px",
                    ACCENT, extra_style={'flex': '1.4', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Prime collectée vs sinistre payé (scatter)",
                    "ass-rent-graph-scatter",
                    "rent-scatter",
                    TOOLTIPS["rent-scatter"],
                    "240px",
                    ACCENT, extra_style={'flex': '1'},
                ),

            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 4 — Bonus-malus vs LR + Prime pure
            html.Div([
                card_with_tooltip(
                    "Bonus-malus vs Loss Ratio",
                    "ass-rent-graph-bm-lr",
                    "rent-bm-lr",
                    TOOLTIPS["rent-bm-lr"],
                    "200px",
                    ACCENT, extra_style={'flex': '1', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Prime pure vs prime commerciale par branche",
                    "ass-rent-graph-prime-pure",
                    "rent-prime-pure",
                    TOOLTIPS["rent-prime-pure"],
                    "200px",
                    ACCENT, extra_style={'flex': '1'},
                ),

            ], style={"display": "flex"}),

        ], style={"padding": "14px 24px", "overflow": "auto"}),

            footer_bar("rentabilite", "assurance", footer_data),
    ], style={"display": "flex", "flexDirection": "column",
              "minHeight": "100vh", "background": T["bg"],
              "color": T["text"],
              "paddingBottom": "52px"})
