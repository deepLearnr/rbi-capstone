import requests

from app.core.config import get_settings


class OllamaProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )

        response.raise_for_status()

        data = response.json()
        answer = data.get("response", "").strip()

        if not answer:
            raise RuntimeError("Ollama returned an empty response")

        return answer
