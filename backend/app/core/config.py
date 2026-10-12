from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    llm_provider: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"

    openrouter_api_key: str | None = None
    openrouter_model: str | None = None

    retrieval_top_k: int = 3

    # Optional SMTP configuration. Digest delivery is disabled until explicitly
    # invoked with --send and a recipient is configured.
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    daily_digest_to: str | None = None
    smtp_use_ssl: bool = False
    smtp_starttls: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
