---
source_url: https://csdb.dk/getinternalfile.php/534/futurecomposer + acid demo.zip
fetched_via: direct (curl)
fetch_date: 2026-06-03
author: Union (1990) — repack of FC1.0 (Finnish Gold 1988), FC2.0 (Beastie Boys 1988), FC3.1 (Union 1990)
content_date: 1988-1990
reliability: primary
---

# CSDb — Future Composer V1.0 / V2.0 / V3.1 editor binaries

Downloaded the "futurecomposer + acid demo.zip" from CSDb release #7709
(Future Composer V3.1 by Union). The zip contains a single D64 image:

```
Length      Date    Time    Name
174848  2003-10-18 12:51   futurecomposer + acid demo.D64
```

## D64 contents (PRG files extracted)

| File | Track | Start blocks | Size (.prg) | Load addr |
|------|-------|--------------|-------------|-----------|
| `FUTURE COMP.V1.0` | T17 | 32 blocks | 8088 bytes | $0801 |
| `FUTURE COMP.V2.0` | T19 | 67 blocks | 16851 bytes | $0801 |
| `FUTURE COMP.V3.1` | T16 | 74 blocks | 18699 bytes | $0801 |
| `DISK MENU` | T10 | — | — | — |

All three editor binaries saved at:
- `/tmp/fc_research/fc_v1_0.prg`
- `/tmp/fc_research/fc_v2_0.prg`
- `/tmp/fc_research/fc_v3_1.prg`

The D64 itself remains at `/tmp/fc_research/futurecomposer + acid demo.D64`.

## Packing analysis

The V3.1 editor binary appears packed/crunched (the FC_V3.x signature
`EE 99 ?? EE 9A ?? EE 9B ?? A9` is NOT present as plain bytes — only
high-entropy garbage strings like `'2066 CODE'`, `'/8%#'`, etc.). The
editor uses a depacker stub at $0801 (standard BASIC SYS header) which
inflates the player code into RAM at runtime.

To extract the V3.x player runtime byte-exact would require:
1. Running the .prg in an emulator (VICE) to trigger the depacker.
2. Snapshotting memory after BASIC SYS jumps to the player.
3. Or: locating "2066 CODE" as a Section 8 / Equinoxe / Pu-239 cruncher
   signature and depacking offline.

The string `'2066 CODE'` (early in V3.1.prg) is likely the cruncher's
ID — searches suggest this is one of the popular C64 crunchers from
the late '80s scene (Equinoxe / Section 8 / Pu-238 / Time Cruncher
family). Identifying it would let us depack without VICE.

## Why this matters

- **FC V3.1 is the exact version Hawkeye.sid ships against** (per
  research.md: V3.x is the "Hawkeye driver"; sidid signature confirms
  V3.x match).
- **Editor binary contains the canonical player code** that gets copied
  into songs at save time — extracting it byte-exact gives us the
  ground-truth replay routine without having to reverse-engineer each
  HVSC Hawkeye .sid individually.
- The companion files in this zip (V1.0, V2.0) let us **diff player
  evolution** — V1.0 → V2.0 → V3.x — and identify the V3.x-only
  features (wave table per-frame programs, advanced filter table,
  pulse-arpeggio additions).

## Next steps (for byte-exact rebuild work)

1. Either:
   (a) VICE-snapshot the depacked editor at `$1000` after BASIC SYS,
       and disassemble the player there.
   (b) Identify the cruncher and write an offline depacker.
   (c) Skip the editor route and disassemble a SHIPPED FC V3.x song
       directly from HVSC (e.g. `hvsc84/MUSICIANS/[J]/Jeroen_Tel/Hawkeye.sid`
       or its V3.x peer) — the song already contains the depacked
       player runtime at its load address.

Option (c) is most direct: every FC V3.x SID is a `[load_addr, player +
song_data]` blob with `init = load_addr`, `play = load_addr + 6`. The
player code is verbatim at the head of every song.

## CSDb metadata on the FC V3.1 release

- Release: https://csdb.dk/release/?id=7709
- Year: 1990
- Released by: Union
- Code contributors: Charles Deenen (MoN, Scoop), Finland Cracking
  Service (Finnish Gold), Headline (Union), Softmaster (Audial Arts,
  Hitmen, Ruthless, Union)
- Music: EVS (20th Century Composers), Jeroen Tel (MoN)
- Graphics: Headline (Union)

## Related CSDb releases (for follow-up download)

| Version | CSDb ID | Year | By |
|---------|---------|------|-----|
| FC V1.0 | 10604 | 1988 | Finnish Gold |
| FC V2.0 | 10605 | 1988 | Beastie Boys |
| FC V2.0 | 47498 | 1988 | Beastie Boys + Mayhem |
| FC V2.1 | 134469 | 1988 | Beastie Boys |
| FC V2.1++ | 30048 | 1988 | Quartet |
| FC V3.1 | 7709 | 1990 | Union (downloaded) |
| FC V4.0 | 2667 | 1989 | Dynamix |
| FC V4.1+ | 10607 | 1990 | Dynamix (100%) |
| FC V5.0 | 11644 | 1992 | Warlords TMB Group |
