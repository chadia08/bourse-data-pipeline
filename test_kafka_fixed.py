#!/usr/bin/env python3
import json
from kafka import KafkaConsumer, KafkaProducer
import time

# Essayer différentes configurations
BROKERS = [
    'localhost:9092',      # Pour host direct
    '172.18.0.4:9092',     # IP Docker (à remplacer par la vraie)
    'kafka:9092',          # Pour les containers
    'host.docker.internal:9092'  # Pour communication host-container
]

def test_brokers():
    print("Test des brokers Kafka...")
    
    for broker in BROKERS:
        print(f"\nEssai avec: {broker}")
        try:
            # Test producteur
            producer = KafkaProducer(
                bootstrap_servers=broker,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=5000
            )
            
            # Envoyer un message
            producer.send('test_topic', {'test': 'message'})
            producer.flush(timeout=5)
            
            print(f"✅ Producteur OK avec {broker}")
            
            # Test consommateur
            consumer = KafkaConsumer(
                'test_topic',
                bootstrap_servers=broker,
                auto_offset_reset='earliest',
                consumer_timeout_ms=5000
            )
            
            for msg in consumer:
                print(f"✅ Message reçu: {msg.value.decode()}")
                break
                
            consumer.close()
            producer.close()
            return broker  # Retourne le premier broker qui fonctionne
            
        except Exception as e:
            print(f"❌ Erreur avec {broker}: {type(e).__name__}")
    
    return None

if __name__ == "__main__":
    working_broker = test_brokers()
    
    if working_broker:
        print(f"\n🎉 Broker fonctionnel: {working_broker}")
        print("\nUtilisez cette configuration:")
        print(f"1. Dans NiFi: {working_broker}")
        print(f"2. Dans Python: {working_broker}")
    else:
        print("\n❌ Aucun broker ne fonctionne!")
        print("\nVérifiez que:")
        print("1. Kafka tourne: docker ps")
        print("2. Les ports sont exposés: netstat -an | findstr 9092")