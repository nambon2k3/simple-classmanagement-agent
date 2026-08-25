"""Class rail avatar helpers."""

from __future__ import annotations

import pytest

from app.utils.class_icons import class_icon_data_uri, class_initials, save_class_icon


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


def test_save_and_load_class_icon(tmp_path) -> None:
    save_class_icon(7, "icon.png", b"\x89PNG", directory=tmp_path)
    uri = class_icon_data_uri(7, directory=tmp_path)
    assert uri is not None
    assert uri.startswith("data:image/png;base64,")
    assert class_icon_data_uri(8, directory=tmp_path) is None


def test_save_class_icon_rejects_unknown_type(tmp_path) -> None:
    with pytest.raises(ValueError, match="PNG"):
        save_class_icon(1, "icon.txt", b"hello", directory=tmp_path)
