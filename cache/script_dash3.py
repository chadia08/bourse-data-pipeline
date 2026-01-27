import pandas as pd
from clickhouse_connect import get_client
from pymongo import MongoClient
from datetime import datetime

# 1. Connexion
try:
    ch_client = get_client(host='localhost', username='default', password='admin', port=8123)
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db_mongo = mongo_client["bourse_cache"]
    collection_mom = db_mongo["kpi_momentum"]
    print("Connexion réussie.")
except Exception as e:
    print(f"Erreur : {e}")
    exit()

def aggregate_momentum():
    print(f"Calcul des indicateurs de Momentum (Step-by-Step)... {datetime.now()}")

    # Requête décomposée pour éviter l'imbrication illégale
    query = """
    WITH 
    -- Etape 1 : Calcul des différences de prix simples
    step1 AS (
        SELECT 
            symbole, date, prix_cloture, volume,
            prix_cloture - any(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING) as diff
        FROM bourse.prices
    ),
    -- Etape 2 : Calcul des moyennes pour RSI et Perf
    step2 AS (
        SELECT 
            symbole, date, prix_cloture, volume,
            avg(if(diff > 0, diff, 0)) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 14 PRECEDING AND CURRENT ROW) as avg_gain,
            avg(if(diff < 0, abs(diff), 0)) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 14 PRECEDING AND CURRENT ROW) as avg_loss,
            any(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 5 PRECEDING AND 5 PRECEDING) as price_5j_ago,
            avg(volume) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING) as avg_vol_30j,
            min(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) as min_30j,
            max(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) as max_30j
        FROM step1
    )
    -- Etape 3 : Calcul des KPIs finaux sur la date la plus récente
    SELECT 
        symbole,
        round(((prix_cloture - price_5j_ago) / nullIf(price_5j_ago, 0)) * 100, 2) as perf_5j,
        round(volume / nullIf(avg_vol_30j, 0), 2) as rvol,
        round(100 - (100 / (1 + (avg_gain / nullIf(avg_loss, 0)))), 2) as rsi,
        round(((min_30j - max_30j) / nullIf(max_30j, 0)) * 100, 2) as max_drawdown
    FROM step2
    WHERE date = (SELECT max(date) FROM bourse.prices)
    """
    
    try:
        df = ch_client.query_df(query)
        df = df.fillna(0)

        collection_mom.delete_many({})

        if not df.empty:
            documents = []
            for _, row in df.iterrows():
                documents.append({
                    "Symbole": row['symbole'],
                    "KPI_Momentum": {
                        "Performance_5J_PCT": float(row['perf_5j']),
                        "Volume_Relatif_RVOL": float(row['rvol']),
                        "RSI_14J": float(row['rsi']),
                        "Max_Drawdown_30J_PCT": float(row['max_drawdown'])
                    },
                    "Derniere_MAJ": datetime.now()
                })
            
            collection_mom.insert_many(documents)
            print(f"Cache 'kpi_momentum' mis à jour : {len(documents)} symboles.")
        else:
            print("Aucune donnée retournée par ClickHouse.")

    except Exception as e:
        print(f"Erreur SQL : {e}")

if __name__ == "__main__":
    aggregate_momentum()