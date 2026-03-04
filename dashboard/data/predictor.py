# ============================================================
#  data/predictor.py — Module prédictif N+1 à N+3
#  Méthode : régression linéaire + CAGR + intervalles confiance
# ============================================================

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


COLS_PRED = {
    "PRODUIT.NET.BANCAIRE": "PNB",
    "RESULTAT.NET":         "Résultat Net",
}

# Scénarios : multiplicateur appliqué à la pente de tendance
SCENARIOS = {
    "pessimiste": {"mult": 0.6,  "label": "Pessimiste",  "color": "#F85149"},
    "central":    {"mult": 1.0,  "label": "Central",     "color": "#F0B429"},
    "optimiste":  {"mult": 1.4,  "label": "Optimiste",   "color": "#3FB950"},
}


def _fit_series(years: list, values: list):
    """
    Ajuste une régression linéaire sur la série.
    Retourne (intercept, slope, r2, residual_std).
    """
    if len(years) < 2:
        return None
    X = np.array(years).reshape(-1, 1)
    y = np.array(values, dtype=float)
    lr = LinearRegression().fit(X, y)
    y_pred = lr.predict(X)
    residuals = y - y_pred
    r2  = lr.score(X, y)
    std = float(np.std(residuals, ddof=1)) if len(residuals) > 1 else 0.0
    return {
        "intercept": float(lr.intercept_),
        "slope":     float(lr.coef_[0]),
        "r2":        r2,
        "std":       std,
        "last_val":  float(y[-1]),
        "last_year": int(years[-1]),
        "n_points":  len(years),
    }


def predict_banque(df: pd.DataFrame, banque: str, horizon: int = 3) -> dict:
    """
    Prédit PNB, RN, part de marché et rang pour une banque
    sur horizon années (N+1 à N+horizon).

    Retourne un dict avec clés : years_future, predictions, metadata.
    """
    d_bank = df[df["Sigle"] == banque].sort_values("ANNEE")
    last_year = int(df["ANNEE"].max())
    future_years = list(range(last_year + 1, last_year + horizon + 1))

    results = {}

    for col, label in COLS_PRED.items():
        d_col = d_bank[["ANNEE", col]].dropna()
        if len(d_col) < 2:
            results[col] = None
            continue

        years  = d_col["ANNEE"].astype(int).tolist()
        values = d_col[col].tolist()
        fit    = _fit_series(years, values)
        if not fit:
            results[col] = None
            continue

        # Projections par scénario
        scen_preds = {}
        for scen_key, scen_cfg in SCENARIOS.items():
            preds = []
            for yr in future_years:
                base = fit["intercept"] + fit["slope"] * yr
                # Scénario = on modifie la pente (écart depuis dernière valeur)
                delta = (base - fit["last_val"]) * scen_cfg["mult"]
                val   = max(0, fit["last_val"] + delta)
                preds.append(round(val, 1))
            scen_preds[scen_key] = preds

        # Intervalle de confiance 80% autour du central
        ci_width = fit["std"] * 1.28  # z=1.28 → 80%
        ci_lower = [max(0, v - ci_width * (i+1)**0.5)
                    for i, v in enumerate(scen_preds["central"])]
        ci_upper = [v + ci_width * (i+1)**0.5
                    for i, v in enumerate(scen_preds["central"])]

        results[col] = {
            "label":       label,
            "fit":         fit,
            "scenarios":   scen_preds,
            "ci_lower":    ci_lower,
            "ci_upper":    ci_upper,
            "hist_years":  years,
            "hist_values": values,
        }

    # ── Part de marché et rang ────────────────────────────────
    pnb_col = "PRODUIT.NET.BANCAIRE"
    pdm_results = None
    rang_results = None

    if pnb_col in df.columns:
        # Part de marché historique par année
        pdm_hist = {}
        for yr in sorted(df["ANNEE"].dropna().unique()):
            d_yr  = df[df["ANNEE"] == yr]
            tot   = d_yr[pnb_col].sum()
            v_b   = d_yr[d_yr["Sigle"] == banque][pnb_col].sum()
            if tot > 0 and v_b > 0:
                pdm_hist[int(yr)] = v_b / tot * 100

        if len(pdm_hist) >= 2:
            pdm_years  = list(pdm_hist.keys())
            pdm_values = list(pdm_hist.values())
            fit_pdm = _fit_series(pdm_years, pdm_values)

            if fit_pdm:
                scen_pdm = {}
                for scen_key, scen_cfg in SCENARIOS.items():
                    preds = []
                    for yr in future_years:
                        base  = fit_pdm["intercept"] + fit_pdm["slope"] * yr
                        delta = (base - fit_pdm["last_val"]) * scen_cfg["mult"]
                        val   = max(0, min(100, fit_pdm["last_val"] + delta))
                        preds.append(round(val, 2))
                    scen_pdm[scen_key] = preds

                pdm_results = {
                    "fit":         fit_pdm,
                    "scenarios":   scen_pdm,
                    "hist_years":  pdm_years,
                    "hist_values": pdm_values,
                }

        # Rang historique et prédit
        rang_hist = {}
        for yr in sorted(df["ANNEE"].dropna().unique()):
            d_yr   = df[df["ANNEE"] == yr]
            ranked = d_yr.groupby("Sigle")[pnb_col].sum().sort_values(ascending=False)
            if banque in ranked.index:
                rang_hist[int(yr)] = int(ranked.index.get_loc(banque)) + 1

        # Projeter rang via PNB prédit
        if results.get(pnb_col) and rang_hist:
            rang_scen = {}
            for scen_key, scen_cfg in SCENARIOS.items():
                pnb_futurs = results[pnb_col]["scenarios"][scen_key]
                rangs = []
                d_last = df[df["ANNEE"] == last_year]
                other_pnb = d_last[d_last["Sigle"] != banque]\
                                .groupby("Sigle")[pnb_col].sum().sort_values(ascending=False)
                for pnb_f in pnb_futurs:
                    # Estimer: combien de banques ont un PNB > pnb_f ?
                    rang_est = int((other_pnb > pnb_f).sum()) + 1
                    rangs.append(rang_est)
                rang_scen[scen_key] = rangs

            rang_results = {
                "hist_years":  list(rang_hist.keys()),
                "hist_values": list(rang_hist.values()),
                "scenarios":   rang_scen,
            }

    return {
        "banque":       banque,
        "future_years": future_years,
        "last_year":    last_year,
        "pnb":          results.get("PRODUIT.NET.BANCAIRE"),
        "rn":           results.get("RESULTAT.NET"),
        "pdm":          pdm_results,
        "rang":         rang_results,
    }
