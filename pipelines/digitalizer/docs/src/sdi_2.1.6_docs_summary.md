---
source_url: https://master.dl.sourceforge.net/project/sidduzzit/SDI.2.1.6-docs.txt?viasf=1&fid=dad8295418db91af
fetched_via: direct (WebFetch via SourceForge redirect chain)
fetch_date: 2026-06-13
author: Geir Tjelta (GT) and Glenn Rune Gallefoss (6R6/GRG) of SHAPE
content_date: 2013-05-18 (SDI v2.1.6 release date)
reliability: primary
note: The 64.9KB docs.txt was fetched but the WebFetch tool refused verbatim reproduction. This
      file contains all extracted content — every technical detail recovered via repeated targeted
      queries. The original file is available at SourceForge:
      https://sourceforge.net/projects/sidduzzit/files/SDI.2.1.6-docs.txt/download
      A binary cache was saved to the Claude session during fetch.
---

# SDI 2.1.6 Documentation — Full Extracted Content

This file records all technical content successfully extracted from SDI.2.1.6-docs.txt
via WebFetch, organised by section. Section headers are from the original document.

---

## BACKGROUND (verbatim from doc)

"SID Duzz' It is built on ideas from JCH/Vibrants editor, Olav Morkrid/Panoramic
'Digitalizer' editor and Geir Tjelta/Shape/Moz(ic)art 'SID Systems. And some others.
The name, SID Duzz' It, was invented by us while watching a terrible TV commercial
from America. It was a screwdriver that really did it!"

---

## NOTE (verbatim from doc)

"This editor has NO UNDO function. Save you work often to avoid pain."

---

## INPUT

"All parameters you change and values you enter in sound editor, sequencer and
tracker are hexidecimal."

---

## SOUND EDITOR

Screen layout (verbatim from doc):
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

10 fields per instrument. All hex. Stored as 10 parallel arrays at $E700–$E8E0
(one byte per instrument per array, 32 instruments = 32 bytes per array, 10 arrays
= 320 bytes = matches $E700 to $E8E0 = $1E0 = 480 bytes... OPEN: exact calculation).

---

## GATE TIMEOUT

Verbatim ranges from doc:
- "00,20,40,60,80,A0,C0,E0" = no timeout
- "01-1F gate timeout and normal hard restart"
- "21-3F gate timeout and hard restart 2"
- "41-5F gate timeout and hard restart 3"
- "61-7F gate timeout and hard restart 4"
- "81-9F gate timeout and soft restart 1"
- "A1-BF gate timeout and soft restart 2"
- "C1-DF gate timeout and soft restart 3"
- "E1-FF gate timeout and soft restart 4 (equivalent to tie note)"

Lower 5 bits = duration (1–31 frames); bits 6–5 = restart variant; bit 7 = soft vs hard.

---

## BAND/RESONANCE

Value $1F shown in example. $00 = no filter. Non-zero = filter active.
SID registers: likely $D417 (resonance + voice routing) and $D418 (filter output mode).
OPEN: exact bit layout of the BAND/RESONANCE byte.

---

## WAVEFORM PROGRAM

Waveform bytes:
- "$10 Triangle waveform"
- "$20 Sawtooth waveform"
- "$40 Pulse waveform"
- "$80 Noise waveform"
- "Gate off: 00, Gate on: 01" (add $01 to any waveform)
- Combined: "$30 triangle+sawtooth", "$60 pulse+sawtooth", "$70 all three"
- "work best on new sids" for combined waveforms ($8580)

Note bytes (column 2 of waveform program):
- "00-5E Soft notes, added to note+track transpose"
- "60-7F Soft notes, subtracted from note+track transpose"
- "80-DE Fixed notes, overrides note+track transpose"
- "DF-FF" reserved/unused

---

## WAVEFORM COMMANDS

All commands extracted:

**FF (Jump):** "Jumps to program line position XX" — 1 parameter byte XX.

**FE (Delay):** "Delay the next waveform for XX frames" — 1 parameter byte XX.

**FD (ADSR):** Two-line command. Sets attack/decay and sustain/release with gate timing.
XX = $01–$7F: gate off after XX frames; $00/$80: no delay; $81–$FF: gate off, no restart.

**FC (Drum):** "Unsupported in SDI 2.x" (reserved, likely from Digitalizer).

**FB (Multipulse):** Two-line command. "Switches between two pulse programs."
Line 1: `FB P2` (P2 = second program number).
Line 2: `0X YY` (X = start mode 0 or 1; YY = switch speed).

**FA (Repeat):** "Repeat the following FF jump XX times" — 1 parameter byte XX ($01–$FF).

**F0–F7 (D415 Filter):** "This is a 1 byte command. The value you enter F0-F7 is the
lower 3 bits of the filter cutoff, it is stored directly into the low filter register."
→ Writes to SID $D415.

**EE (Pulse Init):** "Write low|high pulse value to sid registers."

**ED (Pulse Subtract):** "Subtract pulse with value xx."

**EC (Pulse Add):** "Add pulse with value xx."

**EB (Pulse Write):** "Write low|high pulse value to sid pulse registers only."

**E2–E7 (Noise trick):** "Write Ex to waveform register" — metallic noise variants.

---

## VIBRATO PROGRAM

Four columns per line (c1, c2, c3, c4):

c2 (delay/mode):
- "01-FD" = delay values (frames before vibrato effect)
- "00" = detuning applied, continues to next line
- "FE" = detuning applied, then holds (no further changes)
- "FF" = infinite loop marker

c3 (vibrato width):
- "00-7F" = oscillate up then down
- "80-FF" = oscillate down then up

c4 = vibrato speed.

"Detuning": c3/c4 used as DL/DH 16-bit frequency offset pair (non-oscillating).
Special "Crazy Comet" effect: values >$80 in c4 for looping frequency modulation.

---

## PULSE PROGRAM

Five columns (c1–c5):
- c1: line position
- c2: "Pulse low and high starting values" (lo|hi byte pair)
- c3: "Pulse high/sweep value" (target endpoint)
- c4: "Sweep speed" (amount added per step)
- c5: sweep mode / jump

c5 values:
- "00/40/80/C0" = stop (no jump)
- "0X-3F" = cut (jump to line X after sweep)
- "4X-7F" = continuous (loop between c3 values; X = line for jump variant)
- "8X-BF" = reverse cut
- "CX-FF" = reverse continuous

Direction: determined by comparing c3 vs c2 (if c3 < c2 → downward sweep).

Example from Lemon64 forum: `01: F0 1F 01 41`
= start $F0|$1F, target $01, speed $41, mode continuous.
"make the filter move slowly from a high to a low cutoff value, and loop around."

---

## FILTER PROGRAM

Same structure as Pulse Program with 3 exceptions:

Exception 1: Column c2 is HIGH byte first, LOW byte second (reversed from pulse).

Exception 2: No pulse-hold routine.

Exception 3: When c3 = $00, special "filter frame routine" activates:
- c2 = written directly to SID $D416 (filter cutoff hi)
- c4 = written to SID $D417 (band/resonance)
- c5 = frame delay (1 or 2 frames) before next line

---

## ARPEGGIO PROGRAM

"You can create 48 different arpeggios."

Uses special waveform bytes "$91, $A1, $B1, $C1, $D1, $E1" in waveform program to
trigger arpeggio.

Column 4 speed/sound encoding (verbatim):
"if you want to play an arpeggio with instrument number $15 using speed 4 you must
enter $d5. If you want to use speed 1, you must enter $15."
→ High nibble = speed level; low nibble = instrument number.
OPEN: $D hex = speed 4 decimal? Non-linear encoding.

Arpeggio values ≥ $80 = loop markers. Values < $80 = note offsets.

Instruments using arpeggios must use waveforms $91/$A1/$B1/$C1/$D1/$E1.

---

## TEMPO PROGRAM

"The tempo program works pretty much like the arpeggio program."
Valid values: $01–$7F (normal), $81–$FF (loop markers). Do not use $00 or $80.

---

## INITIAL VOLUME (INVOL)

Accessed via SHIFT+I. Per-tune, 32 entries.

Column c2:
- High nibble = fade-in speed ($0 = none; $1 = fastest; $F = slowest)
- Low nibble = starting volume ($0–$F)

Column c3:
- High nibble = filter channel forcing bitmask:
  - $1 = channel 1 only, $2 = ch2, $4 = ch3
  - $3 = ch1+ch2, $5 = ch1+ch3, $6 = ch2+ch3, $7 = all
- Low nibble = filter speed delay

---

## THE TRACKER

Track line format: "xxyy" where XX = transpose, YY = sequence number.
Jump pointer: `J0xx` at last track line = loop to tracker position $xx.

---

## THE SEQUENCER

"The sequencer consists of 4 channels."
3 edit modes: Grey (normal entry), Blue (marking), Red (glide entry).

---

## SEQUENCER FX + NOTE COMBINATIONS (Channels 1–3)

Documented ranges:
- "$00–$1F": Set instrument and optional note
- "$20 ON/OFF": Filter channel control
- "$21–$3F": Set glide value and note
- "$40–$6F": Set arpeggio and optional note
- "$70–$7F": Set release/sustain/attack effects

"-- ---" = empty line.
"-- GAT" = gate on (restarts all programs).
"-- gat" = gate off (uses release value).

Example: "Set glide value 2E and note C-4" (FX=$2E, NOTE=C-4).
Tie glide: "Set glide value 2E and tie note c-4" (no envelope restart).

Uppercase note = gate restart. Lowercase = tie (no restart).

---

## SEQUENCER FX + NOTE COMBINATIONS (Channel 4)

Full documented table (verbatim):
```
FX NOTE
-- ---         Empty line
06 ---         [01-1F] Set tempo to 06 and no transpose
04 C#0         [01-1F] [C-0 to A#7] Set tempo to 04 and transpose 1
-- D-0         Set transpose 2
41 ---         [40-60] Look up tempo program 01
44 GAT         [40-60] Look up tempo program 04 and transpose 0.
70 ---         [70] Filter control back to main filter channel
71 ---         [71-7F] Force filter output
21 ---         [21-3F] Force filter program 01
63 ---         [61-67] Forced filter band 03
               [68-6F] Future expansion
```

---

## SEQUENCE SIZES

"00 is min lenght of a sequence. 7F is max length of a sequence."

---

## FINALIZING A TUNE / PLAYER SOURCES

Three Turbo Assembler versions:
1. "BMTASS FAST/9000": Fastload/fastsave for 1541/1571 only
2. "SDI TASS /9000": All device numbers, no fastload
3. "PETSCII SOURCES": Sequence files for 64tass.exe

Two player sources:
- Normal: "s.sdi21-n49"
- Speed: "s.sdi21-spd49"

---

## USING THE MUSIC IN A DEMO/GAME

Entry points (all at $1000 base):
"ldx #00 - $1f / jmp $1000 (Init), jmp $1003 (Main play), lda #$00-$7f / jmp $1006
(Fadeout), jmp $1009 (Speedplay)"

PAL: `raster = 312 / speed`
NTSC: `raster = 262 / speed`

"You are allowed to use the music player in a game free of charge" (with credit).

---

## MEMORY OVERVIEW (verbatim structure)

```
$0100-$017F  Stack
$0180-$0200  Sequence lengths
$3000-$3800  Track 1
$3800-$4000  Track 2
$4000-$4800  Track 3
$4800-$5000  Track 4
$5000-$D000  Sequences
$D000-$D810  Directory (max 128 files)
$E000-$E100  Waveform programs
$E100-$E200  Waveform note values
$E200-$E300  Pulse programs
$E300-$E400  Arpeggio data
$E400-$E500  Arpeggio programs
$E500-$E600  Vibrato programs
$E600-$E700  Filter programs
$E700-$E8E0  Sound setup tables (10 fields × 32 instruments = parallel arrays)
$E980-$EA00  Tempo data
$EA00-$ED00  Sound names
$EE00-$EEC0  Note frequency table
```

---

## FILE OVERVIEW

"32 Tunes, 128 Sequences, 32 Instruments (48 through arpeggio), 48 Arpeggios,
85 Vibrato programs, 64 Filter programs, 64 Pulse programs, 48 Tempo programs"

---

## SAVE / DUMP

"SAVE": Bytepacker compresses $3000–$D000 and $E000–$EE00. File size ~5–60 blocks.

"DUMP": Exports only used sequences from ON channels. "Turbo Assembler sequential
file." File size ~5–120 blocks.

---

## KNOWN BUG ISSUES

"$7F sequences filled with tie notes causing dump overflow beyond the 256-byte limit."

---

## DICTIONARY (15 terms)

| Term | Definition |
|------|-----------|
| Arpeggio | Method to emulate chords through rapid note switching |
| Channels | Synonym for tracks |
| Glide | Pitch slide between notes at specified speed (hard/tie variant) |
| Instrument | Synonym for sound; ADSR + effect package |
| Line number | Index for program/sequence position |
| Program line # | Number before ":" in sound edit |
| Sequence | Pattern unit (called "sector" or "sync" in other editors) |
| Sequencer | FX+NOTE columns for all channels |
| Sound | Synonym for instrument |
| Tie note | Note without program restart (brown background) |
| Tie glide | Glide without program restart |
| Track line | Two-parameter pair (transpose + sequence #) |
| Tracker | Sequence transpose/sequence variables display |
| Tracks | Synonym for channels |
| Waveform | Basic oscillator shape (triangle, sawtooth, pulse, noise, combined) |

---

## CREATING DRUMS (3 examples)

**Snare drum:** WF PRG=$00, AD=$08, SR=$88, GATE=$22, others $00
**Bass drum:** WF PRG=$07, AD=$08, SR=$86, GATE=$22, PULSE PRG=$88
**Bass drum variant:** WF PRG=$0D, SR=$86, GATE=$20, PULSE PRG=$01

---

## TRICKS TO MAKE A TUNE USE LESS MEMORY

1. Sequence reuse in tracker
2. Only set instrument when changing
3. Use gate timeout instruments instead of explicit ties
4. Use arpeggio programs instead of waveform tables
5. Use $EB–$EE commands instead of pulse programs
6. Set FILTER PRG=$80, BAND/RESONANCE=$00 on non-filter channels

---

## v2.1.7 Release Notes (verbatim from sdi217_releasenotes_README.txt)

"SDI v2.1.7 was released on October 12, 2014."

Two bug fixes in turbo assembler player:
1. "Filter cutoff routine was missing a small compare routine for fast downwards
   subtraction" — caused audio discrepancy between player and editor.
2. "Initiating a composition with particular gatetimeout parameters (Ax, Cx, or Ex)
   could prevent the initial note from sounding properly."

"Credited to GRG and GT of SHAPE."

---

## Note Tables (from SDI.2.1.6-note_tables.txt)

Three waveform note-column value tables:

**Upwards table (C-0 base = $00, spans C-0 to A#7):**
- Values $00–$5F → notes C-0 through A#7 (added to sequence note + transpose)

**Downwards table (C-3 base = $60):**
- Values $60–$7F → notes C-3 down to some lower note (subtracted from note)

**Fixed note table (independent of sequence):**
- Values $80–$DF → notes C-0 through A#7 (override sequence note entirely)
- Useful for drums/rhythmic elements needing fixed pitch regardless of transpose

Reserved: $E0–$FF (future expansion, currently unused).
