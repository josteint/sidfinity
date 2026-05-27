# GT2 pipeline + GoatTracker bundles (deprecated)

The static-binary GT2 / GoatTracker conversion pipeline + the bundled
GoatTracker tracker source distributions (`GoatTracker_2.65` through
`2.77`, both extracted and as `.zip`). Moved from `src/` during the
USF v2 cleanup.

```
converters/
  gt2_to_usf.py        GT2 binary → USF v1
  dmc_to_usf.py        DMC → USF v1
  rh_to_usf.py         Hubbard → USF v1
  regtrace_to_usf.py   universal register-trace → USF v1
  usf_to_sid.py        USF v1 → rebuilt SID (via V2 codegen)
gt2_decompile.py       GT2 binary decompiler
gt2_parse_direct.py    operand-based GT2 parser
gt2_detect_version.py  GT2 player group A/B/C/D detection
gt2_packer.py          GT2 freq tables + packing constants
gt2_to_usf.py          GT2 → USF (top-level)
sidid.py               SidID engine-identification wrapper
sidfinity_pack.py      sidfinity player packer (xa65 asm)
detect_flags.py        GT2 compilation flag detection
discover_freq_tables.py freq-table discovery from played output
gt2/                   embedded GoatTracker headers / driver source
regtrace_to_usf.py     universal fallback — register CSV → USF (v1)
GoatTracker_2.6X/      12 tracker source distributions (2.65 ... 2.77)
GoatTracker_2.6X.zip   the same as zips
```

Superseded by the USF v2 / Hubbard byte-exact pipeline at
`pipelines/hubbard/`. The GT2 work reached partial coverage of HVSC
GT2 SIDs and produced the Grade S/A/B/C/F bucketing — see
`../gt2_grading/` for the grading tools and data snapshots.

## Reviving

Move `converters/`, `gt2*.py`, etc. back to `src/`. The GT2 pipeline
is self-contained (only depended on `src/gt_parser.py`, which is
still in `src/`).
