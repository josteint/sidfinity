"""Companion extract — reads the SID binary and produces per-subtune
data structures the codegen consumes."""

from __future__ import annotations

import os
import struct
from dataclasses import dataclass

from pipelines.companion.config import CFG


@dataclass
class VoiceState:
    """Per-voice locked timbre + initial state from the 32-byte template."""
    pos: int                     # initial orderlist position (always 0 in practice)
    gate_off_flag: int           # initial gate-off flag (always 0)
    pw_lo: int
    pw_hi: int
    ctrl_noGate: int             # ctrl byte with gate bit clear
    ad: int
    sr: int


@dataclass
class SubtuneData:
    """All per-subtune data extracted from the SID binary."""
    index: int
    v1_state: VoiceState
    v2_state: VoiceState
    v3_state: VoiceState
    gate_off_tick: int           # $C6D5 — sub-tick when voices gate off
    note_load_tick: int          # $C6D6 — sub-tick when next note loads
    init_tempo_counter: int      # $C6D7 — initial tempo counter value
    init_pwm_ctr: int            # $C6DE — initial PWM counter ($FF or $00)
    init_pwm_ctr_2: int          # $C6DF — second byte (also $FF or $00)
    vol_filter: int              # value written to $D418
    filter_cutoff_hi: int        # value written to $D416
    orderlist_v1: bytes
    orderlist_v2: bytes
    orderlist_v3: bytes


def _load_binary() -> tuple[bytes, int]:
    """Load the SID payload + load address (no PSID header)."""
    with open(CFG.sid_path, 'rb') as f:
        d = f.read()
    hl = struct.unpack('>H', d[6:8])[0]
    load = struct.unpack('>H', d[8:10])[0]
    code = d[hl:]
    if load == 0:
        load = struct.unpack('<H', code[:2])[0]
        code = code[2:]
    return code, load


def _parse_voice_state(template: bytes, offset: int) -> VoiceState:
    return VoiceState(
        pos=template[offset + 0],
        gate_off_flag=template[offset + 1],
        pw_lo=template[offset + 2],
        pw_hi=template[offset + 3],
        ctrl_noGate=template[offset + 4],
        ad=template[offset + 5],
        sr=template[offset + 6],
    )


def _extract_orderlist(code: bytes, load: int, start: int,
                       extra_bytes: int = 32) -> bytes:
    """Read orderlist bytes starting at `start`, including the $8D
    terminator and `extra_bytes` past it.

    The original engine doesn't stop reading at $8D — V3's $8D
    kills the volume but the engine keeps advancing all voices'
    orderlist positions, reading "garbage" bytes that happen to be
    adjacent data in the binary. For byte-exact verification within
    the HVSC song-length window we need to replicate those garbage
    bytes in our rebuild's orderlists. Extra 32 bytes covers the
    1.1x-songlength tail for every subtune (longest tail is sub 0
    with ~19 frames * 1 byte per step past $8D).
    """
    out = bytearray()
    found_8d = False
    for i in range(512):
        if start - load + i >= len(code):
            break
        b = code[start - load + i]
        out.append(b)
        if found_8d:
            if len(out) >= terminator_len + extra_bytes:
                return bytes(out)
        elif b == 0x8D:
            found_8d = True
            terminator_len = len(out)
    if not found_8d:
        raise ValueError(
            f'orderlist at ${start:04X}: no $8D terminator in 512 bytes')
    return bytes(out)


def extract_subtune(sub_idx: int) -> SubtuneData:
    """Extract all data for one subtune from the SID binary."""
    code, load = _load_binary()

    def at(a: int) -> int:
        return code[a - load]

    template_addr = CFG.template_addrs[sub_idx]
    tmpl = bytes(at(template_addr + i) for i in range(32))

    v1 = _parse_voice_state(tmpl, 0)
    v2 = _parse_voice_state(tmpl, 7)
    v3 = _parse_voice_state(tmpl, 14)
    gate_off_tick = tmpl[21]
    note_load_tick = tmpl[22]
    init_tempo_counter = tmpl[23]
    v1_ord = (tmpl[25] << 8) | tmpl[24]
    v2_ord = (tmpl[27] << 8) | tmpl[26]
    v3_ord = (tmpl[29] << 8) | tmpl[28]

    return SubtuneData(
        index=sub_idx,
        v1_state=v1, v2_state=v2, v3_state=v3,
        gate_off_tick=gate_off_tick,
        note_load_tick=note_load_tick,
        init_tempo_counter=init_tempo_counter,
        init_pwm_ctr=tmpl[30],
        init_pwm_ctr_2=tmpl[31],
        vol_filter=CFG.vol_filter[sub_idx],
        filter_cutoff_hi=CFG.filter_cutoff_hi[sub_idx],
        orderlist_v1=_extract_orderlist(code, load, v1_ord),
        orderlist_v2=_extract_orderlist(code, load, v2_ord),
        orderlist_v3=_extract_orderlist(code, load, v3_ord),
    )


def extract_freq_table() -> tuple[bytes, bytes]:
    """Extract the 128-byte freq-hi and freq-lo tables (Bowden PAL,
    A4 = 423.8 Hz)."""
    code, load = _load_binary()
    hi = bytes(code[CFG.freq_hi_base - load + i] for i in range(128))
    lo = bytes(code[CFG.freq_lo_base - load + i] for i in range(128))
    return hi, lo


def extract_all() -> tuple[list[SubtuneData], bytes, bytes]:
    """Extract all 5 subtunes plus the shared freq table."""
    freq_hi, freq_lo = extract_freq_table()
    subtunes = [extract_subtune(i) for i in range(5)]
    return subtunes, freq_hi, freq_lo


if __name__ == '__main__':
    subs, fh, fl = extract_all()
    for s in subs:
        print(f'sub {s.index}: tempo gate-off={s.gate_off_tick} '
              f'load={s.note_load_tick} init_ctr={s.init_tempo_counter} '
              f'V1.ctrl=${s.v1_state.ctrl_noGate:02X} '
              f'V1.ord_len={len(s.orderlist_v1)}')
