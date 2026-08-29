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
    meta = {'magic': magic, 'version': version, 'init': init, 'play': play,
            'songs': songs, 'start_song': start, 'speed': speed,
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
    raster_line: int           # driver's $D012 IRQ line
    d011: int                  # driver's $D011 value
    speed_reload: int          # steady speed immediate (frames/row - 1)
    speed_init: int            # init-time counter seed ($908E byte)
    base_latch: int            # core-init CIA2 TA latch (lo byte)
    or_mask: int               # the handlers' ORA #imm operand
    d418_init: int             # value core init writes to $D418
    orderlist: list = field(default_factory=list)  # [(pat, repeat)]
    order_term: str = 'stop'   # 'stop' ($FE) | 'loop' ($FF, to pos 0)
    patterns: dict = field(default_factory=dict)   # id -> [row bytes], $FF-truncated
    samples: dict = field(default_factory=dict)    # id -> (start_pg, end_pg, latch)
    pcm: dict = field(default_factory=dict)        # (start_pg,end_pg) -> nibble list


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

    # --- core init: TA latch + $D418 prime
    ci = _find(img, [0xA9, None, 0xA0, 0x00, 0x8D, 0x04, 0xDD])
    if ci is None:
        raise DigiOrganizerUnsupported('core init TA latch not found')
    base_latch = img[ci + 1]
    d4 = _find(img, [0xA9, None, 0x8D, 0x18, 0xD4], ci)
    if d4 is None:
        raise DigiOrganizerUnsupported('core init $D418 prime not found')
    d418_init = img[d4 + 1]

    # --- the standalone DRIVER (init vector) — strict shape probe.
    # The driver's timing (raster line, IRQ wrapper shape) is part of
    # the cycle-strict stream; members whose driver differs from the
    # probed canonical shape are REFUSED until parametrized (C13
    # positive detection, never a silent default).
    iv = meta['init'] - load
    drv = [0x78, 0xA9, 0x35, 0x85, 0x01,        # SEI; port=$35
           0xA9, None, 0x8D, 0xFE, 0xFF,        # IRQ vector lo
           0xA9, None, 0x8D, 0xFF, 0xFF,        # IRQ vector hi
           0xA9, 0x81, 0x8D, 0x0D, 0xDC,        # CIA1 int mask
           0xAD, 0x0D, 0xDC,
           0xA9, None, 0x8D, 0x12, 0xD0,        # raster line
           0xA9, None, 0x8D, 0x11, 0xD0,        # $D011
           0xA2, 0x00, 0x8E, 0x0E, 0xDC,
           0xE8, 0x8E, 0x1A, 0xD0, 0x8E, 0x19, 0xD0,
           0xA9, 0x00, 0x20, None, None,        # JSR core init
           0x58, 0x60]
    if not (0 <= iv <= len(img) - len(drv)) or any(
            p is not None and img[iv + j] != p
            for j, p in enumerate(drv)):
        raise DigiOrganizerUnsupported(
            'standalone driver shape mismatch (not the probed canonical '
            'driver — parametrize before accepting)')
    raster_line = img[iv + 24]
    d011 = img[iv + 29]
    wrapper = (img[iv + 6] | img[iv + 11] << 8) - load
    wsig = [0x48, 0x8A, 0x48, 0x98, 0x48, 0x0E, 0x19, 0xD0,
            0x20, None, None, 0xAD, 0x0D, 0xDC,
            0x68, 0xA8, 0x68, 0xAA, 0x68, 0x40]
    if not (0 <= wrapper <= len(img) - len(wsig)) or any(
            p is not None and img[wrapper + j] != p
            for j, p in enumerate(wsig)):
        raise DigiOrganizerUnsupported('IRQ wrapper shape mismatch')

    m = DigiOrganizerModel(
        sid_path=sid_path, load=load, meta=meta,
        raster_line=raster_line, d011=d011,
        speed_reload=speed_reload, speed_init=speed_init,
        base_latch=base_latch, or_mask=or_mask, d418_init=d418_init)

    # --- walk the orderlist (pos is taken &$7F by the engine) ---
    pos = 0
    while pos < 0x80:
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

    # --- patterns (32 rows, $FF-truncated) ---
    for pat, _rep in m.orderlist:
        if pat in m.patterns:
            continue
        raw = rd((pat_page << 8) + pat * 32, 32)
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
            e = s + 1
        m.samples[sid_] = (s, e, latch)
        key = (s, e)
        if key not in m.pcm:
            data = rd(s << 8, (e - s) << 8)
            nib = []
            for byte in data:
                nib.append(byte >> 4)
                nib.append(byte & 0x0F)
            m.pcm[key] = nib
    return m
