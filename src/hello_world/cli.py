"""Console entry point for hello-world."""

from __future__ import annotations

import argparse
import sys

from hello_world import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hello-world")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.parse_args(argv)
    print(f"Hello, World! ({__version__})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
