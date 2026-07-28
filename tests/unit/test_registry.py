"""Tests for the tool registry — the validation boundary around the model."""

from __future__ import annotations

import pytest
from pydantic import Field

from app.ai.tools.registry import ToolContext, ToolRegistry
from app.core.exceptions import ClassNotFoundError
from app.schemas.common import OperationResult, ToolInput


class EchoInput(ToolInput):
    text: str = Field(description="Anything.")
    count: int = Field(default=1, description="How many times.")


class EchoOutput(OperationResult):
    echoed: str = Field(description="The echoed text.")


async def echo(_: ToolContext, payload: EchoInput) -> EchoOutput:
    return EchoOutput(message="ok", echoed=payload.text * payload.count)


async def explode(_: ToolContext, __: EchoInput) -> EchoOutput:
    raise ClassNotFoundError("No such class.", available_classes=["SE401"])


async def crash(_: ToolContext, __: EchoInput) -> EchoOutput:
    raise RuntimeError("a bug nobody expected")


@pytest.fixture
def registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register("echo", "Echo text back.", EchoInput, echo)
    reg.register("explode", "Always raises a domain error.", EchoInput, explode)
    reg.register("crash", "Always raises an unexpected error.", EchoInput, crash)
    return reg


@pytest.fixture
def context() -> ToolContext:
    return ToolContext(teacher_id=1, services=None)


async def test_successful_call_returns_the_output_model(registry, context):
    result = await registry.execute("echo", '{"text": "hi", "count": 2}', context)
    assert result == {"success": True, "message": "ok", "echoed": "hihi"}


async def test_arguments_may_be_a_dict(registry, context):
    result = await registry.execute("echo", {"text": "yo"}, context)
    assert result["echoed"] == "yo"


async def test_unknown_tool_is_reported_not_raised(registry, context):
    result = await registry.execute("teleport", "{}", context)
    assert result["success"] is False
    assert result["error"] == "tool_not_found"


async def test_invalid_json_is_reported_not_raised(registry, context):
    result = await registry.execute("echo", "{not json", context)
    assert result["error"] == "tool_input_error"


async def test_non_object_arguments_are_rejected(registry, context):
    result = await registry.execute("echo", "[1, 2, 3]", context)
    assert result["error"] == "tool_input_error"


async def test_missing_required_argument_is_reported(registry, context):
    result = await registry.execute("echo", "{}", context)
    assert result["error"] == "tool_input_error"
    assert "text" in result["message"]


async def test_unexpected_argument_is_rejected(registry, context):
    """``extra='forbid'`` means a hallucinated field fails loudly."""
    result = await registry.execute("echo", '{"text": "hi", "colour": "red"}', context)
    assert result["error"] == "tool_input_error"


async def test_domain_error_becomes_structured_output(registry, context):
    result = await registry.execute("explode", '{"text": "x"}', context)
    assert result["error"] == "class_not_found"
    assert result["message"] == "No such class."
    assert result["details"]["available_classes"] == ["SE401"]


async def test_unexpected_error_is_hidden_from_the_model(registry, context):
    result = await registry.execute("crash", '{"text": "x"}', context)
    assert result["error"] == "internal_error"
    assert "bug nobody expected" not in result["message"]


async def test_empty_arguments_string_is_treated_as_no_arguments(registry, context):
    result = await registry.execute("echo", "", context)
    assert result["error"] == "tool_input_error"  # 'text' is still required


def test_duplicate_registration_is_rejected(registry):
    with pytest.raises(ValueError, match="already registered"):
        registry.register("echo", "duplicate", EchoInput, echo)


def test_catalogue_lists_registered_names(registry):
    assert registry.names == ["echo", "explode", "crash"]
    assert {tool["name"] for tool in registry.to_openai_tools()} == set(registry.names)
