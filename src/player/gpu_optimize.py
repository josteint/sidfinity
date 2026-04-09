"""
gpu_optimize.py — Python interface to the GPU 6502 optimizer.

Feeds real V2 player code blocks to the CUDA kernel for brute-force
optimization. Uses ctypes to call the compiled gpu_6502 binary.
"""

import ctypes
import os
import random
import struct

# Load the CUDA library
GPU_LIB = os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'gpu_6502')

# Must be compiled as shared library for ctypes
GPU_SO = GPU_LIB + '.so'

# Op enum (matches gpu_6502.cu)
OP_LDA_IMM = 0; OP_LDA_MEM = 1; OP_LDX_IMM = 2; OP_LDX_MEM = 3
OP_LDY_IMM = 4; OP_LDY_MEM = 5
OP_STA_MEM = 6; OP_STX_MEM = 7; OP_STY_MEM = 8
OP_TAX = 9; OP_TAY = 10; OP_TXA = 11; OP_TYA = 12
OP_ADC_IMM = 13; OP_SBC_IMM = 14; OP_CMP_IMM = 15
OP_AND_IMM = 16; OP_ORA_IMM = 17; OP_EOR_IMM = 18
OP_ASL_A = 19; OP_LSR_A = 20; OP_ROL_A = 21; OP_ROR_A = 22
OP_SEC = 23; OP_CLC = 24
OP_INX = 25; OP_INY = 26; OP_DEX = 27; OP_DEY = 28
OP_NOP = 29

OP_NAMES = {
    OP_LDA_IMM: 'LDA #', OP_LDA_MEM: 'LDA mem', OP_LDX_IMM: 'LDX #',
    OP_LDX_MEM: 'LDX mem', OP_LDY_IMM: 'LDY #', OP_LDY_MEM: 'LDY mem',
    OP_STA_MEM: 'STA mem', OP_STX_MEM: 'STX mem', OP_STY_MEM: 'STY mem',
    OP_TAX: 'TAX', OP_TAY: 'TAY', OP_TXA: 'TXA', OP_TYA: 'TYA',
    OP_ADC_IMM: 'ADC #', OP_SBC_IMM: 'SBC #', OP_CMP_IMM: 'CMP #',
    OP_AND_IMM: 'AND #', OP_ORA_IMM: 'ORA #', OP_EOR_IMM: 'EOR #',
    OP_ASL_A: 'ASL A', OP_LSR_A: 'LSR A', OP_ROL_A: 'ROL A', OP_ROR_A: 'ROR A',
    OP_SEC: 'SEC', OP_CLC: 'CLC',
    OP_INX: 'INX', OP_INY: 'INY', OP_DEX: 'DEX', OP_DEY: 'DEY',
    OP_NOP: 'NOP',
}

CYCLE_COST = {
    OP_LDA_IMM: 2, OP_LDA_MEM: 4, OP_LDX_IMM: 2, OP_LDX_MEM: 4,
    OP_LDY_IMM: 2, OP_LDY_MEM: 4,
    OP_STA_MEM: 5, OP_STX_MEM: 4, OP_STY_MEM: 4,
    OP_TAX: 2, OP_TAY: 2, OP_TXA: 2, OP_TYA: 2,
    OP_ADC_IMM: 2, OP_SBC_IMM: 2, OP_CMP_IMM: 2,
    OP_AND_IMM: 2, OP_ORA_IMM: 2, OP_EOR_IMM: 2,
    OP_ASL_A: 2, OP_LSR_A: 2, OP_ROL_A: 2, OP_ROR_A: 2,
    OP_SEC: 2, OP_CLC: 2,
    OP_INX: 2, OP_INY: 2, OP_DEX: 2, OP_DEY: 2,
    OP_NOP: 2,
}


def format_instruction(op, operand):
    """Format an instruction for display."""
    name = OP_NAMES.get(op, '???')
    if '#' in name:
        return '%s$%02X' % (name, operand)
    elif 'mem' in name:
        return '%s[%d]' % (name, operand)
    return name


def simulate_block(instructions, initial_state):
    """Pure Python 6502 simulator for reference output generation.

    instructions: list of (op, operand) tuples
    initial_state: dict with A, X, Y, C, mem (list of 32 bytes)
    Returns: dict with A, X, Y, C, Z, N, mem, cycles
    """
    A = initial_state.get('A', 0)
    X = initial_state.get('X', 0)
    Y = initial_state.get('Y', 0)
    C = initial_state.get('C', 0)
    Z = 0; N = 0
    mem = list(initial_state.get('mem', [0] * 32))
    cycles = 0

    def set_nz(val):
        nonlocal N, Z
        N = (val >> 7) & 1
        Z = 1 if val == 0 else 0

    for op, operand in instructions:
        cycles += CYCLE_COST.get(op, 2)
        if op == OP_LDA_IMM: A = operand; set_nz(A)
        elif op == OP_LDA_MEM: A = mem[operand]; set_nz(A)
        elif op == OP_LDX_IMM: X = operand; set_nz(X)
        elif op == OP_LDX_MEM: X = mem[operand]; set_nz(X)
        elif op == OP_LDY_IMM: Y = operand; set_nz(Y)
        elif op == OP_LDY_MEM: Y = mem[operand]; set_nz(Y)
        elif op == OP_STA_MEM: mem[operand] = A
        elif op == OP_STX_MEM: mem[operand] = X
        elif op == OP_STY_MEM: mem[operand] = Y
        elif op == OP_TAX: X = A; set_nz(X)
        elif op == OP_TAY: Y = A; set_nz(Y)
        elif op == OP_TXA: A = X; set_nz(A)
        elif op == OP_TYA: A = Y; set_nz(A)
        elif op == OP_ADC_IMM:
            r = A + operand + C; A = r & 0xFF; C = 1 if r > 255 else 0; set_nz(A)
        elif op == OP_SBC_IMM:
            r = A - operand - (1 - C); A = r & 0xFF; C = 0 if r < 0 else 1; set_nz(A)
        elif op == OP_CMP_IMM:
            r = (A - operand) & 0xFF; C = 1 if A >= operand else 0; set_nz(r)
        elif op == OP_AND_IMM: A = A & operand; set_nz(A)
        elif op == OP_ORA_IMM: A = A | operand; set_nz(A)
        elif op == OP_EOR_IMM: A = A ^ operand; set_nz(A)
        elif op == OP_ASL_A: C = (A >> 7) & 1; A = (A << 1) & 0xFF; set_nz(A)
        elif op == OP_LSR_A: C = A & 1; A = A >> 1; set_nz(A)
        elif op == OP_ROL_A: oc = C; C = (A >> 7) & 1; A = ((A << 1) | oc) & 0xFF; set_nz(A)
        elif op == OP_ROR_A: oc = C; C = A & 1; A = (A >> 1) | (oc << 7); set_nz(A)
        elif op == OP_SEC: C = 1
        elif op == OP_CLC: C = 0
        elif op == OP_INX: X = (X + 1) & 0xFF; set_nz(X)
        elif op == OP_INY: Y = (Y + 1) & 0xFF; set_nz(Y)
        elif op == OP_DEX: X = (X - 1) & 0xFF; set_nz(X)
        elif op == OP_DEY: Y = (Y - 1) & 0xFF; set_nz(Y)

    return {'A': A, 'X': X, 'Y': Y, 'C': C, 'Z': Z, 'N': N, 'mem': mem, 'cycles': cycles}


def build_test_vectors(ref_instructions, num_tests=256):
    """Generate test input/output pairs by running the reference on random inputs."""
    random.seed(42)
    inputs = []
    outputs = []
    for _ in range(num_tests):
        state = {
            'A': random.randint(0, 255),
            'X': random.randint(0, 255),
            'Y': random.randint(0, 255),
            'C': random.randint(0, 1),
            'mem': [random.randint(0, 255) for _ in range(32)],
        }
        inputs.append(state)
        outputs.append(simulate_block(ref_instructions, state))
    return inputs, outputs


if __name__ == '__main__':
    # Test: find optimal sequence for SEC / SBC #$60 (note conversion)
    print('Test: optimize SEC / SBC #$60')
    ref = [(OP_SEC, 0), (OP_SBC_IMM, 0x60)]
    inputs, outputs = build_test_vectors(ref)
    ref_cycles = outputs[0]['cycles']
    print('  Reference: %d cycles' % ref_cycles)
    print('  Testing candidates with Python simulator...')

    # Quick brute-force with Python (for validation)
    best = None
    best_cy = ref_cycles
    pool = []
    for v in [0, 1, 0x60, 0x9F, 0xA0, 0xFF]:
        pool.append((OP_SBC_IMM, v))
        pool.append((OP_ADC_IMM, v))
        pool.append((OP_AND_IMM, v))
    pool.extend([(OP_SEC, 0), (OP_CLC, 0), (OP_TAX, 0), (OP_TXA, 0)])

    # Test all single instructions
    for inst in pool:
        cy = CYCLE_COST[inst[0]]
        if cy >= best_cy:
            continue
        ok = True
        for i in range(len(inputs)):
            out = simulate_block([inst], inputs[i])
            if out['A'] != outputs[i]['A']:
                ok = False
                break
        if ok:
            best = [inst]
            best_cy = cy
            print('  FOUND: %s (%d cy)' % (format_instruction(*inst), cy))

    # Test all pairs
    tested = 0
    for i1 in pool:
        for i2 in pool:
            cy = CYCLE_COST[i1[0]] + CYCLE_COST[i2[0]]
            if cy >= best_cy:
                continue
            tested += 1
            ok = True
            for i in range(min(32, len(inputs))):  # quick check first
                out = simulate_block([i1, i2], inputs[i])
                if out['A'] != outputs[i]['A']:
                    ok = False
                    break
            if ok:
                # Full check
                ok = all(simulate_block([i1, i2], inputs[i])['A'] == outputs[i]['A']
                         for i in range(len(inputs)))
                if ok:
                    best = [i1, i2]
                    best_cy = cy
                    print('  FOUND: %s / %s (%d cy)' % (
                        format_instruction(*i1), format_instruction(*i2), cy))

    print('  Tested %d pairs' % tested)
    if best:
        print('  Best: %s (%d cy, saves %d)' % (
            ' / '.join(format_instruction(*i) for i in best), best_cy, ref_cycles - best_cy))
    else:
        print('  No improvement found')
