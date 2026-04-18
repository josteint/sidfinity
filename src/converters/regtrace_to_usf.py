"""
regtrace_to_usf.py — Convert siddump register traces to USF Song format.

Universal approach: works for ANY SID player engine by analyzing the register
output rather than parsing the binary. Bypasses all binary format parsing.

Usage:
    python3 src/regtrace_to_usf.py <sid_file> [--duration 60] [--debug]

Pipeline:
    SID file → siddump → register CSV → frequency/gate/ADSR analysis → USF Song
"""

import subprocess
import sys
import os
import json
import math
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from usf.format import (Song, Instrument, Pattern, NoteEvent, WaveTableStep,
                         PulseTableStep, SpeedTableEntry, note_name)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SIDDUMP = os.path.join(SCRIPT_DIR, '..', '..', 'tools', 'siddump')

# SID register offsets per voice (0-based within the 25-column siddump output)
VOICE_OFFSETS = [0, 7, 14]
IDX_FREQ_LO = 0
IDX_FREQ_HI = 1
IDX_PW_LO = 2
IDX_PW_HI = 3
IDX_CTRL = 4
IDX_AD = 5
IDX_SR = 6
IDX_FILT_LO = 21
IDX_FILT_HI = 22
IDX_FILT_CTRL = 23
IDX_FILT_MODE_VOL = 24

GATE_BIT = 0x01
WAVEFORM_MASK = 0xF0
TEST_BIT = 0x08

# Standard C64 PAL frequency table
FREQ_LO_PAL = [
    0x17,0x27,0x39,0x4B,0x5F,0x74,0x8A,0xA1,0xBA,0xD4,0xF0,0x0E,
    0x2D,0x4E,0x71,0x96,0xBE,0xE8,0x14,0x43,0x74,0xA9,0xE1,0x1C,
    0x5A,0x9C,0xE2,0x2D,0x7C,0xCF,0x28,0x85,0xE8,0x52,0xC1,0x37,
    0xB4,0x39,0xC5,0x5A,0xF7,0x9E,0x4F,0x0A,0xD1,0xA3,0x82,0x6E,
    0x68,0x71,0x8A,0xB3,0xEE,0x3C,0x9E,0x15,0xA2,0x46,0x04,0xDC,
    0xD0,0xE2,0x14,0x67,0xDD,0x79,0x3C,0x29,0x44,0x8D,0x08,0xB8,
    0xA1,0xC5,0x28,0xCD,0xBA,0xF1,0x78,0x53,0x87,0x1A,0x10,0x71,
    0x42,0x89,0x4F,0x9B,0x74,0xE2,0xF0,0xA6,0x0E,0x33,0x20,0xFF]
FREQ_HI_PAL = [
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
    0x04,0x04,0x04,0x05,0x05,0x05,0x06,0x06,0x06,0x07,0x07,0x08,
    0x08,0x09,0x09,0x0A,0x0A,0x0B,0x0C,0x0D,0x0D,0x0E,0x0F,0x10,
    0x11,0x12,0x13,0x14,0x15,0x17,0x18,0x1A,0x1B,0x1D,0x1F,0x20,
    0x22,0x24,0x27,0x29,0x2B,0x2E,0x31,0x34,0x37,0x3A,0x3E,0x41,
    0x45,0x49,0x4E,0x52,0x57,0x5C,0x62,0x68,0x6E,0x75,0x7C,0x83,
    0x8B,0x93,0x9C,0xA5,0xAF,0xB9,0xC4,0xD0,0xDD,0xEA,0xF8,0xFF]

FREQ_TABLE_PAL = [(FREQ_HI_PAL[i] << 8) | FREQ_LO_PAL[i] for i in range(96)]


def run_siddump(sid_path, duration=60):
    """Run siddump on a SID file and return (metadata_dict, frames_list).

    Each frame is a list of 25 integers (hex register values).
    Automatically passes --force-rsid for RSID files so they are not skipped.
    """
    cmd = [SIDDUMP, sid_path, '--duration', str(duration), '--force-rsid']
    r = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=120
    )
    if r.returncode != 0:
        raise RuntimeError(f'siddump failed: {r.stderr[:200]}')

    lines = r.stdout.strip().split('\n')
    if len(lines) < 3:
        raise RuntimeError(f'siddump output too short ({len(lines)} lines)')

    metadata = json.loads(lines[0])
    frames = []
    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue
        vals = [int(v, 16) for v in line.split(',')]
        if len(vals) == 25:
            frames.append(vals)
    return metadata, frames


def freq_to_note_pal(freq16):
    """Map a 16-bit SID frequency to the nearest PAL note number (0-95).

    Returns (note_number, cents_error) or (-1, 0) if freq is 0 or unmappable.
    """
    if freq16 == 0:
        return -1, 0

    best_note = -1
    best_dist = float('inf')
    for i, f in enumerate(FREQ_TABLE_PAL):
        dist = abs(freq16 - f)
        if dist < best_dist:
            best_dist = dist
            best_note = i

    if FREQ_TABLE_PAL[best_note] > 0:
        ratio = freq16 / FREQ_TABLE_PAL[best_note]
        cents = 1200 * math.log2(ratio) if ratio > 0 else 0
    else:
        cents = 0

    return best_note, cents


def freq_hi_to_note(freq_hi):
    """Map just a freq_hi byte to the nearest note.

    This is what gt2_compare uses for note comparison — only freq_hi matters.
    Returns note number (0-95) or -1 if unmappable.
    """
    if freq_hi == 0:
        return -1

    best_note = -1
    best_dist = float('inf')
    for i, fh in enumerate(FREQ_HI_PAL):
        dist = abs(freq_hi - fh)
        if dist < best_dist:
            best_dist = dist
            best_note = i

    return best_note


def _is_hr_frame(ctrl):
    """Check if this control byte is a hard restart frame (test bit, no audible wave)."""
    waveform = ctrl & WAVEFORM_MASK
    return (ctrl & TEST_BIT) != 0 and waveform == 0


def _is_audible_wave(ctrl):
    """Check if control register has an audible waveform (not test-only, not zero)."""
    waveform = ctrl & WAVEFORM_MASK
    is_test = (ctrl & TEST_BIT) != 0 and waveform == 0
    return waveform in (0x10, 0x20, 0x40, 0x80, 0x50, 0x60, 0x30, 0x70) and not is_test


def extract_voice_events(frames, voice_idx, tempo=6, debug=False):
    """Extract note events from register frames for one voice.

    Strategy: detect note boundaries from gate transitions and frequency changes.

    First-wave handling: many SID players use a different waveform on frame 1
    (e.g. noise $80 for a click) then switch to the real waveform on frame 2.
    We detect this and record it as a first_wave property, using the SETTLED
    waveform (frame 2+) as the note's primary waveform.

    Vibrato filtering: frequency changes of +-1 semitone that return within
    the tempo window are classified as vibrato, not new notes.
    """
    off = VOICE_OFFSETS[voice_idx]

    # Phase 1: Collect per-frame state
    frame_states = []
    for frame in frames:
        freq_hi = frame[off + IDX_FREQ_HI]
        freq_lo = frame[off + IDX_FREQ_LO]
        ctrl = frame[off + IDX_CTRL]
        ad = frame[off + IDX_AD]
        sr = frame[off + IDX_SR]
        pw_hi = frame[off + IDX_PW_HI]
        pw_lo = frame[off + IDX_PW_LO]

        gate = bool(ctrl & GATE_BIT)
        waveform = ctrl & WAVEFORM_MASK
        is_test = (ctrl & TEST_BIT) != 0 and waveform == 0
        is_audible = _is_audible_wave(ctrl)
        note = freq_hi_to_note(freq_hi) if freq_hi > 0 else -1

        frame_states.append({
            'freq_hi': freq_hi,
            'freq_lo': freq_lo,
            'freq16': (freq_hi << 8) | freq_lo,
            'gate': gate,
            'waveform': waveform,
            'ctrl': ctrl,
            'is_test': is_test,
            'is_audible': is_audible,
            'note': note,
            'ad': ad,
            'sr': sr,
            'pw': (pw_hi << 8) | pw_lo,
        })

    nframes = len(frame_states)
    if nframes == 0:
        return []

    # Phase 2: Detect note-on boundaries
    # A note starts at gate 0->1 transition, or freq_hi change while gated+audible.
    # Hard restart frames (test bit $08/$09) before gate-on are skipped.
    # First-wave detection: if waveform changes within the first 2 frames of a note,
    # the first frame's waveform is the first_wave and the settled one is primary.

    events = []
    in_note = False
    note_start = -1
    current_note = -1
    current_ad = 0
    current_sr = 0
    current_wave = 0
    current_pw = 0
    first_wave = -1  # first-frame waveform if different from settled

    def _close_note(end_frame):
        nonlocal in_note, current_note
        dur = end_frame - note_start
        if dur > 0 and current_note >= 0:
            # Use the most common freq_hi during this note (the "settled" note),
            # not the first frame's freq_hi (which may be a wave table transient).
            note_fh_counts = Counter()
            freq16_by_fh = defaultdict(list)
            for f in range(note_start, min(end_frame, nframes)):
                fh = frame_states[f]['freq_hi']
                if fh > 0 and frame_states[f]['is_audible']:
                    note_fh_counts[fh] += 1
                    freq16_by_fh[fh].append(frame_states[f]['freq16'])
            if note_fh_counts:
                settled_fh = note_fh_counts.most_common(1)[0][0]
                # Among PAL notes that share the same freq_hi as the
                # original, pick the one whose full 16-bit freq is
                # closest.  This preserves freq_hi (no note_wrong risk)
                # while minimising freq_lo error.
                fh_freq16s = freq16_by_fh[settled_fh]
                settled_freq16 = Counter(fh_freq16s).most_common(1)[0][0]
                candidates = [i for i in range(96)
                              if FREQ_HI_PAL[i] == settled_fh]
                if candidates:
                    settled_note = min(
                        candidates,
                        key=lambda i: abs(FREQ_TABLE_PAL[i] - settled_freq16))
                else:
                    # freq_hi not in PAL table — find nearest by freq_hi
                    settled_note = freq_hi_to_note(settled_fh)
                if settled_note >= 0:
                    current_note = settled_note

            # Use the settled waveform (most common across the note).
            # Frame 0 may be a first-wave transient (noise click, etc.).
            # The settled waveform is what the note actually sounds like.
            wave_counts = Counter()
            for f in range(note_start, min(end_frame, nframes)):
                w = frame_states[f]['waveform']
                if w != 0:
                    wave_counts[w] += 1
            settled_fw = first_wave  # preserve outer scope first_wave
            if wave_counts:
                settled_wave = wave_counts.most_common(1)[0][0]
                frame0_wave = frame_states[note_start]['waveform'] if note_start < nframes else 0
                if frame0_wave != 0 and frame0_wave != settled_wave and dur > 1:
                    settled_fw = frame0_wave
                current_wave = settled_wave

            events.append({
                'type': 'note', 'note': current_note,
                'frame': note_start, 'duration': dur,
                'ad': current_ad, 'sr': current_sr,
                'waveform': current_wave, 'pw': current_pw,
                'first_wave': settled_fw,
            })
        in_note = False

    def _is_vibrato(i, old_note, new_note):
        """Check if a frequency change is vibrato/wave-table (returns within tempo window)."""
        if abs(new_note - old_note) > 2:
            return False
        # Look ahead within one tempo window
        look = min(tempo + 1, nframes - i)
        for j in range(1, look):
            fst = frame_states[i + j]
            if fst['note'] == old_note and fst['gate'] and fst['is_audible']:
                return True
        return False

    def _is_wave_cycling(i, old_note, new_note):
        """Check if a freq change is wave table cycling (arpeggio/octave pattern).

        Returns True if old_note reappears within 4 frames while gate stays on.
        This catches arpeggios with intervals > 2 semitones that _is_vibrato
        misses (e.g., octave arpeggios, major chord patterns).
        """
        look = min(5, nframes - i)
        for j in range(1, look):
            fst = frame_states[i + j]
            if not (fst['gate'] and fst['is_audible']):
                break  # gate went off — not cycling
            if fst['note'] == old_note:
                return True
        return False

    prev_gate = False
    for i, st in enumerate(frame_states):
        gate_on = st['gate'] and st['is_audible'] and st['note'] >= 0
        gate_rising = gate_on and not prev_gate

        if gate_on:
            if gate_rising or not in_note:
                # New note: close previous if any
                if in_note:
                    _close_note(i)

                in_note = True
                note_start = i
                current_ad = st['ad']
                current_sr = st['sr']
                current_pw = st['pw']
                first_wave = -1

                current_wave = st['waveform']
                current_note = st['note']
                first_wave = -1
            else:
                # Already in a note — check for freq change (legato/new note while gated)
                if st['note'] != current_note:
                    if (_is_vibrato(i, current_note, st['note']) or
                            _is_wave_cycling(i, current_note, st['note'])):
                        pass  # vibrato or wave table cycling — ignore
                    else:
                        # Check for legato: new freq sustains for tempo//2 frames
                        new_note = st['note']
                        sustain_count = 0
                        for k in range(i, min(i + tempo + 2, nframes)):
                            if frame_states[k]['note'] == new_note and frame_states[k]['gate']:
                                sustain_count += 1
                            else:
                                break
                        if sustain_count >= max(3, tempo // 2):
                            # Legato: sustained freq change — new note
                            _close_note(i)
                            in_note = True
                            note_start = i
                            current_note = new_note
                            current_ad = st['ad']
                            current_sr = st['sr']
                            current_wave = st['waveform']
                            current_pw = st['pw']
                            first_wave = -1
                        # else: unsustained non-cycling change — ignore
        else:
            if in_note:
                _close_note(i)
                # Emit off event
                events.append({
                    'type': 'off', 'note': -1,
                    'frame': i, 'duration': 1,
                    'ad': 0, 'sr': 0, 'waveform': 0, 'pw': 0,
                    'first_wave': -1,
                })

        prev_gate = st['gate'] and st['is_audible']

    # Close final note
    if in_note:
        _close_note(nframes)

    # Phase 3: Absorb short init notes into the following real note.
    # Pattern: chains of 1-2 frame notes at note start (wave table init)
    # followed by a longer note. The short notes get absorbed into the
    # longer note (their frames become part of its duration).
    # Example: [noise 1fr] [pulse D#3 1fr] [pulse F#1 169fr] → [F#1 171fr fw=noise]
    absorbed = []
    i_ev = 0
    while i_ev < len(events):
        e = events[i_ev]
        if e['type'] == 'note' and e['duration'] <= 2:
            # Collect chain of short notes
            chain = [e]
            j = i_ev + 1
            while (j < len(events) and events[j]['type'] == 'note' and
                   events[j]['duration'] <= 2 and
                   events[j]['frame'] == chain[-1]['frame'] + chain[-1]['duration']):
                chain.append(events[j])
                j += 1

            # Check if chain is followed by a longer note (the "real" note)
            if (j < len(events) and events[j]['type'] == 'note' and
                    events[j]['frame'] == chain[-1]['frame'] + chain[-1]['duration'] and
                    events[j]['duration'] > 2):
                # Absorb the chain into the real note
                real = dict(events[j])
                total_init = sum(c['duration'] for c in chain)
                real['duration'] += total_init
                real['frame'] = chain[0]['frame']
                # Record first-wave from the first chain element if waveform differs
                if chain[0]['waveform'] != real['waveform']:
                    real['first_wave'] = chain[0]['waveform']
                absorbed.append(real)
                i_ev = j + 1
                continue

        absorbed.append(e)
        i_ev += 1
    events = absorbed

    # Phase 4: Merge consecutive off events and compute gap durations
    merged = []
    for e in events:
        if merged and merged[-1]['type'] == 'off' and e['type'] == 'off':
            merged[-1]['duration'] += e['duration']
        else:
            merged.append(e)

    # Recompute off durations from frame positions
    for i in range(len(merged) - 1):
        if merged[i]['type'] == 'off' and merged[i + 1]['type'] != 'off':
            merged[i]['duration'] = merged[i + 1]['frame'] - merged[i]['frame']

    return merged


def detect_tempo_from_frames(frames, fps=50):
    """Detect tempo directly from raw frames by finding the most common
    gate-on interval across all voices.

    This is more reliable than detecting from extracted events because
    it works before note extraction (which may split wave-table arpeggio
    frames into separate events).
    """
    intervals = []
    for v in range(3):
        off = VOICE_OFFSETS[v]
        prev_gate_on = -1
        prev_gate = False
        for i, frame in enumerate(frames):
            ctrl = frame[off + IDX_CTRL]
            gate = bool(ctrl & GATE_BIT) and _is_audible_wave(ctrl)
            if gate and not prev_gate:
                if prev_gate_on >= 0:
                    d = i - prev_gate_on
                    if 3 <= d <= 64:
                        intervals.append(d)
                prev_gate_on = i
            prev_gate = gate

    if not intervals:
        return 6

    counter = Counter(intervals)
    best_tempo = 6
    best_score = 0

    for tempo in range(3, 17):
        score = 0
        total = 0
        for dur, count in counter.items():
            weight = count
            total += weight
            if dur % tempo == 0:
                score += weight
            elif dur % tempo <= 1 or (tempo - dur % tempo) <= 1:
                score += weight * 0.5
        if total > 0:
            ratio = score / total
            if ratio > best_score:
                best_score = ratio
                best_tempo = tempo

    # Prefer double when both score well
    double = best_tempo * 2
    counter2 = Counter(intervals)
    if double <= 16:
        score_d = sum(c for d, c in counter2.items() if d % double == 0 or d % double <= 1 or (double - d % double) <= 1)
        total_d = sum(counter2.values())
        if total_d > 0 and score_d / total_d > 0.25:
            best_tempo = double

    return best_tempo


def detect_tempo(voice_events_list, fps=50):
    """Detect the most likely tempo (frames per row) from note event timing.

    Uses note durations and inter-onset intervals. Prefers tempos that
    evenly divide most observed durations. Minimum tempo is 3 because
    tempo 1-2 causes player init bugs.
    """
    durations = []
    onsets = []
    for voice_events in voice_events_list:
        for e in voice_events:
            if e['duration'] > 0:
                durations.append(e['duration'])
            if e['type'] == 'note':
                onsets.append(e['frame'])

    if not durations:
        return 6

    # Inter-onset intervals
    onsets.sort()
    intervals = []
    for i in range(1, len(onsets)):
        d = onsets[i] - onsets[i - 1]
        if 2 <= d <= 64:
            intervals.append(d)

    all_values = durations + intervals
    counter = Counter(all_values)

    best_tempo = 6
    best_score = 0
    tempo_scores = {}

    for tempo in range(3, 17):
        score = 0
        total = 0
        for dur, count in counter.items():
            # Weight longer durations more (short durations are noisy)
            weight = count * max(1, dur // 6)
            total += weight
            remainder = dur % tempo
            if remainder == 0:
                score += weight
            elif remainder <= 1 or (tempo - remainder) <= 1:
                score += weight * 0.5

        if total > 0:
            ratio = score / total
            tempo_scores[tempo] = ratio
            if ratio > best_score:
                best_score = ratio
                best_tempo = tempo

    # Prefer higher tempo when it's a multiple of a lower candidate.
    # Every duration divisible by 6 is also divisible by 3, so tempo 3
    # always scores >= tempo 6. Check: if best_tempo has a double that
    # also scores reasonably (> 25%), prefer the double.
    double = best_tempo * 2
    if double in tempo_scores and tempo_scores[double] > 0.25:
        best_tempo = double

    return best_tempo


def collapse_arpeggios(voice_events, tempo):
    """Collapse rapid note sequences within tick boundaries into single notes
    with arpeggio wave tables.

    Within a single tick (tempo frames), the player may cycle freq_hi through
    multiple values — this is a wave table arpeggio, not separate notes.
    Detect these patterns and merge into one note event with an 'arpeggio' field.
    """
    if not voice_events:
        return voice_events

    # Group consecutive note events that fit within tick-aligned windows
    result = []
    i = 0
    while i < len(voice_events):
        e = voice_events[i]

        if e['type'] != 'note' or e['duration'] > tempo:
            result.append(e)
            i += 1
            continue

        # Collect a run of short notes, skipping intervening off events
        # (the off events are gate-off frames within the arpeggio tick cycle)
        run = [e]
        j = i + 1
        while j < len(voice_events):
            nxt = voice_events[j]
            if nxt['type'] == 'off' and nxt['duration'] <= tempo:
                j += 1  # skip short off events
                continue
            if nxt['type'] != 'note' or nxt['duration'] > tempo:
                break
            # Check time proximity — must be within 2 ticks of the run
            prev_end = run[-1]['frame'] + run[-1]['duration']
            gap = nxt['frame'] - prev_end
            if gap > tempo + 1:
                break
            run.append(nxt)
            j += 1

        if len(run) < 6:
            # Too short to be arpeggio — need at least 3 full cycles of 2 notes
            result.extend(run)
            i = j
            continue

        # Check for repeating note pattern
        notes = [r['note'] for r in run]
        unique_notes = set(notes)

        if len(unique_notes) < 2 or len(unique_notes) > 4:
            # All same note, or too many different notes — not a clean arpeggio
            result.extend(run)
            i = j
            continue

        # Find the repeating period (2-4 notes) and the longest clean prefix
        best_period = None
        best_prefix_len = 0
        for period in range(2, min(5, len(notes) // 2 + 1)):
            pattern = notes[:period]
            # Find how far the pattern repeats cleanly
            prefix_len = period
            for k in range(period, len(notes)):
                if notes[k] == pattern[k % period]:
                    prefix_len = k + 1
                else:
                    break
            if prefix_len >= 6 and prefix_len > best_prefix_len:
                best_period = period
                best_prefix_len = prefix_len

        if best_period is None:
            result.extend(run)
            i = j
            continue

        # Use only the clean prefix, leave the rest for further processing
        arp_run = run[:best_prefix_len]
        leftover = run[best_prefix_len:]

        # Build arpeggio: base note = first note, offsets relative
        base_note = arp_run[0]['note']
        arp_steps = []
        for k in range(best_period):
            offset = arp_run[k]['note'] - base_note
            wave = arp_run[k]['waveform']
            arp_steps.append((wave, offset))

        total_frames = (arp_run[-1]['frame'] + arp_run[-1]['duration']) - arp_run[0]['frame']

        merged = {
            'type': 'note',
            'note': base_note,
            'frame': arp_run[0]['frame'],
            'duration': total_frames,
            'ad': arp_run[0]['ad'],
            'sr': arp_run[0]['sr'],
            'waveform': arp_run[0]['waveform'],
            'pw': arp_run[0].get('pw', 0),
            'first_wave': -1,
            'arpeggio': arp_steps,
        }
        result.append(merged)

        # Put leftover notes back for further processing
        # Rewind j to process them
        if leftover:
            j = i + 1
            # Find where leftover[0] is in voice_events
            target_frame = leftover[0]['frame']
            while j < len(voice_events) and voice_events[j]['frame'] < target_frame:
                j += 1
        else:
            # Skip any trailing off events within the arpeggio range
            while j < len(voice_events) and voice_events[j]['type'] == 'off':
                if voice_events[j]['frame'] < merged['frame'] + merged['duration']:
                    j += 1
                else:
                    break

        i = j

    return result


def _extract_note_wave_pattern(frames, voice_idx, note_start, note_dur, settled_note, max_steps=8):
    """Extract the per-frame (waveform_byte, note_offset) pattern for one note.

    Looks at the first `max_steps` frames of the note (or fewer if the note is
    shorter). Returns a tuple of (waveform_with_gate, note_semitone_offset)
    for each frame, relative to the settled note.

    The settled note is the most common freq_hi during the note (already
    computed by _close_note). Note offsets are in semitones relative to it.

    Noise waveform frames use note_offset=0 (noise freq is not musically
    meaningful — it controls timbre, not pitch).
    """
    off = VOICE_OFFSETS[voice_idx]
    nframes = len(frames)
    pattern = []
    settled_fh = FREQ_HI_PAL[settled_note] if 0 <= settled_note < 96 else 0

    for f in range(note_start, min(note_start + max_steps, note_start + note_dur, nframes)):
        fh = frames[f][off + IDX_FREQ_HI]
        ctrl = frames[f][off + IDX_CTRL]

        waveform_bits = ctrl & WAVEFORM_MASK
        gate = ctrl & GATE_BIT
        # Skip test-bit-only frames (hard restart)
        if (ctrl & TEST_BIT) and waveform_bits == 0:
            continue

        wave_byte = waveform_bits | (0x01 if gate else 0x00)

        # Compute note offset from settled note.
        # Noise waveform: offset is always 0 (noise frequency = timbre, not pitch)
        if waveform_bits == 0x80:
            note_offset = 0
        elif fh > 0 and settled_fh > 0:
            frame_note = freq_hi_to_note(fh)
            note_offset = frame_note - settled_note if frame_note >= 0 else 0
        else:
            note_offset = 0

        pattern.append((wave_byte, note_offset))

    return tuple(pattern)


def _detect_pulse_modulation(pw_sequences):
    """Detect pulse modulation speed from per-note PW frame sequences.

    Only returns a result when there is strong evidence of intentional
    pulse modulation: consistent speed, significant PW range, enough notes.
    """
    if len(pw_sequences) < 3:
        return None

    all_deltas = []
    initial_pws = []
    pw_ranges = []
    for seq in pw_sequences:
        if len(seq) < 4:
            continue
        initial_pws.append(seq[0])
        pw_ranges.append(max(seq) - min(seq))
        for i in range(1, len(seq)):
            delta = seq[i] - seq[i - 1]
            if delta != 0:
                all_deltas.append(delta)

    if not all_deltas or len(initial_pws) < 3:
        return None

    # PW range must be significant (at least 0x100 across notes)
    median_range = sorted(pw_ranges)[len(pw_ranges) // 2] if pw_ranges else 0
    if median_range < 0x100:
        return None

    abs_deltas = [abs(d) for d in all_deltas]
    delta_counter = Counter(abs_deltas)
    most_common_abs, count = delta_counter.most_common(1)[0]

    # Need at least 60% of deltas to agree on magnitude (strict)
    if count < len(all_deltas) * 0.6:
        return None
    if most_common_abs == 0 or most_common_abs > 127:
        return None

    pos_count = sum(1 for d in all_deltas if d > 0)
    neg_count = sum(1 for d in all_deltas if d < 0)
    if pos_count == 0 and neg_count == 0:
        return None

    direction_changes = (pos_count > len(all_deltas) * 0.2 and
                         neg_count > len(all_deltas) * 0.2)

    speed = most_common_abs if pos_count >= neg_count else -most_common_abs
    speed_byte = speed & 0xFF

    initial_pw = Counter(initial_pws).most_common(1)[0][0] if initial_pws else 0x0808

    return (initial_pw, speed_byte, direction_changes)


def build_instruments(all_voice_events, frames=None):
    """Build instrument definitions from observed (ad, sr, waveform) combinations.

    If `frames` is provided, reconstructs wave tables from per-frame register
    data (ctrl + freq_hi sequences within each note). Otherwise falls back to
    simple first-wave and arpeggio detection.

    Returns (instruments_list, inst_map, shared_pulse_table) where inst_map maps
    (ad, sr, waveform) -> instrument id.
    """
    combos = Counter()
    pw_info = defaultdict(list)
    pw_sequences = defaultdict(list)
    gate_off_durations = defaultdict(list)  # key -> list of gate-off frame counts
    wave_patterns = defaultdict(list)  # key -> list of per-frame patterns

    for voice_idx, voice_events in enumerate(all_voice_events):
        for ev_i, e in enumerate(voice_events):
            if e['type'] != 'note':
                continue
            key = (e['ad'], e['sr'], e['waveform'])
            combos[key] += 1
            if e.get('pw', 0) > 0:
                pw_info[key].append(e['pw'])

            # Collect per-frame PW sequence for pulse modulation detection
            if frames is not None and e['duration'] >= 4:
                vi = e.get('voice_idx', voice_idx)
                voff = VOICE_OFFSETS[vi]
                pw_seq = []
                for f in range(e['frame'], min(e['frame'] + e['duration'], len(frames))):
                    pw_hi = frames[f][voff + IDX_PW_HI]
                    pw_lo = frames[f][voff + IDX_PW_LO]
                    pw_seq.append((pw_hi << 8) | pw_lo)
                if len(pw_seq) >= 4:
                    pw_sequences[key].append(pw_seq)

            # Detect gate-off duration preceding this note.
            # The off event before a note tells us how many frames gate was off
            # (the hard-restart gap), which is the gate_timer for this instrument.
            if ev_i > 0 and voice_events[ev_i - 1]['type'] == 'off':
                off_dur = voice_events[ev_i - 1]['duration']
                if 1 <= off_dur <= 15:
                    gate_off_durations[key].append(off_dur)

            # Extract per-frame wave pattern from raw register data
            if frames is not None and e['duration'] >= 2:
                pat = _extract_note_wave_pattern(
                    frames, e.get('voice_idx', voice_idx),
                    e['frame'], e['duration'], e['note'],
                    max_steps=min(8, max(4, e['duration']))
                )
                if len(pat) >= 2:
                    wave_patterns[key].append(pat)

    sorted_combos = combos.most_common()

    instruments = []
    inst_map = {}

    wave_names = {0x10: 'tri', 0x20: 'saw', 0x40: 'pulse', 0x80: 'noise',
                  0x50: 'pulse', 0x30: 'saw', 0x60: 'pulse', 0x70: 'pulse',
                  # Ring modulation (bit 2)
                  0x14: 'tri_ring', 0x24: 'saw_ring', 0x44: 'pulse_ring',
                  # Hard sync (bit 1)
                  0x12: 'tri_sync', 0x22: 'saw_sync', 0x42: 'pulse_sync',
                  # Ring + sync
                  0x16: 'tri_ring_sync', 0x26: 'saw_ring_sync', 0x46: 'pulse_ring_sync'}

    # Also collect arpeggio patterns from collapse_arpeggios
    arp_info = defaultdict(list)
    for voice_events in all_voice_events:
        for e in voice_events:
            if e['type'] != 'note':
                continue
            key = (e['ad'], e['sr'], e['waveform'])
            if 'arpeggio' in e:
                arp_info[key].append(tuple(tuple(s) for s in e['arpeggio']))

    # Build shared pulse table from detected modulation patterns.
    shared_pulse_table = []
    pulse_mod_info = {}

    for (ad, sr, waveform), count in sorted_combos:
        key = (ad, sr, waveform)
        seqs = pw_sequences.get(key, [])
        if not seqs:
            continue
        mod_result = _detect_pulse_modulation(seqs)
        if mod_result is None:
            continue
        initial_pw, speed_byte, direction_changes = mod_result
        pulse_ptr = len(shared_pulse_table) + 1
        pw_hi_nib = (initial_pw >> 8) & 0x0F
        pw_lo_byte = initial_pw & 0xFF
        shared_pulse_table.append((0x80 | pw_hi_nib, pw_lo_byte))
        shared_pulse_table.append((127, speed_byte))
        if direction_changes:
            reverse_speed = ((256 - speed_byte) & 0xFF)
            shared_pulse_table.append((127, reverse_speed))
            shared_pulse_table.append((0xFF, pulse_ptr + 1))
        else:
            shared_pulse_table.append((0xFF, pulse_ptr))
        pulse_mod_info[key] = (pulse_ptr, initial_pw)

    for idx, ((ad, sr, waveform), count) in enumerate(sorted_combos):
        waveform_name = wave_names.get(waveform, 'pulse')

        key = (ad, sr, waveform)
        pw = 0x0808
        if key in pulse_mod_info:
            pw = pulse_mod_info[key][1]
        elif pw_info[key]:
            pw = Counter(pw_info[key]).most_common(1)[0][0]

        wave_byte = waveform | 0x01  # add gate bit
        wave_table = []
        fw_val = -1

        # Try to build wave table from per-frame register patterns
        patterns = wave_patterns.get((ad, sr, waveform), [])

        if patterns and len(patterns) >= 2:
            wave_table, fw_val = _build_wave_table_from_patterns(
                patterns, wave_byte, waveform)

        # Fallback: arpeggio from collapse_arpeggios
        if not wave_table:
            arp_list = arp_info.get((ad, sr, waveform), [])
            if arp_list:
                arp_counter = Counter(arp_list)
                most_common_arp, arp_count = arp_counter.most_common(1)[0]
                if arp_count >= max(1, len(arp_list) * 0.3):
                    for wave_val, note_off in most_common_arp:
                        wb = (wave_val | 0x01) if wave_val & 0xF0 else wave_byte
                        wave_table.append(WaveTableStep(waveform=wb, note_offset=note_off))
                    wave_table.append(WaveTableStep(is_loop=True, loop_target=0))

        # Fallback: simple single-step wave table
        if not wave_table:
            wave_table.append(WaveTableStep(waveform=wave_byte, note_offset=0))
            wave_table.append(WaveTableStep(is_loop=True, loop_target=0))

        # Detect gate timer from observed gate-off durations for this instrument.
        # Gate timers are the short, consistent off gaps between notes (hard restart).
        # Musical rests are longer and less consistent.
        # Only short gaps (1-4 frames) are reliable gate timers; longer gaps are
        # usually musical rests.  Default to 2 when no clear short gap is found.
        gt_key = (ad, sr, waveform)
        gt_durs = gate_off_durations.get(gt_key, [])
        detected_gt = 2  # safe default — most GT2 songs use gate_timer=2
        if len(gt_durs) >= 2:
            gt_counter = Counter(gt_durs)
            # Only consider durations 1-4 as candidate gate timers
            short_durs = {d: c for d, c in gt_counter.items() if 1 <= d <= 4}
            if short_durs:
                detected_gt = max(short_durs, key=short_durs.get)
            # else: all gaps are long musical rests — keep default of 2

        p_ptr = pulse_mod_info[key][0] if key in pulse_mod_info else 0

        inst = Instrument(
            id=idx,
            ad=ad,
            sr=sr,
            waveform=waveform_name,
            first_wave=fw_val if fw_val >= 0 else -1,
            gate_timer=detected_gt,
            hr_method='gate',
            pulse_width=pw,
            wave_table=wave_table,
            pulse_ptr=p_ptr,
        )
        instruments.append(inst)
        inst_map[(ad, sr, waveform)] = idx

    # Ensure at least one instrument
    if not instruments:
        instruments.append(Instrument(
            id=0, ad=0x09, sr=0x00, waveform='pulse',
            gate_timer=2, hr_method='gate',
            wave_table=[
                WaveTableStep(waveform=0x41, note_offset=0),
                WaveTableStep(is_loop=True, loop_target=0),
            ],
        ))
        inst_map[(0x09, 0x00, 0x40)] = 0

    return instruments, inst_map, shared_pulse_table


def _build_wave_table_from_patterns(patterns, wave_byte, settled_waveform):
    """Build a WaveTableStep list from collected per-frame register patterns.

    Takes a list of per-note patterns (each a tuple of (wave_byte, note_offset)
    per frame) and finds the consensus pattern across all notes of this instrument.

    Focused approach: detect two specific wave table patterns that improve quality:
    1. First-wave waveform change (noise click, different waveform on frame 0)
    2. First-wave octave up (freq_hi doubled on frame 0, common attack transient)

    Only builds a 2-3 step wave table: [first_wave_step, sustain_step, loop].
    Avoids complex multi-step patterns that cause regressions.

    Returns (wave_table_steps, first_wave_value).
    """
    if not patterns:
        return [], -1

    if len(patterns) < 3:
        return [], -1

    min_len = min(len(p) for p in patterns)
    if min_len < 2:
        return [], -1

    settled_wave_type = settled_waveform  # & 0xF0

    # Analyze frame 0 and frame 1 across all patterns
    frame0_waves = Counter()
    frame0_offsets = Counter()
    frame1_waves = Counter()
    frame1_offsets = Counter()

    for pat in patterns:
        wb0, noff0 = pat[0]
        frame0_waves[wb0 & 0xF0] += 1
        frame0_offsets[noff0] += 1
        if len(pat) >= 2:
            wb1, noff1 = pat[1]
            frame1_waves[wb1 & 0xF0] += 1
            frame1_offsets[noff1] += 1

    # Check for first-wave waveform change on frame 0
    # (frame 0 has a different waveform type than the settled waveform)
    best_fw0, fw0_count = frame0_waves.most_common(1)[0]
    fw0_ratio = fw0_count / len(patterns)

    # Check frame 1 — should be the settled waveform (confirms frame 0 is transient)
    if frame1_waves:
        best_fw1, fw1_count = frame1_waves.most_common(1)[0]
    else:
        best_fw1 = settled_wave_type

    # Pattern 1: First-wave waveform change (non-noise)
    # Frame 0 has different waveform, frame 1 has settled waveform.
    # Skip noise first-wave — the V2 player wave table timing doesn't match
    # the original's noise click well enough (causes wave_wrong regressions).
    if (fw0_ratio >= 0.5 and best_fw0 != settled_wave_type and
            best_fw0 != 0x80 and  # skip noise
            best_fw1 == settled_wave_type):
        offset0 = 0
        best_off0, off0_count = frame0_offsets.most_common(1)[0]
        if off0_count >= len(patterns) * 0.5 and abs(best_off0) >= 7:
            offset0 = best_off0

        fw_byte = best_fw0 | 0x01
        sustain_byte = settled_wave_type | 0x01
        steps = [
            WaveTableStep(waveform=fw_byte, note_offset=offset0),
            WaveTableStep(waveform=sustain_byte, note_offset=0),
            WaveTableStep(is_loop=True, loop_target=1),
        ]
        return steps, fw_byte

    # Pattern 2: Octave-up transient on frame 0
    # Same waveform but freq_hi is one octave up (+12 semitones)
    best_off0, off0_count = frame0_offsets.most_common(1)[0]
    off0_ratio = off0_count / len(patterns)

    if (off0_ratio >= 0.5 and best_off0 >= 12 and
            best_fw0 == settled_wave_type):
        sustain_byte = settled_wave_type | 0x01
        steps = [
            WaveTableStep(waveform=sustain_byte, note_offset=best_off0),
            WaveTableStep(waveform=sustain_byte, note_offset=0),
            WaveTableStep(is_loop=True, loop_target=1),
        ]
        return steps, -1

    # Pattern 3: Cycling arpeggio — repeating (waveform, note_offset) sequence
    # Build per-frame consensus across all patterns, then detect a repeating cycle.
    max_frames = min(min_len, 8)
    consensus = []
    consensus_confidence = []
    for f in range(max_frames):
        pair_counts = Counter()
        for pat in patterns:
            if f < len(pat):
                wb, noff = pat[f]
                pair_counts[(wb & 0xF0, noff)] += 1

        best_pair, best_count = pair_counts.most_common(1)[0]
        confidence = best_count / len(patterns)
        consensus.append(best_pair)
        consensus_confidence.append(confidence)

    # Try cycle periods 2, 3, 4
    best_cycle = None
    best_cycle_score = 0
    for period in range(2, min(5, max_frames // 2 + 1)):
        cycle = consensus[:period]
        # Check: do the cycle steps have at least 2 distinct values?
        if len(set(cycle)) < 2:
            continue
        # Count how many consensus frames match the cycle
        matches = 0
        total = 0
        for f in range(max_frames):
            expected = cycle[f % period]
            if consensus[f] == expected and consensus_confidence[f] >= 0.4:
                matches += 1
            total += 1
        score = matches / total if total > 0 else 0
        # Also check agreement across patterns: for each frame position,
        # what fraction of patterns match the cycle's expected value?
        pattern_agreement = 0
        pattern_total = 0
        for f in range(min(max_frames, period * 3)):
            expected = cycle[f % period]
            for pat in patterns:
                if f < len(pat):
                    actual = (pat[f][0] & 0xF0, pat[f][1])
                    pattern_total += 1
                    if actual == expected:
                        pattern_agreement += 1
        pat_score = pattern_agreement / pattern_total if pattern_total > 0 else 0

        if score >= 0.75 and pat_score >= 0.5 and score > best_cycle_score:
            best_cycle = cycle
            best_cycle_score = score

    if best_cycle is not None:
        steps = []
        for wave_bits, note_off in best_cycle:
            wb = wave_bits | 0x01  # add gate bit
            steps.append(WaveTableStep(waveform=wb, note_offset=note_off))
        steps.append(WaveTableStep(is_loop=True, loop_target=0))
        fw_val = -1
        if (best_cycle[0][0] != settled_waveform and
                best_cycle[0][0] == 0x80):
            fw_val = best_cycle[0][0] | 0x01
        return steps, fw_val

    # No clear pattern — don't emit a wave table
    return [], -1


def quantize_events(voice_events, tempo):
    """Quantize frame-based events to tick-based durations.

    Each event's frame duration is divided by tempo and rounded.
    Minimum 1 tick.
    """
    quantized = []
    for e in voice_events:
        q = dict(e)
        raw_dur = e['duration']
        ticks = max(1, round(raw_dur / tempo))
        q['ticks'] = ticks
        quantized.append(q)
    return quantized


def events_to_pattern(quantized_events, inst_map):
    """Convert quantized events to a list of NoteEvent objects using duration encoding.

    Uses NoteEvent.duration for held notes instead of emitting one event per tick.
    A note held for 4 ticks = NoteEvent(duration=4), NOT 4 separate events.
    This produces compact patterns like real GT2 data.
    """
    note_events = []
    current_inst = -1

    for e in quantized_events:
        ticks = e['ticks']
        if ticks <= 0:
            continue

        # Cap duration at 32 (max USF duration token)
        remaining = ticks
        is_first = True

        while remaining > 0:
            chunk = min(remaining, 32)
            remaining -= chunk

            if is_first:
                if e['type'] == 'note':
                    key = (e['ad'], e['sr'], e['waveform'])
                    inst_id = inst_map.get(key, 0)
                    inst_arg = inst_id if inst_id != current_inst else -1
                    if inst_arg >= 0:
                        current_inst = inst_id

                    note_events.append(NoteEvent(
                        type='note',
                        note=e['note'],
                        duration=chunk,
                        instrument=inst_arg,
                    ))
                elif e['type'] == 'off':
                    note_events.append(NoteEvent(type='off', duration=chunk))
                else:
                    note_events.append(NoteEvent(type='rest', duration=chunk))
                is_first = False
            else:
                # Continuation beyond 32 ticks: rest (sustain)
                note_events.append(NoteEvent(type='rest', duration=chunk))

    return note_events


def detect_digi_playback(frames):
    """Detect 4-bit digi/sample playback from rapid $D418 volume register changes.

    When the SID volume register ($D418, low nibble) changes rapidly (every few
    cycles/frames rather than occasional volume changes), it indicates the player
    is using the volume register as a 4-bit DAC for sample playback.

    This is a detection stub — full sample extraction (decoding the sample data,
    detecting playback rate, identifying sample boundaries) is a future task that
    requires cycle-level timing from siddump --writelog output.

    Args:
        frames: List of 25-element register value lists from siddump.

    Returns:
        dict with detection results:
            'detected': bool — True if digi playback was found
            'digi_frames': list of (start_frame, end_frame) ranges
            'change_rate': float — average $D418 changes per frame (0 if none)
    """
    # TODO: Implement full digi detection. Current approach:
    # 1. Track $D418 low nibble (volume) changes per frame
    # 2. If volume changes on >50% of frames in a window, it's likely digi playback
    # 3. Identify contiguous digi regions (sample start/end)
    # 4. Future: use siddump --writelog for cycle-level timing to determine
    #    playback rate and extract raw sample data
    #
    # Key heuristic: normal volume changes (fades, muting) change $D418 a few
    # times per song. Digi playback changes it EVERY frame (or multiple times
    # per frame with CIA timer IRQ). A sustained run of >10 consecutive frames
    # with volume changes is almost certainly digi playback.

    if not frames:
        return {'detected': False, 'digi_frames': [], 'change_rate': 0.0}

    vol_changes = 0
    prev_vol = frames[0][IDX_FILT_MODE_VOL] & 0x0F
    digi_regions = []
    run_start = -1
    run_length = 0

    for i in range(1, len(frames)):
        vol = frames[i][IDX_FILT_MODE_VOL] & 0x0F
        if vol != prev_vol:
            vol_changes += 1
            if run_start < 0:
                run_start = i - 1
            run_length += 1
        else:
            if run_length >= 10:
                digi_regions.append((run_start, i))
            run_start = -1
            run_length = 0
        prev_vol = vol

    if run_length >= 10:
        digi_regions.append((run_start, len(frames)))

    change_rate = vol_changes / max(1, len(frames) - 1)
    detected = len(digi_regions) > 0

    return {
        'detected': detected,
        'digi_frames': digi_regions,
        'change_rate': change_rate,
    }


def _try_extract_freq_table(sid_path):
    """Try to extract the actual frequency table from the SID binary.

    Scans the binary for byte patterns matching the PAL freq table.
    Handles separate (stride 1) and interleaved (stride 2) layouts.

    Returns (freq_table_16bit, first_note) or None.
    """
    try:
        with open(sid_path, 'rb') as f:
            data = f.read()

        magic = data[:4]
        if magic not in (b'PSID', b'RSID'):
            return None

        header_len = int.from_bytes(data[6:8], 'big')
        code = data[header_len:]
        load_addr_h = int.from_bytes(data[8:10], 'big')
        if load_addr_h == 0:
            binary = code[2:]
        else:
            binary = code

        if len(binary) < 96:
            return None

        pal_hi = FREQ_HI_PAL

        best_matches = 0
        best_result = None

        for stride in [1, 2]:
            hi_col = 1 if stride == 2 else 0
            max_offset = len(binary) - 48 * stride
            if max_offset < 0:
                continue
            for offset in range(max_offset):
                for note_off in range(0, 48):
                    n = min(96 - note_off, (len(binary) - offset - hi_col) // stride)
                    if n < 24:
                        continue
                    matches = 0
                    for i in range(n):
                        bi = offset + hi_col + i * stride
                        if bi >= len(binary):
                            break
                        if abs(binary[bi] - pal_hi[note_off + i]) <= 1:
                            matches += 1
                    if matches > best_matches and matches >= n * 0.7:
                        best_matches = matches
                        # Extract full table
                        freq_table = []
                        for i in range(n):
                            bi_lo = offset + (0 if stride == 2 else 0) + i * stride
                            bi_hi = offset + hi_col + i * stride
                            if bi_hi >= len(binary) or bi_lo >= len(binary):
                                break
                            if stride == 2:
                                lo = binary[bi_lo]
                                hi = binary[bi_hi]
                            else:
                                hi = binary[bi_hi]
                                # For separate tables, freq_lo is harder to locate
                                lo = FREQ_LO_PAL[note_off + i]  # use PAL as fallback
                            freq_table.append((hi << 8) | lo)
                        if len(freq_table) >= 24:
                            best_result = (freq_table, note_off)

        if best_result and best_matches >= 30:
            return best_result
    except Exception:
        pass
    return None


def regtrace_to_usf(sid_path, duration=60, debug=False):
    """Convert a SID file to USF Song via register trace analysis.

    Args:
        sid_path: Path to the .sid file
        duration: Playback duration in seconds
        debug: Print debug info

    Returns:
        usf.Song object
    """
    metadata, frames = run_siddump(sid_path, duration)

    # Try to extract the actual frequency table via taint tracking.
    # This handles engines with custom tuning (Hubbard, etc.)
    # When found, temporarily replace the module-level PAL tables so all
    # note detection functions use the correct tuning.
    global FREQ_LO_PAL, FREQ_HI_PAL, FREQ_TABLE_PAL
    orig_lo, orig_hi, orig_table = FREQ_LO_PAL, FREQ_HI_PAL, FREQ_TABLE_PAL

    custom_freq = _try_extract_freq_table(sid_path)
    if custom_freq:
        table, first_note = custom_freq
        if debug:
            print(f"  Custom freq table: {len(table)} entries, first_note={first_note}")
        # Rebuild full 96-note table, padding with PAL for missing notes
        full_table = list(FREQ_TABLE_PAL)  # start with PAL
        for i in range(len(table)):
            if first_note + i < 96:
                full_table[first_note + i] = table[i]
        FREQ_TABLE_PAL = full_table
        FREQ_LO_PAL = [f & 0xFF for f in full_table]
        FREQ_HI_PAL = [(f >> 8) & 0xFF for f in full_table]

    try:
        result = _regtrace_to_usf_inner(sid_path, metadata, frames, duration, debug)
    finally:
        # Restore original tables
        FREQ_LO_PAL, FREQ_HI_PAL, FREQ_TABLE_PAL = orig_lo, orig_hi, orig_table

    return result


def _regtrace_to_usf_inner(sid_path, metadata, frames, duration, debug):
    """Inner implementation of regtrace_to_usf (after freq table setup)."""

    # Detect digi/sample playback (rapid $D418 writes)
    digi_info = detect_digi_playback(frames)

    if debug:
        print(f"Loaded {len(frames)} frames from {sid_path}")
        print(f"Metadata: {metadata}")
        if digi_info['detected']:
            print(f"  DIGI DETECTED: {len(digi_info['digi_frames'])} regions, "
                  f"change rate: {digi_info['change_rate']:.2f}/frame")
            for start, end in digi_info['digi_frames'][:5]:
                print(f"    frames {start}-{end} ({end - start} frames)")

    # TODO: Detect voice 3 modulation patterns.
    # Voice 3 used as modulation source ($D41B osc3 / $D41C env3) exhibits:
    #   - Voice 3 frequency changes but waveform has no gate (or gate is always on
    #     with no note changes — acting as LFO, not musical voice)
    #   - No audible output on voice 3 (test bit set, or volume=0, or filter routing
    #     excludes voice 3)
    #   - Correlated changes in other registers: filter cutoff, pulse width, or volume
    #     track voice 3's frequency/waveform cycle
    # Detection approach:
    #   1. Check if voice 3 gate is rarely toggled but freq changes regularly (LFO pattern)
    #   2. Check if voice 3 waveform is triangle/saw (typical LFO shapes) with no gate-off
    #   3. Look for correlation between voice 3 freq and filter cutoff / pulse width changes
    #   4. If detected, set song.voice3_as_modulator = True and populate
    #      song.modulation_routes with ModulationRoute entries
    # This is common in Rob Hubbard and demo scene players.

    # Detect tempo: try frame-based first (works before event extraction),
    # then refine with event-based detection after extraction.
    tempo_initial = detect_tempo_from_frames(frames, fps=int(metadata.get('fps', 50)))

    # Detect init silence — how many frames before any voice produces sound.
    # The V2 player needs this as leading rest ticks to align with the original.
    init_silent_frames = 0
    for i, frame in enumerate(frames):
        any_gate = any(frame[VOICE_OFFSETS[v] + IDX_CTRL] & GATE_BIT
                       for v in range(3))
        if any_gate:
            init_silent_frames = i
            break

    # Extract events per voice using initial tempo, then refine tempo
    all_voice_events = []
    for v in range(3):
        events = extract_voice_events(frames, v, tempo=tempo_initial, debug=debug)
        events = collapse_arpeggios(events, tempo_initial)
        all_voice_events.append(events)
        if debug:
            note_count = sum(1 for e in events if e['type'] == 'note')
            print(f"  Voice {v+1}: {note_count} notes, {len(events)} events total")
            for e in events[:5]:
                if e['type'] == 'note':
                    fw = e.get('first_wave', -1)
                    fw_str = f" fw=${fw:02X}" if fw >= 0 else ""
                    print(f"    frame={e['frame']} {note_name(e['note'])} dur={e['duration']} "
                          f"AD=${e['ad']:02X} SR=${e['sr']:02X} wave=${e['waveform']:02X}{fw_str}")

    # Refine tempo with event-based detection (more accurate for many songs)
    tempo = detect_tempo(all_voice_events, fps=int(metadata.get('fps', 50)))
    if debug:
        print(f"  Detected tempo: {tempo} frames/tick")

    # Tag events with voice index for wave pattern extraction
    for v in range(3):
        for e in all_voice_events[v]:
            e['voice_idx'] = v

    # Build instruments with wave table reconstruction from raw frames
    instruments, inst_map, shared_pulse_table = build_instruments(all_voice_events, frames=frames)
    if debug:
        print(f"  Detected {len(instruments)} instruments:")
        for inst in instruments:
            fw_str = f" fw=${inst.first_wave:02X}" if inst.first_wave >= 0 else ""
            print(f"    I{inst.id}: AD=${inst.ad:02X} SR=${inst.sr:02X} "
                  f"wave={inst.waveform}{fw_str}")

    # Build song
    # TODO: Extract filter data from register trace.
    # For each frame, capture $D415 (IDX_FILT_LO, low 3 bits) and $D416
    # (IDX_FILT_HI) writes. Build FilterTableStep sequences with cutoff_low
    # set when non-zero. This enables full 11-bit filter cutoff resolution
    # for demo-scene players that write both registers.
    # Also detect a global filter_cutoff_low default if $D415 is constant.

    song = Song(
        title=metadata.get('title', os.path.basename(sid_path)),
        author=metadata.get('author', ''),
        sid_model=metadata.get('sid_model', '6581'),
        clock=metadata.get('clock', 'PAL'),
        tempo=tempo,
        instruments=instruments,
        nowavedelay=True,
        shared_pulse_table=shared_pulse_table,
    )

    clock_flag = 0x04 if metadata.get('clock') == 'PAL' else 0x08
    sid_flag = 0x10 if metadata.get('sid_model') == '6581' else 0x20
    song.psid_flags = clock_flag | sid_flag

    v2_init_delay = 6  # typical V2 init delay in frames

    pattern_id = 0
    for v in range(3):
        quantized = quantize_events(all_voice_events[v], tempo)
        note_events = events_to_pattern(quantized, inst_map)

        # Note: events have absolute frame numbers from siddump. The V2
        # player init delay (~6 frames) roughly aligns with the original's
        # init silence for most songs. No additional leading rest needed.

        if note_events:
            pat = Pattern(id=pattern_id, events=note_events)
            song.patterns.append(pat)
            song.orderlists[v].append((pattern_id, 0))
            pattern_id += 1
        else:
            # Empty voice: add a rest pattern covering the whole song
            total_ticks = max(1, len(frames) // tempo)
            pat = Pattern(id=pattern_id, events=[
                NoteEvent(type='rest', duration=min(total_ticks, 32))
            ])
            song.patterns.append(pat)
            song.orderlists[v].append((pattern_id, 0))
            pattern_id += 1

    # Set orderlist restart to last pattern (no loop for register-traced songs)
    for v in range(3):
        if song.orderlists[v]:
            song.orderlists[v].append(song.orderlists[v][-1])
            song.orderlist_restart[v] = len(song.orderlists[v]) - 1

    if debug:
        total_events = sum(len(p.events) for p in song.patterns)
        print(f"\n  Song: {len(song.patterns)} patterns, {len(song.instruments)} instruments, "
              f"{total_events} events total")
        for v in range(3):
            total_ticks = sum(e.duration for p_id, _ in song.orderlists[v]
                            for e in song.patterns[p_id].events)
            print(f"  Voice {v+1}: {len(song.orderlists[v])} orderlist entries, {total_ticks} ticks")

    return song


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert SID register trace to USF')
    parser.add_argument('sid_file', help='Path to .sid file')
    parser.add_argument('--duration', type=int, default=60, help='Playback duration (seconds)')
    parser.add_argument('--debug', action='store_true', help='Print debug info')
    parser.add_argument('--output', '-o', help='Output rebuilt .sid file')
    parser.add_argument('--compare', action='store_true', help='Compare original vs rebuilt')
    parser.add_argument('--text', action='store_true', help='Print USF text representation')
    args = parser.parse_args()

    song = regtrace_to_usf(args.sid_file, args.duration, args.debug)

    if args.text:
        from adapters.usf_tokens import tokenize
        from adapters.usf_text import to_text
        tokens = tokenize(song)
        print(to_text(tokens))

    if args.output or args.compare:
        from converters.usf_to_sid import usf_to_sid
        out_path = args.output or '/tmp/regtrace_rebuilt.sid'
        usf_to_sid(song, out_path)
        print(f"Rebuilt SID: {out_path}")

        if args.compare:
            from sid_compare import compare_sids_tolerant
            comp = compare_sids_tolerant(args.sid_file, out_path,
                                          min(args.duration, 10))
            if comp:
                print(f"Grade: {comp['grade']}  Score: {comp['score']:.1f}")
                for v in range(3):
                    vk = f'v{v+1}'
                    if vk in comp:
                        vc = comp[vk]
                        nw = vc.get('note_wrong', 0)
                        ww = vc.get('wave_wrong', 0)
                        nj = vc.get('note_jitter', 0)
                        print(f"  V{v+1}: note_wrong={nw} wave_wrong={ww} note_jitter={nj}")
            else:
                print("Comparison failed")


if __name__ == '__main__':
    main()
