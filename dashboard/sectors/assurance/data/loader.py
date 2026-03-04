# ============================================================
#  sectors/assurance/data/loader.py
# ============================================================

import os
import glob
import pandas as pd
import numpy as np

_CACHE = None


def _find_csv() -> str | None:
    env = os.environ.get("ASSURANCE_CSV")
    if env and os.path.exists(env):
        return env
    root = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "..", "..", ".."))
    candidates = [
        os.path.join(root, "data", "assurance", "assurance_data_1000.csv"),
        os.path.join(root, "data", "assurance_data_1000.csv"),
        os.path.join(root, "assurance_data_1000.csv"),
    ]
    candidates += glob.glob(
        os.path.join(root, "**", "*assurance*.csv"), recursive=True)
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


CSV_PATH = _find_csv()


def get_dataframe() -> pd.DataFrame:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not CSV_PATH:
        raise FileNotFoundError(
            "Fichier assurance introuvable.\n"
            "Placez-le dans data/assurance/ ou :\n"
            "  export ASSURANCE_CSV=/chemin/assurance_data_1000.csv")
    df = pd.read_csv(CSV_PATH, sep=';')
    df = _normalize(df)
    _CACHE = df
    return df


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['date_derniere_sinistre'] = pd.to_datetime(
        df['date_derniere_sinistre'], errors='coerce')
    df['annee']  = df['date_derniere_sinistre'].dt.year.astype('Int64')
    df['mois']   = df['date_derniere_sinistre'].dt.month.astype('Int64')
    # Ratio S/P individuel
    df['ratio_sp'] = np.where(
        df['montant_prime'] > 0,
        df['montant_sinistres'] / df['montant_prime'] * 100,
        np.nan)
    # Tranche d'âge
    df['tranche_age'] = pd.cut(
        df['age'], bins=[17, 30, 45, 60, 79],
        labels=['18–30', '31–45', '46–60', '61–79'])
    # Sinistré (bool)
    df['sinistre'] = df['nb_sinistres'] > 0
    return df


def get_kpis_globaux(df: pd.DataFrame = None) -> dict:
    if df is None:
        df = get_dataframe()
    total_primes    = float(df['montant_prime'].sum())
    total_sinistres = float(df['montant_sinistres'].sum())
    return {
        "nb_contrats":    int(len(df)),
        "total_primes":   total_primes,
        "total_sinistres":total_sinistres,
        "ratio_sp":       total_sinistres / total_primes * 100 if total_primes else 0,
        "taux_sinistralite": float((df['nb_sinistres'] > 0).mean() * 100),
        "prime_moyenne":  float(df['montant_prime'].mean()),
        "sinistre_moyen": float(df[df['sinistre']]['montant_sinistres'].mean()),
        "bonus_malus_moy":float(df['bonus_malus'].mean()),
    }
