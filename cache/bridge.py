import time
import pandas as pd
import numpy as np
from clickhouse_connect import get_client
from pymongo import MongoClient
from datetime import datetime

# --- CONFIGURATION ---
try:
    ch_client = get_client(host='localhost', username='default', password='admin', port=8123)
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["bourse_cache"]
    print("✅ Connexion ClickHouse & MongoDB établie.")
except Exception as e:
    print(f"❌ Erreur de connexion : {e}")
    exit()

# --- 1. FONCTION DASH 1 : PRICES ---
def sync_prices():
    query = """
    SELECT symbole,
           argMax(prix_cloture, date) as dernier_prix,
           round(((argMax(prix_cloture, date) - argMax(prix_ouverture, date)) / argMax(prix_ouverture, date)) * 100, 2) as variation_journaliere,
           round(stddevPop(variation), 4) as volatilite_30j,
           round(avg(volume), 0) as volume_moyen_30j,
           round(avg(prix_cloture), 2) as prix_moyen_global
    FROM bourse.prices GROUP BY symbole """
    df = ch_client.query_df(query)
    for _, row in df.iterrows():
        db.kpi_prices.update_one(
            {"Symbole": row['symbole']},
            {"$set": {
                "KPI_Prices": {
                    "Dernier_Prix": float(row['dernier_prix']),
                    "Variation_PCT": float(row['variation_journaliere']),
                    "Volatilite_30J": float(row['volatilite_30j']),
                    "Volume_Moyen_30J": float(row['volume_moyen_30j']),
                    "Prix_Moyen_Global": float(row['prix_moyen_global'])
                },
                "Derniere_MAJ": datetime.now()
            }}, upsert=True)

# --- 2. FONCTION DASH 2 : FUNDAMENTALS (MISE À JOUR) ---
def sync_fundamentals():
    query = """
    SELECT symbole, nom, secteur,
           ifNull(round((resultat_net / nullIf(revenu_total, 0)) * 100, 2), 0) as marge_net,
           ifNull(round(rentabilite_fonds_propres_roe / 100, 4), 0) as roe_norm,
           ifNull(round(total_passifs / nullIf(capitaux_propres, 0), 2), 0) as ratio_dette,
           ifNull(round(ratio_courant / 100, 2), 0) as current_ratio_norm,
           revenu_total,
           benefice_par_action,
           dividendes
    FROM bourse.fundamentals_analytics """
    
    # On trie par année pour prendre la donnée la plus récente par symbole
    df = ch_client.query_df(query).groupby('symbole').first().reset_index()
    
    for _, row in df.iterrows():
        db.kpi_fundamentals.update_one(
            {"Symbole": row['symbole']},
            {"$set": {
                "Identity": {"Nom": row['nom'], "Secteur": row['secteur']},
                "KPI_Fundamentals": {
                    "Marge_Beneficiaire_PCT": float(row['marge_net']),
                    "ROE_Decimal": float(row['roe_norm']),
                    "Ratio_Dette_Equity": float(row['ratio_dette']),
                    "Ratio_Courant": float(row['current_ratio_norm']),
                    "Chiffre_Affaires": float(row['revenu_total']),
                    "EPS": float(row['benefice_par_action']), # Ajouté
                    "Dividendes": float(row['dividendes'])    # Ajouté
                },
                "Derniere_MAJ": datetime.now()
            }}, upsert=True)

# --- 3. FONCTION DASH 3 : MOMENTUM ---
def sync_momentum():
    query = """
    WITH step1 AS (
        SELECT symbole, date, prix_cloture, volume,
               prix_cloture - any(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING) as diff
        FROM bourse.prices
    ),
    step2 AS (
        SELECT symbole, date, prix_cloture, volume,
               avg(if(diff > 0, diff, 0)) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 14 PRECEDING AND CURRENT ROW) as avg_gain,
               avg(if(diff < 0, abs(diff), 0)) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 14 PRECEDING AND CURRENT ROW) as avg_loss,
               any(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 5 PRECEDING AND 5 PRECEDING) as price_5j_ago,
               avg(volume) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING) as avg_vol_30j,
               min(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) as min_30j,
               max(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) as max_30j
        FROM step1
    )
    SELECT symbole,
           round(((prix_cloture - price_5j_ago) / nullIf(price_5j_ago, 0)) * 100, 2) as perf_5j,
           round(volume / nullIf(avg_vol_30j, 0), 2) as rvol,
           round(100 - (100 / (1 + (avg_gain / nullIf(avg_loss, 0)))), 2) as rsi,
           round(((min_30j - max_30j) / nullIf(max_30j, 0)) * 100, 2) as max_drawdown
    FROM step2 WHERE date = (SELECT max(date) FROM bourse.prices) """
    df = ch_client.query_df(query).fillna(0)
    for _, row in df.iterrows():
        db.kpi_momentum.update_one(
            {"Symbole": row['symbole']},
            {"$set": {
                "KPI_Momentum": {
                    "Performance_5J_PCT": float(row['perf_5j']),
                    "Volume_Relatif_RVOL": float(row['rvol']),
                    "RSI_14J": float(row['rsi']),
                    "Max_Drawdown_30J_PCT": float(row['max_drawdown'])
                },
                "Derniere_MAJ": datetime.now()
            }}, upsert=True)

# --- 4. FONCTION DASH 4 : INVESTMENT ---
def sync_investment():
    query_prices = """
    WITH stats AS (
        SELECT symbole, argMin(prix_cloture, date) as prix_init, argMax(prix_cloture, date) as prix_final,
               nullIf(dateDiff('year', min(date), max(date)), 0) as n_annees,
               stddevPop(variation) as sigma_daily, prix_cloture,
               max(prix_cloture) OVER (PARTITION BY symbole ORDER BY date) as max_so_far
        FROM bourse.prices GROUP BY symbole, prix_cloture, date
    )
    SELECT symbole,
           round((pow(prix_final / nullIf(prix_init, 0), 1 / nullIf(n_annees, 1)) - 1) * 100, 2) as cagr,
           round(sigma_daily * sqrt(252) * 100, 2) as vol_annualisee,
           round(min((prix_cloture - max_so_far) / nullIf(max_so_far, 0)) * 100, 2) as max_drawdown_hist
    FROM stats GROUP BY symbole, prix_init, prix_final, n_annees, sigma_daily """
    
    df_prices = ch_client.query_df(query_prices)
    df_fund = ch_client.query_df("SELECT symbole, rentabilite_fonds_propres_roe as roe, marge_beneficiaire, total_passifs / nullIf(capitaux_propres, 0) as ratio_dette FROM bourse.fundamentals_analytics")
    df_fund = df_fund.groupby('symbole').first().reset_index()

    for _, row in df_prices.iterrows():
        fund_row = df_fund[df_fund['symbole'] == row['symbole']]
        score = 0
        if not fund_row.empty:
            f = fund_row.iloc[0]
            if f['roe'] > 15: score += 33
            if f['marge_beneficiaire'] > 10: score += 33
            if f['ratio_dette'] < 0.5: score += 34

        db.kpi_investment.update_one(
            {"Symbole": row['symbole']},
            {"$set": {
                "KPI_Investment": {
                    "CAGR_Annualise_PCT": float(row['cagr']) if pd.notnull(row['cagr']) else 0,
                    "Volatilite_Annualisee_PCT": float(row['vol_annualisee']) if pd.notnull(row['vol_annualisee']) else 0,
                    "Max_Drawdown_Historique_PCT": float(row['max_drawdown_hist']) if pd.notnull(row['max_drawdown_hist']) else 0,
                    "Score_Solidite_Financiere": int(score)
                },
                "Derniere_MAJ": datetime.now()
            }}, upsert=True)

# --- BOUCLE PRINCIPALE ---
if __name__ == "__main__":
    print("🚀 Démarrage de la synchronisation en temps réel (Fréquence: 5s)...")
    while True:
        try:
            start_time = time.time()
            sync_prices()
            sync_fundamentals()
            sync_momentum()
            sync_investment()
            
            duration = round(time.time() - start_time, 2)
            print(f"✅ Mise à jour effectuée à {datetime.now().strftime('%H:%M:%S')} (Temps: {duration}s)")
            
        except Exception as e:
            print(f"❌ Erreur lors du cycle de synchro : {e}")
        
        time.sleep(5)