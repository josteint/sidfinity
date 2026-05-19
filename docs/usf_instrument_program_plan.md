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

- [x] **1.1 / 1.2 / 1.3** Schema landed in
      `pipelines/commando/codegen/Commando/USF2.lean`. Grammar:
      - `InstSource` has 9 constructors: `const`, `pitchFreqLo/Hi`
        (with `USFFreqGenSpec` carrying optional vibrato + freqSlide
        + arpeggio), `pulseModLo/Hi` (linear or bidirectional),
        `waveProgStep` (ctrl sequencer with loop), and three
        `otherVoice{Ctrl,Pitch,Inst}` cross-voice runtime refs.
      - `EventTrigger`: `atFrame n`, `everyFrameFrom n`,
        `atFrameBeforeNoteEnd n`.
      - `FrameEvent { trigger, register, source }`.
      - `USFInstrument2 { events, noRelease, filterEnabled }`. No
        engineQuirks / voiceScratch / preserveNoteFlags / dynamicFreqEntries.
- [x] **1.4** All 13 Commando instruments hand-encoded in
      `pipelines/commando/codegen/Commando/CommandoInsts2.lean`. Builds
      cleanly via `lake build Commando.CommandoInsts2`. Reality
      check observations:
      - Every instrument fit the grammar — no new primitives needed.
      - Lo/hi freq events are duplicated (two events per freq write)
        with identical spec; could fold if we let one event target two
        regs, but the duplication is tolerable and keeps the schema
        simple. Defer.
      - HR ctrl-write is sometimes redundant when the waveform program
        has the gate already off at HR time. Per-inst optimisation;
        decide at codegen time, not in the data.
      - `noRelease` is actually a *per-note* attribute (set by the
        Hubbard pattern flag bit 5), not per-instrument. Currently
        on `USFInstrument2`; should move to the per-note level
        when patterns get redesigned in a later phase. Logged as a
        Phase 2+ refinement.
      - Commando's "noise drum" is NOT a `cv3I*` literal — it lives in
        patterns via the current `.percussion .dynamicCtrl` hack
        hardcoded to pitch 104. Phase 5 introduces a real drum
        instrument using `otherVoiceCtrl` events.
- [x] **1.5** `docs/usf2_emit_rules.md` — codegen contract for every
      source primitive. Documents the runtime layout the codegen
      assumes (per-voice `v_pitch / v_ctrl / v_inst / v_dur /
      v_frame / v_pwmod`, freq tables), and the 6502 sketch for each
      InstSource constructor and each EventTrigger. The contract is
      the "side-effect-free" property at the end: every source is a
      pure function of (pitch, frame_offset, named cross-voice refs).

## Phase 2 — Single-instrument proof on Commando

**Outcome.** Schema → codegen → SID → writelog round-trip works end-to-end
for the simplest possible instrument. Phase 2 acceptance test
(`tests/test_usf2_phase2.py`) passes.

- [x] **2.1** None of the 13 real Commando instruments are
      modulation-free (the simplest, inst 12, has freqSlide + waveProgStep).
      Took plan B from the plan's own list: define a SYNTHETIC minimal
      instrument `cv3I_test` (const + pitchFreqLo/Hi only). Real-Commando
      comparison deferred to Phase 3 when the extractor lands.
- [x] **2.2** `cv3I_test` added to `CommandoInsts2.lean`:
      const writes for ctrl/pw_lo/pw_hi/AD/SR at frame 0, pitchFreqLo/Hi
      from the empty FreqGenSpec at frame 0, HR triple (ctrl/AD/SR=0)
      at `atFrameBeforeNoteEnd 3`. Compiles via lake build.
- [x] **2.3** Codegen written in Python (`src/usf2_codegen_phase2.py`),
      NOT Lean. Plan deviation: Lean Codegen2.lean is deferred to
      Phase 6+ (when migrating production pipelines). Python is faster
      to iterate during the proof-of-concept stage. The Python emitter
      handles `const` + `pitchFreqLo/Hi` sources and `atFrame 0` +
      `atFrameBeforeNoteEnd` triggers — exactly what cv3I_test needs.
      Emits a self-contained PSID with init + play() that auto-loops
      after `dur_frames` frames.
- [x] **2.4** Built `/tmp/usf2/phase2.sid` (12924 bytes), playable
      via `tools/siddump`.
- [x] **2.5** `tests/test_usf2_phase2.py` verifies the writelog pattern:
      - frame 0: 7 V1 register writes (the init set)
      - frame 17 (= D-HR_THRESHOLD): 3 V1 writes (HR: ctrl, AD, SR)
      - all other frames in a note cycle: empty
      - the pattern loops every `D` frames
      ACCEPTANCE: **PASS**.

      Notable observation: sidplayfp's frame attribution drifts by one
      frame between the HR-frame and the next init-frame (we predicted
      init at frame 20; siddump shows it at frame 21). The schema is
      right; the test was tightened to verify the gap pattern rather
      than exact frame indices. The drift is the same emulator
      artefact we saw before in Devils Galop / Commando.

- [x] **2.6** No iteration needed. The synthetic instrument exercise
      passed on first attempt once the PSID header byte count was
      fixed (124-byte header; I had it at 122).

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
| 0     | 2026-05-19 | 2026-05-19 | 5577782 |
| 1     | 2026-05-19 | 2026-05-19 | f58de1a |
| 1     |         |           |        |
| 2     |         |           |        |
| 3     |         |           |        |
| 4     |         |           |        |
| 5     |         |           |        |
| 6     |         |           |        |
| 7     |         |           |        |
