# ============================================================
#  downloader.py — Téléchargement des PDFs BCEAO
# ============================================================

import os
import time
import logging
import requests
from pathlib import Path
from config import PDF_URLS, PDF_DIR, LOGS_DIR

# --- Logging ---
Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{LOGS_DIR}/pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def download_pdf(year: int, url: str, output_dir: str) -> str | None:
    """
    Télécharge un PDF BCEAO pour une année donnée.
    Retourne le chemin local du fichier, ou None en cas d'échec.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = os.path.join(output_dir, f"bceao_bilans_{year}.pdf")

    # Ne re-télécharge pas si le fichier existe déjà
    if os.path.exists(output_path):
        logger.info(f"[{year}] PDF déjà présent : {output_path}")
        return output_path

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/pdf,*/*",
        "Referer": "https://www.bceao.int/",
    }

    try:
        logger.info(f"[{year}] Téléchargement depuis : {url}")
        response = requests.get(url, headers=headers, timeout=120, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

        size_mb = downloaded / (1024 * 1024)
        logger.info(f"[{year}] ✅ Téléchargé : {output_path} ({size_mb:.1f} Mo)")
        time.sleep(2)  # Respecter le serveur BCEAO
        return output_path

    except requests.exceptions.RequestException as e:
        logger.error(f"[{year}] ❌ Erreur téléchargement : {e}")
        return None


def download_all_pdfs() -> dict[int, str]:
    """
    Télécharge tous les PDFs configurés.
    Retourne un dict {année: chemin_local}.
    """
    results = {}
    for year, url in PDF_URLS.items():
        path = download_pdf(year, url, PDF_DIR)
        if path:
            results[year] = path
    logger.info(f"Téléchargements terminés : {len(results)}/{len(PDF_URLS)} réussis")
    return results


if __name__ == "__main__":
    download_all_pdfs()
