import json
import time
import random
import pandas as pd
from datetime import datetime, timedelta
from kafka import KafkaProducer

# --- CONFIGURATION ---
TOPIC_NAME = 'generate_prices'
KAFKA_SERVER = 'localhost:9092'
CSV_FILE = 'Data/Raw/securities.csv'

# --- INITIALISATION KAFKA ---
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# --- CHARGEMENT DES SYMBOLES ---
try:
    df = pd.read_csv(CSV_FILE)
    SYMBOLS = df['Ticker symbol'].tolist()
except Exception as e:
    print(f"Erreur CSV: {e}")
    SYMBOLS = ['AAPL', 'MSFT', 'GOOGL'] # Secours

# --- INITIALISATION DE LA MÉMOIRE ---
# On commence tous au 01/01/2017
current_sim_date = datetime(2017, 1, 1)
# Un dictionnaire pour garder le dernier prix de chaque entreprise
last_prices = {s: random.uniform(50.0, 500.0) for s in SYMBOLS}

print(f"Démarrage de la simulation pour {len(SYMBOLS)} entreprises.")

try:
    while True:
        # Vérification si on a dépassé la date d'aujourd'hui
        if current_sim_date > datetime.now():
            print("Date limite atteinte. Redémarrage en 2017...")
            current_sim_date = datetime(2017, 1, 1)

        print(f"Génération de la journée : {current_sim_date.strftime('%Y-%m-%d')}")

        # Pour chaque journée, on traite TOUTES les entreprises
        # On peut envoyer par petits lots (ex: 50 entreprises par message) 
        # pour ne pas saturer un seul message Kafka
        batch_size = 50
        for i in range(0, len(SYMBOLS), batch_size):
            chunk = SYMBOLS[i:i + batch_size]
            messages_to_send = []

            for s in chunk:
                # Logique financière
                drift = 0.0002
                volatility = 0.012
                change_pct = drift + (volatility * random.gauss(0, 1))

                open_price = last_prices[s]
                close_price = open_price * (1 + change_pct)
                high_price = max(open_price, close_price) * (1 + abs(random.gauss(0, 0.002)))
                low_price = min(open_price, close_price) * (1 - abs(random.gauss(0, 0.002)))

                record = {
                    "date": current_sim_date.strftime("%Y-%m-%d"),
                    "symbol": s,
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": round(random.uniform(1000000, 5000000), 0)
                }
                
                messages_to_send.append(record)
                last_prices[s] = close_price # Sauvegarde pour le jour suivant

            # Envoi du lot de 50 entreprises à Kafka
            producer.send(TOPIC_NAME, messages_to_send)

        # Une fois que toutes les entreprises sont envoyées pour cette date :
        # On passe au jour suivant
        current_sim_date += timedelta(days=1)

        # Pause de 10 secondes avant de générer la date suivante
        time.sleep(10)

except KeyboardInterrupt:
    print("\nSimulateur arrêté.")
finally:
    producer.close()