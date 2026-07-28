"""Inline-keyboard callback handlers.

Button presses bypass the language model entirely: the callback payload already
names the session, the student and the status, so there is nothing to infer.
They still go through the same services as the conversational path, which is
what keeps the two ways of marking attendance consistent.
"""

from __future__ import annotations

from telegram.ext import ContextTypes

from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.models.enums import AttendanceStatus
from app.schemas.attendance import AttendanceSessionRead
from app.services.container import ServiceContainer
from app.telegram.formatting import render_finish_summary
from app.telegram.keyboards import (
    NOOP_DATA,
    AttendanceCallback,
    CallbackParseError,
    parse_attendance_callback,
)
from app.telegram.runtime import get_runtime
from app.telegram.views import refresh_attendance_board, reply_html
from app.utils.text import truncate
from telegram import Update

logger = get_logger(__name__)

#: Telegram truncates callback answers beyond 200 characters.
_MAX_TOAST_LENGTH = 190


async def handle_attendance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Apply an attendance button press and redraw the board."""
    query = update.callback_query
    user = update.effective_user
    if query is None or user is None:
        return

    if query.data == NOOP_DATA:
        await query.answer()
        return

    board_message = query.message
    if board_message is None:
        # The original message is too old for Telegram to hand back to us.
        await query.answer("This board has expired. Send /attendance to reopen it.")
        return

    try:
        action = parse_attendance_callback(query.data or "")
    except CallbackParseError:
        logger.info("Ignoring unrecognised callback", extra={"data": query.data})
        await query.answer("That button is no longer valid.")
        return

    runtime = get_runtime(context)
    try:
        async with runtime.scope(user) as (services, teacher):
            state = await runtime.conversations.get_or_create(board_message.chat_id, teacher.id)
            session, toast, closing_summary = await _apply(services, teacher.id, action)
    except AppError as exc:
        await query.answer(truncate(exc.message, _MAX_TOAST_LENGTH), show_alert=True)
        return

    await query.answer(toast)
    if session is None:
        return

    state.focus_class_id = session.class_id
    state.focus_session_id = session.session_id
    state.attendance_message_id = board_message.message_id

    await refresh_attendance_board(
        context.bot,
        board_message.chat_id,
        board_message.message_id,
        session,
        action.page,
        keep_keyboard=closing_summary is None,
    )

    if closing_summary is not None:
        state.clear_attendance_focus()
        await reply_html(board_message, closing_summary)

    await runtime.conversations.save(state)


async def _apply(
    services: ServiceContainer,
    teacher_id: int,
    action: AttendanceCallback,
) -> tuple[AttendanceSessionRead | None, str, str | None]:
    """Perform the requested action and report what should be rendered.

    Args:
        services: Service container bound to the current transaction.
        teacher_id: Owner of the data.
        action: The decoded button press.

    Returns:
        The session state to draw, the toast to show on the button, and a
        closing summary when the session has just ended (``None`` otherwise).
    """
    attendance = services.attendance

    match action.action:
        case "mark" if action.student_id is not None and action.status is not None:
            session = await attendance.set_status_by_ids(
                teacher_id, action.session_id, action.student_id, action.status
            )
            return session, f"{action.status.emoji} {_entry_name(session, action.student_id)}", None

        case "page":
            session = await attendance.get_session_view(teacher_id, action.session_id)
            return session, "", None

        case "rest":
            result = await attendance.mark_remaining_in_session(
                teacher_id, action.session_id, AttendanceStatus.PRESENT
            )
            session = await attendance.get_session_view(teacher_id, action.session_id)
            return session, f"Marked {result.updated} present", None

        case "done":
            result = await attendance.finish_session(teacher_id, action.session_id)
            session = await attendance.get_session_view(teacher_id, action.session_id)
            return session, "Attendance saved", render_finish_summary(result)

        case "cancel":
            await attendance.cancel_session(teacher_id, action.session_id)
            session = await attendance.get_session_view(teacher_id, action.session_id)
            return session, "Session cancelled", "🚫 <b>Attendance session cancelled.</b>"

        case _:
            logger.warning("Unhandled attendance action", extra={"action": action.action})
            return None, "", None


def _entry_name(session: AttendanceSessionRead, student_id: int) -> str:
    """Name of a student inside a rendered session, for the toast message."""
    for entry in session.entries:
        if entry.student_id == student_id:
            return truncate(entry.full_name, 40)
    return "Student"
