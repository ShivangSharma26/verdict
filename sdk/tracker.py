import time
import requests
import functools
from datetime import datetime

# In production, this should be an environment variable
VERDICT_COLLECTOR_URL = "http://localhost:8000/v1/traces"

def track_llm(model: str, prompt_version: str = "v1", project_id: int = 1):
    """
    Decorator to trace an LLM call.
    Assumes the decorated function returns a tuple of (response_text, prompt_tokens, completion_tokens).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # The prompt is usually the first argument or a named kwarg 'prompt'
            prompt = kwargs.get('prompt', args[0] if args else "unknown prompt")
            
            try:
                # Execute the actual LLM call
                result = func(*args, **kwargs)
                response_text = result[0]
                prompt_tokens = result[1]
                completion_tokens = result[2]
            except Exception as e:
                # If the call fails, we could log the failure, but we re-raise
                raise e
            finally:
                latency_ms = (time.time() - start_time) * 1000.0

            # Construct the trace payload
            trace_payload = {
                "project_id": project_id,
                "model": model,
                "prompt_version": prompt_version,
                "prompt": str(prompt),
                "response": str(response_text) if 'response_text' in locals() else "FAILED",
                "latency_ms": latency_ms,
                "prompt_tokens": prompt_tokens if 'prompt_tokens' in locals() else 0,
                "completion_tokens": completion_tokens if 'completion_tokens' in locals() else 0,
                "total_tokens": (prompt_tokens + completion_tokens) if 'prompt_tokens' in locals() else 0,
                "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Fire and forget trace to collector (non-blocking)
            try:
                # Timeout is very short so it doesn't block the AI app
                requests.post(VERDICT_COLLECTOR_URL, json=trace_payload, timeout=0.5)
            except Exception as e:
                # Do not crash the AI app if the collector is down
                print(f"Failed to send trace to Verdict: {e}")

            return result
        return wrapper
    return decorator
