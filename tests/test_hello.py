from __future__ import annotations

import subprocess
import sys

from hello_world import __version__
from hello_world.cli import main


def test_version_is_non_empty() -> None:
    assert __version__
    assert isinstance(__version__, str)


def test_main_prints_hello(capsys) -> None:
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out
    assert __version__ in captured.out


def test_cli_version_flag() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "hello_world", "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "hello-world" in result.stdout
    assert __version__ in result.stdout
