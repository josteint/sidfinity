import Commando.Codegen
import Commando.SongData

open V3

def main : IO Unit := do
  let sid := generateSID commandoV3
  let handle ← IO.FS.Handle.mk "commando.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated commando.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {commandoV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {commandoV3.instruments.length}"
  IO.println s!"  Patterns: {commandoV3.patterns.length}"
  IO.println s!"  Voices: {commandoV3.voices.length}"
