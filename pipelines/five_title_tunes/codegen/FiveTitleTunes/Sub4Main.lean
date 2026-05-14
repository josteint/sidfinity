import FiveTitleTunes.Codegen
import FiveTitleTunes.Sub4

open FiveTitleTunesNS

def main : IO Unit := do
  let sid := generateSID (baseAddr := 0x4900) sub4V3
  let handle ← IO.FS.Handle.mk "five_tt_4.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_tt_4.sid ({sid.size} bytes)"
