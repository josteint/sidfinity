/-
  VerifyMain.lean — Run the Lean 6502 emulator on a generated SID
  and compare the SID writes against sidplayfp's ground truth.
-/
import CPU6502
import Codegen

def main : IO Unit := do
  -- Generate the SID
  let sid := generateSID commandoSong
  IO.println s!"Generated SID: {sid.size} bytes"

  -- Load into 6502 model
  let sidBA := ByteArray.mk sid
  match loadSID sidBA with
  | none => IO.println "Failed to load SID"
  | some (cpu, initAddr, playAddr) =>
    IO.println s!"Loaded: init=${initAddr} play=${playAddr}"

    -- Run init
    let (cpu, initWrites) := execInit cpu initAddr
    IO.println s!"Init: {initWrites.length} SID writes"

    -- Run 10 frames
    let frames := execFrames cpu playAddr 10
    IO.println s!"Executed {frames.length} frames"

    for i in [:frames.length] do
      match frames[i]? with
      | some writes =>
        let desc := writes.map fun w =>
          let rn := match w.reg with
            | .freqLo v => s!"V{v.val+1}flo"  | .freqHi v => s!"V{v.val+1}fhi"
            | .pwLo v => s!"V{v.val+1}plo"    | .pwHi v => s!"V{v.val+1}phi"
            | .ctrl v => s!"V{v.val+1}ctl"    | .ad v => s!"V{v.val+1}ad"
            | .sr v => s!"V{v.val+1}sr"
            | .filtLo => "Flo" | .filtHi => "Fhi" | .filtCtrl => "Fctl" | .modeVol => "Vol"
          s!"{rn}=${w.val.val}"
        IO.println s!"  F{i}: {String.intercalate " " desc}"
      | none => pure ()
