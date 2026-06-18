---
name: feedback_convergence_ledger
description: "TRIPWIRE before implementing ANY non-trivial solution: consult docs/convergence_ledger.md for the canonical form first; record every solution after. The weak link is consulting BEFORE solving — when deep in a problem I just solve it and skip the lookup."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 61079d2b-5be1-445b-9baa-b2959d4e0ea3
---

There is a maintained **convergence ledger** at
[`docs/convergence_ledger.md`](../../docs/convergence_ledger.md): one entry per
recurring sub-problem → its canonical (idiomatic-for-us) solution, where the
shared code lives (or `factor-candidate`), and boundary conditions. It exists so
a new engine reuses the best technique instead of inventing variant #15, and so
[Move 1](../../docs/refactor_1_remaining.md) inherits a pre-decided convergence
map instead of an archaeology dig.

**Why this is a TRIPWIRE and not just a CLAUDE.md note:** the discipline is
loaded every session, but the *consult-BEFORE-solving* step is the one I skip —
when I'm deep in a problem I just solve it (today's off-table fix was re-derived
3× across filter/pulse/wave; DMC v4 `PwmConfig` vs v5 `SweepEnvelope` is the same
DOF solved twice). Recording-after and the `/uready-review` sweep are more
reliable than pausing to look first, so this tripwire targets the lookup.

**The discipline — three timings, do NOT conflate (see the ledger's "How to use"):**

1. **CONSULT — before choosing how to solve any non-trivial problem.** STOP and
   ask: *have we solved this class before?* Targeted lookup by problem-class in
   the ledger's Index (a few seconds, not a full read). If there's an entry, use
   its solution — call the shared code, or implement the recorded form. Ask this
   BEFORE writing the approach, not after.
2. **RECORD — log every solution on 1st sight** (status `logged`), even a 1×
   one. The recorded 1st occurrence is what makes the 2nd a lookup instead of a
   memory feat. Don't gate recording on recurrence.
3. **CANONICALIZE / FACTOR — on the 2nd occurrence** (≥2× → pick the one form,
   `factor-candidate`/`shared`). ≥2× gates ONLY this step. Code-factoring across
   engine families waits for Move 1 (the ledger is a record, not a refactor).

**The tell that I'm drifting:** I'm partway through implementing a solution to a
non-trivial problem and I never opened the ledger — I went straight from
"diagnosed" to "coding the fix." When I notice that tell, I've already failed the
consult; stop and run the lookup before continuing.

Related: [[feedback_reanchor_at_decisions]] (the sibling decision-time tripwire),
[[feedback_uready_vocabulary]] (uready criterion 5 = cross-engine reuse; the
`/uready-review` skill is the ledger's periodic maintainer + backstop).
