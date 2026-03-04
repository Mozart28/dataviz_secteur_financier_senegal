# ============================================================
#  pages/comparaison/layout.py — Comparaison Interbancaire
# ============================================================

from dash import html, dcc
from config import T, MONO, SERIF
from components.tooltip_info import card_with_tooltip
from data import get_dataframe, get_annees
from data.tooltips import TOOLTIPS

ACCENT     = T["accent"]
MAX_BANQUES = 5
DEFAULT_BANQUES = ["CBAO", "SGBS", "BIS"]


def _card(children, extra=None):
    s = {"background": T["card"], "border": f"1px solid {T['border']}",
         "borderRadius": "8px", "padding": "20px"}
    if extra: s.update(extra)
    return html.Div(children, style=s)


def _graph(gid, height="240px"):
    return dcc.Loading(
        dcc.Graph(id=gid, style={"height": height}, config={"displayModeBar": False}),
        type="dot", color=ACCENT, style={"minHeight": height},
    )


def _section_title(text):
    return html.Div(text, style={"color": ACCENT, "fontSize": "9px",
        "letterSpacing": "2.5px", "fontFamily": MONO, "fontWeight": "600",
        "marginBottom": "14px", "textTransform": "uppercase"})


def get_layout():
    df      = get_dataframe()
    banques = sorted(df["Sigle"].dropna().unique().tolist())
    annees  = get_annees()
    defaults = [b for b in DEFAULT_BANQUES if b in banques][:3]
    if len(defaults) < 2:
        defaults = banques[:3]

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("BCEAO · Analyse comparative", style={"color": ACCENT,
                    "fontSize": "10px", "letterSpacing": "2px",
                    "fontFamily": MONO, "fontWeight": "600"}),
                html.H1("Comparaison interbancaire", style={"margin": "6px 0 0",
                    "fontSize": "20px", "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF, "letterSpacing": "0.3px"}),
            ]),
            html.Div([
                html.Div([
                    html.Div("BANQUES (MAX 5)", style={"color": T["muted"], "fontSize": "9px",
                        "letterSpacing": "1.5px", "fontFamily": MONO, "marginBottom": "8px"}),
                    dcc.Dropdown(id="cmp-dropdown-banques",
                        options=[{"label": b, "value": b} for b in banques],
                        value=defaults, multi=True, clearable=False,
                        style={"width": "380px", "fontSize": "12px"}),
                ]),
                html.Div([
                    html.Div("ANNÉE", style={"color": T["muted"], "fontSize": "9px",
                        "letterSpacing": "1.5px", "fontFamily": MONO, "marginBottom": "8px"}),
                    dcc.Dropdown(id="cmp-dropdown-annee",
                        options=[{"label": str(y), "value": y} for y in annees],
                        value=max(annees), clearable=False,
                        style={"width": "100px", "fontSize": "12px"}),
                ], style={"marginLeft": "16px"}),
            ], style={"display": "flex", "alignItems": "flex-end"}),
        ], style={"display": "flex", "alignItems": "center",
            "justifyContent": "space-between", "padding": "20px 28px",
            "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)"}),

        html.Div(id="cmp-alert", style={"padding": "6px 28px"}),

        # ── Corps ─────────────────────────────────────────────
        html.Div([

            # Ligne 1 : Heatmap (avec dropdown) + Radar
            html.Div([
                # Heatmap — wrapper custom pour intégrer dropdown
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div("HEATMAP DES PERFORMANCES", style={"color": ACCENT,
                                "fontSize": "9px", "letterSpacing": "2.5px",
                                "fontFamily": MONO, "fontWeight": "600", "textTransform": "uppercase"}),
                            html.Div([
                                html.Span("ⓘ", style={"color": "#8B949E", "fontSize": "13px",
                                    "cursor": "help", "fontFamily": "sans-serif"}),
                                html.Div([
                                    html.Div(TOOLTIPS["cmp-heatmap"].get("titre",""), style={
                                        "color": "#E6EDF3", "fontFamily": MONO, "fontSize": "10px",
                                        "fontWeight": "700", "marginBottom": "10px",
                                        "paddingBottom": "8px", "borderBottom": "1px solid #30363D"}),
                                    html.Div([html.Div("📐 Ce que ça mesure", style={"color":"#8B949E","fontFamily":MONO,"fontSize":"8px","fontWeight":"600","letterSpacing":"1px","textTransform":"uppercase","marginBottom":"3px"}), html.Div(TOOLTIPS["cmp-heatmap"]["mesure"], style={"color":"#E6EDF3","fontSize":"11px","lineHeight":"1.5"})], style={"marginBottom":"10px"}),
                                    html.Div([html.Div("👁  Comment le lire", style={"color":"#8B949E","fontFamily":MONO,"fontSize":"8px","fontWeight":"600","letterSpacing":"1px","textTransform":"uppercase","marginBottom":"3px"}), html.Div(TOOLTIPS["cmp-heatmap"]["lire"], style={"color":"#E6EDF3","fontSize":"11px","lineHeight":"1.5"})], style={"marginBottom":"10px"}),
                                    html.Div([html.Div("⚠️  À surveiller", style={"color":"#8B949E","fontFamily":MONO,"fontSize":"8px","fontWeight":"600","letterSpacing":"1px","textTransform":"uppercase","marginBottom":"3px"}), html.Div(TOOLTIPS["cmp-heatmap"]["surveiller"], style={"color":"#E6EDF3","fontSize":"11px","lineHeight":"1.5"})]),
                                ], style={"display":"none","position":"absolute","top":"22px","right":"0","width":"290px","background":"#1C2128","border":"1px solid #30363D","borderRadius":"8px","padding":"14px","zIndex":"9999","boxShadow":"0 8px 24px rgba(0,0,0,0.7)","pointerEvents":"none"},
                                   id="ttp-cmp-heatmap", className="tooltip-panel"),
                            ], style={"position":"relative","display":"inline-block"}, className="tooltip-trigger"),
                        ], style={"display":"flex","justifyContent":"space-between","alignItems":"center","marginBottom":"14px"}),
                        dcc.Dropdown(id="cmp-heatmap-indic",
                            options=[
                                {"label": "Normalisé (base 100 = max)", "value": "norm"},
                                {"label": "Valeurs absolues (Mds)",     "value": "abs"},
                            ],
                            value="norm", clearable=False,
                            style={"width": "230px", "fontSize": "11px", "marginBottom": "8px"}),
                    ]),
                    _graph("cmp-graph-heatmap", "230px"),
                ], style={"flex": "1.4", "marginRight": "14px",
                    "background": T["card"], "border": f"1px solid {T['border']}",
                    "borderRadius": "8px", "padding": "20px", "position": "relative"}),

                card_with_tooltip(
                    "Radar multi-banques", "cmp-graph-radar",
                    "cmp-radar", TOOLTIPS["cmp-radar"],
                    "230px", ACCENT,
                    extra_style={"flex": "1", "background": T["card"],
                        "border": f"1px solid {T['border']}"},
                ),
            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 2 : Classement (tableau) + Évolution
            html.Div([
                # Classement — tableau sans graphe, pas de card_with_tooltip
                _card([
                    html.Div([
                        _section_title("Classement"),
                        dcc.Dropdown(id="cmp-table-indic",
                            options=[
                                {"label": "Produit Net Bancaire", "value": "PRODUIT.NET.BANCAIRE"},
                                {"label": "Total Bilan",          "value": "BILAN"},
                                {"label": "Résultat Net",         "value": "RESULTAT.NET"},
                                {"label": "ROE (%)",              "value": "ROE"},
                                {"label": "ROA (%)",              "value": "ROA"},
                            ],
                            value="PRODUIT.NET.BANCAIRE", clearable=False,
                            style={"width": "200px", "fontSize": "11px"}),
                    ], style={"display": "flex", "alignItems": "center",
                        "justifyContent": "space-between", "marginBottom": "12px"}),
                    html.Div(id="cmp-table"),
                ], {"flex": "1", "marginRight": "14px"}),

                # Évolution comparée avec dropdown
                html.Div([
                    html.Div([
                        html.Div("ÉVOLUTION COMPARÉE", style={"color": ACCENT,
                            "fontSize": "9px", "letterSpacing": "2.5px",
                            "fontFamily": MONO, "fontWeight": "600", "textTransform": "uppercase"}),
                        dcc.Dropdown(id="cmp-evol-indic",
                            options=[
                                {"label": "Produit Net Bancaire", "value": "pnb"},
                                {"label": "Total Bilan",          "value": "bilan"},
                                {"label": "Résultat Net",         "value": "rn"},
                                {"label": "ROE (%)",              "value": "roe"},
                            ],
                            value="pnb", clearable=False,
                            style={"width": "200px", "fontSize": "11px"}),
                    ], style={"display": "flex", "alignItems": "center",
                        "justifyContent": "space-between", "marginBottom": "14px"}),
                    _graph("cmp-graph-evol", "260px"),
                ], style={"flex": "1.4", "background": T["card"],
                    "border": f"1px solid {T['border']}",
                    "borderRadius": "8px", "padding": "20px"}),

            ], style={"display": "flex"}),

            # Éléments cachés
            html.Div(id="cmp-radar-label", style={"display": "none"}),

        ], style={"padding": "16px 24px", "flex": "1", "overflow": "auto"}),

    ], style={"display": "flex", "flexDirection": "column", "minHeight": "100vh",
        "background": T["bg"], "color": T["text"]})
