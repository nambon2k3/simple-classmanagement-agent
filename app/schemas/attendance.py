"""Attendance read models and tool contracts."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

from pydantic import Field

from app.models.enums import AttendanceSessionStatus, AttendanceStatus
from app.schemas.common import (
    ClassName,
    DateInput,
    OperationResult,
    ShortText,
    StudentReference,
    ToolInput,
    ToolOutput,
)


class AttendanceEntry(ToolOutput):
    """One student's state inside an attendance session."""

    student_id: int = Field(description="Internal student identifier.")
    student_code: str = Field(description="Teacher-facing student ID.")
    full_name: str = Field(description="Student's full name.")
    status: AttendanceStatus | None = Field(
        default=None, description="Recorded status, or null if not marked yet."
    )
    note: str | None = Field(default=None, description="Optional note on the record.")


class AttendanceSummary(ToolOutput):
    """Counts of each status within a session or a date range."""

    present: int = Field(default=0, description="Students marked present.")
    absent: int = Field(default=0, description="Students marked absent.")
    late: int = Field(default=0, description="Students marked late.")
    excused: int = Field(default=0, description="Students marked excused.")
    unmarked: int = Field(default=0, description="Students with no status yet.")
    total: int = Field(default=0, description="Total students considered.")

    @property
    def attendance_rate(self) -> float:
        """Share of students who were in the room (present or late), 0..1."""
        if not self.total:
            return 0.0
        return (self.present + self.late) / self.total

    @classmethod
    def from_counts(
        cls, counts: Mapping[AttendanceStatus, int], total: int | None = None
    ) -> AttendanceSummary:
        """Build a summary from per-status counts.

        Args:
            counts: Number of records per status.
            total: Size of the cohort.  Defaults to the number of marked
                records, which is what reports (as opposed to live sessions)
                want, since an unmarked student has no record at all.
        """
        marked = sum(counts.values())
        cohort = marked if total is None else total
        return cls(
            present=counts.get(AttendanceStatus.PRESENT, 0),
            absent=counts.get(AttendanceStatus.ABSENT, 0),
            late=counts.get(AttendanceStatus.LATE, 0),
            excused=counts.get(AttendanceStatus.EXCUSED, 0),
            unmarked=max(0, cohort - marked),
            total=cohort,
        )


class AttendanceSessionRead(ToolOutput):
    """Full state of an attendance session."""

    session_id: int = Field(description="Internal attendance session identifier.")
    class_id: int = Field(description="Internal identifier of the class.")
    class_name: str = Field(description="Class the session belongs to.")
    session_date: date = Field(description="Calendar date of the session.")
    status: AttendanceSessionStatus = Field(description="Session lifecycle state.")
    entries: list[AttendanceEntry] = Field(description="Per-student state, ordered by name.")
    summary: AttendanceSummary = Field(description="Aggregate counts for the session.")


# -------------------------------------------------------- start_attendance --


class StartAttendanceInput(ToolInput):
    """Arguments for ``start_attendance``."""

    class_name: ClassName = Field(description="Class to take attendance for.")
    session_date: DateInput | None = Field(
        default=None,
        description="Date of the session as YYYY-MM-DD. Defaults to today when omitted.",
    )
    reopen: bool = Field(
        default=False,
        description=(
            "Set to true only when the teacher explicitly wants to amend attendance "
            "that was already completed for that date."
        ),
    )


class StartAttendanceOutput(OperationResult):
    """Result of opening an attendance session."""

    session: AttendanceSessionRead = Field(description="The session that is now open.")
    resumed: bool = Field(
        default=False,
        description="True when an existing open session was resumed rather than created.",
    )


# ------------------------------------------------------- update_attendance --


class UpdateAttendanceInput(ToolInput):
    """Arguments for ``update_attendance``."""

    student: StudentReference = Field(
        description="Student name or ID, for example 'John' or 'SE001'."
    )
    status: AttendanceStatus = Field(description="Status to record for the student.")
    class_name: ClassName | None = Field(
        default=None,
        description=(
            "Class of the session. Omit when an attendance session is already active; "
            "supply it only to disambiguate."
        ),
    )
    note: ShortText | None = Field(default=None, description="Optional note, e.g. a reason.")


class UpdateAttendanceOutput(OperationResult):
    """Result of marking one student."""

    student: str = Field(description="Label of the student that was marked.")
    status: AttendanceStatus = Field(description="The status that was recorded.")
    summary: AttendanceSummary = Field(description="Session counts after the change.")


# ------------------------------------------------- mark_remaining_students --


class MarkRemainingInput(ToolInput):
    """Arguments for ``mark_remaining_students``."""

    status: AttendanceStatus = Field(
        default=AttendanceStatus.PRESENT,
        description="Status to apply to everyone not marked yet.",
    )
    class_name: ClassName | None = Field(
        default=None, description="Class of the session, when it is ambiguous."
    )


class MarkRemainingOutput(OperationResult):
    """Result of bulk-marking the unmarked students."""

    updated: int = Field(description="How many students were marked.")
    summary: AttendanceSummary = Field(description="Session counts after the change.")


# ------------------------------------------------------- finish_attendance --


class FinishAttendanceInput(ToolInput):
    """Arguments for ``finish_attendance``."""

    class_name: ClassName | None = Field(
        default=None, description="Class of the session, when it is ambiguous."
    )
    default_status_for_unmarked: AttendanceStatus = Field(
        default=AttendanceStatus.PRESENT,
        description="Status applied to any student still unmarked when finishing.",
    )


class FinishAttendanceOutput(OperationResult):
    """Summary produced when a session is finalised."""

    class_name: str = Field(description="Class the session belonged to.")
    session_date: date = Field(description="Date of the session.")
    summary: AttendanceSummary = Field(description="Final counts.")
    absent_students: list[str] = Field(
        default_factory=list, description="Names of students marked absent."
    )
    late_students: list[str] = Field(
        default_factory=list, description="Names of students marked late."
    )
    excused_students: list[str] = Field(
        default_factory=list, description="Names of students marked excused."
    )


# -------------------------------------------------------- cancel / inspect --


class CancelAttendanceInput(ToolInput):
    """Arguments for ``cancel_attendance``."""

    class_name: ClassName | None = Field(
        default=None, description="Class of the session to abandon."
    )


class GetAttendanceStateInput(ToolInput):
    """Arguments for ``get_attendance_state``."""

    class_name: ClassName | None = Field(
        default=None, description="Class to inspect. Defaults to the active session."
    )


class GetAttendanceStateOutput(ToolOutput):
    """The currently open session, if there is one."""

    has_active_session: bool = Field(description="Whether a session is currently open.")
    session: AttendanceSessionRead | None = Field(
        default=None, description="The open session, when one exists."
    )
