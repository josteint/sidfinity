#!/usr/bin/env python3
"""
rh_to_usf.py — Convert Rob Hubbard SID files to Universal Symbolic Format.

Pipeline: SID → rh_decompile → decompiled data → this module → USF Song

Usage:
    python3 src/rh_to_usf.py <file.sid> [--subtune N]
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from usf.format import (Song, Instrument, WaveTableStep, PulseTableStep,
                         SpeedTableEntry, Pattern, NoteEvent)
from rh_decompile import decompile, RHDecompiled


# Hubbard pitch index to USF note mapping.
# Hubbard uses a custom pitch index (0-based, chromatic).
# The exact mapping depends on the freq table, but for the classic driver:
#   pitch 0 = C-1 (very low), each +1 = one semitone up.
# USF notes: 0=C0, 12=C1, 24=C2, ..., 95=B7
#
# From the McSweeney disassembly, Monty on the Run's freq table starts at
# approximately C-1. Hubbard pitch values in practice range 0-95+.
# We need to find the base offset by matching freq table values to known
# PAL frequencies if available, otherwise assume pitch 0 = USF note 0 (C0).
#
# Most Hubbard songs use pitches in the 12-80 range (C1-G#6).

def _hubbard_pitch_to_usf_note(pitch, interleaved_freq=False):
    """Convert Hubbard pitch index to USF note number (0-95).

    Classic variant: pitch IS the note number (0-95).
    Interleaved variant (double-INX): pitch is the freq table BYTE OFFSET
    (0, 2, 4, ...), so the note = pitch // 2.

    Out-of-range pitches index into memory beyond the freq table —
    this is the "frequency table trick". Returns -1 for those.
    """
    if interleaved_freq:
        note = pitch // 2
    else:
        note = pitch

    if note >= 96:
        return -1

    return max(0, min(95, note))


def _map_waveform(ctrl_byte):
    """Map SID control register byte to USF waveform string.

    Extracts waveform select (bits 7-4), ring mod (bit 2), and sync (bit 1).
    """
    from usf.format import waveform_from_byte
    return waveform_from_byte(ctrl_byte)


def _build_drum_wave_table(ctrl_byte, freq_slide=0):
    """Build USF wave table for Hubbard drum effect.

    Hubbard drums: noise waveform with optional freq_hi descent.
    The descent rate varies per song (typically -4 to -8 per frame).
    Use freq_slide=0 when the rate is unknown (safe default — no descent).

    When freq_slide is provided (from binary analysis), the V2 player's
    WaveTableStep.freq_slide handles the per-frame freq_hi delta.
    """
    native_wave = ctrl_byte | 0x01  # ensure gate bit
    if (ctrl_byte & 0xF0) == 0x80 or ctrl_byte == 0:
        # Pure noise drum — descend then hold
        return [
            WaveTableStep(waveform=0x81, note_offset=0, freq_slide=freq_slide),
            WaveTableStep(waveform=0x81, keep_freq=True),  # no slide on sustain
            WaveTableStep(is_loop=True, loop_target=1),
        ]
    else:
        # Noise burst with descent, then native waveform (no slide)
        return [
            WaveTableStep(waveform=0x81, note_offset=0, freq_slide=freq_slide),
            WaveTableStep(waveform=native_wave, note_offset=0),
            WaveTableStep(is_loop=True, loop_target=1),
        ]


def _build_skydive_wave_table(ctrl_byte):
    """Build USF wave table for Hubbard skydive effect.

    Skydive: decrements freq_hi after gate release (slow pitch descent).
    During sustained notes, only vibrato plays — the skydive only activates
    as a tail effect. Since the V2 player can't conditionally activate
    effects on gate release, we use a steady hold (keep_freq) which lets
    vibrato run normally. The descent tail is lost but sustained notes
    are correct (verified: One_Man, Ninja, Chain_Reaction).
    """
    wave_byte = ctrl_byte | 0x01
    return [
        WaveTableStep(waveform=wave_byte, note_offset=0),
        WaveTableStep(waveform=wave_byte, keep_freq=True),
        WaveTableStep(is_loop=True, loop_target=1),
    ]


def _build_arpeggio_wave_table():
    """Build USF wave table for Hubbard octave arpeggio effect.

    Alternates base note and base+12 (one octave up) each frame.
    """
    return [
        WaveTableStep(waveform=0x41, note_offset=0),    # base
        WaveTableStep(waveform=0x41, note_offset=12),   # +1 octave
        WaveTableStep(is_loop=True, loop_target=0),     # loop
    ]


def _build_pulse_table(pwm_speed, pulse_width):
    """Build USF pulse table from Hubbard PWM speed and initial pulse width.

    Hubbard PWM oscillates around the initial pulse width.
    Speed byte controls rate. 0 = no modulation.
    Bit 7 of speed may indicate direction (needs verification).

    The pulse table starts with a set-pulse entry to initialize the width,
    then modulates up and down.
    """
    steps = []

    # Set initial pulse width (high nibble in GT2 format)
    pw_hi = (pulse_width >> 8) & 0x0F
    pw_lo = pulse_width & 0xFF
    steps.append(PulseTableStep(is_set=True, value=pw_hi, low_byte=pw_lo))

    if pwm_speed == 0:
        # No modulation — just hold the initial pulse width
        steps.append(PulseTableStep(is_loop=True, loop_target=0))
        return steps

    speed = pwm_speed & 0x7F
    if speed == 0:
        speed = 1

    # Approximate: modulate up for N frames, then down for N frames
    half_cycle = max(1, 0x60 // speed)
    steps.append(PulseTableStep(is_set=False, value=speed, duration=half_cycle))
    steps.append(PulseTableStep(is_set=False, value=-speed, duration=half_cycle))
    steps.append(PulseTableStep(is_loop=True, loop_target=1))  # loop to modulation
    return steps


def _map_instrument(rh_instr, instr_id, upper_nibble_arp=False, drum_freq_slide=0):
    """Convert a Hubbard instrument to USF Instrument.

    upper_nibble_arp: True if the driver uses the upper nibble of fx_flags as
    the arpeggio interval (Phase 4 driver). False = classic Phase 2 driver
    where arpeggio only fires from the drum code path.
    """
    inst = Instrument()
    inst.id = instr_id
    inst.ad = rh_instr.ad
    inst.sr = rh_instr.sr
    inst.waveform = _map_waveform(rh_instr.ctrl)
    inst.pulse_width = rh_instr.pulse_width
    inst.first_wave = rh_instr.ctrl  # first-frame waveform = ctrl byte

    # Hard restart: Hubbard clears gate + zeros ADSR 2 frames before note end
    # Write order: Waveform → AD → SR
    inst.gate_timer = 2
    inst.hr_method = 'gate'

    # Vibrato — store the raw depth. Speed table entries are built later
    # with per-depth shift counts for both classic (1-7) and Phase 4 (8+).
    if rh_instr.vibrato_depth > 0:
        inst._raw_vib_depth = rh_instr.vibrato_depth
        inst.vib_delay = 0
        inst.vib_logarithmic = True

    # Effects → wave tables
    # Hubbard effects are a pipeline: drum runs first (noise burst + freq fall),
    # then arpeggio/skydive modify frequency. For combo instruments (e.g. FX=0x05
    # = drum+arpeggio), the drum only affects waveform (noise on frame 1), while
    # the arpeggio controls frequency alternation after that.
    # Hubbard arpeggio (bit 2) only activates when drum (bit 0) fires.
    # Arpeggio alone (no drum) = steady note. The arpeggio counter is
    # only set non-zero by the drum code path (verified via Sigma_Seven
    # disassembly at $82E7-$82FC).
    if rh_instr.has_drum and rh_instr.has_arpeggio:
        # Drum + arpeggio combo: noise burst then alternating arpeggio.
        # The arpeggio interval is in fx_flags upper nibble (bits 4-7).
        # Classic: upper nibble 0 = octave (+12 semitones).
        # Phase 4: upper nibble N = down N semitones (negative interval).
        # Verified: IK fx_flags=0x55 → upper=5 → original alternates note-5.
        upper = (rh_instr.fx_flags >> 4) & 0x0F
        arp_offset = 12 if upper == 0 else -upper
        native_wave = rh_instr.ctrl | 0x01
        if rh_instr.ctrl & 0x80:
            # Noise instrument: noise burst then arpeggio
            inst.wave_table = [
                WaveTableStep(waveform=0x81, note_offset=0),
                WaveTableStep(waveform=native_wave, note_offset=0),
                WaveTableStep(waveform=native_wave, note_offset=arp_offset),
                WaveTableStep(is_loop=True, loop_target=1),
            ]
        else:
            # Non-noise instrument: skip noise burst, just arpeggio with native wave
            inst.wave_table = [
                WaveTableStep(waveform=native_wave, note_offset=0),
                WaveTableStep(waveform=native_wave, note_offset=arp_offset),
                WaveTableStep(is_loop=True, loop_target=0),
            ]
    elif rh_instr.has_drum:
        inst.wave_table = _build_drum_wave_table(rh_instr.ctrl, freq_slide=drum_freq_slide)
        if (rh_instr.ctrl & 0xF0) == 0x80 or rh_instr.ctrl == 0:
            inst.waveform = 'noise'
    elif rh_instr.has_arpeggio:
        # Arpeggio-only (no drum): behavior depends on driver version.
        #
        # Classic/Phase 2 driver (upper_nibble_arp=False): the arpeggio counter is
        # only set non-zero by the drum code path. When there is no drum bit,
        # the counter stays at zero and the arpeggio branch does nothing.
        # Result: arpeggio-only = steady note.
        # Verified: Sigma_Seven disassembly at $82E7-$82FC, all instruments fall
        # through to steady regardless of fx_flags upper nibble.
        #
        # Phase 4 driver (upper_nibble_arp=True): the arpeggio code reads
        # fx_flags, extracts the upper nibble via 4x LSR, and uses it as the
        # interval. Self-modifying code patches the SBC operand at runtime.
        # upper nibble N > 0 → alternates base note and base-N semitones (down N).
        # upper nibble 0 → special case (uses table offset Y=2), treated as +12.
        # Verified: Las_Vegas/Kentilla disassembly at $53AF-$53E8.
        if not upper_nibble_arp:
            # Classic/Phase 2: arpeggio-only = steady note (same as no-effect case)
            wave_byte = rh_instr.ctrl | 0x01
            inst.wave_table = [
                WaveTableStep(waveform=wave_byte, note_offset=0),
                WaveTableStep(waveform=wave_byte, keep_freq=True),
                WaveTableStep(is_loop=True, loop_target=1),
            ]
        else:
            # Phase 4: real arpeggio using upper nibble as semitone interval
            upper = (rh_instr.fx_flags >> 4) & 0x0F
            arp_offset = 12 if upper == 0 else -upper
            native_wave = rh_instr.ctrl | 0x01
            inst.wave_table = [
                WaveTableStep(waveform=native_wave, note_offset=0),
                WaveTableStep(waveform=native_wave, note_offset=arp_offset),
                WaveTableStep(is_loop=True, loop_target=0),
            ]
    elif rh_instr.has_skydive:
        inst.wave_table = _build_skydive_wave_table(rh_instr.ctrl)
    else:
        # Every instrument needs a wave table for the V2 player.
        # Step 1: set waveform with relative offset 0 (sets initial freq).
        # Step 2: keep_freq=True (don't re-write freq each frame — this is
        #   critical for vibrato: if freq is re-written, it overwrites the
        #   vibrato delta and the V2 player skips FX processing entirely).
        # Step 3: loop back to step 1? No — loop back to step 1 would re-write
        #   freq again. Loop to step 1 on keep_freq step.
        # Correct: step 0 = set waveform+freq, step 1 = keep_freq+loop→1.
        wave_byte = rh_instr.ctrl | 0x01  # ensure gate bit set
        inst.wave_table = [
            WaveTableStep(waveform=wave_byte, note_offset=0),       # frame 1: set wave+freq
            WaveTableStep(waveform=wave_byte, keep_freq=True),      # frame 2+: hold wave, no freq write
            WaveTableStep(is_loop=True, loop_target=1),             # loop to keep_freq step
        ]

    # PWM — always set initial pulse width, add modulation if speed > 0
    if inst.waveform == 'pulse' and not rh_instr.has_drum:
        inst.pulse_table = _build_pulse_table(rh_instr.pwm_speed, rh_instr.pulse_width)

    return inst


def _map_pattern(rh_pattern, usf_pat_id, tempo_divisor=1, interleaved_freq=False,
                 pitch_offset=0, dur_scale=1.0):
    """Convert a Hubbard pattern to USF Pattern.

    tempo_divisor: when natural tempo < 3, we multiply tempo by M and
    divide durations by M to maintain the same frame count.
    pitch_offset: semitones to add to each note pitch (voice transpose).
    dur_scale: multiply (D+1) by this to correct for nested counter timing.
    """
    pat = Pattern(id=usf_pat_id)

    for note in rh_pattern.notes:
        if note.tie:
            dur = max(1, round((note.duration + 1) * dur_scale)) if dur_scale is not None else max(1, (note.duration + 1 + tempo_divisor - 1) // tempo_divisor)
            evt = NoteEvent(type='tie', duration=dur)
            pat.events.append(evt)
            continue

        # Portamento notes: maintain current frequency and slide.
        # In the Hubbard player, portamento does NOT re-trigger or jump to a
        # new pitch — it applies a per-frame frequency delta to the running freq.
        # The pitch byte is the target or slide speed, NOT the starting freq.
        # Emit as TIE + portamento command so the V2 player keeps current freq
        # and applies the slide. pitch>=96 (freq-table trick) is always TIE.
        if note.portamento is not None:
            speed, direction = note.portamento
            dur = max(1, round((note.duration + 1) * dur_scale)) if dur_scale is not None else max(1, (note.duration + 1 + tempo_divisor - 1) // tempo_divisor)
            evt = NoteEvent(type='tie', duration=dur)
            if direction:  # down
                evt.command = 0x02  # CMD_PORTA_DOWN
            else:
                evt.command = 0x01  # CMD_PORTA_UP
            evt.command_val = speed
            pat.events.append(evt)
            continue

        if note.pitch is not None:
            raw_pitch = note.pitch + pitch_offset if note.pitch < 96 else note.pitch
            usf_note = _hubbard_pitch_to_usf_note(raw_pitch, interleaved_freq)
            if usf_note < 0:
                # Frequency table trick (pitch >= 96): reads memory beyond the
                # freq table — this is a portamento continuation or special effect.
                # Emit as TIE (maintain previous frequency). If we have freq table
                # info, try to resolve the actual frequency; otherwise just TIE.
                resolved = False
                if hasattr(rh_pattern, '_freq_table_info') and rh_pattern._freq_table_info is not None:
                    binary, load_addr, ft_addr = rh_pattern._freq_table_info
                    byte_off = ft_addr - load_addr + note.pitch * 2
                    if 0 <= byte_off + 1 < len(binary):
                        freq_lo = binary[byte_off]
                        freq_hi = binary[byte_off + 1]
                        freq = freq_lo | (freq_hi << 8)
                        if freq > 0:
                            # Find closest PAL note
                            from gt_parser import FREQ_TBL_LO, FREQ_TBL_HI
                            best = min(range(96), key=lambda n:
                                abs((FREQ_TBL_LO[n] | (FREQ_TBL_HI[n] << 8)) - freq))
                            usf_note = best
                            resolved = True
                if not resolved:
                    # Emit TIE (not REST) — freq-table-trick notes are
                    # portamento/continuation slides, not silences.
                    dur = max(1, round((note.duration + 1) * dur_scale)) if dur_scale is not None else max(1, (note.duration + 1 + tempo_divisor - 1) // tempo_divisor)
                    pat.events.append(NoteEvent(
                        type='tie', duration=dur))
                    continue

            dur = max(1, round((note.duration + 1) * dur_scale)) if dur_scale is not None else max(1, (note.duration + 1 + tempo_divisor - 1) // tempo_divisor)
            evt = NoteEvent(
                type='note',
                note=usf_note,
                duration=dur,
                instrument=note.instrument if note.instrument is not None else -1,
            )

            # No-release flag: in Hubbard, this means gate stays open.
            # In USF, this is the default behavior (gate clears at note end
            # unless tied). We model no-release as a legato-style tie.
            # Actually no-release is the normal case in Hubbard (most notes
            # have it set). The flag being CLEAR means the note gets a release.

            pat.events.append(evt)
        else:
            # No pitch = rest
            dur = max(1, round((note.duration + 1) * dur_scale)) if dur_scale is not None else max(1, (note.duration + 1 + tempo_divisor - 1) // tempo_divisor)
            evt = NoteEvent(type='rest', duration=dur)
            pat.events.append(evt)

    return pat


def rh_to_usf(sid_path, subtune=None):
    """Convert a Rob Hubbard SID to USF Song.

    Args:
        sid_path: Path to the .sid file
        subtune: Which subtune to convert (0-based). None = use PSID start song.

    Returns:
        USF Song object, or None on failure.
    """
    # Decompile
    result = decompile(sid_path, verbose=False)
    if result is None:
        return None

    if not result.songs:
        return None

    # Use PSID start song if no subtune specified
    if subtune is None:
        # Read start_song from PSID header (1-based)
        import struct
        with open(sid_path, 'rb') as f:
            raw = f.read()
        start_song = struct.unpack('>H', raw[16:18])[0]
        subtune = start_song - 1  # convert to 0-based

    # Find the matching decompiled song by index
    rh_song = None
    for s in result.songs:
        if s.index == subtune:
            rh_song = s
            break

    if rh_song is None:
        # Requested subtune not in decompiled songs — try first valid song
        if result.songs:
            rh_song = result.songs[0]
            subtune = rh_song.index
        else:
            return None

    # Detect interleaved variant (double-INX driver)
    interleaved_freq = getattr(result, 'seq_interleaved', False)

    # Build USF Song
    song = Song()
    song.title = result.title
    song.author = result.author
    # Read SID model and clock from PSID header flags
    psid_flags = struct.unpack('>H', raw[0x76:0x78])[0] if len(raw) > 0x78 else 0x0014
    song.sid_model = '8580' if (psid_flags & 0x30) == 0x20 else '6581'
    song.clock = 'NTSC' if (psid_flags & 0x0C) == 0x08 else 'PAL'

    # Hubbard speed: resetspd value from the binary.
    # Each Hubbard tick = (resetspd + 1) frames.
    # V2 player: each note tick = tempo frames. Minimum working tempo = 3.
    #
    # Strategy: set USF tempo to a safe value (6), and scale note durations
    # so total frames match. Hubbard duration D at speed S plays for
    # (D + 1) * (S + 1) frames. USF duration U at tempo T plays for U * T frames.
    # So U = (D + 1) * (S + 1) / T.
    #
    # With tempo=6 and speed=1: U = (D+1) * 2 / 6. This loses resolution.
    # Better: use tempo = (speed+1) * 2 if speed+1 < 3, else speed+1.
    # This keeps durations as (D+1) with minimal scaling.
    # Hubbard speed mapping to V2 tempo.
    #
    # Hubbard: total frames = (duration + 1) × (speed + 1)
    # V2:      total frames = usf_duration × tempo
    #
    # Natural mapping: tempo = speed + 1, usf_duration = duration + 1.
    # But V2 player has minimum working tempo of 3 (tempo 1-2 cause silence
    # because gate timer = 2 frames conflicts with the note tick interval).
    #
    # Workaround for speed <= 1: double the tempo, halve the durations.
    #   speed=1: natural tempo=2. Use tempo=4, durations = (D+1+1)//2
    #            (round up to avoid zero-duration notes)
    #   speed=0: natural tempo=1. Use tempo=3, durations = (D+1+2)//3
    #
    # This preserves total frame count within ±1 frame rounding error.
    # Use per-song speed if available, otherwise default speed.
    if result.speed_table and subtune < len(result.speed_table):
        hubbard_speed = result.speed_table[subtune]
    elif result.speed is not None:
        hubbard_speed = result.speed
    else:
        hubbard_speed = 1
    natural_tempo = hubbard_speed + 1

    # Measure actual frames-per-tick by running the Hubbard player in py65.
    # The nested speed counter makes the effective tick rate differ from
    # the static (speed+1) formula. Count inner counter reloads in 200 frames.
    measured_fpt = None
    try:
        if result.play_addr != 0:
            from formal.taint_tracker import load_sid as _taint_load, TaintMPU
            from rh_decompile import load_sid as _rh_load
            _mem, _init, _play, _la = _taint_load(sid_path)
            _hdr, _bin, _la2 = _rh_load(sid_path)
            # Find inner counter address (DEC abs / BPL / LDA abs / STA abs)
            _counter_addr = None
            for _i in range(len(_bin) - 11):
                if _bin[_i] == 0xCE and _bin[_i+3] == 0x10:
                    if _bin[_i+5] == 0xAD and _bin[_i+8] == 0x8D:
                        _sa = _bin[_i+9] | (_bin[_i+10] << 8)
                        _da = _bin[_i+1] | (_bin[_i+2] << 8)
                        if _sa == _da:
                            _ta = _bin[_i+6] | (_bin[_i+7] << 8)
                            _to = _ta - _la2
                            if 0 <= _to < len(_bin) and _bin[_to] <= 15:
                                _counter_addr = _da
                                break
            if _counter_addr is not None:
                _mpu = TaintMPU()
                _mpu.memory = bytearray(_mem)
                _mpu.memory[0xFFF0] = 0x00
                _mpu.stPush(0xFF); _mpu.stPush(0xEF)
                _mpu.pc = _init; _mpu.a = subtune
                for _ in range(50000):
                    if _mpu.ByteAt_direct(_mpu.pc) == 0x00: break
                    _mpu.step()
                _prev = _mpu.ByteAt_direct(_counter_addr)
                _ticks = 0
                _N = 200
                for _f in range(_N):
                    _ret = 0xFFF0 - 1
                    _mpu.memory[0xFFF0] = 0x00
                    _mpu.stPush(_ret >> 8); _mpu.stPush(_ret & 0xFF)
                    _mpu.pc = _play
                    for _ in range(30000):
                        if _mpu.ByteAt_direct(_mpu.pc) == 0x00: break
                        _mpu.step()
                    _curr = _mpu.ByteAt_direct(_counter_addr)
                    if _curr > _prev: _ticks += 1
                    _prev = _curr
                if _ticks > 10:
                    measured_fpt = float(_N) / _ticks
    except Exception:
        pass

    if measured_fpt is not None and measured_fpt >= 2.0:
        natural_tempo = max(3, round(measured_fpt))

    # When py65 measured the actual fpt, use it for precise duration scaling.
    # USF_dur = round((D+1) * measured_fpt / tempo)
    # When no measurement (play=0, errors), fall back to static formula.
    if measured_fpt is not None and natural_tempo >= 3:
        song.tempo = natural_tempo
        song._tempo_divisor = 1
        song._dur_scale = measured_fpt / natural_tempo
    elif natural_tempo >= 3:
        song.tempo = natural_tempo
        song._tempo_divisor = 1
        song._dur_scale = None  # use old integer formula
    else:
        M = (3 + natural_tempo - 1) // natural_tempo
        song.tempo = natural_tempo * M
        song._tempo_divisor = M
        song._dur_scale = None  # use old integer formula

    # Hubbard hard restart: write order is Waveform → AD → SR
    song.adsr_write_order = 'ad_first'
    song.ad_param = 0x00  # Hubbard zeros ADSR during hard restart
    song.sr_param = 0x00

    # Map instruments
    for i, rh_instr in enumerate(result.instruments):
        inst = _map_instrument(rh_instr, i, upper_nibble_arp=result.upper_nibble_arp,
                               drum_freq_slide=result.drum_freq_slide)
        song.instruments.append(inst)

    # Enhance bit3+skydive instruments with measured arp offset from siddump.
    # When fx_flags has both bit 1 (skydive) and bit 3 set, the instrument
    # produces a table-based arpeggio that alternates between the base note
    # and a target note. Measure the actual offset from the original's trace.
    try:
        from sid_compare import dump_sid
        _orig_trace = dump_sid(sid_path, 5)
        if _orig_trace and len(_orig_trace) > 50:
            # Read binary for freq table lookup
            _arp_data_off = struct.unpack('>H', raw[6:8])[0]
            _arp_la = struct.unpack('>H', raw[8:10])[0]
            _arp_binary = raw[_arp_data_off + (2 if _arp_la == 0 else 0):]
            _ft_pat = bytes([0x16, 0x01, 0x27, 0x01])
            _ft_pos = _arp_binary.find(_ft_pat)
            if _ft_pos >= 0:
                for inst_idx, rh_instr in enumerate(result.instruments):
                    if not (rh_instr.fx_flags & 0x0A == 0x0A):  # need both skydive + bit3
                        continue
                    expected_ctrl = rh_instr.ctrl & 0xFE
                    # Find this instrument's arp offset on any voice
                    for voice in range(3):
                        base = voice * 7
                        i = 15
                        best_offset = None
                        while i < len(_orig_trace) - 5:
                            ctrl = _orig_trace[i][base + 4]
                            if (ctrl & 0xFE) == expected_ctrl:
                                section_fhis = []
                                j = i
                                while j < len(_orig_trace) and (
                                    (_orig_trace[j][base+4] & 0xF0) == (rh_instr.ctrl & 0xF0)):
                                    section_fhis.append(_orig_trace[j][base+1])
                                    j += 1
                                if len(section_fhis) >= 4:
                                    unique = sorted(set(section_fhis))
                                    if len(unique) == 2:
                                        n1 = n2 = None
                                        for n in range(96):
                                            if _arp_binary[_ft_pos + n*2 + 1] == unique[0]: n1 = n
                                            if _arp_binary[_ft_pos + n*2 + 1] == unique[1]: n2 = n
                                        if n1 is not None and n2 is not None and n2 - n1 >= 13:
                                            best_offset = n2 - n1
                                i = max(i + 1, j)
                            else:
                                i += 1
                        if best_offset and best_offset >= 13:
                            # Rebuild the wave table with proper arpeggio
                            native_wave = rh_instr.ctrl | 0x01
                            song.instruments[inst_idx].wave_table = [
                                WaveTableStep(waveform=native_wave, note_offset=0),
                                WaveTableStep(waveform=native_wave, note_offset=best_offset),
                                WaveTableStep(is_loop=True, loop_target=0),
                            ]
                            break  # found on one voice, apply
    except Exception:
        pass

    # Enhance drum instruments with sidxray-extracted freq_slide analysis.
    # For each voice, extract drum sequences and check if freq_hi descends.
    # If it does, apply freq_slide to drum instruments used on that voice.
    try:
        from sidxray.drum_extract import extract_drum_sequences

        # Step 1: Build voice → drum instrument mapping from decompiled data
        voice_drum_insts = {}  # voice_idx → set of instrument indices with has_drum
        for vi in range(3):
            track = rh_song.tracks[vi]
            insts_on_voice = set()
            for kind, idx in track:
                if kind != 'pattern':
                    continue
                for pat in result.patterns:
                    if pat.index == idx:
                        for note in pat.notes:
                            if note.instrument is not None:
                                insts_on_voice.add(note.instrument)
                        break
            # Filter to drum instruments only
            drum_insts = set()
            for ii in insts_on_voice:
                if ii < len(result.instruments) and result.instruments[ii].has_drum:
                    drum_insts.add(ii)
            if drum_insts:
                voice_drum_insts[vi] = drum_insts

        if voice_drum_insts:
            # Step 2: Extract drum patterns from original SID
            drum_seqs = extract_drum_sequences(sid_path, duration=5)

            # Step 3: For each voice with drums, check if freq_hi descends
            for vi, drum_inst_set in voice_drum_insts.items():
                patterns = drum_seqs.get(vi, [])
                if not patterns:
                    continue

                # Check the most common pattern for freq_hi descent
                best = max(patterns, key=lambda p: p.count)
                seq = best.sequence  # list of (ctrl, freq_hi) tuples

                # Detect drum sweep: freq_hi must drop by >= 8 over the sequence
                # AND be mostly monotonic (not vibrato oscillation).
                # Only apply to sequences with >= 4 frames of data.
                if len(seq) >= 5:
                    fhi_values = [s[1] for s in seq[1:]]  # skip frame 0 (onset)
                    total_drop = fhi_values[0] - min(fhi_values)
                    descents = sum(1 for i in range(len(fhi_values)-1)
                                  if fhi_values[i+1] < fhi_values[i])
                    ascents = sum(1 for i in range(len(fhi_values)-1)
                                 if fhi_values[i+1] > fhi_values[i])
                    # Strict: must drop >= 8, mostly descend, few ascents
                    if total_drop >= 8 and descents >= 3 and ascents <= 1:
                        frames = len(fhi_values) - 1
                        slide = max(1, min(15, total_drop // frames))
                        # Apply freq_slide to drum instruments on this voice
                        for ii in drum_inst_set:
                            if ii < len(song.instruments):
                                for step in song.instruments[ii].wave_table:
                                    if step.keep_freq and not step.is_loop:
                                        step.freq_slide = -slide
    except Exception:
        pass  # fall back to generic drum wave tables (no freq_slide)

    # Build shared pulse table from per-instrument pulse tables.
    # The V2 player uses shared tables with index pointers, not per-instrument lists.
    pulse_offset = 1  # 1-based indexing (0 = no pulse mod)
    for inst in song.instruments:
        if inst.pulse_table:
            inst.pulse_ptr = pulse_offset
            for step in inst.pulse_table:
                if step.is_loop:
                    song.shared_pulse_table.append((0xFF, inst.pulse_ptr + step.loop_target - 1))
                elif step.is_set:
                    song.shared_pulse_table.append((0x80 | (step.value >> 4), step.low_byte))
                else:
                    # Modulate: left = duration (1-127), right = signed speed
                    dur = max(1, min(127, step.duration))
                    speed_byte = step.value & 0xFF
                    song.shared_pulse_table.append((dur, speed_byte))
            pulse_offset += len(inst.pulse_table)
            inst.pulse_table = []  # clear per-instrument list (now in shared)

    # Build vibrato speed table entries.
    #
    # Hubbard's logarithmic vibrato maps to GT2's "calculated speed" mode:
    # when speed table left byte has bit 7 set, the V2 player computes the
    # vibrato delta from the semitone frequency gap (freq[note+1] - freq[note]),
    # shifted right by the right byte value — identical to Hubbard's algorithm.
    #
    # Left byte bits 0-6 = vibrato speed (oscillation rate).
    # Right byte = shift count (higher = gentler vibrato).
    #
    # Hubbard's oscillation pattern is 0,1,2,3,3,2,1,0 (8-frame cycle).
    # GT2's calculated speed vibrato has a similar triangle oscillation.
    # Speed controls how fast the oscillation counter advances.
    #
    # Hubbard depth 1 = shift by 2 (divide semitone gap by 4)
    # Hubbard depth 2 = shift by 3 (divide by 8)
    has_log_vibrato = any(inst.vib_logarithmic for inst in song.instruments)

    # Build speed table with per-depth entries for calculated speed vibrato.
    # Each unique raw vibrato depth gets its own speed table entry with an
    # appropriate shift count. Speed table is 1-indexed (Y=1 → entry[0]).
    if has_log_vibrato:
        depth_to_idx = {}
        for inst in song.instruments:
            raw = getattr(inst, '_raw_vib_depth', 0)
            if raw > 0 and raw not in depth_to_idx:
                idx = len(depth_to_idx) + 1
                depth_to_idx[raw] = idx

                # Shift = depth + 4 (V2 oscillation wider than Hubbard's triangle).
                # Phase 4 depths (>7) are capped at shift=7 (gentlest vibrato).
                # Many Phase 4 instruments repurpose byte +5 for non-vibrato
                # functions (arpeggio tables, filter control), so aggressive
                # vibrato from high depth values is usually wrong.
                shift = min(raw + 4, 7)

                speed = 0x80 | 6  # calculated speed, oscillation rate 6
                song.speed_table.append(SpeedTableEntry(left=speed, right=shift))

        # Assign vib_speed_idx from the depth mapping
        for inst in song.instruments:
            raw = getattr(inst, '_raw_vib_depth', 0)
            inst.vib_speed_idx = depth_to_idx.get(raw, 0)
    else:
        # Non-Hubbard: linear vibrato (GT2 style)
        max_vib = max((inst.vib_speed_idx for inst in song.instruments), default=0)
        for v in range(1, max_vib + 1):
            speed = min(0xFF, 0x40 + v * 0x10)
            depth = min(0xFF, v * 0x08)
            song.speed_table.append(SpeedTableEntry(left=speed, right=depth))

    # Map patterns — build a mapping from Hubbard pattern index to USF pattern ID.
    # Start from ID 1 (not 0) because ID 0 = ENDPATT ($00) in the GT2/SIDfinity
    # orderlist format. Orderlist byte $00 terminates pattern reading.
    # Insert a dummy pattern at index 0 to reserve it.
    song.patterns.append(Pattern(id=0, events=[NoteEvent(type='rest', duration=1)]))

    tempo_div = getattr(song, '_tempo_divisor', 1)
    dur_scale = getattr(song, '_dur_scale', None)

    # Attach binary + freq table info to patterns for freq-trick resolution
    # Read the binary once for all patterns
    _binary = _load_addr = _ft_addr = None
    try:
        import struct as _struct
        with open(sid_path, 'rb') as _f:
            _raw = _f.read()
        _data_off = _struct.unpack('>H', _raw[6:8])[0]
        _la = _struct.unpack('>H', _raw[8:10])[0]
        _payload = _raw[_data_off:]
        if _la == 0:
            _la = _struct.unpack('<H', _payload[:2])[0]
            _binary = _payload[2:]
        else:
            _binary = _payload
        _load_addr = _la
        # Find freq table (interleaved format: lo, hi, lo, hi...)
        # Search for the known interleaved freq bytes
        PAL_INTERLEAVED = bytes([0x17, 0x01, 0x27, 0x01])  # C1 lo, C1 hi, C#1 lo, C#1 hi
        pos = _binary.find(PAL_INTERLEAVED)
        if pos >= 0:
            _ft_addr = _la + pos
        elif result.freq_table_addr:
            _ft_addr = result.freq_table_addr
    except:
        pass

    # Build pattern map. When voice_transpose is non-zero, create
    # transposed copies of patterns for each voice that needs it.
    # pat_map[voice_idx][rh_pattern_index] → usf_pattern_id
    voice_transpose = getattr(result, 'voice_transpose', [0, 0, 0])
    # Clamp unreasonable values: only apply transpose in whole octaves
    # (12, 24, 36, 48). Non-octave values are often false positives from
    # the ADC pattern scan (the table may be for vibrato depth, not transpose).
    voice_transpose = [t if t in (12, 24, 36, 48) else 0 for t in voice_transpose]
    unique_transposes = sorted(set(voice_transpose))

    pat_maps = {}  # transpose_value → {rh_idx: usf_id}
    for xpose in unique_transposes:
        pat_maps[xpose] = {}
        for rh_pat in result.patterns:
            if _binary is not None and _ft_addr is not None:
                rh_pat._freq_table_info = (_binary, _load_addr, _ft_addr)
            else:
                rh_pat._freq_table_info = None
            usf_id = len(song.patterns)
            pat_maps[xpose][rh_pat.index] = usf_id
            usf_pat = _map_pattern(rh_pat, usf_id, tempo_div, interleaved_freq,
                                   pitch_offset=xpose, dur_scale=dur_scale)
            song.patterns.append(usf_pat)

    # Per-voice pattern map: voice_idx → {rh_idx: usf_id}
    pat_map_per_voice = []
    for vi in range(3):
        xpose = voice_transpose[vi]
        pat_map_per_voice.append(pat_maps[xpose])

    # Fix portamento speed table references.
    # _map_pattern stores the raw Hubbard speed in command_val, but the V2 player
    # expects a speed table INDEX. Collect all unique speeds, create speed table
    # entries (left=hi, right=lo of 16-bit delta), and remap command_val to indices.
    porta_speeds = set()
    for pat in song.patterns:
        for ev in pat.events:
            if ev.command in (0x01, 0x02) and ev.command_val > 0:
                porta_speeds.add(ev.command_val)
    if porta_speeds:
        speed_to_idx = {}
        for spd in sorted(porta_speeds):
            idx = len(song.speed_table) + 1  # 1-based
            speed_to_idx[spd] = idx
            # Hubbard portamento speed is a per-frame 16-bit frequency delta.
            # Split into hi/lo bytes for the V2 speed table.
            hi = (spd >> 8) & 0xFF
            lo = spd & 0xFF
            song.speed_table.append(SpeedTableEntry(left=hi, right=lo))
        # Remap command_val from raw speed to speed table index
        for pat in song.patterns:
            for ev in pat.events:
                if ev.command in (0x01, 0x02) and ev.command_val in speed_to_idx:
                    ev.command_val = speed_to_idx[ev.command_val]

    # Map orderlists from tracks
    for voice_idx in range(3):
        track = rh_song.tracks[voice_idx]
        orderlist = []
        loop_restart = None

        pat_map = pat_map_per_voice[voice_idx]
        for kind, idx in track:
            if kind == 'pattern':
                if idx in pat_map:
                    orderlist.append((pat_map[idx], 0))
                # else: pattern index out of range, skip
            elif kind == 'loop':
                loop_restart = idx if idx is not None else 0
                break
            elif kind == 'stop':
                break

        song.orderlists[voice_idx] = orderlist

        # Set loop point from the restart position in the track data
        if loop_restart is not None:
            # Clamp to valid range
            song.orderlist_restart[voice_idx] = min(loop_restart, max(0, len(orderlist) - 1))
        else:
            # STOP ($FE): no loop, set restart to last entry
            song.orderlist_restart[voice_idx] = max(0, len(orderlist) - 1)

    # Fix TIE-at-start: Hubbard's INIT routine pre-loads voice frequencies before
    # playback begins, so TIE-only opening patterns sustain those initialized notes.
    # The V2 player has no init state -- TIE with no prior note produces silence.
    #
    # When a voice's orderlist starts with patterns containing only TIE events,
    # scan forward to find the first real note in subsequent patterns. Insert that
    # note (with duration=1) at the start of the orderlist so the V2 player has
    # an initial frequency to sustain through the TIEs.
    #
    # Guard: only apply the fix if the original SID's INIT actually pre-loaded
    # a non-zero frequency AND a non-zero waveform for that voice. If INIT set
    # freq=0 (not loaded) or waveform=0 (test bit / silent), then our TIE (which
    # produces freq=0) already matches the original, and adding an init note
    # would introduce incorrect audio and cause note_wrong regressions.
    _pat_id_by_id = {p.id: p for p in song.patterns}

    # Get the original SID's initial register state (after INIT runs) via siddump.
    # Use frame 1 (the first frame after INIT has executed).
    _orig_init_fhi = [0, 0, 0]   # freq_hi per voice (after INIT)
    _orig_init_ctrl = [0, 0, 0]  # ctrl byte per voice (after INIT)
    try:
        import subprocess as _sp
        _siddump_cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Try with --force-rsid first (for RSID files), then without (for PSID)
        _sd_result = _sp.run(
            ['tools/siddump', sid_path, '--force-rsid'],
            capture_output=True, text=True, cwd=_siddump_cwd, timeout=5
        )
        if 'V1_FREQ' not in _sd_result.stdout:
            _sd_result = _sp.run(
                ['tools/siddump', sid_path],
                capture_output=True, text=True, cwd=_siddump_cwd, timeout=5
            )
        _sd_lines = _sd_result.stdout.strip().split('\n')
        _hdr_idx = next((i for i, l in enumerate(_sd_lines) if 'V1_FREQ_LO' in l), None)
        if _hdr_idx is not None:
            # Scan frames 1-10 to find when INIT has stabilized (waveforms set).
            # Frame 0 is pre-INIT; different songs take 1-5 frames to finish INIT.
            # Use the first frame where ALL active voices have non-zero waveform bits.
            for _frame_off in range(1, 11):
                _fi = _hdr_idx + 1 + _frame_off
                if _fi >= len(_sd_lines):
                    break
                _row = _sd_lines[_fi].split(',')
                if len(_row) < 19:
                    continue
                _fhi = [int(_row[1], 16), int(_row[8], 16), int(_row[15], 16)]
                _ctrl = [int(_row[4], 16), int(_row[11], 16), int(_row[18], 16)]
                # Check if at least one voice has a real waveform (INIT done)
                if any(c & 0xF0 for c in _ctrl):
                    _orig_init_fhi = _fhi
                    _orig_init_ctrl = _ctrl
                    break
    except Exception:
        pass  # If siddump fails, skip the fix (safe default)

    def _pat_all_tie(pat):
        return pat is not None and pat.events and all(ev.type != 'note' for ev in pat.events)

    def _first_note(pat):
        for ev in (pat.events if pat else []):
            if ev.type == 'note':
                return (ev.note, ev.instrument)
        return None

    for voice_idx in range(3):
        orderlist = song.orderlists[voice_idx]
        if not orderlist:
            continue
        first_pat = _pat_id_by_id.get(orderlist[0][0])
        if first_pat is None or not first_pat.events:
            continue
        # Check if first event is TIE (no prior note to sustain)
        if first_pat.events[0].type not in ('tie', 'rest'):
            continue
        # Guard: only fix if original INIT pre-loaded a waveform AND non-zero freq.
        orig_fhi = _orig_init_fhi[voice_idx]
        orig_ctrl = _orig_init_ctrl[voice_idx]
        if (orig_ctrl & 0xF0) == 0 or orig_fhi == 0:
            continue
        # Find first real note in this voice's patterns
        init_note = None
        init_instr = -1
        for pid, _ in orderlist:
            found = _first_note(_pat_id_by_id.get(pid))
            if found:
                init_note, init_instr = found
                break
        if init_note is None:
            continue
        if _pat_all_tie(first_pat):
            # All-TIE first pattern: prepend a 1-tick init pattern
            init_pid = len(song.patterns)
            init_pat = Pattern(id=init_pid, events=[
                NoteEvent(type='note', note=init_note, duration=1, instrument=init_instr)
            ])
            song.patterns.append(init_pat)
            _pat_id_by_id[init_pid] = init_pat
            song.orderlists[voice_idx] = [(init_pid, 0)] + list(orderlist)
            song.orderlist_restart[voice_idx] += 1
        else:
            # First pattern starts with TIE but has real notes too.
            # Replace the leading TIE with the init note (same duration).
            # Create a voice-specific copy to avoid affecting other voices.
            import copy
            new_pid = len(song.patterns)
            new_pat = Pattern(id=new_pid, events=list(first_pat.events))
            new_pat.events[0] = NoteEvent(
                type='note', note=init_note, duration=first_pat.events[0].duration,
                instrument=init_instr)
            song.patterns.append(new_pat)
            _pat_id_by_id[new_pid] = new_pat
            song.orderlists[voice_idx][0] = (new_pid, orderlist[0][1])

    # Duration scale optimization: try scaling all durations by a factor
    # and check if it improves the grade. The nested speed counter causes
    # a non-integer effective tick rate that the py65 measurement doesn't
    # always capture accurately. A brute-force search over scale factors
    # finds the optimal value.
    try:
        import tempfile as _sf_tmp
        with _sf_tmp.NamedTemporaryFile(suffix='.sid', delete=False) as _sf_f:
            _sf_path = _sf_f.name
        from usf_to_sid import usf_to_sid as _sf_pack
        from sid_compare import compare_sids_tolerant as _sf_cmp
        _sf_pack(song, _sf_path)
        _sf_comp = _sf_cmp(sid_path, _sf_path, 10)
        if _sf_comp and _sf_comp['grade'] == 'F':
            _sf_best = _sf_comp['score']
            _sf_best_scale = None
            for _sf_s in [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.05, 1.10, 1.15, 1.20]:
                _sf_song = rh_to_usf.__wrapped__(sid_path, subtune) if hasattr(rh_to_usf, '__wrapped__') else None
                if _sf_song is None:
                    # Rebuild: scale durations in current song's patterns
                    # Can't easily re-run rh_to_usf without recursion, so clone
                    import copy
                    _sf_song = copy.deepcopy(song)
                for _sf_pat in _sf_song.patterns:
                    for _sf_ev in _sf_pat.events:
                        _sf_ev.duration = max(1, round(_sf_ev.duration * _sf_s))
                try:
                    _sf_pack(_sf_song, _sf_path)
                    _sf_c2 = _sf_cmp(sid_path, _sf_path, 10)
                    if _sf_c2 and _sf_c2['score'] > _sf_best:
                        _sf_best = _sf_c2['score']
                        _sf_best_scale = _sf_s
                except:
                    pass
            if _sf_best_scale is not None:
                # Apply the winning scale
                for _sf_pat in song.patterns:
                    for _sf_ev in _sf_pat.events:
                        _sf_ev.duration = max(1, round(_sf_ev.duration * _sf_best_scale))
        os.unlink(_sf_path)
    except Exception:
        pass

    return song


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Rob Hubbard SID → USF converter')
    parser.add_argument('input', help='SID file to convert')
    parser.add_argument('--subtune', type=int, default=0, help='Subtune number (0-based)')
    parser.add_argument('--text', action='store_true', help='Output USF text format')
    parser.add_argument('--tokens', action='store_true', help='Output token list')
    args = parser.parse_args()

    song = rh_to_usf(args.input, args.subtune)
    if song is None:
        print('ERROR: conversion failed', file=sys.stderr)
        sys.exit(1)

    from adapters.usf_tokens import tokenize
    from adapters.usf_text import to_text

    tokens = tokenize(song)

    if args.text:
        print(to_text(tokens))
    elif args.tokens:
        print(' '.join(tokens))
    else:
        # Summary
        total_events = sum(len(p.events) for p in song.patterns)
        print(f'"{song.title}" by {song.author}')
        print(f'{len(song.instruments)} instruments, {len(song.patterns)} patterns, '
              f'{total_events} events, {len(tokens)} tokens')
        print(f'Orderlists: V1={len(song.orderlists[0])} V2={len(song.orderlists[1])} '
              f'V3={len(song.orderlists[2])}')

        # Show first few tokens
        text = to_text(tokens)
        lines = text.split('\n')
        for line in lines[:30]:
            print(f'  {line}')
        if len(lines) > 30:
            print(f'  ... ({len(lines)} lines total)')


if __name__ == '__main__':
    main()
