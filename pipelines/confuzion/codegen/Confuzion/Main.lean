import Confuzion.Codegen
import Confuzion.SongData

open ConfuzionNS

def main : IO Unit := do
  let sid := generateSID confuzionV3
  let handle ← IO.FS.Handle.mk "confuzion.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated confuzion.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {confuzionV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {confuzionV3.instruments.length}"
  IO.println s!"  Patterns: {confuzionV3.patterns.length}"
  IO.println s!"  Subtunes: {confuzionV3.subtunes.length}"
