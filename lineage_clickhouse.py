from atlasclient.client import Atlas

client = Atlas('localhost', port=21000, username='admin', password='admin')

def create_full_lineage(topic, table_queue, table_final, mv_name):
    # 1. Topic Kafka (Ajout de 'uri' et 'topic' qui sont obligatoires)
    kafka_entity = {
        "entity": {
            "typeName": "kafka_topic",
            "attributes": {
                "name": topic,
                "qualifiedName": f"{topic}@bourse_cluster",
                "clusterName": "bourse_cluster",
                "topic": topic,
                "uri": f"kafka://kafka:9092/{topic}" # Attribut manquant corrigé
            }
        }
    }
    client.entity_post.create(data=kafka_entity)
    
    # 2. Table ClickHouse (DataSet générique)
    table_entity = {
        "entity": {
            "typeName": "DataSet",
            "attributes": {
                "name": table_final,
                "qualifiedName": f"{table_final}@bourse_cluster",
                "description": f"Table finale ClickHouse pour {topic}"
            }
        }
    }
    client.entity_post.create(data=table_entity)

    # 3. Processus (Lien entre Kafka et ClickHouse)
    process = {
        "entity": {
            "typeName": "Process",
            "attributes": {
                "name": f"Sync_{mv_name}",
                "qualifiedName": f"{mv_name}@bourse_cluster",
                "inputs": [{"typeName": "kafka_topic", "uniqueAttributes": {"qualifiedName": f"{topic}@bourse_cluster"}}],
                "outputs": [{"typeName": "DataSet", "uniqueAttributes": {"qualifiedName": f"{table_final}@bourse_cluster"}}]
            }
        }
    }
    client.entity_post.create(data=process)

try:
    print("🚀 Génération du lignage pour Company...")
    create_full_lineage("send_company", "company_kafka_queue", "company", "company_mv")

    print("🚀 Génération du lignage pour Prices...")
    create_full_lineage("send_prices", "prices_queue", "prices", "prices_mv")

    print("🚀 Génération du lignage pour Fundamentals...")
    create_full_lineage("send_fundamentals", "fundamentals_queue", "fundamentals", "fundamentals_mv")

    print("✅ Lignage complet injecté avec succès !")
except Exception as e:
    print(f"❌ Erreur lors de l'injection : {e}")
