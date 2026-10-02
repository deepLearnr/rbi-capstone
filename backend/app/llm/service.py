from app.core.config import get_settings
from app.llm.base import LLMProvider
from app.llm.ollama import OllamaProvider
from app.llm.openrouter import OpenRouterProvider


def get_llm_provider() -> LLMProvider:
    settings = get_settings()

    if settings.llm_provider == "ollama":
        return OllamaProvider()

    if settings.llm_provider == "openrouter":
        return OpenRouterProvider()

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )
