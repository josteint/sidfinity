"""
gt2_to_usf.py - Convert GoatTracker V2 SID files to Universal Symbolic Format.

Since the SIDfinity player IS the GT2 player, this should be the easiest case.
GT2→USF→SID roundtrip validates the USF format itself.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import parse_goattracker_sid, parse_psid_header, find_freq_table, collect_abs_addresses
from usf import Song, Instrument, WaveTableStep, Pattern, NoteEvent


def extract_tables(data):
    """Extract wave/pulse/filter/speed tables from GT2 SID binary.

    GT2 packed layout after freq table:
      - Song table (lo[se], hi[se])  — or sometimes after instruments
      - Pattern table (lo[np], hi[np])
      - Instrument columns (9 x ni bytes): AD, SR, waveptr, pulseptr,
        filtptr, vibparam, vibdelay, gatetimer, firstwave
      - Wave table (left[n], right[n])
      - Pulse table (left[n], right[n])
      - Filter table (left[n], right[n])
      - Speed table (left[n], right[n])
      - Orderlists
      - Patterns

    The order of song/patt tables vs instrument columns varies. We find
    everything by matching address pairs referenced by the player code.

    Returns dict with raw table bytes keyed by name.
    """
    header, binary, load_addr = parse_psid_header(data)
    ft = find_freq_table(binary, load_addr)
    if ft is None:
        return {}

    freq_off, first_note, num_notes, lo_first = ft
    freq_end = freq_off + num_notes * 2
    songs = header['songs']
    se = songs * 3

    addrs = sorted(set(a for a in collect_abs_addresses(binary, load_addr, 0, freq_off)
                       if a >= load_addr + freq_end))
    if len(addrs) < 4:
        return {}

    # Find song table (pair with gap = songs*3)
    song_lo = None
    for a in addrs:
        if a + se in addrs:
            song_lo = a
            break
    if song_lo is None:
        return {}

    # Find pattern table (pair after song table)
    patt_lo = None
    for a in addrs:
        if a <= song_lo + se:
            continue
        for n in range(1, 256):
            if a + n in addrs:
                patt_lo = a
                break
        if patt_lo:
            break

    # Instrument region: addresses between freq_end and song_lo
    instr_region = sorted(a for a in addrs if load_addr + freq_end <= a < song_lo)
    if len(instr_region) < 2:
        return {}

    ni = instr_region[1] - instr_region[0]
    if ni < 1 or ni > 63:
        return {}

    # Compute instrument column addresses (stride ni from first)
    first_col = instr_region[0]
    instr_col_addrs = set()
    for k in range(9):
        instr_col_addrs.add(first_col + k * ni)
    instr_end_addr = first_col + 9 * ni

    # Table addresses: in instr_region but NOT instrument columns,
    # AND after the instrument columns
    table_addrs = sorted(a for a in instr_region
                         if a >= instr_end_addr and a not in instr_col_addrs)

    # GT2 tables are accessed as pairs: left column at addr A, right at addr A+1
    # via LDA table,Y and LDA table+1,Y. Both A and A+1 appear in the address list.
    # The ACTUAL table pairs are: wave(left, right), pulse(left, right), etc.
    # Left and right are stored as separate contiguous arrays.
    # Find pairs: addresses where addr and addr+1 are both referenced.
    pairs = []
    seen = set()
    for a in table_addrs:
        if a in seen:
            continue
        if a + 1 in set(table_addrs):
            # This is a left/right pair accessed via LDA x,Y / LDA x+1,Y
            # Find the size: gap to next pair or to song_lo
            remaining = [x for x in table_addrs if x > a + 1]
            if remaining:
                next_start = remaining[0]
                # But next_start might be part of the SAME table (right column)
                # The right column = left column + (next_pair_start - left_start) / 2? No.
                # Actually in GT2, LDA table,Y is left and LDA table+1,Y is NOT table+1
                # It's a SEPARATE address: mt_notetbl. Let me reconsider.
                pass

            pairs.append(a)
            seen.add(a)
            seen.add(a + 1)

    # Simpler approach: the table addresses (after instruments, before song table)
    # are the left/right column bases. They come in pairs where consecutive
    # addresses have a gap > 1 (the table size). The +1 references are just
    # right-column accesses.
    #
    # Filter out the +1 references: keep only addresses where addr-1 is NOT in the set
    clean_addrs = sorted(a for a in table_addrs if (a - 1) not in set(table_addrs))

    tables = {}
    # GT2 table order: wave_l, wave_r, pulse_l, pulse_r, filt_l, filt_r, speed_l, speed_r
    names = ['wave_left', 'wave_right', 'pulse_left', 'pulse_right',
             'filter_left', 'filter_right', 'speed_left', 'speed_right']

    endpoints = clean_addrs + [song_lo]
    for idx in range(min(len(clean_addrs), len(names))):
        a = clean_addrs[idx]
        size = endpoints[idx + 1] - a
        off = a - load_addr
        if 0 <= off and off + size <= len(binary):
            tables[names[idx]] = bytes(binary[off:off + size])

    return tables


def read_instrument_columns(data):
    """Read instrument columns from GT2 SID binary.

    GT2 packer strips unused columns (NOPULSE, NOFILTER, etc.), so the
    number of columns varies. We identify column bases by looking at
    player code references and filtering out mid-column addresses.
    """
    header, binary, load_addr = parse_psid_header(data)
    ft = find_freq_table(binary, load_addr)
    if ft is None:
        return [], 0

    freq_off, first_note, num_notes, lo_first = ft
    freq_end = freq_off + num_notes * 2
    songs = header['songs']
    se = songs * 3

    addrs = sorted(set(a for a in collect_abs_addresses(binary, load_addr, 0, freq_off)
                       if a >= load_addr + freq_end))
    if len(addrs) < 2:
        return [], 0

    # Find song table to bound the instrument region
    song_lo = None
    for a in addrs:
        if a + se in addrs:
            song_lo = a
            break
    if song_lo is None:
        return [], 0

    # Instrument addresses: between freq_end and song_lo
    instr_addrs = sorted(a for a in addrs if load_addr + freq_end <= a < song_lo)
    if len(instr_addrs) < 2:
        return [], 0

    ni = instr_addrs[1] - instr_addrs[0]
    if ni < 1 or ni > 63:
        return [], 0

    # Filter out mid-column refs: keep only addresses that are at stride-ni
    # boundaries from the first address
    first = instr_addrs[0]
    col_bases = []
    for a in instr_addrs:
        offset_from_first = a - first
        if offset_from_first % ni == 0:
            col_bases.append(a)

    # The GT2 column order (when present):
    # AD, SR, wave_ptr, pulse_ptr, filter_ptr, vib_param, vib_delay, gate_timer, first_wave
    # Not all may be present. We map by position.
    col_names = ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr',
                 'vib_param', 'vib_delay', 'gate_timer', 'first_wave']

    instruments = []
    for i in range(ni):
        inst = {'index': i}
        for ci, name in enumerate(col_names):
            if ci < len(col_bases):
                off = col_bases[ci] - load_addr + i
                if off < len(binary):
                    inst[name] = binary[off]
                else:
                    inst[name] = 0
            else:
                inst[name] = 0
        instruments.append(inst)

    return instruments, ni


def gt2_to_usf(sid_path):
    """Convert a GoatTracker V2 SID file to USF Song."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    parsed = parse_goattracker_sid(data)
    tables = extract_tables(data)

    header = parsed['header']
    song = Song(
        title=header['title'],
        author=header['author'],
        sid_model='6581',
        clock='PAL',
        tempo=6,
    )

    # Convert instruments
    for gt_inst in parsed['instruments']:
        ad = gt_inst.get('ad', 0)
        sr = gt_inst.get('sr', 0)
        fw = gt_inst.get('first_wave', 0x41)
        gt = gt_inst.get('gate_timer', 2)
        wp = gt_inst.get('wave_ptr', 0)

        wave_bits = (fw >> 4) & 0xF
        waveform = {1: 'tri', 2: 'saw', 4: 'pulse', 8: 'noise'}.get(wave_bits, 'pulse')

        hr = 'none' if gt >= 0x80 else 'gate'

        # Build wave table from raw table data
        wt = []
        wl = tables.get('wave_left', b'')
        wr = tables.get('wave_right', b'')
        if wp > 0 and wp <= len(wl):
            idx = wp - 1  # GT2 wave table is 1-based
            while idx < len(wl) and len(wt) < 64:
                left = wl[idx]
                right = wr[idx] if idx < len(wr) else 0x80

                if left == 0xFF:
                    # Loop: right column has loop target (1-based)
                    loop_target = max(0, (right - 1) - (wp - 1))
                    wt.append(WaveTableStep(is_loop=True, loop_target=loop_target))
                    break
                else:
                    if right >= 0x80:
                        # Relative note offset
                        note_off = right - 0x80
                        wt.append(WaveTableStep(waveform=left, note_offset=note_off))
                    elif right > 0:
                        # Absolute note
                        wt.append(WaveTableStep(waveform=left, absolute_note=right))
                    else:
                        wt.append(WaveTableStep(waveform=left, note_offset=0))
                idx += 1

        if not wt:
            wt = [
                WaveTableStep(waveform=fw, note_offset=0),
                WaveTableStep(is_loop=True, loop_target=0),
            ]

        inst = Instrument(
            id=len(song.instruments),
            ad=ad,
            sr=sr,
            waveform=waveform,
            first_wave=fw if fw not in (0x00, 0xFE, 0xFF) else -1,
            hr_method=hr,
            gate_timer=gt & 0x3F,
            legato=bool(gt & 0x40),
            vib_speed_idx=gt_inst.get('vib_param', 0),
            vib_delay=gt_inst.get('vib_delay', 0),
            wave_table=wt,
        )
        song.instruments.append(inst)

    # Convert patterns: GT2 unpacked rows → USF NoteEvents
    for pi, gt_patt in enumerate(parsed['patterns']):
        patt = Pattern(id=pi)
        for row in gt_patt:
            note_type = row.get('note', 'REST')
            inst_num = row.get('instrument')
            if inst_num is not None:
                inst_num -= 1  # GT2 is 1-based

            cmd = row.get('command', 0) or 0
            cmd_val = row.get('param', 0) or 0

            ev_kwargs = dict(
                duration=1,
                instrument=inst_num if inst_num is not None else -1,
                command=cmd,
                command_val=cmd_val,
            )

            if note_type == 'REST':
                patt.events.append(NoteEvent(type='rest', **ev_kwargs))
            elif note_type == 'KEYOFF':
                patt.events.append(NoteEvent(type='off', **ev_kwargs))
            elif note_type == 'KEYON':
                patt.events.append(NoteEvent(type='on', **ev_kwargs))
            elif 'note_num' in row:
                patt.events.append(NoteEvent(type='note', note=row['note_num'], **ev_kwargs))

        song.patterns.append(patt)

    # Convert orderlists
    # Parser returns: orderlists[song_idx] = list of 3 channel dicts
    # Each channel dict has 'entries' list with type/pattern/transpose/repeat
    if parsed['orderlists']:
        channels = parsed['orderlists'][0]  # song 0
        for vi in range(min(3, len(channels))):
            ol = []
            current_trans = 0
            for entry in channels[vi].get('entries', []):
                etype = entry.get('type')
                if etype == 'transpose':
                    current_trans = entry.get('value', 0)
                elif etype == 'pattern':
                    ol.append((entry['pattern'], current_trans))
                elif etype == 'repeat':
                    # Repeat: expand the previous N patterns
                    count = entry.get('count', 1)
                    if ol:
                        repeated = ol[-1:]
                        for _ in range(count - 1):
                            ol.extend(repeated)
            song.orderlists[vi] = ol

    return song


def main():
    from usf import tokenize, to_text

    if len(sys.argv) < 2:
        print("Usage: gt2_to_usf.py <file.sid>")
        sys.exit(1)

    song = gt2_to_usf(sys.argv[1])
    tokens = tokenize(song)
    print(f'Token count: {len(tokens)}')
    print(f'Instruments: {len(song.instruments)}')
    print(f'Patterns: {len(song.patterns)}')
    print(f'Orderlists: {[len(ol) for ol in song.orderlists]}')
    print()
    print(to_text(tokens))


if __name__ == '__main__':
    main()
