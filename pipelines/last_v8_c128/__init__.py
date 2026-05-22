"""Pipeline for Rob Hubbard's *The Last V8 (C128 version)* (1985 MAD).

This SID is an RSID, IRQ-driven, with a dual engine — a tracker driver
(subtunes 0-2 and 6+) plus a one-shot digital-sample player (subtunes
3-5) that's relocated to $C000 at init time.

The pipeline currently covers the **extract** step (it parses the binary
and produces a structured engine model). The Lean **codegen** step is a
tombstone — it builds and runs, but the generated SID has no player
code yet. See README.md for what's implemented and what isn't.
"""
