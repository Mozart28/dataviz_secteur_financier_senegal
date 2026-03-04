# ============================================================
#  mongo_loader.py — Chargement des données dans MongoDB
# ============================================================

import logging
import pandas as pd
from datetime import datetime
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

logger = logging.getLogger(__name__)


def get_mongo_client():
    """Retourne un client MongoDB."""
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test de connexion
        logger.info(f"✅ Connexion MongoDB réussie : {MONGO_URI}")
        return client
    except Exception as e:
        logger.error(f"❌ Impossible de se connecter à MongoDB : {e}")
        raise


def df_to_mongo(df: pd.DataFrame, replace: bool = False) -> dict:
    """
    Insère un DataFrame dans MongoDB.
    
    Args:
        df: DataFrame à insérer
        replace: Si True, vide la collection avant insertion
    
    Returns:
        dict avec les stats d'insertion
    """
    client = get_mongo_client()
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    # Optionnel : vider la collection
    if replace:
        collection.drop()
        logger.info("Collection vidée avant réimportation")

    # Convertir le DataFrame en liste de dicts
    records = df.where(pd.notnull(df), None).to_dict(orient="records")

    # MongoDB n'accepte pas les points dans les noms de clés ($set interprète "A.B" comme chemin)
    # On remplace tous les points par des underscores
    def sanitize_keys(record: dict) -> dict:
        return {k.replace('.', '_'): v for k, v in record.items()}

    records = [sanitize_keys(r) for r in records]

    # Ajouter métadonnées
    now = datetime.utcnow().isoformat()
    for record in records:
        record["_created_at"] = now
        record["_updated_at"] = now

    # Upsert : mettre à jour si (Sigle, ANNEE) existe déjà, sinon insérer
    stats = {"inserted": 0, "updated": 0, "errors": 0}

    for record in records:
        try:
            sigle = record.get("Sigle")
            annee = record.get("ANNEE")
            if not sigle or not annee:
                continue

            result = collection.update_one(
                {"Sigle": sigle, "ANNEE": annee},
                {"$set": record},
                upsert=True
            )
            if result.upserted_id:
                stats["inserted"] += 1
            else:
                stats["updated"] += 1

        except Exception as e:
            logger.error(f"Erreur lors de l'insertion de {record.get('Sigle')}/{record.get('ANNEE')}: {e}")
            stats["errors"] += 1

    # Créer les index pour accélérer les requêtes du dashboard
    collection.create_index([("Sigle", 1), ("ANNEE", 1)], unique=True)
    collection.create_index([("ANNEE", 1)])
    collection.create_index([("Goupe_Bancaire", 1)])

    logger.info(f"MongoDB : {stats['inserted']} insérés, {stats['updated']} mis à jour, {stats['errors']} erreurs")
    client.close()
    return stats


def query_banque(sigle: str) -> list[dict]:
    """Récupère toutes les données d'une banque."""
    client = get_mongo_client()
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    result = list(collection.find({"Sigle": sigle}, {"_id": 0}).sort("ANNEE", 1))
    client.close()
    return result


def query_annee(year: int) -> list[dict]:
    """Récupère toutes les banques pour une année donnée."""
    client = get_mongo_client()
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    result = list(collection.find({"ANNEE": year}, {"_id": 0}))
    client.close()
    return result


def get_all_data() -> pd.DataFrame:
    """Récupère toutes les données sous forme de DataFrame (pour le dashboard)."""
    client = get_mongo_client()
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    data = list(collection.find({}, {"_id": 0, "_created_at": 0, "_updated_at": 0}))
    client.close()
    return pd.DataFrame(data)
