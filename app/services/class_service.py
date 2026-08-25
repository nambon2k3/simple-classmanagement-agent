"""Class management business logic."""

from __future__ import annotations

from app.core.exceptions import (
    ClassAlreadyExistsError,
    ClassNotFoundError,
    ConfirmationRequiredError,
)
from app.core.logging import get_logger
from app.models.classroom import Classroom
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.tuition_charge_repository import TuitionChargeRepository
from app.schemas.classroom import (
    ClassInfoInput,
    ClassInfoOutput,
    ClassRead,
    CreateClassInput,
    CreateClassOutput,
    DeleteClassInput,
    DeleteClassOutput,
    ListClassesOutput,
    RenameClassInput,
    RenameClassOutput,
)
from app.schemas.tuition import SetClassTuitionFeeInput, SetClassTuitionFeeOutput
from app.utils.money import format_vnd

logger = get_logger(__name__)


class ClassService:
    """Create, rename, delete and inspect a teacher's classes.

    Also owns :meth:`resolve` — the single place that turns a class name into a
    class entity — so that student and attendance logic never re-implement
    lookup or ownership checks.
    """

    def __init__(
        self,
        class_repository: ClassRepository,
        attendance_repository: AttendanceRepository,
        tuition_charge_repository: TuitionChargeRepository,
    ) -> None:
        """Wire the service to its data sources.

        Args:
            class_repository: Access to the ``classes`` table.
            attendance_repository: Used to enrich class info with session data.
            tuition_charge_repository: Recalculates unpaid charges when the fee changes.
        """
        self._classes = class_repository
        self._attendance = attendance_repository
        self._charges = tuition_charge_repository

    # ----------------------------------------------------------- resolution --

    async def get_by_id(self, class_id: int) -> Classroom | None:
        """Fetch a class by primary key without an ownership check.

        Only for call sites that have *already* verified ownership by another
        route, such as resolving the class of an attendance session that was
        itself loaded through an owner-scoped query.
        """
        return await self._classes.get(class_id)

    async def resolve(self, teacher_id: int, name: str) -> Classroom:
        """Look up one of the teacher's classes by name.

        Args:
            teacher_id: Owner of the class.
            name: Class name, matched case-insensitively.

        Returns:
            The matching class.

        Raises:
            ClassNotFoundError: When the teacher has no class with that name.
                The error lists the available names so the assistant can
                suggest alternatives.
        """
        classroom = await self._classes.get_by_name(teacher_id, name)
        if classroom is None:
            available = [item.name for item in await self._classes.list_for_teacher(teacher_id)]
            raise ClassNotFoundError(
                f"You don't have a class called '{name}'.",
                requested=name,
                available_classes=available,
            )
        return classroom

    # --------------------------------------------------------------- create --

    async def create_class(self, teacher_id: int, payload: CreateClassInput) -> CreateClassOutput:
        """Create a new class for the teacher.

        Raises:
            ClassAlreadyExistsError: If a class with that name already exists.
        """
        existing = await self._classes.get_by_name(teacher_id, payload.name)
        if existing is not None:
            raise ClassAlreadyExistsError(
                f"You already have a class called '{existing.name}'.",
                existing_class=existing.name,
            )

        classroom = await self._classes.add(
            Classroom(
                teacher_id=teacher_id,
                name=payload.name,
                description=payload.description,
                daily_tuition_fee=payload.daily_tuition_fee,
            )
        )
        logger.info("Class created", extra={"teacher_id": teacher_id, "class_id": classroom.id})
        return CreateClassOutput(
            message=f"Class '{classroom.name}' created.",
            classroom=_class_read(classroom, student_count=0),
        )

    # --------------------------------------------------------------- rename --

    async def rename_class(self, teacher_id: int, payload: RenameClassInput) -> RenameClassOutput:
        """Rename an existing class.

        Raises:
            ClassNotFoundError: If the current name does not match a class.
            ClassAlreadyExistsError: If the new name is taken by another class.
        """
        classroom = await self.resolve(teacher_id, payload.current_name)

        clash = await self._classes.get_by_name(teacher_id, payload.new_name)
        if clash is not None and clash.id != classroom.id:
            raise ClassAlreadyExistsError(
                f"You already have a class called '{clash.name}'.",
                existing_class=clash.name,
            )

        previous_name = classroom.name
        classroom.name = payload.new_name
        await self._classes.flush()

        student_count = await self._classes.count_students(classroom.id)
        logger.info(
            "Class renamed",
            extra={"teacher_id": teacher_id, "class_id": classroom.id, "from": previous_name},
        )
        return RenameClassOutput(
            message=f"Renamed '{previous_name}' to '{classroom.name}'.",
            classroom=_class_read(classroom, student_count=student_count),
        )

    # --------------------------------------------------------------- delete --

    async def delete_class(self, teacher_id: int, payload: DeleteClassInput) -> DeleteClassOutput:
        """Delete a class along with its students and attendance history.

        Raises:
            ClassNotFoundError: If no class matches the name.
            ConfirmationRequiredError: If ``confirm`` was not set, so the
                assistant asks the teacher first.
        """
        classroom = await self.resolve(teacher_id, payload.name)
        student_count = await self._classes.count_students(classroom.id)

        if not payload.confirm:
            raise ConfirmationRequiredError(
                f"Deleting '{classroom.name}' will also remove {student_count} "
                "student(s) and all attendance history. Please confirm.",
                class_name=classroom.name,
                student_count=student_count,
            )

        name = classroom.name
        await self._classes.delete(classroom)
        logger.info("Class deleted", extra={"teacher_id": teacher_id, "class_name": name})
        return DeleteClassOutput(
            message=f"Class '{name}' and its {student_count} student(s) were deleted.",
            deleted_class=name,
            deleted_students=student_count,
        )

    # ----------------------------------------------------------------- read --

    async def list_classes(self, teacher_id: int) -> ListClassesOutput:
        """List every class the teacher owns, with student counts."""
        rows = await self._classes.list_with_student_counts(teacher_id)
        classes = [_class_read(classroom, student_count=count) for classroom, count in rows]
        return ListClassesOutput(classes=classes, total=len(classes))

    async def get_class_info(self, teacher_id: int, payload: ClassInfoInput) -> ClassInfoOutput:
        """Describe one class, including its attendance activity."""
        classroom = await self.resolve(teacher_id, payload.name)
        student_count = await self._classes.count_students(classroom.id)

        total_sessions = await self._attendance.count_for_class(classroom.id)
        last_date = await self._attendance.latest_session_date(classroom.id)
        open_session = await self._attendance.get_open_for_class(classroom.id)

        return ClassInfoOutput(
            classroom=_class_read(classroom, student_count=student_count),
            total_sessions=total_sessions,
            last_session_date=last_date.isoformat() if last_date else None,
            has_open_session=open_session is not None,
            daily_tuition_fee=classroom.daily_tuition_fee,
            formatted_daily_tuition_fee=format_vnd(classroom.daily_tuition_fee),
        )

    async def set_class_tuition_fee(
        self, teacher_id: int, payload: SetClassTuitionFeeInput
    ) -> SetClassTuitionFeeOutput:
        """Set the daily tuition fee charged per attended day for every student."""
        classroom = await self.resolve(teacher_id, payload.class_name)
        classroom.daily_tuition_fee = payload.daily_tuition_fee
        await self._classes.flush()
        await self._charges.update_not_yet_amounts(classroom.id, payload.daily_tuition_fee)
        logger.info(
            "Class tuition fee updated",
            extra={
                "teacher_id": teacher_id,
                "class_id": classroom.id,
                "daily_tuition_fee": payload.daily_tuition_fee,
            },
        )
        return SetClassTuitionFeeOutput(
            class_name=classroom.name,
            daily_tuition_fee=classroom.daily_tuition_fee,
            formatted_fee=format_vnd(classroom.daily_tuition_fee),
            message=(
                f"Daily tuition for '{classroom.name}' is now "
                f"{format_vnd(classroom.daily_tuition_fee)} per attended day."
            ),
        )

    async def set_class_description(
        self, teacher_id: int, class_id: int, description: str | None
    ) -> Classroom:
        """Update the free-text description of an owned class."""
        classroom = await self._classes.get_owned(class_id, teacher_id)
        if classroom is None:
            raise ClassNotFoundError("I couldn't find that class.")
        classroom.description = description
        await self._classes.flush()
        return classroom


def _class_read(classroom: Classroom, *, student_count: int) -> ClassRead:
    """Project a classroom ORM row onto the teacher-facing read model."""
    return ClassRead(
        id=classroom.id,
        name=classroom.name,
        description=classroom.description,
        student_count=student_count,
        daily_tuition_fee=classroom.daily_tuition_fee,
    )
