"""Data access for :class:`~app.models.teacher.Teacher`."""

from __future__ import annotations

from sqlalchemy import select

from app.models.teacher import Teacher
from app.repositories.base import BaseRepository


class TeacherRepository(BaseRepository[Teacher]):
    """Queries scoped to teacher accounts."""

    model = Teacher

    async def get_by_telegram_id(self, telegram_id: int) -> Teacher | None:
        """Look up the teacher behind a Telegram user id.

        Args:
            telegram_id: The Telegram account id of the sender.

        Returns:
            The matching teacher, or ``None`` if they have never used the bot.
        """
        return await self.session.scalar(select(Teacher).where(Teacher.telegram_id == telegram_id))
