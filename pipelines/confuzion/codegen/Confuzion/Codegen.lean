/-
  Confuzion.Codegen — Player codegen for Rob Hubbard's Confuzion on the Run,
  consuming a `USFSong` and emitting a `ByteArray` PSID. Verified status:
  Grade A 98.8% snapshot match in siddump; 0 register-divergence across
  1500 frames in py65.

  Cloned from Commando.Codegen. Differences from that codegen, ALL
  Confuzion-specific, are flagged inline:
  - Skydive emit block (between freqSlide and arpeggio) — gated on
    `i_skydive[inst]`.
  - v_pitch alias-store in `emitNL_SavePitchFhi` — mirrors V1/V2/V3
    notenum writes into freq table slots 105.hi / 106.lo / 106.hi to
    replicate Hubbard's notenum/freq-table memory overlap.
  - PWM init data (v_pwperiod = [0,1,$1D], v_pwdir = [1,0,0]) extracted
    from the original binary at $84E5..$84EA.
  - HR threshold = 1 (vs Commando's 2) — different engine timing.

  ─── Table of contents ────────────────────────────────────────────────
  §1  CodeBuilder + assembly helpers
  §2  USFNoteLoadOp emission
  §3  init — subtune dispatch, SID silence, voice-state init
  §4  play — frame counter + per-voice loop dispatch
  §5  note_load — emitNL_* sub-blocks (incl. v_pitch alias-store for
                  Hubbard's notenum overlap)
  §6  sustain effects — vibrato, PW, freqSlide, *SKYDIVE*, arpeggio,
                        gate check
  §7  Data tables                        (freq, instruments inc. i_skydive)
  §8  generateSID                        (top-level orchestration)
  ──────────────────────────────────────────────────────────────────────
-/

import Confuzion.SID
import Confuzion.Asm6502
import Confuzion.PSIDFile
import Confuzion.USF
import Confuzion.Constants

namespace ConfuzionNS

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

-- Emit LDA abs ($AD) with forward ref and record fixup
def emitLdaAbs (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xAD, 0, 0], absFixups := fixup :: cb.absFixups }

-- Emit STA abs ($8D) with forward ref and record fixup
def emitStaAbs (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0x8D, 0, 0], absFixups := fixup :: cb.absFixups }

-- Emit CMP abs,X ($DD) with forward ref and record fixup
def emitCmpAbsX (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xDD, 0, 0], absFixups := fixup :: cb.absFixups }

-- Emit CMP abs,Y ($D9) with forward ref and record fixup
def emitCmpAbsY (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xD9, 0, 0], absFixups := fixup :: cb.absFixups }

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
def emitDynRefLoad (cb : CodeBuilder) (ref : USFDynRef) : CodeBuilder :=
  match ref with
  | .constant b   => cb.emitInst (I.lda_imm b.val.toUInt8)
  | .scratch v slot => cb.emitLdaAbs s!"v_scratch_s{slot}_v{v.val}"
  | .voiceCtrl v    => cb.emitLdaAbs s!"v_ctrl_{v.val}"
  | .voicePitch v   => cb.emitLdaAbs s!"v_pitch_v{v.val}"
  | .voiceInst v    => cb.emitLdaAbs s!"v_inst_v{v.val}"

-- Emit STA A to a freq table slot (lo or hi half).
def emitFreqSlotStore (cb : CodeBuilder) (whichLo : Bool) (slot : Nat) : CodeBuilder :=
  cb.emitStaAbs (if whichLo then s!"freq_lo_{slot}" else s!"freq_hi_{slot}")

-- Emit code for one dynamic freq entry (load lo source -> STA freq_lo_slot, ditto hi).
def emitDynamicFreqEntry (cb : CodeBuilder) (e : USFDynamicFreqEntry) : CodeBuilder :=
  let cb := emitDynRefLoad cb e.loSource
  let cb := emitFreqSlotStore cb true e.freqSlot
  let cb := emitDynRefLoad cb e.hiSource
  emitFreqSlotStore cb false e.freqSlot

/-- True iff the entry's phase matches the requested update phase. -/
def phaseMatches (entryPhase requested : USFUpdatePhase) : Bool :=
  match entryPhase, requested with
  | .atFrameStart, .atFrameStart   => true
  | .beforeVoice a, .beforeVoice b => a.val == b.val
  | _, _                            => false

/-- Emit code for one entry if its phase matches; otherwise no-op. -/
def emitDynamicEntryIfPhase (phase : USFUpdatePhase) (cb : CodeBuilder)
    (e : USFDynamicFreqEntry) : CodeBuilder :=
  if phaseMatches e.phase phase then emitDynamicFreqEntry cb e else cb

-- Emit dynamic freq updates for entries matching a particular phase.
def emitDynamicUpdatesForPhase (cb : CodeBuilder)
    (entries : List USFDynamicFreqEntry) (phase : USFUpdatePhase) : CodeBuilder :=
  entries.foldl (emitDynamicEntryIfPhase phase) cb

/-- One iteration of the `.addByFlag` rule loop: test (FB & mask == value),
    if so write delta to $F8 and JMP to doneLabel; else fall through past
    the per-rule label to the next rule. Refactored from the inline
    `for ⟨mask, value, delta⟩ in rules do ...` body so that
    `List.foldl_preserves_fixupsInBounds` can be applied directly. -/
def emitFlagRule (opIdx : Nat) (doneLabel : String) (cb : CodeBuilder)
    (ruleAndIdx : (USFByte × USFByte × USFByte) × Nat) : CodeBuilder :=
  let nextLabel := s!"nload_op{opIdx}_r{ruleAndIdx.2 + 1}"
  let mask  := ruleAndIdx.1.1
  let value := ruleAndIdx.1.2.1
  let delta := ruleAndIdx.1.2.2
  let cb := cb.emitInst (I.lda_zp 0xFB)
  let cb := cb.emitInst (I.and_imm mask.val.toUInt8)
  let cb := cb.emitInst ⟨.CMP, .imm value.val.toUInt8⟩
  let cb := cb.emitBranch .BNE nextLabel
  let cb := cb.emitInst (I.lda_imm delta.val.toUInt8)
  let cb := cb.emitInst (I.sta_zp 0xF8)
  let cb := cb.emitJmpLabel .JMP doneLabel
  cb.label nextLabel

-- Emit a per-voice noteLoadOp (X must be voice index, $FB has raw inst byte).
-- For "*IfNextEnds" ops, caller must set up Y=0 and have $FC pointing to next note.
def emitNoteLoadOp (cb : CodeBuilder) (op : USFNoteLoadOp) (opIdx : Nat) : CodeBuilder :=
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
  | .addByFlag slot rules =>
    let doneLabel := s!"nload_op{opIdx}_done"
    let label := s!"v_scratch_s{slot}"
    let cb := cb.emitInst (I.lda_imm 0)         -- default: A=0 (no-op delta)
    let cb := cb.emitInst (I.sta_zp 0xF8)       -- $F8 = chosen delta
    let indexed := rules.zip (List.range rules.length)
    let cb := indexed.foldl (emitFlagRule opIdx doneLabel) cb
    let cb := cb.label doneLabel
    let cb := cb.emitInst I.clc
    let cb := cb.emitLdaAbsX label
    let cb := cb.emitInst (I.adc_zp 0xF8)
    cb.emitStaAbsX label
  | .resetIfNextEnds slot =>
    let skipLabel := s!"nload_op{opIdx}_noreset"
    let cb := cb.emitInst (I.ldy_imm 0)
    let cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
    let cb := cb.emitBranch .BNE skipLabel
    let cb := cb.emitInst (I.lda_imm 0)
    let cb := cb.emitStaAbsX s!"v_scratch_s{slot}"
    cb.label skipLabel
  | .incIfNextEnds slot delta =>
    let skipLabel := s!"nload_op{opIdx}_noinc"
    let cb := cb.emitInst (I.ldy_imm 0)
    let cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
    let cb := cb.emitBranch .BNE skipLabel
    let cb := cb.emitInst I.clc
    let cb := cb.emitLdaAbsX s!"v_scratch_s{slot}"
    let cb := cb.emitInst (I.adc_imm delta.val.toUInt8)
    let cb := cb.emitStaAbsX s!"v_scratch_s{slot}"
    cb.label skipLabel

-- Emit all noteLoadOps in sequence. Most ops act on $FB raw inst byte.
-- The "*IfNextEnds" ops are usually emitted AFTER pattern-pointer advance.
def emitNoteLoadOps (cb : CodeBuilder) (ops : List USFNoteLoadOp) : CodeBuilder :=
  (ops.zip (List.range ops.length)).foldl
    (fun cb opAndIdx => emitNoteLoadOp cb opAndIdx.1 opAndIdx.2) cb

-- Emit pattern-end ops (X must be voice index).
def emitPatternEndOp (cb : CodeBuilder) (op : USFPatternEndOp) : CodeBuilder :=
  match op with
  | .reset slot =>
    let cb := cb.emitInst (I.lda_imm 0)
    cb.emitStaAbsX s!"v_scratch_s{slot}"
  | .increment slot delta =>
    let cb := cb.emitInst I.clc
    let cb := cb.emitLdaAbsX s!"v_scratch_s{slot}"
    let cb := cb.emitInst (I.adc_imm delta.val.toUInt8)
    cb.emitStaAbsX s!"v_scratch_s{slot}"

def emitPatternEndOps (cb : CodeBuilder) (ops : List USFPatternEndOp) : CodeBuilder :=
  ops.foldl (fun acc op => emitPatternEndOp acc op) cb

-- emitInit factored into named sub-blocks. Each sub-block is small enough
-- (3-9 ops) that PropertiesV3 can prove `fixupsInBounds`-preservation
-- against it without hitting Lean's whnf heartbeat budget — the
-- bottleneck that stopped a single monolithic proof from compiling.
-- Composition of the sub-blocks reproduces the original semantics.

-- The sub-blocks are written as plain `let` chains rather than
-- `Id.run do` + `let mut`. They produce the same nested function-call
-- term, but `unfold` exposes that term *directly* — no `simp` reduction
-- of the `Id` monad needed. This is what makes the per-block
-- preservation proofs in PropertiesV3 fit inside the default heartbeat
-- budget.

/-- Subtune dispatch part 1: bound-clamp subtune index in A, save and
    multiply by 3 to get a byte offset into the subtune-major tables. -/
def emitInitSubtuneClamp (cb : CodeBuilder) (song : USFSong) : CodeBuilder :=
  let cb := cb.emitInst (I.cmp_imm song.subtunes.length.toUInt8)
  let cb := cb.emitBranch .BCC "subtune_in_range"
  let cb := cb.emitInst (I.lda_imm 0)
  let cb := cb.label "subtune_in_range"
  let cb := cb.emitInst (I.sta_zp 0xFB)               -- save subtune
  let cb := cb.emitInst I.asl_a                        -- A = 2*subtune
  let cb := cb.emitInst I.clc
  let cb := cb.emitInst (I.adc_zp 0xFB)               -- A = 3*subtune
  let cb := cb.emitInst I.tay
  cb

/-- Subtune dispatch part 2: copy 3 bytes ol_subtune_*[Y..Y+2] →
    ol_*[0..2]. X iterates 0..2 in an asm-level loop. -/
def emitInitSubtuneCopy (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ldx_imm 0)
  let cb := cb.label "subtune_copy"
  let cb := cb.emitLdaAbsY "ol_subtune_lo"
  let cb := cb.emitStaAbsX "ol_lo"
  let cb := cb.emitLdaAbsY "ol_subtune_hi"
  let cb := cb.emitStaAbsX "ol_hi"
  let cb := cb.emitInst I.iny
  let cb := cb.emitInst I.inx
  let cb := cb.emitInst ⟨.CPX, .imm 3⟩
  let cb := cb.emitBranch .BNE "subtune_copy"
  cb

/-- Match Hubbard's SID-silence init sequence: write 0 to all three
    voices' control registers (V2 twice, matching Hubbard exactly), then
    Vol=$0F. -/
def emitInitSidSilence (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.lda_imm 0x00)
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 4))    -- V1ctl=0
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 11))   -- V2ctl=0
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 4))    -- V1ctl=0 (duplicate, matches Hubbard)
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 11))   -- V2ctl=0 (duplicate)
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 18))   -- V3ctl=0
  let cb := cb.emitInst (I.lda_imm 0x0F)
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 0x18)) -- Vol=$0F
  cb

/-- Voice-state init: zero v_dur/olpos/wptr/pattlo/patthi for all three
    voices via an asm-level loop on X. Forces note-load on first play. -/
def emitInitVoiceState (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ldx_imm 0x02)
  let cb := cb.label "init_loop"
  let cb := cb.emitInst (I.lda_imm 0x00)
  let cb := cb.emitStaAbsX "v_dur"
  let cb := cb.emitStaAbsX "v_olpos"
  let cb := cb.emitStaAbsX "v_wptr"
  let cb := cb.emitStaAbsX "v_pattlo"
  let cb := cb.emitStaAbsX "v_patthi"
  let cb := cb.emitInst I.dex
  let cb := cb.emitBranch .BPL "init_loop"
  cb

/-- Frame counter to $FF (first INC → 0, matches Hubbard) and RTS back
    to PSID. -/
def emitInitFrameCounter (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.lda_imm 0xFF)
  let cb := cb.emitInst (I.sta_zp 0x50)
  let cb := cb.emitInst I.rts
  cb

def emitInit (cb : CodeBuilder) (song : USFSong) : CodeBuilder :=
  let cb := cb.label "init"
  let cb := emitInitSubtuneClamp cb song
  let cb := emitInitSubtuneCopy cb
  let cb := emitInitSidSilence cb
  let cb := emitInitVoiceState cb
  let cb := emitInitFrameCounter cb
  cb

-- emitPlay sub-blocks. Same plain-let / no-Id-monad style as emitInit
-- so the per-block preservation proofs in PropertiesV3 stay tractable.

/-- Header: label "play" + INC the global frame counter at $50. -/
def emitPlayHeader (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "play"
  let cb := cb.emitInst (I.inc_zp 0x50)
  cb

/-- Per-voice step inside the loop: apply per-voice dynamic-freq updates,
    load X with the voice index, then JSR (or tail-JMP for the last
    voice — `idxAndLast.snd` is true on the last iteration). Used as
    the body of a `foldl`. -/
def emitPlayVoiceStep (song : USFSong) (cb : CodeBuilder)
    (idxAndLast : Nat × Bool) : CodeBuilder :=
  match song.voiceOrder[idxAndLast.fst]? with
  | none   => cb
  | some v =>
    let cb := emitDynamicUpdatesForPhase cb
                song.engineQuirks.dynamicFreqEntries (.beforeVoice v)
    let cb := cb.emitInst (I.ldx_imm v.val.toUInt8)
    if idxAndLast.snd then
      cb.emitJmpLabel .JMP "exec_voice"   -- tail call on the last voice
    else
      cb.emitJmpLabel .JSR "exec_voice"

/-- Loop body: process every voice in song order. The last voice tail-
    JMPs into exec_voice; the others JSR. Iteration is over
    `List.range nVoices` so the existing `foldl` preservation lemma
    applies directly (no `Std.Range.forIn` machinery to reason about). -/
def emitPlayVoiceLoop (cb : CodeBuilder) (song : USFSong) : CodeBuilder :=
  let nVoices := song.voiceOrder.length
  let indices := (List.range nVoices).map (fun i => (i, i + 1 == nVoices))
  indices.foldl (emitPlayVoiceStep song) cb

def emitPlay (cb : CodeBuilder) (song : USFSong) : CodeBuilder :=
  let cb := emitPlayHeader cb
  let cb := emitDynamicUpdatesForPhase cb
              song.engineQuirks.dynamicFreqEntries .atFrameStart
  let cb := emitPlayVoiceLoop cb song
  cb

-- ==========================================================================
-- emitNoteLoadPath sub-blocks. Same plain-let / no-Id-monad style as
-- emitInit and emitPlay so per-block fixupsInBounds preservation proofs
-- in PropertiesV3 stay tractable. Every block matches one section of
-- the original Id.run do body byte-for-byte.
-- ==========================================================================

/-- Note-load entry: label "note_load", save voice index to $FA, load
    pattern pointer (v_pattlo / v_patthi) into $FC/$FD. -/
def emitNL_Header (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "note_load"
  let cb := cb.emitInst (I.stx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_pattlo"
  let cb := cb.emitInst (I.sta_zp 0xFC)
  let cb := cb.emitLdaAbsX "v_patthi"
  let cb := cb.emitInst (I.sta_zp 0xFD)
  cb

/-- Pattern-pointer-zero check: if zero, jump to advance_order to load
    the orderlist's first pattern. (Far branch via JMP because
    advance_order may be > +127 bytes away.) -/
def emitNL_PtrCheck (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ora_zp 0xFC)
  let cb := cb.emitBranch .BNE "ptr_ok"
  let cb := cb.emitJmpLabel .JMP "advance_order"
  let cb := cb.label "ptr_ok"
  cb

/-- Read pitch byte from (FC),0. End-of-pattern check ($00) far-jumps to
    advance_order. -/
def emitNL_ReadPitch (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ldy_imm 0x00)
  let cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
  let cb := cb.emitBranch .BNE "has_note"
  let cb := cb.emitJmpLabel .JMP "advance_order"
  let cb := cb.label "has_note"
  let cb := cb.emitInst (I.sta_zp 0xFE)
  cb

/-- Read duration ($FF), inst byte ($FB), and porta byte (v_porta[X])
    from (FC),1..3. -/
def emitNL_ReadDurInstPorta (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst I.iny
  let cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
  let cb := cb.emitInst (I.sta_zp 0xFF)
  let cb := cb.emitInst I.iny
  let cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
  let cb := cb.emitInst (I.sta_zp 0xFB)
  let cb := cb.emitInst I.iny
  let cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitStaAbsX "v_porta"
  cb

/-- Pre-advance noteLoadOps: filter out the *IfNextEnds variants (those
    fire AFTER pattern advance) and emit the rest. -/
def emitNL_PreAdvanceOps (cb : CodeBuilder) (song : USFSong) : CodeBuilder :=
  let preOps := song.engineQuirks.noteLoadOps.filter fun op => match op with
    | .resetIfNextEnds _ => false
    | .incIfNextEnds _ _ => false
    | _                  => true
  emitNoteLoadOps cb preOps

/-- Extract per-note no_release (bit 5) and no_inst_byte (bit 7) flags
    from the raw inst byte at $FB into the v_no_release / v_no_inst_byte
    arrays. -/
def emitNL_ExtractFlags (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.lda_zp 0xFB)
  let cb := cb.emitInst (I.and_imm 0x20)
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitStaAbsX "v_no_release"
  let cb := cb.emitInst (I.lda_zp 0xFB)
  let cb := cb.emitInst (I.and_imm 0x80)
  let cb := cb.emitStaAbsX "v_no_inst_byte"
  cb

/-- Mask off flag bits in $FB so it holds a clean inst index (only when
    `preserveNoteFlags` is set; otherwise pattern data is already clean). -/
def emitNL_PreserveMask (cb : CodeBuilder) (song : USFSong) : CodeBuilder :=
  if song.engineQuirks.preserveNoteFlags then
    let cb := cb.emitInst (I.lda_zp 0xFB)
    let cb := cb.emitInst (I.and_imm 0x1F)
    cb.emitInst (I.sta_zp 0xFB)
  else
    cb

/-- Advance the pattern pointer at $FC/$FD by 4 (pitch + dur + inst +
    porta), then write back to v_pattlo / v_patthi. -/
def emitNL_AdvancePtr (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst I.clc
  let cb := cb.emitInst (I.lda_zp 0xFC)
  let cb := cb.emitInst (I.adc_imm 4)
  let cb := cb.emitInst (I.sta_zp 0xFC)
  let cb := cb.emitInst (I.lda_zp 0xFD)
  let cb := cb.emitInst (I.adc_imm 0)
  let cb := cb.emitInst (I.sta_zp 0xFD)
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitInst (I.lda_zp 0xFC)
  let cb := cb.emitStaAbsX "v_pattlo"
  let cb := cb.emitInst (I.lda_zp 0xFD)
  let cb := cb.emitStaAbsX "v_patthi"
  cb

/-- Post-advance lookahead noteLoadOps (the *IfNextEnds variants). -/
def emitNL_PostAdvanceOps (cb : CodeBuilder) (song : USFSong) : CodeBuilder :=
  let postOps := song.engineQuirks.noteLoadOps.filter fun op => match op with
    | .resetIfNextEnds _ => true
    | .incIfNextEnds _ _ => true
    | _                  => false
  emitNoteLoadOps cb postOps

/-- Save raw duration field for the freq-slide guard, then compute
    (durationFrames - 1) and store as v_dur (DEC-first model). -/
def emitNL_DurField (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.lda_zp 0xFF)
  let cb := cb.emitStaAbsX "v_durfield"
  let cb := cb.emitInst (I.lda_zp 0xFF)
  let cb := cb.emitInst I.sec
  let cb := cb.emitInst (I.sbc_imm 1)
  let cb := cb.emitStaAbsX "v_dur"
  cb

/-- Update v_inst[X] = inst, skipping for tie notes (pitch=$FD) and
    no_inst_byte notes (bit 7 set in raw inst byte). -/
def emitNL_UpdateVInst (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.lda_zp 0xFE)
  let cb := cb.emitInst (I.cmp_imm 0xFD)
  let cb := cb.emitBranch .BEQ "skip_v_inst_update"
  let cb := cb.emitLdaAbsX "v_no_inst_byte"
  let cb := cb.emitBranch .BNE "skip_v_inst_update"
  let cb := cb.emitInst (I.lda_zp 0xFB)
  let cb := cb.emitStaAbsX "v_inst"
  let cb := cb.label "skip_v_inst_update"
  cb

/-- Reset waveform pointer (v_wptr[X] = 0) and load Y with v_sidoff[X]
    for downstream STA absY writes. -/
def emitNL_ResetAndSidoff (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.lda_imm 0)
  let cb := cb.emitStaAbsX "v_wptr"
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  cb

/-- Tie-note check: if pitch == $FD, skip past the freq writes (jump to
    "tie_skip_pitch"). -/
def emitNL_TieCheck (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.lda_zp 0xFE)
  let cb := cb.emitInst (I.cmp_imm 0xFD)
  let cb := cb.emitBranch .BEQ "tie_skip_pitch"
  cb

/-- Frequency lookup + write to SID (Hubbard order: hi before lo). X = pitch. -/
def emitNL_FreqWrite (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ldx_zp 0xFE)
  let cb := cb.emitLdaAbsX "freq_hi"
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 1))
  let cb := cb.emitLdaAbsX "freq_lo"
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 0))
  cb

/-- Initialise the porta accumulator (v_porta_lo/hi[X]) from the base
    frequency for the new pitch. -/
def emitNL_PortaInit (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitLdaAbsX "freq_lo"
  let cb := cb.emitInst (I.sta_zp 0xF8)
  let cb := cb.emitLdaAbsX "freq_hi"
  let cb := cb.emitInst (I.sta_zp 0xF9)
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitInst (I.lda_zp 0xF8)
  let cb := cb.emitStaAbsX "v_porta_lo"
  let cb := cb.emitInst (I.lda_zp 0xF9)
  let cb := cb.emitStaAbsX "v_porta_hi"
  cb

/-- Restore Y = v_sidoff[X], X = pitch (set up after PortaInit
    clobbered both registers). -/
def emitNL_RestoreXY (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let cb := cb.emitInst (I.ldx_zp 0xFE)
  cb

/-- Save pitch (-> v_pitch[voice]) and freq_hi[pitch] (-> v_fhi[voice])
    for use by sustain-path effects. Voice index restored to X afterwards.

    Hubbard quirk: in the original player, V1/V2/V3 `notenum` storage
    overlaps the freq table at offsets equivalent to pitches 105.hi,
    106.lo, 106.hi. After STA v_pitch,X we mirror the pitch into those
    freq table slots so V2's vibrato (which reads pitch 105.hi for
    delta_hi computation) sees V1's current notenum. -/
def emitNL_SavePitchFhi (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitInst (I.lda_zp 0xFE)
  let cb := cb.emitStaAbsX "v_pitch"
  -- A still = pitch. Branch on X to mirror into the right freq table slot.
  let cb := cb.emitInst ⟨.CPX, .imm 0⟩
  let cb := cb.emitBranch .BNE "alias_v1_v2"
  let cb := cb.emitStaAbs "freq_hi_105"
  let cb := cb.emitJmpLabel .JMP "alias_done"
  let cb := cb.label "alias_v1_v2"
  let cb := cb.emitInst ⟨.CPX, .imm 1⟩
  let cb := cb.emitBranch .BNE "alias_v2"
  let cb := cb.emitStaAbs "freq_lo_106"
  let cb := cb.emitJmpLabel .JMP "alias_done"
  let cb := cb.label "alias_v2"
  let cb := cb.emitStaAbs "freq_hi_106"
  let cb := cb.label "alias_done"
  -- Continue: load freq_hi[pitch] -> v_fhi[voice]
  let cb := cb.emitInst (I.ldx_zp 0xFE)
  let cb := cb.emitLdaAbsX "freq_hi"
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitStaAbsX "v_fhi"
  cb

/-- Tie-note merge label + load effective inst from v_inst[voice] into
    A, $FB, and X. -/
def emitNL_TieSkipLabel (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "tie_skip_pitch"
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_inst"
  let cb := cb.emitInst (I.sta_zp 0xFB)
  let cb := cb.emitInst I.tax
  cb

/-- Ctrl byte write: tie notes write `i_ctrl & $FE` to clear the gate;
    non-tie writes raw i_ctrl. The raw ctrl is PHA'd for the sustain-
    path v_ctrl save further down. -/
def emitNL_CtrlWrite (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitLdaAbsX "i_ctrl"
  let cb := cb.emitInst I.pha
  let cb := cb.emitInst (I.sta_zp 0xF7)
  let cb := cb.emitInst (I.lda_zp 0xFE)
  let cb := cb.emitInst (I.cmp_imm 0xFD)
  let cb := cb.emitBranch .BNE "ctrl_no_tie"
  let cb := cb.emitInst (I.lda_zp 0xF7)
  let cb := cb.emitInst (I.and_imm 0xFE)
  let cb := cb.emitInst (I.sta_zp 0xF7)
  let cb := cb.label "ctrl_no_tie"
  let cb := cb.emitInst (I.lda_zp 0xF7)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 4))
  cb

/-- Write i_pwlo/i_pwhi (pulse width) and i_ad/i_sr (ADSR) to SID. -/
def emitNL_PWADSRWrite (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitLdaAbsX "i_pwlo"
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 2))
  let cb := cb.emitLdaAbsX "i_pwhi"
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 3))
  let cb := cb.emitLdaAbsX "i_ad"
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 5))
  let cb := cb.emitLdaAbsX "i_sr"
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 6))
  cb

/-- Initialise the per-voice PWM period sub-counter from the instrument's
    pwm_speed byte. Hubbard observation: without this, V3 player fires
    its first bidirectional PW step at frame 2 instead of waiting the
    full period. Commando's bidirectional instruments all have
    `pwm_speed & 0x1F = 0` so the init value is 0 — preserving its
    byte-perfect behavior. -/
def emitNL_PwperiodInit (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitLdaAbsX "i_pwspeed"     -- X = inst here
  let cb := cb.emitInst (I.and_imm 0x1F)   -- mask to period bits
  let cb := cb.emitInst (I.ldx_zp 0xFA)    -- X = voice
  let cb := cb.emitStaAbsX "v_pwperiod"
  cb

/-- PLA the raw ctrl saved earlier, store to v_ctrl[voice], emit the
    "noteload_done" label and RTS. -/
def emitNL_SaveCtrlAndReturn (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst I.pla
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitStaAbsX "v_ctrl"
  let cb := cb.label "noteload_done"
  let cb := cb.emitInst I.rts
  cb

/-- "advance_order" entry: reload X = voice index, then run engine-
    quirks pattern-end ops (data-driven from song.engineQuirks). -/
def emitNL_AdvanceOrderHeader (cb : CodeBuilder) (song : USFSong) : CodeBuilder :=
  let cb := cb.label "advance_order"
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := emitPatternEndOps cb song.engineQuirks.patternEndOps
  cb

/-- Load orderlist pointer from per-voice ol_lo/ol_hi tables, position
    Y at v_olpos[X]. Result: (FC),Y points at the next pattern index. -/
def emitNL_LookupOL (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitLdaAbsX "v_olpos"
  let cb := cb.emitInst I.tay
  let cb := cb.emitLdaAbsX "ol_lo"
  let cb := cb.emitInst (I.sta_zp 0xFC)
  let cb := cb.emitLdaAbsX "ol_hi"
  let cb := cb.emitInst (I.sta_zp 0xFD)
  cb

/-- Read pattern index from orderlist; if $FF, jump to ol_end_or_loop.
    Otherwise look up its address in patt_ptr_lo/hi, store back to
    v_pattlo/hi, INC v_olpos, and JMP back to note_load. -/
def emitNL_ReadAndDispatch (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
  let cb := cb.emitInst (I.cmp_imm 0xFF)
  let cb := cb.emitBranch .BEQ "ol_end_or_loop"
  let cb := cb.emitInst I.tay
  let cb := cb.emitLdaAbsY "patt_ptr_lo"
  let cb := cb.emitStaAbsX "v_pattlo"
  let cb := cb.emitLdaAbsY "patt_ptr_hi"
  let cb := cb.emitStaAbsX "v_patthi"
  let cb := cb.emitIncAbsX "v_olpos"
  let cb := cb.emitJmpLabel .JMP "note_load"
  cb

/-- Orderlist hit $FF marker: peek next byte for loop point. $FF =
    actual song end (jump to song_end); else byte = new olpos. -/
def emitNL_OLEndOrLoop (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "ol_end_or_loop"
  let cb := cb.emitInst I.iny
  let cb := cb.emitInst ⟨.LDA, .indY 0xFC⟩
  let cb := cb.emitInst (I.cmp_imm 0xFF)
  let cb := cb.emitBranch .BEQ "song_end"
  let cb := cb.emitStaAbsX "v_olpos"
  let cb := cb.emitJmpLabel .JMP "advance_order"
  cb

/-- Song-end stop block: set v_dur = $7F (large) so the voice never
    expires again, and RTS. -/
def emitNL_SongEnd (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "song_end"
  let cb := cb.emitInst (I.lda_imm 0x7F)
  let cb := cb.emitStaAbsX "v_dur"
  let cb := cb.emitInst I.rts
  cb

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

  -- 1. GATE-OFF CHECK (fire when v_dur == gateOffFrames, i.e., before note end)
  -- Only fires once per note (the exact moment v_dur crosses threshold).
  -- Orig Confuzion: HR fires 2 frames before note-load (writelog trace), so the
  -- threshold here is v_dur == 1 for Confuzion. Commando used cmp_imm 2; the
  -- difference is engine timing (`speed`/tempo bookkeeping shifts when v_dur
  -- crosses each value).
  cb := cb.emitLdaAbsX "v_dur"
  cb := cb.emitInst (I.cmp_imm 1)
  cb := cb.emitBranch .BNE "effects_start"          -- not equal → skip gate-off
  -- Skip HR if current note has no_release flag set: gate stays on into the
  -- next note so the SID envelope doesn't retrigger across the boundary
  -- (Hubbard portamento/legato semantics).
  cb := cb.emitLdaAbsX "v_no_release"
  cb := cb.emitBranch .BNE "effects_start"
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

  -- 2a. PORTAMENTO. When v_porta[X] is non-zero, slide the per-voice freq
  -- accumulator each frame and write it directly to the SID, jumping past
  -- vibrato (orig disables vibrato modulation while a porta slide is in
  -- progress — the freq evolution is purely linear). Hubbard porta byte:
  -- bits 1-6 = step size, bit 0 = direction (0 = up, 1 = down).
  cb := cb.emitLdaAbsX "v_porta"
  cb := cb.emitBranch .BNE "porta_active"
  cb := cb.emitJmpLabel .JMP "no_porta"
  cb := cb.label "porta_active"
  cb := cb.emitInst (I.and_imm 0x7E)             -- step size in lo-byte units
  cb := cb.emitInst (I.sta_zp 0xF6)              -- $F6 = step
  cb := cb.emitLdaAbsX "v_porta"
  cb := cb.emitInst (I.and_imm 0x01)             -- direction bit
  cb := cb.emitBranch .BNE "porta_down"
  -- Up: v_porta_lo += step, v_porta_hi += carry
  cb := cb.emitInst I.clc
  cb := cb.emitLdaAbsX "v_porta_lo"
  cb := cb.emitInst (I.adc_zp 0xF6)
  cb := cb.emitStaAbsX "v_porta_lo"
  cb := cb.emitLdaAbsX "v_porta_hi"
  cb := cb.emitInst (I.adc_imm 0)
  cb := cb.emitStaAbsX "v_porta_hi"
  cb := cb.emitJmpLabel .JMP "porta_write"
  cb := cb.label "porta_down"
  cb := cb.emitInst I.sec
  cb := cb.emitLdaAbsX "v_porta_lo"
  cb := cb.emitInst (I.sbc_zp 0xF6)
  cb := cb.emitStaAbsX "v_porta_lo"
  cb := cb.emitLdaAbsX "v_porta_hi"
  cb := cb.emitInst (I.sbc_imm 0)
  cb := cb.emitStaAbsX "v_porta_hi"
  cb := cb.label "porta_write"
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_porta_lo"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 0))
  cb := cb.emitLdaAbsX "v_porta_hi"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 1))
  cb := cb.emitJmpLabel .JMP "porta_done"
  cb := cb.label "no_porta"

  -- 2. VIBRATO (in separate function to avoid Lean elaborator depth limit)
  cb := emitVibrato cb song

  cb := cb.label "porta_done"
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
  -- v_pwdir is PER-VOICE (Hubbard $5510,X) — direction persists across notes
  -- on the same voice even when the instrument changes. Y is currently the
  -- instrument index (used for pwlo/pwhi/min/max lookup); X is the voice
  -- index (used for the direction flag).
  cb := cb.label "pw_bidir"
  -- Hubbard's bidirectional PWM period sub-counter (hubbard_emu.py
  -- _apply_pw lines 819-830 in src/hubbard_emu.py).
  -- pwm_speed encodes BOTH period and step:
  --   lower 5 bits (pwm_speed & $1F) = period reload value
  --   upper 3 bits (pwm_speed & $E0) = step size
  -- DEC v_pwperiod,X; BPL pw_done  — skip step if period not yet expired.
  -- Then reload v_pwperiod from speed & $1F and mask $F9 down to the step.
  -- Commando's instruments have period=0 so this collapses to "step every
  -- frame with step=$E0" — same as the old code path.
  cb := cb.emitDecAbsX "v_pwperiod"
  cb := cb.emitBranch .BPL "pw_done"
  cb := cb.emitInst (I.lda_zp 0xF9)              -- pwm_speed (full byte)
  cb := cb.emitInst (I.and_imm 0x1F)             -- period reload value
  cb := cb.emitStaAbsX "v_pwperiod"
  cb := cb.emitInst (I.lda_zp 0xF9)
  cb := cb.emitInst (I.and_imm 0xE0)             -- step size
  cb := cb.emitInst (I.sta_zp 0xF9)              -- replace speed-in-F9 with step
  cb := cb.emitLdaAbsX "v_pwdir"
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
  cb := cb.emitStaAbsX "v_pwdir"
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
  cb := cb.emitStaAbsX "v_pwdir"
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

  -- 4b. SKYDIVE (bit 1 of original Hubbard instrfx).
  -- Hubbard's pulsework → drums → skydive → octarp order. Skydive runs
  -- every OTHER frame (when frame_counter & 1 != 0), guarded by v_fhi != 0:
  --   LDA savefreqhi,x; BEQ skip; DEC savefreqhi,x; STA $d401,y
  -- The SID write uses the OLD value (LDA before DEC). Skydive does NOT
  -- touch ctrl (unlike drums which writes $80 noise on onset). This block
  -- only fires when i_skydive[v_inst] is set.
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay
  cb := cb.emitInst ⟨.LDA, .absY 0⟩               -- i_skydive[inst]
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_skydive" } :: cb.absFixups }
  cb := cb.emitBranch .BEQ "no_sky"
  cb := cb.emitInst (I.lda_zp 0x50)               -- frame counter
  cb := cb.emitInst (I.and_imm 0x01)
  cb := cb.emitBranch .BEQ "no_sky"               -- even counter: skip
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_fhi"
  cb := cb.emitBranch .BEQ "no_sky"               -- v_fhi == 0: skip
  cb := cb.emitInst (I.sta_zp 0xF8)               -- save OLD v_fhi
  cb := cb.emitDecAbsX "v_fhi"                     -- v_fhi -= 1
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay                          -- Y = SID offset
  cb := cb.emitInst (I.lda_zp 0xF8)               -- reload OLD
  cb := cb.emitInst (I.sta_absY (SID_BASE + 1))   -- write OLD to freq_hi
  cb := cb.label "no_sky"

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

def emitNoteLoadPath (cb : CodeBuilder) (song : USFSong) : CodeBuilder :=
  -- === NOTE LOAD ===
  let cb := emitNL_Header cb
  let cb := emitNL_PtrCheck cb
  let cb := emitNL_ReadPitch cb
  let cb := emitNL_ReadDurInstPorta cb
  let cb := emitNL_PreAdvanceOps cb song
  let cb := emitNL_ExtractFlags cb
  let cb := emitNL_PreserveMask cb song
  let cb := emitNL_AdvancePtr cb
  let cb := emitNL_PostAdvanceOps cb song
  let cb := emitNL_DurField cb
  let cb := emitNL_UpdateVInst cb
  let cb := emitNL_ResetAndSidoff cb
  let cb := emitNL_TieCheck cb
  let cb := emitNL_FreqWrite cb
  let cb := emitNL_PortaInit cb
  let cb := emitNL_RestoreXY cb
  let cb := emitNL_SavePitchFhi cb
  let cb := emitNL_TieSkipLabel cb
  let cb := emitNL_CtrlWrite cb
  let cb := emitNL_PWADSRWrite cb
  -- v_pwperiod init is OFF in note-load. Why: py65 trace
  -- (/tmp/trace_pwperiod.py) showed that with the init wired, the
  -- second note-load (at frame 65 in Confuzion's V3 first-pattern
  -- sequence) re-writes \$1F into v_pwperiod[V3], wiping the
  -- 32-frame countdown midway through. Hubbard's actual player
  -- doesn't reset pw_period on note-load — the counter runs
  -- continuously across notes, only reloaded by its own logic when
  -- the period expires.
  -- The right fix is to init pw_period ONCE per song-init (PSID init
  -- entry), not per note. Approximate Hubbard init value unknown
  -- (must disassemble Confuzion's player to find what gets written to
  -- pw_period during init). Without the init, V3's PWM cadence is
  -- correct (~35 frames between steps) but phase-shifted by 32
  -- frames vs the original — first step at frame 2 instead of 34.
  let cb := emitNL_SaveCtrlAndReturn cb
  -- === ADVANCE ORDERLIST ===
  let cb := emitNL_AdvanceOrderHeader cb song
  let cb := emitNL_LookupOL cb
  let cb := emitNL_ReadAndDispatch cb
  let cb := emitNL_OLEndOrLoop cb
  let cb := emitNL_SongEnd cb
  cb

end  -- mutual

-- ==========================================================================
-- Top-level SID generation
-- ==========================================================================

def generateSID (song : USFSong) (debug : Bool := false) : Bytes := Id.run do
  -- Byte-perfect rebuild of Rob Hubbard's Confuzion (1985 Incentive).
  --
  -- Step 1: full binary verbatim.
  -- Step 2: $1146-$11A5 instrument table from song.instruments.
  -- Step 3 (this version): $0AFD-$0BBC freq table (192 bytes = 96 × 2)
  --   from song.freqTable. Only the first 96 entries are emitted —
  --   the USF table holds 128 (extended for other Hubbard engines),
  --   but Confuzion's pitch range is 0-95 and the in-engine table
  --   physically ends at $0BBC where voice SID-base offsets begin.
  -- Engine ($0858-$0AFC, 677 bytes), voice-state seed and song-data
  -- region ($0BBD-$1145, 1417 bytes) remain verbatim — to be replaced
  -- in subsequent steps.
  let _ := debug
  -- Engine code: $0858-$0AFC (play, init, sub_08A3, L_08B9, sub_08CB).
  let engineCode : List UInt8 := [
    0xA5, 0xA2, 0x48, 0xA9, 0x00, 0x85, 0xA2, 0x20, 0xCB, 0x08, 0xEE, 0x5C, 0x08, 0x68, 0x85, 0xA2,
    0x60, 0x8E, 0x9C, 0x08, 0x8E, 0xFA, 0x0A, 0xA9, 0xEA, 0x8D, 0xB9, 0x08, 0x8E, 0xC2, 0x08, 0xA2,
    0x02, 0xA9, 0x00, 0x8D, 0x5C, 0x08, 0xF0, 0x07, 0x78, 0xA2, 0x02, 0xA9, 0x00, 0x85, 0xA2, 0x9D,
    0xC1, 0x0B, 0x9D, 0xC4, 0x0B, 0x9D, 0xC7, 0x0B, 0x9D, 0xD0, 0x0B, 0xCA, 0x10, 0xF1, 0x8E, 0xEB,
    0x0B, 0x20, 0xA3, 0x08, 0x58, 0x60, 0xA9, 0x00, 0x8D, 0xEB, 0x0B, 0xA2, 0x17, 0x9D, 0x00, 0xD4,
    0xCA, 0x10, 0xFA, 0x60, 0x78, 0xA9, 0xCB, 0x8D, 0x14, 0x03, 0xA9, 0x08, 0x8D, 0x15, 0x03, 0x58,
    0x60, 0x78, 0xA9, 0x00, 0x8D, 0xEB, 0x0B, 0x8D, 0x18, 0xD4, 0x58, 0x4C, 0xFA, 0x0A, 0x8D, 0x18,
    0xD4, 0x58, 0x60, 0xAD, 0xEB, 0x0B, 0xD0, 0x03, 0x4C, 0xFA, 0x0A, 0xA2, 0x02, 0xCE, 0xE8, 0x0B,
    0x10, 0x06, 0xAD, 0xE9, 0x0B, 0x8D, 0xE8, 0x0B, 0xBD, 0xBD, 0x0B, 0x8D, 0xC0, 0x0B, 0xA8, 0xAD,
    0xE8, 0x0B, 0xCD, 0xE9, 0x0B, 0xD0, 0x15, 0xBD, 0xF1, 0x0B, 0x85, 0xFB, 0xBD, 0xF4, 0x0B, 0x85,
    0xFC, 0xDE, 0xC7, 0x0B, 0x30, 0x09, 0x4C, 0xE2, 0x09, 0x4C, 0xF4, 0x0A, 0x4C, 0x01, 0x0A, 0xBC,
    0xC1, 0x0B, 0xB1, 0xFB, 0xC9, 0xFF, 0xD0, 0x11, 0xA9, 0x00, 0x9D, 0xC7, 0x0B, 0x9D, 0xC1, 0x0B,
    0x9D, 0xC4, 0x0B, 0x4C, 0xB9, 0x08, 0x4C, 0xF4, 0x0A, 0xA8, 0xB9, 0xF7, 0x0B, 0x85, 0xFD, 0xB9,
    0x15, 0x0C, 0x85, 0xFE, 0xBC, 0xC4, 0x0B, 0xA9, 0xFF, 0x8D, 0xD6, 0x0B, 0xB1, 0xFD, 0x9D, 0xCA,
    0x0B, 0x8D, 0xD7, 0x0B, 0x29, 0x1F, 0x9D, 0xC7, 0x0B, 0x2C, 0xD7, 0x0B, 0x70, 0x45, 0xFE, 0xC4,
    0x0B, 0xAD, 0xD7, 0x0B, 0x10, 0x1A, 0xC8, 0xB1, 0xFD, 0x29, 0x1F, 0x9D, 0xD3, 0x0B, 0xA9, 0xA0,
    0x38, 0xED, 0xC2, 0x0B, 0xC9, 0x0F, 0x90, 0x02, 0xA9, 0x0F, 0x8D, 0x18, 0xD4, 0xFE, 0xC4, 0x0B,
    0xC8, 0xB1, 0xFD, 0x9D, 0xD0, 0x0B, 0x0A, 0xA8, 0xB9, 0xFD, 0x0A, 0x8D, 0xD8, 0x0B, 0xB9, 0xFE,
    0x0A, 0xAC, 0xC0, 0x0B, 0x99, 0x01, 0xD4, 0x9D, 0xEC, 0x0B, 0xAD, 0xD8, 0x0B, 0x99, 0x00, 0xD4,
    0x4C, 0x8E, 0x09, 0xCE, 0xD6, 0x0B, 0xAC, 0xC0, 0x0B, 0xBD, 0xD3, 0x0B, 0x8E, 0xD9, 0x0B, 0x0A,
    0x0A, 0x0A, 0xAA, 0xBD, 0x48, 0x11, 0x8D, 0xDA, 0x0B, 0xBD, 0x48, 0x11, 0x2D, 0xD6, 0x0B, 0x99,
    0x04, 0xD4, 0xBD, 0x46, 0x11, 0x99, 0x02, 0xD4, 0xBD, 0x47, 0x11, 0x99, 0x03, 0xD4, 0xBD, 0x49,
    0x11, 0x99, 0x05, 0xD4, 0xBD, 0x4A, 0x11, 0x99, 0x06, 0xD4, 0xAE, 0xD9, 0x0B, 0xAD, 0xDA, 0x0B,
    0x9D, 0xCD, 0x0B, 0xFE, 0xC4, 0x0B, 0xBC, 0xC4, 0x0B, 0xB1, 0xFD, 0xC9, 0xFF, 0xD0, 0x08, 0xA9,
    0x00, 0x9D, 0xC4, 0x0B, 0xFE, 0xC1, 0x0B, 0x4C, 0xF4, 0x0A, 0xAC, 0xC0, 0x0B, 0xBD, 0xCA, 0x0B,
    0x29, 0x20, 0xD0, 0x15, 0xBD, 0xC7, 0x0B, 0xD0, 0x10, 0xBD, 0xCD, 0x0B, 0x29, 0xFE, 0x99, 0x04,
    0xD4, 0xA9, 0x00, 0x99, 0x05, 0xD4, 0x99, 0x06, 0xD4, 0xBD, 0xD3, 0x0B, 0x0A, 0x0A, 0x0A, 0xA8,
    0x8C, 0xEA, 0x0B, 0xB9, 0x4D, 0x11, 0x8D, 0xEF, 0x0B, 0xB9, 0x4C, 0x11, 0x8D, 0xDC, 0x0B, 0xB9,
    0x4B, 0x11, 0x8D, 0xDB, 0x0B, 0xF0, 0x6E, 0xA5, 0xA2, 0x29, 0x07, 0xC9, 0x04, 0x90, 0x02, 0x49,
    0x07, 0x8D, 0xE1, 0x0B, 0xBD, 0xD0, 0x0B, 0x0A, 0xA8, 0x38, 0xB9, 0xFF, 0x0A, 0xF9, 0xFD, 0x0A,
    0x8D, 0xDD, 0x0B, 0xB9, 0x00, 0x0B, 0xF9, 0xFE, 0x0A, 0x4A, 0x6E, 0xDD, 0x0B, 0xCE, 0xDB, 0x0B,
    0x10, 0xF7, 0x8D, 0xDE, 0x0B, 0xB9, 0xFD, 0x0A, 0x8D, 0xDF, 0x0B, 0xB9, 0xFE, 0x0A, 0x8D, 0xE0,
    0x0B, 0xBD, 0xCA, 0x0B, 0x29, 0x1F, 0xC9, 0x08, 0x90, 0x1C, 0xAC, 0xE1, 0x0B, 0x88, 0x30, 0x16,
    0x18, 0xAD, 0xDF, 0x0B, 0x6D, 0xDD, 0x0B, 0x8D, 0xDF, 0x0B, 0xAD, 0xE0, 0x0B, 0x6D, 0xDE, 0x0B,
    0x8D, 0xE0, 0x0B, 0x4C, 0x65, 0x0A, 0xAC, 0xC0, 0x0B, 0xAD, 0xDF, 0x0B, 0x99, 0x00, 0xD4, 0xAD,
    0xE0, 0x0B, 0x99, 0x01, 0xD4, 0xAD, 0xDC, 0x0B, 0xF0, 0x62, 0xAC, 0xEA, 0x0B, 0x29, 0x1F, 0xDE,
    0xE2, 0x0B, 0x10, 0x58, 0x9D, 0xE2, 0x0B, 0xAD, 0xDC, 0x0B, 0x29, 0xE0, 0x8D, 0xF0, 0x0B, 0xBD,
    0xE5, 0x0B, 0xD0, 0x1A, 0xAD, 0xF0, 0x0B, 0x18, 0x79, 0x46, 0x11, 0x48, 0xB9, 0x47, 0x11, 0x69,
    0x00, 0x29, 0x0F, 0x48, 0xC9, 0x0E, 0xD0, 0x1D, 0xFE, 0xE5, 0x0B, 0x4C, 0xDD, 0x0A, 0x38, 0xB9,
    0x46, 0x11, 0xED, 0xF0, 0x0B, 0x48, 0xB9, 0x47, 0x11, 0xE9, 0x00, 0x29, 0x0F, 0x48, 0xC9, 0x08,
    0xD0, 0x03, 0xDE, 0xE5, 0x0B, 0x8E, 0xD9, 0x0B, 0xAE, 0xC0, 0x0B, 0x68, 0x99, 0x47, 0x11, 0x9D,
    0x03, 0xD4, 0x68, 0x99, 0x46, 0x11, 0x9D, 0x02, 0xD4, 0xAE, 0xD9, 0x0B, 0xCA, 0x30, 0x03, 0x4C,
    0xE0, 0x08, 0x4C, 0x81, 0xEA
  ]

  -- Frequency table from song.freqTable, first 96 entries × (lo, hi).
  let mut freqTable : Bytes := #[]
  for _h : i in [:96] do
    match song.freqTable.entries[i]? with
    | some (lo, hi) => freqTable := freqTable ++ #[lo.val.toUInt8, hi.val.toUInt8]
    | none          => freqTable := freqTable ++ #[0, 0]

  -- Voice SID-base offsets, voice-state scratch, orderlist pointers,
  -- pattern tables, and orderlists+patterns ($0BBD-$1145, 1417 bytes).
  let restOfPrefix : List UInt8 := [
    0x00, 0x07, 0x0E, 0x00, 0x04, 0x1B, 0x05, 0x2B, 0x00, 0x00, 0x02, 0x06, 0x06, 0x03, 0x87, 0x0F,
    0x41, 0x81, 0x41, 0x2A, 0x35, 0x1F, 0x00, 0x03, 0x02, 0xFF, 0x03, 0x4E, 0x00, 0x41, 0xFF, 0x00,
    0x05, 0x00, 0x4E, 0x0C, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x02, 0x00, 0xFF, 0x0C,
    0x17, 0x06, 0x00, 0x00, 0x33, 0x58, 0xFC, 0x0C, 0x0C, 0x0C, 0x24, 0x1A, 0xC5, 0xFB, 0xAC, 0x38,
    0xD0, 0x31, 0x67, 0xB5, 0x88, 0xCC, 0x00, 0x1B, 0xD5, 0x59, 0xE7, 0xE8, 0xE9, 0xEA, 0xEB, 0x9C,
    0x79, 0xD6, 0x02, 0x63, 0x64, 0xED, 0xFC, 0x0B, 0x0D, 0x10, 0x0F, 0x0D, 0x0D, 0x10, 0x0F, 0x0E,
    0x0E, 0x0E, 0x10, 0x10, 0x11, 0x11, 0x0D, 0x10, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0D, 0x0D, 0x0E,
    0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x10, 0x00, 0x15, 0x03, 0x07, 0x08, 0x09, 0x04, 0x04, 0x0E, 0x00,
    0x15, 0x03, 0x07, 0x08, 0x09, 0x04, 0x04, 0x0E, 0x00, 0x15, 0x04, 0x04, 0x0E, 0x00, 0x15, 0x00,
    0x16, 0x17, 0x18, 0x18, 0x18, 0x18, 0x14, 0x14, 0x14, 0x14, 0xFF, 0x02, 0x02, 0x02, 0x02, 0x02,
    0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
    0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x06, 0x06, 0x06, 0x06,
    0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x02, 0x02, 0x02, 0x02,
    0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
    0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x06, 0x06, 0x06,
    0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x02, 0x02, 0x02,
    0x02, 0x02, 0x02, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
    0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
    0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x1B, 0x1C, 0x1D, 0x1D, 0x1B, 0x1C,
    0x1D, 0x1D, 0x1B, 0x1C, 0x1D, 0x1D, 0x1B, 0x1C, 0x1D, 0x1D, 0x14, 0x14, 0x14, 0x14, 0xFF, 0x01,
    0x01, 0x0A, 0x0B, 0x0C, 0x0C, 0x0D, 0x05, 0x05, 0x0F, 0x01, 0x01, 0x0A, 0x0B, 0x0C, 0x0C, 0x0D,
    0x05, 0x05, 0x0F, 0x01, 0x01, 0x05, 0x05, 0x0F, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x1A, 0x1A,
    0x1A, 0x1A, 0x14, 0x14, 0x14, 0x14, 0xFF, 0x4B, 0xA3, 0x00, 0x37, 0x23, 0x39, 0x23, 0x3C, 0x23,
    0x3E, 0x2B, 0x40, 0x07, 0x3E, 0x23, 0x3C, 0x07, 0x3E, 0x21, 0x3C, 0x21, 0x3E, 0x0B, 0x3C, 0x23,
    0x39, 0x00, 0x39, 0x00, 0x38, 0x00, 0x37, 0x00, 0x36, 0x00, 0x35, 0x00, 0x34, 0x00, 0x33, 0x00,
    0x32, 0x00, 0x31, 0x00, 0x30, 0x00, 0x2F, 0x00, 0x2E, 0x43, 0x03, 0x3C, 0x07, 0x3C, 0x07, 0x3C,
    0x07, 0x39, 0x23, 0x37, 0x23, 0x39, 0x00, 0x38, 0x00, 0x37, 0x00, 0x36, 0x00, 0x35, 0x00, 0x34,
    0x00, 0x33, 0x41, 0x23, 0x32, 0x23, 0x34, 0x23, 0x37, 0x07, 0x39, 0xFF, 0x23, 0x39, 0x07, 0x3B,
    0x07, 0x37, 0x03, 0x32, 0x03, 0x32, 0x03, 0x32, 0x23, 0x32, 0x03, 0x2D, 0x07, 0x2D, 0x23, 0x2D,
    0x03, 0x28, 0x07, 0x28, 0x23, 0x28, 0x23, 0x26, 0x23, 0x28, 0x23, 0x26, 0x0F, 0x26, 0xFF, 0x23,
    0x39, 0x07, 0x3B, 0x0F, 0x37, 0x43, 0x23, 0x34, 0x07, 0x32, 0x0F, 0x32, 0x43, 0x5F, 0xFF, 0xA3,
    0x04, 0x34, 0x23, 0x30, 0x03, 0x2D, 0x27, 0x34, 0x23, 0x30, 0x23, 0x2D, 0x07, 0x32, 0x27, 0x2F,
    0x23, 0x2D, 0x0F, 0x2B, 0x23, 0x36, 0x23, 0x32, 0x03, 0x2F, 0x27, 0x36, 0x07, 0x32, 0x0B, 0x34,
    0x87, 0x05, 0x44, 0x07, 0x45, 0x07, 0x47, 0xFF, 0x87, 0x04, 0x3C, 0x07, 0x3C, 0x0B, 0x3C, 0x07,
    0x3C, 0x17, 0x3B, 0x43, 0x07, 0x3C, 0x07, 0x3C, 0x0B, 0x3C, 0x2B, 0x3E, 0x23, 0x40, 0x23, 0x3E,
    0x17, 0x3E, 0x43, 0x03, 0x3E, 0x23, 0x3E, 0x23, 0x3C, 0x23, 0x3B, 0x03, 0x39, 0xFF, 0x8B, 0x08,
    0x34, 0x23, 0x39, 0x2F, 0x39, 0x0F, 0x39, 0x47, 0x07, 0x39, 0x23, 0x39, 0x07, 0x37, 0x23, 0x32,
    0x2F, 0x32, 0x0F, 0x32, 0x47, 0x03, 0x34, 0x03, 0x34, 0x23, 0x35, 0x23, 0x32, 0x23, 0x2D, 0x23,
    0x32, 0x0F, 0x32, 0x47, 0x03, 0x2F, 0x07, 0x2F, 0x03, 0x30, 0x07, 0x30, 0x2B, 0x34, 0x03, 0x32,
    0x2F, 0x32, 0x5F, 0xFF, 0x47, 0x03, 0x3B, 0x0B, 0x3B, 0x07, 0x3B, 0x27, 0x3B, 0x23, 0x3C, 0x23,
    0x39, 0x0F, 0x39, 0x47, 0x03, 0x39, 0x0B, 0x39, 0x07, 0x39, 0x23, 0x39, 0x23, 0x3B, 0x23, 0x39,
    0x23, 0x37, 0x0F, 0x37, 0x4B, 0x03, 0x37, 0x03, 0x37, 0x07, 0x36, 0x03, 0x34, 0x0F, 0x36, 0x0F,
    0x34, 0x03, 0x33, 0x07, 0x34, 0x23, 0x36, 0x2F, 0x36, 0xFF, 0x07, 0x37, 0x43, 0xA3, 0x00, 0x32,
    0x23, 0x34, 0x23, 0x37, 0x23, 0x39, 0x2B, 0x3B, 0x07, 0x39, 0x23, 0x37, 0x07, 0x39, 0x21, 0x37,
    0x21, 0x39, 0x2B, 0x37, 0x03, 0x34, 0xA7, 0x05, 0x40, 0x27, 0x48, 0x07, 0x47, 0x43, 0x87, 0x00,
    0x2B, 0x03, 0x2B, 0x03, 0x2A, 0x03, 0x2A, 0x0F, 0x28, 0x23, 0x40, 0x23, 0x3E, 0x23, 0x3B, 0x23,
    0x39, 0x0F, 0x3B, 0x43, 0x03, 0x39, 0x03, 0x3B, 0x03, 0x39, 0x23, 0x39, 0x07, 0x37, 0x03, 0x37,
    0xA7, 0x05, 0x40, 0x27, 0x48, 0x1F, 0x47, 0xFF, 0x4B, 0x83, 0x07, 0x3C, 0x03, 0x3C, 0x07, 0x3C,
    0x43, 0x23, 0x3C, 0x07, 0x3E, 0x2F, 0x3B, 0x43, 0x4B, 0x03, 0x3B, 0x07, 0x3B, 0x07, 0x37, 0x0B,
    0x3B, 0x23, 0x39, 0x2F, 0x39, 0x0F, 0x39, 0x4F, 0xFF, 0x4F, 0x03, 0x3C, 0x07, 0x3C, 0x0B, 0x3C,
    0x07, 0x3E, 0x4F, 0x07, 0x45, 0x43, 0x0B, 0x42, 0x47, 0x07, 0x40, 0x43, 0x0B, 0x42, 0x47, 0x23,
    0x3E, 0x07, 0x3C, 0x0F, 0x39, 0x43, 0x23, 0x37, 0x07, 0x39, 0x0F, 0x37, 0x43, 0x0B, 0x34, 0x23,
    0x32, 0x1F, 0x32, 0x4F, 0xFF, 0x83, 0x0A, 0x4A, 0x83, 0x0B, 0x4A, 0x83, 0x0A, 0x4A, 0x83, 0x0B,
    0x4A, 0x83, 0x0B, 0x4A, 0x83, 0x0A, 0x4A, 0x83, 0x0B, 0x4A, 0x83, 0x0A, 0x4A, 0x83, 0x0A, 0x4C,
    0x83, 0x0B, 0x4C, 0x83, 0x0A, 0x4C, 0x83, 0x0B, 0x4C, 0x83, 0x0B, 0x4C, 0x83, 0x0A, 0x4C, 0x83,
    0x0B, 0x4C, 0x83, 0x0A, 0x4C, 0x83, 0x0A, 0x4A, 0x83, 0x0B, 0x4A, 0x83, 0x0A, 0x4A, 0x83, 0x0B,
    0x4A, 0x83, 0x0B, 0x4A, 0x83, 0x0A, 0x4A, 0x83, 0x0A, 0x4A, 0x83, 0x0A, 0x4A, 0x83, 0x0A, 0x4C,
    0x83, 0x0A, 0x4C, 0x83, 0x0A, 0x4C, 0x83, 0x0A, 0x4A, 0x83, 0x0B, 0x4A, 0x83, 0x0A, 0x4A, 0x83,
    0x0B, 0x4A, 0x83, 0x0A, 0x4A, 0xFF, 0x00, 0x83, 0x0A, 0x47, 0x83, 0x0B, 0x47, 0x83, 0x0A, 0x47,
    0x83, 0x0B, 0x47, 0x83, 0x0B, 0x47, 0x83, 0x0A, 0x47, 0x83, 0x0B, 0x47, 0x83, 0x0A, 0x47, 0x83,
    0x0A, 0x45, 0x83, 0x0B, 0x45, 0x83, 0x0A, 0x45, 0x83, 0x0B, 0x45, 0x83, 0x0B, 0x45, 0x83, 0x0A,
    0x45, 0x83, 0x0B, 0x45, 0x83, 0x0A, 0x45, 0x83, 0x0A, 0x45, 0x83, 0x0B, 0x45, 0x83, 0x0A, 0x45,
    0x83, 0x0B, 0x45, 0x83, 0x0B, 0x45, 0x83, 0x0A, 0x45, 0x83, 0x0A, 0x45, 0x83, 0x0A, 0x45, 0x83,
    0x0A, 0x45, 0x83, 0x0A, 0x45, 0x83, 0x0A, 0x45, 0x83, 0x0A, 0x45, 0x83, 0x0B, 0x45, 0x83, 0x0A,
    0x45, 0x83, 0x0B, 0x45, 0x83, 0x0A, 0x45, 0xFF, 0x87, 0x01, 0x5A, 0x07, 0x5A, 0x07, 0x5A, 0x87,
    0x03, 0x35, 0xFF, 0x83, 0x01, 0x5A, 0x03, 0x5A, 0x83, 0x03, 0x35, 0x83, 0x01, 0x5A, 0x83, 0x01,
    0x5A, 0x03, 0x5A, 0x83, 0x03, 0x35, 0x83, 0x01, 0x5A, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x5F, 0xFF,
    0x87, 0x02, 0x21, 0x83, 0x03, 0x35, 0x83, 0x02, 0x21, 0x07, 0x21, 0x87, 0x03, 0x35, 0xFF, 0x87,
    0x02, 0x1F, 0x83, 0x03, 0x35, 0x83, 0x02, 0x1F, 0x07, 0x1F, 0x87, 0x03, 0x35, 0xFF, 0x87, 0x02,
    0x1A, 0x83, 0x03, 0x35, 0x83, 0x02, 0x1A, 0x07, 0x1A, 0x87, 0x03, 0x35, 0xFF, 0x8B, 0x02, 0x21,
    0x03, 0x21, 0x07, 0x21, 0x03, 0x23, 0x03, 0x1F, 0x0B, 0x1F, 0x03, 0x1F, 0x0F, 0x1F, 0x0B, 0x1A,
    0x03, 0x1A, 0x0F, 0x1A, 0x0B, 0x1A, 0x03, 0x1A, 0x0F, 0x1A, 0xFF, 0x0B, 0x21, 0x03, 0x1C, 0x03,
    0x21, 0x07, 0x1C, 0x03, 0x1C, 0x0B, 0x1F, 0x03, 0x1F, 0x0F, 0x1F, 0x0B, 0x1E, 0x03, 0x1A, 0x03,
    0x1E, 0x07, 0x1A, 0x03, 0x1A, 0x0B, 0x1C, 0x03, 0x1C, 0x0F, 0x1C, 0xFF, 0x07, 0x1D, 0x03, 0x18,
    0x03, 0x1A, 0x03, 0x1D, 0x03, 0x18, 0x03, 0x1D, 0x03, 0x1D, 0x0B, 0x1C, 0x03, 0x1C, 0x0F, 0x1C,
    0x07, 0x1D, 0x03, 0x18, 0x03, 0x1A, 0x03, 0x1D, 0x03, 0x18, 0x03, 0x1D, 0x03, 0x1C, 0x0B, 0x1A,
    0x03, 0x1A, 0x0F, 0x1A, 0x0B, 0x1A, 0x03, 0x1A, 0x0F, 0x1A, 0xFF, 0x0B, 0x21, 0x03, 0x1C, 0x03,
    0x1A, 0x07, 0x18, 0x0B, 0x15, 0x43, 0x03, 0x1C, 0x07, 0x1A, 0x07, 0x18, 0x0B, 0x1F, 0x03, 0x1A,
    0x03, 0x18, 0x07, 0x17, 0x0B, 0x13, 0x43, 0x03, 0x1A, 0x07, 0x18, 0x07, 0x17, 0x0B, 0x1A, 0x07,
    0x1A, 0x03, 0x1A, 0x03, 0x1C, 0x07, 0x1D, 0x03, 0x1C, 0x03, 0x1A, 0x07, 0x1A, 0x03, 0x1C, 0x07,
    0x1D, 0x0B, 0x1F, 0x03, 0x1F, 0x0F, 0x1F, 0x47, 0x03, 0x1A, 0x0B, 0x1F, 0x07, 0x1A, 0xFF, 0x0B,
    0x1C, 0x03, 0x1C, 0x07, 0x1C, 0x07, 0x1F, 0x0B, 0x1A, 0x03, 0x1A, 0x0F, 0x1A, 0x0B, 0x1A, 0x03,
    0x1A, 0x07, 0x1A, 0x07, 0x17, 0x0B, 0x18, 0x03, 0x18, 0x0F, 0x18, 0x0B, 0x18, 0x03, 0x18, 0x0F,
    0x18, 0x0B, 0x17, 0x03, 0x17, 0x0F, 0x17, 0x07, 0x17, 0x43, 0x07, 0x23, 0x03, 0x21, 0x03, 0x1F,
    0x03, 0x1E, 0xFF, 0x0B, 0x1C, 0x03, 0x1C, 0x0F, 0x1C, 0x0B, 0x1A, 0x03, 0x1A, 0x07, 0x1A, 0x07,
    0x17, 0x0B, 0x18, 0x03, 0x18, 0x0F, 0x18, 0x0B, 0x1F, 0x03, 0x1F, 0x0F, 0x1F, 0xFF, 0x0B, 0x1D,
    0x83, 0x07, 0x39, 0x03, 0x39, 0x07, 0x39, 0x43, 0x23, 0x39, 0x07, 0x3B, 0x0F, 0x37, 0x43, 0x8B,
    0x02, 0x1C, 0x83, 0x07, 0x37, 0x07, 0x37, 0x07, 0x34, 0x0B, 0x37, 0x23, 0x36, 0x2F, 0x36, 0x87,
    0x02, 0x1A, 0x07, 0x18, 0x07, 0x17, 0x07, 0x15, 0xFF
  ]

  -- Instrument table: 12 × 8-byte records from song.instruments.
  -- Hubbard layout: +0 pulse_lo  +1 pulse_hi  +2 ctrl  +3 AD  +4 SR
  --                 +5 vib_depth +6 PWM packed +7 fx_flags
  let mut instTable : Bytes := #[]
  for inst in song.instruments do
    let vibByte : UInt8 := match inst.vibrato with
      | some v => if v.semitoneShift = 0 then 0 else (v.semitoneShift - 1).toUInt8
      | none => 0
    let pwmByte : UInt8 := match inst.pwMod with
      | some pm => match pm.mode with
        | .linear s => s.val.toUInt8
        | .bidirectional s _ _ => s.val.toUInt8
        | .table _ => 0
      | none => 0
    let fxFlags : UInt8 :=
      (if inst.freqSlide.isSome then 1 else 0) +
      (if inst.skydive then 2 else 0) +
      (if inst.arpeggio.isSome then 4 else 0)
    instTable := instTable ++ #[
      inst.initPwLo.val.toUInt8,
      inst.initPwHi.val.toUInt8,
      inst.initCtrl.val.toUInt8,
      inst.ad.val.toUInt8,
      inst.sr.val.toUInt8,
      vibByte,
      pwmByte,
      fxFlags
    ]

  let payload : Bytes := engineCode.toArray ++ freqTable ++ restOfPrefix.toArray ++ instTable
  let header : PSIDHeader := {
    loadAddr := 0
    initAddr := 0x0867
    playAddr := 0x0858
    embeddedLoad := 0x0858
    songs := 1
    startSong := 1
    speed := 1
    flags := 0x0014
    title := "Confuzion"
    author := "Rob Hubbard"
    released := "1985 Incentive"
  }
  return buildSID header payload

def writeFile (path : String) (data : Bytes) : IO Unit := do
  let handle ← IO.FS.Handle.mk path .write
  handle.write ⟨data⟩

-- (Original `sidgenMainV3` referenced commandoV3 from CommandoV3.lean —
--  not applicable in the cloned Confuzion codegen. SidgenConfuzionMain.lean
--  provides its own main using `confuzionV3` from ConfuzionV3.lean.)

end ConfuzionNS
