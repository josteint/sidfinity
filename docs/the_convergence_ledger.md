# The Convergence Ledger

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
- **Decision rules** live in `docs/the_principle.md`.
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
  **Placement rule — what goes IN the entry vs. where it links:** an entry
  carries the *transferable* knowledge — the problem-class, canonical solution,
  boundaries/refinements, TELLs, and warnings about alternative fixes that
  failed (those are technique, keep them verbatim). Per-occurrence *status* —
  member names, round numbers, "+N FULL" counts, commit hashes, member-specific
  byte values — lives in the engine's memory (`project_<engine>`, its round
  changelog) and the entry LINKS there (e.g. "worked example: [[project_dmc]]
  round 18") instead of duplicating it. One home per fact; the ledger holds
  what generalizes, the engine file holds who hit it and when. (Entries written
  before 2026-07-14 predate this rule and are grandfathered as-is — do not
  retroactively distill them; distillation of technique is lossy.)
- **CANONICALIZE / FACTOR — on the 2nd occurrence.** When a problem-class recurs
  (the [`/uready-review`](../.claude/skills/uready-review/SKILL.md) cross-engine
  pass flags **≥2×**, or you notice it directly), pick the one canonical form
  (status `recurring`) and either point at shared code (`shared`) or mark it a
  Move-1 `factor-candidate`. The ≥2× threshold governs ONLY this step — never
  whether something is recorded. The code-factoring itself waits for Move 1.

`/uready-review` is the periodic maintainer (cross-checks + promotes); per-solve
recording is the everyday reflex (see the CLAUDE.md "before pipeline work" list).

When a fix for a member's first divergence **regresses other members**, run the
[`/amend`](../.claude/skills/amend/SKILL.md) skill — it operationalises this
ledger + the CORE TENET + the principle + the trichotomy for exactly that
situation (options to EXPLORE, not presumed causes: maybe a suboptimal PAST fix
is the real defect and an overarching fix serves both, maybe the divergence is
editorial intent to keep — or maybe the new fix is just wrong; always score by
the first divergence, not FULL).

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
| de-fused per-entity pool exceeds byte-index capacity · "pool overflow" · separate copies per instrument | C8 | canonicalized |
| runtime param unreadable by py65 (init hangs / IRQ-set / bad opcode) · measure from libsidplayfp writelog | C9 | logged |
| chip-global $D415-$D418 automation during a song · master vol / filter varies · global_track vs MasterVolConfig/filter_programs · explicit-event vs parametric | C10 | logged |
| engine reads a table via an 8-bit index register (`base,Y` w/ Y=#*stride) · orig "reads garbage"/looks broken · extractor must wrap `(#*stride)&0xFF` · suspect OUR extractor not the packer | C11 | logged |
| off-table read sonifies a "positional" byte counter (sector position / stream offset) · per-event deltas derive from row kind + stated commands → live shadow, stated-command flags = §8 arrangement (DMC sectpos) | C11 | logged |
| off-table read sonifies the live WAVE POSITION ($177A) · composer pool offsets ≠ orig's → layout-preserving pool packing from per-instrument editor wave-table positions (`wave_table_pos`, §8 arrangement) + gated redirect row (DMC wavepos) | C11 | logged |
| accumulated per-step rounding drift in a round-trip · USF stores DELTAS (durations), player sums them to ABSOLUTE positions · a min/floor on each delta drifts over a long song · short tunes pass, long tunes length_fail · keep deltas EXACT (allow 0) | C12 | logged |
| engine variant dispatch · player jump-table init offset shifted but play body at canonical offset · "no_jumptable"/code-mismatch reject · dispatch on the PLAY-body signature not init (we emit our own init) | C13 | logged |
| command-per-row tracker effect (note + fx + param per row) · porta/vibrato/arp/filter/tempo on a row · NOT per-instrument · how to represent in NoteRow | C14 | recurring (FC + GoatTracker V1) |
| INAUDIBLE writes · idle/gate-off voice freewheels · "audio-equivalence" verdict relaxation | C15 | ⛔ REMOVED (user decision 2026-07-01): every SID gets STRICT write-stream match, always — never propose relaxing the verdict during per-engine work. If an idle-freewheel divergence blocks a member, REPRODUCE the writes (core tenet permits reproducing the mechanism). Design parked in `refactor_1_remaining.md` as a Move-1-era-ONLY consideration. |
| per-frame WRITE-ORDER differs · orig batches note-on writes (SR/AD/CTRL) separately from wave-step writes (freq/PW/CTRL) or uses a different voice interleave · rebuild emits a different order · NOT a wholesale composer rewrite — PARAMETRIZE the composer's EMISSION order (precedent: FC `nextvoice_write_order`) | C16 | logged |
| HETEROGENEOUS per-step write shapes in a trace-lift · one superset order can't embed all steps (conflicting reg orders / intra-step dups / sections) · cluster steps by EXACT write shape → K positional templates + per-step template id | C17 | logged |
| play-vector WRAPPER with per-call PHASE behaviour · slow-tempo / multispeed-effects cycler · every Nth call runs the full play, others run effects-only / register-refresh / nothing · wrapper shapes vary (SMC, DEC+dual-JMP, parity AND) — OBSERVE entry-point reachability under py65, don't parse · arm F-ENTRY variant: wavestep ($1591) vs vibrato half-cycle ($1567, flips reshape vibrato to a square) → `effect_entry_variant: vibflip` | C18 | logged |
| TRICHOTOMY VERDICT alignment · rebuild emits its OWN init (universal reset+priming) so streams differ by an init prefix · Check A end-of-init state + aligned play-stream compare · TWO implementations exist: `verify_cycle._trichotomy_compare` (FC, shift recovery) + `usf_roundtrip._compare_music/_split_aligned` (basic_program, known-init-length + probe search) — CONSULT MISS, factor at Move 1 | C21 | factor-candidate (2×) |
| hand-patched player WEDGE inside the canon body · SMC opcode toggle · 1-byte opcode patch · JMP over canonical loads · runtime state ≠ static file byte · PWM bound-shift (LSR count) wedge · init-PREFIX `LDA #imm` hard-forces the played tune record (extract walks the wrong record) · STATIC opcode probe, never a bounded stream scan · census carriers both sides · reproduce semantics behind a factory-probed param (EXTRACT-only when the wedge changes a derived musical value; COMPOSER param when it changes a write-stream TIMING/VALUE, e.g. $D418 re-asserted every frame · SWITCH gate-toggle EOR immediate) | C19 | canonicalized (11×) |
| stale-FULL palimpsest · recorded 'full' the current code can't reproduce · hides members from residue censuses · verify the STORED build first, then USF-diff/param-bisect to attribute · never mass-write with code that didn't produce the verdict | C20 | canonicalized |
| AMBIGUOUS round-trip flag encoding · two distinct engine ops render to OVERLAPPING USF flag sets · the decoder's branch test uses a SUBSET of the discriminator → misroutes one op onto the other's path · matches for most content (paths coincide when inputs coincide), diverges on the distinguishing case | C22 | canonicalized (2×) |
| a play-phase/schedule TOKEN hides a per-member behavioural ambiguity · same P_F123 token = note-init-on-F vs deferred 2-frame arm · fixing one class REGRESSES same-token FULLs · NOT derivable from the token/multispeed → OBSERVE the distinguishing write-footprint per member · regression-safe when the "changed" verdict has no false positive | C23 | logged |
| play-body UNIT-repeat · play body runs ONE of its 4 units (v0/v1/v2/filter-tail) N× per play() (JSR-to-N-call stub; JMP-tail form re-runs the filter tail) · "double-speed voice" · unified play_unit_repeat=[v0,v1,v2,filter] list · distinct from play_repeat (whole play()) + C18 play_phases (whole calls) · static byte-probe (C19 method) | C24 | recurring |
| whole-play N-repeat (WHOLE play() body run N× per VBI = double-speed TUNE) via a play-VECTOR wrapper · perfect play-stream PREFIX + clean ~N× length tail on a VBLANK tune · `JSR T ×N :RTS` or `JSR T; JMP T` · `_detect_play_repeat` must FOLLOW a base+3 JMP indirection into the wrapper, not short-circuit on play==base+3 | C24 | note (recurring 10×) |
| composer play body OVERRUNS a tight CIA latch · perfect play-stream prefix + length tail ~0.5% (rate drift, no content divergence) · common-path cost creep (per-row compare chains growing with each round's shadow additions) · fast-path the common case O(1) · the rebuild's play must FIT the smallest latch it ships under | C25 | logged |
| song data ABSENT from file image · init generates/unpacks tables in RAM · operands point outside the loaded image · extract from POST-INIT RAM (py65), all-or-nothing signature · banking-wrapper JT-less base from the wrapper JSR target | C26 | logged |
| multi-SID (2SID/3SID) · N chips, one player each behind a dispatch wrapper · players run sequentially -> merged log = [chip1][chip2] · extract/compose/verify each with single-chip machinery, chip-TAGGED (reg=chip*$20+reg) · voices number through chips, addresses are pipeline constants not USF | C27 | logged |
| multi-SID VERDICT · rebuild is per-chip correct but the merged chip-tagged stream diverges on a CROSS-CHIP adjacency (chip1 vs chip2 write order) · cross-chip order is physically UNobservable (independent hardware, Trap-B analogue) · split by reg//0x20, require each chip's substream to pass · compare_instruction_stream(n_chips=N) · do NOT chase cycle precision / straddle-free capture | C28 | logged |
| track $FF loop into an OUT-OF-IMAGE sector (garbage sector# past the ptr table → $0000) · engine sonifies live ZEROPAGE as notes (6510 port $00=$2F/$01=$37 then static zp, read via ($F8),y=$0000) · extract overlays libsidplayfp runtime low-RAM (C9, py65 can't reproduce env zp) gated on _loops_offimage · port + $F8/$F9 read-time corrections · regr-safe: unplayed decode = byte-identical | C29 | logged |
| LOSSY ENUM over independently-toggleable flag bits · USF enum assumed two editor flags mutually exclusive (gate hold $10 / never-release $08) · engine gives one priority so the co-set bit is MECHANICALLY DEAD · but the raw flags byte is OBSERVABLE via a state-as-data read (off-table fxf) → reconstruction misses the dead bit · carry the masked flag as an elidable boolean CO-FIELD, keep the enum = the EFFECTIVE articulation | C30 | logged |

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
  `default_filter`. **basic_program per-frame PWM — ✅ LANDED (commit f2eaabf,
  Cascading FULL)** — a free-running per-voice pulse-width sweep PROGRAM: each
  voice runs an independent automation orderlist (a value-table of distinct
  period bytes + RLE sections `(offset, period_len, repeats)`; dedup reuses
  identical period runs). The single-`SweepEnvelope` form was insufficient — the
  real signal is a multi-section program (~40 sections/voice), so it generalizes
  the contour into a sectioned orderlist (still parametric/musical, NOT a raw
  period table — the table holds only distinct periods, sections index them).
  This is the `default_pulse` continuous analog, not per-instrument. Player =
  a 6502 sweep walker advancing at a FRACTIONAL rate (mod_inc/256 ticks per
  play() = the BASIC-loop rate, not 50Hz); notes re-timed onto the sweep-tick
  clock; PW emitted before the note check ([PW][note] within a tick). Confirms
  C1 generalizes to a 5th family. Remaining basic_program modulation tunes need
  per-voice gating + arp (Pong/Doom_Comer) or filter-`$D416` modulation
  (Sullen/Pepper/Brickout, not yet handled).
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
- **Consumers:** DMC v4 filter-def walk (2026-07-02, +17 FULL): repeat>5 reloads
  the step index past the 6-entry arrays and the exact-match `CMP #6` wrap never
  fires again → an unbounded upward walk through adjacent 16-byte def records.
  Canonical form here = emit the composer's table in the ORIG's record layout
  (fdrec, 17 records = the full 8-bit index window; fdstep/fddur as +4/+10 label
  views) so every walked read is byte-exact by construction — reproducing the
  layout beats capturing per-index values when the walk is unbounded.
  DMC v5 filter (orig), pulse (+17 FULL), wave (+6 FULL) — all
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
- **Off-table ONE-SHOT program (no $90 loop) — family-4 pulse, FIRST family-4 FULL
  (Jupiter41, 2026-07-01).** A pointer that walks off-table with no loop is a one-shot
  ramp into adjacent STATIC bytes. Four sub-lessons, all needed:
  1. **CLASSIFY first — taint-check the source** with `tools/taint_source.py <sid>
     <LO-HI> --all` (built 2026-07-01). It runs `siddump --memtrace` (per-ACCESS,
     within-frame-complete; NOT per-frame `--memwatch`, which misses a write-then-restore
     inside one play()) over all subtunes and reports whether the source region is ever
     written. Source never written ⟹ REPRESENTABLE; written ⟹ hard residue. Pure
     black-box observation CANNOT classify it — you must read the source RAM. Cross-cuts
     C6 freq too. (Maturity: one concrete probe validated on Jupiter41 — an OBSERVATION
     over played code paths, not a proof over unexercised branches; raise `--duration` if
     a write might occur only late in the song.)
  2. **Reach = the RE-INIT INTERVAL, not the whole-song window.** A program that re-inits
     every note-load never runs the full song; bounding the walk by the verify window
     over-captures.
  3. **On PHASE_CAP, TRUNCATE the prefix — never fall back to a different-count-WIDTH
     walk.** A one-shot ramp generates unbounded phases at the whole-song reach → phase
     cap. Keep the captured prefix (`_capture_env(truncate_on_cap)`), which covers ≫ the
     re-init interval. The old family-4 fallback to the 16-bit `_capture_env` mis-read the
     8-bit count (`E0`→`0xFFE0`=65504 terminal hold), collapsing the program to `+32`
     forever and DISCARDING the off-table sweep.
  4. **The correct capture is LARGE ⟹ overflow-gated pooling (C8)** to fit the 256-byte
     single-byte index (Jupiter41: 356 B un-shared → 209 B shared).
  ALWAYS localize with the FLAT write-stream (Trap-C-robust), NEVER per-frame register
  snapshots (retracted 3 per-frame localizations this session as Trap-C artifacts, caught
  by a negative control on FULL members). Status: **logged** (1 member: Jupiter41 FULL,
  0 regression); canonicalize when it recurs on another off-table one-shot program.

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
  a small, labeled blob; DMC's off-table capture IS minimized as of 2026-06-21 —
  per-instrument `offtable_freq` records, median 1/file, the old window gone);
  (c) **exclude** the tune as engine-quirk-dependent.
- **Status:** `methodology` (recurring). **Before adding any new content-by-reference
  / `bytes`-typed USF field, CONSULT this entry and pick (a)/(b)/(c) deliberately.**
  Audit hook: `/uready-review` should flag every content-by-reference/`bytes` USF
  field as a B-class candidate. (Distinct from C6, which is the off-table-freq
  TECHNIQUE; C7 is the anti-pattern lens over it + extended_freq + the freq_table tail.)
- **B-class audit RESOLVED (2026-07-06, user-ratified): `dual_freq_generator` +
  `dual_generator_steps`** (round 35, Taurus_02, sole corpus carrier; renamed from
  `dual_hack`/`dual_hack_steps` — behavior naming was the one uready criterion it
  failed). The `/uready-review` first flagged it LEAK-adjacent by comparison with
  the same week's `filter_mod`; the full re-anchor OVERTURNED that comparison as a
  CATEGORY ERROR: `filter_mod` is C10 (global automation with RECOVERABLE
  structure — a triangle LFO, compressible to a contour → typed parametric form
  correct); the dual generator is C19 (hand-patched wedge → probe → param IS the
  canonical form, 5 occurrences). Decision = **C7-(b) document-and-minimize**:
  every write-determining constant is in USF (9 CSV values, 2 lines of a 654-line
  file), the composer holds ONE fixed mechanism (BASIC-ROM bytes = environment,
  same category as the PSID env's zp $2F=$A9 that creates the wedge), default
  byte-identical, capture minimal. The "lift to musical form" direction is the
  TRAP, recorded so it isn't re-litigated: a `law: random` enum value would NOT
  determine the write stream (the chaos generator would be hidden per-member
  composer mechanism = the §8 disease proper); putting the generator arithmetic
  in USF = Pole B. `dual_generator_steps` derivability was checked and is genuinely
  unavailable (Taurus_02's inst-6 raws land past the table end in the wavectrl
  region, whose layout is not in USF for this member) → justified-minimal C2-class
  capture. Lower-stakes siblings flagged same review — **RESOLVED 2026-07-09**
  (composer→extract relocation, `docs/dmc_composer_to_extract_plan.md` Phase A):
  the params `offtable_redirect='0'` (a serialized bit describing the ORIG's memory
  geometry — config fields must never describe HVSC layout) and `sectpos_shadow`
  (probe-result transport) were DELETED from the USF and replaced by a per-read
  behavioral flag on `offtable_freq`: `live(off,note,lo,hi)` marks a read that
  sonifies a live-varying value vs `at(...)` for a fixed byte. Extract stamps it
  (`canon_geom ∧ idx ∈ composer_asm.offtable_live_idx()`); the composer re-derives
  its member-global redirect boolean as `not (any static read at a live-served idx)`
  — the non-canon member being the only one that must serve every read statically,
  uniquely detectable as an `at(...)` read at a live position. Byte-identical rebuild
  across all 5401 family-1 members (golden `tools/golden_sid_diff.py`).

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
- **Status:** `canonical` (FC standard + DMC v5 + GoatTracker V1, all migrated to
  `offtable_freq`). Schema + USF I/O shared; the composer reconstruction is per-composer
  (FC `composer_asm._offtable_window` · v5 `composer_v5` · GT V1 `_Tables` freqlo/freqhi
  rebuild) → a Move-1 factor-candidate. Distinct from **C2** (off-table PROGRAM tables;
  this is off-table DATA lookup).
- **TRANSITION reads — deferred note-init / soft notes (2026-07-06, Bladeswede,
  DMC v4):** the reach model must enumerate more than (instrument's offsets ×
  that instrument's row notes). Notes are FETCHED on one play() call (curnote +
  base update) but note-init (wave restart) can be DEFERRED to a later call —
  an intervening wave-step call runs the OLD instrument's program with the NEW
  curnote; and a SOFT ($7C) note skips note-init entirely, so the old program
  runs for the note's whole duration. Off-table idx = old-program offset + new
  note (Bladeswede: noise-arp off 52 + soft note 47 = idx 99 → hi read $170A =
  V1 track-ptr hi, runtime $1B vs file-image $00). Extract fix: track the
  RUNNING instrument per voice during enumeration; for every note row also
  add_note(note, running); soft rows don't update `running`. The existing
  post-init correction then captures init-set state bytes.
- **SUBTUNE-AWARE post-init correction (2026-07-08, Cool_Musax, DMC v4):** the
  off-table byte can be PER-SUBTUNE init-written state (track-ptr slots
  $1707-$170C are set from the tune record at init — constant within a subtune,
  different across subtunes), and the post-init capture sampled only the
  DEFAULT start song (Cool_Musax sub 1: off 60 + note 36 = idx 96 → $1707 =
  V1 track-ptr lo, start-song $F8 vs reading-song $17). Extract fix: the reach
  model records WHICH songs reach each `(inst, off, note)` record
  (`m.offtable_songs`); `_correct_offtable_postinit` samples `_postinit_values`
  per reaching subtune (`--subtune`) and uses a record's reaching-song value
  only when every reaching song was sampled and they AGREE; any ambiguity
  (idle records carry no attribution, disagreement, missing sample) falls back
  to the start-song sample = the old behavior. Regression-safe by construction:
  a FULL member's served value already matched every subtune's stream, so the
  reaching-subtune capture returns the same value → byte-identical build.
- **GT V1 consumer (2026-06-30, commit 8a743d1):** `extract/to_usf._offtable_freq` —
  per-inst reachable reads (wave/arp/**bare-note** idx≥96, via a cross-pattern
  instrument-carry walk; the bare-note read `freq[note]` for note+transpose≥96 was the
  key case the FC/DMC players don't have). Encoded `(idx,0,lo,hi)` (GT's freq table is
  global → idx is the off-table note index). **TWO GT-V1-specific lessons:** (1) the
  composer must PAD its internal freqlo/freqhi to a stable ≥128 size — a per-tune-varying
  array size shifts the BSS, changes page-crossing branch cycles, and drifts the song-end
  capture boundary by a partial frame (a `sig=len` flip, Trap B — NOT a value divergence;
  diffing a pre-migration baseline was what isolated it). (2) The migration here is
  CORRECTNESS-NEUTRAL ML-cleanliness, NOT a convergence fix: GT V1 reads cap at idx≤~110
  (note≤93 + offset), the old 128-window already covered them, so 0 FULL-count change
  (164→164, 0 status changes vs baseline). Verify before assuming an off-table read is
  the divergence cause (the GT V1 deep partials looked like C6 but are wrong-NOTE).
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
  field removal is the pending cleanup (`deprecated/old_docs/offtable_freq_plan.md` Phase 7).
- **NON-CANON STATE GEOMETRY (2026-07-06, DMC v4, Viiskyt_vuotta_humppaa +3 Finn;
  status: logged):** every LIVE-serving of a window position (the
  DMC_OFFTABLE_STATE redirect rows, the sectpos shadow, the co-located
  sidoff/fbit/fmask/spd/mvol block at window pos 6..16, the event-driven
  capture's memwatch addresses) identifies window idx with canon state vars via
  the CANON table→state geometry — invariant under whole-image relocation but
  WRONG for variant builds that moved the state block (the page-3 builds:
  Bakewell/Finn/Stix/Aomeba/Ed keep per-voice state at $03xx; freq tables shift
  −$13). There, idx 130 "sectpos" is an opcode byte, idx 208 "cvram" is an INY,
  window pos 16 "live mvol" is a static $07 — all STATIC, exactly what the
  post-init static capture already serves, and every live redirect/co-location
  SHADOWS the correct static value. FIX: probe the geometry statically per
  member (C19 method — the canon player's `DEC dur,x` must exist at
  freq_hi + ($173B−$16A7); fail-open on a stray match) → non-canon members get
  `offtable_redirect=0` (map emptied, window fully static, live structs emitted
  outside it, sectpos shadow + event-driven capture off). Real-probe census:
  10 carriers / 1212 stored-offtable members; +4 FULL, 0 regressions.
  When adding ANY new live-serving of a window position, gate it on the same
  probe.

### C5 — Detection ≠ FULL
- **Canonical:** accepting a member past the factory's detection gate just moves
  it to its NEXT failure mode (cia / partial / error) — it is NOT a FULL. The
  verify PARTIALS, not the detect-rejects, are the FULL bottleneck.
- **Status:** 📋 methodology — see [[reference_divergence_census]],
  `tools/divergence_census.py`.
- **Boundary:** any wide-family residue triage.
- **Consumers:** DMC v5 reloc@$10E5 (2026-06-18: cleared the reloc gate → 32
  surfaced as cia_multispeed, only 5 reached FULL).

### C8 — A de-fused per-entity program pool overflows the engine's byte index
- **Canonical:** the engine stores N programs in one table indexed by a single
  byte (position ≤ 255); the composer emits a SEPARATE copy per entity, so a
  member with many same-shape entities inflates the pool past 255 → hard build
  error. **Dedup identical programs** (key on the exact emitted bytes + loop):
  identical entities point at one pooled copy. Byte-identical for the write
  stream — each entity re-inits its position to its start per use and reads the
  same byte sequence. This is what the original packer does (programs share).
- **Status:** canonicalized ≥2× (DMC v4 wave pool 2026-06-25; DMC v5 wave pool
  2026-07-01).
- **Sibling — dedup KEY excludes a reachability artifact (2026-07-10, Balloonacy
  compilation instrument pool, C31):** the overflowing pool is the 28-inst
  5-bit id cap of a merged compilation. Two instruments identical but for
  `offtable_freq` (a C6 which-notes-played artifact, NOT intrinsic content) are
  ONE instrument — dedup on all fields EXCEPT offtable_freq and carry the UNION
  of records (collision → refuse). Same lesson as the base entry (share what the
  packer shares), applied to the DEDUP KEY: exclude non-intrinsic fields so
  behaviorally-identical entities collapse. See C31 for detail.
- **Sibling instance (capacity of a COMPOSER-side stream index, 2026-07-03):**
  when the overflowing index is the composer's OWN runtime cursor (not a pooled
  table) — e.g. the DMC track stream growing past 255 bytes once entries went
  2→3 bytes — dedup doesn't apply; WIDEN the cursor to a 16-bit running pointer
  and emit jump targets as assembler label arithmetic (`.byt $FF, <(lbl+n*3),
  >(lbl+n*3)`). Audit every 8-bit index whenever a stride/record grows.
- **Boundary:** dedup is pure packing (zero write-stream change) ONLY when the
  pool layout is position-INDEPENDENT — i.e. the loop marker is RELATIVE (V4's
  `$90 + n - loop`, identical bytes at any position). When the marker encodes an
  ABSOLUTE target (V5's `$90, s+loop`), moving a program rewrites its marker and
  dedup is NOT guaranteed byte-identical: it perturbed a currently-FULL member
  (CreaMD Ambient, freq divergence — the de-fusion adjacency coupling the pulse
  table also shows). Fix = OVERFLOW-GATE the dedup (share only when the un-shared
  pool > 256), which is zero-regression BY CONSTRUCTION: it only ever touches
  members that can't build un-shared (all currently non-FULL), so no working
  member changes. **SUFFIX/OVERLAP packing is REFUTED as the next tier (2026-07-01,
  `tmp/measure_suffix_overlap.py`):** measured on the DMC v5 family-4 pulse-overflow
  members, suffix-containment AND greedy shortest-common-superstring add essentially
  NOTHING over identical-dedup (e.g. Deep_Acid 346→346, Speed_Biker 306→305; 2/10 fit).
  REASON: each program is captured as a SEPARATE SweepEnvelope with its START value
  PREPENDED to its phases; in the ORIGINAL shared table a program's start is just a
  position that ALSO serves as another program's phase byte (start+phases overlap), but
  the un-fused capture puts a distinct start (a PW value) in front of each phase list, so
  the sequences don't share suffixes even when the programs walk the same table. The
  engine's compactness IS the shared table — packing the separate captures can't recover
  it. **The real next tier is EMIT-AND-WALK the shared static table** (emit the 256-entry
  m.pulse/filter once, point each instrument's pulse_ptr/filter_ptr into it, like the
  engine) — fits by construction (256 positions = the byte pointer's range) but is a
  representation change, not a packing tweak. Deferred (bigger architectural change);
  the 71 family-4 `pulse/filter_table_overflow` members are current residue.
- **Consumers:** DMC v4 `composer_asm.py` wave pool (`add_prog` dedup cache,
  commit c73a1d0 — 40 overflow members → 37 build, +5 FULL). DMC v5
  `from_usf.py add_wave` (overflow-gated, 2026-07-01 — 17/19 overflow members
  build, +5 FULL, 0 regression). DMC v5 `from_usf.py` PULSE pool (`add_pulse`
  overflow-gated dedup, 2026-07-01) — a correctly-captured OFF-TABLE pulse program
  is large (~97 B, a one-shot ramp truncated at `_PHASE_CAP`), so many instruments
  over few programs overflow un-shared (Jupiter41: 16 insts / 5 programs = 356 B →
  209 B shared). Paired with the `_capture_env(truncate_on_cap)` fix (keep the
  off-table prefix instead of the family-4-incorrect 16-bit fallback), this landed
  **the first family-4 FULL (Jupiter41)**, 0 family-3 regression.

### C9 — A runtime parameter py65 can't read → measure it from the writelog
- **Canonical:** when a build-time parameter is set by code py65 can't execute
  (init hangs, the value is programmed in an IRQ handler, or an unsupported
  opcode aborts the trace), DON'T reject the member — MEASURE the parameter from
  the GROUND-TRUTH writelog (libsidplayfp runs the real CPU). Sibling of C4
  (localize a divergence via memwatch); both replace a py65 limitation with a
  libsidplayfp observation.
- **Status:** recurring (DMC v4 CIA multispeed rate 2026-06-25; single-speed
  DEFAULT latch 2026-07-06).
- **Boundary:** works when the parameter is OBSERVABLE in the write timing /
  memory. CIA multispeed rate: count play()s per PAL frame from
  `--writelog-per-irq --per-irq-debug` (`nentries`/frame, `base`=abs PHI1
  clock), round N to the integer factor, latch = 19656/N − 1 (the exact
  canonical $2663=2x / $1331=4x). The rounding makes it robust (N within 0.01).
- **NOTE — the SINGLE-SPEED CIA default latch (2026-07-06, Phobos/Crazy_Mix
  +3 FULL):** a PSID speed-bit tune whose init programs NO timer is still a
  CIA tune — it runs at the PSID environment's DEFAULT latch $4025 (16422
  cycles, ~60 Hz). The old "no readable latch → single-speed fallback"
  blanket built it as a vblank 50 Hz tune: the write SEQUENCE matches as a
  perfect prefix but under-runs ~20% = a guaranteed length partial (the
  Trap-C-looking flat pos-0 divergence is the CIA init-phase artifact —
  localize per-IRQ). Fix: when N rounds to <2, measure the exact
  entry-to-entry period (median of entry0 deltas; a 2-entry frame doubles
  one delta, the median discards it) and return $4025 iff it matches (±2).
  A 50 Hz-ish single-speed CIA rate is left 0 (a vblank build is
  equivalent). Regression-safe by construction: any member this changes was
  rate-wrong (never FULL). Also: call the writelog fallback for
  CANONICAL-play members (play == base+3), not only wrappers — the canon
  path never measured them.
- **Consumers:** DMC v4 `factory._cia_period_from_writelog` (commit 2114f21 —
  67 py65-unreadable cia_multispeed members → 56 build, +20 FULL; default
  latch $4025: Crazy_Mix/Love_Song/Magnum_Theme 2026-07-06).

### C10 — Chip-global ($D415-$D418) automation that varies during a song (master vol + filter)
- **The DOF:** master volume + filter cutoff/res/mode/route — chip-GLOBAL state
  (one per SID, not per voice), changing across the song. Distinct from C1, which
  is the *per-instrument* swept contour; this is the *whole-subtune* global track.
- **Canonical — choose by MUSICAL STRUCTURE, not by engine:**
  - **PARAMETRIC** (mechanism + a few knobs; the engine GENERATES the per-frame
    values) when a formula/table drives it: `MasterVolConfig` (fade formula, e.g.
    Confuzion `clamp(BASE − voice1_orderpos)`), `master_vol_every_frame`/`_every_note`
    (re-assert a fixed value; DMC `master_vol_reassert_filter_tail` re-asserts `$D418 = filter-mode
    | mvol` every frame with the mode tracked from filter note-inits — C19 round 65),
    `FilterProgConfig`/`filter_programs` + DMC
    `default_filter` + instrument `filter_env` (filter cutoff-ENVELOPE programs ≈
    C1 `SweepEnvelope`), `init.sid { master_vol, filter{…} }` (one-time priming).
    Values are derived at runtime, never enumerated.
  - **EXPLICIT** per-step event list — `MusicSubtune.global_track` = list of
    `GlobalEvent(step, dyn?/cutoff?/res?/mode?/route?)`, NAMED musical fields
    decomposed from the registers ($D418=mode<<4|dyn, $D417=res<<4|route,
    $D416=cutoff), running-state (emit a field only when it changes) — ONLY when
    the automation is **arbitrary authored data with no recoverable mechanism**:
    the trace-lift case (basic_program hand-POKEs, e.g. Deutschlandlied
    `vol 0F→08→06`). The composer re-packs the exact register bytes; write ORDER
    comes from the per-tune template.
  - This is the SAME explicit-vs-parametric axis used one level up at per-VOICE
    scope: `NoteRow` (explicit melody) vs `VibratoConfig`/`ArpConfig` (parametric
    per-frame contour). We don't store vibrato-bent freqs as NoteRows; likewise
    don't store a formula-driven fade as a `dyn` event list.
- **ANTI-PATTERN (do NOT do this):** converting a parametric form to `global_track`
  (e.g. "make all FULL SIDs use the global track"). It is the C7 opaque/dump
  direction — explodes file size (Confuzion: 2 knobs → ~hundreds of `at N dyn=X`
  rows), discards the musical mechanism, and degrades ML-legibility. The
  representation must track the structure, not the engine.
- **Status:** logged (basic_program `global_track` added 2026-06-27, commit cd81a61;
  the parametric forms predate it).
- **Boundary / Move-1 convergence TODO:** (1) `global_track` is currently
  basic_program-only but is a GENERIC primitive — make it SHARED for any engine
  with genuinely-arbitrary global automation. (2) The DUAL: basic_program emits
  `global_track` explicitly even when the captured sequence IS parametric
  (Moog_Swing cutoff = a sawtooth sweep stored as 190 explicit events) — a
  sweep-detecting trace-lift could lift those to a filter-program (C1). (3) The
  register family now has N coexisting representations (`global_track`,
  `MasterVolConfig`, `master_vol_every_*`, `FilterProgConfig`, `default_filter`,
  `filter_env`, `init.sid.filter`) splitting along parametric×explicit ×
  global×per-instrument × init×runtime — `/uready-review` should reconcile. The
  filter-program parametric forks are already tracked under C1's divergent-forms note.
- **Consumers:** basic_program `global_track` (224 FULL); `MasterVolConfig`
  (Hubbard Confuzion/TOAS); `FilterProgConfig` (FC Jarre_2); `default_filter` /
  `filter_env` (DMC v5); `filter_mod` (DMC v4, Ed/Core_of_Acid — see note
  below). See C1 (per-instrument sweep) and C7 (opaque-dump lens).
- **NOTE (2026-07-06, DMC v4 `filter_mod` — Ed/Core_of_Acid, sole corpus
  carrier):** a play-vector wrapper streams an init-GENERATED 513-byte
  triangle table into the filter DEFINITION's init/stop cutoff bytes via two
  SMC roving pointers (+1/frame, wrap, +16-byte phase offset); the engine
  samples both at filter note-init, so every filter note starts/freezes at
  the LFO's current position. Landed as the PARAMETRIC form: USF
  `filter_mod { prog N: start= init_phase= stop_phase= step (d,f)... }`
  (reuses the `fp_step` piecewise-rate token = C1's contour shape; the two
  taps are phase offsets of ONE contour), factory `_filter_mod_probe`
  (C19-style static opcode probe of the wrapper + automaton; contour bytes
  read from post-init RAM and delta-RLE'd — NOT a byte dump), composer =
  two sweep walkers feeding `fdinit+slot`/`fdstop+slot` each play() call.
  Default byte-identical. Recipe transfers to any "engine data table
  rewritten per frame by a play wrapper" hack: probe wrapper → lift the
  written sequence as a parametric contour + tap phases.

### C11 — Engine indexes a table via an 8-bit register → the offset WRAPS mod 256

> **Entry map (this entry grew into two clusters — navigate, don't skim):**
> **(a) 8-bit wrap in EXTRACTION arithmetic** — bug class + canonical `&0xFF`
> fix, the add-chain-carry refinement, the TELL, wrap occurrences (glide
> targets, wave-walk underflow, chained marker, note+transpose, vibdepth).
> **(b) OFF-TABLE LIVE-REDIRECT methodology** (overlaps C6) — all-read-sites
> rule, wavepos layout-preserving pool, wjmp-chase shadow, durrel, var-naming,
> measure-regressions methodology, init-cleared seeding, the a/b/c
> unexposed-tracking-var diagnostic, shared-scratch shadowing, cache-var
> materialization, derivable "positional" counters, sparse-var seeding,
> event-driven capture — plus two HARD BOUNDARIES (dynamic work-RAM;
> off-table glide targets). Candidate for a lossless split at a future
> `/uready-review` (many `[ledger C11]` back-refs in [[project_dmc]] would
> need repointing — do not split casually).

- **The bug class:** the player reaches a record/table entry with a 6502 INDEX
  register (`LDA base,Y` / `,X`), and the index is computed as `entry# * stride`.
  The register is 8-BIT, so once `entry# * stride >= 256` the access WRAPS
  (`(entry# * stride) & 0xFF`) — a tightly-packed table deliberately reuses its
  low bytes for high entries. A by-hand extractor that reads `mem[base +
  entry#*stride]` with FULL-WIDTH arithmetic reads PAST the table (into whatever
  follows) and lifts garbage for the high entries.
- **Canonical fix:** mirror the register width — `off = (entry# * stride) & 0xFF`
  (or the engine's actual index width). SAFE BY CONSTRUCTION: entries below the
  wrap threshold are byte-identical (no change), so it can only fix, never
  regress. ALWAYS read the indexing instruction (is it `,Y`/`,X` 8-bit, or a
  16-bit pointer?) before trusting a `base + i*stride` extract.
- **⚠️ REFINEMENT (2026-07-03, DMC family-1 round 16):** `& 0xFF` models the
  wrap ONLY when the engine multiplies in one step. When the offset is an ADD
  CHAIN with a single CLC (DMC v4 `$1213`: CLC/ASL×3/ADC #n ×3), an
  INTERMEDIATE ADC's carry-out feeds the NEXT add — the result is NOT
  `(n*stride) & 0xFF` (DMC iid 26: chain gives $1F, mod-256 gives $1E; every
  iid ≥ 26 is +1, ≥ 52 +2). EMULATE THE EXACT INSTRUCTION SEQUENCE, don't
  algebraize it. The mod-256 model validated on iid 24-25 where the two
  coincide — validate a wrap model on an entry PAST the first intermediate
  carry, not just past the wrap threshold.
- **TELL / how it presents:** the orig appears to read "out-of-range / garbage"
  data and the SID seems "broken" — but a real packer does NOT emit broken SIDs.
  When a trace shows an out-of-range/garbage read, SUSPECT THE EXTRACTOR (8-bit
  wrap / wrong base / wrong stride) FIRST, not the data. (DMC user-caught,
  2026-06-27.) Sibling of [[feedback_6502_mindset]]: all bugs are pointer errors;
  think in exact byte offsets — including index-register width.
- **Status:** logged (DMC v4 instrument record offset `#*11 & 0xFF`, commit
  3cae4fd; instr >= 24 → ~6% of partials recovered, 0 regression). ALSO DMC v5
  glide/slide targets (commit 65ac05f, +27): targets are stored TRANSPOSE-RELATIVE
  (raw $FE), player does `(target+transpose)&$FF` → usually wraps back in-table; the
  extractor's stale `>119` reject (`note_out_of_range`) predated 2-digit-octave
  off-table pitches — raising it to 255 round-trips the byte losslessly. Same lesson:
  the orig "reads garbage"/the byte looks out-of-range, but it's the WRAP — fix the
  extractor, not the data. ALSO DMC v4 wave-walk jump-back UNDERFLOW (family-1
  round 18, +20 FULL 0 regr): the wave marker hop is an 8-bit SBC — a back-distance
  larger than the position wraps to a HIGH window position (Cool_Compo_Tune: marker
  $FF at pos $26 → $B7); `_slice_wave`'s in-table path used full-width arithmetic
  (a NEGATIVE Python slice = silently read the extended table's tail; the pre-chain
  variant RAISED wave_marker_chain = 13 false detect-rejects). Fix routes both
  underflow cases to `_resolve_wave_chain` (the existing mod-256 walk simulator) —
  canonical-form compliant: only previously-wrong/refused paths change.
  ALSO DMC v4 CHAINED marker in the pre-start loop region (family-1 round 29,
  Tichelmann_03 +1 FULL 0 regr): `_slice_wave`'s loop-target-before-start branch
  concatenated `ctrl_tab[loop_pos:start]` UNSCANNED — a marker there (inst 12:
  `$14,$14,$14,$94`; $94 hops to $91 which hops to the settled $41/freq $00 hold
  step) was emitted as a literal wave step. Same canonical fix: gate on
  `any(b >= 0x90)` in the copied region → delegate to `_resolve_wave_chain`.
  ALSO DMC v4 NOTE+TRANSPOSE off-table read (family-1 round 66, Journey +1 FULL
  +5 siblings, 0 regr): note-init adds the transpose with an 8-bit ADC ($11A3),
  so a NEGATIVE transpose wraps a LOW note past the 96-entry freq/vibdepth tables
  (note 0 + tr −4 → curnote $FC). The reach model `_assign_offtable_freq.add_note`
  gated on the RAW SIGNED sum (`if n > 95` with n = note+tr = −4) → missed every
  negative-transpose off-table read. Canonical fix: `n &= 0xFF` at entry (mirror
  the 8-bit Y index); notes already in 0..255 unchanged → regression-safe.
  **⚠️ REFINEMENT — capture VIBDEPTH but NOT FREQ for a WRAP:** the off-table
  VIBDEPTH read (the drum vibrato step) lands on STATIC instr-record bytes →
  representable, always capture (this is what Journey needs). The off-table FREQ
  read of a wrap (note 0 − k → 250..255, the DMC drum/silent idiom) lands on
  freq-table-adjacent PER-SUBTUNE engine state (NOT statically representable in
  one window; last-writer-wins picks a wrong subtune's value) AND its base freq
  is drum-overridden or $0000 — so a static capture REGRESSES (Other_Side FULL→
  partial, caught in the flip-set census: flo+254 = $00 in subtune-0 but $5E in
  inst-6's reaching subtune). Gate the freq record on `if not wrapped`; the
  pre-fix default (no capture) is correct for wraps. See also C6 (off-table FREQ
  is representable only when it lands on STATIC bytes; per-subtune/dynamic is
  residue). The vibdepth CODE-OVERLAP HEAD (indices 3,4 = the vstep-store operand,
  which relocates for page-3/relocated-state builds — $03BC vs canonical $1792)
  is the SAME class one level up: a note reading vibdepth idx 0-5 gets a build-
  specific byte; capture the member's actual head byte where it differs from
  the canonical VIBDEPTH constant, composer overrides `_vd[note]` in place (no
  table-size change → regression-safe). The head byte is a STATE-ADDRESS operand
  = C7-(b) state-as-data — flag for `/uready-review` (572 f1 members have a
  relocated head; flip-set = the readers). **GENERALIZED to IN-TABLE musical
  deviations (2026-07-10, DMC f1 round 69, Enter/Bax +1 FULL 0 regr):** the head
  was the special case, not the whole class. The vibdepth table is per-member
  MUSICAL content — a note's vibrato depth can be authored non-canonically at ANY
  index 0-95, not only the code-overlap head. Enter's `$1888[44]=$10` vs the
  canonical player's $20 (a note that vibrates half as deep) made orig vibrato
  step $10 vs rebuild $20 (2×). FIX: generalize the head gate `n<6 and mem!=
  VIBDEPTH[n]` → `n<96 and mem!=VIBDEPTH[n]` in `_assign_offtable_freq.add_note`
  — capture the member's actual byte wherever a REACHABLE note's vibdepth differs
  from canonical; same in-place composer override. Regression-safe by construction
  (canonical members deviate nowhere they play → byte-identical; a FULL with an
  ACTIVE-vibrato deviation can't exist, an INACTIVE one is inert).
- **Boundary / watch-list:** the SAME class applies to ANY 8-bit-indexed engine
  table — e.g. the DMC wave POSITION ($177A is 8-bit, so a wave program crossing
  $FF wraps to wctab[0]; `_slice_wave` reads linearly past it — a candidate
  unfixed instance). Audit other `mem[base + i*stride]` extracts for the same.
- **ALL read SITES must honor the live redirect, not just one (2026-07-10, DMC
  family-1 round 68, Secret_Loser +1 FULL 0 regr).** An off-table freq index has
  THREE distinct 6502 read sites in the DMC player: the WAVE-STEP (`wftab[pos]+
  curnote`), the NOTE-FETCH base reload (`freqlo[curnote]` at note load), and the
  GLIDE-ARRIVAL base reload (`freqlo[target]`). The composer's live redirect
  (`_gen_offtable_redirect` over `DMC_OFFTABLE_STATE`) served only the wave step;
  the two BASE-reload sites read the raw table → a captured `LIVE`-flagged record
  (Secret_Loser: curnote $F4 → $173B = V1's live duration counter, sonified as V3
  base freq) resolved to the STALE static window byte ($07 file-image) instead of
  the live counter ($06). FIX: factor a shared `reload_base` subroutine running
  the SAME redirect, `jsr`-ed from both base-reload sites. Regression-safe by the
  wave-step's own invariant (the map's vars track byte-identically; in-table /
  unmapped indices fall through to the identical `lda freqlo,y`); affected-set
  census 17/17 FULLs hold + 5 CIA FULLs (added-`jsr` latch check, C25) hold.
  LESSON: a captured `LIVE` record is only reproduced if the READING site honors
  it — audit every read site of a redirected quantity, not just the first one fixed.
- **~~HARD BOUNDARY~~ → RESOLVED — off-table reads that sonify the ABSOLUTE
  wave position (2026-06-28 Object_of_Art blocked; 2026-07-06 Distant_Echoes
  resolved, +5 FULL 0 regr).** When a wave program's arp index runs off-table
  and lands on `$177A` (wavepos itself), the orig plays the absolute wave
  POSITION as a frequency. The un-gated redirect row was net-NEGATIVE (0
  recoveries + 1 FULL regression): our composer re-packs the wave pool with
  its own offsets (`iwst` — idle-first + dedup + instrument-order), so our
  wavepos diverges from the orig's (Object_of_Art V2/V3 = orig+5).
  **CANONICAL FIX — layout-preserving pool packing from arrangement (the §8
  sectpos playbook applied to the wave table):** the DMC wave table is an
  EDITOR-SHARED table the composer typed positions into (instrument byte 9)
  — carry each instrument's editor wave-table position as USF
  `Instrument.wave_table_pos` (emitted only for members whose off-table
  reads hit fhi idx 211-213), and the composer PLACES its pool at those
  positions instead of appending+dedup — then its `wavepos,x` EQUALS orig
  `$177A,x` at every settled moment (marker hops included: verbatim slices
  carry identical marker bytes/distances) and a plain gated redirect row
  (`DMC_WAVEPOS_ROW`) serves the read live. GATE (extract
  `_wave_layout_verbatim`): canon geometry (C6 note) + idle walk and EVERY
  instrument's program a verbatim contiguous slice ending on the orig marker
  `$90+(n-loop)`; a wave_start ON the program's own end marker (the "start
  at the loop marker" editor idiom) is admitted with the chased first-step
  position, EXCEPT when the member also reads the wjmp window (the skipped
  transient chase writes $171F). Non-verbatim (chain-resolved / off-table /
  runaway) programs stay honest residue. Default byte-identical (MD5
  old-vs-new, Aktarus); 30-member exposure sweep: 12 FULLs hold, +5 FULL
  (Distant_Echoes/No_Name_Remix/In_die_Dunkelheit/Das_Remix/II-V3), 2
  partials moved LATER, 0 regressions.
- **WJMP-CHASE SHADOW — the "reads wjmp with a chasing instrument" carve-out
  above is now RESOLVED independently of the wavepos layout (2026-07-08,
  High_Tech +1 FULL, 0 regr; USF `Instrument.wave_start_on_marker`).** A
  member reads the wjmp window ($171F, fhi idx 120 / flo idx 216) AND has an
  instrument the editor started ON its own loop marker ($90+n, loop 0 — "start
  at the loop marker"). The orig chases that marker back n on the FIRST read
  every note-init, storing $171F=n; the composer packs the SETTLED program
  (skips the transient chase), so it misses exactly that one write — while
  every SETTLED frame after still hops naturally (pinned at the marker),
  writing wjmp=n. So the ONLY divergence is the note-init frame, and ONLY when
  a wjmp read lands on it before another voice overwrites $171F (High_Tech: V1
  inst-7 note-init frame, V2 doesn't overwrite, V3 reads idx-120=$171F).
  FIX (CORE TENET — reproduce the WRITE not the mechanism, layout-independent):
  extract detects own-end-marker chasers (gated on a wjmp read, canon geom) →
  per-instrument `wave_start_on_marker`; composer re-asserts `wjmp = n` at
  note-init (`iwchase` table + `ni_chase`), emitted only when some instrument
  chases. REGRESSION-SAFE BY CONSTRUCTION: it re-asserts a write the orig
  ALWAYS makes at that note-init, observable only where the orig itself
  diverged — a FULL member has no such read, so its stream is unchanged (6
  random FULLs + all portfolio byte-identical; full regression 0-regr).
  Distinct from wavepos layout (`_wave_layout_verbatim` / `wave_table_pos`) —
  that fixes the wavepos read via pool placement; this fixes the wjmp read via
  a value re-assert and needs NO layout match. Exposure: 4 f1 partial carriers
  (High_Tech FULL; Chwat + Solar_Energy first-div resolved -> deeper blocker;
  King_of_Earth unchanged — its wjmp read diverges for a different, non-chase
  reason = honest residue).
- **Redirect-map consumer — durrel (2026-07-03, +26 FULL f1, 0 attributable
  regressions):** $173E duration-reload mapped as a live shadow; works because
  every composer EVENT's stored duration == the orig's reload at that row BY
  CONSTRUCTION (each orig row reloads its counter from $173E, so row duration
  ≡ current reload). Priming from the file-image/post-init leftover, emitted
  only for window-reading members. SCHEMA HOME: the pre-first-event leftover
  is §4.5 engine-state PRIMING (trichotomy report) — a TYPED
  `InitVoice.dur_reload` field alongside `guard`, NOT a params scalar (the
  first landing used `durrel_init*` params citing the hardrestart_test_init precedent;
  re-reading the principle doc flagged that as the "cite a precedent to defend
  the easy choice" drift-tell and it was moved to the typed init block, 46
  builds byte-identical → provably neutral). EXONERATION LESSON: the one 'regression'
  in the 66-member exposure gate (Sweet_Honey) was a PRE-EXISTING latent —
  attribute by rebuilding under the pre-change committed tree BEFORE blaming
  the new map row (stash → build → verify; same first-divergence = exonerated).
- **Redirect-map var-NAMING must match the value the ORIG address holds
  (2026-07-04, +13 FULL f1+f2, 0 regr):** a composer variable can be
  self-consistently MIS-NAMED — DMC's `cpwmin`/`cpwmax` hold PW bound A /
  bound B (extract sets min_hi=bound_a, max_hi=bound_b), and the PWM sweep
  set+compare both use the swapped names, so normal operation is correct and
  the members were FULL. But the off-table redirect maps orig $1756 (bound A)
  → var `cpwmax`, which holds bound B ($0B = A EOR $0F) → mine=$0B where
  orig=$04. TELL: a whole cluster whose (orig,mine) values are EOR-$0F
  complements ($04↔$0B) at an early/mid freq-hi read = a redirect entry
  pointing at the complement var. Fix = point each orig ADDRESS at the var
  HOLDING THAT ADDRESS'S VALUE, not the var whose NAME matches the disasm
  label. This also cured a pre-existing Flyt/Yoko palimpsest cluster (the
  latent the full closeout surfaced). Whenever a redirect entry names a var,
  verify the var's RUNTIME VALUE equals the orig address's, not just that the
  names rhyme.
- **METHODOLOGY — the C6 off-table redirect map is NOT free; measure regressions.**
  Adding a `(addr, var, n)` entry can REGRESS a FULL whose off-table read happened
  to match via the STATIC freq-table overrun byte (the value the read got before
  the redirect). Always run a FULL-songlength transfer test (partials for
  recovery + a FULL sample for regression) before committing a new map entry;
  otrk/wnote were lucky on small samples. Reading $171C/$177A regressed
  Humppa_Demo (1/33 FULLs). **UPDATE (round 22): $171C fcut ALONE is safe and
  IS now mapped (+~6, 0/150-FULL regression).** The old regression was fcut
  BUNDLED with wavepos $177A — fcut tracks the $D416 write stream by
  construction, so live fcut == orig $171C (verified King_of_Earth $20==$20);
  Humppa's divergence is byte-IDENTICAL with/without the fcut row (not an fcut
  read), and Object_of_Art (the wavepos member) merely moves its first-div
  later. LESSON: when a caution names TWO co-mapped addresses, re-test them
  SEPARATELY — one may be the sole culprit. Still NOT mapped: $1720 fclaim
  (rejected f2) + $1721/$1722 (no composer cache var — read inline).
- **INIT-CLEARED STATE seeds the FIRST event, NOT the file image (DMC v4 round 54,
  Klepkomania +3 FULL, 0 regr).** A first-event parameter read from per-voice
  ENGINE STATE that INIT CLEARS must be seeded from the POST-INIT (cleared) value,
  never the file-image leftover and never a hardcoded default. DMC's note-load
  reads the duration RELOAD $173E,x; init's $1718-$179D wipe zeros $173E-$1740, so
  a first note with NO preceding sector $80-$BF duration command plays for reload
  0 (a held 256-tick note, $173B DECs 0->$FF) — the `_Sticky` extract default of 1
  gave it a too-short life, dropping one frame at the $FE terminator (the whole
  free-running PW-sweep phase then shifts). Fix: `_Sticky` default dur 1->0.
  REGRESSION-SAFE BY CONSTRUCTION: any voice whose first row is preceded by a
  duration command has st.dur OVERWRITTEN -> byte-identical (FULL-side flip-set 0
  of 1200 changed build). TELL / how it presents: a per-play "voice drops one
  update at the track/pattern boundary" (counts off by exactly one voice-block,
  the voice's own value stream identical). TRAP: the file-image byte ($173E=8),
  the old default 1, AND the libsidplayfp runtime memwatch ($173E=6, a
  py65/libsidplayfp during-play divergence) all mislead — only py65 POST-INIT +
  an empirical duration-sweep give the true value 0. The durrel_init capture's
  "orig init never writes $173E" comment is factually wrong (init clears it); the
  round-31 durrel priming should also be post-init but was left untouched here
  (it's gated + only surfaces on a $173E off-table read before the first note).
- **HARD BOUNDARY — off-table reads sonifying DYNAMIC work-RAM (DMC family-2 freq
  tail, 2026-06-29).** 429/533 family-2 partials diverge on an off-table read; the
  dominant case (Death_Comes V2 first note, arp 121 → $1720) sonifies the FILTER
  CLAIM FLAG ($1720: $00 at frame start, voice+1 on claim). Two clean fixes both
  REJECTED on the 0-regression rule — record so they're not re-tried:
  (1) *post-init value instead of file image* (`_postinit_values` earliest
  fallback for varying bytes): +7 family-2 but −2 family-1 (Fear reads its byte
  DEEP at frame 442 where it = the file image; no static discriminator between
  "read early = init value" and "read deep = file image").
  (2) *map $1720 → the composer's live `fclaim`*: +0 recovery, −1 family-1
  (Long_Night) — the composer's `fclaim` doesn't track the orig's $1720 at the
  READ MOMENT (voice/claim ordering differs). So live-state redirect needs
  byte-IDENTICAL state evolution, which a re-implemented engine rarely has.
  The only clean lever is the earliest-value fix as a VERIFY-FALLBACK (try
  file-image default, retry earliest for partials, accept iff FULL → +7, 0-regr
  by construction; deferred — re-extract-retry plumbing not worth +7). The real
  fix is an EVENT-DRIVEN capture (record the ACTUAL value the orig reads at the
  read frame via memwatch-on-write base-hi, like `tmp/capturable.py`) — correct by
  construction, recovers the value-consistent reads. Family-2 freq tail accepted
  as the hard residue (matches family-1's freq-floor "no single lever").
- **HARD BOUNDARY — a glide/slide TARGET that is an off-table "note" terminates
  the sweep on a DYNAMIC scratch byte (2026-07-04, Plasmachaos/Calypso).** A
  DMC glide_to whose target note ≥ octave-10 (raw noteB byte $7E etc.) is NOT a
  real musical target — the arrival check `CMP freqhi[glb]` reads
  freqhi[125]=$1724=dtmpl / freqhi[126]=$1725=dtmph, the dual-slide temp (C11
  dynamic work-RAM). So it's a fast freq SWEEP that stops when the HI byte hits
  a scratch value (Calypso C-3 -> F#10 = a 90-semitone "glide"). The composer's
  `_row_event` glide_to parse `sep = tgt[1] if len(tgt)==3 else '-'` drops the
  '#' for 2-digit octaves (F#10 -> parsed 125 not 126) — LOOKS like a bug, and
  IS one in isolation, but it sits in a SELF-CONSISTENT balance: the parsed-125
  target stops the sweep on dtmpl, which the composer's state happens to track.
  "Fixing" it to `sep = tgt[1]` (target 126 -> dtmph) REGRESSED 20/104 FULL
  members and recovered 0 (Plasmachaos, the degenerate gla==125 special case,
  has an otrk-legacy 2nd blocker). A SURGICAL retry — restore the '#' ONLY when
  the drop degenerates the glide to the row's own note (target==note) — ALSO
  regressed 22/104 (Garfield_Story/Speedy/...): those members glide up 1 to a
  sharp-oct10 too and are FULL WITH the degenerate no-op (their dynamic-byte
  sweep resolves to match). So the note-glide model CANNOT reproduce these for
  ANY target choice — the current natural-parse is write-stream-OPTIMAL for the
  corpus. DO NOT re-attempt any glide-target adjustment (both a blanket and a
  surgical fix are proven net-negative). The real fix is a REPRESENTATION
  change: an off-table glide target is a dynamic-byte-terminated sweep, not a
  note glide (Move-1). Plasmachaos is doubly-blocked (this + otrk-legacy).
- **UNEXPOSED-TRACKING-VAR pattern — most of the "deep off-table tail" is NOT
  hard state, just a missing redirect ROW (2026-07-04, family-1 round 22, +50
  FULL: ioff +12, filter-state +19, +19 deeper-blocker).** The composer ALREADY
  maintains most engine state byte-identically — it MUST, to reproduce the
  $D4xx write stream — so an off-table read that sonifies that state only needs
  a redirect row exposing the already-tracking var; it is NOT a divergent-state
  bug. DIAGNOSTIC (the index-match check, `tmp/verify_ioff.py`/`verify_filtervar.py`):
  build the member, `siddump --memwatch-on-write D40x <composer_var>,<wnote>` at
  the divergent event N (N = per-reg write count up to flat_div pos). Three
  outcomes: (a) **wnote matches orig + composer_var == orig** ⇒ unexposed
  tracking var → ADD a redirect row (clean, transfers to the whole cluster,
  0-regression by construction — the live var == the orig value the FULL members
  read via the static byte); (b) **wnote differs** ⇒ wavepos drift (the composer
  re-packs the wave pool, positional — HARD, C11 wavepos boundary); (c) **wnote
  matches but composer_var != orig** ⇒ a genuinely non-tracking ACCUMULATOR
  (fcut $171C, the cutoff sum drifts; already-mapped otrk/dur/gla) — HARD, needs
  the var's evolution fixed, not a row. Landed rows: `ioff` ($174D inst#*11, the
  exact 6502 chain — the composer indexes by SLOT so it had no offset var) and
  the global filter state ($1718 spdctr / $1719 fstep / $171A fframe / $171B
  fbase / $1723 fres — all verified tracking). WHY the earlier census read them
  as a hard freq tail: the STALE-PARTIAL palimpsest (C20) — the merged truth's
  partials predated the round-21 fixes, so the deep census classified stale
  members; a drift re-verify (fix-verdict step) is MANDATORY before censusing a
  residue, else you chase already-fixed members (I burned an hour on stale
  Abrakadabra/cpwmax before catching it via a fresh `find_first_divergence`).
- **A GENUINELY-VARYING read can still be an unexposed tracking var — shadow a
  SHARED SCRATCH by mirroring ALL its writers (2026-07-06, commit 1198016,
  Ok_Ob_2_intro).** $171F ("wjmp_tmp", round-22 rejected bucket) varies per
  (inst,off,note) key, so static AND event-driven capture both fail — but it is
  a shared effect scratch with exactly 3 writers (pulse-program raw speed byte /
  glide step<<4 / wave jump-back distance), all values the composer already
  computes. A global `wjmp` var stored 1:1 at the three composer sites + a
  redirect row reproduces it exactly (raw pulse byte reconstructed from the
  decoded per-phase steps — `isteps[even] | isteps[odd]>>4` — as a derived
  `irawsp` table, NO schema change). Requirements to check before shadowing a
  scratch: enumerate ALL orig writers (disasm grep), confirm identical gating +
  per-frame order both sides, and init-clear/dense-write convergence (no seed
  needed when the orig init wipes it and one writer runs unconditionally per
  voice per frame). Exposure census: 30 FULL idx-carriers held, 12 partials
  none-earlier / 3 improved.
- **CACHE bytes with "no composer var" are shadowable by MATERIALIZING the
  var at the writer site (2026-07-06, Saturday_Dance +7 FULL — fxf $177D-F,
  fsz $1721, fdu $1722, overturning the round-22 "$1721/$1722 read inline via
  fdstep/fddur, no cache VAR to redirect to" rejection).** Two sub-cases in one
  first-divergence chase: (a) $177D fx-flags cache — the composer ALREADY had
  the var (`fxf,x`, stored at note-init exactly where the orig stores instr
  byte 10; `iflags()` is the lossless byte-10 reconstruction from typed fields
  — verify the ROUND-TRIP per instrument before mapping a reconstructed
  value); plain missing-row case, add `(0x177D,'fxf',3)`. (b) $1721/$1722
  filter step-size/duration caches — the composer read them inline into
  scratch (`tmp`/`tmp2`) at exactly the orig's STA sites; "no var to redirect
  to" is not a rejection, it's a one-edit fix: RENAME the scratch to dedicated
  vars (`fsz`/`fdu`) and add the rows. Both inside the orig's $1718-$179D init
  wipe + composer state wipe → no seed. Exposure sweep (83 idx-carriers): 62
  FULLs held, +7 partial→FULL, 0 regressions; full regression green.
- **A "POSITIONAL" counter is shadowable when its per-event deltas DERIVE from
  row content + stated-command flags (2026-07-06, Rodney/Intro_Music_2 —
  sectpos $1729-$172B, overturning the round-22 REJECTED verdict).** DMC's
  per-voice sector position (INC per consumed sector byte, reset 0 at the $7F
  end check run in the same fetch) was rejected as "cumulative orig byte count,
  needs per-event byte-widths in USF = C7 anti-pattern". The reframe: the
  visible value during a row is a PER-ROW CONSTANT = cumulative width through
  that row's fetch (0 on the pattern's last row), and width = base bytes of
  the row kind (note/rest/switch 1, slide 2, glide 3) + the STATED dur/instr/
  vol/soft commands. Statedness is a byte FACT of the sector (instance-
  independent, so widths are pattern facts that survive dedup); a value-change
  derivation reconstructs it EXCEPT for redundant re-statements — which are
  the editor's command PLACEMENT = §8 arrangement (the exact class ratified
  for redundant orderlist transpose commands, `otrk_rcmd`). So: the extract
  records per-row `dur_cmd/instr_cmd/vol_cmd/soft_cmd` fx_flags; the composer derives the
  per-row visible values at BUILD time, embeds one byte per pattern event
  (gated on `sectpos_shadow`, extract-set when an off-table freq read lands on
  $1729-$172B), stores it to a live `sectpos,x` at every fetch, + a redirect
  row (DMC_SECTPOS_ROW). NO byte offsets in USF. Default byte-identical
  (event layout + BSS + redirect row all gated); non-gated members re-merge in
  the composer's encoded-bytes pattern dedup even where the extract key split.
  GENERAL RULE: before accepting a counter as positional-hard, ask whether its
  per-event DELTAS are a function of (row kind, stated commands) — if yes, the
  counter is derivable content, and only the stated-command placement (usually
  = value changes, plus the rare redundant re-statements) needs carrying.
- **A MAPPED var that does NOT init-track needs SEEDING, not removal (2026-07-05,
  commit 87bde4c, 98_Mix).** A redirect var is only correct if the composer's copy
  tracks the orig FROM INIT. DMC's SPARSE glide state (gla/glb/glsp, $1744/$1747/
  $1741) is written ONLY in the glide branches, so a voice that never glides leaves
  it at the composer's ZERO-init while the orig keeps its uncleared file-image
  LEFTOVER — a static-leftover off-table read (98_Mix inst-0 wave freq=255 -> idx
  255 -> gla[2]) then read $00 vs the orig's $4C, the redirect shadowing the correct
  static `offtable_freq` capture. REMOVING the vars from the map fixed the static
  reader but REGRESSED a DYNAMIC reader (Alien_WOW/Hardcore, deep glide read) that
  legitimately needs the live redirect — the amend Lens-1 signal that the blanket
  map (commit 1ab8c46, "these track byte-identically") was the real defect, not a
  reason to pick one behaviour. OVERARCHING FIX: keep the redirect, SEED gla/glb,x
  at init from the captured off-table leftover (the ovr-window byte at the var's
  position, `A-ORIG_FLO-192`), so they track from frame 0 — the static reader gets
  the leftover, the dynamic reader overwrites the seed on its glide arm. glsp is NOT
  seeded (a non-zero glsp spuriously triggers fx_glide, gated `lda glsp,x/beq`) —
  a glsp static read stays residue. 0-regression by construction for the seeded
  vars: the seed differs from zero-init only where the orig leftover is non-zero AND
  read pre-glide (currently-partial members). GENERAL LESSON: before adding a var to
  the redirect map, check it is either init-cleared on BOTH sides OR densely written
  every note (so it converges) — a SPARSELY-written var must be seeded from the
  leftover, else it regresses static-leftover readers.
- **EVENT-DRIVEN capture recovers a STABLE-when-read dynamic byte (2026-07-06,
  commit 8eb86a4, +24 f1: 4803->4827).** Landed round-22's deferred "event-driven
  capture" — reached via the /amend skill overturning the round-22 "sectorpos
  $1729 is positional, defer to Move-1" BLANKET (which predates round-23's
  arrangement technique). An off-table freq read can land on a byte that varies
  GLOBALLY yet is STABLE at the moment a given note reads it: I_Hate_Techkkno's
  V1 noise note (inst $12, off-note y=$82) reads $16A7+$82=$1729 = SECTOR POSITION
  (cycles 0-9 over the song) and it's $08 EVERY time this note reads it. The old
  capture is wrong twice: `_assign_offtable_freq` reads the file image, and
  `_correct_offtable_postinit` only fixes bytes CONSTANT over a 6s TIME-sample, so
  it omits $1729 (globally-varying) and keeps the wrong file byte. FIX
  (`_offtable_eventdriven`): snapshot all 3 voices' (y=$1783, curnote=$1012,
  inst=$1015, base=$172F/$1732) at every $D416 write (once per play(), CIA-safe),
  and per (inst,off,note) key use the read-moment base where STABLE across the
  whole verify window. Gate: only when post-init left a globally-varying byte
  (skip members whose off-table reads are all init-constant). DIAGNOSTIC DELTA vs
  the earlier a/b/c triage: this is the (c)-looking case (byte varies) that is
  actually fixable because it's PER-KEY stable — measure stability AT THE READ,
  keyed by (inst,off,note), not over a time window.
  ⚠️ **CALIMERO REGRESSION = amend Lens-1 RECURSIVELY:** the event-driven fix
  collided with a PAST fix (round-25 igla/iglb seeding). Reads on REDIRECT-MAPPED
  idx (gla/glb/ioff/dur — the DMC_OFFTABLE_STATE positions) are served by the LIVE
  var and SEEDED from the file-image leftover; overriding their static window
  value with the deep runtime value broke the seed (FULL->partial). DISCRIMINATOR:
  `_redirect_mapped_idx()` (derived from composer_asm DMC_OFFTABLE_STATE + ORIG_FHI)
  — event-driven applies ONLY to WINDOW-served (non-mapped) idx; $1729 sectorpos is
  non-mapped ✓, dur/glb/ioff are mapped ✗. Regression-safe on the window-served
  set: a FULL member's read already matches → runtime value == file-image → no
  change. GENERAL LESSON: an off-table capture-value fix must respect which idx the
  composer serves from the STATIC window vs a LIVE redirect var — only correct the
  window-served ones; the redirect-served ones' static value is a leftover SEED.
- **Consumers:** DMC v4 `_decode_instrument` (commit 3cae4fd). Redirect rows:
  `ioff` (07c2125), filter-state $1718-$1723 (a026b74). Seeded (leftover-priming)
  redirect vars: `gla`/`glb` (87bde4c). Event-driven capture:
  `_offtable_eventdriven` + `_redirect_mapped_idx` (8eb86a4).

  ALSO DMC v4 TRACK + SECTOR positions (2026-07-07, error-cluster triage,
  25 errors → 0: +1 FULL +24 partial): the track position (`LDY $1726,x`) and
  sector position (`LDY $1729,x / LDA ($f8),y`) are BOTH one byte — a
  terminator-less track/sector (header-overstated subtunes: Bayliss PSID says
  6 songs, the tune table has 1 real record; subtunes 1-5 point at zero fill)
  wraps mod 256 in hardware and plays a 256-byte cycle forever. `_walk_track`
  walked pos full-width → RuntimeError 'never settles' (or IndexError past the
  64K image). Fix mirrors the wrap + detects the wrapped cycle by loop-top
  state repeat; an unterminated SECTOR returns `('endless', lead, period)` and
  the voice self-loops on the period entry. Regression-impossible: both paths
  previously HARD-ERRORED, no FULL member can carry them.

### C14 — Command-per-row tracker effects (note + effect + param per row)
- **The problem class:** unlike instrument-effect-driven engines (Hubbard / DMC
  where effects are per-instrument configs), classic trackers attach an EFFECT
  COMMAND + PARAM to each pattern ROW (ProTracker-style): porta up/down, tone
  porta, vibrato, arpeggio, set-filter, set-SR, set-tempo. `NoteRow` has no
  effect+param field — only `pitch/duration/instr/fx_flags`.
- **Canonical:** encode each per-row command as a **`NoteRow.fx_flags` string**
  with its parameter — `glide={delay}`, `glide_up=$XXXX`, `wave_adjust=N`,
  `filter=$XX`, `noretrig` (FC); `arp=X,Y`, `portaup=N`, `portadown=N`,
  `toneporta=N`, `vibrato=X,Y`, `filter=N`, `sr=$XX`, `tempo=N` (GoatTracker V1).
  Musical + parametric (each is a named effect with a continuous param), NOT an
  engine-library index → passes the USF principle WITHOUT a schema change. The
  composer parses the flag strings and emits the effect code.
- **Status:** `recurring` (FC `to_usf` established it; GoatTracker V1 reuses).
  Boundary: the flag VOCABULARY is per-family (each tracker's command set) but
  the MECHANISM (typed strings on the row) is shared. Move-1 candidate: a typed
  `RowCommand` union could replace the strings if the vocabulary stabilises — but
  strings are the current shared form; do NOT add a schema field per family.
- **Consumers:** FC (`pipelines/future_composer/to_usf.py` `_pattern_to_rows`),
  GoatTracker V1 (planned, RE_NOTES §7). **basic_program linear glide (2026-07-02,
  +11 FULL):** REUSED the standard-FC `glide_up=$XXXX`/`glide_down=$XXXX`
  directional-rate vocabulary + ONE new musical param `glide_ticks=N` (discrete
  slide granularity — engines that tick at their own loop rate, not per-frame).
  A constant-delta freq run (>=4 releaseless same-shape single-voice steps) lifts
  to the head NoteRow + these flags; the intermediates are engine MECHANISM and
  are regenerated at read time (freq = head + k*delta, the head's own C17
  template, frames spread over a `bp_glide{k}` span param) — they never enter the
  freq alphabet / rows / tids. This is what keeps >96-distinct-freq glide tunes
  inside the 96-slot per-tune pitch alphabet. Detection `semantic_lift
  _mark_glide_runs` (loop-head-safe). **REFINED to the REST-ROW scheme (+5 more,
  436 total, 2026-07-02):** members are NOT dropped — they stay ordinary steps
  (own tid / exact frames / durations) whose gliding-voice row is a REST; the
  reader arms a per-voice glide state from the head's fx and derives each
  member's freq (head + k*delta) when it sees a rest row whose template writes
  that voice's freq. Exact order+frames by construction, works for INTERLEAVED
  multi-voice simultaneous glides (per-voice run scan skips other voices' steps;
  Tron FULL 3936/3936), and deleted the drop-scheme's kept-filter / span params /
  loop-remap complexity. Paired with a segment() fix: the gated grouper now KEEPS
  the trailing capture-cut partial group (gate-off past the window) — only the
  min_trim variants retain it downstream. NOT handled: dual alternating glide
  streams within ONE voice (Sleepy V2 — odd/even substreams each constant-delta)
  and exponential/float-computed slides (C_Prog_07 — BASIC float rounding is not
  parametrically reproducible). **ROUND 3 (+7, 443 total, 2026-07-02):**
  (a) PER-VOICE CHAINS — a step writing several voices' freqs (a two-voice
  [V1hi,V2hi] tick) contributes an observation to EACH voice's chain; a step is a
  candidate for voice V iff among V's regs it writes ONLY freq (other voices' /
  global regs in the same step are fine), so simultaneous multi-voice glides
  bundled in shared steps lift (Wood_Steve/Music FULL 2345/2345). (b) STAIRCASE
  fit `u_t = u0 + (t//R)*delta` + NEW musical param `glide_hold=R` (level held R
  ticks; R=1 = plain ramp). (c) multi kmax 48→128 (Christmas_Album K>48 → FULL
  1867/1867; tid is a byte, the stride guard still bounds records). (d) the
  min_trim glide retry fires on ANY non-FULL res8 (Music needed min_trim for the
  ALPHABET, not for length). ALSO capture-retry hardening: verify_cycle
  writelog_capture + proof_twinkle capture_real retry 3x on rc!=0/empty stdout —
  a parallel-load siddump death silently read as "the SID emits nothing" and
  corrupted verdicts (the transient portfolio flake).

### C12 — Accumulated per-step rounding drift in a delta-encoded round-trip
- **The bug class:** the USF (or any parametric form) stores a sequence as
  per-step DELTAS — note durations, inter-event gaps, hold lengths — and the
  player/reader reconstructs ABSOLUTE positions by SUMMING them
  (`pos += hold + gap`). If each delta is passed through a floor/min/round
  (e.g. `gap = max(1, nxt - off)` to avoid a 0-duration row), the per-step error
  ACCUMULATES. Short tunes stay within the verification tolerance; LONG tunes
  (hundreds of steps) drift past it — the reconstructed positions land late, the
  song's tail falls outside the capture window, and it reads as `length_fail`
  (an exact PREFIX, short by a growing amount). The model itself is exact; the
  loss is entirely in the delta encoding.
- **TELL / how it presents:** a CLUSTER of LONG tunes that are exact-prefix and
  short by an amount that scales with song length (not a fixed tail). Building
  DIRECTLY (model → player, no round-trip) gives a tiny shortfall; through the
  round-trip the shortfall balloons. The smoking gun: diff the direct model's
  on_frames vs the round-tripped model's — a PROGRESSIVE divergence (step k off
  by ~k·ε) is delta-rounding accumulation, a CONSTANT offset is a start/seed bug.
- **Canonical fix:** keep the deltas EXACT — allow the degenerate value (gap 0 =
  back-to-back events; a duration-0 row is fine if the writer/reader don't floor
  it). Remove the floor on BOTH the writer (`model_to_usf`) and the reader
  (`usf_to_model`). The cumulative then telescopes back to the exact positions.
- **BOUNDARY — exactness can expose a SAME-FRAME-ORDER hazard.** A delta of 0 puts
  two events in the SAME frame, so their relative WRITE ORDER now matters. If the
  0 is GENUINE (truly back-to-back) the player's fixed order matches; but if the
  0 is SPURIOUS — an upstream rounding (rho-scaling) collapsed two distinct frames
  into one — exactness REORDERS same-frame writes and turns a FULL into an
  overlap_diverge. When you can't cheaply tell genuine from spurious, ship the
  exact encoding as a length_fail-only VERIFY-FALLBACK (try the floored default
  first; only if it's length_fail, retry exact and accept iff FULL). The
  floored-default tunes never reach the exact pass, so the spurious-collapse
  reorder can't regress them — 0-regression by construction. It must COMPOSE with
  the other fallbacks (a tune can need exact-gap AND min-trim), so run the WHOLE
  fallback chain twice rather than just the base model.
- **Status:** logged (basic_program gap_exact, commit 33c12de; +13 long tunes,
  0 regression — 3 rho-collapse-spurious tunes stay FULL via the floored default).
- **Consumers:** basic_program `model_to_usf(gap_exact=)` + `best_attempt` 2-pass.
  WATCH-LIST: any other delta-encoded round-trip (DMC duration counters, note
  durations in trackers) — audit for a `max(1,…)`/`round` on the per-step delta.

### C13 — Engine-variant dispatch: shifted init, canonical play body
- **The bug class:** a player family has sub-variants that differ ONLY in the
  init/dispatch header while the per-frame PLAY body — the code that emits the
  `$D4xx` write stream — sits at the SAME relative offset as the canonical
  member. A dispatch keyed on the init handler's offset (or a full-image code
  compare) rejects these variants (`no_jumptable` / `player_code_mismatch`),
  even though their play body is byte-identical and every operand site is in the
  unshifted body. Because the composer EMITS ITS OWN init (universal reset +
  typed priming, never reproducing the original's init writes — see the CORE
  TENET and the init-trichotomy), the init handler's layout is IRRELEVANT to the
  write-stream verdict; only the play body matters.
- **TELL / how it presents:** a cluster of build-fails whose jump table has the
  canonical PLAY target (e.g. DMC family-2 `JMP base+$85`) but an init target a
  few bytes off (`base+$38..$3A` vs the canonical `base+$37`). The play body
  decodes cleanly; only the init region differs.
- **Canonical fix:** dispatch on the PLAY-body signature, NOT the init offset.
  Accept the variant, extract operands from the (unshifted) canonical play-body
  sites, emit your own init, and let BUILD+VERIFY (the write stream) be the
  judge. A loosened dispatch can never false-FULL — a genuinely-different engine
  that happens to share the play offset extracts garbage operands and verifies
  partial, not full. Keep the init-offset window tight enough to be principled
  (near the family's real init region) but don't gate on an exact match.
- **Status:** logged (DMC family-2 `_jt_layout` play+$85 / init∈[+$30,+$40],
  commit 2a07a7e; +12 FULL / 2 correctly-partial / 0 false-accept). Composes with
  the earlier build+verify-gate change (aaa914c) that replaced the family-2
  code-identity hard-reject with a `break` + build+verify judge — same principle
  (the write stream judges, not code identity), one round apart.
- **Consumers:** `pipelines/dmc/v4/factory.py` `_jt_layout`. WATCH-LIST: any
  feature-driven family whose detection compares init/dispatch code — the
  verdict is the play stream, so dispatch should key on the play body.
- **NOTE — signature LOCATORS are dispatch too (2026-07-07, f1 no_jumptable
  62→0, commit 2ac58cbb).** The dataflow path's opcode-WINDOW signatures are
  a form of init-adjacent dispatch: a read site whose surrounding window
  includes rewritten init/preamble code fails every window width even though
  the read's own inner shape is intact. Four fixes, all "key on the play
  body / the read itself, not the neighborhood": (a) `_sigs_op` tries ALL
  canon reference sites for a data operand, not the first (d417's first ref
  is in the rewritten preamble; its RMW sites still match); (b) per-table
  INNER-SHAPE fallbacks with value-dedup (tunetab paired lo/hi read; wavectrl
  `LDY pos,x / LDA t,y / CMP #$90`; d417 `LDA v / ORA / STA $D417|v`);
  (c) base candidates from wrapper `JMP` targets carrying a strict `4C..4C`
  table + loose `4C`-only tables, each judged by locate-success (never a
  full-image loose scan — an interior 4C..4C pair locates from the wrong
  base); (d) when the jump-table play entry points at zeroed RAM (ripper
  artifact), retrace from the PSID header's play. +31 FULL / +31 partial,
  0 false-accepts, regression-impossible (all four only run on paths that
  previously refused).
- **COROLLARY — variant-KNOB probes must be layout-independent too (2026-07-02,
  DMC family-1 dataflow path).** Accepting a re-assembled member is only half
  the job: the canon path's sub-build KNOB probes (rest-skip dispatch, $D418
  helper, ...) read canon-RELATIVE sites, so on a re-assembled layout they
  silently MISS and the member builds with default knobs — a wrong-MECHANISM
  rebuild that presents as an early (<64) flat divergence, not a build-fail
  (Hyper: rest-skip player + default `rest_effects='run'` → flat pos 2). Fix:
  re-probe each knob by OPCODE SHAPE (`factory._dataflow_knob_probes`: find the
  rest handler `LDA,x/STA,x/INC,x/[JSR]/JMP` and classify the JMP target by the
  wave-step `BD..29 01 D0` vs effects `BD..F0..DE` signature). Landed: 29
  partials re-typed, +5 FULL immediately, Hyper's divergence moved pos 2 →
  296k; 0 currently-FULL members flip (probe census first — always census the
  FULL-side flip set before landing a knob probe). REMAINING: the other canon
  probes (D418 helper, all-off mask, hard-restart variant, filter-mode
  extraction) still canon-site-only — port them the same way when their
  clusters surface (~10 of the 29 still diverge early on other knobs).
- **NOTE — a variant CLASSIFIER's binary "not-A ⟹ B" rule hides a THIRD form;
  fix it by POSITIVE detection of the minority, never by flipping the default
  (2026-07-08, DMC f1 loop hook, +6 FULL 0 regr).** The `track_loop_target`
  probe split the `$FF` track-loop into TWO forms: canon `STA $1726,x`
  (loop-to-0, False) vs the read-next-byte JSR hook `INY/LDA($f8),y/STA $1726,x`
  (True), with `dataflow.locate` encoding it as `track_loop_target = loop_site
  is None` (canon-STA sig absent ⟹ assume read-next). A THIRD form existed: a
  JSR to `LDA #0/STA $1726 / LDA #0/STA $1727 / LDA #0/STA $1728` =
  RESET-ALL-VOICES-to-0 (a SYNC restart), semantically loop-to-0 but mislabeled
  read-next → the walk mis-read `$FF`+1 as a loop-target jump (Unfinished_1:
  byte 21 `FF`, byte 22 `82`=130 → bogus entry at byte 131, loop_to=20 instead
  of 0). Presents as a note-fetch divergence at the FIRST loop-back deep in the
  ×1.1 tail (state ✓, perfect prefix). These members fail the canon
  masked-compare (wedge bytes) so they reach the dataflow path; the canon
  loop-hook probe is NOT involved (fix is dataflow-only).
  **THE TRAP I NEARLY LANDED (amend Step 3.2):** the first fix flipped the
  DEFAULT — `True` only when a read-next idiom (`c8 b1 f8 9d`) is scanned, else
  `False`. That is the SAME "not-A ⟹ B" mistake inverted: a read-next hook whose
  zp differs from `$f8` (relocated variants use `$58/$61/$68…`; the track-pointer
  zp and track-pos addr both vary) false-NEGATIVEs the scan → a genuine read-next
  member regresses to loop-to-0. **CANONICAL FIX:** keep the base rule
  (`loop_site is None`) UNCHANGED — so every read-next member keeps `True`
  regardless of zp — and flip to `False` ONLY on a POSITIVE match of the exact
  reset-all 3-pair idiom (`A9 00 8D a / A9 00 8D a+1 / A9 00 8D a+2` to
  consecutive track-pos addrs) in the reachable trace. That idiom has 0
  occurrences in the canon player and in all 848 read-next members (census: 8
  carriers in all HVSC-DMC, every one reset-all) → the "changed" verdict has NO
  false positive = regression-safety is a THEOREM, not a hope. LESSON: when a
  probe splits variants with an "else ⟹ the other form" default, DON'T flip the
  default (you only move the blind spot) — detect the minority form by a POSITIVE
  signature verified absent from the majority. `dataflow.locate` reset-all match.
- **REFINEMENT — the reset-all hook target need not be 0 (2026-07-09, DMC f1
  Action_G, +1 partial → FULL, 0 regr).** Round-53 hardcoded the reset-all
  immediate as `#0` (loop-to-0). Action_G's `$FF` handler is `LDA #5 / STA $1726 /
  LDA #5 / STA $1727 / LDA #5 / STA $1728` = reset-all-to-**5** = a synchronized
  loop to track position 5 (the intro block pos 0-4 plays ONCE, then the loop
  body starts at the second, byte-identical `A1 01 01 01 05` block at pos 5). The
  round-53 detector's `mem[...]==0x00` guard skipped it, so `track_loop_target`
  stayed True (read-next) → the walk read `$FF`+1 (`A1`=161) as a jump target and
  marched off past the terminator into garbage (entry_offsets `…45, 161, 162`,
  self-loop). GROUND TRUTH: pc-trace the `$FF` handler ($10DF `JSR $1020`; $1020 =
  the 3× `LDA #5/STA $172x`) + memwatch the $1726 trajectory (`…2E → 06`, i.e. it
  lands on the transpose marker at pos 5 then advances to 6 — inconsistent with
  reset-to-0 which would show pos 1). FIX (extract-only, dataflow): generalize the
  round-53 idiom to capture the immediate N (require all three LDA equal — the
  discriminator is the equal-immediate + consecutive-address SHAPE, N is the loop
  target); new `DMCV4Config.loop_reset_pos` (None ≡ loop-to-0/read-next) threaded
  to `_walk_track` (`tgt = loop_reset_pos` at `$FF`). NO USF field, NO composer
  change — the walk emits the correct resolved orderlist; loop_reset_pos is a
  derivation knob consumed entirely at extract time. REGRESSION-SAFE BY
  CONSTRUCTION: N==0 leaves loop_reset_pos None ⟹ the 6 round-53 carriers build
  byte-identical (confirmed); N>0 flips only members that were walking garbage
  past `$FF` — census over 5833 f1 members = exactly 3 carriers (Action_G N=5,
  Axel_F_v2 N=4, MON_Tribute N=5), ALL previously partial ⟹ 0 FULL exposure =
  the round-53 theorem holds. Full tools/regression.py GREEN (0 regr all 7
  families). Action_G FULL 111670/111670 (100%, state ✓). Post-fix sweep of the
  2 sibling carriers SKIPPED per user (next batch accounts via code_hash).
- **REFINEMENT² — the reset-all target can be PER-VOICE, not one N (2026-07-09,
  DMC f1 Attacker, +1 partial → FULL, 0 regr).** Round-62 required the three
  reset immediates EQUAL (loop every voice to the same N). Attacker's `$FF`
  handler (`JSR $1020`; `$1020 = LDA #3/STA $1726 / LDA #$1E/STA $1727 /
  LDA #3/STA $1728`) loops each voice to a DISTINCT position — 3/30/3 — so
  round-62's equal-immediate guard skipped it and `track_loop_target` stayed
  True (read-next) → V1 walked past `$FF` into the loop tail. TELL: deep in the
  ×1.1 loop tail (state ✓, ~98.8%), a synchronized 3-voice hard-restart where
  only 2 voices resync in the rebuild; memwatch the three track positions
  ($1726/7/8) and read the `$FF` handler's `JSR` target. FIX (extract-only):
  generalize `loop_reset_pos` scalar N → per-voice tuple `(n0,n1,n2)`; drop the
  equal-imm requirement but ANCHOR the STA triple to the track-position address
  (operand of the fetch read `LDY tpos,x` [`BC`] immediately followed by
  `LDA (zp),y` [`B1`], relocation-safe) so a non-reset-all 3-consecutive-store
  init can't false-match. `_walk_track` gets the per-voice scalar (extract call
  site indexes the tuple). NO USF field, NO composer change. REGRESSION-SAFE BY
  CONSTRUCTION: the equal-imm path is byte-identical (round-53/62 carriers
  unchanged); the per-voice branch is a positive minority anchored to track_pos.
  CENSUS (`dataflow.locate`, all 5401 f1): exactly 1 tuple carrier = Attacker
  (previously partial) ⟹ 0 FULL exposure. LESSON (round-62's, one level deeper):
  the SHAPE is the discriminator, EACH literal is per-voice DATA — don't presume
  the literals are equal any more than you bake in their value.

### C15 — ⛔ REMOVED (audio-equivalence verdict relaxation)
**User decision 2026-07-01: every SID always gets the STRICT write-stream match.**
The "audio-equivalence" verdict (dropping inaudible idle-freewheel writes from the
compare) is NOT a per-engine tool and must not be proposed during migration work.
When an idle/gate-off freewheel divergence blocks a member, the answer is to
**REPRODUCE the writes** — the core tenet explicitly permits reproducing the
original's mechanism (DMC `idle_wave` / resting-voice and the family-4
`f4_idle_notes` leadin priming are the precedents). The full design (soundness
gate, sync/ring-mod guard, validation record) is parked in
`docs/refactor_1_remaining.md` ("Move-1-era considerations") and may be
revisited ONLY around Move 1, when most/all engines are uready — not before.


### C16 — Per-frame SID write-ORDER differs across engines
- **The problem class:** two engines in the same family emit the SAME per-frame
  $D400-$D418 writes but in a DIFFERENT ORDER. Within a frame the order matters
  (Mode 1: gate edges, test bit, ADSR delay, $D418 clicks), so the rebuild
  diverges even though the VALUES are right and the cycles don't matter. Two
  granularities seen: (a) WITHIN-VOICE register order (which of FREQ_LO/HI,
  PW_LO/HI, CTRL a voice writes and in what order); (b) ACROSS-VOICE / PASS
  structure — e.g. DMC V5 family-4's 2-phase player does a NOTE-ON pass
  (SR/AD/CTRL for voices that fetched this frame) and a SEPARATE WAVE-STEP pass
  (FREQ/PW/CTRL), so the stream is `V1 note-on · V2 note-on · …wave-steps…`,
  whereas the family-3 composer does it PER-VOICE INTERLEAVED (V1 note-init +
  wave-step, then V2 …).
- **TELL / how it presents:** the writelog match holds through the leadin, then
  forks where the orig writes one voice's note-on register but the rebuild
  writes another voice's freq (or the same voice's freq vs the next voice's
  ctrl). Sweeping the leadin/timing does NOT move the fork (it's structural, not
  a phase offset). The VALUES on both sides are individually present nearby —
  only the interleave differs.
- **Canonical solution:** PARAMETRIZE the composer's EMISSION order; do NOT
  rewrite the player or fake it. The CORE TENET explicitly licenses "completely
  re-arranged effect-chain emitters" — the composer is free to emit in whatever
  order matches the write-log. Precedent: FC's
  `pipelines/future_composer/composer_asm.py:_emit_nextvoice_writes(write_order)`
  — a config tuple of the 0-4 register offsets a voice writes, threaded as
  `nextvoice_write_order`. For the across-voice/pass case, the analogue is a
  composer knob that splits the per-voice emit into a note-on pass + a wave-step
  pass (gated on the engine flag, e.g. `m.family4`).
- **METHODOLOGY — TRACE THE EXACT ORDER FIRST (don't guess the scope).** Before
  declaring "needs a big restructuring," fully trace the per-frame call graph and
  write the literal register-write sequence for 2-3 frames; the reorder is almost
  always a bounded emission-order knob, not a rewrite. (DMC family-4: I prematurely
  scoped it as a multi-session composer rewrite before tracing — this consult +
  the FC precedent reframed it as a parametrize-emission-order knob.)
- **Status:** logged (consult 2026-06-29, DMC V5 family-4 — diagnosed, the
  emission-order knob is the next step). FC `nextvoice_write_order` is the shipped
  precedent for the within-voice granularity.
- **Consumers (seen):** FC `nextvoice_write_order` (shipped, within-voice). DMC
  V5 family-4 (the across-voice 2-pass case; pending). **GoatTracker V1 player1
  OPTIMIZED variant (shipped 2026-06-30, commit 3f20ab5):** `optimized`-gated knob
  moves the per-voice pulse write from pulseexec (before freq, conditional on
  instpulsespd!=0) to AFTER loadregs's $D404 (unconditional, every frame) = player2's
  loadpulse-after-freq order. 435-tune bucket (`v1_pwlo`/`v1_freqlo` div<50, half of
  player1's partials). I MIS-SCOPED it as a "flow restructure" first; the C16 consult
  + the FC precedent reframed it to a bounded knob (the same lesson C16 already
  records for DMC family-4 — trace first, don't pre-scope a rewrite).


### C17 — Heterogeneous per-step write shapes in a trace-lift (multi-template)
- **The problem class:** a trace-lifted per-step write model assumes ONE step
  template (or one superset order + per-step masks). Real hand-authored tunes
  (basic_program) have K DISTINCT step shapes — alternating one-voice-per-step
  textures, sections with different register orders, gate-off groups writing a
  register twice — so a single ordered union does not exist (`_union_order`
  precedence cycle) or an intra-step dup breaks the reg-keyed superset.
- **Census first (the shape of the evidence):** 143 censused residue members —
  112 fail on ORDER conflicts, the rest on release-side dups; K ≤ 16 shapes for
  137/143, top-16 shapes cover ≥95% of steps for 142/143. Small K ⟹ the general
  form is affordable.
- **Canonical:** cluster steps by their EXACT (attack reg-seq, release reg-seq)
  shape; each cluster is a POSITIONAL template (const/perstep per slot — a
  repeated register is just two slots, so dups are free); each step carries a
  template id. The single template and the masked superset are the K=1 special
  cases. Write model (templates + tids) goes in scalar `params{}` exactly like
  `bp_atk{i}`/`bp_mask{k}`; musical content (pitch/duration/instrument/global
  track) stays in the USF body unchanged. Player = per-template straight-line
  emit blocks + a tid dispatch. TWO exactness sub-lessons (C12 family): keep
  HOLD exact too (a zero-length hold — gate-off in the gate-on frame — floored
  to 1 accumulates +1/step drift), and a per-note RELEASE ctrl that isn't
  `attack_ctrl & $FE` is instrument content (the gate-off waveform) — carried
  as `Instrument.waveform[1]`, not derivable.
- **Status:** logged (basic_program `_multi_templates` + `build_player_multi` +
  `bp_multi` params, 2026-07-02; wired as a best_attempt verify-fallback →
  0-regression by construction). **RESULT: +107 FULL (278→385, 57.2%→79.2%),
  0 regressions**, cutting across FIVE prior buckets (variable_template 41 /
  too_few_after_trim 33 / length_fail 12 / legato_variable 12 /
  overlap_diverge 9) — the census-predicted shared lever.
- **Round 2 — multi+SPLIT (+35 FULL, 385→420, 86.4%):** an intra-step dup FREQ
  (arp within one step) builds fine positionally but round-trips WRONG through
  the USF — one NoteRow pitch per step can't carry two freqs, so both dup slots
  reconstruct the same value (early freq-reg divergence, the residue census
  tell). The unsplit multi MODEL succeeds, so the auto split-fallback never
  fired; the fix is an explicit `multi_template=True, force_split=True` retry
  (each freq gets its own sub-step = its own NoteRow) + holds kept exact in ALL
  multi branches (same-frame split sub-steps otherwise drift +1). Lesson: a
  representation can be write-stream-complete at the MODEL level and still
  lossy at the USF level — always census the round-trip, not just the build.
- **Boundary:** kmax=48 shapes / 250-byte record stride. Applies to TRACE-LIFT
  write models (the engine IS arbitrary hand-written code); tracker engines with
  a real per-frame player don't have this DOF (their write order is the player's
  code — C16 territory, parametrize the composer's emission order instead).
- **Consumers:** basic_program (`pipelines/basic_program/semantic_lift.py`,
  `usf_roundtrip.py`).
- **NORMAL-FORM EVOLUTION (2026-07-02, user-driven):** storing the K templates +
  per-step tids in USF params was recognized as representation-principle §3
  FAILURE MODE B (the USF carrying a per-tune engine program — "complete but
  unlearnable"). Resolution per §4: WHAT a step writes derives from row-level
  event types (note + changed-byte flags / re-poke / tie / glide tick /
  timbre-setup / globals-from-track); the per-tune residue is NAMED string
  params `bp_order_<sig>: "v1_flo v1_fhi v1_ctrl / v1_ctrl"` (the C16 knob
  shape; params grammar gained string values). Templates + tids became INTERNAL
  player artifacts, re-derived by the reader via `_multi_templates(steps)` —
  C17's clustering lives on as mechanism, not as USF content. Non-derivable
  tunes (same-sig order conflicts, re-poked unchanged globals) raise
  `nf_conflict` and keep the legacy form (260 NF / 195 legacy at stage 1).
  LESSON: when a write model lands in params, ask FIRST whether rows + a few
  named order knobs derive it — the census (`tmp/bp_census_derivable.py` /
  `_rowaware.py`) made the call quantitative (79-82% derivable) before any
  code was written. **LEGIBILITY refinements (2026-07-03, user-driven):**
  (a) ADAPTIVE SIGNATURE COARSENESS — the writer picks the MINIMAL flag subset
  ({bytes, tie, norel, ins}, coarsest-first SIG_SUBSETS ladder) whose
  sig→order map is conflict-free, so keys carry only the distinctions a tune
  needs (God_Save: 9 flag-soup keys → 4 readable `v1_note_norel__v2_setup`
  keys); the reader looks up FINEST-first (keys with flags outside the
  writer's subset were never stored → no false hits; coarse-first WOULD
  false-hit the plain branch of a refined pair — caught as a real bug).
  (b) the NF global track records WRITTEN fields, not just changed (an
  unchanged re-poke is a real per-note write — the master-vol-per-note idiom).

### C21 — Trichotomy-verdict alignment (rebuild emits its own init)
- **The problem class:** under the init trichotomy the rebuild's init writes are
  a universal reset + typed priming, structurally different from the original's
  init sequence — so a flat prefix compare diverges at write 0. The verdict must
  (A) check the end-of-init chip STATE matches and (B) compare the PLAY streams
  after aligning past both inits.
- **Two implementations now exist (recorded as a CONSULT MISS, 2026-07-03):**
  `pipelines/hubbard/verify_cycle._trichotomy_compare` (FC universal_reset:
  recovers the alignment as a stream SHIFT d, then Check A + aligned compare +
  close-length tolerance) and `pipelines/basic_program/usf_roundtrip.
  _compare_music` + `_split_aligned` (the rebuild's init length is KNOWN from
  the typed model, and the orig's split point is found by locating the
  rebuild's first 8 music writes in the orig stream — needed because a
  gate-on-based split misfires when init PRIMES a gate/freq seed, and the
  BASIC "init" is a minutes-long setup phase rather than a fixed-length
  prefix). The basic_program variant was written WITHOUT consulting this
  ledger; whether shift-recovery could have served is unassessed. Move-1
  factor-candidate: one shared trichotomy verdict with pluggable alignment
  (shift-recovery | known-length + probe).
- **Status:** factor-candidate (2×).
- **Consumers:** FC standard (`compare_instruction_stream(mode='trichotomy')`),
  basic_program NF stage 2+.


### C18 — Play-vector wrapper with per-call PHASE behaviour
- **Canonical:** when a member's play vector is a WRAPPER that behaves
  differently on successive calls (the editor's slow-tempo / multispeed-effects
  trick), do NOT parse the wrapper code (shapes vary: SMC JSR-operand table,
  DEC counter + dual JMP, parity `AND #1`, re-authored JT slots). OBSERVE it:
  run init + N play() calls under py65 and classify each call by which engine
  ENTRY POINT it reaches — full play body (P) / per-voice frame entry, effects
  only (F<voices>) / per-voice glide+write tail, register REFRESH re-emitting
  current freq/PW/ctrl without ticking (R<voices>) / none (S). Take the minimal
  repeating period as a schedule string (`P_S`, `P_F123_F123_F123`, `P_R123`)
  and have the composer emit a phase-counter dispatcher whose per-phase routines
  JSR the composer's OWN corresponding entry points. Entry-point mirroring makes
  the reproduction exact by construction — the phase routine runs the same code
  the original's phase runs.
- **Trap:** a call that emits SID writes can still classify as S if you only
  watch the P/F entries — Toccata's "silent" phase was a register refresh hidden
  in the re-authored all-off JT slot (`LDX/JSR $141C ×3`). Before accepting an S
  classification for a diverging member, check the orig's per-IRQ stream for
  writes in the non-P calls.
- **GROUND-TRUTH observer (2026-07-04): straddle-free pc-trace.** py65
  observation FAILS on CIA/IRQ-armed members that idle silent under the
  interpreter — it reads their effect frames as `S` (no writes), yielding a
  bogus `P_S` schedule (9 CIA members mis-observed this way). The fix is a
  ground-truth observer off the libsidplayfp pc-trace
  (`verify_cycle.pctrace_per_play_capture` + `factory._observe_play_phases_pctrace`),
  wired as a fallback whenever py65 gives `None` OR an `S`-containing schedule.
  KEY LESSON: do NOT observe phases from the per-IRQ *writelog* — it buckets by
  play-entry CYCLE, so a play() spanning a siddump-frame boundary STRADDLES into
  the next chunk (F.A.K.E-Intro's writelog view showed a spurious `F P P` warm-up
  and a doubled P; the pc-trace, bucketed by CPU INVOCATION at PC==play_addr, is
  a clean `P F123 P F123` from call 0). This is what the parked
  `_observe_play_phases_writelog` got wrong. Also: the F-vs-R classification
  FLAPS (a held note stops advancing → reads R for a frame), so fit the period
  on a collapsed key (F/R→same) and resolve each phase's F/R by MAJORITY. The
  observer is correct + regression-safe (0/40 CIA-full sample) but recovered 0
  currently-partial members — the `P_S`-mis-observed ones have DEEPER blockers
  (note-start 2-frame arm, positional residue), so correct phases alone don't
  flip them. Landed as latent-correctness infrastructure, not a FULL-count gain.
- **CHIP-STATE R/F rule (2026-07-06, Bladeswede):** classifying R vs F against
  the PREVIOUS CALL's write set (or by majority-with-ties→R) misreads an
  effects phase whose program repeats values early — a chord wave program
  [0,0,0,3,...] re-emits identical freqs for its first steps, observed as
  R123, and the rebuild froze the arpeggio at tone 1 forever. The precise
  discriminator is CHIP STATE: a pure register refresh can only re-emit the
  value currently ON the chip, so track `chip[reg]` across all observed calls
  (a reg's FIRST sighting is recorded, never counted as advancing — the
  pc-trace capture drops the init prefix) and mark a call F iff it writes a
  known reg a DIFFERENT value. Resolve a phase position F on ANY advancing
  occurrence (a true refresh can never advance ⇒ no false F); keep the
  period fit on the collapsed F/R key. Empirically 0-drift: all 86 stored
  play_phases/cia_period carriers (incl. Compotune's genuine
  P_R123_R123_R123) reproduce identically. Supersedes the majority rule.
- **FRAME-ENTRY REACHABILITY for the offset-blind observers (2026-07-08,
  My_Rusty_Love_C64 +1 FULL, 0 regr):** the chip-state rule alone still
  false-reads a HELD note's frame entry as R — ALL its writes are idempotent
  for the whole observation window (freq/PW/ctrl re-emit the held values), so
  nothing "advances", yet the orig runs the FULL frame entry every call and
  re-asserts the holding gate-off `AD/SR=$00` (sub_17EC) whenever the duration
  counter sits at 1. The rebuild's R emission (glide+write tail) drops exactly
  those writes (My_Rusty_Love: re-assembled 6x-CIA member, wrapper `$18F1`
  = per-sub-phase VOICE-MASK tables driving `JMP $11FA` = full frame entry;
  misread `P_F1_R1_F13_R13_R13`, truth `P_F1_F1_F13_F13_F13`). FIX = restore
  the CANONICAL C18 form (entry reachability) on the offset-blind paths:
  locate the frame entry BY SHAPE (`LDA pending,X / BNE +3 / JMP` = `bd ?? ??
  d0 03 4c`, `factory._frame_entry_candidates` — re-assembled variants shift
  it off canon base+$1F9, e.g. $11FA) and classify F POSITIVELY iff the call
  reaches a candidate, OR-ed with the chip-state advance (kept as fallback for
  shapes the signature misses; a true refresh reaches no frame entry and can
  never advance ⇒ still no false F). Wired in `_observe_play_phases_writes`
  (py65 PC watch) + `_observe_play_phases_pctrace` (pc-trace `watch_pcs`).
  Exposure proof: 25 stored R-token FULLs (Finn ×20, Bakewell ×2, +3) all
  genuinely never reach a frame entry → tokens unchanged, builds
  byte-identical; flip census over all 236 f1 partials = exactly 1 carrier
  (My_Rusty_Love, → FULL 388489/388489 state ✓). Round-53 lesson applied:
  detect the minority (F-behind-R-disguise) positively; never flip a default.
- **F-ENTRY-POINT variant — vib_half instead of wavestep (2026-07-09,
  Acid_Dance +1 FULL, 0 regr):** on a noteinit_deferred member the F phase enters
  PAST the note-init check — but there are TWO such entries with IDENTICAL
  F-call write footprints: the plain wave step (canon $1591) and the vibrato
  half-cycle boundary (canon $1567: vibctr=0, flip vibdir, run the swell,
  fall through $1591). The difference is vibrato STATE only, observable later
  as the vibrato's SHAPE: 3 flips between full plays turn the triangle into a
  ±vstep SQUARE (Acid_Dance V2: orig $268↔$26C alternation vs the rebuild's
  free-running $268→$258 triangle; wrapper = SMC JSR-operand table → JT slot 3
  → `LDX #0/JSR $1567/INX/JSR $1567/INX/JSR $1567`). Not derivable from the
  footprint, so OBSERVE entry reachability (the C18 canonical form):
  `factory._detect_effect_entry_variant_vibhalf` shape-locates $1567 (`a9 00 9d ?? ?? bd
  ?? ?? 49 01 9d`, reloc/re-assembly invariant) and answers vib_half iff EVERY
  observed F invocation (voice writes, no $D416) executes a candidate — a
  wavestep-entry F call can never reach $1567 (it lies upstream; nothing jumps
  back) ⇒ no false positive ⇒ regression-safe by construction. Param
  `effect_entry_variant: vibflip` (vocabulary shared with `rest_effects='vibflip'`, the
  $1180 rest-tail patch this member ALSO carries — two INDEPENDENT edits, do
  not derive one from the other); composer's `voice_fx` JMPs its own
  `vib_half` label. Exposure: all 19 stored noteinit_deferred FULLs probe False
  (builds byte-identical).
- **R-ENTRY-POINT variant — pulse TAIL instead of register refresh (2026-07-10,
  Toccata_v2 +1 FULL, 0 regr):** the R (non-tick) phase can run a SECOND pulse
  advance per music tick, not a plain refresh. Toccata_v2's parity wrapper is
  `$2702: LDA/INC $26EF / AND #$01 / BEQ→$1003(full) / JMP $1006`, and $1006 →
  `$162F: LDX #0/JSR $135D/INX/JSR $135D/INX/JSR $135D`. `$135D` is the pulse
  routine PAST its `LDA $18f3,y / STA $171F` speed-nibble reload (the full-play
  path reaches $135D only by FALL-THROUGH from $134E, never by JSR), so the tail
  computes its step from the STALE $171F left by the prior full-play frame — a
  real extra sweep. The write-footprint observer read it as a refresh `R` (the
  pulse HOLDS its value for the first ~6 frames before the sweep moves, so no
  advance shows in the 12-call window); once the sweep moves, the R frame's PW
  diverges (orig advances, rebuild's `fx_glide` refresh does not). Not derivable
  from the schedule, so OBSERVE by EXECUTION (C18 form):
  `factory._rphase_pulse_tail_probe` runs a few play() calls and watches for a
  `JSR base+$35D` (uniquely the wrapper's R entry — the fall-through can't be a
  JSR) → `rphase_variant: pulse_tail`. Composer factors the pulse sweep behind a
  `pw_sweep` label and adds a gated `pulse_tail` routine (nibble-select the step
  from the stale `wjmp` = $171F by `pwphase` parity, +`cpwbase`, `jmp pw_sweep`);
  the R token's body JSRs `pulse_tail` instead of `fx_glide`. The composer
  already writes `wjmp` at the same points the orig writes $171F, so the stale
  value coincides. Regression-safe by construction: census over ALL 743
  non-canonical-play f1 members = exactly 1 carrier (Toccata_v2, partial); every
  other build is byte-identical (label emits no bytes; gated routine + `r_call`
  unchanged when the param is absent).
- **Status:** logged (DMC family-1, 2026-07-02: P/F/S round +5 FULL, R round
  +26 FULL → 4198/5401; 2026-07-04 straddle-free pc-trace observer, +0 FULL but
  fixes the `P_S` mis-observation; 2026-07-08 frame-entry reachability, +1;
  2026-07-09 F-entry vib_half variant, +1; 2026-07-10 R-entry pulse_tail
  variant, +1).
- **Consumers:** DMC v4 `factory._observe_play_phases` (canon, py65) +
  `_observe_play_phases_writes` (dataflow, py65) + `_observe_play_phases_pctrace`
  (ground-truth fallback) → `composer_asm` play_phases dispatcher. Sibling of C9
  (measure, don't parse) — C9/pctrace measure from libsidplayfp, C18-py65 from
  interpreter entry-point reachability.

### C19 — Hand-patched player wedge (SMC opcode toggle / skipped-load variants)
- **Canonical:** a scene-circle "editor mod" ships a CANON player with a few
  BYTE-LEVEL WEDGES (a JMP over 2-3 canonical loads, a JSR re-pointed through
  a stub, a store retargeted at another instruction's OPCODE = an SMC toggle).
  Diagnose with the divergence recipe, then: (1) dump the ORIG's bytes at the
  canon site the disassembly says produces the diverging write — a wedge shows
  as a changed opcode (`JMP` where canon has `LDA abs,y`); (2) fingerprint the
  wedge bytes base-relative and CENSUS the whole family for carriers (both to
  size the class and to prove 0-FULL regression exposure); (3) reproduce the
  wedge's SEMANTICS in the composer behind a factory-probed boolean param —
  e.g. `hardrestart_smc_variant`: PW step base never loaded + phase/dir persist + the
  hard-restart TEST write gated by a global flag toggled per note-init from
  the instrument's $04 flag (the orig toggles the STA/LDA opcode at $17FB;
  the composer keeps an explicit `hrtest` byte primed from the file-image
  opcode). Reproduce state-machine EFFECTS, never the SMC mechanism.
- **Trap:** the file-image state of the toggled byte differs per member (save
  moment) — it is PRIMING, so capture it as a param (`hardrestart_test_init`), don't
  assume a constant.
- **Diagnosis tell:** runtime state ≠ file-image table byte while taint_source
  says the byte is STATIC ⇒ the READ SITE differs from canon — dump the
  operand/opcode at the canon site.
- **8th occurrence (round 60, 2026-07-09):** the PW-DIRECTION reset redirect
  (Artlace/End_of_1992_intro + The_Syndrom/Black_It, only carriers in f1):
  the note-init pulse reset's second store `LDA #$00 / STA phase,x /
  STA dir,x` has its direction operand re-pointed at an INERT byte (Artlace:
  the unused $179E-$17AF state gap; Black_It: the post-note guard, which
  note-init unconditionally overwrites to 2 right after) → the PWM sweep
  DIRECTION persists across note-inits while value/bounds/step/phase still
  reset. Tell: at a note-init both streams write the same fresh PW value,
  next frame orig sweeps DOWN (continuing the pre-note direction) where the
  rebuild sweeps UP. `factory._pulsewidth_dir_persist_probe` (anchor `A9 00 9D
  <base+$762> 9D <op>`, reloc-aware, positive minority: op != base+$765) →
  `pulsewidth_dir_persist` param → composer drops the one `sta pwdir,x` line from
  the pulse-reset block.
- **9th occurrence (round 63, 2026-07-09) — INIT-PREFIX subtune force:** the
  wedge is a 2-byte init WRAPPER, not a body patch. Sans_intro's PSID init =
  `$0FFE` (base $1000 − 2): `A9 01` (LDA #$01) falling straight through into
  the canon `$1000: 4C 1D 10` (JMP $101D = tune-select, `A*8→Y`). So EVERY
  play hard-forces tune record 1 regardless of the PSID song number — but the
  extract's `for sub in range(n_subtunes): rec = tunetab + sub*8` walked record
  0, a DUMMY record whose V1/V2 tracks are `$FE` (immediate stop), so V1/V2
  were dropped and the rebuild played the primed idle note under an empty
  orderlist (`orderlist: stop`). This is a DERIVATION wedge (changes WHICH
  record is musical content, not a value), so EXTRACT-ONLY: `_forced_subtune_probe`
  (init≠base + `mem[init]==$A9` + `base` is the canon `JMP base+$1D` dispatch +
  the `LDA #imm` reaches it by fall-through or `JMP base`) → `DMCV4Config.
  forced_subtune` → `extract` walks `rec = tunetab + forced*8`. NO USF field,
  NO composer change (the composer plays the walked content; the forced index
  is an engine artifact per the principle §8). Ground truth: memwatch $1707/
  $170A (runtime track ptr lo/hi) = $1A36 = record 1; pc-trace `$101d f 01`
  (A=1) + `$180d ... 1ac6,Y [1ace]` (Y=8) confirm the force. REGRESSION-SAFE
  BY CONSTRUCTION: `forced` is None for canon init==base (byte-identical) and
  imm==0 reproduces the record-0 walk; the dispatch guard rejects banking /
  other LDA#-leading wrappers. Census over 5833 f1: exactly 2 carriers, both
  previously partial (Sans_intro fall-through form, Devilock/Sub_Effect
  JMP-to-base form) ⇒ 0 FULL exposure. Sans_intro FULL 255559/255559 state ✓;
  full `tools/regression.py` green (0 regr all 8 families). TELL: a rebuild
  that plays a voice's PRIMED IDLE NOTE under an empty orderlist while orig
  plays a full part on that voice = a wrong-tune-record walk — memwatch the
  runtime track-ptr ($1707/$170A) + pc-trace the init A at the tune-select.
- **10th occurrence (round 65, 2026-07-09) — $D418 RE-ASSERTED EVERY FRAME
  (COMPOSER param, not extract-only; also C10 master-vol-every-frame form):**
  Groove/Bakewell_Dwayne (+ Rap/Hands_up_Ravers, Rorschach/For_Vandalism_27 —
  the only 3 f1 carriers). The wedge changes a write-stream TIMING, not a
  derived value, so it needs a composer param. The play-body global filter
  routine's `STA $D417` is replaced by `JSR <wrapper>`, and the wrapper does
  `STA $D417 / LDA #mode / ORA mvol / STA $D418 / RTS` → `$D418 = mode | mvol`
  is re-written EVERY frame (at the filter-tail END); the canon filter note-init
  `STA $D418` ($12A8) is neutered to `BIT $D418` and its preceding `STA $2004`
  self-modifies the wrapper's mode immediate per note-init. `factory.
  _master_vol_reassert_filter_tail_probe` → USF param `master_vol_reassert_filter_tail` (initial mode imm) →
  composer: note-init stores `fdmode` to a `d418mode` shadow (suppress the
  note-init `$D418`), the per-frame filter tail re-asserts `lda d418mode / ora
  mvol / sta $d418`, init primes `d418mode`. Sibling of `master_vol_every_play` (the
  play-VECTOR wrapper form, `$D418` at play START); this is the filter-tail END
  form. Default None → byte-identical. **PROBE-ANCHORING LESSON (why the STATIC
  opcode probe must target the REACHABLE site, not a byte pattern):** the first
  LOOSE probe (`STA $D417 .. STA $D418` anywhere) false-fired on Qbhead_01's
  aux/init routine (`STA $D416 / LDA #imm / ... / STA $D418` at $1CA8) whose
  live per-frame routine is canonical — it would have REGRESSED a FULL member.
  Anchoring on the play-body computation shape (`STA $D416 / LDA abs / ORA abs /
  JSR-wrapper` at +9) excluded it. Caught by localizing each census carrier's
  first divergence BEFORE committing (the orig had no per-frame `$D418`). f1 3
  carriers all previously partial ⟹ 0 FULL exposure; Groove FULL 155620/155620;
  full regression green (0 regr all 7 families).
- **11th occurrence (round 70, 2026-07-10) — SWITCH ($7D) GATE-MASK TOGGLE
  IMMEDIATE (COMPOSER param):** Bax/Feed_a_Bird (the ONLY carrier in all 5833
  f1 members). The tie/legato handler at base+$183 canonically toggles ONLY the
  gate bit: `LDA gatemask,x / EOR #$01 / STA gatemask,x` (mask $FF<->$FE = gate
  as the wave table says <-> force gate off). The wedge patches the EOR
  immediate $01->$1F (byte at base+$18D), so a SWITCH toggles
  gate+test+ring+sync+triangle ($FF<->$E0) — CUTTING a triangle/ring/sync note
  to SILENCE ($17 & $E0 = $00) where canon merely releases the gate
  ($17 & $FE = $16). Presents as V3 ctrl orig $00 vs rebuild $16 at a legato
  boundary (localize the flat write-stream, then memwatch the gate mask $100f+v
  across the transition — it goes $FF->$E0, NOT ->$FE; the pc-trace shows
  $118C = `49 1F` not `49 01`). MISSED by `dmc_canon_diff` — an immediate-value
  tweak (unchanged opcode $49, no operand repoint) sits in its documented blind
  spot. Fix: `factory._switch_toggle_mask_probe` (STATIC opcode probe, anchors
  on the LDA/STA operands = gatemask_addr, reloc-aware, guards gatemask_addr
  None) → new USF param `switch_toggle_mask` (the toggled bit-set; default $01)
  → composer's `ev_switch` emits `eor #<mask>`. Default $01 -> byte-identical
  text. REGRESSION-SAFE BY CONSTRUCTION: the composer applies the probed mask
  verbatim so its $D404 write can only match the orig MORE often, never less;
  and $E0 vs $FE coincide for noise/pulse/saw notes (only bits 5-7 survive
  either mask), so the value only bites on sync/ring/test/triangle notes.
  Census 5833 f1: 1 carrier (partial), 5502 canon $01, 0 FULL exposure.
  Feed_a_Bird partial -> FULL 130578/130578 state ✓; full regression green
  (0 regr all 8 families: Hubbard 71, Companion 44, C64ME 15, Jay_Derrett 17,
  FC 31, DMC 12, Basic 22).
- **Status:** CANONICALIZED (11 occurrences: DMC family-1 rounds
  13 + 19 + 32 + 35 + 36 + 50 + 55 + 60 + 63 + 65 + 70). Canonical form: STATIC opcode probe (read the patched
  instruction itself — never a bounded write-stream scan, which can
  false-negative on members that exercise the path only late) → factory
  `extra_params` → an existing/new composer param; census carriers on BOTH
  sides (partials = recovery set, FULLs = exposure set to re-verify+rewrite).
- **2nd occurrence (round 19):** the holding gate-off 1-BYTE patch —
  sub_17EC's `$17EF: BC->60` (LDY→RTS) turns `gate mask + AD/SR=$00` into
  mask-only. A widespread editor build (Surgeon/Imaic/Rio/Taxim/Phobos/
  Behdad_Arman: 514 FULL + 97 partial carriers); 179 of the FULLs had been
  rescued only by the batch's blind `frames_clear_adsr` mask_only retry,
  and the 97 partials were exactly the members that retry could NOT reach
  (their origs write AD/SR=$00 through OTHER paths, so the stream scan
  gates off). `factory._hold_gateoff_probe` follows the holding-branch JSR
  by opcode shape (layout-blind, C13 corollary) and classifies the byte
  after the gate-mask STA. The param (`hold_gateoff='mask_only'`) already
  existed for family-2 — the probe just feeds it for family-1 carriers.
- **4th occurrence (round 35):** the dual-effect FREQ-GENERATOR wedge
  (Taurus/Taurus_02, the only carrier in ALL 10,676 DMC members): the dual
  ($40) odd-parity path's `LDA $172F,x` opcode patched BD→A6 (`LDX $2F`;
  zp $2F = $A9 under the PSID environment) so every subsequent per-voice
  read lands +$A9 past the state arrays — onto fixed CODE bytes (slide
  speed = a JMP opcode, base hi = a CMP operand, PW/ctrl = sub_17EC/17FB
  bytes) — while the "slide accumulator" self-modifies two tune-setup code
  bytes (file-image values = the seed) and the update ORs in a BASIC ROM
  byte ($BD68,y) and rotates a feedback byte via an ILLEGAL RRA on zp $12.
  Net: one GLOBAL free-running pseudo-random freq ramp on dual frames +
  pwphase[V3] clobbered to $42/$43 (live-carry-dependent), driving the
  pulse machine's speed fetch off the instrument record (static bytes past
  the table). Fix: `factory._dual_freq_gen_probe` (wedge-anchored regex, all
  effective constants captured from the image) → `dual_freq_generator` param
  (renamed from `dual_hack` 2026-07-06, C7-note decision) →
  composer emits the generator as CLEAN code (legal ror+adc = RRA,
  inlined constants, live-carry pwphase store) + `dual_generator_steps`
  (extract-captured static bytes) EXTENDS the stride-8 isteps/irawsp
  tables at the reachable garbage-phase indices — zero pulse-code change.
  Python-simulate the generator against ALL observed dual events (3826/
  3826) BEFORE composing. Default byte-identical (3-member MD5).
- **5th occurrence (round 36, 2026-07-06):** the hard-restart AD/SR
  IMMEDIATE patch (Stryyker, 4 carriers, all family-1, all value $0A):
  sub_17FB's `LDA #$0F` operand ($17FF) patched to $0A, so every
  note-fetch frame primes AD=SR=$0A instead of $0F/$0F. The simplest C19
  form yet — one immediate byte. `factory._hr_preset_probe` anchors on the
  routine's opcode shape (`[99|B9] 04 D4 A9 vv 99 05 D4 99 06 D4 60`,
  layout-blind; first opcode admits $B9 for the _hardrestart_smc_variant_probe SMC
  variant) and feeds the value through the EXISTING `hard_restart` param
  (domain extended: 'preset'/'none'/numeric — no new schema field);
  composer renders `lda #$vv`. Guarded against family-2's preset
  'none'. Default renders identical text → byte-identical. Census over
  all 10,676: 4 carriers, 0 FULL exposure; 3 flipped FULL, Sans_intro has
  an unrelated pre-existing first blocker (identical flat_div before/after).
- **3rd occurrence (round 32):** the PW-hi SOURCE patch (Olsen/Lame, 1
  family-1 carrier): the sidwrite tail's `LDA $1753,x / STA $D403,y`
  operand re-pointed at base+$707 (the track-ptr lo triple, constant after
  init) — each voice's audible PW hi pinned at a per-voice constant while
  the internal PWM machine still runs on $1753. `factory._pulsewidth_hi_const_probe`
  anchors on the `$D402/$D403` store pair + the canon PW-accum-lo operand,
  captures the POST-INIT bytes at the patched operand → `pulsewidth_hi_const='a,b,c'`
  param; composer swaps the pwwrite source to a 3-byte table. Default
  byte-identical; base-relative census proved exactly 1 carrier.
- **COROLLARY — a probed knob must be honored on EVERY orig path that funnels
  through the patched site (2026-07-06, Chojnow_Music_Compo_1).** A wedge is
  ONE instruction, so every orig code path reaching it inherits the variant
  behaviour; the composer's re-architected handlers must EACH route through
  the parametrized target. The `rest_effects='skip'` JMP ($117D → $1591) is
  shared by rest, switch, slide AND the $7C soft-note fetch — composer's
  `ev_n_softq` hard-coded `jmp run_effects`, so soft-note fetch frames stepped
  the pulse where the orig held it (V2 PW one step ahead from the first soft
  fetch, flat div 266023). Fix = `jmp {rest_jmp}` (byte-identical for canon
  'run'). When landing a knob, grep the composer for ALL jumps to the
  canon-target label and check each against the orig's funnel paths.
- **6th occurrence (round 50, 2026-07-08):** the PWM bound-A SHIFT wedge
  (Aomeba/20_Years_of_NOP, the ONLY carrier in all 5401 family-1 members):
  note-init byte $124D patched $4A->$17 (LSR -> the 2-byte illegal SLO $4A,X,
  which ASLs an UNUSED zp scratch byte + ORs 0 into A = inert; zp $4A-$4C are
  unreferenced by the player), so the bound-A extraction runs LSR x2 not x4:
  bound A = byte+2 >> 2 (not its hi nibble), bound B = A EOR $0F. Effect: the
  PWM sweep hi-byte bounces over a much WIDER band before flipping (inst
  byte+2 $77 -> canon bounds 7/8, wedge bounds $1D/$12; the rebuild flipped at
  pwh=8 where the orig ramps 7->8->9->10..., first div V2 PW frame 4). CLEANEST
  C19 outcome yet — EXTRACT-ONLY: the bound values ARE musical content (USF
  min_hi/max_hi), so the probe only fixes their DERIVATION; no USF field, no
  composer change. `factory._pw_bound_shift_probe` anchors on the
  STA $1756,x / EOR #$0F / STA $1759,x tail (reloc-aware, operands
  base+$756/$759), decodes the 4-byte PLA->STA window counting LSR-A ($4A;
  $17 = known 2-byte filler, any unknown opcode bails to canon). Threaded as
  EXTRACT-ONLY `cfg.extra_params['pw_bound_shift']` (POPPED before the USF
  params block so the derivation knob never leaks to ML — the derived bounds
  already carry the music). Census: 1 carrier, 5400 canonical (shift=4 =
  byte-identical) => regression-safe by construction. 20_Years_of_NOP
  partial -> FULL 294517/294517.
- **7th occurrence (round 55, 2026-07-08):** the hard-restart prep-CALL SKIP
  wedge (SilverFox/Seaside_99 + 8 more, 9 family-1 carriers). The note-load's
  hard-restart primer `LDA #$08 / JSR sub_17FB / LDA #$FF` (base+$1D9..$1DF;
  sub_17FB writes TEST $08 + AD/SR $0F0F on the fetch frame) has its JSR opcode
  patched $20->$2C = `BIT $17FB`, neutering the ENTIRE call: the fetch frame
  writes NOTHING (no TEST, no AD/SR), while pending (base+$4A) is still set so
  the note inits normally next frame and the old note rings through the fetch
  frame. Presents as the rebuild emitting an EXTRA 3-write prep block
  (D40x=08/0F/0F) at each note-fetch frame that the orig lacks — localize
  per-IRQ (Trap-C-free) so the extra writes don't smear across frame buckets;
  the pc-trace ($11DB = `2c fb 17` not `20 fb 17`) is the ground truth (the
  memwatch showed pending going FF = hard-restart path taken, which
  contradicted "no prep" until the pc-trace revealed the neutered opcode).
  Distinct from 'none' (family-2, keeps the $08 TEST write) and the numeric
  preset wedge (5th occ, patches sub_17FB's immediate, call intact). Fix:
  `factory._hr_prep_skip_probe` (STATIC opcode probe, reloc-aware base+offset,
  verifies the shape both sides: LDA #$08, the sub_17FB operand = base+$7FB,
  LDA #$FF) → the EXISTING `hard_restart` param, domain extended to a 4th value
  'skip'; composer suppresses BOTH `hr_test_write` and `hard_restart_adsr` in
  `ev_n_hard`. NB some carriers ALSO patch sub_17FB's first byte $99->$60 (RTS)
  — irrelevant since the call is neutered, so the census keys on the call-site
  opcode + the reloc-invariant `op - code_start == $622`, never on sub_17FB's
  shape. Census over all 5401 f1: exactly 9 carriers (Welcome_to_Egypt, Bayliss
  DMC_Collection_3_intro / DMC_V4_0_Collection_note / Tarkus_4K /
  Snowball_Caper_2, DaFunk I_Dont_Need_Love / 3-Speed, SilverFox Poison_Girl /
  Seaside_99), ALL partial (0 FULL exposure) => regression-safe by
  construction; ALL 9 partial -> FULL. 0 f2 carriers.
- **Consumers:** DMC v4 `factory._hardrestart_smc_variant_probe` + composer_asm
  hardrestart_smc_variant/hardrestart_test_init gating; `factory._hold_gateoff_probe` →
  `hold_gateoff` param; `factory._pulsewidth_hi_const_probe` → `pulsewidth_hi_const` param;
  `factory._hr_preset_probe` (numeric) + `factory._hr_prep_skip_probe`
  ('skip') → the shared `hard_restart` param (domain
  preset/none/numeric/skip). Sibling of C18 (wrapper OUTSIDE the player) —
  C19 is patches INSIDE the canon body. The round-14 $D418 play-vector prefix
  (`LDA #imm/STA $D418/JMP base+3`, factory `_d418_play_wrapper` →
  `master_vol_every_play`, +6 FULL, commit efbf639) is the degenerate stateless
  case: a wrapper with NO phase behaviour — probe the PSID play vector's
  target shape whenever a member's play ≠ base+3 OR the JT entry target ≠ the
  canon play body.

### C20 — Stale-FULL palimpsest (a 'full' row the CURRENT code cannot reproduce)
- **Canonical:** a member's recorded FULL status was earned by an OLDER
  code/verdict combination; the stored artifacts may even still match the orig,
  but re-extracting + rebuilding with CURRENT code yields a partial. The row is
  a PALIMPSEST — it hides the member from every residue census (it never
  appears in a partial cluster) and silently mis-scopes regression claims.
  Occurrences: 0ldsk00l_endtheme (round 9, pre-otrk partial recorded full),
  Happy_Hour (round 16 — exposed the >85-entry track-capacity latent), Yo_Raps
  (stored build diverged at write 0!), Brendas_Got_a_Baby_Mix (round 17 —
  exposed the $175C off-table gap). CANONICAL HANDLING:
  1. When ANY currently-FULL member fails a re-verify, FIRST verify its STORED
     build against the orig. Stored-matches + fresh-fails = a CURRENT-CODE
     latent regression (bisect: USF-diff old vs fresh USF → param-strip bisect
     → divergence-context read); stored-fails = the row was stale — re-bucket
     honestly (tally goes DOWN) and treat the member as a fresh diagnosis.
  2. Attribute before blaming the newest change: the USF diff exonerates or
     convicts extract-side changes in one step.
  3. Periodically re-verify FULL slices with current code (the round-16 727
     sweep found 2 palimpsests); a full-family closeout batch is the complete
     cure.
- **Companion discipline (verify/build code-mismatch):** NEVER mass-write
  artifacts with code that did not produce the verify verdict being trusted —
  a batch's workers import modules at start, so a mid-batch code change (or a
  stashed/popped tree, or committing between verify and write) silently writes
  UNVERIFIED builds recorded as FULL. Re-verify status-changed members with
  the CURRENT tree before mass-writing them.
- **THE "MY FIX REGRESSED N FULLS" TRAP (2026-07-04, round 23 — cost hours,
  TWICE in one session).** When a genuinely-CORRECT shared-code fix appears to
  regress FULL members, the near-universal cause is NOT the fix — it is (a) a
  STALE baseline or (b) a batch flake, and often (c) the "regressed" members
  were FULL through a SUBOPTIMAL path the fix legitimately removes (the user's
  load-bearing insight). Concretely: the round-23 otrk fix "regressed 22 glide
  members + Zak_2 + Bilinski". Reality: all 22 glide members were STALE (a grep
  of stored `.usf` files claimed FULL; CURRENT code builds them partial — I
  compared against `.usf` status, not a fresh build); Zak_2 was a PARALLEL-BATCH
  siddump FLAKE (FULL on a single-threaded re-verify); Bilinski was a stale-full
  palimpsest. NET: 0 real regressions, +12 recoveries. MANDATORY before
  believing ANY regression: re-verify the suspect with a FRESH SINGLE-MEMBER
  current-code build (`find_first_divergence` or a 1-member batch) — never
  against stored `.usf`/DB status, never trust one parallel-batch verdict.
  Corollary: derive a "FULL members" list from a fresh batch, NOT from grepping
  `hvsc84/*.usf` (those are palimpsest-prone).
- **ROOT CAUSE (why palimpsests appeared ~2026-07-03, not before) + STRUCTURAL
  FIX (2026-07-04).** The rapid family-1 rounds switched from *clean full-batch*
  closeouts (jsonl DELETED → every FULL re-earned) to *incremental-merge*
  closeouts for speed (`tmp/merge_r22_reverify.py`: `merged = dict(old)` then
  overlay only the re-verified members → un-touched FULLs keep OLD verdicts
  across code changes). Plus ad-hoc shortcuts that trust persisted artifacts as
  the FULL baseline: `tmp/verify_ondisk_usf.py` (rebuilt from the STORED `.usf`
  → old extract) and `glob hvsc84/*.usf` existence as a "was FULL" proxy. All
  three are the same anti-pattern: a persisted verdict no fresh process
  re-earns. STRUCTURAL FIX: (1) batch results jsonls stamped with a `code_hash`
  (`src/code_fingerprint.py` = hash of the engine's `pipelines/<engine>` +
  `src/usf` + `verify_cycle` dep set); resume reuses a row ONLY on hash match,
  so a code change auto-re-verifies affected members (no "remember to delete the
  jsonl"; parallel-session-safe). (2) `*_mass_write.py` skip + warn on stale-hash
  FULL rows → never write an unverified `.usf`. (3) the HVSC index dropped ALL
  build-status columns + the `record_*` write-through (2026-07-04) — it's a
  static catalogue now (`hvsc84.parquet`), so it can no longer be a stale-verdict
  surface. Deleted `tmp/verify_ondisk_usf.py`. See [[reference_hvsc_db]].
- **Status:** canonicalized (6 occurrences, 2026-07-02/04, DMC family-1).
- **Consumers:** DMC family-1 rounds 9/16/17/23 handling; the round-16 sweep
  runner `tmp/f1_round16_sweeps.py` (re-verify → then rewrite).

### C22 — Ambiguous round-trip flag encoding (decoder misroutes one op onto another's path)
- **The bug class:** two DISTINCT engine operations are rendered to USF with
  OVERLAPPING flag sets (op A → `noretrig glide=N`; op B-under-mode →
  `noretrig glide=N glide_to=X`), and the composer-side decoder branches on a
  SUBSET of the true discriminator (`noretrig and glide` instead of
  `noretrig and glide and NOT glide_to`) — so op B takes op A's runtime path.
  Deadly because the two paths COINCIDE for most content (DMC: slide-from-
  current == rebase-to-A + glide when the previous note equals note A), so
  members verify FULL until one hits the distinguishing case, presenting as a
  DEEP heterogeneous divergence (Gangstallica at 28k: rebuild held the old base
  and stepped DOWN where the orig rebased to note A and stepped UP).
- **Canonical fix:** make the decoder's branch test the EXACT injective
  discriminator (here: absence of `glide_to`). Better: when adding a flag
  rendering in to_usf, check the flag COMBINATIONS are injective over the
  engine ops — if two ops can render identically, the representation (not the
  decoder) is the bug.
- **TELL / how it presents:** a deep first divergence where the rebuild's value
  derives from the PREVIOUS musical state (old base freq) while the orig's
  derives from the row's own data (new note's base) — i.e. "the rebuild missed
  a re-anchor". Cross-check the USF row's flags against BOTH engine ops'
  renderings before suspecting the runtime.
- **Status:** CANONICALIZED (3 occurrences, DMC family-1 rounds 18 + 19):
  (1) mode-0 glide under soft-start vs mode-1 slide — decoder tested
  `noretrig and glide` but the true discriminator adds `NOT glide_to`
  (+138 FULL, 2 exposed FULLs held); (2) mode-1 slide with SPEED NIBBLE 0
  (engine op = "set target, no note load, hold" — the $Dx handler jumps to
  the REST tail) rendered identically to a plain soft note because to_usf
  suppressed `glide=0` — the composer then LOADED the note early
  (Apocalypsa: octave drop 10 frames before the orig). Canonical form:
  emit the distinguishing flag ALWAYS (`glide=N` incl. 0 on slide rows)
  and decode on flag PRESENCE, not truthiness. When adding any fx_flags
  rendering, check injectivity over the engine ops FIRST.
  (3) round 19, the mode-0 twin of (2): a $Cx GLIDE with speed nibble 0 is
  the engine's GLIDE-CANCEL (the $Cx handler unconditionally stores the
  nibble to glsp) — to_usf suppressed `glide=0` on mode-0 rows AND the
  composer's pattern encoder keyed the glide tail on `if gspd` — so the
  cancel became a plain note and a previous row's armed glide kept ramping
  the freq accumulator (+speed×16/frame) in the rebuild forever
  (Grave_Story_intro, div at 6427 → FULL 130165/130165). TELL: deep freq-LO
  divergences whose (mine−orig) deltas are QUANTIZED TO ×16 across a
  member class (the speed-nibble ASL×4) = a glide/slide step-count or
  arming drift; census the delta histogram before per-member drilling.
  Fix keys BOTH sides on presence: to_usf emits glide=N whenever
  glide_to is set; the encoder emits the [gspd,target] tail whenever
  target is not None. 0-regression by construction: a FULL with a
  $C0-speed-0 row could only have matched if no glide was armed there
  (else its old always-ramping build couldn't have been FULL), and the
  cancel is then a no-op.

### C23 — A play-phase TOKEN hides a per-member behavioural ambiguity (2-frame note-start)
- **The problem class:** a C18 play-phase schedule token (`P_F123`) is treated
  as fully specifying what each call does, but the SAME token maps to TWO
  distinct play-routine behaviours across members. DMC F phase: some members'
  play-routine enters the F call at the note-init check (`$11F9` → note-init on
  the F call = IMMEDIATE note-start), others enter PAST it (`$1591` wave-step),
  so a note fetched on a P call only ARMS on the F call (wave-step only, ADSR
  held at the `$0F0F` hard-restart leftover) and note-inits on the NEXT P call
  = a 2-FRAME note-start. The blanket model (F → frame_entry) is right for the
  majority and wrong for the deferring class.
- **TELL / how it presents:** you fix the minority class and it REGRESSES
  currently-FULL members carrying the SAME token (Words and F.A.K.E-Intro are
  both `P_F123`, opposite behaviour). The regression is the signal that the
  token is INCOMPLETE, NOT that the fix is wrong (the round-23 lesson: a correct
  fix that regresses ⇒ the regressed members are FULL through a blanket/
  suboptimal model; reimplement to serve BOTH). Sibling of C22 (an encoding
  that renders two ops identically) — here the "encoding" is the phase token.
- **Canonical fix:** do NOT pick one behaviour or add a schedule-string
  heuristic — the distinction is not derivable from the token OR the editor
  setting (Words/F.A.K.E are both `P_F123` AND both 1.82 calls/frame). OBSERVE
  the distinguishing behaviour per member (C18: observe, don't parse) from the
  WRITE FOOTPRINT (reloc-invariant, no PCs): the opening note-start's first
  freq/ctrl re-emit after a voice's HR call (ctrl=`$08`, AD=SR=`$0F`) is the
  note-init IFF it also writes AD/SR; freq/ctrl with NO AD/SR = the arm ⇒
  deferred. Emit a per-member param; the one composer routes on it (F →
  wavestep when deferred, frame_entry otherwise). **Regression-safe by
  construction:** note-init ALWAYS carries AD/SR, so the "deferred" verdict has
  no false positive — the immediate majority is provably untouched.
- **METHODOLOGY:** measure the candidate discriminator (multispeed factor,
  schedule string) against BOTH the fixed set and the regressed set BEFORE
  designing the fix — if they overlap, it's a per-member observable, not a
  derived rule. Focus the verdict on FIRST-DIVERGENCE resolution, not FULL: the
  fix resolved the note-start for all 15 cluster members (0 regr) even though
  only 4 reached FULL (the other 11 advanced to a separate freq-drift blocker).
- **Status:** logged (DMC family-1, 2026-07-05: +4 FULL [2_Speed / Voices /
  Canned / Compotune], 0 regressions across all 56 currently-FULL F-token
  members + full `tools/regression.py`). Commit 1a632fe.
- **2026-07-06 refinement (commit 17fd27e):** the observation must cover ALL
  voices, not stop at the first voice with an observed HR. With a PARTIAL F
  phase (`P_F3`) only the F-phase voice defers — the others note-init directly
  on P calls and read "immediate", so a first-voice verdict misses the arm
  (Dresden_Party: V2 immediate, V3 arms → detector said immediate). Fix: any
  voice's arm footprint ⇒ deferred (still no false positive — note-init always
  carries AD/SR). 0 verdict drift over all 62 stored F-token carriers;
  Dresden_Party_95_II FULL, Dresden_Party first-div 13 → 78261 (freq-drift
  second blocker).
- **2026-07-06 refinement 2 — the observation WINDOW must reach the first HR:**
  the fixed 12-frame capture ends before a soft-start opening's first hard
  restart (Wavefrontline: first HR at play ~41), so the detector read
  "conservative immediate" for a member that defers from its very first soft
  note (the arm also delays the GATE-MASK 0→$FE transition — the divergence is
  visible at play 1, long before any HR, but the HR footprint is the only
  observable discriminator). Fix: ESCALATE the window (12 → 96 frames) only
  when the short pass is inconclusive (some voice with no HR or no emit
  following); a definitive all-voices-immediate verdict stops the escalation,
  so members the short window already decides are byte-identical. 0 verdict
  drift over all 76 stored F-token carriers; among 166 partials exactly ONE new
  arm carrier (Wavefrontline → FULL 288100/288100); the 8 other arm partials
  were already detected at 12 frames (deeper blockers, builds unchanged).
- **Consumers:** DMC v4 `factory._detect_noteinit_deferred` → `noteinit_deferred` param
  → `composer_asm` voice_fx routing. Refines C18.
- **Generalised:** this entry + round-23 otrk are the worked examples behind the
  [`/amend`](../.claude/skills/amend/SKILL.md) skill (the methodology for "my
  first-divergence fix regressed other members").

### C24 — Play-body UNIT-repeat (the play body runs one unit N× per play())
- **The problem class:** a hand-patched DMC player redirects one of the play
  body's per-frame `JSR`s to a stub that calls that routine N times. The play
  body runs FOUR units per frame — voice 0, voice 1, voice 2, then the global
  filter tail ($D416/$D417) — so the hack makes one unit run N times: a
  "double-speed voice" (`JSR <voice> ×N`, so its wave/pulse program advances N
  steps/frame and its full block is emitted N times), and/or — via a stub that
  ends in `JMP <filter-tail>` instead of RTS — the filter tail re-runs (the
  leftover play-body JSR return address makes the tail's own RTS re-enter it, so
  $D416/$D417 write twice). DISTINCT from `play_repeat` (repeats the WHOLE
  play() — all four units together) and from C18 `play_phases` (the play VECTOR
  cycles whole CALLS across successive play()s; here it's ONE unit multiplied
  WITHIN a single call).
- **Canonical:** ONE unified `play_unit_repeat` params list of 4 ints
  `[v0,v1,v2,filter]` (default `'1,1,1,1'`). The composer emits the play body's
  voice-call sequence and the filter-tail block from it; `'1,1,1,1'` is
  byte-identical to the fixed single-pass body. The two example members differ
  only in the last slot: Talk_a_Lot `1,1,2,1`, 3rd_Voice `1,1,2,2`. Factory
  detects it with a STATIC byte-probe (C19 method): follow the play vector,
  locate `STX fclaim` (base+$720), read the three per-voice JSR sites, and for a
  redirected site count the `JSR <voice>` inside the stub — terminator RTS
  (clean) or, on the LAST voice only, `JMP <filter-tail>` (= filter slot 2). Any
  other stub shape ⇒ None (build unchanged).
- **CORE-TENET framing (why `filter_tail` is first-class, not a compromise):**
  both the voice slots and the filter slot are per-engine config fields that
  parametrise a WRITE-LOG difference (unit's writes emitted N×) and encode NO
  code layout (the value is a count, never the stub address / JMP target). That
  is exactly the sanctioned class (`nextvoice_write_order`,
  `held_note_clears_stod404_gate`). The filter re-write is inaudible (identical
  values) but the strict-write-stream policy requires reproducing it, and the
  composer produces it with CLEAN inline code — it does NOT mirror the stack
  re-entry trick (the tenet's "emit clean code that produces the writes, don't
  reproduce the mechanism"). An early "filter_tail is less musical / bookkeeping"
  hesitation was the re-anchor tell: applying the §7 musical-content lens to an
  engine-config field, where the CORE TENET is the governing one.
- **Status:** recurring (DMC family-1, 2026-07-05: Talk_a_Lot `1,1,2,1` +
  3rd_Voice `1,1,2,2`, both FULL). Regression-safe by construction: `'1,1,1,1'`
  is byte-identical (proven via old-vs-new MD5 on canonical members) and the
  actual probe run over all 4802 FULL members fires on exactly ONE (Talk_a_Lot
  itself). A layout-independent write-stream recheck confirmed these are the
  ONLY two family-1 members with the feature (others with doubled writes are
  whole-play multispeed `[N,N,N]` = `play_repeat`, or a bespoke test player).
- **Consumers:** DMC v4 `factory._play_unit_repeat_probe` → `play_unit_repeat`
  param → `composer_asm` play-body `voice_calls` + `filter_tail`. Reuses the C19
  static-probe + factory-param canonical form (a WRITE-STREAM difference, not the
  same wedge shape). FACTOR at Move 1 if a 3rd variant appears (a voice ×3, or a
  unit-repeat on a relocated/2-entry layout the STX-$1720 probe can't locate).
- **SIBLING — whole-play N-repeat via a base+3 JMP indirection (2026-07-08,
  round 52, +10 f1 FULL, 0 regr).** The WHOLE play() (all four units) run N× per
  VBI = a double-speed TUNE, detected by `factory._detect_play_repeat` (the
  `play_repeat` param, distinct from the per-UNIT C24 above). The probe follows a
  play-VECTOR wrapper of `JSR T ×N :RTS` or `JSR T; JMP T` and returns N. BUG it
  fixed: the guard `if play == base+3: return 1` short-circuited members whose
  base+3 is itself a `JMP <double-play wrapper>` (Scan_Collection_end: $1003 =
  `JMP $2000`, $2000 = `JSR $1050; JMP $1050`). Even the CANON player has
  `$1003: JMP $1085`, but $1085 is the plain body (`DEC` speed-counter) — the
  loop already follows a leading JMP once and returns 1 for a plain body, so the
  short-circuit only skipped a walk that would have returned the same answer.
  FIX: guard on `play == base+3 and mem[play] != 0x4C` — a non-JMP base+3 still
  short-circuits; a JMP base+3 falls through and the existing loop follows the
  indirection (1 for a plain body, N for a genuine wrapper). REGRESSION-SAFE BY
  CONSTRUCTION: a double-play built single-speed is ALWAYS a length partial
  (½ the writes), never a FULL, so no FULL can flip. Census over all 5401 f1:
  exactly 10 carriers (Lio ×3 / Logan / PRI ×2 / The_Syndrom ×4), all
  partial→FULL. TELL: perfect play-stream PREFIX + a clean ~N× length tail on a
  VBLANK member ⇒ whole-play multispeed, not a missing effect — count
  writes/frame, then disassemble the play VECTOR and FOLLOW its JMP.

### C25 — The composer's play body must FIT the tightest CIA latch it ships under
- **The problem class:** a high-multispeed CIA member (latch ≪ a PAL frame, e.g.
  Revolution-Evolution 2456 = 8×) gives the play() handler a hard cycle budget.
  When the composer's body chronically exceeds it, the next CIA IRQ is delayed
  (fires immediately after RTI) — the rebuild's effective play rate slips below
  the latch rate. **Presentation:** a batch "regression" with a PERFECT
  play-stream prefix over the full overlap, state match, and ONLY a length tail
  (~0.5%) beyond the CIA close tolerance. No `(reg,val)` content divergence
  exists — per the trichotomy this is an ENVIRONMENT (rate) failure, so don't
  chase effect emitters; measure the average play-entry period
  (`--per-irq-debug`, sum nentries / cycle span) of orig vs stored artifact vs
  fresh build. Orig == latch, fresh > latch is the tell (Revolution: 2456.9 vs
  2464.1).
- **Root cause seen (2026-07-07):** common-path cycle CREEP — the off-table
  redirect compare chain (`_gen_offtable_redirect`) sat on the per-voice
  per-frame wave-step read path and cost ~4-5 cycles PER MAPPED ROW for every
  in-table read; rounds 31→39 grew the map (wjmp/sectpos/wavepos/fxf/fsz), each
  row taxing EVERY member. The accumulation pushed tight-latch members over
  budget while all content stayed exact.
- **Canonical fix:** make the COMMON case O(1) — one leading bounds check
  (`cpy #min_mapped_off / bcs chain`) jumps straight to the static in-table
  load; the full chain runs only for mapped-window candidates. Content-identical
  BY CONSTRUCTION (the fast path serves exactly the Ys that fell through every
  row anyway) — the change is pure cycle timing, free under Mode 1 within a
  frame, and restores the entry rate (2456.9/2810.0 == latch on both carriers).
- **Boundary / the mirrored class:** members whose ORIG play chronically
  overruns its own latch (Compotune_1: latch 4913, orig runs ≈5393) need the
  rebuild to be exactly-as-slow — rate-matching an overrunning handler is NOT
  covered by this entry (those members were never FULL; honest residue).
  Guard when adding ANY code to a per-voice per-frame path: ask what it costs ×
  3 voices × the tightest corpus latch.
- **Status:** logged (1×, DMC family-1: Revolution-Evolution + Ucieczka_z_Tropiku
  both FULL after the fast path; regression green).

### C26 — Song data ABSENT from the file image (init GENERATES/unpacks it in RAM)

- **Problem shape:** the player is a known variant (canon/2entry body matches),
  its data-table operands are internally CONSISTENT — but they point OUTSIDE
  the loaded image (or at zero fill): the member's init generates or unpacks
  the song data into high RAM at runtime. Any file-image extraction reads
  nothing. Seen as `nonstandard_instr_base` refusals (DMC family-1 Flash trio:
  instr $B961/$A70B/$ACEA, ALL six table operands out of image) and, composed
  with a banking wrapper, `nonstandard_vectors` (Itinerant: init copies
  $1900→$7100 behind `LDA #$35/STA $01`).
- **Canonical fix:** read what the ENGINE reads — run the member's OWN init
  under py65 and extract every data table + priming byte from the POST-INIT
  RAM (`DMCV4Config.data_post_init` → extract swaps its whole memory for
  `_postinit_window(s, 0, 0x10000)`). Detection signature is all-or-nothing:
  EVERY data operand outside the image ⇒ unpacker (a mixed layout stays
  refused). Skip the canonical packing-order (layout) check for this class —
  the unpacked tables sit wherever the unpacker put them. Verify-gated; both
  acceptance paths run only where the extractor previously refused, so FULL
  regressions are impossible by construction.
- **Related prior forms (same principle, narrower scope):** `_postinit_window`
  on the filter defs (Ed members' init stamps res/cutoff over the records),
  `post_init_state` priming capture (dataflow members whose init clears
  leftovers), round-40 filter_mod contour (init-generated triangle table).
  This entry is the WHOLESALE form: all tables at once.
- **Banking-wrapper base candidate (C13 tier, same session):** a play vector
  `LDA #$35/STA $01/JSR t/LDA #$37/STA $01/RTS` whose jump table was
  overwritten by the wrapper/init code names the play handler explicitly:
  base = t−$50 (2entry) / t−$85 (canonical), validated by the masked identity
  compare downstream.
- **Status:** logged (1× wholesale, 4 members: Haste/Kan-Kan/Wind_of_Dead
  303301+53319+484596 FULL, Itinerant 174180 FULL; narrower forms 3× prior).

### C27 — Multi-SID (2SID/3SID): N independent players, one per chip

- **Problem shape:** a member declares 2/3 SID chips (PSID v3/v4 header
  +$7A/+$7B) and its play vector is a dispatch WRAPPER calling two/three
  complete sub-players, each writing a different chip ($D400 / $D420 /
  $D440). The player families are otherwise ordinary (DMC 2entry here). One
  sub-player's jump table is often overwritten by the wrapper.
- **Decomposition (the key insight):** a multi-SID tune = N independent
  single-chip tunes playing simultaneously. Because the wrapper runs the
  players SEQUENTIALLY (JSR p1; JSR p2), the merged write-log per frame =
  [p1's chip-1 stream][p2's chip-2 stream] — so each sub-player is extracted
  + composed + verified with the EXISTING single-chip machinery, only
  chip-TAGGED.
- **Verify:** siddump logs every installed chip, merged into one
  cycle-ordered stream with reg encoded `chip*$20 + reg`; single-chip output
  is byte-identical, so all flat `(reg,val)` comparators work unchanged.
- **USF:** voices number THROUGH the chips (1-3 = chip 1, 4-6 = chip 2, ...);
  chip count derives from the voice-block count; per-chip tempo/global/init
  ride optional `tempo N`/`global N`/`sid N` forms; the extra chips' SID
  MODELS ride `psid.sid2/sid3` (only when the header states one). Chip I/O
  ADDRESSES are NOT in USF — they are pipeline constants (chip 2 = $D420,
  chip 3 = $D440), the I/O-space analogue of "the composer always emits the
  player at $1000" (they'd be opaque hardware tokens hurting ML). Merge
  gives each chip's instruments + filter window a fixed-stride disjoint id
  block so the composer's split inverts it exactly (each chip's sub-USF ==
  its standalone extraction).
- **Compose:** one clean player instance per chip (own origin; chip k>0
  writes $D400+k*$20 via a register-operand relocation) + a dispatcher whose
  init/play call each in turn. Per-instance write-stream QUIRKS are config,
  not mechanism (Nice_Dream: the res/route $D417 write is left on chip 1 for
  BOTH players — an editor relocation quirk, reproduced by keeping $D417
  un-relocated).
- **Status:** logged (1×, DMC family-1 Nice_Dream_2SID: unsupported ->
  partial). Infrastructure is engine-neutral (314 2SID + 27 3SID members
  corpus-wide). NB the round-48 "residual = filter-def-walk res-timing at
  write 3221" was a MISDIAGNOSIS — it is a cross-chip ordering artifact of
  comparing the merged stream flat; see **C28** for the correct verdict
  (compare per chip). After C28 the true blocker is a single-chip
  note-duration drift at ~74s, not multi-SID.

### C28 — Multi-SID verdict: compare each chip's stream INDEPENDENTLY

- **Problem shape:** a multi-SID rebuild (C27) that is per-chip CORRECT still
  shows a `(reg,val)` divergence when the merged chip-tagged stream is
  prefix-compared flat. The first divergence is a CROSS-CHIP adjacency: orig
  has `[chip1 write][chip2 write]`, rebuild has `[chip2 write][chip1 write]`
  (or a chip-1 write lands on the other side of a chip-2 block).
- **Root cause:** two SID chips are INDEPENDENT hardware — each latches only
  its own register writes and evolves only from them. So the ORDER of a write
  to chip 1 vs a write to chip 2 within a frame is PHYSICALLY UNOBSERVABLE
  (the multi-SID analogue of within-frame cycle position, Trap B). The merged
  write-log is cycle-SORTED, and siddump's per-chip write cycles are not
  reliable to sub-write precision for cross-chip interleaving (chip-2 writes
  cluster at one cycle value), so a rebuild with a few-cycle timing delta
  places a cross-chip write on the other side of the boundary. Classic
  trigger: an editor quirk that routes chip 2's res write onto chip 1's
  $D417 (Nice_Dream), whose position vs chip 2's body then flips.
- **Fix (canonical):** split the merged stream by chip (`reg // 0x20`) and
  require EVERY chip's own substream to pass the single-chip verdict.
  Within-chip order and every value stay fully checked; only cross-chip
  interleaving is dropped, so nothing real is masked. `compare_instruction_
  stream(..., n_chips=N)` runs the compare per chip and aggregates (localise
  on the first failing chip; when all pass, report the worst tail + AND of
  audio_guaranteed so a caller's playback-safety gate sees the worst chip).
  `verify.verify_all` routes on `_n_chips` (PSID v3+ header +$7A/+$7B) via
  `_music_ok_multichip`; `dmc_family_batch` passes `n_chips=len(cfgs2)` and
  localises flat_div per chip. Single-chip (`n_chips=1`) is byte-identical.
- **Do NOT** try to fix this by making the capture straddle-free (a siddump
  per-irq global-abs rewrite was tried and REVERTED — it does not fix the
  cross-chip reorder and it perturbs the shared CIA verdict path). The order
  is unobservable; drop it from the verdict, don't chase cycle precision.
- **Trap:** a pc-trace per-CPU-invocation capture (program order,
  straddle-free) OR any short (2-6s) capture can show "byte-perfect" while a
  real blocker sits deeper — always verify at FULL songlength (× ~1.1)
  before declaring FULL.
- **Status:** logged (1×, DMC Nice_Dream_2SID: match 3221 -> 63496 writes;
  full regression green, single-chip byte-identical). Generalises to all
  314 2SID + 27 3SID corpus members (per-chip works for n_chips=3).

### C29 — Track LOOP into an OUT-OF-IMAGE sector → engine sonifies live ZEROPAGE as notes

- **Problem shape:** a voice's track (orderlist) hits its `$FF` loop marker,
  and the loop-target position holds a garbage sector number PAST the
  sector-pointer table, so `secp_lo[n]|secp_hi[n]<<8` resolves to `$0000` (or
  another address below the load addr). The file image is all-zero there, so the
  naive sector decode is "note-0 forever"; the ORIGINAL, at runtime, reads live
  LOW RAM as note data — for the `$0000` case that is the 6510 I/O port
  (`$00=$2F` DDR / `$01=$37` port, the PSID environment defaults) then static
  zeropage, read via `LDA ($F8),y` with the sector pointer `$F8/$F9=$0000`. The
  write stream plays notes `$2F`(=47), `$37`(=55), then the static zp bytes as
  notes/prefixes — a real, reproducible outro, NOT a bug to clamp (strict
  write-stream policy). Presents as a deep first-divergence: a voice plays two
  "impossible" high notes then a held low note, where the rebuild plays note-0.
- **Canonical fix (extract-side; C26 shape but from LIBSIDPLAYFP not py65):**
  read what the engine reads. Gated on `_loops_offimage` (a `$FF` loop reaching
  a sector `< load`), capture the runtime low RAM
  (`_postinit_values(path, range(0x100))` — py65 CANNOT reproduce the
  emulator ENVIRONMENT's zeropage, ledger C9) and OVERLAY it onto the
  file-image `mem` before `_walk_track`, with two read-time corrections:
  (a) 6510 port offsets `$00/$01 = $2F/$37` (memwatch reads the RAM UNDER the
  port, not the port register — hardcoded PSID reset value, pc-trace-confirmed
  `[0000]{2f}`/`[0001]{37}`); (b) sector pointer `$F8/$F9 = $00` (during the
  read they hold the `$0000` base). `_simulate_sector` then decodes the true
  endless outro; the off-table reach model picks up the new notes/instruments
  automatically (Killer_Beat's `$FF00` region = instr-7 note-28 off-table freq).
- **Regression-safe BY CONSTRUCTION:** the overlay only changes the DECODE of
  out-of-image sectors, and a sector's decode only affects the write-log if it
  is PLAYED. A played out-of-image sector was always mis-decoded (image zeros ≠
  runtime), so any member the change touches was already non-FULL; an unplayed
  sector's decode change is byte-identical. The overlay writes only `$00-$FF`,
  which nothing else in the extract reads → no FULL can regress (proven: full
  `tools/regression.py` green 0-regr all 7 families; a no-OOB FULL builds
  byte-identical MD5 old-vs-new).
- **Combines** C26 (out-of-image data → read runtime RAM) + C9 (py65 can't
  reproduce the environment → measure from libsidplayfp). Distinct from C26's
  init-UNPACKER (there the member's OWN init generates the tables and py65 runs
  it); here the sonified bytes are the EMULATOR ENVIRONMENT's zeropage + the
  6510 port, which only libsidplayfp holds.
- **Boundary / residue:** works when the sonified low RAM is STATIC during play
  (taint-confirm `$0000-$00FF`: for the DMC player only `$F8/$F9` are written,
  and those read `$00` from the voice's own `$0000` sector pointer). A member
  whose sonified zp region has a byte WRITTEN during play (dynamic) keeps that
  byte wrong (defaulted 0) = honest residue; the first divergence still moves
  deeper (Lens 3 win). Off-table dynamic residue + the 2SID multi-subtune
  limit (unrelated) account for the 29 members that stayed partial.
- **Status:** logged (1×, DMC family-1). Census: 44 f1 STORED-partials carry the
  signature; the batch flipped 14 to FULL, but re-baselining each against the
  PARENT commit (b81785e5, amend Step 3.4 / C20) shows **4 GENUINE partial → FULL**
  — Killer_Beat (121386/121386), Axel_Foley, Remix_1995, Centric_tune_4 — while
  the other 10 (9 Flash + Narwana) were ALREADY FULL under parent (stale
  palimpsest rows predating round 55; my overlay is neutral for them = their
  out-of-image sector is UNPLAYED in the verify window → byte-identical). 29 stay
  partial, 1 pre-existing 2SID-multisubtune error (exonerated vs a parent build).
  0 regressions (full tools/regression.py green). LESSON (re-confirms C20): the
  stored jsonl before-status is NOT a trustworthy baseline — re-verify each
  apparent flip against a fresh PARENT-code build before counting it.

### C30 — Lossy enum over independently-toggleable editor flag bits (dead bit observable via state-as-data read)
- **First sight (2026-07-08, DMC v4, Phobos/Strain_2 → FULL):** USF
  `EnvelopeConfig.gate_mode` modeled DMC instrument byte 10's two gate bits
  ($10 HOLDING FX, $08 NO GATE FX — the TND tutorial documents them as
  independent editor toggles) as a 3-value enum, assuming mutual exclusivity.
  The corpus falsifies it: instruments carry BOTH bits ($18). The engine tests
  $10 first ($132D) so $08 is mechanically dead when $10 is set — audibly
  $18 ≡ $10 — but the RAW flags byte is cached in $177D,x and READ AS DATA by
  the off-table freq-hi lookup (C6 idx 216 → $177F), so the composer's
  reconstructed byte (`iflags()`, missing the dead bit) diverges the stream.
- **Canonical form:** keep the enum = the EFFECTIVE articulation (engine
  priority applied), and carry the masked co-set flag as an **elidable boolean
  co-field** (`gate_open: bool = False`, emitted only when true). Extract sets
  it from `(fx & 0x18) == 0x18`; reconstruction ORs it back in. Do NOT mint a
  4th enum value ('open_hold') — a categorical token duplicating 'hold' hides
  the similarity the boolean makes explicit; do NOT store the raw byte (Pole B).
- **Regression-safety argument (by construction):** the composed engine mirrors
  the orig's bit priority, so the added bit changes the write stream ONLY at
  state-as-data reads of the flags byte — exactly where the orig already
  diverged from the old rebuild. A FULL whose stream contained such a read
  would have mismatched → no FULL can regress. Default False → writer elides →
  all existing USFs byte-identical.
- **The general smell:** any USF enum derived from a FLAGS byte where the
  source bits are independent editor toggles. Round-trip-verify the
  reconstruction against the raw byte per instrument (the round-39 lesson);
  a failure means the enum is lossy, not that the data is dirty.
- **Status:** `logged` (1×).

### C31 — Compilation: one file packs N INDEPENDENT players, a per-subtune dispatch wrapper selects (player, song)
- **First sight (2026-07-10, DMC v4 family-1, Abyssal_Karma-Part_One, Richard
  Bayliss):** the PSID header overstates songs (5), but the file is a
  COMPILATION of TWO independent, fully-relocated copies of the SAME DMC v4
  engine, each with its own data pool (instruments / freq-wave-filter tables /
  sectors / tracks / tune records). A small SMC dispatch wrapper at the PSID
  init/play vectors maps subtune → (player_base, song): `LDX subtune;
  LDA base_hi_tab,X → STA <both JMP hi-bytes>; LDA song_tab,X → A; JMP
  player`. Here subtune 0 → (player@$8000, song 0); subtunes 1-4 →
  (player@$9100, songs 0-3). Player A carries only 1 real song; player B carries
  4.
- **How it PRESENTS / why the extractor gets it wrong:** `_build_via_canon` base
  detection tries play-3 then LOAD; both players have a valid canonical DMC
  jump table (`4C b+1D 4C b+85`), and the running player is neither play-3 (=the
  wrapper) nor uniquely load — the LOAD-address player (A) wins, and all 5
  subtunes are decoded from A's tune table. sub0 is FULL (it genuinely IS
  player A song 0); subtunes 1-4 read PAST player A's 1-record tune table into
  garbage bytes (tracks point at `$FE` stops or out-of-image $3Cxx) → they
  decode to silence / off-image residue and diverge at frame 1. The downstream
  masked-identity compare does NOT catch it — player A is a byte-valid player,
  just the wrong one for those subtunes.
- **Detection signature:** the file image contains ≥2 canonical DMC jump tables
  at different bases (`4C b+1D 4C b+85`). Bayliss folder alone: 15 such members
  (Balloonacy = 4 players, Lane_Crazy = 4, Defuzion_3 = 3, …); the pattern
  spans the DMC corpus. The dispatch wrapper is the confirmer (per-subtune SMC
  patch of a JMP hi-byte + song# from `LDA tab,X`).
- **Analogues (same class, other engines):** FC Adrenalin ([[project_adrenalin]]
  — "a COMPILATION, 3 engines + 4 independent data pools") and the 5-Title-Tunes
  unified engine ([[project_five_title_tunes]] — multiple independent songs
  merged into one engine via globally-renumbered instruments + per-subtune
  params). DISTINCT from C27/C28 multi-SID: those are N players running in
  PARALLEL on N chips every frame (merged chip-tagged stream); a compilation
  runs exactly ONE player per subtune, SEQUENTIALLY selected — the per-subtune
  streams are fully independent.
- **Canonical solution — UNIFIED-MERGE (built 2026-07-10, `pipelines/dmc/v4/
  compilation.py`):** the 5TT playbook, extract-side only, NO USF/composer
  change. `detect_compilation` (>=2 canonical JT bases + static wrapper decode
  of the base-hi + song X-indexed tables) -> per-subtune (player, song) map;
  `factory.dmc_v4_config(base_override=B)` extracts each player as a standalone
  canonical DMC (canon path for a UNIFORM relocation; on its code-identity
  mismatch, the signature-based `_build_via_dataflow(base_override)` handles the
  NON-uniformly-relocated players — the packer moves state scratch, e.g. the
  $100C active-flag array, independently of the code); `merge_models` merges
  into one DmcModel — shared freq/vibdepth (verified identical), instruments
  renumbered+deduped into one compact <=28 pool, songs reordered by PSID
  subtune, rows' instr rewritten. Then the ordinary `model_to_usf` -> composer
  (compilation-unaware). Two knobs made it work: (i) mask the all-off/sfx
  jump-table entries ($1006-$100B) in the canon compare for base_override
  players — packers point them at a SHARED all-off routine, write-stream-
  irrelevant; (ii) FILTER-DEF window: strategy-1 SHARE the start player's
  17-record window when non-start players' played defs coincide (Abyssal_Karma);
  strategy-2 COMPACT-remap+dedup on conflict, gated on no played def OVERRUNNING
  (C2 repeat<=5, so adjacency is irrelevant) and <=16 distinct (Chwat,
  Para_Lander). Per-subtune master_vol rides `DmcSong.master_vol` already;
  per-player idle priming is global-only but verified UNREAD for the cluster
  (build B with A's priming still FULL) — a per-subtune-priming member would
  show as a partial, not a wrong build.
- **Regression safety (proven):** the >=2-DISTINCT-player-dispatch signature
  never coincides with a FULL single-player member — census of all 5401
  family-1 members found 17 compilations, ALL previously partial/error/
  unsupported, NONE full. Both `dmc_build_one` and the family batch fall back to
  the single-player path on any merge/compose failure, so an unmergeable
  compilation keeps its prior status.
- **Landed (verified FULL):** Abyssal_Karma (2p, 5 subtunes), Sharkz (2p, 6),
  Para_Lander/Race_n_Smash/Chwat/Poing_Ultra (compact-remap), **Balloonacy
  (4p, 7 subtunes — 2026-07-10)**. RESIDUE (fall back, 0 regr): 3 filter
  OVERRUN (repeat>5 — Zap_Zone/Protox-1/Mission_Moon, need an overrun-adjacency-
  preserving window); 1 instrument overflow (Heavy_Metal, 30 > 28); the
  remaining per-player `locate` residue (Lane_Crazy/Wiz_Max/Goldrake_plus_2/
  Mystery/Rogue_Ninja) is now unblocked by the region-bounded locate below but
  unverified this round (deferred to the next batch). DUAL-PLAYER emit (composer
  multi-player) is the alternative for the unmergeable tail.
- **PER-PLAYER `locate` — REGION-BOUNDED (2026-07-10, Balloonacy, +1 FULL):** a
  co-packed player can be uniformly relocated for CODE + DATA TABLES yet carry
  DEAD-CODE JMPs into a SIBLING player's canonical code (an un-relocated
  `JMP $1591` when the live path uses its own `$3591`; ground truth `--pc-trace`
  = the player runs entirely in its own `$Xxxx` page, the `$1xxx` jumps never
  execute). The static `_instrs` trace follows them, so every opcode-window
  signature matches TWICE (once per player) → every site ambiguous → `locate`
  returns None → whole compilation falls to single-player. FIX:
  `dataflow.locate(region=(base, base+0x900))` bounds the located instructions
  to the forced player's own code window; the sibling's block sorts outside the
  range (the player's own block stays contiguous, signature windows intact) so
  sites are unique again. `base_override`-only — the general single-player path
  passes `region=None` (a re-assembled player may spread code past a fixed
  window). Regression-safe: can only turn ambiguous-None into a unique match.
- **INSTRUMENT-POOL fit via OFFTABLE-UNION dedup (2026-07-10, Balloonacy; C8
  sibling):** after the locate fix the 4-player merge overflowed the 28-inst
  5-bit id cap (29 > 28). The tightest pair differed ONLY in `offtable_freq` —
  a C6 reachability artifact (which wave-offset/note the instrument was played
  at), NOT intrinsic content. `merge_models` now keys the dedup on everything
  EXCEPT `offtable_freq` and carries the UNION of records per merged id
  (Principle Rule 1 — cluster by behavior; each record fires only for its own
  (off,note), inert for a song that never plays it). A record COLLISION (same
  (off,note) → different (lo,hi) across the two players' freq tables) refuses
  the union → distinct ids. 29 → 28. Regression-safe: only `merge_models`;
  every currently-FULL compilation keeps its identical instrument count
  (offtable-union changes nothing when no two insts share a base key).
- **HETEROGENEOUS compilation — DMC players + a distinct dmc_sfx sub-player
  (2026-07-10, Canyon_Tank_Duel, Bayliss; +1 FULL, 13/13 subtunes):** the packed
  players need NOT all be the same engine. Canyon packs 2 canonical DMC music
  players ($1000/$2000) + a tiny (~257 B) CUSTOM SFX sequencer at $3000 — its
  own note/instrument/waveform format, NOT DMC (also in Widding's
  Empire_Strikes_Back @ $3D00; two authors → a shared DMC-editor SFX sub-player,
  named `dmc_sfx`). Three pieces, all landed:
  1. **Detection from the WRAPPER TABLE, not a JT scan.** `_canon_jt_bases`
     required the canonical `4C b+1D 4C b+85` head and MISSED the re-assembled
     dmc_sfx player (jump table at +$1B2/+$F0). FIX: `detect_compilation` now
     derives the player bases from the dispatch wrapper's own base-hi `LDA
     abs,X` table (the authoritative list of what it selects), each validated by
     the RELOCATION-invariant three-JMP head (`_is_player_base`: JMP at
     +0/+3/+6). Regression-safe: keeps the >=2-DISTINCT-player gate + the
     merge-fallback; only WIDENS which bases are recognized. (Also newly detects
     Empire as a 4-player heterogeneous compilation.)
  2. **dmc_sfx migrated as a typed USF engine** (NOT opaque bytes / a §8 engine
     library). New `dmc_sfx {}` block + `dmcsfx`-kind subtunes carry the shared
     musical content: a rotating filter-cutoff LFO, an arp pitch-program table,
     tuning tables (extended over the off-table reads), 8 instruments (each a
     4-phase ctrl/freqbase timbre+pitch modulation + envelope/PW), 8 song
     records, and the shared initial voice state (a song sets up only ITS voice;
     the others play from file-image leftover = a typed `voice_init`). One quirk:
     a glide can push the freq index past the 96-entry table → an off-table read;
     mostly static code bytes captured as extended tuning (C6), the ONE live one
     ($30F1 = the play counter) reproduced by a composer redirect at
     `live_counter_fidx` (C11 state-as-data). Extract `sfx_engine.py`
     (+ a pure-Python reference interpreter reading ONLY the typed model — proves
     completeness); composer `sfx_composer.py` (a clean 6502 re-implementation).
  3. **Heterogeneous composer dispatch** (`build_dmc_compilation_sid`): emit BOTH
     the DMC engine and the dmc_sfx interpreter into one image behind a
     per-subtune stub at $1000 — init(A=subtune) latches the owning engine +
     routes with the engine-local index, play jumps to the latched engine. Same
     "one engine per subtune, sequential" shape as the 2SID dispatcher, but
     per-subtune-selected (only one runs) rather than parallel.
  Regression-safe by construction: the whole path is gated on `usf.dmc_sfx`
  presence (single-player + homogeneous-compilation members never touch it) and
  on the SFX-player detection (an existing wide-family invariant: the
  >=2-distinct-player-dispatch signature never coincides with a FULL single
  player); write_dmc_compilation_usf falls back to single-player on any failure.
- **Status:** `logged` (built, 7 members FULL incl. the first HETEROGENEOUS
  (Canyon, 13/13); family-wide residue tail documented — see
  [[project_dmc_compilations]]).
