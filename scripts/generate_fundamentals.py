import json
import time
import random
import pandas as pd
from kafka import KafkaProducer

# --- CONFIGURATION ---
TOPIC_NAME = 'generate_fundamentals'
KAFKA_SERVER = 'localhost:9092'
CSV_FILE = 'Data/Raw/securities.csv'

# Initialisation du Producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Chargement des symboles
try:
    df = pd.read_csv(CSV_FILE)
    SYMBOLS = df['Ticker symbol'].tolist()
except:
    SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']

def generate_raw_data(year):
    print(f"📤 Envoi des données BRUTES pour l'année : {year}")
    
    for s in SYMBOLS:
        # Simulation des valeurs
        rev = random.uniform(10e9, 100e9)
        profit = rev * 0.4
        
        # ON UTILISE LES ANCIENS NOMS (Format attendu par ta JOLT)
        record = {
            "Ticker Symbol": s,
            "Period Ending": f"{year}-12-31",
            "For Year": int(year),
            "Total Revenue": int(rev),
            "Gross Profit": int(profit),
            "Net Income": int(profit * 0.5),
            "Operating Income": int(profit * 0.8),
            "Operating Margin": round(random.uniform(10, 25), 2),
            "Profit Margin": round(random.uniform(5, 15), 2),
            "Total Assets": int(rev * 2),
            "Total Liabilities": int(rev * 1.2),
            "Long-Term Debt": int(rev * 0.5),
            "Total Equity": int(rev * 0.8),
            "Goodwill": int(rev * 0.1),
            "Current Ratio": round(random.uniform(1.1, 2.5), 2),
            "Quick Ratio": round(random.uniform(0.9, 2.0), 2),
            "Earnings Per Share": round(random.uniform(1, 15), 2),
            "After Tax ROE": round(random.uniform(10, 30), 2)
        }
        
        producer.send(TOPIC_NAME, record)
    
    producer.flush()
    print(f"✅ Lot de l'année {year} envoyé au pipeline NiFi.")

if __name__ == "__main__":
    # Début de la simulation en 2017
    sim_year = 2017
    
    try:
        while True:
            generate_raw_data(sim_year)
            
            # Temps d'attente pour voir le flux passer dans NiFi/Jolt/ClickHouse
            print(f"⏳ Attente avant de générer l'année {sim_year + 1}...")
            time.sleep(10) 
            
            sim_year += 1
            
    except KeyboardInterrupt:
        print("\nSimulation arrêtée.")
    finally:
        producer.close()