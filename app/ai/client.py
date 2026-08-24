"""Groq client construction.

Uses the official ``groq`` Python SDK (``AsyncGroq``) so requests match
https://console.groq.com/docs exactly.  Timeouts and credentials are configured
in one place; tests inject a fake client without touching the network.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from groq import AsyncGroq

from app.ai.groq import model_supports_tool_calling
from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GroqClient:
    """Thin async wrapper around the official Groq chat completions SDK."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: float,
        *,
        log_prompts: bool = False,
    ) -> None:
        """Create the client.

        Args:
            api_key: API key from https://console.groq.com/keys
            base_url: Groq OpenAI-compatible root, e.g. ``https://api.groq.com/openai/v1``.
            timeout: Request timeout in seconds.
            log_prompts: When true, log the full message list sent to Groq.
        """
        self._log_prompts = log_prompts
        self._client = AsyncGroq(api_key=api_key, base_url=base_url, timeout=timeout)

    async def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Send one chat completion request with optional tools.

        Args:
            model: Groq model id, e.g. ``llama-3.3-70b-versatile``.
            messages: OpenAI-style chat history including the system prompt.
            tools: Function definitions offered to the model.

        Returns:
            Parsed completion payload as a plain dict (OpenAI-compatible shape).
        """
        if self._log_prompts:
            logger.info(
                "Groq request model=%s messages=%s tools=%s",
                model,
                messages,
                len(tools),
            )

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
        }
        if tools and model_supports_tool_calling(model):
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        completion = await self._client.chat.completions.create(**kwargs)
        return completion.model_dump()

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.close()


def build_groq_client(settings: Settings | None = None) -> GroqClient:
    """Create a Groq client configured from application settings."""
    settings = settings or get_settings()
    api_key = settings.groq_api_key.get_secret_value()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is required for the Groq assistant.")
    return GroqClient(
        api_key=api_key,
        base_url=settings.groq_base_url,
        timeout=settings.groq_timeout_seconds,
        log_prompts=settings.groq_log_prompts,
    )


@lru_cache(maxsize=1)
def get_groq_client() -> GroqClient:
    """Return the process-wide Groq client, creating it on first use."""
    return build_groq_client()
