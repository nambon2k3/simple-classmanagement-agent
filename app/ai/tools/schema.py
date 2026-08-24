"""Convert Pydantic models into JSON schemas for LLM function tools.

Providers validate tool arguments against the schema they are given, but each
one accepts a slightly different JSON Schema subset.  This module narrows
Pydantic's output to a conservative form:

* ``$ref``/``$defs`` are inlined, so nested models and enums cannot trip over
  reference-resolution differences;
* ``required`` follows Pydantic — only fields without defaults are mandatory.
  Groq rejects tool calls when optional keys are listed in ``required`` but
  omitted by the model;
* ``additionalProperties`` is omitted because some providers reject it;
* validation keywords the API may reject (lengths, numeric bounds, formats) are
  dropped.

Dropping those keywords costs nothing, because the arguments are re-validated
against the real Pydantic model before any service is called; the schema is a
hint to the model, not the enforcement boundary.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

#: Keywords carried through to the API.  Anything else is discarded.
_ALLOWED_KEYWORDS = frozenset(
    {
        "type",
        "description",
        "enum",
        "properties",
        "items",
        "anyOf",
        "required",
        "title",
    }
)

#: OpenAI strict-mode schemas also allow this keyword.
_OPENAI_EXTRA_KEYWORDS = frozenset({"additionalProperties"})

#: Guard against a pathological or self-referential schema.
_MAX_DEPTH = 12


def build_tool_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Build a JSON schema for a tool's input model.

    Args:
        model: The Pydantic model describing the tool's arguments.

    Returns:
        A JSON schema object ready to be sent as function ``parameters``.
    """
    raw = model.model_json_schema(ref_template="#/$defs/{model}")
    definitions: dict[str, Any] = raw.pop("$defs", {})
    inlined = _inline_refs(raw, definitions, depth=0)
    return _strictify(inlined, depth=0)


def build_openai_tool_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Build a strict-mode JSON schema for legacy OpenAI tool definitions."""
    raw = model.model_json_schema(ref_template="#/$defs/{model}")
    definitions: dict[str, Any] = raw.pop("$defs", {})
    inlined = _inline_refs(raw, definitions, depth=0)
    return _strictify(inlined, depth=0, for_openai=True)


def _inline_refs(node: Any, definitions: dict[str, Any], *, depth: int) -> Any:
    """Replace every ``$ref`` with a copy of the definition it points at."""
    if depth > _MAX_DEPTH:
        return {"type": "object"}

    if isinstance(node, list):
        return [_inline_refs(item, definitions, depth=depth + 1) for item in node]
    if not isinstance(node, dict):
        return node

    if "$ref" in node:
        reference = str(node["$ref"]).removeprefix("#/$defs/")
        target = definitions.get(reference, {})
        merged = {**_inline_refs(target, definitions, depth=depth + 1)}
        # Siblings of ``$ref`` (typically ``description``) win over the target's
        # own values, matching JSON Schema 2020-12 semantics.
        for key, value in node.items():
            if key != "$ref":
                merged[key] = _inline_refs(value, definitions, depth=depth + 1)
        return merged

    return {key: _inline_refs(value, definitions, depth=depth + 1) for key, value in node.items()}


def _strictify(node: Any, *, depth: int, for_openai: bool = False) -> Any:
    """Prune to the allowed keyword subset and enforce object rules."""
    allowed = _ALLOWED_KEYWORDS | (_OPENAI_EXTRA_KEYWORDS if for_openai else frozenset())
    if depth > _MAX_DEPTH:
        return {"type": "object"}
    if isinstance(node, list):
        return [_strictify(item, depth=depth + 1, for_openai=for_openai) for item in node]
    if not isinstance(node, dict):
        return node

    result: dict[str, Any] = {}
    for key, value in node.items():
        if key not in allowed:
            continue
        if key in {"properties"} and isinstance(value, dict):
            result[key] = {
                name: _strictify(subschema, depth=depth + 1, for_openai=for_openai)
                for name, subschema in value.items()
            }
        elif key in {"items", "anyOf"}:
            result[key] = _strictify(value, depth=depth + 1, for_openai=for_openai)
        else:
            result[key] = value

    if result.get("type") == "object" or "properties" in result:
        properties = result.setdefault("properties", {})
        result["type"] = "object"
        if for_openai:
            # OpenAI strict mode expects every property listed as required.
            result["required"] = list(properties)
            result["additionalProperties"] = False
        else:
            existing_required = result.get("required")
            if isinstance(existing_required, list):
                result["required"] = [name for name in existing_required if name in properties]
            else:
                result["required"] = list(properties)

    # A bare ``anyOf`` of a single branch adds nothing but nesting.
    branches = result.get("anyOf")
    if isinstance(branches, list) and len(branches) == 1:
        only = branches[0]
        if isinstance(only, dict):
            description = result.get("description")
            result = {**only}
            if description:
                result["description"] = description

    return result
