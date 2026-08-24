"""Centralised application configuration.

All runtime configuration is read from environment variables (or a local
``.env`` file) exactly once and exposed through the cached :func:`get_settings`
accessor.  Nothing else in the codebase is allowed to read ``os.environ``
directly, which keeps configuration testable and makes every tunable knob
discoverable from a single place.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "development", "staging", "production"]
TelegramMode = Literal["polling", "webhook"]


class Settings(BaseSettings):
    """Strongly typed application settings.

    Attributes are populated from environment variables using the field name in
    upper case (for example ``telegram_bot_token`` reads ``TELEGRAM_BOT_TOKEN``).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ----------------------------------------------------------------- app --
    app_name: str = "Class Management Assistant"
    environment: Environment = "local"
    debug: bool = False
    log_level: str = "INFO"
    log_json: bool = False

    #: IANA timezone used to resolve "today" for attendance sessions and
    #: reports.  Attendance is a human, local-time concept, so this must not be
    #: hardcoded to UTC.
    timezone: str = "UTC"

    # ------------------------------------------------------------ database --
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/class_management"
    db_echo: bool = False
    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=10, ge=0)
    db_pool_pre_ping: bool = True

    # ------------------------------------------------------------ telegram --
    telegram_bot_token: SecretStr = SecretStr("")
    telegram_mode: TelegramMode = "polling"
    telegram_webhook_url: str | None = None
    telegram_webhook_secret: SecretStr | None = None

    #: Optional allow-list of Telegram user ids.  When empty the bot onboards
    #: any user as a teacher, which is the sensible default for a single-school
    #: deployment.  Populate it to lock the bot down.
    telegram_allowed_user_ids: list[int] = Field(default_factory=list)

    # --------------------------------------------------------------- groq ----
    #: API key from https://console.groq.com/keys
    groq_api_key: SecretStr = SecretStr("")
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com"
    groq_timeout_seconds: float = Field(default=120.0, gt=0)
    groq_max_retries: int = Field(default=1, ge=0)
    groq_log_prompts: bool = False

    # --------------------------------------------------------- assistant ----
    #: How long a conversation (chat history + attendance focus) survives
    #: without activity before it is discarded.
    conversation_ttl_seconds: int = Field(default=1800, ge=60)
    #: Upper bound on sequential tool calls for a single user turn.  Prevents a
    #: misbehaving model from looping forever.
    max_tool_iterations: int = Field(default=8, ge=1, le=25)
    #: Maximum number of conversation items retained per chat.
    max_history_items: int = Field(default=40, ge=4)

    # ----------------------------------------------------------------- api --
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    @field_validator("database_url")
    @classmethod
    def _force_async_driver(cls, value: str) -> str:
        """Normalise a PostgreSQL DSN to the asyncpg driver.

        Deployment platforms hand out ``postgresql://`` URLs, but the
        application talks to the database asynchronously.  Rewriting here means
        callers never have to remember the ``+asyncpg`` suffix.
        """
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("groq_base_url")
    @classmethod
    def _normalize_groq_base_url(cls, value: str) -> str:
        """Normalise for the official Groq SDK (root URL only).

        The SDK appends ``/openai/v1`` itself.  Older configs used the full
        OpenAI-compatible path and ended up calling
        ``/openai/v1/openai/v1/chat/completions``.
        """
        value = value.strip().rstrip("/")
        if value.endswith("/openai/v1"):
            value = value[: -len("/openai/v1")].rstrip("/")
        return value or "https://api.groq.com"

    @field_validator("groq_model")
    @classmethod
    def _reject_classifier_models(cls, value: str) -> str:
        lowered = value.lower()
        if "prompt-guard" in lowered or "llama-guard" in lowered:
            raise ValueError(
                f"GROQ_MODEL={value!r} is a security classifier, not a chat assistant. "
                "Use llama-3.3-70b-versatile or llama-3.1-8b-instant for this bot."
            )
        return value

    @field_validator("timezone")
    @classmethod
    def _validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:  # pragma: no cover
            raise ValueError(f"Unknown IANA timezone: {value!r}") from exc
        return value

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, value: str) -> str:
        level = value.upper()
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
        if level not in allowed:
            raise ValueError(f"log_level must be one of {sorted(allowed)}")
        return level

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_database_url(self) -> str:
        """Blocking DSN, required by Alembic's migration runner."""
        return self.database_url.replace("+asyncpg", "")

    @property
    def tzinfo(self) -> ZoneInfo:
        """Resolved :class:`ZoneInfo` for :attr:`timezone`."""
        return ZoneInfo(self.timezone)

    @property
    def is_production(self) -> bool:
        """Whether the process is running in the production environment."""
        return self.environment == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings singleton.

    Cached so that ``.env`` parsing and validation happen once.  Tests can call
    ``get_settings.cache_clear()`` to pick up patched environment variables.
    """
    return Settings()
