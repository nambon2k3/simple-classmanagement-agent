"""Tests for the Ollama conversation adapter."""

from __future__ import annotations

import json

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


def test_split_response_recovers_tool_json_embedded_in_prose():
    content = (
        'Based on the docs, I will use the `set_class_tuition_fee` function.\n\n'
        "Here's how you can do it:\n\n"
        "```\n"
        '{"type":"function","name":"set_class_tuition_fee",'
        '"parameters":{"class_name":"Lop7","daily_tuition_fee":50000}}\n'
        "```\n"
        "This will set the fee."
    )
    calls, text = split_response({"message": {"role": "assistant", "content": content}})

    assert text == ""
    assert calls[0]["name"] == "set_class_tuition_fee"
    assert '"class_name": "Lop7"' in calls[0]["arguments"]
    assert "50000" in calls[0]["arguments"]


def test_split_response_recovers_malformed_missing_colon():
    content = (
        '{"type":"function","name":"set_class_tuition_fee",'
        '"parameters {"class_name":"Lop7","daily_tuition_fee":50000}}'
    )
    calls, text = split_response({"message": {"role": "assistant", "content": content}})

    assert text == ""
    assert calls[0]["name"] == "set_class_tuition_fee"
    assert "Lop7" in calls[0]["arguments"]
    assert "50000" in calls[0]["arguments"]


def test_rewrite_create_class_intent_maps_fee_tool():
    from app.ai.ollama import rewrite_create_class_intent

    calls = [
        {
            "call_id": "x",
            "name": "set_class_tuition_fee",
            "arguments": '{"class_name": "Lop7", "daily_tuition_fee": 50000}',
        }
    ]
    rewritten = rewrite_create_class_intent(
        calls, "Yes create new class named Lop7 and tution fee is 50000"
    )
    assert rewritten[0]["name"] == "create_class"
    assert "Lop7" in rewritten[0]["arguments"]
    assert "50000" in rewritten[0]["arguments"]


def test_rewrite_does_not_map_add_tuition_fee_to_create_class():
    from app.ai.ollama import rewrite_create_class_intent

    calls = [
        {
            "call_id": "x",
            "name": "set_class_tuition_fee",
            "arguments": '{"class_name": "SE1734", "daily_tuition_fee": 50000}',
        }
    ]
    rewritten = rewrite_create_class_intent(calls, "Add tuition fee 50000 for class SE1734")
    assert rewritten[0]["name"] == "set_class_tuition_fee"


def test_rewrite_add_student_intent_maps_attendance_tool():
    from app.ai.ollama import rewrite_add_student_intent

    calls = [
        {
            "call_id": "x",
            "name": "update_attendance",
            "arguments": '{"student": "HN", "class_name": "SE1734"}',
        }
    ]
    rewritten = rewrite_add_student_intent(
        calls, "Add student HoaiNam with code HN to class SE1734"
    )
    assert rewritten[0]["name"] == "add_student"
    args = json.loads(rewritten[0]["arguments"])
    assert args == {
        "class_name": "SE1734",
        "full_name": "HoaiNam",
        "student_code": "HN",
    }


def test_rewrite_add_student_leaves_attendance_marking_alone():
    from app.ai.ollama import rewrite_add_student_intent

    calls = [
        {
            "call_id": "x",
            "name": "update_attendance",
            "arguments": '{"student": "HN", "status": "present", "class_name": "SE1734"}',
        }
    ]
    rewritten = rewrite_add_student_intent(calls, "HN present in SE1734")
    assert rewritten[0]["name"] == "update_attendance"


def test_split_response_recovers_nested_function_object():
    content = (
        '{"type":"function","function":{"name":"create_class",'
        '"arguments":{"name":"Lop7","daily_tuition_fee":50000}}}'
    )
    calls, text = split_response({"message": {"role": "assistant", "content": content}})

    assert text == ""
    assert calls[0]["name"] == "create_class"
    assert "Lop7" in calls[0]["arguments"]
