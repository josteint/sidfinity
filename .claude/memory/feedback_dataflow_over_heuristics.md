---
name: feedback_dataflow_over_heuristics
description: "For reverse-engineered 6502 players (and any structured engineered code where the source bytes are in hand), default to semantic dataflow tracing — find the SID-register STA, follow A backwards through predecessor instructions to its source. Reach for content heuristics ONLY when the semantics aren't recoverable."
type: feedback
---

When extracting engine data from a 6502 SID player, default to
dataflow tracing, not content heuristics.

**Why:** The engine is engineered code. Every value it writes to a
SID register has a provenance — trace it through the LDA/STA chain.
If `STA $D400,X` is V_FREQ_LO, then the A loaded just before it
came from the freq_lo table. Walk back through predecessor
instructions (skipping A-neutral ops: CLC, SEC, INC mem, STA, STX,
LDX, …) until you hit an LDA. Follow indirection through voice-state
slots when needed. That's an unambiguous answer.

Content heuristics — "the table with more distinct values is freq_lo",
"the lower address is the lo table" — work most of the time and
fail silently at the edges. Blade_Runner and Space_Doubt store their
freq tables in *reverse* order (hi at lower address) — my
"lower=lo" heuristic would have shipped the wrong tables, and the
mistake would only have surfaced dozens of commits later at byte-
exact verify.

**How to apply:**

- **Find the SID write first.** For freq_lo: `STA $D400/$D407/$D40E,X/Y`.
  For master vol: `STA $D418`. For voice ctrl: `STA $D404/...,X/Y`.
  These are the load-bearing observations.
- **Walk back through predecessors.** Build a sorted reachable-PC
  list, find the index of the STA, walk earlier indices skipping
  A-neutral ops until you hit the LDA.
- **Follow indirection if needed.** If the immediate LDA is from a
  voice-state slot (`LDA $abs,Y`), find the STA to that slot
  elsewhere and recurse — one more LDA back gets you to the table
  in 95% of cases.
- **Save heuristics for genuinely opaque cases.** If the engine
  computes a freq via SBC/ADC chains without a table at all, the
  trace won't terminate at a `LDA abs,X` — that's the case where
  you fall back to something else. Until then: trace.

**Lesson from session of 2026-05-31:** I shipped a content
heuristic for jay_derrett's freq-table detection (lo<hi
content-distinct-count). The user pushed back on the heuristic since
I'd done a full disassembly. Rewriting to dataflow took ~100 lines
vs ~10 — but caught two real engines (Blade_Runner, Space_Doubt)
where the heuristic would have silently shipped wrong tables.

**Related:** [[feedback_principle_first_analysis]] (run the
representation-principle checklist first), [[feedback_6502_mindset]]
(everything is a pointer error — including "where did A come from"),
[[feedback_user_nudge_pattern]] (the user catches code smells the
model misses).
