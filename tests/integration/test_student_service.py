"""Student management and reference resolution against a real database."""

from __future__ import annotations

import pytest

from app.core.exceptions import (
    AmbiguousStudentError,
    ConfirmationRequiredError,
    DuplicateStudentError,
    StudentNotFoundError,
)
from app.schemas.classroom import CreateClassInput
from app.schemas.student import (
    AddStudentInput,
    ListStudentsInput,
    RemoveStudentInput,
    SearchStudentInput,
    UpdateStudentInput,
)


async def test_add_student(services, teacher, classroom):
    result = await services.students.add_student(
        teacher.id,
        AddStudentInput(class_name="SE401", full_name="Nguyen Van A", student_code="SE001"),
    )
    assert result.student.student_code == "SE001"
    assert result.student.class_name == "SE401"


async def test_student_codes_are_normalised_to_upper_case(services, teacher, classroom):
    result = await services.students.add_student(
        teacher.id,
        AddStudentInput(class_name="SE401", full_name="Someone", student_code=" se009 "),
    )
    assert result.student.student_code == "SE009"


async def test_duplicate_student_code_within_a_class_is_rejected(services, teacher, roster):
    with pytest.raises(DuplicateStudentError) as error:
        await services.students.add_student(
            teacher.id,
            AddStudentInput(class_name="SE401", full_name="Someone Else", student_code="SE001"),
        )
    assert error.value.details["existing_student"] == "Nguyen Van A"


async def test_the_same_code_may_exist_in_another_class(services, teacher, roster):
    await services.classes.create_class(teacher.id, CreateClassInput(name="AI202"))
    result = await services.students.add_student(
        teacher.id,
        AddStudentInput(class_name="AI202", full_name="Different Person", student_code="SE001"),
    )
    assert result.success


async def test_list_students_is_ordered_by_name(services, teacher, roster):
    result = await services.students.list_students(
        teacher.id, ListStudentsInput(class_name="SE401")
    )
    assert result.total == 3
    assert [student.full_name for student in result.students] == [
        "Alice Nguyen",
        "John Smith",
        "Nguyen Van A",
    ]


async def test_resolve_by_student_code(services, teacher, roster):
    student = await services.students.resolve(teacher.id, "se001")
    assert student.full_name == "Nguyen Van A"


async def test_resolve_by_first_name(services, teacher, roster):
    student = await services.students.resolve(teacher.id, "John")
    assert student.student_code == "SE002"


async def test_resolve_by_accentless_full_name(services, teacher, classroom):
    await services.students.add_student(
        teacher.id,
        AddStudentInput(class_name="SE401", full_name="Nguyễn Thị B", student_code="SE010"),
    )
    student = await services.students.resolve(teacher.id, "nguyen thi b")
    assert student.student_code == "SE010"


async def test_ambiguous_reference_lists_the_candidates(services, teacher, roster):
    await services.students.add_student(
        teacher.id,
        AddStudentInput(class_name="SE401", full_name="John Doe", student_code="SE004"),
    )
    with pytest.raises(AmbiguousStudentError) as error:
        await services.students.resolve(teacher.id, "John")
    assert len(error.value.details["candidates"]) == 2


async def test_ambiguity_is_resolved_by_narrowing_to_a_class(services, teacher, roster):
    """The same person's name in two classes is only ambiguous across both."""
    second = await services.classes.create_class(teacher.id, CreateClassInput(name="AI202"))
    for class_name, code in (("SE401", "SE004"), ("AI202", "AI001")):
        await services.students.add_student(
            teacher.id,
            AddStudentInput(class_name=class_name, full_name="John Doe", student_code=code),
        )

    with pytest.raises(AmbiguousStudentError):
        await services.students.resolve(teacher.id, "John Doe")

    student = await services.students.resolve(teacher.id, "John Doe", class_id=second.classroom.id)
    assert student.student_code == "AI001"


async def test_unknown_student_is_reported(services, teacher, roster):
    with pytest.raises(StudentNotFoundError):
        await services.students.resolve(teacher.id, "Zebediah Nobody")


async def test_search_returns_several_matches_without_erroring(services, teacher, roster):
    result = await services.students.search_student(teacher.id, SearchStudentInput(query="nguyen"))
    assert result.total == 2


async def test_update_changes_only_the_supplied_fields(services, teacher, roster):
    result = await services.students.update_student(
        teacher.id, UpdateStudentInput(student="SE002", new_full_name="Jonathan Smith")
    )
    assert result.student.full_name == "Jonathan Smith"
    assert result.student.student_code == "SE002"


async def test_update_can_change_the_student_code(services, teacher, roster):
    result = await services.students.update_student(
        teacher.id, UpdateStudentInput(student="SE002", new_student_code="SE099")
    )
    assert result.student.student_code == "SE099"


async def test_update_to_a_taken_code_is_rejected(services, teacher, roster):
    with pytest.raises(DuplicateStudentError):
        await services.students.update_student(
            teacher.id, UpdateStudentInput(student="SE002", new_student_code="SE001")
        )


async def test_update_with_nothing_to_change_is_a_no_op(services, teacher, roster):
    result = await services.students.update_student(teacher.id, UpdateStudentInput(student="SE002"))
    assert "Nothing to change" in result.message


async def test_remove_requires_confirmation(services, teacher, roster):
    with pytest.raises(ConfirmationRequiredError):
        await services.students.remove_student(teacher.id, RemoveStudentInput(student="SE001"))

    result = await services.students.list_students(
        teacher.id, ListStudentsInput(class_name="SE401")
    )
    assert result.total == 3


async def test_remove_deletes_the_student(services, teacher, roster):
    result = await services.students.remove_student(
        teacher.id, RemoveStudentInput(student="SE001", confirm=True)
    )
    assert "Nguyen Van A" in result.removed_student

    remaining = await services.students.list_students(
        teacher.id, ListStudentsInput(class_name="SE401")
    )
    assert remaining.total == 2


async def test_one_teacher_cannot_resolve_anothers_student(services, teacher, roster):
    from app.schemas.teacher import TeacherIdentity

    intruder = await services.teachers.get_or_create(
        TeacherIdentity(telegram_id=999, full_name="Intruder")
    )
    with pytest.raises(StudentNotFoundError):
        await services.students.resolve(intruder.id, "SE001")
