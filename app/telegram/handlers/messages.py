"""Natural-language message handler.

This is the primary interface: the teacher types whatever they mean and the
assistant works out which tools to call.  The handler itself contains no
business logic — it opens a unit of work, hands the message to the agent, and
renders whatever comes back.
"""

from __future__ import annotations

from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from app.ai.agent import AgentReply
from app.ai.memory import ConversationState
from app.ai.tools.definitions import EMIT_ATTENDANCE_CLOSED, EMIT_ATTENDANCE_SESSION
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.schemas.attendance import AttendanceSessionRead
from app.services.container import ServiceContainer
from app.telegram.runtime import get_runtime
from app.telegram.views import (
    refresh_attendance_board,
    reply_assistant_text,
    send_attendance_board,
)
from app.utils.text import truncate
from telegram import Message, Update

logger = get_logger(__name__)

#: Tools whose effects are visible on the attendance board, so the board is
#: redrawn after the model calls any of them.
_ATTENDANCE_TOOLS = frozenset(
    {
        "update_attendance",
        "mark_remaining_students",
        "start_attendance",
        "finish_attendance",
        "cancel_attendance",
    }
)

#: Longest message accepted.  Anything longer is almost certainly a paste
#: accident, and sending it to the model would be slow and expensive.
_MAX_INPUT_LENGTH = 1500


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route a plain-text message through the assistant."""
    message, user = update.effective_message, update.effective_user
    if message is None or user is None or not message.text:
        return

    text = message.text.strip()
    if not text:
        return
    if len(text) > _MAX_INPUT_LENGTH:
        text = truncate(text, _MAX_INPUT_LENGTH)

    runtime = get_runtime(context)
    await context.bot.send_chat_action(message.chat_id, ChatAction.TYPING)

    # The database transaction stays open across the model round trip because
    # the tools need it mid-loop. That is an acceptable trade for a bot of this
    # size; a high-traffic deployment would give each tool call its own session.
    async with runtime.scope(user) as (services, teacher):
        state = await runtime.conversations.get_or_create(message.chat_id, teacher.id)
        # Finishing a session clears the focus, so remember it beforehand or the
        # board can no longer be located to strip its buttons.
        prior_session_id = state.focus_session_id
        reply = await runtime.agent.run(text, state=state, services=services)
        board, close_board = await _resolve_board(
            state, reply, services, teacher.id, prior_session_id
        )

    await reply_assistant_text(message, reply.text)

    if board is not None:
        if close_board:
            await _close_board(context, message.chat_id, state, board)
        else:
            await _show_board(context, message, state, board)

    await runtime.conversations.save(state)


async def _resolve_board(
    state: ConversationState,
    reply: AgentReply,
    services: ServiceContainer,
    teacher_id: int,
    prior_session_id: int | None,
) -> tuple[AttendanceSessionRead | None, bool]:
    """Decide whether the attendance board needs drawing or refreshing.

    Runs inside the unit of work, because reading the session state is a
    database query; the actual sending happens after the transaction commits.

    Args:
        state: Live conversation state, already updated by the agent.
        reply: What the agent produced this turn.
        services: Service container bound to the current transaction.
        teacher_id: Owner of the data.
        prior_session_id: Session in focus *before* the turn ran.

    Returns:
        The session to render (or ``None``), and whether the session has ended.
    """
    session = reply.emitted.get(EMIT_ATTENDANCE_SESSION)
    if isinstance(session, AttendanceSessionRead):
        return session, False

    if reply.emitted.get(EMIT_ATTENDANCE_CLOSED) and prior_session_id is not None:
        return await _safe_session_view(services, teacher_id, prior_session_id), True

    if (
        state.focus_session_id is not None
        and state.attendance_message_id is not None
        and set(reply.tool_calls) & _ATTENDANCE_TOOLS
    ):
        return await _safe_session_view(services, teacher_id, state.focus_session_id), False

    return None, False


async def _safe_session_view(
    services: ServiceContainer, teacher_id: int, session_id: int
) -> AttendanceSessionRead | None:
    """Load a session for rendering, tolerating one that has gone away."""
    try:
        return await services.attendance.get_session_view(teacher_id, session_id)
    except AppError as exc:
        logger.info("Attendance board not refreshed", extra={"reason": exc.code})
        return None


async def _show_board(
    context: ContextTypes.DEFAULT_TYPE,
    message: Message,
    state: ConversationState,
    session: AttendanceSessionRead,
) -> None:
    """Draw the board, editing the existing one when possible."""
    state.focus_class_id = session.class_id
    state.focus_session_id = session.session_id

    if state.attendance_message_id is not None:
        refreshed = await refresh_attendance_board(
            context.bot,
            state.chat_id,
            state.attendance_message_id,
            session,
        )
        if refreshed:
            return

    posted = await send_attendance_board(message, session)  # type: ignore[arg-type]
    state.attendance_message_id = posted.message_id


async def _close_board(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    state: ConversationState,
    session: AttendanceSessionRead,
) -> None:
    """Strip the buttons from a board whose session has ended."""
    if state.attendance_message_id is not None:
        await refresh_attendance_board(
            context.bot,
            chat_id,
            state.attendance_message_id,
            session,
            keep_keyboard=False,
        )
    state.clear_attendance_focus()
