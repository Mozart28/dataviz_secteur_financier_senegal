# ============================================================
#  pages/structure/layout.py — Structure & Opérationnel
#  Couvre : A2, A3, B4, C1, C2, C3
# ============================================================

from dash import html, dcc
from config import T, MONO, SERIF, SANS
from components.tooltip_info import card_with_tooltip
from data import get_dataframe, get_annees
from data.tooltips import TOOLTIPS

ACCENT = T["accent"]


def _build_tooltip_panel(content: dict) -> list:
    """Reproduit _build_panel de tooltip_info.py pour usage inline."""
    children = []
    if content.get("titre"):
        children.append(html.Div(content["titre"], style={
            "color": "#E6EDF3", "fontFamily": MONO, "fontSize": "10px",
            "fontWeight": "700", "marginBottom": "10px",
            "paddingBottom": "8px", "borderBottom": "1px solid #30363D",
        }))
    for key, label in [("mesure",     "📐 Ce que ça mesure"),
                        ("lire",       "👁  Comment le lire"),
                        ("surveiller", "⚠️  À surveiller")]:
        if content.get(key):
            children.append(html.Div([
                html.Div(label, style={"color": "#8B949E", "fontFamily": MONO,
                    "fontSize": "8px", "fontWeight": "600", "letterSpacing": "1px",
                    "textTransform": "uppercase", "marginBottom": "3px"}),
                html.Div(content[key], style={"color": "#E6EDF3", "fontFamily": SANS,
                    "fontSize": "11px", "lineHeight": "1.5"}),
            ], style={"marginBottom": "10px"}))
    return children


def get_layout():
    annees  = get_annees()
    df      = get_dataframe()
    groupes = sorted(df["Goupe_Bancaire"].dropna().unique().tolist())

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("BCEAO · Analyse opérationnelle", style={"color": ACCENT,
                    "fontSize": "10px", "letterSpacing": "2px",
                    "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Structure & Efficacité Opérationnelle", style={"margin": "6px 0 0",
                    "fontSize": "20px", "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF, "letterSpacing": "0.3px"}),
                html.P("Réseau · Personnel · Comptes · Productivité · Corrélations",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),
            html.Div([
                html.Div([
                    html.Div("ANNÉE", style={"color": T["muted"], "fontSize": "9px",
                        "letterSpacing": "1.5px", "fontFamily": MONO, "marginBottom": "8px"}),
                    dcc.Dropdown(id="str-dropdown-annee",
                        options=[{"label": str(y), "value": y} for y in annees],
                        value=max(annees), clearable=False,
                        style={"width": "110px", "fontSize": "12px"}),
                ]),
                html.Div([
                    html.Div("GROUPE", style={"color": T["muted"], "fontSize": "9px",
                        "letterSpacing": "1.5px", "fontFamily": MONO, "marginBottom": "8px"}),
                    dcc.Dropdown(id="str-dropdown-groupe",
                        options=[{"label": "Tous", "value": "tous"}] +
                                [{"label": g.replace("Groupes ", ""), "value": g}
                                 for g in groupes],
                        value="tous", clearable=False,
                        style={"width": "200px", "fontSize": "12px"}),
                ], style={"marginLeft": "12px"}),
            ], style={"display": "flex", "alignItems": "flex-end"}),
        ], style={"display": "flex", "alignItems": "center",
            "justifyContent": "space-between", "padding": "20px 28px",
            "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)"}),

        # ── KPI Row ───────────────────────────────────────────
        dcc.Loading(
            html.Div(id="str-kpis", style={"display": "grid",
                "gridTemplateColumns": "repeat(5, 1fr)", "gap": "1px",
                "background": T["border"], "borderBottom": f"1px solid {T['border']}"}),
            type="dot", color=ACCENT,
        ),

        # ── Corps ─────────────────────────────────────────────
        html.Div([

            # Ligne 1 : Evolution agences+effectif | Comptes par groupe
            html.Div([
                card_with_tooltip(                                          # A2
                    section_title_text="Évolution réseau & personnel par année",
                    graph_id="str-graph-reseau-evol",
                    tooltip_id="str-reseau-evol",
                    tooltip_content=TOOLTIPS["str-reseau-evol"],
                    graph_height="230px",
                    accent=ACCENT,
                    extra_style={"flex": "1.4", "marginRight": "14px"},
                ),
                card_with_tooltip(                                          # A3
                    section_title_text="Volume de comptes par groupe bancaire",
                    graph_id="str-graph-comptes-groupe",
                    tooltip_id="str-comptes-groupe",
                    tooltip_content=TOOLTIPS["str-comptes-groupe"],
                    graph_height="230px",
                    accent=ACCENT,
                    extra_style={"flex": "1"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 2 : Capitalisation | Evolution EMPLOI
            html.Div([
                card_with_tooltip(                                          # B4
                    section_title_text="Capitalisation : Continentaux vs Régionaux",
                    graph_id="str-graph-capitalisation",
                    tooltip_id="str-capitalisation",
                    tooltip_content=TOOLTIPS["str-capitalisation"],
                    graph_height="230px",
                    accent=ACCENT,
                    extra_style={"flex": "1", "marginRight": "14px"},
                ),
                card_with_tooltip(                                          # C1
                    section_title_text="Évolution de l'EMPLOI sectoriel",
                    graph_id="str-graph-emploi",
                    tooltip_id="str-emploi",
                    tooltip_content=TOOLTIPS["str-emploi"],
                    graph_height="230px",
                    accent=ACCENT,
                    extra_style={"flex": "1"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 3 : Productivité (avec dropdown) | Scatter Agences vs Bilan
            html.Div([
                # Productivité : card manuelle car dropdown interne incompatible
                # avec la signature de card_with_tooltip
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div("Productivité du personnel", style={ # C2
                                "color": ACCENT, "fontSize": "9px",
                                "letterSpacing": "2.5px", "fontFamily": MONO,
                                "fontWeight": "600", "textTransform": "uppercase"}),
                            html.Div([
                                html.Span("ⓘ", style={
                                    "color": "#8B949E", "fontSize": "13px",
                                    "cursor": "help", "fontFamily": "sans-serif"}),
                                html.Div(
                                    _build_tooltip_panel(TOOLTIPS["str-productivite"]),
                                    className="tooltip-panel",
                                    id="ttp-str-productivite",
                                    style={
                                        "display": "none", "position": "absolute",
                                        "top": "22px", "right": "0", "width": "290px",
                                        "background": "#1C2128",
                                        "border": "1px solid #30363D",
                                        "borderRadius": "8px", "padding": "14px",
                                        "zIndex": "9999",
                                        "boxShadow": "0 8px 24px rgba(0,0,0,0.7)",
                                        "pointerEvents": "none",
                                    },
                                ),
                            ], className="tooltip-trigger",
                               style={"position": "relative", "display": "inline-block"}),
                        ], style={"display": "flex", "justifyContent": "space-between",
                                  "alignItems": "center"}),
                        dcc.Dropdown(id="str-dropdown-productivite",
                            options=[
                                {"label": "COMPTE / EFFECTIF", "value": "compte_eff"},
                                {"label": "BILAN / EFFECTIF",  "value": "bilan_eff"},
                            ],
                            value="compte_eff", clearable=False,
                            style={"width": "200px", "fontSize": "11px",
                                   "marginTop": "10px", "marginBottom": "14px"}),
                    ]),
                    dcc.Loading(
                        dcc.Graph(id="str-graph-productivite",
                                  style={"height": "230px"},
                                  config={"displayModeBar": False}),
                        type="dot", color=ACCENT, style={"minHeight": "230px"},
                    ),
                ], style={
                    "background": T["card"], "border": f"1px solid {T['border']}",
                    "borderRadius": "8px", "padding": "18px", "position": "relative",
                    "flex": "1", "marginRight": "14px",
                }),

                card_with_tooltip(                                          # C3 / E4
                    section_title_text="Corrélation Agences vs Bilan (régression)",
                    graph_id="str-graph-scatter-agences",
                    tooltip_id="str-scatter-agences",
                    tooltip_content=TOOLTIPS["str-scatter-agences"],
                    graph_height="230px",
                    accent=ACCENT,
                    extra_style={"flex": "1"},
                ),
            ], style={"display": "flex"}),

        ], style={"padding": "16px 24px", "flex": "1", "overflow": "auto"}),

    ], style={"display": "flex", "flexDirection": "column", "minHeight": "100vh",
        "background": T["bg"], "color": T["text"]})
