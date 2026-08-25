# GT2 grading / HVSC dashboard (deprecated)

The pre-USF-v2 workflow for measuring SIDfinity's coverage of HVSC. Built
around the Grade S/A/B/C/F bucketing produced by `src/sid_compare.py`'s
jitter-tolerant comparator and tracked at HVSC scale (22 269 songs in
`grades.db`).

Superseded by the byte-exact USF v2 workflow — `pipelines.hubbard.verify.verify_all`
returns a simple per-subtune OK/FAIL based on md5 of per-frame SID-register
snapshots, with no need for a grade DB or coverage dashboard.

The GT2 / GoatTracker pipeline itself (the static parsers at `src/gt2_*.py`)
is still active code, but its grading and HVSC-coverage tooling sit here
because they're tied to the old comparison methodology.

## ⚠ `data/grades.db` IS NO LONGER IN THIS REPO (removed 2026-08-25)

Four scripts here still reference `data/grades.db` — `grade_db.py`,
`hvsc_dashboard.py`, `update_readme.py` and `regression_test.py`. The file is
gone from the working tree AND from git history, so nothing here runs as-is
until you put it back.

It was a 13 MB SQLite database (22,269 songs + 48,302 history rows) and it is
NOT regenerable — `regression_test.py` calls it a FROZEN baseline, and the
comparator that produced it (`src/sid_compare.py`'s jitter-tolerant grading)
is itself deprecated. So it was preserved rather than deleted:

    ~/gt2-grades-baseline.db          (verified: PRAGMA integrity_check = ok)

To revive this tooling, copy it back:

    cp ~/gt2-grades-baseline.db deprecated/gt2_grading/data/grades.db

⚠ Do NOT commit it. It was removed because the repo carried ~2.4 GB of
superseded database snapshots across its history (`hvsc84.db` × 128 versions,
`hvsc84.csv` × 72, plus this and `phase0_register_roundtrip/data/validation.db`);
scrubbing them took `.git` from 158 MB to 43 MB. Re-committing a binary DB
that changes wholesale on every write recreates exactly that problem.

## What's here

```
data/
  grades.db                  22269 song grades + 48302 history rows
                             (path, engine, grade, score, last_tested,
                              commit_hash)
  dashboard_cache.json       summary counts of A/USF/ID/PARSE per engine
                             (dmc, gt2, hubbard, jch)
  sidid_full.txt             4.3 MB sidid output across HVSC
  gt2_regression.db          0 bytes — was a placeholder
  player_analysis.json       per-engine aggregate stats (7 known engines)
  player_analysis_all.json   per-file analysis: writes_per_frame, hard-
                             restart classification, multispeed flag, etc.
                             1714 entries
  player_samples.json        per-engine sample lists, 642 entries
  player_file_map.json       per-engine file counts (DMC=10747, GT2=7562...)

scripts/
  hvsc_dashboard.py          HVSC coverage dashboard (reads grades.db +
                             dashboard_cache.json + sidid_full.txt)
  update_readme.py           updates the README Status line from grades.db
  grade_db.py                SQLite API for grades.db
  gt2_triage.py              automated F-grade GT2 song triager
  regression_test.py         3478-song GT2 regression suite (was at
                             src/player/regression_test.py)
  batch_dasmodel_hubbard.py  was: batch-build das_model SIDs for each
                             discovered Hubbard SID; raised
                             NotImplementedError pending the demo/ asm
                             rewrite that never happened (src/)
  commando_hg2.py            was: hand-tuned "holy grail" Commando rebuild
                             experiment, pre-USF-v2 (src/hubbard/)
```

## Reviving

If the GT2 / Grade A workflow becomes useful again:

1. Move `data/*` back to the project's top-level `data/` directory.
2. Move `scripts/hvsc_dashboard.py`, `gt2_triage.py`, `update_readme.py`,
   `grade_db.py`, `batch_dasmodel_hubbard.py` back to `src/`.
3. Move `scripts/regression_test.py` back to `src/player/`.
4. Move `scripts/commando_hg2.py` back to `src/hubbard/`.
4. Update CLAUDE.md and README.md to reference them again.

The data is a snapshot from a specific point in time (approximately the
state at HVSC #84 release) — re-run the relevant pipelines against current
HVSC if you need a fresh measurement.

## Addendum (2026-05-27): grading + analysis tools added during the src/ cleanup

The following grading-era utilities also moved here from `src/`:

```
sid_compare.py             jitter-tolerant register comparator (the
                           comparator that produced Grade S/A/B/C/F)
writelog_diff.py           writelog comparison
writelog_align_grade.py    align-by-content + grade
writelog_grade.py          writelog-based grading
audio_compare.py           PCM cross-correlation + spectral similarity
py65_grade.py              py65-based grading
ground_truth.py            ground-truth helpers
batch_grade_hubbard.py     batch-grade all Hubbard SIDs
batch_discover_landmarks.py
discover_hubbard_landmarks.py
code_flow.py               control-flow code_end detection
freq_reconstruct.py        reconstruct freq table from played output
memdiff.py                 classify static vs dynamic memory
memdump_freq.py
rh_decompile.py            Hubbard binary decompiler (the OLD one;
                           pipelines/hubbard/<engine>/extract/decompile.py
                           is the active per-engine decompiler)
rh_to_usf.py               Hubbard → USF (v1) converter
sid_data_extractor.py      universal SID data table discovery
```
