"""Tests for the fuzzy student-reference matching helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.utils.text import find_matches, normalize, normalize_code, similarity, truncate


@dataclass
class Person:
    name: str


def names(people: list[Person]) -> list[str]:
    return [person.name for person in people]


PEOPLE = [
    Person("Nguyen Van A"),
    Person("John Smith"),
    Person("John Doe"),
    Person("Alice Nguyen"),
    Person("Nguyễn Thị B"),
]


def test_normalize_strips_accents_and_case():
    assert normalize("Nguyễn  Văn  A") == "nguyen van a"


def test_normalize_code_removes_spaces_and_uppercases():
    assert normalize_code(" se 001 ") == "SE001"


def test_exact_match_wins_over_partial():
    matches = find_matches("John Smith", PEOPLE, key=lambda p: p.name)
    assert names(matches) == ["John Smith"]


def test_first_name_matches_every_person_with_that_word():
    matches = find_matches("john", PEOPLE, key=lambda p: p.name)
    assert names(matches) == ["John Smith", "John Doe"]


def test_accent_insensitive_match():
    matches = find_matches("nguyen thi b", PEOPLE, key=lambda p: p.name)
    assert names(matches) == ["Nguyễn Thị B"]


def test_substring_match_when_no_word_matches():
    matches = find_matches("smi", PEOPLE, key=lambda p: p.name)
    assert names(matches) == ["John Smith"]


def test_typo_falls_back_to_fuzzy_matching():
    matches = find_matches("alise nguyen", PEOPLE, key=lambda p: p.name)
    assert names(matches)[0] == "Alice Nguyen"


def test_no_match_returns_empty():
    assert find_matches("zzzzzz", PEOPLE, key=lambda p: p.name) == []


def test_blank_query_returns_empty():
    assert find_matches("   ", PEOPLE, key=lambda p: p.name) == []


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [("john", "john", 1.0), ("john", "", 0.0)],
)
def test_similarity_bounds(left: str, right: str, expected: float):
    assert similarity(left, right) == pytest.approx(expected)


def test_truncate_appends_suffix_only_when_needed():
    assert truncate("short", 10) == "short"
    assert truncate("a very long name indeed", 10).endswith("…")
    assert len(truncate("a very long name indeed", 10)) <= 10
