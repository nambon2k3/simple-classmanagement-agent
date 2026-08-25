"""Shared FastAPI dependencies for the administrator API.

The web UI operates as a single administrator, with no login.  This dependency
opens one unit of work per request, resolves the administrator teacher, and
commits (or rolls back) when the request ends.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends

from app.database.session import get_database
from app.models.teacher import Teacher
from app.services.container import ServiceContainer


async def admin_context() -> AsyncIterator[tuple[ServiceContainer, Teacher]]:
    """Yield the service container and administrator for one request.

    The surrounding :meth:`Database.session` context commits when the request
    handler returns normally and rolls back if it raises, so handlers never
    manage the transaction themselves.
    """
    async with get_database().session() as session:
        services = ServiceContainer(session=session)
        teacher = await services.teachers.ensure_administrator()
        yield services, teacher


#: Injected pair of the request-scoped services and the administrator teacher.
AdminContext = Annotated[tuple[ServiceContainer, Teacher], Depends(admin_context)]
