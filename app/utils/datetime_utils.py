"""Date and time helpers.

Attendance is anchored to the teacher's local calendar day, not to UTC, so
"today" must always be resolved through these helpers rather than by calling
:meth:`datetime.date.today` directly.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.config import get_settings

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def utc_now() -> datetime:
    """Current instant as a timezone-aware UTC datetime."""
    return datetime.now(UTC)


def current_timezone() -> ZoneInfo:
    """The configured application timezone."""
    return get_settings().tzinfo


def today(tz: ZoneInfo | None = None) -> date:
    """Return the current local calendar date.

    Args:
        tz: Timezone to resolve the date in.  Defaults to the configured
            application timezone.
    """
    return datetime.now(tz or current_timezone()).date()


def parse_date(value: str | date | None, *, default_to_today: bool = True) -> date:
    """Coerce a user- or model-supplied value into a :class:`~datetime.date`.

    Accepts ``date`` objects, ISO ``YYYY-MM-DD`` strings and the relative
    keywords ``today`` and ``yesterday`` that language models like to emit.

    Args:
        value: The value to interpret.
        default_to_today: Whether ``None`` resolves to today rather than raising.

    Raises:
        ValueError: If the value cannot be interpreted as a date.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if value is None:
        if default_to_today:
            return today()
        raise ValueError("A date is required.")

    text = value.strip().lower()
    if text in {"", "today", "now"}:
        return today()
    if text == "yesterday":
        return today() - timedelta(days=1)
    if text == "tomorrow":
        return today() + timedelta(days=1)
    if _ISO_DATE.match(text):
        return date.fromisoformat(text)
    raise ValueError(f"Could not understand the date {value!r}. Use YYYY-MM-DD.")


def week_bounds(anchor: date | None = None) -> tuple[date, date]:
    """Return the Monday-to-Sunday range containing ``anchor`` (inclusive)."""
    anchor = anchor or today()
    start = anchor - timedelta(days=anchor.weekday())
    return start, start + timedelta(days=6)


def month_bounds(anchor: date | None = None) -> tuple[date, date]:
    """Return the first and last day of the month containing ``anchor``."""
    anchor = anchor or today()
    start = anchor.replace(day=1)
    next_month = (start + timedelta(days=32)).replace(day=1)
    return start, next_month - timedelta(days=1)


def format_date(value: date) -> str:
    """Render a date the way it is shown to teachers, e.g. ``Mon 27 Jul 2026``."""
    return value.strftime("%a %d %b %Y")
