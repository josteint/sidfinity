---
name: feedback_residue_claim_is_measured
description: "A 'hard boundary / residue / can't-reproduce / accept-it' verdict must be a MEASUREMENT proving unreachability from ground truth, never an inference. Five tells you're about to over-claim a boundary + the re-test-the-load-bearing-assumptions reflex. From DMC Verdict_01 (r164-166), where 'hard boundary' was mis-claimed 3x and each fell to one measurement (the last reached FULL)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b4c1234d-8f88-4730-bc1b-2ba0a9e91742
---

Declaring a divergence UNREACHABLE — "hard residue", "dynamic work-RAM", "our
representation can't express it", "accept it", "not worth it for a singleton" —
is a load-bearing verdict. It must be backed by a MEASUREMENT that PROVES
unreachability, never by an inference. In DMC Verdict_01 (r164-166) the same
"hard boundary" was declared THREE times and each time ONE ground-truth
measurement overturned it — the third correction reached FULL.

**Why:** the pull to be done biases you toward "hard boundary" — the mirror of
the chase-FULL bias the `amend` skill's Lens 3 fights. A give-up verdict feels
like humility but is usually an un-measured inference. And "not worth it" is a
SCHEDULING decision (fine to DEFER a singleton) — it is NEVER a reason to
CONCLUDE something is unfixable. Keep those two apart: defer without a proof,
never conclude-unreachable without one.

**How to apply — five tells you're about to over-claim, each with its measurement:**

1. **You're reasoning ABOUT the mechanism instead of MEASURING it.** If "it's
   hard" rests on a chain of reasoning from the disasm/prior analysis, that
   chain is the signal to go measure instead. Every Verdict_01 correction came
   from a fresh measurement, not more analysis.
2. **An unexplained value in your own model is a stop-and-resolve, not a
   footnote.** When your model can't account for a MEASURED value (glsp=$03
   "despite init clearing it" — actually a ghost unit's `INC` aliasing onto
   $1741), the model is wrong and the contradiction IS the disproof. Resolve it
   before you conclude anything.
3. **"Dynamic" is a measured TRAJECTORY, not an assumption.** Before "dynamic
   residue", plot the value over frames (`siddump --memwatch ADDR`). The
   Verdict_01 off-table target was called dynamic/cross-voice-coupled; one
   memwatch over 30 frames showed it flat.
4. **"Our representation can't express X" -> first grep the composer/USF for
   whether it ALREADY carries X.** The compacted slot-array composer "couldn't
   do a mid-11-byte-record read" — but already emitted `irawsp` (the raw record
   bytes). Read the code before declaring a representational wall.
5. **Prior-session artifacts go stale — re-derive load-bearing facts from the
   SOURCE, not the annotation.** A `disassembly.s` comment, a round-note, a
   memory claim can be wrong (Verdict_01: an annotated `flags[$0C]=$01` vs the
   file's actual `$00`, 30 s to check). Re-read the byte / the code.

**The re-test reflex — what "re-test every assumption" actually means:** NOT
re-test everything (too expensive). When a blocking conclusion (residue /
can't-fix / "that regressed N members") isn't landing, ENUMERATE the
load-bearing assumptions it rests on and re-derive EACH from ground truth.
Trigger: about to declare residue on inference, OR an unexplained value in your
model, OR the "singleton / not worth it" pull.

**Ground truth means libsidplayfp** — `siddump --writelog` / `--memwatch` /
`--pc-trace`, the file-image bytes, the composer source. ⚠ NEVER run py65 to
READ a value that depends on divergent or uninitialized memory (that read is
emulator-dependent — the third mode of [[feedback_ground_truth]]). py65 is for
extraction of file-loaded / provably-just-written values only, and any
py65-derived value that reaches the write stream is verified against siddump
before shipping. So every "measurement" a residue claim needs comes from
siddump / the artifacts, not py65.

Siblings that fire at DIFFERENT moments: [[feedback_measure_mechanism_before_precedent]]
(measure before matching a divergence to a precedent — during DIAGNOSIS);
[[feedback_completeness_over_dominant_cause]] (work every failure mode, drop the
worth-it hedging — during TRIAGE); this one fires at the GIVE-UP decision.
Technique corollary (recorded in ledger C19 from Verdict_01): a garbage-INDEXED
read of a STATIC table (freqtable via the C6 redirect; instrument records via a
reconstructed record image) is serviceable from the composer's OWN data — only
genuinely DYNAMIC work-RAM is the real hard boundary, and even that is a claim
you MEASURE (taint-classify the source, [[feedback_ground_truth]]), not infer.
