---
source_url: https://hvmec.altervista.org/blog/wp-content/uploads/2010/05/dmc_5_docs.txt.gz (original V5.0 docs, primary) + https://tnd64.dreamhosters.com/music_scene.html section 3 (TND DMC 5 tutorial, secondary)
fetched_via: direct
fetch_date: 2026-06-12
author: synthesis by Claude (sidfinity research wave); underlying texts by The Syndrom/Crest+TIA (1993-94) and Richard Bayliss/TND (~2002-2009)
content_date: 1993-2009
reliability: primary (parameter set, table semantics, $4000 anchor) / inference clearly flagged where used
---

# DMC V5 format notes — the 8-byte instrument + 2-byte tables

Closes most of HOLE 1 (V5's 8-byte instrument format). Full source texts in
`dmc_v5_docs_original.txt` (first-party) and `tnd_dmc_tutorial.txt` §3.

## The 8 instrument parameters (RESOLVED at parameter level)

Both sources agree on the sound-editor parameter set and display order:

```
AD SR WV PU FL V1 V2 V3        (TND shows a literal instrument row:
0C 00 04 00 00 00 00 00         AD=$0C, WV→wave-table pos 4, rest 0)
```

| # | Field | Semantics (original docs wording) |
|---|-------|------------------------------------|
| 0 | AD | SID attack/decay → $D405 |
| 1 | SR | SID sustain/release → $D406 |
| 2 | WV | POINTER (position index) into the wave/"arpeggio" table |
| 3 | PU | POINTER into the pulse table. 00 = "no pulse restart" |
| 4 | FL | POINTER into the filter table. 00 = "no filter restart" |
| 5 | V1 | Vibrato delay |
| 6 | V2 | Vibrato speed ("useful are 01-05") |
| 7 | V3 | Vibrato width — only bits 0-2 used ($00-$07) |

**Memory anchor (primary):** the packer instructions say to check whether sound
#00 is used by inspecting **$4000-$4007** in the editor's memory — i.e. 8
contiguous bytes per instrument, row-major, starting at $4000 (editor layout;
packed-module location differs). Sound numbers are **$00-$1F** (32 max,
"SND ($00-$1F)").

**Inference (high confidence, needs one binary check):** stored byte order =
display order AD,SR,WV,PU,FL,V1,V2,V3. The $4000-$4007 emptiness test plus the
editor cursor walking left→right across exactly these 8 columns make any other
order unlikely.

## Where V4's other 5 bytes went (analysis)

V4's 11 bytes were AD, SR, wave-ptr, PW1-3, PW-limit, vib1, vib2, filter,
fx-flags. V5 drops PW1-PW3 + PW-limit + fx-flags and adds two table pointers:

- **Pulse behaviour** moved from 3 speed bytes + limit into the fully
  programmable pulse table (start value, per-frame add, frame count, loop).
- **Filter routing** moved from the fx-flag bits into the FL pointer +
  sector-level FLT/FRQ commands.
- **Drum mode** moved from fx-flag bit 0 into the wave table: test bit ($08)
  set in a wave entry's first byte = hi-freq/drum mode for that step.
- **Hard-restart suppression (tie)** moved to the sector SWITCH command.
- V5 vibrato keeps 3 bytes but re-defines them (delay / speed / width) vs
  V4's 2 packed bytes.

## The 2-byte tables (wave / pulse / filter)

All three tables use 2-byte entries addressed by absolute position index, and
the same loop marker: **first byte $90 = loop, second byte = absolute position
to jump to** ("direct-pointer looping"). One entry is consumed per frame.

### Wave ("arpeggio") table
- byte 0 = SID waveform/control value. Every bit usable EXCEPT bit 3 ($08),
  which is repurposed: **test bit set = drum/hi-freq mode** — the entry's
  second byte goes DIRECTLY into the freq hi register ($D401/$D408/$D40F).
  "Values above $87 are crap."
- byte 1 = semitone offset added to the playing note (arpeggio); in test-bit
  mode = literal frequency hi-byte.
- Examples (original docs + TND):
  - minor chord: `21-00, 21-03, 21-07, 90-00`
  - bass: `89-YY` (noise at fixed freq YY) then `41-00`
  - drum: `89-FF, 49-0B, 49-09, 09-00, 90-15` (note $49/$09 = test bit set)

### Pulse table
- Entry at position PU = **starting pulse** (12-bit; "leave the first nibble
  as it is").
- Then alternating pairs: next entry = **16-bit add value** applied per frame
  (two's complement to subtract: adding $FFF0 == subtracting $0010; the
  editor's `*` key complements a value), next entry = **number of frames** to
  apply it.
- `90-xx` loops to position xx.
- Drum example: `01: 08-00` (start $0800), `02: 00-00` (add 0), `03: 00-00`
  (count), `04: 90-02` (loop to 02).
- Position 00 is reserved: PU=00 means "no pulse restart" (keep the channel's
  running pulse program — pair with an init instrument).

### Filter table
"Works exactly as the pulse table, with one exception: all 16 bits are used."
FL=00 = no filter restart. NB: the V5.0 player only filters **voice 3**
(original docs: "filtering is only possible in voice 3").

## Misc V5 player facts (primary unless noted)

- Sectors usable: $00-$5F (96). No gaps allowed in used sectors/instruments
  (save drops everything after a gap).
- Track editor: TR+xx/TR-xx transpose, -END- with loop position operand,
  STOP!. Music setup: speed (never 00) + volume (≤ $0F).
- Sector data: **never use a parameter value above $FE — $FF means END; the
  packer scans for $FF** (so $FF terminates a sector in storage).
- Editor SYS $1200; instruments at $4000; packer SYS $2E00. Packed tunes:
  init $1000 / play $1003 (TND).
- Hard restart is built into the player ("proper hardrestart ... implemented
  in the player's coding").
- V5.0+ (CreaMD, CSDb #22938, Dec 2002) added audible sector editing, an
  extended sector window, track-play of edited sector, configurable
  fast-forward — **editor-side changes only**, no documented format change.

## Still UNKNOWN for V5 (needs RE from binaries)

1. Stored instrument byte order (the display-order inference above) — confirm
   against `DMC_V5.prg` (in tmp/dmc_hunt/) wave-pointer dataflow.
2. Packed-module memory map (where the 8-byte instrument block, 2-byte tables,
   tracks, sector pointers land after the $2E00 packer runs).
3. Sector command BYTE ENCODING for the ~14 V5 commands — see
   `dmc_sector_commands.md`.
4. Whether WV/PU/FL pointers are entry indices or byte offsets (display shows
   entry positions; ×2 for byte offset would be applied by the player).
