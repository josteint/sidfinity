# sidxray — player reverse-engineering toolkit (deprecated)

Originally at `src/sidxray/`. A toolkit for cracking new SID player
engines by capturing memory traces from `siddump --memtrace` and
analysing the access patterns: data-region discovery, freq-table
discovery, GT2-layout detection, autocorrelation/periodicity/tempo
analysis.

```
analyze.py           autocorrelation, periodicity, tempo, column classification
discover.py          data region discovery from memory access patterns
discover_to_usf.py   discovery → USF (v1)
drum_extract.py
gt2_detect.py        GT2 layout detection from traces
METHODOLOGY.md       how to reverse-engineer any SID player
docs/                research notes
```

Useful research material — kept for reference if a future workstream
ever tackles a new engine outside the Hubbard '85 family. The USF v2
/ Hubbard byte-exact workflow doesn't need this toolkit (each engine
is reverse-engineered by hand and described as an `EngineConfig`).

## Reviving

Move `sidxray/` back to `src/sidxray/`. Nothing in the active path
imports from it.
