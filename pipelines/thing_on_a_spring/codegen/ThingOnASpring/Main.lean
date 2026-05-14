import ThingOnASpring.Codegen
import ThingOnASpring.SongData

open ThingOnASpringNS

def main : IO Unit := do
  let sid := generateSID thing_on_a_springV3
  IO.FS.createDirAll "pipelines/thing_on_a_spring/build"
  let handle ← IO.FS.Handle.mk "pipelines/thing_on_a_spring/build/thing_on_a_spring.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated thing_on_a_spring.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {thing_on_a_springV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {thing_on_a_springV3.instruments.length}"
  IO.println s!"  Patterns: {thing_on_a_springV3.patterns.length}"
  IO.println s!"  Subtunes: {thing_on_a_springV3.subtunes.length}"
