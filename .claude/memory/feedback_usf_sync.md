---
name: USF spec must stay in sync
description: When USF changes, update spec doc, all converters (X→USF and USF→SID), player, and tests
type: feedback
---

Whenever USF is modified (new fields, event types, tokens, or behavioral changes):

1. Update `src/usf.py` (dataclasses + tokenize/detokenize)
2. Update `docs/usf_spec.md` (the canonical spec)
3. Update ALL `*_to_usf.py` converters to emit the new data
4. Update `src/usf_to_sid.py` to consume the new data
5. Update `src/sidfinity_packer.py` if new assembly defines needed
6. Update `src/player/sidfinity_gt2.asm` if player needs new capabilities
7. Run GT2→USF→SID roundtrip test to verify no regression

**Why:** User explicitly requested this as a meta rule. USF is the central hub — if it drifts out of sync with converters, bugs are invisible until late.

**How to apply:** Before committing any USF change, grep for all files that import from `usf` and verify they handle the change. Check `docs/usf_spec.md` version history.
