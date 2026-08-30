"""HTTP surface: health probes and error mapping."""

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
from app.utils.datetime_utils import today


@pytest.fixture
async def client(database) -> AsyncIterator[AsyncClient]:
    """An HTTP client bound to the app without running its lifespan."""
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


async def test_openapi_document_is_served(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/health/live" in paths


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


async def test_class_image_round_trips_through_the_database(client):
    created = await client.post("/api/classes", json={"name": "SE401"})
    assert created.status_code == 201
    class_id = created.json()["classroom"]["id"]

    uploaded = await client.post(
        f"/api/classes/{class_id}/icon",
        content=b"\x89PNG",
        params={"filename": "icon.png"},
    )
    assert uploaded.status_code == 200

    listed = await client.get("/api/classes")
    assert listed.json()[0]["has_icon"] is True

    image = await client.get(f"/api/classes/{class_id}/icon")
    assert image.status_code == 200
    assert image.content == b"\x89PNG"
    assert image.headers["content-type"] == "image/png"


async def test_class_channel_url_serves_the_dashboard_shell(client):
    response = await client.get("/classes/1/students")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="app"' in response.text


async def test_chat_url_serves_the_dashboard_shell(client):
    response = await client.get("/chat")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="app"' in response.text


async def test_api_classes_still_returns_json(client):
    response = await client.get("/api/classes")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert isinstance(response.json(), list)


async def test_complete_teaching_day_and_calendar_completion(client):
    created = await client.post("/api/classes", json={"name": "SE401"})
    assert created.status_code == 201
    class_id = created.json()["classroom"]["id"]

    enrolled = await client.post(
        "/api/students",
        json={"class_name": "SE401", "full_name": "Nguyen Van A", "student_code": "SE001"},
    )
    assert enrolled.status_code == 201

    day = today()
    scheduled = await client.post(
        "/api/schedule/rule",
        json={
            "class_id": class_id,
            "weekday": day.weekday(),
            "start_time": "18:00:00",
            "end_time": "20:00:00",
        },
    )
    assert scheduled.status_code == 201

    before = await client.get("/api/dashboard/today")
    assert before.status_code == 200
    rows = before.json()
    assert len(rows) == 1
    assert rows[0]["class_id"] == class_id
    assert rows[0]["completed"] is False

    finished = await client.post("/api/attendance/complete-day", json={"class_id": class_id})
    assert finished.status_code == 200
    assert finished.json()["present"] == 1
    assert finished.json()["absent"] == 0

    after = await client.get("/api/dashboard/today")
    assert after.json()[0]["completed"] is True
    assert after.json()[0]["cancelled"] is False

    month = await client.get("/api/schedule/month", params={"year": day.year, "month": day.month})
    assert month.status_code == 200
    today_events = [item for item in month.json() if item["session_date"] == day.isoformat()]
    assert today_events
    assert all(item["completed"] is True for item in today_events)

    again = await client.post("/api/attendance/complete-day", json={"class_id": class_id})
    assert again.status_code == 409


async def test_cancel_teaching_day_marks_students_absent(client):
    created = await client.post("/api/classes", json={"name": "SE401"})
    assert created.status_code == 201
    class_id = created.json()["classroom"]["id"]

    enrolled = await client.post(
        "/api/students",
        json={"class_name": "SE401", "full_name": "Nguyen Van A", "student_code": "SE001"},
    )
    assert enrolled.status_code == 201

    day = today()
    scheduled = await client.post(
        "/api/schedule/rule",
        json={
            "class_id": class_id,
            "weekday": day.weekday(),
            "start_time": "18:00:00",
            "end_time": "20:00:00",
        },
    )
    assert scheduled.status_code == 201

    before = await client.get("/api/dashboard/today")
    assert before.json()[0]["cancelled"] is False

    cancelled = await client.post("/api/attendance/cancel-day", json={"class_id": class_id})
    assert cancelled.status_code == 200
    assert cancelled.json()["present"] == 0
    assert cancelled.json()["absent"] == 1

    after = await client.get("/api/dashboard/today")
    assert after.json()[0]["completed"] is True
    assert after.json()[0]["cancelled"] is True

    month = await client.get("/api/schedule/month", params={"year": day.year, "month": day.month})
    today_events = [item for item in month.json() if item["session_date"] == day.isoformat()]
    assert today_events
    assert all(item["cancelled"] is True for item in today_events)
