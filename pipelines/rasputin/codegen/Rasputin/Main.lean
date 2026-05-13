import Rasputin.Codegen
import Rasputin.SongData

open RasputinNS

def main : IO Unit := do
  let sid := generateSID rasputinV3
  let handle ← IO.FS.Handle.mk "rasputin.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated rasputin.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {rasputinV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {rasputinV3.instruments.length}"
  IO.println s!"  Patterns: {rasputinV3.patterns.length}"
  IO.println s!"  Subtunes: {rasputinV3.subtunes.length}"
