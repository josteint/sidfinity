import Monty.Codegen
import Monty.SongData

open MV3

def main : IO Unit := do
  let sid := generateSID montyV3
  IO.FS.createDirAll "pipelines/monty/build"
  let handle ← IO.FS.Handle.mk "pipelines/monty/build/monty.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated monty.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {montyV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {montyV3.instruments.length}"
  IO.println s!"  Patterns: {montyV3.patterns.length}"
  IO.println s!"  Subtunes: {montyV3.subtunes.length}"
