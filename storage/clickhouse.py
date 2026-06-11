import clickhouse_connect

def get_client():
    # In production, these should be environment variables
    return clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='verdict',
        password='verdict_password',
        database='verdict'
    )

def setup_tables():
    client = get_client()
    # Create the traces table
    # We use MergeTree which is standard for ClickHouse
    client.command("""
    CREATE TABLE IF NOT EXISTS traces (
        trace_id UUID,
        project_id Int32,
        user_id String,
        session_id String,
        prompt_version String,
        model String,
        prompt String,
        response String,
        latency_ms Float64,
        prompt_tokens Int32,
        completion_tokens Int32,
        total_tokens Int32,
        timestamp DateTime,
        
        -- Evaluation Scores
        faithfulness_score Float32 NULL,
        relevance_score Float32 NULL,
        hallucination_score Float32 NULL,
        agent_success Int8 NULL,
        cost Float64 NULL
    ) ENGINE = MergeTree()
    ORDER BY (project_id, timestamp, trace_id)
    """)
    print("ClickHouse tables setup successfully.")

if __name__ == "__main__":
    setup_tables()
