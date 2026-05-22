/-
  Commando.Codegen — Player codegen for Rob Hubbard's Commando, consuming
  a `USFSong` and emitting a `ByteArray` PSID. Locked invariant: the
  resulting `commando.sid` has md5 `1964b77e8b542a5187fdd0a6db2d0186` and
  matches the original frame-for-frame in siddump's writelog.

  The player handles all USF v3 abstractions:
  - NoteKind (pitched / percussion / rest / tie)
  - Per-frame durations (no tick math)
  - Effect chain order from `instrument.effectOrder`
  - stepEvery counters per effect
  - startDelay timing per effect
  - Release spec (framesBeforeEnd / zeroAdsr / noRelease)

  Frame-accurate: cycle ordering within a frame is deterministic per
  effect, not configurable. Sufficient for all tracker music.

  ─── Table of contents ────────────────────────────────────────────────
  §1  CodeBuilder + assembly helpers     (CodeBuilder, emitInst*, labels)
  §2  USFNoteLoadOp emission             (engine-quirk DSL)
  §3  init — subtune dispatch, SID silence, voice-state init
  §4  play — frame counter + per-voice loop dispatch
  §5  note_load — emitNL_* sub-blocks (header, ptr check, read pitch,
                  read dur/inst/porta, advance ops, freq write, …)
  §6  sustain effects — vibrato, PW, freqSlide, arpeggio, gate check
  §7  Data tables                        (freq, instruments, patterns, voices)
  §8  generateSID                        (top-level orchestration + PSID wrap)
  ──────────────────────────────────────────────────────────────────────
-/

import Commando.SID
import Commando.Asm6502
import Commando.PSIDFile
import Commando.USF
import Commando.Constants

namespace V3

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
    for use by sustain-path effects. Voice index restored to X afterwards. -/
def emitNL_SavePitchFhi (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitInst (I.lda_zp 0xFE)
  let cb := cb.emitStaAbsX "v_pitch"
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

  -- 1. GATE-OFF CHECK (fire when v_dur == gateOffFrames, i.e., 3 frames before end)
  -- Only fires once per note (the exact moment v_dur crosses threshold)
  cb := cb.emitLdaAbsX "v_dur"
  cb := cb.emitInst (I.cmp_imm 2)                  -- empirically tuned (was 3 in original)
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
  -- (v_pwdir lives below in the v_* mutable storage block; per-VOICE,
  -- not per-instrument — Hubbard $5510,X.)
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
      -- 4th byte: portamento descriptor. 0 = none. Bits 1-6 = step size,
      -- bit 0 = direction (1 = down). Codegen reads at note-load and runs
      -- a per-frame freq slide while non-zero.
      cb := cb.emitByte note.porta.toUInt8
    cb := cb.emitByte 0x00

  cb := cb.label "patt_ptr_lo"
  cb := cb.emitData patPtrLo
  cb := cb.label "patt_ptr_hi"
  cb := cb.emitData patPtrHi

  -- Orderlist data per (subtune, voice) + build pointer tables.
  -- Layout for each orderlist: [entries..., $FF, loopPoint_or_FF].
  -- When advance_order reads $FF, it consults the next byte: if $FF, song
  -- ends; otherwise that byte is the new orderlist position (loop back).
  --
  -- For multi-subtune support we emit a subtune-major flat table:
  -- ol_subtune_lo/hi has len(subtunes)*3 bytes (3 voice ptrs per subtune).
  -- Init copies the requested subtune's 3 bytes into the runtime ol_lo/hi
  -- (which retains the per-voice 3-byte layout the rest of the codegen
  -- uses).
  let mut olSubtuneLo : List UInt8 := []
  let mut olSubtuneHi : List UInt8 := []
  for st in song.subtunes do
    for vi in [:3] do
      match st.voices[vi]? with
      | some voiceSpec =>
        let addr := cb.currentAddr
        olSubtuneLo := olSubtuneLo ++ [addr.toUInt8]
        olSubtuneHi := olSubtuneHi ++ [(addr >>> 8).toUInt8]
        cb := cb.emitData (voiceSpec.orderlist.map (·.toUInt8))
        cb := cb.emitByte 0xFF
        let loopByte : UInt8 := match voiceSpec.loopPoint with
          | some p => p.toUInt8
          | none   => 0xFF
        cb := cb.emitByte loopByte
      | none =>
        olSubtuneLo := olSubtuneLo ++ [0]
        olSubtuneHi := olSubtuneHi ++ [0]
  -- Active per-voice orderlist pointers (init copies one subtune's block here).
  let olLo : List UInt8 := [0, 0, 0]
  let olHi : List UInt8 := [0, 0, 0]

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
  -- Per-voice no_release flag: bit 5 of the raw inst byte at note-load.
  -- When set, the next HR check skips itself, leaving the gate on so the
  -- following note inherits it (Hubbard portamento/legato).
  cb := cb.label "v_no_release"
  cb := cb.emitData [(0 : UInt8), 0, 0]
  -- Per-voice "no instrument byte" flag (bit 7 of pattern inst byte).
  -- Set on note-load when the pattern note omits the instrument; v_inst
  -- update skips itself, so the previous instrument's tables continue to
  -- drive Ctrl/PW/ADSR.
  cb := cb.label "v_no_inst_byte"
  cb := cb.emitData [(0 : UInt8), 0, 0]
  -- Per-voice portamento state. v_porta = porta descriptor byte (Hubbard
  -- format: bits 1-6 = step size, bit 0 = direction). v_porta_lo/hi = the
  -- 16-bit current freq accumulator that the slide modifies each frame.
  -- All initialised to 0 (= no porta).
  cb := cb.label "v_porta"
  cb := cb.emitData [(0 : UInt8), 0, 0]
  cb := cb.label "v_porta_lo"
  cb := cb.emitData [(0 : UInt8), 0, 0]
  cb := cb.label "v_porta_hi"
  cb := cb.emitData [(0 : UInt8), 0, 0]
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
  -- Subtune-major orderlist pointer tables. Each subtune contributes 3
  -- bytes (voice 0/1/2 orderlist start). Init reads the requested subtune
  -- index from A, computes the byte offset (= subtune * 3), and copies
  -- 3 bytes from each into ol_lo/ol_hi.
  cb := cb.label "ol_subtune_lo"
  cb := cb.emitData olSubtuneLo
  cb := cb.label "ol_subtune_hi"
  cb := cb.emitData olSubtuneHi
  -- Per-subtune tempo (frames per tick). Currently unused at runtime
  -- because pattern durations are pre-multiplied; included for future
  -- tick-based support and so the data is preserved through the pipeline.
  cb := cb.label "tempo_subtune"
  cb := cb.emitData (song.subtunes.map (·.tempo.toUInt8))

  -- Resolve all forward references
  cb := cb.resolve

  let header : PSIDHeader := {
    initAddr := base
    playAddr := base + 3
    songs := song.subtunes.length.toUInt16
    startSong := 1
    title := "Commando"
    author := "Rob Hubbard"
    released := "1985 Elite"
  }
  return buildSID header cb.bytes

def writeFile (path : String) (data : Bytes) : IO Unit := do
  let handle ← IO.FS.Handle.mk path .write
  handle.write ⟨data⟩

end V3
