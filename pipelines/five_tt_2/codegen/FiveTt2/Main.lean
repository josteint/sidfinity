import FiveTt2.Codegen
import FiveTt2.SongData

open FiveTt2NS

def main : IO Unit := do
  let sid := generateSID (baseAddr := 0x2F00) five_tt_2V3
  let handle ← IO.FS.Handle.mk "five_tt_2.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_tt_2.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {five_tt_2V3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {five_tt_2V3.instruments.length}"
  IO.println s!"  Patterns: {five_tt_2V3.patterns.length}"
  IO.println s!"  Subtunes: {five_tt_2V3.subtunes.length}"
