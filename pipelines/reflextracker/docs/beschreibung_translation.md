---
source_url: BESCHREIBUNG PRG file extracted from Reflextracker V1.1 D64 (CSDb #43348)
fetched_via: python3 D64 binary extraction + string analysis
fetch_date: 2026-06-15
author: PVCF / Reflex
content_date: 1995
reliability: primary (original documentation)
---

# Reflextracker V1.1 — BESCHREIBUNG (Documentation) Summary

The BESCHREIBUNG is a 112-block PRG file (BASIC + machine code display program) containing the full German-language manual for Reflextracker V1.1. The text was extracted from printable ASCII runs in the PETSCII binary.

**Note:** The disk directory entry in zip #1 says "^ SORRY TO NON GERMAN[S] — A TRANSLATED VERSION SOON!" — that translated version was apparently never released.

---

## Credits (from BESCHREIBUNG)

```
EDITORCODE:    ZORC/REFLEX
EDITORDESIGN:  PVCF/REFLEX
DISK UND OPTIMYZE-SYSTEM:  KB/TOM
CODE UND SAMPLEMENUEDESIGN: KB/TOM
BESCHREIBUNG:  PVCF
BEISPIELLIEDER: PVCF
SAMPLE-PACK CODE: QUISS/REFLEX
SAMPLES: PVCF/REFLEX
```

---

## Contact Address (from BESCHREIBUNG)

```
MATTHIAS KRAMM
MOEWESTR. [N]
[80xx] MUENCHEN
GERMANY
```
(Matthias Kramm = Quiss; PVCF directed users to Quiss for the latest version)

---

## Key Technical Information (extracted from documentation)

### Format Overview

- **Type:** PC-based tracker that outputs C64 SID files
- **Voices:** 2 audio voices (ZWEI STIMMIG = two-voiced)
  - Track table has VOICEr and VOICEq columns (= Voice 1 and Voice 2)
  - Each voice plays independently; if one has "--" in the track table, only the other plays
- **Samples:** PCM-based (4-bit or 8-bit digitised samples, not SID synthesis)
- **QuadSID:** Supported for multi-chip configurations (up to 10 channels), but those cannot be saved to standard .sid format
- **Play interrupt:** Self-installed IRQ (PSID play_addr = $0000 = PAL VBI)

### Player Memory Layout (from "MEMORY LOCATIONS" screen)

```
[MUSIC DATA address]    ds   MUSIC
[+2]                   dt   CODE
[+x]                   dx   x CHARSETS
                        F sr  TEXTPAGES
```
(The exact addresses depend on sample sizes; the player always loads to $C000)

### Player Start Address

- **Init:** $C006 (SYS 49158) — standard for all HVSC Reflextracker SIDs
- **Play:** $0000 (PAL VBI self-installed IRQ)
- **Player size:** 9 disk blocks = 2048 bytes ($C000–$C7FF)

### Track Table Format

```
PATT    VOICE1          VOICE2
NR      NR  TAB         NR  SND IS DSV
pp  --  --  --          --  --  --
pq  pp  mm  mm          pr  mm  mm
...
```

Fields per voice per pattern row:
- **NR:** Pattern number (hex, 0-$4F = max $4F patterns = 79 in decimal, BESCHREIBUNG says up to $7F = 127 patterns)
- **SND:** Note (C-1 through B-7)
- **IS:** Instrument number
- **D:** Direction (0 = forward, 1 = backward playback)
- **S:** Speed (0 = slowest, F = fastest; recommended value = 7 for normal 4/4 time at pattern length $1F)
- **V:** Volume (0 = max, 3 = min; 4 levels)

Special track table entries:
- `--` = skip this voice for this position
- `RP` = Repeat: jump back to position 00 in track table (only for one voice; other continues)
- `ED` = End: stop the player

### Pattern Format

Each pattern is $10 (16) rows long (hex). Columns per pattern row per voice:
- **SND:** Note name + octave (e.g., "Cm" + "s" = C in octave s)
- **IS:** Instrument number (sample number); `--` = continue playing previous sample at new pitch (SWITCH effect)
- **D:** Direction (0 or 1)
- **S:** Speed
- **V:** Volume

**SWITCH effect:** If IS is `--`, the previously playing sample continues at the new note frequency (pitch change without re-triggering attack).

### Pattern Keys

- F1: PLAY from cursor position
- F2: OPTIMAL PLAY (with playback optimisation)
- F3: STOP PLAY
- F4: CONTINUE PLAY
- `^` (Shift+Arrow): Save pattern content to RAM from cursor position
- `|` (pipe): Write RAM content back to pattern at cursor position
- `--`: Delete note
- `K`: Insert "kill" (stop this voice, sample continues elsewhere)
- `}` (=): Write END (jump to next pattern in track table)
- SH+RETURN: Open pattern under cursor
- SH+I: Insert line
- SH+D: Delete line
- SH+CLR: Increment all notes in pattern by 1 semitone
- SH+INST: Decrement all notes in pattern by 1 semitone
- SH+UP/DOWN: Increment/decrement sample number

### Key Layout (Note Entry — QWERTY keyboard)

```
Keyboard:  A S D  F G H J K L z {
Notes:     C D E  F G A B C
```
- W = C# (C with sharp), E = D#, T = F#, Y = G#, U = A#
- Numbers 2-7 select octave
- B-7 = highest note, C-1 = lowest note

### Edit Modes (F7 key cycles)

- **Mode 1 (blue frame):** Notes entered AND played simultaneously; song stops if running
- **Mode 2 (light blue frame):** Notes entered without playback; song keeps playing (for live editing)
- **Mode 3 (black frame):** Keyboard mode — play current sample without entering it to pattern (for testing)

### Sample Menu

Each sample entry stores:
- Name (up to 16 chars)
- Start address (4-digit hex)
- End address (4-digit hex)

Sample operations available:
- SET NAME, SET START, SET END, DELETE, COPY, LOAD, SAVE
- **UPSAMPLE:** Half-length (one octave higher), slight quality loss
- **DOWNSAMPLE:** Double-length (one octave lower), use only on high-quality samples
- **CHANGE NBS (NIBBLE SWAP):** Swap high/low nibbles of each byte — fixes scratchy playback; lossless, reversible
- **MIX:** Mix two samples together (only at original sample rate; result = 50%+50%)
- **ECHO (HALL):** Add echo/reverb effect; delay rate depends on total sample length
- **FILTER:** (V1.1 new feature) High-frequency filter — removes high frequencies from noisy basses/whistles
- **AMIGA TRANSFER:** Receive samples from Amiga or Archimedes via parallel cable; Amiga saves as "(ARC: [name])"
- **RECORD:** Live sampling using loaded SDRV driver; shows real-time sample monitor; SPACE to start recording, SPACE again to stop; auto-trims silence

### SID Waveform Driver (SDRV.SIDWAVE)

Converts SID chip waveforms to PCM samples:
```
WFORM+PULSE: First digit = waveform (1-4), last 3 digits = 12-bit pulse width (for waveforms 3-4)
FREQUENCY: SID register value (use C64 handbook note table)

C64 SID frequency table (from BESCHREIBUNG, PETSCII hex notation translated):
C-0 = $D411v  (?? — need proper hex decode)
C-1 = $D422p
C-2 = $D4QtB
C-3 = $D4xBt
...
```
(The exact hex values need proper PETSCII-to-hex decoding of the original binary)

### Disk Menu

- LOAD SONG: Load a module file
- SAVE SONG: Save current module
- DIRECTORY: Show disk directory
- STATUS: Query floppy error status
- CLEAR ALL: Erase all RAM data
- LOAD DRIVER: Load a sampler driver (SDRV.*)

### Error Recovery

If the player crashes: RESET, then type `SYS $CFF5` or `SYS 53237` to return to editor. (The editor must be re-enabled first with a command — possibly RUN/STOP or a special SYS.)

### Version History Note

The BESCHREIBUNG mentions: "EBEN BEKAM ICH DIE NEUESTE UPDATETE VERSION, DIE V1.1 VOM TRACKER" — PVCF only just received the V1.1 update while writing the documentation. New V1.1 features: FILTER, AMIGA TRANSFER, RECORD functions.

---

## Language

Entirely in German. A translated version was promised ("SORRY TO NON GERMAN[S] — A TRANSLATED VERSION SOON!") but never released.
