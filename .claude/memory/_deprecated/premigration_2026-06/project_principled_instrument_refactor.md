---
name: project-principled-instrument-refactor
description: Done 2026-06-01. The Instrument schema is now fully self-contained — five per-engine-bookkeeping leaks removed in favor of typed per-instrument sub-configs. Hubbard 71 + Companion 35 byte-exact through the new schema.
metadata: 
  node_type: memory
  type: project
  originSessionId: ce060f8a-e40f-4b55-9551-2d4fc0bb3028
---

# Principled Instrument schema refactor (done 2026-06-01)

## What it did

Removed five same-pattern §2-failure-mode leaks from the `Instrument`
schema. Pattern was always: a per-instrument flag/scalar paired with
per-tune parameters in `params { }` (or `engine_constants.py`) that
completed its meaning. Model saw a token whose meaning lived outside
the data → the leak.

Fixes (all phases in `docs/refactor_plan_principled_instrument.md`):

1. **`freq_slide: bool` → `freq_slide_config: FreqSlideConfig`**
   (mode + initial_dir + bounds + step + high_oct_arp). One-shot-halt
   captures Hubbard's skydive; bidirectional captures jay_derrett's
   sweep.
2. **`inc_by2: bool` + per-tune `incby2_*` → `inc_by2_config: IncBy2Config`**
   (mode + step + onset + late_gate).
3. **`envelope.gate_off_delta` + `adsr_zero_delta` → `envelope.release_ctrl: int`**
   The musical content is "the CTRL byte during release," universal
   across engines. Mechanism (delta-add vs OR-in) stays engine-private.
4. **per-tune `vib_onset` → `vibrato.onset`** per-instrument.
5. **per-tune `arp_interval`/`arp_period`/`arp_phase_invert` → per-instrument `arp.*` fields.**

Phase 1: additive schema (new fields, defaults). Phase 2: Hubbard
extract populates the new fields from existing per-tune values.
Phase 3a: composer prefers per-inst over params. Phase 3b: extract
stops writing legacy. Phase 3c: schema drops the deprecated fields
entirely.

## Final state

A grep for the forbidden shapes returns nothing across all USFs:

```
gate_off_delta, adsr_zero_delta, fx: freq_slide, fx: inc_by2,
vib_onset: (top params), arp_interval: (top params), arp_period:,
arp_phase_invert:, incby2_step: (top params), incby2_late_gate: (top),
incby2_onset:
```

Each `Instrument` is **fully self-contained** — reading any one
instrument in isolation tells you exactly what it does musically.
Model sees per-instrument values that mean the same musical thing
across all engines (cross-engine cardinality test passes).

Regression: 71 Hubbard '85 + 35 Companion stay byte-exact across
the entire refactor; verified after every phase.

## Notable specifics

- **5TT `_Inputs` shim**: 5_Title_Tunes' unified `_Inputs` lacks
  `vib_onset` / `arp_phase_invert` named fields. Its `write_unified_usf`
  passes a small `_5TTConfig` shim to `_convert_instrument` that
  supplies `vib_onset=8` and `arp_phase_invert=False` (5TT engine's
  true tune-level values). Without the shim, Phase 3b broke 3/5 5TT
  subtunes because instruments inherited the EngineConfig defaults
  (vib_onset=6).
- **Companion engines (clever_music, bowden, henrys_house, yes_tune)**:
  envelope.release_ctrl stays at 0 (default). Composer's hr_ctrl for
  Companion paths derives from `init_ctrl & $FE` as before.
- **Composer fallback paths preserved**: the `prefer_inst` helper in
  `_inputs_from_usf` still has param-key fallbacks (`get(param_key,
  default)`) even though no current USF triggers them. Dead code but
  harmless — left in case some downstream USF lacks the new fields.

## Out of scope (separate audits)

Remaining `params { }` leaks (not same shape — these are tune-level
or engine-quirk, not per-instrument with hidden tune-level
parameters):

- **5TT per-subtune `subtune.params`** still carries `incby2_step`,
  `incby2_late_gate`, `tick_divider`, `speed_ctr_init`. These are
  per-subtune-mechanism (the 5 compound sub-engines). The composer's
  per-subtune-table codegen reads them; `has_per_subtune` triggers
  via per-sub `init` (not by these keys). They could move per-inst
  (each 5TT inst belongs to one sub) but that's a 5TT-specific
  refactor.
- **Master volume modulation** (`master_vol_*` family — 5 knobs).
- **Engine-quirk booleans** (`linear_pw_or`, `seed_overlap`,
  `tie_preserves_slide`, `frame_ctr_init`, etc.).
- **SFX bookkeeping** (`sfx_state_ofs`, `sfx_framectr_ofs`, etc.).
- **`digi_player: chimera_1bit`** named reference (Pole A-shaped
  but the value is musically descriptive — re-evaluate when more
  digi engines land).
