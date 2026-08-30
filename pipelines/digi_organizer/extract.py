"""Digi-Organizer — binary → typed model (standalone members).

Player layout: RE_NOTES.md. All per-member data is read from LOCATED
INSTRUCTION OPERANDS (ledger C39 — the core shifts a few bytes between
members), never from fixed offsets. The core is identified by the two
nibble-play signatures (131/131 HVSC carriers have both).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field


class DigiOrganizerUnsupported(Exception):
    pass


# ---------------------------------------------------------------------------
# image loading
# ---------------------------------------------------------------------------

def load_image(sid_path: str):
    """Return (header_meta, load_addr, image bytes)."""
    d = open(sid_path, 'rb').read()
    off = struct.unpack('>H', d[6:8])[0]
    magic = d[:4].decode('latin1')
    version = struct.unpack('>H', d[4:6])[0]
    load, init, play, songs, start = struct.unpack('>HHHHH', d[8:18])
    speed = struct.unpack('>I', d[18:22])[0]

    def _s(a, b):
        return d[a:b].split(b'\0')[0].decode('latin1')
    title, author, released = _s(0x16, 0x36), _s(0x36, 0x56), _s(0x56, 0x76)
    body = d[off:]
    if load == 0:
        load = struct.unpack('<H', body[:2])[0]
        img = body[2:]
    else:
        # Some rips declare load in the header AND carry the inline
        # prefix; detect by the prefix matching the declared load.
        if len(body) >= 2 and struct.unpack('<H', body[:2])[0] == load:
            img = body[2:]
        else:
            img = body
    # header flags (+118, v2+): clock bits 2-3 / SID model bits 4-5.
    # The raster-IRQ tick runs at the FRAME rate, so an NTSC member's
    # whole stream is 60 Hz — a PAL-defaulted rebuild plays at 5/6
    # speed with a perfect content prefix (Digi_Zak_1/_2).
    flags = struct.unpack('>H', d[0x76:0x78])[0] if version >= 2 else 0
    clock = {1: 'PAL', 2: 'NTSC', 3: 'both'}.get((flags >> 2) & 3, 'unknown')
    sid_model = {1: 6581, 2: 8580, 3: 'both'}.get((flags >> 4) & 3, 0)
    meta = {'magic': magic, 'version': version, 'init': init, 'play': play,
            'songs': songs, 'start_song': start, 'speed': speed,
            'clock': clock, 'sid_model': sid_model,
            'title': title, 'author': author, 'released': released}
    return meta, load, img


# ---------------------------------------------------------------------------
# signature location (operand wildcards = None)
# ---------------------------------------------------------------------------

def _find(img, pattern, start=0):
    """Find a byte pattern with None wildcards; return offset or None."""
    n = len(pattern)
    for i in range(start, len(img) - n + 1):
        if all(p is None or img[i + j] == p
               for j, p in enumerate(pattern)):
            return i
    return None


def _find_all(img, pattern):
    out, i = [], 0
    while True:
        j = _find(img, pattern, i)
        if j is None:
            return out
        out.append(j)
        i = j + 1


@dataclass
class DigiOrganizerModel:
    sid_path: str
    load: int
    meta: dict
    speed_reload: int          # steady speed immediate (frames/row - 1)
    speed_init: int            # init-time counter seed ($908E byte)
    base_latch: int            # core-init CIA2 TA latch (lo byte)
    or_mask: int               # the handlers' ORA #imm operand
    d418_init: int             # value core init writes to $D418
    driver: str = 'irq_vec'    # driver class (registry in extract_model)
    driver_params: dict = field(default_factory=dict)
    port_preinit: 'int | None' = None  # core-entry port stub value (Morton)
    preinit_form: 'str | None' = None  # jmp | nopslide | romcopy
    nmi_vec: str = 'fffa'              # NMI vector target: fffa | 0318 (KERNAL)
    core_tail: str = 'rts'             # core-init tail: rts | nop_rts | cli_rts
    raster_line: 'int | None' = None   # driver's $D012 IRQ line (None = env)
    d011: 'int | None' = None          # driver's $D011 value (None = env)
    orderlist: list = field(default_factory=list)  # [(pat, repeat)]
    order_term: str = 'stop'   # 'stop' ($FE) | 'loop' ($FF, to pos 0)
    patterns: dict = field(default_factory=dict)   # id -> [row bytes], $FF-truncated
    samples: dict = field(default_factory=dict)    # id -> (start_pg, end_pg, latch)
    pcm: dict = field(default_factory=dict)        # (start_pg,end_pg) -> nibble list
    # sample ids whose table row uses the engine's DEGENERATE one-page
    # form (end <= start, clamped to start+1 by a branch in the trigger)
    onepage_degenerate: list = field(default_factory=list)
    # the measured facts a universal driver reproduces (see _driver_facts)
    driver_facts: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# THE DRIVER DECODER — measure the facts, never recognise a shape
# ---------------------------------------------------------------------------
# opcode -> (mnemonic, length, cycles)
_OPS = {
    0x78: ('sei', 1, 2), 0x58: ('cli', 1, 2), 0x60: ('rts', 1, 6),
    0x40: ('rti', 1, 6), 0xEA: ('nop', 1, 2),
    0xA9: ('lda#', 2, 2), 0xA2: ('ldx#', 2, 2), 0xA0: ('ldy#', 2, 2),
    0x85: ('staz', 2, 3), 0x86: ('stxz', 2, 3), 0x84: ('styz', 2, 3),
    0x8D: ('sta', 3, 4), 0x8E: ('stx', 3, 4), 0x8C: ('sty', 3, 4),
    0xAD: ('lda', 3, 4), 0xAE: ('ldx', 3, 4), 0xAC: ('ldy', 3, 4),
    0xA5: ('ldaz', 2, 3),
    0x20: ('jsr', 3, 6), 0x4C: ('jmp', 3, 3),
    0xAA: ('tax', 1, 2), 0x8A: ('txa', 1, 2), 0xA8: ('tay', 1, 2),
    0x98: ('tya', 1, 2), 0xE8: ('inx', 1, 2), 0xCA: ('dex', 1, 2),
    0x48: ('pha', 1, 3), 0x68: ('pla', 1, 4),
    0xEE: ('inc', 3, 6), 0xCE: ('dec', 3, 6), 0x0E: ('asl', 3, 6),
    0x2C: ('bit', 3, 4), 0x29: ('and#', 2, 2), 0x09: ('ora#', 2, 2),
    0xC9: ('cmp#', 2, 2), 0xE0: ('cpx#', 2, 2), 0xCD: ('cmp', 3, 4),
    0xD0: ('bne', 2, 2), 0xF0: ('beq', 2, 2),
    0x10: ('bpl', 2, 2), 0x30: ('bmi', 2, 2),
}
_STORES = {'sta': 'a', 'stx': 'x', 'sty': 'y',
           'staz': 'a', 'stxz': 'x', 'styz': 'y'}


def _decode_driver(img, load, meta, core_base, core_plus, tick_imm):
    """Walk the member's driver and MEASURE what it contributes.

    No catalogue of known shapes: the walk reports the machine STATE the
    driver establishes, the CYCLES before it hands over to the core (the
    sample clock's phase against the frame clock), what the CPU does
    afterwards, and the per-interrupt wrapper — the four things that reach
    the write stream (ledger C40). An unfamiliar driver is therefore
    decoded rather than refused.
    """
    def at(pc):
        o = img[pc - load]
        if o not in _OPS:
            raise DigiOrganizerUnsupported(
                f'driver decode: unknown opcode ${o:02X} at ${pc:04X}')
        mn, ln, cy = _OPS[o]
        ops = img[pc - load + 1:pc - load + ln]
        arg = (ops[0] | ops[1] << 8) if ln == 3 else (ops[0] if ln == 2 else None)
        return mn, ln, cy, arg

    def name(addr, val, regs):
        """A store's token, recognising the few structural targets."""
        if addr in (0xFFFE, 0xFFFF, 0x0314, 0x0315, 0xFFFA, 0xFFFB):
            return None                       # vector halves, paired below
        if addr == tick_imm:
            # The sequencer's speed immediate. The POKED value is the
            # member's tempo, so it is musical and must be recovered: the
            # walk records where the value came from and reads it.
            if isinstance(regs['a'], tuple) and regs['a'][0] == 'from':
                poked.append(img[regs['a'][1] - load])
            elif val is not None:
                poked.append(val)
            return 'SPD'
        if isinstance(val, tuple):
            val = img[val[1] - load] if val[0] == 'from' else None
        if val is None:
            # a store whose value the walk cannot know statically and which
            # is not one of the structural targets: refuse rather than guess
            raise DigiOrganizerUnsupported(
                f'driver decode: store to ${addr:04X} of an unknown value')
        if addr >= 0x0100 and not 0xD000 <= addr <= 0xDFFF:
            # the driver's own scratch/SMC byte, not an environment
            # register: private state, redirected to a byte of ours
            return f'S{scratch.setdefault(addr, len(scratch))}={val:02x}'
        return f'{addr:02x}={val:02x}' if addr < 0x100 else f'{addr:04x}={val:02x}'

    toks, cyc, entry, pc = [], 0, None, meta['init']
    cyc_post = 0
    scratch = {}
    post_pcs, post_cyc = [], {}
    poked = []
    regs = {'a': 0, 'x': None, 'y': None}     # RSID enters with A = subtune
    vec = {}
    seen = set()
    phase = 'pre'
    post, tail, wrapper_addr = [], 'rts', None
    guard = 0
    while True:
        guard += 1
        if guard > 400:
            raise DigiOrganizerUnsupported('driver decode: walk did not settle')
        mn, ln, cy, arg = at(pc)
        out = toks if phase == 'pre' else post
        if mn in ('jsr', 'jmp') and arg in (core_base, core_plus):
            if phase == 'pre':
                cyc += cy
                entry = 'core40' if arg == core_plus else 'core'
                phase = 'post'
                pc += ln
                if mn == 'jmp':               # entered via a JSR'd sub: the
                    return_pc = _RET.pop() if _RET else None   # core RTSes back
                    if return_pc is not None:
                        pc = return_pc
                continue
            raise DigiOrganizerUnsupported('driver decode: second core call')
        if mn == 'jsr':                       # inline a helper subroutine
            _RET.append(pc + ln)
            pc = arg
            if phase == 'pre':
                cyc += cy
            continue
        if mn == 'rts':
            if _RET:
                pc = _RET.pop()
                if phase == 'pre':
                    cyc += cy
                continue
            tail = 'rts'
            break
        if mn == 'jmp':
            if arg == pc:                     # jmp self = the idle lock
                tail = 'lock'
                break
            if arg in seen:
                raise DigiOrganizerUnsupported('driver decode: loop in driver')
            seen.add(arg)
            if phase == 'pre':
                cyc += cy
            pc = arg
            continue
        here = cyc if phase == 'pre' else cyc_post
        mark = len(out)
        if mn == 'sei':
            out.append(f'SEI@{here}')
        elif mn == 'cli':
            out.append(f'CLI@{here}')
        elif mn in _STORES:
            r = _STORES[mn]
            if arg in (0xFFFE, 0xFFFF, 0x0314, 0x0315, 0xFFFA, 0xFFFB):
                # a vector half; emit the token once BOTH halves are in,
                # since originals install them in either order
                vec[arg] = regs[r]
                pair = {0xFFFE: (0xFFFE, 0xFFFF, 'IRQ'),
                        0xFFFF: (0xFFFE, 0xFFFF, 'IRQ'),
                        0x0314: (0x0314, 0x0315, 'IRQK'),
                        0x0315: (0x0314, 0x0315, 'IRQK'),
                        0xFFFA: (0xFFFA, 0xFFFB, 'NMI'),
                        0xFFFB: (0xFFFA, 0xFFFB, 'NMI')}[arg]
                lo_a, hi_a, tk = pair
                if lo_a in vec and hi_a in vec and tk not in out:
                    out.append(f'{tk}@{here}')
                    if tk in ('IRQ', 'IRQK') and vec[hi_a] is not None:
                        wrapper_addr = (vec[hi_a] << 8) | vec[lo_a]
            elif isinstance(regs[r], tuple) and regs[r][0] == 'rmw' \
                    and regs[r][1] == arg:
                out.append(f'AND:{arg:04x}={regs[r][2]:02x}@{here}')
            else:
                t = name(arg, regs[r], regs)
                if t:
                    out.append(f'{t}@{here}')
        elif mn in ('lda#', 'ldx#', 'ldy#'):
            regs[mn[2]] = arg
        elif mn in ('lda', 'ldx', 'ldy', 'ldaz'):
            reg = mn[2] if mn != 'ldaz' else 'a'
            if 0xD000 <= (arg or 0) <= 0xDFFF:
                out.append(f'R:{arg:04x}@{here}')   # an interrupt ack
                regs[reg] = None
            else:
                regs[reg] = ('from', arg)      # a value fetched from memory
        elif mn in ('tax', 'txa', 'tay', 'tya'):
            m = {'tax': ('a', 'x'), 'txa': ('x', 'a'),
                 'tay': ('a', 'y'), 'tya': ('y', 'a')}[mn]
            regs[m[1]] = regs[m[0]]
        elif mn == 'inx':
            regs['x'] = None if regs['x'] is None else (regs['x'] + 1) & 0xFF
        elif mn == 'dex':
            regs['x'] = None if regs['x'] is None else (regs['x'] - 1) & 0xFF
        elif mn == 'and#':
            # a read-modify-write on an environment register: its RESULT
            # depends on what the environment already holds, so it is
            # reproduced as the operation, not as a value
            if out and out[-1].startswith('R:'):
                regs['a'] = ('rmw', int(out.pop()[2:].split('@')[0], 16), arg)
            else:
                regs['a'] = None
        elif mn == 'dec':
            out.append(f'DEC:{arg:04x}@{here}')
        elif mn in ('bne', 'beq', 'bpl', 'bmi'):
            dest = pc + ln + (arg - 256 if arg > 127 else arg)
            if dest <= pc:                     # backward = a loop
                if phase != 'post':
                    raise DigiOrganizerUnsupported(
                        'driver decode: loop before the core call')
                # A counted startup delay. It runs with interrupts LIVE, so
                # its loop PERIOD is observable and the composer emits an
                # equivalent loop over its own scratch counters — but the
                # counter SEEDS are ordinary scheduled writes, so only the
                # loop BODY is trimmed here. The body begins at the first
                # decrement of a scratch byte after the CLI.
                decs = [(tk, tpc) for tk, tpc in zip(post, post_pcs)
                        if tk.startswith('DEC:')]
                if not decs:
                    raise DigiOrganizerUnsupported(
                        'driver decode: a delay loop with no counter')
                loop_at = min(tpc for _tk, tpc in decs)
                outer = scratch.get(int(decs[0][0][4:].split('@')[0], 16))
                inner = [i for a, i in sorted(scratch.items(), key=lambda kv: kv[1])
                         if i != outer and any(
                             t.startswith(f'S{i}=') for t in post)]
                post[:] = [tk for tk, tpc in zip(post, post_pcs)
                           if tpc < loop_at]
                cyc_post = post_cyc.get(loop_at, cyc_post)
                tail = 'delay=%s' % ':'.join(
                    str(x) for x in ([outer] + inner[:2]))
                break
            if phase == 'pre':
                cyc += cy + 1
            pc = dest                          # assume taken (the init path)
            continue
        elif mn in ('nop', 'bit', 'cmp#', 'cpx#', 'ora#', 'cmp', 'inc',
                    'asl', 'pha', 'pla'):
            pass
        while len(post_pcs) < len(post):
            post_pcs.append(pc)
        if phase == 'pre':
            cyc += cy
        else:
            post_cyc.setdefault(pc, cyc_post)
            cyc_post += cy
        pc += ln
    return dict(pre=','.join(toks), cyc=cyc, entry=entry or 'core',
                post=','.join(post), cyc_post=cyc_post, tail=tail,
                wrapper=wrapper_addr,
                speed_poke=(poked[0] if poked else None))


_RET = []


def _decode_wrapper(img, load, addr, core_plus3):
    """Tokenise the per-interrupt wrapper into BEHAVIOURS.

    This is the one part of a driver whose instruction boundaries are
    observable — NMIs are non-maskable, so they fire while it runs and are
    taken at whatever instruction is executing. So it is decoded to a token
    sequence whose emitted lengths follow from the tokens, rather than to a
    cycle count. The vocabulary is small and structural (save the
    registers, acknowledge, wait for a scanline, call the tick, exit); a
    wrapper built from an unseen COMBINATION of them needs no new code.
    """
    ins = []
    pc, guard = addr, 0
    while guard < 60:
        guard += 1
        o = img[pc - load]
        if o not in _OPS:
            raise DigiOrganizerUnsupported(
                f'wrapper decode: unknown opcode ${o:02X} at ${pc:04X}')
        mn, ln, _cy = _OPS[o]
        ops = img[pc - load + 1:pc - load + ln]
        arg = (ops[0] | ops[1] << 8) if ln == 3 else (ops[0] if ln == 2 else None)
        ins.append((mn, arg, pc, ln))
        if mn in ('rti', 'jmp'):
            break
        pc += ln
    toks, i = [], 0
    while i < len(ins):
        mn, arg, at_, ln = ins[i]
        nxt = ins[i + 1][0] if i + 1 < len(ins) else None
        seq = [x[0] for x in ins[i:i + 6]]
        if seq[:5] in (['pha', 'txa', 'pha', 'tya', 'pha'],
                       ['pha', 'tya', 'pha', 'txa', 'pha']):
            toks.append('save'); i += 5; continue
        if seq[:6] == ['pla', 'tay', 'pla', 'tax', 'lda', 'pla'] \
                and ins[i + 4][1] == 0xDC0D:
            toks.append('restore_cia'); i += 6; continue
        if seq[:5] in (['pla', 'tay', 'pla', 'tax', 'pla'],
                       ['pla', 'tax', 'pla', 'tay', 'pla']):
            toks.append('restore'); i += 5; continue
        if mn in ('asl', 'inc', 'dec') and arg == 0xD019:
            toks.append(f'ack={mn}'); i += 1; continue
        if mn == 'lda#' and nxt == 'sta' and ins[i + 1][1] == 0xD019:
            toks.append('ack=lda'); i += 2; continue
        if mn == 'lda#' and nxt == 'cmp' and ins[i + 1][1] == 0xD012:
            toks.append(f'spin={arg:02x}'); i += 3; continue
        if mn in ('lda', 'ldaz') and nxt == 'cmp#' and ins[i + 2][0] == 'bne':
            toks.append('gate'); i += 3; continue
        if mn in ('lda', 'ldaz') and nxt == 'beq':
            toks.append('gate_beq'); i += 2; continue
        if mn == 'jsr' and arg == core_plus3:
            toks.append('tick'); i += 1; continue
        if mn == 'lda' and arg is not None and 0xD000 <= arg <= 0xDFFF:
            toks.append(f'read={arg:04x}'); i += 1; continue
        if mn == 'lda#' and nxt == 'sta':
            toks.append(f'set={ins[i + 1][1]:04x}:{arg:02x}'); i += 2; continue
        if mn == 'nop':
            toks.append('pad=2'); i += 1; continue
        if mn == 'bit':
            toks.append('pad=4'); i += 1; continue
        if mn == 'rti':
            toks.append('rti'); i += 1; continue
        if mn == 'jmp':
            toks.append(f'jmp={arg:04x}'); i += 1; continue
        raise DigiOrganizerUnsupported(
            f'wrapper decode: unhandled {mn} at ${at_:04X}')
    return ','.join(toks)


_RET = []


def extract_model(sid_path: str) -> DigiOrganizerModel:
    meta, load, img = load_image(sid_path)

    def rd(addr, n=1):
        o = addr - load
        if not (0 <= o and o + n <= len(img)):
            raise DigiOrganizerUnsupported(
                f'read ${addr:04X}+{n} outside image '
                f'(${load:04X}-${load + len(img):04X})')
        return img[o:o + n]

    # --- locate the two NMI handlers (the family identity) ---
    hi_sig = [0x4A, 0x4A, 0x4A, 0x4A, 0x09, None, 0x8D, 0x18, 0xD4]
    lo_sig = [0x29, 0x0F, 0x09, None, 0x8D, 0x18, 0xD4]
    hi_off = _find(img, hi_sig)
    lo_off = _find(img, lo_sig)
    if hi_off is None or lo_off is None:
        raise DigiOrganizerUnsupported('nibble-play signatures not found')
    or_mask = img[hi_off + 5]
    if img[lo_off + 3] != or_mask:
        raise DigiOrganizerUnsupported(
            f'handlers disagree on or_mask: '
            f'${img[hi_off + 5]:02X} vs ${img[lo_off + 3]:02X}')

    # --- sequencer tick head: DEC ctr / BMI +1 / RTS / LDA #spd / STA ctr
    tick = _find(img, [0xCE, None, None, 0x30, 0x01, 0x60,
                       0xA9, None, 0x8D, None, None])
    if tick is None:
        raise DigiOrganizerUnsupported('sequencer tick head not found')
    speed_reload = img[tick + 7]
    speedctr = img[tick + 1] | img[tick + 2] << 8

    # --- init-speed byte: BIT $9086 / LDA $908E / STA ctr
    isp = _find(img, [0x2C, None, None, 0xAD, None, None,
                      0x8D, (speedctr & 0xFF), (speedctr >> 8)])
    if isp is None:
        raise DigiOrganizerUnsupported('init-speed loader not found')
    speed_init = rd(img[isp + 4] | img[isp + 5] << 8)[0]

    # --- orderlist fetch: LDA $9200,x / TAX / CPX #$FE
    olf = _find(img, [0xBD, None, None, 0xAA, 0xE0, 0xFE])
    if olf is None:
        raise DigiOrganizerUnsupported('orderlist fetch not found')
    ol_base = img[olf + 1] | img[olf + 2] << 8

    # --- pattern page base: ROL chain tail ... CLC / ADC #pg / STA
    ppb = _find(img, [0xEA, 0xEA, 0xEA, 0xEA, 0x8D, None, None,
                      0xAD, None, None, 0x18, 0x69, None, 0x8D])
    if ppb is None:
        raise DigiOrganizerUnsupported('pattern page base not found')
    pat_page = img[ppb + 12]

    # --- sample table: ASL/ASL/TAY/LDA $92FC,y
    smf = _find(img, [0x0A, 0x0A, 0xA8, 0xB9, None, None])
    if smf is None:
        raise DigiOrganizerUnsupported('sample table fetch not found')
    smp_base = img[smf + 4] | img[smf + 5] << 8

    # --- NMI vector TARGET: canon cores swap $FFFA/$FFFB; a
    # KERNAL-path member (port $36, KERNAL banked in) re-points ALL
    # NINE vector-swap operands at $0318/$0319 (the KERNAL NMI RAM
    # vector) — probe the core-init store pair, then REQUIRE the other
    # sites to agree (a mixed core would be a different variant).
    vecp = _find(img, [0xA0, 0x91, 0x8C, None, None,
                       0xA9, 0x57, 0x8D, None, None])
    if vecp is None:
        raise DigiOrganizerUnsupported('core-init NMI vector stores not found')
    hi_t = img[vecp + 3] | img[vecp + 4] << 8
    lo_t = img[vecp + 8] | img[vecp + 9] << 8
    if (lo_t, hi_t) == (0xFFFA, 0xFFFB):
        nmi_vec = 'fffa'
    elif (lo_t, hi_t) == (0x0318, 0x0319):
        nmi_vec = '0318'
    else:
        raise DigiOrganizerUnsupported(
            f'NMI vector target ${lo_t:04X}/${hi_t:04X} unclassified')
    pair = bytes((lo_t & 0xFF, lo_t >> 8))
    n_sites = img.count(b'\x8d' + pair) + img.count(b'\x8c' + pair)
    if n_sites < 8:
        raise DigiOrganizerUnsupported(
            f'NMI vector sites inconsistent ({n_sites} of >=8 use '
            f'${lo_t:04X})')

    # --- core init: TA latch + $D418 prime
    ci = _find(img, [0xA9, None, 0xA0, 0x00, 0x8D, 0x04, 0xDD])
    if ci is None:
        raise DigiOrganizerUnsupported('core init TA latch not found')
    base_latch = img[ci + 1]
    d4 = _find(img, [0xA9, None, 0x8D, 0x18, 0xD4], ci)
    if d4 is None:
        raise DigiOrganizerUnsupported('core init $D418 prime not found')
    d418_init = img[d4 + 1]

    # --- the standalone DRIVER (init vector) — a CLASS REGISTRY of
    # strict shape probes (C13 positive detection). The driver's cycle
    # shape up to the core-init call sets the CIA2-NMI PHASE for the
    # whole song, so each class is mirrored cycle-for-cycle by the
    # composer; a member matching NO class is REFUSED (never defaulted).
    core_base = load + tick - 0x87
    iv = meta['init'] - load

    # --- core ENTRY stub: the $9000 JMP may route through a PORT
    # PRE-INIT (`SEI / LDA #port / STA $01 / JMP core+$40`) — the
    # Morton variant sets $01=$35 here because its driver never does;
    # other members carry the stub unreached (editor leftover).
    cb = core_base - load

    def _probe_port_preinit():
        # Only meaningful when a driver actually ENTERS via the $9000
        # JMP — an unreached entry stub is editor leftover (Digitune's
        # driver JSRs core+$40 directly past a stale stub). Returns
        # (form, port): 'jmp' (SEI/port/JMP core+$40), 'nopslide'
        # (SEI/port/NOP... falling into core init), or 'romcopy' (the
        # KERNAL-$E000-$FFFF copy-under-itself + DEC $01 — how a
        # KERNAL-path member banks the ROM 'out' yet keeps its IRQ
        # chain: ~131k pre-timer cycles, part of the grid phase).
        ent = img[cb + 1] | img[cb + 2] << 8
        if ent == core_base + 0x40:
            return None
        so = ent - load
        head = [0x78, 0xA9, None, 0x85, 0x01]
        if not _match(so, head):
            raise DigiOrganizerUnsupported(
                f'core entry routes to ${ent:04X} — no port stub head')
        port = img[so + 2]
        tail = so + 5
        if _match(tail, [0x4C, (core_base + 0x40) & 0xFF,
                         (core_base + 0x40) >> 8]):
            return ('jmp', port)
        end = cb + 0x40
        if tail < end and all(img[k] == 0xEA for k in range(tail, end)):
            return ('nopslide', port)
        romcopy = [0xA9, 0xE0, 0x85, 0x21, 0xA0, 0x00, 0x84, 0x20,
                   0xB1, 0x20, 0x91, 0x20, 0xC8, 0xD0, 0xF9,
                   0xE6, 0x21, 0xD0, 0xF5, 0xC6, 0x01]
        if _match(tail, romcopy) and tail + len(romcopy) == end:
            return ('romcopy', port)
        raise DigiOrganizerUnsupported(
            f'core entry stub at ${ent:04X}: unclassified tail')

    # --- core-init TAIL byte (core+$7F): canon RTS; NOP / CLI variants
    # fall through into the $60 byte at core+$80. Post-timer, but it
    # shifts the idle-loop phase against the NMI grid = a constant
    # per-write latency delta under Mode-2 — mirror it exactly.
    tail_b = img[cb + 0x7F]
    if tail_b == 0x60:
        core_tail = 'rts'
    elif tail_b == 0xEA and img[cb + 0x80] == 0x60:
        core_tail = 'nop_rts'
    elif tail_b == 0x58 and img[cb + 0x80] == 0x60:
        core_tail = 'cli_rts'
    else:
        raise DigiOrganizerUnsupported(
            f'core-init tail ${tail_b:02X} at core+$7F unclassified')

    def _match(off, pat):
        return (0 <= off <= len(img) - len(pat)) and all(
            p is None or img[off + j] == p for j, p in enumerate(pat))

    # MEASURE the driver rather than recognise it (ledger C40). The walk
    # below replaced fourteen hand-written shape probes: an unfamiliar
    # driver is now decoded instead of refused, and the facts come from the
    # binary instead of from a transcription (transcribing them by hand is
    # exactly what went wrong the first time this was attempted).
    _RET.clear()
    facts = _decode_driver(img, load, meta, core_base, core_base + 0x40,
                           load + tick + 7)
    if facts['wrapper'] is None:
        raise DigiOrganizerUnsupported('driver installs no IRQ vector')
    facts['wrap'] = _decode_wrapper(img, load, facts['wrapper'], core_base + 3)
    # a label for reports and the regression portfolio — never for emission
    driver = f"{facts['tail']}/{facts['wrap'].split(',')[0]}"
    dp = {'core_entry': facts['entry']}

    # Any class whose recorded entry is 'core' goes through the $9000
    # JMP (and may hit the port pre-init stub); a 'core40' entry
    # bypasses it, making the stub dead.
    enters_via_jmp = dp.get('core_entry', 'core') == 'core'
    pre = _probe_port_preinit() if enters_via_jmp else None
    preinit_form, port_preinit = pre if pre else (None, None)

    # A poke of the tick's speed immediate BEFORE the core call lands
    # before anything reads it, so it replaces the image byte for both the
    # init seed and every steady reload — the file's byte is then editor
    # residue. Poked AFTER, the image byte really is the first row's
    # duration and the poked value is the steady tempo.
    if facts['speed_poke'] is not None:
        if 'SPD' in facts['pre']:
            speed_reload = speed_init = facts['speed_poke']
        else:
            dp['speed_poke'] = facts['speed_poke']

    m = DigiOrganizerModel(
        sid_path=sid_path, load=load, meta=meta, driver_facts=facts,
        driver=driver, driver_params=dp, port_preinit=port_preinit,
        preinit_form=preinit_form, nmi_vec=nmi_vec,
        core_tail=core_tail,
        raster_line=dp.get('raster'), d011=dp.get('d011'),
        speed_reload=speed_reload, speed_init=speed_init,
        base_latch=base_latch, or_mask=or_mask, d418_init=d418_init)

    # --- walk the orderlist (pos is taken &$7F by the engine) ---
    # An UNTERMINATED authored orderlist runs the walk into the member's
    # own PLAYER CODE (Digi_Zak_2: the sphere driver init sits at $9240,
    # right after 32 authored entries — `SEI/LDA #$35/...` read as
    # "pattern 120 repeat 41" + garbage sample-table rows, latch $00).
    # Memory at/after a located code/table structure can never hold
    # authored entries (the player would be corrupt), so the walk stops
    # there: the song plays once and ends. The engine WOULD sonify its
    # own code if left running (~90 s past the recorded songlength —
    # measured: order pos <= $1E over the whole ratified window), which
    # is not musical content (C7); represent the authored end as 'stop'.
    code_barrier = min((a for a in (meta['init'], smp_base)
                        if a >= ol_base), default=None)
    pos = 0
    while pos < 0x80:
        if code_barrier is not None and ol_base + pos * 2 + 2 > code_barrier:
            m.order_term = 'stop'
            break
        b0, b1 = rd(ol_base + pos * 2, 2)
        if b0 == 0xFE:
            m.order_term = 'stop'
            break
        if b0 == 0xFF:
            m.order_term = 'loop'
            break
        m.orderlist.append((b0, b1 & 0x7F))
        pos += 1
    else:
        raise DigiOrganizerUnsupported('orderlist has no terminator')

    # --- patterns (32 rows, $FF-truncated; a slot past the image end
    # is PLAYED ENVIRONMENT, C29 — served CPU-eye like the PCM) ---
    for pat, _rep in m.orderlist:
        if pat in m.patterns:
            continue
        raw = _read_pcm(sid_path, load, img, (pat_page << 8) + pat * 32, 32)
        rows = []
        for b in raw:
            if b == 0xFF:
                break
            rows.append(b)
        m.patterns[pat] = rows

    # --- samples ---
    used = sorted({b for rows in m.patterns.values() for b in rows if b})
    for sid_ in used:
        s, e, latch = rd(smp_base + sid_ * 4, 3)
        if s >= e:
            # The engine's DEGENERATE one-page row: the trigger clamps
            # `end = start + 1`, so the sample is one page either way and
            # the audio is identical to a row written `end = start + 1`.
            # But the clamp is a BRANCH, so which form the row uses costs
            # 2 cycles in the trigger — signal under the Mode-2 verdict,
            # and NOT derivable from the page count (the corpus has both
            # forms at one page). Recorded so the composer can emit the
            # same form; never a musical difference.
            e = s + 1
            m.onepage_degenerate.append(sid_)
        m.samples[sid_] = (s, e, latch)
        key = (s, e)
        if key not in m.pcm:
            data = _read_pcm(sid_path, load, img, s << 8, (e - s) << 8)
            nib = []
            for byte in data:
                nib.append(byte >> 4)
                nib.append(byte & 0x0F)
            m.pcm[key] = nib
    return m


def _read_pcm(sid_path, load, img, addr, n):
    """Sample bytes; a range past the image end is PLAYED ENVIRONMENT
    RAM (ledger C29) — serve those bytes CPU-EYE via `siddump
    --peek-post-init` (libsidplayfp ground truth, never py65/zeros)."""
    end_img = load + len(img)
    in_img = img[addr - load:min(addr + n, end_img) - load] \
        if addr < end_img else b''
    missing = n - len(in_img)
    if missing <= 0:
        return in_img
    lo = addr + len(in_img)
    hi = lo + missing - 1
    if hi > 0xFFFF:
        raise DigiOrganizerUnsupported(
            f'sample range ${addr:04X}+{n} wraps past $FFFF')
    import subprocess
    r = subprocess.run(
        ['siddump', sid_path, '--force-rsid', '--duration', '0',
         '--peek-post-init', f'{lo:X}-{hi:X}'],
        capture_output=True, text=True)
    got = {}
    for line in r.stdout.splitlines():
        if line.startswith('PEEK:'):
            for kv in line[5:].strip().split(','):
                k, v = kv.split('=')
                got[int(k, 16)] = int(v, 16)
    if len(got) >= missing:
        tail = bytes(got[a] for a in range(lo, hi + 1))
        return in_img + tail
    raise DigiOrganizerUnsupported(
        f'peek-post-init failed for ${lo:04X}-${hi:04X}')
