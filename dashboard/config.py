# ============================================================
#  config.py — Thème global + accents par secteur
# ============================================================

GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@300;400;500;600;700&"
    "family=JetBrains+Mono:wght@400;600&"
    "family=Playfair+Display:wght@300;400&display=swap"
)
SANS  = "Inter, sans-serif"
MONO  = "JetBrains Mono, monospace"
SERIF = "Playfair Display, serif"

# ── Couleurs de base (partagées) ──────────────────────────────
_BASE = {
    "bg":    "#0D1117",
    "card":  "#161B22",
    "card2": "#1C2128",
    "border":"#30363D",
    "text":  "#E6EDF3",
    "muted": "#8B949E",
    "blue":  "#58A6FF",
    "green": "#3FB950",
    "red":   "#F85149",
}

# ── Accents par secteur ───────────────────────────────────────
SECTOR_ACCENTS = {
    "bancaire":  "#F0B429",   # Or       — richesse, finance
    "energie":   "#3FB950",   # Vert     — nature, électricité
    "assurance": "#58A6FF",   # Bleu     — confiance, stabilité
}

SECTOR_META = {
    "bancaire": {
        "label":    "Secteur Bancaire",
        "sublabel": "24 banques · BCEAO · 2015–2022",
        "icon":     "◈",
        "accent":   SECTOR_ACCENTS["bancaire"],
        "pages":    6,
        "kpis":     ["PNB total", "ROA médian", "ROE médian"],
    },
    "energie": {
        "label":    "Secteur Énergétique",
        "sublabel": "Production · Distribution · Tarifs",
        "icon":     "⚡",
        "accent":   SECTOR_ACCENTS["energie"],
        "pages":    5,
        "kpis":     ["Ratio S/P", "Taux sinistralité", "Primes totales"],
    },
    "assurance": {
        "label":    "Secteur Assurance",
        "sublabel": "1 000 contrats · CIMA · 2021–2025",
        "icon":     "◉",
        "accent":   SECTOR_ACCENTS["assurance"],
        "pages":    5,
        "kpis":     ["Loss Ratio", "Fréquence", "Score risque"],
    },
}


def get_theme(sector: str = "bancaire") -> dict:
    """Retourne le thème complet pour un secteur donné."""
    accent = SECTOR_ACCENTS.get(sector, SECTOR_ACCENTS["bancaire"])
    return {**_BASE, "accent": accent, "sector": sector}


def plotly_base(sector: str = "bancaire", **kwargs) -> dict:
    T = get_theme(sector)
    base = dict(
        paper_bgcolor=T["bg"],
        plot_bgcolor=T["card"],
        font=dict(family=MONO, color=T["muted"], size=10),
        xaxis=dict(gridcolor=T["border"], linecolor=T["border"],
                   tickfont=dict(size=9), showline=False, zeroline=False),
        yaxis=dict(gridcolor=T["border"], linecolor=T["border"],
                   tickfont=dict(size=9), showline=False, zeroline=False),
        margin=dict(l=12, r=12, t=28, b=28),
        hoverlabel=dict(bgcolor=T["card2"], bordercolor=T["border"],
                        font=dict(family=MONO, size=11, color=T["text"])),
    )
    base.update(kwargs)
    return base


def empty_fig(msg: str = "Données non disponibles", sector: str = "bancaire"):
    import plotly.graph_objects as go
    T = get_theme(sector)
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False, font=dict(color=T["muted"], size=12, family=MONO))
    fig.update_layout(**plotly_base(sector,
        xaxis=dict(visible=False), yaxis=dict(visible=False)))
    return fig


# Palette groupes bancaires (spécifique au secteur bancaire)
GROUPE_COLORS = {
    "Groupes Internationaux": "#F0B429",
    "Groupes Continentaux":   "#58A6FF",
    "Groupes Locaux":         "#3FB950",
    "Groupes Règionaux":      "#A78BFA",
}

# Rétrocompatibilité : T = thème bancaire par défaut
T = get_theme("bancaire")

# ── Chemins données ───────────────────────────────────────────
import os as _os, glob as _glob

def _find_data(pattern: str, env_var: str = None) -> str | None:
    if env_var:
        v = _os.environ.get(env_var)
        if v and _os.path.exists(v): return v
    root = _os.path.dirname(_os.path.abspath(__file__))
    candidates = _glob.glob(
        _os.path.join(root, "**", pattern), recursive=True)
    return candidates[0] if candidates else None

EXCEL_FALLBACK = _find_data("*bancaire*senegal*.xlsx", "BANCAIRE_EXCEL")
