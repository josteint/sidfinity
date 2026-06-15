---
source_url: D64 disk image: BESCHREIBUNG file (side 1 of Reflextracker_V1.1.zip)
fetched_via: curl + Python D64 parser + PETSCII decode
fetch_date: 2026-06-15
author: PVCF / Reflex
content_date: 1995
reliability: primary (original documentation)
---

# Reflextracker V1.1 — German Manual (BESCHREIBUNG)

Extracted from the BESCHREIBUNG PRG file (D64 side 1, 28077 bytes, loads at $0801).
PETSCII decoded to ASCII. Some characters may be mis-decoded due to PETSCII graphics chars.
Note: "." in decoded output = non-printable PETSCII byte.

## Credits block (from file)

```
EDITORCODE: ZORC/REFLEX
EDITORDESIGN: PVCF/REFLEX
DISK UND OPTIMYZESYSTEM: KB/TOM
CODE UND SAMPLEMENUEDESIGN: KB/TOM
BESCHREIBUNG: PVCF
BEISPIELLIEDER: PVCF
SAMPLEPACK CODE: QUISS/REFLEX
SALES: PVCF/REFLEX
```

## Introduction

DER REFLEXTRACKER IST EIN MUSIKPROGRAMM WELCHES MIT EINER ZWEISTIMMIGEN
DIGGISPUR ARBEITET. DER EDITOR IST MIT FUER DEN C64 SEHR GROSSEM COMFORT
AUSGESTATTET UND ERLAUBT ES BINNEN EXTREM KURZER EINARBEITUNGSZEIT
QUALITATIV GUTE LIEDER SELBST FUER EINEN ANFAENGER HERZUSTELLEN.

(Translation: "The Reflextracker is a music program that works with a two-voiced
digi track. The editor is equipped with very great comfort for the C64 and allows
one to create qualitatively good songs within an extremely short learning time,
even for a beginner.")

## The editor field

In the music editor, you always see the following parameter line:
```
SMPLNAME: PANFLOETE Q
SMPLPAR:  NR:QR  LEN:DRSTS
```

You see the most important info line of the tracker: the currently used sample
(here "PANFLOETE Q") with instrument number "QR" and length RSTS bytes (hex).

Below this, the editor shows:
```
PATT   VOICE1   VOICE2
NR     SND IS DSV   SND IS DSV
PQ     ..M MM ..P   ..M MM ..P
```

Columns: NR = row number, SND = sound/note, IS = instrument/sample, DSV = direction/speed/volume

## Track table (TRACKTABELLE)

The cursor starts in the track editor where you enter pattern numbers for the positions
where they should be played later. If instead of a pattern number there is "MM" in a voice,
nothing is played in that voice; the other voice continues until that pattern ends.
Then the play position moves down one row and plays the patterns entered there.

**Important:** Never have "MM" in BOTH voices simultaneously! The play routine searches for
pattern numbers to open and read the playback speed from. If no pattern number is found,
a program error may occur causing a system crash.

In this case, do a RESET and enter the start address with `SYS DCFFS` or `SYS USRSU`
and press RETURN to return to the editor.

### Track table key bindings

- `.` = Go to sample/disk menu
- `R` = Insert repeat byte (RP): player jumps back to start of track table
- `M` = Clear pattern number, insert "MM" (mute)
- `.` (second use) = Store current voice's table to RAM
- `J` = Write RAM buffer back to table at cursor position
- `.` (third) = Insert "ED" (END): player stops at this position
- `Shift+Return` = Open pattern at cursor

Other: cursor keys, Inst/Del, Clr/Home work normally. Pattern numbers entered with number keys (hexadecimal mode: after 9 comes A, B, etc.).

**Max patterns: hex 1F** (31 patterns can be edited — actually from garbled text, may be more).

## Pattern editor

Reached from track table via Shift+Return. Shows the pattern at the current pattern number.
Format:
```
VOICE1          VOICE2
NR  SND IS DSV  SND IS DSV
PP  ..M MM ..P  ..M MM ..P
PQ  ..M MM ..P  CMS QR ..P
```

**Pattern length: 16 rows** (hex $0F + 1)

### Column descriptions

- **NR**: Row number of the pattern
- **SND (Sound/Note)**: The note to play (e.g. CM = C in octave 3, DM = D in octave 3)
- **IS (Instrument/Sample)**: Sample table number. "MM" = continue previously playing sample at new pitch (switch effect)
- **D (Direction)**: P = forward playback, Q = backward playback
- **S (Speed)**: P = slowest, F = fastest. W recommended for normal tempo (at pattern length 16)
  - Voice 1 has priority over playback speed
- **V (Volume)**: P = maximum, S = minimum, 4 levels

### Special pattern entries

- `MM` as instrument: continue previously playing sample at new pitch ("switch effect")
- `K`: kill — sample stops playing
- `.` (period): inserts "END" — jump to next pattern in track table
- `Shift+K`: sample stops playing
- `Shift+M` (decrements all notes in whole pattern by 1)
- `Shift+K` (increments all notes in whole pattern by 1) — "from FM5 becomes EM5"

### Edit modes (F5 key cycles)

- **Mode 1 (blue border)**: Notes entered AND played simultaneously; running song pauses
- **Mode 2 (light blue border)**: Notes entered but NOT played; can edit live song
- **Mode 3 (black border = "keyboard mode")**: Notes play but NOT entered (test-only)

### Note keyboard layout

```
Q W E R T Y U I O P  ← C# D# F# G# A#
A S D F G H J K L Z  ← C  D  E  F  G  A  B  C
```
(W=C#, E=D#, T=F#, Y=G#, U=A#)
Numbers 1-4 = octave selection. "4" = highest note, "1" = lowest.

### Pattern editor key bindings

Same F-key bindings as track editor, plus:
- `.` = Store pattern content from cursor position to RAM
- `J` = Write RAM back to pattern from cursor position

## Sample menu

The lower half of the screen lists samples. The upper area shows the selected sample as a sine-wave display.
Press Return on a sample to access:

- **Set Name**: Rename sample
- **Set Start**: Set new start address
- **Set End**: Set new end address  
- **Delete**: Erase sample
- **Copy**: Copy sample data/addresses to another slot
- **Load**: Load sample from disk (D key = show directory)
- **Save**: Save sample to disk (uses floppy drive X)
- **Upsample**: Halve sample length (sounds one octave higher, slight quality loss)
- **Downsample**: Double sample length (one octave lower, double memory usage; can play from C-1)
- **Change NBS**: Swap high/low nibbles (fixes scratchy samples; can be applied repeatedly without quality loss)
- **Mix**: Mix two samples together (each at 50%; requires samples at same sample rate as C-3)
- **Echo**: Add hall/reverb effect (delay rate depends on sample length)

## Disk menu

- **Load Song**: Load song (module)
- **Save Song**: Save song (module)
- **Directory**: Show disk directory
- **STAT**: Check floppy errors
- **Clear All**: Clear all RAM data
- **Load Driver**: Load sampler driver

## Memory locations

```
$1009+  : Music (sample data)
$C000   : Code (player)
$D000+  : X charsets
$F000+  : Text pages (4)
```

## The Player

On disk there should be a 9-block player that can play the saved MOD files.
Start: `$C000` or `SYS 49152`.

(From docs: "DER START IST IN $C000 ODER SYS 49152")

In the MOD file, the finished and complete tracker song is stored.

## Sampler drivers (SDRV.* files)

Multiple sampling drivers available. Differences: quality and connection type.

Drivers:
- `SDRV.UPRT 4BHI/4BLO/8BIT`: Userport (USRP) 4-bit hi, 4-bit lo, 8-bit samplers
- `SDRV.UPRT AMIGA`: Amiga parallel cable sampler
- `SDRV.I/O1 4BHI/4BLO/8BIT`: Module port 1 samplers
- `SDRV.I/O2 4BHI/4BLO/8BIT`: Module port 2 samplers  
- `SDRV.JOY1 2BHI/2BLO/4BIT`: Joystick port 1 samplers (2-bit hi/lo, 4-bit)
- `SDRV.JOY2 *`: Joystick port 2 samplers

**Warning:** Module port drivers may crash the system if no sampler is connected.

### Special driver: SDRV.SIDWAVE

Converts SID chip waveforms to samples. After loading, selecting "Sample" shows a window for:
- **WFORM/PULSE**: First digit = waveform type (1-7 meaningful), last 3 digits = 12-bit pulse width for waveforms 4-7
- **FREQUENCY**: SID frequency register value

SID frequency table for C-x notes (hex):
```
C-2: $0119 (decimal: ~281)  — Note: hex needed, docs give decimal
C-3: $0232 (decimal: ~562)  — These appear garbled in PETSCII decode
C-4: $0463
...
```
(Values from the manual appear garbled in PETSCII; refer to C64 SID frequency table)

## V1.1 new features (added just before final release)

New sample menu operations:
- **...filter...**: Filters high frequencies from a sample (useful for noisy basses or samples with hissing)
- **...Amiga...**: Transfer Amiga samples via standard parallel cable. Select "Receive" then on Amiga (or Archimedes): save file with name `PAR.` (Archimedes: `Parallel`). Tracker handles the rest automatically.

## Note on QuadSID

The documentation itself does NOT mention QuadSID in the BESCHREIBUNG. The QuadSID support was a PC-side feature of the tracker frontend. Standard C64 output = 2 voices via the digi engine.
