import json, asyncio, logging, ipaddress
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
from elasticsearch import Elasticsearch
from influxdb_client import InfluxDBClient
from neo4j import GraphDatabase
import clickhouse_connect
# import openai  # Uncomment if using OpenAI

class DevSecOpsAIAgent:
    def __init__(self):
        self.kafka_consumer = KafkaConsumer(
            'processed-security-events', 'enriched-events',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='ai-agent'
        )
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )
        self.es = Elasticsearch(['http://localhost:9200'])
        self.influx = InfluxDBClient(url="http://localhost:8086", token="your-influx-token")
        self.neo4j = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        self.ch = clickhouse_connect.get_client(host='localhost', port=8123)
        # openai.api_key = "your-openai-api-key"
        self.logger = self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            handlers=[logging.FileHandler("/var/log/ai-security-agent.log"), logging.StreamHandler()]
        )
        return logging.getLogger("AI-Agent")

    async def analyze_security_event(self, event_data: dict):
        try:
            context = await self._gather_context(event_data)
            # ai = await self._llm_analysis(event_data, context)  # Optional: call LLM
            ai = self._rule_based(event_data, context)  # fallback/simple
            actions = await self._determine_actions(ai)
            if ai.get("auto_response"):
                await self._execute_actions(actions)
            await self._notify(ai, actions)
            await self._record(event_data, ai, actions)
            return ai
        except Exception as e:
            self.logger.error("Analyze error: %s", e)
            return {"error": str(e)}

    async def _gather_context(self, ev: dict):
        return {
            "related_events": [],
            "historical_patterns": [],
            "network_context": {},
            "system_metrics": [],
            "threat_intelligence": await self._ti(ev.get("source_ip", ""))
        }

    async def _ti(self, ip: str):
        rep = {"reputation": "unknown", "categories": [], "confidence": 0.0}
        try:
            ipaddress.ip_address(ip)
        except Exception:
            return rep
        # toy examples of ranges
        for cidr in ["10.0.0.0/8", "192.168.0.0/16"]:
            if ipaddress.ip_address(ip) in ipaddress.ip_network(cidr):
                return {"reputation": "suspicious", "categories": ["internal"], "confidence": 0.7}
        return rep

    def _rule_based(self, ev: dict, ctx: dict):
        sev = (ev.get("severity") or "low").lower()
        threat = "low"
        if sev in ["high", "critical"]:
            threat = "high"
        elif sev == "medium":
            threat = "medium"
        return {
            "threat_level": threat,
            "confidence": 0.6 if threat != "low" else 0.4,
            "attack_category": ev.get("event_type", "unknown"),
            "recommendations": [{
                "action": "investigate",
                "priority": "high" if threat == "high" else "medium",
                "description": f"Investigate event {ev.get('event_type')} from {ev.get('source_ip')}",
                "automated": False
            }],
            "auto_response": False
        }

    async def _determine_actions(self, analysis: dict):
        actions = []
        for rec in analysis.get("recommendations", []):
            actions.append({
                "id": f"action_{datetime.utcnow().timestamp()}",
                "type": rec["action"],
                "priority": rec["priority"],
                "description": rec["description"],
                "automated": rec["automated"],
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            })
        return actions

    async def _execute_actions(self, actions):
        for a in actions:
            a["status"] = "completed"
            a["completed_at"] = datetime.utcnow().isoformat()

    async def _notify(self, analysis: dict, actions: list):
        self.kafka_producer.send('alerts-critical', value={
            "ts": datetime.utcnow().isoformat(),
            "threat_level": analysis.get("threat_level"),
            "analysis": analysis,
            "actions": actions
        })

    async def _record(self, event_data, analysis, actions):
        self.es.index(index=f"ml-training-{datetime.utcnow():%Y-%m}", document={
            "event": event_data, "analysis": analysis, "actions": actions, "ts": datetime.utcnow().isoformat()
        })

    async def run(self):
        self.logger.info("AI Agent started")
        try:
            for msg in self.kafka_consumer:
                ev = msg.value
                await self.analyze_security_event(ev)
        finally:
            self.kafka_consumer.close()
            self.kafka_producer.close()
            self.neo4j.close()

if __name__ == "__main__":
    asyncio.run(DevSecOpsAIAgent().run())
