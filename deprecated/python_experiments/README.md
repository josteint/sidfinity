# Deprecated Python experiments

One-off scripts and dead-end approaches from earlier work on the Commando
roundtrip and packing experiments. Moved here to declutter `src/`.

None of these are imported by the current pipeline (composer-native
asm under `pipelines/composer.py`); cross-references between them
point only at other files in this directory.

## Categories

**Old Commando build experiments** (codebook / "holy grail" packing
attempts that predate the USF v3 pipeline):
- `build_commando_codebook.py`, `build_commando_hg9.py`, `build_commando_hg10.py`,
  `build_commando_holyscale.py`, `build_hg12.py`
- `commando_codebook.py`, `commando_hg17.py`, `commando_hg17_flat.py`,
  `commando_z3joint.py`
- `make_commando_hg3.py`
- `holy_grail_compact.py`, `holy_grail_pack.py`, `holy_scale.py`,
  `holy_scale_codegen.py`
- `simple_codegen.py`, `stream_codegen.py`
- `strip_decompose.py`, `structured_pack.py`

**das_model comparison helpers** (used while iterating on the Hubbard
asm model, before V3 became the canonical pipeline):
- `das_compare_5000.py`, `das_compare_context.py`, `das_compare_detail.py`
- `das_model_codegen.py`

**Z3 / SMT exploration** (tried using SMT for various decompose tasks):
- `z3_decompose.py`, `z3_guided_strip.py`, `z3_parallel.py`
- `hubbard_z3_freq_lookup.py`, `hubbard_z3_wavetable.py`

**Effect-detection experiments**:
- `auto_effect_discover.py`, `effect_templates.py`, `effect_to_usf.py`
- `info_theory_analysis.py`
- `effect_detect.py` — DFT / segment analysis routines from the
  initial reverse-engineering phase. The only piece still used (the
  PAL freq table) now lives in `pipelines/hubbard/engine_constants.py`
  as `FREQ_PAL` / `HUBBARD_85_PAL_FREQ_TABLE`.

**GT2 parser**:
- `gt_parser.py` — GoatTracker 2 binary parser from the deprecated
  GT2 pipeline. The PAL freq tables it exported are now derived from
  `engine_constants.HUBBARD_85_PAL_FREQ_TABLE`.

**Old tests / verification scripts**:
- `test_wave_encoding.py`, `verify_note_extraction.py`

If any of these become useful again, lift the specific file back to
`src/` rather than re-importing from this directory.
