/-
  Compile.lean — Main compilation loop: Song → SongStream
-/

import SID
import State
import Effects

def noteLoad (song : Song) (voice : Fin 3) (vs : VoiceState) (es : EngineState) :
    FrameStream × VoiceState := sorry

def evalFrame (song : Song) (voice : Fin 3) (vs : VoiceState) (es : EngineState) :
    FrameStream × VoiceState := sorry

def processVoice (song : Song) (voice : Fin 3) (vs : VoiceState) (es : EngineState) :
    FrameStream × VoiceState :=
  if vs.tickCtr == 0 then noteLoad song voice vs es
  else evalFrame song voice vs es

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

def compileFrames (song : Song) (nFrames : Nat) : SongStream :=
  let initState := EngineState.init song.instruments.length
  let (stream, _) := (List.range nFrames).foldl
    (fun (acc : SongStream × EngineState) _ =>
      let (prevStream, es) := acc
      let (frameWrites, newEs) := processFrame song es
      (prevStream ++ [frameWrites], newEs))
    ([], initState)
  stream
