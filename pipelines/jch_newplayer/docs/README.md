# JCH NewPlayer — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-13).

JCH NewPlayer, by **Jens-Christian Huus (JCH) of Vibrants**, 1988+. ~3,611 HVSC
tunes (6th-largest family; ~4,004 incl. NP-family relatives), 0 migrated.
init=$1000, play=$1003. **The best-documented unmigrated family yet** — released
player source exists, and it's a sibling of DMC (already `OK`).

A six-cluster sweep ran 2026-06-13. Outcome: format + per-frame write model are
**grounded in actual player source** (CheeseCutter's `player_v4.acme` = "Based on
JCH NP 21.G4 by Laxity/VIB") plus a maintained NP20 parser (SID Factory II's
`converter_jch.cpp`), both available as local read-only checkouts, plus a real
HVSC binary decoded end-to-end.

## Start here (canonical)

1. **`spec_extraction_plan.md`** — ordered binary→USF checklist + the OPEN items
   (each with the exact trace to close it). Read first.
2. **`spec_write_model.md`** — per-frame `$D400-$D418` write model (Mode-1 target).
3. **`github_cheesecutter.md`** — from `CheeseCutter/src/c64/player_v4.acme` (the
   actual NP21.G4 6502 player): per-frame `setsid` block, full effect chain,
   hard-restart semantics, table processing. The semantics oracle.
4. **`github_sidfactory2.md`** — SF2's `converter_jch.cpp`: a maintained C++
   parser of the **NP20.gX packed binary** (the on-disk layout HVSC actually uses).
5. **`csdb_codebase64_format_spec.md`** — the published codebase64 20.G4 spec
   (thin by its author's admission; the `$xxCB` map + AA/BB sequence grammar).

## ⚠ Critical: two binary encodings under one engine name

The decompiler must branch on this. **The CheeseCutter source explains
*behaviour*, but its *data encoding* is NOT what most HVSC tunes use:**

| | **Packed NP20.G4** (HVSC majority, ~3195/3611, init=$1000) | **CheeseCutter / NP21+ runtime** |
|---|---|---|
| pulse/filter table rows | **2 bytes** | **4 bytes** |
| instruments | **32, row-major 8-byte records** | **48, column-major (stride 48)** |
| sequence end-mark | `$7F` | `$BF` |
| order-list | 2-byte `(transpose, seq#)`, `$FF` end | 4-byte tracks, `$Fx` wrap |

**Extraction must read the packed form** (`converter_jch.cpp` is the reference);
**the write model uses CheeseCutter semantics**. Also: sequence pointers in the
packed binary are **rebased at init** (they point outside the loaded image) —
confirm via `--pc-trace` of init (spec OPEN-3).

## Per-frame write model (the Mode-1 target)

`setsid`, per voice, fixed order: **freq-lo, freq-hi, SR (`$D406`), AD (`$D405`),
PW-lo, PW-hi, ctrl (waveform AND gate)** — **SR-before-AD is a JCH fingerprint**.
Voices run **V2→V1→V0**; then once/frame `$D415`, `$D416`, `$D417` (filter-init
rows only), `$D418` (volume | bandpass). No separate gate-edge / `$09` testbit
write in this player. **HR-AD is global** (super-table row 0, default `$0F`);
**HR-SR is per-instrument** (instrument byte 6 — *not* "unused" as `research.md`
says). 4 hard-restart types: `$0x`/`$4x`/`$8x`/`$Ax` (`$Ax` = "Laxity restart",
AD preserved). ~98% of tunes are vblank (Mode-1 flat path); ~2% CIA-timed
Q-series → `siddump --writelog-per-irq` (Trap C).

## Version lineage (THREE authors — the version-parsing trap)

- **JCH**: v05 (1989) → **20.G4 (May 1991)**, which JCH calls his "last standard
  player on C64". (2-byte tables, 32 instruments.)
- **Laxity** continuation: **NP21.G4 / G5 / B6** — the 21-series is *Laxity's*,
  not JCH's. (4-byte tables, 48 instruments.) CheeseCutter forked this.
- **Dane** (Booze Design) resurrection: **NP22/23/24/25** + JCH-Editor 3.1 (2011).
- Ports/successors: **CheeseCutter** (Abaddon, open source) + **SID Factory II**
  (distinct successor engine, `SidFactory_II/Laxity` = 377 SIDs separately).
- Suffix grammar: **G** = single-speed; **Q** = multispeed (PSID speed≠0, CIA);
  **B** = CheeseCutter-era. DMC is a **sibling** (Danish editor tradition), not a
  parent — but shares the entry convention + hard-restart + programmable-table model.

## File index

| Topic | Canonical | Corroborating |
|---|---|---|
| Extraction plan + OPEN items | `spec_extraction_plan.md` | — |
| Per-frame write model | `spec_write_model.md` | `forum_hard_restart_and_write_model.md` |
| Player source (NP21.G4) | `github_cheesecutter.md` | `forum_cheesecutter_np21_format.md` |
| Packed NP20 parser | `github_sidfactory2.md` | — |
| Published format spec | `csdb_codebase64_format_spec.md` | — |
| Variant taxonomy (V1–V20) | `sidid_variant_taxonomy.md` | `deepsid_lineage_and_version_map.md` |
| Version lineage / authors | `archive_version_history.md` | `archive_jch_vibrants.md`, `forum_version_lineage_and_comparison.md` |
| Releases / released source | `csdb_releases_and_source.md` | `forum_version_history_and_tooling.md` |
| Tool landscape | `github_parser_notes.md` | — |

Multiple files per topic = independent sources that agree; full provenance in
each file + `provenance_log.md`. (`research.md`'s overview has minor errors the
sweep corrected: CPU ~28-33 rasterlines not 12-13; player <1900 bytes; instrument
byte 6 = HR-SR not unused.)

## What's solved

- **Released player source** (CheeseCutter `player_v4.acme` = NP21.G4) + a
  maintained packed-NP20 parser (SF2 `converter_jch.cpp`) — both local, read-only.
- **Per-frame write model** + hard-restart semantics, grounded in source.
- **Packed binary layout** decoded (incl. a real HVSC tune, `Odkin/Wild.sid`).
- **Variant taxonomy** (V1–V20 + Laxity/Glover/Dane relatives) + the 3-author lineage.
- **DMC→JCH transfer map**: shared entry convention / hard-restart / table model;
  NEW pieces = the AA/BB **sequence grammar**, the **super/command table** (9
  parametric effects: slide ±, vibrato, detune, set-ADSR, lo-fi vibrato,
  set-waveform, portamento, stop), the **chord table**, column-major instruments.

## What remains (migration, not research)

- **Disassemble one packed NP20.G4 tune** (`seed_disassembly.py` →
  `disassembly.s`) to close the spec OPEN items: seq-pointer rebasing at init
  (OPEN-3), packed super-table stride/HR-AD location (OPEN-6), relocation base,
  transpose zero-point, 2-vs-4-byte table detection per fingerprint.
- **Map the ~21 sidid signatures → version → layout branch** (the discriminator
  the extractor keys on); per-variant HVSC counts need a local `sidid -m` run
  (the DB stores only the coarse `JCH_NewPlayer` label).
- **Leverage the DMC pipeline** — JCH is a sibling; the hard-restart + table
  machinery may partly transfer from `pipelines/dmc/`.
- Q-series multispeed → CIA per-play verdict.

## Top leads (if migration needs more)

1. **JCH's own native asm source** (not CheeseCutter's reimpl) — `vibrants.dk`,
   funet `Vibrants/`, and CSDb (503 all session, retry): id=165426 (NP20.g2 docs),
   id=100406 / getinternalfile 97829 (NP22-25 English manual `.doc`), id=26563 (NP21).
2. **`JCH Editor-docs.prg`** (zimmers.net, 14,269 B) — JCH's own manual; de-PRG it.
3. **Read CheeseCutter's full play loop** — only the header + descriptors + setsid
   were captured; the $00–$08 effect-command routines are the NP21 write oracle.
4. **HVMEC 1.0** (High Voltage Music Engine Collection) — bundles JCH Editor ≤3.07.
