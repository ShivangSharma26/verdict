from storage.clickhouse import get_client

def compare_prompt_versions(project_id: int, version_a: str, version_b: str):
    """
    Compares two prompt versions across average latency, cost, and quality scores.
    """
    client = get_client()
    query = f"""
    SELECT
        prompt_version,
        count() as request_count,
        avg(latency_ms) as avg_latency,
        sum(cost) as total_cost,
        avg(relevance_score) as avg_relevance,
        avg(faithfulness_score) as avg_faithfulness,
        avg(hallucination_score) as avg_hallucination
    FROM traces
    WHERE project_id = {project_id} AND prompt_version IN ('{version_a}', '{version_b}')
    GROUP BY prompt_version
    ORDER BY prompt_version
    """
    result = client.query(query)
    
    report = {}
    for row in result.result_rows:
        v, reqs, lat, cost, rel, faith, hal = row
        report[v] = {
            "requests": reqs,
            "avg_latency_ms": lat,
            "total_cost": cost,
            "avg_relevance": rel,
            "avg_faithfulness": faith,
            "avg_hallucination": hal
        }
    return report

if __name__ == "__main__":
    print(compare_prompt_versions(1, "v1", "v2"))

# Prompt A/B testing framework.
