"""Data access for attendance sessions, records and report aggregates.

Aggregation is deliberately pushed into SQL: summing thousands of records in
Python would not survive a real school's data volume.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.orm import selectinload

from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.classroom import Classroom
from app.models.enums import AttendanceSessionStatus, AttendanceStatus
from app.models.student import Student
from app.repositories.base import BaseRepository

#: Attendance statuses that incur the daily tuition fee.
_BILLABLE_STATUSES = (
    AttendanceStatus.PRESENT,
    AttendanceStatus.LATE,
)


class AttendanceRepository(BaseRepository[AttendanceSession]):
    """Queries over attendance sessions and their records."""

    model = AttendanceSession

    # ------------------------------------------------------------ sessions --

    @staticmethod
    def _owned(teacher_id: int) -> Select[tuple[AttendanceSession]]:
        return (
            select(AttendanceSession)
            .join(Classroom, AttendanceSession.class_id == Classroom.id)
            .where(Classroom.teacher_id == teacher_id)
        )

    async def get_owned(self, session_id: int, teacher_id: int) -> AttendanceSession | None:
        """Fetch a session by id, scoped to the owning teacher."""
        return await self.session.scalar(
            self._owned(teacher_id).where(AttendanceSession.id == session_id)
        )

    async def get_with_records(self, session_id: int, teacher_id: int) -> AttendanceSession | None:
        """Fetch a session with its records, students and class eagerly loaded."""
        return await self.session.scalar(
            self._owned(teacher_id)
            .where(AttendanceSession.id == session_id)
            .options(
                selectinload(AttendanceSession.records).selectinload(AttendanceRecord.student),
                selectinload(AttendanceSession.classroom),
            )
        )

    async def get_for_class_on_date(
        self, class_id: int, session_date: date
    ) -> AttendanceSession | None:
        """Fetch the (at most one) session for a class on a given day."""
        return await self.session.scalar(
            select(AttendanceSession).where(
                AttendanceSession.class_id == class_id,
                AttendanceSession.session_date == session_date,
            )
        )

    async def get_open_for_class(self, class_id: int) -> AttendanceSession | None:
        """Fetch the currently open session for a class, if any."""
        return await self.session.scalar(
            select(AttendanceSession)
            .where(
                AttendanceSession.class_id == class_id,
                AttendanceSession.status == AttendanceSessionStatus.OPEN,
            )
            .order_by(AttendanceSession.session_date.desc())
        )

    async def list_open_for_teacher(self, teacher_id: int) -> list[AttendanceSession]:
        """Every open session belonging to a teacher, newest first."""
        result = await self.session.scalars(
            self._owned(teacher_id)
            .where(AttendanceSession.status == AttendanceSessionStatus.OPEN)
            .options(selectinload(AttendanceSession.classroom))
            .order_by(AttendanceSession.session_date.desc())
        )
        return list(result)

    async def list_for_class(
        self, class_id: int, start: date, end: date
    ) -> list[AttendanceSession]:
        """Sessions for a class within an inclusive date range, oldest first."""
        result = await self.session.scalars(
            select(AttendanceSession)
            .where(
                AttendanceSession.class_id == class_id,
                AttendanceSession.session_date >= start,
                AttendanceSession.session_date <= end,
            )
            .order_by(AttendanceSession.session_date)
        )
        return list(result)

    async def list_session_dates_for_class(
        self, class_id: int, *, since: date | None = None
    ) -> list[date]:
        """Dates a class actually met, oldest first, ignoring cancelled days."""
        statement = select(AttendanceSession.session_date).where(
            AttendanceSession.class_id == class_id,
            AttendanceSession.status != AttendanceSessionStatus.CANCELLED,
        )
        if since is not None:
            statement = statement.where(AttendanceSession.session_date > since)
        result = await self.session.scalars(statement.order_by(AttendanceSession.session_date))
        return list(result)

    async def list_marks_for_class(
        self, class_id: int, *, since: date | None = None
    ) -> list[tuple[int, date, AttendanceStatus]]:
        """Every ``(student_id, date, status)`` mark for a class, oldest first."""
        statement = (
            select(
                AttendanceRecord.student_id,
                AttendanceSession.session_date,
                AttendanceRecord.status,
            )
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .where(
                AttendanceSession.class_id == class_id,
                AttendanceSession.status != AttendanceSessionStatus.CANCELLED,
            )
        )
        if since is not None:
            statement = statement.where(AttendanceSession.session_date > since)
        result = await self.session.execute(statement.order_by(AttendanceSession.session_date))
        return [
            (student_id, day, AttendanceStatus(status)) for student_id, day, status in result.all()
        ]

    async def count_for_class(self, class_id: int) -> int:
        """Total number of attendance sessions ever held for a class."""
        return (
            await self.session.scalar(
                select(func.count(AttendanceSession.id)).where(
                    AttendanceSession.class_id == class_id
                )
            )
        ) or 0

    async def latest_session_date(self, class_id: int) -> date | None:
        """Date of the most recent session for a class, or ``None`` if none."""
        return await self.session.scalar(
            select(func.max(AttendanceSession.session_date)).where(
                AttendanceSession.class_id == class_id
            )
        )

    async def list_for_teacher_on_date(
        self, teacher_id: int, session_date: date
    ) -> list[AttendanceSession]:
        """Every session a teacher held on one day, with class preloaded."""
        result = await self.session.scalars(
            self._owned(teacher_id)
            .where(AttendanceSession.session_date == session_date)
            .options(selectinload(AttendanceSession.classroom))
            .order_by(Classroom.name)
        )
        return list(result)

    async def list_completed_days_in_range(
        self, teacher_id: int, start: date, end: date
    ) -> list[tuple[int, date, str | None]]:
        """``(class_id, date, note)`` for finalised teaching days in ``start``..``end``."""
        result = await self.session.execute(
            select(
                AttendanceSession.class_id,
                AttendanceSession.session_date,
                AttendanceSession.note,
            )
            .join(Classroom, AttendanceSession.class_id == Classroom.id)
            .where(
                Classroom.teacher_id == teacher_id,
                AttendanceSession.status == AttendanceSessionStatus.COMPLETED,
                AttendanceSession.session_date >= start,
                AttendanceSession.session_date <= end,
            )
        )
        return [(class_id, day, note) for class_id, day, note in result.all()]

    # ------------------------------------------------------------- records --

    async def get_record(self, session_id: int, student_id: int) -> AttendanceRecord | None:
        """Fetch one student's record within a session."""
        return await self.session.scalar(
            select(AttendanceRecord).where(
                AttendanceRecord.session_id == session_id,
                AttendanceRecord.student_id == student_id,
            )
        )

    async def list_records(self, session_id: int) -> list[AttendanceRecord]:
        """Every record in a session, with students preloaded, ordered by name."""
        result = await self.session.scalars(
            select(AttendanceRecord)
            .join(Student, AttendanceRecord.student_id == Student.id)
            .where(AttendanceRecord.session_id == session_id)
            .options(selectinload(AttendanceRecord.student))
            .order_by(Student.full_name)
        )
        return list(result)

    async def add_record(self, record: AttendanceRecord) -> AttendanceRecord:
        """Persist a new attendance record."""
        self.session.add(record)
        await self.session.flush()
        return record

    # ---------------------------------------------------------- aggregates --

    async def status_counts_for_session(self, session_id: int) -> dict[AttendanceStatus, int]:
        """Count records per status within a single session."""
        result = await self.session.execute(
            select(AttendanceRecord.status, func.count(AttendanceRecord.id))
            .where(AttendanceRecord.session_id == session_id)
            .group_by(AttendanceRecord.status)
        )
        return {AttendanceStatus(status): count for status, count in result.all()}

    async def status_counts_for_class(
        self, class_id: int, start: date, end: date
    ) -> dict[AttendanceStatus, int]:
        """Count records per status for a class over a date range."""
        result = await self.session.execute(
            select(AttendanceRecord.status, func.count(AttendanceRecord.id))
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .where(
                AttendanceSession.class_id == class_id,
                AttendanceSession.session_date >= start,
                AttendanceSession.session_date <= end,
            )
            .group_by(AttendanceRecord.status)
        )
        return {AttendanceStatus(status): count for status, count in result.all()}

    async def status_counts_for_student(
        self, student_id: int, start: date, end: date
    ) -> dict[AttendanceStatus, int]:
        """Count records per status for one student over a date range."""
        result = await self.session.execute(
            select(AttendanceRecord.status, func.count(AttendanceRecord.id))
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .where(
                AttendanceRecord.student_id == student_id,
                AttendanceSession.session_date >= start,
                AttendanceSession.session_date <= end,
            )
            .group_by(AttendanceRecord.status)
        )
        return {AttendanceStatus(status): count for status, count in result.all()}

    async def list_student_history(
        self, student_id: int, start: date, end: date
    ) -> list[tuple[date, AttendanceStatus]]:
        """A student's day-by-day statuses over a range, oldest first."""
        result = await self.session.execute(
            select(AttendanceSession.session_date, AttendanceRecord.status)
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .where(
                AttendanceRecord.student_id == student_id,
                AttendanceSession.session_date >= start,
                AttendanceSession.session_date <= end,
            )
            .order_by(AttendanceSession.session_date)
        )
        return [(day, AttendanceStatus(status)) for day, status in result.all()]

    async def per_student_status_counts(
        self, class_id: int, start: date, end: date
    ) -> list[tuple[Student, AttendanceStatus, int]]:
        """Per-student, per-status counts for a class over a range.

        Powers the monthly summary: one query returns the whole matrix instead
        of a query per student.
        """
        result = await self.session.execute(
            select(Student, AttendanceRecord.status, func.count(AttendanceRecord.id))
            .join(AttendanceRecord, AttendanceRecord.student_id == Student.id)
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .where(
                AttendanceSession.class_id == class_id,
                AttendanceSession.session_date >= start,
                AttendanceSession.session_date <= end,
            )
            .group_by(Student.id, AttendanceRecord.status)
            .order_by(Student.full_name)
        )
        return [
            (student, AttendanceStatus(status), count) for student, status, count in result.all()
        ]

    async def list_records_with_status(
        self,
        teacher_id: int,
        statuses: list[AttendanceStatus],
        start: date,
        end: date,
        *,
        class_id: int | None = None,
    ) -> list[tuple[AttendanceRecord, Student, Classroom, date]]:
        """Records matching any of ``statuses`` in a range.

        Answers questions such as "who was absent today?" and "how many
        students were absent this week?" in one round trip.
        """
        statement = (
            select(AttendanceRecord, Student, Classroom, AttendanceSession.session_date)
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .join(Classroom, AttendanceSession.class_id == Classroom.id)
            .join(Student, AttendanceRecord.student_id == Student.id)
            .where(
                Classroom.teacher_id == teacher_id,
                AttendanceRecord.status.in_(statuses),
                AttendanceSession.session_date >= start,
                AttendanceSession.session_date <= end,
            )
        )
        if class_id is not None:
            statement = statement.where(AttendanceSession.class_id == class_id)
        result = await self.session.execute(
            statement.order_by(AttendanceSession.session_date, Classroom.name, Student.full_name)
        )
        return [
            (record, student, classroom, day) for record, student, classroom, day in result.all()
        ]

    # ----------------------------------------------------------- tuition --

    async def billable_days_per_student(
        self, class_id: int, start: date, end: date
    ) -> list[tuple[Student, int]]:
        """Count attended days per student from completed sessions in a range."""
        result = await self.session.execute(
            select(Student, func.count(AttendanceRecord.id))
            .join(AttendanceRecord, AttendanceRecord.student_id == Student.id)
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .where(
                Student.class_id == class_id,
                AttendanceSession.class_id == class_id,
                AttendanceSession.status == AttendanceSessionStatus.COMPLETED,
                AttendanceSession.session_date >= start,
                AttendanceSession.session_date <= end,
                AttendanceRecord.status.in_(_BILLABLE_STATUSES),
            )
            .group_by(Student.id)
            .order_by(Student.full_name)
        )
        return [(student, count) for student, count in result.all()]

    async def count_teaching_days_for_class(self, class_id: int, start: date, end: date) -> int:
        """Number of completed attendance sessions for one class in a range."""
        return (
            await self.session.scalar(
                select(func.count(AttendanceSession.id)).where(
                    AttendanceSession.class_id == class_id,
                    AttendanceSession.status == AttendanceSessionStatus.COMPLETED,
                    AttendanceSession.session_date >= start,
                    AttendanceSession.session_date <= end,
                )
            )
        ) or 0

    async def count_teaching_days_for_teacher(self, teacher_id: int, start: date, end: date) -> int:
        """Distinct calendar days with a completed session across all classes."""
        return (
            await self.session.scalar(
                select(func.count(func.distinct(AttendanceSession.session_date)))
                .join(Classroom, AttendanceSession.class_id == Classroom.id)
                .where(
                    Classroom.teacher_id == teacher_id,
                    AttendanceSession.status == AttendanceSessionStatus.COMPLETED,
                    AttendanceSession.session_date >= start,
                    AttendanceSession.session_date <= end,
                )
            )
        ) or 0

    async def teaching_days_per_class(
        self, teacher_id: int, start: date, end: date
    ) -> list[tuple[str, int]]:
        """Completed session counts grouped by class name."""
        result = await self.session.execute(
            select(Classroom.name, func.count(AttendanceSession.id))
            .join(AttendanceSession, AttendanceSession.class_id == Classroom.id)
            .where(
                Classroom.teacher_id == teacher_id,
                AttendanceSession.status == AttendanceSessionStatus.COMPLETED,
                AttendanceSession.session_date >= start,
                AttendanceSession.session_date <= end,
            )
            .group_by(Classroom.id)
            .order_by(Classroom.name)
        )
        return [(name, count) for name, count in result.all()]
