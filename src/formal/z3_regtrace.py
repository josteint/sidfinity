"""
z3_regtrace.py — Z3-enhanced register trace to USF converter.

Uses the Z3 inverse solver for note extraction and instrument identification,
replacing the heuristic approach in regtrace_to_usf.py. Falls back to
heuristics where Z3 is too slow or can't find a solution.

This is the test of whether "math beats heuristics" for SID decompilation.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from converters.regtrace_to_usf import (
    run_siddump, extract_voice_events, detect_tempo_from_frames,
    detect_tempo, collapse_arpeggios, build_instruments,
    quantize_events, events_to_pattern, freq_hi_to_note,
    VOICE_OFFSETS, IDX_FREQ_HI, IDX_CTRL, IDX_AD, IDX_SR,
    IDX_PW_HI, IDX_PW_LO, GATE_BIT, WAVEFORM_MASK,
)
from formal.inverse_solver import (
    solve_freq_note, solve_waveform, solve_adsr,
)
from usf.format import (
    Song, Instrument, Pattern, NoteEvent, WaveTableStep,
    PulseTableStep, SpeedTableEntry, note_name,
)


def z3_extract_voice_events(frames, voice_idx, tempo=6):
    """Extract note events using Z3 for note identification.

    Strategy: use the heuristic to find note BOUNDARIES (gate transitions),
    then use Z3 to identify the NOTES within each boundary.
    """
    # Step 1: Use heuristic boundary detection (it's good at this)
    events = extract_voice_events(frames, voice_idx, tempo=tempo)
    events = collapse_arpeggios(events, tempo)

    # Step 2: For each note event, use Z3 to verify/improve the note
    off = VOICE_OFFSETS[voice_idx]
    for ev in events:
        if ev['type'] != 'note' or ev['duration'] < 2:
            continue

        start = ev['frame']
        end = min(start + ev['duration'], len(frames))
        if end - start < 2:
            continue

        # Extract freq_hi values for this note
        seg_fhi = [frames[i][off + IDX_FREQ_HI] for i in range(start, end)]

        # Skip if all zeros
        if all(f == 0 for f in seg_fhi):
            continue

        # Z3 solve for the base note
        try:
            result = solve_freq_note(seg_fhi[:16])  # limit to 16 frames for speed
            if result['status'] in ('exact', 'approximate'):
                z3_note = result['note']
                # Only override if Z3 is more confident
                if result['error'] == 0 and z3_note != ev['note']:
                    ev['note'] = z3_note
        except Exception:
            pass  # fall back to heuristic note

    return events


def z3_build_instruments(all_voice_events, frames=None):
    """Build instruments with Z3-enhanced ADSR detection.

    Uses the heuristic for instrument grouping, then Z3 for
    precise AD/SR/gate_timer extraction.
    """
    # Use heuristic instrument builder (handles wave tables, pulse, etc.)
    instruments, inst_map, shared_pulse = build_instruments(all_voice_events, frames=frames)

    # Z3 ADSR enhancement: only override AD/SR values, keep heuristic gate_timer.
    # The heuristic gate_timer is better because it's statistical (many notes),
    # while Z3 looks at one note and can miscount HR preamble frames.
    if frames is not None:
        for inst_key, inst_id in inst_map.items():
            ad, sr, waveform = inst_key
            inst = instruments[inst_id]

            note_frames = []
            for voice_events in all_voice_events:
                for ev in voice_events:
                    if ev['type'] == 'note' and (ev['ad'], ev['sr'], ev['waveform']) == inst_key:
                        vi = ev.get('voice_idx', 0)
                        voff = VOICE_OFFSETS[vi]
                        start = ev['frame']
                        dur = min(ev['duration'], 30)
                        seg_ad = [frames[i][voff + IDX_AD] for i in range(start, min(start + dur, len(frames)))]
                        seg_sr = [frames[i][voff + IDX_SR] for i in range(start, min(start + dur, len(frames)))]
                        seg_wav = [frames[i][voff + 4] for i in range(start, min(start + dur, len(frames)))]
                        if len(seg_ad) >= 4:
                            note_frames.append((seg_ad, seg_sr, seg_wav))

            if note_frames:
                try:
                    seg_ad, seg_sr, seg_wav = note_frames[0]
                    z3_result = solve_adsr(seg_ad, seg_sr, seg_wav)
                    if z3_result['status'] in ('exact', 'approximate'):
                        inst.ad = z3_result['ad']
                        inst.sr = z3_result['sr']
                        # Keep heuristic gate_timer — don't override
                except Exception:
                    pass

    return instruments, inst_map, shared_pulse


def z3_regtrace_to_usf(sid_path, duration=60, debug=False):
    """Convert a SID file to USF using Z3-enhanced analysis.

    Same pipeline as regtrace_to_usf but uses Z3 for:
    1. Note identification (frequency → note number)
    2. ADSR extraction (AD/SR/gate_timer from register values)
    """
    metadata, frames = run_siddump(sid_path, duration)

    if debug:
        print(f"Loaded {len(frames)} frames from {sid_path}")

    # Tempo detection (heuristic is fine here)
    tempo_initial = detect_tempo_from_frames(frames, fps=int(metadata.get('fps', 50)))

    # Extract events per voice with Z3-enhanced note detection
    all_voice_events = []
    for v in range(3):
        events = z3_extract_voice_events(frames, v, tempo=tempo_initial)
        all_voice_events.append(events)
        if debug:
            note_count = sum(1 for e in events if e['type'] == 'note')
            print(f"  Voice {v+1}: {note_count} notes")

    # Refine tempo
    tempo = detect_tempo(all_voice_events, fps=int(metadata.get('fps', 50)))
    if debug:
        print(f"  Tempo: {tempo}")

    # Tag events with voice index
    for v in range(3):
        for e in all_voice_events[v]:
            e['voice_idx'] = v

    # Build instruments with Z3-enhanced ADSR
    instruments, inst_map, shared_pulse = z3_build_instruments(
        all_voice_events, frames=frames)

    if debug:
        print(f"  {len(instruments)} instruments")

    # Build song (same as regtrace_to_usf)
    song = Song(
        title=metadata.get('title', os.path.basename(sid_path)),
        author=metadata.get('author', ''),
        sid_model=metadata.get('sid_model', '6581'),
        clock=metadata.get('clock', 'PAL'),
        tempo=tempo,
        instruments=instruments,
        nowavedelay=True,
        shared_pulse_table=shared_pulse,
    )

    clock_flag = 0x04 if metadata.get('clock') == 'PAL' else 0x08
    sid_flag = 0x10 if metadata.get('sid_model') == '6581' else 0x20
    song.psid_flags = clock_flag | sid_flag

    pattern_id = 0
    for v in range(3):
        quantized = quantize_events(all_voice_events[v], tempo)
        note_events = events_to_pattern(quantized, inst_map)

        if note_events:
            pat = Pattern(id=pattern_id, events=note_events)
            song.patterns.append(pat)
            song.orderlists[v].append((pattern_id, 0))
            pattern_id += 1
        else:
            total_ticks = max(1, len(frames) // tempo)
            pat = Pattern(id=pattern_id, events=[
                NoteEvent(type='rest', duration=min(total_ticks, 32))
            ])
            song.patterns.append(pat)
            song.orderlists[v].append((pattern_id, 0))
            pattern_id += 1

    for v in range(3):
        if song.orderlists[v]:
            song.orderlists[v].append(song.orderlists[v][-1])
            song.orderlist_restart[v] = len(song.orderlists[v]) - 1

    return song


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Z3-enhanced SID to USF converter')
    parser.add_argument('sid_file', help='Path to .sid file')
    parser.add_argument('--duration', type=int, default=60)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--compare', action='store_true')
    args = parser.parse_args()

    song = z3_regtrace_to_usf(args.sid_file, args.duration, args.debug)

    if args.compare:
        from converters.usf_to_sid import usf_to_sid
        from sid_compare import compare_sids_tolerant, print_results
        usf_to_sid(song, '/tmp/z3_rebuilt.sid')
        comp = compare_sids_tolerant(args.sid_file, '/tmp/z3_rebuilt.sid',
                                      min(args.duration, 10))
        if comp:
            print_results(comp, os.path.basename(args.sid_file))
