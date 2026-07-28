"""Global error handler.

Nothing that reaches here should ever be shown verbatim to a teacher.  Expected
domain failures carry a message that was written for them; anything else is
logged in full and replaced with a neutral apology.
"""

from __future__ import annotations

from telegram.error import Forbidden, NetworkError, TelegramError
from telegram.ext import ContextTypes

from app.core.exceptions import AppError, PermissionDeniedError
from app.core.logging import get_logger
from app.telegram.views import reply_html
from app.utils.text import truncate
from telegram import Update

logger = get_logger(__name__)

_GENERIC_APOLOGY = "😕 Something went wrong on my side. Please try again in a moment."


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log an unhandled exception and tell the teacher something useful."""
    error = context.error

    if isinstance(error, Forbidden):
        # The teacher blocked the bot; there is nobody left to apologise to.
        logger.info("Bot was blocked by the user")
        return
    if isinstance(error, NetworkError):
        logger.warning("Telegram network error", extra={"error": str(error)})
        return

    if isinstance(error, AppError):
        level = logger.info if isinstance(error, PermissionDeniedError) else logger.warning
        level("Domain error surfaced to handler", extra={"code": error.code})
        await _notify(update, f"⚠️ {truncate(error.message, 500)}")
        return

    logger.exception("Unhandled exception while processing an update", exc_info=error)
    await _notify(update, _GENERIC_APOLOGY)


async def _notify(update: object, text: str) -> None:
    """Best-effort reply to whoever triggered the failure."""
    if not isinstance(update, Update) or update.effective_message is None:
        return
    try:
        await reply_html(update.effective_message, text)
    except TelegramError:
        logger.info("Could not deliver the error message to the chat")
