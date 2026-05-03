/-
  CPU6502.lean — Formal model of the MOS 6502 CPU.

  This is a cycle-accurate (instruction-level) model of the 6502 processor.
  Each `step` executes one instruction and returns the new CPU state plus
  any SID register writes that occurred (stores to $D400-$D41C).

  The model covers the subset of 6502 needed for SID player verification:
  all official opcodes, all addressing modes. Unofficial opcodes are not modeled.

  Key design decisions:
  - Memory is a flat 64KB array (UInt8 → UInt8 function for efficiency)
  - SID writes are captured as a side-channel (List SIDWrite)
  - The model is pure — no IO, no mutable state
  - Flags are individual Bools for easy reasoning
-/

import SID

-- ==========================================================================
-- CPU State
-- ==========================================================================

structure Flags where
  carry    : Bool := false    -- C
  zero     : Bool := true     -- Z
  irqDis   : Bool := true     -- I
  decimal  : Bool := false    -- D
  overflow : Bool := false    -- V
  negative : Bool := false    -- N
  deriving Repr, BEq

structure CPU where
  a    : UInt8 := 0
  x    : UInt8 := 0
  y    : UInt8 := 0
  sp   : UInt8 := 0xFD
  pc   : UInt16 := 0
  flags : Flags := {}
  mem  : ByteArray           -- 64KB
  cycles : Nat := 0          -- total cycle count

-- A SID write with its cycle timestamp
structure TimedSIDWrite where
  cycle : Nat
  write : SIDWrite

-- Result of executing one instruction
structure StepResult where
  cpu      : CPU
  sidWrites : List TimedSIDWrite  -- writes to $D400-$D41C with cycle stamps
  halted   : Bool := false

-- ==========================================================================
-- Memory access
-- ==========================================================================

def CPU.read (cpu : CPU) (addr : UInt16) : UInt8 :=
  cpu.mem.get! addr.toNat

def CPU.read16 (cpu : CPU) (addr : UInt16) : UInt16 :=
  let lo := cpu.read addr
  let hi := cpu.read (addr + 1)
  lo.toUInt16 ||| (hi.toUInt16 <<< 8)

-- Read 16-bit from zero page (wraps at $FF)
def CPU.readZP16 (cpu : CPU) (addr : UInt8) : UInt16 :=
  let lo := cpu.read addr.toUInt16
  let hi := cpu.read ((addr + 1) &&& 0xFF).toUInt16  -- wrap in ZP
  lo.toUInt16 ||| (hi.toUInt16 <<< 8)

-- Write to memory, capturing SID writes with cycle timestamp
def CPU.write (cpu : CPU) (addr : UInt16) (val : UInt8) : CPU × List TimedSIDWrite :=
  let newMem := cpu.mem.set! addr.toNat val
  let cpu' := { cpu with mem := newMem }
  -- Capture writes to SID range $D400-$D41C
  if addr >= 0xD400 && addr <= 0xD41C then
    let sidOff := (addr - 0xD400).toNat
    let reg : SIDReg := match sidOff with
      | 0  => .freqLo ⟨0, by omega⟩  | 1  => .freqHi ⟨0, by omega⟩
      | 2  => .pwLo ⟨0, by omega⟩    | 3  => .pwHi ⟨0, by omega⟩
      | 4  => .ctrl ⟨0, by omega⟩    | 5  => .ad ⟨0, by omega⟩
      | 6  => .sr ⟨0, by omega⟩
      | 7  => .freqLo ⟨1, by omega⟩  | 8  => .freqHi ⟨1, by omega⟩
      | 9  => .pwLo ⟨1, by omega⟩    | 10 => .pwHi ⟨1, by omega⟩
      | 11 => .ctrl ⟨1, by omega⟩    | 12 => .ad ⟨1, by omega⟩
      | 13 => .sr ⟨1, by omega⟩
      | 14 => .freqLo ⟨2, by omega⟩  | 15 => .freqHi ⟨2, by omega⟩
      | 16 => .pwLo ⟨2, by omega⟩    | 17 => .pwHi ⟨2, by omega⟩
      | 18 => .ctrl ⟨2, by omega⟩    | 19 => .ad ⟨2, by omega⟩
      | 20 => .sr ⟨2, by omega⟩
      | 21 => .filtLo              | 22 => .filtHi
      | 23 => .filtCtrl            | 24 => .modeVol
      | _  => .modeVol  -- shouldn't happen
    let w : SIDWrite := { reg := reg, val := ⟨val.toNat % 256, by omega⟩ }
    (cpu', [{ cycle := cpu.cycles, write := w }])
  else
    (cpu', [])

-- ==========================================================================
-- Flag helpers
-- ==========================================================================

def updateNZ (flags : Flags) (val : UInt8) : Flags :=
  { flags with zero := val == 0, negative := val &&& 0x80 != 0 }

-- ==========================================================================
-- Addressing mode resolution
-- ==========================================================================

-- Resolved operand: either a value or an address (for read-modify-write)
inductive Operand where
  | value : UInt8 → Operand
  | addr  : UInt16 → Operand

-- Fetch operand based on addressing mode encoded in the opcode
-- Returns (operand, new PC, bytes consumed)
def CPU.fetchOperand (cpu : CPU) (mode : Nat) : UInt8 × UInt16 :=
  let pc1 := cpu.pc + 1
  match mode with
  | 0 => -- Immediate
    (cpu.read pc1, cpu.pc + 2)
  | 1 => -- Zero page
    let zp := cpu.read pc1
    (cpu.read zp.toUInt16, cpu.pc + 2)
  | 2 => -- Zero page, X
    let zp := (cpu.read pc1) + cpu.x
    (cpu.read (zp &&& 0xFF).toUInt16, cpu.pc + 2)
  | 3 => -- Zero page, Y
    let zp := (cpu.read pc1) + cpu.y
    (cpu.read (zp &&& 0xFF).toUInt16, cpu.pc + 2)
  | 4 => -- Absolute
    let addr := cpu.read16 pc1
    (cpu.read addr, cpu.pc + 3)
  | 5 => -- Absolute, X
    let addr := cpu.read16 pc1 + cpu.x.toUInt16
    (cpu.read addr, cpu.pc + 3)
  | 6 => -- Absolute, Y
    let addr := cpu.read16 pc1 + cpu.y.toUInt16
    (cpu.read addr, cpu.pc + 3)
  | 7 => -- (Indirect, X)
    let zp := (cpu.read pc1) + cpu.x
    let addr := cpu.readZP16 zp
    (cpu.read addr, cpu.pc + 2)
  | 8 => -- (Indirect), Y
    let zp := cpu.read pc1
    let base := cpu.readZP16 zp
    let addr := base + cpu.y.toUInt16
    (cpu.read addr, cpu.pc + 2)
  | _ => (0, cpu.pc + 1)  -- implied/accumulator

-- Fetch the effective address (for STA, DEC, INC, etc.)
def CPU.fetchAddr (cpu : CPU) (mode : Nat) : UInt16 × UInt16 :=
  let pc1 := cpu.pc + 1
  match mode with
  | 1 => -- Zero page
    ((cpu.read pc1).toUInt16, cpu.pc + 2)
  | 2 => -- Zero page, X
    (((cpu.read pc1) + cpu.x).toUInt16 &&& 0xFF, cpu.pc + 2)
  | 3 => -- Zero page, Y
    (((cpu.read pc1) + cpu.y).toUInt16 &&& 0xFF, cpu.pc + 2)
  | 4 => -- Absolute
    (cpu.read16 pc1, cpu.pc + 3)
  | 5 => -- Absolute, X
    (cpu.read16 pc1 + cpu.x.toUInt16, cpu.pc + 3)
  | 6 => -- Absolute, Y
    (cpu.read16 pc1 + cpu.y.toUInt16, cpu.pc + 3)
  | 8 => -- (Indirect), Y
    let zp := cpu.read pc1
    let base := cpu.readZP16 zp
    (base + cpu.y.toUInt16, cpu.pc + 2)
  | _ => (0, cpu.pc + 1)

-- ==========================================================================
-- Stack operations
-- ==========================================================================

def CPU.push (cpu : CPU) (val : UInt8) : CPU :=
  let addr := 0x0100 + cpu.sp.toUInt16
  let mem := cpu.mem.set! addr.toNat val
  { cpu with sp := cpu.sp - 1, mem := mem }

def CPU.pull (cpu : CPU) : CPU × UInt8 :=
  let sp' := cpu.sp + 1
  let val := cpu.mem.get! (0x0100 + sp'.toNat)
  ({ cpu with sp := sp' }, val)

def CPU.push16 (cpu : CPU) (val : UInt16) : CPU :=
  let cpu := cpu.push (val >>> 8).toUInt8  -- push high byte first
  cpu.push val.toUInt8

def CPU.pull16 (cpu : CPU) : CPU × UInt16 :=
  let (cpu, lo) := cpu.pull
  let (cpu, hi) := cpu.pull
  (cpu, lo.toUInt16 ||| (hi.toUInt16 <<< 8))

-- ==========================================================================
-- Instruction execution
-- ==========================================================================

-- Addressing mode encoding used in the opcode decode table:
-- 0=imm, 1=zp, 2=zpX, 3=zpY, 4=abs, 5=absX, 6=absY, 7=indX, 8=indY, 9=impl, 10=acc, 11=rel

-- Helper: execute a branch instruction
private def doBranch (cpu : CPU) (taken : Bool) : StepResult :=
  let offset := cpu.read (cpu.pc + 1)
  let pc' := cpu.pc + 2
  if taken then
    let target := if offset &&& 0x80 != 0 then pc' - (256 - offset.toUInt16) else pc' + offset.toUInt16
    ⟨{ cpu with pc := target }, [], false⟩
  else ⟨{ cpu with pc := pc' }, [], false⟩

-- Helper: load register, set NZ flags
private def doLoad (cpu : CPU) (mode : Nat) (reg : String) : StepResult :=
  let (v, pc) := cpu.fetchOperand mode
  match reg with
  | "a" => ⟨{ cpu with a := v, pc := pc, flags := updateNZ cpu.flags v }, [], false⟩
  | "x" => ⟨{ cpu with x := v, pc := pc, flags := updateNZ cpu.flags v }, [], false⟩
  | "y" => ⟨{ cpu with y := v, pc := pc, flags := updateNZ cpu.flags v }, [], false⟩
  | _ => ⟨cpu, [], true⟩

-- Helper: store register
private def doStore (cpu : CPU) (mode : Nat) (val : UInt8) : StepResult :=
  let (addr, pc) := cpu.fetchAddr mode
  let (cpu', ws) := cpu.write addr val
  ⟨{ cpu' with pc := pc }, ws, false⟩

-- Helper: ALU operation (AND/ORA/EOR on accumulator)
private def doALU (cpu : CPU) (mode : Nat) (op : UInt8 → UInt8 → UInt8) : StepResult :=
  let (v, pc) := cpu.fetchOperand mode
  let r := op cpu.a v
  ⟨{ cpu with a := r, pc := pc, flags := updateNZ cpu.flags r }, [], false⟩

-- Helper: compare register with memory
private def doCMP (cpu : CPU) (mode : Nat) (reg : UInt8) : StepResult :=
  let (v, pc) := cpu.fetchOperand mode
  let diff := (reg.toNat + 256 - v.toNat) % 256
  ⟨{ cpu with pc := pc, flags := { (updateNZ cpu.flags diff.toUInt8) with carry := reg >= v } }, [], false⟩

-- Helper: shift/rotate on memory
private def doShiftMem (cpu : CPU) (mode : Nat)
    (op : UInt8 → Bool → UInt8 × Bool) : StepResult :=
  let (addr, pc) := cpu.fetchAddr mode
  let v := cpu.read addr
  let (result, carry) := op v cpu.flags.carry
  let (cpu', ws) := cpu.write addr result
  ⟨{ cpu' with pc := pc, flags := { (updateNZ cpu.flags result) with carry := carry } }, ws, false⟩

-- Shift operations
private def aslOp (v : UInt8) (_carry : Bool) : UInt8 × Bool := (v <<< 1, v &&& 0x80 != 0)
private def lsrOp (v : UInt8) (_carry : Bool) : UInt8 × Bool := (v >>> 1, v &&& 0x01 != 0)
private def rolOp (v : UInt8) (carry : Bool) : UInt8 × Bool :=
  let c : UInt8 := if carry then 1 else 0
  ((v <<< 1) ||| c, v &&& 0x80 != 0)
private def rorOp (v : UInt8) (carry : Bool) : UInt8 × Bool :=
  let c : UInt8 := if carry then 0x80 else 0
  ((v >>> 1) ||| c, v &&& 0x01 != 0)

-- Flags register to/from byte
private def flagsToByte (f : Flags) : UInt8 :=
  (if f.carry then 0x01 else 0) ||| (if f.zero then 0x02 else 0) |||
  (if f.irqDis then 0x04 else 0) ||| (if f.decimal then 0x08 else 0) |||
  0x30 |||  -- bits 4,5 always set when pushed
  (if f.overflow then 0x40 else 0) ||| (if f.negative then 0x80 else 0)

private def byteToFlags (b : UInt8) : Flags :=
  { carry := b &&& 0x01 != 0, zero := b &&& 0x02 != 0, irqDis := b &&& 0x04 != 0,
    decimal := b &&& 0x08 != 0, overflow := b &&& 0x40 != 0, negative := b &&& 0x80 != 0 }

-- Base cycle count per opcode (not counting page-crossing penalties)
def opcodeCycles (op : UInt8) : Nat :=
  match op.toNat with
  -- Immediate: 2 cycles
  | 0xA9 | 0xA2 | 0xA0 | 0x69 | 0xE9 | 0x29 | 0x09 | 0x49 | 0xC9 | 0xE0 | 0xC0 => 2
  -- Zero page: 3 cycles (load) or 3 (store)
  | 0xA5 | 0xA6 | 0xA4 | 0x65 | 0xE5 | 0x25 | 0x05 | 0x45 | 0xC5 | 0xE4 | 0xC4 | 0x24 => 3
  | 0x85 | 0x86 | 0x84 => 3
  -- Zero page,X/Y: 4 cycles
  | 0xB5 | 0xB4 | 0xB6 | 0x75 | 0xF5 | 0x35 | 0x15 | 0x55 | 0xD5 => 4
  | 0x95 | 0x94 | 0x96 => 4
  -- Absolute: 4 cycles (load/store)
  | 0xAD | 0xAE | 0xAC | 0x6D | 0xED | 0x2D | 0x0D | 0x4D | 0xCD | 0xEC | 0xCC | 0x2C => 4
  | 0x8D | 0x8E | 0x8C => 4
  -- Absolute,X/Y: 4+ cycles
  | 0xBD | 0xBC | 0xBE | 0x7D | 0xFD | 0x3D | 0x1D | 0x5D | 0xDD => 4
  | 0xB9 | 0x79 | 0xF9 | 0x39 | 0x19 | 0x59 | 0xD9 => 4
  | 0x9D | 0x99 => 5
  -- (Indirect,X): 6 cycles
  | 0xA1 | 0x61 | 0xE1 | 0x21 | 0x01 | 0x41 | 0xC1 => 6
  | 0x81 => 6
  -- (Indirect),Y: 5+ cycles
  | 0xB1 | 0x71 | 0xF1 | 0x31 | 0x11 | 0x51 | 0xD1 => 5
  | 0x91 => 6
  -- INC/DEC memory
  | 0xE6 | 0xC6 => 5  -- zp
  | 0xF6 | 0xD6 => 6  -- zp,X
  | 0xEE | 0xCE => 6  -- abs
  | 0xFE | 0xDE => 7  -- abs,X
  -- Implied (1 byte)
  | 0xE8 | 0xCA | 0xC8 | 0x88 => 2  -- INX/DEX/INY/DEY
  | 0xAA | 0xA8 | 0x8A | 0x98 | 0xBA | 0x9A => 2  -- transfers
  | 0x18 | 0x38 | 0x58 | 0x78 | 0xB8 | 0xD8 | 0xF8 => 2  -- flag ops
  | 0xEA => 2  -- NOP
  -- Shift/rotate accumulator
  | 0x0A | 0x4A | 0x2A | 0x6A => 2
  -- Shift/rotate memory
  | 0x06 | 0x46 | 0x26 | 0x66 => 5  -- zp
  | 0x16 | 0x56 | 0x36 | 0x76 => 6  -- zp,X
  | 0x0E | 0x4E | 0x2E | 0x6E => 6  -- abs
  | 0x1E | 0x5E | 0x3E | 0x7E => 7  -- abs,X
  -- Branch: 2 (not taken), 3 (taken), 4 (taken + page cross)
  | 0x90 | 0xB0 | 0xF0 | 0xD0 | 0x30 | 0x10 | 0x50 | 0x70 => 2
  -- JMP
  | 0x4C => 3  -- abs
  | 0x6C => 5  -- indirect
  -- JSR/RTS/RTI
  | 0x20 => 6
  | 0x60 => 6
  | 0x40 => 6
  -- Stack
  | 0x48 | 0x08 => 3  -- PHA/PHP
  | 0x68 | 0x28 => 4  -- PLA/PLP
  -- BRK
  | 0x00 => 7
  | _ => 2

def stepRaw (cpu : CPU) : StepResult :=
  let opcode := cpu.read cpu.pc
  match opcode.toNat with

  -- === LOADS ===
  | 0xA9 => doLoad cpu 0 "a"  | 0xA5 => doLoad cpu 1 "a"  | 0xB5 => doLoad cpu 2 "a"
  | 0xAD => doLoad cpu 4 "a"  | 0xBD => doLoad cpu 5 "a"  | 0xB9 => doLoad cpu 6 "a"
  | 0xA1 => doLoad cpu 7 "a"  | 0xB1 => doLoad cpu 8 "a"
  | 0xA2 => doLoad cpu 0 "x"  | 0xA6 => doLoad cpu 1 "x"  | 0xB6 => doLoad cpu 3 "x"
  | 0xAE => doLoad cpu 4 "x"  | 0xBE => doLoad cpu 6 "x"
  | 0xA0 => doLoad cpu 0 "y"  | 0xA4 => doLoad cpu 1 "y"  | 0xB4 => doLoad cpu 2 "y"
  | 0xAC => doLoad cpu 4 "y"  | 0xBC => doLoad cpu 5 "y"

  -- === STORES ===
  | 0x85 => doStore cpu 1 cpu.a  | 0x95 => doStore cpu 2 cpu.a  | 0x8D => doStore cpu 4 cpu.a
  | 0x9D => doStore cpu 5 cpu.a  | 0x99 => doStore cpu 6 cpu.a  | 0x81 => doStore cpu 7 cpu.a
  | 0x91 => doStore cpu 8 cpu.a
  | 0x86 => doStore cpu 1 cpu.x  | 0x96 => doStore cpu 3 cpu.x  | 0x8E => doStore cpu 4 cpu.x
  | 0x84 => doStore cpu 1 cpu.y  | 0x94 => doStore cpu 2 cpu.y  | 0x8C => doStore cpu 4 cpu.y

  -- === ADC ===
  | 0x69 | 0x65 | 0x75 | 0x6D | 0x7D | 0x79 | 0x61 | 0x71 =>
    let mode := match opcode.toNat with
      | 0x69 => 0 | 0x65 => 1 | 0x75 => 2 | 0x6D => 4 | 0x7D => 5 | 0x79 => 6 | 0x61 => 7 | 0x71 => 8 | _ => 0
    let (v, pc) := cpu.fetchOperand mode
    let sum := cpu.a.toNat + v.toNat + (if cpu.flags.carry then 1 else 0)
    let result := (sum % 256).toUInt8
    ⟨{ cpu with a := result, pc := pc, flags := { (updateNZ cpu.flags result) with
        carry := sum > 255,
        overflow := ((cpu.a ^^^ result) &&& (v ^^^ result) &&& 0x80) != 0 } }, [], false⟩

  -- === SBC ===
  | 0xE9 | 0xE5 | 0xF5 | 0xED | 0xFD | 0xF9 | 0xE1 | 0xF1 =>
    let mode := match opcode.toNat with
      | 0xE9 => 0 | 0xE5 => 1 | 0xF5 => 2 | 0xED => 4 | 0xFD => 5 | 0xF9 => 6 | 0xE1 => 7 | 0xF1 => 8 | _ => 0
    let (v, pc) := cpu.fetchOperand mode
    let diff := cpu.a.toNat + 256 - v.toNat - (if cpu.flags.carry then 0 else 1)
    let result := (diff % 256).toUInt8
    ⟨{ cpu with a := result, pc := pc, flags := { (updateNZ cpu.flags result) with
        carry := diff >= 256,
        overflow := ((cpu.a ^^^ result) &&& ((255 - v) ^^^ result) &&& 0x80) != 0 } }, [], false⟩

  -- === AND ===
  | 0x29 => doALU cpu 0 (· &&& ·)  | 0x25 => doALU cpu 1 (· &&& ·)  | 0x35 => doALU cpu 2 (· &&& ·)
  | 0x2D => doALU cpu 4 (· &&& ·)  | 0x3D => doALU cpu 5 (· &&& ·)  | 0x39 => doALU cpu 6 (· &&& ·)
  | 0x21 => doALU cpu 7 (· &&& ·)  | 0x31 => doALU cpu 8 (· &&& ·)

  -- === ORA ===
  | 0x09 => doALU cpu 0 (· ||| ·)  | 0x05 => doALU cpu 1 (· ||| ·)  | 0x15 => doALU cpu 2 (· ||| ·)
  | 0x0D => doALU cpu 4 (· ||| ·)  | 0x1D => doALU cpu 5 (· ||| ·)  | 0x19 => doALU cpu 6 (· ||| ·)
  | 0x01 => doALU cpu 7 (· ||| ·)  | 0x11 => doALU cpu 8 (· ||| ·)

  -- === EOR ===
  | 0x49 => doALU cpu 0 (· ^^^ ·)  | 0x45 => doALU cpu 1 (· ^^^ ·)  | 0x55 => doALU cpu 2 (· ^^^ ·)
  | 0x4D => doALU cpu 4 (· ^^^ ·)  | 0x5D => doALU cpu 5 (· ^^^ ·)  | 0x59 => doALU cpu 6 (· ^^^ ·)
  | 0x41 => doALU cpu 7 (· ^^^ ·)  | 0x51 => doALU cpu 8 (· ^^^ ·)

  -- === CMP ===
  | 0xC9 => doCMP cpu 0 cpu.a  | 0xC5 => doCMP cpu 1 cpu.a  | 0xD5 => doCMP cpu 2 cpu.a
  | 0xCD => doCMP cpu 4 cpu.a  | 0xDD => doCMP cpu 5 cpu.a  | 0xD9 => doCMP cpu 6 cpu.a
  | 0xC1 => doCMP cpu 7 cpu.a  | 0xD1 => doCMP cpu 8 cpu.a
  -- === CPX ===
  | 0xE0 => doCMP cpu 0 cpu.x  | 0xE4 => doCMP cpu 1 cpu.x  | 0xEC => doCMP cpu 4 cpu.x
  -- === CPY ===
  | 0xC0 => doCMP cpu 0 cpu.y  | 0xC4 => doCMP cpu 1 cpu.y  | 0xCC => doCMP cpu 4 cpu.y

  -- === INC memory ===
  | 0xE6 | 0xF6 | 0xEE | 0xFE =>
    let mode := match opcode.toNat with | 0xE6 => 1 | 0xF6 => 2 | 0xEE => 4 | 0xFE => 5 | _ => 1
    let (addr, pc) := cpu.fetchAddr mode
    let result := cpu.read addr + 1
    let (cpu', ws) := cpu.write addr result
    ⟨{ cpu' with pc := pc, flags := updateNZ cpu.flags result }, ws, false⟩

  -- === DEC memory ===
  | 0xC6 | 0xD6 | 0xCE | 0xDE =>
    let mode := match opcode.toNat with | 0xC6 => 1 | 0xD6 => 2 | 0xCE => 4 | 0xDE => 5 | _ => 1
    let (addr, pc) := cpu.fetchAddr mode
    let result := cpu.read addr - 1
    let (cpu', ws) := cpu.write addr result
    ⟨{ cpu' with pc := pc, flags := updateNZ cpu.flags result }, ws, false⟩

  -- === INX/DEX/INY/DEY ===
  | 0xE8 => let r := cpu.x + 1; ⟨{ cpu with x := r, pc := cpu.pc + 1, flags := updateNZ cpu.flags r }, [], false⟩
  | 0xCA => let r := cpu.x - 1; ⟨{ cpu with x := r, pc := cpu.pc + 1, flags := updateNZ cpu.flags r }, [], false⟩
  | 0xC8 => let r := cpu.y + 1; ⟨{ cpu with y := r, pc := cpu.pc + 1, flags := updateNZ cpu.flags r }, [], false⟩
  | 0x88 => let r := cpu.y - 1; ⟨{ cpu with y := r, pc := cpu.pc + 1, flags := updateNZ cpu.flags r }, [], false⟩

  -- === ASL ===
  | 0x0A => let (r, c) := aslOp cpu.a cpu.flags.carry
            ⟨{ cpu with a := r, pc := cpu.pc + 1, flags := { (updateNZ cpu.flags r) with carry := c } }, [], false⟩
  | 0x06 => doShiftMem cpu 1 aslOp  | 0x16 => doShiftMem cpu 2 aslOp
  | 0x0E => doShiftMem cpu 4 aslOp  | 0x1E => doShiftMem cpu 5 aslOp

  -- === LSR ===
  | 0x4A => let (r, c) := lsrOp cpu.a cpu.flags.carry
            ⟨{ cpu with a := r, pc := cpu.pc + 1, flags := { (updateNZ cpu.flags r) with carry := c } }, [], false⟩
  | 0x46 => doShiftMem cpu 1 lsrOp  | 0x56 => doShiftMem cpu 2 lsrOp
  | 0x4E => doShiftMem cpu 4 lsrOp  | 0x5E => doShiftMem cpu 5 lsrOp

  -- === ROL ===
  | 0x2A => let (r, c) := rolOp cpu.a cpu.flags.carry
            ⟨{ cpu with a := r, pc := cpu.pc + 1, flags := { (updateNZ cpu.flags r) with carry := c } }, [], false⟩
  | 0x26 => doShiftMem cpu 1 rolOp  | 0x36 => doShiftMem cpu 2 rolOp
  | 0x2E => doShiftMem cpu 4 rolOp  | 0x3E => doShiftMem cpu 5 rolOp

  -- === ROR ===
  | 0x6A => let (r, c) := rorOp cpu.a cpu.flags.carry
            ⟨{ cpu with a := r, pc := cpu.pc + 1, flags := { (updateNZ cpu.flags r) with carry := c } }, [], false⟩
  | 0x66 => doShiftMem cpu 1 rorOp  | 0x76 => doShiftMem cpu 2 rorOp
  | 0x6E => doShiftMem cpu 4 rorOp  | 0x7E => doShiftMem cpu 5 rorOp

  -- === BIT ===
  | 0x24 | 0x2C =>
    let mode := if opcode == 0x24 then 1 else 4
    let (v, pc) := cpu.fetchOperand mode
    ⟨{ cpu with pc := pc, flags := { cpu.flags with
        zero := cpu.a &&& v == 0, negative := v &&& 0x80 != 0, overflow := v &&& 0x40 != 0 } }, [], false⟩

  -- === BRANCHES ===
  | 0x90 => doBranch cpu (!cpu.flags.carry)       -- BCC
  | 0xB0 => doBranch cpu cpu.flags.carry          -- BCS
  | 0xF0 => doBranch cpu cpu.flags.zero           -- BEQ
  | 0xD0 => doBranch cpu (!cpu.flags.zero)        -- BNE
  | 0x30 => doBranch cpu cpu.flags.negative       -- BMI
  | 0x10 => doBranch cpu (!cpu.flags.negative)    -- BPL
  | 0x50 => doBranch cpu (!cpu.flags.overflow)    -- BVC
  | 0x70 => doBranch cpu cpu.flags.overflow       -- BVS

  -- === JMP ===
  | 0x4C => ⟨{ cpu with pc := cpu.read16 (cpu.pc + 1) }, [], false⟩              -- JMP abs
  | 0x6C =>                                                                        -- JMP (ind)
    let ptr := cpu.read16 (cpu.pc + 1)
    -- 6502 bug: if ptr is $xxFF, high byte wraps within page
    let lo := cpu.read ptr
    let hiAddr := if ptr &&& 0xFF == 0xFF then ptr &&& 0xFF00 else ptr + 1
    let hi := cpu.read hiAddr
    ⟨{ cpu with pc := lo.toUInt16 ||| (hi.toUInt16 <<< 8) }, [], false⟩

  -- === JSR / RTS / RTI ===
  | 0x20 =>
    let target := cpu.read16 (cpu.pc + 1)
    let cpu := cpu.push16 (cpu.pc + 2)
    ⟨{ cpu with pc := target }, [], false⟩
  | 0x60 =>
    let (cpu, addr) := cpu.pull16
    ⟨{ cpu with pc := addr + 1 }, [], false⟩
  | 0x40 =>  -- RTI
    let (cpu, flags) := cpu.pull
    let (cpu, addr) := cpu.pull16
    ⟨{ cpu with pc := addr, flags := byteToFlags flags }, [], false⟩

  -- === STACK ===
  | 0x48 => ⟨{ cpu.push cpu.a with pc := cpu.pc + 1 }, [], false⟩                  -- PHA
  | 0x68 => let (cpu, v) := cpu.pull                                                -- PLA
            ⟨{ cpu with a := v, pc := cpu.pc + 1, flags := updateNZ cpu.flags v }, [], false⟩
  | 0x08 => ⟨{ cpu.push (flagsToByte cpu.flags) with pc := cpu.pc + 1 }, [], false⟩ -- PHP
  | 0x28 => let (cpu, v) := cpu.pull                                                -- PLP
            ⟨{ cpu with pc := cpu.pc + 1, flags := byteToFlags v }, [], false⟩

  -- === TRANSFERS ===
  | 0xAA => ⟨{ cpu with x := cpu.a, pc := cpu.pc + 1, flags := updateNZ cpu.flags cpu.a }, [], false⟩  -- TAX
  | 0xA8 => ⟨{ cpu with y := cpu.a, pc := cpu.pc + 1, flags := updateNZ cpu.flags cpu.a }, [], false⟩  -- TAY
  | 0x8A => ⟨{ cpu with a := cpu.x, pc := cpu.pc + 1, flags := updateNZ cpu.flags cpu.x }, [], false⟩  -- TXA
  | 0x98 => ⟨{ cpu with a := cpu.y, pc := cpu.pc + 1, flags := updateNZ cpu.flags cpu.y }, [], false⟩  -- TYA
  | 0xBA => ⟨{ cpu with x := cpu.sp, pc := cpu.pc + 1, flags := updateNZ cpu.flags cpu.sp }, [], false⟩ -- TSX
  | 0x9A => ⟨{ cpu with sp := cpu.x, pc := cpu.pc + 1 }, [], false⟩                                    -- TXS

  -- === FLAGS ===
  | 0x18 => ⟨{ cpu with pc := cpu.pc + 1, flags := { cpu.flags with carry := false } }, [], false⟩      -- CLC
  | 0x38 => ⟨{ cpu with pc := cpu.pc + 1, flags := { cpu.flags with carry := true } }, [], false⟩       -- SEC
  | 0x58 => ⟨{ cpu with pc := cpu.pc + 1, flags := { cpu.flags with irqDis := false } }, [], false⟩     -- CLI
  | 0x78 => ⟨{ cpu with pc := cpu.pc + 1, flags := { cpu.flags with irqDis := true } }, [], false⟩      -- SEI
  | 0xB8 => ⟨{ cpu with pc := cpu.pc + 1, flags := { cpu.flags with overflow := false } }, [], false⟩   -- CLV
  | 0xD8 => ⟨{ cpu with pc := cpu.pc + 1, flags := { cpu.flags with decimal := false } }, [], false⟩    -- CLD
  | 0xF8 => ⟨{ cpu with pc := cpu.pc + 1, flags := { cpu.flags with decimal := true } }, [], false⟩     -- SED

  -- === NOP / BRK ===
  | 0xEA => ⟨{ cpu with pc := cpu.pc + 1 }, [], false⟩
  | 0x00 => ⟨{ cpu with pc := cpu.pc + 1 }, [], true⟩

  -- Unknown opcode: halt
  | _ => ⟨cpu, [], true⟩

-- Detect page crossing: do two addresses have different high bytes?
private def pageCross (a b : UInt16) : Bool := (a &&& 0xFF00) != (b &&& 0xFF00)

-- Step with cycle counting including page-crossing penalties
def step (cpu : CPU) : StepResult :=
  let opcode := cpu.read cpu.pc
  let result := stepRaw cpu
  let base := opcodeCycles opcode

  -- Branch penalty: +1 if taken, +1 more if page crossed
  let isBranch := opcode.toNat == 0x90 || opcode.toNat == 0xB0 || opcode.toNat == 0xF0 ||
     opcode.toNat == 0xD0 || opcode.toNat == 0x30 || opcode.toNat == 0x10 ||
     opcode.toNat == 0x50 || opcode.toNat == 0x70
  let branchPenalty := if isBranch && result.cpu.pc != cpu.pc + 2 then
    if pageCross (cpu.pc + 2) result.cpu.pc then 2 else 1
  else 0

  -- Page-crossing penalty for indexed addressing modes: +1 cycle
  -- Applies to: LDA/LDX/LDY/ADC/SBC/AND/ORA/EOR/CMP abs,X/abs,Y and (ind),Y READS
  -- Does NOT apply to STA/STX/STY (stores always take the extra cycle)
  let indexPenalty := match opcode.toNat with
    -- abs,X reads: check if base+X crosses page
    | 0xBD | 0xBC | 0x7D | 0xFD | 0x3D | 0x1D | 0x5D | 0xDD =>
      let baseAddr := cpu.read16 (cpu.pc + 1)
      if pageCross baseAddr (baseAddr + cpu.x.toUInt16) then 1 else 0
    -- abs,Y reads
    | 0xB9 | 0xBE | 0x79 | 0xF9 | 0x39 | 0x19 | 0x59 | 0xD9 =>
      let baseAddr := cpu.read16 (cpu.pc + 1)
      if pageCross baseAddr (baseAddr + cpu.y.toUInt16) then 1 else 0
    -- (ind),Y reads
    | 0xB1 | 0x71 | 0xF1 | 0x31 | 0x11 | 0x51 | 0xD1 =>
      let zp := cpu.read (cpu.pc + 1)
      let baseAddr := cpu.readZP16 zp
      if pageCross baseAddr (baseAddr + cpu.y.toUInt16) then 1 else 0
    | _ => 0

  let cyc := base + branchPenalty + indexPenalty
  { result with cpu := { result.cpu with cycles := cpu.cycles + cyc } }

-- ==========================================================================
-- Execution helpers
-- ==========================================================================

-- Run until PC reaches a sentinel address (simulates JSR + RTS return)
partial def execUntilPC (cpu : CPU) (stopPC : UInt16) (maxSteps : Nat := 500000) : CPU × List TimedSIDWrite :=
  if maxSteps == 0 then (cpu, [])
  else if cpu.pc == stopPC then (cpu, [])
  else
    let result := step cpu
    if result.halted then
      (result.cpu, result.sidWrites)
    else
      let (cpu', writes) := execUntilPC result.cpu stopPC (maxSteps - 1)
      (cpu', result.sidWrites ++ writes)

-- Execute a subroutine call (JSR simulation via sentinel)
def execCall (cpu : CPU) (addr : UInt16) : CPU × List TimedSIDWrite :=
  let cpu := { cpu with mem := cpu.mem.set! 0xFFF0 0x00 }
  let cpu := cpu.push16 0xFFEF
  let cpu := { cpu with pc := addr }
  execUntilPC cpu 0xFFF0

-- Execute the init routine
def execInit (cpu : CPU) (initAddr : UInt16) (subtune : UInt8 := 0) : CPU × List TimedSIDWrite :=
  let cpu := { cpu with a := subtune }
  execCall cpu initAddr

-- Execute one play call
def execPlay (cpu : CPU) (playAddr : UInt16) : CPU × List TimedSIDWrite :=
  execCall cpu playAddr

-- Execute N frames by calling play, grouping by function call (NOT cycle-accurate)
partial def execFrames (cpu : CPU) (playAddr : UInt16) (nFrames : Nat) : List (List TimedSIDWrite) :=
  if nFrames == 0 then []
  else
    let (cpu', writes) := execPlay cpu playAddr
    writes :: execFrames cpu' playAddr (nFrames - 1)

-- PAL frame = 19656 cycles (312 lines × 63 cycles) + 32 margin (siddump convention)
def PAL_CYCLES_PER_FRAME : Nat := 19656 + 32

-- Execute for exactly one PAL frame worth of cycles
-- Calls play at the start, then idles until the frame boundary
-- This matches sidplayfp's timing model
partial def execFrameCycleAccurate (cpu : CPU) (playAddr : UInt16) : CPU × List TimedSIDWrite :=
  let frameStart := cpu.cycles
  let frameEnd := frameStart + PAL_CYCLES_PER_FRAME
  -- Call play routine
  let (cpu, writes) := execCall cpu playAddr
  -- "Idle" until frame boundary — just advance the cycle counter
  let cpu := { cpu with cycles := frameEnd }
  (cpu, writes)

-- Execute N frames with cycle-accurate timing
partial def execFramesCycleAccurate (cpu : CPU) (playAddr : UInt16) (nFrames : Nat) : List (List TimedSIDWrite) :=
  if nFrames == 0 then []
  else
    let (cpu', writes) := execFrameCycleAccurate cpu playAddr
    writes :: execFramesCycleAccurate cpu' playAddr (nFrames - 1)

-- ==========================================================================
-- Load a SID file into CPU memory
-- ==========================================================================

def loadSID (sidData : ByteArray) : Option (CPU × UInt16 × UInt16) := do
  -- Parse PSID header
  if sidData.size < 126 then none
  -- Check magic "PSID"
  if sidData.get! 0 != 0x50 || sidData.get! 1 != 0x53 then none
  let dataOffset := (sidData.get! 6).toNat * 256 + (sidData.get! 7).toNat
  let loadAddr := (sidData.get! 8).toNat * 256 + (sidData.get! 9).toNat
  let initAddr : UInt16 := ((sidData.get! 10).toNat * 256 + (sidData.get! 11).toNat).toUInt16
  let playAddr : UInt16 := ((sidData.get! 12).toNat * 256 + (sidData.get! 13).toNat).toUInt16

  -- Load payload into memory
  let mut mem := ByteArray.mk #[]
  for _ in [:65536] do
    mem := mem.push 0
  let payload := sidData.extract dataOffset sidData.size
  let actualLoadAddr := if loadAddr == 0 then
    -- First 2 bytes of payload are the load address (little-endian)
    let la := (payload.get! 0).toNat + (payload.get! 1).toNat * 256
    la
  else loadAddr
  let payloadStart := if loadAddr == 0 then 2 else 0
  for i in [:payload.size - payloadStart] do
    let addr := actualLoadAddr + i
    if addr < 65536 then
      mem := mem.set! addr (payload.get! (payloadStart + i))

  let cpu : CPU := { mem := mem }
  some (cpu, initAddr, playAddr)
