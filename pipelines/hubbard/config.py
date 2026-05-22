"""config.py — per-engine configuration for the shared Hubbard '85 core.

The reference interpreter (song_interp) and the codegen are engine-
agnostic; everything that genuinely differs between Hubbard engines
(Commando, Devils Galop, ...) is captured in an EngineConfig. Each
engine pipeline builds one of these and hands it to the shared core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class EngineConfig:
    """The per-engine deltas the shared Hubbard '85 core needs.

    `extract` returns this engine's ExtractedSong for a subtune;
    `resetspd` returns the subtune's tick divider; `extract_sfx`
    (only when `has_sfx`) returns the sound-effect table. These are
    supplied by the engine's own pipeline — its decompiler is
    engine-specific.
    """
    name: str
    sid_path: str
    instr_base: int                 # instrument-table address
    instr_count: int                # number of instruments
    freq_table_base: int            # freq-table address in the binary
    extract: Callable               # extract(subtune) -> ExtractedSong
    resetspd: Callable              # resetspd(subtune, binary, load) -> int
    subtunes: tuple = (0,)          # music subtunes to pack
    arp_interval: int = 12          # arpeggio interval in semitones
    vib_onset: int = 6              # min note dur for vibrato to apply
    has_sfx: bool = False           # engine has a sound-effect sub-engine
    extract_sfx: Optional[Callable] = None   # extract_sfx(path) -> (list, ...)
    # fx-bit1 "inc-by-2" slide — Commando ramps +2 on odd frames; Devils
    # Galop's init patches INC->DEC, so it ramps -1 every frame.
    incby2_step: int = 2
    incby2_every_frame: bool = False
    # the $178B drum-priority gate suppresses the very first voice's
    # first-frame note-start SID writes (Devils Galop only).
    suppress_first_notestart: bool = False
