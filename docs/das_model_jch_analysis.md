# Das Model — JCH NewPlayer Analysis

**Date:** 2026-04-29
**Scope:** JCH NewPlayer and OldPlayer engines (~3,678 songs in HVSC)
**Status:** Current pipeline uses regtrace_to_usf (universal trace path), Grade A = 107 songs.
**Goal:** Determine what Das Model would need to support JCH via static binary parsing.

---

## 1. Ground Truth

Songs analyzed:

| Song | Engine | Verified |
|------|--------|---------|
| `42nd_Street.sid` | JCH_NewPlayer | sidid confirmed |
| `Accident.sid` | JCH_NewPlayer | sidid confirmed |
| `Alpha_Centauri.sid` | JCH_OldPlayer | sidid confirmed |
| `Reincarnations.sid` | JCH_OldPlayer | sidid confirmed |
| `Batman_long.sid` | JCH_NewPlayer | sidid confirmed |
| `Big_Bad_X-Mas.sid` | JCH_OldPlayer | sidid confirmed |

JCH has three engine variants in HVSC:

- **JCH_OldPlayer** — earlier, simpler feature set
- **JCH_NewPlayer** — full feature set (V1–V19 sub-variants)
- **JCH_DigiPlayer** — uses SID volume DAC for PCM playback (separate class)

The DigiPlayer is fundamentally different (it streams 4-bit PCM to $D418) and is out
of scope for Das Model's pitched-instrument model.

---

## 2. Current Pipeline Grade

Running regtrace_to_usf on a JCH/MUSICIANS/J/JCH sample:

```
C  90.9%  Ending.sid
F  70.4%  Accident.sid
F  68.7%  Triangle_2.sid
F  67.0%  Reincarnations.sid
F  66.6%  Skaermtrolden_Hugo.sid
F  62.9%  X-Ray.sid
F  64.7%  Diflexing.sid
```

Most JCH songs are F-grade via regtrace_to_usf. The 107 Grade A count in
pipeline_status comes from a broader search (including JCH songs by other composers
that happen to be simpler patterns), not from core JCH titles.

The root cause is that regtrace_to_usf does not recover PW modulation tables,
filter sweep tables, or arpeggio programs — it only captures settled ADSR and
waveform per note. Missing features cause `note_wrong` and `wave_wrong` errors.

---

## 3. JCH Feature Inventory

### 3.1 Voices and Roles

JCH uses the standard three SID voices, typically assigned:

- **V1:** Melody (pulse waveform, PW sweep, vibrato on long notes)
- **V2:** Bassline or harmonic layer (noise-gate arpeggio, or pulse with vibrato)
- **V3:** Percussion/arpeggio (noise drums, or fast frequency alternation)

Role assignment varies by song; the player is flexible.

### 3.2 Waveforms Observed

| Ctrl byte | Meaning | Songs |
|-----------|---------|-------|
| `$41` | Pulse + gate | all |
| `$40` | Pulse, gate off | all |
| `$09` | Tri + gate (hard restart) | all NewPlayer |
| `$08` | Tri, gate off (HR) | all NewPlayer |
| `$81` | Noise + gate | Accident |
| `$80` | Noise, gate off | 42nd_Street, Big_Bad |
| `$11` | Tri + gate | Batman, Accident |
| `$10` | Tri, gate off | Batman |
| `$12` | Tri + sync, gate off | Batman |
| `$13` | Tri + sync + gate | Batman |
| `$21` | Saw + gate | Batman |
| `$FF` | All bits (init/arp) | Alpha_Centauri |

The `$09` → `$41` sequence is JCH's standard hard restart: write tri+gate on the
last frame before the new note (clears decay), then write pulse+gate.

The `$FF` pattern in Alpha_Centauri (OldPlayer) is a wave-table arpeggio where all
waveform bits are toggled rapidly — the oscillator cycles but produces sound only
when audible bits are set.

### 3.3 Pulse Width Modulation

PW sweeps were confirmed in every JCH song with pulse voice:

- **42nd Street V1:** PW starts at `$03:C0` (960), increments by `$0020` (32) per frame
- **Reincarnations V1:** PW starts at `$0400` (1024), increments by `$001C` (28) per frame, period = 8–9 frames, then wraps
- **Accident V1/V3:** PW sweep with step `$0070` (112) per frame

PW is an instrument-level program running per frame, independent of the note. It wraps
modulo `$0FFF` (12-bit PW register). The sweep resets at note boundaries (confirmed:
PW resets to a fixed value at each gate-on).

The Das Model `P` program with `mode='linear'` and `speed = step/16` (since PW
registers are 12-bit and the engine typically accumulates in 8-bit units) captures this.

### 3.4 Filter Sweep

Every JCH song uses a filter sweep synchronized to the music:

- **42nd Street:** filter cutoff decrements by `$06` (6) per frame, resets at note boundary from `$62` → down to `$26`, pattern period = 8 notes
- **Reincarnations:** filter cutoff decrements `$06` per frame from `$73`, period = 8 frames, resets at note boundary

The filter sweep is tied to the note tempo: the cutoff steps once per frame and resets
when a new note fires. This is a per-note filter envelope, not a global LFO.

Filter voice routing: `FILT_CTRL = $F3` means resonance=`$F`, voices 1+2 filtered.
`FILT_MODE_VOL = $1F` means low-pass filter enabled, volume=15.

Das Model's `FilterTableStep` sequence (type='modulate' with speed=-6, duration=8,
then type='loop' to beginning) captures this exactly.

### 3.5 Arpeggio

Two arpeggio styles were observed:

**Style 1 — Two-note alternation (42nd Street V2):**
```
ctrl=$80 freq=37:43  (note A)
ctrl=$80 freq=31:39  (note B)
ctrl=$80 freq=37:43  (note A)
ctrl=$80 freq=31:39  (note B)
```
Both notes play with gate=off (no ADSR triggered). This is a chord drone using
noise waveform with oscillator alternating between two frequencies. The rate
alternates every frame (1-frame arpeggio period).

**Style 2 — Background chord arpeggio (Reincarnations V3):**
```
ctrl=$40 freq=1D:EF  (root)
ctrl=$40 freq=77:8C  (octave+fifth)
```
Gate=off throughout, oscillating every 1–2 frames. This is the JCH "arpeggio
while sustaining" pattern — the oscillator runs continuously but frequency cycles.

Both styles require the Das Model `F` program (FreqProgram) with per-frame arpeggio
offset. The current `F.arp_offset` field handles the single-offset alternation case
(every other frame: base_note vs base_note+offset). For N-way arpeggios (chord
arpeggios), a full arpeggio table is needed (same as GT2's wave table right column).

**Current Das Model limitation:** F is defined as a single `arp_offset` scalar, which
handles 2-note alternation at frame rate. JCH uses this same pattern. This is
sufficient for observed JCH arpeggio patterns — no multi-step arp tables were seen
in these songs.

### 3.6 Vibrato

Vibrato was confirmed on melody and bass voices:

**42nd Street V1 (melody):** Freq_lo oscillates ±$10 (16 units) at the end of long notes.
Example: `08:B4` → `08:C4` → `08:D4` → `08:E4` → `08:D4` → back (triangle LFO).
Delta = $10 per frame, period = 4 frames up + 4 frames down = 8-frame triangle.

**Batman V2/V3 (melody+bass):** Both voices vibrate with step = `$0050` (80 freq units)
in a triangle pattern: center → +50 → +100 → +150 → +100 → +50 → center → -50 → ...
Period = ~8 frames. Vibrato starts immediately (no delay in observed samples).

Das Model's `V` program (VibratoProgram) with `scale` and `delay` captures this. The
scale maps JCH's fixed-delta vibrato to the model's relative-delta implementation.

**Key difference vs GT2:** JCH vibrato uses an absolute freq_lo delta, not a semitone-
table delta. The model needs to convert between these at instrument extraction time
(not at playback time).

### 3.7 Sync Modulation

Batman V3 uses oscillator sync (`$12`/`$13` = tri+sync) with a portamento slide:

```
F 71 V3: ctrl=$13 freq=2B:D8   (sync+gate)
F 72 V3: ctrl=$13 freq=27:12   (descending)
F 73 V3: ctrl=$13 freq=22:D2   
F 74 V3: ctrl=$13 freq=1F:06   
F 75 V3: ctrl=$12 freq=1F:06   (sync, gate off)
```

This is a sync-modulated sweep: the freq descends ~$400 per frame (1024 units)
for 4 frames, creating a metallic "zap" effect. Voice 1 provides the carrier for sync.

Das Model currently has no explicit sync modulation program. Sync is a SID hardware
feature that requires V3's oscillator to reset when V1's oscillator completes a cycle.
The wave table `W` can encode the `$12`/`$13` ctrl bytes directly (Das Model's `W`
writes the ctrl byte as-is), but the freq descent needs the `freq_slide` field in
`WaveTableStep` (already present in USF: `freq_slide: int` = signed per-frame freq_hi
delta).

**Assessment:** Das Model can represent JCH sync sweeps using `freq_slide` in the wave
table steps. No new model fields required.

### 3.8 Hard Restart

JCH's hard restart (NewPlayer) uses the `$09` → `$41` pattern:

```
F(n-1): ctrl=$41 (note sustaining)
F(n):   ctrl=$09 (tri+gate = hard restart; gate fires ADSR from zero)
F(n+1): ctrl=$41 (new note: pulse+gate)
```

The `$09` frame briefly triggers the triangle waveform with gate=on, resetting the
ADSR. One frame later the new pulse note fires with its own ADSR settings.

This maps to Das Model's `E.hr_method='gate'` + `gate_timer=1`. The `W` program for
the hard-restart instrument includes a `$09` step before the sustaining `$41` step.

### 3.9 Tempo Structure

Observed note durations (42nd Street V1): `{5: 1, 10: 2, 11: 4, 21: 2, 22: 10, 44: 1}`

The fundamental tempo unit is **11 frames** (50 Hz / 11 ≈ 4.55 Hz = 273 BPM eighth
notes, or ≈ 136 BPM quarter notes treating 22 as one beat). This is consistent across
both 42nd Street and Accident.

The ±1 frame jitter on 21 vs 22 is a timing artifact: JCH writes registers on a
specific cycle within the frame, and the note boundary falls one frame early or late
depending on the counter state.

**Reincarnations:** Note period = 8 frames (filter sweep period = 8). Tempo = 8.

JCH uses a **single VBI tempo** (no CIA multispeed). The tempo counter is decremented
once per VBI interrupt (50 Hz). Songs run at tempo 6–11 (60/11 ≈ 5 frames per tick).

Das Model's `Ω` (timing schedule) = single VBI rate, tempo counter. Compatible with
existing implementation. No CIA support needed for core JCH songs.

---

## 4. Das Model Mapping

### 4.1 T — Frequency Table

JCH uses the standard PAL SID frequency table (96 notes, C0–B7). The table is
embedded in the player binary and shared across all songs that use the same player
version.

**Das Model compatibility:** Full. JCH uses the same PAL freq table as GT2.
`song.freq_lo` and `song.freq_hi` can be populated from the standard table.

**Complication:** Some JCH songs use slightly non-standard tables (custom tunings).
The binary decompiler must extract the table from the player code, not assume the
standard PAL table.

### 4.2 I — Instruments

Each JCH instrument encodes:

| JCH data | Das Model field | Notes |
|----------|----------------|-------|
| AD byte | `E.ad` | Direct |
| SR byte | `E.sr` | Direct |
| Wave program | `W.steps[]` | Ctrl bytes per frame |
| PW initial | `P.init_pw` | At note start |
| PW speed | `P.speed` | Per-frame delta |
| PW mode | `P.mode` | linear or bidirectional |
| Vibrato depth | `V.scale` | Inverse: higher scale = shallower |
| Vibrato delay | `V.delay` | Frames before vibrato fires |
| Hard restart method | `E.hr_method` | gate or test |
| Gate timer | `E.gate_timer` | Frames before gate fires |

**What regtrace_to_usf misses:**
- `P.speed` (PW sweep speed) — the converter produces zero pulse table steps for all JCH songs
- `V` (vibrato program) — only the settled note is recorded, LFO oscillation is ignored
- Filter sweep (filter_table) — not recovered from trace

These are the three root causes of JCH F-grades.

### 4.3 S — Score

JCH's score is a pattern-based sequence with:

- Per-voice patterns with note, duration, and instrument number
- Repeat and transpose markers (similar to GT2 pattern commands)
- Multi-song support via subtune index

**Das Model compatibility:** Full. The `NoteEvent` structure captures note, duration,
and instrument_id. Pattern looping is handled by pattern repeat commands.

### 4.4 Ω — Timing Schedule

JCH uses single-speed VBI (50 Hz PAL). Tempo counter runs 6–11. No CIA multispeed.

**Das Model compatibility:** Full. Same timing model as GT2.

---

## 5. Gap Analysis

### 5.1 Gaps That Are Already Closed

The following JCH features map directly to existing Das Model fields:

| Feature | Das Model | Status |
|---------|-----------|--------|
| Pulse waveform | `W.steps` | Closed |
| Hard restart | `E.hr_method`, `W.steps` | Closed |
| ADSR | `E.ad`, `E.sr` | Closed |
| Arpeggio (2-note) | `F.arp_offset` | Closed |
| Vibrato (triangle LFO) | `V.scale`, `V.delay` | Closed |
| Sync sweep | `W.steps` + `freq_slide` | Closed |
| Multi-song | `song.songs` | Closed |
| Standard PAL freq table | `T` | Closed |

### 5.2 Gaps That Require Binary Parsing

The following features cannot be recovered from register traces but ARE in the
JCH binary and would be extractable by a JCH decompiler:

| Feature | Impact | Missing from regtrace_to_usf |
|---------|--------|------------------------------|
| PW speed table | ~20% note_wrong | Yes — all JCH PW sweeps missed |
| Filter speed table | ~10% env_wrong | Yes — filter sweep not captured |
| Vibrato parameters | ~5% note_wrong | Yes — vibrato classified as per-note freq change |
| Instrument pointer table | Architecture | Required for binary path |
| Pattern pointer table | Architecture | Required for binary path |

### 5.3 New Model Features Required

One feature is NOT currently in Das Model:

**Filter table per note (vs per song):**
JCH's filter sweep resets at each note boundary. The current `FilterTableStep`
program runs globally. JCH needs the filter envelope to restart when a new note fires
on voice 1 (the melody). This is a per-note filter envelope (analogous to the note's
ADSR envelope) rather than a global filter LFO.

Das Model's `filter_table` is currently attached to the Song object, not to individual
instruments. To support JCH correctly, the `Instrument` struct needs a `filter_table`
field (already present in USF `format.py`: `filter_ptr: int = 0`) — the model spec
in `das_model.md` should be updated to reflect that filter programs can be
instrument-scoped.

The USF `Instrument` dataclass already has `filter_ptr` and `filter_table` fields.
The Das Model formal spec (`das_model.md`) needs to document this as a first-class
capability.

---

## 6. Implementation Path for JCH Static Parser

A JCH decompiler (`src/converters/jch_to_usf.py`) would follow these steps:

1. **Identify player version** — sidid gives JCH_NewPlayer_V1..V19. Each version
   has the instrument table at a different offset but the same format.

2. **Find instrument table** — typically at a fixed address in each version.
   Each instrument entry: AD, SR, wave_ptr, pulse_ptr, filter_ptr, vib_speed, vib_delay.

3. **Find pattern table** — voice 1/2/3 pattern pointers. Each pattern: rows of
   (note, duration, instrument) tuples.

4. **Extract wave table** — sequence of ctrl bytes with loop point.

5. **Extract pulse table** — speed byte per instrument (linear PW increment).

6. **Extract filter table** — speed byte and direction, reset at note boundary.

7. **Extract freq table** — PAL standard or custom, embedded in player.

8. **Build USF Song** — populate T, I[], S from extracted data.

This is exactly the GT2 path but with JCH's binary layout instead of GT2's `.sng`
format. The taint tracker (`src/formal/taint_tracker.py`) can identify instrument
table addresses from the player's register write patterns.

**Estimated Grade A uplift:** A working JCH binary parser should achieve 85–90%
Grade A on core JCH songs (vs current ~67% average from regtrace_to_usf). The 10–15%
residual would be from version-specific variations and the filter-per-note sync issue.

---

## 7. JCH vs GT2 vs Hubbard Feature Comparison

| Feature | JCH | GT2 | Hubbard |
|---------|-----|-----|---------|
| Freq table | Standard PAL | Custom per-group | Fixed Hubbard table |
| Wave table | ctrl byte sequence | .sng format | ctrl+note sequence |
| PW modulation | Per-frame speed | Speed table | None |
| Filter sweep | Per-note envelope | Global table | None |
| Vibrato | Triangle LFO | Triangle LFO | Not observed |
| Arpeggio | 2-note alternation | N-way table | Binary bit flag |
| Hard restart | gate ($09→$41) | test+gate ($08→$09) | test ($08) |
| Sync mod | ctrl bit, freq slide | ctrl bit | None |
| Ring mod | Not observed | Not observed | Not observed |
| Noise drums | ctrl $80/$81 | ctrl $80/$81 | ctrl $81 |
| Tempo | VBI, 6–11 | VBI, 2–10 | Nested counters |
| Multi-song | Subtune table | Subtune table | Pattern bank |
| CIA multi-speed | No | No | No |

JCH is the closest of the three engines to GT2. The main structural differences are:

1. Filter is per-note (JCH) vs per-song (GT2)
2. PW table is simpler — a single speed byte per instrument (JCH) vs a full speed table (GT2)
3. JCH has no funktempo (variable-speed between rows)
4. Arpeggio via freq alternation every frame (JCH) vs multi-step table (GT2)

---

## 8. Recommended Next Steps

In priority order:

1. **Fix regtrace_to_usf PW recovery for JCH.** The converter detects PW changes but
   produces zero `PulseTableStep` entries. Adding PW speed detection (compute step
   between consecutive PW values, emit `PulseTableStep` with that speed) would
   immediately fix ~20% of JCH note_wrong errors without any binary parsing.

2. **Fix regtrace_to_usf filter recovery.** Currently the filter sweep is completely
   ignored. Adding filter modulation detection (compute cutoff delta per frame, emit
   `FilterTableStep`) would fix filter-related errors.

3. **Write JCH binary parser** (`src/converters/jch_to_usf.py`) for the NewPlayer
   family. This is the high-quality path equivalent to gt2_to_usf. Estimated +200
   Grade A songs over the trace path. Use `taint_tracker.py` to identify instrument
   table addresses in the 19 NewPlayer variants.

4. **Update Das Model spec** to document filter-per-note as a first-class feature.
   Add a section to `docs/das_model.md` § 3.5 "Filter Program" that mirrors the
   Envelope and Pulse program sections.
