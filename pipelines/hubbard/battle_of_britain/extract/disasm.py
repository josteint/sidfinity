#!/usr/bin/env python3
"""Recursive-descent 6502 disassembler.

Produces the ACME-flavoured listing that `pipelines/hubbard/battle_of_britain/
disassembly.s` was hand-annotated on top of: $XXXX-prefixed addresses,
hex byte bodies, lowercase mnemonics, branch targets resolved as
labels (sub_XXXX / L_XXXX / data_XXXX), and "data gap" comments
spanning unreachable bytes. SID-register absolute writes are tagged
with their friendly name (V1_FREQ_LO, VOL, etc.).

Used by hand to seed `pipelines/hubbard/battle_of_britain/disassembly.s`.
Reusable for any PSID — pass the .sid path on the command line.

Usage:
    python -m pipelines.hubbard.battle_of_britain.extract.disasm \\
        hvsc84/MUSICIANS/H/Hubbard_Rob/Battle_of_Britain.sid \\
        > /tmp/seed.s
"""

import struct
import sys

# ----- 6502 opcode table (length, mnemonic, address mode) ---------------------
# mode codes: imp, acc, imm, zp, zpx, zpy, izx, izy, abs, abx, aby, ind, rel

_OP: dict[int, tuple[str, str]] = {}


def _def(op: int, mnem: str, mode: str) -> None:
    _OP[op] = (mnem, mode)


def _build_table() -> None:
    rows = [
        (0x69, 'ADC', 'imm'), (0x65, 'ADC', 'zp'), (0x75, 'ADC', 'zpx'),
        (0x6D, 'ADC', 'abs'), (0x7D, 'ADC', 'abx'), (0x79, 'ADC', 'aby'),
        (0x61, 'ADC', 'izx'), (0x71, 'ADC', 'izy'),
        (0x29, 'AND', 'imm'), (0x25, 'AND', 'zp'), (0x35, 'AND', 'zpx'),
        (0x2D, 'AND', 'abs'), (0x3D, 'AND', 'abx'), (0x39, 'AND', 'aby'),
        (0x21, 'AND', 'izx'), (0x31, 'AND', 'izy'),
        (0x0A, 'ASL', 'acc'), (0x06, 'ASL', 'zp'), (0x16, 'ASL', 'zpx'),
        (0x0E, 'ASL', 'abs'), (0x1E, 'ASL', 'abx'),
        (0x24, 'BIT', 'zp'), (0x2C, 'BIT', 'abs'),
        (0x10, 'BPL', 'rel'), (0x30, 'BMI', 'rel'), (0x50, 'BVC', 'rel'),
        (0x70, 'BVS', 'rel'), (0x90, 'BCC', 'rel'), (0xB0, 'BCS', 'rel'),
        (0xD0, 'BNE', 'rel'), (0xF0, 'BEQ', 'rel'),
        (0x00, 'BRK', 'imp'),
        (0x18, 'CLC', 'imp'), (0x38, 'SEC', 'imp'),
        (0x58, 'CLI', 'imp'), (0x78, 'SEI', 'imp'),
        (0xB8, 'CLV', 'imp'), (0xD8, 'CLD', 'imp'), (0xF8, 'SED', 'imp'),
        (0xC9, 'CMP', 'imm'), (0xC5, 'CMP', 'zp'), (0xD5, 'CMP', 'zpx'),
        (0xCD, 'CMP', 'abs'), (0xDD, 'CMP', 'abx'), (0xD9, 'CMP', 'aby'),
        (0xC1, 'CMP', 'izx'), (0xD1, 'CMP', 'izy'),
        (0xE0, 'CPX', 'imm'), (0xE4, 'CPX', 'zp'), (0xEC, 'CPX', 'abs'),
        (0xC0, 'CPY', 'imm'), (0xC4, 'CPY', 'zp'), (0xCC, 'CPY', 'abs'),
        (0xC6, 'DEC', 'zp'), (0xD6, 'DEC', 'zpx'),
        (0xCE, 'DEC', 'abs'), (0xDE, 'DEC', 'abx'),
        (0xCA, 'DEX', 'imp'), (0x88, 'DEY', 'imp'),
        (0x49, 'EOR', 'imm'), (0x45, 'EOR', 'zp'), (0x55, 'EOR', 'zpx'),
        (0x4D, 'EOR', 'abs'), (0x5D, 'EOR', 'abx'), (0x59, 'EOR', 'aby'),
        (0x41, 'EOR', 'izx'), (0x51, 'EOR', 'izy'),
        (0xE6, 'INC', 'zp'), (0xF6, 'INC', 'zpx'),
        (0xEE, 'INC', 'abs'), (0xFE, 'INC', 'abx'),
        (0xE8, 'INX', 'imp'), (0xC8, 'INY', 'imp'),
        (0x4C, 'JMP', 'abs'), (0x6C, 'JMP', 'ind'),
        (0x20, 'JSR', 'abs'),
        (0x60, 'RTS', 'imp'), (0x40, 'RTI', 'imp'),
        (0xA9, 'LDA', 'imm'), (0xA5, 'LDA', 'zp'), (0xB5, 'LDA', 'zpx'),
        (0xAD, 'LDA', 'abs'), (0xBD, 'LDA', 'abx'), (0xB9, 'LDA', 'aby'),
        (0xA1, 'LDA', 'izx'), (0xB1, 'LDA', 'izy'),
        (0xA2, 'LDX', 'imm'), (0xA6, 'LDX', 'zp'), (0xB6, 'LDX', 'zpy'),
        (0xAE, 'LDX', 'abs'), (0xBE, 'LDX', 'aby'),
        (0xA0, 'LDY', 'imm'), (0xA4, 'LDY', 'zp'), (0xB4, 'LDY', 'zpx'),
        (0xAC, 'LDY', 'abs'), (0xBC, 'LDY', 'abx'),
        (0x4A, 'LSR', 'acc'), (0x46, 'LSR', 'zp'), (0x56, 'LSR', 'zpx'),
        (0x4E, 'LSR', 'abs'), (0x5E, 'LSR', 'abx'),
        (0xEA, 'NOP', 'imp'),
        (0x09, 'ORA', 'imm'), (0x05, 'ORA', 'zp'), (0x15, 'ORA', 'zpx'),
        (0x0D, 'ORA', 'abs'), (0x1D, 'ORA', 'abx'), (0x19, 'ORA', 'aby'),
        (0x01, 'ORA', 'izx'), (0x11, 'ORA', 'izy'),
        (0x48, 'PHA', 'imp'), (0x68, 'PLA', 'imp'),
        (0x08, 'PHP', 'imp'), (0x28, 'PLP', 'imp'),
        (0x2A, 'ROL', 'acc'), (0x26, 'ROL', 'zp'), (0x36, 'ROL', 'zpx'),
        (0x2E, 'ROL', 'abs'), (0x3E, 'ROL', 'abx'),
        (0x6A, 'ROR', 'acc'), (0x66, 'ROR', 'zp'), (0x76, 'ROR', 'zpx'),
        (0x6E, 'ROR', 'abs'), (0x7E, 'ROR', 'abx'),
        (0xE9, 'SBC', 'imm'), (0xE5, 'SBC', 'zp'), (0xF5, 'SBC', 'zpx'),
        (0xED, 'SBC', 'abs'), (0xFD, 'SBC', 'abx'), (0xF9, 'SBC', 'aby'),
        (0xE1, 'SBC', 'izx'), (0xF1, 'SBC', 'izy'),
        (0x85, 'STA', 'zp'), (0x95, 'STA', 'zpx'),
        (0x8D, 'STA', 'abs'), (0x9D, 'STA', 'abx'), (0x99, 'STA', 'aby'),
        (0x81, 'STA', 'izx'), (0x91, 'STA', 'izy'),
        (0x86, 'STX', 'zp'), (0x96, 'STX', 'zpy'), (0x8E, 'STX', 'abs'),
        (0x84, 'STY', 'zp'), (0x94, 'STY', 'zpx'), (0x8C, 'STY', 'abs'),
        (0xAA, 'TAX', 'imp'), (0x8A, 'TXA', 'imp'),
        (0xA8, 'TAY', 'imp'), (0x98, 'TYA', 'imp'),
        (0xBA, 'TSX', 'imp'), (0x9A, 'TXS', 'imp'),
    ]
    for op, m, mode in rows:
        _def(op, m, mode)


_build_table()

_MODE_LEN = {
    'imp': 1, 'acc': 1,
    'imm': 2, 'zp': 2, 'zpx': 2, 'zpy': 2, 'izx': 2, 'izy': 2, 'rel': 2,
    'abs': 3, 'abx': 3, 'aby': 3, 'ind': 3,
}


# ----- PSID loader ------------------------------------------------------------

def load_psid(path: str) -> tuple[int, int, int, bytes]:
    """Return (load_addr, init_addr, play_addr, binary_payload)."""
    with open(path, 'rb') as f:
        raw = f.read()
    data_off = struct.unpack('>H', raw[6:8])[0]
    init_addr = struct.unpack('>H', raw[10:12])[0]
    play_addr = struct.unpack('>H', raw[12:14])[0]
    load_field = struct.unpack('>H', raw[8:10])[0]
    payload = raw[data_off:]
    if load_field == 0:
        load_addr = struct.unpack('<H', payload[:2])[0]
        binary = payload[2:]
    else:
        load_addr = load_field
        binary = payload
    return load_addr, init_addr, play_addr, binary


# ----- Disassembly engine -----------------------------------------------------

def trace(binary: bytes, la: int, entry_points: list[int]) -> dict[int, tuple]:
    """Recursive descent: returns dict pos -> (mnem, mode, length, operand,
    address)."""
    code: dict[int, tuple] = {}
    work = list(entry_points)
    while work:
        addr = work.pop()
        if addr is None:
            continue
        pos = addr - la
        if pos < 0 or pos >= len(binary) or pos in code:
            continue
        op = binary[pos]
        if op not in _OP:
            # Unknown opcode → halt this trace.
            continue
        mnem, mode = _OP[op]
        length = _MODE_LEN[mode]
        if pos + length > len(binary):
            continue
        operand: int | None = None
        if length == 2:
            operand = binary[pos + 1]
        elif length == 3:
            operand = binary[pos + 1] | (binary[pos + 2] << 8)
        code[pos] = (mnem, mode, length, operand, addr)
        # Control flow.
        if mode == 'rel':
            off = operand if operand < 0x80 else operand - 0x100
            target = (addr + 2 + off) & 0xFFFF
            work.append(target)
            work.append(addr + length)
        elif mnem == 'JMP' and mode == 'abs':
            work.append(operand)
        elif mnem == 'JMP' and mode == 'ind':
            pass  # indirect target unknown statically
        elif mnem == 'JSR':
            work.append(operand)
            work.append(addr + length)
        elif mnem in ('RTS', 'RTI', 'BRK'):
            pass
        else:
            work.append(addr + length)
    return code


# ----- Formatting -------------------------------------------------------------

_SID_NAMES = {
    0xD400: 'V1_FREQ_LO', 0xD401: 'V1_FREQ_HI',
    0xD402: 'V1_PW_LO',   0xD403: 'V1_PW_HI',
    0xD404: 'V1_CTRL',    0xD405: 'V1_AD',     0xD406: 'V1_SR',
    0xD407: 'V2_FREQ_LO', 0xD408: 'V2_FREQ_HI',
    0xD409: 'V2_PW_LO',   0xD40A: 'V2_PW_HI',
    0xD40B: 'V2_CTRL',    0xD40C: 'V2_AD',     0xD40D: 'V2_SR',
    0xD40E: 'V3_FREQ_LO', 0xD40F: 'V3_FREQ_HI',
    0xD410: 'V3_PW_LO',   0xD411: 'V3_PW_HI',
    0xD412: 'V3_CTRL',    0xD413: 'V3_AD',     0xD414: 'V3_SR',
    0xD415: 'FC_LO',  0xD416: 'FC_HI', 0xD417: 'RES_FILT',
    0xD418: 'VOL',    0xD419: 'POT_X', 0xD41A: 'POT_Y',
    0xD41B: 'OSC3',   0xD41C: 'ENV3',
}


def fmt_operand(mnem: str, mode: str, operand: int, addr: int) -> str:
    if mode == 'imp':
        return ''
    if mode == 'acc':
        return 'A'
    if mode == 'imm':
        return f'#${operand:02x}'
    if mode == 'zp':
        return f'${operand:02x}'
    if mode == 'zpx':
        return f'${operand:02x},X'
    if mode == 'zpy':
        return f'${operand:02x},Y'
    if mode == 'izx':
        return f'(${operand:02x},X)'
    if mode == 'izy':
        return f'(${operand:02x}),Y'
    if mode == 'rel':
        off = operand if operand < 0x80 else operand - 0x100
        tgt = (addr + 2 + off) & 0xFFFF
        return f'${tgt:04x}'
    base = operand
    if mode == 'abs':
        return (f'${base:04x} ;{_SID_NAMES[base]}'
                if base in _SID_NAMES else f'${base:04x}')
    if mode == 'abx':
        return (f'${base:04x},X ;{_SID_NAMES[base]},X'
                if base in _SID_NAMES else f'${base:04x},X')
    if mode == 'aby':
        return (f'${base:04x},Y ;{_SID_NAMES[base]},Y'
                if base in _SID_NAMES else f'${base:04x},Y')
    if mode == 'ind':
        return f'(${base:04x})'
    return '?'


def annotate_target(mnem: str, mode: str, operand: int, addr: int,
                    jsr_targets: set[int], branch_targets: set[int],
                    init_addr: int, play_addr: int) -> str | None:
    if mode == 'rel':
        off = operand if operand < 0x80 else operand - 0x100
        tgt = (addr + 2 + off) & 0xFFFF
    elif mnem == 'JMP' and mode == 'abs':
        tgt = operand
    elif mnem == 'JSR':
        tgt = operand
    else:
        return None
    if tgt == init_addr:
        return 'init'
    if tgt == play_addr:
        return 'play'
    if tgt in jsr_targets:
        return f'sub_{tgt:04X}'
    if tgt in branch_targets:
        return f'L_{tgt:04X}'
    return None


def emit_listing(binary: bytes, la: int, init_addr: int, play_addr: int,
                 code: dict[int, tuple]) -> str:
    jsr_targets: set[int] = set()
    branch_targets: set[int] = set()
    for pos, (mnem, mode, length, operand, addr) in code.items():
        if mnem == 'JSR':
            jsr_targets.add(operand)
        elif mode == 'rel':
            off = operand if operand < 0x80 else operand - 0x100
            branch_targets.add((addr + 2 + off) & 0xFFFF)
        elif mnem == 'JMP' and mode == 'abs':
            branch_targets.add(operand)
    items = sorted(code.items())
    out: list[str] = []
    cur = la
    end = la + len(binary)
    for pos, (mnem, mode, length, operand, code_addr) in items:
        addr = la + pos
        if addr > cur:
            out.append(
                f'; ----- data gap ${cur:04X}-${addr - 1:04X} '
                f'({addr - cur} bytes) -----')
            out.append('')
        if addr == init_addr:
            out.extend(['', '; ======= init: =======', 'init:'])
        elif addr == play_addr:
            out.extend(['', '; ======= play: =======', 'play:'])
        elif addr in jsr_targets:
            out.append(f'sub_{addr:04X}:')
        elif addr in branch_targets:
            out.append(f'L_{addr:04X}:')
        byte_str = ' '.join(f'{binary[pos + k]:02X}' for k in range(length))
        operand_str = fmt_operand(mnem, mode, operand, code_addr)
        instr = f'{mnem} {operand_str}' if operand_str else mnem
        tgt = annotate_target(mnem, mode, operand, code_addr,
                              jsr_targets, branch_targets,
                              init_addr, play_addr)
        comment = f'   ; → {tgt}' if tgt else ''
        out.append(f'    ${addr:04X}: {byte_str:<11} {instr}{comment}')
        cur = addr + length
    if cur < end:
        out.append(
            f'; ----- data gap ${cur:04X}-${end - 1:04X} '
            f'({end - cur} bytes) -----')
    return '\n'.join(out) + '\n'


# ----- CLI --------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        sys.stderr.write(
            'usage: python -m pipelines.hubbard.battle_of_britain.extract.disasm '
            '<path.sid>\n')
        sys.exit(2)
    path = sys.argv[1]
    la, init, play, binary = load_psid(path)
    sys.stderr.write(
        f'; Load=${la:04X} Init=${init:04X} Play=${play:04X} '
        f'Size={len(binary)}\n')
    code = trace(binary, la, [init, play])
    instr_bytes = sum(c[2] for c in code.values())
    sys.stderr.write(
        f'; Reached {len(code)} instructions ({instr_bytes} bytes)\n')
    sys.stdout.write(emit_listing(binary, la, init, play, code))


if __name__ == '__main__':
    main()
