---
name: project-rayden-digi
description: "The Rayden_Digi family — status, structure and the decisions taken while migrating it (phase 3 of the digi parametrization)."
metadata: 
  node_type: memory
  type: project
  originSessionId: f1faf039-b5bd-478f-9b9a-c67ad2296f7a
  modified: 2026-08-31T20:12:20.834Z
---

Newest-first. **Read `pipelines/rayden_digi/RE_NOTES.md` first** — it holds
the player anatomy, the measurements and the per-item NEXT list; this file
holds status and the decisions.

## 2026-08-31 — extract built and gated; USF writer blocked on one decision

17 carriers, all `MUSICIANS/R/Rayden/`, all RSID `play=$0000` (ledger C40's
self-driven class). Phase 3 of `docs/digi_parametrization_proposal.md`.

**State.** `pipelines/rayden_digi/{extract.py, verify_score.py, to_usf.py}`.
The extract decodes the score, sample table and playback core;
`verify_score.py` predicts the whole `$D418` stream and checks it against
`siddump --writelog`, over each member's FULL songlength. Morbital,
Morbital_plus and Spelling_Around pass CONTENT and TIMING — 1,957,156 /
3,152,731 / 3,704,788 digi writes explained, residual p90 0.151% / 0.140% /
3.454%. Embarassed_Emotions passes CONTENT only: its dominant sample is a
1-byte constant and its IRQ inserts a per-frame idle write, so event
boundaries inside a silent run are not pinned down and `verify_score` says
so (`timing_ok`) rather than calling it a pass. No `.usf` is stored for any
member yet.

⚠ A 60 s capture reported all three as 100% clean while the single-pass
aligner actually lost them at 28-65% of the song. A partial capture of a
looping score does not look truncated — it looks CLEAN. The cure was a
two-pass alignment (fit the tick rate, then use it to place re-triggers
hidden inside constant runs), which costs the independence of the CONTENT
and TIMING checks; `run_resolved_onsets` reports how much a member leaned
on the prior.

**The V1/V2 split is not a build fact.** 13 of the 17 carriers — nine of
them sidid `Rayden_Digi_V1` — run the SAME sequencer; only the playback
CORE differs (vector-swapped zero-page NMI handlers vs the V1 core, plus a
raster burst that has exactly one carrier). Six V1 members now decode their
sequencer and refuse at the core with a precise message. This is the
measured backing for the RE_NOTES §8 guard: branch on the measured core,
never on the version string.

**Blocked, deliberately.** `SampleInstrument` has no loop point, and
Rayden's engine uses all three forms (loop-to-start / one-shot /
attack+sustain). `to_usf.py` refuses sustaining members rather than routing
the loop through `params` — a typed sibling exists, so per the owner gate it
is a written proposal: **backlog item 38**, recommendation
`SampleInstrument.loop_start`.

**Open question raised, not acted on.** The engine's rate table is a 12-TET
tuning table, so the digi voice is a pitched melodic channel. The landed
schema carries this as per-row `rate=$XXXX` latches, which is a genuine
parameter and needs no approval — but note + digi tuning table would put the
digi and SID voices in ONE parameter space (Principle §9 test 4). Parked in
RE_NOTES for the owner.

**Two general findings that outlived the family:**
- `--pc-watch` under-counts by ~10% on an interrupt-paced member (a fast NMI
  breaks C36's ascending-read execution signature) — recorded as C36's
  second gap. Never use it as a rate meter there.
- `digi_voice_block` skipped the orderlist-modifier normalisation
  `voice_block` does, so a CONSTRUCTED digi orderlist failed
  `parse(write(x)) == x`. Invisible to `usf_spec_lint`, whose round-trip
  starts from the parser's own output. Fixed in `src/usf/parser.py`.

Related: [[project_digi_organizer]] (phase 2, closed 39/39 — the parametric
digi emitter this family should reuse), [[feedback_ground_truth]] (the file
image lies about this player's core; every runtime value is measured).
