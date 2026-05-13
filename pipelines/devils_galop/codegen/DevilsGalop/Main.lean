import DevilsGalop.Codegen
import DevilsGalop.SongData

open DevilsGalopNS

def main : IO Unit := do
  let sid := generateSID devils_galopV3
  let handle ← IO.FS.Handle.mk "devils_galop.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated devils_galop.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {devils_galopV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {devils_galopV3.instruments.length}"
  IO.println s!"  Patterns: {devils_galopV3.patterns.length}"
  IO.println s!"  Subtunes: {devils_galopV3.subtunes.length}"
