"""
abstract_interp.py - Abstract interpretation framework for 6502 SID player analysis.

Given a 6502 binary (SID file player code), symbolically executes it to extract
high-level structure WITHOUT needing to know the player engine. This is the formal
version of what sidxray does heuristically via runtime tracing.

Key idea: track abstract values through 6502 instructions to discover data flow
from tables to SID register writes. For example:
    LDA freq_lo,X  -> A = TableIndex($1000, X)
    STA $D400      -> SID freq_lo[voice] = FreqValue from table[$1000+X]

Usage:
    python3 -m formal.abstract_interp path/to/song.sid
"""

import struct
import sys
import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Union
from collections import defaultdict

# ---------------------------------------------------------------------------
# 6502 instruction table
# ---------------------------------------------------------------------------

# Instruction lengths by opcode (same as code_flow.py)
_INST_LEN = [0] * 256
for _op in [0x00, 0x08, 0x0A, 0x18, 0x28, 0x2A, 0x38, 0x40, 0x48, 0x4A,
            0x58, 0x60, 0x68, 0x6A, 0x78, 0x88, 0x8A, 0x98, 0x9A, 0xA8,
            0xAA, 0xB8, 0xBA, 0xC8, 0xCA, 0xD8, 0xE8, 0xEA, 0xF8]:
    _INST_LEN[_op] = 1
for _op in range(256):
    if _INST_LEN[_op] > 0:
        continue
    _mode = _op & 0x1F
    if _mode in (0x00, 0x01, 0x02, 0x04, 0x05, 0x06, 0x09, 0x0A,
                 0x10, 0x11, 0x12, 0x14, 0x15, 0x16):
        _INST_LEN[_op] = 2
for _i in range(256):
    if _INST_LEN[_i] == 0:
        _INST_LEN[_i] = 3

# Opcode names for disassembly
_OPCODE_NAMES = {
    0x00: 'BRK', 0x01: 'ORA', 0x05: 'ORA', 0x06: 'ASL', 0x08: 'PHP',
    0x09: 'ORA', 0x0A: 'ASL', 0x0D: 'ORA', 0x0E: 'ASL', 0x10: 'BPL',
    0x11: 'ORA', 0x15: 'ORA', 0x16: 'ASL', 0x18: 'CLC', 0x19: 'ORA',
    0x1D: 'ORA', 0x1E: 'ASL', 0x20: 'JSR', 0x21: 'AND', 0x24: 'BIT',
    0x25: 'AND', 0x26: 'ROL', 0x28: 'PLP', 0x29: 'AND', 0x2A: 'ROL',
    0x2C: 'BIT', 0x2D: 'AND', 0x2E: 'ROL', 0x30: 'BMI', 0x31: 'AND',
    0x35: 'AND', 0x36: 'ROL', 0x38: 'SEC', 0x39: 'AND', 0x3D: 'AND',
    0x3E: 'ROL', 0x40: 'RTI', 0x41: 'EOR', 0x45: 'EOR', 0x46: 'LSR',
    0x48: 'PHA', 0x49: 'EOR', 0x4A: 'LSR', 0x4C: 'JMP', 0x4D: 'EOR',
    0x4E: 'LSR', 0x50: 'BVC', 0x51: 'EOR', 0x55: 'EOR', 0x56: 'LSR',
    0x58: 'CLI', 0x59: 'EOR', 0x5D: 'EOR', 0x5E: 'LSR', 0x60: 'RTS',
    0x61: 'ADC', 0x65: 'ADC', 0x66: 'ROR', 0x68: 'PLA', 0x69: 'ADC',
    0x6A: 'ROR', 0x6C: 'JMP', 0x6D: 'ADC', 0x6E: 'ROR', 0x70: 'BVS',
    0x71: 'ADC', 0x75: 'ADC', 0x76: 'ROR', 0x78: 'SEI', 0x79: 'ADC',
    0x7D: 'ADC', 0x7E: 'ROR', 0x81: 'STA', 0x84: 'STY', 0x85: 'STA',
    0x86: 'STX', 0x88: 'DEY', 0x8A: 'TXA', 0x8C: 'STY', 0x8D: 'STA',
    0x8E: 'STX', 0x90: 'BCC', 0x91: 'STA', 0x94: 'STY', 0x95: 'STA',
    0x96: 'STX', 0x98: 'TYA', 0x99: 'STA', 0x9A: 'TXS', 0x9D: 'STA',
    0xA0: 'LDY', 0xA1: 'LDA', 0xA2: 'LDX', 0xA4: 'LDY', 0xA5: 'LDA',
    0xA6: 'LDX', 0xA8: 'TAY', 0xA9: 'LDA', 0xAA: 'TAX', 0xAC: 'LDY',
    0xAD: 'LDA', 0xAE: 'LDX', 0xB0: 'BCS', 0xB1: 'LDA', 0xB4: 'LDY',
    0xB5: 'LDA', 0xB6: 'LDX', 0xB8: 'CLV', 0xB9: 'LDA', 0xBA: 'TSX',
    0xBC: 'LDY', 0xBD: 'LDA', 0xBE: 'LDX', 0xC0: 'CPY', 0xC1: 'CMP',
    0xC4: 'CPY', 0xC5: 'CMP', 0xC6: 'DEC', 0xC8: 'INY', 0xC9: 'CMP',
    0xCA: 'DEX', 0xCC: 'CPY', 0xCD: 'CMP', 0xCE: 'DEC', 0xD0: 'BNE',
    0xD1: 'CMP', 0xD5: 'CMP', 0xD6: 'DEC', 0xD8: 'CLD', 0xD9: 'CMP',
    0xDD: 'CMP', 0xDE: 'DEC', 0xE0: 'CPX', 0xE1: 'SBC', 0xE4: 'CPX',
    0xE5: 'SBC', 0xE6: 'INC', 0xE8: 'INX', 0xE9: 'SBC', 0xEA: 'NOP',
    0xEC: 'CPX', 0xED: 'SBC', 0xEE: 'INC', 0xF0: 'BEQ', 0xF1: 'SBC',
    0xF5: 'SBC', 0xF6: 'INC', 0xF8: 'SED', 0xF9: 'SBC', 0xFD: 'SBC',
    0xFE: 'INC',
}

# Branch opcodes
_BRANCHES = {0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0}

# SID register range
SID_BASE = 0xD400
SID_END = 0xD419  # exclusive

SID_REG_NAMES = {
    0x00: 'freq_lo_1', 0x01: 'freq_hi_1', 0x02: 'pw_lo_1', 0x03: 'pw_hi_1',
    0x04: 'ctrl_1', 0x05: 'ad_1', 0x06: 'sr_1',
    0x07: 'freq_lo_2', 0x08: 'freq_hi_2', 0x09: 'pw_lo_2', 0x0A: 'pw_hi_2',
    0x0B: 'ctrl_2', 0x0C: 'ad_2', 0x0D: 'sr_2',
    0x0E: 'freq_lo_3', 0x0F: 'freq_hi_3', 0x10: 'pw_lo_3', 0x11: 'pw_hi_3',
    0x12: 'ctrl_3', 0x13: 'ad_3', 0x14: 'sr_3',
    0x15: 'fc_lo', 0x16: 'fc_hi', 0x17: 'res_filt', 0x18: 'mode_vol',
}


# ---------------------------------------------------------------------------
# Abstract Domain
# ---------------------------------------------------------------------------

class AbsKind(Enum):
    CONCRETE = auto()
    TABLE_INDEX = auto()
    COUNTER = auto()
    SID_REGISTER = auto()
    FREQ_VALUE = auto()
    COMPUTED = auto()   # result of arithmetic on abstract values
    UNKNOWN = auto()


@dataclass(frozen=True)
class AbsVal:
    """Abstract value representing what a byte might be."""
    kind: AbsKind
    # For CONCRETE: value is the known byte
    value: Optional[int] = None
    # For TABLE_INDEX: base address and which register is the index
    table_base: Optional[int] = None
    index_reg: Optional[str] = None  # 'X' or 'Y'
    # For COUNTER: range and step
    min_val: Optional[int] = None
    max_val: Optional[int] = None
    step: Optional[int] = None
    # For FREQ_VALUE: which note variable it came from
    note_source: Optional[str] = None
    # For COMPUTED: operation description
    op_desc: Optional[str] = None
    # For SID_REGISTER: register id
    reg_id: Optional[int] = None

    def __repr__(self):
        if self.kind == AbsKind.CONCRETE:
            return f'Concrete(${self.value:02X})' if self.value is not None else 'Concrete(?)'
        elif self.kind == AbsKind.TABLE_INDEX:
            return f'Table[${self.table_base:04X}+{self.index_reg}]'
        elif self.kind == AbsKind.COUNTER:
            return f'Counter({self.min_val}..{self.max_val}, step={self.step})'
        elif self.kind == AbsKind.FREQ_VALUE:
            return f'Freq({self.note_source})'
        elif self.kind == AbsKind.COMPUTED:
            return f'Computed({self.op_desc})'
        elif self.kind == AbsKind.SID_REGISTER:
            name = SID_REG_NAMES.get(self.reg_id, f'${self.reg_id:02X}')
            return f'SIDReg({name})'
        return 'Unknown'


UNKNOWN = AbsVal(kind=AbsKind.UNKNOWN)

def concrete(val):
    return AbsVal(kind=AbsKind.CONCRETE, value=val & 0xFF)

def table_index(base, reg):
    return AbsVal(kind=AbsKind.TABLE_INDEX, table_base=base, index_reg=reg)

def counter(mn, mx, step=1):
    return AbsVal(kind=AbsKind.COUNTER, min_val=mn, max_val=mx, step=step)

def freq_value(source):
    return AbsVal(kind=AbsKind.FREQ_VALUE, note_source=source)

def computed(desc):
    return AbsVal(kind=AbsKind.COMPUTED, op_desc=desc)


# ---------------------------------------------------------------------------
# SID Write Record
# ---------------------------------------------------------------------------

@dataclass
class SIDWrite:
    """A detected write to a SID register."""
    addr: int              # absolute address $D400-$D418
    reg_name: str          # human-readable register name
    source: AbsVal         # abstract value being written
    pc: int                # program counter where the write happens
    voice: int             # voice number 0-2 (or -1 for filter/global)
    category: str = ''     # 'freq', 'waveform', 'adsr', 'pulse', 'filter', 'global'

    def __repr__(self):
        return f'SIDWrite(${self.addr:04X} {self.reg_name} <- {self.source} @${self.pc:04X})'


@dataclass
class DataTable:
    """A discovered data table."""
    base_addr: int
    size_hint: int     # estimated size (may be approximate)
    label: str         # 'freq_lo', 'freq_hi', 'waveform', 'adsr', 'pattern', etc.
    accessed_by: list = field(default_factory=list)  # list of PCs that read this table
    index_reg: str = ''  # 'X' or 'Y'

    def __repr__(self):
        return f'DataTable(${self.base_addr:04X} [{self.label}] ~{self.size_hint} bytes, idx={self.index_reg})'


@dataclass
class DriverAnalysis:
    """Complete analysis result."""
    freq_table: Optional[tuple] = None      # (lo_addr, hi_addr)
    instrument_table: Optional[int] = None
    wave_table: Optional[int] = None
    pattern_base: Optional[int] = None
    orderlist_base: Optional[int] = None
    tempo_counter_addr: Optional[int] = None
    voice_loop_type: str = 'unknown'        # 'indexed_x', 'separate', 'unrolled'
    sid_writes: list = field(default_factory=list)
    tables: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Abstract CPU State
# ---------------------------------------------------------------------------

@dataclass
class AbsCPUState:
    """Abstract 6502 CPU state."""
    A: AbsVal = field(default_factory=lambda: UNKNOWN)
    X: AbsVal = field(default_factory=lambda: UNKNOWN)
    Y: AbsVal = field(default_factory=lambda: UNKNOWN)
    SP: AbsVal = field(default_factory=lambda: concrete(0xFF))
    C: Optional[bool] = None   # None = unknown
    Z: Optional[bool] = None
    N: Optional[bool] = None
    V: Optional[bool] = None
    # Abstract memory: addr -> AbsVal (only tracked locations)
    mem: dict = field(default_factory=dict)

    def clone(self):
        s = AbsCPUState()
        s.A = self.A
        s.X = self.X
        s.Y = self.Y
        s.SP = self.SP
        s.C = self.C
        s.Z = self.Z
        s.N = self.N
        s.V = self.V
        s.mem = dict(self.mem)
        return s


def merge_abs(a, b):
    """Merge two abstract values (join in the lattice). Used at loop headers."""
    if a == b:
        return a
    if a.kind == AbsKind.UNKNOWN or b.kind == AbsKind.UNKNOWN:
        return UNKNOWN
    # Two different concrete values -> counter or unknown
    if a.kind == AbsKind.CONCRETE and b.kind == AbsKind.CONCRETE:
        va, vb = a.value, b.value
        diff = (vb - va) & 0xFF
        if diff <= 127:
            return counter(min(va, vb), max(va, vb), diff if diff > 0 else 1)
        return UNKNOWN
    # Same table base -> keep it
    if (a.kind == AbsKind.TABLE_INDEX and b.kind == AbsKind.TABLE_INDEX
            and a.table_base == b.table_base):
        return a
    return UNKNOWN


def merge_states(s1, s2):
    """Merge two abstract CPU states (join)."""
    s = AbsCPUState()
    s.A = merge_abs(s1.A, s2.A)
    s.X = merge_abs(s1.X, s2.X)
    s.Y = merge_abs(s1.Y, s2.Y)
    s.C = s1.C if s1.C == s2.C else None
    s.Z = s1.Z if s1.Z == s2.Z else None
    s.N = s1.N if s1.N == s2.N else None
    s.V = s1.V if s1.V == s2.V else None
    # Merge memory: only keep entries present in both with same value
    all_addrs = set(s1.mem.keys()) | set(s2.mem.keys())
    for addr in all_addrs:
        v1 = s1.mem.get(addr, UNKNOWN)
        v2 = s2.mem.get(addr, UNKNOWN)
        merged = merge_abs(v1, v2)
        if merged.kind != AbsKind.UNKNOWN:
            s.mem[addr] = merged
    return s


# ---------------------------------------------------------------------------
# 6502 Disassembler
# ---------------------------------------------------------------------------

class AddressingMode(Enum):
    IMPLIED = auto()
    ACCUMULATOR = auto()
    IMMEDIATE = auto()
    ZERO_PAGE = auto()
    ZERO_PAGE_X = auto()
    ZERO_PAGE_Y = auto()
    ABSOLUTE = auto()
    ABSOLUTE_X = auto()
    ABSOLUTE_Y = auto()
    INDIRECT = auto()
    INDIRECT_X = auto()
    INDIRECT_Y = auto()
    RELATIVE = auto()


def _decode_addressing_mode(opcode):
    """Determine addressing mode from opcode."""
    # Implied / accumulator (1-byte instructions)
    if opcode in (0x00, 0x08, 0x18, 0x28, 0x38, 0x40, 0x48, 0x58, 0x60,
                  0x68, 0x78, 0x88, 0x8A, 0x98, 0x9A, 0xA8, 0xAA, 0xB8,
                  0xBA, 0xC8, 0xCA, 0xD8, 0xE8, 0xEA, 0xF8):
        return AddressingMode.IMPLIED
    if opcode in (0x0A, 0x2A, 0x4A, 0x6A):
        return AddressingMode.ACCUMULATOR
    # Branches
    if opcode in _BRANCHES:
        return AddressingMode.RELATIVE
    # Indirect JMP
    if opcode == 0x6C:
        return AddressingMode.INDIRECT

    lo = opcode & 0x1F
    # Determine by low 5 bits pattern
    if lo == 0x09 or lo == 0x00 and opcode in (0xA0, 0xA2, 0xC0, 0xE0):
        return AddressingMode.IMMEDIATE
    if lo == 0x09:
        return AddressingMode.IMMEDIATE
    if lo == 0x01:
        return AddressingMode.INDIRECT_X
    if lo == 0x11:
        return AddressingMode.INDIRECT_Y
    if lo in (0x05, 0x06, 0x04):
        return AddressingMode.ZERO_PAGE
    if lo in (0x15, 0x16, 0x14):
        # STX/LDX zp,Y uses 0x96/0xB6
        if opcode in (0x96, 0xB6):
            return AddressingMode.ZERO_PAGE_Y
        return AddressingMode.ZERO_PAGE_X
    if lo in (0x0D, 0x0E, 0x0C):
        return AddressingMode.ABSOLUTE
    if lo in (0x1D, 0x1E, 0x1C):
        if opcode in (0xBE,):
            return AddressingMode.ABSOLUTE_Y
        return AddressingMode.ABSOLUTE_X
    if lo == 0x19:
        return AddressingMode.ABSOLUTE_Y
    # JSR/JMP abs
    if opcode in (0x20, 0x4C):
        return AddressingMode.ABSOLUTE
    # STA abs,Y
    if opcode == 0x99:
        return AddressingMode.ABSOLUTE_Y
    # STA abs,X
    if opcode == 0x9D:
        return AddressingMode.ABSOLUTE_X
    # Fallback by instruction length
    ln = _INST_LEN[opcode]
    if ln == 2:
        return AddressingMode.IMMEDIATE
    if ln == 3:
        return AddressingMode.ABSOLUTE
    return AddressingMode.IMPLIED


@dataclass
class Instruction:
    """Decoded 6502 instruction."""
    addr: int           # absolute address
    opcode: int
    name: str
    mode: AddressingMode
    operand: int        # raw operand value (byte or word)
    length: int

    def __repr__(self):
        name = self.name
        if self.mode == AddressingMode.IMPLIED:
            return f'${self.addr:04X}: {name}'
        elif self.mode == AddressingMode.ACCUMULATOR:
            return f'${self.addr:04X}: {name} A'
        elif self.mode == AddressingMode.IMMEDIATE:
            return f'${self.addr:04X}: {name} #${self.operand:02X}'
        elif self.mode == AddressingMode.ZERO_PAGE:
            return f'${self.addr:04X}: {name} ${self.operand:02X}'
        elif self.mode == AddressingMode.ZERO_PAGE_X:
            return f'${self.addr:04X}: {name} ${self.operand:02X},X'
        elif self.mode == AddressingMode.ZERO_PAGE_Y:
            return f'${self.addr:04X}: {name} ${self.operand:02X},Y'
        elif self.mode == AddressingMode.ABSOLUTE:
            return f'${self.addr:04X}: {name} ${self.operand:04X}'
        elif self.mode == AddressingMode.ABSOLUTE_X:
            return f'${self.addr:04X}: {name} ${self.operand:04X},X'
        elif self.mode == AddressingMode.ABSOLUTE_Y:
            return f'${self.addr:04X}: {name} ${self.operand:04X},Y'
        elif self.mode == AddressingMode.INDIRECT:
            return f'${self.addr:04X}: {name} (${self.operand:04X})'
        elif self.mode == AddressingMode.INDIRECT_X:
            return f'${self.addr:04X}: {name} (${self.operand:02X},X)'
        elif self.mode == AddressingMode.INDIRECT_Y:
            return f'${self.addr:04X}: {name} (${self.operand:02X}),Y'
        elif self.mode == AddressingMode.RELATIVE:
            # Compute target
            offset = self.operand if self.operand < 128 else self.operand - 256
            target = self.addr + 2 + offset
            return f'${self.addr:04X}: {name} ${target:04X}'
        return f'${self.addr:04X}: {name} ???'


def disassemble_at(memory, load_addr, addr):
    """Disassemble one instruction at the given absolute address.
    memory: the raw binary bytes. load_addr: base address of memory[0].
    Returns an Instruction or None if out of bounds.
    """
    offset = addr - load_addr
    if offset < 0 or offset >= len(memory):
        return None
    opcode = memory[offset]
    length = _INST_LEN[opcode]
    if offset + length > len(memory):
        return None
    name = _OPCODE_NAMES.get(opcode, f'???_{opcode:02X}')
    mode = _decode_addressing_mode(opcode)

    if length == 1:
        operand = 0
    elif length == 2:
        operand = memory[offset + 1]
    else:
        operand = memory[offset + 1] | (memory[offset + 2] << 8)

    return Instruction(addr=addr, opcode=opcode, name=name, mode=mode,
                       operand=operand, length=length)


# ---------------------------------------------------------------------------
# Abstract Interpreter
# ---------------------------------------------------------------------------

class AbstractInterpreter:
    """Abstract interpreter for 6502 code.

    Executes code symbolically, tracking abstract values through registers
    and memory. At conditional branches, explores both paths. Detects loops
    via back-edge detection and uses widening after a fixed number of iterations.
    """

    MAX_STEPS = 50000       # safety limit per analysis
    MAX_LOOP_ITER = 3       # widen after this many iterations of a loop header
    MAX_CALL_DEPTH = 8      # maximum JSR nesting

    def __init__(self, memory, load_addr):
        self.memory = memory
        self.load_addr = load_addr
        self.end_addr = load_addr + len(memory)

        # Results
        self.sid_writes = []        # list of SIDWrite
        self.table_accesses = defaultdict(list)  # base_addr -> list of (pc, reg)
        self.tables = []            # discovered DataTable objects

        # Analysis state
        self._steps = 0
        self._loop_counts = defaultdict(int)  # addr -> visit count
        self._visited_states = {}  # addr -> list of AbsCPUState seen

    def read_byte(self, addr):
        """Read a concrete byte from memory, or None if out of range."""
        off = addr - self.load_addr
        if 0 <= off < len(self.memory):
            return self.memory[off]
        return None

    def _resolve_read(self, state, insn):
        """Resolve the abstract value that an instruction reads.

        Returns (AbsVal, effective_address_or_None).
        """
        mode = insn.mode
        op = insn.operand

        if mode == AddressingMode.IMMEDIATE:
            return concrete(op), None

        if mode == AddressingMode.ACCUMULATOR:
            return state.A, None

        if mode == AddressingMode.ZERO_PAGE:
            val = state.mem.get(op, UNKNOWN)
            return val, op

        if mode == AddressingMode.ZERO_PAGE_X:
            if state.X.kind == AbsKind.CONCRETE:
                eff = (op + state.X.value) & 0xFF
                return state.mem.get(eff, UNKNOWN), eff
            return UNKNOWN, None

        if mode == AddressingMode.ZERO_PAGE_Y:
            if state.Y.kind == AbsKind.CONCRETE:
                eff = (op + state.Y.value) & 0xFF
                return state.mem.get(eff, UNKNOWN), eff
            return UNKNOWN, None

        if mode == AddressingMode.ABSOLUTE:
            # Check concrete memory first
            val = state.mem.get(op)
            if val is not None:
                return val, op
            b = self.read_byte(op)
            if b is not None:
                return concrete(b), op
            return UNKNOWN, op

        if mode == AddressingMode.ABSOLUTE_X:
            if state.X.kind == AbsKind.CONCRETE:
                eff = op + state.X.value
                val = state.mem.get(eff)
                if val is not None:
                    return val, eff
                b = self.read_byte(eff)
                if b is not None:
                    return concrete(b), eff
                return UNKNOWN, eff
            # X is not concrete: this is a table access
            self.table_accesses[op].append((insn.addr, 'X'))
            return table_index(op, 'X'), None

        if mode == AddressingMode.ABSOLUTE_Y:
            if state.Y.kind == AbsKind.CONCRETE:
                eff = op + state.Y.value
                val = state.mem.get(eff)
                if val is not None:
                    return val, eff
                b = self.read_byte(eff)
                if b is not None:
                    return concrete(b), eff
                return UNKNOWN, eff
            self.table_accesses[op].append((insn.addr, 'Y'))
            return table_index(op, 'Y'), None

        if mode == AddressingMode.INDIRECT_Y:
            # (zp),Y - read pointer from zp, add Y
            lo_val = state.mem.get(op, UNKNOWN)
            hi_val = state.mem.get((op + 1) & 0xFF, UNKNOWN)
            if lo_val.kind == AbsKind.CONCRETE and hi_val.kind == AbsKind.CONCRETE:
                base = lo_val.value | (hi_val.value << 8)
                if state.Y.kind == AbsKind.CONCRETE:
                    eff = base + state.Y.value
                    b = self.read_byte(eff)
                    if b is not None:
                        return concrete(b), eff
                    return UNKNOWN, eff
                self.table_accesses[base].append((insn.addr, 'Y'))
                return table_index(base, 'Y'), None
            return UNKNOWN, None

        if mode == AddressingMode.INDIRECT_X:
            # (zp,X) - add X to zp, read pointer
            if state.X.kind == AbsKind.CONCRETE:
                ptr = (op + state.X.value) & 0xFF
                lo_val = state.mem.get(ptr, UNKNOWN)
                hi_val = state.mem.get((ptr + 1) & 0xFF, UNKNOWN)
                if lo_val.kind == AbsKind.CONCRETE and hi_val.kind == AbsKind.CONCRETE:
                    eff = lo_val.value | (hi_val.value << 8)
                    b = self.read_byte(eff)
                    if b is not None:
                        return concrete(b), eff
                    return UNKNOWN, eff
            return UNKNOWN, None

        return UNKNOWN, None

    def _resolve_write_addr(self, state, insn):
        """Resolve the effective address for a store instruction."""
        mode = insn.mode
        op = insn.operand

        if mode == AddressingMode.ZERO_PAGE:
            return op
        if mode == AddressingMode.ZERO_PAGE_X:
            if state.X.kind == AbsKind.CONCRETE:
                return (op + state.X.value) & 0xFF
            return None
        if mode == AddressingMode.ZERO_PAGE_Y:
            if state.Y.kind == AbsKind.CONCRETE:
                return (op + state.Y.value) & 0xFF
            return None
        if mode == AddressingMode.ABSOLUTE:
            return op
        if mode == AddressingMode.ABSOLUTE_X:
            if state.X.kind == AbsKind.CONCRETE:
                return op + state.X.value
            # SID writes often use STA $D400,X with X=0,7,14
            # Even if X is unknown, we know the base
            return None
        if mode == AddressingMode.ABSOLUTE_Y:
            if state.Y.kind == AbsKind.CONCRETE:
                return op + state.Y.value
            return None
        if mode == AddressingMode.INDIRECT_Y:
            lo_val = state.mem.get(op, UNKNOWN)
            hi_val = state.mem.get((op + 1) & 0xFF, UNKNOWN)
            if lo_val.kind == AbsKind.CONCRETE and hi_val.kind == AbsKind.CONCRETE:
                base = lo_val.value | (hi_val.value << 8)
                if state.Y.kind == AbsKind.CONCRETE:
                    return base + state.Y.value
            return None
        return None

    def _record_sid_write(self, addr, source, pc, state, insn):
        """Record a write to a SID register."""
        if addr is None:
            # Check if this is a STA $D4xx,X pattern with unknown X
            if (insn.mode == AddressingMode.ABSOLUTE_X and
                    SID_BASE <= insn.operand < SID_END):
                # Record with base address; X determines voice
                for voice_off in (0, 7, 14):
                    reg = insn.operand - SID_BASE + voice_off
                    if 0 <= reg < 0x19:
                        self._add_sid_write(insn.operand + voice_off, source, pc, reg)
                return
            return

        if not (SID_BASE <= addr < SID_END):
            return

        reg = addr - SID_BASE
        self._add_sid_write(addr, source, pc, reg)

    def _add_sid_write(self, addr, source, pc, reg):
        """Add a SID write record with classification."""
        reg_name = SID_REG_NAMES.get(reg, f'reg_{reg:02X}')

        if reg < 21:
            voice = reg // 7
        else:
            voice = -1

        reg_in_voice = reg % 7 if voice >= 0 else -1

        if reg_in_voice in (0, 1):
            category = 'freq'
            # If the source is a table index, it might be a freq table lookup
            if source.kind == AbsKind.TABLE_INDEX:
                source = AbsVal(kind=AbsKind.FREQ_VALUE,
                                note_source=f'table[${source.table_base:04X}+{source.index_reg}]')
        elif reg_in_voice in (2, 3):
            category = 'pulse'
        elif reg_in_voice == 4:
            category = 'waveform'
        elif reg_in_voice in (5, 6):
            category = 'adsr'
        elif reg >= 0x15:
            category = 'filter' if reg <= 0x17 else 'global'
        else:
            category = 'unknown'

        sw = SIDWrite(addr=addr, reg_name=reg_name, source=source,
                      pc=pc, voice=voice, category=category)
        self.sid_writes.append(sw)

    def _exec_one(self, state, insn):
        """Execute one instruction abstractly. Returns new state."""
        s = state.clone()
        name = insn.name
        mode = insn.mode

        # ----- Loads -----
        if name == 'LDA':
            s.A, _ = self._resolve_read(s, insn)
            self._set_nz(s, s.A)
        elif name == 'LDX':
            s.X, _ = self._resolve_read(s, insn)
            self._set_nz(s, s.X)
        elif name == 'LDY':
            s.Y, _ = self._resolve_read(s, insn)
            self._set_nz(s, s.Y)

        # ----- Stores -----
        elif name == 'STA':
            eff = self._resolve_write_addr(s, insn)
            self._record_sid_write(eff, s.A, insn.addr, s, insn)
            if eff is not None:
                s.mem[eff] = s.A
        elif name == 'STX':
            eff = self._resolve_write_addr(s, insn)
            self._record_sid_write(eff, s.X, insn.addr, s, insn)
            if eff is not None:
                s.mem[eff] = s.X
        elif name == 'STY':
            eff = self._resolve_write_addr(s, insn)
            self._record_sid_write(eff, s.Y, insn.addr, s, insn)
            if eff is not None:
                s.mem[eff] = s.Y

        # ----- Transfers -----
        elif name == 'TAX':
            s.X = s.A
            self._set_nz(s, s.X)
        elif name == 'TAY':
            s.Y = s.A
            self._set_nz(s, s.Y)
        elif name == 'TXA':
            s.A = s.X
            self._set_nz(s, s.A)
        elif name == 'TYA':
            s.A = s.Y
            self._set_nz(s, s.A)
        elif name == 'TSX':
            s.X = UNKNOWN
        elif name == 'TXS':
            s.SP = s.X

        # ----- Arithmetic -----
        elif name == 'ADC':
            val, _ = self._resolve_read(s, insn)
            if s.A.kind == AbsKind.CONCRETE and val.kind == AbsKind.CONCRETE and s.C is not None:
                carry = 1 if s.C else 0
                result = s.A.value + val.value + carry
                s.C = result > 0xFF
                s.A = concrete(result)
            else:
                desc = f'{s.A}+{val}'
                s.A = computed(desc)
                s.C = None
            self._set_nz(s, s.A)

        elif name == 'SBC':
            val, _ = self._resolve_read(s, insn)
            if s.A.kind == AbsKind.CONCRETE and val.kind == AbsKind.CONCRETE and s.C is not None:
                borrow = 0 if s.C else 1
                result = s.A.value - val.value - borrow
                s.C = result >= 0
                s.A = concrete(result)
            else:
                desc = f'{s.A}-{val}'
                s.A = computed(desc)
                s.C = None
            self._set_nz(s, s.A)

        # ----- Compare -----
        elif name == 'CMP':
            val, _ = self._resolve_read(s, insn)
            if s.A.kind == AbsKind.CONCRETE and val.kind == AbsKind.CONCRETE:
                s.C = s.A.value >= val.value
                s.Z = s.A.value == val.value
                s.N = ((s.A.value - val.value) & 0x80) != 0
            else:
                s.C = None
                s.Z = None
                s.N = None
        elif name == 'CPX':
            val, _ = self._resolve_read(s, insn)
            if s.X.kind == AbsKind.CONCRETE and val.kind == AbsKind.CONCRETE:
                s.C = s.X.value >= val.value
                s.Z = s.X.value == val.value
                s.N = ((s.X.value - val.value) & 0x80) != 0
            else:
                s.C = None
                s.Z = None
                s.N = None
        elif name == 'CPY':
            val, _ = self._resolve_read(s, insn)
            if s.Y.kind == AbsKind.CONCRETE and val.kind == AbsKind.CONCRETE:
                s.C = s.Y.value >= val.value
                s.Z = s.Y.value == val.value
                s.N = ((s.Y.value - val.value) & 0x80) != 0
            else:
                s.C = None
                s.Z = None
                s.N = None

        # ----- Logic -----
        elif name == 'AND':
            val, _ = self._resolve_read(s, insn)
            if s.A.kind == AbsKind.CONCRETE and val.kind == AbsKind.CONCRETE:
                s.A = concrete(s.A.value & val.value)
            else:
                s.A = computed(f'{s.A}&{val}')
            self._set_nz(s, s.A)
        elif name == 'ORA':
            val, _ = self._resolve_read(s, insn)
            if s.A.kind == AbsKind.CONCRETE and val.kind == AbsKind.CONCRETE:
                s.A = concrete(s.A.value | val.value)
            else:
                s.A = computed(f'{s.A}|{val}')
            self._set_nz(s, s.A)
        elif name == 'EOR':
            val, _ = self._resolve_read(s, insn)
            if s.A.kind == AbsKind.CONCRETE and val.kind == AbsKind.CONCRETE:
                s.A = concrete(s.A.value ^ val.value)
            else:
                s.A = computed(f'{s.A}^{val}')
            self._set_nz(s, s.A)

        # ----- Shifts -----
        elif name == 'ASL':
            val, _ = self._resolve_read(s, insn)
            if val.kind == AbsKind.CONCRETE:
                s.C = (val.value & 0x80) != 0
                result = concrete((val.value << 1) & 0xFF)
            else:
                result = computed(f'{val}<<1')
                s.C = None
            if mode == AddressingMode.ACCUMULATOR:
                s.A = result
            else:
                eff = self._resolve_write_addr(s, insn)
                if eff is not None:
                    s.mem[eff] = result
            self._set_nz(s, result)

        elif name == 'LSR':
            val, _ = self._resolve_read(s, insn)
            if val.kind == AbsKind.CONCRETE:
                s.C = (val.value & 0x01) != 0
                result = concrete(val.value >> 1)
            else:
                result = computed(f'{val}>>1')
                s.C = None
            if mode == AddressingMode.ACCUMULATOR:
                s.A = result
            else:
                eff = self._resolve_write_addr(s, insn)
                if eff is not None:
                    s.mem[eff] = result
            self._set_nz(s, result)

        elif name == 'ROL':
            val, _ = self._resolve_read(s, insn)
            if val.kind == AbsKind.CONCRETE and s.C is not None:
                old_c = 1 if s.C else 0
                s.C = (val.value & 0x80) != 0
                result = concrete(((val.value << 1) | old_c) & 0xFF)
            else:
                result = computed(f'ROL({val})')
                s.C = None
            if mode == AddressingMode.ACCUMULATOR:
                s.A = result
            else:
                eff = self._resolve_write_addr(s, insn)
                if eff is not None:
                    s.mem[eff] = result
            self._set_nz(s, result)

        elif name == 'ROR':
            val, _ = self._resolve_read(s, insn)
            if val.kind == AbsKind.CONCRETE and s.C is not None:
                old_c = 0x80 if s.C else 0
                s.C = (val.value & 0x01) != 0
                result = concrete((val.value >> 1) | old_c)
            else:
                result = computed(f'ROR({val})')
                s.C = None
            if mode == AddressingMode.ACCUMULATOR:
                s.A = result
            else:
                eff = self._resolve_write_addr(s, insn)
                if eff is not None:
                    s.mem[eff] = result
            self._set_nz(s, result)

        # ----- Inc/Dec -----
        elif name == 'INC':
            val, _ = self._resolve_read(s, insn)
            eff = self._resolve_write_addr(s, insn)
            if val.kind == AbsKind.CONCRETE:
                result = concrete((val.value + 1) & 0xFF)
            else:
                result = computed(f'{val}+1')
            if eff is not None:
                s.mem[eff] = result
            self._set_nz(s, result)
        elif name == 'DEC':
            val, _ = self._resolve_read(s, insn)
            eff = self._resolve_write_addr(s, insn)
            if val.kind == AbsKind.CONCRETE:
                result = concrete((val.value - 1) & 0xFF)
            else:
                result = computed(f'{val}-1')
            if eff is not None:
                s.mem[eff] = result
            self._set_nz(s, result)
        elif name == 'INX':
            if s.X.kind == AbsKind.CONCRETE:
                s.X = concrete((s.X.value + 1) & 0xFF)
            else:
                s.X = computed(f'{s.X}+1')
            self._set_nz(s, s.X)
        elif name == 'INY':
            if s.Y.kind == AbsKind.CONCRETE:
                s.Y = concrete((s.Y.value + 1) & 0xFF)
            else:
                s.Y = computed(f'{s.Y}+1')
            self._set_nz(s, s.Y)
        elif name == 'DEX':
            if s.X.kind == AbsKind.CONCRETE:
                s.X = concrete((s.X.value - 1) & 0xFF)
            else:
                s.X = computed(f'{s.X}-1')
            self._set_nz(s, s.X)
        elif name == 'DEY':
            if s.Y.kind == AbsKind.CONCRETE:
                s.Y = concrete((s.Y.value - 1) & 0xFF)
            else:
                s.Y = computed(f'{s.Y}-1')
            self._set_nz(s, s.Y)

        # ----- Flags -----
        elif name == 'SEC':
            s.C = True
        elif name == 'CLC':
            s.C = False
        elif name == 'SED':
            pass  # decimal mode — not modeled
        elif name == 'CLD':
            pass
        elif name == 'SEI':
            pass
        elif name == 'CLI':
            pass
        elif name == 'CLV':
            s.V = False

        # ----- Stack -----
        elif name == 'PHA':
            pass  # not modeled in detail
        elif name == 'PLA':
            s.A = UNKNOWN
            s.N = None
            s.Z = None
        elif name == 'PHP':
            pass
        elif name == 'PLP':
            s.C = None
            s.Z = None
            s.N = None
            s.V = None

        # ----- BIT -----
        elif name == 'BIT':
            val, _ = self._resolve_read(s, insn)
            if val.kind == AbsKind.CONCRETE:
                s.N = (val.value & 0x80) != 0
                s.V = (val.value & 0x40) != 0
                if s.A.kind == AbsKind.CONCRETE:
                    s.Z = (s.A.value & val.value) == 0
                else:
                    s.Z = None
            else:
                s.N = None
                s.V = None
                s.Z = None

        # ----- NOP -----
        elif name == 'NOP':
            pass

        return s

    def _set_nz(self, state, val):
        """Set N and Z flags from an abstract value."""
        if val.kind == AbsKind.CONCRETE:
            state.N = (val.value & 0x80) != 0
            state.Z = val.value == 0
        else:
            state.N = None
            state.Z = None

    def analyze(self, entry_addr, initial_state=None, call_depth=0):
        """Run abstract interpretation from entry_addr.

        Uses a worklist of (addr, state) pairs. At branches, explores both
        paths. At loop headers (back edges), applies widening.
        """
        if initial_state is None:
            initial_state = AbsCPUState()

        worklist = [(entry_addr, initial_state)]
        visited = defaultdict(int)  # addr -> visit count

        while worklist and self._steps < self.MAX_STEPS:
            addr, state = worklist.pop()

            # Out of bounds?
            if addr < self.load_addr or addr >= self.end_addr:
                continue

            # Loop detection: if we've visited this address too many times, widen and stop
            visited[addr] += 1
            if visited[addr] > self.MAX_LOOP_ITER:
                # Widen: set all registers to unknown and stop exploring this path
                continue

            # If we've visited with a compatible state before, merge and check for fixpoint
            if addr in self._visited_states:
                old = self._visited_states[addr]
                merged = merge_states(old, state)
                # Simple fixpoint check: if merge didn't change anything, stop
                if (merged.A == old.A and merged.X == old.X and merged.Y == old.Y):
                    continue
                state = merged

            self._visited_states[addr] = state
            self._steps += 1

            insn = disassemble_at(self.memory, self.load_addr, addr)
            if insn is None:
                continue

            # Handle control flow
            if insn.opcode == 0x60:  # RTS
                continue
            if insn.opcode == 0x40:  # RTI
                continue
            if insn.opcode == 0x00:  # BRK
                continue

            if insn.opcode == 0x4C:  # JMP absolute
                worklist.append((insn.operand, state))
                continue

            if insn.opcode == 0x6C:  # JMP indirect
                # Try to resolve pointer
                lo = self.read_byte(insn.operand)
                hi = self.read_byte(insn.operand + 1)
                if lo is not None and hi is not None:
                    target = lo | (hi << 8)
                    worklist.append((target, state))
                continue

            if insn.opcode == 0x20:  # JSR
                if call_depth < self.MAX_CALL_DEPTH:
                    # Execute subroutine with current state
                    sub_state = state.clone()
                    self.analyze(insn.operand, sub_state, call_depth + 1)
                    # After JSR, state is partially unknown (subroutine may have changed regs)
                    # Conservative: keep memory writes but reset registers
                    # Less conservative: propagate state from subroutine analysis
                    state = state.clone()
                    state.A = UNKNOWN
                    state.X = UNKNOWN
                    state.Y = UNKNOWN
                    state.C = None
                    state.Z = None
                    state.N = None
                worklist.append((addr + insn.length, state))
                continue

            if insn.opcode in _BRANCHES:
                # Conditional branch: explore both paths
                offset = insn.operand if insn.operand < 128 else insn.operand - 256
                target = addr + insn.length + offset
                new_state = self._exec_one(state, insn)  # execute for flag side effects? No, branches don't change state
                # Actually branches don't modify state, just test flags
                # But we should NOT execute the branch as an instruction
                # Fork: taken and not-taken paths both get the current state
                worklist.append((target, state.clone()))
                worklist.append((addr + insn.length, state.clone()))
                continue

            # Normal instruction: execute and continue
            state = self._exec_one(state, insn)
            worklist.append((addr + insn.length, state))

    def _classify_tables(self):
        """Classify discovered table accesses into categories based on
        which SID registers they feed into."""
        # Map: table_base -> set of SID write categories
        table_to_sid = defaultdict(set)
        for sw in self.sid_writes:
            src = sw.source
            if src.kind == AbsKind.TABLE_INDEX and src.table_base is not None:
                table_to_sid[src.table_base].add(sw.category)
            elif src.kind == AbsKind.FREQ_VALUE and src.note_source:
                # Parse "table[$XXXX+R]" format
                if 'table[' in src.note_source:
                    try:
                        base_str = src.note_source.split('$')[1].split('+')[0]
                        base = int(base_str, 16)
                        table_to_sid[base].add('freq')
                    except (IndexError, ValueError):
                        pass

        # Build table objects
        for base_addr, accesses in self.table_accesses.items():
            pcs = [pc for pc, _ in accesses]
            regs = set(r for _, r in accesses)
            idx_reg = 'X' if 'X' in regs else ('Y' if 'Y' in regs else '?')

            categories = table_to_sid.get(base_addr, set())
            if 'freq' in categories:
                label = 'freq'
            elif 'waveform' in categories:
                label = 'waveform'
            elif 'adsr' in categories:
                label = 'adsr'
            elif 'pulse' in categories:
                label = 'pulse'
            elif 'filter' in categories:
                label = 'filter'
            else:
                label = 'data'

            # Estimate size: look for another table nearby or use 256
            size_hint = 96 if label == 'freq' else 256

            self.tables.append(DataTable(
                base_addr=base_addr,
                size_hint=size_hint,
                label=label,
                accessed_by=pcs,
                index_reg=idx_reg,
            ))

        self.tables.sort(key=lambda t: t.base_addr)

    def _detect_voice_loop(self):
        """Detect the voice loop structure from SID write patterns."""
        # Check for indexed writes: STA $D400,X where X varies
        indexed_writes = [sw for sw in self.sid_writes
                          if sw.source.kind in (AbsKind.TABLE_INDEX, AbsKind.FREQ_VALUE,
                                                AbsKind.COMPUTED, AbsKind.UNKNOWN)]
        # Check if SID writes span multiple voices
        voices_seen = set(sw.voice for sw in self.sid_writes if sw.voice >= 0)

        if len(voices_seen) >= 2:
            # Check if the writes come from the same PC (indexed loop)
            write_pcs = defaultdict(set)
            for sw in self.sid_writes:
                write_pcs[sw.pc].add(sw.voice)
            multi_voice_pcs = {pc: voices for pc, voices in write_pcs.items()
                               if len(voices) >= 2}
            if multi_voice_pcs:
                return 'indexed_x'
            # Multiple voices but different PCs -> unrolled
            return 'unrolled'
        elif len(voices_seen) == 1:
            return 'separate'
        return 'unknown'

    def _detect_tempo_counter(self):
        """Try to detect the tempo counter address.

        Tempo counters are typically:
        - DEC zp / BNE skip -> a countdown that gates note processing
        - LDA zp / SBC #1 / STA zp -> same but with SBC
        """
        # Look for DEC <addr> followed by BNE in the visited states
        candidates = []
        for addr in sorted(self._visited_states.keys()):
            insn = disassemble_at(self.memory, self.load_addr, addr)
            if insn is None:
                continue
            if insn.name == 'DEC' and insn.mode in (AddressingMode.ZERO_PAGE, AddressingMode.ABSOLUTE):
                # Check if next instruction is a branch
                next_insn = disassemble_at(self.memory, self.load_addr, addr + insn.length)
                if next_insn and next_insn.opcode in _BRANCHES:
                    candidates.append(insn.operand)
        return candidates[0] if candidates else None

    def build_analysis(self):
        """Build the final DriverAnalysis from collected data."""
        self._classify_tables()
        voice_type = self._detect_voice_loop()
        tempo_addr = self._detect_tempo_counter()

        analysis = DriverAnalysis()
        analysis.sid_writes = self.sid_writes
        analysis.tables = self.tables
        analysis.voice_loop_type = voice_type
        analysis.tempo_counter_addr = tempo_addr

        # Identify freq table pair (lo, hi)
        freq_tables = [t for t in self.tables if t.label == 'freq']
        if len(freq_tables) >= 2:
            analysis.freq_table = (freq_tables[0].base_addr, freq_tables[1].base_addr)
        elif len(freq_tables) == 1:
            # Single freq table — might be lo, with hi at +96
            analysis.freq_table = (freq_tables[0].base_addr,
                                   freq_tables[0].base_addr + 96)

        # Identify other tables
        for t in self.tables:
            if t.label == 'waveform' and analysis.wave_table is None:
                analysis.wave_table = t.base_addr
            elif t.label == 'adsr' and analysis.instrument_table is None:
                analysis.instrument_table = t.base_addr
            elif t.label == 'data':
                # First unclassified data table could be pattern or orderlist
                if analysis.pattern_base is None:
                    analysis.pattern_base = t.base_addr
                elif analysis.orderlist_base is None:
                    analysis.orderlist_base = t.base_addr

        return analysis


# ---------------------------------------------------------------------------
# SID file loader
# ---------------------------------------------------------------------------

def load_sid(path):
    """Load a SID file, parse header, return (header_dict, binary, load_addr)."""
    with open(path, 'rb') as f:
        data = f.read()

    if len(data) < 124:
        raise ValueError(f"File too small: {len(data)} bytes")

    magic = data[:4]
    if magic not in (b'PSID', b'RSID'):
        raise ValueError(f"Not a SID file (magic: {magic})")

    version = struct.unpack('>H', data[4:6])[0]
    data_offset = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]
    songs = struct.unpack('>H', data[14:16])[0]
    start_song = struct.unpack('>H', data[16:18])[0]

    title = data[22:54].split(b'\x00')[0].decode('latin-1', errors='replace')
    author = data[54:86].split(b'\x00')[0].decode('latin-1', errors='replace')

    payload = data[data_offset:]
    if load_addr == 0 and len(payload) >= 2:
        load_addr = struct.unpack('<H', payload[:2])[0]
        binary = payload[2:]
    else:
        binary = payload

    header = {
        'magic': magic.decode('ascii'),
        'version': version,
        'data_offset': data_offset,
        'load_addr': load_addr,
        'init_addr': init_addr,
        'play_addr': play_addr,
        'songs': songs,
        'start_song': start_song,
        'title': title,
        'author': author,
    }

    return header, binary, load_addr


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyze_sid(path, verbose=False):
    """Analyze a SID file and return a DriverAnalysis."""
    header, binary, load_addr = load_sid(path)

    if verbose:
        print(f'"{header["title"]}" by {header["author"]}')
        print(f'  Load: ${load_addr:04X}, Size: {len(binary)} bytes')
        print(f'  Init: ${header["init_addr"]:04X}, Play: ${header["play_addr"]:04X}')
        print(f'  Songs: {header["songs"]}')

    interp = AbstractInterpreter(binary, load_addr)

    # Analyze the play routine (the main per-frame entry point)
    play_addr = header['play_addr']
    if play_addr != 0:
        if verbose:
            print(f'\nAnalyzing play routine at ${play_addr:04X}...')
        interp.analyze(play_addr)

    # Also analyze the init routine for setup (table pointers, etc.)
    init_addr = header['init_addr']
    if init_addr != 0 and init_addr != play_addr:
        if verbose:
            print(f'Analyzing init routine at ${init_addr:04X}...')
        init_state = AbsCPUState()
        init_state.A = concrete(0)  # subtune 0
        interp.analyze(init_addr, init_state)

    analysis = interp.build_analysis()

    if verbose:
        print(f'\n=== Analysis Results ===')
        print(f'Steps executed: {interp._steps}')
        print(f'Voice loop type: {analysis.voice_loop_type}')

        if analysis.freq_table:
            print(f'Freq table: lo=${analysis.freq_table[0]:04X} hi=${analysis.freq_table[1]:04X}')
        if analysis.instrument_table:
            print(f'Instrument table: ${analysis.instrument_table:04X}')
        if analysis.wave_table:
            print(f'Wave table: ${analysis.wave_table:04X}')
        if analysis.pattern_base:
            print(f'Pattern base: ${analysis.pattern_base:04X}')
        if analysis.orderlist_base:
            print(f'Orderlist base: ${analysis.orderlist_base:04X}')
        if analysis.tempo_counter_addr:
            print(f'Tempo counter: ${analysis.tempo_counter_addr:04X}')

        if analysis.sid_writes:
            print(f'\n=== SID Register Writes ({len(analysis.sid_writes)}) ===')
            # Deduplicate by (addr, source, pc)
            seen = set()
            for sw in analysis.sid_writes:
                key = (sw.addr, str(sw.source), sw.pc)
                if key in seen:
                    continue
                seen.add(key)
                print(f'  {sw}')

        if analysis.tables:
            print(f'\n=== Data Tables ({len(analysis.tables)}) ===')
            for t in analysis.tables:
                print(f'  {t}')
                for pc in t.accessed_by[:5]:
                    insn = disassemble_at(binary, load_addr, pc)
                    if insn:
                        print(f'    accessed from: {insn}')

    return analysis


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: python3 -m formal.abstract_interp <sid_file> [-v]')
        print(f'  Analyzes a SID file player code via abstract interpretation.')
        print(f'  -v: verbose output')
        sys.exit(1)

    sid_path = sys.argv[1]
    verbose = '-v' in sys.argv or '--verbose' in sys.argv

    if not os.path.exists(sid_path):
        print(f'Error: file not found: {sid_path}')
        sys.exit(1)

    analysis = analyze_sid(sid_path, verbose=verbose)

    if not verbose:
        # Brief summary
        print(f'Voice loop: {analysis.voice_loop_type}')
        if analysis.freq_table:
            print(f'Freq table: ${analysis.freq_table[0]:04X}/${analysis.freq_table[1]:04X}')
        print(f'SID writes: {len(analysis.sid_writes)}')
        print(f'Tables: {len(analysis.tables)}')
        if analysis.tempo_counter_addr:
            print(f'Tempo counter: ${analysis.tempo_counter_addr:04X}')
