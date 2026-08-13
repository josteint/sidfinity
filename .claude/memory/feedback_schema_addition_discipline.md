---
name: feedback_schema_addition_discipline
description: "Don't add USF schema fields without re-reading the principle doc IN FULL and exhausting derivation/existing-params alternatives; and NEVER land a grammar/schema/typed-field change without OWNER approval first (2026-08-13 rule). `bytes`-typed schema fields are suspicious by default. Lessons: Companion's reverted `VoiceBlock.trailing`; the `direct` filter_mod marker landed solo (blessed after the fact, process fault)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
  modified: 2026-08-13T19:35:02.335Z
---

When a USF schema addition feels imminent, **stop and follow the
checklist below**. Adding the wrong field, even temporarily, costs
real time and leaves git-history cruft.

**Why:** During the Companion (Up, up & Away!) migration I added a
`VoiceBlock.trailing: bytes` field to round-trip the engine's
post-$8D byte stream. The user pushed back; on re-examination the
field violated docs/the_principle.md (opaque
byte blob, engine-flavoured shape on the schema). It got reverted.
The actual correct solution required **no schema change** —
adjacent codegen layout + 6 named integers in the existing
per-subtune `params { }` bag covered everything.

## The checklist — run BEFORE adding any schema field

1. **Re-read `docs/the_principle.md` IN FULL.** Not a
   skim, not the cached summary. Per docs/the_principle.md
   the doc is load-bearing precisely because the principle is easy
   to violate by drift.

2. **Is it derivable from data already in the USF?** Companion's
   post-$8D bytes turned out to be 95% derivable from adjacency to
   the next voice's orderlist or the per-subtune init template
   (both already in the USF). The codegen just had to lay subtune
   data out as `[V1 ord][V2 ord][V3 ord][template]`.

3. **Does it belong in `engine_constants`?** If the value is the
   same across every tune for this engine, it's engine mechanism,
   not USF data. Companion's 256-byte freq table is the canonical
   example — `pipelines/companion/engine_constants.py`, not in USF.

4. **Does it fit in the existing `params { }` bag?** Per-subtune
   `params` is an extensible key-value dict already holding
   engine-state knobs (gate_off_tick, vol_filter, init_pwm_ctr,
   speed_ctr_init, …). Adding 6 more keys for Companion's per-voice
   pad metadata was free — no schema change.

5. **Can it be expressed as named integers on a musical or
   well-known engine basis?** Per §4 of the principle: parameters,
   not kinds. `(count, byte)` per voice = 2 named ints per voice.
   That beats a `bytes` field every time.

6. **Only if all of (2)-(5) fail, propose the schema addition** —
   and then write the justification as if defending it to the
   principle doc before writing the code.

## THE OWNER-APPROVAL GATE (2026-08-13 — supersedes any impression that a well-defended change may land solo)

**No grammar change, no typed-field addition, no new representation
KIND lands without the owner approving it first — full stop.** Passing
the checklist above and the principle's four tests is the *argument to
bring the owner*, never a permission slip. This includes autonomous /
overnight sessions: park the change as a written proposal (options +
recommendation) and continue other work.

**Why:** On 2026-08-13 a session landed a `filter_mod` grammar marker
(`direct`) for a SOLE carrier plus two params keys homed inconsistently
with their typed sibling, all in one day, all gates green — and the
owner's reaction was "you create new grammar almost willy-nilly, gives
me a bad feeling." The audit found the representations defensible but
the PROCESS wrong: this project's canon (the Principle itself, the
4k_Byter reversal) was forged by the owner's adversarial pushback on
exactly such drafts; landing same-day removes that pushback from the
loop. The owner blessed `direct` after the fact and approved re-typing
the two keys (C33) — but ratification is theirs, not the gates'.

**How to apply — the green/red split:**
- GREEN (proceed solo): probes, params-key wedge knobs under existing
  C19 licensing (registered in tools/composer_params.json), extract
  fixes, per-subtune carriage a ledger entry has pre-decided, batches,
  gates.
- RED (propose first, never land): grammar.lark changes, src/usf
  typed-field additions, new blocks, new representation kinds, any
  enum growth on a typed field. When in doubt, it's red.
- HOMING RULE for green-path knobs: if a typed sibling of the same
  musical family exists (e.g. the init_behavior articulation block),
  say so in the proposal instead of quietly taking the params-bag
  shortcut — inconsistent homing was the second fault that day.

## Tripwires

- **`bytes`-typed schema fields are suspicious by default.** Raw
  bytes carry no musical structure for the model to learn. Force
  every such field to either become structured (named ints, enums
  on a musical basis) or move out of the schema (engine constants,
  existing params bag, derivable from layout).
- **A field that only one engine ever uses is a smell.** It says
  "the schema has this concept" when really only the engine has it.
- **Carry-over reflex from a prior step.** If you already
  implemented the byte-blob approach in codegen earlier, you'll
  reflexively reach for the byte-blob shape in USF. Stop and
  rederive from the principle.

## What to ask, in order

When the codegen needs a byte the USF doesn't seem to carry:

> "What minimum *named* integers does the codegen need to reproduce
> this, where each integer has a learnable musical or engine-state
> meaning?"

If the answer is "I just need these raw bytes," go back to question 2
above. Almost always something is derivable that you missed.

## Related

- docs/the_principle.md — the tripwire to read
  the principle in full before any effect/instrument design.
- [[feedback_principle_first_analysis]] — 6-question checklist for
  effect representation. This memory's checklist generalises it to
  any schema field.
- [[feedback_always_through_usf]] — the goal that makes USF schema
  hygiene matter (USF is the source of truth).
- [[project_companion]] — the project where this lesson was earned;
  see its "USF representation" section for the final design.
