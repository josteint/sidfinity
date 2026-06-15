---
source_url: local disk image — ariston_illusion.d64 (csdb.dk/getinternalfile.php/2252/ariston_illusion.d64)
fetched_via: curl from csdb.dk 2026-06-15; JC64dis 2.3 disassembly embedded in Ariston.dis
fetch_date: 2026-06-15
author: Stefano Tognon (JC64dis 2.3 — disassembly tool author); original music driver by Ian Crabtree / Philip Brabbin / Wally Beben
content_date: driver (c) 1987/88; disassembly by Tognon (tool version 2.3, undated)
reliability: primary (machine-disassembly of live binary with human annotations)
---

# Ariston Music Driver — JC64dis 2.3 Annotated Disassembly Findings

Source: `tmp/ariston_research/Ariston.dis` (embedded in the JC64dis .dis project file).
The file also contains a path `/C:\Users\stefano_tognon\Downloads\Dark_Side.sid`, indicating
the analysis was done on Wally Beben's "Dark Side" (1988 Incentive) — which uses the Wally_Beben
variant of the Ariston player.

---

## Credits in-binary

From the PRG executable on ariston_illusion.d64:

```
PROGRAMMED BY PHILIP BRABBIN 1987/88
(C) ARISTON DESIGNS '88
```

(The bytes 0x04 and 0xAD between "PHILIPP" and "BBIN" are CBM PETSCII control codes;
the actual string is "PROGRAMMED BY PHILIP BRABBIN 1987/88".)

---

## Tuning

The frequency table is labelled:
```
A4=459 HZ (PAL) | A4=477 HZ (NTSC)
```

Note: The VGMPF wiki states "424 Hz or 434 Hz." These may be measured from different
driver variants (Ian_Crabtree_V1/V2 vs. Wally_Beben). The JC64dis annotation is
from Dark_Side.sid (Wally_Beben variant).

---

## Instrument Format (8 bytes per instrument)

```
+0  control          — SID waveform/gate control byte
+1  attack/decay     — ADSR: attack nibble | decay nibble
+2  sustain/release  — ADSR: sustain nibble | release nibble
+3  pulse wave width — 2 bytes packed (lo|hi)
+4  vibrato step/size — nibble-packed: tttt ssss (t=step, s=size)
+5  pulse wave sweep  — pulse sweep rate
+6  trill bits        — which trill table(s) active
+7  effect byte       — drum/plunk/echo effects:
        bit 0: drum effect BASS
        bit 1: plunk effect
        bit 2: echo effect
        bit 3: drum effect SIDE
```

---

## Track Format (orderlist)

```
00..7F   pattern number (0–127 patterns)
80..BF   transpose − (00..3F semitones down)
C0..FE   transpose + (00..3E semitones up)
FF       end of track (loop back to start)
```

---

## Pattern Format

```
00..5F    note number (0–95, covers 8 octaves)
7A dd nn  DVI  delay/vibrato: dd=delay, nn=note
7B nn yy  GLI  glissando: nn=note, yy=length/delay (high nibble=length, low nibble=delay)
7C bb     CTR  continue trill: bb=trill bits
7D bb     TRL  trill: bb=trill bits
7E nn     TIN  trill increment: nn=note
7F nn     TDE  trill decrement: nn=note
80..BF    Lxx  note length (00..3F = durations 0–63)
C0..DF    Ixx  instrument select (00..1F = instruments 0–31)
F0..FB    Sxx  speed (0..B) — tempo change
FC vv     VOL  set volume: vv=volume/filter byte ($D418)
FD        (not in the pattern command docs; possibly reserved)
FE        STP  stop of sound (gate off, silence voice)
FF        END  end of pattern (advance to next pattern in track)
```

---

## SID Register Indexing

The driver uses an offset table: `Sid offset table (0, 7, E)` — i.e. voice 1 at $D400,
voice 2 at $D407, voice 3 at $D40E. This is the standard C64 SID voice stride.

---

## Assembled JC64dis Constants (Dasm format)

```asm
DVI = $7A
GLI = $7B
CTR = $7C
TRL = $7D
TIN = $7E
TDE = $7F
; Lengths: L00=$80 .. L3F=$BF
; Instruments: I00=$C0 .. I1F=$DF
VOL = $FD
STP = $FE
END = $FF
```

---

## Engine Sub-routines (annotated labels)

From the JC64dis annotations:

- `initSongs`         — init entry point
- `playSound`         — play (IRQ) entry point
- `loopSetTrack`      — set up voice track pointers
- `loopVoiceReadTrack` — main voice processing loop
- `getNextPattVal`    — read next pattern byte
- `calculateNote`     — compute SID frequency for note+transpose
- `goTestNoteToPlay`  — check if note should play
- `testContinueTrill` — trill continuation test
- `testNoteLength`    — note duration check
- `setInstrOpcode`    — set instrument data for voice
- `testTrillInc` / `testGlissando` — effect type dispatch
- `setTrillData`      — set up trill buffer for voice
- `verifyGlissando`   — glissando step: high nibble=length, low nibble=delay
- `goTestForVibrato`  / `testForVibrato` — vibrato enabled test
- `loopGenerateVibSize` — compute vibrato amplitude
- `testVibCounter2`   — vibrato timing counter 2
- `incVibCounter`     — vibrato counter increment
- `testActDelayVib`   — vibrato activation delay
- `setupVibFreq`      — set vibrato base frequency
- `testPulseSweep`    — pulse width sweep test
- `testEchoEffect`    — echo effect check
- `testEffectSide`    — drum SIDE effect check
- `testEffectBass`    — drum BASS effect check
- `testEffectPlunk`   — plunk effect check
- `readTrackCmd`      — read track command (transpose / pattern)
- `setTranspose`      — apply transpose value to voice
- `decreaseDuration`  — countdown note length
- `outUndertone`      — silence output
- `processTrill`      — apply trill buffer step
- `updatePattPtr`     — advance pattern pointer for voice
- `loopClearSid`      — clear SID registers (on init/silence)

---

## Voice State Per-Voice (zero page / RAM)

- `Track index for voice (0, 1, 2)`
- `Pattern low for voice (0, 1, 2)`
- `Pattern high for voice (0, 1, 2)`
- `Pattern index` (current offset into pattern)
- `Transpose for voice`
- `Trill bits value for each voice`
- `Trill offset for each voice`
- `Index in trill buffer for each voice`
- `Trill buffer for each voice`
- `Trill value being processed`
- `Glissando length/delay`
- `Wave direction (0=up) for voice (0, 1, 2)` — pulse sweep direction
- `Pulse wave value (lo|hi)` — current PW value
- `Pulse wave step/size for vibrato` — vibrato amplitude
- `Pulse wave sweep` — sweep step
- `Vibrato frequency low` / `Vibrato frequency high`
- `Vibrato frequency low step` / `Vibrato frequency high step`
- `actNoteLength` — active note duration counter
- `noiseCounter` — noise waveform counter
- `allowSoundFlag` — voice enable gate
- `inverseEffectFlag`
- `releaseNotMax` / `Release is not a max value`
- `attackDecayFlag` — ADSR state machine flag
- `curVibratoStepSize`
- `Instruction code: FE inc, DE dec` — pattern scan direction ($FE=ascending, $DE=descending)

---

## Pattern Scan Direction

The pattern byte scan can go forward (FE=INC) or backward (DE=DEC). This is an unusual
feature — it suggests the engine can play patterns in reverse for some effects.

---

## UI Labels (from the Ariston Music Editor binary)

```
VOLUME
NVIB. D[ELAY]   — vibrato delay
CHROMATIC
GLISSANDO
ANGLE SAWTOOT[H]  — triangle / sawtooth waveform
PULS[E]/NOIS[E]/SYNC  — waveform selectors
PRESS 1-4 FOR MUSIC
TR: [track number]
RETUR[N]
CRSR [cursor]
```

The keyboard layout string found: `C C#D D#E F #G G#A A#B` — chromatic keyboard
mapping for note entry, with `ZSXDCVGBHNJM,` for the lower octave row (standard
QWERTY-style piano layout).

---

## SID Chip Quirk: "Phasing" Effect

From VGMPF/Wally Beben research: In late 1987, Maniacs of Noise contacted Wally Beben
to ask about the "phasing" effect in his Ariston-based music. Beben shared the source
code; they enhanced the drum routines and sent it back. This phasing effect is likely
the `echo effect` documented in instrument byte +7 bits, possibly combined with the
trill/vibrato interaction.

---

## Notes on Disk Image

The disk image `ariston_illusion.d64` (CSDb release 29914) contains a single PRG file
named `ARISTON` (119 blocks = ~29,750 bytes) loaded at $0801.
This is the cracked version by "Criminals in Computers + Illusion" (1988-06-24).
The cracker intro shows: "ILLUSION / IMPORTED ON / MEMBERS / BIG MAN - BLACKBEARD - SATAN
/ DOCTOR D - INTRUDER / INTRO BY SATAN"

The `ariston_cic.d64` disk image (CSDb release 119920) contains `ARISTON/CIC` (76 blocks)
— possibly the player-only portion (no cracker intro, smaller).
