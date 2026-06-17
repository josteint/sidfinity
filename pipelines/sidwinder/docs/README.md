---
source_url: index (see individual files + provenance_log.md)
fetched_via: research-player sweep (6 parallel agents + orchestrator)
fetch_date: 2026-06-17
author: research synthesis (Jostein Trondal session)
content_date: 2026-06-17
reliability: primary (built on the official GPL source archive + HVSC local data)
---

# SidWinder — research docs index

Research-player sweep completed **2026-06-17**. **Outcome: the full GPL source
of the player + packer + editor was recovered and is committed under `src/`.**
There is no guesswork left for the format — the migration phase reads the asm
directly. Family state bumped `LITTLE → OK`.

## Engine identity

- **SidWinder** — C64 SID music editor + player by **Balázs Takács ("Taki")** of
  the Hungarian group **Natural Beat**.
- Code originally written **1994**; first public release **V01.22 (1999)**.
- **V01.23** (the version whose source we have) is a GPL release, **2000-03-15**,
  by **Levente Hársfalvi (TLC / Coroners)** — adds a Plus/4 port, relative labels,
  selectable SID base + freq table, and a relocating packer. The player is
  "_almost identical_" to V01.22 (per the PLAYER.ASM header).
- **HVSC #84: 117 SIDs** tagged `SidWinder` (purely via sidid). Top musicians:
  Factor6, Luca, Taki, Eclipse, then PCH / Zapac / Puterman / Phobos. Eclipse
  has tunes dated 2025 → still in active use.

## What the engine is (format in brief — all confirmed from `src/`)

- **3 voices, PAL only, VBI-driven** (PSID `speed = 0`, NOT CIA). Multispeed up
  to **16×** via repeated play calls.
- **Three entry points:** `$1000` init / `$1003` play (1×) / `$1006` multispeed
  play (effects-only inner call).
- Hierarchy: **track → sector → instrument**. Up to **32 subtunes, 96 sectors,
  64 instruments**.
- **7-byte instruments:** AD, SR, gate-off counter, + 4 pointers into the effect
  tables.
- **4 effect tables** (per the manual + PLAYER.ASM):
  - wave/arpeggio — 2-byte rows (waveform, arp offset)
  - filter — 3-byte rows ($D415/16/17 sweep)
  - pulse-width — 3-byte rows
  - slide/vibrato — 3-byte rows; `$FE` = drum/absolute-freq mode
  - `$FF` row = jump (loop) in every table.
- **Hard restart** is hardwired — fires on every new note / sector boundary
  (test-bit); min safe note duration ~4 frames.
- **Sector commands:** `$00–$5E` note, `$60–$6E` glide, `$6F` hold, `$70–$7E`
  slide, `$7F` finish, `$80–$BF` duration, `$C0–$FF` instrument-select.
  (One cross-source variance: `csdb_forum.md`'s binary read of `Radiation.sid`
  reports `$5F`=rest and `$FF`=loop — reconcile against PLAYER.ASM at migration.)
- **Track commands:** `$00–$7F` transpose, `$80–$DF` sector-play, `$E0–$EF`
  set-volume, `$F1–$FE` volume-slide, `$FF +byte` jump.
- **Known quirk:** glide/slide speeds are **absolute 16-bit freq deltas** (not
  semitone-normalised) — glide rate depends on the note's frequency. The Plus/4
  fixed-packer corrects an endpoint/glide bug that bites long songs.
- **Packed format:** HVSC tunes are *packer output* — `PACKER.ASM` strips unused
  areas, relocates to a chosen base, links the player in. The extractor must
  parse the **packed** layout, so `src/PACKER.ASM` is as load-bearing as
  `src/PLAYER.ASM`.

## Detection (sidid)

Single 27-byte signature, no V01.22/V01.23 split (the relocatable opcodes
survive relocation). From cadaver/sidid (== WilfredC64/player-id):

```
[SidWinder]
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```

Covers the voice-dispatch loop (speed-counter LDA/BEQ, DEC, DEY+JMP, command CMP
dispatch + STA SID). Details in `sidid_signature.md`.

## Recovered source — `src/` (the ground truth)

| File | What it is |
|------|-----------|
| `src/PLAYER.ASM` | **V01.23 player, 6502 (TASM→TDA), 1167 lines.** Primary RE reference. |
| `src/PLAY0122.ASM` | V01.22 player — diff against V01.23 to characterise the version delta. |
| `src/PACKER.ASM` | **Packer + relocator** — defines the packed/stripped on-disk format HVSC tunes use. |
| `src/ED.ASM` | Editor (138 KB) — defines the in-memory / data-file format the packer consumes. |
| `src/SIDR.ASM`, `src/VIEWER.ASM` | Standalone player ripper + viewer (secondary). |
| `src/SIDW0122.txt` | Taki's ~800-line V01.22 user+programmer manual — the prose format spec. |
| `src/SUMMARY.txt` | Command reference (track/sector/table opcodes). |
| `src/GENERAL.txt`, `PROGRAMM.txt`, `HISTORY.txt`, `README.txt`, `COPYING.txt` | Docs + changelog + GPL license. |
| `src/sidid_cfg_sidwinder_section.txt`, `player_id_sidwinder.txt` | Signature provenance. |

Full extracted source tree (incl. `PRE_0123/{0120,0122}`, `PLUS4/`, `TOOLS/`,
`.BIN` data tables) is in `tmp/sidwinder_research/sidwinder_src/` (scratch, not
committed — re-fetch the ZIP if needed; URL in provenance_log.md).

## Synthesised docs (start here for reading)

- `research.md` — full synthesis (best single overview).
- `format_spec.md`, `format_from_source.md` — structured format spec from the source.
- `csdb_forum.md` — incl. a per-version census of the 117 HVSC SIDs + a
  binary-level read of `Radiation.sid` (treat byte-level claims as
  *to-confirm-against-PLAYER.ASM*, since binary reads can drift).
- `wiki_codebase64_lemon64.md` — the Plus/4 World format description (best
  online write-up) + name-collision disambiguation.
- CSDb cluster: `csdb_release_notes.md`, `csdb_source_links.md`,
  `csdb_format_technical.md`, `csdb_author_context.md`, `csdb_author_group.md`,
  `csdb_summary.md`, `csdb_sidwinder.md`.
- `github_tools.md` — open-source tool survey (no parser exists; only sidid).
- `hvsc_docs.md`, `sidid_signature.md`, `deepsid_notes.md`.
- Archive cluster: `archive_survey.md`, `demozoo_natural_beat.md`,
  `wayback_ftp_mirrors.md`, `research_sweep_2026_06_17.md`.
- Forums cluster: `forum_forum64.md`, `forum_usenet_web.md`,
  `techarticle_sidwinder_overview.md`.

## Leads followed → yield

- **Zimmers GPL source ZIP** (the top lead from 4 of 6 agents) → **fetched +
  extracted; player/packer/editor sources committed to `src/`.** This closes the
  research goal.
- **Plus/4 World page** → best online format description (in
  `wiki_codebase64_lemon64.md`).
- **sidid / WilfredC64 player-id** → exact detection signature, single variant.
- **Name-collision check** (Raistlin/Genesis Project "SIDwinder" 2025; "Thomas
  Jansson" mention) → **unrelated modern SID-analyzer tool**, flagged in
  `github_tools.md` + `techarticle_sidwinder_overview.md`. Do not conflate.

## Leads NOT chased (low value — source already in hand)

- Predecessor Natural Beat releases (Naturality #8709, Harmony #5075, Taki's
  Music Analyzer #99142), Taki's defunct homepage, FTP mirrors — historical
  colour, no format value beyond the source we have.
- Forks: **PCH "Enhanced" (2011, #99574)** and **Draxish "V1.24 sub030"** —
  format-compatibility unconfirmed; only matters if their HVSC tunes fail
  detection/build. Defer to migration.

## Gaps (all fillable WITHOUT more online research)

1. **V01.22 ↔ V01.23 player diff** — both `.ASM` in hand; do at migration.
2. **Packed-format byte map** — `PACKER.ASM` defines it; summarise into a
   `disassembly.s`-style spec during migration (not done here — that's RE).
3. **Per-version axis confirmation across the 117 SIDs** — `csdb_forum.md`'s
   census (V01.14/20/22/23/36/37) is from binary reads and unverified; confirm
   via sidid + the recovered freq-table/header layout at migration.
4. **Fork compatibility** (PCH, Draxish) — verify only if their tunes fail.

## Migration starting point

- Player asm: `src/PLAYER.ASM`. Packed-format: `src/PACKER.ASM`. Prose spec:
  `src/SIDW0122.txt` + `src/SUMMARY.txt`.
- Canary candidates: a Taki original (e.g. `MUSICIANS/T/Taki/...`) for the
  reference V01.22/23 layout; an Eclipse 2025 tune to confirm the still-current
  build matches one signature.
- Verdict = the standard write-log instruction-sequence match. VBI-driven →
  flat Mode-1 comparison; multispeed tunes need the per-IRQ capture.
