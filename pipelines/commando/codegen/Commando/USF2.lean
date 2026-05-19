/-
  USF2.lean — instrument-as-program schema (Phase 1 of the refactor).

  See docs/usf_instrument_program_plan.md.

  An instrument is a list of `FrameEvent`s. Each event says:
    trigger:  WHEN to write this register (one-shot at frame N,
              every frame from N, or N frames before note end).
    register: WHICH SID register to write (one of 7 per-voice regs).
    source:   WHERE the value comes from — a pure function of
              (frame_offset, pitch) or a cross-voice runtime reference.

  No engine-aware fields in the schema: no `dynamicFreqEntries`, no
  `voiceScratch`, no `preserveNoteFlags`, no `.percussion .dynamicCtrl`
  with hardcoded pitch 104. Everything is expressed through the same
  uniform event/source vocabulary.

  Phase 1 sandbox: nothing reads this yet. Phase 2 builds a minimal
  Codegen2.lean that consumes this schema for ONE Commando instrument
  and verifies the writelog matches.
-/

namespace USF2

abbrev USFByte := UInt8

/-- The 7 per-voice SID registers the player ever writes. Filter and
    volume are global (not per-voice) and are handled separately. -/
inductive USFReg where
  | freqLo | freqHi
  | pwLo   | pwHi
  | ctrl
  | ad     | sr
  deriving Repr, DecidableEq

/-- Vibrato LFO shape. Hubbard only uses triangle in 1985-era SIDs.
    Adding sine / sawtooth would just extend this enum + the codegen. -/
inductive USFVibShape where
  | triangle
  deriving Repr

/-- PWM modulation style.
    - `linear speed`: every frame, add `speed` (signed) to pw_hi. Wraps.
    - `bidirectional lo hi speed`: pw_hi bounces between `lo` and `hi`,
       changing by `speed` per frame.
    Most Hubbard instruments use one of these two; if a SID uses
    something else we add a variant. -/
inductive USFPwMode where
  | linear        (speed : USFByte)
  | bidirectional (lo hi : USFByte) (speed : USFByte)
  deriving Repr

/-- Spec for the freq source: base pitch lookup with optional
    modulations. All modulations are pure functions of
    (frame_offset, pitch); they compose in the fixed order
    vibrato → freqSlide → arpeggio (arpeggio OVERWRITES base pitch,
    so it must come last). -/
structure USFVibSpec where
  period : Nat            -- LFO period in frames (Hubbard uses 8)
  depth  : Nat            -- right-shift count → semitone delta scale
  onset  : Nat            -- frames of no-modulation at note start
  shape  : USFVibShape
  deriving Repr

structure USFFreqSlideSpec where
  delta      : Int        -- signed per-step delta added to freq_hi
  startDelay : Nat        -- frames before slide starts
  stopAtZero : Bool       -- stop sliding when freq reaches 0
  deriving Repr

structure USFArpSpec where
  intervals  : List Int   -- semitone offsets to cycle through
  stepEvery  : Nat        -- frames per arp step
  startDelay : Nat        -- frames before arpeggio starts
  deriving Repr

structure USFFreqGenSpec where
  vibrato   : Option USFVibSpec       := none
  freqSlide : Option USFFreqSlideSpec := none
  arpeggio  : Option USFArpSpec       := none
  deriving Repr

structure USFPwGenSpec where
  mode       : USFPwMode
  startDelay : Nat        := 0
  deriving Repr

/-- Waveform program: per-frame ctrl values. Index advances by 1 every
    `stepEvery` frames. Once past the program's end, the active step
    is `loop` for all subsequent frames. -/
structure USFWaveProgSpec where
  program   : List USFByte
  loop      : Nat
  stepEvery : Nat
  deriving Repr

/-- Where a register write's value comes from.

    Pure sources (depend on `frame_offset` and `pitch` only):
      const, freqLo, freqHi, pwLo, pwHi, waveStep, ad, sr (all
      ad/sr are usually const).
    Engine-state sources (cross-voice runtime refs — for Hubbard's
    noise drums and similar):
      otherVoiceCtrl, otherVoicePitch, otherVoiceInst.

    The codegen knows how to emit 6502 for each. For pure sources
    it computes from pitch + frame_offset; for engine-state sources
    it emits a direct LDA against the named runtime variable. -/
inductive InstSource where
  | const            : USFByte → InstSource
  | pitchFreqLo      : USFFreqGenSpec  → InstSource
  | pitchFreqHi      : USFFreqGenSpec  → InstSource
  | pulseModLo       : USFPwGenSpec    → InstSource
  | pulseModHi       : USFPwGenSpec    → InstSource
  | waveProgStep     : USFWaveProgSpec → InstSource
  | otherVoiceCtrl   : Fin 3 → InstSource
  | otherVoicePitch  : Fin 3 → InstSource
  | otherVoiceInst   : Fin 3 → InstSource
  deriving Repr

/-- When the event fires, relative to note start. -/
inductive EventTrigger where
  /-- One-shot write at frame N (relative to note-start). -/
  | atFrame              : Nat → EventTrigger
  /-- Every frame from N until note end (inclusive). -/
  | everyFrameFrom       : Nat → EventTrigger
  /-- One-shot at the frame that is N frames before the note ends
      (i.e. when the note's frame counter equals N). Used for the
      Hubbard "HR" gate-off + AD/SR-zero just before the next note
      starts, so the SID envelope retriggers cleanly. -/
  | atFrameBeforeNoteEnd : Nat → EventTrigger
  deriving Repr

structure FrameEvent where
  trigger  : EventTrigger
  register : USFReg
  source   : InstSource
  deriving Repr

/-- An instrument is just a list of frame events plus a couple of
    engine-agnostic bookkeeping flags. NO `dynamicFreqEntries`,
    `voiceScratch`, `preserveNoteFlags`, etc. -/
structure USFInstrument2 where
  events        : List FrameEvent
  /-- If true, the gate-off events at `atFrameBeforeNoteEnd` are
      suppressed: this instrument's gate stays on into the next note
      (tie / legato semantics). -/
  noRelease     : Bool := false
  /-- If true, this voice routes through the global filter. -/
  filterEnabled : Bool := false
  deriving Repr

end USF2
