import csv
import json
from pathlib import Path

RESULTS_PATH = Path("evaluation/results/rag_results.jsonl")
REVIEW_PATH = Path("evaluation/results/groundedness_review.csv")

def main():
      REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)

      with RESULTS_PATH.open("r", encoding="utf-8") as results_file:
          results = [
              json.loads(line)
              for line in results_file
              if line.strip()
          ]

      with REVIEW_PATH.open(
          "w",
          encoding="utf-8",
          newline="",
      ) as review_file:
          writer = csv.DictWriter(
              review_file,
              fieldnames=[
                  "id",
                  "question",
                  "answer",
                  "context",
                  "retrieved_sources",
                  "groundedness_score",
                  "review_notes",
              ],
          )

          writer.writeheader()

          for result in results:
              writer.writerow({
                  "id": result["id"],
                  "question": result["question"],
                  "answer": result["answer"],
                  "context": result["context"],
                  "retrieved_sources": json.dumps(
                      result["retrieved_sources"],
                      ensure_ascii=False,
                  ),
                  "groundedness_score": "",
                  "review_notes": "",
              })

      print(f"Created {REVIEW_PATH}")


if __name__ == "__main__":
      main()