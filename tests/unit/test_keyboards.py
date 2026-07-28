"""Tests for the attendance keyboard and its callback-data codec."""

from __future__ import annotations

import pytest

from app.models.enums import AttendanceSessionStatus, AttendanceStatus
from app.schemas.attendance import AttendanceEntry, AttendanceSessionRead, AttendanceSummary
from app.telegram.keyboards import (
    PAGE_SIZE,
    CallbackParseError,
    build_attendance_keyboard,
    clamp_page,
    encode_mark,
    encode_page,
    encode_simple,
    page_count,
    parse_attendance_callback,
)
from app.utils.datetime_utils import today


def make_session(student_count: int) -> AttendanceSessionRead:
    entries = [
        AttendanceEntry(
            student_id=index,
            student_code=f"SE{index:03d}",
            full_name=f"Student Number {index}",
            status=None,
        )
        for index in range(1, student_count + 1)
    ]
    return AttendanceSessionRead(
        session_id=99,
        class_id=7,
        class_name="SE401",
        session_date=today(),
        status=AttendanceSessionStatus.OPEN,
        entries=entries,
        summary=AttendanceSummary(total=student_count, unmarked=student_count),
    )


@pytest.mark.parametrize("status", list(AttendanceStatus))
def test_mark_callback_round_trips(status: AttendanceStatus):
    decoded = parse_attendance_callback(encode_mark(12, 34, status, 2))
    assert decoded.action == "mark"
    assert decoded.session_id == 12
    assert decoded.student_id == 34
    assert decoded.status is status
    assert decoded.page == 2


def test_page_callback_round_trips():
    decoded = parse_attendance_callback(encode_page(5, 3))
    assert (decoded.action, decoded.session_id, decoded.page) == ("page", 5, 3)


@pytest.mark.parametrize("action", ["rest", "done", "cancel"])
def test_simple_callbacks_round_trip(action: str):
    decoded = parse_attendance_callback(encode_simple(action, 8, 1))
    assert (decoded.action, decoded.session_id, decoded.page) == (action, 8, 1)


@pytest.mark.parametrize(
    "payload",
    ["", "nonsense", "att:", "att:mark:1", "att:mark:1:2:z:0", "other:done:1:0", "att:fly:1:0"],
)
def test_malformed_callbacks_are_rejected(payload: str):
    with pytest.raises(CallbackParseError):
        parse_attendance_callback(payload)


def test_callback_data_fits_telegram_limit():
    """Telegram silently drops callback data longer than 64 bytes."""
    payload = encode_mark(9_223_372_036_854, 9_223_372_036_854, AttendanceStatus.EXCUSED, 999)
    assert len(payload.encode()) <= 64


def test_page_count_and_clamping():
    assert page_count(0) == 1
    assert page_count(PAGE_SIZE) == 1
    assert page_count(PAGE_SIZE + 1) == 2
    assert clamp_page(-5, 10) == 0
    assert clamp_page(99, 10) == page_count(10) - 1


def test_keyboard_shows_one_row_per_student_plus_actions():
    keyboard = build_attendance_keyboard(make_session(3)).inline_keyboard
    # 3 student rows, no pagination row (single page), rest/finish row, cancel row.
    assert len(keyboard) == 5
    assert len(keyboard[0]) == 4  # label + present/absent/late


def test_keyboard_paginates_large_rosters():
    session = make_session(PAGE_SIZE * 2 + 1)
    keyboard = build_attendance_keyboard(session, page=1).inline_keyboard
    student_rows = [row for row in keyboard if len(row) == 4]
    assert len(student_rows) == PAGE_SIZE
    labels = [row[1].callback_data for row in student_rows]
    assert all(data[-2:] == ":1" for data in labels)  # page is encoded in the payload


def test_keyboard_reflects_recorded_statuses():
    session = make_session(2)
    session.entries[0].status = AttendanceStatus.ABSENT
    keyboard = build_attendance_keyboard(session).inline_keyboard
    assert keyboard[0][0].text.startswith(AttendanceStatus.ABSENT.emoji)
    assert keyboard[1][0].text.startswith("⬜")
