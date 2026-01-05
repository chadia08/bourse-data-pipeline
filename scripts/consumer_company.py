# import json
# from datetime import datetime
# from kafka import KafkaConsumer
# import clickhouse_connect

# # --- CONFIGURATION ---
# KAFKA_BROKER = 'localhost:9092'
# KAFKA_TOPIC = 'send_company'
# CH_HOST = 'localhost'
# CH_PORT = 8123
# CH_USER = 'default'
# CH_PASSWORD = 'admin'
# CH_DATABASE = 'bourse'

# def start_bridge():
#     try:
#         client = clickhouse_connect.get_client(host=CH_HOST, port=CH_PORT, 
#                                              username=CH_USER, password=CH_PASSWORD, 
#                                              database=CH_DATABASE)
#         print("✅ Connecté à ClickHouse")
#     except Exception as e:
#         print(f"❌ Erreur connexion ClickHouse: {e}")
#         return

#     try:
#         consumer = KafkaConsumer(
#             KAFKA_TOPIC,
#             bootstrap_servers=[KAFKA_BROKER],
#             auto_offset_reset='earliest',
#             group_id='bridge_consumer_final_v3',
#             value_deserializer=lambda x: json.loads(x.decode('utf-8')),
#             consumer_timeout_ms=10000
#         )
#         print(f"🚀 Bridge démarré sur '{KAFKA_TOPIC}'...")
#     except Exception as e:
#         print(f"❌ Erreur connexion Kafka: {e}")
#         return

#     batch = []
#     batch_size = 100
#     total_inserted = 0

#     for message in consumer:
#         data = message.value
        
#         # --- NETTOYAGE ULTRA-SÉCURISÉ DE LA DATE ---
#         raw_date = data.get('date_introduction')
#         date_obj = None
        
#         if raw_date and str(raw_date).strip().lower() not in ['none', 'null', '', 'nan']:
#             try:
#                 # Tentative de conversion
#                 temp_date = datetime.strptime(str(raw_date).strip(), '%Y-%m-%d').date()
                
#                 # SÉCURITÉ : ClickHouse Date32 supporte 1900-2299
#                 # Si l'année est hors de cette plage (ex: 0001), on force à None
#                 if 1900 <= temp_date.year <= 2299:
#                     date_obj = temp_date
#                 else:
#                     date_obj = None 
#             except (ValueError, TypeError):
#                 date_obj = None

#         row = [
#             str(data.get('symbole', '')),
#             str(data.get('nom', '')),
#             str(data.get('secteur', '')),
#             str(data.get('sous_secteur', '')),
#             str(data.get('siege', '')),
#             date_obj, 
#             str(data.get('cik', ''))
#         ]
#         batch.append(row)

#         if len(batch) >= batch_size:
#             try:
#                 client.insert('dim_company', batch, column_names=[
#                     'symbole', 'nom', 'secteur', 'sous_secteur', 'siege', 'date_introduction', 'cik'
#                 ])
#                 total_inserted += len(batch)
#                 print(f"📥 {total_inserted} lignes insérées...")
#                 batch = []
#             except Exception as e:
#                 print(f"❌ Erreur lors de l'insertion du batch: {e}")
#                 batch = [] # On vide pour ne pas boucler sur l'erreur

#     if batch:
#         client.insert('dim_company', batch, column_names=['symbole', 'nom', 'secteur', 'sous_secteur', 'siege', 'date_introduction', 'cik'])
#         total_inserted += len(batch)
    
#     print(f"🏁 Terminé ! Total : {total_inserted} lignes.")

# if __name__ == "__main__":
#     start_bridge()









import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'send_prices',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    consumer_timeout_ms=3000
)

print("--- ANALYSE DES DONNÉES KAFKA ---")
for message in consumer:
    print("Voici une ligne reçue :")
    print(json.dumps(message.value, indent=2))
    break # On en regarde juste une seule