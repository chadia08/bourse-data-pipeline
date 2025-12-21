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