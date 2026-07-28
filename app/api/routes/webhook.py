"""Telegram webhook endpoint.

Used when ``TELEGRAM_MODE=webhook``.  The route does the minimum amount of work
possible — authenticate, parse, enqueue — so Telegram gets its ``200`` quickly
and never retries an update that is already being processed.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.core.config import get_settings
from app.core.logging import get_logger
from telegram import Update

logger = get_logger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])

#: Header Telegram echoes back when a webhook secret is configured.
SECRET_HEADER = "X-Telegram-Bot-Api-Secret-Token"


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def telegram_webhook(
    request: Request,
    payload: dict[str, Any],
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    """Accept one update from Telegram and hand it to the bot application.

    Args:
        request: Used to reach the application state holding the bot.
        payload: The raw update body.
        x_telegram_bot_api_secret_token: Shared secret echoed by Telegram.

    Returns:
        A trivial acknowledgement.

    Raises:
        HTTPException: ``401`` when the secret does not match, ``503`` when the
            bot is not running in webhook mode.
    """
    settings = get_settings()
    expected = settings.telegram_webhook_secret

    if expected is not None:
        provided = x_telegram_bot_api_secret_token or ""
        if provided != expected.get_secret_value():
            logger.warning("Rejected webhook call with a bad secret token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid secret token."
            )

    application = getattr(request.app.state, "telegram", None)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The bot is not accepting webhook updates.",
        )

    update = Update.de_json(payload, application.bot)
    if update is None:
        logger.info("Discarded an unparseable webhook payload")
        return {"status": "ignored"}

    # Queue rather than await: processing can involve a model round trip, and
    # Telegram re-sends any update it does not see acknowledged quickly.
    await application.update_queue.put(update)
    return {"status": "queued"}
