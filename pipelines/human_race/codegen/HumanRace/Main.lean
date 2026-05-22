import HumanRace.Codegen
import HumanRace.SongData

open HumanRaceNS

def main : IO Unit := do
  let sid := generateSID human_raceV3
  IO.FS.createDirAll "pipelines/human_race/build"
  let handle ← IO.FS.Handle.mk "pipelines/human_race/build/human_race.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated human_race.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {human_raceV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {human_raceV3.instruments.length}"
  IO.println s!"  Patterns: {human_raceV3.patterns.length}"
  IO.println s!"  Subtunes: {human_raceV3.subtunes.length}"
