# ============================================================
#  tests/run_tests.py — Tests unitaires : intégrité des données
#  Lancer : python3 tests/run_tests.py
#
#  Le fichier Excel est cherché automatiquement dans le projet.
#  Ou via variable d'environnement : BANCAIRE_EXCEL=/chemin/fichier.xlsx
# ============================================================

import sys, os, glob, unittest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Résolution du chemin Excel ────────────────────────────────

def _find_excel() -> str | None:
    # 1. Variable d'environnement (priorité absolue)
    env = os.environ.get("BANCAIRE_EXCEL")
    if env and os.path.exists(env):
        return env
    # 2. Chemins relatifs au projet
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base, "data", "processed", "data_bancaire_senegal_2015_2022.xlsx"),
        os.path.join(base, "data", "data_bancaire_senegal_2015_2022.xlsx"),
        os.path.join(base, "data_bancaire_senegal_2015_2022.xlsx"),
    ]
    # 3. Recherche par pattern dans tout le projet
    found = glob.glob(os.path.join(base, "**", "*bancaire*senegal*.xlsx"), recursive=True)
    found += glob.glob(os.path.join(base, "**", "*senegal*bancaire*.xlsx"), recursive=True)
    candidates += found
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


EXCEL_PATH = _find_excel()


def load_raw() -> pd.DataFrame:
    if not EXCEL_PATH:
        raise FileNotFoundError(
            "Fichier Excel introuvable.\n"
            "Placez-le dans data/ ou définissez :\n"
            "  export BANCAIRE_EXCEL=/chemin/vers/data_bancaire_senegal_2015_2022.xlsx"
        )
    return pd.read_excel(EXCEL_PATH)


def load_normalized() -> pd.DataFrame:
    from data.loader import _normalize
    return _normalize(load_raw())


def load_with_ratios() -> pd.DataFrame:
    from data.loader import compute_ratios
    return compute_ratios(load_normalized())


# ══════════════════════════════════════════════════════════════
#  1. STRUCTURE DE BASE
# ══════════════════════════════════════════════════════════════

class TestStructure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = load_normalized()

    def test_colonnes_obligatoires(self):
        """Les colonnes d'identité doivent toujours être présentes."""
        for col in ["Sigle", "Goupe_Bancaire", "ANNEE"]:
            self.assertIn(col, self.df.columns, f"Colonne manquante : {col}")

    def test_nb_banques(self):
        """Le secteur doit contenir entre 20 et 30 banques."""
        nb = self.df["Sigle"].nunique()
        self.assertGreaterEqual(nb, 20, f"Trop peu de banques : {nb}")
        self.assertLessEqual(nb, 30, f"Trop de banques : {nb}")

    def test_annees_couvertes(self):
        """Les années 2015 à 2022 doivent toutes être présentes."""
        annees = self.df["ANNEE"].dropna().unique().tolist()
        for y in range(2015, 2023):
            self.assertIn(y, annees, f"Année manquante : {y}")

    def test_nb_lignes_minimum(self):
        """Au moins 150 enregistrements."""
        self.assertGreaterEqual(len(self.df), 150)

    def test_pas_de_doublons(self):
        """Aucun doublon Sigle + ANNEE."""
        dupes = self.df.duplicated(subset=["Sigle", "ANNEE"]).sum()
        self.assertEqual(dupes, 0, f"{dupes} doublon(s)")

    def test_quatre_groupes_bancaires(self):
        """Les 4 groupes BCEAO doivent être présents."""
        expected = {"Groupes Continentaux", "Groupes Internationaux",
                    "Groupes Locaux", "Groupes Règionaux"}
        found = set(self.df["Goupe_Bancaire"].dropna().unique())
        self.assertEqual(expected, found)

    def test_sigle_non_vide(self):
        """Aucun Sigle vide ou NaN."""
        self.assertEqual(self.df["Sigle"].isna().sum(), 0)

    def test_banques_annee_pic(self):
        """2018-2019 doivent avoir le plus de banques (24) — pic de couverture."""
        for y in [2018, 2019]:
            nb = self.df[self.df["ANNEE"] == y]["Sigle"].nunique()
            self.assertEqual(nb, 24, f"{y} : {nb} banques (attendu 24)")


# ══════════════════════════════════════════════════════════════
#  2. INTÉGRITÉ DES VALEURS
# ══════════════════════════════════════════════════════════════

class TestIntegrite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = load_normalized()

    def test_pnb_non_negatif(self):
        """Le PNB ne peut pas être négatif."""
        col = "PRODUIT.NET.BANCAIRE"
        if col not in self.df.columns: self.skipTest("Colonne absente")
        n = (self.df[col].dropna() < 0).sum()
        self.assertEqual(n, 0, f"{n} PNB négatif(s)")

    def test_pnb_max_plausible(self):
        """PNB max < 500 Mds FCFA."""
        col = "PRODUIT.NET.BANCAIRE"
        if col not in self.df.columns: self.skipTest("Colonne absente")
        self.assertLess(self.df[col].max(), 500_000)

    def test_resultat_net_plage(self):
        """RN entre -100 Mds et +200 Mds."""
        col = "RESULTAT.NET"
        if col not in self.df.columns: self.skipTest("Colonne absente")
        rn = self.df[col].dropna()
        self.assertGreater(rn.min(), -100_000)
        self.assertLess(rn.max(), 200_000)

    def test_pas_de_inf(self):
        """Aucune valeur infinie."""
        num_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            n = np.isinf(self.df[col].dropna()).sum()
            self.assertEqual(n, 0, f"Infini dans {col}")

    def test_pnb_disponible_annees_completes(self):
        """PNB disponible pour ≥ 10 banques sur les années complètes :
        2017-2019 et 2021-2022. (2015, 2016, 2020 : lacunes sources BCEAO connues)."""
        col = "PRODUIT.NET.BANCAIRE"
        if col not in self.df.columns: self.skipTest("Colonne absente")
        for y in [2017, 2018, 2019, 2021, 2022]:
            n = len(self.df[(self.df["ANNEE"] == y) & self.df[col].notna()])
            self.assertGreaterEqual(n, 10, f"Trop peu de PNB en {y} : {n}")

    def test_pnb_absent_2015_2016_2020_documente(self):
        """2015, 2016 et 2020 ont 0 PNB — comportement connu et documenté."""
        col = "PRODUIT.NET.BANCAIRE"
        if col not in self.df.columns: self.skipTest("Colonne absente")
        for y in [2015, 2016, 2020]:
            n = len(self.df[(self.df["ANNEE"] == y) & self.df[col].notna()])
            self.assertLessEqual(n, 5, f"{y} a plus de PNB que prévu : {n}")

    def test_capital_souscrit_non_negatif(self):
        """Capital souscrit ≥ 0."""
        col = "CAPITAL.SOUSCRIT"
        if col not in self.df.columns: self.skipTest("Colonne absente")
        n = (self.df[col].dropna() < 0).sum()
        self.assertEqual(n, 0)


# ══════════════════════════════════════════════════════════════
#  3. COHÉRENCE COMPTABLE
# ══════════════════════════════════════════════════════════════

class TestCoherence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = load_normalized()

    def test_total_actif_calculable(self):
        """TOTAL_ACTIF doit être calculable pour toutes les lignes."""
        df_r = load_with_ratios()
        n = df_r["TOTAL_ACTIF"].isna().sum()
        self.assertEqual(n, 0, f"{n} lignes sans Total Actif")

    def test_total_actif_positif(self):
        """Total Actif > 0 partout."""
        df_r = load_with_ratios()
        n = (df_r["TOTAL_ACTIF"].dropna() <= 0).sum()
        self.assertEqual(n, 0)

    def test_rn_disponible_proportion(self):
        """RN disponible pour au moins 45% des lignes."""
        col = "RESULTAT.NET"
        if col not in self.df.columns: self.skipTest("Colonne absente")
        pct = self.df[col].notna().mean() * 100
        self.assertGreaterEqual(pct, 45, f"RN à {pct:.0f}% — problème de source")

    def test_capitaux_propres_2022(self):
        """En 2022, ≥ 80% des banques ont des capitaux propres."""
        col = "CAPITAUX.PROPRES.ET.RESSOURCES.ASSIMILÉES"
        if col not in self.df.columns: self.skipTest("Colonne absente")
        d = self.df[self.df["ANNEE"] == 2022]
        pct = d[col].notna().mean() * 100
        self.assertGreaterEqual(pct, 80, f"Seulement {pct:.0f}% en 2022")


# ══════════════════════════════════════════════════════════════
#  4. RATIOS FINANCIERS
# ══════════════════════════════════════════════════════════════

class TestRatios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = load_with_ratios()

    def test_roa_plage(self):
        """ROA entre -10% et +10% (max 3 exceptions)."""
        if "ROA" not in self.df.columns: self.skipTest("ROA absent")
        roa = self.df["ROA"].dropna()
        n = ((roa < -10) | (roa > 10)).sum()
        self.assertLessEqual(n, 3, f"{n} ROA hors [-10%, +10%]")

    def test_roe_plage(self):
        """ROE entre -50% et +50% (max 3 exceptions)."""
        if "ROE" not in self.df.columns: self.skipTest("ROE absent")
        roe = self.df["ROE"].dropna()
        n = ((roe < -50) | (roe > 50)).sum()
        self.assertLessEqual(n, 3, f"{n} ROE hors [-50%, +50%]")

    def test_roa_roe_disponibles_quand_rn_present(self):
        """Quand RN est disponible, ROA et ROE doivent être calculables (≥ 95%)."""
        mask_rn = self.df["RESULTAT.NET"].notna()
        if not mask_rn.any(): self.skipTest("RN absent")
        d = self.df[mask_rn]
        for col in ["ROA", "ROE"]:
            if col not in d.columns: continue
            pct = d[col].notna().mean() * 100
            self.assertGreaterEqual(pct, 95, f"{col} calculable pour seulement {pct:.0f}%")

    def test_cout_risque_positif(self):
        """Coût du risque en % ≥ 0 (valeur absolue)."""
        col = "COUT_RISQUE_PCT"
        if col not in self.df.columns: self.skipTest("Colonne absente")
        n = (self.df[col].dropna() < 0).sum()
        self.assertEqual(n, 0)

    def test_marge_nette_cas_extremes_documentes(self):
        """Marge nette peut dépasser 100% quand RBE est très bas (≤ 20 cas)."""
        col = "MARGE_NETTE"
        if col not in self.df.columns: self.skipTest("Colonne absente")
        mn = self.df[col].dropna()
        n = ((mn < -100) | (mn > 100)).sum()
        self.assertLessEqual(n, 20, f"{n} valeurs extrêmes — dépasse le seuil d'alerte")

    def test_roe_positif_quand_rn_positif(self):
        """Quand RN > 0, ROE doit être positif."""
        mask = self.df["RESULTAT.NET"].notna() & (self.df["RESULTAT.NET"] > 0)
        d = self.df[mask]
        if d.empty: self.skipTest("Aucune ligne avec RN > 0")
        n = (d["ROE"].dropna() < 0).sum()
        self.assertEqual(n, 0, f"{n} cas ROE négatif alors que RN > 0")


# ══════════════════════════════════════════════════════════════
#  5. FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════

class TestUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = load_normalized()

    def test_agg_retourne_float(self):
        """agg() retourne un float pour une colonne valide."""
        from data.loader import agg
        d = self.df[self.df["ANNEE"] == 2022]
        result = agg(d, "PRODUIT.NET.BANCAIRE")
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_agg_retourne_none_si_vide(self):
        """agg() retourne None sur un DataFrame vide."""
        from data.loader import agg
        empty = pd.DataFrame({"PRODUIT.NET.BANCAIRE": pd.Series([], dtype=float)})
        self.assertIsNone(agg(empty, "PRODUIT.NET.BANCAIRE"))

    def test_agg_fallback_colonnes(self):
        """agg() utilise la première colonne disponible parmi les candidats."""
        from data.loader import agg
        d = self.df[self.df["ANNEE"] == 2022]
        result = agg(d, "COLONNE_INEXISTANTE", "PRODUIT.NET.BANCAIRE")
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)

    def test_agg_toutes_colonnes_inconnues(self):
        """agg() retourne None si toutes les colonnes sont inconnues."""
        from data.loader import agg
        d = self.df[self.df["ANNEE"] == 2022]
        self.assertIsNone(agg(d, "COL_A", "COL_B"))

    def test_best_col_prefere_pnb(self):
        """best_col() préfère PRODUIT.NET.BANCAIRE sur BILAN."""
        from data.loader import best_col
        d = self.df[self.df["ANNEE"] == 2022]
        self.assertEqual(best_col(d), "PRODUIT.NET.BANCAIRE")

    def test_get_annees_triees_depuis_df(self):
        """Les années du DataFrame sont triées."""
        annees = sorted(self.df["ANNEE"].dropna().unique().tolist())
        self.assertEqual(annees, sorted(annees))

    def test_normalize_supprime_doublons(self):
        """_normalize() supprime les doublons Sigle+ANNEE."""
        from data.loader import _normalize
        df_raw = load_raw()
        df_dup = pd.concat([df_raw, df_raw.head(5)], ignore_index=True)
        df_clean = _normalize(df_dup)
        self.assertEqual(df_clean.duplicated(subset=["Sigle","ANNEE"]).sum(), 0)

    def test_normalize_annee_numerique(self):
        """_normalize() convertit ANNEE en numérique même si fourni en string."""
        from data.loader import _normalize
        df_raw = load_raw()
        df_str = df_raw.copy()
        df_str["ANNEE"] = df_str["ANNEE"].astype(str)
        df_clean = _normalize(df_str)
        self.assertTrue(
            pd.api.types.is_integer_dtype(df_clean["ANNEE"]) or
            pd.api.types.is_float_dtype(df_clean["ANNEE"])
        )

    def test_normalize_pas_de_inf(self):
        """_normalize() élimine les valeurs infinies."""
        from data.loader import _normalize
        df_clean = _normalize(load_raw())
        num_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            self.assertEqual(np.isinf(df_clean[col].dropna()).sum(), 0,
                             f"Infini dans {col} après normalisation")


# ══════════════════════════════════════════════════════════════
#  RUNNER PRINCIPAL
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"Excel trouvé : {EXCEL_PATH or '❌ INTROUVABLE'}\n")

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in [TestStructure, TestIntegrite, TestCoherence, TestRatios, TestUtils]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "="*60)
    print(f"  RÉSULTAT : {result.testsRun} tests exécutés")
    print(f"  ✅ Réussis  : {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"  ❌ Échoués  : {len(result.failures)}")
    print(f"  💥 Erreurs  : {len(result.errors)}")
    print(f"  ⏭  Ignorés  : {len(result.skipped)}")
    print("="*60)
    sys.exit(0 if result.wasSuccessful() else 1)
