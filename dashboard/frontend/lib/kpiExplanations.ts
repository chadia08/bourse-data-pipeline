export interface KPIExplanation {
  title: string;
  description: string;
  interpretation: {
    good: string;
    neutral?: string;
    bad: string;
  };
  example: string;
  disclaimer: string;
}

export const kpiExplanations: Record<string, KPIExplanation> = {
  // ==========================================
  // INDICATEURS DE TRADING
  // ==========================================
  
  variation: {
    title: "Variation du Prix",
    description: "Montre si le prix de l'action a monté (vert) ou baissé (rouge) aujourd'hui par rapport à hier.",
    interpretation: {
      good: "🟢 Positif (+2%) : L'action gagne de la valeur aujourd'hui",
      neutral: "⚪ Neutre (0%) : Le prix n'a pas bougé",
      bad: "🔴 Négatif (-3%) : L'action perd de la valeur aujourd'hui"
    },
    example: "Si une action valait 100€ hier et vaut 105€ aujourd'hui, la variation est de +5%.",
    disclaimer: "Cette information ne constitue pas un conseil d'investissement. Une hausse passée ne garantit pas une hausse future."
  },

  rsi: {
    title: "RSI (Force du Mouvement)",
    description: "Indique si une action est \"trop achetée\" ou \"trop vendue\". C'est comme un thermomètre du prix : au-dessus de 70°, c'est chaud (peut baisser), en-dessous de 30°, c'est froid (peut remonter).",
    interpretation: {
      good: "🟢 RSI < 30 : L'action est peut-être sous-évaluée (opportunité potentielle)",
      neutral: "⚪ RSI entre 30 et 70 : Zone normale, pas de signal clair",
      bad: "🔴 RSI > 70 : L'action est peut-être surévaluée (prudence recommandée)"
    },
    example: "RSI à 25 → Beaucoup ont vendu, le prix est bas, possible rebond à venir.",
    disclaimer: "Cet indicateur est une aide à l'analyse, pas une garantie. Consultez plusieurs sources avant toute décision."
  },

  macd: {
    title: "MACD (Direction de la Tendance)",
    description: "Montre si la tendance du prix est à la hausse ou à la baisse. C'est comme une boussole qui indique la direction du marché.",
    interpretation: {
      good: "🟢 MACD positif : La tendance est à la hausse",
      bad: "🔴 MACD négatif : La tendance est à la baisse"
    },
    example: "Quand le MACD passe de négatif à positif, c'est souvent le début d'une remontée.",
    disclaimer: "Les tendances passées ne garantissent pas les résultats futurs. Ceci n'est pas un conseil d'achat ou de vente."
  },

  bollinger: {
    title: "Bandes de Bollinger (Zone de Prix Normal)",
    description: "Imagine une route avec des bordures. Quand le prix sort de la route, il revient souvent vers le centre. Cela aide à voir si un prix est anormalement haut ou bas.",
    interpretation: {
      good: "🟢 En-dessous de la bande : Le prix est très bas, peut remonter",
      neutral: "⚪ Entre les bandes : Prix dans la normale",
      bad: "🔴 Au-dessus de la bande : Le prix est très haut, peut redescendre"
    },
    example: "Si le prix touche la bordure basse, c'est comme un rebond sur un mur : il peut repartir vers le haut.",
    disclaimer: "Indicateur d'aide à la décision uniquement. Ne remplace pas une analyse complète."
  },

  volumeRelatif: {
    title: "Volume Relatif (Niveau d'Activité)",
    description: "Montre si beaucoup de gens achètent/vendent l'action aujourd'hui comparé à d'habitude. Plus le nombre est élevé, plus l'activité est importante.",
    interpretation: {
      good: "🟢 Volume > 2.0 : Beaucoup d'activité, mouvement de prix fiable",
      neutral: "⚪ Volume entre 0.8 et 1.5 : Activité normale",
      bad: "🔴 Volume < 0.5 : Peu d'activité, mouvement peu fiable"
    },
    example: "Si le volume relatif est à 3.5, cela veut dire qu'il y a 3.5 fois plus d'échanges que d'habitude.",
    disclaimer: "Un volume élevé confirme un mouvement mais ne garantit pas sa direction. Aide à l'analyse uniquement."
  },

  signal: {
    title: "Signal de Trading",
    description: "Notre système analyse plusieurs indicateurs et donne une suggestion : Achat (l'action pourrait monter), Vente (pourrait baisser), ou Neutre (pas de signal clair).",
    interpretation: {
      good: "🟢 Achat : Les indicateurs suggèrent une possible hausse",
      neutral: "⚪ Neutre : Aucun signal clair",
      bad: "🔴 Vente : Les indicateurs suggèrent une possible baisse"
    },
    example: "Un signal 'Achat' avec une force de 8/10 signifie que plusieurs indicateurs pointent vers une hausse.",
    disclaimer: "⚠️ IMPORTANT : Ceci n'est PAS un conseil d'investissement. C'est une aide à l'analyse. Faites vos propres recherches."
  },

  force: {
    title: "Force du Signal",
    description: "Note de 0 à 10 qui indique à quel point notre système est \"sûr\" de son signal. Plus le chiffre est élevé, plus les indicateurs sont d'accord entre eux.",
    interpretation: {
      good: "🟢 Force > 7 : Signal fort, plusieurs indicateurs concordent",
      neutral: "⚪ Force 4-7 : Signal modéré",
      bad: "🔴 Force < 4 : Signal faible, peu d'indicateurs concordent"
    },
    example: "Force de 9/10 sur un signal Achat = beaucoup d'indicateurs techniques suggèrent une hausse.",
    disclaimer: "Une force élevée n'est pas une garantie. Les marchés sont imprévisibles. Aide à la décision uniquement."
  },

  confiance: {
    title: "Niveau de Confiance",
    description: "Mesure la fiabilité du signal en fonction de l'historique récent de l'action. Plus c'est élevé, plus le signal a de chances d'être pertinent.",
    interpretation: {
      good: "🟢 Confiance > 70% : Signal historiquement fiable",
      neutral: "⚪ Confiance 50-70% : Fiabilité moyenne",
      bad: "🔴 Confiance < 50% : Signal incertain"
    },
    example: "85% de confiance signifie que dans le passé, ce type de signal était correct 85% du temps pour cette action.",
    disclaimer: "Les performances passées ne préjugent pas des performances futures. Ne constitue pas un conseil financier."
  },

  // ==========================================
  // INDICATEURS D'INVESTISSEMENT
  // ==========================================

  roe: {
    title: "ROE - Rentabilité de l'Entreprise",
    description: "Montre combien l'entreprise gagne pour chaque euro investi par les actionnaires. Plus c'est élevé, mieux elle utilise l'argent.",
    interpretation: {
      good: "🟢 ROE > 20% : Entreprise très rentable (excellent)",
      neutral: "⚪ ROE 10-20% : Rentabilité correcte",
      bad: "🔴 ROE < 10% : Faible rentabilité"
    },
    example: "ROE de 25% = pour chaque 100€ investis, l'entreprise génère 25€ de profit par an.",
    disclaimer: "Indicateur de performance passée. Ne garantit pas les résultats futurs. Aide à l'évaluation uniquement."
  },

  marge: {
    title: "Marge Bénéficiaire",
    description: "Montre quel pourcentage des ventes devient du profit. C'est comme si sur 100€ de ventes, combien reste après avoir payé toutes les dépenses.",
    interpretation: {
      good: "🟢 Marge > 20% : Entreprise très profitable",
      neutral: "⚪ Marge 10-20% : Profitabilité correcte",
      bad: "🔴 Marge < 5% : Faible profitabilité"
    },
    example: "Marge de 15% = sur 100€ de ventes, l'entreprise garde 15€ de profit net.",
    disclaimer: "Varie selon les secteurs. Une marge faible n'est pas forcément mauvaise (exemple : supermarchés). Aide à la comparaison."
  },

  dette: {
    title: "Ratio d'Endettement",
    description: "Compare les dettes de l'entreprise à ses fonds propres. Plus le chiffre est bas, moins l'entreprise est endettée (c'est mieux en général).",
    interpretation: {
      good: "🟢 Dette < 0.5 : Peu endettée, situation saine",
      neutral: "⚪ Dette 0.5-1.5 : Endettement modéré",
      bad: "🔴 Dette > 2.0 : Fortement endettée, risque plus élevé"
    },
    example: "Dette de 0.3 = l'entreprise doit 30€ pour chaque 100€ qu'elle possède. C'est peu, donc rassurant.",
    disclaimer: "Un endettement élevé n'est pas toujours mauvais si l'entreprise investit dans sa croissance. Aide à l'évaluation du risque."
  },

  dividendes: {
    title: "Rendement du Dividende",
    description: "Montre combien l'entreprise verse d'argent chaque année aux actionnaires, comparé au prix de l'action. C'est comme un \"loyer\" que l'action vous paie.",
    interpretation: {
      good: "🟢 Dividende > 4% : Revenus réguliers intéressants",
      neutral: "⚪ Dividende 2-4% : Revenus modérés",
      bad: "🔴 Dividende < 1% : Peu ou pas de revenus réguliers"
    },
    example: "Dividende de 5% = si vous achetez une action à 100€, vous recevez environ 5€ par an en dividendes.",
    disclaimer: "Les dividendes peuvent être réduits ou supprimés. Performances passées non garanties. Aide à l'évaluation uniquement."
  },

  cagr: {
    title: "CAGR - Croissance Annuelle",
    description: "Montre de combien le prix de l'action a augmenté en moyenne chaque année sur les dernières années. C'est comme un taux d'intérêt composé.",
    interpretation: {
      good: "🟢 CAGR > 15% : Croissance exceptionnelle",
      neutral: "⚪ CAGR 5-15% : Croissance correcte",
      bad: "🔴 CAGR < 5% : Croissance faible"
    },
    example: "CAGR de 20% sur 5 ans = 10 000€ investis en 2019 valent environ 24 883€ en 2024.",
    disclaimer: "Les performances passées ne garantissent pas les performances futures. Aide à évaluer l'historique uniquement."
  },

  score: {
    title: "Score de Solidité Financière",
    description: "Note globale de 0 à 100 qui combine plusieurs critères : rentabilité, endettement, croissance, liquidité. Plus c'est élevé, plus l'entreprise semble solide.",
    interpretation: {
      good: "🟢 Score > 80 : Entreprise très solide financièrement",
      neutral: "⚪ Score 60-80 : Situation financière correcte",
      bad: "🔴 Score < 40 : Situation financière fragile"
    },
    example: "Score de 92/100 = l'entreprise est rentable, peu endettée, et en croissance. Bon signe de santé financière.",
    disclaimer: "Score basé sur des données historiques. Ne garantit pas la stabilité future. Complétez avec votre propre analyse."
  },

  // ==========================================
  // INDICATEURS DE PRIX
  // ==========================================

  prix: {
    title: "Prix Actuel",
    description: "Le prix auquel l'action se négocie en ce moment sur le marché.",
    interpretation: {
      good: "Le prix seul ne dit rien. Il faut le comparer à d'autres indicateurs.",
      bad: "Un prix élevé ne veut pas dire que c'est cher, ni qu'un prix bas est une bonne affaire."
    },
    example: "Une action à 500€ peut être moins chère qu'une action à 50€, selon la valeur de l'entreprise.",
    disclaimer: "Prix indicatif. Peut varier rapidement. Complétez avec d'autres analyses avant toute décision."
  },

  volatilite: {
    title: "Volatilité (Amplitude des Variations)",
    description: "Mesure à quel point le prix de l'action bouge beaucoup. Plus c'est élevé, plus le prix peut faire de grands sauts (à la hausse ou à la baisse).",
    interpretation: {
      good: "🟢 Volatilité < 2% : Prix stable, risque plus faible",
      neutral: "⚪ Volatilité 2-4% : Mouvements normaux",
      bad: "🔴 Volatilité > 5% : Prix très variable, risque plus élevé"
    },
    example: "Volatilité de 8% = le prix peut varier de ±8% fréquemment. Risqué mais potentiellement plus profitable.",
    disclaimer: "Une forte volatilité = plus de risque ET plus d'opportunités. À évaluer selon votre tolérance au risque."
  },

  secteur: {
    title: "Secteur d'Activité",
    description: "Le domaine dans lequel l'entreprise travaille (technologie, banque, santé, etc.). Chaque secteur a ses propres caractéristiques.",
    interpretation: {
      good: "Certains secteurs sont plus stables (alimentaire), d'autres plus volatils (tech)",
      neutral: "Il n'y a pas de \"bon\" ou \"mauvais\" secteur, cela dépend de vos objectifs",
      bad: "Diversifiez vos investissements entre plusieurs secteurs pour réduire le risque"
    },
    example: "Le secteur technologique peut offrir de fortes croissances, mais avec plus de volatilité.",
    disclaimer: "Le secteur influence la performance mais ne la garantit pas. Analysez chaque entreprise individuellement."
  },

  // ==========================================
  // PRÉDICTIONS ML
  // ==========================================

  prediction: {
    title: "Prédiction de Prix (Intelligence Artificielle)",
    description: "Notre système utilise l'historique des prix pour estimer où le prix pourrait aller dans les prochains jours. C'est une projection, pas une certitude.",
    interpretation: {
      good: "🟢 Tendance haussière prédite : Le modèle anticipe une hausse possible",
      neutral: "⚪ Tendance stable : Peu de mouvement prévu",
      bad: "🔴 Tendance baissière prédite : Le modèle anticipe une baisse possible"
    },
    example: "Si le modèle prédit 105€ dans 30 jours et que l'action est à 100€, il anticipe +5%.",
    disclaimer: "⚠️ Les prédictions sont basées sur l'historique et peuvent être inexactes. Les marchés sont imprévisibles. Ne vous fiez jamais uniquement à une prédiction."
  },

  borneSuperieure: {
    title: "Borne Supérieure (Scénario Optimiste)",
    description: "Le prix maximum que le modèle estime possible selon un scénario favorable. C'est la limite haute de la prédiction.",
    interpretation: {
      good: "Représente le meilleur cas possible selon le modèle",
      bad: "N'est atteint que dans des conditions très favorables, rarement réalisé"
    },
    example: "Borne supérieure à 120€ = dans le meilleur des cas, le prix pourrait atteindre 120€.",
    disclaimer: "Scénario optimiste peu probable. Utilisez cette information avec prudence. Pas un conseil d'achat."
  },

  borneInferieure: {
    title: "Borne Inférieure (Scénario Pessimiste)",
    description: "Le prix minimum que le modèle estime possible selon un scénario défavorable. C'est la limite basse de la prédiction.",
    interpretation: {
      good: "Aide à évaluer le risque de baisse potentiel",
      bad: "Représente le pire cas possible selon le modèle"
    },
    example: "Borne inférieure à 90€ = dans le pire des cas, le prix pourrait descendre à 90€.",
    disclaimer: "Scénario pessimiste. Peut aider à évaluer le risque mais n'est pas une garantie. Pas un conseil de vente."
  },

  horizon: {
    title: "Horizon de Prédiction",
    description: "La durée sur laquelle la prédiction est faite (généralement 30 jours). Plus l'horizon est loin, moins la prédiction est fiable.",
    interpretation: {
      good: "Court terme (7-30 jours) : Prédictions plus fiables",
      bad: "Long terme (> 90 jours) : Prédictions très incertaines"
    },
    example: "Horizon 30 jours = le modèle prédit les prix pour les 30 prochains jours.",
    disclaimer: "Plus l'horizon est éloigné, plus l'incertitude augmente. Utilisez pour une tendance générale uniquement."
  },

  // ==========================================
  // VUES D'ENSEMBLE (OVERVIEW CARDS)
  // ==========================================

  qualiteMarche: {
    title: "Qualité Moyenne du Marché",
    description: "Mesure la rentabilité moyenne de toutes les entreprises disponibles. Basé sur le ROE (rentabilité) et la marge bénéficiaire.",
    interpretation: {
      good: "🟢 Excellente (ROE > 20%) : Le marché est composé d'entreprises très rentables",
      neutral: "⚪ Bonne (ROE 15-20%) : Rentabilité correcte du marché",
      bad: "🔴 Moyenne (ROE < 15%) : Rentabilité globale faible"
    },
    example: "Si la qualité moyenne est 'Excellente' avec 25% de ROE, cela signifie qu'en moyenne, les entreprises génèrent 25€ de profit pour chaque 100€ investis.",
    disclaimer: "Cette moyenne masque les disparités individuelles. Certaines entreprises peuvent être excellentes et d'autres mauvaises. Analysez chaque action séparément."
  },

  croissanceMarche: {
    title: "Croissance Moyenne du Marché",
    description: "Mesure la croissance annuelle moyenne des prix des actions sur les dernières années (CAGR).",
    interpretation: {
      good: "🟢 Forte (> 15%) : Le marché a fortement progressé",
      neutral: "⚪ Modérée (5-15%) : Croissance normale",
      bad: "🔴 Faible (< 5%) : Peu de croissance historique"
    },
    example: "Un CAGR de 12% signifie qu'en moyenne, les actions ont gagné 12% par an. 10 000€ investis il y a 5 ans valent environ 17 623€ aujourd'hui.",
    disclaimer: "La croissance passée ne garantit pas la croissance future. Les marchés peuvent baisser. Aide à évaluer l'historique uniquement."
  },

  soliditeMarche: {
    title: "Solidité Financière Moyenne",
    description: "Score global moyen (0-100) qui évalue la santé financière des entreprises : peu endettées, bonnes liquidités, croissance stable.",
    interpretation: {
      good: "🟢 Solide (Score > 80) : Entreprises financièrement saines",
      neutral: "⚪ Modérée (Score 60-80) : Situation acceptable",
      bad: "🔴 Fragile (Score < 60) : Risques financiers élevés"
    },
    example: "Un score de 85/100 indique qu'en moyenne, les entreprises ont peu de dettes, des liquidités suffisantes et une croissance régulière.",
    disclaimer: "Score basé sur des données historiques. Une bonne solidité passée ne garantit pas la stabilité future. Évaluez chaque entreprise individuellement."
  },

  dividendesMarche: {
    title: "Rendement Dividendes Moyen",
    description: "Pourcentage moyen que les entreprises versent en dividendes par rapport au prix de l'action. C'est comme un 'loyer' annuel que vous recevez.",
    interpretation: {
      good: "🟢 Élevé (> 4%) : Revenus réguliers intéressants pour les investisseurs",
      neutral: "⚪ Moyen (2-4%) : Équilibre entre dividendes et croissance",
      bad: "🔴 Faible (< 2%) : Peu de revenus réguliers, priorité à la croissance"
    },
    example: "Un rendement moyen de 3% signifie que si vous investissez 10 000€, vous recevrez environ 300€ par an en dividendes.",
    disclaimer: "Les dividendes peuvent être réduits ou supprimés à tout moment. Ne constituent pas un revenu garanti. Complétez avec d'autres critères."
  },

  symbole: {
    title: "Symbole Boursier",
    description: "Code unique qui identifie l'action en bourse. C'est comme une plaque d'immatriculation pour l'entreprise.",
    interpretation: {
      good: "Utilisez ce symbole pour rechercher l'action sur d'autres plateformes",
      bad: "Un même nom d'entreprise peut avoir plusieurs symboles sur différentes bourses"
    },
    example: "AAPL = Apple Inc., MSFT = Microsoft Corporation, GOOGL = Alphabet (Google)",
    disclaimer: "Vérifiez toujours que le symbole correspond bien à l'entreprise recherchée."
  }
};

// ==========================================
// DISCLAIMER GÉNÉRAL
// ==========================================

export const GENERAL_DISCLAIMER = `
⚠️ AVERTISSEMENT IMPORTANT

Les informations présentées sur cette plateforme sont fournies à titre informatif uniquement et constituent une aide à l'analyse, PAS un conseil en investissement.

• Les performances passées ne garantissent pas les résultats futurs
• Les marchés financiers comportent des risques de perte en capital
• Faites vos propres recherches avant toute décision d'investissement
• Consultez un conseiller financier professionnel si nécessaire
• Ne investissez que des sommes que vous pouvez vous permettre de perdre

Cette plateforme n'est pas responsable des décisions prises sur la base de ces informations.
`;


