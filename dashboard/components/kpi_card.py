# ============================================================
#  components/kpi_card.py — Composant KPI réutilisable
# ============================================================

import numpy as np
from dash import html
from config import T, MONO


def fmt(val) -> tuple[str, str]:
    """Formate une valeur numérique → (valeur, unité)."""
    if val is None or (isinstance(val, float) and np.isnan(val)) or val == 0:
        return "—", ""
    if abs(val) >= 1_000_000: return f"{val/1_000_000:.2f}", "Bn FCFA"
    if abs(val) >= 1_000:     return f"{val/1_000:.1f}",     "Mds FCFA"
    return f"{val:,.0f}", "M FCFA"


def delta_badge(cur, prev) -> html.Span | str:
    """Badge de variation en % avec couleur et flèche."""
    if cur is None or prev is None or prev == 0:
        return ""
    pct   = (cur - prev) / abs(prev) * 100
    color = T["green"] if pct >= 0 else T["red"]
    arrow = "▲" if pct >= 0 else "▼"
    return html.Span(
        f"{arrow} {abs(pct):.1f}%",
        style={"color": color, "fontSize": "11px", "fontFamily": MONO, "fontWeight": "600"},
    )


def kpi_card(
    label: str,
    value,
    prev_value=None,
    unit: str = "M FCFA",
    highlight: bool = False,
) -> html.Div:
    """
    Carte KPI avec valeur, unité et badge de variation.

    Args:
        label:       Titre affiché en majuscules
        value:       Valeur courante
        prev_value:  Valeur période précédente (pour le delta)
        unit:        Unité de secours (peut être adapté par fmt())
        highlight:   Bordure accent en haut si True
    """
    val_str, unit_str = fmt(value)
    badge = delta_badge(value, prev_value)

    return html.Div(
        [
            html.Div(
                label.upper(),
                style={"color": T["muted"], "fontSize": "9px", "letterSpacing": "1.5px",
                       "fontFamily": MONO, "fontWeight": "600", "marginBottom": "10px"},
            ),
            html.Div(
                val_str,
                style={"color": T["accent"], "fontSize": "28px",
                       "fontWeight": "700", "fontFamily": MONO, "lineHeight": "1"},
            ),
            html.Div(
                [
                    html.Span(unit_str, style={"color": T["muted"], "fontSize": "10px", "fontFamily": MONO}),
                    html.Span(" · ", style={"color": T["border"]}) if badge else "",
                    badge,
                ],
                style={"display": "flex", "alignItems": "center", "gap": "4px", "marginTop": "6px"},
            ),
        ],
        style={
            "background": T["card2"],
            "padding":    "20px 24px",
            "borderTop":  f"2px solid {T['accent']}" if highlight else "2px solid transparent",
        },
    )
