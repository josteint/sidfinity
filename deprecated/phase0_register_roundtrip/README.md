# Phase 0: Register-Level Roundtrip

The earliest pipeline: dump SID registers frame-by-frame, convert to a symbolic format, rebuild a SID that replays the exact register sequence. Achieved 100% lossless roundtrip on 56,936 PSID files.

Superseded by the USF pipeline which works at the musical level (notes, instruments, patterns) instead of raw register dumps. The register-level approach produced byte-identical output but had no musical understanding — useless for ML training.

## `data/validation.db` — a frozen historical record, tracked on purpose

12 MB SQLite, 60,572 rows in `results`: one per HVSC file, the recorded outcome
of the original full-corpus validation run that established the 100% lossless
register-level roundtrip claim above.

Kept in git deliberately. `validate_hvsc.py` takes `--db` and CREATES a fresh
database, so the tooling runs without it — what would be lost is the
MEASUREMENT itself, and re-running it would need the whole deprecated
register-level pipeline back on its feet.

⚠ It was briefly removed on 2026-08-25 during a history scrub and then
restored, so it appears only in recent history. That scrub targeted
`hvsc84.db` (128 versions) and `hvsc84.csv` (72) — REGENERATED artifacts where
every rebuild stored a whole new copy. This file is the opposite case: written
once, never rewritten. Do not remove it on size grounds.

- `sid_symbolic.py` — register CSV to/from symbolic format
- `sid_builder.py` — build PSID v2 from register CSV
- `validate_hvsc.py` — batch validation on all HVSC files
