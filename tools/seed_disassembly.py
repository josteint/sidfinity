#!/usr/bin/env python3
"""
Seed an annotated 6502 disassembly file from a PSID, in the style of
docs/hubbard_action_biker_disassembly.s. Auto-traces reachable code
from (init, play) entry points; everything else is emitted as data
gap markers. The output is intended to be hand-annotated afterwards.

Usage:
    PYTHONPATH=tools/py65_lib python3 tools/seed_disassembly.py <file.sid> > out.s
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py65_lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU
from code_flow import _INST_LEN, _BRANCHES
# code_flow's _INST_LEN[0x20] is 2, but JSR abs is 3 bytes. Patch locally.
_INST_LEN[0x20] = 3

# code_flow._INST_LEN miscategorizes JSR ($20) as 2 bytes (low nibble matches
# the 2-byte mode mask). Patch a local copy so the seed is accurate.
_INST_LEN = list(_INST_LEN)
_INST_LEN[0x20] = 3


SID_REG_NAMES = {
    0xD400: 'V1_FREQ_LO', 0xD401: 'V1_FREQ_HI',
    0xD402: 'V1_PW_LO',   0xD403: 'V1_PW_HI',
    0xD404: 'V1_CTRL',    0xD405: 'V1_AD',  0xD406: 'V1_SR',
    0xD407: 'V2_FREQ_LO', 0xD408: 'V2_FREQ_HI',
    0xD409: 'V2_PW_LO',   0xD40A: 'V2_PW_HI',
    0xD40B: 'V2_CTRL',    0xD40C: 'V2_AD',  0xD40D: 'V2_SR',
    0xD40E: 'V3_FREQ_LO', 0xD40F: 'V3_FREQ_HI',
    0xD410: 'V3_PW_LO',   0xD411: 'V3_PW_HI',
    0xD412: 'V3_CTRL',    0xD413: 'V3_AD',  0xD414: 'V3_SR',
    0xD415: 'FC_LO', 0xD416: 'FC_HI', 0xD417: 'RES_FILT', 0xD418: 'VOL',
    0xD419: 'POTX', 0xD41A: 'POTY', 0xD41B: 'OSC3', 0xD41C: 'ENV3',
}


def parse_psid(path):
    with open(path, 'rb') as f:
        sid = f.read()
    assert sid[:4] in (b'PSID', b'RSID')
    data_off = int.from_bytes(sid[6:8], 'big')
    load = int.from_bytes(sid[8:10], 'big')
    init = int.from_bytes(sid[10:12], 'big')
    play = int.from_bytes(sid[12:14], 'big')
    songs = int.from_bytes(sid[14:16], 'big')
    start = int.from_bytes(sid[16:18], 'big')
    name = sid[22:54].rstrip(b'\0').decode('latin-1')
    author = sid[54:86].rstrip(b'\0').decode('latin-1')
    released = sid[86:118].rstrip(b'\0').decode('latin-1')
    payload = sid[data_off:]
    if load == 0:
        load = payload[0] | (payload[1] << 8)
        payload = payload[2:]
    return {
        'load': load, 'init': init, 'play': play,
        'songs': songs, 'start': start,
        'name': name, 'author': author, 'released': released,
        'payload': payload,
    }


def trace(payload, load, init, play, extra_entries=()):
    """Walk reachable code; return (code_addrs, label_targets, jsr_targets)."""
    n = len(payload)
    code = set()              # addresses (not offsets) of every code byte
    starts = set()            # instruction start addresses
    labels = set()            # branch/JMP targets that need a label
    jsr_tgts = set()          # JSR targets get sub_NNNN labels
    visited = set()
    worklist = []
    for a in tuple(extra_entries) + (init, play):
        off = a - load
        if 0 <= off < n:
            worklist.append(off)
            jsr_tgts.add(a)   # treat init/play as subroutine roots
        elif a == 0:
            # RSID play=0: IRQ-driven; the init routine patches CIA/IRQ.
            # We'll discover the play target during hand-annotation.
            pass
    while worklist:
        pos = worklist.pop()
        if pos in visited or not (0 <= pos < n):
            continue
        visited.add(pos)
        op = payload[pos]
        ilen = _INST_LEN[op]
        if pos + ilen > n:
            continue
        starts.add(load + pos)
        for b in range(pos, pos + ilen):
            code.add(load + b)
        if op in (0x60, 0x40, 0x00):
            continue
        if op == 0x4C:
            tgt = payload[pos + 1] | (payload[pos + 2] << 8)
            labels.add(tgt)
            t_off = tgt - load
            if 0 <= t_off < n:
                worklist.append(t_off)
            continue
        if op == 0x6C:
            continue
        if op == 0x20:
            tgt = payload[pos + 1] | (payload[pos + 2] << 8)
            jsr_tgts.add(tgt)
            t_off = tgt - load
            if 0 <= t_off < n:
                worklist.append(t_off)
            worklist.append(pos + ilen)
            continue
        if op in _BRANCHES:
            offset = payload[pos + 1]
            if offset >= 0x80:
                offset -= 0x100
            t = load + pos + ilen + offset
            labels.add(t)
            t_off = t - load
            if 0 <= t_off < n:
                worklist.append(t_off)
            worklist.append(pos + ilen)
            continue
        worklist.append(pos + ilen)
    return code, starts, labels, jsr_tgts


def annotate_sid_writes(line, op):
    """If the operand resolves into SID register space, append ;NAME(,Y/,X)."""
    # Skip the address column ($NNNN: ...) and match the OPERAND.
    import re
    body = line.split(':', 1)[-1] if ':' in line else line
    m = re.search(r'\$([0-9A-Fa-f]{4})', body)
    if not m:
        return line
    addr = int(m.group(1), 16)
    if addr in SID_REG_NAMES:
        # Distinguish ,X / ,Y / plain
        suffix = ''
        tail = line.rstrip().lower()
        if tail.endswith(',y'):
            suffix = ',Y'
        elif tail.endswith(',x'):
            suffix = ',X'
        return f'{line} ;{SID_REG_NAMES[addr]}{suffix}'
    return line


def label_for(addr, jsr_tgts, init_addr, play_addr):
    if addr == init_addr:
        return 'init'
    if addr == play_addr:
        return 'play'
    if addr in jsr_tgts:
        return f'sub_{addr:04X}'
    return f'L_{addr:04X}'


def fmt_inst(addr, ibytes, mnem_str):
    """Format an instruction line."""
    bs = ' '.join(f'{b:02X}' for b in ibytes)
    bs = bs.ljust(8)
    return f'    ${addr:04X}: {bs}   {mnem_str}'


def main(sid_path, extra_entries=(), virts=()):
    s = parse_psid(sid_path)
    payload, load = s['payload'], s['load']
    init, play = s['init'], s['play']
    end_addr = load + len(payload) - 1
    code, starts, labels, jsr_tgts = trace(payload, load, init, play, extra_entries)
    # Virtual relocation: also trace bytes treated as if they were at vdst.
    # Each virt = (src, length, vdst). We build a synthetic payload at vdst
    # and append its trace results into the main sets, keyed by vdst addresses.
    virt_blocks = []
    for src, vlen, vdst in virts:
        src_off = src - load
        vpayload = bytes(payload[src_off:src_off + vlen])
        vcode, vstarts, vlabels, vjsr = trace(vpayload, vdst, vdst, 0)
        # Merge — addresses in vdst-space won't collide with the load-space set.
        code.update(vcode)
        starts.update(vstarts)
        labels.update(vlabels)
        jsr_tgts.update(vjsr)
        virt_blocks.append((src, vlen, vdst, vpayload))

    # Set up disassembler with the binary in memory
    mpu = MPU()
    for i, b in enumerate(payload):
        mpu.memory[load + i] = b
    # Also map the virtual relocation blocks at their destination addresses
    # so the disassembler can decode operands of those instructions.
    for src, vlen, vdst, vpayload in virt_blocks:
        for i, b in enumerate(vpayload):
            mpu.memory[vdst + i] = b
    dis = Disassembler(mpu)

    out = []
    out.append('; ============================================================================')
    out.append(f'; Rob Hubbard - {s["name"]} ({s["released"]})')
    out.append('; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)')
    out.append('; ============================================================================')
    out.append(';')
    out.append(f'; Binary: {sid_path}')
    out.append(f'; Load:   ${load:04X}   Init: ${init:04X}   Play: ${play:04X}')
    out.append(f'; PSID:   {s["songs"]} subtune(s), default subtune {s["start"]}')
    out.append(f'; Binary: ${load:04X}-${end_addr:04X} ({len(payload)} bytes)')
    out.append(';')
    out.append(f'; Auto-traced {len(code)} reachable code bytes from init+play.')
    out.append(';')
    out.append('; ============================================================================')
    out.append('')

    # Walk the payload top-down, emitting code blocks and data gaps.
    pos = 0
    n = len(payload)
    while pos < n:
        addr = load + pos
        if addr in code and addr in starts:
            # Emit block header (label) if needed
            if addr in jsr_tgts or addr in labels:
                lbl = label_for(addr, jsr_tgts, init, play)
                # Heading style: subroutines get a ======= header, plain
                # branch targets get a bare "L_XXXX:" line.
                if addr == init:
                    out.append('; ======= init: =======')
                    out.append('init:')
                elif addr == play:
                    out.append('; ======= play: =======')
                    out.append('play:')
                elif addr in jsr_tgts:
                    out.append(f'{lbl}:')
                else:
                    out.append(f'{lbl}:')
            try:
                length, mnem = dis.instruction_at(addr)
                ilen = length
            except Exception:
                ilen = _INST_LEN[payload[pos]]
                length, mnem = ilen, f'.byte ${payload[pos]:02X}'
            ibytes = payload[pos:pos + ilen]
            # Append symbolic target for control-flow ops
            op = payload[pos]
            comment_tail = ''
            if op in (0x4C, 0x20):  # JMP abs, JSR
                tgt = payload[pos + 1] | (payload[pos + 2] << 8)
                t_off = tgt - load
                if tgt in code:
                    comment_tail = f'   ; → {label_for(tgt, jsr_tgts, init, play)}'
            elif op in _BRANCHES:
                offset = payload[pos + 1]
                if offset >= 0x80:
                    offset -= 0x100
                tgt = addr + ilen + offset
                t_off = tgt - load
                if tgt in code:
                    comment_tail = f'   ; → {label_for(tgt, jsr_tgts, init, play)}'
            # Uppercase mnemonic, lowercase hex operand (Action Biker style)
            parts = mnem.split(None, 1)
            if len(parts) == 2:
                mnem = parts[0].upper() + ' ' + parts[1].lower()
            else:
                mnem = parts[0].upper()
            line = fmt_inst(addr, ibytes, mnem.ljust(14))
            line = annotate_sid_writes(line, op)
            line += comment_tail
            out.append(line)
            pos += ilen
        elif addr in code:
            # Mid-instruction byte (overlapping decode); skip 1 byte.
            pos += 1
        else:
            # Data gap: scan forward until next code-instruction start
            gap_start = addr
            gap_pos = pos
            while gap_pos < n and (load + gap_pos) not in starts:
                gap_pos += 1
            gap_end = load + gap_pos - 1
            out.append(f'; ----- data gap ${gap_start:04X}-${gap_end:04X} ({gap_pos - pos} bytes) -----')
            out.append('')
            pos = gap_pos

    # Emit virtual relocation blocks as separate sections.
    for src, vlen, vdst, vpayload in virt_blocks:
        out.append('')
        out.append('; ============================================================================')
        out.append(f'; VIRTUAL: bytes ${src:04X}-${src + vlen - 1:04X} disassembled as if at ${vdst:04X}')
        out.append(f';         (copied at runtime by the relocator)')
        out.append('; ============================================================================')
        out.append('')
        vpos = 0
        while vpos < vlen:
            addr = vdst + vpos
            if addr in code and addr in starts:
                if addr in jsr_tgts or addr in labels:
                    lbl = label_for(addr, jsr_tgts, init, play)
                    out.append(f'{lbl}:')
                try:
                    length, mnem = dis.instruction_at(addr)
                    ilen = length
                except Exception:
                    ilen = _INST_LEN[vpayload[vpos]]
                    length, mnem = ilen, f'.byte ${vpayload[vpos]:02X}'
                ibytes = vpayload[vpos:vpos + ilen]
                op = vpayload[vpos]
                comment_tail = ''
                if op in (0x4C, 0x20):
                    tgt = vpayload[vpos + 1] | (vpayload[vpos + 2] << 8)
                    if tgt in code:
                        comment_tail = f'   ; → {label_for(tgt, jsr_tgts, init, play)}'
                elif op in _BRANCHES:
                    offset = vpayload[vpos + 1]
                    if offset >= 0x80:
                        offset -= 0x100
                    tgt = addr + ilen + offset
                    if tgt in code:
                        comment_tail = f'   ; → {label_for(tgt, jsr_tgts, init, play)}'
                parts = mnem.split(None, 1)
                if len(parts) == 2:
                    mnem = parts[0].upper() + ' ' + parts[1].lower()
                else:
                    mnem = parts[0].upper()
                line = fmt_inst(addr, ibytes, mnem.ljust(14))
                line = annotate_sid_writes(line, op)
                line += comment_tail
                out.append(line)
                vpos += ilen
            elif addr in code:
                vpos += 1
            else:
                gap_start = addr
                gap_pos = vpos
                while gap_pos < vlen and (vdst + gap_pos) not in starts:
                    gap_pos += 1
                gap_end = vdst + gap_pos - 1
                out.append(f'; ----- data gap ${gap_start:04X}-${gap_end:04X} ({gap_pos - vpos} bytes) -----')
                out.append('')
                vpos = gap_pos
    print('\n'.join(out))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('sid')
    ap.add_argument('--entry', action='append', default=[],
                    help='extra entry address, hex (e.g. 0x7F73); repeatable')
    ap.add_argument('--virt', action='append', default=[],
                    help='virtual relocation block SRC:LEN:DST in hex '
                         '(e.g. 0x7B40:0x400:0xC000); repeatable')
    args = ap.parse_args()
    extras = [int(e, 0) for e in args.entry]
    virts = []
    for v in args.virt:
        s, l, d = v.split(':')
        virts.append((int(s, 0), int(l, 0), int(d, 0)))
    main(args.sid, extras, virts)
