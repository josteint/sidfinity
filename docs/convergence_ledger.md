# Convergence ledger — canonical solutions for recurring problems

## Why this exists

When we migrate a new engine we keep hitting sub-problems we've solved before
(a value swept over time; a byte-indexed program table; a runtime divergence to
localize). Without a record we re-invent a variant each time, and the eventual
grand unification ([Move 1](refactor_1_remaining.md)) becomes a giant
retroactive untangling of N slightly-different solutions.

This ledger **pre-decides** convergence incrementally: each recurring
problem-class gets ONE entry naming the canonical (idiomatic-for-us) solution,
where the shared code lives (or that it's a factor-candidate), and the boundary
conditions. It is a **record, not a refactor** — recording "this should be one
implementation" is cheap and happens now; *making* it one implementation across
engine families is Move 1, deferred until the corpus is rich enough not to
overfit. The ledger is what makes Move 1 smooth: the decisions are already made.

It does NOT replace existing convergence machinery — it routes to it:
- **Representation** convergence is enforced by the **USF schema**
  (`src/usf/types.py`): one dataclass per musical DOF. Most entries below just
  point at the schema.
- **Decision rules** live in `docs/usf_representation_principle.md`.
- **Process/methodology lessons** live in `.claude/memory/` (`feedback_*`).
This ledger's unique value is the **technique/algorithm catalog** — the
*how-we-solve* knowledge that none of those stores holds.

## How to use it

Three separate timings — do NOT conflate them (the record happens first so the
recurrence is later found by lookup, not by memory):

- **CONSULT — before choosing how to solve any non-trivial problem.** Scan the
  Index below by problem-class; if there's an entry, use its solution (call the
  shared code, or implement the recorded form) instead of inventing a variant.
  A consult is a targeted lookup keyed by the problem, not a full read.
- **RECORD — log EVERY solution to a non-trivial problem, on first sight**
  (status `logged`), even if it has occurred only once. This is the point: a
  recorded 1st occurrence makes the 2nd a cheap lookup. Don't wait for a repeat.
- **CANONICALIZE / FACTOR — on the 2nd occurrence.** When a problem-class recurs
  (the [`/uready-review`](../.claude/skills/uready-review/SKILL.md) cross-engine
  pass flags **≥2×**, or you notice it directly), pick the one canonical form
  (status `recurring`) and either point at shared code (`shared`) or mark it a
  Move-1 `factor-candidate`. The ≥2× threshold governs ONLY this step — never
  whether something is recorded. The code-factoring itself waits for Move 1.

`/uready-review` is the periodic maintainer (cross-checks + promotes); per-solve
recording is the everyday reflex (see the CLAUDE.md "before pipeline work" list).

Entry schema: **Problem class** | **Canonical solution** | **Status** |
**Boundary / when it applies** | **Consumers (seen)**.

**Status:** `logged` (seen 1×, provisional form) · `recurring` (≥2×, canonical
form chosen) · `factor-candidate` (recurring, awaiting Move-1 code-factoring) ·
`shared` (one implementation exists; consumers call it) · `methodology` (a
practice, not code to factor).

If the Index outgrows a quick scan, migrate to a queryable store (the
`hvsc84.csv` → DuckDB precedent) — keep consults O(lookup), never O(read-all).

## Index (problem-class → entry)

| Problem class / keywords | Entry | Status |
|---|---|---|
| value swept over time · PW / cutoff contour · oscillator · ramp | C1 | shared |
| byte-indexed program table · runs off-table · table extent / size | C2 | factor-candidate (3×) |
| "no program" detection · leading (0,0) · idle position 0 | C3 | methodology |
| localize runtime divergence · writelog diverges, cause internal · memwatch | C4 | methodology |
| detection ≠ FULL · residue triage · accept-at-detect | C5 | methodology |

---

## Entries

### C1 — A control value swept over time (pulse-width, filter cutoff, any contour)
- **Canonical:** `SweepEnvelope(start, phases=[(rate, frames)], loop)`. Capture
  with `pipelines/dmc/v5/extract/to_usf.py:_capture_env`; rebuild with
  `from_usf.py:add_env`.
- **Status:** ✅ SHARED (USF schema + `_capture_env` + `add_env`).
- **Boundary:** piecewise-constant-rate contours. A bounded bidirectional
  oscillator is the special case `start + [(+s,n),(−s,n)], loop=0` — verified
  losslessly expressible (decision-1 gate, 2026-06-18).
- **Consumers:** DMC `pulse_env`, `filter_env`, `default_pulse`, `default_filter`.
  **DMC-v4 `PwmConfig`** is a DIVERGENT second form of the same DOF →
  [Move-1 decision 1](refactor_1_remaining.md): unify onto `SweepEnvelope`.

### C2 — Engine program table indexed by a byte pointer (program runs off-table)
- **Canonical:** bound the captured table by `min(256, 0x10000-a_lo,
  0x10000-a_hi)` — NOT the lo/hi-array delta. The pointer is a byte, so a
  program longer than the array runs into the overlapping/adjacent arrays; let
  the per-program walker bound reachability (loop / terminal / song-reach).
- **Status:** ⚠️ DUPLICATED in `engine_model.py` (`n_filter`/`n_pulse`/`n_wave`)
  — same idiom written 3×. Local v5 dedup is cheap anytime; the cross-engine
  table-handling convergence is a Move-1 factor-candidate. **Seen 3×.**
- **Boundary:** byte-indexed `(step,count)` or `(ctrl,freq)` program tables laid
  out contiguously by a packer.
- **Consumers:** DMC v5 filter (orig), pulse (+17 FULL), wave (+6 FULL) — all
  2026-06-18.

### C3 — "No program" detection at table position 0
- **Canonical:** a leading `(0,0)` is a VALID zero-rate phase (its count is at
  the next slot), not "no program." Detect genuine absence as a single zero-rate
  **terminal** hold (count ≥ `0x9000`). Never gate on `entry0 != (0,0)`.
- **Status:** 📋 methodology (encoded in v5 `to_usf` `default_pulse`).
- **Boundary:** `(add,count)` phase tables with a default/idle position 0.
- **Consumers:** DMC v5 `default_pulse` (+25 FULL, 2026-06-18). The wrong gate
  caused both "mine holds where orig ramps" and "mine's null pos-0 bleeds into
  the adjacent program."

### C4 — Localizing a runtime divergence (writelog diverges, cause is engine-internal)
- **Canonical:** `assemble(asm, return_labels=True)` to get OUR engine's state
  symbol addresses; `siddump --memwatch-on-write <reg> <addrs>` to snapshot our
  state per write; compare event-by-event against the ORIG's state at its known
  disasm addresses. Diagnostic: "full note-state identical + only the output
  register differs ⇒ the bug is the program that register runs, not the
  note/trigger logic."
- **Status:** 📋 technique (used 2026-06-18 to crack `default_pulse`). Generalizes
  the FC event-aligned `state_diff` idea to our own composed engines.
- **Boundary:** when `find_first_divergence` localizes the register but not the
  cause; needs a hand-annotated orig `disassembly.s` for the orig addresses.

### C5 — Detection ≠ FULL
- **Canonical:** accepting a member past the factory's detection gate just moves
  it to its NEXT failure mode (cia / partial / error) — it is NOT a FULL. The
  verify PARTIALS, not the detect-rejects, are the FULL bottleneck.
- **Status:** 📋 methodology — see [[reference_divergence_census]],
  `tools/divergence_census.py`.
- **Boundary:** any wide-family residue triage.
- **Consumers:** DMC v5 reloc@$10E5 (2026-06-18: cleared the reloc gate → 32
  surfaced as cia_multispeed, only 5 reached FULL).
