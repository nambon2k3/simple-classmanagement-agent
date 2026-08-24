"""Groq conversation adapter.

Translates between the internal history format and the OpenAI-compatible chat
messages that Groq's ``/openai/v1/chat/completions`` endpoint expects.
"""

from __future__ import annotations

import json
from typing import Any

from app.ai.ollama import new_call_id, split_response as _split_message_payload

#: Models that classify or moderate input — not usable as the classroom assistant.
_CLASSIFIER_MODEL_MARKERS = ("prompt-guard", "llama-guard")


def model_supports_tool_calling(model: str) -> bool:
    """Whether *model* can run the assistant's tool-calling loop."""
    lowered = model.lower()
    return not any(marker in lowered for marker in _CLASSIFIER_MODEL_MARKERS)


def history_to_messages(history: list[dict[str, Any]], *, system: str) -> list[dict[str, Any]]:
    """Convert stored history items into OpenAI-style chat messages.

    Args:
        history: Internal conversation items persisted on
            :class:`~app.ai.memory.ConversationState`.
        system: System prompt prepended as the first message.

    Returns:
        Messages ready for Groq chat completions.
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
            call_id = item.get("call_id") or new_call_id(item["name"])
            arguments = item.get("arguments") or "{}"
            if isinstance(arguments, dict):
                arguments = json.dumps(arguments, ensure_ascii=False)
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
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
                    "tool_call_id": item.get("call_id") or new_call_id(item.get("name", "tool")),
                    "content": item.get("output", "{}"),
                }
            )

    return messages


def split_response(response: dict[str, Any]) -> tuple[list[dict[str, str]], str]:
    """Separate function calls from assistant text in a Groq chat response."""
    if "choices" in response:
        message = (response.get("choices") or [{}])[0].get("message") or {}
        return _split_message_payload({"message": message})
    return _split_message_payload(response)
