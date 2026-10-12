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

    # Comma-separated list of browser origins allowed to call the API.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins, trimming whitespace and blanks."""
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

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
