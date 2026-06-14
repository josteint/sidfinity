"""DMC V5 binary -> structured model.

Lifts a V5 packed module (family-3/5 player) into a V5Model: freq tables,
8-byte instruments, the three programmable 2-byte tables (wave/pulse/
filter), per-voice orderlists, and sector event streams. Table bases are
read by dataflow from the operand sites in DMCV5Config; region sizes are
derived from the address deltas (V4-style). See pipelines/dmc/v5/
disassembly.s for the byte maps this decoder follows.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class V5Instrument:
    id: int
    ad: int
    sr: int
    wave_ptr: int      # entry index into the wave table
    pulse_ptr: int     # entry index into the pulse table (0 = no restart)
    filter_ptr: int    # entry index into the filter table (0 = no restart)
    vib_delay: int
    vib_speed: int
    vib_width: int     # & $07


@dataclass
class V5Model:
    freq_lo: list = field(default_factory=list)     # 96
    freq_hi: list = field(default_factory=list)      # 96
    instruments: list = field(default_factory=list)  # list[V5Instrument]
    wave: list = field(default_factory=list)         # list[(ctrl, freq)]
    pulse: list = field(default_factory=list)        # list[(lo, hi)]
    filter: list = field(default_factory=list)       # list[(lo, hi)]
    speed: int = 2
    master_vol: int = 0x0F
    orderlists: list = field(default_factory=list)   # 3 x list[event]
    sectors: list = field(default_factory=list)      # list[list[event]]
    orderlist_raw: list = field(default_factory=list)  # 3 x bytes (song data)
    sector_raw: list = field(default_factory=list)     # list[bytes]
    # file-image leftovers the player init does NOT clear (written to the
    # SID before the filter table overwrites them — V4 $1018-shadow analog)
    lo_filtmode: int = 0    # $1015 -> $D418 (mode nibble)
    lo_fchi: int = 0        # $1016 -> $D416 (cutoff hi)
    lo_fclo: int = 0        # $1017 -> $D415 (cutoff lo)
    title: str = ''
    author: str = ''
    released: str = ''


def _load(path: str):
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', '..', 'tools'))
    from seed_disassembly import parse_psid
    s = parse_psid(path)
    mem = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    return mem, s


def _rd16(mem, a):
    return mem[a] | (mem[a + 1] << 8)


# ----- orderlist (track) decode: $FF loop / $FE end / $FD,$FC transpose --
def _decode_orderlist(mem, ptr: int):
    out = []
    pos = 0
    guard = 0
    while guard < 512:
        guard += 1
        b = mem[ptr + pos]
        if b == 0xFF:
            out.append(('loop', mem[ptr + pos + 1]))
            return out, bytes(mem[ptr:ptr + pos + 2])
        if b == 0xFE:
            out.append(('end',))
            return out, bytes(mem[ptr:ptr + pos + 1])
        if b == 0xFD:
            out.append(('transpose', mem[ptr + pos + 1]))
            pos += 2
            continue
        if b == 0xFC:
            out.append(('transpose', (-mem[ptr + pos + 1]) & 0xFF))
            pos += 2
            continue
        out.append(('sector', b))
        pos += 1
    raise RuntimeError(f'orderlist at ${ptr:04X} never ends')


# ----- sector decode: notes (<$80) + commands ($F1-$FE) + $FF end -------
# (byte counts per pipelines/dmc/v5/disassembly.s sector dispatch)
_CMD = {
    0xF1: ('srr', 2), 0xF2: ('adr', 2), 0xF3: ('vol', 2),
    0xF4: ('gate_tie', 1), 0xF5: ('gate_toggle', 1),
    0xF6: ('fade_out', 2), 0xF7: ('fade_in', 2),
    0xF8: ('frq', 2), 0xF9: ('flt', 2),
    0xFA: ('slide', 3), 0xFB: ('glide', 4),
    0xFC: ('snd', 2), 0xFD: ('dur', 2), 0xFE: ('gate', 1),
}


def _decode_sector(mem, ptr: int):
    out = []
    pos = 0
    guard = 0
    while guard < 4096:
        guard += 1
        b = mem[ptr + pos]
        if b == 0xFF:
            out.append(('end',))
            return out, bytes(mem[ptr:ptr + pos + 1])
        if b < 0x80:
            out.append(('note', b))
            pos += 1
            continue
        if b not in _CMD:
            raise RuntimeError(f'unknown sector cmd ${b:02X} @ ${ptr+pos:04X}')
        name, n = _CMD[b]
        args = tuple(mem[ptr + pos + 1 + k] for k in range(n - 1))
        out.append((name,) + args)
        pos += n
    raise RuntimeError(f'sector at ${ptr:04X} never ends')


def extract(cfg, hvsc_root: str = 'hvsc84') -> V5Model:
    mem, s = _load(os.path.join(hvsc_root, cfg.sid_path))

    a_order = _rd16(mem, cfg.op_orderlist)
    a_secp_lo = _rd16(mem, cfg.op_secp_lo)
    a_secp_hi = _rd16(mem, cfg.op_secp_hi)
    a_instr = _rd16(mem, cfg.op_instr)
    a_flo = _rd16(mem, cfg.op_freq_lo)
    a_fhi = _rd16(mem, cfg.op_freq_hi)
    a_wc = _rd16(mem, cfg.op_wave_ctrl)
    a_wf = _rd16(mem, cfg.op_wave_freq)
    a_pl = _rd16(mem, cfg.op_pulse_lo)
    a_ph = _rd16(mem, cfg.op_pulse_hi)
    a_fl = _rd16(mem, cfg.op_filter_lo)
    a_fh = _rd16(mem, cfg.op_filter_hi)
    end = s['load'] + len(s['payload'])

    # region sizes from address deltas (the packer lays tables contiguously:
    # instr | wave_ctrl | wave_freq | pulse_lo | pulse_hi | filter_lo |
    # filter_hi | <end>)
    n_wave = a_wf - a_wc
    n_pulse = a_ph - a_pl
    n_filter = a_fh - a_fl
    n_instr = (a_wc - a_instr) // 8
    n_sectors = a_secp_hi - a_secp_lo

    m = V5Model(
        freq_lo=[mem[a_flo + i] for i in range(96)],
        freq_hi=[mem[a_fhi + i] for i in range(96)],
        speed=mem[a_order + 6], master_vol=mem[a_order + 7],
        lo_filtmode=mem[cfg.base + 0x15], lo_fchi=mem[cfg.base + 0x16],
        lo_fclo=mem[cfg.base + 0x17],
        title=s.get('name', ''), author=s.get('author', ''),
        released=s.get('released', ''),
    )
    for i in range(n_instr):
        b = [mem[a_instr + i * 8 + k] for k in range(8)]
        m.instruments.append(V5Instrument(
            id=i, ad=b[0], sr=b[1], wave_ptr=b[2], pulse_ptr=b[3],
            filter_ptr=b[4], vib_delay=b[5], vib_speed=b[6],
            vib_width=b[7] & 0x07))
    m.wave = [(mem[a_wc + i], mem[a_wf + i]) for i in range(n_wave)]
    m.pulse = [(mem[a_pl + i], mem[a_ph + i]) for i in range(n_pulse)]
    m.filter = [(mem[a_fl + i], mem[a_fh + i]) for i in range(n_filter)]

    for v in range(3):
        tp = _rd16(mem, a_order + v * 2)
        ev, raw = _decode_orderlist(mem, tp)
        m.orderlists.append(ev)
        m.orderlist_raw.append(raw)
    for i in range(n_sectors):
        sp = mem[a_secp_lo + i] | (mem[a_secp_hi + i] << 8)
        ev, raw = _decode_sector(mem, sp)
        m.sectors.append(ev)
        m.sector_raw.append(raw)
    return m
