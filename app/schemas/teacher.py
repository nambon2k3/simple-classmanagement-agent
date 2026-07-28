"""Teacher read models."""

from __future__ import annotations

from pydantic import Field

from app.schemas.common import ToolOutput


class TeacherRead(ToolOutput):
    """A teacher account as exposed by the API."""

    id: int = Field(description="Internal teacher identifier.")
    telegram_id: int = Field(description="Telegram user id of the teacher.")
    full_name: str = Field(description="Teacher's display name.")
    username: str | None = Field(default=None, description="Telegram username, if set.")
    is_active: bool = Field(default=True, description="Whether the account may use the bot.")


class TeacherIdentity(ToolOutput):
    """The minimal identity used to onboard a teacher from a Telegram update."""

    telegram_id: int = Field(description="Telegram user id.")
    full_name: str = Field(description="Name taken from the Telegram profile.")
    username: str | None = Field(default=None, description="Telegram username, if set.")
    language_code: str | None = Field(default=None, description="Telegram UI language code.")
