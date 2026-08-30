"""Class management behaviour against a real database."""

from __future__ import annotations

import pytest

from app.core.exceptions import (
    ClassAlreadyExistsError,
    ClassNotFoundError,
    ConfirmationRequiredError,
)
from app.schemas.classroom import (
    ClassInfoInput,
    CreateClassInput,
    DeleteClassInput,
    RenameClassInput,
)


async def test_create_class(services, teacher):
    result = await services.classes.create_class(
        teacher.id, CreateClassInput(name="SE401", description="Software Engineering")
    )
    assert result.success
    assert result.classroom.name == "SE401"
    assert result.classroom.student_count == 0


async def test_duplicate_class_name_is_rejected(services, teacher, classroom):
    with pytest.raises(ClassAlreadyExistsError) as error:
        await services.classes.create_class(teacher.id, CreateClassInput(name="SE401"))
    assert error.value.details["existing_class"] == "SE401"


async def test_class_names_collide_case_insensitively(services, teacher, classroom):
    with pytest.raises(ClassAlreadyExistsError):
        await services.classes.create_class(teacher.id, CreateClassInput(name="se401"))


async def test_two_teachers_may_use_the_same_class_name(services, teacher, classroom):
    from app.schemas.teacher import TeacherIdentity

    other = await services.teachers.get_or_create(
        TeacherIdentity(telegram_id=777, full_name="Other Teacher")
    )
    result = await services.classes.create_class(other.id, CreateClassInput(name="SE401"))
    assert result.classroom.name == "SE401"


async def test_list_classes_includes_student_counts(services, teacher, classroom, roster):
    result = await services.classes.list_classes(teacher.id)
    assert result.total == 1
    assert result.classes[0].student_count == len(roster)


async def test_rename_class(services, teacher, classroom):
    result = await services.classes.rename_class(
        teacher.id, RenameClassInput(current_name="SE401", new_name="SE402")
    )
    assert result.classroom.name == "SE402"
    assert (await services.classes.list_classes(teacher.id)).classes[0].name == "SE402"


async def test_rename_onto_an_existing_name_is_rejected(services, teacher, classroom):
    await services.classes.create_class(teacher.id, CreateClassInput(name="AI202"))
    with pytest.raises(ClassAlreadyExistsError):
        await services.classes.rename_class(
            teacher.id, RenameClassInput(current_name="SE401", new_name="AI202")
        )


async def test_unknown_class_lists_the_available_ones(services, teacher, classroom):
    with pytest.raises(ClassNotFoundError) as error:
        await services.classes.resolve(teacher.id, "NOPE")
    assert error.value.details["available_classes"] == ["SE401"]


async def test_delete_requires_confirmation_first(services, teacher, classroom, roster):
    with pytest.raises(ConfirmationRequiredError) as error:
        await services.classes.delete_class(teacher.id, DeleteClassInput(name="SE401"))
    assert error.value.details["student_count"] == len(roster)

    # The class is still there.
    assert (await services.classes.list_classes(teacher.id)).total == 1


async def test_delete_removes_the_class_and_its_students(services, teacher, classroom, roster):
    result = await services.classes.delete_class(
        teacher.id, DeleteClassInput(name="SE401", confirm=True)
    )
    assert result.deleted_students == len(roster)
    assert (await services.classes.list_classes(teacher.id)).total == 0

    remaining = await services.student_repository.list_for_teacher(teacher.id)
    assert remaining == []


async def test_a_teacher_cannot_reach_another_teachers_class(services, teacher, classroom):
    from app.schemas.teacher import TeacherIdentity

    intruder = await services.teachers.get_or_create(
        TeacherIdentity(telegram_id=888, full_name="Intruder")
    )
    with pytest.raises(ClassNotFoundError):
        await services.classes.resolve(intruder.id, "SE401")
    assert await services.class_repository.get_owned(classroom.id, intruder.id) is None


async def test_class_info_reports_attendance_activity(services, teacher, classroom, roster):
    from app.schemas.attendance import StartAttendanceInput

    before = await services.classes.get_class_info(teacher.id, ClassInfoInput(name="SE401"))
    assert before.total_sessions == 0
    assert before.has_open_session is False

    await services.attendance.start_attendance(teacher.id, StartAttendanceInput(class_name="SE401"))
    after = await services.classes.get_class_info(teacher.id, ClassInfoInput(name="SE401"))
    assert after.total_sessions == 1
    assert after.has_open_session is True
    assert after.last_session_date is not None


async def test_class_image_is_stored_on_the_class_row(services, teacher, classroom):
    assert classroom.has_icon is False
    await services.classes.set_class_icon(teacher.id, classroom.id, "icon.png", b"\x89PNG")
    listed = await services.classes.list_classes(teacher.id)
    assert listed.classes[0].has_icon is True
    image = await services.classes.get_class_icon(teacher.id, classroom.id)
    assert image == (b"\x89PNG", "image/png")


async def test_class_image_rejects_an_unknown_type(services, teacher, classroom):
    with pytest.raises(ValueError, match="PNG"):
        await services.classes.set_class_icon(teacher.id, classroom.id, "icon.txt", b"hello")
    assert await services.classes.get_class_icon(teacher.id, classroom.id) is None

