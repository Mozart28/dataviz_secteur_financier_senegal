# ============================================================
#  sectors/energie/pages/vue_globale/layout.py
#  Page 01 — Vue Globale Production
# ============================================================

from dash import html, dcc
from config import get_theme, MONO, SERIF
from components.tooltip_info import card_with_tooltip
from components.footer_bar import footer_bar
from sectors.energie.data.loader import get_dataframe, get_kpis
from sectors.energie.data.tooltips import TOOLTIPS

T      = get_theme("energie")
ACCENT = T["accent"]

COUNTRY_COLORS = {
    "Norway":    "#58A6FF",
    "Brazil":    "#3FB950",
    "India":     "#F0B429",
    "Australia": "#F85149",
}


def _kpi(label, value, sub, color=None, border=None):
    c = color or ACCENT
    return html.Div([
        html.Div(label, style={"color": T["muted"], "fontSize": "9px",
            "fontFamily": MONO, "letterSpacing": "1.5px",
            "textTransform": "uppercase", "marginBottom": "8px"}),
        html.Div(value, style={"color": c, "fontSize": "22px",
            "fontWeight": "700", "fontFamily": MONO, "lineHeight": "1"}),
        html.Div(sub, style={"color": T["muted"], "fontSize": "9px",
            "fontFamily": MONO, "marginTop": "6px"}),
    ], style={
        "background": T["card2"], "border": f"1px solid {T['border']}",
        "borderTop": f"3px solid {border or c}",
        "borderRadius": "8px", "padding": "16px", "flex": "1",
    })


def get_layout():
    df   = get_dataframe()
    kpis = get_kpis(df)

    pays = sorted(df['Country'].unique().tolist())

    footer_data = {
        "total_yield":    kpis['total_yield'],
        "efficiency_moy": kpis['efficiency_moy'],
        "irradiation_moy":kpis['irradiation_moy'],
        "best_country":   kpis['best_country'],
        "ratio_sp":       0,
    }

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("Énergie Solaire · 4 Pays · 2024", style={
                    "color": ACCENT, "fontSize": "10px",
                    "letterSpacing": "2px", "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Vue Globale Production", style={
                    "margin": "6px 0 0", "fontSize": "20px",
                    "fontWeight": "300", "color": T["text"], "fontFamily": SERIF}),
                html.P("Norway · Brazil · India · Australia — Production DC/AC · Rendement · Irradiation",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),
            html.Div([
                html.Div("PAYS", style={"color": T["muted"], "fontSize": "9px",
                    "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="eng-vg-dropdown-pays",
                    options=[{"label": "Tous les pays", "value": "all"}] +
                            [{"label": p, "value": p} for p in pays],
                    value="all", clearable=False,
                    style={"width": "180px", "fontSize": "12px"},
                ),
            ]),
            html.Div([
                html.Div("MOIS", style={"color": T["muted"], "fontSize": "9px",
                    "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="eng-vg-dropdown-mois",
                    options=[{"label": "Tous les mois", "value": "all"}] +
                            [{"label": m, "value": i} for i, m in enumerate(
                                ["","Janv","Févr","Mars","Avr","Mai","Juin",
                                 "Juil","Août","Sept","Oct","Nov","Déc"], 1)],
                    value="all", clearable=False,
                    style={"width": "150px", "fontSize": "12px"},
                ),
            ]),
        ], style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "flex-end", "flexWrap": "wrap", "gap": "12px",
            "padding": "20px 28px",
            "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)",
        }),

        # ── Corps ─────────────────────────────────────────────
        html.Div([

            # KPIs
            html.Div([
                _kpi("Production totale",
                    f"{kpis['total_yield']/1e6:.2f} M kWh",
                    "4 pays · 12 mois"),
                _kpi("Puissance DC moy.",
                    f"{kpis['dc_power_moy']:.1f} W",
                    "toutes heures confondues",
                    ACCENT),
                _kpi("Rendement DC→AC",
                    f"{kpis['efficiency_moy']:.1f}%",
                    "efficacité conversion",
                    T["green"]),
                _kpi("Irradiation moy.",
                    f"{kpis['irradiation_moy']:.3f} W/m²",
                    "rayonnement solaire",
                    T["blue"]),
                _kpi("Meilleur pays",
                    kpis['best_country'],
                    f"{kpis['best_yield']/1e6:.2f} M kWh cumulés",
                    COUNTRY_COLORS.get(kpis['best_country'], ACCENT)),
            ], style={"display": "flex", "gap": "12px",
                      "marginBottom": "14px", "flexWrap": "wrap"}),

            # Ligne 2 — Production par pays + Évolution mensuelle
            html.Div([
                card_with_tooltip(
                    "Production totale par pays",
                    "eng-vg-graph-yield-pays",
                    "vg-yield-pays",
                    TOOLTIPS["vg-yield-pays"],
                    "260px", ACCENT,
                    extra_style={"flex": "1", "marginRight": "14px"},
                ),
                card_with_tooltip(
                    "Évolution mensuelle de la production",
                    "eng-vg-graph-evolution",
                    "vg-evolution",
                    TOOLTIPS["vg-evolution"],
                    "260px", ACCENT,
                    extra_style={"flex": "1.6"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 3 — Rendement + Heatmap irradiation
            html.Div([
                card_with_tooltip(
                    "Rendement DC → AC par pays",
                    "eng-vg-graph-efficacite",
                    "vg-efficacite",
                    TOOLTIPS["vg-efficacite"],
                    "240px", ACCENT,
                    extra_style={"flex": "1", "marginRight": "14px"},
                ),
                card_with_tooltip(
                    "Irradiation moyenne — Pays × Mois",
                    "eng-vg-graph-irradiation",
                    "vg-irradiation",
                    TOOLTIPS["vg-irradiation"],
                    "240px", ACCENT,
                    extra_style={"flex": "1.4"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

        ], style={"padding": "14px 24px", "overflow": "auto"}),

        footer_bar("vue_globale", "energie", footer_data),

    ], style={"display": "flex", "flexDirection": "column",
              "minHeight": "100vh", "background": T["bg"],
              "color": T["text"], "paddingBottom": "52px"})
