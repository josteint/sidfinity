import LastV8C128.Codegen
import LastV8C128.SongData

open LastV8C128NS

def main : IO Unit := do
  let sid := generateSID last_v8_c128V3
  let handle ← IO.FS.Handle.mk "last_v8_c128.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated last_v8_c128.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {last_v8_c128V3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {last_v8_c128V3.instruments.length}"
  IO.println s!"  Patterns: {last_v8_c128V3.patterns.length}"
  IO.println s!"  Subtunes: {last_v8_c128V3.subtunes.length}"
