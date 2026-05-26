/-
  State.lean — Engine state for the Das Model compiler.

  The compile function is a pure state machine:
    (Song, State) → (State, FrameStream)

  State captures everything the engine needs to track between frames.
  This is the formalization of what das_model_gen.py stores in ZP bytes.
-/

import «SID»

-- Per-voice state (what each voice tracks between frames)
structure VoiceState where
  tickCtr    : Nat        -- frames until next note (0 = load new note)
  noteLen    : Nat        -- total frames for current note
  patIdx     : Nat        -- current index in orderlist
  noteIdx    : Nat        -- current index within pattern
  wPtr       : Nat        -- position in waveform W program
  pwLo       : Byte       -- current pulse width lo
  pwHi       : Byte       -- current pulse width hi
  pwDir      : Bool       -- PW direction (false=up, true=down)
  pwPeriod   : Nat        -- PW sub-counter (for bidirectional period)
  prevInst   : Option Nat -- previous instrument ID (none = first note)
  fhiState   : Byte       -- freq_hi internal state (for freq slide / bit0)
  hubOff     : Nat        -- pattern byte offset (for extended table T[100])
  basePitch  : Byte       -- current note's pitch index

-- Global engine state
structure EngineState where
  frameCtr   : Byte                  -- global frame counter (wraps at 256)
  voices     : Fin 3 → VoiceState   -- per-voice state
  pwLive     : List Byte             -- per-instrument mutable PW lo (shared state)
  ctrlByte   : Fin 3 → Byte         -- last ctrl written per voice (for T[104])

-- Initial state: all voices ready to load first note
def VoiceState.init : VoiceState :=
  { tickCtr := 0          -- triggers note load on first frame (Hubbard: DEC 0 → $FF → BMI)
  , noteLen := 0
  , patIdx := 0
  , noteIdx := 0
  , wPtr := 0
  , pwLo := ⟨0, by omega⟩
  , pwHi := ⟨0, by omega⟩
  , pwDir := false
  , pwPeriod := 0
  , prevInst := none
  , fhiState := ⟨0, by omega⟩
  , hubOff := 0
  , basePitch := ⟨0, by omega⟩
  }

def EngineState.init (instruments : List Instrument) : EngineState :=
  { frameCtr := ⟨255, by omega⟩  -- INC on first frame → 0
  , voices := fun _ => VoiceState.init
  , pwLive := instruments.map fun i => i.pw.initLo
  , ctrlByte := fun _ => ⟨0, by omega⟩
  }

