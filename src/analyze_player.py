"""
analyze_player.py - Analyze SID player behavior from write logs.

Takes a SID file, runs siddump --writelog, and produces a structured analysis
of how the player engine works:
  - Register write order per frame
  - Hard restart detection and timing
  - Multispeed detection
  - Which registers change vs stay constant
  - Intra-frame timing patterns
  - Data region identification via byte mutation

Usage:
  python3 analyze_player.py <file.sid> [--mutate] [--frames N]
"""

import json
import os
import struct
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field


def find_siddump():
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'tools', 'siddump'),
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return os.path.abspath(c)
    raise FileNotFoundError("siddump not found")


REG_NAMES = [
    'V1_FLo','V1_FHi','V1_PWL','V1_PWH','V1_Ctl','V1_AD','V1_SR',
    'V2_FLo','V2_FHi','V2_PWL','V2_PWH','V2_Ctl','V2_AD','V2_SR',
    'V3_FLo','V3_FHi','V3_PWL','V3_PWH','V3_Ctl','V3_AD','V3_SR',
    'Flt_Lo','Flt_Hi','Flt_Ct','Flt_MV',
]


def run_siddump(siddump_bin, sid_path, duration=10, writelog=True):
    """Run siddump and return parsed frames."""
    args = [siddump_bin, sid_path, '--duration', str(duration)]
    if writelog:
        args.append('--writelog')
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if result.returncode not in (0,):
        return None, None

    lines = result.stdout.strip().split('\n')
    if len(lines) < 3:
        return None, None

    metadata = json.loads(lines[0])
    frames = []
    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue

        writes = []
        reg_state = None

        if '|W' in line:
            parts = line.split('|W:')
            reg_hex = parts[0].rstrip(',')
            reg_state = [int(h, 16) for h in reg_hex.split(',')]

            wlog = parts[1]
            fields = wlog.split(':')
            for i in range(0, len(fields) - 2, 3):
                cycle = int(fields[i])
                reg = int(fields[i+1], 16)
                val = int(fields[i+2], 16)
                writes.append((cycle, reg, val))
        else:
            reg_hex = line.split('|')[0].rstrip(',')
            reg_state = [int(h, 16) for h in reg_hex.split(',')]

        frames.append({
            'regs': reg_state,
            'writes': writes,
        })

    return metadata, frames


def analyze_write_order(frames):
    """Analyze the register write order across frames.

    Returns the most common write sequence patterns.
    """
    order_counts = Counter()
    for frame in frames:
        if not frame['writes']:
            continue
        # Extract register sequence (ignoring cycle offsets)
        reg_order = tuple(w[1] for w in frame['writes'])
        order_counts[reg_order] += 1

    return order_counts.most_common(10)


def analyze_hard_restart(frames):
    """Detect hard restart patterns across all known methods.

    Methods used by different players:
    1. Gate toggle: gate on → gate off → gate on (classic)
    2. Test bit: write $09/$08 to control reg to reset oscillator
    3. ADSR manipulation: write specific ADSR values before new note
    4. Waveform $00: clear waveform to silence before new note

    We detect note transitions by watching for frequency changes with gate on,
    then look backwards to find the preparation sequence.
    """
    hr_patterns = []

    for voice in range(3):
        base = voice * 7
        ctrl_reg = base + 4
        ad_reg = base + 5
        sr_reg = base + 6
        fhi_reg = base + 1

        # Track per-frame state from register snapshots
        for i in range(4, len(frames)):
            curr = frames[i]['regs']
            prev1 = frames[i-1]['regs']
            prev2 = frames[i-2]['regs']
            prev3 = frames[i-3]['regs']

            # Detect note start: gate on with new frequency
            curr_gate = curr[ctrl_reg] & 0x01
            curr_freq = curr[fhi_reg]
            prev1_freq = prev1[fhi_reg]

            if not curr_gate or curr_freq == prev1_freq:
                continue

            # New note detected. Look back for HR preparation.
            hr_type = None
            hr_frames = 0
            hr_detail = {}

            # Check for test bit ($08 or $09) in preceding frames
            for back in range(1, 4):
                if i - back < 0:
                    break
                prev_ctrl = frames[i-back]['regs'][ctrl_reg]
                if prev_ctrl & 0x08:  # test bit set
                    hr_type = 'test_bit'
                    hr_frames = back
                    hr_detail['test_frame_ctrl'] = prev_ctrl
                    break

            # Check for gate off in preceding frames
            if hr_type is None:
                for back in range(1, 4):
                    if i - back < 0:
                        break
                    prev_ctrl = frames[i-back]['regs'][ctrl_reg]
                    if not (prev_ctrl & 0x01):  # gate off
                        hr_type = 'gate_off'
                        hr_frames = back
                        hr_detail['gateoff_ctrl'] = prev_ctrl
                        break

            # Check for ADSR change in preceding frames
            if hr_type is None:
                for back in range(1, 3):
                    if i - back < 0:
                        break
                    prev_ad = frames[i-back]['regs'][ad_reg]
                    prev_sr = frames[i-back]['regs'][sr_reg]
                    prev2_ad = frames[i-back-1]['regs'][ad_reg] if i-back-1 >= 0 else prev_ad
                    prev2_sr = frames[i-back-1]['regs'][sr_reg] if i-back-1 >= 0 else prev_sr
                    if prev_ad != prev2_ad or prev_sr != prev2_sr:
                        hr_type = 'adsr_change'
                        hr_frames = back
                        break

            # Check for waveform $00 (silence) in preceding frames
            if hr_type is None:
                for back in range(1, 3):
                    if i - back < 0:
                        break
                    prev_ctrl = frames[i-back]['regs'][ctrl_reg]
                    if (prev_ctrl & 0xF0) == 0 and not (prev_ctrl & 0x01):  # no waveform, no gate
                        hr_type = 'waveform_clear'
                        hr_frames = back
                        break

            if hr_type is None:
                hr_type = 'none'  # no HR detected — direct note change
                hr_frames = 0

            # Capture the ADSR values used during HR
            hr_ad = None
            hr_sr = None
            for back in range(1, hr_frames + 1):
                if i - back >= 0:
                    hr_ad = frames[i-back]['regs'][ad_reg]
                    hr_sr = frames[i-back]['regs'][sr_reg]

            hr_patterns.append({
                'frame': i,
                'voice': voice,
                'type': hr_type,
                'hr_frames': hr_frames,
                'gate_on_waveform': curr[ctrl_reg],
                'hr_ad': hr_ad,
                'hr_sr': hr_sr,
                'new_freq_hi': curr_freq,
                **hr_detail,
            })

    # Summarize by type
    hr_types = Counter()
    for p in hr_patterns:
        hr_types[p['type']] += 1

    # Summarize by (type, hr_frames, hr_ad, hr_sr)
    hr_detail_types = Counter()
    for p in hr_patterns:
        key = (p['type'], p['hr_frames'],
               f"${p['hr_ad']:02X}" if p['hr_ad'] is not None else None,
               f"${p['hr_sr']:02X}" if p['hr_sr'] is not None else None)
        hr_detail_types[key] += 1

    return hr_patterns, hr_types, hr_detail_types


def analyze_multispeed(frames):
    """Detect multispeed by looking for multiple distinct write bursts per frame."""
    burst_counts = []
    for frame in frames:
        if not frame['writes']:
            burst_counts.append(0)
            continue

        # Group writes into bursts (gap > 100 cycles = new burst)
        bursts = 1
        prev_cycle = frame['writes'][0][0]
        for cycle, reg, val in frame['writes'][1:]:
            if cycle - prev_cycle > 500:  # significant gap between bursts
                bursts += 1
            prev_cycle = cycle

        burst_counts.append(bursts)

    avg_bursts = sum(burst_counts) / len(burst_counts) if burst_counts else 0
    max_bursts = max(burst_counts) if burst_counts else 0

    return {
        'avg_bursts_per_frame': round(avg_bursts, 1),
        'max_bursts': max_bursts,
        'likely_multispeed': avg_bursts > 1.5,
        'speed_multiplier': round(avg_bursts) if avg_bursts > 1.5 else 1,
    }


def analyze_register_usage(frames):
    """Analyze which registers are used and how often they change."""
    write_counts = [0] * 25
    change_counts = [0] * 25
    prev_regs = None

    for frame in frames:
        regs = frame['regs']
        if regs is None:
            continue

        for w in frame['writes']:
            if w[1] < 25:
                write_counts[w[1]] += 1

        if prev_regs:
            for r in range(25):
                if regs[r] != prev_regs[r]:
                    change_counts[r] += 1

        prev_regs = regs

    return {
        'writes_per_reg': {REG_NAMES[r]: write_counts[r] for r in range(25)},
        'changes_per_reg': {REG_NAMES[r]: change_counts[r] for r in range(25)},
    }


def analyze_timing(frames):
    """Analyze intra-frame write timing."""
    first_write_cycles = []
    last_write_cycles = []
    total_write_spans = []

    for frame in frames:
        if not frame['writes']:
            continue
        cycles = [w[0] for w in frame['writes']]
        first_write_cycles.append(min(cycles))
        last_write_cycles.append(max(cycles))
        total_write_spans.append(max(cycles) - min(cycles))

    if not first_write_cycles:
        return {}

    return {
        'avg_first_write_cycle': round(sum(first_write_cycles) / len(first_write_cycles)),
        'avg_last_write_cycle': round(sum(last_write_cycles) / len(last_write_cycles)),
        'avg_write_span_cycles': round(sum(total_write_spans) / len(total_write_spans)),
        'avg_writes_per_frame': round(
            sum(len(f['writes']) for f in frames) / len(frames), 1),
    }


def mutate_and_diff(siddump_bin, sid_path, offset, original_val, new_val, duration=5):
    """Mutate one byte in the SID file and compare register output."""
    with open(sid_path, 'rb') as f:
        data = bytearray(f.read())

    data[offset] = new_val

    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        _, mutated_frames = run_siddump(siddump_bin, tmp_path, duration, writelog=False)
        return mutated_frames
    except Exception:
        return None
    finally:
        os.unlink(tmp_path)


def find_data_regions(siddump_bin, sid_path, duration=3):
    """Find data regions by mutating bytes and observing effects.

    Scans the data portion of the SID file, flipping bytes and checking
    which ones affect the register output.
    """
    with open(sid_path, 'rb') as f:
        raw = f.read()

    # Parse header to find data start
    data_offset = struct.unpack('>H', raw[6:8])[0]
    load_addr = struct.unpack('>H', raw[8:10])[0]
    if load_addr == 0:
        data_offset += 2  # skip embedded load address

    # Get baseline output
    _, baseline = run_siddump(siddump_bin, sid_path, duration, writelog=False)
    if not baseline:
        return {}

    baseline_regs = [f['regs'] for f in baseline if f['regs']]

    # Scan data area, test every Nth byte
    stride = 16  # test every 16th byte for speed
    affected = {}

    for off in range(data_offset, len(raw), stride):
        orig = raw[off]
        test_val = orig ^ 0xFF  # flip all bits

        mutated = mutate_and_diff(siddump_bin, sid_path, off, orig, test_val, duration)
        if not mutated:
            continue

        mutated_regs = [f['regs'] for f in mutated if f['regs']]

        # Compare
        diff_count = 0
        diff_regs = set()
        for b, m in zip(baseline_regs, mutated_regs):
            for r in range(25):
                if b[r] != m[r]:
                    diff_count += 1
                    diff_regs.add(r)

        if diff_count > 0:
            affected[off - data_offset] = {
                'diff_count': diff_count,
                'affected_regs': sorted(diff_regs),
                'affected_reg_names': [REG_NAMES[r] for r in sorted(diff_regs)],
            }

    return affected


def analyze_sid(sid_path, duration=10, do_mutate=False):
    """Full analysis of a SID file."""
    siddump_bin = find_siddump()

    print(f"Analyzing: {sid_path}", file=sys.stderr)
    metadata, frames = run_siddump(siddump_bin, sid_path, duration)

    if not frames:
        return {'error': 'siddump failed'}

    result = {
        'file': os.path.basename(sid_path),
        'metadata': metadata,
        'frame_count': len(frames),
    }

    # Write order analysis
    write_orders = analyze_write_order(frames)
    result['write_order'] = {
        'top_patterns': [
            {'order': [REG_NAMES[r] if r < 25 else f'${r:02X}' for r in pattern],
             'count': count}
            for pattern, count in write_orders[:5]
        ],
        'num_distinct_patterns': len(write_orders),
    }

    # Hard restart analysis
    hr_patterns, hr_types, hr_detail_types = analyze_hard_restart(frames)
    result['hard_restart'] = {
        'total_note_changes': len(hr_patterns),
        'by_type': {k: v for k, v in hr_types.most_common()},
        'details': [
            {'type': k[0], 'frames': k[1], 'hr_ad': k[2], 'hr_sr': k[3], 'count': v}
            for k, v in hr_detail_types.most_common(10)
        ],
    }

    # Multispeed analysis
    result['multispeed'] = analyze_multispeed(frames)

    # Register usage
    result['register_usage'] = analyze_register_usage(frames)

    # Timing analysis
    result['timing'] = analyze_timing(frames)

    # Mutation analysis (optional, slow)
    if do_mutate:
        print("Running mutation analysis...", file=sys.stderr)
        result['data_regions'] = find_data_regions(siddump_bin, sid_path, min(duration, 3))

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Analyze SID player behavior')
    parser.add_argument('input', help='SID file path')
    parser.add_argument('--duration', type=int, default=10, help='Analysis duration in seconds')
    parser.add_argument('--mutate', action='store_true', help='Run byte mutation analysis (slow)')
    parser.add_argument('-o', '--output', help='Output JSON file')
    args = parser.parse_args()

    result = analyze_sid(args.input, args.duration, args.mutate)

    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)


if __name__ == '__main__':
    main()
