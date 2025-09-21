#!/usr/bin/env bash
set -euo pipefail

echo "Initializing DevSecOps databases..."
sleep 5

# Kafka topics (safe defaults)
/opt/kafka/bin/kafka-topics.sh --create --topic honeypot-cowrie --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 || true
/opt/kafka/bin/kafka-topics.sh --create --topic processed-security-events --bootstrap-server localhost:9092 --partitions 6 --replication-factor 1 || true
/opt/kafka/bin/kafka-topics.sh --create --topic alerts-critical --bootstrap-server localhost:9092 --partitions 2 --replication-factor 1 || true

# Elasticsearch templates
bash "$(dirname "$0")/../02-elasticsearch/create_templates.sh" || true

# ClickHouse DDL
clickhouse-client --multiquery --query="$(cat "$(dirname "$0")/../04-clickhouse/schema.sql")" || true

# Neo4j constraints
cat "$(dirname "$0")/../05-neo4j/setup.cql" | cypher-shell -u neo4j -p your_password || true

echo "Done."
