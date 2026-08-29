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

    driver = None
    dp = {}  # driver params

    # class 'irq_vec' (Heavy-Beat / Suffer_the_Noise / TDU / Koester /
    # Digi-Zak_4_Mix): SEI, port, IRQ vector, mask $81+ack, raster,
    # $D011, stop TA, enable raster, JSR core, CLI RTS.
    pat_a = [0x78, 0xA9, 0x35, 0x85, 0x01,
             0xA9, None, 0x8D, 0xFE, 0xFF,
             0xA9, None, 0x8D, 0xFF, 0xFF,
             0xA9, 0x81, 0x8D, 0x0D, 0xDC,
             0xAD, 0x0D, 0xDC,
             0xA9, None, 0x8D, 0x12, 0xD0,
             0xA9, None, 0x8D, 0x11, 0xD0,
             0xA2, 0x00, 0x8E, 0x0E, 0xDC,
             0xE8, 0x8E, 0x1A, 0xD0, 0x8E, 0x19, 0xD0,
             0xA9, 0x00, 0x20, None, None,
             0x58, 0x60]
    wrap_ack = [0x48, 0x8A, 0x48, 0x98, 0x48, 0x0E, 0x19, 0xD0,
                0x20, None, None, 0xAD, 0x0D, 0xDC,
                0x68, 0xA8, 0x68, 0xAA, 0x68, 0x40]
    wrap_noack = [0x48, 0x8A, 0x48, 0x98, 0x48, 0x0E, 0x19, 0xD0,
                  0x20, None, None,
                  0x68, 0xA8, 0x68, 0xAA, 0x68, 0x40]
    if _match(iv, pat_a):
        w = (img[iv + 6] | img[iv + 11] << 8) - load
        if img[iv + 48] | img[iv + 49] << 8 != core_base:
            raise DigiOrganizerUnsupported('irq_vec: JSR is not core init')
        if _match(w, wrap_ack):
            driver = 'irq_vec'
            dp = {'raster': img[iv + 24], 'd011': img[iv + 29]}

    # class 'nmi_first' (Digitune / N_H_Digi / Samples1 / Digi_Music_1 /
    # Memomay / Lets_Do_It): [SEI] port, NMI vector pre-set, A=0 JSR
    # core(+$40), IRQ vector, mask, ack, raster, $D011, X-form, CLI RTS.
    if driver is None:
        sei = img[iv:iv + 1] == b'\x78'
        p0 = iv + (1 if sei else 0)
        pat_b = [0xA9, 0x35, 0x85, 0x01,
                 0xA9, None, 0x8D, 0xFB, 0xFF,
                 0xA9, None, 0x8D, 0xFA, 0xFF,
                 0xA9, 0x00, 0x20, None, None,
                 0xA9, None, 0x8D, 0xFE, 0xFF,
                 0xA9, None, 0x8D, 0xFF, 0xFF,
                 0xA9, 0x81, 0x8D, 0x0D, 0xDC,
                 0xAD, 0x0D, 0xDC,
                 0xA9, None, 0x8D, 0x12, 0xD0,
                 0xA9, None, 0x8D, 0x11, 0xD0,
                 0xA2, 0x00, 0x8E, 0x0E, 0xDC,
                 0xE8, 0x8E, 0x1A, 0xD0, 0x8E, 0x19, 0xD0,
                 0x58, 0x60]
        if _match(p0, pat_b):
            entry = img[p0 + 17] | img[p0 + 18] << 8
            if entry == core_base:
                core_entry = 'core'
            elif entry == core_base + 0x40:
                core_entry = 'core40'
            else:
                raise DigiOrganizerUnsupported(
                    'nmi_first: JSR is not core init')
            # The NMI pre-set operands are DEAD (no NMI can fire before
            # core init, which re-points the vector) — the composer
            # emits its own idle label there; only the instruction
            # shape matters for the cycle skeleton.
            w = (img[p0 + 20] | img[p0 + 25] << 8) - load
            if _match(w, wrap_noack):
                driver = 'nmi_first'
                dp = {'raster': img[p0 + 38], 'd011': img[p0 + 43],
                      'sei': sei, 'core_entry': core_entry}

    # class 'xreg' (Demi-Demo_4 / Simpsons / Xmas_Chortles ×2): X-reg
    # form; ONE immediate serves raster line + both CIA masks; STA
    # $DC0E relies on A=0 (the RSID song number).
    if driver is None:
        pat_c = [0x78, 0xA2, 0x35, 0x86, 0x01,
                 0xA2, None, 0x8E, 0x12, 0xD0,
                 0x8E, 0x0D, 0xDC, 0x8E, 0x0D, 0xDD,
                 0xAE, 0x0D, 0xDC, 0xAE, 0x0D, 0xDD,
                 0xA2, 0x01, 0x8E, 0x19, 0xD0, 0x8E, 0x1A, 0xD0,
                 0x8D, 0x0E, 0xDC,
                 0xA9, None, 0x8D, 0x11, 0xD0,
                 0xA9, None, 0x8D, 0xFF, 0xFF,
                 0xA9, None, 0x8D, 0xFE, 0xFF,
                 0x20, None, None,
                 0x58, 0x60]
        wrap_inc = [0x48, 0x8A, 0x48, 0x98, 0x48, 0xEE, 0x19, 0xD0,
                    0x20, None, None, 0xAD, 0x0D, 0xDC,
                    0x68, 0xA8, 0x68, 0xAA, 0x68, 0x40]
        if _match(iv, pat_c[:-5]):
            q = iv + len(pat_c) - 5          # after the vector stores
            has_bit = img[q] == 0x2C
            if has_bit:
                q += 3                        # BIT abs filler (Xmas form)
            if img[q] != 0x20 or img[q + 3:q + 5] != b'\x58\x60':
                raise DigiOrganizerUnsupported('xreg: tail shape mismatch')
            entry = img[q + 1] | img[q + 2] << 8
            if entry == core_base:
                core_entry = 'core'
            elif entry == core_base + 0x40:
                core_entry = 'core40'
            else:
                raise DigiOrganizerUnsupported('xreg: JSR is not core init')
            w = (img[iv + 44] | img[iv + 39] << 8) - load
            wrap_inc_bit = wrap_inc[:8] + [0x2C, None, None] + wrap_inc[8:]
            if _match(w, wrap_inc_bit if has_bit else wrap_inc):
                driver = 'xreg'
                dp = {'raster': img[iv + 6], 'd011': img[iv + 34],
                      'core_entry': core_entry, 'bit_pad': has_bit}

    # class 'bare_stub' (the Morton_Adam shape ×7): LDA #0 JSR core JMP L;
    # L: [NOP] IRQ vector, mask $7F, enable raster, ack, CLI RTS. No
    # port / raster-line / $D011 writes — the environment's defaults
    # serve, and they cancel between orig and rebuild by construction.
    if driver is None:
        pat_d0 = [0xA9, 0x00, 0x20, None, None, 0x4C, None, None]
        if _match(iv, pat_d0):
            if img[iv + 3] | img[iv + 4] << 8 != core_base:
                raise DigiOrganizerUnsupported(
                    'bare_stub: JSR is not core init')
            t = (img[iv + 6] | img[iv + 7] << 8) - load
            nop = img[t:t + 1] == b'\xEA'
            p1 = t + (1 if nop else 0)
            pat_d1 = [0xA9, None, 0x8D, 0xFE, 0xFF,
                      0xA9, None, 0x8D, 0xFF, 0xFF,
                      0xA9, 0x7F, 0x8D, 0x0D, 0xDC,
                      0xA9, 0x01, 0x8D, 0x1A, 0xD0,
                      0xAD, 0x0D, 0xDC, 0x58, 0x60]
            if _match(p1, pat_d1):
                w = (img[p1 + 1] | img[p1 + 6] << 8) - load
                wrap_nops = wrap_ack[:11] + [0xEA, 0xEA, 0xEA] \
                    + wrap_ack[11:]
                if _match(w, wrap_ack):
                    driver = 'bare_stub'
                    dp = {'nop': nop}
                elif _match(w, wrap_nops):
                    driver = 'bare_stub'
                    dp = {'nop': nop, 'wrap_nops': True}

    # class 'jer_lock' (Jer Digimix ×3): SEI, port, IRQ vector via an
    # A/X immediate pair, D01A=1 + a $DC0D=$01 write, $D011 read-AND-$7F
    # writeback (env-relative — cancels when mirrored), raster, JSR
    # core+$40, 14 NOPs, CLI, JMP-self LOCK (init never returns).
    if driver is None:
        pat_j = [0x78, 0xA9, 0x35, 0x85, 0x01,
                 0xA9, None, 0xA2, None,
                 0x8D, 0xFE, 0xFF, 0x8E, 0xFF, 0xFF,
                 0xA9, 0x01, 0x8D, 0x1A, 0xD0, 0x8D, 0x0D, 0xDC,
                 0xAD, 0x11, 0xD0, 0x29, 0x7F, 0x8D, 0x11, 0xD0,
                 0xA9, None, 0x8D, 0x12, 0xD0,
                 0x20, None, None] + [0xEA] * 14 + [0x58, 0x4C]
        wrap_j = [0x48, 0x8A, 0x48, 0x98, 0x48, 0xEE, 0x19, 0xD0,
                  0x20, None, None,
                  0x68, 0xA8, 0x68, 0xAA, 0xAD, 0x0D, 0xDC,
                  0x68, 0x40]
        if _match(iv, pat_j):
            if img[iv + 37] | img[iv + 38] << 8 != core_base + 0x40:
                raise DigiOrganizerUnsupported('jer_lock: JSR not core+$40')
            w = (img[iv + 6] | img[iv + 8] << 8) - load
            if _match(w, wrap_j):
                driver = 'jer_lock'
                dp = {'raster': img[iv + 32], 'core_entry': 'core40'}

    # class 'sphere' (Sphere_Chromance ×2): SEI, port, mask $7F, IRQ
    # vector, D01A=1, A=X=Y=0, JSR core+$40, $D011 AFTER, CLI RTS. The
    # WRAPPER re-writes $D011 + raster EVERY IRQ (push order Y-then-X).
    if driver is None:
        pat_s = [0x78, 0xA9, 0x35, 0x85, 0x01,
                 0xA9, 0x7F, 0x8D, 0x0D, 0xDC,
                 0xA9, None, 0x8D, 0xFE, 0xFF,
                 0xA9, None, 0x8D, 0xFF, 0xFF,
                 0xA9, 0x01, 0x8D, 0x1A, 0xD0,
                 0xA9, 0x00, 0xA2, 0x00, 0xA0, 0x00,
                 0x20, None, None,
                 0xA9, None, 0x8D, 0x11, 0xD0,
                 0x58, 0x60]
        wrap_s = [0x48, 0x98, 0x48, 0x8A, 0x48, 0xEE, 0x19, 0xD0,
                  0xA9, None, 0x8D, 0x11, 0xD0,
                  0xA9, None, 0x8D, 0x12, 0xD0,
                  0x20, None, None, 0xAD, 0x0D, 0xDC,
                  0x68, 0xAA, 0x68, 0xA8, 0x68, 0x40]
        if _match(iv, pat_s):
            if img[iv + 32] | img[iv + 33] << 8 != core_base + 0x40:
                raise DigiOrganizerUnsupported('sphere: JSR not core+$40')
            w = (img[iv + 11] | img[iv + 16] << 8) - load
            if _match(w, wrap_s):
                driver = 'sphere'
                dp = {'raster': img[w + 14], 'd011': img[w + 9],
                      'd011_init': img[iv + 35], 'core_entry': 'core40'}

    # class 'earbleed' (The_Mighty_Bulldozer ×2): SEI, port, $D011,
    # raster, D01A/D019=1, mask $7F, ack, DC0E=0, IRQ vector, A=0, JSR
    # core, CLI RTS; wrapper = INC-ack, no $DC0D read, no register-X/Y
    # ack reorder.
    if driver is None:
        pat_e = [0x78, 0xA9, 0x35, 0x85, 0x01,
                 0xA9, None, 0x8D, 0x11, 0xD0,
                 0xA9, None, 0x8D, 0x12, 0xD0,
                 0xA9, 0x01, 0x8D, 0x1A, 0xD0, 0x8D, 0x19, 0xD0,
                 0xA9, 0x7F, 0x8D, 0x0D, 0xDC,
                 0xAD, 0x0D, 0xDC,
                 0xA9, 0x00, 0x8D, 0x0E, 0xDC,
                 0xA9, None, 0x8D, 0xFE, 0xFF,
                 0xA9, None, 0x8D, 0xFF, 0xFF,
                 0xA9, 0x00, 0x20, None, None,
                 0x58, 0x60]
        wrap_e = [0x48, 0x8A, 0x48, 0x98, 0x48, 0xEE, 0x19, 0xD0,
                  0x20, None, None,
                  0x68, 0xA8, 0x68, 0xAA, 0x68, 0x40]
        if _match(iv, pat_e):
            if img[iv + 49] | img[iv + 50] << 8 != core_base:
                raise DigiOrganizerUnsupported('earbleed: JSR not core')
            w = (img[iv + 37] | img[iv + 42] << 8) - load
            if _match(w, wrap_e):
                driver = 'earbleed'
                dp = {'raster': img[iv + 11], 'd011': img[iv + 6]}

    # class 'poke_stub' (the delayed Morton shape ×4): flag=0, JSR core,
    # pokes counters ($D0 into two delay cells + $0B into an outer
    # counter), OPTIONAL speed poke (`LDA src / STA $908E` — the runtime
    # TEMPO; the image byte is only the first-row seed), JMP tail: SEI,
    # IRQ vector, mask $7F, D01A=1, ack, CLI, then a nested busy-wait
    # DELAY (~2 frames) before flag=1 unlocks the flag-gated wrapper.
    if driver is None:
        pat_p0 = [0xA9, 0x00, 0x8D, None, None,       # flag = 0
                  0x20, None, None,                   # JSR core
                  0xA9, None, 0x8D, None, None, 0x8D, None, None,
                  0xA9, None, 0x8D, None, None]       # counter pokes
        if _match(iv, pat_p0):
            if img[iv + 6] | img[iv + 7] << 8 != core_base:
                raise DigiOrganizerUnsupported('poke_stub: JSR not core')
            q = iv + 21
            speed_poke = None
            speedb = load + tick + 7                  # the tick immediate
            if img[q] == 0xAD and \
                    img[q + 3] == 0x8D and \
                    (img[q + 4] | img[q + 5] << 8) == speedb:
                speed_poke = rd(img[q + 1] | img[q + 2] << 8)[0]
                q += 6
            if img[q] != 0x4C:
                raise DigiOrganizerUnsupported('poke_stub: no JMP tail')
            t = (img[q + 1] | img[q + 2] << 8) - load
            tail_sei = img[t] == 0x78
            if not tail_sei and img[t] != 0xEA:
                raise DigiOrganizerUnsupported(
                    f'poke_stub: tail lead ${img[t]:02X} not SEI/NOP')
            pat_p1 = [None,
                      0xA9, None, 0x8D, 0xFE, 0xFF,
                      0xA9, None, 0x8D, 0xFF, 0xFF,
                      0xA9, 0x7F, 0x8D, 0x0D, 0xDC,
                      0xA9, 0x01, 0x8D, 0x1A, 0xD0,
                      0xAD, 0x0D, 0xDC, 0x58,
                      # delay: DEC outer / JSR sub / LDA outer / BNE /
                      # INC flag / RTS
                      0xCE, None, None, 0x20, None, None,
                      0xAD, None, None, 0xD0, 0xF5,
                      0xEE, None, None, 0x60,
                      # sub: two DEC/LDA/CMP#0/BNE loops + RTS
                      0xCE, None, None, 0xAD, None, None,
                      0xC9, 0x00, 0xD0, 0xF6,
                      0xCE, None, None, 0xAD, None, None,
                      0xC9, 0x00, 0xD0, 0xF6, 0x60]
            wrap_cmp = [0x48, 0x8A, 0x48, 0x98, 0x48,
                        0xAD, None, None, 0xC9, 0x01, 0xD0, 0x03,
                        0x20, None, None,
                        0x0E, 0x19, 0xD0, 0xAD, 0x0D, 0xDC,
                        0x68, 0xA8, 0x68, 0xAA, 0x68, 0x40]
            wrap_beq = [0x48, 0x8A, 0x48, 0x98, 0x48,
                        0x0E, 0x19, 0xD0,
                        0xAD, None, None, 0xF0, 0x03,
                        0x20, None, None,
                        0xAD, 0x0D, 0xDC,
                        0x68, 0xA8, 0x68, 0xAA, 0x68, 0x40]
            if _match(t, pat_p1):
                w = (img[t + 2] | img[t + 7] << 8) - load
                gate_form = None
                if _match(w, wrap_cmp):
                    gate_form = 'cmp1'
                elif _match(w, wrap_beq):
                    gate_form = 'ackfirst_beq'
                if gate_form:
                    driver = 'poke_stub'
                    dp = {'core_entry': 'core',
                          'delay_seed': img[iv + 9],
                          'outer_seed': img[iv + 17],
                          'speed_poke': speed_poke,
                          'tail_sei': tail_sei,
                          'gate_form': gate_form}

    # class 'kernal_irq' (Second_Thoughts): core FIRST, then SEI, mask,
    # ack, $D011, raster, the KERNAL $0314 vector (port stays $37 — the
    # wrapper exits via JMP $EA31), D019/D01A=1, CLI RTS.
    if driver is None:
        pat_k = ([0x20, None, None, 0x78,
                  0xA9, 0x7F, 0x8D, 0x0D, 0xDC, 0xAD, 0x0D, 0xDC,
                  0xA9, None, 0x8D, 0x11, 0xD0,
                  0xA9, None, 0x8D, 0x12, 0xD0,
                  0xA9, None, 0x8D, 0x14, 0x03,
                  0xA9, None, 0x8D, 0x15, 0x03,
                  0xA9, 0x01, 0x8D, 0x19, 0xD0, 0x8D, 0x1A, 0xD0,
                  0x58, 0x60])
        wrap_k = [0xA9, 0x01, 0x8D, 0x19, 0xD0, 0x20, None, None,
                  0x4C, 0x31, 0xEA]
        if _match(iv, pat_k):
            if img[iv + 1] | img[iv + 2] << 8 != core_base:
                raise DigiOrganizerUnsupported('kernal_irq: JSR not core')
            w = (img[iv + 23] | img[iv + 28] << 8) - load
            if _match(w, wrap_k):
                driver = 'kernal_irq'
                dp = {'raster': img[iv + 18], 'd011': img[iv + 13]}

    # class 'kernal_lock' (Digi-Zak_3): A=1 serves D01A/mask/raster(!),
    # $D011, DEC-ack, KERNAL $0314 vector, JSR core, CLI, JMP-self;
    # wrapper DEC-acks and exits via JMP $EA81.
    if driver is None:
        pat_l = [0x78, 0xA9, 0x01,
                 0x8D, 0x1A, 0xD0, 0x8D, 0x0D, 0xDC, 0x8D, 0x12, 0xD0,
                 0xA9, None, 0x8D, 0x11, 0xD0,
                 0xCE, 0x19, 0xD0,
                 0xA9, None, 0x8D, 0x14, 0x03,
                 0xA9, None, 0x8D, 0x15, 0x03,
                 0x20, None, None, 0x58, 0x4C]
        wrap_l = [0xCE, 0x19, 0xD0, 0x20, None, None, 0x4C, 0x81, 0xEA]
        if _match(iv, pat_l):
            if img[iv + 31] | img[iv + 32] << 8 != core_base:
                raise DigiOrganizerUnsupported('kernal_lock: JSR not core')
            w = (img[iv + 21] | img[iv + 26] << 8) - load
            if _match(w, wrap_l):
                driver = 'kernal_lock'
                dp = {'raster': 1, 'd011': img[iv + 13]}

    # class 'arnie' (Arnie-Rap): SEI, mask, JSR sub {STA $DD0D(A=$7F),
    # acks both CIAs, D019=1, JMP core — core RTSes back to the
    # caller}, then port, vector hi-then-lo, DC0E=0, D01A/D019=1,
    # raster, $D011, CLI RTS; wrap_inc wrapper.
    if driver is None:
        pat_r0 = [0x78, 0xA9, 0x7F, 0x8D, 0x0D, 0xDC, 0x20, None, None]
        pat_sub = [0x8D, 0x0D, 0xDD, 0xAD, 0x0D, 0xDC, 0xAD, 0x0D, 0xDD,
                   0xA9, 0x01, 0x8D, 0x19, 0xD0, 0x4C, None, None]
        pat_r1 = [0xA9, 0x35, 0x85, 0x01,
                  0xA9, None, 0x8D, 0xFF, 0xFF,
                  0xA9, None, 0x8D, 0xFE, 0xFF,
                  0xA9, 0x00, 0x8D, 0x0E, 0xDC,
                  0xA9, 0x01, 0x8D, 0x1A, 0xD0, 0x8D, 0x19, 0xD0,
                  0xA9, None, 0x8D, 0x12, 0xD0,
                  0xA9, None, 0x8D, 0x11, 0xD0,
                  0x58, 0x60]
        if _match(iv, pat_r0):
            sb = (img[iv + 7] | img[iv + 8] << 8) - load
            if _match(sb, pat_sub) and \
                    img[sb + 15] | img[sb + 16] << 8 == core_base and \
                    _match(iv + 9, pat_r1):
                w = (img[iv + 9 + 10] | img[iv + 9 + 5] << 8) - load
                wrap_inc2 = [0x48, 0x8A, 0x48, 0x98, 0x48,
                             0xEE, 0x19, 0xD0, 0x20, None, None,
                             0xAD, 0x0D, 0xDC,
                             0x68, 0xA8, 0x68, 0xAA, 0x68, 0x40]
                if _match(w, wrap_inc2):
                    driver = 'arnie'
                    dp = {'raster': img[iv + 9 + 28],
                          'd011': img[iv + 9 + 33]}

    if driver is None:
        raise DigiOrganizerUnsupported(
            'driver shape matches no probed class (irq_vec / nmi_first '
            '/ xreg / bare_stub / jer_lock / sphere / earbleed / '
            'poke_stub / kernal_irq / kernal_lock / arnie) — '
            'parametrize before accepting')

    # Any class whose recorded entry is 'core' goes through the $9000
    # JMP (and may hit the port pre-init stub); a 'core40' entry
    # bypasses it, making the stub dead.
    enters_via_jmp = dp.get('core_entry', 'core') == 'core'
    pre = _probe_port_preinit() if enters_via_jmp else None
    preinit_form, port_preinit = pre if pre else (None, None)

    m = DigiOrganizerModel(
        sid_path=sid_path, load=load, meta=meta,
        driver=driver, driver_params=dp, port_preinit=port_preinit,
        preinit_form=preinit_form, nmi_vec=nmi_vec,
        core_tail=core_tail,
        raster_line=dp.get('raster'), d011=dp.get('d011'),
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
            e = s + 1
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
