"""Greeting message formatting."""

from __future__ import annotations

from hello_world.models import GreetingStyle


def format_greeting(
    name: str | None = None,
    style: GreetingStyle = GreetingStyle.CASUAL,
) -> str:
    """Return a greeting for the given name and style."""
    who = name or "World"
    if style is GreetingStyle.FORMAL:
        return f"Good day, {who}."
    return f"Hello, {who}!"
