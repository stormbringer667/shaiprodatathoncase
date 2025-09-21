CREATE DATABASE IF NOT EXISTS security_analytics;
CREATE DATABASE IF NOT EXISTS compliance_reports;

CREATE TABLE IF NOT EXISTS security_analytics.events_summary (
    date Date,
    hour UInt8,
    source_type LowCardinality(String),
    event_type LowCardinality(String),
    severity LowCardinality(String),
    source_ip IPv4,
    destination_ip IPv4,
    country LowCardinality(String),
    event_count UInt64,
    unique_sources UInt32,
    risk_score Float32
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, hour, source_type, event_type)
SETTINGS index_granularity = 8192;

CREATE TABLE IF NOT EXISTS security_analytics.attack_chains (
    chain_id String,
    timestamp DateTime,
    source_ip IPv4,
    attack_sequence Array(String),
    techniques Array(String),
    severity LowCardinality(String),
    duration_minutes UInt32,
    affected_assets Array(String)
) ENGINE = MergeTree()
ORDER BY (timestamp, source_ip)
SETTINGS index_granularity = 8192;

-- Materialized view expects `security_analytics.raw_events` as a Kafka or log ingestion table (create as needed).
CREATE MATERIALIZED VIEW IF NOT EXISTS security_analytics.events_summary_mv
TO security_analytics.events_summary AS
SELECT
    toDate(timestamp) AS date,
    toHour(timestamp) AS hour,
    source_type,
    event_type,
    severity,
    source_ip,
    destination_ip,
    country,
    count() AS event_count,
    uniq(source_ip) AS unique_sources,
    avg(risk_score) AS risk_score
FROM security_analytics.raw_events
GROUP BY date, hour, source_type, event_type, severity, source_ip, destination_ip, country;
