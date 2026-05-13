import ActionBiker.Codegen
import ActionBiker.SongData

open ActionBikerNS

def main : IO Unit := do
  let sid := generateSID action_bikerV3
  let handle ← IO.FS.Handle.mk "action_biker.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated action_biker.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {action_bikerV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {action_bikerV3.instruments.length}"
  IO.println s!"  Patterns: {action_bikerV3.patterns.length}"
  IO.println s!"  Subtunes: {action_bikerV3.subtunes.length}"
