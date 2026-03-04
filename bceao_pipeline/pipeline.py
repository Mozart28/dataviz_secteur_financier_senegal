# ============================================================
#  pipeline.py — Orchestrateur principal du pipeline
# ============================================================
"""
Usage :
    python pipeline.py                     # Pipeline complet
    python pipeline.py --step download     # Téléchargement seul
    python pipeline.py --step extract      # Extraction seul (PDFs déjà téléchargés)
    python pipeline.py --step load         # Chargement MongoDB seul (CSV déjà généré)
    python pipeline.py --excel-only        # Charger uniquement le fichier Excel dans MongoDB
    python pipeline.py --year 2021         # Traiter une seule année
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from config import PDF_DIR, PROCESSED_DIR, LOGS_DIR
from downloader import download_all_pdfs
from extractor import extract_senegal_data
from cleaner import merge_all_data, save_processed_data, generate_quality_report
from mongo_loader import df_to_mongo

# --- Logging ---
Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{LOGS_DIR}/pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Chemin vers le fichier Excel de base
EXCEL_PATH = "data/BASE_SENEGAL2.xlsx"


def run_download() -> str | None:
    """
    Étape 1 : Télécharger le PDF BCEAO 2022.
    Retourne le chemin local du PDF.
    """
    logger.info("=" * 50)
    logger.info("ÉTAPE 1 : TÉLÉCHARGEMENT DU PDF BCEAO 2022")
    logger.info("=" * 50)

    pdf_paths = download_all_pdfs()
    if not pdf_paths:
        logger.error("Aucun PDF téléchargé !")
        return None

    pdf_path = pdf_paths[2022]
    logger.info(f"PDF disponible : {pdf_path}")
    return pdf_path


def run_extract(pdf_path: str) -> dict[int, list]:
    """
    Étape 2 : Extraire 2021 ET 2022 depuis le seul PDF 2022.
    Le fascicule BCEAO 2022 présente les 3 années en colonnes.
    Retourne {2021: [...], 2022: [...]}
    """
    logger.info("=" * 50)
    logger.info("ÉTAPE 2 : EXTRACTION 2021 & 2022 DEPUIS LE PDF 2022")
    logger.info("=" * 50)

    if not pdf_path or not Path(pdf_path).exists():
        logger.error(f"PDF introuvable : {pdf_path}")
        return {}

    all_records = extract_senegal_data(pdf_path)

    # Grouper par année
    scraped_data = {}
    for record in all_records:
        year = record.get("ANNEE")
        if year:
            scraped_data.setdefault(year, []).append(record)

    for year, records in scraped_data.items():
        logger.info(f"[{year}] {len(records)} banques extraites")

    return scraped_data


def run_merge_and_clean(scraped_data: dict[int, list]) -> "pd.DataFrame":
    """Étape 3 : Fusionner et nettoyer."""
    logger.info("=" * 50)
    logger.info("ÉTAPE 3 : FUSION ET NETTOYAGE")
    logger.info("=" * 50)

    df = merge_all_data(EXCEL_PATH, scraped_data)

    # Rapport qualité
    report = generate_quality_report(df)
    logger.info(f"Rapport qualité :")
    logger.info(f"  Total enregistrements : {report['total_records']}")
    logger.info(f"  Banques : {len(report['banques'])}")
    logger.info(f"  Années : {report['annees']}")

    if report["banques_avec_donnees_manquantes"]:
        logger.warning("Banques avec données manquantes (>30%) :")
        for banque, pct in report["banques_avec_donnees_manquantes"].items():
            logger.warning(f"  {banque}: {pct}% manquant")

    # Sauvegarder localement
    csv_path, xlsx_path = save_processed_data(df)

    # Sauvegarder le rapport qualité
    Path(PROCESSED_DIR).mkdir(parents=True, exist_ok=True)
    with open(f"{PROCESSED_DIR}/quality_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return df


def run_load_mongo(df) -> dict:
    """Étape 4 : Charger dans MongoDB."""
    logger.info("=" * 50)
    logger.info("ÉTAPE 4 : CHARGEMENT DANS MONGODB")
    logger.info("=" * 50)

    stats = df_to_mongo(df, replace=False)
    return stats


def run_full_pipeline():
    """Lance le pipeline complet."""
    logger.info("🚀 DÉMARRAGE DU PIPELINE BCEAO")
    logger.info("Source   : PDF BCEAO 2022 (contient les années 2020, 2021, 2022)")
    logger.info("Objectif : extraire 2021 & 2022 → fusionner avec Excel 2015-2020")

    try:
        # Étape 1 : Téléchargement du seul PDF 2022
        pdf_path = run_download()
        if not pdf_path:
            sys.exit(1)

        # Étape 2 : Extraction de 2021 ET 2022 depuis ce PDF
        scraped_data = run_extract(pdf_path)

        # Étape 3 : Fusion avec l'Excel 2015-2020 + nettoyage
        df = run_merge_and_clean(scraped_data)

        # Étape 4 : Chargement dans MongoDB
        stats = run_load_mongo(df)

        logger.info("=" * 50)
        logger.info("✅ PIPELINE TERMINÉ AVEC SUCCÈS")
        logger.info(f"   Résumé MongoDB : {stats}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"❌ ERREUR PIPELINE : {e}", exc_info=True)
        sys.exit(1)


def run_excel_only():
    """Charge uniquement le fichier Excel dans MongoDB (sans PDF)."""
    from cleaner import load_excel_data
    logger.info("Chargement Excel uniquement vers MongoDB")
    df = load_excel_data(EXCEL_PATH)
    stats = df_to_mongo(df, replace=False)
    logger.info(f"✅ Excel chargé : {stats}")
    return df


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline d'extraction BCEAO")
    parser.add_argument("--step", choices=["download", "extract", "load", "all"],
                        default="all", help="Étape à exécuter")
    parser.add_argument("--excel-only", action="store_true",
                        help="Charger uniquement le fichier Excel dans MongoDB")
    args = parser.parse_args()

    if args.excel_only:
        run_excel_only()
    elif args.step == "all":
        run_full_pipeline()
    elif args.step == "download":
        run_download()
    elif args.step == "extract":
        import os
        pdf_path = os.path.join(PDF_DIR, "bceao_bilans_2022.pdf")
        run_extract(pdf_path)
    elif args.step == "load":
        import pandas as pd
        csv_path = f"{PROCESSED_DIR}/data_bancaire_senegal_2015_2022.csv"
        df = pd.read_csv(csv_path)
        run_load_mongo(df)
