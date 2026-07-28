"""Attendance workflow business logic.

The workflow is driven by database state rather than by whatever the
conversation remembers: an attendance session is "active" because a row has
status ``open``, not because the chat context says so.  Conversation memory
only supplies a *hint* about which class the teacher is focused on, so the
workflow still behaves correctly after a restart or a context expiry.

Each operation has two entry points that share one implementation:

* a **conversational** one (``finish_attendance``) that resolves the session
  from a class name or a focus hint, used by the AI tools; and
* a **direct** one (``finish_session``) that takes a session id, used by
  Telegram inline buttons where the id is already known.
"""

from __future__ import annotations

from app.core.exceptions import (
    AmbiguousReferenceError,
    AttendanceAlreadyTakenError,
    AttendanceSessionClosedError,
    EmptyClassError,
    NoActiveAttendanceSessionError,
    StudentNotFoundError,
)
from app.core.logging import get_logger
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.enums import AttendanceSessionStatus, AttendanceStatus
from app.models.student import Student
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.student_repository import StudentRepository
from app.schemas.attendance import (
    AttendanceEntry,
    AttendanceSessionRead,
    AttendanceSummary,
    CancelAttendanceInput,
    FinishAttendanceInput,
    FinishAttendanceOutput,
    GetAttendanceStateInput,
    GetAttendanceStateOutput,
    MarkRemainingInput,
    MarkRemainingOutput,
    StartAttendanceInput,
    StartAttendanceOutput,
    UpdateAttendanceInput,
    UpdateAttendanceOutput,
)
from app.schemas.common import OperationResult
from app.services.class_service import ClassService
from app.services.student_service import StudentService
from app.utils.datetime_utils import format_date, parse_date, utc_now

logger = get_logger(__name__)


class AttendanceService:
    """Open, fill in and finalise attendance sessions."""

    def __init__(
        self,
        attendance_repository: AttendanceRepository,
        student_repository: StudentRepository,
        class_service: ClassService,
        student_service: StudentService,
    ) -> None:
        """Wire the service to its collaborators.

        Args:
            attendance_repository: Access to sessions and records.
            student_repository: Used to build the roster of a session.
            class_service: Resolves class names and enforces ownership.
            student_service: Resolves loose student references.
        """
        self._attendance = attendance_repository
        self._students = student_repository
        self._classes = class_service
        self._student_service = student_service

    # ------------------------------------------------------------- starting --

    async def start_attendance(
        self, teacher_id: int, payload: StartAttendanceInput
    ) -> StartAttendanceOutput:
        """Open (or resume) the attendance session for a class on a date.

        Raises:
            ClassNotFoundError: If the class does not exist.
            EmptyClassError: If the class has no students to mark.
            AttendanceAlreadyTakenError: If the session for that date is already
                completed and ``reopen`` was not requested.
        """
        classroom = await self._classes.resolve(teacher_id, payload.class_name)
        session_date = parse_date(payload.session_date)

        roster = await self._students.list_for_class(classroom.id)
        if not roster:
            raise EmptyClassError(
                f"{classroom.name} has no students yet, so there is nothing to mark.",
                class_name=classroom.name,
            )

        existing = await self._attendance.get_for_class_on_date(classroom.id, session_date)
        resumed = False

        if existing is None:
            session = await self._attendance.add(
                AttendanceSession(
                    class_id=classroom.id,
                    session_date=session_date,
                    status=AttendanceSessionStatus.OPEN,
                )
            )
        elif existing.status is AttendanceSessionStatus.OPEN:
            session, resumed = existing, True
        elif existing.status is AttendanceSessionStatus.COMPLETED and not payload.reopen:
            counts = await self._attendance.status_counts_for_session(existing.id)
            raise AttendanceAlreadyTakenError(
                f"Attendance for {classroom.name} on {format_date(session_date)} is already "
                "complete. I can reopen it if you want to make changes.",
                class_name=classroom.name,
                session_date=session_date.isoformat(),
                summary=AttendanceSummary.from_counts(counts, len(roster)).model_dump(),
            )
        else:
            existing.status = AttendanceSessionStatus.OPEN
            existing.closed_at = None
            await self._attendance.flush()
            session, resumed = existing, True

        logger.info(
            "Attendance session opened",
            extra={
                "teacher_id": teacher_id,
                "class_id": classroom.id,
                "session_id": session.id,
                "resumed": resumed,
            },
        )
        verb = "Resumed" if resumed else "Started"
        return StartAttendanceOutput(
            message=(
                f"{verb} attendance for {classroom.name} on {format_date(session_date)} "
                f"({len(roster)} students)."
            ),
            session=await self.build_session_read(session, classroom.name, roster=roster),
            resumed=resumed,
        )

    # -------------------------------------------------------------- marking --

    async def update_attendance(
        self,
        teacher_id: int,
        payload: UpdateAttendanceInput,
        *,
        preferred_class_id: int | None = None,
    ) -> UpdateAttendanceOutput:
        """Record one student's status in the active session.

        Raises:
            NoActiveAttendanceSessionError: If no session is open.
            StudentNotFoundError: If the reference matches nobody in the class.
            AmbiguousStudentError: If it matches several students.
        """
        session = await self.resolve_active_session(
            teacher_id, payload.class_name, preferred_class_id=preferred_class_id
        )
        student = await self._student_service.resolve(
            teacher_id, payload.student, class_id=session.class_id
        )

        await self._apply_status(session, student, payload.status, payload.note)
        summary = await self._live_summary(session)

        logger.info(
            "Attendance marked",
            extra={
                "session_id": session.id,
                "student_id": student.id,
                "status": payload.status.value,
            },
        )
        return UpdateAttendanceOutput(
            message=(
                f"{student.full_name} marked {payload.status.label.lower()}. "
                f"{summary.unmarked} student(s) still unmarked."
            ),
            student=student.display_label,
            status=payload.status,
            summary=summary,
        )

    async def set_status_by_ids(
        self,
        teacher_id: int,
        session_id: int,
        student_id: int,
        status: AttendanceStatus,
    ) -> AttendanceSessionRead:
        """Mark a student by primary key, for Telegram inline buttons.

        Raises:
            NoActiveAttendanceSessionError: If the session is not visible to
                this teacher.
            AttendanceSessionClosedError: If the session is no longer open.
            StudentNotFoundError: If the student is not in that class.
        """
        session = await self._require_session(teacher_id, session_id)
        student = await self._students.get_owned(student_id, teacher_id)
        if student is None or student.class_id != session.class_id:
            raise StudentNotFoundError("That student is not in this class.")

        await self._apply_status(session, student, status, None)
        return await self.build_session_read(session, await self._class_name(session))

    async def mark_remaining(
        self,
        teacher_id: int,
        payload: MarkRemainingInput,
        *,
        preferred_class_id: int | None = None,
    ) -> MarkRemainingOutput:
        """Apply one status to every student not marked yet."""
        session = await self.resolve_active_session(
            teacher_id, payload.class_name, preferred_class_id=preferred_class_id
        )
        return await self._mark_remaining(session, payload.status)

    async def mark_remaining_in_session(
        self, teacher_id: int, session_id: int, status: AttendanceStatus
    ) -> MarkRemainingOutput:
        """Bulk-mark the unmarked students of a known session."""
        session = await self._require_session(teacher_id, session_id)
        return await self._mark_remaining(session, status)

    # ------------------------------------------------------------ finishing --

    async def finish_attendance(
        self,
        teacher_id: int,
        payload: FinishAttendanceInput,
        *,
        preferred_class_id: int | None = None,
    ) -> FinishAttendanceOutput:
        """Finalise the active session, defaulting anyone still unmarked.

        Raises:
            NoActiveAttendanceSessionError: If no session is open.
        """
        session = await self.resolve_active_session(
            teacher_id, payload.class_name, preferred_class_id=preferred_class_id
        )
        return await self._finalise(session, payload.default_status_for_unmarked)

    async def finish_session(
        self,
        teacher_id: int,
        session_id: int,
        *,
        default_status: AttendanceStatus = AttendanceStatus.PRESENT,
    ) -> FinishAttendanceOutput:
        """Finalise a known session, for Telegram inline buttons."""
        session = await self._require_session(teacher_id, session_id)
        return await self._finalise(session, default_status)

    async def cancel_attendance(
        self,
        teacher_id: int,
        payload: CancelAttendanceInput,
        *,
        preferred_class_id: int | None = None,
    ) -> OperationResult:
        """Abandon the active session without finalising it."""
        session = await self.resolve_active_session(
            teacher_id, payload.class_name, preferred_class_id=preferred_class_id
        )
        return await self._cancel(session)

    async def cancel_session(self, teacher_id: int, session_id: int) -> OperationResult:
        """Abandon a known session, for Telegram inline buttons."""
        session = await self._require_session(teacher_id, session_id)
        return await self._cancel(session)

    # ----------------------------------------------------------------- read --

    async def get_state(
        self,
        teacher_id: int,
        payload: GetAttendanceStateInput,
        *,
        preferred_class_id: int | None = None,
    ) -> GetAttendanceStateOutput:
        """Return the currently open session, if there is one."""
        try:
            session = await self.resolve_active_session(
                teacher_id, payload.class_name, preferred_class_id=preferred_class_id
            )
        except NoActiveAttendanceSessionError:
            return GetAttendanceStateOutput(has_active_session=False, session=None)

        return GetAttendanceStateOutput(
            has_active_session=True,
            session=await self.build_session_read(session, await self._class_name(session)),
        )

    async def get_session_view(self, teacher_id: int, session_id: int) -> AttendanceSessionRead:
        """Render a session by id, for refreshing the Telegram keyboard.

        Unlike :meth:`_require_session` this tolerates a closed session, since
        the keyboard still has to be redrawn (without buttons) after finishing.

        Raises:
            NoActiveAttendanceSessionError: If the session is not visible to
                this teacher.
        """
        session = await self._attendance.get_owned(session_id, teacher_id)
        if session is None:
            raise NoActiveAttendanceSessionError("That attendance session is no longer available.")
        return await self.build_session_read(session, await self._class_name(session))

    async def resolve_active_session(
        self,
        teacher_id: int,
        class_name: str | None = None,
        *,
        preferred_class_id: int | None = None,
    ) -> AttendanceSession:
        """Find the session the teacher is currently working on.

        Resolution order: an explicit class name wins; otherwise the class the
        conversation is focused on; otherwise the teacher's only open session.

        Args:
            teacher_id: Owner of the data.
            class_name: Explicit class, when the teacher named one.
            preferred_class_id: Focus hint from conversation memory.

        Raises:
            NoActiveAttendanceSessionError: If nothing is open.
            AmbiguousReferenceError: If several sessions are open and no hint
                identifies which one is meant.
        """
        if class_name:
            classroom = await self._classes.resolve(teacher_id, class_name)
            session = await self._attendance.get_open_for_class(classroom.id)
            if session is None:
                raise NoActiveAttendanceSessionError(
                    f"There is no attendance session open for {classroom.name}. Start one first.",
                    class_name=classroom.name,
                )
            return session

        if preferred_class_id is not None:
            session = await self._attendance.get_open_for_class(preferred_class_id)
            if session is not None:
                return session

        open_sessions = await self._attendance.list_open_for_teacher(teacher_id)
        if not open_sessions:
            raise NoActiveAttendanceSessionError(
                "No attendance session is open right now. Tell me which class to start with."
            )
        if len(open_sessions) > 1:
            raise AmbiguousReferenceError(
                "You have attendance open for several classes. Which one do you mean?",
                open_classes=[session.classroom.name for session in open_sessions],
            )
        return open_sessions[0]

    async def build_session_read(
        self,
        session: AttendanceSession,
        class_name: str,
        *,
        roster: list[Student] | None = None,
    ) -> AttendanceSessionRead:
        """Project a session plus its roster onto the output schema.

        Every student in the class appears, whether or not they have been
        marked, which is what both the assistant and the inline keyboard need.
        """
        if roster is None:
            roster = await self._students.list_for_class(session.class_id)
        records = {
            record.student_id: record for record in await self._attendance.list_records(session.id)
        }
        entries = [
            AttendanceEntry(
                student_id=student.id,
                student_code=student.student_code,
                full_name=student.full_name,
                status=records[student.id].status if student.id in records else None,
                note=records[student.id].note if student.id in records else None,
            )
            for student in roster
        ]
        counts = _count_statuses(list(records.values()))
        return AttendanceSessionRead(
            session_id=session.id,
            class_id=session.class_id,
            class_name=class_name,
            session_date=session.session_date,
            status=session.status,
            entries=entries,
            summary=AttendanceSummary.from_counts(counts, len(roster)),
        )

    # ------------------------------------------------------------ internals --

    async def _finalise(
        self, session: AttendanceSession, default_status: AttendanceStatus
    ) -> FinishAttendanceOutput:
        """Close a session and build its summary."""
        class_name = await self._class_name(session)
        roster = await self._students.list_for_class(session.class_id)
        auto_marked = await self._mark_unmarked(session, roster, default_status)

        session.status = AttendanceSessionStatus.COMPLETED
        session.closed_at = utc_now()
        await self._attendance.flush()

        records = await self._attendance.list_records(session.id)
        summary = AttendanceSummary.from_counts(_count_statuses(records), len(roster))

        logger.info(
            "Attendance session completed",
            extra={"session_id": session.id, "auto_marked": auto_marked},
        )
        return FinishAttendanceOutput(
            message=(
                f"Attendance for {class_name} on {format_date(session.session_date)} saved: "
                f"{summary.present} present, {summary.absent} absent, {summary.late} late, "
                f"{summary.excused} excused."
            ),
            class_name=class_name,
            session_date=session.session_date,
            summary=summary,
            absent_students=_names_with_status(records, AttendanceStatus.ABSENT),
            late_students=_names_with_status(records, AttendanceStatus.LATE),
            excused_students=_names_with_status(records, AttendanceStatus.EXCUSED),
        )

    async def _cancel(self, session: AttendanceSession) -> OperationResult:
        """Mark a session cancelled."""
        class_name = await self._class_name(session)
        session.status = AttendanceSessionStatus.CANCELLED
        session.closed_at = utc_now()
        await self._attendance.flush()

        logger.info("Attendance session cancelled", extra={"session_id": session.id})
        return OperationResult(
            message=(
                f"Cancelled attendance for {class_name} on "
                f"{format_date(session.session_date)}. Nothing was saved as final."
            )
        )

    async def _mark_remaining(
        self, session: AttendanceSession, status: AttendanceStatus
    ) -> MarkRemainingOutput:
        """Give ``status`` to everyone unmarked and report the new totals."""
        roster = await self._students.list_for_class(session.class_id)
        updated = await self._mark_unmarked(session, roster, status)
        return MarkRemainingOutput(
            message=f"Marked {updated} remaining student(s) as {status.label.lower()}.",
            updated=updated,
            summary=await self._live_summary(session, roster=roster),
        )

    async def _require_session(self, teacher_id: int, session_id: int) -> AttendanceSession:
        """Load an owned session that is still open.

        Raises:
            NoActiveAttendanceSessionError: If it does not exist or is not owned.
            AttendanceSessionClosedError: If it has already been closed.
        """
        session = await self._attendance.get_owned(session_id, teacher_id)
        if session is None:
            raise NoActiveAttendanceSessionError("That attendance session is no longer available.")
        if not session.is_open:
            raise AttendanceSessionClosedError("That attendance session has already been closed.")
        return session

    async def _apply_status(
        self,
        session: AttendanceSession,
        student: Student,
        status: AttendanceStatus,
        note: str | None,
    ) -> AttendanceRecord:
        """Insert or update the record for one student in a session.

        Raises:
            AttendanceSessionClosedError: If the session is not open.
        """
        if not session.is_open:
            raise AttendanceSessionClosedError(
                "That attendance session is closed. Reopen it to make changes."
            )

        record = await self._attendance.get_record(session.id, student.id)
        if record is None:
            return await self._attendance.add_record(
                AttendanceRecord(
                    session_id=session.id,
                    student_id=student.id,
                    status=status,
                    note=note,
                    marked_at=utc_now(),
                )
            )

        record.status = status
        record.marked_at = utc_now()
        if note is not None:
            record.note = note
        await self._attendance.flush()
        return record

    async def _mark_unmarked(
        self,
        session: AttendanceSession,
        roster: list[Student],
        status: AttendanceStatus,
    ) -> int:
        """Give ``status`` to every student in ``roster`` without a record.

        Returns:
            How many records were created.
        """
        existing = {record.student_id for record in await self._attendance.list_records(session.id)}
        missing = [student for student in roster if student.id not in existing]
        for student in missing:
            await self._attendance.add_record(
                AttendanceRecord(
                    session_id=session.id,
                    student_id=student.id,
                    status=status,
                    marked_at=utc_now(),
                )
            )
        return len(missing)

    async def _live_summary(
        self, session: AttendanceSession, *, roster: list[Student] | None = None
    ) -> AttendanceSummary:
        """Counts for an in-progress session, including unmarked students."""
        total = (
            len(roster)
            if roster is not None
            else len(await self._students.list_for_class(session.class_id))
        )
        counts = await self._attendance.status_counts_for_session(session.id)
        return AttendanceSummary.from_counts(counts, total)

    async def _class_name(self, session: AttendanceSession) -> str:
        """Return the class name for a session without relying on lazy loading."""
        classroom = await self._classes.get_by_id(session.class_id)
        return classroom.name if classroom is not None else "the class"


def _count_statuses(records: list[AttendanceRecord]) -> dict[AttendanceStatus, int]:
    """Tally attendance statuses across records."""
    counts: dict[AttendanceStatus, int] = {}
    for record in records:
        counts[record.status] = counts.get(record.status, 0) + 1
    return counts


def _names_with_status(records: list[AttendanceRecord], status: AttendanceStatus) -> list[str]:
    """Names of students holding a particular status, alphabetically."""
    return sorted(record.student.full_name for record in records if record.status is status)
