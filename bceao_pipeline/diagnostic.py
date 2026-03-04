"""
diagnostic.py — Inspecter la structure réelle du PDF BCEAO
Lancer avec : python3 bceao_pipeline/diagnostic.py
"""
import pdfplumber

PDF_PATH = "data/raw_pdfs/bceao_bilans_2022.pdf"

# Pages réelles de la section Sénégal : 266-319
# On inspecte les 8 premières pages (= ~4 premières banques, 2 pages chacune)
PAGES_TO_INSPECT = list(range(266, 274))


def inspect_page(page, page_num):
    print(f"\n{'='*70}")
    print(f"  PAGE {page_num}")
    print('='*70)

    # Texte brut complet
    text = page.extract_text() or ""
    print("── TEXTE BRUT ──")
    print(text[:1500])

    # Tous les tableaux
    tables = page.extract_tables()
    print(f"\n── TABLEAUX TROUVÉS : {len(tables)} ──")
    for t_idx, table in enumerate(tables):
        print(f"\n  [Tableau {t_idx+1}] — {len(table)} lignes × {len(table[0]) if table else 0} colonnes")
        for r_idx, row in enumerate(table):
            print(f"    [{r_idx:02d}] {row}")
            if r_idx > 30:
                print(f"    ... ({len(table) - 30} lignes supplémentaires)")
                break


with pdfplumber.open(PDF_PATH) as pdf:
    total = len(pdf.pages)
    print(f"PDF : {total} pages au total")
    print(f"Inspection des pages {PAGES_TO_INSPECT[0]} à {PAGES_TO_INSPECT[-1]}")

    for page_num in PAGES_TO_INSPECT:
        if page_num <= total:
            page = pdf.pages[page_num - 1]  # pdfplumber est 0-indexé
            inspect_page(page, page_num)
