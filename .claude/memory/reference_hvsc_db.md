---
name: hvsc84-db
description: "hvsc84.db — SQLite index of every HVSC #84 SID with engine classification + our build status. Run tools/build_sid_db.py to refresh after migrations / new builds / HVSC updates."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

`hvsc84.db` at the project root indexes every `.sid` file under
`hvsc84/` with PSID/RSID header fields, engine classification (from
sidid), HVSC songlength, and our per-SID build status.

Built by `tools/build_sid_db.py`. Re-runnable, idempotent. ~20 s
incremental (mtime cache), ~45 s cold.

## Why this exists

Engine-by-engine work is the natural unit when extending coverage —
not composer-by-composer. The DB lets you ask
"which Rob_Hubbard tunes haven't we migrated yet, sorted by
musical substance?" with one SQL query instead of walking 60k files.

## Schema (essentials)

One table `sids`, primary key `path` (relative to `hvsc84/`).

Key columns:
- `engine` — sidid classification, e.g. `'Rob_Hubbard'`, `'Companion'`,
  `'GoatTracker_V2.x'`, `'DMC'`. NULL = unclassified by sidid (~2,600 files).
- `title`, `author`, `released` — PSID/RSID header strings
- `n_subtunes`, `is_psid`, `psid_version`, `load_addr`, `init_addr`, `play_addr`
- `songlength_s` — HVSC total songlength (sum over subtunes)
- `md5` — original file's md5
- `pipeline` — `'pipelines/hubbard/<engine>'` if migrated, else NULL
- `usf_path` — relative path to our `.usf` if it exists
- `sidfinity_md5` — md5 of our rebuilt `.sidfinity.sid` if it exists
- `verify_status` — `'ok'` | `'fail'` | NULL (NOT YET WIRED — future verify_all hook)

Indexes on `engine`, `pipeline`, `md5`.

## Querying — no sqlite3 CLI, use Python

```python
import sqlite3
db = sqlite3.connect('hvsc84.db')

# Coverage by engine
for row in db.execute("""
    SELECT engine, COUNT(*),
           SUM(pipeline IS NOT NULL) AS migrated,
           SUM(sidfinity_md5 IS NOT NULL) AS built
    FROM sids GROUP BY engine ORDER BY 2 DESC LIMIT 20
"""): print(row)

# Unmigrated Rob_Hubbard tunes by length
for path, title, length in db.execute("""
    SELECT path, title, songlength_s FROM sids
    WHERE engine='Rob_Hubbard' AND pipeline IS NULL
    ORDER BY songlength_s DESC LIMIT 10
"""): print(f'{length:5.0f}s  {title}  ({path})')
```

## Auto-updates from the pipeline

The pipeline writes back to the DB automatically via `src/sid_db.py`:

- per-engine `extract/to_usf.write_*_usf()`       → `usf_path`
- `pipelines.build_from_usf.build_from_usf()`     → `sidfinity_md5`
- `pipelines.hubbard.verify.verify_all()` → `verify_status`, `verify_ok_subs`, `verify_total_subs`, `last_verified_at`

All wrapped in try/except — best-effort, never blocks the build. If
`hvsc84.db` doesn't exist yet, the writes silently no-op.

## When to manually re-run `tools/build_sid_db.py`

- First-time DB initialisation (auto-updates need the row to exist)
- Adding a new engine pipeline → so `pipeline` column gets populated
  for that SID (auto-update only writes after the next build)
- HVSC update (re-walks the tree; adds rows for new SIDs)
- Re-running sidid (refreshes `engine` column)
- Schema changes — re-run with `--rebuild` to re-hash everything

For day-to-day work: just build and verify normally, the DB stays
current.

## Counts as of 2026-05-27

```
total SIDs:           60,572
classified by sidid:  57,933
with songlength:      60,572
Rob_Hubbard:             287 (12 migrated, 12 built)
Companion:                26 (13 migrated, 13 built)
```

## Related

- [[reference_usf_v2_format]] — the USF v2 format the `.usf` files use
- [[project_pipelines_layout]] — where the pipelines live
