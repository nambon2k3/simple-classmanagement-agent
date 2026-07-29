"""Tests for post-tool reply selection."""

from app.ai.agent import _should_use_tool_message_instead


def test_empty_reply_after_tools_should_use_tool_message():
    assert _should_use_tool_message_instead("")
    assert _should_use_tool_message_instead("Done.")


def test_refusal_phrases_are_detected():
    assert _should_use_tool_message_instead(
        "I'm sorry, I cannot use tools or call functions for you."
    )
    assert _should_use_tool_message_instead(
        "As an AI language model, I don't have access to tools."
    )


def test_normal_summary_is_kept():
    assert not _should_use_tool_message_instead("Class *SE401* created for you.")
