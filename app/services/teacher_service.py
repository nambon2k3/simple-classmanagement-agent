"""Teacher onboarding and authorisation."""

from __future__ import annotations

from app.core.config import Settings, get_settings
from app.core.exceptions import PermissionDeniedError
from app.core.logging import get_logger
from app.models.teacher import Teacher
from app.repositories.teacher_repository import TeacherRepository
from app.schemas.teacher import TeacherIdentity

logger = get_logger(__name__)

#: Sentinel ``telegram_id`` for a local administrator created by the web
#: dashboard when the database has no teachers yet.
LOCAL_ADMIN_TELEGRAM_ID = 0


class TeacherService:
    """Ownership boundary for teacher accounts.

    The web dashboard uses :meth:`ensure_administrator`, which attaches to an
    existing teacher or creates a local admin.  :meth:`get_or_create` is the
    general-purpose onboarding path used by tests and external integrations.
    """

    def __init__(
        self,
        teacher_repository: TeacherRepository,
        settings: Settings | None = None,
    ) -> None:
        """Wire the service to its data source.

        Args:
            teacher_repository: Access to the ``teachers`` table.
            settings: Configuration.
        """
        self._teachers = teacher_repository
        self._settings = settings or get_settings()

    async def get_or_create(self, identity: TeacherIdentity) -> Teacher:
        """Return the teacher for an identity, creating them on first use.

        Profile fields are refreshed on every call so a renamed account does
        not go stale in the database.

        Raises:
            PermissionDeniedError: If the account has been deactivated.
        """
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

    async def ensure_administrator(self) -> Teacher:
        """Return the teacher the web dashboard should operate as.

        Prefers the earliest active teacher so existing classes created during
        a previous session stay in view.  When the table is empty, creates a
        local administrator.
        """
        existing = [row for row in await self._teachers.list_all() if row.is_active]
        if existing:
            return min(existing, key=lambda row: row.id)

        teacher = await self._teachers.add(
            Teacher(
                telegram_id=LOCAL_ADMIN_TELEGRAM_ID,
                full_name="Administrator",
                username="admin",
            )
        )
        logger.info("Local administrator created", extra={"teacher_id": teacher.id})
        return teacher
