import time
from typing import List, Dict
from eval.judge import evaluate_trace

class RegressionTestSuite:
    def __init__(self, benchmark_cases: List[Dict[str, str]]):
        """
        benchmark_cases: list of dicts with 'question' and 'expected_answer'
        """
        self.benchmark_cases = benchmark_cases

    def run_suite(self, ai_function, prompt_version: str):
        """
        Runs the benchmark suite against a given AI function and evaluates the results.
        Returns the delta report.
        """
        results = []
        total_latency = 0
        total_cost = 0.0 # Stub

        for case in self.benchmark_cases:
            start = time.time()
            # Call the AI function
            # AI function is expected to be decorated with track_llm or return text
            response, p_tokens, c_tokens = ai_function(case["question"])
            latency = (time.time() - start) * 1000.0
            
            # Evaluate using LLM judge
            scores = evaluate_trace(case["question"], response)
            
            results.append({
                "question": case["question"],
                "response": response,
                "latency_ms": latency,
                "scores": scores
            })
            total_latency += latency

        # Summarize
        avg_latency = total_latency / len(self.benchmark_cases)
        avg_faithfulness = sum(r["scores"]["faithfulness_score"] or 0 for r in results) / len(results)
        
        return {
            "prompt_version": prompt_version,
            "test_cases_run": len(results),
            "avg_latency_ms": avg_latency,
            "avg_faithfulness": avg_faithfulness,
            "details": results
        }
