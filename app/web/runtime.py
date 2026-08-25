"""Long-lived collaborators shared by the web UI's HTTP handlers.

The FastAPI process already runs on a single asyncio loop, so the web UI only
needs a conversation store and a lazily built assistant, kept alive for the
life of the process so the AI chat can remember context between turns.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.ai.agent import AssistantAgent
from app.ai.client import get_groq_client
from app.ai.memory import InMemoryConversationStore
from app.ai.tools.definitions import build_registry
from app.core.config import Settings, get_settings

#: Conversation key for the web dashboard chat.  Isolated from Telegram chats.
WEB_CHAT_ID = 1


@dataclass(slots=True)
class WebRuntime:
    """Assistant collaborators shared by every web request."""

    conversations: InMemoryConversationStore
    settings: Settings
    _agent: AssistantAgent | None = None

    @classmethod
    def create(cls, settings: Settings | None = None) -> WebRuntime:
        """Build the runtime from application settings.

        Args:
            settings: Configuration to use.  Defaults to the process singleton.
        """
        settings = settings or get_settings()
        return cls(
            conversations=InMemoryConversationStore(settings.conversation_ttl_seconds),
            settings=settings,
        )

    @property
    def agent(self) -> AssistantAgent:
        """The language-model agent, created on the first chat turn."""
        if self._agent is None:
            self._agent = AssistantAgent(get_groq_client(), build_registry(), self.settings)
        return self._agent


_runtime: WebRuntime | None = None


def get_web_runtime() -> WebRuntime:
    """Return the process-wide web runtime, creating it on first use."""
    global _runtime
    if _runtime is None:
        _runtime = WebRuntime.create()
    return _runtime
