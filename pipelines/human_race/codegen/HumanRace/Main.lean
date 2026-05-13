import HumanRace.Codegen
import HumanRace.SongData

open HumanRaceNS

def main : IO Unit := do
  let sid := generateSID human_raceV3
  let handle ← IO.FS.Handle.mk "human_race.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated human_race.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {human_raceV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {human_raceV3.instruments.length}"
  IO.println s!"  Patterns: {human_raceV3.patterns.length}"
  IO.println s!"  Subtunes: {human_raceV3.subtunes.length}"
