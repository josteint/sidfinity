"""
gt2_test_pipeline.py — End-to-end test: GT2 SID → USF → flags → gt2asm → SID → compare.
"""

import sys
import os
import subprocess
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt2_to_usf import gt2_to_usf
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
    """Build a SID from USF data + flags using gt2asm."""
    ni = len(song.instruments)
    raw = getattr(song, '_raw_gt2', None) or {}
    raw_cols = raw.get('col_data', {})

    def raw_col(name, default=0):
        vals = raw_cols.get(name, [])
        if vals:
            result = list(vals[:ni])
            while len(result) < ni:
                result.append(default)
            return bytes(result)
        return bytes([default] * ni)

    # Get instrument columns
    ad_col = raw_col('ad')
    sr_col = raw_col('sr')
    wp_col = raw_col('wave_ptr')
    pp_col = raw_col('pulse_ptr')
    fp_col = raw_col('filter_ptr')
    vp_col = raw_col('vib_param')
    vd_col = raw_col('vib_delay')
    gt_col = raw_col('gate_timer', 0x02)
    fw_col = raw_col('first_wave', 0x41)

    # Classify and reorder instruments
    reorder, num_normal, num_nohr, num_legato = classify_instruments(gt_col)

    # If all normal (most common), no reorder needed
    if num_nohr == 0 and num_legato == 0:
        # No reorder
        pass
    else:
        ad_col = reorder_column(ad_col, reorder)
        sr_col = reorder_column(sr_col, reorder)
        wp_col = reorder_column(wp_col, reorder)
        pp_col = reorder_column(pp_col, reorder)
        fp_col = reorder_column(fp_col, reorder)
        vp_col = reorder_column(vp_col, reorder)
        vd_col = reorder_column(vd_col, reorder)
        gt_col = reorder_column(gt_col, reorder)
        fw_col = reorder_column(fw_col, reorder)

    # FIXEDPARAMS: extract first instrument's values
    first_wave_param = fw_col[0] if fw_col else 0x09
    gate_timer_param = (gt_col[0] & 0x3F) if gt_col else 0x02

    # Encode patterns
    gt2_patterns = [usf_pattern_to_gt2(p) for p in song.patterns]

    # Encode orderlists
    gt2_orderlists = []
    for vi in range(3):
        entries = song.orderlists[vi]
        ol = bytearray()
        i = 0
        while i < len(entries):
            patt_id, transpose = entries[i]
            repeat_count = 1
            while (i + repeat_count < len(entries) and
                   entries[i + repeat_count] == entries[i]):
                repeat_count += 1
            if i == 0 or transpose != entries[i - 1][1]:
                if transpose >= 0:
                    ol.append(0xF0 + transpose)
                else:
                    ol.append(0xE0 + (16 + transpose))
            if repeat_count <= 2:
                for _ in range(repeat_count):
                    ol.append(patt_id)
            else:
                ol.append(patt_id)
                ol.append(0xD0 + (repeat_count - 1))
            i += repeat_count
        ol.extend([0xFF, 0x00])
        gt2_orderlists.append(bytes(ol))

    # Shared tables
    wave_l = bytearray()
    wave_r = bytearray()
    if song.shared_wave_table:
        for l, rv in song.shared_wave_table:
            wave_l.append(l)
            wave_r.append(rv)

    pulse_l = bytearray()
    pulse_r = bytearray()
    if song.shared_pulse_table:
        for l, rv in song.shared_pulse_table:
            pulse_l.append(l)
            pulse_r.append(rv)

    filter_l = bytearray()
    filter_r = bytearray()
    if song.shared_filter_table:
        for l, rv in song.shared_filter_table:
            filter_l.append(l)
            filter_r.append(rv)

    speed_l = raw.get('speed_left') or bytes([0])
    speed_r = raw.get('speed_right') or bytes([0])

    freq_lo = getattr(song, 'freq_lo', None)
    freq_hi = getattr(song, 'freq_hi', None)

    first_note = getattr(song, 'first_note', 0)
    last_note = first_note + 95  # default range
    # Adjust last_note based on freq table if available
    if first_note > 0:
        last_note = 95  # always end at note 95

    return pack_gt2(
        flags=flags,
        base_addr=r['la'],
        songs=1,
        first_note=first_note,
        last_note=last_note,
        default_tempo=getattr(song, 'tempo', 6) - 1,
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
        wave_left=bytes(wave_l) if wave_l else None,
        wave_right=bytes(wave_r) if wave_r else None,
        pulse_left=bytes(pulse_l) if pulse_l else None,
        pulse_right=bytes(pulse_r) if pulse_r else None,
        filter_left=bytes(filter_l) if filter_l else None,
        filter_right=bytes(filter_r) if filter_r else None,
        speed_left=speed_l,
        speed_right=speed_r,
        orderlists=gt2_orderlists,
        patterns=gt2_patterns,
        freq_lo=freq_lo,
        freq_hi=freq_hi,
        title=song.title,
        author=song.author,
        player_group=getattr(song, 'gt2_player_group', ''),
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

    # Start with all features enabled, then disable based on actual data.
    # This ensures the data layout matches: tables that don't exist in the
    # data aren't emitted by the packer (no phantom bytes to shift offsets).
    flags = {k: 0 for k in [
        'NOEFFECTS','NOGATE','NOFILTER','NOFILTERMOD','NOPULSE','NOPULSEMOD',
        'NOWAVEDELAY','NOWAVECMD','NOREPEAT','NOTRANS','NOPORTAMENTO','NOTONEPORTA',
        'NOVIB','NOINSTRVIB','NOSETAD','NOSETSR','NOSETWAVE','NOSETWAVEPTR',
        'NOSETPULSEPTR','NOSETFILTPTR','NOSETFILTCTRL','NOSETFILTCUTOFF',
        'NOSETMASTERVOL','NOFUNKTEMPO','NOGLOBALTEMPO','NOCHANNELTEMPO',
        'NOFIRSTWAVECMD','NOCALCULATEDSPEED','NONORMALSPEED','NOZEROSPEED']}
    flags['FIXEDPARAMS'] = 0
    flags['SIMPLEPULSE'] = 0

    # Keep all features enabled — the original GT2 packer includes ALL
    # instrument columns and tables even when unused (zero-filled).
    # Disabling features removes columns, shifting the wave table position.

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
