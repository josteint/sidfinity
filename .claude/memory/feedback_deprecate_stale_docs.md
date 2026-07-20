---
name: feedback_deprecate_stale_docs
description: "User preference: a docs/ file that no longer holds live relevant info gets DEPRECATED (git mv to deprecated/old_docs/ + dated banner), not left in docs/ with an in-place supersession banner."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2fd17f14-4e33-43c7-81e5-9dcd7bcbca9a
---

When a document in `docs/` has been overtaken — its plan executed, its method
superseded by a ledger entry, or its content now held better in a
`project_<engine>` memory or in code — the user prefers it be **deprecated**
(physically moved to `deprecated/old_docs/`), NOT left in `docs/` with a
supersession banner on top. The in-place banner is the weaker disposition; the
move is the default.

**Why:** a stale doc left in `docs/` still reads as a live plan on a directory
scan — the reader has to open it and notice the banner. Moving it out makes its
non-live status unambiguous by LOCATION, so a stale proposal can't be mistaken
for pending work. It's the CLAUDE.md "Archive on resolve" memory rule applied to
docs. **Deprecate, never DELETE:** the user browses `deprecated/` from time to
time to see whether an old idea fits a new situation, so the file's residual
value is preserved by the move itself — the archived doc IS the idea library.
(A recurring source of these: the project's early "throw math at it and see what
happens" explorations — decomposers, Z3/SMT, exact-learning/automata machinery —
little of which stuck; e.g. the 2026-07-20 off-table cluster.)

**How to apply:** the test is "does every live fact in it already live elsewhere
(a memory, a ledger entry, code)?" — if yes, deprecate. Repo convention:
`git mv docs/X.md deprecated/old_docs/X.md`; add a dated supersession banner at
the top of the moved file (what superseded it + why kept); add a line to
`deprecated/old_docs/README.md`; repoint any inbound references; run
`python3 tools/memory_lint.py` to catch dead links. Precedents:
`canary_picker.md`, `usf_digi_plan.md`, `principled_fc_composer_plan.md`.
Related: [[feedback_knowledge_placement]].
