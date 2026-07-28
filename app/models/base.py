"""Declarative base and shared column mixins."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

#: Deterministic constraint names.  Without these, Alembic autogenerate emits
#: unnamed constraints that cannot be dropped in a downgrade on PostgreSQL.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

#: 64-bit primary keys on PostgreSQL, plain INTEGER on SQLite where SQLite
#: only auto-increments a column typed exactly ``INTEGER``.
BigIntPk = BigInteger().with_variant(Integer, "sqlite")


class Base(DeclarativeBase):
    """Base class for every ORM model."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        """Return ``<ModelName id=...>`` for readable logs and test failures."""
        identifier = getattr(self, "id", None)
        return f"<{type(self).__name__} id={identifier}>"


class IdMixin:
    """Surrogate integer primary key."""

    id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)


class TimestampMixin:
    """Server-side created/updated audit columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
