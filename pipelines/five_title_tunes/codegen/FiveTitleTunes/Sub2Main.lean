import FiveTitleTunes.Codegen
import FiveTitleTunes.Sub2

open FiveTitleTunesNS

def main : IO Unit := do
  let sid := generateSID (baseAddr := 0x2F00) sub2V3
  let handle ← IO.FS.Handle.mk "five_tt_2.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_tt_2.sid ({sid.size} bytes)"
