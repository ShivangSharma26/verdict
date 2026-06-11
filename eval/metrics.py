from storage.clickhouse import get_client

def get_latency_percentiles(project_id: int):
    """
    Returns the P50, P90, and P99 latency for a given project from ClickHouse.
    """
    client = get_client()
    query = f"""
    SELECT
        quantiles(0.50, 0.90, 0.99)(latency_ms) as percentiles
    FROM traces
    WHERE project_id = {project_id}
    """
    result = client.query(query)
    if result.result_rows:
        p50, p90, p99 = result.result_rows[0][0]
        return {"p50": p50, "p90": p90, "p99": p99}
    return None

def get_total_cost(project_id: int):
    client = get_client()
    query = f"SELECT sum(cost) FROM traces WHERE project_id = {project_id}"
    result = client.query(query)
    if result.result_rows:
        return result.result_rows[0][0]
    return 0.0

def get_agent_success_rate(project_id: int):
    client = get_client()
    query = f"""
    SELECT sum(agent_success) / count() as success_rate
    FROM traces
    WHERE project_id = {project_id} AND agent_success IS NOT NULL
    """
    result = client.query(query)
    if result.result_rows:
        return result.result_rows[0][0]
    return None
