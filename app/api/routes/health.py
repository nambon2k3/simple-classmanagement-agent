"""Health and readiness endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.database.session import get_session

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class LivenessResponse(BaseModel):
    """Reply to a liveness probe."""

    status: str = Field(description="Always 'ok' when the process is running.")
    app: str = Field(description="Application name.")
    environment: str = Field(description="Deployment environment.")


class ReadinessResponse(BaseModel):
    """Reply to a readiness probe."""

    status: str = Field(description="'ok' when every dependency is reachable.")
    database: bool = Field(description="Whether the database answered a trivial query.")


@router.get("/live", response_model=LivenessResponse)
async def liveness(
    settings: Annotated[Settings, Depends(get_settings)],
) -> LivenessResponse:
    """Report that the process is up.

    Deliberately dependency-free: an orchestrator must not restart a healthy
    process just because the database is briefly unavailable.
    """
    return LivenessResponse(status="ok", app=settings.app_name, environment=settings.environment)


@router.get("/ready", response_model=ReadinessResponse)
async def readiness(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReadinessResponse:
    """Report whether the service can actually serve traffic."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Readiness probe failed to reach the database")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(status="degraded", database=False)
    return ReadinessResponse(status="ok", database=True)
