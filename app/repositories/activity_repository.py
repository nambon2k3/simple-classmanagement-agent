"""Recent-change queries built from the audit columns every table already has.

There is no separate event log: ``created_at``, ``updated_at`` and the
attendance/tuition lifecycle timestamps already record when each change
happened, so the feed is derived instead of duplicated.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select

from app.models.attendance import AttendanceSession
from app.models.classroom import Classroom
from app.models.enums import AttendanceSessionStatus, TuitionChargeStatus
from app.models.student import Student
from app.models.tuition import TuitionCharge
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Classroom]):
    """Read-only queries that feed the recent-activity list."""

    model = Classroom

    async def recent_classes(
        self, teacher_id: int, limit: int
    ) -> list[tuple[str, datetime, datetime]]:
        """``(name, created_at, updated_at)`` for the newest-touched classes."""
        result = await self.session.execute(
            select(Classroom.name, Classroom.created_at, Classroom.updated_at)
            .where(Classroom.teacher_id == teacher_id)
            .order_by(Classroom.updated_at.desc())
            .limit(limit)
        )
        return [(name, created, updated) for name, created, updated in result.all()]

    async def recent_students(
        self, teacher_id: int, limit: int
    ) -> list[tuple[str, str, str, datetime, datetime]]:
        """``(name, code, class_name, created_at, updated_at)`` for recent students."""
        result = await self.session.execute(
            select(
                Student.full_name,
                Student.student_code,
                Classroom.name,
                Student.created_at,
                Student.updated_at,
            )
            .join(Classroom, Student.class_id == Classroom.id)
            .where(Classroom.teacher_id == teacher_id)
            .order_by(Student.updated_at.desc())
            .limit(limit)
        )
        return [
            (name, code, class_name, created, updated)
            for name, code, class_name, created, updated in result.all()
        ]

    async def recent_sessions(
        self, teacher_id: int, limit: int
    ) -> list[tuple[str, AttendanceSessionStatus, datetime, datetime | None]]:
        """``(class_name, status, opened_at, closed_at)`` for recent roll-calls."""
        result = await self.session.execute(
            select(
                Classroom.name,
                AttendanceSession.status,
                AttendanceSession.opened_at,
                AttendanceSession.closed_at,
            )
            .join(Classroom, AttendanceSession.class_id == Classroom.id)
            .where(Classroom.teacher_id == teacher_id)
            .order_by(AttendanceSession.opened_at.desc())
            .limit(limit)
        )
        return [
            (name, AttendanceSessionStatus(status), opened, closed)
            for name, status, opened, closed in result.all()
        ]

    async def recent_payments(
        self, teacher_id: int, limit: int
    ) -> list[tuple[str, str, int, int, datetime]]:
        """``(student_name, class_name, days, amount_vnd, completed_at)`` per payment.

        Charges paid in the same action share one ``completed_at``, so grouping
        on it turns a batch of rows back into the single payment it was.
        """
        result = await self.session.execute(
            select(
                Student.full_name,
                Classroom.name,
                func.count(TuitionCharge.id),
                func.coalesce(func.sum(TuitionCharge.amount_vnd), 0),
                TuitionCharge.completed_at,
            )
            .join(Student, TuitionCharge.student_id == Student.id)
            .join(Classroom, Student.class_id == Classroom.id)
            .where(
                Classroom.teacher_id == teacher_id,
                TuitionCharge.status == TuitionChargeStatus.COMPLETED,
                TuitionCharge.completed_at.is_not(None),
            )
            .group_by(Student.id, Student.full_name, Classroom.name, TuitionCharge.completed_at)
            .order_by(TuitionCharge.completed_at.desc())
            .limit(limit)
        )
        return [
            (student, class_name, int(days), int(amount), completed_at)
            for student, class_name, days, amount, completed_at in result.all()
        ]
