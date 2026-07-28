"""Teacher ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.classroom import Classroom


class Teacher(IdMixin, TimestampMixin, Base):
    """A bot user who owns classes.

    The teacher is the ownership root of the data model: every class, student
    and attendance record is reachable from exactly one teacher, and every
    service call is scoped by ``teacher_id``.  Adding a ``School`` tenant above
    this later only requires a nullable foreign key on this table.
    """

    __tablename__ = "teachers"

    #: Telegram user id.  Telegram ids exceed 32 bits, hence ``BigInteger``.
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), default=None)
    language_code: Mapped[str | None] = mapped_column(String(16), default=None)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )

    classes: Mapped[list[Classroom]] = relationship(
        back_populates="teacher",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise_on_sql",
    )

    @property
    def display_name(self) -> str:
        """Preferred way to address the teacher in bot replies."""
        return self.full_name or (f"@{self.username}" if self.username else "teacher")
