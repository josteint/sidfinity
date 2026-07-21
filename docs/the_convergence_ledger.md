# The Convergence Ledger

## Why this exists

When we migrate a new engine we keep hitting sub-problems we've solved before
(a value swept over time; a byte-indexed program table; a runtime divergence to
localize). Without a record we re-invent a variant each time, and the eventual
grand unification (docs/the_move-1_plan.md — Move 1) becomes a giant
retroactive untangling of N slightly-different solutions.

This ledger **pre-decides** convergence incrementally: each recurring
problem-class gets ONE entry naming the canonical (idiomatic-for-us) solution,
where the shared code lives (or that it's a factor-candidate), and the boundary
conditions. It is a **record, not a refactor** — recording "this should be one
implementation" is cheap and happens now; *making* it one implementation across
engine families is Move 1, deferred. The ledger is what makes Move 1 smooth:
the decisions are already made.

## Two layers (structure since 2026-07-18)

- **THIS FILE = the recognition layer**, imported into every session: the
  Index plus one RECOGNITION CARD per entry (problem signature, how it
  PRESENTS mid-investigation, one-line canonical answer, status).
- **`docs/ledger/C<n>.md` = the full entries**: canonical solution detail,
  boundaries, refinements, warnings about fixes that failed, worked examples,
  consumers. **A card is never enough to ACT on — read the full entry before
  applying a solution.** Recognize here; apply from the entry file.

(The split replaced the former full-import, per the ledger's own "if the Index
outgrows a quick scan" clause; validated 2026-07-18 by a recognition benchmark
— digest-only matched full-import 24/24 + 16/16 on oblique cases, and the one
error in the whole experiment was a full-import agent mis-attributing a lesson
buried deep in a monster entry. Benchmark method: tmp/ledger_bench/, ephemeral.)

It does NOT replace existing convergence machinery — it routes to it:
- **Representation** convergence is enforced by the **USF schema**
  (`src/usf/types.py`): one dataclass per musical DOF.
- **Decision rules** live in `docs/the_principle.md`.
- **Process/methodology lessons** live in `.claude/memory/` (`feedback_*`).
This ledger's unique value is the **technique/algorithm catalog** — the
*how-we-solve* knowledge that none of those stores holds.

## How to use it

Three separate timings — do NOT conflate them (the record happens first so the
recurrence is later found by lookup, not by memory):

- **CONSULT — before choosing how to solve any non-trivial problem.** Scan the
  Index + cards below by problem-class; on a match, READ the full entry
  (`docs/ledger/C<n>.md`) and use its solution (call the shared code, or
  implement the recorded form) instead of inventing a variant.
- **RECORD — log EVERY solution to a non-trivial problem, on first sight**
  (status `logged`), even if it has occurred only once: create
  `docs/ledger/C<n>.md`, add an Index row + a recognition card here. Don't wait
  for a repeat. **Placement rule:** the entry carries the *transferable*
  knowledge — problem-class, canonical solution, boundaries, TELLs, failed
  alternatives. Per-occurrence *status* (member names, round numbers, counts,
  commit hashes) lives in the engine's memory (`project_<engine>`) and the
  entry LINKS there. One home per fact. (Entries written before 2026-07-14
  predate this rule and are grandfathered — do not retroactively distill them.)
- **CANONICALIZE / FACTOR — on the 2nd occurrence.** When a problem-class
  recurs (the `/uready-review` cross-engine pass flags **≥2×**, or you notice
  it directly), pick the one canonical form (status `recurring`) and either
  point at shared code (`shared`) or mark it a Move-1 `factor-candidate`. The
  ≥2× threshold governs ONLY this step — never whether something is recorded.

`/uready-review` is the periodic maintainer (cross-checks + promotes + keeps
cards in sync with their entries); per-solve recording is the everyday reflex.

When a fix for a member's first divergence **regresses other members**, run the
`/amend` skill — it operationalises this ledger + the CORE TENET + the
principle + the trichotomy for exactly that situation.

Entry schema: **Problem class** | **Canonical solution** | **Status** |
**Boundary / when it applies** | **Consumers (seen)**.

**Status:** `logged` (seen 1×, provisional form) · `recurring` (≥2×, canonical
form chosen) · `factor-candidate` (recurring, awaiting Move-1 code-factoring) ·
`shared` (one implementation exists; consumers call it) · `methodology` (a
practice, not code to factor).

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
| INAUDIBLE writes · idle/gate-off voice freewheels · "audio-equivalence" verdict relaxation | C15 | ⛔ REMOVED (user decision 2026-07-01): every SID gets STRICT write-stream match, always — never propose relaxing the verdict during per-engine work. If an idle-freewheel divergence blocks a member, REPRODUCE the writes (core tenet permits reproducing the mechanism). Design parked in `the_move-1_plan.md` as a Move-1-era-ONLY consideration. |
| per-frame WRITE-ORDER differs · orig batches note-on writes (SR/AD/CTRL) separately from wave-step writes (freq/PW/CTRL) or uses a different voice interleave · rebuild emits a different order · NOT a wholesale composer rewrite — PARAMETRIZE the composer's EMISSION order (precedent: FC `nextvoice_write_order`) | C16 | logged |
| HETEROGENEOUS per-step write shapes in a trace-lift · one superset order can't embed all steps (conflicting reg orders / intra-step dups / sections) · cluster steps by EXACT write shape → K positional templates + per-step template id | C17 | logged |
| play-vector WRAPPER with per-call PHASE behaviour · slow-tempo / multispeed-effects cycler · every Nth call runs the full play, others run effects-only / register-refresh / nothing · wrapper shapes vary (SMC, DEC+dual-JMP, parity AND) — OBSERVE entry-point reachability under py65, don't parse · arm F-ENTRY variant: wavestep ($1591) vs vibrato half-cycle ($1567, flips reshape vibrato to a square) → `effect_entry_variant: vibflip` | C18 | logged |
| TRICHOTOMY VERDICT alignment · rebuild emits its OWN init (universal reset+priming) so streams differ by an init prefix · Check A end-of-init state + aligned play-stream compare · TWO implementations exist: `verify_cycle._trichotomy_compare` (FC, shift recovery) + `usf_roundtrip._compare_music/_split_aligned` (basic_program, known-init-length + probe search) — CONSULT MISS, factor at Move 1 | C21 | factor-candidate (2×) |
| hand-patched player WEDGE inside the canon body · SMC opcode toggle · 1-byte opcode patch · JMP over canonical loads · runtime state ≠ static file byte · PWM bound-shift (LSR count) wedge · init-PREFIX `LDA #imm` hard-forces the played tune record (extract walks the wrong record) · STATIC opcode probe, never a bounded stream scan · census carriers both sides · reproduce semantics behind a factory-probed param (EXTRACT-only when the wedge changes a derived musical value; COMPOSER param when it changes a write-stream TIMING/VALUE, e.g. $D418 re-asserted every frame · SWITCH gate-toggle EOR immediate · multi-SID relocation MISS) | C19 | canonicalized (12×) |
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
| COMPILATION · one file packs N INDEPENDENT players + a per-subtune SMC dispatch wrapper (subtune→(base,song)) · header overstates songs, sub0 FULL others silent/garbage · ≥2 jump-table bases · unified-merge (renumber+dedup instruments) · heterogeneous engines (dmc_sfx) · distinct from C27 parallel chips | C31 | logged |
| engine STICKY STATE materialized into effective variants · orderlist state over the loop wrap (fitted pad/period/rcmd) · pattern-row sticky duration/instr/vol (FC (fc_id,init_len) variants · len=L pickup · DMC ~intro decode variants) · fold to STATED notation (value present iff the stream states the command; absent = inherit) + ONE shared resolution interpreter (src/usf/resolve.py) · re-derivation assert, fallback wholesale | C32 | canonicalized (2×) |
| close a `Params.fields` ESCAPE-HATCH key → typed field · untyped behavior-named scalar in the generic params bag (init-phase state / mechanism scalar), borderline §7 · NOT opaque-bytes (C7) / NOT a wedge knob (C19) · it's a byte-identity CARRIER REFACTOR not a schema addition (value already in USF) · census ALL consumers (often cross-engine SHARED + dead readers) · clone an existing typed field of the same trichotomy category · type by MUSICAL category NOT a composer grouping · gate regenerates + MD5-compares every consumer family (surfaces broken extract paths behind a FULL verdict) | C33 | methodology |

---

## Recognition cards

### C1 — a control value swept over time (PW, cutoff, any contour)
- PRESENTS: an engine ramps a value up/down over frames — pulse width rising N
  frames then falling N frames, a filter cutoff walking a contour, any
  piecewise-constant-rate sweep, possibly looping.
- CANONICAL: `SweepEnvelope(start, phases=[(rate, frames)], loop)`; capture
  with `_capture_env`, rebuild with `add_env`. A bounded bidirectional
  oscillator is the special case `start + [(+s,n),(−s,n)], loop=0`. Divergent
  per-family forms exist (Hubbard pwm / FC programs / DMC v4 pwm vs v5 env) —
  Move-1 decisions D1/D2.
- FULL ENTRY: [`ledger/C1.md`](ledger/C1.md) — read it before applying.

### C2 — byte-indexed program table; the program RUNS OFF the table
- PRESENTS: a program/step index is a BYTE and the program is longer than its
  array — the pointer walks past the nominal end into overlapping/adjacent
  arrays or the next record's fields, and the ORIG plays those bytes as real
  program steps (e.g. a repeat byte > array size producing a rise-then-stop
  sweep; a wave program walking into the next table). The rebuild, bounding
  the table by its nominal length, diverges.
- CANONICAL: never bound capture by the array's nominal length — bound by
  `min(256, 0x10000-addr)` and let the per-program walker bound reachability;
  when the walk is unbounded, EMIT THE ORIG'S RECORD LAYOUT (or simulate the
  walk and emit the resolved sequence) so every walked read is byte-exact.
  For a one-shot off-table ramp (no loop): taint-classify the source FIRST
  (static ⇒ representable / written ⇒ residue), reach = the re-init interval,
  on phase-cap TRUNCATE the prefix, and pool large captures (C8).
- FULL ENTRY: [`ledger/C2.md`](ledger/C2.md) — read it before applying.

### C3 — "no program" detection at table position 0
- PRESENTS: instruments hold a constant value where the orig ramps — because a
  leading `(0,0)` entry was treated as "no program". A leading (0,0) is a
  VALID zero-rate phase (its count sits in the next slot).
- CANONICAL: detect genuine absence as a single zero-rate TERMINAL hold
  (count ≥ $9000); never gate on `entry0 != (0,0)`.
- FULL ENTRY: [`ledger/C3.md`](ledger/C3.md) — read it before applying.

### C4 — localizing a runtime divergence whose cause is engine-internal
- PRESENTS: `find_first_divergence` names the register but not the cause.
- CANONICAL: `assemble(asm, return_labels=True)` for OUR label addresses +
  `siddump --memwatch-on-write <reg> <addrs>` to snapshot state per write;
  compare event-by-event vs the orig's disasm addresses. Diagnostic: full
  note-state identical + only the output register differs ⇒ the bug is in the
  program that register runs, not the note/trigger logic.
- FULL ENTRY: [`ledger/C4.md`](ledger/C4.md) — read it before applying.

### C5 — detection ≠ FULL (residue triage)
- PRESENTS: loosening a factory detection gate to "accept" members; they then
  fail at the NEXT stage (cia / partial / error) — acceptance ≠ FULL.
- CANONICAL: the verify PARTIALS, not the detect-rejects, are the FULL
  bottleneck. Census residue (`tools/divergence_census.py`) before attacking.
- FULL ENTRY: [`ledger/C5.md`](ledger/C5.md) — read it before applying.

### C6 — off-table FREQ-table lookup (index past the freq table)
- PRESENTS: a melodic/effect path computes `(offset + note) & $FF` past the
  freq table (arp offset + note ≥ table size; note+transpose wrap; bare-note
  idx ≥ 96) and the ORIG reads image bytes beyond the table, PLAYING them as
  real frequencies — the audible pitch corresponds to those bytes. GOTCHA:
  the read is BOTH freqlo[idx] and freqhi[idx] at different depths.
- CANONICAL: deconstruct each off-table read to a musical frequency attributed
  to (instrument, offset, note): per-instrument `offtable_freq` records with
  `at(...)`/`live(...)` read flags; the composer rebuilds its window from the
  records. ❌ never a contiguous `freq_overrun` window. Reach model must
  include deferred note-init / soft-note TRANSITION reads and per-subtune
  post-init state; non-canon state geometry must be probed before any live
  serving. Full entry has the hard-boundary list (dynamic work-RAM residue).
- FULL ENTRY: [`ledger/C6.md`](ledger/C6.md) — read it before applying.

### C7 — ANTI-PATTERN: orig bytes carrying musical intent that bypass / opaquely sit in the USF
- PRESENTS: extract/composer wants to carry raw orig bytes (a window, a blob,
  a `bytes` field) because "the engine just reads them".
- CANONICAL: three severities — A leapfrog (orig→output bypassing USF: never),
  B opaque blob in USF (decide deliberately: (a) deconstruct to musical form,
  (b) document+minimize, (c) exclude), C justified (bytes ARE the natural
  musical form: tuning tables, digi PCM). Consult the full entry before adding
  ANY content-by-reference / bytes-typed USF field.
- FULL ENTRY: [`ledger/C7.md`](ledger/C7.md) — read it before applying.

### C8 — de-fused per-entity program pool overflows the engine's byte index
- PRESENTS: composer emits a separate program copy per instrument; a member
  with many same-shape instruments inflates the pool past 255 → hard build
  error ("pool overflow", "table_overflow").
- CANONICAL: dedup identical programs (key: exact emitted bytes + loop);
  OVERFLOW-GATE the dedup when loop markers encode absolute targets (dedup
  only when un-shared > 256 — zero-regression by construction). Dedup keys
  must EXCLUDE reachability artifacts (e.g. offtable_freq) — carry the union.
  A composer-side 8-bit stream cursor that overflows is the sibling: widen to
  16-bit, don't dedup. Suffix/overlap packing is REFUTED (see full entry).
- FULL ENTRY: [`ledger/C8.md`](ledger/C8.md) — read it before applying.

### C9 — a runtime parameter py65 can't read → measure it from the writelog
- PRESENTS: a build parameter is set by code py65 can't execute (init hangs
  waiting for an IRQ, value programmed inside the IRQ handler, unsupported
  opcode) — static/interpreter extraction impossible.
- CANONICAL: don't reject the member — MEASURE the parameter from the
  libsidplayfp ground-truth writelog (CIA rate: count play() entries/frame
  via `--writelog-per-irq --per-irq-debug`, round to the integer factor).
  TELL for the single-speed default latch: a PSID speed-bit tune whose init
  programs no timer runs at the environment default $4025 (~60 Hz) — built
  as vblank it under-runs ~20% with a perfect prefix. TELL for a WHOLLY
  UNMEASURED rate (a second build path that defaulted `cia_period=0`): an
  exact prefix at a clean 1/N of the orig's length, no content divergence —
  right notes, wrong speed (distinct from C25's ~0.5% drift). A C18 phase
  schedule DIVIDES the rate, so period and multispeed factor read together.
  When a param is measured in one build path, grep the OTHER constructors.
- FULL ENTRY: [`ledger/C9.md`](ledger/C9.md) — read it before applying.

### C10 — chip-global ($D415-$D418) automation that varies during the song
- PRESENTS: master volume / filter cutoff / res / routing changes across the
  song (not per-voice, not per-instrument).
- CANONICAL: choose by MUSICAL STRUCTURE — PARAMETRIC (MasterVolConfig fade
  formula, filter programs, master_vol_every_* reassertion, init.sid priming)
  when a mechanism drives it; EXPLICIT `global_track` event list ONLY for
  arbitrary authored data with no recoverable mechanism (hand-POKEd values).
  ANTI-PATTERN: converting a parametric form to an event list.
- FULL ENTRY: [`ledger/C10.md`](ledger/C10.md) — read it before applying.

### C11 — engine indexes via an 8-BIT register: the offset WRAPS mod 256 (+ the off-table live-redirect cluster)
- PRESENTS (wrap): extraction computes `mem[base + entry#*stride]` full-width
  and reads "garbage"/out-of-image for high entries — but the orig plays fine,
  because its index register is 8-bit and WRAPS: `(entry#*stride) & $FF`.
  TELL: when a trace shows an out-of-range/garbage read, SUSPECT THE
  EXTRACTOR (wrap / wrong base / wrong stride) FIRST, not the data. An
  add-chain with intermediate carries is NOT `& $FF` — emulate the exact
  instruction sequence. Negative transposes wrap low notes HIGH.
- PRESENTS (live-redirect): an off-table read sonifies ENGINE STATE — the
  first-divergence value equals a live counter / position / scratch var, not
  a static byte. TELLs: a cluster whose (orig,mine) values are EOR-$0F
  complements = redirect row naming the complement var; "voice drops one
  update at a pattern boundary" = init-cleared seed; per-(inst,off,note)-
  stable dynamic byte = event-driven capture. Diagnostic (a/b/c): wnote
  matches + var matches ⇒ add a redirect row; wnote differs ⇒ wavepos layout;
  var differs ⇒ non-tracking accumulator (hard). ALL read sites must honor a
  redirect, sparse vars need seeding, shared scratch is shadowable by
  mirroring all writers. Full entry has the hard boundaries (dynamic work-RAM,
  off-table glide targets — do NOT re-attempt the glide-target fixes).
- FULL ENTRY: [`ledger/C11.md`](ledger/C11.md) — read it before applying.

### C12 — accumulated per-step rounding drift in a delta-encoded round-trip
- PRESENTS: LONG tunes fail as an exact prefix SHORT by an amount that scales
  with song length; short tunes pass. The USF stores DELTAS (durations/gaps)
  and a floor/min/round is applied per step (e.g. `max(1, gap)`), so error
  accumulates as the player re-sums absolute positions.
- CANONICAL: keep deltas EXACT (allow 0) on writer AND reader. A genuine 0
  gap makes same-frame write order matter — ship exactness as a
  length_fail-only verify-fallback when spurious collapses are possible.
- FULL ENTRY: [`ledger/C12.md`](ledger/C12.md) — read it before applying.

### C13 — engine-variant dispatch: shifted init, canonical play body
- PRESENTS: a cluster of build-fails (`no_jumptable` / code-mismatch) whose
  jump table has the CANONICAL play target but an init target a few bytes
  off; the play body decodes cleanly — only the init region differs.
- CANONICAL: dispatch on the PLAY-body signature, never the init offset (we
  emit our own init; a loosened dispatch can't false-FULL — build+verify
  judges). Corollaries: variant-knob probes must be layout-independent;
  a binary "not-A ⟹ B" classifier hides a THIRD form — fix by POSITIVE
  detection of the minority (verified absent from the majority), never by
  flipping the default; probe literals are per-voice DATA (don't assume
  equal immediates).
- FULL ENTRY: [`ledger/C13.md`](ledger/C13.md) — read it before applying.

### C14 — command-per-row tracker effects (note + fx + param per row)
- PRESENTS: a tracker family attaches an EFFECT COMMAND + PARAM to each
  pattern ROW (porta up/down, toneporta, vibrato, arp, set-filter, set-SR,
  set-tempo) — not per-instrument configs; NoteRow has no effect field.
- CANONICAL: encode each command as a `NoteRow.fx_flags` STRING with its
  parameter (`glide=`, `arp=X,Y`, `portaup=N`, `vibrato=X,Y`, `tempo=N`...).
  Musical + parametric; no schema change. Glide runs can lift to head-row
  flags with regenerated intermediates (rest-row scheme).
- FULL ENTRY: [`ledger/C14.md`](ledger/C14.md) — read it before applying.

### C15 — ⛔ REMOVED (audio-equivalence verdict)
- Every SID gets the STRICT write-stream match, always. Never propose
  relaxing the verdict during per-engine work; REPRODUCE inaudible writes
  (idle_wave precedents). Design parked in the Move-1 plan.
- FULL ENTRY: [`ledger/C15.md`](ledger/C15.md) — read it before applying.

### C16 — per-frame SID write-ORDER differs across engines
- PRESENTS: the writelog matches through the leadin then forks where the orig
  writes one voice's note-on register but the rebuild writes another voice's
  freq — the VALUES are all present nearby, only the interleave differs
  (within-voice register order, or a batched note-on pass vs per-voice
  interleave). Sweeping timing/leadin does NOT move the fork.
- CANONICAL: PARAMETRIZE the composer's EMISSION order (precedent:
  `nextvoice_write_order`) — never rewrite the player, never pre-scope "a big
  restructuring": trace the literal register-write sequence for 2-3 frames
  first; it is almost always a bounded emission-order knob.
- FULL ENTRY: [`ledger/C16.md`](ledger/C16.md) — read it before applying.

### C17 — heterogeneous per-step write shapes in a trace-lift
- PRESENTS: a trace-lifted write model assumes ONE step template but the tune
  has K distinct step shapes (alternating textures, per-section orders,
  intra-step duplicate registers) — no single superset order exists.
- CANONICAL: cluster steps by EXACT (attack, release) register-sequence shape
  → K positional templates + per-step template id; K=1 is the special case.
  Prefer deriving WHAT a step writes from row-level event types + a few named
  order knobs (normal form) — full templates in USF is Pole B.
- FULL ENTRY: [`ledger/C17.md`](ledger/C17.md) — read it before applying.

### C18 — play-vector WRAPPER with per-call PHASE behaviour
- PRESENTS: the PSID play vector points at a wrapper that behaves DIFFERENTLY
  on successive calls — every Nth call runs the full play body, others run
  effects-only / register-refresh / nothing (slow-tempo & multispeed-effects
  idioms; SMC JSR-operand tables, DEC+dual-JMP, parity AND shapes).
- CANONICAL: OBSERVE entry-point reachability under py65 / pc-trace — never
  parse the wrapper. Classify each call P / F<voices> / R<voices> / S; minimal
  repeating period = a schedule string (`P_F123`...); composer emits a
  phase-counter dispatcher JSR-ing its OWN entry points. Traps: a "silent"
  phase may hide a register refresh; F-vs-R needs the CHIP-STATE rule + frame-
  entry reachability (a held note's F looks like R); variant F/R entry points
  exist (vib_half, pulse_tail) — full entry lists them.
- FULL ENTRY: [`ledger/C18.md`](ledger/C18.md) — read it before applying.

### C19 — hand-patched player WEDGE inside the canon body
- PRESENTS: a member built from a known canon player diverges on ONE effect;
  dumping the orig's bytes at the canon site that produces the diverging
  write shows a changed opcode/operand (JMP over canonical loads, JSR
  re-pointed at a stub, an STA re-targeted at another instruction's operand =
  SMC toggle, a patched immediate). TELL: runtime state ≠ file-image byte
  while taint says the byte is STATIC ⇒ the READ SITE differs from canon —
  dump the canon-site bytes.
- CANONICAL: STATIC opcode probe (read the patched instruction itself; never
  a bounded stream scan) → factory `extra_params` → an existing/new composer
  param; CENSUS carriers on BOTH sides (partials = recovery, FULLs = exposure)
  before landing. Extract-only when the wedge changes a derived musical
  value; composer param when it changes write-stream timing/value. Probe must
  anchor on the REACHABLE site (a loose byte-pattern probe false-fires).
  ALSO COVERS a build-TOOL miss, not only a hand patch (the multi-SID
  relocation leaving one store operand un-offset). COROLLARY: **a default
  generalised from ONE observed carrier is an un-probed hardcode in
  disguise** — probe the operand, never enshrine the quirk (`keep_res=True`
  was wrong for 7 of 8 carriers). Watch GRANULARITY: the wedge can be
  per-STORE while the knob is per-register.
  12 occurrences — the full entry catalogues every known wedge.
- FULL ENTRY: [`ledger/C19.md`](ledger/C19.md) — read it before applying.

### C20 — stale-FULL palimpsest
- PRESENTS: a member recorded 'full' verifies partial under current code; OR
  a fix appears to regress N currently-FULL members. THE TRAP: the baseline
  is stale (old jsonl rows, stored .usf files, grep-derived FULL lists) or a
  parallel-batch flake — not your fix.
- CANONICAL: when a FULL fails re-verify, FIRST verify the STORED build vs
  orig (stored-matches + fresh-fails = current-code latent; stored-fails =
  stale row). Before believing ANY regression: fresh single-member
  current-code build. Never mass-write with code that didn't produce the
  verdict (code_hash gating). Coverage source of truth = a fresh batch.
- RELATIVE (C33): the EXTRACT-layer version — a member FULL in regression can
  hide a silently-broken REGENERATION path (regression builds from a STORED
  .usf, not from regeneration); a byte-gate that REGENERATES surfaces it.
- THIRD LAYER — the stored ARTIFACT is unreadable by the CURRENT grammar
  (schema drift). A typed-field move orphaned 1,182/11,943 stored .usf (9.9%)
  while regression stayed green — it builds from a ~116-member portfolio,
  never from the corpus. NO TELL; found by accident. Breaks `verify_usf` +
  every ML consumer. DETECTOR: `tools/usf_corpus_check.py` (~9 s) — run it
  after ANY grammar/parser/writer/types change. CURE: map failures to families
  FIRST, then per-family batch + mass-write (a wrongly-scoped mass-write can
  regenerate 5,221 members and fix zero). Non-FULL members are skipped by
  every mass-write, so their leftover .usf must be DELETED, not rebuilt.
- FULL ENTRY: [`ledger/C20.md`](ledger/C20.md) — read it before applying.

### C21 — trichotomy-verdict alignment (rebuild emits its own init)
- PRESENTS: an engine whose composer emits the universal reset + typed
  priming (its own init) — a flat prefix compare diverges at write 0 even
  though play streams match.
- CANONICAL: Check A (end-of-init chip state) + aligned play-stream compare.
  TWO implementations exist (`_trichotomy_compare` shift-recovery; basic
  known-length + probe) — consult before writing a third.
- FULL ENTRY: [`ledger/C21.md`](ledger/C21.md) — read it before applying.

### C22 — ambiguous round-trip flag encoding
- PRESENTS: a member verifies FULL for tens of thousands of writes then
  diverges DEEP at a "the rebuild missed a re-anchor" moment: the rebuild's
  value derives from PREVIOUS musical state (held base) while the orig's
  derives from the row's own data (new note's base, opposite slide
  direction). Two engine ops rendered to OVERLAPPING USF flag sets; the
  decoder branch tests a SUBSET of the discriminator. TELL: deep freq deltas
  QUANTIZED ×16 across a member class = speed-nibble arming drift.
- CANONICAL: make the decoder test the EXACT injective discriminator; emit
  the distinguishing flag ALWAYS (incl. zero values) and decode on flag
  PRESENCE, not truthiness. Check injectivity when adding any fx rendering.
- FULL ENTRY: [`ledger/C22.md`](ledger/C22.md) — read it before applying.

### C23 — a play-phase TOKEN hides a per-member behavioural ambiguity
- PRESENTS: the same schedule token (e.g. `P_F123`) maps to TWO behaviours
  across members (note-init on the F call vs a deferred arm: freq/ctrl
  without AD/SR, init on the next P). Fixing one class REGRESSES same-token
  FULLs — the regression is the SIGNAL the token is incomplete, not that the
  fix is wrong.
- CANONICAL: OBSERVE the distinguishing write-footprint per member (note-init
  always carries AD/SR ⇒ the "deferred" verdict has no false positive);
  cover ALL voices; escalate the observation window if inconclusive. Never
  derive from the token or a schedule heuristic.
- FULL ENTRY: [`ledger/C23.md`](ledger/C23.md) — read it before applying.

### C24 — play-body UNIT repeat / whole-play N-repeat
- PRESENTS (unit): one of the play body's 4 units (voice 0/1/2/filter-tail)
  runs N× per play() via a redirected JSR stub — a "double-speed voice", or
  doubled $D416/$D417 writes (JMP-tail re-enters the filter tail).
- PRESENTS (whole-play): a VBLANK member with a PERFECT play-stream prefix
  and a clean ~N× length tail — the whole play() runs N× per VBI. Count
  writes/frame, then disassemble the play VECTOR and FOLLOW its JMP
  indirection (`JSR T ×N :RTS` / `JSR T; JMP T`).
- CANONICAL: `play_unit_repeat=[v0,v1,v2,filter]` list / `play_repeat=N`
  param, detected by static byte-probe (C19 method). Distinct from C18
  (phase behaviour across CALLS).
- FULL ENTRY: [`ledger/C24.md`](ledger/C24.md) — read it before applying.

### C25 — the composer's play body must FIT the tightest CIA latch
- PRESENTS: a high-multispeed CIA member shows a PERFECT play-stream prefix,
  state match, and ONLY a small (~0.5%) length tail — no content divergence.
  Measured average play-entry period of the rebuild exceeds the latch (the
  orig's equals it): the rebuild's play body chronically overruns the cycle
  budget, delaying IRQs.
- CANONICAL: profile for common-path cycle CREEP (per-frame compare chains
  that grew); make the common case O(1) (leading bounds check). Content-
  identical by construction; pure timing. Ask what any per-voice per-frame
  addition costs × 3 voices × the tightest corpus latch.
- FULL ENTRY: [`ledger/C25.md`](ledger/C25.md) — read it before applying.

### C26 — song data ABSENT from the file image (init generates/unpacks in RAM)
- PRESENTS: the player is a known variant but its data-table operands are
  internally consistent AND point OUTSIDE the loaded image (or at zero
  fill); the file's data area is ~zeros; the tune plays fine. Init
  generates/unpacks the song data into RAM at runtime.
- CANONICAL: read what the ENGINE reads — run the member's own init under
  py65 and extract every table from POST-INIT RAM. Detection is
  all-or-nothing (EVERY operand outside the image ⇒ unpacker; mixed stays
  refused). Skip the packing-order layout check for this class.
- FULL ENTRY: [`ledger/C26.md`](ledger/C26.md) — read it before applying.

### C27 — multi-SID (2SID/3SID): N chips, one player per chip
- PRESENTS: the PSID v3/v4 header declares 2-3 SID chips; the play vector is
  a dispatch wrapper calling N complete sub-players, each writing a
  different chip base ($D400/$D420/$D440), sequentially per frame.
- CANONICAL: a multi-SID tune = N independent single-chip tunes; extract/
  compose/verify each with single-chip machinery, chip-TAGGED
  (reg = chip*$20+reg). Voices number through chips; chip addresses are
  pipeline constants, never USF content. Per-instance write-stream QUIRKS
  (e.g. an editor build leaving chip 2's $D417 res/route write on chip 1)
  are per-chip CONFIG reproduced as-is — not bugs to normalize away, but
  PROBE them per member (C19 12th occ) — never hardcode one carrier's quirk
  as the default. A subtune need NOT sound every chip, and the wrapper picks
  each chip's SONG (Rayden: sub 0 both / 1 chip-1 / 2 chip-2, every chip
  always playing its own song 0) — observe both under py65 (C18), represent
  by which VOICES the subtune carries (no new field). TRAP: the merge kept
  only chip 1's params, silently dropping per-voice otrk scalars + any chip-2
  wedge. DETECTION traps: accept a NEUTERED call ($2C) in the wrapper scan;
  identify a chip by its ENTRY VECTORS never an address RANGE (players sit
  <1 page apart, the wrapper can lie inside a player's page); a C18 phase
  cycler can sit in FRONT of the calls → discover bases by RUNNING init.
- FULL ENTRY: [`ledger/C27.md`](ledger/C27.md) — read it before applying.

### C28 — multi-SID VERDICT: compare each chip's stream independently
- PRESENTS: a multi-SID rebuild that is per-chip correct still diverges in
  the merged chip-tagged stream — at a CROSS-CHIP adjacency (orig has
  [chip1, chip2], rebuild the reverse within a frame).
- CANONICAL: cross-chip order is physically UNOBSERVABLE (independent
  hardware — the multi-chip Trap B). Split by `reg // $20`; require each
  chip's substream to pass (`n_chips=N`). Do NOT chase capture cycle
  precision. Trap: short captures can show "byte-perfect" over a deeper
  blocker — verify at full songlength.
- FULL ENTRY: [`ledger/C28.md`](ledger/C28.md) — read it before applying.

### C29 — track $FF loop into an OUT-OF-IMAGE sector → live zeropage sonified
- PRESENTS: a voice's $FF loop marker resolves to a garbage sector past the
  pointer table → address $0000/below load. The file image there is zeros
  (decode = note 0 forever) but the ORIG audibly plays "impossible" notes —
  47, 55, then held low notes: it is reading the 6510 I/O port ($00=$2F,
  $01=$37) and static zeropage as note data.
- CANONICAL: overlay libsidplayfp's runtime low RAM onto the image for the
  decode (py65 cannot reproduce the environment zp — C9), gated on the
  loop-off-image detection, with port + sector-pointer read-time
  corrections. Regression-safe: unplayed decode is byte-identical.
- FULL ENTRY: [`ledger/C29.md`](ledger/C29.md) — read it before applying.

### C30 — lossy enum over independently-toggleable editor flag bits
- PRESENTS: a USF enum was derived from a FLAGS byte assuming two editor
  toggles are mutually exclusive; the corpus has BOTH bits set. The engine's
  priority makes one bit mechanically DEAD (audibly identical) — but the raw
  flags byte is OBSERVABLE via a state-as-data read, so the reconstructed
  byte (missing the dead bit) diverges the stream.
- CANONICAL: keep the enum = the EFFECTIVE articulation; carry the masked
  co-set bit as an elidable boolean CO-FIELD (`gate_open`), OR'd back at
  reconstruction. Never mint a 4th enum value; never store the raw byte.
  SMELL: any enum derived from independent flag bits — round-trip-verify
  reconstruction against the raw byte per instrument.
- FULL ENTRY: [`ledger/C30.md`](ledger/C30.md) — read it before applying.

### C32 — engine sticky state materialized into effective variants → fold to STATED notation
- PRESENTS: an extractor bakes engine STICKY state (transpose over the loop
  wrap; note length / instrument / volume carried across pattern
  boundaries) into per-context EFFECTIVE copies — orderlists ~2× the
  physical track with fitted byte-counter phase params (pad/period/rcmd);
  pattern pools inflated by entry-context variants (FC `(fc_id, init_len)`
  dedup — 41% phantom duplicates; `loop@N len=L` wrap pickup; DMC `~intro`
  decode variants — ~100% vol/instr carry); fit/fold-failure residue
  classes stuck partial.
- CANONICAL: fold to STATED notation by DIRECT OBSERVATION (never fitting):
  a value is written only where the source stream states the command
  (presence = the byte fact), absent = inherit — over wraps and pattern
  boundaries; leading runs resolve from init.voice_state seeds. ONE shared
  resolution interpreter (`src/usf/resolve.py`) serves both composers
  (compose-time materialization → byte-identity gate) + Layer-3. The
  extract RE-RUNS the resolver against the walk's ground truth (both
  passes); any mismatch → keep the effective form WHOLESALE. Emit no form
  the composer can't structurally discriminate (vol-only inheritance;
  auxiliary width shadows need ONE unambiguous source). WARNING: fitted
  models breed latent bugs (rho off-by-one) — observe, don't fit.
- FULL ENTRY: [`ledger/C32.md`](ledger/C32.md) — read it before applying.

### C31 — COMPILATION: one file packs N independent players; a dispatch wrapper selects (player, song)
- PRESENTS: the PSID header overstates songs; subtune 0 rebuilds FULL while
  others decode to silence/garbage (track pointers at $FE stops, sectors out
  of image) — because the file contains ≥2 COMPLETE copies of the player
  (distinct jump-table bases), each with its own data pool, and a small SMC
  wrapper at the init/play vectors patches a JMP hi-byte + song number from
  X-indexed tables.
- CANONICAL: detect from the WRAPPER's own base-table (≥2 distinct validated
  player bases); per-subtune (player, song) map; extract each player
  standalone (base_override; region-bounded locate); UNIFIED-MERGE into one
  model (renumber+dedup instruments, share/compact tables) → the ordinary
  composer. Players need not be the same engine (heterogeneous: dmc_sfx).
  Distinct from C27 (parallel chips every frame; here exactly ONE player
  runs per subtune). Analogues: FC Adrenalin, 5-Title-Tunes.
- FULL ENTRY: [`ledger/C31.md`](ledger/C31.md) — read it before applying.

### C33 — closing a `Params.fields` escape-hatch key → a typed field
- PRESENTS: a leak scan flags a `params.fields['<key>']` that affects the
  write stream but isn't quite musical CONTENT (init-phase engine state, a
  mechanism scalar). Instinct: "add a schema field" or "type it for the one
  engine." It is NOT opaque bytes (C7), NOT a wedge knob (C19).
- CANONICAL: it's a byte-identity CARRIER REFACTOR, not a schema addition
  (the value already lives in the USF → no representation gap, the schema-
  addition alarm doesn't apply). Recipe: (1) census ALL consumers first — the
  key is often cross-engine SHARED (scope surprise) + has DEAD readers to
  delete; (2) home it by cloning an existing typed field of the same
  trichotomy category (§4.5 priming → an InitState scalar beside slide_phase;
  a shared init_block rule serves file-level + per-subtune at once); (3) type
  by MUSICAL/SEMANTIC category, NEVER a composer-internal grouping (bundling
  by a composer's dispatch set re-leaks composer structure into the schema,
  §8); (4) gate = regenerate the USF (TEXT changes by design) + rebuild,
  require the .sid MD5-identical across EVERY consumer family. TRAP: a
  FULL-in-regression member can hide a BROKEN extract path (regression builds
  from a STORED .usf, not from regeneration) — regenerating to gate surfaces
  it (the C20 relative at the extract layer).
- FULL ENTRY: [`ledger/C33.md`](ledger/C33.md) — read it before applying.
