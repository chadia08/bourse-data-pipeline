-- 1. Table de stockage final (Reste identique)
DROP TABLE IF EXISTS bourse.dim_company;
CREATE TABLE bourse.dim_company
(
    symbole String,
    nom String,
    secteur String,
    sous_secteur String,
    siege String,
    date_introduction Date,
    cik String
) ENGINE = MergeTree()
ORDER BY symbole;

-- 2. La Queue (Modifiée pour Docker)
DROP TABLE IF EXISTS bourse.company_kafka_queue;
CREATE TABLE bourse.company_kafka_queue
(
    symbole String,
    nom String,
    secteur String,
    sous_secteur String,
    siege String,
    date_introduction String,
    cik String
)
ENGINE = Kafka
SETTINGS kafka_broker_list = 'kafka:29092', 
         kafka_topic_list = 'send_company',
         kafka_group_name = 'ch_group_docker_v1', 
         kafka_format = 'JSONEachRow',
         kafka_skip_broken_messages = 1;

-- 3. La Vue Matérialisée (Reste identique)
DROP TABLE IF EXISTS bourse.company_mv;
CREATE MATERIALIZED VIEW bourse.company_mv TO bourse.dim_company AS
SELECT
    symbole,
    nom,
    secteur,
    sous_secteur,
    siege,
    -- Conversion sécurisée en Date
    toDate(parseDateTimeBestEffortOrNull(date_introduction)) AS date_introduction,
    cik
FROM bourse.company_kafka_queue;

--------------------------------------------------------------------------------------------------------
-- fact prices
DROP TABLE IF EXISTS bourse_mv;
DROP TABLE IF EXISTS bourse_kafka_queue;
DROP TABLE IF EXISTS bourse_data;

CREATE TABLE bourse.bourse_data (
    id String,
    date Date,              -- Correspond au champ "date" du JSON
    symbole LowCardinality(String),
    prix_ouverture Float64,
    prix_cloture Float64,
    prix_bas Float64,
    prix_haut Float64,
    volume Float64,
    variation Float64,
    volatilite Float64,
    dollar_volume Float64
) 
ENGINE = MergeTree()
ORDER BY (symbole, date);

CREATE TABLE bourse.bourse_kafka_queue (
    id String,
    date String,
    symbole String,
    prix_ouverture Float64,
    prix_cloture Float64,
    prix_bas Float64,
    prix_haut Float64,
    volume Float64,
    variation Float64,
    volatilite Float64,
    dollar_volume Float64
)
ENGINE = Kafka()
SETTINGS 
    kafka_broker_list = 'kafka:29092', 
    kafka_topic_list = 'send_prices',
    kafka_group_name = 'group_final_v5', -- Nouveau groupe pour déclencher la lecture
    kafka_format = 'JSONEachRow';

CREATE MATERIALIZED VIEW bourse.bourse_mv TO bourse.bourse_data AS
SELECT 
    id, 
    toDate(date) AS date, -- Conversion du String "2016-01-05" en Date
    symbole, 
    prix_ouverture, 
    prix_cloture, 
    prix_bas, 
    prix_haut, 
    volume, 
    variation, 
    volatilite, 
    dollar_volume
FROM bourse_kafka_queue;


--------------------------------------------------------------------------------------------------------

-- Table de jointure dans trino
CREATE TABLE clickhouse.bourse.v_bourse_complete_analytics AS
SELECT 
    p.id,
    p.date,
    p.symbole,
    p.prix_ouverture,
    p.prix_cloture,
    p.prix_bas,
    p.prix_haut,
    p.volume,
    p.variation,
    p.volatilite,
    p.dollar_volume,
    c.nom,
    c.secteur,
    c.sous_secteur,
    c.siege,
    c.date_introduction
FROM clickhouse.bourse.prices p
LEFT JOIN clickhouse.bourse.company c ON p.symbole = c.symbole;