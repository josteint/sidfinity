# GMC / Game Music Creator — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-13).

GMC ("Game Music Creator"), by **Balázs Farkas (Brian) of Graffity** (Hungary),
December 1990. ~446 HVSC tunes (`GMC/Superiors`) + 9 `GMC_V2.0/Superiors`
(a 2010-23 revival). 0 migrated. **Closed engine — no public source.**

A six-cluster sweep ran 2026-06-13 (gather+summarise, on sonnet). The standout
result is the **GMC→DMC lineage** (see below) — it makes GMC a low-risk migration
because the already-migrated DMC pipeline largely transfers.

## 🔑 The headline: GMC is the direct predecessor of DMC

Same author, **8 weeks apart**: Brian shipped GMC V1.0 (Dec 1990) then DMC V1.2
(Feb 1991). DMC is SIDfinity's #1 family and is already migrated (`pipelines/dmc/`,
`doc_state` OK). They share:
- the **two-level Tracks → Sectors** architecture,
- the **$1000 init / $1003 play** entry convention,
- the **8-subtune pointer table**,
- the **abs,X multi-voice SID write dispatch** (opcode-level match).

**Key difference**: GMC instruments are **16 bytes** (indexed via 4× `ASL` = ×16);
DMC V4 uses 11-byte instruments, and GMC's instrument-decode path differs. So the
migration should **reuse the DMC pipeline** — USF schema blocks, `composer_asm.py`,
the dataflow-operand extractor, the batch runner, regression wiring — and write
**fresh GMC instrument/sector-decode routines**. `forum_gmc_dmc_lineage.md` maps
23 elements + an 8-component DMC-reuse assessment.

## Engine model

- Entry: $1000 init / $1003 play. **Tracks → Sectors** (≤8 tunes/file; tracks
  reference sectors with transpose). Per-step sector fields: **DUR** (duration),
  **SND** (sound#), **APM** (amplitude/mod), **GLD** (glide/portamento), **HLD**
  (hold), **CONT** (tie/continuation), **END**. **Sound definitions = 16 bytes**
  each (×16 indexing). Praised for "twisted filtering."

## Versions

- **V1.0** (Dec 1990) → **V1.6** (editor updates; same player) → **V2.0** — a
  *modern revival* (all 9 HVSC V2.0 tunes are 2010-23, mostly NecroPolo), not a
  1990s branch. sidid distinguishes V1 (`18 0A 0A 0A 0A` = ×16 instrument stride)
  from V2.0 (`AND #$F0 / AND #$0F` nibble-split → packed fields, lifts the 16-
  instrument cap). **Fenek's "GMC V2" (2006, CSDb #44814)** is a reimplementation
  *from a disassembly* — the closest thing to a public GMC disasm. **HVMEC**
  hosts the V1.0/V1.6/V2.0 editor D64s. "Superiors" = Graffity's internal label.

## Census & verification (`hvsc84.db`, read-only)

455 total (446 V1 + 9 V2.0), 0 migrated. V1 layouts: **`init=$18EA / play=$14EA`**
(289, the native Hungarian address, `init=play+$400`) + **`$1000 / $1003`** (114)
+ ~43 other relocations. 94.6% single-subtune. 4 RSID (`play=0`, CIA). VBlank/50 Hz
→ flat **Mode-1** verdict (PSID speed-bit survey is an OPEN; the 4 RSID need per-IRQ).

## ⚠ Closed engine — byte layout OPEN

No public source; no human-readable disassembly. The migration bootstrap is the
**HVMEC editor binaries** + **Fenek's reimplementation** + `seed_disassembly.py`
on a canary (anchor on the `18 0A 0A 0A 0A` ×16 instrument-stride from the sidid
sig). Byte-level OPENs (recorded, not RE'd here): exact sector-byte packing, the
16-byte sound-def layout, track/transpose encoding, APM & HLD semantics, the
V1↔V2.0 nibble-field difference.

## File index

| Topic | Canonical | Corroborating |
|---|---|---|
| **GMC→DMC lineage** | `forum_gmc_dmc_lineage.md` | `spec_extraction_plan.md` |
| Extraction plan + OPENs | `spec_extraction_plan.md` | — |
| Per-frame write model | `spec_write_model.md` | — |
| sidid V1/V2 sigs | `sidid_signature_analysis.md` | `github_tools_and_parsers.md` |
| Releases / lineage | `csdb_releases_and_lineage.md` | `archive_version_history.md`, `forum_csdb_hvmec_scene.md` |
| Author / Hungarian scene | `csdb_author.md` | `archive_authors_scene.md` |
| Population / DeepSID | `deepsid_labeling.md` | — |
| Tooling (closed) / negatives | `github_tools_and_parsers.md` | `forum_compsyscbm_negative.md` |

Provenance headers on every file; `provenance_log.md` lists URLs hit/blocked.

## What's solved

- The **GMC→DMC lineage + the DMC-pipeline reuse map** (the strategic payoff).
- Engine model (Tracks→Sectors, sector fields, 16-byte sounds), version taxonomy,
  the "Superiors" clarification, author/scene history, census, sidid V1/V2 split.
- Bootstrap identified (HVMEC editors + Fenek reimplementation).

## What remains (migration — OPENs, deferred from this gather-only sweep)

- **Disassemble a canary** (anchor on `18 0A×4`): pin sector packing, the 16-byte
  sound layout, track/transpose, APM/HLD semantics, the V1↔V2.0 difference —
  bootstrap with HVMEC's editor + Fenek's reimplementation.
- **Reuse the DMC pipeline** (schema/composer/dataflow-extract/batch/regression);
  write fresh GMC instrument/sector decode. Proposed `pipelines/gmc/v1/` (+`v2/`).
- **PSID speed-bit survey** (VBlank expected → flat Mode-1; 4 RSID per-IRQ).
- Canary: a mid-length single-subtune `init=$18EA` V1 tune.

## Top leads

1. **HVMEC editor D64s** (`hvmec.altervista.org/blog/?p=1256/1265/1272`) — carve the player.
2. **Fenek's GMC V2** (CSDb #44814) — reimplementation-from-disasm; closest to a source.
3. **`deprecated/dmc_wip/dmc/docs/lead_predecessors_and_jch.md`** — prior in-repo GMC lineage notes.
4. **APM / HLD semantics** — the two most GMC-specific unknowns; ask NecroPolo / Wacek (active composers).
