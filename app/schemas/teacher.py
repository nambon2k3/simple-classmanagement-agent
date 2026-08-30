"""Teacher read models."""

from __future__ import annotations

from pydantic import Field

from app.schemas.common import ToolOutput


class TeacherRead(ToolOutput):
    """A teacher account as exposed by the API."""

    id: int = Field(description="Internal teacher identifier.")
    telegram_id: int = Field(description="External user id of the teacher.")
    full_name: str = Field(description="Teacher's display name.")
    username: str | None = Field(default=None, description="Username, if set.")
    is_active: bool = Field(default=True, description="Whether the account is active.")


class TeacherIdentity(ToolOutput):
    """The minimal identity used to onboard a teacher."""

    telegram_id: int = Field(description="External user id.")
    full_name: str = Field(description="Display name.")
    username: str | None = Field(default=None, description="Username, if set.")
    language_code: str | None = Field(default=None, description="UI language code.")
