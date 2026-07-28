"""Tuition billing from attendance."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.models.enums import AttendanceStatus
from app.schemas.attendance import (
    FinishAttendanceInput,
    StartAttendanceInput,
    UpdateAttendanceInput,
)
from app.schemas.reports import ReportPeriod
from app.schemas.tuition import SetClassTuitionFeeInput, TeachingDaysReportInput, TuitionReportInput
from app.utils.datetime_utils import today


async def _finish_day(
    services,
    teacher,
    day: date,
    *,
    class_name: str = "SE401",
    statuses: dict[str, AttendanceStatus] | None = None,
) -> None:
    await services.attendance.start_attendance(
        teacher.id,
        StartAttendanceInput(class_name=class_name, session_date=day.isoformat()),
    )
    for reference, status in (statuses or {}).items():
        await services.attendance.update_attendance(
            teacher.id, UpdateAttendanceInput(student=reference, status=status)
        )
    await services.attendance.finish_attendance(
        teacher.id, FinishAttendanceInput(class_name=class_name)
    )


@pytest.fixture
async def fee_class(services, teacher, classroom):
    await services.tuition.set_class_tuition_fee(
        teacher.id,
        SetClassTuitionFeeInput(class_name="SE401", daily_tuition_fee=50_000),
    )


async def test_set_class_tuition_fee(services, teacher, classroom):
    result = await services.tuition.set_class_tuition_fee(
        teacher.id,
        SetClassTuitionFeeInput(class_name="SE401", daily_tuition_fee=50_000),
    )
    assert result.daily_tuition_fee == 50_000
    assert "50.000 VND" in result.formatted_fee


async def test_tuition_charges_attended_days_only(services, teacher, roster, fee_class):
    day = today()
    await _finish_day(
        services,
        teacher,
        day,
        statuses={
            "SE001": AttendanceStatus.PRESENT,
            "SE002": AttendanceStatus.ABSENT,
            "SE003": AttendanceStatus.LATE,
        },
    )

    report = await services.tuition.tuition_report(
        teacher.id,
        TuitionReportInput(class_name="SE401", period=ReportPeriod.TODAY),
    )

    assert report.classes[0].teaching_days == 1
    assert report.classes[0].total_tuition_vnd == 100_000
    by_code = {row.student_code: row for row in report.classes[0].students}
    assert by_code["SE001"].amount_vnd == 50_000
    assert by_code["SE002"].amount_vnd == 0
    assert by_code["SE003"].amount_vnd == 50_000


async def test_tuition_totals_multiple_days(services, teacher, roster, fee_class):
    days = [today() - timedelta(days=1), today()]
    await _finish_day(services, teacher, days[0], statuses={"SE001": AttendanceStatus.PRESENT})
    await _finish_day(services, teacher, days[1], statuses={"SE001": AttendanceStatus.PRESENT})

    report = await services.tuition.tuition_report(
        teacher.id,
        TuitionReportInput(class_name="SE401", period=ReportPeriod.THIS_WEEK),
    )

    se001 = next(row for row in report.classes[0].students if row.student_code == "SE001")
    assert se001.attended_days == 2
    assert se001.amount_vnd == 100_000
    assert report.classes[0].teaching_days == 2


async def test_teaching_days_report_counts_completed_sessions(services, teacher, roster, fee_class):
    await _finish_day(services, teacher, today())
    await _finish_day(services, teacher, today() - timedelta(days=1))

    report = await services.tuition.teaching_days_report(
        teacher.id,
        TeachingDaysReportInput(period=ReportPeriod.THIS_WEEK),
    )

    assert report.total_teaching_days == 2
    assert report.classes[0].teaching_days == 2


async def test_open_sessions_do_not_count_toward_tuition(services, teacher, roster, fee_class):
    await services.attendance.start_attendance(
        teacher.id,
        StartAttendanceInput(class_name="SE401"),
    )
    await services.attendance.update_attendance(
        teacher.id,
        UpdateAttendanceInput(student="SE001", status=AttendanceStatus.PRESENT),
    )

    report = await services.tuition.tuition_report(
        teacher.id,
        TuitionReportInput(class_name="SE401", period=ReportPeriod.TODAY),
    )

    assert report.classes[0].total_tuition_vnd == 0
    assert report.classes[0].teaching_days == 0
