"""Ollama client construction.

Isolated from the agent so that timeouts and the base URL are configured in
exactly one place, and so tests can inject a fake client without touching the
network.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import httpx

from app.core.config import Settings, get_settings


class OllamaClient:
    """Thin async wrapper around Ollama's ``/api/chat`` endpoint."""

    def __init__(self, base_url: str, timeout: float) -> None:
        """Create the client.

        Args:
            base_url: Ollama server root, e.g. ``http://127.0.0.1:11434``.
            timeout: Request timeout in seconds.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._http: httpx.AsyncClient | None = None

    def _client(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        return self._http

    async def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Send one non-streaming chat request with optional tools.

        Args:
            model: Ollama model tag, e.g. ``llama3.2:3b``.
            messages: OpenAI-style chat history including the system prompt.
            tools: Function definitions offered to the model.

        Returns:
            Parsed JSON response from Ollama.
        """
        response = await self._client().post(
            "/api/chat",
            json={
                "model": model,
                "messages": messages,
                "tools": tools,
                "stream": False,
            },
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise httpx.HTTPError("Ollama returned a non-object JSON payload.")
        return payload

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        if self._http is not None:
            await self._http.aclose()
            self._http = None


def build_ollama_client(settings: Settings | None = None) -> OllamaClient:
    """Create an Ollama client configured from application settings."""
    settings = settings or get_settings()
    return OllamaClient(
        base_url=settings.ollama_host,
        timeout=settings.ollama_timeout_seconds,
    )


@lru_cache(maxsize=1)
def get_ollama_client() -> OllamaClient:
    """Return the process-wide Ollama client, creating it on first use."""
    return build_ollama_client()
