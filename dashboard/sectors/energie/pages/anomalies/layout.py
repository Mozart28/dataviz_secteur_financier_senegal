# ============================================================
#  sectors/energie/pages/anomalies/layout.py
#  Page 06 — Anomalies & Qualité de Production
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
    "Norway": "#58A6FF", "Brazil": "#3FB950",
    "India":  "#F0B429", "Australia": "#F85149",
}


def _kpi(label, value, sub, color=None, alert=False):
    c = color or ACCENT
    border_color = T["red"] if alert else c
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
        "borderTop": f"3px solid {border_color}",
        "borderRadius": "8px", "padding": "16px", "flex": "1",
    })


def get_layout():
    df   = get_dataframe()
    kpis = get_kpis(df)
    pays = sorted(df['Country'].unique().tolist())

    import numpy as np

    # KPIs anomalies globaux
    seuil = 0.05
    heures_sol = df[df['Hour'].between(6, 18)]
    anom = heures_sol[(heures_sol['DC_Power'] == 0) & (heures_sol['Irradiation'] > seuil)]
    nb_anom = len(anom)

    # Écart moyen global
    prod = df[df['Irradiation'] > 0]
    m, b = np.polyfit(prod['Irradiation'], prod['DC_Power'], 1)
    df2 = df.copy()
    df2['DC_theorique'] = (m * df2['Irradiation'] + b).clip(lower=0)
    df2['ecart_pct'] = np.where(
        df2['DC_theorique'] > 1,
        (df2['DC_Power'] - df2['DC_theorique']) / df2['DC_theorique'] * 100,
        np.nan
    )
    ecart_moy = df2['ecart_pct'].mean()
    pct_anom  = nb_anom / len(heures_sol) * 100

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
                html.Span("Énergie Solaire · Qualité & Anomalies", style={
                    "color": T["red"], "fontSize": "10px",
                    "letterSpacing": "2px", "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Détection d'Anomalies", style={
                    "margin": "6px 0 0", "fontSize": "20px",
                    "fontWeight": "300", "color": T["text"], "fontFamily": SERIF}),
                html.P("Production nulle · Écart réel vs théorique · Heures perdues · Carte anomalies",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),
            html.Div([
                html.Div([
                    html.Div("PAYS", style={"color": T["muted"], "fontSize": "9px",
                        "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "8px"}),
                    dcc.Dropdown(
                        id="eng-ano-dropdown-pays",
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
                        id="eng-ano-dropdown-mois",
                        options=[{"label": "Tous les mois", "value": "all"}] +
                                [{"label": m, "value": i} for i, m in enumerate(
                                    ["","Janv","Févr","Mars","Avr","Mai","Juin",
                                     "Juil","Août","Sept","Oct","Nov","Déc"], 1)],
                        value="all", clearable=False,
                        style={"width": "150px", "fontSize": "12px"},
                    ),
                ]),
            ], style={"display": "flex", "gap": "16px"}),
        ], style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "flex-end", "flexWrap": "wrap", "gap": "12px",
            "padding": "20px 28px",
            "borderBottom": f"1px solid {T['red']}44",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)",
        }),

        html.Div([

            # KPIs anomalies
            html.Div([
                _kpi("Anomalies détectées",
                    f"{nb_anom}",
                    "heures DC=0, Irr>0.05",
                    T["red"], alert=True),
                _kpi("Taux d'anomalie",
                    f"{pct_anom:.2f}%",
                    "des heures solaires (6h–18h)",
                    T["red"] if pct_anom > 1 else T["green"]),
                _kpi("Écart moyen DC",
                    f"{ecart_moy:+.1f}%",
                    "réel vs théorique global",
                    T["green"] if ecart_moy > 0 else T["red"]),
                _kpi("Seuil irradiation",
                    "0.05 W/m²",
                    "seuil détection anomalie",
                    T["muted"]),
            ], style={"display": "flex", "gap": "12px",
                      "marginBottom": "14px", "flexWrap": "wrap"}),

            # Ligne 1 — Série temporelle + Écart réel vs théorique
            html.Div([
                card_with_tooltip(
                    "Série temporelle DC — zones anormales surlignées",
                    "eng-ano-graph-serie",
                    "ano-serie",
                    TOOLTIPS["ano-serie"],
                    "280px", T["red"],
                    extra_style={"flex": "1.5", "marginRight": "14px",
                                 "borderTop": f"3px solid {T['red']}"},
                ),
                card_with_tooltip(
                    "Écart DC réel vs DC théorique",
                    "eng-ano-graph-ecart",
                    "ano-ecart",
                    TOOLTIPS["ano-ecart"],
                    "280px", T["red"],
                    extra_style={"flex": "1",
                                 "borderTop": f"3px solid {T['red']}"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 2 — Heatmap anomalies + Heures perdues
            html.Div([
                card_with_tooltip(
                    "Carte des anomalies — Heure × Mois",
                    "eng-ano-graph-heatmap",
                    "ano-heatmap",
                    TOOLTIPS["ano-heatmap"],
                    "250px", T["red"],
                    extra_style={"flex": "1", "marginRight": "14px",
                                 "borderTop": f"3px solid {T['red']}"},
                ),
                card_with_tooltip(
                    "Heures perdues par pays et mois",
                    "eng-ano-graph-top",
                    "ano-top",
                    TOOLTIPS["ano-top"],
                    "250px", T["red"],
                    extra_style={"flex": "1",
                                 "borderTop": f"3px solid {T['red']}"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

        ], style={"padding": "14px 24px", "overflow": "auto"}),

        footer_bar("anomalies", "energie", footer_data),

    ], style={"display": "flex", "flexDirection": "column",
              "minHeight": "100vh", "background": T["bg"],
              "color": T["text"], "paddingBottom": "52px"})
