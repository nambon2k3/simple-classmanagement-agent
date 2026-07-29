"""Ollama conversation adapter.

Translates between the internal history format shared by the agent and the
OpenAI-compatible chat messages that Ollama's ``/api/chat`` endpoint expects.
"""

from __future__ import annotations

import json
import re
from typing import Any
from uuid import uuid4

from app.core.logging import get_logger

logger = get_logger(__name__)

#: Local models often wrap a tool payload in markdown fences or prose.
_FENCE_RE = re.compile(r"```(?:json|javascript|js)?\s*([\s\S]*?)```", re.IGNORECASE)
#: llama-family models often omit the colon: ``"parameters {"`` → ``"parameters":{``.
_MISSING_COLON_RE = re.compile(
    r'"(parameters|arguments|function|properties)"\s*\{',
)
_TOOL_NAME_RE = re.compile(r'"name"\s*:\s*"([a-z][a-z0-9_]*)"')
_CLASS_NAME_RE = re.compile(r'"class_name"\s*:\s*"([^"]+)"')
_CLASS_NAME_ALT_RE = re.compile(r'"name"\s*:\s*"([^"]+)"')
_FEE_RE = re.compile(r'"daily_tuition_fee"\s*:\s*(\d+)')


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

    # Some local models emit a JSON tool payload in ``content`` (sometimes
    # wrapped in prose or markdown fences) instead of ``tool_calls``.
    recovered = _recover_tool_calls_from_text(text)
    if recovered:
        logger.info(
            "Recovered tool call from assistant text tool=%s",
            recovered[0]["name"],
        )
        return recovered, ""

    return [], text


def rewrite_create_class_intent(
    calls: list[dict[str, str]], user_message: str
) -> list[dict[str, str]]:
    """Map a mis-chosen fee update onto ``create_class`` when the teacher asked to create.

    Local models often call ``set_class_tuition_fee`` for "create class X with fee Y"
    even though the class does not exist yet.
    """
    if not calls or not _looks_like_create_class(user_message):
        return calls

    rewritten: list[dict[str, str]] = []
    for call in calls:
        if call["name"] != "set_class_tuition_fee":
            rewritten.append(call)
            continue
        try:
            args = json.loads(call["arguments"] or "{}")
        except json.JSONDecodeError:
            rewritten.append(call)
            continue
        if not isinstance(args, dict):
            rewritten.append(call)
            continue
        class_name = args.get("class_name") or args.get("name")
        if not isinstance(class_name, str) or not class_name.strip():
            rewritten.append(call)
            continue
        new_args: dict[str, Any] = {"name": class_name.strip()}
        fee = args.get("daily_tuition_fee")
        if isinstance(fee, int) or (isinstance(fee, str) and fee.isdigit()):
            new_args["daily_tuition_fee"] = int(fee)
        logger.info(
            "Rewrote set_class_tuition_fee → create_class for create intent name=%s",
            new_args["name"],
        )
        rewritten.append(
            {
                "call_id": new_call_id("create_class"),
                "name": "create_class",
                "arguments": json.dumps(new_args, ensure_ascii=False),
            }
        )
    return rewritten


def rewrite_add_student_intent(
    calls: list[dict[str, str]], user_message: str
) -> list[dict[str, str]]:
    """Map a mis-chosen attendance mark onto ``add_student`` when enrolling.

    Local models often call ``update_attendance`` for "add student X with code Y
    to class Z" because both mention a student reference and a class name.
    """
    if not calls or not _looks_like_add_student(user_message):
        return calls

    parsed = _parse_add_student_from_message(user_message)
    rewritten: list[dict[str, str]] = []
    for call in calls:
        if call["name"] != "update_attendance":
            rewritten.append(call)
            continue
        try:
            args = json.loads(call["arguments"] or "{}")
        except json.JSONDecodeError:
            rewritten.append(call)
            continue
        if not isinstance(args, dict) or args.get("status"):
            rewritten.append(call)
            continue

        class_name = _first_non_empty(
            parsed.get("class_name"),
            args.get("class_name") if isinstance(args.get("class_name"), str) else None,
        )
        student_code = _first_non_empty(
            parsed.get("student_code"),
            args.get("student") if isinstance(args.get("student"), str) else None,
        )
        full_name = parsed.get("full_name")
        if not all(isinstance(value, str) and value.strip() for value in (class_name, student_code, full_name)):
            rewritten.append(call)
            continue

        new_args = {
            "class_name": class_name.strip(),
            "full_name": full_name.strip(),
            "student_code": student_code.strip(),
        }
        logger.info(
            "Rewrote update_attendance → add_student for enrol intent name=%s code=%s class=%s",
            new_args["full_name"],
            new_args["student_code"],
            new_args["class_name"],
        )
        rewritten.append(
            {
                "call_id": new_call_id("add_student"),
                "name": "add_student",
                "arguments": json.dumps(new_args, ensure_ascii=False),
            }
        )
    return rewritten


def _looks_like_add_student(message: str) -> bool:
    """Heuristic: teacher wants to enrol a new student, not mark attendance."""
    if re.search(r"(?i)\b(present|absent|late|excused)\b", message):
        return False
    return bool(
        re.search(
            r"(?i)"
            r"\b(add|enrol|enroll|register|insert)\b.{0,40}\bstudent\b|"
            r"\bstudent\b.{0,40}\b(to|into)\b.{0,20}\bclass\b",
            message,
        )
    )


def _parse_add_student_from_message(message: str) -> dict[str, str]:
    """Best-effort scrape of enrolment fields from the teacher's message."""
    result: dict[str, str] = {}

    class_match = re.search(r"(?i)(?:to\s+class|into\s+class|class)\s+(\S+)", message)
    if class_match:
        result["class_name"] = class_match.group(1).rstrip(".,!?")

    code_match = re.search(r"(?i)(?:with\s+)?code\s+(\S+)", message)
    if code_match:
        result["student_code"] = code_match.group(1).rstrip(".,!?")

    name_match = re.search(
        r"(?i)(?:add|enrol|enroll|register|insert)\s+student\s+"
        r"(.+?)(?:\s+with\s+code|\s+to\s+class|\s+into\s+class|\s+class\b|$)",
        message,
    )
    if name_match:
        result["full_name"] = name_match.group(1).strip().rstrip(".,!?")

    return result


def _first_non_empty(*values: str | None) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _looks_like_create_class(message: str) -> bool:
    """Heuristic: teacher is asking to create/add a new class."""
    if re.search(
        r"(?i)\b(create|open|new)\b.{0,40}\bclass\b|\bclass\b.{0,20}\b(?:named|called)\b",
        message,
    ):
        return True
    if re.search(r"(?i)\badd\b.{0,20}\b(?:a\s+)?(?:new\s+)?class\b", message):
        # "add tuition fee for class X" updates a fee; it is not "add class X".
        if re.search(r"(?i)\b(tuition|fee|fees|price|cost)\b", message):
            return False
        return True
    return False


def _recover_tool_calls_from_text(text: str) -> list[dict[str, str]]:
    """Pull tool-call JSON out of plain content when the model narrated it."""
    if not text:
        return []

    candidates = _FENCE_RE.findall(text)
    candidates.append(text)

    for chunk in candidates:
        for blob in _iter_json_objects(chunk):
            call = _tool_call_from_payload(blob)
            if call is not None:
                return [call]
        # Brace matcher may fail on broken JSON; try a repaired whole-chunk parse.
        call = _tool_call_from_payload(_repair_tool_json(chunk.strip()))
        if call is not None:
            return [call]
        call = _tool_call_from_lenient_text(chunk)
        if call is not None:
            return [call]
    return []


def _repair_tool_json(blob: str) -> str:
    """Fix common local-model JSON mistakes before ``json.loads``."""
    return _MISSING_COLON_RE.sub(r'"\1":{', blob)


def _iter_json_objects(text: str) -> list[str]:
    """Yield top-level ``{...}`` slices, respecting string escaping."""
    objects: list[str] = []
    i = 0
    length = len(text)
    while i < length:
        if text[i] != "{":
            i += 1
            continue
        depth = 0
        in_string = False
        escape = False
        start = i
        for j in range(i, length):
            ch = text[j]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    objects.append(text[start : j + 1])
                    i = j + 1
                    break
        else:
            break
    return objects


def _tool_call_from_payload(blob: str) -> dict[str, str] | None:
    """Return a normalised tool call when *blob* looks like one."""
    for candidate in (blob, _repair_tool_json(blob)):
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue

        # OpenAI-ish: {"type":"function","name":"...","parameters":{...}}
        # Compact: {"name":"...","arguments":{...}}
        # Nested: {"type":"function","function":{"name":"...","arguments":{...}}}
        name = payload.get("name")
        arguments = payload.get("parameters") if "parameters" in payload else payload.get("arguments")
        nested = payload.get("function")
        if isinstance(nested, dict):
            name = nested.get("name") or name
            if "arguments" in nested:
                arguments = nested.get("arguments")
            elif "parameters" in nested:
                arguments = nested.get("parameters")

        if not isinstance(name, str) or not name.strip():
            continue
        if arguments is None:
            arguments = {}
        if isinstance(arguments, str):
            arguments_json = arguments or "{}"
        elif isinstance(arguments, dict):
            arguments_json = json.dumps(arguments, ensure_ascii=False)
        else:
            continue

        return {
            "call_id": new_call_id(name),
            "name": name.strip(),
            "arguments": arguments_json,
        }
    return None


def _tool_call_from_lenient_text(text: str) -> dict[str, str] | None:
    """Last-resort scrape of tool name + common create/fee fields from broken JSON."""
    names = _TOOL_NAME_RE.findall(text)
    if not names:
        return None
    # Prefer a tool-looking snake_case name that is not a generic field.
    name = next((n for n in names if "_" in n or n in {"list_classes", "create_class"}), names[0])
    args: dict[str, Any] = {}

    class_match = _CLASS_NAME_RE.search(text)
    if class_match:
        args["class_name"] = class_match.group(1)
    elif name == "create_class":
        # Second "name" field is often the class name after the tool name.
        name_fields = _CLASS_NAME_ALT_RE.findall(text)
        if len(name_fields) >= 2:
            args["name"] = name_fields[1]
        elif len(name_fields) == 1 and name_fields[0] != name:
            args["name"] = name_fields[0]

    fee_match = _FEE_RE.search(text)
    if fee_match:
        args["daily_tuition_fee"] = int(fee_match.group(1))

    if name == "set_class_tuition_fee" and "class_name" not in args and "name" in args:
        args["class_name"] = args.pop("name")

    if not args and name not in {"list_classes"}:
        return None

    return {
        "call_id": new_call_id(name),
        "name": name,
        "arguments": json.dumps(args, ensure_ascii=False),
    }
