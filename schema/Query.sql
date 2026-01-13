-- 1. Table de stockage final (Reste identique)
DROP TABLE IF EXISTS bourse.dim_company;
CREATE TABLE bourse.company
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
CREATE MATERIALIZED VIEW bourse.company_mv TO bourse.company AS
SELECT
    symbole,
    nom,
    secteur,
    sous_secteur,
    siege,
    toDate(parseDateTimeBestEffortOrNull(date_introduction)) AS date_introduction,
    cik
FROM bourse.company_kafka_queue;

--------------------------------------------------------------------------------------------------------
-- fact prices
DROP TABLE IF EXISTS prices_mv;
DROP TABLE IF EXISTS prices_kafka_queue;
DROP TABLE IF EXISTS prices;

CREATE TABLE bourse.prices (
    id String,
    date Date,              
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

CREATE TABLE bourse.prices_queue (
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

CREATE MATERIALIZED VIEW bourse.prices_mv TO bourse.prices AS
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
FROM bourse.prices_queue;


--------------------------------------------------------------------------------------------------------

-- Table de jointure dans trino
CREATE VIEW bourse.prices_analytics AS
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
FROM bourse.prices p
LEFT JOIN bourse.company c ON p.symbole = c.symbole;

--------------------------------------------------------------------------
----fundamentals

DROP TABLE IF EXISTS bourse.fundamentals;

CREATE TABLE bourse.fundamentals (
    symbole String,
    annee_fiscale Int32,
    date_fin_periode Date,
    revenu_total Float64,  -- CHANGÉ DE Int64
    profit_brut Float64,   -- CHANGÉ DE Int64
    resultat_net Float64,  -- CHANGÉ DE Int64
    resultat_exploitation Float64, -- CHANGÉ DE Int64
    marge_exploitation Float32,
    marge_beneficiaire Float32,
    total_actifs Float64,  -- CHANGÉ DE Int64
    total_passifs Float64, -- CHANGÉ DE Int64
    dette_long_terme Float64, -- CHANGÉ DE Int64
    capitaux_propres Float64, -- CHANGÉ DE Int64
    goodwill Float64,      -- CHANGÉ DE Int64
    ratio_courant Float32,
    ratio_liquidite_immediate Float32,
    benefice_par_action Float32,
    rentabilite_fonds_propres_roe Float32
) 
ENGINE = MergeTree()
ORDER BY (symbole, annee_fiscale);


CREATE TABLE bourse.fundamentals_queue (
    symbole String,
    annee_fiscale String,
    date_fin_periode String,
    revenu_total String,
    profit_brut String,
    resultat_net String,
    resultat_exploitation String,
    marge_exploitation String,
    marge_beneficiaire String,
    total_actifs String,
    total_passifs String,
    dette_long_terme String,
    capitaux_propres String,
    goodwill String,
    ratio_courant String,
    ratio_liquidite_immediate String,
    benefice_par_action String,
    rentabilite_fonds_propres_roe String
)
ENGINE = Kafka
SETTINGS 
    kafka_broker_list = 'kafka:29092', 
    kafka_topic_list = 'send_fundamentals',
    kafka_group_name = 'group_final_reborn_v1', -- Nouveau nom pour tout relire
    kafka_format = 'JSONEachRow';


CREATE MATERIALIZED VIEW bourse.fundamentals_mv TO bourse.fundamentals AS
SELECT 
    symbole,
    -- On convertit d'abord en Float pour accepter le ".0", puis en UInt32
    toUInt32(toFloat64OrZero(annee_fiscale)) AS annee_fiscale,
    toDateOrZero(date_fin_periode) AS date_fin_periode,
    -- On utilise toFloat64 partout car tes données Kafka sont en notation scientifique (ex: 2.48E10)
    toFloat64OrZero(revenu_total) AS revenu_total,
    toFloat64OrZero(profit_brut) AS profit_brut,
    toFloat64OrZero(resultat_net) AS resultat_net,
    toFloat64OrZero(resultat_exploitation) AS resultat_exploitation,
    toFloat32OrZero(marge_exploitation) AS marge_exploitation,
    toFloat32OrZero(marge_beneficiaire) AS marge_beneficiaire,
    toFloat64OrZero(total_actifs) AS total_actifs,
    toFloat64OrZero(total_passifs) AS total_passifs,
    toFloat64OrZero(dette_long_terme) AS dette_long_terme,
    toFloat64OrZero(capitaux_propres) AS capitaux_propres,
    toFloat64OrZero(goodwill) AS goodwill,
    toFloat32OrZero(ratio_courant) AS ratio_courant,
    toFloat32OrZero(ratio_liquidite_immediate) AS ratio_liquidite_immediate,
    toFloat32OrZero(benefice_par_action) AS benefice_par_action,
    toFloat32OrZero(rentabilite_fonds_propres_roe) AS rentabilite_fonds_propres_roe
FROM bourse.fundamentals_queue;

--------------------------------------------------------------------------------------------------------
CREATE VIEW bourse.fundamentals_analytics AS
SELECT 
    -- Données COMPANY (c)
    c.nom,
    c.secteur,
    c.sous_secteur,
    c.siege,
    c.date_introduction,
    
    -- Données FUNDAMENTALS (f)
    f.symbole,
    f.annee_fiscale,
    f.date_fin_periode,
    f.revenu_total,
    f.profit_brut,
    f.resultat_net,
    f.resultat_exploitation,
    f.marge_exploitation,
    f.marge_beneficiaire,
    f.total_actifs,
    f.total_passifs,
    f.dette_long_terme,
    f.capitaux_propres,
    f.goodwill,
    f.ratio_courant,
    f.ratio_liquidite_immediate,
    f.benefice_par_action,
    f.rentabilite_fonds_propres_roe

FROM bourse.fundamentals f
LEFT JOIN bourse.company c ON f.symbole = c.symbole;