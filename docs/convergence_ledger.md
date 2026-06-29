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
| de-fused per-entity pool exceeds byte-index capacity · "pool overflow" · separate copies per instrument | C8 | logged |
| runtime param unreadable by py65 (init hangs / IRQ-set / bad opcode) · measure from libsidplayfp writelog | C9 | logged |
| chip-global $D415-$D418 automation during a song · master vol / filter varies · global_track vs MasterVolConfig/filter_programs · explicit-event vs parametric | C10 | logged |
| engine reads a table via an 8-bit index register (`base,Y` w/ Y=#*stride) · orig "reads garbage"/looks broken · extractor must wrap `(#*stride)&0xFF` · suspect OUR extractor not the packer | C11 | logged |
| accumulated per-step rounding drift in a round-trip · USF stores DELTAS (durations), player sums them to ABSOLUTE positions · a min/floor on each delta drifts over a long song · short tunes pass, long tunes length_fail · keep deltas EXACT (allow 0) | C12 | logged |
| engine variant dispatch · player jump-table init offset shifted but play body at canonical offset · "no_jumptable"/code-mismatch reject · dispatch on the PLAY-body signature not init (we emit our own init) | C13 | logged |
| command-per-row tracker effect (note + fx + param per row) · porta/vibrato/arp/filter/tempo on a row · NOT per-instrument · how to represent in NoteRow | C14 | recurring (FC + GoatTracker V1) |

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

### C8 — A de-fused per-entity program pool overflows the engine's byte index
- **Canonical:** the engine stores N programs in one table indexed by a single
  byte (position ≤ 255); the composer emits a SEPARATE copy per entity, so a
  member with many same-shape entities inflates the pool past 255 → hard build
  error. **Dedup identical programs** (key on the exact emitted bytes + loop):
  identical entities point at one pooled copy. Byte-identical for the write
  stream — each entity re-inits its position to its start per use and reads the
  same byte sequence. This is what the original packer does (programs share).
- **Status:** logged (DMC v4 wave pool, 2026-06-25).
- **Boundary:** dedup is pure packing (zero write-stream change) and recovers
  exact-duplicate programs only. SUFFIX/substring overlap (a program that is a
  tail of another) is the next packing tier — needed for the residue that
  exceeds 255 even after dedup (DMC: Marek_Bilinski_1 / Riders / Abject_17, all
  all-unique programs). Not yet built.
- **Consumers:** DMC v4 `composer_asm.py` wave pool (`add_prog` dedup cache,
  commit c73a1d0 — 40 overflow members → 37 build, +5 FULL).

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
- **TELL / how it presents:** the orig appears to read "out-of-range / garbage"
  data and the SID seems "broken" — but a real packer does NOT emit broken SIDs.
  When a trace shows an out-of-range/garbage read, SUSPECT THE EXTRACTOR (8-bit
  wrap / wrong base / wrong stride) FIRST, not the data. (DMC user-caught,
  2026-06-27.) Sibling of [[feedback_6502_mindset]]: all bugs are pointer errors;
  think in exact byte offsets — including index-register width.
- **Status:** logged (DMC v4 instrument record offset `#*11 & 0xFF`, commit
  3cae4fd; instr >= 24 → ~6% of partials recovered, 0 regression).
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
- **METHODOLOGY — the C6 off-table redirect map is NOT free; measure regressions.**
  Adding a `(addr, var, n)` entry can REGRESS a FULL whose off-table read happened
  to match via the STATIC freq-table overrun byte (the value the read got before
  the redirect). Always run a FULL-songlength transfer test (partials for
  recovery + a FULL sample for regression) before committing a new map entry;
  otrk/wnote were lucky on small samples. Reading $171C/$177A regressed
  Humppa_Demo (1/33 FULLs).
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
- **Consumers:** DMC v4 `_decode_instrument` (commit 3cae4fd).


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
  GoatTracker V1 (planned, RE_NOTES §7).

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
