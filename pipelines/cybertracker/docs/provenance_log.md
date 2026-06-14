# Provenance log — CyberTracker research sweep (2026-06-14)

Every source attempted this sweep, fetched or failed. The feature/data model is from the
public manual (saved under `src/`); the byte-level file layout is the open gap (#1 lead).

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/cybertracker/docs/research.md` | read | pre-existing stub |
| `tools/sidid.cfg` (local) | read | `CyberTracker` + `CyberTracker_exe` sigs |
| `tools/build_sid_db.py`, `tools/engine_docs.json` | read | family map (both strings → cybertracker) + prior state |
| `hvsc84.db` (read-only) | queried | 125 _ct + 130 _exe; build-class clustering |

## Phase 2 — cluster agents

### Manual + format (cluster_manual_and_format.md)
| Source | Status | Notes |
|---|---|---|
| noname.c64.org/tracker/ + manual_online.php | fetched | full feature/data model → `src/manual_online_fetched.md` |
| CSDb #2601 (V1.00) / #25 (V1.01) | fetched | version history |
| pouet #13365, cadaver/sidid.nfo | fetched | corroboration |

### Write model + variants (cluster_write_model_and_variants.md)
| Source | Status | Notes |
|---|---|---|
| HVSC _ct + _exe binaries (read-only inspection) | analysed | write model, state-page map, the 2-variant write-order difference |
| noname.c64.org manual | cross-ref | grounds the register semantics |
| deepsid / libsidplayfp | checked | no CyberTracker-specific handling |

### Corpus + scene (cluster_corpus_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | 255-SID build-class table (both strings); all VBL; author cohorts |
| HVSC DOCUMENTS dir (local) | read | no CyberTracker mention |
| CSDb / noname.c64.org history | fetched | version timeline; No Name group; CyberBrain co-founded CSDb |

## Phase 3 — lead-follow (orchestrator)
| Source | Status | Notes |
|---|---|---|
| noname.c64.org/download.php/ct_v101_fileformat_fixed.zip | curl empty / unfetchable | binary ZIP; sandbox curl no egress; WebFetch can't unzip |
| web.archive.org (ZIP + justsolve mirror) | blocked | WebFetch refuses web.archive.org in this env |
| justsolve.archiveteam.org `CyberTracker_module` / `_instrument` | ECONNREFUSED | site down this session |
| `web.archive.org/web/20251001020254/http://noname.c64.org:80/download.php/ctmisc/ctfileformat-1_01.html` | **OBTAINED** (user downloaded the Wayback capture 2026-06-14; capture dated 2025-10-01) | the author's byte-format spec → `cluster_byte_format.md` + `src/ctfileformat-1_01.txt`. **#1 gap CLOSED.** |

## Failures / blocked (retry later)
- ~~byte-level `.ct`/`.ci` file-format spec~~ — **RESOLVED** (user fetched the Wayback HTML
  capture; the HTML version of the same doc, not the ZIP).
- CSDb 503 intermittent on some release pages.
- Remaining: file↔in-memory ($10xx/$53A2) offset binding (one disassembly, migration phase).
