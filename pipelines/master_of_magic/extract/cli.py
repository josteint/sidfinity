"""Command-line entry point for the MasterOfMagic extract pipeline.

Usage:
    python -m pipelines.master_of_magic.extract                   # alias for `cli`
    python -m pipelines.master_of_magic.extract.cli               # explicit
    python -m pipelines.master_of_magic.extract.cli 0,1,2         # all three music subtunes
    python -m pipelines.master_of_magic.extract.cli -v 0          # subtune 0, debug-level logs

Options:
    subtunes           Comma-separated 0-indexed subtune numbers (default 0)
    -v, --verbose      Enable DEBUG-level logging during extraction
    -h, --help         Show this help and exit
"""
from __future__ import annotations

import argparse
import logging
import sys

from . import emit_usf


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m pipelines.master_of_magic.extract",
        description=(
            "Read the original MasterOfMagic on the Run SID, extract one or more "
            "subtunes, and write SongData.lean for the Lean codegen."
        ),
    )
    parser.add_argument(
        "subtunes",
        nargs="?",
        default="0",
        help="Comma-separated 0-indexed subtune list (default: 0).",
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
    emit_usf.main([args.subtunes])
    return 0


if __name__ == "__main__":
    sys.exit(main())
