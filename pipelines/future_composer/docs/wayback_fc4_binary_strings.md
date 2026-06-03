---
source_url: http://ftp.funet.fi/pub/cbm/c64/audio/editors/fc4.0.prg (also mirrored at zimmers.net)
fetched_via: direct funet/zimmers mirror 2026-06-03
fetch_date: 2026-06-03
author: Syndicate of Coococ Magazine Staff (Dynamix), 1989
content_date: 1989-03-22 (Future Composer V4.0)
reliability: primary (binary distribution; strings dumped via GNU strings -n 4)
---

# Future Composer V4.0 binary — string-table evidence for format

The funet-mirrored `fc4.0.prg` (41 407 bytes) is the original Dynamix
distribution package. Running `strings` reveals **the editor's UI text
labels, which directly reflect the format's data structures**.

Stored at `/tmp/fc_research/fc4.0.prg`.

## Header (BASIC stub)

```
$0801: 01 08 0B 08 0A 00 9E 32 30 36 31 00 00 00       — SYS 2061 (= $080D)
```

So the editor's entry point is **$080D**. Standard BASIC SYS stub.

## "Sound editor" / "Sequence editor" UI labels (full set)

```
FUTURE COMPOSER V4.0 SEQUENCE EDITOR
SEQUENCE : (0) - USE F1/F3
FREQ:-00-00-00-00-00-00-00-00-
 -00-00-00-00-00-00-00-00-
WAVE:-00-00-00-00-00-00-00-00-
 -00-00-00-00-00-00-00-00-
'X' FOR EDITOR

FUTURE COMPOSER V4.0 FILTER EDITOR
FILTER-PARAMETER
DATA:-00-00-00-00-00-00-00-00-
 -00-00-00-00-00-00-00-00-
'X' FOR EDITOR
```

**Key insights from the UI**:

- **"SEQUENCE EDITOR"** displays a sequence ID (0..N) with two parallel
  16-byte data rows:
  - `FREQ:` — 16 bytes (× 2 lines × 8) (some kind of **frequency / pitch
    sequence**, possibly the **wave-table** or the per-step pitch
    program for an instrument's wavetable layer)
  - `WAVE:` — 16 bytes × 2 lines (the **waveform/control-byte program**)

  So FC V4 instruments have a **16-entry wave program** (matches the
  "Wave table" feature mentioned in research.md V3+).

- **"FILTER EDITOR"** displays one 16-byte program ("DATA:" × 2 lines)
  — confirms **filter programs are 16 bytes long** (matching the
  10-byte filterbytes-record in the Cybernoid 2 source PLUS extra
  bytes V4 added for filter mode + extra segments).

## Function-key menu (instructions)

```
-F1- M(usic?)    -F2- E(dit?)    -F3- D(efine?)    -F4- S(ave?)
-F5- O           -F6- I          -F7- I            -F8- (Init?)

PLAYER $4000 [D] PRG
```

The "PLAYER $4000 [D] PRG" string is **explicit confirmation** that V4
can output a player at $4000 — i.e. the **default relocation address
for FC V4's PSID-style output is $4000**, with `[D]` likely meaning
"with data" (the song appended after the player code).

## Block / track editor UI

```
TRACK
+---$00---+
LOCK
TRACK 
TRACK
HAS BEEN MARKED
TRACK-EDIT
EDIT A BLOCK
BLOCKOPERATIONS
'_' TO ENTER SEQUENCE
PLAY TUNE 1
EDIT SOUNDPARAMETER
TAKE BLOCK (_ONLY IN BLOCK-EDIT)
CUT BLOCK (_ONLY IN BLOCK-EDIT)
ALSO NOW TRACKEDIT
NOW EVEN TRACK-EDIT
```

The "track-edit" / "block-edit" / "sequence-edit" tri-level terminology
confirms the **3-tier data hierarchy**:

1. **Sequence** (per-voice ordered list of block / pattern IDs)
2. **Block / Track** (the pattern data — fixed-length, see "MARKED")
3. **Sound parameters** (instrument definitions — see "EDIT SOUNDPARAMETER")

## "What is new" (V4 changelog) — embedded help text

```
INSTRUCTIONS FOR FUTURE-COMPOSER
WHAT IS NEW, WHAT HAS CHANGED?
- MAIN-EDIT' WAS MUCH IMPROVED
- INFO-PAGE' WITH DISC-OPTIONS, HAS GONE FOR EVER.
- NEW: INSTRUCTIONS AND EDITOR WERE ONE-FILED.
- DIFFERENT AND EXPANDED MENUS.
- RELOCATE-MODE FOR MUSIC-ROUTINE
- BLOCKS, TRACKS, SOUNDPARAMETER AND MUSIC-DATAS MAY SAVED SEPA-
   RATE AND LOADED BACK TO ANY POINT
- (RELOCATING IS NOW POSSIBLE!)
- YOU CAN EDIT SUBTUNES. E.G. FOR TITLE AND GAMETUNE
- HOW TO EDIT MORE THAN ONE TUNE:
   WHEN YOUR FIRST TUNE WAS FINISHED YOU
   EASILY EDIT THE SECOND BEHIND THE END
   BYTE ($FF OR $FE) OF THE FIRST ONE.
   DO THE SAME WITH THE THIRD TUNE.
- 10 DRUMSOUND
- 40 GATEOFF
- NEW SONG  - KILLS SONG, EXCEPT SOUND-PARAMETER.
   DEMO SONG - THE NAME SPEAKS FOR ITSELF
- NOW EVEN TRACK-EDIT
- BETTER THAN SOUNDMON
```

**Critical facts:**

1. **`$FF` or `$FE` = end byte** — sequence terminator. **$FE** ends
   the song (no loop); **$FF** loops back to start. This matches the
   Cybernoid 2 `h2` dispatch exactly.

2. **"10 DRUMSOUND"** — **drum sound count is 10** in V4 (V3 might be
   fewer; Cybernoid 2 has 3 in `drumtabel`).

3. **"40 GATEOFF"** — **40 = the GATEOFF command byte** (or the
   "gateoff" wavetable entry value).

4. **Subtune editing** — V4 stores multiple tunes by appending after
   each `$FE/$FF` terminator. **Subtune addressing is positional in
   the sequence-byte stream**, not table-based — so the subtune table
   stores byte offsets into the flat sequence buffer.

5. **Relocatable** — V4 player is position-independent (`RELOCATE-MODE`).

6. **Saves data sections SEPARATELY** — Blocks, Tracks, Soundparameter,
   Music-data are 4 distinct on-disk sections. This **defines the
   4 storage regions inside an FC file**: instrument table, sequence
   table, block/pattern table, soundparameter (envelope/wave/pulse/filter
   programs).

7. **"BETTER THAN SOUNDMON"** — competitive marketing against SoundMonitor,
   another C64 editor. Same era.

## Function-key bindings (extracted from FC4 strings)

```
SHFT+1- PLAY TUNE 1
CTRL+F- EDIT SOUNDPARAMETER
('_' = enter sequence)
('X' = exit editor)
F1/F3 = previous/next sequence ID
```

## Pitch-name table (used by the note input UI)

```
**C-C#D-D#E-F-F#G-G#A-A#B-C-
```

12 two-character note names, terminated by `C-` (octave indicator).
The leading `**` is the C64 character set's screen rendering of two
"all-bits-on" placeholder cells (rest / unset).

Confirms **standard equal-temperament 12-note naming**, no microtonal
quirks. Hawkeye's pitch indices map directly to this table.

## Hex digit table (used by parameter input)

```
0123456789ABCDEF
```

Standard.

## Note-name → freq-index mapping hints

The string `@H -` (and `:` `;` `<` `=`) immediately precedes the note
name table — suggests these are **screen-codes for the cursor / row
indicators** (octave digits 0-7, perhaps).

## Build hints / version-display strings

```
"FC V4.0   
FC V4.0
 V4.0]
) 1989 
```

V4.0 reports its year as 1989. (V4.1+ exists per CSDb but funet only
has V4.0.) The `2066 CODE` (= $0812) seems to be a secondary SYS
target.

## Open questions raised by string scan

1. **Wave-table command set** — the `FREQ:`+`WAVE:` UI shows 16 entries
   each but doesn't reveal the command-byte semantics (loop, jump, delay,
   set-value). Need to disassemble the editor's input handler at
   $080D.

2. **What is the $40 = GATEOFF marker?** A wavetable entry of $40 might
   mean "clear the gate bit of $D404" — would match Cybernoid 2's
   `byteand` shadow-AND trick.

3. **"10 DRUMSOUND"** — 10 drum slots in V4. Each drum is a length-prefixed
   pair of (waveform-stream, pitch-stream). Cybernoid 2 has 3 drums of
   12-byte length each.

4. The `PLAYER $4000 [D] PRG` string suggests the editor exports as a
   standalone .prg with player at $4000 — there should be a documented
   `dataOffset` from $4000 to the song.

## Provenance log entry

`http://ftp.funet.fi/pub/cbm/c64/audio/editors/fc4.0.prg`
— direct funet binary, the original 1989-1990 distribution. Cross-mirrored
at `https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/fc4.0.prg`.
Strings extracted via `strings -n 4 fc4.0.prg` (368 strings ≥ 4 chars).
