# Provenance log — EMS/Odie research sweep (2026-06-14)

Every source attempted this sweep. UNUSUALLY well-sourced for an obscure editor: the
official V7.03 disk's 7 HELP files were decoded and saved (`src/`). Binary record offsets
remain migration-phase RE.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/ems_odie/docs/research.md` | read | pre-existing stub |
| `tools/sidid.cfg` (local) | read | EMS/Odie main sig + V7.03/V9.x/V10.x sub-sigs + related Odie strings |
| `tools/engine_docs.json`, `tools/build_sid_db.py` | read | family map (`EMS/Odie`→ems_odie) + prior state |
| `hvsc84.db` (read-only) | queried | 196 SIDs + related Odie strings; load/init/play clusters |

## Phase 2 — cluster agents

### Editor + Cosine (cluster_editor_and_cosine.md)
| Source | Status | Notes |
|---|---|---|
| CSDb #4649 → `ems_v703.d64` | downloaded + extracted | **7 HELP files decoded from PETSCII → `src/*.txt`** (the complete feature model) |
| Lemon64 / CSDb / cosine.org.uk | fetched | author/version context (V4.3→V7.03→V8→V9→V10) |

### Write model + versions (cluster_write_model_and_versions.md)
| Source | Status | Notes |
|---|---|---|
| HVSC EMS binaries (read-only inspection) | analysed | per-frame write model; V7.03/V9.x/V10.x binary differences; Odie subgroups |
| cadaver/sidid sidid.cfg + sidid.nfo | read | the 3 sub-sigs + provenance |
| deepsid / libsidplayfp | checked | no EMS-specific handling |

### Corpus + scene (cluster_corpus_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | 196-SID cluster table + related-string counts; Merman 50%; 1 CIA + 1 2SID |
| HVSC DOCUMENTS/STIL (local) | read | one non-technical EMS mention; no engine doc |
| CSDb / Demozoo (Cosine) | fetched | version timeline; UK scene network |

## Failures / blocked (retry later)
- **No V9 or V10 disk image found** — would document the later-gen data format (esp. V10's
  $53-entry packed-freq decompress). Retry cosine.org.uk + CSDb.
- **TMR's EMS tutorial** (~2003) — referenced, not located.
- **Binary instrument-record byte offsets** — the 15 params' exact bytes + stream/table wire
  formats need disassembling a compiled V7.03 SID (migration phase; the HELP files give the
  semantics, not the bytes).
- CSDb 503 intermittent on some pages.