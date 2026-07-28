"""Class read models and tool contracts."""

from __future__ import annotations

from pydantic import Field, field_validator

from app.schemas.common import (
    ClassName,
    OperationResult,
    ShortText,
    ToolInput,
    ToolOutput,
    validate_meaningful_name,
)


class ClassRead(ToolOutput):
    """A class as presented to the teacher."""

    id: int = Field(description="Internal class identifier.")
    name: str = Field(description="Class name, for example SE401.")
    description: str | None = Field(default=None, description="Optional free-text description.")
    student_count: int = Field(default=0, description="Number of enrolled students.")
    daily_tuition_fee: int = Field(
        default=0,
        description="Daily tuition in VND charged per student for each attended day.",
    )


# ------------------------------------------------------------ create_class --


class CreateClassInput(ToolInput):
    """Arguments for ``create_class``."""

    name: ClassName = Field(description="Name of the new class, for example 'SE401'.")
    description: ShortText | None = Field(
        default=None, description="Optional description of the class."
    )
    daily_tuition_fee: int = Field(
        default=0,
        ge=0,
        description="Optional daily tuition in VND per attended day. Defaults to 0.",
    )

    @field_validator("name")
    @classmethod
    def _check_name(cls, value: str) -> str:
        return validate_meaningful_name(value, "class name")


class CreateClassOutput(OperationResult):
    """Result of creating a class."""

    classroom: ClassRead = Field(description="The class that was created.")


# ------------------------------------------------------------ rename_class --


class RenameClassInput(ToolInput):
    """Arguments for ``rename_class``."""

    current_name: ClassName = Field(description="The existing name of the class.")
    new_name: ClassName = Field(description="The new name for the class.")

    @field_validator("new_name")
    @classmethod
    def _check_new_name(cls, value: str) -> str:
        return validate_meaningful_name(value, "class name")


class RenameClassOutput(OperationResult):
    """Result of renaming a class."""

    classroom: ClassRead = Field(description="The class after renaming.")


# ------------------------------------------------------------ delete_class --


class DeleteClassInput(ToolInput):
    """Arguments for ``delete_class``."""

    name: ClassName = Field(description="Name of the class to delete.")
    confirm: bool = Field(
        default=False,
        description=(
            "Set to true only after the teacher has explicitly confirmed the deletion. "
            "Deleting a class also deletes its students and attendance history."
        ),
    )


class DeleteClassOutput(OperationResult):
    """Result of deleting a class."""

    deleted_class: str = Field(description="Name of the class that was deleted.")
    deleted_students: int = Field(description="How many students were removed with it.")


# ------------------------------------------------------------ list_classes --


class ListClassesInput(ToolInput):
    """``list_classes`` takes no arguments."""


class ListClassesOutput(ToolOutput):
    """Every class owned by the teacher."""

    classes: list[ClassRead] = Field(description="The teacher's classes.")
    total: int = Field(description="Number of classes.")


# --------------------------------------------------------- get_class_info --


class ClassInfoInput(ToolInput):
    """Arguments for ``get_class_info``."""

    name: ClassName = Field(description="Name of the class to describe.")


class ClassInfoOutput(ToolOutput):
    """Detailed information about a single class."""

    classroom: ClassRead = Field(description="The class itself.")
    total_sessions: int = Field(description="Attendance sessions recorded so far.")
    last_session_date: str | None = Field(
        default=None, description="Date of the most recent attendance session (YYYY-MM-DD)."
    )
    has_open_session: bool = Field(
        default=False, description="Whether an attendance session is currently open."
    )
    daily_tuition_fee: int = Field(
        default=0, description="Daily tuition in VND per attended day."
    )
    formatted_daily_tuition_fee: str = Field(
        description="Human-readable daily tuition, for example '50.000 VND'."
    )
