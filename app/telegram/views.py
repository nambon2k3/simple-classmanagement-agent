"""Message-sending helpers shared by the Telegram handlers.

Keeping the send calls here means the handlers stay declarative, and the two
awkward realities of the Telegram API — fragile Markdown parsing and
``edit_message`` failing when nothing changed — are each handled in one place.
"""

from __future__ import annotations

from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ExtBot

from app.core.logging import get_logger
from app.schemas.attendance import AttendanceSessionRead
from app.telegram.formatting import clip, render_attendance_session
from app.telegram.keyboards import build_attendance_keyboard, clamp_page
from telegram import LinkPreviewOptions, Message

logger = get_logger(__name__)

_NO_PREVIEW = LinkPreviewOptions(is_disabled=True)

#: Telegram raises this when an edit would leave the message unchanged; it is
#: an expected outcome of a double tap, not an error worth reporting.
_UNCHANGED = "message is not modified"


async def reply_assistant_text(message: Message, text: str) -> Message:
    """Send free text written by the language model.

    Attempts Markdown first because the model formats its replies, and falls
    back to plain text if the markup is unbalanced.  Escaping the text instead
    would show the teacher literal asterisks.

    Args:
        message: Message to reply to.
        text: The model's reply.

    Returns:
        The sent message.
    """
    body = clip(text)
    try:
        return await message.reply_text(
            body, parse_mode=ParseMode.MARKDOWN, link_preview_options=_NO_PREVIEW
        )
    except BadRequest:
        logger.info("Falling back to plain text; model output was not valid Markdown")
        return await message.reply_text(body, link_preview_options=_NO_PREVIEW)


async def reply_html(message: Message, text: str) -> Message:
    """Send a message this application composed, using HTML formatting."""
    return await message.reply_text(
        clip(text), parse_mode=ParseMode.HTML, link_preview_options=_NO_PREVIEW
    )


async def send_attendance_board(
    message: Message, session: AttendanceSessionRead, page: int = 0
) -> Message:
    """Post the interactive attendance board as a new message.

    Args:
        message: Message to reply to.
        session: Current session state.
        page: Roster page to show first.

    Returns:
        The sent message, whose id the caller should remember so the board can
        later be edited in place.
    """
    page = clamp_page(page, len(session.entries))
    return await message.reply_text(
        render_attendance_session(session),
        parse_mode=ParseMode.HTML,
        reply_markup=build_attendance_keyboard(session, page),
        link_preview_options=_NO_PREVIEW,
    )


async def refresh_attendance_board(
    bot: ExtBot,
    chat_id: int,
    message_id: int,
    session: AttendanceSessionRead,
    page: int = 0,
    *,
    keep_keyboard: bool = True,
) -> bool:
    """Update an existing attendance board in place.

    Args:
        bot: Bot used to perform the edit.
        chat_id: Chat containing the board.
        message_id: Message to edit.
        session: New session state to render.
        page: Roster page to show.
        keep_keyboard: ``False`` removes the buttons, which is what a finished
            or cancelled session wants.

    Returns:
        ``True`` if the message was updated, ``False`` if the edit was a no-op
        or the message could no longer be edited.
    """
    page = clamp_page(page, len(session.entries))
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=render_attendance_session(session),
            parse_mode=ParseMode.HTML,
            reply_markup=build_attendance_keyboard(session, page) if keep_keyboard else None,
            link_preview_options=_NO_PREVIEW,
        )
    except BadRequest as exc:
        if _UNCHANGED in str(exc).lower():
            return False
        logger.info("Could not refresh attendance board", extra={"reason": str(exc)})
        return False
    return True
