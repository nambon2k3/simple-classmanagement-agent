"""Logging configuration.

Provides a single :func:`configure_logging` entry point so every process
(API server, bot worker, test run) emits logs in the same shape.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from app.core.config import Settings, get_settings

#: Third-party loggers that are far too chatty at INFO level.
_NOISY_LOGGERS: tuple[tuple[str, int], ...] = (
    ("httpx", logging.WARNING),
    ("httpcore", logging.WARNING),
    ("hpack", logging.WARNING),
    ("telegram.ext.Application", logging.INFO),
    ("apscheduler", logging.WARNING),
    ("aiosqlite", logging.WARNING),
)


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON for log aggregators."""

    _RESERVED = frozenset(logging.LogRecord("", 0, "", 0, "", None, None).__dict__)

    def format(self, record: logging.LogRecord) -> str:
        """Serialise a log record, merging in any ``extra`` fields."""
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # Anything attached via ``logger.info(..., extra={...})``.
        for key, value in record.__dict__.items():
            if key not in self._RESERVED and key not in payload and not key.startswith("_"):
                payload[key] = value
        return json.dumps(payload, default=str, ensure_ascii=False)


def configure_logging(settings: Settings | None = None) -> None:
    """Install the root log handler.

    Safe to call more than once; existing handlers are replaced so that
    reloads under ``uvicorn --reload`` do not duplicate output.

    Args:
        settings: Configuration to read the level and format from.  Defaults to
            the process settings singleton.
    """
    settings = settings or get_settings()

    handler = logging.StreamHandler(sys.stdout)
    if settings.log_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.log_level)

    for name, level in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger.

    Thin wrapper over :func:`logging.getLogger` that keeps import sites
    consistent and gives us one place to swap in structured logging later.
    """
    return logging.getLogger(name)
