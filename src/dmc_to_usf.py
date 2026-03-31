"""
dmc_to_usf.py - Convert parsed DMC data to Universal Symbolic Format.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dmc_parser import parse_dmc_sid
from usf import Song, Instrument, WaveTableStep, Pattern, NoteEvent
from sid_data_extractor import parse_sid_header


def dmc_to_usf(sid_path):
    """Convert a DMC SID file to USF Song."""
    dmc = parse_dmc_sid(sid_path)
    if dmc is None:
        raise ValueError(f"Failed to parse DMC: {sid_path}")

    # Also get track data
    with open(sid_path, 'rb') as f:
        raw = f.read()
    _, binary, la = parse_sid_header(raw)

    song = Song(
        title=dmc['header']['title'],
        author=dmc['header']['author'],
        sid_model='6581',
        clock='PAL',
        tempo=6,  # default DMC speed
    )

    # Convert instruments
    for dmc_instr in dmc['instruments']:
        if dmc_instr is None:
            song.instruments.append(Instrument(id=len(song.instruments)))
            continue

        fx = dmc_instr['fx']
        waveform = 'pulse'
        if fx & 0x01:  # drum
            waveform = 'noise'
        elif fx & 0x80:  # cymbal
            waveform = 'noise'

        hr = 'gate'
        if fx & 0x08:  # nogate
            hr = 'none'

        # Simple wave table: just set the waveform and keep note frequency
        wt = [
            WaveTableStep(waveform={'pulse': 0x41, 'saw': 0x21, 'tri': 0x11,
                                     'noise': 0x81}[waveform], note_offset=0),
            WaveTableStep(is_loop=True, loop_target=0),
        ]

        inst = Instrument(
            id=len(song.instruments),
            ad=dmc_instr['ad'],
            sr=dmc_instr['sr'],
            waveform=waveform,
            hr_method=hr,
            gate_timer=0 if hr == 'none' else 2,
            wave_table=wt,
        )
        song.instruments.append(inst)

    # Convert sectors to patterns
    for sec_idx, sector in enumerate(dmc['sectors']):
        patt = Pattern(id=sec_idx)
        current_duration = 1

        for event in sector:
            etype = event['type']

            if etype == 'duration':
                current_duration = event['value'] + 1

            elif etype == 'instrument':
                # Next note will use this instrument
                # Store as instrument change on the next event
                patt.events.append(NoteEvent(
                    type='rest', duration=0, instrument=event['value']))

            elif etype == 'note':
                patt.events.append(NoteEvent(
                    type='note', note=event['value'],
                    duration=current_duration))

            elif etype == 'gate_off':
                patt.events.append(NoteEvent(
                    type='off', duration=current_duration))

            elif etype == 'continuation':
                patt.events.append(NoteEvent(type='tie'))

            elif etype == 'glide':
                # TODO: convert to portamento effect
                pass

        # Remove zero-duration instrument-only events by merging into next
        merged = []
        pending_inst = -1
        for ev in patt.events:
            if ev.duration == 0 and ev.instrument >= 0:
                pending_inst = ev.instrument
            else:
                if pending_inst >= 0:
                    ev.instrument = pending_inst
                    pending_inst = -1
                merged.append(ev)
        patt.events = merged

        song.patterns.append(patt)

    # Convert tracks to orderlists
    # Find tune pointer table (hardcoded for now, needs generalization)
    tpt_off = None
    # Search for tune pointer table using address analysis
    from sid_data_extractor import find_freq_table, collect_addresses
    ft = find_freq_table(binary)
    if ft:
        freq_off = ft[0]
        fhi = freq_off if ft[1] == 'hi_lo' else freq_off + 96
        instr_off = fhi + 0x0248
        code_regions = [(0, freq_off), (freq_off + 192, instr_off)]
        refs = collect_addresses(binary, la, code_regions)
        data_addrs = sorted(a for a, r in refs.items()
                            if r['is_data'] and (a - la) >= instr_off + 352)

        # Find tune pointer table: 3 consecutive addresses pointing into track area
        for a in data_addrs:
            off = a - la
            if off + 6 <= len(binary):
                v1 = binary[off] | (binary[off + 1] << 8)
                v2 = binary[off + 2] | (binary[off + 3] << 8)
                v3 = binary[off + 4] | (binary[off + 5] << 8)
                if (la < v1 < la + len(binary) and
                    la < v2 < la + len(binary) and
                    la < v3 < la + len(binary) and
                    v1 != v2):
                    tpt_off = off
                    break

    if tpt_off is not None:
        voice_addrs = [binary[tpt_off + i] | (binary[tpt_off + i + 1] << 8)
                       for i in range(0, 6, 2)]

        for vi, va in enumerate(voice_addrs):
            ol = []
            off = va - la
            trans = 0
            while off < len(binary):
                b = binary[off]
                if b <= 0x3F:
                    ol.append((b, trans))
                    off += 1
                elif b == 0xFF:
                    break
                elif b == 0xFE:
                    break
                elif 0xA0 <= b <= 0xAF:
                    trans = b & 0x0F
                    off += 1
                else:
                    off += 1
            song.orderlists[vi] = ol

    return song


def main():
    from usf import tokenize, to_text

    if len(sys.argv) < 2:
        print("Usage: dmc_to_usf.py <file.sid>")
        sys.exit(1)

    song = dmc_to_usf(sys.argv[1])
    tokens = tokenize(song)
    print(f'Token count: {len(tokens)}')
    print(f'Instruments: {len(song.instruments)}')
    print(f'Patterns: {len(song.patterns)}')
    print(f'Orderlists: {[len(ol) for ol in song.orderlists]}')
    print()
    print(to_text(tokens))


if __name__ == '__main__':
    main()
