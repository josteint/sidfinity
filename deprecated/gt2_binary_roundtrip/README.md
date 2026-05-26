# GT2 Binary Roundtrip

Tools for parsing GoatTracker V2 SID binaries and re-encoding them byte-for-byte. Used to verify the parser extracted data correctly before the USF pipeline existed.

Superseded by the USF pipeline which goes through a musical intermediate representation instead of binary-level round-tripping.

- `gt_encoder.py` — encode parsed GT2 data back to a SID binary
- `gt_roundtrip.py` — verify lossless parse/encode cycle
- `gt_modify.py` — modify GT2 SIDs (transpose, etc.)
