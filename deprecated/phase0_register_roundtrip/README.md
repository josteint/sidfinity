# Phase 0: Register-Level Roundtrip

The earliest pipeline: dump SID registers frame-by-frame, convert to a symbolic format, rebuild a SID that replays the exact register sequence. Achieved 100% lossless roundtrip on 56,936 PSID files.

Superseded by the USF pipeline which works at the musical level (notes, instruments, patterns) instead of raw register dumps. The register-level approach produced byte-identical output but had no musical understanding — useless for ML training.

- `sid_symbolic.py` — register CSV to/from symbolic format
- `sid_builder.py` — build PSID v2 from register CSV
- `validate_hvsc.py` — batch validation on all HVSC files
