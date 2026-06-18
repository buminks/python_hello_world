"""Domain models for hello-world."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GreetingStyle(Enum):
    """Supported greeting styles."""

    CASUAL = "casual"
    FORMAL = "formal"


@dataclass(frozen=True)
class TextStats:
    """Statistics computed from a block of text."""

    lines: int
    words: int
    characters: int
    longest_word: str
