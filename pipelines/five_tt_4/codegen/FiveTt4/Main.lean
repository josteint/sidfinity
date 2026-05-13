import FiveTt4.Codegen
import FiveTt4.SongData

open FiveTt4NS

def main : IO Unit := do
  let sid := generateSID (baseAddr := 0x4900) five_tt_4V3
  let handle ← IO.FS.Handle.mk "five_tt_4.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_tt_4.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {five_tt_4V3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {five_tt_4V3.instruments.length}"
  IO.println s!"  Patterns: {five_tt_4V3.patterns.length}"
  IO.println s!"  Subtunes: {five_tt_4V3.subtunes.length}"
