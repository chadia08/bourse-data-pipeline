import pandas as pd
from clickhouse_connect import get_client
from pymongo import MongoClient
from datetime import datetime

# 1. Connexion
try:
    ch_client = get_client(host='localhost', username='default', password='admin', port=8123)
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db_mongo = mongo_client["bourse_cache"]
    collection_fund = db_mongo["kpi_fundamentals"] 
    print("Connexion réussie.")
except Exception as e:
    print(f"Erreur : {e}")
    exit()

def aggregate_fundamentals():
    print(f"Calcul des KPI Fondamentaux... {datetime.now()}")

    query = """
    SELECT 
        symbole,
        nom,
        secteur,
        -- Correction et calcul des 5 KPIs
        ifNull(round((resultat_net / nullIf(revenu_total, 0)) * 100, 2), 0) as marge_net,
        ifNull(round(rentabilite_fonds_propres_roe / 100, 4), 0) as roe_norm,
        ifNull(round(total_passifs / nullIf(capitaux_propres, 0), 2), 0) as ratio_dette,
        ifNull(round(ratio_courant / 100, 2), 0) as current_ratio_norm,
        revenu_total
    FROM bourse.fundamentals_analytics
    """
    
    try:
        df = ch_client.query_df(query)
        df_latest = df.groupby('symbole').first().reset_index()

        # Nettoyage de la collection pour éviter les anciens doublons
        collection_fund.delete_many({})

        for _, row in df_latest.iterrows():
            document = {
                "Symbole": row['symbole'],
                "Identity": {
                    "Nom": row['nom'],
                    "Secteur": row['secteur']
                },
                "KPI_Fundamentals": {
                    "Marge_Beneficiaire_PCT": float(row['marge_net']),
                    "ROE_Decimal": float(row['roe_norm']),
                    "Ratio_Dette_Equity": float(row['ratio_dette']),
                    "Ratio_Courant": float(row['current_ratio_norm']),
                    "Chiffre_Affaires": float(row['revenu_total'])
                },
                "Derniere_MAJ": datetime.now()
            }
            
            collection_fund.insert_one(document)
        
        print(f"Cache 'kpi_fundamentals' mis à jour : {len(df_latest)} symboles.")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    aggregate_fundamentals()