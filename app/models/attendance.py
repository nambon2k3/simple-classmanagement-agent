"""Attendance ORM models."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BigIntPk, IdMixin, TimestampMixin
from app.models.enums import AttendanceSessionStatus, AttendanceStatus

if TYPE_CHECKING:
    from app.models.classroom import Classroom
    from app.models.student import Student


def _pg_enum(enum_type: type, name: str) -> Enum:
    """Build a database enum that stores the lower-case member *values*.

    Without ``values_callable`` SQLAlchemy persists member *names*
    (``PRESENT``), which would not round-trip against the string values used
    throughout the schemas and AI tool contracts.
    """
    return Enum(
        enum_type,
        name=name,
        native_enum=True,
        validate_strings=True,
        values_callable=lambda enum: [member.value for member in enum],
    )


class AttendanceSession(IdMixin, TimestampMixin, Base):
    """One roll-call for a class on a given calendar day.

    At most one session may exist per class per day; the unique constraint is
    what turns a second "take attendance for SE401" into a friendly
    "attendance already taken today" instead of duplicate data.
    """

    __tablename__ = "attendance_sessions"
    __table_args__ = (
        UniqueConstraint(
            "class_id", "session_date", name="uq_attendance_sessions_class_id_session_date"
        ),
        Index("ix_attendance_sessions_class_id_session_date", "class_id", "session_date"),
    )

    class_id: Mapped[int] = mapped_column(
        BigIntPk,
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[AttendanceSessionStatus] = mapped_column(
        _pg_enum(AttendanceSessionStatus, "attendance_session_status"),
        nullable=False,
        default=AttendanceSessionStatus.OPEN,
    )
    note: Mapped[str | None] = mapped_column(Text, default=None)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    classroom: Mapped[Classroom] = relationship(
        back_populates="attendance_sessions", lazy="raise_on_sql"
    )
    records: Mapped[list[AttendanceRecord]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise_on_sql",
    )

    @property
    def is_open(self) -> bool:
        """Whether records may still be modified."""
        return self.status is AttendanceSessionStatus.OPEN


class AttendanceRecord(IdMixin, TimestampMixin, Base):
    """The status of one student within one attendance session."""

    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "student_id", name="uq_attendance_records_session_id_student_id"
        ),
        Index("ix_attendance_records_student_id_session_id", "student_id", "session_id"),
    )

    session_id: Mapped[int] = mapped_column(
        BigIntPk,
        ForeignKey("attendance_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[int] = mapped_column(
        BigIntPk,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        _pg_enum(AttendanceStatus, "attendance_status"),
        nullable=False,
        default=AttendanceStatus.PRESENT,
    )
    note: Mapped[str | None] = mapped_column(Text, default=None)
    marked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    session: Mapped[AttendanceSession] = relationship(back_populates="records", lazy="raise_on_sql")
    student: Mapped[Student] = relationship(
        back_populates="attendance_records", lazy="raise_on_sql"
    )
