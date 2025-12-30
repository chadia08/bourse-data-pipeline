import csv
import json
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_csv_to_kafka(file_path, topic_name, delimiter=';'):
    """
    Envoie un CSV vers Kafka avec gestion du délimiteur et ajout d'un ID.
    """
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            # On détecte automatiquement les colonnes et on applique le délimiteur
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            count = 0
            for row in reader:
                count += 1
                
                # --- AJOUT DE L'ID (Auto-incrémenté) ---
                row['id'] = count
                
                # Envoi vers Kafka
                producer.send(topic_name, value=row)
                
                if count % 1000 == 0:
                    print(f"🚀 {count} lignes envoyées vers {topic_name}...")
            
            producer.flush()
            print(f"✅ Terminé : {count} lignes envoyées au topic {topic_name}.")
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du CSV : {e}")

# --- EXEMPLES D'UTILISATION ---


# send_csv_to_kafka('data/raw/securities.csv', 'securities_topic', delimiter=',')

send_csv_to_kafka('data/raw/prices_test.csv', 'prices_topic', delimiter=',')

# send_csv_to_kafka('data/raw/fundamentals.csv', 'fundamentals_topic', delimiter=',')