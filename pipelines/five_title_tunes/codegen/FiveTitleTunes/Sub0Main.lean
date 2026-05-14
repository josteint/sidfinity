import FiveTitleTunes.Codegen
import FiveTitleTunes.Sub0

open FiveTitleTunesNS

def main : IO Unit := do
  let sid := generateSID (baseAddr := 0x1000) sub0V3
  let handle ← IO.FS.Handle.mk "five_tt_0.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_tt_0.sid ({sid.size} bytes)"
