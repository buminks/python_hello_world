"""Text analysis utilities."""

from __future__ import annotations

import re

from hello_world.models import TextStats

_WORD_PATTERN = re.compile(r"\b\w+\b")


def analyze_text(text: str) -> TextStats:
    """Compute line, word, and character statistics for text."""
    lines = text.splitlines()
    if not lines and text:
        lines = [text]

    words = _WORD_PATTERN.findall(text)
    longest_word = max(words, key=len) if words else ""

    return TextStats(
        lines=len(lines),
        words=len(words),
        characters=len(text),
        longest_word=longest_word,
    )
