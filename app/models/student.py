"""Student ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BigIntPk, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.attendance import AttendanceRecord
    from app.models.classroom import Classroom
    from app.models.tuition import TuitionCharge


class Student(IdMixin, TimestampMixin, Base):
    """A learner enrolled in exactly one class.

    ``student_code`` is the teacher-facing identifier (for example ``SE001``).
    It is stored upper-cased by the service layer so that the unique constraint
    below behaves case-insensitively without needing a functional index.
    """

    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("class_id", "student_code", name="uq_students_class_id_student_code"),
    )

    class_id: Mapped[int] = mapped_column(
        BigIntPk,
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_code: Mapped[str] = mapped_column(String(32), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), default=None)
    phone: Mapped[str | None] = mapped_column(String(32), default=None)
    note: Mapped[str | None] = mapped_column(Text, default=None)

    classroom: Mapped[Classroom] = relationship(back_populates="students", lazy="raise_on_sql")
    attendance_records: Mapped[list[AttendanceRecord]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise_on_sql",
    )
    tuition_charges: Mapped[list[TuitionCharge]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise_on_sql",
    )

    @property
    def display_label(self) -> str:
        """``"Nguyen Van A (SE001)"`` — how a student is shown to the teacher."""
        return f"{self.full_name} ({self.student_code})"
