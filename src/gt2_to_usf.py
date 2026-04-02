"""
gt2_to_usf.py - Convert GoatTracker V2 SID files to Universal Symbolic Format.

Uses sidxray to detect the actual instrument layout (ni, column count)
since the GT2 packer's conditional compilation means the layout varies per file.
Falls back to the gt_parser for patterns and orderlists (which work correctly).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import parse_goattracker_sid, parse_psid_header, find_freq_table
from usf import Song, Instrument, WaveTableStep, Pattern, NoteEvent
from gt2_parse_direct import parse_gt2_direct
from gt2_detect_version import detect_gt2_player_group


def gt2_to_usf(sid_path, trace_duration=10):
    """Convert a GoatTracker V2 SID file to USF Song."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    # Use gt_parser for patterns and orderlists (these work)
    parsed = parse_goattracker_sid(data)

    # Use direct parser for instrument columns and wave table
    layout = parse_gt2_direct(sid_path)

    header = parsed['header']

    # Detect player behavior group, FIRSTNOTE, and DEFAULTTEMPO from binary
    version_info = detect_gt2_player_group(sid_path)
    player_group = version_info['group'] if version_info else ''

    header_obj, binary, la = parse_psid_header(data)

    # Extract DEFAULTTEMPO from the binary: find LDA #xx / STA abs,X / LDA #$01
    # pattern in the init code (mt_initchn sets counter=1, tempo=DEFAULTTEMPO)
    default_tempo = 6  # GT2 default if not found
    ft_check = find_freq_table(binary, la)
    if ft_check:
        for i in range(ft_check[0] - 8):
            if (binary[i] == 0xA9 and binary[i + 2] == 0x9D and
                    binary[i + 5] == 0xA9 and binary[i + 6] == 0x01 and
                    binary[i + 7] == 0x9D):
                default_tempo = binary[i + 1] + 1  # stored as tempo-1 in the binary
                break
    ft = find_freq_table(binary, la)
    first_note = ft[1] if ft else 0

    song = Song(
        title=header['title'],
        author=header['author'],
        sid_model='6581',
        clock='PAL',
        tempo=default_tempo,
        first_note=first_note,
        gt2_player_group=player_group or '',
    )

    # Read instrument data from direct parser
    ni = layout['ni'] if layout else 5
    col_data = layout['col_data'] if layout else {}

    # Attach raw GT2 data for direct passthrough to packer.
    # Column data is already correctly extracted (1-based Y indexing).
    # Table data starts at operand address — we pass it raw and let
    # the packer handle the -1 addressing.
    if layout:
        # Populate shared wave table from raw bytes.
        # Use wave_size (not len(wave_left)) to exclude the ni padding bytes
        # that gt2_parse_direct appends past the actual table data.
        raw_wl = layout.get('wave_left', b'')
        raw_wr = layout.get('wave_right', b'')
        wt_size = layout.get('wave_size', 0)
        if raw_wl and raw_wr:
            size = wt_size if wt_size > 0 else min(len(raw_wl), len(raw_wr))
            song.shared_wave_table = [(raw_wl[i], raw_wr[i]) for i in range(size)]

        # Populate shared pulse/filter tables using exact sizes from parser
        raw_pl = layout.get('pulse_left', b'')
        raw_pr = layout.get('pulse_right', b'')
        pt_size = layout.get('pulse_size', 0)
        if raw_pl and raw_pr:
            size = pt_size if pt_size > 0 else min(len(raw_pl), len(raw_pr))
            song.shared_pulse_table = [(raw_pl[i], raw_pr[i]) for i in range(size)]

        raw_fl = layout.get('filter_left', b'')
        raw_fr = layout.get('filter_right', b'')
        ft_size = layout.get('filter_size', 0)
        if raw_fl and raw_fr:
            size = ft_size if ft_size > 0 else min(len(raw_fl), len(raw_fr))
            song.shared_filter_table = [(raw_fl[i], raw_fr[i]) for i in range(size)]

        # Populate speed table from raw bytes
        raw_sl = layout.get('speed_left', b'')
        raw_sr = layout.get('speed_right', b'')
        st_size = layout.get('speed_size', 0)
        if raw_sl and raw_sr and st_size > 0:
            from usf import SpeedTableEntry
            for i in range(st_size):
                song.speed_table.append(SpeedTableEntry(left=raw_sl[i], right=raw_sr[i]))

    # Build instruments from column data — no raw passthrough
    for y in range(ni):
        def col(name, default=0):
            vals = col_data.get(name, [])
            return vals[y] if y < len(vals) else default

        ad = col('ad')
        sr = col('sr')
        wp = col('wave_ptr')
        fw_byte = col('first_wave')
        gt_byte = col('gate_timer', 2)
        vp = col('vib_param')
        vd = col('vib_delay')
        pp = col('pulse_ptr')
        fp = col('filter_ptr')

        # Determine waveform from first_wave byte
        if fw_byte in (0, 0xFE, 0xFF):
            waveform = 'pulse'
            fw = fw_byte  # preserve exact value for roundtrip
        else:
            wave_bits = (fw_byte >> 4) & 0xF
            waveform = {1: 'tri', 2: 'saw', 4: 'pulse', 8: 'noise'}.get(wave_bits, 'pulse')
            fw = fw_byte

        # Hard restart method
        hr = 'none' if gt_byte & 0x80 else 'gate'

        # Build wave table from extracted binary data
        wt = []
        wl = layout.get('wave_left', b'') if layout else b''
        wr = layout.get('wave_right', b'') if layout else b''
        if wp > 0 and wp <= len(wl):
            idx = wp - 1
            while idx < len(wl) and len(wt) < 64:
                left = wl[idx]
                right = wr[idx] if idx < len(wr) else 0x80

                if left == 0xFF:
                    if right > 0:
                        loop_target = max(0, right - wp)
                        wt.append(WaveTableStep(is_loop=True, loop_target=loop_target))
                    break
                elif left < 0x10:
                    if right == 0x00:
                        wt.append(WaveTableStep(delay=left, keep_freq=True))
                    elif right < 0x80:
                        wt.append(WaveTableStep(delay=left, absolute_note=right))
                    else:
                        rel = right if right < 0xC0 else right - 0x100
                        wt.append(WaveTableStep(delay=left, note_offset=rel - 0x80))
                else:
                    if right == 0x00:
                        wt.append(WaveTableStep(waveform=left, keep_freq=True))
                    elif right < 0x80:
                        wt.append(WaveTableStep(waveform=left, absolute_note=right))
                    else:
                        rel = right if right < 0xC0 else right - 0x100
                        wt.append(WaveTableStep(waveform=left, note_offset=rel - 0x80))
                idx += 1

        if not wt:
            default_fw = fw if fw > 0 else 0x41
            wt = [WaveTableStep(waveform=default_fw, note_offset=0),
                  WaveTableStep(is_loop=True, loop_target=0)]

        inst = Instrument(
            id=y,
            ad=ad,
            sr=sr,
            waveform=waveform,
            first_wave=fw,
            hr_method=hr,
            gate_timer=gt_byte & 0x3F,
            legato=bool(gt_byte & 0x40),
            wave_ptr=wp,
            vib_speed_idx=vp,
            vib_delay=vd,
            wave_table=wt,
            pulse_ptr=pp,
            filter_ptr=fp,
        )
        inst._gate_timer_raw = gt_byte
        song.instruments.append(inst)

    # NOTE: Some instruments have pulse_ptr/filter_ptr values that reference
    # entries beyond the table size. These are stale pointers from greloc.c
    # stripping unused table entries. We preserve them because they're part
    # of the original column data and changing them affects the binary layout.

    # Convert patterns
    for pi, gt_patt in enumerate(parsed['patterns']):
        patt = Pattern(id=pi)
        for row in gt_patt:
            note_type = row.get('note', 'REST')
            inst_num = row.get('instrument')
            if inst_num is not None:
                inst_num -= 1  # GT2 pattern bytes are 1-based

            cmd = row.get('command')  # None = no command, 0 = effect 0 (instrvib)
            cmd_val = row.get('param') or 0

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
    if parsed['orderlists']:
        channels = parsed['orderlists'][0]
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
                    count = entry.get('count', 1)
                    if ol:
                        repeated = ol[-1:]
                        for _ in range(count - 1):
                            ol.extend(repeated)
            song.orderlists[vi] = ol

    # Extract orderlist loop points from the original binary.
    # The byte after $FF is a byte OFFSET into the orderlist. We convert
    # it to a PATTERN ENTRY INDEX so USF is position-independent.
    if ft:
        freq_end = ft[0] + ft[2] * 2
        songs_count = header_obj['songs']
        se = songs_count * 3
        if freq_end + se * 2 < len(binary):
            st_lo = [binary[freq_end + i] for i in range(se)]
            st_hi = [binary[freq_end + se + i] for i in range(se)]
            for vi in range(3):  # USF currently only handles subtune 0
                addr = st_lo[vi] | (st_hi[vi] << 8)
                off = addr - la
                # Walk the orderlist bytes, mapping byte positions to entry indices
                byte_to_entry = {}
                entry_idx = 0
                pos = 0
                while off + pos < len(binary):
                    byte = binary[off + pos]
                    if byte == 0xFF:
                        restart_byte = binary[off + pos + 1] if off + pos + 1 < len(binary) else 0
                        # Convert byte offset to entry index
                        song.orderlist_restart[vi] = byte_to_entry.get(restart_byte, 0)
                        break
                    elif byte >= 0xE0:  # transpose marker
                        pos += 1
                        continue  # doesn't count as an entry
                    elif byte >= 0xD0:  # repeat marker
                        pos += 1
                        continue  # repeat applies to previous entry
                    else:  # pattern ID
                        byte_to_entry[pos] = entry_idx
                        entry_idx += 1
                        pos += 1

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
