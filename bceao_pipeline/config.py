# ============================================================
#  config.py — Configuration centrale du pipeline BCEAO
# ============================================================

# URLs des rapports PDF BCEAO
# Le rapport 2022 contient les bilans des années 2020, 2021 et 2022.
# On n'utilise que ce seul PDF pour extraire les données 2021 et 2022.
PDF_URLS = {
    2022: "https://www.bceao.int/sites/default/files/2024-05/Bilans%20et%20comptes%20de%20r%C3%A9sultat%20des%20banques%2C%20%C3%A9tablissements%20financiers%20et%20compagnies%20financi%C3%A8res%20de%20l%27UMOA%202022.pdf",
}

# Années à extraire depuis le PDF 2022 (on ignore 2020 car déjà dans l'Excel)
YEARS_TO_EXTRACT = [2021, 2022]

# Dossiers
PDF_DIR       = "data/raw_pdfs"
PROCESSED_DIR = "data/processed"
LOGS_DIR      = "logs"

# MongoDB
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB  = "banking_senegal"
MONGO_COLLECTION = "bilans_banques"

# Les 24 banques sénégalaises à cibler (sigles + noms alternatifs dans les PDFs)
BANQUES_SENEGAL = {
    "BAS":        ["BAS", "Banque Atlantique Sénégal"],
    "BCIM":       ["BCIM", "Banque de Crédit et d'Investissement"],
    "BDK":        ["BDK", "Banque de Dakar"],
    "BGFI":       ["BGFI", "BGFIBank Sénégal", "BGFI BANK"],
    "BHS":        ["BHS", "Banque de l'Habitat du Sénégal"],
    "BICIS":      ["BICIS", "Banque Internationale pour le Commerce et l'Industrie du Sénégal"],
    "BIS":        ["BIS", "Banque Islamique du Sénégal"],
    "BNDE":       ["BNDE", "Banque Nationale pour le Développement Économique"],
    "BOA":        ["BOA", "Bank of Africa Sénégal", "BOA SÉNÉGAL"],
    "BRM":        ["BRM", "Banque Régionale des Marchés"],
    "BSIC":       ["BSIC", "Banque Sahélo-Saharienne"],
    "CBAO":       ["CBAO", "Compagnie Bancaire de l'Afrique Occidentale"],
    "CBI":        ["CBI", "Crédit du Sénégal"],
    "CDS":        ["CDS", "Crédit du Sénégal", "Caisse de Dépôt et de Consignation"],
    "CISA":       ["CISA", "Citibank Sénégal"],
    "CITIBANK":   ["CITIBANK", "Citibank"],
    "ECOBANK":    ["ECOBANK", "Ecobank Sénégal"],
    "FBNBANK":    ["FBNBANK", "FBNBank Sénégal"],
    "LBA":        ["LBA", "La Banque Agricole"],
    "LBO":        ["LBO", "Locafrique"],
    "NSIA Banque":["NSIA", "NSIA Banque"],
    "ORABANK":    ["ORABANK", "Orabank Sénégal"],
    "SGBS":       ["SGBS", "Société Générale de Banques au Sénégal"],
    "UBA":        ["UBA", "United Bank for Africa Sénégal"],
}

# Mapping des colonnes Excel → libellés attendus dans les PDFs BCEAO
# (les PDFs utilisent les codes du Plan Comptable Bancaire de l'UMOA)
COLONNES_EXCEL = [
    "Sigle", "Goupe_Bancaire", "ANNEE",
    "EMPLOI", "BILAN", "RESSOURCES", "FONDS.PROPRE",
    "EFFECTIF", "AGENCE", "COMPTE",
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
