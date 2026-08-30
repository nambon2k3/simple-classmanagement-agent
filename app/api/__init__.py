"""HTTP API: health probes and the administrator dashboard."""

from app.api.errors import register_exception_handlers
from app.api.routes import health_router

__all__ = ["health_router", "register_exception_handlers"]
