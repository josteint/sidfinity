"""Command-line entry point for the Dragon's Lair Part II extract pipeline.

Usage:
    python -m pipelines.dragons_lair_part_ii.extract        # full structural emit
    python -m pipelines.dragons_lair_part_ii.extract -v     # with debug logging
    # alternate paths (call directly when you want only one piece):
    python -m pipelines.dragons_lair_part_ii.extract.dl2_decompile
    python -m pipelines.dragons_lair_part_ii.extract.emit_engine_image
    python -m pipelines.dragons_lair_part_ii.extract.emit_usf_dl2

This runs **both** emitters: the structural USF emitter
(`emit_usf_dl2`) which writes `SongData.lean`, and the verbatim
engine-image emitter (`emit_engine_image`) which writes
`EngineImage.lean`. Main.lean currently reads only `EngineImage.lean`;
`SongData.lean` is a structural checkpoint for the in-progress
structural codegen.
"""
from __future__ import annotations

import argparse
import logging
import sys

from . import emit_engine_image, emit_usf_dl2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m pipelines.dragons_lair_part_ii.extract",
        description=(
            "Read the original Dragon's Lair Part II SID and write both "
            "SongData.lean (structural USF) and EngineImage.lean (verbatim "
            "binary) for the Lean codegen."
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
    emit_usf_dl2.main()
    emit_engine_image.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
