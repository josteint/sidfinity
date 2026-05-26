/-
  Effects.lean — Effect evaluation for Das Model compiler.

  Each effect is a pure function producing SID writes + updated state.
  Effects write to SID independently. Later effects overwrite earlier ones.
  The chain order is part of the instrument specification.
-/

import SID
import State

-- Helper: look up frequency from table
def lookupFreq (song : Song) (pitch : Nat) : Byte × Byte :=
  match song.freqTable.entries[pitch]? with
  | some pair => pair
  | none => (⟨0, by omega⟩, ⟨0, by omega⟩)

-- Helper: byte arithmetic (wrapping)
def byteAdd (a b : Byte) : Byte := ⟨(a.val + b.val) % 256, by omega⟩
def byteSub (a b : Byte) : Byte := ⟨(a.val + 256 - b.val) % 256, by omega⟩

-- Triangle LFO: 0,1,2,...,n-1,n-1,...,1,0 over `period` frames
def triangleLFO (period : Nat) (frame : Nat) : Nat :=
  if period == 0 then 0
  else
    let phase := frame % period
    let half := period / 2
    if phase < half then phase else period - 1 - phase

/-
  Vibrato: modulate frequency with LFO.
  Full 16-bit computation: delta = freq[pitch+1] - freq[pitch],
  right-shifted (depthShift+1) times, multiplied by LFO depth.
  Writes freq_lo and freq_hi to SID (intermediate write).
-/
def evalVibrato (spec : VibratoSpec) (voice : Fin 3) (vs : VoiceState)
    (es : EngineState) (song : Song) : List SIDWrite :=
  -- Check onset delay
  let framesElapsed := if vs.noteLen ≥ vs.tickCtr then vs.noteLen - vs.tickCtr else 0
  if framesElapsed < spec.onset then []
  else
    let depth := triangleLFO spec.period es.frameCtr.val
    let (flo, fhi) := lookupFreq song vs.basePitch.val
    if depth == 0 then
      -- LFO at zero: write unmodulated base frequency
      [⟨.freqLo voice, flo⟩, ⟨.freqHi voice, fhi⟩]
    else
      -- Compute semitone delta (16-bit)
      let (flo1, fhi1) := lookupFreq song (vs.basePitch.val + 1)
      let baseFreq := fhi.val * 256 + flo.val
      let nextFreq := fhi1.val * 256 + flo1.val
      let delta := if nextFreq ≥ baseFreq then nextFreq - baseFreq else 0
      -- Right-shift by depthShift+1 (Hubbard's DEC/BPL includes zero iteration)
      let shifted := delta / (2 ^ (spec.depthShift + 1))
      -- Multiply by LFO depth and add to base
      let modFreq := baseFreq + shifted * depth
      let modFhi : Byte := ⟨(modFreq / 256) % 256, by omega⟩
      let modFlo : Byte := ⟨modFreq % 256, by omega⟩
      [⟨.freqLo voice, modFlo⟩, ⟨.freqHi voice, modFhi⟩]

/-
  Frequency slide (bit0/skydive): DEC freq_hi state each frame.
  Writes OLD freq_hi to SID, then decrements state for next frame.
  Also writes ctrl with gate cleared.
-/
def evalFreqSlide (_spec : FreqSlideSpec) (voice : Fin 3) (vs : VoiceState)
    (inst : Instrument) : List SIDWrite × VoiceState :=
  if vs.fhiState.val == 0 then ([], vs)
  else
    -- Write OLD freq_hi state to SID
    let ctrlByte := inst.waveform.head?.getD ⟨0, by omega⟩
    let ctrlNoGate : Byte := ⟨ctrlByte.val % 256 / 2 * 2, by omega⟩  -- clear bit 0
    let writes : List SIDWrite :=
      [⟨.freqHi voice, vs.fhiState⟩, ⟨.ctrl voice, ctrlNoGate⟩]
    -- DEC freq_hi state (wrapping)
    let newFhi : Byte := ⟨(vs.fhiState.val + 255) % 256, by omega⟩
    (writes, { vs with fhiState := newFhi })

/-
  Arpeggio: alternate frequency between intervals each frame.
  Uses global frame counter (Hubbard) or per-voice counter.
  Writes freq_hi and freq_lo to SID (overwrites vibrato + slide).
-/
def evalArpeggio (spec : ArpSpec) (voice : Fin 3) (vs : VoiceState)
    (es : EngineState) (song : Song) : List SIDWrite :=
  if spec.intervals.isEmpty then []
  else
    -- Determine phase from counter source
    let phase := match spec.phase with
      | .global => es.frameCtr.val
      | .perVoice => vs.tickCtr
    -- Select interval based on phase
    let idx := if spec.rate == 0 then 0
               else (phase / spec.rate) % spec.intervals.length
    let interval := match spec.intervals[idx]? with
      | some i => i
      | none => 0
    -- Apply interval to base pitch
    let arpPitch := ((vs.basePitch.val : Int) + interval).toNat % 256
    let (flo, fhi) := lookupFreq song arpPitch
    [⟨.freqHi voice, fhi⟩, ⟨.freqLo voice, flo⟩]

/-
  PW modulation: sweep pulse width per frame.
  Accumulate-then-write order (Hubbard behavior).
  Linear: pw_lo += speed, 8-bit wrap.
  Bidirectional: bounce between minHi and maxHi, exact equality flip.
-/
def evalPW (spec : PWSpec) (voice : Fin 3) (vs : VoiceState) :
    List SIDWrite × VoiceState :=
  if spec.speed.val == 0 then ([], vs)
  else match spec.mode with
  | .linear =>
    let newLo := byteAdd vs.pwLo spec.speed
    let writes := [⟨.pwLo voice, newLo⟩, ⟨.pwHi voice, vs.pwHi⟩]
    (writes, { vs with pwLo := newLo })
  | .bidirectional =>
    if vs.pwDir then
      -- Down: subtract speed (16-bit)
      let borrow := vs.pwLo.val < spec.speed.val
      let newLo := byteSub vs.pwLo spec.speed
      let newHi : Byte := if borrow
        then ⟨(vs.pwHi.val + 255) % 256, by omega⟩
        else vs.pwHi
      -- Flip at exact min boundary (Hubbard uses BNE)
      let flip := newHi.val == spec.minHi.val
      let writes := [⟨.pwLo voice, newLo⟩, ⟨.pwHi voice, newHi⟩]
      (writes, { vs with pwLo := newLo, pwHi := newHi,
                         pwDir := if flip then false else true })
    else
      -- Up: add speed (16-bit)
      let carry := vs.pwLo.val + spec.speed.val > 255
      let newLo := byteAdd vs.pwLo spec.speed
      let newHi : Byte := if carry
        then ⟨(vs.pwHi.val + 1) % 256, by omega⟩
        else vs.pwHi
      -- Flip at exact max boundary
      let flip := newHi.val == spec.maxHi.val
      let writes := [⟨.pwLo voice, newLo⟩, ⟨.pwHi voice, newHi⟩]
      (writes, { vs with pwLo := newLo, pwHi := newHi,
                         pwDir := if flip then true else false })
  | .table => ([], vs)  -- TODO: table-driven PW

/-
  Run the complete effect chain for one voice on one eval frame.
  Order: vibrato → freqSlide → arpeggio. Each writes to SID independently.
  Later effects overwrite earlier ones (arp overwrites vibrato+slide).
-/
def evalEffectChain (chain : EffectChain) (voice : Fin 3) (vs : VoiceState)
    (es : EngineState) (song : Song) (inst : Instrument) :
    List SIDWrite × VoiceState :=
  -- Step 1: Vibrato (writes freq)
  let vibWrites := match chain.vibrato with
    | some spec => evalVibrato spec voice vs es song
    | none => []
  -- Step 2: Freq slide (writes freq_hi + ctrl, updates fhiState)
  let (slideWrites, vs2) := match chain.freqSlide with
    | some spec => evalFreqSlide spec voice vs inst
    | none => ([], vs)
  -- Step 3: Arpeggio (writes freq, overwrites vibrato + slide)
  let arpWrites := match chain.arpeggio with
    | some spec => evalArpeggio spec voice vs2 es song
    | none => []
  (vibWrites ++ slideWrites ++ arpWrites, vs2)
