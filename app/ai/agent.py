"""The assistant agent: one user message in, one reply out.

Implements the tool-calling loop against a local Ollama model.  The agent owns
*conversation* concerns — history, iteration limits, turning API failures into
something a teacher can read — and nothing else.  It cannot touch the database;
the only capability it has is asking the registry to run a named tool, and the
registry validates and authorises every one of those calls.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.ai.client import OllamaClient
from app.ai.memory import ConversationState
from app.ai.ollama import (
    history_to_messages,
    rewrite_add_student_intent,
    rewrite_create_class_intent,
    split_response,
)
from app.ai.prompts import build_system_prompt
from app.ai.tools.registry import ToolContext, ToolRegistry
from app.core.config import Settings, get_settings
from app.core.exceptions import AssistantError
from app.core.logging import get_logger

logger = get_logger(__name__)

#: Shown when the model produces no text at all, which should be rare.
_EMPTY_REPLY_FALLBACK = "Done."
#: Shown when the model keeps calling tools past the iteration budget.
_ITERATION_LIMIT_REPLY = (
    "That turned into more steps than I expected. Could you try asking for one thing at a time?"
)
#: Shown when the model only narrates a tool call and we cannot recover it.
_COULD_NOT_RUN_TOOL_REPLY = (
    "I couldn't run that action just now. Please try again in one short sentence, "
    "for example: create class Lop7 with tuition fee 50000."
)
#: Local models sometimes describe a tool call in prose instead of emitting
#: ``tool_calls``.
_NARRATED_TOOL_RE = re.compile(
    r'(?is)("type"\s*:\s*"function"|I will use the|here\'s how you can do it|'
    r"call the `|use the `?\w+_?\w*`? function|"
    r'"name"\s*:\s*"[a-z][a-z0-9_]*")',
)
#: After tools already ran, small local models often apologise that they
#: "cannot use tools". Never show that to the teacher.
_TOOL_REFUSAL_RE = re.compile(
    r"(?is)"
    r"(cannot|can't|do not|don't|unable to|not able to)"
    r".{0,40}"
    r"(use tools?|call tools?|access tools?|execute tools?|support tools?|"
    r"run tools?|use functions?|call functions?)"
    r"|"
    r"(as an ai|language model).{0,60}(cannot|can't|don't|unable)"
    r"|"
    r"I (?:do not|don't) have (?:access|ability).{0,40}tool",
)


@dataclass(slots=True)
class AgentReply:
    """The outcome of a single user turn."""

    #: Text to send to the teacher.
    text: str
    #: Names of the tools that ran, in order.  Useful for logs and tests.
    tool_calls: list[str] = field(default_factory=list)
    #: Side-channel data published by handlers, such as an attendance session
    #: that the Telegram layer should render as an inline keyboard.
    emitted: dict[str, Any] = field(default_factory=dict)
    #: Class the conversation ended up focused on.
    focus_class_id: int | None = None
    #: Attendance session the conversation ended up focused on.
    focus_session_id: int | None = None


class AssistantAgent:
    """Runs the model's tool-calling loop for one conversation turn."""

    def __init__(
        self,
        client: OllamaClient,
        registry: ToolRegistry,
        settings: Settings | None = None,
    ) -> None:
        """Wire the agent to its dependencies.

        Args:
            client: Configured Ollama client.
            registry: Catalogue of tools the model may call.
            settings: Configuration for the model name and loop limits.
        """
        self._client = client
        self._registry = registry
        self._settings = settings or get_settings()

    async def run(
        self,
        message: str,
        *,
        state: ConversationState,
        services: Any,
    ) -> AgentReply:
        """Handle one user message.

        Args:
            message: What the teacher typed.
            state: Live conversation state; its history is read and updated.
            services: The :class:`~app.services.container.ServiceContainer`
                bound to the current unit of work.

        Returns:
            The reply to send, plus anything the tools emitted.

        Raises:
            AssistantError: Only if Ollama itself is unreachable or
                misconfigured.  Tool failures never raise; they come back to
                the model as structured errors.
        """
        context = ToolContext(
            teacher_id=state.teacher_id,
            services=services,
            focus_class_id=state.focus_class_id,
            focus_session_id=state.focus_session_id,
        )
        tools = self._registry.to_ollama_tools()
        instructions = build_system_prompt(state)

        turn_items: list[dict[str, Any]] = [{"role": "user", "content": message}]
        called: list[str] = []
        reply_text = ""

        logger.info(
            "Model turn started teacher_id=%s message=%s",
            state.teacher_id,
            _clip_for_log(message),
        )

        iterations = 0
        while iterations < self._settings.max_tool_iterations:
            iterations += 1
            response = await self._generate(
                instructions=instructions,
                history=state.history + turn_items,
                tools=tools,
            )

            calls, text = split_response(response)
            calls = rewrite_create_class_intent(calls, message)
            calls = rewrite_add_student_intent(calls, message)
            if text:
                reply_text = text

            if not calls:
                if text and _NARRATED_TOOL_RE.search(text):
                    if called:
                        # Class/fee may already have been applied; do not undo that
                        # with a "please try again" after a successful tool round.
                        logger.info(
                            "Ignoring narrated follow-up after tools teacher_id=%s",
                            state.teacher_id,
                        )
                        reply_text = (
                            _message_from_last_tool(turn_items) or _EMPTY_REPLY_FALLBACK
                        )
                        break
                    logger.warning(
                        "Model narrated a tool call and recovery failed teacher_id=%s reply=%s",
                        state.teacher_id,
                        _clip_for_log(text),
                    )
                    reply_text = _COULD_NOT_RUN_TOOL_REPLY
                    break

                logger.info(
                    "Model decided to reply without tools iteration=%s teacher_id=%s reply=%s",
                    iterations,
                    state.teacher_id,
                    _clip_for_log(text or ""),
                )
                if text:
                    turn_items.append({"role": "assistant", "content": text})
                break

            logger.info(
                "Model decided to call tools iteration=%s teacher_id=%s tools=%s",
                iterations,
                state.teacher_id,
                [call["name"] for call in calls],
            )

            for call in calls:
                logger.info(
                    "Model tool call iteration=%s teacher_id=%s tool=%s arguments=%s",
                    iterations,
                    state.teacher_id,
                    call["name"],
                    _clip_for_log(call["arguments"]),
                )
                turn_items.append(
                    {
                        "type": "function_call",
                        "call_id": call["call_id"],
                        "name": call["name"],
                        "arguments": call["arguments"],
                    }
                )
                result = await self._registry.execute(call["name"], call["arguments"], context)
                called.append(call["name"])
                logger.info(
                    "Model tool result teacher_id=%s tool=%s outcome=%s",
                    state.teacher_id,
                    call["name"],
                    _summarise_tool_result(result),
                )
                turn_items.append(
                    {
                        "type": "function_call_output",
                        "call_id": call["call_id"],
                        "name": call["name"],
                        "output": json.dumps(result, ensure_ascii=False, default=str),
                    }
                )
            # After tools run, clear any narrated prose so the final reply comes
            # from the next model turn (or fallback).
            reply_text = ""
        else:
            logger.warning(
                "Tool loop hit the iteration limit",
                extra={"teacher_id": state.teacher_id, "iterations": iterations},
            )
            reply_text = reply_text or _ITERATION_LIMIT_REPLY

        state.extend_history(turn_items, limit=self._settings.max_history_items)
        state.focus_class_id = context.focus_class_id
        state.focus_session_id = context.focus_session_id

        reply_text = _final_reply_text(reply_text, turn_items, tools_ran=bool(called))

        return AgentReply(
            text=reply_text,
            tool_calls=called,
            emitted=dict(context.emitted),
            focus_class_id=context.focus_class_id,
            focus_session_id=context.focus_session_id,
        )

    async def _generate(
        self,
        *,
        instructions: str,
        history: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Call Ollama, translating transport failures.

        Raises:
            AssistantError: If the server cannot be reached or rejects the request.
        """
        messages = history_to_messages(history, system=instructions)
        attempts = self._settings.ollama_max_retries + 1
        last_error: Exception | None = None

        for attempt in range(attempts):
            try:
                return await self._client.chat(
                    model=self._settings.ollama_model,
                    messages=messages,
                    tools=tools,
                )
            except httpx.TimeoutException as exc:
                logger.warning("Ollama request timed out", extra={"attempt": attempt + 1})
                last_error = exc
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                logger.exception(
                    "Ollama HTTP error",
                    extra={"status": status, "attempt": attempt + 1},
                )
                if status >= 500 and attempt + 1 < attempts:
                    last_error = exc
                    continue
                if status == 404:
                    raise AssistantError(
                        f"I couldn't find the model '{self._settings.ollama_model}'. "
                        "Please pull it with Ollama first."
                    ) from exc
                raise AssistantError(
                    "I couldn't reach my language model just now. Please try again in a moment."
                ) from exc
            except httpx.HTTPError as exc:
                logger.exception("Ollama connection error", extra={"attempt": attempt + 1})
                last_error = exc
            except Exception as exc:
                logger.exception("Ollama client error")
                raise AssistantError(
                    "My assistant configuration looks wrong. Please tell the administrator."
                ) from exc

        if isinstance(last_error, httpx.TimeoutException):
            raise AssistantError("That took too long. Please try again.") from last_error
        raise AssistantError(
            "I couldn't reach my language model just now. Please try again in a moment."
        ) from last_error


def _clip_for_log(value: Any, *, limit: int = 500) -> str:
    """Render a value for logs without dumping unbounded model output."""
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, default=str)
    text = text.replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _summarise_tool_result(result: dict[str, Any]) -> str:
    """Compact success/error summary for the model's tool-call outcome."""
    if result.get("success") is False or "error" in result:
        error = result.get("error", "unknown_error")
        message = result.get("message", "")
        return f"error code={error} message={_clip_for_log(message, limit=200)}"
    message = result.get("message")
    if message:
        return f"ok message={_clip_for_log(message, limit=200)}"
    return "ok"


def _message_from_last_tool(turn_items: list[dict[str, Any]]) -> str | None:
    """Prefer the last tool's teacher-facing message when the model won't summarise."""
    for item in reversed(turn_items):
        if item.get("type") != "function_call_output":
            continue
        try:
            payload = json.loads(item.get("output") or "{}")
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            message = payload.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()
    return None


def _final_reply_text(text: str, turn_items: list[dict[str, Any]], *, tools_ran: bool) -> str:
    """Choose what the teacher sees after a turn, masking weak local-model prose."""
    if not tools_ran:
        return text or _EMPTY_REPLY_FALLBACK
    if _should_use_tool_message_instead(text):
        tool_message = _message_from_last_tool(turn_items)
        if tool_message:
            logger.info("Replacing model reply with last tool message after successful tools")
            return tool_message
    return text or _EMPTY_REPLY_FALLBACK


def _should_use_tool_message_instead(text: str) -> bool:
    """Whether to ignore the model's words and show the tool result instead."""
    if not text or text in {_EMPTY_REPLY_FALLBACK, _COULD_NOT_RUN_TOOL_REPLY}:
        return True
    if _TOOL_REFUSAL_RE.search(text):
        return True
    return bool(_NARRATED_TOOL_RE.search(text))
