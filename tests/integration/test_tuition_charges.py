"""Persisted tuition charges created from completed attendance."""

from __future__ import annotations

import pytest

from app.models.enums import AttendanceStatus, TuitionChargeStatus
from app.schemas.attendance import (
    FinishAttendanceInput,
    StartAttendanceInput,
    UpdateAttendanceInput,
)
from app.schemas.reports import ReportPeriod
from app.schemas.tuition import SetClassTuitionFeeInput, TuitionReportInput
from app.utils.datetime_utils import today
from tests.integration.test_tuition import _finish_day


@pytest.fixture
async def fee_class(services, teacher, classroom):
    await services.tuition.set_class_tuition_fee(
        teacher.id,
        SetClassTuitionFeeInput(class_name="SE401", daily_tuition_fee=50_000),
    )


async def test_finish_creates_unpaid_charges_for_billable_students(
    services, teacher, roster, classroom, fee_class
):
    await _finish_day(
        services,
        teacher,
        today(),
        statuses={
            "SE001": AttendanceStatus.PRESENT,
            "SE002": AttendanceStatus.ABSENT,
            "SE003": AttendanceStatus.LATE,
        },
    )
    rows = await services.tuition.student_status_rows(teacher.id, classroom.id)
    by_code = {row.student_code: row for row in rows}
    assert by_code["SE001"].unpaid_days == 1
    assert by_code["SE001"].unpaid_vnd == 50_000
    assert by_code["SE001"].status == TuitionChargeStatus.NOT_YET.label
    assert by_code["SE002"].unpaid_days == 0
    assert by_code["SE002"].status == TuitionChargeStatus.COMPLETED.label
    assert by_code["SE003"].unpaid_days == 1
    assert by_code["SE003"].unpaid_vnd == 50_000

    summary = await services.tuition.status_summary(teacher.id)
    assert summary.not_yet_vnd == 100_000
    assert summary.completed_vnd == 0


async def test_fee_update_recalculates_unpaid_charges_only(
    services, teacher, roster, classroom, fee_class
):
    day = today()
    await _finish_day(
        services,
        teacher,
        day,
        statuses={
            "SE001": AttendanceStatus.PRESENT,
            "SE002": AttendanceStatus.PRESENT,
            "SE003": AttendanceStatus.ABSENT,
        },
    )
    class_id = classroom.id
    await services.tuition.mark_student_completed(teacher.id, class_id, roster[0].id)
    await services.tuition.set_class_tuition_fee(
        teacher.id, SetClassTuitionFeeInput(class_name="SE401", daily_tuition_fee=80_000)
    )
    rows = await services.tuition.student_status_rows(teacher.id, class_id)
    by_code = {row.student_code: row for row in rows}
    assert by_code["SE001"].unpaid_days == 0
    assert by_code["SE001"].completed_vnd == 50_000
    assert by_code["SE002"].unpaid_days == 1
    assert by_code["SE002"].unpaid_vnd == 80_000


async def test_mark_completed_pays_all_outstanding_days(
    services, teacher, roster, classroom, fee_class
):
    class_id = classroom.id
    await _finish_day(
        services,
        teacher,
        today(),
        statuses={
            "SE001": AttendanceStatus.PRESENT,
            "SE002": AttendanceStatus.ABSENT,
            "SE003": AttendanceStatus.ABSENT,
        },
    )
    updated = await services.tuition.mark_student_completed(teacher.id, class_id, roster[0].id)
    assert updated == 1
    rows = await services.tuition.student_status_rows(teacher.id, class_id)
    se001 = next(row for row in rows if row.student_code == "SE001")
    assert se001.unpaid_days == 0
    assert se001.status == TuitionChargeStatus.COMPLETED.label
    summary = await services.tuition.status_summary(teacher.id)
    assert summary.not_yet_vnd == 0
    assert summary.completed_vnd == 50_000


async def test_tuition_report_still_counts_all_attended_days(
    services, teacher, roster, classroom, fee_class
):
    await _finish_day(
        services,
        teacher,
        today(),
        statuses={
            "SE001": AttendanceStatus.PRESENT,
            "SE002": AttendanceStatus.ABSENT,
            "SE003": AttendanceStatus.ABSENT,
        },
    )
    await services.tuition.mark_student_completed(teacher.id, classroom.id, roster[0].id)
    report = await services.tuition.tuition_report(
        teacher.id, TuitionReportInput(class_name="SE401", period=ReportPeriod.TODAY)
    )
    by_code = {row.student_code: row for row in report.classes[0].students}
    assert by_code["SE001"].amount_vnd == 50_000


async def test_reopen_and_finish_does_not_duplicate_charges(
    services, teacher, roster, classroom, fee_class
):
    day = today()
    await _finish_day(
        services,
        teacher,
        day,
        statuses={
            "SE001": AttendanceStatus.PRESENT,
            "SE002": AttendanceStatus.ABSENT,
            "SE003": AttendanceStatus.ABSENT,
        },
    )
    await services.attendance.start_attendance(
        teacher.id,
        StartAttendanceInput(class_name="SE401", session_date=day.isoformat(), reopen=True),
    )
    await services.attendance.update_attendance(
        teacher.id, UpdateAttendanceInput(student="SE001", status=AttendanceStatus.PRESENT)
    )
    await services.attendance.finish_attendance(
        teacher.id, FinishAttendanceInput(class_name="SE401")
    )
    rows = await services.tuition.student_status_rows(teacher.id, classroom.id)
    se001 = next(row for row in rows if row.student_code == "SE001")
    assert se001.unpaid_days == 1
