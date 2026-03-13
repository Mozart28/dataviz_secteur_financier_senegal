# Observatoire Économique · Sénégal

Dashboard de datavisualisation multi-secteur pour l'analyse des secteurs **bancaire**, **énergétique** et **assurantiel** au Sénégal.

> Projet académique M2 Big Data — données officielles BCEAO · Parc PV Sénégal · Données confidentielles

---

## Aperçu

| Secteur | Pages | Source | Période |
|---|---|---|---|
| 🏦 Bancaire | 7 | BCEAO | 2015 – 2022 |
| ⚡ Énergie | 6 | Parc Photovoltaïque Sénégal | — |
| ◉ Assurance | 4 | Données confidentielles | — |

---

## Stack technique

- **Frontend** — Dash (Plotly) · Dash Bootstrap Components
- **Backend** — Python 3.12 · Flask
- **Base de données** — MongoDB Atlas
- **Pipeline données** — Extraction PDF BCEAO → pandas → MongoDB
- **Déploiement** — Render

---

## Structure du projet

```
PROJET_DATAVIZ_SECTEUR_BANCAIRE_SENEGAL/
├── dashboard/
│   ├── app.py                  # Point d'entrée, routing, auth
│   ├── login.py                # Page d'authentification
│   ├── home.py                 # Page d'accueil multi-secteur
│   ├── config.py               # Thème, couleurs, constantes
│   ├── assets/                 # CSS global
│   ├── components/
│   │   ├── navbar.py           # Sidebar + fil d'Ariane
│   │   ├── export_utils.py     # Export CSV universel
│   │   └── tooltip_info.py
│   └── sectors/
│       ├── bancaire/           # 7 pages
│       ├── energie/            # 6 pages
│       └── assurance/          # 4 pages
├── bceao_pipeline/
│   ├── extractor.py            # Extraction PDF BCEAO (v9)
│   └── data/processed/         # CSV final 168 lignes · 60 colonnes
├── inject_mongo.py             # Script réinjection MongoDB Atlas
└── requirements.txt
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

Accès : [http://localhost:8050](http://localhost:8050) · Mot de passe : défini via `APP_PASSWORD`

---

## Variables d'environnement

| Variable | Description | Exemple |
|---|---|---|
| `MONGO_URI` | URI MongoDB Atlas | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `APP_PASSWORD` | Mot de passe dashboard | `senegal2024` |

---

## Pipeline données BCEAO

Le script `bceao_pipeline/extractor.py` extrait automatiquement les bilans bancaires depuis les PDF annuels BCEAO :

```bash
python bceao_pipeline/extractor.py
```

Résultat : `data/processed/data_bancaire_senegal_2015_2022.csv` — 168 documents · 24 banques · 8 années

Pour réinjecter dans MongoDB Atlas :

```bash
python inject_mongo.py \
  --uri "mongodb+srv://..." \
  --csv bceao_pipeline/data/processed/data_bancaire_senegal_2015_2022.csv
```

---

## Déploiement

Le dashboard est déployé sur **Render** via connexion GitHub. Tout push sur `main` déclenche un redéploiement automatique.
