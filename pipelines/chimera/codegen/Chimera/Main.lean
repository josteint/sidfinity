import Chimera.Codegen
import Chimera.SongData

open ChimeraNS

def main : IO Unit := do
  let sid := generateSID chimeraV3
  let handle ← IO.FS.Handle.mk "chimera.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated chimera.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {chimeraV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {chimeraV3.instruments.length}"
  IO.println s!"  Patterns: {chimeraV3.patterns.length}"
  IO.println s!"  Subtunes: {chimeraV3.subtunes.length}"
