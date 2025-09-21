#!/usr/bin/env bash
set -euo pipefail

# Create main topics for data sources
/opt/kafka/bin/kafka-topics.sh --create --topic honeypot-cowrie   --bootstrap-server localhost:9092 --partitions 3  --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic honeypot-dionaea  --bootstrap-server localhost:9092 --partitions 2  --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic honeypot-tpot     --bootstrap-server localhost:9092 --partitions 5  --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic firewall-paloalto --bootstrap-server localhost:9092 --partitions 10 --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic firewall-fortinet --bootstrap-server localhost:9092 --partitions 5  --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic firewall-pfsense  --bootstrap-server localhost:9092 --partitions 3  --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic siem-splunk       --bootstrap-server localhost:9092 --partitions 5  --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic siem-elastic      --bootstrap-server localhost:9092 --partitions 5  --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic siem-qradar       --bootstrap-server localhost:9092 --partitions 3  --replication-factor 1

# Processed/enriched data
/opt/kafka/bin/kafka-topics.sh --create --topic processed-security-events --bootstrap-server localhost:9092 --partitions 6 --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic enriched-events           --bootstrap-server localhost:9092 --partitions 5 --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic ml-predictions            --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic alerts-critical           --bootstrap-server localhost:9092 --partitions 2 --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --create --topic response-actions          --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# List topics
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
