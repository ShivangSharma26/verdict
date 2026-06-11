from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pipeline.producer import produce_trace
import uuid

app = FastAPI(title="Verdict Collector API")

class TraceEvent(BaseModel):
    trace_id: Optional[str] = None
    project_id: int = 1
    user_id: Optional[str] = "anonymous"
    session_id: Optional[str] = None
    prompt_version: Optional[str] = "v1"
    model: str
    prompt: str
    response: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

@app.post("/v1/traces")
async def collect_trace(trace: TraceEvent, background_tasks: BackgroundTasks):
    if not trace.trace_id:
        trace.trace_id = str(uuid.uuid4())
    
    # We use background tasks to immediately return a response to the SDK
    # while the trace is being pushed to Kafka
    background_tasks.add_task(produce_trace, trace.dict())
    
    return {"status": "received", "trace_id": trace.trace_id}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# FastAPI server for ingesting LLM traces.
