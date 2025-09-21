# flink_security_processor.py
# NOTE: This is a template; configure PyFlink connectors per your environment.
from pyflink.table import EnvironmentSettings, TableEnvironment

def main():
    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = TableEnvironment.create(env_settings)

    t_env.execute_sql("""
        CREATE TABLE security_events (
            timestamp STRING,
            source_ip STRING,
            destination_ip STRING,
            event_type STRING,
            severity STRING,
            source_type STRING,
            raw_data STRING
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'honeypot-cowrie',
            'properties.bootstrap.servers' = 'localhost:9092',
            'properties.group.id' = 'flink-processor',
            'format' = 'json',
            'scan.startup.mode' = 'latest-offset'
        )
    """)

    t_env.execute_sql("""
        CREATE TABLE correlated_events (
            window_start TIMESTAMP(3),
            window_end   TIMESTAMP(3),
            source_ip    STRING,
            event_count  BIGINT,
            severity_levels STRING,
            attack_types   STRING
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'processed-security-events',
            'properties.bootstrap.servers' = 'localhost:9092',
            'format' = 'json'
        )
    """)

    t_env.execute_sql("""
        INSERT INTO correlated_events
        SELECT
            WINDOW_START, WINDOW_END, source_ip,
            COUNT(*) AS event_count,
            LISTAGG(DISTINCT severity) AS severity_levels,
            LISTAGG(DISTINCT event_type) AS attack_types
        FROM TABLE(
            TUMBLE(TABLE security_events, DESCRIPTOR(timestamp), INTERVAL '5' MINUTES)
        )
        WHERE source_ip IS NOT NULL
        GROUP BY WINDOW_START, WINDOW_END, source_ip
        HAVING COUNT(*) > 10
    """)

if __name__ == "__main__":
    main()
