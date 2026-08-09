# Provenance log — Ubik's Musik research sweep (2026-06-14)

Every source attempted this sweep, fetched or failed. NOTE: no public player source or
disassembly exists; the player structure was recovered from byte-stable corpus analysis
(an annotated disasm of the canonical player is saved under `src/`). Data encoding is
migration-phase RE.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/ubiks_musik/docs/research.md` | read | pre-existing stub |
| `tools/sidid.cfg` (local) | read | single `Ubik's_Musik` sig (gate-clear `99 04 D4` anchor) |
| `tools/engine_docs.json`, `tools/build_sid_db.py` | read | family map (`Ubik's_Musik`→ubiks_musik) + prior state |
| `hvsc84.db` (read-only) | queried | 288 SIDs; base $C600 + relocations |

## Phase 2 — cluster agents

### Editor RE + source hunt (cluster_editor_re_and_source.md)
| Source | Status | Notes |
|---|---|---|
| GitHub, CSDb, Codebase64, Pouet, Demozoo, Archive.org | searched | **no released source / disassembly exists** |
| HVSC binaries (byte-stability across 11 SIDs) | analysed | player code-region map, one-voice-per-play() LDX, $F3/$FF seq cmds |
| WilfredC64/player-id, cadaver/sidid | read | signature provenance |

### Write model + tools (cluster_write_model_and_tools.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc85/GAMES/A-F/Fire_Breath.sid` (canonical, structural read) | analysed | per-frame write model + effect register semantics → `src/fire_breath_c600_disasm.txt` |
| PRG2SID v1.26 (detection logic) | referenced | `$C666` scan + stub injection (only tool w/ Ubik handling) |
| DeepSID / libsidplayfp / VICE | checked | no Ubik-specific handling; STIL has no Ubik entries |

### Corpus + scene (cluster_corpus_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | 288-SID address-cluster table; composer cohorts; all VBI |
| HVSC DOCUMENTS dir (local) | read | no Ubik-specific doc |
| CSDb #39950 / Gamebase64 / Lemon64 / remix64 | partial | games-using-it list, scene timeline |

## Failures / blocked (retry later)
- **CSDb (csdb.dk) — 503** for the editor release page (#39950) + comments — the
  highest-value remaining lead (editor disk + scene RE notes).
- **No public disassembly** — confirmed absent; the data encoding (instrument table,
  note/duration bytes, song-pointer stride, drum-offset table) requires disassembling a
  compiled HVSC SID (migration phase; the `src/` disasm is the head start).
