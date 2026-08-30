"""HTTP translation of domain errors.

The API surface reuses the same exception hierarchy as the services, so a
service raising :class:`~app.core.exceptions.ClassNotFoundError` produces a
``404`` here and a friendly sentence in the chat, with no duplicated mapping
logic.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AmbiguousReferenceError,
    AppError,
    ConfirmationRequiredError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

#: Domain error category to HTTP status. Ordered most specific first, because
#: several of these classes inherit from one another.
_STATUS_BY_TYPE: tuple[tuple[type[AppError], int], ...] = (
    (ConfirmationRequiredError, status.HTTP_409_CONFLICT),
    (AmbiguousReferenceError, status.HTTP_409_CONFLICT),
    (NotFoundError, status.HTTP_404_NOT_FOUND),
    (ConflictError, status.HTTP_409_CONFLICT),
    (PermissionDeniedError, status.HTTP_403_FORBIDDEN),
    (ValidationError, status.HTTP_422_UNPROCESSABLE_CONTENT),
)


def http_status_for(error: AppError) -> int:
    """Map a domain error onto an HTTP status code."""
    for error_type, code in _STATUS_BY_TYPE:
        if isinstance(error, error_type):
            return code
    return status.HTTP_400_BAD_REQUEST


def register_exception_handlers(app: FastAPI) -> None:
    """Install the application-wide exception handlers."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        """Return a structured body for an expected domain failure."""
        return JSONResponse(status_code=http_status_for(exc), content=exc.to_dict())

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        """Log an unexpected failure and return an opaque 500."""
        logger.exception(
            "Unhandled error serving a request",
            extra={"path": request.url.path},
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred."},
        )
