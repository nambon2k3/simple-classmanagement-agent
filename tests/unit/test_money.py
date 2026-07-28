"""Tests for VND formatting."""

from app.utils.money import format_vnd


def test_format_vnd_uses_dot_thousands_separator():
    assert format_vnd(50_000) == "50.000 VND"
    assert format_vnd(1_250_000) == "1.250.000 VND"
    assert format_vnd(0) == "0 VND"
