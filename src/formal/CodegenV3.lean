/-
  CodegenV3.lean — Universal player codegen consuming USF v3.

  Reads a USFSong and produces a valid .sid file containing a 6502 player
  plus song data. The player handles all USF v3 abstractions universally:
  - NoteKind (pitched/percussion/rest/tie)
  - Per-frame durations (no tick math)
  - Effect chain order from instrument.effectOrder
  - stepEvery counters per effect
  - startDelay timing per effect
  - Release spec (framesBeforeEnd, zeroAdsr, noRelease)

  Frame-accurate: cycle ordering within a frame is deterministic per effect,
  not configurable. Sufficient for all tracker music (PSID, single-speed).
-/

import SID
import Asm6502
import PSIDFile
import USFv3
import CommandoV3

namespace V3

def SID_BASE : UInt16 := 0xD400

-- ==========================================================================
-- Code builder with label/fixup support
-- ==========================================================================

structure Fixup where
  byteIdx    : Nat
  targetLabel : String
  isRelative : Bool      -- branch (1 byte) vs JMP/JSR (2 byte)
  instrAddr  : UInt16

-- Fixup for absolute-indexed LDA/STA instructions (patch the 2-byte address)
structure AbsFixup where
  byteIdx    : Nat       -- index of lo byte of the address operand
  targetLabel : String

structure CodeBuilder where
  bytes    : Bytes := #[]
  baseAddr : UInt16 := 0x1000
  labels   : List (String × UInt16) := []
  fixups   : List Fixup := []
  absFixups : List AbsFixup := []

namespace CodeBuilder

def currentAddr (cb : CodeBuilder) : UInt16 :=
  cb.baseAddr + cb.bytes.size.toUInt16

def emit (cb : CodeBuilder) (bs : Bytes) : CodeBuilder :=
  { cb with bytes := cb.bytes ++ bs }

def emitInst (cb : CodeBuilder) (inst : Instruction) : CodeBuilder :=
  match assembleInst inst with
  | some bs => cb.emit bs
  | none    => cb

def label (cb : CodeBuilder) (name : String) : CodeBuilder :=
  { cb with labels := (name, cb.currentAddr) :: cb.labels }

def lookupLabel (cb : CodeBuilder) (name : String) : Option UInt16 :=
  cb.labels.lookup name

def emitBranch (cb : CodeBuilder) (mn : Mnemonic) (target : String) : CodeBuilder :=
  let instrAddr := cb.currentAddr
  let op := match opcode mn (.rel 0) with | some v => v | none => 0
  let fixup : Fixup := { byteIdx := cb.bytes.size + 1, targetLabel := target,
                          isRelative := true, instrAddr := instrAddr }
  { cb with bytes := cb.bytes ++ #[op, 0], fixups := fixup :: cb.fixups }

def emitJmpLabel (cb : CodeBuilder) (mn : Mnemonic) (target : String) : CodeBuilder :=
  let op := match mn with | .JMP => 0x4C | .JSR => 0x20 | _ => 0x4C
  let fixup : Fixup := { byteIdx := cb.bytes.size + 1, targetLabel := target,
                          isRelative := false, instrAddr := cb.currentAddr }
  { cb with bytes := cb.bytes ++ #[op, 0, 0], fixups := fixup :: cb.fixups }

-- Emit LDA abs,X with forward-referenced table address
-- Opcode $BD (LDA abs,X) + 2-byte address placeholder
def emitLdaAbsX (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xBD, 0, 0], absFixups := fixup :: cb.absFixups }

-- LDA abs,Y with forward ref ($B9)
def emitLdaAbsY (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xB9, 0, 0], absFixups := fixup :: cb.absFixups }

-- STA abs,X with forward ref ($9D)
def emitStaAbsX (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0x9D, 0, 0], absFixups := fixup :: cb.absFixups }

-- DEC abs,X with forward ref ($DE)
def emitDecAbsX (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xDE, 0, 0], absFixups := fixup :: cb.absFixups }

-- INC abs,X with forward ref ($FE)
def emitIncAbsX (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xFE, 0, 0], absFixups := fixup :: cb.absFixups }

-- Resolve all fixups
def resolve (cb : CodeBuilder) : CodeBuilder := Id.run do
  let mut bytes := cb.bytes
  for f in cb.fixups do
    match cb.lookupLabel f.targetLabel with
    | some targetAddr =>
      if f.isRelative then
        let target : Int := targetAddr.toNat
        let source : Int := f.instrAddr.toNat + 2
        let offset := ((target - source) % 256).toNat.toUInt8
        bytes := bytes.set! f.byteIdx offset
      else
        bytes := bytes.set! f.byteIdx targetAddr.toUInt8
        bytes := bytes.set! (f.byteIdx + 1) (targetAddr >>> 8).toUInt8
    | none => pure ()
  for f in cb.absFixups do
    match cb.lookupLabel f.targetLabel with
    | some addr =>
      bytes := bytes.set! f.byteIdx addr.toUInt8
      bytes := bytes.set! (f.byteIdx + 1) (addr >>> 8).toUInt8
    | none => pure ()
  return { cb with bytes := bytes, fixups := [], absFixups := [] }

def emitData (cb : CodeBuilder) (data : List UInt8) : CodeBuilder :=
  cb.emit data.toArray

def emitByte (cb : CodeBuilder) (v : UInt8) : CodeBuilder :=
  cb.emit #[v]

-- Emit STA abs,Y ($99) with forward ref and record fixup
def emitStaAbsY (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0x99, 0, 0], absFixups := fixup :: cb.absFixups }

-- Emit LDA abs,Y ($B9) with forward ref (alias)
def emitLdaAbsYL (cb : CodeBuilder) (target : String) : CodeBuilder :=
  cb.emitLdaAbsY target

-- Add a manual abs fixup for the last emitted 3-byte instruction
def addAbsFixup (cb : CodeBuilder) (target : String) : CodeBuilder :=
  { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := target } :: cb.absFixups }

end CodeBuilder

-- ==========================================================================
-- Player code generation
-- ==========================================================================

-- The player is a subroutine called per voice with X = voice index (0/1/2).
-- All voice state is in absolute tables indexed by X.
-- SID writes use Y = SID offset (loaded from v_sidoff[X]).

-- ==========================================================================
-- Engine-quirks emit helpers (data-driven)
-- ==========================================================================
-- Naming convention for labels:
--   v_scratch_s{slot}_v{voice}  - one byte per (slot, voice)
--   v_scratch_s{slot}           - 3-byte array (start = voice 0)
--   freq_lo_{slot}, freq_hi_{slot}  - alias labels into the freq table

-- Emit LDA A from a USFDynRef. Uses absolute addressing only (no X/Y needed).
private def emitDynRefLoad (cb : CodeBuilder) (ref : USFDynRef) : CodeBuilder :=
  match ref with
  | .constant b =>
    cb.emitInst (I.lda_imm b.val.toUInt8)
  | .scratch v slot =>
    let label := s!"v_scratch_s{slot}_v{v.val}"
    let cb := cb.emitInst (I.lda_abs 0)
    { cb with absFixups :=
      { byteIdx := cb.bytes.size - 2, targetLabel := label } :: cb.absFixups }
  | .voiceCtrl v =>
    let label := s!"v_ctrl_{v.val}"
    let cb := cb.emitInst (I.lda_abs 0)
    { cb with absFixups :=
      { byteIdx := cb.bytes.size - 2, targetLabel := label } :: cb.absFixups }
  | .voicePitch v =>
    let label := s!"v_pitch_v{v.val}"
    let cb := cb.emitInst (I.lda_abs 0)
    { cb with absFixups :=
      { byteIdx := cb.bytes.size - 2, targetLabel := label } :: cb.absFixups }
  | .voiceInst v =>
    let label := s!"v_inst_v{v.val}"
    let cb := cb.emitInst (I.lda_abs 0)
    { cb with absFixups :=
      { byteIdx := cb.bytes.size - 2, targetLabel := label } :: cb.absFixups }

-- Emit STA A to a freq table slot (lo or hi half).
private def emitFreqSlotStore (cb : CodeBuilder) (whichLo : Bool) (slot : Nat) : CodeBuilder :=
  let label := if whichLo then s!"freq_lo_{slot}" else s!"freq_hi_{slot}"
  let cb := cb.emitInst (I.sta_abs 0)
  { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := label } :: cb.absFixups }

-- Emit code for one dynamic freq entry (load lo source -> STA freq_lo_slot, ditto hi).
private def emitDynamicFreqEntry (cb : CodeBuilder) (e : USFDynamicFreqEntry) : CodeBuilder :=
  let cb := emitDynRefLoad cb e.loSource
  let cb := emitFreqSlotStore cb true e.freqSlot
  let cb := emitDynRefLoad cb e.hiSource
  emitFreqSlotStore cb false e.freqSlot

-- Emit dynamic freq updates for entries matching a particular phase.
private def emitDynamicUpdatesForPhase (cb : CodeBuilder) (entries : List USFDynamicFreqEntry)
    (phase : USFUpdatePhase) : CodeBuilder := Id.run do
  let mut cb := cb
  for e in entries do
    let phaseMatches := match e.phase, phase with
      | .atFrameStart, .atFrameStart => true
      | .beforeVoice a, .beforeVoice b => a.val == b.val
      | _, _ => false
    if phaseMatches then
      cb := emitDynamicFreqEntry cb e
  return cb

-- Emit a per-voice noteLoadOp (X must be voice index, $FB has raw inst byte).
-- For "*IfNextEnds" ops, caller must set up Y=0 and have $FC pointing to next note.
private def emitNoteLoadOp (cb : CodeBuilder) (op : USFNoteLoadOp) (opIdx : Nat) : CodeBuilder :=
  match op with
  | .addConst slot delta =>
    let label := s!"v_scratch_s{slot}"
    let cb := cb.emitInst I.clc
    let cb := cb.emitLdaAbsX label
    let cb := cb.emitInst (I.adc_imm delta.val.toUInt8)
    cb.emitStaAbsX label
  | .setConst slot value =>
    let cb := cb.emitInst (I.lda_imm value.val.toUInt8)
    cb.emitStaAbsX s!"v_scratch_s{slot}"
  | .addByFlag slot rules => Id.run do
    let doneLabel := s!"nload_op{opIdx}_done"
    let mut cb := cb
    cb := cb.emitInst (I.lda_imm 0)             -- default: A=0 (no-op delta)
    cb := cb.emitInst (I.sta_zp 0xF8)           -- $F8 = chosen delta
    let mut ruleIdx := 0
    for ⟨mask, value, delta⟩ in rules do
      let nextLabel := s!"nload_op{opIdx}_r{ruleIdx + 1}"
      cb := cb.emitInst (I.lda_zp 0xFB)
      cb := cb.emitInst (I.and_imm mask.val.toUInt8)
      cb := cb.emitInst ⟨.CMP, .imm value.val.toUInt8⟩
      cb := cb.emitBranch .BNE nextLabel
      cb := cb.emitInst (I.lda_imm delta.val.toUInt8)
      cb := cb.emitInst (I.sta_zp 0xF8)
      cb := cb.emitJmpLabel .JMP doneLabel
      cb := cb.label nextLabel
      ruleIdx := ruleIdx + 1
    cb := cb.label doneLabel
    let label := s!"v_scratch_s{slot}"
    cb := cb.emitInst I.clc
    cb := cb.emitLdaAbsX label
    cb := cb.emitInst (I.adc_zp 0xF8)
    cb := cb.emitStaAbsX label
    return cb
  | .resetIfNextEnds slot => Id.run do
    let skipLabel := s!"nload_op{opIdx}_noreset"
    let mut cb := cb
    cb := cb.emitInst (I.ldy_imm 0)
    cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
    cb := cb.emitBranch .BNE skipLabel
    cb := cb.emitInst (I.lda_imm 0)
    cb := cb.emitStaAbsX s!"v_scratch_s{slot}"
    return cb.label skipLabel
  | .incIfNextEnds slot delta => Id.run do
    let skipLabel := s!"nload_op{opIdx}_noinc"
    let mut cb := cb
    cb := cb.emitInst (I.ldy_imm 0)
    cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
    cb := cb.emitBranch .BNE skipLabel
    cb := cb.emitInst I.clc
    cb := cb.emitLdaAbsX s!"v_scratch_s{slot}"
    cb := cb.emitInst (I.adc_imm delta.val.toUInt8)
    cb := cb.emitStaAbsX s!"v_scratch_s{slot}"
    return cb.label skipLabel

-- Emit all noteLoadOps in sequence. Most ops act on $FB raw inst byte.
-- The "*IfNextEnds" ops are usually emitted AFTER pattern-pointer advance.
-- For now we emit them all together; caller responsibility to call this AFTER
-- pattern advance.
private def emitNoteLoadOps (cb : CodeBuilder) (ops : List USFNoteLoadOp) : CodeBuilder := Id.run do
  let mut cb := cb
  let mut idx := 0
  for op in ops do
    cb := emitNoteLoadOp cb op idx
    idx := idx + 1
  return cb

-- Emit pattern-end ops (X must be voice index).
private def emitPatternEndOp (cb : CodeBuilder) (op : USFPatternEndOp) : CodeBuilder :=
  match op with
  | .reset slot =>
    let cb := cb.emitInst (I.lda_imm 0)
    cb.emitStaAbsX s!"v_scratch_s{slot}"
  | .increment slot delta =>
    let cb := cb.emitInst I.clc
    let cb := cb.emitLdaAbsX s!"v_scratch_s{slot}"
    let cb := cb.emitInst (I.adc_imm delta.val.toUInt8)
    cb.emitStaAbsX s!"v_scratch_s{slot}"

private def emitPatternEndOps (cb : CodeBuilder) (ops : List USFPatternEndOp) : CodeBuilder :=
  ops.foldl (fun acc op => emitPatternEndOp acc op) cb

private def emitInit (cb : CodeBuilder) (song : USFSong) : CodeBuilder := Id.run do
  let mut cb := cb.label "init"

  -- Match Hubbard's init sequence:
  -- (sidplayfp pre-writes Vol=$0F before calling init)
  -- Then init: V1ctl=0, V2ctl=0 (twice), V3ctl=0, Vol=$0F again
  cb := cb.emitInst (I.lda_imm 0x00)
  cb := cb.emitInst (I.sta_abs (SID_BASE + 4))    -- V1ctl=0
  cb := cb.emitInst (I.sta_abs (SID_BASE + 11))   -- V2ctl=0
  cb := cb.emitInst (I.sta_abs (SID_BASE + 4))    -- V1ctl=0 (duplicate, matches Hubbard)
  cb := cb.emitInst (I.sta_abs (SID_BASE + 11))   -- V2ctl=0 (duplicate)
  cb := cb.emitInst (I.sta_abs (SID_BASE + 18))   -- V3ctl=0
  cb := cb.emitInst (I.lda_imm 0x0F)
  cb := cb.emitInst (I.sta_abs (SID_BASE + 0x18)) -- Vol=$0F

  -- Init voice state: set duration to 0 (force note load on first play)
  -- Also set orderlist position to 0 and load first pattern pointer
  cb := cb.emitInst (I.ldx_imm 0x02)
  cb := cb.label "init_loop"
  -- duration = 0
  cb := cb.emitInst (I.lda_imm 0x00)
  cb := cb.emitStaAbsX "v_dur"
  cb := cb.emitStaAbsX "v_olpos"
  cb := cb.emitStaAbsX "v_wptr"
  -- Load first pattern index from orderlist
  -- We need the orderlist pointer for this voice
  -- For init, we just set pattlo/hi to the first pattern's data address
  -- This will be handled by the noteload path on first play call
  cb := cb.emitStaAbsX "v_pattlo"
  cb := cb.emitStaAbsX "v_patthi"
  cb := cb.emitInst I.dex
  cb := cb.emitBranch .BPL "init_loop"

  -- Init frame counter to $FF (first INC → 0, matching Hubbard's reset)
  cb := cb.emitInst (I.lda_imm 0xFF)
  cb := cb.emitInst (I.sta_zp 0x50)

  cb := cb.emitInst I.rts
  return cb

private def emitPlay (cb : CodeBuilder) (song : USFSong) : CodeBuilder := Id.run do
  let mut cb := cb.label "play"

  -- Increment global frame counter (for arpeggio phase)
  cb := cb.emitInst (I.inc_zp 0x50)

  -- Apply dynamic freq-table updates with phase = atFrameStart
  cb := emitDynamicUpdatesForPhase cb song.engineQuirks.dynamicFreqEntries .atFrameStart

  -- Process voices in song order. Apply per-voice phase updates BEFORE each
  -- voice runs (so the voice sees the latest state from previous voices).
  let nVoices := song.voiceOrder.length
  for h : i in [:nVoices] do
    match song.voiceOrder[i]? with
    | some v =>
      cb := emitDynamicUpdatesForPhase cb song.engineQuirks.dynamicFreqEntries (.beforeVoice v)
      cb := cb.emitInst (I.ldx_imm v.val.toUInt8)
      if i + 1 < nVoices then
        cb := cb.emitJmpLabel .JSR "exec_voice"
      else
        cb := cb.emitJmpLabel .JMP "exec_voice"   -- tail call
    | none => pure ()
  return cb

mutual
def emitExecVoice (cb : CodeBuilder) (song : USFSong) : CodeBuilder := Id.run do
  let mut cb := cb.label "exec_voice"
  -- X = voice index (0/1/2) on entry, preserved throughout

  -- DEC v_dur[X] — if negative, load new note (far branch)
  cb := cb.emitDecAbsX "v_dur"
  cb := cb.emitBranch .BPL "sustain"              -- not expired → sustain
  cb := cb.emitJmpLabel .JMP "note_load"          -- expired → far jump to note load
  cb := cb.label "sustain"

  -- === SUSTAIN PATH (Hubbard order) ===
  -- Order: gate-off → vibrato → PW → freq_slide+ctrl → arpeggio
  cb := cb.emitInst (I.stx_zp 0xFA)              -- save voice index

  -- 1. GATE-OFF CHECK (fire when v_dur == gateOffFrames, i.e., 3 frames before end)
  -- Only fires once per note (the exact moment v_dur crosses threshold)
  cb := cb.emitLdaAbsX "v_dur"
  cb := cb.emitInst (I.cmp_imm 2)                  -- empirically tuned (was 3 in original)
  cb := cb.emitBranch .BNE "effects_start"          -- not equal → skip gate-off
  -- Gate off + zero ADSR
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay
  cb := cb.emitLdaAbsX "v_ctrl"
  cb := cb.emitInst (I.and_imm 0xFE)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 4))
  cb := cb.emitInst (I.lda_imm 0x00)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 5))
  cb := cb.emitInst (I.sta_absY (SID_BASE + 6))
  -- Fall through to effects: Hubbard runs PW/vibrato/etc. inline with gate-off,
  -- not as an early-out (writelog shows PWlo update on gate-off frame).

  cb := cb.label "effects_start"

  -- 2. VIBRATO (in separate function to avoid Lean elaborator depth limit)
  cb := emitVibrato cb song

  -- 3+ continues below
  cb := emitSustainEffects cb song
  return cb

def emitVibrato (cb : CodeBuilder) (_song : USFSong) : CodeBuilder := Id.run do
  let mut cb := cb
  -- If vib_depth > 0: compute LFO, modulate freq, write freq_lo/freq_hi to SID
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay                          -- Y = instrument
  cb := cb.emitInst ⟨.LDA, .absY 0⟩               -- i_vib[inst] (vib_depth, 0=none)
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_vib" } :: cb.absFixups }
  -- CLC here so the no-vibrato path enters PWM with C=0 (matching Hubbard's
  -- behavior where V3-style instruments hit linear PWM without leaking the
  -- prior gate-check carry). CLC doesn't touch Z so BNE below still works.
  cb := cb.emitInst I.clc
  cb := cb.emitBranch .BNE "has_vib"
  cb := cb.emitJmpLabel .JMP "no_vib"
  cb := cb.label "has_vib"
  cb := cb.emitInst (I.sta_zp 0xF7)               -- $F7 = vib_depth

  -- Triangle LFO: frame_counter & 7 → 0,1,2,3,3,2,1,0
  cb := cb.emitInst (I.lda_zp 0x50)               -- frame counter
  cb := cb.emitInst (I.and_imm 0x07)              -- 0-7
  cb := cb.emitInst (I.cmp_imm 4)
  cb := cb.emitBranch .BCC "vib_phase_ok"          -- < 4: keep
  cb := cb.emitInst (I.eor_imm 0x07)              -- >= 4: flip → 3,2,1,0
  cb := cb.label "vib_phase_ok"
  cb := cb.emitInst (I.sta_zp 0xF6)               -- $F6 = LFO step (0-3)

  -- Compute delta: (freq[pitch+1] - freq[pitch]) >> (vib_depth+1)
  -- Look up freq[pitch] and freq[pitch+1]
  cb := cb.emitLdaAbsX "v_pitch"
  cb := cb.emitInst I.tay                          -- Y = pitch
  cb := cb.emitLdaAbsY "freq_lo"
  cb := cb.emitInst (I.sta_zp 0xF8)               -- $F8 = base_flo
  cb := cb.emitLdaAbsY "freq_hi"
  cb := cb.emitInst (I.sta_zp 0xF9)               -- $F9 = base_fhi
  cb := cb.emitInst I.iny                          -- Y = pitch+1
  -- Compute 16-bit delta: freq[pitch+1] - freq[pitch].
  -- 6502 16-bit subtraction: lo first (sets borrow), then hi.
  cb := cb.emitInst I.sec
  cb := cb.emitLdaAbsY "freq_lo"                   -- next_flo
  cb := cb.emitInst (I.sbc_zp 0xF8)               -- delta_lo = next_flo - base_flo
  cb := cb.emitInst (I.sta_zp 0xF4)               -- $F4 = delta_lo
  cb := cb.emitLdaAbsY "freq_hi"                   -- next_fhi
  cb := cb.emitInst (I.sbc_zp 0xF9)               -- delta_hi = next_fhi - base_fhi - borrow
  cb := cb.emitInst (I.sta_zp 0xF5)               -- $F5 = delta_hi
  -- Right-shift the 16-bit delta semitoneShift times (das_model: lsr hi /
  -- ror lo, repeated). Our semitoneShift already encodes das_model's i_vib+1.
  cb := cb.label "vib_shift"
  cb := cb.emitInst ⟨.LSR, .zp 0xF5⟩              -- LSR delta_hi
  cb := cb.emitInst ⟨.ROR, .zp 0xF4⟩              -- ROR delta_lo (rotate carry in from hi)
  cb := cb.emitInst (I.dec_zp 0xF7)               -- dec vib_depth counter
  cb := cb.emitBranch .BNE "vib_shift"             -- loop while != 0
  -- $F4 = shifted delta_lo, $F5 = shifted delta_hi

  -- Start from base freq, add delta × LFO step
  -- vibrato_freq = base_freq + delta * step
  -- Check onset: durationFrames >= 21 for vibrato to be active.
  -- das_model: cmp #21 against dur*3 (= durationFrames in our units).
  -- Notes shorter than 7 ticks skip vibrato and just write base freq.
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_durfield"
  cb := cb.emitInst (I.cmp_imm 21)
  cb := cb.emitBranch .BCS "vib_onset_ok"          -- dur >= 21 frames: vibrato active
  -- dur < 6: write base freq directly
  cb := cb.emitJmpLabel .JMP "vib_write_base"
  cb := cb.label "vib_onset_ok"

  -- Load LFO step, DEY to check if 0
  cb := cb.emitInst (I.ldy_zp 0xF6)               -- Y = step
  cb := cb.emitInst I.dey                          -- Y--
  cb := cb.emitBranch .BMI "vib_write_base"        -- step was 0: no addition

  -- Add delta × step to base freq. Y is currently step-1 (post-DEY above).
  -- Loop runs exactly `step` times: das_model counts 0 < X <= step iterations.
  cb := cb.emitInst (I.lda_zp 0xF8)               -- base_flo
  cb := cb.emitInst (I.sta_zp 0xF2)               -- $F2 = target_lo
  cb := cb.emitInst (I.lda_zp 0xF9)               -- base_fhi
  cb := cb.emitInst (I.sta_zp 0xF3)               -- $F3 = target_hi

  cb := cb.label "vib_add_loop"
  cb := cb.emitInst I.clc
  cb := cb.emitInst (I.lda_zp 0xF2)
  cb := cb.emitInst (I.adc_zp 0xF4)               -- target_lo += delta_lo
  cb := cb.emitInst (I.sta_zp 0xF2)
  cb := cb.emitInst (I.lda_zp 0xF3)
  cb := cb.emitInst (I.adc_zp 0xF5)               -- target_hi += delta_hi + carry
  cb := cb.emitInst (I.sta_zp 0xF3)
  cb := cb.emitInst I.dey
  cb := cb.emitBranch .BPL "vib_add_loop"

  -- Write computed freq to SID
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay
  cb := cb.emitInst (I.lda_zp 0xF2)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 0))   -- freq_lo
  cb := cb.emitInst (I.lda_zp 0xF3)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 1))   -- freq_hi
  cb := cb.emitJmpLabel .JMP "no_vib"

  -- Write base freq (no vibrato modulation)
  cb := cb.label "vib_write_base"
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay
  cb := cb.emitInst (I.lda_zp 0xF8)               -- base_flo
  cb := cb.emitInst (I.sta_absY (SID_BASE + 0))
  cb := cb.emitInst (I.lda_zp 0xF9)               -- base_fhi
  cb := cb.emitInst (I.sta_absY (SID_BASE + 1))

  cb := cb.label "no_vib"
  cb := cb.emitInst (I.ldx_zp 0xFA)               -- restore X = voice
  return cb

def emitSustainEffects (cb : CodeBuilder) (song : USFSong) : CodeBuilder := Id.run do
  let mut cb := cb
  -- 3. PW MODULATION
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay
  cb := cb.emitInst ⟨.LDA, .absY 0⟩               -- pw_speed[inst]
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_pwspeed" } :: cb.absFixups }
  cb := cb.emitBranch .BNE "pw_has_speed"
  cb := cb.emitJmpLabel .JMP "pw_done"
  cb := cb.label "pw_has_speed"
  cb := cb.emitInst (I.sta_zp 0xF9)               -- $F9 = speed
  cb := cb.emitInst ⟨.LDA, .absY 0⟩               -- pw_mode[inst]
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_pwmode" } :: cb.absFixups }
  -- Mode encoding (bit 7) lets us branch via BMI without disturbing C.
  -- Hubbard's linear-PW path (no CLC before ADC) deliberately leaks the
  -- carry from vibrato's last high-byte ADC into PWM speed, giving an
  -- occasional +1 to PW lo on vibrato-overflow frames. Preserve C from
  -- vibrato all the way to the ADC at line below.
  cb := cb.emitBranch .BMI "pw_linear"             -- bit 7 set → linear
  cb := cb.emitJmpLabel .JMP "pw_bidir"
  cb := cb.label "pw_linear"

  -- PW state is per-INSTRUMENT (mutable i_pwlo/i_pwhi/i_pwdir tables),
  -- not per-voice. das_model: when a voice retriggers a previously-used
  -- instrument (e.g. V3 cycles inst 2 -> 3 -> 2), the PW counter resumes
  -- from where that instrument left off. v_inst[X] gives Y = inst index.
  cb := cb.emitInst (I.ldx_zp 0xFA)               -- X = voice
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay                          -- Y = inst (preserved across PW)

  -- LINEAR PW. NOTE: no CLC — we deliberately use C from vibrato's last
  -- high-byte ADC, matching Hubbard's $5237 path. This is what makes orig
  -- PW lo occasionally +speed+1 instead of +speed.
  cb := cb.emitLdaAbsY "i_pwlo"
  cb := cb.emitInst (I.adc_zp 0xF9)
  cb := cb.emitStaAbsY "i_pwlo"
  cb := cb.emitInst (I.sta_zp 0xF8)               -- save new pwlo
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay                          -- Y = sidoff (clobbers inst Y)
  cb := cb.emitInst (I.lda_zp 0xF8)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 2))
  cb := cb.emitJmpLabel .JMP "pw_done"

  -- BIDIRECTIONAL PW
  cb := cb.label "pw_bidir"
  cb := cb.emitLdaAbsY "i_pwdir"
  cb := cb.emitBranch .BNE "pw_bidir_down"
  -- Up: i_pwlo += speed, i_pwhi += carry, mask hi to 4 bits
  cb := cb.emitInst I.clc
  cb := cb.emitLdaAbsY "i_pwlo"
  cb := cb.emitInst (I.adc_zp 0xF9)
  cb := cb.emitStaAbsY "i_pwlo"
  cb := cb.emitLdaAbsY "i_pwhi"
  cb := cb.emitInst (I.adc_imm 0)
  cb := cb.emitInst (I.and_imm 0x0F)
  cb := cb.emitStaAbsY "i_pwhi"
  -- Compare i_pwhi with i_pwmax, flip direction if equal
  cb := cb.emitInst ⟨.CMP, .absY 0⟩
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_pwmax" } :: cb.absFixups }
  cb := cb.emitBranch .BNE "pw_bidir_write"
  cb := cb.emitInst (I.lda_imm 1)
  cb := cb.emitStaAbsY "i_pwdir"
  cb := cb.emitJmpLabel .JMP "pw_bidir_write"
  -- Down: i_pwlo -= speed, i_pwhi -= borrow, mask hi to 4 bits
  cb := cb.label "pw_bidir_down"
  cb := cb.emitInst I.sec
  cb := cb.emitLdaAbsY "i_pwlo"
  cb := cb.emitInst (I.sbc_zp 0xF9)
  cb := cb.emitStaAbsY "i_pwlo"
  cb := cb.emitLdaAbsY "i_pwhi"
  cb := cb.emitInst (I.sbc_imm 0)
  cb := cb.emitInst (I.and_imm 0x0F)
  cb := cb.emitStaAbsY "i_pwhi"
  -- Compare i_pwhi with i_pwmin (hardcoded $08 in Hubbard, but we honor i_pwmin)
  cb := cb.emitInst ⟨.CMP, .absY 0⟩
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_pwmin" } :: cb.absFixups }
  cb := cb.emitBranch .BNE "pw_bidir_write"
  cb := cb.emitInst (I.lda_imm 0)
  cb := cb.emitStaAbsY "i_pwdir"
  -- Write PW to SID. Y is currently inst; switch to sidoff.
  cb := cb.label "pw_bidir_write"
  cb := cb.emitLdaAbsY "i_pwlo"
  cb := cb.emitInst (I.sta_zp 0xF8)               -- save pwlo
  cb := cb.emitLdaAbsY "i_pwhi"
  cb := cb.emitInst (I.sta_zp 0xF7)               -- save pwhi (was old-inst slot, no longer needed here)
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay
  cb := cb.emitInst (I.lda_zp 0xF8)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 2))
  cb := cb.emitInst (I.lda_zp 0xF7)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 3))
  cb := cb.label "pw_done"

  -- 4. FREQ SLIDE (bit0) + CTRL WRITE
  -- Hubbard: if bit0=0, skip entire section.
  -- If bit0=1: check guards (fhi≠0, countdown≠0), then check note age.
  -- Path A (note not at start): DEC fhi, write OLD fhi, write ctrl (gate cleared)
  -- Path B (note at start): write fhi (no DEC), write ctrl=$80 (noise)
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay
  cb := cb.emitInst ⟨.LDA, .absY 0⟩               -- i_bit0[inst]
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_bit0" } :: cb.absFixups }
  cb := cb.emitBranch .BNE "has_slide"
  cb := cb.emitJmpLabel .JMP "no_slide"
  cb := cb.label "has_slide"

  -- Guard: skip if fhi == 0
  cb := cb.emitLdaAbsX "v_fhi"
  cb := cb.emitBranch .BNE "fhi_ok"
  cb := cb.emitJmpLabel .JMP "no_slide"
  cb := cb.label "fhi_ok"

  -- Guard: skip slide entirely once we are at/past the gate-off frame.
  -- das_model uses `cmp #4 / bcc skip` on its dur*3 countdown; ours is
  -- (dur-1) so the equivalent threshold is v_dur < 3 (gate-off fires at
  -- v_dur == 2). This matches Hubbard's behavior of leaving the voice
  -- alone once release starts.
  cb := cb.emitLdaAbsX "v_dur"
  cb := cb.emitInst (I.cmp_imm 3)
  cb := cb.emitBranch .BCS "dur_ok"
  cb := cb.emitJmpLabel .JMP "no_slide"
  cb := cb.label "dur_ok"

  -- Check note age: (dur_field - 1) * tempo vs countdown
  -- Hubbard countdown is in ticks; ours is in frames. Multiply threshold by tempo.
  cb := cb.emitInst I.sec
  -- USF v3: v_durfield is in FRAMES. Hubbard guard "dur_ticks - 1 < countdown_frames"
  -- equates to: skip until countdown <= (dur_ticks - 1)*tempo = (durationFrames/tempo - 1)*tempo
  -- For Commando tempo=3: skip until countdown <= durationFrames - tempo = durationFrames - 3.
  -- So compare (durationFrames - tempo) with countdown.
  cb := cb.emitLdaAbsX "v_durfield"
  cb := cb.emitInst (I.sbc_imm 4)                 -- A = durationFrames - 4 (empirically tuned for Hubbard)
  cb := cb.emitInst ⟨.CMP, .absX 0⟩               -- cmp countdown
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "v_dur" } :: cb.absFixups }

  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay                          -- Y = SID offset

  cb := cb.emitBranch .BCC "slide_path_b"          -- dur_field-1 < countdown → Path B

  -- PATH A: DEC freq_hi, write OLD, write ctrl (gate cleared)
  -- Use i_ctrl[inst] (static instrument ctrl byte), NOT waveform program
  -- Hubbard reads $54F8,X which is the cached instrument ctrl byte
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay
  cb := cb.emitInst ⟨.LDA, .absY 0⟩               -- i_ctrl[inst]
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_ctrl" } :: cb.absFixups }
  cb := cb.emitInst (I.sta_zp 0xFB)               -- save ctrl

  -- DEC fhi, write OLD value to SID
  cb := cb.emitLdaAbsX "v_fhi"                     -- A = old fhi
  cb := cb.emitInst (I.sta_zp 0xF8)               -- save old fhi
  cb := cb.emitDecAbsX "v_fhi"                     -- decrement in memory
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay                          -- Y = SID offset
  cb := cb.emitInst (I.lda_zp 0xF8)               -- A = old fhi
  cb := cb.emitInst (I.sta_absY (SID_BASE + 1))   -- write freq_hi
  -- Write ctrl with gate cleared
  cb := cb.emitInst (I.lda_zp 0xFB)               -- ctrl from waveform
  cb := cb.emitInst (I.and_imm 0xFE)              -- clear gate
  cb := cb.emitInst (I.sta_absY (SID_BASE + 4))   -- write ctrl

  cb := cb.emitJmpLabel .JMP "slide_done"

  -- PATH B: no DEC, write fhi + ctrl=$80
  cb := cb.label "slide_path_b"
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_fhi"
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay
  cb := cb.emitLdaAbsX "v_fhi"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 1))   -- write freq_hi (no DEC)
  cb := cb.emitInst (I.lda_imm 0x80)              -- noise waveform
  cb := cb.emitInst (I.sta_absY (SID_BASE + 4))   -- write ctrl=$80

  cb := cb.label "slide_done"
  cb := cb.label "no_slide"

  -- 5. ARPEGGIO
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay
  cb := cb.emitInst ⟨.LDA, .absY 0⟩               -- i_arp[inst]
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_arp" } :: cb.absFixups }
  cb := cb.emitBranch .BNE "has_arp"
  cb := cb.emitJmpLabel .JMP "sustain_done"
  cb := cb.label "has_arp"
  cb := cb.emitInst (I.sta_zp 0xF8)               -- $F8 = arp_offset
  cb := cb.emitInst (I.lda_zp 0x50)               -- frame counter
  cb := cb.emitInst (I.and_imm 0x01)              -- bit 0
  cb := cb.emitBranch .BEQ "arp_base"
  -- Odd frame: pitch + arp_offset
  cb := cb.emitInst I.clc
  cb := cb.emitLdaAbsX "v_pitch"
  cb := cb.emitInst (I.adc_zp 0xF8)
  cb := cb.emitJmpLabel .JMP "arp_write"
  cb := cb.label "arp_base"
  cb := cb.emitLdaAbsX "v_pitch"
  cb := cb.label "arp_write"
  -- Lookup freq and write
  cb := cb.emitInst I.tay                          -- Y = pitch
  cb := cb.emitLdaAbsY "freq_hi"
  cb := cb.emitInst (I.sta_zp 0xF9)
  cb := cb.emitLdaAbsY "freq_lo"
  cb := cb.emitInst (I.sta_zp 0xF8)
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay
  cb := cb.emitInst (I.lda_zp 0xF9)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 1))   -- freq_hi
  cb := cb.emitInst (I.lda_zp 0xF8)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 0))   -- freq_lo

  cb := cb.label "sustain_done"
  cb := cb.emitInst I.rts

  -- Continue with note load path (split for Lean elaborator depth)
  cb := emitNoteLoadPath cb song
  return cb

def emitNoteLoadPath (cb : CodeBuilder) (song : USFSong) : CodeBuilder := Id.run do
  let mut cb := cb

  -- === NOTE LOAD ===
  cb := cb.label "note_load"

  -- Save voice index to $FA (scratch, used throughout)
  cb := cb.emitInst (I.stx_zp 0xFA)

  -- Load pattern pointer into $FC/$FD
  cb := cb.emitLdaAbsX "v_pattlo"
  cb := cb.emitInst (I.sta_zp 0xFC)
  cb := cb.emitLdaAbsX "v_patthi"
  cb := cb.emitInst (I.sta_zp 0xFD)

  -- Check if pointer is zero (first call, not yet initialized) — far branch
  cb := cb.emitInst (I.ora_zp 0xFC)
  cb := cb.emitBranch .BNE "ptr_ok"
  cb := cb.emitJmpLabel .JMP "advance_order"
  cb := cb.label "ptr_ok"

  -- Read note: pitch at ($FC),0 / duration at ($FC),1 / instrument at ($FC),2
  cb := cb.emitInst (I.ldy_imm 0x00)
  cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
  -- End of pattern check — far branch
  cb := cb.emitBranch .BNE "has_note"
  cb := cb.emitJmpLabel .JMP "advance_order"
  cb := cb.label "has_note"
  cb := cb.emitInst (I.sta_zp 0xFE)              -- $FE = pitch

  cb := cb.emitInst I.iny
  cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
  cb := cb.emitInst (I.sta_zp 0xFF)              -- $FF = duration

  cb := cb.emitInst I.iny
  cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
  cb := cb.emitInst (I.sta_zp 0xFB)              -- $FB = raw inst byte (with bits 6/7 flags if preserved)

  -- Engine-quirks note-load operations (data-driven from song.engineQuirks).
  -- These act on per-voice scratch slots and may peek $FB raw inst byte.
  -- The "*IfNextEnds" ops happen later (after pattern advance) - we filter here.
  let preAdvanceOps := song.engineQuirks.noteLoadOps.filter fun op => match op with
    | .resetIfNextEnds _ => false
    | .incIfNextEnds _ _ => false
    | _                  => true
  cb := emitNoteLoadOps cb preAdvanceOps

  -- Mask off flag bits so $FB holds clean inst index for table lookups (only
  -- if quirks asked to preserve them; otherwise pattern data already clean).
  -- For tie notes (pitch=$FD), DON'T update v_inst[X] either - v_inst keeps
  -- the previous note's inst index so subsequent SID writes use the correct
  -- instrument's i_ctrl/i_ad/i_sr/i_pwlo values. das_model's v_hubt/v_hub2
  -- paths reuse the previous inst ($A2/$B6) for the same reason.
  if song.engineQuirks.preserveNoteFlags then
    cb := cb.emitInst (I.lda_zp 0xFB)
    cb := cb.emitInst (I.and_imm 0x3F)
    cb := cb.emitInst (I.sta_zp 0xFB)

  -- Advance pattern pointer by 3
  cb := cb.emitInst I.clc
  cb := cb.emitInst (I.lda_zp 0xFC)
  cb := cb.emitInst (I.adc_imm 3)
  cb := cb.emitInst (I.sta_zp 0xFC)
  cb := cb.emitInst (I.lda_zp 0xFD)
  cb := cb.emitInst (I.adc_imm 0)
  cb := cb.emitInst (I.sta_zp 0xFD)

  -- Save pattern pointer back to voice state
  cb := cb.emitInst (I.ldx_zp 0xFA)              -- X = voice index
  cb := cb.emitInst (I.lda_zp 0xFC)
  cb := cb.emitStaAbsX "v_pattlo"
  cb := cb.emitInst (I.lda_zp 0xFD)
  cb := cb.emitStaAbsX "v_patthi"

  -- Engine-quirks lookahead ops: peek next note byte, fire if end-of-pattern.
  let postAdvanceOps := song.engineQuirks.noteLoadOps.filter fun op => match op with
    | .resetIfNextEnds _ => true
    | .incIfNextEnds _ _ => true
    | _                  => false
  cb := emitNoteLoadOps cb postAdvanceOps

  -- Save raw duration field for freq slide guard
  cb := cb.emitInst (I.lda_zp 0xFF)
  cb := cb.emitStaAbsX "v_durfield"

  -- USF v3: durationFrames is in frames. Subtract 1 for DEC-first model.
  cb := cb.emitInst (I.lda_zp 0xFF)
  cb := cb.emitInst I.sec
  cb := cb.emitInst (I.sbc_imm 1)
  cb := cb.emitStaAbsX "v_dur"

  -- Store NEW instrument index in voice state. EXCEPT for tie notes (pitch
  -- $FD) which keep the previous v_inst so downstream SID writes use the
  -- correct instrument's tables. das_model's v_hubt/v_hub2 paths do the
  -- same (don't update $A2/$B6 for tie/legato notes).
  cb := cb.emitInst (I.lda_zp 0xFE)              -- pitch
  cb := cb.emitInst (I.cmp_imm 0xFD)
  cb := cb.emitBranch .BEQ "skip_v_inst_update"
  cb := cb.emitInst (I.lda_zp 0xFB)
  cb := cb.emitStaAbsX "v_inst"
  cb := cb.label "skip_v_inst_update"

  -- Reset waveform pointer to 0
  -- First sustain frame will re-read waveform[0] (same as noteLoad ctrl)
  -- then advance to 1. This costs 1 frame delay but is simple and safe.
  cb := cb.emitInst (I.lda_imm 0)
  cb := cb.emitStaAbsX "v_wptr"

  -- Write SID registers: freq, ctrl, pw, adsr
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay                        -- Y = SID offset

  -- TIE-NOTE HANDLING: pitch byte $FD means "no new pitch" (legato).
  -- Skip the freq write + v_pitch/v_fhi updates, but still do Ctrl (with
  -- gate cleared by das_model's i_ctrl & FE convention - we'll handle that
  -- by using v_inst[voice] which has the previous inst).
  cb := cb.emitInst (I.lda_zp 0xFE)
  cb := cb.emitInst (I.cmp_imm 0xFD)
  cb := cb.emitBranch .BEQ "tie_skip_pitch"

  -- Frequency lookup (Hubbard order: freq_hi BEFORE freq_lo). For dynamic
  -- table slots (e.g. T[104]), the freq_lo/freq_hi tables already hold the
  -- per-frame updated values (see engineQuirks.dynamicFreqEntries).
  cb := cb.emitInst (I.ldx_zp 0xFE)              -- X = pitch
  cb := cb.emitLdaAbsX "freq_hi"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 1))
  cb := cb.emitLdaAbsX "freq_lo"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 0))

  -- Save pitch and freq_hi for effects
  cb := cb.emitInst (I.ldx_zp 0xFA)               -- X = voice
  cb := cb.emitInst (I.lda_zp 0xFE)               -- pitch
  cb := cb.emitStaAbsX "v_pitch"
  cb := cb.emitInst (I.ldx_zp 0xFE)               -- X = pitch
  cb := cb.emitLdaAbsX "freq_hi"
  cb := cb.emitInst (I.ldx_zp 0xFA)               -- X = voice
  cb := cb.emitStaAbsX "v_fhi"

  cb := cb.label "tie_skip_pitch"
  -- Instrument lookups: X = instrument from v_inst (which we deliberately
  -- DON'T update for tie notes - so this gets the previous note's inst,
  -- giving the right ctrl/pw/adsr table values).
  cb := cb.emitInst (I.ldx_zp 0xFA)              -- X = voice
  cb := cb.emitLdaAbsX "v_inst"                  -- A = v_inst[voice]
  cb := cb.emitInst (I.sta_zp 0xFB)              -- $FB = effective inst
  cb := cb.emitInst I.tax                         -- X = inst

  -- Ctrl: tie notes (pitch=$FD) write i_ctrl & $FE to SID so gate stays
  -- cleared (das_model's v_tie). The RAW i_ctrl (gate-on) is what gets
  -- saved to v_ctrl[X] for the sustain path & dynamic T[104] update -
  -- mirrors das_model saving raw to $C3/$A4 etc. before AND #$FE.
  cb := cb.emitLdaAbsX "i_ctrl"
  cb := cb.emitInst I.pha                         -- save RAW ctrl (for sustain v_ctrl)
  cb := cb.emitInst (I.sta_zp 0xF7)               -- and to scratch for SID write
  cb := cb.emitInst (I.lda_zp 0xFE)               -- pitch
  cb := cb.emitInst (I.cmp_imm 0xFD)
  cb := cb.emitBranch .BNE "ctrl_no_tie"
  cb := cb.emitInst (I.lda_zp 0xF7)
  cb := cb.emitInst (I.and_imm 0xFE)              -- tie: clear gate for SID
  cb := cb.emitInst (I.sta_zp 0xF7)
  cb := cb.label "ctrl_no_tie"
  cb := cb.emitInst (I.lda_zp 0xF7)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 4))
  -- Note: A no longer holds the saved value; the PHA above saved the raw ctrl.
  -- The PLA further down (line ~916) restores raw ctrl into v_ctrl[X].

  -- PW: i_pwlo/i_pwhi are mutable per-instrument running counters.
  -- Write the current state to SID. No reset on retrigger - the instrument's
  -- counter persists across notes (and across other voices using the same
  -- instrument), matching Hubbard's i_pwlo,X-as-state convention.
  -- (X = NEW inst from line 700; Y = sidoff from earlier.)
  cb := cb.emitLdaAbsX "i_pwlo"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 2))
  cb := cb.emitLdaAbsX "i_pwhi"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 3))

  -- ADSR
  cb := cb.emitLdaAbsX "i_ad"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 5))
  cb := cb.emitLdaAbsX "i_sr"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 6))

  -- Store ctrl in voice state for sustain path
  cb := cb.emitInst I.pla                         -- ctrl from stack
  cb := cb.emitInst (I.ldx_zp 0xFA)              -- X = voice index
  cb := cb.emitStaAbsX "v_ctrl"

  cb := cb.label "noteload_done"
  cb := cb.emitInst I.rts

  -- === ADVANCE ORDERLIST ===
  cb := cb.label "advance_order"
  cb := cb.emitInst (I.ldx_zp 0xFA)              -- X = voice index

  -- Engine-quirks pattern-end ops (data-driven from song.engineQuirks)
  cb := emitPatternEndOps cb song.engineQuirks.patternEndOps

  -- Read pattern index from orderlist
  -- Each voice has its own orderlist. We store per-voice orderlist pointers.
  cb := cb.emitLdaAbsX "v_olpos"
  cb := cb.emitInst I.tay                         -- Y = orderlist position

  -- Look up the orderlist entry: need voice-specific orderlist base address
  -- We'll use per-voice orderlist pointer tables (ol_lo, ol_hi)
  cb := cb.emitLdaAbsX "ol_lo"
  cb := cb.emitInst (I.sta_zp 0xFC)
  cb := cb.emitLdaAbsX "ol_hi"
  cb := cb.emitInst (I.sta_zp 0xFD)

  -- Read pattern index at orderlist[olpos]
  cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩           -- A = pattern index
  cb := cb.emitInst (I.cmp_imm 0xFF)
  cb := cb.emitBranch .BEQ "ol_end_or_loop"       -- $FF = end of orderlist

  -- Look up pattern data address from pattern pointer table
  cb := cb.emitInst I.tay                          -- Y = pattern index
  cb := cb.emitLdaAbsY "patt_ptr_lo"
  cb := cb.emitStaAbsX "v_pattlo"
  cb := cb.emitLdaAbsY "patt_ptr_hi"
  cb := cb.emitStaAbsX "v_patthi"

  -- Advance orderlist position
  cb := cb.emitIncAbsX "v_olpos"

  -- Jump back to note_load to read the first note
  cb := cb.emitJmpLabel .JMP "note_load"

  -- Orderlist hit $FF marker: peek next byte for loop point.
  -- $FF in next byte = song actually ends; else byte = new olpos.
  cb := cb.label "ol_end_or_loop"
  cb := cb.emitInst I.iny                         -- Y = position of loop byte
  cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
  cb := cb.emitInst (I.cmp_imm 0xFF)
  cb := cb.emitBranch .BEQ "song_end"
  cb := cb.emitStaAbsX "v_olpos"                   -- loop back: olpos = loop byte
  cb := cb.emitJmpLabel .JMP "advance_order"

  -- Song end: set long duration to stop
  cb := cb.label "song_end"
  cb := cb.emitInst (I.lda_imm 0x7F)
  cb := cb.emitStaAbsX "v_dur"
  cb := cb.emitInst I.rts

  return cb

end  -- mutual

-- ==========================================================================
-- Top-level SID generation
-- ==========================================================================

def generateSID (song : USFSong) (debug : Bool := false) : Bytes := Id.run do
  let base : UInt16 := 0x1000
  let mut cb : CodeBuilder := { baseAddr := base }

  -- Jump table
  cb := cb.emitJmpLabel .JMP "init"
  cb := cb.emitJmpLabel .JMP "play"

  -- Player code
  cb := emitInit cb song
  cb := emitPlay cb song
  cb := emitExecVoice cb song

  -- === DATA TABLES ===

  -- Frequency table (split lo/hi)
  -- Frequency table: entry 104 is dynamic (ctrl byte, 0 at init)
  -- Compute set of freq slots that are dynamic (referenced by engineQuirks)
  let dynSlots : List Nat := song.engineQuirks.dynamicFreqEntries.map (·.freqSlot)
  cb := cb.label "freq_lo"
  for hi : i in [:song.freqTable.entries.length] do
    if dynSlots.contains i then cb := cb.label s!"freq_lo_{i}"
    match song.freqTable.entries[i]? with
    | some p => cb := cb.emitByte (if dynSlots.contains i then 0 else p.1.val.toUInt8)
    | none => cb := cb.emitByte 0
  cb := cb.label "freq_hi"
  for hi : i in [:song.freqTable.entries.length] do
    if dynSlots.contains i then cb := cb.label s!"freq_hi_{i}"
    match song.freqTable.entries[i]? with
    | some p => cb := cb.emitByte (if dynSlots.contains i then 0 else p.2.val.toUInt8)
    | none => cb := cb.emitByte 0

  -- Waveform data: all instruments' waveform steps concatenated
  let mut waveData : List UInt8 := []
  let mut waveBases : List UInt8 := []
  let mut waveLens : List UInt8 := []
  let mut waveLoops : List UInt8 := []
  for inst in song.instruments do
    waveBases := waveBases ++ [waveData.length.toUInt8]
    waveLens := waveLens ++ [inst.waveformProgram.length.toUInt8]
    waveLoops := waveLoops ++ [inst.waveLoop.toUInt8]
    waveData := waveData ++ inst.waveformProgram.map (·.val.toUInt8)

  cb := cb.label "wave_data"
  cb := cb.emitData waveData
  cb := cb.label "i_wavebase"
  cb := cb.emitData waveBases
  cb := cb.label "i_wavelen"
  cb := cb.emitData waveLens
  cb := cb.label "i_waveloop"
  cb := cb.emitData waveLoops

  -- Instrument tables (USF v3 — direct field access, no nested effectChain)
  cb := cb.label "i_ctrl"
  cb := cb.emitData (song.instruments.map fun i => i.initCtrl.val.toUInt8)
  cb := cb.label "i_pwlo"
  cb := cb.emitData (song.instruments.map fun i => i.initPwLo.val.toUInt8)
  cb := cb.label "i_pwhi"
  cb := cb.emitData (song.instruments.map fun i => i.initPwHi.val.toUInt8)
  cb := cb.label "i_ad"
  cb := cb.emitData (song.instruments.map fun i => i.ad.val.toUInt8)
  cb := cb.label "i_sr"
  cb := cb.emitData (song.instruments.map fun i => i.sr.val.toUInt8)
  -- PW: speed/mode/min/max derived from optional pwMod
  cb := cb.label "i_pwspeed"
  cb := cb.emitData (song.instruments.map fun i => match i.pwMod with
    | none => (0 : UInt8)
    | some pm => match pm.mode with
      | .linear sp => sp.val.toUInt8
      | .bidirectional sp _ _ => sp.val.toUInt8
      | .table _ => 0)
  cb := cb.label "i_pwmode"
  -- Bit 7 = linear (so BMI selects it without touching C; see emitSustainEffects).
  cb := cb.emitData (song.instruments.map fun i => match i.pwMod with
    | none => (0 : UInt8)
    | some pm => match pm.mode with
      | .linear _ => 0x80
      | .bidirectional _ _ _ => 0x01
      | .table _ => 0)
  cb := cb.label "i_pwmin"
  cb := cb.emitData (song.instruments.map fun i => match i.pwMod with
    | some { mode := .bidirectional _ minHi _, .. } => minHi.val.toUInt8
    | _ => 0)
  cb := cb.label "i_pwmax"
  cb := cb.emitData (song.instruments.map fun i => match i.pwMod with
    | some { mode := .bidirectional _ _ maxHi, .. } => maxHi.val.toUInt8
    | _ => 0)
  -- Mutable per-instrument PW direction (0 = up, 1 = down). Persists across
  -- voices so that re-triggering an instrument resumes its bidirectional state.
  cb := cb.label "i_pwdir"
  cb := cb.emitData (song.instruments.map fun _ => (0 : UInt8))
  -- Vibrato depth (0 = none, 1-3 = depth shift)
  cb := cb.label "i_vib"
  cb := cb.emitData (song.instruments.map fun i =>
    match i.vibrato with
    | some spec => spec.semitoneShift.toUInt8
    | none => 0)

  -- Arpeggio offset (0 = none, 12 = octave, etc.)
  cb := cb.label "i_arp"
  cb := cb.emitData (song.instruments.map fun i =>
    match i.arpeggio with
    | some spec => match spec.intervals[1]? with
      | some v => v.toNat.toUInt8
      | none => 0
    | none => 0)
  -- Freq slide flag (0 = none, 1 = active)
  cb := cb.label "i_bit0"
  cb := cb.emitData (song.instruments.map fun i =>
    match i.freqSlide with
    | some _ => (1 : UInt8)
    | none => 0)

  -- Pattern data: [pitch, duration, instrument]* per pattern, 0x00 = end
  -- For now, encode percussion .dynamicCtrl as pitch=104 to match old player behavior
  let mut patPtrLo : List UInt8 := []
  let mut patPtrHi : List UInt8 := []
  for pat in song.patterns do
    let addr := cb.currentAddr
    patPtrLo := patPtrLo ++ [addr.toUInt8]
    patPtrHi := patPtrHi ++ [(addr >>> 8).toUInt8]
    for note in pat.notes do
      let pitchByte : UInt8 := match note.kind with
        | .pitched p => p.val.toUInt8
        | .percussion _ => 104       -- TODO: distinguish noiseHit vs dynamicCtrl
        | .rest => 0xFE              -- TODO: rest handling
        | .tie => 0xFD               -- TODO: tie handling
      cb := cb.emitByte pitchByte
      cb := cb.emitByte note.durationFrames.toUInt8
      cb := cb.emitByte note.instrument.toUInt8
    cb := cb.emitByte 0x00

  cb := cb.label "patt_ptr_lo"
  cb := cb.emitData patPtrLo
  cb := cb.label "patt_ptr_hi"
  cb := cb.emitData patPtrHi

  -- Orderlist data per voice + build pointer tables.
  -- Layout: [entries..., $FF, loopPoint_or_FF].
  -- When advance_order reads $FF, it consults the next byte: if $FF, song
  -- ends; otherwise that byte is the new orderlist position (loop back).
  let mut olLo : List UInt8 := []
  let mut olHi : List UInt8 := []
  for vi in [:song.voices.length] do
    match song.voices[vi]? with
    | some voiceSpec =>
      let addr := cb.currentAddr
      olLo := olLo ++ [addr.toUInt8]
      olHi := olHi ++ [(addr >>> 8).toUInt8]
      cb := cb.emitData (voiceSpec.orderlist.map (·.toUInt8))
      cb := cb.emitByte 0xFF
      let loopByte : UInt8 := match voiceSpec.loopPoint with
        | some p => p.toUInt8
        | none   => 0xFF
      cb := cb.emitByte loopByte
    | none =>
      olLo := olLo ++ [0]
      olHi := olHi ++ [0]

  -- Voice state variables (3 bytes each, indexed by voice 0/1/2)
  cb := cb.label "v_dur"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_pattlo"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_patthi"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_olpos"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_ctrl"
  cb := cb.label "v_ctrl_0"
  cb := cb.emitByte 0
  cb := cb.label "v_ctrl_1"
  cb := cb.emitByte 0
  cb := cb.label "v_ctrl_2"
  cb := cb.emitByte 0
  cb := cb.label "v_wptr"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_inst"
  cb := cb.label "v_inst_v0"
  cb := cb.emitByte 0
  cb := cb.label "v_inst_v1"
  cb := cb.emitByte 0
  cb := cb.label "v_inst_v2"
  cb := cb.emitByte 0
  cb := cb.label "v_pitch"
  cb := cb.label "v_pitch_v0"
  cb := cb.emitByte 0
  cb := cb.label "v_pitch_v1"
  cb := cb.emitByte 0
  cb := cb.label "v_pitch_v2"
  cb := cb.emitByte 0
  cb := cb.label "v_fhi"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_durfield"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_pwlo"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_pwhi"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_pwdir"
  cb := cb.emitData [0, 0, 0]
  -- Per-voice scratch slots from engineQuirks.voiceScratch.
  -- Each scratch slot allocates 3 bytes (one per voice), with v_scratch_s{N}
  -- (start of array) and v_scratch_s{N}_v{V} (per-voice byte) labels.
  for hi : si in [:song.engineQuirks.voiceScratch.length] do
    match song.engineQuirks.voiceScratch[si]? with
    | some scratch =>
      let init := scratch.initial.val.toUInt8
      cb := cb.label s!"v_scratch_s{si}"
      cb := cb.label s!"v_scratch_s{si}_v0"
      cb := cb.emitByte init
      cb := cb.label s!"v_scratch_s{si}_v1"
      cb := cb.emitByte init
      cb := cb.label s!"v_scratch_s{si}_v2"
      cb := cb.emitByte init
    | none => pure ()
  -- Constants
  cb := cb.label "v_sidoff"
  cb := cb.emitData [0, 7, 14]
  cb := cb.label "ol_lo"
  cb := cb.emitData olLo
  cb := cb.label "ol_hi"
  cb := cb.emitData olHi

  -- Resolve all forward references
  cb := cb.resolve

  let header : PSIDHeader := {
    initAddr := base
    playAddr := base + 3
    title := "Commando"
    author := "Rob Hubbard"
    released := "1985 Elite"
  }
  return buildSID header cb.bytes

def writeFile (path : String) (data : Bytes) : IO Unit := do
  let handle ← IO.FS.Handle.mk path .write
  handle.write ⟨data⟩

def sidgenMainV3 : IO Unit := do
  let sid := generateSID commandoV3
  writeFile "commando_v3.sid" sid
  IO.println s!"Generated commando_v3.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {commandoV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {commandoV3.instruments.length}"
  IO.println s!"  Patterns: {commandoV3.patterns.length}"
  IO.println s!"  Voices: {commandoV3.voices.length}"

end V3
