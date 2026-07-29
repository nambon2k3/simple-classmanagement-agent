"""Tests for class tool input aliases."""

from app.schemas.classroom import ClassInfoInput, CreateClassInput, DeleteClassInput


def test_get_class_info_accepts_class_name_alias():
    payload = ClassInfoInput.model_validate({"class_name": "SE1734"})
    assert payload.name == "SE1734"


def test_create_class_accepts_class_name_alias():
    payload = CreateClassInput.model_validate({"class_name": "SE401"})
    assert payload.name == "SE401"


def test_delete_class_accepts_class_name_alias():
    payload = DeleteClassInput.model_validate({"class_name": "SE401", "confirm": True})
    assert payload.name == "SE401"
