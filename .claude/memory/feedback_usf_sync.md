---
name: usf-spec-must-stay-in-sync
description: "When USF changes, update spec doc, all converters (X→USF and USF→SID), player, and tests"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4994dfd8-7bf7-414e-a073-16595cdd2a38
---

Whenever USF is modified (new fields, event types, or behavioral changes):

1. Update `src/usf/` (types.py dataclasses + grammar.lark + parser/writer)
2. Update `docs/usf_format.md` (the canonical spec)
3. Update ALL per-engine `extract/to_usf.py` writers to emit the new data
4. Update `pipelines/composer.py` (and any per-family composer that
   consumes the field) to consume the new data
5. Update the extract smoke tests (`pytest pipelines/`) where they
   touch the changed surface
6. Run full `tools/regression.py` — a USF change is shared plumbing

**Why:** User explicitly requested this as a meta rule. USF is the central hub — if it drifts out of sync with converters, bugs are invisible until late.

**How to apply:** Before committing any USF change, grep for all files that import from `usf` and verify they handle the change.

(Checklist rewritten 2026-07-16: the original listed the GT2-era files —
`src/usf.py`, `docs/usf_spec.md`, `src/usf_to_sid.py`, `sidfinity_packer.py`,
`sidfinity_gt2.asm` — all gone; the rule itself is unchanged.)
