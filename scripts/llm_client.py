from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResult:
    enabled: bool
    provider: str
    model: str | None
    text: str | None = None
    error: str | None = None


class LLMClient:
    def __init__(self, config: dict[str, Any]) -> None:
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass
        self.config = config or {}
        self.provider = self.config.get("provider", "none")
        self.enabled = self.provider in {"openai_compatible", "ollama"}
        self.endpoint = (self.config.get("baseUrl") or self.config.get("endpoint") or "").rstrip("/")
        self.model = self.config.get("model")
        self.api_key_env = self.config.get("apiKeyEnv", "OPENAI_API_KEY")
        self.temperature = float(self.config.get("temperature", 0.2))
        self.calls_attempted = 0
        self.calls_succeeded = 0
        self.calls_failed = 0
        self.last_error: str | None = None

    def available(self) -> bool:
        if not self.enabled:
            return False
        if self.provider == "ollama":
            return bool(self.endpoint and self.model)
        return bool(self.endpoint and self.model and os.getenv(self.api_key_env))

    def diagnostics(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "endpointConfigured": bool(self.endpoint),
            "modelConfigured": bool(self.model),
            "apiKeyEnv": self.api_key_env,
            "apiKeyPresent": bool(os.getenv(self.api_key_env)) if self.provider == "openai_compatible" else None,
            "enabled": self.enabled,
            "available": self.available(),
        }

    def test_connection(self) -> tuple[bool, str]:
        if not self.enabled:
            return False, "LLM is disabled."
        if not self.endpoint or not self.model:
            return False, "Endpoint and model are required."
        if self.provider == "openai_compatible" and not os.getenv(self.api_key_env):
            return False, f"Environment variable {self.api_key_env} is not set in .env or system env."
        try:
            text = self.summarize("Reply with exactly: ok")
            if text.strip():
                return True, "LLM connection succeeded."
            return False, "LLM returned an empty response."
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    def summarize(self, prompt: str, system_prompt: str | None = None) -> str:
        if not self.available():
            raise RuntimeError("LLM disabled or missing configuration/API key.")
        self.calls_attempted += 1
        try:
            import requests
        except ImportError as exc:
            self.calls_failed += 1
            self.last_error = "requests is required when LLM provider is enabled. Install requirements.txt."
            raise RuntimeError("requests is required when LLM provider is enabled. Install requirements.txt.") from exc

        try:
            if self.provider == "ollama":
                ollama_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = requests.post(
                    f"{self.endpoint}/api/generate",
                    json={"model": self.model, "prompt": ollama_prompt, "stream": False},
                    timeout=120,
                )
                response.raise_for_status()
                text = response.json().get("response", "")
                self.calls_succeeded += 1
                return text
            headers = {
                "Authorization": f"Bearer {os.getenv(self.api_key_env)}",
                "Content-Type": "application/json",
            }
            response = requests.post(
                f"{self.endpoint}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt or "You are a source-grounded lecture note generator."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": self.temperature,
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            self.calls_succeeded += 1
            return text
        except Exception as exc:  # noqa: BLE001 - keep fallback local-first
            self.calls_failed += 1
            self.last_error = str(exc)
            raise RuntimeError(str(exc)) from exc
