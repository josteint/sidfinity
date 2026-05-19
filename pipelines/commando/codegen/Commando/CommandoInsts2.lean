/-
  CommandoInsts2.lean — hand-encoded versions of all 13 Commando
  instruments in the USF2 schema (Phase 1.4 reality check).

  Source of truth: the existing typed-fields `cv3I0 .. cv3I12` literals
  in `SongData.lean`, hand-translated to USF2 events.

  Goal: discover where the new schema is incomplete or awkward BEFORE
  writing extractor / codegen. Lessons learned go into the phase log
  in `docs/usf_instrument_program_plan.md`.

  NOTE: 12 of the 13 instruments below are melodic (no cross-voice
  references). Commando's "noise drum" (the percussion case) is
  realised in patterns via `.percussion .dynamicCtrl` events
  hardcoded to pitch 104 in the current codegen — there is no
  dedicated `cv3I_drum`. The drum's behavior gets handled in Phase 5
  via `otherVoiceCtrl` events on a synthesised drum instrument; we
  defer it until then.
-/

import Commando.USF2

namespace USF2

-- Shorthands so the event literals stay readable.

private def F (n : Nat) : EventTrigger := .atFrame n
private def E (n : Nat) : EventTrigger := .everyFrameFrom n
private def H (n : Nat) : EventTrigger := .atFrameBeforeNoteEnd n

private def C (b : Nat) : InstSource := .const b.toUInt8

private def tri (period depth onset : Nat) : USFVibSpec :=
  { period := period, depth := depth, onset := onset, shape := .triangle }

private def slide (delta : Int) (startDelay : Nat) (stopAtZero : Bool := true)
    : USFFreqSlideSpec :=
  { delta := delta, startDelay := startDelay, stopAtZero := stopAtZero }

private def arp (intervals : List Int) (stepEvery startDelay : Nat) : USFArpSpec :=
  { intervals := intervals, stepEvery := stepEvery, startDelay := startDelay }

/-- Helper: emit the standard one-shot init block (ctrl, pw, ad, sr)
    at frame 0, plus the HR triple at `framesBeforeEnd` frames before
    note end. `hrCtrl` is what `initCtrl & $FE` evaluates to (caller
    precomputes; for ctrl=$41 it's $40; for noise ctrl=$80 it stays $80). -/
private def initFrameAndHR
    (initCtrl initPwLo initPwHi ad sr : Nat)
    (hrCtrl : Nat) (hrThreshold : Nat) : List FrameEvent :=
  [ ⟨F 0, .ctrl,  C initCtrl⟩,
    ⟨F 0, .pwLo,  C initPwLo⟩,
    ⟨F 0, .pwHi,  C initPwHi⟩,
    ⟨F 0, .ad,    C ad⟩,
    ⟨F 0, .sr,    C sr⟩,
    ⟨H hrThreshold, .ctrl, C hrCtrl⟩,
    ⟨H hrThreshold, .ad,   C 0⟩,
    ⟨H hrThreshold, .sr,   C 0⟩,
  ]

-- ============================================================================
-- Inst 0 — pulse + vibrato (triangle period=8 depth=3 onset=6) + bidirectional PWM
-- ctrl=$41, pw=$0900, AD=$29 SR=$5F, HR threshold=3, HR ctrl=$41&$FE=$40
-- ============================================================================
def cv3I0_v2 : USFInstrument2 := {
  events :=
    initFrameAndHR 0x41 0x00 0x09 0x29 0x5F 0x40 3
    ++ [
      ⟨E 0, .freqLo, .pitchFreqLo { vibrato := some (tri 8 3 6) }⟩,
      ⟨E 0, .freqHi, .pitchFreqHi { vibrato := some (tri 8 3 6) }⟩,
      ⟨E 0, .pwHi,   .pulseModHi  { mode := .bidirectional 0x08 0x0E 0xE0 }⟩,
    ]
}

-- ============================================================================
-- Inst 1 — pulse with waveform program + arp + freqSlide
-- ctrl progression: [$41, $80, $80, $80, $40] loop=4
-- pw=$0180 AD=$06 SR=$4B
-- freqSlide -1 startDelay 9 stopAtZero
-- arpeggio [0,12] stepEvery=1
-- ============================================================================
def cv3I1_v2 : USFInstrument2 := {
  events := [
    ⟨F 0, .pwLo, C 0x80⟩, ⟨F 0, .pwHi, C 0x01⟩,
    ⟨F 0, .ad,   C 0x06⟩, ⟨F 0, .sr,   C 0x4B⟩,
    ⟨E 0, .ctrl, .waveProgStep { program := #[0x41, 0x80, 0x80, 0x80, 0x40].toList,
                                  loop := 4, stepEvery := 1 }⟩,
    -- freq with freqSlide + arp
    ⟨E 0, .freqLo, .pitchFreqLo { freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨E 0, .freqHi, .pitchFreqHi { freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    -- HR — note: HR ctrl = LAST waveform step ($40), gate already clear.
    -- No need to write ctrl at HR since waveform program has us at $40 already;
    -- the AD/SR=0 zeroing is what matters.
    ⟨H 3, .ad, C 0⟩, ⟨H 3, .sr, C 0⟩,
  ]
}

-- ============================================================================
-- Inst 2 — pulse + linear PWM (speed=22)
-- ctrl=$41 pw=$0180 AD=$09 SR=$9F
-- ============================================================================
def cv3I2_v2 : USFInstrument2 := {
  events :=
    initFrameAndHR 0x41 0x80 0x01 0x09 0x9F 0x40 3
    ++ [
      ⟨E 0, .pwHi, .pulseModHi { mode := .linear 0x16 }⟩,
    ]
}

-- ============================================================================
-- Inst 3 — noise + waveform program + freqSlide + arpeggio
-- ctrl=$81 (noise) pw=$0200 AD=$0A SR=$09
-- waveformProgram=[$81, $80, $80, $80, $80] loop=4
-- ============================================================================
def cv3I3_v2 : USFInstrument2 := {
  events := [
    ⟨F 0, .pwLo, C 0x00⟩, ⟨F 0, .pwHi, C 0x02⟩,
    ⟨F 0, .ad,   C 0x0A⟩, ⟨F 0, .sr,   C 0x09⟩,
    ⟨E 0, .ctrl, .waveProgStep { program := #[0x81, 0x80, 0x80, 0x80, 0x80].toList,
                                  loop := 4, stepEvery := 1 }⟩,
    ⟨E 0, .freqLo, .pitchFreqLo { freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨E 0, .freqHi, .pitchFreqHi { freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨H 3, .ad, C 0⟩, ⟨H 3, .sr, C 0⟩,
  ]
}

-- ============================================================================
-- Inst 4 — pulse+triangle ($43) wave program + freqSlide
-- ctrl=$43 pw=$0200 AD=$0F SR=$C4
-- ============================================================================
def cv3I4_v2 : USFInstrument2 := {
  events := [
    ⟨F 0, .pwLo, C 0x00⟩, ⟨F 0, .pwHi, C 0x02⟩,
    ⟨F 0, .ad,   C 0x0F⟩, ⟨F 0, .sr,   C 0xC4⟩,
    ⟨E 0, .ctrl, .waveProgStep { program := #[0x43, 0x80, 0x80, 0x80, 0x42].toList,
                                  loop := 4, stepEvery := 1 }⟩,
    ⟨E 0, .freqLo, .pitchFreqLo { freqSlide := some (slide (-1) 9) }⟩,
    ⟨E 0, .freqHi, .pitchFreqHi { freqSlide := some (slide (-1) 9) }⟩,
    ⟨H 3, .ad, C 0⟩, ⟨H 3, .sr, C 0⟩,
  ]
}

-- ============================================================================
-- Inst 5 — pulse + wave program + linear PWM + freqSlide + arp
-- ctrl=$41 pw=$0880 AD=$05 SR=$A9
-- ============================================================================
def cv3I5_v2 : USFInstrument2 := {
  events := [
    ⟨F 0, .pwLo, C 0x80⟩, ⟨F 0, .pwHi, C 0x08⟩,
    ⟨F 0, .ad,   C 0x05⟩, ⟨F 0, .sr,   C 0xA9⟩,
    ⟨E 0, .ctrl, .waveProgStep { program := #[0x41, 0x80, 0x80, 0x80, 0x40].toList,
                                  loop := 4, stepEvery := 1 }⟩,
    ⟨E 0, .pwHi,  .pulseModHi { mode := .linear 0x02 }⟩,
    ⟨E 0, .freqLo, .pitchFreqLo { freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨E 0, .freqHi, .pitchFreqHi { freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨H 3, .ad, C 0⟩, ⟨H 3, .sr, C 0⟩,
  ]
}

-- ============================================================================
-- Inst 6 — like inst 0 but different AD/SR; bidirectional PWM + vibrato
-- ctrl=$41 pw=$0800 AD=$38 SR=$7A
-- ============================================================================
def cv3I6_v2 : USFInstrument2 := {
  events :=
    initFrameAndHR 0x41 0x00 0x08 0x38 0x7A 0x40 3
    ++ [
      ⟨E 0, .freqLo, .pitchFreqLo { vibrato := some (tri 8 3 6) }⟩,
      ⟨E 0, .freqHi, .pitchFreqHi { vibrato := some (tri 8 3 6) }⟩,
      ⟨E 0, .pwHi,   .pulseModHi  { mode := .bidirectional 0x08 0x0E 0xE0 }⟩,
    ]
}

-- ============================================================================
-- Inst 7 — wave program + vibrato + freqSlide + arp (ctrl=$15 triangle+ring)
-- pw=$0180 AD=$0D SR=$FB, vibrato depth=2
-- ============================================================================
def cv3I7_v2 : USFInstrument2 := {
  events := [
    ⟨F 0, .pwLo, C 0x80⟩, ⟨F 0, .pwHi, C 0x01⟩,
    ⟨F 0, .ad,   C 0x0D⟩, ⟨F 0, .sr,   C 0xFB⟩,
    ⟨E 0, .ctrl, .waveProgStep { program := #[0x15, 0x80, 0x80, 0x80, 0x14].toList,
                                  loop := 4, stepEvery := 1 }⟩,
    ⟨E 0, .freqLo, .pitchFreqLo { vibrato   := some (tri 8 2 6),
                                   freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨E 0, .freqHi, .pitchFreqHi { vibrato   := some (tri 8 2 6),
                                   freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨H 3, .ad, C 0⟩, ⟨H 3, .sr, C 0⟩,
  ]
}

-- ============================================================================
-- Inst 8 — pulse + linear PWM + vibrato (no waveform program looping)
-- ctrl=$41 pw=$0800 AD=$49 SR=$5B vibrato depth=3
-- ============================================================================
def cv3I8_v2 : USFInstrument2 := {
  events :=
    initFrameAndHR 0x41 0x00 0x08 0x49 0x5B 0x40 3
    ++ [
      ⟨E 0, .freqLo, .pitchFreqLo { vibrato := some (tri 8 3 6) }⟩,
      ⟨E 0, .freqHi, .pitchFreqHi { vibrato := some (tri 8 3 6) }⟩,
      ⟨E 0, .pwHi,   .pulseModHi  { mode := .linear 0x03 }⟩,
    ]
}

-- ============================================================================
-- Inst 9 — sawtooth+ring ($21) wave program + vibrato + freqSlide + arp
-- pw=$0800 AD=$04 SR=$6F vibrato depth=4
-- ============================================================================
def cv3I9_v2 : USFInstrument2 := {
  events := [
    ⟨F 0, .pwLo, C 0x00⟩, ⟨F 0, .pwHi, C 0x08⟩,
    ⟨F 0, .ad,   C 0x04⟩, ⟨F 0, .sr,   C 0x6F⟩,
    ⟨E 0, .ctrl, .waveProgStep { program := #[0x21, 0x80, 0x80, 0x80, 0x20].toList,
                                  loop := 4, stepEvery := 1 }⟩,
    ⟨E 0, .freqLo, .pitchFreqLo { vibrato   := some (tri 8 4 6),
                                   freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨E 0, .freqHi, .pitchFreqHi { vibrato   := some (tri 8 4 6),
                                   freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨H 3, .ad, C 0⟩, ⟨H 3, .sr, C 0⟩,
  ]
}

-- ============================================================================
-- Inst 10 — full ensemble: wave program + linear PWM + vibrato + freqSlide + arp
-- ctrl=$41 pw=$0300 AD=$09 SR=$6B
-- ============================================================================
def cv3I10_v2 : USFInstrument2 := {
  events := [
    ⟨F 0, .pwLo, C 0x00⟩, ⟨F 0, .pwHi, C 0x03⟩,
    ⟨F 0, .ad,   C 0x09⟩, ⟨F 0, .sr,   C 0x6B⟩,
    ⟨E 0, .ctrl, .waveProgStep { program := #[0x41, 0x80, 0x80, 0x80, 0x40].toList,
                                  loop := 4, stepEvery := 1 }⟩,
    ⟨E 0, .pwHi,  .pulseModHi { mode := .linear 0x01 }⟩,
    ⟨E 0, .freqLo, .pitchFreqLo { vibrato   := some (tri 8 3 6),
                                   freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨E 0, .freqHi, .pitchFreqHi { vibrato   := some (tri 8 3 6),
                                   freqSlide := some (slide (-1) 9),
                                   arpeggio  := some (arp [0, 12] 1 0) }⟩,
    ⟨H 3, .ad, C 0⟩, ⟨H 3, .sr, C 0⟩,
  ]
}

-- ============================================================================
-- Inst 11 — pulse+triangle ($43) wave program + vibrato + freqSlide (no arp)
-- pw=$0200 AD=$07 SR=$09 vibrato depth=2
-- ============================================================================
def cv3I11_v2 : USFInstrument2 := {
  events := [
    ⟨F 0, .pwLo, C 0x00⟩, ⟨F 0, .pwHi, C 0x02⟩,
    ⟨F 0, .ad,   C 0x07⟩, ⟨F 0, .sr,   C 0x09⟩,
    ⟨E 0, .ctrl, .waveProgStep { program := #[0x43, 0x80, 0x80, 0x80, 0x42].toList,
                                  loop := 4, stepEvery := 1 }⟩,
    ⟨E 0, .freqLo, .pitchFreqLo { vibrato   := some (tri 8 2 6),
                                   freqSlide := some (slide (-1) 9) }⟩,
    ⟨E 0, .freqHi, .pitchFreqHi { vibrato   := some (tri 8 2 6),
                                   freqSlide := some (slide (-1) 9) }⟩,
    ⟨H 3, .ad, C 0⟩, ⟨H 3, .sr, C 0⟩,
  ]
}

-- ============================================================================
-- Inst 12 — pulse wave program + freqSlide only (no vibrato, no arp, no PWM)
-- ctrl=$41 pw=$0800 AD=$09 SR=$0A
-- ============================================================================
def cv3I12_v2 : USFInstrument2 := {
  events := [
    ⟨F 0, .pwLo, C 0x00⟩, ⟨F 0, .pwHi, C 0x08⟩,
    ⟨F 0, .ad,   C 0x09⟩, ⟨F 0, .sr,   C 0x0A⟩,
    ⟨E 0, .ctrl, .waveProgStep { program := #[0x41, 0x80, 0x80, 0x80, 0x40].toList,
                                  loop := 4, stepEvery := 1 }⟩,
    ⟨E 0, .freqLo, .pitchFreqLo { freqSlide := some (slide (-1) 9) }⟩,
    ⟨E 0, .freqHi, .pitchFreqHi { freqSlide := some (slide (-1) 9) }⟩,
    ⟨H 3, .ad, C 0⟩, ⟨H 3, .sr, C 0⟩,
  ]
}

-- ============================================================================
-- All 13 collected. Reality check: do they compile?
-- ============================================================================
def allCommandoInsts2 : List USFInstrument2 :=
  [cv3I0_v2,  cv3I1_v2,  cv3I2_v2,  cv3I3_v2,  cv3I4_v2,  cv3I5_v2,
   cv3I6_v2,  cv3I7_v2,  cv3I8_v2,  cv3I9_v2,  cv3I10_v2, cv3I11_v2,
   cv3I12_v2]

end USF2
