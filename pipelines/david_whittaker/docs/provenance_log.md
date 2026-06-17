# David Whittaker research — provenance log

Sweep completed 2026-06-17 (clean re-run with leaf agents; an earlier run was
killed by the session token limit and salvaged only Panther.asm). Per-file
provenance headers carry exact URLs; this is the consolidated attempt log.

## Primary / high-value (fetched)

| Source | Status |
|--------|--------|
| `github.com/realdmx/c64_6581_sid_players` → `Whittaker_David/Whittaker_David_Panther.asm` (dmx87) | **FETCHED** → `docs/src/`. The ONLY Whittaker tune disassembled in that repo (single commit 2023-04-23). |
| `github.com/neumatho/NostalgicPlayer` (C#, Amiga `.dw` parser) | fetched — most complete cross-platform format implementation; old(QBall)/new split, 3 period tables. |
| `github.com/rofl0r/c-flod` (C, Amiga player) | fetched — 42-variant 68000 detection, voice/effect/period structs. |
| `vgmpf.com/Wiki/.../David_Whittaker_(NES_Driver)` (Tony Bybell) | fetched — song-table byte layout, end-byte table, freq/vibrato tables. |
| `vgmpf.com/Wiki/.../Jason_Brooke` | fetched — the June 1986 rewrite, macro-asm workflow. |
| `github.com/cadaver/sidid` + `github.com/WilfredC64/player-id` | fetched — 5 alternative `David_Whittaker` signatures, no variant split. |
| local: `hvsc84/DOCUMENTS/Update00.hvs`, `Update02.hvs`, `Update_Announcements/{20020817,20240630}.txt`, `STIL.txt` | read — attributions/reclassifications; Prg2Sid 1.20 "Whittaker (2 variants)". |
| local: sidid signature DB + 103-SID binary fingerprint census | done — P1/P2/P3/P5/unknown breakdown. |
| `deepsid.chordian.net` / jsSID `jsSID-modified.js` | fetched — named "Whittaker player workaround" (gate-off = hard-restart). |
| CSDb scener #2598 + release/ripper pages (Whittex V1.0 #104167, DW Ripper #33379) | fetched — bio, rip catalogue, version timeline. |
| Remix64 / c64.com / karsmakers interviews | fetched — composing workflow, macro-expanded data. |
| CSDb Bansai Xenon ZX→C64 conversion notes | fetched — cross-platform data-compat confirmation. |
| archive.org "David Whittaker Music Mix (1988)(Defjam)" (Amiga) | located — oldest Amiga variant binary (not downloaded). |

## Leads NOT chased (for migration / a future wave)

- **realdmx (GitHub):** request Lazy Jones / Glider Rider / Red Max disassemblies (P2/P3 variants).
- **UADE** `players/DavidWhittaker` — original 68000 Amiga binary (primary Amiga RE source).
- **ExoticA** `EP_DWhittaker.lha` — Amiga EaglePlayer 68000 source (command table).
- **Bansai (CSDb #38332):** holds full Xenon player source + song data in C64 format (Jason Brooke variant) — CSDb PM.
- **Prg2Sid 1.20** (CSDb #238521): read its exact 2-variant identification logic.
- Download a 1988 Amiga `.dw` from archive.org to study the oldest Amiga binary.
- Refresh `hvsc84.csv` (`tools/build_sid_db.py`) to fix 7 P1 false-negatives.

## Not found (likely doesn't exist online)

- Original Whittaker driver source (hand-coded per game; never released as a reusable driver).
- A second published C64 disassembly (only Panther/P1 exists publicly).
- Scene-magazine deep-dive article on the routine (none surfaced).
