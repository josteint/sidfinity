"""Companion extract — reads the SID binary and produces per-subtune
data structures the codegen consumes."""

from __future__ import annotations

import os
import struct
from dataclasses import dataclass

from pipelines.companion.up_up_and_away.config import CFG


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
class VoicePadding:
    """Per-voice engine-layout padding: the original binary allocates a
    fixed-size slot for each voice's orderlist; if the orderlist (plus
    its $8D terminator) is shorter than the slot, the remaining bytes
    are filler.  The engine reads past $8D and consumes these bytes
    silently (after V3's $8D fires vol=0). For byte-exact rebuild we
    must reproduce them — parametrically, as (count, byte_value)."""
    count: int
    byte: int


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
    v1_padding: VoicePadding
    v2_padding: VoicePadding
    v3_padding: VoicePadding
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


def _extract_orderlist(code: bytes, load: int, start: int) -> bytes:
    """Read orderlist bytes starting at `start`, up to and including
    the first $8D terminator.

    The Companion engine continues reading past $8D (it doesn't check
    song_alive), but those post-terminator bytes are NOT part of this
    voice's data — they're whatever happens to be adjacent in memory.
    The codegen reproduces that adjacency by laying each subtune out
    as `[V1 ord][V2 ord][V3 ord][template]`, so engine reads past any
    voice's $8D naturally fall into the next chunk.
    """
    out = bytearray()
    for i in range(512):
        if start - load + i >= len(code):
            break
        b = code[start - load + i]
        out.append(b)
        if b == 0x8D:
            return bytes(out)
    raise ValueError(
        f'orderlist at ${start:04X}: no $8D terminator in 512 bytes')


def _extract_padding(code: bytes, load: int, ord_end_addr: int,
                     next_addr: int) -> VoicePadding:
    """Measure the engine-layout padding between this voice's
    orderlist terminator and the next adjacent chunk. The padding
    is a uniform byte (verified by sampling); we record (count, byte).
    """
    n = next_addr - ord_end_addr
    if n <= 0:
        return VoicePadding(count=0, byte=0)
    bs = bytes(code[ord_end_addr - load + i] for i in range(n))
    if len(set(bs)) > 1:
        raise ValueError(
            f'padding at ${ord_end_addr:04X}..${next_addr:04X} is not uniform: '
            f'{bs.hex()}')
    return VoicePadding(count=n, byte=bs[0])


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

    ord_v1 = _extract_orderlist(code, load, v1_ord)
    ord_v2 = _extract_orderlist(code, load, v2_ord)
    ord_v3 = _extract_orderlist(code, load, v3_ord)

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
        v1_padding=_extract_padding(code, load, v1_ord + len(ord_v1), v2_ord),
        v2_padding=_extract_padding(code, load, v2_ord + len(ord_v2), v3_ord),
        v3_padding=_extract_padding(code, load, v3_ord + len(ord_v3), template_addr),
        orderlist_v1=ord_v1,
        orderlist_v2=ord_v2,
        orderlist_v3=ord_v3,
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
