from functools import lru_cache

import torch
from langchain_huggingface import HuggingFaceEmbeddings

from backend.config import get_settings

def resolve_device() -> str:
    settings = get_settings()

    if settings.embedding_device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"

    if settings.embedding_device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("EMBEDDING_DEVICE is set to cuda, but CUDA is unavailable.")

    return settings.embedding_device


@lru_cache
def get_embeddings() -> HuggingFaceEmbeddings:
    settings = get_settings()

    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={
            "device":resolve_device(),
            "local_files_only":True
        },
        encode_kwargs={"normalize_embeddings":True}
    )

