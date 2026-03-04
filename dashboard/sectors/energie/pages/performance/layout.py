from dash import html, dcc
from config import get_theme, MONO, SERIF
from components.tooltip_info import card_with_tooltip
from components.footer_bar import footer_bar
from sectors.energie.data.loader import get_dataframe, get_kpis
from sectors.energie.data.tooltips import TOOLTIPS

T = get_theme("energie"); ACCENT = T["accent"]

def get_layout():
    df = get_dataframe(); kpis = get_kpis(df)
    pays = sorted(df['Country'].unique().tolist())
    footer_data = {"total_yield": kpis['total_yield'], "efficiency_moy": kpis['efficiency_moy'],
                   "irradiation_moy": kpis['irradiation_moy'], "best_country": kpis['best_country'], "ratio_sp": 0}

    return html.Div([
        html.Div([
            html.Div([
                html.Span("Énergie Solaire · Performance & Rendement", style={
                    "color": ACCENT, "fontSize": "10px", "letterSpacing": "2px",
                    "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Performance & Rendement", style={
                    "margin": "6px 0 0", "fontSize": "20px", "fontWeight": "300",
                    "color": T["text"], "fontFamily": SERIF}),
                html.P("Efficacité DC→AC · Corrélation Irradiation · Pertes · Heures de pointe",
                    style={"color": T["muted"], "fontSize": "11px", "fontFamily": MONO, "marginTop": "4px"}),
            ]),
            html.Div([
                html.Div("PAYS", style={"color": T["muted"], "fontSize": "9px",
                    "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "8px"}),
                dcc.Dropdown(id="eng-perf-dropdown-pays",
                    options=[{"label": "Tous les pays", "value": "all"}] +
                            [{"label": p, "value": p} for p in pays],
                    value="all", clearable=False, style={"width": "180px", "fontSize": "12px"}),
            ]),
            html.Div([
                html.Div("MOIS", style={"color": T["muted"], "fontSize": "9px",
                    "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="eng-perf-dropdown-mois",
                    options=[{"label": "Tous les mois", "value": "all"}] +
                            [{"label": m, "value": i} for i, m in enumerate(
                                ["","Janv","Févr","Mars","Avr","Mai","Juin",
                                 "Juil","Août","Sept","Oct","Nov","Déc"], 1)],
                    value="all", clearable=False,
                    style={"width": "150px", "fontSize": "12px"},
                ),
            ]),
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-end",
                  "flexWrap": "wrap", "gap": "12px", "padding": "20px 28px",
                  "borderBottom": f"1px solid {T['border']}",
                  "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)"}),

        html.Div([
            html.Div([
                card_with_tooltip("Irradiation vs Puissance DC", "eng-perf-graph-scatter",
                    "perf-scatter", TOOLTIPS["perf-scatter"], "260px", ACCENT,
                    extra_style={"flex": "1.2", "marginRight": "14px"}),
                card_with_tooltip("Rendement DC→AC par tranche horaire", "eng-perf-graph-rendement-heure",
                    "perf-rendement-heure", TOOLTIPS["perf-rendement-heure"], "260px", ACCENT,
                    extra_style={"flex": "1"}),
            ], style={"display": "flex", "marginBottom": "14px"}),
            html.Div([
                card_with_tooltip("Pertes de conversion DC→AC par pays", "eng-perf-graph-pertes",
                    "perf-pertes", TOOLTIPS["perf-pertes"], "240px", ACCENT,
                    extra_style={"flex": "1", "marginRight": "14px"}),
                card_with_tooltip("Distribution puissance DC — heures productives", "eng-perf-graph-pic-production",
                    "perf-pic-production", TOOLTIPS["perf-pic-production"], "240px", ACCENT,
                    extra_style={"flex": "1"}),
            ], style={"display": "flex", "marginBottom": "14px"}),
            # Ligne 3 — DC vs AC + Rendement mensuel
            html.Div([
                card_with_tooltip(
                    "Évolution DC vs AC — pertes mensuelles",
                    "eng-perf-graph-dc-vs-ac",
                    "perf-pertes",
                    TOOLTIPS["perf-pertes"],
                    "220px", ACCENT,
                    extra_style={"flex": "1.2", "marginRight": "14px"},
                ),
                card_with_tooltip(
                    "Rendement DC→AC par mois",
                    "eng-perf-graph-rendement-mensuel",
                    "perf-rendement-heure",
                    TOOLTIPS["perf-rendement-heure"],
                    "220px", ACCENT,
                    extra_style={"flex": "1"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

        ], style={"padding": "14px 24px", "overflow": "auto"}),

        footer_bar("performance", "energie", footer_data),

    ], style={"display": "flex", "flexDirection": "column", "minHeight": "100vh",
              "background": T["bg"], "color": T["text"], "paddingBottom": "52px"})
