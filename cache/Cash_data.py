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
    print(f"🚀 Début de l'extraction ClickHouse... {datetime.now()}")
    
    # MODIFICATION : Jointure avec les fondamentaux pour le KPI 5
    query = """
    SELECT 
        p.symbole, p.date, p.prix_cloture, p.prix_ouverture, p.variation, p.volume,
        f.profit_margin, f.roe, f.debt_to_equity
    FROM bourse.prices p
    LEFT JOIN bourse.fondamentals f ON p.symbole = f.symbol
    """
    df = ch_client.query_df(query)
    
    # Tri crucial pour le calcul des SMA et de la Volatilité
    df = df.sort_values(['symbole', 'date'])
    
    aggregated_data = []

    for symbole, group in df.groupby('symbole'):
        # --- Calcul des Features Techniques ---
        group['sma_20'] = group['prix_cloture'].rolling(window=20).mean()
        group['sma_50'] = group['prix_cloture'].rolling(window=50).mean()
        
        # Volatilité (KPI 3 corrigé) : Écart-type des rendements quotidiens
        group['returns'] = group['prix_cloture'].pct_change()
        group['volatility'] = group['returns'].rolling(window=20).std() * np.sqrt(252)
        
        # --- Calcul de la Résilience (KPI 4 - Drawdown) ---
        rolling_max = group['prix_cloture'].rolling(window=252, min_periods=1).max()
        group['drawdown'] = (group['prix_cloture'] - rolling_max) / rolling_max

        # Target ML : 1 si hausse demain
        group['target'] = (group['prix_cloture'].shift(-1) > group['prix_cloture']).astype(int)

        # Nettoyage des NaNs (causés par les fenêtres rolling)
        features_df = group.dropna(subset=['sma_50', 'volatility'])
        
        for _, row in features_df.iterrows():
            aggregated_data.append({
                "symbole": row['symbole'],
                "date": row['date'], # MongoDB gère bien les objets datetime
                "metrics": {
                    "prix_cloture": float(row['prix_cloture']),
                    "variation": float(row['variation']),
                    "volume": int(row['volume']),
                    "drawdown": float(row['drawdown'])
                },
                "features_ml": {
                    "sma_20": float(row['sma_20']),
                    "sma_50": float(row['sma_50']),
                    "volatility": float(row['volatility'])
                },
                "fondamentals": {
                    "profit_margin": float(row.get('profit_margin', 0)),
                    "roe": float(row.get('roe', 0)),
                    "debt_to_equity": float(row.get('debt_to_equity', 0))
                },
                "target": int(row['target'])
            })

    # 3. Insertion optimisée dans MongoDB
    if aggregated_data:
        collection_ml.delete_many({}) 
        # Utilisation de batch_size pour éviter de saturer la RAM
        collection_ml.insert_many(aggregated_data)
        print(f"✅ Terminé : {len(aggregated_data)} documents synchronisés.")

if __name__ == "__main__":
    generate_cache_for_ml()