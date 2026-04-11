#!/usr/bin/env python3
"""
rh_to_usf.py — Convert Rob Hubbard SID files to Universal Symbolic Format.

Pipeline: SID → rh_decompile → decompiled data → this module → USF Song

Usage:
    python3 src/rh_to_usf.py <file.sid> [--subtune N]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usf import (Song, Instrument, WaveTableStep, PulseTableStep,
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

def _hubbard_pitch_to_usf_note(pitch):
    """Convert Hubbard pitch index to USF note number (0-95).

    Hubbard pitch 0 = C-1 in McSweeney's notation = C0 in modern convention.
    The freq table has 96 entries (8 octaves), indexed by pitch*2 (interleaved
    lo/hi bytes). The values match the standard PAL freq table within ±1.

    Hubbard pitch maps directly to V2/USF note number with NO offset.
    Verified: Hubbard pitch 86 = freq $9C40 = PAL[86] exactly.

    Out-of-range pitches (>=96) index into player variables after the freq
    table — this is the "frequency table trick" used in Commando etc.
    Returns -1 for those.
    """
    if pitch >= 96:
        return -1  # frequency table trick — not a real note

    return max(0, min(95, pitch))


def _map_waveform(ctrl_byte):
    """Map SID control register byte to USF waveform string."""
    wave_bits = ctrl_byte & 0xF0
    if wave_bits & 0x80:
        return 'noise'
    elif wave_bits & 0x40:
        return 'pulse'
    elif wave_bits & 0x20:
        return 'saw'
    elif wave_bits & 0x10:
        return 'tri'
    return 'pulse'  # default


def _build_drum_wave_table():
    """Build USF wave table for Hubbard drum effect.

    Drum: noise waveform ($81) for rapid freq slide, then original waveform.
    The Hubbard drum does:
      Frame 1: set waveform to noise ($81), high frequency
      Frame 2+: frequency slides down rapidly with fast decay
    """
    return [
        WaveTableStep(waveform=0x81, note_offset=24),   # noise, +2 octaves
        WaveTableStep(waveform=0x81, note_offset=12),    # noise, +1 octave
        WaveTableStep(waveform=0x81, note_offset=0),     # noise, base
        WaveTableStep(waveform=0x41, note_offset=0),     # back to pulse
        WaveTableStep(is_loop=True, loop_target=3),      # loop on pulse
    ]


def _build_skydive_wave_table():
    """Build USF wave table for Hubbard skydive effect.

    Skydive: decrements freq_hi every other frame (slow pitch descent).
    We approximate this as a gradual downward pitch bend.
    """
    steps = []
    for i in range(8):
        steps.append(WaveTableStep(waveform=0x41, note_offset=-i))
    steps.append(WaveTableStep(is_loop=True, loop_target=7))  # hold lowest
    return steps


def _build_arpeggio_wave_table():
    """Build USF wave table for Hubbard octave arpeggio effect.

    Alternates base note and base+12 (one octave up) each frame.
    """
    return [
        WaveTableStep(waveform=0x41, note_offset=0),    # base
        WaveTableStep(waveform=0x41, note_offset=12),   # +1 octave
        WaveTableStep(is_loop=True, loop_target=0),     # loop
    ]


def _build_pulse_table(pwm_speed):
    """Build USF pulse table from Hubbard PWM speed byte.

    Hubbard PWM oscillates between ~$0800 and ~$0E00.
    Speed byte controls rate. 0 = no modulation.
    Bit 7 of speed may indicate direction (needs verification).
    """
    if pwm_speed == 0:
        return []

    # The speed is applied as a signed value to pulse width each frame
    # Positive = increase, then reverse at bounds
    # We model this as a modulation cycle
    speed = pwm_speed & 0x7F
    if speed == 0:
        speed = 1

    # Approximate: modulate up for N frames, then down for N frames
    half_cycle = max(1, 0x60 // speed)  # ~96 frames for full sweep at speed 1
    return [
        PulseTableStep(is_set=False, value=speed, duration=half_cycle),
        PulseTableStep(is_set=False, value=-speed, duration=half_cycle),
        PulseTableStep(is_loop=True, loop_target=0),
    ]


def _map_instrument(rh_instr, instr_id):
    """Convert a Hubbard instrument to USF Instrument."""
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

    # Vibrato
    if 0 < rh_instr.vibrato_depth <= 7:
        # Hubbard vibrato uses logarithmic freq delta.
        # Classic driver uses depths 1-3. Values > 7 in later drivers
        # may repurpose this byte for other effects — ignore those.
        inst.vib_speed_idx = rh_instr.vibrato_depth
        inst.vib_delay = 0  # Hubbard vibrato starts immediately

    # Effects → wave tables
    if rh_instr.has_drum:
        inst.wave_table = _build_drum_wave_table()
        inst.waveform = 'noise'
    elif rh_instr.has_arpeggio:
        inst.wave_table = _build_arpeggio_wave_table()
    elif rh_instr.has_skydive:
        inst.wave_table = _build_skydive_wave_table()
    else:
        # Every instrument needs a wave table for the V2 player.
        # Instruments without effects get a simple "set waveform and hold" table.
        wave_byte = rh_instr.ctrl | 0x01  # ensure gate bit set
        inst.wave_table = [
            WaveTableStep(waveform=wave_byte, note_offset=0),
            WaveTableStep(is_loop=True, loop_target=0),
        ]

    # PWM
    if rh_instr.pwm_speed > 0 and not rh_instr.has_drum:
        inst.pulse_table = _build_pulse_table(rh_instr.pwm_speed)

    return inst


def _map_pattern(rh_pattern, usf_pat_id, dur_scale=1):
    """Convert a Hubbard pattern to USF Pattern."""
    pat = Pattern(id=usf_pat_id)

    for note in rh_pattern.notes:
        if note.tie:
            # Tied note: extend previous note
            evt = NoteEvent(type='tie', duration=(note.duration + 1) * dur_scale)
            pat.events.append(evt)
            continue

        if note.pitch is not None:
            usf_note = _hubbard_pitch_to_usf_note(note.pitch)
            if usf_note < 0:
                # Frequency table trick — treat as a note with the raw index
                # clamped to valid range (best effort)
                usf_note = min(95, note.pitch)

            evt = NoteEvent(
                type='note',
                note=usf_note,
                duration=(note.duration + 1) * dur_scale,
                instrument=note.instrument if note.instrument is not None else -1,
            )

            # Portamento → USF command
            if note.portamento is not None:
                speed, direction = note.portamento
                if direction:  # down
                    evt.command = 0x02  # CMD_PORTA_DOWN
                else:
                    evt.command = 0x01  # CMD_PORTA_UP
                evt.command_val = speed

            # No-release flag: in Hubbard, this means gate stays open.
            # In USF, this is the default behavior (gate clears at note end
            # unless tied). We model no-release as a legato-style tie.
            # Actually no-release is the normal case in Hubbard (most notes
            # have it set). The flag being CLEAR means the note gets a release.

            pat.events.append(evt)
        else:
            # No pitch = rest
            evt = NoteEvent(type='rest', duration=(note.duration + 1) * dur_scale)
            pat.events.append(evt)

    return pat


def rh_to_usf(sid_path, subtune=0):
    """Convert a Rob Hubbard SID to USF Song.

    Args:
        sid_path: Path to the .sid file
        subtune: Which subtune to convert (0-based, default=0)

    Returns:
        USF Song object, or None on failure.
    """
    # Decompile
    result = decompile(sid_path, verbose=False)
    if result is None:
        return None

    if not result.songs:
        return None

    if subtune >= len(result.songs):
        # Try to use first valid song
        subtune = 0

    rh_song = result.songs[subtune]

    # Build USF Song
    song = Song()
    song.title = result.title
    song.author = result.author
    song.sid_model = '6581'
    song.clock = 'PAL'

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
    hubbard_speed = result.speed if result.speed is not None else 1
    frames_per_tick = hubbard_speed + 1

    if frames_per_tick >= 3:
        song.tempo = frames_per_tick
        song._duration_scale = 1  # no scaling needed
    else:
        # Speed too fast for V2 player. Multiply to get above minimum.
        # speed=1 (2 frames/tick): use tempo=6, scale durations by 3
        # speed=0 (1 frame/tick): use tempo=6, scale durations by 6
        multiplier = (3 + frames_per_tick - 1) // frames_per_tick  # ceil(3 / fpt)
        song.tempo = frames_per_tick * multiplier
        song._duration_scale = multiplier

    # Hubbard hard restart: write order is Waveform → AD → SR
    song.adsr_write_order = 'ad_first'
    song.ad_param = 0x00  # Hubbard zeros ADSR during hard restart
    song.sr_param = 0x00

    # Map instruments
    for i, rh_instr in enumerate(result.instruments):
        inst = _map_instrument(rh_instr, i)
        song.instruments.append(inst)

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

    # Build vibrato speed table entries
    # Hubbard vibrato depths 1-7 map to different speed/depth combinations
    max_vib = max((inst.vib_speed_idx for inst in song.instruments), default=0)
    max_vib = min(max_vib, 7)  # cap to valid range
    for v in range(max_vib + 1):
        # Approximate Hubbard logarithmic vibrato as GT2 speed table entries
        # Depth 1 = gentle, 2 = medium, 3 = strong
        speed = min(0xFF, 0x40 + v * 0x10)
        depth = min(0xFF, v * 0x08)
        song.speed_table.append(SpeedTableEntry(left=speed, right=depth))

    # Map patterns — build a mapping from Hubbard pattern index to USF pattern ID
    dur_scale = getattr(song, '_duration_scale', 1)
    pat_map = {}  # rh_pattern_index → usf_pattern_id
    for rh_pat in result.patterns:
        usf_id = len(song.patterns)
        pat_map[rh_pat.index] = usf_id
        usf_pat = _map_pattern(rh_pat, usf_id, dur_scale)
        song.patterns.append(usf_pat)

    # Map orderlists from tracks
    for voice_idx in range(3):
        track = rh_song.tracks[voice_idx]
        orderlist = []
        has_loop = False

        for kind, idx in track:
            if kind == 'pattern':
                if idx in pat_map:
                    orderlist.append((pat_map[idx], 0))  # (pattern_id, transpose=0)
                # else: pattern index out of range, skip
            elif kind == 'loop':
                has_loop = True
                break
            elif kind == 'stop':
                break

        song.orderlists[voice_idx] = orderlist

        # Set loop point: if track ends with LOOP ($FF), loop back to start
        if has_loop:
            song.orderlist_restart[voice_idx] = 0
        else:
            # STOP ($FE): no loop, set restart to last entry
            song.orderlist_restart[voice_idx] = max(0, len(orderlist) - 1)

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

    from usf import tokenize, to_text

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
