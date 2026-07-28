"""Reporting tool contracts."""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import Field

from app.models.enums import AttendanceStatus
from app.schemas.attendance import AttendanceSummary
from app.schemas.common import ClassName, DateInput, StudentReference, ToolInput, ToolOutput


class ReportPeriod(StrEnum):
    """Named date ranges the model can request without doing date arithmetic.

    Letting the model pick a keyword instead of computing ``start_date`` and
    ``end_date`` removes a whole class of off-by-one errors, and keeps
    "this week" anchored to the teacher's configured timezone.
    """

    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    ALL_TIME = "all_time"
    CUSTOM = "custom"


class DateRange(ToolOutput):
    """The concrete range a report was computed over."""

    start_date: date = Field(description="First day included, inclusive.")
    end_date: date = Field(description="Last day included, inclusive.")
    label: str = Field(description="Human-readable description of the range.")


class SessionSummaryRead(ToolOutput):
    """One session's headline numbers inside a report."""

    session_id: int = Field(description="Internal attendance session identifier.")
    session_date: date = Field(description="Date of the session.")
    class_name: str = Field(description="Class the session belongs to.")
    status: str = Field(description="Whether the session is open, completed or cancelled.")
    summary: AttendanceSummary = Field(description="Counts for the session.")


class StudentAttendanceRow(ToolOutput):
    """One student's aggregated attendance inside a report."""

    student_code: str = Field(description="Teacher-facing student ID.")
    full_name: str = Field(description="Student's full name.")
    present: int = Field(default=0, description="Sessions marked present.")
    absent: int = Field(default=0, description="Sessions marked absent.")
    late: int = Field(default=0, description="Sessions marked late.")
    excused: int = Field(default=0, description="Sessions marked excused.")
    attendance_rate: float = Field(
        default=0.0, description="Share of sessions attended, between 0 and 1."
    )


# -------------------------------------------------------- attendance_report --


class AttendanceReportInput(ToolInput):
    """Arguments for ``attendance_report``.

    Covers "attendance for SE401", "attendance report for today" and any
    custom range, without needing three separate tools.
    """

    class_name: ClassName | None = Field(
        default=None, description="Restrict to one class. Omit to cover every class."
    )
    period: ReportPeriod = Field(
        default=ReportPeriod.TODAY, description="Named range to report on."
    )
    start_date: DateInput | None = Field(
        default=None, description="First day (YYYY-MM-DD). Only used when period is 'custom'."
    )
    end_date: DateInput | None = Field(
        default=None, description="Last day (YYYY-MM-DD). Only used when period is 'custom'."
    )


class AttendanceReportOutput(ToolOutput):
    """Attendance aggregated over a date range."""

    range: DateRange = Field(description="The range that was reported on.")
    class_name: str | None = Field(default=None, description="Class filter that was applied.")
    summary: AttendanceSummary = Field(description="Totals across every session in range.")
    sessions: list[SessionSummaryRead] = Field(
        default_factory=list, description="Per-session breakdown, oldest first."
    )
    total_sessions: int = Field(default=0, description="Number of sessions in range.")


# ------------------------------------------------ student_attendance_report --


class StudentAttendanceReportInput(ToolInput):
    """Arguments for ``student_attendance_report``."""

    student: StudentReference = Field(description="Student name or ID to report on.")
    class_name: ClassName | None = Field(
        default=None, description="Class to look in, when the reference is ambiguous."
    )
    period: ReportPeriod = Field(
        default=ReportPeriod.THIS_MONTH, description="Named range to report on."
    )
    start_date: DateInput | None = Field(
        default=None, description="First day (YYYY-MM-DD). Only used when period is 'custom'."
    )
    end_date: DateInput | None = Field(
        default=None, description="Last day (YYYY-MM-DD). Only used when period is 'custom'."
    )


class AttendanceHistoryEntry(ToolOutput):
    """A single dated status in a student's history."""

    session_date: date = Field(description="Date of the session.")
    status: AttendanceStatus = Field(description="Status recorded on that date.")


class StudentAttendanceReportOutput(ToolOutput):
    """One student's attendance over a range."""

    range: DateRange = Field(description="The range that was reported on.")
    student: StudentAttendanceRow = Field(description="Aggregated counts for the student.")
    class_name: str = Field(description="Class the student belongs to.")
    history: list[AttendanceHistoryEntry] = Field(
        default_factory=list, description="Day-by-day statuses, oldest first."
    )


# ----------------------------------------------- monthly_attendance_summary --


class MonthlySummaryInput(ToolInput):
    """Arguments for ``monthly_attendance_summary``."""

    class_name: ClassName = Field(description="Class to summarise.")
    month: DateInput | None = Field(
        default=None,
        description="Any date inside the month of interest (YYYY-MM-DD). Defaults to this month.",
    )


class MonthlySummaryOutput(ToolOutput):
    """Per-student attendance matrix for one month."""

    range: DateRange = Field(description="The month that was summarised.")
    class_name: str = Field(description="Class that was summarised.")
    total_sessions: int = Field(description="Sessions held in the month.")
    students: list[StudentAttendanceRow] = Field(
        default_factory=list, description="Per-student totals, worst attendance first."
    )
    summary: AttendanceSummary = Field(description="Class-wide totals for the month.")


# ------------------------------------------------------ students_by_status --


class StudentsByStatusInput(ToolInput):
    """Arguments for ``list_students_by_status``.

    Answers "who was absent today?" and "how many students were absent this
    week?".
    """

    status: AttendanceStatus = Field(
        default=AttendanceStatus.ABSENT, description="Status to filter on."
    )
    class_name: ClassName | None = Field(default=None, description="Restrict to one class.")
    period: ReportPeriod = Field(default=ReportPeriod.TODAY, description="Named range to search.")
    start_date: DateInput | None = Field(
        default=None, description="First day (YYYY-MM-DD). Only used when period is 'custom'."
    )
    end_date: DateInput | None = Field(
        default=None, description="Last day (YYYY-MM-DD). Only used when period is 'custom'."
    )


class StudentStatusOccurrence(ToolOutput):
    """One occurrence of a status for a student on a date."""

    student_code: str = Field(description="Teacher-facing student ID.")
    full_name: str = Field(description="Student's full name.")
    class_name: str = Field(description="Class the student belongs to.")
    session_date: date = Field(description="Date the status was recorded.")
    note: str | None = Field(default=None, description="Note attached to the record, if any.")


class StudentsByStatusOutput(ToolOutput):
    """Every occurrence of a status in a range."""

    range: DateRange = Field(description="The range that was searched.")
    status: AttendanceStatus = Field(description="The status that was searched for.")
    class_name: str | None = Field(default=None, description="Class filter that was applied.")
    occurrences: list[StudentStatusOccurrence] = Field(
        default_factory=list, description="Matching records, oldest first."
    )
    total_occurrences: int = Field(default=0, description="Number of matching records.")
    unique_students: int = Field(default=0, description="Number of distinct students involved.")
