---
source_url: https://csdb.dk/release/?id=253740 (downloads 311671=d2ct.d64, 311672="Compotech The Force full release.d64")
fetched_via: direct (curl, via csdb.dk/storage redirect)
fetch_date: 2026-06-16
author: Astral / Mister Giga (release); Compotech editor by X-Ample Architectures
content_date: release 253740
reliability: primary (actual disk images)
---

# CSDb #253740 "Docs 2 Compotech" — what's actually on the disks

The disasm-cluster agent flagged this release as "likely contains format
documentation for the evolved engine." **We downloaded both disk images and
checked — that characterization is WRONG.** Recording the correction so a
future session doesn't re-chase it expecting a format spec.

## `d2ct.d64` (CSDb file 311671)
D64 directory: a single PRG `DOCS2COMPOTECH!` (21 blocks, load $0801).
Extracted + decoded (PETSCII + screen-code passes). It is a **scene
greetings / credits / release-notes "docs" viewer** (a note-writer scroller),
NOT a technical manual. Legible content: viewer key controls
(`SPACE`, `RUNSTOP..`, `ENTER A LINE`, `CRUNCHING...`), greetings, an author
contact (`...IS MY ADDY:` + a Finnish phone `+358 (9)1...480 55`), `LEGAL`
notice, end credits (Mister Giga / Astral), and `MUSIC BY GM IN JCH'S NP-V19`
(the disk's background tune uses JCH NewPlayer v19 — incidental). **No
byte-layout / format documentation.**

"Docs 2 Compotech" = "docs TO [the] Compotech [release]", i.e. scene notes,
not "documentation OF the Compotech editor format."

## `Compotech The Force full release.d64` (CSDb file 311672)
D64 directory:
```
PRG 70 blk  COMPOTECH/FORCE     <- main release (the Compotech editor/demo)
PRG  4 blk  1.SFX DEMO
PRG 11 blk  2.MUSIC DEMO        <- player + a tune
PRG 21 blk  DOCS2COMPOTECH!     <- same docs scroller as above
```
This disk DOES carry the actual **Compotech editor + player** code. BUT:
1. Extracting/disassembling that player is reverse-engineering → migration
   phase, out of scope for the gather sweep.
2. **Compotech is the `xample` sidid family, NOT `lords_of_sonics`.** It's the
   *evolved* engine Schneider co-wrote after joining X-Ample (1989). For the
   LordsOfSonics/MS family the ground-truth editor is **Parsec Music Editor
   V5.1 (CSDb #10744)** — a different, earlier tool.

So these disks are filed here (the lead originated here) but are most relevant
to a future **xample** migration. Disk images kept alongside this note so the
artifacts don't have to be re-fetched.
