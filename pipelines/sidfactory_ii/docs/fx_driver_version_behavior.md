---
source_url: https://github.com/Chordian/sidfactory2 (driver notes + C++ source + user manual)
fetched_via: direct
fetch_date: 2026-06-13
author: Thomas Egeskov Petersen (Laxity), Jens-Christian Huus (JCH)
content_date: 2026-03-14
reliability: primary
secondary_sources:
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver11.txt
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver12.txt
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver13.txt
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver14.txt
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver15.txt
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver16.txt
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/user_manual_20260314.txt (p.14-15)
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/faq.txt
---

# SID Factory II — Driver Version Behavioral Differences

This document catalogues the register-level behavioral differences between all SF2 drivers
(11, 12, 13, 14, 15, 16) with focus on what changes at the SID $D400–$D418 write level.
A re-emitter must detect the driver version and apply the correct model.

---

## Driver 11 — The Standard (reference driver; most HVSC SF2 tunes use this)

Full-featured driver. See `fx_register_semantics.md` and `fx_table_execution.md` for
the complete model.

### Version sub-history (all sub-versions have the same core model; additions only):

| Sub-version | Binary file         | Added behavior |
|-------------|---------------------|----------------|
| 11.00       | sf2driver11_00.prg  | Base driver (all core effects above) |
| 11.01       | sf2driver11_01.prg  | +Fret slide command T4 |
| 11.02       | sf2driver11_02.prg  | +Pulse program index (Tc), Tempo program index (Td), Main volume (Te) |
| 11.03       | sf2driver11_03.prg  | +Filter enable flag in instrument byte 2 bit 5 ($20) |
| 11.04       | sf2driver11_04.prg  | +Note delay: T-nibble of note byte (0–15 tick delay) |
| 11.05       | sf2driver11_05.prg  | -Fret slide removed; HR table 16→8 rows; +skip-pulse-reset flag $08 |

### Core tables present: Wave, Pulse, Filter, HR, Arp, Tempo, Init, Instruments, Commands
### Instrument: 6 bytes (AD, SR, Flags, Filter-idx, Pulse-idx, Wave-idx)
### Multi-speed: NOT supported (FAQ confirms: "multispeed" is a planned future feature)
### Hard restart: User-configurable HR table; fires 2 frames before next note

---

## Driver 12 — The Barber (simplest driver)

"Extremely simple driver that can only do the most basic effects."

### Tables: Wave only (no pulse table, no filter table, no HR, no arp, no tempo)
### Instrument: 4 bytes
```
Byte 0: AD
Byte 1: SR
Byte 2: Waveform  (written directly to Voice+4; static, not a table index)
Byte 3: Pulse width XY  (X = middle 4 bits of 12-bit PW, Y = top 4 bits)
         12-bit PW = (Y << 8) | (X << 4)  → written to Voice+2/3 statically
```

### Commands: 3 types only (no ADSR, no filter, no arp, no portamento, no HR)
```
0X XX  Slide up   (12-bit speed: X = hi nibble, XX = lo byte)
1X XX  Slide down (12-bit speed: X = hi nibble, XX = lo byte)
2X -Y  Vibrato    (X = frequency, Y = amplitude)
```

### Differences from driver 11:
- No pulse TABLE — pulse width is a static value in the instrument, not a running program
- No filter control whatsoever ($D415–$D418 filter bits never written by driver)
- No hard restart table — no HR at all
- No arpeggio table (arp only via wave table semitone stepping)
- Slide speed is 12-bit (driver 11 uses 16-bit); different speed encoding
- Vibrato format identical to driver 11's in terms of parameters but 12-bit speed variant
- No portamento (T2), no ADSR commands (T8/T9), no filter commands, no demo sync

### SID registers written by driver 12:
- Voice+4 (ctrl): from instrument byte 2 (static waveform; not per-frame table)
- Voice+5 (AD), Voice+6 (SR): from instrument bytes 0/1
- Voice+2/3 (PW lo/hi): from instrument byte 3 (static; not updated per frame unless slide active)
- Voice+0/1 (freq lo/hi): note frequency + slide/vibrato

---

## Driver 13 — The Hubbard Experience (Rob Hubbard emulation)

"A driver that emulates the sound of Rob Hubbard's driver."
This is an EMULATION within the SF2 framework — it mimics Hubbard's characteristic
sounds using its own internal mechanism, NOT binary compatibility with Hubbard's engine.

### Tables: NO separate wave/pulse/filter/HR/arp tables (all built into instrument)
### Instrument: 7 bytes

```
Byte 0: AD
Byte 1: SR
Byte 2: Waveform (written to Voice+4; direct SID ctrl value)
Byte 3: Pulse width XY  (X = pulsating speed, Y = high nibble start pulse width = Y<<8)
Byte 4: Pulse sweep range
Byte 5: Flags
    $8X  Alternate arpeggio: X = semitones added each arp step
         (requires byte 6 arp properties to be set)
    $40  Dive effect
    $20  Ignore order list transposition
    $10  Add noise in the beginning of note
Byte 6: Arp properties XY  (X = regularity, Y = speed)
```

### Commands: 3 types only
```
0X XX  Slide up   (12-bit speed)
1X XX  Slide down (12-bit speed)
2X -Y  Vibrato    (X = frequency, Y = amplitude)
```

### Key behavioral differences from driver 11 at the SID register level:

**Pulse sweep (built-in, instrument bytes 3-4):**
Unlike driver 11's separate pulse table program, driver 13 implements a built-in
oscillating pulse sweep controlled by the instrument:
- Byte 3 X nibble = pulsating speed (how fast PW oscillates per frame)
- Byte 3 Y nibble = starting PW hi nibble (initial PW = Y << 8)
- Byte 4 = sweep range (how far PW oscillates from the start value)
The pulse sweeps automatically each frame within [start, start ± range].
OPEN: exact oscillation model (triangle wave? sawtooth? bouncing?) needs disasm.

**Alternate arpeggio (flag $8X in byte 5):**
When bit 7 of byte 5 is set, X = semitones to add. Arpeggio cycles based on byte 6:
- X nibble of byte 6 = regularity (how many frames between arp steps)
- Y nibble of byte 6 = speed (arp advancement rate)
OPEN: exact arpeggio cycle model needs disasm. It appears to be a 2-stage arp
(base note alternating with base+X semitones), driven by the regularity and speed
counters. Written to Voice+0/1 each frame.

**Dive effect (flag $40 in byte 5):**
Activates a pitch dive on note start — the frequency slides downward from an initial
higher value to the target note's frequency over several frames.
OPEN: exact dive starting offset, step size, and duration need disasm.

**Add noise at start (flag $10 in byte 5):**
On the first frame of a note, noise waveform ($81 or $80 variant) is written to Voice+4
before switching to the instrument's waveform. This generates a transient noise burst
at note onset (emulating Hubbard's drum hit with noise prefix).
OPEN: exact duration of noise prefix (1 frame? N frames?), exact ctrl byte value, and
whether it's $81 (noise+gate) or $09 (test+gate) need disasm.

**Ignore transpose (flag $20 in byte 5):**
When set, the orderlist transpose byte is NOT added to the note value. The note plays
at its literal sequence pitch regardless of the order list transposition.
Effect: Voice+0/1 frequency computed without the orderlist XX byte contribution.

**No filter control:**
Driver 13 does not write to $D415/$D416/$D417/$D418 filter registers (no filter table).
OPEN: does it write $D418 for main volume? Likely writes init volume from init-equivalent
but no per-frame filter writes.

**No wave table:**
The waveform is a static value from instrument byte 2 (not a per-frame stepping table).
No per-frame waveform changes other than the noise-start flag effect.

---

## Driver 14 — The Experiment (short gate-off variant of driver 11)

"An experimental approach to writing to the SID. It allows for very short durations of gate
off but also has a greater chance of instability."

### Tables: Wave, Pulse, Filter (same format as driver 11)
### Instrument: 6 bytes (same columns as driver 11 BUT different flag bit meanings)

```
Byte 0: AD
Byte 1: SR
Byte 2: Flags
    $80  Enable "immediate response" type hard restart (DIFFERENT from driver 11 HR)
    $40  Start filter program (same as driver 11)
    [bits 4-0: not documented; $10/$20/$08 absent from driver 14 notes]
Byte 3: Filter table index
Byte 4: Pulse table index
Byte 5: Wave table index
```

### Commands: 2 types only (vs driver 11's full command set)
```
00 XX YY  Slide up/down  (XXYY = 16-bit speed; same encoding as driver 11 T0)
01 XX YY  Vibrato        (XX = freq, YY = amplitude; same encoding as driver 11 T1)
```

### Key behavioral differences from driver 11:

**"Immediate response" hard restart ($80):**
The hard restart type is different. Driver 11's HR fires 2 frames before the note;
driver 14's "$80 = immediate response" variant likely fires differently (possibly on
the same frame as gate-off, or with a shorter pre-note window).
The intent is to allow shorter note durations (below driver 11's minimum of 2 frames)
before a new note triggers, at the cost of potential ADSR instability.
OPEN: exact timing of driver 14's HR mechanism needs disasm. Does it write $09 to ctrl
on the same frame as gate-off, immediately before gate-on? Or zero frames before?

**Short gate-off duration:**
The driver is specifically designed for "very short durations of gate off" — implying
the gate is cleared and then re-set within fewer frames than driver 11 normally allows.
This enables rapid percussion hits and staccato effects that driver 11 cannot do cleanly.
The "greater chance of instability" comes from the SID's ADSR hardware potentially not
having enough time to fully reset before the next gate-on.

**No oscillator reset flag ($10):** Not listed in driver 14's instrument flags.
**No filter-enable-per-instrument ($20):** Not listed.
**No skip-pulse-reset ($08):** Not listed.
**No HR table:** Not mentioned; the "immediate response" mechanism does not use an HR table.
**No arpeggio table:** No T3 command in driver 14.
**No ADSR override commands (T8/T9):** Only slide + vibrato available.
**No pulse/tempo/main-vol commands (Tc/Td/Te):** Not listed.

### Wave, Pulse, Filter tables: IDENTICAL format to driver 11
(2-byte wave rows, 3-byte pulse rows, 3-byte filter rows; same encoding)

---

## Driver 15 — Tiny Mark I

"Small driver; variation of driver 12 with a few more effects; zero-page variable storage."

### Tables: Wave only
### Instrument: 5 bytes
```
Byte 0: AD
Byte 1: SR
Byte 2: Pulse width XY  (X = middle 4 bits, Y = top 4 bits of 12-bit PW)
Byte 3: Linear pulse sweep XY  (X = add to mid 4 bits per frame, Y = add to top 4 bits)
Byte 4: Wave table index
```

### Linear pulse sweep (instrument byte 3):
Unlike driver 11's pulse TABLE, driver 15 has a simple per-frame linear add built into
the instrument:
- Each frame: pw_mid_nibble += byte3_X, pw_hi_nibble += byte3_Y (with wrap)
- Written to Voice+2/3 each frame automatically when note is active

### Commands: 4 types (v15.02; earlier versions had 3)
```
0X XX  Slide up   (12-bit speed)
1X XX  Slide down (12-bit speed)
2X -Y  Vibrato    (X = freq, Y = amplitude)
3X YY  [v15.02] Set wave program pointer to YY (wave table index)
```

### Hard restart: ALWAYS ON (not user-configurable per instrument)
Driver 15 always applies hard restart; it is not a per-instrument flag.
v15.00 HR: set SR to $00.
v15.02 HR: set ADSR to $0F $00 (both AD and SR written; more aggressive reset).

### Zero-page variable usage:
All driver state variables live in C64 zero-page RAM (faster 6502 addressing). This
reduces the driver's code footprint at the cost of using ZP addresses (configurable
range specified at pack time).

### Version differences:
- 15.00: Basic, wave programs suspended during HR phase (caused artifacts)
- 15.02: Wave programs run during HR phase; HR uses $0F $00 ADSR; adds 3X command

### SID registers: same as driver 12 (Voice+4 ctrl from wave table; Voice+2/3 from linear
sweep; no filter writes; no arp table)

---

## Driver 16 — Tiny Mark II

"Like driver 15 but with NO commands at all."

### Tables: Wave only
### Instrument: 5 bytes — IDENTICAL to driver 15
```
Byte 0: AD
Byte 1: SR
Byte 2: Pulse width XY  (same as driver 15)
Byte 3: Linear pulse sweep XY  (same as driver 15)
Byte 4: Wave table index
```

### Commands: NONE
All effects are instrument-driven only. No slide, no vibrato, no wave-program command.

### Hard restart: ALWAYS ON (same as driver 15)

### Zero-page variable usage: same as driver 15

### SID register behavior: identical to driver 15 except without command-driven effects

---

## Feature Matrix by Driver

| Feature                        | D11  | D12  | D13  | D14  | D15  | D16  |
|-------------------------------|------|------|------|------|------|------|
| Wave table                    | YES  | NO*  | NO*  | YES  | YES  | YES  |
| Pulse table                   | YES  | NO   | NO   | YES  | NO   | NO   |
| Filter table                  | YES  | NO   | NO   | YES  | NO   | NO   |
| HR table (user-configurable)  | YES  | NO   | NO   | NO** | NO   | NO   |
| HR always-on                  | NO   | NO   | NO   | NO   | YES  | YES  |
| Arpeggio table                | YES  | NO   | NO   | NO   | NO   | NO   |
| Tempo table                   | YES  | NO   | NO   | NO   | NO   | NO   |
| Init table                    | YES  | NO   | NO   | NO   | NO   | NO   |
| Slide (T0/0X)                 | YES  | YES  | YES  | YES  | YES  | NO   |
| Vibrato (T1/2X)               | YES  | YES  | YES  | YES  | YES  | NO   |
| Portamento (T2)               | YES  | NO   | NO   | NO   | NO   | NO   |
| Arpeggio command (T3)         | YES  | NO   | NO   | NO   | NO   | NO   |
| Fret slide (T4)               | 11.01-11.04 | NO | NO | NO | NO | NO |
| ADSR override (T8/T9)         | YES  | NO   | NO   | NO   | NO   | NO   |
| Filter cmd (Ta)               | YES  | NO   | NO   | NO   | NO   | NO   |
| Wave cmd (Tb)                 | YES  | NO   | NO   | NO   | NO   | NO   |
| Pulse cmd (Tc)                | 11.02+ | NO | NO | NO   | NO   | NO   |
| Tempo cmd (Td)                | 11.02+ | NO | NO | NO   | NO   | NO   |
| Main vol cmd (Te)             | 11.02+ | NO | NO | NO   | NO   | NO   |
| Note delay                    | 11.04+ | NO | NO | NO   | NO   | NO   |
| Wave cmd (3X)                 | NO   | NO   | NO   | NO   | 15.02+ | NO |
| Built-in arp (instrument)     | NO   | NO   | YES  | NO   | NO   | NO   |
| Built-in pulse sweep (inst)   | NO   | YES  | YES  | NO   | YES  | YES  |
| Linear pulse sweep (inst)     | NO   | NO   | NO   | NO   | YES  | YES  |
| Dive effect (instrument)      | NO   | NO   | YES  | NO   | NO   | NO   |
| Noise-on-attack (instrument)  | NO   | NO   | YES  | NO   | NO   | NO   |
| Ignore-transpose (instrument) | NO   | NO   | YES  | NO   | NO   | NO   |
| Filter per-instrument ($20)   | 11.03+ | NO | NO | NO   | NO   | NO   |
| Skip pulse reset ($08)        | 11.05+ | NO | NO | NO   | NO   | NO   |
| Multispeed / CIA timer        | NO   | NO   | NO   | NO   | NO   | NO   |
| Zero-page vars                | NO   | NO   | NO   | NO   | YES  | YES  |
| $D418 filter writes           | YES  | NO   | NO?  | YES  | NO   | NO   |
| $D415/$D416 writes            | YES  | NO   | NO   | YES  | NO   | NO   |
| $D417 writes                  | YES  | NO   | NO   | YES  | NO   | NO   |

*D12/D13 use static waveform byte in instrument, not a per-frame stepping table.
**D14's HR is "immediate response" type — no user-selectable HR table; behavior OPEN.

---

## Driver 11 Sub-version Detection

To distinguish driver 11 sub-versions in HVSC SID files, use the descriptor block:
- Block 1 (Descriptor): `version_major` = 11, `version_minor` = 0/1/2/3/4/5
- OR: Check behavioral features:
  - No T4 command rows in any pattern + HR table size = 8 → must be ≥ 11.05
  - Has T4 command rows → 11.01–11.04
  - Has Tc/Td/Te command types → ≥ 11.02
  - Instrument byte 2 has $20 bits set → ≥ 11.03
  - Note rows have high nibble > 0 → ≥ 11.04
  - HR table has 16 rows → ≤ 11.04; 8 rows → 11.05

---

## Multispeed — Not Implemented

The SF2 FAQ (faq.txt) explicitly lists "Multispeed" as a planned future feature not yet
available. All SF2 drivers operate at single-speed: the `update` routine is called once
per VBI frame (50 Hz PAL, 60 Hz NTSC). There is no CIA-timer multispeed in any current
driver. SF2 tunes in HVSC will always have PSID speed=0 (VBI only).

---

## Leads to follow

- **OPEN: Driver 13 internal pulse sweep model** — exact oscillation model (triangle? bounce?).
  Disassemble `sf2driver13_00.prg` and locate the per-frame pulse update routine.
- **OPEN: Driver 13 alternate arpeggio model** — how do "regularity" (byte 6 X) and "speed"
  (byte 6 Y) interact? Confirm 2-stage arp vs multi-stage.
- **OPEN: Driver 13 dive effect** — starting freq offset, step size, duration. Disasm needed.
- **OPEN: Driver 13 noise-at-start** — how many frames? What ctrl byte is written ($81/$80/$09)?
- **OPEN: Driver 14 "immediate response" HR** — exact frame when HR writes $09 + HR ADSR to SID.
  Is it frame 0 (same frame as gate-off) or frame -1 (one frame before new note)?
- **OPEN: Driver 14 stability issues** — does the driver write gate-off and gate-on in the
  SAME frame to the SID chip (both in one update cycle)? This would be the "short gate-off."
  Disasm the driver 14 update routine to find the exact write sequence.
- **OPEN: Driver 15 linear sweep wraparound** — does pw_mid_nibble overflow affect pw_hi_nibble
  (i.e., carry propagates)? Or each nibble wraps independently?
- **OPEN: Driver 13 filter behavior** — does driver 13 ever write to $D415–$D418? The notes
  don't mention a filter table or filter command. Confirm by disasm or siddump capture.
- **OPEN: SIDID patterns** — the fingerprints used by sidid/HVSC to classify SF2 tunes by
  driver version. Check `github_sidid_fingerprints.md` in docs/.
- **Per-driver .prg disassembly** — all behavioral OPENs above resolve from disassembling
  the .prg files in `SIDFactoryII/drivers/`. The driver_info descriptor block at load_address
  gives driver_code_top and driver_code_size; disassemble that range with the xa65 disassembler
  or py65 single-step trace via siddump --pc-trace on a driver 13/14 test SID.
