"""The agent's tool-calling loop, driven by a scripted model.

The Groq client is faked so the loop is deterministic, but everything below
it is real: the registry validates, the services run and the database is
written to.  These tests are what prove the model can only reach the data
through tools.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import httpx
import pytest
from groq import APIStatusError

from app.ai.agent import AssistantAgent
from app.ai.memory import ConversationState
from app.ai.tools.definitions import EMIT_ATTENDANCE_CLOSED, EMIT_ATTENDANCE_SESSION, build_registry
from app.core.config import get_settings
from app.core.exceptions import AssistantError
from app.models.enums import AttendanceStatus
from app.schemas.classroom import ListClassesInput  # noqa: F401  (documents the tool surface)


@dataclass
class FakeResponse:
    """Mimics a Groq ``/chat/completions`` assistant message."""

    message: dict[str, Any] = field(default_factory=dict)


class ScriptedClient:
    """Stands in for :class:`~app.ai.client.GroqClient`."""

    def __init__(self, script: list[FakeResponse]) -> None:
        self._script = list(script)
        self.requests: list[dict[str, Any]] = []

    async def chat(self, **kwargs: Any) -> dict[str, Any]:
        self.requests.append(kwargs)
        if not self._script:
            return {"choices": [{"message": {"role": "assistant", "content": "(no more scripted responses)"}}]}
        item = self._script.pop(0)
        return {"choices": [{"message": item.message}]}


def tool_call(name: str, arguments: dict[str, Any], call_id: str | None = None) -> FakeResponse:
    return FakeResponse(
        message={
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": call_id or f"call_{name}",
                    "type": "function",
                    "function": {"name": name, "arguments": json.dumps(arguments, ensure_ascii=False)},
                }
            ],
        }
    )


def tool_calls(*calls: tuple[str, dict[str, Any]]) -> FakeResponse:
    return FakeResponse(
        message={
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": f"call_{name}",
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(arguments, ensure_ascii=False),
                    },
                }
                for name, arguments in calls
            ],
        }
    )


def text_response(message: str) -> FakeResponse:
    return FakeResponse(message={"role": "assistant", "content": message})


def make_agent(script: list[FakeResponse]) -> tuple[AssistantAgent, ScriptedClient]:
    client = ScriptedClient(script)
    return AssistantAgent(client, build_registry(), get_settings()), client


@pytest.fixture
def state(teacher) -> ConversationState:
    return ConversationState(chat_id=1, teacher_id=teacher.id)


# ----------------------------------------------------------------- the loop --


async def test_a_tool_call_reaches_the_database(services, teacher, state):
    agent, _ = make_agent(
        [
            tool_call("create_class", {"name": "SE401", "description": None}),
            text_response("Created *SE401* for you."),
        ]
    )
    reply = await agent.run("Create class SE401", state=state, services=services)

    assert reply.tool_calls == ["create_class"]
    assert reply.text == "Created *SE401* for you."
    listed = await services.classes.list_classes(teacher.id)
    assert [item.name for item in listed.classes] == ["SE401"]


async def test_the_model_is_offered_every_tool(services, teacher, state):
    agent, client = make_agent([text_response("Hello!")])
    await agent.run("hi", state=state, services=services)

    request = client.requests[0]
    offered = {tool["function"]["name"] for tool in request["tools"]}
    assert offered == set(build_registry().names)
    system_message = request["messages"][0]
    assert system_message["role"] == "system"
    assert "class management assistant" in system_message["content"].lower()


async def test_several_tools_can_run_in_one_turn(services, teacher, classroom, state):
    agent, _ = make_agent(
        [
            tool_calls(
                (
                    "add_student",
                    {
                        "class_name": "SE401",
                        "full_name": "Nguyen Van A",
                        "student_code": "SE001",
                        "email": None,
                        "phone": None,
                        "note": None,
                    },
                ),
                (
                    "add_student",
                    {
                        "class_name": "SE401",
                        "full_name": "John Smith",
                        "student_code": "SE002",
                        "email": None,
                        "phone": None,
                        "note": None,
                    },
                ),
            ),
            text_response("Added both students."),
        ]
    )
    reply = await agent.run("Add two students", state=state, services=services)

    assert reply.tool_calls == ["add_student", "add_student"]
    from app.schemas.student import ListStudentsInput

    roster = await services.students.list_students(
        teacher.id, ListStudentsInput(class_name="SE401")
    )
    assert roster.total == 2


async def test_a_failing_tool_is_reported_back_to_the_model(services, teacher, state):
    agent, client = make_agent(
        [
            tool_call("get_class_info", {"name": "GHOST"}),
            text_response("You don't have a class called GHOST."),
        ]
    )
    reply = await agent.run("Show me GHOST", state=state, services=services)

    follow_up_messages = client.requests[1]["messages"]
    tool_messages = [message for message in follow_up_messages if message["role"] == "tool"]
    payload = json.loads(tool_messages[0]["content"])
    assert payload["error"] == "class_not_found"
    assert reply.text.startswith("You don't have")


async def test_invalid_arguments_never_reach_the_service(services, teacher, state):
    agent, client = make_agent(
        [
            tool_call("create_class", {"name": "   "}),
            text_response("What should the class be called?"),
        ]
    )
    await agent.run("Create a class", state=state, services=services)

    follow_up_messages = client.requests[1]["messages"]
    tool_messages = [message for message in follow_up_messages if message["role"] == "tool"]
    payload = json.loads(tool_messages[0]["content"])
    assert payload["error"] == "tool_input_error"
    assert (await services.classes.list_classes(teacher.id)).total == 0


async def test_the_loop_stops_at_the_iteration_limit(services, teacher, classroom, state):
    """A model stuck in a tool loop must not spin forever."""
    limit = get_settings().max_tool_iterations
    agent, client = make_agent([tool_call("list_classes", {}) for _ in range(limit + 5)])
    reply = await agent.run("loop please", state=state, services=services)

    assert len(client.requests) == limit
    assert len(reply.tool_calls) == limit
    assert "one thing at a time" in reply.text


async def test_api_failures_surface_as_a_readable_error(services, teacher, state):
    class FailingClient:
        async def chat(self, **_: Any) -> dict[str, Any]:
            request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
            response = httpx.Response(503, request=request)
            raise APIStatusError("service unavailable", response=response, body=None)

    agent = AssistantAgent(FailingClient(), build_registry(), get_settings())
    with pytest.raises(AssistantError, match="language model"):
        await agent.run("hello", state=state, services=services)


# ------------------------------------------------------------- conversation --


async def test_history_carries_over_between_turns(services, teacher, classroom, state):
    agent, client = make_agent(
        [
            text_response("Hi there."),
            text_response("Still here."),
        ]
    )
    await agent.run("hello", state=state, services=services)
    await agent.run("are you there?", state=state, services=services)

    second_request_messages = client.requests[1]["messages"]
    assert {"role": "user", "content": "hello"} in second_request_messages
    assert {"role": "assistant", "content": "Hi there."} in second_request_messages


async def test_history_is_trimmed_to_the_configured_limit(services, teacher, state):
    agent, _ = make_agent([text_response("ok") for _ in range(30)])
    for index in range(30):
        await agent.run(f"message {index}", state=state, services=services)

    assert len(state.history) <= get_settings().max_history_items


# -------------------------------------------------------------- attendance --


async def test_starting_attendance_publishes_the_board(services, teacher, roster, state):
    agent, _ = make_agent(
        [
            tool_call(
                "start_attendance",
                {"class_name": "SE401", "session_date": None, "reopen": False},
            ),
            text_response("Here's SE401 — tap to mark."),
        ]
    )
    reply = await agent.run("Take attendance for SE401", state=state, services=services)

    session = reply.emitted[EMIT_ATTENDANCE_SESSION]
    assert session.class_name == "SE401"
    assert len(session.entries) == 3
    assert state.focus_session_id == session.session_id
    assert state.focus_class_id == session.class_id


async def test_a_bare_name_marks_a_student_in_the_focused_session(services, teacher, roster, state):
    """'John absent' works because the focus hint identifies the session."""
    agent, _ = make_agent(
        [
            tool_call(
                "start_attendance",
                {"class_name": "SE401", "session_date": None, "reopen": False},
            ),
            text_response("Ready."),
            tool_call(
                "update_attendance",
                {
                    "student": "John",
                    "status": "absent",
                    "class_name": None,
                    "note": None,
                },
            ),
            text_response("Marked John absent."),
        ]
    )
    await agent.run("Take attendance for SE401", state=state, services=services)
    await agent.run("John absent", state=state, services=services)

    view = await services.attendance.get_session_view(teacher.id, state.focus_session_id)
    marked = {entry.full_name: entry.status for entry in view.entries}
    assert marked["John Smith"] is AttendanceStatus.ABSENT


async def test_finishing_clears_the_attendance_focus(services, teacher, roster, state):
    agent, _ = make_agent(
        [
            tool_call(
                "start_attendance",
                {"class_name": "SE401", "session_date": None, "reopen": False},
            ),
            text_response("Ready."),
            tool_call(
                "finish_attendance",
                {"class_name": None, "default_status_for_unmarked": "present"},
            ),
            text_response("All saved."),
        ]
    )
    await agent.run("Take attendance for SE401", state=state, services=services)
    reply = await agent.run("Done", state=state, services=services)

    assert reply.emitted[EMIT_ATTENDANCE_CLOSED] is True
    assert state.focus_session_id is None
    assert state.focus_class_id is not None  # the class stays in focus


async def test_groq_tools_are_built_from_the_registry():
    tools = build_registry().to_ollama_tools()
    assert {tool["function"]["name"] for tool in tools} == set(build_registry().names)
    assert all(tool["type"] == "function" for tool in tools)


async def test_refusal_after_successful_tools_shows_tool_message(services, teacher, state):
    """Local models often apologise about tools even after they ran."""
    agent, _ = make_agent(
        [
            tool_call("create_class", {"name": "SE401", "description": None}),
            text_response(
                "I'm sorry, I cannot use tools or call functions to create classes for you."
            ),
        ]
    )
    reply = await agent.run("Create class SE401", state=state, services=services)

    assert reply.tool_calls == ["create_class"]
    assert "cannot use tools" not in reply.text.lower()
    assert "SE401" in reply.text
    listed = await services.classes.list_classes(teacher.id)
    assert [item.name for item in listed.classes] == ["SE401"]


async def test_add_student_rewrites_wrong_attendance_tool(services, teacher, classroom, state):
    """Small models often pick update_attendance when enrolling someone new."""
    agent, _ = make_agent(
        [
            tool_call("update_attendance", {"student": "HN", "class_name": "SE401"}),
            text_response("Added HoaiNam to SE401."),
        ]
    )
    reply = await agent.run(
        "Add student HoaiNam with code HN to class SE401",
        state=state,
        services=services,
    )

    assert reply.tool_calls == ["add_student"]
    from app.schemas.student import ListStudentsInput

    roster = await services.students.list_students(
        teacher.id, ListStudentsInput(class_name="SE401")
    )
    assert roster.total == 1
    assert roster.students[0].student_code == "HN"
    assert roster.students[0].full_name == "HoaiNam"
