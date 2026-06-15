---
source_url: orchestrator synthesis (this dir)
fetched_via: synthesis
fetch_date: 2026-06-15
author: research-player sweep (6 parallel sonnet agents + orchestrator)
content_date: 2026-06-15
reliability: secondary (index over the per-file primary/secondary sources)
---

# Vibrants/Laxity — research docs index

**Engine:** the original **Laxity Editor** player (HVSC engine string `Vibrants/Laxity`,
179 SIDs), by **Thomas Egeskov Petersen ("Laxity")** of Vibrants / Maniacs of Noise.
Composed *directly in a machine-code monitor* from ~1987; the editor (TFA → v3.34/3.35)
came later. This player is the **ancestor of the entire JCH NewPlayer line** and, through
it, of **SID Factory II**. JCH reverse-engineered Laxity's player in 1988, was told to
stop, and wrote NewPlayer instead (see `csdb_jch_firsthand_account.md` / `laxity_orig` README).

`research-player` sweep status: **COMPLETE** (this 2026-06-15 sweep → `engine_docs` state `OK`).

## The central research finding

**The original Laxity player was never published as source.** It survives only as:
1. The **HVSC binaries** (179 SIDs) — RE belongs to the migration phase, not here.
2. The **SIDId signature** (5 AND-lines) — decoded opcode-by-opcode below.
3. **JCH's first-hand testimony** that NewPlayer's pulse/filter step-table system is
   *"the same system as used in LAXITY's player"* — so the well-documented JCH/CheeseCutter
   format is our **best proxy** for the original, with the caveat that JCH redesigned the
   instrument byte layout repeatedly (v14 → v15 → v20) as it diverged.
4. **Authentic original-format data:** 6 `.DAT` files JCH composed *in Laxity's player* in
   1988, preserved at `src/laxity_orig_dat/` — the closest ground-truth binary for the
   original data layout (the `.SID` siblings are CSDb text stubs, not playable).

So this dir documents the format along the lineage **Laxity → JCH NewPlayer (v12→v21) →
CheeseCutter → SID Factory 0.5 → SID Factory II**, and flags exactly where the original
Laxity player is *inferred* vs *confirmed*.

## What we have (per-frame write model, from SIDId signatures — `sidid_opcode_analysis.md`)

Confirmed for the **original** Laxity player directly from its signature:
- **Freq write order is hi-before-lo / `$D401` before `$D400`** (`STA $D401,Y` then `STA $D400,Y`); voice stride Y ∈ {0,7,14}.
- Note index is `ASL`-doubled into a word-aligned freq table; slide is an `ADC abs,X` accumulator.
- `STA $D404,Y` control-register writes for all 3 voices; `$D416` filter-cutoff-hi sweep with a BIT/BVS direction flip.
- Duration model uses **count-up `INC abs,X`** plus **4 nested `DEC`/`BPL` counters** per voice (note + 3 effect counters) — NOT Hubbard's single DEC.
- Play entry is at **init+$06**. Pulse-width ($D402/$D403) is **absent** from the signature — open question whether the original player has PW at all (`sidid_opcode_analysis.md`, gap #6).

## File index

### Synthesis / start here
- **`sidid_opcode_analysis.md`** — per-fragment 6502 decode of every signature → the original player's write model. **Read first.**
- `src/article_np21_format_synthesis.md` — byte-level format synthesis across all sources (instrument 8B, wave 2-col, pulse/filter 4B pointer-chained, sequence pairs, orderlist, hard restart, write order). The single best format reference (JCH-proxy).
- `github_parser_notes.md` — player family tree + NP20-vs-SF2 distinction + sequence/orderlist parse algorithms (from SF2 C++).
- `hvsc_engine_taxonomy.md` — HVSC counts + version lineage 1987–2026.

### The original Laxity player (closest to target)
- `csdb_jch_firsthand_account.md`, `src/laxity_orig_readme.txt` — JCH's account; confirms `.DAT` data extension + player/data separation + Turbo-Assembler distribution.
- `src/laxity_orig_dat/*.DAT` — **authentic original-Laxity-format music data** (6 tunes, 1988). Migration-phase decode target.
- `csdb_technical_context.md` — early memory map (data $0F00–$2000, instruments ~$1700, init $0900/SYS2304; 3x-speed variant at $4000, 97-byte player).
- `csdb_player_detection.md`, `forum_sidid_signatures.md`, `sidid_signatures.md` — all 12 family signature blocks, verbatim + annotated.

### SIDId / identity / authorship
- `sidid_signatures.md` — complete verbatim extraction of all Laxity/Vibrants/JCH signatures + HVSC counts; confirmed identical to cadaver/sidid master.
- `wiki_sidid_nfo_authorship.md` — `Vibrants/JO` = **Poul-Jesper Olsen** (distinct engine, own pipeline `vibrants_jo/`); `JCH_OldPlayer` = JCH composing *in Laxity's format* (32 SIDs — likely same player binary, different data).

### JCH NewPlayer (the documented descendant = format proxy)
- `github_jch_source.md` — JCH editor memory map, $0F00 pointer table, NP20 data layout.
- `src/jch_editor37_source.txt` — full 96 KB JCH editor v3.03 assembler source (1995).
- `src/jch_np20g4_full_instructions.txt`, `src/jch_np15g6_full_instructions.txt` — JCH's own format manuals (the "same system as Laxity" statement lives here).
- `src/jch_np21g4_source_glover.txt`, `src/jch_np21g5_source_glover.txt`, `src/jch_np21g6_glover_notes.txt` — Glover/Samar NP21 6502 source ("Based on JCH NP 21.G4 by Laxity/VIB").
- `jch_player_format_primary.md`, `archive_jch_editor_complete_docs.md` — extracted instrument(8B)/arp/pulse/filter/super-table/sequence specs across v12–v20.
- `wiki_codebase64_jch20g4_format.md`, `src/article_codebase64_jch20g4_format.md` — Codebase64 NP20.G4 fixed-memory-layout article.

### CheeseCutter (most deeply annotated NP21 reimplementation = per-frame oracle)
- `src/cheesecutter_player_v4.acme` — 1763-line ACME source, "Based on JCH NP 21.G4 by Laxity/VIB". The reference for exact $D400–$D418 write order.
- `src/disasm_cheesecutter_player_v4_annotations.md` — enums, routine behaviours, memory map, effect state machine.

### SID Factory 0.5 / II (Laxity's own later format thinking)
- `src/laxity_sf05_driver5_docs.txt`, `src/laxity_sf05_driver6_docs.txt` — Laxity's own 2006 driver docs (Driver 5 = 8B instr/3B tables; Driver 6 = 6B instr/2B tables).
- `archive_sidfactory05_alpha_drivers.md` — SF 0.5 alpha analysis.
- `github_sf2_driver.md`, `archive_sidfactory2_drivers.md`, `src/sf2_notes_driver11..16.txt`, `src/sf2_driver_info.h` — SF2 drivers 11–16 byte layouts.
- `src/sf2_converter_jch.cpp`, `src/sf2_datasource_{orderlist,sequence}.cpp` — authoritative SF2-side NP20 parser + orderlist/sequence pack-unpack (C++).
- `forum_sidfactory2_blog_instruments.md` — SF2 instrument tutorial layout.

### Provenance / history
- `external_sources.md` — every web source fetched, per-entry provenance.
- `csdb_release_notes.md`, `csdb_version_history.md`, `forum_csdb_laxity_editor_releases.md`, `wiki_chordian_jch_timeline.md`, `wiki_sidpreservation_tracker_entry.md` — release metadata + dated lineage.
- `provenance_log.md` — every URL attempted (fetched/failed) so future waves don't re-fetch.

## What each priority need looks like now

| Need | Status | Where |
|---|---|---|
| Original player **source** | **Does not exist publicly** (confirmed ×6 agents). RE-only. | — |
| Original per-frame write model | **Partial, confirmed** from signature | `sidid_opcode_analysis.md` |
| Format byte layout | **Strong (JCH/CC proxy)** + authentic `.DAT` samples | `src/article_np21_format_synthesis.md`, `src/laxity_orig_dat/` |
| Other tools' parsers | **Have** (SF2 C++, CheeseCutter ACME) | `src/sf2_*.cpp`, `src/cheesecutter_player_v4.acme` |
| Version differences | **Have** (v12→v21→SF2) | `archive_jch_editor_complete_docs.md`, `hvsc_engine_taxonomy.md` |
| Effect → register semantics | **Strong** for the JCH line; **inferred** for original | CheeseCutter annotations + JCH manuals |

## Gaps — and which phase owns each

**Fillable only by RE of our own binaries (migration phase — NOT research):**
1. The exact byte layout of the **original** Laxity-player `.DAT`/SID data (instrument size, table strides, command set). Start: decode `src/laxity_orig_dat/*.DAT`, and disassemble one HVSC tune (e.g. `Laxity/Fast_Stuff_1.sid`; init/play from header) with `tools/seed_disassembly.py`.
2. Whether the original player has **pulse-width** at all (absent from signature).
3. Whether **`JCH_OldPlayer`** (32 SIDs) shares the same player binary as `Vibrants/Laxity` — if so, one extractor covers both.
4. **CIA/multispeed** subtune census (`--writelog-per-irq`) for the 3x-speed / quattro variants.
5. The exact diff between original-Laxity and JCH-v20 instrument byte assignment (JCH says tables match; instrument bytes were redesigned).

**Fillable online but deprioritised (RE would resolve faster; left as leads in `provenance_log.md`):**
- `JCH_SRC.D64` (in the downloaded JCH package) — v17/v19/v20.G4 player source + NP-Packer v5.3.
- `NP22-25 docs.doc` (CSDb #100406), SF2 user-manual pp.13+ — post-NP21 / SF2 byte detail.
- Disassembling the editor D64s (`Laxity_Editor_V32-3_34.d64`, `TFA_Editor_3_24.d64`) or the 97-byte `3xplayer.prg` — these *contain* the original player, but extracting it is RE.

**Probably unfillable online:** the original 1988 monitor-composed player source — it was hand-distributed in Turbo Assembler form and never released publicly.
