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

CREATE TABLE bourse.fact_prices (
    id UInt64,
    date_seance Date32,
    symbole String,
    prix_ouverture Float64,
    prix_cloture Float64,
    prix_bas Float64,
    prix_haut Float64,
    volume Float64
) ENGINE = MergeTree()
ORDER BY (symbole, date_seance);


CREATE TABLE bourse.kafka_prices_queue (
    id String,
    date_seance String,
    symbole String,
    prix_ouverture String,
    prix_cloture String,
    prix_bas String,
    prix_haut String,
    volume String
) ENGINE = Kafka
SETTINGS kafka_broker_list = 'kafka:29092', 
         kafka_topic_list = 'send_company',
         kafka_group_name = 'ch_group_docker_v1', 
         kafka_format = 'JSONEachRow',
         kafka_skip_broken_messages = 1;



DROP TABLE IF EXISTS bourse.mv_prices_consumer;

CREATE MATERIALIZED VIEW bourse.mv_prices_consumer TO bourse.fact_prices AS
SELECT
    toUInt64OrZero(id) AS id,
    parseDateTimeBestEffortOrNull(date_seance) AS date_seance,
    symbole,
    toFloat64OrZero(prix_ouverture) AS prix_ouverture,
    toFloat64OrZero(prix_cloture) AS prix_cloture,
    toFloat64OrZero(prix_bas) AS prix_bas,
    toFloat64OrZero(prix_haut) AS prix_haut,
    toFloat64OrZero(volume) AS volume
FROM bourse.kafka_prices_queue;


--------------------------------------------------------------------------------------------------------