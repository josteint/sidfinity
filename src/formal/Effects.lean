/-
  Effects.lean — Effect evaluation for Das Model compiler.

  Each effect is a pure function:
    (EffectSpec, VoiceState, EngineState, Song) → (List SIDWrite, VoiceState)

  Effects write to SID independently. Later effects may overwrite earlier ones.
  The effect CHAIN order is part of the instrument specification.
-/

import «SID»
import «State»

-- Helper: look up frequency from table (handles extended entries)
def lookupFreq (song : Song) (pitch : Byte) : Byte × Byte :=
  match song.freqTable.entries.get? pitch.val with
  | some pair => pair
  | none => (⟨0, by omega⟩, ⟨0, by omega⟩)  -- out of range

-- Helper: byte wrapping arithmetic
def byteAdd (a b : Byte) : Byte := ⟨(a.val + b.val) % 256, by omega⟩
def byteSub (a b : Byte) : Byte := ⟨(a.val + 256 - b.val) % 256, by omega⟩

-- Compute LFO value for a given shape and frame
def lfoValue (shape : LFOShape) (period : Nat) (frame : Nat) : Nat :=
  match shape with
  | .triangle =>
    -- Hubbard triangle: 0,1,2,3,3,2,1,0 for period=8
    let phase := frame % period
    let half := period / 2
    if phase < half then phase else period - 1 - phase
  | .sine => 0      -- TODO: sine table lookup
  | .square =>
    let phase := frame % period
    if phase < period / 2 then 0 else period / 2
  | .sawtooth =>
    frame % period

/-
  Vibrato effect: modulate frequency with LFO

  Writes: freq_lo, freq_hi to SID (intermediate write, may be overwritten by arp)
-/
def evalVibrato (spec : VibratoSpec) (voice : Fin 3) (vs : VoiceState)
    (es : EngineState) (song : Song) : List SIDWrite :=
  -- Check onset: has the note played long enough?
  let framesElapsed := vs.noteLen - vs.tickCtr
  if framesElapsed < spec.onset then []
  else
    -- Compute LFO depth
    let depth := lfoValue spec.shape spec.period es.frameCtr.val
    if depth == 0 then
      -- Depth zero: write unmodulated base frequency
      let (flo, fhi) := lookupFreq song vs.basePitch
      [⟨.freqLo voice, flo⟩, ⟨.freqHi voice, fhi⟩]
    else
      -- Compute semitone delta: freq[pitch+1] - freq[pitch]
      let (flo, fhi) := lookupFreq song vs.basePitch
      let pitch1 : Byte := ⟨(vs.basePitch.val + 1) % 256, by omega⟩
      let (flo1, fhi1) := lookupFreq song pitch1
      -- 16-bit delta (hi:lo), right-shifted depthShift+1 times
      let deltaFull := fhi1.val * 256 + flo1.val - (fhi.val * 256 + flo.val)
      let shifted := deltaFull / (2 ^ (spec.depthShift + 1))
      -- Multiply by depth and add to base
      let modulation := shifted * depth
      let baseFreq := fhi.val * 256 + flo.val
      let modFreq := baseFreq + modulation
      let modFhi : Byte := ⟨(modFreq / 256) % 256, by omega⟩
      let modFlo : Byte := ⟨modFreq % 256, by omega⟩
      [⟨.freqLo voice, modFlo⟩, ⟨.freqHi voice, modFhi⟩]

/-
  Frequency slide effect (bit0/skydive): DEC freq_hi state each frame

  Writes: freq_hi to SID (intermediate write), ctrl with gate cleared
  Updates: fhiState in VoiceState
-/
def evalFreqSlide (spec : FreqSlideSpec) (voice : Fin 3) (vs : VoiceState)
    (inst : Instrument) : List SIDWrite × VoiceState :=
  if vs.fhiState.val == 0 then ([], vs)
  else
    -- Write OLD fhi_state to SID, then decrement
    let writes : List SIDWrite :=
      [⟨.freqHi voice, vs.fhiState⟩,
       -- Write ctrl with gate cleared
       ⟨.ctrl voice, ⟨(inst.waveform.head?.getD ⟨0, by omega⟩).val &&& 0xFE, by omega⟩⟩]
    let newFhi : Byte := ⟨(vs.fhiState.val + 255) % 256, by omega⟩  -- DEC
    (writes, { vs with fhiState := newFhi })

/-
  Arpeggio effect: alternate frequency between intervals

  Writes: freq_lo, freq_hi to SID (overwrites vibrato and freq slide)
-/
def evalArpeggio (spec : ArpSpec) (voice : Fin 3) (vs : VoiceState)
    (es : EngineState) (song : Song) : List SIDWrite :=
  if spec.intervals.isEmpty then []
  else
    -- Determine which interval to use based on phase
    let phase := match spec.phase with
      | .global => es.frameCtr.val
      | .perVoice => vs.tickCtr  -- simplified
    let idx := (phase / spec.rate) % spec.intervals.length
    let interval := spec.intervals.get? idx |>.getD 0
    -- Apply interval to base pitch
    let arpPitch : Byte := ⟨((vs.basePitch.val : Int) + interval).toNat % 256, by omega⟩
    let (flo, fhi) := lookupFreq song arpPitch
    [⟨.freqHi voice, fhi⟩, ⟨.freqLo voice, flo⟩]

/-
  PW modulation: sweep pulse width

  Writes: pw_lo, pw_hi to SID
  Updates: pwLo, pwHi, pwDir, pwPeriod in VoiceState
-/
def evalPW (spec : PWSpec) (voice : Fin 3) (vs : VoiceState) :
    List SIDWrite × VoiceState :=
  if spec.speed.val == 0 then ([], vs)
  else
    match spec.mode with
    | .linear =>
      -- Accumulate first, then write (Hubbard order)
      let newLo := byteAdd vs.pwLo spec.speed
      let writes := [⟨.pwLo voice, newLo⟩, ⟨.pwHi voice, vs.pwHi⟩]
      (writes, { vs with pwLo := newLo })
    | .bidirectional =>
      -- Simplified bidirectional (full version needs period counter)
      if vs.pwDir then
        -- Down: subtract
        let newLo := byteSub vs.pwLo spec.speed
        let borrow := if vs.pwLo.val < spec.speed.val then true else false
        let newHi := if borrow then ⟨(vs.pwHi.val + 255) % 256, by omega⟩ else vs.pwHi
        let flip := newHi.val == spec.minHi.val
        let writes := [⟨.pwLo voice, newLo⟩, ⟨.pwHi voice, newHi⟩]
        (writes, { vs with pwLo := newLo, pwHi := newHi,
                           pwDir := if flip then false else true })
      else
        -- Up: add
        let newLo := byteAdd vs.pwLo spec.speed
        let carry := if vs.pwLo.val + spec.speed.val > 255 then true else false
        let newHi := if carry then ⟨(vs.pwHi.val + 1) % 256, by omega⟩ else vs.pwHi
        let flip := newHi.val == spec.maxHi.val
        let writes := [⟨.pwLo voice, newLo⟩, ⟨.pwHi voice, newHi⟩]
        (writes, { vs with pwLo := newLo, pwHi := newHi,
                           pwDir := if flip then true else false })
    | .table => ([], vs)  -- TODO: table-driven PW

/-
  Run the complete effect chain for one voice on one eval frame.
  Each effect writes to SID independently. Later effects overwrite earlier ones.
  Returns: (all writes, updated voice state)
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

end
