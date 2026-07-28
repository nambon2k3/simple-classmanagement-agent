"""Attendance reporting business logic."""

from __future__ import annotations

from datetime import date, timedelta

from app.core.logging import get_logger
from app.models.enums import AttendanceStatus
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.class_repository import ClassRepository
from app.schemas.attendance import AttendanceSummary
from app.schemas.reports import (
    AttendanceHistoryEntry,
    AttendanceReportInput,
    AttendanceReportOutput,
    DateRange,
    MonthlySummaryInput,
    MonthlySummaryOutput,
    ReportPeriod,
    SessionSummaryRead,
    StudentAttendanceReportInput,
    StudentAttendanceReportOutput,
    StudentAttendanceRow,
    StudentsByStatusInput,
    StudentsByStatusOutput,
    StudentStatusOccurrence,
)
from app.services.class_service import ClassService
from app.services.student_service import StudentService
from app.utils.datetime_utils import (
    format_date,
    month_bounds,
    parse_date,
    today,
    week_bounds,
)

logger = get_logger(__name__)

#: Lower/upper bounds standing in for "no date filter at all".
_MIN_DATE = date(1970, 1, 1)
_MAX_DATE = date(9999, 12, 31)


def resolve_period(
    period: ReportPeriod,
    start_date: str | None = None,
    end_date: str | None = None,
) -> DateRange:
    """Turn a named period into a concrete inclusive date range.

    Keeping this in one function means every report interprets "this week" the
    same way, anchored to the configured timezone.

    Args:
        period: The named range requested.
        start_date: First day, only consulted for :attr:`ReportPeriod.CUSTOM`.
        end_date: Last day, only consulted for :attr:`ReportPeriod.CUSTOM`.

    Returns:
        The resolved range together with a human-readable label.

    Raises:
        ValueError: If a custom range is requested with unparsable dates or
            with the end before the start.
    """
    match period:
        case ReportPeriod.TODAY:
            day = today()
            return DateRange(start_date=day, end_date=day, label=f"today ({format_date(day)})")
        case ReportPeriod.YESTERDAY:
            day = today() - timedelta(days=1)
            return DateRange(start_date=day, end_date=day, label=f"yesterday ({format_date(day)})")
        case ReportPeriod.THIS_WEEK:
            start, end = week_bounds()
            return DateRange(start_date=start, end_date=end, label="this week")
        case ReportPeriod.LAST_WEEK:
            start, end = week_bounds(today() - timedelta(days=7))
            return DateRange(start_date=start, end_date=end, label="last week")
        case ReportPeriod.THIS_MONTH:
            start, end = month_bounds()
            return DateRange(start_date=start, end_date=end, label=start.strftime("%B %Y"))
        case ReportPeriod.LAST_MONTH:
            start, end = month_bounds(today().replace(day=1) - timedelta(days=1))
            return DateRange(start_date=start, end_date=end, label=start.strftime("%B %Y"))
        case ReportPeriod.ALL_TIME:
            return DateRange(start_date=_MIN_DATE, end_date=_MAX_DATE, label="all time")
        case ReportPeriod.CUSTOM:
            start = parse_date(start_date, default_to_today=True)
            end = parse_date(end_date, default_to_today=True)
            if end < start:
                raise ValueError("The end date cannot be before the start date.")
            return DateRange(
                start_date=start,
                end_date=end,
                label=(
                    format_date(start)
                    if start == end
                    else f"{format_date(start)} to {format_date(end)}"
                ),
            )


class ReportService:
    """Aggregate attendance data into teacher-facing reports."""

    def __init__(
        self,
        attendance_repository: AttendanceRepository,
        class_repository: ClassRepository,
        class_service: ClassService,
        student_service: StudentService,
    ) -> None:
        """Wire the service to its collaborators.

        Args:
            attendance_repository: Source of all aggregate queries.
            class_repository: Used to enumerate classes and roster sizes.
            class_service: Resolves class names.
            student_service: Resolves loose student references.
        """
        self._attendance = attendance_repository
        self._class_repo = class_repository
        self._classes = class_service
        self._students = student_service

    # ---------------------------------------------------- class / date report --

    async def attendance_report(
        self, teacher_id: int, payload: AttendanceReportInput
    ) -> AttendanceReportOutput:
        """Report attendance for one class, or all classes, over a range."""
        date_range = resolve_period(payload.period, payload.start_date, payload.end_date)

        if payload.class_name:
            classroom = await self._classes.resolve(teacher_id, payload.class_name)
            class_ids = [(classroom.id, classroom.name)]
        else:
            class_ids = [
                (item.id, item.name) for item in await self._class_repo.list_for_teacher(teacher_id)
            ]

        sessions: list[SessionSummaryRead] = []
        totals: dict[AttendanceStatus, int] = {}

        for class_id, class_name in class_ids:
            # Counted once per class rather than once per session.
            roster_size = await self._class_repo.count_students(class_id)
            for session in await self._attendance.list_for_class(
                class_id, date_range.start_date, date_range.end_date
            ):
                counts = await self._attendance.status_counts_for_session(session.id)
                for status, count in counts.items():
                    totals[status] = totals.get(status, 0) + count
                sessions.append(
                    SessionSummaryRead(
                        session_id=session.id,
                        session_date=session.session_date,
                        class_name=class_name,
                        status=session.status.value,
                        summary=AttendanceSummary.from_counts(counts, roster_size),
                    )
                )

        sessions.sort(key=lambda item: (item.session_date, item.class_name))
        return AttendanceReportOutput(
            range=date_range,
            class_name=payload.class_name,
            summary=AttendanceSummary.from_counts(totals),
            sessions=sessions,
            total_sessions=len(sessions),
        )

    # ------------------------------------------------------- student report --

    async def student_attendance_report(
        self, teacher_id: int, payload: StudentAttendanceReportInput
    ) -> StudentAttendanceReportOutput:
        """Report one student's attendance over a range."""
        date_range = resolve_period(payload.period, payload.start_date, payload.end_date)
        class_id = None
        if payload.class_name:
            classroom = await self._classes.resolve(teacher_id, payload.class_name)
            class_id = classroom.id

        student = await self._students.resolve(teacher_id, payload.student, class_id=class_id)
        counts = await self._attendance.status_counts_for_student(
            student.id, date_range.start_date, date_range.end_date
        )
        history = await self._attendance.list_student_history(
            student.id, date_range.start_date, date_range.end_date
        )

        return StudentAttendanceReportOutput(
            range=date_range,
            class_name=student.classroom.name,
            student=_to_row(student.student_code, student.full_name, counts),
            history=[
                AttendanceHistoryEntry(session_date=day, status=status) for day, status in history
            ],
        )

    # ------------------------------------------------------- monthly summary --

    async def monthly_summary(
        self, teacher_id: int, payload: MonthlySummaryInput
    ) -> MonthlySummaryOutput:
        """Per-student attendance matrix for one class over one month."""
        classroom = await self._classes.resolve(teacher_id, payload.class_name)
        anchor = parse_date(payload.month) if payload.month else today()
        start, end = month_bounds(anchor)
        date_range = DateRange(start_date=start, end_date=end, label=start.strftime("%B %Y"))

        rows = await self._attendance.per_student_status_counts(classroom.id, start, end)
        per_student: dict[int, tuple[str, str, dict[AttendanceStatus, int]]] = {}
        for student, status, count in rows:
            entry = per_student.setdefault(
                student.id, (student.student_code, student.full_name, {})
            )
            entry[2][status] = count

        students = [_to_row(code, name, counts) for code, name, counts in per_student.values()]
        students.sort(key=lambda row: (row.attendance_rate, row.full_name))

        totals: dict[AttendanceStatus, int] = {}
        for _, _, counts in per_student.values():
            for status, count in counts.items():
                totals[status] = totals.get(status, 0) + count

        sessions = await self._attendance.list_for_class(classroom.id, start, end)
        return MonthlySummaryOutput(
            range=date_range,
            class_name=classroom.name,
            total_sessions=len(sessions),
            students=students,
            summary=AttendanceSummary.from_counts(totals),
        )

    # ----------------------------------------------------- status occurrences --

    async def students_by_status(
        self, teacher_id: int, payload: StudentsByStatusInput
    ) -> StudentsByStatusOutput:
        """List every occurrence of a status in a range.

        Backs both "who was absent today?" and "how many students were absent
        this week?" — the first reads ``occurrences``, the second reads the
        counts.
        """
        date_range = resolve_period(payload.period, payload.start_date, payload.end_date)
        class_id = None
        if payload.class_name:
            classroom = await self._classes.resolve(teacher_id, payload.class_name)
            class_id = classroom.id

        rows = await self._attendance.list_records_with_status(
            teacher_id,
            [payload.status],
            date_range.start_date,
            date_range.end_date,
            class_id=class_id,
        )
        occurrences = [
            StudentStatusOccurrence(
                student_code=student.student_code,
                full_name=student.full_name,
                class_name=classroom.name,
                session_date=day,
                note=record.note,
            )
            for record, student, classroom, day in rows
        ]
        return StudentsByStatusOutput(
            range=date_range,
            status=payload.status,
            class_name=payload.class_name,
            occurrences=occurrences,
            total_occurrences=len(occurrences),
            unique_students=len({item.student_code for item in occurrences}),
        )


def _to_row(
    student_code: str, full_name: str, counts: dict[AttendanceStatus, int]
) -> StudentAttendanceRow:
    """Build a per-student report row from raw status counts."""
    summary = AttendanceSummary.from_counts(counts)
    return StudentAttendanceRow(
        student_code=student_code,
        full_name=full_name,
        present=summary.present,
        absent=summary.absent,
        late=summary.late,
        excused=summary.excused,
        attendance_rate=round(summary.attendance_rate, 4),
    )
