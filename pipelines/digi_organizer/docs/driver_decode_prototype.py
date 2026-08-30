"""Prototype: a GENERIC driver decoder.

Walks the member's init vector as 6502 instructions and reports the facts a
universal driver would need — the ordered environment writes, the cycle count
to the core call, and the tail form — with no per-class pattern matching.
If this reproduces every member, the 14-class registry is redundant.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from pipelines.digi_organizer.extract import load_image, _find

# opcode -> (mnemonic, length, cycles, kind)  — only what these drivers use
OPS = {
 0x78:('sei',1,2,None), 0x58:('cli',1,2,None), 0x60:('rts',1,6,'ret'),
 0x40:('rti',1,6,'ret'), 0xEA:('nop',1,2,None),
 0xA9:('lda#',2,2,'setA'), 0xA2:('ldx#',2,2,'setX'), 0xA0:('ldy#',2,2,'setY'),
 0x85:('sta_zp',2,3,'store'), 0x86:('stx_zp',2,3,'store'), 0x84:('sty_zp',2,3,'store'),
 0x8D:('sta',3,4,'store'), 0x8E:('stx',3,4,'store'), 0x8C:('sty',3,4,'store'),
 0xAD:('lda',3,4,'load'), 0xAE:('ldx',3,4,'load'), 0xAC:('ldy',3,4,'load'),
 0xA5:('lda_zp',2,3,'load'),
 0x20:('jsr',3,6,'call'), 0x4C:('jmp',3,3,'jump'),
 0xAA:('tax',1,2,'xfer'), 0x8A:('txa',1,2,'xfer'), 0xA8:('tay',1,2,'xfer'),
 0x98:('tya',1,2,'xfer'), 0xE8:('inx',1,2,'incx'), 0xCA:('dex',1,2,None),
 0x48:('pha',1,3,None), 0x68:('pla',1,4,None),
 0xEE:('inc',3,6,'rmw'), 0xCE:('dec',3,6,'rmw'), 0x0E:('asl',3,6,'rmw'),
 0x2C:('bit',3,4,None), 0x29:('and#',2,2,None), 0x09:('ora#',2,2,None),
 0xC9:('cmp#',2,2,None), 0xE0:('cpx#',2,2,None), 0xCD:('cmp',3,4,None),
 0xD0:('bne',2,2,'branch'), 0xF0:('beq',2,2,'branch'),
 0x10:('bpl',2,2,'branch'), 0x30:('bmi',2,2,'branch'),
}

def decode(sid, core_base, iv_addr, load, img, limit=80):
    """Walk from iv_addr; return (writes, cycles_to_core, entry, tail, trace)."""
    pc, cycles, writes, trace = iv_addr, 0, [], []
    regs = {'a': None, 'x': None, 'y': None}
    for _ in range(limit):
        o = img[pc - load]
        if o not in OPS:
            return None, None, None, f'UNKNOWN_OPCODE ${o:02X} @ ${pc:04X}', trace
        mn, ln, cy, kind = OPS[o]
        ops = img[pc - load + 1: pc - load + ln]
        arg = (ops[0] | ops[1] << 8) if ln == 3 else (ops[0] if ln == 2 else None)
        trace.append(f'${pc:04X} {mn} {arg if arg is None else hex(arg)}')
        if kind == 'call' or (kind == 'jump' and arg in (core_base, core_base + 0x40)):
            if arg in (core_base, core_base + 0x40):
                return writes, cycles + cy, ('core40' if arg == core_base + 0x40
                                             else 'core'), None, trace
            # JSR to a sub-routine: inline it (sub_jmp's shape)
            sw, sc, se, st, str_ = decode(sid, core_base, arg, load, img, limit=40)
            if se:                                  # the sub reached the core
                return writes + sw, cycles + cy + sc, se, None, trace + str_
            return None, None, None, 'JSR_NOT_CORE', trace
        if kind == 'store':
            src = {'sta': 'a', 'stx': 'x', 'sty': 'y'}[mn.split('_')[0]]
            writes.append((arg, regs[src]))
        elif kind in ('setA', 'setX', 'setY'):
            regs[{'setA': 'a', 'setX': 'x', 'setY': 'y'}[kind]] = arg
        elif kind == 'xfer':
            regs[mn[1]] = regs[mn[0].replace('t', '')] if False else regs[mn[1]]
            m = {'tax': ('a', 'x'), 'txa': ('x', 'a'), 'tay': ('a', 'y'), 'tya': ('y', 'a')}
            regs[m[mn][1]] = regs[m[mn][0]]
        elif kind == 'incx':
            regs['x'] = None if regs['x'] is None else (regs['x'] + 1) & 0xFF
        elif kind == 'load':
            regs[{'lda': 'a', 'ldx': 'x', 'ldy': 'y'}[mn.split('_')[0]]] = None
        elif kind == 'branch':
            cycles += 1                              # assume taken
            pc = pc + ln + (arg - 256 if arg > 127 else arg); cycles += cy; continue
        cycles += cy
        pc += ln
    return None, None, None, 'NO_CORE_CALL_IN_LIMIT', trace


def decode_wrapper(core_base, addr, load, img, limit=40):
    """Walk an IRQ wrapper; return (pre_cycles, post_cycles, writes, reads,
    saves, exit_form) with no per-class matching."""
    pc, pre, post, seen = addr, 0, 0, False
    writes, reads, saves, exitf = [], [], [], None
    regs = {'a': None, 'x': None, 'y': None}
    for _ in range(limit):
        o = img[pc - load]
        if o not in OPS:
            return None, None, None, None, None, f'UNKNOWN ${o:02X}'
        mn, ln, cy, kind = OPS[o]
        ops = img[pc - load + 1: pc - load + ln]
        arg = (ops[0] | ops[1] << 8) if ln == 3 else (ops[0] if ln == 2 else None)
        if kind == 'call' and arg == core_base + 3:
            seen = True; pre += cy; pc += ln; continue
        if mn == 'rti':
            exitf = 'rti'; (post if seen else pre); break
        if kind == 'jump':
            exitf = f'jmp ${arg:04X}'; break
        if mn == 'pha': saves.append('push')
        if mn == 'pla': saves.append('pull')
        if kind == 'store': writes.append((arg, regs['a' if mn.startswith('sta')
                                                   else 'x' if mn.startswith('stx') else 'y']))
        if kind == 'rmw': writes.append((arg, mn))
        if kind == 'load': reads.append(arg)
        if kind in ('setA','setX','setY'):
            regs[{'setA':'a','setX':'x','setY':'y'}[kind]] = arg
        if kind == 'branch':
            pc = pc + ln + (arg - 256 if arg > 127 else arg)
            (post if seen else pre).__class__      # branch back = a wait loop
            if seen: post += cy + 1
            else: pre += cy + 1
            continue
        if seen: post += cy
        else: pre += cy
        pc += ln
    return pre, post, writes, reads, saves, exitf
