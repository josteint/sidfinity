---
source_url: local: csdb_manual_0_01b.pdf  (downloaded from https://csdb.dk/getinternalfile.php/137191/masm_manual_0_01b.pdf)
fetched_via: curl 2026-06-13
fetch_date: 2026-06-13
author: Marco Swagerman (MC), Sept 2010 — author of the editor
content_date: 2010 (manual); editor itself Nov 1987 – Feb 1989
reliability: primary (author-written manual)
---

# Music Assembler — official manual technical notes

"Music Assembler 1.0 User Manual", manual version 0.01b, written by Marco
Swagerman (MC) of Dutch USA-Team, September 2010 (21 years after release).
15 pages. Full text vendored alongside as `csdb_manual_0_01b.txt`.

**SCOPE WARNING:** the manual documents the **editor's authoring data model**,
NOT the packed/assembled on-disk player format. The manual explicitly says the
edited data is "assembled into intricate, to many people unreadable data which
is disassembled by the player routine while playing." For the actual packed
byte layout see `csdb_packed_format_disasm.md` (disassembled from real song
files). This file = the *semantics* a USF converter must reproduce; that file =
the *bytes* a decompiler must parse.

## Engine identity (from the prologue)

- Authors MC (Marco Swagerman) + OPM (Oscar Giesen), Dutch USA-Team.
- Predecessor experience: the authors wrote tunes in Chris Hülsbeck's
  *Soundmonitor* before building their own editor. (Their earlier in-house
  tools were *Rockmonitor 2* (1987) and *Rockmonitor 5* (1988) per CSDb — a
  likely lineage to check for a shared player ancestor.)
- Published by **Markt+Technik** (German publisher; sold mostly in Germany).
- It is NOT a tracker. It "assembles" a standalone, relocatable executable that
  bundles player + data. Playable from BASIC via `SYS <base>`. **No stop-from-
  BASIC code was included** (the music keeps running until reset).

## Player / file mechanics

- A saved song relocates anywhere in `$0400`–`$FF00`. Base is user-chosen at
  save time. (Confirmed by specimens at $5000 / $6800 / $C000 / $2900.)
- Entry points (verified against binaries — see packed-format doc):
  `base+$00` IRQ-installer / `base+$21` play / `base+$48` init.
- Two file types:
  - `s.<name>` = complete song (player + packed data, relocatable executable).
  - `p.<name>` = **presets only** (32 presets + their 16 arpeggios), shareable
    and swappable between songs. (Specimen `p.` was 770 bytes, load $4300.)

## Data model (authoring view)

### Presets (instruments) — 32 max, **8 bytes each**

Each preset holds: ADSR envelope, waveform byte, pulse waveform rate + pulse
effect, vibrato params, and a link to one of the 16 arpeggios.

- **ADSR**: two pairs of hex digits (AD byte, SR byte) → SID $D405/$D406 model
  (0–15 == $0–$F per nibble). Standard SID envelope.
- **Waveform byte** (the value written to $D404 control, gate handled
  separately). Bit table (verbatim from manual):
  | bit | val | function | bit | val | function |
  |----|----|----|----|----|----|
  | 7 | $80 | random noise | 3 | $08 | **disable oscillator** |
  | 6 | $40 | pulse | 2 | $04 | ring modulation |
  | 5 | $20 | sawtooth | 1 | $02 | sync |
  | 4 | $10 | triangle | 0 | $01 | gate (1=A/D/S, 0=Release) |
  - Left nibble selects waveform(s); right nibble = trigger/ring/sync/gate.
  - Ring/sync are with the **left-adjacent channel**: voice 3↔2, 2↔1, **1↔3**.
  - **Hard-reset trick**: a waveform value of `$09` or `$08` is **both
    normalised to $08 by the player**. It switches the oscillator OFF (instead
    of just clearing the gate → release) at note end. Used with an arpeggio
    that selects the real waveform. This is the classic "hard restart" — the
    USF model must capture "preset uses hard-reset wave $08/$09" as a flag.
- **Pulse rate**: one hex byte, **nibble order is swapped** — "the left digit
  is the LEAST significant and the right the MOST significant." So byte `$08`
  decodes to a pulse-width value of `$80` (=50% duty, "100% pure pulse"). A
  decompiler must un-swap: `pw = ((byte & 0x0F) << 4) | (byte >> 4)` style — VERIFY
  against the packed bytes; the editor stores it differently than it displays.
- **Pulse effects** (mutually-exclusive, F3 / F5 toggles):
  - *Pulse Slide*: adds "pulse byte" to the pulse rate **every frame** (50 Hz).
    A one-directional ramp (oldskool rough edge).
  - *Pulse Vibrate*: adds/subtracts "pulse level" for "pulse speed" frames, then
    reverses — a triangle LFO on PW (the Hubbard/Galway smooth pulse). Params:
    pulse byte, pulse level, pulse speed.
- **Vibrato** (3 params): *delay* (frames after note trigger before vibrato
  starts), *speed* (frames per direction change), *level* (freq add/subtract).
  NB manual notes vibrato has more pitch impact on low notes (linear freq
  delta against the SID's non-linear note table).
- **Arpeggio link**: index into the 16-entry arpeggio table, or none.

### Arpeggios — 16 max

A tiny per-frame sequence (each step = 1/50 s). Each step = **3 columns**:
waveform, note offset, low-pass filter frequency.

- Note offset is **relative** by default (added to the sequenced note) OR
  **absolute** when prefixed with `<` (ignores the sequenced note; uses the
  arp value as the literal note). `$0C` = one octave.
- Terminator (in the **waveform column**): `$FF` = loop, `$FE` = stop.
- Using an arpeggio **cancels the preset's vibrato**. Arpeggios are
  **overruled by sequence-originated portamento (slide)**.
- Manual examples (waveform / note-offset / filter triplets):
  ```
  chord:    41 00 00 / 41 04 00 / 41 07 00 / FF      (C, E, G relative; loop)
  percuss:  81 5F< 00 / 11 00 00 / FE                (noise click then tri; stop)
  ```
  So a step row is literally `[wave] [note(.absolute if <)] [filterfreq]`,
  with the loop/stop sentinel occupying the wave column of the final row.

### Tracks — exactly 3 (one per SID voice)

Each track is a list of entries; each entry = **3 columns**:
- Sequence number `$00`–`$FD` (`$FE`=stop track, `$FF`=loop track).
- Transpose offset `0`–`15` semitones up.
- Repeat count (0 = play once; N = play N+1 times total).
- Constraint: sequence numbers must be **contiguous from $00** (no gaps; you
  can't have seq $03 without seq $02 existing).
- (Editor-only nicety: a secondary "swap" track set for testing; not in output.)

### Sequences — monophonic note lists

Per step (authoring columns):
- **Note** (C..B; toggle US vs German notation — German uses H for B).
- **Duration** in the 2nd column, **counted from 0** (the famous off-by-one):
  | hex | length |
  |----|----|
  | `1F` | double-whole ("see you tomorrow") |
  | `0F` | whole |
  | `07` | half |
  | `03` | quarter |
  | `01` | 8th |
  | `00` | 16th |
  So actual length = `duration + 1` sixteenths. (Duration is a 5-bit field —
  see the packed `AND #$1F` in the decode.)
- **PRE command** (key P): selects a preset (preset # in 2nd column).
- **No-trigger note** (Shift+note, shown `<`): plays the note WITHOUT
  re-gating the ADSR (legato; used at the end of a slide).
- **Hold**: holds current note up to 2 whole notes; chainable (no max). Does
  NOT release.
- **Rest**: like Hold but **kicks the Release phase** of the ADSR.
- **Portamento / slide** (Shift+S): activates 2 extra columns = slide
  **LSB (fine) + MSB (coarse)**. Downward slide: set last column `$FF`/`$FE`
  (= -1 / -2). **Rattling slide trick**: ODD LSB value → effect applied only
  every *other* frame (rougher); even LSB → smooth. Slide **cancels arpeggio
  and vibrato** for its duration.
- **Low-pass filter** (Shift+F on the length column): 3 params in 2 extra
  columns. First column splits into two nibbles:
  - nibble 1 = **start cut-off** (`0`=lowest … `F`=highest).
  - nibble 2 = **direction/speed** (verbatim table):
    | val | dir | val | dir |
    |----|----|----|----|
    | 7 | down 2/frame | 9 | up 2/frame |
    | 6 | down 4 | A | up 4 |
    | 5 | down 6 | B | up 6 |
    | 4 | down 8 | C | up 8 |
    | 3 | down 10 | D | up 10 |
    | 2 | down 12 | E | up 12 |
    | 1 | down 14 | F | up 14 |
    | 0 | down 16 | 8 | **hold steady** |
  - 2nd extra column = **number of frames** the filter sweep runs (clamps the
    cutoff). Entering `00` here **switches filtering OFF**.

### Filter — global, low-pass only

- SID has one filter shared by all 3 voices (only LP used; HP/BP deemed not
  musically useful).
- Filter effects are applied to the **triggering track AND all lower-numbered
  tracks**: filter from track 3 also filters 2 & 1; from track 2 also filters
  1; track 1 filters only itself. Normal practice = filter from track 1.
- This cascade is a USF-modelling subtlety: a filter command in the V3 sequence
  silently enables filter routing on V1/V2 as well ($D417 bits).

## Disk menu

- The editor's directory view **shows only its own `s.`/`p.` files**; other
  files are hidden.
- Relocation happens at save. Format = `N:diskname,ID`; scratch = `S:s.name`
  (wildcards OK).

## Implications for the decompiler / USF model

1. Player write-model is per-frame (50 Hz), 3 independent monophonic voices,
   one shared LP filter — fits the existing tracker Mode-1 (per-frame
   instruction-sequence) verification path; no digi.
2. Effects that already map onto shared-core primitives: vibrato (delay/speed/
   level), pulse-slide (per-frame PW add ≡ pulse program), pulse-vibrate (PW
   triangle LFO ≡ pwm), portamento (freq slide LSB/MSB, with a *rattling* every-
   other-frame variant), arpeggio (per-frame wave+note-offset+filter table),
   filter sweep (cutoff start + signed step + frame count).
3. Quirks to carry as typed config/flags, not bytes:
   - pulse-rate **nibble-swap** on decode,
   - duration = **stored+1** sixteenths,
   - hard-reset wave **$08/$09 → $08** normalisation,
   - filter **cascade to lower voices**,
   - rattling-slide **odd-LSB → half-rate** flag,
   - ring/sync adjacency **1↔3** wrap.
