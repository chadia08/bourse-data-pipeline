from kafka import KafkaProducer
import csv
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

with open('./data/raw/securities.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        producer.send('securities_topic', row)

producer.flush()
print("CSV envoyé dans Kafka")
                