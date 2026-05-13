import SampleMusicIKarate.Codegen
import SampleMusicIKarate.SongData

open SampleMusicIKarateNS

def main : IO Unit := do
  let sid := generateSID sample_music_i_karateV3
  let handle ← IO.FS.Handle.mk "sample_music_i_karate.sid" .write
  handle.write ⟨sid⟩
  IO.println s!"Generated sample_music_i_karate.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {sample_music_i_karateV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {sample_music_i_karateV3.instruments.length}"
  IO.println s!"  Patterns: {sample_music_i_karateV3.patterns.length}"
  IO.println s!"  Subtunes: {sample_music_i_karateV3.subtunes.length}"
