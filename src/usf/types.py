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
    # FC family — when True, the engine treats this subtune as SFX:
    # structurally identical to music (3-voice note streams) but the
    # play loop doesn't sustain the gate on song-end. Default False
    # for music; FC's SFX subtunes (Hawkeye 6..11) set this.
    is_sfx: bool = False
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
    # Per-SFX freqtab overlay carrying the byte values the sweep reads
    # at offsets ≥ 192 — i.e. the V1/V2 frequencies this SFX emits when
    # `sfx_y = (index*2) & $FF` lands past the 96-entry musical table,
    # or when V2's `sfx_y - v2_offset` underflows into the upper region.
    # Maps freqtab byte offset → byte value. Empty when the sweep stays
    # within 0..191 throughout its run.
    extended_freq: dict = field(default_factory=dict)
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
    # OR mask applied to PW low byte every frame in linear-PWM mode
    # (Hubbard '85's `ora #LINEAR_PW_OR`). Default 0 = no OR. Chimera
    # uses $40 on its linear-PWM instruments. Per-instrument: each
    # inst's linear-PWM update gets its own mask.
    lo_or_mask: int = 0


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
    """Vibrato per-instrument config — parameterized over a musical
    basis per the USF representation principle (§4).

    Five musical knobs:

      `shape` (default 'triangle') — LFO shape. Hubbard '85 uses
        triangle always; other engines may add 'sine', 'square',
        'table' (etc.). Discrete enum — values generalize across
        engines.

      `period_frames` (default 8) — LFO period in PAL frames. Hubbard
        hardcodes 8 (counter ANDed with $07 then folded). Other
        engines may differ.

      `polarity` (default 'unipolar') — 'unipolar' = modulation only
        upward from base freq; 'bipolar' = symmetric around base.
        Hubbard is unipolar.

      `scale` — depth control. For Hubbard the byte value is a
        right-shift count: actual modulation amplitude is approximately
        `(freq_table[pitch+1] - freq_table[pitch]) >> (scale+1)` per
        step, so larger scale = SMALLER modulation. The scale=0 case
        modulates by half a semitone per step.

      `onset` (default 6) — frames of note duration before vibrato
        kicks in. Below this duration counter, vibrato is gated off.

    FC v1 additions (`amplitude`/`speed`/`direction`) carry FC's
    fx1-byte decomposition. They coexist with Hubbard's scale/onset/etc;
    each engine populates the subset it uses.
    """
    scale: int = 0
    onset: int = 6
    shape: str = 'triangle'      # 'triangle' | 'sine' | 'square' | 'table' | ...
    period_frames: int = 8
    polarity: str = 'unipolar'    # 'unipolar' | 'bipolar'
    # Max modulation amplitude in semitones (descriptive metadata
    # derived from `scale` at extract time). For Hubbard the asm's
    # right-shift loop yields amplitude = 3 / 2^(shifts), where
    # `shifts` depends on `scale` in a non-trivial way (see
    # pipelines/hubbard/to_usf._scale_byte_to_depth_semitones).
    # Composer uses `scale` as engine byte; this field exists for
    # the model to see continuous musical amplitude.
    depth_semitones: float = 0.0
    # FC v1 — fx1 byte decomposition. amplitude=0 means vibrato is
    # disabled (the engine short-circuits on fx1==0).
    amplitude: int = 0           # 0-15 (low nibble of fx1)
    speed: int = 0               # 0-7 (bits 4-6 of fx1, >> 4)
    direction: str = 'up'        # 'up' (bit 7 clear) | 'down' (set)


@dataclass
class PulseProgConfig:
    """FC v1 — pulse-program per-instrument config (replaces opaque
    fc_fx2 byte).

    `program` (1-7; 0 = disabled) selects the engine's pulsetabel
    entry — an 8-byte program describing how pulse-width sweeps over
    time. The pulsetabel is engine-shared (not yet inlined per-inst).
    v2 deferral: inline the 8 bytes here as named per-segment fields.

    `increment` (0-15) is the default per-frame pulse-width step,
    scaled to fx2's high nibble (0-$F0 in 16-step increments).
    """
    program: int = 0
    increment: int = 0


@dataclass
class FilterProgConfig:
    """FC v1 — filter-program per-instrument config (replaces opaque
    fc_fil_count byte + fx2 bit 3 + fx3 bit 0).

    `program` (1-15; 0 = disabled) selects the filter program; the
    engine indexes filterbytes by program * 4.

    `strange` enables the bidirectional cutoff sweep on $D416 (fx2.3).
    `double_voice` is the lo-freq detune trick (filcount bit 3 = $08).
    `aux_bits` carries fil_count's high-nibble bits whose musical
    meaning isn't fully RE'd yet (v2 deferral).
    """
    program: int = 0
    strange: bool = False
    double_voice: bool = False
    aux_bits: int = 0


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
    # When True, the ramp runs every frame instead of odd-frames-only
    # (was per-tune `params.incby2_every_frame`). Devils Galop + Thing
    # on a Spring use True.
    every_frame: bool = False


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
    # FC v1 — decomposed instrument effects (replaces v0's opaque
    # fc_fil_count/fc_fx1-3 bytes). See
    # pipelines/future_composer/docs/usf_schema_v1.md.
    # vibrato.amplitude/speed/direction carry the fx1 byte.
    pulse_prog: PulseProgConfig = field(default_factory=PulseProgConfig)
    filter_prog: FilterProgConfig = field(default_factory=FilterProgConfig)
    # Effect flags from fx3 bits — names match the engine routines
    # they enable (see usf_schema_v1.md bit table). Empty set = no
    # effects active.
    effects: frozenset = field(default_factory=frozenset)


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
class InitBehaviorConfig:
    """Engine's first-frame play behavior — replaces the two flat
    per-tune flags `first_frame_gate_off` and `suppress_first_notestart`.

    The model sees these as ONE block of related boot-time behavior
    instead of two scattered booleans named after Hubbard mechanism.

      `silence_all_voices_on_frame_0`: when True, the engine writes
        ctrl=$00 to all 3 voices on play frame 0. Result: voices
        start silent before any notes. Action Biker uses this.

      `no_first_attack_voice`: when non-zero, the engine suppresses
        that voice's first-frame note-start SID writes (no envelope
        attack on the very first note). The value is the voice id
        (1, 2, or 3). 0 = no suppression (default). Devils Galop
        suppresses voice 3 — the engine's drum-priority gate is the
        mechanism, but the musical effect is "voice N doesn't attack
        on its first frame."
    """
    silence_all_voices_on_frame_0: bool = False
    no_first_attack_voice: int = 0      # 0 = none; 1/2/3 = voice id


@dataclass
class SfxConfig:
    """SFX sub-engine bookkeeping — replaces 3 flat per-tune keys
    (`has_sfx`, `sfx_framectr_ofs`, `sfx_state_ofs`).

    Presence of the block itself signals the engine has a SFX
    sub-engine (the legacy `has_sfx=True`). Composer reads the
    addresses when emitting SFX support code.

      `framectr_ofs` — freq-table offset where the SFX-readable frame
        counter lives. Default 253 = Commando-family.
      `state_ofs` — freq-table offset of the SFX state block (sweep
        index, step counter, etc.). None = scattered Commando layout;
        non-None = packed layout (Monty $FB, One Man $FB).

    Engine-internal positional offsets, but per-tune-stable.
    Replaces 3 flat keys with one named block.
    """
    framectr_ofs: int = 253
    state_ofs: Optional[int] = None


@dataclass
class MasterVolConfig:
    """Master-volume modulation algorithm — replaces 5 flat per-tune
    keys (`master_vol_subtrahend_voice`, `_base`, `_trigger`,
    `_reset_on_loop`, `_underflow_clamp`). The five fields describe
    ONE musical concept (master-vol modulation driven by a voice's
    pattern-progress counter) and belong together.

    `subtrahend_voice` (0/1/2) — which voice's pattern-position
    advances drive the modulation. When None, no modulation is
    active and the block is omitted from USF entirely.

    `base` (default $A0) — starting master-vol byte. The modulation
    decrements from here.

    `trigger` ('inst_change' default | 'every_note') — when the
    modulation counter advances.

    `reset_on_loop` — when True, the master-vol counter resets to
    `base` whenever the orderlist loops.

    `underflow_clamp` — when True, the counter clamps to 0 on
    underflow (vs wrapping at $FF).
    """
    subtrahend_voice: int = 0          # 0/1/2 = voice id
    base: int = 0xA0
    trigger: str = 'inst_change'       # 'inst_change' | 'every_note'
    reset_on_loop: bool = False
    underflow_clamp: bool = False


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
    # Engine first-frame init behavior — replaces the flat per-tune
    # `first_frame_gate_off` and `suppress_first_notestart` flags.
    init_behavior: Optional[InitBehaviorConfig] = None
    # Master-volume modulation — replaces the 5 flat per-tune
    # `master_vol_*` keys. None when no modulation is active.
    master_vol: Optional[MasterVolConfig] = None
    # SFX sub-engine bookkeeping — replaces flat `has_sfx` +
    # `sfx_framectr_ofs` + `sfx_state_ofs`. None when the engine has
    # no SFX sub-engine.
    sfx: Optional[SfxConfig] = None
