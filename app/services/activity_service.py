"""Build the recent-activity feed shown on the administrator home page."""

from __future__ import annotations

from datetime import timedelta

from app.core.logging import get_logger
from app.models.enums import AttendanceSessionStatus
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity import ActivityEntry, ActivityKind
from app.utils.money import format_vnd

logger = get_logger(__name__)

#: ``updated_at`` is set by the same statement that inserts a row, so a change
#: only counts as an edit once it is clearly later than the creation.
_EDIT_THRESHOLD = timedelta(seconds=2)


class ActivityService:
    """Merge per-table change timestamps into one reverse-chronological feed."""

    def __init__(self, activity_repository: ActivityRepository) -> None:
        """Wire the service to its data source."""
        self._activity = activity_repository

    async def recent(self, teacher_id: int, limit: int = 12) -> list[ActivityEntry]:
        """Return the newest changes across classes, students, roll-calls and payments."""
        entries: list[ActivityEntry] = []

        for name, created, updated in await self._activity.recent_classes(teacher_id, limit):
            entries.append(
                ActivityEntry(
                    kind=ActivityKind.CLASS_CREATED,
                    text=f"Class {name} created",
                    occurred_at=created,
                    class_name=name,
                )
            )
            if _is_edit(created, updated):
                entries.append(
                    ActivityEntry(
                        kind=ActivityKind.CLASS_UPDATED,
                        text=f"Class {name} updated",
                        occurred_at=updated,
                        class_name=name,
                    )
                )

        for name, code, class_name, created, updated in await self._activity.recent_students(
            teacher_id, limit
        ):
            entries.append(
                ActivityEntry(
                    kind=ActivityKind.STUDENT_ADDED,
                    text=f"{name} ({code}) enrolled in {class_name}",
                    occurred_at=created,
                    class_name=class_name,
                )
            )
            if _is_edit(created, updated):
                entries.append(
                    ActivityEntry(
                        kind=ActivityKind.STUDENT_UPDATED,
                        text=f"{name} ({code}) details updated",
                        occurred_at=updated,
                        class_name=class_name,
                    )
                )

        for name, status, opened, closed in await self._activity.recent_sessions(teacher_id, limit):
            entries.append(
                ActivityEntry(
                    kind=ActivityKind.ATTENDANCE_STARTED,
                    text=f"Attendance started for {name}",
                    occurred_at=opened,
                    class_name=name,
                )
            )
            if closed is not None and status is AttendanceSessionStatus.COMPLETED:
                entries.append(
                    ActivityEntry(
                        kind=ActivityKind.ATTENDANCE_COMPLETED,
                        text=f"Attendance finished for {name}",
                        occurred_at=closed,
                        class_name=name,
                    )
                )

        for student, class_name, days, amount, paid_at in await self._activity.recent_payments(
            teacher_id, limit
        ):
            entries.append(
                ActivityEntry(
                    kind=ActivityKind.TUITION_PAID,
                    text=f"{student} paid {format_vnd(amount)} for {days} day(s) in {class_name}",
                    occurred_at=paid_at,
                    class_name=class_name,
                )
            )

        entries.sort(key=lambda entry: entry.occurred_at, reverse=True)
        return entries[:limit]


def _is_edit(created: object, updated: object) -> bool:
    """Whether ``updated`` is late enough after ``created`` to be a real edit."""
    if created is None or updated is None:
        return False
    try:
        return updated - created > _EDIT_THRESHOLD  # type: ignore[operator]
    except TypeError:  # pragma: no cover - mixed naive/aware timestamps
        return False
