TOOLTIPS = {
    # Vue Globale
    "vg-yield-pays": {
        "titre":      "Production totale par pays",
        "mesure":     "Énergie cumulée produite (Daily Yield) sur l'année entière pour chaque pays.",
        "lire":       "Barres horizontales triées. Plus la barre est longue, plus le pays produit d'énergie solaire annuellement.",
        "surveiller": "L'écart entre Norway et Brazil reflète directement la différence d'ensoleillement entre les deux pays.",
    },
    "vg-evolution": {
        "titre":      "Évolution mensuelle de la production",
        "mesure":     "Puissance DC moyenne par mois et par pays. Montre la saisonnalité de la production solaire.",
        "lire":       "Chaque courbe = un pays. Les pics correspondent aux mois les plus ensoleillés selon l'hémisphère.",
        "surveiller": "Norway et Australia ont des profils inversés — hémisphères nord et sud.",
    },
    "vg-efficacite": {
        "titre":      "Rendement DC → AC par pays",
        "mesure":     "Efficacité de conversion des panneaux solaires : énergie AC produite / énergie DC captée × 100.",
        "lire":       "Un rendement > 90% est excellent. La perte (~10%) est due aux onduleurs et câblages.",
        "surveiller": "Un rendement qui baisse dans le temps peut indiquer un vieillissement des panneaux.",
    },
    "vg-irradiation": {
        "titre":      "Irradiation moyenne par pays et mois",
        "mesure":     "Quantité d'énergie solaire reçue (W/m²) par les panneaux, par pays et par mois.",
        "lire":       "Plus la cellule est foncée, plus l'irradiation est forte. Corrélation directe avec la production.",
        "surveiller": "Brazil et India affichent les irradiations les plus élevées — meilleur potentiel solaire.",
    },
    # Temporelle
    "tmp-heatmap": {
        "titre":      "Heatmap production — Heure × Mois",
        "mesure":     "Puissance DC moyenne pour chaque combinaison heure de la journée × mois de l'année.",
        "lire":       "Axe Y = heure (0–23h). Axe X = mois. Zone jaune/orange = forte production. Bleu = faible.",
        "surveiller": "La plage productive est typiquement 8h–17h. Les mois d'été montrent une plage plus large.",
    },
    "tmp-courbe-journaliere": {
        "titre":      "Profil journalier moyen",
        "mesure":     "Puissance DC moyenne heure par heure, pour chaque pays. Montre la courbe solaire typique.",
        "lire":       "Courbe en cloche avec pic à midi. La largeur de la courbe = durée d'ensoleillement quotidien.",
        "surveiller": "Norway a une courbe plus étroite (jours courts en hiver), Brazil plus plate (ensoleillement stable).",
    },
    "tmp-saisonnalite": {
        "titre":      "Saisonnalité — Production par saison",
        "mesure":     "Production moyenne par saison (Printemps/Été/Automne/Hiver) pour chaque pays.",
        "lire":       "Barres groupées par saison. L'Été = saison de pointe dans l'hémisphère nord.",
        "surveiller": "Australia a son pic en hiver calendaire (= été austral). Profil inverse des pays nordiques.",
    },
    "tmp-daily-yield": {
        "titre":      "Distribution du rendement journalier",
        "mesure":     "Histogramme des valeurs Daily Yield — énergie produite chaque jour par panneau.",
        "lire":       "Pic à gauche = nombreux jours faibles (nuit, nuages). Queue à droite = jours ensoleillés.",
        "surveiller": "Une distribution très étalée indique une forte variabilité météo (ex : Norway).",
    },
    # Performance
    "perf-scatter": {
        "titre":      "Irradiation vs Puissance DC",
        "mesure":     "Corrélation entre l'irradiation solaire reçue et la puissance DC produite.",
        "lire":       "Chaque point = une mesure horaire. La droite de régression montre la relation linéaire.",
        "surveiller": "Des points loin de la droite = anomalies (ombrage, panne, météo exceptionnelle).",
    },
    "perf-rendement-heure": {
        "titre":      "Rendement DC→AC par tranche horaire",
        "mesure":     "Efficacité moyenne de conversion selon l'heure de la journée.",
        "lire":       "Le rendement est plus faible aux extrémités de la journée (faible irradiation, seuils d'onduleur).",
        "surveiller": "Un rendement < 85% en milieu de journée est anormal et mérite investigation.",
    },
    "perf-pertes": {
        "titre":      "Pertes de conversion par pays",
        "mesure":     "Différence entre puissance DC captée et puissance AC injectée (DC − AC = pertes).",
        "lire":       "Barres empilées : vert = AC utilisable, rouge = pertes onduleur. % annoté = taux de perte.",
        "surveiller": "Des pertes > 15% sont excessives et indiquent un problème d'onduleur ou de câblage.",
    },
    "perf-pic-production": {
        "titre":      "Heures de pointe par pays",
        "mesure":     "Distribution de la production horaire — quelles heures concentrent le plus d'énergie.",
        "lire":       "Box plots par pays. La médiane = heure typique de mi-production. Queue = variabilité.",
        "surveiller": "Des pics décalés entre pays reflètent les fuseaux horaires et latitudes différents.",
    },
    # Climatique
    "clim-temp-rendement": {
        "titre":      "Température module vs Rendement",
        "mesure":     "Corrélation entre la température du panneau et l'efficacité DC→AC.",
        "lire":       "Les panneaux solaires perdent en efficacité quand ils chauffent trop (coeff. ~0.4%/°C).",
        "surveiller": "Au-delà de 45°C, les pertes thermiques deviennent significatives.",
    },
    "clim-distribution-temp": {
        "titre":      "Distribution des températures par pays",
        "mesure":     "Box plots de la température ambiante et du module pour chaque pays.",
        "lire":       "La boîte = P25–P75. Les moustaches = étendue. Les points = valeurs extrêmes.",
        "surveiller": "Norway affiche les températures les plus basses, India les plus élevées.",
    },
    "clim-heatmap-temp": {
        "titre":      "Température ambiante — Heure × Mois",
        "mesure":     "Température ambiante moyenne pour chaque heure et chaque mois de l'année.",
        "lire":       "Montre les cycles thermiques journaliers et saisonniers. Utile pour anticiper les pertes.",
        "surveiller": "Les cellules très chaudes (été + après-midi) correspondent aux plus fortes pertes thermiques.",
    },
    "clim-irr-temp": {
        "titre":      "Irradiation vs Température module",
        "mesure":     "Relation entre l'ensoleillement et l'échauffement des panneaux solaires.",
        "lire":       "Corrélation attendue positive : plus il fait soleil, plus les panneaux chauffent.",
        "surveiller": "Des températures très élevées pour une faible irradiation = problème de refroidissement.",
    },
    # Comparaison
    "cmp-radar": {
        "titre":      "Radar multicritères — 4 pays",
        "mesure":     "Compare les 4 pays sur 5 dimensions normalisées : production, rendement, irradiation, température, variabilité.",
        "lire":       "Plus la surface couverte est grande, plus le pays performe globalement. Chaque axe = 0 à 100.",
        "surveiller": "Aucun pays n'est optimal sur tous les axes — chacun a ses forces et faiblesses.",
    },
    "cmp-classement": {
        "titre":      "Classement des pays par KPI",
        "mesure":     "Tableau de bord comparatif : production totale, rendement, irradiation, température moy.",
        "lire":       "Chaque ligne = un pays. Les barres de progression montrent le score relatif au meilleur.",
        "surveiller": "Brazil domine en production totale. Norway est le moins productif mais le plus froid.",
    },
    "cmp-profils": {
        "titre":      "Profils de production normalisés",
        "mesure":     "Courbes journalières moyennes normalisées (0–100%) pour comparer la forme de production.",
        "lire":       "Normaliser permet de comparer la forme sans l'effet d'échelle de la production absolue.",
        "surveiller": "Des profils très différents indiquent des conditions d'ensoleillement distinctes.",
    },
    "cmp-mensuel": {
        "titre":      "Production mensuelle comparative",
        "mesure":     "Barres groupées de production mensuelle pour les 4 pays sur 12 mois.",
        "lire":       "Permet de voir quel pays performe le mieux chaque mois et la saisonnalité comparative.",
        "surveiller": "Les croisements de courbes entre Norway et Australia reflètent l'inversion saisonnière.",
    },

    # Anomalies
    "ano-serie": {
        "titre":      "Série temporelle DC avec zones anormales",
        "mesure":     "Production DC heure par heure sur l'année. Les zones rouges = anomalies détectées (DC=0 avec irradiation > 0.05 W/m²).",
        "lire":       "Courbe bleue = production réelle. Zones rouges surlignées = pannes ou capteurs défaillants pendant des heures normalement productives.",
        "surveiller": "Des anomalies groupées sur plusieurs heures consécutives indiquent une panne matérielle, pas juste une mesure aberrante.",
    },
    "ano-ecart": {
        "titre":      "Écart DC réel vs DC théorique",
        "mesure":     "Différence entre la puissance DC mesurée et la puissance théorique calculée depuis l'irradiation (modèle linéaire : DC = 62×Irr − 0.67).",
        "lire":       "Valeur positive = sur-performance. Valeur négative = sous-performance. La ligne 0 = comportement attendu.",
        "surveiller": "Des écarts systématiquement négatifs (−20% ou plus) sur un pays signalent une dégradation des panneaux ou un problème de calibration.",
    },
    "ano-heatmap": {
        "titre":      "Carte des anomalies — Heure × Mois",
        "mesure":     "Nombre d'anomalies (DC=0, Irr>0.05) détectées pour chaque combinaison heure × mois.",
        "lire":       "Les cellules colorées pendant les heures solaires (8h–17h) sont les plus critiques. Plus la cellule est foncée, plus les anomalies sont fréquentes.",
        "surveiller": "Une concentration d'anomalies sur un mois précis peut indiquer une maintenance ou un événement météo exceptionnel.",
    },
    "ano-top": {
        "titre":      "Top anomalies par pays et mois",
        "mesure":     "Nombre total d'heures anormales (DC nul avec ensoleillement) par pays, décomposé par mois.",
        "lire":       "Barres empilées : chaque couleur = un mois. La hauteur totale = nb d'heures perdues sur l'année.",
        "surveiller": "Brazil affiche le plus d'anomalies. Si un mois domine nettement, investiguer les conditions de ce mois.",
    },

    # Anomalies & Qualité
    "ano-serie": {
        "titre":      "Série temporelle DC avec zones anormales",
        "mesure":     "Production DC heure par heure. Zones rouges = anomalies (DC=0 avec irradiation > 0.05).",
        "lire":       "Courbe = production réelle. Zones rouges = pannes ou capteurs défaillants en heures productives.",
        "surveiller": "Anomalies groupées sur plusieurs heures consecutives indiquent une panne materielle.",
    },
    "ano-ecart": {
        "titre":      "Ecart DC reel vs DC theorique",
        "mesure":     "Difference entre DC mesure et DC theorique (62 x Irradiation). Positif = sur-performance.",
        "lire":       "Distribution par pays. La ligne 0 = comportement attendu par le modele.",
        "surveiller": "Mediane negative a -20% ou plus signale une degradation des panneaux.",
    },
    "ano-heatmap": {
        "titre":      "Carte des anomalies Heure x Mois",
        "mesure":     "Nombre d anomalies detectees par heure et par mois pour le pays selectionne.",
        "lire":       "Cellules colorees entre 8h et 17h sont critiques. Plus fonce = plus frequent.",
        "surveiller": "Concentration sur un mois = maintenance ou evenement meteo exceptionnel.",
    },
    "ano-top": {
        "titre":      "Heures perdues par pays et mois",
        "mesure":     "Nombre d heures de production nulle anormale par pays, decompose par mois.",
        "lire":       "Barres empilees par mois. Hauteur totale = heures perdues sur l annee.",
        "surveiller": "Si un mois domine nettement sur un pays, investiguer les conditions de cette periode.",
    },
}
