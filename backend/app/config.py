from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Document Validator"
    app_env: str = "development"
    log_level: str = "INFO"

    # LLM provider: ollama | anthropic | grok
    llm_provider: str = "ollama"
    llm_api_key: Optional[str] = None
    llm_model: str = "llama2"

    # Ollama-specific — only used when llm_provider=ollama
    ollama_host: str = "http://localhost:11434"

    # Embedding provider: dummy placeholder until Phase 2 real providers are added
    embedding_provider: str = "dummy"
    embedding_api_key: Optional[str] = None
    embedding_model: str = "dummy-embedding"

    max_file_size_mb: int = 10
    max_text_length: int = 50000
    max_rules: int = 100

    cors_origins: list = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
