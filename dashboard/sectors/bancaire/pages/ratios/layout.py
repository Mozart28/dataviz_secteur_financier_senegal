# ============================================================
#  pages/ratios/layout.py — Ratios & Analyse
# ============================================================

from dash import html, dcc
from config import T, MONO, SERIF
from components.tooltip_info import card_with_tooltip
from data import get_dataframe, get_annees
from data.tooltips import TOOLTIPS

ACCENT = T["accent"]


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


def _kpi_ratio(label, ratio_id, color, benchmark, bench_label):
    return html.Div([
        html.Div(label, style={"color": T["muted"], "fontSize": "9px",
            "letterSpacing": "1.5px", "fontFamily": MONO, "fontWeight": "600",
            "marginBottom": "8px", "textTransform": "uppercase"}),
        html.Div(id=ratio_id, style={"color": color, "fontSize": "24px",
            "fontWeight": "700", "fontFamily": MONO, "lineHeight": "1"}),
        html.Div([
            html.Span("mediane secteur", style={"color": T["muted"],
                "fontSize": "9px", "fontFamily": MONO}),
            html.Span(f" ref {benchmark}", style={"color": T["border"],
                "fontSize": "9px", "fontFamily": MONO}),
        ], style={"marginTop": "4px"}),
    ], style={"background": T["card2"], "padding": "16px 20px",
              "borderRadius": "8px", "borderTop": f"2px solid {color}"})


def _section_header_with_tooltip(title, tooltip_key):
    """Titre de section + icône ⓘ — sans dropdown."""
    tt = TOOLTIPS[tooltip_key]
    rows = []
    for k, lbl in [("mesure","CE QUE CA MESURE"),("lire","COMMENT LE LIRE"),("surveiller","A SURVEILLER")]:
        if tt.get(k):
            rows.append(html.Div([
                html.Div(lbl, style={"color":"#8B949E","fontFamily":MONO,"fontSize":"8px",
                    "fontWeight":"600","letterSpacing":"1px","textTransform":"uppercase","marginBottom":"3px"}),
                html.Div(tt[k], style={"color":"#E6EDF3","fontSize":"11px","lineHeight":"1.5"}),
            ], style={"marginBottom":"10px"}))

    ttp_icon = html.Div([
        html.Span("i", style={"color":"#8B949E","fontSize":"13px","cursor":"help",
            "fontFamily":"sans-serif","fontWeight":"600"}),
        html.Div([
            html.Div(tt.get("titre",""), style={"color":"#E6EDF3","fontFamily":MONO,
                "fontSize":"10px","fontWeight":"700","marginBottom":"10px",
                "paddingBottom":"8px","borderBottom":"1px solid #30363D"}),
            *rows,
        ], style={"display":"none","position":"absolute","top":"22px","right":"0",
            "width":"290px","background":"#1C2128","border":"1px solid #30363D",
            "borderRadius":"8px","padding":"14px","zIndex":"9999",
            "boxShadow":"0 8px 24px rgba(0,0,0,0.7)","pointerEvents":"none"},
           id=f"ttp-{tooltip_key}", className="tooltip-panel"),
    ], style={"position":"relative","display":"inline-block"}, className="tooltip-trigger")

    return html.Div([
        html.Div(title, style={"color":ACCENT,"fontSize":"9px","letterSpacing":"2.5px",
            "fontFamily":MONO,"fontWeight":"600","textTransform":"uppercase"}),
        ttp_icon,
    ], style={"display":"flex","justifyContent":"space-between","alignItems":"center",
              "marginBottom":"10px"})


def get_layout():
    annees  = get_annees()
    df      = get_dataframe()
    groupes = sorted(df["Goupe_Bancaire"].dropna().unique().tolist())

    return html.Div([

        html.Div([
            html.Div([
                html.Span("BCEAO · Analyse prudentielle", style={"color":ACCENT,
                    "fontSize":"10px","letterSpacing":"2px","fontFamily":MONO,"fontWeight":"600"}),
                html.H1("Ratios & Analyse sectorielle", style={"margin":"6px 0 0",
                    "fontSize":"20px","fontWeight":"300","color":T["text"],
                    "fontFamily":SERIF,"letterSpacing":"0.3px"}),
            ]),
            html.Div([
                html.Div([
                    html.Div("ANNEE", style={"color":T["muted"],"fontSize":"9px",
                        "letterSpacing":"1.5px","fontFamily":MONO,"marginBottom":"8px"}),
                    dcc.Dropdown(id="rat-dropdown-annee",
                        options=[{"label":str(y),"value":y} for y in annees],
                        value=max(annees), clearable=False,
                        style={"width":"110px","fontSize":"12px"}),
                ]),
                html.Div([
                    html.Div("GROUPE", style={"color":T["muted"],"fontSize":"9px",
                        "letterSpacing":"1.5px","fontFamily":MONO,"marginBottom":"8px"}),
                    dcc.Dropdown(id="rat-dropdown-groupe",
                        options=[{"label":"Tous","value":"tous"}]+
                                [{"label":g.replace("Groupes ",""),"value":g} for g in groupes],
                        value="tous", clearable=False,
                        style={"width":"180px","fontSize":"12px"}),
                ], style={"marginLeft":"12px"}),
            ], style={"display":"flex","alignItems":"flex-end"}),
        ], style={"display":"flex","alignItems":"center","justifyContent":"space-between",
            "padding":"20px 28px","borderBottom":f"1px solid {T['border']}",
            "background":f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)"}),

        dcc.Loading(
            html.Div([
                _kpi_ratio("ROA median",           "rat-kpi-roa",   T["accent"],"> 1%","bon"),
                _kpi_ratio("ROE median",            "rat-kpi-roe",   T["blue"],  "> 15%","bon"),
                _kpi_ratio("Cout du risque median","rat-kpi-risk",  T["red"],   "< 20%","sain"),
                _kpi_ratio("Marge nette mediane",  "rat-kpi-marge", T["green"], "> 30%","solide"),
                _kpi_ratio("Nb banques rentables", "rat-kpi-profit",T["accent"],"RN > 0","seuil"),
            ], style={"display":"grid","gridTemplateColumns":"repeat(5,1fr)",
                "gap":"1px","background":T["border"],"borderBottom":f"1px solid {T['border']}"}),
            type="dot", color=ACCENT,
        ),

        html.Div([

            # Ligne 1 : Distribution + Top/Flop
            html.Div([
                html.Div([
                    _section_header_with_tooltip("Distribution ROA / ROE", "rat-distribution"),
                    dcc.Dropdown(id="rat-box-indic",
                        options=[{"label":"ROA (%)","value":"ROA"},
                                 {"label":"ROE (%)","value":"ROE"},
                                 {"label":"Marge nette (%)","value":"MARGE_NETTE"},
                                 {"label":"Cout du risque (%)","value":"COUT_RISQUE_PCT"}],
                        value="ROE", clearable=False,
                        style={"width":"190px","fontSize":"11px","marginBottom":"8px"}),
                    _graph("rat-graph-box","230px"),
                ], style={"flex":"1","marginRight":"14px","position":"relative",
                    "background":T["card"],"border":f"1px solid {T['border']}",
                    "borderRadius":"8px","padding":"20px"}),

                html.Div([
                    _section_header_with_tooltip("Top & Flop 5", "rat-topflop"),
                    dcc.Dropdown(id="rat-topflop-indic",
                        options=[{"label":"ROE (%)","value":"ROE"},
                                 {"label":"ROA (%)","value":"ROA"},
                                 {"label":"Marge nette (%)","value":"MARGE_NETTE"},
                                 {"label":"Cout du risque (%)","value":"COUT_RISQUE_PCT"}],
                        value="ROE", clearable=False,
                        style={"width":"190px","fontSize":"11px","marginBottom":"8px"}),
                    _graph("rat-graph-topflop","230px"),
                ], style={"flex":"1","position":"relative",
                    "background":T["card"],"border":f"1px solid {T['border']}",
                    "borderRadius":"8px","padding":"20px"}),
            ], style={"display":"flex","marginBottom":"14px"}),

            # Ligne 2 : Scatter + Evolution mediane
            html.Div([
                card_with_tooltip(
                    "Matrice risque x rentabilite","rat-graph-scatter",
                    "rat-scatter", TOOLTIPS["rat-scatter"],
                    "230px", ACCENT,
                    extra_style={"flex":"1","marginRight":"14px",
                        "background":T["card"],"border":f"1px solid {T['border']}"},
                ),
                html.Div([
                    _section_header_with_tooltip("Evolution mediane sectorielle", "rat-evolution"),
                    dcc.Dropdown(id="rat-evol-indic",
                        options=[{"label":"ROE (%)","value":"ROE"},
                                 {"label":"ROA (%)","value":"ROA"},
                                 {"label":"Marge nette (%)","value":"MARGE_NETTE"},
                                 {"label":"Cout du risque (%)","value":"COUT_RISQUE_PCT"}],
                        value="ROE", clearable=False,
                        style={"width":"190px","fontSize":"11px","marginBottom":"8px"}),
                    _graph("rat-graph-evol","230px"),
                ], style={"flex":"1","position":"relative",
                    "background":T["card"],"border":f"1px solid {T['border']}",
                    "borderRadius":"8px","padding":"20px"}),
            ], style={"display":"flex","marginBottom":"14px"}),

            # Ligne 3 : Tableau
            _card([
                html.Div([
                    html.Div("TABLEAU SYNTHESE", style={"color":ACCENT,"fontSize":"9px",
                        "letterSpacing":"2.5px","fontFamily":MONO,"fontWeight":"600",
                        "textTransform":"uppercase"}),
                    dcc.Dropdown(id="rat-table-sort",
                        options=[{"label":"Trier par ROE","value":"ROE"},
                                 {"label":"Trier par ROA","value":"ROA"},
                                 {"label":"Trier par Marge nette","value":"MARGE_NETTE"},
                                 {"label":"Trier par Cout du risque","value":"COUT_RISQUE_PCT"}],
                        value="ROE", clearable=False,
                        style={"width":"210px","fontSize":"11px"}),
                ], style={"display":"flex","alignItems":"center",
                    "justifyContent":"space-between","marginBottom":"12px"}),
                html.Div(id="rat-table", style={"overflowX":"auto"}),
            ]),

            html.Div(id="rat-scatter-label", style={"display":"none"}),

        ], style={"padding":"16px 24px","flex":"1","overflow":"auto"}),

    ], style={"display":"flex","flexDirection":"column","minHeight":"100vh",
        "background":T["bg"],"color":T["text"]})
