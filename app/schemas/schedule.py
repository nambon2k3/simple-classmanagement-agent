"""Schedule read models used by the administrator dashboard."""

from __future__ import annotations

from datetime import date, time
from typing import Literal

from pydantic import Field

from app.schemas.common import AppModel, ShortText

WEEKDAY_LABELS: tuple[str, ...] = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


class ScheduleRuleRead(AppModel):
    """A repeating weekday slot."""

    id: int
    class_id: int
    weekday: int = Field(ge=0, le=6)
    weekday_label: str
    start_time: time
    end_time: time
    is_active: bool = True


class ExtraSessionRead(AppModel):
    """A one-off extra class."""

    id: int
    class_id: int
    session_date: date
    start_time: time
    end_time: time
    note: str | None = None


class ScheduleOccurrence(AppModel):
    """One calendar cell entry generated from a weekly rule or an extra session."""

    class_id: int
    class_name: str
    session_date: date
    start_time: time
    end_time: time
    kind: Literal["weekly", "extra"]
    extra_id: int | None = None
    note: ShortText | None = None
    completed: bool = False
    cancelled: bool = False


class TodaySlot(AppModel):
    """One meeting time for a class on the current day."""

    start_time: time
    end_time: time
    kind: Literal["weekly", "extra"]


class TodayClassRead(AppModel):
    """A class scheduled today, with whether its teaching day is finished."""

    class_id: int
    class_name: str
    slots: list[TodaySlot]
    completed: bool
    cancelled: bool = False
    student_count: int
