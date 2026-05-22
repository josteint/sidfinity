"""config.py — per-engine configuration for the shared Hubbard '85 core.

The reference interpreter (song_interp) and the codegen are engine-
agnostic; everything that genuinely differs between Hubbard engines
(Commando, Devils Galop, ...) is captured in an EngineConfig. Each
engine pipeline builds one of these and hands it to the shared core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class EngineConfig:
    """The per-engine deltas the shared Hubbard '85 core needs.

    `extract` returns this engine's ExtractedSong for a subtune;
    `resetspd` returns the subtune's tick divider. Both are supplied
    by the engine's own pipeline (its decompiler is engine-specific).
    """
    name: str
    sid_path: str
    instr_base: int                 # instrument-table address
    instr_count: int                # number of instruments
    extract: Callable               # extract(subtune) -> ExtractedSong
    resetspd: Callable              # resetspd(subtune, binary, load) -> int
    arp_interval: int = 12          # arpeggio interval in semitones
