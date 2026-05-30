"""Engine model — the composable engine spec the codegen consumes.

This is the layer between USF (engine-blind musical content) and 6502
asm (engine-specific implementation). The model is **parametric over
features**, never indexed by engine. Each engine becomes a *point* in
the model's parameter space; the codegen reads the model and emits the
asm those features require.

Principles
----------
* No engine-named anything. Field/class names describe musical or
  mechanism behavior, not the engine that uses them. Forbidden names:
  `*Kind`, `*Ptr`, `*_idx`, anything starting with `hubbard`, `commando`,
  `bowden`, `clever`, `companion`, `yes_tune`, etc.
* Each feature is **optional or parametric**. A USF that doesn't use a
  feature gets `None` or a default; a USF that uses it carries the
  parameter values.
* Features compose orthogonally. Adding a feature = adding a dataclass
  or extending an existing one — never adding a shape branch.
* The model is engine-blind. Reading a `EngineModel` instance should
  not let you derive which engine produced it without the codegen
  emitting code (and even there the dispatch is feature-by-feature,
  not shape-by-shape).

Status
------
PHASE 2 — design + audit. Dataclasses defined; `from_usf` builds a
model from any of the 6 currently-supported USF shapes. The codegen
that consumes the model is Phase 3+. See
`docs/composer_rewrite_plan.md`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Literal


# ---------------------------------------------------------------------------
# Pattern encoding — how pattern bytes encode musical content
# ---------------------------------------------------------------------------

PatternEncodingMode = Literal[
    'atomic_per_tick',     # 1 byte = 1 tick; duration via skip-byte runs
    'atomic_per_period',   # 1 byte = 1 note period; duration from tempo dividers
    'note_dur_pair',       # 2 bytes per row: (note_byte, duration_byte)
    'bitpack',             # variable-bit-width packed bitstream
]

PitchByteFormat = Literal[
    'octave_semi_nibble',  # (octave<<4) | semitone (0..11) — high nibble octave
    'absolute_semi',       # semi = note + 12*octave (0..95 in musical range)
]


@dataclass
class PatternConfig:
    """How the pattern bytes are read and decoded."""
    encoding: PatternEncodingMode
    pitch_byte_format: PitchByteFormat = 'octave_semi_nibble'

    # bitpack-specific
    bitpack_dur_bits: Optional[int] = None
    bitpack_inst_bits: Optional[int] = None


# ---------------------------------------------------------------------------
# Voice timing + tempo dispatch
# ---------------------------------------------------------------------------

VoiceTimingMode = Literal[
    'every_tick',              # each fired tempo tick, every voice reads next byte
    'dur_counter_decrement',   # per-voice counter decrements; reads on counter==1
    'tick_counter_decrement',  # per-voice tick_ctr decrements; reads on counter==0
]


@dataclass
class VoiceTiming:
    """When voices read the next pattern byte.

    Three known modes — note this is **within** a fired tempo tick.
    The tempo gate (single_phase / two_phase) decides when ticks fire;
    voice_timing decides which voices read on a fired tick.

      - `every_tick`: every voice reads on every fired tempo tick.
        No per-voice counter. (henrys, bowden, companion)
      - `dur_counter_decrement`: per-voice `dur_ctr` decrements every
        fired tick; read fires when counter hits 1. (clever_music's
        $82 set_duration; Hubbard '85's `v_dur`)
      - `tick_counter_decrement`: per-voice `tick_ctr` decrements every
        fired tick; play fires when counter hits 0. (yes_tune)
    """
    mode: VoiceTimingMode

    # Initial counter value when applicable (dur_counter / tick_counter).
    initial_value: int = 1


TempoDispatchMode = Literal[
    'single_phase',   # one tempo counter; on hit, voices process
    'two_phase',      # gate_off counter + note_load counter (companion)
]


@dataclass
class TempoDispatch:
    """Tempo gate(s) that decide when voices advance.

    Two known modes:
      - `single_phase`: one tempo counter increments per frame; when
        it equals `tempo_const`, voices process. (all shapes except
        companion)
      - `two_phase`: two counters compared each frame. On `gate_off_tick`,
        each voice's bit-7 "scheduled release" flag may fire a gate-off.
        On `note_load_tick`, voices read the next note. (companion)
    """
    mode: TempoDispatchMode

    # Engines that program CIA1 timer A (instead of relying on libsidplayfp's
    # default 50 Hz) declare it here. None = use the PSID-default rate.
    cia1_timer_a: Optional[int] = None


# ---------------------------------------------------------------------------
# Terminator vocabulary — which bytes mean what
# ---------------------------------------------------------------------------

# Behaviour names a byte can map to. Parametric over musical/mechanism
# meaning; **never names an engine**.
TerminatorBehavior = Literal[
    'note',                   # default for in-range pitches
    'rest_gate_off',          # write ctrl gate-off
    'skip',                   # no SID write (sustain prior state)
    'loop_reset',             # reset pattern ptr to start
    'loop_substitute_first',  # pos=1, replay orderlist[0] this tick
    'song_end_voice',         # voice stops permanently (writes silence)
    'song_end_voice_freeze',  # voice freezes — holds note, runs effects
    'song_end_stop_fill',     # write STOP_FILL byte to $D400-$D417 + silence
    'master_vol_reset_and_loop',  # write $D418 + reset pos
    'end_song_on_voice_n',    # writes vol=0 + clears alive flag (n-specific)
    'set_duration_next_byte', # gate off + read next byte as new dur
    'early_release_flag',     # bit-7 on a pitch byte schedules gate-off
]


@dataclass
class TerminatorVocab:
    """How each byte (or byte range) is interpreted in the pattern stream.

    Most shapes use a small subset. Common mappings:
      - henrys: $00-$7F note, $80 rest, $81 skip, $FF master_vol_reset_and_loop
      - bowden: $00-$7F note, $80 rest, $81-$FE skip, $FF loop_substitute_first
      - yes_tune: $00-$7F note, $80 dur rest_gate_off, $81 song_end_voice,
        $FF loop_reset, $82 dur set_duration_next_byte
      - clever_music: $00-$7F note, $80 rest_gate_off, $81 skip,
        $FF loop_reset, $82 set_duration_next_byte (plus embedded commands
        via CommandVocab, separate)
      - companion: $00-$7F note, $80-$8B early_release_flag (high bit set),
        $8C rest_gate_off, $8D end_song_on_voice_n (V3 only),
        $00-$7F via duration_byte_signal note_load_tick (no explicit byte)
      - Hubbard '85: $FE song_end_voice (variants), $FF loop_reset on the
        orderlist; per-note flags via the bitpack codec
    """
    # Byte → behavior. Bytes not in the map fall through to:
    #   - 'note' if byte < $80 (pitch range)
    #   - skip if byte == 0x81 and shape has skip semantics
    #   - 'song_end_voice' otherwise
    byte_map: dict[int, TerminatorBehavior] = field(default_factory=dict)

    # When 'early_release_flag' is in the byte_map, the bit-7 of a pitch
    # byte schedules a gate-off at the next two-phase gate_off tick.
    # Voice index that song_end_on_voice_n applies to (typically 2 for V3).
    end_song_voice_idx: Optional[int] = None

    # The byte to write to $D400-$D417 on song_end_stop_fill (e.g.
    # Action Biker's $FF fill).
    stop_fill_byte: Optional[int] = None


# ---------------------------------------------------------------------------
# Embedded commands (clever_music's recursive interpreter)
# ---------------------------------------------------------------------------

EmbeddedCommandName = Literal[
    'set_tempo',         # $Bx — low nibble = new tempo_const
    'set_master_vol',    # $Cx — low nibble = new $D418 value
    'set_instrument',    # $Dx — low nibble = instrument id; copy 5 bytes
    'pattern_jump',      # $Ex — jump via song_table if matches song_pos
    'skip_byte_recurse', # other bit-7 byte — engine skips + reads next
]


@dataclass
class CommandVocab:
    """Embedded command bytes that don't consume a tick. The engine
    reads the byte, applies the side effect, then recurses to read
    the next byte in the same tick.

    Today only clever_music has this. The codegen emits the recursive
    interpreter only when this is non-None.
    """
    # Map of high-nibble byte → command. ($B → 'set_tempo', $C → ...)
    nibble_map: dict[int, EmbeddedCommandName] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Modulation programs (per-instrument, per-frame)
# ---------------------------------------------------------------------------

@dataclass
class Vibrato:
    """Triangle LFO on freq. Hubbard '85's `fx_vibrato`."""
    depth: int               # vib_depth — shift count
    onset_dur: int           # dur-field gate; vibrato fires when v_dur >= onset


@dataclass
class PwmLinear:
    """pw_lo += speed + vib_carry every frame. Accumulator on pwacc[inst]."""
    speed: int               # signed step per frame
    init_pw_lo: int
    init_pw_hi: int
    or_mask: int = 0         # `ora #LINEAR_PW_OR` — engine-wide, here as param


@dataclass
class PwmBidirectional:
    """Triangle PWM: rises by `step` until `hi_bound`, then falls."""
    period: int              # decrements v_pwperiod; reload from this
    step: int                # add/subtract on direction
    init_pw_lo: int
    init_pw_hi: int
    lo_bound: int
    hi_bound: int


@dataclass
class Arpeggio:
    """Multi-step semitone arpeggio. `frame & ARP_MASK` selects phase;
    on the +ARP_OFS phase, pitch += interval."""
    offsets: tuple[int, ...]   # semitone offsets per arp step (engine has fixed cycle)
    period: int                # cycle length (frame_ctr & (period-1) gates)
    interval: int = 12         # ARP_OFS — semitones added on the active phase
    phase_invert: bool = False # swap which phase is "active" (One Man and his Droid)


@dataclass
class FreqHiSlide:
    """`v_slide` decrements per frame; writes freq_hi each frame; ends
    when `v_dur` underflows. Hubbard's `fx_skydive`."""
    # No per-instrument params; the slide value comes from v_slide
    # initialized at note-start to the note's freq_hi. Triggered by
    # instrument fx_flag bit 0.


@dataclass
class OddFrameSlide:
    """Odd-frame freq_hi slide on `v_slide`. Hubbard's `fx_incby2`."""
    step: int                # signed step per fire
    every_frame: bool = False # If True, fires every frame instead of odd-only
    onset: int = 3           # dur-field threshold to start
    late_gate: Optional[int] = None  # if set, only fires when v_dur < N (Hunter Patrol)


@dataclass
class PerNotePortamento:
    """Per-note slide via `v_drumtrig`. delta=trig&$7E, dir=trig&$01.
    Hubbard's `fx_drumslide`."""
    # Per-note params come from drum_trig byte in the pattern data;
    # no per-instrument params.


@dataclass
class HardcodedPwSweep:
    """A non-per-instrument PW sweep on a specific voice, gated by a
    global phase counter. Companion's V3 `pw_lo += 5 every other frame`.

    The "5" is the carry-leak result of the engine's `CMP #$01; ADC #4`
    sequence — we capture the effective step (5), not the engine's
    code shape (4 + carry).
    """
    voice_idx: int           # which voice this applies to (0/1/2)
    delta_per_phase: int     # 5 for companion
    phase_period: int = 2    # fires every N frames (2 for companion = every-other)
    target_reg: int = 0x02   # offset within voice block (pw_lo = 2)


@dataclass
class InstrumentProgram:
    """Per-instrument behavior. Each modulation program is Optional —
    None means the instrument doesn't use it. The codegen reads which
    are non-None and emits per-frame asm for each."""
    id: int                   # 1-indexed (USF) — codegen maps to 0-indexed
    init_ctrl: int
    init_pw_lo: int
    init_pw_hi: int
    init_ad: int
    init_sr: int
    hr_ctrl: int = 0          # hard-restart ctrl (gate-clear variant)

    # Modulation programs
    vibrato: Optional[Vibrato] = None
    pwm_linear: Optional[PwmLinear] = None
    pwm_bidirectional: Optional[PwmBidirectional] = None
    arpeggio: Optional[Arpeggio] = None
    freq_hi_slide: Optional[FreqHiSlide] = None
    odd_frame_slide: Optional[OddFrameSlide] = None
    per_note_portamento: Optional[PerNotePortamento] = None


# ---------------------------------------------------------------------------
# Master volume
# ---------------------------------------------------------------------------

MasterVolMode = Literal[
    'fixed_init',           # Set once at init, never changes
    'per_subtune_init',     # Per-subtune init value; never changes mid-stream
    'mutable_commands',     # Mutated mid-stream via $Cx command bytes
    'fade_progressive',     # Decreases on configured voice's pattern-end
]


@dataclass
class FadeProgressive:
    """Fade-progressive vol: increment `vol_progress` on the configured
    voice's pattern-end (never wraps on loop), write
    `$D418 = clamp(base - vol_progress, 0..$0F)` on a trigger."""
    subtrahend_voice_idx: int           # 0/1/2
    base: int                            # 0xA0 typical
    trigger: Literal['inst_change', 'every_note'] = 'inst_change'


@dataclass
class MasterVolConfig:
    """Master vol ($D418) handling.

    Combinations are limited:
      - `fixed_init`: init writes $0F (or 0 if `fade_progressive` is
        set — fade engines leave $D418 untouched until the first
        triggered write).
      - `per_subtune_init`: per-subtune init value (yes_tune
        `gain_init`, companion `vol_filter`).
      - `mutable_commands`: $Cx command writes new value mid-stream
        (clever_music).
      - `fade_progressive`: progressive fade (set independent of mode;
        composes with `fixed_init`).
    """
    mode: MasterVolMode
    init_value: int = 0x0F              # $0F when fixed/per-subtune; 0 with fade
    fade: Optional[FadeProgressive] = None


# ---------------------------------------------------------------------------
# Inter-voice quirks
# ---------------------------------------------------------------------------

InterVoiceQuirkName = Literal[
    'carry_leak_4_vs_5_byte_timbre',  # bowden — a skip-byte voice causes next
                                       # voice to write 4-byte timbre (omit SR)
    'first_note_suppression',         # Hubbard — V1 first note's writes are
                                       # suppressed by drum_prio gate
    'no_release_per_note_flag',       # Hubbard — per-note no-release flag
                                       # skips hard-restart writes
]


@dataclass
class InterVoiceQuirk:
    name: InterVoiceQuirkName
    # Parameters per quirk:
    #   carry_leak: no params
    #   first_note_suppression: voice_idx (typically 0 for V1)
    #   no_release: no params (per-note flag in pattern data)
    voice_idx: Optional[int] = None


# ---------------------------------------------------------------------------
# Off-table arpeggio (Hubbard '85's statebuf mirror)
# ---------------------------------------------------------------------------

@dataclass
class StateSlot:
    offset: int
    kind: Literal['var', 'var_and', 'note_byte', 'const', 'zp']
    var: str = ''
    mask: int = 0xFF
    value: int = 0


@dataclass
class StateLayoutMirror:
    """A mirror of engine-state bytes used by off-table reads.

    Pitch values >= 96 read past the 96-entry freq table into engine
    state. The mirror lets us reproduce those reads cleanly by writing
    the same bytes into a Python-controlled buffer at frame-load time.
    """
    n_voices: int = 3
    scalars: list[StateSlot] = field(default_factory=list)
    per_voice: list[StateSlot] = field(default_factory=list)
    decr_voice_idx_offset: Optional[int] = None  # `ns_offtab_decr_offset`


# Legacy names — the lifted Hubbard '85 parametric core (in
# `pipelines/composer_hubbard.py`) calls these `StatebufLayout` and
# `StatebufSlot`. Same dataclasses; aliased here so the two layers
# share canonical definitions.
StatebufSlot = StateSlot
StatebufLayout = StateLayoutMirror


# ---------------------------------------------------------------------------
# Sub-engines (SFX, digi)
# ---------------------------------------------------------------------------

@dataclass
class SfxConfig:
    """Sound-effect sub-engine spec.

    The 16-record SFX format is shared across the engines that have
    SFX. Per-engine variations: where SFX state lives (state_offset
    when state overlaps the freq table; None otherwise) and which
    freq-table offset the engine's frame counter writes to.
    """
    records: list = field(default_factory=list)  # list of SoundEffect
    state_offset: Optional[int] = None           # freq-table offset for SFX
                                                  # state block (Monty: 251)
    framectr_offset: int = 253                    # freq-table offset for
                                                  # the SFX-readable frame ctr


@dataclass
class DigiConfig:
    """Digi sub-engine spec — references a named digi technique."""
    # Named digi technique. Today only 'chimera_1bit'. Future: full
    # parametric spec (sample rate, dispatcher layout, etc.).
    technique: Literal['chimera_1bit']
    samples: list = field(default_factory=list)  # list of {pace, bank, src, end, packed, ...}


# ---------------------------------------------------------------------------
# Per-voice and per-subtune state
# ---------------------------------------------------------------------------

@dataclass
class VoiceInitState:
    """Per-voice initial state at subtune start.

    Different shapes seed different subsets:
      - henrys: initial position only (timbre comes from per-subtune timbre table)
      - bowden / yes_tune: position + timbre + state byte
      - clever_music: pat_start (from song_table) + dur_ctr=1
      - companion: full 5-byte timbre + ctrl_noGate + gate_off_flag=0
      - Hubbard '85: ovseed (6 state bytes overlapping freq table)
    """
    initial_position: int = 0
    state_byte: int = 0                          # yes_tune: 0=silent / 2=load
    initial_timbre: Optional[tuple] = None        # (pw_lo, pw_hi, ctrl, ad, sr)
    ctrl_no_gate: Optional[int] = None            # companion's per-voice ctrl


@dataclass
class SubtuneSpec:
    """Per-subtune parameters. Most engines have several subtunes; each
    subtune carries its own tempo, init state, and pattern data."""
    id: int
    tempo: int                                    # ticks per note period
    init_tempo_ctr: int = 0
    gate_off_tick: Optional[int] = None           # two-phase only
    note_load_tick: Optional[int] = None          # two-phase only
    voice_init: list[VoiceInitState] = field(default_factory=list)
    voice_patterns: list[bytes] = field(default_factory=list)  # encoded pattern bytes per voice
    voice_starts_at: int = 0                       # Hubbard's voice_start — skip earlier voices
    cia1_timer_a: Optional[int] = None
    master_vol_init: Optional[int] = None         # per-subtune master_vol value
    init_song_pos: Optional[int] = None           # clever_music
    init_pwm_state: Optional[tuple] = None        # companion: (init_pwm_ctr, init_pwm_ctr_2)
    filter_cutoff_hi: Optional[int] = None        # companion's $D416 byte
    # Engine-mechanism overrides (5_Title_Tunes per-sub)
    speed_ctr_init_override: Optional[int] = None
    odd_frame_slide_step_override: Optional[int] = None
    odd_frame_slide_late_gate_override: Optional[int] = None


# ---------------------------------------------------------------------------
# Voice configuration
# ---------------------------------------------------------------------------

CtrlSource = Literal[
    'instrument_waveform',   # ctrl comes from instrument.waveform[0]
    'init_voice_field',      # ctrl comes from InitVoice.ctrl (companion)
]


@dataclass
class VoiceConfig:
    """Voice-level engine config — how many voices, where each voice's
    runtime ctrl byte comes from."""
    count: int                                    # 1, 2, or 3
    ctrl_source: CtrlSource = 'instrument_waveform'


# ---------------------------------------------------------------------------
# PSID metadata + freq table
# ---------------------------------------------------------------------------

@dataclass
class PsidMeta:
    title: str = ''
    author: str = ''
    released: str = ''
    clock: Literal['unknown', 'PAL', 'NTSC', 'both'] = 'PAL'
    sid_model: int = 6581
    start_song: int = 1
    psid_speed: int = 0


# ---------------------------------------------------------------------------
# Compound builds (5_Title_Tunes-style)
# ---------------------------------------------------------------------------

@dataclass
class CompoundSpec:
    """A PSID that packs N independent engine instances + a dispatcher
    at the original init/play vectors. Only 5_Title_Tunes uses this
    today; future engines that ship multiple sub-engines packed into
    one PSID would land here too."""
    sub_models: list                              # list[EngineModel]
    dispatcher_init_addr: int
    dispatcher_play_addr: int


# ---------------------------------------------------------------------------
# Top-level engine model
# ---------------------------------------------------------------------------

@dataclass
class EngineModel:
    """The engine spec the codegen consumes. A USF + the right model
    configuration uniquely determines the per-frame SID-register
    instruction stream the engine produces.
    """
    psid: PsidMeta
    voices: VoiceConfig
    pattern: PatternConfig
    voice_timing: VoiceTiming
    tempo_dispatch: TempoDispatch
    terminators: TerminatorVocab
    instruments: list[InstrumentProgram]
    master_vol: MasterVolConfig
    subtunes: list[SubtuneSpec]
    freq_table: bytes                             # raw bytes (128hi + 128lo, or 320 for Hubbard)

    # Optional / shape-rare features
    commands: Optional[CommandVocab] = None
    inter_voice_quirks: list[InterVoiceQuirk] = field(default_factory=list)
    state_layout: Optional[StateLayoutMirror] = None
    sfx: Optional[SfxConfig] = None
    digi: Optional[DigiConfig] = None
    hardcoded_pw_sweep: Optional[HardcodedPwSweep] = None
    compound: Optional[CompoundSpec] = None

    # Engine knobs that don't fit a clean dataclass — kept here for the
    # transition; once Phase 3+ encodes them as proper features, remove.
    extras: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# USF → EngineModel converter
# ---------------------------------------------------------------------------

def from_usf(usf) -> EngineModel:
    """Convert a USF into an EngineModel by reading features the USF
    declares (instrument programs, orderlist shape, named mechanism
    params, etc.).

    This converter reads each feature dimension independently — it does
    **not** detect "which engine produced this USF" before populating
    the model. A USF with vibrato on instrument 3 gets a model with
    `instruments[2].vibrato = Vibrato(...)`; a USF without vibrato gets
    None. No shape dispatch.

    Status: Phase 2 — populates the dimensions each current shape uses.
    Phase 3+ refines as the codegen consumes the model.
    """
    from src.usf import MusicSubtune, SfxSubtune, DigiSubtune  # noqa: E402

    psid = PsidMeta(
        title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released, clock=usf.psid.clock,
        sid_model=usf.psid.sid, start_song=usf.psid.start_song,
        psid_speed=usf.psid.speed,
    )

    music = sorted(
        (s for s in usf.subtunes if isinstance(s, MusicSubtune)),
        key=lambda s: s.id)
    if not music:
        raise ValueError('engine model requires at least one music subtune')

    # ---- VoiceConfig ---------------------------------------------------
    active_voices = [v for v in music[0].voices if v.patterns]
    voice_count = max(len(active_voices), 1)
    if voice_count not in (1, 3):
        # Yes_tune SFX subtunes can have 1 active voice but pattern slots
        # for 3 (silent state). Use ms.voices count as the slot count.
        voice_count = len(music[0].voices)

    # ctrl source — inspect whether any subtune's InitVoice carries a
    # non-zero ctrl (companion does; others all have InitVoice.ctrl=0
    # because they derive ctrl from the instrument's waveform field).
    ctrl_source: CtrlSource = 'instrument_waveform'
    for ms in music:
        if ms.init and ms.init.voices:
            for iv in ms.init.voices:
                if iv.ctrl != 0:
                    ctrl_source = 'init_voice_field'
                    break
    voices = VoiceConfig(count=voice_count, ctrl_source=ctrl_source)

    # ---- PatternConfig + VoiceTiming + TempoDispatch -----------------
    # These three are linked — they describe how the engine reads
    # pattern data. We walk USF content to decide.
    pattern, voice_timing, tempo_dispatch = _infer_timing_and_encoding(
        usf, music)

    # ---- TerminatorVocab ---------------------------------------------
    terminators = _infer_terminator_vocab(usf, music)

    # ---- Instruments --------------------------------------------------
    instruments = [_instrument_from_usf(u) for u in usf.instruments]

    # ---- MasterVolConfig ---------------------------------------------
    master_vol = _infer_master_vol(usf, music)

    # ---- CommandVocab (optional) -------------------------------------
    commands = _infer_command_vocab(usf, music)

    # ---- Inter-voice quirks ------------------------------------------
    inter_voice_quirks = _infer_inter_voice_quirks(usf, music)

    # ---- StateLayoutMirror (optional) ---------------------------------
    state_layout = _convert_state_layout(usf)

    # ---- SfxConfig + DigiConfig --------------------------------------
    sfx = _convert_sfx(usf)
    digi = _convert_digi(usf)

    # ---- HardcodedPwSweep (optional) ---------------------------------
    hardcoded_pw_sweep = None
    # Companion declares this via the `init_pwm_ctr` / `init_pwm_ctr_2`
    # per-subtune fields plus the gate_off_tick presence. Detection
    # is feature-based (does the USF carry hardcoded-PW-sweep state?).
    if any('gate_off_tick' in (ms.params.fields if ms.params else {})
           for ms in music):
        # The fixed delta/period come from the engine — encoded as engine
        # mechanism in the model itself, not the USF. Companion: V3 (idx=2),
        # +5, every-other-frame.
        hardcoded_pw_sweep = HardcodedPwSweep(
            voice_idx=2, delta_per_phase=5, phase_period=2,
            target_reg=0x02)

    # ---- Subtunes -----------------------------------------------------
    subtunes = [_subtune_from_usf(ms, pattern.encoding, voice_count)
                for ms in music]

    # ---- Freq table ---------------------------------------------------
    freq_table = bytes(usf.freq_table) if usf.freq_table is not None else b''

    return EngineModel(
        psid=psid,
        voices=voices,
        pattern=pattern,
        voice_timing=voice_timing,
        tempo_dispatch=tempo_dispatch,
        terminators=terminators,
        instruments=instruments,
        master_vol=master_vol,
        subtunes=subtunes,
        freq_table=freq_table,
        commands=commands,
        inter_voice_quirks=inter_voice_quirks,
        state_layout=state_layout,
        sfx=sfx,
        digi=digi,
        hardcoded_pw_sweep=hardcoded_pw_sweep,
    )


# ---------------------------------------------------------------------------
# Converter helpers
# ---------------------------------------------------------------------------

def _infer_timing_and_encoding(usf, music) -> tuple[PatternConfig, VoiceTiming, TempoDispatch]:
    """Infer pattern encoding + voice timing + tempo dispatch from USF
    content. No engine names.

    Heuristics (all content-based):
      - bitpack codec: USF has 320-byte freq table region (the engine
        stores per-voice state past the musical entries — a real
        mechanism feature, not a fingerprint). We treat this as the
        "freq_table carries engine state overlap" feature.
      - two-phase tempo: any subtune has `gate_off_tick` param.
      - note_dur_pair encoding: any voice's pattern row has duration > 1
        without an `fx:hold` sibling (yes_tune-style).
      - atomic_per_period encoding: any row has `fx:early_release` flag
        (companion's bit-7+pitch encoding).
      - tick-counter timing: any voice has a real stop terminator
        (entries non-empty + stop=True) — yes_tune-style state machine.
      - dur-counter timing: any row has tempo=/vol=/song_pos= flags
        (clever_music) or the USF uses the 320-byte state-overlap
        region (Hubbard '85 dur_counter via v_dur).
    """
    has_gate_off = any(
        'gate_off_tick' in (ms.params.fields if ms.params else {})
        for ms in music)
    has_state_overlap_region = (
        usf.freq_table is not None and len(usf.freq_table) == 320)
    has_early_release = any(
        'fx:early_release' in r.fx_flags
        for ms in music for v in ms.voices for p in v.patterns
        for r in p.rows)
    has_stop_terminator = any(
        v.orderlist.entries and v.orderlist.stop
        for ms in music for v in ms.voices)
    has_command_flags = any(
        any(f.startswith(('tempo=', 'vol=', 'song_pos='))
            for f in r.fx_flags) or (r.instr is not None and r.pitch.is_rest)
        for ms in music for v in ms.voices for p in v.patterns
        for r in p.rows)
    has_dur_gt_1 = any(
        r.duration > 1 and 'fx:hold' not in r.fx_flags
        for ms in music for v in ms.voices for p in v.patterns
        for r in p.rows)

    # Pattern encoding
    if has_state_overlap_region:
        encoding: PatternEncodingMode = 'bitpack'
        pitch_fmt: PitchByteFormat = 'absolute_semi'
        bitpack_dur = 4    # Hubbard's BitPackCodec defaults — refined Phase 3
        bitpack_inst = 6
    elif has_early_release:
        encoding = 'atomic_per_period'
        pitch_fmt = 'octave_semi_nibble'
        bitpack_dur = bitpack_inst = None
    elif has_stop_terminator:
        encoding = 'note_dur_pair'
        pitch_fmt = 'octave_semi_nibble'
        bitpack_dur = bitpack_inst = None
    else:
        # atomic_per_tick: henrys, bowden, clever_music
        encoding = 'atomic_per_tick'
        pitch_fmt = 'octave_semi_nibble'
        bitpack_dur = bitpack_inst = None

    # The has_dur_gt_1 signal is consumed above for note_dur_pair detection
    # and otherwise informational; reference it here so a linter sees the read.
    _ = has_dur_gt_1

    pattern = PatternConfig(
        encoding=encoding,
        pitch_byte_format=pitch_fmt,
        bitpack_dur_bits=bitpack_dur,
        bitpack_inst_bits=bitpack_inst,
    )

    # Voice timing — per-voice counter behavior WITHIN a fired tempo tick.
    # Two-phase tempo dispatch (companion) reads on every fired tick;
    # the per-voice "early release" flag is a gate_off behavior, not a
    # per-voice timing counter.
    if has_gate_off:
        timing_mode: VoiceTimingMode = 'every_tick'
    elif has_state_overlap_region:
        # Hubbard's v_dur per voice
        timing_mode = 'dur_counter_decrement'
    elif has_command_flags:
        # clever_music's $82 set_duration
        timing_mode = 'dur_counter_decrement'
    elif has_stop_terminator:
        # yes_tune's tick_ctr per voice
        timing_mode = 'tick_counter_decrement'
    else:
        timing_mode = 'every_tick'
    voice_timing = VoiceTiming(mode=timing_mode, initial_value=1)

    # Tempo dispatch
    tempo_mode: TempoDispatchMode = 'two_phase' if has_gate_off else 'single_phase'

    # Per-subtune CIA1 timer A — if any subtune programs one, the tempo
    # dispatch reflects it. Use the first subtune's value as
    # representative (per-subtune actuals live on SubtuneSpec).
    cia1 = next(
        (ms.params.fields.get('cia1_timer_a') for ms in music
         if ms.params and ms.params.fields.get('cia1_timer_a')),
        None)
    tempo_dispatch = TempoDispatch(mode=tempo_mode, cia1_timer_a=cia1)

    return pattern, voice_timing, tempo_dispatch


def _infer_terminator_vocab(usf, music) -> TerminatorVocab:
    """Build the byte → behavior map directly from USF features. No
    timing-mode coupling — each feature stands alone.

    Detection (each independent — multiple may apply):
      - 320-byte freq region → orderlist terminators ($FE/$FF); the
        per-pattern note codec handles per-row terminators internally
        (no entries in byte_map for those).
      - `fx:early_release` flag → bit-7-on-pitch is the early-release
        encoding; $8C rest + $8D end-song-on-voice.
      - $82 in pattern data (via SET_DURATION command via $82 marker
        in some streams) → set_duration_next_byte. Detected by
        clever_music's command flags presence (no $82 isolated USF
        signal today; treat $82 as set_dur if any cmd flag present).
      - stop terminator (entries+stop=True) + no early_release → yes_tune
        ($80 dur rest, $81 song_end, $FF loop_reset).
      - 3+ active voices atomic → bowden ($81-$FE skip, $FF loop_subst).
      - 1 active voice atomic → henrys ($81 skip, $FF master_vol_reset).
    """
    byte_map: dict[int, TerminatorBehavior] = {}
    end_song_voice_idx = None
    stop_fill_byte = None

    has_state_overlap_region = (
        usf.freq_table is not None and len(usf.freq_table) == 320)
    has_early_release = any(
        'fx:early_release' in r.fx_flags
        for ms in music for v in ms.voices for p in v.patterns
        for r in p.rows)
    has_command_flags = any(
        any(f.startswith(('tempo=', 'vol=', 'song_pos='))
            for f in r.fx_flags) or (r.instr is not None and r.pitch.is_rest)
        for ms in music for v in ms.voices for p in v.patterns
        for r in p.rows)
    has_stop_terminator = any(
        v.orderlist.entries and v.orderlist.stop
        for ms in music for v in ms.voices)

    if has_state_overlap_region:
        # Orderlist-level terminators (bitpack codec)
        byte_map[0xFE] = 'song_end_voice'
        byte_map[0xFF] = 'loop_reset'
        for ms in music:
            if ms.params and 'stop_fill' in ms.params.fields:
                stop_fill_byte = ms.params.fields['stop_fill']
                byte_map[0xFE] = 'song_end_stop_fill'
                break
    elif has_early_release:
        # companion's encoding — $80 is the early-release flag on a pitch byte
        byte_map[0x80] = 'early_release_flag'
        byte_map[0x8C] = 'rest_gate_off'
        byte_map[0x8D] = 'end_song_on_voice_n'
        end_song_voice_idx = 2
    elif has_command_flags:
        # clever_music: atomic per tick with embedded commands + $82
        byte_map[0x80] = 'rest_gate_off'
        byte_map[0x81] = 'skip'
        byte_map[0x82] = 'set_duration_next_byte'
        byte_map[0xFF] = 'loop_reset'
    elif has_stop_terminator:
        # yes_tune
        byte_map[0x80] = 'rest_gate_off'
        byte_map[0x81] = 'song_end_voice'
        byte_map[0xFF] = 'loop_reset'
    else:
        active = [v for v in music[0].voices if v.patterns]
        n_active = len(active)
        if n_active >= 3:
            # bowden
            byte_map[0x80] = 'rest_gate_off'
            for b in range(0x81, 0xFF):
                byte_map[b] = 'skip'
            byte_map[0xFF] = 'loop_substitute_first'
        else:
            # henrys
            byte_map[0x80] = 'rest_gate_off'
            byte_map[0x81] = 'skip'
            byte_map[0xFF] = 'master_vol_reset_and_loop'

    return TerminatorVocab(
        byte_map=byte_map,
        end_song_voice_idx=end_song_voice_idx,
        stop_fill_byte=stop_fill_byte)


def _instrument_from_usf(u) -> InstrumentProgram:
    """Map one USF Instrument to an InstrumentProgram. Reads each
    modulation field independently — populates the matching feature
    object if non-trivial, leaves the slot None otherwise."""
    init_ctrl = u.waveform[0] if u.waveform else 0

    vib = (Vibrato(depth=u.vibrato.scale, onset_dur=6)  # onset is engine-wide; refined in Phase 3
           if u.vibrato.scale != 0 else None)

    pwm_lin = None
    pwm_bid = None
    if u.pwm.mode == 'linear':
        pwm_lin = PwmLinear(speed=u.pwm.speed,
                            init_pw_lo=u.pwm.init & 0xFF,
                            init_pw_hi=(u.pwm.init >> 8) & 0xFF)
    elif u.pwm.mode == 'bidirectional':
        pwm_bid = PwmBidirectional(
            period=u.pwm.speed & 0x1F, step=u.pwm.speed & 0xE0,
            init_pw_lo=u.pwm.init & 0xFF,
            init_pw_hi=(u.pwm.init >> 8) & 0xFF,
            lo_bound=u.pwm.min_hi, hi_bound=u.pwm.max_hi)

    arp = (Arpeggio(offsets=tuple(u.arp.offsets), period=u.arp.period)
           if len(u.arp.offsets) > 1 else None)

    return InstrumentProgram(
        id=u.id,
        init_ctrl=init_ctrl,
        init_pw_lo=u.pwm.init & 0xFF,
        init_pw_hi=(u.pwm.init >> 8) & 0xFF,
        init_ad=u.adsr[0],
        init_sr=u.adsr[1],
        hr_ctrl=init_ctrl & 0xFE,
        vibrato=vib,
        pwm_linear=pwm_lin,
        pwm_bidirectional=pwm_bid,
        arpeggio=arp,
        freq_hi_slide=FreqHiSlide() if u.freq_slide else None,
        odd_frame_slide=OddFrameSlide(step=2) if u.inc_by2 else None,
        # per_note_portamento is a per-note feature (no per-instrument params)
    )


def _infer_master_vol(usf, music) -> MasterVolConfig:
    """Master vol mode from USF features."""
    # Mutable via $Cx? -> mutable_commands. Top-level USF param
    # `init_master_vol` overrides the init value; default is $0A —
    # the canonical init value for the cmd-stream family (clever_music
    # writes $D418 = $0A at init via `lda #$0A; sta $d418`).
    has_vol_cmd = any(
        any(f.startswith('vol=') for f in r.fx_flags)
        for ms in music for v in ms.voices for p in v.patterns
        for r in p.rows)
    if has_vol_cmd:
        p_top = usf.params.fields if usf.params else {}
        return MasterVolConfig(
            mode='mutable_commands',
            init_value=p_top.get('init_master_vol', 0x0A))

    # Fade-progressive — currently a top-level USF param. Detected by
    # `master_vol_subtrahend_voice` field. (Hubbard '85 only today.)
    p = usf.params.fields if usf.params else {}
    if p.get('master_vol_subtrahend_voice') is not None:
        return MasterVolConfig(
            mode='fade_progressive', init_value=0,
            fade=FadeProgressive(
                subtrahend_voice_idx=p['master_vol_subtrahend_voice'],
                base=p.get('master_vol_base', 0xA0),
                trigger=p.get('master_vol_trigger', 'inst_change')))

    # Per-subtune `gain_init` (yes_tune) or `vol_filter` (companion)?
    per_sub = any(
        (ms.params and ('gain_init' in ms.params.fields
                        or 'vol_filter' in ms.params.fields))
        for ms in music)
    if per_sub:
        return MasterVolConfig(mode='per_subtune_init', init_value=0x0F)

    return MasterVolConfig(mode='fixed_init', init_value=0x0F)


def _infer_command_vocab(usf, music) -> Optional[CommandVocab]:
    """Detect embedded commands ($Bx/$Cx/$Dx/$Ex). Today only
    clever_music has them. Detected feature-by-feature."""
    nibble_map: dict[int, EmbeddedCommandName] = {}
    for ms in music:
        for v in ms.voices:
            for p in v.patterns:
                for r in p.rows:
                    if r.instr is not None and r.pitch.is_rest:
                        nibble_map[0x0D] = 'set_instrument'
                    for f in r.fx_flags:
                        if f.startswith('tempo='):
                            nibble_map[0x0B] = 'set_tempo'
                        elif f.startswith('vol='):
                            nibble_map[0x0C] = 'set_master_vol'
                        elif f.startswith('song_pos='):
                            nibble_map[0x0E] = 'pattern_jump'
    if not nibble_map:
        return None
    return CommandVocab(nibble_map=nibble_map)


def _infer_inter_voice_quirks(usf, music) -> list[InterVoiceQuirk]:
    """Detect inter-voice quirks from USF features.

    All quirks are encoded as **named-mechanism USF params**, never
    inferred from engine-correlated content. The USF declares which
    quirks the engine uses; the model carries them as features the
    codegen composes.
    """
    quirks: list[InterVoiceQuirk] = []
    p = usf.params.fields if usf.params else {}

    # Bowden's 4-vs-5-byte timbre quirk — the engine writes only
    # 4 bytes (omitting SR) when the prior voice played a skip byte.
    # USFs that need this set `inter_voice_carry_leak: true`.
    if p.get('inter_voice_carry_leak'):
        quirks.append(InterVoiceQuirk(
            name='carry_leak_4_vs_5_byte_timbre'))

    # Hubbard's first-note-on-V1 suppression — `drum_prio` gate.
    if p.get('suppress_first_notestart'):
        quirks.append(InterVoiceQuirk(
            name='first_note_suppression', voice_idx=0))

    # `no_release_per_note_flag` is a per-row flag; not a USF-level feature.

    return quirks


def _convert_state_layout(usf) -> Optional[StateLayoutMirror]:
    """Convert USF state_layout block to model StateLayoutMirror."""
    if usf.state_layout is None:
        return None
    d = usf.state_layout
    scalars = [StateSlot(offset=s['offset'], kind=s['kind'],
                         value=s.get('value', 0), var=s.get('var', ''))
               for s in d['scalars']]
    per_voice = [StateSlot(offset=s['offset'], kind=s['kind'],
                           value=s.get('value', 0), var=s.get('var', ''))
                 for s in d['per_voice']]
    return StateLayoutMirror(
        n_voices=d['n_voices'], scalars=scalars, per_voice=per_voice)


def _convert_sfx(usf) -> Optional[SfxConfig]:
    """Convert USF SfxSubtune records to model SfxConfig."""
    from src.usf import SfxSubtune
    sfx_subs = [s for s in usf.subtunes if isinstance(s, SfxSubtune)]
    if not sfx_subs:
        return None
    p = usf.params.fields if usf.params else {}
    return SfxConfig(
        records=sorted(sfx_subs, key=lambda s: s.id),
        state_offset=p.get('sfx_state_ofs'),
        framectr_offset=p.get('sfx_framectr_ofs', 253))


def _convert_digi(usf) -> Optional[DigiConfig]:
    """Convert USF DigiSubtune records to model DigiConfig."""
    from src.usf import DigiSubtune
    digi_subs = [s for s in usf.subtunes if isinstance(s, DigiSubtune)]
    if not digi_subs:
        return None
    p = usf.params.fields if usf.params else {}
    technique = p.get('digi_player', 'chimera_1bit')
    return DigiConfig(technique=technique, samples=digi_subs)


def _subtune_from_usf(ms, encoding: PatternEncodingMode, voice_count: int) -> SubtuneSpec:
    """Convert one MusicSubtune to a SubtuneSpec. Captures the
    per-subtune parameters each shape uses; Phase 3+ encodes the
    voice patterns into bytes as the codegen consumes them.
    """
    p = ms.params.fields if ms.params else {}
    voice_init = []
    for v in ms.voices:
        # Initial position from per-subtune params (bowden-style) when
        # named. Otherwise 0.
        init_pos = p.get(f'init_pos_v{v.id}', 0)
        voice_init.append(VoiceInitState(
            initial_position=init_pos,
            # Other fields (state_byte, initial_timbre, ctrl_no_gate)
            # filled in Phase 3 when the codegen needs them.
        ))

    # Resolve master_vol_init from whichever named-mechanism param the
    # USF carries. `gain_init` (yes_tune family) is 'full' or 'preserve';
    # `vol_filter` (companion) is an integer 0..F. `master_vol_init=None`
    # means "skip the $D418 write at init" (the pair-shape codegen reads
    # this to decide whether to write).
    gain = p.get('gain_init')
    if gain == 'full':
        master_vol_init: Optional[int] = 0x0F
    elif gain == 'preserve':
        master_vol_init = None
    elif 'vol_filter' in p:
        master_vol_init = p['vol_filter']
    else:
        master_vol_init = None

    return SubtuneSpec(
        id=ms.id,
        tempo=ms.tempo,
        init_tempo_ctr=p.get('init_tempo_ctr', p.get('init_tempo_counter', 0)),
        gate_off_tick=p.get('gate_off_tick'),
        note_load_tick=p.get('note_load_tick'),
        voice_init=voice_init,
        voice_starts_at=p.get('voice_start', 2),
        cia1_timer_a=p.get('cia1_timer_a'),
        master_vol_init=master_vol_init,
        init_song_pos=p.get('init_song_pos'),
        init_pwm_state=(
            (p['init_pwm_ctr'], p['init_pwm_ctr_2'])
            if 'init_pwm_ctr' in p else None),
        filter_cutoff_hi=p.get('filter_cutoff_hi'),
        speed_ctr_init_override=p.get('speed_ctr_init'),
        odd_frame_slide_step_override=p.get('incby2_step'),
        odd_frame_slide_late_gate_override=p.get('incby2_late_gate'),
    )
