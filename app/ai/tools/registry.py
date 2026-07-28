"""Tool registry: the only bridge between the language model and the backend.

The model can do exactly one thing to this system — ask for a named tool with
some JSON arguments.  :meth:`ToolRegistry.execute` is the choke point where
those arguments are parsed, validated against a Pydantic model and dispatched
to a service.  It never raises: every failure comes back as a structured
:class:`~app.schemas.common.ErrorResult` so the model can explain it or ask a
follow-up question, and so an internal error can never reach the teacher as a
stack trace.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from app.ai.tools.schema import build_openai_tool_schema, build_tool_schema
from app.core.exceptions import AppError, ToolInputError, ToolNotFoundError
from app.core.logging import get_logger
from app.schemas.common import ErrorResult

logger = get_logger(__name__)

#: A handler receives the execution context plus validated arguments and
#: returns a Pydantic model that will be serialised back to the model.
ToolHandler = Callable[["ToolContext", Any], Awaitable[BaseModel]]


@dataclass(slots=True)
class ToolContext:
    """Everything a tool needs beyond its own arguments.

    Passing the teacher id through the context rather than through the tool
    arguments is a deliberate security decision: the language model has no way
    to name a teacher, so it cannot reach another teacher's data even if it
    tries.
    """

    teacher_id: int
    #: Service composition root bound to the current unit of work.  Typed as
    #: ``Any`` to keep the AI layer free of a hard import cycle with services.
    services: Any
    #: Class the conversation is currently focused on, if any.  A hint only —
    #: the services still verify ownership and session state.
    focus_class_id: int | None = None
    #: Attendance session the conversation is currently filling in, if any.
    focus_session_id: int | None = None
    #: Side-channel for handlers to report state the caller should remember,
    #: for example a newly opened attendance session.
    emitted: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """A single callable exposed to the language model."""

    name: str
    description: str
    input_model: type[BaseModel]
    handler: ToolHandler

    def to_function_declaration(self) -> dict[str, Any]:
        """Render this tool as a function declaration dict."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": build_tool_schema(self.input_model),
        }

    def to_ollama_tool(self) -> dict[str, Any]:
        """Render this tool for Ollama's OpenAI-compatible tools field."""
        return {
            "type": "function",
            "function": self.to_function_declaration(),
        }

    def to_openai_tool(self) -> dict[str, Any]:
        """Render this tool in the legacy OpenAI Responses API format."""
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": build_openai_tool_schema(self.input_model),
            "strict": True,
        }


class ToolRegistry:
    """Holds the tool catalogue and executes calls against it."""

    def __init__(self) -> None:
        """Create an empty registry."""
        self._tools: dict[str, ToolSpec] = {}

    def register(
        self,
        name: str,
        description: str,
        input_model: type[BaseModel],
        handler: ToolHandler,
    ) -> None:
        """Add a tool to the catalogue.

        Args:
            name: Name the model will call, e.g. ``create_class``.
            description: What the tool does and when to use it.  This is the
                model's only documentation, so it should read like an
                instruction.
            input_model: Pydantic model validating the arguments.
            handler: Coroutine invoked with the context and validated input.

        Raises:
            ValueError: If the name is already registered.
        """
        if name in self._tools:
            raise ValueError(f"Tool {name!r} is already registered.")
        self._tools[name] = ToolSpec(
            name=name, description=description, input_model=input_model, handler=handler
        )

    def get(self, name: str) -> ToolSpec | None:
        """Return a tool by name, or ``None`` when it is not registered."""
        return self._tools.get(name)

    @property
    def names(self) -> list[str]:
        """Names of every registered tool, in registration order."""
        return list(self._tools)

    def to_function_declarations(self) -> list[dict[str, Any]]:
        """Render every tool as a function declaration dict."""
        return [spec.to_function_declaration() for spec in self._tools.values()]

    def to_ollama_tools(self) -> list[dict[str, Any]]:
        """Render the whole catalogue for Ollama function calling."""
        return [spec.to_ollama_tool() for spec in self._tools.values()]

    def to_openai_tools(self) -> list[dict[str, Any]]:
        """Render the whole catalogue in the legacy OpenAI Responses API format."""
        return [spec.to_openai_tool() for spec in self._tools.values()]

    async def execute(
        self, name: str, arguments: str | dict[str, Any], context: ToolContext
    ) -> dict[str, Any]:
        """Validate and run a tool call.

        Args:
            name: Tool the model asked for.
            arguments: Raw JSON string (as the API sends it) or a decoded dict.
            context: Execution context carrying the teacher and focus hints.

        Returns:
            A JSON-serialisable dict: either the tool's output model or an
            :class:`ErrorResult`.  This method does not raise.
        """
        spec = self._tools.get(name)
        if spec is None:
            logger.warning("Model requested unknown tool", extra={"tool": name})
            return _error(ToolNotFoundError(f"I don't know how to do '{name}'."))

        try:
            payload = _decode_arguments(arguments)
        except ToolInputError as exc:
            return _error(exc)

        try:
            validated = spec.input_model.model_validate(payload)
        except PydanticValidationError as exc:
            logger.info(
                "Tool arguments failed validation",
                extra={"tool": name, "errors": exc.error_count()},
            )
            return _error(
                ToolInputError(_describe_validation_error(exc), tool=name),
            )

        try:
            result = await spec.handler(context, validated)
        except AppError as exc:
            # Expected domain failures: the model turns these into a natural
            # reply or a follow-up question.
            logger.info(
                "Tool returned a domain error",
                extra={"tool": name, "code": exc.code},
            )
            return _error(exc)
        except Exception:
            # Unexpected: log the detail for us, tell the model something bland.
            logger.exception("Tool raised an unexpected error", extra={"tool": name})
            return ErrorResult(
                error="internal_error",
                message="Something went wrong on my side. Please try again.",
            ).model_dump(mode="json", exclude_none=True)

        logger.info("Tool executed", extra={"tool": name, "teacher_id": context.teacher_id})
        return result.model_dump(mode="json", exclude_none=True)


def _decode_arguments(arguments: str | dict[str, Any]) -> dict[str, Any]:
    """Turn the API's argument payload into a dict.

    Raises:
        ToolInputError: If the payload is not a JSON object.
    """
    if isinstance(arguments, dict):
        return arguments
    text = (arguments or "").strip()
    if not text:
        return {}
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ToolInputError("The arguments were not valid JSON.") from exc
    if not isinstance(decoded, dict):
        raise ToolInputError("The arguments must be a JSON object.")
    return decoded


def _describe_validation_error(error: PydanticValidationError) -> str:
    """Summarise a validation failure in language the model can act on."""
    problems = []
    for item in error.errors()[:4]:
        location = ".".join(str(part) for part in item["loc"]) or "input"
        problems.append(f"{location}: {item['msg']}")
    return "Some arguments were not valid — " + "; ".join(problems)


def _error(exc: AppError) -> dict[str, Any]:
    """Serialise a domain error into the model-facing error shape."""
    return ErrorResult(
        error=exc.code,
        message=exc.message,
        details=exc.details or None,
    ).model_dump(mode="json", exclude_none=True)
