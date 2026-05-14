import OneManAndHisDroid.Codegen
import OneManAndHisDroid.SongData

open OneManAndHisDroidNS

def main : IO Unit := do
  let sid := generateSID one_man_and_his_droidV3
  IO.FS.createDirAll "pipelines/one_man_and_his_droid/build"
  let handle ← IO.FS.Handle.mk "pipelines/one_man_and_his_droid/build/one_man_and_his_droid.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated one_man_and_his_droid.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {one_man_and_his_droidV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {one_man_and_his_droidV3.instruments.length}"
  IO.println s!"  Patterns: {one_man_and_his_droidV3.patterns.length}"
  IO.println s!"  Subtunes: {one_man_and_his_droidV3.subtunes.length}"
