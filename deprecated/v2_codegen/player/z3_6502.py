"""
z3_6502.py — 6502 CPU model for Z3 SMT synthesis.

Models the 6502 CPU state (A, X, Y, SP, flags, memory) as Z3 bit-vectors.
Given a reference instruction sequence and its input/output behavior, finds
equivalent sequences with MINIMUM CYCLE COUNT (bytes don't matter).

Usage:
    model = CPU6502()
    state = model.init_state()
    state = model.execute(state, 'lda', '#0')
    state = model.execute(state, 'sta', 'mt_chnfx,x')
    # ... then use Z3 to find equivalent with fewer cycles
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'z3_lib'))

from z3 import *

# =============================================================================
# 6502 instruction definitions: (mnemonic, mode, bytes, cycles)
# =============================================================================

# Cycle counts for common addressing modes
# Page-crossing penalty is NOT modeled (it's data-dependent)
INSTRUCTIONS = {
    # Loads
    ('lda', 'imm'): (2, 2), ('lda', 'zp'): (2, 3), ('lda', 'abs'): (3, 4),
    ('lda', 'absx'): (3, 4), ('lda', 'absy'): (3, 4), ('lda', 'indy'): (2, 5),
    ('ldx', 'imm'): (2, 2), ('ldx', 'zp'): (2, 3), ('ldx', 'abs'): (3, 4),
    ('ldy', 'imm'): (2, 2), ('ldy', 'zp'): (2, 3), ('ldy', 'abs'): (3, 4),
    # Stores
    ('sta', 'zp'): (2, 3), ('sta', 'abs'): (3, 4), ('sta', 'absx'): (3, 5),
    ('stx', 'zp'): (2, 3), ('stx', 'abs'): (3, 4),
    ('sty', 'zp'): (2, 3), ('sty', 'abs'): (3, 4),
    # Arithmetic
    ('adc', 'imm'): (2, 2), ('adc', 'zp'): (2, 3), ('adc', 'abs'): (3, 4),
    ('adc', 'absx'): (3, 4),
    ('sbc', 'imm'): (2, 2), ('sbc', 'zp'): (2, 3), ('sbc', 'abs'): (3, 4),
    ('sbc', 'absx'): (3, 4),
    # Compare
    ('cmp', 'imm'): (2, 2), ('cmp', 'zp'): (2, 3), ('cmp', 'abs'): (3, 4),
    ('cpx', 'imm'): (2, 2), ('cpy', 'imm'): (2, 2),
    # Logic
    ('and', 'imm'): (2, 2), ('and', 'zp'): (2, 3), ('and', 'abs'): (3, 4),
    ('ora', 'imm'): (2, 2), ('ora', 'zp'): (2, 3), ('ora', 'abs'): (3, 4),
    ('eor', 'imm'): (2, 2), ('eor', 'zp'): (2, 3), ('eor', 'abs'): (3, 4),
    # Shifts
    ('asl', 'acc'): (1, 2), ('asl', 'zp'): (2, 5),
    ('lsr', 'acc'): (1, 2), ('lsr', 'zp'): (2, 5),
    ('rol', 'acc'): (1, 2), ('rol', 'zp'): (2, 5),
    ('ror', 'acc'): (1, 2), ('ror', 'zp'): (2, 5),
    # Inc/Dec
    ('inc', 'zp'): (2, 5), ('inc', 'abs'): (3, 6),
    ('dec', 'zp'): (2, 5), ('dec', 'abs'): (3, 6),
    ('inx', 'impl'): (1, 2), ('iny', 'impl'): (1, 2),
    ('dex', 'impl'): (1, 2), ('dey', 'impl'): (1, 2),
    # Transfer
    ('tax', 'impl'): (1, 2), ('tay', 'impl'): (1, 2),
    ('txa', 'impl'): (1, 2), ('tya', 'impl'): (1, 2),
    # Flags
    ('sec', 'impl'): (1, 2), ('clc', 'impl'): (1, 2),
    ('sed', 'impl'): (1, 2), ('cld', 'impl'): (1, 2),
    # Stack
    ('pha', 'impl'): (1, 3), ('pla', 'impl'): (1, 4),
    # NOP
    ('nop', 'impl'): (1, 2),
    # BIT
    ('bit', 'zp'): (2, 3), ('bit', 'abs'): (3, 4),
}


class CPUState:
    """Symbolic 6502 CPU state using Z3 bit-vectors."""

    def __init__(self, prefix=''):
        p = prefix
        self.A = BitVec(f'{p}A', 8)
        self.X = BitVec(f'{p}X', 8)
        self.Y = BitVec(f'{p}Y', 8)
        self.C = Bool(f'{p}C')   # carry
        self.Z = Bool(f'{p}Z')   # zero
        self.N = Bool(f'{p}N')   # negative
        self.V = Bool(f'{p}V')   # overflow
        # Memory: model as a dict of symbolic values
        # Only track locations that are read/written
        self.mem = {}
        self.cycles = 0

    def clone(self, prefix=''):
        """Create a copy with new symbolic names."""
        s = CPUState(prefix)
        s.A = self.A
        s.X = self.X
        s.Y = self.Y
        s.C = self.C
        s.Z = self.Z
        s.N = self.N
        s.V = self.V
        s.mem = dict(self.mem)
        s.cycles = self.cycles
        return s

    def set_nz(self, val):
        """Set N and Z flags from an 8-bit value."""
        self.N = Extract(7, 7, val) == 1
        self.Z = val == 0


def execute(state, mnemonic, mode, operand=None):
    """Execute one instruction on a symbolic state. Returns new state.

    operand: for immediate mode, a concrete value or Z3 BitVec.
             for memory modes, a string key into state.mem.
    """
    s = state.clone()
    op = mnemonic.lower()
    info = INSTRUCTIONS.get((op, mode))
    if info:
        s.cycles += info[1]

    # Helper: read operand value
    def read_val():
        if mode == 'imm':
            return operand if isinstance(operand, BitVecRef) else BitVecVal(operand, 8)
        elif mode in ('zp', 'abs', 'absx', 'absy', 'indy'):
            return s.mem.get(operand, BitVec(f'mem_{operand}', 8))
        elif mode == 'acc':
            return s.A
        return BitVecVal(0, 8)

    # Helper: write value to destination
    def write_val(val):
        if mode in ('zp', 'abs', 'absx', 'absy', 'indy'):
            s.mem[operand] = val
        elif mode == 'acc':
            s.A = val

    if op == 'lda':
        s.A = read_val()
        s.set_nz(s.A)
    elif op == 'ldx':
        s.X = read_val()
        s.set_nz(s.X)
    elif op == 'ldy':
        s.Y = read_val()
        s.set_nz(s.Y)
    elif op == 'sta':
        s.mem[operand] = s.A
    elif op == 'stx':
        s.mem[operand] = s.X
    elif op == 'sty':
        s.mem[operand] = s.Y
    elif op == 'tax':
        s.X = s.A
        s.set_nz(s.X)
    elif op == 'tay':
        s.Y = s.A
        s.set_nz(s.Y)
    elif op == 'txa':
        s.A = s.X
        s.set_nz(s.A)
    elif op == 'tya':
        s.A = s.Y
        s.set_nz(s.A)
    elif op == 'adc':
        val = read_val()
        carry = If(s.C, BitVecVal(1, 8), BitVecVal(0, 8))
        result16 = ZeroExt(8, s.A) + ZeroExt(8, val) + ZeroExt(8, carry)
        result = Extract(7, 0, result16)
        s.C = Extract(8, 8, result16) == 1
        s.V = And(Extract(7, 7, s.A ^ val) == 0,
                  Extract(7, 7, s.A ^ result) == 1)
        s.A = result
        s.set_nz(s.A)
    elif op == 'sbc':
        val = read_val()
        borrow = If(s.C, BitVecVal(0, 8), BitVecVal(1, 8))
        result16 = ZeroExt(8, s.A) - ZeroExt(8, val) - ZeroExt(8, borrow)
        result = Extract(7, 0, result16)
        s.C = Not(Extract(8, 8, result16) == 1)  # carry = NOT borrow
        s.V = And(Extract(7, 7, s.A ^ val) == 1,
                  Extract(7, 7, s.A ^ result) == 1)
        s.A = result
        s.set_nz(s.A)
    elif op == 'cmp':
        val = read_val()
        result = s.A - val
        s.C = UGE(s.A, val)
        s.set_nz(result)
    elif op == 'cpx':
        val = read_val()
        result = s.X - val
        s.C = UGE(s.X, val)
        s.set_nz(result)
    elif op == 'cpy':
        val = read_val()
        result = s.Y - val
        s.C = UGE(s.Y, val)
        s.set_nz(result)
    elif op == 'and':
        s.A = s.A & read_val()
        s.set_nz(s.A)
    elif op == 'ora':
        s.A = s.A | read_val()
        s.set_nz(s.A)
    elif op == 'eor':
        s.A = s.A ^ read_val()
        s.set_nz(s.A)
    elif op == 'asl':
        val = read_val()
        s.C = Extract(7, 7, val) == 1
        result = val << 1
        write_val(result)
        s.set_nz(result)
    elif op == 'lsr':
        val = read_val()
        s.C = Extract(0, 0, val) == 1
        result = LShR(val, 1)
        write_val(result)
        s.set_nz(result)
    elif op == 'rol':
        val = read_val()
        old_c = If(s.C, BitVecVal(1, 8), BitVecVal(0, 8))
        s.C = Extract(7, 7, val) == 1
        result = (val << 1) | old_c
        write_val(result)
        s.set_nz(result)
    elif op == 'ror':
        val = read_val()
        old_c = If(s.C, BitVecVal(0x80, 8), BitVecVal(0, 8))
        s.C = Extract(0, 0, val) == 1
        result = LShR(val, 1) | old_c
        write_val(result)
        s.set_nz(result)
    elif op == 'inc':
        val = read_val() + 1
        s.mem[operand] = val
        s.set_nz(val)
    elif op == 'dec':
        val = read_val() - 1
        s.mem[operand] = val
        s.set_nz(val)
    elif op == 'inx':
        s.X = s.X + 1
        s.set_nz(s.X)
    elif op == 'iny':
        s.Y = s.Y + 1
        s.set_nz(s.Y)
    elif op == 'dex':
        s.X = s.X - 1
        s.set_nz(s.X)
    elif op == 'dey':
        s.Y = s.Y - 1
        s.set_nz(s.Y)
    elif op == 'sec':
        s.C = True
    elif op == 'clc':
        s.C = False
    elif op == 'pha':
        pass  # stack push — not modeled in detail
    elif op == 'pla':
        pass  # stack pop — not modeled in detail
    elif op == 'nop':
        pass
    elif op == 'bit':
        val = read_val()
        s.N = Extract(7, 7, val) == 1
        s.V = Extract(6, 6, val) == 1
        s.Z = (s.A & val) == 0

    return s


def equivalent(state1, state2, outputs):
    """Check if two states are equivalent on the specified outputs.

    outputs: list of ('reg', 'A') or ('mem', 'addr') or ('flag', 'C') etc.
    Returns a list of Z3 constraints that must all be satisfied.
    """
    constraints = []
    for kind, name in outputs:
        if kind == 'reg':
            if name == 'A':
                constraints.append(state1.A == state2.A)
            elif name == 'X':
                constraints.append(state1.X == state2.X)
            elif name == 'Y':
                constraints.append(state1.Y == state2.Y)
        elif kind == 'mem':
            v1 = state1.mem.get(name, BitVec(f'undef1_{name}', 8))
            v2 = state2.mem.get(name, BitVec(f'undef2_{name}', 8))
            constraints.append(v1 == v2)
        elif kind == 'flag':
            if name == 'C':
                constraints.append(state1.C == state2.C)
            elif name == 'Z':
                constraints.append(state1.Z == state2.Z)
            elif name == 'N':
                constraints.append(state1.N == state2.N)
    return constraints


def verify_equivalence(ref_instructions, candidate_instructions, inputs, outputs):
    """Verify that two instruction sequences produce the same outputs
    for ALL possible initial states.

    ref_instructions: [(mnemonic, mode, operand), ...]
    candidate_instructions: same format
    inputs: not used (both start from universally quantified state)
    outputs: what must match (list of (kind, name))

    Returns (True, candidate_cycles) if equivalent, (False, None) if not.
    """
    # Create ONE shared initial state — both sequences start from it
    init = CPUState('s_')

    # Execute reference from init
    ref = init.clone()
    for mnem, mode, operand in ref_instructions:
        ref = execute(ref, mnem, mode, operand)

    # Execute candidate from init (same starting state)
    cand = init.clone()
    for mnem, mode, operand in candidate_instructions:
        cand = execute(cand, mnem, mode, operand)

    # Check: for ANY initial state, do the outputs differ?
    eq = equivalent(ref, cand, outputs)
    if not eq:
        return True, cand.cycles  # no outputs to check

    solver = Solver()
    solver.set('timeout', 5000)  # 5 second timeout
    solver.add(Not(And(*eq)))  # look for counterexample

    result = solver.check()
    if result == unsat:
        return True, cand.cycles  # no counterexample → equivalent for all inputs
    else:
        return False, None


# =============================================================================
# Quick test
# =============================================================================

if __name__ == '__main__':
    # Test: LDA #0 / STA addr should be equivalent to LDA #0 / STA addr
    ref = [('lda', 'imm', 0), ('sta', 'abs', 'test_addr')]
    cand = [('lda', 'imm', 0), ('sta', 'abs', 'test_addr')]
    ok, cycles = verify_equivalence(ref, cand, [], [('mem', 'test_addr')])
    print(f'Identity test: equivalent={ok}, cycles={cycles}')

    # Test: SEC / LDA #5 / SBC #1 vs LDA #4 (result should be same in A)
    ref = [('sec', 'impl', None), ('lda', 'imm', 5), ('sbc', 'imm', 1)]
    cand = [('lda', 'imm', 4)]
    ok, cycles = verify_equivalence(ref, cand, [], [('reg', 'A')])
    print(f'SEC/LDA/SBC vs LDA: equivalent={ok} (A only, ignoring flags)')

    # Same but also check carry flag
    ok2, _ = verify_equivalence(ref, cand, [], [('reg', 'A'), ('flag', 'C')])
    print(f'SEC/LDA/SBC vs LDA: equivalent={ok2} (A + carry)')

    print(f'\nRef cycles: {ref[0]}: 2 + {ref[1]}: 2 + {ref[2]}: 2 = 6')
    print(f'Cand cycles: {cand[0]}: 2 = 2')
    print(f'Cycle savings: 4')
