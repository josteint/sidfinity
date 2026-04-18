# Mathematical Methods: Experiment Results

**Date:** 2026-04-18
**Scope:** 10 experiments testing mathematical approaches for SIDfinity

## Summary

6 useful, 1 needs work, 3 not useful. The trace equivalence formalization gained +393 Grade A songs — more impact than all other methods combined.

| # | Method | Verdict | Key Result |
|---|--------|---------|------------|
| 7 | Trace equivalence formalization | **VERY USEFUL** | +393 Grade A (symmetric FrameShift, both-gates-off, EarlyNoteStart) |
| 5 | E-graphs / USF normalization | **USEFUL** | 22% token reduction for ML training |
| 6 | Formal USF semantics | **USEFUL** | 15x faster validation, 19/20 bugs triaged correctly |
| 3 | Symbolic execution (taint tracking) | **USEFUL** | 100% structure detection, engine fingerprinting |
| 9 | Information theory | **USEFUL** | 31% voice redundancy, rest-token optimization target |
| 10 | Parser combinators | USEFUL (low) | 3x more concise format specs, but not for discovery |
| 2 | Abstract interpretation | NEEDS WORK | 82% SID writes, only 10% freq tables (indirect addressing) |
| 1 | Z3 inverse solver | NOT USEFUL | Static parser already handles custom freq tables |
| 4 | CEGIS auto-fix | NOT USEFUL | Marginal improvements, treats symptoms not causes |
| 8 | Lean 4 | NOT JUSTIFIED | Z3 sufficient, wrong abstraction level, 24-40 week investment |

## What Works and Why

The useful approaches share a trait: they operate on the **comparison/grading layer** or provide **development speed**.

- **Trace equivalence**: directly finds bugs in the grading function. Each bug fix reclassifies hundreds of songs. Low effort, high impact.
- **E-graphs normalization**: reduces token count for ML training without affecting audio quality.
- **Formal semantics**: 15x faster than siddump for smoke testing. Correctly triages bugs to extraction vs codegen.
- **Taint tracking**: reveals engine architecture automatically. GT2 and Hubbard have mirror-image data flow.
- **Information theory**: identifies optimization targets (rest tokens = 42% of stream, voices 31% correlated).

## What Doesn't Work and Why

- **Z3 inverse solver**: the static GT2 parser already extracts custom freq tables and arpeggios. Z3 finds the same answers slower.
- **CEGIS**: Grade C/F errors are systematic pipeline bugs (wrong timing, wrong table interpretation), not individual wrong bytes. Fixing one note at a time treats symptoms.
- **Lean**: proves properties of 6502 instructions, but the project's bugs are in decompiler/codegen logic, not instruction semantics. The regression suite catches more real bugs.
