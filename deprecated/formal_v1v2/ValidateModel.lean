/-
  ValidateModel.lean — Validate Lean 6502 model against sidplayfp --writelog.
  Compares the full instruction stream: (cycle, register, value) per write.
-/
import CPU6502

def parseHex' (s : String) : Nat :=
  s.foldl (fun acc c =>
    acc * 16 + (if c.isDigit then c.toNat - '0'.toNat
               else if c >= 'a' && c <= 'f' then c.toNat - 'a'.toNat + 10
               else if c >= 'A' && c <= 'F' then c.toNat - 'A'.toNat + 10
               else 0)) 0

-- Parse writelog: extract (cycle, reg, val) triples per frame
def parseWrites (wpart : String) : List (Nat × Nat × UInt8) := Id.run do
  let tokens := wpart.splitOn ":"
  let mut writes : List (Nat × Nat × UInt8) := []
  let mut i := 0
  while i + 2 < tokens.length do
    match tokens[i]?, tokens[i + 1]?, tokens[i + 2]? with
    | some cycStr, some regStr, some valStr =>
      writes := writes ++ [(parseHex' cycStr, parseHex' regStr, (parseHex' valStr).toUInt8)]
    | _, _, _ => pure ()
    i := i + 3
  return writes

def parseLog (output : String) : List (List (Nat × Nat × UInt8)) :=
  let lines := output.splitOn "\n"
  lines.filterMap fun line =>
    if (line.splitOn "|W:").length > 1 then
      match (line.splitOn "|W:")[1]? with
      | some w => some (parseWrites w)
      | none => some []
    else if line.length > 10 && !line.startsWith "{" && !line.startsWith "V1_" then
      some []
    else none

-- Convert TimedSIDWrite to (reg_offset, value)
def twToRegVal (tw : TimedSIDWrite) : Nat × UInt8 :=
  let reg := match tw.write.reg with
    | .freqLo v => v.val * 7      | .freqHi v => v.val * 7 + 1
    | .pwLo v => v.val * 7 + 2    | .pwHi v => v.val * 7 + 3
    | .ctrl v => v.val * 7 + 4    | .ad v => v.val * 7 + 5
    | .sr v => v.val * 7 + 6
    | .filtLo => 21  | .filtHi => 22  | .filtCtrl => 23  | .modeVol => 24
  (reg, (tw.write.val.val % 256).toUInt8)

def main : IO Unit := do
  let nFrames := 500
  let origPath := "../../data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid"
  let origData ← IO.FS.readBinFile origPath

  -- 1. Run sidplayfp
  IO.println "Running sidplayfp..."
  let duration := nFrames / 50 + 1
  let result ← IO.Process.output {
    cmd := "../../tools/siddump"
    args := #[origPath, "--subtune", "1", "--duration", toString duration, "--writelog"]
  }
  let spFrames := parseLog result.stdout
  IO.println s!"sidplayfp: {spFrames.length} frames"

  -- 2. Run Lean 6502
  match loadSID origData with
  | none => IO.println "Failed to load SID"
  | some (cpu, initAddr, playAddr) =>
    IO.println s!"Lean 6502: init=${initAddr} play=${playAddr}"
    -- Simulate sidplayfp's pre-init Vol write
    let (cpu, volWrites) := cpu.write 0xD418 0x0F
    let (cpu, initWrites) := execInit cpu initAddr
    -- Reset cycles for frame counting
    let cpu := { cpu with cycles := 0 }
    let playFrames := execFrames cpu playAddr nFrames
    -- Prepend init writes to F0
    let leanFrames := match playFrames with
      | f0 :: rest => (volWrites ++ initWrites ++ f0) :: rest
      | [] => [volWrites ++ initWrites]
    IO.println s!"Lean: {leanFrames.length} frames"

    -- 3. Flatten both streams with (cycle, reg, val)
    -- For Lean: cycle is absolute from cpu.cycles
    let mut flatLean : List (Nat × Nat × UInt8) := []
    for frame in leanFrames do
      for tw in frame do
        let (reg, val) := twToRegVal tw
        flatLean := flatLean ++ [(tw.cycle, reg, val)]

    let mut flatSP : List (Nat × Nat × UInt8) := []
    -- sidplayfp cycles are per-frame; convert to absolute
    let mut frameBase : Nat := 0
    for frame in spFrames do
      for (cyc, reg, val) in frame do
        flatSP := flatSP ++ [(frameBase + cyc, reg, val)]
      frameBase := frameBase + PAL_CYCLES_PER_FRAME

    IO.println s!"Total writes: Lean={flatLean.length} SPFP={flatSP.length}"

    -- 4. Compare: find first divergence in (reg, val) — ignoring cycles
    let mut regValMatch := 0
    let mut regValStop := false
    for i in [:min flatLean.length flatSP.length] do
      if !regValStop then
        match flatLean[i]?, flatSP[i]? with
        | some (_, lr, lv), some (_, sr, sv) =>
          if lr == sr && lv == sv then regValMatch := regValMatch + 1
          else regValStop := true
        | _, _ => regValStop := true
    IO.println s!"Reg+Val match: {regValMatch}/{min flatLean.length flatSP.length}"

    -- 5. Compare WITH cycles: find first cycle divergence
    let mut fullMatch := 0
    let mut fullStop := false
    let mut firstCycleDiff := 0
    for i in [:min flatLean.length flatSP.length] do
      if !fullStop then
        match flatLean[i]?, flatSP[i]? with
        | some (lc, lr, lv), some (sc, sr, sv) =>
          if lc == sc && lr == sr && lv == sv then fullMatch := fullMatch + 1
          else
            if firstCycleDiff == 0 then
              firstCycleDiff := i
              IO.println s!"First divergence at write #{i}:"
              IO.println s!"  Lean: cycle={lc} reg={lr} val={lv.toNat}"
              IO.println s!"  SPFP: cycle={sc} reg={sr} val={sv.toNat}"
              -- Show surrounding writes
              if i > 0 then
                match flatLean[i-1]?, flatSP[i-1]? with
                | some (lc2, lr2, lv2), some (sc2, sr2, sv2) =>
                  IO.println s!"  Prev Lean: cycle={lc2} reg={lr2} val={lv2.toNat}"
                  IO.println s!"  Prev SPFP: cycle={sc2} reg={sr2} val={sv2.toNat}"
                | _, _ => pure ()
            fullStop := true
        | _, _ => fullStop := true
    IO.println s!"Full match (cycle+reg+val): {fullMatch}/{min flatLean.length flatSP.length}"

    -- 6. Check if a constant cycle offset fixes everything
    match flatLean[0]?, flatSP[0]? with
    | some (lc0, _, _), some (sc0, _, _) =>
      let offset : Int := sc0 - lc0
      IO.println s!"Trying constant cycle offset: {offset}"
      let mut offsetMatch := 0
      let mut offsetStop := false
      let mut firstOffDiff := 0
      for i in [:min flatLean.length flatSP.length] do
        if !offsetStop then
          match flatLean[i]?, flatSP[i]? with
          | some (lc, lr, lv), some (sc, sr, sv) =>
            if (lc + offset.toNat) == sc && lr == sr && lv == sv then
              offsetMatch := offsetMatch + 1
            else if firstOffDiff == 0 then
              firstOffDiff := i
              IO.println s!"  Offset fails at write #{i}: Lean+{offset}={lc + offset.toNat} vs SPFP={sc} (drift={sc - lc - offset.toNat})"
              offsetStop := true
          | _, _ => offsetStop := true
      IO.println s!"  With offset: {offsetMatch}/{min flatLean.length flatSP.length}"
      if offsetMatch == min flatLean.length flatSP.length then
        IO.println "PERFECT MATCH with constant cycle offset!"
    | _, _ => pure ()
