Pipeline de Données : Stock Market ETL (NiFi → Kafka → ClickHouse)
===============================================================

Ce document décrit le flux de traitement des données boursières (prices.csv) implémenté avec Apache NiFi, Kafka et ClickHouse. Il est conçu pour être copié dans le README du projet ou utilisé comme documentation technique.

1. Architecture Globale
-----------------------

- Source : Fichiers CSV locaux (ex : `prices.csv`).
- Traitement : Apache NiFi (nettoyage et transformation avec QueryRecord, Jolt, etc.).
- Transport : Apache Kafka (topic de transport des données nettoyées).
- Destination : ClickHouse (pour analyse rapide et connexion à Power BI).

2. Objectifs
------------

- Nettoyer et normaliser les données en amont (filtrage, cast des types).
- Garantir la résilience (Kafka bufferise si la destination est indisponible).
- Produire un format structuré (JSON / CSVWithNames) pour l’ingestion dans ClickHouse.

3. Description détaillée des étapes NiFi
---------------------------------------

A. Ingestion — `GetFile`

- Rôle : Surveille le répertoire source et lit `prices.csv`.
- Configuration : Lecture par morceaux pour limiter l'utilisation mémoire.

B. Enrichissement — `UpdateAttribute`

- Rôle : Ajout/gestion des métadonnées.
- Attributs typiques : `schema.name = Bourse_schema`, `event_time` (timestamp d'ingestion).

C. Nettoyage SQL — `QueryRecord`

- Rôle : Composant central de nettoyage (utilise Apache Calcite pour SQL sur FlowFiles).
- Opérations :
  - Filtrage : `WHERE volume > 0` (suppression des lignes sans volume).
  - Casting : `CAST(close AS DOUBLE)` pour assurer le typage numérique.
  - Sélection : garder uniquement `date, symbol, close, volume`.
- Format de sortie : conversion vers JSON (par `RecordSetWriter`).

D. Transformation structurelle — `JoltTransformJSON`

- Rôle : Remappage/renommage des champs pour standardiser le schéma.
- Exemple de mapping (Shift) :
  - `symbol` ➔ `ticker`
  - `close` ➔ `price_usd`
  - `volume` ➔ `volume_traded`

E. Distribution — `PublishKafkaRecord`

- Rôle : Publier chaque enregistrement nettoyé sur un topic Kafka (ex : `stock-market-clean`).
- Avantage : Décorrèle NiFi de la base de stockage; aucune perte si ClickHouse est down.

4. Schéma de transformation (résumé)
-----------------------------------

Champ original (CSV) → Champ final (JSON) :

- `date` → `date_transaction` (ISO-Date)
- `symbol` → `ticker` (String)
- `close` → `price_usd` (Double)
- `volume` → `volume_traded` (Double, filtré > 0)

5. ClickHouse : consommation depuis Kafka
----------------------------------------

Option 1 — ClickHouse lit directement depuis Kafka (engine `Kafka`) :

Exemple DDL :

CREATE TABLE kafka_source (
  date_transaction String,
  ticker String,
  price_usd Float64,
  volume_traded Float64
) ENGINE = Kafka
SETTINGS
  kafka_broker_list = 'broker1:9092',
  kafka_topic_list = 'stock-market-clean',
  kafka_group_name = 'ch_group_stock',
  kafka_format = 'JSONEachRow',
  kafka_num_consumers = 1;

CREATE TABLE real_table (
  date_transaction DateTime,
  ticker String,
  price_usd Float64,
  volume_traded Float64
) ENGINE = MergeTree()
ORDER BY (date_transaction, ticker);

CREATE MATERIALIZED VIEW mv_kafka_to_real TO real_table AS
SELECT
  parseDateTimeBestEffort(date_transaction) AS date_transaction,
  ticker,
  price_usd,
  volume_traded
FROM kafka_source;

Remarques :
- Si NiFi envoie du CSV, utilisez `kafka_format = 'CSV'` ou `CSVWithNames` et alignez les colonnes.
- Si Kafka est sécurisé, ajoutez les paramètres SASL/SSL dans les `SETTINGS` (ex : `kafka_security_protocol`, `kafka_sasl_*`, `kafka_ssl_*`).

6. Tests rapides
-----------------

- Vérifier le topic Kafka :
  kafka-topics.sh --bootstrap-server broker:9092 --describe --topic stock-market-clean
- Produire un message de test :
  kcat -b broker:9092 -t stock-market-clean -P <<EOF
  {"date_transaction":"2025-12-01T10:00:00","ticker":"ABC","price_usd":12.34,"volume_traded":100}
  EOF
- Contrôler l'insertion dans ClickHouse :
  clickhouse-client --query="SELECT count() FROM real_table"

7. Pourquoi cette solution ?
---------------------------

- Fiabilité : Bufferisation via Kafka et typage fort dans ClickHouse.
- Performance : Filtrage en amont réduit la charge réseau et stockage.
- Modularité : Ajout facile de nouveaux fichiers/processors NiFi.

8. Déploiement rapide
---------------------

1. Démarrer ZooKeeper et Kafka.
2. Activer les Controller Services NiFi (`CSVReader`, `JsonRecordSetWriter`).
3. Placer `prices.csv` dans le dossier surveillé par `GetFile`.
4. Surveiller le topic Kafka et vérifier l'arrivée des messages :
   kafka-console-consumer --bootstrap-server localhost:9092 --topic stock-market-clean --from-beginning

9. Remarques finales
-------------------

Conservez une copie des specifications Jolt et du SQL utilisé dans `QueryRecord` dans le repository pour garantir traçabilité et reproductibilité.

---

Cette documentation a été générée à partir de votre description. Si vous voulez que je l'ajoute dans `README.md` principal au lieu d'un fichier séparé, ou que je modifie le texte (ajouter DDL exact, brokers, topic names), dites-le et je mets à jour et pousse les changements.
