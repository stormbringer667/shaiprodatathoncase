#!/usr/bin/env bash
set -euo pipefail

echo "=== DevSecOps Platform Integration Test ==="
echo "1. Checking services..."
services=(kafka elasticsearch influxdb clickhouse-server neo4j fluent-bit prometheus)
for s in "${services[@]}"; do
  if systemctl is-active --quiet "$s"; then echo "✓ $s running"; else echo "✗ $s NOT running"; fi
done

echo
echo "2. Kafka topics:"
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 || true

echo
echo "3. Sending test event to honeypot-cowrie..."
evt='{"timestamp":"'"$(date -Iseconds)"'","source_ip":"192.168.1.100","destination_ip":"10.0.0.5","source_port":12345,"destination_port":22,"event_type":"ssh_bruteforce","severity":"high","honeypot_type":"cowrie","session_id":"test_session_001","username":"admin","password":"123456"}'
echo "$evt" | /opt/kafka/bin/kafka-console-producer.sh --topic honeypot-cowrie --bootstrap-server localhost:9092

echo
echo "4. Elasticsearch search (may need a few seconds for ingestion)..."
sleep 5
curl -s -X GET "localhost:9200/honeypot-cowrie-*/_search?size=1&sort=@timestamp:desc" -H 'Content-Type: application/json' | jq '.hits.total.value' || true

echo
echo "5. InfluxDB databases:"
influx -execute 'SHOW DATABASES' 2>/dev/null || echo "Influx v2 or not accessible"

echo
echo "6. ClickHouse databases:"
clickhouse-client --query "SHOW DATABASES" 2>/dev/null || echo "ClickHouse not accessible"

echo
echo "7. Neo4j ping:"
echo 'RETURN "Neo4j OK" as status;' | cypher-shell -u neo4j -p your_password 2>/dev/null || echo "Neo4j not accessible"

echo
echo "8. Open ports:"
ss -tlnp | grep -E ':(9092|9200|8086|9000|7474|2020|9090|3000)' || true

echo "=== Done ==="
