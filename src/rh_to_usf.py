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


def _build_drum_wave_table(ctrl_byte):
    """Build USF wave table for Hubbard drum effect.

    From McSweeney + data_format_reference.md:
    - Frame 1: noise ($81) at high pitch, freq_hi decrements rapidly
    - If ctrl is noise ($80/$81): always noise
    - If ctrl is non-noise: square on first frame, then noise, then back

    The V2 wave table can approximate this with descending relative offsets.
    The original does a per-frame freq_hi decrement which we can't exactly
    replicate, but descending semitone steps are close enough.
    """
    # Hubbard drum: noise burst on frame 1, then instrument's own waveform.
    # From data_format_reference.md:
    #   ctrl=$00/$80/$81: always noise
    #   ctrl=non-zero: instrument waveform + noise on first frame, then waveform only
    # The actual freq_hi decrement is in SoundWork, not reproducible in V2 wave table.
    # Keep it short to not disrupt timing.
    native_wave = ctrl_byte | 0x01  # ensure gate bit
    if (ctrl_byte & 0xF0) == 0x80 or ctrl_byte == 0:
        # Pure noise drum
        return [
            WaveTableStep(waveform=0x81, note_offset=0),
            WaveTableStep(waveform=0x81, keep_freq=True),
            WaveTableStep(is_loop=True, loop_target=1),
        ]
    else:
        # Noise burst then native waveform
        return [
            WaveTableStep(waveform=0x81, note_offset=0),     # frame 1: noise burst
            WaveTableStep(waveform=native_wave, keep_freq=True),
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


def _map_instrument(rh_instr, instr_id, upper_nibble_arp=False):
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
        inst.wave_table = _build_drum_wave_table(rh_instr.ctrl)
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


def _map_pattern(rh_pattern, usf_pat_id, tempo_divisor=1):
    """Convert a Hubbard pattern to USF Pattern.

    tempo_divisor: when natural tempo < 3, we multiply tempo by M and
    divide durations by M to maintain the same frame count.
    """
    pat = Pattern(id=usf_pat_id)

    for note in rh_pattern.notes:
        if note.tie:
            dur = max(1, (note.duration + 1 + tempo_divisor - 1) // tempo_divisor)
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
            dur = max(1, (note.duration + 1 + tempo_divisor - 1) // tempo_divisor)
            evt = NoteEvent(type='tie', duration=dur)
            if direction:  # down
                evt.command = 0x02  # CMD_PORTA_DOWN
            else:
                evt.command = 0x01  # CMD_PORTA_UP
            evt.command_val = speed
            pat.events.append(evt)
            continue

        if note.pitch is not None:
            usf_note = _hubbard_pitch_to_usf_note(note.pitch)
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
                    dur = max(1, (note.duration + 1 + tempo_divisor - 1) // tempo_divisor)
                    pat.events.append(NoteEvent(
                        type='tie', duration=dur))
                    continue

            dur = max(1, (note.duration + 1 + tempo_divisor - 1) // tempo_divisor)
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
            dur = max(1, (note.duration + 1 + tempo_divisor - 1) // tempo_divisor)
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

    # Always read raw SID bytes (needed for PSID header fields below)
    import struct
    with open(sid_path, 'rb') as f:
        raw = f.read()

    # Use PSID start song if no subtune specified
    if subtune is None:
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
    # V2 player: each note tick = tempo frames.
    #
    # Natural mapping: tempo = speed + 1, usf_duration = duration + 1.
    # Hubbard: total frames = (duration + 1) × (speed + 1)
    # V2:      total frames = usf_duration × tempo  ✓
    #
    # The V2 player supports tempo=1 and tempo=2: gate_timer is clamped to
    # max(0, tempo-1) in usf_to_sid.py so hard restart never fires too early.
    # Use per-song speed if available, otherwise default speed
    if result.speed_table and subtune < len(result.speed_table):
        hubbard_speed = result.speed_table[subtune]
    elif result.speed is not None:
        hubbard_speed = result.speed
    else:
        hubbard_speed = 1
    song.tempo = max(1, hubbard_speed + 1)
    song._tempo_divisor = 1

    # Hubbard hard restart: write order is Waveform → AD → SR
    song.adsr_write_order = 'ad_first'
    song.ad_param = 0x00  # Hubbard zeros ADSR during hard restart
    song.sr_param = 0x00

    # Map instruments
    for i, rh_instr in enumerate(result.instruments):
        inst = _map_instrument(rh_instr, i, upper_nibble_arp=result.upper_nibble_arp)
        song.instruments.append(inst)

    # Enhance drum instruments with sidxray-extracted wave table sequences.
    #
    # Strategy:
    # - If a voice uses EXACTLY ONE drum instrument, the most common extracted
    #   drum pattern IS that instrument's behavior — safe to replace its wave
    #   table with absolute_note steps from the extraction.
    # - If a voice uses MULTIPLE drum instruments, correlate each instrument
    #   to its extracted sequence using note-trigger timing: for each note
    #   trigger, find the nearest drum hit within ±5 frames, and vote for
    #   which canonical sequence belongs to which instrument.
    #
    # Safety requirements for wave table replacement:
    #   1. Extracted pattern has >= 2 hits (consistent, not a one-off).
    #   2. Instrument does NOT have has_arpeggio — arpeggio combos use
    #      note-relative frequencies and can't use absolute_note steps.
    #   3. Each instrument is only replaced ONCE — if it appears on
    #      multiple voices, use the highest-count pattern.
    #
    # The wave table is built from DrumPattern.wave_table_steps which
    # already produces WaveTableStep-compatible dicts with absolute_note.
    try:
        from sidxray.drum_extract import extract_drum_sequences, _run_siddump, _is_noise_onset, _extract_sequence, _canonicalize_sequence
        from collections import Counter as _Counter, defaultdict as _defaultdict

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
            # Determine siddump duration needed: for multi-drum-instrument voices,
            # we may need to dump longer to find frames where each instrument fires.
            # Check if any voice has multiple drum instruments.
            has_multi_drum_voice = any(len(ds) > 1 for ds in voice_drum_insts.values())
            dump_duration = 30 if has_multi_drum_voice else 5

            # Step 2: Extract drum patterns from original SID
            drum_seqs = extract_drum_sequences(sid_path, duration=dump_duration, min_hits=2)

            # Also get raw frame data for multi-drum correlation
            _raw_frames = None
            _VOICE_OFFSETS = None
            if has_multi_drum_voice:
                try:
                    from sidxray.drum_extract import VOICE_OFFSETS as _VOICE_OFFSETS
                    _, _raw_frames = _run_siddump(sid_path, duration=dump_duration)
                except Exception:
                    pass

            # Track which instruments have already been replaced via wave table
            replaced_insts = set()

            # Step 3a: For voices with EXACTLY ONE drum instrument,
            # replace the wave table with extracted absolute_note steps.
            #
            # Build a map: instrument_index → best pattern (highest count)
            # across all eligible single-drum voices.
            inst_best_pattern = {}  # ii → DrumPattern
            for vi, drum_inst_set in voice_drum_insts.items():
                if len(drum_inst_set) != 1:
                    continue  # multiple drum insts on this voice — handled in 3b

                patterns = drum_seqs.get(vi, [])
                if not patterns:
                    continue

                best = max(patterns, key=lambda p: p.count)
                if best.count < 2:
                    continue  # not consistent enough — skip

                ii = next(iter(drum_inst_set))
                if ii >= len(result.instruments):
                    continue

                # Skip drum+arpeggio combos: their post-noise frequency is
                # note-relative, so absolute_note steps would be wrong.
                if result.instruments[ii].has_arpeggio:
                    continue

                # Keep best pattern across all voices for this instrument
                prev = inst_best_pattern.get(ii)
                if prev is None or best.count > prev.count:
                    inst_best_pattern[ii] = best

            # Apply wave table replacement for qualifying instruments
            for ii, best in inst_best_pattern.items():
                if ii >= len(song.instruments):
                    continue

                # Build the new wave table from extracted steps
                new_wave_table = []
                for step_dict in best.wave_table_steps:
                    if step_dict.get('is_loop'):
                        new_wave_table.append(WaveTableStep(
                            is_loop=True,
                            loop_target=step_dict['loop_target'],
                        ))
                    elif step_dict.get('keep_freq'):
                        new_wave_table.append(WaveTableStep(
                            waveform=step_dict['waveform'],
                            keep_freq=True,
                        ))
                    else:
                        new_wave_table.append(WaveTableStep(
                            waveform=step_dict['waveform'],
                            absolute_note=step_dict['absolute_note'],
                        ))

                song.instruments[ii].wave_table = new_wave_table
                replaced_insts.add(ii)

            # Step 3b: For voices with MULTIPLE drum instruments, correlate
            # each instrument to its extracted sequence via note-trigger timing.
            #
            # Method: build the note trigger timeline for the voice (from
            # decompiled patterns), then for each note trigger, find the
            # nearest drum hit within a ±WINDOW frame window. Vote for which
            # canonical sequence is associated with which instrument. The
            # instrument gets the most-voted canonical's extracted DrumPattern.
            #
            # The window (CORR_WINDOW=5) is tight enough to avoid capturing
            # secondary hits from another drum instrument's noise tail, while
            # wide enough to account for Hubbard player latency (2-4 frames).
            CORR_WINDOW = 5

            for vi, drum_inst_set in voice_drum_insts.items():
                if len(drum_inst_set) <= 1:
                    continue  # single-drum voices handled above

                patterns = drum_seqs.get(vi, [])
                if not patterns or _raw_frames is None or _VOICE_OFFSETS is None:
                    continue

                # Extract all drum hit frames for this voice from raw siddump data
                off = _VOICE_OFFSETS[vi]
                raw_hits = []
                for i in range(1, len(_raw_frames)):
                    if _is_noise_onset(_raw_frames[i-1][off['ctrl']],
                                       _raw_frames[i][off['ctrl']]):
                        seq = _extract_sequence(_raw_frames, i, vi, 12)
                        if len(seq) >= 2:
                            raw_hits.append((i, seq))

                if not raw_hits:
                    continue

                # Build note trigger timeline for this voice
                track = rh_song.tracks[vi]
                pat_by_idx = {pat.index: pat for pat in result.patterns}
                tempo_frames = hubbard_speed + 1  # frames per Hubbard tick
                global_frame = 0
                note_triggers = []  # (frame, instrument_index)

                for kind, pidx in track:
                    if kind == 'pattern':
                        pat = pat_by_idx.get(pidx)
                        if not pat:
                            continue
                        cur_instr = None
                        for note in pat.notes:
                            if note.instrument is not None:
                                cur_instr = note.instrument
                            dur = (note.duration + 1) * tempo_frames
                            if not note.tie and cur_instr is not None:
                                if cur_instr in drum_inst_set:
                                    note_triggers.append((global_frame, cur_instr))
                            global_frame += dur
                    elif kind in ('loop', 'stop'):
                        break

                if not note_triggers:
                    continue

                # For each note trigger, find nearest drum hit within ±CORR_WINDOW
                # and vote for which canonical sequence belongs to this instrument.
                inst_canon_votes = _defaultdict(_Counter)  # inst → {canon: count}

                for note_frame, instr in note_triggers:
                    if note_frame >= len(_raw_frames):
                        continue
                    best_hit = None
                    best_dist = CORR_WINDOW + 1
                    for hf, seq in raw_hits:
                        dist = abs(hf - note_frame)
                        if dist < best_dist:
                            best_dist = dist
                            best_hit = (hf, seq)
                    if best_hit is not None:
                        canon = _canonicalize_sequence(best_hit[1])
                        inst_canon_votes[instr][canon] += 1

                # Build a canonical → DrumPattern lookup from extracted patterns
                # (match by comparing canonical forms of each pattern's sequence)
                canon_to_pattern = {}
                for pat in patterns:
                    pat_canon = _canonicalize_sequence(pat.sequence)
                    # Only store if not already mapped (keep highest count)
                    if pat_canon not in canon_to_pattern or pat.count > canon_to_pattern[pat_canon].count:
                        canon_to_pattern[pat_canon] = pat

                # Assign each drum instrument to its best-matching DrumPattern
                for instr_ii, votes in inst_canon_votes.items():
                    if instr_ii in replaced_insts:
                        continue
                    if instr_ii >= len(result.instruments):
                        continue
                    if result.instruments[instr_ii].has_arpeggio:
                        continue  # skip arpeggio combos

                    # Most-voted canonical for this instrument
                    if not votes:
                        continue
                    best_canon, best_vote_count = votes.most_common(1)[0]
                    if best_vote_count < 1:
                        continue

                    matched_pattern = canon_to_pattern.get(best_canon)
                    if matched_pattern is None:
                        continue

                    if matched_pattern.count < 2:
                        continue  # not consistent enough

                    # Build the wave table from matched pattern steps
                    new_wave_table = []
                    for step_dict in matched_pattern.wave_table_steps:
                        if step_dict.get('is_loop'):
                            new_wave_table.append(WaveTableStep(
                                is_loop=True,
                                loop_target=step_dict['loop_target'],
                            ))
                        elif step_dict.get('keep_freq'):
                            new_wave_table.append(WaveTableStep(
                                waveform=step_dict['waveform'],
                                keep_freq=True,
                            ))
                        else:
                            new_wave_table.append(WaveTableStep(
                                waveform=step_dict['waveform'],
                                absolute_note=step_dict['absolute_note'],
                            ))

                    if ii < len(song.instruments):
                        song.instruments[instr_ii].wave_table = new_wave_table
                        replaced_insts.add(instr_ii)

            # Step 3c: For all voices with drum instruments that were NOT already
            # replaced by wave table in steps 3a/3b, fall back to freq_slide heuristic.
            # This covers: voices where correlation failed, and single-instrument voices
            # where the instrument was skipped (e.g. has_arpeggio=True).
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
                        frames_count = len(fhi_values) - 1
                        slide = max(1, min(15, total_drop // frames_count))
                        # Apply freq_slide to drum instruments on this voice
                        # that were not already replaced via wave table
                        for ii in drum_inst_set:
                            if ii in replaced_insts:
                                continue
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
    # The Hubbard vibrato_depth byte encodes two fields:
    #   bits 0-2: shift count applied to the semitone gap delta (fine control)
    #             0 = full gap, 1 = half gap, 2 = quarter gap, etc.
    #   bits 3-5: oscillation counter_max (controls period and amplitude)
    #             amplitude = (counter_max >> 1) * delta
    #
    # Verified from Thrust.sid (depth=48=0x30 playing note 69/A5):
    #   bits 0-2 = 0 → shift=0 → delta = 842 (full downward semitone gap at A5)
    #   bits 3-5 = 6 → counter_max=6 → amplitude = 3*842 = 2526 ≈ ±10 freq_hi ✓
    #
    # V2 speed table mapping:
    #   left byte = 0x80 | counter_max  (bit 7 = calculated speed mode)
    #   right byte = shift count
    #
    # Note: V2 uses upward gap (freq[note+1]-freq[note]) while Hubbard uses
    # downward gap (freq[note]-freq[note-1]). These differ by ~6% but are
    # close enough for accurate reproduction.
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

                # Decode the two fields from the Hubbard depth byte:
                #   bits 0-2 = shift count (right-shift applied to semitone gap)
                #   bits 3-5 = counter_max (oscillation period/amplitude control)
                shift = raw & 0x07           # bits 0-2
                counter_max = (raw & 0x38) >> 3  # bits 3-5

                # If counter_max is 0, there's no oscillation — default to 6
                # (avoids zero-amplitude vibrato for unusual depth values)
                if counter_max == 0:
                    counter_max = 6

                # V2 player: left byte bits 0-6 = oscillation threshold (counter_max)
                # with bit 7 set to enable calculated speed mode
                speed = 0x80 | counter_max
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

    # Attach binary + freq table info to patterns for freq-trick resolution.
    # Also populate song.freq_lo / song.freq_hi when a truly custom interleaved
    # freq table was detected (deviation from PAL > 5%).
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
        # For freq-trick resolution: find the interleaved freq table using an
        # ascending 16-bit pair scan starting in the C0-octave range (0x0100-0x0200).
        # Hubbard songs use slightly different tuning (0x0115-0x0117 for pitch 0),
        # so we do a generic scan rather than matching a fixed byte pattern.
        # Safety: pitch>=96 reads are only resolved when the frequency is non-zero
        # (zero means we're past the end of the actual table — emit TIE instead).
        #
        # Previous approach used PAL_INTERLEAVED = [0x17, 0x01, 0x27, 0x01] which
        # never matched any Hubbard song (they use 0x16, 0x01 or 0x15, 0x01).
        _ft_addr = None
        best_pos = -1
        best_len = 0
        for _i in range(len(_binary) - 8):
            _v = _binary[_i] | (_binary[_i + 1] << 8)
            if 0x0100 <= _v <= 0x0200:
                _run = 1
                _j = _i + 2
                while _j + 1 < len(_binary):
                    _vn = _binary[_j] | (_binary[_j + 1] << 8)
                    if _v > 0 and 1.03 < _vn / _v < 1.15:
                        _run += 1
                        _v = _vn
                        _j += 2
                    else:
                        break
                if _run > best_len:
                    best_len = _run
                    best_pos = _i
        if best_len >= 12 and best_pos >= 0:
            _ft_addr = _la + best_pos
        elif result.freq_table_addr and not getattr(result, 'freq_table_interleaved', False):
            # Separated-format table (non-interleaved): safe to use for freq-trick resolution
            _ft_addr = result.freq_table_addr
    except Exception:
        pass

    # Populate custom freq table when a genuinely non-PAL interleaved table was detected.
    if getattr(result, 'freq_table_interleaved', False) and result.freq_table_addr and _binary is not None:
        off = result.freq_table_addr - _load_addr
        lo_bytes = []
        hi_bytes = []
        for n in range(96):
            b = off + n * 2
            if b + 1 < len(_binary):
                lo_bytes.append(_binary[b])
                hi_bytes.append(_binary[b + 1])
            else:
                from gt_parser import FREQ_TBL_LO, FREQ_TBL_HI
                lo_bytes.append(FREQ_TBL_LO[n])
                hi_bytes.append(FREQ_TBL_HI[n])
        song.freq_lo = bytes(lo_bytes)
        song.freq_hi = bytes(hi_bytes)

    pat_map = {}  # rh_pattern_index → usf_pattern_id
    for rh_pat in result.patterns:
        if _binary is not None and _ft_addr is not None:
            rh_pat._freq_table_info = (_binary, _load_addr, _ft_addr)
        else:
            rh_pat._freq_table_info = None
        usf_id = len(song.patterns)
        pat_map[rh_pat.index] = usf_id
        usf_pat = _map_pattern(rh_pat, usf_id, tempo_div)
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
    # Per-voice first frame where INIT writes a waveform (ctrl & 0xF0 != 0).
    # Used to measure the init timing delay and compensate via first-note duration.
    _orig_voice_first_gate = [None, None, None]
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
            _ctrl_cols = [4, 11, 18]  # column indices for V1/V2/V3 ctrl bytes
            for _frame_off in range(1, 11):
                _fi = _hdr_idx + 1 + _frame_off
                if _fi >= len(_sd_lines):
                    break
                _row = _sd_lines[_fi].split(',')
                if len(_row) < 19:
                    continue
                _fhi = [int(_row[1], 16), int(_row[8], 16), int(_row[15], 16)]
                _ctrl = [int(_row[_ctrl_cols[vi]], 16) for vi in range(3)]
                # Check if at least one voice has a real waveform (INIT done)
                if any(c & 0xF0 for c in _ctrl):
                    _orig_init_fhi = _fhi
                    _orig_init_ctrl = _ctrl
                    break
            # Now record per-voice first gate frame (scan up to 20 frames).
            # This tells us when the original Hubbard INIT pre-loaded each voice.
            # Note: frame_off=0 corresponds to siddump row hdr_idx+1 (the very
            # first data row, i.e. "Frame 1" in 1-indexed output).
            for _frame_off in range(0, 21):
                _fi = _hdr_idx + 1 + _frame_off
                if _fi >= len(_sd_lines):
                    break
                _row = _sd_lines[_fi].split(',')
                if len(_row) < 19:
                    continue
                for vi in range(3):
                    if _orig_voice_first_gate[vi] is None:
                        _c = int(_row[_ctrl_cols[vi]], 16)
                        # Require BOTH waveform bits (upper nibble) AND gate bit (bit 0).
                        # Hubbard INIT pre-sets waveform bits (ctrl & 0xF0) without gate
                        # to prime the oscillator. We want the frame where the first real
                        # note starts (gate opened with a waveform active).
                        if (_c & 0xF0) and (_c & 0x01):  # waveform bit + gate bit both set
                            _orig_voice_first_gate[vi] = _frame_off
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
        # Check first pattern is all-TIE
        if not _pat_all_tie(_pat_id_by_id.get(orderlist[0][0])):
            continue
        # Guard: only fix if original INIT pre-loaded a waveform AND non-zero freq.
        # If orig ctrl has no waveform bits or freq=0, our TIE (freq=0) already matches.
        orig_fhi = _orig_init_fhi[voice_idx]
        orig_ctrl = _orig_init_ctrl[voice_idx]
        if (orig_ctrl & 0xF0) == 0 or orig_fhi == 0:
            continue  # Original had no waveform or zero freq -- TIE is correct
        # Count leading TIE-only patterns
        leading = 0
        for pid, _ in orderlist:
            if _pat_all_tie(_pat_id_by_id.get(pid)):
                leading += 1
            else:
                break
        # Find first real note after the TIE prefix
        init_note = None
        init_instr = -1
        for pid, _ in orderlist[leading:]:
            found = _first_note(_pat_id_by_id.get(pid))
            if found:
                init_note, init_instr = found
                break
        if init_note is None:
            continue
        # Build a 1-tick init pattern with the found note
        init_pid = len(song.patterns)
        init_pat = Pattern(id=init_pid, events=[
            NoteEvent(type='note', note=init_note, duration=1, instrument=init_instr)
        ])
        song.patterns.append(init_pat)
        _pat_id_by_id[init_pid] = init_pat
        # Prepend to orderlist; shift restart index to skip the init pattern on loops
        song.orderlists[voice_idx] = [(init_pid, 0)] + list(orderlist)
        song.orderlist_restart[voice_idx] += 1

    # Init timing compensation: the V2 player emits its first register write at
    # siddump frame_off = (1 + tempo), measured empirically:
    #   frame_off=0 → siddump row hdr+1 = "Frame 1" (1-indexed printout)
    #   Game_Killer: tempo=2, rebuilt fires at "Frame 4" = frame_off=3 = 1+tempo ✓
    #   Human_Race:  tempo=4, rebuilt fires at "Frame 6" = frame_off=5 = 1+tempo ✓
    #   Monty:       tempo=2, rebuilt fires at "Frame 4" = frame_off=3 = 1+tempo ✓
    #   Commando:    tempo=3, rebuilt fires at "Frame 5" = frame_off=4 = 1+tempo ✓
    #
    # The Hubbard INIT routine pre-loads registers so the original SID fires at
    # frame_off 0-1 (Frame 1-2). The gap (rebuilt_frame_off - orig_frame_off) is
    # the init delay in frames. We compensate by reducing the first note's duration
    # so that the V2 player finishes it (and starts the NEXT note) at the right time.
    #
    # The first note's duration in frames = duration × tempo. Reducing it by
    # delay_ticks = ceil(delay_frames / tempo) means the first note finishes
    # delay_frames sooner, aligning all subsequent notes to the original.
    #
    # Guard: only reduce if delay > 0 and orig first gate is known.
    # Clamp: first note duration must remain >= 1.
    _rebuilt_base_frame = 1 + song.tempo  # frame_off when V2 player fires first note
    for voice_idx in range(3):
        orig_gate = _orig_voice_first_gate[voice_idx]
        if orig_gate is None:
            continue  # can't measure — skip
        delay_frames = _rebuilt_base_frame - orig_gate
        if delay_frames <= 0:
            continue  # no delay or rebuilt fires earlier (shouldn't happen)
        delay_ticks = (delay_frames + song.tempo - 1) // song.tempo  # ceil divide

        # Find the first note event in the voice's current orderlist
        orderlist = song.orderlists[voice_idx]
        found_first_note = False
        for pid, _ in orderlist:
            pat = _pat_id_by_id.get(pid)
            if pat is None:
                continue
            for evt in pat.events:
                if evt.type == 'note':
                    # Reduce duration, clamp to minimum 1
                    old_dur = evt.duration
                    evt.duration = max(1, old_dur - delay_ticks)
                    found_first_note = True
                    break
            if found_first_note:
                break

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
