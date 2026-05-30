---
name: Formal methods tools
description: New formal methods infrastructure in src/formal/ — USF semantics, trace equivalence, inverse solver, abstract interpreter
type: reference
---

## src/formal/ — Mathematical Tools

| File | Purpose | Verdict |
|------|---------|---------|
| `usf_semantics.py` | Executable USF playback state machine. USFPlayer(song).run(N). | USEFUL: 15x faster than siddump, 84% frame accuracy, bug triage |
| `trace_equivalence.py` | Formal refactoring of sid_compare.py as composable rules. | VERY USEFUL: found 3 bugs → +393 Grade A songs |
| `inverse_solver.py` | Z3-based trace→USF solver. 19/19 tests pass. | NOT USEFUL for GT2 (static parser better). May help non-GT2. |
| `abstract_interp.py` | Abstract interpretation of 6502 SID drivers. | NEEDS WORK: 82% SID writes but only 10% freq tables |
| `z3_regtrace.py` | Z3-enhanced register trace converter. | NOT USEFUL: same results as heuristic |
| `test_semantics.py` | 11 property tests for formal USF semantics. | All pass |

## docs/formal/
| File | Purpose |
|------|---------|
| `experiment_results.md` | **READ THIS FIRST** — 10 experiments tested, verdicts, what works/doesn't |
| `procedure.md` | When to use which tool, decision framework |
| `mathematical_framework.md` | 5-layer formal model, notation, theory |
| `lean_feasibility.md` | Lean 4 research (verdict: not justified) |
