/-
  CompareMain.lean — Compare original SID vs generated SID,
  both executed by the Lean 6502 model. No external tools needed.
-/
import CPU6502
import Codegen

def cmpShowWrite (w : SIDWrite) : String :=
  let rn := match w.reg with
    | .freqLo v => s!"V{v.val+1}flo"  | .freqHi v => s!"V{v.val+1}fhi"
    | .pwLo v => s!"V{v.val+1}plo"    | .pwHi v => s!"V{v.val+1}phi"
    | .ctrl v => s!"V{v.val+1}ctl"    | .ad v => s!"V{v.val+1}ad"
    | .sr v => s!"V{v.val+1}sr"
    | .filtLo => "Flo" | .filtHi => "Fhi" | .filtCtrl => "Fctl" | .modeVol => "Vol"
  s!"{rn}=${w.val.val}"

def cmpShowFrame (writes : List SIDWrite) : String :=
  String.intercalate " " (writes.map cmpShowWrite)

def writeEq (a b : SIDWrite) : Bool :=
  match a.reg, b.reg with
  | .freqLo v1, .freqLo v2 => v1 == v2 && a.val == b.val
  | .freqHi v1, .freqHi v2 => v1 == v2 && a.val == b.val
  | .pwLo v1, .pwLo v2 => v1 == v2 && a.val == b.val
  | .pwHi v1, .pwHi v2 => v1 == v2 && a.val == b.val
  | .ctrl v1, .ctrl v2 => v1 == v2 && a.val == b.val
  | .ad v1, .ad v2 => v1 == v2 && a.val == b.val
  | .sr v1, .sr v2 => v1 == v2 && a.val == b.val
  | .filtLo, .filtLo => a.val == b.val
  | .filtHi, .filtHi => a.val == b.val
  | .filtCtrl, .filtCtrl => a.val == b.val
  | .modeVol, .modeVol => a.val == b.val
  | _, _ => false

def frameEq (a b : List SIDWrite) : Bool :=
  a.length == b.length && (a.zip b).all (fun (x, y) => writeEq x y)

def main : IO Unit := do
  let nFrames := 20

  -- Load original Commando SID
  let origPath := "../../data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid"
  let origData ← IO.FS.readBinFile origPath
  IO.println s!"Original: {origData.size} bytes"

  -- Generate our SID
  let genBytes := generateSID commandoSong
  let genData := ByteArray.mk genBytes
  IO.println s!"Generated: {genData.size} bytes"

  -- Load both into 6502
  match loadSID origData, loadSID genData with
  | some (cpuO, initO, playO), some (cpuG, initG, playG) =>
    IO.println s!"Original:  init=${initO} play=${playO}"
    IO.println s!"Generated: init=${initG} play=${playG}"

    -- Run init on both
    let (cpuO, initWritesO) := execInit cpuO initO
    IO.println s!"Original init: {initWritesO.length} writes, PC after=${cpuO.pc}"
    let (cpuG, initWritesG) := execInit cpuG initG
    IO.println s!"Generated init: {initWritesG.length} writes, PC after=${cpuG.pc}"

    -- Debug: check what's at play address for original
    IO.println s!"Original play[0..3]: ${cpuO.read playO} ${cpuO.read (playO+1)} ${cpuO.read (playO+2)} ${cpuO.read (playO+3)}"

    -- Test: run one play call manually and count writes
    let (cpuOtest, writesOtest) := execPlay cpuO playO
    IO.println s!"Original F0: {writesOtest.length} writes, PC after=${cpuOtest.pc} SP=${cpuOtest.sp}"
    -- Check what opcode is at the halt PC
    let haltOp := cpuOtest.read cpuOtest.pc
    IO.println s!"  Halted at opcode={haltOp.toNat}"
    match writesOtest with
    | w :: _ => IO.println s!"  First write: {cmpShowWrite w}"
    | [] => pure ()

    -- Execute frames
    let framesO := execFrames cpuO playO nFrames
    let framesG := execFrames cpuG playG nFrames

    -- Compare
    let mut matchCount := 0
    let mut diffShown := 0
    for i in [:min framesO.length framesG.length] do
      match framesO[i]?, framesG[i]? with
      | some fo, some fg =>
        if frameEq fo fg then
          matchCount := matchCount + 1
        else if diffShown < 8 then
          diffShown := diffShown + 1
          IO.println s!"F{i}: ORIG({fo.length}) {cmpShowFrame (fo.take 8)}"
          IO.println s!"     LEAN({fg.length}) {cmpShowFrame (fg.take 8)}"
      | _, _ => pure ()

    let total := min framesO.length framesG.length
    IO.println s!""
    IO.println s!"Match: {matchCount}/{total} ({matchCount * 100 / total}%)"

  | _, _ => IO.println "Failed to load SIDs"
