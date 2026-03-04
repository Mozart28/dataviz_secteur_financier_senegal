# ============================================================
#  pages/ratios/callbacks.py — Ratios & Analyse sectorielle
# ============================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, html

from config import T, MONO, GROUPE_COLORS, plotly_base, empty_fig
from data import get_dataframe, compute_ratios

PALETTE = ["#F0B429", "#58A6FF", "#3FB950", "#F85149", "#A78BFA",
           "#FFA07A", "#20B2AA", "#DDA0DD", "#90EE90", "#87CEEB"]

RATIO_META = {
    "ROA":           {"label": "ROA (%)",            "ref": 1.0,  "higher_better": True},
    "ROE":           {"label": "ROE (%)",             "ref": 15.0, "higher_better": True},
    "MARGE_NETTE":   {"label": "Marge nette (%)",     "ref": 30.0, "higher_better": True},
    "COUT_RISQUE_PCT":{"label": "Coût du risque (%)","ref": 20.0, "higher_better": False},
}


def _get_df(annee, groupe):
    df = compute_ratios(get_dataframe())
    if annee:
        df = df[df["ANNEE"] == annee]
    if groupe and groupe != "tous":
        df = df[df["Goupe_Bancaire"] == groupe]
    return df


def _safe_median(series):
    v = series.dropna()
    return float(v.median()) if len(v) > 0 else None


def _fmt_pct(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "—"
    return f"{val:.2f}%"


# ── KPI médianes ──────────────────────────────────────────────

@callback(
    Output("rat-kpi-roa",    "children"),
    Output("rat-kpi-roe",    "children"),
    Output("rat-kpi-risk",   "children"),
    Output("rat-kpi-marge",  "children"),
    Output("rat-kpi-profit", "children"),
    Input("rat-dropdown-annee",  "value"),
    Input("rat-dropdown-groupe", "value"),
)
def cb_kpis(annee, groupe):
    df = _get_df(annee, groupe)
    profit = int((df["RESULTAT.NET"] > 0).sum()) if "RESULTAT.NET" in df.columns else 0
    total  = int(df["Sigle"].nunique())
    return (
        _fmt_pct(_safe_median(df["ROA"])),
        _fmt_pct(_safe_median(df["ROE"])),
        _fmt_pct(_safe_median(df["COUT_RISQUE_PCT"])),
        _fmt_pct(_safe_median(df["MARGE_NETTE"])),
        f"{profit} / {total}",
    )


# ── Box plot distribution ─────────────────────────────────────

@callback(
    Output("rat-graph-box", "figure"),
    Input("rat-dropdown-annee",  "value"),
    Input("rat-dropdown-groupe", "value"),
    Input("rat-box-indic",       "value"),
)
def cb_box(annee, groupe, indic):
    # Box plot sur toutes les années avec année sélectionnée en surbrillance
    df_all = compute_ratios(get_dataframe())
    if groupe and groupe != "tous":
        df_all = df_all[df_all["Goupe_Bancaire"] == groupe]

    annees = sorted(df_all["ANNEE"].dropna().unique().tolist())
    meta   = RATIO_META.get(indic, {"label": indic, "ref": None})

    if indic not in df_all.columns:
        return empty_fig(f"{indic} non disponible")

    fig = go.Figure()

    for y in annees:
        d_y   = df_all[df_all["ANNEE"] == y][indic].dropna()
        is_sel = (y == annee)
        fig.add_trace(go.Box(
            y=d_y,
            name=str(y),
            marker=dict(color=T["accent"] if is_sel else T["muted"],
                        size=5, outliercolor=T["red"]),
            line=dict(color=T["accent"] if is_sel else T["border"], width=2 if is_sel else 1),
            fillcolor=f"rgba(240,180,41,0.15)" if is_sel else f"rgba(48,54,61,0.3)",
            boxpoints="outliers",
            showlegend=False,
            hovertemplate=f"<b>%{{x}}</b><br>{meta['label']}: %{{y:.2f}}%<extra></extra>",
        ))

    # Ligne de référence
    if meta.get("ref"):
        fig.add_hline(y=meta["ref"], line_dash="dot", line_color=T["blue"], line_width=1.5,
            annotation_text=f"Réf. {meta['ref']}%",
            annotation_font=dict(size=8, color=T["blue"], family=MONO),
            annotation_position="right")

    fig.update_layout(**plotly_base(
        yaxis_title=meta["label"], showlegend=False,
        xaxis=dict(gridcolor=T["border"], tickfont=dict(size=10, family=MONO)),
    ))
    return fig


# ── Top & Flop 5 ──────────────────────────────────────────────

@callback(
    Output("rat-graph-topflop", "figure"),
    Input("rat-dropdown-annee",  "value"),
    Input("rat-dropdown-groupe", "value"),
    Input("rat-topflop-indic",   "value"),
)
def cb_topflop(annee, groupe, indic):
    df   = _get_df(annee, groupe)
    meta = RATIO_META.get(indic, {"label": indic, "higher_better": True})

    if indic not in df.columns:
        return empty_fig()

    d = df[["Sigle", "Goupe_Bancaire", indic]].dropna(subset=[indic])
    if d.empty:
        return empty_fig("Données insuffisantes")

    d_sorted = d.sort_values(indic, ascending=False)
    top5  = d_sorted.head(5)
    flop5 = d_sorted.tail(5).sort_values(indic, ascending=True)

    fig = go.Figure()

    # TOP 5
    fig.add_trace(go.Bar(
        x=top5[indic], y=top5["Sigle"],
        orientation="h", name="Top 5",
        marker=dict(color=T["green"], opacity=0.85, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in top5[indic]],
        textposition="outside",
        textfont=dict(size=10, color=T["muted"], family=MONO),
        hovertemplate="<b>%{y}</b><br>%{x:.2f}%<extra></extra>",
    ))

    # FLOP 5 (valeurs négatives ou basses)
    fig.add_trace(go.Bar(
        x=flop5[indic], y=flop5["Sigle"],
        orientation="h", name="Flop 5",
        marker=dict(color=T["red"], opacity=0.75, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in flop5[indic]],
        textposition="outside",
        textfont=dict(size=10, color=T["muted"], family=MONO),
        hovertemplate="<b>%{y}</b><br>%{x:.2f}%<extra></extra>",
    ))

    # Ligne médiane
    med = _safe_median(d[indic])
    if med:
        fig.add_vline(x=med, line_dash="dot", line_color=T["accent"], line_width=1.5,
            annotation_text=f"Médiane : {med:.1f}%",
            annotation_font=dict(size=8, color=T["accent"], family=MONO),
            annotation_position="top")

    layout = plotly_base(
        xaxis_title=meta["label"], showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9, color=T["muted"]),
            bgcolor="rgba(0,0,0,0)"),
        bargap=0.25,
    )
    layout["yaxis"] = dict(gridcolor=T["border"], tickfont=dict(size=10),
                           showline=False, autorange="reversed")
    fig.update_layout(**layout)
    return fig


# ── Scatter risque × rentabilité ──────────────────────────────

@callback(
    Output("rat-graph-scatter",  "figure"),
    Output("rat-scatter-label",  "children"),
    Input("rat-dropdown-annee",  "value"),
    Input("rat-dropdown-groupe", "value"),
)
def cb_scatter(annee, groupe):
    df = _get_df(annee, groupe)

    needed = ["ROE", "ROA", "COUT_RISQUE_PCT", "Sigle", "Goupe_Bancaire"]
    avail  = [c for c in needed if c in df.columns]
    if "ROE" not in avail or "COUT_RISQUE_PCT" not in avail:
        return empty_fig("ROE ou Coût du risque non disponibles"), ""

    d = df[avail].dropna(subset=["ROE", "COUT_RISQUE_PCT"])
    if d.empty:
        return empty_fig("Données insuffisantes"), ""

    colors = [GROUPE_COLORS.get(g, T["muted"]) for g in d["Goupe_Bancaire"]]
    sizes  = [12] * len(d)
    if "ROA" in d.columns:
        roa_clean = d["ROA"].fillna(0)
        sizes = (roa_clean.clip(lower=0) / (roa_clean.max() or 1) * 18 + 8).tolist()

    fig = go.Figure()

    # Quadrants
    med_roe  = _safe_median(d["ROE"])
    med_risk = _safe_median(d["COUT_RISQUE_PCT"])
    if med_roe and med_risk:
        fig.add_hline(y=med_roe,  line_dash="dot", line_color=T["border"], line_width=1)
        fig.add_vline(x=med_risk, line_dash="dot", line_color=T["border"], line_width=1)
        # Labels quadrants
        x_max = d["COUT_RISQUE_PCT"].max() * 1.1
        y_max = d["ROE"].max() * 1.1
        for txt, xa, ya, col in [
            ("Rentable · Risqué",   x_max*0.85, y_max*0.9,  T["accent"]),
            ("Rentable · Sain",     x_max*0.05, y_max*0.9,  T["green"]),
            ("Fragile · Risqué",    x_max*0.85, y_max*0.05, T["red"]),
            ("Fragile · Sain",      x_max*0.05, y_max*0.05, T["muted"]),
        ]:
            fig.add_annotation(x=xa, y=ya, text=txt, showarrow=False,
                font=dict(size=8, color=col, family=MONO),
                bgcolor="rgba(13,17,23,0.7)", borderpad=3)

    fig.add_trace(go.Scatter(
        x=d["COUT_RISQUE_PCT"], y=d["ROE"],
        mode="markers+text", text=d["Sigle"],
        textposition="top center",
        textfont=dict(size=9, color=T["muted"], family=MONO),
        marker=dict(size=sizes, color=colors,
                    line=dict(color=T["bg"], width=1.5), opacity=0.85),
        hovertemplate="<b>%{text}</b><br>ROE : %{y:.1f}%<br>Coût risque : %{x:.1f}%<extra></extra>",
    ))

    fig.update_layout(**plotly_base(
        xaxis_title="Coût du risque (%)",
        yaxis_title="ROE (%)",
        showlegend=False, hovermode="closest",
    ))
    return fig, f"Taille des bulles = ROA · {annee}"


# ── Évolution médiane sectorielle ─────────────────────────────

@callback(
    Output("rat-graph-evol", "figure"),
    Input("rat-dropdown-groupe", "value"),
    Input("rat-evol-indic",      "value"),
)
def cb_evol(groupe, indic):
    df_all = compute_ratios(get_dataframe())
    if groupe and groupe != "tous":
        df_all = df_all[df_all["Goupe_Bancaire"] == groupe]

    if indic not in df_all.columns:
        return empty_fig()

    annees = sorted(df_all["ANNEE"].dropna().unique().tolist())
    meta   = RATIO_META.get(indic, {"label": indic, "ref": None})

    med_vals  = []
    q1_vals   = []
    q3_vals   = []

    for y in annees:
        d_y = df_all[df_all["ANNEE"] == y][indic].dropna()
        if len(d_y) == 0:
            continue
        med_vals.append((y, float(d_y.median())))
        q1_vals.append((y,  float(d_y.quantile(0.25))))
        q3_vals.append((y,  float(d_y.quantile(0.75))))

    if not med_vals:
        return empty_fig()

    xs   = [r[0] for r in med_vals]
    meds = [r[1] for r in med_vals]
    q1s  = [r[1] for r in q1_vals]
    q3s  = [r[1] for r in q3_vals]

    fig = go.Figure()

    # Intervalle Q1-Q3
    fig.add_trace(go.Scatter(
        x=xs + xs[::-1],
        y=q3s + q1s[::-1],
        fill="toself",
        fillcolor="rgba(240,180,41,0.08)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=True, name="Intervalle Q1–Q3",
        hoverinfo="skip",
    ))

    # Médiane
    fig.add_trace(go.Scatter(
        x=xs, y=meds,
        mode="lines+markers", name="Médiane",
        line=dict(color=T["accent"], width=2.5),
        marker=dict(size=8, color=T["accent"], line=dict(color=T["bg"], width=2)),
        hovertemplate="<b>%{x}</b><br>Médiane : %{y:.2f}%<extra></extra>",
    ))

    # Ligne de référence
    if meta.get("ref"):
        fig.add_hline(y=meta["ref"], line_dash="dot", line_color=T["blue"], line_width=1.5,
            annotation_text=f"Réf. {meta['ref']}%",
            annotation_font=dict(size=8, color=T["blue"], family=MONO),
            annotation_position="right")

    # Annotation COVID
    if 2020 in xs:
        y_covid = meds[xs.index(2020)]
        fig.add_annotation(x=2020, y=y_covid, text="COVID-19",
            showarrow=True, arrowhead=2, arrowcolor=T["red"],
            ax=30, ay=-25,
            font=dict(size=8, color=T["red"], family=MONO),
            bgcolor="rgba(248,81,73,0.10)",
            bordercolor=T["red"], borderwidth=1, borderpad=3)

    fig.update_layout(**plotly_base(
        yaxis_title=meta["label"], showlegend=True, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9, color=T["muted"]),
            bgcolor="rgba(0,0,0,0)"),
    ))
    return fig


# ── Tableau synthèse ──────────────────────────────────────────

@callback(
    Output("rat-table", "children"),
    Input("rat-dropdown-annee",  "value"),
    Input("rat-dropdown-groupe", "value"),
    Input("rat-table-sort",      "value"),
)
def cb_table(annee, groupe, sort_col):
    df = _get_df(annee, groupe)

    cols_show = ["Sigle", "Goupe_Bancaire", "ROA", "ROE", "MARGE_NETTE", "COUT_RISQUE_PCT"]
    avail = [c for c in cols_show if c in df.columns]
    d = df[avail].copy()

    if sort_col in d.columns:
        d = d.sort_values(sort_col, ascending=False, na_position="last")

    if d.empty:
        return html.Div("Aucune donnée", style={"color": T["muted"],
            "fontFamily": MONO, "fontSize": "12px"})

    # Header
    col_labels = {
        "Sigle": "BANQUE", "Goupe_Bancaire": "GROUPE",
        "ROA": "ROA %", "ROE": "ROE %",
        "MARGE_NETTE": "MARGE NETTE %", "COUT_RISQUE_PCT": "COÛT RISQUE %",
    }
    header = html.Div(
        [html.Div(col_labels.get(c, c), style={
            "flex": "2" if c in ("Sigle","Goupe_Bancaire") else "1",
            "color": T["muted"], "fontSize": "9px", "fontFamily": MONO,
            "letterSpacing": "1px", "fontWeight": "600",
            "color": T["accent"] if c == sort_col else T["muted"],
        }) for c in avail],
        style={"display": "flex", "gap": "8px", "padding": "8px 0",
               "borderBottom": f"1px solid {T['border']}", "marginBottom": "4px"},
    )

    def _cell_color(col, val):
        """Couleur conditionnelle selon seuil."""
        if val is None or np.isnan(val): return T["muted"]
        meta = RATIO_META.get(col)
        if not meta: return T["text"]
        ref  = meta["ref"]
        better = meta["higher_better"]
        if better:
            return T["green"] if val >= ref else (T["red"] if val < 0 else T["text"])
        else:
            return T["green"] if val <= ref else T["red"]

    rows = []
    for _, row in d.iterrows():
        grp_color = GROUPE_COLORS.get(row.get("Goupe_Bancaire",""), T["muted"])
        cells = []
        for c in avail:
            val = row.get(c)
            if c == "Sigle":
                cells.append(html.Div(str(val), style={"flex":"2","fontFamily":MONO,
                    "fontSize":"12px","color":T["text"],"fontWeight":"600"}))
            elif c == "Goupe_Bancaire":
                cells.append(html.Div(str(val).replace("Groupes ",""),
                    style={"flex":"2","fontFamily":MONO,"fontSize":"10px","color":grp_color}))
            else:
                fval = float(val) if val is not None and not (isinstance(val,float) and np.isnan(val)) else None
                color = _cell_color(c, fval)
                text  = f"{fval:.2f}%" if fval is not None else "—"
                cells.append(html.Div(text, style={"flex":"1","fontFamily":MONO,
                    "fontSize":"12px","color":color,"textAlign":"right"}))

        rows.append(html.Div(cells, style={"display":"flex","gap":"8px",
            "alignItems":"center","padding":"9px 0",
            "borderBottom":f"1px solid {T['border']}"}))

    return html.Div([header] + rows)
