"""HTTP surface: health probes, the webhook receiver and error mapping."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.errors import http_status_for
from app.core.exceptions import (
    AmbiguousStudentError,
    AppError,
    ClassAlreadyExistsError,
    ClassNotFoundError,
    ConfirmationRequiredError,
    EmptyClassError,
    PermissionDeniedError,
)


@pytest.fixture
async def client(database) -> AsyncIterator[AsyncClient]:
    """An HTTP client bound to the app without running its lifespan.

    Skipping the lifespan keeps the tests offline: no bot is started and no
    Telegram or Groq credentials are needed.
    """
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http:
        yield http


async def test_liveness_does_not_depend_on_the_database(client):
    response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_readiness_checks_the_database(client):
    response = await client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": True}


async def test_webhook_is_unavailable_when_the_bot_is_not_running(client):
    response = await client.post("/telegram/webhook", json={"update_id": 1})
    assert response.status_code == 503


async def test_webhook_rejects_a_bad_secret_token(client, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "the-real-secret")
    get_settings.cache_clear()
    try:
        response = await client.post(
            "/telegram/webhook",
            json={"update_id": 1},
            headers={"X-Telegram-Bot-Api-Secret-Token": "not-the-secret"},
        )
        assert response.status_code == 401
    finally:
        get_settings.cache_clear()


async def test_openapi_document_is_served(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/health/live" in paths
    assert "/telegram/webhook" in paths


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (ClassNotFoundError(), 404),
        (ClassAlreadyExistsError(), 409),
        (ConfirmationRequiredError(), 409),
        (AmbiguousStudentError(), 409),
        (PermissionDeniedError(), 403),
        (EmptyClassError(), 422),
        (AppError(), 400),
    ],
)
def test_domain_errors_map_to_sensible_status_codes(error: AppError, expected: int):
    assert http_status_for(error) == expected


def test_error_serialisation_is_safe_to_return(client):
    error = ClassNotFoundError("No class named GHOST.", available_classes=["SE401"])
    assert error.to_dict() == {
        "error": "class_not_found",
        "message": "No class named GHOST.",
        "details": {"available_classes": ["SE401"]},
    }
