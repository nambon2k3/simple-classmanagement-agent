"""Data access for weekly timetable rules and extra sessions."""

from __future__ import annotations

from datetime import date, time

from sqlalchemy import select

from app.models.classroom import Classroom
from app.models.schedule import ClassExtraSession, ClassScheduleRule
from app.repositories.base import BaseRepository


class ScheduleRepository(BaseRepository[ClassScheduleRule]):
    """Queries for repeating slots.  Extra sessions use the same session."""

    model = ClassScheduleRule

    async def list_rules_for_class(self, class_id: int) -> list[ClassScheduleRule]:
        """Return active and inactive weekly slots for one class, weekday order."""
        result = await self.session.scalars(
            select(ClassScheduleRule)
            .where(ClassScheduleRule.class_id == class_id)
            .order_by(ClassScheduleRule.weekday, ClassScheduleRule.start_time)
        )
        return list(result)

    async def list_active_rules_for_teacher(self, teacher_id: int) -> list[ClassScheduleRule]:
        """Every active weekly slot owned by the teacher."""
        result = await self.session.scalars(
            select(ClassScheduleRule)
            .join(Classroom, ClassScheduleRule.class_id == Classroom.id)
            .where(Classroom.teacher_id == teacher_id, ClassScheduleRule.is_active.is_(True))
            .order_by(ClassScheduleRule.weekday, ClassScheduleRule.start_time)
        )
        return list(result)

    async def get_rule(self, rule_id: int, class_id: int) -> ClassScheduleRule | None:
        """Fetch one weekly slot belonging to a class."""
        return await self.session.scalar(
            select(ClassScheduleRule).where(
                ClassScheduleRule.id == rule_id,
                ClassScheduleRule.class_id == class_id,
            )
        )

    async def get_rule_by_slot(
        self, class_id: int, weekday: int, start: time
    ) -> ClassScheduleRule | None:
        """Look up a weekly slot by its unique key."""
        return await self.session.scalar(
            select(ClassScheduleRule).where(
                ClassScheduleRule.class_id == class_id,
                ClassScheduleRule.weekday == weekday,
                ClassScheduleRule.start_time == start,
            )
        )

    async def list_extras_for_class(self, class_id: int) -> list[ClassExtraSession]:
        """One-off sessions for a class, chronological."""
        result = await self.session.scalars(
            select(ClassExtraSession)
            .where(ClassExtraSession.class_id == class_id)
            .order_by(ClassExtraSession.session_date, ClassExtraSession.start_time)
        )
        return list(result)

    async def list_extras_for_teacher_in_range(
        self, teacher_id: int, start: date, end: date
    ) -> list[ClassExtraSession]:
        """Extra sessions whose date falls in ``[start, end)``."""
        result = await self.session.scalars(
            select(ClassExtraSession)
            .join(Classroom, ClassExtraSession.class_id == Classroom.id)
            .where(
                Classroom.teacher_id == teacher_id,
                ClassExtraSession.session_date >= start,
                ClassExtraSession.session_date < end,
            )
            .order_by(ClassExtraSession.session_date, ClassExtraSession.start_time)
        )
        return list(result)

    async def get_extra(self, extra_id: int, class_id: int) -> ClassExtraSession | None:
        """Fetch one extra session belonging to a class."""
        return await self.session.scalar(
            select(ClassExtraSession).where(
                ClassExtraSession.id == extra_id,
                ClassExtraSession.class_id == class_id,
            )
        )

    async def get_extra_on_date(
        self, class_id: int, session_date: date
    ) -> ClassExtraSession | None:
        """Look up an extra session by class and calendar day."""
        return await self.session.scalar(
            select(ClassExtraSession).where(
                ClassExtraSession.class_id == class_id,
                ClassExtraSession.session_date == session_date,
            )
        )

    async def add_extra(self, extra: ClassExtraSession) -> ClassExtraSession:
        """Persist a one-off session."""
        self.session.add(extra)
        await self.session.flush()
        return extra

    async def delete_extra(self, extra: ClassExtraSession) -> None:
        """Remove a one-off session."""
        await self.session.delete(extra)
        await self.session.flush()
