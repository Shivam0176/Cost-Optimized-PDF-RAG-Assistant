def normalize_filename(filename: str) -> str:
    return filename.replace("\\","/").split("/")[-1].lower()

def document_key(document) -> tuple[str, int]:
    filename = normalize_filename(
        document.metadata.get("source","")
    )

    page = document.metadata.get("page",0) + 1

    return filename, page

def gold_source_keys(record: dict) -> set[tuple[str, int]]:
    keys = set()

    for source in record["gold_sources"]:
        filename = normalize_filename(source["filename"])

        for page in source["pages"]:
            keys.add((filename, page))

    return keys

def retrieval_metrics(
    record: dict,
    documents: list,
    k: int = 3
) -> dict:
    if not record["answerable"]:
        return {
            "hit_at_k": None,
            "reciprocal_rank": None
        }

    gold_keys = gold_source_keys(record)
    retrieved_keys = [
        document_key(document)
        for document in documents[:k]
    ]

    first_match_rank = None

    for rank, key in enumerate(retrieved_keys, start=1):
        if key in gold_keys:
            first_match_rank = rank
            break

    return {
        "hit_at_k": first_match_rank is not None,
        "reciprocal_rank": (
            1 / first_match_rank
            if first_match_rank is not None
            else 0.0
        )
    }


def estimate_groq_cost(
      input_tokens: int,
      output_tokens: int,
      input_price_per_million: float = 0.075,
      output_price_per_million: float = 0.30,
  ) -> float:
      input_cost = (
          input_tokens / 1_000_000
      ) * input_price_per_million

      output_cost = (
          output_tokens / 1_000_000
      ) * output_price_per_million

      return input_cost + output_cost