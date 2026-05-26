"""
drum_extract.py — Extract per-frame drum register sequences from SID files.

Uses siddump register traces to capture the exact waveform + freq_hi behavior
of Hubbard-style drum instruments. The output is suitable for building accurate
USF wave tables with absolute_note entries.

Drum hits are detected by transitions to noise waveform ($80/$81) in the ctrl
register. After each hit, the next N frames of (ctrl, freq_hi) are captured
to form the complete drum sequence.

Usage:
    from sidxray.drum_extract import extract_drum_sequences
    seqs = extract_drum_sequences('path/to/song.sid')
    for voice, patterns in seqs.items():
        for pat in patterns:
            print(f'V{voice}: {pat}')
"""

import os
import sys
import subprocess
import json
import math
from collections import Counter

TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools')
SIDDUMP = os.path.join(TOOLS_DIR, 'siddump')

# Register indices in siddump CSV output (25 columns per frame)
# V1: 0=flo, 1=fhi, 2=pwlo, 3=pwhi, 4=ctrl, 5=ad, 6=sr
# V2: 7=flo, 8=fhi, 9=pwlo, 10=pwhi, 11=ctrl, 12=ad, 13=sr
# V3: 14=flo, 15=fhi, 16=pwlo, 17=pwhi, 18=ctrl, 19=ad, 20=sr
# Filter: 21=filt_lo, 22=filt_hi, 23=filt_ctrl, 24=filt_mode_vol
VOICE_OFFSETS = {
    0: {'flo': 0, 'fhi': 1, 'pwlo': 2, 'pwhi': 3, 'ctrl': 4, 'ad': 5, 'sr': 6},
    1: {'flo': 7, 'fhi': 8, 'pwlo': 9, 'pwhi': 10, 'ctrl': 11, 'ad': 12, 'sr': 13},
    2: {'flo': 14, 'fhi': 15, 'pwlo': 16, 'pwhi': 17, 'ctrl': 18, 'ad': 19, 'sr': 20},
}

# Noise waveform bit
NOISE_BIT = 0x80
GATE_BIT = 0x01
WAVEFORM_MASK = 0xF0

# Standard C64 PAL frequency table (freq_hi values for note lookup)
FREQ_HI_PAL = [
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
    0x04,0x04,0x04,0x05,0x05,0x05,0x06,0x06,0x06,0x07,0x07,0x08,
    0x08,0x09,0x09,0x0A,0x0A,0x0B,0x0C,0x0D,0x0D,0x0E,0x0F,0x10,
    0x11,0x12,0x13,0x14,0x15,0x17,0x18,0x1A,0x1B,0x1D,0x1F,0x20,
    0x22,0x24,0x27,0x29,0x2B,0x2E,0x31,0x34,0x37,0x3A,0x3E,0x41,
    0x45,0x49,0x4E,0x52,0x57,0x5C,0x62,0x68,0x6E,0x75,0x7C,0x83,
    0x8B,0x93,0x9C,0xA5,0xAF,0xB9,0xC4,0xD0,0xDD,0xEA,0xF8,0xFF]

NOTE_NAMES = ['C-','C#','D-','D#','E-','F-','F#','G-','G#','A-','A#','B-']


def freq_hi_to_note(fhi):
    """Map a freq_hi byte to the nearest PAL note number (0-95).

    Returns (note_number, note_name_str) or (-1, '??') if unmappable.
    """
    if fhi == 0:
        return -1, '??'
    best = -1
    best_dist = 256
    for i, h in enumerate(FREQ_HI_PAL):
        dist = abs(fhi - h)
        if dist < best_dist:
            best_dist = dist
            best = i
    octave = best // 12
    semitone = best % 12
    return best, f'{NOTE_NAMES[semitone]}{octave}'


def _run_siddump(sid_path, duration=10):
    """Run siddump and return list of frames (each frame = list of 25 ints)."""
    ld_path = os.path.join(os.path.dirname(SIDDUMP), '..', 'local', 'lib')
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = ld_path + ':' + env.get('LD_LIBRARY_PATH', '')

    cmd = [SIDDUMP, sid_path, '--duration', str(duration), '--force-rsid']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
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


def _is_noise_onset(prev_ctrl, curr_ctrl):
    """Detect a noise waveform onset (transition into noise).

    Returns True if current frame has noise bit set and either:
    - Previous frame did not have noise bit set, OR
    - Gate just turned on (gate was off, now on)
    """
    curr_noise = (curr_ctrl & NOISE_BIT) != 0
    prev_noise = (prev_ctrl & NOISE_BIT) != 0
    curr_gate = (curr_ctrl & GATE_BIT) != 0
    prev_gate = (prev_ctrl & GATE_BIT) != 0

    if not curr_noise:
        return False

    # Transition into noise from non-noise waveform
    if not prev_noise:
        return True

    # Gate on while already noise = new drum hit (re-trigger)
    if curr_gate and not prev_gate:
        return True

    return False


def _extract_sequence(frames, start_frame, voice, max_len=12):
    """Extract (ctrl, freq_hi) pairs for max_len frames after a drum onset.

    The sequence ends early if:
    - A new noise onset occurs (next drum hit starting)
    - We've settled into a steady non-noise state for 2+ frames
    - We reach end of frames
    """
    off = VOICE_OFFSETS[voice]
    seq = []

    for i in range(start_frame, min(start_frame + max_len, len(frames))):
        ctrl = frames[i][off['ctrl']]
        fhi = frames[i][off['fhi']]

        # Stop if a new noise onset happens (except on the very first frame)
        if len(seq) >= 1 and i > start_frame:
            prev_ctrl = frames[i-1][off['ctrl']]
            if _is_noise_onset(prev_ctrl, ctrl):
                break

        seq.append((ctrl, fhi))

        # If we've moved past the initial noise burst and settled into a
        # non-noise waveform for 2+ frames, stop capturing
        if len(seq) >= 3:
            last_two_non_noise = (
                (seq[-1][0] & NOISE_BIT) == 0 and
                (seq[-2][0] & NOISE_BIT) == 0
            )
            last_two_same = seq[-1] == seq[-2]
            if last_two_non_noise and last_two_same:
                # Settled into steady state -- trim the duplicate
                seq.pop()
                break

    return tuple(seq)


def _canonicalize_sequence(seq):
    """Produce a canonical form for grouping by stripping the gate bit
    and quantizing freq_hi to the nearest note.

    Two sequences that differ only in gate bit timing or minor freq_hi
    jitter (same nearest note) are the same drum.
    """
    canon = []
    for ctrl, fhi in seq:
        wave = ctrl & 0xFE  # strip gate bit
        note, _ = freq_hi_to_note(fhi)
        canon.append((wave, note))
    return tuple(canon)


def extract_drum_sequences(sid_path, duration=10, max_seq_len=12, min_hits=2):
    """Extract drum register sequences from a SID file.

    Args:
        sid_path: Path to .sid file
        duration: Seconds to analyze
        max_seq_len: Max frames to capture per drum hit
        min_hits: Minimum occurrences to report a pattern

    Returns:
        dict mapping voice index (0-2) to list of DrumPattern objects.
        Each DrumPattern has:
            .sequence: list of (ctrl_byte, freq_hi) tuples
            .count: number of times this pattern was seen
            .first_frame: frame number of first occurrence
            .wave_table_steps: suggested WaveTableStep parameters
    """
    metadata, frames = _run_siddump(sid_path, duration)

    result = {}

    for voice in range(3):
        off = VOICE_OFFSETS[voice]
        hits = []  # (frame_idx, sequence)

        for i in range(1, len(frames)):
            prev_ctrl = frames[i-1][off['ctrl']]
            curr_ctrl = frames[i][off['ctrl']]

            if _is_noise_onset(prev_ctrl, curr_ctrl):
                seq = _extract_sequence(frames, i, voice, max_seq_len)
                if len(seq) >= 2:  # need at least 2 frames to be meaningful
                    hits.append((i, seq))

        if not hits:
            continue

        # Group by canonical form (ignore gate bit differences)
        groups = {}
        for frame_idx, seq in hits:
            canon = _canonicalize_sequence(seq)
            if canon not in groups:
                groups[canon] = {
                    'sequences': [],
                    'frames': [],
                    'representative': seq,
                }
            groups[canon]['sequences'].append(seq)
            groups[canon]['frames'].append(frame_idx)

        # Build patterns for groups with enough hits
        patterns = []
        for canon, group in groups.items():
            count = len(group['sequences'])
            if count < min_hits:
                continue

            seq = group['representative']
            patterns.append(DrumPattern(
                sequence=list(seq),
                count=count,
                first_frame=group['frames'][0],
            ))

        # Sort by count (most common first)
        patterns.sort(key=lambda p: -p.count)

        if patterns:
            result[voice] = patterns

    return result


class DrumPattern:
    """A detected drum register sequence pattern."""

    def __init__(self, sequence, count, first_frame):
        self.sequence = sequence  # list of (ctrl, freq_hi)
        self.count = count
        self.first_frame = first_frame

    @property
    def wave_table_steps(self):
        """Convert this drum pattern to WaveTableStep-compatible dicts.

        Each step has 'waveform' and either 'absolute_note' or 'keep_freq',
        matching the USF WaveTableStep fields.
        """
        steps = []
        prev_fhi = None
        for ctrl, fhi in self.sequence:
            wave = ctrl | GATE_BIT  # ensure gate bit for audibility
            note_num, note_name = freq_hi_to_note(fhi)

            step = {'waveform': wave}
            if note_num >= 0:
                if prev_fhi is not None and fhi == prev_fhi:
                    step['keep_freq'] = True
                else:
                    step['absolute_note'] = note_num
                    step['note_name'] = note_name
            else:
                step['keep_freq'] = True

            steps.append(step)
            prev_fhi = fhi

        # Add loop back to last step (hold)
        if steps:
            steps.append({'is_loop': True, 'loop_target': len(steps) - 1})

        return steps

    def __repr__(self):
        parts = []
        for ctrl, fhi in self.sequence:
            wave_str = _wave_name(ctrl)
            _, note = freq_hi_to_note(fhi)
            parts.append(f'{wave_str}@{note}(${fhi:02X})')
        return f'DrumPattern({" -> ".join(parts)}, x{self.count})'


def _wave_name(ctrl):
    """Human-readable waveform name from ctrl byte."""
    wave = ctrl & 0xF0
    gate = 'g' if (ctrl & GATE_BIT) else '.'
    names = {
        0x00: f'off{gate}',
        0x10: f'tri{gate}',
        0x20: f'saw{gate}',
        0x30: f'ts{gate}',
        0x40: f'pul{gate}',
        0x50: f'tp{gate}',
        0x60: f'sp{gate}',
        0x80: f'noi{gate}',
    }
    return names.get(wave, f'${ctrl:02X}')


def print_drum_report(sid_path, duration=10):
    """Print a human-readable drum analysis report."""
    print(f'=== Drum Analysis: {os.path.basename(sid_path)} ===')
    print()

    seqs = extract_drum_sequences(sid_path, duration=duration, min_hits=1)

    if not seqs:
        print('No drum patterns detected.')
        return seqs

    for voice in sorted(seqs.keys()):
        patterns = seqs[voice]
        print(f'--- Voice {voice + 1} ({len(patterns)} pattern(s)) ---')
        for i, pat in enumerate(patterns):
            print(f'  Pattern {i+1} (seen {pat.count}x, first at frame {pat.first_frame}):')
            print(f'    Raw: {pat}')
            print(f'    Wave table steps:')
            for j, step in enumerate(pat.wave_table_steps):
                if step.get('is_loop'):
                    print(f'      [{j}] LOOP -> step {step["loop_target"]}')
                elif step.get('keep_freq'):
                    print(f'      [{j}] wave=${step["waveform"]:02X} keep_freq')
                else:
                    note_str = step.get('note_name', '??')
                    print(f'      [{j}] wave=${step["waveform"]:02X} absolute_note={step["absolute_note"]} ({note_str})')
            print()
    return seqs


# --- CLI entry point ---
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <sid_file> [duration_seconds]')
        sys.exit(1)

    sid_file = sys.argv[1]
    dur = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    print_drum_report(sid_file, dur)
