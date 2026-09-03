from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

import requests


class OllamaErrorCode(str, Enum):
    TIMEOUT = "TIMEOUT"
    CONNECTION = "CONNECTION"
    HTTP_ERROR = "HTTP_ERROR"
    MALFORMED_JSON = "MALFORMED_JSON"
    INVALID_RESPONSE = "INVALID_RESPONSE"


class OllamaClientError(RuntimeError):
    """A classified Ollama transport or response failure."""

    def __init__(self, code: OllamaErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    model: str = "qwen3:4b"
    timeout_seconds: float = 60.0
    temperature: float = 0.1
    malformed_json_retries: int = 1
    keep_alive: int = -1

    def __post_init__(self) -> None:
        normalized_url = self.base_url.strip().rstrip("/")
        normalized_model = self.model.strip()
        if not normalized_url:
            raise ValueError("OLLAMA_BASE_URL must not be empty")
        if not normalized_model:
            raise ValueError("OLLAMA_MODEL must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("AI_TIMEOUT_SECONDS must be greater than zero")
        if self.malformed_json_retries < 0:
            raise ValueError("malformed_json_retries must not be negative")
        object.__setattr__(self, "base_url", normalized_url)
        object.__setattr__(self, "model", normalized_model)

    @classmethod
    def from_env(cls) -> "OllamaConfig":
        timeout_value = os.getenv("AI_TIMEOUT_SECONDS", "60")
        try:
            timeout_seconds = float(timeout_value)
        except ValueError as exc:
            raise ValueError("AI_TIMEOUT_SECONDS must be a number") from exc

        keep_alive_env = os.getenv("OLLAMA_KEEP_ALIVE", "-1")
        try:
            keep_alive = int(keep_alive_env)
        except ValueError:
            keep_alive = -1

        return cls(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "qwen3:4b"),
            timeout_seconds=timeout_seconds,
            keep_alive=keep_alive,
        )

    @property
    def generate_url(self) -> str:
        return f"{self.base_url}/api/generate"


class OllamaClient:
    """Minimal Ollama JSON-mode client without orchestration or fallback logic."""

    def __init__(
        self,
        config: Optional[OllamaConfig] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.config = config or OllamaConfig.from_env()
        self._session = session or requests.Session()

    def warmup(self) -> bool:
        """Preload the model into memory with keep_alive to eliminate cold-start latency."""
        try:
            res = self._session.post(
                self.config.generate_url,
                json={"model": self.config.model, "keep_alive": self.config.keep_alive},
                timeout=15.0,
            )
            return res.status_code == 200
        except Exception:
            return False

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        payload = {
            "model": self.config.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "format": "json",
            "keep_alive": self.config.keep_alive,
            "options": {"temperature": self.config.temperature},
        }
        deadline = time.monotonic() + self.config.timeout_seconds
        attempts = self.config.malformed_json_retries + 1

        for attempt in range(attempts):
            remaining_seconds = deadline - time.monotonic()
            if remaining_seconds <= 0:
                raise OllamaClientError(
                    OllamaErrorCode.TIMEOUT,
                    "Ollama request exceeded the configured total timeout",
                )

            try:
                response = self._session.post(
                    self.config.generate_url,
                    json=payload,
                    timeout=remaining_seconds,
                )
                response.raise_for_status()
            except (requests.ConnectTimeout, requests.ConnectionError) as exc:
                raise OllamaClientError(
                    OllamaErrorCode.CONNECTION,
                    "Could not connect to Ollama",
                ) from exc
            except requests.Timeout as exc:
                raise OllamaClientError(
                    OllamaErrorCode.TIMEOUT,
                    "Ollama request timed out",
                ) from exc
            except requests.RequestException as exc:
                raise OllamaClientError(
                    OllamaErrorCode.HTTP_ERROR,
                    "Ollama returned an HTTP error",
                ) from exc

            try:
                return self._decode_json_object(response)
            except OllamaClientError as exc:
                should_retry = (
                    exc.code == OllamaErrorCode.MALFORMED_JSON
                    and attempt < attempts - 1
                )
                if not should_retry:
                    raise

        raise AssertionError("Ollama retry loop exited unexpectedly")

    @staticmethod
    def _decode_json_object(response: requests.Response) -> Dict[str, Any]:
        try:
            envelope = response.json()
        except ValueError as exc:
            raise OllamaClientError(
                OllamaErrorCode.MALFORMED_JSON,
                "Ollama returned malformed response JSON",
            ) from exc

        if not isinstance(envelope, dict):
            raise OllamaClientError(
                OllamaErrorCode.MALFORMED_JSON,
                "Ollama response envelope must be a JSON object",
            )

        generated_text = envelope.get("response")
        if not isinstance(generated_text, str) or not generated_text.strip():
            raise OllamaClientError(
                OllamaErrorCode.INVALID_RESPONSE,
                "Ollama response is missing generated JSON text",
            )

        try:
            generated_value = json.loads(generated_text)
        except json.JSONDecodeError as exc:
            raise OllamaClientError(
                OllamaErrorCode.MALFORMED_JSON,
                "Ollama generated malformed JSON",
            ) from exc

        if not isinstance(generated_value, dict):
            raise OllamaClientError(
                OllamaErrorCode.MALFORMED_JSON,
                "Ollama generated JSON must be an object",
            )
        return generated_value