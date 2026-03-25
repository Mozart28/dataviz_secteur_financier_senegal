# Observatoire Économique · Sénégal

> Dashboard de datavisualisation interactive pour l'analyse des secteurs **bancaire**, **énergétique** et **assurantiel** au Sénégal.

🔗 **[Live Demo → dataviz-secteur-financier-senegal.onrender.com](https://dataviz-secteur-financier-senegal.onrender.com)**

---

## Présentation

Ce projet propose une plateforme d'analyse multi-secteur construite sur des données officielles extraites automatiquement depuis des rapports PDF de la BCEAO, enrichies de données terrain du parc photovoltaïque sénégalais et de données assurantielles anonymisées.

L'objectif : rendre lisibles et exploitables des données financières complexes à travers des visualisations interactives, un pipeline de données automatisé et une interface pensée pour l'analyse.

---

## Secteurs couverts

### 🏦 Secteur Bancaire — 7 pages
| Page | Description |
|---|---|
| Vue Marché | Vue d'ensemble du secteur bancaire sénégalais |
| Fiche Banque | Analyse individuelle par établissement |
| Comparaison | Comparatif multi-banques sur indicateurs clés |
| Ratios | Ratios prudentiels et de performance |
| Benchmark | Positionnement relatif des banques |
| Carte | Répartition géographique des agences |
| Structure | Structure bilancielle agrégée du secteur |
| Positionnement Marché | Simulation du positionnement d'une nouvelle banque dans le secteur |

**Source :** BCEAO · 24 banques · 2015 – 2022 · 168 observations · 60 variables

### ⚡ Secteur Énergie — 6 pages
| Page | Description |
|---|---|
| Vue Globale | Production et consommation d'énergie solaire |
| Analyse Temporelle | Évolution temporelle des mesures capteurs |
| Performance | Rendement et efficacité de l'installation |
| Climatique | Corrélation irradiation / production |
| Comparaison | Comparatif périodes / saisons |
| Anomalies | Détection d'anomalies de production |

**Source :** Parc Photovoltaïque Sénégal · 35 000+ mesures capteurs terrain

### ◉ Secteur Assurance — 4 pages
| Page | Description |
|---|---|
| Vue Portefeuille | Analyse du portefeuille de contrats |
| Sinistres | Fréquence, coût et évolution des sinistres |
| Profil Assuré | Segmentation et profil des assurés |
| Rentabilité | Indicateurs de rentabilité technique |

**Source :** Données réelles anonymisées · Portefeuille entreprise

---

## Architecture technique

```
┌─────────────────────────────────────────────────────────┐
│                     SOURCES DE DONNÉES                  │
│   PDF BCEAO ──── Excel BCEAO ──── Capteurs PV ──── CSV  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  PIPELINE D'EXTRACTION                   │
│                                                         │
│   bceao_pipeline/extractor.py (v9)                      │
│   ├── Parsing PDF (pdfplumber)                          │
│   ├── Nettoyage & validation (pandas)                   │
│   └── Export CSV → 168 lignes · 60 colonnes             │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   MONGODB ATLAS                          │
│   Base : senegal_finance                                │
│   Collection : bancaire (168 documents)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  DASHBOARD DASH                          │
│                                                         │
│   app.py ──── routing ──── auth                         │
│   ├── home.py          (accueil multi-secteur)          │
│   ├── components/                                       │
│   │   ├── navbar.py    (sidebar + fil d'Ariane)         │
│   │   └── export_utils.py  (export CSV)                 │
│   └── sectors/                                         │
│       ├── bancaire/    (7 pages + callbacks)            │
│       ├── energie/     (6 pages + callbacks)            │
│       └── assurance/   (4 pages + callbacks)            │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                     RENDER (Cloud)                       │
│   https://dataviz-secteur-financier-senegal.onrender.com│
└─────────────────────────────────────────────────────────┘
```

---

## Pipeline d'extraction BCEAO

L'extracteur `bceao_pipeline/extractor.py` traite automatiquement les rapports PDF annuels publiés par la BCEAO :

```
PDF BCEAO (2021, 2022)
       │
       ▼
pdfplumber → extraction tableaux bruts
       │
       ▼
Détection automatique des lignes BILAN / RESSOURCES / FONDS PROPRES
       │
       ▼
Nettoyage : suppression espaces insécables, normalisation encodage
       │
       ▼
Fusion avec données Excel historiques (2015–2020)
       │
       ▼
Validation : 17/17 banques × 2 années · 0 NaN sur colonnes clés
       │
       ▼
data/processed/data_bancaire_senegal_2015_2022.csv
(168 lignes · 60 colonnes · 24 banques · 8 années)
```

Pour réexécuter l'extraction :
```bash
python bceao_pipeline/extractor.py
```

Pour réinjecter dans MongoDB Atlas :
```bash
python inject_mongo.py \
  --uri "mongodb+srv://user:pass@cluster.mongodb.net/" \
  --csv bceao_pipeline/data/processed/data_bancaire_senegal_2015_2022.csv
```

---

## Installation locale

```bash
git clone https://github.com/Mozart28/dataviz_secteur_financier_senegal.git
cd PROJET_DATAVIZ_SECTEUR_BANCAIRE_SENEGAL

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd dashboard
python app.py
```

Accès : [http://localhost:8050](http://localhost:8050)

---

## Stack technique

| Composant | Technologie |
|---|---|
| Interface | Dash · Plotly · Dash Bootstrap Components |
| Backend | Python 3.12 · Flask |
| Base de données | MongoDB Atlas |
| Extraction PDF | pdfplumber · pandas |
| Déploiement | Render |
| Versioning | GitHub |

---

## Variables d'environnement

| Variable | Description |
|---|---|
| `MONGO_URI` | URI de connexion MongoDB Atlas |
| `APP_PASSWORD` | Mot de passe d'accès au dashboard |

---

## Structure du projet

```
PROJET_DATAVIZ_SECTEUR_BANCAIRE_SENEGAL/
├── dashboard/
│   ├── app.py                      # Point d'entrée, routing
│   ├── home.py                     # Page d'accueil
│   ├── config.py                   # Thème, constantes
│   ├── assets/                     # CSS
│   ├── components/
│   │   ├── navbar.py               # Sidebar + fil d'Ariane
│   │   ├── export_utils.py         # Export CSV universel
│   │   └── tooltip_info.py
│   └── sectors/
│       ├── bancaire/               # 7 pages (layout + callbacks)
│       ├── energie/                # 6 pages (layout + callbacks)
│       └── assurance/              # 4 pages (layout + callbacks)
├── bceao_pipeline/
│   ├── extractor.py                # Extraction PDF BCEAO v9
│   └── data/
│       └── processed/
│           └── data_bancaire_senegal_2015_2022.csv
├── inject_mongo.py                 # Réinjection MongoDB Atlas
├── requirements.txt
└── README.md
```
