# Provenance log — Electrosound research sweep (2026-06-14)

Every source attempted this sweep, fetched or failed. Future waves: don't re-fetch
fetched-OK rows. NOTE: no public player source or disassembly exists — this family's
byte-level format is migration-phase RE.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/electrosound/docs/research.md` | read | pre-existing stub |
| `tools/sidid.cfg` (local) | read | single sig `F0 01 60 A9 64 9D ?? ?? BD ?? ?? C9 01` |
| `tools/engine_docs.json`, `tools/build_sid_db.py` | read | prior state (no explicit family-map entry → default) |
| `hvsc84.db` (read-only) | queried | 297 SIDs; varied load/init/play |

## Phase 2 — cluster agents

### Editor + manual (cluster_editor_and_manual.md)
| Source | Status | Notes |
|---|---|---|
| VGMPF, c64-music blogspot, Lemon64, remix64 interviews | fetched | musical model (10 inst / 5 modulators / 20 seq / drums / 423.9 Hz) |
| scribd.com/document/460293234 (ELECTROSOUND manual, 18pp) | blocked | subscription-gated; not retrieved |
| CSDb release IDs 27433/85170/150998/254231 | 503 | retry for editor disk + comments |

### Disassembly + tools (cluster_disassembly_and_tools.md)
| Source | Status | Notes |
|---|---|---|
| Lemon64 (Warren Pilkington, 2008) | fetched | player layout offsets (init +$0518, play +$0A65, $02xx state) |
| DeepSID + github.com/Chordian/deepsid | fetched | no Electrosound-specific code; delegates to SIDId |
| codebase64 / pouet / GitHub | searched | **no published disassembly/RE exists** |
| JC64dis | referenced | auto-labels a compiled Electrosound binary (output unpublished) |

### Corpus + scene (cluster_corpus_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | 297-SID address-cluster table; play=load+$0A65 (79%); composer cohorts |
| HVSC DOCUMENTS dir (local) | read | **no Electrosound doc present** |
| Lemon64 / remix64 / CSDb history | fetched | scene timeline (1985→1987, 2020 revival) |

## Failures / blocked (retry later)
- **CSDb (csdb.dk) — 503** all session (release pages + comments — the highest-value
  remaining lead, since the editor disk + scene RE notes live there).
- **Scribd manual PDF** — subscription-gated.
- **No public disassembly** — confirmed absent; byte-level format requires disassembling
  a compiled HVSC SID (migration phase).
