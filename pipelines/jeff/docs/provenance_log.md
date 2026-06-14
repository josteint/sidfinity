# Provenance log — Jeff (Søren Lund) research sweep (2026-06-14)

Every source attempted this sweep. Feature model from Jeff's own interviews + byte-stable
binary analysis (version string `-PLAYER V9.6 (C) JEFF / CAMELOT-`). No source/format spec
is public; binary record offsets + older gens are migration-phase RE.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/jeff/docs/research.md` | read | pre-existing stub |
| `tools/sidid.cfg` (local) | read | `Jeff` main sig + Airwalk/BullSID/FLT/XLarge/BullSID3 sub-sigs |
| `tools/engine_docs.json` | read | prior state |
| `hvsc84.db` (read-only) | queried | 192 `Jeff` + sub-tags; load/init/play clusters |

## Phase 2 — cluster agents

### Author + editor (cluster_author_and_editor.md)
| Source | Status | Notes |
|---|---|---|
| remix64.com/interviews/interview-soren-jeff-lund.html | fetched | 2002 interview → feature model → `src/remix64_interview_2002_lund.md` |
| Recollection (Domination 13) interview | fetched | → `src/recollection_domination13_interview.md` |
| CSDb #122334 (CZP Music Editor V2.0) + scener #8059 + #47985 (X-SID) | fetched | editors + variant provenance (FLT = FairLight custom) |

### Write model + variants (cluster_write_model_and_variants.md)
| Source | Status | Notes |
|---|---|---|
| HVSC Jeff binaries (read-only inspection, incl. Action_Hunter V9.6) | analysed | write model, binary layout, pattern/instrument format → `src/action_hunter_v96_hexdump.txt` |
| cadaver/sidid sidid.cfg + sidid.nfo | read | variant sub-sigs + provenance |
| deepsid / libsidplayfp | checked | no Jeff-specific handling |

### Corpus + scene (cluster_corpus_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | cluster table + sub-string counts; Søren Lund 85% |
| HVSC DOCUMENTS/STIL (local) | read | ~20 first-person Jeff annotations; no engine doc |
| CSDb / Demozoo (Camelot/CZP/Viruz) | fetched | scene timeline; group lineage |

## Failures / blocked (retry later)
- **CZP Music Editor V2.0 `.d64`** (CSDb #122334) — not yet disassembled (the canonical
  editor binary + 4 example SIDs = format spec by example; highest-value next step).
- **X-SID** (`6581.dk/xsid-viruz.rar`, CSDb #47985) — the 2007 redesigned editor; not fetched.
- **No public source/format spec** — instrument-record offsets + the $FD0/Airwalk-V4/XLarge/
  X-SID variants need disassembling compiled SIDs (migration phase).
- CSDb 503 intermittent on some pages.