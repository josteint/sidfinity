# Plan — off-table freq as ML-optimal musical frequency (DMC v5 → FC)

**Supersedes** `docs/offtable_statebuf_plan.md` and `docs/deconstruct_offtable_freq_plan.md`.
The deciding criterion is now explicit: **the USF must be ML-training-optimal**
(the project goal — "engine-neutral musical data an ML model can learn from").
That criterion *rules out* the `StateLayoutMirror` mechanism the prior plan
proposed, and the `freq_overrun` blob, in favour of representing each off-table
read as an explicit **frequency** attached to its wave step.

---

## Deciding criterion — ML-training-optimal USF

The USF feeds an ML model. Judge every representation by **what the model learns**:

| Representation | What the model sees | ML verdict |
|---|---|---|
| `freq_overrun` blob (today) | raw bytes at memory offsets after the freq table | **worst** — a memory dump; *hides* musical content (drum pitches) as opaque bytes |
| `StateLayoutMirror` (prior plan) | engine-state-layout metadata ("var X at offset N") | **bad** — teaches engine internals, not music |
| **per-step explicit frequency** | a frequency on a wave step → "noise/pulse at body-pitch F" | **best** — frequencies/pitches, engine-neutral, the stated goal |

So the off-table output is represented as a **frequency** (a musical pitch the
model learns), never bytes-at-offset and never a state-layout mirror.

---

## What the off-table read is (re-anchored 2026-06-20, rounds 12-14)

The engine computes `(wave_offset + curnote) & $FF` with no bounds check and reads
`freqlo/freqhi`; index > 95 falls past the 96-entry freq table into per-voice work
RAM, and that byte is played as a frequency. Ground-truth findings:
- **Dead-padding dominates** — ~81% of off-table members never fire the read
  (round 13); for them the blob is pure padding → the optimum is **nothing**.
- **Load-bearing reads are clean** — every load-bearing hit measured was
  **single-value** and **layout-independent** (round 14: Astovel/`Electric_Drum`,
  Dgazz/`Fourth`; round 13 audible Compotune `$0A00` pulse bass, Dead_End `$FF00`
  noise drum). These are real **drums / fixed-pitch tones** with a body frequency.
- **The residue is `trkptr`** — an absolute pointer (`LDA ($f8),y`), so its bytes
  are an address that *advances per frame*. A read landing here is a per-frame
  glitch, not a stable pitch (round 12).
- **DMC v5 layout**: `freqlo[96]` then `freqhi[96]` contiguous → the off-table
  **lo** read lands in the `freqhi` *table* (already in the USF; the composer
  derives it); only the off-table **hi** read is the work-RAM state byte.

---

## The chosen representation — per-step explicit frequency

Add an **absolute-frequency** form to the wave step (alongside the existing
note-relative melodic form and the TEST/drum form): the step carries the explicit
16-bit frequency it plays. The composer emits `ctrl` + that frequency directly —
**no out-of-bounds read, no window, no statebuf**. `freq_overrun` is dropped.

- **Stable off-table step** (drum / fixed tone — the load-bearing few): the
  frequency is constant → store it as the step's absolute freq. The model learns
  "this percussion/bass step plays at pitch F." Musical, engine-neutral, exact.
- **Never-reached step** (the ~81%): carry nothing extra; the next data table
  follows `freqhi`. No training noise, no blob.
- **Dynamic `trkptr` step** (per-frame glitch): **NOT** a musical pitch — do not
  encode it as an absolute freq (that teaches the model a false constant pitch).
  Out of the musical layer; the honest residue (see below).

Note-dependence: a step played at several notes reads several indices → store the
freq per reached note (a small map; one value for the single-note drum case).
The **lo** byte is derived from the freq table; only the state-derived **hi** is
intrinsic — but the USF exposes the *full* frequency (the model wants the pitch,
not a derivation rule).

---

## Success criteria (ML-led)

- [ ] **G-ML (deciding)** — the model sees off-table output as a **frequency on a
      wave step**, never bytes-at-offset / never state-layout metadata. Any
      non-musical residue is flagged engine-bookkeeping the tokenizer excludes.
- [ ] **G1 — write-log preserved** (CORE TENET): no regression vs the v5 baseline,
      full songlength, gated by the batch + `tools/regression.py`.
- [ ] **G2 — no opaque blob**: `freq_overrun` no longer emitted for DMC v5 (then
      FC); §9.2 leak scan clean.
- [ ] **G3 — parametric/musical** (§4): off-table steps carry frequencies/pitches.
- [ ] **G4 — reversible**: extract↔USF round-trips the absolute-freq steps.
- [ ] **G5 — cross-engine reuse** (§9.4): the absolute-freq wave-step form serves
      DMC v5 + FC (and is a natural fit for any off-table engine).
- [ ] **G6 — trichotomy**: non-musical residue is bookkeeping, decoupled from the
      musical layer; positional artifacts never enter musical USF.
- [ ] **G7 — residue honest**: dynamic `trkptr` glitches are measured, named, kept
      out of the musical layer, and never dressed as a musical pitch.

---

## Phase 0 — Re-anchor (every session)

- [ ] Re-read CORE TENET + `usf_representation_principle.md` §4/§7 + trichotomy
      §4.4. Confirm the ML criterion is the adversarial check, not a justification.
- [ ] Consult convergence-ledger C6/C7 (this plan is their canonical resolution).

## Phase 1 — USF: the absolute-frequency wave step

- [ ] Design the wave-step absolute-freq form (16-bit freq, optional per-note map)
      in `src/usf/{types,grammar.lark,parser,writer}.py` + `docs/usf_format.md`
      (usf_sync: spec + converters + player + tests together).
- [ ] Round-trip test (G4): a wave program with an absolute-freq step.

## Phase 2 — Composer: emit absolute-freq, drop the blob

- [ ] `composer_v5`: a wave-step path that writes `ctrl` + the explicit freq
      (no off-table read, no TEST side-effect on `$D404`).
- [ ] Stop emitting `freq_overrun`; remove the window after `freqhi`.

## Phase 3 — Extract: deconstruct off-table steps to frequencies

- [ ] For each off-table melodic step, compute the freq it produces at each
      reached note (lo from the freq table, hi = the work-RAM byte); emit the
      absolute-freq step. Reuse the reachability bound; minimal capture.
- [ ] Replace `_freq_overrun` with this per-step capture.

## Phase 4 — Measure & split the residue (go/no-go, with user)

- [ ] Build + verify the stratified subset. Stable steps → FULL (clean, musical).
      Regressions = members reaching the dynamic `trkptr` glitch.
- [ ] Census the regressions: `trkptr_hi` (near-constant page → typeable as
      bookkeeping const) vs `trkptr_lo` (advancing → genuine glitch). Confirms the
      round-13 hypothesis (audible/reached = clean) at scale.
- [ ] **Decision point (surface to user):** dynamic glitches → honest partial
      (kept out of the musical layer) vs heavier positional bookkeeping. Never
      re-blob, never fake a musical pitch.

## Phase 5 — Verify (subset → full batch), regression-gated

- [ ] Subset green (no regression vs its FULL members).
- [ ] Full v5 batch (background): FULL count ≥ baseline (stable clean wins offset
      any honest residue; report both). `tools/regression.py` clean before commit.
- [ ] Mass-write + `build_sid_db.py` refresh; commit (no Co-Authored-By).

## Phase 6 — FC unification (Move-1 payoff)

- [ ] Map FC's `freq_overrun` reads to frequencies (FC's are 8-bit wave-relative;
      likely land mostly in tables the USF already has → possibly *cleaner* than
      v5: measure). Migrate FC to the same absolute-freq wave step; drop FC's blob.
- [ ] Verify the FC wide-batch pass-rate holds.

## Phase 7 — Schema cleanup + prevent recurrence

- [ ] Remove the `freq_overrun` field once DMC v5 + FC are off it (usf_sync).
- [ ] §9.2 leak scan clean.
- [ ] Update convergence-ledger C6/C7: canonical resolution = "off-table reads →
      explicit per-step **frequency** (ML-musical); NEVER a verbatim window or a
      state-layout mirror; dynamic positional glitches → honest residue, out of
      the musical layer."
- [ ] `/uready-review`: standing B-class audit flags any new bytes-at-offset freq
      field.

---

## Risks & open questions

- **R1 — dynamic `trkptr` glitch is irreducible & non-musical.** It is neither a
  stable pitch (don't fake one) nor clean bookkeeping (per-frame). Honest partial
  for the members that reach it; Phase 4 sizes it (likely small — most never reach,
  audible cases look clean).
- **R2 — note-dependent multi-value steps.** A step played at many notes needs a
  per-note freq map; keep it minimal (only reached notes). If a step is genuinely
  many-valued and dynamic, it's the R1 glitch, not a map.
- **R3 — exactness vs ML.** Writelog-exactness (CORE TENET) still gates; the
  absolute-freq form is exact for stable steps. The ML criterion only changes the
  *shape* of what we store (a frequency, not bytes), not the exactness bar.
- **R4 — lo derivation assumes `freqhi` follows `freqlo`.** Verify contiguity per
  member; fall back to storing the full freq if not.

## Sequencing

Phase 0 → 1 → 2 → 3 → 4 (**go/no-go on the residue, with user**) → 5 → 6 → 7.
Write-log-gated throughout; full batch at Phase-5 closeout only.
