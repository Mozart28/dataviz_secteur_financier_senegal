# ============================================================
#  sectors/assurance/pages/sinistres/layout.py
#  Page 02 — Analyse Sinistres
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
        "fontFamily": MONO, "fontWeight": "600", "marginBottom": "14px",
        "textTransform": "uppercase",
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
    df      = get_dataframe()
    branches = sorted(df['type_assurance'].dropna().unique().tolist())
    regions  = sorted(df['region'].dropna().unique().tolist())

    # KPIs sinistres
    sin_df    = df[df['sinistre']]
    freq_glob = df['sinistre'].mean() * 100
    sev_glob  = sin_df['montant_sinistres'].mean()
    cout_tot  = df['montant_sinistres'].sum()
    p90       = sin_df['montant_sinistres'].quantile(0.9)
    multi_sin = (df['nb_sinistres'] >= 2).sum()

    footer_data = {
        "freq":       freq_glob,
        "severite":   sev_glob,
        "cout_total": cout_tot,
        "p90":        p90,
        "ratio_sp":   cout_tot / df['montant_prime'].sum() * 100,
    }

    def _kpi(label, value, sub, color=None):
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
            "borderTop": f"3px solid {color or ACCENT}",
            "borderRadius": "8px", "padding": "18px", "flex": "1",
        })

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("CIMA · Secteur Assurance · Sénégal", style={
                    "color": ACCENT, "fontSize": "10px",
                    "letterSpacing": "2px", "fontFamily": MONO,
                    "fontWeight": "600"}),
                html.H1("Analyse Sinistres", style={
                    "margin": "6px 0 0", "fontSize": "20px",
                    "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF}),
                html.P("Fréquence · Sévérité · Distribution · Top contrats à risque",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),

            # Filtres
            html.Div([
                html.Div([
                    html.Div("BRANCHE", style={"color": T["muted"],
                        "fontSize": "9px", "fontFamily": MONO,
                        "letterSpacing": "1.5px", "marginBottom": "8px"}),
                    dcc.Dropdown(
                        id="ass-sin-dropdown-branche",
                        options=[{"label": "Toutes", "value": "all"}] +
                                [{"label": b, "value": b} for b in branches],
                        value="all", clearable=False,
                        style={"width": "160px", "fontSize": "12px"},
                    ),
                ]),
                html.Div([
                    html.Div("RÉGION", style={"color": T["muted"],
                        "fontSize": "9px", "fontFamily": MONO,
                        "letterSpacing": "1.5px", "marginBottom": "8px"}),
                    dcc.Dropdown(
                        id="ass-sin-dropdown-region",
                        options=[{"label": "Toutes", "value": "all"}] +
                                [{"label": r, "value": r} for r in regions],
                        value="all", clearable=False,
                        style={"width": "150px", "fontSize": "12px"},
                    ),
                ], style={"marginLeft": "16px"}),
            ], style={"display": "flex", "alignItems": "flex-end"}),

        ], style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "flex-end", "flexWrap": "wrap",
            "padding": "20px 28px",
            "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)",
        }),

        # ── Corps ─────────────────────────────────────────────
        html.Div([

            # Ligne 1 — KPIs
            html.Div([
                _kpi("Fréquence globale",
                     f"{freq_glob:.1f}%",
                     "contrats sinistrés", T["accent"]),
                _kpi("Sévérité moyenne",
                     f"{sev_glob:,.0f}",
                     "montant moyen / sinistre sinistrés", T["red"]),
                _kpi("Coût total sinistres",
                     f"{cout_tot/1e6:.2f} M",
                     "portefeuille entier", T["red"]),
                _kpi("P90 sévérité",
                     f"{p90:,.0f}",
                     "90% des sinistres en-dessous", T["muted"]),
                _kpi("Multi-sinistres",
                     f"{multi_sin}",
                     "contrats avec 2+ sinistres", T["green"]),
            ], style={"display": "flex", "gap": "12px",
                      "marginBottom": "14px", "flexWrap": "wrap"}),

            # Ligne 2 — Fréquence × Sévérité + Distribution
            html.Div([
                card_with_tooltip(
                    "Fréquence vs Sévérité par branche",
                    "ass-sin-graph-freq-sev",
                    "sin-freq-sev",
                    TOOLTIPS["sin-freq-sev"],
                    "260px",
                    ACCENT, extra_style={'flex': '1', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Distribution des montants sinistres",
                    "ass-sin-graph-distrib",
                    "sin-distrib",
                    TOOLTIPS["sin-distrib"],
                    "260px",
                    ACCENT, extra_style={'flex': '1', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Sinistres par nombre d'occurrences",
                    "ass-sin-graph-nb-sin",
                    "sin-nb-sin",
                    TOOLTIPS["sin-nb-sin"],
                    "260px",
                    ACCENT, extra_style={'flex': '0.8'},
                ),

            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 3 — Par tranche d'âge + Par région
            html.Div([
                card_with_tooltip(
                    "Fréquence & sévérité par tranche d'âge",
                    "ass-sin-graph-age",
                    "sin-age",
                    TOOLTIPS["sin-age"],
                    "220px",
                    ACCENT, extra_style={'flex': '1', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Coût sinistres par région et branche",
                    "ass-sin-graph-region-branche",
                    "sin-region-branche",
                    TOOLTIPS["sin-region-branche"],
                    "220px",
                    ACCENT, extra_style={'flex': '1.4'},
                ),

            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 4 — Top contrats à risque
            card_with_tooltip(
                    "Top 15 contrats — Montant sinistres le plus élevé",
                    "ass-sin-graph-top-contrats",
                    "sin-top-contrats",
                    TOOLTIPS["sin-top-contrats"],
                    "220px",
                    ACCENT,
                ),

        ], style={"padding": "14px 24px", "overflow": "auto"}),

            footer_bar("sinistres", "assurance", footer_data),
    ], style={"display": "flex", "flexDirection": "column",
              "minHeight": "100vh", "background": T["bg"],
              "color": T["text"],
              "paddingBottom": "52px"})
