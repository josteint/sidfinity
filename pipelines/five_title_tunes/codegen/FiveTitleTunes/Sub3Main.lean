import FiveTitleTunes.Codegen
import FiveTitleTunes.Sub3

open FiveTitleTunesNS

def main : IO Unit := do
  let sid := generateSID (baseAddr := 0x3B00) sub3V3
  let handle ← IO.FS.Handle.mk "five_tt_3.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_tt_3.sid ({sid.size} bytes)"
