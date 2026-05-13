import FiveTitleTunes.Codegen
import FiveTitleTunes.SongData

open FiveTitleTunesNS

def main : IO Unit := do
  let sid := generateSID five_title_tunesV3
  let handle ← IO.FS.Handle.mk "five_title_tunes.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated five_title_tunes.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {five_title_tunesV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {five_title_tunesV3.instruments.length}"
  IO.println s!"  Patterns: {five_title_tunesV3.patterns.length}"
  IO.println s!"  Subtunes: {five_title_tunesV3.subtunes.length}"
