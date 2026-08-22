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
| byte-indexed program table · runs off-table · table extent / size · index overruns into adjacent array · in-table walk hits table end with NO marker (runaway ≠ hold) | C2 | factor-candidate (6×+: freq/pulse/wave×3/filter) |
| "no program" detection · leading (0,0) · idle position 0 | C3 | methodology |
| localize runtime divergence · writelog diverges, cause internal · memwatch | C4 | methodology |
| detection ≠ FULL · residue triage · accept-at-detect | C5 | methodology |
| off-table FREQ lookup · index past freq table · wave-relative note offset | C6 | recurring (FC + v5) |
| ANTI-PATTERN: verbatim/opaque musical bytes · leapfrog · content-by-reference blob | C7 | methodology (recurring) |
| de-fused per-entity pool exceeds byte-index capacity · "pool overflow" · separate copies per instrument | C8 | canonicalized |
| runtime param unreadable by py65 (init hangs / IRQ-set / bad opcode) · measure from libsidplayfp writelog · a SECOND build path that defaults probed params → fix the CONSTRUCTOR, not the knob · and check WHICH LAYER the canonical build attaches params at (probe table applied by the CALLER) | C9 | logged |
| chip-global $D415-$D418 automation during a song · master vol / filter varies · global_track vs MasterVolConfig/filter_programs · explicit-event vs parametric | C10 | logged |
| engine reads a table via an 8-bit index register (`base,Y` w/ Y=#*stride) · orig "reads garbage"/looks broken · extractor must wrap `(#*stride)&0xFF` · suspect OUR extractor not the packer | C11 | logged |
| off-table read sonifies a "positional" byte counter (sector position / stream offset) · per-event deltas derive from row kind + stated commands → live shadow, stated-command flags = §8 arrangement (DMC sectpos) | C11 | logged |
| off-table read sonifies the live WAVE POSITION ($177A) · composer pool offsets ≠ orig's → layout-preserving pool packing from per-instrument editor wave-table positions (`wave_table_pos`, §8 arrangement) + gated redirect row (DMC wavepos) | C11 | logged |
| accumulated per-step rounding drift in a round-trip · USF stores DELTAS (durations), player sums them to ABSOLUTE positions · a min/floor on each delta drifts over a long song · short tunes pass, long tunes length_fail · keep deltas EXACT (allow 0) | C12 | logged |
| engine variant dispatch · player jump-table init offset shifted but play body at canonical offset · "no_jumptable"/code-mismatch reject · dispatch on the PLAY-body signature not init (we emit our own init) | C13 | logged |
| command-per-row tracker effect (note + fx + param per row) · porta/vibrato/arp/filter/tempo on a row · NOT per-instrument · how to represent in NoteRow · DMC custom-build TEMPO MAILBOX (V3 instr cmd >= $10 = speed reload; probe + gated [$05,N] prefix event) | C14 | recurring (FC + GoatTracker V1 + DMC) |
| INAUDIBLE writes · idle/gate-off voice freewheels · "audio-equivalence" verdict relaxation | C15 | ⛔ REMOVED (user decision 2026-07-01): every SID gets STRICT write-stream match, always — never propose relaxing the verdict during per-engine work. If an idle-freewheel divergence blocks a member, REPRODUCE the writes (core tenet permits reproducing the mechanism). Design parked in `the_move-1_plan.md` as a Move-1-era-ONLY consideration. |
| per-frame WRITE-ORDER differs · orig batches note-on writes (SR/AD/CTRL) separately from wave-step writes (freq/PW/CTRL) or uses a different voice interleave · rebuild emits a different order · NOT a wholesale composer rewrite — PARAMETRIZE the composer's EMISSION order (precedent: FC `nextvoice_write_order`) | C16 | logged |
| HETEROGENEOUS per-step write shapes in a trace-lift · one superset order can't embed all steps (conflicting reg orders / intra-step dups / sections) · cluster steps by EXACT write shape → K positional templates + per-step template id | C17 | logged |
| play-vector WRAPPER with per-call PHASE behaviour · slow-tempo / multispeed-effects cycler · every Nth call runs the full play, others run effects-only / register-refresh / nothing · wrapper shapes vary (SMC, DEC+dual-JMP, parity AND) — OBSERVE entry-point reachability under py65, don't parse · arm F-ENTRY variant: wavestep ($1591) vs vibrato half-cycle ($1567, flips reshape vibrato to a square) → `effect_entry_variant: vibflip` | C18 | logged |
| TRICHOTOMY VERDICT alignment · rebuild emits its OWN init (universal reset+priming) so streams differ by an init prefix · Check A end-of-init state + aligned play-stream compare · TWO implementations exist: `verify_cycle._trichotomy_compare` (FC, shift recovery) + `usf_roundtrip._compare_music/_split_aligned` (basic_program, known-init-length + probe search) — CONSULT MISS, factor at Move 1 | C21 | factor-candidate (2×) |
| hand-patched player WEDGE inside the canon body · SMC opcode toggle · 1-byte opcode patch · JMP over canonical loads · runtime state ≠ static file byte · PWM bound-shift (LSR count) wedge · init-PREFIX `LDA #imm` hard-forces the played tune record (extract walks the wrong record) · STATIC opcode probe, never a bounded stream scan · census carriers both sides · reproduce semantics behind a factory-probed param (EXTRACT-only when the wedge changes a derived musical value; COMPOSER param when it changes a write-stream TIMING/VALUE, e.g. $D418 re-asserted every frame · SWITCH gate-toggle EOR immediate · multi-SID relocation MISS · glide-speed store re-pointed INTO SONG DATA = glide dead + runtime data poke · track-loop IMMEDIATE loop-to-N · $FF track-loop handler re-pointed at INIT = the song RESTARTS at the first track end (init writes land mid-stream, state resets — not loop-carried); SHAPE B (bare `A9 00 / 4C init`, wrap voice ≠ last) ALSO runs the remaining voices as GHOST units — reproduce init + captured V1-reg burst + surviving-voice state pokes (incl. the freq-determining curnote/gatemask BELOW $1718 that init doesn't clear) + skip-our-ghosts jmp-to-filter-tail; DISCRIMINATOR = the JMP target LEADS TO INIT (siblings whose `A9 00 / 4C` jumps the re-fetch LOOP are not re-init, reject them) · $D417 route-bit CLEAR store re-pointed to a void byte = routing bits accumulate, leftover res_routing persists · per-play fclaim CLEAR re-pointed to a void = filter claim persists, filter program frozen after the first claim (cutoff moves only on $F1 commands) · rest-tail RTS = rest_effects 'none', resting voice emits ZERO writes that frame · APPENDED DATA-ANIMATOR driver: both vectors re-pointed, SMC-phased ramp/LFO pokes the filter-def TABLE the player reads — res nibble WALKS across note-inits, SMC slot's file byte is stale · filter-tail stub pokes player DATA from PAST-EOF addresses = power-on pattern sonified (peek-post-init LIES there — psiddrv reloc; memwatch is truth) · the Ed driver FAMILY: 3 singleton appendix animators (SMC counters/indexes + generated tables poking def/wave cells) · $7D SWITCH dispatch BEQ operand re-pointed at canon's glide replay tail = $7D retriggers the stored glide note (branch-operand wedge, invisible to dmc_canon_diff) · drum freq-hi store re-pointed at the NEXT voice's PW-hi (freq hi stays the note's base; table byte pokes the neighbour) · $D418-every-play wrapper INDIRECT topology (play JT slot re-pointed JMP→appended `LDA #imm/STA $D418/JMP body`; follow one JMP from the play vector) · POST-NOTE GUARD immediate patched ($02→$00 at canon $12F8 = gate drops 1 frame after note-init not 3, ctrl gate-bit divergence → composer `note_guard_init`) · PULSE UP-REVERSAL bound operand repointed ($1759 bound-B → $1710 route-bit const at canon $1393 = PW up-sweep ramps the full 16-bit range → composer `pw_up_reverse='routebit'` = `cmp fbit,x`) · STATIC $D418 (both canon $D418 stores NOPed + init-wrapper writes a fixed mode|vol ONCE = no play-time $D418 → composer `master_vol_static=$3F`) · STATIC FILTER (re-assembled play NOPs `STA $D416`/`STA $D417`, filter cutoff/res set once at init = no play-time filter tail → composer `filter_static` · CONDITIONAL per-subtune tune-record remap (observed `subtune_songs` map) · $FF LOOP-hook store re-pointed OFF otrk = dead loop, tune HALTS+HOLDS at song-end (observe-confirmed; dead-code mismatches DON'T fire) | C19 | canonicalized (43×) |
| stale-FULL palimpsest · recorded 'full' the current code can't reproduce · hides members from residue censuses · verify the STORED build first, then USF-diff/param-bisect to attribute · never mass-write with code that didn't produce the verdict | C20 | canonicalized |
| AMBIGUOUS round-trip flag encoding · two distinct engine ops render to OVERLAPPING USF flag sets · the decoder's branch test uses a SUBSET of the discriminator → misroutes one op onto the other's path · matches for most content (paths coincide when inputs coincide), diverges on the distinguishing case | C22 | canonicalized (2×) |
| a play-phase/schedule TOKEN hides a per-member behavioural ambiguity · same P_F123 token = note-init-on-F vs deferred 2-frame arm · fixing one class REGRESSES same-token FULLs · NOT derivable from the token/multispeed → OBSERVE the distinguishing write-footprint per member · regression-safe when the "changed" verdict has no false positive · GENERAL FORM: any per-member build semantics a static probe can't address (re-assembled layout) — classify per-IRQ write-footprints all-or-nothing (deferred-wave note-init / hr prep $08-then-$09) | C23 | recurring (2×) |
| play-body UNIT-repeat · play body runs ONE of its 4 units (v0/v1/v2/filter-tail) N× per play() (JSR-to-N-call stub; JMP-tail form re-runs the filter tail) · "double-speed voice" · OR a unit REMOVED (count 0: INX inserted before the JSR — a two-voice build; one voice's writes wholly absent from frame 1) · unified play_unit_repeat=[v0,v1,v2,filter] list · distinct from play_repeat (whole play()) + C18 play_phases (whole calls) · static byte-probe (C19 method) | C24 | recurring |
| whole-play N-repeat (WHOLE play() body run N× per VBI = double-speed TUNE) via a play-VECTOR wrapper · perfect play-stream PREFIX + clean ~N× length tail on a VBLANK tune · `JSR T ×N :RTS` or `JSR T; JMP T` · `_detect_play_repeat` must FOLLOW a base+3 JMP indirection into the wrapper — or a JSR-FIRST wrapper sitting AT base+3 itself — never short-circuit on play==base+3 alone | C24 | note (recurring 12×) |
| composer play body OVERRUNS a tight CIA latch · perfect play-stream prefix + length tail ~0.5% (rate drift, no content divergence) · common-path cost creep (per-row compare chains growing with each round's shadow additions) · fast-path the common case O(1) · the rebuild's play must FIT the smallest latch it ships under | C25 | logged |
| song data ABSENT from file image · init generates/unpacks tables in RAM · operands point outside the loaded image · extract from POST-INIT RAM (py65), all-or-nothing signature · banking-wrapper JT-less base from the wrapper JSR target | C26 | logged |
| multi-SID (2SID/3SID) · N chips, one player each behind a dispatch wrapper · players run sequentially -> merged log = [chip1][chip2] · extract/compose/verify each with single-chip machinery, chip-TAGGED (reg=chip*$20+reg) · voices number through chips, addresses are pipeline constants not USF | C27 | logged |
| multi-SID VERDICT · rebuild is per-chip correct but the merged chip-tagged stream diverges on a CROSS-CHIP adjacency (chip1 vs chip2 write order) · cross-chip order is physically UNobservable (independent hardware, Trap-B analogue) · split by reg//0x20, require each chip's substream to pass · compare_instruction_stream(n_chips=N) · do NOT chase cycle precision / straddle-free capture | C28 | logged |
| PLAYED sector reads the EMULATOR ENVIRONMENT · $FF loop → $0000 live zp sonified · truncated-copy wrapper → power-on-RAM secp byte → KERNAL-tail window + patched psiddrv vectors + 16-bit wrap · sector-POINTER fetch itself off-image (track byte indexes past the pointer tables → power-on $FF hi-byte mislocates the sector, `_undefined_secp_reads` pre-pass) · gate = any played sector leaving defined RAM (`_offimage_sectors`) · CPU-EYE capture `siddump --peek-post-init` (`_cpu_peek`) · py65 pattern-seed (`_poweron_fill`) · overlay ONLY undefined bytes · NULL-POINTER LOOP TARGET: patched $FF handler reads loop-otrk via a zp pointer that is $0000 → reads ZERO PAGE (measure from LIBSIDPLAYFP not py65 — they differ) · LIVE-STACK window: below-SP bytes are deterministic PER READ SITE — the end-of-row PEEK and the row FETCH run at different call depths and see DIFFERENT stale bytes (same address!); serve each site its own measured map (`_dispatch_depth_serve` fetch + `_PEEK_DEPTH_MAP` peek, r137/b); lap-2 pairs by PLAYIDX; a garbage row can DOUBLE command prefixes — width flags are COUNTS (Deprave FULL, r137d) · ORDERLIST-POINTER itself in banked ROM ($F256 KERNAL) → `_offimage_track_ptrs` overlays it (STATIC ROM only; zp track-ptr = dynamic residue) · SCAN↔WALK: the off-image scans must mirror `_walk_track`'s post-transpose "next byte is a sector # even if >= $80" · PLAY-HEAD PORT RE-BANK: played code's own `LDA #imm/STA $01` overrides iomap(play) — ROM-range windows served per-ROM on the EFFECTIVE port (skip-zero-unpacker zeros read BASIC error text otherwise) | C29 | recurring (6×) |
| LOSSY ENUM over independently-toggleable flag bits · USF enum assumed two editor flags mutually exclusive (gate hold $10 / never-release $08) · engine gives one priority so the co-set bit is MECHANICALLY DEAD · but the raw flags byte is OBSERVABLE via a state-as-data read (off-table fxf) → reconstruction misses the dead bit · carry the masked flag as an elidable boolean CO-FIELD, keep the enum = the EFFECTIVE articulation | C30 | logged |
| COMPILATION · one file packs N INDEPENDENT players + a per-subtune SMC dispatch wrapper (subtune→(base,song)) · header overstates songs, sub0 FULL others silent/garbage · ≥2 jump-table bases · unified-merge (renumber+dedup instruments) · heterogeneous engines (dmc_sfx) · distinct from C27 parallel chips | C31 | logged |
| engine STICKY STATE materialized into effective variants · orderlist state over the loop wrap (fitted pad/period/rcmd) · pattern-row sticky duration/instr/vol (FC (fc_id,init_len) variants · len=L pickup · DMC ~intro decode variants) · fold to STATED notation (value present iff the stream states the command; absent = inherit) + ONE shared resolution interpreter (src/usf/resolve.py) · re-derivation assert, fallback wholesale | C32 | canonicalized (2×) |
| one FILE needs more than one COMPOSER · original packs players of DIFFERENT families behind a per-subtune dispatch wrapper · cannot be stored as one .usf · `origin_engine` Move-1 scaffold, boundary = "more than one COMPOSER" NOT "more than one engine" (5TT packs 5 sub-engines and needs none) | C35 | logged |
| packed-stream byte whose meaning depends on the DECODER'S POSITION · a command handler consumes the following bytes itself with its OWN coarser rules (skipping the top-level dispatch AND the terminator test) · MA: invisible to the verdict (round-trips) — corrupts USF CONTENT · DMC track transpose handler: post-transpose $FF = a one-row pseudo-sector, then loop WITHOUT sectpos reset (visible at the wrap) · the quirk must reach EVERY walk that mirrors the dispatch — the C29 GATE walks skipped it, silently disabling the zp overlay (pseudo-sector $0000; probe the 'endless' sim's ROW 0) · ONE-ROW LAW GENERAL FORM: engine re-dispatches track[pos] EVERY fetch, sectpos persists ($7F-only reset) → a post-transpose $80-$FD byte plays ONE row then MUTATES into a transpose (`runon` flag + composer sectpos base threading) · find it by READING the handler | C34 | recurring (4×) |
| close a `Params.fields` ESCAPE-HATCH key → typed field · untyped behavior-named scalar in the generic params bag (init-phase state / mechanism scalar), borderline §7 · NOT opaque-bytes (C7) / NOT a wedge knob (C19) · it's a byte-identity CARRIER REFACTOR not a schema addition (value already in USF) · census ALL consumers (often cross-engine SHARED + dead readers) · clone an existing typed field of the same trichotomy category · type by MUSICAL category NOT a composer grouping · gate regenerates + MD5-compares every consumer family (surfaces broken extract paths behind a FULL verdict) | C33 | methodology |
| PC-triggered bus tap false-fires on DATA reads of the trigger address · "capture at PC X" watches cpuRead, bus can't tell fetch from data · plausible WRONG snapshot · discriminate EXECUTION by the ≥3-consecutive-ascending-reads bus signature · validate any new tap by CROSS-EMULATOR byte-identity (also proves non-perturbation) · writelog_capture frame indices are COMPACTED (writes-only frames) vs raw siddump frames · GAP: 2-byte indirect sites (`LDA (zp),y`) are INVISIBLE to the discriminator — watch a 3-byte site at the same call depth with --pc-watch-abs | C36 | logged |
| subtune SAVE-STATE RESUME wrapper · header overstates songs, tune table has ONE record · appended init wrapper copies a per-subtune state snapshot + DATA POKES then forces song 0 · non-start subtune diverges at play pos 0, wrong first note/instrument · only init-wipe SURVIVORS matter (priming → init.voice_state; song-data pokes → per-subtune walk memory; wave/filter-table pokes → C31 clone-and-remap, def clones in unused nibble slots) | C37 | recurring (5×, all FULL) |
| song-end REST before the repeat (no fade; silence by NOT CALLING the player; RESTART first then rest) · typed `MusicSubtune.song_restart_gap` = the rest in play() calls · trigger is STRUCTURAL (every voice has entered its FINAL orderlist entry — a dedicated terminator pattern; peek whether the next track byte is the loop marker) · ⚠ do NOT store the orig's sentinel note (INAUDIBLE, and not even in the pattern data after transposition — §7) nor the survivors (save/restore around the restart, C31 medley carry) · MEASURE the rest (seeds say 255, truth 256) · probe: the rest must be preceded by the init's clear sweep, else a musical silence false-fires · ARM PER SUBTUNE | C38 | logged |
| song-end master-vol FADE → silence → whole-song RESTART loop · appended PLAY wrapper counts play() to N → `dec` mvol every STEP (note-init `ora mvol/sta $D418` emits it) → `$D418=$00` silence for SIL plays → JMP re-init loop · diverges DEEP in the REPLAY · restart re-runs the SHARED init (clears $1718-$179D, LEAVES $100F-$1018 survivors) · MEASURE schedule + survivors from libsidplayfp not py65 (pc-watch fade STA=N/STEP, writelog $00-run=SIL, memwatch-on-write d418 over silence=note-state) · modular wrapper (count/ramp/silence/songrestart) · ⚠ prime EXACTLY the init-uncleared block (gatemask/curnote/curinst=$1015/shadow17) NOT cinst (the ACTIVE pulse-record $174D that init CLEARS — over-prime sweeps a soft-glide voice's PW) · fade = C10 parametric mvol, restart = C37 sibling (whole-song loop not per-subtune) | C38 | logged |
| a data table the extract reads at a FIXED OFFSET from another table is a packer-patched OPERAND that can relocate INDEPENDENTLY · DMC filter step-DURATION table assumed at op_filtdef+10 (interleaved) but read via its own `LDA fdu,Y` operand → some members put it elsewhere (Vai/Hardtechno +165, all zeros = never-advancing filter steps) · TELL: a table-driven value right at the start then a DIFFERENT CONTOUR · resolve the table from the PLAY operand (gated on the canon opcode, fallback = the assumed offset, byte-identical) · distinct from C2 (index runs off the table END; here the BASE is wrong) | C39 | logged |

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
  Move-1 decisions D1/D2. Song-global cutoff/RES contours: the TYPED
  `filter_mod` block (loop/once, 1-2 taps, routing markers `direct` = the
  cutoff REGISTER itself / `res` = the prog's RESONANCE cell, a `period`
  contour clock, and `loop_to` = one-time lead-in + cycle) + ONE
  generalized interpreter now serve FC/Ed LFOs, the 4k_Byter one-shot
  morph AND the two Ed filter-def drivers (deconstructed 2026-08-16;
  sim + replay-verify in `filterdef_anim_lift.py`) — see entry.
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
  This includes the IN-table walk that reaches the nominal end with no
  terminator: the engine does NOT hold there — simulate the continued walk
  (cap-and-hold is the same nominal-length disease one branch later).
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
  include deferred note-init / soft-note TRANSITION reads, per-subtune
  post-init state, AND glide-ARRIVAL curnote reloads landing under a LATER
  instrument's wave (glide-to-0 dive → idx 255..; statically un-walkable —
  the event capture CREATES those records, gated to glide-target keys);
  non-canon state geometry must be probed before any live
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
- A3 — the PARAM-SHAPED leapfrog: a probe lifts an orig byte into a CONFIG
  FIELD and the composer emits from it — orig→output, never through the USF,
  just not shaped like a blob. TELL: a value that varies per MEMBER within one
  engine family and reaches the composer as a constructor argument (a family
  CONSTANT is mechanism and correctly lives in the engine). Live instance:
  fc_standard's std_vibrato_stale_tail / std_glide_hi_reg / std_arp3_init.
- ⚠ BYTE-IDENTITY IS A ONE-WAY GATE: `same bytes ⇒ same verdict` is valid;
  `diff bytes ⇒ different behaviour` is NOT. To decide whether a knob MATTERS,
  force a wrong value and verify against the ORIGINAL — diffing your own two
  rebuilds answers a different question (an init seed changes the `lda #$xx`
  immediate while the write stream is identical). Test real CARRIERS and report
  the carrier count, never one example.
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
- ⚠ FIRST ASK WHOSE CAP IT IS — before packing harder, check the constant is
  OUR composer's bound and not the ORIGINAL FORMAT'S transcribed from the
  disasm (TELL: its comment cites the orig's bit-field width). DMC's merged
  instrument pool was capped at the editor's 5-bit `$60+id` row field, which
  binds nothing in a composer that emits its own encoding; the real bound is
  the widest id-scaled index (8-bit, stride 8 ⇒ 32) and raising it to the
  measured value landed a 30-instrument member unchanged.
- ⚠ THEN WIDEN THE INDEX ITSELF past that bound — raising the constant alone
  aliases (ids ≥32 wrapped onto instrument 0, diverging at V1 PW lo). Shrink
  the STRIDE to the record's true width + a per-entity base BYTE (keeps the
  index 8-bit, one cycle cheaper than the shift chain, cap 256/stride);
  GATE on the count so everything below emits byte-identical code (proof =
  a corpus-wide MD5 rebuild); REFUSE where another feature encodes positions
  in the old layout. The ORIGINAL may have no answer to copy — its own index
  wraps EARLIER; the overflow is created by our merge of N packed players.
  3rd widening (r180): above 42, POOL deduped step blocks — istepbase = a
  per-instrument POINTER, capacity = distinct blocks ≤ 42, instruments ≤ 255.
  FIRST apply behavioral-identity dedup (C31) — the pressure is usually
  over-splitting, not content. 4th widening (Session): the SUBTUNE record
  index `subtune*16` wraps at 17+ subtunes → every sub ≥16 plays sub (k-16)'s
  record (state mismatch + wrong first note at play 0 across a subtune BLOCK);
  cure = init SMC-patches the reads' operand HI byte with `subtune>>4`, gated
  on >16 subs. TELL: diff the rebuild's own subtunes against each other first.
  5th widening (Artris 6/6, 2026-08-21): the merged WAVE POOL — 2 players'
  programs pool past the 8-bit wavepos though each player's own pool fits;
  SPLIT per subtune-component (`_split_wave_pools`: component idle at pos 0,
  init SMC-patches the 4 wave-step read operands via wpooltab[cursong]);
  fires only where the single pool overflowed = previously a hard error.
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
  When a param is measured in one build path, grep the OTHER constructors —
  and don't stop at the one knob: if a second constructor hand-rolls its
  config (TELL: addresses only, no probes / no `extra_params`), make it RUN
  the canonical build instead, keeping the hand-rolled form as a fallback.
  A defaulted knob is silently wrong MUSIC, not a refusal. 5th occ: "make it
  run the canonical build" is only a cure if you check WHICH LAYER the params
  attach at — the wedge-probe table was applied by the CALLER, one layer above
  the constructor the sub-player path stops at, so every wedge knob still came
  back defaulted. Grep the probe table's CALL SITES, not just the constructor.
  TELL when a retry hides it: batch FULL but a fresh build partial → the
  stored `.usf` and `.sid` disagree (C20 fifth layer). 7th occ: the speed
  mask is PER-SUBTUNE (a file mixes a CIA song with vblank ones) — rebuild
  a clean N× the orig's length on a NON-start subtune = the composer
  stamped the bit on every subtune; `PsidMeta.speed` already models the
  mask — populate + respect it, NO schema addition. 8th occ: a per-IRQ
  latch-reprogramming SWING driver has a NON-canonical steady rate — the
  probe's `19656//N−1` is a hypothesis; check it against the MEDIAN of
  per-frame period estimates (a raw mean is poisoned by the init-gap
  outlier — census every estimator before landing). 6th occ: the init
  probe can SUCCEED with a plausible WRONG latch (fine byte programmed at a
  site init never runs — KB's $2600 vs measured $2663) → CROSS-CHECK every
  init-probed latch against the measured entry period, prefer the
  measurement on a STABLE disagreement (`_cia_period_crosschecked`).
- 9th occ (f2 dual_parity_addr): the defaulted knob can be a STATE-VAR
  ADDRESS inherited from canon in a variant family (f2 parity beside its
  RELOCATED shadow) — audit the canon PAIR when one var moves; and census
  the VARIABLE'S READERS, not the flag naming it (13 predicted, +254
  recovered). 10th occ (f2 $FF loop imm, 2026-08-21 — Conversion + Witchs +
  Just_11, f2 CLOSED 100%): a probe handling a WRAPPER that POKES an operand
  (X-mas per-subtune loop target) proved the operand is a live knob — but
  nothing read its SHIPPED value; 10 carriers walked loop@0 instead of
  loop@N. Three "unrelated deep classes" were all downstream of the wrong
  wrap rows; the decisive measurement = the orig's otrk AT the wrap.
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
- PRESENTS (wavepos): a note-init/wave-step freq write diverges and an
  instrument's (wave offset + note) & $FF hits fhi idx 211-213 ($177A-$177C =
  live wave position). CANONICAL since phase 4 (2026-07-28): POSITIONAL pool
  emission from the stated wave_table (norm carriers — full 256-cell table
  verbatim, labels native, chain walks included; compose-side resolve proof,
  idle validated against the table's own walk). Legacy old-form fix =
  layout-preserving pool (`wave_table_pos`); the
  verbatim gate admits NON-verbatim programs that are UNOBSERVABLE (every
  wavepos read self-referential to a verbatim instrument → free-slot
  placement, r98). ⚠ `dmc_offtable_probe`'s by-value attribution has
  mis-fired 3× here (6× overall) — r116 added the PROXIMITY GATE (only
  ±3-frame-window matches are trusted; far matches labeled coincidences),
  but still check idx 211-213 against instrument offsets FIRST.
- PRESENTS (live-redirect): an off-table read sonifies ENGINE STATE — the
  first-divergence value equals a live counter / position / scratch var, not
  a static byte. f2 vdep row (2026-08-14, Spice_Up): a SLIDE-form glide
  (`noretrig`+`glide=`, target = the ROW PITCH, 8-bit-wrapped) sends the
  arrival compare into $178C-8E = the live vib increment — the row is
  FAMILY-SCOPED (parametric offtable_live_idx: canon f1's $178C is not
  vdep) and READER-GATED (glide_offtable OR a 229-231 record; the broad
  gate rebuilt thousands of non-readers byte-different). ⚠ the
  glide_offtable derivation must scan BOTH target forms (glide_to= AND the
  slide row-pitch form); ⚠ verify play_match vs find_first_divergence flat
  position are DIFFERENT COUNTERS — never read a small delta BETWEEN tools
  as progress. TELLs: a cluster whose (orig,mine) values are EOR-$0F
  complements = redirect row naming the complement var; "voice drops one
  update at a pattern boundary" = init-cleared seed; per-(inst,off,note)-
  stable dynamic byte = event-driven capture. Diagnostic (a/b/c): wnote
  matches + var matches ⇒ add a redirect row; wnote differs ⇒ wavepos layout;
  var differs ⇒ non-tracking accumulator (hard). ALL read sites must honor a
  redirect (incl. the glide-ARRIVAL compare — served via the same map, gated,
  r97; 4th site 2026-08-21: the f2 vib-INCREMENT `lda freqhi,y` at note-init —
  an off-table note reads its own live fbh, vdep = fbh>>1; the static byte
  starves the swell, presenting as a missing vibrato excursion or a phantom
  down-slide — `nv_rd_sub`, gated `vib_inc_redirect`; For_Nitro +
  Hot_Mallorca FULL), sparse vars need seeding, shared scratch is shadowable by mirroring
  all writers. ⚠ a sparse-var SEED holds only if the leftover SURVIVES the
  member's init: the canon clear loop wipes $1718-$179D (gla/glb included),
  so canon-init members' frame-0 glide state is $00 — gate the igla/iglb
  seeds on the init CLEAR-RANGE probe (`glide_leftover_cleared`, r177
  Other_Side: seed $5E vs the orig's cleared $00; 98_Mix's re-assembled
  $0342-clear family keeps the leftover + the seeding). Full entry has the remaining hard boundaries (dynamic
  work-RAM); the former "off-table glide target" boundary is RESOLVED (r97 —
  the 2nd re-measure expiry: dtmph now tracks 1:1, exact parse + live-served
  arrival landed 109/109 class FULL + Cleve_24).
- ⚠ THE MIRROR — A REDIRECT ROW CAN BE WRONGLY *APPLIED*: rows are mapped by
  ADDRESS and extract stamps `live` on `idx in live_idx` alone, never checking
  whether the value MOVES. Where the var's writers are enumerable, constancy is
  PROVABLE and a live stamp asserts a movement that never happens (vibdel
  $1771,x: written only at that voice's note-init, else only DECed, init-cleared
  ⇒ a voice that never plays a `vib_delay` instrument holds $00 all song). Prove
  from the WRITE SITES, don't sample — the proof caught 27 members where a
  siddump census had flagged 18. Drop PER VOICE (2026-08-10): the row is a
  contiguous range, so live voices survive as contiguous-run sub-rows with
  expression labels (`lda vibdel+2-204,y`), expanded at the otmap build only;
  eligibility = the explicit `DMC_DEREDIRECTABLE` allowlist (inferring from
  staticness would eat the non-canon detector), and those idx are EXEMPTED
  from `_static_at_live`. ⚠ when EVERY record-bearing voice is dead the WHOLE
  row still drops (the historical form — else all 27 prior converts re-churn).
- ⚠ A RECORDED REJECTION OF A REDIRECT ROW EXPIRES. "Our var doesn't track
  theirs" was measured against ONE composer on ONE date (often on ONE family);
  the composer is re-implemented continuously. RE-MEASURE before accepting it
  as a boundary: `siddump ORIG --memwatch-on-write <diverging reg> <orig addr>`
  vs the same on the REBUILD with OUR label (`return_labels=True`), compared
  event-by-event. TRAP: the player is usually RELOCATED — offset every watched
  address by the member's `base`, or you are watching garbage (TELL: watched
  bytes that contradict the write stream). $1720 fclaim, rejected 2026-06-29,
  landed 2026-07-23 at 0 regressed / 11 gained.
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
  equal immediates). Worked third form (r124): the $FF handler with canon
  loop-to-0 store + author TEXT overwriting the re-dispatch JMP — the text
  EXECUTES (BVC into the dispatch, A=$00) and injects a spurious note-0
  row each wrap (`loop_note_inject`); pc-watch decided what static reading
  couldn't. A per-member STATE-address locator is dispatch too: a re-assembled
  member can SPLIT its state block (audible note-fetch/wave-step path at one
  delta, a dead glide-init at another) — locate curnote from the note-fetch
  WRITE site (`TYA/STA $1012,X`), not the first-occurrence glide-init READ, and
  cross-check (no-op when they agree ⇒ byte-identical). Pulsate: idle-seed read
  the wrong array → a freewheeling voice's +$9A note error; probe MIS-FIRED
  by-value while pc-watch showed the wave-step IN-TABLE.
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
  first; it is almost always a bounded emission-order knob. UNIT-ORDER form
  (Ofyron_Gadaf 2026-08-21): the filter tail runs BEFORE a voice (neutered
  in-body JSR + a 9-byte play wrapper) — audible purely through WHEN the
  tail samples the routing shadow (pre- vs post-clear); composer
  `filter_before_voice=N` splices the tail into the voice-call sequence.
  TRAP: the member's shadow was RELOCATED into "header text" ($1034) — a
  canon-address memwatch reads static and the byte dump reads as a static
  wedge; watch the RELOCATED var at the writes before concluding either.
- FULL ENTRY: [`ledger/C16.md`](ledger/C16.md) — read it before applying.

### C17 — heterogeneous per-step write shapes in a trace-lift
- PRESENTS: a trace-lifted write model assumes ONE step template but the tune
  has K distinct step shapes (alternating textures, per-section orders,
  intra-step duplicate registers) — no single superset order exists.
- CANONICAL: cluster steps by EXACT (attack, release) register-sequence shape
  → K positional templates + per-step template id; K=1 is the special case.
  Prefer deriving WHAT a step writes from row-level event types + a few named
  order knobs (normal form) — full templates in USF is Pole B. When the
  normal form's row-derivation seems to hit its limit (a slow interpreter
  splits one event's writes MID-VOICE across frames), check whether the decl
  vocabulary already carries the grouping: THE DECLS ARE A GRAMMAR, THE
  READER IS ITS PARSER — whole-song backtracking parse of the per-(onset,
  voice) event queues, combined-candidates first (2026-08-11 refinement).
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
  entry reachability BOTH WAYS (a held note's F looks like R; an R whose
  vibrato runs ADVANCES and looks like F — effects-tail-entry reachability is
  R-positive, Real_Hardcore); variant F/R entry points exist (vib_half,
  pulse_tail, and the f2 `pulse_tail_hi` — R step = stale wjmp HIGH nibble, no
  parity swap; parity P/R wrapper under a tight CIA latch, Knowledge_Posse) —
  full entry lists them. ⚠ the observer's watch PCs are f1-canon offsets —
  blind on f2 wrappers; a static skeleton probe covers the known f2 shape. When the wrapper is the SMC JSR-TABLE idiom, the per-call TARGET sequence is static ground truth — force same-target calls to ONE (majority) token; a single-call F/R misread otherwise starves a multi-step wave program one advance per cycle, invisible until the program's next value change (Hexzakk). Same failure via a DIRECT `LDX #v / JMP base+$591` wrapper call (an idle voice's ADVANCING arm entry misread as R) — static-flip the R token to F + force the arm mode (Mathematika_II, Radio_Napalm). F-PHASE PER-VOICE REPEAT (massive multispeed, PVCF/Sound_Test, STIL '11-speeder'): the effects branch runs `JSR SUB xk`, SUB advancing each voice's wave-step m× → V_i steps m*k/E-call in the interleaved order (a flat total would diverge); static-decode the nested JSR structure → `fphase_repeat` 'k:VxC,..', composer expands the F-token to outer×[voice×inner] wave-step calls (the C18 F-phase analog of C24 play_unit_repeat; sole carrier in 10,676).
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
  per-STORE while the knob is per-register — cure by naming the store with
  the COMPOSER LABEL of the routine that plays its role (`00@sidwrite`),
  never an address; an unmapped site keeps the coarse behaviour, no guessing.
  A re-pointed store can also land INSIDE THE SONG DATA — the wedge then
  BOTH kills the mechanism (glide dead ⇒ decode speed 0) and POKES runtime
  state over a data byte the music later plays (simulate the poke in the
  extract; TELL: a note-init off by a fixed amount only on a pattern's
  LATER occurrences). An APPENDED driver can also ANIMATE THE DATA the
  player reads (SMC-phased res ramp + cutoff-init LFO poking the filter-def
  table; probe the SMC aim from the INIT immediates — the slot's file byte
  is stale). A wedge can be a lone BRANCH OPERAND re-pointed at other CANON
  code (Dreck's $7D SWITCH BEQ → canon's glide replay tail = $7D retriggers
  the stored glide note) — same-opcode branch repoints are INVISIBLE to
  `dmc_canon_diff`; when a canon-family member's divergence has no probed
  wedge, raw byte-diff it against the canon binary. A repoint can also aim
  ONE effect's store at ANOTHER effect's state (drum freq-hi store →
  next voice's PW-hi: freq hi stays the note's base, the table byte pokes
  the neighbour's PW). A multi-immediate site's probe must capture EVERY
  immediate — a pattern anchored on one canon immediate (`A9 81`) is blind
  to a patch of that same immediate (cymbal ctrl $81→$02, 26th occ) · the
  $FF handler wholly REPLACED by `JMP stub` with PER-VOICE immediate loop
  targets (CPX dispatch; no canon site ⇒ the binary classifier defaulted
  to read-next-byte garbage — 27th occ) · the forced-tune-record wedge's 3rd FORM: `LDA #imm / JSR base` deep in a longer init wrapper (29th occ) · the play-clock parity byte EMBEDDED IN A PLAYED SECTOR — a glide row's start note IS the live counter (30th occ, `note_clock` row flag + labeled-seed mechanism reproduction) · the pulse-base ADC re-pointed into SID-MIRROR space — reproduce the exact absolute read, gate to $D4xx-space operands only (31st occ) · the $D418-every-play wrapper's INDIRECT topology — the canon play JT slot (base+3) re-pointed `JMP <appended wrapper>`, the wrapper `LDA #imm/STA $D418/JMP <real play body>`; `_d418_play_wrapper` follows ONE JMP from the play vector (32nd occ) · the DURREL-RAMP driver (33rd occ, Rayden f1 +3) — an appended non-canon routine cycles a 4-entry table and writes ALL voices' durrel every V1 advance = a GLOBAL period-4 note-duration beat; ⚠ a composer param reproducing it is the PRINCIPLE §8 LEAK — a wedge changing a MUSICAL VALUE (duration) is DECONSTRUCTED to per-row `duration` EXTRACT-ONLY (patterns 4-beat-aligned → row i = table[i%4], no C32 variants, no composer/schema change; $8x-driven carriers untouched byte-identical) · the POST-NOTE GUARD immediate patched (34th occ, Rayden/NOFX_tune_2 +1) — note-init `LDA #$02` at canon $12F8 → `#$00` = the end-of-note gate-off is no longer skipped, gate drops 1 frame after note-init not 3 (ctrl steps to wavectrl&$FE early); a write-stream gate TIMING → COMPOSER param `note_guard_init` (`_note_guard_probe`, imm iff !=$02); TELL = ctrl $20/$21 (gate) divergence on the first wave-step, guard $1786,x is 0 at note-init not 2 · the PULSE UP-REVERSAL bound operand repointed (35th occ, Rygar/Complications +1) — canon `CMP $1759,x` (pwh vs bound B) at $1393 → `CMP $1710,x` (the route-bit const $01/$02/$04), so the PW up-sweep reverses at the route bit not bound B = a voice starting above its route bit ramps the FULL 16-bit PW range (wraps); write-stream PW → COMPOSER param `pw_up_reverse='routebit'` (`_pw_up_reverse_probe`) → `cmp fbit,x`; TELL = orig sweeps monotonically past its (correct) bound B, byte-diff the $1393 CMP operand · STATIC $D418 (36th occ, Signor/Logic_Intro +1) — BOTH canon $D418 stores NOPed (init base+$5C + filter note-init base+$2A8) and an appended init WRAPPER writes $D418=fixed mode|vol ONCE (`LDA #$3F/STA $D418`), so $D418 is set at init and never during play (a static filter mode); default composer writes it per filter note-init (501× vs the orig's 2) → composer `master_vol_static=$3F` (init primes it, note-init emits no $D418); TELL = orig's TOTAL $D418 count ~2 vs rebuild's hundreds · STATIC FILTER (37th occ, SilverFox/Blood_2_game +1) — a RE-ASSEMBLED play routine keeps the filter-tail LOADS but NOPs `STA $D416`/`STA $D417` (`LDA $171C/EA EA EA ... ORA $1723/EA EA EA`), so the filter cutoff/res are set once at init and never during play; default composer writes them per-frame (2761× vs the orig's 3) → composer `filter_static` (no play-time filter tail); TELL = orig's TOTAL $D416/$D417 count ~2-3 vs rebuild's per-frame · the forced-tune-record wedge's 4th FORM — CONDITIONAL per-subtune remap (38th occ, The_Magical_Garfield/Bomberman_preview +1) — init wrapper `STA c / LDA c / CMP #$00 / BNE / LDA #$05 / JSR base` remaps ONLY subtune 0 → song 5 (subs 1-3 straight), a map [5,1,2,3] uniform `forced_subtune` can't express (its probe REFUSES the conditional shape); extract walks record 0 → subtune 0's V2/V3 tracks read as `$FE` stops = the tune mis-decodes; a byte scan can't see the branch so OBSERVE (C18/C31): run init(A=sub) per header subtune, read A entering base, use it iff NON-identity + NON-uniform → cfg `subtune_songs` (extract-only, `_rec_of` generalizes `forced` int→list; sole corpus carrier, 1 anchored member = 0 perf/regression) · the $FF-reinit GHOST shape's JSR-INIT RESUME form (39th occ, Verdict/Verdict_01, sole carrier — member FULL as of r166) — a 3rd $FF-handler shape `A9 00 / 20 <init> / 4C <base+D2>` (JSR the real init + JMP the canon re-fetch IN-FRAME; init clobbers X=$18 → THREE ghost units vs shape-B's two); teach `_track_ff_reinit_ghost_probe` the anchor, REUSE the ghost capture + `track_ff_reinit_ghost` branch (the burst reads FILE-IMAGE constants, member-constant). Two reusable 0-regr refinements it surfaced: `_reinit_ghost_state_map` += `shadow17` (a survivor the ORIG init PRESERVES but ours RE-primes = the $D417 fix; poked only WARM≠COLD so For_Party byte-identical) + REMAP the `curinst` poke orig#→slot (the poke carries the raw orig survivor; the composer's curinst is the COMPACTED ioffval slot, id=orig#+1; identity when uncompacted). RESIDUE — the ghost frame ALIASES `INC $1729,x`/`STA $172f,x` at X=$18 onto the glide state (glsp=$03 @ $1741, glb=$A7 @ $1747), so V1 runs a GARBAGE glide whose arrival compare reads off-table into the state block ($16A7+$A7=$174E=ioff+1) — a plain C6 read SERVED by `m.glide_offtable` for the ghost member (existing redirect maps $174E→ioff+1; freq MATCHES). The LAST blocker was ONE garbage INSTRUMENT-RECORD read (r166, member now FULL): V1's pulse step reads `$18f3[$07]=$18FA` (a mid-11-byte-record byte) because the ghost frame de-links ioff from cinst ~1 frame — reproduced by emitting an 11-byte-record IMAGE by orig# (`irecimg`, from the composer's OWN arrays, byte layout recoverable from musical fields) + reading the step via ioff (byte-identical when ioff=curinst*11). ⚠ FIRST mis-framed 3× as a "C6/C11 dynamic-work-RAM hard boundary" — re-testing each time showed the garbage read was of a STATIC table (freqtable, instrument records) and thus SERVICEABLE from the composer's data; the genuinely-hard case is DYNAMIC work-RAM, which this member never hit. Don't repeat the over-claim. · the $FE track-STOP handler re-pointed at the KERNAL RESET vector (40th occ, r167, Wayne/Dark_Side +1 FULL, sole carrier) — canon $FE (base+$E9) `A9 00 / 9D 0C 10 (STA $100C,x = clear voice-active) / 60` = PER-VOICE stop (voice freewheels, others play on); wedge overwrites the first 3 bytes with `4C E2 FC` = `JMP $FCE2` (KERNAL RESET), so the FIRST voice to hit its `$FE` stop resets the machine → IOINIT `STX $D418` (X=0, $FDC4) = a lone `$D418=$00` silence → the CPU idles in the BASIC loop = the WHOLE song HALTS (no more writes). Default per-voice-stop composer KEEPS PLAYING past that (stopped voice freewheels, others run on). TELL: a divergence in the ~10% tail where the orig writes a lone `$D418=$00` at a NEW frame then emits NO more writes (identical held snapshots) while the rebuild keeps writing per-frame; orig writes $D418 nowhere else (set once at init). DIAGNOSE: pc-trace the `STA $D418` → PC `$FDC4` (KERNAL); binary-scan `JMP/JSR $E000-$FFFF` finds `JMP $FCE2` at the $FE handler (`dmc_canon_diff` blind — RE-ASSEMBLED). FIX (CORE TENET, reproduce the stream not the reset): `_track_fe_reset_probe` (anchor `C9 FE D0 06` at base+$E5 + `JMP $FCE2`, reloc-aware) → composer `track_fe_reset`: the $FE handler emits one `$D418=$00`, sets a `halted` byte (OUTSIDE state0..state_end; init runs once), unwinds the frame (`pla/pla` drop the jsr voice return, `jmp pf_exit` skip remaining voices + filter tail); every later play() checks `halted` at playframe entry → RTS with no writes. No param → canonical per-voice stop, byte-identical (10-member golden set incl. the 2 non-carrier Wayne siblings). Distinct from `track_ff_reinit*` ($FF LOOP→INIT = whole-song RESTART); this is $FE STOP→RESET = whole-song SILENCE+HALT. · the forced-tune-record wedge's 5th FORM (41st occ, r173, Yuro/Fatamorcana_intro +3 FULL) — a RE-ASSEMBLED member whose base does `JMP $1807` (NOT canon `JMP base+$1D`) with a wrapper `LDA #imm / TAX / TAY / JMP base` that no fixed static shape parses; `_forced_subtune_probe` rejected it on the canon-dispatch guard. FIX: for a non-canon-dispatch base + `LDA #imm` wrapper, OBSERVE (C18) — run init(A=sub) under py65, read A at base (`_init_song_observe`), fire iff UNIFORM+NON-IDENTITY. ⚠ THE OBSERVATION ALONE FALSE-FIRES (a wrapper whose `LDA #imm` is not a record index / an init that IGNORES A reads A=imm at base but plays record 0 — census saw bogus forced 99/90/49, though those all ERROR `no_jumptable`): CONFIRM with `_init_forced_changes_state(base, forced)` — enter the init BODY at `base` (bypassing the A-overriding wrapper) with A=0 vs A=forced and require post-init RAM to DIFFER (the init actually USES A). Regression-safe: a FULL member walking record 0 has A==0 at base (identity, no fire); an init that ignores A → equal states → no fire. · the FILTER-TAIL cutoff LOAD operand repointed fcut→fbase (42nd occ, r174, Zyron/One_Man_and_Boris + Gop/Buddhas_Garden, +2 FULL) — canon filter tail base+$A0 `LDA $171C (fcut, swept cutoff) / STA $D416`; wedge repoints the LOAD operand one byte down to `LDA $171B` (fbase = filter-def base index def#<<4), so $D416 sources the DEF INDEX (per-def constant, steps on def change) not the cutoff; `_filter_cut_from_fbase_probe` (static: `AD` LDA-abs at base+$A0, operand==base+$71B, followed by `STA $D416`) → composer `filter_cut_from_fbase` loads fbase; regression-safe (canon operand +$71C returns None → byte-identical). Found by `dmc_canon_diff` (canon-layout member). · the $FF LOOP hook's store re-pointed OFF otrk (43rd
  occ, r175, Zyron/Solar_Energy +1 FULL) — the JSR-hook's `STA otrk,x` operand
  aimed at a dead address ($6726) = the loop never advances, play() spins on
  `$FF` at song-end → the tune HALTS+HOLDS (zero further writes, NO $D418=$00 —
  the "end, don't loop" trick); TELL = pure length tail (all orig writes match,
  rebuild runs longer with a re-init burst) + otrk frozen at the $FF positions;
  probe `_track_loop_dead_probe` = static store≠the dispatch's own LDY operand
  + OBSERVE-CONFIRM the orig halts (writes cease ≥20 s before songlength×1.15+30
  capture end — the static mismatch alone false-fires on DEAD-code dispatches:
  KB/PVCF relocated members store to un-relocated $1726 but never reach the
  hook, and the recorded songlength can end at the fade SHORT of the halt) →
  extract walks $FF as STOP + composer halt-and-hold ($FE handler, the
  track_fe_reset machinery minus its $D418 write). 55 occurrences (53rd-55th:
  the f2 singleton trio — vib-swell ADC->ROR with a NEIGHBOR-POKE writeback
  (reproduce the orig ADDRESS MAP neighbor, not label+1 — Petshopmix); the
  def-index ADC->EOR abs,x whose meaning depends on RUNTIME X = the claiming
  voice, MEASURE it (Inside); the dead fdu store = filter advances every
  frame (Childs_Play); 52nd: the
  f2 $10C3 duration-fetch branch BEQ→BMI = fetch on UNDERFLOW — every row
  lasts one extra tick, the init seed lasts two plays; presents as
  "diverges at play position 0" though every row is stretched; knob
  `dur_fetch_underflow`, temporal family of tempo_override — Delta_Zak;
  51st: the
  f2 $1571 vib direction-flip writeback re-pointed to a void = accelerating
  one-way pitch drift — DECONSTRUCTED per the 33rd-occ rule to the typed
  `vibrato { shape: drift }` (owner-approved enum growth), NOT a knob;
  lesson: the mechanism-knob reflex fires fastest when a sibling knob
  family exists — re-run the 33rd-occ test per occurrence; 44th: the f2 $11C4
  rampctr CLEAR re-pointed dead = the vibrato swell PERSISTS across notes
  (legato swell) -> typed `vibrato_ramp_persist`; 45th: the 4k_Byter
  instrument-byte animator NOT probed as a wedge — deconstructed per the
  33rd-occ rule to the C1 one-shot filter_mod contour, now enforced
  mechanically by tools/composer_param_lint.py; 46th: the f2 fetch-frame
  PREP-CTRL immediate $08→$40 (`prep_ctrl`, 3 Brian carriers incl.
  Rowdy's relocated sub-player = the C31 per-subtune form); 47th: the f2
  filter note-init `STA $D418` killed while the INIT mvol store survives
  (`d418_noteinit_dead` — distinct from the 36th's master_vol_static);
  48th: the f2 filter-tail `STA $D416` NOPed (`filter_cut_static`) beside
  an appended cutoff-table cycler deconstructed to the C1 `filter_mod`
  DIRECT entry; 49th/50th: the f2 vib singles — the $12F5 vdep store
  re-pointed to CMP (`vib_step_dead`, swell ramps by 0) and the $11BE
  vibdir clear patched to a 2-byte EOR whose MISALIGNMENT kills the vibctr
  clear too (`vib_phase_persist`, the persist family's phase flavor);
  28th: the
  negative-transpose ADC immediate — canon
  `EOR #$1F/ADC #$01` biased to #$11, $81 → +$0F; extract-only
  `transpose_neg_bias`) — the full entry catalogues every known wedge.
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
- FOURTH LAYER — a CONSUMER takes a DIFFERENT BUILD PATH than the VERIFIER
  (writer, localizer, or the REGRESSION HARNESS — 2026-08-22: regression built
  every DMC portfolio member as a single player, so two COMPILATIONS pulled in
  by a portfolio re-derivation read as REGRESSED with the C31 signature, sub 0
  FULL and the rest garbage; cure = `verify_member` runs the canonical
  dispatch and RAISES on an unimplemented path).
  `code_hash` proves the verdict came from current code, NOT that the stored
  artifact is what earned it. DMC's mass-writer built every member through
  the single-player constructor while the batch dispatches multi-SID ->
  compilation -> single, so multi-SID members were stored as 3-voice
  single-chip `.usf` for 6-voice tunes — hash-blessed, well-formed, WRONG,
  and invisible to every gate. RULE: a mass-writer must call the SAME
  dispatch as the verifier; when the build path grows a branch, grep every
  tool that reconstructs a member. DETECTOR: re-verify FROM THE STORED
  artifact (not a fresh in-memory build). CLOSED structurally by
  `src/corpus_sync.py` (shared by every `*_mass_write.py`): the batch
  RECORDS `build_path` and the writer REPLAYS it; non-FULL members get their
  orphaned artifacts DELETED (nothing else ever does); the writer audits a
  path-stratified sample from disk.
- ORPHAN DELETION — a batch may only delete what it OWNS. The orphan rule
  assumes the batch owns every member it lists. FC's batch sweeps every HVSC
  FutureComposer SID but `fc_standard_config` REFUSES the Tel-variant canaries
  (`flagged`); read as "not full" they were orphaned and their stored
  `.usf`/`.sid` DELETED (Cybernoid_II / Hawkeye / Adrenalin), breaking the
  regression. Distinguish NOT MINE (extractor refused ⇒ skip the row entirely,
  `plan(out_of_scope=('flagged',))`) from MINE-AND-FAILED (`partial`/`error`/
  DMC's `unsupported` = my member, can't build ⇒ genuine orphan). TELL: the
  orphan list names ANOTHER path's canaries — inspect `plan().orphans` before
  any sync whose batch sweeps a whole engine family. NB deduping rows exposed
  this: a canary previously had both an old `full` and a new `flagged` row, so
  it was deleted then immediately rewritten — two wrongs cancelling.
- FIFTH LAYER — the stored `.usf` does not REBUILD the stored `.sid`. Writer
  and verifier take the SAME path, but the build consumes a PARAMETER absent
  from the stored `.usf`: DMC's batch write-stream RETRY set `hold_gateoff` on
  the PARSED object, recorded it in the jsonl, and the mass-writer re-injected
  it post-parse. Verdict right, `.sid` right, `.usf` beside them specifying a
  DIFFERENT build — and NO gate sees it (batch green, hash matches, `.usf`
  parses AND is byte-identical to a fresh extract, and the 4th-layer audit
  re-verifies the `.sid`, which passes). TELL: a member reads FULL in the batch
  but a fresh build verifies partial with IDENTICAL numbers across unrelated
  code changes. Split the layers: verify the stored `.sid` → diff stored vs
  fresh `.usf` → rebuild FROM the stored `.usf` and compare bytes. DETECTOR
  (wired, ALL families): `corpus_sync.audit_rebuild` asserts
  `build(rel, stored .usf) == stored .sid` — the corpus-side Principle §8
  invariant, general to any build input that leaks outside the USF; it needs
  only the family's BUILDER (no verify signature), which is why it lives in
  corpus_sync unlike the verdict audit. CURE: push the value onto the CONFIG so the
  writer emits it natively (a parse→write round-trip is NOT available — the USF
  round-trip isn't byte-stable, 20/60), refuse the member if it still misses,
  and root-cause why it was absent (here C9's 5th occ).
- THIRD-LAYER CLEAN-UP, WORKED (2026-07-22): the 80 residual unreadable `.usf`
  split EXACTLY along their failure cause, and the two halves needed OPPOSITE
  actions — which is why "delete the stale ones" would have been wrong. 52
  (`dcmd`, a renamed fx flag) were FULL under current v4 → regenerate. 27
  (`speed_ctr_init` left in `params` by the typed-field move) came back
  `DMCV4Unsupported: no_jumptable` — which reads like "not full ⇒ orphan ⇒
  delete", but is the ORPHAN-DELETION rule's **NOT MINE** case: they are DMC
  **v5**-owned, and all 27 verify FULL there. Deleting them would have
  destroyed 27 verified artifacts. RULE: before deleting an artifact because
  path A refuses the member, ask which path OWNS it — an extractor refusal is
  evidence about the PATH, never about the member. Then restore the fifth-layer
  invariant too: regenerating a `.usf` leaves the neighbouring `.sid` built by
  older code, so rebuild it FROM the stored `.usf`.
- SIXTH LAYER — NET AGGREGATE COUNTS MASK REGRESSIONS: a closeout printing
  "+57 full" hid 4 full→partial regressions between two DMC batches
  (cdfa9c42's overlay contaminated 3 Flash members; d80c1b94 broke
  Other_Side) — both carrier-censused fixes whose EXPOSURE sets weren't
  enumerated; the alphabetical queue had passed their letters, so they sat a
  week. DETECTOR: `tools/batch_diff.py OLD NEW [--fail-on-regression]` at
  EVERY closeout; triage regressions FIRST, separately from the tail.
  Attribute by MD5-bisecting the member's BUILD across the window.
- SEVENTH LAYER — the ORIGINAL changed under the stored artifact (a COLLECTION
  UPDATE, HVSC #84→#85). The mirror of every layer above: the INPUT drifts, not
  our code. No gate can see it — code_hash speaks about our code, corpus_check
  parses fine, regression builds from the stored `.usf` and never from the
  original. ⚠ DO NOT match members by WHOLE-FILE hash: an update's dominant
  edit is a CREDIT/TITLE fix (which is also what drives re-filing), so
  whole-file matching read 47 members as "gone" when 46 were merely RENAMED —
  the orphan rule would have DELETED 46 valid artifacts. Identity across
  versions = the PSID PAYLOAD hash (bytes after dataOffset); the three-hash
  compare (header/payload/whole) classifies every member in one pass as
  carry / reextract_header / move[_reextract_header] / reextract_data / delete.
  Gate the header-only class by BYTE-IDENTITY (payload identical ⇒ write stream
  cannot move ⇒ re-verification learns nothing) — it also surfaces artifacts
  built by older code. ALSO: classification is PATH-keyed, so an update silently
  shrinks every family (DMC 10,676→10,642) — compare family counts across the
  update and carry classifications over by payload. AND renaming the tree edits
  docstrings in fingerprinted files ⇒ `code_fingerprint` changes ⇒ every batch
  verdict goes stale (5,401 DMC rows at once); sequence it with a planned batch.
- EIGHTH LAYER — the recorded verdict's VERIFY WINDOW was weaker than
  ratified: a `_dur` cap (bp `min(songlength*1.1, 120)`) recorded FULL on
  truncated evidence — 44/49 exposed long members were false FULLs, and every
  gate reused the capped window so the verdicts were self-consistent. TELL:
  old rows' `len_a` ≪ the ratified-window capture; any cap in a dur helper.
  CURE: remove the cap, re-verify the WHOLE exposure set at the ratified
  window, re-lift or orphan-delete casualties. Second-order: the window's
  SOURCE (SLDB songlength) is itself broken for RSID-BASIC (precalc dead-air)
  — measure first-gate-on + last-write before trusting an entry
  (31 measured `songlength_overrides` corrections).
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
  known-length + probe) — consult before writing a third. The verdict is
  sound only under SYMMETRIC OBSERVATION: a capture that drops the init
  prefix on one side (per-IRQ + an orig that DEFERS a chip's init burst
  into an early play(), Kordiaukis 2SID) makes Check A compare primed state
  vs invisible defaults — fix with `writelog_per_irq_capture(keep_init=True)`
  (the |N chunk), never by deferring the rebuild's init to match.
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
- GENERAL FORM (2nd occ): the rule serves ANY per-member build semantics a
  static canon-offset probe can't address — a RE-ASSEMBLED build's note-init
  that RTSes before the wave step (init frame = AD/SR only, note lands next
  play) + a prep that writes ctrl $08-then-$09. Classify per-IRQ chunks
  from the original's writelog (`_noteinit_defer_probe` →
  `noteinit_defer_wave`/`hr_prep_gate`); gate to dataflow-path members,
  skip under a C18 phase wrapper. ⚠ NEITHER gate is strict all-or-nothing —
  a HIGH-MULTISPEED CIA member (the Wodnik family, r168-169) has the occasional
  per-IRQ BUCKETING COLLISION (two play()s merged into one capture bucket).
  DEFER-WAVE (Akademia, r168): the merge puts a deferred init's AD/SR with the
  next play's wave ctrl = a false canon-init, per-chunk INDISTINGUISHABLE ⇒ use
  the RATIO `with_ctrl*5 < inits` (< 20% carry ctrl), not `== 0`. HR-PREP-GATE
  (CH2, r169): the merge PREPENDS the prior note's ctrl → `[$41,$08,$09]`, which
  a strict `== [$08,$09]` misreads as canon, but the `[$08,$09]` SUBSEQUENCE
  survives ⇒ test the SUBSEQUENCE + relax the aggregate to `preps_gate9*5 >
  preps*4` (> 80% show it, absorbing the rare bucket that SPLITS $08/$09). Both:
  the two populations separate with a huge empty gap (canon 0% / ~100% vs the
  variant's ~100% / 0%); 0-regression is STRUCTURAL — a FULL-without-variant
  member is canon-shaped (a canon prep writes $08 ALONE; a canon init carries
  AD/SR+ctrl same-play) ⇒ can NEVER fall in the flip band, only variant-shaped
  PARTIALS flip. ⚠ SPARSE defer members (LONG notes, King_Leter r170) need the
  window ESCALATED (10s→30s when `inits<8 and with_ctrl==0`) — but naive
  escalation REGRESSES cymbal siblings (R1/R2/R4/R5 FULL→8.8%): a cymbal note
  LANDS as a `$81` burst and the capture SEPARATES its AD/SR from the burst, so
  the standalone AD/SR is a false "melodic init". R1/King_Leter are per-chunk
  IDENTICAL (`[ad,sr]`-only); the discriminator is the note's LANDING — the same
  voice's NEXT ctrl write, `$81`=cymbal (EXCLUDE, extend the same-frame cymbal
  exclusion to this deferred/split form) vs a melodic gate-on (real deferred
  init). `with_ctrl` alone can't tell real-defer from split-canon; the landing
  can (AMEND worked example — the escalation regression was the signal the
  premise "AD/SR-only chunk = deferred init" was a blanket model).
- FULL ENTRY: [`ledger/C23.md`](ledger/C23.md) — read it before applying.

### C24 — play-body UNIT repeat / whole-play N-repeat
- PRESENTS (unit): one of the play body's 4 units (voice 0/1/2/filter-tail)
  runs N× per play() via a redirected JSR stub — a "double-speed voice", or
  doubled $D416/$D417 writes (JMP-tail re-enters the filter tail). f2
  zero-count form (Koshimo '0,1,1,0'): a per-voice call re-pointed at the
  tail's RTS (voice removed) and/or the LAST JSR patched to a tail-call JMP
  (the fall-through filter tail removed — no $D416/$D417 all song).
- PRESENTS (whole-play): a VBLANK member with a PERFECT play-stream prefix
  and a clean ~N× length tail — the whole play() runs N× per VBI. Count
  writes/frame, then disassemble the play VECTOR and FOLLOW its JMP
  indirection (`JSR T ×N :RTS` / `JSR T; JMP T`). A CIA member with a
  clean ×1.5 tail at an IDENTICAL measured rate = the ALTERNATING form
  (parity wrapper doubles every other call; per-play counts 34/17 vs flat
  17) → observed parity → a `P2` token in the C18 phase alphabet. 5th form
  (r161, Vegeta/Heniek): the SMC-immediate parity wrapper `LDA #imm / INC
  abs(==the LDA operand) / AND #$01 / BEQ / (JSR T)* / JMP T` with MULTI > 2
  — even=single, odd=(k+1) body-runs (Heniek 1/3, a clean ×2 tail; per-IRQ
  17/51) → `P_P{multi}` (`P_P3`), the composer's `P2` token generalised to
  `Pn`; probe FOLLOWS the play-vector JMP + detects both parity shapes. 6th
  form (r162, Vegeta/Trzewiki): a periodic-COUNTER wrapper (NOT parity) `LDA
  cz / CMP #M / BNE / LDA #$FF / STA cz / (JSR T)+ / INC cz / (JSR T)* / JMP T`
  = BASE bodies/IRQ + `extra` every (M+1)th → a UNIFORM period-(M+1)
  `play_phases` schedule M×`P{BASE}` + 1×`P{BASE+extra}` (Trzewiki `P4`×40 +
  `P5`, reuses the composer Pn token, no composer change). FULLY STATIC (the
  multi frame is deterministic from the CMP — no observation, unlike parity).
  TELL: perfect flat prefix + a NON-INTEGER length multiple (×4.024); a
  constant `play_repeat=BASE` is short by 1 body/period (Trzewiki −0.6%).
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
- MIRRORED CLASS (orig OVERRUNS its own latch, rebuild too fast): honest
  residue ONLY for un-attributable slowness. When the overrun is a SPECIFIC
  reproducible per-play OP — Strange_Acidshit's play VECTOR re-arms $DC04/$DC05
  (the SAME latch) every call (~12 cyc), which our init-only setup skips → we
  run faster → length overshoot — reproduce THAT op (`_cia_rearm_probe` →
  `cia_rearm_per_play` → composer `playcia:` wrapper). ⚠ GATE on MEASURED orig
  overrun (period > latch), NOT the static re-arm shape (105 carriers): fire
  only when orig overruns (our lighter body overshoots → re-arm helps); skip
  when orig fits its latch and OUR body is heavier (undershoot, e.g. Compozak
  0.9986 → re-arm would worsen). Firing set 10, all FULL; C9 measure-don't-guess.
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
  cycler can sit in FRONT of the calls (or BE the play vector) and a player
  can be reached by JMP not JSR → discover bases by RUNNING init (JSR-only
  pass first, JMP-inclusive retry after). A SUB-PLAYER IS AN ORDINARY
  PLAYER: build it through the canonical path with the base forced, never a
  hand-rolled config (C9 4th occ) — first generalise the masked compare over
  per-chip `$D4xx` operands, and any probe keyed on a per-chip engine
  constant (the zp track pointer). PER-CHIP PARAMS ARE A CLASS (keep_regs +
  `play_phases`/`noteinit_deferred`): a wrapper can run ONE chip per call →
  COMPLEMENTARY schedules (`P_S`/`S_P`), each chip at half the timer rate;
  accept an 'S' phase only on that structural evidence. TIME-MULTIPLEXED —
  SAME FORM WITHOUT A SECOND CHIP (Techno-Rap, BUILT + FULL): a ~100 Hz CIA
  alternates TWO INDEPENDENT tunes, both writing $D400-$D418, each at
  ~50 Hz. Built as SIX voices with NO sid2 declared (no schema addition —
  the composer derives same-chip + one-player-per-call from `>3 voices and
  psid.sid2 is None`); `detect_multiplex` = strict static wrapper shape,
  1 carrier in 8,369; init runs the players IN ORDER while play starts with
  the SECOND (Check A is last-write-per-register, so init order decides
  whose priming wins); two player-body copies are emitted deliberately
  (the one-body alternative touches 91 sites in the body every DMC member
  compiles from, to save bytes no gate measures). ⚠ do NOT collapse the two bursts
  into one frame — the flat stream then matches byte-for-byte (verdict says
  FULL) but the bursts sit 50.2% of a frame APART, so bunching shifts one
  whole tune ~10 ms against the other: the worked example behind the
  **Trap B BOUNDARY in the_core_tenet.md** (intra-frame position is SIGNAL
  when the orig spreads work across sub-frame IRQs). Diagnose by splitting
  the per-IRQ capture by PARITY; mind the capture STRADDLE (a truncated
  chunk's tail opens the next chunk — it reads as a content divergence).
  RELOCATING WRAPPER
  (C31 × multi-SID, Mothafucka_2SID): init copies players AND SONG DATA out of
  the file image (chip 1's player at $1000 but its sectors at $8000+, zero-fill
  in the image → garbage rows) — when ANY chip's player is out of the image,
  extract EVERY chip from POST-INIT RAM (`post_init_sub` threaded through
  `_config_at_base`), in-image members byte-identical.
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

### C29 — PLAYED sector reads the EMULATOR ENVIRONMENT (zp / ROM / power-on RAM)
- PRESENTS: a played sector's pointer resolves out of defined RAM — a $FF
  loop into a garbage sector# → $0000 (live zp sonified: port $2F/$37 then
  static zp), OR a truncated-copy wrapper leaves a secp byte at POWER-ON RAM
  ($FF stripe) sending the sector into banked-in KERNAL ROM with a 16-bit
  wrap (Super_Seven $FFEF: the jump table's $4C opcodes ARE "note 76", plus
  psiddrv's PATCHED reset vector). File image/py65 reads zeros there. OR the
  SECTOR-POINTER FETCH itself is off-image (track byte indexes past the
  pointer tables; secp_hi[n] past EOF reads power-on $FF → the sector is at
  $FFxx, not the image-zero $00xx — Trailways_A: KERNAL's `JMP ($0320)`
  operand IS the audible note 32). TELL: every voice's note = ours + K with
  otrk/sectpos/transp in lockstep — the walk agrees, the CONTENT differs.
- CANONICAL: `_offimage_sectors` gate (ANY played sector leaving defined
  RAM — incl. a sector BASE past the IMAGE END in plain RAM, 2026-08-21
  Final_Game+James_Bond+Fantasia: the power-on $FF stripe IS f2's in-sector
  terminator, so the environment ENDS the pattern where image-zeros decode
  an endless self-loop and the walk folds loop@N; base-past-end ONLY — the
  window-tail form flags 44% of the family, the Kaj2 gate-on-the-walk rule)
  + `siddump --peek-post-init` CPU-EYE window capture (banked ROM incl.
  patched vectors + port + RAM pattern in one mechanism) + `_poweron_fill`
  pattern-seeded py65 + `_undefined_secp_reads` pre-pass (serve off-image
  POINTER bytes the CPU-eye value BEFORE resolving sector windows).
  ⚠ overlay ONLY undefined bytes (≠ image,
  ≠ init-written) — spurious garbage-record windows clobber real data.
- NULL-POINTER LOOP TARGET (Hank/Roots): a patched $FF-loop handler reads the
  loop-to otrk through a zp pointer that is $0000 on this member, so it reads
  ZERO PAGE `$0000+otrk+1` instead of the track — each voice loops to a live zp
  byte (a player scratch / the track-ptr-hi slot). ⚠⚠ **MEASURE FROM
  LIBSIDPLAYFP, NOT py65** ([[feedback_ground_truth]]): the read sources are
  uninitialized/player-written zp whose value DIFFERS between emulators (py65
  read $00 where siddump reads $87, and the two even play different NOTES
  post-loop). Gate the override to the null read only — compare the measured
  landing to the canon default `track[otrk+1]`; a valid pointer lands within a
  few transposes of it and is already correct, so LEAVE IT (an "override any
  non-start landing" heuristic regressed 3 valid-pointer siblings).
- ORDERLIST-POINTER class (Memomania): the out-of-image read can be the TRACK
  (orderlist) POINTER ITSELF, not a sector — a tune-table track ptr lands in
  banked ROM ($F256 = KERNAL; others $C2xx) so the whole orderlist is read from
  ROM and played (sector-1 melody + a transpose walk). `_offimage_track_ptrs`
  pre-pass overlays the CPU-eye window (shares `_overlay_offimage_windows` with
  the sector overlay), BEFORE the secp/sector walks. ⚠ STATIC ROM ONLY
  ($A000-$BFFF / $E000-$FFFF); a below-load/zp track ptr reads DYNAMIC RAM
  (served 0 = old zero-fill) so overlaying only MOVES a divergence. ⚠ GATE to
  NON-post-init members (like `_undefined_secp_reads`): a post-init member's
  ROM-range orderlist address is GENERATED RAM, not banked ROM (Kan-Kan $A3A1)
  — overlaying it clobbers the generated orderlist. Memomania landed FULL via
  this + the C34 one-row generalization (runon/sectpos threading) + the
  PLAY-TIME PORT rule below.
- PLAY-TIME 6510 PORT: psiddrv sets `$01 = iomap(play_addr)` before each
  play() — a player at/above $A000 runs with BASIC banked OUT ($36), while
  `--peek-post-init` snapshots the IDLE-time $37. A $0000-window read at
  offset 1 sonifies the PLAY-time value (`_psid_play_iomap`); the peek's $37
  decoded Memomania's note one semitone high. Corollary: under $36,
  $A000-$BFFF is RAM at play time — the ROM-window rules hold only when
  iomap(play) = $37. ⚠ THE PLAYED CODE ITSELF CAN RE-BANK (r176, Flash
  members): a play wrapper opening `LDA #$35 / STA $01` banks BASIC+KERNAL
  OUT although iomap(play)=$37 — every ROM-range window is then RAM at play
  time, and serving the peek's ROM bytes overlays BASIC ERROR TEXT over
  init-GENERATED data (zero bytes a skip-zero unpacker never writes are
  "undefined" to the mem≠ref gate wherever the power-on pattern is also $00
  → per-byte ROM-text contamination of instrument records; TELL = decoded
  fields that are a BYTE-MIX of real data and ASCII). WAVE-WINDOW surface
  (7th occ, Kaj2): the wave step's 8-bit Y makes the idle marker-chase
  mod-256 — a window past EOF sends the chase through environment bytes
  (pos 0 → $FF past EOF, power-on ≥ $90 chains on; idle voices cycle
  garbage ctrl cells the image-zero view never reaches). Same overlay,
  GATED to "the idle walk's sim visits a past-EOF position" — the broad
  window-off-image gate is REFUTED (an unplayed instrument chain that
  settles on zeros CYCLES on the true bytes → hard reject, LSD_4K; and it
  changes verdict-proven bytes, Andjana). Static probe: an
  `A9 imm / 85 01` pair in the play-vector head overrides `_psid_play_iomap`;
  the overlay's ROM ranges are gated per-ROM on the EFFECTIVE port
  (BASIC in iff port&3==3, KERNAL iff port&2). 10 static carriers in
  HVSC-DMC; +3 FULL (Itinerant/Kan-Kan/Wind_of_Dead), rest byte-identical.
- SCAN↔WALK CONSISTENCY: `_offimage_sectors` / `_undefined_secp_reads` must
  MIRROR `_walk_track` — post-transpose byte is a sector # UNCONDITIONALLY
  (orig $10FE-$1101, no re-dispatch) even when >= $80 (`$F3 $A5` = sector $A5).
  The scans only special-cased post-transpose $FE/$FF (C34) → missed the
  $80-$FD case → off-image sector un-overlaid, walk self-loops on image zeros.
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
  boundaries; leading runs resolve from init.voice_state seeds whose VALUE
  is the engine's init state OBSERVED (the $1015,x work-file leftover —
  canon init does NOT clear it; never assume 0). ONE shared
  resolution interpreter (`src/usf/resolve.py`) serves both composers
  (compose-time materialization → byte-identity gate) + Layer-3. The
  extract RE-RUNS the resolver against the walk's ground truth (both
  passes); any mismatch → keep the effective form WHOLESALE. Emit no form
  the composer can't structurally discriminate (vol-only inheritance;
  auxiliary width shadows need ONE unambiguous source). WARNING: fitted
  models breed latent bugs (rho off-by-one) — observe, don't fit.
  ENDLESS-TAIL (r128): an unterminated mod-256 sector self-loop FOLDS —
  one track byte carries lead+period entries at EQUAL offsets (intro plays
  once, the loop re-fetches steady at the frozen otrk); admission scoped
  to cycle-length-1 tails, longer cycles keep the encoding-equivalence
  refusal. SLOT-MODEL fold (r183, the loop_not_rho lever): closures NOT
  at the rho boundary (inject-rotation / multi-region $FF-jump tracks /
  multi-pass transpose convergence / new-offset re-entry) fold via
  first-visit slot linearization + whole-walk replay (`_fold_slot_model`;
  strict one-intro variant shape). ⚠ a fold-acceptance change's exposure
  census = a whole-family BYTE SWEEP, not the otrk-field census (fitted
  pad/period carriers are invisible to it — 19 of 24 were). BYTE-FAITHFUL
  stated notation (I5, 2026-08-06): the 3 residue refusal buckets
  (mid-sector re-entry / C34 dual-role / loop-landing past the mark)
  share ONE root — the engine re-enters the byte stream past stated
  commands carrying live decode state; store the AUTHORED byte structure
  (`orderlist stated faithful:` — dual `&`, mid-track jumps `@T`, landing
  skip `>K`, ring/endless/inject terminators) and DERIVE re-entry offsets
  + carried transposes by REPLAYING the dispatch
  (`pipelines/dmc/track_replay.py`; double replay-vs-walk proof in walk
  AND compose space; the composer MATERIALIZES at compose time — no
  player change).
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
  composer. Players need not be the same engine (heterogeneous: dmc_sfx, MA,
  DMC V5 beside V4 — a V5 sub-player can be PARTIALLY RELOCATED: dead paths
  left at canon; per-player file-level pools ride per-subtune overrides
  incl. wave_programs).
  Distinct from C27 (parallel chips every frame; here exactly ONE player
  runs per subtune). Analogues: FC Adrenalin, 5-Title-Tunes.
- DON'T keep teaching the static wrapper parser new shapes (scaled index
  `ASL A;TAX`, lo/hi vector PAIRS) — OBSERVE (C18/C27): run init(A=subtune)
  under py65; the LANDING is the player, A is its song. Later pass + a
  ≥2-page-aligned-base pre-gate = zero-regression. TRAP: observation alone
  cannot separate this from a MULTI-SID member whose wrapper gates chips per
  subtune (Rayden) — discriminate on the PSID chip count.
  ⚠ EXCEPTION — NON-PAGE-ALIGNED bases (Pievspie/Mission_Moon $5E24, $5000):
  "observe instead of teaching static" FAILS here because observation is ALSO
  page-aligned by construction (`--pc-watch` watches low-byte $00/$48; the
  pre-gate scans page-aligned addresses; `_is_player_head` asserts `a&0xFF==0`).
  A wrapper that carries an explicit lo table + hi table selecting non-page-
  aligned bases is INVISIBLE to both. So DO teach the static parser this ONE
  shape: pair the two `LDA abs,X` tables (`base = lo[x] | hi[x]<<8`) and validate
  every base with a page-alignment-FREE exact-canon-offset check
  (`_is_canon_base_unaligned`) — strict enough that a spurious pairing can't
  validate; sole carrier in the family.
- RELOCATING WRAPPER: the packed player may not be IN THE IMAGE AT ALL — the
  wrapper COPIES it into RAM per subtune, so an image scan can never find it
  (C26 applied to DETECTION). Admit via a 2nd pre-gate "≥1 in-image base AND
  the init vector does NOT lead into any of them" (2.7 s over 5401 members, 0
  FULLs change path); DROP the load-address floor on every RAM read (a player
  can be copied BELOW load); snapshot AT THE LANDING, not post-init (running
  init to completion overwrites the very leftovers read as PRIMING); and give
  EVERY layer that memory view — the PROBE TABLE included (C9 5th occ one
  layer further out: probing a base the image lacks reads zeros ⇒ every wedge
  silently DEFAULTED). Per-player facts the merge collapses to the START
  player are a recurring family: `d417_shadow` (→ per-subtune
  `init.sid.filter.res_routing`, no schema addition), a disagreeing WEDGE
  KNOB (`rest_effects` → `MusicSubtune.params` + gated composer runtime
  dispatch, Super_Seven; 2nd/3rd knobs `vib_ramp` + `prep_ctrl`, Rowdy —
  sparse overrides, file-level stays the START player's; the standalone
  per-player build+compare splits merge-loss from missing-probe), `idle_wave` (→ per-subtune `MusicSubtune.
  wave_programs[0]`, Mission_Moon), the INSTRUMENT NUMBER a note sonifies via
  the off-table `ioff` read (idx 166-168 = orig inst# * 11; the merge
  RENUMBERS each player's instruments into one pool → `record_offset` per-
  instrument field carries the ORIG offset + rides the dedup key so different-
  offset instruments never share a slot, Goldrake), and any memory RE-READ
  inside extract (the filter-def post-init window decoded all-zero). RULE: any
  RUNTIME measurement inside a per-player extract must run the FILE subtune
  that SELECTS that player (song numbering is LOCAL; the wrong subtune leaves
  that player's work RAM at the never-inited file-image leftover — a stable,
  well-formed, WRONG byte). And no FILE-LEVEL idx-keyed composer table (the
  off-table window) can hold a per-player fact: attribute records to subtunes
  by the instruments their ROWS play, patch the disagreeing positions at init
  (gated ⇒ conflict-free members byte-identical). ⚠ BEHAVIORAL IDENTITY IS
  THE MERGE DEDUP KEY (r181): positional fields (record_offset / wave_start /
  wave_pool_pos) ride `_inst_key` ONLY for players with a position-sonifying
  read (ioff 166-168 ∪ wavepos fhi 211-213) — unconditional stamping was §6
  Rule-1 over-splitting and drove Lane_Crazy past the C8 cap (verified: 23/23
  merge_models members FULL under the default). SINGLE-PLAYER FORM (r99):
  the window fact can be per-SUBTUNE through ONE SHARED instrument (track-ptr
  slots are per-subtune init state) — instrument-usage attribution can't
  disagree, so the extract SPLITS the instrument per sampled VALUE-CLASS
  (clone + remap the disagreeing subtune's rows; `ovr_sub` then serves each).
  DEAD-CARGO REFINEMENT (2026-08-21, Blast_n_Scream + Zwei_Bereten FULL):
  `ovr_sub` is last-wins over ALL records of USED instruments, so a record a
  subtune never READS can overwrite the byte it does read at a shared window
  position — (a) split clones now filter records by song attribution; (b) the
  cross-instrument form (no per-record value disagreement, split never fires)
  is cured by `_declutter_offtable_by_reach`: clone-and-remap gated on an
  actual read-value collision (unattributed/idle records stay everywhere;
  same-song two-value positions = C11 dynamic residue, skipped).
- SUB_BURNER's THREE (2026-08-20): a copied player's TWO-JMP head parked
  BELOW its body → implied base = play-$85 (C13; guard: init==base+$37,
  base > head) · per-subtune IDLE-PULSE record (`idle_pulse_instr` — an
  idling voice runs ITS player's record-0 pulse program; the pulse sibling
  of idle_wave) · `filter_def_orig` (the fbase read idx 116/212 sonifies
  the ORIG def#<<4 — serve a SHADOW, ⚠ never re-anchor the def window:
  that broke the verdict-proven Lane_Crazy whose readers' remaps are
  unobservable).
- THE MERGE CAN FAIL BY REFUSING, NOT ONLY BY COLLAPSING (r182, Bayliss/
  Heavy_Metal_Solid_preview +1 FULL): `merge_models` ASSERTED the packed
  players share a freq table and RAISED, dropping the member to the
  single-player fallback = every non-start subtune built from the WRONG
  player's data (sub 0 FULL, sub 1 wrong from its FIRST note). Tuning is
  per-tune CONTENT (§7/C7 category C), so carry it per-subtune like every fact
  above — `MusicSubtune.freq_table` already exists (r93), NO schema addition.
  ⚠ COMPOSER: PATCH the shared tables at init (per-subtune `(note,lo,hi)`
  stream, `$FF`-terminated, beside the `ovr` window patch) — do NOT repoint the
  base, `freqlo`/`freqhi` are contiguous with the off-table window and all
  off-table addressing depends on that adjacency. ⚠ LATENT SIBLING: the census
  found tuning disagreement in 1 member but VIBDEPTH disagreement in 22 —
  RESOLVED 2026-08-10: measured per-index, that signal was ~all the relocating
  code-overlap head (idx 3-4) + unreached notes (the raw `vibdepth` copy is
  DEAD — no downstream consumer); the sonifiable fact is the REACHED
  `offtable_vibdepth` dicts, conflicting in only 4 members, now carried as
  sparse per-subtune `MusicSubtune.offtable_vibdepth` overrides + a
  FIXED-LENGTH count-based `vpat` init patch (a $FF terminator collides with
  idx 255). Gate was the RE-VERIFY of all 22 (C7's one-way gate), 22/22 FULL. ⚠ METHOD: this was nearly mis-diagnosed 3 ways
  (detection miss / instrument-cap residue / C35) by acting on the CARD;
  detection was fine. Read the entry.
- IDENTIFYING an unfamiliar packed player: build the opcode skeleton from
  REACHABLE CODE ONLY. A window spanning the player's SMC/scratch bytes is
  member-specific and reports "1 carrier in HVSC" for a player that actually
  has thousands (Freespace_2075's sub-players scanned as unique, then matched
  6,349 Music_Assembler members). Cross-check a candidate skeleton's carriers
  against the `engine` column before concluding anything about rarity.
- A RE-ASSEMBLED player may carry only a TWO-JMP head (init/play vectors) then
  DATA at +6, not the canonical three-JMP head → the three-JMP predicate
  rejects it and the file falls to the single-player path. Generalise to the two
  vectors + a reloc-invariant target-range guard (`[base, base+$1000)`) as the
  false-positive gate; prove 0-regr by an old-vs-new detection diff over the
  whole family (only the intended None→compilation members may change). MERGED
  FILTER-DEF window: preserve a GENUINE overrun's record adjacency, but
  `repeat>5` OVER-approximates "genuine" — a dur-0-pinned step stays in-record;
  simulate the `fx_filter` step-walk and test whether the index actually reaches
  ≥6 (a LOOPING repeat≤5 def hits the sim cap → do NOT key on settling, it
  regressed 2 FULLs). Overrun-anchored layout = op's window verbatim at native
  indices to reach R, others in free slots R+1..15 (cap 16).
- MERGE TRAPS, both invisible until a voice idles a WHOLE song (a track that
  is a bare `$FE` stop): merged slot 0 must stay RECORD 0 (init clears the
  note-init cache to 0, so idle voices run record 0's pulse/wave mechanism —
  the merge rebuilt the pool from ROW-referenced instruments and lost it); and
  idle PRIMING is PER-SUBTUNE, each packed player having its own work-file
  leftovers → ride `subtune{init{voice N{note/gate_mask/dur_reload}}}` (NO
  schema addition — same file-level-vs-per-subtune split as `speed_ctr_init`),
  with the composer's table widening GATED so existing members stay
  byte-identical. `idle_wave` (the cleared-cache lead-in wave a voice walks
  before its first note) is the SAME per-player fact and is now rode per-subtune
  too: the merge sets per-song `idle_wave` (compilation.py), to_usf emits it as
  the pre-existing `MusicSubtune.wave_programs[0]` override ONLY where it differs
  from the file-level idle wave, and the composer APPENDS each distinct override
  to the wave pool and primes that subtune's voices' `wavepos` to its position
  (`sub_iwpos`, reusing the `per_sub_prime` subtune*3+voice init addressing).
  Two players whose wave tables differ at pos 0 otherwise made the non-base
  player's idle voice walk the WRONG wave → its freq-base cache (fbl) diverged →
  an off-table freq read of fbl mis-played (Pievspie/Mission_Moon sub 1: fbl+1
  idx 233 read $8F vs orig $F7 — landed FULL). Gated so single-player /
  same-idle-wave-compilation members stay byte-identical; INCOMPATIBLE with the
  layout-preserving / positional wave pools (which pin wavepos to the orig's
  live $177A), where it is IGNORED (collapsed-idle residue, never a build fail).
- TIME-MEDLEY VARIANT (r150, Praiser/Mega_Mix): the dispatch is on the PLAY
  vector + a frame COUNTDOWN, not the init vector + subtune — one file packs ≥2
  players, exposes ONE looping PSID song, time-switching player1(seg0)→player2
  (seg1)→loop. SEPARATE static detector (`detect_medley`/`_parse_medley_wrapper`/
  `_parse_reinit`) — `detect_compilation` scans the init vector (here just P1's
  cold init). Extract each base, `merge_models` ONE SUBTUNE PER SEGMENT, carry
  the schedule as the composer's gated `medley='seg:lo:hi,...'` + `play_repeat`;
  `playmedley` reproduces countdown/double-play/re-init; `songs=1`. Sole carrier
  in 10,676 (0 false-pos); strict shape + build+verify gate (C13). NEW per-player
  fact the merge collapses: the $D417 routing accumulator (shadow17 = $1018).
  Native measure ($101D writes ONLY $1719-$1794 → $1018 CARRIES; orig P1 $1018
  and P2 $2818 are separate, so P1's routing bit persists across P2's segment,
  cycle 2 starts at $04). Merge shares one shadow17 → lost. FIX = reproduce the
  separate accumulators: SAVE the outgoing segment's shadow17 before its
  switch-init, RESTORE the incoming's after (medcarry[] seeded from medrout[] so
  a first entry is a no-op — P2's routing prime is $02). Self-consistent, no
  measured constant. Same family as d417_shadow/idle_wave/record_offset but
  per-SEGMENT + runtime-preserved.
- FULL ENTRY: [`ledger/C31.md`](ledger/C31.md) — read it before applying.

### C35 — one FILE, more than one COMPOSER (`origin_engine`)
- PRESENTS: an original packs players from DIFFERENT engine families behind a
  per-subtune dispatch wrapper. Each subtune verifies on its own, but the file
  cannot be STORED as one `.usf` — nothing says which composer builds which
  subtune (today that dispatch is caller-side and invisible).
- CANONICAL: `MusicSubtune.origin_engine`, permitted EXACTLY when a file
  demonstrably requires more than one COMPOSER. A Move-1 scaffold declared in
  the principle §8 and enforced by `validate.py` (all-or-nothing + >=2 distinct
  values, so a file whose subtunes agree is refused).
- ⚠ THE TEST IS "MORE THAN ONE COMPOSER", NOT "MORE THAN ONE ENGINE": 5 Title
  Tunes packs FIVE independent Hubbard '85 sub-engines and needs no tag — one
  composer serves them via per-subtune params, and the unified build is 38% the
  size of the compound one. Same-family plurality is a parameterization problem;
  try that first.
- File/subtune level ONLY. It is deleted BY Move 1 (the condition becomes false
  for every file); a per-instrument engine `kind` is NOT — Move 1 unifies
  composers, not representations — and would be permanent §7 damage.
- FULL ENTRY: [`ledger/C35.md`](ledger/C35.md) — read it before applying.

### C34 — a packed-stream byte whose meaning depends on the DECODER'S POSITION
- PRESENTS: you decode an engine's command stream from its per-byte dispatch
  map, but a COMMAND HANDLER consumes the following byte ITSELF and dispatches
  it by its own coarser rules — skipping both the top-level sub-splits and the
  end-of-pattern test. The same byte means different things at different
  positions (MA: after a preset select, `$A0+` is a REST not a HOLD, and `$FF`
  is a rest not a terminator; DMC track layer: after a transpose command,
  `$FF` is a SECTOR NUMBER for one row — then re-dispatched as the loop,
  which inherits the consumed bytes as the target sector's start position —
  presenting as a ~95%-in wrap divergence, r100 Dance).
- ⚠ THE WRITE-STREAM VERDICT IS BLIND TO IT: re-emitting the mis-decoded event
  yields a byte the player reinterprets identically, so the member verifies
  FULL forever while the USF carries wrong musical content (a `tie` where the
  music rests). Find it by READING the handler, not by waiting for a failure.
- CANONICAL: give the decoder the position state the player has (a "previous
  command consumed me" flag + per-handler dispatch transcribed from the
  handler's real branches) — in EVERY walk that mirrors the dispatch (the C29
  gate walks included; 3rd occ). Behaviour-preserving, so it is safe to land
  alone.
- ONE-ROW LAW, GENERAL FORM (4th occ, Memomania FULL): the engine re-reads
  track[pos] on EVERY duration expiry (only $7F advances pos; sectpos
  persists). A post-transpose byte $80-$FD plays ONE row of its (garbage)
  sector then MUTATES into a TRANSPOSE on the next fetch ($FE/$FF = the
  earlier stop/loop forms). One-row mechanics: consumed bytes ACCUMULATE in
  the persistent sectpos (`pending_off`), and the post-row $7F peek can
  advance the track immediately. The accumulated sectpos is observable
  (off-table hi @ idx 130-132) → `runon` row flag + composer sectpos-shadow
  per-entry base threading.
- TELL: a handler that does `INY / LDA (ptr),Y` before returning to the loop,
  whose compare chain is SHORTER than the top-level map's.
- FULL ENTRY: [`ledger/C34.md`](ledger/C34.md) — read it before applying.

### C37 — subtune SAVE-STATE RESUME wrapper (one song, N entry states)
- PRESENTS: header claims N subtunes, tune table has ONE real record; the
  non-start subtune diverges at play position 0 (state_match=False) — its
  first row plays a DIFFERENT note/instrument than the walk decoded. The
  init vector is an APPENDED wrapper: SMC copy loop pastes a per-subtune
  engine-state snapshot (+ song-DATA pokes) into the player, then forces
  `LDA #0` into the real init. Memwatch giveaway: every subtune loads the
  SAME tune-record track pointers.
- CANONICAL: py65-diff POST-INIT memory per subtune vs the start song's;
  keep only the init-wipe SURVIVORS (the copy runs BEFORE the wipe — the
  rest is dead cargo, never represent it). Sticky curnote/cache survivors →
  existing per-subtune `init.voice_state` priming; data pokes → extract
  that subtune's songs from ITS OWN post-init memory view. Distinct from
  C31 (N independent players) and C19 (static single-value poke). SECOND
  LAYER: the copy can also edit FILE-LEVEL tables (wavefreq cells /
  filter defs) — carried by C31 clone-and-remap (clone instrument + def,
  remap the subtune's rows; def clones must land in an UNUSED NIBBLE slot
  0-15, the 8-bit slot*16 base wraps past 15 — C11). A per-subtune
  wave_table-override schema was drafted and REVERTED (the
  position-locked premise was an artifact; name-on-proof held).
  NOT DMC-SPECIFIC (4th occ, FIRST NON-DMC): Hubbard '85 Human_Race in HVSC
  #85 — header 6 songs / song table 5, appended init wrapper `CMP #$05 / LDA
  #$04 / STX <per-song tick byte> / JMP <real init>` = the DEGENERATE form,
  ONE data poke and no state snapshot, so subtune 6 is song 5 one tick slower.
  A single poked table byte is the same problem as a whole pasted state block:
  the file-image byte is STALE for the subtune that plays it. Land as an
  observed subtune→(song, knob) map + identity-defaulting extract args (every
  other rip byte-identical). ⚠ MEASURE WITH SIDDUMP not py65 once the poked
  value reaches the write stream (a TEMPO does): `--pc-watch <real-init PC>
  0-2 --pc-watch-first` gives A=song and X=the poke, `--memwatch <table>` the
  table as read. ⚠ `--peek-post-init` CANNOT read a player at $A000-$BFFF —
  the idle-time port banks BASIC ROM over it and returns the SAME ROM bytes
  for every subtune (C29's trap in its ordinary form).
  DETECTION IS OBSERVATION-FIRST (3rd carrier, 2nd wrapper shape): when
  the static skeleton misses, run init(A=sub) under py65 per subtune —
  fire iff every subtune enters base with the SAME A and ≥1 non-start
  subtune's post-init RAM differs (≤256 bytes) from the start subtune's;
  the diff IS the survivor set. Survivor categories now also include the
  d417 routing SHADOW (→ subtune res_routing priming) and the GLOBAL
  vib/slide half-rate parity $1019 twin (→ subtune init.slide_phase) —
  a resumed parity shifts every vibrato-flagged voice's WAVE-STEP phase
  by one play (a mid-song wave divergence, not a position-0 one).
- 5th occ (f2 X-mas_Cooperation): the KNOB-POKE degenerate form — init
  wrapper pokes table[sub] into the f2 $FF handler's loop-to IMMEDIATE =
  per-subtune loop_reset_pos, extract-only, identity-defaulting.
- FULL ENTRY: [`ledger/C37.md`](ledger/C37.md) — read it before applying.

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
  it (the C20 relative at the extract layer). GRAMMAR TRAP (2nd occ): a typed
  field whose name exists as a wild params{} key must use the generic
  CNAME-key + transformer-validation pattern — a keyword terminal shadows
  CNAME corpus-wide and breaks every old-form stored file (corpus_check
  catches it; run it BEFORE trusting any other gate).
- FULL ENTRY: [`ledger/C33.md`](ledger/C33.md) — read it before applying.

### C36 — a PC-triggered bus tap false-fires on DATA reads of the trigger address
- PRESENTS: an observation hook fires when "the CPU reaches PC X" by watching
  cpuRead — but code and data share the bus, so a table walk / off-table read
  touching X as DATA fires it early, and the capture reports a coherent-looking
  WRONG snapshot (For_Party: wedge $10DD read as data at frame 200, ~9600
  frames before it executes; WARM off by 79/2048 bytes). The play-vector
  counter's bare check is safe ONLY because a play vector is never read as
  data — that does not generalize.
- CANONICAL: discriminate EXECUTION by the 6502 bus signature — ≥3 consecutive
  ascending reads (opcode @PC, operand @PC+1, fetch @PC+2); no data pattern
  produces that run. Validate any new tap by CROSS-EMULATOR byte-identity of
  the captured state (also subsumes the non-perturbation gate). NB
  `writelog_capture` frame indices are COMPACTED (writes-only frames) vs raw
  siddump frames — localize with same-process captures.
- FULL ENTRY: [`ledger/C36.md`](ledger/C36.md) — read it before applying.

### C38 — song-end master-vol FADE → silence → whole-song RESTART loop (appended play wrapper)
- PRESENTS: a member verifies FULL through the whole first play + fade ramp +
  silence, then diverges DEEP (~98%) in a REPLAY. An appended PLAY-vector
  wrapper counts play() to N, `dec`s the master-vol shadow by 1 every STEP plays
  (riding the note-init `ora mvol / sta $D418` filter-tail write — the wrapper
  writes no $D418 during the fade), holds `$D418=$00` for SIL plays, then JMPs a
  re-init to loop the WHOLE song. The restart re-runs the SHARED init (clears
  $1718-$179D, LEAVES the note-state block $100F-$1018) so the replay resumes
  from the end-of-song survivor note-state.
- CANONICAL: static-gate detect (fade `DEC ctr / LDA ctr / STA mvol_shadow` +
  `LDA #$00 / STA $D418`, relocation-aware). MEASURE the schedule + survivors
  from libsidplayfp, NEVER py65 (they feed the write stream — [[feedback_ground_truth]]
  third mode): `--pc-watch` the fade STA → N (first hit's play index) + STEP
  (delta); writelog longest `$D418=$00` run → SIL; `--memwatch-on-write d418
  <$100F-$1018>` mode over the silence snapshots → note-state. Compose a MODULAR
  play-vector wrapper (count → `dec mvol` ramp → `$D418=$00` silence →
  `songrestart` = reset counters + `jsr init` + prime); keep the fade counters
  OUTSIDE the cleared state block so `init` can't wipe the play counter.
- ⚠ PRIME EXACTLY the init-uncleared survivors ($100F-$1018 = gatemask/curnote/
  curinst=$1015/shadow17) and NOTHING more. NOT `cinst` (the composer's mirror
  of the orig's ACTIVE pulse-record offset $174D, which lives in the
  $1718-$179D block init CLEARS to 0): a voice whose first REPLAYED note is SOFT
  (a glide — running-effects path, never note-inits, never copies curinst→cinst)
  then runs fx_pulse against the survivor instrument instead of instrument 0,
  sweeping PW where the orig (cinst-offset 0) holds it flat (TELL: PW-lo
  alternating across a glide note whose freq trajectory matches perfectly).
  GENERAL: the survivor set is EXACTLY the init-uncleared range — prime only the
  leftovers, never a byte init clears.
- Fade = C10 parametric master-vol (NOT a global_track event list); restart =
  C37 sibling (survivor-preserving re-init) but a WHOLE-SONG play()-counter loop,
  not a per-subtune dispatch; distinct from C19 (static single-value poke).
- FULL ENTRY: [`ledger/C38.md`](ledger/C38.md) — read it before applying.

### C39 — a fixed-offset table read is a packer-patched OPERAND that can relocate independently
- PRESENTS: a table-driven value (DMC filter cutoff) follows the RIGHT initial
  values then diverges into a DIFFERENT CONTOUR — the rebuild advances a program
  step the orig doesn't (or vice-versa). The extraction reads table B (filter
  step DURATIONS) at a hard-coded offset from table A (filter-def records,
  durs at record+10), but the player reads B via its OWN operand, which the
  packer relocated INDEPENDENTLY (Vai/Hardtechno: fdu at op_filtdef+165, all
  zeros → filter steps never advance, +$60/frame forever).
- TELL: ground-truth `siddump --memwatch-on-write <reg> <step-caches>` shows a
  size/duration cache that does NOT match the decoded record byte ($1722 fdu=$00
  vs record+10 byte $02). Right start + wrong contour = wrong table BASE, not a
  wrong index.
- CANONICAL: resolve B's address from the PLAY body operand (gated on the canon
  opcode; fallback to the assumed offset = byte-identical). Census the corpus for
  members where B is not at A+offset — that set is the fix's whole exposure
  (filter durs: exactly 2, both Vai). No FULL member regresses (a filter-using
  FULL had durs at +10 already; the operand read is ground truth). Distinct from
  C2 (index off the table END; here the base moved).
- FULL ENTRY: [`ledger/C39.md`](ledger/C39.md) — read it before applying.
