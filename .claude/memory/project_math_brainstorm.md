---
name: Math brainstorm checklist
description: 10+ mathematical approaches to improve Das Model fidelity — from information theory to category theory. Checklist of ideas to revisit.
type: project
---

# Math & CS Brainstorm for Das Model

Generated 2026-04-26 during discussion about fundamental limitations (90.2% register match ceiling).

## Context
Das Model loses information at two steps: abstraction (binary → model) and reconstruction (model → code). The user's key insight: grab behavior directly from the original instead of reconstructing from scratch. These ideas formalize and extend that insight.

## Immediately Actionable

- [x] **~~Table arpeggio~~** — CORRECTED: bit 3 in Commando is PW mode, NOT table arp (post-1986 only). No missing arp feature in Commando.
- [x] **~~Skydive/vibrato~~** — Investigated: doesn't fire in Commando (notes too short for >=3 frame condition). Only matters for other Hubbard songs with longer skydive notes.
- [ ] **Direct code transplant** — Still promising for other engines. For Commando, all features are now accounted for.
- [x] **DFT on error signal** — DONE. Key findings: (1) V1 PW error is sinusoidal at sweep period = siddump measurement artifact, V1 PW is 100% correct in py65. (2) V1 freq error is non-periodic = extended table, no periodic fix. (3) Overall py65 match is 95.0% vs siddump's 89.8% — 5.2% was fake measurement noise.
- [ ] **Statechart formalization** — Still useful for systematically modeling other engines.

## Deep Analysis

- [ ] **Information theory (Shannon)** — Compute entropy map of the original binary. High-entropy regions = can't be dropped without loss. Calculate mutual information between engine code sections and register output to find which code contributes most to sound. Our SID is 329 bytes smaller = 329 bytes of lost information.
- [ ] **Kolmogorov complexity** — Our engine approximates the shortest program producing the register trace. Gap between our engine size and K(x) tells us how much more we could compress without losing fidelity. If near K(x), we're optimal. If far, we're missing structural patterns.
- [ ] **Bisimulation (process algebra)** — Formalize both engines as labeled transition systems. Check bisimulation, not just trace equivalence. Bisimulation failure points = exact behavioral branches we're missing. Stronger than register comparison.
- [ ] **Lossless compression theory** — Original: 4KB → 90KB registers (22:1). Compute theoretical minimum SID size for lossless register reproduction. Any lossless representation must preserve ALL information. If our SID is smaller AND lossy, the gap quantifies exactly how much to add back.

## Speculative / Research

- [ ] **Category theory** — There's a functor F: HubbardStates → DasModelStates that isn't faithful. The kernel of F = lost behavioral features. Finding this kernel formally = finding what to fix. Beautiful but possibly impractical.
- [ ] **Automata learning (L*, Angluin)** — Treat original SID as black box with oracle access (siddump). Learn minimal DFA describing its behavior. Compare to DFA our engine implements. Difference in state count = missing complexity.
- [x] **~~Live-memory T entries~~** — TESTED: copying our pat_ptr into T[100] produces WRONG values because our data is at different addresses. T[100] = V2 pat_ptr lo, T[100] hi = V3 pat_ptr lo in Hubbard. Our addresses differ → different values. Mechanism is correct but values don't match. Extended table is a fundamental limitation of memory layout abstraction.
- [ ] **T as program** — Extend Das Model so T entries can be "computed" instead of static. For T[100]: `read byte at ZP offset +N`. Generalizes static table without data bloat.
- [ ] **Linear algebra (SVD/PCA)** — Run SVD or PCA on the register trace matrix (frames × registers). Principal components reveal the dominant patterns of variation. Could find hidden correlations between voices.
- [ ] **Temporal logic (LTL/CTL)** — Specify properties like "always eventually gate turns off before new note" or "PW never exceeds $0E00 in bidirectional mode." Model-check both engines. Violations = bugs.
- [ ] **Markov chains** — Model register transitions as probabilistic state machine. Hidden Markov model could reveal state dependencies we're not capturing (e.g., cross-voice interactions).
- [ ] **Group theory** — Arpeggio = cyclic group on pitch (Z/12Z for octave arp). PW sweep = group action on pulse width. Table arp = action of a finite group. Symmetry analysis could reveal structural invariants.

## Meta-Insights

- The user's nudge pattern: "extract instruments from the original instead of creating from scratch" was the turning point. Generalized: **always prefer extraction over reconstruction**. Every reconstruction step is a lossy compression.
- 329 bytes smaller = 329 bytes of dropped features. Hubbard is not an idiot. Every byte earns its place.
- The "sustain" issue was really "44% of notes play flat because we ignore TABLE_ARP." User's ear detected a missing FEATURE, not a wrong PARAMETER.
- **Why:** These ideas exist because the gap between 90% and 100% can't be closed by parameter tuning — it requires structural changes to the model.
- **How to apply:** Before attempting a new improvement, check this list. The right mathematical tool for the problem saves weeks of trial-and-error.
