"""Tests for the Pydantic to JSON-schema converter used by LLM tools."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.ai.tools.definitions import build_registry
from app.ai.tools.schema import build_openai_tool_schema, build_tool_schema


class Colour(StrEnum):
    RED = "red"
    BLUE = "blue"


class Nested(BaseModel):
    depth: int = Field(description="How deep.")


class Sample(BaseModel):
    name: str = Field(description="Required name.")
    colour: Colour = Field(default=Colour.RED, description="A colour.")
    optional: str | None = Field(default=None, description="May be null.")
    nested: Nested | None = Field(default=None, description="A nested object.")


def test_every_property_is_required():
    schema = build_tool_schema(Sample)
    assert set(schema["required"]) == {"name", "colour", "optional", "nested"}


def test_llm_schema_omits_additional_properties():
    schema = build_tool_schema(Sample)
    assert "additionalProperties" not in schema
    nested = schema["properties"]["nested"]
    branches = nested.get("anyOf", [nested])
    objects = [branch for branch in branches if branch.get("type") == "object"]
    assert objects and all("additionalProperties" not in branch for branch in objects)


def test_openai_schema_disables_additional_properties():
    schema = build_openai_tool_schema(Sample)
    assert schema["additionalProperties"] is False
    nested = schema["properties"]["nested"]
    branches = nested.get("anyOf", [nested])
    objects = [branch for branch in branches if branch.get("type") == "object"]
    assert objects and all(branch["additionalProperties"] is False for branch in objects)


def test_defaults_are_stripped():
    schema = build_tool_schema(Sample)
    assert "default" not in schema["properties"]["colour"]


def test_enums_are_inlined_with_their_values():
    schema = build_tool_schema(Sample)
    assert schema["properties"]["colour"]["enum"] == ["red", "blue"]


def test_no_references_survive():
    rendered = repr(build_tool_schema(Sample))
    assert "$ref" not in rendered
    assert "$defs" not in rendered


def test_optional_is_expressed_as_a_null_union():
    schema = build_tool_schema(Sample)
    types = {branch["type"] for branch in schema["properties"]["optional"]["anyOf"]}
    assert types == {"string", "null"}


def test_empty_model_produces_a_valid_object_schema():
    class Empty(BaseModel):
        pass

    schema = build_tool_schema(Empty)
    assert schema == {
        "type": "object",
        "properties": {},
        "required": [],
        "title": "Empty",
    }


def test_every_registered_tool_produces_an_llm_schema():
    """Guards the whole catalogue, not just the sample model."""
    for tool in build_registry().to_function_declarations():
        assert tool["name"]
        assert tool["description"]
        _assert_llm(tool["parameters"], tool["name"])


def _assert_llm(node: object, path: str) -> None:
    if isinstance(node, dict):
        assert "$ref" not in node, path
        assert "default" not in node, path
        assert "allOf" not in node, path
        assert "additionalProperties" not in node, path
        if node.get("type") == "object":
            assert set(node["required"]) == set(node["properties"]), path
        for key, value in node.items():
            _assert_llm(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _assert_llm(value, f"{path}[{index}]")
