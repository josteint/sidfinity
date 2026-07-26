# Verification plan: did the py65→siddump initiative perturb anything?

**Status:** proposed 2026-07-26. A skeptic's exhaustive audit of the
"native-capture" initiative (migrating DMC extraction observers off py65 onto
`siddump`). The claim under test — *"net +63 FULL, no regressions caused by the
initiative"* — was measured against a **stale, conflated baseline** and by a
**recompiled verdict engine**. Neither is airtight. This plan replaces the
hand-wave with four independently-falsifiable questions. Time cost is not a
constraint (owner's instruction: spend whatever it takes).

## Why the earlier "+63" is NOT trustworthy (the two holes)

1. **Conflated variable.** The "+63" diffed HEAD against `tmp/dmc_f1_qc.jsonl`
   (Jul-23). Between Jul-23 and HEAD, TWO things landed: (a) this initiative,
   and (b) the **r113–r119 DMC grind cluster** (a large batch of unrelated
   C19/C29/C24/C31/C34 fixes). The +63 is their SUM. The initiative's own
   effect was never isolated.
2. **Moved ruler.** The verdict (FULL/PARTIAL) is a `siddump --writelog`
   comparison. The initiative **recompiled `siddump`/libsidplayfp** (new
   overlay taps). If those C++ changes are not perfectly observe-only, the
   writelog itself shifted — and every verdict, before and after, is measured
   against a different ruler. This was asserted (C36 "observe-only") but never
   proven by a broad byte-identity test.

## The commit anchors (durable — git, not tmp)

- **BEFORE** (pre-initiative code, includes r119): `c2790604` (Phase-0 doc; its
  code == `003974a5`). The first initiative CODE change is `4b6e3c45` (Phase 1).
- **AFTER**: current HEAD (initiative complete).
- **C++/verdict-engine touched in exactly 3 commits**: `4b6e3c45` (Phase 1,
  `--reinit-snapshot`), `1fd9286d` (Phase 2a, `--pc-watch` + overlay taps +
  `mos6510.h` getters), `0782c000` (C36, `c64cpu.h`). Everything else is Python
  extraction code or docs.
- **Python extraction touched**: `pipelines/dmc/v4/factory.py` (2b, 2e),
  `pipelines/dmc/v4/compilation.py` (2a), `pipelines/dmc/v4/extract/engine_model.py`
  (2c — reverted), `pipelines/music_assembler/heterogeneous.py` (guard-rail only).
- **`tmp/` is gitignored and may be wiped** (host history: `~/.local` wiped
  twice). Do NOT depend on tmp artifacts — REGENERATE from git + code. The only
  thing lost on a wipe is the Jul-23 baseline (`dmc_f1_qc.jsonl`), which is
  needed ONLY for the secondary r-cluster decomposition (Q2 does not need it).

## The four questions (each falsifiable; answer all)

### Q1 — Did the verdict engine (`siddump --writelog`) shift? (the ruler test)
This is the FOUNDATION; if it fails, every other comparison is invalid.

- Build `siddump` at BEFORE (`c2790604`) and at AFTER (HEAD) — two binaries.
  (Use a git worktree for BEFORE; see "Worktree setup" below.)
- On **every one of the 5401 f1 members** (and, to be maximal, every stored
  rebuild `.sid` too), run BOTH binaries with **`--writelog`** AND
  **`--writelog-per-irq`** (both are verdict inputs; the DMC CIA verdict uses
  per-irq, and the C36 commit `0782c000` touched the per-irq play-entry cycle
  code, so it MUST be included). Full songlength × 1.1.
- **Success = byte-identical** output, before vs after, for every member, both
  modes. This proves the C++ changes are provably observe-only and the ruler is
  fixed — so any verdict comparison downstream is valid.
- **If ANY member differs**: the ruler moved. Enumerate exactly which members /
  which `(cycle,reg,val)` writes differ, and for each ask "could this flip a
  FULL↔PARTIAL verdict?" (a difference only in a `--writelog` cycle timestamp
  within a frame is Trap-B-inert; a difference in the `(reg,val)` sequence is
  not). Quantify the blast radius. This is a real possible finding — do not
  assume it passes.
- Logically, `--writelog` is deterministic per input SID, so byte-identity on
  the ORIGINALS already proves the ruler is fixed for rebuilds too; running the
  rebuilds as well is cheap insurance.

### Q2 — The initiative's TRUE net verdict effect (isolate from the r-cluster)
A controlled A/B **at the commit boundary**, same ruler both sides.

- In a worktree at BEFORE (`c2790604`): build+verify all 5401 f1 members →
  `V_before`. (This code uses the py65 observers; it calls `siddump` only for
  the `--writelog` verify.)
- At AFTER (HEAD): build+verify all 5401 → `V_after` (a fresh run; do NOT reuse
  the possibly-stale `tmp/dmc_f1_fullbatch_verify.jsonl` — regenerate it).
- **Use the SAME siddump binary for the VERIFY on both sides** (valid iff Q1
  passes). The extraction differs (py65 vs siddump) — that IS the variable — but
  the RULER must be one fixed binary. Use the AFTER binary for both verifies.
- Diff `V_before` vs `V_after`. This is the initiative's isolated effect:
  `{FULL→PARTIAL}` = **initiative-caused regressions** (the number that matters),
  `{PARTIAL→FULL}` = **initiative gains**. r119 is in BOTH sides, so it cancels.
- **Success criterion for "did not perturb in the wrong direction":**
  `{FULL→PARTIAL}` is **empty** (or every member in it is understood and
  accepted). The honest headline becomes "the initiative's net effect is
  +G/−R", replacing the meaningless "+63 vs Jul-23".
- Secondary (needs the Jul-23 baseline if it survived): diff `V_before` vs
  `dmc_f1_qc.jsonl` to quantify the **r-cluster's** separate effect, so the
  total "+63" is fully decomposed into initiative + r-cluster + baseline-drift.

### Q3 — Are the FULL verdicts TRUE? (did the initiative introduce FALSE FULLs?)
The sharpest fear: the changes made the verdict LENIENT, inflating FULLs that
don't truly match. Operationalize the confusion matrix by **multi-method
agreement** (independent verdict paths must concur; disagreement = a suspect).

- Confusion matrix, per member, for BOTH BEFORE and AFTER:
  - **TP** = declared FULL and every independent method agrees.
  - **FP** = declared FULL but some independent method says PARTIAL (a FALSE
    FULL — the dangerous class).
  - **TN** = declared PARTIAL and methods agree it doesn't match.
  - **FN** = declared PARTIAL but every method says it matches (pessimistic
    artifact).
- Independent methods to require agreement across: (1) flat `--writelog`
  compare, (2) `--writelog-per-irq` compare, (3) the trichotomy compare
  (`compare_instruction_stream(mode='trichotomy')`), (4) a **2× songlength**
  capture (catches a late divergence the standard ×1.1 window misses), and (5)
  the OWNER'S EAR on a sample (the final arbiter per `feedback_ground_truth` —
  play a handful of "new FULL" members in real `sidplayfp`).
- Scope: apply to every member FULL at AFTER that (a) CHANGED verdict in Q2, (b)
  is one of the 4 named regressions, (c) is one of the 67 Jul-23 gains, plus (d)
  a stratified random sample of stable-FULLs (e.g. 200) for a baseline FP rate.
- **The decisive number: ΔFP = FP_after − FP_before must be ≤ 0.** If the
  initiative introduced even one false FULL, ΔFP > 0 and the +count is
  partly fictitious. This is the crux of the owner's skepticism.

### Q4 — Was the carrier enumeration complete? (the meta-risk)
Every earlier "the initiative can't have touched member X" claim rested on MY
carrier enumeration (writes-with-P, compilations, shape-B, canon-wrapper). Q2's
commit-boundary A/B is the INDEPENDENT check:

- The set of members that change verdict in Q2 MUST be a subset of the union of
  the carrier sets (regenerate them; do not trust tmp): 2e writes-with-P +
  inverse, 2a compilations, phase-1 shape-B, 2b canon-JT play-wrapper.
- **If any Q2-changed member is OUTSIDE those sets → the enumeration was
  incomplete** (the initiative touched a path I didn't identify). Investigate
  each such member: which changed observer ran, and why the census missed it.
- Regeneration entry points (re-derive, don't reuse tmp):
  - writes-with-P / inverse: re-run the 2e census (`_observe_play_phases_writes`
    vs `_observe_play_phases_pctrace` over all f1 members).
  - compilations: `compilation.detect_compilation` over all f1.
  - shape-B: the `_track_ff_reinit_ghost_probe` static scan (r118 census).
  - canon-wrapper: canon-JT members with `play != base+3`.

## Worktree setup (mandatory — never `git stash` in the main tree)

Per `feedback_old_code_compare_worktree`: use a worktree for BEFORE, never a
stash. The gitignored build deps are NOT in a fresh worktree — symlink them:

```
git worktree add ../sf_before c2790604
cd ../sf_before
ln -s <main>/hvsc84 hvsc84
ln -s <main>/tools/c64roms tools/c64roms
ln -s <main>/.pylocal .pylocal
ln -s <main>/tools/xa65 tools/xa65
# build BEFORE's siddump HERE (for Q1); for Q2 verify, use ONE binary (Q1-proven identical)
bash tools/build.sh
```

Clean up with `git worktree remove` when done (the worktree agents-must-commit
rule does not apply — this is read-only measurement, commit nothing in it).

## Deliverable

A short report stating, with evidence:
1. **Q1 verdict**: ruler fixed (byte-identical) — yes/no, and if no, the blast
   radius + whether it can flip any verdict.
2. **Q2 verdict**: the initiative's isolated effect `+G / −R`, with every
   `FULL→PARTIAL` member named and root-caused; and the r-cluster's separate
   effect (decomposing the +63).
3. **Q3 verdict**: the BEFORE/AFTER confusion matrices and **ΔFP** — the count
   of false FULLs the initiative introduced (must be 0), with the ear-check
   sample result.
4. **Q4 verdict**: every Q2-changed member is inside the enumerated carriers
   (yes/no); if no, the missed members explained.

Only if Q1 = fixed, Q2 `−R` = 0 (or all understood), Q3 `ΔFP` ≤ 0, and Q4 =
complete, is "+63 real and the initiative caused no wrong-direction
perturbation" PROVEN rather than asserted.

## Notes / traps for the executor
- Read `feedback_ground_truth.md`, `feedback_verification_modes.md` (Traps
  A/B/C), and ledger C20 (stale-FULL palimpsest) FIRST — the verdict has known
  ways to lie, and this audit exists precisely to catch them.
- Trap C: a raw `--writelog` "diverge at position 0" on a CIA member is a
  frame-bucketing artifact, not a real divergence — always cross-check with
  per-irq (`divergence_triage` already does this; reuse it).
- Do NOT let the batch's own `code_hash` gate reuse rows across the commit
  boundary — the two code states have different hashes, so a fresh `--out` file
  per side avoids contamination.
- The batch tool: `tools/dmc_family_batch.py --members <f1 list> --out <file>`
  (crash-safe/resumable). ~5 h/side on the X230, ~20 min on the EPYC.
