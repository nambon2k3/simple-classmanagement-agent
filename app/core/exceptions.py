"""Domain exception hierarchy.

Services raise these instead of leaking driver or ORM errors upwards.  Each
error carries a stable machine-readable :attr:`code` plus a message that is
safe to show to an end user, which lets the AI layer turn a failure into a
natural reply without ever seeing a stack trace or SQL fragment.
"""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Base class for every expected, user-recoverable domain failure."""

    #: Stable identifier surfaced to the AI layer and to API clients.
    code: str = "app_error"
    #: Default human-readable message used when none is supplied.
    default_message: str = "Something went wrong."

    def __init__(self, message: str | None = None, /, **details: Any) -> None:
        """Create the error.

        Args:
            message: Teacher-safe explanation.  Falls back to
                :attr:`default_message`.
            **details: Structured context (candidate names, conflicting values)
                that the assistant can use to ask a precise follow-up question.
        """
        self.message = message or self.default_message
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Serialise the error for tool output or an HTTP error body."""
        payload: dict[str, Any] = {"error": self.code, "message": self.message}
        if self.details:
            payload["details"] = self.details
        return payload

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        """Return a developer-facing representation including the error code."""
        return f"{type(self).__name__}(code={self.code!r}, message={self.message!r})"


# --------------------------------------------------------------- generic ----


class NotFoundError(AppError):
    """A requested entity does not exist."""

    code = "not_found"
    default_message = "The requested item could not be found."


class ConflictError(AppError):
    """The request clashes with the current state of the data."""

    code = "conflict"
    default_message = "That conflicts with something that already exists."


class ValidationError(AppError):
    """Input failed a business rule (as opposed to a schema rule)."""

    code = "validation_error"
    default_message = "The information provided is not valid."


class PermissionDeniedError(AppError):
    """The caller does not own, and may not touch, the target resource."""

    code = "permission_denied"
    default_message = "You do not have access to that."


class ConfirmationRequiredError(AppError):
    """A destructive action was requested without explicit confirmation.

    Raised rather than performed so the assistant asks the teacher to confirm
    before anything is deleted.
    """

    code = "confirmation_required"
    default_message = "Please confirm before I do that."


class AmbiguousReferenceError(AppError):
    """A human reference matched several records and needs disambiguation."""

    code = "ambiguous_reference"
    default_message = "That matches more than one record. Please be more specific."


# --------------------------------------------------------------- classes ----


class ClassNotFoundError(NotFoundError):
    """The teacher has no class with the requested name."""

    code = "class_not_found"
    default_message = "I couldn't find that class."


class ClassAlreadyExistsError(ConflictError):
    """The teacher already owns a class with that name."""

    code = "class_already_exists"
    default_message = "You already have a class with that name."


class EmptyClassError(ValidationError):
    """The class exists but has no students enrolled."""

    code = "empty_class"
    default_message = "That class has no students yet."


class ScheduleConflictError(ConflictError):
    """A weekly slot or extra session already exists for that class."""

    code = "schedule_conflict"
    default_message = "That schedule slot already exists."


# -------------------------------------------------------------- students ----


class StudentNotFoundError(NotFoundError):
    """No student matched the reference the teacher used."""

    code = "student_not_found"
    default_message = "I couldn't find that student."


class DuplicateStudentError(ConflictError):
    """The student ID is already taken within the class."""

    code = "duplicate_student"
    default_message = "A student with that ID already exists in this class."


class AmbiguousStudentError(AmbiguousReferenceError):
    """The reference matched more than one student."""

    code = "ambiguous_student"
    default_message = "Several students match that name. Please use the student ID."


# ------------------------------------------------------------ attendance ----


class AttendanceSessionNotFoundError(NotFoundError):
    """No attendance session exists for that class and date."""

    code = "attendance_session_not_found"
    default_message = "There is no attendance session for that class and date."


class AttendanceAlreadyTakenError(ConflictError):
    """Attendance for that class and date is already complete."""

    code = "attendance_already_taken"
    default_message = "Attendance for that class has already been completed today."


class NoActiveAttendanceSessionError(ValidationError):
    """No attendance session is currently open."""

    code = "no_active_attendance_session"
    default_message = "No attendance session is currently open."


class AttendanceSessionClosedError(ValidationError):
    """The session is closed and can no longer be edited."""

    code = "attendance_session_closed"
    default_message = "That attendance session is already closed."


# --------------------------------------------------------------- ai layer ---


class ToolNotFoundError(AppError):
    """The model asked for a tool that is not registered."""

    code = "tool_not_found"
    default_message = "That action is not available."


class ToolInputError(ValidationError):
    """The arguments supplied by the model failed validation."""

    code = "tool_input_error"
    default_message = "Some required information is missing or invalid."


class AssistantError(AppError):
    """The assistant could not complete the turn."""

    code = "assistant_error"
    default_message = "I had trouble processing that. Please try again."
