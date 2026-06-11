import json
from confluent_kafka import Consumer, KafkaError
from storage.clickhouse import get_client
from eval.judge import evaluate_trace
from datetime import datetime
import uuid

def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    # Basic cost calculation stub
    # In reality, this would lookup pricing from a DB
    prices = {
        "llama3-70b-8192": {"prompt": 0.00059, "completion": 0.00079},
        "llama3-8b-8192": {"prompt": 0.00005, "completion": 0.00008}
    }
    # Pricing is usually per 1k tokens
    price = prices.get(model.lower(), {"prompt": 0.0, "completion": 0.0})
    return (prompt_tokens / 1000.0 * price["prompt"]) + (completion_tokens / 1000.0 * price["completion"])

def start_consumer():
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'verdict-consumer-group',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(conf)
    consumer.subscribe(['verdict-traces'])
    ch_client = get_client()

    print("Kafka Consumer started. Waiting for traces...")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            # Parse the trace event
            trace_json = msg.value().decode('utf-8')
            trace = json.loads(trace_json)
            
            print(f"Received trace: {trace['trace_id']}")

            # Evaluate trace asynchronously (in this simplified version, synchronously)
            scores = evaluate_trace(trace['prompt'], trace['response'])
            
            # Calculate cost
            cost = calculate_cost(trace['model'], trace['prompt_tokens'], trace['completion_tokens'])

            # Prepare row for ClickHouse
            # Convert timestamp to proper datetime format or use current
            ts = trace.get('timestamp', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            if 'T' in ts:
                ts = ts.replace('T', ' ').split('.')[0]

            row = [
                uuid.UUID(trace['trace_id']),
                trace.get('project_id', 1),
                trace.get('user_id', 'anonymous'),
                trace.get('session_id', ''),
                trace.get('prompt_version', 'v1'),
                trace.get('model', 'unknown'),
                trace.get('prompt', ''),
                trace.get('response', ''),
                float(trace.get('latency_ms', 0.0)),
                int(trace.get('prompt_tokens', 0)),
                int(trace.get('completion_tokens', 0)),
                int(trace.get('total_tokens', 0)),
                datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') if isinstance(ts, str) else datetime.utcnow(),
                scores['faithfulness_score'],
                scores['relevance_score'],
                scores['hallucination_score'],
                None, # agent_success
                cost
            ]

            # Insert into ClickHouse
            ch_client.insert('traces', [row], column_names=[
                'trace_id', 'project_id', 'user_id', 'session_id', 'prompt_version', 'model',
                'prompt', 'response', 'latency_ms', 'prompt_tokens', 'completion_tokens', 'total_tokens',
                'timestamp', 'faithfulness_score', 'relevance_score', 'hallucination_score', 'agent_success', 'cost'
            ])
            print(f"Trace {trace['trace_id']} saved to ClickHouse.")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    start_consumer()
