"""Ollama conversation adapter.

Translates between the internal history format shared by the agent and the
OpenAI-compatible chat messages that Ollama's ``/api/chat`` endpoint expects.
"""

from __future__ import annotations

import json
from typing import Any
from uuid import uuid4


def new_call_id(name: str) -> str:
    """Create a stable-enough identifier for a function call within one turn."""
    return f"{name}:{uuid4().hex[:8]}"


def history_to_messages(history: list[dict[str, Any]], *, system: str) -> list[dict[str, Any]]:
    """Convert stored history items into Ollama chat messages.

    Args:
        history: Internal conversation items persisted on
            :class:`~app.ai.memory.ConversationState`.
        system: System prompt prepended as the first message.

    Returns:
        Messages ready for ``POST /api/chat``.
    """
    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]

    for item in history:
        role = item.get("role")
        if role == "user":
            messages.append({"role": "user", "content": item["content"]})
            continue
        if role == "assistant":
            messages.append({"role": "assistant", "content": item["content"]})
            continue

        item_type = item.get("type")
        if item_type == "function_call":
            arguments = json.loads(item.get("arguments") or "{}")
            call_id = item.get("call_id") or new_call_id(item["name"])
            messages.append(
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {"name": item["name"], "arguments": arguments},
                        }
                    ],
                }
            )
            continue

        if item_type == "function_call_output":
            messages.append(
                {
                    "role": "tool",
                    "tool_name": item.get("name", "unknown"),
                    "content": item.get("output", "{}"),
                }
            )

    return messages


def split_response(response: dict[str, Any]) -> tuple[list[dict[str, str]], str]:
    """Separate function calls from assistant text in an Ollama chat response.

    Args:
        response: JSON body returned by ``POST /api/chat``.

    Returns:
        A pair of *(function calls, assistant text)*.  Each call dict carries
        ``call_id``, ``name`` and ``arguments`` (a JSON string).
    """
    calls: list[dict[str, str]] = []
    message = response.get("message") or {}
    text = (message.get("content") or "").strip()

    for tool_call in message.get("tool_calls") or []:
        function = tool_call.get("function") or {}
        name = function.get("name") or ""
        if not name:
            continue
        arguments = function.get("arguments", {})
        if isinstance(arguments, str):
            arguments_json = arguments or "{}"
        else:
            arguments_json = json.dumps(arguments, ensure_ascii=False)
        calls.append(
            {
                "call_id": tool_call.get("id") or new_call_id(name),
                "name": name,
                "arguments": arguments_json,
            }
        )

    if calls:
        return calls, text

    # Some local models emit a JSON tool payload in ``content`` instead of
    # ``tool_calls``; recover when the shape is obvious.
    if text.startswith("{") and '"name"' in text:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return [], text
        name = payload.get("name")
        if isinstance(name, str) and name:
            arguments = payload.get("parameters") or payload.get("arguments") or {}
            if isinstance(arguments, dict):
                return (
                    [
                        {
                            "call_id": new_call_id(name),
                            "name": name,
                            "arguments": json.dumps(arguments, ensure_ascii=False),
                        }
                    ],
                    "",
                )

    return [], text
