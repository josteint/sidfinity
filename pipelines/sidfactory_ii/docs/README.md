# SID Factory II — research docs index

Player family: **SID Factory II** ("SF2"), by Thomas Egeskov Petersen ("Laxity"),
with JCH (Jens-Christian Huus) and Youth (Michel de Bree). GPL v2, open source.
Repo: https://github.com/Chordian/sidfactory2 · CSDb: #210571 · blog: https://blog.chordian.net/sf2/

HVSC #84 footprint (engine = `SidFactory_II/Laxity`): **377 SIDs**. Sibling
classifications also present: `SidFactory/Laxity` (39, the V1 editor) and the
JCH `NewPlayer`/NP20 lineage that SF2 grew out of.

Research sweep date: **2026-06-13**. Two waves of parallel sonnet agents
(GitHub source · CSDb/scene · official manual · driver internals · packed-export ·
effect semantics). This was GATHER-only — no RE, no siddump/py65. The migration
phase redoes the 6502-level RE properly (see Open items).

## TL;DR for the migration phase

- **The format is fully open.** The 6502 driver `.asm` is NOT in the repo, but
  the editor's C++ is, and it is effectively a complete reader/writer library
  (`sf2_interface.cpp`, the `datasource_*` and `driver_info.*` files). Every
  pack/unpack algorithm is documented byte-for-byte below.
- **A `.sf2` editor file is self-describing** via a block chain at `load+2`
  (magic `0x1337`), but **the EXPORTED .sid in HVSC is NOT** — the packer strips
  all descriptor metadata. See the export verdict below; this is the single most
  important fact for the extractor.
- **All SF2 tunes are single-speed** raster-IRQ ($D012). Multispeed is unsupported
  by every driver (listed as a future feature). → Mode-1 frame-by-frame verdict
  applies cleanly; no CIA/per-IRQ machinery needed.
- **Modular drivers 11–16** share the data model; behavioral diffs are bounded and
  documented (`fx_driver_version_behavior.md`). Driver 11 dominates HVSC.

## Extractor anchoring (the export verdict — read first)

The packer copies only (1) the relocated driver code blob and (2) the packed data
sections after it. The `0x1337` descriptor block and the `$0FFB` aux pointer are
editor-only and **never written to the exported .sid**. So a HVSC SF2 extractor
must:

1. **Fingerprint the driver version** from the code blob (sidid pattern in
   `github_sidid_fingerprints.md` identifies the family; sub-version 11.00–11.05
   needs a finer byte probe — OPEN).
2. **Anchor on the PSID header** `InitAddress` / `UpdateAddress` (reliable: they
   point at the relocated driver's init / play entry points).
3. **Locate data tables** at fixed offsets within the known driver layout, OR by
   reading the (packer-patched, already-relocated) ABS operands of the driver's
   pointer-array load instructions. The order-list and sequence pointer arrays
   (C64 lo/hi split) are the entry points to all musical data.
4. **Multi-song**: `InitAddress` points at an injected stub (fixed byte pattern
   `85 XX 0A 18 65 XX AA A0 00 BD …`); the per-song order-list pointer table sits
   immediately before it. See `packed_multisong.md`.

## File index

### Format & byte layout
- `github_format_spec.md` — **the master byte-level spec** (519 lines): sequence
  stream, order-list packing, all tables, instrument 6-byte row, column- vs
  row-major in-memory layout. Start here.
- `manual_table_formats.md` — same tables from the official manual/driver notes
  (independent cross-check of the source-derived spec).
- `driver_descriptor_format.md` — the `.sf2` editor-file block chain (9 block
  types, field-by-field). Editor-file only; stripped on export — but it documents
  what each table IS and where the editor expects it.
- `github_parser_notes.md` — C++ parser internals; the pack/unpack algorithms.

### Effect / register semantics
- `fx_register_semantics.md` — **every command + table effect → exact $D4xx
  register**, per-frame update model (driver 11). The re-emitter reference.
- `fx_table_execution.md` — per-tick execution algorithms for wave / pulse /
  filter / HR / arp / tempo / init tables; set-vs-add rows, jump/loop, $D418
  filter-mode nibble mapping, 12-bit PW packing.
- `manual_command_reference.md` / `manual_effect_semantics.md` — manual-sourced
  command table + register mapping (cross-check).

### Driver versions
- `fx_driver_version_behavior.md` — **behavioral diff 11/12/13/14/15/16** + the
  11.00–11.05 sub-version history; driver 13 Hubbard-emulation specifics; confirms
  no multispeed anywhere.
- `github_version_differences.md` / `csdb_version_differences.md` — version/format
  deltas from source and from CSDb release notes.
- `driver11_source.md` — behavioral reconstruction of driver 11 from the C++
  (no asm in repo).

### Packed / exported output
- `packed_export_format.md` — the full pack pipeline, ZP relocation,
  `MoveDataToTopAddress`, PSID header encoding.
- `packed_auxiliary_data.md` — aux block format + why it's absent from HVSC files.
- `packed_multisong.md` — multi-song stub injection (annotated 6502 stub bytes +
  fixup offsets).

### Lineage / scene
- `csdb_release_notes.md` — release chronology (9 builds 2020→2026, driver .prg
  inventory).
- `csdb_forum_discussion.md` — lineage: JCH OldPlayer 1987 → NewPlayer → NP20.G4
  → SF2; SF2 is a SEPARATE family from the DMC player line.
- `github_player_source.md` — driver inventory + the NP20 (JCH) format decoded
  from `converter_jch.cpp` (relevant to the `jch_newplayer` family too).
- `github_sidid_fingerprints.md` — sidid byte patterns.

### Verbatim third-party source (`src/`)
Editor C++ that authoritatively defines the format (kept so `file:line` citations
don't rot): `sf2_interface.{h,cpp}`, `driver_info.{h,cpp}`, `driver_utils.cpp`,
`datasource_orderlist.*`, `datasource_sequence.*`, `converter_jch.cpp`,
`packer_cpp.cpp`, `psidfile_cpp.cpp`, `auxilary_data_*_cpp.cpp`, and the official
`notes_driver11.txt`–`notes_driver16.txt` + `user_manual_20260314.txt`.

## What we have (quality assessment)

| Need | Status |
|---|---|
| Order-list / sequence packing | **SOLVED** — byte-exact from C++ source + manual |
| Instrument + wave/pulse/filter/HR/arp/tempo table layouts | **SOLVED** — byte-exact, two independent sources agree |
| Command table semantics (driver 11) | **SOLVED** — every command → register |
| Per-tick table execution model | **SOLVED at the behavioral level** (exact within-frame write ORDER is OPEN) |
| Relocation / pack pipeline | **SOLVED** — from `packer.cpp` |
| How to locate tables in a HVSC .sid | **SOLVED (method)** — fingerprint + PSID anchors + driver-layout offsets |
| Driver version diffs | **SOLVED** — bounded, documented |
| Single- vs multi-speed | **SOLVED** — all single-speed |

## Open items (defer to the migration/RE phase — each is a disasm trace, not a websearch)

1. **Exact within-frame SID write ORDER** (freq → ctrl → ADSR …). Mode-1 cares
   about order, not cycle. Trace: `siddump --writelog` one driver-11 tune, read the
   per-play() sequence.
2. **The note→frequency table** (256 × 2 bytes). Known to be a standard PAL
   Laxity/JCH table; exact values need disasm of `sf2driver11_05.prg` at
   `driver_code_top + N`. Trace: locate via the freq-load instruction's ABS operand.
3. **Driver 11 sub-version discriminator** (11.00–11.05) — finer byte probe than
   the family sidid pattern.
4. **Driver 13 (Hubbard-emu)** exact dive step / arp cycle / noise-prefix frame
   count / PWM step — semantics known, magnitudes need disasm.
5. **Driver 14 "immediate-response" HR** exact same-frame gate timing.
6. **Vibrato LFO shape/table** (sine vs triangle, size) and osc-reset ($10) write
   timing relative to note-on.
7. **Auxiliary data full chunk format** (`auxilary_data_collection.cpp`) — only
   needed if we ever read editor `.sf2` files, NOT for HVSC .sid extraction.

All Open items are confined to the 6502 binary and are the proper subject of the
`disassembly.s` + extractor step. Nothing further is fillable from online sources.

## Suggested first migration target

Driver-11 single-subtune tunes dominate. Pick a long, well-known driver-11 tune
from HVSC (`SELECT path FROM sids WHERE engine='SidFactory_II/Laxity' ORDER BY
songlength_s DESC`) and confirm the driver fingerprint before extracting.
