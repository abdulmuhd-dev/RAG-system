from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All application settings loaded from environment variables.
    Pydantic validates types automatically — if CHUNK_SIZE is
    set to "abc" in .env, the app crashes immediately with a
    clear error instead of silently breaking later.
    """

    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model_name: str = "mistralai/mistral-7b-instruct:free"

    embedding_model: str = "all-MiniLM-L6-v2"

    chroma_persist_dir: str = "./chroma_db"
    collection_name: str = "rag_documents"

    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 4

    langchain_api_key: str | None = None
    langchain_project: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
