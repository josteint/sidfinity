/-
  MasterOfMagic.Codegen — Direct-emit 6502 player for Rob Hubbard's
  "The Master of Magic" (1985 MAD/Mastertronic).

  Implements the play-loop semantics documented in
  docs/hubbard_master_of_magic_disassembly.s exactly:

  - init: copy 6 orderlist-pointer bytes, set first-frame sentinel ($C41D=$40).
  - play: INC frame counter. BIT $C41D dispatch:
      bit 7 set → end-of-song silence path (sticky $80).
      bit 6 set → first-frame: zero v_olpos/patpos/dur/pitch, clear $C41D.
      both clear → normal per-voice loop.
  - Per-voice loop: X = 2 → 1 → 0 (V3 first).
    Global tick divider DEC / reload controls note-load gate.
    Note-load gate: fires only when $C41A == $C41B after DEC/reload.
    If gate fails → effects-only (vibrato + PWM + fx_flags effects).
    If gate passes → DEC v_dur; if expired → load next note from orderlist/pattern.
    Hard-restart: fires when v_dur == 0 and no_release flag clear.
  - Effects (in order):
      vibrato (triangle LFO, modulates freq),
      PWM (bit3=simple or standard bidirectional with $08/$0E bounds),
      skydive/drum (bit0: DEC freq_hi after midpoint, $80 ctrl at sweep end),
      slow-descent (bit1: DEC freq_hi every other frame on long notes in tail),
      table-arp (bit2: alternate pitch+12 when (frame&7)!=0).
  - End-of-song volume fade: VOL = clamp($75 - v_olpos[V3], 0, $0F) on each note-load.

  All data (freq table, instrument table, orderlists, patterns) is stored
  verbatim from the MoM binary via MoMSong fields. The codegen emits a
  PSID with the player code + data tables inlined.

  ─── Table of contents ─────────────────────────────────────────────────
  §1  CodeBuilder + assembly helpers (shared infra, same as Monty)
  §2  MoMSong data type
  §3  emitInit — init entry: copy orderlist ptrs, set sentinel
  §4  emitPlay — play entry: frame counter + BIT dispatch
  §5  emitFirstFrame — first-frame zeroing path
  §6  emitEndOfSong — silence + sticky-$80 path
  §7  emitPerVoiceLoop — per-voice dispatch (X=2,1,0)
  §8  emitEffectsOnly — effects-only path (vibrato+PWM+fx_flags)
  §9  emitNoteLoad — note-load path (orderlists + patterns)
  §10 emitSustainHR — sustain / hard-restart check
  §11 emitVibrato — triangle LFO frequency modulation
  §12 emitPWM — pulse-width modulation (simple + bidirectional)
  §13 emitSkydive — bit0 drum/skydive effect
  §14 emitSlowDescent — bit1 slow-descent effect
  §15 emitTableArp — bit2 table-arp at +12 semitones
  §16 generateSID — top-level: code + data tables + PSID header
  ──────────────────────────────────────────────────────────────────────
-/

import MasterOfMagic.SID
import MasterOfMagic.Asm6502
import MasterOfMagic.PSIDFile
import MasterOfMagic.Constants

namespace MasterOfMagicNS

-- ==========================================================================
-- §1  CodeBuilder + assembly helpers
-- ==========================================================================

structure Fixup where
  byteIdx    : Nat
  targetLabel : String
  isRelative : Bool
  instrAddr  : UInt16

structure AbsFixup where
  byteIdx    : Nat
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

def emitLdaAbsX (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xBD, 0, 0], absFixups := fixup :: cb.absFixups }

def emitLdaAbsY (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xB9, 0, 0], absFixups := fixup :: cb.absFixups }

def emitStaAbsX (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0x9D, 0, 0], absFixups := fixup :: cb.absFixups }

def emitStaAbsY (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0x99, 0, 0], absFixups := fixup :: cb.absFixups }

def emitDecAbsX (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xDE, 0, 0], absFixups := fixup :: cb.absFixups }

def emitIncAbsX (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xFE, 0, 0], absFixups := fixup :: cb.absFixups }

def emitLdaAbs (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xAD, 0, 0], absFixups := fixup :: cb.absFixups }

def emitStaAbs (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0x8D, 0, 0], absFixups := fixup :: cb.absFixups }

def emitCmpAbsX (cb : CodeBuilder) (target : String) : CodeBuilder :=
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := target }
  { cb with bytes := cb.bytes ++ #[0xDD, 0, 0], absFixups := fixup :: cb.absFixups }

def emitData (cb : CodeBuilder) (data : List UInt8) : CodeBuilder :=
  cb.emit data.toArray

def emitByte (cb : CodeBuilder) (v : UInt8) : CodeBuilder :=
  cb.emit #[v]

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

end CodeBuilder

-- ==========================================================================
-- §2  MoMSong data type
-- ==========================================================================

/-- Raw 8-byte Hubbard instrument record (direct from binary):
    +0 pw_lo  +1 pw_hi  +2 ctrl  +3 AD  +4 SR
    +5 vib_depth  +6 vib_period  +7 fx_flags
    fx_flags:  bit0=skydive, bit1=slow-descent, bit2=table-arp, bit3=simple-PWM -/
structure MoMInstrument where
  pwLo     : UInt8
  pwHi     : UInt8
  ctrl     : UInt8
  ad       : UInt8
  sr       : UInt8
  vibDepth : UInt8
  vibPeriod: UInt8
  fxFlags  : UInt8
  deriving Repr

/-- Complete MoM song data, extracted verbatim from the original binary. -/
structure MoMSong where
  -- Frequency table: 96 entries, (lo, hi) pairs.
  freqLo   : List UInt8
  freqHi   : List UInt8
  -- Instrument table (variable count).
  instruments : List MoMInstrument
  -- Orderlist bytes for V1/V2/V3. Each terminates with $FF (loop) or $FE (stop).
  olV1     : List UInt8
  olV2     : List UInt8
  olV3     : List UInt8
  -- Pattern pointer tables (parallel arrays of lo/hi).
  patPtrLo : List UInt8
  patPtrHi : List UInt8
  -- Pattern raw bytes (each terminates with $FF).
  patterns : List (List UInt8)
  -- Load-time binary state (not zeroed by init):
  initVInst  : UInt8 × UInt8 × UInt8   -- (V1, V2, V3) initial v_inst
  initVPitch : UInt8 × UInt8 × UInt8   -- initial v_pitch
  initVFhi   : UInt8 × UInt8 × UInt8   -- initial v_fhi (saved freq_hi for effects)
  initVPwmStep : UInt8 × UInt8 × UInt8 -- initial v_pwm_step counter
  initVPwmDir  : UInt8 × UInt8 × UInt8 -- initial v_pwm_dir (0=add, nonzero=sub)
  initVCtrl    : UInt8 × UInt8 × UInt8 -- initial v_ctrl (saved inst.ctrl)
  tickReload : UInt8  -- $C41B initial value (global tick reload)
  title    : String
  author   : String
  released : String
  deriving Repr

-- ==========================================================================
-- §3  emitInit
-- ==========================================================================

/-- Init: given subtune index in A (0-indexed), copy 6 bytes from the
    subtune orderlist-pointer table to the active pointers, then set the
    first-frame sentinel ($C41D = $40). This is the COMPLETE init — all
    voice-state zeroing is deferred to the first play frame. -/
def emitInit (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "init"
  -- Compute A*6: A*2 → stash, A*4 → +stash = A*6, TAX
  let cb := cb.emitInst (I.sta_zp 0xFB)      -- stash A (subtune index)
  let cb := cb.emitInst I.asl_a               -- A*2
  let cb := cb.emitInst (I.sta_zp 0xFC)       -- stash A*2
  let cb := cb.emitInst I.asl_a               -- A*4
  let cb := cb.emitInst I.clc
  let cb := cb.emitInst (I.adc_zp 0xFC)       -- A*4 + A*2 = A*6
  let cb := cb.emitInst I.tax                 -- X = subtune*6
  -- Copy 6 bytes from ol_subtune_table[X..X+5] to ol_v1_lo..ol_v3_hi
  -- Y counts 0..5
  let cb := cb.emitInst (I.ldy_imm 0)
  let cb := cb.label "init_copy"
  let cb := cb.emitLdaAbsX "ol_subtune_table" -- LDA ol_subtune_table,X
  let cb := cb.emitStaAbsY "ol_active_lo"     -- STA ol_active_lo,Y (Y=0..2: lo; Y=3..5: hi via same array)
  let cb := cb.emitInst I.inx
  let cb := cb.emitInst I.iny
  let cb := cb.emitInst (I.cpy_imm 6)
  let cb := cb.emitBranch .BNE "init_copy"
  -- Set first-frame sentinel
  let cb := cb.emitInst (I.lda_imm 0x40)
  let cb := cb.emitStaAbs "engine_state"
  let cb := cb.emitInst I.rts
  cb

-- ==========================================================================
-- §4  emitPlay
-- ==========================================================================

/-- Play: INC frame counter, dispatch on engine_state ($C41D).
    bit 7 (N) = end-of-song, bit 6 (V) = first-frame. -/
def emitPlay (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "play"
  let cb := cb.emitInst (I.inc_abs (SID_BASE + 0x26))  -- placeholder; will be "frame_ctr" via STA
  -- Actually emit INC frame_ctr via abs label
  -- Patch: replace the INC abs with the proper label version
  -- Use emitInst-style INC abs manually:
  let cb := { cb with bytes := cb.bytes.extract 0 (cb.bytes.size - 3) }  -- undo last emitInst
  -- Emit INC abs with forward ref
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "frame_ctr" }
  let cb := { cb with bytes := cb.bytes ++ #[0xEE, 0, 0],
                      absFixups := fixup :: cb.absFixups }
  -- BIT engine_state
  let fixup2 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "engine_state" }
  let cb := { cb with bytes := cb.bytes ++ #[0x2C, 0, 0],
                      absFixups := fixup2 :: cb.absFixups }
  -- BMI end_of_song (bit 7 set)
  let cb := cb.emitBranch .BMI "end_of_song"
  -- BVC per_voice_start (bit 6 clear = normal frame)
  let cb := cb.emitBranch .BVC "per_voice_start"
  -- Fall through: bit 6 set = first-frame path
  cb

-- ==========================================================================
-- §5  emitFirstFrame
-- ==========================================================================

/-- First-frame setup: zero v_olpos, v_patpos, v_dur, v_pitch for all 3 slots.
    Reset frame counter to 0. Clear engine_state. Then fall into per-voice loop.
    Does NOT zero v_inst, v_fhi, v_pwm_step, v_pwm_dir, v_ctrl — those
    keep their load-time binary values. -/
def emitFirstFrame (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.lda_imm 0)
  -- Reset frame counter to 0 (first-frame path does this)
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "frame_ctr" }
  let cb := { cb with bytes := cb.bytes ++ #[0x8D, 0, 0],
                      absFixups := fixup :: cb.absFixups }
  let cb := cb.emitInst (I.ldx_imm 2)
  let cb := cb.label "ff_loop"
  let cb := cb.emitStaAbsX "v_olpos"
  let cb := cb.emitStaAbsX "v_patpos"
  let cb := cb.emitStaAbsX "v_dur"
  let cb := cb.emitStaAbsX "v_pitch"
  let cb := cb.emitInst I.dex
  let cb := cb.emitBranch .BPL "ff_loop"
  -- Clear engine_state
  let fixup2 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "engine_state" }
  let cb := { cb with bytes := cb.bytes ++ #[0x8D, 0, 0],
                      absFixups := fixup2 :: cb.absFixups }
  -- JMP per_voice_start (cannot fall through — end-of-song code is next)
  let cb := cb.emitJmpLabel .JMP "per_voice_start"
  cb

-- ==========================================================================
-- §6  emitEndOfSong
-- ==========================================================================

/-- End-of-song path. First entry: $C41D = $C0 (both bits set).
    BVC tests bit 6:
    - bit 6 clear (sticky $80) → just RTS
    - bit 6 set → silence SID, set sticky $80, RTS
    Next frame: BMI takes us here, BVC clears → RTS. -/
def emitEndOfSong (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "end_of_song"
  -- BVC rts_now (if bit 6 clear = sticky end → just RTS)
  let cb := cb.emitBranch .BVC "rts_now"
  -- Silence all 3 voices
  let cb := cb.emitInst (I.lda_imm 0)
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 4))   -- V1_CTRL = 0
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 11))  -- V2_CTRL = 0
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 18))  -- V3_CTRL = 0
  let cb := cb.emitInst (I.lda_imm 0x0F)
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 0x18)) -- VOL = $0F
  -- Set sticky $80
  let cb := cb.emitInst (I.lda_imm 0x80)
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "engine_state" }
  let cb := { cb with bytes := cb.bytes ++ #[0x8D, 0, 0],
                      absFixups := fixup :: cb.absFixups }
  let cb := cb.label "rts_now"
  let cb := cb.emitInst I.rts
  cb

-- ==========================================================================
-- §7  emitPerVoiceLoop
-- ==========================================================================

/-- Per-voice loop entry. Processes X = 2, 1, 0 (V3, V2, V1).
    Global tick divider at v_tickdiv:
    - DEC v_tickdiv; if negative, reload from v_tickreload.
    Note-load gate: fires only when v_tickdiv == v_tickreload after DEC.
    If gate fails → effects-only path.
    If gate passes → DEC v_dur; if expired → note-load; else sustain/HR check. -/
def emitPerVoiceLoop (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "per_voice_start"
  let cb := cb.emitInst (I.ldx_imm 2)   -- start at slot 2 (= V3)
  -- DEC tick divider ONCE per frame (before the per-voice iterations).
  -- Subsequent voices loop back to "voice_top" which is AFTER the DEC.
  let fixup1 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "v_tickdiv" }
  let cb := { cb with bytes := cb.bytes ++ #[0xCE, 0, 0],
                      absFixups := fixup1 :: cb.absFixups }
  let cb := cb.emitBranch .BPL "tickdiv_ok"
  -- Reload: LDA v_tickreload, STA v_tickdiv
  let fixup2 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "v_tickreload" }
  let cb := { cb with bytes := cb.bytes ++ #[0xAD, 0, 0],
                      absFixups := fixup2 :: cb.absFixups }
  let fixup3 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "v_tickdiv" }
  let cb := { cb with bytes := cb.bytes ++ #[0x8D, 0, 0],
                      absFixups := fixup3 :: cb.absFixups }
  let cb := cb.label "tickdiv_ok"
  -- Per-voice entry point (V2 and V1 loop back here, past the DEC).
  let cb := cb.label "voice_top"
  -- Load current SID base offset for this voice slot into A and TAY.
  -- Y = SID base offset (0/7/14 for V1/V2/V3). Each effect path reloads
  -- Y from v_sidoff[X] before any SID write, so we don't need a saved copy.
  let cb := cb.emitLdaAbsX "v_sidoff"        -- A = sid_offset[X]
  let cb := cb.emitInst (I.sta_zp 0xF0)     -- ZP $F0 = SID base offset (for sustain/HR)
  let cb := cb.emitInst I.tay               -- Y = SID base offset
  -- Note-load gate check: LDA v_tickdiv, CMP v_tickreload; BNE effects_only
  let fixup5 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "v_tickdiv" }
  let cb := { cb with bytes := cb.bytes ++ #[0xAD, 0, 0],
                      absFixups := fixup5 :: cb.absFixups }
  let fixup6 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "v_tickreload" }
  let cb := { cb with bytes := cb.bytes ++ #[0xCD, 0, 0],
                      absFixups := fixup6 :: cb.absFixups }
  let cb := cb.emitBranch .BNE "effects_only_jmp"
  -- Note-load gate passed: DEC v_dur[X]. BPL → sustain. BMI → load new note.
  let cb := cb.emitDecAbsX "v_dur"
  let cb := cb.emitBranch .BPL "sustain_check"
  let cb := cb.emitJmpLabel .JMP "note_load"
  let cb := cb.label "effects_only_jmp"
  let cb := cb.emitJmpLabel .JMP "effects_only"
  -- sustain_check: gate-off (HR) check, then effects
  let cb := cb.label "sustain_check"
  cb

-- ==========================================================================
-- §8  emitEffectsOnly
-- ==========================================================================

/-- Effects-only entry: jumped to when tick gate fails.
    Runs vibrato → PWM → fx_flags effects in MoM order.
    On entry: X = voice slot (0/1/2), Y = SID base offset. -/
def emitEffectsOnly (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "effects_only"
  -- Save voice X (Y may get clobbered by effects)
  let cb := cb.emitInst (I.stx_zp 0xFA)
  cb

-- ==========================================================================
-- §10 emitSustainHR
-- ==========================================================================

/-- Sustain / Hard-restart check. Reached when DEC v_dur >= 0 (note still active).
    HR fires when v_dur == 0 AND v_flags has no_release clear. -/
def emitSustainHR (cb : CodeBuilder) : CodeBuilder :=
  -- Save voice index (Y may be clobbered)
  let cb := cb.emitInst (I.stx_zp 0xFA)
  -- Check no_release flag (bit 5 of v_flags)
  let cb := cb.emitLdaAbsX "v_flags"
  let cb := cb.emitInst (I.and_imm 0x20)
  let cb := cb.emitBranch .BNE "effects_only"   -- no_release set: skip HR
  -- Check v_dur == 0
  let cb := cb.emitLdaAbsX "v_dur"
  let cb := cb.emitBranch .BNE "effects_only"   -- not zero: skip HR
  -- HR: gate off + zero AD/SR
  let cb := cb.emitLdaAbsX "v_ctrl"
  let cb := cb.emitInst (I.and_imm 0xFE)        -- clear gate bit
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 4))
  let cb := cb.emitInst (I.lda_imm 0)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 5))  -- AD = 0
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 6))  -- SR = 0
  -- Fall through to effects_only
  cb

-- ==========================================================================
-- §11 emitVibrato
-- ==========================================================================

/-- Vibrato: triangle LFO modulates frequency.
    On entry: X = voice slot saved in $FA; Y = SID base offset.
    Reads v_inst[X] → inst table → vib_depth (byte+5).
    If vib_depth == 0: skip to no_vib, write base freq.
    If orig_dur < 4: skip vibrato sum (short note).
    LFO: (frame_ctr & 7) folded 0-3-3-0 triangle. -/
def emitVibrato (cb : CodeBuilder) : CodeBuilder :=
  -- Original: load inst*8 → Y, load fx_flags/vib_period/vib_depth.
  -- Our flat arrays are indexed by inst index (not inst*8).
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_inst"
  let cb := cb.emitInst I.tay              -- Y = inst index
  -- Load vib_depth; if 0 → BEQ skip to vib_done (no freq write for depth=0).
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_vib_depth" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup :: cb.absFixups }
  -- depth=0: skip to vib_done (no vibrato, no freq write). Use BNE+JMP trampoline.
  let cb := cb.emitBranch .BNE "vib_active"  -- depth≠0: do vibrato
  let cb := cb.emitJmpLabel .JMP "vib_done"  -- depth=0: skip to vib_done (no freq write)
  let cb := cb.label "vib_active"
  let cb := cb.emitInst (I.sta_zp 0xF7)   -- $F7 = vib_depth countdown
  -- Triangle LFO: frame_ctr & 7 → fold >=4 via EOR #7
  let fixup3 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "frame_ctr" }
  let cb := { cb with bytes := cb.bytes ++ #[0xAD, 0, 0],
                      absFixups := fixup3 :: cb.absFixups }
  let cb := cb.emitInst (I.and_imm 7)
  let cb := cb.emitInst (I.cmp_imm 4)
  let cb := cb.emitBranch .BCC "lfo_ok"
  let cb := cb.emitInst (I.eor_imm 7)
  let cb := cb.label "lfo_ok"
  let cb := cb.emitInst (I.sta_zp 0xF5)   -- $F5 = LFO triangle value (0-3)
  -- Load base freq for current pitch into $F8/$F9 (accumulators).
  -- Also compute delta = freq[pitch+1] - freq[pitch].
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_pitch"
  let cb := cb.emitInst I.tay              -- Y = pitch
  let fixup4 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "freq_lo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup4 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF8)   -- $F8 = base_flo accumulator
  let fixup5 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "freq_hi" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup5 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF9)   -- $F9 = base_fhi accumulator
  let cb := cb.emitInst I.iny              -- Y = pitch+1
  -- delta_lo = freq_lo[pitch+1] - freq_lo[pitch]
  let cb := cb.emitInst I.sec
  let fixup6 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "freq_lo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup6 :: cb.absFixups }
  let cb := cb.emitInst (I.sbc_zp 0xF8)
  let cb := cb.emitInst (I.sta_zp 0xF4)   -- delta_lo
  -- delta_hi = freq_hi[pitch+1] - freq_hi[pitch] (with borrow)
  let fixup7 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "freq_hi" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup7 :: cb.absFixups }
  let cb := cb.emitInst (I.sbc_zp 0xF9)   -- A = delta_hi (with borrow from delta_lo SBC)
  -- Right-shift delta by vib_depth bits (loop)
  let cb := cb.label "vib_shift"
  let cb := cb.emitInst ⟨.LSR, .acc⟩      -- LSR A (delta_hi)
  let cb := cb.emitInst ⟨.ROR, .zp 0xF4⟩ -- ROR delta_lo
  let cb := cb.emitInst (I.dec_zp 0xF7)   -- dec countdown
  let cb := cb.emitBranch .BNE "vib_shift"
  let cb := cb.emitInst (I.sta_zp 0xF3)   -- $F3 = shifted delta_hi
  -- Skip vibrato accumulation on very short notes (orig dur < 4)
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_flags"
  let cb := cb.emitInst (I.and_imm 0x1F)  -- orig duration bits
  let cb := cb.emitInst (I.cmp_imm 4)
  let cb := cb.emitBranch .BCC "vib_write_freq"  -- dur < 4: write base freq as-is
  -- Accumulate delta × LFO steps into $F8/$F9
  let cb := cb.emitInst (I.ldy_zp 0xF5)   -- Y = LFO triangle value
  let cb := cb.label "vib_add"
  let cb := cb.emitInst I.dey
  let cb := cb.emitBranch .BMI "vib_write_freq"  -- Y went negative: done accumulating
  let cb := cb.emitInst I.clc
  let cb := cb.emitInst (I.lda_zp 0xF8)
  let cb := cb.emitInst (I.adc_zp 0xF4)   -- flo += delta_lo
  let cb := cb.emitInst (I.sta_zp 0xF8)
  let cb := cb.emitInst (I.lda_zp 0xF9)
  let cb := cb.emitInst (I.adc_zp 0xF3)   -- fhi += delta_hi + carry
  let cb := cb.emitInst (I.sta_zp 0xF9)
  let cb := cb.emitJmpLabel .JMP "vib_add"
  -- Write $F8/$F9 (modulated or base) to SID freq registers
  let cb := cb.label "vib_write_freq"
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let cb := cb.emitInst (I.lda_zp 0xF8)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 0))  -- freq_lo to SID
  let cb := cb.emitInst (I.lda_zp 0xF9)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 1))  -- freq_hi to SID
  -- Fall through to vib_done (= start of PWM block)
  let cb := cb.label "vib_done"
  let cb := cb.emitInst (I.ldx_zp 0xFA)   -- restore X = voice slot
  cb

-- ==========================================================================
-- §12 emitPWM
-- ==========================================================================

/-- PWM block. Two modes selected by fx_flags bit 3:
    bit 3 = 1 → simple: pw_lo += vib_period each frame (in-place on inst table).
    bit 3 = 0 → standard bidirectional: bounce pw_hi between $08 and $0E.
    On entry: X = voice slot in $FA; inst index in Y (from vibrato setup). -/
def emitPWM (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_inst"
  let cb := cb.emitInst I.tay              -- Y = inst index
  -- Load fx_flags for this instrument
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_fx_flags" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup :: cb.absFixups }
  let cb := cb.emitInst (I.and_imm 0x08)  -- bit 3 = simple PWM
  let cb := cb.emitBranch .BNE "pw_simple"
  -- Standard bidirectional PWM: check vib_period (= pwm speed byte)
  let fixup2 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_vib_period" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup2 :: cb.absFixups }
  -- BEQ "pw_done" would be >127 bytes: use BNE+JMP trampoline
  let cb := cb.emitBranch .BNE "pw_bidir_active"   -- period≠0: do bidir PWM
  let cb := cb.emitJmpLabel .JMP "pw_done"           -- period=0: skip
  let cb := cb.label "pw_bidir_active"
  let cb := cb.emitInst (I.sta_zp 0xF9)  -- $F9 = vib_period (speed byte)
  -- DEC v_pwm_step[X]; BMI+JMP trampoline (BPL "pw_done" would be >127 bytes)
  let cb := cb.emitDecAbsX "v_pwm_step"
  let cb := cb.emitBranch .BMI "pw_step_expired"    -- just expired: do update
  let cb := cb.emitJmpLabel .JMP "pw_done"           -- not expired: skip
  let cb := cb.label "pw_step_expired"
  -- Reload step counter: low 5 bits of speed
  let cb := cb.emitInst (I.lda_zp 0xF9)
  let cb := cb.emitInst (I.and_imm 0x1F)
  let cb := cb.emitStaAbsX "v_pwm_step"
  -- Extract step size: high 3 bits
  let cb := cb.emitInst (I.lda_zp 0xF9)
  let cb := cb.emitInst (I.and_imm 0xE0)
  let cb := cb.emitInst (I.sta_zp 0xF9)  -- $F9 = step size
  -- Check direction
  let cb := cb.emitLdaAbsX "v_pwm_dir"
  let cb := cb.emitBranch .BNE "pw_bidir_down"
  -- UP: i_pwlo[Y] += step; i_pwhi[Y] += carry
  let cb := cb.emitInst I.clc
  let fixup3 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwlo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup3 :: cb.absFixups }
  let cb := cb.emitInst (I.adc_zp 0xF9)
  let fixup4 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwlo" }
  let cb := { cb with bytes := cb.bytes ++ #[0x99, 0, 0],
                      absFixups := fixup4 :: cb.absFixups }
  let fixup5 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwhi" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup5 :: cb.absFixups }
  let cb := cb.emitInst (I.adc_imm 0)    -- carry
  let cb := cb.emitInst (I.and_imm 0x0F) -- mask to 4 bits
  let fixup6 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwhi" }
  let cb := { cb with bytes := cb.bytes ++ #[0x99, 0, 0],
                      absFixups := fixup6 :: cb.absFixups }
  -- Compare with upper bound $0E; flip direction if equal
  let cb := cb.emitInst (I.cmp_imm 0x0E)
  let cb := cb.emitBranch .BNE "pw_bidir_write"
  let cb := cb.emitInst (I.lda_imm 1)
  let cb := cb.emitStaAbsX "v_pwm_dir"
  let cb := cb.emitJmpLabel .JMP "pw_bidir_write"
  let cb := cb.label "pw_bidir_down"
  -- DOWN: i_pwlo[Y] -= step; i_pwhi[Y] -= borrow
  let cb := cb.emitInst I.sec
  let fixup7 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwlo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup7 :: cb.absFixups }
  let cb := cb.emitInst (I.sbc_zp 0xF9)
  let fixup8 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwlo" }
  let cb := { cb with bytes := cb.bytes ++ #[0x99, 0, 0],
                      absFixups := fixup8 :: cb.absFixups }
  let fixup9 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwhi" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup9 :: cb.absFixups }
  let cb := cb.emitInst (I.sbc_imm 0)
  let cb := cb.emitInst (I.and_imm 0x0F)
  let fixup10 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwhi" }
  let cb := { cb with bytes := cb.bytes ++ #[0x99, 0, 0],
                      absFixups := fixup10 :: cb.absFixups }
  let cb := cb.emitInst (I.cmp_imm 0x08)
  let cb := cb.emitBranch .BNE "pw_bidir_write"
  let cb := cb.emitInst (I.lda_imm 0)
  let cb := cb.emitStaAbsX "v_pwm_dir"
  let cb := cb.label "pw_bidir_write"
  -- Write pw_lo/hi to SID
  let fixup11 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwlo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup11 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF8)
  let fixup12 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwhi" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup12 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF7)
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let cb := cb.emitInst (I.lda_zp 0xF8)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 2))  -- PW_LO
  let cb := cb.emitInst (I.lda_zp 0xF7)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 3))  -- PW_HI
  let cb := cb.emitJmpLabel .JMP "pw_done"
  -- Simple PWM: pw_lo += vib_period (inst.pw_lo is mutated in-place)
  let cb := cb.label "pw_simple"
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_inst"
  let cb := cb.emitInst I.tay
  -- Load vib_period as the increment
  let fixup13 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_vib_period" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup13 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF9)
  -- i_pwlo[Y] += vib_period. In the original engine, carry was clear from AND #$08.
  -- In our layout the AND is far away (branch taken to pw_simple), so we must CLC.
  let fixup14 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwlo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup14 :: cb.absFixups }
  let cb := cb.emitInst I.clc
  let cb := cb.emitInst (I.adc_zp 0xF9)
  let fixup15 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwlo" }
  let cb := { cb with bytes := cb.bytes ++ #[0x99, 0, 0],
                      absFixups := fixup15 :: cb.absFixups }
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let fixup16 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwlo" }
  -- Reload Y for inst (it was clobbered by sidoff)
  -- Actually we need to store first, then do SID write
  -- Recompute: load v_inst[X], tay, load i_pwlo[Y], write to SID
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_inst"
  let cb := cb.emitInst I.tay
  let fixup17 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwlo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup17 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF8)
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let cb := cb.emitInst (I.lda_zp 0xF8)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 2))  -- PW_LO only
  let cb := cb.label "pw_done"
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  cb

-- ==========================================================================
-- §13 emitSkydive
-- ==========================================================================

/-- Skydive (drum): bit 0 of fx_flags. DEC freq_hi each frame after note
    midpoint, writing OLD value; writes $80 ctrl at sweep start.
    Guards: v_fhi != 0, v_dur != 0.
    On entry: X = voice slot ($FA); Y = SID base offset. -/
def emitSkydive (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_inst"
  let cb := cb.emitInst I.tay
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_fx_flags" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup :: cb.absFixups }
  let cb := cb.emitInst (I.and_imm 0x01)
  let cb := cb.emitBranch .BEQ "no_sky"
  -- Guard: v_fhi != 0
  let cb := cb.emitLdaAbsX "v_fhi"
  let cb := cb.emitBranch .BEQ "no_sky"
  -- Guard: v_dur != 0
  let cb := cb.emitLdaAbsX "v_dur"
  let cb := cb.emitBranch .BEQ "no_sky"
  -- Check note age vs midpoint: (orig_dur - 1) vs v_dur
  let cb := cb.emitLdaAbsX "v_flags"
  let cb := cb.emitInst (I.and_imm 0x1F)  -- orig_dur
  let cb := cb.emitInst I.sec
  let cb := cb.emitInst (I.sbc_imm 1)     -- orig_dur - 1
  let cb := cb.emitCmpAbsX "v_dur"        -- compare with current v_dur
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let cb := cb.emitBranch .BCC "sky_path_b"  -- past midpoint: path A
  -- Path A: DEC v_fhi, write OLD value, ctrl with gate clear
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_fhi"        -- A = old v_fhi
  let cb := cb.emitInst (I.sta_zp 0xF8)   -- save old
  let cb := cb.emitDecAbsX "v_fhi"
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let cb := cb.emitInst (I.lda_zp 0xF8)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 1))  -- freq_hi = old
  let cb := cb.emitLdaAbsX "v_ctrl"
  let cb := cb.emitInst (I.and_imm 0xFE)  -- clear gate
  let cb := cb.emitBranch .BNE "sky_write_ctrl"
  let cb := cb.label "sky_path_b"
  -- Path B: write v_fhi unchanged, ctrl = $80 (test-bit)
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_fhi"
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let cb := cb.emitLdaAbsX "v_fhi"
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 1))
  let cb := cb.emitInst (I.lda_imm 0x80)  -- test-bit ctrl
  let cb := cb.label "sky_write_ctrl"
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 4))  -- ctrl
  let cb := cb.label "no_sky"
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  cb

-- ==========================================================================
-- §14 emitSlowDescent
-- ==========================================================================

/-- Slow-descent: bit 1 of fx_flags. On long notes (orig_dur >= $10) in the
    tail (v_dur < $12), every other frame ((frame_ctr & 1) != 0), DEC v_fhi.
    Guard: v_fhi != 0.
    Writes NEW value directly to SID. -/
def emitSlowDescent (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_inst"
  let cb := cb.emitInst I.tay
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_fx_flags" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup :: cb.absFixups }
  let cb := cb.emitInst (I.and_imm 0x02)
  let cb := cb.emitBranch .BEQ "no_descent"
  -- Guard: orig_dur >= $10
  let cb := cb.emitLdaAbsX "v_flags"
  let cb := cb.emitInst (I.and_imm 0x1F)
  let cb := cb.emitInst (I.cmp_imm 0x10)
  let cb := cb.emitBranch .BCC "no_descent"
  -- Guard: v_dur < $12
  let cb := cb.emitLdaAbsX "v_dur"
  let cb := cb.emitInst (I.cmp_imm 0x12)
  let cb := cb.emitBranch .BCS "no_descent"
  -- Guard: (frame_ctr & 1) != 0
  let fixup2 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "frame_ctr" }
  let cb := { cb with bytes := cb.bytes ++ #[0xAD, 0, 0],
                      absFixups := fixup2 :: cb.absFixups }
  let cb := cb.emitInst (I.and_imm 0x01)
  let cb := cb.emitBranch .BEQ "no_descent"
  -- Guard: v_fhi != 0
  let cb := cb.emitLdaAbsX "v_fhi"
  let cb := cb.emitBranch .BEQ "no_descent"
  -- DEC v_fhi, write to SID
  let cb := cb.emitDecAbsX "v_fhi"
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let cb := cb.emitLdaAbsX "v_fhi"
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 1))
  let cb := cb.label "no_descent"
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  cb

-- ==========================================================================
-- §15 emitTableArp
-- ==========================================================================

/-- Table-arp: bit 2 of fx_flags. When (frame_ctr & 7) == 0 → play base pitch;
    else play pitch+12 (octave up). Reads from freq table and writes both
    freq_lo and freq_hi to SID. -/
def emitTableArp (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_inst"
  let cb := cb.emitInst I.tay
  let fixup : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_fx_flags" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup :: cb.absFixups }
  let cb := cb.emitInst (I.and_imm 0x04)
  let cb := cb.emitBranch .BEQ "no_arp"
  -- (frame_ctr & 7) == 0 → base pitch
  let fixup2 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "frame_ctr" }
  let cb := { cb with bytes := cb.bytes ++ #[0xAD, 0, 0],
                      absFixups := fixup2 :: cb.absFixups }
  let cb := cb.emitInst (I.and_imm 0x07)
  let cb := cb.emitBranch .BEQ "arp_base"
  -- Offset pitch: v_pitch + 12
  let cb := cb.emitInst I.clc
  let cb := cb.emitLdaAbsX "v_pitch"
  let cb := cb.emitInst (I.adc_imm 12)
  let cb := cb.emitJmpLabel .JMP "arp_lookup"
  let cb := cb.label "arp_base"
  let cb := cb.emitLdaAbsX "v_pitch"
  let cb := cb.label "arp_lookup"
  let cb := cb.emitInst I.tay              -- Y = pitch
  let fixup3 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "freq_lo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup3 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF8)
  let fixup4 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "freq_hi" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup4 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF9)
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let cb := cb.emitInst (I.lda_zp 0xF9)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 1))
  let cb := cb.emitInst (I.lda_zp 0xF8)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 0))
  let cb := cb.label "no_arp"
  cb

-- ==========================================================================
-- Combined effects emission + voice loop tail
-- ==========================================================================

/-- Emit the full effects chain for both sustain and effects-only paths.
    Called after vibrato setup (voice X in $FA, Y = SID base).
    Order: vibrato → PWM → skydive → slow-descent → table-arp → voice-loop-tail. -/
def emitEffectsChain (cb : CodeBuilder) : CodeBuilder :=
  let cb := emitVibrato cb
  let cb := emitPWM cb
  let cb := emitSkydive cb
  let cb := emitSlowDescent cb
  let cb := emitTableArp cb
  -- Voice loop tail: DEX; if negative, done; else JMP voice_top
  -- BMI "play_done" would be >127 bytes: use BPL+JMP trampoline
  let cb := cb.emitInst (I.ldx_zp 0xFA)   -- restore X
  let cb := cb.emitInst I.dex
  let cb := cb.emitBranch .BPL "effects_next_voice"   -- X >= 0: continue
  let cb := cb.emitJmpLabel .JMP "play_done"           -- X < 0: all done
  let cb := cb.label "effects_next_voice"
  let cb := cb.emitJmpLabel .JMP "voice_top"
  cb

-- ==========================================================================
-- §9  emitNoteLoad
-- ==========================================================================

/-- Note-load: called when tick gate passes AND v_dur expired (went negative).
    On entry: X = voice slot. Y = SID base offset.
    Reads orderlist → pattern index → pattern bytes (var-length Hubbard format).
    Pattern byte format:
      byte 0: bits 0-4 = duration (0-31), bit 5 = no_release, bit 6 = tie, bit 7 = has_modifier
      if has_modifier: byte 1 = inst index (or porta byte if bit 7 set)
      if not pure-tie: last byte = pitch
    On note-load: update v_dur, v_flags, v_inst, v_pitch, write SID.
    End-of-song volume fade: VOL = clamp($75 - v_olpos[V3], 0, $0F). -/
def emitNoteLoad (cb : CodeBuilder) : CodeBuilder :=
  let cb := cb.label "note_load"
  let cb := cb.emitInst (I.stx_zp 0xFA)   -- save voice slot
  -- Load orderlist pointer for voice X into ZP $FB/$FC
  let cb := cb.emitLdaAbsX "ol_lo"
  let cb := cb.emitInst (I.sta_zp 0xFB)
  let cb := cb.emitLdaAbsX "ol_hi"
  let cb := cb.emitInst (I.sta_zp 0xFC)
  -- Read orderlist[v_olpos[X]]
  let cb := cb.emitLdaAbsX "v_olpos"
  let cb := cb.emitInst I.tay
  let cb := cb.emitInst ⟨.LDA, .indY 0xFB⟩
  let cb := cb.emitInst (I.cmp_imm 0xFF)
  let cb := cb.emitBranch .BEQ "ol_wrap"
  let cb := cb.emitInst (I.cmp_imm 0xFE)
  let cb := cb.emitBranch .BEQ "song_end"
  -- A = pattern index
  let cb := cb.emitInst I.tay
  -- Look up pattern address
  let fixup1 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "pat_ptr_lo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup1 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xFD)
  let fixup2 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "pat_ptr_hi" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup2 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xFE)
  -- Y = v_patpos[X] (byte offset within pattern)
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_patpos"
  let cb := cb.emitInst I.tay
  -- Read flags+dur byte from pattern
  let cb := cb.emitInst ⟨.LDA, .indY 0xFD⟩
  -- $FF = end of pattern → advance_ol
  let cb := cb.emitInst (I.cmp_imm 0xFF)
  let cb := cb.emitBranch .BEQ "advance_ol"
  -- Save flags+dur byte to both v_flags[X] and ZP $F2 (for BIT test below)
  let cb := cb.emitStaAbsX "v_flags"
  let cb := cb.emitInst (I.sta_zp 0xF2)   -- $F2 = saved flags byte (for BIT)
  let cb := cb.emitInst (I.and_imm 0x1F)
  let cb := cb.emitStaAbsX "v_dur"         -- v_dur[X] = duration
  -- Volume fade: VOL = clamp($75 - v_olpos[V3], 0, $0F)
  let fixup3 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "v_olpos_v3" }
  let cb := { cb with bytes := cb.bytes ++ #[0xAD, 0, 0],
                      absFixups := fixup3 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF6)
  let cb := cb.emitInst (I.lda_imm 0x75)
  let cb := cb.emitInst I.sec
  let cb := cb.emitInst (I.sbc_zp 0xF6)
  let cb := cb.emitInst (I.cmp_imm 0x0F)
  let cb := cb.emitBranch .BCC "vol_ok"
  let cb := cb.emitInst (I.lda_imm 0x0F)
  let cb := cb.label "vol_ok"
  let cb := cb.emitInst (I.sta_abs (SID_BASE + 0x18))
  -- Gate mask: default $FF; cleared to $FE for ties
  let cb := cb.emitInst (I.lda_imm 0xFF)
  let cb := cb.emitInst (I.sta_zp 0xF6)   -- $F6 = gate_mask
  -- BIT $F2: V = bit 6 (tie), N = bit 7 (new instrument follows)
  let cb := cb.emitInst (I.bit_zp 0xF2)
  -- BVS tie_path: bit 6 (tie) is set → clear gate bit (gate stays off)
  let cb := cb.emitBranch .BVS "is_tie"
  -- Not tie: advance v_patpos past flags byte, then check for new inst
  let cb := cb.emitIncAbsX "v_patpos"
  -- Must reload flags byte to set N from bit7 (INC clobbered the N flag).
  -- Original engine: LDA $C409 (saved flags); BPL (no new inst).
  let cb := cb.emitInst (I.lda_zp 0xF2)   -- reload saved flags byte
  -- BPL no_new_inst: bit 7 (N) clear = no new instrument byte
  let cb := cb.emitBranch .BPL "no_new_inst"
  -- New instrument byte: INY, read it, store to v_inst[X], INC v_patpos
  let cb := cb.emitInst I.iny
  let cb := cb.emitInst ⟨.LDA, .indY 0xFD⟩
  let cb := cb.emitStaAbsX "v_inst"
  let cb := cb.emitIncAbsX "v_patpos"
  let cb := cb.label "no_new_inst"
  -- Read pitch byte: INY, (FD),Y
  let cb := cb.emitInst I.iny
  let cb := cb.emitInst ⟨.LDA, .indY 0xFD⟩
  let cb := cb.emitStaAbsX "v_pitch"
  -- Freq table lookup: Y = pitch
  let cb := cb.emitInst I.tay
  let fixup4 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "freq_lo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup4 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF7)   -- freq_lo temp
  let fixup5 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "freq_hi" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup5 :: cb.absFixups }
  let cb := cb.emitStaAbsX "v_fhi"         -- v_fhi[X] = freq_hi (for effects)
  -- Write freq to SID (hi first, then lo — matches original)
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay
  let cb := cb.emitLdaAbsX "v_fhi"
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 1))  -- freq_hi
  let cb := cb.emitInst (I.lda_zp 0xF7)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 0))  -- freq_lo
  -- Advance v_patpos past pitch byte
  let cb := cb.emitIncAbsX "v_patpos"
  let cb := cb.emitJmpLabel .JMP "write_inst_to_sid"
  -- Tie path: DEC gate_mask ($FF → $FE = clear gate bit)
  let cb := cb.label "is_tie"
  let cb := cb.emitInst (I.dec_zp 0xF6)
  -- Write instrument table to SID (ctrl with gate mask, pw, ad, sr)
  let cb := cb.label "write_inst_to_sid"
  -- Peek next byte; if $FF, pattern ended → advance_ol
  let cb := cb.emitInst (I.ldx_zp 0xFA)
  let cb := cb.emitLdaAbsX "v_patpos"
  let cb := cb.emitInst I.tay
  let cb := cb.emitInst ⟨.LDA, .indY 0xFD⟩
  let cb := cb.emitInst (I.cmp_imm 0xFF)
  let cb := cb.emitBranch .BNE "pat_continues"
  -- Pattern ended: zero v_patpos, bump v_olpos
  let cb := cb.emitInst (I.lda_imm 0)
  let cb := cb.emitStaAbsX "v_patpos"
  let cb := cb.emitIncAbsX "v_olpos"
  let cb := cb.label "pat_continues"
  -- Write instrument table to SID.
  -- Strategy: load inst fields into ZP temps (using Y=inst#), then write to SID (Y=sidoff).
  -- Step 1: collect ctrl, pw_lo, pw_hi, AD, SR into ZP temps.
  let cb := cb.emitLdaAbsX "v_inst"
  let cb := cb.emitInst I.tay              -- Y = inst index
  let fixup6 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_ctrl" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup6 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF3)   -- ZP$F3 = raw ctrl
  let fixup7 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwlo" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup7 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF4)   -- ZP$F4 = pw_lo
  let fixup8 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_pwhi" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup8 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF5)   -- ZP$F5 = pw_hi
  let fixup9 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_ad" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup9 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF7)   -- ZP$F7 = AD
  let fixup10 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "i_sr" }
  let cb := { cb with bytes := cb.bytes ++ #[0xB9, 0, 0],
                      absFixups := fixup10 :: cb.absFixups }
  let cb := cb.emitInst (I.sta_zp 0xF8)   -- ZP$F8 = SR
  -- Step 2: write to SID using Y = sidoff
  let cb := cb.emitLdaAbsX "v_sidoff"
  let cb := cb.emitInst I.tay              -- Y = sidoff
  -- ctrl: AND gate_mask, write to SID, also save raw ctrl to v_ctrl[X]
  let cb := cb.emitInst (I.lda_zp 0xF3)
  let cb := cb.emitStaAbsX "v_ctrl"        -- v_ctrl[X] = raw ctrl (unmasked)
  let cb := cb.emitInst (I.and_zp 0xF6)   -- AND gate_mask
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 4))  -- ctrl to SID
  let cb := cb.emitInst (I.lda_zp 0xF4)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 2))  -- pw_lo to SID
  let cb := cb.emitInst (I.lda_zp 0xF5)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 3))  -- pw_hi to SID
  let cb := cb.emitInst (I.lda_zp 0xF7)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 5))  -- AD to SID
  let cb := cb.emitInst (I.lda_zp 0xF8)
  let cb := cb.emitInst (I.sta_absY (SID_BASE + 6))  -- SR to SID
  -- Voice loop tail: DEX, loop or done
  let cb := cb.emitInst I.dex
  let cb := cb.emitBranch .BMI "play_done"
  let cb := cb.emitJmpLabel .JMP "voice_top"
  -- Orderlist wrap ($FF → reset v_olpos, v_patpos, retry)
  let cb := cb.label "ol_wrap"
  let cb := cb.emitInst (I.lda_imm 0)
  let cb := cb.emitStaAbsX "v_dur"
  let cb := cb.emitStaAbsX "v_olpos"
  let cb := cb.emitStaAbsX "v_patpos"
  let cb := cb.emitJmpLabel .JMP "note_load"
  -- Advance orderlist ($FF at end of pattern)
  let cb := cb.label "advance_ol"
  let cb := cb.emitInst (I.lda_imm 0)
  let cb := cb.emitStaAbsX "v_patpos"
  let cb := cb.emitIncAbsX "v_olpos"
  let cb := cb.emitJmpLabel .JMP "note_load"
  -- Song end: set engine_state = $C0
  let cb := cb.label "song_end"
  let cb := cb.emitInst (I.lda_imm 0xC0)
  let fixup11 : AbsFixup := { byteIdx := cb.bytes.size + 1, targetLabel := "engine_state" }
  let cb := { cb with bytes := cb.bytes ++ #[0x8D, 0, 0],
                      absFixups := fixup11 :: cb.absFixups }
  let cb := cb.emitInst I.rts
  cb

-- ==========================================================================
-- §16 generateSID
-- ==========================================================================

def generateSID (song : MoMSong) : Bytes := Id.run do
  let base : UInt16 := 0x1000
  let mut cb : CodeBuilder := { baseAddr := base }

  -- Jump table (init at base+0, play at base+3)
  cb := cb.emitJmpLabel .JMP "init"
  cb := cb.emitJmpLabel .JMP "play"

  -- ===== PLAYER CODE =====

  -- §3 init
  cb := emitInit cb

  -- §4 play dispatch
  cb := emitPlay cb

  -- §5 first-frame (falls through to per_voice_start)
  cb := emitFirstFrame cb

  -- §6 end-of-song
  cb := emitEndOfSong cb

  -- §7 per-voice loop structure
  cb := emitPerVoiceLoop cb

  -- §10 sustain/HR (at sustain_check label, falls through to effects_only)
  cb := emitSustainHR cb

  -- §8 effects-only entry: save X, then run effects chain
  cb := emitEffectsOnly cb

  -- Combined effects chain: vibrato → PWM → skydive → slow-descent → table-arp → voice-tail
  cb := emitEffectsChain cb

  -- §9 note-load path (after voice loop tail, unreachable but needed for label)
  cb := emitNoteLoad cb

  -- play_done label (after DEX + BMI)
  cb := cb.label "play_done"
  cb := cb.emitInst I.rts

  -- ===== DATA TABLES =====

  -- Frequency table (split lo/hi arrays, indexed by pitch 0-95)
  cb := cb.label "freq_lo"
  cb := cb.emitData song.freqLo
  cb := cb.label "freq_hi"
  cb := cb.emitData song.freqHi

  -- Instrument tables (flat arrays indexed by inst index)
  let nInst := song.instruments.length
  cb := cb.label "i_ctrl"
  cb := cb.emitData (song.instruments.map (·.ctrl))
  cb := cb.label "i_ad"
  cb := cb.emitData (song.instruments.map (·.ad))
  cb := cb.label "i_sr"
  cb := cb.emitData (song.instruments.map (·.sr))
  cb := cb.label "i_pwlo"
  cb := cb.emitData (song.instruments.map (·.pwLo))
  cb := cb.label "i_pwhi"
  cb := cb.emitData (song.instruments.map (·.pwHi))
  cb := cb.label "i_vib_depth"
  cb := cb.emitData (song.instruments.map (·.vibDepth))
  cb := cb.label "i_vib_period"
  cb := cb.emitData (song.instruments.map (·.vibPeriod))
  cb := cb.label "i_fx_flags"
  cb := cb.emitData (song.instruments.map (·.fxFlags))

  -- Pattern pointer tables: emit placeholders, patch after patterns are laid out.
  -- The original patPtrLo/Hi contain addresses in the original SID's address space,
  -- which are wrong for our rebuilt SID. We must use the actual addresses where we
  -- emit the patterns below.
  cb := cb.label "pat_ptr_lo"
  cb := cb.emitData (List.replicate song.patterns.length 0)
  cb := cb.label "pat_ptr_hi"
  cb := cb.emitData (List.replicate song.patterns.length 0)

  -- Pattern raw bytes (each $FF-terminated). Label each pattern so we can patch
  -- the pointer table above with actual addresses.
  let mut patIdx := 0
  for pat in song.patterns do
    cb := cb.label s!"pat_{patIdx}"
    cb := cb.emitData pat
    patIdx := patIdx + 1

  -- Patch pat_ptr_lo / pat_ptr_hi with actual addresses of each pattern.
  match cb.lookupLabel "pat_ptr_lo", cb.lookupLabel "pat_ptr_hi" with
  | some ptrLoAddr, some ptrHiAddr =>
    let ptrLoOff := (ptrLoAddr - base).toNat
    let ptrHiOff := (ptrHiAddr - base).toNat
    let mut bytes := cb.bytes
    for i in List.range song.patterns.length do
      match cb.lookupLabel s!"pat_{i}" with
      | some patAddr =>
        bytes := bytes.set! (ptrLoOff + i) patAddr.toUInt8
        bytes := bytes.set! (ptrHiOff + i) (patAddr >>> 8).toUInt8
      | none => pure ()
    cb := { cb with bytes := bytes }
  | _, _ => pure ()

  -- Orderlists (V1/V2/V3)
  cb := cb.label "ol_v1"
  cb := cb.emitData song.olV1
  cb := cb.label "ol_v2"
  cb := cb.emitData song.olV2
  cb := cb.label "ol_v3"
  cb := cb.emitData song.olV3

  -- Orderlist active pointers (per voice, filled by init copy from subtune table)
  -- Active ol_lo[0..2] / ol_hi[0..2] (6 bytes total)
  -- Initial values: point to olV1/V2/V3 (for subtune 0; init overwrites for other subtunes)
  -- We compute these addresses via fixups after layout is known.
  -- Strategy: emit 6 placeholder bytes and fix them up as labels.
  -- Actually the subtune table already encodes the absolute addresses for each subtune.
  -- For single-subtune builds we can just hardcode; for multi-subtune we need the copy loop.
  -- Use: ol_active_lo[0..2] = lo bytes of V1/V2/V3 ol addresses
  --      ol_active_hi[0..2] = hi bytes
  -- We lay out the active pointers as a 6-byte block that init copies INTO.
  -- The subtune table (ol_subtune_table) holds 3 subtunes × 6 bytes of addresses.
  cb := cb.label "ol_active_lo"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "ol_active_hi"
  cb := cb.emitData [0, 0, 0]

  -- ol_lo[X] and ol_hi[X] used by note_load: same as active arrays.
  -- We alias them: ol_lo = ol_active_lo, ol_hi = ol_active_hi.
  -- But note_load uses LDA ol_lo,X / ol_hi,X (abs,X). The active arrays
  -- are already labeled. The init copy fills them from the subtune table.
  -- Actually: let's use a flat 6-byte block [lo0,lo1,lo2] / [hi0,hi1,hi2]
  -- but the init copy puts subtune_table[0..5] → ol_active_lo[0..5] as a
  -- 6-byte block indexed Y=0..5. The lo bytes go to Y=0,1,2 and hi to Y=3,4,5.
  -- This means ol_active_lo must be followed immediately by ol_active_hi.
  -- The label "ol_lo" = start of ol_active_lo (lo bytes), "ol_hi" = start of ol_active_hi.
  -- But for LDA ol_lo,X (abs,X) with X=0,1,2 we need lo bytes at consecutive addresses.

  -- Subtune orderlist pointer table: 3 subtunes × 6 bytes (lo0,lo1,lo2,hi0,hi1,hi2)
  -- For now just emit subtune 0's pointers as the only subtune.
  -- We'll store: subtune0 = [olV1_lo, olV2_lo, olV3_lo, olV1_hi, olV2_hi, olV3_hi]
  -- Addresses of olV1/V2/V3 are computed after layout.
  -- Emit placeholder subtune table; will be fixed by the addr system below.
  cb := cb.label "ol_subtune_table"
  -- 6 placeholder bytes: lo3 + hi3 for V1/V2/V3
  -- These need to be patched to the actual addresses of ol_v1/ol_v2/ol_v3.
  -- Use AbsFixups for each byte... but AbsFixup writes 2 bytes (lo+hi).
  -- Emit lo bytes first, then hi bytes.
  -- lo byte of ol_v1 address: fixup writes addr[0..7] to byte N
  -- hi byte: fixup writes addr[8..15] to byte N+1
  -- But our fixup always writes both lo+hi. For the lo-only and hi-only
  -- slots we need separate single-byte fixups.
  -- Simplest: use the existing 2-byte AbsFixup for each, overlapping pairs.
  -- Alternatively: write the 6-byte block after resolve using a post-process.
  -- For now, emit 6 bytes and add custom fixups for each byte individually.
  -- We'll use a trick: emit 6 placeholder bytes and fix them in a post-pass.
  cb := cb.emitData [0, 0, 0, 0, 0, 0]

  -- Voice state variables (3 bytes each)
  cb := cb.label "v_dur"
  let (vi1, vi2, vi3) := song.initVInst
  let (vp1, vp2, vp3) := song.initVPitch
  let (vf1, vf2, vf3) := song.initVFhi
  let (vs1, vs2, vs3) := song.initVPwmStep
  let (vd1, vd2, vd3) := song.initVPwmDir
  let (vc1, vc2, vc3) := song.initVCtrl
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_olpos"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_patpos"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_flags"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_pitch"
  cb := cb.emitData [vp1, vp2, vp3]     -- load-time binary values
  cb := cb.label "v_inst"
  cb := cb.emitData [vi1, vi2, vi3]     -- v_inst[V1]=$07, V2=$0E, V3=$03
  cb := cb.label "v_ctrl"
  cb := cb.emitData [vc1, vc2, vc3]     -- v_ctrl binary values
  cb := cb.label "v_fhi"
  cb := cb.emitData [vf1, vf2, vf3]     -- v_fhi binary values
  cb := cb.label "v_pwm_step"
  cb := cb.emitData [vs1, vs2, vs3]
  cb := cb.label "v_pwm_dir"
  cb := cb.emitData [vd1, vd2, vd3]
  -- v_sidoff: SID register offsets for slots 0/1/2 → V1/V2/V3
  cb := cb.label "v_sidoff"
  cb := cb.emitData [0, 7, 14]
  -- ol_lo / ol_hi: aliases to ol_active_lo / ol_active_hi (same bytes)
  -- These are already labeled as ol_active_lo / ol_active_hi above.
  -- Add aliases so note_load's LDA ol_lo,X works.
  -- The labels were already emitted; add extra alias labels here.
  -- (We can't add labels to past positions, so we reference the labels directly.)
  -- Note: ol_lo and ol_hi are already in the note_load via ol_active_lo fixups.

  -- v_olpos_v3 alias: byte 2 of v_olpos (for volume fade)
  -- The label "v_olpos" points to byte 0; v_olpos_v3 = v_olpos + 2.
  -- We'll need this in note_load. Emit a separate single-byte label.
  -- Strategy: don't use a separate label; instead in note_load use LDA v_olpos+2
  -- via AbsFixup pointing at v_olpos_v3. We need to emit it here.
  -- Actually v_olpos is laid out as [V1, V2, V3], so v_olpos[2] = *(v_olpos+2).
  -- We add a label at current address that's v_olpos_v3 AFTER emitting v_olpos[2].
  -- But v_olpos was already emitted above. We need to retroactively add a label.
  -- Workaround: emit a 1-byte "peek" at v_olpos_v3 that gets its address from
  -- the label system. Use: labels.lookup "v_olpos" + 2 in a post-pass.
  -- For now: hardcode v_olpos_v3 as a forward label in note_load. We'll fix it
  -- by adding a label "v_olpos_v3" here that = v_olpos + 2 bytes.
  -- Since we can't go back, emit v_olpos_v3 by adjusting the label:
  -- cb.labels already has "v_olpos" at some address. We want "v_olpos_v3" at +2.
  -- Use a manual label:
  match cb.lookupLabel "v_olpos" with
  | some vopAddr =>
    cb := { cb with labels := ("v_olpos_v3", vopAddr + 2) :: cb.labels }
  | none => pure ()

  -- Also alias "ol_lo" → "ol_active_lo" and "ol_hi" → "ol_active_hi":
  match cb.lookupLabel "ol_active_lo" with
  | some lo => cb := { cb with labels := ("ol_lo", lo) :: cb.labels }
  | none => pure ()
  match cb.lookupLabel "ol_active_hi" with
  | some hi => cb := { cb with labels := ("ol_hi", hi) :: cb.labels }
  | none => pure ()

  -- Tick divider and reload (global, not per-voice)
  cb := cb.label "v_tickdiv"
  cb := cb.emitByte song.tickReload        -- initial = reload value
  cb := cb.label "v_tickreload"
  cb := cb.emitByte song.tickReload

  -- Engine state byte ($C41D equivalent)
  cb := cb.label "engine_state"
  cb := cb.emitByte 0x40                  -- initial = first-frame sentinel

  -- Frame counter
  cb := cb.label "frame_ctr"
  cb := cb.emitByte 0x00

  -- Scratch: current voice's SID base offset (saved for SID writes in effects)
  cb := cb.label "v_sidoff_cur"
  cb := cb.emitByte 0x00

  -- Patch the subtune table lo/hi bytes.
  -- We need: ol_subtune_table[0..5] = [lo(ol_v1), lo(ol_v2), lo(ol_v3), hi(ol_v1), hi(ol_v2), hi(ol_v3)]
  -- Find the address of "ol_subtune_table" and patch it.
  match cb.lookupLabel "ol_subtune_table",
        cb.lookupLabel "ol_v1",
        cb.lookupLabel "ol_v2",
        cb.lookupLabel "ol_v3" with
  | some tblAddr, some v1Addr, some v2Addr, some v3Addr =>
    let tblOff := (tblAddr - base).toNat
    let bytes := cb.bytes
    let bytes := bytes.set! tblOff        v1Addr.toUInt8
    let bytes := bytes.set! (tblOff + 1)  v2Addr.toUInt8
    let bytes := bytes.set! (tblOff + 2)  v3Addr.toUInt8
    let bytes := bytes.set! (tblOff + 3)  (v1Addr >>> 8).toUInt8
    let bytes := bytes.set! (tblOff + 4)  (v2Addr >>> 8).toUInt8
    let bytes := bytes.set! (tblOff + 5)  (v3Addr >>> 8).toUInt8
    cb := { cb with bytes := bytes }
  | _, _, _, _ => pure ()

  -- Resolve all fixups
  cb := cb.resolve

  let header : PSIDHeader := {
    initAddr := base
    playAddr := base + 3
    songs := 1
    startSong := 1
    title := song.title
    author := song.author
    released := song.released
  }
  return buildSID header cb.bytes

end MasterOfMagicNS
