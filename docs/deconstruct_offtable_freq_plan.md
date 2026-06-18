# Plan — deconstruct the off-table-freq opaque-blob anti-pattern to musical form

**Goal (option (a) from the C7 analysis):** eliminate every Class-B opaque
content-by-reference blob that carries *musical-intent frequency data* —
`freq_overrun` (FC standard + DMC v5), `SfxSubtune.extended_freq` (Hubbard SFX),
and the 320-byte `freq_table` "state/scratch tail" (Hubbard notenum-overlap
engines) — by representing the data as **first-principles musical content** in
the USF, so an ML model learns *frequencies/pitches*, never *bytes-at-an-offset*.

This is the anti-pattern the project has fought since inception (late March):
original bytes carrying musical intent that sit opaquely in / leapfrog the USF.
See convergence-ledger **C7** + **C6**, `docs/usf_representation_principle.md`,
the CORE TENET (CLAUDE.md), and the init trichotomy (`docs/sid_init_report.md`).

---

## The design THESIS (what "musical" means here, and why it's correct)

An off-table read is `freq_table[offset + note]` with the index past 96. Three
facts pin the right representation:

1. **The value read IS a frequency the voice plays** → musical output we must
   reproduce (CORE TENET: the `$D400/$D401` write stream is the target).
2. **It is note-dependent** (same wave step, different notes → different indices
   → different freqs) → it is intrinsically *a table indexed by pitch*, not a
   per-step constant.
3. **The bytes are STATIC at read time** (content-by-reference reproduces the
   full-songlength write-log; verified directly on Elysium: the off-table region
   is one distinct value-tuple over 12 s). → they behave as **fixed tuning
   entries for pitch indices > 95**, not live engine state.

**Therefore the musical form is: the freq table (the tuning) is simply LONGER
than 96 entries.** The "overrun" is *the tuning at its true reachable length*;
wave/arp steps index it **uniformly** (in-table and beyond are the same lookup).
The "off-table" concept — and the blob — **dissolves**. The model sees a tuning
table + pitch indexing, both already first-class musical, with nothing special
to learn (the §7 test: "must the model learn each value from scratch?" → no; it
learns "pitch i has frequency F_i," uniform with the chromatic 96).

**CORE-TENET alignment.** The original read only works because the engine's
state region sits contiguously after the freq table (an *engine-positional*
artifact). We emit our OWN explicit extended freq_table and relocate work RAM
elsewhere — killing the positional dependency while preserving the write stream.
We are free to invent the layout; only the writes must match.

**Trichotomy alignment.** Where the off-table region double-duties as the
engine's state region, the *same bytes* have two roles. We DECOUPLE them: the
*tuning* role → `freq_table` (musical content); the *engine-state init* role →
`init.sid` priming / `state_layout` (the trichotomy's priming/leftover). Two
representations of one value's two roles, no longer the same memory.

**Honesty caveat (open question O1).** For Case-2 entries (state-derived, not a
chromatic continuation) the tail is "unusual frequencies." They are still the
frequencies the voice plays (musical), so a single `freq_table` of true length
is honest-enough; a tagged chromatic/extended split is a possible refinement —
decided in Phase 2.

---

## Success criteria (the gate — all must hold per migrated instance)

- [ ] **G1 — write-log preserved** (CORE TENET): rebuilt SID's `$D400-$D418`
      stream matches the original over full songlength (regression FULL).
- [ ] **G2 — no opaque blob** (§7): no `bytes`-typed / content-by-reference freq
      field remains (`freq_overrun`, `extended_freq` gone); the leak scan is clean.
- [ ] **G3 — parametric/musical** (§4): off-table steps index the tuning
      uniformly; the model sees frequencies/pitches, not bytes-at-offset.
- [ ] **G4 — reversible** (§9): extract↔USF round-trips the freq_table region.
- [ ] **G5 — cross-engine reuse** (§9.4): ONE form (true-length `freq_table` +
      uniform indexing) serves FC, DMC v5, Hubbard SFX, and the Hubbard tail.
- [ ] **G6 — trichotomy audio-equiv**: canaries pass `compare_instruction_stream
      (mode='trichotomy')` (init-state + play-stream), since our layout differs
      from the original's (not byte-identity).

---

## Phase 0 — Re-anchor (do FIRST, every session that touches this)

- [ ] Re-read `docs/usf_representation_principle.md` §4/§7/§8/§9 IN FULL.
- [ ] Re-read the CORE TENET (CLAUDE.md) + `docs/sid_init_report.md` (trichotomy).
- [ ] Re-read convergence-ledger C6 + C7; consult before any schema change.
- [ ] Confirm the THESIS above still holds against the principles (adversarial
      check, not justification — [[feedback_reanchor_at_decisions]]).

## Phase 1 — Diagnose (measure, do NOT assume)

- [ ] Build `tools/offtable_freq_census.py`: per Class-B instance + member,
      classify the off-table region as
      **Case 1** (coherent chromatic-ish continuation),
      **Case 2** (static state-derived freqs — Elysium), or
      **Case 3** (DYNAMIC — engine writes the read offsets before they're read;
      content-by-reference would FAIL → un-deconstructable).
- [ ] Static-vs-dynamic test per member: memwatch the off-table-read offsets per
      play() — 1 distinct tuple ⇒ static (deconstructable); >1 ⇒ Case 3.
- [ ] Census the four instances (FC `freq_overrun`, DMC-v5 `freq_overrun`,
      Hubbard SFX `extended_freq`, Hubbard 320-tail): member counts, Case 1/2/3
      split, **max reachable index N** (the extended-tuning length needed).
- [ ] Record the Case-3 count (the documented residue ceiling for option (a)).

## Phase 2 — Design the unified representation (decision points → confirm with human)

- [ ] **Schema shape:** `freq_table` carries its TRUE reachable length (one
      tuning, lo[N] + hi[N], N ≤ 256). REMOVE `freq_overrun` and
      `SfxSubtune.extended_freq`; reframe the Hubbard 320-tail as tuning.
- [ ] **lo/hi contiguity:** preserve the layout invariant the off-table reads
      need — `freqlo[N]` then `freqhi[N]` contiguous (the freq_overrun fix
      already lays them out this way); verify `freqlo[i>95]` reading into
      `freqhi` still resolves under the extended length.
- [ ] **Reachability:** the extension covers `[96 .. max reachable index]`
      contiguously (gaps filled with the actual static bytes — never read but
      needed for contiguous indexing); reachability-minimal beyond max.
- [ ] **Decouple double-duty (trichotomy):** tuning-value → `freq_table`;
      engine-state init value → `init.sid`/`state_layout`. Composer emits the
      explicit extended freq_table + relocates work RAM.
- [ ] **O1 — honesty refinement decision:** single `freq_table` (length N) vs a
      tagged `chromatic[96] + extended[]` split. Pick the minimal-but-honest
      form; justify against §7. **(surface to human)**
- [ ] **O2 — Case 3 policy:** dynamic-state members → keep content-by-reference
      (documented B2) OR exclude (`tools/excluded_sids.json`). **(surface)**
- [ ] **Cross-engine check:** confirm the one form serves all four instances
      (FC arp/+$04, DMC wave, Hubbard SFX sweep, Hubbard arp extension).

## Phase 3 — Schema implementation (the usf_sync discipline — all together)

- [ ] `src/usf/types.py`: extend `freq_table` semantics; remove/deprecate
      `freq_overrun` + `SfxSubtune.extended_freq` (+ the "320/128 state tail"
      comment → "tuning of true length").
- [ ] `src/usf/grammar.lark` + `parser.py` + `writer.py`: freq_table block
      length-flexible; drop the `freq_overrun` / `extended_freq` blocks.
- [ ] `docs/usf_format.md`: update the freq_table spec.
- [ ] Tests: round-trip a long freq_table; assert no freq_overrun field.
- [ ] (feedback_usf_sync: spec + all converters + player + tests in one change.)

## Phase 4 — Per-engine migration (write-log-gated, one commit each)

- [ ] **DMC v5** — extract emits extended `freq_table` (drop `_freq_overrun`);
      composer indexes uniformly (the contiguous layout already exists). Verify
      the +44 stay FULL. *(Also closes the C3 minimization gap by construction.)*
- [ ] **FC standard** — extract emits extended `freq_table` (drop
      `_std_freq_overrun`'s separate field; keep its reachability logic for the
      length). Verify the wide-batch pass-rate is unchanged.
- [ ] **Hubbard SFX** — `extended_freq` → the SFX freq lookup over the extended
      tuning. Verify Commando/Monty SFX subtunes FULL.
- [ ] **Hubbard 320-tail engines** — reframe the tail as tuning + decouple the
      work-RAM/state role into `state_layout`/`init`. Verify those engines FULL.

## Phase 5 — Verify & prove (per instance, then globally)

- [ ] G1 write-log: `tools/regression.py` FULL across every touched family.
- [ ] G6 trichotomy: canaries audio-equivalent (`mode='trichotomy'`).
- [ ] G2 leak scan: `grep` shows no `freq_overrun`/`extended_freq`/`: bytes`
      freq field remains; convergence-ledger §9.2 scan clean.
- [ ] G4 round-trip: extract↔USF for the freq_table region (pattern_stream_verify
      analog for freq).
- [ ] G3/G5 review: re-run `/uready-review` — confirm the four instances now
      share the one `freq_table` dimension (B-class candidates → 0 for freq).

## Phase 6 — Prevent recurrence

- [ ] Convergence ledger: update C6/C7 — canonical resolution is "freq table =
      tuning at TRUE reachable length + uniform indexing; never 96 + overrun."
- [ ] `/uready-review`: add the standing B-class audit (flag any new
      content-by-reference / `bytes` USF field).
- [ ] Principle note: "freq tables are the tuning at their true reachable length"
      — so the next engine never re-introduces an off-table blob.

---

## Risks & open questions

- **O1 (honesty):** single vs tagged freq_table for Case-2 tails (Phase 2).
- **O2 (Case 3):** dynamic-state members are un-deconstructable by option (a) —
  the residue ceiling; policy in Phase 2 (content-by-reference vs exclude).
- **R1 (scope):** four engine families + a shared-schema change = multi-session.
  Land per-instance, write-log-gated, one commit each; DMC v5 first (smallest,
  freshest, also closes its C3 gap).
- **R2 (regression surface):** the schema change touches `src/usf/` (shared) →
  full `tools/regression.py` before every commit, not just the touched family.
- **R3 (FC reachability):** FC's `_std_freq_overrun` already does a minimized
  reachable-window walk — reuse that logic to size the extended `freq_table`
  length, don't re-derive (convergence-ledger consult).

## Sequencing (recommended)

Phase 0 → 1 (census, the go/no-go on Case-3 ceiling) → 2 (confirm O1/O2 with
human) → 3 (schema) → 4 DMC v5 → 4 FC → 4 Hubbard SFX → 4 Hubbard tail → 5/6.
Each Phase-4 instance is independently shippable and write-log-gated.
