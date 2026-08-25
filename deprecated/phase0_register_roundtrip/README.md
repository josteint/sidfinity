# Phase 0: Register-Level Roundtrip

The earliest pipeline: dump SID registers frame-by-frame, convert to a symbolic format, rebuild a SID that replays the exact register sequence. Achieved 100% lossless roundtrip on 56,936 PSID files.

Superseded by the USF pipeline which works at the musical level (notes, instruments, patterns) instead of raw register dumps. The register-level approach produced byte-identical output but had no musical understanding — useless for ML training.

## ⚠ `data/validation.db` IS PRESENT BUT UNTRACKED (since 2026-08-25)

The file is on disk (60,572 rows in `results` — the stored outcome of the
original full-HVSC validation run) and `validate_hvsc.py` reads it normally.
It is simply **no longer in git**, and `.gitignore` keeps it that way.

Scrubbed from the entire history along with `hvsc84.db` × 128 versions,
`hvsc84.csv` × 72 and `gt2_grading/data/grades.db`: each is a binary rewritten
WHOLESALE on every run, so git stored a complete new copy per commit — ~2.4 GB
of raw history between them, and `.git` went from 158 MB to 43 MB without them.

⚠ A fresh clone will NOT have this file. Less critical than its gt2_grading
counterpart — `validate_hvsc.py` takes `--db` and CREATES the database, so the
tooling runs either way; what a clone lacks is the recorded RESULTS. Copy it
across by hand when moving hosts; do not `git add -f` it.

- `sid_symbolic.py` — register CSV to/from symbolic format
- `sid_builder.py` — build PSID v2 from register CSV
- `validate_hvsc.py` — batch validation on all HVSC files
