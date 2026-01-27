import pandas as pd
from clickhouse_connect import get_client
from pymongo import MongoClient
from datetime import datetime

# Connexion aux bases
ch_client = get_client(host='localhost', username='default', password='admin', port=8123)
mongo_client = MongoClient("mongodb://localhost:27017/")
db_mongo = mongo_client["bourse_cache"]
collection_hist = db_mongo["kpi_history"]

def aggregate_dynamic_history():
    print(f"Extraction de l'historique ClickHouse... {datetime.now()}")

    # Extraction dynamique de toutes les colonnes nécessaires par année fiscale
    query = """
    SELECT 
        symbole,
        annee_fiscale,
        revenu_total,
        resultat_net,
        total_actifs,
        capitaux_propres,
        rentabilite_fonds_propres_roe as roe
    FROM bourse.fundamentals_analytics
    ORDER BY annee_fiscale DESC
    """
    
    try:
        df = ch_client.query_df(query)
        if df.empty: return

        # Nettoyage pour mise à jour temps réel
        collection_hist.delete_many({})

        # Groupement par symbole pour créer une structure historique dans MongoDB
        for symbole, group in df.groupby('symbole'):
            history_list = []
            for _, row in group.iterrows():
                history_list.append({
                    "annee": int(row['annee_fiscale']),
                    "revenu": float(row['revenu_total']),
                    "profit": float(row['resultat_net']),
                    "roe": float(row['roe'])
                })
            
            document = {
                "Symbole": symbole,
                "Historique": history_list,
                "annees_disponibles": [item["annee"] for item in history_list],
                "Derniere_MAJ": datetime.now()
            }
            collection_hist.insert_one(document)
            
        print(f"Historique synchronisé pour {len(df['symbole'].unique())} sociétés.")
    except Exception as e:
        print(f"Erreur extraction : {e}")

if __name__ == "__main__":
    aggregate_dynamic_history()