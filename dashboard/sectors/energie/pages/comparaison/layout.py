from dash import html, dcc
from config import get_theme, MONO, SERIF
from components.tooltip_info import card_with_tooltip
from components.footer_bar import footer_bar
from sectors.energie.data.loader import get_dataframe, get_kpis
from sectors.energie.data.tooltips import TOOLTIPS

T = get_theme("energie"); ACCENT = T["accent"]

def get_layout():
    df = get_dataframe(); kpis = get_kpis(df)
    footer_data = {"total_yield": kpis['total_yield'], "efficiency_moy": kpis['efficiency_moy'],
                   "irradiation_moy": kpis['irradiation_moy'], "best_country": kpis['best_country'], "ratio_sp": 0}

    return html.Div([
        html.Div([
            html.Div([
                html.Span("Énergie Solaire · Comparaison Pays", style={
                    "color": ACCENT, "fontSize": "10px", "letterSpacing": "2px",
                    "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Comparaison Pays", style={
                    "margin": "6px 0 0", "fontSize": "20px",
                    "fontWeight": "300", "color": T["text"], "fontFamily": SERIF}),
                html.P("Radar multicritères · Classement · Profils normalisés · Production mensuelle",
                    style={"color": T["muted"], "fontSize": "11px", "fontFamily": MONO, "marginTop": "4px"}),
            ]),
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-end",
                  "padding": "20px 28px", "borderBottom": f"1px solid {T['border']}",
                  "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)"}),

        html.Div([
            html.Div([
                card_with_tooltip("Radar multicritères — 4 pays", "eng-cmp-graph-radar",
                    "cmp-radar", TOOLTIPS["cmp-radar"], "320px", ACCENT,
                    extra_style={"flex": "1", "marginRight": "14px"}),
                card_with_tooltip("Classement des pays par KPI", "eng-cmp-graph-classement",
                    "cmp-classement", TOOLTIPS["cmp-classement"], "320px", ACCENT,
                    extra_style={"flex": "1.3"}),
            ], style={"display": "flex", "marginBottom": "14px"}),
            html.Div([
                card_with_tooltip("Profils de production normalisés", "eng-cmp-graph-profils",
                    "cmp-profils", TOOLTIPS["cmp-profils"], "240px", ACCENT,
                    extra_style={"flex": "1", "marginRight": "14px"}),
                card_with_tooltip("Production mensuelle comparative", "eng-cmp-graph-mensuel",
                    "cmp-mensuel", TOOLTIPS["cmp-mensuel"], "240px", ACCENT,
                    extra_style={"flex": "1.3"}),
            ], style={"display": "flex", "marginBottom": "14px"}),
        ], style={"padding": "14px 24px", "overflow": "auto"}),

        footer_bar("comparaison", "energie", footer_data),

    ], style={"display": "flex", "flexDirection": "column", "minHeight": "100vh",
              "background": T["bg"], "color": T["text"], "paddingBottom": "52px"})
