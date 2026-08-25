"""Weekly timetable expansion and extra-session overlay."""

from __future__ import annotations

from datetime import date, time

import pytest

from app.core.exceptions import ScheduleConflictError, ValidationError


async def test_weekly_rule_expands_onto_matching_weekdays(services, teacher, classroom):
    await services.schedule.add_rule(
        teacher.id, classroom.id, weekday=1, start_time=time(19, 0), end_time=time(21, 0)
    )
    occurrences = await services.schedule.month_occurrences(teacher.id, 2026, 8)
    tuesdays = [item for item in occurrences if item.session_date.weekday() == 1]
    assert tuesdays
    assert all(item.class_name == "SE401" for item in tuesdays)
    assert all(item.kind == "weekly" for item in tuesdays)
    assert all(item.start_time == time(19, 0) for item in tuesdays)


async def test_extra_session_overlays_weekly_slot_on_that_date(services, teacher, classroom):
    await services.schedule.add_rule(
        teacher.id, classroom.id, weekday=1, start_time=time(19, 0), end_time=time(21, 0)
    )
    extra_day = date(2026, 8, 25)
    await services.schedule.add_extra(
        teacher.id, classroom.id, extra_day, time(9, 0), time(11, 0), note="Makeup"
    )
    occurrences = await services.schedule.month_occurrences(teacher.id, 2026, 8)
    on_day = [item for item in occurrences if item.session_date == extra_day]
    assert len(on_day) == 1
    assert on_day[0].kind == "extra"
    assert on_day[0].start_time == time(9, 0)
    assert on_day[0].note == "Makeup"


async def test_duplicate_weekly_slot_is_rejected(services, teacher, classroom):
    await services.schedule.add_rule(
        teacher.id, classroom.id, weekday=2, start_time=time(18, 0), end_time=time(20, 0)
    )
    with pytest.raises(ScheduleConflictError):
        await services.schedule.add_rule(
            teacher.id, classroom.id, weekday=2, start_time=time(18, 0), end_time=time(20, 0)
        )


async def test_end_time_must_follow_start_time(services, teacher, classroom):
    with pytest.raises(ValidationError):
        await services.schedule.add_rule(
            teacher.id, classroom.id, weekday=0, start_time=time(20, 0), end_time=time(18, 0)
        )


async def test_remove_rule(services, teacher, classroom):
    rule = await services.schedule.add_rule(
        teacher.id, classroom.id, weekday=4, start_time=time(8, 0), end_time=time(10, 0)
    )
    await services.schedule.remove_rule(teacher.id, classroom.id, rule.id)
    remaining = await services.schedule.list_rules(teacher.id, classroom.id)
    assert remaining == []
