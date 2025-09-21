import psutil, json, socket, time, subprocess
from datetime import datetime
from kafka import KafkaProducer

SERVICES = {
    'kafka':         {'port': 9092, 'process': 'kafka'},
    'elasticsearch': {'port': 9200, 'process': 'elasticsearch'},
    'influxdb':      {'port': 8086, 'process': 'influxd'},
    'clickhouse':    {'port': 9000, 'process': 'clickhouse-server'},
    'neo4j':         {'port': 7474, 'process': 'neo4j'},
    'fluent-bit':    {'port': 2020, 'process': 'fluent-bit'},
}

def port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex(('localhost', port)) == 0

def main():
    prod = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'))
    while True:
        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": getattr(psutil, "getloadavg", lambda: (0,0,0))(),
            },
            "services": {},
            "overall_status": "healthy"
        }
        failed = []
        for name, cfg in SERVICES.items():
            s = {"port_open": port_open(cfg["port"]), "process_running": False}
            for p in psutil.process_iter(['name', 'cmdline']):
                try:
                    if cfg['process'] in (p.info.get('name') or '') or any(cfg['process'] in (c or '') for c in (p.info.get('cmdline') or [])):
                        s["process_running"] = True
                        break
                except Exception:
                    pass
            s["healthy"] = s["port_open"] and s["process_running"]
            if not s["healthy"]:
                failed.append(name)
            health["services"][name] = s

        if failed:
            health["overall_status"] = "degraded"
        if health["system"]["cpu_percent"] > 90 or health["system"]["memory_percent"] > 90:
            health["overall_status"] = "critical"

        prod.send("enriched-events", value=health)
        time.sleep(15)

if __name__ == "__main__":
    main()
