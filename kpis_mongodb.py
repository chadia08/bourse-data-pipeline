import time
from clickhouse_driver import Client
from pymongo import MongoClient

# Connexion aux services (localhost car tu lances le script depuis le terminal Codespaces)
try:
    ch = Client(host='localhost', port=9000, user='default', password='admin', database='bourse')
    mongo = MongoClient('mongodb://localhost:27017/')
    
    db_cache = mongo['bourse_cache']
    col_stats = db_cache['market_summary']
    print("✅ Connexion ClickHouse et MongoDB établie.")
except Exception as e:
    print(f"❌ Erreur de connexion : {e}")
    exit(1)

def sync_job():
    print("⏳ Agrégation des données dans ClickHouse...")
    
    # ⚠️ VERIFIE LE NOM DE TA TABLE CI-DESSOUS ⚠️
    # Si NiFi a inséré les données dans une table nommée 'fundamentals', change 'prices_analytics' par 'fundamentals'
    query = """
    SELECT 
        Ticker_Symbol, 
        avg(toDecimal64(Net_Income, 2)) as profit_moyen,
        max(toDecimal64(Total_Revenue, 2)) as max_revenu,
        sum(toUInt64(volume)) as volume_total,
        max(Period_Ending) as derniere_maj
    FROM prices_analytics
    GROUP BY Ticker_Symbol
    """
    
    try:
        data = ch.execute(query)
        
        if not data:
            print("pfff... Aucune donnée trouvée dans ClickHouse. As-tu chargé le CSV ?")
            return

        for row in data:
            stats_doc = {
                "ticker": row[0],
                "avg_profit": float(row[1]),
                "max_revenue": float(row[2]),
                "total_volume": int(row[3]),
                "last_update": str(row[4])
            }
            
            # Upsert : Mise à jour si ticker existe, sinon création
            col_stats.replace_one({"ticker": row[0]}, stats_doc, upsert=True)
            
        print(f"🚀 Succès : {len(data)} symboles agrégés et envoyés vers MongoDB.")
        
    except Exception as e:
        # Si l'erreur est "Table prices_analytics doesn't exist", c'est qu'il faut la créer !
        print(f"❌ Erreur lors de l'agrégation : {e}")

if __name__ == "__main__":
    sync_job()