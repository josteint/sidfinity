# Provenance log — CheeseCutter 2.x research sweep (2026-06-14)

Every source attempted this sweep, fetched or failed. Future waves: don't re-fetch
fetched-OK rows. The player effect chain itself lives in `jch_newplayer/docs/` (the
shared NP21.G4 base) — this sweep is the CheeseCutter-specific delta.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/cheesecutter/docs/research.md` | read | pre-existing stub |
| `tools/sidid.cfg` copies (local) | read | 4 CheeseCutter sub-sigs + parent `CheeseCutter_2.x` |
| `tools/build_sid_db.py`, `tools/engine_docs.json` | read | family map + prior state |
| `tmp/dmc_hunt/CheeseCutter/` (full source, read-only) | read | the live oracle for player + export |
| `hvsc84.db` (read-only) | queried | 302 SIDs, load/init/play distribution |

## Phase 2 — cluster agents

### Native player + export layout (cluster_native_player_and_export.md)
| Source | Status | Notes |
|---|---|---|
| `tmp/dmc_hunt/CheeseCutter/src/ct/{song,build,dump,base}.d` | read | export packing, variable INSNO, INCLUDE_* stripping, .ct format → `src/*.d` excerpts |
| `tmp/dmc_hunt/CheeseCutter/src/c64/player_v4.acme` | cross-ref | vs jch/laxity docs (not re-captured) |

### Versions + 2SID (cluster_versions_and_2sid.md)
| Source | Status | Notes |
|---|---|---|
| local `src/ct/build.d` (INCLUDE_* flags, subinit) | read | maps the 4 sidid sub-sigs to player regions |
| HVSC `Auxillary_Love_2SID.sid` (structural read) | analysed | 6-voice 2SID write model, voice table {$00,$07,$0E,$20,$27,$2E} |
| github.com/theyamo/CheeseCutter (tags/releases) | partial | player strings cc4.03/4.04/4.07 |

### History + scene + corpus (cluster_history_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| github.com/theyamo/CheeseCutter (CHANGELOG, tags, README) | fetched | release timeline 0.4.0→2.10 |
| `tmp/dmc_hunt/CheeseCutter/{README.md,doc/README}` | read | repo docs |
| DeepSID / Lemon64 / Pouet | partial | scene context |
| `hvsc84.db` (read-only) | queried | 302-tune corpus shape; $080D/play=0 + $0FED groups flagged |

## Failures / blocked (retry later)
- **CSDb (csdb.dk) — 503** all session for release pages/comments.
- **Wayback Machine** — blocked this session.
- **CheeseCutter changelog website — 401.**
  → v2.3–v2.6 feature dates reconstructed from search snippets; retry for confirmation.
- **No version string in exported SIDs** — player version is only recoverable by
  comparing the player byte image (migration-phase disassembly).
