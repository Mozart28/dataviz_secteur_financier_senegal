# ============================================================
#  data/loader.py — Chargement et normalisation des données
#  Source : MongoDB (priorité) ou Excel (fallback)
# ============================================================

import logging
import numpy as np
import pandas as pd
from functools import lru_cache

logger = logging.getLogger(__name__)

# Mapping complet underscore (MongoDB) → points (format interne)
UNDERSCORE_TO_DOT = {
    "FONDS_PROPRE":                     "FONDS.PROPRE",
    "INTERETS_ET_PRODUITS_ASSIMILES":   "INTERETS.ET.PRODUITS.ASSIMILES",
    "NTERETS_ET_CHARGES_ASSIMILEES":    "NTERETS.ET.CHARGES.ASSIMILEES",
    "REVENUS_DES_TITRES_A_REVENU_VARIABLE": "REVENUS.DES.TITRES.A.REVENU.VARIABLE",
    "PRODUIT_NET_BANCAIRE":             "PRODUIT.NET.BANCAIRE",
    "RESULTAT_NET":                     "RESULTAT.NET",
    "RESULTAT_AVANT_IMPOT":             "RESULTAT.AVANT.IMPOT",
    "RESULTAT_AVANT_IMPÔT":             "RESULTAT.AVANT.IMPÔT",
    "COÛT_DU_RISQUE":                   "COÛT.DU.RISQUE",
    "COUT_DU_RISQUE":                   "COÛT.DU.RISQUE",
    "IMPOTS_SUR_LES_BENEFICES":         "IMPÔTS.SUR.LES.BENEFICES",
    "IMPÔTS_SUR_LES_BENEFICES":         "IMPÔTS.SUR.LES.BENEFICES",
    "DOTATIONS_AUX_AMORTISSEMENTS_ET_AUX_DEPRECIATIONS_DES_IMMOBILISATIONS_INCORPORELLES_ET_CORPORELLES": "DOTATIONS.AUX.AMORTISSEMENTS",
    "GAINS_OU_PERTES_NETS_SUR_OPERATIONS_DES_PORTEFEUILLES_DE_NEGOCIATION":            "GAINS.PORTEFEUILLES.NEGOCIATION",
    "GAINS_OU_PERTES_NETS_SUR_OPERATIONS_DES_PORTEFEUILLES_DE_PLACEMENT_ET_ASSIMILES": "GAINS.PORTEFEUILLES.PLACEMENT",
    "GAINS_OU_PERTES_NETS_SUR_ACTIFS_IMMOBILISES": "GAINS.ACTIFS.IMMOBILISES",
    "CAISSE_BANQUE_CENTRALE_CCP":        "CAISSE.BANQUE.CENTRALE.CCP",
    "EFFETS_PUBLICS_ET_VALEURS_ASSIMILÉES": "EFFETS.PUBLICS.ET.VALEURS.ASSIMILÉES",
    "CRÉANCES_INTERBANCAIRES_ET_ASSIMILÉES": "CRÉANCES.INTERBANCAIRES.ET.ASSIMILÉES",
    "CRÉANCES_SUR_LA_CLIENTÈLE":         "CRÉANCES.SUR.LA.CLIENTÈLE",
    "OBLIGATIONS_ET_AUTRES_TITRES_À_REVENU_FIXE": "OBLIGATIONS.ET.AUTRES.TITRES.À.REVENU.FIXE",
    "ACTIONS_ET_AUTRES_TITRES_À_REVENU_VARIABLE":  "ACTIONS.ET.AUTRES.TITRES.À.REVENU.VARIABLE",
    "ACTIONNAIRES_OU_ASSOCIÉS":          "ACTIONNAIRES.OU.ASSOCIÉS",
    "AUTRES_ACTIFS":                     "AUTRES.ACTIFS",
    "COMPTES_DE_RÉGULARISATION":         "COMPTES.DE.RÉGULARISATION",
    "PARTICIPATIONS_ET_AUTRES_TITRES_DÉTENUS_À_LONG_TERME": "PARTICIPATIONS.ET.AUTRES.TITRES.DÉTENUS.À.LONG.TERME",
    "PARTS_DANS_LES_ENTREPRISES_LIÉES":  "PARTS.DANS.LES.ENTREPRISES.LIÉES",
    "PRÊTS_SUBORDONNÉS":                 "PRÊTS.SUBORDONNÉS",
    "IMMOBILISATIONS_INCORPORELLES":     "IMMOBILISATIONS.INCORPORELLES",
    "IMMOBILISATIONS_CORPORELLES":       "IMMOBILISATIONS.CORPORELLES",
    "BANQUE_CENTRALE_CCP":               "BANQUE.CENTRALE.CCP",
    "DETTES_INTERBANCAIRES_ET_ASSIMILÉES": "DETTES.INTERBANCAIRES.ET.ASSIMILÉES",
    "DETTES_À_L_ÉGARD_DE_LA_CLIENTÈLE":  "DETTES.À.L.ÉGARD.DE.LA.CLIENTÈLE",
    "DETTES_REPRÉSENTÉES_PAR_UN_TITRE":  "DETTES.REPRÉSENTÉES.PAR.UN.TITRE",
    "AUTRES_PASSIFS":                    "AUTRES.PASSIFS",
    "EMPRUNTS_ET_TITRES_ÉMIS_SUBORDONNES": "EMPRUNTS.ET.TITRES.ÉMIS.SUBORDONNES",
    "CAPITAUX_PROPRES_ET_RESSOURCES_ASSIMILÉES": "CAPITAUX.PROPRES.ET.RESSOURCES.ASSIMILÉES",
    "CAPITAL_SOUSCRIT":                  "CAPITAL.SOUSCRIT",
    "PRIMES_LIÉES_AU_CAPITAL":           "PRIMES.LIÉES.AU.CAPITAL",
    "RÉSERVES":                          "RÉSERVES",
    "ÉCARTS_DE_RÉÉVALUATION":            "ÉCARTS.DE.RÉÉVALUATION",
    "PROVISIONS_RÉGLEMENTÉES":           "PROVISIONS.RÉGLEMENTÉES",
    "REPORT_À_NOUVEAU":                  "REPORT.À.NOUVEAU",
    "RÉSULTAT_DE_LEXERCICE":             "RÉSULTAT.DE.LEXERCICE",
    # Apostrophes (MongoDB et Excel)
    "AUTRES_PRODUITS_D'EXPLOITATION_BANCAIRE": "AUTRES.PRODUITS.EXPLOITATION.BANCAIRE",
    "AUTRES_CHARGES_D'EXPLOITATION_BANCAIRE":  "AUTRES.CHARGES.EXPLOITATION.BANCAIRE",
    "CHARGES_GENERALES_D'EXPLOITATION":        "CHARGES.GENERALES.EXPLOITATION",
    "SUBVENTIONS_D'INVESTISSEMENT":            "SUBVENTIONS.INVESTISSEMENT",
    "RESULTAT_BRUT_D'EXPLOITATION":            "RESULTAT.BRUT.EXPLOITATION",
    "RESULTAT_D'EXPLOITATION":                 "RESULTAT.EXPLOITATION",
    "CHARGES.GENERALES.D'EXPLOITATION":        "CHARGES.GENERALES.EXPLOITATION",
    "AUTRES.PRODUITS.D'EXPLOITATION.BANCAIRE": "AUTRES.PRODUITS.EXPLOITATION.BANCAIRE",
    "AUTRES.CHARGES.D'EXPLOITATION.BANCAIRE":  "AUTRES.CHARGES.EXPLOITATION.BANCAIRE",
    "SUBVENTIONS.D'INVESTISSEMENT":            "SUBVENTIONS.INVESTISSEMENT",
    "RESULTAT.BRUT.D'EXPLOITATION":            "RESULTAT.BRUT.EXPLOITATION",
    "RESULTAT.D'EXPLOITATION":                 "RESULTAT.EXPLOITATION",
}

IDENTITY_COLS = {"Sigle", "Goupe_Bancaire", "ANNEE", "source"}


def _load_from_mongodb() -> pd.DataFrame | None:
    try:
        from pymongo import MongoClient
        from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.server_info()
        data = list(client[MONGO_DB][MONGO_COLLECTION].find({}, {"_id": 0}))
        client.close()
        if data:
            logger.info(f"MongoDB : {len(data)} enregistrements")
            return pd.DataFrame(data)
    except Exception as e:
        logger.warning(f"MongoDB indisponible : {e}")
    return None


def _load_from_excel(path: str) -> pd.DataFrame | None:
    import os
    if not os.path.exists(path):
        logger.error(f"Excel introuvable : {path}")
        return None
    logger.info(f"Excel : {path}")
    return pd.read_excel(path)


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().rename(columns=UNDERSCORE_TO_DOT)
    df["ANNEE"] = pd.to_numeric(df["ANNEE"], errors="coerce").astype("Int64")
    for col in df.columns:
        if col not in IDENTITY_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.drop_duplicates(subset=["Sigle", "ANNEE"], keep="last")
    return df.sort_values(["Sigle", "ANNEE"]).reset_index(drop=True)


@lru_cache(maxsize=1)
def get_dataframe() -> pd.DataFrame:
    """Point d'entrée unique — résultat mis en cache."""
    from config import EXCEL_FALLBACK
    df = _load_from_mongodb()
    if df is None or df.empty:
        df = _load_from_excel(EXCEL_FALLBACK)
    if df is None or df.empty:
        raise RuntimeError("Aucune source de données disponible.")
    result = _normalize(df)
    logger.info(f"Données prêtes : {len(result)} lignes")
    return result


def get_annees() -> list[int]:
    return sorted(get_dataframe()["ANNEE"].dropna().unique().tolist())


def agg(df: pd.DataFrame, *cols: str) -> float | None:
    """Somme la première colonne non-nulle parmi les candidats."""
    for c in cols:
        if c in df.columns and df[c].notna().any():
            v = df[c].sum()
            if v != 0:
                return float(v)
    return None


def best_col(df: pd.DataFrame) -> str | None:
    """Retourne la meilleure colonne indicateur disponible (PNB > Bilan)."""
    return next(
        (c for c in ["PRODUIT.NET.BANCAIRE", "BILAN"]
         if c in df.columns and df[c].notna().any() and df[c].sum() != 0),
        None,
    )


# ── Calcul des ratios financiers ──────────────────────────────

ACTIF_COLS = [
    "CAISSE.BANQUE.CENTRALE.CCP",
    "EFFETS.PUBLICS.ET.VALEURS.ASSIMILÉES",
    "CRÉANCES.INTERBANCAIRES.ET.ASSIMILÉES",
    "CRÉANCES.SUR.LA.CLIENTÈLE",
    "OBLIGATIONS.ET.AUTRES.TITRES.À.REVENU.FIXE",
    "ACTIONS.ET.AUTRES.TITRES.À.REVENU.VARIABLE",
    "AUTRES.ACTIFS",
    "COMPTES.DE.RÉGULARISATION",
    "PARTICIPATIONS.ET.AUTRES.TITRES.DÉTENUS.À.LONG.TERME",
    "PARTS.DANS.LES.ENTREPRISES.LIÉES",
    "PRÊTS.SUBORDONNÉS",
    "IMMOBILISATIONS.INCORPORELLES",
    "IMMOBILISATIONS.CORPORELLES",
]


def total_actif(row) -> float | None:
    """Calcule le total actif depuis les postes du bilan (quand BILAN est absent)."""
    import numpy as np
    # Priorité 1 : colonne BILAN directe
    if "BILAN" in row.index and pd.notna(row["BILAN"]) and row["BILAN"] != 0:
        return float(row["BILAN"])
    # Priorité 2 : somme des postes actif
    total = sum(
        float(row[c]) for c in ACTIF_COLS
        if c in row.index and pd.notna(row[c]) and row[c] != 0
    )
    return total if total > 0 else None


def compute_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute les colonnes de ratios calculés au DataFrame.
    Ratios ajoutés : ROA, ROE, COUT_RISQUE_PCT, MARGE_NETTE, TOTAL_ACTIF_CALC
    """
    import numpy as np

    df = df.copy()

    # Total actif calculé (fallback si BILAN absent)
    df["TOTAL_ACTIF"] = df.apply(total_actif, axis=1)

    # ROA = Résultat Net / Total Actif × 100
    df["ROA"] = np.where(
        df["TOTAL_ACTIF"].notna() & (df["TOTAL_ACTIF"] != 0) & df["RESULTAT.NET"].notna(),
        df["RESULTAT.NET"] / df["TOTAL_ACTIF"] * 100,
        np.nan,
    )

    # ROE = Résultat Net / Fonds Propres × 100
    fp_col = df["FONDS.PROPRE"].where(df["FONDS.PROPRE"].notna() & (df["FONDS.PROPRE"] != 0),
                                       df.get("CAPITAUX.PROPRES.ET.RESSOURCES.ASSIMILÉES"))
    df["ROE"] = np.where(
        fp_col.notna() & (fp_col != 0) & df["RESULTAT.NET"].notna(),
        df["RESULTAT.NET"] / fp_col * 100,
        np.nan,
    )

    # Coût du risque / RBE × 100
    rbe_col = df.get("RESULTAT.BRUT.EXPLOITATION", pd.Series(np.nan, index=df.index))
    risk_col = df.get("COÛT.DU.RISQUE", pd.Series(np.nan, index=df.index))
    df["COUT_RISQUE_PCT"] = np.where(
        rbe_col.notna() & (rbe_col != 0) & risk_col.notna(),
        risk_col.abs() / rbe_col.abs() * 100,
        np.nan,
    )

    # Marge nette = RN / RBE × 100
    df["MARGE_NETTE"] = np.where(
        rbe_col.notna() & (rbe_col != 0) & df["RESULTAT.NET"].notna(),
        df["RESULTAT.NET"] / rbe_col.abs() * 100,
        np.nan,
    )

    return df
