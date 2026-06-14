# Provenance log — TFX research sweep (2026-06-14)

Every source attempted this sweep, fetched or failed. NOTE: this family is unusually
well-sourced — the actual player source + manual + on-disk-layout unpacker were
recovered (all under `src/`). Remaining gap = the V1.x (play=$1100) layout.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/tfx/docs/research.md` | read | pre-existing stub (corrected: Czech not Polish; DMC-derived) |
| `tools/sidid.cfg` (local) | read | single `TFX` sig (X-indexed hard-restart anchor) |
| `tools/engine_docs.json` | read | prior state |
| `hvsc84.db` (read-only) | queried | 269 SIDs; init/play clusters |

## Phase 2 — cluster agents

### Editor + scene + source (cluster_editor_and_scene_source.md)
| Source | Status | Notes |
|---|---|---|
| unreal64.net `Tfx_2_99.zip` | fetched | **player source `Player.ass` + manual + keys + changelog + `hyperPacker.c`** → `src/*` |
| CSDb (Ray id=1594, releases v1.0–v2.99) | fetched | 13 releases; DMC→TFX converter (1996); author = Lada "Ray" Lostak (CZ) |
| Factor6 / Henne interviews | searched | no TFX-specific connections found |

### Write model + binary (cluster_write_model_and_binary.md)
| Source | Status | Notes |
|---|---|---|
| HVSC TFX binaries (read-only inspection) | analysed | binary layout, write order, pattern encoding → `src/atariada_disasm_fragments.s` |
| `Player.ass` (cross-ref) | read | grounds the write model |
| DeepSID / libsidplayfp / VICE | checked | no TFX-specific handling |

### Corpus + versions (cluster_corpus_and_versions.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | 269-SID address-cluster table → version cohorts; author concentration |
| HVSC DOCUMENTS dir (local) | read | no TFX-specific doc |
| CSDb / Demozoo (version history) | fetched | V1.0→V2.99 series; Czech/AU author genealogy; DMC descent |

## Failures / blocked (retry later)
- **CSDb (csdb.dk) — 503** for the v1.0/v1.2 editor disk pages (#110111 / #38900) —
  the only real remaining lead (a v1.x binary to map the play=$1100 layout).
- **unreal64.net/tfx main page** — not recovered (the v2.99 zip was reachable directly).
- **No v1.x manual/source exists** — v1.x layout is migration-phase RE from a v1.x binary.
