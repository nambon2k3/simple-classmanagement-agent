"""Telegram update handlers.

Handlers are intentionally thin: they translate an update into a service or
agent call and render the result.  No business rule lives in this package.
"""

from app.telegram.handlers.callbacks import handle_attendance_callback
from app.telegram.handlers.commands import (
    attendance_command,
    classes_command,
    help_command,
    reset_command,
    start_command,
)
from app.telegram.handlers.errors import handle_error
from app.telegram.handlers.messages import handle_message

__all__ = [
    "attendance_command",
    "classes_command",
    "handle_attendance_callback",
    "handle_error",
    "handle_message",
    "help_command",
    "reset_command",
    "start_command",
]
