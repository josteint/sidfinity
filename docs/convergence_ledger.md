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
| accumulated per-step rounding drift in a round-trip · USF stores DELTAS (durations), player sums them to ABSOLUTE positions · a min/floor on each delta drifts over a long song · short tunes pass, long tunes length_fail · keep deltas EXACT (allow 0) | C12 | logged |
| engine variant dispatch · player jump-table init offset shifted but play body at canonical offset · "no_jumptable"/code-mismatch reject · dispatch on the PLAY-body signature not init (we emit our own init) | C13 | logged |
| command-per-row tracker effect (note + fx + param per row) · porta/vibrato/arp/filter/tempo on a row · NOT per-instrument · how to represent in NoteRow | C14 | recurring (FC + GoatTracker V1) |
| INAUDIBLE writes · idle/gate-off voice freewheels · "audio-equivalence" verdict relaxation | C15 | ⛔ REMOVED (user decision 2026-07-01): every SID gets STRICT write-stream match, always — never propose relaxing the verdict during per-engine work. If an idle-freewheel divergence blocks a member, REPRODUCE the writes (core tenet permits reproducing the mechanism). Design parked in `refactor_1_remaining.md` as a Move-1-era-ONLY consideration. |
| per-frame WRITE-ORDER differs · orig batches note-on writes (SR/AD/CTRL) separately from wave-step writes (freq/PW/CTRL) or uses a different voice interleave · rebuild emits a different order · NOT a wholesale composer rewrite — PARAMETRIZE the composer's EMISSION order (precedent: FC `nextvoice_write_order`) | C16 | logged |
| HETEROGENEOUS per-step write shapes in a trace-lift · one superset order can't embed all steps (conflicting reg orders / intra-step dups / sections) · cluster steps by EXACT write shape → K positional templates + per-step template id | C17 | logged |
| play-vector WRAPPER with per-call PHASE behaviour · slow-tempo / multispeed-effects cycler · every Nth call runs the full play, others run effects-only / register-refresh / nothing · wrapper shapes vary (SMC, DEC+dual-JMP, parity AND) — OBSERVE entry-point reachability under py65, don't parse | C18 | logged |
| TRICHOTOMY VERDICT alignment · rebuild emits its OWN init (universal reset+priming) so streams differ by an init prefix · Check A end-of-init state + aligned play-stream compare · TWO implementations exist: `verify_cycle._trichotomy_compare` (FC, shift recovery) + `usf_roundtrip._compare_music/_split_aligned` (basic_program, known-init-length + probe search) — CONSULT MISS, factor at Move 1 | C21 | factor-candidate (2×) |
| hand-patched player WEDGE inside the canon body · SMC opcode toggle · 1-byte opcode patch · JMP over canonical loads · runtime state ≠ static file byte · STATIC opcode probe, never a bounded stream scan · census carriers both sides · reproduce semantics behind a factory-probed param | C19 | canonicalized (2×) |
| stale-FULL palimpsest · recorded 'full' the current code can't reproduce · hides members from residue censuses · verify the STORED build first, then USF-diff/param-bisect to attribute · never mass-write with code that didn't produce the verdict | C20 | canonicalized |
| AMBIGUOUS round-trip flag encoding · two distinct engine ops render to OVERLAPPING USF flag sets · the decoder's branch test uses a SUBSET of the discriminator → misroutes one op onto the other's path · matches for most content (paths coincide when inputs coincide), diverges on the distinguishing case | C22 | canonicalized (2×) |
| a play-phase/schedule TOKEN hides a per-member behavioural ambiguity · same P_F123 token = note-init-on-F vs deferred 2-frame arm · fixing one class REGRESSES same-token FULLs · NOT derivable from the token/multispeed → OBSERVE the distinguishing write-footprint per member · regression-safe when the "changed" verdict has no false positive | C23 | logged |
| play-body UNIT-repeat · play body runs ONE of its 4 units (v0/v1/v2/filter-tail) N× per play() (JSR-to-N-call stub; JMP-tail form re-runs the filter tail) · "double-speed voice" · unified play_unit_repeat=[v0,v1,v2,filter] list · distinct from play_repeat (whole play()) + C18 play_phases (whole calls) · static byte-probe (C19 method) | C24 | recurring |

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
- **Status:** logged (DMC v4 CIA multispeed rate, 2026-06-25).
- **Boundary:** works when the parameter is OBSERVABLE in the write timing /
  memory. CIA multispeed rate: count play()s per PAL frame from
  `--writelog-per-irq --per-irq-debug` (`nentries`/frame, `base`=abs PHI1
  clock), round N to the integer factor, latch = 19656/N − 1 (the exact
  canonical $2663=2x / $1331=4x). The rounding makes it robust (N within 0.01).
- **Consumers:** DMC v4 `factory._cia_period_from_writelog` (commit 2114f21 —
  67 py65-unreadable cia_multispeed members → 56 build, +20 FULL).

### C10 — Chip-global ($D415-$D418) automation that varies during a song (master vol + filter)
- **The DOF:** master volume + filter cutoff/res/mode/route — chip-GLOBAL state
  (one per SID, not per voice), changing across the song. Distinct from C1, which
  is the *per-instrument* swept contour; this is the *whole-subtune* global track.
- **Canonical — choose by MUSICAL STRUCTURE, not by engine:**
  - **PARAMETRIC** (mechanism + a few knobs; the engine GENERATES the per-frame
    values) when a formula/table drives it: `MasterVolConfig` (fade formula, e.g.
    Confuzion `clamp(BASE − voice1_orderpos)`), `master_vol_every_frame`/`_every_note`
    (re-assert a fixed value), `FilterProgConfig`/`filter_programs` + DMC
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
  `filter_env` (DMC v5). See C1 (per-instrument sweep) and C7 (opaque-dump lens).

### C11 — Engine indexes a table via an 8-bit register → the offset WRAPS mod 256
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
- **Boundary / watch-list:** the SAME class applies to ANY 8-bit-indexed engine
  table — e.g. the DMC wave POSITION ($177A is 8-bit, so a wave program crossing
  $FF wraps to wctab[0]; `_slice_wave` reads linearly past it — a candidate
  unfixed instance). Audit other `mem[base + i*stride]` extracts for the same.
- **HARD BOUNDARY — off-table reads that sonify the ABSOLUTE wave position
  (2026-06-28, Object_of_Art).** When a wave program's arp index runs off-table
  and lands on `$177A` (wavepos itself), the orig plays the absolute wave
  POSITION as a frequency. This is NOT addable to the C6 off-table redirect map:
  our composer RE-PACKS the wave pool with its own offsets (`iwst` in
  composer_asm — idle-program-first + dedup + instrument-order), so our wavepos
  diverges from the orig's (Object_of_Art V2/V3 = orig+5). The off-table read can
  only match if the composer reproduces the orig packer's wave-pool layout
  BYTE-FOR-BYTE (offsets + sharing) — the encoding-specific-layout class (sibling
  of sectorpos). Object_of_Art: first-div LO byte = `fcut` ($171C, derivable,
  cleanly mappable) but HI byte = wavepos (blocked). Mapping wavepos+fcut was
  net-NEGATIVE: 0 recoveries (wavepos wrong) + 1 FULL regression.
- **Redirect-map consumer — durrel (2026-07-03, +26 FULL f1, 0 attributable
  regressions):** $173E duration-reload mapped as a live shadow; works because
  every composer EVENT's stored duration == the orig's reload at that row BY
  CONSTRUCTION (each orig row reloads its counter from $173E, so row duration
  ≡ current reload). Priming from the file-image/post-init leftover, emitted
  only for window-reading members. SCHEMA HOME: the pre-first-event leftover
  is §4.5 engine-state PRIMING (trichotomy report) — a TYPED
  `InitVoice.dur_reload` field alongside `guard`, NOT a params scalar (the
  first landing used `durrel_init*` params citing the hr_test_init precedent;
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
- **Status:** logged (DMC family-1, 2026-07-02: P/F/S round +5 FULL, R round
  +26 FULL → 4198/5401; 2026-07-04 straddle-free pc-trace observer, +0 FULL but
  fixes the `P_S` mis-observation).
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
  e.g. `hr_patch`: PW step base never loaded + phase/dir persist + the
  hard-restart TEST write gated by a global flag toggled per note-init from
  the instrument's $04 flag (the orig toggles the STA/LDA opcode at $17FB;
  the composer keeps an explicit `hrtest` byte primed from the file-image
  opcode). Reproduce state-machine EFFECTS, never the SMC mechanism.
- **Trap:** the file-image state of the toggled byte differs per member (save
  moment) — it is PRIMING, so capture it as a param (`hr_test_init`), don't
  assume a constant.
- **Diagnosis tell:** runtime state ≠ file-image table byte while taint_source
  says the byte is STATIC ⇒ the READ SITE differs from canon — dump the
  operand/opcode at the canon site.
- **Status:** CANONICALIZED (2 occurrences, DMC family-1 rounds 13 + 19,
  2026-07-03). Canonical form: STATIC opcode probe (read the patched
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
- **Consumers:** DMC v4 `factory._hr_patch_probe` + composer_asm
  hr_patch/hr_test_init gating; `factory._hold_gateoff_probe` →
  `hold_gateoff` param. Sibling of C18 (wrapper OUTSIDE the player) —
  C19 is patches INSIDE the canon body. The round-14 $D418 play-vector prefix
  (`LDA #imm/STA $D418/JMP base+3`, factory `_d418_play_wrapper` →
  `d418_every_play`, +6 FULL, commit efbf639) is the degenerate stateless
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
  DEEP heterogeneous divergence (Gangstallica @28k: rebuild held the old base
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
  (Grave_Story_intro, div @6427 → FULL 130165/130165). TELL: deep freq-LO
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
- **Consumers:** DMC v4 `factory._detect_notestart_arm` → `notestart_arm` param
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
