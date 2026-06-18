"""Console entry point for hello-world."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from hello_world import __version__
from hello_world.greetings import format_greeting
from hello_world.models import GreetingStyle, TextStats
from hello_world.text_stats import analyze_text


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hello-world")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    greet_parser = subparsers.add_parser("greet", help="Print a greeting")
    greet_parser.add_argument(
        "--name",
        help="Name to greet (default: World)",
    )
    greet_parser.add_argument(
        "--style",
        choices=[style.value for style in GreetingStyle],
        default=GreetingStyle.CASUAL.value,
        help="Greeting style",
    )

    stats_parser = subparsers.add_parser("stats", help="Show text statistics")
    stats_group = stats_parser.add_mutually_exclusive_group(required=True)
    stats_group.add_argument(
        "text",
        nargs="?",
        help="Text to analyze",
    )
    stats_group.add_argument(
        "--file",
        type=Path,
        help="Read text from a file",
    )

    return parser


def _render_stats_table(stats: TextStats) -> Table:
    table = Table(title="Text statistics")
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    table.add_row("Lines", str(stats.lines))
    table.add_row("Words", str(stats.words))
    table.add_row("Characters", str(stats.characters))
    table.add_row("Longest word", stats.longest_word or "-")

    return table


def _run_greet(args: argparse.Namespace) -> int:
    style = GreetingStyle(args.style)
    print(format_greeting(name=args.name, style=style))
    return 0


def _run_stats(args: argparse.Namespace) -> int:
    if args.file is not None:
        text = args.file.read_text(encoding="utf-8")
    else:
        text = args.text or ""

    stats = analyze_text(text)
    console = Console()
    console.print(_render_stats_table(stats))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "greet":
        return _run_greet(args)
    if args.command == "stats":
        return _run_stats(args)

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
