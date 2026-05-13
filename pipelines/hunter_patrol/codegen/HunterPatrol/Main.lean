import HunterPatrol.Codegen
import HunterPatrol.SongData

open HunterPatrolNS

def main : IO Unit := do
  let sid := generateSID hunter_patrolV3
  let handle ← IO.FS.Handle.mk "hunter_patrol.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated hunter_patrol.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {hunter_patrolV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {hunter_patrolV3.instruments.length}"
  IO.println s!"  Patterns: {hunter_patrolV3.patterns.length}"
  IO.println s!"  Subtunes: {hunter_patrolV3.subtunes.length}"
