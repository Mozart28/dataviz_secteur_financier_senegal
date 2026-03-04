# ============================================================
#  sectors/assurance/pages/profil_assure/layout.py
#  Page 03 — Profil Assuré
# ============================================================

from dash import html, dcc
from config import get_theme, MONO, SERIF
from components.footer_bar import footer_bar
from components.tooltip_info import card_with_tooltip
from sectors.assurance.data.tooltips import TOOLTIPS
from sectors.assurance.data.loader import get_dataframe

T      = get_theme("assurance")
ACCENT = T["accent"]


def _section_title(text):
    return html.Div(text, style={
        "color": ACCENT, "fontSize": "9px", "letterSpacing": "2.5px",
        "fontFamily": MONO, "fontWeight": "600",
        "marginBottom": "14px", "textTransform": "uppercase",
    })


def _card(children, extra=None):
    s = {"background": T["card"], "border": f"1px solid {T['border']}",
         "borderRadius": "8px", "padding": "18px"}
    if extra:
        s.update(extra)
    return html.Div(children, style=s)


def _graph(gid, height="240px"):
    return dcc.Loading(
        dcc.Graph(id=gid, style={"height": height},
                  config={"displayModeBar": False}),
        type="dot", color=ACCENT, style={"minHeight": height},
    )


def get_layout():
    df      = get_dataframe()
    branches = sorted(df['type_assurance'].dropna().unique().tolist())

    # KPIs profil
    age_moy   = df['age'].mean()
    age_med   = df['age'].median()
    pct_masc  = (df['sexe'] == 'masculin').mean() * 100
    dur_moy   = df['duree_contrat'].mean()
    bm_moy    = df['bonus_malus'].mean()
    nb_region = df['region'].nunique()

    footer_data = {
        "age_moy":  age_moy,
        "age_med":  age_med,
        "pct_h":    pct_masc,
        "duree_moy":dur_moy,
        "bm_moy":   bm_moy,
        "ratio_sp": df['montant_sinistres'].sum() / df['montant_prime'].sum() * 100,
    }

    def _kpi(label, value, sub, color=None):
        return html.Div([
            html.Div(label, style={"color": T["muted"], "fontSize": "9px",
                "fontFamily": MONO, "letterSpacing": "1.5px",
                "textTransform": "uppercase", "marginBottom": "8px"}),
            html.Div(value, style={"color": color or ACCENT,
                "fontSize": "24px", "fontWeight": "700",
                "fontFamily": MONO, "lineHeight": "1"}),
            html.Div(sub, style={"color": T["muted"], "fontSize": "9px",
                "fontFamily": MONO, "marginTop": "6px"}),
        ], style={
            "background": T["card2"], "border": f"1px solid {T['border']}",
            "borderTop": f"3px solid {color or ACCENT}",
            "borderRadius": "8px", "padding": "18px", "flex": "1",
        })

    return html.Div([

        # ── Header ────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("CIMA · Secteur Assurance · Sénégal", style={
                    "color": ACCENT, "fontSize": "10px",
                    "letterSpacing": "2px", "fontFamily": MONO,
                    "fontWeight": "600"}),
                html.H1("Profil Assuré", style={
                    "margin": "6px 0 0", "fontSize": "20px",
                    "fontWeight": "300", "color": T["text"],
                    "fontFamily": SERIF}),
                html.P("Démographie · Fidélité · Segmentation · Comportement",
                    style={"color": T["muted"], "fontSize": "11px",
                           "fontFamily": MONO, "marginTop": "4px"}),
            ]),
            # Filtre branche
            html.Div([
                html.Div("BRANCHE", style={"color": T["muted"],
                    "fontSize": "9px", "fontFamily": MONO,
                    "letterSpacing": "1.5px", "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="ass-profil-dropdown-branche",
                    options=[{"label": "Toutes", "value": "all"}] +
                            [{"label": b, "value": b} for b in branches],
                    value="all", clearable=False,
                    style={"width": "170px", "fontSize": "12px"},
                ),
            ]),
        ], style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "flex-end", "flexWrap": "wrap",
            "padding": "20px 28px",
            "borderBottom": f"1px solid {T['border']}",
            "background": f"linear-gradient(135deg, {T['card']} 0%, {T['bg']} 100%)",
        }),

        # ── Corps ─────────────────────────────────────────────
        html.Div([

            # Ligne 1 — KPIs
            html.Div([
                _kpi("Âge moyen",       f"{age_moy:.1f} ans",
                     f"médiane {age_med:.0f} ans",     ACCENT),
                _kpi("Hommes / Femmes", f"{pct_masc:.0f}% / {100-pct_masc:.0f}%",
                     f"{df['sexe'].value_counts()['masculin']} H · {df['sexe'].value_counts()['feminin']} F",
                     T["blue"]),
                _kpi("Durée moy. contrat", f"{dur_moy:.1f} ans",
                     "fidélité portefeuille",           T["green"]),
                _kpi("Bonus-malus moy.", f"{bm_moy:.3f}",
                     "référence = 1.000",               T["muted"]),
                _kpi("Régions couvertes", f"{nb_region}",
                     "Dakar · Thiès · S-L · Kaolack",  T["accent"]),
            ], style={"display": "flex", "gap": "12px",
                      "marginBottom": "14px", "flexWrap": "wrap"}),

            # Ligne 2 — Pyramide des âges + Répartition branche/sexe
            html.Div([
                card_with_tooltip(
                    "Pyramide des âges par sexe",
                    "ass-profil-graph-pyramide",
                    "profil-pyramide",
                    TOOLTIPS["profil-pyramide"],
                    "280px",
                    ACCENT, extra_style={'flex': '1', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Portefeuille branche × sexe",
                    "ass-profil-graph-branche-sexe",
                    "profil-branche-sexe",
                    TOOLTIPS["profil-branche-sexe"],
                    "280px",
                    ACCENT, extra_style={'flex': '1', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Répartition géographique",
                    "ass-profil-graph-region",
                    "profil-region",
                    TOOLTIPS["profil-region"],
                    "280px",
                    ACCENT, extra_style={'flex': '0.9'},
                ),

            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 3 — Fidélité + Bonus-malus par profil
            html.Div([
                card_with_tooltip(
                    "Fidélité — sinistralité selon durée contrat",
                    "ass-profil-graph-fidelite",
                    "profil-fidelite",
                    TOOLTIPS["profil-fidelite"],
                    "230px",
                    ACCENT, extra_style={'flex': '1.4', 'marginRight': '14px'},
                ),

                card_with_tooltip(
                    "Bonus-malus — distribution par tranche d'âge",
                    "ass-profil-graph-bm-age",
                    "profil-bm-age",
                    TOOLTIPS["profil-bm-age"],
                    "230px",
                    ACCENT, extra_style={'flex': '1'},
                ),

            ], style={"display": "flex", "marginBottom": "14px"}),

            # Ligne 4 — Heatmap âge × région
            card_with_tooltip(
                    "Concentration du portefeuille — Âge × Région",
                    "ass-profil-graph-heatmap",
                    "profil-heatmap",
                    TOOLTIPS["profil-heatmap"],
                    "240px",
                    ACCENT,
                ),

        ], style={"padding": "14px 24px", "overflow": "auto"}),

            footer_bar("profil_assure", "assurance", footer_data),
    ], style={"display": "flex", "flexDirection": "column",
              "minHeight": "100vh", "background": T["bg"],
              "color": T["text"],
              "paddingBottom": "52px"})
