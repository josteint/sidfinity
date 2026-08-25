# Phase 0: Register-Level Roundtrip

The earliest pipeline: dump SID registers frame-by-frame, convert to a symbolic format, rebuild a SID that replays the exact register sequence. Achieved 100% lossless roundtrip on 56,936 PSID files.

Superseded by the USF pipeline which works at the musical level (notes, instruments, patterns) instead of raw register dumps. The register-level approach produced byte-identical output but had no musical understanding — useless for ML training.

## ⚠ `data/validation.db` IS NO LONGER IN THIS REPO (removed 2026-08-25)

`validate_hvsc.py` takes `--db validation.db` and CREATES it, so the scripts
here still run — but the stored RESULTS of the original 60,572-file HVSC
validation run are no longer in the working tree or in git history. Preserved
outside the repo instead of deleted:

    ~/phase0-validation.db            (verified: PRAGMA integrity_check = ok,
                                       60,572 rows in `results`)

Removed as part of taking `.git` from 158 MB to 43 MB — the history carried
~2.4 GB of superseded database snapshots (`hvsc84.db` × 128 versions,
`hvsc84.csv` × 72, plus this and `gt2_grading/data/grades.db`). If you restore
it, keep it OUT of git: a binary DB rewritten wholesale on every run is what
caused the bloat.

- `sid_symbolic.py` — register CSV to/from symbolic format
- `sid_builder.py` — build PSID v2 from register CSV
- `validate_hvsc.py` — batch validation on all HVSC files
