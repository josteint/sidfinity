/-
  Effects.lean — Effect evaluation for Das Model compiler.
-/

import SID
import State

def lookupFreq (song : Song) (pitch : Nat) : Byte × Byte :=
  match song.freqTable.entries[pitch]? with
  | some pair => pair
  | none => (⟨0, by omega⟩, ⟨0, by omega⟩)

def byteAdd (a b : Byte) : Byte := ⟨(a.val + b.val) % 256, by omega⟩
def byteSub (a b : Byte) : Byte := ⟨(a.val + 256 - b.val) % 256, by omega⟩

def triangleLFO (period : Nat) (frame : Nat) : Nat :=
  if period == 0 then 0
  else
    let phase := frame % period
    let half := period / 2
    if phase < half then phase else period - 1 - phase

def evalVibrato (spec : VibratoSpec) (voice : Fin 3) (vs : VoiceState)
    (es : EngineState) (song : Song) : List SIDWrite := sorry

def evalFreqSlide (_spec : FreqSlideSpec) (voice : Fin 3) (vs : VoiceState)
    (_inst : Instrument) : List SIDWrite × VoiceState := sorry

def evalArpeggio (spec : ArpSpec) (voice : Fin 3) (vs : VoiceState)
    (es : EngineState) (song : Song) : List SIDWrite := sorry

def evalPW (spec : PWSpec) (voice : Fin 3) (vs : VoiceState) :
    List SIDWrite × VoiceState := sorry

def evalEffectChain (chain : EffectChain) (voice : Fin 3) (vs : VoiceState)
    (es : EngineState) (song : Song) (inst : Instrument) :
    List SIDWrite × VoiceState :=
  let vibWrites := match chain.vibrato with
    | some spec => evalVibrato spec voice vs es song
    | none => []
  let (slideWrites, vs2) := match chain.freqSlide with
    | some spec => evalFreqSlide spec voice vs inst
    | none => ([], vs)
  let arpWrites := match chain.arpeggio with
    | some spec => evalArpeggio spec voice vs2 es song
    | none => []
  (vibWrites ++ slideWrites ++ arpWrites, vs2)
