DROP TABLE IF EXISTS bourse.company;
DROP TABLE IF EXISTS bourse.company_queue;
DROP TABLE IF EXISTS bourse.mv_fundamentals;
DROP TABLE IF EXISTS bourse.kafka_fundamentals_queue;

CREATE TABLE IF NOT EXISTS bourse.company
(
    symbole String,
    nom String,
    secteur String,
    sous_secteur String,
    siege String,
    date_introduction DateTime64(3),
    cik String
) ENGINE = MergeTree() 
ORDER BY symbole; -- C'est ici ta "clé primaire" (index de tri)

-- Étape B : Le connecteur Kafka (Queue)
CREATE TABLE IF NOT EXISTS bourse.company_queue
(
    symbole String,
    nom String,
    secteur String,
    sous_secteur String,
    siege String,
    date_introduction DateTime64(3),
    cik String
) ENGINE = Kafka
SETTINGS kafka_broker_list = 'kafka:29092',
         kafka_topic_list = 'send_clickhouse', -- Ton topic
         kafka_group_name = 'clickhouse_consumer_group',
         kafka_format = 'JSONEachRow',
         kafka_skip_broken_messages = 1;


CREATE MATERIALIZED VIEW IF NOT EXISTS bourse.company_mv TO bourse.company AS
SELECT * FROM bourse.company_queue;

---------------------------------------------------------------------------------------------------
-- 1. Supprimer la vue et la queue actuelle

CREATE TABLE IF NOT EXISTS bourse.fact_fundamentals (
    symbole String,
    date_fin_periode DateTime64(3),
    resultat_net Float64,
    total_actifs Float64,
    total_passif Float64,
    revenu_total Float64,
    annee_fiscale Nullable(Float64),
    eps Nullable(Float64),
    depenses_rd Float64,
    cash_disponible Float64,
    marge_operationnelle Float64,
    capitaux_propres Float64
) 
ENGINE = MergeTree()
PARTITION BY toYear(date_fin_periode)
ORDER BY (symbole, date_fin_periode);

-- 2. Recréer la queue avec un NOUVEAU groupe et des réglages de lecture souples
CREATE TABLE bourse.kafka_fundamentals_queue (
    symbole String,
    date_fin_periode Int64,
    resultat_net Float64,
    total_actifs Float64,
    total_passif Float64,
    revenu_total Float64,
    annee_fiscale Nullable(Float64),
    eps Nullable(Float64),
    depenses_rd Float64,
    cash_disponible Float64,
    marge_operationnelle Float64,
    capitaux_propres Float64
)
ENGINE = Kafka
SETTINGS 
    kafka_broker_list = 'kafka:29092',
    kafka_topic_list = 'send_clickhouse',
    kafka_group_name = 'clickhouse_group_v_final', -- Nouveau nom pour reset l'offset
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 1,
    kafka_skip_broken_messages = 100,             -- Ignore jusqu'à 100 erreurs de format
    input_format_import_nested_json = 1;

-- 3. Recréer la Vue Matérialisée
CREATE MATERIALIZED VIEW bourse.mv_fundamentals TO bourse.fact_fundamentals AS
SELECT
    symbole,
    fromUnixTimestamp64Milli(date_fin_periode) AS date_fin_periode,
    resultat_net,
    total_actifs,
    total_passif,
    revenu_total,
    annee_fiscale,
    eps,
    depenses_rd,
    cash_disponible,
    marge_operationnelle,
    capitaux_propres
FROM bourse.kafka_fundamentals_queue;