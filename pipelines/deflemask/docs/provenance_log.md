# Provenance log — DefleMask research sweep (2026-06-14)

Every source attempted this sweep, fetched or failed. Future waves: don't re-fetch
fetched-OK rows.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/deflemask/docs/research.md` | read | pre-existing stub (DefleMask v12, 245 tunes) |
| `tools/sidid.cfg` (several local copies) | read | v1/v2/v12 + Reflextracker signatures (byte-identical across copies) |
| `tools/build_sid_db.py`, `tools/engine_docs.json` | read | family map (DefleMask_v1/v2/v12 → deflemask) + prior state |
| `hvsc84.db` (read-only) | queried | 310 SIDs (v12=240, v2=69, v1=1); load/init/play distribution |

## Phase 2 — cluster agents

### Embedded player (cluster_embedded_player.md)
| Source | Status | Notes |
|---|---|---|
| github.com/chiptunecafe/deflestream64 | fetched | VGM streamer, NOT the HVSC player → `src/deflestream64_main_s.txt` |
| HVSC v12/v2/v1 binaries (structural read) | analysed | write model + song-data layout → `src/deflemask_v12_player_hex.txt` |
| GitHub "deflemask sid player c64" / Delek GitHub | searched | no public DefleMask export-player source exists |

### DMF spec + effects (cluster_dmf_spec_and_effects.md)
| Source | Status | Notes |
|---|---|---|
| deflemask.com/DMF_SPECS.txt (+ Wayback) | fetched | 3 versions → `src/DMF_SPECS_0x11/0x15/0x18.txt` (v9c / v11.1 / v1.0.0) |
| github.com/tildearrow/furnace (`sysDef.cpp`, `doc/7-systems/c64.md`) | fetched | C64 effect catalogue + instrument model (the semantics oracle) |

### Variants & scene (cluster_variants_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| deflemask.com (+ Wayback), Delek pages | fetched | app-version → export-player-version → SIDId-tag map |
| DeepSID (deepsid.chordian.net + Chordian/deepsid) | fetched | player-detection notes |
| Lemon64 / Pouet threads | fetched | scene reception (DefleMask "useless for native C64") |
| DefleMask GitHub issues #216 / #353 | referenced | CIA-write hardware-incompat bugs |

## Failures / blocked (retry later)
- **CSDb (csdb.dk)** — comment threads 503 this session.
- **ChipMusic.org** DefleMask thread pages 23–25 — 403.
- **No public DefleMask export-player source** — confirmed absent; the bit-field decode
  detail is only recoverable by disassembling our own v12 binaries (migration phase).
