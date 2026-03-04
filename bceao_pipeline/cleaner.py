# ============================================================
#  cleaner.py — Nettoyage et fusion des données (v2 FINAL)
#  Conserve TOUTES les colonnes PDF sans filtrage
# ============================================================

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from config import PROCESSED_DIR

logger = logging.getLogger(__name__)


def load_excel_data(excel_path: str) -> pd.DataFrame:
    logger.info(f"Chargement du fichier Excel : {excel_path}")
    df = pd.read_excel(excel_path, sheet_name="Sheet 1")
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        if col not in ["Sigle", "Goupe_Bancaire", "ANNEE"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["source"] = "excel_2015_2020"
    logger.info(f"Excel chargé : {len(df)} lignes, années {sorted(df['ANNEE'].dropna().unique().tolist())}")
    return df


def clean_scraped_data(records: list[dict], year: int) -> pd.DataFrame:
    """
    Conserve TOUS les champs extraits du PDF — pas de filtrage sur COLONNES_EXCEL.
    MongoDB est schemaless : chaque document peut avoir ses propres champs.
    Les nouvelles colonnes Bilan (CAISSE.BANQUE.CENTRALE.CCP, etc.) sont conservées.
    """
    if not records:
        logger.warning(f"[{year}] Aucune donnée à nettoyer")
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Convertir toutes les colonnes numériques (sans filtrer)
    skip_cols = {"Sigle", "Goupe_Bancaire", "ANNEE", "source"}
    for col in df.columns:
        if col not in skip_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["source"] = f"bceao_pdf_{year}"
    logger.info(f"[{year}] Nettoyage terminé : {len(df)} banques, {len(df.columns) - 4} KPIs")
    return df


def merge_all_data(excel_path: str, scraped_data: dict[int, list[dict]]) -> pd.DataFrame:
    """
    Fusionne Excel (2015-2020) avec PDF (2021-2022).
    pd.concat aligne automatiquement par nom de colonne — NaN si absent dans une source.
    Résultat : toutes les colonnes des deux sources sont présentes.
    """
    logger.info("=== Fusion des données ===")

    df_excel = load_excel_data(excel_path)

    dfs_scraped = []
    for year, records in scraped_data.items():
        df_year = clean_scraped_data(records, year)
        if not df_year.empty:
            dfs_scraped.append(df_year)

    if not dfs_scraped:
        logger.warning("Aucune donnée PDF, retour des données Excel uniquement")
        return df_excel

    df_scraped = pd.concat(dfs_scraped, ignore_index=True)
    df_merged  = pd.concat([df_excel, df_scraped], ignore_index=True)

    # Dédupliquer (priorité PDF si doublon Sigle+ANNEE)
    df_merged = df_merged.sort_values("source").drop_duplicates(
        subset=["Sigle", "ANNEE"], keep="last"
    )
    df_merged = df_merged.sort_values(["Sigle", "ANNEE"]).reset_index(drop=True)

    logger.info(f"Fusion terminée : {len(df_merged)} lignes, {len(df_merged.columns)} colonnes")
    logger.info(f"  dont {len(df_excel.columns)} colonnes Excel + {len(df_merged.columns) - len(df_excel.columns)} nouvelles colonnes PDF")
    logger.info(f"Années : {sorted(df_merged['ANNEE'].dropna().unique().tolist())}")
    logger.info(f"Banques : {sorted(df_merged['Sigle'].unique().tolist())}")

    return df_merged


def generate_quality_report(df: pd.DataFrame) -> dict:
    numeric_cols = [c for c in df.columns if c not in ["Sigle", "Goupe_Bancaire", "ANNEE", "source"]]
    report = {
        "total_records": len(df),
        "banques": sorted(df["Sigle"].unique().tolist()),
        "annees": sorted(df["ANNEE"].dropna().unique().tolist()),
        "completude_par_colonne": {},
        "banques_avec_donnees_manquantes": {},
    }
    for col in numeric_cols:
        pct_filled = df[col].notna().mean() * 100
        report["completude_par_colonne"][col] = round(pct_filled, 1)
    for banque in df["Sigle"].unique():
        df_banque = df[df["Sigle"] == banque][numeric_cols]
        missing_pct = df_banque.isna().mean().mean() * 100
        if missing_pct > 30:
            report["banques_avec_donnees_manquantes"][banque] = round(missing_pct, 1)
    return report


def save_processed_data(df: pd.DataFrame, filename: str = "data_bancaire_senegal_2015_2022.csv"):
    Path(PROCESSED_DIR).mkdir(parents=True, exist_ok=True)
    csv_path  = f"{PROCESSED_DIR}/{filename}"
    xlsx_path = f"{PROCESSED_DIR}/{filename.replace('.csv', '.xlsx')}"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False, sheet_name="Données Bancaires")
    logger.info(f"Données sauvegardées : {csv_path}")
    logger.info(f"Données sauvegardées : {xlsx_path}")
    return csv_path, xlsx_path
