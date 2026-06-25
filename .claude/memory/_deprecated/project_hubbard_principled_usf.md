---
name: hubbard-principled-usf
description: "Phase-2 principled-USF refactor — moved ~300 engine-mechanism integers out of Hubbard '85 USFs into engine_constants.py per engine name. USFs now carry music + per-tune init state only."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

The 12 Hubbard '85 engines (+ Companion '84) each shipped a top-level
`params { ... }` block in their .usf files with ~23 named mechanism
ints (`arp_interval`, `vib_onset`, `master_vol_base`,
`first_frame_gate_off`, `seed_overlap`, ...). 5_Title_Tunes additionally
carried per-subtune `params { ... }` blocks (~5 fields × 5 subs).
Up_up_and_Away had 3 vestigial `freq_table_base/instr_base/instr_count`
placeholders. Total: ~300 forbidden-shape ints across the corpus.

Per [[feedback_usf_representation_principle]] Rule 2 — "musical content
to USF, mechanism to engine" — these are engine properties, not music.

**Phase 2 (2026-05-29)** moved them all to
`pipelines/hubbard/engine_constants.py`. The shape:

- 20 new fields on `EngineConstants` (one per knob).
- New `subtune_overrides: dict[int, dict]` for compound engines
  (5_Title_Tunes is the only user — its 5 sub-engines each get an
  override entry keyed by subtune index).
- Defaults match the Commando flavor; each engine's
  `ENGINE_CONSTANTS[name]` sets only the deltas.
- `_inputs_from_usf` in `build_from_usf.py` reads from
  `ec.foo` instead of `usf.params.fields.get('foo', default)`.
- The extract path (`_params_from_config`) emits an empty
  top-level Params; 5_Title_Tunes drops the per-subtune Params
  blocks; Up_up_and_Away drops the 3 placeholder fields.

## Verification

- 11 standard engines × 85 subtunes byte-exact via `verify_all`.
- 5_Title_Tunes 4/5 byte-exact via `compare_instruction_stream`.
  Sub 2's failure is a pre-existing `skip_init` alignment artifact
  (same on baseline) — not a refactor regression.
- Up_up_and_Away unchanged from baseline (writelog comparison was
  already failing before this refactor; uses a different verification
  path that I didn't disturb).

## Phase 3 (same date) — drop per-voice init block too

The per-voice init values for the 11 standard engines weren't actually
per-tune: each is the byte at a fixed freq-table-overlap offset (205,
208, 214, 229, 232, 239) — bytes already present in
`engine_constants.freq_bytes`. Phase 3 drops the init block from those
USFs entirely; the codegen reads from engine constants directly.

Grammar widened: `init_voice+` → `init_voice*` so `init { }` parses.
The reader-side overlay honors legacy init voices if present so old
.usf files still build byte-exact.

## What still stays in USF (intentionally)

- 5_Title_Tunes' per-subtune init blocks (each of the 5 sub-engines
  has its own `freq_bytes`; the per-sub ovseed comes from each sub's
  overlap region). Could be derived from `subtune_overrides` carrying
  per-sub `EngineConstants` references; deferred.
- Companion's per-subtune params blocks (Up_up_and_Away) — separate
  pipeline with subtune-level engine state in params; not touched.

## Read-side default elimination

Previously `_inputs_from_usf` had ~22 calls of the form
`get('foo', default_value)` — each one a soft default that legacy
USFs (missing the field) could rely on. Now every value comes from
`ec.foo` directly. If a new engine is added without setting a knob
in `ENGINE_CONSTANTS`, the EngineConstants dataclass default fires
explicitly — there's one place to look.

## Related

- [[feedback_usf_representation_principle]] — Rule 2 is what drove this
- [[project_companion_principled_usf]] — Phase 1 (Companion strains)
- [[project_usf_refactor]] — the broader USF effort
