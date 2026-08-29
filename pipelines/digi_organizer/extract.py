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
        # driver JSRs core+$40 directly past a stale stub).
        ent = img[cb + 1] | img[cb + 2] << 8
        if ent == core_base + 0x40:
            return None
        stub = [0x78, 0xA9, None, 0x85, 0x01,
                0x4C, (core_base + 0x40) & 0xFF, (core_base + 0x40) >> 8]
        so = ent - load
        if not (0 <= so <= len(img) - len(stub)) or any(
                q is not None and img[so + j] != q
                for j, q in enumerate(stub)):
            raise DigiOrganizerUnsupported(
                f'core entry routes to ${ent:04X} — not core+$40 and '
                'not the port pre-init stub')
        return img[so + 2]

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
                if _match(w, wrap_ack):
                    driver = 'bare_stub'
                    dp = {'nop': nop}

    if driver is None:
        raise DigiOrganizerUnsupported(
            'driver shape matches no probed class (irq_vec / nmi_first '
            '/ xreg / bare_stub) — parametrize before accepting')

    # Any class whose recorded entry is 'core' goes through the $9000
    # JMP (and may hit the port pre-init stub); a 'core40' entry
    # bypasses it, making the stub dead.
    enters_via_jmp = dp.get('core_entry', 'core') == 'core'
    port_preinit = _probe_port_preinit() if enters_via_jmp else None

    m = DigiOrganizerModel(
        sid_path=sid_path, load=load, meta=meta,
        driver=driver, driver_params=dp, port_preinit=port_preinit,
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
