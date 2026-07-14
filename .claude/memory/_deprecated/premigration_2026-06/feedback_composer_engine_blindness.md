---
name: feedback-composer-engine-blindness
description: "The USF representation principle binds the composer too, not just the schema. The composer is one universal engine; engine identification via USF content sniffing is the same disease as `vibratoKind: int` in schema, just hidden in Python."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 02f65b25-1c68-4ebb-b180-7ebbd9c37c55
---

The user has had to make this correction REPEATEDLY across sessions, including
to me directly. Stating the rule sharply so I do not narrow it again:

**USF → SID must be engine-blind.** The composer is one universal engine that
reads USF as the COMPLETE specification of the music. It must not identify the
originating engine (by content sniffing or any other means) and must not
dispatch to per-engine 6502 emitters. The musical content the composer needs
to produce correct audio must live in USF, available to the ML model. Anything
the composer "recovers" by recognising the USF's shape is musical knowledge
the model cannot see.

**Why:** the project's value as ML training data depends on USF being the
complete musical specification. If the composer needs to know "this is Hubbard"
to produce correct audio, then USF is incomplete and the composer is silently
supplying the missing information. The audible character of a Hubbard rebuild
then comes from `_emit_hubbard_fx_vibrato` / `_emit_hubbard_hr_writes` / etc. —
NOT from the USF, NOT from anything the model could learn.

**How to apply:**

- Before adding ANY engine-discriminator path to the composer (`_needs_X_path`,
  `is_companion = ...`, `if model.voice_timing.mode == ...`), stop. The
  discriminator + dispatch IS the leak. Same disease as a `vibratoKind: int`
  field in USF, just hidden one layer deeper in Python.
- "Feature-parametric dispatch" is a cover story when there is only one
  consumer of the feature combination. `_needs_hubbard85_path` returns True
  iff the USF has features that "currently" only Hubbard uses, and the True
  branch is "emit Hubbard's exact 6502 engine." That is engine identification
  + engine-library lookup, regardless of what the function's docstring claims.
- The principle doc (`docs/usf_representation_principle.md`) addresses USF
  schema fields only. The structural analog for the composer is NOT in the
  doc — but the user expects me to apply the principle's PURPOSE, not just
  its letter. The purpose is no leakage of original-engine identity into the
  rebuild path.
- When migrating a new engine and "we need engine X's exact bytes to match"
  comes up, the right answer is not "add a per-engine emitter path." The
  right answer is either (a) the USF carries the musical content that makes
  the rebuild correct, or (b) the universal composer grows a parametric
  feature that the USF then uses.

**Current state of the violation (as of 2026-06-03):** `pipelines/composer.py`
has `_needs_hubbard85_path` (line 3329) dispatching to `_emit_hubbard85_bytes`,
which calls `_compose_hubbard_engine_asm`, which composes 18 `_emit_hubbard_*`
routine emitters. There is also `is_companion` shape dispatch (line 5283). All
of this is the same disease.

**Past failure pattern (mine):** when challenged, I narrow the principle to
"the schema rule" and treat composer dispatch as out of scope. The user has
corrected this multiple times. The principle's purpose binds the composer; do
not narrow.

Related: [[feedback-usf-representation-principle]], [[feedback-principle-first-analysis]],
[[feedback-schema-addition-discipline]], [[project-composer-dissolution]] (the
phase-8 work that consolidated Hubbard emitters into composer.py — fixing the
dispatch leak is the NEXT structural cleanup, separate from that work).
