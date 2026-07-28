"""Slash-command handlers.

Commands are shortcuts, not the primary interface: everything they do can also
be said in plain language.  They exist because ``/help`` is discoverable and
because a few read-only actions are not worth a model round trip.
"""

from __future__ import annotations

from telegram.ext import ContextTypes

from app.core.logging import get_logger
from app.schemas.attendance import GetAttendanceStateInput
from app.telegram.formatting import HELP_MESSAGE, WELCOME_MESSAGE, escape_html
from app.telegram.runtime import get_runtime
from app.telegram.views import reply_html, send_attendance_board
from telegram import Update

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greet the teacher and register their account on first contact."""
    message, user = update.effective_message, update.effective_user
    if message is None or user is None:
        return

    runtime = get_runtime(context)
    async with runtime.scope(user) as (_, teacher):
        greeting = escape_html(teacher.display_name.split()[0])

    await reply_html(message, WELCOME_MESSAGE.format(name=greeting))


async def help_command(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Explain what the assistant can do."""
    if update.effective_message is not None:
        await reply_html(update.effective_message, HELP_MESSAGE)


async def classes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List the teacher's classes without involving the language model."""
    message, user = update.effective_message, update.effective_user
    if message is None or user is None:
        return

    runtime = get_runtime(context)
    async with runtime.scope(user) as (services, teacher):
        result = await services.classes.list_classes(teacher.id)

    if not result.classes:
        await reply_html(
            message,
            "You don't have any classes yet.\nTry: <i>Create class SE401</i>",
        )
        return

    lines = ["<b>Your classes</b>", ""]
    lines += [
        f"• <b>{escape_html(item.name)}</b> — {item.student_count} student(s)"
        for item in result.classes
    ]
    await reply_html(message, "\n".join(lines))


async def attendance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the open attendance session, if there is one."""
    message, user = update.effective_message, update.effective_user
    if message is None or user is None:
        return

    runtime = get_runtime(context)
    async with runtime.scope(user) as (services, teacher):
        state = await runtime.conversations.get_or_create(message.chat_id, teacher.id)
        result = await services.attendance.get_state(
            teacher.id,
            GetAttendanceStateInput(class_name=None),
            preferred_class_id=state.focus_class_id,
        )
        session = result.session

    if session is None:
        await reply_html(
            message,
            "No attendance session is open.\nTry: <i>Take attendance for SE401</i>",
        )
        return

    board = await send_attendance_board(message, session)
    state.focus_class_id = session.class_id
    state.focus_session_id = session.session_id
    state.attendance_message_id = board.message_id
    await runtime.conversations.save(state)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forget the conversation context.

    Only the chat context is cleared — classes, students and attendance stay in
    the database, and an open session remains open.
    """
    message = update.effective_message
    if message is None:
        return

    await get_runtime(context).conversations.clear(message.chat_id)
    await reply_html(
        message,
        "🧹 Context cleared. Your classes and attendance records are untouched.",
    )
