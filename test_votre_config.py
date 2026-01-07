#!/usr/bin/env python3
"""
Test spécifique pour votre configuration NiFi
"""
import json
from kafka import KafkaConsumer
import time
from datetime import datetime

def tester_topic_kafka(topic_name):
    """Teste si un topic spécifique reçoit des données"""
    print(f"\n🔍 Test du topic: '{topic_name}'")
    
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        consumer_timeout_ms=5000  # 5 secondes
    )
    
    messages = []
    start_time = time.time()
    
    print(f"Attente de données sur le topic '{topic_name}'...")
    
    while time.time() - start_time < 5:
        batch = consumer.poll(timeout_ms=1000)
        
        if batch:
            for tp, msgs in batch.items():
                for msg in msgs:
                    try:
                        data = json.loads(msg.value.decode('utf-8'))
                        messages.append(data)
                        print(f"✅ Message reçu à {datetime.now().strftime('%H:%M:%S')}")
                    except Exception as e:
                        print(f"⚠️  Message raw: {msg.value[:50]}...")
        
        # Afficher un indicateur de progression
        print(".", end="", flush=True)
    
    consumer.close()
    
    if messages:
        print(f"\n🎉 SUCCÈS: {len(messages)} message(s) reçu(s) sur '{topic_name}'")
        
        # Afficher le premier message
        print("\nPremier message reçu:")
        for key, value in messages[0].items():
            print(f"  {key}: {value}")
        
        return True
    else:
        print(f"\n❌ ÉCHEC: Aucun message sur '{topic_name}'")
        return False

def lister_topics_kafka():
    """Liste tous les topics Kafka disponibles"""
    print("\n📋 Liste des topics Kafka:")
    
    try:
        from kafka import KafkaAdminClient
        from kafka.admin import KafkaAdminClient, NewTopic
        from kafka.errors import UnknownTopicOrPartitionError
        
        admin = KafkaAdminClient(bootstrap_servers='localhost:9092')
        topics = admin.list_topics()
        admin.close()
        
        print("Topics disponibles:")
        for topic in sorted(topics):
            print(f"  - {topic}")
        
        return topics
    except Exception as e:
        print(f"Erreur: {e}")
        # Fallback avec docker
        import subprocess
        cmd = 'docker exec kafka kafka-topics --list --bootstrap-server localhost:9092'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print("Topics (via docker):")
            for line in result.stdout.strip().split('\n'):
                if line and not line.startswith('__'):
                    print(f"  - {line}")
            return result.stdout.strip().split('\n')
        else:
            print("Impossible de récupérer les topics")
            return []

def creer_topic_si_inexistant(topic_name):
    """Crée le topic s'il n'existe pas"""
    print(f"\n🔧 Vérification du topic '{topic_name}'...")
    
    topics = lister_topics_kafka()
    
    if topic_name in topics or any(topic_name in str(t) for t in topics):
        print(f"✅ Topic '{topic_name}' existe déjà")
        return True
    else:
        print(f"⚠️  Topic '{topic_name}' n'existe pas, création...")
        
        try:
            import subprocess
            cmd = f'docker exec kafka kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic {topic_name}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Topic '{topic_name}' créé avec succès")
                return True
            else:
                print(f"❌ Échec création: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

def main():
    print("="*60)
    print("TEST DE VOTRE CONFIGURATION NiFi")
    print("="*60)
    
    # 1. Lister tous les topics
    topics = lister_topics_kafka()
    
    # 2. Tester avec VOTRE nom de topic
    # Selon votre configuration, le topic devrait être 'securities'
    # (car filename: 'securities.csv' → substringBefore('.') → 'securities')
    
    votre_topic = 'securities'  # C'est ce que votre NiFi devrait créer
    
    print(f"\n🎯 Votre configuration NiFi devrait créer le topic: '{votre_topic}'")
    print(f"   (car fichiers CSV → UpdateAttribute → kafka.topic = ${{filename:substringBefore('.')}})")
    
    # 3. Créer le topic s'il n'existe pas
    creer_topic_si_inexistant(votre_topic)
    
    # 4. Tester aussi d'autres topics possibles
    topics_a_tester = [
        votre_topic,
        'securities.csv',  # Au cas où l'expression ne fonctionne pas
        'test_topic',
        'fundamentales',
        'prices'
    ]
    
    print("\n" + "="*60)
    print("DÉBUT DES TESTS")
    print("="*60)
    
    succes = False
    for topic in topics_a_tester:
        if tester_topic_kafka(topic):
            succes = True
            print(f"\n💡 Conseil: Votre NiFi envoie sur le topic '{topic}'")
            print("   Vérifiez que PublishKafka a bien: Topic Name = ${kafka.topic}")
            break
    
    if not succes:
        print("\n" + "="*60)
        print("DIAGNOSTIC")
        print("="*60)
        print("\nProblèmes possibles:")
        print("1. NiFi n'envoie pas vers Kafka")
        print("2. Mauvais nom de topic dans PublishKafka")
        print("3. Processeurs NiFi arrêtés")
        print("4. Données bloquées dans une file")
        
        print("\n🔧 Actions à faire dans NiFi:")
        print("1. Vérifiez que tous les processeurs sont démarrés (verts)")
        print("2. Cliquez droit sur UpdateAttribute → View data provenance")
        print("3. Vérifiez que 'kafka.topic' est bien défini")
        print("4. Videz les files si elles sont pleines")

if __name__ == "__main__":
    main()