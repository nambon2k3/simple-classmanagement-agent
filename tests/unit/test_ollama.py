"""Tests for the Ollama conversation adapter."""

from __future__ import annotations

from app.ai.ollama import history_to_messages, split_response


def test_history_to_messages_includes_system_prompt_and_tool_round_trip():
    history = [
        {"role": "user", "content": "Create class SE401"},
        {
            "type": "function_call",
            "call_id": "call_1",
            "name": "create_class",
            "arguments": '{"name": "SE401"}',
        },
        {
            "type": "function_call_output",
            "call_id": "call_1",
            "name": "create_class",
            "output": '{"success": true}',
        },
        {"role": "assistant", "content": "Done."},
    ]

    messages = history_to_messages(history, system="You are helpful.")

    assert messages[0] == {"role": "system", "content": "You are helpful."}
    assert messages[1]["role"] == "user"
    assert messages[2]["tool_calls"][0]["function"]["name"] == "create_class"
    assert messages[3]["role"] == "tool"
    assert messages[3]["tool_name"] == "create_class"
    assert messages[4]["content"] == "Done."


def test_split_response_reads_tool_calls():
    calls, text = split_response(
        {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_abc",
                        "function": {"name": "list_classes", "arguments": {}},
                    }
                ],
            }
        }
    )

    assert text == ""
    assert calls[0]["name"] == "list_classes"
    assert calls[0]["call_id"] == "call_abc"


def test_split_response_falls_back_to_json_content():
    calls, text = split_response(
        {
            "message": {
                "role": "assistant",
                "content": '{"name": "create_class", "parameters": {"name": "SE401"}}',
            }
        }
    )

    assert text == ""
    assert calls[0]["name"] == "create_class"
    assert '"name": "SE401"' in calls[0]["arguments"]
