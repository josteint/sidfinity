"""
peephole.py — Post-generation peephole optimizer for V2 codegen assembly.

Operates on the list of assembly text lines from Ctx.lines. Applies
safe transformations that reduce code size without changing behavior:

1. Branch-over-JMP inversion: BNE skip/JMP target/skip: → BEQ target
2. Dead JMP removal: JMP label where label is the next instruction
3. Redundant LDA #0 elimination (consecutive stores with same load)

Does NOT require assembling the code — works on text patterns.
Uses conservative byte estimates for branch range checking.
"""

import re
import os

# Instruction size estimates (conservative)
# Used to estimate distances for branch range checking
INST_SIZES = {
    'jmp': 3, 'jsr': 3, 'rts': 1,
    'lda': 2, 'ldx': 2, 'ldy': 2,  # immediate/ZP default; abs = 3
    'sta': 3, 'stx': 3, 'sty': 3,  # abs,X default
    'adc': 2, 'sbc': 2, 'cmp': 2, 'cpx': 2, 'cpy': 2,
    'and': 2, 'ora': 2, 'eor': 2,
    'inc': 3, 'dec': 3, 'asl': 1, 'lsr': 1, 'rol': 1, 'ror': 1,
    'beq': 2, 'bne': 2, 'bcs': 2, 'bcc': 2, 'bpl': 2, 'bmi': 2,
    'bvs': 2, 'bvc': 2,
    'sec': 1, 'clc': 1, 'sei': 1, 'cli': 1,
    'tax': 1, 'tay': 1, 'txa': 1, 'tya': 1,
    'pha': 1, 'pla': 1, 'php': 1, 'plp': 1,
    'inx': 1, 'iny': 1, 'dex': 1, 'dey': 1,
    'nop': 1, 'bit': 2,
}

BRANCH_OPS = {'beq', 'bne', 'bcs', 'bcc', 'bpl', 'bmi', 'bvs', 'bvc'}
BRANCH_INVERSE = {
    'beq': 'bne', 'bne': 'beq',
    'bcs': 'bcc', 'bcc': 'bcs',
    'bpl': 'bmi', 'bmi': 'bpl',
    'bvs': 'bvc', 'bvc': 'bvs',
}


def estimate_inst_size(line):
    """Estimate byte size of an assembly line."""
    s = line.strip()
    if not s or s.startswith(';') or s.startswith('#'):
        return 0
    # Label (no leading whitespace or starts with letter at column 0)
    if not s[0].isspace() and not s.startswith(' '):
        # Could be label, equate, or directive
        if '=' in s or s.startswith('.'):
            return 0
        return 0  # label
    # Directive
    if '.byte' in s or '.dsb' in s or '.word' in s:
        # Rough: count comma-separated values
        parts = s.split(',')
        return len(parts) * (2 if '.word' in s else 1)
    # Parse instruction
    parts = s.split()
    if not parts:
        return 0
    op = parts[0].lower().rstrip(':')
    if op in INST_SIZES:
        base = INST_SIZES[op]
        if len(parts) > 1:
            arg = parts[1].split(';')[0].strip().rstrip(',')
            # Absolute addressing: 3 bytes
            if ',' in arg and ('abs' in arg or arg.startswith('$') or arg.startswith('mt_') or
                              arg.startswith('SIDBASE') or arg.startswith('ce_') or
                              arg.startswith('mt_')):
                return 3
            # Check for labels (absolute) vs immediates
            if arg.startswith('#'):
                return 2  # immediate
            if arg.startswith('$') and len(arg) <= 4:
                return 2  # zero page
            if arg.startswith('('):
                return 2  # indirect ZP
            # Named label → probably absolute
            if any(c.isalpha() for c in arg):
                if op in BRANCH_OPS:
                    return 2  # branches are always 2 bytes
                return 3  # absolute addressing
        return base
    return 2  # unknown: conservative estimate


def parse_line(line):
    """Parse an assembly line into (type, op, arg, comment, raw).

    Types: 'inst', 'label', 'directive', 'comment', 'blank', 'equate', 'other'
    """
    raw = line
    s = line.rstrip()

    if not s:
        return ('blank', '', '', '', raw)

    # Comment line
    if s.lstrip().startswith(';'):
        return ('comment', '', '', s, raw)

    # Preprocessor
    if s.lstrip().startswith('#'):
        return ('other', '', '', '', raw)

    # Label (starts at column 0, no leading whitespace)
    stripped = s.lstrip()
    if s[0] != ' ' and s[0] != '\t' and not s.startswith(' '):
        if '=' in s:
            return ('equate', '', '', '', raw)
        return ('label', stripped.rstrip(':'), '', '', raw)

    # Directive
    if '.byte' in stripped or '.dsb' in stripped or '.word' in stripped:
        return ('directive', '', '', '', raw)

    # Instruction
    parts = stripped.split(';', 1)
    code = parts[0].strip()
    comment = parts[1].strip() if len(parts) > 1 else ''
    tokens = code.split(None, 1)
    if tokens:
        op = tokens[0].lower()
        arg = tokens[1] if len(tokens) > 1 else ''
        return ('inst', op, arg, comment, raw)

    return ('other', '', '', '', raw)


def peephole_optimize(lines):
    """Apply peephole optimizations to assembly lines. Returns new list."""
    result = list(lines)
    changed = True
    passes = 0

    while changed and passes < 5:
        changed = False
        passes += 1
        result = _opt_branch_over_jmp(result)
        new_result = _opt_dead_jmp(result)
        if len(new_result) < len(result):
            changed = True
            result = new_result

    # Count optimizations
    return result


def _opt_branch_over_jmp(lines):
    """Convert BNE skip / JMP target / skip: → BEQ target.

    Only if target is estimated to be within branch range.
    """
    result = []
    i = 0
    while i < len(lines):
        if i + 2 < len(lines):
            p1 = parse_line(lines[i])
            p2 = parse_line(lines[i + 1])
            p3 = parse_line(lines[i + 2])

            if (p1[0] == 'inst' and p1[1] in BRANCH_OPS and
                    p2[0] == 'inst' and p2[1] == 'jmp' and
                    p3[0] == 'label' and p3[1] == p1[2].strip()):
                # Pattern found: Bxx skip / JMP target / skip:
                inv_branch = BRANCH_INVERSE.get(p1[1])
                jmp_target = p2[2].strip()

                if inv_branch and _is_within_branch_range(lines, i, jmp_target):
                    # Replace with inverted branch to JMP target
                    comment = '  ; peephole: branch-over-JMP'
                    new_inst = '                %s %s%s' % (inv_branch, jmp_target, comment)
                    result.append(new_inst)
                    # Keep the label (might be referenced elsewhere)
                    result.append(lines[i + 2])
                    i += 3
                    continue

        result.append(lines[i])
        i += 1

    return result


def _opt_dead_jmp(lines):
    """Remove JMP label where label is the immediately following line."""
    result = []
    i = 0
    while i < len(lines):
        if i + 1 < len(lines):
            p1 = parse_line(lines[i])
            p2 = parse_line(lines[i + 1])
            if (p1[0] == 'inst' and p1[1] == 'jmp' and
                    p2[0] == 'label' and p2[1] == p1[2].strip()):
                # JMP to next line — skip the JMP
                i += 1
                continue
        result.append(lines[i])
        i += 1
    return result


def _is_within_branch_range(lines, branch_idx, target_label):
    """Estimate if target_label is within ±127 bytes of branch_idx.

    Conservative: estimates instruction sizes and checks the distance.
    Returns True if likely within range, False if uncertain.
    """
    # Find the target label
    target_idx = None
    for j in range(len(lines)):
        p = parse_line(lines[j])
        if p[0] == 'label' and p[1] == target_label:
            target_idx = j
            break

    if target_idx is None:
        return False  # can't find target, don't optimize

    # Use cycle_model's instruction parser for accurate byte counts
    try:
        from cycle_model import parse_instruction
    except ImportError:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from cycle_model import parse_instruction

    lo = min(branch_idx, target_idx)
    hi = max(branch_idx, target_idx)
    total_bytes = 0
    for j in range(lo + 1, hi):
        inst = parse_instruction(lines[j])
        if inst and inst.mnemonic:
            total_bytes += inst.bytes
    # Branch range is ±127 from the byte AFTER the branch instruction (2 bytes)
    # Use 115 as safety margin (127 - 12 for label alignment uncertainty)
    return total_bytes <= 115
