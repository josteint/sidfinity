---
name: feedback_principle_first_analysis
description: "Run the representation-principle checklist BEFORE proposing any effect/instrument design. Don't wait for the user to catch slips."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Before proposing any effect/instrument/note-field design — and before
any "engine variant" / "engine-specific codegen" suggestion — answer
ALL of these. If I can't, the proposal isn't ready.

1. **What does the MODEL see?** Sketch the USF token sequence the
   model trains on. Does this proposal add a `*Kind`/index/engine-
   library-reference to that sequence?

2. **Which pole?** Locate the proposal on Pole A (thin reference →
   engine library) vs Pole B (raw program → unlearnable) vs the
   structured middle. Be specific. "Mostly Pole A" is the disease
   wearing a moderation badge.

3. **Rule 1 — cluster by behavior, not by code.** When proposing
   "same musical concept, different engine implementation": is the
   *audible/structural* behavior identical? If unknown, that's a
   research task before the design proposal. "Probably the same"
   is not the test. Use [[reference_audit_tool]]
   (`src/usf/audit.py`) for PC-traced per-voice writes when the
   frame-level writelog conflates voices.

4. **§8 test 3 (interpolation).** Name two real corpus instances of
   this effect and describe what averaging their parameters would
   produce. If the answer is "undefined" or "engine identity
   doesn't average," the parameterization has failed. If averaging
   gives a sensible intermediate, the basis is musical.

5. **§8 test 4 (cross-engine reuse).** Will the next engine's
   instances of this effect land in the same parameter space?
   Or will I need a new "kind" to handle the next engine? If yes
   to the latter, the basis is overfit and I'm building the leak.

6. **Posture declaration for the commit.** State explicitly:
   - This field is in USF data (must be parametric/musical), OR
   - This is in EngineConfig (mechanism — engine code config), OR
   - This is in the codegen ENGINE asm (mechanism — interpreter).
   Mixing these up is where the slips happen.

**Why:** I've slipped twice in one session — verbatim digi-player
bytes presented as "engine mechanism" without scrutiny, and
"engine-specific codegen" presented as fine when it's actually the
forbidden-shape `*Kind` wearing a disguise. The user caught both.
The cost of false-positive principle worries is small. The cost of
missing real drift is the entire ML goal of the refactor.

**How to apply:** Run this checklist BEFORE writing the proposal.
Not after. The slips happen because I'm goal-oriented short-term
("get HR working") and the principle requires explicit short-term
work to enforce against a long-term goal. If I can't answer all 6
above, the proposal IS the slip — pause and do the audit first.

Related: [[feedback_usf_representation_principle]] is the TRIPWIRE
that says "read the doc." This memory is the CHECKLIST that says
"run the doc's tests on this specific proposal, before proposing."
