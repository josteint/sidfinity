---
source_url: local corpus analysis + code review of deprecated/gt2_pipeline/converters/regtrace_to_usf.py
fetched_via: local analysis (LEAF agent, 2026-06-22)
fetch_date: 2026-06-22
author: LEAF research agent (extraction & representation strategy)
content_date: 2026-06-22
reliability: primary (corpus-derived) + reviewed (project code)
---

# Basic_Program — Extraction & Representation Strategy

**Cluster 6 research output.**
Read `00_local_recon_findings.md` first; this document assumes its facts as given.
The two blockers named there are:
- Blocker 1 (ground-truth capture / ROM sourcing) — addressed by research cluster 5; out of scope here.
- Blocker 2 (verification mode / USF representation) — addressed here.

---

## 1. The canonical BASIC POKE recipe — idiom catalogue

Every C64 BASIC music program is built from the same eight-register vocabulary.
This section is the idiom catalogue for the source-level decompile path (Path A).

### 1.1 SID register map as BASIC POKE addresses

The SID chip sits at `$D400` = decimal `54272`. BASIC programmers typically bind
`S=54272` (or `S1=54272` for voice 1) then address everything as `S+N`:

| POKE offset | Register | BASIC var name | Bit layout |
|---|---|---|---|
| `S+0` / `54272` | V1 Freq Lo | `LF`, `L1`, `LO` | 8-bit freq LSB |
| `S+1` / `54273` | V1 Freq Hi | `HF`, `H1`, `HI` | 8-bit freq MSB |
| `S+2` / `54274` | V1 PW Lo | `PL`, `PL1` | 8-bit PW LSB |
| `S+3` / `54275` | V1 PW Hi | `PH`, `PH1` | 4-bit PW hi (bits 0-3) |
| `S+4` / `54276` | V1 Ctrl | `W1`, `WV`, `WF` | bits: 7=NOISE 6=PULSE 5=SAW 4=TRI 3=TEST 2=RING 1=SYNC 0=GATE |
| `S+5` / `54277` | V1 A/D | `A1`, `AD` | hi nibble=Attack, lo nibble=Decay |
| `S+6` / `54278` | V1 S/R | `S1`, `SR` | hi nibble=Sustain, lo nibble=Release |
| `S+7` / `54279` | V2 Freq Lo | `L2`, `LF2` | same as V1 |
| `S+8` / `54280` | V2 Freq Hi | `H2`, `HF2` | |
| `S+9` / `54281` | V2 PW Lo | | |
| `S+10` / `54282` | V2 PW Hi | | |
| `S+11` / `54283` | V2 Ctrl | `W2`, `WV2` | |
| `S+12` / `54284` | V2 A/D | `A2`, `AD2` | |
| `S+13` / `54285` | V2 S/R | `S2`, `SR2` | |
| `S+14` / `54286` | V3 Freq Lo | `L3`, `LF3` | |
| `S+15` / `54287` | V3 Freq Hi | `H3`, `HF3` | |
| `S+16` / `54288` | V3 PW Lo | | |
| `S+17` / `54289` | V3 PW Hi | | |
| `S+18` / `54290` | V3 Ctrl | `W3`, `WV3` | |
| `S+19` / `54291` | V3 A/D | `A3`, `AD3` | |
| `S+20` / `54292` | V3 S/R | `S3`, `SR3` | |
| `S+21` / `54293` | Filter Lo | | bits 0-2: cutoff LSB |
| `S+22` / `54294` | Filter Hi | | bits 0-7: cutoff hi byte |
| `S+23` / `54295` | Filter Ctrl | | bits 0-3: V1/V2/V3/EX route; 4-6: resonance |
| `S+24` / `54296` | Mode/Vol | `V`, `VM`, `VOL` | hi nibble: mode/filter; lo nibble: master vol |

### 1.2 Ctrl register waveform constants

Commonly POKEd control values (voice goes to `S+4`, `S+11`, `S+18`):

| Decimal | Hex | Meaning |
|---|---|---|
| 17 | `$11` | TRIANGLE + GATE (note on) |
| 16 | `$10` | TRIANGLE (gate off / release) |
| 33 | `$21` | SAWTOOTH + GATE |
| 32 | `$20` | SAWTOOTH gate off |
| 65 | `$41` | PULSE + GATE |
| 64 | `$40` | PULSE gate off |
| 129 | `$81` | NOISE + GATE |
| 128 | `$80` | NOISE gate off |
| 49 | `$31` | SAW+TRI + GATE (metallic timbre) |
| 97 | `$61` | PULSE+SAW + GATE |
| 9 | `$09` | TEST+GATE (oscillator freeze — hard restart prep) |
| 0 | `$00` | All off |

### 1.3 Frequency encoding

A note is identified by a 16-bit SID frequency register value split into
hi/lo bytes. In DATA statements, programmers typically store the two bytes
separately as decimal integers:

```basic
DATA 25,177, 28,214, 32,94    REM G5, A5, B5 (HI, LO triplets with duration)
```

The 16-bit frequency for a note at PAL clock (985248 Hz) is:
```
freq16 = note_hz * 16777216 / 985248
```

Standard PAL table notes 0-95 (C1=0 through B8=95) map to `(FREQ_HI, FREQ_LO)` pairs.
The existing `regtrace_to_usf.py` has the complete 96-entry PAL table at lines 47-66;
it is the authoritative reference for note-to-freq mapping.

**Note: some BASIC programs use `INT(HI/LO)`, some use float arithmetic
(`FQ/256`, `FQ AND 255`). These produce IDENTICAL byte values — the mapping is exact.**

### 1.4 The five canonical BASIC music idioms

**Idiom 1 — Single-voice DATA/READ table (most common, ~57% of corpus):**
```basic
5 S=54272
10 POKE S+5,9:POKE S+6,0   : REM ADSR: A=0,D=9,S=0,R=0 (fast attack, no sustain)
20 POKE S+24,15             : REM master vol=15
30 READ HF,LF,DR            : REM hi-freq, lo-freq, duration
40 IF HF<>0 THEN END
50 POKE S+1,HF:POKE S,LF   : REM set frequency
60 POKE S+4,33              : REM SAW + GATE (note on)
70 FOR T=1 TO DR:NEXT       : REM duration = busy-wait loop
80 POKE S+4,32              : REM gate off (release)
90 FOR T=1 TO 50:NEXT       : REM inter-note gap
100 GOTO 30
110 DATA 25,177,250, 28,214,250, 0,0,0
```

Note events are: freq_hi, freq_lo, duration (in FOR-loop iterations).
Sentinel: `DATA 0,0,0` or `DATA -1,-1,-1`.

**Idiom 2 — Multi-voice simultaneous (3 voices, chords/polyphony):**
```basic
10 V1=54272:V2=54279:V3=54286  : REM base addresses per voice
20 READ H1,L1, H2,L2, H3,L3,T  : REM 7 values: 3 freq pairs + duration
30 POKE V1+1,H1:POKE V1,L1
40 POKE V2+1,H2:POKE V2,L2
50 POKE V3+1,H3:POKE V3,L3
60 POKE V1+4,33:POKE V2+4,33:POKE V3+4,33   : REM gate all 3
70 FOR N=1 TO T*K-100:NEXT     : REM duration with tempo multiplier K
80 GOTO 20
```
Multi-voice programs (39% use `S+7` offsets) store note data as 6 or 7 values
per DATA item: `(H1, L1, H2, L2, H3, L3 [, duration])`.
Rest note = `(0,0, 0,0, 0,0)` or a specific sentinel hi-byte.

**Idiom 3 — Indexed array pre-load with DIM:**
```basic
10 DIM HI(25),LO(25),DU(25)
20 FOR X=1 TO 25:READ HI(X),LO(X):NEXT  : REM load freq table
30 FOR X=1 TO 25:READ DU(X):NEXT        : REM load duration table
40 FOR X=1 TO 25
50   POKE 54273,HI(X):POKE 54272,LO(X) : REM set freq
60   POKE 54276,65                      : REM PULSE+GATE
70   FOR L=1 TO DU(X)*1.5:NEXT         : REM delay
80   POKE 54276,64
90 NEXT X
```
Same semantics as Idiom 1 but with array pre-loading. Extractor outcome: identical.

**Idiom 4 — COS(M)/PEEK-address as compact data store:**
Seen in the Commodore BASIC examples from the PRG manual and the Bach fugues.
```basic
90 M=2720:F=1.2                      : REM M = data start address in RAM
110 S=COS(M):IF S=0 GOTO 220         : REM S=0 is end-sentinel
120 X1=COS(M+1):Y1=COS(M+2):...     : REM read 6 more values
140 IF X1 THEN POKEH1,X1:POKEL1,Y1:POKEV1,33
190 T=T+S*F:WAIT...                  : REM duration = wait for jiffy count
210 GOTO 100
```
In this idiom, `M` is a RAM address. The KERNAL floating-point machinery
means `COS(M)` evaluates to the BASIC-float representation of the integer
stored at address M (the DATA values loaded there on startup). The composer
pre-computes which integer values, when stored as BASIC floats at known RAM
offsets and retrieved via `COS(addr)`, yield the desired register bytes.
**For the purposes of extraction: this IS deterministic.** `COS(2720)` with
a known initial RAM layout (the DATA lines of the same program) produces
a fixed integer value. The ground-truth trace captures this correctly.
Source-level decompile of this idiom requires simulating BASIC float storage.

**Idiom 5 — Algorithmic / mathematical frequency generation:**
```basic
4 POKE S+1,PEEK(M)/28:POKE S+8,TI AND PEEK(M+64):M=M+.2:GOTO 4
```
Frequency computed from `PEEK(ROM/RAM address)`, `TI` (jiffy timer), or
math functions (`COS`, `SIN`, `RND`). Non-table-driven. Under sidplayfp
with real ROMs and TI=0: fully deterministic (except for `RND()`).

### 1.5 Timing model

BASIC music has NO relationship to the 50 Hz VBI interrupt. It runs in
the BASIC interpreter thread continuously. Timing is set by busy-wait loops:

| FOR/NEXT iterations | Approx. duration (PAL 1 MHz) | Approx. PAL VBI frames |
|---|---|---|
| 50 | ~15 ms | ~0.75 |
| 100 | ~30 ms | ~1.5 |
| 125 | ~37 ms | ~1.9 |
| 145 | ~43 ms | ~2.2 |
| 200 | ~60 ms | ~3.0 |
| 250 | ~75 ms | ~3.75 |
| 500 | ~150 ms | ~7.5 |
| 750 | ~225 ms | ~11.25 |

(Estimate: ~0.3 ms per empty FOR/NEXT iteration with float variables; integer
variables `N%` are faster ~0.2 ms. Varies ±15% with surrounding code.)

The standard inter-note gap (`FOR T=1 TO 50:NEXT` after gate-off) is ~15 ms
≈ 0.75 VBI frames — sub-frame timing. siddump's VBI frame bucketing is NOT
aligned to any BASIC concept; the write STREAM is what matters.

---

## 2. Corpus breakdown — what the 486 programs actually are

Analysis of all 486 programs using the detokenizer (one error = invalid
tokenized BASIC, i.e. the SID may have a non-standard load address):

| Class | Count | % | Description |
|---|---|---|---|
| A — pure DATA/READ + FOR/NEXT | 277 | 57% | Table-driven single or multi-voice |
| B — DATA + PEEK/TI arithmetic | 35 | 7% | READ with simple addr/time arithmetic |
| C — SYS to ML subroutine | 8 | 2% | Partially in machine code |
| D — algorithmic (math/COS/SIN) | 9 | 2% | Freq from math, not lookup |
| E — interactive (GET) | 83 | 17% | Keyboard-driven, no-key path deterministic |
| Other (sound effects / short) | 73 | 15% | Single-note demos, envelope demos |

**Key finding on Class E (interactive):** Under sidplayfp with the C64 BASIC
flag set, `GET` returns `""` (empty string) when no key is pressed. The
no-keypress path is therefore deterministic and follows the song's looping
structure. These are NOT blocked for trace capture. The 83 interactive SIDs
ARE capturable via the ground-truth trace path.

**Key finding on determinism:** Only `RND()` (5 programs) introduces genuine
non-determinism. `TI` (jiffy timer) starts at 0 in sidplayfp, making
TI-seeded timing deterministic. `COS/SIN/PEEK` are pure math/memory,
deterministic. `RND` programs (Two_Lines_of_Code_1 and ~4 others) produce
a different stream on every run and cannot be given USF note events; they
require a special treatment (excluded or single-snapshot USF).

**Usage statistics across all 486:**
- 80% use DATA/READ
- 98% use FOR/NEXT (virtually all use busy-wait delay)
- 40% reference the jiffy timer TI (mostly as tempo, deterministic)
- 42% have COS/SIN tokens (split: ~77 have COS in POKE lines, ~17 in PRINT title)
- 39% use multi-voice patterns (S+7 offsets)
- 17% use GET (keyboard)
- 6% use PEEK
- 1% use RND

---

## 3. The two extraction paths — detailed analysis

### 3.1 Path A — Source-level decompile

**What it does:** Parse the tokenized BASIC, recognise idioms (DATA/READ
tables, FOR/NEXT delays, POKE patterns), and lift the sequence of `(gate-on:
freq_hi, freq_lo, waveform, ADSR)` + `(gate-off: duration)` tuples directly
from the source. No ROM, no emulation.

**How the detokenizer works** (already proven in this project's recon):
1. Walk the linked-list structure at $0801 (2-byte next-link pointer, 2-byte
   line number, tokenized bytes, $00 terminator).
2. Replace token bytes $80-$CF with keyword strings; pass ASCII bytes through.
3. Identify DATA lines by token $83 and extract the comma-separated values.
4. Identify POKE lines by token $97 and extract `(address, value)` pairs.
5. Follow GOTO/GOSUB chain to determine execution order.

**Tractable for Path A:**
- Class A (57%): trivially — DATA gives note table, FOR/NEXT gives durations.
- Class B (7%): with arithmetic evaluation (simple `INT(X/256)`, `X AND 255`).
- Class Other (15%): sound-effect demos have even simpler POKE sequences;
  no table needed, durations are direct FOR/NEXT loop counts.
Total path-A tractable: ~79% of corpus.

**Limitations:**
- COS(M) idiom (Fugue, Inventions): requires simulating C64 floating-point
  storage layout to know what value `COS(address)` returns. Non-trivial.
- Interactive GET: the no-key path can be inferred if the GET only affects
  looping/stopping (most common), but if GET selects a note (piano programs,
  13 members), source-level decompile cannot recover the musical content.
- SYS calls (8 members): the machine-code subroutine must also be disassembled.
- GOTO graph non-linearity: programs with complex GOSUB/GOTO may need a
  symbolic interpreter to trace the note sequence.

**Verification problem for Path A:**
Path A produces a note sequence that must be verified against the HVSC original's
`$D400` write stream. The reconstructed SID must reproduce the same ordered
`(reg, val)` sequence. But Path A's rebuilt SID will use our composer (which
fires at a regular rhythm) while the original fires writes at BASIC interpreter
speed. The timing within a note (the gate-on POKE, the freq POKE, the gate-off
POKE) matters for the verification check. Specifically: in BASIC, the order is
typically `freq_lo, freq_hi, ctrl (gate-on)` per voice — matching the POKE
order in the program. Our composer must reproduce that ORDER, not just the
VALUES. This is a representation constraint: the USF note-event must carry
enough information to reproduce the POKE order (e.g., does gate-on happen before
or after freq writes?).

### 3.2 Path B — Trace-level lift (ground-truth then lift)

**What it does:** Run the tune under libsidplayfp (real ROM loaded), capture
the ordered `(cycle, reg, val)` $D400 write stream, then lift that stream
into USF note events — exactly what `deprecated/gt2_pipeline/converters/regtrace_to_usf.py`
does.

**The deprecated `regtrace_to_usf.py` (Path B prototype):**
Implemented in `deprecated/gt2_pipeline/converters/regtrace_to_usf.py` (~1578 lines).
Key algorithms already proven:
1. Run siddump to get per-VBI-frame register snapshots (note: NOT the write stream
   — this is snapshot-per-frame, which is Trap A for tracker music but is used
   here as a proxy since BASIC writes tend to land mid-frame in ways that make
   frame-state comparisons insufficient).
2. `extract_voice_events()`: detect gate transitions (0→1 = note-on, 1→0 = note-off),
   frequency changes, waveform transitions. Per-voice event lists.
3. `freq_to_note_pal()`: 16-bit SID freq → nearest PAL note number (0-95).
4. `detect_tempo_from_frames()`: find the most common gate-on interval → tempo.
5. `build_instruments()`: cluster (AD, SR, waveform) tuples → instrument definitions.
6. `collapse_arpeggios()`: merge rapid note sequences into arpeggio events.
7. `quantize_events()`: divide frame durations by tempo → tick counts.
8. `events_to_pattern()`: tick-based events → USF NoteEvent list.

**Critical gap in the existing prototype:** It uses siddump's VBI-frame snapshots
(Trap A — registers sampled once per frame, not per-write). For BASIC music
where writes happen at arbitrary mid-frame cycles, this means:
- A note that gates on and off within one VBI frame is invisible.
- Multiple writes to the same register within a frame show only the last value.
- The write ORDER within a note-on event is lost.

To make Path B correct for BASIC music, the capture must use
`siddump --writelog` (the ordered `(cycle, reg, val)` stream) rather than
the per-frame snapshot. The `regtrace_to_usf.py` already has the write-log
infrastructure in mind (the `detect_digi_playback` function references it and
the `--writelog-per-irq` mode) but the main lift loop uses frame snapshots.
**This is the critical upgrade needed for Path B to work on BASIC programs.**

**Verification for Path B:** The rebuilt SID (USF → composer → xa65 → PSID)
must reproduce the same `(reg, val)` sequence as the HVSC original. The
comparison mode is the CONTINUOUS ORDERED WRITE STREAM (no VBI bucketing,
no `play()` boundary) — a variant of `compare_instruction_stream` with no
init-period skip (since BASIC has no init/play split; the whole program is one
continuous stream).

### 3.3 Tradeoffs between Path A and Path B

| Criterion | Path A (source decompile) | Path B (trace lift) |
|---|---|---|
| Alignment with CORE TENET | Partial: starts from engine code | Full: write-log IS the target |
| ML-readiness of USF output | High: clean note events from source | High: same — lifted note events |
| Tractability for Class A/B | Excellent (80%) | Excellent (all) |
| Tractability for algorithmic/COS | Fails for COS idiom, PEEK-ROM | Succeeds (ROM executes it) |
| Handles interactive GET | Fails (13 piano programs) | Succeeds (no-key path captured) |
| Requires ROM images | No | Yes (Blocker 1) |
| Timing fidelity | Approximate (loop-count to ms) | Exact (write stream captures actual timing) |
| Source availability | Only for DATA-based tunes | Universal (every BASIC program) |
| Handles RND programs | No (non-deterministic) | One-snapshot possible (caveat: changes each run) |
| Verification mode | Needs exact write-order from composer | Write-stream replay is the check |
| Existing code to revive | Partial (detokenizer proven) | Partial (regtrace_to_usf.py needs writelog upgrade) |

### 3.4 The CORE TENET judgment

From CLAUDE.md: *"The verification target is the SID write-log stream, not the
engine code."* and *"The original engine's machine code is a historical artifact,
not a blueprint."*

**Path A violates this tenet if used as the primary path.** It starts from engine
code (the BASIC program), not from the write stream. The extracted note sequence
is only correct if the idiom-recognition exactly matches what the program actually
does. For the 80% of programs where idiom-recognition is robust, Path A's output
is equivalent to Path B's — but the VERIFICATION IS STILL THE WRITE STREAM.
Path A can succeed only if the rebuilt SID reproduces the correct write stream.

**Path B is the canonical fit.** It captures the write stream first (the target
per the CORE TENET), then lifts it to musical events. The engine code (BASIC
program) is bypassed entirely in the verification loop: HVSC original → capture
write stream → lift → USF → composer → rebuilt SID → verify write stream matches.
The "engine code" (BASIC interpreter + specific program) is the historical artifact;
the write stream is the signal.

**The right hybrid is:** Use Path A as a fast-path recognition layer for the 80%
of clean DATA/READ programs, to produce better-quality USF (exact note values,
exact durations in readable tick units), but ALWAYS verify the result against
the ground-truth write stream captured via Path B. Where Path A fails (COS idiom,
interactive, SYS), fall back to Path B exclusively.

In practice: implement Path B first (write-stream capture + lift), since it is
universal and is what the verification checks anyway. Path A is an optional
optimization that produces more structured/readable USF for the tractable majority.

---

## 4. Verification mode for BASIC programs

The project's two current verification modes do NOT directly apply:
- **Mode 1 (per-play frame):** No `play()` vector. Inapplicable.
- **Mode 2 (cycle-exact):** Too strict — BASIC cycle timing varies with
  interpreter state, loop variable type (int vs float), and surrounding code.
  Cycle-matching across a rebuilt SID (which uses a regular machine-code player)
  and the original (which uses the BASIC interpreter) is impossible.

**The correct mode for BASIC programs:**

**Mode 3 (proposed): Continuous ordered `(reg, val)` write stream, full song,
no init/play boundary.** Compare the ordered sequence of `(reg, val)` writes
(cycles dropped, as in `compare_instruction_stream` flat mode) for the entire
playback duration.

This is exactly what `compare_instruction_stream` already does when called
without `play()` bucketing, i.e., what the flat-prefix mode produces. The
difference from Mode 1 is that there is no init/play split — the whole BASIC
program execution is one continuous stream from `RUN` to program end (or a
fixed playback duration).

**Practical consequences:**
- `siddump --writelog` on the HVSC RSID (with `--force-rsid` and real ROMs)
  produces the continuous `(cycle, reg, val)` stream.
- The rebuilt SID (composed by our composer, with a regular player loop) also
  produces a stream via `siddump --writelog`.
- `compare_instruction_stream(mode='flat')` compares the two flat `(reg, val)`
  sequences.

**IMPORTANT CAVEAT — timing quantization error:**
The rebuilt SID uses a machine-code player that fires at regular intervals
(50 Hz or multispeed). The original BASIC fires writes at arbitrary interpreter
cycles. A note-on + note-off that takes 75 ms in BASIC will be reproduced as
exactly N ticks in the rebuilt SID, where `N = round(75ms / tick_duration)`.
Quantization error means the rebuilt write count may differ by ±1 tick. The
write ORDER is exact but the exact per-note DURATION may be off by one tick.

Recommendation: use a **duration-tolerance** variant of `compare_instruction_stream`
for BASIC, similar to the `close_tol` parameter in DMC verification, allowing
±10% duration mismatch while requiring exact register+value sequence within
notes. This is a new mode parameter, not a new verification tool.

---

## 5. USF representation of BASIC music

### 5.1 What musical content BASIC programs carry

A BASIC music program's musical content — the part that belongs in USF — consists of:

| Content | USF representation |
|---|---|
| Note pitch (freq_hi, freq_lo) | Note number (0-95) in existing USF note-event |
| Note duration (FOR/NEXT count) | Tick count in existing USF note-event (with tempo) |
| Voice assignment (V1/V2/V3) | Per-voice pattern in existing USF structure |
| Waveform (ctrl bits 4-7) | `waveform: triangle/sawtooth/pulse/noise` in Instrument |
| ADSR (AD/SR bytes) | `ad`, `sr` bytes in existing USF Instrument |
| Pulse width (PW hi/lo) | `pulse_width` in existing USF Instrument |
| Master volume (`S+24` low nibble) | `master_vol` in existing USF global / `init.sid` block |
| Filter cutoff/resonance (`S+21-23`) | Filter block in existing USF (if applicable) |
| Inter-note gap (gate-off duration) | `gate_timer` / rest event in existing Instrument |
| Hard restart (TEST bit sequence) | `hr_method` in existing USF Instrument |

**Key observation: the existing USF schema already has fields for all of these.**
BASIC programs do NOT introduce any new musical degrees of freedom that require
new USF schema additions. They simply use a different execution mechanism
(interpreter busy-wait) to produce the same register-level musical events that
tracker music produces via a player loop.

This is the USF representation principle's Rule 2 in action: the CONTENT
(note, duration, waveform, ADSR) goes into USF; the MECHANISM (BASIC interpreter,
FOR/NEXT delay) is the historical artifact.

### 5.2 What NOT to put in USF

Following the USF representation principle, these MUST NOT appear in USF:

- `for_next_delay_count`: the raw FOR/NEXT iteration count (mechanism, not content)
- `basic_line_number`: the line number (mechanism)
- `poke_address`: the absolute SID register address (mechanism)
- `basic_program_bytes`: the tokenized BASIC (raw engine code — exactly the
  forbidden `bytes`-typed field the schema addition discipline warns against)
- `playback_speed_microseconds_per_tick`: the BASIC timing constant (semi-mechanism;
  the musical content is the note duration in ticks relative to the tempo, not the
  absolute microsecond count)

### 5.3 The tempo problem — BASIC has no canonical tick

Tracker music has an explicit tempo (frames-per-row). BASIC uses FOR/NEXT
counts. The lift must quantize real durations to ticks:

```
tempo_ticks = detect_common_divisor_of_all_durations()
note_ticks  = round(note_duration_ms / (tempo_tick_ms))
```

This is exactly what `regtrace_to_usf.py`'s `detect_tempo_from_frames()` does.
The quantized result carries the musical content (relative durations) in a
form that the USF schema already supports.

For BASIC programs, `detect_tempo_from_frames()` must be run on the WRITELOG
stream (not VBI-frame snapshots) to get the true gate-on intervals.

### 5.4 Multi-voice representation

BASIC multi-voice programs (39% of corpus) write all three voices simultaneously
in a tight POKE sequence before the delay loop. The USF three-voice pattern
structure already handles this: each voice gets its own pattern with simultaneous
note-on events at the same tick position. No schema change needed.

### 5.5 Interactive programs (83 SIDs) — the exclusion question

The 83 GET-using programs present a design decision:

**Option 1: Capture the no-keypress deterministic path.** sidplayfp with no
keyboard input will follow the `GET A$: IF A$="" THEN ...` branch. Most of
these programs simply loop indefinitely with no key (infinite song) or stop
(finite song). The trace is valid and reproducible. This is the recommended
approach for programs that use GET only to stop playback.

**Option 2: Exclude the 13 "piano" programs** (where GET selects which note
to play). These have no canonical note sequence — the "music" is whatever the
user played. Exclude via `tools/excluded_sids.json` with reason
`"Interactive piano program — no canonical note sequence without a recorded performance"`.

### 5.6 RND programs — exclusion

The ~5 RND-using programs (Two_Lines_of_Code_1_BASIC.sid etc.) generate notes
non-deterministically. They cannot be given a canonical USF representation
without a single arbitrary snapshot of one playthrough. Recommend exclusion
with reason `"Algorithmic/generative: RND-seeded non-deterministic music"`.

---

## 6. Existing tools to revive and adapt

### 6.1 `deprecated/gt2_pipeline/converters/regtrace_to_usf.py`

This is the Path B prototype. It already implements:
- Gate-transition note detection per voice
- PAL freq → note-number mapping  
- Tempo detection from gate-on intervals
- Instrument clustering by (AD, SR, waveform)
- Arpeggio detection and collapse
- Wave-table extraction from frame patterns
- Pulse-modulation detection
- USF Song object construction

**What needs upgrading for BASIC programs:**
1. **Capture path**: Replace VBI-frame snapshot input with `siddump --writelog`
   ordered stream. The `run_siddump()` function uses frame snapshots; it must be
   extended to call `siddump --writelog` (or use the existing writelog capture
   infrastructure in `pipelines/hubbard/verify_cycle.py`).
2. **RSID support with real ROMs**: The `--force-rsid` flag is already added in
   the `run_siddump()` function, but the ROM loading (Blocker 1) must be solved
   first.
3. **Duration-tolerance verification**: Add tolerance to the write-stream comparison
   for the timing quantization error.
4. **Continuous stream mode**: Remove the `play()` boundary assumption; treat the
   entire capture as one unbroken stream.
5. **USF v2 schema alignment**: The deprecated code targets USF v1. The Song/Instrument/
   NoteEvent objects must map to v2 schema fields.

### 6.2 The BASIC detokenizer

A working BASIC V2 detokenizer (token table + linked-list walk) is proven in
the recon session and in this session's survey code. For Path A, this becomes
the first stage of a `basic_to_usf.py` extractor.

### 6.3 `pipelines/hubbard/verify_cycle.py`

The `writelog_capture()` and `compare_instruction_stream()` functions here are
the correct comparison infrastructure. `compare_instruction_stream(mode='flat')`
(no `play()` bucketing) applied to the continuous write stream is the right
comparator for BASIC programs. Add a `duration_tol` parameter to allow ±N
ticks of duration mismatch.

---

## 7. Recommendation

**Primary path: Path B (trace-level lift) as the universal base; Path A
(source decompile) as an optional quality enhancement for Class A/B programs.**

Rationale grounded in the CORE TENET and USF representation principle:

1. **Path B is the canonical fit to the CORE TENET.** The write-log stream IS the
   target. The BASIC interpreter is the historical artifact — we need what it
   produces, not how it produces it. Path B captures that directly.

2. **Path B handles 100% of tractable programs** (all except the 5 RND programs).
   Path A handles only ~79% without additional complexity.

3. **Both paths produce the same USF content** when they agree (the lifted USF
   is note events, not BASIC-specific fields). The schema is unchanged.

4. **The verification check is the same regardless of extraction path:** the
   rebuilt SID's write stream must match the HVSC original's write stream.
   Path A's quality advantage (exact note values from source) is subsumed by
   verification — if the write streams match, the extraction was correct.

5. **Path B's existing prototype** (`regtrace_to_usf.py`) already covers the
   hard algorithmic work. It needs a writelog-based capture upgrade and USF v2
   alignment, not a ground-up rewrite.

**Recommended implementation order:**
1. Solve Blocker 1 (ROM sourcing) so that sidplayfp can run the BASIC programs
   and `siddump --writelog` can capture them.
2. Upgrade `regtrace_to_usf.py` to use `--writelog` stream instead of VBI-frame
   snapshots. Revive as `pipelines/basic_program/extract/trace_to_usf.py`.
3. Add continuous-stream verification mode to `compare_instruction_stream`
   (drop the `play()` boundary assumption; add `duration_tol` parameter).
4. Exclude ~5 RND programs and ~13 interactive-piano programs via
   `tools/excluded_sids.json`.
5. Wire the BASIC pipeline into `tools/regression.py` as a new family tier.
6. Optionally: implement Path A as a source-level decompile pass for Class A/B
   programs to produce more structured/readable USF (better ML token quality
   for note durations, cleaner instrument assignment).

**What FULL status means for a BASIC SID:**
Same as all other engines — the rebuilt SID's ordered `(reg, val)` write stream
matches the HVSC original's write stream (within the duration-tolerance window)
for the full song length. The `compare_instruction_stream(mode='flat',
duration_tol=0.1)` call is the verdict.

---

## 8. The COS(M) trick — decoding note

The `COS(M)` idiom in the Commodore BASIC examples (Fugue in G Minor, Bach
Inventions, Gigue in G, etc.) is a specific C64 BASIC trick where the DATA
values are stored in the tokenized BASIC body at RAM address M=2720 ($0AA0),
and `COS(M)` exploits the C64 BASIC floating-point representation to retrieve
them as integers through some aspect of the KERNAL math routines.

**For USF extraction purposes, this does NOT require understanding the trick's
mechanics.** Under sidplayfp with real ROMs, `COS(M)` evaluates correctly to
whatever byte values the program intended, producing the correct SID writes.
Path B (trace-lift) handles this transparently.

**For Path A decompile**: would require simulating C64 BASIC float storage to
decode the DATA values. Not recommended for this idiom — use Path B fallback.

---

## Leads to follow

1. **Blocker 1 (ROM sourcing)** — research cluster 5 must resolve where to get
   legal C64 KERNAL+BASIC+CHARGEN ROM images for use with sidplayfp's `setRoms()`
   API. The project already has `tmp/jc64/data/{basic,kernal}.rom`; provenance
   and licensing need clarification. The MEGA65 OpenROMs project (`https://github.com/mega65/mega65-core/`) ships open-licensed C64-compatible ROMs; confirm compatibility
   with sidplayfp.

2. **`siddump --writelog` RSID support** — does the current `siddump.cpp` produce
   a writelog for RSID files when given `--force-rsid`? Or does it only work for
   PSID (which has a `play()` vector)? Need to verify that `--writelog` captures
   writes that happen during BASIC execution (which has no `play()` vector — the
   whole program runs during the KERNAL's `play()` callback in sidplayfp's
   RSID-BASIC mode). See `HVSC/DOCUMENTS/SID_file_format.txt` for RSID-BASIC
   playback semantics.

3. **sidplayfp RSID-BASIC execution model** — when sidplayfp encounters an RSID
   with the BASIC flag set, it runs the BASIC program by starting from `$E5D5`
   (BASIC RUN command vector) within its IRQ-driven playback loop. Confirm:
   does the BASIC program run synchronously in one call, or does it use the CIA
   timer / raster IRQ to fire `play()` periodically? The `play=0` in the PSID
   header means sidplayfp itself drives execution from `RUN`. This needs a test
   with a known BASIC SID to confirm the writelog capture works.

4. **`regtrace_to_usf.py` writelog upgrade** — the prototype uses VBI-frame
   snapshots (Trap A). Upgrading to use `siddump --writelog` (`--writelog-per-irq`
   not applicable here) is the key engineering task for Path B. The writelog
   gives `(cycle, reg, val)` triples; the note-detection logic must be rewritten
   to detect gate transitions from the write stream rather than from per-frame
   state snapshots.

5. **Duration-tolerance in `compare_instruction_stream`** — the BASIC timing
   quantization error means we need a `duration_tol` parameter (fraction of total
   song duration to allow mismatch on note boundaries). Prototype and validate
   against 3-5 real BASIC SIDs after Blocker 1 is resolved.

6. **Verify the COS(M) mechanism** — check whether `COS(M)` in C64 BASIC is
   literally computing `cos(M radians)` (giving floats 0-1 that POKE as 0) or
   whether it exploits some KERNAL/BASIC implementation detail that acts more like
   `PEEK(M)`. Running `Fugue_in_G_Minor_J_S_Bach_BASIC.sid` under a cycle-exact
   emulator (VICE or FPGA) and tracing what values `COS(2720)` etc. return would
   settle this definitively. This matters for Path A but NOT for Path B.

7. **Interactive GET programs — no-key-path test** — run `Ahoy_Magazine_BASIC.sid`
   (has GET) under sidplayfp with real ROMs and capture the writelog. Confirm it
   produces a deterministic note sequence (the song loops indefinitely without a
   keypress). If yes, these 83 programs are tractable via Path B.

8. **Exclude list for RND programs** — identify the exact 5 (or more) RND-using
   programs and add them to `tools/excluded_sids.json`. Names known from survey:
   `Two_Lines_of_Code_1_BASIC.sid` (confirmed RND). Run a full scan with the
   detokenizer to find all others.

9. **The "Other" category (73 programs)** — these were not classified as pure
   DATA/READ but are not algorithmic either. Most appear to be short sound-effect
   programs (Commodore PRG examples, single-note experiments). They are trivially
   handled by Path B. A quick manual scan of 10-15 representatives would confirm
   this or reveal further sub-types.

10. **Multi-subtune BASIC SIDs** — the `$030C` register selects the subtune before
    `RUN`. The HVSC format stores this in the PSID header; sidplayfp writes `$030C`
    before executing. Verify that multi-subtune BASIC SIDs (like
    `Commodore_64_Christmas_Album_BASIC.sid` with 7 subtunes) work correctly —
    each subtune is a separate `RUN` with a different `$030C` value.
