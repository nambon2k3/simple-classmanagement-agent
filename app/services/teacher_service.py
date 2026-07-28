"""Teacher onboarding and authorisation."""

from __future__ import annotations

from app.core.config import Settings, get_settings
from app.core.exceptions import PermissionDeniedError
from app.core.logging import get_logger
from app.models.teacher import Teacher
from app.repositories.teacher_repository import TeacherRepository
from app.schemas.teacher import TeacherIdentity

logger = get_logger(__name__)


class TeacherService:
    """Maps a Telegram account onto a teacher record.

    This is the application's authentication boundary: every other service
    takes a ``teacher_id`` that originated here, which is what guarantees a
    teacher can only ever reach their own data.
    """

    def __init__(
        self,
        teacher_repository: TeacherRepository,
        settings: Settings | None = None,
    ) -> None:
        """Wire the service to its data source.

        Args:
            teacher_repository: Access to the ``teachers`` table.
            settings: Configuration holding the optional allow-list.
        """
        self._teachers = teacher_repository
        self._settings = settings or get_settings()

    async def get_or_create(self, identity: TeacherIdentity) -> Teacher:
        """Return the teacher for a Telegram user, creating them on first use.

        Profile fields are refreshed on every call so a renamed Telegram
        account does not go stale in the database.

        Raises:
            PermissionDeniedError: If an allow-list is configured and this user
                is not on it, or if the account has been deactivated.
        """
        self._assert_allowed(identity.telegram_id)

        teacher = await self._teachers.get_by_telegram_id(identity.telegram_id)
        if teacher is None:
            teacher = await self._teachers.add(
                Teacher(
                    telegram_id=identity.telegram_id,
                    full_name=identity.full_name,
                    username=identity.username,
                    language_code=identity.language_code,
                )
            )
            logger.info(
                "Teacher onboarded",
                extra={"teacher_id": teacher.id, "telegram_id": identity.telegram_id},
            )
            return teacher

        if not teacher.is_active:
            raise PermissionDeniedError("This account has been deactivated.")

        teacher.full_name = identity.full_name or teacher.full_name
        teacher.username = identity.username
        teacher.language_code = identity.language_code or teacher.language_code
        await self._teachers.flush()
        return teacher

    def _assert_allowed(self, telegram_id: int) -> None:
        """Enforce the optional allow-list from configuration."""
        allowed = self._settings.telegram_allowed_user_ids
        if allowed and telegram_id not in allowed:
            logger.warning("Rejected unlisted Telegram user", extra={"telegram_id": telegram_id})
            raise PermissionDeniedError(
                "This bot is private. Ask the administrator to grant you access."
            )
