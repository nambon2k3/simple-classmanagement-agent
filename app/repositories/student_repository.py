"""Data access for :class:`~app.models.student.Student`."""

from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import selectinload

from app.models.classroom import Classroom
from app.models.student import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    """Queries scoped to the students inside a teacher's classes."""

    model = Student

    @staticmethod
    def _owned(teacher_id: int) -> Select[tuple[Student]]:
        """Base query joining through ``classes`` to enforce ownership."""
        return (
            select(Student)
            .join(Classroom, Student.class_id == Classroom.id)
            .where(Classroom.teacher_id == teacher_id)
        )

    async def get_owned(self, student_id: int, teacher_id: int) -> Student | None:
        """Fetch one student by id, scoped to the owning teacher."""
        return await self.session.scalar(self._owned(teacher_id).where(Student.id == student_id))

    async def get_with_class(self, student_id: int, teacher_id: int) -> Student | None:
        """Fetch a student together with their class."""
        return await self.session.scalar(
            self._owned(teacher_id)
            .where(Student.id == student_id)
            .options(selectinload(Student.classroom))
        )

    async def get_by_code_in_class(self, class_id: int, student_code: str) -> Student | None:
        """Fetch a student by their code within one class."""
        return await self.session.scalar(
            select(Student).where(
                Student.class_id == class_id,
                Student.student_code == student_code.strip().upper(),
            )
        )

    async def list_by_code_for_teacher(self, teacher_id: int, student_code: str) -> list[Student]:
        """Find every student with this code across all of a teacher's classes.

        Codes are only unique per class, so this can legitimately return more
        than one row; the service turns that into a disambiguation prompt.
        """
        result = await self.session.scalars(
            self._owned(teacher_id)
            .where(Student.student_code == student_code.strip().upper())
            .options(selectinload(Student.classroom))
        )
        return list(result)

    async def list_for_class(self, class_id: int) -> list[Student]:
        """Return the roster of a class ordered by name."""
        result = await self.session.scalars(
            select(Student).where(Student.class_id == class_id).order_by(Student.full_name)
        )
        return list(result)

    async def list_for_teacher(
        self, teacher_id: int, *, class_id: int | None = None
    ) -> list[Student]:
        """Return all students a teacher owns, optionally limited to one class.

        Used as the candidate pool for fuzzy name resolution, which happens in
        the service layer where the matching rules live.
        """
        statement = self._owned(teacher_id).options(selectinload(Student.classroom))
        if class_id is not None:
            statement = statement.where(Student.class_id == class_id)
        result = await self.session.scalars(statement.order_by(Student.full_name))
        return list(result)

    async def search_by_name(
        self, teacher_id: int, term: str, *, class_id: int | None = None
    ) -> list[Student]:
        """Case-insensitive substring search on name or code.

        Narrows the candidate set in the database before the service applies
        its finer-grained matching rules.
        """
        pattern = f"%{term.strip().lower()}%"
        statement = self._owned(teacher_id).where(
            func.lower(Student.full_name).like(pattern)
            | func.lower(Student.student_code).like(pattern)
        )
        if class_id is not None:
            statement = statement.where(Student.class_id == class_id)
        result = await self.session.scalars(
            statement.options(selectinload(Student.classroom)).order_by(Student.full_name)
        )
        return list(result)
