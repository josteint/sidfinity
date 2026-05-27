"""Per-sub engine model for 5 Title Tunes.

Forked from Chimera's engine_model with one fix:

  When `pw_speed=0` AND fx-flags bit 3 (linear-PW mode) is set, the
  engine writes pw_lo=init_pw every frame (the linear-PW path runs
  unconditionally). Chimera's extract maps this case to `pw_mode='none'`
  which makes the codegen SKIP the pw_lo write. For 5 Title Tunes
  sub_0 inst 7, this caused the V2.pw_lo=00 writes to be missing
  in the rebuild. Fix: when fx bit 3 is set, keep `pw_mode='linear'`
  even if `pw_speed=0`.

Everything else mirrors `pipelines.hubbard.chimera.extract.engine_model`.
"""
from __future__ import annotations

import logging
import os
import struct
import sys

from pipelines.hubbard.chimera.extract.types import (
    Envelope, ExtractedSong, Instrument, Note, PWMConfig, Score,
    Voice, Waveform,
)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))))
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

logger = logging.getLogger(__name__)


def extract(
    subtune: int = 0,
    sid_path: str | None = None,
    ft_base: int | None = None,
    default_pw_min: int = 0x08,
    default_pw_max: int = 0x0E,
    verbose: bool = False,
) -> ExtractedSong:
    """Like Chimera's extract but with the pw_mode='linear' fix above."""
    from effect_detect import FREQ_PAL
    from py65.devices.mpu6502 import MPU
    from pipelines.hubbard.chimera.extract.decompile import decompile

    if sid_path is None:
        raise ValueError("sid_path required for 5 Title Tunes sub extract")
    if ft_base is None:
        raise ValueError("ft_base required (each sub has a different freq table)")

    decomp = decompile(sid_path)

    # T: Frequency Table (PAL + runtime extension from binary state region)
    T: list[int] = list(FREQ_PAL)
    with open(sid_path, 'rb') as f:
        d = f.read()
    hl = struct.unpack('>H', d[6:8])[0]
    la = struct.unpack('>H', d[8:10])[0]
    code = d[hl:]
    if la == 0:
        la = struct.unpack('<H', code[:2])[0]
        code = code[2:]
    mem = bytearray(65536)
    mem[la:la + len(code)] = code
    m = MPU()
    m.memory = bytearray(mem)
    m.memory[0xFFF0] = 0x00
    m.stPush(0xFF); m.stPush(0xEF)
    m.pc = struct.unpack('>H', d[10:12])[0]
    m.a = 0
    for _ in range(100000):
        if m.memory[m.pc] == 0:
            break
        m.step()
    m.stPush(0xFF); m.stPush(0xEF)
    m.pc = struct.unpack('>H', d[12:14])[0]
    for _ in range(50000):
        if m.memory[m.pc] == 0:
            break
        m.step()
    while len(T) < 120:
        i = len(T)
        addr = ft_base + i * 2
        T.append((m.memory[addr + 1] << 8) | m.memory[addr])

    # I: Instruments
    instruments: list[Instrument] = []
    if decomp.speed_table is not None and subtune < len(decomp.speed_table):
        speed = decomp.speed_table[subtune]
    elif decomp.speed is not None:
        speed = decomp.speed
    else:
        speed = 2
    hr_frames = 3

    for rh in decomp.instruments:
        ctrl = rh.ctrl
        if rh.has_drum:
            w_steps = [ctrl | 0x01, 0x80, 0x80, 0x80, ctrl & 0xFE]
            w_loop = 4
        else:
            w_steps = [ctrl | 0x01]
            w_loop = 0
        arp_offset = 12 if rh.has_arpeggio else 0
        flags = rh.fx_flags if rh.fx_flags is not None else 0
        vibrato_scale = rh.vibrato_depth if hasattr(rh, 'vibrato_depth') else 0
        pw_speed = rh.pwm_speed
        pw_simple = (flags >> 3) & 1  # bit 3 = linear PWM mode

        # PWM mode rules — DIFFERENT from Chimera:
        #   - linear bit set → always 'linear' (engine writes pw_lo every
        #     frame even when speed=0; 5 Title Tunes sub_0 inst 7 hits this)
        #   - linear bit clear + speed=0 → 'none'
        #   - linear bit clear + speed>0 → 'bidirectional'
        if pw_simple:
            pw_mode = 'linear'
            pw_min = 0xFF
            pw_max = 0xFF
        elif pw_speed == 0:
            pw_mode = 'none'
            pw_min = 0xFF
            pw_max = 0xFF
        else:
            pw_mode = 'bidirectional'
            pw_min = default_pw_min
            pw_max = default_pw_max

        has_bit0 = bool(flags & 1)
        has_skydive = bool(flags & 2)
        instruments.append(Instrument(
            id=rh.index,
            waveform=Waveform(steps=w_steps, loop=w_loop),
            pwm=PWMConfig(
                speed=pw_speed, mode=pw_mode,
                min_hi=pw_min, max_hi=pw_max,
                init_pw=rh.pulse_width,
            ),
            envelope=Envelope(
                ad=rh.ad, sr=rh.sr,
                gate_off_delta=hr_frames, adsr_zero_delta=hr_frames,
            ),
            arp_offset=arp_offset,
            vibrato_scale=vibrato_scale,
            has_bit0=has_bit0,
            has_skydive=has_skydive,
        ))

    # S: Score
    if subtune >= len(decomp.songs):
        raise ValueError(f"subtune {subtune} out of range")
    song = decomp.songs[subtune]
    tick_length = speed + 1
    pat_dict = {p.index: p for p in decomp.patterns}
    score = Score(tempo=tick_length, voices=[])
    for v_track in song.tracks:
        voice = Voice(orderlist=[], patterns={}, loop=-1)
        for entry in v_track:
            if entry[0] == 'pattern':
                pat_idx = entry[1]
                voice.orderlist.append(pat_idx)
                if pat_idx not in voice.patterns:
                    pat = pat_dict[pat_idx]
                    notes: list[Note] = []
                    cur_inst = 0
                    for note in pat.notes:
                        if note.instrument is not None:
                            cur_inst = note.instrument
                        dur = note.duration if note.duration is not None else 0
                        is_tie = note.tie
                        if note.pitch is None or is_tie:
                            pitch = notes[-1].pitch if notes else 0
                        else:
                            pitch = note.pitch
                        has_inst_byte = (note.instrument is not None)
                        no_release = (hasattr(note, 'no_release') and
                                      bool(note.no_release))
                        stored_inst = (cur_inst
                                       | (0 if has_inst_byte else 0x80)
                                       | (0x40 if is_tie else 0))
                        drum_trig_byte = 0
                        if hasattr(note, 'portamento') and note.portamento is not None:
                            porta_speed, direction = note.portamento
                            drum_trig_byte = ((porta_speed & 0x3F) << 1) | (direction & 1)
                        if no_release:
                            drum_trig_byte |= 0x80
                        notes.append(Note(
                            pitch=pitch,
                            duration=dur + 1,
                            instrument=stored_inst,
                            tie=is_tie,
                            drum_trig=drum_trig_byte,
                        ))
                    voice.patterns[pat_idx] = notes
            elif entry[0] == 'loop':
                voice.loop = entry[1]
            elif entry[0] == 'stop':
                voice.stop = True
        score.voices.append(voice)
    return ExtractedSong(freq_table=T, instruments=instruments, score=score)
