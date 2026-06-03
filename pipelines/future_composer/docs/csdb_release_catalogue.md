---
source_url: multiple — see per-row source_url
fetched_via: direct (CSDb release pages + downloaded D64 contents)
fetch_date: 2026-06-03
author: various scene authors (per-row credits)
content_date: 1988-1990
reliability: primary (metadata) / primary (binaries verified by extraction)
---

# FC editor release catalogue — what each version actually contains

I downloaded the two main FC compilation disks from CSDb, extracted
every PRG, and verified load addresses + sizes. This table is the
ground truth on what binaries exist and where to get them.

## Master CSDb URLs

| FC version       | CSDb release id | URL |
|------------------|-----------------|-----|
| V1.0 (FIG, 1988) | 10604 | https://csdb.dk/release/?id=10604 |
| V2.0 (BB, 1988)  | 10605 | https://csdb.dk/release/?id=10605 |
| V2.1 (BB, 1988)  | 134469 | https://csdb.dk/release/?id=134469 |
| V2.1++ (Quartet) | 30048 | https://csdb.dk/release/?id=30048 |
| **V3.0 (Mnemonic Designs)** | 196273 | https://csdb.dk/release/?id=196273 |
| **V3.1 (Union)** | 7709  | https://csdb.dk/release/?id=7709 |
| **V4.0 (Dynamix)** | 2667  | https://csdb.dk/release/?id=2667 |
| **V4.1+ (Dynamix)** | 10607 | https://csdb.dk/release/?id=10607 |
| V5.0 (Warlords TMB) | 11644 | https://csdb.dk/release/?id=11644 |

## Disk image #1 — "futurecomposer + acid demo.D64"

CSDb internal file id **534**, served by V1.0/V2.0/V3.1/V4.1
release pages. URL:
`https://csdb.dk/getinternalfile.php/534/futurecomposer%20+%20acid%20demo.zip`
(149,605 bytes, contains a 174,848-byte D64).

Disk label: `*BINARY ZONE PD*`. PRG inventory:

| Filename            | Load  | Size (bytes) | Notes |
|---------------------|-------|--------------|-------|
| `FUTURE COMP.V1.0`  | $0801 | 8,088        | FIG 1988 editor |
| `FUTURE COMP.V2.0`  | $0801 | 16,851       | Beastie Boys editor |
| `FUTURE COMP.V3.1`  | $0801 | 18,699       | **Union 1990 — the canonical V3 editor** |
| `FUTURE COMP.V4.1`  | $0801 | 21,994       | Dynamix 1990 editor |
| `FUTURE RELOCATOR`  | $0801 | 2,897        | Re-locator utility for FC players |
| `FC INSTRUCTIONS!`  | $0801 | 20,107       | Compiled-BASIC instructions viewer (text obfuscated — needs MC unpack) |
| `^ - FC TUNES - ^`  | -     | -            | Section divider |
| `- VOICES IN SPC.`  | -     | 3,072        | Demo tune (V3-era) |
| `- HEART`           | -     | 3,328        | Demo tune |
| `- IT'S A SIN`      | -     | 3,072        | Demo tune |
| `- GAME OVER`       | -     | 3,328        | Demo tune |
| `REAL ACID DEMO`    | -     | 12,544       | Bundled demo |
| `ZOOLOOK (MUSIC)`   | -     | 8,704        | Demo |
| `REVOLUTIONS/DEEK`  | -     | 9,984        | Demo |
| `SPHINX (2 PTS)`    | -     | 13,824       | Demo |
| `STAR PAWS DEMO`    | -     | 14,592       | Demo |

The 4 short tunes (`- VOICES IN SPC.` etc) are the most useful
single-file V3 song-format test material — small enough to
hand-trace, real V3 driver bytes.

## Disk image #2 — "FutureComposerV4 + Note + TestTunes.D64"

CSDb internal file id **573**, from the V4.0 release.
174,848-byte D64. Disk label: ` MEGATRONIX PD! `.

| Filename            | Load  | Size  | Notes |
|---------------------|-------|-------|-------|
| `FUTURE COMP 4.0`   | $0801 | 29,367 | V4.0 editor |
| `KIPPER1 /COD` … `KIPPER14/COD` | - | 2.4–4.1 KB each | 14 demo tunes in V4 format |
| **`PLAYER $4000 [D]`** | $4000 | 82 | **80-byte standalone player wrapper** — fully disassembled in `csdb_fc_v4_player_disasm.md` |
| `PLAYER NOTE...`    | $0801 | 336 | BASIC instructions (recovered text in that doc) |

## Disk image #3 — "futurecomposerv3.d64"

V3.0 release file id **204446**, served by Mnemonic Designs release.
174,848-byte D64. Label `(M)/F.COMP. V3.0`.

| Filename             | Load  | Size  | Notes |
|----------------------|-------|-------|-------|
| `(M)/F.COMP. V3.0`   | $0801 | 11,411 | **The V3.0 editor binary (pre-Union)** |
| `(M)/F.COMP. NOTE`   | $0801 | 3,954 | Compiled-MC notes program |

V3.0 editor is **2.7 KB smaller than V3.1** (Union) — V3.1 added
the credit/intro scroll and an editor UI polish; the core driver
is essentially the same.

## Caveat — the FC editor PRG is the EDITOR, not the player

Every `FUTURE COMP.Vx.y` PRG loads at $0801 and includes:
- A BASIC stub doing `SYS <entry>`
- The full editor UI (menus, screen drawing, keyboard handler,
  pattern/sequence/instrument editors)
- The driver (which is what we actually care about — the part
  that gets emitted into stand-alone SIDs)

To extract just the driver, locate the FC_V3.x signature inside the
PRG and the surrounding routine boundaries. See
`csdb_sidid_signatures.md` for the exact pattern. For Hawkeye-style
SIDs, the driver-only block is typically 1.5–2.5 KB.

## Artifacts saved in-tree

All PRGs are saved under `pipelines/future_composer/artifacts/`:

- `FC_V1.0.prg` (8 KB)
- `FC_V3.1.prg` (18.7 KB — Union, with editor)
- `MoN_FC_V3.0.prg` (11.4 KB — Mnemonic Designs)
- `FC_V4.0.prg` (29.4 KB)
- `FC_V4.1.prg` (22 KB)
- `FC_V4_Player_4000.prg` (82 B — the standalone wrapper)
- `FC_Relocator.prg` (2.9 KB — see below)

## The FC Re-Locator

Released by Raze in 1989 (Internet Archive item
`d64_Future_Composer_Re-Locator_v1.3_1989_Raze`). 2.9 KB on the
acid demo disk. Tool for relocating an FC-format song from one
load address to another — used to embed FC songs into games. The
*existence* of a re-locator is itself a fact about the engine:

- FC V3.x output is **NOT relocatable at runtime** — absolute
  addresses are baked in. Hence the need for an offline re-locator.
- This is a key constraint for our pipeline: when rebuilding, we
  must choose a load address up front and bake every absolute
  reference accordingly.
