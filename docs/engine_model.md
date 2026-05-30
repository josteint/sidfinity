# Engine model — composable codegen spec

The engine model is the layer between USF (engine-blind musical
content) and 6502 asm (engine-specific implementation). It's a
Python dataclass tree, parametric over features, that the codegen
reads to emit asm. **No engine identity.** Each engine becomes a
*point* in the model's parameter space.

Module: `pipelines/engine_model.py`. Builder: `from_usf(usf)`. Tests:
`tests/test_engine_model_audit.py`.

## Layer position

```
USF (.usf file)
  ↓ src.usf.parse_file
UsfFile dataclass
  ↓ pipelines.engine_model.from_usf
EngineModel  ← THIS LAYER
  ↓ pipelines.universal_codegen (codegen — Phase 3+)
6502 asm
  ↓ xa65
6502 bytes
  ↓ PSID wrapper
.sid file
```

The model is the artifact that didn't exist before. It captures every
feature the audit identified, parametrically.


## Top-level structure

```
EngineModel
├── psid             PsidMeta (title, author, clock, sid_model, ...)
├── voices           VoiceConfig (count, ctrl_source)
├── pattern          PatternConfig (encoding, pitch_byte_format, ...)
├── voice_timing     VoiceTiming (every_tick / dur_counter / tick_counter)
├── tempo_dispatch   TempoDispatch (single_phase / two_phase, cia1)
├── terminators      TerminatorVocab (byte → behavior map)
├── instruments      list[InstrumentProgram]
├── master_vol       MasterVolConfig (fixed / per_subtune / mutable / fade)
├── subtunes         list[SubtuneSpec]
├── freq_table       bytes (engine mechanism, currently inlined in USF)
└── (optional)
    commands           CommandVocab — embedded $Bx/$Cx/$Dx/$Ex bytes
    inter_voice_quirks list[InterVoiceQuirk]
    state_layout       StateLayoutMirror — off-table arpeggio state mirror
    sfx                SfxConfig — sound-effect sub-engine
    digi               DigiConfig — digi sub-engine
    hardcoded_pw_sweep HardcodedPwSweep — single-voice forced PW sweep
    compound           CompoundSpec — N packed sub-engines + dispatcher
```

Every field maps to a feature the audit found in at least one
engine. Optional fields stay `None` for USFs that don't use them.


## Feature dimensions

The model spans these dimensions; the values listed are the ones the
6 currently-supported shapes occupy.

### Pattern encoding (`PatternConfig`)

| Mode | Used by | Description |
|---|---|---|
| `atomic_per_tick` | henrys, bowden, clever_music | 1 byte = 1 tick; duration via skip-byte runs |
| `atomic_per_period` | companion | 1 byte = 1 note period; duration from tempo dividers |
| `note_dur_pair` | yes_tune | 2 bytes per row (note_byte, duration_byte) |
| `bitpack` | Hubbard '85 | variable-bit-width packed bitstream |

Pitch byte format:
- `octave_semi_nibble`: `(octave << 4) | semi` — used by henrys, bowden, yes_tune, clever, companion.
- `absolute_semi`: `note + 12*octave` — Hubbard '85.

### Voice timing (`VoiceTiming`)

Behavior **within** a fired tempo tick:

| Mode | Used by | Description |
|---|---|---|
| `every_tick` | henrys, bowden, companion | No per-voice counter — every voice reads every fired tick |
| `dur_counter_decrement` | clever_music, Hubbard '85 | Per-voice counter decrements every fired tick; reads on counter==1 |
| `tick_counter_decrement` | yes_tune | Per-voice counter decrements every fired tick; plays on counter==0 |

### Tempo dispatch (`TempoDispatch`)

Decides when a tempo tick fires (which gates voice processing):

| Mode | Used by | Description |
|---|---|---|
| `single_phase` | henrys, bowden, yes_tune, clever, Hubbard | One global counter; fires when counter crosses threshold |
| `two_phase` | companion | Two counters (gate_off_tick + note_load_tick); gate_off fires early-release, note_load fires next-note |

### Terminator vocabulary (`TerminatorVocab`)

Map of byte value → behavior. Each behavior is a parametric musical
or mechanism action. Behaviors:

- `note` — default for in-range pitch bytes
- `rest_gate_off` — write ctrl gate-off
- `skip` — no SID write
- `loop_reset` — reset pattern ptr to start
- `loop_substitute_first` — pos=1, replay orderlist[0] this tick (bowden)
- `song_end_voice` — voice stops permanently
- `song_end_voice_freeze` — voice freezes (holds note, runs effects)
- `song_end_stop_fill` — write STOP_FILL byte to $D400-$D417 (Action Biker)
- `master_vol_reset_and_loop` — write $D418 + reset pos (henrys)
- `end_song_on_voice_n` — clears alive flag + writes $D418=0 (companion V3)
- `set_duration_next_byte` — read next byte as new dur_ctr (clever $82)
- `early_release_flag` — bit-7-on-pitch schedules gate-off (companion)

### Modulation programs (`InstrumentProgram`)

Per-instrument modulation runs each fired tempo tick. Each program
is `Optional[T]` — `None` means the instrument doesn't use it.

| Program | Hubbard '85 fx_flags bit | Description |
|---|---|---|
| `Vibrato` | 3 | Triangle LFO on freq |
| `PwmLinear` | 4 | pw_lo += speed per frame |
| `PwmBidirectional` | (encoded in PwmConfig.mode) | Triangle PWM with bounds |
| `Arpeggio` | 2 | Multi-step semitone arpeggio |
| `FreqHiSlide` | 0 | freq_hi slide while v_dur > 0 (skydive) |
| `OddFrameSlide` | 1 | odd-frame freq_hi slide (incby2) |
| `PerNotePortamento` | (per-note `drum_trig`) | per-note pitch slide |

### Master volume (`MasterVolConfig`)

| Mode | Used by |
|---|---|
| `fixed_init` | Most engines — write $0F once at init |
| `per_subtune_init` | yes_tune (gain_init), companion (vol_filter) |
| `mutable_commands` | clever_music — $Cx writes new value mid-stream |
| `fade_progressive` | Hubbard '85 — TOAS family; decreases on configured voice's pattern-end |

### Inter-voice quirks (`InterVoiceQuirk`)

| Quirk | Used by | Description |
|---|---|---|
| `carry_leak_4_vs_5_byte_timbre` | bowden | Skip-byte voice causes next voice to omit SR write |
| `first_note_suppression` | Hubbard (drum_prio) | V1's first note's writes suppressed |
| `no_release_per_note_flag` | Hubbard | Per-note flag skips hard-restart writes |

### Off-table arpeggio (`StateLayoutMirror`)

Hubbard '85's `state_layout` block. When pitch ≥ 96, the engine
reads past the 96-entry freq table into engine state. The mirror
makes those reads parametric.

### Sub-engines

- `SfxConfig` — sound-effect sub-engine (16 records, 2-voice freq-sweep + register snapshot). Hubbard '85 only.
- `DigiConfig` — digi sub-engine (currently `chimera_1bit`). Hubbard '85 only.

### Compound builds (`CompoundSpec`)

5_Title_Tunes-style: N packed engine instances + dispatcher at the
original init/play vectors. Distinct from per-subtune mechanism.


## Builder behavior

`from_usf(usf)` reads each feature dimension **independently** from
the USF. It does NOT detect "which engine produced this USF" before
populating the model. Each detection is content-based:

- "Does any instrument have vibrato?" → `instrument.vibrato.scale != 0`
- "Does any voice have a stop terminator?" → `orderlist.entries and orderlist.stop`
- "Does any subtune carry `gate_off_tick`?" → `params.fields['gate_off_tick']`
- etc.

Multiple features can be true simultaneously; the model captures all
of them. The eventual codegen reads which features are set and emits
asm for each — there's no shape selection step.

## Test coverage

`tests/test_engine_model_audit.py` runs the builder against one or
more USFs per shape and asserts:
- Pattern encoding mode + pitch byte format
- Voice timing mode
- Tempo dispatch mode
- Master vol mode
- Terminator vocab entries
- Sub-engine presence (SFX, digi, state_layout, hardcoded_pw_sweep)
- Per-shape commands presence

If a feature dimension is added to the model, add an assertion in
the relevant test confirming the builder populates it.


## What this layer does NOT do

- **Emit asm.** That's the codegen layer (Phase 3+).
- **Validate USF correctness.** USF is validated by `src.usf.validate`
  before reaching the builder.
- **Verify byte-exact output.** That's `verify_all` and
  `compare_instruction_stream` on the rebuild path.
- **Identify the originating engine.** Forbidden by principle. The
  model captures *what features the music uses*, not *which engine
  produced it*. Two USFs from different engines that happen to use
  the same features will produce identical model instances.


## Open items for Phase 3+

- **Voice-init seeding** — `VoiceInitState` is defined but the
  builder only populates `initial_position` today. Phase 3+ fills in
  per-voice timbres, state bytes, and ctrl_no_gate as the codegen
  consumes them.
- **Per-voice pattern bytes** — `SubtuneSpec.voice_patterns` is empty
  in Phase 2 output. Phase 3+ encodes each voice's pattern row stream
  to bytes (the encoding chosen by `PatternConfig.encoding`).
- **Carry-leak detection** — bowden's `InterVoiceQuirk` isn't
  populated today; the audit identified it but the converter
  doesn't add it yet. Phase 4 (bowden absorption) adds the
  detection + the feature.
- **`bitpack_dur_bits` / `bitpack_inst_bits`** — currently default
  to 4 / 6 (Hubbard's `BitPackCodec` defaults). When `BitPackCodec`
  becomes parametric per-USF, these are read from the USF instead.
- **Compound builds** — the converter doesn't handle 5_Title_Tunes
  compound USFs yet. Phase 8 covers Hubbard '85; compound is part
  of that scope.
