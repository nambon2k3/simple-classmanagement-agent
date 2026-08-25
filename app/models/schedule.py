"""Weekly class timetable and one-off extra sessions."""

from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, SmallInteger, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BigIntPk, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.classroom import Classroom


class ClassScheduleRule(IdMixin, TimestampMixin, Base):
    """A repeating weekday slot for one class, for example every Tuesday 19:00-21:00."""

    __tablename__ = "class_schedule_rules"
    __table_args__ = (
        UniqueConstraint(
            "class_id",
            "weekday",
            "start_time",
            name="uq_class_schedule_rules_class_id_weekday_start_time",
        ),
    )

    class_id: Mapped[int] = mapped_column(
        BigIntPk,
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    #: Monday = 0 … Sunday = 6, matching :meth:`datetime.date.weekday`.
    weekday: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    classroom: Mapped[Classroom] = relationship(
        back_populates="schedule_rules", lazy="raise_on_sql"
    )


class ClassExtraSession(IdMixin, TimestampMixin, Base):
    """A one-off extra class on a specific calendar date."""

    __tablename__ = "class_extra_sessions"
    __table_args__ = (
        UniqueConstraint(
            "class_id",
            "session_date",
            name="uq_class_extra_sessions_class_id_session_date",
        ),
    )

    class_id: Mapped[int] = mapped_column(
        BigIntPk,
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, default=None)

    classroom: Mapped[Classroom] = relationship(
        back_populates="extra_sessions", lazy="raise_on_sql"
    )
