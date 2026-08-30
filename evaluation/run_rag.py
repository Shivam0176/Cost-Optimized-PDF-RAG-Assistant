import json
import time
from pathlib import Path
from backend.llm import chatbot_with_usage
from backend.retriver import retriever
from evaluation.metrics import estimate_groq_cost

DATASET_PATH = Path("evaluation/datasets/unit_ii.jsonl")
RESULTS_PATH = Path("evaluation/results/rag_results.jsonl")

def load_dataset():
      with DATASET_PATH.open("r", encoding="utf-8") as dataset_file:
          return [
              json.loads(line)
              for line in dataset_file
              if line.strip()
          ]


def main():
      records = load_dataset()
      results = []

      for record in records:
          retrieval_start = time.perf_counter()
          documents = retriever(record["question"])
          retrieval_latency_ms = (
              time.perf_counter() - retrieval_start
          ) * 1000

          context = "\n\n".join(
              document.page_content
              for document in documents
          )

          generation_start = time.perf_counter()
          answer, usage = chatbot_with_usage(
              record["question"],
              context,
          )
          generation_latency_ms = (
              time.perf_counter() - generation_start
          ) * 1000

          input_tokens = usage.get("input_tokens", 0)
          output_tokens = usage.get("output_tokens", 0)

          cost = estimate_groq_cost(
              input_tokens,
              output_tokens,
          )

          result = {
              "id": record["id"],
              "question": record["question"],
              "answer": answer,
              "context": context,
                "retrieved_sources": [
                    {
                        "filename": str(
                            document.metadata.get("source", "unknown")
                        ),
                        "page": document.metadata.get("page", 0) + 1,
                    }
                    for document in documents
                ],
              "input_tokens": input_tokens,
              "output_tokens": output_tokens,
              "total_tokens": usage.get("total_tokens", 0),
              "estimated_cost_usd": cost,
              "retrieval_latency_ms": retrieval_latency_ms,
              "generation_latency_ms": generation_latency_ms,
              "total_latency_ms": (
                  retrieval_latency_ms
                  + generation_latency_ms
              ),
          }

          results.append(result)


          print(
              f"{record['id']} | "
              f"tokens={result['total_tokens']} | "
              f"cost=${cost:.6f} | "
              f"retrieval={retrieval_latency_ms:.2f} ms | "
              f"generation={generation_latency_ms:.2f} ms"
          )

      RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

      with RESULTS_PATH.open("w", encoding="utf-8") as results_file:
            for result in results:
                results_file.write(
                    json.dumps(result, ensure_ascii=False)
                    + "\n"
                )

      print(f"\nSaved results to {RESULTS_PATH}")  
      print("\nSummary")

      print(
          "Average cost: $"
          f"{sum(r['estimated_cost_usd'] for r in results) / len(results):.6f}"
      )

      print(
          "Average retrieval latency: "
          f"{sum(r['retrieval_latency_ms'] for r in results) / len(results):.2f} ms"
      )

      print(
          "Average generation latency: "
          f"{sum(r['generation_latency_ms'] for r in results) / len(results):.2f} ms"
      )


if __name__ == "__main__":
      main()