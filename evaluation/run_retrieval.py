import json
from pathlib import Path
import time

from backend.retriever import retriever
from evaluation.metrics import retrieval_metrics

DATASET_PATH = Path("evaluation/datasets/unit_ii.jsonl")

def load_dataset():
    with DATASET_PATH.open("r",encoding="utf-8") as dataset_file:
        return [
            json.loads(line)
            for line in dataset_file
            if line.strip()
        ]

def source_summary(document):
      source = str(document.metadata.get("source", "unknown"))
      filename = source.replace("\\", "/").split("/")[-1]
      page = document.metadata.get("page", 0) + 1

      return f"{filename} - page {page}"

def main():
      records = load_dataset()
      results = []

    
      for record in records:
          retrieval_start = time.perf_counter()

          documents = retriever(record["question"])

          retrieval_latency_ms = (
               time.perf_counter() - retrieval_start
               ) * 1000

          metrics = retrieval_metrics(
              record,
              documents,
              k=3,
          )

          result = {
              "id": record["id"],
              "question": record["question"],
              "retrieval_latency_ms": round(retrieval_latency_ms,2),
              "retrieved_sources": [
                  source_summary(document)
                  for document in documents[:3]
              ],
              **metrics,
          }

          results.append(result)

          print(
      f"{record['id']} | "
      f"Hit@3={metrics['hit_at_k']} | "
      f"MRR={metrics['reciprocal_rank']} | "
      f"Latency={retrieval_latency_ms:.2f} ms | "
      f"Retrieved={result['retrieved_sources']}"
  )

      answerable_results = [
          result
          for result in results
          if result["hit_at_k"] is not None
      ]

      hit_rate = sum(
          result["hit_at_k"]
          for result in answerable_results
      ) / len(answerable_results)

      mean_reciprocal_rank = sum(
          result["reciprocal_rank"]
          for result in answerable_results
      ) / len(answerable_results)

      print("\nSummary")
      print(f"Answerable questions: {len(answerable_results)}")
      print(f"Hit@3: {hit_rate:.3f}")
      print(f"MRR: {mean_reciprocal_rank:.3f}")


if __name__ == "__main__":
      main()
