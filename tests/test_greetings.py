from __future__ import annotations

from hello_world.greetings import format_greeting
from hello_world.models import GreetingStyle


def test_format_greeting_default() -> None:
    assert format_greeting() == "Hello, World!"


def test_format_greeting_casual_with_name() -> None:
    assert format_greeting(name="Alice") == "Hello, Alice!"


def test_format_greeting_formal_with_name() -> None:
    greeting = format_greeting(name="Alice", style=GreetingStyle.FORMAL)
    assert greeting == "Good day, Alice."


def test_format_greeting_formal_default_name() -> None:
    assert format_greeting(style=GreetingStyle.FORMAL) == "Good day, World."
