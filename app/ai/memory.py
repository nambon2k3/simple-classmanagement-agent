"""Short-lived conversation state.

The assistant needs just enough memory to make follow-up messages work: the
recent turns, and which class or attendance session the teacher is focused on.
That is what lets "John absent" mean "mark John absent in SE401's session for
today".

State is intentionally *ephemeral*.  Nothing here is a source of truth — the
open attendance session lives in the database, and losing this cache only costs
the teacher a little extra typing.  The :class:`ConversationStore` protocol
exists so the in-memory implementation can be swapped for Redis when the bot
runs as more than one process.
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Protocol, runtime_checkable

from app.core.config import get_settings
from app.core.logging import get_logger
from app.utils.datetime_utils import utc_now

logger = get_logger(__name__)


@dataclass(slots=True)
class ConversationState:
    """Everything remembered between two messages in one chat."""

    #: Chat identifier the conversation belongs to.
    chat_id: int
    #: Teacher who owns the conversation.
    teacher_id: int
    #: Conversation items (user messages, tool calls, tool outputs).
    history: list[dict[str, Any]] = field(default_factory=list)
    #: Class the teacher is currently working with, if any.
    focus_class_id: int | None = None
    #: Attendance session currently being filled in, if any.
    focus_session_id: int | None = None
    #: Last time the conversation was touched; drives expiry.
    updated_at: datetime = field(default_factory=utc_now)

    def touch(self) -> None:
        """Mark the conversation as active right now."""
        self.updated_at = utc_now()

    def is_expired(self, ttl: timedelta) -> bool:
        """Whether the conversation has been idle for longer than ``ttl``."""
        return utc_now() - self.updated_at > ttl

    def extend_history(self, items: Iterable[dict[str, Any]], *, limit: int) -> None:
        """Append items and trim the history to the most recent ``limit``.

        Trimming keeps the request payload — and therefore latency and cost —
        bounded during a long attendance session.
        """
        self.history.extend(items)
        if len(self.history) > limit:
            del self.history[: len(self.history) - limit]

    def clear_attendance_focus(self) -> None:
        """Forget the attendance session, e.g. after it has been finalised."""
        self.focus_session_id = None


@runtime_checkable
class ConversationStore(Protocol):
    """Storage for :class:`ConversationState`, keyed by chat id."""

    async def get(self, chat_id: int) -> ConversationState | None:
        """Return the live state for a chat, or ``None`` if absent or expired."""
        ...

    async def save(self, state: ConversationState) -> None:
        """Persist a conversation, refreshing its expiry."""
        ...

    async def clear(self, chat_id: int) -> None:
        """Forget a conversation entirely."""
        ...


class InMemoryConversationStore:
    """Process-local conversation store with time-based expiry.

    Suitable for a single-process deployment, which is what a polling bot is.
    Horizontal scaling requires a shared implementation of
    :class:`ConversationStore`; nothing outside this module needs to change.
    """

    def __init__(self, ttl_seconds: int | None = None) -> None:
        """Create the store.

        Args:
            ttl_seconds: Idle lifetime of a conversation.  Defaults to the
                configured ``CONVERSATION_TTL_SECONDS``.
        """
        settings = get_settings()
        self._ttl = timedelta(seconds=ttl_seconds or settings.conversation_ttl_seconds)
        self._states: dict[int, ConversationState] = {}
        self._lock = asyncio.Lock()

    @property
    def ttl(self) -> timedelta:
        """How long a conversation survives without activity."""
        return self._ttl

    async def get(self, chat_id: int) -> ConversationState | None:
        """Return the live state for a chat, dropping it if it has expired."""
        async with self._lock:
            state = self._states.get(chat_id)
            if state is None:
                return None
            if state.is_expired(self._ttl):
                del self._states[chat_id]
                logger.info("Conversation expired", extra={"chat_id": chat_id})
                return None
            return state

    async def save(self, state: ConversationState) -> None:
        """Persist a conversation and refresh its expiry."""
        async with self._lock:
            state.touch()
            self._states[state.chat_id] = state

    async def clear(self, chat_id: int) -> None:
        """Forget a conversation entirely."""
        async with self._lock:
            self._states.pop(chat_id, None)

    async def purge_expired(self) -> int:
        """Drop every expired conversation.

        Returns:
            How many conversations were removed.  Without this, a bot that
            serves many one-off chats would grow its memory forever.
        """
        async with self._lock:
            stale = [
                chat_id for chat_id, state in self._states.items() if state.is_expired(self._ttl)
            ]
            for chat_id in stale:
                del self._states[chat_id]
        if stale:
            logger.info("Purged expired conversations", extra={"count": len(stale)})
        return len(stale)

    async def get_or_create(self, chat_id: int, teacher_id: int) -> ConversationState:
        """Return the live conversation for a chat, creating one if needed."""
        state = await self.get(chat_id)
        if state is None or state.teacher_id != teacher_id:
            state = ConversationState(chat_id=chat_id, teacher_id=teacher_id)
            await self.save(state)
        return state
