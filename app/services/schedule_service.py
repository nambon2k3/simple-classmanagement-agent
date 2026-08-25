"""Weekly timetable and extra-session business logic."""

from __future__ import annotations

from calendar import monthrange
from datetime import date, time, timedelta

from app.core.exceptions import (
    ClassNotFoundError,
    ScheduleConflictError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models.classroom import Classroom
from app.models.schedule import ClassExtraSession, ClassScheduleRule
from app.repositories.class_repository import ClassRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import (
    WEEKDAY_LABELS,
    ExtraSessionRead,
    ScheduleOccurrence,
    ScheduleRuleRead,
)

logger = get_logger(__name__)


class ScheduleService:
    """Maintain repeating slots and expand them onto a month calendar."""

    def __init__(
        self,
        schedule_repository: ScheduleRepository,
        class_repository: ClassRepository,
    ) -> None:
        """Wire the service to its data sources."""
        self._schedule = schedule_repository
        self._classes = class_repository

    async def list_rules(self, teacher_id: int, class_id: int) -> list[ScheduleRuleRead]:
        """Weekly slots for one owned class."""
        await self._require_class(teacher_id, class_id)
        rules = await self._schedule.list_rules_for_class(class_id)
        return [_rule_read(rule) for rule in rules]

    async def add_rule(
        self,
        teacher_id: int,
        class_id: int,
        weekday: int,
        start_time: time,
        end_time: time,
    ) -> ScheduleRuleRead:
        """Add a repeating weekday slot.

        Raises:
            ClassNotFoundError: If the class is not owned by the teacher.
            ValidationError: If the weekday or times are invalid.
            ScheduleConflictError: If that slot already exists.
        """
        await self._require_class(teacher_id, class_id)
        _validate_slot(weekday, start_time, end_time)
        existing = await self._schedule.get_rule_by_slot(class_id, weekday, start_time)
        if existing is not None:
            raise ScheduleConflictError(
                f"{WEEKDAY_LABELS[weekday]} at {start_time.strftime('%H:%M')} "
                "is already on the timetable."
            )
        rule = await self._schedule.add(
            ClassScheduleRule(
                class_id=class_id,
                weekday=weekday,
                start_time=start_time,
                end_time=end_time,
                is_active=True,
            )
        )
        logger.info(
            "Schedule rule added",
            extra={"class_id": class_id, "weekday": weekday, "start": str(start_time)},
        )
        return _rule_read(rule)

    async def remove_rule(self, teacher_id: int, class_id: int, rule_id: int) -> None:
        """Delete a weekly slot."""
        await self._require_class(teacher_id, class_id)
        rule = await self._schedule.get_rule(rule_id, class_id)
        if rule is None:
            raise ClassNotFoundError("That timetable slot could not be found.")
        await self._schedule.delete(rule)

    async def list_extras(self, teacher_id: int, class_id: int) -> list[ExtraSessionRead]:
        """One-off extra classes for an owned class."""
        await self._require_class(teacher_id, class_id)
        extras = await self._schedule.list_extras_for_class(class_id)
        return [_extra_read(extra) for extra in extras]

    async def add_extra(
        self,
        teacher_id: int,
        class_id: int,
        session_date: date,
        start_time: time,
        end_time: time,
        note: str | None = None,
    ) -> ExtraSessionRead:
        """Schedule a one-off extra class.

        Raises:
            ScheduleConflictError: If that class already has an extra on the date.
        """
        await self._require_class(teacher_id, class_id)
        _validate_times(start_time, end_time)
        existing = await self._schedule.get_extra_on_date(class_id, session_date)
        if existing is not None:
            raise ScheduleConflictError(
                f"An extra class is already scheduled on {session_date.isoformat()}."
            )
        extra = await self._schedule.add_extra(
            ClassExtraSession(
                class_id=class_id,
                session_date=session_date,
                start_time=start_time,
                end_time=end_time,
                note=note,
            )
        )
        logger.info(
            "Extra session added",
            extra={"class_id": class_id, "session_date": session_date.isoformat()},
        )
        return _extra_read(extra)

    async def remove_extra(self, teacher_id: int, class_id: int, extra_id: int) -> None:
        """Delete a one-off extra class."""
        await self._require_class(teacher_id, class_id)
        extra = await self._schedule.get_extra(extra_id, class_id)
        if extra is None:
            raise ClassNotFoundError("That extra class could not be found.")
        await self._schedule.delete_extra(extra)

    async def month_occurrences(
        self,
        teacher_id: int,
        year: int,
        month: int,
        class_id: int | None = None,
    ) -> list[ScheduleOccurrence]:
        """Expand weekly rules and extras onto the days of ``year``/``month``."""
        start = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end = date(year, month, last_day) + timedelta(days=1)

        if class_id is not None:
            classroom = await self._require_class(teacher_id, class_id)
            rules = [
                rule
                for rule in await self._schedule.list_rules_for_class(class_id)
                if rule.is_active
            ]
            extras = [
                extra
                for extra in await self._schedule.list_extras_for_class(class_id)
                if start <= extra.session_date < end
            ]
            names = {classroom.id: classroom.name}
        else:
            rules = await self._schedule.list_active_rules_for_teacher(teacher_id)
            extras = await self._schedule.list_extras_for_teacher_in_range(teacher_id, start, end)
            classrooms = await self._classes.list_for_teacher(teacher_id)
            names = {item.id: item.name for item in classrooms}

        overridden = {(extra.class_id, extra.session_date) for extra in extras}
        occurrences: list[ScheduleOccurrence] = []
        day = start
        while day < end:
            weekday = day.weekday()
            for rule in rules:
                if rule.weekday != weekday:
                    continue
                if (rule.class_id, day) in overridden:
                    continue
                class_name = names.get(rule.class_id)
                if class_name is None:
                    continue
                occurrences.append(
                    ScheduleOccurrence(
                        class_id=rule.class_id,
                        class_name=class_name,
                        session_date=day,
                        start_time=rule.start_time,
                        end_time=rule.end_time,
                        kind="weekly",
                    )
                )
            day += timedelta(days=1)

        for extra in extras:
            class_name = names.get(extra.class_id)
            if class_name is None:
                continue
            occurrences.append(
                ScheduleOccurrence(
                    class_id=extra.class_id,
                    class_name=class_name,
                    session_date=extra.session_date,
                    start_time=extra.start_time,
                    end_time=extra.end_time,
                    kind="extra",
                    extra_id=extra.id,
                    note=extra.note,
                )
            )

        occurrences.sort(key=lambda item: (item.session_date, item.start_time, item.class_name))
        return occurrences

    async def _require_class(self, teacher_id: int, class_id: int) -> Classroom:
        """Return the class or raise if the teacher does not own it."""
        classroom = await self._classes.get_owned(class_id, teacher_id)
        if classroom is None:
            raise ClassNotFoundError("I couldn't find that class.")
        return classroom


def _validate_slot(weekday: int, start_time: time, end_time: time) -> None:
    """Reject an out-of-range weekday or inverted times."""
    if weekday < 0 or weekday > 6:
        raise ValidationError("Weekday must be between Monday and Sunday.")
    _validate_times(start_time, end_time)


def _validate_times(start_time: time, end_time: time) -> None:
    """Require a positive duration."""
    if end_time <= start_time:
        raise ValidationError("End time must be after start time.")


def _rule_read(rule: ClassScheduleRule) -> ScheduleRuleRead:
    """Project a weekly slot onto the dashboard read model."""
    return ScheduleRuleRead(
        id=rule.id,
        class_id=rule.class_id,
        weekday=rule.weekday,
        weekday_label=WEEKDAY_LABELS[rule.weekday],
        start_time=rule.start_time,
        end_time=rule.end_time,
        is_active=rule.is_active,
    )


def _extra_read(extra: ClassExtraSession) -> ExtraSessionRead:
    """Project a one-off session onto the dashboard read model."""
    return ExtraSessionRead(
        id=extra.id,
        class_id=extra.class_id,
        session_date=extra.session_date,
        start_time=extra.start_time,
        end_time=extra.end_time,
        note=extra.note,
    )
