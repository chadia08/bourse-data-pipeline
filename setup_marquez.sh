curl -X PUT http://localhost:5002/api/v1/sources/clickhouse -H "Content-Type: application/json" -d '{"type": "CLICKHOUSE", "connectionUrl": "jdbc:clickhouse://clickhouse:8123/bourse", "description": "Serveur ClickHouse principal"}'
curl -X PUT http://localhost:5002/api/v1/namespaces/bourse-pipeline -H "Content-Type: application/json" -d '{"ownerName": "mourad", "description": "Pipeline de données boursières"}'
# Les 3 Tables Sources
curl -X PUT http://localhost:5002/api/v1/namespaces/bourse-pipeline/datasets/bourse.company -H "Content-Type: application/json" -d '{"type": "DB_TABLE", "physicalName": "bourse.company", "sourceName": "clickhouse", "description": "Référentiel entreprises"}'
curl -X PUT http://localhost:5002/api/v1/namespaces/bourse-pipeline/datasets/bourse.prices -H "Content-Type: application/json" -d '{"type": "DB_TABLE", "physicalName": "bourse.prices", "sourceName": "clickhouse", "description": "Prix quotidiens"}'
curl -X PUT http://localhost:5002/api/v1/namespaces/bourse-pipeline/datasets/bourse.fundamentals -H "Content-Type: application/json" -d '{"type": "DB_TABLE", "physicalName": "bourse.fundamentals", "sourceName": "clickhouse", "description": "Données financières"}'

# Les 2 Vues Analytics (Cibles)
curl -X PUT http://localhost:5002/api/v1/namespaces/bourse-pipeline/datasets/bourse.prices_analytics -H "Content-Type: application/json" -d '{"type": "DB_TABLE", "physicalName": "bourse.prices_analytics", "sourceName": "clickhouse", "description": "Vue finale Prix"}'
curl -X PUT http://localhost:5002/api/v1/namespaces/bourse-pipeline/datasets/bourse.fundamentals_analytics -H "Content-Type: application/json" -d '{"type": "DB_TABLE", "physicalName": "bourse.fundamentals_analytics", "sourceName": "clickhouse", "description": "Vue finale Fondamentaux"}'
# Lignage pour les Prix
curl -X POST http://localhost:5002/api/v1/lineage -H "Content-Type: application/json" -d '{"eventType": "COMPLETE", "eventTime": "2026-01-12T17:30:00Z", "run": {"runId": "d70f7f32-8491-496a-8686-218f263e7901"}, "job": {"namespace": "bourse-pipeline", "name": "build_prices_analytics"}, "inputs": [{"namespace": "bourse-pipeline", "name": "bourse.prices"}, {"namespace": "bourse-pipeline", "name": "bourse.company"}], "outputs": [{"namespace": "bourse-pipeline", "name": "bourse.prices_analytics"}], "producer": "https://github.com/OpenLineage"}'

# Lignage pour les Fondamentaux
curl -X POST http://localhost:5002/api/v1/lineage -H "Content-Type: application/json" -d '{"eventType": "COMPLETE", "eventTime": "2026-01-12T17:35:00Z", "run": {"runId": "e81g8g43-9502-507b-9797-329g374f8012"}, "job": {"namespace": "bourse-pipeline", "name": "build_fundamentals_analytics"}, "inputs": [{"namespace": "bourse-pipeline", "name": "bourse.fundamentals"}, {"namespace": "bourse-pipeline", "name": "bourse.company"}], "outputs": [{"namespace": "bourse-pipeline", "name": "bourse.fundamentals_analytics"}], "producer": "https://github.com/OpenLineage"}'
