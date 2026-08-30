"""Application entry point.

One process runs the FastAPI app serving the JSON API, the AI chat endpoint,
and the administrator dashboard.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.errors import register_exception_handlers
from app.api.routes import admin_router, health_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging, get_logger
from app.database.session import get_database

logger = get_logger(__name__)

_STATIC_DIR = Path(__file__).resolve().parent / "web" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Start and stop the database alongside the HTTP server."""
    settings = get_settings()
    configure_logging(settings)
    logger.info("Starting %s", settings.app_name, extra={"environment": settings.environment})

    try:
        yield
    finally:
        await get_database().dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application.

    Args:
        settings: Configuration to use.  Defaults to the process singleton.

    Returns:
        The configured application.
    """
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        summary="AI-powered assistant for classroom management.",
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None,
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(admin_router)
    register_exception_handlers(app)

    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
    _register_html_routes(app)

    return app


#: In-page class channels that map to ``/classes/{id}/{channel}``.
_CLASS_CHANNELS = frozenset({"students", "attendance", "reports", "info"})


def _dashboard_shell() -> FileResponse:
    """Return the single-page dashboard HTML."""
    return FileResponse(_STATIC_DIR / "index.html")


def _register_html_routes(app: FastAPI) -> None:
    """Serve the dashboard shell for UI paths so F5 keeps the current view.

    ``/api`` and ``/static`` are already mounted and are not handled here.
    """

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        """Home dashboard."""
        return _dashboard_shell()

    @app.get("/chat", include_in_schema=False)
    async def chat_page() -> FileResponse:
        """AI chat."""
        return _dashboard_shell()

    @app.get("/classes/{class_id}/{channel}", include_in_schema=False)
    async def class_page(class_id: int, channel: str) -> FileResponse:
        """A class channel (students, attendance, reports, info)."""
        if channel not in _CLASS_CHANNELS:
            return FileResponse(_STATIC_DIR / "index.html", status_code=404)
        return _dashboard_shell()


app = create_app()
