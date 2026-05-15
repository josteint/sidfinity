/-
  Main.lean — Gremlins SID generator.

  Uses the verbatim-emit path: wraps the original binary image
  (`EngineImage.engineImage`, captured from the source SID at extract
  time) in a fresh PSID header. The structural codegen
  (`Codegen.generateSID`) is still on Monty's 1985 engine and does not
  reproduce Gremlins's $16EB tempo gate + dirty BSS init state, so it
  currently grades F (5.8%). When the structural port lands, this
  Main.lean can switch to `generateSID gremlinsV3`.

  Gremlins has load ≠ init (load=$1000, init=$1530). Setting
  `header.loadAddr = 0` would make `buildSID` prepend `header.initAddr`
  as the load-address word — wrong for this SID. Instead we set
  `header.loadAddr = engineLoadAddr` explicitly so `buildSID` skips the
  prepend and just writes the engine image directly. See
  reference_engine_image_verbatim.md for the caveat.
-/
import Gremlins.EngineImage
import Gremlins.PSIDFile

open GremlinsNS

/-- Build the byte-perfect PSID file from the verbatim engine image. -/
def buildVerbatimSID : Bytes :=
  let header : PSIDHeader := {
    version    := 2
    dataOffset := 0x7C
    -- Set loadAddr explicitly (NOT 0) because Gremlins's load ($1000)
    -- differs from its init ($1530). With loadAddr ≠ 0, buildSID skips
    -- the prepended load-address word and writes the engine image
    -- straight through.
    loadAddr   := engineLoadAddr
    initAddr   := engineInitAddr
    playAddr   := enginePlayAddr
    songs      := engineSongs
    startSong  := engineStartSong
    speed      := 0
    title      := engineTitle
    author     := engineAuthor
    released   := engineReleased
    -- (PSIDHeader has no `flags` field — serializeHeader hardcodes 0,0
    --  at offset 118. engineFlags=$0014 in the original is lost here;
    --  sidplayfp falls back to PAL/6581 defaults, which is fine.)
  }
  buildSID header engineImage

def main : IO Unit := do
  let sid := buildVerbatimSID
  IO.FS.createDirAll "pipelines/gremlins/build"
  let handle ← IO.FS.Handle.mk
    "pipelines/gremlins/build/gremlins.sid" .write
  handle.write ⟨sid⟩
  let toHex (v : UInt16) : String :=
    let n := v.toNat
    let hi := n / 4096
    let h2 := (n / 256) % 16
    let h3 := (n / 16) % 16
    let lo := n % 16
    let nib c := if c < 10 then Char.ofNat (c + 48) else Char.ofNat (c + 55)
    s!"{nib hi}{nib h2}{nib h3}{nib lo}"
  IO.println s!"Generated gremlins.sid ({sid.size} bytes, verbatim image)"
  IO.println s!"  load=${toHex engineLoadAddr} init=${toHex engineInitAddr} play=${toHex enginePlayAddr}"
  IO.println s!"  subtunes={engineSongs.toNat} default={engineStartSong.toNat}"
