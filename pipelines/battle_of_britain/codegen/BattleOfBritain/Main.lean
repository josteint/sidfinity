import BattleOfBritain.Codegen
import BattleOfBritain.SongData

open BattleOfBritainNS

def main : IO Unit := do
  let sid := generateSID battle_of_britainV3
  IO.FS.createDirAll "pipelines/battle_of_britain/build"
  let handle ← IO.FS.Handle.mk "pipelines/battle_of_britain/build/battle_of_britain.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated battle_of_britain.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {battle_of_britainV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {battle_of_britainV3.instruments.length}"
  IO.println s!"  Patterns: {battle_of_britainV3.patterns.length}"
  IO.println s!"  Subtunes: {battle_of_britainV3.subtunes.length}"
