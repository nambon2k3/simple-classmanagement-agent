"""Text normalisation and fuzzy-matching helpers.

Teachers refer to students the way they speak: "John", "nguyen van a", "SE001".
These helpers turn such loose references into deterministic candidate sets so
that the *service* layer — never the language model — decides which student was
meant.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Iterable, Sequence
from difflib import SequenceMatcher

_WHITESPACE = re.compile(r"\s+")

#: Similarity below which a fuzzy candidate is discarded outright.
DEFAULT_SIMILARITY_THRESHOLD = 0.72


def strip_accents(value: str) -> str:
    """Remove diacritics so ``"Nguyễn"`` and ``"Nguyen"`` compare equal."""
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def normalize(value: str) -> str:
    """Casefold, strip accents and collapse whitespace for comparison."""
    return _WHITESPACE.sub(" ", strip_accents(value).casefold().strip())


def normalize_code(value: str) -> str:
    """Canonical form for identifiers such as student codes and class names."""
    return _WHITESPACE.sub("", value).upper()


def similarity(left: str, right: str) -> float:
    """Return a 0..1 similarity ratio between two normalised strings."""
    return SequenceMatcher(None, normalize(left), normalize(right)).ratio()


def find_matches[T](
    query: str,
    candidates: Iterable[T],
    key: Callable[[T], str],
    *,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> list[T]:
    """Rank ``candidates`` against ``query`` using a tiered matching strategy.

    Tiers are tried in order and the first non-empty tier wins, so an exact
    match is never diluted by weaker fuzzy hits:

    1. exact match on the normalised value;
    2. prefix or whole-word match (how people abbreviate names);
    3. substring match;
    4. fuzzy similarity above ``threshold``, best first.

    Args:
        query: The user's reference, e.g. ``"john"``.
        candidates: Objects to search.
        key: Extracts the comparable string from a candidate.
        threshold: Minimum similarity for the fuzzy tier.

    Returns:
        Matching candidates, best first.  Empty when nothing is close enough.
        More than one result means the reference was ambiguous.
    """
    needle = normalize(query)
    if not needle:
        return []

    items: Sequence[tuple[T, str]] = [(item, normalize(key(item))) for item in candidates]

    exact = [item for item, value in items if value == needle]
    if exact:
        return exact

    word_matches = [
        item
        for item, value in items
        if value.startswith(needle) or any(word == needle for word in value.split())
    ]
    if word_matches:
        return word_matches

    substring = [item for item, value in items if needle in value]
    if substring:
        return substring

    scored = [(item, SequenceMatcher(None, needle, value).ratio()) for item, value in items]
    fuzzy = sorted(
        ((item, score) for item, score in scored if score >= threshold),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return [item for item, _ in fuzzy]


def truncate(value: str, limit: int, suffix: str = "…") -> str:
    """Shorten ``value`` to ``limit`` characters, appending ``suffix`` if cut."""
    if len(value) <= limit:
        return value
    return value[: max(0, limit - len(suffix))].rstrip() + suffix
