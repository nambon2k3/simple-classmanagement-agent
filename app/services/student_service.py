"""Student management business logic."""

from __future__ import annotations

from app.core.exceptions import (
    AmbiguousStudentError,
    ConfirmationRequiredError,
    DuplicateStudentError,
    StudentNotFoundError,
)
from app.core.logging import get_logger
from app.models.classroom import Classroom
from app.models.student import Student
from app.repositories.student_repository import StudentRepository
from app.schemas.student import (
    AddStudentInput,
    AddStudentOutput,
    ImportStudentsInput,
    ImportStudentsOutput,
    ListStudentsInput,
    ListStudentsOutput,
    RemoveStudentInput,
    RemoveStudentOutput,
    SearchStudentInput,
    SearchStudentOutput,
    StudentRead,
    UpdateStudentInput,
    UpdateStudentOutput,
)
from app.services.class_service import ClassService
from app.utils.text import find_matches, normalize_code

logger = get_logger(__name__)

#: How many names to include in a disambiguation or "not found" hint.
_MAX_HINT_CANDIDATES = 10


class StudentService:
    """Enrol, update, remove and find students.

    :meth:`resolve` is the shared entry point for turning the loose references
    teachers use ("John", "SE001", "nguyen van a") into exactly one student.
    Every other service calls it instead of matching names itself.
    """

    def __init__(
        self,
        student_repository: StudentRepository,
        class_service: ClassService,
    ) -> None:
        """Wire the service to its collaborators.

        Args:
            student_repository: Access to the ``students`` table.
            class_service: Used to resolve class names and enforce ownership.
        """
        self._students = student_repository
        self._classes = class_service

    # ----------------------------------------------------------- resolution --

    async def resolve(
        self,
        teacher_id: int,
        reference: str,
        *,
        class_id: int | None = None,
    ) -> Student:
        """Resolve a human reference to exactly one student.

        Candidates are narrowed in the database before any fuzzy matching so
        that a large roster does not have to be loaded into memory for the
        common case.

        Args:
            teacher_id: Owner of the data.
            reference: Student ID, full name or partial name.
            class_id: Restrict the search to a single class.

        Returns:
            The single matching student, with ``classroom`` loaded.

        Raises:
            StudentNotFoundError: When nothing matches closely enough.
            AmbiguousStudentError: When several students match; the error
                carries the candidates so the assistant can ask which one.
        """
        candidates = await self._gather_candidates(teacher_id, reference, class_id=class_id)

        if not candidates:
            raise StudentNotFoundError(
                f"I couldn't find a student matching '{reference}'.",
                reference=reference,
            )
        if len(candidates) > 1:
            raise AmbiguousStudentError(
                f"'{reference}' matches {len(candidates)} students. Which one did you mean?",
                reference=reference,
                candidates=[
                    f"{student.full_name} ({student.student_code}) in {student.classroom.name}"
                    for student in candidates[:_MAX_HINT_CANDIDATES]
                ],
            )
        return candidates[0]

    async def _gather_candidates(
        self, teacher_id: int, reference: str, *, class_id: int | None
    ) -> list[Student]:
        """Return every student plausibly referred to by ``reference``."""
        by_code = await self._students.list_by_code_for_teacher(
            teacher_id, normalize_code(reference)
        )
        if class_id is not None:
            by_code = [student for student in by_code if student.class_id == class_id]
        if by_code:
            return by_code

        narrowed = await self._students.search_by_name(teacher_id, reference, class_id=class_id)
        if narrowed:
            ranked = find_matches(reference, narrowed, key=lambda student: student.full_name)
            return ranked or narrowed

        pool = await self._students.list_for_teacher(teacher_id, class_id=class_id)
        return find_matches(reference, pool, key=lambda student: student.full_name)

    # ------------------------------------------------------------------ add --

    async def add_student(self, teacher_id: int, payload: AddStudentInput) -> AddStudentOutput:
        """Enrol a new student into a class.

        Raises:
            ClassNotFoundError: If the target class does not exist.
            DuplicateStudentError: If the student ID is taken within that class.
        """
        classroom = await self._classes.resolve(teacher_id, payload.class_name)
        code = normalize_code(payload.student_code)

        existing = await self._students.get_by_code_in_class(classroom.id, code)
        if existing is not None:
            raise DuplicateStudentError(
                f"{classroom.name} already has a student with ID {code} ({existing.full_name}).",
                student_code=code,
                class_name=classroom.name,
                existing_student=existing.full_name,
            )

        student = await self._students.add(
            Student(
                class_id=classroom.id,
                student_code=code,
                full_name=payload.full_name,
                email=payload.email,
                phone=payload.phone,
                note=payload.note,
            )
        )
        logger.info(
            "Student added",
            extra={"teacher_id": teacher_id, "class_id": classroom.id, "student_id": student.id},
        )
        return AddStudentOutput(
            message=f"Added {student.full_name} ({code}) to {classroom.name}.",
            student=self._to_read(student, classroom.name),
        )

    async def import_students(
        self, teacher_id: int, payload: ImportStudentsInput
    ) -> ImportStudentsOutput:
        """Enrol a whole roster, skipping rows that clash instead of failing.

        A spreadsheet almost always contains a few duplicates, so one bad row
        must not discard the rest of the import.

        Raises:
            ClassNotFoundError: If the target class does not exist.
        """
        classroom = await self._classes.resolve(teacher_id, payload.class_name)
        added: list[StudentRead] = []
        skipped: list[str] = []
        seen: set[str] = set()

        for row in payload.students:
            code = normalize_code(row.student_code)
            if code in seen:
                skipped.append(f"{row.full_name} ({code}): repeated in the file.")
                continue
            seen.add(code)

            existing = await self._students.get_by_code_in_class(classroom.id, code)
            if existing is not None:
                skipped.append(
                    f"{row.full_name} ({code}): ID already used by {existing.full_name}."
                )
                continue

            student = await self._students.add(
                Student(
                    class_id=classroom.id,
                    student_code=code,
                    full_name=row.full_name,
                    email=row.email,
                    phone=row.phone,
                    note=row.note,
                )
            )
            added.append(self._to_read(student, classroom.name))

        logger.info(
            "Roster imported",
            extra={
                "teacher_id": teacher_id,
                "class_id": classroom.id,
                "added": len(added),
                "skipped": len(skipped),
            },
        )
        return ImportStudentsOutput(
            message=f"Added {len(added)} student(s) to {classroom.name}.",
            class_name=classroom.name,
            added=len(added),
            students=added,
            skipped=skipped,
        )

    # --------------------------------------------------------------- remove --

    async def remove_student(
        self, teacher_id: int, payload: RemoveStudentInput
    ) -> RemoveStudentOutput:
        """Remove a student and their attendance history.

        Raises:
            ConfirmationRequiredError: If ``confirm`` was not set.
        """
        class_id = await self._optional_class_id(teacher_id, payload.class_name)
        student = await self.resolve(teacher_id, payload.student, class_id=class_id)
        label = student.display_label
        class_name = student.classroom.name

        if not payload.confirm:
            raise ConfirmationRequiredError(
                f"Removing {label} from {class_name} also deletes their attendance "
                "history. Please confirm.",
                student=label,
                class_name=class_name,
            )

        await self._students.delete(student)
        logger.info("Student removed", extra={"teacher_id": teacher_id, "student": label})
        return RemoveStudentOutput(
            message=f"Removed {label} from {class_name}.",
            removed_student=label,
        )

    # --------------------------------------------------------------- update --

    async def update_student(
        self, teacher_id: int, payload: UpdateStudentInput
    ) -> UpdateStudentOutput:
        """Update a student's details, changing only the fields supplied.

        Raises:
            DuplicateStudentError: If the new student ID clashes inside the class.
            ValidationError: If no changes were requested.
        """
        class_id = await self._optional_class_id(teacher_id, payload.class_name)
        student = await self.resolve(teacher_id, payload.student, class_id=class_id)

        changes: list[str] = []

        if payload.new_student_code:
            new_code = normalize_code(payload.new_student_code)
            if new_code != student.student_code:
                clash = await self._students.get_by_code_in_class(student.class_id, new_code)
                if clash is not None:
                    raise DuplicateStudentError(
                        f"{student.classroom.name} already has a student with ID {new_code}.",
                        student_code=new_code,
                    )
                student.student_code = new_code
                changes.append(f"ID → {new_code}")

        for attribute, value, label in (
            ("full_name", payload.new_full_name, "name"),
            ("email", payload.email, "email"),
            ("phone", payload.phone, "phone"),
            ("note", payload.note, "note"),
        ):
            if value is not None and getattr(student, attribute) != value:
                setattr(student, attribute, value)
                changes.append(f"{label} → {value}")

        if not changes:
            return UpdateStudentOutput(
                message=f"Nothing to change for {student.display_label}.",
                student=self._to_read(student, student.classroom.name),
            )

        await self._students.flush()
        logger.info("Student updated", extra={"teacher_id": teacher_id, "student_id": student.id})
        return UpdateStudentOutput(
            message=f"Updated {student.full_name}: {', '.join(changes)}.",
            student=self._to_read(student, student.classroom.name),
        )

    # ----------------------------------------------------------------- read --

    async def list_students(
        self, teacher_id: int, payload: ListStudentsInput
    ) -> ListStudentsOutput:
        """List the roster of one class."""
        classroom = await self._classes.resolve(teacher_id, payload.class_name)
        students = await self._students.list_for_class(classroom.id)
        return ListStudentsOutput(
            class_name=classroom.name,
            students=[self._to_read(student, classroom.name) for student in students],
            total=len(students),
        )

    async def search_student(
        self, teacher_id: int, payload: SearchStudentInput
    ) -> SearchStudentOutput:
        """Find students matching a name fragment or ID.

        Unlike :meth:`resolve`, several matches are a valid result here rather
        than an error.
        """
        class_id = await self._optional_class_id(teacher_id, payload.class_name)
        matches = await self._gather_candidates(teacher_id, payload.query, class_id=class_id)
        return SearchStudentOutput(
            query=payload.query,
            students=[self._to_read(student, student.classroom.name) for student in matches],
            total=len(matches),
        )

    # ------------------------------------------------------------- internals --

    async def _optional_class_id(self, teacher_id: int, class_name: str | None) -> int | None:
        """Resolve an optional class name to an id, keeping ``None`` as-is."""
        if not class_name:
            return None
        classroom: Classroom = await self._classes.resolve(teacher_id, class_name)
        return classroom.id

    @staticmethod
    def _to_read(student: Student, class_name: str | None) -> StudentRead:
        """Project a student entity onto its output schema."""
        return StudentRead(
            id=student.id,
            student_code=student.student_code,
            full_name=student.full_name,
            class_name=class_name,
            email=student.email,
            phone=student.phone,
            note=student.note,
        )
