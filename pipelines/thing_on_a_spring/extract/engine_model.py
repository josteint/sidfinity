"""Engine model: read a Hubbard SID binary, return an ExtractedSong.

Identical to the Commando engine_model except for the default SID path
and that ``has_skydive`` (fx_flags bit 1) is propagated through to each
extracted instrument.
"""

from __future__ import annotations

import logging
import os
import struct
import sys

from .types import (
    Envelope,
    ExtractedSong,
    Instrument,
    Note,
    PWMConfig,
    Score,
    Voice,
    Waveform,
)

ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

SID_PATH = os.path.join(
    ROOT, 'hvsc84', 'MUSICIANS', 'H',
    'Hubbard_Rob', 'Thing_on_a_Spring.sid',
)

logger = logging.getLogger(__name__)


# ===================================================================
# DECOMPILER: Extract ExtractedSong from a Hubbard binary
# ===================================================================
# This section is Hubbard-specific. It reads the binary and builds
# universal (W, F, P, E) programs from Hubbard's instrument format.

def extract(
    subtune: int = 0,
    sid_path: str | None = None,
    ft_base: int | None = None,
    default_pw_min: int = 0x08,
    default_pw_max: int = 0x0E,
    verbose: bool = False,
) -> ExtractedSong:
    """Extract an :class:`ExtractedSong` from a Hubbard-engine SID.

    subtune: 0-indexed subtune number (default 0 = first subtune = PSID subtune 1).
    sid_path: SID file to extract from. Defaults to ThingOnASpring (SID_PATH).
    ft_base:  Base address of the freq table for extended-table runtime
              values. Defaults to 0x5428 (Commando-specific). Pass the
              discovered freq_table_addr for other songs.
    default_pw_min, default_pw_max:
              PWM bidirectional-mode bounds for the pulse_hi byte.
              Defaults match Commando ($08/$0E). Other Hubbard songs
              use different bounds — observe pw_hi range in the original
              SID's siddump output and pass appropriate values.
    verbose:  Raise this module's logger to DEBUG for the duration of the call.
    """
    from effect_detect import FREQ_PAL
    from py65.devices.mpu6502 import MPU

    from .decompile import decompile

    prev_level = logger.level
    if verbose:
        logger.setLevel(logging.DEBUG)

    try:
        if sid_path is None:
            sid_path = SID_PATH
        if ft_base is None:
            ft_base = 0x5428

        logger.debug("extract: sid_path=%s subtune=%d ft_base=$%04X",
                     sid_path, subtune, ft_base)

        decomp = decompile(sid_path)

        # --- T: Frequency Table ---
        T: list[int] = list(FREQ_PAL)  # T[0..95] = standard PAL

        # Extend with runtime values (Hubbard reads past the table)
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
        m.stPush(0xFF)
        m.stPush(0xEF)
        m.pc = struct.unpack('>H', d[10:12])[0]
        m.a = 0
        for _ in range(100000):
            if m.memory[m.pc] == 0x00:
                break
            m.step()
        m.stPush(0xFF)
        m.stPush(0xEF)
        m.pc = struct.unpack('>H', d[12:14])[0]
        for _ in range(50000):
            if m.memory[m.pc] == 0x00:
                break
            m.step()
        while len(T) < 120:
            i = len(T)
            addr = ft_base + i * 2
            T.append((m.memory[addr + 1] << 8) | m.memory[addr])

        # --- I: Instruments ---
        # Build W and F PROGRAMS from Hubbard's fx_flags.
        # The engine doesn't know about drums/arpeggio — only the decompiler does.

        instruments: list[Instrument] = []
        # Per-subtune speed if available; else fall back to default.
        if decomp.speed_table is not None and subtune < len(decomp.speed_table):
            speed = decomp.speed_table[subtune]
        elif decomp.speed is not None:
            speed = decomp.speed
        else:
            speed = 2
        hr_frames = 3  # Hubbard hard-restarts 3 frames before note end

        for rh in decomp.instruments:
            ctrl = rh.ctrl

            # W program: sequence of waveform bytes
            # Hubbard's pattern: drum instruments get noise burst ($80) on frames 1-2
            if rh.has_drum:
                w_steps = [ctrl | 0x01, 0x80, 0x80, 0x80, ctrl & 0xFE]
                w_loop = 4  # sustain loops on last step
            else:
                w_steps = [ctrl | 0x01]  # gate on (engine handles gate-off via E)
                w_loop = 0

            # Arp: Thing-on-a-Spring uses +24 semitones (2 octaves), not +12.
            # Engine code: $C2ED: LDA v_pitch; CLC; ADC #$18 (=24).
            # The Commando/Monty default of +12 was wrong for this engine
            # and caused V1's arp pitches to play one octave too low,
            # producing 24-frame snapshot drift around F186-F209.
            arp_offset = 24 if rh.has_arpeggio else 0

            # fx_flags
            flags = rh.fx_flags if rh.fx_flags is not None else 0

            # Vibrato: byte+5 of instrument table = vibrato depth scaler.
            # When nonzero, a triangle-wave LFO modulates frequency.
            # LFO: (frame_counter & 7) → 0,1,2,3,3,2,1,0 (period 8 frames)
            # Delta: freq[pitch+1] - freq[pitch], right-shifted byte5 times
            # Applied: base_freq + delta * depth, after 6 frames into note
            # rh_decompile.py stores this as vibrato_depth (data[5]).
            vibrato_scale = rh.vibrato_depth if hasattr(rh, 'vibrato_depth') else 0

            # P program: PW modulation
            # fx_flags bit 3 determines PW MODE (not table arp — that's post-1986)
            pw_speed = rh.pwm_speed
            pw_simple = (flags >> 3) & 1  # bit 3
            if pw_speed == 0:
                pw_mode = 'none'
                pw_min = 0xFF
                pw_max = 0xFF
            elif pw_simple:
                # Simple increment: pw_lo += pw_speed each frame, 8-bit wrap
                pw_mode = 'linear'
                pw_min = 0xFF
                pw_max = 0xFF
            else:
                # Oscillating: bounce pw between default_pw_min and default_pw_max
                # in pulse_hi. Defaults are Commando's $08/$0E; pass explicit
                # values for other songs via extract(default_pw_min=..., ...).
                pw_mode = 'bidirectional'
                pw_min = default_pw_min
                pw_max = default_pw_max

            # E spec: ADSR + gate/adsr timing
            # Vibrato runs for ALL instruments (even arp) — intermediate write affects SID
            has_bit0 = bool(flags & 1)
            has_skydive = bool(flags & 2)   # bit 1 in Hubbard instrfx
            instruments.append(Instrument(
                id=rh.index,
                waveform=Waveform(steps=w_steps, loop=w_loop),
                pwm=PWMConfig(
                    speed=pw_speed,
                    mode=pw_mode,
                    min_hi=pw_min,
                    max_hi=pw_max,
                    init_pw=rh.pulse_width,
                ),
                envelope=Envelope(
                    ad=rh.ad,
                    sr=rh.sr,
                    gate_off_delta=hr_frames,
                    adsr_zero_delta=hr_frames,
                ),
                arp_offset=arp_offset,
                vibrato_scale=vibrato_scale,
                has_bit0=has_bit0,
                has_skydive=has_skydive,
            ))

        # --- S: Score ---
        if subtune >= len(decomp.songs):
            raise ValueError(
                f"subtune {subtune} out of range "
                f"(have {len(decomp.songs)} songs)"
            )
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
                                # TIE: use previous note's pitch; no freq write, no gate
                                pitch = notes[-1].pitch if notes else 0
                            else:
                                pitch = note.pitch
                            # has_inst_byte: whether the original Hubbard note had an instrument byte
                            # This determines hub_off advance (3 bytes if yes, 2 if no)
                            # Portamento notes have inst=None but use 3 bytes in Hubbard format
                            # (pitch byte + portamento byte = 2 bytes, no separate instrument byte).
                            # In Hubbard's format, portamento notes do NOT have an extra inst byte.
                            has_inst_byte = (note.instrument is not None)
                            # Bit7=1 → no inst byte (hub_off += 2)
                            # Bit6=1 → tie note (no freq write, ctrl without gate)
                            # no_release encoded only in drum_trig bit7 (not in stored_inst)
                            no_release = hasattr(note, 'no_release') and bool(note.no_release)
                            stored_inst = (
                                cur_inst
                                | (0 if has_inst_byte else 0x80)
                                | (0x40 if is_tie else 0)
                            )
                            # drum_trig: portamento notes set a per-frame freq slide.
                            # Encoded as raw byte: (speed << 1) | direction, where:
                            #   delta = drum_trig & 0x7E (bits 6-1)
                            #   direction = drum_trig & 0x01 (0=up, 1=down)
                            drum_trig_byte = 0
                            if hasattr(note, 'portamento') and note.portamento is not None:
                                porta_speed, direction = note.portamento
                                drum_trig_byte = ((porta_speed & 0x3F) << 1) | (direction & 1)
                            # Encode no_release flag in bit7 of drum_trig.
                            # Drum slide uses bits 0-6 only (delta=bits6-1, dir=bit0).
                            # Bit7=1 means: skip gate-off at note end (GT no_release flag).
                            if no_release:
                                drum_trig_byte |= 0x80
                            notes.append(Note(
                                pitch=pitch,
                                duration=dur + 1,  # Hubbard: counter loads D, decrements to -1
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

        logger.debug("extract: %d instruments, %d voices, tempo=%d",
                     len(instruments), len(score.voices), score.tempo)

        return ExtractedSong(freq_table=T, instruments=instruments, score=score)
    finally:
        if verbose:
            logger.setLevel(prev_level)
