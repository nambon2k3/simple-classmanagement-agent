"""Student read models and tool contracts."""

from __future__ import annotations

from pydantic import Field, field_validator

from app.schemas.common import (
    ClassName,
    EmailAddress,
    OperationResult,
    PersonName,
    PhoneNumber,
    ShortText,
    StudentCode,
    StudentReference,
    ToolInput,
    ToolOutput,
    validate_meaningful_name,
)


class StudentRead(ToolOutput):
    """A student as presented to the teacher."""

    id: int = Field(description="Internal student identifier.")
    student_code: str = Field(description="Teacher-facing student ID, for example SE001.")
    full_name: str = Field(description="Student's full name.")
    class_name: str | None = Field(default=None, description="Name of the class they belong to.")
    email: str | None = Field(default=None, description="Contact email, if recorded.")
    phone: str | None = Field(default=None, description="Contact phone number, if recorded.")
    note: str | None = Field(default=None, description="Free-text note about the student.")


# ------------------------------------------------------------- add_student --


class AddStudentInput(ToolInput):
    """Arguments for ``add_student``."""

    class_name: ClassName = Field(description="Class to enrol the student into.")
    full_name: PersonName = Field(description="Student's full name, for example 'Nguyen Van A'.")
    student_code: StudentCode = Field(
        description="Student ID within the class, for example 'SE001'."
    )
    email: EmailAddress | None = Field(default=None, description="Optional contact email.")
    phone: PhoneNumber | None = Field(default=None, description="Optional phone number.")
    note: ShortText | None = Field(default=None, description="Optional note.")

    @field_validator("full_name")
    @classmethod
    def _check_name(cls, value: str) -> str:
        return validate_meaningful_name(value, "student name")


class AddStudentOutput(OperationResult):
    """Result of enrolling a student."""

    student: StudentRead = Field(description="The student that was added.")


# ---------------------------------------------------------- remove_student --


class RemoveStudentInput(ToolInput):
    """Arguments for ``remove_student``."""

    student: StudentReference = Field(
        description="Student ID or name, for example 'SE001' or 'Nguyen Van A'."
    )
    class_name: ClassName | None = Field(
        default=None,
        description="Class to look in. Required only when the reference is ambiguous.",
    )
    confirm: bool = Field(
        default=False,
        description=(
            "Set to true only after the teacher confirmed. Removing a student also "
            "deletes their attendance history."
        ),
    )


class RemoveStudentOutput(OperationResult):
    """Result of removing a student."""

    removed_student: str = Field(description="Label of the student that was removed.")


# ---------------------------------------------------------- update_student --


class UpdateStudentInput(ToolInput):
    """Arguments for ``update_student``.

    Only the fields that are supplied are changed; omitted fields are left
    untouched, so the model never has to resend values it does not know.
    """

    student: StudentReference = Field(description="Student ID or name identifying the student.")
    class_name: ClassName | None = Field(
        default=None, description="Class to look in, when the reference is ambiguous."
    )
    new_full_name: PersonName | None = Field(default=None, description="Replacement full name.")
    new_student_code: StudentCode | None = Field(
        default=None, description="Replacement student ID."
    )
    email: EmailAddress | None = Field(default=None, description="Replacement email address.")
    phone: PhoneNumber | None = Field(default=None, description="Replacement phone number.")
    note: ShortText | None = Field(default=None, description="Replacement note.")


class UpdateStudentOutput(OperationResult):
    """Result of updating a student."""

    student: StudentRead = Field(description="The student after the update.")


# ----------------------------------------------------------- list_students --


class ListStudentsInput(ToolInput):
    """Arguments for ``list_students``."""

    class_name: ClassName = Field(description="Class whose roster should be listed.")


class ListStudentsOutput(ToolOutput):
    """Roster of a class."""

    class_name: str = Field(description="The class that was listed.")
    students: list[StudentRead] = Field(description="Students in the class, ordered by name.")
    total: int = Field(description="Number of students.")


# ---------------------------------------------------------- search_student --


class SearchStudentInput(ToolInput):
    """Arguments for ``search_student``."""

    query: StudentReference = Field(description="Name fragment or student ID to search for.")
    class_name: ClassName | None = Field(
        default=None, description="Restrict the search to one class."
    )


class SearchStudentOutput(ToolOutput):
    """Students matching a search."""

    query: str = Field(description="The search term that was used.")
    students: list[StudentRead] = Field(description="Matching students, best match first.")
    total: int = Field(description="Number of matches.")
