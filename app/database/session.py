"""Async database engine and session management.

The :class:`Database` object owns the engine and session factory.  Everything
else in the application receives an :class:`~sqlalchemy.ext.asyncio.AsyncSession`
by dependency injection, which keeps the data layer swappable and lets tests
bind an in-memory SQLite database without patching globals.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Database:
    """Owns the async engine and hands out sessions."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Create the engine and session factory.

        Args:
            settings: Configuration supplying the DSN and pool sizing.
                Defaults to the process settings singleton.
        """
        self._settings = settings or get_settings()
        self._engine: AsyncEngine = create_async_engine(
            self._settings.database_url,
            echo=self._settings.db_echo,
            future=True,
            **self._pool_options(),
        )
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    def _pool_options(self) -> dict[str, Any]:
        """Pool tuning that only applies to real server-backed databases.

        SQLite (used by the test suite) rejects ``pool_size``/``max_overflow``
        because it uses a different pool implementation.
        """
        if self._settings.database_url.startswith("sqlite"):
            return {}
        return {
            "pool_size": self._settings.db_pool_size,
            "max_overflow": self._settings.db_max_overflow,
            "pool_pre_ping": self._settings.db_pool_pre_ping,
        }

    @property
    def engine(self) -> AsyncEngine:
        """The underlying async engine."""
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Factory used to create new sessions."""
        return self._session_factory

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Yield a session inside a transaction (unit of work).

        The transaction is committed when the block exits normally and rolled
        back if it raises, so callers never have to remember either.
        """
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()

    async def dispose(self) -> None:
        """Close all pooled connections.  Called on application shutdown."""
        await self._engine.dispose()
        logger.info("Database connection pool disposed")


_database: Database | None = None


def get_database() -> Database:
    """Return the process-wide :class:`Database`, creating it on first use."""
    global _database
    if _database is None:
        _database = Database()
    return _database


def set_database(database: Database | None) -> None:
    """Override the process-wide database.  Intended for tests only."""
    global _database
    _database = database


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a transactional session."""
    async with get_database().session() as session:
        yield session
