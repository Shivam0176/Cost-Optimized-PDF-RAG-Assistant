from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str = Field(min_length=1)

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "auto"

    llm_model: str = "openai/gpt-oss-20b"
    max_output_tokens: int = Field(default=400,ge=1,le=2000)

    max_upload_bytes: int = Field(default=200 * 1024 * 1024, ge=1)
    chunk_size: int = Field(default=600,ge=100)
    chunk_overlap: int = Field(default=100,ge=0)
    retrieval_k:int = Field(default=3,ge=1,le=10)

    upload_dir: Path = Path("uploads")
    vectorstore_dir: Path = Path("vectorstore/chroma_local_db")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

