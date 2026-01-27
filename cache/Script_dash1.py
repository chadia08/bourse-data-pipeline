import pandas as pd
from clickhouse_connect import get_client
from pymongo import MongoClient
from datetime import datetime

# 1. Connexion (Source: ClickHouse, Destination: MongoDB) 
try:
    ch_client = get_client(host='localhost', username='default', password='admin', port=8123)
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db_mongo = mongo_client["bourse_cache"]
    # Nom de collection clair pour Power BI
    collection_prices = db_mongo["kpi_prices"] 
    print("Connexion réussie aux bases de données.")
except Exception as e:
    print(f"Erreur de connexion : {e}")
    exit()

def aggregate_prices_dashboard():
    # Requête SQL avec noms de colonnes explicites
    query = """
    SELECT 
        symbole,
        argMax(prix_cloture, date) as dernier_prix,
        round(((argMax(prix_cloture, date) - argMax(prix_ouverture, date)) / argMax(prix_ouverture, date)) * 100, 2) as variation_journaliere,
        round(stddevPop(variation), 4) as volatilite_30j,
        round(avg(volume), 0) as volume_moyen_30j,
        round(avg(prix_cloture), 2) as prix_moyen_global
    FROM bourse.prices
    GROUP BY symbole
    """
    
    try:
        df = ch_client.query_df(query)
        
        if df.empty:
            print("Aucune donnée trouvée dans ClickHouse.")
            return

        # 2. Nettoyage et Insertion
        # On vide la collection avant pour éviter les vieux résidus (Clean Start)
        collection_prices.delete_many({}) 

        for _, row in df.iterrows():
            document = {
                "Symbole": row['symbole'],
                "KPI_Prices": {
                    "Dernier_Prix": float(row['dernier_prix']),
                    "Variation_PCT": float(row['variation_journaliere']),
                    "Volatilite_30J": float(row['volatilite_30j']),
                    "Volume_Moyen_30J": float(row['volume_moyen_30j']),
                    "Prix_Moyen_Global": float(row['prix_moyen_global'])
                },
                "Derniere_MAJ": datetime.now()
            }
            
            collection_prices.insert_one(document)

        print(f"Cache MongoDB 'kpi_prices' mis à jour : {len(df)} symboles.")

    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")

if __name__ == "__main__":
    aggregate_prices_dashboard()