"""The recent-activity feed derived from audit timestamps."""

from __future__ import annotations

from app.schemas.activity import ActivityKind
from app.schemas.tuition import SetClassTuitionFeeInput
from app.utils.datetime_utils import today
from tests.integration.test_tuition import _finish_day


async def test_feed_is_empty_for_a_new_teacher(services, teacher):
    assert await services.activity.recent(teacher.id) == []


async def test_feed_reports_class_and_student_creation(services, teacher, roster, classroom):
    entries = await services.activity.recent(teacher.id)
    kinds = {entry.kind for entry in entries}

    assert ActivityKind.CLASS_CREATED in kinds
    assert ActivityKind.STUDENT_ADDED in kinds
    assert any("SE401 created" in entry.text for entry in entries)
    assert any(entry.text == "Nguyen Van A (SE001) enrolled in SE401" for entry in entries)


async def test_feed_reports_attendance_and_payments(services, teacher, roster, classroom):
    await services.tuition.set_class_tuition_fee(
        teacher.id, SetClassTuitionFeeInput(class_name="SE401", daily_tuition_fee=50_000)
    )
    await _finish_day(services, teacher, today(), statuses={"SE001": "present"})
    await services.tuition.mark_student_completed(teacher.id, classroom.id, roster[0].id)

    entries = await services.activity.recent(teacher.id, limit=30)
    kinds = {entry.kind for entry in entries}

    assert ActivityKind.ATTENDANCE_STARTED in kinds
    assert ActivityKind.ATTENDANCE_COMPLETED in kinds
    assert ActivityKind.TUITION_PAID in kinds
    payment = next(entry for entry in entries if entry.kind is ActivityKind.TUITION_PAID)
    assert "50.000 VND" in payment.text
    assert payment.class_name == "SE401"


async def test_feed_is_newest_first(services, teacher, roster):
    entries = await services.activity.recent(teacher.id, limit=30)
    timestamps = [entry.occurred_at for entry in entries]
    assert timestamps == sorted(timestamps, reverse=True)
