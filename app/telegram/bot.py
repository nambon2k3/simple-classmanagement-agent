"""Telegram application assembly.

Builds the ``python-telegram-bot`` application, registers handlers and exposes
the two ways of receiving updates: long polling for local development and a
webhook fed by the FastAPI app for production.
"""

from __future__ import annotations

from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.telegram.handlers import (
    attendance_command,
    classes_command,
    handle_attendance_callback,
    handle_error,
    handle_message,
    help_command,
    reset_command,
    start_command,
)
from app.telegram.keyboards import ATTENDANCE_PREFIX, NOOP_DATA
from app.telegram.runtime import RUNTIME_KEY, BotRuntime, install_runtime
from telegram import BotCommand

logger = get_logger(__name__)

#: Command menu shown by Telegram's UI.
BOT_COMMANDS: tuple[BotCommand, ...] = (
    BotCommand("start", "Welcome message"),
    BotCommand("help", "What I can do"),
    BotCommand("classes", "List your classes"),
    BotCommand("attendance", "Show the open attendance session"),
    BotCommand("reset", "Clear our conversation context"),
)

#: How often expired conversations are swept out of memory.
_PURGE_INTERVAL_SECONDS = 300


def build_application(settings: Settings | None = None) -> Application:
    """Create and wire the Telegram application.

    Args:
        settings: Configuration providing the bot token.  Defaults to the
            process settings singleton.

    Returns:
        A configured application that has not been started yet.

    Raises:
        ValueError: If no bot token is configured.
    """
    settings = settings or get_settings()
    token = settings.telegram_bot_token.get_secret_value()
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set.")

    application = (
        ApplicationBuilder()
        .token(token)
        .rate_limiter(AIORateLimiter())
        .post_init(_on_startup)
        .build()
    )
    install_runtime(application, BotRuntime.create(settings))
    _register_handlers(application)
    return application


def _register_handlers(application: Application) -> None:
    """Attach every handler in priority order."""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("classes", classes_command))
    application.add_handler(CommandHandler("attendance", attendance_command))
    application.add_handler(CommandHandler("reset", reset_command))

    application.add_handler(
        CallbackQueryHandler(
            handle_attendance_callback,
            pattern=rf"^({ATTENDANCE_PREFIX}:|{NOOP_DATA}$)",
        )
    )

    # Everything else that is plain text goes to the assistant.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_error_handler(handle_error)


async def _on_startup(application: Application) -> None:
    """Publish the command menu and schedule conversation clean-up."""
    await application.bot.set_my_commands(BOT_COMMANDS)

    if application.job_queue is not None:
        application.job_queue.run_repeating(
            _purge_conversations,
            interval=_PURGE_INTERVAL_SECONDS,
            first=_PURGE_INTERVAL_SECONDS,
            name="purge-conversations",
        )
    else:  # pragma: no cover - only when the job-queue extra is absent
        logger.warning("Job queue unavailable; expired conversations will not be purged")

    logger.info("Telegram application ready")


async def _purge_conversations(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Drop conversations that have been idle past their TTL."""
    runtime = context.application.bot_data.get(RUNTIME_KEY)
    if isinstance(runtime, BotRuntime):
        await runtime.conversations.purge_expired()
