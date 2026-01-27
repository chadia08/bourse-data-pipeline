import pandas as pd
import numpy as np
from clickhouse_connect import get_client
from pymongo import MongoClient
from datetime import datetime

# 1. Connexion ClickHouse
ch_client = get_client(host='localhost', username='default', password='admin', port=8123)

# 2. Connexion MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db_mongo = mongo_client["bourse_cache"]
collection_ml = db_mongo["ml_features_aggregated"]

def generate_cache_for_ml():
    print(f"Extraction ClickHouse vers MongoDB... {datetime.now()}")
    
    # ÉTAPE 7 : Extraction depuis ClickHouse
    query = "SELECT symbole, date, prix_cloture, variation, volume FROM bourse.prices"
    df = ch_client.query_df(query)
    
    aggregated_data = []
    df = df.sort_values(['symbole', 'date'])

    for symbole, group in df.groupby('symbole'):
        # Calcul des Features obligatoires pour l'Étape 8
        group['sma_20'] = group['prix_cloture'].rolling(window=20).mean()
        group['sma_50'] = group['prix_cloture'].rolling(window=50).mean()
        group['volatility'] = group['variation'].rolling(window=20).std()
        
        # Target : 1 si le prix monte le lendemain, sinon 0
        group['target'] = (group['prix_cloture'].shift(-1) > group['prix_cloture']).astype(int)

        features_df = group.dropna()
        
        for _, row in features_df.iterrows():
            aggregated_data.append({
                "symbole": row['symbole'],
                "date": str(row['date']),
                "features": {
                    "prix_cloture": float(row['prix_cloture']),
                    "variation": float(row['variation']),
                    "sma_20": float(row['sma_20']),
                    "sma_50": float(row['sma_50']),
                    "volatility": float(row['volatility'])
                },
                "target": int(row['target'])
            })

    # Insertion dans le Cache MongoDB
    if aggregated_data:
        collection_ml.delete_many({}) 
        collection_ml.insert_many(aggregated_data)
        print(f"Étape 7 terminée : {len(aggregated_data)} documents stockés pour le ML.")

if __name__ == "__main__":
    generate_cache_for_ml()