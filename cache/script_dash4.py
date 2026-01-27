import pandas as pd
import numpy as np
from clickhouse_connect import get_client
from pymongo import MongoClient
from datetime import datetime

# 1. Connexion
try:
    ch_client = get_client(host='localhost', username='default', password='admin', port=8123)
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db_mongo = mongo_client["bourse_cache"]
    collection_inv = db_mongo["kpi_investment"]
    print("Connexion réussie.")
except Exception as e:
    print(f"Erreur de connexion : {e}")
    exit()

def aggregate_investment():
    print(f"Calcul des indicateurs d'investissement (Version robuste)... {datetime.now()}")

    # Requête pour les indicateurs de prix (CAGR, Volatilité, Max Drawdown Historique)
    query_prices = """
    WITH stats AS (
        SELECT 
            symbole,
            argMin(prix_cloture, date) as prix_init,
            argMax(prix_cloture, date) as prix_final,
            -- Calcul de n années (minimum 1 pour éviter division par 0)
            nullIf(dateDiff('year', min(date), max(date)), 0) as n_annees,
            stddevPop(variation) as sigma_daily,
            prix_cloture,
            max(prix_cloture) OVER (PARTITION BY symbole ORDER BY date) as max_so_far
        FROM bourse.prices
        GROUP BY symbole, prix_cloture, date
    )
    SELECT 
        symbole,
        round((pow(prix_final / nullIf(prix_init, 0), 1 / nullIf(n_annees, 1)) - 1) * 100, 2) as cagr,
        round(sigma_daily * sqrt(252) * 100, 2) as vol_annualisee,
        round(min((prix_cloture - max_so_far) / nullIf(max_so_far, 0)) * 100, 2) as max_drawdown_hist
    FROM stats
    GROUP BY symbole, prix_init, prix_final, n_annees, sigma_daily
    """

    # Requête pour les fondamentaux : on n'utilise que les colonnes sûres
    query_fund = """
    SELECT 
        symbole, 
        rentabilite_fonds_propres_roe as roe, 
        marge_beneficiaire, 
        total_passifs / nullIf(capitaux_propres, 0) as ratio_dette
    FROM bourse.fundamentals_analytics
    """

    try:
        df_prices = ch_client.query_df(query_prices)
        df_fund = ch_client.query_df(query_fund)
        
        # Nettoyage des fondamentaux
        df_fund = df_fund.groupby('symbole').first().reset_index()

        collection_inv.delete_many({})
        documents = []

        for _, row in df_prices.iterrows():
            # Calcul du Score de Solidité
            fund_row = df_fund[df_fund['symbole'] == row['symbole']]
            score = 0
            if not fund_row.empty:
                f = fund_row.iloc[0]
                # On ajuste le score sur 3 critères (33 points chacun) car croissance_revenu manque
                if f['roe'] > 15: score += 33
                if f['marge_beneficiaire'] > 10: score += 33
                if f['ratio_dette'] < 0.5: score += 34

            documents.append({
                "Symbole": row['symbole'],
                "KPI_Investment": {
                    "CAGR_Annualise_PCT": float(row['cagr']) if pd.notnull(row['cagr']) else 0,
                    "Volatilite_Annualisee_PCT": float(row['vol_annualisee']) if pd.notnull(row['vol_annualisee']) else 0,
                    "Max_Drawdown_Historique_PCT": float(row['max_drawdown_hist']) if pd.notnull(row['max_drawdown_hist']) else 0,
                    "Score_Solidite_Financiere": int(score)
                },
                "Derniere_MAJ": datetime.now()
            })
        
        if documents:
            collection_inv.insert_many(documents)
            print(f"Cache 'kpi_investment' mis à jour : {len(documents)} symboles.")

    except Exception as e:
        print(f"Erreur durant l'agrégation : {e}")

if __name__ == "__main__":
    aggregate_investment()