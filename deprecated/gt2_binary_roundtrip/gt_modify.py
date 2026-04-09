"""
gt_modify.py - Modify GoatTracker V2 SID files.

Takes a GT2 SID, applies modifications to the music data
(transpose, instrument swap, etc.), and outputs a new valid SID.

Uses coarse binary split: player blob stays unchanged, only the
data section is modified. The player code references absolute addresses,
so address-sensitive modifications (adding/removing data) are not
supported — only in-place value changes.
"""

import struct
import subprocess
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import (parse_psid_header, find_freq_table, collect_abs_addresses,
                       unpack_pattern, FIRSTNOTE, LASTNOTE, REST, KEYOFF, KEYON,
                       FIRSTPACKEDREST, FX, FXONLY, ENDPATT)


def load_gt2_sid(sid_path):
    """Load and parse a GT2 SID file."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    header_bytes = data[:124]
    header, binary, load_addr = parse_psid_header(data)
    ft = find_freq_table(binary, load_addr)
    if ft is None:
        raise ValueError("Could not find GoatTracker frequency table")

    freq_off, first_note, num_notes, lo_first = ft
    freq_end = freq_off + num_notes * 2
    songs = header['songs']
    se = songs * 3

    addrs = sorted(set(a for a in collect_abs_addresses(binary, load_addr, 0, freq_off)
                       if a >= load_addr + freq_end))

    # Find song table
    song_lo = None
    for a in addrs:
        if a + se in addrs:
            song_lo = a
            break
    if song_lo is None:
        raise ValueError("Could not find song table")

    # Find pattern table
    patt_lo = patt_hi = None
    num_patt = 0
    for a in addrs:
        if a <= song_lo + se:
            continue
        for n in range(1, 256):
            if a + n in addrs:
                patt_lo = a
                patt_hi = a + n
                num_patt = n
                break
        if patt_lo:
            break
    if patt_lo is None:
        raise ValueError("Could not find pattern table")

    # Read pattern addresses
    pl_off = patt_lo - load_addr
    ph_off = patt_hi - load_addr
    patt_addrs = []
    for j in range(num_patt):
        patt_addrs.append(binary[pl_off + j] | (binary[ph_off + j] << 8))

    return {
        'header_bytes': header_bytes,
        'header': header,
        'load_addr_bytes': data[124:126],
        'binary': bytearray(binary),
        'load_addr': load_addr,
        'freq_off': freq_off,
        'freq_end': freq_end,
        'first_note': first_note,
        'num_notes': num_notes,
        'songs': songs,
        'song_lo': song_lo,
        'patt_lo': patt_lo,
        'patt_hi': patt_hi,
        'num_patt': num_patt,
        'patt_addrs': patt_addrs,
    }


def save_gt2_sid(sid, output_path):
    """Save a modified GT2 SID to file."""
    with open(output_path, 'wb') as f:
        f.write(sid['header_bytes'])
        f.write(sid['load_addr_bytes'])
        f.write(sid['binary'])


def transpose_patterns(sid, semitones):
    """Transpose all notes in all patterns by N semitones.

    Modifies the binary in-place. Only touches note bytes in pattern data.
    """
    binary = sid['binary']
    load_addr = sid['load_addr']
    patt_addrs = sid['patt_addrs']
    num_patt = sid['num_patt']

    sorted_pa = sorted(set(patt_addrs))
    modified = 0

    for idx, p_addr in enumerate(sorted_pa):
        off = p_addr - load_addr

        # Find max bytes for this pattern
        if idx + 1 < len(sorted_pa):
            max_bytes = sorted_pa[idx + 1] - p_addr
        else:
            max_bytes = len(binary) - off

        y = 0
        while y < max_bytes:
            b = binary[off + y]
            if b == ENDPATT:
                break

            # Instrument change
            if b < FX:
                y += 1
                if y >= max_bytes:
                    break
                b = binary[off + y]

            # FX / FXONLY
            if b < FIRSTNOTE:
                is_fxonly = (b >= FXONLY)
                cmd = b & 0x0F
                y += 1
                if cmd != 0 and y < max_bytes:
                    y += 1
                if is_fxonly:
                    if y < max_bytes and binary[off + y] == ENDPATT:
                        break
                    continue
                if y >= max_bytes:
                    break
                b = binary[off + y]

            # Note / rest / keyoff / keyon / packed rest
            if FIRSTNOTE <= b <= LASTNOTE:
                # Transpose the note
                new_note = b + semitones
                if FIRSTNOTE <= new_note <= LASTNOTE:
                    binary[off + y] = new_note
                    modified += 1
                y += 1
            elif b == REST or b == KEYOFF or b == KEYON:
                y += 1
            elif b >= FIRSTPACKEDREST:
                y += 1
            else:
                y += 1

            # Check for end of pattern
            if y < max_bytes and binary[off + y] == ENDPATT:
                break

    return modified


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Modify GoatTracker V2 SID files')
    parser.add_argument('input', help='Input SID file')
    parser.add_argument('-o', '--output', required=True, help='Output SID file')
    parser.add_argument('--transpose', type=int, help='Transpose all notes by N semitones')
    parser.add_argument('--verify', action='store_true', help='Compare register output with siddump')
    args = parser.parse_args()

    sid = load_gt2_sid(args.input)

    if args.transpose:
        n = transpose_patterns(sid, args.transpose)
        print(f'Transposed {n} notes by {args.transpose} semitones')

    save_gt2_sid(sid, args.output)
    print(f'Saved {args.output}')

    if args.verify:
        siddump = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'tools', 'siddump')
        if os.path.exists(siddump):
            r1 = subprocess.run([siddump, args.input, '--duration', '5'],
                              capture_output=True, text=True, timeout=30)
            r2 = subprocess.run([siddump, args.output, '--duration', '5'],
                              capture_output=True, text=True, timeout=30)
            if r1.returncode == 0 and r2.returncode == 0:
                l1 = r1.stdout.strip().split('\n')[2:]
                l2 = r2.stdout.strip().split('\n')[2:]
                matches = sum(1 for a, b in zip(l1, l2) if a == b)
                total = min(len(l1), len(l2))
                if args.transpose:
                    print(f'Register comparison: {matches}/{total} frames match (expected different due to transpose)')
                else:
                    print(f'Register comparison: {matches}/{total} frames match')


if __name__ == '__main__':
    main()
