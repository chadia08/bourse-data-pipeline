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
docker compose up -d
```

### 💡 Commandes utiles
Arrêter les conteneurs : ```docker-compose down```

Quitter l'environnement virtuel : ```deactivate```

Vérifier l'état de la branche : ```git status```



## Etape Nifi
### 🏁 FLOW 1 — securities (Kafka) étape par étape
#### Étape A : Envoyer le CSV vers Kafka
##### 1️⃣ Préparer le CSV

Place ton fichier securities.csv dans un dossier accessible depuis Docker (ex: ./data/raw/securities.csv).

##### 2️⃣ Créer le topic Kafka (si pas déjà fait)
``docker exec -it kafka kafka-topics --create --topic securities_topic --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1``

##### 3️⃣ Script Python pour publier le CSV

#### Étape B : NiFi — ConsumeKafka
##### 1️⃣ Ajouter le processor ConsumeKafka
Topic Name : securities_topic
Kafka Brokers : kafka:9092
Group ID : nifi-securities-consumer
Auto Offset Reset : earliest (pour relire depuis le début)

##### 2️⃣ Démarrer le processor
Clic droit → Start
Vérifie que les messages sont consommés (stats In / Out > 0)

#### Étape C : ConvertRecord
##### 1️⃣ Ajouter le processor ConvertRecord
Record Reader : CSVReader
Schema Access Strategy : Infer Schema
First Line is Header : true
Delimiter : ,
Record Writer : JSONRecordSetWriter ou AvroRecordSetWriter

##### 2️⃣ Connecter à ConsumeKafka
Tire un lien de sortie de ConsumeKafka → ConvertRecord
Objectif : chaque message CSV devient un record structuré, prêt pour le nettoyage

#### Étape D : UpdateRecord (nettoyage / normalisation)
##### 1️⃣ Ajouter UpdateRecord
Actions à faire :
Renommer les colonnes :
Ticker symbol → ticker_symbol
Security → company_name
GICS Sector → sector
GICS Sub Industry → sub_industry
Supprimer lignes invalides (ticker_symbol vide)
Normaliser les valeurs (trim, majuscules si besoin)

##### 2️⃣ Connecter ConvertRecord → UpdateRecord

#### Étape E : PutDatabaseRecord (ClickHouse)
##### 1️⃣ Créer Database Connection Pool
Controller Service : ClickHouse
Paramètres : host clickhouse, port 8123, database default

##### 2️⃣ Ajouter PutDatabaseRecord
Table Name : dim_company
Connection Pool : ClickHouse créé
Mode : Insert

##### 3️⃣ Connecter UpdateRecord → PutDatabaseRecord



--------------------------------------------------------------------------
#### vérifier nifi ----> kafka 
``docker exec -it kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic send_clickhouse --from-beginning --timeout-ms 10000``


---
## Connecter ClickHouse à powerBi
### 1. Installer le Driver ODBC ClickHouse
Power BI ne possède pas de connecteur "natif" pré-installé pour ClickHouse. Tu dois installer le driver officiel sur ton ordinateur (Windows) :
- Va sur le GitHub officiel des drivers ClickHouse [https://github.com/ClickHouse/clickhouse-odbc/releases].
- Télécharge et installe la version Windows MSI (prends la version x64 pour Power BI Desktop).

### 2. Configurer la source de données (DSN) sur Windows
Avant d'ouvrir Power BI, tu dois déclarer ta base Docker à Windows :
- Dans la barre de recherche Windows, tape "Sources de données ODBC (64 bits)".
- Va dans l'onglet DSN Système et clique sur Ajouter.
- Choisis ClickHouse Unicode.
- Remplis les informations : <br>
    ```
    Name : ClickHouse_Bourse 
    Host : localhost (ou l'adresse IP de ta machine Docker)
    Port : 8123 (C'est le port HTTP que nous avons ouvert dans le docker-compose)
    Database : bourse
    User : default
    Password : admin
    ```
### 3. Connexion dans Power BI
- Ouvre Power BI Desktop.
- Clique sur Obtenir les données > Plus...
- Cherche ODBC et clique sur Se connecter.
- Dans le menu déroulant "Nom de la source de données (DSN)", choisis ClickHouse_Bourse.
- Si Power BI demande des identifiants, choisis "Par défaut ou Personnalisé" (puisque tu les as déjà mis dans le DSN).

### 4. DirectQuery vs Import
Une fois connecté, Power BI va te demander comment traiter les données :
- Import : Power BI télécharge les données. C'est plus rapide pour les calculs complexes, mais il faut rafraîchir manuellement.
- DirectQuery : Power BI interroge ClickHouse à chaque clic. C'est l'idéal pour voir tes données boursières bouger presque en "temps réel" dès que NiFi pousse un message.