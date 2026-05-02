/-
  Compile.lean — Main compilation loop: Song → SongStream

  The compiler is a pure state machine stepping one frame at a time.
  Each frame processes voices in the specified order, producing an
  ordered list of SID register writes — the instruction stream.
-/

import SID
import State
import Effects

-- Helper: get instrument with a safe default
private def getInst (song : Song) (idx : Nat) : Instrument :=
  match song.instruments[idx]? with
  | some i => i
  | none => {
    waveform := [⟨0, by omega⟩], waveLoop := 0,
    effectChain := { vibrato := none, freqSlide := none, arpeggio := none },
    pw := { mode := .linear, speed := ⟨0, by omega⟩,
            minHi := ⟨0, by omega⟩, maxHi := ⟨0, by omega⟩, period := ⟨0, by omega⟩ },
    hardRestart := { gateOffFrames := 3, adsrZeroFrame := 0 },
    ad := ⟨0, by omega⟩, sr := ⟨0, by omega⟩,
    writeOrder := .freqCtrlPwAdsr, digi := none }

-- Helper: get pattern
private def getPat (song : Song) (idx : Nat) : Pattern :=
  match song.patterns[idx]? with
  | some p => p
  | none => { notes := [] }

-- Helper: get voice spec
private def getVoice (song : Song) (idx : Fin 3) : Voice :=
  match song.voices[idx.val]? with
  | some v => v
  | none => { orderlist := [], loopPoint := none }

/-
  Note load: read next note from pattern, produce the note-on writes.
  Write order: freq → ctrl → pw → adsr (configurable per instrument).
  This is the ONLY path that writes ADSR and sets gate ON.
-/
def noteLoad (song : Song) (voice : Fin 3) (vs : VoiceState) (_es : EngineState) :
    FrameStream × VoiceState :=
  let voiceSpec := getVoice song voice
  -- Get current pattern from orderlist
  let patIdx := match voiceSpec.orderlist[vs.patIdx]? with
    | some i => i
    | none => 0
  let pattern := getPat song patIdx
  -- Get current note
  match pattern.notes[vs.noteIdx]? with
  | none =>
    -- End of pattern: advance orderlist, reset note index
    let newPatIdx := vs.patIdx + 1
    -- TODO: handle orderlist loop
    ([], { vs with patIdx := newPatIdx, noteIdx := 0, tickCtr := 1, hubOff := 0 })
  | some note =>
    let inst := getInst song note.instrument
    let (flo, fhi) := lookupFreq song note.pitch.val
    let tickCtr := note.duration.val * song.tickLength
    let ctrl := inst.waveform.head?.getD ⟨0, by omega⟩
    -- Determine PW from shared mutable table (or init value)
    let pwLo := match _es.pwLive[note.instrument]? with
      | some v => v
      | none => ⟨0, by omega⟩
    -- Build writes in Hubbard order: freq → ctrl → pw → adsr
    -- The order IS the music (affects SID ADSR internal state)
    let writes : FrameStream :=
      [ ⟨.freqHi voice, fhi⟩,
        ⟨.freqLo voice, flo⟩,
        ⟨.ctrl voice, ctrl⟩,
        ⟨.pwLo voice, pwLo⟩,
        ⟨.pwHi voice, ⟨0, by omega⟩⟩,
        ⟨.ad voice, inst.ad⟩,
        ⟨.sr voice, inst.sr⟩ ]
    -- Update state
    let newVs : VoiceState :=
      { vs with
        tickCtr := tickCtr,
        noteLen := tickCtr,
        noteIdx := vs.noteIdx + 1,
        wPtr := 0,
        basePitch := note.pitch,
        fhiState := fhi,
        prevInst := some note.instrument }
    (writes, newVs)

/-
  Eval frame: run effects on the current note (sustain frame).
  Effect chain → W program → PW → ADSR zero.
  Effects are SKIPPED on note-load frames (Hubbard behavior).
-/
def evalFrame (song : Song) (voice : Fin 3) (vs : VoiceState) (es : EngineState) :
    FrameStream × VoiceState :=
  let instIdx := vs.prevInst.getD 0
  let inst := getInst song instIdx
  -- Step 1: Effect chain (vibrato → freqSlide → arp)
  -- Each effect independently writes to SID; later overwrites earlier
  let (effectWrites, vs2) := evalEffectChain inst.effectChain voice vs es song inst
  -- Step 2: W program (ctrl/waveform write)
  let wByte := inst.waveform[vs.wPtr]?.getD ⟨0, by omega⟩
  -- Gate off check: clear gate bit near note end
  let gatedByte : Byte :=
    if vs.tickCtr ≤ inst.hardRestart.gateOffFrames
    then ⟨wByte.val / 2 * 2, by omega⟩  -- clear bit 0 (gate)
    else wByte
  let ctrlWrite : SIDWrite := ⟨.ctrl voice, gatedByte⟩
  -- Advance W pointer with loop
  let newWPtr := if vs.wPtr + 1 ≥ inst.waveform.length
    then inst.waveLoop
    else vs.wPtr + 1
  -- Step 3: PW modulation (accumulate then write)
  let isNoteStart := vs.tickCtr == vs.noteLen
  let (pwWrites, vs3) := if isNoteStart then ([], vs2)  -- skip PW on note-start
    else evalPW inst.pw voice vs2
  -- Step 4: ADSR zeroing (hard restart)
  let adsrWrites : List SIDWrite :=
    if vs.tickCtr == inst.hardRestart.gateOffFrames
    then [⟨.ad voice, ⟨0, by omega⟩⟩, ⟨.sr voice, ⟨0, by omega⟩⟩]
    else []
  -- Combine: effect chain → ctrl → PW → ADSR (Hubbard order)
  let allWrites := effectWrites ++ [ctrlWrite] ++ pwWrites ++ adsrWrites
  let vs4 := { vs3 with
    wPtr := newWPtr,
    tickCtr := if vs.tickCtr > 0 then vs.tickCtr - 1 else 0 }
  (allWrites, vs4)

/-
  Process one voice: decide note-load vs eval path.
-/
def processVoice (song : Song) (voice : Fin 3) (vs : VoiceState) (es : EngineState) :
    FrameStream × VoiceState :=
  if vs.tickCtr == 0 then noteLoad song voice vs es
  else evalFrame song voice vs es

/-
  Process one frame: all voices in the specified order.
-/
def processFrame (song : Song) (es : EngineState) : FrameStream × EngineState :=
  let newFrameCtr : Byte := ⟨(es.frameCtr.val + 1) % 256, by omega⟩
  let es1 := { es with frameCtr := newFrameCtr }
  song.voiceOrder.foldl
    (fun (acc : FrameStream × EngineState) voiceIdx =>
      let (prevWrites, curEs) := acc
      let vs := curEs.voices voiceIdx
      let (newWrites, newVs) := processVoice song voiceIdx vs curEs
      let updatedEs := { curEs with
        voices := fun v => if v == voiceIdx then newVs else curEs.voices v }
      (prevWrites ++ newWrites, updatedEs))
    ([], es1)

/-
  THE MAIN COMPILE FUNCTION.
  Song × frame count → complete instruction stream.
  Pure, deterministic, total (for finite nFrames).
-/
def compileFrames (song : Song) (nFrames : Nat) : SongStream :=
  let initState := EngineState.init song.instruments.length
  let (stream, _) := (List.range nFrames).foldl
    (fun (acc : SongStream × EngineState) _ =>
      let (prevStream, es) := acc
      let (frameWrites, newEs) := processFrame song es
      (prevStream ++ [frameWrites], newEs))
    ([], initState)
  stream
