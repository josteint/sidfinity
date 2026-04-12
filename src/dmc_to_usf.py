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

    dmc_version = dmc.get('dmc_version', 'v4')

    # Also get track data
    with open(sid_path, 'rb') as f:
        raw = f.read()
    _, binary, la = parse_sid_header(raw)

    # Extract DMC frequency table
    ft = find_freq_table(binary)
    freq_lo = None
    freq_hi = None
    if ft:
        freq_off, freq_order = ft
        if freq_order == 'hi_lo':
            fhi_off = freq_off
            flo_off = freq_off + 96
        else:
            flo_off = freq_off
            fhi_off = freq_off + 96
        freq_hi = bytes(binary[fhi_off:fhi_off + 96])
        freq_lo = bytes(binary[flo_off:flo_off + 96])

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
    # DMC stores tune pointers as interleaved table: lo0 hi0 lo1 hi1 lo2 hi2
    # 8 subtunes x 6 bytes = 48 bytes max. First subtune at offset 0.
    # V5 allows sector refs up to $5F (96 sectors), V4 up to $3F (64 sectors).
    max_sector_ref = 0x5F if dmc_version == 'v5' else 0x3F
    layout = dmc['layout']
    instr_end_off = layout['instr_end']

    # Find tune pointer table by brute-force scanning data region.
    # Look for 3 interleaved 16-bit pointers to valid track data.
    # Track data = sequence of: sector refs, transpose commands, end/loop markers.
    # We require at least 2 of 3 voices to have non-empty tracks (>= 1 sector ref)
    # to avoid false positives in wave/pulse/filter table areas.
    def _is_track_byte(b):
        return (b <= max_sector_ref or
                0x80 <= b <= 0x8F or  # transpose down
                0xA0 <= b <= 0xAF or  # transpose up
                b in (0xFE, 0xFF))    # end / loop

    def _track_length(start_off):
        """Count sector refs in track data starting at offset.

        Returns (sector_refs, terminated) where terminated means we hit $FE/$FF.
        Tolerates unknown bytes in the stream (V5 has speed/loop commands
        in the $B0-$BF range that we don't fully document yet).
        """
        off = start_off
        sector_refs = 0
        steps = 0
        while off < len(binary) and steps < 256:
            b = binary[off]
            if b <= max_sector_ref:
                sector_refs += 1
            elif b in (0xFE, 0xFF):
                return (sector_refs, True)
            off += 1
            steps += 1
        return (sector_refs, False)

    tpt_off = None
    for scan_off in range(instr_end_off, len(binary) - 6):
        ptrs = []
        valid = True
        for k in range(3):
            v = binary[scan_off + k * 2] | (binary[scan_off + k * 2 + 1] << 8)
            if not (la <= v < la + len(binary)):
                valid = False
                break
            ptrs.append(v)
        if not valid or len(set(ptrs)) < 2:
            continue
        # All 3 pointed-to bytes must look like track data start
        if not all(_is_track_byte(binary[p - la]) for p in ptrs):
            continue
        # Verify: at least 2 voices must have sector refs AND terminate properly
        track_info = [_track_length(p - la) for p in ptrs]
        voices_with_content = sum(1 for refs, term in track_info if refs > 0 and term)
        all_terminated = all(term for _, term in track_info)
        if voices_with_content >= 2 or (voices_with_content >= 1 and all_terminated):
            tpt_off = scan_off
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
                if b <= max_sector_ref:
                    ol.append((b, trans))
                    off += 1
                elif b == 0xFF or b == 0xFE:
                    break
                elif 0xA0 <= b <= 0xAF:
                    trans = b & 0x0F
                    off += 1
                elif 0x80 <= b <= 0x8F:
                    trans = -(b & 0x0F)
                    off += 1
                else:
                    # Unknown track command ($B0-$BF range, speed cmds, etc.)
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
