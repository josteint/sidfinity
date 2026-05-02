/-
  Compile.lean — Main compilation loop: Song → SongStream

  This is the core of Das Model v2. It transforms a universal Song
  description into the exact instruction stream that drives the SID chip.

  The compilation is a pure state machine, stepping one frame at a time.
  Each frame processes all voices in the specified order, producing
  an ordered list of SID register writes.
-/

import «SID»
import «State»
import «Effects»

/-
  Note load: read next note from pattern, set up voice state,
  produce the instruction stream for the note-on event.

  Write order is specified per instrument (part of the behavioral spec).
-/
def noteLoad (song : Song) (voice : Fin 3) (vs : VoiceState) (es : EngineState) :
    FrameStream × VoiceState :=
  -- Get the voice's pattern sequence
  let voiceSpec := song.voices.get? voice.val |>.getD { orderlist := [], loopPoint := none }
  -- Get current pattern index from orderlist
  let patternIdx := voiceSpec.orderlist.get? vs.patIdx |>.getD 0
  -- Get the pattern
  let pattern := song.patterns.get? patternIdx |>.getD { notes := [] }
  -- Get the current note
  match pattern.notes.get? vs.noteIdx with
  | none =>
    -- End of pattern: advance to next pattern in orderlist
    let newPatIdx := vs.patIdx + 1
    -- TODO: handle orderlist wrap/loop
    ([], { vs with patIdx := newPatIdx, noteIdx := 0, tickCtr := 1, hubOff := 0 })
  | some note =>
    -- Load the note
    let inst := song.instruments.get? note.instrument |>.getD {
      waveform := [], waveLoop := 0, effectChain := { vibrato := none, freqSlide := none, arpeggio := none },
      pw := { mode := .linear, speed := ⟨0, by omega⟩, minHi := ⟨0, by omega⟩, maxHi := ⟨0, by omega⟩, period := ⟨0, by omega⟩ },
      hardRestart := { gateOffFrames := 3, adsrZeroFrame := 0 },
      ad := ⟨0, by omega⟩, sr := ⟨0, by omega⟩,
      writeOrder := .freqCtrlPwAdsr, digi := none }
    let (flo, fhi) := lookupFreq song note.pitch
    let tickCtr := note.duration.val * song.tickLength
    let ctrl := inst.waveform.head?.getD ⟨0, by omega⟩
    -- Determine PW: from shared mutable table if same instrument was used before
    let pwLo := match es.pwLive.get? note.instrument with
      | some v => v
      | none => inst.pw.speed  -- fallback
    -- Build writes in the specified order
    let writes : FrameStream := match inst.writeOrder with
      | .freqCtrlPwAdsr =>
        [ ⟨.freqHi voice, fhi⟩, ⟨.freqLo voice, flo⟩,
          ⟨.ctrl voice, ctrl⟩,
          ⟨.pwLo voice, pwLo⟩, ⟨.pwHi voice, ⟨0, by omega⟩⟩,
          ⟨.ad voice, inst.ad⟩, ⟨.sr voice, inst.sr⟩ ]
      | _ =>
        -- Other orders (for future engines)
        [ ⟨.freqHi voice, fhi⟩, ⟨.freqLo voice, flo⟩,
          ⟨.ctrl voice, ctrl⟩,
          ⟨.ad voice, inst.ad⟩, ⟨.sr voice, inst.sr⟩ ]
    -- Update voice state
    let newVs : VoiceState :=
      { vs with
        tickCtr := tickCtr
        noteLen := tickCtr
        noteIdx := vs.noteIdx + 1
        wPtr := 0
        basePitch := note.pitch
        fhiState := fhi
        prevInst := some note.instrument
      }
    (writes, newVs)

/-
  Eval frame: run effects, W program, PW, ADSR for a sustain frame.
  This is where the multi-write effect chain produces intermediate SID writes.
-/
def evalFrame (song : Song) (voice : Fin 3) (vs : VoiceState) (es : EngineState) :
    FrameStream × VoiceState :=
  let instIdx := vs.prevInst.getD 0
  let inst := song.instruments.get? instIdx |>.getD {
    waveform := [], waveLoop := 0, effectChain := { vibrato := none, freqSlide := none, arpeggio := none },
    pw := { mode := .linear, speed := ⟨0, by omega⟩, minHi := ⟨0, by omega⟩, maxHi := ⟨0, by omega⟩, period := ⟨0, by omega⟩ },
    hardRestart := { gateOffFrames := 3, adsrZeroFrame := 0 },
    ad := ⟨0, by omega⟩, sr := ⟨0, by omega⟩,
    writeOrder := .freqCtrlPwAdsr, digi := none }
  -- Step 1: Effect chain (vibrato → freqSlide → arp)
  let (effectWrites, vs2) := evalEffectChain inst.effectChain voice vs es song inst
  -- Step 2: W program (ctrl write)
  let wByte := inst.waveform.get? vs.wPtr |>.getD ⟨0, by omega⟩
  -- Gate off check: clear gate bit if near note end
  let gatedByte : Byte :=
    if vs.tickCtr ≤ inst.hardRestart.gateOffFrames
    then ⟨wByte.val &&& 0xFE, by omega⟩  -- clear gate
    else wByte
  let ctrlWrite : SIDWrite := ⟨.ctrl voice, gatedByte⟩
  -- Advance W pointer (with loop)
  let newWPtr := if vs.wPtr + 1 ≥ inst.waveform.length
    then inst.waveLoop
    else vs.wPtr + 1
  -- Step 3: PW modulation
  let (pwWrites, vs3) := evalPW inst.pw voice vs2
  -- Step 4: ADSR zeroing (hard restart)
  let adsrWrites : List SIDWrite :=
    if vs.tickCtr == inst.hardRestart.gateOffFrames
    then [⟨.ad voice, ⟨0, by omega⟩⟩, ⟨.sr voice, ⟨0, by omega⟩⟩]
    else []
  -- Combine all writes
  let allWrites := effectWrites ++ [ctrlWrite] ++ pwWrites ++ adsrWrites
  let vs4 := { vs3 with wPtr := newWPtr, tickCtr := vs.tickCtr - 1 }
  (allWrites, vs4)

/-
  Process one voice for one frame.
  Decides between note-load path and eval path.
-/
def processVoice (song : Song) (voice : Fin 3) (vs : VoiceState) (es : EngineState) :
    FrameStream × VoiceState :=
  if vs.tickCtr == 0 then
    -- Note load: read next note, set up state, produce note-on writes
    noteLoad song voice vs es
  else
    -- Eval: run effects on current note
    evalFrame song voice vs es

/-
  Process one frame: all voices in order.
  Returns the combined FrameStream and updated EngineState.
-/
def processFrame (song : Song) (es : EngineState) : FrameStream × EngineState :=
  -- Increment global frame counter
  let newFrameCtr : Byte := ⟨(es.frameCtr.val + 1) % 256, by omega⟩
  let es1 := { es with frameCtr := newFrameCtr }
  -- Process each voice in the specified order
  let (writes, finalEs) := song.voiceOrder.foldl
    (fun (acc : FrameStream × EngineState) voiceIdx =>
      let (prevWrites, curEs) := acc
      let vs := curEs.voices voiceIdx
      let (newWrites, newVs) := processVoice song voiceIdx vs curEs
      let updatedEs := { curEs with
        voices := fun v => if v == voiceIdx then newVs else curEs.voices v }
      (prevWrites ++ newWrites, updatedEs))
    ([], es1)
  (writes, finalEs)

/-
  THE MAIN COMPILE FUNCTION.
  Generates the complete instruction stream for a song.
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

end
