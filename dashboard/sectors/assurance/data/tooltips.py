# ============================================================
#  sectors/assurance/data/tooltips.py
#  Contenus des tooltips pour toutes les pages assurance
# ============================================================

TOOLTIPS = {

    # ── Vue Portefeuille ──────────────────────────────────────
    "vm-evolution": {
        "titre":      "Évolution annuelle — Primes vs Sinistres",
        "mesure":     "Compare les primes collectées et les sinistres payés chaque année, avec le ratio S/P (Loss Ratio) sur l'axe secondaire.",
        "lire":       "Les barres vertes = primes encaissées. Les barres rouges = sinistres décaissés. La courbe dorée = ratio S/P en %. Un S/P < 100% signifie que les primes couvrent les sinistres.",
        "surveiller": "Un ratio S/P qui dépasse 100% signale une activité techniquement déficitaire. Surveiller la tendance sur 2–3 ans.",
    },
    "vm-donut-branche": {
        "titre":      "Répartition des primes par branche",
        "mesure":     "Poids de chaque branche (Auto, Santé, Vie, Habitation) dans le total des primes collectées.",
        "lire":       "Un portefeuille équilibré répartit le risque entre branches. La branche en surbrillance au centre est la plus importante.",
        "surveiller": "Une branche représentant plus de 50% du portefeuille crée une concentration de risque.",
    },
    "vm-sp-branche": {
        "titre":      "Ratio S/P par branche",
        "mesure":     "Le Loss Ratio (sinistres / primes × 100) mesure le coût des sinistres pour chaque euro de prime encaissé.",
        "lire":       "Vert < 70% : bonne rentabilité. Or 70–100% : acceptable. Rouge > 100% : la branche coûte plus qu'elle ne rapporte.",
        "surveiller": "Toute branche avec un S/P > 100% nécessite une révision tarifaire ou une politique de souscription plus stricte.",
    },
    "vm-sin-region": {
        "titre":      "Taux de sinistralité par région",
        "mesure":     "Part des contrats ayant déclaré au moins un sinistre dans chaque région.",
        "lire":       "Un taux élevé dans une région peut indiquer un risque géographique spécifique (accidents, catastrophes naturelles, fraude).",
        "surveiller": "Un écart > 10pts entre régions mérite une analyse approfondie des causes.",
    },
    "vm-bonus": {
        "titre":      "Distribution du bonus-malus",
        "mesure":     "Répartition des coefficients bonus-malus du portefeuille par branche. Le coefficient 1.0 est la référence neutre.",
        "lire":       "< 1.0 = assuré bonus (peu de sinistres). > 1.0 = assuré malus (sinistres fréquents). La largeur du violon indique la densité.",
        "surveiller": "Une distribution fortement décalée vers > 1.0 signale un portefeuille à risque élevé.",
    },
    "vm-heatmap": {
        "titre":      "Concentration sinistres — Branche × Région",
        "mesure":     "Pour chaque branche, montre comment les sinistres se répartissent entre les 4 régions (en % du total de la branche).",
        "lire":       "Une cellule foncée = forte concentration. Chaque ligne somme à 100%. Les valeurs en gras = nb de sinistres absolus.",
        "surveiller": "Une concentration > 40% dans une seule région pour une branche indique une dépendance géographique risquée.",
    },

    # ── Analyse Sinistres ─────────────────────────────────────
    "sin-freq-sev": {
        "titre":      "Fréquence vs Sévérité",
        "mesure":     "Positionne chaque branche selon deux axes : fréquence (% de contrats sinistrés) et sévérité (montant moyen des sinistres). La taille de la bulle = coût total.",
        "lire":       "Idéal : bulle en bas à gauche (faible fréquence ET faible sévérité). Les quadrants permettent de classer les risques.",
        "surveiller": "Une branche en haut à droite (haute fréquence + haute sévérité) est la plus coûteuse à gérer.",
    },
    "sin-distrib": {
        "titre":      "Distribution des montants sinistres",
        "mesure":     "Histogramme de fréquence des montants de sinistres avec les percentiles P50 (médiane), P75 et P90.",
        "lire":       "La médiane = montant en dessous duquel se trouvent 50% des sinistres. P90 = 10% des sinistres les plus élevés.",
        "surveiller": "Un P90 très éloigné de la médiane indique une forte présence de sinistres extrêmes (queue de distribution lourde).",
    },
    "sin-nb-sin": {
        "titre":      "Répartition par nombre de sinistres",
        "mesure":     "Nombre de contrats selon qu'ils ont déclaré 0, 1, 2, 3 ou 4 sinistres sur la période.",
        "lire":       "La majorité des contrats devraient être en 0 sinistre. Plus la barre de 0 est haute, plus le portefeuille est sain.",
        "surveiller": "Des contrats avec 3+ sinistres représentent un coût disproportionné — envisager une révision ou résiliation.",
    },
    "sin-age": {
        "titre":      "Fréquence & sévérité par tranche d'âge",
        "mesure":     "Croise fréquence de sinistres (barres) et sévérité moyenne (courbe) par tranche d'âge.",
        "lire":       "Barres = % de contrats sinistrés. Courbe rouge = montant moyen du sinistre. Deux axes indépendants.",
        "surveiller": "Les tranches avec fréquence ET sévérité élevées sont les plus coûteuses à assurer.",
    },
    "sin-region-branche": {
        "titre":      "Coût sinistres par région et branche",
        "mesure":     "Coût total des sinistres par région, décomposé par branche (barres empilées), avec la fréquence en overlay.",
        "lire":       "La hauteur totale de la barre = coût total de la région. Les couleurs = branches. La ligne blanche = fréquence.",
        "surveiller": "Une région avec un coût élevé ET une fréquence élevée concentre le risque le plus important.",
    },
    "sin-top-contrats": {
        "titre":      "Top 15 contrats — Montant sinistres",
        "mesure":     "Liste les 15 contrats avec les montants de sinistres les plus élevés du portefeuille filtré.",
        "lire":       "Couleur = branche. Survol pour voir l'âge, bonus-malus, nb sinistres et prime. Ce sont les contrats les plus déficitaires.",
        "surveiller": "Si plusieurs contrats du top 15 ont un bonus-malus > 1.3 et des sinistres élevés, la politique de malus est insuffisante.",
    },

    # ── Profil Assuré ─────────────────────────────────────────
    "profil-pyramide": {
        "titre":      "Pyramide des âges par sexe",
        "mesure":     "Distribution de l'âge des assurés par tranches de 5 ans, séparée hommes (gauche) et femmes (droite).",
        "lire":       "Plus la barre est longue, plus cette tranche est représentée. L'axe central = 0. Lecture symétrique.",
        "surveiller": "Un portefeuille très concentré sur les 60+ ans peut anticiper une hausse de la sinistralité santé/vie.",
    },
    "profil-branche-sexe": {
        "titre":      "Portefeuille branche × sexe",
        "mesure":     "Nombre de contrats par branche, ventilé par sexe (hommes vs femmes), avec prime moyenne en tooltip.",
        "lire":       "Barres pleines = hommes. Barres hachurées = femmes. Hauteur = nombre de contrats.",
        "surveiller": "Un déséquilibre fort H/F dans une branche peut biaiser les statistiques de sinistralité.",
    },
    "profil-region": {
        "titre":      "Répartition géographique",
        "mesure":     "Part de chaque région dans le portefeuille total de contrats.",
        "lire":       "La région centrale du donut = région dominante avec son % de part. Survol pour la prime et fréquence moyennes.",
        "surveiller": "Une région représentant plus de 40% du portefeuille crée une dépendance à un marché local.",
    },
    "profil-fidelite": {
        "titre":      "Fidélité — sinistralité selon durée",
        "mesure":     "Croise la durée du contrat (1 à 10 ans) avec la fréquence de sinistres (rouge) et le bonus-malus moyen (vert).",
        "lire":       "Les barres grises = nb contrats. La courbe rouge = fréquence sinistres. La courbe verte pointillée = bonus-malus.",
        "surveiller": "Une fréquence de sinistres qui repart à la hausse après plusieurs années peut indiquer de l'anti-sélection.",
    },
    "profil-bm-age": {
        "titre":      "Bonus-malus par tranche d'âge",
        "mesure":     "Distribution des coefficients bonus-malus pour chaque tranche d'âge, séparée par sexe (box plots).",
        "lire":       "La boîte = 25e–75e percentile. La ligne centrale = médiane. Les moustaches = étendue. La ligne en pointillés = référence 1.0.",
        "surveiller": "Une médiane significativement > 1.0 pour une tranche indique des assurés structurellement malus.",
    },
    "profil-heatmap": {
        "titre":      "Concentration du portefeuille — Âge × Région",
        "mesure":     "Nombre de contrats (et %) pour chaque combinaison tranche d'âge × région.",
        "lire":       "Couleur plus foncée = plus de contrats. Les valeurs = nb absolu + % du total portefeuille.",
        "surveiller": "Une cellule très dense peut amplifier l'impact d'un événement régional (catastrophe, épidémie) sur ce segment.",
    },

    # ── Rentabilité ───────────────────────────────────────────
    "rent-waterfall": {
        "titre":      "Combined Ratio — décomposition",
        "mesure":     "Décompose le Combined Ratio en partant de 100% (primes) et en soustrayant le Loss Ratio puis l'Expense Ratio.",
        "lire":       "Partant de 100%, chaque barre rouge = coût. Si le total dépasse 100%, la branche est techniquement déficitaire.",
        "surveiller": "Un Combined Ratio > 100% signifie que l'assureur perd de l'argent sur son activité technique pure.",
    },
    "rent-lr-branche": {
        "titre":      "Loss Ratio par branche",
        "mesure":     "Ratio sinistres/primes pour chaque branche, avec le Combined Ratio (LR + ER) marqué en losange blanc.",
        "lire":       "Vert < 70% = très rentable. Or 70–100% = équilibré. Rouge > 100% = déficitaire. Le losange = combined ratio.",
        "surveiller": "Une branche avec LR > 100% doit faire l'objet d'une revue tarifaire immédiate.",
    },
    "rent-cr-region": {
        "titre":      "Combined Ratio par région",
        "mesure":     "Décomposition barres empilées du Combined Ratio (Loss + Expense) pour chaque région.",
        "lire":       "Chaque barre = LR (rouge) + ER fixe (gris). La ligne dorée verticale = seuil d'équilibre à 100%.",
        "surveiller": "Les régions à droite de la ligne dorée sont structurellement déficitaires.",
    },
    "rent-evolution": {
        "titre":      "Évolution LR & CR annuels",
        "mesure":     "Suivi de l'évolution du Loss Ratio et Combined Ratio année par année, avec la zone Expense Ratio entre les deux courbes.",
        "lire":       "La zone grise entre les deux courbes = Expense Ratio constant. La flèche en haut à droite = tendance sur la période.",
        "surveiller": "Une courbe ascendante sur 2+ années consécutives est un signal fort de dégradation structurelle.",
    },
    "rent-scatter": {
        "titre":      "Prime collectée vs Sinistre payé",
        "mesure":     "Nuage de points : chaque point = un contrat. Axe X = prime, axe Y = sinistre. La diagonale = équilibre (prime = sinistre).",
        "lire":       "Points sous la diagonale = contrats rentables (prime > sinistre). Points au-dessus = contrats déficitaires.",
        "surveiller": "Si la majorité des points est au-dessus de la diagonale, le portefeuille est globalement déficitaire.",
    },
    "rent-bm-lr": {
        "titre":      "Bonus-malus vs Loss Ratio",
        "mesure":     "Loss Ratio moyen par tranche de coefficient bonus-malus (0.5–0.75 / 0.75–1.0 / 1.0–1.25 / 1.25–1.5).",
        "lire":       "Un bon système de bonus-malus devrait montrer une corrélation positive : plus le BM est élevé, plus le LR est élevé.",
        "surveiller": "Si les tranches BM élevées ont un LR similaire aux tranches basses, le système tarifaire est inefficace.",
    },
    "rent-prime-pure": {
        "titre":      "Prime pure vs Prime commerciale",
        "mesure":     "Décompose la prime commerciale moyenne en prime pure (coût du risque = fréquence × sévérité) et chargement (frais + marge).",
        "lire":       "Rouge = prime pure (coût réel du risque). Vert = chargement (frais de gestion + profit). Le % annoté = taux de chargement.",
        "surveiller": "Un taux de chargement < 15% peut indiquer une sous-tarification. Un taux > 40% peut être non-compétitif.",
    },

    # ── Scoring ───────────────────────────────────────────────
    "scor-distrib": {
        "titre":      "Distribution des scores de risque",
        "mesure":     "Histogramme de la distribution des scores prédits par le modèle Random Forest pour tout le portefeuille.",
        "lire":       "Score proche de 0 = risque faible. Score proche de 1 = risque élevé. Les lignes verticales = coupures de quintiles.",
        "surveiller": "Une distribution très concentrée autour de 0.5 indique un modèle peu discriminant.",
    },
    "scor-importance": {
        "titre":      "Importance des variables (Random Forest)",
        "mesure":     "Contribution de chaque variable à la prédiction du modèle, calculée par impureté de Gini sur 100 arbres.",
        "lire":       "Plus la barre est longue, plus la variable influence le score. La somme des importances = 1.",
        "surveiller": "Si une seule variable domine à > 50%, le modèle est fragile et dépendant de cette seule information.",
    },
    "scor-roc": {
        "titre":      "Courbe ROC",
        "mesure":     "Courbe Receiver Operating Characteristic : mesure la capacité du modèle à distinguer sinistrés vs non-sinistrés.",
        "lire":       "AUC = 0.5 : modèle aléatoire (diagonale). AUC = 1.0 : modèle parfait. La courbe bleue doit être au-dessus de la diagonale.",
        "surveiller": "AUC < 0.6 = modèle peu utile. AUC > 0.7 = bon modèle. AUC > 0.8 = très bon modèle.",
    },
    "scor-segments": {
        "titre":      "Calibration — Fréquence réelle vs score",
        "mesure":     "Valide le modèle en comparant la fréquence réelle de sinistres (barres) au score prédit moyen (courbe) par segment.",
        "lire":       "Si les barres et la courbe suivent la même tendance croissante, le modèle est bien calibré.",
        "surveiller": "Un écart important entre barres et courbe sur un segment indique un problème de calibration pour ce groupe.",
    },
    "scor-heatmap": {
        "titre":      "Score moyen — Branche × Région",
        "mesure":     "Score de risque moyen prédit par le modèle pour chaque combinaison branche × région.",
        "lire":       "Vert = faible risque moyen. Rouge = risque élevé. Permet d'identifier les segments les plus risqués.",
        "surveiller": "Les cellules rouges (score > 0.5) indiquent des segments à surveiller ou à sur-tarifer.",
    },
}
