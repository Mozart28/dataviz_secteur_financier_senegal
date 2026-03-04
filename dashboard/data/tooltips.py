# ============================================================
#  data/tooltips.py
#  Contenu analytique des tooltips — 7 pages · 30 tooltips
# ============================================================

TOOLTIPS = {

    # ── Vue Marché ────────────────────────────────────────────────────────────
    "vm-evolution": {
        "titre":      "Évolution sectorielle",
        "mesure":     "Indicateur financier agrégé (PNB, ROE, Total Actif…) de l'ensemble du secteur bancaire sénégalais, par année.",
        "lire":       "La courbe montre la tendance du secteur. Un pic ou une rupture révèle un choc macroéconomique ou réglementaire.",
        "surveiller": "Une baisse du PNB sectoriel de plus de 5% sur 2 ans consécutifs est un signal d'alerte structurel.",
    },
    "vm-classement": {
        "titre":      "Classement des banques",
        "mesure":     "Classement des banques selon l'indicateur sélectionné pour l'année choisie.",
        "lire":       "Barres horizontales triées. La longueur = la valeur absolue. La couleur = le groupe bancaire d'appartenance.",
        "surveiller": "Les banques en bas du classement sur plusieurs indicateurs sont en situation de fragilité relative.",
    },
    "vm-repartition": {
        "titre":      "Répartition par groupe bancaire",
        "mesure":     "Part de chaque groupe (filiales internationales, banques locales, institutions de développement) dans le total sectoriel.",
        "lire":       "Donut chart : chaque arc = un groupe. Survoler pour voir la valeur exacte et le pourcentage.",
        "surveiller": "Une concentration > 60% sur un seul groupe expose le secteur à un risque systémique en cas de choc externe.",
    },
    "vm-pnb-rn": {
        "titre":      "PNB vs Résultat Net",
        "mesure":     "Comparaison entre le Produit Net Bancaire (revenus bruts) et le Résultat Net (bénéfice après charges) pour chaque banque.",
        "lire":       "Scatter plot : axe X = PNB, axe Y = RN. Plus un point est haut à droite, plus la banque est rentable et volumineuse.",
        "surveiller": "Des banques avec un PNB élevé mais un RN faible ont des charges d'exploitation ou des provisions excessives.",
    },

    # ── Profil Banque ─────────────────────────────────────────────────────────
    "pb-evolution": {
        "titre":      "Évolution sur la période",
        "mesure":     "Historique de l'indicateur sélectionné pour la banque choisie, année par année.",
        "lire":       "Courbe temporelle. La pente révèle la trajectoire de croissance ou de déclin de la banque.",
        "surveiller": "Une inflexion brutale (hausse ou baisse > 20% en 1 an) mérite une analyse des causes sous-jacentes.",
    },
    "pb-ratios": {
        "titre":      "Ratios financiers clés",
        "mesure":     "Tableau des ratios prudentiels et de performance : ROA, ROE, Tier 1, Cost-to-Income, NPL.",
        "lire":       "Chaque ratio est comparé à la médiane sectorielle. Rouge = sous la médiane. Vert = au-dessus.",
        "surveiller": "Un ratio NPL (Non-Performing Loans) > 10% signale une dégradation de la qualité du portefeuille de crédit.",
    },
    "pb-pdm": {
        "titre":      "Part de marché sectorielle",
        "mesure":     "Position de la banque dans le secteur : sa part du PNB total, du total actif et des dépôts sénégalais.",
        "lire":       "Barres de progression normalisées sur 100%. La référence = la banque leader du secteur.",
        "surveiller": "Une part de marché qui diminue sur 3 ans consécutifs signale une perte de compétitivité.",
    },
    "pb-radar": {
        "titre":      "Positionnement vs secteur",
        "mesure":     "Radar à 5 axes : PNB, ROE, Tier 1, PDM, Cost-to-Income. Chaque axe est normalisé 0–100 vs le secteur.",
        "lire":       "Plus la surface est grande, plus la banque performe globalement. Un axe creux = faiblesse identifiée.",
        "surveiller": "Un Tier 1 bas combiné à un ROE élevé peut indiquer une prise de risque excessive via l'effet de levier.",
    },

    # ── Comparaison ───────────────────────────────────────────────────────────
    "cmp-heatmap": {
        "titre":      "Heatmap des performances",
        "mesure":     "Matrice banques × indicateurs. Chaque cellule = valeur normalisée de l'indicateur pour une banque donnée.",
        "lire":       "Cellule foncée = valeur élevée. Cellule claire = valeur faible. Permet de voir les forces/faiblesses en un coup d'œil.",
        "surveiller": "Une colonne entièrement claire (indicateur faible pour toutes les banques) peut signaler un problème sectoriel.",
    },
    "cmp-radar": {
        "titre":      "Radar multi-banques",
        "mesure":     "Superposition des profils radar des banques sélectionnées sur les mêmes 5 dimensions normalisées.",
        "lire":       "Chaque couleur = une banque. Les intersections montrent où les banques sont équivalentes.",
        "surveiller": "Des profils très similaires entre concurrents indiquent un marché homogène avec peu de différenciation.",
    },
    "cmp-classement": {
        "titre":      "Classement comparatif",
        "mesure":     "Tableau de classement des banques sélectionnées selon l'indicateur choisi, avec rang absolu dans le secteur.",
        "lire":       "Tri décroissant par valeur. Le rang entre parenthèses = position dans l'ensemble du secteur sénégalais.",
        "surveiller": "Un écart > 3× entre la 1ère et la dernière banque indique une forte hétérogénéité du marché.",
    },
    "cmp-evolution": {
        "titre":      "Évolution comparée",
        "mesure":     "Courbes temporelles superposées de l'indicateur sélectionné pour les banques choisies.",
        "lire":       "Les croisements de courbes sont particulièrement informatifs : ils marquent des changements de position relative.",
        "surveiller": "Une banque qui rattrape le leader en moins de 3 ans mérite une analyse de sa stratégie de croissance.",
    },

    # ── Ratios & Analyse ──────────────────────────────────────────────────────
    "rat-distribution": {
        "titre":      "Distribution ROA / ROE",
        "mesure":     "Box plot de la distribution du ratio sélectionné pour toutes les banques du secteur, par année.",
        "lire":       "La boîte = P25–P75. La ligne médiane = P50. Les moustaches = min/max hors valeurs aberrantes.",
        "surveiller": "Un écart interquartile large (boîte haute) signale une forte dispersion des performances dans le secteur.",
    },
    "rat-topflop": {
        "titre":      "Top & Flop 5",
        "mesure":     "Les 5 meilleures et les 5 moins bonnes banques sur le ratio sélectionné pour l'année en cours.",
        "lire":       "Barres vertes = top performers. Barres rouges = sous-performers. La ligne = médiane sectorielle.",
        "surveiller": "Les banques récurrentes dans le Flop 5 sur plusieurs indicateurs sont candidates à une surveillance renforcée.",
    },
    "rat-scatter": {
        "titre":      "Matrice risque × rentabilité",
        "mesure":     "Positionnement des banques sur 2 axes simultanés : un axe risque (NPL ou Tier 1 inversé) et un axe rentabilité (ROE ou ROA).",
        "lire":       "4 quadrants : idéal = bas risque + haute rentabilité (haut gauche). À éviter = haut risque + faible rentabilité.",
        "surveiller": "Les banques dans le quadrant haut risque / haute rentabilité prennent des risques potentiellement non soutenables.",
    },
    "rat-evolution": {
        "titre":      "Évolution médiane sectorielle",
        "mesure":     "Trajectoire de la médiane du ratio sélectionné sur l'ensemble du secteur sénégalais.",
        "lire":       "Courbe avec intervalle de confiance (P25–P75). L'élargissement de la bande = divergence croissante entre banques.",
        "surveiller": "Une médiane ROE sous 5% sur 2 ans consécutifs indique une compression structurelle de la rentabilité sectorielle.",
    },
    "rat-tableau": {
        "titre":      "Tableau synthèse — tous les ratios",
        "mesure":     "Vue tabulaire complète de tous les ratios financiers pour toutes les banques, triable par colonne.",
        "lire":       "Cliquer sur un en-tête de colonne pour trier. Les cellules colorées = déviation par rapport à la médiane.",
        "surveiller": "Trier par NPL pour identifier rapidement les banques avec des portefeuilles de crédit dégradés.",
    },

    # ── Benchmark ─────────────────────────────────────────────────────────────
    "bm-classement": {
        "titre":      "Positionnement dans le classement PNB",
        "mesure":     "Rang de la banque simulée dans le classement sectoriel selon son PNB estimé, comparé aux banques réelles.",
        "lire":       "La banque simulée apparaît en surbrillance. Les flèches indiquent combien de places elle gagne ou perd vs l'année précédente.",
        "surveiller": "Un rang dans le top 5 PNB avec un ROE faible suggère une structure de coûts inefficiente à corriger.",
    },
    "bm-allocation": {
        "titre":      "Allocation du bilan — groupe de référence",
        "mesure":     "Structure bilantielle typique des banques du même groupe de référence : crédits, titres, dépôts, fonds propres.",
        "lire":       "Barres empilées normalisées à 100%. La banque simulée est comparée à la médiane de son groupe.",
        "surveiller": "Un ratio crédits/dépôts > 90% peut indiquer un risque de liquidité si les dépôts se retirent rapidement.",
    },
    "bm-prediction": {
        "titre":      "Projection financière sur 3 ans",
        "mesure":     "Modèle de régression (Random Forest ou linéaire) entraîné sur les données historiques bancaires sénégalaises.",
        "lire":       "La courbe pleine = historique. La courbe pointillée = projection. L'intervalle de confiance = plage de scénarios.",
        "surveiller": "La fiabilité du modèle (R² affiché) doit être > 0.75 pour que les projections soient analytiquement exploitables.",
    },

    # ── Carte & Réseau ────────────────────────────────────────────────────────
    "carte-map": {
        "titre":      "Carte interactive du Sénégal",
        "mesure":     "Choroplèthe des 14 régions administratives du Sénégal colorées selon la métrique sélectionnée (PNB, agences, taux de bancarisation…).",
        "lire":       "Plus la région est foncée, plus la valeur est élevée. Cliquer sur une région pour voir le détail.",
        "surveiller": "Dakar concentre généralement > 70% du PNB bancaire — surveiller l'évolution des régions secondaires.",
    },
    "carte-reseau": {
        "titre":      "Réseau national des agences",
        "mesure":     "Distribution géographique des agences bancaires par région, avec ratio agences/habitant.",
        "lire":       "Barres groupées par groupe bancaire. La densité agences/habitant est l'indicateur clé d'accessibilité financière.",
        "surveiller": "Un ratio < 1 agence pour 50 000 habitants indique un sous-équipement bancaire de la région.",
    },
    "carte-bancarisation": {
        "titre":      "Taux de bancarisation par région",
        "mesure":     "Pourcentage de la population adulte ayant accès à un compte bancaire formel, par région administrative.",
        "lire":       "Barres horizontales. La ligne rouge = moyenne nationale. Les régions sous cette ligne sont sous-bancarisées.",
        "surveiller": "Les régions avec taux < 10% représentent les opportunités d'expansion prioritaires pour les banques.",
    },
    "carte-concentration": {
        "titre":      "Concentration géographique du PNB",
        "mesure":     "Part de chaque région dans le PNB bancaire total national. Mesure la dépendance géographique du secteur.",
        "lire":       "Donut chart : chaque arc = une région. L'indice de concentration (Herfindahl) est affiché au centre.",
        "surveiller": "Un indice HHI > 0.25 signale une concentration géographique excessive et un risque de fragilité régionale.",
    },

    # ── Structure & Opérationnel ──────────────────────────────────────────────
    "str-reseau-evol": {
        "titre":      "Évolution réseau & personnel",
        "mesure":     "Nombre d'agences et effectif total du groupe sélectionné, année par année.",
        "lire":       "Barres = agences (axe gauche). Courbe = effectif (axe droit). Un réseau qui croît sans effectif proportionnel gagne en productivité.",
        "surveiller": "Une baisse simultanée agences + effectif signale une restructuration ou une contraction stratégique du groupe.",
    },
    "str-comptes-groupe": {
        "titre":      "Volume de comptes par groupe bancaire",
        "mesure":     "Nombre total de comptes clients (en millions) détenus par chaque groupe bancaire pour l'année sélectionnée.",
        "lire":       "Barres horizontales triées par volume. Le pourcentage indique la part de marché comptes de chaque groupe.",
        "surveiller": "Un groupe Régional ou Local avec une part comptes > part bilan indique une clientèle de détail forte mais des bilans modestes.",
    },
    "str-capitalisation": {
        "titre":      "Capitalisation : Continentaux vs Régionaux",
        "mesure":     "Ratio Fonds Propres / Total Bilan (%) par groupe bancaire, sur la période 2015–2022. Mesure l'adéquation des fonds propres.",
        "lire":       "Courbes par groupe. La ligne rouge = seuil BCEAO 8%. Tout groupe sous ce seuil est en infraction réglementaire.",
        "surveiller": "Une convergence vers le seuil minimum (8%) des groupes régionaux indique une fragilisation progressive de leur capitalisation.",
    },
    "str-emploi": {
        "titre":      "Évolution de l'EMPLOI sectoriel",
        "mesure":     "EMPLOI = total des crédits accordés à la clientèle (en milliards FCFA). RESSOURCES = total des dépôts collectés.",
        "lire":       "La surface sous la courbe EMPLOI = volume de crédit octroyé. L'écart EMPLOI / RESSOURCES mesure le taux de transformation.",
        "surveiller": "Un taux de transformation (EMPLOI/RESSOURCES) > 90% est un signal de tension sur la liquidité sectorielle.",
    },
    "str-productivite": {
        "titre":      "Productivité du personnel",
        "mesure":     "COMPTE/EFFECTIF : nombre de comptes gérés par employé. BILAN/EFFECTIF : volume de bilan géré par employé (en millions FCFA).",
        "lire":       "Barres horizontales par banque. La ligne verticale = médiane sectorielle. Les banques à droite sont au-dessus de la moyenne.",
        "surveiller": "Une banque avec un ratio BILAN/EFFECTIF élevé mais un COMPTE/EFFECTIF faible opère sur des grands comptes corporate plutôt que retail.",
    },
    "str-scatter-agences": {
        "titre":      "Corrélation Agences vs Bilan",
        "mesure":     "Relation entre le nombre d'agences physiques et le total du bilan de chaque banque. La droite = régression linéaire.",
        "lire":       "Les points au-dessus de la droite ont un bilan supérieur à ce que prédit leur réseau (efficacité élevée). En-dessous = sous-performance relative.",
        "surveiller": "Un R² élevé (> 0.7) confirme que le réseau physique reste un déterminant fort du volume d'activité au Sénégal.",
    },
}
