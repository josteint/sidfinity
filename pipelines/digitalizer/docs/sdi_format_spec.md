---
source_url: https://master.dl.sourceforge.net/project/sidduzzit/SDI.2.1.6-docs.txt (primary); https://sourceforge.net/projects/sidduzzit/files/ (file listing); http://chordian.net/c64editors.htm (comparison table); https://www.lemon64.com/forum/viewtopic.php?t=24039 (forum); https://www.lemon64.com/forum/viewtopic.php?t=31585 (forum)
fetched_via: direct (WebFetch chain through SourceForge redirects)
fetch_date: 2026-06-13
author: Geir Tjelta (GT) and Glenn Rune Gallefoss (6R6/GRG) of SHAPE
content_date: SDI v2.1.6 docs (2013-05-18), v2.1.7 release notes (2014-10-12)
reliability: primary (SDI 2.1.6 manual), secondary (comparison table cells, forum posts)
---

# SID Duzz' It (SDI) v2.1 — Format Specification

SID Duzz' It (SDI) is a C64 music tracker/editor by Geir Tjelta (GT) and Glenn Rune
Gallefoss (6R6/GRG) of SHAPE, released 2001–2014. The SDI documentation explicitly
states: "SID Duzz' It is built on ideas from JCH/Vibrants editor, Olav
Morkrid/Panoramic 'Digitalizer' editor and Geir Tjelta/Shape/Moz(ic)art 'SID Systems."
This makes SDI the best available proxy for understanding the Digitalizer format.

All values in this document are hexadecimal unless otherwise stated.

---

## Overview / Capabilities

| Parameter | Value |
|-----------|-------|
| Voices | 3 music + 1 control (Ch4 = tempo/transpose/filter) |
| Sub-tunes | 32 |
| Sequences | 128 (each up to $7F = 127 rows max; $00 = 1 row min) |
| Instruments | 32 (+ 16 via arpeggio = 48 effective) |
| Arpeggios | 48 (arpeggio programs, 0–47) |
| Vibrato programs | 85 |
| Pulse programs | 64 |
| Filter programs | 64 |
| Tempo programs | 48 |
| SID chips | 1 (separate digi version exists) |
| PAL/NTSC | Both supported (frequency table selectable) |
| Player size | < 2400 bytes |
| Zero page | 2 bytes (defined in assembler source) |
| CPU time (1x) | ~24–27 rasterlines |
| Speeds | 1x to 16x (multi-speed) |

---

## Memory Map (editor RAM layout)

All addresses are the editor's C64 RAM layout. The compiled player is re-based; see
"Player Entry Points" below.

| Address range | Contents |
|--------------|---------|
| $0100–$017F | Stack |
| $0180–$0200 | Sequence lengths (128 × 1 byte) |
| $3000–$3800 | Track 1 data (2 KB) |
| $3800–$4000 | Track 2 data (2 KB) |
| $4000–$4800 | Track 3 data (2 KB) |
| $4800–$5000 | Track 4 data (control channel; 2 KB) |
| $5000–$D000 | Sequence data (32 KB for 128 sequences) |
| $D000–$D810 | Directory (max 128 files) |
| $E000–$E100 | Waveform program bytecodes (256 bytes; see §Waveform Programs) |
| $E100–$E200 | Waveform note values (256 bytes; parallel array to $E000) |
| $E200–$E300 | Pulse programs (256 bytes; 64 programs × 4 bytes each) |
| $E300–$E400 | Arpeggio data (256 bytes) |
| $E400–$E500 | Arpeggio programs (256 bytes) |
| $E500–$E600 | Vibrato programs (256 bytes) |
| $E600–$E700 | Filter programs (256 bytes; 64 programs × 4 bytes each) |
| $E700–$E8E0 | Sound/instrument setup tables (448 bytes = 10 tables × 32 entries, explained below) |
| $E980–$EA00 | Tempo data |
| $EA00–$ED00 | Sound names (32 instruments × up to $18 bytes ASCII) |
| $EE00–$EEC0 | Note frequency table (PAL-tuned; 96 entries) |

### Instrument/Sound setup table layout ($E700–$E8E0)

The 10 instrument parameters are stored as PARALLEL arrays (not records). Each array
has 32 entries (indices $00–$1F for 32 instruments, plus $10 extra via arpeggio path
= 48 maximum). Array stride = 32 bytes per field = $20 bytes.

The comparison table confirms: "10 bytes per instrument (effective span across regions)."

| Base address | Array | Values |
|-------------|-------|--------|
| $E700–$E72F | Waveform program pointer | $01–$55 (pointer into $E000 table) |
| $E730–$E75F | Attack/Decay | $00–$FF (high nibble=attack, low=decay) |
| $E760–$E78F | Sustain/Release | $00–$FF (high nibble=sustain, low=release) |
| $E790–$E7BF | Gate timeout (hard/soft restart) | $00–$FF (see §Gate Timeout) |
| $E7C0–$E7EF | Vibrato program pointer | $00=none, $01–$55=programs |
| $E7F0–$E81F | Pulse program pointer | $00=none, $01–$40=normal, $41–$80=infinite |
| $E820–$E84F | Filter program pointer | $00=none, $01–$40=normal, $41–$80+ sweep modes |
| $E850–$E87F | Band/Resonance | $00=no filter; see §Band/Resonance |
| $E880–$E8AF | Detune Hi | $00–$FF (signed frequency offset high byte) |
| $E8B0–$E8DF | Detune Lo | $00–$FF (signed frequency offset low byte) |

---

## Instrument / Sound Editor Fields

The sound editor screen displays 10 parameters for each instrument. Example layout
from the manual:

```
05 WAVEFORM PRG
08 ATTACK/DECAY
7D SUST/RELEASE
20 GATE TIMEOUT
08 VIBRATO  PRG
02 PULSE    PRG
01 FILTER   PRG
1F BAND/RESONANS
00 DETUNE HI
00 DETUNE LO
```

### Field details

**WAVEFORM PRG** ($01–$55)
Pointer into the Waveform program table at $E000. The waveform program controls which
SID voice-control byte ($D404/$D40B/$D412) is written per tick, including the gate bit,
and can embed note offsets for arpeggio-like effects.

**ATTACK/DECAY** ($00–$FF)
Written to SID $D405/$D40C/$D413. High nibble = Attack (0–15), low nibble = Decay
(0–15). OPEN: Glenn Gallefoss stated in the Chordian comparison thread that SDI
"cannot set Decay" — this suggests the Decay nibble may be fixed in some contexts.

**SUST/RELEASE** ($00–$FF)
Written to SID $D406/$D40D/$D414. High nibble = Sustain (0–15), low nibble = Release
(0–15).

**GATE TIMEOUT** ($00–$FF)
Controls the gate-off timing and restart behaviour. See §Gate Timeout below.

**VIBRATO PRG** ($00=none, $01–$55)
Pointer to the vibrato program at $E500. $00 means no vibrato.

**PULSE PRG** ($00=none, $01–$40=normal, $41–$80=infinite)
Pointer to the pulse program at $E200. $00 = no pulse program. $01–$40 = 64 programs
(each runs once). $41–$80 = same 64 programs but run continuously (infinite loop).
$80 = special "inherit from other channel" flag (do not route to a program line).

**FILTER PRG** ($00=none, $01–$40=normal, $41–$80+ sweep modes)
Pointer to the filter program at $E600. Same structure as PULSE PRG. Additional modes
above $40 enable different sweep behaviours.

**BAND/RESONANCE** ($00–$FF; $00 = no filter)
Encodes SID filter routing and resonance. $00 = filter completely off for this
instrument. Non-zero value: suggested mapping (OPEN — needs RE to confirm exact bit
layout) is high nibble = resonance (SID $D417 bits 4–7), low nibble = filter channel
routing (SID $D418 bits 4–6 for voice 1/2/3 filter enable). Value $1F in the manual
example.

**DETUNE HI / DETUNE LO** ($00–$FF each)
A 16-bit signed frequency offset added to the base note frequency. Used for chorus,
detuning, or precise pitch adjustment independent of arpeggio.

---

## Gate Timeout / Hard Restart Field

The gate timeout byte encodes TWO things: (1) how many frames before the gate-off
is triggered after note-on, and (2) which "restart" mode to use when the next note
fires.

| Byte range | Timeout duration | Restart type |
|-----------|-----------------|-------------|
| $00, $20, $40, $60, $80, $A0, $C0, $E0 | None (immediate) | See bits 6–5 |
| $01–$1F | 1–31 frames | Hard restart 1 (normal) |
| $21–$3F | 1–31 frames | Hard restart 2 |
| $41–$5F | 1–31 frames | Hard restart 3 |
| $61–$7F | 1–31 frames | Hard restart 4 |
| $81–$9F | 1–31 frames | Soft restart 1 |
| $A1–$BF | 1–31 frames | Soft restart 2 |
| $C1–$DF | 1–31 frames | Soft restart 3 |
| $E1–$FF | 1–31 frames | Soft restart 4 (≈ tie note) |

Lower 5 bits = timeout duration (0 = no wait; 1–$1F = frames 1–31).
Bits 6–5 = restart type (0=hard1, 1=hard2, 2=hard3, 3=hard4 when bit7=0;
                          0=soft1, 1=soft2, 2=soft3, 3=soft4 when bit7=1).
OPEN: Exact SID-register-write sequence for each restart type needs RE.

---

## Waveform Program

One program per instrument pointer. Programs are stored at $E000 (command bytes) and
$E100 (note values), as parallel arrays.

Each program line = 2 bytes: command byte at $E000+n and note byte at $E100+n.

### Command byte (waveform byte) values

| Bits | Meaning |
|------|---------|
| $10 | Triangle waveform (SID voice ctrl bit 4) |
| $20 | Sawtooth waveform (SID voice ctrl bit 5) |
| $40 | Pulse waveform (SID voice ctrl bit 6) |
| $80 | Noise waveform (SID voice ctrl bit 7) |
| $30 | Triangle + Sawtooth combined |
| $60 | Pulse + Sawtooth combined |
| $70 | Pulse + Sawtooth + Triangle combined |
| Combined waveforms note | "Works best on new SIDs ($8580)" |
| +$01 | Gate ON (SID voice ctrl bit 0) — add to any waveform above |
| $00 | Gate off (no waveform set) |
| $91–$E1 | Special arpeggio waveform values (see §Arpeggio Program) |

### Note byte ($E100+n) values

| Byte range | Meaning |
|-----------|---------|
| $00–$5F | "Soft" upward: offset ADDED to current note + track transpose |
| $60–$7F | "Soft" downward: offset SUBTRACTED from note + track transpose |
| $80–$DE | "Fixed" note: overrides sequence note + transpose entirely |
| $DF–$FF | Reserved (unused in v2.1) |

The note byte interacts with SID registers $D400/$D401/$D407/$D408/$D40E/$D40F
(voice frequency lo/hi for each of 3 voices). OPEN: whether "soft" offsets apply
to the note number (semitones) or directly to the 16-bit SID frequency value.

### Waveform program command bytes (special control codes)

These appear in the command-byte array at $E000, NOT as waveform values:

| Code | Name | Format | Action |
|------|------|--------|--------|
| $FF | Jump | `FF XX` | Jump to program line $XX |
| $FE | Delay | `FE XX` | Wait $XX frames, then continue |
| $FD | ADSR | `FD XX` / (next line: AD SR) | Set new ADSR; XX=timeout: $01–$7F=gate off after XX frames; $00/$80=no wait; $81–$FF=gate off, no restart. Two-line command. |
| $FC | Drum | — | Unsupported in SDI v2.x (reserved for Digitalizer-inherited feature) |
| $FB | Multipulse | `FB P2` / (next: `0X YY`) | Switch between two pulse programs. P2=second program#; X=start mode (0 or 1); YY=switch speed. Two-line. |
| $FA | Repeat | `FA XX` | Execute the following `FF` jump $XX times before continuing |
| $F0–$F7 | D415 low bits | `FX` (1 byte) | Write F0–F7 directly to SID $D415 (filter cutoff low byte; sets lower 3 bits) |
| $EE | Pulse Init | `EE` + parameter | Write pulse lo|hi to SID $D402/$D403 (or equivalent per voice) |
| $ED | Pulse Subtract | `ED XX` | Subtract $XX from current pulse value |
| $EC | Pulse Add | `EC XX` | Add $XX to current pulse value |
| $EB | Pulse Write | `EB` + param | Write lo|hi pulse directly to pulse registers only |
| $E2–$E7 | Noise trick | `Ex YY` | Write $Ex to voice waveform register (metallic noise variants) |

**11-bit filter:** The combination of `$F0–$F7` (sets $D415 bits 0–2) plus the filter
program (which writes $D416 hi byte) enables full 11-bit filter cutoff control.

---

## Vibrato Program

Programs stored at $E500. 85 programs available.

Each program line has 4 columns:

| Column | Name | Values | Meaning |
|--------|------|--------|---------|
| c1 | Program line# / pointer | $00–$54 | Program index |
| c2 | Delay/mode | $00, $01–$FD, $FE, $FF | Control byte (see below) |
| c3 | Vibrato width | $00–$7F, $80–$FF | $00–$7F = oscillate up-then-down; $80–$FF = oscillate down-then-up |
| c4 | Vibrato speed | $00–$FF | Speed of oscillation per frame |

**c2 control byte:**
- $00 = Apply detuning (c3/c4 as DL/DH frequency offset pair), continue to next line
- $01–$FD = Delay: wait this many frames before the effect fires
- $FE = Apply detuning and hold (no further lines executed)
- $FF = Infinite loop marker (vibrato program repeats from here)

"Detuning" uses c3/c4 as a 16-bit detune value (low byte / high byte), producing a
static frequency offset rather than oscillation. Combining detuning and vibrato is
possible in the same program via separate lines.

---

## Pulse Program

64 programs stored at $E200. Each program = 4 bytes (c2–c5 = columns 2–5).
Programs are accessed by instrument pointer.

| Column | Name | Values | Meaning |
|--------|------|--------|---------|
| c1 | Program line# | — | Internal reference |
| c2 | Start value (lo\|hi) | $00–$FF | Starting pulse low + high byte pair |
| c3 | Target/sweep value | $00–$FF | Target pulse hi byte (or range endpoint) |
| c4 | Sweep speed | $00–$FF | Amount added per frame step |
| c5 | Mode/jump | $00–$FF | Sweep direction and loop behaviour (see below) |

**c5 sweep mode bits:**

| c5 range | Mode | Behaviour |
|---------|------|-----------|
| $00, $40, $80, $C0 | Stop | Sweep to target, then stop |
| $01–$3F | Cut | Sweep to target, then cut back to c2 start; low nibble = jump target line |
| $41–$7F | Continuous | Continuous sweep between c3 values; if low nibble matches current line = loop |
| $81–$BF | Reverse cut | Like $01–$3F but reversed direction |
| $C1–$FF | Reverse continuous | Like $41–$7F but reversed |

Sweep direction is determined by comparing c3 vs c2; if c3 < c2 the sweep is downward.
Pulse programs write to SID $D402/$D403/$D409/$D40A/$D410/$D411 (pulse lo/hi per voice).

**Pulse hold:** Normal programs run once; $41–$80 pointer range = infinite (hold the
last pulse state indefinitely after the program completes its sweep).

---

## Filter Program

64 programs stored at $E600. Structure identical to Pulse Program EXCEPT:

**Exception 1:** Column c2 bytes are stored HIGH byte first, then LOW byte (reversed vs
pulse; pulse is lo|hi order, filter is hi|lo).

**Exception 2:** No pulse-hold routine. The "infinite" pointer flag ($41–$80) behaves
differently.

**Exception 3:** When c3 = $00, the "filter frame routine" mode activates:
- c2 = cutoff hi byte written directly to SID $D416
- c4 = band/resonance value written to SID $D417
- c5 = frame delay (1 or 2 frames) before advancing to next line

In normal mode (c3 ≠ 0), filter program sweeps SID $D416 (cutoff hi) while $D415
can be set separately via waveform `$F0–$F7` commands for 11-bit precision.

---

## Arpeggio Program

48 arpeggios stored at $E300 (data) and $E400 (programs).

Arpeggios in SDI work through the waveform program via special waveform bytes
$91/$A1/$B1/$C1/$D1/$E1 (see §Waveform Program). These values trigger the arpeggio
engine. The exact waveform-to-SID-register mapping:

| Waveform byte | Equivalent base | SID voice ctrl value |
|--------------|----------------|---------------------|
| $91 | $11 + arp bit | Triangle + gate ($10 + $01) |
| $A1 | $21 + arp bit | Sawtooth + gate ($20 + $01) |
| $B1 | $31 + arp bit | Triangle + Sawtooth + gate |
| $C1 | $41 + arp bit | Pulse + gate |
| $D1 | $51 + arp bit | Pulse + Triangle + gate |
| $E1 | $61 + arp bit | Pulse + Sawtooth + gate |

**Arpeggio program column 4 encoding (speed/sound byte):**
The speed/sound byte combines instrument selection and arpeggio speed:
```
speed_byte = (speed * $10) + instrument_low_nibble
Example: $D5 = speed=$D (decimal 13? or speed-level 4?), instrument=$5
Example: $15 = speed=$1 (level 1), instrument=$5
```
OPEN: The manual states $D5 = "speed 4, instrument $15" but $D hex ≠ 4 decimal.
Likely speed is encoded as a 4-bit value mapped non-linearly to frame counts.

Arpeggio data values ≥ $80 act as loop markers. Values < $80 are note offsets applied
to the base note. OPEN: whether these are semitone offsets or raw frequency offsets.

**Arpeggio count in sequencer:** Arpeggios referenced via FX codes $40–$6F (48
possible arpeggio slots, 0–$2F mapped through $40 base).

---

## Tempo Program

48 programs stored at $E980–$EA00. Each program = multi-byte sequence.

| Column | Values | Meaning |
|--------|--------|---------|
| c1 | Program line# / tempo# | Index |
| c2 | Tempo value | $01–$7F = normal speed; $81–$FF = same but marks loop point |
| c3 | Program pointer | Forward reference |

Do NOT use values $00 or $80 — "will not work with the final player."

Tempo represents frames-per-step (lower value = faster). OPEN: whether the tempo
value is a direct rasterline count or a divide factor.

---

## Initial Volume (INVOL)

Per-tune volume configuration (accessed via SHIFT+I). 32 entries (one per tune).

| Column | Encoding | Meaning |
|--------|----------|---------|
| c1 | $00–$1F | Tune number |
| c2 high nibble | $0–$F ($0=none) | Fade-in speed ($1=fastest, $F=slowest) |
| c2 low nibble | $0–$F | Starting volume (SID $D418 low nibble) |
| c3 high nibble | $0–$7 | Filter channel forcing (bitmask: bit0=ch1, bit1=ch2, bit2=ch3) |
| c3 low nibble | $0–$F | Filter speed delay |

---

## Sequence Format

128 sequences. Each stored in $5000–$D000. Max 127 rows per sequence ($7F); min 1 row.
Sequence lengths stored at $0180–$01FF.

Each sequence row = 2 bytes:
- Byte 0: FX column (see §Sequencer FX Commands)
- Byte 1: NOTE column (note value or command parameter)

**NOTE byte values (for normal note entry):**
Notes range from C-0 to A#7. Uppercase note = gate restart (programs restart).
Lowercase note = tie note (no gate restart, programs continue). Special values:
- `GAT` / `-- GAT` = gate event only, no note change
- `-- ---` = empty row (no change)

---

## Sequencer FX Commands — Channels 1–3

| FX value | Function | Note column meaning |
|---------|---------|---------------------|
| $00–$1F | Set instrument | Instrument number embedded; NOTE plays with that instrument |
| $20 | Filter on/off | Note = ON or OFF parameter for this channel's filter routing |
| $21–$3F | Set glide | Glide speed in FX; NOTE = target pitch to glide toward |
| $40–$6F | Set arpeggio | Arpeggio# ($00–$2F) via FX−$40; NOTE = base pitch (optional) |
| $70–$7F | Release/Sustain/Attack | Modify envelope parameters; NOTE = parameter |
| $80–$FF | Not documented (presumably unused in v2.1) | — |

Instrument numbers $00–$1F in the FX column are used WITHOUT a separate "instrument
select" code — the FX column IS the instrument selector when in range $00–$1F.

**Tie notes:** A note in lowercase (brown background in editor) sets NOTE without
restarting programs, gate, or arpeggio. Allows held notes and legato.

**"-- GAT":** Triggers a gate event (gate on/off) without changing the frequency.

---

## Sequencer FX Commands — Channel 4 (Control Channel)

Channel 4 controls global tempo, transpose, and filter.

| FX value | Function | Note column meaning |
|---------|---------|---------------------|
| $00 | Empty | No change |
| $01–$1F | Set tempo | NOTE = transpose value (C-0 to A#7 for +/- transposition) |
| $21–$3F | Force filter program | Force specific filter program globally; NOTE = transpose |
| $40–$60 | Look up tempo program | Tempo program pointer; NOTE = transpose |
| $61–$67 | Force filter band | Override filter band; NOTE = specific band value |
| $68–$6F | Future expansion | Reserved |
| $70 | Filter control to main | Return filter control to per-instrument assignments |
| $71–$7F | Force filter output | Enable filter on specific channels |
| Others | Not documented | — |

Channel 4 should start with `-- GAT` (gate event, no transpose) to initialize.
Avoid transpose values outside C-0 to C-2 range.

---

## Tracker Format (Track Editor)

The tracker defines song structure: each track is a sequence of steps.
Each tracker line = 2 fields:
- Transpose byte ($00–$7F for different transpose amounts; negative via upper values)
- Sequence number ($00–$7F = sequence 0–127)

Track data at $3000–$4FFF (4 tracks × 2 KB each).
Track jump: last track line contains `J0xx` (jump to tracker position $xx).
Loop is set by `R` (restart bar marker). Stop by `S` (stop marker).
`*` key switches "track bank" — implies multiple track banks exist for longer songs.

---

## Sequence Size Reference

From the manual's explicit table:
- Minimum: $00 = 1 row (empty/silent)
- Maximum: $7F = 127 rows
- Common lengths: $10 (16), $20 (32), $40 (64) rows

---

## Compiled Player Entry Points

When music is exported (dump → Turbo Assembler → assemble), the player loads at $1000
by default.

| Address | Function | Register use |
|---------|---------|-------------|
| $1000 | Init (select tune) | X = tune number $00–$1F |
| $1003 | Play (main, tracks + sequences + sounds) | — |
| $1006 | Fade out | A = fade level $00–$7F |
| $1009 | Speed play (sound update only, no track advance) | — |

**PAL IRQ setup for speed N:**
```
raster_interval = 312 / N  (scanlines between play calls)
```
One main call ($1003) + (N−1) speed calls ($1009) per 312-scanline frame.
NTSC: use 262 instead of 312.

**Player size:** < 2400 bytes. Source code: `s.sdi21-n49` (normal) or `s.sdi21-spd49`
(speed variant).

---

## File Save / Dump

**SAVE (SH+S):** Stores the complete SDI project file in compressed format. The
"bytepacker" compresses memory ranges $3000–$D000 and $E000–$EE00. File size ~5–60
blocks (1 block = 254 bytes on C64). Preserves all data including unused sequences.
OPEN: exact file header format not documented in the manual.

**DUMP (c=+S):** Exports only the sequences actually in use (channels that are ON).
Outputs as Turbo Assembler sequential (.seq) file format. File size ~5–120 blocks.
The dump is loaded into Turbo Assembler alongside the player source and then assembled
into a binary. **OPEN: byte-level format of the .seq dump is undocumented in the manual.**

---

## Note Frequency Table

Stored at $EE00–$EEC0. Tuned for PAL (985,248 Hz clock). Alternative NTSC table
available as separate source file. Range: C#0 (lowest) to A#7 (highest) = ~96 notes.

From the note table documentation:
- Values $00–$5F in waveform note column = upward offsets from current sequence note
  (C-0 base = $00, steps up by semitone to C-7 = $5F)
- Values $60–$7F = downward offsets (C-3 base = $60, stepping down to $7F)
- Values $80–$DF = fixed notes (C-0 = $80 upward through A#7 = ~$DF)
- Values $E0–$FF = reserved (future expansion)

---

## Memory Optimisation Tricks (from manual)

1. **Sequence reuse**: Use the same sequence number in multiple tracker positions
   instead of duplicating note patterns.
2. **Selective instrument assignment**: Only put instrument FX ($00–$1F) in FX column
   when changing instruments — save 1–2 bytes per note row.
3. **Tie emulation**: Use gate-timeout instruments with $80 pulse pointer (infinite)
   instead of explicit tie notes — smaller sequence data.
4. **Arpeggio instead of waveform table**: Arpeggio programs can replace complex
   waveform programs for chord-like effects.
5. **Pulse manual control**: Use $EB–$EE waveform commands instead of a pulse program
   for simple one-shot pulse shapes.
6. **Filter trick**: Set FILTER PRG = $80 + BAND/RESONANCE = $00 on non-filter channels
   to suppress filter routing without wasting a filter program slot.

---

## Known Issues (from manual)

- A sequence of length $7F filled entirely with tie notes may cause dump overflow
  beyond the 256-byte limit per channel. Workaround: keep tie sequences shorter.
- Version 2.1.7 fixes: filter cutoff fast-downward subtraction routine; gate timeout
  with values $Ax/$Cx/$Ex preventing initial note from sounding.

---

## Leads to follow

- OPEN: Exact byte-level format of the SAVE file (after bytepacker decompression).
  The packed $3000–$D000 and $E000–$EE00 ranges are the full song data; decompressor
  is in the editor binary. No documentation of the bytepacker algorithm.
- OPEN: Exact byte-level format of the DUMP (.seq) file. Critical for understanding
  how SDI data is serialised and potentially mapping back to Digitalizer.
- OPEN: The "10 bytes per instrument" (from comparison table) is confirmed structurally
  (10 parallel arrays × 1 byte each), but the comparison table says this is per-
  instrument in the compiled player — confirm via RE of player source.
- OPEN: Decay "cannot be set" (per Glenn's comment in chordian table) — is the Decay
  nibble of the Attack/Decay byte always zero, or is there a separate mechanism?
- OPEN: The Arpeggio speed encoding ($D5 = "speed 4, instrument $15") — the hex digit
  $D ≠ decimal 4. Either the speed nibble maps non-linearly, or the documentation
  example has a typo. Needs RE of player source to resolve.
- OPEN: The "Restart types" (hard restart 1–4, soft restart 1–4) — what SID register
  writes do they produce? E.g., hard restart likely writes $00 to $D404 then the new
  waveform+gate; soft restart may only write the new waveform without clearing ADSR.
- OPEN: Glide effect SID register target per frame — which register is written and
  what is the delta formula?
- OPEN: The filter channel 4 FX $21–$3F overlaps with glide in channels 1–3. The
  documentation lists both; likely the interpreter is context-sensitive per channel.
- OPEN: "Separate digi version" of SDI — what features does it add/remove? Does it
  share the same instrument format?
- SOURCE TO FETCH: SDI player source files (`s.sdi21-n49`, `s.sdi21-spd49`) from the
  Turbo Assembler disk inside the SDI distribution ZIP. These are the definitive
  reference for player-level behaviour.
- SOURCE TO FETCH: SDI 2.1.7 PDF manual (psylicium.dk) — includes revised arpeggio
  chapter; fetch URL: https://psylicium.dk (or CSDb mirror at release ID 153760).
- SOURCE TO FETCH: DTZ2SDI converter disk image
  (csdb.dk/getinternalfile.php/251569/digitalizer_v3x_to_sdi_converter_v20_shape.zip)
  — contains a C64 .d64 disk image. Extract with vice/D64 tools and read the PETSCII
  help text or source code to identify the field mapping from Digitalizer to SDI.
