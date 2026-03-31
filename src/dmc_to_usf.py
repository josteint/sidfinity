"""
dmc_to_usf.py - Convert parsed DMC data to Universal Symbolic Format.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dmc_parser import parse_dmc_sid
from usf import Song, Instrument, WaveTableStep, Pattern, NoteEvent
from sid_data_extractor import parse_sid_header, find_freq_table, collect_addresses


def dmc_to_usf(sid_path):
    """Convert a DMC SID file to USF Song."""
    dmc = parse_dmc_sid(sid_path)
    if dmc is None:
        raise ValueError(f"Failed to parse DMC: {sid_path}")

    # Also get track data
    with open(sid_path, 'rb') as f:
        raw = f.read()
    _, binary, la = parse_sid_header(raw)

    # Extract DMC frequency table
    ft = find_freq_table(binary)
    freq_lo = None
    freq_hi = None
    if ft:
        fhi_off = ft[0]
        freq_hi = bytes(binary[fhi_off:fhi_off + 96])
        freq_lo = bytes(binary[fhi_off + 96:fhi_off + 192])

    song = Song(
        title=dmc['header']['title'],
        author=dmc['header']['author'],
        sid_model='6581',
        clock='PAL',
        tempo=6,  # default DMC speed
    )
    song.freq_lo = freq_lo
    song.freq_hi = freq_hi

    # Find DMC wave table addresses by tracing player code
    # Wave table has two columns: left (waveform bytes) and right (note data)
    # Left column accessed via: LDA $XXXX,Y followed by CMP #$90
    # Right column accessed via: LDA $YYYY,Y shortly after
    dmc_wt_left = None
    dmc_wt_right = None
    for i in range(len(binary) - 5):
        if binary[i] == 0xB9:  # LDA abs,Y
            addr = binary[i + 1] | (binary[i + 2] << 8)
            for j in range(i + 3, min(i + 10, len(binary) - 1)):
                if binary[j] == 0xC9 and binary[j + 1] == 0x90:
                    dmc_wt_left = addr - la
                    # Find right column: next LDA abs,Y after the branch
                    for k in range(j + 2, min(j + 40, len(binary) - 2)):
                        if binary[k] == 0xB9:
                            raddr = binary[k + 1] | (binary[k + 2] << 8)
                            roff = raddr - la
                            if roff > dmc_wt_left and roff < dmc_wt_left + 200:
                                dmc_wt_right = roff
                                break
                    break
            if dmc_wt_left is not None:
                break

    # Convert instruments
    for dmc_instr in dmc['instruments']:
        if dmc_instr is None:
            song.instruments.append(Instrument(id=len(song.instruments)))
            continue

        fx = dmc_instr['fx']
        hr = 'gate'
        if fx & 0x08:  # nogate
            hr = 'none'

        # Extract wave table from DMC binary (both columns)
        wt = []
        wp = dmc_instr['wave_ptr']
        if dmc_wt_left is not None and wp > 0:
            idx = wp
            while dmc_wt_left + idx < len(binary) and len(wt) < 32:
                b = binary[dmc_wt_left + idx]
                if b == 0xFE:
                    wt.append(WaveTableStep(waveform=0x00, note_offset=0))
                elif b < 0x90:
                    # Raw SID waveform byte (left column)
                    # Right column has note data
                    note_data = 0
                    if dmc_wt_right is not None and dmc_wt_right + idx < len(binary):
                        note_data = binary[dmc_wt_right + idx]
                    wt.append(WaveTableStep(waveform=b, note_offset=note_data))
                else:
                    # Command >= $90: loop back (b - $90) steps
                    jump_back = b - 0x90
                    loop_target = max(0, len(wt) - jump_back)
                    wt.append(WaveTableStep(is_loop=True, loop_target=loop_target))
                    break
                idx += 1

        if not wt:
            # Default: pulse wave, loop
            wt = [
                WaveTableStep(waveform=0x41, note_offset=0),
                WaveTableStep(is_loop=True, loop_target=0),
            ]

        # Determine primary waveform from first non-loop wave table entry
        first_wave = wt[0].waveform if wt and not wt[0].is_loop else 0x41
        wave_bits = (first_wave >> 4) & 0xF
        waveform = {1: 'tri', 2: 'saw', 4: 'pulse', 8: 'noise'}.get(wave_bits, 'pulse')

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
    # Find tune pointer table by searching player code for LDA abs,Y pairs
    # DMC stores tune pointers as an interleaved table: lo0 hi0 lo1 hi1 lo2 hi2
    # Player accesses via LDA $XXXX,Y and LDA $XXXX+1,Y with Y=0,2,4
    tpt_off = None
    ft = find_freq_table(binary)
    if ft:
        freq_off = ft[0]
        fhi = freq_off if ft[1] == 'hi_lo' else freq_off + 96
        instr_off = fhi + 0x0248
        code_end = freq_off  # player code is before freq table

        # Collect all LDA abs,Y ($B9) in player code pointing past instruments
        lda_refs = []
        for i in range(code_end - 2):
            if binary[i] == 0xB9:  # LDA abs,Y
                addr = binary[i + 1] | (binary[i + 2] << 8)
                off = addr - la
                if instr_off <= off < len(binary):
                    lda_refs.append(addr)

        # Find pairs where addresses differ by 1 (lo/hi table access)
        lda_set = set(lda_refs)
        for addr in sorted(lda_set):
            if addr + 1 in lda_set:
                off = addr - la
                # Check if this looks like 3 interleaved 16-bit pointers
                if off + 6 <= len(binary):
                    ptrs = []
                    valid = True
                    for k in range(3):
                        v = binary[off + k * 2] | (binary[off + k * 2 + 1] << 8)
                        if not (la <= v < la + len(binary)):
                            valid = False
                            break
                        ptrs.append(v)
                    if valid and len(set(ptrs)) >= 2:
                        tpt_off = off
                        break

    if tpt_off is not None:
        voice_addrs = [binary[tpt_off + i * 2] | (binary[tpt_off + i * 2 + 1] << 8)
                       for i in range(3)]

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
                elif 0x80 <= b <= 0x8F:
                    trans = -(b & 0x0F)
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
