import FiveTitleTunes.Codegen
import FiveTitleTunes.SongData

open FiveTitleTunesNS

def main : IO Unit := do
  let sid := generateSID fiveTtV3
  let handle ← IO.FS.Handle.mk "five_title_tunes.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_title_tunes.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {fiveTtV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {fiveTtV3.instruments.length}"
  IO.println s!"  Patterns: {fiveTtV3.patterns.length}"
  IO.println s!"  Subtunes: {fiveTtV3.subtunes.length}"
