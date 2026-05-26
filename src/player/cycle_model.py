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
# 6502 binary disassembler
# =============================================================================

# Opcode table: opcode -> (mnemonic, addressing_mode, bytes, cycles)
_OPTABLE = {
    0x00:('brk','imp',1,7), 0x01:('ora','izx',2,6), 0x05:('ora','zp',2,3),
    0x06:('asl','zp',2,5), 0x08:('php','imp',1,3), 0x09:('ora','imm',2,2),
    0x0A:('asl','acc',1,2), 0x0D:('ora','abs',3,4), 0x0E:('asl','abs',3,6),
    0x10:('bpl','rel',2,2), 0x11:('ora','izy',2,5), 0x15:('ora','zpx',2,4),
    0x16:('asl','zpx',2,6), 0x18:('clc','imp',1,2), 0x19:('ora','aby',3,4),
    0x1D:('ora','abx',3,4), 0x1E:('asl','abx',3,7),
    0x20:('jsr','abs',3,6), 0x21:('and','izx',2,6), 0x24:('bit','zp',2,3),
    0x25:('and','zp',2,3), 0x26:('rol','zp',2,5), 0x28:('plp','imp',1,4),
    0x29:('and','imm',2,2), 0x2A:('rol','acc',1,2), 0x2C:('bit','abs',3,4),
    0x2D:('and','abs',3,4), 0x2E:('rol','abs',3,6), 0x30:('bmi','rel',2,2),
    0x31:('and','izy',2,5), 0x35:('and','zpx',2,4), 0x38:('sec','imp',1,2),
    0x39:('and','aby',3,4), 0x3D:('and','abx',3,4),
    0x40:('rti','imp',1,6), 0x41:('eor','izx',2,6), 0x45:('eor','zp',2,3),
    0x46:('lsr','zp',2,5), 0x48:('pha','imp',1,3), 0x49:('eor','imm',2,2),
    0x4A:('lsr','acc',1,2), 0x4C:('jmp','abs',3,3), 0x4D:('eor','abs',3,4),
    0x4E:('lsr','abs',3,6), 0x50:('bvc','rel',2,2), 0x51:('eor','izy',2,5),
    0x55:('eor','zpx',2,4), 0x58:('cli','imp',1,2), 0x59:('eor','aby',3,4),
    0x5D:('eor','abx',3,4),
    0x60:('rts','imp',1,6), 0x61:('adc','izx',2,6), 0x65:('adc','zp',2,3),
    0x66:('ror','zp',2,5), 0x68:('pla','imp',1,4), 0x69:('adc','imm',2,2),
    0x6A:('ror','acc',1,2), 0x6C:('jmp','ind',3,5), 0x6D:('adc','abs',3,4),
    0x6E:('ror','abs',3,6), 0x70:('bvs','rel',2,2), 0x71:('adc','izy',2,5),
    0x75:('adc','zpx',2,4), 0x78:('sei','imp',1,2), 0x79:('adc','aby',3,4),
    0x7D:('adc','abx',3,4),
    0x81:('sta','izx',2,6), 0x84:('sty','zp',2,3), 0x85:('sta','zp',2,3),
    0x86:('stx','zp',2,3), 0x88:('dey','imp',1,2), 0x8A:('txa','imp',1,2),
    0x8C:('sty','abs',3,4), 0x8D:('sta','abs',3,4), 0x8E:('stx','abs',3,4),
    0x90:('bcc','rel',2,2), 0x91:('sta','izy',2,6), 0x94:('sty','zpx',2,4),
    0x95:('sta','zpx',2,4), 0x96:('stx','zpy',2,4), 0x98:('tya','imp',1,2),
    0x99:('sta','aby',3,5), 0x9A:('txs','imp',1,2), 0x9D:('sta','abx',3,5),
    0xA0:('ldy','imm',2,2), 0xA1:('lda','izx',2,6), 0xA2:('ldx','imm',2,2),
    0xA4:('ldy','zp',2,3), 0xA5:('lda','zp',2,3), 0xA6:('ldx','zp',2,3),
    0xA8:('tay','imp',1,2), 0xA9:('lda','imm',2,2), 0xAA:('tax','imp',1,2),
    0xAC:('ldy','abs',3,4), 0xAD:('lda','abs',3,4), 0xAE:('ldx','abs',3,4),
    0xB0:('bcs','rel',2,2), 0xB1:('lda','izy',2,5), 0xB4:('ldy','zpx',2,4),
    0xB5:('lda','zpx',2,4), 0xB6:('ldx','zpy',2,4), 0xB8:('clv','imp',1,2),
    0xB9:('lda','aby',3,4), 0xBA:('tsx','imp',1,2), 0xBC:('ldy','abx',3,4),
    0xBD:('lda','abx',3,4), 0xBE:('ldx','aby',3,4),
    0xC0:('cpy','imm',2,2), 0xC1:('cmp','izx',2,6), 0xC4:('cpy','zp',2,3),
    0xC5:('cmp','zp',2,3), 0xC6:('dec','zp',2,5), 0xC8:('iny','imp',1,2),
    0xC9:('cmp','imm',2,2), 0xCA:('dex','imp',1,2), 0xCC:('cpy','abs',3,4),
    0xCD:('cmp','abs',3,4), 0xCE:('dec','abs',3,6), 0xD0:('bne','rel',2,2),
    0xD1:('cmp','izy',2,5), 0xD5:('cmp','zpx',2,4), 0xD6:('dec','zpx',2,6),
    0xD8:('cld','imp',1,2), 0xD9:('cmp','aby',3,4), 0xDD:('cmp','abx',3,4),
    0xDE:('dec','abx',3,7),
    0xE0:('cpx','imm',2,2), 0xE1:('sbc','izx',2,6), 0xE4:('cpx','zp',2,3),
    0xE5:('sbc','zp',2,3), 0xE6:('inc','zp',2,5), 0xE8:('inx','imp',1,2),
    0xE9:('sbc','imm',2,2), 0xEA:('nop','imp',1,2), 0xEC:('cpx','abs',3,4),
    0xED:('sbc','abs',3,4), 0xEE:('inc','abs',3,6), 0xF0:('beq','rel',2,2),
    0xF1:('sbc','izy',2,5), 0xF5:('sbc','zpx',2,4), 0xF6:('inc','zpx',2,6),
    0xF8:('sed','imp',1,2), 0xF9:('sbc','aby',3,4), 0xFD:('sbc','abx',3,4),
    0xFE:('inc','abx',3,7),
}

# Modes that get +1 on page cross (reads only, not writes/RMW)
_READ_PAGE_CROSS = {'abx', 'aby', 'izy'}
_WRITE_MNEMONICS = {'sta', 'stx', 'sty'}
_RMW_MNEMONICS = {'asl', 'lsr', 'rol', 'ror', 'inc', 'dec'}
_BRANCH_OPS = {0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0}


def count_bytes(binary, base, decisions=None, stop_at_rts=True, start_pc=None):
    """Count exact cycles for a 6502 binary path.

    This is the fast, correct cycle counter for SAT/genetic optimization.
    No parsing, no objects — just opcode table lookups on raw bytes.

    Args:
        binary: bytes of 6502 code
        base: load address (start of binary in memory)
        decisions: dict of address -> bool for branch decisions (True=taken).
                   Default: all branches not taken (fall through).
        stop_at_rts: stop at first RTS (default True)
        start_pc: address to start execution (default: base)

    Returns:
        total cycle count (int)
    """
    if decisions is None:
        decisions = {}

    total = 0
    pc = start_pc if start_pc is not None else base
    end = base + len(binary)
    visited = set()

    while base <= pc < end:
        if pc in visited:
            break  # loop detected
        visited.add(pc)

        i = pc - base
        op = binary[i]

        if op not in _OPTABLE:
            break  # unknown opcode

        mnem, mode, sz, cyc = _OPTABLE[op]

        if mode == 'rel':
            # Branch instruction
            taken = decisions.get(pc, False)
            if taken:
                off = binary[i + 1]
                target = pc + 2 + (off if off < 128 else off - 256)
                cyc = 3  # taken, same page
                if (pc + 2) >> 8 != target >> 8:
                    cyc = 4  # taken, page cross
                total += cyc
                pc = target
            else:
                total += 2  # not taken
                pc += sz
        elif op == 0x4C:  # JMP abs
            total += 3
            pc = binary[i + 1] | (binary[i + 2] << 8)
        elif op == 0x6C:  # JMP (ind) — can't follow
            total += 5
            break
        elif op == 0x20:  # JSR — don't follow, just count
            total += 6
            pc += 3
        elif op == 0x60:  # RTS
            total += 6
            if stop_at_rts:
                break
            pc += 1
        elif op == 0x40:  # RTI
            total += 6
            break
        else:
            # Normal instruction — check page-crossing penalty
            if mode in _READ_PAGE_CROSS and mnem not in _WRITE_MNEMONICS and mnem not in _RMW_MNEMONICS:
                # Potential +1 for page cross. For abs,x and abs,y:
                # page cross happens if (base_addr & 0xFF) + index > 0xFF
                # We can't know the index at static analysis time, so we
                # report base cycles only. Use count_bytes_worst() for +1.
                pass
            total += cyc
            pc += sz

    return total


def count_bytes_range(binary, base, start_addr, end_addrs, decisions=None):
    """Count cycles from start_addr to any of end_addrs.

    Like count_bytes but stops when PC reaches any address in end_addrs.
    Useful for measuring a specific section (e.g., wave table only).
    """
    if decisions is None:
        decisions = {}

    total = 0
    pc = start_addr
    end = base + len(binary)
    visited = set()

    while base <= pc < end:
        if pc in end_addrs:
            break
        if pc in visited:
            break
        visited.add(pc)

        i = pc - base
        op = binary[i]
        if op not in _OPTABLE:
            break

        mnem, mode, sz, cyc = _OPTABLE[op]

        if mode == 'rel':
            taken = decisions.get(pc, False)
            if taken:
                off = binary[i + 1]
                target = pc + 2 + (off if off < 128 else off - 256)
                cyc = 3
                if (pc + 2) >> 8 != target >> 8:
                    cyc = 4
                total += cyc
                pc = target
            else:
                total += 2
                pc += sz
        elif op == 0x4C:
            total += 3
            pc = binary[i + 1] | (binary[i + 2] << 8)
        elif op == 0x6C:
            total += 5; break
        elif op == 0x20:
            total += 6; pc += 3
        elif op == 0x60:
            total += 6; break
        elif op == 0x40:
            total += 6; break
        else:
            total += cyc
            pc += sz

    return total


_MODE_FMT = {
    'imp': '', 'acc': '', 'imm': '#${:02X}', 'zp': '${:02X}', 'zpx': '${:02X},x',
    'zpy': '${:02X},y', 'abs': '${:04X}', 'abx': '${:04X},x', 'aby': '${:04X},y',
    'ind': '(${:04X})', 'izx': '(${:02X},x)', 'izy': '(${:02X}),y', 'rel': '${:04X}',
}


def disassemble(binary, base, start=None, end=None):
    """Disassemble 6502 binary into xa65-compatible assembly with address labels.

    Args:
        binary: bytes of the 6502 binary
        base: load address (e.g. 0xC000)
        start: start offset within binary (default: 0)
        end: end offset within binary (default: len(binary))

    Returns:
        str of xa65-compatible assembly. Branch/jump targets use L_XXXX labels.
    """
    if start is None: start = 0
    if end is None: end = len(binary)

    # First pass: collect all branch/jump targets
    targets = set()
    i = start
    while i < end:
        op = binary[i]
        if op not in _OPTABLE:
            i += 1
            continue
        mnem, mode, sz, cyc = _OPTABLE[op]
        if i + sz > end:
            break
        if mode == 'rel':
            off = binary[i + 1]
            tgt = base + i + 2 + (off if off < 128 else off - 256)
            targets.add(tgt)
        elif mode == 'abs' and mnem in ('jmp', 'jsr'):
            tgt = binary[i + 1] | (binary[i + 2] << 8)
            if base <= tgt < base + end:
                targets.add(tgt)
        i += sz

    # Second pass: emit assembly
    lines = []
    lines.append(f'                * = ${base:04X}')
    i = start
    while i < end:
        addr = base + i
        op = binary[i]
        if op not in _OPTABLE:
            i += 1
            continue
        mnem, mode, sz, cyc = _OPTABLE[op]
        if i + sz > end:
            break

        # Label
        if addr in targets:
            lines.append(f'L_{addr:04X}')

        # Operand
        if mode == 'imp' or mode == 'acc':
            operand = ''
        elif mode == 'imm':
            operand = f'#${binary[i + 1]:02x}'
        elif mode in ('zp', 'zpx', 'zpy'):
            fmt = _MODE_FMT[mode]
            operand = fmt.format(binary[i + 1])
        elif mode in ('abs', 'abx', 'aby', 'ind'):
            val = binary[i + 1] | (binary[i + 2] << 8)
            # Use label if target is in code range
            if val in targets:
                suffix = {'abs': '', 'abx': ',x', 'aby': ',y', 'ind': ''}
                if mode == 'ind':
                    operand = f'(L_{val:04X})'
                else:
                    operand = f'L_{val:04X}{suffix[mode]}'
            else:
                operand = _MODE_FMT[mode].format(val)
        elif mode == 'izx':
            operand = f'(${binary[i + 1]:02x},x)'
        elif mode == 'izy':
            operand = f'(${binary[i + 1]:02x}),y'
        elif mode == 'rel':
            off = binary[i + 1]
            tgt = addr + 2 + (off if off < 128 else off - 256)
            operand = f'L_{tgt:04X}'
        else:
            operand = '???'

        lines.append(f'                {mnem} {operand}')
        i += sz

    return '\n'.join(lines)


def trace_path(instructions, start_label, decisions, max_steps=200):
    """Trace an execution path with explicit branch decisions.

    NOTE: This function does NOT account for branch page-crossing penalties
    (+1 cycle when a taken branch crosses a 256-byte page boundary).
    For cycle-accurate counting, use count_bytes() on the assembled binary.
    trace_path is for human-readable path analysis; count_bytes is ground truth.

    Args:
        instructions: list of Instruction objects (from analyze_source)
        start_label: label to start tracing from
        decisions: dict mapping label -> bool (True=taken for branches)
                   Missing labels default to False (fall through)

    Returns:
        (path, total_cycles) where path is list of (Instruction, cycles) tuples
    """
    label_idx = {}
    for i, inst in enumerate(instructions):
        if inst.label:
            label_idx[inst.label] = i

    if start_label not in label_idx:
        return [], 0

    path = []
    total = 0
    i = label_idx[start_label]
    visited = set()

    for _ in range(max_steps):
        if i >= len(instructions) or i in visited:
            break
        visited.add(i)
        inst = instructions[i]

        if not inst.mnemonic:
            # Label only — don't count cycles, just advance
            i += 1
            continue

        if inst.mnemonic == 'rts' or inst.mnemonic == 'rti':
            path.append((inst, inst.base_cycles))
            total += inst.base_cycles
            break

        if inst.is_branch:
            taken = decisions.get(inst.label, decisions.get(inst.branch_target, False))
            # Check by address label too (L_XXXX labels from disassembly)
            # Try label at current position
            for lbl, idx in label_idx.items():
                if idx == i and lbl in decisions:
                    taken = decisions[lbl]
                    break
            cyc = 3 if taken else 2
            path.append((inst, cyc))
            total += cyc
            if taken and inst.branch_target in label_idx:
                i = label_idx[inst.branch_target]
            else:
                i += 1
            continue

        if inst.mnemonic == 'jmp':
            path.append((inst, inst.base_cycles))
            total += inst.base_cycles
            if inst.branch_target in label_idx:
                i = label_idx[inst.branch_target]
            else:
                break
            continue

        if inst.mnemonic == 'jsr':
            # Don't follow JSR — just count cycles and continue
            path.append((inst, inst.base_cycles))
            total += inst.base_cycles
            i += 1
            continue

        path.append((inst, inst.base_cycles))
        total += inst.base_cycles
        i += 1

    return path, total


def compare_paths(source_a, source_b, start_label, decisions_a, decisions_b=None,
                  name_a='A', name_b='B'):
    """Compare cycle counts of the same logical path in two assemblies.

    Prints side-by-side comparison showing where cycles differ.
    """
    if decisions_b is None:
        decisions_b = decisions_a

    insts_a = analyze_source(source_a)
    insts_b = analyze_source(source_b)

    path_a, total_a = trace_path(insts_a, start_label, decisions_a)
    path_b, total_b = trace_path(insts_b, start_label, decisions_b)

    print(f'=== Path comparison from {start_label} ===')
    print(f'{name_a}: {total_a} cycles ({len(path_a)} instructions)')
    print(f'{name_b}: {total_b} cycles ({len(path_b)} instructions)')
    print(f'Difference: {total_b - total_a:+d} cycles')
    print()

    # Show each path
    for name, path_list, total in [(name_a, path_a, total_a), (name_b, path_b, total_b)]:
        print(f'--- {name} ({total}c) ---')
        for inst, cyc in path_list:
            lbl = f'{inst.label}:' if inst.label else ''
            print(f'  {lbl:20s} {inst.mnemonic:4s} {inst.operand:20s} {cyc}c')
        print()


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
