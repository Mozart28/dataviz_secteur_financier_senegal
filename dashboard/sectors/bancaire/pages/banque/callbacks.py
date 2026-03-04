# ============================================================
#  pages/banque/callbacks.py — Profil Banque avec export PDF
#  Export : graphiques capturés côté client → PDF reportlab
# ============================================================

import io
import base64
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, html, clientside_callback, ClientsideFunction

from config import T, MONO, SERIF, GROUPE_COLORS, plotly_base, empty_fig
from data import get_dataframe, agg, compute_ratios
from components.kpi_card import kpi_card, fmt

INDIC_COLS = {
    "bilan": ("BILAN",                "Total Bilan",  T["blue"]),
    "pnb":   ("PRODUIT.NET.BANCAIRE", "PNB",          T["accent"]),
    "rn":    ("RESULTAT.NET",         "Résultat Net", T["green"]),
    "fp":    ("FONDS.PROPRE",         "Fonds Propres","#A78BFA"),
    "ressources": ("RESSOURCES",       "Ressources",  "#FB923C"),
}

RADAR_AXES = [
    ("PRODUIT.NET.BANCAIRE", "PNB"),
    ("RESULTAT.NET",         "Résultat Net"),
    ("FONDS.PROPRE",         "Fonds Propres"),
    ("CAPITAUX.PROPRES.ET.RESSOURCES.ASSIMILÉES", "Capitaux Propres"),
    ("CRÉANCES.SUR.LA.CLIENTÈLE", "Créances clients"),
]


def _annees(df, banque):
    return sorted(df[df["Sigle"] == banque]["ANNEE"].dropna().unique().tolist())


def _safe_pct(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "—"
    return f"{val:.2f}%"


# ── Identité ──────────────────────────────────────────────────

@callback(Output("pb-identity-bar", "children"), Input("pb-dropdown-banque", "value"))
def cb_identity(banque):
    if not banque: return []
    df = get_dataframe()
    d  = df[df["Sigle"] == banque]
    if d.empty: return []

    groupe  = d["Goupe_Bancaire"].iloc[0]
    color   = GROUPE_COLORS.get(groupe, T["muted"])
    annees  = _annees(df, banque)
    periode = f"{min(annees)} – {max(annees)}" if annees else "—"

    def _item(label, value, val_color=None):
        return html.Div([
            html.Div(label, style={"color": T["muted"], "fontSize": "8px",
                "fontFamily": MONO, "letterSpacing": "1.5px", "marginBottom": "4px"}),
            html.Div(value, style={"color": val_color or T["text"],
                "fontSize": "12px", "fontFamily": MONO, "fontWeight": "600"}),
        ])

    return [
        html.Div(banque, style={"fontSize": "22px", "fontWeight": "700",
            "fontFamily": MONO, "color": T["text"]}),
        _item("GROUPE", groupe.replace("Groupes ", ""), color),
        _item("PÉRIODE", periode),
        _item("DONNÉES", f"{len(annees)} années"),
    ]


# ── KPI Cards ─────────────────────────────────────────────────

@callback(Output("pb-kpis", "children"), Input("pb-dropdown-banque", "value"))
def cb_kpis(banque):
    if not banque: return []
    df     = get_dataframe()
    annees = _annees(df, banque)
    if not annees: return []

    last   = max(annees)
    prev   = last - 1 if (last - 1) in annees else None
    d_cur  = df[(df["Sigle"] == banque) & (df["ANNEE"] == last)]
    d_prev = df[(df["Sigle"] == banque) & (df["ANNEE"] == prev)] if prev else None
    def p(*c): return agg(d_prev, *c) if d_prev is not None else None

    return [
        kpi_card("Total Bilan",         agg(d_cur, "BILAN"),                highlight=True, prev_value=p("BILAN")),
        kpi_card("Produit Net Bancaire", agg(d_cur, "PRODUIT.NET.BANCAIRE"), highlight=True, prev_value=p("PRODUIT.NET.BANCAIRE")),
        kpi_card("Résultat Net",         agg(d_cur, "RESULTAT.NET"),         highlight=True, prev_value=p("RESULTAT.NET")),
        kpi_card("Fonds Propres",        agg(d_cur, "FONDS.PROPRE",
            "CAPITAUX.PROPRES.ET.RESSOURCES.ASSIMILÉES"),                                    prev_value=p("FONDS.PROPRE")),
    ]


# ── Jauges ratios ─────────────────────────────────────────────

@callback(
    Output("pb-ratio-roa",   "children"),
    Output("pb-ratio-roe",   "children"),
    Output("pb-ratio-risk",  "children"),
    Output("pb-ratio-marge", "children"),
    Input("pb-dropdown-banque", "value"),
)
def cb_ratio_gauges(banque):
    if not banque: return "—", "—", "—", "—"
    df     = compute_ratios(get_dataframe())
    annees = _annees(df, banque)
    if not annees: return "—", "—", "—", "—"
    last = max(annees)
    row  = df[(df["Sigle"] == banque) & (df["ANNEE"] == last)]
    if row.empty: return "—", "—", "—", "—"
    r = row.iloc[0]
    return (
        _safe_pct(r.get("ROA")),
        _safe_pct(r.get("ROE")),
        _safe_pct(r.get("COUT_RISQUE_PCT")),
        _safe_pct(r.get("MARGE_NETTE")),
    )


# ── Évolution ratios ──────────────────────────────────────────

@callback(Output("pb-graph-ratios", "figure"), Input("pb-dropdown-banque", "value"))
def cb_graph_ratios(banque):
    if not banque: return empty_fig()
    df     = compute_ratios(get_dataframe())
    d_bank = df[df["Sigle"] == banque].sort_values("ANNEE")
    if d_bank.empty: return empty_fig()

    annees = d_bank["ANNEE"].tolist()
    fig    = go.Figure()

    for col, label, color in [
        ("ROA",        "ROA (%)",        T["accent"]),
        ("ROE",        "ROE (%)",        T["blue"]),
        ("MARGE_NETTE","Marge nette (%)",T["green"]),
    ]:
        if col in d_bank.columns and d_bank[col].notna().any():
            fig.add_trace(go.Scatter(
                x=annees, y=d_bank[col], name=label, mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(size=6, color=color, line=dict(color=T["bg"], width=1.5)),
                hovertemplate=f"{label} <b>%{{x}}</b> : %{{y:.2f}}%<extra></extra>",
            ))

    if "ROE" in d_bank.columns and d_bank["ROE"].notna().any():
        max_roe = d_bank["ROE"].max()
        max_yr  = int(d_bank.loc[d_bank["ROE"].idxmax(), "ANNEE"])
        fig.add_annotation(x=max_yr, y=max_roe, text=f"ROE max : {max_roe:.1f}%",
            showarrow=True, arrowhead=2, arrowcolor=T["blue"],
            ax=30, ay=-25, font=dict(size=8, color=T["blue"], family=MONO),
            bgcolor="rgba(88,166,255,0.12)", bordercolor=T["blue"], borderwidth=1, borderpad=3)

    fig.add_hline(y=1, line_dash="dot", line_color=T["muted"], line_width=1,
        annotation_text="ROA ref. 1%",
        annotation_font=dict(size=8, color=T["muted"], family=MONO),
        annotation_position="right")

    if not fig.data: return empty_fig("Ratios non calculables")

    fig.update_layout(**plotly_base(
        yaxis_title="(%)", showlegend=True, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9, color=T["muted"]),
            bgcolor="rgba(0,0,0,0)"),
    ))
    return fig


# ── Évolution KPIs ────────────────────────────────────────────

@callback(
    Output("pb-graph-evolution", "figure"),
    Input("pb-dropdown-banque",     "value"),
    Input("pb-dropdown-indicateur", "value"),
)
def cb_evolution(banque, indic):
    if not banque: return empty_fig()
    df     = get_dataframe()
    d_bank = df[df["Sigle"] == banque].sort_values("ANNEE")
    if d_bank.empty: return empty_fig()

    annees = d_bank["ANNEE"].tolist()
    fig    = go.Figure()

    def _add_line(col, label, color):
        if col not in d_bank.columns: return
        vals = d_bank[col] / 1000
        if vals.notna().any():
            fig.add_trace(go.Scatter(
                x=annees, y=vals, name=label, mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(size=7, color=color, line=dict(color=T["bg"], width=1.5)),
                hovertemplate=f"<b>{label}</b> %{{x}}<br>%{{y:,.1f}} Mds FCFA<extra></extra>",
            ))

    if indic == "all":
        _add_line("BILAN",                "Bilan",        T["blue"])
        _add_line("PRODUIT.NET.BANCAIRE", "PNB",          T["accent"])
        _add_line("RESULTAT.NET",         "Résultat Net", T["green"])
    else:
        col, label, color = INDIC_COLS[indic]
        _add_line(col, label, color)

    if not fig.data: return empty_fig("Données non disponibles")

    fig.update_layout(**plotly_base(
        yaxis_title="Milliards FCFA", showlegend=True, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=9, color=T["muted"]),
            bgcolor="rgba(0,0,0,0)"),
    ))
    return fig


# ── Part de marché ────────────────────────────────────────────

@callback(Output("pb-graph-pdm", "figure"), Input("pb-dropdown-banque", "value"))
def cb_pdm(banque):
    if not banque: return empty_fig()
    df  = get_dataframe()
    col = next((c for c in ["PRODUIT.NET.BANCAIRE","BILAN"]
                if c in df.columns and df[c].notna().any()), None)
    if not col: return empty_fig()

    annees   = sorted(df["ANNEE"].dropna().unique().tolist())
    pdm_vals = []
    for y in annees:
        d_y = df[df["ANNEE"] == y]
        tot = agg(d_y, col)
        d_b = d_y[d_y["Sigle"] == banque]
        v_b = agg(d_b, col)
        if tot and v_b:
            pdm_vals.append((int(y), v_b / tot * 100))

    if not pdm_vals: return empty_fig("Part de marché non disponible")
    xs  = [r[0] for r in pdm_vals]
    ys  = [r[1] for r in pdm_vals]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=xs, y=ys,
        marker=dict(
            color=[T["accent"] if i == len(xs)-1 else T["card2"] for i in range(len(xs))],
            line=dict(color=T["accent"], width=1),
        ),
        text=[f"{v:.1f}%" for v in ys], textposition="outside",
        textfont=dict(size=10, color=T["muted"], family=MONO),
        hovertemplate="<b>%{x}</b><br>Part de marché : %{y:.2f}%<extra></extra>",
    ))
    if len(xs) > 2:
        z   = np.polyfit(range(len(xs)), ys, 1)
        fit = np.poly1d(z)(range(len(xs)))
        fig.add_trace(go.Scatter(x=xs, y=list(fit), mode="lines",
            line=dict(color=T["blue"], width=1.5, dash="dot"),
            showlegend=False, hoverinfo="skip"))
        trend = "hausse" if z[0] > 0 else "baisse"
        fig.add_annotation(x=xs[-1], y=ys[-1], text=f"Tendance : {trend}",
            showarrow=False, yshift=18,
            font=dict(size=8, color=T["blue"], family=MONO))

    fig.update_layout(**plotly_base(
        yaxis_title="Part marché (%)", showlegend=False, bargap=0.35,
    ))
    return fig


# ── Radar ─────────────────────────────────────────────────────

@callback(
    Output("pb-graph-radar",      "figure"),
    Output("pb-radar-year-label", "children"),
    Input("pb-dropdown-banque",   "value"),
)
def cb_radar(banque):
    if not banque: return empty_fig(), ""
    df     = get_dataframe()
    annees = _annees(df, banque)
    if not annees: return empty_fig(), ""

    last   = max(annees)
    d_year = df[df["ANNEE"] == last]
    d_bank = d_year[d_year["Sigle"] == banque]
    nb     = d_year["Sigle"].nunique()

    axes, vals_b, vals_s = [], [], []
    for col, label in RADAR_AXES:
        if col not in df.columns: continue
        v_b = agg(d_bank, col)
        v_s = agg(d_year, col)
        if not v_b or not v_s: continue
        axes.append(label)
        vals_b.append(min(v_b / (v_s / nb) * 100, 300))
        vals_s.append(100)

    if len(axes) < 3: return empty_fig("Données insuffisantes"), ""

    axes   += [axes[0]];   vals_b += [vals_b[0]];   vals_s += [vals_s[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=vals_s, theta=axes, fill="toself",
        fillcolor="rgba(88,166,255,0.06)",
        line=dict(color=T["blue"], width=1.5, dash="dot"),
        name="Moyenne secteur"))
    fig.add_trace(go.Scatterpolar(r=vals_b, theta=axes, fill="toself",
        fillcolor="rgba(240,180,41,0.12)",
        line=dict(color=T["accent"], width=2),
        name=banque))

    base = {k: v for k, v in plotly_base().items() if k not in ("xaxis","yaxis")}
    base.update(
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,300],
                tickfont=dict(size=8, color=T["muted"]),
                gridcolor=T["border"], linecolor=T["border"]),
            angularaxis=dict(tickfont=dict(size=10, family=MONO, color=T["muted"]),
                gridcolor=T["border"], linecolor=T["border"])),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15,
            xanchor="center", x=0.5, font=dict(size=9, color=T["muted"]),
            bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=40, t=20, b=40),
    )
    fig.update_layout(**base)
    return fig, f"Référence : {last} · Base 100 = moyenne sectorielle"



# ── Export PDF (matplotlib, sans kaleido) ─────────────────────

@callback(
    Output("pb-download-pdf",  "data"),
    Output("pb-export-status", "children"),
    Input("pb-btn-export",     "n_clicks"),
    State("pb-dropdown-banque", "value"),
    prevent_initial_call=True,
)
def cb_export(n_clicks, banque):
    if not n_clicks or not banque:
        return None, ""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
        from matplotlib.patches import FancyBboxPatch
        import io as _io
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl_colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         Table, TableStyle, Image as RLImage,
                                         HRFlowable, KeepTogether)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        df     = compute_ratios(get_dataframe())
        d_bank = df[df["Sigle"] == banque].sort_values("ANNEE")
        annees = _annees(df, banque)
        if not annees:
            return None, "Aucune donnée disponible"
        last   = max(annees)
        groupe = d_bank["Goupe_Bancaire"].iloc[0] if not d_bank.empty else "—"
        row    = d_bank[d_bank["ANNEE"] == last].iloc[0] if not d_bank[d_bank["ANNEE"] == last].empty else None

        # ─ Palette ──────────────────────────────────────────
        BG     = "#0D1117"
        CARD   = "#161B22"
        GOLD   = "#F0B429"
        BLUE   = "#58A6FF"
        GREEN  = "#3FB950"
        RED    = "#F85149"
        TEXT   = "#E6EDF3"
        MUTED  = "#8B949E"
        BORDER = "#30363D"

        def _mpl_fig(w_cm=17, h_cm=7):
            fig = plt.figure(figsize=(w_cm/2.54, h_cm/2.54))
            fig.patch.set_facecolor(BG)
            return fig

        def _style_ax(ax):
            ax.set_facecolor(CARD)
            ax.tick_params(colors=MUTED, labelsize=7)
            ax.spines["bottom"].set_color(BORDER)
            ax.spines["left"].set_color(BORDER)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.yaxis.label.set_color(MUTED)
            ax.xaxis.label.set_color(MUTED)
            ax.title.set_color(GOLD)
            ax.grid(axis="y", color=BORDER, linewidth=0.5, linestyle="--", alpha=0.5)
            return ax

        def fig_to_rl(fig, w=17*cm, h=7*cm):
            buf = _io.BytesIO()
            fig.savefig(buf, format="png", dpi=180, bbox_inches="tight",
                        facecolor=BG)
            buf.seek(0)
            plt.close(fig)
            return RLImage(buf, width=w, height=h)

        # ─ Graphique 1 : Évolution PNB / RN / Bilan ─────────
        fig1 = _mpl_fig(17, 7)
        ax1  = fig1.add_subplot(111)
        _style_ax(ax1)
        colors_evol = {"PRODUIT.NET.BANCAIRE": GOLD,
                       "RESULTAT.NET": GREEN, "BILAN": BLUE}
        labels_evol = {"PRODUIT.NET.BANCAIRE": "PNB",
                       "RESULTAT.NET": "Résultat Net", "BILAN": "Bilan"}
        plotted = False
        for col, color in colors_evol.items():
            d_col = d_bank[["ANNEE", col]].dropna()
            if d_col.empty: continue
            xs = d_col["ANNEE"].astype(int).tolist()
            ys = (d_col[col] / 1000).tolist()
            ax1.plot(xs, ys, color=color, linewidth=2,
                     marker="o", markersize=5,
                     markerfacecolor=color, markeredgecolor=BG,
                     label=labels_evol[col])
            plotted = True
        if plotted:
            ax1.set_ylabel("Milliards FCFA", fontsize=8, color=MUTED)
            ax1.legend(fontsize=7, facecolor=CARD, edgecolor=BORDER,
                       labelcolor=TEXT, loc="upper left")
            ax1.set_title(f"Évolution temporelle · {banque}", fontsize=9,
                          color=GOLD, pad=8)
        img_evol = fig_to_rl(fig1, 17*cm, 7*cm)

        # ─ Graphique 2 : Part de marché ──────────────────────
        fig2 = _mpl_fig(8, 6)
        ax2  = fig2.add_subplot(111)
        _style_ax(ax2)
        col_pdm = "PRODUIT.NET.BANCAIRE" if "PRODUIT.NET.BANCAIRE" in df.columns else None
        pdm_xs, pdm_ys = [], []
        if col_pdm:
            for y in sorted(df["ANNEE"].dropna().unique()):
                d_y  = df[df["ANNEE"] == y]
                tot  = d_y[col_pdm].sum()
                d_b  = d_y[d_y["Sigle"] == banque]
                v_b  = d_b[col_pdm].sum()
                if tot > 0 and v_b > 0:
                    pdm_xs.append(int(y))
                    pdm_ys.append(v_b / tot * 100)
        if pdm_xs:
            bar_colors = [GOLD if x == last else BORDER for x in pdm_xs]
            bars = ax2.bar(pdm_xs, pdm_ys, color=bar_colors, width=0.6,
                           edgecolor="none")
            for b, v in zip(bars, pdm_ys):
                ax2.text(b.get_x()+b.get_width()/2, b.get_height()+0.05,
                         f"{v:.1f}%", ha="center", va="bottom",
                         fontsize=6, color=MUTED)
            ax2.set_ylabel("Part de marché (%)", fontsize=8, color=MUTED)
            ax2.set_title("Part de marché", fontsize=9, color=GOLD, pad=8)
        img_pdm = fig_to_rl(fig2, 8.2*cm, 6*cm)

        # ─ Graphique 3 : Radar vs secteur ────────────────────
        fig3 = _mpl_fig(8, 6)
        ax3  = fig3.add_subplot(111, polar=True)
        ax3.set_facecolor(CARD)
        fig3.patch.set_facecolor(BG)
        ax3.spines["polar"].set_color(BORDER)
        ax3.tick_params(colors=MUTED, labelsize=6)
        ax3.yaxis.grid(color=BORDER, linewidth=0.5)
        ax3.xaxis.grid(color=BORDER, linewidth=0.5)

        d_year = df[df["ANNEE"] == last]
        nb     = d_year["Sigle"].nunique()
        d_b    = d_year[d_year["Sigle"] == banque]
        r_labels, r_vals = [], []
        for col_r, lbl_r in [
            ("PRODUIT.NET.BANCAIRE","PNB"),
            ("RESULTAT.NET","RN"),
            ("FONDS.PROPRE","FP"),
            ("CAPITAUX.PROPRES.ET.RESSOURCES.ASSIMILÉES","Capitaux"),
            ("CRÉANCES.SUR.LA.CLIENTÈLE","Créances"),
        ]:
            if col_r not in df.columns: continue
            v_b = d_b[col_r].sum()
            v_s = d_year[col_r].sum()
            if v_b > 0 and v_s > 0 and nb > 0:
                r_labels.append(lbl_r)
                r_vals.append(min(v_b / (v_s / nb) * 100, 300))
        if len(r_labels) >= 3:
            N     = len(r_labels)
            theta = [n / float(N) * 2 * np.pi for n in range(N)]
            theta += theta[:1]
            r_vals_c = r_vals + r_vals[:1]
            sect_vals = [100] * N + [100]
            ax3.plot(theta, sect_vals, color=BLUE, linewidth=1.5,
                     linestyle="--", label="Secteur")
            ax3.fill(theta, sect_vals, color=BLUE, alpha=0.05)
            ax3.plot(theta, r_vals_c, color=GOLD, linewidth=2, label=banque)
            ax3.fill(theta, r_vals_c, color=GOLD, alpha=0.12)
            ax3.set_xticks(theta[:-1])
            ax3.set_xticklabels(r_labels, color=MUTED, fontsize=6)
            ax3.set_ylim(0, 300)
            ax3.set_yticks([100, 200, 300])
            ax3.set_yticklabels(["100%","200%","300%"], color=MUTED, fontsize=5)
            ax3.legend(fontsize=6, facecolor=CARD, edgecolor=BORDER,
                       labelcolor=TEXT, loc="upper right",
                       bbox_to_anchor=(1.3, 1.1))
            ax3.set_title("Radar vs secteur", fontsize=9, color=GOLD, pad=12)
        img_radar = fig_to_rl(fig3, 8.2*cm, 6*cm)

        # ─ Graphique 4 : Ratios ROA/ROE ──────────────────────
        fig4 = _mpl_fig(17, 6)
        ax4  = fig4.add_subplot(111)
        _style_ax(ax4)
        ratios_plot = [("ROA","ROA (%)",GOLD),
                       ("ROE","ROE (%)",BLUE),
                       ("MARGE_NETTE","Marge nette (%)",GREEN)]
        for col_r, lbl_r, c_r in ratios_plot:
            d_r = d_bank[["ANNEE", col_r]].dropna()
            if d_r.empty: continue
            xs = d_r["ANNEE"].astype(int).tolist()
            ys = d_r[col_r].tolist()
            ax4.plot(xs, ys, color=c_r, linewidth=2,
                     marker="o", markersize=5,
                     markerfacecolor=c_r, markeredgecolor=BG,
                     label=lbl_r)
        ax4.axhline(y=1, color=MUTED, linewidth=1, linestyle=":",
                    alpha=0.7, label="ROA réf. 1%")
        ax4.set_ylabel("(%)", fontsize=8, color=MUTED)
        ax4.set_title("Évolution des ratios ROA / ROE / Marge nette", fontsize=9,
                      color=GOLD, pad=8)
        ax4.legend(fontsize=7, facecolor=CARD, edgecolor=BORDER,
                   labelcolor=TEXT, loc="upper left")
        img_ratios = fig_to_rl(fig4, 17*cm, 6*cm)

        # ─ Assemblage PDF ────────────────────────────────────
        buf_pdf = _io.BytesIO()
        doc = SimpleDocTemplate(buf_pdf, pagesize=A4,
            leftMargin=1.8*cm, rightMargin=1.8*cm,
            topMargin=1.5*cm, bottomMargin=1.5*cm)

        DARK_RL   = rl_colors.HexColor("#0D1117")
        GOLD_RL   = rl_colors.HexColor("#F0B429")
        LIGHT_RL  = rl_colors.HexColor("#E6EDF3")
        MUTED_RL  = rl_colors.HexColor("#8B949E")
        GREEN_RL  = rl_colors.HexColor("#3FB950")
        RED_RL    = rl_colors.HexColor("#F85149")
        BORDER_RL = rl_colors.HexColor("#30363D")
        CARD_RL   = rl_colors.HexColor("#161B22")

        styles = getSampleStyleSheet()
        s_title = ParagraphStyle("T", parent=styles["Normal"],
            fontSize=26, textColor=LIGHT_RL, fontName="Helvetica-Bold",
            spaceAfter=4, leading=30)
        s_sub   = ParagraphStyle("S", parent=styles["Normal"],
            fontSize=10, textColor=MUTED_RL, fontName="Helvetica", spaceAfter=14)
        s_sec   = ParagraphStyle("SC", parent=styles["Normal"],
            fontSize=8, textColor=GOLD_RL, fontName="Helvetica-Bold",
            spaceBefore=16, spaceAfter=8, letterSpacing=2)
        s_label = ParagraphStyle("LB", parent=styles["Normal"],
            fontSize=8, textColor=MUTED_RL, fontName="Helvetica")
        s_val   = ParagraphStyle("VL", parent=styles["Normal"],
            fontSize=13, textColor=LIGHT_RL, fontName="Helvetica-Bold")

        def _tbl(data, col_widths):
            t = Table(data, colWidths=col_widths)
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,0),  CARD_RL),
                ("TEXTCOLOR",     (0,0),(-1,0),  GOLD_RL),
                ("FONTNAME",      (0,0),(-1,-1), "Helvetica"),
                ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
                ("FONTSIZE",      (0,0),(-1,-1), 8),
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [CARD_RL, DARK_RL]),
                ("TEXTCOLOR",     (0,1),(-1,-1), LIGHT_RL),
                ("GRID",          (0,0),(-1,-1), 0.3, BORDER_RL),
                ("TOPPADDING",    (0,0),(-1,-1), 5),
                ("BOTTOMPADDING", (0,0),(-1,-1), 5),
                ("LEFTPADDING",   (0,0),(-1,-1), 7),
                ("RIGHTPADDING",  (0,0),(-1,-1), 7),
            ]))
            return t

        elems = []

        # Page de garde
        elems.append(HRFlowable(width="100%", thickness=2, color=GOLD_RL))
        elems.append(Spacer(1, 0.5*cm))
        elems.append(Paragraph(banque, s_title))
        elems.append(Paragraph(
            f"{groupe.replace('Groupes ','')}  ·  Rapport de performance  ·  {last}",
            s_sub))
        elems.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_RL))
        elems.append(Spacer(1, 0.4*cm))

        # KPIs
        elems.append(Paragraph("INDICATEURS CLÉS", s_sec))
        kpi_rows = [["INDICATEUR", "VALEUR", "INDICATEUR", "VALEUR"]]
        kpis_left, kpis_right = [], []
        if row is not None:
            # Valeurs absolues
            for col_k, lbl_k in [
                ("PRODUIT.NET.BANCAIRE","PNB"),
                ("RESULTAT.NET","Résultat Net"),
                ("TOTAL_ACTIF","Total Actif"),
            ]:
                v = row.get(col_k, np.nan)
                if pd.notna(v) and float(v) != 0:
                    v_mds = f"{float(v)/1000:.1f} Mds"
                    kpis_left.append((lbl_k, v_mds, None))
            # Ratios
            for rk, rl, rb, rh in [
                ("ROA","ROA",1.0,True),("ROE","ROE",15.0,True),
                ("COUT_RISQUE_PCT","Coût risque",20.0,False),
                ("MARGE_NETTE","Marge nette",30.0,True),
            ]:
                v = row.get(rk, np.nan)
                if pd.notna(v):
                    good = (float(v) >= rb) if rh else (float(v) <= rb)
                    c_hex = "3FB950" if good else "F85149"
                    kpis_right.append((rl,
                        f'<font color="#{c_hex}">{float(v):.2f}%</font>',
                        c_hex))

        # Construire les lignes du tableau KPI
        max_r = max(len(kpis_left), len(kpis_right))
        for i in range(max_r):
            l_lbl = kpis_left[i][0]  if i < len(kpis_left)  else ""
            l_val = kpis_left[i][1]  if i < len(kpis_left)  else ""
            r_lbl = kpis_right[i][0] if i < len(kpis_right) else ""
            r_val = kpis_right[i][1] if i < len(kpis_right) else ""
            kpi_rows.append([
                Paragraph(l_lbl, s_label),
                Paragraph(l_val, s_val),
                Paragraph(r_lbl, s_label),
                Paragraph(r_val, s_val),
            ])
        if len(kpi_rows) > 1:
            elems.append(_tbl(kpi_rows, [4.5*cm, 4*cm, 4.5*cm, 4*cm]))

        elems.append(Spacer(1, 0.3*cm))

        # Graphiques
        elems.append(Paragraph("ÉVOLUTION TEMPORELLE", s_sec))
        elems.append(img_evol)

        elems.append(Paragraph("PART DE MARCHÉ  ·  RADAR VS SECTEUR", s_sec))
        elems.append(Table([[img_pdm, "", img_radar]],
            colWidths=[8.2*cm, 0.4*cm, 8.2*cm]))

        elems.append(Paragraph("RATIOS ROA / ROE / MARGE NETTE", s_sec))
        elems.append(img_ratios)

        # Tableau historique
        elems.append(Paragraph("DONNÉES HISTORIQUES", s_sec))
        hist_cols = [
            ("ANNEE","Année",2*cm),
            ("PRODUIT.NET.BANCAIRE","PNB (Mds)",2.8*cm),
            ("RESULTAT.NET","RN (Mds)",2.5*cm),
            ("TOTAL_ACTIF","Actif (Mds)",2.8*cm),
            ("ROA","ROA %",2*cm),
            ("ROE","ROE %",2*cm),
            ("MARGE_NETTE","Marge %",2.2*cm),
        ]
        avail = [(c,l,w) for c,l,w in hist_cols
                 if c in d_bank.columns or c == "ANNEE"]

        def _fv(r, col):
            if col == "ANNEE":
                return str(int(r["ANNEE"]))
            v = r.get(col, np.nan)
            if v is None or (isinstance(v, float) and np.isnan(v)):
                return "—"
            fv = float(v)
            if col in ("ROA","ROE","MARGE_NETTE","COUT_RISQUE_PCT"):
                return f"{fv:.2f}%"
            return f"{fv/1000:.1f}"

        hist_rows = [[l for _,l,_ in avail]]
        for _, r in d_bank.iterrows():
            hist_rows.append([_fv(r, c) for c,_,_ in avail])
        elems.append(_tbl(hist_rows, [w for _,_,w in avail]))

        # Pied de page
        elems.append(Spacer(1, 0.4*cm))
        elems.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_RL))
        elems.append(Spacer(1, 0.15*cm))
        elems.append(Paragraph(
            f"Rapport généré automatiquement · Dashboard Bancaire Sénégal · Données BCEAO {last}",
            ParagraphStyle("FT", parent=styles["Normal"], fontSize=7,
                textColor=MUTED_RL, fontName="Helvetica", alignment=1)))

        def _page_bg(canvas, _doc):
            canvas.saveState()
            canvas.setFillColor(DARK_RL)
            canvas.rect(0, 0, A4[0], A4[1], fill=True, stroke=False)
            canvas.restoreState()

        doc.build(elems, onFirstPage=_page_bg, onLaterPages=_page_bg)
        buf_pdf.seek(0)
        return dcc.send_bytes(buf_pdf.read(),
               filename=f"rapport_{banque}_{last}.pdf"),                f"✅ Rapport {banque} · {last} prêt"

    except ImportError as e:
        missing = str(e).split("'")[1] if "'" in str(e) else str(e)
        return None, f"⚠ Manquant : pip install {missing}"
    except Exception as e:
        import traceback as _tb
        full = _tb.format_exc()
        lines = [l for l in full.strip().splitlines() if l.strip()]
        last3 = " | ".join(lines[-4:])
        return None, f"Erreur : {last3[:400]}"

import pandas as pd
