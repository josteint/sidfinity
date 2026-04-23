"""
effect_to_usf.py — Convert detected effects to structured USF.

Takes output from effect_detect.analyze_effects() and produces a USF Song
that can be fed to usf_to_sid() for SID generation.

Pipeline position:
    ground_truth.py → effect_detect.py → effect_to_usf.py → usf_to_sid.py → SID

Usage:
    from ground_truth import capture_sid
    from effect_detect import analyze_effects
    from effect_to_usf import effects_to_usf
    from converters.usf_to_sid import usf_to_sid

    trace = capture_sid('song.sid', subtunes=[1]).subtunes[0]
    analysis = analyze_effects(trace)
    song = effects_to_usf(analysis, trace)
    usf_to_sid(song, 'output.sid')
"""

import os
import sys
import struct
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from usf.format import (Song, Instrument, Pattern, NoteEvent, WaveTableStep,
                         PulseTableStep, FilterTableStep, SpeedTableEntry,
                         CMD_VIBRATO, CMD_PORTA_UP, CMD_PORTA_DOWN,
                         CMD_TONE_PORTA, CMD_SET_FILTCTL, CMD_SET_FILTCUT,
                         CMD_SET_MASTERVOL, CMD_SET_TEMPO)


def _fingerprint_note(note_data):
    """Extract instrument fingerprint from a note's effect list."""
    effects = {e.effect: e for e in note_data['effects']}

    ad = effects['adsr'].params['ad'] if 'adsr' in effects else 0
    sr = effects['adsr'].params['sr'] if 'adsr' in effects else 0

    wave = effects.get('waveform')
    wave_byte = wave.params['waveform_byte'] if wave else 0x40

    # Wave signature (arpeggio, drum, waveform sequence, or plain)
    arp = effects.get('arpeggio')
    wseq = effects.get('waveform_sequence')
    drum = effects.get('drum_freq_slide')

    if drum:
        wave_sig = ('drum',)
    elif arp:
        wave_sig = ('arp', tuple(sorted(arp.params['intervals'])))
    elif wseq and len(wseq.params['unique_waveforms']) >= 2:
        wave_sig = ('wseq', tuple(wseq.params['unique_waveforms']))
    else:
        wave_sig = ('plain',)

    # Pulse signature
    pwm_d = effects.get('pwm_direct')
    pwm_s = effects.get('pwm_sweep')
    if pwm_d:
        pulse_sig = ('pwm', pwm_d.params['speed'])
    elif pwm_s:
        pulse_sig = ('pwm_sweep', pwm_s.params['speed'])
    else:
        pulse_sig = ('no_pwm',)

    return (ad, sr, wave_byte, wave_sig, pulse_sig)


def _wave_name(byte):
    """Convert waveform byte to name string."""
    names = {0x10: 'tri', 0x20: 'saw', 0x40: 'pulse', 0x80: 'noise',
             0x50: 'tri_pulse', 0x60: 'saw_pulse'}
    return names.get(byte & 0xF0, 'pulse')


def _build_wave_table(fingerprint, note_data):
    """Build wave table steps from instrument fingerprint and note effects."""
    ad, sr, wave_byte, wave_sig, pulse_sig = fingerprint
    effects = {e.effect: e for e in note_data['effects']}

    steps = []
    kind = wave_sig[0]

    if kind == 'drum':
        # Drum: noise burst then silence
        drum_det = effects['drum_freq_slide']
        steps.append(WaveTableStep(waveform=0x81, note_offset=0,
                                   freq_slide=-1))
        steps.append(WaveTableStep(is_loop=True, loop_target=0))

    elif kind == 'arp':
        arp = effects['arpeggio']
        intervals = sorted(arp.params['intervals'])
        # Arpeggio: alternate between base (offset=0) and base+interval
        wseq = effects.get('waveform_sequence')
        if wseq:
            # Use the actual waveform sequence for the first frames
            wave_list = [int(w.replace('$', '0x'), 16) for w in wseq.params['sequence']]
            # First frame: gate on
            steps.append(WaveTableStep(waveform=wave_list[0] | 0x01, note_offset=0))
            # Second frame: might be different waveform + arpeggio
            if len(intervals) == 1:
                steps.append(WaveTableStep(waveform=wave_list[1] if len(wave_list) > 1 else wave_byte,
                                           note_offset=intervals[0]))
                # Sustain: alternate between base and arp
                steps.append(WaveTableStep(waveform=wave_byte, note_offset=0))
                steps.append(WaveTableStep(waveform=wave_byte, note_offset=intervals[0]))
                steps.append(WaveTableStep(is_loop=True, loop_target=2))
            else:
                # Multi-interval arpeggio
                for intv in intervals:
                    steps.append(WaveTableStep(waveform=wave_byte, note_offset=intv))
                steps.append(WaveTableStep(waveform=wave_byte, note_offset=0))
                steps.append(WaveTableStep(is_loop=True, loop_target=1))
        else:
            # Simple arpeggio without waveform sequence
            steps.append(WaveTableStep(waveform=wave_byte | 0x01, note_offset=0))
            for intv in intervals:
                steps.append(WaveTableStep(waveform=wave_byte, note_offset=intv))
            steps.append(WaveTableStep(is_loop=True, loop_target=0))

    elif kind == 'wseq':
        # Waveform sequence without arpeggio
        wave_strs = wave_sig[1]
        for i, ws in enumerate(wave_strs):
            wb = int(ws.replace('$', '0x'), 16)
            if i == 0:
                wb |= 0x01  # gate on
            steps.append(WaveTableStep(waveform=wb, note_offset=0))
        # Loop to the last (sustain) waveform
        steps.append(WaveTableStep(is_loop=True, loop_target=len(wave_strs) - 1))

    else:
        # Plain: just the waveform
        steps.append(WaveTableStep(waveform=wave_byte | 0x01, note_offset=0))
        steps.append(WaveTableStep(waveform=wave_byte, note_offset=0))
        steps.append(WaveTableStep(is_loop=True, loop_target=1))

    return steps


def _build_pulse_table(fingerprint, note_data):
    """Build pulse table steps from detected PWM effect."""
    _, _, _, _, pulse_sig = fingerprint
    effects = {e.effect: e for e in note_data['effects']}

    if pulse_sig[0] == 'no_pwm':
        return []

    if pulse_sig[0] == 'pwm':
        pwm = effects['pwm_direct']
        speed = pwm.params['speed']
        return [
            PulseTableStep(is_set=False, value=speed, duration=127),
            PulseTableStep(is_loop=True, loop_target=0),
        ]

    if pulse_sig[0] == 'pwm_sweep':
        pwm = effects['pwm_sweep']
        speed = pwm.params['speed']
        return [
            PulseTableStep(is_set=False, value=speed, duration=127),
            PulseTableStep(is_set=False, value=-speed, duration=127),
            PulseTableStep(is_loop=True, loop_target=0),
        ]

    return []


def _get_gate_timer(notes_for_instrument):
    """Determine gate timer from hard restart detections across all notes of an instrument."""
    gaps = []
    for nd in notes_for_instrument:
        effects = {e.effect: e for e in nd['effects']}
        hr = effects.get('hard_restart')
        if hr:
            gaps.append(hr.params['gap_frames'])

    if not gaps:
        return 2, 'gate'

    counter = Counter(gaps)
    most_common_gap = counter.most_common(1)[0][0]

    # Determine method from any note
    methods = []
    for nd in notes_for_instrument:
        effects = {e.effect: e for e in nd['effects']}
        hr = effects.get('hard_restart')
        if hr:
            methods.append(hr.params['method'])

    method = Counter(methods).most_common(1)[0][0] if methods else 'gate'
    return min(most_common_gap, 63), method


def _get_pulse_width(notes_for_instrument):
    """Get initial pulse width from the first note of an instrument."""
    for nd in notes_for_instrument:
        effects = {e.effect: e for e in nd['effects']}
        pwm = effects.get('pwm_direct') or effects.get('pwm_sweep')
        if pwm and 'initial_pw' in pwm.params:
            return pwm.params['initial_pw']
    return 0x0800  # default


def _get_note_value(note_data):
    """Extract the note index from a note's effects."""
    effects = {e.effect: e for e in note_data['effects']}
    note_det = effects.get('note')
    if note_det:
        return note_det.params['note']
    return 0


def _discover_patterns(voice_events, min_pattern_len=4):
    """Find repeated note sequences in a voice's event list.

    Returns (patterns, orderlist) where:
      patterns: list of Pattern objects
      orderlist: list of (pattern_id, transpose) tuples
    """
    if not voice_events:
        return [], []

    # Convert events to hashable tuples: (note, instrument_id, duration)
    event_keys = [(e.note, e.instrument, e.duration) for e in voice_events]
    n = len(event_keys)

    # Try window sizes from large to small
    best_patterns = None
    best_orderlist = None
    best_score = n  # worst case: one note per pattern

    for window in range(n // 2, min_pattern_len - 1, -1):
        if n % window != 0:
            continue

        # Check if all windows match the first
        blocks = [event_keys[i:i + window] for i in range(0, n, window)]
        if all(b == blocks[0] for b in blocks):
            pat = Pattern(id=0, events=voice_events[:window])
            orderlist = [(0, 0)] * len(blocks)
            score = window  # fewer unique notes = better
            if score < best_score:
                best_patterns = [pat]
                best_orderlist = orderlist
                best_score = score
            break

    if best_patterns is None:
        # No repeating pattern found — use one big pattern
        best_patterns = [Pattern(id=0, events=voice_events)]
        best_orderlist = [(0, 0)]

    return best_patterns, best_orderlist


def effects_to_usf(analysis, trace=None, sid_path=None):
    """Convert effect analysis to USF Song.

    Args:
        analysis: output of analyze_effects()
        trace: optional SubtuneTrace for supplementary data
        sid_path: optional, for PSID metadata

    Returns: Song object ready for usf_to_sid()
    """
    song = Song()
    song.nowavedelay = True

    # Metadata from PSID header
    if sid_path and os.path.exists(sid_path):
        with open(sid_path, 'rb') as f:
            data = f.read()
        if len(data) > 0x36:
            song.title = data[0x16:0x36].decode('ascii', errors='ignore').rstrip('\x00').strip()
            song.author = data[0x36:0x56].decode('ascii', errors='ignore').rstrip('\x00').strip()

    # Tempo
    tempo_det = analysis.get('tempo')
    if tempo_det and tempo_det.params['frames_per_tick'] > 0:
        song.tempo = tempo_det.params['frames_per_tick']
    else:
        song.tempo = 6

    # --- Step 1: Fingerprint all notes, build instrument map ---
    fp_to_id = {}  # fingerprint → instrument_id
    fp_to_notes = {}  # fingerprint → list of note_data (for gate timer consensus)
    all_note_fps = []  # (voice, note_idx, fingerprint) for each note

    for v in range(3):
        voice_data = analysis['voices'][v]
        for ni, nd in enumerate(voice_data['notes']):
            fp = _fingerprint_note(nd)
            if fp not in fp_to_id:
                fp_to_id[fp] = len(fp_to_id) + 1  # 1-indexed
                fp_to_notes[fp] = []
            fp_to_notes[fp].append(nd)
            all_note_fps.append((v, ni, fp))

    # --- Step 2: Build Instrument objects ---
    instruments = []
    shared_pulse_table = []
    pulse_ptr_map = {}  # fingerprint pulse_sig → pulse_ptr

    for fp, inst_id in sorted(fp_to_id.items(), key=lambda x: x[1]):
        ad, sr, wave_byte, wave_sig, pulse_sig = fp
        notes = fp_to_notes[fp]

        # Wave table from first note with this fingerprint
        wave_steps = _build_wave_table(fp, notes[0])

        # Pulse table
        pulse_steps = _build_pulse_table(fp, notes[0])
        pulse_ptr = 0
        if pulse_steps:
            if pulse_sig not in pulse_ptr_map:
                pulse_ptr_map[pulse_sig] = len(shared_pulse_table) + 1  # 1-indexed
                for ps in pulse_steps:
                    if ps.is_loop:
                        shared_pulse_table.append((0xFF, ps.loop_target))
                    elif ps.is_set:
                        shared_pulse_table.append((0x80 | ps.value, ps.low_byte))
                    else:
                        # value is signed speed, duration
                        speed = ps.value & 0xFF
                        shared_pulse_table.append((min(ps.duration, 0x7F), speed))
            pulse_ptr = pulse_ptr_map[pulse_sig]

        # Gate timer
        gate_timer, hr_method = _get_gate_timer(notes)

        # Pulse width
        pw = _get_pulse_width(notes)

        # First wave (transient)
        first_wave = -1
        wseq = None
        for e in notes[0]['effects']:
            if e.effect == 'waveform_sequence':
                wseq = e
                break
        if wseq and len(wseq.params['unique_waveforms']) >= 2:
            first_w = int(wseq.params['unique_waveforms'][0].replace('$', '0x'), 16)
            if first_w != wave_byte:
                first_wave = first_w

        inst = Instrument(
            id=inst_id,
            ad=ad,
            sr=sr,
            waveform=_wave_name(wave_byte),
            first_wave=first_wave,
            gate_timer=gate_timer,
            hr_method=hr_method,
            wave_table=wave_steps,
            pulse_width=pw,
            pulse_ptr=pulse_ptr,
        )
        instruments.append(inst)

    song.instruments = instruments
    song.shared_pulse_table = shared_pulse_table

    # --- Step 3: Build note events per voice ---
    tempo = song.tempo
    voice_events_list = []

    for v in range(3):
        voice_data = analysis['voices'][v]
        events = []
        for ni, nd in enumerate(voice_data['notes']):
            fp = _fingerprint_note(nd)
            inst_id = fp_to_id[fp]
            note_val = _get_note_value(nd)

            # For arpeggio, use the lowest note as the base
            effects = {e.effect: e for e in nd['effects']}
            arp = effects.get('arpeggio')
            if arp:
                note_val = min(arp.params['notes'])

            # Quantize duration to ticks
            dur_frames = nd['length']
            dur_ticks = max(1, round(dur_frames / tempo))

            events.append(NoteEvent(
                type='note',
                note=min(note_val, 95),  # clamp to valid range
                duration=dur_ticks,
                instrument=inst_id,
            ))

        voice_events_list.append(events)

    # --- Step 4: Pattern discovery ---
    song.patterns = []
    song.orderlists = [[], [], []]
    song.orderlist_restart = [0, 0, 0]

    global_pat_id = 0
    for v in range(3):
        patterns, orderlist = _discover_patterns(voice_events_list[v])

        # Renumber pattern IDs globally
        for pat in patterns:
            pat.id = global_pat_id
            song.patterns.append(pat)
            # Update orderlist references
            orderlist = [(global_pat_id if pid == pat.id - global_pat_id + patterns[0].id else pid, tr)
                         for pid, tr in orderlist]
            global_pat_id += 1

        # Fix: simple renumbering
        pat_id_offset = global_pat_id - len(patterns)
        song.orderlists[v] = [(pat_id_offset + pid, tr) for pid, tr in orderlist]
        song.orderlist_restart[v] = 0

    # --- Step 5: Filter setup ---
    filter_det = analysis.get('filter')
    if filter_det and filter_det.params.get('filter_type', 0) > 0:
        # Add filter setup as command on first note of voice 0
        if song.patterns and song.patterns[0].events:
            first_event = song.patterns[0].events[0]
            ftype = filter_det.params['filter_type']
            res = filter_det.params['resonance']
            routing = (int(filter_det.params.get('voice1', False)) |
                       (int(filter_det.params.get('voice2', False)) << 1) |
                       (int(filter_det.params.get('voice3', False)) << 2))
            first_event.command = CMD_SET_FILTCTL
            first_event.command_val = (res << 4) | routing

    # --- Step 6: Loop point ---
    if trace and trace.loop_frame is not None:
        # Set orderlist restart to loop back
        # For now, just loop the whole song
        for v in range(3):
            song.orderlist_restart[v] = 0

    return song


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 effect_to_usf.py <file.sid> [subtune] [output.sid]")
        sys.exit(1)

    from ground_truth import capture_sid
    from effect_detect import analyze_effects

    sid_path = sys.argv[1]
    subtune = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    output = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Capturing ground truth for subtune {subtune}...")
    result = capture_sid(sid_path, subtunes=[subtune], max_frames=1500)
    trace = result.subtunes[0]

    print(f"Analyzing effects ({trace.n_frames} frames)...")
    analysis = analyze_effects(trace)

    print(f"Converting to USF...")
    song = effects_to_usf(analysis, trace, sid_path)

    print(f"\nUSF Song:")
    print(f"  Tempo: {song.tempo}")
    print(f"  Instruments: {len(song.instruments)}")
    print(f"  Patterns: {len(song.patterns)}")
    for v in range(3):
        ol = song.orderlists[v]
        n_events = sum(len(p.events) for p in song.patterns
                       if any(pid == p.id for pid, _ in ol))
        print(f"  V{v + 1}: {len(ol)} orderlist entries, {n_events} events")
    print(f"  Pulse table: {len(song.shared_pulse_table)} entries")

    if output:
        from converters.usf_to_sid import usf_to_sid
        print(f"\nBuilding SID: {output}")
        os.environ['PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          '..', 'tools', 'xa65', 'xa') + ':' + os.environ.get('PATH', '')
        usf_to_sid(song, output)

        import subprocess
        sz = os.path.getsize(output)
        print(f"  Output: {sz} bytes ({sz / 1024:.1f} KB)")

        # Quick compare if source path provided
        try:
            from sid_compare import compare_sids_tolerant
            comp = compare_sids_tolerant(sid_path, output, 10)
            print(f"  Grade: {comp['grade']} Score: {comp['score']:.1f}%")
        except Exception as e:
            print(f"  Compare failed: {e}")
