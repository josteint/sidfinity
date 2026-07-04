"""Henrys_House (Chris Murray, 1984) — SID → USF extract.

A single-voice variant of the Companion family. Tempo hardcoded to 8.
Note bytes: $00-$7F NORMAL_NOTE, $80 REST, $81 SKIP, $FF LOOP_RESTART.
Freq table identical to Clever Music.

The build path is the universal `pipelines.build_from_usf.build_from_usf`,
which routes single-voice USFs with a 256-byte freq_table block
through `_emit_sid_simple_tracker`. This file only does the SID→USF
direction.
"""

from __future__ import annotations

import os
import struct

from src.usf import (
    UsfFile, PsidMeta, Params, InitState, InitVoice, Instrument,
    PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig, MusicSubtune,
    VoiceBlock, Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
    write_file, validate,
)
from pipelines.companion.clever_music.engine_constants import (
    CLEVER_FREQ_HI, CLEVER_FREQ_LO, note_byte_to_pitch,
)


# ---------------------------------------------------------------------------
# Extract (SID → USF)
# ---------------------------------------------------------------------------

def _run_init(sid_path: str):
    """Run init via py65 to capture per-tune state + init SID writes."""
    import sys as _sys
    _sys.path.insert(0, 'tools/py65_lib')
    from py65.devices.mpu6502 import MPU

    class _Mem(bytearray):
        sid_writes: list  # type: ignore

        def __new__(cls, size):
            obj = super().__new__(cls, size)
            obj.sid_writes = []
            return obj

        def __setitem__(self, idx, val):
            if isinstance(idx, int) and 0xD400 <= idx <= 0xD418:
                self.sid_writes.append((idx - 0xD400, val))
            super().__setitem__(idx, val)

    raw = open(sid_path, 'rb').read()
    body = raw[124:]
    load_in = struct.unpack('>H', raw[8:10])[0]
    if load_in == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    else:
        load = load_in
    init_addr = struct.unpack('>H', raw[10:12])[0]
    mpu = MPU()
    mpu.memory = _Mem(0x10000)
    mpu.memory[load:load + len(body)] = body
    mpu.memory.sid_writes.clear()
    mpu.a = 0; mpu.x = 0; mpu.y = 0; mpu.p = 0x20; mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE; mpu.memory[0x01FE] = 0xFE
    mpu.memory.sid_writes.clear()
    mpu.pc = init_addr
    for _ in range(50000):
        if not load <= mpu.pc < load + len(body):
            break
        mpu.step()
    return bytearray(mpu.memory), list(mpu.memory.sid_writes), raw, load


def _extract_pattern_rows(body: bytes) -> list[NoteRow]:
    """Decode the pattern's byte body into a list of NoteRows.

    Engine bytes: $00-$7F = note, $80 = rest (writes gate-off),
    $81 = skip (no write — continues whatever the voice was doing).
    A run of one head byte ($00-$7F or $80) followed by $81s is
    musically a single event of the head's kind whose duration is
    the run length. So we collapse runs into rows whose `duration`
    is the tick count.
    """
    rows: list[NoteRow] = []
    for b in body:
        if b == 0x81:
            if rows:
                rows[-1].duration += 1
            else:
                # Pattern beginning with $81 — engine does nothing this
                # tick. Encode as a rest tick we extend later.
                rows.append(NoteRow(pitch=Pitch.rest(), duration=1))
        elif b == 0x80:
            rows.append(NoteRow(pitch=Pitch.rest(), duration=1))
        elif b & 0x80:
            # Pattern body should never hit this (only $80/$81/note);
            # $FF is the terminator handled separately. Keep a raw
            # escape for defence in depth.
            rows.append(NoteRow(pitch=Pitch.rest(), duration=1,
                                fx_flags=(f'fx:raw_{b:02x}',)))
        else:
            name, octave = note_byte_to_pitch(b)
            rows.append(NoteRow(pitch=Pitch(name=name, octave=octave),
                                duration=1))
    return rows


# Known data offsets in Henrys_House's binary (relative to load $ACC0).
# Discovered by hand-disasm; documented in project memory.
HH_TIMBRE_ADDR = 0xAEA1     # 5 bytes
HH_ORDERLIST = 0xADC0       # ends at $FF
HH_FREQ_HI = 0xACC0
HH_FREQ_LO = 0xAD40


def build_usf(sid_path: str) -> UsfFile:
    mem, init_sid, raw, load = _run_init(sid_path)

    # Extract orderlist (up to and including $FF)
    ol_start = HH_ORDERLIST
    ol_end = ol_start + 256
    ol_slice = bytes(mem[ol_start:ol_end])
    ff = ol_slice.find(0xFF)
    if ff < 0:
        raise ValueError('no $FF terminator in orderlist')
    orderlist = ol_slice[:ff + 1]

    # Extract timbre
    tb = bytes(mem[HH_TIMBRE_ADDR:HH_TIMBRE_ADDR + 5])
    pw = (tb[1] << 8) | tb[0]
    instrument = Instrument(
        id=1,
        waveform=[tb[2]],
        loop=0,
        pwm=PwmConfig(mode='none', speed=0, init=pw, min_hi=0, max_hi=0),
        adsr=(tb[3], tb[4]),
        arp=ArpConfig(offsets=[0], period=1),
        vibrato=VibratoConfig(scale=0),
        envelope=EnvelopeConfig(),
    )

    rows = _extract_pattern_rows(orderlist[:-1])         # exclude $FF terminator
    total_ticks = sum(r.duration for r in rows)
    voice = VoiceBlock(
        id=1,
        orderlist=Orderlist(entries=[1], loop_to=0),
        patterns=[Pattern(id=1, length=total_ticks, rows=rows)],
    )
    # Grammar requires 3 voices per subtune; pad with empty placeholders
    # that the codegen ignores (henrys_house is single-voice).
    placeholder = lambda i: VoiceBlock(
        id=i,
        orderlist=Orderlist(entries=[], stop=True),
        patterns=[],
    )

    music = MusicSubtune(
        id=0,
        tempo=8,                     # hardcoded in the engine
        voices=[voice, placeholder(2), placeholder(3)],
        params=Params(fields={}),
    )

    # PSID meta
    title = raw[0x16:0x36].rstrip(b'\x00').decode('latin-1')
    author = raw[0x36:0x56].rstrip(b'\x00').decode('latin-1')
    released = raw[0x56:0x76].rstrip(b'\x00').decode('latin-1')
    flags = int.from_bytes(raw[0x76:0x78], 'big')
    clock = {0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[(flags >> 2) & 0x03]
    sid_model = {0: 6581, 1: 6581, 2: 8580, 3: 6581}[(flags >> 4) & 0x03]
    psid = PsidMeta(
        title=title, author=author, released=released,
        clock=clock, sid=sid_model,
        start_song=int.from_bytes(raw[0x10:0x12], 'big'),
        speed=int.from_bytes(raw[0x12:0x16], 'big'),
    )

    # Inline the freq table — engine-neutral data the USF carries, so
    # the codegen doesn't need to know about Clever Music's tables.
    freq_table = list(CLEVER_FREQ_HI) + list(CLEVER_FREQ_LO)

    return UsfFile(
        psid=psid,
        params=Params(),
        init=InitState(voices=[InitVoice(id=1, instr=InstrumentRef(id=1))]),
        instruments=[instrument],
        subtunes=[music],
        freq_table=freq_table,
    )


def write_usf(sid_path: str, out_path: str | None = None) -> str:
    if out_path is None:
        base, _ = os.path.splitext(sid_path)
        out_path = base + '.usf'
    usf = build_usf(sid_path)
    validate(usf)
    write_file(usf, out_path)
    return out_path
