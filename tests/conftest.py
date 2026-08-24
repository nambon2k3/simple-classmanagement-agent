"""Shared pytest fixtures.

Integration tests run against a real (SQLite) database rather than mocks, so
the SQL the repositories build is genuinely exercised.  Only the Groq client
is faked, because that is the one dependency a test must never reach.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

TEST_ENVIRONMENT = {
    "ENVIRONMENT": "local",
    "TIMEZONE": "UTC",
    "TELEGRAM_BOT_TOKEN": "test-telegram-token",
    "GROQ_API_KEY": "test-groq-key",
    "GROQ_MODEL": "llama-3.3-70b-versatile",
    "TELEGRAM_ALLOWED_USER_IDS": "[]",
    "LOG_LEVEL": "WARNING",
}


@pytest.fixture(scope="session", autouse=True)
def _configure_environment() -> Iterator[None]:
    """Pin configuration for the whole test session.

    Environment variables win over any developer ``.env`` file, so a test run
    can never accidentally talk to a real database or a real bot.
    """
    from app.core.config import get_settings

    previous = {key: os.environ.get(key) for key in TEST_ENVIRONMENT}
    os.environ.update(TEST_ENVIRONMENT)
    get_settings.cache_clear()
    yield
    for key, value in previous.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    get_settings.cache_clear()


@pytest.fixture
async def database(tmp_path, _configure_environment) -> AsyncIterator[object]:
    """A throwaway SQLite database with the full schema applied.

    A file-backed database (rather than ``:memory:``) is used so that every
    pooled connection sees the same data, matching how PostgreSQL behaves.
    """
    from app.core.config import Settings, get_settings
    from app.database.session import Database, set_database
    from app.models import Base

    get_settings.cache_clear()
    settings = Settings(database_url=f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    db = Database(settings)

    # SQLite ignores foreign keys unless asked, which would let ON DELETE
    # CASCADE silently do nothing and hide real bugs.
    @event.listens_for(db.engine.sync_engine, "connect")
    def _enable_foreign_keys(connection, _record) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with db.engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    set_database(db)
    yield db
    await db.dispose()
    set_database(None)


@pytest.fixture
async def session(database) -> AsyncIterator[AsyncSession]:
    """A transactional session, committed when the test body succeeds."""
    async with database.session() as active:
        yield active


@pytest.fixture
def services(session: AsyncSession) -> object:
    """Service container bound to the test session."""
    from app.services.container import ServiceContainer

    return ServiceContainer(session=session)


@pytest.fixture
async def teacher(services) -> object:
    """A registered teacher to own the test data."""
    from app.schemas.teacher import TeacherIdentity

    return await services.teachers.get_or_create(
        TeacherIdentity(telegram_id=424242, full_name="Test Teacher", username="tester")
    )


@pytest.fixture
async def classroom(services, teacher):
    """A class named ``SE401`` owned by :func:`teacher`."""
    from app.schemas.classroom import CreateClassInput

    result = await services.classes.create_class(
        teacher.id, CreateClassInput(name="SE401", description=None)
    )
    return result.classroom


@pytest.fixture
async def roster(services, teacher, classroom):
    """Three students enrolled in :func:`classroom`."""
    from app.schemas.student import AddStudentInput

    people = [
        ("SE001", "Nguyen Van A"),
        ("SE002", "John Smith"),
        ("SE003", "Alice Nguyen"),
    ]
    created = []
    for code, name in people:
        result = await services.students.add_student(
            teacher.id,
            AddStudentInput(class_name=classroom.name, full_name=name, student_code=code),
        )
        created.append(result.student)
    return created
