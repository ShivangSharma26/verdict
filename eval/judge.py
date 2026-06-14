import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
from typing import Dict, Any

# Ensure GROQ_API_KEY is set in your environment variables
# export GROQ_API_KEY="your-groq-api-key"
try:
    client = Groq()
except Exception:
    client = None

def evaluate_trace(prompt: str, response: str) -> Dict[str, Any]:
    """
    Uses an LLM as a judge to evaluate a trace.
    Returns faithfulness, relevance, and hallucination scores.
    """
    if not client:
        return {
            "faithfulness_score": None,
            "relevance_score": None,
            "hallucination_score": None
        }

    evaluation_prompt = f"""
    You are an expert AI judge evaluating the quality of an AI's response.
    Given the following Prompt and Response, evaluate the quality on a scale of 0.0 to 1.0 for three metrics:
    1. Relevance: Does the response directly answer the prompt? (1.0 = highly relevant, 0.0 = completely off-topic)
    2. Faithfulness: Is the response logical and consistent? (1.0 = highly logical, 0.0 = nonsensical)
    3. Hallucination: Does the response contain made-up or factually incorrect information? (1.0 = hallucinated, 0.0 = factually sound/no hallucinations) Note: higher hallucination score means WORSE.

    Prompt: {prompt}
    Response: {response}

    Return ONLY a valid JSON object in the exact format below, with no markdown formatting or extra text:
    {{
        "relevance_score": 0.9,
        "faithfulness_score": 0.8,
        "hallucination_score": 0.1
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a strict, objective AI evaluation judge. Always return JSON."},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        import json
        result_text = completion.choices[0].message.content
        scores = json.loads(result_text)
        
        return {
            "relevance_score": float(scores.get("relevance_score", 0.0)),
            "faithfulness_score": float(scores.get("faithfulness_score", 0.0)),
            "hallucination_score": float(scores.get("hallucination_score", 0.0))
        }
    except Exception as e:
        print(f"Evaluation failed: {e}")
        return {
            "faithfulness_score": None,
            "relevance_score": None,
            "hallucination_score": None
        }

# LLM-as-a-judge using Groq LLaMA-3.
