# Provenance log — Cyberlogic SoundStudio research sweep (2026-06-14)

Every source attempted this sweep, fetched or failed. No source/spec/manual is public;
the player structure is from byte-stable HVSC inspection + Oliver Klee's first-person STIL
notes. The effect-opcode map is migration-phase RE.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/cyberlogic/docs/research.md` | read | pre-existing stub |
| `tools/sidid.cfg` (local) | read | single `Cyberlogic_SoundStudio` sig (LSR×4 nibble dispatch) |
| `tools/engine_docs.json`, `tools/build_sid_db.py` | read | family map + prior state |
| `hvsc84.db` (read-only) | queried | 196 SIDs; load/init/play clusters; composer folders |

## Phase 2 — cluster agents

### Editor + authors (cluster_editor_and_authors.md)
| Source | Status | Notes |
|---|---|---|
| CSDb #170632 (CSS V4.0) + #97286 | fetched | release pages, CSS packer + low-raster variant |
| CSDb sceners #5968 (Odi/Oliver Klee) + #3288 (celticdesign/Sascha Nagie) | fetched | author confirmation |
| HVSC binaries (embedded strings) | analysed | "MUSIC SASCHA NAGIE, PLAYER O.KLEE"; load layout; note encoding |
| zimmers.net FUNET editors index | fetched | `Soundstudio.prg` (12/11/92 Preview) located — top lead |
| oliverklee.de | fetched | no C64 content |

### Write model + binary (cluster_write_model_and_binary.md)
| Source | Status | Notes |
|---|---|---|
| HVSC Cyberlogic binaries (read-only inspection) | analysed | write model, table layout, $6000 split → `src/v_arc_early_bytemap.md` |
| cadaver/sidid sidid.cfg + sidid.nfo | read | signature + author provenance |
| deepsid / libsidplayfp | checked | no CSS-specific handling |

### Corpus + scene (cluster_corpus_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | 196-SID cluster table; composer cohorts; all VBL |
| HVSC STIL.txt (local) | read | 93 entries; **Oliver Klee's 14 first-person CSS comments** (effect/filter notes) |
| HVSC DOCUMENTS dir (local) | read | no CSS player doc |
| CSDb / Demozoo (Demons of Sound) | fetched | scene timeline 1991–2021; group history |

## Failures / blocked (retry later)
- **No public source/spec/manual** — the `$80–$FB` effect opcodes, `$FC/$FD` args, section
  advance, and the multi-generation layouts need disassembling a compiled HVSC SID
  (migration phase; `src/` byte map + STIL notes are the head start).
- `Soundstudio.prg` (zimmers.net) + `css.d64` (CSDb #170632) — editor binaries; not yet
  disassembled (the closest thing to a format spec).
- CSDb 503 intermittent on some pages.