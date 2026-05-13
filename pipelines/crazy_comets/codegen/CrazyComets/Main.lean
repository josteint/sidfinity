import CrazyComets.Codegen
import CrazyComets.SongData

open CrazyCometsNS

def main : IO Unit := do
  let sid := generateSID crazy_cometsV3
  let handle ← IO.FS.Handle.mk "crazy_comets.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated crazy_comets.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {crazy_cometsV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {crazy_cometsV3.instruments.length}"
  IO.println s!"  Patterns: {crazy_cometsV3.patterns.length}"
  IO.println s!"  Subtunes: {crazy_cometsV3.subtunes.length}"
