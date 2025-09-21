from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import json
from datetime import datetime

class KafkaElasticsearchConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'honeypot-cowrie', 'honeypot-dionaea', 'honeypot-tpot',
            'firewall-paloalto', 'firewall-fortinet', 'firewall-pfsense',
            'siem-splunk', 'siem-elastic', 'siem-qradar',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='elasticsearch-consumer',
            enable_auto_commit=True,
            auto_offset_reset='latest'
        )
        self.es = Elasticsearch(['http://localhost:9200'])

    def start(self):
        for msg in self.consumer:
            try:
                topic = msg.topic
                date_suffix = datetime.utcnow().strftime('%Y.%m')
                index_name = f"{topic}-{date_suffix}"
                doc = msg.value
                doc['kafka_metadata'] = {
                    'topic': topic,
                    'partition': msg.partition,
                    'offset': msg.offset,
                    'key': msg.key.decode('utf-8') if msg.key else None
                }
                self.es.index(index=index_name, document=doc)
            except Exception as e:
                print("Indexing error:", e)


if __name__ == "__main__":
    KafkaElasticsearchConsumer().start()
