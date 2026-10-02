import time

import requests

from app.core.config import get_settings


class OpenRouterProvider:
    def __init__(self) -> None:
        settings = get_settings()

        if not settings.openrouter_api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured"
            )

        if not settings.openrouter_model:
            raise RuntimeError(
                "OPENROUTER_MODEL is not configured"
            )

        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model

    def generate(self, prompt: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=90,
            )

            if response.status_code not in {429, 500, 502, 503, 504}:
                response.raise_for_status()
                break

            if attempt == max_attempts:
                response.raise_for_status()

            delay = 2 ** attempt
            time.sleep(delay)

        data = response.json()

        try:
            answer = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError) as exc:
            raise RuntimeError(
                "OpenRouter returned an unexpected response"
            ) from exc

        if not answer:
            raise RuntimeError("OpenRouter returned an empty response")

        return answer