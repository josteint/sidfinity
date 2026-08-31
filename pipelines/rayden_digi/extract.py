"""Rayden_Digi — binary → typed model.

Player anatomy is in RE_NOTES.md.  Short form: a per-frame SEQUENCER walks a
command-byte score and re-triggers the sample playback core, which is a pair
of vector-swapped CIA2-NMI handlers RELOCATED out of the file image (zero
page on every V2 member).

Two rules this module is built around, both learned the expensive way:

  * **Locate, never assume an address.**  Every table base, state byte and
    store site is read from the LOCATED INSTRUCTION OPERAND of the member's
    own code (ledger C39).  Watching one member's PCs against another's
    image returns a confidently wrong answer.

  * **The file image LIES about the playback core.**  Its handler template
    carries `$EA` filler pointer operands and `ORA #$00` where the running
    code has the member's real or_mask, because init RELOCATES the handlers
    and the music player POKES the mask into them.  So the core is read from
    `siddump --peek-post-init` and the mask is MEASURED with
    `--memwatch` ([[feedback_ground_truth]] third failure mode).

The score itself is decoded by RUNNING the member's own sequencer over its
own file-image data (an idealized extraction sim — every byte it reads was
loaded by the image or written by the routine that just ran).  The result is
gated against the libsidplayfp write stream by `verify_score.py`.
"""
from __future__ import annotations

import os
import struct
import subprocess
from dataclasses import dataclass, field

SIDDUMP = os.path.join(os.path.dirname(__file__), '..', '..', 'tools',
                       'siddump')


class RaydenDigiUnsupported(Exception):
    pass


# ---------------------------------------------------------------------------
# image loading
# ---------------------------------------------------------------------------

def load_image(sid_path: str):
    """Return (meta, load_addr, image bytes)."""
    d = open(sid_path, 'rb').read()
    off = struct.unpack('>H', d[6:8])[0]
    magic = d[:4].decode('latin1')
    version = struct.unpack('>H', d[4:6])[0]
    load, init, play, songs, start = struct.unpack('>HHHHH', d[8:18])
    speed = struct.unpack('>I', d[18:22])[0]

    def _s(a, b):
        return d[a:b].split(b'\0')[0].decode('latin1')

    body = d[off:]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        img = body[2:]
    elif len(body) >= 2 and struct.unpack('<H', body[:2])[0] == load:
        img = body[2:]
    else:
        img = body
    flags = struct.unpack('>H', d[0x76:0x78])[0] if version >= 2 else 0
    meta = {'magic': magic, 'version': version, 'init': init, 'play': play,
            'songs': songs, 'start_song': start, 'speed': speed,
            'clock': {1: 'PAL', 2: 'NTSC', 3: 'both'}.get((flags >> 2) & 3,
                                                          'unknown'),
            'sid_model': {1: 6581, 2: 8580, 3: 'both'}.get((flags >> 4) & 3, 0),
            'title': _s(0x16, 0x36), 'author': _s(0x36, 0x56),
            'released': _s(0x56, 0x76)}
    return meta, load, img


# ---------------------------------------------------------------------------
# a minimal 6502 decoder (operand reading only — never for timing)
# ---------------------------------------------------------------------------

_M = {
    0x00: ('brk', 'imp'), 0x05: ('ora', 'zp'), 0x06: ('asl', 'zp'),
    0x08: ('php', 'imp'), 0x09: ('ora', 'imm'), 0x0A: ('asl', 'acc'),
    0x0D: ('ora', 'abs'), 0x0E: ('asl', 'abs'), 0x10: ('bpl', 'rel'),
    0x11: ('ora', 'izy'), 0x15: ('ora', 'zpx'), 0x18: ('clc', 'imp'),
    0x19: ('ora', 'aby'), 0x1D: ('ora', 'abx'), 0x20: ('jsr', 'abs'),
    0x24: ('bit', 'zp'), 0x25: ('and', 'zp'), 0x26: ('rol', 'zp'),
    0x28: ('plp', 'imp'), 0x29: ('and', 'imm'), 0x2A: ('rol', 'acc'),
    0x2C: ('bit', 'abs'), 0x2D: ('and', 'abs'), 0x2E: ('rol', 'abs'),
    0x30: ('bmi', 'rel'), 0x31: ('and', 'izy'), 0x38: ('sec', 'imp'),
    0x39: ('and', 'aby'), 0x3D: ('and', 'abx'), 0x40: ('rti', 'imp'),
    0x45: ('eor', 'zp'), 0x46: ('lsr', 'zp'), 0x48: ('pha', 'imp'),
    0x49: ('eor', 'imm'), 0x4A: ('lsr', 'acc'), 0x4C: ('jmp', 'abs'),
    0x4D: ('eor', 'abs'), 0x4E: ('lsr', 'abs'), 0x50: ('bvc', 'rel'),
    0x51: ('eor', 'izy'), 0x58: ('cli', 'imp'), 0x59: ('eor', 'aby'),
    0x5D: ('eor', 'abx'), 0x60: ('rts', 'imp'), 0x65: ('adc', 'zp'),
    0x66: ('ror', 'zp'), 0x68: ('pla', 'imp'), 0x69: ('adc', 'imm'),
    0x6A: ('ror', 'acc'), 0x6C: ('jmp', 'ind'), 0x6D: ('adc', 'abs'),
    0x6E: ('ror', 'abs'), 0x70: ('bvs', 'rel'), 0x71: ('adc', 'izy'),
    0x78: ('sei', 'imp'), 0x79: ('adc', 'aby'), 0x7D: ('adc', 'abx'),
    0x81: ('sta', 'izx'), 0x84: ('sty', 'zp'), 0x85: ('sta', 'zp'),
    0x86: ('stx', 'zp'), 0x88: ('dey', 'imp'), 0x8A: ('txa', 'imp'),
    0x8C: ('sty', 'abs'), 0x8D: ('sta', 'abs'), 0x8E: ('stx', 'abs'),
    0x90: ('bcc', 'rel'), 0x91: ('sta', 'izy'), 0x94: ('sty', 'zpx'),
    0x95: ('sta', 'zpx'), 0x96: ('stx', 'zpy'), 0x98: ('tya', 'imp'),
    0x99: ('sta', 'aby'), 0x9A: ('txs', 'imp'), 0x9D: ('sta', 'abx'),
    0xA0: ('ldy', 'imm'), 0xA1: ('lda', 'izx'), 0xA2: ('ldx', 'imm'),
    0xA4: ('ldy', 'zp'), 0xA5: ('lda', 'zp'), 0xA6: ('ldx', 'zp'),
    0xA8: ('tay', 'imp'), 0xA9: ('lda', 'imm'), 0xAA: ('tax', 'imp'),
    0xAC: ('ldy', 'abs'), 0xAD: ('lda', 'abs'), 0xAE: ('ldx', 'abs'),
    0xB0: ('bcs', 'rel'), 0xB1: ('lda', 'izy'), 0xB4: ('ldy', 'zpx'),
    0xB5: ('lda', 'zpx'), 0xB6: ('ldx', 'zpy'), 0xB8: ('clv', 'imp'),
    0xB9: ('lda', 'aby'), 0xBA: ('tsx', 'imp'), 0xBC: ('ldy', 'abx'),
    0xBD: ('lda', 'abx'), 0xBE: ('ldx', 'aby'), 0xC0: ('cpy', 'imm'),
    0xC4: ('cpy', 'zp'), 0xC5: ('cmp', 'zp'), 0xC6: ('dec', 'zp'),
    0xC8: ('iny', 'imp'), 0xC9: ('cmp', 'imm'), 0xCA: ('dex', 'imp'),
    0xCC: ('cpy', 'abs'), 0xCD: ('cmp', 'abs'), 0xCE: ('dec', 'abs'),
    0xD0: ('bne', 'rel'), 0xD1: ('cmp', 'izy'), 0xD5: ('cmp', 'zpx'),
    0xD6: ('dec', 'zpx'), 0xD8: ('cld', 'imp'), 0xD9: ('cmp', 'aby'),
    0xDD: ('cmp', 'abx'), 0xDE: ('dec', 'abx'), 0xE0: ('cpx', 'imm'),
    0xE4: ('cpx', 'zp'), 0xE5: ('sbc', 'zp'), 0xE6: ('inc', 'zp'),
    0xE8: ('inx', 'imp'), 0xE9: ('sbc', 'imm'), 0xEA: ('nop', 'imp'),
    0xEC: ('cpx', 'abs'), 0xED: ('sbc', 'abs'), 0xEE: ('inc', 'abs'),
    0xF0: ('beq', 'rel'), 0xF1: ('sbc', 'izy'), 0xF5: ('sbc', 'zpx'),
    0xF6: ('inc', 'zpx'), 0xF8: ('sed', 'imp'), 0xF9: ('sbc', 'aby'),
    0xFD: ('sbc', 'abx'), 0xFE: ('inc', 'abx'),
}
_LEN = {'imp': 1, 'acc': 1, 'imm': 2, 'zp': 2, 'zpx': 2, 'zpy': 2,
        'izx': 2, 'izy': 2, 'rel': 2, 'abs': 3, 'abx': 3, 'aby': 3, 'ind': 3}


def decode(mem, base, pc, count):
    """Linear-decode `count` bytes from `pc`; mem[i] is the byte at base+i.

    STOPS at an unrecognised opcode rather than guessing a length: a wrong
    length desynchronises the whole walk, and a desynchronised walk finds
    plausible instructions that were never in the code.  Callers check
    whether they reached what they were looking for.
    """
    out = []
    end = pc + count
    while pc < end:
        op = mem[pc - base]
        if op not in _M:
            break
        mn, mode = _M[op]
        n = _LEN[mode]
        arg = None
        if mode in ('imm', 'zp', 'zpx', 'zpy', 'izx', 'izy'):
            arg = mem[pc - base + 1]
        elif mode == 'rel':
            arg = (pc + 2 + ((mem[pc - base + 1] ^ 0x80) - 0x80)) & 0xFFFF
        elif mode in ('abs', 'abx', 'aby', 'ind'):
            arg = mem[pc - base + 1] | (mem[pc - base + 2] << 8)
        out.append((pc, mn, mode, arg, n))
        pc += n
    return out


# ---------------------------------------------------------------------------
# the model
# ---------------------------------------------------------------------------

@dataclass
class RaydenDigiModel:
    sid_path: str
    load: int
    meta: dict
    head: int                     # `jmp reset / jmp tick` + the two pointers
    reset: int
    tick: int
    seq: dict                     # decoded sequencer facts (addresses)
    or_mask: int                  # measured: bits held high on every write
    terminator: int               # in-stream end-of-sample byte
    nibble_order: str             # 'low_first' | 'high_first'
    idle_level: 'int | None'      # per-frame idle assertion, None = absent
    events: list = field(default_factory=list)   # [(sample, latch, dur)]
    loop_at: 'int | None' = None                 # event index the score loops to
    samples: dict = field(default_factory=dict)  # id -> (start, loop)
    pcm: dict = field(default_factory=dict)      # id -> nibble list
    order: list = field(default_factory=list)    # block ids (two-level only)
    order_loop: int = 0
    blocks: dict = field(default_factory=dict)   # block id -> [event index]


# ---------------------------------------------------------------------------
# location + static decode
# ---------------------------------------------------------------------------

def locate_head(img, load):
    """The digi module's head: `jmp reset / jmp tick`, then the score-start
    and loop pointers.  `tick` is identified by its duration countdown
    (`dec zp / beq +1 / rts`), which every member of the family shares.

    NB the head is NOT at the PSID load address on every member
    (Spelling_Around loads at $0801 with the module at $0820).
    """
    for i in range(len(img) - 6):
        if img[i] != 0x4C or img[i + 3] != 0x4C:
            continue
        reset = img[i + 1] | (img[i + 2] << 8)
        tick = img[i + 4] | (img[i + 5] << 8)
        if not all(load <= a < load + len(img) - 8 for a in (reset, tick)):
            continue
        t, r = tick - load, reset - load
        if (img[t] == 0xC6 and img[t + 2] == 0xF0 and img[t + 3] == 0x01
                and img[t + 4] == 0x60 and img[r] == 0xA9 and img[r + 1] == 0):
            return load + i, reset, tick
    return None


def decode_sequencer(img, load, reset, tick):
    """Read every address the sequencer uses out of its own operands."""
    f = {}
    rins = decode(img, load, reset, 0x18)
    for pc, mn, mode, arg, _n in rins:
        if mn == 'rts':
            break
        if mn == 'ldx' and mode == 'abs':
            f['score_ptr_addr'] = arg
    ins = decode(img, load, tick, 0x100)
    if ins[0][1] != 'dec':
        raise RaydenDigiUnsupported('tick does not open with the countdown')
    f['dur_zp'] = ins[0][3]
    trig = None
    for k in range(len(ins) - 1):
        if (ins[k][1] == 'lda' and ins[k][2] == 'imm' and ins[k][3] == 0
                and ins[k + 1][1] == 'sta' and ins[k + 1][3] == 0xDD0E):
            trig = k + 2
            break
    if trig is None:
        end = ins[-1][0] + ins[-1][4] if ins else tick
        raise RaydenDigiUnsupported(
            f'no trigger block: the walk from ${tick:04X} stopped at '
            f'${end:04X} without a `lda #$00 / sta $DD0E`'
            + (f' (unknown opcode ${img[end - load]:02X})'
               if load <= end < load + len(img) else ''))
    seq, tr = ins[:trig], ins[trig:]
    if tr[0][1] != 'ldy' or tr[0][2] != 'zp':
        raise RaydenDigiUnsupported('trigger does not index by the sample var')
    f['sample_zp'] = tr[0][3]
    # four `lda tab,y / sta dest` pairs: the sample START pointer then the
    # sample LOOP pointer, each poked into the NMI handlers' own operands.
    # A member with no per-sample loop point NEUTERS the second pair's
    # stores to `bit` (the V1 members do) — the core's built-in immediate
    # then stands, so record the destination but flag it dead.
    dsts, tabs, k, neutered = [], [], 1, []
    while len(dsts) < 4:
        ld, st = tr[k], tr[k + 1]
        if ld[1] != 'lda' or ld[2] != 'aby' or st[1] not in ('sta', 'bit'):
            raise RaydenDigiUnsupported(
                f'unexpected pointer-table load at ${ld[0]:04X} '
                f'({ld[1]} {ld[2]}) / store {st[1]}')
        tabs.append(ld[3])
        dsts.append(st[3])
        neutered.append(st[1] == 'bit')
        k += 2
    if tabs[1] != tabs[0] + 1 or tabs[3] != tabs[2] + 1:
        raise RaydenDigiUnsupported('pointer tables are not interleaved words')
    if neutered[0] or neutered[1]:
        raise RaydenDigiUnsupported('the sample START pointer store is dead')
    f['start_tab'], f['loop_tab'] = tabs[0], tabs[2]
    f['ptr_lo'], f['ptr_hi'], f['looppoke_lo'], f['looppoke_hi'] = dsts
    f['loop_ptr_live'] = not (neutered[2] or neutered[3])
    if tr[k][1] != 'ldy' or tr[k][2] != 'zp':
        raise RaydenDigiUnsupported('trigger does not index by the rate var')
    f['rate_zp'] = tr[k][3]
    k += 1
    # the latch load pair, located by its STORES: a member whose rate table
    # was patched out to a fixed latch carries `lda #imm / nop / sta`, so the
    # instruction spacing differs from the table form
    lds = {}
    for n, (_pc, mn, _mode, arg, _sz) in enumerate(tr[k:], start=k):
        if mn == 'sta' and arg in (0xDD04, 0xDD05):
            prev = next((tr[p] for p in range(n - 1, k - 1, -1)
                         if tr[p][1] == 'lda'), None)
            if prev is None:
                raise RaydenDigiUnsupported('latch store with no load')
            lds[arg] = prev
        if arg == 0xDD0E and mn == 'sta':
            break
    if set(lds) != {0xDD04, 0xDD05}:
        raise RaydenDigiUnsupported('the trigger does not program both latch '
                                    'bytes')
    ld_lo, ld_hi = lds[0xDD04], lds[0xDD05]
    if ld_lo[2] == 'aby':
        # a rate TABLE: the score's rate byte indexes it (a tuning table)
        if ld_hi[3] != ld_lo[3] + 1:
            raise RaydenDigiUnsupported('latch table is not interleaved words')
        f['latch_tab'] = ld_lo[3]
    elif ld_lo[2] == 'imm':
        # the table read was patched out to a fixed latch
        f['latch_tab'] = None
        f['latch_fixed'] = ld_lo[3] | (ld_hi[3] << 8)
    else:
        raise RaydenDigiUnsupported('unrecognised latch load')
    izy = [i[3] for i in seq if i[1] == 'lda' and i[2] == 'izy']
    if not izy:
        raise RaydenDigiUnsupported('no score-stream fetch')
    f['stream_zp'] = izy[-1]
    outer = [z for z in izy if z != f['stream_zp']]
    f['two_level'] = bool(outer)
    f['order_zp'] = outer[0] if outer else None
    f['blocktab'] = next((i[3] for i in seq
                          if i[1] == 'lda' and i[2] == 'abx'), None)
    f['loop_ptr_addr'] = next((i[3] for i in seq
                               if i[1] == 'ldx' and i[2] == 'abs'), None)
    if f['two_level'] and f['blocktab'] is None:
        raise RaydenDigiUnsupported('two-level score without a block table')
    return f


# ---------------------------------------------------------------------------
# the playback core, read from the RUNNING machine (never from the image)
# ---------------------------------------------------------------------------

def _siddump(sid_path, *args, timeout=600):
    cmd = [SIDDUMP, sid_path, '--force-rsid', *args]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.stdout


def _peek(sid_path, ranges):
    out = _siddump(sid_path, '--peek-post-init', ranges)
    for line in out.splitlines():
        if line.startswith('PEEK:'):
            return {int(k, 16): int(v, 16)
                    for k, v in (t.split('=') for t in
                                 line[5:].strip().split(','))}
    raise RaydenDigiUnsupported('siddump --peek-post-init produced no PEEK')


def _decode_handler(mem, at):
    """Decode one NMI handler up to its RTI.  Returns the facts it carries
    plus the low byte its vector store hands to its sibling."""
    f = {'at': at, 'term': None, 'mask_addr': None, 'low_nibble': False,
         'sibling': None}
    pending_imm = None
    for pc, mn, mode, arg, _n in decode(mem, 0, at, min(0x60, 0x100 - at)):
        if mn == 'lda' and mode == 'imm':
            pending_imm = arg
        elif mn == 'cmp' and mode == 'imm' and f['term'] is None:
            f['term'] = arg
        elif mn == 'and' and mode == 'imm' and arg == 0x0F:
            f['low_nibble'] = True
        elif mn == 'ora' and mode == 'imm':
            f['mask_addr'] = pc + 1
        elif mn == 'sta' and mode == 'abs' and arg == 0xFFFA:
            f['sibling'] = pending_imm
        elif mn == 'rti':
            break
    return f


def decode_core(sid_path):
    """Decode the relocated NMI handler PAIR as it actually runs.

    The vector may point at either handler when the peek is taken, so follow
    the `lda #imm / sta $FFFA` swap to the sibling and decode both.  The
    handler carrying the terminator compare is the one that reads the sample
    byte; whether it masks the LOW nibble decides the packing order.

    Returns (terminator, nibble_order, [or_mask operand addresses]).
    """
    peek = _peek(sid_path, '0000-00FF,FFFA-FFFB')
    vec = peek[0xFFFA] | (peek[0xFFFB] << 8)
    if vec > 0xFF:
        raise RaydenDigiUnsupported(
            f'NMI handler at ${vec:04X} is outside zero page — the V1 '
            f'playback core is not yet decoded')
    mem = bytes(peek[a] for a in range(0x100))
    hs = [_decode_handler(mem, vec)]
    if hs[0]['sibling'] is not None and hs[0]['sibling'] != vec:
        hs.append(_decode_handler(mem, hs[0]['sibling']))
    reader = next((h for h in hs if h['term'] is not None), None)
    masks = [h['mask_addr'] for h in hs if h['mask_addr'] is not None]
    if reader is None or not masks:
        raise RaydenDigiUnsupported(
            'the NMI handler pair carries no terminator / or_mask')
    return (reader['term'],
            'low_first' if reader['low_nibble'] else 'high_first',
            masks)


def measure_or_mask(sid_path, addrs, duration):
    """The mask is POKED into the handlers by the music player's filter
    note-init, so it is only knowable at runtime — and it must be constant
    for `DigiConfig.or_mask` to be the right home.  Measure and assert."""
    watch = ','.join(f'{a:04X}' for a in addrs)
    out = _siddump(sid_path, '--duration', str(duration), '--raw',
                   '--memwatch', watch)
    seen = {}
    for line in out.splitlines():
        if '|M:' not in line:
            continue
        body = line.split('|M:', 1)[1].split('|P:')[0]
        for tok in body.split(':'):
            a, v = tok.split('=')
            seen.setdefault(int(a, 16), []).append(int(v, 16))
    vals = {}
    for a, seq in seen.items():
        # frame 0 is pre-poke by construction; the poke lands on the music
        # player's first filter note-init
        tail = seq[1:] or seq
        uniq = sorted(set(tail))
        if len(uniq) != 1:
            raise RaydenDigiUnsupported(
                f'or_mask at ${a:04X} is NOT constant over {duration}s: '
                f'{uniq} — it would need a per-event carrier')
        vals[a] = uniq[0]
    if len(set(vals.values())) != 1:
        raise RaydenDigiUnsupported(f'handlers disagree on or_mask: {vals}')
    return next(iter(vals.values()))


# NB there is deliberately NO tick-rate measurement here.  `--pc-watch`
# under-counts by ~10% on these members: the C36 execution discriminator
# needs three consecutive ascending bus reads, and an NMI firing every
# ~105-210 cycles regularly lands between a watched instruction's opcode and
# operand fetches, breaking the signature.  The sequencer's call rate is
# recovered exactly instead by `verify_score.py`'s timing fit against the
# write stream, and the composer reproduces the member's IRQ schedule rather
# than a rate number.


# ---------------------------------------------------------------------------
# the score, decoded by running the member's own sequencer
# ---------------------------------------------------------------------------

def simulate_score(img, load, reset, tick, seq, max_events=20000):
    """Run reset+tick over a 64K image copy and read off each triggered
    event.  The duration counter is forced to expire every call: the
    countdown is pure timing, the decode is the content."""
    from py65.devices.mpu6502 import MPU
    mem = bytearray(0x10000)
    mem[load:load + len(img)] = img
    mpu = MPU(memory=mem)

    def call(addr, maxsteps=20000):
        mpu.pc = addr
        mem[0x01FC] = 0xFC          # sentinel return address $FFFC+1
        mem[0x01FD] = 0xFF
        mpu.sp = 0xFB
        for _ in range(maxsteps):
            if mpu.pc == 0xFFFD:
                return
            mpu.step()
        raise RaydenDigiUnsupported(f'sequencer runaway at ${mpu.pc:04X}')

    call(reset)
    events, seen, loop_at = [], {}, None
    for _ in range(max_events):
        mem[seq['dur_zp']] = 1
        mem[0xDD0E] = 0
        call(tick)
        if mem[0xDD0E] != 0x81:
            raise RaydenDigiUnsupported('tick did not arm the sample timer')
        stream = mem[seq['stream_zp']] | (mem[seq['stream_zp'] + 1] << 8)
        order = (mem[seq['order_zp']] | (mem[seq['order_zp'] + 1] << 8)
                 if seq['two_level'] else 0)
        key = (stream, order)
        if key in seen:
            loop_at = seen[key]
            break
        seen[key] = len(events)
        events.append({
            'sample': mem[seq['sample_zp']] // 2,
            'latch': mem[0xDD04] | (mem[0xDD05] << 8),
            'dur': mem[seq['dur_zp']] or 256,
            'ptr': mem[seq['ptr_lo']] | (mem[seq['ptr_hi']] << 8),
            'loop': mem[seq['looppoke_lo']] | (mem[seq['looppoke_hi']] << 8),
            'stream': stream, 'order': order,
        })
    return events, loop_at


def sample_nibbles(img, load, ptr, terminator, cap=1 << 20):
    """The sample's writes from `ptr` to its terminator, low nibble first."""
    out, p = [], ptr
    while len(out) < cap:
        if not (load <= p < load + len(img)):
            return None
        b = img[p - load]
        if b == terminator:
            return out
        out.append(b & 0x0F)
        out.append(b >> 4)
        p = (p + 1) & 0xFFFF
    return None


def extract_model(sid_path: str, duration: float = 60.0) -> RaydenDigiModel:
    meta, load, img = load_image(sid_path)
    if meta['play'] != 0:
        raise RaydenDigiUnsupported('not a self-driven RSID (play != $0000)')
    h = locate_head(img, load)
    if h is None:
        raise RaydenDigiUnsupported('no Rayden_Digi sequencer head')
    head, reset, tick = h
    seq = decode_sequencer(img, load, reset, tick)
    term, order, ora_addrs = decode_core(sid_path)
    or_mask = measure_or_mask(sid_path, ora_addrs, duration)
    events, loop_at = simulate_score(img, load, reset, tick, seq)
    samples, pcm = {}, {}
    for e in events:
        sid_ = e['sample']
        key = (e['ptr'], e['loop'])
        if sid_ in samples and samples[sid_] != key:
            raise RaydenDigiUnsupported(
                f'sample {sid_} has two pointer pairs {samples[sid_]} {key}')
        samples[sid_] = key
    for sid_, (ptr, lop) in samples.items():
        head_n = sample_nibbles(img, load, ptr, term)
        loop_n = sample_nibbles(img, load, lop, term)
        if head_n is None or loop_n is None:
            raise RaydenDigiUnsupported(
                f'sample {sid_} walks out of the image')
        pcm[sid_] = (head_n, loop_n)
    return RaydenDigiModel(
        sid_path=sid_path, load=load, meta=meta, head=head, reset=reset,
        tick=tick, seq=seq, or_mask=or_mask, terminator=term,
        nibble_order=order, idle_level=None,
        events=events, loop_at=loop_at, samples=samples, pcm=pcm)
