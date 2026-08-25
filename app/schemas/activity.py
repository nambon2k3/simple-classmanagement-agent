"""Recent-activity read models for the administrator home page."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from app.schemas.common import ToolOutput


class ActivityKind(StrEnum):
    """What kind of change an activity entry describes."""

    CLASS_CREATED = "class_created"
    CLASS_UPDATED = "class_updated"
    STUDENT_ADDED = "student_added"
    STUDENT_UPDATED = "student_updated"
    ATTENDANCE_STARTED = "attendance_started"
    ATTENDANCE_COMPLETED = "attendance_completed"
    TUITION_PAID = "tuition_paid"

    @property
    def badge(self) -> str:
        """Two- or three-letter marker shown next to the entry."""
        return _BADGES[self]


_BADGES: dict[ActivityKind, str] = {
    ActivityKind.CLASS_CREATED: "NEW",
    ActivityKind.CLASS_UPDATED: "UPD",
    ActivityKind.STUDENT_ADDED: "NEW",
    ActivityKind.STUDENT_UPDATED: "UPD",
    ActivityKind.ATTENDANCE_STARTED: "ATT",
    ActivityKind.ATTENDANCE_COMPLETED: "ATT",
    ActivityKind.TUITION_PAID: "PAID",
}


class ActivityEntry(ToolOutput):
    """One thing that happened, newest first in a feed."""

    kind: ActivityKind = Field(description="What changed.")
    text: str = Field(description="Teacher-facing description of the change.")
    occurred_at: datetime = Field(description="When it happened, in UTC.")
    class_name: str | None = Field(default=None, description="Class the change belongs to.")
