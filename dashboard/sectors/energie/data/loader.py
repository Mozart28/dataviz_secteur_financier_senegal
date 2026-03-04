# ============================================================
#  sectors/energie/data/loader.py
# ============================================================

import pandas as pd
import numpy as np
import os

_DF = None

def get_dataframe() -> pd.DataFrame:
    global _DF
    if _DF is not None:
        return _DF

    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, "solar_data.csv")
    df = pd.read_csv(path, sep=';')

    # Parsing datetime
    df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d/%m/%Y %H:%M')
    df['Date']     = pd.to_datetime(df['Date'], format='%d/%m/%Y')

    # Efficacité DC→AC
    df['efficiency'] = np.where(
        df['DC_Power'] > 0,
        df['AC_Power'] / df['DC_Power'] * 100,
        np.nan
    )

    # Saison (hémisphère nord par défaut, inversé pour Australia/Brazil)
    def _season(row):
        m = row['Month']
        if row['Country'] in ('Australia',):
            # Hémisphère sud
            if m in (12, 1, 2):   return 'Été'
            if m in (3, 4, 5):    return 'Automne'
            if m in (6, 7, 8):    return 'Hiver'
            return 'Printemps'
        else:
            if m in (12, 1, 2):   return 'Hiver'
            if m in (3, 4, 5):    return 'Printemps'
            if m in (6, 7, 8):    return 'Été'
            return 'Automne'
    df['season'] = df.apply(_season, axis=1)

    # Tranche horaire
    def _slot(h):
        if h < 6:   return 'Nuit (0–6h)'
        if h < 12:  return 'Matin (6–12h)'
        if h < 18:  return 'Après-midi (12–18h)'
        return 'Soir (18–24h)'
    df['time_slot'] = df['Hour'].apply(_slot)

    # Puissance active (hors nuit)
    df['is_producing'] = df['DC_Power'] > 0

    _DF = df
    return _DF


def get_kpis(df: pd.DataFrame = None) -> dict:
    if df is None:
        df = get_dataframe()

    prod = df[df['DC_Power'] > 0]
    return {
        'total_yield':      df.groupby('Country')['Daily_Yield'].sum().sum(),
        'dc_power_moy':     df['DC_Power'].mean(),
        'ac_power_moy':     df['AC_Power'].mean(),
        'efficiency_moy':   prod['efficiency'].mean(),
        'irradiation_moy':  df['Irradiation'].mean(),
        'temp_amb_moy':     df['Ambient_Temperature'].mean(),
        'temp_mod_moy':     df['Module_Temperature'].mean(),
        'nb_pays':          df['Country'].nunique(),
        'nb_mesures':       len(df),
        'best_country':     df.groupby('Country')['Total_Yield'].max().idxmax(),
        'best_yield':       df.groupby('Country')['Total_Yield'].max().max(),
        'peak_hour':        df.groupby('Hour')['DC_Power'].mean().idxmax(),
        'peak_month':       df.groupby('Month')['DC_Power'].mean().idxmax(),
    }
