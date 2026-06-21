"""DMC V6 binary -> structured model.

Lifts a V6 module (the internal/unreleased DMC by Brian + The Syndrom; a
SEPARATE player from V4/V5, ~0.01 fingerprint Jaccard, but the SAME musical
shape v5 models). See pipelines/dmc/v6/RE_NOTES.md + dmc_v6_note/disassembly.s
for the byte maps this decoder follows.

The player code carries the data-table base addresses as fixed LITERAL operands,
so for a relocated tune everything shifts uniformly by (load - $1000); we address
tables as `load + offset` where the offsets are the $1000-relative bases from the
RE. (A future factory will dataflow-resolve the operands per tune to also cover
the wrapper-init members; for now this covers the $1000 + simple-relocation set.)
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

# --- $1000-relative table bases (from the RE; see disassembly header) ---
OFF_PW_LO   = 0x3FD     # PW oscillator LUT lo (64 entries, &$1F + $20 sign)
OFF_PW_HI   = 0x43D     # PW oscillator LUT hi (256 entries, full accumulator)
OFF_FREQ_LO = 0x53D     # 96-entry freq table lo
OFF_FREQ_HI = 0x59D     # 96-entry freq table hi
OFF_AD      = 0x5FD     # per-inst tables, 22-entry stride from here
OFF_SR      = 0x613
OFF_PWINIT  = 0x629
OFF_PWSTEP  = 0x63F
OFF_WAVEPTR = 0x655
OFF_PITCHDLY= 0x66B
OFF_FILTCUT = 0x681
OFF_FILTCNT = 0x697
OFF_FILTSTEP= 0x6AD
OFF_WAVE_CTRL = 0x6C3   # wave program ctrl bytes ($FF = loop)
OFF_WAVE_OFF  = 0x757   # wave program note-offsets (loop-back index at $FF slot)
OFF_OL_V1   = 0x7EB     # per-voice orderlists ($FF = wrap)
OFF_OL_V2   = 0x804
OFF_OL_V3   = 0x835
OFF_PAT_LO  = 0x84E     # 16 pattern pointers (lo)
OFF_PAT_HI  = 0x85E     # 16 pattern pointers (hi)

N_INST_SLOTS = 22       # per-inst tables are 22 entries
N_PATTERNS   = 16
FREQ_ENTRIES = 96


@dataclass
class V6Instrument:
    id: int
    ad: int
    sr: int
    pw_init: int        # PW oscillator phase init ($1629)
    pw_step: int        # PW oscillator phase step per frame ($163F)
    wave_ptr: int       # start index into the wave program ($1655)
    pitch_delay: int    # frames before the octave-up pitch slide ($166B; 0 = none)
    filt_cut: int       # filter cutoff init ($1681; V2-owned)
    filt_count: int     # filter sweep frame count ($1697)
    filt_step: int      # filter cutoff step per frame ($16AD)


@dataclass
class V6WaveStep:
    ctrl: int           # waveform control byte ($D404 etc.)
    offset: int         # semitone offset added to the note (arpeggio)


@dataclass
class V6WaveProgram:
    steps: list = field(default_factory=list)   # list[V6WaveStep] up to the loop
    loop: int = 0       # step index the $FF loop jumps back to


# pattern event vocabulary (decoded from the byte stream)
@dataclass
class V6PatNote:
    note: int
@dataclass
class V6PatDuration:
    dur: int
@dataclass
class V6PatInstrument:
    instr: int


@dataclass
class V6Model:
    load: int = 0x1000
    freq_lo: list = field(default_factory=list)      # 96
    freq_hi: list = field(default_factory=list)      # 96
    pw_lut_lo: list = field(default_factory=list)     # 64 (shared PW shape)
    pw_lut_hi: list = field(default_factory=list)     # 256
    instruments: list = field(default_factory=list)   # list[V6Instrument]
    wave_programs: dict = field(default_factory=dict)  # inst-wave_ptr -> V6WaveProgram
    wave_raw: list = field(default_factory=list)       # raw [(ctrl,off)] table
    orderlists: list = field(default_factory=list)     # 3 x list[pattern-id]
    patterns: dict = field(default_factory=dict)       # pat-id -> list[event]
    pattern_raw: dict = field(default_factory=dict)    # pat-id -> bytes
    title: str = ''
    author: str = ''
    released: str = ''


def _psid_body(path: str) -> tuple[int, bytes, dict]:
    d = open(path, 'rb').read()
    dataoff = struct.unpack('>H', d[6:8])[0]
    load = struct.unpack('>H', d[8:10])[0]
    body = d[dataoff:]
    if load == 0:                       # real load is the first 2 body bytes
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    meta = {
        'title':  d[0x16:0x36].split(b'\x00')[0].decode('latin1'),
        'author': d[0x36:0x56].split(b'\x00')[0].decode('latin1'),
        'released': d[0x56:0x76].split(b'\x00')[0].decode('latin1'),
    }
    return load, body, meta


def _decode_wave_program(wave_raw: list, start: int) -> V6WaveProgram:
    """Walk the wave program from `start` until the $FF ctrl (loop marker).
    The offset byte at the $FF slot is the step index to loop back to."""
    steps = []
    i = start
    seen = set()
    while 0 <= i < len(wave_raw) and i not in seen:
        seen.add(i)
        ctrl, off = wave_raw[i]
        if ctrl == 0xFF:
            return V6WaveProgram(steps=steps, loop=off - start if off >= start
                                 else 0)
        steps.append(V6WaveStep(ctrl=ctrl, offset=off))
        i += 1
    return V6WaveProgram(steps=steps, loop=0)


def _decode_pattern(body: bytes, off: int) -> tuple[list, bytes]:
    """Decode one pattern byte stream until (and including) the $FF that
    terminates it. Vocabulary: bit7-clear=note; $FD x=duration; other
    high-byte + x = instrument; $FF (after a note) = end."""
    events = []
    i = off
    n = len(body)
    raw_start = off
    while i < n:
        b = body[i]
        if b < 0x80:                    # note
            events.append(V6PatNote(note=b))
            i += 1
            if i < n and body[i] == 0xFF:   # pattern-end peek
                i += 1
                break
            continue
        if b == 0xFF:                   # bare end (defensive)
            i += 1
            break
        if b == 0xFD:                   # duration: $FD <dur>
            events.append(V6PatDuration(dur=body[i + 1]))
            i += 2
            continue
        # any other high byte: instrument-set ( <marker> <instr> )
        events.append(V6PatInstrument(instr=body[i + 1]))
        i += 2
    return events, body[raw_start:i]


def _orderlist(body: bytes, base: int, load: int) -> list:
    """Read a per-voice orderlist (pattern ids) up to the $FF wrap marker."""
    out = []
    i = base - load
    while i < len(body):
        v = body[i]
        if v == 0xFF:
            break
        out.append(v)
        i += 1
    return out


def extract(path: str) -> V6Model:
    load, body, meta = _psid_body(path)

    def b(addr):       # absolute addr -> body byte
        return body[addr - load]

    def tbl(off, n):   # n bytes at load+off
        s = off
        return list(body[s:s + n])

    m = V6Model(load=load, **meta)
    m.freq_lo = tbl(OFF_FREQ_LO, FREQ_ENTRIES)
    m.freq_hi = tbl(OFF_FREQ_HI, FREQ_ENTRIES)
    m.pw_lut_lo = tbl(OFF_PW_LO, 64)
    m.pw_lut_hi = tbl(OFF_PW_HI, 256)

    ad = tbl(OFF_AD, N_INST_SLOTS); sr = tbl(OFF_SR, N_INST_SLOTS)
    pwi = tbl(OFF_PWINIT, N_INST_SLOTS); pws = tbl(OFF_PWSTEP, N_INST_SLOTS)
    wp = tbl(OFF_WAVEPTR, N_INST_SLOTS); pd = tbl(OFF_PITCHDLY, N_INST_SLOTS)
    fcut = tbl(OFF_FILTCUT, N_INST_SLOTS); fcnt = tbl(OFF_FILTCNT, N_INST_SLOTS)
    fstp = tbl(OFF_FILTSTEP, N_INST_SLOTS)
    m.instruments = [
        V6Instrument(id=i, ad=ad[i], sr=sr[i], pw_init=pwi[i], pw_step=pws[i],
                     wave_ptr=wp[i], pitch_delay=pd[i], filt_cut=fcut[i],
                     filt_count=fcnt[i], filt_step=fstp[i])
        for i in range(N_INST_SLOTS)]

    # wave program table — read until the data tails into the orderlists.
    n_wave = OFF_OL_V1 - OFF_WAVE_CTRL    # ctrl table extent (a safe upper bound)
    wctrl = tbl(OFF_WAVE_CTRL, n_wave); woff = tbl(OFF_WAVE_OFF, n_wave)
    m.wave_raw = list(zip(wctrl, woff))
    for ins in m.instruments:
        if ins.wave_ptr not in m.wave_programs:
            m.wave_programs[ins.wave_ptr] = _decode_wave_program(
                m.wave_raw, ins.wave_ptr)

    # orderlists + patterns
    m.orderlists = [_orderlist(body, load + o, load)
                    for o in (OFF_OL_V1, OFF_OL_V2, OFF_OL_V3)]
    plo = tbl(OFF_PAT_LO, N_PATTERNS); phi = tbl(OFF_PAT_HI, N_PATTERNS)
    used = {pid for ol in m.orderlists for pid in ol}
    for pid in sorted(used):
        if pid >= N_PATTERNS:
            continue
        addr = plo[pid] | (phi[pid] << 8)
        if not (load <= addr < load + len(body)):
            continue
        events, raw = _decode_pattern(body, addr - load)
        m.patterns[pid] = events
        m.pattern_raw[pid] = raw
    return m
