#!/usr/bin/env python3
"""
Test si Kafka reçoit bien les messages depuis NiFi
"""

from kafka import KafkaConsumer
import json

def test_kafka_connection():
    print("=== TEST CONNEXION KAFKA ===")
    
    try:
        # Essayer de se connecter
        consumer = KafkaConsumer(
            bootstrap_servers='localhost:9092',
            group_id='test_group',
            auto_offset_reset='earliest',
            consumer_timeout_ms=5000  # timeout après 5 secondes
        )
        
        # S'abonner au topic
        topics = ['fundamentales', 'prices', 'prices_ajusted', 'securities']
        consumer.subscribe(topics)
        
        print(f"Connecté à Kafka! Topics surveillés: {topics}")
        print("En attente de messages... (attendre 10 secondes)")
        
        # Lire les messages pendant 10 secondes
        messages_recus = 0
        for message in consumer:
            messages_recus += 1
            print(f"\nMessage #{messages_recus}:")
            print(f"  Topic: {message.topic}")
            print(f"  Partition: {message.partition}")
            print(f"  Offset: {message.offset}")
            
            try:
                data = json.loads(message.value.decode('utf-8'))
                print(f"  Données: {data}")
            except:
                print(f"  Données (raw): {message.value}")
            
            if messages_recus >= 3:  # Limiter à 3 messages pour le test
                break
        
        if messages_recus == 0:
            print("⚠️  Aucun message reçu. Vérifiez que NiFi envoie bien les données.")
        else:
            print(f"\n✅ {messages_recus} message(s) reçu(s) avec succès!")
            
        consumer.close()
        
    except Exception as e:
        print(f"❌ Erreur de connexion à Kafka: {e}")
        print("\nVérifiez que:")
        print("1. Kafka est démarré: docker ps | grep kafka")
        print("2. Le topic existe: docker exec kafka kafka-topics --list --bootstrap-server localhost:9092")
        print("3. NiFi est connecté au bon broker: kafka:9092")

if __name__ == "__main__":
    test_kafka_connection()