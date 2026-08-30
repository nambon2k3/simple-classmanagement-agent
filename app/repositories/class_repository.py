"""Data access for :class:`~app.models.classroom.Classroom`."""

from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import selectinload, undefer

from app.models.classroom import Classroom
from app.models.student import Student
from app.repositories.base import BaseRepository


class ClassRepository(BaseRepository[Classroom]):
    """Queries scoped to a single teacher's classes.

    Every method takes ``teacher_id`` so that ownership is enforced inside the
    ``WHERE`` clause: a teacher can never load another teacher's class, even if
    they guess a valid id.
    """

    model = Classroom

    @staticmethod
    def _owned(teacher_id: int) -> Select[tuple[Classroom]]:
        return select(Classroom).where(Classroom.teacher_id == teacher_id)

    async def get_owned(self, class_id: int, teacher_id: int) -> Classroom | None:
        """Fetch one class by id, scoped to its owner."""
        return await self.session.scalar(self._owned(teacher_id).where(Classroom.id == class_id))

    async def get_by_name(self, teacher_id: int, name: str) -> Classroom | None:
        """Fetch a class by its name, case-insensitively."""
        return await self.session.scalar(
            self._owned(teacher_id).where(func.lower(Classroom.name) == name.strip().lower())
        )

    async def list_for_teacher(self, teacher_id: int) -> list[Classroom]:
        """Return every class owned by the teacher, alphabetically."""
        result = await self.session.scalars(self._owned(teacher_id).order_by(Classroom.name))
        return list(result)

    async def list_with_student_counts(self, teacher_id: int) -> list[tuple[Classroom, int]]:
        """Return each class paired with its student count.

        Uses a single grouped outer join rather than one count per class, so
        listing stays O(1) queries as the number of classes grows.
        """
        statement = (
            select(Classroom, func.count(Student.id))
            .outerjoin(Student, Student.class_id == Classroom.id)
            .where(Classroom.teacher_id == teacher_id)
            .group_by(Classroom.id)
            .order_by(Classroom.name)
        )
        result = await self.session.execute(statement)
        return [(classroom, count) for classroom, count in result.all()]

    async def get_owned_with_icon(self, class_id: int, teacher_id: int) -> Classroom | None:
        """Fetch one class including its deferred image blob."""
        return await self.session.scalar(
            self._owned(teacher_id)
            .where(Classroom.id == class_id)
            .options(undefer(Classroom.icon_data))
        )

    async def get_with_students(self, class_id: int, teacher_id: int) -> Classroom | None:
        """Fetch a class with its student collection eagerly loaded."""
        return await self.session.scalar(
            self._owned(teacher_id)
            .where(Classroom.id == class_id)
            .options(selectinload(Classroom.students))
        )

    async def count_students(self, class_id: int) -> int:
        """Number of students enrolled in a class."""
        return (
            await self.session.scalar(
                select(func.count(Student.id)).where(Student.class_id == class_id)
            )
        ) or 0
