from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Document Validator"
    app_env: str = "development"
    log_level: str = "INFO"

    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"

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
