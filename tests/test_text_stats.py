from __future__ import annotations

from hello_world.text_stats import analyze_text


def test_analyze_text_empty() -> None:
    stats = analyze_text("")
    assert stats.lines == 0
    assert stats.words == 0
    assert stats.characters == 0
    assert stats.longest_word == ""


def test_analyze_text_single_line() -> None:
    stats = analyze_text("Hello world")
    assert stats.lines == 1
    assert stats.words == 2
    assert stats.characters == 11
    assert stats.longest_word == "Hello"


def test_analyze_text_multiline() -> None:
    stats = analyze_text("one two\nthree")
    assert stats.lines == 2
    assert stats.words == 3
    assert stats.characters == 13
    assert stats.longest_word == "three"


def test_analyze_text_ignores_punctuation_for_words() -> None:
    stats = analyze_text("Hello, world!")
    assert stats.words == 2
    assert stats.longest_word == "Hello"
