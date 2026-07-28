"""Telegram presentation layer.

Contains only transport concerns: update routing, keyboards, message rendering
and error presentation.  Business rules live in :mod:`app.services`.
"""

from app.telegram.bot import build_application
from app.telegram.runtime import BotRuntime, get_runtime

__all__ = ["BotRuntime", "build_application", "get_runtime"]
