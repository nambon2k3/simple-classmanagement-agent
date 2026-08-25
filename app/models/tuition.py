"""Persisted tuition charges billed from completed attendance."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BigIntPk, IdMixin, TimestampMixin
from app.models.enums import TuitionChargeStatus

if TYPE_CHECKING:
    from app.models.attendance import AttendanceSession
    from app.models.student import Student


def _pg_enum(enum_type: type, name: str) -> Enum:
    """Store enum *values* (``not_yet``) rather than member names."""
    return Enum(
        enum_type,
        name=name,
        native_enum=True,
        validate_strings=True,
        values_callable=lambda enum: [member.value for member in enum],
    )


class TuitionCharge(IdMixin, TimestampMixin, Base):
    """One billed attendance day for one student.

    Created when an attendance session is finished.  ``not_yet`` rows follow
    the current class fee; ``completed`` rows keep the amount that was paid.
    """

    __tablename__ = "tuition_charges"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "session_id",
            name="uq_tuition_charges_student_id_session_id",
        ),
    )

    student_id: Mapped[int] = mapped_column(
        BigIntPk,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[int] = mapped_column(
        BigIntPk,
        ForeignKey("attendance_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_vnd: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    status: Mapped[TuitionChargeStatus] = mapped_column(
        _pg_enum(TuitionChargeStatus, "tuition_charge_status"),
        nullable=False,
        default=TuitionChargeStatus.NOT_YET,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    student: Mapped[Student] = relationship(back_populates="tuition_charges", lazy="raise_on_sql")
    session: Mapped[AttendanceSession] = relationship(
        back_populates="tuition_charges", lazy="raise_on_sql"
    )
