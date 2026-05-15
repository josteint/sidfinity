"""
Auto-disassemble a PSID binary from init+play, emit a seed in the same
format as docs/hubbard_action_biker_disassembly.s.

Usage: python3 disasm_seed.py <psid> > out.s
"""
import struct, sys

def trace_starts(binary, la, entries):
    """Return set of instruction-start addresses reachable from entry points."""
    starts = set()
    work = list(entries)
    while work:
        addr = work.pop()
        if addr in starts:
            continue
        off = addr - la
        if off < 0 or off >= len(binary):
            continue
        op = binary[off]
        if op not in OPS:
            continue
        _, mode, ln = OPS[op]
        if off + ln > len(binary):
            continue
        starts.add(addr)
        # Successors
        if op in (0x60, 0x40, 0x00):  # RTS, RTI, BRK
            continue
        if op == 0x4C:  # JMP abs
            tgt = binary[off+1] | (binary[off+2] << 8)
            work.append(tgt)
            continue
        if op == 0x6C:  # JMP indirect — give up
            continue
        if op == 0x20:  # JSR — successor at target and fall-through
            tgt = binary[off+1] | (binary[off+2] << 8)
            work.append(tgt)
            work.append(addr + ln)
            continue
        if op in BRANCHES:
            disp = binary[off+1]
            tgt = addr + ln + (disp if disp < 128 else disp - 256)
            work.append(tgt)
            work.append(addr + ln)
            continue
        # Default: fall through
        work.append(addr + ln)
    return starts

# Minimal 6502 opcode table (full undocumented set NOT needed; everything
# Hubbard uses is documented). Format: opcode -> (mnem, mode, length).
OPS = {}
def _add(op, mnem, mode, length):
    OPS[op] = (mnem, mode, length)

# Generated/hand-built minimal documented 6502 table — enough for Hubbard.
# (taken from src/player/cycle_model.py optable shape, abbreviated)
_OPT = """
00 BRK imp 1
01 ORA izx 2
05 ORA zp  2
06 ASL zp  2
08 PHP imp 1
09 ORA imm 2
0A ASL acc 1
0D ORA abs 3
0E ASL abs 3
10 BPL rel 2
11 ORA izy 2
15 ORA zpx 2
16 ASL zpx 2
18 CLC imp 1
19 ORA aby 3
1D ORA abx 3
1E ASL abx 3
20 JSR abs 3
21 AND izx 2
24 BIT zp  2
25 AND zp  2
26 ROL zp  2
28 PLP imp 1
29 AND imm 2
2A ROL acc 1
2C BIT abs 3
2D AND abs 3
2E ROL abs 3
30 BMI rel 2
31 AND izy 2
35 AND zpx 2
36 ROL zpx 2
38 SEC imp 1
39 AND aby 3
3D AND abx 3
3E ROL abx 3
40 RTI imp 1
41 EOR izx 2
45 EOR zp  2
46 LSR zp  2
48 PHA imp 1
49 EOR imm 2
4A LSR acc 1
4C JMP abs 3
4D EOR abs 3
4E LSR abs 3
50 BVC rel 2
51 EOR izy 2
55 EOR zpx 2
56 LSR zpx 2
58 CLI imp 1
59 EOR aby 3
5D EOR abx 3
5E LSR abx 3
60 RTS imp 1
61 ADC izx 2
65 ADC zp  2
66 ROR zp  2
68 PLA imp 1
69 ADC imm 2
6A ROR acc 1
6C JMP ind 3
6D ADC abs 3
6E ROR abs 3
70 BVS rel 2
71 ADC izy 2
75 ADC zpx 2
76 ROR zpx 2
78 SEI imp 1
79 ADC aby 3
7D ADC abx 3
7E ROR abx 3
81 STA izx 2
84 STY zp  2
85 STA zp  2
86 STX zp  2
88 DEY imp 1
8A TXA imp 1
8C STY abs 3
8D STA abs 3
8E STX abs 3
90 BCC rel 2
91 STA izy 2
94 STY zpx 2
95 STA zpx 2
96 STX zpy 2
98 TYA imp 1
99 STA aby 3
9A TXS imp 1
9D STA abx 3
A0 LDY imm 2
A1 LDA izx 2
A2 LDX imm 2
A4 LDY zp  2
A5 LDA zp  2
A6 LDX zp  2
A8 TAY imp 1
A9 LDA imm 2
AA TAX imp 1
AC LDY abs 3
AD LDA abs 3
AE LDX abs 3
B0 BCS rel 2
B1 LDA izy 2
B4 LDY zpx 2
B5 LDA zpx 2
B6 LDX zpy 2
B8 CLV imp 1
B9 LDA aby 3
BA TSX imp 1
BC LDY abx 3
BD LDA abx 3
BE LDX aby 3
C0 CPY imm 2
C1 CMP izx 2
C4 CPY zp  2
C5 CMP zp  2
C6 DEC zp  2
C8 INY imp 1
C9 CMP imm 2
CA DEX imp 1
CC CPY abs 3
CD CMP abs 3
CE DEC abs 3
D0 BNE rel 2
D1 CMP izy 2
D5 CMP zpx 2
D6 DEC zpx 2
D8 CLD imp 1
D9 CMP aby 3
DD CMP abx 3
DE DEC abx 3
E0 CPX imm 2
E1 SBC izx 2
E4 CPX zp  2
E5 SBC zp  2
E6 INC zp  2
E8 INX imp 1
E9 SBC imm 2
EA NOP imp 1
EC CPX abs 3
ED SBC abs 3
EE INC abs 3
F0 BEQ rel 2
F1 SBC izy 2
F5 SBC zpx 2
F6 INC zpx 2
F8 SED imp 1
F9 SBC aby 3
FD SBC abx 3
FE INC abx 3
"""
for line in _OPT.strip().splitlines():
    p = line.split()
    _add(int(p[0],16), p[1].lower(), p[2], int(p[3]))

BRANCHES = {0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0}

# SID register names ($D400-$D418) — for ;V1_FREQ_LO style annotations.
SID_REGS = {
    0x00:'V1_FREQ_LO', 0x01:'V1_FREQ_HI', 0x02:'V1_PW_LO', 0x03:'V1_PW_HI',
    0x04:'V1_CTRL',    0x05:'V1_AD',      0x06:'V1_SR',
    0x07:'V2_FREQ_LO', 0x08:'V2_FREQ_HI', 0x09:'V2_PW_LO', 0x0A:'V2_PW_HI',
    0x0B:'V2_CTRL',    0x0C:'V2_AD',      0x0D:'V2_SR',
    0x0E:'V3_FREQ_LO', 0x0F:'V3_FREQ_HI', 0x10:'V3_PW_LO', 0x11:'V3_PW_HI',
    0x12:'V3_CTRL',    0x13:'V3_AD',      0x14:'V3_SR',
    0x15:'F_LO', 0x16:'F_HI', 0x17:'RES_FILT', 0x18:'VOL',
}

def parse_psid(path):
    d = open(path,'rb').read()
    ver = struct.unpack('>H', d[4:6])[0]
    off = struct.unpack('>H', d[6:8])[0]
    la  = struct.unpack('>H', d[8:10])[0]
    init = struct.unpack('>H', d[10:12])[0]
    play = struct.unpack('>H', d[12:14])[0]
    songs = struct.unpack('>H', d[14:16])[0]
    start = struct.unpack('>H', d[16:18])[0]
    name = d[22:54].rstrip(b'\x00').decode('latin-1','ignore')
    author = d[54:86].rstrip(b'\x00').decode('latin-1','ignore')
    released = d[86:118].rstrip(b'\x00').decode('latin-1','ignore')
    body = d[off:]
    if la == 0:
        la = body[0] | (body[1] << 8)
        body = body[2:]
    return {
        'name': name, 'author': author, 'released': released,
        'load': la, 'init': init, 'play': play,
        'songs': songs, 'start': start, 'binary': body,
    }

def operand_str(mode, b, addr, code_addrs, sub_addrs):
    """Build operand string + optional comment for one instruction.
    Returns (operand_text, comment_text_or_None)."""
    if mode in ('imp','acc'):
        return '', None
    if mode == 'imm':
        return f'#${b[1]:02x}', None
    if mode in ('zp','zpx','zpy'):
        suf = {'zp':'', 'zpx':',x', 'zpy':',y'}[mode]
        return f'${b[1]:02x}{suf}', None
    if mode in ('abs','abx','aby','ind'):
        val = b[1] | (b[2] << 8)
        suf = {'abs':'', 'abx':',x', 'aby':',y', 'ind':''}[mode]
        if mode == 'ind':
            text = f'(${val:04x})'
        else:
            text = f'${val:04x}{suf}'
        # SID register annotation
        if 0xD400 <= val <= 0xD418:
            reg = SID_REGS.get(val - 0xD400, f'SID+{val-0xD400:02x}')
            return text, reg + suf
        return text, None
    if mode == 'izx':
        return f'(${b[1]:02x},x)', None
    if mode == 'izy':
        return f'(${b[1]:02x}),y', None
    if mode == 'rel':
        off = b[1]
        tgt = addr + 2 + (off if off < 128 else off - 256)
        return f'${tgt:04x}', None
    return '???', None

def jump_label(addr, sub_addrs):
    if addr in sub_addrs:
        return f'sub_{addr:04X}'
    return f'L_{addr:04X}'

def disassemble(psid):
    la, init, play, binary = psid['load'], psid['init'], psid['play'], psid['binary']
    starts = trace_starts(binary, la, [init, play])

    branch_targets = set()
    jsr_targets = set()
    rel_branches = set()
    addr_to_insn = {}     # addr -> (mnem, mode, len, bytes-tuple)

    for addr in sorted(starts):
        off = addr - la
        op = binary[off]
        mnem, mode, ln = OPS[op]
        b = tuple(binary[off:off+ln])
        addr_to_insn[addr] = (mnem, mode, ln, b)

        if op == 0x20:  # JSR abs
            tgt = b[1] | (b[2] << 8)
            jsr_targets.add(tgt)
            branch_targets.add(tgt)
        elif op == 0x4C:  # JMP abs
            tgt = b[1] | (b[2] << 8)
            branch_targets.add(tgt)
        elif op in BRANCHES:
            disp = b[1]
            tgt = addr + 2 + (disp if disp < 128 else disp - 256)
            branch_targets.add(tgt)
            rel_branches.add(addr)
        # JMP ind and others: ignore for label gen

    # Always label init + play even if no branch targets them.
    branch_targets.add(init)
    branch_targets.add(play)

    # Build the output lines.
    lines = []
    psid_summary_addr = la + len(binary) - 1
    lines.append(f'; ============================================================================')
    lines.append(f'; Rob Hubbard - {psid["name"]} ({psid["released"]})')
    lines.append(f'; ANNOTATED DISASSEMBLY (auto-generated seed; hand annotation TODO)')
    lines.append(f'; ============================================================================')
    lines.append(f';')
    lines.append(f'; Binary: data/C64Music/MUSICIANS/H/Hubbard_Rob/{psid["name"].replace(" ","_")}.sid')
    lines.append(f'; Load:   ${la:04X}   Init: ${init:04X}   Play: ${play:04X}')
    lines.append(f'; PSID:   {psid["songs"]} subtunes, default subtune {psid["start"]} (1-indexed)')
    lines.append(f'; Binary: ${la:04X}-${psid_summary_addr:04X} ({len(binary)} bytes)')
    lines.append(f';')
    lines.append(f'; Auto-traced {len(starts)} reachable instructions from init+play.')
    lines.append(f'; ============================================================================')
    lines.append('')

    sorted_addrs = sorted(addr_to_insn.keys())
    prev_end = la  # address one past the last emitted instruction
    last_was_terminal = True

    for addr in sorted_addrs:
        mnem, mode, ln, b = addr_to_insn[addr]

        # Data gap before this instruction?
        if addr > prev_end:
            gap_start, gap_end = prev_end, addr - 1
            lines.append(f'; ----- data gap ${gap_start:04X}-${gap_end:04X} ({gap_end - gap_start + 1} bytes) -----')
            lines.append('')

        # Label?
        if addr == play:
            lines.append('; ======= play: =======')
            lines.append('play:')
        elif addr == init:
            lines.append('; ======= init: =======')
            lines.append('init:')
        elif addr in jsr_targets:
            lines.append(f'sub_{addr:04X}:')
        elif addr in branch_targets:
            lines.append(f'L_{addr:04X}:')

        # Bytes column (max 3 bytes, padded to 9 chars: "XX XX XX ")
        bytes_str = ' '.join(f'{x:02X}' for x in b).ljust(9)
        operand_text, sid_comment = operand_str(mode, b, addr, addr_to_insn, jsr_targets)

        # Mnemonic+operand
        mnem_up = mnem.upper()
        line = f'    ${addr:04X}: {bytes_str} {mnem_up} {operand_text}'.rstrip()

        # Cross-reference comment for control-flow instructions.
        xref = None
        if mnem in ('jmp','jsr') and mode == 'abs':
            tgt = b[1] | (b[2] << 8)
            xref = f'→ {jump_label(tgt, jsr_targets)}'
        elif mode == 'rel':
            disp = b[1]
            tgt = addr + 2 + (disp if disp < 128 else disp - 256)
            xref = f'→ {jump_label(tgt, jsr_targets)}'

        # Build trailing comment.
        comments = []
        if xref:
            comments.append(xref)
        if sid_comment:
            comments.append(sid_comment)

        # Pad to col 32 before the comment(s).
        if comments:
            line = f'{line:<32}; {"   ; ".join(comments)}'

        lines.append(line)
        prev_end = addr + ln

    return '\n'.join(lines) + '\n'

if __name__ == '__main__':
    psid = parse_psid(sys.argv[1])
    out = disassemble(psid)
    sys.stdout.write(out)
