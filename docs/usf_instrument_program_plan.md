# Plan: USF instrument-as-program refactor

**Goal.** Replace USF's current typed-fields representation of instruments
(`initCtrl`, `vibrato`, `pwMod`, `arpeggio`, `skydive`, plus per-song
`engineQuirks` that describe Hubbard memory-aliasing tricks) with a
*behavioral spec*: each instrument is a small program of per-frame SID
register writes, parameterised by pitch (and, where the original
engine does so, by cross-voice state).

**Success criterion.** For every Hubbard SID in `pipelines/`, the
rebuild's `siddump --writelog` stream is identical to the original's,
frame-for-frame and register-for-register. The .sid file's raw bytes
may differ (the codegen is allowed to emit longer / different 6502
than Hubbard did). Only the SID-register write stream matters.

**Why.** The current USF leaks engine implementation into the data
(`dynamicFreqEntries`, `preserveNoteFlags`, `voiceScratch`,
`.percussion .dynamicCtrl`). That defeats USF's value as ML training
data: a model trained on it would learn Hubbard's address-aliasing
tricks rather than musical structure. Re-expressing instruments as
behavioral programs keeps the music abstract and pushes all
engine-specific knowledge into the codegen, which is plumbing.

---

## Phase 0 — Foundations

- [x] **0.1** Verification harness: `src/writelog_diff.py` — runs siddump
      --writelog on two SIDs and compares per-frame register-write
      sequences. Cycle counters within a frame are ignored; write
      ORDER within a frame is significant by default
      (`--ignore-order` available for diagnostic / multi-set view).
      Identity test = 100% ordered. Confirmed surfaces real
      differences (Devils Galop: 47.6% ordered / 91.4% ignore-order —
      shows PW write-order diffs and ~60 missed VOL writes).
- [x] **0.2** Canary pipeline: **Commando** (most engine-quirk-loaded).
      Reality check: the current Commando rebuild is NOT writelog-
      identical to the original — 61.5% strict-ordered, 92.4%
      ignore-order. The "Grade A" claim in its README is from
      `writelog_grade.py`'s CSV snapshot, not write-sequence match.
      This actually strengthens the case for the refactor: the
      current engineQuirks block isn't producing a writelog-identical
      rebuild even with all its engine awareness, so simplifying
      shouldn't make things worse and might make things better.
- [x] **0.3** Baseline captured at `tests/baselines/commando_original_writelog.txt`
      (siddump --writelog --duration 30 --raw of
      demo/hubbard/Commando_original.sid; 1498 frame lines).
- [x] **0.4** New schema lives in `pipelines/commando/codegen/Commando/USF2.lean`
      (placeholder file created; Phase 1 fills it in). Co-located with
      Commando's existing USF.lean so the current pipeline keeps
      working during the refactor. Will be promoted to a shared
      location once Phase 6 migration begins.

## Phase 1 — Schema design

- [ ] **1.1** Draft the `InstSource` enumeration. First-pass vocabulary:
  - `const : USFByte`
  - `pitchFreqLo`, `pitchFreqHi` — freq_table[pitch] lookup
  - `vibrato { shape, period, depth, onset }` — produces an LFO-modulated
    freq. Either-or: emit as a `function`-primitive, or precompute
    per-frame values and emit as constants.
  - `pwBidir { lo, hi, speed }` — bidirectional PWM bouncing pw_hi
    between `lo` and `hi` at `speed` increments per frame.
  - `freqSlide { delta, startDelay, stopAtZero }` — additive freq slide
    (Hubbard "skydive" is this).
  - `arpeggio { intervals, stepEvery }` — pitch rotation.
  - `otherVoiceCtrl  : Fin 3` — cross-voice reference (Hubbard drum).
  - `otherVoicePitch : Fin 3`
  - `otherVoiceInst  : Fin 3`
  - `prevValue` — the freq/pw/etc. value this register held last frame.
- [ ] **1.2** Draft `FrameEvent { atFrame, register, source }`.
- [ ] **1.3** Draft `USFInstrument2 { events : List FrameEvent, loopFrom : Option Nat }`.
- [ ] **1.4** Encode all 13 Commando instruments by hand from the
      annotated disassembly. Reality-check: do all of them fit cleanly
      in this grammar, or do we discover new primitives needed?
- [ ] **1.5** Document the FrameEvent → 6502 emit rules for each source
      primitive (e.g. `vibrato` → `LDA frame_ctr; AND #$07; ...`).
      Side-effect-free: an instrument's events should describe pure
      writes; no implicit state beyond `atFrame`, `pitch`, and the
      named cross-voice sources.

## Phase 2 — Single-instrument proof on Commando

- [ ] **2.1** Pick the SIMPLEST Commando instrument that has none of
      vibrato/PWM/fx (a plain pulse-with-envelope; e.g. an instrument
      used only for melody notes). Confirm via disassembly that its
      per-frame writes are constant-plus-pitch-lookup.
- [ ] **2.2** Hand-write its `USFInstrument2` literal in `USF2.lean`.
- [ ] **2.3** Write a minimal alternate codegen
      `Codegen2.lean::emitInstrumentProgram` that, given a
      `USFInstrument2` and a pitch, emits 6502 to perform the
      described writes when the instrument is played. No engine
      assumptions beyond "this is one voice of a 3-voice player."
- [ ] **2.4** Build a tiny test pattern that triggers ONLY this
      instrument (one note, one voice). Run it through the codegen,
      produce a SID, dump its writelog.
- [ ] **2.5** Compare to the corresponding note in the original
      Commando writelog (extract just that note's per-frame writes).
      Acceptance: register-for-register match for the note's duration.
- [ ] **2.6** Iterate on the source primitive set until 2.5 passes.

## Phase 3 — Extractor prototype

- [ ] **3.1** Build `pipelines/commando/extract/inst_program.py`: given
      an instrument index, run the original SID in py65, find every
      note that uses this instrument, capture the per-frame register
      writes during those notes.
- [ ] **3.2** Generalise across the captured note-occurrences: which
      writes are constant, which scale with pitch, which need
      explicit per-frame values, which depend on cross-voice state.
- [ ] **3.3** Emit a `USFInstrument2` literal automatically.
- [ ] **3.4** Auto-extract the Phase 2 instrument and verify the
      output matches the hand-written version byte-for-byte.
- [ ] **3.5** Auto-extract a vibrato-bearing Commando instrument.
      Verify writelog match for one note via the same harness.

## Phase 4 — All Commando melodic instruments

- [ ] **4.1** Auto-extract all 13 Commando instruments via 3.x.
- [ ] **4.2** Extend `Codegen2.lean` to emit each source primitive
      (vibrato, PWM, freqSlide, arpeggio).
- [ ] **4.3** Build a Commando SID using `USF2` + `Codegen2` (no engineQuirks,
      no dynamicFreqEntries). Run the full song.
- [ ] **4.4** Diff writelogs: ours vs. original, for the entire song.
      Expected outcome: drum sections diverge (Phase 5 handles them);
      everything else should match.

## Phase 5 — The hard case: cross-voice alias (drum)

- [ ] **5.1** Implement `InstSource.otherVoiceCtrl` / `otherVoicePitch`
      in `Codegen2`. Each requires the codegen to know the runtime
      address of `v_ctrl[N]` / `v_pitch[N]` and emit a direct LDA
      against that — no freq-table-aliasing trick.
- [ ] **5.2** Auto-extract Commando's drum instrument (the one with 25
      `.dynamicCtrl` occurrences in the current patterns). The
      extractor should detect: "this instrument's freq_lo each frame
      equals `v_ctrl[V1]` at the moment of write."
- [ ] **5.3** Codegen emits the equivalent 6502 directly: e.g.
      `LDA v_ctrl_v1; STA $D40E; LDA v_ctrl_v2; STA $D40F`.
- [ ] **5.4** Run full Commando. Diff writelogs. Expected: identical
      to original.
- [ ] **5.5** If divergence remains: investigate. Possible causes:
      cycle-timing of when v_ctrl is captured (Hubbard's aliased read
      reads CURRENT v_ctrl; our LDA might read same; but if our
      voice-processing order differs, the captured value could differ).
      Fix by adjusting either the source primitive's "read phase" or
      the codegen's per-voice scheduling.

## Phase 6 — Migration of other pipelines

- [ ] **6.1** Migrate **Devils Galop** (2 dynamicFreqEntries, 1
      aliased pitch — simplest cross-voice case).
- [ ] **6.2** Migrate Hubbard pipelines with no aliasing (Action Biker,
      Chimera, Monty, Human Race, Hunter Patrol, Thing on a Spring,
      One Man and His Droid). These should be straightforward since
      they have 0 dynamicFreqEntries — just need clean instrument
      programs.
- [ ] **6.3** Migrate remaining D/F pipelines (Last V8, Rasputin,
      Battle of Britain, Bump Set Spike, Master of Magic, Gremlins) —
      whatever's left after parallel-thread cleanup of those.
- [ ] **6.4** Remove `USFEngineQuirks` from the `USF.lean` schema
      entirely. Drop `dynamicFreqEntries`, `voiceScratch`,
      `noteLoadOps`, `patternEndOps`, `preserveNoteFlags`. Drop
      `.percussion` from `USFNoteKind`.
- [ ] **6.5** Delete `USF.lean`, rename `USF2.lean` to `USF.lean`.
      Same for `SongData.lean` / `Codegen.lean`. CLAUDE.md +
      `docs/PLAN.md` updated.

## Phase 7 — ML-readiness verification

- [ ] **7.1** Grep all `pipelines/*/codegen/*/SongData.lean` files for
      any field that references runtime addresses, engine variables,
      or per-frame state. Expectation: nothing matches.
- [ ] **7.2** Document the final `InstSource` vocabulary as the
      "instrument primitive set" — this is what an ML model treats
      as its action space when generating instruments.
- [ ] **7.3** Export all migrated SongData as a clean tokenised dataset.
      Sanity-check: re-importing the tokenised form regenerates the
      original `USFInstrument2` literals exactly.
- [ ] **7.4** Train a small baseline model on the dataset (or hand off
      to the ML side of the project) and confirm it produces valid,
      playable USF — closing the loop on the "USF is good ML training
      data" claim.

---

## Risks and open questions

- [ ] **R.1** **Vibrato as data**: Hubbard's vibrato is a per-frame
      computation (`LDA frame_ctr; AND #$07; CMP #4; ...`). Can we
      describe it as a parametric source primitive (`vibrato { ... }`)
      that the codegen expands to that 6502 — or do we need a more
      general "function" primitive? Test in Phase 1.4.
- [ ] **R.2** **PWM state**: bidirectional PWM has a direction bit
      stored in voice state. The instrument can be parameterised by
      thresholds, but the voice-local direction is engine state. Where
      does it live in the new schema? Probably a `pwState` field per
      voice in the codegen, not in the instrument program itself.
- [ ] **R.3** **Codegen size**: replacing Hubbard's compact tricks with
      straightforward code may make play() take longer per frame.
      If it overruns the PAL VBI (~19656 cycles), the rebuild won't
      play correctly. Estimate cycle costs in Phase 1; measure after
      Phase 4.
- [ ] **R.4** **Engine state for cross-voice references**: when an
      instrument reads `otherVoiceCtrl V1`, the codegen needs to know
      where `v_ctrl[V1]` lives (absolute address or zero-page). That's
      a codegen contract, not USF data. Document it in 1.5.
- [ ] **R.5** **Phase ordering in cross-voice reads**: Hubbard's
      original reads aliased pitches at specific moments in the
      per-voice loop (some at frame start, some between V3 and V2,
      etc.). Our codegen must place its direct LDAs at equivalent
      timing points for the writelog to match. The current
      `USFDynamicFreqEntry.phase` field captures this notion; in the
      new schema, an `atFrame` event might need to be augmented with
      "at which point in the voice loop the read happens." Test in
      Phase 5.5.
- [ ] **R.6** **Some Hubbard SIDs may need primitives we haven't
      thought of**. Phase 1.4's hand-encoding of all 13 Commando
      instruments is the first sanity check; Phase 6.1-6.3 will
      surface anything Commando didn't.

## Stop conditions

We pause and re-plan if:
- Phase 2.5 fails after >3 days of source-primitive iteration (means
  the InstSource grammar isn't expressive enough — needs a meta-
  primitive like "function pointer" which would hurt ML interpretability).
- Phase 4 reveals a Commando instrument that can't be cleanly
  decomposed (e.g., truly stateful inter-instrument dependencies).
- Phase 5 shows that any direct re-implementation of the drum
  diverges from the original writelog at a layer below cycle-timing
  — i.e., a *semantic* difference we can't capture.

In any of those cases, document the obstacle and decide whether
to expand the grammar, accept some engine-aware extension, or
abandon the refactor for that instrument class.

---

## Tracking

Add commit hashes per phase as they complete. Reuse this file as the
single source of truth — no parallel TODO lists.

| Phase | Started | Completed | Commit |
|---|---|---|---|
| 0     |         |           |        |
| 1     |         |           |        |
| 2     |         |           |        |
| 3     |         |           |        |
| 4     |         |           |        |
| 5     |         |           |        |
| 6     |         |           |        |
| 7     |         |           |        |
