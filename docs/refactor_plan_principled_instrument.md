# Refactor plan — principled Instrument schema (Hubbard migration + jay_derrett add)

> **Status: DONE 2026-06-01.** The five Instrument-schema leaks are
> closed; Hubbard 71/71 + Companion 35 + Jay_Derrett 17 byte-exact
> through the new schema. This document is the original plan, kept as
> historical reference for the design reasoning. Current schema state
> lives in `src/usf/types.py` and the `project_principled_instrument_refactor`
> memory.

## Goal

A schema audit found **five same-pattern leaks** in the `Instrument`
schema where per-instrument fields are paired with per-tune
parameters that complete their meaning. The pattern: a per-instrument
flag/scalar says "this instrument has effect X" but the actual
parameters of X live in `params { }` (or `engine_constants.py`),
shared across all instruments of the tune. Same effect-flag means
different musical behaviors across engines/tunes — exactly the §2
failure mode of the [USF representation principle](usf_representation_principle.md).

The five leaks:

1. **`freq_slide: bool`** + skydive curve params elsewhere (initial
   `slide_v`, step is hardcoded engine mechanism). Same flag means
   different slide curves across engines.
2. **`envelope.gate_off_delta: int`** + **`adsr_zero_delta`** (both
   currently DEAD in the composer code — not read) describe Hubbard
   release ARITHMETIC, not the musical content of release.
3. **`inc_by2: bool`** (per-inst) + **`incby2_step` / `incby2_late_gate`**
   (per-tune in `params { }`). The flag is meaningless without the
   per-tune step/gate values.
4. **`vibrato.scale: int`** (per-inst depth) + **`vib_onset`**
   (per-tune onset duration in `params { }`). Vibrato is a musical
   primitive; ALL its parameters (depth, onset, period if engine
   supports it) should be per-instrument.
5. **`arp.offsets: list[int]`** (per-inst) + **`arp_interval` /
   `arp_period` / `arp_phase_invert`** (per-tune in `params { }`).
   `ArpConfig.period` exists in the schema but is currently dead —
   composer reads `params.arp_period` instead. Arp is a per-instrument
   musical primitive; ALL its parameters should be per-instrument.

The refactor inlines every per-instrument musical parameter onto
each instrument. Per-tune params lose their effect-shape fields;
genuinely-per-tune content (master_vol formula, voice_starts,
engine-quirk booleans) stays in `params { }`.

After it lands, every Instrument is **fully self-described** —
schema review can read an instrument in isolation and know exactly
what it does musically. The model sees per-instrument values that
mean the same musical thing across all engines.

This refactor is also a prerequisite for jay_derrett, whose
per-instrument slide-params + per-instrument gate-off-ctrl don't
fit the existing schema at all (they need the typed sub-configs
that this refactor introduces).

## Success criteria

1. Every Hubbard '85 USF re-extracts with the new fields filled in;
   the rebuilt SIDs match byte-exact via `verify_all`. 71/71
   subtunes stay green through the regression.
2. Every Companion USF (35 subtunes across 5 strains) stays green
   through the regression.
3. 15/15 Type A jay_derrett SIDs build through the new composer
   path and pass `verify_all` (per-frame snapshot match).
4. A grep for the forbidden shapes returns nothing:
   - `freq_slide: bool`, `inc_by2: bool` (in USFs or schema)
   - `gate_off_delta:`, `adsr_zero_delta:` (in USFs or schema)
   - `vib_onset:`, `arp_interval:`, `arp_period:`, `arp_phase_invert:`
     in `params { }` blocks
   - `incby2_step:`, `incby2_late_gate:`, `incby2_onset:` in
     `params { }` blocks
5. Per-instrument cross-engine cardinality test: for each new
   per-inst field (e.g. `vibrato.onset`), grouping field values by
   engine should NOT show disjoint sets — same musical depth value
   should appear in Commando and Confuzion instruments alike. (§8
   test 2 from the principle doc.)

## New schema (in `src/usf/types.py`)

### `FreqSlideConfig` — replaces `freq_slide: bool` + skydive params

```python
@dataclass
class FreqSlideConfig:
    """Per-instrument freq slide / sweep — musical content, fully
    self-contained. Three operating modes covering the corpus so far:

      'none'           — no slide.
      'one_shot_halt'  — slide toward bound_1; at bound, step → 0
                         (freq frozen). Hubbard's skydive shape.
      'one_shot_swap'  — slide toward bound_1; at bound, jump to
                         bound_2 freq (and continue holding).
                         Bound-crossing arp shape.
      'bidirectional'  — slide toward bound_1; at bound, flip
                         direction; slide toward bound_2; flip; repeat.

    All bounds are SIGNED 16-bit deltas from the note's freq-table
    value (the engine adds them at note-start to get absolute target
    freqs).

    `high_oct_arp` selects the high-octave freq variant
    (`freq_table[note + 16]`) as the SID write source when the slide
    has crossed bound_1 — used by jay_derrett's bound-crossing arp.
    """
    mode: str = 'none'                  # 'none' | 'one_shot_halt' |
                                        # 'one_shot_swap' | 'bidirectional'
    initial_dir: str = 'up'             # 'up' (ADC) or 'down' (SBC)
    upper_delta: int = 0                # signed 16-bit
    lower_delta: int = 0                # signed 16-bit
    step: int = 0                       # 16-bit unsigned
    high_oct_arp: bool = False
```

### `IncBy2Config` — replaces `inc_by2: bool` + incby2 params

```python
@dataclass
class IncBy2Config:
    """Per-instrument odd-frame freq-hi ramp (Hubbard '85's `inc_by2`
    effect). On every other frame (frame_ctr & 1), the engine adds
    `step` to freq_hi until duration reaches `late_gate` threshold,
    then halts. `onset` delays the start by N frames after note-on.

    mode='none' = no ramp. Otherwise:
      'on'     — ramp active for the whole note.
      'late_gated' — ramp halts when `v_dur < late_gate`.
    """
    mode: str = 'none'                  # 'none' | 'on' | 'late_gated'
    step: int = 1                       # 8-bit signed
    onset: int = 0                      # frames after note-on
    late_gate: int = 0                  # only used if mode='late_gated'
```

### `EnvelopeConfig` — `release_ctrl` replaces both deltas

```python
@dataclass
class EnvelopeConfig:
    release_ctrl: int = 0               # CTRL byte during release.
                                        # Always present, explicit.
    # gate_off_delta + adsr_zero_delta — REMOVED (dead in composer;
    # release_ctrl carries the musical content directly).
```

### `VibratoConfig` — onset moves from per-tune

```python
@dataclass
class VibratoConfig:
    scale: int = 0                      # depth — already per-inst
    onset: int = 6                      # NEW — was per-tune
                                        # `params.vib_onset`. 6 was
                                        # the codebase default.
```

### `ArpConfig` — interval / phase_invert / period all move to per-inst

```python
@dataclass
class ArpConfig:
    offsets: list[int] = field(default_factory=list)  # already per-inst
    interval: int = 12                  # NEW — was per-tune
                                        # `params.arp_interval` (semitones
                                        # to add per arp step).
    period: int = 2                     # FIELD EXISTS BUT WAS DEAD —
                                        # composer now reads from instrument
                                        # instead of `params.arp_period`.
                                        # Default 2 = Commando-family value.
    phase_invert: bool = False          # NEW — was per-tune
                                        # `params.arp_phase_invert`.
```

### `PwmConfig` — small expansion for jay_derrett's two-phase shape

```python
@dataclass
class PwmConfig:
    # Existing fields (Hubbard '85 / clever_music):
    mode: str = 'none'
    speed: int = 0
    init: int = 0
    min_hi: int = 0
    max_hi: int = 0
    # New (jay_derrett's two-phase modulation):
    phase1_dir: str = 'up'              # 'up' | 'down'
    phase1_bound: int = 0
    phase1_step: int = 0
    # Existing min_hi / max_hi / speed serve as the phase2/oscillation
    # bounds/step (already named bound-shaped). No new fields needed
    # for the oscillation half.
```

### `Instrument` — booleans removed, sub-configs added

```python
@dataclass
class Instrument:
    # Existing:
    id: int
    name: Optional[str] = None
    waveform: list[int] = field(default_factory=list)
    loop: int = 0
    pwm: PwmConfig = field(default_factory=PwmConfig)
    adsr: tuple = (0, 0)
    arp: ArpConfig = field(default_factory=ArpConfig)
    vibrato: VibratoConfig = field(default_factory=VibratoConfig)
    envelope: EnvelopeConfig = field(default_factory=EnvelopeConfig)
    # REMOVED: freq_slide: bool, inc_by2: bool
    # NEW:
    freq_slide_config: FreqSlideConfig = field(default_factory=FreqSlideConfig)
    inc_by2_config: IncBy2Config = field(default_factory=IncBy2Config)
```

## Params fields that go away after migration

The following per-tune `params { … }` fields are removed once their
content moves to per-instrument:

- `vib_onset` → `vibrato.onset` (per-inst)
- `arp_interval` → `arp.interval` (per-inst)
- `arp_period` → `arp.period` (per-inst)
- `arp_phase_invert` → `arp.phase_invert` (per-inst)
- `incby2_step` → `inc_by2_config.step` (per-inst)
- `incby2_late_gate` → `inc_by2_config.late_gate` (per-inst)
- `incby2_onset` → `inc_by2_config.onset` (per-inst)

For each: during Phase 2 (Hubbard migration), every instrument in
each Hubbard USF gets the per-tune value copied onto its per-inst
field. The composer then reads per-inst values. If two instruments
in the same Hubbard USF carry different values (impossible for the
engine to realize), the composer asserts equality and uses the
shared value.

## Params fields that STAY (out of scope for this refactor)

These are TUNE-LEVEL or ENGINE-QUIRK fields, not per-instrument
musical content. They warrant a separate analysis pass:

- `master_vol_*` (master VOL formula — per-tune musical content)
- `voice_starts`, `subtune_overrides` (tune structural)
- `linear_pw_or`, `seed_overlap`, `suppress_first_notestart`,
  `first_frame_gate_off`, `frame_ctr_init`, `tie_preserves_slide`,
  `speed_ctr_init`, `freeze_on_stop`, `stop_fill`,
  `loop_silences_song`, `hubidx_wrap_at_patend`,
  `ns_offtab_decr_offset`, `sfx_*`, `has_sfx`, `digi_player` —
  engine-quirk booleans + SFX/digi bookkeeping. Each likely
  warrants a more-musical reframing, but doing them en masse is
  separate from the per-instrument leak fix.

## Phase 1 — additive schema changes (no migrations)

Goal: all new fields exist; old fields still present; all existing
tests pass.

1. **Grammar / parser / writer** (`src/usf/grammar.lark`,
   `parser.py`, `writer.py`, `types.py`):
   - Add `freq_slide { … }` block syntax inside `instrument`.
   - Add `inc_by2 { … }` block syntax inside `instrument`.
   - Add `release_ctrl: $NN` inside `envelope { … }`.
   - Add `onset` field inside `vibrato { … }`.
   - Add `interval` / `phase_invert` fields inside `arp { … }`.
     (`period` field already exists in grammar — currently dead.)
   - Add `phase1_dir` / `phase1_bound` / `phase1_step` inside
     `pwm { … }`.
   - All new fields are OPTIONAL; absent → default values.
   - Existing `freq_slide` / `inc_by2` fx flags stay accepted.

2. **Composer reads either** (`pipelines/composer.py`):
   - If `freq_slide_config.mode != 'none'` → use config.
   - Else if `freq_slide: bool` → fall back to existing path (read
     skydive params from `params { }`).
   - Same dual-path for `inc_by2_config` / `inc_by2: bool`.
   - If `envelope.release_ctrl != 0` → use directly.
   - For vibrato/arp: prefer per-instrument fields if present;
     fall back to `params { }` values for back-compat.

3. **Tests**: `pytest pipelines/` + `tools/regression.py` — 71+35
   subtunes stay green. No USF files touched yet.

**Commit boundary**: schema additions land, nothing migrates yet,
zero risk to existing builds.

## Phase 2 — Hubbard '85 extract migration

Goal: every Hubbard USF carries the new per-instrument fields,
populated from the engine's existing tune-level params + per-inst
flags. Composer prefers per-inst values over the params fallback.

For each instrument in each Hubbard '85 engine, derive at extract
time:

1. **`freq_slide_config`** — if `freq_slide: bool` was set:
   - mode = `'one_shot_halt'` (Hubbard's skydive is one-shot,
     freezes at bound).
   - initial_dir = `'down'` (skydive decrements).
   - upper_delta = 0, lower_delta = 0 (target = 0; bound is "freq
     reaches zero").
   - step = 1 (hardcoded engine mechanism — v_slide decrements
     by 1 each frame).
   - high_oct_arp = False.

2. **`inc_by2_config`** — if `inc_by2: bool` was set:
   - mode = `'late_gated'` if the tune has `params.incby2_late_gate`,
     else `'on'`.
   - step = `params.incby2_step` (default 1).
   - onset = `params.incby2_onset` (default 0).
   - late_gate = `params.incby2_late_gate` (default 0).

3. **`envelope.release_ctrl`** = `waveform[0] & 0xFE` (Hubbard's
   gate-off = gate bit cleared).

4. **`vibrato.onset`** = `params.vib_onset` (per-tune value copied
   to every instrument that has vibrato).

5. **`arp.interval`** = `params.arp_interval` (per-tune value
   copied to every instrument).
   **`arp.period`** = `params.arp_period`.
   **`arp.phase_invert`** = `params.arp_phase_invert`.

Steps:

1. Update `pipelines/hubbard/to_usf.py` (the v3 extract) to emit
   the new per-instrument fields, populated from the per-engine
   `EngineConfig`/`EngineConstants` data.
2. **Re-extract all 12 Hubbard engines.** New USF files carry both
   old + new fields. Composer reads new when present.
3. **Regression**: Hubbard 71/71 must stay green.

**Commit boundary**: Hubbard USFs migrated, both old + new fields
present, regression green.

## Phase 3 — drop deprecated fields

Goal: old engine-bookkeeping shapes gone from schema + code +
USFs.

1. **Composer**: remove all fallback paths. Read only:
   - `freq_slide_config` (not `freq_slide: bool` + `params` lookup)
   - `inc_by2_config` (not `inc_by2: bool` + `params` lookup)
   - `envelope.release_ctrl` (not `gate_off_delta` + waveform-deriv)
   - `vibrato.onset` (not `params.vib_onset`)
   - `arp.interval` / `arp.period` / `arp.phase_invert` (not
     `params.*` versions)
   Anything still missing in a USF → composer raises a clear
   validation error.

2. **Schema**: remove these fields:
   - `Instrument.freq_slide: bool`
   - `Instrument.inc_by2: bool`
   - `EnvelopeConfig.gate_off_delta`
   - `EnvelopeConfig.adsr_zero_delta`
   - Grammar's `fx: freq_slide`, `fx: inc_by2` flag tokens
   - Grammar's `env_args` accepting `gate_off_delta` / `adsr_zero_delta`

3. **Params cleanup**: USF writer + parser + grammar stop accepting
   the deprecated per-tune keys (`vib_onset`, `arp_interval`,
   `arp_period`, `arp_phase_invert`, `incby2_step`,
   `incby2_late_gate`, `incby2_onset`). Anyone who writes one gets
   a clear error from the validator.

4. **Re-extract all 12 Hubbard engines** one more time (writes
   USFs without the deprecated fields and without the deprecated
   params keys). Run `tools/regression.py`: still 71/71 green.

**Commit boundary**: schema is fully principled for these five
leak shapes. The forbidden grep returns nothing.

## Phase 4 — jay_derrett extract → USF

Goal: 15 Type A USF files written, parsing round-trip, validating.

1. **`pipelines/companion/jay_derrett/extract/instrument.py`** (new):
   Given a 24-byte instrument program (already captured in the
   `_extracted/<NAME>.json` dumps), decode into:
   - `waveform: [ctrl_byte]` from offset $14
   - `adsr: (AD, SR)` from $15/$16
   - `envelope.release_ctrl = ctrl_byte | offset_$17`
   - `pwm: PwmConfig(...)` from $0A-$12 (two-phase as designed)
   - `freq_slide_config: FreqSlideConfig(...)` from $00 + $03-$08
   - Bytes $09, $0D, $13: dropped (unread by engine, irrelevant
     to instruction stream).

2. **`pipelines/companion/jay_derrett/extract/to_usf.py`** (new,
   modeled on `clever_music/extract/to_usf.py`):
   - Consume the JSON dump.
   - Walk per-voice byte stream → NoteRows (row vocabulary per the
     schema proposal: `set_dur=$NN`, `section_end=N` + existing
     `tempo=N`/`vol=N`/`i{N}` etc).
   - Decode instruments via instrument.py.
   - Inline freq table.
   - Validate + write to `hvsc84/MUSICIANS/D/Derrett_Jay/<NAME>.usf`.

3. **15 USF files written and parsing round-trip.** No composer
   work yet; just that the schema is expressive enough to hold the
   data and the writer round-trips.

**Commit boundary**: extract side complete for Type A.

## Phase 5 — composer codegen for jay_derrett

Goal: `build_from_usf` emits a jay_derrett-shape SID from each
USF. Free to invent any 6502 architecture — only the SID writes
per frame need to match the original.

1. **Add `_emit_jay_derrett_bytes()`** in `composer.py` (parallel
   to `_emit_hubbard85_bytes()`):
   - Per-voice orderlist emitted as a flat byte stream (codegen
     can use ANY scheme — doesn't have to be the original's
     pointer-walker + sub-jump table).
   - For each instrument: emit a per-frame modulation block that
     reads from `freq_slide_config` + expanded `PwmConfig` + the
     envelope settings, writes SID registers each frame matching
     the original's pattern.
   - For section_end fx flag: emit a per-voice loop-back to start
     (simplest scheme — original's global counter trick is
     replaced with per-voice pointer reset).

2. **Dispatch in `emit_sid_from_usf`**: detect jay_derrett by
   instrument shape (presence of `freq_slide_config` with non-`none`
   mode + the two-phase PWM config? Or via a top-level signal). TBD
   the cleanest discriminator.

3. **Build all 15 → SIDs.**

**Commit boundary**: composer can produce SIDs for jay_derrett.
Verification is the next phase.

## Phase 6 — verify + per-tune debug

Goal: 15/15 Type A pass per-frame snapshot match.

1. **`verify_all` on all 15.** First pass will surface mismatches.
2. **Per-tune debug**: for each failing subtune, capture the first
   mismatching frame, trace which SID register/voice/instrument
   the mismatch points to, fix the composer's modulation code.
3. **Roll into `tools/regression.py`**: add jay_derrett's 15 to
   the known-clean roster.

**Commit boundary**: jay_derrett Type A done. Total: Hubbard 71 +
Companion 35 + jay_derrett 15 = 121 subtunes verified.

## Out of scope (surfaced for future work)

Remaining `params { }` fields are tune-level / engine-quirk rather
than per-instrument musical content. Each likely warrants a more-
musical reframing, but they're a separate analysis pass from the
per-instrument leak fix this refactor addresses:

- **Master volume modulation** — `master_vol_subtrahend_voice`,
  `master_vol_base`, `master_vol_trigger`, `master_vol_reset_on_loop`,
  `master_vol_underflow_clamp`. Currently a 5-knob ad-hoc shape.
  Likely refactorable into a unified `master_vol_modulation { … }`
  block with named modes — but that's its own analysis.

- **Engine-quirk booleans** — `linear_pw_or`, `seed_overlap`,
  `suppress_first_notestart`, `first_frame_gate_off`,
  `frame_ctr_init`, `tie_preserves_slide`, `freeze_on_stop`,
  `stop_fill`, `loop_silences_song`, `hubidx_wrap_at_patend`,
  `ns_offtab_decr_offset`. Each names an engine BEHAVIOR. Some are
  legitimate per-tune musical state (song-end semantics); others
  smell engine-mechanism-flavored. Each warrants individual review
  against the §6 challenge.

- **SFX bookkeeping** — `sfx_state_ofs`, `sfx_framectr_ofs`,
  `has_sfx`. Engine-positional addresses; could be replaced with
  a musical `has_sfx: bool` and the offsets becoming engine-
  internal (composer's choice).

- **Digi named reference** — `digi_player: chimera_1bit` is a
  named reference to a digi-mechanism implementation. Borderline
  Pole-A but the value is musically descriptive. Probably fine
  but worth confirming once more engines with digi land.

- **Tune structural** — `voice_starts`, `subtune_overrides`,
  `speed_ctr_init` — these are tune-structural, not effect-shape.
  Per-tune is correct; might benefit from a tidier organization.

Tracked as a separate audit pass after this refactor lands. Not
blocking jay_derrett.

## Risks

- **Phase 2 derivation correctness**: computing `release_ctrl` and
  `freq_slide_config` from existing data + engine_constants must
  be exact, or Hubbard regression breaks. Mitigation: re-run
  `verify_all` after each engine migrates; isolate any failures
  per-engine.
- **Phase 5 composer**: implementing jay_derrett's modulation
  cleanly (without the original's self-mod-counter dispatch) takes
  real work. First pass may need iteration. Mitigation: start with
  the simplest tune (Ninja_Hamster — smallest, fully RE'd), get it
  byte-exact, then scale.
- **Phase 4 PWM two-phase**: the schema design for two-phase PWM
  needs confirmation that no Hubbard '85 instrument needs the
  expanded fields — if any do, those need to be set during the
  Phase 2 migration too.

## Estimated session count

The scope expanded from 2 leak fixes to 5 (vibrato.onset,
arp.interval/period/phase_invert, inc_by2_config also covered).
Roughly 1 extra session worth of work across phases 1-3 — the
mechanical pattern is the same per field; each addition is a small
extension of the same code path.

- Phase 1: 1-2 sessions (more grammar/parser/writer additions).
- Phase 2: 2 sessions (per-engine extract migration + regression
  triage — five new fields to derive correctly).
- Phase 3: 1 session (cleanup + per-tune key removal).
- Phase 4: 1 session.
- Phase 5: 1-2 sessions.
- Phase 6: 1-2 sessions (per-tune debugging).

Total: ~7-10 sessions.
