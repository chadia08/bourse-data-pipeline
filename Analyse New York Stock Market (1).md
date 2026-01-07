## Data Card

| Fichier                     | Rôle métier                                                      |
| --------------------------- | ---------------------------------------------------------------- |
| `fundamentals.csv`          | **Santé financière** des entreprises (comptabilité, performance) |
| `prices.csv`                | **Prix boursiers journaliers**                                   |
| `prices-split-adjusted.csv` | Prix corrigés des **splits d’actions**                           |
| `securities.csv`            | **Référentiel des entreprises cotées**                           |
### A. `securities.csv` → QUI est l’entreprise




Ces colonnes décrivent **l’identité** de la société.

| Colonne                   | Signification                             |
| ------------------------- | ----------------------------------------- |
| `Ticker symbol`           | Code boursier (AAPL, MSFT…)               |
| `Security`                | Nom de l’entreprise                       |
| `SEC filings`             | Lien vers rapports réglementaires         |
| `GICS Sector`             | Secteur économique (Technology, Finance…) |
| `GICS Sub Industry`       | Sous-secteur                              |
| `Address of Headquarters` | Siège                                     |
| `Date first added`        | Date d’introduction / ajout               |
| `CIK`                     | Identifiant officiel SEC                  |

### B. `prices.csv` → Comportement du marché (faits journaliers)

Ces colonnes décrivent **comment l’action se comporte chaque jour**.

| Colonne  | Signification              |
| -------- | -------------------------- |
| `date`   | Date de cotation           |
| `symbol` | Ticker                     |
| `open`   | Prix d’ouverture           |
| `close`  | Prix de clôture            |
| `low`    | Plus bas                   |
| `high`   | Plus haut                  |
| `volume` | Nombre d’actions échangées |

### C. `fundamentals.csv` → Comptabilité & performance (le plus important)

Ce fichier contient **les états financiers**.  
Je vais les expliquer **par blocs métier**.

#### 🔹 1. Identification & période

| Colonne         | Rôle              |
| --------------- | ----------------- |
| `Ticker Symbol` | Entreprise        |
| `Period Ending` | Fin de l’exercice |
| `For Year`      | Année             |

👉 Clé temporelle annuelle/trimestrielle

---

#### 🔹 2. Revenus & rentabilité

| Colonne              | Signification         |
| -------------------- | --------------------- |
| `Total Revenue`      | Chiffre d’affaires    |
| `Cost of Revenue`    | Coût de production    |
| `Gross Profit`       | Revenue – Cost        |
| `Gross Margin`       | Marge brute           |
| `Operating Income`   | Résultat opérationnel |
| `Operating Margin`   | Marge opérationnelle  |
| `Net Income`         | Bénéfice net          |
| `Profit Margin`      | Rentabilité finale    |
| `Earnings Per Share` | Bénéfice par action   |

👉 **Métier** : est-ce que l’entreprise gagne de l’argent ?

---

#### 🔹 3. Bilan (actifs / passifs)

#### Actifs

|Colonne|
|---|
|`Total Assets`|
|`Current Assets`|
|`Cash and Cash Equivalents`|
|`Inventory`|
|`Fixed Assets`|
|`Intangible Assets`|
|`Goodwill`|

#### Passifs

|Colonne|
|---|
|`Total Liabilities`|
|`Current Liabilities`|
|`Long-Term Debt`|
|`Short-Term Debt`|

👉 **Métier** : solidité financière

---

#### 🔹 4. Liquidité & ratios

| Colonne         | Utilité                        |
| --------------- | ------------------------------ |
| `Current Ratio` | Capacité à payer à court terme |
| `Quick Ratio`   | Liquidité stricte              |
| `Cash Ratio`    | Cash pur                       |
| `After Tax ROE` | Rentabilité des fonds propres  |
| `Pre-Tax ROE`   | ROE avant impôt                |

👉 Très utilisés par analystes financiers

---

#### 🔹 5. Flux de trésorerie (Cash Flow)

| Colonne                |
| ---------------------- |
| `Net Cash Flow`        |
| `Operating Cash Flow`  |
| `Investing Cash Flow`  |
| `Financing Cash Flow`  |
| `Capital Expenditures` |

👉 **Métier** : l’entreprise génère-t-elle du cash ?


## Business Understanding
### Contexte Business
Les acteurs du marché financier (investisseurs, analystes, institutions financières) ont besoin d’informations fiables, centralisées et à jour pour suivre l’évolution des entreprises cotées et prendre des décisions d’investissement. Cependant, les données boursières sont souvent dispersées, hétérogènes et difficiles à exploiter directement, ce qui limite leur valeur business.
### Problématique Business  "Comment investir ?"


#### Problématiques descriptives

- Quelles sont les entreprises cotées par secteur ?
- Quel est le volume d’échange quotidien par action ?
- Comment évolue le prix de clôture d’une action dans le temps ?
#### Problématiques analytiques
- Quels secteurs sont les plus performants sur une période donnée ?
- Quelles entreprises présentent la plus forte volatilité ?
- Existe-t-il une corrélation entre le volume échangé et le prix de l’action ?
#### Problématiques décisionnelles
- Quels titres présentent un potentiel d’investissement ?
- Quels secteurs montrent des tendances haussières ou baissières ?
- Quelles entreprises sont les plus stables à long terme ?

### Besoins Fonctionnels (VISION MÉTIER)
####  Vision sur les entreprises cotées
- Disposer d’une liste claire et fiable des entreprises cotées.
- Identifier chaque entreprise par son symbole boursier.
- Connaître le secteur et le sous-secteur d’activité de chaque entreprise.
- Accéder aux informations de référence (nom, siège, date d’introduction).
#### Suivi de la performance boursière
- Suivre l’évolution quotidienne des prix des actions.
- Analyser les volumes échangés.
- Comparer les performances entre plusieurs entreprises.
- Observer les variations sur différentes périodes (jour, mois, année).
#### Analyse sectorielle
- Comparer la performance des secteurs économiques.
- Identifier les secteurs en croissance ou en déclin. 
- Mesurer l’impact des tendances sectorielles sur les entreprises.   
#### Aide à la décision
- Identifier les titres les plus performants.
- Repérer les entreprises stables ou volatiles.
- Détecter des signaux d’opportunité ou de risque.
- Appuyer les décisions d’investissement sur des indicateurs mesurables.
#### Pilotage et reporting
- Produire des tableaux de bord clairs et compréhensibles.
- Accéder aux indicateurs clés via des visualisations interactives.
- Faciliter la communication des résultats aux parties prenantes.
---

### Securities
## 🎯 OBJECTIF BUSINESS 





`securities.csv` ne sert **PAS** à calculer des KPI financiers directement.  
Son rôle est **stratégique** :

> Donner **le contexte métier** pour interpréter les prix, les risques et la performance.

👉 Sans `securities`, **les KPI de prices n’ont aucun sens business**.

---

# 🧱 1. RÔLE DE `securities.csv` DANS L’ARCHITECTURE

|Fichier|Rôle|
|---|---|
|prices|CE QUI SE PASSE|
|fundamentals|POURQUOI|
|**securities**|**QUI + DANS QUEL SECTEUR**|

👉 `securities` = **dimension principale**

---

# 🧠 2. COLONNES BRUTES DISPONIBLES

| Colonne originale         | Sens métier               |
| ------------------------- | ------------------------- |
| `Ticker symbol`           | Identifiant boursier      |
| `Security`                | Nom entreprise            |
| `GICS Sector`             | Secteur économique        |
| `GICS Sub Industry`       | Sous-secteur              |
| `Address of Headquarters` | Localisation              |
| `Date first added`        | Ancienneté                |
| `CIK`                     | Identifiant réglementaire |
| `SEC filings`             | Lien (inutile analytique) |

---

# ❌ 3. COLONNES À SUPPRIMER (NETTOYAGE MÉTIER)

| Colonne                   | Décision     | Pourquoi                      |
| ------------------------- | ------------ | ----------------------------- |
| `SEC filings`             | ❌ supprimer  | Aucun KPI                     |
| `Address of Headquarters` | ⚠️ optionnel | Peu utile pour investissement |
| `CIK`                     | ⚠️ optionnel | Technique, pas business       |

---

# ✅ 4. COLONNES CLÉS À CONSERVER

## 🔑 Colonnes stratégiques

|Nouvelle colonne|Source|Rôle|
|---|---|---|
|`symbol`|Ticker symbol|Clé primaire|
|`company_name`|Security|Identification|
|`sector`|GICS Sector|Analyse sectorielle|
|`sub_sector`|GICS Sub Industry|Analyse fine|
|`date_introduction`|Date first added|Ancienneté|

---

# 🧩 5. TABLE FINALE – `dim_company`

👉 **Dimension utilisée par prices et fundamentals**

|Colonne|Type|
|---|---|
|symbol (PK)|String|
|company_name|String|
|sector|String|
|sub_sector|String|
|date_introduction|Date|

---

# 📊 6. KPI POSSIBLES À PARTIR DE `securities`

⚠️ Important :  
Les KPI **ne sont PAS calculés directement dans NiFi**, mais via **jointure avec prices / fundamentals**.

---

## 🔹 KPI 1 – Nombre d’entreprises par secteur

`COUNT(symbol) BY sector`

**Utilité**

- Identifier les secteurs dominants
    
- Pondérer les analyses
    

---

## 🔹 KPI 2 – Performance moyenne par secteur

👉 Après jointure avec `prices`

`AVG(variation_pct) BY sector`

**Business**

- Secteurs gagnants / perdants
    

---

## 🔹 KPI 3 – Risque sectoriel

`STDDEV(variation_pct) BY sector`

**Business**

- Secteurs stables vs spéculatifs
    

---

## 🔹 KPI 4 – Volume échangé par secteur

`SUM(money_volume) BY sector`

👉 **Indicateur de liquidité sectorielle**

---

## 🔹 KPI 5 – Ancienneté moyenne par secteur

`AVG(YEAR(today) - YEAR(date_introduction))`

**Business**

- Secteurs matures vs récents


---
### Prices
- ~={yellow}**Variation (%)**=~ : Pour voir la **direction** (Hausse/Baisse).
- ~={yellow}**Volatilité (%)** =~: Pour voir le **risque** (Calme/Nerveux).
- ~={yellow}**Volume Argent**=~ : Pour voir la **force** (Populaire/Oubliée)
#### ~={red}**~={yellow}Variation=~**=~ 

la différence entre le prix au moment où le marché a ouvert le matin (**Open**) et le prix au moment où il a fermé le soir (**Close**).

	 Variation = Prix de Fermeture - Prix d'Ouverture
	 
**Formule du pourcentage :** `(Variation / Open) * 100`
	 ${close:minus(${open}):divide(${open}):multiply(100)}

##### Si la variation ~={red}~={green}AUGMENTE=~=~ (Valeur positive : +2€)
- ***Ce que ça signifie*** : L'action a pris de la valeur pendant la journée. On dit qu'elle est "dans le vert".
  
- ***Pourquoi c'est utile* :** Cela veut dire que beaucoup de gens ont voulu acheter cette action. La demande était plus forte que l'offre.
  
- ***Interprétation* :** C'est un signe de **confiance**. Les investisseurs pensent que l'entreprise va bien.
##### Si la variation ~={red}DIMINUE=~ (Valeur négative : -3€)
- ***Ce que ça signifie*** : L'action a perdu de la valeur. On dit qu'elle est "dans le rouge".
- ***Pourquoi c'est utile*** : Cela veut dire que les gens ont eu peur ou ont voulu récupérer leur argent en vendant leurs actions.
- ***Interprétation*** : C'est un signe de **méfiance** ou de mauvaise nouvelle pour l'entreprise.

#### ~={yellow}Volatilité=~ 
L'écart entre le prix le plus haut (**High**) et le prix le plus bas (**Low**) atteint durant la journée. Elle mesure la "nervosité" du marché.

	Volatilité = Prix le plus Haut - Prix le plus Bas

**Formule du pourcentage :** `(Volatilité / Close) * 100` `${high:minus(${low}):divide(${close}):multiply(100)}`

##### Si la volatilité est **~={green}ÉLEVÉE=~** (Grand écart de prix)
- ***Ce que ça signifie* :** Le prix a fait des bonds énormes (montagnes russes).
- ***Pourquoi c'est utile* :** Indique une période de forte incertitude ou une annonce majeure (grosse nouvelle).
- ***Interprétation* :** C'est un signe de **danger** ou de **spéculation**. L'action est très risquée.
##### Si la volatilité est **~={red}FAIBLE=~** (Petit écart de prix)
- ***Ce que ça signifie* :** Le prix a très peu bougé durant la journée.
- ***Pourquoi c'est utile* :** Indique une période de calme et de stabilité.
- ***Interprétation* :** C'est un signe de **sécurité** et de **stabilité**. L'action est sereine.

#### ~={yellow}Volume en Argent=~
Le montant total d'argent qui a circulé pour cette action durant la journée. On multiplie le nombre d'actions vendues par leur prix.

	Volume Argent = Volume d'actions × Prix de Fermeture 

**Formule NiFi :** `${volume:multiply(${close})}`

##### Si le volume est **~={red}~={green}ÉLEVÉ=~=~** (Beaucoup d'argent circule)
- ***Ce que ça signifie* :** Énormément d'investisseurs achètent et vendent cette action en même temps.
- ***Pourquoi c'est utile* :** Cela confirme que le mouvement du prix est "vrai". Si le prix monte avec un gros volume, la hausse est solide.
- ***Interprétation* :** C'est un signe d'**intérêt majeur**. L'action est très "liquide" (facile à acheter/vendre).

##### Si le volume est **~={red}FAIBLE=~** (Peu d'argent circule)
- ***Ce que ça signifie* :** Très peu de transactions ont eu lieu. Presque personne ne s'intéresse à l'action ce jour-là.
- ***Pourquoi c'est utile* :** Attention danger ! Si le prix bouge avec un petit volume, c'est peut-être un hasard ou une manipulation, ce n'est pas fiable.
- ***Interprétation* :** C'est un signe d'**indifférence**. L'action est "endormie".

---
### Fundamentals

# 1️⃣ IDENTIFICATION & TEMPS

### 🎯 Rôle : structurer toute l’analyse

### Colonnes

- `Ticker Symbol`
    
- `For Year`
    
- `Period Ending`
    

### Pourquoi ce bloc est fondamental

Ce bloc **ne sert pas à analyser**, mais à **organiser l’analyse**.  
Sans lui :

- impossible de comparer deux entreprises
    
- impossible de suivre l’évolution dans le temps
    
- impossible de joindre avec `prices.csv` ou `securities.csv`
    

### Interprétation métier

- `Ticker Symbol` → identifiant unique de l’entreprise en bourse
    
- `For Year` → année fiscale (comparaison annuelle)
    
- `Period Ending` → date exacte de clôture comptable
    

### Dans Power BI

- Axe temporel des graphiques
    
- Slicers par entreprise et par année
    
- Jointure avec données de prix
    

📌 **Message à l’oral**

> “Ce bloc permet de structurer l’analyse temporelle et multi-entreprises.”

---

# 2️⃣ TAILLE ÉCONOMIQUE

### 🎯 Rôle : mesurer le poids de l’entreprise

### Colonnes

- `Total Revenue`
    
- (optionnel) `Gross Profit`
    

### Question métier

> L’entreprise est-elle **petite, moyenne ou grande** ?

### Interprétation financière

- `Total Revenue` = chiffre d’affaires  
    → mesure la **taille du business**
    
- Une grande entreprise :
    
    - plus stable
        
    - moins risquée
        
    - mais parfois moins rentable
        

### Valeur analytique

- Comparer les profits **relativement à la taille**
    
- Éviter de comparer une startup à une multinationale
    

### Dans Power BI

- Classement des entreprises par CA
    
- Visualisation de la croissance du revenu
    
- Pondération des KPI de rentabilité
    

📌 **Message clé**

> “La taille permet de contextualiser la performance financière.”

---

# 3️⃣ RENTABILITÉ

### 🎯 Rôle : savoir si l’entreprise crée de la valeur

### Colonnes

- `Net Income`
    
- `Operating Income`
    
- `Profit Margin`
    
- `Operating Margin`
    

### Question métier

> L’entreprise **gagne-t-elle réellement de l’argent** ?

### Interprétation financière

- `Operating Income`  
    → performance du **cœur de métier**
    
- `Net Income`  
    → bénéfice final après tout
    
- `Operating Margin`  
    → efficacité opérationnelle
    
- `Profit Margin`  
    → rentabilité globale
    

### Lecture analytique

- Marges élevées = avantage concurrentiel
    
- Marges stables = modèle économique sain
    
- Marges en baisse = problème structurel
    

### Dans Power BI

- Graphiques d’évolution des marges
    
- Comparaison entre entreprises
    
- Détection d’entreprises inefficaces
    

📌 **Message clé**

> “La rentabilité mesure la capacité à transformer le chiffre d’affaires en profit.”

---

# 4️⃣ SOLIDITÉ FINANCIÈRE (RISQUE)

### 🎯 Rôle : mesurer le risque de faillite

### Colonnes

- `Total Assets`
    
- `Total Liabilities`
    
- `Long-Term Debt`
    
- `Total Equity`
    

### Question métier

> L’entreprise est-elle **financièrement stable** ?

### Interprétation financière

- `Total Assets` → ce que l’entreprise possède
    
- `Total Liabilities` → ce qu’elle doit
    
- `Long-Term Debt` → risque futur
    
- `Total Equity` → valeur nette
    

### KPI dérivés

- **Debt Ratio** = Liabilities / Assets
    
- **Leverage** = Debt / Equity
    

### Lecture analytique

- Dette trop élevée → risque élevé
    
- Bon équilibre → entreprise résiliente
    

### Dans Power BI

- Indicateurs de risque
    
- Cartographie des entreprises à risque
    
- Comparaison dette / profit
    

📌 **Message clé**

> “Une entreprise rentable mais surendettée est un investissement dangereux.”

---

# 5️⃣ LIQUIDITÉ

### 🎯 Rôle : capacité de survie à court terme

### Colonnes

- `Current Ratio`
    
- (optionnel) `Quick Ratio`
    

### Question métier

> L’entreprise peut-elle **payer ses dettes immédiates** ?

### Interprétation financière

- `Current Ratio` = Actifs courts / Passifs courts
    
- Seuils :
    
    - < 1 → danger
        
    - 1–2 → sain
        
    - > 2 → inefficacité du capital
        

### Importance stratégique

Beaucoup d’entreprises rentables meurent par **manque de liquidité**.

### Dans Power BI

- Alertes de liquidité
    
- Filtres de sélection d’entreprises solides
    

📌 **Message clé**

> “La liquidité mesure la capacité de l’entreprise à survivre aux chocs.”

---

# 6️⃣ VALEUR POUR L’ACTIONNAIRE

### 🎯 Rôle : décider d’investir ou non

### Colonnes

- `Earnings Per Share (EPS)`
    
- `After Tax ROE`
    

### Question métier

> Est-ce que l’investissement **rapporte réellement à l’actionnaire** ?

### Interprétation financière

- `EPS`  
    → bénéfice par action (clé en bourse)
    
- `ROE`  
    → rendement du capital investi par les actionnaires
    

### Lecture analytique

- ROE élevé et stable = entreprise performante
    
- EPS croissant = création de valeur
    

### Dans Power BI

- Classement des meilleures entreprises
    
- Indicateurs de performance actionnariale
    
- Croisement avec prix boursiers
    

📌 **Message clé**

> “Ce bloc traduit la performance financière en valeur boursière.”


# ✅ TABLE FINALE – COLONNES ESSENTIELLES

## Dataset : `fundamentals.csv`

---

## 1️⃣ IDENTIFICATION & TEMPS (OBLIGATOIRE)

|Colonne originale|Nouvelle colonne|Action NiFi|Pourquoi indispensable|
|---|---|---|---|
|`Ticker Symbol`|`ticker`|rename|Clé métier principale|
|`For Year`|`year`|cast int|Analyse annuelle|
|`Period Ending`|`period_end`|cast date|Jointure temporelle|

📌 **Sans ce bloc : aucune analyse possible**

---

## 2️⃣ TAILLE DE L’ENTREPRISE (CONTEXTE)

|Colonne originale|Nouvelle colonne|Action NiFi|Valeur métier|
|---|---|---|---|
|`Total Revenue`|`total_revenue`|cast decimal|Taille économique|
|`Gross Profit`|`gross_profit`|cast decimal|Capacité commerciale|

📊 Sert à **pondérer tous les autres KPI**

---

## 3️⃣ RENTABILITÉ (CRÉATION DE VALEUR)

|Colonne originale|Nouvelle colonne|Action NiFi|KPI clé|
|---|---|---|---|
|`Net Income`|`net_income`|cast decimal|Profit réel|
|`Operating Income`|`operating_income`|cast decimal|Performance métier|
|`Operating Margin`|`operating_margin`|cast %|Efficacité|
|`Profit Margin`|`profit_margin`|cast %|Rentabilité finale|

📌 **Cœur de la décision d’investissement**

---

## 4️⃣ SOLIDITÉ FINANCIÈRE (RISQUE)

|Colonne originale|Nouvelle colonne|Action NiFi|KPI|
|---|---|---|---|
|`Total Assets`|`total_assets`|cast decimal|Richesse|
|`Total Liabilities`|`total_liabilities`|cast decimal|Dette|
|`Long-Term Debt`|`long_term_debt`|cast decimal|Risque long terme|
|`Total Equity`|`equity`|cast decimal|Valeur nette|

📉 Sert à calculer **ratios de risque**

---

## 5️⃣ LIQUIDITÉ (SURVIE COURT TERME)

|Colonne originale|Nouvelle colonne|Action NiFi|Alerte|
|---|---|---|---|
|`Current Ratio`|`current_ratio`|cast decimal|Faillite possible|

⚠️ Très utilisé par analystes financiers

---

## 6️⃣ VALEUR ACTIONNAIRE (DÉCISION FINALE)

|Colonne originale|Nouvelle colonne|Action NiFi|Décision|
|---|---|---|---|
|`Earnings Per Share`|`eps`|cast decimal|Attractivité|
|`After Tax ROE`|`roe`|cast %|Rentabilité capital|

🎯 **Détermine si on investit ou non**

#### ~={yellow}Résultat Net (Net Income)=~
C'est l'argent qui reste à la fin, une fois que toutes les factures et les impôts sont payés.
##### Si le résultat net est **~={red}NÉGATIF=~** (comme ici : -1,87 milliard)

- ***Ce que ça signifie :*** L'entreprise a perdu de l'argent cette année-là. Elle a dépensé plus qu'elle n'a gagné.
- ***Pourquoi c'est utile :*** C'est le signal d'alarme numéro 1.
- ***Interprétation* :** C'est un signe de **difficulté financière**. L'entreprise "brûle" son cash.

#### ~={yellow}Revenu Total (Total Revenue)=~
C'est tout l'argent que l'entreprise a encaissé en vendant ses services (billets d'avion), avant de payer ses dépenses.
##### Si le revenu total est **~={green}ÉLEVÉ=~** (24,8 milliards)
- ***Ce que ça signifie* :** L'entreprise est une "grosse machine" qui attire beaucoup de clients.
- ***Pourquoi c'est utile :*** Cela montre la taille de l'entreprise sur le marché.
- ***Interprétation* :** C'est un signe de **puissance commerciale**, même si elle n'est pas encore rentable.

#### ~={yellow}Le Ratio Courant (Current Ratio)=~
C'est la capacité de l'entreprise à payer ses dettes qui arrivent bientôt (le mois prochain par exemple).
##### Si le ratio est **~={orange}INFÉRIEUR=~ À 100** (ici : 78)
- ***Ce que ça signifie :*** L'entreprise n'a pas assez d'argent liquide pour payer toutes ses dettes immédiates.
- ***Pourquoi c'est utile* :** C'est l'indicateur de survie à court terme.
- ***Interprétation* :** C'est un signe de **fragilité**. Elle doit faire attention à ne pas se retrouver bloquée.

---

























## Analyse possible : le rendement
### 🔹 Définition métier du rendement
Le **rendement** mesure la **variation relative du prix** sur une période.
👉 Il répond à la question :
> _De combien le titre a-t-il progressé par rapport à son prix de départ ?_
### Repérer les entreprises volatiles

### 🔹 Objectif métier
Identifier les actions dont le **prix varie fortement** sur une période donnée.
C’est essentiel pour :
- évaluer le **risque**
- éviter des titres instables
- ou au contraire, cibler des opportunités à **fort potentiel** (trading)

### Que signifie “volatile” en bourse ?

Une action est dite **volatile** lorsque :
- son prix **monte et descend fortement**
- sur une **courte période de temps**
👉 Plus les écarts de prix sont grands, plus le **risque** est élevé.
### 🔹 Interprétation métier
- Volatilité **faible**  
    → prix stable  
    → action peu risquée
- Volatilité **élevée**  
    → fortes fluctuations  
    → action risquée
<mark style="background: #FF5582A6;">attention: prices.csv est varie en terme journaliere comment evaluer la volatilité ?</mark>

### Évaluer le risque
### 🎯 Objectif métier

L’entreprise ou l’investisseur souhaite **comprendre le niveau de risque** associé à chaque action afin de :
- anticiper les **pertes possibles**
- ajuster le **portefeuille**
- prendre des décisions d’investissement **plus sûres**
---

## 📊 Données utilisées dans le dataset

- **Variations de prix** : par exemple, `close − open` ou les rendements `(close − open)/open`   
- **Volume** : nombre d’actions échangées
Ces informations permettent de mesurer **l’amplitude et la fréquence des fluctuations**.
---
## 📈 Analyse possible : mesure statistique du risque

### 🔹 Écart-type des rendements

- L’écart-type mesure la **dispersion des rendements** autour de leur moyenne
- Plus l’écart-type est élevé → plus l’action est **instable / risquée**
- Plus il est faible → l’action est **stable / moins risquée**
### 🔹 Interprétation métier
- Action avec **fortes variations de prix** → risque élevé
- Action avec **faible variation** → risque faible
- On peut combiner cette analyse avec le **volume** :
    - forte fluctuation avec gros volume → signal important
    - forte fluctuation avec faible volume → mouvement moins significatif
---

---

### 🔹 Interprétation simple

- Rendement **positif** → le titre a gagné de la valeur    
- Rendement **négatif** → le titre a perdu de la valeur
- Rendement **élevé** → titre plus performant
## Data Cleaning 
- Dates → format et date actuelle
- Montants → numériques
- Valeurs nulles → 
- Harmoniser les symboles
### Securities
| Colonne originale         | Nouvelle colonne    | Utile ?             | Pourquoi                                                            |
| ------------------------- | ------------------- | ------------------- | ------------------------------------------------------------------- |
| `Ticker symbol`           | `symbole`           | ✅ OUI (obligatoire) | Identifiant principal du titre boursier                             |
| `Security`                | `nom`               | ✅ OUI               | Nom de l’entreprise                                                 |
| `SEC filings`             | ❌ supprimée         | ❌ NON               | Toujours la même valeur (`reports`), aucune valeur analytique       |
| `GICS Sector`             | `secteur`           | ✅ OUI               | Analyse sectorielle                                                 |
| `GICS Sub Industry`       | `sous_secteur`      | ✅ OUI               | Analyse plus fine                                                   |
| `Address of Headquarters` | `siege`             | ⚠️ OPTIONNEL        | Utile si tu veux analyse géographique                               |
| `Date first added`        | `date_introduction` | ⚠️ OPTIONNEL        | Utile pour analyses historiques                                     |
| `CIK`                     | `cik`               | ⚠️ OPTIONNEL        | Identifiant officiel SEC, utile pour croiser avec d’autres datasets |
## Data Modeling

### ⭐ Dimension tables

#### `dim_company`
- ticker_symbol (PK)
- company_name
- sector
- sub_industry
- headquarters
- cik

#### `dim_date`
- date_id
- date
- year
- month
- quarter
---
### ⭐ Fact tables
#### `fact_market_prices`
- date_id
- ticker_symbol
- open
- close
- high
- low
- volume
- adjusted_flag

#### `fact_financials`
- period_id    
- ticker_symbol
- total_revenue
- net_income
- earnings_per_share
- total_assets
- total_liabilities
- operating_margin
- profit_margin
- roe

## Dashboarding

- Évolution du prix vs résultats financiers
- Classement par secteur
- Rentabilité par entreprise
- Corrélation prix ↔ bénéfices