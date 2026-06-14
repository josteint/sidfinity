# Provenance log — AMP research sweep (2026-06-14)

Every source attempted this sweep, fetched or failed. No formal format spec / source is
public; the player structure was recovered from byte-stable HVSC binary inspection +
binary credits string. The editor 4-file data encoding is migration-phase RE.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/amp/docs/research.md` | read | pre-existing stub |
| `tools/sidid.cfg` (local) | read | single `AMP` sig (filter `$D416` + `$D418` table loop) |
| `tools/engine_docs.json` | read | prior state |
| `hvsc84.db` (read-only) | queried | 246 SIDs; load/init/play clusters; composer folders |

## Phase 2 — cluster agents

### Editor + Magic Disk 64 (cluster_editor_and_magicdisk.md)
| Source | Status | Notes |
|---|---|---|
| CSDb #35519 + scener #14045 (Andrew Miller/Burton) | fetched | author confirmation; AMP V2.3 1990; Magic Disk 64 12/91 |
| amp.d64 binary credits string | extracted | "programmed by ANDREW MILLER w/ help of MARKUS MUELLER 1990" → `src/amp_binary_credits_extracted.txt` |
| VGMPF / 8bitlegends / Demozoo / C64-Wiki | fetched | provenance corroboration; 4-file format + .DAT layout → `src/amp_dat_file_structure_notes.txt` |

### Write model + binary (cluster_write_model_and_binary.md)
| Source | Status | Notes |
|---|---|---|
| HVSC AMP binaries (read-only inspection, incl. Anti_Airwolf) | analysed | layout, write model, SMC, freq table → `src/Anti_Airwolf_player_disasm.txt` |
| sidid.cfg / sidid.nfo | read | signature + provenance |
| deepsid / libsidplayfp | checked | no AMP-specific handling |

### Corpus + scene (cluster_corpus_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | 246-SID address-cluster table; all VBL; composer/geography cohorts |
| HVSC DOCUMENTS dir (local) | read | no AMP mention |
| CSDb / VGMPF / Demozoo | fetched | scene timeline 1988-2015; German/Dutch dominance |

## Failures / blocked (retry later)
- **A.M.P. V2.3 Pack** (CSDb #200544) with Cobra's documentation — not yet read (the
  best candidate for a format spec).
- **Magic Disk 64 12/1991 D64** German tutorial — not mounted/read.
- **No public source/spec** — the editor 4-file (.SNG/.VOI/.NOT/.DAT) byte layout +
  note-index formula require disassembling a compiled HVSC SID (migration phase).
- CSDb 503 intermittent on some pages.
