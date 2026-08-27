---
name: hvsc-db
description: "hvsc85.parquet (+ engine_docs.csv) — the HVSC STATIC catalogue, DuckDB-queried via src/sid_db. Catalogue-only (no build-status columns as of 2026-07-04); build status/coverage comes from a fresh family batch, NOT the index. Regenerate with tools/build_sid_db.py."
metadata:
  node_type: memory
  type: reference
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
  modified: 2026-08-09T19:15:09.858Z
---

The HVSC index at the repo root indexes every `.sid` under `hvsc85/`. Storage
history: SQLite `hvsc84.db` → CSV (2026-06-15) → **Parquet** (2026-07-04, zstd
~3 MB, dropped from the 12 MB CSV). The file is named for the HVSC release it
indexes, so it is renamed on every collection update (`hvsc84.parquet` →
`hvsc85.parquet`, 2026-08-09). Queried via DuckDB through
`src/sid_db.py`. Second table `engine_docs` (per-family research state) stays a
small CSV.

## sidid is the OUTERMOST DENOMINATOR (2026-08-27)

The `engine` column comes from sidid, and every family's corpus is selected
from it (`route.DMC_ENGINE_SQL = "engine LIKE 'DMC%'"`). So the chain is
**sidid -> `engine` -> the family roster -> routing -> batches -> coverage %**,
and every number quoted anywhere is conditional on the first step. This is the
one denominator ABOVE the roster, so `pipelines/dmc/route.py --gaps` cannot see
it by construction (that check starts from the roster).

Two failure directions, and they behave differently:

- **False negative** (a real family member sidid labels otherwise, or leaves
  unclassified) — invisible EVERYWHERE: no roster row, no routing, no batch, no
  census. PROBED 2026-08-27: both DMC detectors run over all 1,331 unclassified
  members plus 1,730 sampled across the other 644 engine strings -> **0 claimed**
  (`tmp/sidid_falseneg.py`). ⚠ That bounds one thing only — a member our
  factories ALREADY recognise. A DMC-derived player neither factory knows looks
  identical to a non-DMC file from here, so the probe cannot rule it out.
- **False positive** (labelled DMC, isn't) — lands in the roster's UNCLAIMED
  bucket and reads as work to do. `route.summarise`'s "no pipeline recognises
  the player" split (110 of DMC's 309, 2026-08-27) is where they hide.

**THE LEVEL ABOVE SIDID — does every file even REACH the catalogue?**
Reconciled 2026-08-27, as SETS not counts (equal counts can hide a swap):

| | n |
|---|---:|
| `.sid` on disk under `hvsc85/`, excluding our 12,673 `*.sidfinity.sid` | **61,157** |
| rows in `hvsc85.parquet` | **61,157** |
| classified paths in `tools/sidid_full.txt` | 59,826 |
| `engine IS NULL` | 1,331 |

on-disk minus DB = 0, DB minus on-disk = 0, sidid-minus-disk = 0, and
`disk - sidid` is EXACTLY the `engine IS NULL` set (so there is no third
state: every file is classified or explicitly unclassified). `build_sid_db`'s
walk skips `DOCUMENTS` / `C64Music` / `update`; all three verified to hold
**0** `.sid` (`C64Music` does not exist — this tree is flattened to
DEMOS/GAMES/MUSICIANS at the top level), so the filter loses nothing today —
RE-CHECK IT AFTER A COLLECTION UPDATE, since an update pack landing in
`update/` would be skipped silently. Known deliberate exclusion: the top-level
`.d64`/`.d71`/`.d81`/`.dfi` HVSC bonus disk images (SIDs inside a disk image,
not extracted files).

**⚠⚠ WE RUN SIDID IN SINGLE-MATCH MODE AND THROW AWAY HALF ITS OUTPUT
(2026-08-27).** `sidid -m` = "scan each file for multiple signatures"; without
it the C loop does `if (!multiscan) break;` on the first hit, so `engine` is
whichever signature happens to come first in `sidid.cfg`. Re-scanned HVSC with
`-m`: **28,198 of 58,457 matched files (48.2%) match MORE THAN ONE player**
(2 matches 27,061 · 3 1,035 · 4 89 · 5 8 · 6 5). Two things are being lost:

- **SUB-VERSIONS.** The parenthesised names are finer signatures — top pairs:
  `(DMC_V4.x)+DMC` 5,394 · `(DMC_V5.x)+DMC` 2,254 ·
  `(FutureComposer_V1.0)+MoN/FutureComposer` 3,119 ·
  `(VoiceTracker)+Music_Assembler` 2,376 · `(MusicMaster_1)+Soundmonitor` 2,193.
  **sidid already knows v4 from v5**, and we discard it and re-derive the split
  with route.py's factory dispatch.
- **HETEROGENEOUS FILES.** Freespace_2075 -> `DMC + (DMC_V4.x) +
  Music_Assembler + (Music_Assembler/MC)`; Black_It and Super_Tau-Zeta ->
  `DMC + (DMC_V4.x) + (DMC_V5.x)`. Correct in every case, and exactly the C31 /
  C35 structure we currently rediscover per family. Single-match reports plain
  `DMC` for all three.

⚠ NB the `-m` output format: a continuation line has a BLANK 56-char path
field, so a parser keyed on "line starts with a path" silently drops every
extra match and reports 0% multi (it did, first try).

**HOW FAR SIDID CAN BE TRUSTED — measured, not assumed.** It is byte-pattern
matching: 788 player entries / 934 signatures, `??` wildcards, matched anywhere
in the file including DATA. Structural weaknesses: first-match-wins without
`-m`, so cfg ORDER decides; **41 signatures are <=8 bytes** (shortest 5:
`(Steve_Rowlands)`, `256bytes/LFT`, `Basic_Program` x3, `Drumtex/SidBarrett`);
and a PACKED file matches the cruncher, not the player (it has
`Crunched:Exomizer` / `Crunched:PUCrunch` signatures for exactly that).
Against that, the empirical agreement with our OWN play-body dispatch — which
is relocation-invariant and strictly stronger — is high: v4<->v4 5,399,
v5<->v5 2,014, v6<->v6 16, and only **11 members where sidid names one
sub-version and we route to the other** (all sidid-v5 / routed-v4, listed in
[[project_dmc]]). No DMC false negatives either (see the probe above).

**AND IT REFRAMES THE 309 UNROUTED**: sidid gives a sub-version for **286 of
them** (240 v5, 42 v4, 4 both) — only 23 are bare `DMC`. So they are mostly NOT
mislabels; they are genuine family members whose specific player OUR factory
does not recognise. Treat sidid's sub-version as the candidate generator when
attacking them.

⚠ It is also a MOVING denominator, regenerated by hand (~3 min), never on a
trigger — C20's seventh layer at the classification level. Two known hazards,
both integrity-checked 2026-08-27 and clean: upstream's 56-char path truncation
(silently dropped 1,384 members = 2.3% of HVSC; `tools/sidid_no_truncate.patch`
fixes it and A RE-CLONE WITHOUT THE PATCH REINTRODUCES THE LOSS) — verified by
`0 of 59,826 classified paths missing from disk`; and its scan of our own
`*.sidfinity.sid` rebuilds — verified filtered (the only "sidfinity" in the
dump is the header's scope note).

**It gates RESEARCH priority too**, via `engine_docs` being keyed on the sidid
family: 646 distinct engine strings, only **49 have an `engine_docs` row** (45
OK + 4 LITTLE, 52,657 SIDs = 86% of the corpus). The other ~597 have no row at
all — `Kosa_Protracker` (13 members) among them. A sidid label meaning "not
this family" is a correct ROUTING answer and says nothing about whether the
family deserves work; conflating those two is how a 2026-08-27 session
mis-reported 11 Kosa members as unrouted DMC. See [[project_dmc]].

## 2026-07-04: catalogue-only + parquet (the big change)

The index is now **static catalogue ONLY** — path, PSID header, `engine`,
`songlength_s`, `md5`, `excluded`/`exclusion_reason`. The build-status columns
(`verify_status`/`verify_ok_subs`/`verify_total_subs`/`last_verified_at`/
`usf_path`/`sidfinity_md5`/`pipeline`) and the `src/sid_db.record_*`
write-through were **REMOVED**: zero readers, ~99.9% empty, palimpsest-prone (a
persisted verdict rots the moment extract/composer code changes), and the
full-file-rewrite write path was a concurrency hazard for parallel sessions.

So **nothing writes the index in normal dev** — it's regenerated wholesale by
`build_sid_db.py` and is read-mostly / parallel-safe. `record_usf`/
`record_rebuild`/`record_verify` are gone; all callsites removed. **Do NOT
reintroduce a build-status column** — see [[feedback_convergence_ledger]] C20.

## Coverage / FULL-list = a fresh family batch, never the index or stored files

The source of truth for "which members are FULL" is a fresh
`pipelines/<family>/family_batch.py` run (each `run_member` re-extracts into a temp
dir — it never reads stored `.usf`). Do NOT derive a FULL list from stored
`hvsc85/*.usf` existence or from the index. Batch results jsonls are stamped
with a **`code_hash`** ([[reference_hvsc_db]] → `src/code_fingerprint.py`): on
resume a row is reused ONLY if its hash matches the current engine dependency
set (`pipelines/<engine>` + `src/usf` + `verify_cycle`), so a code change
auto-re-verifies the members it could have affected — killing the "stale-.usf
palimpsest" trap (the phantom "my fix regressed N FULLs"). This is safe under
parallel sessions on different engines: a shared-code edit changes every
dependent engine's hash; an other-engine edit doesn't. The `pipelines/<family>/mass_write.py`
tools skip + warn on any FULL row whose code_hash is stale, so they never write
an unverified build to disk.

## Querying — `src/sid_db` shells out to the DuckDB CLI binary

`src/sid_db.query(sql, params)` / `connect().execute(...)` spawn
`duckdb -json -c "<view setup>; <sql>"` (binary on PATH → `~/.local/bin/duckdb`),
return sqlite3-style tuples. **Reads need only `duckdb` on PATH — NO env.sh /
PYTHONPATH / .pylocal.** The python `duckdb` module is not used. The `sids` view
= `read_parquet('hvsc85.parquet')`; `engine_docs` = `read_csv(...)`. `read_all()`
= one `duckdb -json` process (typed rows) for per-row loops. `?` params, LIKE,
`random()` work; **no `SUM(bool)`** (use `SUM(CASE WHEN … THEN 1 ELSE 0 END)`).
Ad-hoc CLI: `duckdb -c "SELECT … FROM read_parquet('hvsc85.parquet')"`.

```python
from src import sid_db
for path, title in sid_db.query(
    "SELECT path, title FROM sids WHERE engine='Rob_Hubbard' "
    "ORDER BY songlength_s DESC LIMIT 10"): print(path, title)
```

## When to re-run `tools/build_sid_db.py`

Only when the STATIC catalogue changes: an HVSC update (#85), a `sidid` re-run
(engine column), or edits to `tools/excluded_sids.json` / `tools/engine_docs.json`
(`apply_engine_docs.py` refreshes just the docs CSV). Idempotent, ~13 s with the
mtime cache. No per-build triggers anymore. `--rebuild` re-hashes everything.

## Related

- [[reference_usf_format]] — the USF format the `.usf` files use
- [[feedback_convergence_ledger]] — C20 stale-FULL palimpsest (the trap this scheme closes)
