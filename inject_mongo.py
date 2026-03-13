#!/usr/bin/env python3
# ============================================================
#  inject_mongo.py — Réinjection données bancaires → MongoDB Atlas
#  Usage : python inject_mongo.py --uri "mongodb+srv://..." --csv data.csv
# ============================================================
import argparse
import math
import sys
import pandas as pd
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError

# ── Config ────────────────────────────────────────────────────
DB_NAME         = "senegal_finance"
COLLECTION_NAME = "bancaire"
CSV_DEFAULT     = "bceao_pipeline/data/processed/data_bancaire_senegal_2015_2022.csv"


def clean_value(v):
    """Convertit NaN → None, numpy int/float → Python natif."""
    if v is None:
        return None
    try:
        if math.isnan(float(v)):
            return None
    except (TypeError, ValueError):
        pass
    # numpy types → Python natif
    if hasattr(v, "item"):
        return v.item()
    return v


def row_to_doc(row: dict) -> dict:
    """Transforme une ligne CSV en document MongoDB propre."""
    doc = {}
    for k, v in row.items():
        # Clé : remplace les caractères problématiques pour Mongo
        clean_key = (k
            .replace(".", "_")
            .replace("$", "")
            .replace(" ", "_")
            .strip("_")
        )
        doc[clean_key] = clean_value(v)
    return doc


def inject(uri: str, csv_path: str, dry_run: bool = False):
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Chargement CSV : {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"  → {len(df)} lignes, {len(df.columns)} colonnes")

    # Validation données clés
    df21 = df[df["ANNEE"].isin([2021, 2022])]
    nas = df21[["BILAN", "RESSOURCES", "FONDS.PROPRE"]].isna().sum().sum()
    if nas > 0:
        print(f"  ⚠️  ATTENTION : {nas} NaN détectés sur BILAN/RESSOURCES/FONDS.PROPRE (2021-2022)")
        print("     Vérifie que tu utilises le CSV corrigé (extracteur v9).")
    else:
        print(f"  ✅ 0 NaN sur BILAN/RESSOURCES/FONDS.PROPRE pour 2021-2022")

    print(f"  Banques : {df['Sigle'].nunique()} | Années : {sorted(df['ANNEE'].unique())}")

    if dry_run:
        print("\n[DRY-RUN] Aucune écriture. Retire --dry-run pour injecter.")
        # Affiche un aperçu des documents
        sample = row_to_doc(df.iloc[0].to_dict())
        print("\nExemple document (1ère ligne) :")
        for k, v in list(sample.items())[:10]:
            print(f"  {k}: {v!r}")
        print("  ...")
        return

    # ── Connexion Atlas ───────────────────────────────────────
    print(f"\nConnexion à MongoDB Atlas…")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    try:
        client.admin.command("ping")
        print("  ✅ Connecté")
    except Exception as e:
        print(f"  ❌ Connexion échouée : {e}")
        sys.exit(1)

    db  = client[DB_NAME]
    col = db[COLLECTION_NAME]

    # ── Upsert (Sigle + ANNEE = clé unique) ──────────────────
    print(f"\nInjection dans {DB_NAME}.{COLLECTION_NAME}…")
    operations = []
    for _, row in df.iterrows():
        doc = row_to_doc(row.to_dict())
        operations.append(UpdateOne(
            {"Sigle": doc.get("Sigle"), "ANNEE": doc.get("ANNEE")},
            {"$set": doc},
            upsert=True,
        ))

    try:
        result = col.bulk_write(operations, ordered=False)
        print(f"\n  ✅ Injection terminée :")
        print(f"     Insérés  : {result.upserted_count}")
        print(f"     Modifiés : {result.modified_count}")
        print(f"     Total    : {result.upserted_count + result.modified_count} / {len(df)}")
    except BulkWriteError as e:
        print(f"  ⚠️  Erreurs bulk write : {e.details}")

    # ── Vérification post-injection ───────────────────────────
    total = col.count_documents({})
    print(f"\n  Total documents dans la collection : {total}")

    # Check 2021-2022
    sample = col.find_one({"Sigle": "CBAO", "ANNEE": 2022})
    if sample:
        print(f"\n  Vérification CBAO 2022 :")
        print(f"    BILAN      : {sample.get('BILAN')}")
        print(f"    RESSOURCES : {sample.get('RESSOURCES')}")
        print(f"    FONDS_PROPRE: {sample.get('FONDS_PROPRE')}")
    else:
        print("  ⚠️  CBAO 2022 introuvable après injection")

    client.close()
    print("\n✅ Script terminé.\n")


# ── CLI ───────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Injecte les données bancaires dans MongoDB Atlas"
    )
    parser.add_argument(
        "--uri",
        required=True,
        help='URI MongoDB Atlas, ex: "mongodb+srv://user:pass@cluster.mongodb.net/"',
    )
    parser.add_argument(
        "--csv",
        default=CSV_DEFAULT,
        help=f"Chemin vers le CSV (défaut: {CSV_DEFAULT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Teste sans écrire dans MongoDB",
    )
    args = parser.parse_args()
    inject(uri=args.uri, csv_path=args.csv, dry_run=args.dry_run)
