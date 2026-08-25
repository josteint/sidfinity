---
name: feedback_relaxing_an_error_kills_its_guards
description: "Before making code stop raising, grep for who CATCHES that error — guards written as `except` around a call become dead code silently, with no test failing."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 75fd1220-dabb-4ad4-80b0-801b7846cac6
  modified: 2026-08-25T20:02:02.947Z
---

When you relax a function so it no longer raises, every guard implemented as
`except <ThatError>:` around a call to it becomes **dead code** — silently, with
no test failing anywhere. The guard does not report that it stopped firing; it
simply never runs again, and whatever it was protecting against flows straight
through.

**Why:** a `try/except` guard encodes its real condition *implicitly*, in
whatever made the callee raise. Nothing links the two. The callee's author sees
"this error is wrong, the data is fine" and removes it; the guard's author is
absent; no test covers "the guard fired", because guards fire on inputs nobody
wrote a test for. Type checkers, linters and the regression gate are all blind
to it — the code still compiles, still runs, and still returns plausible
results. This is the same family as ledger C20's palimpsest layers: the failure
is in the *invalidation* mechanism, not in the thing being computed.

Worked instance (DMC v5 sector/orderlist decode, 2026-08-25 — ledger C34's 5th
occurrence): two unrelated protections in one file were written as
`except RuntimeError:` around the decoder — "the PSID header overstates the song
count, drop phantom tune-table records" and "a compilation's unreferenced
sector-pointer tail holds un-relocated junk, keep an empty placeholder".
Correcting the decoder to match the player (it had been refusing bytes the
player accepts) killed both. Garbage tune-table records became real subtunes
(one member went from 12 sectors to 67, referencing index 246 against a
43-entry table), and junk tail sectors became real patterns that tripped an
unrelated refusal and took a **FULL member down**. Neither was visible by
reasoning about the change; both surfaced only from an old-vs-new byte
comparison across the family.

**How to apply:**

1. **Before** removing or narrowing a `raise`, grep the repo for handlers of
   that exception type reachable from the call — `except <Error>`, and bare
   `except` around the call site. Each one is a guard whose condition you are
   about to delete.
2. For every hit, ask what the guard was *really* testing. It is never "an
   exception happened"; it is a property of the data that happened to make the
   callee raise.
3. Re-express that property as a **positive condition** the relaxed code emits
   deliberately. In the worked instance the condition was "this stream never
   states an end", carried as a distinct `wrap` tag that downstream reads as an
   ordinary loop — so the guard tests a fact rather than an accident.
4. Gate the change by **differential comparison over a real population**, not by
   reasoning. Byte-identity old-vs-new across the family is what caught both
   guards here; a targeted test suite would not have.

Related: [[feedback_old_code_compare_worktree]] (how to run the old-vs-new
comparison), [[feedback_residue_claim_is_measured]] (the same "measure, don't
infer" reflex).
