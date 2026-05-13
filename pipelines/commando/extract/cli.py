"""Command-line entry point for the Commando extract pipeline.

Usage:
    python -m pipelines.commando.extract       # alias for `cli`
    python -m pipelines.commando.extract.cli   # explicit

Options:
    -v, --verbose      Enable DEBUG-level logging during extraction
    -h, --help         Show this help and exit

This is a thin wrapper around `emit_usf.main()`. Use it instead of invoking
emit_usf directly when you want CLI flag parsing.
"""
from __future__ import annotations

import argparse
import logging
import sys

from . import emit_usf


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m pipelines.commando.extract",
        description=(
            "Read the original Commando SID, extract its musical data, "
            "and write SongData.lean for the Lean codegen to consume."
        ),
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging during extraction.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )
    emit_usf.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
