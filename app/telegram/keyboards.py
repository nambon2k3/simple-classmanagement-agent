"""Inline keyboards and their callback-data codec.

Telegram caps ``callback_data`` at 64 bytes, so actions are encoded as short
colon-separated tokens rather than JSON.  Encoding and decoding live together
here so the two can never drift apart, and both are pure functions that are
trivial to unit test.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from app.models.enums import AttendanceStatus
from app.schemas.attendance import AttendanceSessionRead
from app.utils.text import truncate
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

#: Namespace prefix for every attendance callback.
ATTENDANCE_PREFIX: Final = "att"
#: Callback for buttons that exist only as labels.
NOOP_DATA: Final = "noop"

#: Students shown per keyboard page.  Telegram renders long keyboards poorly,
#: and a page of six keeps the whole roll-call on one screen.
PAGE_SIZE: Final = 6

#: Single-character codes keep callback data inside the 64-byte limit.
_STATUS_CODES: Final[dict[str, AttendanceStatus]] = {
    "p": AttendanceStatus.PRESENT,
    "a": AttendanceStatus.ABSENT,
    "l": AttendanceStatus.LATE,
    "e": AttendanceStatus.EXCUSED,
}
_CODE_BY_STATUS: Final[dict[AttendanceStatus, str]] = {
    status: code for code, status in _STATUS_CODES.items()
}

#: Maximum characters of a student's name shown on a button.
_NAME_BUTTON_WIDTH: Final = 16


class CallbackParseError(ValueError):
    """The callback payload did not match any known action."""


@dataclass(frozen=True, slots=True)
class AttendanceCallback:
    """A decoded attendance button press."""

    #: One of ``mark``, ``page``, ``rest``, ``done`` or ``cancel``.
    action: str
    session_id: int
    student_id: int | None = None
    status: AttendanceStatus | None = None
    page: int = 0


def encode_mark(session_id: int, student_id: int, status: AttendanceStatus, page: int) -> str:
    """Encode a "set this student's status" button."""
    return f"{ATTENDANCE_PREFIX}:mark:{session_id}:{student_id}:{_CODE_BY_STATUS[status]}:{page}"


def encode_page(session_id: int, page: int) -> str:
    """Encode a pagination button."""
    return f"{ATTENDANCE_PREFIX}:page:{session_id}:{page}"


def encode_simple(action: str, session_id: int, page: int = 0) -> str:
    """Encode a whole-session action such as finishing or cancelling."""
    return f"{ATTENDANCE_PREFIX}:{action}:{session_id}:{page}"


def parse_attendance_callback(data: str) -> AttendanceCallback:
    """Decode a callback payload produced by this module.

    Args:
        data: The raw ``callback_data`` string.

    Returns:
        The decoded action.

    Raises:
        CallbackParseError: If the payload is malformed or unknown.
    """
    parts = data.split(":")
    if len(parts) < 3 or parts[0] != ATTENDANCE_PREFIX:
        raise CallbackParseError(f"Unrecognised callback data: {data!r}")

    action = parts[1]
    try:
        session_id = int(parts[2])
        if action == "mark":
            return AttendanceCallback(
                action=action,
                session_id=session_id,
                student_id=int(parts[3]),
                status=_STATUS_CODES[parts[4]],
                page=int(parts[5]),
            )
        if action in {"page", "rest", "done", "cancel"}:
            return AttendanceCallback(action=action, session_id=session_id, page=int(parts[3]))
    except (IndexError, KeyError, ValueError) as exc:
        raise CallbackParseError(f"Malformed callback data: {data!r}") from exc

    raise CallbackParseError(f"Unknown callback action: {action!r}")


def page_count(total: int) -> int:
    """Number of keyboard pages needed for ``total`` students (at least one)."""
    return max(1, -(-total // PAGE_SIZE))


def clamp_page(page: int, total: int) -> int:
    """Constrain a page index to the range that actually exists."""
    return max(0, min(page, page_count(total) - 1))


def build_attendance_keyboard(
    session: AttendanceSessionRead, page: int = 0
) -> InlineKeyboardMarkup:
    """Build the tap-to-mark keyboard for an attendance session.

    Each student occupies one row: a label showing their current status,
    followed by present / absent / late buttons.  Excused is reached by typing,
    which keeps the common case to one tap.

    Args:
        session: Current session state, including who has been marked.
        page: Zero-based page of the roster to display.

    Returns:
        The keyboard markup.
    """
    total = len(session.entries)
    page = clamp_page(page, total)
    window = session.entries[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]

    rows: list[list[InlineKeyboardButton]] = []
    for entry in window:
        icon = entry.status.emoji if entry.status else "⬜"
        rows.append(
            [
                InlineKeyboardButton(
                    f"{icon} {truncate(entry.full_name, _NAME_BUTTON_WIDTH)}",
                    callback_data=NOOP_DATA,
                ),
                *(
                    InlineKeyboardButton(
                        status.emoji,
                        callback_data=encode_mark(
                            session.session_id, entry.student_id, status, page
                        ),
                    )
                    for status in (
                        AttendanceStatus.PRESENT,
                        AttendanceStatus.ABSENT,
                        AttendanceStatus.LATE,
                    )
                ),
            ]
        )

    pages = page_count(total)
    if pages > 1:
        rows.append(
            [
                InlineKeyboardButton(
                    "◀️",
                    callback_data=encode_page(session.session_id, max(0, page - 1)),
                ),
                InlineKeyboardButton(f"{page + 1}/{pages}", callback_data=NOOP_DATA),
                InlineKeyboardButton(
                    "▶️",
                    callback_data=encode_page(session.session_id, min(pages - 1, page + 1)),
                ),
            ]
        )

    rows.append(
        [
            InlineKeyboardButton(
                "✅ Rest present",
                callback_data=encode_simple("rest", session.session_id, page),
            ),
            InlineKeyboardButton(
                "🏁 Finish",
                callback_data=encode_simple("done", session.session_id, page),
            ),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(
                "✖️ Cancel session",
                callback_data=encode_simple("cancel", session.session_id, page),
            )
        ]
    )
    return InlineKeyboardMarkup(rows)
