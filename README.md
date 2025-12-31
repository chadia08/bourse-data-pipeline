# README.md
---

## 🚀 Installation et Lancement du Projet

Suivez ces étapes pour configurer l environnement de développement sur votre machine.

---

### 1. Cloner le dépôt
Commencez par récupérer le projet localement :
```bash
git clone https://github.com/chadia08/bourse-data-pipeline.git

cd bourse-data-pipeline
```
### 2. Créer une branche personnalisée
Il est recommandé de travailler sur une branche séparée portant votre nom :

```
git checkout -b prenom
```

### 3. Configuration de l'environnement virtuel
Créez un environnement Python pour isoler les dépendances du projet :

Sur Windows :

```
python -m venv venv

.\venv\Scripts\activate
```

Sur macOS / Linux :
```
python3 -m venv venv

source venv/bin/activate
```
### 4. Installer les dépendances
Une fois l'environnement activé, installez les bibliothèques nécessaires listées dans le fichier requirements :
```
pip install -r requirements.txt
```
### 5. Lancer l'application avec Docker
Pour démarrer tous les services (base de données, application, etc.) via Docker Compose :
```
docker-compose up --build
```

### 💡 Commandes utiles
Arrêter les conteneurs : ```docker-compose down```

Quitter l'environnement virtuel : ```deactivate```

Vérifier l'état de la branche : ```git status```

### 6 Premierement la Préparation des fichiers CSV , pour ce projet on a choisi:
- prices.csv → Données de prix boursiers
- fundamentals.csv → Données financières
- prices-split-adjusted.csv → Prix ajustés
- securities.csv → Informations sur les entreprises
### 7: apres preparation le fichier compose.yml comme a singler mes colleague avant verification des contenurs si tout Run BIEN.
- Passant a la Configuration NiFi pour l’ingestion des donnees,flux NiFi suggéré :

1-GetFile → Lit les fichiers CSV depuis un dossier local
2-UpdateAttribute → Ajoute un attribut filename et timestamp
3-ConvertRecord (CSV → JSON) → Transforme chaque ligne en JSON
4-PartitionRecord → Peut partitionner par symbole boursier si besoin
5-PublishKafka → Envoie chaque enregistrement vers un topic Kafka

maintenant on va detailler la configuration de chaque processus
Étape 1 : GETFILE (création processus)
-	Il lit les fichiers CSV depuis /opt/nifi/data/raw/
-	Sortie sur la relation success
Configuration à vérifier sur l'onglet PROPERTIES .
Input Directory: /opt/nifi/data/raw
File Filter: *.csv 
Keep Source File: false
Polling Interval: 10 sec
en fin:	Cliquez APPLY

Étape 2 :SplitRecord : apres je mensionne les configuration
Étape 3 :UPDATEATTRIBUTE son objectif et d'jouter des métadonnées et timestamps
- Ajouter le processeur :
-Connectez-le à GetFile :
-Sélectionnez la relation success
Configurer UpdateAttribute ,aller dans les propriétés :
ingestion_timestamp	${now():format('yyyy-MM-dd HH:mm:ss')}
processing_date	${now():format('yyyyMMdd')}
pipeline_id	real_time_2025
file_source	${filename}
- dans l'onglet SCHEDULING :
Scheduling Strategy: Timer driven
Run Schedule: 0 sec
Concurrent Tasks: 1
Puis cliquez APPLY
Ouvrir le bon Administrateur ODBC
Fermez la fenêtre actuelle.

Dans votre barre de recherche Windows, tapez bien : "Sources de données ODBC (64 bits)".

C'est crucial car, sur votre écran, on voit que le DSN ClickHouse_Bourse est associé à un driver 32 bits, ce qui causera une erreur dans Power BI.

2. Création du DSN Système (64 bits)
Une fois la fenêtre 64 bits ouverte :

Allez dans l'onglet Sources de données système.

Cliquez sur Ajouter....

Sélectionnez ClickHouse ODBC Driver (Unicode) dans la liste. L'Unicode est indispensable pour ne pas corrompre les noms des entreprises comme "AbbVie" ou "AFLAC".

3. Remplissage des paramètres de connexion
Une nouvelle fenêtre de configuration va s'ouvrir. Remplissez ces champs avec précision :

Name : ClickHouse_Bourse (C'est ce nom que vous chercherez dans Power BI).

Host : 127.0.0.1 (C'est l'adresse locale de votre machine où tourne le conteneur Docker).

Port : 8123 (C'est le port HTTP de ClickHouse).

Database : default (La base par défaut où vous avez créé votre table securities_data).

User : default.

Password : Laissez vide (sauf si vous avez configuré un mot de passe spécifique dans Docker).

4. Validation et Test
Cliquez sur le bouton Test. Si vous voyez un message "Success", la liaison entre Windows et votre base ClickHouse est établie.

Cliquez sur OK pour enregistrer.



