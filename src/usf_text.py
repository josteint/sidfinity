"""
usf_text.py - Lossless human-readable text serialization for USF Song objects.

Unlike the token format (designed for ML training, compact, lossy on metadata),
this format preserves every field of the Song dataclass for exact roundtripping.

Format: line-oriented, one element per line, sections delimited by headers.
All numeric values stored in decimal unless noted (hex prefixed with 0x).

Roundtrip guarantee: from_text(to_text(song)) produces an identical Song object.
"""

import sys
import os
import base64

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usf import (Song, Instrument, WaveTableStep, PulseTableStep,
                 FilterTableStep, SpeedTableEntry, Pattern, NoteEvent,
                 note_name, note_from_name)


# ============================================================
# Serialization: Song -> text
# ============================================================

def to_text(song: Song) -> str:
    """Serialize a Song to human-readable text. Lossless."""
    lines = []

    # Song header
    lines.append('[SONG]')
    lines.append(f'title = {song.title}')
    lines.append(f'author = {song.author}')
    lines.append(f'sid_model = {song.sid_model}')
    lines.append(f'clock = {song.clock}')
    lines.append(f'tempo = {song.tempo}')
    first_note = getattr(song, 'first_note', 0)
    lines.append(f'first_note = {first_note}')
    gt2_pg = getattr(song, 'gt2_player_group', '')
    if gt2_pg:
        lines.append(f'gt2_player_group = {gt2_pg}')

    # Frequency tables (base64 encoded if present)
    if song.freq_lo is not None:
        lines.append(f'freq_lo = {base64.b64encode(song.freq_lo).decode("ascii")}')
    if song.freq_hi is not None:
        lines.append(f'freq_hi = {base64.b64encode(song.freq_hi).decode("ascii")}')

    # Orderlist restart points
    ol_restart = getattr(song, 'orderlist_restart', [0, 0, 0])
    lines.append(f'orderlist_restart = {ol_restart[0]} {ol_restart[1]} {ol_restart[2]}')
    lines.append('')

    # Shared tables
    if song.shared_wave_table:
        lines.append('[SHARED_WAVE_TABLE]')
        for i, (l, r) in enumerate(song.shared_wave_table):
            lines.append(f'{i}: {l} {r}')
        lines.append('')

    if song.shared_pulse_table:
        lines.append('[SHARED_PULSE_TABLE]')
        for i, (l, r) in enumerate(song.shared_pulse_table):
            lines.append(f'{i}: {l} {r}')
        lines.append('')

    if song.shared_filter_table:
        lines.append('[SHARED_FILTER_TABLE]')
        for i, (l, r) in enumerate(song.shared_filter_table):
            lines.append(f'{i}: {l} {r}')
        lines.append('')

    # Speed table
    if song.speed_table:
        lines.append('[SPEED_TABLE]')
        for i, entry in enumerate(song.speed_table):
            lines.append(f'{i}: {entry.left} {entry.right}')
        lines.append('')

    # Instrument fields with defaults for older USF versions
    INST_FIELDS = [
        ('ad', 0x09), ('sr', 0x00), ('waveform', 'pulse'), ('first_wave', -1),
        ('gate_timer', 2), ('hr_method', 'gate'), ('legato', False),
        ('pulse_width', 0x0808), ('wave_ptr', 0), ('vib_speed_idx', 0),
        ('vib_delay', 0), ('pulse_ptr', 0), ('filter_ptr', 0),
    ]

    # Instruments
    for inst in song.instruments:
        lines.append(f'[INSTRUMENT {inst.id}]')
        for fname, fdefault in INST_FIELDS:
            val = getattr(inst, fname, fdefault)
            lines.append(f'{fname} = {val}')

        # Wave table
        if inst.wave_table:
            lines.append('  [WAVE_TABLE]')
            for si, step in enumerate(inst.wave_table):
                parts = [f'{si}:']
                parts.append(f'wf={step.waveform}')
                parts.append(f'off={step.note_offset}')
                parts.append(f'abs={step.absolute_note}')
                parts.append(f'loop={step.is_loop}')
                parts.append(f'lt={step.loop_target}')
                parts.append(f'delay={step.delay}')
                parts.append(f'kf={step.keep_freq}')
                lines.append('  ' + ' '.join(parts))
            lines.append('  [/WAVE_TABLE]')

        # Pulse table
        if inst.pulse_table:
            lines.append('  [PULSE_TABLE]')
            for si, step in enumerate(inst.pulse_table):
                parts = [f'{si}:']
                parts.append(f'set={step.is_set}')
                parts.append(f'val={step.value}')
                parts.append(f'lo={step.low_byte}')
                parts.append(f'dur={step.duration}')
                parts.append(f'loop={step.is_loop}')
                parts.append(f'lt={step.loop_target}')
                lines.append('  ' + ' '.join(parts))
            lines.append('  [/PULSE_TABLE]')

        # Filter table
        if inst.filter_table:
            lines.append('  [FILTER_TABLE]')
            for si, step in enumerate(inst.filter_table):
                parts = [f'{si}:']
                parts.append(f'type={step.type}')
                parts.append(f'val={step.value}')
                parts.append(f'dur={step.duration}')
                parts.append(f'loop={step.is_loop}')
                parts.append(f'lt={step.loop_target}')
                lines.append('  ' + ' '.join(parts))
            lines.append('  [/FILTER_TABLE]')

        lines.append('')

    # Patterns
    for patt in song.patterns:
        lines.append(f'[PATTERN {patt.id}]')
        for ei, ev in enumerate(patt.events):
            # Format: idx: type note duration instrument command command_val
            cmd_str = 'None' if ev.command is None else str(ev.command)
            lines.append(f'{ei}: {ev.type} {ev.note} {ev.duration} {ev.instrument} {cmd_str} {ev.command_val}')
        lines.append('')

    # Orderlists
    for vi in range(3):
        lines.append(f'[ORDERLIST {vi}]')
        for oi, (pat_id, transpose) in enumerate(song.orderlists[vi]):
            lines.append(f'{oi}: {pat_id} {transpose}')
        lines.append('')

    lines.append('[/SONG]')
    return '\n'.join(lines)


# ============================================================
# Deserialization: text -> Song
# ============================================================

def from_text(text: str) -> Song:
    """Deserialize a Song from text. Inverse of to_text()."""
    song = Song()
    lines = text.split('\n')
    i = 0
    current_instrument = None
    current_sub_table = None  # 'wave', 'pulse', 'filter'

    def finalize_instrument():
        nonlocal current_instrument, current_sub_table
        if current_instrument is not None:
            song.instruments.append(current_instrument)
            current_instrument = None
            current_sub_table = None

    def read_indexed_block(start):
        """Read lines of form 'idx: ...' until empty line or section header."""
        entries = []
        j = start
        while j < len(lines):
            sl = lines[j].strip()
            if not sl or sl.startswith('['):
                break
            entries.append(sl)
            j += 1
        return entries, j

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == '[SONG]':
            i += 1
            continue
        elif stripped == '[/SONG]':
            finalize_instrument()
            break

        # Top-level sections that end the current instrument
        elif stripped == '[SHARED_WAVE_TABLE]':
            finalize_instrument()
            entries, i = read_indexed_block(i + 1)
            song.shared_wave_table = []
            for e in entries:
                vals = e.split(':')[1].strip().split()
                song.shared_wave_table.append((int(vals[0]), int(vals[1])))
            continue

        elif stripped == '[SHARED_PULSE_TABLE]':
            finalize_instrument()
            entries, i = read_indexed_block(i + 1)
            song.shared_pulse_table = []
            for e in entries:
                vals = e.split(':')[1].strip().split()
                song.shared_pulse_table.append((int(vals[0]), int(vals[1])))
            continue

        elif stripped == '[SHARED_FILTER_TABLE]':
            finalize_instrument()
            entries, i = read_indexed_block(i + 1)
            song.shared_filter_table = []
            for e in entries:
                vals = e.split(':')[1].strip().split()
                song.shared_filter_table.append((int(vals[0]), int(vals[1])))
            continue

        elif stripped == '[SPEED_TABLE]':
            finalize_instrument()
            entries, i = read_indexed_block(i + 1)
            song.speed_table = []
            for e in entries:
                vals = e.split(':')[1].strip().split()
                song.speed_table.append(SpeedTableEntry(left=int(vals[0]), right=int(vals[1])))
            continue

        elif stripped.startswith('[INSTRUMENT '):
            finalize_instrument()
            inst_id = int(stripped.split()[1].rstrip(']'))
            current_instrument = Instrument(id=inst_id)
            current_sub_table = None
            i += 1
            continue

        elif stripped.startswith('[PATTERN '):
            finalize_instrument()
            pat_id = int(stripped.split()[1].rstrip(']'))
            patt = Pattern(id=pat_id)
            entries, i = read_indexed_block(i + 1)
            for e in entries:
                vals = e.split(':')[1].strip().split()
                patt.events.append(NoteEvent(
                    type=vals[0], note=int(vals[1]), duration=int(vals[2]),
                    instrument=int(vals[3]),
                    command=None if vals[4] == 'None' else int(vals[4]),
                    command_val=int(vals[5])))
            song.patterns.append(patt)
            continue

        elif stripped.startswith('[ORDERLIST '):
            finalize_instrument()
            vi = int(stripped.split()[1].rstrip(']'))
            entries, i = read_indexed_block(i + 1)
            ol = []
            for e in entries:
                vals = e.split(':')[1].strip().split()
                ol.append((int(vals[0]), int(vals[1])))
            song.orderlists[vi] = ol
            continue

        # Sub-tables within instruments
        elif stripped == '[WAVE_TABLE]':
            current_sub_table = 'wave'
            i += 1
            continue
        elif stripped == '[/WAVE_TABLE]':
            current_sub_table = None
            i += 1
            continue
        elif stripped == '[PULSE_TABLE]':
            current_sub_table = 'pulse'
            i += 1
            continue
        elif stripped == '[/PULSE_TABLE]':
            current_sub_table = None
            i += 1
            continue
        elif stripped == '[FILTER_TABLE]':
            current_sub_table = 'filter'
            i += 1
            continue
        elif stripped == '[/FILTER_TABLE]':
            current_sub_table = None
            i += 1
            continue

        # Key-value pairs
        elif '=' in stripped and not stripped[0].isdigit():
            key, val = stripped.split('=', 1)
            key = key.strip()
            val = val.strip()

            if current_instrument is None:
                if key == 'title':
                    song.title = val
                elif key == 'author':
                    song.author = val
                elif key == 'sid_model':
                    song.sid_model = val
                elif key == 'clock':
                    song.clock = val
                elif key == 'tempo':
                    song.tempo = int(val)
                elif key == 'first_note':
                    if hasattr(song, 'first_note'):
                        song.first_note = int(val)
                elif key == 'gt2_player_group':
                    if hasattr(song, 'gt2_player_group'):
                        song.gt2_player_group = val
                elif key == 'freq_lo':
                    song.freq_lo = base64.b64decode(val)
                elif key == 'freq_hi':
                    song.freq_hi = base64.b64decode(val)
                elif key == 'orderlist_restart':
                    if hasattr(song, 'orderlist_restart'):
                        parts = val.split()
                        song.orderlist_restart = [int(parts[0]), int(parts[1]), int(parts[2])]
            else:
                # Instrument fields — only set if the field exists on the class
                INT_FIELDS = {'ad', 'sr', 'first_wave', 'gate_timer',
                              'pulse_width', 'wave_ptr', 'vib_speed_idx',
                              'vib_delay', 'pulse_ptr', 'filter_ptr'}
                BOOL_FIELDS = {'legato'}
                STR_FIELDS = {'waveform', 'hr_method'}
                if not hasattr(current_instrument, key):
                    pass  # field not in this version of Instrument
                elif key in INT_FIELDS:
                    setattr(current_instrument, key, int(val))
                elif key in BOOL_FIELDS:
                    setattr(current_instrument, key, val == 'True')
                elif key in STR_FIELDS:
                    setattr(current_instrument, key, val)

        # Indexed sub-table entries within instruments
        elif current_instrument and current_sub_table and stripped[0].isdigit():
            kvs = {}
            for token in stripped.split(':')[1].strip().split():
                k, v = token.split('=', 1)
                kvs[k] = v

            if current_sub_table == 'wave':
                current_instrument.wave_table.append(WaveTableStep(
                    waveform=int(kvs['wf']),
                    note_offset=int(kvs['off']),
                    absolute_note=int(kvs['abs']),
                    is_loop=kvs['loop'] == 'True',
                    loop_target=int(kvs['lt']),
                    delay=int(kvs['delay']),
                    keep_freq=kvs['kf'] == 'True',
                ))
            elif current_sub_table == 'pulse':
                current_instrument.pulse_table.append(PulseTableStep(
                    is_set=kvs['set'] == 'True',
                    value=int(kvs['val']),
                    low_byte=int(kvs['lo']),
                    duration=int(kvs['dur']),
                    is_loop=kvs['loop'] == 'True',
                    loop_target=int(kvs['lt']),
                ))
            elif current_sub_table == 'filter':
                current_instrument.filter_table.append(FilterTableStep(
                    type=kvs['type'],
                    value=int(kvs['val']),
                    duration=int(kvs['dur']),
                    is_loop=kvs['loop'] == 'True',
                    loop_target=int(kvs['lt']),
                ))

        i += 1

    # Finalize last instrument if pending (no [/SONG] encountered)
    finalize_instrument()

    return song


# ============================================================
# Comparison helper
# ============================================================

def songs_equal(a: Song, b: Song) -> list:
    """Compare two Song objects field by field. Return list of differences."""
    diffs = []

    # Top-level scalar fields
    for field_name in ['title', 'author', 'sid_model', 'clock', 'tempo']:
        va = getattr(a, field_name)
        vb = getattr(b, field_name)
        if va != vb:
            diffs.append(f'song.{field_name}: {va!r} != {vb!r}')

    # Optional fields (may not exist in older USF versions)
    for field_name, default in [('first_note', 0), ('gt2_player_group', '')]:
        va = getattr(a, field_name, default)
        vb = getattr(b, field_name, default)
        if va != vb:
            diffs.append(f'song.{field_name}: {va!r} != {vb!r}')

    # Bytes fields
    for field_name in ['freq_lo', 'freq_hi']:
        va = getattr(a, field_name, None)
        vb = getattr(b, field_name, None)
        if va != vb:
            diffs.append(f'song.{field_name}: differs')

    # Orderlist restart
    ol_a = getattr(a, 'orderlist_restart', [0, 0, 0])
    ol_b = getattr(b, 'orderlist_restart', [0, 0, 0])
    if ol_a != ol_b:
        diffs.append(f'orderlist_restart: {ol_a} != {ol_b}')

    # Shared tables
    for tbl_name in ['shared_wave_table', 'shared_pulse_table', 'shared_filter_table']:
        ta = getattr(a, tbl_name)
        tb = getattr(b, tbl_name)
        if ta != tb:
            diffs.append(f'{tbl_name}: {len(ta)} entries vs {len(tb)} entries')

    # Speed table
    if len(a.speed_table) != len(b.speed_table):
        diffs.append(f'speed_table: {len(a.speed_table)} vs {len(b.speed_table)}')
    else:
        for i, (sa, sb) in enumerate(zip(a.speed_table, b.speed_table)):
            if sa.left != sb.left or sa.right != sb.right:
                diffs.append(f'speed_table[{i}]: ({sa.left},{sa.right}) != ({sb.left},{sb.right})')

    # Instruments
    if len(a.instruments) != len(b.instruments):
        diffs.append(f'instruments: {len(a.instruments)} vs {len(b.instruments)}')
    else:
        for ii, (ia, ib) in enumerate(zip(a.instruments, b.instruments)):
            for f in ['id', 'ad', 'sr', 'waveform', 'first_wave', 'gate_timer',
                       'hr_method', 'legato', 'pulse_width', 'wave_ptr',
                       'vib_speed_idx', 'vib_delay', 'pulse_ptr', 'filter_ptr']:
                va = getattr(ia, f, None)
                vb = getattr(ib, f, None)
                if va != vb:
                    diffs.append(f'inst[{ii}].{f}: {va!r} != {vb!r}')

            # Wave table
            if len(ia.wave_table) != len(ib.wave_table):
                diffs.append(f'inst[{ii}].wave_table: {len(ia.wave_table)} vs {len(ib.wave_table)} steps')
            else:
                for si, (sa, sb) in enumerate(zip(ia.wave_table, ib.wave_table)):
                    for f in ['waveform', 'note_offset', 'absolute_note', 'is_loop',
                               'loop_target', 'delay', 'keep_freq']:
                        va = getattr(sa, f)
                        vb = getattr(sb, f)
                        if va != vb:
                            diffs.append(f'inst[{ii}].wt[{si}].{f}: {va!r} != {vb!r}')

            # Pulse table
            if len(ia.pulse_table) != len(ib.pulse_table):
                diffs.append(f'inst[{ii}].pulse_table: {len(ia.pulse_table)} vs {len(ib.pulse_table)} steps')
            else:
                for si, (sa, sb) in enumerate(zip(ia.pulse_table, ib.pulse_table)):
                    for f in ['is_set', 'value', 'low_byte', 'duration', 'is_loop', 'loop_target']:
                        va = getattr(sa, f)
                        vb = getattr(sb, f)
                        if va != vb:
                            diffs.append(f'inst[{ii}].pt[{si}].{f}: {va!r} != {vb!r}')

            # Filter table
            if len(ia.filter_table) != len(ib.filter_table):
                diffs.append(f'inst[{ii}].filter_table: {len(ia.filter_table)} vs {len(ib.filter_table)} steps')
            else:
                for si, (sa, sb) in enumerate(zip(ia.filter_table, ib.filter_table)):
                    for f in ['type', 'value', 'duration', 'is_loop', 'loop_target']:
                        va = getattr(sa, f)
                        vb = getattr(sb, f)
                        if va != vb:
                            diffs.append(f'inst[{ii}].ft[{si}].{f}: {va!r} != {vb!r}')

    # Patterns
    if len(a.patterns) != len(b.patterns):
        diffs.append(f'patterns: {len(a.patterns)} vs {len(b.patterns)}')
    else:
        for pi, (pa, pb) in enumerate(zip(a.patterns, b.patterns)):
            if pa.id != pb.id:
                diffs.append(f'pattern[{pi}].id: {pa.id} != {pb.id}')
            if len(pa.events) != len(pb.events):
                diffs.append(f'pattern[{pi}].events: {len(pa.events)} vs {len(pb.events)}')
            else:
                for ei, (ea, eb) in enumerate(zip(pa.events, pb.events)):
                    for f in ['type', 'note', 'duration', 'instrument', 'command', 'command_val']:
                        va = getattr(ea, f)
                        vb = getattr(eb, f)
                        if va != vb:
                            diffs.append(f'pat[{pi}].ev[{ei}].{f}: {va!r} != {vb!r}')

    # Orderlists
    for vi in range(3):
        if a.orderlists[vi] != b.orderlists[vi]:
            diffs.append(f'orderlist[{vi}]: {len(a.orderlists[vi])} vs {len(b.orderlists[vi])} entries')

    return diffs


# ============================================================
# Main: roundtrip test
# ============================================================

def main():
    """Test roundtrip with a GT2 SID file or the built-in demo song."""
    import argparse

    parser = argparse.ArgumentParser(description='USF text format roundtrip test')
    parser.add_argument('sid_file', nargs='?', help='GT2 SID file to test (optional)')
    parser.add_argument('-o', '--output', help='Write text output to file')
    args = parser.parse_args()

    if args.sid_file:
        from gt2_to_usf import gt2_to_usf
        song = gt2_to_usf(args.sid_file)
        print(f'Parsed: {args.sid_file}')
    else:
        # Use demo song from usf.py
        from usf import Instrument, WaveTableStep, Pattern, NoteEvent
        song = Song(
            title='Demo Song',
            author='SIDfinity',
            sid_model='6581',
            clock='PAL',
            tempo=6,
            instruments=[
                Instrument(id=0, ad=0x09, sr=0x00, waveform='pulse', hr_method='test',
                           gate_timer=2, wave_table=[
                               WaveTableStep(waveform=0x41, note_offset=0),
                               WaveTableStep(waveform=0x41, note_offset=4),
                               WaveTableStep(waveform=0x41, note_offset=7),
                               WaveTableStep(is_loop=True, loop_target=0),
                           ]),
                Instrument(id=1, ad=0x0A, sr=0xD9, waveform='saw', hr_method='gate',
                           gate_timer=2),
            ],
            patterns=[
                Pattern(id=0, events=[
                    NoteEvent(type='note', note=48, duration=4, instrument=0),
                    NoteEvent(type='note', note=52, duration=4),
                    NoteEvent(type='rest', duration=2),
                    NoteEvent(type='off', duration=1),
                    NoteEvent(type='note', note=55, duration=4, command=4, command_val=1),
                ]),
                Pattern(id=1, events=[
                    NoteEvent(type='note', note=24, duration=8, instrument=1),
                    NoteEvent(type='tie', duration=8),
                ]),
            ],
            orderlists=[
                [(0, 0), (0, 5), (0, -3)],
                [(1, 0), (1, 0)],
                [],
            ],
            speed_table=[SpeedTableEntry(left=0x20, right=0x40)],
        )
        print('Using built-in demo song')

    print(f'  Instruments: {len(song.instruments)}')
    print(f'  Patterns: {len(song.patterns)}')
    print(f'  Events: {sum(len(p.events) for p in song.patterns)}')
    print(f'  Orderlists: {[len(ol) for ol in song.orderlists]}')
    if song.shared_wave_table:
        print(f'  Shared wave table: {len(song.shared_wave_table)} entries')
    if song.shared_pulse_table:
        print(f'  Shared pulse table: {len(song.shared_pulse_table)} entries')
    if song.shared_filter_table:
        print(f'  Shared filter table: {len(song.shared_filter_table)} entries')
    if song.speed_table:
        print(f'  Speed table: {len(song.speed_table)} entries')

    # Serialize
    text = to_text(song)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(text)
        print(f'  Written to: {args.output}')

    # Deserialize
    song2 = from_text(text)

    # Compare
    diffs = songs_equal(song, song2)
    if not diffs:
        print('Roundtrip: PASS')
    else:
        print(f'Roundtrip: FAIL ({len(diffs)} differences)')
        for d in diffs[:20]:
            print(f'  {d}')

    # Double roundtrip: serialize again and compare text
    text2 = to_text(song2)
    if text == text2:
        print('Text stability: PASS (to_text is idempotent)')
    else:
        print('Text stability: FAIL')
        lines1 = text.split('\n')
        lines2 = text2.split('\n')
        for i, (a, b) in enumerate(zip(lines1, lines2)):
            if a != b:
                print(f'  Line {i}: {a!r}')
                print(f'       vs: {b!r}')
                break

    return 0 if not diffs else 1


if __name__ == '__main__':
    sys.exit(main())
