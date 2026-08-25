"""Data access for persisted tuition charges."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from sqlalchemy import Select, func, select, update
from sqlalchemy.orm import selectinload

from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.classroom import Classroom
from app.models.enums import TuitionChargeStatus
from app.models.student import Student
from app.models.tuition import TuitionCharge
from app.repositories.base import BaseRepository


class TuitionChargeRepository(BaseRepository[TuitionCharge]):
    """Queries over billed attendance days."""

    model = TuitionCharge

    @staticmethod
    def _owned(teacher_id: int) -> Select[tuple[TuitionCharge]]:
        return (
            select(TuitionCharge)
            .join(Student, TuitionCharge.student_id == Student.id)
            .join(Classroom, Student.class_id == Classroom.id)
            .where(Classroom.teacher_id == teacher_id)
        )

    async def list_for_session(self, session_id: int) -> list[TuitionCharge]:
        """Every charge attached to one attendance session."""
        result = await self.session.scalars(
            select(TuitionCharge).where(TuitionCharge.session_id == session_id)
        )
        return list(result)

    async def list_for_class(self, class_id: int) -> list[TuitionCharge]:
        """Charges for students in one class, with student and session loaded."""
        result = await self.session.scalars(
            select(TuitionCharge)
            .join(AttendanceSession, TuitionCharge.session_id == AttendanceSession.id)
            .where(AttendanceSession.class_id == class_id)
            .options(
                selectinload(TuitionCharge.student),
                selectinload(TuitionCharge.session),
            )
        )
        return list(result)

    async def paid_through_per_student(self, class_id: int) -> dict[int, date]:
        """Latest session date each student has already paid for in this class.

        Used as the "last submitted tuition fee date": anything after it is
        still outstanding.
        """
        result = await self.session.execute(
            select(TuitionCharge.student_id, func.max(AttendanceSession.session_date))
            .join(AttendanceSession, TuitionCharge.session_id == AttendanceSession.id)
            .where(
                AttendanceSession.class_id == class_id,
                TuitionCharge.status == TuitionChargeStatus.COMPLETED,
            )
            .group_by(TuitionCharge.student_id)
        )
        return {student_id: day for student_id, day in result.all() if day is not None}

    async def unpaid_totals_per_student(self, class_id: int) -> dict[int, int]:
        """Outstanding VND per student for one class."""
        result = await self.session.execute(
            select(
                TuitionCharge.student_id,
                func.coalesce(func.sum(TuitionCharge.amount_vnd), 0),
            )
            .join(AttendanceSession, TuitionCharge.session_id == AttendanceSession.id)
            .where(
                AttendanceSession.class_id == class_id,
                TuitionCharge.status == TuitionChargeStatus.NOT_YET,
            )
            .group_by(TuitionCharge.student_id)
        )
        return {student_id: int(total) for student_id, total in result.all()}

    async def totals_for_teacher(self, teacher_id: int) -> tuple[int, int]:
        """Return ``(not_yet_vnd, completed_vnd)`` across every class."""
        statement = (
            select(TuitionCharge.status, func.coalesce(func.sum(TuitionCharge.amount_vnd), 0))
            .select_from(TuitionCharge)
            .join(Student, TuitionCharge.student_id == Student.id)
            .join(Classroom, Student.class_id == Classroom.id)
            .where(Classroom.teacher_id == teacher_id)
            .group_by(TuitionCharge.status)
        )
        result = await self.session.execute(statement)
        not_yet = 0
        completed = 0
        for status, total in result.all():
            amount = int(total)
            if status is TuitionChargeStatus.NOT_YET or status == TuitionChargeStatus.NOT_YET:
                not_yet = amount
            else:
                completed = amount
        return not_yet, completed

    async def update_not_yet_amounts(self, class_id: int, daily_fee: int) -> int:
        """Set the amount on unpaid charges for a class to the current daily fee.

        Returns:
            Number of rows updated.
        """
        session_ids = select(AttendanceSession.id).where(AttendanceSession.class_id == class_id)
        result = await self.session.execute(
            update(TuitionCharge)
            .where(
                TuitionCharge.session_id.in_(session_ids),
                TuitionCharge.status == TuitionChargeStatus.NOT_YET,
            )
            .values(amount_vnd=daily_fee)
        )
        await self.session.flush()
        return result.rowcount or 0

    async def complete_for_student(
        self, student_id: int, class_id: int, *, completed_at: datetime
    ) -> int:
        """Mark every unpaid charge for the student in this class as paid.

        Returns:
            Number of rows updated.
        """
        session_ids = select(AttendanceSession.id).where(AttendanceSession.class_id == class_id)
        result = await self.session.execute(
            update(TuitionCharge)
            .where(
                TuitionCharge.student_id == student_id,
                TuitionCharge.session_id.in_(session_ids),
                TuitionCharge.status == TuitionChargeStatus.NOT_YET,
            )
            .values(status=TuitionChargeStatus.COMPLETED, completed_at=completed_at)
        )
        await self.session.flush()
        return result.rowcount or 0

    async def sync_for_session(
        self,
        session_id: int,
        daily_fee: int,
        records: Sequence[AttendanceRecord],
    ) -> None:
        """Create or refresh charges after a session is finished.

        Completed (paid) rows are left alone.  Unpaid rows follow the current
        fee.  Students who are no longer billable lose their unpaid charge.
        """
        existing = {charge.student_id: charge for charge in await self.list_for_session(session_id)}
        billable_ids = {record.student_id for record in records if record.status.counts_as_attended}

        for student_id in billable_ids:
            charge = existing.get(student_id)
            if charge is None:
                await self.add(
                    TuitionCharge(
                        student_id=student_id,
                        session_id=session_id,
                        amount_vnd=daily_fee,
                        status=TuitionChargeStatus.NOT_YET,
                    )
                )
            elif charge.status is TuitionChargeStatus.NOT_YET:
                charge.amount_vnd = daily_fee

        for student_id, charge in existing.items():
            if student_id not in billable_ids and charge.status is TuitionChargeStatus.NOT_YET:
                await self.delete(charge)

        await self.flush()
