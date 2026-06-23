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
| byte-indexed program table · runs off-table · table extent / size · index overruns into adjacent array | C2 | factor-candidate (5×+: freq/pulse/wave/filter) |
| "no program" detection · leading (0,0) · idle position 0 | C3 | methodology |
| localize runtime divergence · writelog diverges, cause internal · memwatch | C4 | methodology |
| detection ≠ FULL · residue triage · accept-at-detect | C5 | methodology |
| off-table FREQ lookup · index past freq table · wave-relative note offset | C6 | recurring (FC + v5) |
| ANTI-PATTERN: verbatim/opaque musical bytes · leapfrog · content-by-reference blob | C7 | methodology (recurring) |

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
- **Consumers (canonical):** DMC `pulse_env`, `filter_env`, `default_pulse`,
  `default_filter`.
- **DIVERGENT forms of the same DOF across families** (Move-1 decisions D1/D2,
  see [refactor_1_remaining.md](refactor_1_remaining.md) all-families review
  2026-06-18 — unify onto `SweepEnvelope`): Hubbard `pwm` (linear/bidi) · FC
  `pulse_prog`+`pulse_programs` and `filter_prog`+`filter_programs` (indexed
  library — the §7-adjacent form) · DMC-v4 `pwm` (bidi) + `filter_programs`
  (its `steps` are already `(rate,frames)` ≈ phases). 4 PW forms + 3 filter
  forms across the corpus; even DMC v4↔v5 disagree (intra-family fork).

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
  2026-06-18. **DMC v4 (2026-06-23):** wave off-table (`_slice_wave` extended +
  `_resolve_wave_chain` for multi-hop marker chains, zero_wave_table 117 -> 37
  FULL); FILTER step-index overrun (the `repeat` byte > 5 indexes past the 6
  step-sizes into the durations — the engine reads `size = def+4+index`, so a
  contiguous `[6 sizes][6 durations]` layout reproduces the rise-to-stop sweep;
  the composer had an 8-byte `[6 sizes][2 pad]` stride that broke it, +11 FULL).
  The lesson recurs at EVERY table the packer lays contiguously: capture/lay-out
  the adjacent bytes the overrun index reads (or SIMULATE the walk and emit the
  resolved sequence — the wave marker-chain resolver), never bound by the array's
  nominal length. **Seen 5×+ now (freq C6, pulse, wave×2, filter) — canonicalize.**

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

### C7 — ANTI-PATTERN: original bytes carrying musical intent that bypass / opaquely sit in the USF
- **The smell (user's, since project inception):** bytes from the original SID
  that encode MUSICAL information end up in the output SID without being produced
  from first principles by musical content in the USF. Three severities — keep
  them distinct:
  - **Class A — leapfrog:** orig bytes → output, BYPASSING the USF entirely. The
    ML never sees them. Worst when the bytes are musical (A2). *Status across the
    live verdict pipelines: NONE* (all composers build orig-free except synthesized
    metadata + digi PCM). FC's `compose_fc_asm`/`build_via_asm`/`_emit_verbatim_region`
    were the only leapfrog and are session-1 scaffold — gated off live (every config
    sets `emit_data_from_usf=True`); the dead functions were removed 2026-06-18.
  - **Class B — opaque blob IN the USF:** bytes round-trip through the USF (§9-clean)
    but as a raw content-by-reference list with no musical structure → the ML sees a
    black box. **`freq_overrun` is RESOLVED (2026-06-21):** both consumers (FC std +
    DMC v5) deconstructed to musical per-instrument `offtable_freq` frequencies via
    C7-option-(a) — see C6; the field itself is pending removal (plan Phase 7).
    Remaining B instances: `SfxSubtune.extended_freq` (Hubbard SFX off-table sweep),
    some Hubbard engines' 320-byte `freq_table` (192 musical + 128 state tail read by
    arp extension; the notenum-overlap engines — Commando itself is a clean 192).
  - **Class C — justified:** the bytes ARE the natural musical form (`freq_table`
    tuning, digi PCM). Not the anti-pattern.
- **Why B recurs (the mechanism):** an engine indexes PAST a freq table
  (`index = offset + note > table_size`) into its own state/scratch region, and
  those bytes get PLAYED as frequencies. The same bytes are BOTH engine state AND
  read-as-freq — content-by-reference captures them (write-stream correct) but
  presents them opaquely. Largely **B2** (state read as freq, incidental) not
  **B1** (deliberate extended tuning): the off-table bytes don't form a coherent
  monotonic tuning (Elysium window = state/scratch, not a tuning continuation).
- **Decision (per instance, the human's — surface, don't cargo-cult):**
  (a) **deconstruct to musical** — represent each off-table step's RESULTING freq
  as an absolute freq/note (hard: note-dependent → effectively an extended tuning
  table, and for B2 the extra entries are state-derived); (b) **document + minimize**
  — reachability-minimal capture, flagged "engine reads state-as-freq" (the ML sees
  a small, labeled blob; DMC v5's `freq_overrun` is NOT minimized yet — a C3-gap);
  (c) **exclude** the tune as engine-quirk-dependent.
- **Status:** `methodology` (recurring). **Before adding any new content-by-reference
  / `bytes`-typed USF field, CONSULT this entry and pick (a)/(b)/(c) deliberately.**
  Audit hook: `/uready-review` should flag every content-by-reference/`bytes` USF
  field as a B-class candidate. (Distinct from C6, which is the off-table-freq
  TECHNIQUE; C7 is the anti-pattern lens over it + extended_freq + the freq_table tail.)

### C6 — Off-table FREQ-table lookup (index past the N-entry freq table)
- **Canonical (CANONICALIZED 2026-06-21, both consumers):** when a melodic/effect
  path adds a table-relative offset to a note and the 8-bit index
  `(offset + note) & $FF` passes the freq table, the read falls into the following
  image bytes, which the orig plays as REAL freqs (content-by-reference, not a bug
  to clamp). **Deconstruct each off-table read to a musical FREQUENCY attributed to
  the instrument + note that plays it** — per-instrument `Instrument.offtable_freq`
  records `(offset, note, lo, hi)`, idx=(offset+note)&$FF (the ML learns a
  drum/tone pitch, not a byte at a memory offset). The composer rebuilds whatever
  internal window/layout it needs FROM those records (engine-blind); the USF never
  carries the opaque window. This is C7-option-(a) realized. ❌ DO NOT emit a
  contiguous `freq_overrun` window — that is the superseded form (it silently masks
  reach-model under-captures within its span; see the LO-read bug below).
- **Status:** `canonical` (FC standard + DMC v5, both migrated to `offtable_freq`).
  Schema + USF I/O shared; the composer reconstruction is per-composer (FC
  `composer_asm._offtable_window` vs v5 `composer_v5`) → a Move-1 factor-candidate.
  Distinct from **C2** (off-table PROGRAM tables; this is off-table DATA lookup).
- **Boundary:** reachability = offset values × played notes × transposes
  (conservative over-approx). With exact per-read capture an under-capture diverges
  in verify (never silent). **GOTCHA — the dual lo/hi read:** the off-table read is
  BOTH `freqlo[idx]` and `freqhi[idx]`; with contiguous freqlo[entries],
  freqhi[entries],window the LO read at idx≥2·entries lands DEEPER in the same
  window (pos idx−2·entries) than the HI read (pos idx−entries). The composer must
  populate BOTH positions (provably the same byte, `mem[hi_base+idx] ==
  mem[lo_base+idx+entries]`). A contiguous window hides this; exact capture exposes
  it (FC At_War class, 2026-06-21).
- **Consumers:** FC standard (`engine_model._std_offtable_freq` → 2528 FULL,
  freq_overrun blob eliminated, 2026-06-21); DMC v5 (`engine_model._assign_offtable_freq`
  → 1041 FULL, blob eliminated, 2026-06-21). Both `freq_overrun`-free; the schema
  field removal is the pending cleanup (`docs/offtable_freq_plan.md` Phase 7).

### C5 — Detection ≠ FULL
- **Canonical:** accepting a member past the factory's detection gate just moves
  it to its NEXT failure mode (cia / partial / error) — it is NOT a FULL. The
  verify PARTIALS, not the detect-rejects, are the FULL bottleneck.
- **Status:** 📋 methodology — see [[reference_divergence_census]],
  `tools/divergence_census.py`.
- **Boundary:** any wide-family residue triage.
- **Consumers:** DMC v5 reloc@$10E5 (2026-06-18: cleared the reloc gate → 32
  surfaced as cia_multispeed, only 5 reached FULL).
