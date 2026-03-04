# ============================================================
#  pages/comparaison/callbacks.py — Comparaison Interbancaire
# ============================================================

import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, callback, html

from config import T, MONO, GROUPE_COLORS, plotly_base, empty_fig
from data import get_dataframe, agg, compute_ratios

MAX_BANQUES = 5

# Palette de couleurs distinctes pour les 5 banques
PALETTE = ["#F0B429", "#58A6FF", "#3FB950", "#F85149", "#A78BFA"]

# Indicateurs pour heatmap
HEATMAP_ROWS = [
    ("PRODUIT.NET.BANCAIRE", "PNB"),
    ("RESULTAT.NET",         "Résultat Net"),
    ("FONDS.PROPRE",         "Fonds Propres"),
    ("CRÉANCES.SUR.LA.CLIENTÈLE", "Créances clients"),
]

RADAR_AXES = [
    ("PRODUIT.NET.BANCAIRE", "PNB"),
    ("RESULTAT.NET",         "RN"),
    ("FONDS.PROPRE",         "FP"),
    ("CRÉANCES.SUR.LA.CLIENTÈLE", "Créances"),
    ("CAPITAUX.PROPRES.ET.RESSOURCES.ASSIMILÉES", "Capitaux"),
]


def _clamp(banques):
    """Limite à MAX_BANQUES et garantit une liste."""
    if not banques:
        return []
    if isinstance(banques, str):
        banques = [banques]
    return list(banques)[:MAX_BANQUES]


# ── Alerte dépassement ────────────────────────────────────────

@callback(Output("cmp-alert", "children"), Input("cmp-dropdown-banques", "value"))
def cb_alert(banques):
    if banques and len(banques) > MAX_BANQUES:
        return html.Div(
            f"⚠ Maximum {MAX_BANQUES} banques — seules les {MAX_BANQUES} premières sont affichées.",
            style={"color": T["red"], "fontSize": "10px", "fontFamily": MONO,
                   "padding": "6px 12px", "background": "rgba(248,81,73,0.08)",
                   "borderRadius": "4px", "border": f"1px solid {T['red']}",
                   "marginTop": "8px"},
        )
    return ""


# ── Heatmap ───────────────────────────────────────────────────

@callback(
    Output("cmp-graph-heatmap", "figure"),
    Input("cmp-dropdown-banques", "value"),
    Input("cmp-dropdown-annee",   "value"),
    Input("cmp-heatmap-indic",    "value"),
)
def cb_heatmap(banques, annee, mode):
    banques = _clamp(banques)
    if not banques or not annee:
        return empty_fig()

    df = compute_ratios(get_dataframe())
    d  = df[df["ANNEE"] == annee]

    # Indicateurs : absolus + ratios
    rows_abs = [(c, lbl) for c, lbl in HEATMAP_ROWS if c in df.columns]
    rows_ratio = []
    for col, lbl in [("ROA", "ROA (%)"), ("ROE", "ROE (%)")]:
        if col in df.columns:
            rows_ratio.append((col, lbl))
    all_rows = rows_abs + rows_ratio

    # Construire la matrice banques × indicateurs
    z_vals  = []
    z_text  = []
    y_labels = [lbl for _, lbl in all_rows]

    for col, lbl in all_rows:
        row_vals = []
        row_text = []
        col_data = [agg(d[d["Sigle"] == b], col) for b in banques]
        col_data_clean = [v for v in col_data if v is not None]
        max_v = max(col_data_clean) if col_data_clean else 1

        for b in banques:
            v = agg(d[d["Sigle"] == b], col)
            if v is None:
                row_vals.append(None)
                row_text.append("—")
            else:
                if mode == "norm":
                    row_vals.append(v / max_v * 100 if max_v != 0 else 0)
                    row_text.append(f"{v/1000:.1f} Mds" if col not in ("ROA","ROE") else f"{v:.2f}%")
                else:
                    row_vals.append(v / 1000 if col not in ("ROA","ROE") else v)
                    row_text.append(f"{v/1000:.1f}" if col not in ("ROA","ROE") else f"{v:.2f}%")
        z_vals.append(row_vals)
        z_text.append(row_text)

    fig = go.Figure(go.Heatmap(
        z=z_vals,
        x=banques,
        y=y_labels,
        text=z_text,
        texttemplate="%{text}",
        textfont=dict(size=10, family=MONO),
        colorscale=[
            [0.0,  "rgba(13,17,23,1)"],
            [0.3,  "rgba(22,27,34,1)"],
            [0.6,  "rgba(88,166,255,0.4)"],
            [0.85, "rgba(240,180,41,0.7)"],
            [1.0,  "rgba(240,180,41,1)"],
        ],
        showscale=False,
        hoverongaps=False,
        hovertemplate="<b>%{x}</b> · %{y}<br>%{text}<extra></extra>",
    ))

    layout = plotly_base(showlegend=False)
    layout["xaxis"] = dict(tickfont=dict(size=11, family=MONO, color=T["text"]),
                           gridcolor="rgba(0,0,0,0)")
    layout["yaxis"] = dict(tickfont=dict(size=10, family=MONO, color=T["muted"]),
                           gridcolor="rgba(0,0,0,0)", autorange="reversed")
    layout["margin"] = dict(l=130, r=8, t=20, b=8)
    fig.update_layout(**layout)
    return fig


# ── Radar multi-banques ───────────────────────────────────────

@callback(
    Output("cmp-graph-radar",  "figure"),
    Output("cmp-radar-label",  "children"),
    Input("cmp-dropdown-banques", "value"),
    Input("cmp-dropdown-annee",   "value"),
)
def cb_radar(banques, annee):
    banques = _clamp(banques)
    if not banques or not annee:
        return empty_fig(), ""

    df     = get_dataframe()
    d_year = df[df["ANNEE"] == annee]
    nb     = d_year["Sigle"].nunique()

    fig = go.Figure()
    axes_labels = None

    for i, banque in enumerate(banques):
        d_bank = d_year[d_year["Sigle"] == banque]
        axes, vals = [], []

        for col, label in RADAR_AXES:
            if col not in df.columns:
                continue
            v_b = agg(d_bank, col)
            v_s = agg(d_year, col)
            if not v_b or not v_s or nb == 0:
                continue
            axes.append(label)
            vals.append(min(v_b / (v_s / nb) * 100, 300))

        if len(axes) < 3:
            continue

        if axes_labels is None:
            axes_labels = axes

        # Fermer le polygone
        axes_r = axes + [axes[0]]
        vals_r = vals + [vals[0]]
        color  = PALETTE[i % len(PALETTE)]

        fig.add_trace(go.Scatterpolar(
            r=vals_r, theta=axes_r,
            fill="toself",
            fillcolor="rgba({},{},{},0.08)".format(
                int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            ) if color.startswith("#") else color,
            line=dict(color=color, width=2),
            name=banque,
        ))

    if not fig.data:
        return empty_fig("Données insuffisantes"), ""

    base = {k: v for k, v in plotly_base().items() if k not in ("xaxis", "yaxis")}
    base.update(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 300],
                tickfont=dict(size=8, color=T["muted"]),
                gridcolor=T["border"], linecolor=T["border"]),
            angularaxis=dict(tickfont=dict(size=10, family=MONO, color=T["muted"]),
                gridcolor=T["border"], linecolor=T["border"]),
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2,
            xanchor="center", x=0.5, font=dict(size=9, color=T["muted"]),
            bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=40, t=20, b=50),
    )
    fig.update_layout(**base)
    return fig, f"Base 100 = moyenne sectorielle · {annee}"


# ── Tableau classement ────────────────────────────────────────

@callback(
    Output("cmp-table", "children"),
    Input("cmp-dropdown-banques", "value"),
    Input("cmp-dropdown-annee",   "value"),
    Input("cmp-table-indic",      "value"),
)
def cb_table(banques, annee, indic):
    banques = _clamp(banques)
    if not banques or not annee:
        return ""

    df = compute_ratios(get_dataframe())
    d  = df[df["ANNEE"] == annee]

    # Construire les données du tableau
    rows = []
    for b in banques:
        d_b = d[d["Sigle"] == b]
        if d_b.empty:
            continue
        row = d_b.iloc[0]
        val = row.get(indic, np.nan)
        if isinstance(val, float) and np.isnan(val):
            val = None
        rows.append({"banque": b, "val": val,
                     "groupe": row.get("Goupe_Bancaire", "")})

    # Trier par valeur décroissante
    rows_valid = [r for r in rows if r["val"] is not None]
    rows_null  = [r for r in rows if r["val"] is None]
    rows_valid.sort(key=lambda r: r["val"], reverse=True)
    rows_sorted = rows_valid + rows_null

    is_ratio  = indic in ("ROA", "ROE")
    max_val   = max((r["val"] for r in rows_valid), default=1) or 1

    def _bar(val):
        """Mini barre de progression inline."""
        if val is None or max_val == 0:
            return html.Div("—", style={"color": T["muted"], "fontFamily": MONO})
        pct = min(val / max_val * 100, 100)
        fmt = f"{val:.2f}%" if is_ratio else f"{val/1000:.1f} Mds"
        return html.Div([
            html.Div(fmt, style={"color": T["text"], "fontFamily": MONO,
                "fontSize": "12px", "marginBottom": "4px"}),
            html.Div(style={"height": "4px", "borderRadius": "2px",
                "background": f"linear-gradient(90deg, {T['accent']} {pct}%, {T['border']} {pct}%)"}),
        ])

    header = html.Div([
        html.Div("RANG",   style={"width": "40px",  "color": T["muted"], "fontSize": "9px", "fontFamily": MONO, "letterSpacing": "1px"}),
        html.Div("BANQUE", style={"flex": "1",      "color": T["muted"], "fontSize": "9px", "fontFamily": MONO, "letterSpacing": "1px"}),
        html.Div("GROUPE", style={"width": "130px", "color": T["muted"], "fontSize": "9px", "fontFamily": MONO, "letterSpacing": "1px"}),
        html.Div("VALEUR", style={"width": "180px", "color": T["muted"], "fontSize": "9px", "fontFamily": MONO, "letterSpacing": "1px"}),
    ], style={"display": "flex", "gap": "12px", "padding": "8px 0",
              "borderBottom": f"1px solid {T['border']}", "marginBottom": "4px"})

    table_rows = []
    for rank, r in enumerate(rows_sorted, 1):
        color  = GROUPE_COLORS.get(r["groupe"], T["muted"])
        medal  = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        table_rows.append(html.Div([
            html.Div(medal, style={"width": "40px", "fontFamily": MONO,
                "fontSize": "13px", "color": T["accent"] if rank == 1 else T["muted"]}),
            html.Div(r["banque"], style={"flex": "1", "fontFamily": MONO,
                "fontSize": "13px", "color": T["text"], "fontWeight": "600"}),
            html.Div(r["groupe"].replace("Groupes ", ""),
                style={"width": "130px", "fontFamily": MONO, "fontSize": "10px", "color": color}),
            html.Div(_bar(r["val"]), style={"width": "180px"}),
        ], style={"display": "flex", "gap": "12px", "alignItems": "center",
            "padding": "10px 0", "borderBottom": f"1px solid {T['border']}"}))

    return html.Div([header] + table_rows)


# ── Évolution comparée ────────────────────────────────────────

@callback(
    Output("cmp-graph-evol", "figure"),
    Input("cmp-dropdown-banques", "value"),
    Input("cmp-evol-indic",       "value"),
)
def cb_evol(banques, indic):
    banques = _clamp(banques)
    if not banques:
        return empty_fig()

    col_map = {
        "pnb":   ("PRODUIT.NET.BANCAIRE", "PNB (Mds FCFA)",    False),
        "bilan": ("BILAN",                "Bilan (Mds FCFA)",   False),
        "rn":    ("RESULTAT.NET",         "RN (Mds FCFA)",      False),
        "roe":   ("ROE",                  "ROE (%)",            True),
    }
    col, ylabel, is_ratio = col_map.get(indic, col_map["pnb"])

    df = compute_ratios(get_dataframe()) if is_ratio else get_dataframe()
    annees = sorted(df["ANNEE"].dropna().unique().tolist())
    fig = go.Figure()

    for i, banque in enumerate(banques):
        d_b  = df[df["Sigle"] == banque].sort_values("ANNEE")
        if col not in d_b.columns:
            continue
        vals = d_b[col] if is_ratio else d_b[col] / 1000
        if not vals.notna().any():
            continue

        color = PALETTE[i % len(PALETTE)]
        xs    = d_b["ANNEE"].tolist()

        fig.add_trace(go.Scatter(
            x=xs, y=vals,
            name=banque, mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=7, color=color, line=dict(color=T["bg"], width=1.5)),
            hovertemplate=f"<b>{banque}</b> %{{x}}<br>%{{y:,.2f}}<extra></extra>",
        ))

        # Annotation dernière valeur
        last_val = vals.dropna().iloc[-1] if vals.notna().any() else None
        last_yr  = d_b.loc[vals.notna(), "ANNEE"].iloc[-1] if vals.notna().any() else None
        if last_val is not None:
            fig.add_annotation(
                x=last_yr, y=last_val,
                text=f" {banque}",
                showarrow=False, xanchor="left",
                font=dict(size=9, color=color, family=MONO),
            )

    if not fig.data:
        return empty_fig("Données non disponibles")

    # Annotation COVID
    if 2020 in annees:
        fig.add_vline(x=2020, line_dash="dot", line_color=T["red"], line_width=1,
            annotation_text="COVID", annotation_position="top",
            annotation_font=dict(size=8, color=T["red"], family=MONO))

    fig.update_layout(**plotly_base(
        yaxis_title=ylabel, showlegend=True, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9, color=T["muted"]),
            bgcolor="rgba(0,0,0,0)"),
    ))
    return fig
