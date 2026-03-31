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
from sidxray.gt2_detect import detect_gt2_layout


def gt2_to_usf(sid_path, trace_duration=10):
    """Convert a GoatTracker V2 SID file to USF Song."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    # Use gt_parser for patterns and orderlists (these work)
    parsed = parse_goattracker_sid(data)

    # Use sidxray to detect instrument layout (ni, columns)
    layout = detect_gt2_layout(sid_path, trace_duration)

    header = parsed['header']

    # Detect initial tempo from first SETTEMPO command in patterns
    initial_tempo = 6  # GT2 default
    for patt in parsed['patterns']:
        for row in patt:
            if row.get('command') == 15 and row.get('param'):
                val = row['param']
                if val < 0x80:  # global tempo (not channel-specific)
                    initial_tempo = val
                    break
        else:
            continue
        break

    song = Song(
        title=header['title'],
        author=header['author'],
        sid_model='6581',
        clock='PAL',
        tempo=initial_tempo,
    )

    # Read instrument data from detected layout
    ni = layout['ni'] if layout else 5
    columns = layout['columns'] if layout else {}
    num_cols = layout['num_columns'] if layout else 0

    # GT2 column order confirmed by disassembly (STA $D405/D406 mapping):
    # col 0 → SID AD ($D405), col 1 → SID SR ($D406), col 2 → wave_ptr,
    # col 3 → first_wave, col 4+ → varies (pulse_ptr, filter_ptr, etc.)
    # Note: some columns may be stripped by FIXEDPARAMS/NOPULSE/NOFILTER.
    # The detected column count tells us how many are present.
    col_names = ['ad', 'sr', 'wave_ptr', 'first_wave', 'pulse_ptr',
                 'filter_ptr', 'vib_param', 'vib_delay', 'gate_timer']

    for y in range(ni):
        fields = {}
        for ci in range(min(num_cols, len(col_names))):
            if ci in columns and y < len(columns[ci]):
                fields[col_names[ci]] = columns[ci][y]

        ad = fields.get('ad', 0)
        sr = fields.get('sr', 0)
        wp = fields.get('wave_ptr', 0)
        fw_byte = fields.get('first_wave', 0)
        gt_byte = fields.get('gate_timer', 2)
        vp = fields.get('vib_param', 0)
        vd = fields.get('vib_delay', 0)

        # Determine waveform from first_wave byte
        if fw_byte in (0, 0xFE, 0xFF):
            waveform = 'pulse'
            fw = -1
        else:
            wave_bits = (fw_byte >> 4) & 0xF
            waveform = {1: 'tri', 2: 'saw', 4: 'pulse', 8: 'noise'}.get(wave_bits, 'pulse')
            fw = fw_byte

        # Hard restart method
        hr = 'none' if gt_byte >= 0x80 else 'gate'

        # Build wave table from extracted binary data
        wt = []
        wl = layout.get('wave_left', b'') if layout else b''
        wr = layout.get('wave_right', b'') if layout else b''
        if wp > 0 and wp < len(wl):
            idx = wp  # wave_ptr = Y value; array stored from operand, so index=Y
            while idx < len(wl) and len(wt) < 64:
                left = wl[idx]
                right = wr[idx] if idx < len(wr) else 0x80

                if left == 0xFF:
                    # Loop: right column has target (same indexing as wave_ptr)
                    loop_target = max(0, right - wp)
                    wt.append(WaveTableStep(is_loop=True, loop_target=loop_target))
                    break
                elif left < 0x10:
                    # Delay
                    wt.append(WaveTableStep(delay=left))
                else:
                    # Waveform + note
                    if right == 0x80:
                        wt.append(WaveTableStep(waveform=left, keep_freq=True))
                    elif right > 0x80:
                        wt.append(WaveTableStep(waveform=left, absolute_note=right - 0x81))
                    elif right >= 0x60:
                        wt.append(WaveTableStep(waveform=left, note_offset=right - 0x100))
                    else:
                        wt.append(WaveTableStep(waveform=left, note_offset=right))
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
            gate_timer=gt_byte & 0x3F if gt_byte < 0x80 else 0,
            legato=bool(gt_byte & 0x40) if num_cols > 7 else False,
            vib_speed_idx=vp,
            vib_delay=vd,
            wave_table=wt,
        )
        song.instruments.append(inst)

    # Convert patterns
    for pi, gt_patt in enumerate(parsed['patterns']):
        patt = Pattern(id=pi)
        for row in gt_patt:
            note_type = row.get('note', 'REST')
            inst_num = row.get('instrument')
            if inst_num is not None:
                inst_num -= 1  # GT2 pattern bytes are 1-based

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
