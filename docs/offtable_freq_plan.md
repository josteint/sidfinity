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

> **MEASUREMENT RESOLVED (round 15, verify-gated, authoritative).** Of 1217
> members with a non-empty blob: **997 dead-padding** (drop the blob), **44
> load-bearing** (all STABLE by definition → absolute-freq, exact), **176 partial
> *with* the blob** (pre-existing partials — index/wavepos bugs, dynamic state,
> non-freq — the blob is NOT their fix; untouched by this work). Therefore the
> de-verbatim is **LOSSLESS** (no FULL lost), and **`StateLayoutMirror` is NOT
> needed** — a load-bearing *dynamic* tier cannot exist (a static snapshot only
> fixes stable reads). The Phase-4 go/no-go below is thus already answered: **no
> residue is introduced by this work.** Recovering the 176 is separate future
> coverage.

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
- **Dynamic reads do not occur among the load-bearing set** (round 15: a static
  snapshot can only fix a stable read, so every blob-fixed member is stable). A
  dynamic off-table read would instead be a *pre-existing partial* (the 176) that
  the blob never fixed — those are separate coverage work, untouched here. So this
  de-verbatim has **no dynamic residue to handle**.

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

## Phase 1 — USF: the absolute-frequency wave step — ✅ DONE

- [x] `Instrument.offtable_freq: list[(step, note, lo, hi)]` — NOTE-KEYED (the
      44-shape check forced it: 55/98 load-bearing steps are multi-value) + full
      lo+hi (29 steps reach idx>=192 where lo is also state). `src/usf/types.py`
      + `grammar.lark` (`at(step,note,lo,hi)`) + `parser.py`/`writer.py` +
      `docs/usf_format.md`.
- [x] Round-trip test (G4): note-keyed + multi-value + idx>=192 survive
      write->parse, no leakage. Full regression green (0 regressed, all families).

## Phase 2 — Composer: emit absolute-freq, drop the blob — ✅ DONE

- [x] `composer_v5` builds extended in-bounds freqlo/freqhi from `offtable_freq`
      (idx = program freq[step]+note); no OOB read, no window, no TEST side-effect.
- [x] `freq_overrun` no longer emitted for v5.

## Phase 3 — Extract: deconstruct off-table steps to frequencies — ✅ DONE

- [x] `engine_model._assign_offtable_freq` walks each voice's orderlist
      (snd-tracked instrument + transpose) and records per-instrument
      `(step, note, lo, hi)` for every reached off-table read; `_slice_wave`
      moved to engine_model for consistent step indexing; `m.freq_overrun=[]`.
- [x] to_usf emits `Instrument.offtable_freq`; from_usf threads it into the model.

## Phase 4 — Measure the residue — ✅ DONE (round 15)

Verify-gated measurement (build with/without the blob, diff): **44 load-bearing
(all stable), 997 dead-padding, 176 pre-existing partials the blob never fixed.**
The de-verbatim introduces **no residue** (44 → absolute-freq stay FULL, 997 stay
FULL, 176 unchanged). No `StateLayoutMirror` tier exists. Nothing to decide here.
- [x] Residue sized: zero residue from the de-verbatim itself.
- [ ] (separate future coverage) classify the 176 partials' true causes (index/
      wavepos vs genuine dynamic counter vs other) — NOT part of this de-verbatim.

## Phase 5 — Verify (subset → full batch), regression-gated — ✅ DONE

- [x] Subset green: 42/44 load-bearing FULL, 60/60 dead-padding FULL.
- [x] Full v5 batch (step-keyed): 1039 FULL vs 1041 freq_overrun baseline.
- [x] Offset-keyed + offset-0 base-read capture: 1040 (recovers Redemption_6_4).
- [x] **Idle-program off-table capture: 1041 FULL = the freq_overrun baseline,
      0 regressed — FULLY LOSSLESS.** The off-table capture is complete: wave-
      program steps + offset-0 base reads (vib/note/glide-arrival) + the lead-in
      idle program. Both former "−2" bugs were **capture gaps**, not glide/
      vibrato/wave-position effect bugs (Redemption = vib_setup base read;
      Planet_Love = idle program). See RE_NOTES rounds 17-18.
- [x] Mass-wrote 1041 `.usf`+`.sidfinity.sid` + `build_sid_db.py` refresh;
      committed (no Co-Authored-By). `freq_overrun` blob eliminated from v5;
      off-table reads are ML-musical per-instrument frequencies.

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

- **R1 — RESOLVED (round 15).** The de-verbatim has no residue: load-bearing
  members are all stable (→ absolute-freq), dead-padding drops cleanly, and the 176
  dynamic/other partials were never blob-fixed (pre-existing, untouched). No
  dynamic glitch needs handling *in this work*; recovering the 176 is separate.
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
