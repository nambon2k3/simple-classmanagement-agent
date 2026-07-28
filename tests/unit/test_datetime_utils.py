"""Tests for date parsing and range helpers."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.utils.datetime_utils import (
    format_date,
    month_bounds,
    parse_date,
    today,
    week_bounds,
)


def test_parse_iso_date():
    assert parse_date("2026-03-14") == date(2026, 3, 14)


def test_parse_relative_keywords():
    assert parse_date("today") == today()
    assert parse_date("yesterday") == today() - timedelta(days=1)
    assert parse_date("tomorrow") == today() + timedelta(days=1)


def test_parse_none_defaults_to_today():
    assert parse_date(None) == today()


def test_parse_none_can_be_rejected():
    with pytest.raises(ValueError, match="date is required"):
        parse_date(None, default_to_today=False)


def test_parse_passes_through_date_objects():
    value = date(2026, 1, 1)
    assert parse_date(value) is value


def test_parse_rejects_nonsense():
    with pytest.raises(ValueError, match="Could not understand"):
        parse_date("next tuesday-ish")


def test_week_bounds_span_monday_to_sunday():
    start, end = week_bounds(date(2026, 3, 18))  # a Wednesday
    assert start == date(2026, 3, 16)
    assert end == date(2026, 3, 22)
    assert start.weekday() == 0
    assert (end - start).days == 6


def test_month_bounds_handle_february():
    start, end = month_bounds(date(2026, 2, 14))
    assert start == date(2026, 2, 1)
    assert end == date(2026, 2, 28)


def test_month_bounds_handle_december():
    start, end = month_bounds(date(2026, 12, 5))
    assert start == date(2026, 12, 1)
    assert end == date(2026, 12, 31)


def test_format_date_is_human_readable():
    assert format_date(date(2026, 7, 27)) == "Mon 27 Jul 2026"
