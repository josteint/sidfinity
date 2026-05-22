import LastV8C128.Codegen
import LastV8C128.SongData
import LastV8C128.Constants

open LastV8C128NS

def main : IO Unit := do
  let m := lastV8C128Model
  let sid := generateTombstone m
  IO.FS.createDirAll "pipelines/last_v8_c128/build"
  let h ← IO.FS.Handle.mk "pipelines/last_v8_c128/build/last_v8_c128.sid" .write
  h.write ⟨sid⟩
  IO.println s!"Wrote pipelines/last_v8_c128/build/last_v8_c128.sid ({sid.size} bytes)"
  IO.println ""
  IO.println "  WARNING: this is a TOMBSTONE rebuild."
  IO.println "  The payload is a single RTS — no player code is emitted yet."
  IO.println "  See pipelines/last_v8_c128/README.md for what's missing."
  IO.println ""
  IO.println s!"  Original metadata preserved:"
  IO.println s!"    name      : {m.header.name}"
  IO.println s!"    author    : {m.header.author}"
  IO.println s!"    released  : {m.header.released}"
  let routeSummary :=
    String.intercalate ", "
      (m.routes.map (fun r => s!"{r.subtune}={r.kind}"))
  IO.println s!"    subtunes  : {m.header.songs} (routes: {routeSummary})"
  IO.println s!"    samples   : {m.samples.length}"
  IO.println s!"    instruments: {m.instruments.length}"
  IO.println s!"    patterns  : {m.patterns.length}"
  IO.println s!"    music     : {m.musicSubtunes.length} subtune(s)"
  for s in m.musicSubtunes do
    let voiceLens :=
      String.intercalate " "
        (s.voices.map (fun v => s!"V{v.voice}={v.indices.length}({v.terminator})"))
    IO.println s!"      subtune {s.subtune}: {voiceLens}"
