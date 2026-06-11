import json
from confluent_kafka import Producer

# Configuration for Kafka Producer
# In production, these should be configurable via env vars
conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'verdict-fastapi-producer'
}

producer = Producer(conf)

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def produce_trace(trace_dict: dict):
    """
    Pushes a trace event to the Kafka topic 'verdict-traces'.
    """
    topic = 'verdict-traces'
    # Convert trace to json string
    trace_json = json.dumps(trace_dict)
    
    # Asynchronously produce message
    producer.produce(
        topic, 
        trace_json.encode('utf-8'), 
        callback=delivery_report
    )
    # Trigger any available delivery report callbacks
    producer.poll(0)

# Kafka Producer for trace ingestion.
