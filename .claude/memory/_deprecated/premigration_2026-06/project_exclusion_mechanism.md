---
name: project-exclusion-mechanism
description: "Pipeline-enforced exclusion list for SIDs that don't fit the principled USF representation. JSON-driven, DB-tracked, refused at build/extract time with clear errors."
metadata: 
  node_type: memory
  type: project
  originSessionId: ce060f8a-e40f-4b55-9551-2d4fc0bb3028
---

# SID exclusion mechanism (2026-06-01)

Some engine families can't fit into the principled USF schema without
dragging engine-mechanism bookkeeping (sub-jump tables, positional
pointers, raw byte programs) into it. Rather than pollute USF, those
SIDs are excluded from the pipeline.

## Components

- **`tools/excluded_sids.json`** — single source of truth. Entries:
  `{path: "hvsc84/...", reason: "...", excluded_date: "YYYY-MM-DD"}`.

- **`src/exclusions.py`** — `is_excluded(path)`, `exclusion_reason(path)`,
  `check_or_raise(path)`, `all_excluded()`. Repo-root-relative path
  normalization (works with absolute or relative paths).

- **`pipelines/build_from_usf.py`** — calls `check_or_raise()` on the
  inferred `.sid` path before parsing the `.usf`. Raises
  `PipelineExclusionError` with the reason + JSON path.

- **Per-engine `write_usf` paths** — same check before extracting.
  jay_derrett's `extract/to_usf.write_usf_for()` enforces this.

- **`hvsc84.db`** — `excluded` (INTEGER DEFAULT 0) + `exclusion_reason`
  (TEXT) columns. Synced from JSON each `tools/build_sid_db.py`
  rebuild. Query: `SELECT path, exclusion_reason FROM sids WHERE excluded=1`.

## First inhabitants (15 entries)

All Companion/Jay_Derrett Type A SIDs: Counterforce, Destruct,
Discovery, Jetboys, Lifeforce, Mandroid, Ninja_Hamster, Osmium,
Road_Warrior, Stratton, Thundercross, Traxxion, Trigger_Happy,
Vengeance, ZIP.

Reason: aperiodic by engine design. The engine's self-mod $E0..$E9
counter + per-voice ptr drift means voices never simultaneously
realign. Tested NH for 100k frames (~33 minutes), 4 other Type A
tunes for 30k frames — none realign. The song is conceptually
infinite. HVSC songlength is a curator-chosen cut-off, not an engine
loop point.

## Adding an exclusion

1. Append to `entries[]` in `tools/excluded_sids.json` with path +
   reason + date.
2. Re-run `tools/build_sid_db.py` to sync the DB.
3. Pipeline refusal is automatic (no code change).

## Files retained (not deleted)

The jay_derrett extract toolchain stays in
`pipelines/companion/jay_derrett/` for reference / future analysis:
scanner (engine_model.py), play-capture simulator, orderlist decoder,
instrument decoder, round-trip verifier, JSON dumps, RE notes
(disassembly_ninja_hamster.s + README). Just not connected to the
pipeline.
