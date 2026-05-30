---
name: Mathematical formalization initiative
description: Strategic decision to formalize SIDfinity mathematically — 6502+SID semantics, USF semantics, trace equivalence, inverse solver — to crack all of HVSC systematically
type: project
---

User invested in formalizing SIDfinity mathematically. 10 approaches tested on 2026-04-18. Results in `docs/formal/experiment_results.md`, procedure in `docs/formal/procedure.md`.

**What works (use these):**
1. **Trace equivalence analysis** — mine sid_compare.py for mathematical property violations (symmetry, new tolerance rules). Gained +393 Grade A songs. THE highest-ROI math work.
2. **USF normalization** — 22% token reduction via rest merging, dedup, transpose inlining. Use before ML training.
3. **Formal USF semantics** (`src/formal/usf_semantics.py`) — 15x faster than siddump for smoke testing, correctly triages 19/20 bugs to extraction vs codegen.
4. **Taint tracking** (`/tmp/symbolic_exec.py`) — run py65 with instrumentation, finds driver structure in 100% of songs. GT2/Hubbard have mirror-image architectures.
5. **Information theory** — USF is efficient (5.67 bits/token). Voices 31% correlated. Rest tokens = 42% of stream (optimization target).

**What doesn't work (don't use):**
- Z3 inverse solver for GT2 (static parser already better)
- CEGIS auto-fix (treats symptoms not causes)
- Lean formalization (Z3 sufficient, wrong abstraction level)

**How to apply:** Read `docs/formal/procedure.md` for decision framework: grading problems → trace equivalence; new engines → taint tracking; ML prep → normalization; fast dev → formal semantics.
