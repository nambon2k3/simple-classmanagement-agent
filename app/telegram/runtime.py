"""Shared objects and per-update scoping for the Telegram bot.

Handlers must stay free of business logic, but they still need three things:
the long-lived collaborators (agent, conversation store, database), a database
session scoped to the current update, and the teacher behind it.  This module
provides exactly that and nothing more.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from telegram.ext import Application, ContextTypes

from app.ai.agent import AssistantAgent
from app.ai.client import get_groq_client
from app.ai.memory import InMemoryConversationStore
from app.ai.tools.definitions import build_registry
from app.core.config import Settings, get_settings
from app.database.session import Database, get_database
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherIdentity
from app.services.container import ServiceContainer
from telegram import User as TelegramUser

#: Key under which the runtime is stored in ``Application.bot_data``.
RUNTIME_KEY = "runtime"


@dataclass(slots=True)
class BotRuntime:
    """Long-lived collaborators shared by every handler."""

    database: Database
    agent: AssistantAgent
    conversations: InMemoryConversationStore
    settings: Settings

    @classmethod
    def create(cls, settings: Settings | None = None) -> BotRuntime:
        """Build the runtime from application settings.

        Args:
            settings: Configuration to use.  Defaults to the process singleton.
        """
        settings = settings or get_settings()
        return cls(
            database=get_database(),
            agent=AssistantAgent(get_groq_client(), build_registry(), settings),
            conversations=InMemoryConversationStore(settings.conversation_ttl_seconds),
            settings=settings,
        )

    @asynccontextmanager
    async def scope(self, user: TelegramUser) -> AsyncIterator[tuple[ServiceContainer, Teacher]]:
        """Open a unit of work and resolve the teacher behind an update.

        Everything a handler does inside the block shares one transaction, so
        an update either applies completely or not at all.

        Args:
            user: The Telegram user who sent the update.

        Yields:
            The service container and the resolved teacher.

        Raises:
            PermissionDeniedError: If the user is not allowed to use the bot.
        """
        async with self.database.session() as session:
            services = ServiceContainer(session=session, settings=self.settings)
            teacher = await services.teachers.get_or_create(identity_from(user))
            yield services, teacher


def identity_from(user: TelegramUser) -> TeacherIdentity:
    """Project a Telegram user onto the identity the service layer expects."""
    return TeacherIdentity(
        telegram_id=user.id,
        full_name=user.full_name or user.username or f"User {user.id}",
        username=user.username,
        language_code=user.language_code,
    )


def get_runtime(context: ContextTypes.DEFAULT_TYPE) -> BotRuntime:
    """Fetch the runtime from a handler's context.

    Raises:
        RuntimeError: If the application was not initialised with a runtime,
            which would be a wiring bug rather than a user error.
    """
    runtime = context.application.bot_data.get(RUNTIME_KEY)
    if not isinstance(runtime, BotRuntime):
        raise RuntimeError("Bot runtime is missing; the application was not initialised.")
    return runtime


def install_runtime(application: Application, runtime: BotRuntime) -> None:
    """Attach a runtime to an application so handlers can reach it."""
    application.bot_data[RUNTIME_KEY] = runtime
