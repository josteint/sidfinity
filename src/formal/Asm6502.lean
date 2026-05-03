/-
  Asm6502.lean — 6502 instruction set and assembler.

  Produces raw bytes from structured instructions.
  No external assembler needed — the Lean compiler IS the assembler.
-/

-- 6502 addressing modes
inductive AddrMode where
  | imm    : UInt8 → AddrMode          -- #$xx
  | zp     : UInt8 → AddrMode          -- $xx
  | zpX    : UInt8 → AddrMode          -- $xx,X
  | zpY    : UInt8 → AddrMode          -- $xx,Y
  | abs    : UInt16 → AddrMode         -- $xxxx
  | absX   : UInt16 → AddrMode         -- $xxxx,X
  | absY   : UInt16 → AddrMode         -- $xxxx,Y
  | ind    : UInt16 → AddrMode         -- ($xxxx)
  | indX   : UInt8 → AddrMode          -- ($xx,X)
  | indY   : UInt8 → AddrMode          -- ($xx),Y
  | impl   : AddrMode                  -- implied
  | acc    : AddrMode                  -- accumulator
  | rel    : Int8 → AddrMode           -- relative (branches)
  deriving Repr

-- 6502 mnemonics (subset needed for player codegen)
inductive Mnemonic where
  | LDA | LDX | LDY
  | STA | STX | STY
  | ADC | SBC
  | AND | ORA | EOR
  | CMP | CPX | CPY
  | INC | DEC | INX | DEX | INY | DEY
  | ASL | LSR | ROL | ROR
  | BCC | BCS | BEQ | BNE | BMI | BPL | BVC | BVS
  | JMP | JSR | RTS | RTI
  | PHA | PLA | PHP | PLP
  | TAX | TAY | TXA | TYA | TXS | TSX
  | CLC | SEC | CLI | SEI | CLV | CLD | SED
  | BIT | NOP | BRK
  deriving Repr, BEq

-- A single 6502 instruction
structure Instruction where
  mnemonic : Mnemonic
  mode     : AddrMode
  deriving Repr

-- Raw bytes
abbrev Bytes := Array UInt8

-- Opcode lookup: returns the opcode byte for a mnemonic + addressing mode.
-- Only the combinations we actually use are defined.
def opcode (m : Mnemonic) (mode : AddrMode) : Option UInt8 :=
  match m, mode with
  -- LDA
  | .LDA, .imm _   => some 0xA9
  | .LDA, .zp _    => some 0xA5
  | .LDA, .zpX _   => some 0xB5
  | .LDA, .abs _   => some 0xAD
  | .LDA, .absX _  => some 0xBD
  | .LDA, .absY _  => some 0xB9
  | .LDA, .indY _  => some 0xB1
  -- LDX
  | .LDX, .imm _   => some 0xA2
  | .LDX, .zp _    => some 0xA6
  | .LDX, .abs _   => some 0xAE
  -- LDY
  | .LDY, .imm _   => some 0xA0
  | .LDY, .zp _    => some 0xA4
  | .LDY, .abs _   => some 0xAC
  -- STA
  | .STA, .zp _    => some 0x85
  | .STA, .zpX _   => some 0x95
  | .STA, .abs _   => some 0x8D
  | .STA, .absX _  => some 0x9D
  | .STA, .absY _  => some 0x99
  | .STA, .indY _  => some 0x91
  -- STX
  | .STX, .zp _    => some 0x86
  | .STX, .abs _   => some 0x8E
  -- STY
  | .STY, .zp _    => some 0x84
  | .STY, .abs _   => some 0x8C
  -- ADC
  | .ADC, .imm _   => some 0x69
  | .ADC, .zp _    => some 0x65
  | .ADC, .abs _   => some 0x6D
  | .ADC, .absY _  => some 0x79
  -- SBC
  | .SBC, .imm _   => some 0xE9
  | .SBC, .zp _    => some 0xE5
  -- AND
  | .AND, .imm _   => some 0x29
  | .AND, .zp _    => some 0x25
  -- ORA
  | .ORA, .imm _   => some 0x09
  | .ORA, .zp _    => some 0x05
  -- EOR
  | .EOR, .imm _   => some 0x49
  -- CMP
  | .CMP, .imm _   => some 0xC9
  | .CMP, .zp _    => some 0xC5
  | .CMP, .absX _  => some 0xDD
  | .CMP, .absY _  => some 0xD9
  -- CPX
  | .CPX, .imm _   => some 0xE0
  -- CPY
  | .CPY, .imm _   => some 0xC0
  -- INC/DEC
  | .INC, .zp _    => some 0xE6
  | .INC, .zpX _   => some 0xF6
  | .INC, .abs _   => some 0xEE
  | .DEC, .zp _    => some 0xC6
  | .DEC, .zpX _   => some 0xD6
  | .DEC, .abs _   => some 0xCE
  -- INX/DEX/INY/DEY
  | .INX, .impl    => some 0xE8
  | .DEX, .impl    => some 0xCA
  | .INY, .impl    => some 0xC8
  | .DEY, .impl    => some 0x88
  -- ASL
  | .ASL, .acc     => some 0x0A
  | .ASL, .zp _    => some 0x06
  -- LSR
  | .LSR, .acc     => some 0x4A
  | .LSR, .zp _    => some 0x46
  -- ROL/ROR
  | .ROL, .acc     => some 0x2A
  | .ROR, .acc     => some 0x6A
  | .ROR, .zp _    => some 0x66
  -- Branches
  | .BCC, .rel _   => some 0x90
  | .BCS, .rel _   => some 0xB0
  | .BEQ, .rel _   => some 0xF0
  | .BNE, .rel _   => some 0xD0
  | .BMI, .rel _   => some 0x30
  | .BPL, .rel _   => some 0x10
  | .BVC, .rel _   => some 0x50
  | .BVS, .rel _   => some 0x70
  -- JMP/JSR/RTS
  | .JMP, .abs _   => some 0x4C
  | .JSR, .abs _   => some 0x20
  | .RTS, .impl    => some 0x60
  | .RTI, .impl    => some 0x40
  -- Stack
  | .PHA, .impl    => some 0x48
  | .PLA, .impl    => some 0x68
  -- Transfers
  | .TAX, .impl    => some 0xAA
  | .TAY, .impl    => some 0xA8
  | .TXA, .impl    => some 0x8A
  | .TYA, .impl    => some 0x98
  -- Flags
  | .CLC, .impl    => some 0x18
  | .SEC, .impl    => some 0x38
  | .SEI, .impl    => some 0x78
  | .CLI, .impl    => some 0x58
  -- BIT
  | .BIT, .zp _    => some 0x24
  | .BIT, .abs _   => some 0x2C
  -- NOP/BRK
  | .NOP, .impl    => some 0xEA
  | .BRK, .impl    => some 0x00
  | _, _           => none

-- Encode operand bytes
def operandBytes (mode : AddrMode) : Bytes :=
  match mode with
  | .imm v     => #[v]
  | .zp v      => #[v]
  | .zpX v     => #[v]
  | .zpY v     => #[v]
  | .abs v     => #[v.toUInt8, (v >>> 8).toUInt8]       -- little-endian
  | .absX v    => #[v.toUInt8, (v >>> 8).toUInt8]
  | .absY v    => #[v.toUInt8, (v >>> 8).toUInt8]
  | .ind v     => #[v.toUInt8, (v >>> 8).toUInt8]
  | .indX v    => #[v]
  | .indY v    => #[v]
  | .impl      => #[]
  | .acc       => #[]
  | .rel v     => #[v.toUInt8]

-- Assemble one instruction to bytes
def assembleInst (inst : Instruction) : Option Bytes :=
  match opcode inst.mnemonic inst.mode with
  | some op => some (#[op] ++ operandBytes inst.mode)
  | none    => none

-- Assemble a list of instructions
def assemble (insts : List Instruction) : Option Bytes :=
  insts.foldlM (fun acc inst =>
    match assembleInst inst with
    | some bytes => some (acc ++ bytes)
    | none       => none
  ) #[]

-- Convenience constructors
namespace I
def lda_imm (v : UInt8) : Instruction := ⟨.LDA, .imm v⟩
def ldx_imm (v : UInt8) : Instruction := ⟨.LDX, .imm v⟩
def ldy_imm (v : UInt8) : Instruction := ⟨.LDY, .imm v⟩
def sta_abs (addr : UInt16) : Instruction := ⟨.STA, .abs addr⟩
def sta_zp (addr : UInt8) : Instruction := ⟨.STA, .zp addr⟩
def lda_zp (addr : UInt8) : Instruction := ⟨.LDA, .zp addr⟩
def lda_abs (addr : UInt16) : Instruction := ⟨.LDA, .abs addr⟩
def lda_absX (addr : UInt16) : Instruction := ⟨.LDA, .absX addr⟩
def lda_absY (addr : UInt16) : Instruction := ⟨.LDA, .absY addr⟩
def sta_absX (addr : UInt16) : Instruction := ⟨.STA, .absX addr⟩
def sta_absY (addr : UInt16) : Instruction := ⟨.STA, .absY addr⟩
def inc_zp (addr : UInt8) : Instruction := ⟨.INC, .zp addr⟩
def dec_zp (addr : UInt8) : Instruction := ⟨.DEC, .zp addr⟩
def cmp_imm (v : UInt8) : Instruction := ⟨.CMP, .imm v⟩
def adc_imm (v : UInt8) : Instruction := ⟨.ADC, .imm v⟩
def sbc_imm (v : UInt8) : Instruction := ⟨.SBC, .imm v⟩
def sbc_zp (addr : UInt8) : Instruction := ⟨.SBC, .zp addr⟩
def and_imm (v : UInt8) : Instruction := ⟨.AND, .imm v⟩
def ora_imm (v : UInt8) : Instruction := ⟨.ORA, .imm v⟩
def bne (offset : Int8) : Instruction := ⟨.BNE, .rel offset⟩
def beq (offset : Int8) : Instruction := ⟨.BEQ, .rel offset⟩
def bmi (offset : Int8) : Instruction := ⟨.BMI, .rel offset⟩
def bpl (offset : Int8) : Instruction := ⟨.BPL, .rel offset⟩
def bcc (offset : Int8) : Instruction := ⟨.BCC, .rel offset⟩
def bcs (offset : Int8) : Instruction := ⟨.BCS, .rel offset⟩
def jmp (addr : UInt16) : Instruction := ⟨.JMP, .abs addr⟩
def jsr (addr : UInt16) : Instruction := ⟨.JSR, .abs addr⟩
def rts : Instruction := ⟨.RTS, .impl⟩
def inx : Instruction := ⟨.INX, .impl⟩
def dex : Instruction := ⟨.DEX, .impl⟩
def iny : Instruction := ⟨.INY, .impl⟩
def dey : Instruction := ⟨.DEY, .impl⟩
def tax : Instruction := ⟨.TAX, .impl⟩
def tay : Instruction := ⟨.TAY, .impl⟩
def txa : Instruction := ⟨.TXA, .impl⟩
def tya : Instruction := ⟨.TYA, .impl⟩
def clc : Instruction := ⟨.CLC, .impl⟩
def sec : Instruction := ⟨.SEC, .impl⟩
def sei : Instruction := ⟨.SEI, .impl⟩
def pha : Instruction := ⟨.PHA, .impl⟩
def pla : Instruction := ⟨.PLA, .impl⟩
def nop : Instruction := ⟨.NOP, .impl⟩
def stx_zp (addr : UInt8) : Instruction := ⟨.STX, .zp addr⟩
def ldx_zp (addr : UInt8) : Instruction := ⟨.LDX, .zp addr⟩
def ora_zp (addr : UInt8) : Instruction := ⟨.ORA, .zp addr⟩
def adc_zp (addr : UInt8) : Instruction := ⟨.ADC, .zp addr⟩
def sty_zp (addr : UInt8) : Instruction := ⟨.STY, .zp addr⟩
def ldy_zp (addr : UInt8) : Instruction := ⟨.LDY, .zp addr⟩
def eor_imm (v : UInt8) : Instruction := ⟨.EOR, .imm v⟩
def asl_a : Instruction := ⟨.ASL, .acc⟩
def lsr_a : Instruction := ⟨.LSR, .acc⟩
end I

-- Raw byte emission (for inline data)
def rawByte (v : UInt8) : Bytes := #[v]
def rawWord (v : UInt16) : Bytes := #[v.toUInt8, (v >>> 8).toUInt8]  -- little-endian
def rawBytes (vs : List UInt8) : Bytes := vs.toArray
