# ============================================================
#  components/tooltip_info.py
#  Tooltip contextuel — CSS pur, zéro callback, zéro dcc.Tooltip
# ============================================================

from dash import html, dcc
from config import MONO, SANS


def card_with_tooltip(
    section_title_text: str,
    graph_id: str,
    tooltip_id: str,
    tooltip_content: dict,
    graph_height: str = "240px",
    accent: str = "#58A6FF",
    extra_style: dict = None,
) -> html.Div:

    card_style = {
        "background":   "#161B22",
        "border":       "1px solid #30363D",
        "borderRadius": "8px",
        "padding":      "18px",
        "position":     "relative",
    }
    if extra_style:
        card_style.update(extra_style)

    # Contenu tooltip en texte brut pour l'attribut HTML title
    parts = []
    if tooltip_content.get("mesure"):
        parts.append(f"Ce que ça mesure : {tooltip_content['mesure']}")
    if tooltip_content.get("lire"):
        parts.append(f"Comment le lire : {tooltip_content['lire']}")
    if tooltip_content.get("surveiller"):
        parts.append(f"À surveiller : {tooltip_content['surveiller']}")
    title_text = "\n\n".join(parts)

    # Panel tooltip stylisé — visible au :hover via CSS inline
    tooltip_panel = html.Div(
        _build_panel(tooltip_content),
        style={
            "display":       "none",   # caché par défaut
            "position":      "absolute",
            "top":           "22px",
            "right":         "0",
            "width":         "290px",
            "background":    "#1C2128",
            "border":        "1px solid #30363D",
            "borderRadius":  "8px",
            "padding":       "14px",
            "zIndex":        "9999",
            "boxShadow":     "0 8px 24px rgba(0,0,0,0.7)",
            "pointerEvents": "none",
        },
        id=f"ttp-{tooltip_id}",
        className="tooltip-panel",
    )

    return html.Div([

        # En-tête
        html.Div([
            html.Div(section_title_text, style={
                "color":        accent,
                "fontSize":     "9px",
                "letterSpacing":"2.5px",
                "fontFamily":   MONO,
                "fontWeight":   "600",
                "textTransform":"uppercase",
            }),
            # Wrapper hover — le CSS dans app assets gère le show/hide
            html.Div([
                html.Span("ⓘ", style={
                    "color":      "#8B949E",
                    "fontSize":   "13px",
                    "cursor":     "help",
                    "fontFamily": "sans-serif",
                }),
                tooltip_panel,
            ], style={
                "position": "relative",
                "display":  "inline-block",
            }, className="tooltip-trigger"),

        ], style={
            "display":        "flex",
            "justifyContent": "space-between",
            "alignItems":     "center",
            "marginBottom":   "14px",
        }),

        # Graphe
        dcc.Loading(
            dcc.Graph(id=graph_id, style={"height": graph_height},
                      config={"displayModeBar": False}),
            type="dot", color=accent, style={"minHeight": graph_height},
        ),

    ], style=card_style)


def _build_panel(content: dict) -> list:
    children = []

    if content.get("titre"):
        children.append(html.Div(content["titre"], style={
            "color":        "#E6EDF3",
            "fontFamily":   MONO,
            "fontSize":     "10px",
            "fontWeight":   "700",
            "marginBottom": "10px",
            "paddingBottom":"8px",
            "borderBottom": "1px solid #30363D",
        }))

    sections = [
        ("mesure",     "📐 Ce que ça mesure"),
        ("lire",       "👁  Comment le lire"),
        ("surveiller", "⚠️  À surveiller"),
    ]

    for key, label in sections:
        if content.get(key):
            children.append(html.Div([
                html.Div(label, style={
                    "color":        "#8B949E",
                    "fontFamily":   MONO,
                    "fontSize":     "8px",
                    "fontWeight":   "600",
                    "letterSpacing":"1px",
                    "textTransform":"uppercase",
                    "marginBottom": "3px",
                }),
                html.Div(content[key], style={
                    "color":      "#E6EDF3",
                    "fontFamily": SANS,
                    "fontSize":   "11px",
                    "lineHeight": "1.5",
                }),
            ], style={"marginBottom": "10px"}))

    return children


def register_tooltip_callbacks(app):
    """Rien à enregistrer — CSS pur."""
    pass
