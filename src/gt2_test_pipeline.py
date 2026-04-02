"""
gt2_test_pipeline.py — End-to-end test: GT2 SID → USF → flags → gt2asm → SID → compare.
"""

import sys
import os
import subprocess
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt2_to_usf import gt2_to_usf, pack_wave_left, pack_wave_right
from gt2_parse_direct import parse_gt2_direct
from usf_to_sid import usf_pattern_to_gt2
from gt2_packer import pack_gt2

from detect_flags import detect_gt2_flags

SIDDUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'siddump')


def classify_instruments(gate_timer_col):
    """Classify instruments into normal/nohr/legato per greloc.c logic.
    Returns (reorder_map, num_normal, num_nohr, num_legato)."""
    normals = []
    nohrs = []
    legatos = []
    for i, gt in enumerate(gate_timer_col):
        if gt & 0x40:
            legatos.append(i)
        elif gt & 0x80:
            nohrs.append(i)
        else:
            normals.append(i)
    # greloc.c order: normals first, then nohr, then legato
    reorder = normals + nohrs + legatos
    return reorder, len(normals), len(nohrs), len(legatos)


def reorder_column(col_bytes, order):
    """Reorder instrument column bytes according to classification order."""
    return bytes([col_bytes[i] for i in order])


def build_sid_from_usf(sid_path, song, r, flags):
    """Build a SID from USF data + flags using gt2asm.

    All data comes from USF Song fields — no raw binary passthrough.
    """
    ni = len(song.instruments)

    # Build instrument columns from USF Instrument fields
    ad_col = bytes([inst.ad for inst in song.instruments])
    sr_col = bytes([inst.sr for inst in song.instruments])
    wp_col = bytes([inst.wave_ptr for inst in song.instruments])
    pp_col = bytes([inst.pulse_ptr for inst in song.instruments])
    fp_col = bytes([inst.filter_ptr for inst in song.instruments])
    vp_col = bytes([inst.vib_speed_idx for inst in song.instruments])
    vd_col = bytes([inst.vib_delay for inst in song.instruments])
    gt_col = bytes([getattr(inst, '_gate_timer_raw', inst.gate_timer) for inst in song.instruments])
    fw_col = bytes([inst.first_wave if inst.first_wave >= 0 else 0x41 for inst in song.instruments])

    # Classify and reorder instruments
    reorder, num_normal, num_nohr, num_legato = classify_instruments(gt_col)
    if num_nohr > 0 or num_legato > 0:
        ad_col = reorder_column(ad_col, reorder)
        sr_col = reorder_column(sr_col, reorder)
        wp_col = reorder_column(wp_col, reorder)
        pp_col = reorder_column(pp_col, reorder)
        fp_col = reorder_column(fp_col, reorder)
        vp_col = reorder_column(vp_col, reorder)
        vd_col = reorder_column(vd_col, reorder)
        gt_col = reorder_column(gt_col, reorder)
        fw_col = reorder_column(fw_col, reorder)

    first_wave_param = fw_col[0] if fw_col else 0x09
    gate_timer_param = (gt_col[0] & 0x3F) if gt_col else 0x02

    # Encode patterns and orderlists
    gt2_patterns = [usf_pattern_to_gt2(p) for p in song.patterns]

    gt2_orderlists = []
    for vi in range(3):
        entries = song.orderlists[vi]
        ol = bytearray()
        entry_to_byte = {}  # maps entry index → byte position in ol
        entry_idx = 0
        i = 0
        while i < len(entries):
            patt_id, transpose = entries[i]
            repeat_count = 1
            while (i + repeat_count < len(entries) and
                   entries[i + repeat_count] == entries[i]):
                repeat_count += 1
            prev_trans = entries[i - 1][1] if i > 0 else 0
            if transpose != prev_trans:
                if transpose >= 0:
                    ol.append(0xF0 + transpose)
                else:
                    ol.append(0xE0 + (16 + transpose))
            if repeat_count <= 2:
                for _ in range(repeat_count):
                    entry_to_byte[entry_idx] = len(ol)
                    entry_idx += 1
                    ol.append(patt_id)
            else:
                entry_to_byte[entry_idx] = len(ol)
                entry_idx += 1
                ol.append(patt_id)
                ol.append(0xD0 + (repeat_count - 1))
                for k in range(1, repeat_count):
                    entry_to_byte[entry_idx] = entry_to_byte[entry_idx - 1]
                    entry_idx += 1
            i += repeat_count
        # Convert pattern entry index back to byte offset for the loop point
        restart_entry = song.orderlist_restart[vi] if vi < len(song.orderlist_restart) else 0
        restart_byte = entry_to_byte.get(restart_entry, 0)
        ol.extend([0xFF, restart_byte])
        gt2_orderlists.append(bytes(ol))

    # Tables — from USF shared tables (stored in .sng format) and speed_table.
    # Re-apply packed format transforms for the wave table.
    # Detect NOWAVEDELAY from the .sng data: any delay ($01-$0F) means delays enabled.
    _nowavedelay = True
    for _l, _ in song.shared_wave_table:
        if 0 < _l < 0x10:
            _nowavedelay = False
            break
    wave_l = bytes([pack_wave_left(l, _nowavedelay) for l, _ in song.shared_wave_table]) if song.shared_wave_table else None
    wave_r = bytes([pack_wave_right(r, l) for l, r in song.shared_wave_table]) if song.shared_wave_table else None
    pulse_l = bytes([l for l, _ in song.shared_pulse_table]) if song.shared_pulse_table else None
    pulse_r = bytes([rv for _, rv in song.shared_pulse_table]) if song.shared_pulse_table else None
    filter_l = bytes([l for l, _ in song.shared_filter_table]) if song.shared_filter_table else None
    filter_r = bytes([rv for _, rv in song.shared_filter_table]) if song.shared_filter_table else None
    speed_l = bytes([e.left for e in song.speed_table]) if song.speed_table else None
    speed_r = bytes([e.right for e in song.speed_table]) if song.speed_table else None

    return pack_gt2(
        flags=flags,
        base_addr=r['la'],
        songs=1,
        first_note=song.first_note,
        last_note=95,
        default_tempo=song.tempo - 1,
        num_instruments=ni,
        num_normal=num_normal,
        num_nohr=num_nohr,
        num_legato=num_legato,
        ad_param=0x0F,
        sr_param=0x00,
        first_wave_param=first_wave_param,
        gate_timer_param=gate_timer_param,
        instruments_ad=ad_col,
        instruments_sr=sr_col,
        instruments_waveptr=wp_col,
        instruments_pulseptr=pp_col,
        instruments_filtptr=fp_col,
        instruments_vibparam=vp_col,
        instruments_vibdelay=vd_col,
        instruments_gatetimer=gt_col,
        instruments_firstwave=fw_col,
        wave_left=wave_l,
        wave_right=wave_r,
        pulse_left=pulse_l,
        pulse_right=pulse_r,
        filter_left=filter_l,
        filter_right=filter_r,
        speed_left=speed_l,
        speed_right=speed_r,
        orderlists=gt2_orderlists,
        patterns=gt2_patterns,
        title=song.title,
        author=song.author,
        player_group=song.gt2_player_group,
    )


def compare_sids(orig_path, new_path, duration=10):
    """Compare two SIDs via siddump. Returns (match_pct, total_frames, details)."""
    def dump(path):
        r = subprocess.run([SIDDUMP, path, '--duration', str(duration)],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return None
        lines = r.stdout.strip().split('\n')
        return lines[2:]  # skip header

    orig = dump(orig_path)
    new = dump(new_path)
    if orig is None or new is None:
        return 0, 0, 'dump_failed'

    total = min(len(orig), len(new))
    if total == 0:
        return 0, 0, 'no_frames'

    full_match = sum(1 for o, n in zip(orig, new) if o == n)

    # Per-voice freq_hi match
    voice_match = {}
    for v, idx in enumerate([1, 8, 15]):
        vm = sum(1 for o, n in zip(orig, new)
                 if o.split(',')[idx] == n.split(',')[idx])
        voice_match[f'v{v+1}_fhi'] = vm

    return 100 * full_match / total, total, voice_match


def test_single(sid_path, duration=10, verbose=False):
    """Test a single GT2 SID through the pipeline."""
    # Parse
    r = parse_gt2_direct(sid_path)
    if r is None:
        return {'status': 'parse_fail', 'path': sid_path}

    try:
        song = gt2_to_usf(sid_path)
    except Exception as e:
        return {'status': 'usf_fail', 'path': sid_path, 'error': str(e)}
    if song is None:
        return {'status': 'usf_fail', 'path': sid_path}

    # Detect flags from USF data — this determines which columns and tables
    # the player code includes. Must match the original's layout: if an
    # instrument references pulse_ptr, NOPULSE must be 0 (column present).
    # If no instrument uses pulse, NOPULSE=1 (column absent, table absent).
    flags = detect_gt2_flags(song, r)

    # Build SID
    try:
        sid_bytes, size = build_sid_from_usf(sid_path, song, r, flags)
    except Exception as e:
        return {'status': 'build_fail', 'path': sid_path, 'error': str(e)}

    # Write and compare
    out_path = '/tmp/gt2_test_out.sid'
    with open(out_path, 'wb') as f:
        f.write(sid_bytes)

    match_pct, total, details = compare_sids(sid_path, out_path, duration)

    if verbose:
        name = os.path.basename(sid_path)
        print(f'{name}: {match_pct:.1f}% ({total} frames) size={size}')
        if isinstance(details, dict):
            for k, v in details.items():
                print(f'  {k}: {v}/{total} ({100*v/total:.1f}%)')

    return {
        'status': 'ok',
        'path': sid_path,
        'match_pct': match_pct,
        'frames': total,
        'size': size,
        'details': details,
    }


def test_batch(pattern, duration=10, limit=None):
    """Test a batch of GT2 SIDs."""
    files = sorted(glob.glob(pattern, recursive=True))
    if limit:
        files = files[:limit]

    results = []
    buckets = {'90+': 0, '50-90': 0, '<50': 0, 'fail': 0}

    for i, f in enumerate(files):
        r = test_single(f, duration, verbose=True)
        results.append(r)

        if r['status'] != 'ok':
            buckets['fail'] += 1
        elif r['match_pct'] >= 90:
            buckets['90+'] += 1
        elif r['match_pct'] >= 50:
            buckets['50-90'] += 1
        else:
            buckets['<50'] += 1

        if (i + 1) % 20 == 0:
            print(f'\n--- Progress: {i+1}/{len(files)} ---')
            print(f'  90%+: {buckets["90+"]}  50-90%: {buckets["50-90"]}  '
                  f'<50%: {buckets["<50"]}  fail: {buckets["fail"]}')
            print()

    print(f'\n=== FINAL: {len(files)} files ===')
    print(f'  90%+: {buckets["90+"]}  50-90%: {buckets["50-90"]}  '
          f'<50%: {buckets["<50"]}  fail: {buckets["fail"]}')

    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: gt2_test_pipeline.py <file.sid|glob_pattern> [duration] [limit]")
        sys.exit(1)

    path = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None

    if '*' in path or '?' in path:
        test_batch(path, duration, limit)
    else:
        r = test_single(path, duration, verbose=True)
        print(f"Status: {r['status']}")
