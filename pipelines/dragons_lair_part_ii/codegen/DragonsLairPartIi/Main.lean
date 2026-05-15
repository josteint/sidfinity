import DragonsLairPartIi.Codegen
import DragonsLairPartIi.SongData

open DragonsLairPartIiNS

def main : IO Unit := do
  let sid := generateSID dragons_lair_part_iiV3
  IO.FS.createDirAll "pipelines/dragons_lair_part_ii/build"
  let handle ← IO.FS.Handle.mk "pipelines/dragons_lair_part_ii/build/dragons_lair_part_ii.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated dragons_lair_part_ii.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {dragons_lair_part_iiV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {dragons_lair_part_iiV3.instruments.length}"
  IO.println s!"  Patterns: {dragons_lair_part_iiV3.patterns.length}"
  IO.println s!"  Subtunes: {dragons_lair_part_iiV3.subtunes.length}"
