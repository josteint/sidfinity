"""
validate_data.py — Compare DATA SECTIONS of original and rebuilt GT2 SIDs.

Skips player code (before freq table), song table pointers, and pattern table
pointers (assembler-resolved addresses). Compares byte-for-byte: instrument
columns, wave/pulse/filter/speed tables, orderlists, patterns.

Frequency tables are verified for correctness within the overlapping note range
but size differences are reported separately (they depend on packer parameters,
not music data).

This is the definitive test for data correctness — independent of player code.
"""

import sys
import os
import struct

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import parse_psid_header, find_freq_table, FREQ_TBL_LO, FREQ_TBL_HI


def _find_song_table(binary, la, search_start, songs):
    """Find song table by scanning for valid orderlist pointer pairs.

    The song table has songs*3 lo bytes followed by songs*3 hi bytes.
    Each (lo, hi) pair is an address pointing to an orderlist in the binary.
    """
    num_entries = songs * 3
    end_limit = len(binary) - num_entries * 2

    for off in range(search_start, end_limit):
        # Quick reject: all lo/hi pairs must form valid addresses
        valid = True
        addrs = []
        for j in range(num_entries):
            lo = binary[off + j]
            hi = binary[off + num_entries + j]
            addr = lo | (hi << 8)
            if not (la <= addr < la + len(binary)):
                valid = False
                break
            addrs.append(addr)
        if not valid:
            continue

        # Orderlists must be after all table data (after the song+patt tables)
        min_ol = min(addrs)
        if min_ol - la < off + num_entries * 2:
            continue

        # Each orderlist must have a 0xFF terminator within 256 bytes
        all_ok = True
        for addr in addrs:
            ol_off = addr - la
            found = False
            for k in range(min(256, len(binary) - ol_off)):
                if binary[ol_off + k] == 0xFF:
                    found = True
                    break
            if not found:
                all_ok = False
                break
        if all_ok:
            return off, num_entries

    return None, 0


def _find_pattern_table(binary, la, search_start, max_patts=208):
    """Find pattern table starting at or after search_start.

    The pattern table has N lo bytes followed by N hi bytes.
    Each (lo, hi) pair points to packed pattern data ending with 0x00.
    """
    for off in range(search_start, min(search_start + 32, len(binary))):
        for n in range(1, max_patts + 1):
            if off + n * 2 > len(binary):
                break
            valid = True
            min_addr = la + len(binary)
            for j in range(n):
                lo = binary[off + j]
                hi = binary[off + n + j]
                addr = lo | (hi << 8)
                if not (la <= addr < la + len(binary)):
                    valid = False
                    break
                min_addr = min(min_addr, addr)
            if not valid:
                continue
            # Patterns must be after the pattern table
            if min_addr < la + off + n * 2:
                continue
            # Try n+1: if also valid, keep searching for the true count
            if n < max_patts and off + (n + 1) * 2 <= len(binary):
                extra_lo = binary[off + n]
                extra_hi = binary[off + n * 2 + 1] if off + n * 2 + 1 < len(binary) else 0
                extra_addr = extra_lo | (extra_hi << 8)
                if la <= extra_addr < la + len(binary):
                    continue
            return off, n
    return None, 0


def map_data_sections(binary, la, songs):
    """Map all data sections in a GT2 SID binary.

    Returns dict describing each logical section's location and content,
    or None if the binary cannot be parsed.
    """
    ft = find_freq_table(binary, la)
    if ft is None:
        return None

    freq_off, first_note, num_notes, lo_first = ft
    freq_end = freq_off + num_notes * 2

    # Song table
    song_off, song_entries = _find_song_table(binary, la, freq_end, songs)
    if song_off is None:
        return None
    song_end = song_off + song_entries * 2

    # Pattern table
    patt_off, num_patt = _find_pattern_table(binary, la, song_end)
    if patt_off is None:
        return None
    patt_end = patt_off + num_patt * 2

    # Orderlist addresses (from song table)
    ol_addrs = []
    for j in range(song_entries):
        lo = binary[song_off + j]
        hi = binary[song_off + song_entries + j]
        ol_addrs.append(lo | (hi << 8))
    first_ol_off = min(a - la for a in ol_addrs)

    # Pattern addresses (from pattern table)
    patt_addrs = []
    for j in range(num_patt):
        lo = binary[patt_off + j]
        hi = binary[patt_off + num_patt + j]
        patt_addrs.append(lo | (hi << 8))
    first_patt_off = min(a - la for a in patt_addrs)

    # Last pattern: scan to 0x00 terminator
    last_patt_off = max(a - la for a in patt_addrs)
    patt_data_end = last_patt_off
    while patt_data_end < len(binary) and binary[patt_data_end] != 0x00:
        patt_data_end += 1
    if patt_data_end < len(binary):
        patt_data_end += 1  # include the 0x00

    return {
        'freq_off': freq_off,
        'freq_end': freq_end,
        'first_note': first_note,
        'num_notes': num_notes,
        'song_off': song_off,
        'song_end': song_end,
        'song_entries': song_entries,
        'patt_off': patt_off,
        'patt_end': patt_end,
        'num_patt': num_patt,
        'first_ol_off': first_ol_off,
        'first_patt_off': first_patt_off,
        'patt_data_end': patt_data_end,
        'binary': binary,
    }


def _compare_bytes(name, o_bytes, r_bytes):
    """Compare two byte sequences. Returns a result dict."""
    if len(o_bytes) != len(r_bytes):
        # Compare what we can in the common range
        common = min(len(o_bytes), len(r_bytes))
        diffs_in_common = 0
        first_diff_at = None
        for i in range(common):
            if o_bytes[i] != r_bytes[i]:
                diffs_in_common += 1
                if first_diff_at is None:
                    first_diff_at = i
        return {
            'name': name,
            'match': False,
            'orig_size': len(o_bytes),
            'rebuilt_size': len(r_bytes),
            'size_diff': len(r_bytes) - len(o_bytes),
            'diffs_in_common': diffs_in_common,
            'first_diff_at': first_diff_at,
            'first_diff_orig': f'${o_bytes[first_diff_at]:02X}' if first_diff_at is not None else None,
            'first_diff_rebuilt': f'${r_bytes[first_diff_at]:02X}' if first_diff_at is not None else None,
        }

    # Same size: byte-by-byte
    first_diff_at = None
    for i in range(len(o_bytes)):
        if o_bytes[i] != r_bytes[i]:
            first_diff_at = i
            break

    if first_diff_at is None:
        return {'name': name, 'match': True, 'size': len(o_bytes)}

    total_diffs = sum(1 for i in range(len(o_bytes)) if o_bytes[i] != r_bytes[i])

    # Context around first diff
    ctx_start = max(0, first_diff_at - 4)
    ctx_end = min(len(o_bytes), first_diff_at + 8)

    return {
        'name': name,
        'match': False,
        'size': len(o_bytes),
        'total_diffs': total_diffs,
        'first_diff_at': first_diff_at,
        'orig_byte': f'${o_bytes[first_diff_at]:02X}',
        'rebuilt_byte': f'${r_bytes[first_diff_at]:02X}',
        'orig_context': ' '.join(f'{b:02X}' for b in o_bytes[ctx_start:ctx_end]),
        'rebuilt_context': ' '.join(f'{b:02X}' for b in r_bytes[ctx_start:ctx_end]),
    }


def compare_data_sections(orig_path, rebuilt_path):
    """Compare data sections of original and rebuilt GT2 SIDs byte-for-byte.

    Skips: player code (before freq table), song table pointers, pattern
    table pointers. Compares: freq tables (overlapping range), instrument
    columns, wave/pulse/filter/speed tables, orderlists, patterns.

    Returns dict with:
      'match': True if all comparable data sections match
      'sections': list of per-section results
      'first_diff': description of first difference found, or None
      'orig_map': section layout of original (without binary)
      'rebuilt_map': section layout of rebuilt (without binary)
    """
    with open(orig_path, 'rb') as f:
        orig_data = f.read()
    with open(rebuilt_path, 'rb') as f:
        rebuilt_data = f.read()

    orig_hdr, orig_bin, orig_la = parse_psid_header(orig_data)
    rebuilt_hdr, rebuilt_bin, rebuilt_la = parse_psid_header(rebuilt_data)

    songs = orig_hdr['songs']

    orig_map = map_data_sections(orig_bin, orig_la, songs)
    rebuilt_map = map_data_sections(rebuilt_bin, rebuilt_la, songs)

    if orig_map is None:
        return {'match': False, 'error': 'Could not map original SID data sections',
                'sections': [], 'first_diff': 'parse failed',
                'orig_map': None, 'rebuilt_map': _strip_binary(rebuilt_map)}
    if rebuilt_map is None:
        return {'match': False, 'error': 'Could not map rebuilt SID data sections',
                'sections': [], 'first_diff': 'parse failed',
                'orig_map': _strip_binary(orig_map), 'rebuilt_map': None}

    ob = orig_map['binary']
    rb = rebuilt_map['binary']

    results = []
    first_diff = None
    all_match = True

    def record(r):
        nonlocal first_diff, all_match
        results.append(r)
        if not r['match']:
            all_match = False
            if first_diff is None:
                if 'first_diff_at' in r and r['first_diff_at'] is not None:
                    first_diff = (f"Section '{r['name']}' byte {r['first_diff_at']}: "
                                  f"orig={r.get('orig_byte', r.get('first_diff_orig', '?'))} "
                                  f"rebuilt={r.get('rebuilt_byte', r.get('first_diff_rebuilt', '?'))}")
                elif 'orig_size' in r:
                    first_diff = (f"Section '{r['name']}' size mismatch: "
                                  f"orig={r['orig_size']} rebuilt={r['rebuilt_size']}")
                else:
                    first_diff = f"Section '{r['name']}' differs"

    # 1. Frequency tables — compare overlapping note range
    o_fn, o_nn = orig_map['first_note'], orig_map['num_notes']
    r_fn, r_nn = rebuilt_map['first_note'], rebuilt_map['num_notes']
    common_first = max(o_fn, r_fn)
    common_last = min(o_fn + o_nn, r_fn + r_nn)
    if common_first < common_last:
        common_count = common_last - common_first
        # Extract common range from both (lo then hi)
        o_lo_off = orig_map['freq_off'] + (common_first - o_fn)
        o_hi_off = orig_map['freq_off'] + o_nn + (common_first - o_fn)
        r_lo_off = rebuilt_map['freq_off'] + (common_first - r_fn)
        r_hi_off = rebuilt_map['freq_off'] + r_nn + (common_first - r_fn)

        o_freq = bytes(ob[o_lo_off:o_lo_off + common_count] +
                       ob[o_hi_off:o_hi_off + common_count])
        r_freq = bytes(rb[r_lo_off:r_lo_off + common_count] +
                       rb[r_hi_off:r_hi_off + common_count])
        fr = _compare_bytes(f'freq_tables (notes {common_first}-{common_last-1})', o_freq, r_freq)
        if o_nn != r_nn:
            fr['note'] = f'note range differs: orig={o_fn}-{o_fn+o_nn-1} rebuilt={r_fn}-{r_fn+r_nn-1}'
        record(fr)
    else:
        record({'name': 'freq_tables', 'match': False,
                'orig_size': o_nn * 2, 'rebuilt_size': r_nn * 2,
                'first_diff_at': None})

    # 2. Instrument columns + tables (between end of pattern table pointers
    #    and start of orderlists)
    o_instr = ob[orig_map['patt_end']:orig_map['first_ol_off']]
    r_instr = rb[rebuilt_map['patt_end']:rebuilt_map['first_ol_off']]
    record(_compare_bytes('instruments_and_tables', o_instr, r_instr))

    # 3. Orderlists (between first orderlist and first pattern)
    o_ol = ob[orig_map['first_ol_off']:orig_map['first_patt_off']]
    r_ol = rb[rebuilt_map['first_ol_off']:rebuilt_map['first_patt_off']]
    record(_compare_bytes('orderlists', o_ol, r_ol))

    # 4. Pattern data (from first pattern to end of last pattern)
    o_patt = ob[orig_map['first_patt_off']:orig_map['patt_data_end']]
    r_patt = rb[rebuilt_map['first_patt_off']:rebuilt_map['patt_data_end']]
    record(_compare_bytes('patterns', o_patt, r_patt))

    return {
        'match': all_match,
        'sections': results,
        'first_diff': first_diff,
        'orig_map': _strip_binary(orig_map),
        'rebuilt_map': _strip_binary(rebuilt_map),
    }


def _strip_binary(m):
    """Remove binary data from map for display."""
    if m is None:
        return None
    return {k: v for k, v in m.items() if k != 'binary'}


def print_results(result, orig_name='', rebuilt_name=''):
    """Pretty-print comparison results."""
    if 'error' in result:
        print(f'ERROR: {result["error"]}')
        if not result.get('sections'):
            return

    status = 'MATCH' if result['match'] else 'DIFFER'
    print(f'Data comparison: {status}')
    if orig_name:
        print(f'  Original: {orig_name}')
    if rebuilt_name:
        print(f'  Rebuilt:  {rebuilt_name}')
    print()

    om = result.get('orig_map')
    rm = result.get('rebuilt_map')
    if om and rm:
        print(f'  Original layout:  freq@{om["freq_off"]:4d}  song@{om["song_off"]:4d}  '
              f'patt@{om["patt_off"]:4d}  instr@{om["patt_end"]:4d}  '
              f'ol@{om["first_ol_off"]:4d}  patterns@{om["first_patt_off"]:4d}')
        print(f'  Rebuilt layout:   freq@{rm["freq_off"]:4d}  song@{rm["song_off"]:4d}  '
              f'patt@{rm["patt_off"]:4d}  instr@{rm["patt_end"]:4d}  '
              f'ol@{rm["first_ol_off"]:4d}  patterns@{rm["first_patt_off"]:4d}')

        if om['freq_off'] != rm['freq_off']:
            print(f'  Player code size: orig={om["freq_off"]} rebuilt={rm["freq_off"]} '
                  f'(diff={om["freq_off"] - rm["freq_off"]})')
        if om['num_patt'] != rm['num_patt']:
            print(f'  Pattern count: orig={om["num_patt"]} rebuilt={rm["num_patt"]}')
        print()

    for s in result['sections']:
        name = s['name']
        if s['match']:
            size_str = f'{s["size"]:5d} bytes' if 'size' in s else ''
            note = s.get('note', '')
            extra = f'  ({note})' if note else ''
            print(f'  {name:35s} {size_str}  OK{extra}')
        elif 'orig_size' in s and 'total_diffs' not in s:
            note = s.get('note', '')
            diffs = s.get('diffs_in_common', 0)
            extra = f'  ({note})' if note else ''
            if diffs > 0:
                print(f'  {name:35s} DIFFER  size: {s["orig_size"]} vs {s["rebuilt_size"]}, '
                      f'{diffs} diffs in common range{extra}')
            else:
                print(f'  {name:35s} DIFFER  size: {s["orig_size"]} vs {s["rebuilt_size"]}'
                      f' (content OK in common range){extra}')
        else:
            size = s.get('size', '?')
            diffs = s.get('total_diffs', '?')
            print(f'  {name:35s} {size:5d} bytes  DIFFER  '
                  f'{diffs} byte(s) wrong')
            if 'first_diff_at' in s and s['first_diff_at'] is not None:
                print(f'    First diff at byte {s["first_diff_at"]}: '
                      f'orig={s["orig_byte"]} rebuilt={s["rebuilt_byte"]}')
                if 'orig_context' in s:
                    print(f'    Orig:    {s["orig_context"]}')
                    print(f'    Rebuilt: {s["rebuilt_context"]}')

    if result['first_diff']:
        print(f'\n  First difference: {result["first_diff"]}')
    elif result['match']:
        print(f'\n  All data sections match perfectly.')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Compare data sections of original and rebuilt GT2 SIDs')
    parser.add_argument('original', help='Original SID file')
    parser.add_argument('rebuilt', nargs='?',
                        help='Rebuilt SID file (default: rebuild via pipeline)')
    parser.add_argument('--rebuild', action='store_true',
                        help='Rebuild the original through GT2 pipeline first')
    parser.add_argument('--duration', type=int, default=10,
                        help='Duration for pipeline test (default: 10)')
    args = parser.parse_args()

    if args.rebuilt is None or args.rebuild:
        # Rebuild through pipeline
        from gt2_test_pipeline import test_single
        print(f'Rebuilding {os.path.basename(args.original)} through pipeline...')
        r = test_single(args.original, args.duration, verbose=True)
        if r['status'] != 'ok':
            print(f'Pipeline failed: {r["status"]}')
            if 'error' in r:
                print(f'  Error: {r["error"]}')
            sys.exit(1)
        rebuilt_path = '/tmp/gt2_test_out.sid'
        print()
    else:
        rebuilt_path = args.rebuilt

    result = compare_data_sections(args.original, rebuilt_path)
    print_results(result, os.path.basename(args.original),
                  os.path.basename(rebuilt_path))

    sys.exit(0 if result['match'] else 1)


if __name__ == '__main__':
    main()
