from dash import html, dcc
from config import get_theme, MONO, SERIF
from components.tooltip_info import card_with_tooltip
from components.footer_bar import footer_bar
from sectors.energie.data.loader import get_dataframe, get_kpis
from sectors.energie.data.tooltips import TOOLTIPS

T      = get_theme("energie")
ACCENT = T["accent"]

def get_layout():
    df   = get_dataframe()
    kpis = get_kpis(df)
    pays = sorted(df['Country'].unique().tolist())

    footer_data = {
        "total_yield": kpis['total_yield'], "efficiency_moy": kpis['efficiency_moy'],
        "irradiation_moy": kpis['irradiation_moy'], "best_country": kpis['best_country'],
        "ratio_sp": 0,
    }

    return html.Div([
        html.Div([
            html.Div([
                html.Span("Énergie Solaire · Analyse Temporelle", style={
                    "color": ACCENT, "fontSize": "10px",
                    "letterSpacing": "2px", "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Analyse Temporelle", style={
                    "margin": "6px 0 0", "fontSize": "20px",
                    "fontWeight": "300", "color": T["text"], "fontFamily": SERIF}),
                html.P("Heatmap heure × mois · Profil journalier · Saisonnalité · Distribution",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),
            html.Div([
                html.Div("PAYS", style={"color": T["muted"], "fontSize": "9px",
                    "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="eng-tmp-dropdown-pays",
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
                    id="eng-tmp-dropdown-mois",
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
            "padding": "20px 28px", "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)",
        }),

        html.Div([
            # Ligne 1 — Heatmap + Profil journalier
            html.Div([
                card_with_tooltip(
                    "Heatmap production — Heure × Mois",
                    "eng-tmp-graph-heatmap",
                    "tmp-heatmap",
                    TOOLTIPS["tmp-heatmap"],
                    "280px", ACCENT,
                    extra_style={"flex": "1.2", "marginRight": "14px"},
                ),
                card_with_tooltip(
                    "Profil journalier moyen par pays",
                    "eng-tmp-graph-courbe-journaliere",
                    "tmp-courbe-journaliere",
                    TOOLTIPS["tmp-courbe-journaliere"],
                    "280px", ACCENT,
                    extra_style={"flex": "1"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 2 — Saisonnalité + Distribution
            html.Div([
                card_with_tooltip(
                    "Production moyenne par saison",
                    "eng-tmp-graph-saisonnalite",
                    "tmp-saisonnalite",
                    TOOLTIPS["tmp-saisonnalite"],
                    "240px", ACCENT,
                    extra_style={"flex": "1", "marginRight": "14px"},
                ),
                card_with_tooltip(
                    "Distribution du rendement journalier",
                    "eng-tmp-graph-daily-yield",
                    "tmp-daily-yield",
                    TOOLTIPS["tmp-daily-yield"],
                    "240px", ACCENT,
                    extra_style={"flex": "1"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 3 — Yield cumulé
            html.Div([
                card_with_tooltip(
                    "Yield cumulé jour par jour sur l'année",
                    "eng-tmp-graph-yield-cumul",
                    "tmp-daily-yield",
                    TOOLTIPS["tmp-daily-yield"],
                    "220px", ACCENT,
                    extra_style={"flex": "1"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

        ], style={"padding": "14px 24px", "overflow": "auto"}),

        footer_bar("temporelle", "energie", footer_data),

    ], style={"display": "flex", "flexDirection": "column",
              "minHeight": "100vh", "background": T["bg"],
              "color": T["text"], "paddingBottom": "52px"})
