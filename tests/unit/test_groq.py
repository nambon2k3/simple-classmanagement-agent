"""Tests for the Groq conversation adapter."""

from __future__ import annotations

from app.ai.groq import history_to_messages, model_supports_tool_calling, split_response


def test_classifier_models_do_not_support_tool_calling():
    assert model_supports_tool_calling("llama-3.3-70b-versatile") is True
    assert model_supports_tool_calling("meta-llama/llama-prompt-guard-2-86m") is False


def test_history_to_messages_uses_openai_tool_format():
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
    ]

    messages = history_to_messages(history, system="You are helpful.")

    assert messages[0] == {"role": "system", "content": "You are helpful."}
    assert messages[1]["role"] == "user"
    assert messages[2]["tool_calls"][0]["function"]["name"] == "create_class"
    assert messages[3]["role"] == "tool"
    assert messages[3]["tool_call_id"] == "call_1"


def test_split_response_reads_groq_payload():
    calls, text = split_response(
        {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_abc",
                                "type": "function",
                                "function": {"name": "list_classes", "arguments": "{}"},
                            }
                        ],
                    }
                }
            ]
        }
    )

    assert text == ""
    assert calls[0]["name"] == "list_classes"
    assert calls[0]["call_id"] == "call_abc"
