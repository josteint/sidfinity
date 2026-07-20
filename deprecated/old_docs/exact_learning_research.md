# Exact-learning frameworks for SID reproduction — research synthesis (2026-07-01)

> **📦 ARCHIVED 2026-07-20.** Moved out of `docs/` — a late instance of the
> project's early "throw math at it" mode; little of that math stuck. Its
> motivating premise (the off-table pulse "couples to hidden state", the
> combination-lock framing) was refuted the same day by the taint check in the
> sibling doc (`offtable_unified_transform.md`) — the source is 100% static, no
> hidden coupling. The one surviving idea (grey-box: read the binary just to
> NAME the coupling variable) shipped as `tools/taint_source.py`. Kept here for
> idea-mining if compact behavioral models (spectral WFA / register automata /
> CEGIS) are ever wanted for the ML representation itself.

> **STATUS 2026-07-19:** the immediate wall this research served (Jupiter41's
> off-table pulse) was closed the SAME DAY by a far simpler route (ledger
> C2/C8 — capture + truncate, no learning machinery). The grey-box thesis
> ("use the binary only to NAME the coupling variable") materialized as
> `tools/taint_source.py` and is now standard practice (ledger C2/C11).
> Keep as the Move-1-era reference for exact-learning approaches (spectral
> WFA / register-automata / CEGIS) if compact behavioral models are ever
> needed for the ML representation itself.


**Context.** The "reframe" investigation hit a wall: Jupiter41's off-table pulse is NOT a
deterministic function of its complete *local* state (`$1800` pulsepos + `$1830` counter +
`$182A/D` accumulator → still only 84–94% predictable), so it couples to hidden/external
state. Question: what does the math/CS literature offer for learning a **compact, EXACT**
generator of a deterministic integer sequence with **hidden/external state**, from observation?

**Method.** Deep-research run `wf_d87b53b2-72d`: 6 angles, 30 sources, 143 claims, 25
verified, **9 confirmed 3-0**, 2 killed, 14 left unverified when the session limit hit
(and auto-synthesis was skipped). The synthesis below is mine, grounded in the confirmed +
extracted claims + domain knowledge; confirmed claims are marked ✓, extracted-but-unverified ⚠.

## The convergent finding

**Our problem is exactly register-automaton / EFSM identification, and our specific wall is
the textbook "combination-lock" hidden-state case — which has a known answer: grey-box learning.**

Three legs, all confirmed:

1. ✓ **The model class is an exact fit.** Register automata = "extended finite-state
   machines with a finite control structure extended with registers, assignments, and
   guards, so behavior can depend on stored data values that a plain FSM cannot capture."
   The DMC pulse IS this: finite control (pulsepos phases) + data registers (accumulator,
   counter) + guards (PW thresholds) + arithmetic updates (`acc += add`). (Cassel/Howar/
   Jonsson/Steffen; Springer 10.1007/s00165-016-0355-5.)

2. ✓ **The hidden-state minimum is characterized.** There is a **Myhill–Nerode theorem for
   register automata** — a symbolic language is regular iff three equivalence relations
   (location `≡_l`, transition `≡_t`, register `≡_r`) have **finite index**; the framework
   "generalizes the classical Nerode congruence and canonical-automaton construction to the
   symbolic setting." So "how much state is needed for exact reproduction" is a *computable,
   canonical* quantity — my 84–94% just used a coarser partition than the Nerode-minimal one.
   (arXiv:2007.03540; Springer above.)

3. ✓ **Our wall = the combination-lock case, and grey-box cracks it.** "Grey-box
   register-automata learning enables RALib to learn models provably out of reach of
   black-box active learning, including **combination locks** — machines whose state is only
   distinguishable by an exact hidden input sequence." That is precisely our off-table
   coupling. ✓ And the reason black-box fails is also confirmed: "existing black-box tools …
   are restricted to register automata with only **equality/inequality guards** — they
   cannot natively model arithmetic/accumulator dynamics." (arXiv:2009.09975.)

**This validates the probe conclusion and gives it a formal home.** "Pure observation can't
classify the off-table pulse" is not a dead end — it's the known-hard black-box case, and
the literature's answer is **grey-box**: peek at the binary/RAM (which we already have) *just
enough* to identify the coupling register, then the exact-learning machinery applies. The
elegant path is the MIDDLE between "pure observe-and-fit" (proven to fail here) and
"reverse-engineer the whole mechanism" (the old pain): **use the mechanism minimally to name
the state variables, then represent the behavior as a minimal canonical automaton.**

## Per-framework verdict

| # | Framework | Exact? | Hidden state | Oracle-free? | For us |
|---|---|---|---|---|---|
| 1 | **Register-automaton / EFSM learning** (RALib/SL*, black- & grey-box) | ✓ canonical within RA class (given the right data theory) | ✓ registers ARE the hidden state; grey-box discovers coupling (combination locks) | active (needs queries) — but grey-box uses the binary | **TOP FIT**; black-box can't do arithmetic → lean grey-box |
| 2 | **Spectral / Hankel WFA** (multiplicity automata, Balle–Mohri) | ⚠ **EXACT lossless in the noise-free case** — SVD rank-factorization of a Hankel sub-block recovers the *minimal* WFA; Fliess/Carlyle–Paz gives the exact minimal-state characterization | ⚠ does NOT model hidden state explicitly — it's *recovered* implicitly by the rank | ✓ **passive, no oracle** | **Most elegant exact route**; needs field/ring care for modular byte arithmetic |
| 3 | **PSR / OOM** | ⚠ unified WITH WFA as "multiplicity automata" under one object | represents process by observable statistics, no explicit hidden state | ✓ passive | subsumed by #2 (spectral) — not a separate track |
| 4 | **Passive Moore/Mealy inference** (MooreMI, AALpy, FlexFringe, MINT) | ✓ **MooreMI exact in the identification-in-the-limit sense** (converges on a characteristic sample); ⚠ FlexFringe = *probabilistic* DFA, MINT = *generalized/approximate* | ⚠ MINT discovers data→control coupling via a per-label classifier (approximate); ⚠ AALpy can inject a discovered hidden variable as a custom **local compatibility criterion** forbidding bad merges | ✓ **matches our regime** (traces, no oracle) | good for **discovery**; exact only asymptotically |
| 5 | **CEGIS / SyGuS / SMT synthesis** | ✓ exact by construction | handled if you give it the coupling var (grey-box) | I/O examples | **we already have `z3_decompose`** — a working exact backend |
| 6 | **Smallest-grammar / SLP compression** (SEQUITUR, Re-Pair) | ✓ exact but | no state model — just sequence compression | ✓ | good for the *note-sequence* layer, not the modulation dynamics |
| 7 | **Koopman / subspace ID** (N4SID) | ✗ approximate for finite-state/modular; continuous-dynamics tool | — | — | **poor fit** — de-prioritize |

Killed (1-2 refuted): the "RA↔regular symbolic language is exactly bidirectional" over-claim,
and the "`≡_r` alone handles all hidden state" over-claim. Both are nuance-corrections, not fatal.

## Ranked shortlist — what to try, in order

1. **Grey-box register identification (then exact-learn).** Read the binary to name the
   off-table coupling register: what is `$23BC+pos` for the off-table `pos`, and is it
   static or written during play? This *is* the combination-lock answer and resolves our
   open (a)/(b) question. Once the coupling variable is named, the pulse becomes a
   well-defined EFSM. **Cheapest, highest-information, directly on the critical path.**
2. **Spectral WFA (Hankel-SVD) on the observed modulation stream.** Oracle-free, exact in
   our noise-free regime, yields the *minimal* representation — the most mathematically
   elegant and the most ML-friendly (a small matrix per instrument). Prototype on a clean
   in-table program first (where we know it's exact), then the off-table ones.
3. **SMT/CEGIS via the existing `z3_decompose`.** Exact by construction, native arithmetic
   (BitVec), can consume the grey-box coupling hint. We already have the tool — fastest to
   an exact result once #1 names the variable.
4. **Passive state-merging (AALpy) with a custom compatibility criterion** — as the scalable
   engine for the *whole-corpus* version, injecting discovered hidden variables as
   merge constraints. Discovery-grade (MINT/FlexFringe) for triage, not final exactness.

**De-prioritize:** Koopman/subspace ID (wrong regime); grammar compression (wrong layer,
useful only for note sequences).

## The one-line takeaway

The reframe debate resolves to a **third option neither of us named**: not pure
observe-and-fit (fails on hidden coupling), not full mechanism-mirroring (the old pain), but
**grey-box minimal-model learning** — use the binary only to *name* the state/coupling
variables, then represent behavior as a canonical minimal automaton / WFA fitted from the
trace. That is exact, engine-agnostic in *representation*, ML-friendly, and it's a mature,
tooled research area (RALib, AALpy, spectral-WFA, + our own `z3_decompose`).

## Sources (confirmed-claim anchors)
- RALib / SL* (register-automaton learning): github.com/LearnLib/ralib
- EFSM/register automata + Nerode generalization: link.springer.com/article/10.1007/s00165-016-0355-5
- Grey-box RA / combination locks / arithmetic limitation: arXiv:2009.09975
- Myhill–Nerode for register automata: arXiv:2007.03540
- Passive Moore-machine learning / MooreMI (exact-in-limit): arXiv:1605.07805
- Spectral/Hankel WFA, Fliess theorem (unverified but load-bearing): jmlr.org/papers/v16/thon15a.html,
  cs.nyu.edu/~mohri/pub/cai.pdf, games-automata-play.github.io/blog/fliess_theorem/
- MINT / EFSM-from-executions: researchgate 273757914; FlexFringe/AALpy: arXiv:2203.16331
- CEGIS/SyGuS/trace-RE: cis.upenn.edu/~alur/SyGuS13.pdf, usenix blazytko (Syntia), binsec 2021
