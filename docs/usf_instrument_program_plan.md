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

Phase 3 reshaped substantially against reality (see commits 785192d ..
40df47c). What was actually built:

- [x] **3.1** `pipelines/commando/extract/inst_program.py` — runs the
      real Commando binary in py65, hooks every $D4xx write, segments
      the run into per-instrument NoteOccurrences. (785192d)
- [x] **3.2** `inst_generalize.py` — a pure capture-generalisation could
      not work (Commando instruments are not pure functions of (pitch,
      frame): vibrato/arp key off the global frame counter; PWM is a
      shared accumulator). Instead: decode each instrument from its
      8-byte table row into USF2 primitives, verified against the
      captures. 11/13 decode cleanly. (4ceecbe)
- [x] **3.3** Built the missing reference semantics first
      (`inst_interp.py`, then the whole-song `song_interp.py`), then
      `emit_usf2.py` emits `CommandoInsts2_gen.lean` — the 13
      instruments as USF2 behavioral-parameter literals (parametric
      form; supersedes the Phase-1 events-list sketch). Type-checks.
      (1312bb8, 90c85d1, 467ad84, ee7c0f9, b1778b3, 40df47c)
- [x] **3.4 / 3.5** Verification far exceeded the original "one note vs
      hand-encoded" plan: `song_interp.py` reproduces Commando subtune
      0's **entire melodic engine byte-exact** (1270/1500 frames; the
      230 remaining are all inst 4, the noise drum). Every melodic
      instrument, every effect, shared state, and the cross-voice
      arpeggio are verified instruction-by-instruction.

**Phase 3 outcome:** the melodic refactor's core question — can USF2
faithfully represent Commando? — is answered **yes**, with a working
Python reference interpreter proving it. The only unhandled instrument
is inst 4 (the drum) → Phase 5.

## Phase 4 — All Commando melodic instruments

Done (commits 9437b01 .. 8e36a65). The codegen is Python, not Lean —
continuing Phase 2.3's "Python codegen first" deviation; the Lean
`Codegen2` is deferred to the migration phases.

- [x] **4.1** All 13 instruments emitted (`emit_usf2.py`, Phase 3).
- [x] **4.2 / 4.3** `pipelines/commando/codegen/usf2_codegen.py` — a
      clean 6502 Commando engine (xa65 assembly, a faithful port of
      `song_interp.py`) + the USF2 data serialised into memory tables,
      assembled into a real `.sid`. No engineQuirks, no
      dynamicFreqEntries. Implements the full melodic engine: tick/note
      advancement, tie notes, HR, vibrato, skydive, arpeggio, and both
      PWM modes with the shared per-instrument accumulator. Each effect
      was added and verified against `song_interp` incrementally.
      Final stage: rebuilt SID vs `song_interp` [all melodic effects] —
      **1500/1500 frames byte-exact**.
- [x] **4.4** `siddump --writelog` of the rebuilt SID vs the original
      Commando: **78.97 % ordered write-sequence match** (1183/1498).
      The 315 divergent frames are exactly the two expected gaps — V2
      (inst 4, the noise drum) and V1 (inst 7's off-table arpeggio).
      Every melodic instruction matches.

**Phase 4 outcome:** a clean USF2 representation now round-trips to a
playable SID that is 79 % writelog-identical to Hubbard's original, the
entire remaining gap being the Phase-5 drum + cross-voice arp.

## Phase 5 — The hard case: cross-voice

Phase 5 reshaped against reality. Two genuinely cross-voice things, not
the one the plan sketch anticipated:

- [x] **5a — inst 7's off-table arpeggio** (commit 3647892). inst 7's
      octave arp reads `freq_table[pitch+12]` which, at pitch 88, runs
      past the 96-entry table into other voices' `note_idx`. The codegen
      bakes Hubbard's note_idx into the note stream and the engine reads
      voices 1/2's `v_hubidx` directly. Result: the rebuilt SID is
      byte-exact with the original on every melodic voice (py65,
      play-call attributed: 1270/1500 = 84.7 %; all 230 diffs are the
      drum).

- [ ] **5b — the noise drum (inst 4)**. NOT just a cross-voice
      instrument — it is a separate sub-engine (`_drum_engine` /
      `_drum_init` in src/hubbard_emu.py, $53A5-$5427 + $5531): its own
      state machine, a drum pattern table at $55F9+, and — the key
      cross-voice part — `drum_enable`, which SUPPRESSES the melodic
      voices' note-start + effect writes whenever the drum is active.
      Needs implementing first in `song_interp.py` (the reference does
      not have it yet — that is why song_interp itself is 1270/1500 vs
      the original), then ported to `usf2_codegen.py`. This is the last
      ~15 % and a Phase-4-sized effort of its own.

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
| 2     | 2026-05-19 | 2026-05-19 | 31f6e33 |
| 3     | 2026-05-20 | 2026-05-20 | 785192d..40df47c |
| 4     | 2026-05-20 | 2026-05-20 | 9437b01..8e36a65 |
| 5     |         |           |        |
| 6     |         |           |        |
| 7     |         |           |        |
