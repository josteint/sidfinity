"""Command-line entry point.

Usage:
    python -m pipelines.last_v8_c128.extract           # parse + emit SongData.lean
    python -m pipelines.last_v8_c128.extract -v        # same, debug logs
"""
from __future__ import annotations

import sys

from . import emit_usf


def main(argv: list[str] | None = None) -> int:
    return emit_usf.main(argv)


if __name__ == "__main__":
    sys.exit(main())
