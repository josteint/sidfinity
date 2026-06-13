# Soundmonitor / MusicMaster — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-13).

Soundmonitor, by **Chris Hülsbeck**, published in **64'er Magazin 10/1986**
(Markt+Technik) as a ~5-page type-in listing. ~3,625 HVSC tunes (5th-largest
family), 0 migrated. The standalone replayer is **MusicMaster** (init=$C000,
play=$C020 in the canonical build).

A six-cluster sweep ran 2026-06-13. Outcome: **well-documented and ready to
disassemble.** Unlike most editors, the original code is *public* (magazine
type-in), and there's a complete hand-annotated disassembly already on disk.

## Start here (canonical, grounded in the disassembly)

1. **`spec_extraction_plan.md`** — ordered binary→USF checklist (the parsing
   target), grounded in the local JC64dis disasm.
2. **`spec_write_model.md`** — per-frame `$D400-$D418` write model for the
   Mode-1 instruction-stream verdict.
3. **`github_jc64dis_local_disasm.md`** — the **decoded local JC64dis
   hand-annotation** (Stefano Tognon): 302 labels / 290 block + 378 cell
   comments extracted from `tmp/jc64/doc/example/SoundMonitor_shades.dis`
   (gzip'd JC64dis serialization, cracked this session). Richest layout source.
4. **`archive_64er_1986.md`** — the **primary published source**: the full
   64'er 10/1986 OCR (archive.org `64er_1986_10`), Hülsbeck's own manual +
   the 24-register sound-parameter table + the "Tabelle 1" memory map +
   8 demo-patch fixtures.

## ⚠ Critical correction: editor model ≠ replayer format

`research.md` describes the **editor's on-screen data model** (the
`SP TRK TR ST` rows, "24 parameters"). The **MusicMaster replayer** — what the
3,625 HVSC SIDs actually run, and our extraction target — reads a **compiled**
layout (per `spec_extraction_plan.md` + the disasm):
- master sequence = **4 parallel 16-bit pointer arrays** (`voice{1,2,3}TableIndex`
  + `instrTableIndex`) + 3 transpose byte-arrays + a `progIndexTable` orderlist
  (`$FF` = end → next byte = loop index). NOT `SP TRK TR ST` rows.
- sound patch the replayer reads = a **64-byte ($40) record**, not 24 (24 =
  editor's user-editable count). Verbatim offset map in `spec_extraction_plan.md` §3.
- per-note byte carries only note value (`$00`=rest/gate-off, `$80`=tie);
  **instrument is per-order-position**, not per-note; options come from instr
  fields + `specialCtrlVoice` (`#$30` split), not an in-note nibble.

## Full file index

| Topic | Canonical | Corroborating |
|---|---|---|
| Extraction plan | `spec_extraction_plan.md` | — |
| Per-frame write model | `spec_write_model.md` | `csdb_release_and_downloads.md` (empirical `siddump --writelog`) |
| Annotated disassembly | `github_jc64dis_local_disasm.md` | — |
| Primary published source | `archive_64er_1986.md` | `csdb_namelessalgorithm_RE.md` |
| RE blog (via Wayback) | `archive_wayback_namelessalgorithm.md` | `csdb_namelessalgorithm_RE.md` |
| sidid signatures / variants | `sidid_signatures.md` | `github_sidid_signatures.md`, `csdb_pouet_and_parsers.md` |
| Variant lineage / taxonomy | `deepsid_player_taxonomy.md` | `forum_csdb_tracker_history.md`, `forum_wikis_c64wiki_vgmpf.md` |
| Tool landscape | `github_parser_notes.md` | `csdb_pouet_and_parsers.md` |
| Usenet / FTP inventory | `forum_usenet_csbm.md` | — |

Multiple files per topic = independent sources that **agree**. Every file has a
provenance header; `provenance_log.md` lists URLs hit/blocked. (Note: the
namelessalgorithm blog 404s live but was captured via Wayback — see
`archive_wayback_namelessalgorithm.md`.)

## What's solved

- **Public source + manual**: 64'er 10/1986 full OCR (article + 24-register
  table + memory map + demo patches).
- **Annotated disassembly**: the cracked local JC64dis project — full routine
  labels, table addresses, per-`$D4xx`-write comments.
- **Compiled replayer layout**: pointer arrays + 64-byte sound records +
  `progIndexTable` orderlist + bar/note grammar.
- **Per-frame write model**: register-major sweep; per-voice freq/PW/AD/SR then
  **control written last** (gate edge); note-on writes control twice; `$D418`
  last. **CIA-timed (PSID speed=1)** → use `siddump --writelog-per-irq` + the
  CIA per-play verdict (CLAUDE.md Trap C), not the flat per-frame capture.
- **Variant taxonomy + detection signatures** (below).

## What remains (migration, not research)

- **Fingerprint the 3,625 members into builds** before bulk extraction
  (`tools/engine_fingerprint.py`; template `project_fc_fingerprint_and_standard`).
  `load_addr=$0000` for all; init/play vary — **anchor by code signature, not
  address**. `$C000/$C020` = 1,182; a second build has play-delta `+$475`;
  `play=$0000` = 1,301.
- **Confirm init priming** — the canonical `$C000` init is stubbed in the Shades
  rip; disassemble a clean `init=$C000` member (e.g. `Huelsbeck_Chris/Shades.sid`).
- **Arpeggio data path** + transpose-byte semantics (a `+1` bias is visible).
- **Rockmonitor digi** (4-bit NMI sample voice) = **Mode-2 (cycle-exact)** —
  defer behind base Soundmonitor (Mode-1).
- Per-variant HVSC counts need a `sidid -m` run (the DB stores only the coarse
  `Soundmonitor` label).

## ⚠ Name-collision traps (exclude these)

- **C64-Wiki "MusicMaster"** = an unrelated 1983 Compute! keyboard simulator
  (Metcalf/Sugiyama). Disambiguate by entry point + format, never by name.
- **"The Final Musicplayer" (TFMP→TFMX)** and **MasterComposer** are separate
  Hülsbeck-ecosystem engines — NOT Soundmonitor variants.
- The **11 HVSC `Chris_Huelsbeck`-tagged** tunes are a distinct hand-written
  driver — handle separately from the 3,625 `Soundmonitor` tunes.

## Variant taxonomy

MusicMaster (the replayer, ~1985, predates the editor) → Soundmonitor editor
(V1.0 64'er 10/1986; V1.1 CCT 1986; V1.3 Syndicate 1987) → **Rockmonitor**
(Dutch USA-Team 1987, adds a 4-bit NMI digi voice; II/III/IV/V) → Digitronix.
cadaver's sidid block (in `tmp/dmc_hunt/.../sidid.cfg`; **no `tools/sidid.cfg`
in-repo**) carries ~20 sub-variants under the one `Soundmonitor` heading
(RockMon2–5.1, MusicMaster_1/2/TMM, DigiMonitor, DrumMaker2, Karl_XII,
Huelsbeck_Digi_V1/V2, …). Structural anchor: the 24-register SID-clear
`A0 17 A9 00 99 00 D4` + the per-voice flag loop `BD ?? ?? 29 10 … 9D ?? ??`.

## Binary specimens

`vendor/SOUND-MONITOR.prg` (V1.0 editor, ~13 KB) is committed as a fixture; the
`.t64.gz`/`.d64`/`.zip` containers are git-ignored (reproducible from
CSDb/Archive.org — URLs in the provenance headers).

## Top leads (if migration needs more)

1. **64'er 10/1986 OCR** — `archive.org/stream/64er_1986_10/64er_1986_10_djvu.txt`
   (manual ~17743-18591; memory map ~18640-18800; 24-reg table ~18470-18591;
   11 KB hex Listing 1 from ~20195). Resolves the exact SP/AR-S/song-header packing.
2. **SM-Relocator.prg** + **rockmonitor-2/3/4.prg** (zimmers FTP
   `/pub/cbm/c64/audio/editors/`) — relocation pointer map + the digi delta.
3. **forum64.de** threads 60587 / 145999 ("Alte Sound-Formate", asserts the
   $C000 playroutine + 6502 embed examples) — 403'd, retry via browser/Wayback.
4. **JITT64** (Ice Team) — imports Soundmonitor; black-box oracle if needed.
