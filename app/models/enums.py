"""Enumerations shared by the ORM models, schemas and AI tool contracts."""

from __future__ import annotations

from enum import StrEnum


class AttendanceStatus(StrEnum):
    """How a student was accounted for in a single attendance session."""

    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"

    @property
    def emoji(self) -> str:
        """Icon used when rendering the status in Telegram."""
        return _STATUS_EMOJI[self]

    @property
    def label(self) -> str:
        """Human-readable label, e.g. ``"Late"``."""
        return self.value.capitalize()

    @property
    def counts_as_attended(self) -> bool:
        """Whether the status contributes to the attendance rate.

        Late students were in the room, so they count as attended; excused
        absences do not count as attendance but are reported separately from
        unexcused ones.
        """
        return self in {AttendanceStatus.PRESENT, AttendanceStatus.LATE}


class AttendanceSessionStatus(StrEnum):
    """Lifecycle of an attendance session."""

    #: Being filled in right now; records may still change.
    OPEN = "open"
    #: Finalised by the teacher; the summary has been produced.
    COMPLETED = "completed"
    #: Abandoned without being finalised.
    CANCELLED = "cancelled"


class TuitionChargeStatus(StrEnum):
    """Whether a billed attendance day has been paid."""

    NOT_YET = "not_yet"
    COMPLETED = "completed"

    @property
    def label(self) -> str:
        """Teacher-facing status, e.g. ``"Not yet"``."""
        if self is TuitionChargeStatus.NOT_YET:
            return "Not yet"
        return "Completed"


_STATUS_EMOJI: dict[AttendanceStatus, str] = {
    AttendanceStatus.PRESENT: "✅",
    AttendanceStatus.ABSENT: "❌",
    AttendanceStatus.LATE: "🟡",
    AttendanceStatus.EXCUSED: "📝",
}
