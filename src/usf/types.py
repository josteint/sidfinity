"""USF v2 — AST / model dataclasses.

These are what the parser yields and the writer accepts. See
docs/usf_v2_format.md for the on-disk format the dataclasses
correspond to.

Conventions:
- Integers are Python ints. The on-disk distinction between decimal
  and hex is purely lexical — the writer chooses a format based on
  the field (addresses + masks → hex, counts + durations → decimal).
- Instrument refs in note rows are `InstrumentRef` (id or name);
  reference resolution to a concrete instrument happens during
  validation, not parsing.
- Pitch is `Pitch` (note name + octave) or the rest sentinel.
- `dur_field`, `pwm_period`, `slide_v`, etc. are 8-bit raw values;
  the typing is `int` and the writer emits as hex.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union


# ---------------------------------------------------------------------------
# Pitch + instrument refs (used inside note rows)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Pitch:
    """A note name + octave, or rest."""
    name: str         # 'C', 'D#', 'F', ... or '---' for rest
    octave: int       # 0-7, ignored for rest

    @property
    def is_rest(self) -> bool:
        return self.name == '---'

    @classmethod
    def rest(cls) -> 'Pitch':
        return cls(name='---', octave=0)

    def __str__(self) -> str:
        if self.is_rest:
            return '---'
        # `C-5` for natural, `C#5` for sharp
        sep = self.name[1] if len(self.name) == 2 else '-'
        letter = self.name[0]
        return f'{letter}{sep}{self.octave}'


@dataclass(frozen=True)
class InstrumentRef:
    """A reference to an instrument by id (`i1`) or name (`i:lead`).

    Resolution to a concrete `Instrument` happens during validation.
    """
    id: Optional[int] = None
    name: Optional[str] = None

    def __post_init__(self):
        if (self.id is None) == (self.name is None):
            raise ValueError('InstrumentRef must have exactly one of id/name')

    def __str__(self) -> str:
        return f'i{self.id}' if self.id is not None else f'i:{self.name}'


# ---------------------------------------------------------------------------
# Pattern + note rows
# ---------------------------------------------------------------------------

@dataclass
class NoteRow:
    """One row inside a pattern body."""
    pitch: Pitch
    duration: int
    instr: Optional[InstrumentRef] = None
    fx_flags: tuple = ()  # tuple of strings — 'tie', 'fx:drum', etc.


@dataclass
class Pattern:
    """A named pattern inside a voice block."""
    id: int
    length: int          # declared length in ticks (validated against sum of durations)
    rows: list[NoteRow] = field(default_factory=list)


@dataclass
class Orderlist:
    """A voice's orderlist of pattern ids, with loop/stop terminator."""
    entries: list[int] = field(default_factory=list)
    loop_to: Optional[int] = None      # position to jump to after the list
    stop: bool = False                  # true iff terminator is `stop`

    def __post_init__(self):
        if self.loop_to is not None and self.stop:
            raise ValueError('Orderlist cannot be both looping and stopping')


@dataclass
class VoiceBlock:
    """One of the three voice blocks inside a music subtune."""
    id: int                  # 1, 2, or 3
    orderlist: Orderlist
    patterns: list[Pattern] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Subtunes
# ---------------------------------------------------------------------------

@dataclass
class MusicSubtune:
    """A 3-voice music subtune.

    `params` is an optional per-subtune parameter override. When the
    engine has subtunes that vary in engine-level parameters (e.g. 5
    Title Tunes' 5 sub-engines have different speed_ctr_init,
    incby2_step, late_gate values), each subtune carries its own
    params block. The codegen builds per-subtune tables and the engine
    looks up by current subtune index instead of using compile-time
    constants. When None (most engines), top-level Params applies.
    """
    id: int
    tempo: int
    voices: list[VoiceBlock] = field(default_factory=list)
    params: 'Params | None' = None
    # Per-subtune init override. When set, overrides the top-level
    # `init` for this subtune (the codegen emits subOvseed_<sub> from
    # each subtune's init, and at runtime copies the selected one into
    # the engine's ovseed block). Used by unified-engine builds
    # (5 Title Tunes) where each sub's per-voice load-time state
    # differs. When None (most engines), top-level init applies.
    init: 'InitState | None' = None
    kind: str = 'music'


@dataclass
class DigiSubtune:
    """A digi subtune — a single sample reference."""
    id: int
    sample: str          # filename, relative to the .usf file
    kind: str = 'digi'


@dataclass
class SfxSubtune:
    """A Hubbard '85 sound-effect subtune.

    The engine's SFX record is a 2-voice SID-register snapshot + a
    freq-table pitch sweep. The 16-byte raw record is decomposed into
    these semantic fields:

    `v1` and `v2` are 6 bytes each — freq_hi, pw_lo, pw_hi, ctrl, ad,
    sr. The v1.freq_lo byte is aliased with `start_index`, so it's
    derived not stored. The v2.freq_lo byte is aliased with the gate
    flags + `v2_offset`, so it's also derived.

    `start_index` / `end_index` index into the engine's freq table for
    the sweep. `rate` is 0-15 (the sweep advances every `rate+1`
    frames). `direction` is 'up' or 'down'. `v2_offset` is 0-63 —
    V2's freq-table offset relative to V1's sweep index.

    Flags (booleans): `toggle_v1`, `toggle_v2` retrigger each voice's
    gate per sweep step; `skip_v1`, `skip_both` suppress freq writes.
    """
    id: int
    v1: tuple = (0, 0, 0, 0, 0, 0)       # freq_hi, pw_lo, pw_hi, ctrl, ad, sr
    v2: tuple = (0, 0, 0, 0, 0, 0)
    start_index: int = 0
    end_index: int = 0
    rate: int = 0                         # 0..15
    direction: str = 'down'               # 'up' or 'down'
    v2_offset: int = 0                    # 0..63
    toggle_v1: bool = False
    toggle_v2: bool = False
    skip_v1: bool = False
    skip_both: bool = False
    kind: str = 'sfx'


Subtune = Union[MusicSubtune, DigiSubtune, SfxSubtune]


# ---------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------

@dataclass
class PwmConfig:
    """Pulse-width modulation per-instrument config.

    Existing fields (Hubbard '85 / clever_music): `mode`, `speed`,
    `init`, `min_hi`, `max_hi` describe a single-phase linear or
    bidirectional oscillation.

    Phase 1 addition (jay_derrett's two-phase shape): `phase1_*`
    fields describe an initial sweep (ADC/SBC against `phase1_bound`
    with `phase1_step` per frame), after which the engine
    transitions to bidirectional oscillation between min_hi/max_hi.
    For one-phase engines `phase1_*` defaults leave it inactive.
    """
    mode: str = 'none'           # 'none' | 'linear' | 'bidirectional'
    speed: int = 0
    init: int = 0
    min_hi: int = 0
    max_hi: int = 0
    # Two-phase modulation (jay_derrett); defaults make it inactive.
    phase1_dir: str = 'up'       # 'up' (ADC) or 'down' (SBC)
    phase1_bound: int = 0
    phase1_step: int = 0


@dataclass
class ArpConfig:
    """Arpeggio per-instrument config.

    `offsets` is the per-step semitone delta list (already per-inst).
    `period`, `interval`, `phase_invert` were previously held as
    per-tune `params { }` values shared across all instruments; the
    Phase 1 refactor moves them per-instrument per the USF
    representation principle. For Hubbard engines that only realize
    one value tune-wide, the extract path copies the per-tune value
    onto every instrument.

      `period`       — frame-counter mask + 1. The existing field —
                       previously dead (composer read `params.arp_period`
                       instead). Default 1 is the schema-historical
                       value; Phase 2 fills with engine actuals.
      `interval`     — semitones added per arpeggio step.
      `phase_invert` — invert frame-parity phase (One Man and his
                       Droid).
    """
    offsets: list[int] = field(default_factory=list)
    period: int = 1
    interval: int = 12
    phase_invert: bool = False


@dataclass
class VibratoConfig:
    """Vibrato per-instrument config.

    `scale` is depth (already per-inst). `onset` was previously held
    as per-tune `params.vib_onset`; the Phase 1 refactor moves it
    per-instrument. Default 6 matches the codebase's prior fallback.
    """
    scale: int = 0
    onset: int = 6


@dataclass
class EnvelopeConfig:
    """Per-instrument envelope-shape extras.

    `release_ctrl` is the CTRL byte the engine writes during release
    (gate-off / note-off phase). Universal across engines — Hubbard
    realizes it via delta arithmetic, jay_derrett via OR'd byte;
    both produce the same SID write. Schema carries the musical
    content (the resulting byte), not the mechanism.
    """
    release_ctrl: int = 0


@dataclass
class FreqSlideConfig:
    """Per-instrument freq slide / sweep — replaces the per-engine-
    parameterized `freq_slide: bool` flag.

    Modes:
      'none'           — no slide.
      'one_shot_halt'  — slide toward bound 1; at bound, step → 0
                         (freq frozen). Hubbard '85's skydive shape.
      'one_shot_swap'  — slide toward bound 1; at bound, snap to
                         bound 2's freq.
      'bidirectional'  — slide toward bound 1; at bound, flip
                         direction; slide toward bound 2; flip; repeat.

    Bounds are SIGNED 16-bit deltas from the note's freq-table value
    (the engine adds them at note-start to get absolute target freqs).

    `high_oct_arp` selects the high-octave freq variant
    (`freq_table[note + 16]`) as the SID write source after the
    first bound crossing — jay_derrett's bound-crossing arpeggio.
    """
    mode: str = 'none'           # 'none' | 'one_shot_halt' |
                                 # 'one_shot_swap' | 'bidirectional'
    initial_dir: str = 'up'      # 'up' (ADC) or 'down' (SBC)
    upper_delta: int = 0         # SIGNED 16-bit
    lower_delta: int = 0         # SIGNED 16-bit
    step: int = 0                # 16-bit unsigned
    high_oct_arp: bool = False


@dataclass
class IncBy2Config:
    """Per-instrument odd-frame freq-hi ramp — replaces the per-
    engine-parameterized `inc_by2: bool` flag.

    Modes:
      'none'        — no ramp.
      'on'          — ramp active for the whole note.
      'late_gated'  — ramp halts when v_dur < `late_gate`.

    `step` is the per-(odd-)frame freq_hi delta (signed 8-bit;
    +2 = $02, -1 = $FF). `onset` is the frame delay before ramp
    starts. `late_gate` is the v_dur threshold below which the ramp
    halts (only consulted when mode='late_gated').
    """
    mode: str = 'none'           # 'none' | 'on' | 'late_gated'
    step: int = 1                # signed 8-bit
    onset: int = 0
    late_gate: int = 0


@dataclass
class Instrument:
    id: int
    name: Optional[str] = None
    waveform: list[int] = field(default_factory=list)
    loop: int = 0
    pwm: PwmConfig = field(default_factory=PwmConfig)
    adsr: tuple = (0, 0)             # (ad, sr)
    arp: ArpConfig = field(default_factory=ArpConfig)
    vibrato: VibratoConfig = field(default_factory=VibratoConfig)
    envelope: EnvelopeConfig = field(default_factory=EnvelopeConfig)
    # Per-instrument musical-effect configs. The engine's fx_flags
    # byte (bit 0 = freq_slide, bit 1 = inc_by2, bit 2 = arpeggio,
    # bit 3 = pwm-linear) is derived at codegen time:
    #   bit 0 ← freq_slide_config.mode != 'none'
    #   bit 1 ← inc_by2_config.mode    != 'none'
    #   bit 2 ← arp.offsets has > 1 entry
    #   bit 3 ← pwm.mode == 'linear'
    freq_slide_config: FreqSlideConfig = field(default_factory=FreqSlideConfig)
    inc_by2_config: IncBy2Config = field(default_factory=IncBy2Config)


# ---------------------------------------------------------------------------
# Init state + params + psid
# ---------------------------------------------------------------------------

@dataclass
class InitVoice:
    """Per-voice initial state at engine init. Field set is a superset
    of what any one engine needs — unused fields stay at their defaults
    and the codegen ignores them.
    """
    id: int
    ctrl: int = 0
    dur_field: int = 0
    pwm_period: int = 0
    pwm_dir: str = 'up'          # 'up' or 'down'
    instr: Optional[InstrumentRef] = None
    slide_v: int = 0


# ---------------------------------------------------------------------------
# SID-chip priming — `init.sid { ... }` block
# ---------------------------------------------------------------------------
# Per `docs/sid_init_report.md` (reset / priming / environment trichotomy):
# these fields capture the chip-state priming the engine performs during
# init, distinct from the engine's runtime voice_state (above). The
# composer's universal init reads these and emits the corresponding SID
# writes; default values mean "don't prime."

@dataclass
class InitFilter:
    """Filter priming. Composer writes $D415/$D416/$D417 when at least
    one field is non-default.
    """
    cutoff_lo: int = 0
    cutoff_hi: int = 0
    res_routing: int = 0


@dataclass
class InitSidVoice:
    """Per-voice SID-chip priming the engine performs at init time
    independent of any instrument-bound note.

    `envelope_prime`: writes (ad, sr) to $D405/$D406 (V1), $D40C/$D40D
    (V2), or $D413/$D414 (V3). Bowden's hardcoded V1/V2 AD/SR primes
    live here (`($09, $00)`).

    `pw_init`: writes (lo, hi) to $D402/$D403 (V1), $D409/$D40A (V2),
    or $D410/$D411 (V3). For raw-register pulse-width priming
    independent of any instrument's `pwm.init`.

    Fields are `None` = "don't prime this slot."
    """
    id: int
    envelope_prime: Optional[tuple] = None  # (ad, sr) or None
    pw_init: Optional[int] = None           # 16-bit pulse-width or None


@dataclass
class InitSid:
    """SID-chip priming. The composer's universal init reads this and
    emits the writes after the silence-clear reset. Default = no
    priming (composer emits only the universal reset baseline).
    """
    master_vol: Optional[int] = None        # None = composer default ($0F)
    filter: Optional[InitFilter] = None
    voices: list = field(default_factory=list)  # list[InitSidVoice]


@dataclass
class InitState:
    voices: list[InitVoice] = field(default_factory=list)
    sid: Optional[InitSid] = None           # SID-chip priming (new schema)


@dataclass
class Params:
    """Engine-specific config. Stored as `dict[str, Any]` to keep the
    schema flexible across engines; the codegen knows its required
    keys and types.
    """
    fields: dict = field(default_factory=dict)


@dataclass
class SongEndConfig:
    """End-of-orderlist behavior for both terminator markers.

    Each voice's orderlist ends with either a STOP marker (engine's
    `$FE`) or a LOOP marker (engine's `$FF` → loop back to a position
    within the orderlist). The TUNE-LEVEL `song_end` block specifies
    what those markers actually DO at end-of-list time:

      `stop_marker`:
        'silence'  — voice silences (default — Hubbard standard).
        'freeze'   — voice freezes on its last note (note hangs;
                     effects continue; never gates off).
        'fill'     — voice writes `fill_value` to its 7-byte SID
                     register block, then silences. Used for engines
                     that want a specific outro byte (Action Biker
                     writes `$80` to set noise+gate-off).

      `fill_value`: only consulted when stop_marker='fill'.

      `loop_marker`:
        'loop'         — voice wraps to its loop_to position (default).
        'silence_all'  — when ANY voice hits its loop marker, the
                         entire song silences. Used for engines whose
                         loop kills the song (Hunter Patrol).

    Defaults = Hubbard standard behavior; song_end is optional in USF.
    """
    stop_marker: str = 'silence'      # 'silence' | 'freeze' | 'fill'
    fill_value: int = 0                # only used when stop_marker='fill'
    loop_marker: str = 'loop'          # 'loop' | 'silence_all'


@dataclass
class PsidMeta:
    title: str = ''
    author: str = ''
    released: str = ''
    clock: str = 'PAL'           # 'PAL' | 'NTSC' | 'both' | 'unknown'
    sid: int = 6581              # 6581 | 8580 (0 = unknown, both = ?)
    start_song: int = 1
    # PSID v2 speed field: 32-bit bitmask, bit N = subtune (N+1)'s
    # play() dispatch. 0 = VBI (50/60 Hz), 1 = CIA1 timer (typically
    # the same rate unless the init routine reprograms it). Subtunes
    # past bit 31 inherit bit 31. Default 0 = all VBI.
    speed: int = 0


# ---------------------------------------------------------------------------
# Top-level USF file
# ---------------------------------------------------------------------------

@dataclass
class UsfFile:
    """The full in-memory representation of a .usf file.

    The Hubbard build path requires `freq_table is not None` (the
    self-contained shape). Pipelines with their own build paths (e.g.
    the Companion strain) may use other field combinations.
    """
    psid: PsidMeta
    params: Params
    init: InitState
    instruments: list[Instrument] = field(default_factory=list)
    subtunes: list[Subtune] = field(default_factory=list)
    # Per-tune freq table (v3 only). 320 bytes — first 192 are the
    # musical PAL table, last 128 are engine state/scratch.
    freq_table: Optional[list[int]] = None
    # Off-table-arp statebuf layout (v3 only). Default = the Commando
    # 3-voice family layout; Human Race overrides with a 2-voice
    # layout. Parsed shape: {'n_voices': int, 'scalars': list[dict],
    # 'per_voice': list[dict]} where each dict has offset + kind +
    # (value or var). The build path constructs a StatebufLayout
    # from this dict.
    state_layout: Optional[dict] = None
    # Song-end behavior — replaces the three flat params keys
    # `freeze_on_stop`/`stop_fill`/`loop_silences_song`. When None,
    # composer uses defaults (silence + loop).
    song_end: Optional[SongEndConfig] = None
