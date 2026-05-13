import FiveTt1.Codegen
import FiveTt1.SongData

open FiveTt1NS

def main : IO Unit := do
  let sid := generateSID (baseAddr := 0x2500) five_tt_1V3
  let handle ← IO.FS.Handle.mk "five_tt_1.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_tt_1.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {five_tt_1V3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {five_tt_1V3.instruments.length}"
  IO.println s!"  Patterns: {five_tt_1V3.patterns.length}"
  IO.println s!"  Subtunes: {five_tt_1V3.subtunes.length}"
