"""Tuition billing tool contracts."""

from __future__ import annotations

from datetime import date

from pydantic import Field, field_validator

from app.schemas.common import ClassName, DateInput, ToolInput, ToolOutput
from app.schemas.reports import DateRange, ReportPeriod


class SetClassTuitionFeeInput(ToolInput):
    """Arguments for ``set_class_tuition_fee``."""

    class_name: ClassName = Field(description="Class whose daily tuition fee should change.")
    daily_tuition_fee: int = Field(
        ge=0,
        description="Fee in VND charged per student for each attended day (present or late).",
    )


class SetClassTuitionFeeOutput(ToolOutput):
    """Result of updating a class tuition fee."""

    class_name: str = Field(description="Class that was updated.")
    daily_tuition_fee: int = Field(description="New daily fee in VND.")
    formatted_fee: str = Field(description="Human-readable fee, for example '50.000 VND'.")
    message: str = Field(description="Short confirmation for the teacher.")


class StudentTuitionRow(ToolOutput):
    """One student's tuition over a date range."""

    student_code: str = Field(description="Teacher-facing student ID.")
    full_name: str = Field(description="Student's full name.")
    attended_days: int = Field(description="Days the student attended (present or late).")
    amount_vnd: int = Field(description="Total tuition owed in VND.")
    formatted_amount: str = Field(description="Human-readable total, for example '150.000 VND'.")


class ClassTuitionSummary(ToolOutput):
    """Tuition totals for one class over a date range."""

    class_name: str = Field(description="Class name.")
    daily_tuition_fee: int = Field(description="Fee per attended day in VND.")
    formatted_daily_fee: str = Field(description="Human-readable daily fee.")
    teaching_days: int = Field(
        description="Number of completed teaching days (attendance sessions) in the range."
    )
    students: list[StudentTuitionRow] = Field(
        default_factory=list, description="Per-student tuition, alphabetical by name."
    )
    total_tuition_vnd: int = Field(description="Sum of every student's tuition in VND.")
    formatted_total: str = Field(description="Human-readable class total.")


class TuitionReportInput(ToolInput):
    """Arguments for ``tuition_report``.

    Answers questions like "tuition for SE401 in July" or "how much did students
    owe last week".
    """

    class_name: ClassName | None = Field(
        default=None, description="Restrict to one class. Omit for every class."
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


class TuitionReportOutput(ToolOutput):
    """Tuition billed from attendance over a date range."""

    range: DateRange = Field(description="The range that was reported on.")
    teaching_days: int = Field(
        description="Total completed teaching days across the included classes."
    )
    classes: list[ClassTuitionSummary] = Field(
        default_factory=list, description="Per-class tuition breakdown."
    )
    total_tuition_vnd: int = Field(description="Grand total across all included classes.")
    formatted_total: str = Field(description="Human-readable grand total.")


class TeachingDaysReportInput(ToolInput):
    """Arguments for ``teaching_days_report``."""

    period: ReportPeriod = Field(
        default=ReportPeriod.THIS_MONTH, description="Named range to report on."
    )
    start_date: DateInput | None = Field(
        default=None, description="First day (YYYY-MM-DD). Only used when period is 'custom'."
    )
    end_date: DateInput | None = Field(
        default=None, description="Last day (YYYY-MM-DD). Only used when period is 'custom'."
    )


class ClassTeachingDaysRow(ToolOutput):
    """Teaching-day count for one class."""

    class_name: str = Field(description="Class name.")
    teaching_days: int = Field(description="Completed attendance sessions in the range.")


class TeachingDaysReportOutput(ToolOutput):
    """How many days the teacher held class over a range."""

    range: DateRange = Field(description="The range that was reported on.")
    total_teaching_days: int = Field(
        description="Distinct calendar days with at least one completed session."
    )
    classes: list[ClassTeachingDaysRow] = Field(
        default_factory=list, description="Per-class teaching-day counts."
    )

    @field_validator("classes")
    @classmethod
    def _sort_classes(cls, value: list[ClassTeachingDaysRow]) -> list[ClassTeachingDaysRow]:
        return sorted(value, key=lambda row: row.class_name)


class TuitionStatusSummary(ToolOutput):
    """Completed versus unpaid tuition across the teacher's classes."""

    not_yet_vnd: int = Field(description="Sum of unpaid charges in VND.")
    completed_vnd: int = Field(description="Sum of paid charges in VND.")
    formatted_not_yet: str = Field(description="Human-readable unpaid total.")
    formatted_completed: str = Field(description="Human-readable paid total.")


class StudentTuitionStatusRow(ToolOutput):
    """Payment status for one student in one class."""

    student_id: int = Field(description="Internal student identifier.")
    student_code: str = Field(description="Teacher-facing student ID.")
    full_name: str = Field(description="Student's full name.")
    unpaid_days: int = Field(description="Present/late days that are not yet paid.")
    unpaid_vnd: int = Field(description="Amount still owed in VND.")
    completed_vnd: int = Field(description="Amount already paid in VND.")
    formatted_unpaid: str = Field(description="Human-readable unpaid amount.")
    status: str = Field(description="Not yet or Completed.")


class AttendanceMark(ToolOutput):
    """One day of a student's attendance since their last payment."""

    session_date: date = Field(description="Day the class met.")
    attended: bool = Field(description="True when the student was present or late.")
    recorded: bool = Field(default=True, description="False when nobody marked the student.")


class StudentAttendanceSinceRow(ToolOutput):
    """A student's day-by-day attendance since their last tuition payment."""

    student_id: int = Field(description="Internal student identifier.")
    student_code: str = Field(description="Teacher-facing student ID.")
    full_name: str = Field(description="Student's full name.")
    paid_through: date | None = Field(
        default=None,
        description="Last session date already paid for, or null when nothing was ever paid.",
    )
    marks: list[AttendanceMark] = Field(
        default_factory=list, description="One entry per day the class met, oldest first."
    )
    present_days: int = Field(default=0, description="Days attended in the unpaid window.")
    absent_days: int = Field(default=0, description="Days missed in the unpaid window.")
    unpaid_vnd: int = Field(default=0, description="Outstanding tuition in VND.")
    formatted_unpaid: str = Field(description="Human-readable outstanding amount.")


class ClassAttendanceSinceOutput(ToolOutput):
    """Attendance for every student in a class since their last payment."""

    class_name: str = Field(description="Class that was summarised.")
    students: list[StudentAttendanceSinceRow] = Field(
        default_factory=list, description="Rows ordered by student name."
    )
    total_present: int = Field(default=0, description="Attended days across the class.")
    total_absent: int = Field(default=0, description="Missed days across the class.")
    session_days: int = Field(
        default=0, description="Distinct days the class met inside the reported window."
    )
