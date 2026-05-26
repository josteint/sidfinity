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
    # When True, swap the "base vs +ARP_OFS" sense in fx_arp:
    # `frame_ctr & ARP_MASK == 0` → +ARP_OFS (instead of base).
    # One Man and his Droid uses `frame_ctr & $04 == 0` → +12, the
    # inverse of every other engine. Default False.
    arp_phase_invert: bool = False
    linear_pw_or: int = 0           # OR mask on linear-PW pw_lo (Chimera $40)
    vib_onset: int = 6              # min note dur for vibrato to apply
    has_sfx: bool = False           # engine has a sound-effect sub-engine
    extract_sfx: Optional[Callable] = None   # extract_sfx(path) -> (list, ...)
    # fx-bit1 "inc-by-2" slide — Commando ramps +2 on odd frames; Devils
    # Galop's init patches INC->DEC, so it ramps -1 every frame.
    incby2_step: int = 2
    incby2_every_frame: bool = False
    incby2_onset: int = 3           # min note dur for the fx-bit-1 slide
    # "Late-in-note" gate: if set, the slide only fires when the v_dur
    # countdown is < incby2_late_gate frames. Hunter Patrol uses this
    # (gate=9) — its skydive runs only in the tail of long notes.
    # None = no late gate (the slide fires for the whole note).
    incby2_late_gate: Optional[int] = None
    # Initial value of the music frame counter. After init the codegen
    # writes this to zp `frame_ctr`; the first play() call INCs it.
    # Default $FF gives frame_ctr=0 on frame 0 (the song_interp model).
    # Hunter Patrol's binary ships $A426=$1E, giving frame_ctr=$1F on
    # frame 0 — an OFF parity from the default that arp/skydive observe.
    frame_ctr_init: int = 0xFF
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
    # True if the engine reads its per-voice init state from the freq-
    # table overlap region (+205, +208, +214, +229, +232, +239 past the
    # 96-entry table). All standard Hubbard '85 engines do this; Human
    # Race is the exception — its engine init at $1A9C zeros v_inst etc.
    # at runtime, so seeding from the overlap bytes leaks wrong values.
    seed_overlap: bool = True
    # Master-volume fade driven by a voice's pattern-progress counter.
    # When `master_vol_subtrahend_voice` is set (0=V1, 1=V2, 2=V3), the
    # codegen maintains an 8-bit counter that ticks +1 each time that
    # voice's orderlist position advances (i.e. on every pattern-end);
    # the counter NEVER wraps on song-loop. On every instrument-change
    # note (any voice) the codegen emits `STA $D418, clamp(base-counter,
    # 0..$0F)`. This reproduces Hubbard's late-song fade-out, where
    # `clamp($A0 - V2_orderpos, 0..$0F)` drops below $0F once V2 has
    # advanced past the master_vol_base ($A0) - $0F = $91 patterns.
    # Confuzion uses this with `subtrahend_voice=1, base=$A0`. See
    # [[project_hubbard_song_end_fade]] in memory for the analysis.
    master_vol_subtrahend_voice: Optional[int] = None
    master_vol_base: int = 0xA0
    # WHEN the master_VOL clamp+write fires:
    # - 'inst_change'  → only on notes that change instrument (Confuzion's
    #                    bit-7 path at $094C BPL skip).
    # - 'every_note'   → on every non-tie note load (TOAS's unconditional
    #                    master_VOL block at $C0C0-$C0CC after every dur
    #                    read in the new-note path).
    master_vol_trigger: str = 'inst_change'
    # When True, the codegen's note_codec emits the v_drumtrig clear
    # ONLY in the non-tie path of ln_decode — matching Confuzion's
    # `$807C: STA $841A,X` which the tie's `BVS $80C0` jumps over.
    # When False, the clear is unconditional at the top of ln_decode
    # (pre-9828b37 behaviour). False is the safer default because some
    # engines (Monty, Chimera) emit pattern bytes that our extract
    # decodes as porta but the engine doesn't run a per-note slide on,
    # and the OLD unconditional-clear behaviour matched their output;
    # only Confuzion / Battle of Britain (and any future engine that
    # explicitly preserves the slide across ties) should set this.
    tie_preserves_slide: bool = False
