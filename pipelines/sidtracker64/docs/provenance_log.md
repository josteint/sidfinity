# Provenance log — SidTracker64 research sweep (2026-06-14)

Every source attempted this sweep, fetched or failed. NOTE: closed-source iOS app — no
player source / `.s64` spec is public; the exported-player structure was recovered from
byte-stable HVSC binary inspection. Data encoding is migration-phase RE.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/sidtracker64/docs/research.md` | read | pre-existing stub |
| `tools/sidid.cfg` (local copies) | read | single `SidTracker64` sig (gate-clear `29 FE 9D 04 D4` anchor) |
| `tools/engine_docs.json` | read | prior state |
| `hvsc84.db` (read-only) | queried | 259 SIDs; load/init/play clusters; 47% CIA |

## Phase 2 — cluster agents

### App + format (cluster_app_and_format.md)
| Source | Status | Notes |
|---|---|---|
| Apple App Store (id955421205) | 200 | 32 instruments, 128 patterns, 8 waveforms, export formats, v1.0.5 |
| soundonsound.com / chordian.net c64editors | 200 | player ~2000 B, ZP $F8-$F9, 23-27 rasterlines |
| sidtracker64 social/site (x/fb/updatestar/440audio/synthyfrog) | 402/403/TLS | blocked |
| CSDb search "SidTracker64" | 200 (no results) | iOS-only, not C64-scene-released |

### Write model + binary (cluster_write_model_and_binary.md)
| Source | Status | Notes |
|---|---|---|
| ~10 HVSC SidTracker64 SIDs (read-only byte inspection) | analysed | player structure, write model, pattern encoding, SMC slots, 14 code-size variants |
| All 259 SIDs surveyed (Python, read-only) | analysed | load addresses + code sizes |
| cadaver/sidid `sidid.cfg` (raw) | 200 | signature confirmed |
| WilfredC64/player-id, deepsid (+ Chordian/deepsid) | 200 | no ST64-specific entry/notes |

### Corpus + scene (cluster_corpus_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | 259-SID address-cluster table; 47% CIA; author cohorts; 2015-2025 timeline |
| HVSC DOCUMENTS dir (local) | read | no SidTracker64 mention (Players/STIL/Songlengths) |
| CSDb (Pernod profile, releases) / DeepSID | partial | scene usage; DeepSID magenta tag |

## Failures / blocked (retry later)
- ST64 social/news pages (x.com, facebook, updatestar, 440audio, discchord) — 402/403/refused.
- **No public player source or `.s64` spec** — confirmed absent; the data encoding
  (work-area map, freq table, instrument block, wavetable/pulse/filter tables, FX-track
  stream) requires disassembling HVSC exports (migration phase).
- A v1.x→v2 app changelog detailing export-player changes was not found; the ~14
  code-size variants are the empirical version signal.
