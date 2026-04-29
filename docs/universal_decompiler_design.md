# Universal SID Decompiler — Design Specification

**Date:** 2026-04-29  
**Status:** Design (not yet implemented)

## 1. Goal

Extract Das Model components (T, I, S) from ANY SID player engine by observing its
register output rather than parsing its binary. This generalizes the existing
`regtrace_to_usf.py` — which does a similar job but with several structural
gaps — into a principled, stage-gated algorithm.

The output is a USF `Song` object suitable for the V2 player pipeline.

## 2. What Already Exists

| Tool | What it does | Gaps |
|------|-------------|------|
| `src/converters/regtrace_to_usf.py` | Gate-based event extraction, tempo detection, arpeggio collapse, wave table inference, pulse modulation detection | No pattern dedup, no loop detection, no voice-3-as-modulator, no digi, no filter table |
| `src/effect_detect.py` | Per-note DFT/differencing effect classifiers (vibrato, PWM, portamento, arpeggio) | Not wired into the USF pipeline |
| `src/formal/taint_tracker.py` | 6502 execution with memory read tracking to locate data tables | Only extracts freq table, not called by regtrace path |

The universal decompiler described here is a re-architecture that:
1. Promotes each detection stage to a first-class pipeline step
2. Adds pattern-finding and loop detection (currently missing)
3. Makes the result unambiguous by quantifying confidence at each step
4. Documents the theoretical limits clearly

---

## 3. Theoretical Limits

Before the algorithm: what CAN be recovered from a register trace, and what CANNOT?

### 3.1 Recoverable (always or with high confidence)

- **Frequency table T**: The set of all freq16 values written to SID is a superset of T.
  The exact table is recoverable if we also scan the SID binary (taint tracking locates
  the region, then we read the bytes directly). From the trace alone we get all PLAYED
  entries — unplayed notes are invisible.

- **Envelope (E)**: AD and SR bytes are written directly to $D405/$D406. They are fully
  observable from the trace. Gate timing (gate_off_delta) is observable from the gap
  between waveform-on and gate-off frames within a note.

- **Note durations (S.duration)**: Observable from gate-on to gate-on intervals, divided
  by tempo. Quantization error is at most ±1 tick for well-detected tempo.

- **Base note pitch (S.note)**: The settled freq_hi during a note maps to a note index
  with ~2 cents error using the PAL table (or better if the binary freq table is found).

- **Waveform sequence (W)**: The per-frame ctrl register is fully observable. The wave
  program can be reconstructed by finding the repeating pattern of ctrl values within
  each note.

- **Pulse width modulation (P)**: PW changes are fully observable. Speed and direction
  reversals are detectable by differencing.

### 3.2 Partially Recoverable (with ambiguity)

- **Tempo**: Recoverable when note durations cluster at integer multiples of a base unit.
  Ambiguous when a song uses only one duration (can't distinguish tempo from duration).
  Ambiguous for CIA-multispeed songs (the VBI snapshot misses intermediate writes).

- **Pattern boundaries**: Recoverable only when the note sequence repeats exactly.
  Slight transpositions or one-shot patterns that never repeat cannot be deduped.

- **Instrument identity**: Two physically different instruments that produce the same
  (AD, SR, waveform) output are indistinguishable from the trace. Only the binary
  parser can separate them.

- **Freq table T**: Entries for unplayed notes are invisible. Custom tables differing
  only at unplayed notes are indistinguishable from PAL.

- **Voice-3-as-modulator**: Observable as "voice 3 never gates but changes freq
  synchronously with filter/PW changes on other voices." Confidence depends on
  correlation strength.

### 3.3 Not Recoverable

- **Source format**: Cannot determine GT2 vs Hubbard vs DMC from the trace.

- **Hard restart method**: Gate vs test-bit HR both produce the same audible output.
  Test bit produces a brief silent frame visible in the trace, but the choice of method
  does not affect reconstructed audio.

- **Exact CIA timer frequency** for multispeed songs: The VBI-sampled trace misses the
  intra-frame writes. The player ran N times per VBI but we see only the last state.
  CIAspeed is detectable (note intervals are multiples of 1/N frame) but not perfectly
  quantizable without cycle-level writelog data.

- **Pattern loop points in the original**: We can detect that the same note sequence
  repeats, but we cannot tell whether the original had `REPEAT PATTERN 3` vs
  `COPY PATTERN 3 AS PATTERNS 3,6,9`.

- **Loopback position in the orderlist**: We can detect the song restart (the note
  sequence repeats from frame K), but we cannot distinguish "loop from pattern 0" vs
  "loop from pattern 2" unless the note data between them is unique.

---

## 4. Pipeline Overview

```
SID file
  │
  ├─► [STEP 0] Binary scan + taint tracking
  │     → T: custom freq table (if found), engine hint
  │
  ├─► [STEP 1] Dump register trace
  │     → 25-register frames at 50 fps (or writelog for cycle-level)
  │
  ├─► [STEP 2] Pre-classify frames
  │     → per-frame: gate state, waveform type, is_audible, is_test, freq16, note_idx
  │
  ├─► [STEP 3] Detect tempo
  │     → tempo (frames/tick), confidence, multispeed flag
  │
  ├─► [STEP 4] Detect voice role
  │     → per-voice: melodic | drum | modulator | silent
  │
  ├─► [STEP 5] Extract note events (per voice)
  │     → gate-boundary segmentation, vibrato filter, legato detection
  │
  ├─► [STEP 6] Classify per-note effects
  │     → arpeggio | portamento | vibrato | PWM | drum-slide | filter-mod
  │
  ├─► [STEP 7] Build instrument catalogue (I)
  │     → cluster by (AD, SR, wave_program, pulse_program), assign inst_id
  │
  ├─► [STEP 8] Quantize events to ticks
  │     → note: (note_idx, duration_ticks, inst_id)
  │     → off: (duration_ticks)
  │
  ├─► [STEP 9] Find patterns (repeating event sequences)
  │     → dedup identical sequences → pattern pool
  │
  ├─► [STEP 10] Find loop point (song structure S)
  │     → orderlist per voice, loop-back frame
  │
  └─► [STEP 11] Assemble USF Song
        → Song(T, I, S, tempo, patterns, orderlists)
```

---

## 5. Step-by-Step Algorithm

### Step 0: Binary Scan + Taint Tracking

**Goal:** Extract T (freq table) before running the trace. This avoids note
identification errors for engines with non-PAL tuning.

**Algorithm:**

1. Scan binary for byte patterns matching FREQ_HI_PAL with stride 1 or 2.
   Require 24+ consecutive matches within 2-byte tolerance. This is the existing
   `_try_extract_freq_table()` in `regtrace_to_usf.py`.

2. If binary scan fails, run 20-frame taint-tracked execution using `taint_tracker.py`.
   Find memory regions whose reads feed $D400/$D401. Extract bytes from that region.

3. If both fail, default to PAL table. Flag T as "inferred" in metadata.

**Confidence:** HIGH for binary scan with ≥60 matches. MEDIUM for taint tracking.
LOW for PAL default (acceptable for GT2; risky for Hubbard, JCH).

**Output:** `T: list[int]` (96 16-bit freq values), `T_confidence: str`

---

### Step 1: Dump Register Trace

**Goal:** Capture per-frame SID register state.

**Algorithm:**

Run `siddump --duration N` on the SID file. Parse the 25-column CSV output.
Each frame is a list of 25 uint8 values indexed as defined in `regtrace_to_usf.py`
(VOICE_OFFSETS, IDX_FREQ_LO, etc.).

**Duration choice:**
- Default: 60 seconds (3000 frames at 50 fps)
- For loop detection: capture at least 3 full song cycles. If unknown, use 120 seconds.
- For multispeed detection: also run `siddump --writelog` to get cycle-level timing.

**Output:** `frames: list[list[int]]` (N × 25)

---

### Step 2: Pre-classify Frames

**Goal:** Per-frame derived fields needed by all later steps.

**For each frame, for each voice v:**

```
freq_hi  = frame[VOICE_OFFSETS[v] + IDX_FREQ_HI]
freq_lo  = frame[VOICE_OFFSETS[v] + IDX_FREQ_LO]
freq16   = (freq_hi << 8) | freq_lo
ctrl     = frame[VOICE_OFFSETS[v] + IDX_CTRL]
gate     = bool(ctrl & 0x01)
waveform = ctrl & 0xF0
is_test  = (ctrl & 0x08) != 0 and waveform == 0
is_audible = waveform in AUDIBLE_WAVEFORMS and not is_test
note_idx = nearest_note(freq16, T)
ad       = frame[VOICE_OFFSETS[v] + IDX_AD]
sr       = frame[VOICE_OFFSETS[v] + IDX_SR]
pw       = (frame[...IDX_PW_HI] << 8) | frame[...IDX_PW_LO]
```

**Output:** `classified: list[list[FrameState]]` (N × 3)

---

### Step 3: Detect Tempo

**Goal:** Find the fundamental period (frames/tick) that explains all note durations.

This is the most critical step — an error here cascades into wrong duration
quantization for every note in the song.

**Algorithm (three-pass):**

**Pass A — gate-on autocorrelation (existing approach, extended):**

For each voice, record the frame index of each gate-on edge. Compute all pairwise
intervals between consecutive gate-on edges. Collect all intervals across all voices.

Score each candidate tempo T_cand in range [2, 64]:
```
score(T_cand) = Σ_intervals [ weight(interval) × match(interval, T_cand) ]
```
where:
- `match(d, T) = 1.0` if `d % T == 0`, else `0.5` if `|d % T| <= 1` (±1 tolerance), else `0`
- `weight(d) = 1 + d // T_cand` (longer durations carry more weight)

**Pass B — GCD heuristic:**
Compute `GCD(all_intervals)`. If GCD divides ≥ 80% of intervals, prefer GCD over
the best autocorrelation score.

**Pass C — multispeed detection:**
If the best tempo T from Pass A/B has many intervals at T/2 or T/3, test whether
those intervals are CIA-multispeed ticks rather than note grid ticks:
- CIA songs: all intervals are exact multiples of T (the outer VBI tempo)
- Normal songs: intervals cluster at T/2, T/3 etc. (triplets, halftime)

Multispeed flag fires when: T_best >= 12 AND many intervals at T_best/N for N in {2,3,4,6,8,12}.
In that case, report T = T_best as the VBI tempo and set `multispeed = True`.

**Output:** `tempo: int`, `tempo_confidence: float`, `multispeed: bool`

**Edge cases:**
- Percussion-only voice: no pitched notes, gate-on intervals unreliable. Use other voices.
- Constant-frequency voice (drone): only one gate-on. Exclude from tempo detection.
- Silence at start: don't count the init period.

---

### Step 4: Detect Voice Role

**Goal:** Classify each voice as: melodic | drum | modulator | silent.

**Rules (applied in order, first match wins):**

1. **silent**: gate is never set for this voice across all frames.

2. **modulator**: voice produces no audible sound (gate never on, or always filtered out)
   but its frequency changes are correlated with filter cutoff, pulse width, or volume
   on other voices. Detectable via cross-correlation of freq changes and filter/PW writes.

   Detection: compute `corr(freq_diff(v3), filter_diff)` and `corr(freq_diff(v3), pw_diff)`.
   If either > 0.4, classify as modulator.

3. **drum**: voice uses noise waveform ($80) for ≥ 50% of gated frames. OR the voice
   has very short notes (≤ 3 frames each) with no sustained tones.

4. **melodic**: default.

**Output:** `voice_role: list[str]` (3 elements)

---

### Step 5: Extract Note Events

**Goal:** Partition each voice's frame sequence into note events and rests.

This is the core extraction step. The algorithm must handle:
- Arpeggios (freq cycles through several values per tick — NOT separate notes)
- Vibrato (slow freq modulation — NOT separate notes)
- Legato (freq change while gated — IS a new note)
- Hard restart gap (short gate-off before each note — IS a rest, but short)

**Algorithm:**

For each voice v:

1. **Gate-boundary detection:** Find all gate-rising edges (gate 0→1 while is_audible).
   Each rising edge starts a candidate note event.

2. **Within-note freq change classification:**
   When freq_hi changes while gated, run the classifier:

   a. **Arpeggio check:** Does the original freq_hi return within `tempo` frames?
      If YES → arpeggio (wave table cycling). Do NOT split into new note.

   b. **Vibrato check:** Is the magnitude ≤ 2 semitones AND does it return to original
      within `tempo` frames? If YES → vibrato. Do NOT split.

   c. **Legato check:** Does the new freq_hi SUSTAIN for ≥ `max(3, tempo//2)` consecutive
      frames? If YES → split into new note at this frame.

   d. Otherwise → ignore (transient, wave table one-shot, etc.).

3. **Note settling:** After segmenting, determine each note's "settled" freq_hi as the
   mode (most common) freq_hi during the note's audible frames. Use this for note_idx
   mapping. The first 1-2 frames may be transient (first-wave waveform, wave table init).

4. **Absorb init-chain notes:** Short note chains (≤ 2 frames each) immediately preceding
   a longer note are absorbed into the longer note. Their waveforms are recorded as
   first_wave attributes. (Existing behavior in `regtrace_to_usf.py`.)

5. **Gate-off events:** Between notes, record the gap as a rest event with duration =
   number of silent frames.

**Output per voice:** `events: list[dict]` with fields:
```
type: 'note' | 'off'
frame: int           # absolute start frame
duration: int        # frames
note: int            # note index (for 'note' events)
ad, sr: int          # ADSR bytes
waveform: int        # settled waveform byte (upper nibble)
pw: int              # initial pulse width
first_wave: int      # first-frame waveform if different (-1 if same)
```

---

### Step 6: Classify Per-Note Effects

**Goal:** For each note event, identify which USF table features are needed:
wave program (W), freq program (F — arpeggio offsets), pulse program (P), or none.

**Run the effect detectors from `effect_detect.py` on each note segment:**

**6a. Arpeggio detection (-> F program):**
- Signal: freq cycles through 2–4 discrete values per tick
- Detector: `effect_detect.detect_arpeggio()` (DFT on note-mapped freq)
- Decision: if arpeggio period P divides `tempo` evenly AND there are ≥ 6 frames
  of evidence → build an F program with note offsets `[0, +d1, +d2, ...]` looping at P

**6b. Vibrato detection (-> speed_table):**
- Signal: freq oscillates slowly (2–10 Hz) around center
- Detector: `effect_detect.detect_vibrato()` (DFT with peak between 2–12 Hz)
- Decision: if confidence ≥ 0.5 AND note is ≥ 20 frames → assign speed_table entry
  with depth = peak-to-peak semitones, rate = peak_hz converted to GT2 speed byte

**6c. PWM detection (-> P program):**
- Signal: PW changes linearly or with reversals
- Detector: `effect_detect.detect_pwm_direct()` and `detect_pwm_sweep()`
- Decision: if direct speed consistent ≥ 60% → linear P program. If reversals ≥ 1
  per 20 frames → bidirectional P program.

**6d. Portamento detection (-> freq_slide in wave table):**
- Signal: freq_hi decreases by exactly 1 per frame (drum slide) or constant delta (portamento)
- Detector: `effect_detect.detect_drum_freq_slide()`, `detect_portamento()`
- Decision: for drum slides → record freq_slide = -1 in wave table step. For melodic
  portamento → record freq_slide in wave table step.

**6e. Waveform sequence detection (-> W program):**
- Collect per-frame ctrl bytes for the note's first 8 frames.
- Find the repeating period (1–4 steps) using the existing `_build_wave_table_from_patterns()`.
- If a clear period is found (≥ 75% match across ≥ 3 notes of same instrument) → build W program.

**Output per note:** `effects: dict` with keys `arpeggio`, `vibrato`, `pwm`, `portamento`,
`wave_seq`, each containing the effect parameters or None.

---

### Step 7: Build Instrument Catalogue (I)

**Goal:** Cluster note events into a minimal set of instruments. Each instrument is
a unique (E, W, F, P) tuple — identical programs can share one instrument.

**Algorithm:**

**Clustering key:**
```
key = (ad, sr, settled_waveform, wave_program_hash, arpeggio_hash, pwm_mode)
```

Collect the key for every note event. Each unique key → one instrument entry.

**Instrument construction:**

For each unique key, collect all note events with that key across all voices.

1. **E (Envelope):**
   - `ad` = key.ad, `sr` = key.sr
   - `gate_off_delta`: find modal gate-off frame offset within notes of this instrument.
     Gate-off frame = first frame within the note where ctrl bit 0 goes 0.
     Offset from note END = note_duration - gate_off_frame.
     If most notes have gate_off_delta = 0 (gate off at note end) → 0.
   - `adsr_zero_delta`: look for frames where AD = 00 and SR = 00 within the note.
     If found consistently at a fixed offset from note end → set that offset.

2. **W (Wave Program):**
   - Use the wave sequence detected in Step 6e for this instrument.
   - If no clear sequence: single-step [waveform | 0x01] looping at 0.
   - If first_wave present: [first_wave | 0x01, waveform | 0x01, loop→1].

3. **F (Freq Program):**
   - Use arpeggio offsets from Step 6a.
   - If no arpeggio: single-step [0] looping at 0.
   - If portamento/drum-slide: encode as freq_slide in wave table step (USF WaveTableStep.freq_slide).

4. **P (Pulse Program):**
   - Use PWM parameters from Step 6c.
   - If no modulation: P.mode = 'none', P.init_pw = modal PW value.
   - If linear: P.mode = 'linear', P.speed = detected speed, P.init_pw = initial PW.
   - If bidirectional: P.mode = 'bidirectional', boundaries from observed PW range.

**Instrument dedup:**
If two keys produce identical (E, W, F, P), merge them into one instrument ID.

**Output:** `instruments: list[Instrument]`, `inst_map: dict[key → inst_id]`

---

### Step 8: Quantize Events to Ticks

**Goal:** Convert frame-based durations to tick-based durations for the Score.

```
ticks = max(1, round(duration_frames / tempo))
```

**Rounding policy:**
- round() is correct for most cases.
- If the remainder is ≥ tempo - 1 (i.e., 1 frame short of the next tick), round up.
  This handles the common case where the gate-on frame is counted differently.

**Minimum durations:**
- Note: minimum 1 tick.
- Rest (off): minimum 1 tick. Rests shorter than 1 tick are dropped (absorbed into the
  adjacent note's gate timing).

**Output:** `quantized_events: list[dict]` with `ticks: int` added.

---

### Step 9: Find Patterns (Repeating Event Sequences)

**Goal:** Dedup identical note sequences across the song to build a compact pattern pool.

This step is MISSING from the current `regtrace_to_usf.py` — it emits one giant
pattern per voice with no reuse. Good pattern detection reduces token count by 30–60%
for looping songs.

**Algorithm:**

**9a. Align voices to tick grid:**
Convert each voice's quantized event list to a sequence of (note_idx, inst_id, ticks)
triples. Rests become (REST_SENTINEL, 0, ticks).

**9b. Find the pattern period:**
A song typically repeats every P ticks (the "phrase length"). Detect P by finding the
smallest P such that the note sequence at position 0 matches the sequence at position P
with Levenshtein similarity ≥ 90%.

P candidates: try P = 16, 32, 48, 64, 128 ticks (common phrase lengths).

If no P found: try autocorrelation on the note index sequence (treating notes as a
signal) to find the period.

**9c. Segment into patterns:**
Given phrase length P, split the event stream into contiguous phrases of P ticks each.
Each phrase is a candidate pattern.

**9d. Dedup patterns:**
Hash each pattern (as a tuple of events). Identical hashes → same pattern ID.
Near-identical patterns (Levenshtein edit distance ≤ 2) → same pattern ID if audio
effect of the difference is inaudible (single note_jitter, not note_wrong).

**9e. Build orderlist:**
Each voice's orderlist is the sequence of (pattern_id, transpose) pairs.
Transpose detection: if pattern A and pattern B are identical except all notes are
shifted by +k semitones, emit (pattern_A_id, transpose=+k) instead of a new pattern.

**Output:** `patterns: list[Pattern]`, `orderlists: list[list[tuple]]`

**Fallback:** If no repeating structure is found (medley, one-shot piece), emit one
pattern per voice with all events. This is the current behavior.

---

### Step 10: Find Loop Point

**Goal:** Identify where the song loops back to for infinite playback.

**Algorithm:**

1. Capture 3x the estimated song length (or 120s if unknown).

2. Find the frame L where the note sequence on all three voices simultaneously repeats:
   - The note events starting at frame L match those starting at frame 0 (or some
     earlier restart point R).
   - L is detected by looking for frame-level exact match of (freq_hi, ctrl, ad, sr)
     across all 3 voices simultaneously for ≥ 32 consecutive frames.

3. The loop point in the orderlist is the pattern index at frame L.

4. If no loop found within the capture duration: set loop = end (one-shot).

**Output:** `orderlist_restart: list[int]` (index into orderlist where each voice loops back)

**Corner case:** Songs that loop mid-pattern. If the loop starts inside a pattern rather
than at a pattern boundary, split the pattern at the loop boundary.

---

### Step 11: Assemble USF Song

Combine all extracted components into a `usf.format.Song` object:

```python
Song(
    title    = metadata['title'],
    author   = metadata['author'],
    sid_model = metadata['sid_model'],
    clock    = metadata.get('clock', 'PAL'),
    tempo    = tempo,
    instruments = instruments,
    patterns = patterns,
    orderlists = orderlists,
    orderlist_restart = orderlist_restart,
    nowavedelay = True,           # regtrace path always uses nowavedelay
    shared_pulse_table = shared_pulse_table,
    freq_lo  = custom_freq_lo if T_confidence != 'inferred' else None,
    freq_hi  = custom_freq_hi if T_confidence != 'inferred' else None,
)
```

Set `voice3_as_modulator = True` if voice 3 was classified as modulator in Step 4.

---

## 6. Detecting Note Boundaries Reliably

This is the hardest problem in the pipeline. The existing code gets most cases right
but has known failure modes:

**Reliable case:** Gate 0→1 transition. The rising edge unambiguously starts a new note.
The existing code handles this correctly.

**Ambiguous case: legato.** The gate stays HIGH while freq changes. How do we know if
it's a new note vs vibrato vs arpeggio?

Decision tree (apply in order):
1. Does freq return within `tempo` frames? → arpeggio or vibrato (NOT new note)
2. Does the new freq persist for ≥ `tempo//2` frames? → legato new note
3. Is the freq change ≤ 2 semitones? → vibrato (NOT new note, even if it doesn't return)
4. Otherwise → ignore (transient)

**Ambiguous case: hard restart.** Many players briefly gate off (1-2 frames) between
notes to trigger ADSR. This gate-off is NOT a musical rest.

Detection: if a gate-off gap is ≤ 4 frames AND the next note has the same instrument
(same AD, SR, waveform), classify as HR gap (record as gate_timer in instrument) rather
than musical rest.

**Ambiguous case: multispeed.** With CIA multispeed, the VBI trace only captures the
last register state per frame. Note boundaries within a frame are invisible.

Partial mitigation: when `multispeed = True`, the effective frame rate is `fps * N` where
N is the CIA multiplier. Use `siddump --writelog` to get cycle-level data and reconstruct
the intra-frame writes.

---

## 7. Separating Melody from Drums

**Primary discriminant:** waveform type.
- Noise ($80) dominant across multiple notes → drum voice.
- Pitched waveform (saw $20, triangle $10, pulse $40) → melodic.

**Secondary discriminant:** note duration.
- Very short notes (≤ 3 frames) with no sustained portion → percussion (drum hits).
- Long sustained notes → melodic.

**Tertiary discriminant:** frequency content.
- Melodic voices: freq_hi maps cleanly to PAL note table (≤ 3 cents error).
- Drum voices: freq_hi is arbitrary (used for timbre control, not pitch).

**Implementation:** computed in Step 4 (voice role) and Step 6 (effect classification).
Drum voices get noise waveform instruments; frequency slides become wave table freq_slide
fields rather than note pitch changes.

**Edge case:** a melodic instrument that uses noise for ONE frame (drum burst / attack
click). This is handled by first_wave detection — the noise frame is the first_wave and
the sustained wave is the settled waveform.

---

## 8. Detecting Vibrato

**Definition:** freq oscillates ±N semitones around a stable center pitch at 2–10 Hz.

**DFT approach (from `effect_detect.py`):**
1. Extract freq values during the note as a time series.
2. Compute real DFT.
3. Find dominant peak between 2–12 Hz.
4. If peak magnitude / total energy ≥ 0.15 AND note length ≥ 10 frames → vibrato.

**Parameters to extract:**
- `depth_semitones`: (max_freq - min_freq) converted to semitones
- `rate_hz`: peak frequency from DFT
- `delay_frames`: how many frames before vibrato begins (common: 8–16 frames after note start)

**USF encoding:** assign a SpeedTableEntry with the appropriate speed byte.
The GT2 speed table entry format encodes depth and speed as separate bytes.
Mapping: `rate_hz → speed_byte` via the V2 player's speed table LUT (see `codegen_v2.py`).

**Vs. arpeggio discrimination:**
Arpeggio: freq snaps between ≤ 4 discrete values (low discreteness ratio).
Vibrato: freq varies continuously (high discreteness ratio, sinusoidal spectrum peak).
The `discreteness()` function in `effect_detect.py` computes the ratio.

---

## 9. Detecting Pulse Width Modulation

**Direct PWM:** PW_lo increments by a constant each frame.
- Detection: differencing `pw_lo` sequence → constant_delta ≥ 0.7
- Parameters: speed (signed byte), initial PW
- USF encoding: `WaveTableStep.freq_slide` is NOT for PW. Use `PulseTableStep` with speed.

**Bidirectional PWM (triangle wave LFO):**
- Detection: PW changes with direction reversals, DFT peak ≥ 0.1 power ratio
- Parameters: speed, min_hi, max_hi boundaries
- USF encoding: bidirectional pulse table with loop-back to the speed step

**Persistence:** PW state persists across notes on the same voice. The instrument's
`init_pw` is loaded only once at song start (or at instrument change). The pulse program
continues running from wherever it left off. This matches the GT2 player behavior.

---

## 10. Detecting the Tempo

The existing `detect_tempo_from_frames()` handles standard cases well. Known gaps:

**Gap 1: CIA multispeed.** Tempo >= 12 indicates CIA timer usage. These songs run
the play routine 2–16x per VBI. The note intervals in the trace are still multiples
of the outer VBI tempo, so detection still works, but the quantized durations will
be wrong (off by the CIA multiplier). Fix: detect multispeed and divide tempo by N.

**Gap 2: Funktempo (alternating speeds).** Some GT2 songs alternate between two tempos
(e.g., 6 and 12). The GCD of all intervals will be 6, but some durations are 12
and some are 6. Detect by checking if intervals cluster in two groups at ratio 2:1.
USF encodes this as a speed_table funktempo entry.

**Gap 3: Silence at start.** Don't include the init period (first K silent frames)
in tempo detection. The existing code uses a `3 <= d <= 64` filter on intervals, which
implicitly handles this.

**Scoring priority:** GCD of intervals → autocorrelation score → divisibility score.
When multiple tempos score close, prefer higher tempo (more granular quantization).

---

## 11. Detecting Pattern Boundaries

**Goal:** Find the smallest repeating unit of the score so identical phrases can be
reused as patterns.

**Algorithm:**

The note event sequence (note_idx, inst_id, duration_ticks) for each voice is treated
as a string. We want to find the shortest prefix P such that the remainder of the string
is (approximately) a concatenation of copies of P.

**Step 1: Candidate phrase lengths.**
Try phrase lengths of 8, 16, 32, 48, 64 ticks (common in GT2 and Hubbard).
For each candidate, align the note stream to phrase boundaries and count how many
phrases are identical to phrase 0.

**Step 2: Score candidates.**
```
score(phrase_len) = (identical_phrases / total_phrases) * phrase_len
```
Higher phrase length AND higher identical fraction → better score.

**Step 3: Cross-voice consistency.**
The phrase length must be consistent across all active voices. If voice 1 has phrase
length 32 and voice 2 has 64, use 32 (the shorter one governs).

**Step 4: Transpose variants.**
Two phrases are "transpose-equivalent" if all notes differ by the same constant k.
Detect by computing the note difference sequence between pairs and checking if it is
constant.

**When pattern detection fails (confidence < 0.6):**
Fall back to a single long pattern per voice. This is correct but not compact.
Log a warning so the caller can decide whether to accept lower quality output.

---

## 12. Theoretical Limit Summary

| Das Model Component | Recoverability | Confidence |
|---------------------|---------------|-----------|
| T: freq table entries (played notes) | FULL | HIGH (binary scan) / MEDIUM (PAL assumption) |
| T: freq table entries (unplayed notes) | NONE | N/A |
| E: AD, SR bytes | FULL | HIGH |
| E: gate_off_delta | FULL | MEDIUM (requires consistent note lengths) |
| E: adsr_zero_delta | FULL | MEDIUM |
| W: wave program | FULL | HIGH (ctrl register observed directly) |
| F: arpeggio offsets | FULL | HIGH (DFT on freq) |
| F: vibrato | FULL | MEDIUM (DFT confidence required) |
| F: portamento | FULL | MEDIUM |
| P: PWM speed | FULL | HIGH (direct differencing) |
| P: PWM boundaries | FULL | MEDIUM (from observed PW range) |
| S: note pitches | FULL | HIGH |
| S: note durations | FULL | HIGH (±1 tick quantization error) |
| S: patterns | PARTIAL | MEDIUM (needs repeating structure) |
| S: orderlist | PARTIAL | MEDIUM (needs 3x song length capture) |
| S: loop point | PARTIAL | MEDIUM |
| Instrument identity | PARTIAL | MEDIUM (clustering by observable output) |
| Engine type | NONE | N/A |
| HR method | NONE | N/A |
| CIA timer speed | PARTIAL | LOW without writelog |

**Fundamental limit:** The decompiler operates on the PROJECTION of the player's state
onto SID register space. State variables that don't affect register output are invisible.
The recovered model is equivalent-by-output but not necessarily isomorphic-to-original.
This is sufficient for USF → rebuilt SID → audio comparison purposes.

---

## 13. Implementation Plan

The algorithm above refactors `regtrace_to_usf.py` into a staged pipeline. The stages
map to Python functions as follows:

| Stage | New function | Status |
|-------|-------------|--------|
| Step 0 | `extract_freq_table_hybrid()` | Exists (binary scan); taint-tracking path to add |
| Step 1 | `run_siddump()` | Exists |
| Step 2 | `classify_frames()` | Inline in existing code; extract as function |
| Step 3 | `detect_tempo_v2()` | Exists (detect_tempo_from_frames); extend with GCD pass |
| Step 4 | `classify_voice_roles()` | NEW |
| Step 5 | `extract_note_events()` | Exists (extract_voice_events); already handles most cases |
| Step 6 | `classify_note_effects()` | Exists in effect_detect.py; wire into pipeline |
| Step 7 | `build_instruments_v2()` | Exists (build_instruments); extend with full E/W/F/P |
| Step 8 | `quantize_events()` | Exists |
| Step 9 | `find_patterns()` | NEW — biggest missing piece |
| Step 10 | `find_loop_point()` | NEW |
| Step 11 | `assemble_song()` | Exists (_regtrace_to_usf_inner) |

Priority order for implementation:
1. Step 9 (pattern finding) — highest impact on token count for ML training
2. Step 10 (loop detection) — required for looping playback
3. Step 4 (voice role classification) — improves drum/melody separation
4. Step 6 (wire effect_detect into pipeline) — improves instrument quality
5. Step 0 (taint tracking path) — improves T accuracy for Hubbard/JCH

---

## 14. Test Cases

| Song | Engine | Expected challenge |
|------|--------|--------------------|
| Commando (Hubbard) | Hubbard | Custom freq table, arpeggio, drum slides |
| International Karate (Hubbard) | Hubbard | Multispeed (CIA), voice-3 modulator |
| Ocean Loader (Hubbard) | Hubbard | No patterns (medley structure), long rests |
| Thrust (C64) | GT2 | Clean GT2 — verify no regression vs static parser |
| Delta (Galway) | Galway | Custom engine, unique vibrato implementation |
| Monty on the Run (Hubbard) | Hubbard | Complex arpeggios, filter modulation |

Run `sid_compare.py` on each test case before and after any implementation to measure
improvement vs regression.
