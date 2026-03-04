# ============================================================
#  app.py — Point d'entrée unique · Dashboard Multi-Secteur
# ============================================================

import logging
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback

from config import get_theme, MONO, SANS, GOOGLE_FONTS_URL
from components.navbar import sidebar
from components.tooltip_info import register_tooltip_callbacks

# ── Import des callbacks de chaque secteur ───────────────────
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

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s")

app = dash.Dash(
    __name__, use_pages=False,
    external_stylesheets=[dbc.themes.DARKLY, GOOGLE_FONTS_URL],
    suppress_callback_exceptions=True,
    title="Observatoire Économique · Sénégal",
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
)
server = app.server
register_tooltip_callbacks(app)

T = get_theme()

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
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


@callback(
    Output("sidebar-container", "children"),
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def route(path):
    from home import get_layout as home_layout

    # ── Accueil ───────────────────────────────────────────────
    if not path or path == "/":
        return html.Div(), home_layout()

    # ── Secteur Bancaire ──────────────────────────────────────
    if path.startswith("/bancaire"):
        from sectors.bancaire.pages.vue_marche.layout  import get_layout as vm
        from sectors.bancaire.pages.banque.layout      import get_layout as pb
        from sectors.bancaire.pages.comparaison.layout import get_layout as cmp
        from sectors.bancaire.pages.ratios.layout      import get_layout as rat
        from sectors.bancaire.pages.benchmark.layout   import get_layout as bm
        from sectors.bancaire.pages.carte.layout       import get_layout as ct
        from sectors.bancaire.pages.structure.layout    import get_layout as st
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

    # ── Secteur Énergie ───────────────────────────────────────
    if path.startswith("/energie"):
        from sectors.energie.pages.vue_globale.layout  import get_layout as eng_vg
        from sectors.energie.pages.temporelle.layout   import get_layout as eng_tmp
        from sectors.energie.pages.performance.layout  import get_layout as eng_perf
        from sectors.energie.pages.climatique.layout   import get_layout as eng_clim
        from sectors.energie.pages.comparaison.layout  import get_layout as eng_cmp
        from sectors.energie.pages.anomalies.layout     import get_layout as eng_ano
        nav = sidebar()
        if   path in ("/energie", "/energie/"):    page = eng_vg()
        elif path == "/energie/temporelle":        page = eng_tmp()
        elif path == "/energie/performance":       page = eng_perf()
        elif path == "/energie/climatique":        page = eng_clim()
        elif path == "/energie/comparaison":       page = eng_cmp()
        elif path == "/energie/anomalies":         page = eng_ano()
        else:                                      page = eng_vg()
        return nav, page

    # ── Secteur Assurance ─────────────────────────────────────
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
        else:                                          page = ass_vm()
        return nav, page

    # ── 404 ───────────────────────────────────────────────────
    return html.Div(), html.Div([
        html.Div("404", style={"color": T["muted"], "fontSize": "9px",
            "fontFamily": MONO, "letterSpacing": "3px"}),
        html.H2("Page introuvable", style={"color": T["text"],
            "fontWeight": "300", "fontFamily": "Playfair Display, serif",
            "marginTop": "8px"}),
        dcc.Link("← Retour à l'accueil", href="/",
            style={"color": T["muted"], "fontFamily": MONO,
                   "fontSize": "11px", "marginTop": "16px",
                   "display": "block", "textDecoration": "none"}),
    ], style={"padding": "80px 60px"})


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
  .nav-item:hover {
    background: rgba(240,180,41,0.06) !important;
    color: #E6EDF3 !important;
  }
  .sector-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    border-color: rgba(255,255,255,0.1) !important;
  }
  .Select-control { background-color: #1C2128 !important;
    border-color: #30363D !important; color: #E6EDF3 !important; }
  .Select-menu-outer { background-color: #1C2128 !important;
    border-color: #30363D !important; }
  .Select-option { color: #E6EDF3 !important; }
  .Select-option.is-focused { background-color: #30363D !important; }
  .Select-value-label { color: #E6EDF3 !important; }
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .dash-graph { animation: fadeInUp 0.25s ease forwards; }
  @keyframes fadeIn {
    from { opacity: 0; } to { opacity: 1; }
  }
  #page-content { animation: fadeIn 0.2s ease; }
</style>
</head>
<body>
{%app_entry%}
<footer>{%config%}{%scripts%}{%renderer%}</footer>
</body></html>"""


if __name__ == "__main__":
    app.run(debug=True, port=8050, host="0.0.0.0")
