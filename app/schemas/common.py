"""Shared Pydantic base classes and reusable field types.

These types are the contract in three directions at once: they validate what
the language model sends, they document the tools in the JSON schema handed to
LLM tool contracts, and they shape what gets rendered back to the teacher.
"""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

#: Class and student names must contain at least one letter or digit; a name
#: made only of punctuation is a sign the model mis-parsed the message.
_HAS_ALPHANUMERIC = re.compile(r"[^\W_]", re.UNICODE)


class AppModel(BaseModel):
    """Base model with the conventions used across the application."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=False,
    )


class ToolInput(AppModel):
    """Base class for arguments the language model supplies to a tool.

    ``extra="forbid"`` is deliberate: a hallucinated argument should fail loudly
    and be corrected on the next turn rather than be silently dropped.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

    @model_validator(mode="before")
    @classmethod
    def _blank_strings_become_none(cls, data: object) -> object:
        """Treat ``""`` as omitted — local models often send empty strings for
        optional fields instead of leaving them out."""
        if not isinstance(data, dict):
            return data
        return {key: (None if value == "" else value) for key, value in data.items()}


class ToolOutput(AppModel):
    """Base class for values a tool returns to the language model."""


ClassName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
StudentCode = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=32)]
PersonName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]

# Validated with a pattern rather than pydantic's ``EmailStr``/``format`` so the
# generated JSON schema stays within the subset accepted for function tools
# and the project avoids an extra runtime dependency.
EmailAddress = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    ),
]
PhoneNumber = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=32,
        pattern=r"^[+(]?[\d][\d\s\-().]{3,31}$",
    ),
]

#: A loose, human reference to a student: a name, a partial name or a code.
StudentReference = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]

#: ``YYYY-MM-DD``, or the relative keywords the model tends to emit.
DateInput = Annotated[str, StringConstraints(strip_whitespace=True, max_length=32)]


def validate_meaningful_name(value: str, field_name: str = "name") -> str:
    """Reject names that carry no alphanumeric content.

    Args:
        value: The candidate name.
        field_name: Used to build the error message.

    Raises:
        ValueError: If the name is blank or purely punctuation.
    """
    cleaned = value.strip()
    if not _HAS_ALPHANUMERIC.search(cleaned):
        raise ValueError(f"The {field_name} must contain at least one letter or number.")
    return cleaned


class NamedEntity(ToolOutput):
    """Minimal identity of a record, used inside larger tool responses."""

    id: int = Field(description="Internal identifier.")
    name: str = Field(description="Human-readable name.")


class OperationResult(ToolOutput):
    """Generic acknowledgement for tools that only mutate state."""

    success: bool = Field(default=True, description="Whether the operation succeeded.")
    message: str = Field(description="A short, teacher-friendly description of what happened.")


class ErrorResult(ToolOutput):
    """Structured failure handed back to the model instead of an exception.

    The model reads ``message`` and rephrases it; ``error`` gives it a stable
    signal (for example ``student_not_found``) to branch on, and ``details``
    can carry the options needed to ask a follow-up question.
    """

    success: bool = Field(default=False, description="Always false.")
    error: str = Field(description="Stable machine-readable error code.")
    message: str = Field(description="Explanation that is safe to show the teacher.")
    details: dict[str, object] | None = Field(
        default=None, description="Extra context, such as candidate matches to disambiguate."
    )

    @field_validator("details")
    @classmethod
    def _drop_empty_details(cls, value: dict[str, object] | None) -> dict[str, object] | None:
        return value or None
