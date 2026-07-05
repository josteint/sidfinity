---
name: amend
description: Handle the situation where fixing a member's FIRST DIVERGENCE regresses other members. Lenses to EXPLORE (options, not presumed causes) — (1) maybe a suboptimal PAST fix (a blanket model) is the real defect, fixable by an overarching change that serves both — or maybe your new fix is just wrong; (2) maybe the divergence is an editorial artifact the composer intended, worth keeping as musical content (precedent: the kept transpose command) — or maybe not; plus the firm rule (3) always score by the first divergence, not by making the SID FULL. Read the guiding docs as adversarial checks first. Use when a fix causes regressions, or PROACTIVELY before landing any shared-composer/extract change that could.
argument-hint: "[member.sid or engine + the first-divergence you're fixing]"
user-invocable: true
allowed-tools: Bash Read Write Edit Glob Grep Agent
effort: high
---

# amend — fix a first divergence without trading it for regressions

You reached here because you are (or are about to be) in **this exact
situation**: you localised a member's first `(reg,val)` divergence, you have a
fix, and it **regresses other members** — or you can see it might. `amend` is
the discipline for turning that apparent conflict into a correct, regression-safe,
more-elegant fix. It has been proven twice on DMC family-1: round-23 (otrk
arrangement, commits `9c0c33e`/`9e8f5ea`) and round-24 (note-start arm, ledger
**C23**, commit `1a632fe`).

**The one-line thesis:** a regression is a signal to *investigate the model*,
not proof that your new fix is wrong. It might be — but there are several
possibilities to explore, and picking one side prematurely is the mistake. The
possibilities, roughly:
- your new fix is genuinely wrong (the ordinary case — check it honestly first);
- a **past** fix was a suboptimal / blanket model that those members passed
  through, and an **overarching** fix serves both (the case `amend` exists to
  make sure you *consider* — it's easy to miss because it doesn't feel like your
  bug);
- the two classes genuinely differ and the model is missing a **discriminator**
  (Step 3);
- the "regression" isn't real — a stale-FULL palimpsest or a flake (C20, Step 3).

`amend` is the discipline for **exploring these before committing to one**, and
for reaching for the overarching-fix option when the easy move is to just exclude
the regressors.

---

## STEP 0 — read the guiding documents, as adversarial checks

Do this BEFORE designing the fix. Read them to try to **overturn** your easy
choice, not to defend it (the drift-tell is citing a doc to justify what you
already want — see [[feedback_reanchor_at_decisions]]).

- **CORE TENET** (`CLAUDE.md`, top): the verdict is the `$D400-$D418` write-log
  stream; the composer is FREE to invent any runtime. So you never reproduce the
  orig's *mechanism* (SMC, wrapper bytes, dispatch) — you reproduce the *writes*.
  When stuck on "the disasm forces X", re-state the problem as "what writes does
  this produce this frame" and restructure to emit that stream.
- **USF representation principle** (`docs/usf_representation_principle.md`) IN
  FULL, esp. §7 (forbidden shape: an engine-library index) and §8 (the composer
  twin: one engine-blind composer, never a per-member/per-engine emitter selected
  by content sniffing). Your overarching fix must live inside this.
- **The trichotomy** (`docs/sid_init_report.md`): reset (universal) / priming
  (typed USF) / environment (`playback_rate_hz` / CIA) / bookkeeping (not USF).
  Many "regressions" are really an *environment* difference (multispeed / play
  rate) masquerading as a musical bug — rule that out first ([[feedback_init_trichotomy]]).
- **The convergence ledger** (`docs/convergence_ledger.md`): **CONSULT its Index
  by problem-class.** If an entry already names your situation, use its canonical
  form instead of inventing variant #N. Sibling entries worth knowing here:
  **C16** (per-frame write-ORDER — parametrize emission, don't rewrite),
  **C18** (play-phase observation — observe entry-points, don't parse),
  **C20** (stale-FULL palimpsest — a "regression" that the CURRENT code never
  produced), **C22** (ambiguous encoding — two ops render identically),
  **C23** (a token hiding a per-member behavioural ambiguity — this skill's own
  worked example). See also [[feedback_convergence_ledger]].

---

## STEP 1 — localise the first divergence on GROUND TRUTH

Never design from a prior task description or a py65 trace — both go stale.

- `tools/find_first_divergence.py ORIG.sid REBUILD.sid --subtune N` — the first
  `(reg,val)` mismatch + the voice/role. For CIA/multispeed members use the
  per-IRQ view (`--writelog-per-irq` / `writelog_per_irq_capture`).
- Then get the orig's ACTUAL behaviour at that write: the annotated
  `disassembly.s`, and `tools/effect_chain_profiler.py` / `siddump --pc-trace`
  to attribute each write to its store PC. Ground truth resolves what write
  traces alone cannot (round-24: the pc-trace proved the note-init routine ran
  one *play()-call* later than the composer emitted it).
- Full recipe: [[feedback_writelog_divergence_recipe]]. Ground-truth rule:
  [[feedback_ground_truth]] (only `sidplayfp` writelog is authoritative).

---

## STEP 2 — three lenses

**Lenses 1 and 2 are options to *explore*, not conclusions to assume** — try
them alongside the ordinary check that your new fix is simply wrong; neither is
the presumed answer, and the value is in *considering* them, because the easy
path (exclude the regressors, or accept a conflict) skips them. **Lens 3 is a
scoring rule that always applies.**

### Lens 1 — could a PAST fix be the culprit, not your new one?
This is an option to *explore*, not a default diagnosis. Ask: **how were those
members FULL before?** One possibility worth checking: a *blanket* model — one
behaviour applied to every member — that happened to be right for them and wrong
for your target. **If** that's what you find, the blanket model is the real
defect and your fix merely exposed it; then don't pick one behaviour or bolt on
a heuristic to exclude the regressors — look for the **overarching** fix that
makes the model *complete* so it serves both. (Equally, you may find your new
fix was wrong, or the classes genuinely differ — Step 3. Explore, then decide.)
Two times this option paid off:

- **Round-23 otrk:** the `otrk_legacy` positional *approximation* (round-9,
  `val=i+1`) made a cluster FULL; the exact fix regressed them. Root: the
  approximation was suboptimal. Overarching fix: reproduce the composer's
  transpose-command *placement* as arrangement (§8 musical content) → the exact
  offset derives, and BOTH the new members and the ex-`legacy` cluster went FULL.
- **Round-24 note-start:** C18's F phase was modelled with ONE behaviour
  (`voice_fx → frame_entry`). Correct for the majority, wrong for a deferring
  class. The blanket model was the defect. Overarching fix: **observe** each
  member's actual F behaviour → both classes correct. (ledger C23.)

### Lens 2 — what did the SONG'S COMPOSER intend, in the editor?
Another lens to try (again, an option, not the answer): alongside "how do I
reproduce these bytes", also ask **"what did the musician do at the
tracker/editor, and what write stream did that produce?"** The audible character
(a redundant command, a note-start arm, a hard-restart quirk) *can be* a
deliberate or incidental editorial artifact that belongs in the reproduction as
musical content rather than a bug to fight — so it's worth checking before you
try to derive it away. Sometimes it is; sometimes it isn't.

Precedent (git `9c0c33e`, round-23): the composer left **redundant transpose
commands** (incl. transpose=0 re-assertions) in the orderlist; each one advanced
the `$1726` counter whose value the engine sonifies off-table. We **kept** them
(carried their placement as the voice's arrangement) instead of deriving them
away — that recovered the cluster. The lesson: an "extra" or "redundant" thing
in the original is frequently the composer's intent; capture it, don't erase it.
(Representation guardrail: it goes in USF as **named musical content**, never as
opaque engine bytes or a per-engine emitter — §7/§8.)

### Lens 3 — target the FIRST DIVERGENCE, not FULL  (a scoring rule, not an option)
Unlike Lenses 1–2, this one always applies. FULL is the wrong scoreboard for a
single fix. Score by: **is this first
divergence correctly resolved, with 0 regressions?** Two legitimate outcomes:
1. the member goes FULL, or
2. the first divergence moves **deeper** — a *different*, later blocker is now
   first. **That is progress** — you retired one blocker; the next is separate
   work. (Round-24: the note-start fix resolved the first divergence for all 13
   deferring members; only 4 went FULL, the other 9 exposed a freq-drift blocker
   — a clean, honest, forward step.)
Drop the "is it worth it / only N reach FULL" hedging ([[feedback_completeness_over_dominant_cause]]).

---

## STEP 3 — make the fix regression-safe BY CONSTRUCTION

The overarching fix usually needs a **discriminator**: what tells the target
class apart from the regressed class? Get it right mechanically, not by hope.

1. **Measure the candidate discriminator against BOTH sets — the fixed set AND
   the regressed set — before writing composer code.** If a candidate (schedule
   string, multispeed factor, a param) takes the **same value** on members that
   need **opposite** behaviour, it is NOT the discriminator (round-24: Words and
   F.A.K.E-Intro are both `P_F123` AND both 1.82 calls/frame, opposite
   behaviour). Then the distinction is a **per-member OBSERVABLE**, not a derived
   rule → observe it (C9/C18: measure, don't parse), ideally from a
   reloc-invariant write-footprint.
2. **Prefer a detection whose "changed" verdict has NO false positive.** Round-24:
   note-init ALWAYS carries AD/SR, so "deferred = first note-emit lacks AD/SR"
   cannot mis-fire on an immediate member → the majority is provably untouched.
   When you can arrange this, regression-safety is a theorem, not a hope.
3. **Census the FULL-side exposure BEFORE landing.** Enumerate every currently-
   FULL member the change touches and re-verify them → must be 0 regressions.
   (Round-24: all 56 F-token FULLs re-verified, 0 regressed.) A change to shared
   composer/extract code is only "safe" once its flip-set is measured, not argued.
4. **Re-baseline every apparent regression against a FRESH single-member build
   of the CURRENT code before believing it (C20).** A large fraction of "my fix
   regressed N FULLs" is stale-FULL palimpsests (the stored verdict predates the
   code) or parallel-batch siddump flakes — NOT real regressions. Verify the
   stored build first; attribute by USF-diff / param-bisect. This trap has eaten
   whole sessions; see [[project_dmc]] round-23 ⚠️.

---

## STEP 4 — verify, commit, RECORD

- **Verify:** first divergence resolved on the target (writelog match past the
  old point) **AND** 0 regressions on the FULL-side flip-set **AND** the standard
  regression gate for the touched scope (`tools/regression.py` for shared code;
  the engine's `verify_*` for engine-local changes — see CLAUDE.md "Regression
  scope by touched files"). Ear-test if dispatch/CIA changed ([[feedback_py65_misses_dispatch_bugs]]).
- **Commit** the code as one verified delta (no `Co-Authored-By`).
- **RECORD in the convergence ledger** on first sight (status `logged`), even for
  a 1× occurrence, so the next time is a lookup — and **canonicalize on the 2nd**
  ([[feedback_convergence_ledger]]). Update the engine's `project_<engine>`
  memory with the round + the residue now exposed.
- Optional closeout: if the fix could flip members beyond the one you targeted,
  re-verify the non-FULL set to harvest them (they're a lower bound), mass-write
  the new FULLs. But the *code* is the deliverable; coverage is derivable from a
  fresh batch.

---

## The loop, condensed

```
localise first divergence (ground truth: writelog per-IRQ + pc-trace + disasm)
  → read CORE TENET / principle / trichotomy / ledger as adversarial checks
  → hypothesise fix; if it regresses, EXPLORE (don't assume a cause):
      · is the new fix simply wrong?  (the ordinary case — check first)
      · lens 1: how were the regressors FULL before? — could a blanket/suboptimal
                PAST model be the real defect, fixable by an overarching change?
      · lens 2: what did the composer do in the editor? — is this an editorial
                artifact worth keeping as musical content? (sometimes yes, sometimes no)
      · measure the discriminator on fixed-set AND regressed-set
          → same value, opposite behaviour ⇒ per-member OBSERVABLE, not a rule
  → implement the overarching fix; make the "changed" verdict have no false positive
  → census the FULL-side flip-set; re-baseline any "regression" vs a FRESH build (C20)
  → verify (first-divergence resolved + 0 regressions + gate) → commit → ledger + memory
```

## Anti-patterns (each has cost real sessions)
- Accepting the regression as a fundamental conflict and picking one behaviour.
- Excluding the regressors with a heuristic that isn't the true discriminator
  (measure it on both sets first).
- Chasing FULL — a deeper first divergence is a win, not a failure.
- Believing a "regression" without a fresh single-member re-baseline (C20).
- Reproducing the orig's mechanism (SMC/wrapper/dispatch bytes) instead of its
  write stream (CORE TENET), or smuggling a per-member/per-engine emitter (§8).
