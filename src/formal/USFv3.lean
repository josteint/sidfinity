/-
  USFv3.lean — Universal SID Format, version 3.

  Engine-agnostic representation of SID music. The decompiler converts
  engine-specific binaries (Hubbard, GT2, JCH, etc.) into this format.
  The universal player compiles USF back to a .sid file that reproduces
  the original audio (frame-accurate).

  Design principles (from docs/USF_v3_design.md):
  1. Frame-accurate granularity (frame = play() call count)
  2. Behavioral, not procedural (USF describes what, not how)
  3. All engine state lives in USF or is computed by player
  4. Self-contained instruments
-/

-- Reuse base types from SID.lean
abbrev USFByte := Fin 256
abbrev USFNybble := Fin 16

-- ==========================================================================
-- Instrument behaviors
-- ==========================================================================

inductive USFLFOShape where
  | triangle  -- 0,1,2,3,3,2,1,0 (Hubbard)
  | sine      -- sinusoidal
  | square    -- on/off
  | sawtooth  -- ramp up
  deriving Repr, BEq

inductive USFArpPhase where
  | global    -- uses global frame counter
  | perVoice  -- per-voice counter
  deriving Repr, BEq

-- Pulse Width Modulation
inductive USFPWMode where
  | linear : USFByte → USFPWMode                      -- add `speed` to pw_lo each step
  | bidirectional : USFByte → USFByte → USFByte → USFPWMode
                                                       -- (speed, minHi, maxHi) — bounce
  | table : List (USFByte × USFByte) → USFPWMode      -- explicit (lo,hi) sequence
  deriving Repr

structure USFPWMod where
  mode       : USFPWMode
  stepEvery  : Nat   -- frames between updates (1 = every frame)
  startDelay : Nat   -- frames after note-load before PW starts moving
  deriving Repr

-- Vibrato
structure USFVibrato where
  shape         : USFLFOShape
  periodFrames  : Nat              -- one full LFO cycle in frames
  semitoneShift : Nat              -- right-shift count (larger = smaller vibrato)
  onsetFrames   : Nat              -- frames after note-load before active
  rampUpFrames  : Nat              -- gradual depth increase (0 = sudden)
  unipolar      : Bool             -- 0..depth vs -depth..+depth
  deriving Repr

-- Arpeggio
structure USFArpeggio where
  intervals    : List Int          -- semitone offsets from base pitch
  stepEvery    : Nat               -- frames per arp step
  phaseSource  : USFArpPhase
  startDelay   : Nat               -- frames before arp activates
  deriving Repr

-- Frequency slide
inductive USFFreqSlideKind where
  | monotonic : Int → USFFreqSlideKind
                       -- per-step delta in freq_hi units (negative = down)
  | toTarget : USFByte → USFByte → Int → USFFreqSlideKind
                       -- (target_lo, target_hi, max step size) — portamento
  deriving Repr

structure USFFreqSlide where
  kind        : USFFreqSlideKind
  stepEvery   : Nat                -- frames per slide step
  startDelay  : Nat                -- frames before slide activates
  stopAtZero  : Bool               -- stop when freq_hi reaches 0
  deriving Repr

-- Release / hard restart behavior
structure USFRelease where
  framesBeforeEnd : Nat            -- gate-off this many frames before note ends
  zeroAdsr        : Bool           -- write AD=0, SR=0 on release (hard restart)
  noRelease       : Bool           -- if true: no gate-off at all (sustained)
  deriving Repr

-- Effect chain ordering
inductive USFEffectKind where
  | vibrato
  | freqSlide
  | pwMod
  | arpeggio
  | waveformStep      -- write current waveform[wPtr] to ctrl
  | gateCheck         -- check release condition
  deriving Repr, BEq

-- Initial frequency modifier (for percussion-like behaviors)
inductive USFInitFreqMod where
  | normal                              -- look up freq from pitch table
  | dynamicVoiceCtrl                    -- freq = (v_ctrl[0], v_ctrl[1]) — Hubbard pitch-104 trick
  deriving Repr

-- ==========================================================================
-- Instrument
-- ==========================================================================

structure USFInstrument where
  -- Static parameters (set at note-load time)
  initCtrl      : USFByte           -- ctrl byte at note-on (waveform[0] equivalent)
  initPwLo      : USFByte
  initPwHi      : USFByte
  ad            : USFByte           -- attack/decay (4+4 bits)
  sr            : USFByte           -- sustain/release (4+4 bits)
  initFreqMod   : USFInitFreqMod    -- normal or dynamic (percussion)

  -- Per-frame waveform stepping
  waveformProgram : List USFByte    -- ctrl bytes per step
  waveLoop        : Nat             -- loop point in waveform program
  waveStepEvery   : Nat             -- frames per waveform step (0/1 = every frame)

  -- Effects (each Option = enabled if Some)
  pwMod         : Option USFPWMod
  vibrato       : Option USFVibrato
  freqSlide     : Option USFFreqSlide
  arpeggio      : Option USFArpeggio

  -- Effect chain order (evaluated in this order each sustain frame)
  effectOrder   : List USFEffectKind

  -- Release behavior
  release       : USFRelease

  -- Filter routing
  filterEnabled : Bool              -- this instrument routes through global filter
  deriving Repr

-- ==========================================================================
-- Notes / patterns
-- ==========================================================================

inductive USFPercussion where
  | noiseHit : USFByte → USFByte → USFPercussion   -- explicit (freq_lo, freq_hi)
  | dynamicCtrl                                     -- use voice ctrl bytes as freq
  deriving Repr

inductive USFNoteKind where
  | pitched : USFByte → USFNoteKind                -- normal pitched note (pitch 0-95)
  | percussion : USFPercussion → USFNoteKind        -- drum/noise hit
  | rest                                            -- silence (gate stays off)
  | tie                                             -- continue previous note
  deriving Repr

structure USFNoteEvent where
  kind            : USFNoteKind
  durationFrames  : Nat              -- TOTAL frames this note holds the voice
  instrument      : Nat              -- index into instrument table
  -- Portamento byte (Hubbard format): 0 = no portamento; otherwise bits 1-6
  -- encode the per-frame freq delta and bit 0 encodes direction (1 = down).
  -- Codegen interprets as: delta = byte AND $7E, direction = byte AND $01.
  porta           : Nat := 0
  deriving Repr

structure USFPattern where
  notes : List USFNoteEvent
  deriving Repr

structure USFVoice where
  orderlist  : List Nat              -- pattern indices
  loopPoint  : Option Nat            -- orderlist position to loop back to
  deriving Repr

-- ==========================================================================
-- Filter (song-level resource)
-- ==========================================================================

inductive USFFilterMode where
  | lowpass | bandpass | highpass | off
  deriving Repr, BEq

inductive USFFilterMod where
  | static : UInt16 → USFFilterMod                        -- fixed cutoff
  | linearSweep : UInt16 → Int → Bool → USFFilterMod      -- (start, perFrameDelta, stopAtBound)
  | program : List UInt16 → Nat → USFFilterMod            -- (cutoff sequence, loopPoint)
  deriving Repr

structure USFFilterSpec where
  mode      : USFFilterMode
  resonance : USFNybble
  cutoffMod : USFFilterMod
  deriving Repr

-- ==========================================================================
-- Engine quirks (data-driven, kept out of the core music semantics)
-- ==========================================================================

-- A reference to a byte produced by some piece of voice/voice-state at the
-- moment a dynamic freq-table entry is updated.
inductive USFDynRef where
  | constant   : USFByte → USFDynRef
  | scratch    : (voice : Fin 3) → (slot : Nat) → USFDynRef
                              -- v_scratch[voice][slot]
  | voiceCtrl  : Fin 3 → USFDynRef
                              -- v_ctrl[voice] (voice's last-loaded ctrl byte)
  | voicePitch : Fin 3 → USFDynRef
                              -- v_pitch[voice]
  | voiceInst  : Fin 3 → USFDynRef
                              -- v_inst[voice] (= "prev_inst" if voice hasn't
                              -- loaded yet this frame; current inst otherwise)
  deriving Repr

inductive USFUpdatePhase where
  | atFrameStart                       -- top of play(), before any voice runs
  | beforeVoice : Fin 3 → USFUpdatePhase
                                       -- right before voice N exec runs
                                       -- (= das_model's "between V_prev and V_N")
  deriving Repr

structure USFDynamicFreqEntry where
  freqSlot   : Nat                  -- index into freq table to write
  loSource   : USFDynRef
  hiSource   : USFDynRef
  phase      : USFUpdatePhase
  deriving Repr

structure USFVoiceScratch where
  name    : String           -- documentation only ("hub_off", "seq_idx", ...)
  initial : USFByte          -- value at song-init
  deriving Repr

inductive USFNoteLoadOp where
  | addConst         : Nat → USFByte → USFNoteLoadOp
  | addByFlag        : Nat → List (USFByte × USFByte × USFByte) → USFNoteLoadOp
                          -- (flag_mask, flag_value, delta) entries; first match wins
  | setConst         : Nat → USFByte → USFNoteLoadOp
  -- Eager pattern-end detection: AFTER pattern-pointer advance, peek next pitch
  -- byte; if it's the end-of-pattern marker ($00), apply this op.
  | resetIfNextEnds  : Nat → USFNoteLoadOp
  | incIfNextEnds    : Nat → USFByte → USFNoteLoadOp
  deriving Repr

inductive USFPatternEndOp where
  -- Triggered at advance_order time (when note_load reads $00 as pitch byte).
  | reset     : Nat → USFPatternEndOp
  | increment : Nat → USFByte → USFPatternEndOp
  deriving Repr

structure USFEngineQuirks where
  voiceScratch       : List USFVoiceScratch     := []
  noteLoadOps        : List USFNoteLoadOp       := []
  patternEndOps      : List USFPatternEndOp     := []
  dynamicFreqEntries : List USFDynamicFreqEntry := []
  -- Whether to keep the inst-byte's bits 6/7 in pattern data (consumed by
  -- noteLoadOps via flag-conditional ops). When false, codegen masks at emit.
  preserveNoteFlags  : Bool                     := false
  deriving Repr

-- ==========================================================================
-- Song-level
-- ==========================================================================

inductive USFPlayRate where
  | vbi                              -- one play per VBI (~50Hz PAL)
  | cia : UInt16 → USFPlayRate       -- play every N CPU cycles via CIA timer
  deriving Repr

-- Frequency table. Standard PAL has 96 entries (pitch 0-95). Songs may
-- include extra extended slots (96+) which can be either static values or
-- dynamic feeds (see engineQuirks.dynamicFreqEntries).
structure USFFreqTable where
  entries : List (USFByte × USFByte)  -- (lo, hi) pairs
  deriving Repr

structure USFSong where
  freqTable    : USFFreqTable
  instruments  : List USFInstrument
  voices       : List USFVoice         -- length 1-3 (which SID voices used)
  patterns     : List USFPattern
  voiceOrder   : List (Fin 3)          -- processing order (e.g., [2,1,0])
  filter       : Option USFFilterSpec  -- if Some: filter is active
  playRate     : USFPlayRate           -- VBI or CIA timer
  engineQuirks : USFEngineQuirks := {} -- engine-specific state/dynamic-table behaviors
  -- Metadata
  title        : String
  author       : String
  released     : String
  deriving Repr
