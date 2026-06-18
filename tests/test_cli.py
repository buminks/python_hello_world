from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from hello_world import __version__
from hello_world.cli import main


def test_version_is_non_empty() -> None:
    assert __version__
    assert isinstance(__version__, str)


def test_main_greet_default(capsys) -> None:
    assert main(["greet"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World!"


def test_main_greet_formal(capsys) -> None:
    assert main(["greet", "--name", "Alice", "--style", "formal"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "Good day, Alice."


def test_main_stats_text(capsys) -> None:
    assert main(["stats", "one two three"]) == 0
    captured = capsys.readouterr()
    assert "Text statistics" in captured.out
    assert "3" in captured.out


def test_main_stats_file(tmp_path: Path, capsys) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("alpha beta\ngamma", encoding="utf-8")

    assert main(["stats", "--file", str(sample)]) == 0
    captured = capsys.readouterr()
    assert "Text statistics" in captured.out
    assert "alpha" in captured.out or "5" in captured.out


def test_cli_version_flag() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "hello_world", "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "hello-world" in result.stdout
    assert __version__ in result.stdout


def test_cli_greet_subcommand() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "hello_world", "greet", "--name", "CI"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "Hello, CI!"


def test_cli_stats_subcommand() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "hello_world", "stats", "demo"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Text statistics" in result.stdout
    assert "1" in result.stdout
