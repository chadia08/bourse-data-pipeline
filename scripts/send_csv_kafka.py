from kafka import KafkaProducer
import csv
import json
import time

# Configuration du producteur
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# def stream_csv(file_path, topic_name, delay=0.01):
#     print(f"--- Envoi de {file_path} vers le topic {topic_name} ---")
#     try:
#         with open(file_path, newline='', encoding='utf-8') as csvfile:
#             reader = csv.DictReader(csvfile)
#             count = 0
#             for row in reader:
#                 producer.send(topic_name, row)
#                 count += 1
                
#                 # Simulation streaming : petite pause toutes les 100 lignes
#                 if count % 100 == 0:
#                     time.sleep(delay)
            
#             producer.flush()
#             print(f"Terminé : {count} lignes envoyées.\n")
#     except FileNotFoundError:
#         print(f"Erreur : Le fichier {file_path} est introuvable.\n")


def stream_csv(file_path, topic_name, delay=0.01):
    print(f"--- Envoi de {file_path} vers le topic {topic_name} ---")
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        # On force le reader à bien ignorer les espaces autour des noms de colonnes
        reader = csv.DictReader(csvfile, skipinitialspace=True)
            
        count = 0
        for row in reader:
            # NETTOYAGE : Supprimer les clés 'None' ou 'null' si elles existent
            clean_row = {str(k): v for k, v in row.items() if k is not None}
                
            producer.send(topic_name, clean_row)
            count += 1
                
            if count % 100 == 0:
                time.sleep(delay)
            
    producer.flush()
    print(f"Terminé : {count} lignes envoyées.\n")

    
# --- LANCEMENT DES FLUX ---

# Flux 1 : Securities
stream_csv('./data/raw/securities.csv', 'securities_topic')

# Flux 2 : Prices
# stream_csv('./data/raw/prices.csv', 'prices_topic')

# Flux 3 : Fundamentals
# stream_csv('./data/raw/fundamentals.csv', 'fundamentals_topic')

print("Tous les messages sont dans Kafka !")