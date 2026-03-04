# ============================================================
#  sectors/assurance/pages/vue_portefeuille/layout.py
#  Page 01 — Vue Portefeuille  (avec trend badges)
# ============================================================

from dash import html, dcc
from config import get_theme, MONO, SERIF
from components.footer_bar import footer_bar
from components.tooltip_info import card_with_tooltip
from sectors.assurance.data.tooltips import TOOLTIPS
from sectors.assurance.data.loader import get_dataframe, get_kpis_globaux

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
    if extra: s.update(extra)
    return html.Div(children, style=s)


def _graph(gid, height="240px"):
    return dcc.Loading(
        dcc.Graph(id=gid, style={"height": height},
                  config={"displayModeBar": False}),
        type="dot", color=ACCENT, style={"minHeight": height},
    )


def get_layout():
    df     = get_dataframe()

    kpis = get_kpis_globaux(df)
    footer_data = {
        "total_primes":    kpis["total_primes"],
        "total_sinistres": kpis["total_sinistres"],
        "nb_contrats":     kpis["nb_contrats"],
        "prime_moyenne":   kpis["prime_moyenne"],
        "ratio_sp":        kpis["ratio_sp"],
    }

    branches = sorted(df['type_assurance'].dropna().unique().tolist())



    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("CIMA · Secteur Assurance · Sénégal", style={
                    "color": ACCENT, "fontSize": "10px",
                    "letterSpacing": "2px", "fontFamily": MONO,
                    "fontWeight": "600"}),
                html.H1("Vue Portefeuille", style={
                    "margin": "6px 0 0", "fontSize": "20px",
                    "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF}),
                html.P("Primes · Sinistres · Ratio S/P · Tendances annuelles",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),
            html.Div([
                html.Div("BRANCHE", style={"color": T["muted"],
                    "fontSize": "9px", "fontFamily": MONO,
                    "letterSpacing": "1.5px", "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="ass-vm-dropdown-branche",
                    options=[{"label": "Toutes branches", "value": "all"}] +
                            [{"label": b, "value": b} for b in branches],
                    value="all", clearable=False,
                    style={"width": "180px", "fontSize": "12px"},
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

            # Ligne 1 — Trend badges (mis à jour dynamiquement)
            html.Div(id="ass-vm-trend-row",
                style={"display":"flex","gap":"12px",
                       "marginBottom":"14px","flexWrap":"wrap"}),

            # Ligne 2 — Évolution + Répartition
            html.Div([
                card_with_tooltip(
                    "Évolution annuelle — Primes vs Sinistres",
                    "ass-vm-graph-evolution",
                    "vm-evolution",
                    TOOLTIPS["vm-evolution"],
                    "260px",
                    ACCENT, extra_style={'flex': '1.6', 'marginRight': '14px'},
                ),
                card_with_tooltip(
                    "Répartition primes par branche",
                    "ass-vm-graph-donut-branche",
                    "vm-donut-branche",
                    TOOLTIPS["vm-donut-branche"],
                    "260px",
                    ACCENT, extra_style={'flex': '1'},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 3 — S/P + Région + Bonus-malus
            html.Div([
                card_with_tooltip(
                    "Ratio S/P par branche",
                    "ass-vm-graph-sp-branche",
                    "vm-sp-branche",
                    TOOLTIPS["vm-sp-branche"],
                    "220px",
                    ACCENT, extra_style={'flex': '1', 'marginRight': '14px'},
                ),
                card_with_tooltip(
                    "Taux de sinistralité par région",
                    "ass-vm-graph-sin-region",
                    "vm-sin-region",
                    TOOLTIPS["vm-sin-region"],
                    "220px",
                    ACCENT, extra_style={'flex': '1', 'marginRight': '14px'},
                ),
                card_with_tooltip(
                    "Distribution bonus-malus",
                    "ass-vm-graph-bonus",
                    "vm-bonus",
                    TOOLTIPS["vm-bonus"],
                    "220px",
                    ACCENT, extra_style={'flex': '1'},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 4 — Heatmap
            card_with_tooltip(
                    "Concentration sinistres — Branche × Région",
                    "ass-vm-graph-heatmap",
                    "vm-heatmap",
                    TOOLTIPS["vm-heatmap"],
                    "240px",
                    ACCENT,
                ),

        ], style={"padding": "14px 24px", "overflow": "auto"}),

            footer_bar("vue_portefeuille", "assurance", footer_data),
    ], style={"display": "flex", "flexDirection": "column",
              "minHeight": "100vh", "background": T["bg"],
              "color": T["text"],
              "paddingBottom": "52px"})
