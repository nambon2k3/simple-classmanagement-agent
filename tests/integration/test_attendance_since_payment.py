"""Attendance shown per student for every day since their last payment."""

from __future__ import annotations

from datetime import timedelta

import pytest

from app.models.enums import AttendanceStatus
from app.schemas.attendance import StartAttendanceInput
from app.schemas.tuition import SetClassTuitionFeeInput
from app.utils.datetime_utils import today
from tests.integration.test_tuition import _finish_day


@pytest.fixture
async def fee_class(services, teacher, classroom):
    await services.tuition.set_class_tuition_fee(
        teacher.id,
        SetClassTuitionFeeInput(class_name="SE401", daily_tuition_fee=50_000),
    )


async def test_marks_cover_every_class_day_when_nothing_was_paid(
    services, teacher, roster, classroom, fee_class
):
    first = today() - timedelta(days=2)
    second = today() - timedelta(days=1)
    await _finish_day(
        services,
        teacher,
        first,
        statuses={"SE001": AttendanceStatus.PRESENT, "SE002": AttendanceStatus.ABSENT},
    )
    await _finish_day(
        services,
        teacher,
        second,
        statuses={"SE001": AttendanceStatus.LATE, "SE002": AttendanceStatus.ABSENT},
    )

    summary = await services.tuition.attendance_since_payment(teacher.id, classroom.id)
    by_code = {row.student_code: row for row in summary.students}

    assert summary.session_days == 2
    assert [mark.session_date for mark in by_code["SE001"].marks] == [first, second]
    # Late still counts as attending, so both days are green.
    assert [mark.attended for mark in by_code["SE001"].marks] == [True, True]
    assert by_code["SE001"].present_days == 2
    assert by_code["SE001"].paid_through is None
    assert [mark.attended for mark in by_code["SE002"].marks] == [False, False]
    assert by_code["SE002"].absent_days == 2


async def test_paid_days_drop_out_of_the_window(services, teacher, roster, classroom, fee_class):
    paid_day = today() - timedelta(days=1)
    unpaid_day = today()
    await _finish_day(services, teacher, paid_day, statuses={"SE001": AttendanceStatus.PRESENT})
    await services.tuition.mark_student_completed(teacher.id, classroom.id, roster[0].id)
    await _finish_day(services, teacher, unpaid_day, statuses={"SE001": AttendanceStatus.ABSENT})

    summary = await services.tuition.attendance_since_payment(teacher.id, classroom.id)
    by_code = {row.student_code: row for row in summary.students}

    se001 = by_code["SE001"]
    assert se001.paid_through == paid_day
    assert [mark.session_date for mark in se001.marks] == [unpaid_day]
    assert se001.present_days == 0
    assert se001.absent_days == 1
    assert se001.unpaid_vnd == 0

    # A student who never paid still sees both days.
    assert len(by_code["SE002"].marks) == 2


async def test_unmarked_students_are_neither_present_nor_paid(
    services, teacher, roster, classroom, fee_class
):
    day = today()
    await services.attendance.start_attendance(
        teacher.id,
        StartAttendanceInput(class_name="SE401", session_date=day.isoformat()),
    )

    summary = await services.tuition.attendance_since_payment(teacher.id, classroom.id)
    marks = summary.students[0].marks
    assert [mark.recorded for mark in marks] == [False]
    assert summary.total_present == 0
    assert summary.total_absent == len(roster)
