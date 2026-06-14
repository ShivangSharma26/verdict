import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
import sys
from pathlib import Path

# Add the project root to the python path so we can import the SDK
sys.path.append(str(Path(__file__).parent))
from sdk.tracker import track_llm

try:
    client = Groq()
except Exception:
    print("WARNING: GROQ_API_KEY environment variable not set.")
    client = None

MODEL_NAME = "llama-3.1-8b-instant"

@track_llm(model=MODEL_NAME, prompt_version="v1", project_id=1)
def answer_question(prompt: str) -> tuple[str, int, int]:
    """
    Mock AI App function that calls Groq and returns the response and token usage.
    """
    if not client:
        return "GROQ API KEY IS MISSING", 0, 0
        
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        
        response_text = completion.choices[0].message.content
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        
        return response_text, prompt_tokens, completion_tokens
    except Exception as e:
        print(f"Error calling Groq: {e}")
        return str(e), 0, 0

if __name__ == "__main__":
    print("Running Mock AI App...")
    questions = [
        "What is the capital of France?",
        "Explain the theory of relativity in one sentence.",
        "Why is the sky blue?"
    ]
    
    for q in questions:
        print(f"\nQuestion: {q}")
        response, p_tokens, c_tokens = answer_question(prompt=q)
        print(f"Answer: {response}")
        print(f"Usage: {p_tokens} prompt tokens, {c_tokens} completion tokens")
        print("-" * 50)

# Ensure Docker infrastructure is running before executing this.
