/-
  Codegen.lean — TOMBSTONE codegen for the Last V8 (C128) pipeline.

  The Last V8 engine does not yet have a real rebuild path. This
  codegen produces a *placeholder* PSID:

    * The PSID header preserves the original metadata (title, author,
      release line, subtune count).
    * The payload is a single `RTS` at the load address — an honest
      no-op player. Audio: silent. There is no recovered song data,
      no relocator, no sample player.

  This exists so:
    (a) `lake build sidgen_last_v8_c128` succeeds and produces a file,
    (b) anyone running the exe sees in plain English that the rebuild
        is unimplemented (the IO output is explicit), and
    (c) the directory structure mirrors Commando / Monty so the
        sibling pipelines stay consistent.

  Replacing this with a real codegen requires either (1) lifting the
  music subtunes (0-2, 6+) to a `USFSong` and reusing the V3 codegen,
  plus a separate sample-player emitter for subtunes 3-5, or (2) a
  faithful 6502 emit of the original 17556-byte player. See README.md
  for context.
-/

import LastV8C128.Asm6502
import LastV8C128.PSIDFile
import LastV8C128.SongData
import LastV8C128.Constants

namespace LastV8C128NS

/-- The minimal player payload: a single RTS at $4800. -/
def tombstonePayload : Bytes :=
  #[0x60]   -- RTS

/-- Build a tombstone PSID from the extracted engine model. Preserves
    the original PSID metadata so the file is recognisable in players. -/
def generateTombstone (m : EngineModel) : Bytes :=
  let h : PSIDHeader := {
    version    := 2
    dataOffset := 0x7C
    loadAddr   := 0
    initAddr   := ORIG_LOAD     -- our init = the RTS at the load addr
    playAddr   := ORIG_LOAD     -- same: any "play" jump lands on RTS
    songs      := m.header.songs.toUInt16
    startSong  := 1
    speed      := 0
    title      := m.header.name
    author     := m.header.author
    released   := m.header.released
  }
  buildSID h tombstonePayload

end LastV8C128NS
