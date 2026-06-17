---
source_url: https://vgmpf.com/Wiki/index.php/David_Whittaker_(NES_Driver)
fetched_via: direct (WebFetch 2026-06-17)
fetch_date: 2026-06-17
author: VGMPF contributors (research attributed to Tony Bybell; Whittaker/Brooke interviews)
content_date: 2023-08-13 (wiki last-updated)
reliability: secondary (wiki; based on original source interviews + researcher analysis)
---

# VGMPF: David Whittaker (NES Driver)

Full URL: https://vgmpf.com/Wiki/index.php/David_Whittaker_(NES_Driver)

This is the richest publicly-available cross-platform technical document on the
Whittaker format family. The NES driver is a direct 6502 port of the C64/CPC
Jason Brooke rewrite, so the C64 and NES format architectures are closely related.

---

## Engine identity

- **Creator:** David Whittaker
- **Platform:** NES (Nintendo Entertainment System)
- **Programming language:** 6502 Assembly
- **First release:** Loopz (October 1990)
- **Total NES games:** 8
- **Origin:** Adapted from C64 driver; "the particular C64 driver was based on a
  version written by Jason Brooke" (i.e. the post-June-1986 Brooke rewrite)

---

## Format architecture (Tony Bybell analysis)

> "His music format IS assembler, but only as much as to represent absolute pointer
> addresses for data."

> "Whittaker had an excellent, macro-based system in place that at the source level
> was largely compatible from platform to platform."

The format is **not a standard module format**. Songs and effects are arranged by
typing numbers and labels (macros) into the driver source code. The "assembler"
is the format; macro expansion produces absolute pointer tables at assemble-time.

---

## Song table layout

**C64 (3 SID voices) — 7 bytes per sub-song entry:**

```
byte  0  : speed (tempo counter reload value)
bytes 1–2: voice 1 pattern pointer (lo, hi)
bytes 3–4: voice 2 pattern pointer (lo, hi)
bytes 5–6: voice 3 pattern pointer (lo, hi)
```

**NES (4 2A03 voices) — 9 bytes per sub-song entry:**

```
byte  0  : speed
bytes 1–2: voice 1 lo/hi
bytes 3–4: voice 2 lo/hi
bytes 5–6: voice 3 lo/hi
bytes 7–8: voice 4 lo/hi
```

---

## Pattern format

Patterns are byte streams, terminated by a **platform-specific end byte:**

| Platform  | End byte |
|-----------|----------|
| C64       | `$88`    |
| ZX Spectrum | `$87`  |
| NES       | `$FF`    |

A `0,0` pointer value at the end of the track sequence causes the song to repeat
from the beginning of the sequence.

---

## Effect byte ranges (from VGMPF wiki)

Bytes in patterns split into:
- **Note bytes** (low values): play pitch
- **Effect bytes** (high bit set or specific ranges): commands
  - Speed multiplier: rows to wait
  - Sample/instrument select
  - Envelope reference
  - Arpeggio reference
  - End/Stop, Mute, Wait, Vibrato stop (0 bytes following)
  - Transpose, Speed (1 byte following)
  - Slide, Vibrato (2 bytes following)

---

## Vibrato implementation (C64 vs NES difference)

**C64:** Vibrato depth is scaled per octave. Higher octaves → deeper vibration.
This is because C64 frequency is encoded as a 16-bit linear value; the same
additive delta spans a larger proportion of lower frequencies.

**NES:** Vibrato tables do NOT scale by octave.
> "This limitation doesn't exist in C64 as it encodes frequency differently and in
> fact he scales vibration depth up per octave."

At the highest NES frequencies, vibrato is disabled entirely to avoid audible
artifacts.

---

## Sound parameter tables (instrument effects)

> "NES contains special tables similar to 'soundparameters' found on C64 editors
> such as Future Composer. These encode vibrato and tremolo information."

Structure: byte sequences where the **final byte has its high bit set** (same
convention as arpeggio sequences in C64 Panther — `$88` or any byte >= `$80`
terminates the sequence).

---

## Frequency tables

Two implementations identified:

| Variant | Range | Notes |
|---------|-------|-------|
| Whittaker standard | A-1 (hex 3E7) to G-7 (hex 11) | Used in Loopz, Elite, etc. |
| Manfred Trenz modification | A-1 (hex 3D5) to C-6 (hex 32) | Super Turrican NES only |

Trenz received Whittaker's source code and modified the frequency table for
Super Turrican. The C64 Panther frequency table (91 entries, A-1 to B-8) is
separate from these NES tables.

---

## Driver history timeline (C64 focus)

| Date | Event |
|------|-------|
| Late 1985 | Whittaker writes first C64 driver; "minimalist, tuned at 424 Hz" |
| Before June 1986 | Game programmers at Binary Design complain driver is slow |
| June 1986 | Jason Brooke rewrites CPC driver: "shorter, faster, more flexible"; adds flexible chords, envelopes, pitch bends |
| Late September 1986 | Brooke rewrite "adapted to more platforms and released" (C64 + ZX) |
| Autumn 1987 | Whittaker stops using SID filter (except engine sounds) |
| By 1991 | Driver used without major updates; then Whittaker moves to EA / new platforms |
| October 1990 | First NES game using Whittaker driver: Loopz |

---

## NES game list

| Game | Date |
|------|------|
| Loopz | 1990-10-?? |
| Elite | 1991-??-?? |
| Castelian | 1991-06-?? (sole Japanese release) |
| Krusty's Fun House | 1992-09-?? |
| Spider-Man: Return of the Sinister Six | 1992-10-?? |
| Alfred Chicken | 1993-??-?? |
| Super Turrican | 1993-07-22 (Manfred Trenz modification) |
| The Lion King | 1995-05-25 (used without Whittaker's involvement) |

Unreleased NES titles: 007 Licence to Kill, Ferrari Grand Prix, Populous, Tip-Off.

---

## Researcher attribution

**Tony Bybell**: Provided extensive analysis of NES driver architecture; noted
similarities to the Jason Brooke C64 rewrite; described format as "assembly-based
data with macro expansion rather than true compiled code."

---

## Leads to follow

- Full VGMPF DW article: https://www.vgmpf.com/Wiki/index.php/David_Whittaker
- Jason Brooke VGMPF article: https://www.vgmpf.com/Wiki/index.php/Jason_Brooke
- Jason Brooke c64.com interview: https://www.c64.com/gt_display_interview.php?interview=21 (SSL cert issue — try curl)
- Tony Bybell (NES researcher who reverse-engineered the NES driver format)
- VGMPF Talk pages for both David Whittaker and NES Driver articles
