# ============================================================
#  app.py — Point d'entrée unique · Dashboard Multi-Secteur
# ============================================================
import logging
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback, ctx, no_update

from config import get_theme, MONO, SERIF, SANS, GOOGLE_FONTS_URL
from components.navbar import sidebar
from components.tooltip_info import register_tooltip_callbacks

import sectors.bancaire.pages.vue_marche.callbacks
import sectors.bancaire.pages.banque.callbacks
import sectors.bancaire.pages.comparaison.callbacks
import sectors.bancaire.pages.ratios.callbacks
import sectors.bancaire.pages.benchmark.callbacks
import sectors.bancaire.pages.carte.callbacks
import sectors.bancaire.pages.structure.callbacks
import sectors.assurance.pages.vue_portefeuille.callbacks
import sectors.assurance.pages.sinistres.callbacks
import sectors.assurance.pages.profil_assure.callbacks
import sectors.assurance.pages.rentabilite.callbacks
import sectors.assurance.pages.scoring.callbacks
import sectors.energie.pages.vue_globale.callbacks
import sectors.energie.pages.temporelle.callbacks
import sectors.energie.pages.performance.callbacks
import sectors.energie.pages.climatique.callbacks
import sectors.energie.pages.comparaison.callbacks
import sectors.energie.pages.anomalies.callbacks
import login
import home

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s")

# ── Données du tour ───────────────────────────────────────────
TOUR_STEPS = [
    {
        "title": "Bienvenue 👋",
        "text": "Ce dashboard analyse les secteurs bancaire, énergétique et assurantiel du Sénégal sur la période 2015–2022.",
        "btn_next": "Commencer →",
        "show_prev": False,
    },
    {
        "title": "3 secteurs à explorer",
        "text": "Chaque carte donne accès à un secteur avec ses propres pages d'analyse. Cliquez sur une carte pour entrer.",
        "btn_next": "Suivant →",
        "show_prev": True,
    },
    {
        "title": "Sources officielles ◈",
        "text": "Toutes les données proviennent de sources officielles (BCEAO, SENELEC, CIMA). Consultez-les via ce bouton.",
        "btn_next": "Suivant →",
        "show_prev": True,
    },
    {
        "title": "C'est parti 🚀",
        "text": "Choisissez un secteur ci-dessous pour commencer votre analyse. Bonne exploration !",
        "btn_next": "Démarrer",
        "show_prev": True,
    },
]

app = dash.Dash(
    __name__, use_pages=False,
    external_stylesheets=[dbc.themes.DARKLY, GOOGLE_FONTS_URL],
    suppress_callback_exceptions=True,
    title="Observatoire Économique · Sénégal",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server
app.server.secret_key = "bceao-senegal-2024"
register_tooltip_callbacks(app)
T = get_theme()

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="auth-store", storage_type="session", data={"authenticated": False}),
    dcc.Store(id="tour-store", data={"step": 0, "active": False}),

    # ── Onboarding overlay ────────────────────────────────────
    html.Div(id="tour-backdrop", style={
        "position": "fixed", "inset": "0",
        "background": "rgba(0,0,0,0.7)",
        "zIndex": "200", "display": "none",
    }),
    html.Div([
        # Progression dots
        html.Div(id="tour-dots", style={
            "display": "flex", "gap": "6px", "marginBottom": "20px",
        }),
        # Titre
        html.Div(id="tour-title", style={
            "color": "#E6EDF3", "fontFamily": SERIF,
            "fontWeight": "300", "fontSize": "22px", "marginBottom": "12px",
        }),
        # Texte
        html.Div(id="tour-text", style={
            "color": "#8B949E", "fontFamily": MONO,
            "fontSize": "11px", "lineHeight": "1.9", "marginBottom": "28px",
        }),
        # Boutons
        html.Div([
            html.Button("Passer", id="tour-skip", n_clicks=0, style={
                "background": "none", "border": "none",
                "color": "#8B949E", "fontFamily": MONO,
                "fontSize": "10px", "cursor": "pointer",
                "letterSpacing": "1px",
            }),
            html.Div(style={"flex": "1"}),
            html.Button("←", id="tour-prev", n_clicks=0, style={
                "background": "none", "border": "1px solid #30363D",
                "borderRadius": "6px", "color": "#8B949E",
                "fontFamily": MONO, "fontSize": "13px",
                "cursor": "pointer", "padding": "8px 14px", "marginRight": "8px",
            }),
            html.Button("Suivant →", id="tour-next", n_clicks=0, style={
                "background": "linear-gradient(135deg, rgba(240,180,41,0.2), rgba(63,185,80,0.15))",
                "border": "1px solid rgba(240,180,41,0.5)",
                "borderRadius": "6px", "color": "#F0B429",
                "fontFamily": MONO, "fontSize": "11px",
                "fontWeight": "600", "letterSpacing": "1.5px",
                "cursor": "pointer", "padding": "8px 20px",
            }),
        ], style={"display": "flex", "alignItems": "center"}),
    ], id="tour-bubble", style={
        "position": "fixed",
        "top": "50%", "left": "50%",
        "transform": "translate(-50%, -50%)",
        "background": "#161B22",
        "border": "1px solid #30363D",
        "borderTop": "3px solid #F0B429",
        "borderRadius": "12px",
        "padding": "32px",
        "width": "400px",
        "boxShadow": "0 24px 64px rgba(0,0,0,0.7)",
        "zIndex": "201",
        "display": "none",
    }),

    # ── App principale ────────────────────────────────────────
    html.Div(id="sidebar-container"),
    html.Main(id="page-content", style={
        "flex": "1", "height": "100vh",
        "overflowY": "auto", "background": T["bg"],
    }),
], style={
    "display": "flex", "height": "100vh",
    "background": T["bg"], "color": T["text"],
    "fontFamily": SANS, "overflow": "hidden",
})


# ── Route ─────────────────────────────────────────────────────
@callback(
    Output("sidebar-container", "children"),
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("auth-store", "data"),
)
def route(path, auth_data):
    from login import get_layout as login_layout
    from home  import get_layout as home_layout

    authenticated = auth_data and auth_data.get("authenticated")
    if not authenticated:
        return html.Div(), login_layout()

    if not path or path == "/":
        return html.Div(), home_layout()

    if path.startswith("/bancaire"):
        from sectors.bancaire.pages.vue_marche.layout  import get_layout as vm
        from sectors.bancaire.pages.banque.layout      import get_layout as pb
        from sectors.bancaire.pages.comparaison.layout import get_layout as cmp
        from sectors.bancaire.pages.ratios.layout      import get_layout as rat
        from sectors.bancaire.pages.benchmark.layout   import get_layout as bm
        from sectors.bancaire.pages.carte.layout       import get_layout as ct
        from sectors.bancaire.pages.structure.layout   import get_layout as st
        nav = sidebar()
        if   path == "/bancaire":             page = vm()
        elif path == "/bancaire/banque":      page = pb()
        elif path == "/bancaire/comparaison": page = cmp()
        elif path == "/bancaire/ratios":      page = rat()
        elif path == "/bancaire/benchmark":   page = bm()
        elif path == "/bancaire/carte":       page = ct()
        elif path == "/bancaire/structure":   page = st()
        else:                                 page = vm()
        return nav, page

    if path.startswith("/energie"):
        from sectors.energie.pages.vue_globale.layout  import get_layout as eng_vg
        from sectors.energie.pages.temporelle.layout   import get_layout as eng_tmp
        from sectors.energie.pages.performance.layout  import get_layout as eng_perf
        from sectors.energie.pages.climatique.layout   import get_layout as eng_clim
        from sectors.energie.pages.comparaison.layout  import get_layout as eng_cmp
        from sectors.energie.pages.anomalies.layout    import get_layout as eng_ano
        nav = sidebar()
        if   path in ("/energie", "/energie/"):  page = eng_vg()
        elif path == "/energie/temporelle":      page = eng_tmp()
        elif path == "/energie/performance":     page = eng_perf()
        elif path == "/energie/climatique":      page = eng_clim()
        elif path == "/energie/comparaison":     page = eng_cmp()
        elif path == "/energie/anomalies":       page = eng_ano()
        else:                                    page = eng_vg()
        return nav, page

    if path.startswith("/assurance"):
        from sectors.assurance.pages.vue_portefeuille.layout import get_layout as ass_vm
        from sectors.assurance.pages.sinistres.layout        import get_layout as ass_sin
        nav = sidebar()
        if   path in ("/assurance", "/assurance/"):  page = ass_vm()
        elif path == "/assurance/sinistres":          page = ass_sin()
        elif path == "/assurance/profil":
            from sectors.assurance.pages.profil_assure.layout import get_layout as ass_pr
            page = ass_pr()
        elif path == "/assurance/rentabilite":
            from sectors.assurance.pages.rentabilite.layout import get_layout as ass_rt
            page = ass_rt()
        elif path == "/assurance/scoring":
            from sectors.assurance.pages.scoring.layout import get_layout as ass_sc
            page = ass_sc()
        else:                                         page = ass_vm()
        return nav, page

    return html.Div(), html.Div([
        html.Div("404", style={"color": T["muted"], "fontSize": "9px",
            "fontFamily": MONO, "letterSpacing": "3px"}),
        html.H2("Page introuvable", style={"color": T["text"],
            "fontWeight": "300", "fontFamily": "Playfair Display, serif", "marginTop": "8px"}),
        dcc.Link("← Retour à l'accueil", href="/",
            style={"color": T["muted"], "fontFamily": MONO, "fontSize": "11px",
                   "marginTop": "16px", "display": "block", "textDecoration": "none"}),
    ], style={"padding": "80px 60px"})


# ── Panneau Sources ───────────────────────────────────────────
@callback(
    Output("about-panel",   "style"),
    Output("about-backdrop","style"),
    Input("about-open",     "n_clicks"),
    Input("about-close",    "n_clicks"),
    Input("about-backdrop", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_about_panel(o, c, b):
    panel_base = {
        "position": "fixed", "top": "0", "right": "0",
        "width": "420px", "height": "100vh",
        "background": "#161B22", "borderLeft": "1px solid #30363D",
        "zIndex": "100",
        "transition": "transform 0.35s cubic-bezier(0.4, 0, 0.2, 1)",
        "display": "flex", "flexDirection": "column",
        "boxShadow": "-24px 0 64px rgba(0,0,0,0.6)",
    }
    bd_hidden  = {"position": "fixed", "inset": "0", "background": "rgba(0,0,0,0.5)",
                  "zIndex": "99", "display": "none", "cursor": "pointer"}
    if ctx.triggered_id == "about-open":
        return {**panel_base, "transform": "translateX(0)"}, {**bd_hidden, "display": "block"}
    return {**panel_base, "transform": "translateX(100%)"}, bd_hidden


# ── Tour : déclenchement auto au login ────────────────────────
@callback(
    Output("tour-store", "data"),
    Input("auth-store", "data"),
    State("tour-store", "data"),
    prevent_initial_call=True,
)
def start_tour(auth_data, tour_data):
    if auth_data and auth_data.get("authenticated"):
        return {"step": 0, "active": True}
    return tour_data or {"step": 0, "active": False}


# ── Tour : navigation (next / prev / skip) ────────────────────
@callback(
    Output("tour-store",   "data", allow_duplicate=True),
    Input("tour-next",  "n_clicks"),
    Input("tour-prev",  "n_clicks"),
    Input("tour-skip",  "n_clicks"),
    State("tour-store", "data"),
    prevent_initial_call=True,
)
def navigate_tour(next_c, prev_c, skip_c, tour_data):
    if not tour_data or not tour_data.get("active"):
        return no_update
    step = tour_data.get("step", 0)
    triggered = ctx.triggered_id
    if triggered == "tour-next":
        new_step = step + 1
        if new_step >= len(TOUR_STEPS):
            return {"step": 0, "active": False}
        return {"step": new_step, "active": True}
    elif triggered == "tour-prev":
        return {"step": max(0, step - 1), "active": True}
    elif triggered == "tour-skip":
        return {"step": 0, "active": False}
    return no_update


# ── Tour : rendu de la bulle ──────────────────────────────────
@callback(
    Output("tour-backdrop", "style"),
    Output("tour-bubble",   "style"),
    Output("tour-dots",     "children"),
    Output("tour-title",    "children"),
    Output("tour-text",     "children"),
    Output("tour-next",     "children"),
    Output("tour-prev",     "style"),
    Input("tour-store", "data"),
)
def render_tour(tour_data):
    bubble_base = {
        "position": "fixed", "top": "50%", "left": "50%",
        "transform": "translate(-50%, -50%)",
        "background": "#161B22", "border": "1px solid #30363D",
        "borderTop": "3px solid #F0B429", "borderRadius": "12px",
        "padding": "32px", "width": "400px",
        "boxShadow": "0 24px 64px rgba(0,0,0,0.7)",
        "zIndex": "201",
    }
    bd_hidden     = {"position": "fixed", "inset": "0", "background": "rgba(0,0,0,0.7)",
                     "zIndex": "200", "display": "none"}
    prev_hidden   = {"background": "none", "border": "1px solid #30363D", "borderRadius": "6px",
                     "color": "#8B949E", "fontFamily": MONO, "fontSize": "13px",
                     "cursor": "pointer", "padding": "8px 14px", "marginRight": "8px",
                     "display": "none"}
    prev_visible  = {**prev_hidden, "display": "inline-block"}

    if not tour_data or not tour_data.get("active"):
        return bd_hidden, {**bubble_base, "display": "none"}, [], "", "", "Suivant →", prev_hidden

    step = tour_data.get("step", 0)
    s    = TOUR_STEPS[step]

    # Dots de progression
    dots = [
        html.Div(style={
            "width": "8px", "height": "8px", "borderRadius": "50%",
            "background": "#F0B429" if i == step else "#30363D",
            "transition": "background 0.3s",
        }) for i in range(len(TOUR_STEPS))
    ]

    return (
        {**bd_hidden, "display": "block"},
        {**bubble_base, "display": "block"},
        dots,
        s["title"],
        s["text"],
        s["btn_next"],
        prev_visible if s["show_prev"] else prev_hidden,
    )


app.index_string = """<!DOCTYPE html>
<html><head>
{%metas%}<title>{%title%}</title>{%favicon%}{%css%}
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { overflow: hidden; }
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: #0D1117; }
  ::-webkit-scrollbar-thumb { background: #30363D; border-radius: 2px; }
  ::-webkit-scrollbar-thumb:hover { background: #F0B429; }
  .nav-item:hover { background: rgba(240,180,41,0.06) !important; color: #E6EDF3 !important; }
  .sector-card:hover { transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
  .Select-control { background-color: #1C2128 !important; border-color: #30363D !important; color: #E6EDF3 !important; }
  .Select-menu-outer { background-color: #1C2128 !important; border-color: #30363D !important; }
  .Select-option { color: #E6EDF3 !important; }
  .Select-option.is-focused { background-color: #30363D !important; }
  .Select-value-label { color: #E6EDF3 !important; }
  @keyframes fadeInUp { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
  @keyframes fadeIn   { from { opacity:0; } to { opacity:1; } }
  .dash-graph { animation: fadeInUp 0.25s ease forwards; }
  #page-content { animation: fadeIn 0.2s ease; }
  #tour-bubble { animation: fadeInUp 0.3s ease; }
</style>
</head><body>
{%app_entry%}
<footer>{%config%}{%scripts%}{%renderer%}</footer>
</body></html>"""

if __name__ == "__main__":
    app.run(debug=True, port=8050, host="0.0.0.0")
