"""
dmc_to_gt2.py - Transpile DMC sectors to GoatTracker packed patterns.

Converts DMC's duration-based format to GT2's row-based format:
  DMC: "duration=3, note C4" = note plays for 3 ticks
  GT2: row 0: C4 note, row 1: rest, row 2: rest (3 rows total)

DMC instruments map to GT2 instruments with wave table entries
for the waveform sequence and pulse width modulation.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# GT2 packed pattern encoding
GT2_ENDPATT = 0x00
GT2_FIRSTNOTE = 0x60
GT2_REST = 0xBD
GT2_KEYOFF = 0xBE
GT2_KEYON = 0xBF
GT2_FIRSTPACKEDREST = 0xC0
GT2_FX = 0x40
GT2_FXONLY = 0x50


def dmc_sector_to_gt2_pattern(sector_events):
    """Convert a DMC sector (list of events) to GT2 packed pattern bytes.

    Returns bytearray of GT2 packed pattern data (including $00 end marker).
    """
    # First pass: expand DMC events into a row-by-row representation
    rows = []  # list of (note_byte, instrument, is_gate_off, is_continuation)
    current_duration = 1  # default DMC duration
    current_instrument = None
    pending_instrument = None

    for event in sector_events:
        etype = event['type']

        if etype == 'duration':
            current_duration = event['value'] + 1  # DMC duration 0 = 1 tick
        elif etype == 'instrument':
            pending_instrument = event['value']
        elif etype == 'note':
            # Note plays for current_duration ticks
            note_num = event['value']
            gt2_note = GT2_FIRSTNOTE + note_num  # DMC 0-95 -> GT2 $60-$BF

            if gt2_note > 0xBC:
                gt2_note = 0xBC  # clamp to GT2 max

            # First row: the note (with optional instrument change)
            rows.append({
                'note': gt2_note,
                'instrument': pending_instrument,
                'continuation': False,
            })
            pending_instrument = None

            # Remaining rows: rests for duration-1 ticks
            for _ in range(current_duration - 1):
                rows.append({'note': GT2_REST})

        elif etype == 'gate_off':
            # Gate off for one tick (duration ticks)
            rows.append({'note': GT2_KEYOFF})
            for _ in range(current_duration - 1):
                rows.append({'note': GT2_REST})

        elif etype == 'continuation':
            # Next note won't retrigger ADSR — in GT2 this is a tie
            # We'll handle this by not gating off before the next note
            # For now, just mark it
            pass

        elif etype == 'glide':
            # DMC glide: slide to next note
            # GT2 equivalent: portamento command
            # For now, skip (would need speed table entry)
            pass

        elif etype == 'command':
            # Unknown command, skip
            pass

    # Second pass: pack into GT2 format
    packed = bytearray()
    prev_instrument = None

    i = 0
    while i < len(rows):
        row = rows[i]
        note = row.get('note', GT2_REST)
        instrument = row.get('instrument')

        # Count consecutive rests for packing
        if note == GT2_REST and instrument is None:
            rest_count = 0
            j = i
            while j < len(rows) and rows[j].get('note') == GT2_REST and rows[j].get('instrument') is None:
                rest_count += 1
                j += 1

            # First rest can't be packed (GT2 constraint)
            if i == 0 or rest_count == 1:
                packed.append(GT2_REST)
                i += 1
            elif rest_count <= 64:
                # Packed rest: $C0 + (256 - count)... actually count = 256 - byte
                # So byte = 256 - count
                packed.append(256 - rest_count)
                i += rest_count
            else:
                # Multiple packed rests
                while rest_count > 0:
                    chunk = min(rest_count, 64)
                    if chunk == 1:
                        packed.append(GT2_REST)
                    else:
                        packed.append(256 - chunk)
                    rest_count -= chunk
                    i += chunk
            continue

        # Instrument change
        if instrument is not None and instrument != prev_instrument:
            packed.append(instrument + 1)  # GT2 instruments are 1-based
            prev_instrument = instrument

        # Note / keyoff / keyon
        packed.append(note)
        i += 1

    # End marker
    packed.append(GT2_ENDPATT)
    return bytes(packed)


def dmc_instrument_to_gt2(dmc_instr):
    """Convert a DMC instrument to GT2 instrument columns.

    DMC instrument (11 bytes): AD, SR, wave_ptr, pw1-3, pw_limit, vib1-2, filter, fx
    GT2 instrument (up to 9 columns): AD, SR, wave_ptr, pulse_ptr, filter_ptr,
                                       vib_param, vib_delay, gate_timer, first_wave

    Returns dict with GT2 column values.
    """
    if dmc_instr is None:
        return {
            'ad': 0, 'sr': 0, 'wave_ptr': 0, 'pulse_ptr': 0, 'filter_ptr': 0,
            'vib_param': 0, 'vib_delay': 0, 'gate_timer': 0x02, 'first_wave': 0x41,
        }

    # Map DMC FX flags to GT2 gate timer / HR
    fx = dmc_instr['fx']
    gate_timer = 0x02  # default: 2-frame gate-off for hard restart
    if fx & 0x08:  # no gate flag
        gate_timer = 0x80  # no hard restart

    # Determine waveform from DMC wave table pointer
    # DMC wave_ptr references the wave table; GT2 uses first_wave byte
    # For now, default to pulse wave
    first_wave = 0x41  # pulse + gate
    if fx & 0x01:  # drum flag
        first_wave = 0x81  # noise + gate
    if fx & 0x80:  # cymbal flag
        first_wave = 0x81  # noise + gate

    return {
        'ad': dmc_instr['ad'],
        'sr': dmc_instr['sr'],
        'wave_ptr': 0,  # would need wave table mapping
        'pulse_ptr': 0,  # would need pulse table mapping
        'filter_ptr': 0,  # would need filter table mapping
        'vib_param': dmc_instr['vib1'],
        'vib_delay': (dmc_instr['vib1'] >> 4) & 0x0F,
        'gate_timer': gate_timer,
        'first_wave': first_wave,
    }


def transpile_dmc_to_gt2(parsed_dmc):
    """Transpile parsed DMC data into GT2 structures.

    Returns dict with GT2-format patterns, instruments, orderlists.
    """
    # Convert instruments
    gt2_instruments = []
    for dmc_instr in parsed_dmc['instruments']:
        gt2_instruments.append(dmc_instrument_to_gt2(dmc_instr))

    # Convert sectors to GT2 packed patterns
    gt2_patterns = []
    for sector in parsed_dmc['sectors']:
        packed = dmc_sector_to_gt2_pattern(sector)
        gt2_patterns.append(packed)

    # For now, orderlists are a simple mapping:
    # DMC track references sector numbers, GT2 orderlists reference pattern numbers
    # They map 1:1 since we converted each sector to a pattern
    # (Track parsing not yet implemented — would need to decode DMC track data)

    return {
        'instruments': gt2_instruments,
        'patterns': gt2_patterns,
        'num_patterns': len(gt2_patterns),
        'total_rows': sum(
            sum(1 for b in patt if GT2_FIRSTNOTE <= b <= 0xBC or b == GT2_REST
                or b == GT2_KEYOFF or b >= GT2_FIRSTPACKEDREST)
            for patt in gt2_patterns),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Transpile DMC to GT2 format')
    parser.add_argument('input', help='DMC SID file')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    from dmc_parser import parse_dmc_sid

    parsed = parse_dmc_sid(args.input)
    if parsed is None:
        print('Failed to parse DMC file')
        sys.exit(1)

    result = transpile_dmc_to_gt2(parsed)

    print(f'DMC: {parsed["num_sectors"]} sectors, {parsed["total_notes"]} notes')
    print(f'GT2: {result["num_patterns"]} patterns, {result["total_rows"]} rows')

    if args.verbose:
        for i, patt in enumerate(result['patterns'][:5]):
            print(f'\n  Pattern {i} ({len(patt)} bytes):')
            # Decode for display
            j = 0
            row = 0
            while j < len(patt):
                b = patt[j]
                if b == GT2_ENDPATT:
                    print(f'    END')
                    break
                elif 0x01 <= b <= 0x3F:
                    print(f'    I{b:02X}', end='')
                    j += 1
                    continue
                elif GT2_FIRSTNOTE <= b <= 0xBC:
                    note_num = b - GT2_FIRSTNOTE
                    names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
                    print(f' {names[note_num%12]}{note_num//12}', end='')
                    row += 1
                elif b == GT2_REST:
                    print(f' .', end='')
                    row += 1
                elif b == GT2_KEYOFF:
                    print(f' OFF', end='')
                    row += 1
                elif b >= GT2_FIRSTPACKEDREST:
                    count = 256 - b
                    print(f' .x{count}', end='')
                    row += count
                j += 1
            print(f'  ({row} rows)')


if __name__ == '__main__':
    main()
