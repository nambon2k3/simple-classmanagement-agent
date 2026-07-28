"""Rendering helpers for Telegram messages.

Two parse modes are used deliberately:

* Messages this application composes (attendance rosters, summaries) are sent
  as **HTML**, because every dynamic value can be escaped with certainty.
* Free text written by the language model is sent as legacy **Markdown** with a
  plain-text fallback, since escaping a model's own formatting would destroy
  the emphasis it intended.
"""

from __future__ import annotations

from html import escape

from app.models.enums import AttendanceStatus
from app.schemas.attendance import (
    AttendanceEntry,
    AttendanceSessionRead,
    AttendanceSummary,
    FinishAttendanceOutput,
)
from app.utils.datetime_utils import format_date
from app.utils.text import truncate

#: Telegram rejects messages longer than 4096 characters.
MAX_MESSAGE_LENGTH = 4096

#: Beyond this many students the roster is summarised instead of listed, so the
#: message stays readable and within Telegram's size limit.
MAX_ROSTER_LINES = 40


def escape_html(value: str) -> str:
    """Escape a dynamic value for Telegram's HTML parse mode."""
    return escape(value, quote=False)


def clip(text: str, limit: int = MAX_MESSAGE_LENGTH) -> str:
    """Trim a message to Telegram's maximum length."""
    return truncate(text, limit)


def status_icon(status: AttendanceStatus | None) -> str:
    """Icon for a status, or a hollow marker when the student is unmarked."""
    return status.emoji if status is not None else "⬜"


def render_summary_line(summary: AttendanceSummary) -> str:
    """One-line tally, e.g. ``✅ 18  ❌ 2  🟡 1  ⬜ 3``."""
    parts = [
        f"{AttendanceStatus.PRESENT.emoji} {summary.present}",
        f"{AttendanceStatus.ABSENT.emoji} {summary.absent}",
        f"{AttendanceStatus.LATE.emoji} {summary.late}",
    ]
    if summary.excused:
        parts.append(f"{AttendanceStatus.EXCUSED.emoji} {summary.excused}")
    if summary.unmarked:
        parts.append(f"⬜ {summary.unmarked}")
    return "  ".join(parts)


def render_attendance_session(session: AttendanceSessionRead) -> str:
    """Render the live attendance message body.

    The whole roster is listed regardless of which keyboard page is showing, so
    the teacher can always see everyone's status at a glance.

    Args:
        session: Current state of the session.

    Returns:
        HTML-formatted message text.
    """
    header = (
        f"<b>Attendance — {escape_html(session.class_name)}</b>\n"
        f"{format_date(session.session_date)}\n"
        f"{render_summary_line(session.summary)}"
    )

    if len(session.entries) > MAX_ROSTER_LINES:
        unmarked = [entry for entry in session.entries if entry.status is None]
        body = (
            f"\n\n{len(session.entries)} students. "
            f"{len(unmarked)} still unmarked.\n"
            "Use the buttons below, or just type <i>“John absent”</i>."
        )
        return clip(header + body)

    lines = [_render_entry(entry) for entry in session.entries]
    footer = "\nTap a button, or type <i>“John absent”</i>." if lines else ""
    return clip(header + "\n\n" + "\n".join(lines) + footer)


def _render_entry(entry: AttendanceEntry) -> str:
    """One roster line: icon, name and student code."""
    return (
        f"{status_icon(entry.status)} {escape_html(entry.full_name)} "
        f"<code>{escape_html(entry.student_code)}</code>"
    )


def render_finish_summary(result: FinishAttendanceOutput) -> str:
    """Render the final summary shown when a session is completed."""
    lines = [
        f"<b>Attendance saved — {escape_html(result.class_name)}</b>",
        format_date(result.session_date),
        "",
        render_summary_line(result.summary),
    ]
    rate = round(result.summary.attendance_rate * 100)
    lines.append(f"Attendance rate: <b>{rate}%</b>")

    for label, names in (
        ("Absent", result.absent_students),
        ("Late", result.late_students),
        ("Excused", result.excused_students),
    ):
        if names:
            listed = ", ".join(escape_html(name) for name in names[:15])
            more = f" +{len(names) - 15} more" if len(names) > 15 else ""
            lines.append(f"\n<b>{label}:</b> {listed}{more}")

    return clip("\n".join(lines))


WELCOME_MESSAGE = """\
👋 <b>Hi {name}!</b>

I'm your class management assistant. Just talk to me normally — no commands or \
menus needed.

<b>Try things like</b>
• <i>Create class SE401</i>
• <i>Add Nguyen Van A (SE001) to SE401</i>
• <i>List students in SE401</i>
• <i>Take attendance for SE401</i>
• <i>John absent</i> · <i>Alice late</i> · <i>Done</i>
• <i>Who was absent today?</i>

Send /help any time to see this again."""


HELP_MESSAGE = """\
<b>What I can do</b>

<b>Classes</b>
• Create, rename or delete a class
• <i>Show all my classes</i>

<b>Students</b>
• <i>Add Nguyen Van A (SE001) to SE401</i>
• <i>Remove SE001</i> · <i>List students in SE401</i>
• <i>Find John</i>

<b>Attendance</b>
• <i>Take attendance for SE401</i> — then tap the buttons, or type \
<i>John absent</i>, <i>Alice late</i>
• <i>Done</i> to save and get the summary

<b>Reports</b>
• <i>Attendance report for SE401</i>
• <i>Show John's attendance</i>
• <i>Who was absent today?</i>
• <i>How many students were absent this week?</i>

<b>Commands</b>
/start — welcome message
/help — this message
/classes — list your classes
/attendance — show the open attendance session
/reset — clear our conversation context"""
