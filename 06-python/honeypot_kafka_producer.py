from kafka import KafkaProducer
import json, time, subprocess
from datetime import datetime
try:
    import geoip2.database
    GEOIP_ENABLED = True
except Exception:
    GEOIP_ENABLED = False

GEOIP_DB = "/path/to/GeoLite2-City.mmdb"  # TODO: set correct path

class HoneypotKafkaProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        self.geoip_reader = None
        if GEOIP_ENABLED:
            try:
                import geoip2.database
                self.geoip_reader = geoip2.database.Reader(GEOIP_DB)
            except Exception:
                self.geoip_reader = None

    def process_cowrie_log(self, log_line: str):
        try:
            log_data = json.loads(log_line)
        except Exception:
            return

        enriched_event = {
            'timestamp': datetime.utcnow().isoformat(),
            'honeypot_type': 'cowrie',
            'source_ip': log_data.get('src_ip'),
            'source_port': log_data.get('src_port'),
            'destination_port': log_data.get('dst_port', 2222),
            'username': log_data.get('username'),
            'password': log_data.get('password'),
            'command': log_data.get('input', ''),
            'session_id': log_data.get('session'),
            'event_type': log_data.get('eventid'),
            'severity': self.calculate_severity(log_data),
            'raw_log': log_line,
        }

        if self.geoip_reader and enriched_event.get('source_ip'):
            try:
                resp = self.geoip_reader.city(enriched_event['source_ip'])
                enriched_event['geolocation'] = {
                    'country': resp.country.name,
                    'city': resp.city.name,
                    'latitude': float(resp.location.latitude or 0),
                    'longitude': float(resp.location.longitude or 0),
                }
            except Exception:
                pass

        key = f"{enriched_event.get('source_ip')}_{enriched_event['timestamp']}"
        self.producer.send('honeypot-cowrie', key=key, value=enriched_event)

    def calculate_severity(self, log_data: dict) -> str:
        event_id = (log_data.get('eventid') or '').lower()
        if event_id in ['cowrie.login.success', 'cowrie.command.input']:
            return 'high'
        if event_id in ['cowrie.login.failed']:
            return 'medium'
        return 'low'


def follow_file(path: str):
    proc = subprocess.Popen(['tail', '-f', path], stdout=subprocess.PIPE, text=True)
    for line in proc.stdout:
        yield line.strip()


if __name__ == "__main__":
    producer = HoneypotKafkaProducer()
    # Adjust path to your cowrie JSON log file
    for ln in follow_file('/opt/cowrie/var/log/cowrie/cowrie.json'):
        producer.process_cowrie_log(ln)
