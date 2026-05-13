import FiveTt3.Codegen
import FiveTt3.SongData

open FiveTt3NS

def main : IO Unit := do
  let sid := generateSID (baseAddr := 0x3B00) five_tt_3V3
  let handle ← IO.FS.Handle.mk "five_tt_3.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_tt_3.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {five_tt_3V3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {five_tt_3V3.instruments.length}"
  IO.println s!"  Patterns: {five_tt_3V3.patterns.length}"
  IO.println s!"  Subtunes: {five_tt_3V3.subtunes.length}"
