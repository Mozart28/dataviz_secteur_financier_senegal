# ============================================================
#  components/navbar.py — Sidebar adaptative multi-secteur
# ============================================================

from dash import html, dcc, Input, Output, callback
from config import MONO, SECTOR_META, get_theme

# Pages par secteur
SECTOR_PAGES = {
    "bancaire": [
        {"path": "/bancaire",             "num": "01", "icon": "◈", "label": "Vue Marché"},
        {"path": "/bancaire/banque",      "num": "02", "icon": "◉", "label": "Profil Banque"},
        {"path": "/bancaire/comparaison", "num": "03", "icon": "◐", "label": "Comparaison"},
        {"path": "/bancaire/ratios",      "num": "04", "icon": "◑", "label": "Ratios & Analyse"},
        {"path": "/bancaire/benchmark",   "num": "05", "icon": "◎", "label": "Benchmark"},
        {"path": "/bancaire/carte",       "num": "06", "icon": "◍", "label": "Carte & Réseau"},
        {"path": "/bancaire/structure",    "num": "07", "icon": "⚙️",  "label": "Structure & Opérationnel"},
    ],
    "energie": [
        {"path": "/energie",               "num": "01", "icon": "⚡", "label": "Vue Globale"},
        {"path": "/energie/temporelle",    "num": "02", "icon": "📅", "label": "Analyse Temporelle"},
        {"path": "/energie/performance",   "num": "03", "icon": "⚙️", "label": "Performance"},
        {"path": "/energie/climatique",    "num": "04", "icon": "🌡", "label": "Conditions Climatiques"},
        {"path": "/energie/comparaison",   "num": "05", "icon": "🔀", "label": "Comparaison Pays"},
        {"path": "/energie/anomalies",     "num": "06", "icon": "⚠",  "label": "Anomalies & Qualité"},
    ],
    "assurance": [
        {"path": "/assurance",                    "num": "01", "icon": "◉", "label": "Vue Portefeuille"},
        {"path": "/assurance/sinistres",          "num": "02", "icon": "◈", "label": "Analyse Sinistres"},
        {"path": "/assurance/profil",             "num": "03", "icon": "◐", "label": "Profil Assuré"},
        {"path": "/assurance/rentabilite",        "num": "04", "icon": "◑", "label": "Rentabilité"},
        {"path": "/assurance/scoring",            "num": "05", "icon": "◎", "label": "Scoring Risque"},
    ],
}


def _current_sector(pathname: str) -> str:
    if not pathname or pathname == "/":
        return None
    for s in ["bancaire", "energie", "assurance"]:
        if pathname.startswith(f"/{s}"):
            return s
    return None


def sidebar():
    T = get_theme("bancaire")   # défaut — mis à jour dynamiquement
    return html.Nav([
        # Logo dynamique
        html.Div(id="nav-logo",
            style={"borderBottom": f"1px solid {T['border']}"}),

        # Bouton retour accueil
        html.Div([
            dcc.Link("← Accueil", href="/",
                style={"color": T["muted"], "fontFamily": MONO, "fontSize": "10px",
                       "textDecoration": "none", "letterSpacing": "1px",
                       "padding": "10px 16px", "display": "block",
                       "borderBottom": f"1px solid {T['border']}",
                       "opacity": "0.7"}),
        ], id="nav-back"),

        # Liens de navigation
        html.Div(id="nav-links", style={"padding": "12px 0", "flex": "1"}),

        # Footer
        html.Div(id="nav-footer",
            style={"position": "absolute", "bottom": "20px",
                   "left": "0", "right": "0", "padding": "0 16px"}),

    ], style={
        "width": "210px", "minWidth": "210px",
        "background": T["card"],
        "borderRight": f"1px solid {T['border']}",
        "display": "flex", "flexDirection": "column",
        "height": "100vh", "overflowY": "auto",
        "position": "relative",
    })


@callback(
    Output("nav-logo",    "children"),
    Output("nav-back",    "style"),
    Output("nav-links",   "children"),
    Output("nav-footer",  "children"),
    Input("url", "pathname"),
)
def update_nav(pathname):
    sector  = _current_sector(pathname)
    T       = get_theme(sector or "bancaire")
    meta    = SECTOR_META.get(sector, {})
    accent  = T["accent"]

    # ── Logo ──────────────────────────────────────────────────
    icon  = meta.get("icon", "◈")
    label = meta.get("label", "Dashboard") if sector else "Dashboard"
    sub   = "SÉNÉGAL" if sector else "MULTI-SECTEUR"

    logo = html.Div([
        html.Div(icon, style={
            "width": "38px", "height": "38px",
            "background": accent, "color": T["bg"],
            "display": "flex", "alignItems": "center",
            "justifyContent": "center", "fontWeight": "800",
            "fontSize": "16px", "fontFamily": MONO, "borderRadius": "6px",
        }),
        html.Div([
            html.Div(label.upper()[:16], style={"color": accent, "fontSize": "8px",
                "letterSpacing": "1.5px", "fontFamily": MONO, "fontWeight": "600"}),
            html.Div(sub, style={"color": T["text"], "fontSize": "10px",
                "letterSpacing": "2px", "fontFamily": MONO,
                "fontWeight": "600", "marginTop": "2px"}),
        ], style={"marginLeft": "10px"}),
    ], style={"display": "flex", "alignItems": "center",
              "padding": "20px 16px 20px"})

    # ── Bouton retour : visible seulement si dans un secteur ──
    back_style = {
        "display": "block" if sector else "none",
        "borderBottom": f"1px solid {T['border']}",
    }

    # ── Liens ──────────────────────────────────────────────────
    if not sector:
        # Page d'accueil — pas de liens
        links = []
    else:
        pages = SECTOR_PAGES.get(sector, [])
        links = []
        for p in pages:
            is_active = (pathname == p["path"]) or \
                        (pathname in ("/", "") and p["path"] == f"/{sector}")

            if is_active:
                style = {"display": "flex", "alignItems": "center", "gap": "10px",
                    "padding": "11px 14px", "borderRadius": "6px",
                    "margin": "2px 8px",
                    "background": f"rgba({_hex_to_rgb(accent)},0.10)",
                    "borderLeft": f"2px solid {accent}"}
                label_style = {"fontSize": "12px", "fontFamily": MONO,
                    "color": accent, "fontWeight": "600"}
                icon_col = accent
            else:
                style = {"display": "flex", "alignItems": "center", "gap": "10px",
                    "padding": "11px 14px", "borderRadius": "6px",
                    "margin": "2px 8px", "color": T["muted"],
                    "borderLeft": "2px solid transparent"}
                label_style = {"fontSize": "12px", "fontFamily": MONO,
                    "color": T["muted"]}
                icon_col = T["blue"]

            links.append(dcc.Link(
                html.Div([
                    html.Span(p["num"], style={"color": accent, "fontSize": "9px",
                        "fontFamily": MONO, "fontWeight": "600",
                        "letterSpacing": "1px", "minWidth": "20px", "opacity": "0.7"}),
                    html.Span(p["icon"], style={"fontSize": "14px",
                        "color": icon_col, "minWidth": "20px", "textAlign": "center"}),
                    html.Span(p["label"], style=label_style),
                ], className="" if is_active else "nav-item", style=style),
                href=p["path"], style={"textDecoration": "none"},
            ))

    # ── Footer ─────────────────────────────────────────────────
    sublabel = meta.get("sublabel", "") if sector else "Sénégal · Multi-secteur"
    footer = html.Div([
        html.Div(sublabel, style={"color": T["muted"], "fontSize": "9px",
            "fontFamily": MONO, "opacity": "0.6", "lineHeight": "1.5"}),
    ])

    return logo, back_style, links, footer


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"
