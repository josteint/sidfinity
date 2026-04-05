"""
cycle_model.py — 6502 cycle counting and page-crossing analysis.

Given xa65 assembly source (as emitted by codegen_v2), this module:
1. Counts cycles per instruction with correct addressing mode detection
2. Detects page-crossing penalties for indexed and indirect addressing
3. Traces execution paths to compute per-path cycle budgets
4. Identifies the hot path (gate timer frame) and its cycle cost

This is Phase 3 of the codegen plan: formal reasoning about player timing
instead of guessing.
"""

from dataclasses import dataclass, field
import re


# =============================================================================
# 6502 instruction cycle table
# =============================================================================

# Base cycles by opcode mnemonic + addressing mode.
# Page-crossing penalty (+1) applies to: abs,X / abs,Y / (zp),Y reads.
# Writes never have page-crossing penalty (STA abs,X is always 5).
# RMW (INC/DEC/ASL/LSR/ROL/ROR abs,X) is always 7, no penalty.

CYCLES = {
    # Loads (affected by page crossing on read)
    'lda_imm': 2, 'lda_zp': 3, 'lda_zpx': 4, 'lda_abs': 4,
    'lda_absx': 4, 'lda_absy': 4, 'lda_indy': 5,
    'ldx_imm': 2, 'ldx_zp': 3, 'ldx_abs': 4, 'ldx_absy': 4,
    'ldy_imm': 2, 'ldy_zp': 3, 'ldy_zpx': 4, 'ldy_abs': 4, 'ldy_absx': 4,

    # Stores (no page-crossing penalty)
    'sta_zp': 3, 'sta_zpx': 4, 'sta_abs': 4, 'sta_absx': 5, 'sta_absy': 5, 'sta_indy': 6,
    'stx_zp': 3, 'stx_abs': 4,
    'sty_zp': 3, 'sty_abs': 4,

    # Arithmetic/logic (page crossing on read)
    'adc_imm': 2, 'adc_zp': 3, 'adc_abs': 4, 'adc_absx': 4, 'adc_absy': 4, 'adc_indy': 5,
    'sbc_imm': 2, 'sbc_zp': 3, 'sbc_abs': 4, 'sbc_absx': 4, 'sbc_absy': 4,
    'cmp_imm': 2, 'cmp_zp': 3, 'cmp_abs': 4, 'cmp_absx': 4,
    'cpx_imm': 2, 'cpx_abs': 4,
    'cpy_imm': 2, 'cpy_abs': 4,
    'and_imm': 2, 'and_zp': 3, 'and_abs': 4, 'and_absx': 4,
    'ora_imm': 2, 'ora_zp': 3, 'ora_abs': 4, 'ora_absx': 4,
    'eor_imm': 2, 'eor_zp': 3, 'eor_abs': 4, 'eor_absx': 4,

    # RMW (no page-crossing penalty — always fixed cycles)
    'inc_zp': 5, 'inc_abs': 6, 'inc_absx': 7,
    'dec_zp': 5, 'dec_abs': 6, 'dec_absx': 7,
    'asl_acc': 2, 'asl_zp': 5, 'asl_abs': 6,
    'lsr_acc': 2, 'lsr_zp': 5, 'lsr_abs': 6,
    'rol_acc': 2, 'rol_zp': 5,
    'ror_acc': 2, 'ror_zp': 5,

    # Branches (base: 2 not taken, 3 taken same page, 4 taken cross page)
    'bcc': 2, 'bcs': 2, 'beq': 2, 'bne': 2,
    'bpl': 2, 'bmi': 2, 'bvc': 2, 'bvs': 2,

    # Jumps
    'jmp_abs': 3, 'jsr': 6, 'rts': 6,

    # Implied
    'clc': 2, 'sec': 2, 'cld': 2, 'sed': 2, 'cli': 2, 'sei': 2,
    'tax': 2, 'tay': 2, 'txa': 2, 'tya': 2, 'tsx': 2, 'txs': 2,
    'pha': 3, 'pla': 4, 'php': 3, 'plp': 4,
    'inx': 2, 'iny': 2, 'dex': 2, 'dey': 2,
    'nop': 2, 'brk': 7, 'rti': 6,

    # BIT
    'bit_zp': 3, 'bit_abs': 4,
}

# Addressing modes that can have page-crossing penalty on READ
PAGE_CROSS_MODES = {'absx', 'absy', 'indy'}


@dataclass
class Instruction:
    """Parsed 6502 instruction."""
    label: str = ''          # label on this line (if any)
    mnemonic: str = ''       # e.g., 'lda'
    mode: str = ''           # e.g., 'absx', 'imm', 'abs'
    operand: str = ''        # raw operand text
    base_cycles: int = 0     # cycles without page-crossing penalty
    can_page_cross: bool = False  # True if this instruction can have +1 penalty
    bytes: int = 0           # instruction size in bytes
    comment: str = ''
    is_branch: bool = False
    branch_target: str = ''  # label name for branches/jumps


def parse_addressing_mode(mnemonic, operand):
    """Determine addressing mode from operand syntax."""
    op = operand.strip().lower()
    if not op:
        if mnemonic in ('asl', 'lsr', 'rol', 'ror'):
            return 'acc', 1
        return 'implied', 1

    if op.startswith('#'):
        return 'imm', 2
    if op.startswith('(') and op.endswith(',y'):
        return 'indy', 2
    if op.endswith(',x'):
        base = op[:-2]
        # Zero page if operand is $xx (2 hex digits)
        if re.match(r'^\$[0-9a-f]{2}$', base):
            return 'zpx', 2
        return 'absx', 3
    if op.endswith(',y'):
        base = op[:-2]
        if re.match(r'^\$[0-9a-f]{2}$', base):
            return 'zpy', 2
        return 'absy', 3
    # Zero page or absolute
    if re.match(r'^\$[0-9a-f]{2}$', op):
        return 'zp', 2
    return 'abs', 3


def parse_instruction(line):
    """Parse one line of xa65 assembly into an Instruction."""
    inst = Instruction()

    # Strip comments
    if ';' in line:
        idx = line.index(';')
        inst.comment = line[idx+1:].strip()
        line = line[:idx]

    line = line.rstrip()
    if not line.strip():
        return None

    stripped = line.strip()

    # Skip non-instructions
    if stripped.startswith('.') or stripped.startswith('#') or stripped.startswith('*'):
        return None
    if '=' in stripped and not stripped.startswith(' '):
        return None  # equate

    # Check for label: starts at column 0 (no leading whitespace)
    if line and not line[0].isspace():
        # This is a label
        label_text = stripped.split(':')[0].strip() if ':' in stripped else stripped
        inst.label = label_text
        rest = stripped[stripped.index(':')+1:].strip() if ':' in stripped else ''
        if not rest:
            return inst  # label only
        stripped = rest

    # Instruction (may be indented)
    parts = stripped.split(None, 1)
    if not parts:
        return None
    mnemonic = parts[0].lower()

    # Skip directives
    if mnemonic.startswith('.') or mnemonic.startswith('#'):
        return None

    inst.mnemonic = mnemonic
    operand = parts[1] if len(parts) > 1 else ''
    inst.operand = operand

    # Branches
    if mnemonic in ('beq', 'bne', 'bcc', 'bcs', 'bpl', 'bmi', 'bvc', 'bvs'):
        inst.is_branch = True
        inst.branch_target = operand.strip()
        inst.mode = 'branch'
        inst.base_cycles = CYCLES.get(mnemonic, 2)
        inst.bytes = 2
        return inst

    # Jumps
    if mnemonic == 'jmp':
        inst.mode = 'abs'
        inst.base_cycles = 3
        inst.bytes = 3
        inst.branch_target = operand.strip()
        return inst
    if mnemonic == 'jsr':
        inst.mode = 'abs'
        inst.base_cycles = 6
        inst.bytes = 3
        inst.branch_target = operand.strip()
        return inst

    # Normal instructions
    mode, size = parse_addressing_mode(mnemonic, operand)
    inst.mode = mode
    inst.bytes = size if mode != 'implied' else 1

    key = f'{mnemonic}_{mode}'
    inst.base_cycles = CYCLES.get(key, CYCLES.get(mnemonic, 0))

    # Page-crossing potential
    if mode in PAGE_CROSS_MODES:
        # Only reads can have page-crossing penalty
        # STA/STX/STY never have it (writes are always fixed)
        if mnemonic not in ('sta', 'stx', 'sty'):
            inst.can_page_cross = True

    return inst


def count_path_cycles(instructions, branch_taken=True):
    """Count cycles for a linear sequence of instructions.

    Args:
        instructions: list of Instruction objects
        branch_taken: whether branches are taken (affects cycle count)

    Returns:
        (base_cycles, max_page_cross_penalty, num_instructions)
    """
    total = 0
    penalty = 0
    count = 0
    for inst in instructions:
        if inst.mnemonic == '':
            continue  # label only
        c = inst.base_cycles
        if inst.is_branch:
            c = 3 if branch_taken else 2  # taken=3, not taken=2
        total += c
        if inst.can_page_cross:
            penalty += 1
        count += 1
    return total, penalty, count


def analyze_source(source):
    """Analyze xa65 assembly source. Returns list of Instruction objects."""
    instructions = []
    for line in source.split('\n'):
        inst = parse_instruction(line)
        if inst is not None:
            instructions.append(inst)
    return instructions


def find_path(instructions, start_label, end_labels):
    """Extract a linear path from start_label to any end_label.

    Returns list of Instructions in the path (following fall-through,
    stopping at branches/jumps to labels not in the path).
    """
    # Build label index
    label_idx = {}
    for i, inst in enumerate(instructions):
        if inst.label:
            label_idx[inst.label] = i

    if start_label not in label_idx:
        return []

    path = []
    i = label_idx[start_label]
    visited = set()
    while i < len(instructions):
        if i in visited:
            break
        visited.add(i)
        inst = instructions[i]
        path.append(inst)

        if inst.mnemonic == 'rts' or inst.mnemonic == 'rti':
            break
        if inst.mnemonic == 'jmp':
            if inst.branch_target in end_labels:
                break
            if inst.branch_target in label_idx:
                i = label_idx[inst.branch_target]
                continue
            break
        if inst.is_branch:
            # For path analysis, follow the NOT-taken path (fall through)
            pass
        i += 1

    return path


def report(source, song_name=''):
    """Generate a cycle analysis report for generated assembly."""
    instructions = analyze_source(source)

    # Count total instructions and bytes
    total_inst = sum(1 for i in instructions if i.mnemonic)
    total_bytes = sum(i.bytes for i in instructions if i.mnemonic)
    page_cross_ops = sum(1 for i in instructions if i.can_page_cross)

    print(f'=== Cycle Analysis{f" for {song_name}" if song_name else ""} ===')
    print(f'Instructions: {total_inst}')
    print(f'Code bytes: {total_bytes}')
    print(f'Page-cross-susceptible ops: {page_cross_ops}')
    print()

    # Analyze key paths
    paths = [
        ('Gate timer path', 'ce_getnote', {'ce_ldregs', 'ce_ldwav'}),
        ('Wave table (skip)', 'ce_wave', {'ce_wdone', 'ce_pulse'}),
        ('Pulse (skip)', 'ce_pulse', {'ce_pskip'}),
        ('Register writes', 'ce_ldregs', {'rts'}),
        ('New note init', 'ce_newn', {'ce_ldregs', 'ce_ldwav', 'ce_nnn'}),
    ]

    for name, start, ends in paths:
        path = find_path(instructions, start, ends)
        if not path:
            print(f'{name}: (not found)')
            continue
        cycles, penalty, count = count_path_cycles(path)
        print(f'{name}: {cycles} cycles base, +{penalty} max page-cross penalty, {count} instructions')

    print()

    # Full channel processing estimate (normal frame)
    # filter + channel entry + wave(skip) + pulse(skip) + gate check + loadregs
    sections = ['mt_filterexec', 'mt_execchn', 'ce_wave', 'ce_pulse', 'ce_ldregs']
    total_normal = 0
    for label in sections:
        path = find_path(instructions, label, {'rts', 'ce_wave', 'ce_pulse', 'ce_pskip'})
        c, p, n = count_path_cycles(path)
        total_normal += c

    print(f'Estimated normal frame (1 channel): ~{total_normal} cycles')
    print(f'Estimated normal frame (3 channels): ~{total_normal * 3} cycles')
    print(f'VBI budget: ~1700 cycles')
    print(f'Margin: ~{1700 - total_normal * 3} cycles')


# =============================================================================
# Test
# =============================================================================

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from gt2_to_usf import gt2_to_usf
    from codegen_v2 import generate_player
    import json

    with open('src/player/regression_registry.json') as f:
        reg = json.load(f)

    path = [e['path'] for e in reg if 'Covfefe' in e['path']][0]
    song = gt2_to_usf(path)
    src = generate_player(song)

    report(src, 'Covfefe')
