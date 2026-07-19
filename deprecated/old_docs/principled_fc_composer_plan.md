> **✅ COMPLETED & ARCHIVED 2026-07-19.** The campaign this plan scoped is
> done: §9 fully closed — the whole FC build is orig-free (model-USF
> buildable), both canaries (Cyb II 2/2 + Hawkeye 12/12) de-verbatim,
> PSID header synthesized. See project_fc_principled_composer.md for the
> landed findings; verdict = verify_featuredriven.

# Principled FC composer — plan

## Status (2026-06-06)

The FC family composer (`pipelines/future_composer/composer_asm.py`)
violates the USF representation principle (`docs/the_principle.md`
§9 completeness test): patterns, sequences, aux tables, and several
filler regions are **verbatim-copied from the orig HVSC binary** at
compose time, not emitted from USF content.

The Hawkeye + Cybernoid II canaries verify byte-exact, but that's a
tautology — the composer copies orig's bytes verbatim and asserts the
rebuild matches orig. A model-generated USF that wasn't derived from
an HVSC SID cannot produce a SID via this composer (no orig bytes to
verbatim-copy from). The principle's §9 completeness test fails:
round-trip requires a side input beyond USF.

By contrast, Hubbard '85's composer (`pipelines/composer.py`) IS
principled — patterns flow through a structured note codec, orderlists
reference dense pattern-pool slots, all data sections come from USF
content alone. The composer never reads orig at compose time.

This document scopes the work to bring the FC composer up to the same
standard.

## What's currently verbatim that needs to become USF-emitted

### Data sections (musical content)

- **Pattern bytes** (~3500 bytes/tune in Hawkeye, 54 patterns ×
  avg ~65 bytes). USF already has structured `Pattern.events` —
  `PatNote`/`PatGlide`/`PatSetLength`/`PatInstrumentChange`/
  `PatWaveAdjust`/`PatFilterSet`/`PatEnd`. Need an FC-specific
  encoder. Per CORE TENET the emitted byte format can be more
  compact than orig's as long as the writelog matches.

- **Sequence streams** (~150 bytes × 3 voices/tune). USF already has
  `Sequence.commands` — `SeqPatternJump`/`SeqRepeats`/`SeqVoiceinc`/
  `SeqTranspose`/`SeqEnd`/`SeqWrap`. Encoder walks the structured
  commands → FC seq byte stream.

- **`pattern_ptr_table`** (max_patterns × 2 bytes). After patterns
  emit with known sizes/offsets, the pointer pairs fall out.

### Aux tables (effect program data, currently verbatim)

- **`drumtabel`** (4 bytes/drum × N drums = 2 pointers per drum →
  drum_wave + drum_tone byte streams). USF schema needs a `Drum`
  dataclass + `Instrument.drum_id` ref. Extract reads orig's drum
  tables; emit walks USF drums.

- **`filterbytes`** (4 progs × 10 bytes). Filter-program data:
  cutoff sequence + thresholds + flags. Current
  `FilterProgConfig.program: int` is just a selector — the actual
  bytes live verbatim in orig. New `FilterProgram` dataclass
  decomposing the 10 bytes into musical fields.

- **`arplo`/`arphi`** (per-inst arp ptr tables + N arp programs).
  Each inst's arp program is a small byte stream. Existing
  `Instrument.arp: ArpConfig` partly covers this (offsets list);
  need full per-inst arp program emission.

- **`pulsetabel`** (4 progs × 8 bytes). Same shape as filterbytes:
  lo bound, hi bound, threshold/step pairs per program. New
  `PulseProgram` dataclass.

- **`vibtabwait`** (per-inst vibrato delay, 8-16 bytes). Extend
  `VibratoConfig` with `onset_delay: int`.

- **`wavearp`** (4 bytes constant, e.g. `$80 $10 $80 $10`). Engine
  constant or top-level FCConfig field.

- **`pulsearp`** (8 bytes constant). Same.

- **`startlen`/`starttabel`** (Cyb II noise_tick lookup, per-inst).
  Only relevant when `noise_tick_style='cyb2_table'`. Per-inst
  attack length + waveform program bytes.

### Engine code

Already partially emitted via the feature-driven asm composition
(`_emit_fx_*`, `_emit_nextvoice_writes`, `_emit_playirq_dispatch`,
etc.). Remaining verbatim engine bytes can be lifted incrementally —
already the explicit plan per session 1 docstring at the top of
`composer_asm.py`.

### Filler regions between sections

Audit pass: which inter-section bytes are dead (emit zero) vs. live
(part of a section we haven't classified). Cleanup at end.

## Sequencing

Each phase must keep Hawkeye + Cybernoid II byte-exact through. Run
`verify_featuredriven(HAWKEYE)` and `verify_featuredriven(CYBERNOID_II)`
between every commit. Wire `tools/regression.py` as the gate.

### Phase 1 — Patterns + pattern_ptr_table

The big musical-content shift. The pattern encoder is the highest-risk
piece (Hubbard's bitpack codec was several rewrites).

- Schema: nothing — USF already carries `Pattern.events`
- Encoder: walk events → FC command byte stream
- Pattern pool: dense slot allocation (analogous to Hubbard's
  `_pattern_pool`)
- pattern_ptr_table: lo/hi pairs from emitted offsets
- Verify: Hawkeye + Cyb II byte-exact (or writelog-exact if we
  diverge from orig's byte layout per CORE TENET)

Estimated: 3 sessions.

### Phase 2 — Sequences

- Encoder: walk `Sequence.commands` → FC seq byte stream
- Multiple voices share one sequence pool
- Verify: still byte/writelog-exact

Estimated: 1 session.

### Phase 3 — Aux tables, one family at a time

3a. **`arplo`/`arphi`** — closest to existing schema (uses `ArpConfig`).
    Schema additions minimal. ~1 session.

3b. **`pulsetabel` + `PulseProgram`** — new dataclass + decomposition.
    Apply schema discipline (`feedback_schema_addition_discipline`):
    decompose the 8 bytes into musical fields (lo bound, hi bound,
    thresholds, steps), not as opaque bytes. ~1 session.

3c. **`filterbytes` + `FilterProgram`** — new dataclass + decomposition.
    Same schema discipline. ~1 session.

3d. **`vibtabwait`** — single field on `VibratoConfig`. ~0.5 session.

### Phase 4 — Drum programs

`drumtabel` + per-drum wave/tone byte streams. New `Drum` dataclass.
Drum format is variable-length, more complex than the other aux
tables. ~2 sessions.

### Phase 5 — Engine constants

`wavearp` + `pulsearp`. If they're truly engine-constant across all
FC SIDs, emit from FCConfig. If they vary per SID, treat as USF
content. Decide once we have data from multiple canaries.

~1 session.

### Phase 6 — Cyb II-specific (startlen/starttabel)

Only if/when we want to extend Cyb II coverage. Defer.

### Phase 7 — Engine-code cleanup

Lift remaining verbatim engine bytes into feature-driven emitters
(the unfinished plan from `composer_asm.py` session 1 docstring).

~2-3 sessions.

### Phase 8 — Compose-without-orig validation

The actual §9 completeness test. Build a SID from a USF whose orig
HVSC binary is NOT available (e.g., delete the path, or use a
synthetic test USF). Assert the rebuild plays correctly via
`sidplayfp` ear test + writelog comparison against a captured
reference.

~1 session.

## Honest total estimate

**~13–18 sessions of focused work.** Comparable in scope to Hubbard's
principled-instrument refactor (which is on record as multi-month).

LOC delta: ~2000–3000 lines new emit/extract code, ~150–300 lines
USF schema additions, deletion of ~500 lines of verbatim emission +
`_emit_verbatim_region` paths.

## Risks the scope hides

1. **Pattern encoder is the hardest piece.** Hubbard's bitpack
   codec was rewritten multiple times. FC's command-byte format
   appears simpler but the discipline (each event → exact byte
   sequence) is the same.

2. **Aux table decomposition discipline.** Per
   `feedback_schema_addition_discipline`: exhaust derivation /
   `engine_constants` / existing-params alternatives before adding
   a `bytes`-typed field. `PulseProgram` and `FilterProgram` need
   musical-field decomposition, not opaque byte arrays.

3. **`featuredriven_addr_shift` becomes dynamic.** Hawkeye's
   address-shift trick assumes predictable byte counts for the
   verbatim regions. Once patterns and sequences are emitted from
   USF, the byte counts can change. Either the shift logic
   becomes data-size-aware, or the rebuild commits to a fixed
   memory layout where data tables go after engine code at
   computed offsets. CORE TENET permits the latter.

4. **`pattern_stream_verify.py`** becomes the primary debugging
   tool — it's the "did the round-trip preserve bytes" check, and
   the divergence localiser will be needed every phase.

5. **More SIDs may surface gaps.** Adrenalin exposed this gap.
   Picking ONE more multi-subtune non-Tel FC SID besides
   Adrenalin (e.g., Eliminator or Tomcat from the archived `canary_picker`
   row 4 or row 5) before declaring "done" would reduce the risk
   of re-discovery.

## What this displaces / unlocks

**Displaces:** Adrenalin canary work (#79). Adrenalin is the forcing
function but can't be cleanly migrated until the FC composer is
principled.

**Unlocks:**
- Adrenalin "just works" as a Phase 8 validation target.
- Model-generated USFs can produce FC-family SIDs (the actual ML
  output goal).
- `tools/regression.py FC: 14 ok` becomes a true principled-rebuild
  signal instead of a verbatim-copy tautology.
- The composer unification trigger in `docs/refactor_1_remaining.md`
  (2+ large engine families migrated principled) advances — FC family
  becomes a real second principled family alongside Hubbard '85.

## Why we're doing this now vs. deferring

Per the principle doc §10: parameter sets are provisional and grow
with new engines. The FC verbatim shortcut was acceptable while only
the engine code was being migrated chunk-by-chunk (Sessions 1-7 of
`composer_asm.py`). It is not acceptable as a final state — and
trying to add Adrenalin via the same shortcut is what surfaced it
empirically.

The protocol gap (this not being caught earlier) is captured in
`feedback_check_existing_engine_docs.md` and the related discipline
memories. Adding a verification step to those — "before declaring a
family principled, check that the composer doesn't read orig at
compose time" — should prevent the same gap reopening in future
engine families.
