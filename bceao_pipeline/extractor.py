# ============================================================
#  extractor.py — Extraction complète PDF BCEAO (v9)
#  Noms de colonnes alignés EXACTEMENT avec l'Excel
#  49 KPIs par banque : 29 Bilan + 20 Résultat
#  + Mapping automatique PDF → noms Excel dashboard
#    (EMPLOI, BILAN, RESSOURCES, FONDS.PROPRE)
#  v9 : BILAN reconstruit par somme postes actif
#       RESSOURCES : double variante accent
#       FONDS.PROPRE 2020 : fallback CAPITAUX.PROPRES
# ============================================================
import re, math, logging
import pdfplumber

logger = logging.getLogger(__name__)

SENEGAL_PAGES_START = 266
SENEGAL_PAGES_END   = 319
YEARS_TO_EXTRACT    = [2021, 2022]

SIGLE_PDF_TO_EXCEL = {
    "SGSN":"SGBS","SGBS":"SGBS","BICIS":"BICIS","CBAO":"CBAO",
    "CDS":"CDS","ECOBANK":"ECOBANK","BOA":"BOA","UBA":"UBA",
    "CITIBANK":"CITIBANK","ORABANK":"ORABANK","BAS":"BAS","BGFI":"BGFI",
    "BDK":"BDK","BHS":"BHS","BIS":"BIS","BNDE":"BNDE","BRM":"BRM",
    "BSIC":"BSIC","BCIM":"BCIM","CBI":"CBI","FBNBANK":"FBNBANK",
    "LBA":"LBA","LBO":"LBO","NSIA":"NSIA Banque",
}

GROUPES = {
    "SGBS":"Groupes Internationaux","BICIS":"Groupes Internationaux","CISA":"Groupes Internationaux",
    "BAS":"Groupes Continentaux","BOA":"Groupes Continentaux","CBAO":"Groupes Continentaux",
    "CITIBANK":"Groupes Continentaux","ECOBANK":"Groupes Continentaux",
    "FBNBANK":"Groupes Continentaux","ORABANK":"Groupes Continentaux","UBA":"Groupes Continentaux",
    "BCIM":"Groupes Règionaux","BDK":"Groupes Règionaux","BGFI":"Groupes Règionaux",
    "BIS":"Groupes Règionaux","BRM":"Groupes Règionaux","BSIC":"Groupes Règionaux",
    "CBI":"Groupes Règionaux","CDS":"Groupes Règionaux","NSIA Banque":"Groupes Règionaux",
    "BHS":"Groupes Locaux","BNDE":"Groupes Locaux","LBA":"Groupes Locaux","LBO":"Groupes Locaux",
}

# ── Séquence Résultat avec noms EXACTEMENT identiques à l'Excel ──
SEQUENCE_RESULTAT = [
    "INTERETS.ET.PRODUITS.ASSIMILES",
    "NTERETS.ET.CHARGES.ASSIMILEES",
    "REVENUS.DES.TITRES.A.REVENU.VARIABLE",
    "COMMISSIONS.(PRODUITS)",
    "COMMISSIONS.(CHARGES)",
    "GAINS.OU.PERTES.NETS.SUR.OPERATIONS.DES.PORTEFEUILLES.DE.NEGOCIATION",
    "GAINS.OU.PERTES.NETS.SUR.OPERATIONS.DES.PORTEFEUILLES.DE.PLACEMENT.ET.ASSIMILES",
    "AUTRES.PRODUITS.D'EXPLOITATION.BANCAIRE",
    "AUTRES.CHARGES.D'EXPLOITATION.BANCAIRE",
    "PRODUIT.NET.BANCAIRE",
    "SUBVENTIONS.D'INVESTISSEMENT",
    "CHARGES.GENERALES.D'EXPLOITATION",
    "DOTATIONS.AUX.AMORTISSEMENTS.ET.AUX.DEPRECIATIONS.DES.IMMOBILISATIONS.INCORPORELLES.ET.CORPORELLES",
    "RESULTAT.BRUT.D'EXPLOITATION",
    "COÛT.DU.RISQUE",
    "RESULTAT.D'EXPLOITATION",
    "GAINS.OU.PERTES.NETS.SUR.ACTIFS.IMMOBILISES",
    "RESULTAT.AVANT.IMPÔT",
    "IMPÔTS.SUR.LES.BENEFICES",
    "RESULTAT.NET",
]

# ── Mapping colonnes PDF → noms Excel du dashboard ───────────
PDF_TO_EXCEL_COLS = {
    "CRÉANCES.SUR.LA.CLIENTÈLE":                  "EMPLOI",
    "TOTAL.DE.LACTIF":                            "BILAN",       # présent dans certaines pages
    "DETTES.À.L.ÉGARD.DE.LA.CLIENTÈLE":          "RESSOURCES",  # variante espace après L
    "DETTES.À.LÉGARD.DE.LA.CLIENTÈLE":           "RESSOURCES",  # variante sans espace
    "CAPITAUX.PROPRES.ET.RESSOURCES.ASSIMILÉES":  "FONDS.PROPRE",
}

# Postes actif pour reconstruire BILAN quand TOTAL.DE.LACTIF est absent
ACTIF_COLS = [
    "CAISSE.BANQUE.CENTRALE.CCP",
    "EFFETS.PUBLICS.ET.VALEURS.ASSIMILÉES",
    "CRÉANCES.INTERBANCAIRES.ET.ASSIMILÉES",
    "CRÉANCES.SUR.LA.CLIENTÈLE",
    "OBLIGATIONS.ET.AUTRES.TITRES.À.REVENU.FIXE",
    "ACTIONS.ET.AUTRES.TITRES.À.REVENU.VARIABLE",
    "ACTIONNAIRES.OU.ASSOCIÉS",
    "AUTRES.ACTIFS",
    "COMPTES.DE.RÉGULARISATION",
    "PARTICIPATIONS.ET.AUTRES.TITRES.DÉTENUS.À.LONG.TERME",
    "PARTS.DANS.LES.ENTREPRISES.LIÉES",
    "PRÊTS.SUBORDONNÉS",
    "IMMOBILISATIONS.INCORPORELLES",
    "IMMOBILISATIONS.CORPORELLES",
]

# ── Noms des colonnes Bilan ───────────────────────────────────
def to_col_bilan(label):
    """Libellé Bilan → nom de colonne avec points (convention cohérente)."""
    name = label.strip().upper()
    name = re.sub(r"[''`´]", "", name)
    name = re.sub(r'[\(\)\+\/]', ' ', name)
    name = re.sub(r'[^A-ZÀÂÄÉÈÊËÎÏÔÙÛÜÇ0-9\s]', ' ', name)
    name = re.sub(r'\s+', '.', name.strip())
    return name.strip('.')

# ── Utilitaires numériques ────────────────────────────────────

def tokenize_bceao(line):
    line = re.sub(r'(-\d{1,2})\s+(\d{3})(?!\d)', r'\1\2', line)
    return [t for t in line.strip().split() if re.match(r'^-?\d+$', t)]

def to_val(toks):
    if not toks: return None
    if len(toks) == 1: return float(toks[0])
    if any(t.startswith('-') for t in toks): return None
    return float(''.join(toks))

def score_p(vals):
    logs = [math.log1p(abs(v)) for v in vals if v != 0]
    if not logs: return 0.0
    m = sum(logs) / len(logs)
    return sum((l - m) ** 2 for l in logs)

def parse_exactly_3(toks):
    n, best, bs = len(toks), None, float('inf')
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            v1, v2, v3 = to_val(toks[:i]), to_val(toks[i:j]), to_val(toks[j:])
            if None not in (v1, v2, v3):
                s = score_p([v1, v2, v3])
                if s < bs: bs, best = s, [v1, v2, v3]
    return best or [float(t) for t in toks[:3]]

def parse_line_values(line):
    toks = tokenize_bceao(line)
    return parse_exactly_3(toks) if len(toks) >= 3 else []

def parse_vals_cell(cell):
    if not cell: return []
    lines = [l.strip() for l in str(cell).split('\n') if l.strip()]
    lines = [l for l in lines if not re.search(r'montant|millions|fcfa', l, re.I)]
    result = []
    for l in lines:
        try: result.append(float(re.sub(r'[\s\xa0]', '', l)))
        except: result.append(None)
    return result

SKIP_LBL = {
    'actif', 'passif', 'hors - bilan', 'hors-bilan',
    'montant net en millions de fcfa',
    'engagements donnés', 'engagements reçus',
    'engagements de financement', 'engagement de garantie',
    'engagements sur titres', '2020', '2021', '2022'
}

def clean_labels(cell):
    if not cell: return []
    return [l.strip() for l in str(cell).split('\n')
            if l.strip() and l.strip().lower() not in SKIP_LBL]

# ── Parseur Bilan ─────────────────────────────────────────────

def parse_bilan_table(table, years):
    results = {y: {} for y in years}
    value_rows = {}

    for i, row in enumerate(table):
        if not row: continue
        col0 = row[0]
        col1 = row[1] if len(row) > 1 else None
        col2 = row[2] if len(row) > 2 else None
        col3 = row[3] if len(row) > 3 else None

        skip_col0 = col0 is None or str(col0).strip().lower() in (
            '', 'actif', 'passif', 'hors - bilan', 'hors-bilan')
        labels   = clean_labels(col0) if not skip_col0 else []
        v2020, v2021, v2022 = parse_vals_cell(col1), parse_vals_cell(col2), parse_vals_cell(col3)
        has_vals = any([v2020, v2021, v2022])

        if labels and has_vals:
            for j, lbl in enumerate(labels):
                col = to_col_bilan(lbl)
                if not col: continue
                for year, vl in [(2020, v2020), (2021, v2021), (2022, v2022)]:
                    if year in years and j < len(vl) and vl[j] is not None:
                        results[year][col] = vl[j]

        elif labels and not has_vals:
            orphan = value_rows.get(i - 2)
            if orphan:
                for j, lbl in enumerate(labels):
                    col = to_col_bilan(lbl)
                    if not col: continue
                    for year in years:
                        vl = orphan.get(year, [])
                        if j < len(vl) and vl[j] is not None:
                            results[year][col] = vl[j]

        elif not labels and has_vals:
            value_rows[i] = {2020: v2020, 2021: v2021, 2022: v2022}

    return results

# ── Parseur Résultat ──────────────────────────────────────────

SKIP_RESULT = {
    'senegal', '2020 2021 2022', 'montant net en millions de fcfa',
    'produits/charges', 'comptes de résultat 2020-2021-2022',
}

def parse_resultat_text(text, years):
    """Séquentiel : assigne les valeurs dans l'ordre de SEQUENCE_RESULTAT."""
    results = {y: {} for y in years}
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    seq_idx = 0
    waiting_for_vals = False

    for line in lines:
        if seq_idx >= len(SEQUENCE_RESULTAT): break
        if not line: continue
        if line.lower() in SKIP_RESULT: continue
        if re.match(r'^\d{1,3}$', line): continue
        if re.match(r'^[A-Z\.]{2,12}$', line): continue
        if line.isupper() and len(line) > 15 and not any(c.isdigit() for c in line): continue

        vals = parse_line_values(line)

        if len(vals) == 3:
            col = SEQUENCE_RESULTAT[seq_idx]
            for i, year in enumerate([2020, 2021, 2022]):
                if year in years:
                    results[year][col] = vals[i]
            seq_idx += 1
            waiting_for_vals = False
        else:
            if not waiting_for_vals:
                waiting_for_vals = True
            else:
                waiting_for_vals = False

    return results

# ── Extraction du sigle ───────────────────────────────────────

def extract_sigle(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for i, line in enumerate(lines[:6]):
        if line.upper() == 'SENEGAL' and i + 1 < len(lines):
            candidate = lines[i + 1].strip()
            skip = ['BILAN', 'COMPTE', 'ETABL', 'RAPPORT', 'PRODUIT', 'MONTANT']
            if 2 <= len(candidate) <= 12 and not any(w in candidate.upper() for w in skip):
                return candidate
    return None

def normalize_sigle(raw):
    if not raw: return None
    key = raw.strip().upper().replace('.', '').replace(' ', '')
    for pdf_s, excel_s in SIGLE_PDF_TO_EXCEL.items():
        if key == pdf_s.upper().replace('.', ''):
            return excel_s
    return None

# ── Reconstruction des colonnes manquantes ────────────────────

def _reconstruct_missing(kpis, sigle, year):
    """
    Reconstruit BILAN, RESSOURCES, FONDS.PROPRE si absents après le mapping.
    Couvre les cas où la structure table PDF fusionne les labels en une seule
    cellule, rendant TOTAL.DE.LACTIF non extractible directement.
    """
    # BILAN = somme postes actif (TOTAL.DE.LACTIF absent dans table fusionnée)
    if "BILAN" not in kpis:
        vals = [kpis[c] for c in ACTIF_COLS if c in kpis and kpis[c] is not None]
        if len(vals) >= 3:
            kpis["BILAN"] = sum(vals)
            logger.debug(f"  {sigle} [{year}] BILAN reconstruit = {kpis['BILAN']} ({len(vals)} postes actif)")
        else:
            logger.warning(f"  {sigle} [{year}] BILAN non reconstructible ({len(vals)} postes actif dispo)")

    # RESSOURCES = chercher toute colonne dettes clientèle (fallback accent)
    if "RESSOURCES" not in kpis:
        for k in list(kpis.keys()):
            if "DETTES" in k and "CLIENT" in k:
                kpis["RESSOURCES"] = kpis[k]
                logger.debug(f"  {sigle} [{year}] RESSOURCES ← {k} = {kpis['RESSOURCES']}")
                break
        if "RESSOURCES" not in kpis:
            logger.warning(f"  {sigle} [{year}] RESSOURCES non trouvé")

    # FONDS.PROPRE = fallback sur toute colonne CAPITAUX PROPRES
    if "FONDS.PROPRE" not in kpis:
        for k in list(kpis.keys()):
            if "CAPITAUX" in k and "PROPRES" in k:
                kpis["FONDS.PROPRE"] = kpis[k]
                logger.debug(f"  {sigle} [{year}] FONDS.PROPRE ← {k} = {kpis['FONDS.PROPRE']}")
                break
        if "FONDS.PROPRE" not in kpis:
            logger.warning(f"  {sigle} [{year}] FONDS.PROPRE non trouvé")

    return kpis

# ── Extracteur principal ──────────────────────────────────────

def extract_senegal_data(pdf_path):
    results = []
    logger.info(f"Ouverture du PDF : {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            logger.info(f"Nombre de pages : {total}")
            bank_data = {}

            for page_idx in range(SENEGAL_PAGES_START - 1, SENEGAL_PAGES_END):
                if page_idx >= total: break
                page     = pdf.pages[page_idx]
                page_num = page_idx + 1
                text     = page.extract_text() or ""

                raw_sigle = extract_sigle(text)
                sigle     = normalize_sigle(raw_sigle) if raw_sigle else None
                if not sigle:
                    continue

                if sigle not in bank_data:
                    bank_data[sigle] = {y: {} for y in YEARS_TO_EXTRACT}

                if 'Bilans 2020' in text or 'ACTIF' in text:
                    tables = page.extract_tables()
                    if tables:
                        parsed = parse_bilan_table(tables[0], YEARS_TO_EXTRACT)
                        for year in YEARS_TO_EXTRACT:
                            bank_data[sigle][year].update(parsed[year])
                elif 'Résultat' in text or 'PRODUIT NET BANCAIRE' in text:
                    parsed = parse_resultat_text(text, YEARS_TO_EXTRACT)
                    for year in YEARS_TO_EXTRACT:
                        bank_data[sigle][year].update(parsed[year])

            for sigle, years_data in bank_data.items():
                for year, kpis in years_data.items():
                    if not kpis:
                        logger.warning(f"{sigle} [{year}] : aucun KPI")
                        continue

                    # ── Étape 1 : mapping direct PDF → noms Excel ────────
                    for pdf_col, excel_col in PDF_TO_EXCEL_COLS.items():
                        if pdf_col in kpis and excel_col not in kpis:
                            kpis[excel_col] = kpis[pdf_col]
                            logger.debug(f"  {sigle} [{year}] alias {pdf_col} → {excel_col} = {kpis[excel_col]}")

                    # ── Étape 2 : reconstruction des colonnes manquantes ──
                    kpis = _reconstruct_missing(kpis, sigle, year)

                    results.append({
                        "Sigle":          sigle,
                        "Goupe_Bancaire": GROUPES.get(sigle, "Inconnu"),
                        "ANNEE":          year,
                        **kpis,
                    })
                    logger.info(
                        f"✅ {sigle} [{year}] : {len(kpis)} KPIs — "
                        f"BILAN={'✓' if 'BILAN' in kpis else '✗'}  "
                        f"EMPLOI={'✓' if 'EMPLOI' in kpis else '✗'}  "
                        f"RESSOURCES={'✓' if 'RESSOURCES' in kpis else '✗'}  "
                        f"FONDS.PROPRE={'✓' if 'FONDS.PROPRE' in kpis else '✗'}"
                    )

    except Exception as e:
        logger.error(f"Erreur : {e}", exc_info=True)

    logger.info(f"Extraction terminée : {len(results)} enregistrements")
    return results
