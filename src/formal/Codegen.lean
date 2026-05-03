/-
  Codegen.lean — Generate a SID file from a USF Song.

  Produces a valid .sid file containing a 6502 player + song data.
  The player processes voices each frame: decrement duration,
  load notes from patterns, write registers to SID.

  Memory layout:
    $1000: JMP init / JMP play (entry points)
    $1006+: player code (~800 bytes)
    after code: data tables (freq, instruments, patterns, orderlists)

  Voice state: 3-entry absolute tables (indexed by X = 0/1/2)
    v_dur[3]      duration countdown (DEC / BMI noteLoad)
    v_pattlo[3]   pattern data pointer lo
    v_patthi[3]   pattern data pointer hi
    v_olpos[3]    orderlist position
    v_ctrl[3]     current ctrl byte (waveform)
    v_wptr[3]     waveform program pointer
    v_inst[3]     current instrument index
    v_sidoff[3]   SID register offset (0/7/14) — constant per voice

  Scratch ZP:
    $FC/$FD       indirect pointer for pattern reads
-/

import SID
import Asm6502
import PSIDFile
import Compile
import CommandoData

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

private def emitInit (cb : CodeBuilder) (song : Song) : CodeBuilder := Id.run do
  let mut cb := cb.label "init"

  -- Set volume
  cb := cb.emitInst (I.lda_imm 0x0F)
  cb := cb.emitInst (I.sta_abs (SID_BASE + 0x18))

  -- Clear SID ctrl registers
  cb := cb.emitInst (I.lda_imm 0x00)
  cb := cb.emitInst (I.sta_abs (SID_BASE + 4))
  cb := cb.emitInst (I.sta_abs (SID_BASE + 11))
  cb := cb.emitInst (I.sta_abs (SID_BASE + 18))

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

private def emitPlay (cb : CodeBuilder) (song : Song) : CodeBuilder := Id.run do
  let mut cb := cb.label "play"

  -- Increment global frame counter (for arpeggio phase)
  cb := cb.emitInst (I.inc_zp 0x50)

  -- Process voices in song order
  let nVoices := song.voiceOrder.length
  for h : i in [:nVoices] do
    match song.voiceOrder[i]? with
    | some v =>
      cb := cb.emitInst (I.ldx_imm v.val.toUInt8)
      if i + 1 < nVoices then
        cb := cb.emitJmpLabel .JSR "exec_voice"
      else
        cb := cb.emitJmpLabel .JMP "exec_voice"   -- tail call
    | none => pure ()
  return cb

mutual
def emitExecVoice (cb : CodeBuilder) (song : Song) : CodeBuilder := Id.run do
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

  -- 1. GATE-OFF CHECK (if dur==0: clear gate, zero ADSR, skip effects)
  cb := cb.emitLdaAbsX "v_dur"
  cb := cb.emitBranch .BNE "effects_start"
  -- Gate off
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay
  cb := cb.emitLdaAbsX "v_ctrl"
  cb := cb.emitInst (I.and_imm 0xFE)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 4))
  cb := cb.emitInst (I.lda_imm 0x00)
  cb := cb.emitInst (I.sta_absY (SID_BASE + 5))
  cb := cb.emitInst (I.sta_absY (SID_BASE + 6))
  cb := cb.emitInst I.rts                          -- skip effects on gate-off frame

  cb := cb.label "effects_start"

  -- 2. VIBRATO (in separate function to avoid Lean elaborator depth limit)
  cb := emitVibrato cb song

  -- 3+ continues below
  cb := emitSustainEffects cb song
  return cb

def emitVibrato (cb : CodeBuilder) (_song : Song) : CodeBuilder := Id.run do
  let mut cb := cb
  -- If vib_depth > 0: compute LFO, modulate freq, write freq_lo/freq_hi to SID
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay                          -- Y = instrument
  cb := cb.emitInst ⟨.LDA, .absY 0⟩               -- i_vib[inst] (vib_depth, 0=none)
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_vib" } :: cb.absFixups }
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
  -- Compute 16-bit delta: freq[pitch+1] - freq[pitch]
  cb := cb.emitInst I.sec
  cb := cb.emitLdaAbsY "freq_hi"                   -- next_fhi
  cb := cb.emitInst (I.sbc_zp 0xF9)               -- delta_hi = next_fhi - base_fhi
  cb := cb.emitInst (I.sta_zp 0xF5)               -- $F5 = delta_hi
  cb := cb.emitLdaAbsY "freq_lo"                   -- next_flo
  cb := cb.emitInst (I.sbc_zp 0xF8)               -- delta_lo = next_flo - base_flo
  -- Right-shift (vib_depth+1) times
  -- Loop: LSR delta_lo / ROR delta_hi, decrement depth counter
  cb := cb.label "vib_shift"
  cb := cb.emitInst I.lsr_a                        -- shift A (delta_lo) right
  cb := cb.emitInst ⟨.ROR, .zp 0xF5⟩              -- rotate into delta_hi
  cb := cb.emitInst (I.dec_zp 0xF7)               -- dec vib_depth counter
  cb := cb.emitBranch .BPL "vib_shift"             -- loop while >= 0

  cb := cb.emitInst (I.sta_zp 0xF4)               -- $F4 = shifted delta_lo
  -- $F5 = shifted delta_hi

  -- Start from base freq, add delta × LFO step
  -- vibrato_freq = base_freq + delta * step
  -- Check onset: dur_field >= 6 for vibrato to be active
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_durfield"
  cb := cb.emitInst (I.cmp_imm 6)
  cb := cb.emitBranch .BCS "vib_onset_ok"          -- dur >= 6: vibrato active
  -- dur < 6: write base freq directly
  cb := cb.emitJmpLabel .JMP "vib_write_base"
  cb := cb.label "vib_onset_ok"

  -- Load LFO step, DEY to check if 0
  cb := cb.emitInst (I.ldy_zp 0xF6)               -- Y = step
  cb := cb.emitInst I.dey                          -- Y--
  cb := cb.emitBranch .BMI "vib_write_base"        -- step was 0: no addition

  -- Add delta × step to base freq
  -- Start: target = base freq
  cb := cb.emitInst (I.lda_zp 0xF8)               -- base_flo
  cb := cb.emitInst (I.sta_zp 0xF2)               -- $F2 = target_lo
  cb := cb.emitInst (I.lda_zp 0xF9)               -- base_fhi
  cb := cb.emitInst (I.sta_zp 0xF3)               -- $F3 = target_hi
  cb := cb.emitInst I.iny                          -- restore Y (was DEY'd, now = step-1)

  cb := cb.label "vib_add_loop"
  cb := cb.emitInst I.clc
  cb := cb.emitInst (I.lda_zp 0xF2)
  cb := cb.emitInst (I.adc_zp 0xF5)               -- target_lo += delta_hi (Hubbard swaps lo/hi)
  cb := cb.emitInst (I.sta_zp 0xF2)
  cb := cb.emitInst (I.lda_zp 0xF3)
  cb := cb.emitInst (I.adc_zp 0xF4)               -- target_hi += delta_lo
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

def emitSustainEffects (cb : CodeBuilder) (song : Song) : CodeBuilder := Id.run do
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
  cb := cb.emitInst (I.cmp_imm 2)
  cb := cb.emitBranch .BEQ "pw_bidir"

  -- LINEAR PW
  cb := cb.emitInst I.clc
  cb := cb.emitLdaAbsX "v_pwlo"
  cb := cb.emitInst (I.adc_zp 0xF9)
  cb := cb.emitStaAbsX "v_pwlo"
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay
  cb := cb.emitLdaAbsX "v_pwlo"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 2))
  cb := cb.emitJmpLabel .JMP "pw_done"

  -- BIDIRECTIONAL PW
  cb := cb.label "pw_bidir"
  cb := cb.emitLdaAbsX "v_pwdir"
  cb := cb.emitBranch .BNE "pw_bidir_down"
  -- Up
  cb := cb.emitInst I.clc
  cb := cb.emitLdaAbsX "v_pwlo"
  cb := cb.emitInst (I.adc_zp 0xF9)
  cb := cb.emitStaAbsX "v_pwlo"
  cb := cb.emitLdaAbsX "v_pwhi"
  cb := cb.emitInst (I.adc_imm 0)
  cb := cb.emitInst (I.and_imm 0x0F)
  cb := cb.emitStaAbsX "v_pwhi"
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay
  cb := cb.emitLdaAbsX "v_pwhi"
  cb := cb.emitInst ⟨.CMP, .absY 0⟩
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_pwmax" } :: cb.absFixups }
  cb := cb.emitBranch .BNE "pw_bidir_write"
  cb := cb.emitInst (I.lda_imm 1)
  cb := cb.emitStaAbsX "v_pwdir"
  cb := cb.emitJmpLabel .JMP "pw_bidir_write"
  -- Down
  cb := cb.label "pw_bidir_down"
  cb := cb.emitInst I.sec
  cb := cb.emitLdaAbsX "v_pwlo"
  cb := cb.emitInst (I.sbc_zp 0xF9)
  cb := cb.emitStaAbsX "v_pwlo"
  cb := cb.emitLdaAbsX "v_pwhi"
  cb := cb.emitInst (I.sbc_imm 0)
  cb := cb.emitInst (I.and_imm 0x0F)
  cb := cb.emitStaAbsX "v_pwhi"
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay
  cb := cb.emitLdaAbsX "v_pwhi"
  cb := cb.emitInst ⟨.CMP, .absY 0⟩
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_pwmin" } :: cb.absFixups }
  cb := cb.emitBranch .BNE "pw_bidir_write"
  cb := cb.emitInst (I.lda_imm 0)
  cb := cb.emitStaAbsX "v_pwdir"
  -- Write PW to SID
  cb := cb.label "pw_bidir_write"
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay
  cb := cb.emitLdaAbsX "v_pwlo"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 2))
  cb := cb.emitLdaAbsX "v_pwhi"
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

  -- Guard: skip if countdown == 0
  cb := cb.emitLdaAbsX "v_dur"
  cb := cb.emitBranch .BNE "dur_ok"
  cb := cb.emitJmpLabel .JMP "no_slide"
  cb := cb.label "dur_ok"

  -- Check note age: dur_field - 1 vs countdown
  -- (Simple version — multiplying by tempo caused runaway DEC)
  cb := cb.emitInst I.sec
  cb := cb.emitLdaAbsX "v_durfield"
  cb := cb.emitInst (I.sbc_imm 1)                 -- A = dur_field - 1
  cb := cb.emitInst ⟨.CMP, .absX 0⟩               -- cmp countdown
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "v_dur" } :: cb.absFixups }

  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay                          -- Y = SID offset

  cb := cb.emitBranch .BCC "slide_path_b"          -- dur_field-1 < countdown → Path B

  -- PATH A: DEC freq_hi, write OLD, write ctrl (gate cleared)
  -- Step waveform program to get ctrl byte
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay
  cb := cb.emitLdaAbsX "v_wptr"
  cb := cb.emitInst I.clc
  cb := cb.emitInst ⟨.ADC, .absY 0⟩               -- wPtr + wave_base[inst]
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_wavebase" } :: cb.absFixups }
  cb := cb.emitInst I.tax
  cb := cb.emitLdaAbsX "wave_data"                 -- ctrl byte from waveform
  cb := cb.emitInst (I.sta_zp 0xFB)               -- save ctrl

  -- Advance wPtr
  cb := cb.emitInst (I.ldx_zp 0xFA)
  cb := cb.emitLdaAbsX "v_wptr"
  cb := cb.emitInst I.clc
  cb := cb.emitInst (I.adc_imm 1)
  cb := cb.emitInst I.pha
  cb := cb.emitLdaAbsX "v_inst"
  cb := cb.emitInst I.tay
  cb := cb.emitInst I.pla
  cb := cb.emitInst ⟨.CMP, .absY 0⟩               -- cmp wave_len[inst]
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_wavelen" } :: cb.absFixups }
  cb := cb.emitBranch .BCC "wptr_ok_a"
  cb := cb.emitInst ⟨.LDA, .absY 0⟩               -- wave_loop[inst]
  cb := { cb with absFixups :=
    { byteIdx := cb.bytes.size - 2, targetLabel := "i_waveloop" } :: cb.absFixups }
  cb := cb.label "wptr_ok_a"
  cb := cb.emitStaAbsX "v_wptr"

  -- Store ctrl
  cb := cb.emitInst (I.lda_zp 0xFB)
  cb := cb.emitStaAbsX "v_ctrl"

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

def emitNoteLoadPath (cb : CodeBuilder) (song : Song) : CodeBuilder := Id.run do
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
  cb := cb.emitInst (I.sta_zp 0xFB)              -- $FB = instrument

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

  -- Save raw duration field for freq slide guard
  cb := cb.emitInst (I.lda_zp 0xFF)
  cb := cb.emitStaAbsX "v_durfield"

  -- Compute duration counter: dur * tickLength
  cb := cb.emitInst (I.lda_zp 0xFF)
  if song.tickLength == 1 then
    pure ()
  else if song.tickLength == 3 then
    cb := cb.emitInst (I.sta_zp 0xFF)
    cb := cb.emitInst I.asl_a
    cb := cb.emitInst I.clc
    cb := cb.emitInst (I.adc_zp 0xFF)
  else
    cb := cb.emitInst (I.sta_zp 0xFF)
    for _ in [:song.tickLength - 1] do
      cb := cb.emitInst I.clc
      cb := cb.emitInst (I.adc_zp 0xFF)
  cb := cb.emitStaAbsX "v_dur"

  -- Store instrument index in voice state
  cb := cb.emitInst (I.lda_zp 0xFB)
  cb := cb.emitStaAbsX "v_inst"

  -- Reset waveform pointer to 0
  -- First sustain frame will re-read waveform[0] (same as noteLoad ctrl)
  -- then advance to 1. This costs 1 frame delay but is simple and safe.
  cb := cb.emitInst (I.lda_imm 0)
  cb := cb.emitStaAbsX "v_wptr"

  -- Write SID registers: freq, ctrl, pw, adsr
  cb := cb.emitLdaAbsX "v_sidoff"
  cb := cb.emitInst I.tay                        -- Y = SID offset

  -- Frequency
  cb := cb.emitInst (I.ldx_zp 0xFE)              -- X = pitch
  cb := cb.emitLdaAbsX "freq_lo"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 0))
  cb := cb.emitLdaAbsX "freq_hi"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 1))

  -- Save pitch and freq_hi for effects
  cb := cb.emitInst (I.ldx_zp 0xFA)               -- X = voice
  cb := cb.emitInst (I.lda_zp 0xFE)               -- pitch
  cb := cb.emitStaAbsX "v_pitch"
  -- Reload freq_hi for v_fhi (need pitch in X again)
  cb := cb.emitInst (I.ldx_zp 0xFE)               -- X = pitch
  cb := cb.emitLdaAbsX "freq_hi"
  cb := cb.emitInst (I.ldx_zp 0xFA)               -- X = voice
  cb := cb.emitStaAbsX "v_fhi"

  -- Instrument lookups: X = instrument
  cb := cb.emitInst (I.ldx_zp 0xFB)              -- X = instrument

  -- Ctrl
  cb := cb.emitLdaAbsX "i_ctrl"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 4))
  -- Save ctrl for sustain path
  cb := cb.emitInst I.pha

  -- PW: write to SID and save to voice state
  cb := cb.emitLdaAbsX "i_pwlo"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 2))
  cb := cb.emitInst I.pha                          -- save pwlo
  cb := cb.emitLdaAbsX "i_pwhi"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 3))
  cb := cb.emitInst I.pha                          -- save pwhi
  -- Save to voice state (need voice index)
  cb := cb.emitInst (I.ldx_zp 0xFA)               -- X = voice
  cb := cb.emitInst I.pla                          -- pwhi
  cb := cb.emitStaAbsX "v_pwhi"
  cb := cb.emitInst I.pla                          -- pwlo
  cb := cb.emitStaAbsX "v_pwlo"
  -- Reset PW direction to 0 (up)
  cb := cb.emitInst (I.lda_imm 0)
  cb := cb.emitStaAbsX "v_pwdir"
  -- Restore X = instrument for ADSR lookups
  cb := cb.emitInst (I.ldx_zp 0xFB)

  -- ADSR
  cb := cb.emitLdaAbsX "i_ad"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 5))
  cb := cb.emitLdaAbsX "i_sr"
  cb := cb.emitInst (I.sta_absY (SID_BASE + 6))

  -- Store ctrl in voice state for sustain path
  cb := cb.emitInst I.pla                         -- ctrl from stack
  cb := cb.emitInst (I.ldx_zp 0xFA)              -- X = voice index
  cb := cb.emitStaAbsX "v_ctrl"

  cb := cb.emitInst I.rts

  -- === ADVANCE ORDERLIST ===
  cb := cb.label "advance_order"
  cb := cb.emitInst (I.ldx_zp 0xFA)              -- X = voice index

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
  cb := cb.emitBranch .BEQ "song_end"             -- $FF = end of orderlist

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

def generateSID (song : Song) (debug : Bool := false) : Bytes := Id.run do
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
  cb := cb.label "freq_lo"
  for hi : i in [:song.freqTable.entries.length] do
    match song.freqTable.entries[i]? with
    | some p => cb := cb.emitByte (if i == 104 then 0 else p.1.val.toUInt8)
    | none => cb := cb.emitByte 0
  cb := cb.label "freq_hi"
  for hi : i in [:song.freqTable.entries.length] do
    match song.freqTable.entries[i]? with
    | some p => cb := cb.emitByte (if i == 104 then 0 else p.2.val.toUInt8)
    | none => cb := cb.emitByte 0

  -- Waveform data: all instruments' waveform steps concatenated
  let mut waveData : List UInt8 := []
  let mut waveBases : List UInt8 := []
  let mut waveLens : List UInt8 := []
  let mut waveLoops : List UInt8 := []
  for inst in song.instruments do
    waveBases := waveBases ++ [waveData.length.toUInt8]
    waveLens := waveLens ++ [inst.waveform.length.toUInt8]
    waveLoops := waveLoops ++ [inst.waveLoop.toUInt8]
    waveData := waveData ++ inst.waveform.map (·.val.toUInt8)

  cb := cb.label "wave_data"
  cb := cb.emitData waveData
  cb := cb.label "i_wavebase"
  cb := cb.emitData waveBases
  cb := cb.label "i_wavelen"
  cb := cb.emitData waveLens
  cb := cb.label "i_waveloop"
  cb := cb.emitData waveLoops

  -- Instrument tables
  cb := cb.label "i_ctrl"
  cb := cb.emitData (song.instruments.map fun i =>
    (i.waveform.head?.getD ⟨0, by omega⟩).val.toUInt8)
  cb := cb.label "i_pwlo"
  cb := cb.emitData (song.instruments.map fun i => i.pw.initLo.val.toUInt8)
  cb := cb.label "i_pwhi"
  cb := cb.emitData (song.instruments.map fun i => i.pw.initHi.val.toUInt8)
  cb := cb.label "i_ad"
  cb := cb.emitData (song.instruments.map fun i => i.ad.val.toUInt8)
  cb := cb.label "i_sr"
  cb := cb.emitData (song.instruments.map fun i => i.sr.val.toUInt8)
  cb := cb.label "i_pwspeed"
  cb := cb.emitData (song.instruments.map fun i => i.pw.speed.val.toUInt8)
  cb := cb.label "i_pwmode"
  cb := cb.emitData (song.instruments.map fun i => match i.pw.mode with
    | .linear => if i.pw.speed.val == 0 then (0 : UInt8) else 1
    | .bidirectional => 2
    | .table => 0)
  cb := cb.label "i_pwmin"
  cb := cb.emitData (song.instruments.map fun i => i.pw.minHi.val.toUInt8)
  cb := cb.label "i_pwmax"
  cb := cb.emitData (song.instruments.map fun i => i.pw.maxHi.val.toUInt8)
  -- Vibrato depth (0 = none, 1-3 = depth shift)
  cb := cb.label "i_vib"
  cb := cb.emitData (song.instruments.map fun i =>
    match i.effectChain.vibrato with
    | some spec => spec.depthShift.toUInt8
    | none => 0)

  -- Arpeggio offset (0 = none, 12 = octave, etc.)
  cb := cb.label "i_arp"
  cb := cb.emitData (song.instruments.map fun i =>
    match i.effectChain.arpeggio with
    | some spec => match spec.intervals[1]? with
      | some v => v.toNat.toUInt8
      | none => 0
    | none => 0)
  -- Freq slide flag (0 = none, 1 = active)
  cb := cb.label "i_bit0"
  cb := cb.emitData (song.instruments.map fun i =>
    match i.effectChain.freqSlide with
    | some _ => (1 : UInt8)
    | none => 0)

  -- Pattern data: [pitch, duration, instrument]* per pattern, 0x00 = end
  let mut patPtrLo : List UInt8 := []
  let mut patPtrHi : List UInt8 := []
  for pat in song.patterns do
    let addr := cb.currentAddr
    patPtrLo := patPtrLo ++ [addr.toUInt8]
    patPtrHi := patPtrHi ++ [(addr >>> 8).toUInt8]
    for note in pat.notes do
      cb := cb.emitByte note.pitch.val.toUInt8
      cb := cb.emitByte note.duration.val.toUInt8
      cb := cb.emitByte note.instrument.toUInt8
    cb := cb.emitByte 0x00

  cb := cb.label "patt_ptr_lo"
  cb := cb.emitData patPtrLo
  cb := cb.label "patt_ptr_hi"
  cb := cb.emitData patPtrHi

  -- Orderlist data per voice + build pointer tables
  let mut olLo : List UInt8 := []
  let mut olHi : List UInt8 := []
  for vi in [:song.voices.length] do
    match song.voices[vi]? with
    | some voiceSpec =>
      let addr := cb.currentAddr
      olLo := olLo ++ [addr.toUInt8]
      olHi := olHi ++ [(addr >>> 8).toUInt8]
      cb := cb.emitData (voiceSpec.orderlist.map (·.toUInt8))
      cb := cb.emitByte 0xFF   -- end marker
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
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_wptr"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_inst"
  cb := cb.emitData [0, 0, 0]
  cb := cb.label "v_pitch"
  cb := cb.emitData [0, 0, 0]
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

def sidgenMain : IO Unit := do
  let sid := generateSID commandoSong
  writeFile "commando_lean.sid" sid
  IO.println s!"Generated commando_lean.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {commandoSong.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {commandoSong.instruments.length}"
  IO.println s!"  Patterns: {commandoSong.patterns.length}"
  IO.println s!"  Voices: {commandoSong.voices.length}"
