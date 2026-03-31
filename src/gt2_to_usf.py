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

    Returns dict with table data, or empty dict.
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
    if len(addrs) < 2:
        return {}

    # Find song table (first pair with gap = songs*3)
    song_lo_addr = None
    for a in addrs:
        if a + se in addrs:
            song_lo_addr = a
            break
    if song_lo_addr is None:
        return {}
    song_hi_addr = song_lo_addr + se

    # Find pattern table (first address pair after song table with matching gap)
    patt_lo_addr = patt_hi_addr = None
    num_patt = 0
    for a in addrs:
        if a <= song_hi_addr:
            continue
        for n in range(1, 256):
            if a + n in addrs:
                patt_lo_addr = a
                patt_hi_addr = a + n
                num_patt = n
                break
        if patt_lo_addr:
            break

    # Instrument columns: between freq_end and song_lo
    instr_addrs = sorted(a for a in addrs
                         if load_addr + freq_end <= a < song_lo_addr)
    num_instr = 0
    if len(instr_addrs) >= 2:
        num_instr = instr_addrs[1] - instr_addrs[0]

    # Tables: between last instrument column and song table, or referenced addrs in that range
    if not instr_addrs or not num_instr:
        return {}

    last_instr_end = instr_addrs[-1] - load_addr + num_instr
    # Table addresses are referenced by player code and fall between last instrument and song table
    table_addrs = sorted(a for a in addrs
                         if load_addr + last_instr_end <= a < song_lo_addr)

    # GT2 table layout: wave_left, wave_right, pulse_left, pulse_right,
    #                    filter_left, filter_right, speed_left, speed_right
    # Each pair has the same size (they're indexed together)
    tables = {}
    if len(table_addrs) >= 2:
        # Identify pairs by matching sizes
        pairs = []
        i = 0
        while i < len(table_addrs) - 1:
            a1 = table_addrs[i]
            a2 = table_addrs[i + 1]
            size = a2 - a1
            off1 = a1 - load_addr
            pairs.append({
                'addr': a1,
                'size': size,
                'data': bytes(binary[off1:off1 + size]),
            })
            i += 1
        # Last entry goes to song table
        if table_addrs:
            last = table_addrs[-1]
            off = last - load_addr
            size = song_lo_addr - last
            pairs.append({
                'addr': last,
                'size': size,
                'data': bytes(binary[off:off + size]),
            })

        # Assign pairs to table types based on order
        names = ['wave_left', 'wave_right', 'pulse_left', 'pulse_right',
                 'filter_left', 'filter_right', 'speed_left', 'speed_right']
        for idx, name in enumerate(names):
            if idx < len(pairs):
                tables[name] = pairs[idx]['data']

    return tables


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
            hr_method=hr,
            gate_timer=gt & 0x7F if gt < 0x80 else 0,
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

            if note_type == 'REST':
                patt.events.append(NoteEvent(
                    type='rest', duration=1,
                    instrument=inst_num if inst_num is not None else -1))
            elif note_type == 'KEYOFF':
                patt.events.append(NoteEvent(
                    type='off', duration=1,
                    instrument=inst_num if inst_num is not None else -1))
            elif note_type == 'KEYON':
                patt.events.append(NoteEvent(
                    type='on', duration=1,
                    instrument=inst_num if inst_num is not None else -1))
            elif 'note_num' in row:
                patt.events.append(NoteEvent(
                    type='note', note=row['note_num'], duration=1,
                    instrument=inst_num if inst_num is not None else -1))

        song.patterns.append(patt)

    # Convert orderlists
    for vi in range(3):
        if vi < len(parsed['orderlists']):
            ol = []
            for entry in parsed['orderlists'][vi]:
                patt_id = entry.get('pattern', 0)
                trans = entry.get('transpose', 0)
                if entry.get('type') == 'repeat':
                    break
                ol.append((patt_id, trans))
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
