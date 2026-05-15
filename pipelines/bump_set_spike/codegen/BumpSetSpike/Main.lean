import BumpSetSpike.Codegen
import BumpSetSpike.SongData

open V3

def main : IO Unit := do
  let sid := generateSID bump_set_spikeV3
  IO.FS.createDirAll "pipelines/bump_set_spike/build"
  let handle ← IO.FS.Handle.mk "pipelines/bump_set_spike/build/bump_set_spike.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated bump_set_spike.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {bump_set_spikeV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {bump_set_spikeV3.instruments.length}"
  IO.println s!"  Patterns: {bump_set_spikeV3.patterns.length}"
  IO.println s!"  Voices: {bump_set_spikeV3.voices.length}"
