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
                html.Span("Énergie Solaire · Conditions Climatiques", style={
                    "color": ACCENT, "fontSize": "10px", "letterSpacing": "2px",
                    "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Conditions Climatiques", style={
                    "margin": "6px 0 0", "fontSize": "20px",
                    "fontWeight": "300", "color": T["text"], "fontFamily": SERIF}),
                html.P("Température module · Impact thermique · Distributions · Corrélations",
                    style={"color": T["muted"], "fontSize": "11px", "fontFamily": MONO, "marginTop": "4px"}),
            ]),
            html.Div([
                html.Div("PAYS", style={"color": T["muted"], "fontSize": "9px",
                    "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "8px"}),
                dcc.Dropdown(id="eng-clim-dropdown-pays",
                    options=[{"label": "Tous les pays", "value": "all"}] +
                            [{"label": p, "value": p} for p in pays],
                    value="all", clearable=False, style={"width": "180px", "fontSize": "12px"}),
            ]),
            html.Div([
                html.Div("MOIS", style={"color": T["muted"], "fontSize": "9px",
                    "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="eng-clim-dropdown-mois",
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
                card_with_tooltip("Température module vs Rendement DC→AC", "eng-clim-graph-temp-rendement",
                    "clim-temp-rendement", TOOLTIPS["clim-temp-rendement"], "260px", ACCENT,
                    extra_style={"flex": "1.2", "marginRight": "14px"}),
                card_with_tooltip("Distribution des températures par pays", "eng-clim-graph-distribution-temp",
                    "clim-distribution-temp", TOOLTIPS["clim-distribution-temp"], "260px", ACCENT,
                    extra_style={"flex": "1"}),
            ], style={"display": "flex", "marginBottom": "14px"}),
            html.Div([
                card_with_tooltip("Température ambiante — Heure × Mois", "eng-clim-graph-heatmap-temp",
                    "clim-heatmap-temp", TOOLTIPS["clim-heatmap-temp"], "240px", ACCENT,
                    extra_style={"flex": "1", "marginRight": "14px"}),
                card_with_tooltip("Irradiation vs Température module", "eng-clim-graph-irr-temp",
                    "clim-irr-temp", TOOLTIPS["clim-irr-temp"], "240px", ACCENT,
                    extra_style={"flex": "1"}),
            ], style={"display": "flex", "marginBottom": "14px"}),
        ], style={"padding": "14px 24px", "overflow": "auto"}),

        footer_bar("climatique", "energie", footer_data),

    ], style={"display": "flex", "flexDirection": "column", "minHeight": "100vh",
              "background": T["bg"], "color": T["text"], "paddingBottom": "52px"})
