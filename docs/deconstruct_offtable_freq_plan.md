> **SUPERSEDED (2026-06-20) by `docs/offtable_freq_plan.md`** (via the interim
> `offtable_statebuf_plan.md`). This draft predates the round-12/13/14 findings and
> the ML-optimality deciding criterion. The final plan represents off-table reads
> as an explicit per-step **frequency** (ML-musical), not a parametric "effect"
> reinvention and not the `StateLayoutMirror` the interim plan proposed. History.

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

## The design THESIS (corrected 2026-06-18 — the off-table read is NOT pitch)

**A first thesis ("extend the tuning to its true length") was WRONG and is
rejected.** Investigation of a real case (Elysium inst8/9) showed the off-table
read is *not a pitch* and the region is *not a tuning*:

- inst8/9 is a **percussion/drum**: 2 TEST-bit frames (oscillator-reset = click
  attack) + a sawtooth "sustain" step whose `+64` wave offset pushes the index
  off-table.
- The off-table "frequency" is assembled from **two unrelated tables read as
  lo/hi**: `freq_lo[124] = freq_hi[28]` (the freq-HI table read as the lo byte)
  and `freq_hi[124]` = 28 bytes past the freq-hi table = the wave/pulse region.
  Result: an irregular sub-bass/near-silent body — the drum's body, not a pitch.
- So the bytes are **largely data the USF ALREADY carries** (the freq-hi table;
  the wave/pulse region). `freq_overrun` partly *duplicates* existing USF content.

**Corrected thesis.** An off-table read is the engine reading *adjacent musical
tables / its state region* as a frequency, to realize a musical **EFFECT** (here,
a percussion body; other cases may be out-of-range overtones, sweeps, textures —
the census determines the set). The musical intent is the **effect**, never the
bytes. Per the CORE TENET we owe the original nothing but its write stream:

1. **Deconstruct the EFFECT** each off-table case produces (wave-step waveform /
   TEST-bit / freq behaviour + the resulting `$D400/$D401` contour + note-dep).
2. **Represent that effect parametrically** in the USF (drum/percussion program,
   absolute-freq body, a wave-step's real freq behaviour — by effect type).
3. **Reproduce the identical write-log with our OWN composer**, by any means —
   the values are often derivable from tables the USF already holds. Be creative;
   there is always logic to the madness (unless Frank Zappa wrote the SID).

**Never** extend-the-tuning, **never** keep-blob, **never** exclude — those
preserve mechanism or duck the work. We find the logic and re-implement it.

**CORE-TENET alignment.** The original read works only by engine-positional
luck (the table it lands in sits right after the freq table). We invent our own
layout/engine and emit whatever reproduces the write stream — we owe the original
table nothing.

**Trichotomy alignment.** Where the landed bytes are the engine's state region,
their *engine-state init* role → `init.sid`/`state_layout`; their role *as the
effect's freq source* → the effect's parametric representation. One value, two
roles, decoupled — no shared opaque memory.

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

## Phase 1 — Deconstruct the LOGIC / identify the effect (census by EFFECT TYPE)

Not "classify tuning-coherence" (the old, wrong axis). For every off-table case,
find the MUSICAL EFFECT it produces and bucket by effect type.

- [ ] Build `tools/offtable_effect_census.py`: per off-table-using instrument,
      capture (a) the wave-program steps (waveform / TEST-bit / melodic-vs-abs /
      loop), (b) the actual `$D400/$D401` freq contour the off-table step(s)
      produce (writelog), (c) note-dependence (does the contour change with the
      played note?), (d) WHAT the off-table index lands in (freq-hi table?
      wave/pulse region? state region? — via the address arithmetic).
- [ ] Bucket by **effect type**, e.g.: *percussion/drum body* (TEST-bit attack +
      sub-bass/near-silent off-table sustain — the Elysium pattern); *out-of-range
      overtone* (offset intended as a high harmonic, clamped/wrapped by the
      table edge); *borrowed-table-as-freq* (lands in another musical table whose
      bytes the USF already carries); *texture/noise*; *other (find the logic)*.
- [ ] For each bucket: is the produced freq DERIVABLE from data the USF already
      holds (freq-hi table, wave/pulse tables)? If yes, no new content is needed —
      only a composer strategy. Record the derivation.
- [ ] Census the four instances (FC `freq_overrun`, DMC-v5 `freq_overrun`,
      Hubbard SFX `extended_freq`, Hubbard 320-tail): per-effect-type member
      counts + representatives. There is always logic; if a case truly has none,
      flag it explicitly (do NOT default to keep-blob/exclude).

## Phase 2 — Represent each effect parametrically (be creative)

- [ ] Per effect type, design the musical USF representation (e.g. *percussion*
      → a drum/percussion instrument with TEST-bit attack + an absolute-freq
      body; *out-of-range overtone* → the wave step's intended offset + a clamped
      freq the composer emits; *borrowed-table* → reference the existing USF
      table, composer derives the value from it). The model must learn the
      EFFECT, not bytes-at-offset.
- [ ] Define the composer strategy to reproduce the write-log for each: prefer
      DERIVING the off-table value from existing USF tables (no duplication) over
      emitting it; if a small explicit value is unavoidable, it must be typed as
      the effect's parameter (e.g. "drum body freq"), never a raw `freq_overrun`.
- [ ] **Decouple double-duty (trichotomy):** state-region landings → split the
      engine-state-init role (`init.sid`/`state_layout`) from the effect-freq role.
- [ ] **Eliminate the blob fields:** plan removal of `freq_overrun` +
      `SfxSubtune.extended_freq` + the "320/128 state tail" framing once every
      effect type has a parametric home.
- [ ] **Cross-engine check:** confirm the effect taxonomy + representations span
      all four instances (one set of musical primitives, §9.4).

## Phase 3 — Schema implementation (the usf_sync discipline — all together)

- [ ] `src/usf/types.py`: extend `freq_table` semantics; remove/deprecate
      `freq_overrun` + `SfxSubtune.extended_freq` (+ the "320/128 state tail"
      comment → "tuning of true length").
- [ ] `src/usf/grammar.lark` + `parser.py` + `writer.py`: freq_table block
      length-flexible; drop the `freq_overrun` / `extended_freq` blocks.
- [ ] `docs/usf_format.md`: update the freq_table spec.
- [ ] Tests: round-trip a long freq_table; assert no freq_overrun field.
- [ ] (feedback_usf_sync: spec + all converters + player + tests in one change.)

## Phase 4 — Per-engine migration (per identified effect; write-log-gated, one commit each)

Each instance migrates by REPLACING its blob with the Phase-2 parametric effect
representation + composer strategy (derive-from-existing-USF where possible).

- [ ] **DMC v5** — replace `_freq_overrun` with the effect representations its
      census found (e.g. percussion-body absolute-freq + derive-from-tables for
      borrowed-table cases). Verify the +44 stay FULL; no `freq_overrun` emitted.
- [ ] **FC standard** — replace `_std_freq_overrun` per its census effect types;
      reuse its reachability logic only to bound derivation. Verify wide-batch
      pass-rate unchanged.
- [ ] **Hubbard SFX** — `extended_freq` → the SFX effect's parametric form.
      Verify Commando/Monty SFX subtunes FULL.
- [ ] **Hubbard 320-tail engines** — the arp-extension effect represented
      parametrically; decouple the work-RAM/state role (`state_layout`/`init`).
      Verify those engines FULL.

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

- *(O1/O2 from the first draft are DEAD: O1 assumed an extended tuning — it isn't
  one; O2 proposed keep-blob/exclude — rejected. The real open question is the
  effect TAXONOMY, resolved by the Phase-1 census.)*
- **Q1 — effect taxonomy unknown until the census.** Phase 1 must enumerate the
  effect types (percussion-body, out-of-range overtone, borrowed-table, …) and
  confirm each has a clean parametric home. A genuinely-no-logic case (if any) is
  flagged explicitly, not blob'd/excluded.
- **Q2 — note-dependence per effect.** A note-dependent off-table contour can't
  be one absolute value; the representation must capture it as the effect's
  parameter (or derive it). Census measures note-dependence per instrument.
- **R1 (scope):** four families + a shared-schema change = multi-session. Land
  per-instance, write-log-gated, one commit each; DMC v5 first (smallest,
  freshest, also closes its C3 gap).
- **R2 (regression surface):** removing the blob fields touches `src/usf/`
  (shared) → full `tools/regression.py` before every commit.
- **R3 (derive, don't duplicate):** prefer composer derivation of the off-table
  value from tables the USF already holds (freq-hi, wave/pulse) over emitting any
  explicit value — the blob is partly redundant with existing USF content.

## Sequencing (recommended)

Phase 0 → 1 (census, the go/no-go on Case-3 ceiling) → 2 (confirm O1/O2 with
human) → 3 (schema) → 4 DMC v5 → 4 FC → 4 Hubbard SFX → 4 Hubbard tail → 5/6.
Each Phase-4 instance is independently shippable and write-log-gated.
