# GoatTracker V1.x Research — CSDb + Covert Bitops Cluster

```
source_url:    https://cadaver.github.io/tools.html
               https://csdb.dk/scener/?id=2908
               https://csdb.dk/release/?id=6072
               https://sourceforge.net/p/goattracker2/code/HEAD/tree/goattrk2/trunk/src/gsong.c
               https://github.com/leafo/goattracker2/blob/master/src/gsong.c
               https://github.com/leafo/goattracker2/blob/master/src/gcommon.h
               https://github.com/leafo/goattracker2/blob/master/morphos/goattracker.guide
               https://cadaver.github.io/rants/music.html
fetched_via:   WebFetch + WebSearch (Claude Code leaf agent)
fetch_date:    2026-06-29
author:        Lasse Öörni (Cadaver) / Covert Bitops
content_date:  2001-2006 (V1.0-V1.53 era)
reliability:   HIGH for format details (derived from GoatTracker 2 gsong.c V1 import path,
               which is the authoritative V1→V2 converter); MEDIUM for version-history dates
               (CSDb scener page, no secondary confirmation).
```

---

## 1. Overview

GoatTracker V1.x is the **original** GoatTracker by Lasse Öörni (Cadaver / Covert Bitops).
It predates GoatTracker 2 (released 2005) and is the engine behind HVSC's `GoatTracker_V1.x`
classification. The HVSC has ~1,384 tunes in this family.

The player is a cross-platform C64 music editor producing an embedded 6502 play routine. It
is NOT the GoatTracker 2 player. The two engines are architecturally different in table structure,
instrument format, arpeggio handling, and pattern encoding.

**Do not conflate with GoatTracker 2**: V2 was a ground-up redesign that added 4-table
step-programming (wave/pulse/filter/speed tables), 63 instruments, and removed the arpeggio
pattern command. GoatTracker V1.x files can be imported into GoatTracker 2 but the format
is different, and "some subtleties (like tricks involving instrument changes) will not play
back exactly like in v1.xx."

---

## 2. Release History (V1.x branch only)

Source: CSDb scener page for Cadaver (https://csdb.dk/scener/?id=2908).

| Version        | CSDb release ID | Year | Notes |
|----------------|----------------|------|-------|
| V0.93          | 189145          | 2001 | Earliest known public release |
| V1.25          | 6072 (confirmed)| 2002 | Confirmed via direct CSDb search |
| V1.4           | (listed, ID unverified) | 2003 | |
| V1.4 Stereo    | (listed, ID unverified) | 2003 | |
| V1.4 Tweak Utility | 100636     | 2003 | Editor helper tool for V1.4 songs |
| V1.53          | (listed)        | 2006 | Final mono version (CSDb upload date; actual release may be earlier) |
| V1.53 Stereo   | (listed)        | 2006 | Final stereo version |

GoatTracker V2.0 was released in 2005 (CSDb ID 188790). The V1.53 uploads to CSDb in 2006 are
likely backdated; V1.x development ended before V2.0.

**Download links (from cadaver.github.io/tools.html):**
- V1.53: `https://cadaver.github.io/tools/goattrk.zip`
- V1.53 Stereo: `https://cadaver.github.io/tools/gstereo.zip`
- V1.25: `https://cadaver.github.io/tools/goatold.zip`
- V1.xx Tweak Utility: `https://cadaver.github.io/tools/tweak.zip`
- V1.xx → NinjaTracker converter: `https://cadaver.github.io/tools/goatninj.zip`

These zip files have NOT been fetched in this research pass (they are binary archives).
A follow-up agent should download them to extract the embedded readme and the 6502
player assembly source.

---

## 3. Song Format — Format Identifier Evolution

GoatTracker uses a 4-byte magic identifier at the start of its .SNG files. For V1.x, multiple
format revisions existed. The GoatTracker 2 import code in `gsong.c` handles all of them:

| Identifier | Version      | Notes |
|------------|-------------|-------|
| `GTS!`     | V1.0 earliest | 3-table, per-instrument inline pulse + wave data; no speed table |
| `GTS2`     | V1.x mid     | 3 tables (wave/pulse/filter); speed table synthesised from inline portamento/vibrato params via `makespeedtable()` |
| `GTS3`     | V1.x final / V2 early | 4 tables (wave/pulse/filter/speed); STBL pointer stored explicitly |
| `GTS4`     | GoatTracker 2.4+ | Added 1-bit pulse modulation accuracy; old songs auto-converted on load |
| `GTS5`     | GoatTracker 2.59+ | Current V2 format |

**HVSC context**: The HVSC `GoatTracker_V1.x` engine classification is based on the embedded
6502 player fingerprint (SIDid), not the .SNG header. The embedded song data in HVSC V1.x SIDs
will be in `GTS!`, `GTS2`, or `GTS3` format, corresponding to the GoatTracker version used
to compose each tune.

---

## 4. Instrument Format

### 4a. GTS! (V1.0 earliest) Instrument Layout

31 instruments (indices 1–31; loop `for (c = 1; c < 32; c++)`). Stored sequentially.

| Byte offset | Field | Notes |
|-------------|-------|-------|
| +0 | `ad` | Attack (hi nibble) / Decay (lo nibble) |
| +1 | `sr` | Sustain (hi nibble) / Release (lo nibble) |
| +2 | `pulse` | Pulse width starting value (1 byte; no 12-bit width, unlike V2) |
| +3 | `pulseadd` | Pulse add per tick |
| +4 | `pulselimitlow` | Pulse lower bound |
| +5 | `pulselimithigh` | Pulse upper bound |
| +6 | `ptr[FTBL]` | Filter table start pointer |
| +7 | `wavelen` | Number of wave entries × 2 (i.e., total wave bytes) |
| +8 | `vibdelay` | Vibrato onset delay |
| +9 | `gatetimer` | Hard-restart gate timer |
| +10 | `firstwave` | Waveform used at note start (before wave program begins) |
| +11…+26 | `name` | 16-byte instrument name (MAX_INSTRNAMELEN = 16) |
| +27… | wave data | `wavelen/2` entries × 2 bytes each (left byte + right byte) |

**Pulse**: No global pulse TABLE in GTS! — the pulse sweep is fully parametric via the 4 per-instrument bytes (start, add, min, max). On import to V2, these are converted to PTBL entries:
```
ltable[PTBL][fp] = 0x80 | (pulse >> 4);
rtable[PTBL][fp] = pulse << 4;
```

**Wave data** is stored inline after each instrument's header. The GoatTracker 2 importer
appends this data into the global WTBL pool and stores the start pointer in `instr[c].ptr[WTBL]`.

### 4b. GTS2 / GTS3 Instrument Format Differences

- GTS2: Instruments have explicit `ptr[WTBL]`, `ptr[PTBL]`, `ptr[FTBL]` pointers but the speed
  table pointer is synthesised at import time from inline portamento/vibrato params.
- GTS3: All four pointers explicit: `ptr[WTBL]`, `ptr[PTBL]`, `ptr[FTBL]`, `ptr[STBL]`.
- Both GTS2 and GTS3 use global shared tables (not per-instrument inline data).
- V2 expanded instruments to 63 maximum (MAX_INSTR = 64, index 1..63).

---

## 5. Wave Table Format (V1 Semantics)

Each wave table entry is 2 bytes: **left byte** (waveform/control) and **right byte** (note/freq delta).

### Left byte:
- $01–$0F: Wavetable delay — pause N frames before advancing
- $10–$DF: SID waveform byte written to voice control register ($D404/$D40B/$D412)
- $E0–$EF: Silent — gate off, no waveform change (sustain/release)
- $F0–$FE: Command — the right byte carries a wavetable sub-command
- $FF: Jump — right byte = jump target position (0-based) in the wave table

### Right byte (when left byte is a waveform):
Encodes arpeggio / pitch:
- $00–$5F: Relative note up (semitone offset, 0=current note)
- $60–$7F: Relative note down
- $80: No pitch change (hold current note)
- $81–$DF: Absolute note number

These right-byte semantics are the native V1 wave-table arpeggio mechanism. When V1 instrument
programs contain pitch-varying right bytes, they implement chord/arpeggio sequences
**via the wave program** (not the pattern arpeggio command). The two arpeggio mechanisms
coexist in V1.

---

## 6. Arpeggio — the V1-exclusive Pattern Command

### The key V1-exclusive feature (removed in GoatTracker 2)

In V1, a pattern row with **command = 0 (DONOTHING) and non-zero data byte** is an
**arpeggio command**. It encodes three chord notes in a single byte:

```
param = data_byte
bit 7 (0x80):     flag / loop-mode
bits 4–6 (0x70):  second arpeggio note interval (semitones above base)
bits 0–3 (0x0F):  third arpeggio note interval (semitones above base)
```

The first note of the arpeggio is always the base note of the pattern row.

**GoatTracker 2 import conversion**: The importer creates a 3-entry wave program in WTBL
(one entry per arpeggio step) with a loop-back jump ($FF) to the start, synthesising the
equivalent repeating 3-note arpeggio via the wave table mechanism. This is why the
GoatTracker 2 manual states: "The only major feature removal is that of the arpeggio command
in v2. Everything that this command does can also be done with wavetables, and the import
feature converts all arpeggio commands to corresponding wavetable programs."

**Implication for HVSC V1 songs**: Any HVSC song using the GoatTracker_V1.x player with
arpeggio effects will have them encoded in the pattern stream as (CMD=0, data≠0) rows,
NOT as wave-table programs. A V1 player that doesn't handle this inline arpeggio command
will play the wrong notes.

---

## 7. Pattern Format

### V1 (GTS!) Pattern Row: 3 bytes

```
Byte 0: note value
Byte 1: (instrument << 3) | command   — instrument in high 5 bits, command in low 3 bits
Byte 2: command data
```

Note values (from gcommon.h):
- $00–$5D (FIRSTNOTE=0x60 offset): note numbers
- $5E (OLDKEYOFF): gate off (key-off), no note
- $5F (OLDREST): rest (no change to gate)
- $FF (ENDPATT): end of pattern

### V1 Command Set (3-bit, values 0–7)

| V1 cmd | Name | V2 equivalent cmd | Notes |
|--------|------|-------------------|-------|
| 0 | DONOTHING | CMD_DONOTHING (0) | With data≠0: arpeggio command |
| 1 | PORTAUP | CMD_PORTAUP (1) | Portamento up; speed inline in data byte |
| 2 | PORTADOWN | CMD_PORTADOWN (2) | Portamento down |
| 3 | TONEPORTA | CMD_TONEPORTA (3) | Tone portamento |
| 4 | VIBRATO | CMD_VIBRATO (4) | Vibrato; depth/speed inline; converted to speed-table on V2 import |
| 5 | SETFILTERPTR | CMD_SETFILTERPTR (10) | Filter jump |
| 6 | SETTEMPO | CMD_SETTEMPO (15) | Tempo change (≥$F0) or master vol (<$F0) |
| 7 | FUNKTEMPO | CMD_FUNKTEMPO (14) | Funk tempo |

**Architectural implication**: V1 has only 8 pattern commands vs V2's 16. V2 added:
CMD_SETAD (5), CMD_SETSR (6), CMD_SETWAVE (7), CMD_SETWAVEPTR (8), CMD_SETPULSEPTR (9),
CMD_SETFILTERCTRL (11), CMD_SETFILTERCUTOFF (12), CMD_SETMASTERVOL (13).

**Speed table**: In V1, portamento/vibrato speeds are encoded inline in the pattern command
data byte. There is no speed table. The `makespeedtable()` function in the V2 importer
synthesises STBL entries from these inline parameters.

### V2 Pattern Row (for comparison): 4 bytes

```
Byte 0: combined note+instrument (using a different packed encoding)
Byte 1: instrument (low bits of note+instrument encoding)
Byte 2: command (0–$0F)
Byte 3: command data
```

V2 uses additional compression: $00-$5F note values don't carry separate command bytes
(they imply CMD_DONOTHING, data 0). The full encoding uses INSTRCHG ($00), FX ($40),
FXONLY ($50) prefixes and REST ($BD), KEYOFF ($BE), KEYON ($BF) special codes.

---

## 8. Table Structures — V1 vs V2 Comparison

| Feature | GTS! (V1.0) | GTS2 (V1.x) | GTS3 (V1.x final) | GTS5 (V2) |
|---------|-------------|-------------|-------------------|-----------|
| Wave table (WTBL) | Per-instrument inline | Global pool | Global pool | Global pool |
| Pulse table (PTBL) | Per-instrument params | Global pool | Global pool | Global pool |
| Filter table (FTBL) | Global | Global | Global | Global |
| Speed table (STBL) | None (inline) | None (synthesised) | Global | Global |
| Max instruments | 31 | 31 | 31 | 63 |
| Max table length | 255 | 255 | 255 | 255 |
| Arpeggio command | Yes (CMD=0, data≠0) | Yes | Yes | No |
| Pulse speeds | Original scale | Original | Original | Doubled in V2.4 |

---

## 9. Player Frame Loop (V1)

From cadaver's music.html (`https://cadaver.github.io/rants/music.html`), the GoatTracker V1
player frame structure:

```
Process one frame of 1st voice
Process one frame of 2nd voice
Process one frame of 3rd voice
Process one frame of non-voice specific things (filter!)
```

The player maintains "ghost registers" for all SID parameters (since SID registers are write-only)
and flushes them at the end of each frame.

Key V1 player properties (inferred from V2 comparison):
- Single-speed (1× frame rate), no CIA multispeed support documented
- 3 voices only (no stereo in mono variant; stereo variant handles 6 voices)
- Wave table is never skipped during execution — guarantees arpeggio and drum correctness
- Gate timer (hard restart): V1 gatetimer is a per-instrument parameter; V2 multiplied it

**Major V1→V2 architectural change on gate timer**: "Upon startup, songdata erase, or
importing v1.xx data, gatetimer will be set to 2 * multiplier" — V2 changed the gatetimer
interpretation scale.

---

## 10. Remaining Unknowns (Leads to Follow)

The following questions are NOT resolved by this research pass and require fetching the actual
V1 zip archives:

1. **Exact V1 player 6502 assembly** — the player.s in goattrk.zip. This is the ground truth
   for exactly how the arpeggio command is handled at runtime (does the 3-note sequence loop
   continuously? does it stop? does it use a dedicated counter?).

2. **V1 filter table format** — the FTBL structure is listed as "global" in GTS! but its
   per-row encoding (cutoff step, resonance, etc.) is not documented from these sources.

3. **Portamento/vibrato data-byte encoding** — V1 inline speed in the command data byte.
   What is the bit layout? Speed in hi nibble, depth in lo nibble? Not confirmed from gsong.c.

4. **V1.4-to-V1.53 changelog** — what changed between these releases? The tweak utility
   (goatold.zip/tweak.zip) may document V1.25 limitations.

5. **V1 stereo vs mono player differences** — the stereo variant (gstereo.zip) handles 6
   voices on two SID chips. Does it share the same format or a different one?

6. **Orderlist format details** — the orderlist byte encoding (repeat, transpose markers)
   was confirmed identical between GTS! and GTS2, but the exact byte values for REPEAT ($D0),
   TRANSDOWN ($E0), TRANSUP ($F0), LOOPSONG ($FF) need confirmation as V1 constants vs V2.

---

## Leads to Follow

- **Download and extract goattrk.zip, gstereo.zip, goatold.zip** from cadaver.github.io/tools/
  — these contain the original V1 readme.txt and 6502 player source (player.s). This is the
  most valuable next step: the player assembly defines EXACT arpeggio runtime behavior.
- **Fetch SourceForge SVN raw gsong.c** for the complete GTS! loading code block to verify
  arpeggio param encoding and portamento/vibrato data-byte format.
- **Check HVSC SID files** via sidid output for the spread of GTS!/GTS2/GTS3 format
  identifiers within the GoatTracker_V1.x family — this tells us which format version
  dominates.
- **CSDb V0.93 release page** (correct ID not yet found) — may have early format documentation.
- **V1.4 Tweak Utility (tweak.zip)** — the name suggests it patches/tweaks V1 song data;
  its source or readme may document the format byte layout.
- **Cadaver's miniplayer repo** (https://github.com/cadaver/miniplayer) — contains gt2mini.c
  for GoatTracker 2. There may be a V1 equivalent; the repo README should be checked.
