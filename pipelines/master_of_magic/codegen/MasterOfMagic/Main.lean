import MasterOfMagic.Codegen
import MasterOfMagic.SongData

open MasterOfMagicNS

def main : IO Unit := do
  let sid := generateSID master_of_magicV3
  IO.FS.createDirAll "pipelines/master_of_magic/build"
  let handle ← IO.FS.Handle.mk "pipelines/master_of_magic/build/master_of_magic.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated master_of_magic.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {master_of_magicV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {master_of_magicV3.instruments.length}"
  IO.println s!"  Patterns: {master_of_magicV3.patterns.length}"
  IO.println s!"  Subtunes: {master_of_magicV3.subtunes.length}"
