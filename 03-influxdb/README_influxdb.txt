-- InfluxDB v1-style commands (use with `influx` CLI). For InfluxDB v2, see notes below.

CREATE DATABASE "security_metrics";
CREATE DATABASE "system_metrics";
CREATE DATABASE "performance_metrics";

CREATE RETENTION POLICY "hot_data"  ON "security_metrics" DURATION 90d   REPLICATION 1 DEFAULT;
CREATE RETENTION POLICY "warm_data" ON "security_metrics" DURATION 365d  REPLICATION 1;
CREATE RETENTION POLICY "cold_data" ON "security_metrics" DURATION 2555d REPLICATION 1;

CREATE CONTINUOUS QUERY "hourly_security_events" ON "security_metrics"
BEGIN
  SELECT mean("event_count") AS "mean_events", max("event_count") AS "max_events"
  INTO "security_metrics"."warm_data"."hourly_events"
  FROM "security_metrics"."hot_data"."events"
  GROUP BY time(1h), "source_type", "severity"
END;

CREATE CONTINUOUS QUERY "daily_threat_trends" ON "security_metrics"
BEGIN
  SELECT sum("threat_count") AS "total_threats", mean("risk_score") AS "avg_risk"
  INTO "security_metrics"."warm_data"."daily_threats"
  FROM "security_metrics"."hot_data"."threats"
  GROUP BY time(1d), "threat_type", "source"
END;

-- InfluxDB v2 note:
-- Run `influx setup ...` once, then create buckets and tasks using `influx bucket create` and `influx task create`.
-- Replace with Flux tasks if preferred.
