import time
from clickhouse_driver import Client
from pymongo import MongoClient

# Connexion aux deux mondes
ch = Client(host='localhost', port=9000, user='default', password='admin')
mongo = MongoClient('mongodb://localhost:27017/')
db_cache = mongo['bourse_cache']
col_stats = db_cache['market_summary']

def sync_job():
    print("⏳ Agrégation des données dans ClickHouse...")
    
    # On calcule le prix moyen, max et le volume total par action
    query = """
    SELECT 
        symbole, 
        avg(prix_cloture) as prix_moyen,
        max(prix_haut) as high_24h,
        sum(volume) as volume_total,
        max(date) as derniere_maj,
        avgIf(prix_cloture, date >= '2024-01-01') as prix_moyen_recent,
        stddevPop(prix_cloture),                    -- KPI 2 (Volatilité Écart-type)
        avg((prix_cloture - prix_ouverture) / prix_ouverture) * 100 as variation_moyenne
    FROM bourse.prices_analytics
    GROUP BY symbole
    """
    
    try:
        data = ch.execute(query)
        
        for row in data:
            # Structure du document JSON pour MongoDB
            stats_doc = {
                "ticker": row[0],
                "avg_price": round(row[1], 2),
                "day_high": row[2],
                "total_volume": row[3],
                "timestamp": str(row[4]),
                "avg_price_recent": round(row[5], 2) if row[5] else None,
                # Nouveau KPI : Volatilité (Écart-type)
                "risk_metrics": {
                    "volatility_std_dev": round(row[6], 3) if row[6] else 0,
                    "description": "Écart-type de la population des prix de clôture"
                },
                # AJOUT DU KPI 3
                "performance_metrics": {
                    "avg_daily_change_pct": round(row[7], 2) if row[7] else 0,
                    "status": "POSITIVE" if row[7] and row[7] > 0 else "NEGATIVE"
                }
            }
            
            
            # Upsert : si le symbole existe on met à jour, sinon on crée
            col_stats.replace_one({"ticker": row[0]}, stats_doc, upsert=True)
            
        print(f"🚀 Succès : {len(data)} symboles mis en cache dans MongoDB.")
        
    except Exception as e:
        print(f"❌ Erreur lors de la synchro : {e}")

if __name__ == "__main__":
    # On le fait tourner une première fois
    sync_job()