import FiveTitleTunes.Codegen
import FiveTitleTunes.Sub1

open FiveTitleTunesNS

def main : IO Unit := do
  let sid := generateSID (baseAddr := 0x2500) sub1V3
  let handle ← IO.FS.Handle.mk "five_tt_1.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_tt_1.sid ({sid.size} bytes)"
