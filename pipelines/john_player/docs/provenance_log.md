# Provenance log — John Player research sweep (2026-06-14)

★ BEST-SOURCED family of the sweep: the full WLA-6510 player+editor SOURCE was recovered
(V1.0/V1.4 `source.zip` + V1.6 player). Only V2.0b's exact byte layout remains RE.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/john_player/docs/research.md` | read | pre-existing stub (noted source distributed w/ tool) |
| `tools/sidid.cfg` (local) | read | `John_Player` main sig + V1.0/V1.4/V1.6/V2.0b sub-sigs |
| `tools/engine_docs.json` | read | prior state |
| `hvsc84.db` (read-only) | queried | 183 `John_Player`; load/init/play clusters |

## Phase 2 — cluster agents

### Tool + source + author (cluster_tool_source_and_author.md)
| Source | Status | Notes |
|---|---|---|
| csdb.dk/getinternalfile.php/60840/John_Player_1.0.zip | downloaded | **V1.0 full source → `src/v10/`** |
| csdb.dk/getinternalfile.php/60841/John_Player_1.4.zip | downloaded | **V1.4 full source → `src/v14/`** |
| csdb.dk/getinternalfile.php/6796/johnplayer.zip (V1.6+V2.0b) | downloaded | V1.6 player source + .d64s + help → `src/` |
| pastebin.com/raw/80TaWPMz | fetched | V2.0b help → `src/johnhelp_v20beta.txt` |
| CSDb #2630 / #18767, Pouet #13860, aleksieeben pages | fetched | release/version provenance |

### Write model + versions (cluster_write_model_and_versions.md)
| Source | Status | Notes |
|---|---|---|
| `src/player.asm` + v10/v14 source | read | exact data layout, write model, ZP map, block commands |
| HVSC John Player binaries (read-only) | analysed | version fingerprinting → `src/bytemap_version_discriminators.md` |
| cadaver/sidid sidid.cfg | read | 4 version sub-sigs |

### Corpus + scene (cluster_corpus_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | 183-SID cluster table; Aleksi 29%; 2024 corrected-freq note |
| HVSC DOCUMENTS/STIL (local) | read | no John Player entries |
| CSDb / Pouet | fetched | version timeline V1.0→V2.0b; scene reception |

## Failures / blocked (retry later)
- **V2.0b source** — not in the public release (only `.d64` + help text); the exact
  128-step / 7-byte-sound / $1520-$1700 layout needs a V2.0b disassembly or Aleksi directly.
- **2024 corrected freq table** — the 42 word values (985248 Hz PAL) to be grabbed exactly.
- A few `play=$0000` SIDs — possible CIA mode, unconfirmed (no DB speed field).