import re, json, socket
from datetime import datetime
from kafka import KafkaProducer

class FirewallKafkaProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )
        self.paloalto_pattern = re.compile(
            r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
            r'(?P<device>\S+)\s+(?P<log_type>\w+):\s*.*src=(?P<src_ip>\d+\.\d+\.\d+\.\d+)\s+.*'
            r'dst=(?P<dst_ip>\d+\.\d+\.\d+\.\d+)\s+.*sport=(?P<src_port>\d+)\s+.*dport=(?P<dst_port>\d+)\s+.*'
            r'action=(?P<action>\w+)'
        )

    def process_paloalto_log(self, log_line: str):
        m = self.paloalto_pattern.search(log_line)
        if not m:
            return
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'firewall_vendor': 'paloalto',
            'source_ip': m.group('src_ip'),
            'destination_ip': m.group('dst_ip'),
            'source_port': int(m.group('src_port')),
            'destination_port': int(m.group('dst_port')),
            'action': m.group('action'),
            'log_type': m.group('log_type'),
            'device': m.group('device'),
            'severity': self.get_severity(m.group('action')),
            'raw_log': log_line
        }
        self.producer.send('firewall-paloalto', value=event)

    def get_severity(self, action: str) -> str:
        a = (action or '').lower()
        if a in ['deny', 'drop', 'block']:
            return 'medium'
        if a in ['allow', 'permit']:
            return 'low'
        return 'info'


def run_udp_syslog(host='0.0.0.0', port=514):
    prod = FirewallKafkaProducer()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"Syslog server started on {host}:{port}")
    while True:
        try:
            data, _ = sock.recvfrom(65507)
            msg = data.decode('utf-8', errors='ignore')
            if 'paloalto' in msg.lower():
                prod.process_paloalto_log(msg)
        except Exception as e:
            print("Syslog error:", e)


if __name__ == "__main__":
    run_udp_syslog()
