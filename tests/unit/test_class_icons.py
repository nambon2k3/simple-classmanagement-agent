"""Class image helpers."""

from __future__ import annotations

import pytest

from app.utils.class_icons import class_initials, validate_class_image


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("SE401", "SE"),
        ("se401", "SE"),
        ("A", "A"),
        ("  math  ", "MA"),
        ("", "?"),
        ("   ", "?"),
    ],
)
def test_class_initials(name: str, expected: str) -> None:
    assert class_initials(name) == expected


def test_validate_class_image_accepts_png() -> None:
    assert validate_class_image("icon.png", b"\x89PNG") == "image/png"


def test_validate_class_image_rejects_unknown_type() -> None:
    with pytest.raises(ValueError, match="PNG"):
        validate_class_image("icon.txt", b"hello")


def test_validate_class_image_rejects_empty() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        validate_class_image("icon.png", b"")
