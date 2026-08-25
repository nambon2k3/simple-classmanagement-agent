"""Application entry point.

One process runs both the FastAPI app and the Telegram bot.  Which transport
the bot uses is configuration, not code:

* ``TELEGRAM_MODE=polling`` — the bot pulls updates itself.  Best for local
  development, since it needs no public URL.
* ``TELEGRAM_MODE=webhook`` — Telegram posts updates to ``/telegram/webhook``
  and the route enqueues them for the same application.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from telegram.ext import Application

from app.api.errors import register_exception_handlers
from app.api.routes import admin_router, health_router, webhook_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging, get_logger
from app.database.session import get_database
from app.telegram.bot import build_application
from telegram import Update

logger = get_logger(__name__)

#: Directory holding the compiled-free HTML/CSS/JS administrator dashboard.
_STATIC_DIR = Path(__file__).resolve().parent / "web" / "static"


async def _start_bot(settings: Settings) -> Application:
    """Start the Telegram application in the configured mode.

    Raises:
        ValueError: If webhook mode is selected without a public URL.
    """
    application = build_application(settings)
    await application.initialize()
    await application.start()

    if settings.telegram_mode == "polling":
        await application.updater.start_polling(  # type: ignore[union-attr]
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        logger.info("Telegram bot started in polling mode")
        return application

    if not settings.telegram_webhook_url:
        raise ValueError("TELEGRAM_WEBHOOK_URL is required when TELEGRAM_MODE=webhook.")

    secret = settings.telegram_webhook_secret
    await application.bot.set_webhook(
        url=settings.telegram_webhook_url,
        secret_token=secret.get_secret_value() if secret else None,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
    logger.info(
        "Telegram bot started in webhook mode", extra={"url": settings.telegram_webhook_url}
    )
    return application


async def _stop_bot(application: Application) -> None:
    """Shut the Telegram application down cleanly."""
    updater = application.updater
    if updater is not None and updater.running:
        await updater.stop()
    if application.running:
        await application.stop()
    await application.shutdown()
    logger.info("Telegram bot stopped")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Start and stop the bot and database alongside the HTTP server."""
    settings = get_settings()
    configure_logging(settings)
    logger.info("Starting %s", settings.app_name, extra={"environment": settings.environment})

    application: Application | None = None
    try:
        application = await _start_bot(settings)
        app.state.telegram = application
    except Exception:
        # A missing token should not stop the HTTP server: health checks and
        # migrations still need to work so the failure is visible and fixable.
        logger.exception("Telegram bot failed to start; HTTP API will run without it")
        app.state.telegram = None

    try:
        yield
    finally:
        if application is not None:
            await _stop_bot(application)
        await get_database().dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application.

    Args:
        settings: Configuration to use.  Defaults to the process singleton.

    Returns:
        The configured application.
    """
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        summary="AI-powered Telegram assistant for classroom management.",
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None,
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(webhook_router)
    app.include_router(admin_router)
    register_exception_handlers(app)

    # The single-page dashboard is served from the same process as the API, so
    # a browser hitting "/" gets the UI and its fetch() calls stay same-origin.
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        """Serve the administrator dashboard shell."""
        return FileResponse(_STATIC_DIR / "index.html")

    return app


app = create_app()
