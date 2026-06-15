---
name: hvsc84-db
description: "hvsc84.csv (+ engine_docs.csv) — the HVSC #84 index, git-tracked CSV queried via DuckDB (src/sid_db). Migrated 2026-06-15 from the old hvsc84.db SQLite blob. Run tools/build_sid_db.py to refresh."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

**2026-06-15: migrated SQLite (`hvsc84.db`) → git-trackable CSV + DuckDB.**
The index is now `hvsc84.csv` (path-sorted, one row per SID — build-status
changes show as readable git line diffs instead of a 21MB binary blob churn)
+ `engine_docs.csv`. Queried via DuckDB through `src/sid_db.py`. The old
`hvsc84.db` is deleted + gitignored. Full pipeline regression stayed green
across the migration.

`hvsc84.csv` at the project root indexes every `.sid` file under
`hvsc84/` with PSID/RSID header fields, engine classification (from
sidid), HVSC songlength, and our per-SID build status.

Built by `tools/build_sid_db.py` (walk/hash/classify unchanged; only the
storage swapped to CSV). Re-runnable, idempotent. ~20 s incremental (mtime
cache from the existing CSV), preserves write-through `verify_*` columns.

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
- `verify_status` — `'ok'` | `'fail'` | NULL (wired: `verify_all` write-through
  via `src/sid_db.record_verify`)

Empty CSV field == SQL NULL. Schema (columns + DuckDB types) is defined in
`src/sid_db.py` (`SIDS_TYPES`).

## Querying — via DuckDB through `src/sid_db` (source `src/env.sh` first)

`src/sid_db.connect()` returns a DuckDB connection with `sids` +
`engine_docs` views over the CSVs, wrapped so `db.execute(sql, params)`
returns an iterable of tuples (sqlite3-style, + `.fetchall()/.fetchone()`).
`sid_db.query(sql, params)` is the one-shot helper. DuckDB SQL is
SQLite-compatible for these queries (LIKE, GROUP BY, `?` params,
`ORDER BY random()`, IS NULL on empty fields). The duckdb **Python module**
lives in `.pylocal` (gitignored, on env.sh PYTHONPATH); ad-hoc CLI use:
`read_csv('hvsc84.csv', header=true, nullstr='')`.

```python
from src import sid_db
# Coverage by engine
for row in sid_db.query("""
    SELECT engine, COUNT(*),
           SUM(CASE WHEN pipeline IS NOT NULL THEN 1 ELSE 0 END) AS migrated,
           SUM(CASE WHEN sidfinity_md5 IS NOT NULL THEN 1 ELSE 0 END) AS built
    FROM sids GROUP BY engine ORDER BY 2 DESC LIMIT 20"""): print(row)

# Unmigrated Rob_Hubbard tunes by length
for path, title, length in sid_db.query("""
    SELECT path, title, songlength_s FROM sids
    WHERE engine='Rob_Hubbard' AND pipeline IS NULL
    ORDER BY songlength_s DESC LIMIT 10"""): print(f'{length:5.0f}s  {title}')
```

(NB: DuckDB has no `SUM(bool)`; use `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`
or `COUNT(*) FILTER (WHERE ...)`.)

## Auto-updates from the pipeline

The pipeline writes back to the DB automatically via `src/sid_db.py`:

- per-engine `extract/to_usf.write_*_usf()`       → `usf_path`
- `pipelines.build_from_usf.build_from_usf()`     → `sidfinity_md5`
- `pipelines.hubbard.verify.verify_all()` → `verify_status`, `verify_ok_subs`, `verify_total_subs`, `last_verified_at`

Write-through does a CSV read-modify-write (the file has no row-level
update) — fine for the single-threaded interactive-build / regression paths
that use it (the parallel batches build to `tmp/` and never write-through;
they refresh via an explicit `build_sid_db.py` run after mass-write). If
`hvsc84.csv` doesn't exist yet, or the row is absent (a brand-new SID), the
writes silently no-op — re-run `build_sid_db.py` to insert.

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
