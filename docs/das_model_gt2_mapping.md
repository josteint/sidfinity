# Das Model ↔ GT2 Mapping

This document maps GoatTracker 2 (GT2) features to Das Model (T, I, S) components,
identifies what Das Model cannot represent today, and proposes concrete extensions.

## 1. What Das Model IS

Das Model formalises every SID performance as:

```
SID = (T, I, S)

T : Frequency Table        — note index → 16-bit SID freq
I : Instrument[]           — behavioral programs (W, F, P, E)
S : Score                  — events: (time, voice, note, instrument_id)
```

The universal engine executes (T, I, S) mechanically — it knows nothing about
GT2, Hubbard, or any other player.  All musical variation lives in the data.

## 2. GT2 Component Map

### 2.1 Frequency Table → T

GT2 embeds a 96-entry freq_lo/freq_hi table in the SID binary.
`find_freq_table` + `gt2_parse_direct` extract it exactly.

```
GT2 freq table  →  T : note_index → uint16
```

The USF `Song.freq_lo` and `Song.freq_hi` fields carry this directly.
Das Model T is an exact 1-to-1 representation.  **Full coverage.**

### 2.2 Instruments → I

Each GT2 instrument has these binary columns:

| GT2 column   | Type      | Das Model target |
|--------------|-----------|-----------------|
| `ad`         | uint8     | E.ad            |
| `sr`         | uint8     | E.sr            |
| `gate_timer` | uint8 (bits 6-0 = frames, bit 6 = legato, bit 7 = no-HR) | E.gate_off_delta / E.adsr_zero_delta |
| `first_wave` | uint8     | W (first step waveform byte) |
| `wave_ptr`   | uint8     | W (pointer into shared wave table) |
| `pulse_ptr`  | uint8     | P (pointer into shared pulse table) |
| `filter_ptr` | uint8     | F_filt (pointer into shared filter table — NOT in Das Model F) |
| `vib_param`  | uint8     | speed table index for vibrato — no Das Model equivalent yet |
| `vib_delay`  | uint8     | vibrato delay frames — no Das Model equivalent yet |

#### 2.2.1 Wave Table → W

GT2 shared wave table entries: `(left_byte, right_byte)`.

| GT2 left byte  | Meaning                         | USF / Das Model W |
|----------------|---------------------------------|--------------------|
| $00            | no wave change                  | WaveTableStep.waveform = 0 (no write) |
| $01–$0F        | delay N frames                  | WaveTableStep.delay = N |
| $10–$DF        | SID control byte (waveform)     | WaveTableStep.waveform = byte |
| $E0–$EF        | silent/inaudible waveform ($00–$0F SID value) | WaveTableStep.waveform = byte & $0F |
| $F0–$FE        | pattern command (tempo, wave, filter, volume...) | WaveTableStep (command), no Das Model equivalent |
| $FF            | loop/jump                       | WaveTableStep.is_loop + loop_target |

| GT2 right byte | Meaning                         | USF / Das Model F |
|----------------|---------------------------------|--------------------|
| $00–$5F        | relative note offset up (0–95)  | WaveTableStep.note_offset |
| $60–$7F        | relative note offset down (−32–−1) | WaveTableStep.note_offset (signed) |
| $80            | keep frequency (no change)      | WaveTableStep.keep_freq = True |
| $81–$DF        | absolute note (1–95)            | WaveTableStep.absolute_note |

Das Model W maps directly: each wave table step produces one SID control byte per
frame, with looping.  Das Model W `steps[]` = sequence of wave table left bytes
(after bias removal).  Das Model F `offsets[]` = sequence of right-byte note
offsets.  **Full coverage for arpeggio, hard restart, noise bursts.**

Das Model F is a *note-offset sequence* — this handles GT2's arpeggio (right column
steps through intervals while W advances waveforms).  One F program and one W program
share the same step counter, advancing in lockstep.  This is equivalent to GT2's
paired left/right columns.

**Where it diverges:** Das Model F offsets are `int8` — covers ±127 semitones.
GT2 right-column absolute notes ($81–$DF) need a separate flag (`absolute_note`),
which USF WaveTableStep already carries but Das Model's formal F program spec does
not describe.  Minor extension needed (see Section 4.1).

#### 2.2.2 Pulse Table → P

GT2 pulse table entries: `(left_byte, right_byte)`.

| GT2 left byte | Meaning                          | Das Model P |
|---------------|----------------------------------|-------------|
| $01–$7F       | modulate for N frames            | P.speed applied N times |
| $80–$8F       | set pulse width (high nib = pw_hi) | P.init_pw + mode='none' for that step |
| $FF           | loop/jump                        | P.loop |

The right byte is the signed speed (modulate) or low byte (set).

Das Model P has: `speed`, `mode` (none/linear/bidirectional), `min_hi`, `max_hi`,
`init_pw`.  This covers GT2's most common pulse patterns (linear speed with optional
direction reversal at boundaries).

**Where it diverges:**
- GT2 pulse table is a *multi-step program*, not a single (speed, mode) pair.
  A pulse table can: set PW to value A, modulate at speed X for 8 frames, then set
  to value B, then loop back to the modulate phase.  Das Model P cannot represent
  this — it has only one speed and one mode for the whole instrument.
- GT2 supports bidirectional mode via `$8x` set commands on boundary, not via
  dedicated min/max registers.  The V2 codegen emulates GT2 exactly from the
  table bytes; Das Model P abstracts this into `min_hi/max_hi` bounds, which is
  sufficient for the common case but not for arbitrary multi-phase patterns.

**Verdict:** Das Model P needs extension to a *program* (sequence of pulse steps
with loop) rather than a fixed (speed, mode) tuple.  See Section 4.2.

#### 2.2.3 Filter Table → F_filt (NOT in Das Model)

GT2 has a per-instrument filter table pointer.  The filter table controls:
- Filter cutoff (set or modulate)
- Filter resonance + routing (which voices pass through filter)
- Filter mode (low/band/high pass)

Das Model has **no filter component**.  The universal engine in das_model.md writes
W, F, P, E only — SID registers $D415–$D418 (filter cutoff, resonance, mode/volume)
are not touched.

In the current USF+codegen_v2 pipeline, filter tables ARE fully supported via
`Song.shared_filter_table` and the codegen emits filter update code when needed.
USF has `FilterTableStep` with type ('cutoff', 'modulate', 'params', 'loop'),
value, duration, cutoff_low.  This is fully expressive for GT2 filter use.

Das Model needs a new component to cover this.  See Section 4.3.

#### 2.2.4 Vibrato → no Das Model equivalent

GT2 vibrato is defined by:
- `vib_param` (uint8): speed table index — points to a (speed, depth) entry
- `vib_delay` (uint8): frames before vibrato kicks in
- Speed table `left` byte: bit 7 = note-independent speed (GT2 "calculated speed")

Das Model has no vibrato program.  Vibrato is a periodic frequency modulation — it
could in principle be encoded in F as a repeating sine-shaped offset sequence, but:
1. GT2 vibrato uses a built-in sine table (not the wave table right column)
2. The depth and phase are engine-computed, not stored per-frame in any table
3. The "note-independent speed" (bit 7 of speed table left) changes behaviour

Das Model needs a vibrato sub-spec or a new F program mode.  See Section 4.4.

#### 2.2.5 Portamento and Tone Portamento → no Das Model equivalent

GT2 pattern commands $01/$02 (portamento up/down) and $03 (tone portamento) glide
pitch between notes using the speed table.  These are score-level effects, not
instrument-level programs.

Das Model F is note-offset only — it cannot express continuous pitch glides that
depend on the current vs target note frequency.  See Section 4.5.

#### 2.2.6 Hard Restart → E

GT2 hard restart uses `gate_timer` (bits 5–0 = frames before note end to fire HR).
The V2 codegen maps this to:
- `gate_off_delta`: frames before note end to clear gate bit
- `adsr_zero_delta`: frames before note end to write $00 to AD/SR registers
- `hr_method`: 'none', 'gate', 'test', 'adsr'
- `legato`: bit 6 of gate_timer byte — skip ADSR retrigger

Das Model E already captures this correctly.  **Full coverage.**

### 2.3 Score → S

GT2 score is encoded as:
- **Patterns**: sequences of NoteEvents (note/rest/off/on/tie), each with optional
  instrument change and pattern command.
- **Orderlists**: per-voice sequences of (pattern_id, transpose) pairs with loop.
- **Tempo**: DEFAULTTEMPO (frames per tick); per-channel overrides via command $0F.

Das Model S is simpler: flat per-voice `NoteEvent[]` with (note, duration, instrument).

| GT2 concept          | Das Model S equivalent |
|----------------------|------------------------|
| Pattern rows         | NoteEvent sequence (flattened) |
| Orderlist + transpose | NoteEvent with transposed note |
| Tempo (global)       | Score.tempo |
| Per-channel tempo ($0F) | No Das Model equivalent — tempo is global |
| Pattern commands ($01–$0E) | Not in Das Model S (score-level effects) |
| Multi-song (subtunes) | Not in Das Model S |
| Keyoff / keyon events | Not in Das Model S |
| Tied notes           | Das Model duration accumulation |
| Multispeed (CIA timer) | Not in Das Model (implicit multiplier) |

Das Model S is sufficient for the common case (notes, rests, instrument changes,
global tempo) but is too simple for GT2's full expressiveness.

## 3. Summary: Coverage Matrix

| GT2 Feature               | Das Model component | Coverage |
|---------------------------|---------------------|----------|
| Frequency table           | T                   | Full     |
| ADSR (AD, SR)             | E.ad / E.sr         | Full     |
| Hard restart (gate_timer) | E.gate_off_delta / E.adsr_zero_delta | Full |
| Legato                    | E (gate_off_delta=0)| Full     |
| Wave table (waveform sequence + loop) | W        | Full     |
| Wave table arpeggio (right column note offsets) | F | Full (int8 offsets) |
| Wave table absolute notes ($81–$DF) | F.absolute_note | USF has it; Das Model spec needs updating |
| Wave table delays ($01–$0F left) | W.delay          | USF has it; Das Model spec does not mention |
| Wave table commands ($F0–$FE left) | None             | Not representable in Das Model |
| Pulse table (linear modulation) | P (mode=linear)   | Partial (single-speed only) |
| Pulse table (multi-step program) | P                | NOT representable |
| Pulse table (bidirectional mode) | P (mode=bidirectional) | Partial |
| Filter table              | None (F_filt)       | NOT in Das Model |
| Vibrato (speed + depth + delay) | None             | NOT in Das Model |
| Portamento up/down        | None                | NOT in Das Model |
| Tone portamento           | None                | NOT in Das Model |
| Pattern commands          | None                | NOT in Das Model |
| Orderlist + transpose     | S (flattened)       | Full (after flattening) |
| Global tempo              | S.tempo             | Full     |
| Per-channel tempo         | None                | NOT in Das Model |
| Multi-song subtunes       | None                | NOT in Das Model |
| Keyoff / keyon events     | None                | NOT in Das Model |
| CIA timer / multispeed    | None                | NOT in Das Model |
| Osc3/Env3 modulation routing | None            | NOT in Das Model |
| Paddle (POTX/POTY) routing | None              | NOT in Das Model |
| Digi sample playback      | None                | NOT in Das Model |
| External audio input (EXT IN) | None            | NOT in Das Model |

**Das Model covers the core synthesizer layer (waveform + arpeggio + envelope +
hard restart) but does NOT cover the effects layer (filter, vibrato, portamento,
pattern commands) or the score logistics layer (per-channel tempo, multispeed,
multi-song).**

## 4. Proposed Extensions

The extensions below are ordered by importance to the GT2 pipeline (most songs
affected first).

### 4.1 Minor: F program — absolute note mode

**Gap:** Das Model F specifies `offsets : int8[]`, but GT2 right column $81–$DF
encodes absolute notes, not relative offsets.

**Proposed fix:** Extend F program steps to have a mode flag:

```
FStep = {
    mode   : enum  — 'offset' | 'absolute' | 'keep'
    value  : int8  — semitone offset (offset mode) or note index (absolute mode)
}
```

USF WaveTableStep already has `absolute_note` and `keep_freq` — this is purely a
spec update to das_model.md to match what USF already implements.

### 4.2 Significant: P program — multi-step pulse sequence

**Gap:** Das Model P is a single (speed, mode, min_hi, max_hi) tuple.  GT2 pulse
tables are step-programmable: set PW, modulate for N frames, loop.

**Proposed extension:** Replace P with a pulse program analogous to W:

```
P = {
    steps : PulseStep[]
    loop  : uint
}

PulseStep = {
    mode     : enum    — 'set' | 'modulate'
    value    : int8    — signed speed (modulate) or new PW high byte (set)
    low_byte : uint8   — PW low byte (set mode only)
    duration : uint8   — frame count (modulate mode only)
}
```

This matches GT2's pulse table layout exactly and is fully backward-compatible with
the current USF PulseTableStep dataclass.  Das Model P would evolve from a tuple to
a program.

The universal engine would execute the pulse program identically to how it executes
the wave program: advance step each frame, loop when exhausted.

### 4.3 Major: Filter program — new F_filt component

**Gap:** Das Model has no filter component.  GT2 filter tables control cutoff,
resonance, routing, and filter mode.

**Proposed new component:**

```
Instrument.F_filt = FilterProgram | None

FilterProgram = {
    steps : FilterStep[]
    loop  : uint
}

FilterStep = {
    type     : enum    — 'cutoff' | 'modulate' | 'params'
    value    : uint8   — cutoff value (cutoff) | signed speed (modulate) | res<<4|routing (params)
    duration : uint8   — frame count (modulate only)
    cutoff_low : uint8 — low 3 bits of cutoff ($D415 bits 0-2)
}
```

The engine would execute F_filt each frame in the same way as W and P.  When
`F_filt is None`, filter registers are not touched (current Das Model behaviour).

This matches USF's existing `Instrument.filter_ptr` + `Song.shared_filter_table`.
Das Model would grow from 4 components (W, F, P, E) to 5 (W, F, P, E, F_filt).

Note: filter is a **global resource** — all three voices share one filter.  The
engine must handle voice priority when multiple instruments request filter control
simultaneously.  GT2 resolves this by letting the last-executing voice win.

### 4.4 Major: Vibrato — extend F or add V component

**Gap:** Das Model F is a static note-offset sequence.  GT2 vibrato is a sinusoidal
pitch modulation computed dynamically (speed, depth, built-in sine table, delay).

Two options:

**Option A — encode vibrato in F as a pre-computed offset table.**
Generate the sine wave as a sequence of F offsets at extraction time.  Works for
constant vibrato, but fails for note-independent vibrato (GT2 speed table bit 7),
which changes speed based on current note pitch.

**Option B — add a Vibrato sub-spec to E or I:**

```
Instrument.vibrato = VibratoSpec | None

VibratoSpec = {
    speed_idx  : uint8   — speed table entry index
    delay      : uint8   — frames before onset
    logarithmic : bool   — True = note-independent (speed scales with pitch)
}
```

The engine would apply vibrato on top of the F-computed frequency.  This is how
USF's `Instrument.vib_speed_idx` + `vib_delay` work today.

**Recommendation:** Option B.  Option A breaks note-independent vibrato and would
generate enormous F tables for long-looping instruments.

### 4.5 Major: Portamento — extend S or add glide spec

**Gap:** GT2 portamento (commands $01/$02/$03) requires continuous pitch sliding
between note events.  Das Model S has no glide concept.

**Proposed extension to NoteEvent:**

```
NoteEvent.glide = GlideSpec | None

GlideSpec = {
    mode      : enum   — 'up' | 'down' | 'tone'
    speed_idx : uint8  — speed table entry index
}
```

The engine would apply the glide on intermediate frames between note events.
Tone portamento ('tone' mode) glides toward the target note's frequency and stops.

### 4.6 Minor: Score-level extensions

These are logistics rather than sound-shaping:

| Feature             | Proposed Das Model S extension |
|---------------------|-------------------------------|
| Per-channel tempo   | `Voice.tempo_override : uint8 | None` |
| CIA multispeed      | `Score.cia_multiplier : uint8` (0=VBI, 2–8=CIA) |
| Multi-song subtunes | `Score[]` (array of scores sharing same T and I) |
| Keyoff / keyon      | NoteEvent.type already in USF ('off', 'on') — add to Das Model spec |

## 5. Could Das Model REPLACE the Current Pipeline?

**Short answer: Das Model is the right long-term target, but NOT a drop-in
replacement today.**

The current GT2 pipeline (gt2_to_usf → usf_to_sid → codegen_v2) achieves 4,968
Grade A songs precisely because:
1. USF is a richer format than Das Model (filter tables, vibrato params, pattern
   commands, multi-song, etc. — all the Section 4 gaps)
2. codegen_v2 implements GT2 player semantics in detail (ADSR write order, hard
   restart timing, ghost registers, pulse ASL doubling, etc.)

Das Model + universal engine as currently specified would be Grade A on songs that
use only wave table arpeggio + hard restart + linear pulse modulation — a subset of
GT2's feature space.

**Complement path (recommended):**
1. Implement Sections 4.1–4.2 (F absolute notes, multi-step P) — these are spec
   clarifications matching existing USF fields.
2. Implement Section 4.3 (filter program F_filt) — this eliminates the biggest gap.
3. Implement Section 4.4 (vibrato) — next largest gap.
4. At that point Das Model is semantically equivalent to GT2+USF and the universal
   engine can replace codegen_v2 for GT2.

**Replace path risk:** Rewriting codegen_v2 into a Das Model engine before the gaps
are filled would immediately regress the 4,968 Grade A songs.  Extend the spec
first, verify parity song-by-song, then replace.

## 6. Relationship to USF

USF (`usf/format.py`) is currently the *implementation* of Das Model's ideas, but
extended with GT2-specific fields.  Das Model is the *formal specification* that USF
is converging toward.

The mismatch today:
- USF has `FilterTableStep`, `SpeedTableEntry`, `ModulationRoute`, `PaddleRoute` —
  none of these appear in Das Model.
- Das Model has clean W/F/P/E programs — USF splits W into wave_table (per-instrument)
  vs shared_wave_table (binary-level shared), which is a GT2 implementation detail.

A clean Das Model implementation would have USF Song as the score (S), USF Instrument
(with extended W, F, P, E, F_filt, Vibrato) as the instrument (I), and the freq
table as T.  The GT2-specific shared-table indirection would be hidden inside the
decompiler, not exposed in the model.

The proposed extensions in Section 4 close the gap without breaking the existing
pipeline.  Each extension adds a new field to Das Model's formal spec; USF already
has the corresponding data structures in most cases.
