"""Enrolling a whole roster in one call."""

from __future__ import annotations

from app.schemas.student import ImportStudentRow, ImportStudentsInput, ListStudentsInput


async def test_import_enrols_every_row(services, teacher, classroom):
    result = await services.students.import_students(
        teacher.id,
        ImportStudentsInput(
            class_name="SE401",
            students=[
                ImportStudentRow(student_code="SE001", full_name="Nguyen Van A"),
                ImportStudentRow(student_code="se002", full_name="John Smith", phone="0909123456"),
            ],
        ),
    )

    assert result.added == 2
    assert result.skipped == []
    listed = await services.students.list_students(
        teacher.id, ListStudentsInput(class_name="SE401")
    )
    assert {student.student_code for student in listed.students} == {"SE001", "SE002"}


async def test_import_skips_duplicates_without_losing_the_rest(services, teacher, roster):
    result = await services.students.import_students(
        teacher.id,
        ImportStudentsInput(
            class_name="SE401",
            students=[
                ImportStudentRow(student_code="SE001", full_name="Someone Else"),
                ImportStudentRow(student_code="SE009", full_name="New Student"),
                ImportStudentRow(student_code="SE009", full_name="Repeated Row"),
            ],
        ),
    )

    assert result.added == 1
    assert len(result.skipped) == 2
    assert any("already used" in reason for reason in result.skipped)
    assert any("repeated in the file" in reason for reason in result.skipped)
