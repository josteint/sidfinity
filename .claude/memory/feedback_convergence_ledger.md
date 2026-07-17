---
name: feedback_convergence_ledger
description: "TRIPWIRE before implementing ANY non-trivial solution: check the in-context Convergence Ledger for a matching entry first; record every solution after. The weak link is checking BEFORE solving — when deep in a problem I just solve it and skip the check."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 61079d2b-5be1-445b-9baa-b2959d4e0ea3
---

The Convergence Ledger's RECOGNITION layer (`docs/the_convergence_ledger.md`:
index + per-entry signature cards) is imported at session start (CLAUDE.md
canon block; two-layer split 2026-07-18, benchmark-validated — full entries
live in `docs/ledger/C<n>.md` and MUST be read before applying a solution).
Its "How to use it" section — CONSULT / RECORD / CANONICALIZE, the placement
rule, the entry schema — is therefore already in context; this memory does
not restate it. This memory holds only the failure diagnosis the ledger
doesn't:

**Why this is a TRIPWIRE:** the discipline is loaded every session, but the
*check-BEFORE-solving* step is the one I skip — when I'm deep in a problem I
just solve it (an off-table fix was once re-derived 3× across
filter/pulse/wave; DMC v4 `PwmConfig` vs v5 `SweepEnvelope` is the same DOF
solved twice). Recording-after and the `/uready-review` sweep are reliable;
the before-check is not. The in-context recognition cards exist precisely to
attack this (a known class should be RECOGNIZED from in-context signatures,
not depend on my deciding to look something up — you can't look up what you
don't recognize) — but recognition must still be ACTIVE: before writing an
approach, deliberately ask "does the ledger have this class?" rather than
trusting passive recall. And a card match is only the first half: READ the
full `docs/ledger/C<n>.md` entry before applying — cards are recognition
surface, not application detail.

**The tell that I'm drifting:** I'm partway through implementing a solution to
a non-trivial problem and I never asked the ledger question — I went straight
from "diagnosed" to "coding the fix." When I notice that tell, I've already
failed the check; stop and run it before continuing.

Related: [[feedback_reanchor_at_decisions]] (the sibling decision-time
tripwire), [[feedback_knowledge_placement]] (where entry content vs occurrence
detail lives), [[feedback_uready_vocabulary]] (uready criterion 5 =
cross-engine reuse; the `/uready-review` skill is the ledger's periodic
maintainer + backstop).
