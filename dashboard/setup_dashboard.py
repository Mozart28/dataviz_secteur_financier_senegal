#!/usr/bin/env python3
"""
setup_dashboard.py — Script d'installation du dashboard
Copie tous les fichiers nécessaires dans le bon dossier.

Usage : python3 setup_dashboard.py
"""

import os
import shutil
import sys
from pathlib import Path

# ── Fichiers à créer ──────────────────────────────────────────

PAGES_MISSING = {
    "pages/banque.py": '''\
import dash
from dash import html
from config import THEME, FONTS

dash.register_page(__name__, path="/banque", name="Profil Banque", order=1,
                   title="Dashboard Bancaire · Profil Banque")

layout = html.Div([
    html.Div([
        html.Span("EN CONSTRUCTION", style={
            "color": THEME["accent"], "fontSize": "9px",
            "letterSpacing": "3px", "fontFamily": FONTS["mono"], "fontWeight": "600"
        }),
        html.H2("Profil Banque", style={
            "color": THEME["text"], "fontFamily": FONTS["display"],
            "fontWeight": "300", "marginTop": "8px", "fontSize": "28px"
        }),
        html.P("Évolution des KPIs par banque · Ratios financiers · Export PDF",
            style={"color": THEME["text_muted"], "fontFamily": FONTS["mono"],
                   "fontSize": "12px", "marginTop": "12px"}),
    ], style={"padding": "60px 40px"})
], style={"background": THEME["bg_dark"], "minHeight": "100vh"})
''',

    "pages/comparaison.py": '''\
import dash
from dash import html
from config import THEME, FONTS

dash.register_page(__name__, path="/comparaison", name="Comparaison", order=2,
                   title="Dashboard Bancaire · Comparaison")

layout = html.Div([
    html.Div([
        html.Span("EN CONSTRUCTION", style={
            "color": THEME["accent"], "fontSize": "9px",
            "letterSpacing": "3px", "fontFamily": FONTS["mono"], "fontWeight": "600"
        }),
        html.H2("Comparaison Interbancaire", style={
            "color": THEME["text"], "fontFamily": FONTS["display"],
            "fontWeight": "300", "marginTop": "8px", "fontSize": "28px"
        }),
        html.P("Classement · Radar · Heatmap des performances",
            style={"color": THEME["text_muted"], "fontFamily": FONTS["mono"],
                   "fontSize": "12px", "marginTop": "12px"}),
    ], style={"padding": "60px 40px"})
], style={"background": THEME["bg_dark"], "minHeight": "100vh"})
''',

    "pages/ratios.py": '''\
import dash
from dash import html
from config import THEME, FONTS

dash.register_page(__name__, path="/ratios", name="Ratios & Analyse", order=3,
                   title="Dashboard Bancaire · Ratios")

layout = html.Div([
    html.Div([
        html.Span("EN CONSTRUCTION", style={
            "color": THEME["accent"], "fontSize": "9px",
            "letterSpacing": "3px", "fontFamily": FONTS["mono"], "fontWeight": "600"
        }),
        html.H2("Ratios & Analyse Financière", style={
            "color": THEME["text"], "fontFamily": FONTS["display"],
            "fontWeight": "300", "marginTop": "8px", "fontSize": "28px"
        }),
        html.P("Solvabilité · Liquidité · Rentabilité · ROA · ROE",
            style={"color": THEME["text_muted"], "fontFamily": FONTS["mono"],
                   "fontSize": "12px", "marginTop": "12px"}),
    ], style={"padding": "60px 40px"})
], style={"background": THEME["bg_dark"], "minHeight": "100vh"})
''',

    "pages/__init__.py": "",

    "components/__init__.py": "",

    "data/__init__.py": '''\
from .loader import (
    get_dataframe, get_annees, get_banques, get_groupes,
    get_annee_data, get_banque_data, get_col,
    get_best_indicator_col, invalidate_cache,
)
''',

    "tests/__init__.py": "",
}


def main():
    # Déterminer le dossier cible (là où ce script est lancé)
    target = Path(__file__).parent
    print(f"\n📁 Dossier cible : {target}\n")

    # 1. Créer les dossiers manquants
    for d in ["pages", "components", "data", "tests", "assets",
              "data/processed"]:
        (target / d).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Dossier : {d}/")

    # 2. Créer les fichiers manquants
    print()
    for rel_path, content in PAGES_MISSING.items():
        fpath = target / rel_path
        if not fpath.exists():
            fpath.write_text(content, encoding="utf-8")
            print(f"  ✅ Créé   : {rel_path}")
        else:
            print(f"  ⏭  Existe : {rel_path}")

    # 3. Vérifier les fichiers critiques
    print()
    critical = [
        "app.py", "config.py",
        "data/loader.py",
        "components/kpi_card.py",
        "components/navbar.py",
        "pages/vue_marche/__init__.py",
        "pages/vue_marche/layout.py",
        "pages/vue_marche/callbacks.py",
    ]
    all_ok = True
    for f in critical:
        exists = (target / f).exists()
        icon = "✅" if exists else "❌ MANQUANT"
        print(f"  {icon}  {f}")
        if not exists:
            all_ok = False

    # 4. Vérifier les données
    print()
    data_paths = [
        "data/processed/data_bancaire_senegal_2015_2022.xlsx",
        "data/processed/data_bancaire_senegal_2015_2022.csv",
    ]
    data_ok = False
    for dp in data_paths:
        if (target / dp).exists():
            print(f"  ✅ Données : {dp}")
            data_ok = True
            break
    if not data_ok:
        print(f"  ⚠️  Données manquantes — copie nécessaire :")
        print(f"     cp data/processed/data_bancaire_senegal_2015_2022.xlsx dash/data/processed/")

    # 5. Résumé
    print()
    if all_ok:
        print("  🎉 Installation complète — lance : python3 app.py")
    else:
        print("  ⚠️  Fichiers manquants — télécharge les depuis Claude")

    print()


if __name__ == "__main__":
    main()
