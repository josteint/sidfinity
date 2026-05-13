import Gremlins.Codegen
import Gremlins.SongData

open GremlinsNS

def main : IO Unit := do
  let sid := generateSID gremlinsV3
  let handle ← IO.FS.Handle.mk "gremlins.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated gremlins.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {gremlinsV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {gremlinsV3.instruments.length}"
  IO.println s!"  Patterns: {gremlinsV3.patterns.length}"
  IO.println s!"  Subtunes: {gremlinsV3.subtunes.length}"
