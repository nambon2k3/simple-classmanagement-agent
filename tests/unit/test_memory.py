"""Tests for conversation memory and its expiry rules."""

from __future__ import annotations

from datetime import timedelta

from app.ai.memory import ConversationState, InMemoryConversationStore
from app.utils.datetime_utils import utc_now


async def test_get_or_create_returns_the_same_conversation():
    store = InMemoryConversationStore(ttl_seconds=60)
    first = await store.get_or_create(chat_id=1, teacher_id=10)
    first.focus_class_id = 5
    await store.save(first)

    second = await store.get_or_create(chat_id=1, teacher_id=10)
    assert second.focus_class_id == 5


async def test_a_different_teacher_in_the_same_chat_starts_fresh():
    store = InMemoryConversationStore(ttl_seconds=60)
    first = await store.get_or_create(chat_id=1, teacher_id=10)
    first.focus_class_id = 5
    await store.save(first)

    other = await store.get_or_create(chat_id=1, teacher_id=99)
    assert other.focus_class_id is None


async def test_expired_conversation_is_dropped():
    store = InMemoryConversationStore(ttl_seconds=60)
    state = await store.get_or_create(chat_id=1, teacher_id=10)
    state.updated_at = utc_now() - timedelta(seconds=120)

    assert await store.get(1) is None


async def test_saving_refreshes_the_expiry():
    store = InMemoryConversationStore(ttl_seconds=60)
    state = await store.get_or_create(chat_id=1, teacher_id=10)
    state.updated_at = utc_now() - timedelta(seconds=120)
    await store.save(state)

    assert await store.get(1) is not None


async def test_purge_removes_only_expired_conversations():
    store = InMemoryConversationStore(ttl_seconds=60)
    stale = await store.get_or_create(chat_id=1, teacher_id=10)
    stale.updated_at = utc_now() - timedelta(seconds=600)
    await store.get_or_create(chat_id=2, teacher_id=10)

    assert await store.purge_expired() == 1
    assert await store.get(2) is not None


async def test_clear_forgets_the_conversation():
    store = InMemoryConversationStore(ttl_seconds=60)
    await store.get_or_create(chat_id=1, teacher_id=10)
    await store.clear(1)
    assert await store.get(1) is None


def test_history_is_trimmed_to_the_limit():
    state = ConversationState(chat_id=1, teacher_id=1)
    state.extend_history([{"n": index} for index in range(10)], limit=4)
    assert state.history == [{"n": 6}, {"n": 7}, {"n": 8}, {"n": 9}]


def test_history_below_the_limit_is_kept_intact():
    state = ConversationState(chat_id=1, teacher_id=1)
    state.extend_history([{"n": 1}, {"n": 2}], limit=10)
    assert len(state.history) == 2


def test_clearing_attendance_focus_keeps_the_class_focus():
    state = ConversationState(
        chat_id=1,
        teacher_id=1,
        focus_class_id=3,
        focus_session_id=9,
        attendance_message_id=42,
    )
    state.clear_attendance_focus()
    assert state.focus_class_id == 3
    assert state.focus_session_id is None
    assert state.attendance_message_id is None
