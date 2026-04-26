import json
import os
from dataclasses import dataclass
from pathlib import Path

import httpx
from dotenv import load_dotenv


def load_environment() -> None:
    backend_dir = Path(__file__).resolve().parent.parent
    repo_root = backend_dir.parent

    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(backend_dir / ".env", override=False)


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    model: str
    api_key: str
    base_url: str
    timeout_seconds: float

    @classmethod
    def from_env(cls) -> "LLMSettings":
        load_environment()

        return cls(
            provider=os.getenv("LLM_PROVIDER", "local"),
            model=os.getenv("LLM_MODEL", ""),
            api_key=os.getenv("LLM_API_KEY", ""),
            base_url=os.getenv("LLM_BASE_URL", ""),
            timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "20")),
        )


class LLMClient:
    def __init__(self, settings: LLMSettings | None = None) -> None:
        self._settings = settings

    @property
    def settings(self) -> LLMSettings:
        return self._settings or LLMSettings.from_env()

    def is_enabled(self) -> bool:
        provider = self.settings.provider.lower()

        if provider == "local":
            return False

        return bool(self.settings.api_key and self.settings.model)

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> dict[str, object] | None:
        provider = self.settings.provider.lower()

        if provider in {"openai", "groq"}:
            return await self._generate_openai_compatible_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )

        if provider == "gemini":
            return await self._generate_gemini_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )

        return None

    async def _generate_openai_compatible_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> dict[str, object] | None:
        default_base_urls = {
            "openai": "https://api.openai.com/v1",
            "groq": "https://api.groq.com/openai/v1",
        }
        base_url = self.settings.base_url or default_base_urls[self.settings.provider.lower()]
        url = f"{base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.settings.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        if temperature is not None:
            payload["temperature"] = temperature
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.settings.timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        return json.loads(content)

    async def _generate_gemini_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> dict[str, object] | None:
        base_url = self.settings.base_url or "https://generativelanguage.googleapis.com/v1beta"
        model = self.settings.model
        url = (
            f"{base_url.rstrip('/')}/models/{model}:generateContent"
            f"?key={self.settings.api_key}"
        )
        generation_config: dict[str, object] = {
            "responseMimeType": "application/json"
        }

        if temperature is not None:
            generation_config["temperature"] = temperature

        payload = {
            "generationConfig": generation_config,
            "systemInstruction": {
                "parts": [{"text": system_prompt}],
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}],
                }
            ],
        }

        async with httpx.AsyncClient(timeout=self.settings.timeout_seconds) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        data = response.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]

        return json.loads(content)
