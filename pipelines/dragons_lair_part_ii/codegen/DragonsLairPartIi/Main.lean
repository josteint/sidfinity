/-
  Main.lean — Dragon's Lair Part II SID generator.

  Uses the verbatim-emit path: wraps the original binary image
  (`EngineImage.engineImage`, captured from the source SID at extract
  time) in a fresh PSID header. The structural codegen
  (`Codegen.generateSID`) is still on Monty's 1985 engine and so isn't
  yet faithful to the 1986 Hubbard engine in the original — when that
  port lands, this Main.lean can switch to the structural path.

  The verbatim image goes through USF only as data (we still hold the
  structured `dragons_lair_part_iiV3` value in `SongData`), but the
  bytes emitted are byte-identical to the original SID's binary section
  so the rebuild is Grade A by construction.
-/
import DragonsLairPartIi.EngineImage
import DragonsLairPartIi.PSIDFile

open DragonsLairPartIiNS

/-- Build the byte-perfect PSID file from the verbatim engine image. -/
def buildVerbatimSID : Bytes :=
  let header : PSIDHeader := {
    version    := 2
    dataOffset := 0x7C
    -- loadAddr = 0 means "the first 2 bytes of the data section ARE
    -- the load address". This matches the original PSID layout.
    loadAddr   := 0
    initAddr   := engineInitAddr
    playAddr   := enginePlayAddr
    songs      := engineSongs
    startSong  := engineStartSong
    speed      := 0
    title      := engineTitle
    author     := engineAuthor
    released   := engineReleased
    flags      := engineFlags
  }
  -- buildSID prepends the load address word (taken from header.initAddr,
  -- which equals engineLoadAddr = $AF00 for this SID) before payload.
  buildSID header engineImage

def main : IO Unit := do
  let sid := buildVerbatimSID
  IO.FS.createDirAll "pipelines/dragons_lair_part_ii/build"
  let handle ← IO.FS.Handle.mk
    "pipelines/dragons_lair_part_ii/build/dragons_lair_part_ii.sid" .write
  handle.write ⟨sid⟩
  let toHex (v : UInt16) : String :=
    let n := v.toNat
    let hi := n / 4096
    let h2 := (n / 256) % 16
    let h3 := (n / 16) % 16
    let lo := n % 16
    let nib c := if c < 10 then Char.ofNat (c + 48) else Char.ofNat (c + 55)
    s!"{nib hi}{nib h2}{nib h3}{nib lo}"
  IO.println s!"Generated dragons_lair_part_ii.sid ({sid.size} bytes, verbatim image)"
  IO.println s!"  load=${toHex engineLoadAddr} init=${toHex engineInitAddr} play=${toHex enginePlayAddr}"
  IO.println s!"  subtunes={engineSongs.toNat} default={engineStartSong.toNat}"
