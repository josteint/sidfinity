"""
layout_opt.py — Layout optimization for V2 codegen assembly output.

Analyzes the generated assembly to find:
1. JMP instructions that jump to the very next instruction (can be elided)
2. JMP instructions within ±127 bytes of target (can be converted to branch)
3. Branch instructions that exceed ±127 bytes (assembly errors)
4. Code sections that could be reordered for better fall-through

This is Phase 3.2 of the codegen plan.
"""

import subprocess
import os
import sys


def analyze_layout(source, xa_path='tools/xa65/xa/xa'):
    """Analyze the layout of generated assembly after xa65 assembly.

    Assembles the source and analyzes the binary for branch distances,
    JMP targets, and optimization opportunities.

    Returns a dict with findings.
    """
    # Write source to temp file
    src_path = '/tmp/layout_analysis.s'
    bin_path = '/tmp/layout_analysis.bin'
    with open(src_path, 'w') as f:
        f.write(source)

    # Assemble with default flags
    r = subprocess.run([xa_path, '-XMASM',
        '-Dbase=$1000', '-DDEFAULTTEMPO=$5', '-DADPARAM=$f', '-DSRPARAM=$0',
        '-DFIRSTNOHRINSTR=$3', '-DFIRSTLEGATOINSTR=$3',
        '-o', bin_path, src_path],
        capture_output=True, text=True)

    if r.returncode != 0:
        return {'error': r.stderr[:500]}

    with open(bin_path, 'rb') as f:
        binary = f.read()

    base = 0x1000
    findings = {
        'size': len(binary),
        'jmp_elide': [],       # JMPs that jump to next instruction
        'jmp_to_branch': [],   # JMPs within branch range
        'branch_overflow': [], # branches exceeding ±127 bytes
        'jmp_count': 0,
        'branch_count': 0,
        'total_jmp_bytes': 0,
    }

    BRANCH_OPS = {0x10:'BPL', 0x30:'BMI', 0x50:'BVC', 0x70:'BVS',
                  0x90:'BCC', 0xB0:'BCS', 0xD0:'BNE', 0xF0:'BEQ'}

    # One-byte opcodes (for skipping operands correctly)
    ONE_BYTE = {0x00,0x08,0x0A,0x18,0x28,0x2A,0x38,0x40,0x48,0x4A,0x60,0x68,
                0x6A,0x88,0x8A,0x98,0x9A,0xA8,0xAA,0xBA,0xC8,0xCA,0xD8,0xE8,0xEA,0xF8}
    TWO_BYTE = {0x01,0x05,0x06,0x09,0x10,0x11,0x15,0x16,0x21,0x24,0x25,0x26,
                0x29,0x30,0x31,0x35,0x36,0x41,0x45,0x46,0x49,0x50,0x51,0x55,
                0x56,0x61,0x65,0x66,0x69,0x70,0x71,0x75,0x76,0x81,0x84,0x85,
                0x86,0x90,0x91,0x94,0x95,0x96,0xA0,0xA1,0xA2,0xA4,0xA5,0xA6,
                0xA9,0xB0,0xB1,0xB4,0xB5,0xB6,0xC0,0xC1,0xC4,0xC5,0xC6,0xC9,
                0xD0,0xD1,0xD5,0xD6,0xE0,0xE1,0xE4,0xE5,0xE6,0xE9,0xF0,0xF1,
                0xF5,0xF6}

    i = 0
    while i < len(binary):
        op = binary[i]
        addr = base + i

        # Branch instruction
        if op in BRANCH_OPS:
            findings['branch_count'] += 1
            offset = binary[i+1]
            if offset >= 128:
                offset -= 256
            target = addr + 2 + offset
            distance = abs(offset)
            if distance > 120:  # warn when getting close to 127
                findings['branch_overflow'].append({
                    'addr': addr, 'op': BRANCH_OPS[op],
                    'target': target, 'distance': offset,
                    'at_limit': distance > 126
                })
            i += 2
            continue

        # JMP absolute
        if op == 0x4C:
            findings['jmp_count'] += 1
            findings['total_jmp_bytes'] += 3
            target = binary[i+1] | (binary[i+2] << 8)
            distance = target - (addr + 3)  # distance from after JMP to target

            # Check: does JMP go to the very next instruction?
            next_addr = addr + 3
            if target == next_addr:
                findings['jmp_elide'].append({
                    'addr': addr, 'target': target,
                    'save_bytes': 3, 'save_cycles': 3
                })
            # Check: could this JMP be a branch (within ±127)?
            elif -128 <= distance <= 127:
                findings['jmp_to_branch'].append({
                    'addr': addr, 'target': target, 'distance': distance,
                    'save_bytes': 1, 'save_cycles': 0  # branch taken = 3, JMP = 3
                })

            i += 3
            continue

        # JSR
        if op == 0x20:
            i += 3
            continue

        # Skip other instructions
        if op in ONE_BYTE:
            i += 1
        elif op in TWO_BYTE:
            i += 2
        else:
            i += 3

    return findings


def report(source, song_name=''):
    """Print a layout optimization report."""
    findings = analyze_layout(source)

    if 'error' in findings:
        print(f'Assembly error: {findings["error"]}')
        return

    print(f'=== Layout Analysis{f" for {song_name}" if song_name else ""} ===')
    print(f'Binary size: {findings["size"]} bytes')
    print(f'JMP count: {findings["jmp_count"]} ({findings["total_jmp_bytes"]} bytes)')
    print(f'Branch count: {findings["branch_count"]}')

    if findings['jmp_elide']:
        print(f'\nJMPs to elide (target is next instruction):')
        total_save = 0
        for j in findings['jmp_elide']:
            print(f'  ${j["addr"]:04X}: JMP ${j["target"]:04X} — save {j["save_bytes"]} bytes, {j["save_cycles"]} cycles')
            total_save += j['save_bytes']
        print(f'  Total: {total_save} bytes saveable')

    if findings['jmp_to_branch']:
        print(f'\nJMPs convertible to branches (within ±127):')
        for j in findings['jmp_to_branch']:
            print(f'  ${j["addr"]:04X}: JMP ${j["target"]:04X} (distance {j["distance"]:+d}) — save {j["save_bytes"]} byte')
        print(f'  Total: {len(findings["jmp_to_branch"])} bytes saveable')

    if findings['branch_overflow']:
        print(f'\nBranches near/at limit (±127):')
        for b in findings['branch_overflow']:
            status = 'OVERFLOW!' if b['at_limit'] else 'near limit'
            print(f'  ${b["addr"]:04X}: {b["op"]} ${b["target"]:04X} (offset {b["distance"]:+d}) — {status}')

    total_saveable = (sum(j['save_bytes'] for j in findings['jmp_elide']) +
                      sum(j['save_bytes'] for j in findings['jmp_to_branch']))
    print(f'\nTotal optimization potential: {total_saveable} bytes')
    print(f'Optimized size: {findings["size"] - total_saveable} bytes')

    return findings


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from codegen_v2 import generate_player
    from gt2_to_usf import gt2_to_usf
    import json

    with open('src/player/regression_registry.json') as f:
        reg = json.load(f)

    for name in ['Covfefe', 'Shovel_Funk', 'Boo']:
        entry = [e for e in reg if name in e['path']]
        if not entry:
            continue
        path = entry[0]['path']
        if not os.path.exists(path):
            continue
        song = gt2_to_usf(path)
        if not song:
            continue
        src = generate_player(song)
        print()
        report(src, os.path.basename(path))
        print()
