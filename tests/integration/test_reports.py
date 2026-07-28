"""Reporting behaviour, including period resolution."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.models.enums import AttendanceStatus
from app.schemas.attendance import (
    FinishAttendanceInput,
    StartAttendanceInput,
    UpdateAttendanceInput,
)
from app.schemas.reports import (
    AttendanceReportInput,
    MonthlySummaryInput,
    ReportPeriod,
    StudentAttendanceReportInput,
    StudentsByStatusInput,
)
from app.services.report_service import resolve_period
from app.utils.datetime_utils import month_bounds, today, week_bounds


async def record_day(services, teacher, day: date, statuses: dict[str, AttendanceStatus]) -> None:
    """Run one complete attendance session on ``day``."""
    await services.attendance.start_attendance(
        teacher.id, StartAttendanceInput(class_name="SE401", session_date=day.isoformat())
    )
    for reference, status in statuses.items():
        await services.attendance.update_attendance(
            teacher.id, UpdateAttendanceInput(student=reference, status=status)
        )
    await services.attendance.finish_attendance(
        teacher.id, FinishAttendanceInput(class_name="SE401")
    )


@pytest.fixture
async def history(services, teacher, roster):
    """Three days of attendance: today and the two days before."""
    days = [today() - timedelta(days=offset) for offset in (2, 1, 0)]
    await record_day(services, teacher, days[0], {"SE001": AttendanceStatus.ABSENT})
    await record_day(services, teacher, days[1], {"SE002": AttendanceStatus.LATE})
    await record_day(
        services,
        teacher,
        days[2],
        {"SE001": AttendanceStatus.ABSENT, "SE003": AttendanceStatus.EXCUSED},
    )
    return days


# ------------------------------------------------------- period resolution --


def test_today_period_is_a_single_day():
    resolved = resolve_period(ReportPeriod.TODAY)
    assert resolved.start_date == resolved.end_date == today()


def test_this_week_matches_the_calendar_week():
    resolved = resolve_period(ReportPeriod.THIS_WEEK)
    assert (resolved.start_date, resolved.end_date) == week_bounds()


def test_this_month_matches_the_calendar_month():
    resolved = resolve_period(ReportPeriod.THIS_MONTH)
    assert (resolved.start_date, resolved.end_date) == month_bounds()


def test_last_month_precedes_this_month():
    resolved = resolve_period(ReportPeriod.LAST_MONTH)
    assert resolved.end_date < month_bounds()[0]


def test_custom_period_uses_the_supplied_dates():
    resolved = resolve_period(ReportPeriod.CUSTOM, "2026-01-05", "2026-01-09")
    assert resolved.start_date == date(2026, 1, 5)
    assert resolved.end_date == date(2026, 1, 9)


def test_a_reversed_custom_period_is_rejected():
    with pytest.raises(ValueError, match="cannot be before"):
        resolve_period(ReportPeriod.CUSTOM, "2026-01-09", "2026-01-05")


# ----------------------------------------------------- class / date reports --


async def test_todays_report_covers_only_today(services, teacher, history):
    report = await services.reports.attendance_report(
        teacher.id, AttendanceReportInput(class_name="SE401", period=ReportPeriod.TODAY)
    )
    assert report.total_sessions == 1
    assert report.summary.absent == 1
    assert report.summary.excused == 1
    assert report.summary.present == 1


async def test_a_multi_day_report_aggregates_every_session(services, teacher, history):
    report = await services.reports.attendance_report(
        teacher.id, AttendanceReportInput(class_name="SE401", period=ReportPeriod.ALL_TIME)
    )
    assert report.total_sessions == 3
    assert report.summary.absent == 2
    assert report.summary.late == 1
    assert report.summary.excused == 1


async def test_a_report_without_a_class_covers_every_class(services, teacher, history):
    report = await services.reports.attendance_report(
        teacher.id, AttendanceReportInput(period=ReportPeriod.ALL_TIME)
    )
    assert report.class_name is None
    assert report.total_sessions == 3


async def test_a_report_over_a_quiet_period_is_empty_not_an_error(services, teacher, roster):
    report = await services.reports.attendance_report(
        teacher.id, AttendanceReportInput(class_name="SE401", period=ReportPeriod.LAST_MONTH)
    )
    assert report.total_sessions == 0
    assert report.summary.total == 0


# ------------------------------------------------------------ student report --


async def test_student_report_counts_and_history(services, teacher, history):
    report = await services.reports.student_attendance_report(
        teacher.id,
        StudentAttendanceReportInput(student="SE001", period=ReportPeriod.ALL_TIME),
    )
    assert report.student.full_name == "Nguyen Van A"
    assert report.student.absent == 2
    assert report.student.present == 1
    assert report.class_name == "SE401"
    assert len(report.history) == 3
    assert report.history[0].session_date < report.history[-1].session_date


async def test_student_report_rate_counts_late_as_attended(services, teacher, history):
    report = await services.reports.student_attendance_report(
        teacher.id,
        StudentAttendanceReportInput(student="John", period=ReportPeriod.ALL_TIME),
    )
    assert report.student.late == 1
    assert report.student.present == 2
    assert report.student.attendance_rate == pytest.approx(1.0)


# ---------------------------------------------------------- monthly summary --


async def test_monthly_summary_ranks_worst_attendance_first(services, teacher, history):
    summary = await services.reports.monthly_summary(
        teacher.id, MonthlySummaryInput(class_name="SE401")
    )
    assert summary.class_name == "SE401"
    assert len(summary.students) == 3
    assert summary.students[0].student_code == "SE001"  # two absences
    assert summary.students[0].attendance_rate < summary.students[-1].attendance_rate


# --------------------------------------------------------- status questions --


async def test_who_was_absent_today(services, teacher, history):
    result = await services.reports.students_by_status(
        teacher.id,
        StudentsByStatusInput(status=AttendanceStatus.ABSENT, period=ReportPeriod.TODAY),
    )
    assert result.total_occurrences == 1
    assert result.unique_students == 1
    assert result.occurrences[0].full_name == "Nguyen Van A"


async def test_how_many_absences_this_week(services, teacher, history):
    result = await services.reports.students_by_status(
        teacher.id,
        StudentsByStatusInput(status=AttendanceStatus.ABSENT, period=ReportPeriod.ALL_TIME),
    )
    assert result.total_occurrences == 2
    assert result.unique_students == 1  # the same student, on two days


async def test_status_search_can_be_restricted_to_a_class(services, teacher, history):
    result = await services.reports.students_by_status(
        teacher.id,
        StudentsByStatusInput(
            status=AttendanceStatus.LATE, class_name="SE401", period=ReportPeriod.ALL_TIME
        ),
    )
    assert result.total_occurrences == 1
    assert result.occurrences[0].class_name == "SE401"


async def test_reports_never_leak_another_teachers_data(services, teacher, history):
    from app.schemas.teacher import TeacherIdentity

    intruder = await services.teachers.get_or_create(
        TeacherIdentity(telegram_id=1234, full_name="Intruder")
    )
    result = await services.reports.students_by_status(
        teacher_id=intruder.id,
        payload=StudentsByStatusInput(status=AttendanceStatus.ABSENT, period=ReportPeriod.ALL_TIME),
    )
    assert result.total_occurrences == 0
