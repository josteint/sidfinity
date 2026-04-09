"""
z3_synth.py — Synthesize cycle-optimal 6502 instruction sequences.

Given a reference instruction sequence and its required outputs,
searches for equivalent sequences with MINIMUM cycle count.

Strategy: enumerate candidate sequences by ascending cycle count,
verify each against the reference using Z3.
"""

import sys
import os
import itertools
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'z3_lib'))

from z3_6502 import CPUState, execute, equivalent, INSTRUCTIONS, verify_equivalence


# =============================================================================
# Candidate generation
# =============================================================================

# Instructions available for synthesis, grouped by what they do
SYNTH_OPS = {
    # Loads — parameterized by operand
    'lda_imm': ('lda', 'imm'),
    'ldx_imm': ('ldx', 'imm'),
    'ldy_imm': ('ldy', 'imm'),
    'lda_mem': ('lda', 'abs'),
    'ldx_mem': ('ldx', 'abs'),
    'ldy_mem': ('ldy', 'abs'),
    # Stores
    'sta_mem': ('sta', 'abs'),
    'stx_mem': ('stx', 'abs'),
    'sty_mem': ('sty', 'abs'),
    # Transfers
    'tax': ('tax', 'impl'),
    'tay': ('tay', 'impl'),
    'txa': ('txa', 'impl'),
    'tya': ('tya', 'impl'),
    # Arithmetic
    'adc_imm': ('adc', 'imm'),
    'sbc_imm': ('sbc', 'imm'),
    'and_imm': ('and', 'imm'),
    'ora_imm': ('ora', 'imm'),
    'eor_imm': ('eor', 'imm'),
    # Flags
    'sec': ('sec', 'impl'),
    'clc': ('clc', 'impl'),
    # Shifts
    'asl_a': ('asl', 'acc'),
    'lsr_a': ('lsr', 'acc'),
    'rol_a': ('rol', 'acc'),
    'ror_a': ('ror', 'acc'),
    # Inc/Dec
    'inx': ('inx', 'impl'),
    'iny': ('iny', 'impl'),
    'dex': ('dex', 'impl'),
    'dey': ('dey', 'impl'),
}


def get_cycle_count(mnem, mode):
    """Get cycle count for an instruction."""
    return INSTRUCTIONS.get((mnem, mode), (0, 0))[1]


def synthesize(ref_instructions, outputs, mem_operands=None,
               imm_values=None, max_length=None, max_cycles=None,
               timeout_per_candidate=5):
    """Find an equivalent instruction sequence with fewer cycles.

    Args:
        ref_instructions: [(mnemonic, mode, operand), ...] — the reference
        outputs: [('reg', 'A'), ('mem', 'addr'), ('flag', 'C'), ...] — what must match
        mem_operands: list of memory location names used in the code
        imm_values: list of immediate values to try (None = [0, 1, 0xFF, ...])
        max_length: max instructions in candidate (default: len(ref))
        max_cycles: only search for candidates with fewer cycles than this
        timeout_per_candidate: Z3 timeout in seconds

    Returns:
        (best_sequence, best_cycles) or (None, ref_cycles) if no improvement
    """
    # Calculate reference cycle count
    ref_cycles = sum(get_cycle_count(m, mode) for m, mode, _ in ref_instructions)
    if max_cycles is None:
        max_cycles = ref_cycles
    if max_length is None:
        max_length = len(ref_instructions) + 2  # allow slightly longer

    # Determine operands to use
    if mem_operands is None:
        mem_operands = list(set(op for _, mode, op in ref_instructions
                               if mode in ('abs', 'absx', 'zp') and op is not None))
    if imm_values is None:
        # Extract immediate values from reference + common values
        imm_values = list(set([0, 1, 2, 3, 0xFF, 0xFE, 0x80, 0x7F] +
                              [op for _, mode, op in ref_instructions
                               if mode == 'imm' and isinstance(op, int)]))

    print(f'Synthesizing: {len(ref_instructions)} instructions, {ref_cycles} cycles')
    print(f'  Outputs: {outputs}')
    print(f'  Memory operands: {mem_operands}')
    print(f'  Immediate values: {imm_values}')
    print(f'  Max length: {max_length}, target < {max_cycles} cycles')

    # Build candidate instruction pool
    pool = []
    for name, (mnem, mode) in SYNTH_OPS.items():
        cycles = get_cycle_count(mnem, mode)
        if mode == 'imm':
            for v in imm_values:
                pool.append(((mnem, mode, v), cycles))
        elif mode in ('abs', 'absx', 'zp'):
            for addr in mem_operands:
                pool.append(((mnem, mode, addr), cycles))
        elif mode in ('impl', 'acc'):
            pool.append(((mnem, mode, None), cycles))

    print(f'  Candidate pool: {len(pool)} instructions')

    def format_seq(seq):
        return ' / '.join(f'{m} {mode} {op}' if op is not None else f'{m}'
                          for m, mode, op in seq)

    best = None
    best_cycles = max_cycles
    tested = 0

    # Search by ascending length, pruned by cycle count
    for length in range(1, max_length + 1):
        print(f'  Searching length {length}...')

        # Generate candidates: only try ordered sequences (no permutations)
        # For each position, pick from pool. Prune by running cycle total.
        count_at_length = 0

        def search(seq, cycles_so_far):
            nonlocal best, best_cycles, tested, count_at_length
            if len(seq) == length:
                if cycles_so_far >= best_cycles:
                    return
                tested += 1
                count_at_length += 1
                if tested > 50000:
                    return
                try:
                    ok, _ = verify_equivalence(
                        ref_instructions, seq, [], outputs)
                    if ok and cycles_so_far < best_cycles:
                        best = list(seq)
                        best_cycles = cycles_so_far
                        print(f'  FOUND: {format_seq(best)} ({best_cycles} cycles)')
                except Exception:
                    pass
                return
            # Prune: remaining slots need at least 2 cycles each
            min_remaining = (length - len(seq)) * 2
            if cycles_so_far + min_remaining >= best_cycles:
                return
            for inst, cy in pool:
                if tested > 50000:
                    return
                search(seq + [inst], cycles_so_far + cy)

        search([], 0)
        print(f'    Tested {count_at_length} at length {length}')
        if tested > 50000:
            print(f'  Search limit reached ({tested} total)')
            break

    if best:
        savings = ref_cycles - best_cycles
        print(f'\nBest: {best_cycles} cycles (saves {savings})')
    else:
        print(f'\nNo improvement found (ref: {ref_cycles} cycles)')

    return best, best_cycles


# =============================================================================
# Analyze V2 player code blocks
# =============================================================================

def analyze_player_blocks():
    """Identify code blocks in the V2 player that could be optimized."""

    # Block 1: New note init — LDA #0 / STA sequence
    # Current: LDA #0 (2cy) / STA mt_chnfx,x (5cy) / STA mt_chnnewnote,x (5cy) = 12 cycles
    # Can we do better?
    print('='*60)
    print('Block 1: Clear two channel variables')
    print('='*60)
    ref = [
        ('lda', 'imm', 0),
        ('sta', 'abs', 'mt_chnfx'),
        ('sta', 'abs', 'mt_chnnewnote'),
    ]
    outputs = [('mem', 'mt_chnfx'), ('mem', 'mt_chnnewnote')]
    best, cycles = synthesize(ref, outputs,
                              mem_operands=['mt_chnfx', 'mt_chnnewnote'],
                              max_length=3)

    # Block 2: SEC / SBC #NOTE pattern
    # Current: SEC (2cy) / SBC #$60 (2cy) = 4 cycles
    print('\n' + '='*60)
    print('Block 2: SEC / SBC #NOTE')
    print('='*60)
    ref = [
        ('sec', 'impl', None),
        ('sbc', 'imm', 0x60),
    ]
    # Output: A = input_A - 0x60 (with carry set)
    outputs = [('reg', 'A')]
    best, cycles = synthesize(ref, outputs, max_length=2)

    # Block 3: Frequency table lookup (16-bit)
    # Current: TAY (2cy) / LDA mt_freqtbllo,y (4cy) / STA mt_chnfreqlo,x (5cy)
    #          / LDA mt_freqtblhi,y (4cy) / STA mt_chnfreqhi,x (5cy) = 20 cycles
    print('\n' + '='*60)
    print('Block 3: Freq table lookup (16-bit)')
    print('='*60)
    ref = [
        ('tay', 'impl', None),
        ('lda', 'abs', 'mt_freqtbllo_y'),
        ('sta', 'abs', 'mt_chnfreqlo'),
        ('lda', 'abs', 'mt_freqtblhi_y'),
        ('sta', 'abs', 'mt_chnfreqhi'),
    ]
    outputs = [('mem', 'mt_chnfreqlo'), ('mem', 'mt_chnfreqhi')]
    # This is already minimal — 5 instructions for 2 table lookups + 2 stores + 1 transfer
    best, cycles = synthesize(ref, outputs,
                              mem_operands=['mt_freqtbllo_y', 'mt_freqtblhi_y',
                                            'mt_chnfreqlo', 'mt_chnfreqhi'],
                              max_length=5)


if __name__ == '__main__':
    # Quick test: just Block 1 with minimal pool
    print('Block 1: Clear two channel variables')
    ref = [
        ('lda', 'imm', 0),
        ('sta', 'abs', 'mt_chnfx'),
        ('sta', 'abs', 'mt_chnnewnote'),
    ]
    outputs = [('mem', 'mt_chnfx'), ('mem', 'mt_chnnewnote')]
    best, cycles = synthesize(ref, outputs,
                              mem_operands=['mt_chnfx', 'mt_chnnewnote'],
                              imm_values=[0],  # only 0 needed
                              max_length=3)
