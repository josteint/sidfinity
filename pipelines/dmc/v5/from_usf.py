"""DMC V5 USF -> model (the inverse of extract/to_usf).

Rebuilds a V5Model from a parsed UsfFile so the composer (which is
model-driven and UNCHANGED) can emit the SID. The shared wave / pulse /
filter tables are RE-PACKED from the per-instrument inline programs and
the pointers reassigned -- the engine's packing mechanism. Per the CORE
TENET the rebuilt tables need not match the original's byte layout; only
the resulting $D400-$D418 write stream must (verified by `verify_v5`).

Sectors are content-deduped into a fresh global pool and orderlist
entries remapped to it; sticky dur/instrument are re-emitted on change
(an equivalent stream, not a byte copy).
"""
from __future__ import annotations

from src.usf.types import UsfFile, Pitch
from pipelines.dmc.v5.extract.engine_model import V5Model, V5Instrument

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
_NOTE_IDX = {n: i for i, n in enumerate(NOTE_NAMES)}


def _note_num(p: Pitch) -> int:
    return p.octave * 12 + _NOTE_IDX[p.name]


# --- sector rows -> raw bytes (event order preserved verbatim) ----------
# Leading dur/snd commands are ordered prefix flags ($FD/$FC), emitted
# before the row's main byte (a note pitch, or $FE for a `tie` gate).
def _encode_sector(rows) -> bytes:
    out = bytearray()
    for row in rows:
        for fl in row.fx_flags:
            if fl.startswith('set_dur='):
                out += bytes([0xFD, int(fl.split('=')[1].lstrip('$'), 16) & 0xFF])
            elif fl.startswith('set_instr='):
                out += bytes([0xFC, int(fl.split('=')[1]) & 0xFF])
        if 'tie' in row.fx_flags:
            out.append(0xFE)                         # gate (hold current note)
        else:
            out.append(_note_num(row.pitch) & 0xFF)
    out.append(0xFF)
    return bytes(out)


def _encode_orderlist(ol, remap: dict) -> bytes:
    out = bytearray()
    entry_byte = []
    cur_tr = 0
    for i, e in enumerate(ol.entries):
        entry_byte.append(len(out))
        tr = ol.transpose_at(i)
        if tr != cur_tr:
            if tr >= 0:
                out += bytes([0xFD, tr & 0xFF])      # positive transpose
            else:
                out += bytes([0xFC, (-tr) & 0xFF])   # negative transpose
            cur_tr = tr
        out.append(remap[e] & 0xFF)
    if ol.stop:
        out.append(0xFE)
    elif ol.loop_to is not None:
        tgt = entry_byte[ol.loop_to] if ol.loop_to < len(entry_byte) else 0
        out += bytes([0xFF, tgt & 0xFF])
    else:
        out += bytes([0xFF, 0x00])
    return bytes(out)


def usf_to_model(usf: UsfFile) -> V5Model:
    sub = usf.subtunes[0]
    sid = sub.init.sid if (sub.init and sub.init.sid) else None
    mvol = sid.master_vol if sid and sid.master_vol is not None else 0x0F
    flt = sid.filter if sid else None

    m = V5Model(
        freq_lo=list(usf.freq_table[:96]),
        freq_hi=list(usf.freq_table[96:192]),
        speed=sub.tempo, master_vol=mvol,
        lo_filtmode=flt.res_routing if flt else 0,
        lo_fchi=flt.cutoff_hi if flt else 0,
        lo_fclo=flt.cutoff_lo if flt else 0,
        title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released,
    )

    # ---- re-pack the shared wave table (idle program at index 0, then
    #      each instrument's program) and reassign pointers -------------
    wave = []

    def add_wave(ctrl, freq, loop):
        s = len(wave)
        freq = (list(freq) + [0] * len(ctrl))[:len(ctrl)]
        for c, f in zip(ctrl, freq):
            wave.append((c & 0xFF, f & 0xFF))
        wave.append((0x90, (s + loop) & 0xFF))       # V5 marker: freq = abs target
        return s

    ip = usf.wave_programs.get(0)
    if ip and ip['ctrl']:
        add_wave(ip['ctrl'], ip['freq'], ip.get('loop', 0))

    # ---- re-pack the shared pulse table (null entry 0, then each
    #      restarting instrument's sweep) ------------------------------
    pulse = [(0, 0)]

    def add_pulse(ps):
        s = len(pulse)
        pulse.append(((ps.start >> 8) & 0xFF, ps.start & 0xFF))
        for add, frames in ps.segments:
            a = add & 0xFFFF
            pulse.append(((a >> 8) & 0xFF, a & 0xFF))            # step
            pulse.append(((frames >> 8) & 0xFF, frames & 0xFF))  # count
        if ps.loop is not None:
            pulse.append((0x90, (s + ps.loop) & 0xFF))
        return s

    for inst in usf.instruments:
        wptr = add_wave(inst.waveform, inst.wave_freq, inst.loop)
        pptr = add_pulse(inst.pulse_sweep) if inst.pulse_sweep else 0
        v = inst.vibrato
        m.instruments.append(V5Instrument(
            id=inst.id, ad=inst.adsr[0], sr=inst.adsr[1],
            wave_ptr=wptr, pulse_ptr=pptr, filter_ptr=0,
            vib_delay=v.onset, vib_speed=v.speed, vib_width=v.amplitude))

    m.wave = wave
    m.pulse = pulse
    m.filter = [(0, 0)]                              # Katusha uses no filter

    # ---- sectors: content-dedup the per-voice patterns into one global
    #      pool; remap orderlist entries to it -------------------------
    pool, by_bytes, remap = [], {}, {}
    for voice in sub.voices:
        for pat in voice.patterns:
            enc = _encode_sector(pat.rows)
            idx = by_bytes.get(enc)
            if idx is None:
                idx = len(pool)
                pool.append(enc)
                by_bytes[enc] = idx
            remap[pat.id] = idx
    m.sectors = [None] * len(pool)
    m.sector_raw = list(pool)
    m.orderlist_raw = [_encode_orderlist(v.orderlist, remap)
                       for v in sub.voices]
    return m
