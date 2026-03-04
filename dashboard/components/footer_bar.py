# ============================================================
#  components/footer_bar.py
#  Barre de synthèse fixe en bas — métriques contextuelles
#  par page, toujours visible même en scroll
# ============================================================

from dash import html
from config import MONO


# ── Statut sectoriel global ───────────────────────────────────

def _sector_status(ratio: float, thresholds: tuple = (70, 100)) -> tuple:
    """Retourne (couleur, label, icône) selon un ratio clé."""
    warn, crit = thresholds
    if ratio >= crit:  return "#F85149", "CRITIQUE", "▲"
    if ratio >= warn:  return "#F0B429", "ATTENTION", "◆"
    return "#3FB950", "NORMAL",   "●"


# ── Métrique individuelle ─────────────────────────────────────

def _metric(label: str, value: str, sub: str = "",
            color: str = "#E6EDF3", alert: bool = False) -> html.Div:
    return html.Div([
        html.Div(label, style={
            "color":        "#8B949E",
            "fontSize":     "8px",
            "fontFamily":   MONO,
            "letterSpacing":"1.2px",
            "textTransform":"uppercase",
            "marginBottom": "2px",
        }),
        html.Div([
            html.Span(value, style={
                "color":      color,
                "fontSize":   "12px",
                "fontWeight": "700",
                "fontFamily": MONO,
            }),
            html.Span(f"  {sub}", style={
                "color":    "#8B949E",
                "fontSize": "9px",
                "fontFamily": MONO,
            }) if sub else None,
        ], style={"display": "flex", "alignItems": "baseline"}),
    ], style={
        "padding":        "0 20px",
        "borderLeft":     "1px solid #30363D",
        "display":        "flex",
        "flexDirection":  "column",
        "justifyContent": "center",
    })


def _separator() -> html.Div:
    return html.Div(style={
        "width":      "1px",
        "height":     "24px",
        "background": "#30363D",
        "alignSelf":  "center",
    })


# ── Footer principal ──────────────────────────────────────────

def footer_bar(page: str, sector: str, data: dict) -> html.Div:
    """
    Génère la barre de synthèse fixe.

    page   : identifiant de la page ('vue_portefeuille', 'sinistres', etc.)
    sector : 'assurance' | 'bancaire'
    data   : dict des métriques pré-calculées
    """
    metrics = _get_metrics(page, sector, data)
    status_color, status_label, status_icon = _get_status(page, sector, data)

    accent = {
        "assurance": "#58A6FF",
        "bancaire":  "#3FB950",
        "energie":   "#3FB950",
    }.get(sector, "#58A6FF")

    sector_label = {
        "assurance": "ASSURANCE",
        "bancaire":  "BANCAIRE",
        "energie":   "ÉNERGIE",
    }.get(sector, sector.upper())

    page_label = {
        "vue_portefeuille": "VUE PORTEFEUILLE",
        "sinistres":        "SINISTRES",
        "profil_assure":    "PROFIL ASSURÉ",
        "rentabilite":      "RENTABILITÉ",
        "scoring":          "SCORING RISQUE",
        "vue_globale":      "VUE GLOBALE",
        "temporelle":       "TEMPORELLE",
        "performance":      "PERFORMANCE",
        "climatique":       "CLIMATIQUE",
        "comparaison":      "COMPARAISON",
        "anomalies":        "ANOMALIES",
    }.get(page, page.upper().replace("_", " "))

    return html.Div([

        # ── Gauche : badge secteur + page ────────────────────
        html.Div([
            html.Div([
                html.Span("■ ", style={"color": accent, "fontSize": "8px"}),
                html.Span(sector_label, style={
                    "color":        accent,
                    "fontSize":     "9px",
                    "fontFamily":   MONO,
                    "fontWeight":   "700",
                    "letterSpacing":"1.5px",
                }),
            ]),
            html.Div(page_label, style={
                "color":        "#8B949E",
                "fontSize":     "8px",
                "fontFamily":   MONO,
                "letterSpacing":"1px",
                "marginTop":    "2px",
            }),
        ], style={
            "padding":        "0 20px 0 16px",
            "borderRight":    "1px solid #30363D",
            "display":        "flex",
            "flexDirection":  "column",
            "justifyContent": "center",
            "minWidth":       "130px",
        }),

        # ── Centre : métriques contextuelles ─────────────────
        html.Div(metrics, style={
            "display":    "flex",
            "flex":       "1",
            "alignItems": "stretch",
        }),

        # ── Droite : statut sectoriel ─────────────────────────
        html.Div([
            html.Div([
                html.Span(f"{status_icon} ", style={
                    "color":    status_color,
                    "fontSize": "10px",
                }),
                html.Span("STATUT", style={
                    "color":        "#8B949E",
                    "fontSize":     "8px",
                    "fontFamily":   MONO,
                    "letterSpacing":"1px",
                }),
            ]),
            html.Div(status_label, style={
                "color":      status_color,
                "fontSize":   "11px",
                "fontFamily": MONO,
                "fontWeight": "700",
                "marginTop":  "2px",
            }),
        ], style={
            "padding":        "0 20px",
            "borderLeft":     "1px solid #30363D",
            "display":        "flex",
            "flexDirection":  "column",
            "justifyContent": "center",
            "minWidth":       "100px",
        }),

    ], style={
        "position":      "fixed",
        "bottom":        "0",
        "left":          "0",
        "right":         "0",
        "height":        "52px",
        "background":    "#0D1117",
        "borderTop":     f"1px solid {accent}22",
        "display":       "flex",
        "alignItems":    "stretch",
        "zIndex":        "1000",
        "boxShadow":     "0 -4px 16px rgba(0,0,0,0.4)",
    })


# ── Métriques par page ────────────────────────────────────────

def _get_metrics(page: str, sector: str, data: dict) -> list:
    """Retourne la liste de métriques selon la page."""

    if sector == "assurance":
        if page == "vue_portefeuille":
            lr = data.get("ratio_sp", 0)
            lr_color = "#F85149" if lr > 100 else "#F0B429" if lr > 70 else "#3FB950"
            return [
                _metric("Primes collectées",
                    f"{data.get('total_primes', 0)/1e6:.2f} M FCFA",
                    f"{data.get('nb_contrats', 0):,} contrats"),
                _metric("Ratio S/P",
                    f"{lr:.1f}%",
                    "sinistres / primes",
                    lr_color),
                _metric("Sinistres payés",
                    f"{data.get('total_sinistres', 0)/1e6:.2f} M FCFA"),
                _metric("Prime moyenne",
                    f"{data.get('prime_moyenne', 0):,.0f} FCFA",
                    "par contrat"),
            ]

        elif page == "sinistres":
            return [
                _metric("Fréquence sinistres",
                    f"{data.get('freq', 0):.1f}%",
                    "contrats sinistrés"),
                _metric("Sévérité moyenne",
                    f"{data.get('severite', 0):,.0f}",
                    "montant moy / sinistré",
                    "#F85149"),
                _metric("Coût total sinistres",
                    f"{data.get('cout_total', 0)/1e6:.2f} M FCFA"),
                _metric("P90 sévérité",
                    f"{data.get('p90', 0):,.0f}",
                    "90e percentile"),
            ]

        elif page == "profil_assure":
            return [
                _metric("Âge moyen",
                    f"{data.get('age_moy', 0):.1f} ans",
                    f"médiane {data.get('age_med', 0):.0f} ans"),
                _metric("Hommes / Femmes",
                    f"{data.get('pct_h', 0):.0f}% / {100-data.get('pct_h', 0):.0f}%"),
                _metric("Durée moy. contrat",
                    f"{data.get('duree_moy', 0):.1f} ans",
                    "fidélité portefeuille"),
                _metric("Bonus-malus moyen",
                    f"{data.get('bm_moy', 0):.3f}",
                    "réf. = 1.000",
                    "#3FB950" if data.get("bm_moy", 1) <= 1.0 else "#F0B429"),
            ]

        elif page == "rentabilite":
            cr = data.get("combined_ratio", 0)
            cr_color = "#F85149" if cr > 100 else "#3FB950"
            mg = 100 - cr
            mg_color = "#3FB950" if mg > 0 else "#F85149"
            return [
                _metric("Loss Ratio",
                    f"{data.get('loss_ratio', 0):.1f}%",
                    color="#F85149" if data.get("loss_ratio", 0) > 100 else "#F0B429"),
                _metric("Combined Ratio",
                    f"{cr:.1f}%",
                    "LR + ER", cr_color),
                _metric("Marge technique",
                    f"{mg:+.1f}%",
                    "100% − CR", mg_color),
                _metric("Contrats rentables",
                    f"{data.get('pct_rentable', 0):.1f}%",
                    "prime > sinistre"),
            ]

        elif page == "scoring":
            auc = data.get("auc", 0)
            auc_color = "#3FB950" if auc > 0.7 else "#F0B429" if auc > 0.55 else "#F85149"
            return [
                _metric("AUC modèle",
                    f"{auc:.3f}",
                    "Random Forest", auc_color),
                _metric("Risque élevé / très élevé",
                    f"{data.get('pct_haut_risque', 0):.0f}%",
                    "du portefeuille",
                    "#F0B429"),
                _metric("Score moyen",
                    f"{data.get('score_moy', 0):.3f}",
                    "portefeuille entier"),
                _metric("Meilleur segment",
                    f"{data.get('best_seg_freq', 0):.1f}%",
                    "fréq. risque faible",
                    "#3FB950"),
            ]

    if sector == "energie":
        if page in ("vue_globale","temporelle","performance","climatique","comparaison"):
            eff  = data.get("efficiency_moy", 0)
            irr  = data.get("irradiation_moy", 0)
            best = data.get("best_country", "—")
            yld  = data.get("total_yield", 0)
            eff_color = "#3FB950" if eff >= 90 else "#F0B429" if eff >= 85 else "#F85149"
            return [
                _metric("Production totale",
                    f"{yld/1e6:.1f} M kWh", "4 pays · 12 mois"),
                _metric("Rendement DC→AC",
                    f"{eff:.1f}%", "efficacité conversion", eff_color),
                _metric("Irradiation moy.",
                    f"{irr:.3f} W/m²", "rayonnement solaire", "#F0B429"),
                _metric("Meilleur pays",
                    best, "production cumulée max", "#3FB950"),
            ]

    return []


def _get_status(page: str, sector: str, data: dict) -> tuple:
    """Retourne (couleur, label, icône) pour le statut sectoriel."""
    if sector == "assurance":
        ratio = data.get("ratio_sp", data.get("loss_ratio", 0))
        return _sector_status(ratio, thresholds=(70, 100))
    if sector == "energie":
        eff = data.get("efficiency_moy", 90)
        if eff >= 90:   return "#3FB950", "OPTIMAL",   "●"
        if eff >= 85:   return "#F0B429", "ATTENTION",  "◆"
        return "#F85149", "DÉGRADÉ", "▲"
    return "#8B949E", "N/A", "○"
