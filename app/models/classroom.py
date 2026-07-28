"""Class ORM model.

Named ``Classroom`` in Python because ``class`` is a reserved word; the table
itself is ``classes``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BigIntPk, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.attendance import AttendanceSession
    from app.models.student import Student
    from app.models.teacher import Teacher


class Classroom(IdMixin, TimestampMixin, Base):
    """A group of students taught by one teacher."""

    __tablename__ = "classes"
    __table_args__ = (
        # Case-insensitive uniqueness per teacher: "se401" must collide with
        # "SE401".  Enforced in the database so a race between two concurrent
        # updates cannot create duplicates.
        Index(
            "uq_classes_teacher_id_name_lower",
            "teacher_id",
            text("lower(name)"),
            unique=True,
        ),
    )

    teacher_id: Mapped[int] = mapped_column(
        BigIntPk,
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    teacher: Mapped[Teacher] = relationship(back_populates="classes", lazy="raise_on_sql")
    students: Mapped[list[Student]] = relationship(
        back_populates="classroom",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise_on_sql",
        order_by="Student.full_name",
    )
    attendance_sessions: Mapped[list[AttendanceSession]] = relationship(
        back_populates="classroom",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise_on_sql",
    )
