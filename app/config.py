# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # ── REQUIRED — no default, no Optional
    # app crashes at startup if missing or empty
    openrouter_api_key: str

    # ── HAS DEFAULT — .env overrides it, falls back if absent
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model_name: str = "openrouter/free"
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_persist_dir: str = "./chroma_db"
    collection_name: str = "rag_documents"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 4

    # ── OPTIONAL — genuinely not needed, None by default
    # we'll use this later for LangSmith tracing (observability)
    langchain_api_key: str | None = None
    langchain_project: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
