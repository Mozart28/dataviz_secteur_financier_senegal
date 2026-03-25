# ============================================================
#  components/navbar.py — Sidebar + Fil d'Ariane
# ============================================================
from dash import html, dcc, Input, Output, callback
from config import get_theme, SECTOR_META, MONO, SERIF, SANS

# ── Mapping URL → label page ──────────────────────────────────
PAGE_LABELS = {
    # Bancaire
    "/bancaire":             "Vue Marché",
    "/bancaire/banque":      "Fiche Banque",
    "/bancaire/comparaison": "Comparaison",
    "/bancaire/ratios":      "Ratios",
    "/bancaire/benchmark":   "Benchmark",
    "/bancaire/carte":       "Carte",
    "/bancaire/structure":   "Structure",
    "/bancaire/prediction": "Positionnement Marché",
    # Énergie
    "/energie":              "Vue Globale",
    "/energie/temporelle":   "Analyse Temporelle",
    "/energie/performance":  "Performance",
    "/energie/climatique":   "Climatique",
    "/energie/comparaison":  "Comparaison",
    "/energie/anomalies":    "Anomalies",
    # Assurance
    "/assurance":            "Vue Portefeuille",
    "/assurance/sinistres":  "Sinistres",
    "/assurance/profil":     "Profil Assuré",
    "/assurance/rentabilite":"Rentabilité",
    "/assurance/scoring":    "Scoring",
}

SECTOR_LABELS = {
    "bancaire":  ("🏦", "Bancaire",  "#F0B429"),
    "energie":   ("⚡", "Énergie",   "#3FB950"),
    "assurance": ("◉", "Assurance", "#58A6FF"),
}


def sidebar():
    T = get_theme()
    return html.Div([

        # ── Logo / titre ──────────────────────────────────────
        html.Div([
            dcc.Link(html.Div([
                html.Div("◈", style={
                    "fontSize": "22px",
                    "background": "linear-gradient(135deg, #F0B429, #3FB950, #58A6FF)",
                    "WebkitBackgroundClip": "text",
                    "WebkitTextFillColor": "transparent",
                    "backgroundClip": "text",
                    "lineHeight": "1",
                }),
                html.Div([
                    html.Div("OBSERVATOIRE", style={
                        "color": T["muted"], "fontFamily": MONO,
                        "fontSize": "7px", "letterSpacing": "2px",
                        "fontWeight": "600", "lineHeight": "1.2",
                    }),
                    html.Div("ÉCONOMIQUE", style={
                        "color": T["muted"], "fontFamily": MONO,
                        "fontSize": "7px", "letterSpacing": "2px",
                        "fontWeight": "600",
                    }),
                ], style={"marginLeft": "10px"}),
            ], style={"display": "flex", "alignItems": "center"}),
            href="/", style={"textDecoration": "none"}),

            # Bouton Home discret
            dcc.Link("⌂", href="/", style={
                "color": T["muted"], "fontSize": "16px",
                "textDecoration": "none", "padding": "4px 8px",
                "borderRadius": "6px", "transition": "color 0.2s",
                "title": "Retour à l'accueil",
            }),
        ], style={
            "display": "flex", "alignItems": "center",
            "justifyContent": "space-between",
            "padding": "20px 16px 16px",
            "borderBottom": f"1px solid {T['border']}",
        }),

        # ── Fil d'Ariane (dynamique) ──────────────────────────
        html.Div(id="breadcrumb", style={
            "padding": "12px 16px",
            "borderBottom": f"1px solid {T['border']}",
            "minHeight": "44px",
        }),

        # ── Navigation pages ──────────────────────────────────
        html.Div(id="nav-links", style={
            "flex": "1", "overflowY": "auto", "padding": "8px 0",
        }),

        # ── Footer navbar ─────────────────────────────────────
        html.Div([
            html.Div("2015 — 2022", style={
                "color": T["muted"], "fontFamily": MONO,
                "fontSize": "9px", "letterSpacing": "1.5px",
                "textAlign": "center", "opacity": "0.5",
            }),
        ], style={
            "padding": "16px",
            "borderTop": f"1px solid {T['border']}",
        }),

    ], style={
        "width": "220px", "minWidth": "220px",
        "height": "100vh", "overflowY": "auto",
        "background": T["card"],
        "borderRight": f"1px solid {T['border']}",
        "display": "flex", "flexDirection": "column",
        "flexShrink": "0",
    })


# ── Callback fil d'Ariane + nav links ────────────────────────
@callback(
    Output("breadcrumb", "children"),
    Output("nav-links",  "children"),
    Input("url", "pathname"),
)
def update_nav(path):
    T = get_theme()
    if not path:
        path = "/"

    # Détecter le secteur
    sector_key = None
    for key in SECTOR_LABELS:
        if path.startswith(f"/{key}"):
            sector_key = key
            break

    # ── Fil d'Ariane ─────────────────────────────────────────
    if sector_key:
        icon, label, accent = SECTOR_LABELS[sector_key]
        page_label = PAGE_LABELS.get(path, "")
        breadcrumb = html.Div([
            dcc.Link("Accueil", href="/", style={
                "color": T["muted"], "fontFamily": MONO,
                "fontSize": "9px", "textDecoration": "none",
                "letterSpacing": "0.5px",
            }),
            html.Span(" › ", style={"color": T["muted"], "fontSize": "9px", "margin": "0 4px"}),
            html.Span(f"{icon} {label}", style={
                "color": accent, "fontFamily": MONO,
                "fontSize": "9px", "fontWeight": "600",
            }),
            *([ 
                html.Span(" › ", style={"color": T["muted"], "fontSize": "9px", "margin": "0 4px"}),
                html.Span(page_label, style={
                    "color": T["text"], "fontFamily": MONO, "fontSize": "9px",
                }),
            ] if page_label and path != f"/{sector_key}" else []),
        ], style={"display": "flex", "alignItems": "center", "flexWrap": "wrap"})
    else:
        breadcrumb = html.Div("Accueil", style={
            "color": T["muted"], "fontFamily": MONO,
            "fontSize": "9px", "letterSpacing": "0.5px",
        })

    # ── Liens de navigation ───────────────────────────────────
    if not sector_key:
        nav = html.Div()
    else:
        icon, label, accent = SECTOR_LABELS[sector_key]
        h = accent.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

        # Pages du secteur courant
        pages = {k: v for k, v in PAGE_LABELS.items() if k.startswith(f"/{sector_key}")}

        # Header secteur
        header = html.Div([
            html.Div(f"{icon}  {label.upper()}", style={
                "color": accent, "fontFamily": MONO,
                "fontSize": "9px", "letterSpacing": "2px",
                "fontWeight": "700", "padding": "16px 16px 8px",
            }),
            html.Div(style={
                "height": "1px", "margin": "0 16px 8px",
                "background": f"linear-gradient(90deg, {accent}, transparent)",
                "opacity": "0.4",
            }),
        ])

        # Items de nav
        items = [header]
        for href, page_name in pages.items():
            is_active = path == href
            items.append(
                dcc.Link(html.Div([
                    html.Span("▸ " if is_active else "  ", style={
                        "color": accent, "fontFamily": MONO,
                        "fontSize": "10px", "marginRight": "6px",
                        "opacity": "1" if is_active else "0",
                        "transition": "opacity 0.2s",
                    }),
                    html.Span(page_name, style={
                        "fontFamily": MONO, "fontSize": "11px",
                        "color": accent if is_active else T["muted"],
                        "fontWeight": "600" if is_active else "400",
                        "transition": "color 0.2s",
                    }),
                ], style={
                    "display": "flex", "alignItems": "center",
                    "padding": "9px 16px",
                    "background": f"rgba({r},{g},{b},0.08)" if is_active else "transparent",
                    "borderLeft": f"2px solid {accent}" if is_active else "2px solid transparent",
                    "transition": "all 0.15s ease",
                }, className="nav-item"),
                href=href, style={"textDecoration": "none", "display": "block"})
            )

        # Séparateur + lien retour secteurs
        items.append(html.Div(style={
            "height": "1px", "margin": "12px 16px",
            "background": T["border"],
        }))
        items.append(dcc.Link(html.Div("← Autres secteurs", style={
            "fontFamily": MONO, "fontSize": "10px",
            "color": T["muted"], "padding": "8px 16px",
            "letterSpacing": "0.5px",
        }, className="nav-item"), href="/", style={"textDecoration": "none"}))

        nav = html.Div(items)

    return breadcrumb, nav
