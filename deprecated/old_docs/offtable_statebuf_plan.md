> **SUPERSEDED (2026-06-20) by `deprecated/old_offtable_freq_plan.md`.** The deciding
> criterion became ML-training-optimality, which rules out the `StateLayoutMirror`
> mechanism this plan proposed (the model would learn engine-state-layout metadata,
> not music) in favour of representing each off-table read as an explicit
> **frequency** on its wave step. Kept for the reasoning trail (why "blessed" ≠
> optimal here). The round-12/13/14 findings carry over.

# Plan — replace the off-table-freq blob with a typed state mirror (DMC v5 → FC)

**Supersedes** `deprecated/old_deconstruct_offtable_freq_plan.md` (same goal — kill the
off-table-freq opaque blob — but that draft predates the round-12/13 findings and
the realization that the project already ships the principled mechanism). This
plan is the canonical resolution to convergence-ledger **C6** (off-table freq
lookup) + **C7** (verbatim/opaque-blob anti-pattern).

---

## Why — what we are actually dealing with (re-anchored 2026-06-20)

The off-table read is the engine computing `(wave_offset + curnote) & $FF` with
**no bounds check** and reading `freqlo/freqhi` at that index; indices > 95 fall
**past the 96-entry freq table into the engine's per-voice work RAM**, and that
byte is played as a frequency. It is engine *state read as a frequency*, not a
pitch.

Ground-truth findings driving this plan:
- **Provenance (round 12):** ~84% of off-table reads land on `trkptr` (the track
  read cursor) + position counters; ~10% per-frame counters; ~4% note-params.
- **`trkptr` is an ABSOLUTE pointer** (copied to ZP `$F8/$F9`, read `LDA ($f8),y`)
  — its bytes are a memory address = **layout-dependent**.
- **Audibility (round 13):** overshoot-as-audio is real but rare (Compotune V3
  pulse bass `$0A00`; Dead_End V2 noise drum `$FF00`) and the static counts
  over-estimate hugely; **~81% of "off-table" members never reach the read** — so
  the blob is dead padding for them.
- **DMC v5 layout:** `freqlo[96]` then `freqhi[96]` contiguous, then work RAM. So
  the off-table **lo** read lands in the `freqhi` table (already in USF — clean by
  contiguous layout); only the off-table **hi** read lands in work RAM = the part
  the blob captures.

**The blessed mechanism already exists.** `StateLayoutMirror` / `build_statebuf`
(`pipelines/composer.py`, used by Commando + the Hubbard family) is documented for
*exactly* this: "Pitch values ≥ 96 read past the freq table into engine state; the
mirror reproduces those reads cleanly by writing the same bytes into a
Python-controlled buffer at frame-load time." It **types each off-table byte**
(`var` / `const` / `note_byte` / `zp` / `var_and`) and reconstructs from *our*
engine's equivalent variables — **no verbatim bytes**. DMC v5 and FC instead use
the `freq_overrun` **blob** (raw HVSC bytes) — the C7 anti-pattern. FC blobs it
too, so it is not a model; **both families should move to the typed mirror.**

**The one honest caveat.** Commando's off-table slots are layout-INDEPENDENT
(`v_seqidx`, `v_dur`, `v_pitch` — counters/indices/notes our engine reproduces by
value), so its mirror is fully clean. DMC v5's dominant slot `trkptr` is an
ABSOLUTE address → our pointer ≠ the original's → that slot is the irreducible
**positional residue**. Two facts shrink it: ~81% never reach it, and the
reached/audible values seen (`$0A`, `$FF`) look like counters/constants, not
addresses. Phase 4 *measures* exactly how much is genuinely positional.

---

## Principles re-anchor — Phase 0 gate (re-run every session that touches this)

- [ ] **CORE TENET** (CLAUDE.md): never emit verbatim HVSC byte regions; reproduce
      the write-log with our own engine. The blob violates it; the typed mirror
      satisfies it.
- [ ] **§7 USF principle** (`docs/the_principle.md`): no opaque /
      raw-bytes / engine-positional shapes; typed slots are parametric.
- [ ] **Trichotomy §4.4** (`docs/the_trichotomy.md`): engine bookkeeping (e.g. a
      track pointer) stays OUT of musical USF; the state-reconstruction role rides
      the typed mirror, decoupled from musical content.
- [ ] **Cross-engine reuse §9.4 / Move-1**: ONE mechanism (`StateLayoutMirror`)
      spanning Hubbard + DMC v5 + FC, not a per-family blob.
- [ ] Confirm the direction is an adversarial CHECK, not a justification
      ([[feedback_reanchor_at_decisions]]). The tell of drift here would be
      shrinking the blob instead of replacing it (the rejected verify-gated hack).

---

## Success criteria (the gate — all must hold)

- [ ] **G1 — write-log preserved** (CORE TENET): no regression vs the v5 baseline
      (997 FULL @ round 10), full-songlength, gated by `tools/regression.py` +
      the v5 batch.
- [ ] **G2 — no opaque blob**: `freq_overrun` no longer emitted for DMC v5 (then
      FC); the §9.2 leak scan is clean for both.
- [ ] **G3 — typed/parametric**: every off-table-reachable byte carries a semantic
      type (`var`/`const`/`note_byte`/…), never a raw window.
- [ ] **G4 — reversible**: extract↔USF round-trips the state-layout block.
- [ ] **G5 — cross-engine reuse**: DMC v5 + FC consume the same
      `StateLayoutMirror`/`build_statebuf` as Hubbard (one form).
- [ ] **G6 — trichotomy**: any irreducible positional value is typed as
      bookkeeping (named slot), not musical content; not in the musical USF.
- [ ] **G7 — residue honest**: the genuine positional residue (reached `trkptr`)
      is measured, named, minimal, and documented in `RE_NOTES.md` + memory —
      never hidden in a blanket blob.

---

## Phase 1 — Type the DMC v5 off-table slots

- [ ] Build the canonical off-table → state-var map from `pipelines/dmc/v5/
      disassembly.s` (statebuf offset 0 = `freqhi+96`): off 0-2 `trkptr_lo`,
      3-5 `trkptr_hi`, 6-8 `trkpos`, 9-11 `secpos`, 12-14 `durctr`, 15-17 `durrel`,
      18-20 `instr`, 21-23 `transp`, … (extend per the memory map).
- [ ] Classify each slot **layout-independent** (counters/indices/notes/consts →
      `var`/`note_byte`/`const`) vs **layout-dependent** (`trkptr_lo/hi` →
      address). Record the classification in `RE_NOTES.md`.
- [ ] Confirm the DMC v5 composer already maintains numerically-matching equivalents
      for the layout-independent vars (it must, since it matches the normal-note
      write-log) — list the composer labels to read in `build_statebuf`.

## Phase 2 — Port `build_statebuf` to `composer_v5`

- [ ] Reuse the shared `StateLayoutMirror`/`StateSlot` dataclasses
      (`pipelines/engine_model.py`); factor `_emit_build_statebuf`
      (`pipelines/composer.py`) so `composer_v5` can emit it (share, don't fork).
- [ ] Emit a `statebuf` block right after `freqhi` (where the blob sat) + a
      `build_statebuf` call per play() so off-table indices resolve into it.
- [ ] Expose the per-voice/scalar var labels `build_statebuf` reads (trkpos,
      secpos, durctr, … and the per-voice constant triplets if any — cf. DMC v4's
      `sidoff`/`fbit`/`fmask`).

## Phase 3 — Extract the mirror; drop `freq_overrun` for v5

- [ ] Replace `_freq_overrun` capture with a `StateLayoutMirror` built from the
      Phase-1 map (reuse the existing reachability to bound which slots matter).
- [ ] Thread `state_layout` through `to_usf` / `from_usf` for v5 (the USF block
      already exists for Hubbard — reuse the grammar/parser/writer support).
- [ ] Stop emitting `freq_overrun` from `composer_v5._emit_data`.

## Phase 4 — Measure & characterize the positional residue (the go/no-go)

- [ ] Build + verify the stratified subset with the clean mirror (trkptr slots
      left as our-pointer). Members that stay FULL = reached only clean slots (or
      never reach). Members that regress = they reach `trkptr` (positional).
- [ ] Census the regressions: count + whether they hit `trkptr_hi` (page, mostly
      constant) vs `trkptr_lo` (advancing). **Tests the round-13 hypothesis**
      (audible/reached reads land on clean slots, not addresses).
- [ ] `trkptr_hi` (near-constant page) → type as `const` bookkeeping (the track
      page, one byte/voice — typed, named, out of musical USF). Re-verify.
- [ ] `trkptr_lo` (advancing) → the genuine residue. **Decision point (surface to
      user):** accept honest partial / capture base + model byte-advance (heavy,
      positional) / other. Do NOT silently blob.

## Phase 5 — Verify (subset → full batch), regression-gated

- [ ] Stratified subset green (no regression vs the FULL members in it).
- [ ] Full v5 batch (`tools/dmc_v5_family_batch.py`, background): FULL count ≥ 997
      baseline (clean wins offset any honest residue losses; report both).
- [ ] `tools/regression.py` clean (shared schema touched → full run before commit).
- [ ] Mass-write + `tools/build_sid_db.py` refresh; commit (no Co-Authored-By).

## Phase 6 — FC unification (the Move-1 payoff)

- [ ] Map FC's `freq_overrun` reads to their state vars (FC's reads are 8-bit
      wave-relative/+$04 — likely land mostly in tables the USF already has, so FC
      may be *cleaner* than v5: measure).
- [ ] Migrate FC to the same `StateLayoutMirror`/`build_statebuf`; drop FC's
      `freq_overrun`. Verify the FC wide-batch pass-rate holds.
- [ ] (Stretch) audit Hubbard SFX `extended_freq` + the 320-tail engines against
      the same mechanism for full §9.4 convergence.

## Phase 7 — Schema cleanup + prevent recurrence

- [ ] Once DMC v5 + FC are off it: remove the `freq_overrun` field from
      `src/usf/{types,grammar.lark,parser,writer}.py` + `docs/usf_format.md`
      (usf_sync discipline: spec + converters + player + tests in one change).
- [ ] §9.2 leak scan clean (`grep` shows no `freq_overrun` / `: bytes` freq field).
- [ ] Update convergence-ledger **C6/C7**: canonical resolution = "off-table reads
      → typed `StateLayoutMirror`, reconstruct from our state; NEVER a verbatim
      window. Irreducible positional values → typed bookkeeping slots, measured."
- [ ] `/uready-review`: standing B-class audit flags any new content-by-reference
      freq field.

---

## Risks & open questions

- **R1 — `trkptr_lo` is genuinely positional.** Its value = `(orig_base_lo +
  orig_byte_advance) & $FF`; both terms are the original's layout/encoding.
  Reproducing it cleanly needs the original's track byte-advance (positional). The
  honest fallback is partial for the members that *reach* `trkptr_lo` — Phase 4
  sizes this; it may be small (most never reach off-table; audible cases look
  clean). **Do not blob it back.**
- **R2 — var numerical match.** `build_statebuf` reads our vars; if our counter
  semantics differ from the original's (multispeed, tie, wave-advance), a slot is
  wrong → verify catches it (regression), then fix the engine's counting. Under-
  capture / mismatch cannot pass silently (next data section sits right after).
- **R3 — composer divergence.** `composer_v5` is separate from `composer.py`;
  share the emitter + dataclasses (don't fork) to keep G5 real.
- **R4 — scope.** Multi-step, cross-family. Land per-family, write-log-gated, one
  commit per verified delta. DMC v5 first (freshest, also closes its C3/blob gap).

## Sequencing

Phase 0 → 1 → 2 → 3 → 4 (**go/no-go on the residue, with user**) → 5 → 6 → 7.
Each phase is write-log-gated; the full batch runs at Phase-5 closeout only.
