#!/usr/bin/env bash
set -euo pipefail

curl -X PUT "localhost:9200/_index_template/honeypot-template"  -H 'Content-Type: application/json' -d @templates/honeypot-template.json
curl -X PUT "localhost:9200/_index_template/firewall-template"  -H 'Content-Type: application/json' -d @templates/firewall-template.json
curl -X PUT "localhost:9200/_index_template/siem-events-template" -H 'Content-Type: application/json' -d @templates/siem-events-template.json
