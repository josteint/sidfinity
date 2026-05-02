/-
  Main.lean — Executable entry point for the Das Model compiler.

  Reads a Song from JSON, compiles it to a SongStream, outputs the
  stream as JSON. This allows testing the Lean compiler against
  sidplayfp's ground truth instruction stream.

  Usage:
    lake build
    .lake/build/bin/dasmodel < song.json > stream.json
-/

import SID
import State
import Effects
import Compile

-- Simple JSON-like output for the instruction stream
def streamToString (stream : SongStream) : String :=
  let frameStrs := stream.map fun frame =>
    let writeStrs := frame.map fun w =>
      let regNum : Nat := match w.reg with
        | .freqLo v => v.val * 7
        | .freqHi v => v.val * 7 + 1
        | .pwLo v => v.val * 7 + 2
        | .pwHi v => v.val * 7 + 3
        | .ctrl v => v.val * 7 + 4
        | .ad v => v.val * 7 + 5
        | .sr v => v.val * 7 + 6
        | .filtLo => 21
        | .filtHi => 22
        | .filtCtrl => 23
        | .modeVol => 24
      s!"{regNum}:{w.val.val}"
    "[" ++ ",".intercalate writeStrs ++ "]"
  "[" ++ ",\n".intercalate frameStrs ++ "]"

-- Build a test Song (Commando-like, for quick validation)
def testSong : Song :=
  let freqTable : FreqTable := {
    entries := (List.range 96).map fun i =>
      -- Approximate PAL frequency table
      let freq := (i * 256 + 100) % 65536
      (⟨freq % 256, by omega⟩, ⟨freq / 256 % 256, by omega⟩)
  }
  let inst0 : Instrument := {
    waveform := [⟨0x41, by omega⟩]  -- pulse + gate
    waveLoop := 0
    effectChain := {
      vibrato := none
      freqSlide := none
      arpeggio := some {
        intervals := [0, 12]
        phase := .global
        rate := 1
      }
    }
    pw := { mode := .linear, speed := ⟨0x16, by omega⟩,
            minHi := ⟨0, by omega⟩, maxHi := ⟨0, by omega⟩, period := ⟨0, by omega⟩ }
    hardRestart := { gateOffFrames := 3, adsrZeroFrame := 0 }
    ad := ⟨0x0D, by omega⟩
    sr := ⟨0xFB, by omega⟩
    writeOrder := .freqCtrlPwAdsr
    digi := none
  }
  let pat0 : Pattern := {
    notes := [
      { pitch := ⟨36, by omega⟩, duration := ⟨4, by omega⟩, instrument := 0, tie := false },
      { pitch := ⟨40, by omega⟩, duration := ⟨4, by omega⟩, instrument := 0, tie := false },
      { pitch := ⟨43, by omega⟩, duration := ⟨4, by omega⟩, instrument := 0, tie := false },
    ]
  }
  {
    freqTable := freqTable
    instruments := [inst0]
    voices := [{ orderlist := [0], loopPoint := some 0 }]
    patterns := [pat0]
    tickLength := 3
    voiceOrder := [⟨0, by omega⟩]
  }

def main : IO Unit := do
  -- Compile test song for 30 frames
  let stream := compileFrames testSong 30
  IO.println s!"Compiled {stream.length} frames"
  IO.println s!"Writes per frame: {stream.map (·.length)}"
  -- Show first 5 frames
  for i in [:5] do
    match stream[i]? with
    | some frame =>
      let desc := frame.map fun w =>
        let regName := match w.reg with
          | .freqLo v => s!"V{v.val+1}flo"
          | .freqHi v => s!"V{v.val+1}fhi"
          | .pwLo v => s!"V{v.val+1}plo"
          | .pwHi v => s!"V{v.val+1}phi"
          | .ctrl v => s!"V{v.val+1}ctl"
          | .ad v => s!"V{v.val+1}ad"
          | .sr v => s!"V{v.val+1}sr"
          | .filtLo => "Flo"
          | .filtHi => "Fhi"
          | .filtCtrl => "Fctl"
          | .modeVol => "Vol"
        s!"{regName}=${w.val.val}"
      IO.println s!"  F{i}: {String.intercalate " " desc}"
    | none => pure ()
