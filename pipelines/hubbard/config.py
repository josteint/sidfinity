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
    arp_period: int = 2             # arp cycle length: phase 0 = base note
    linear_pw_or: int = 0           # OR mask on linear-PW pw_lo (Chimera $40)
    vib_onset: int = 6              # min note dur for vibrato to apply
    has_sfx: bool = False           # engine has a sound-effect sub-engine
    extract_sfx: Optional[Callable] = None   # extract_sfx(path) -> (list, ...)
    # fx-bit1 "inc-by-2" slide — Commando ramps +2 on odd frames; Devils
    # Galop's init patches INC->DEC, so it ramps -1 every frame.
    incby2_step: int = 2
    incby2_every_frame: bool = False
    incby2_onset: int = 3           # min note dur for the fx-bit-1 slide
    # the $178B drum-priority gate suppresses the very first voice's
    # first-frame note-start SID writes (Devils Galop only).
    suppress_first_notestart: bool = False
    # the $FE orderlist marker freezes the voice (holds the last note,
    # keeps effects, never gates off) rather than ending the song.
    freeze_on_stop: bool = False
    # initial speed counter — 1 defers the first tick (and the first
    # note-load) to play frame 1 (Action Biker's $C3E7/$C3E8 gate).
    speed_ctr_init: int = 0
    # write ctrl=0 to all three voices on play frame 0 (engines whose
    # first-frame setup runs in play, not init).
    first_frame_gate_off: bool = False
    # per-subtune voice-loop start index (Action Biker subtune 0 skips
    # V3 — $C3F2). Empty = every subtune starts at V3 (index 2).
    voice_starts: tuple = ()
    # if set, the $FE marker ends the song by writing this byte to
    # every voice register, then silence (Action Biker's $C2DC, $80).
    stop_fill: Optional[int] = None
    # freq-table offset where the SFX engine keeps its state block, for
    # engines whose SFX sweep overruns the table into engine state
    # (Monty: $84FB = freqtab+251). None = Commando's scattered layout.
    sfx_state_ofs: Optional[int] = None
    # freq-table offset of the SFX-readable frame counter INC'd each
    # play call (Commando $5525 = freqtab+253; Monty $84FA = +250).
    sfx_framectr_ofs: int = 253
    # PSID subtune indices whose subtune is a digi sample, not a music
    # tune or a SID-synthesis SFX. Verified cycle-strict via siddump
    # --writelog (not the frame-granular py65 capture). Chimera: (2, 3).
    digi_subtunes: tuple = ()
    # the rebuilt SID is RSID (KERNAL-mapped, IRQ-driven). Used by
    # writelog capture (siddump requires --force-rsid) and any future
    # build that emits the RSID header. Chimera is RSID; the standard
    # Hubbard engines are PSID.
    is_rsid: bool = False
