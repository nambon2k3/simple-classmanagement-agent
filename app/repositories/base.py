"""Generic repository base.

Repositories are the only place that builds SQL.  Services depend on them
rather than on :class:`~sqlalchemy.ext.asyncio.AsyncSession` directly, which is
what keeps the business rules unit-testable against fakes.
"""

from __future__ import annotations

from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base


class BaseRepository[ModelT: Base]:
    """CRUD primitives shared by every concrete repository.

    Subclasses set :attr:`model` and add query methods that express domain
    intent (``get_by_name``, ``list_for_teacher``, …) rather than exposing a
    generic query builder.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to a unit of work.

        Args:
            session: The active transactional session.
        """
        self.session = session

    async def get(self, entity_id: int) -> ModelT | None:
        """Fetch a row by primary key, or ``None`` when it does not exist."""
        return await self.session.get(self.model, entity_id)

    async def add(self, instance: ModelT) -> ModelT:
        """Persist a new instance and flush so its primary key is populated."""
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def delete(self, instance: ModelT) -> None:
        """Delete an instance and flush the change."""
        await self.session.delete(instance)
        await self.session.flush()

    async def delete_by_id(self, entity_id: int) -> int:
        """Delete by primary key without loading the row.

        Returns:
            The number of rows removed (0 or 1).
        """
        result = await self.session.execute(
            sa_delete(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        )
        await self.session.flush()
        return result.rowcount or 0

    async def list_all(self) -> list[ModelT]:
        """Return every row.  Intended for small reference tables and tests."""
        result = await self.session.scalars(select(self.model))
        return list(result)

    async def flush(self) -> None:
        """Push pending changes to the database without committing."""
        await self.session.flush()

    async def refresh(self, instance: ModelT) -> ModelT:
        """Reload an instance from the database."""
        await self.session.refresh(instance)
        return instance
