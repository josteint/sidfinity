"""
dmc_to_usf.py - Convert parsed DMC data to Universal Symbolic Format.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from dmc_parser import parse_dmc_sid
from usf.format import Song, Instrument, WaveTableStep, Pattern, NoteEvent
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
        from usf.format import waveform_from_byte
        waveform = waveform_from_byte(first_wave)

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

        Returns (sector_refs, terminated, max_ref) where:
        - sector_refs: number of sector references found
        - terminated: True if we hit $FE/$FF
        - max_ref: highest sector ref seen (for validating against num_sectors)
        """
        off = start_off
        sector_refs = 0
        max_ref = -1
        steps = 0
        while off < len(binary) and steps < 256:
            b = binary[off]
            if b <= max_sector_ref:
                sector_refs += 1
                if b > max_ref:
                    max_ref = b
            elif b in (0xFE, 0xFF):
                return (sector_refs, True, max_ref)
            off += 1
            steps += 1
        return (sector_refs, False, max_ref)

    # Get actual sector count for validation
    num_sectors = dmc['num_sectors']

    tpt_off = None
    best_tpt = None
    best_tpt_score = 0
    # Scan the entire data region for tune pointer table candidates
    # Use the sector count to validate: track data should not reference
    # sectors beyond what exists in the sector pointer table.
    scan_start = min(instr_end_off, layout.get('sector_ptr_lo', instr_end_off) - la) \
                 if layout.get('sector_ptr_lo') else instr_end_off
    scan_start = max(0, scan_start)

    for scan_off in range(scan_start, len(binary) - 6):
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
        # Verify tracks: must terminate, have sector refs, refs within bounds
        track_info = [_track_length(p - la) for p in ptrs]
        voices_with_content = sum(1 for refs, term, _ in track_info if refs > 0 and term)
        all_terminated = all(term for _, term, _ in track_info)
        total_refs = sum(refs for refs, _, _ in track_info)
        max_ref_seen = max((mr for _, _, mr in track_info), default=-1)

        if not (voices_with_content >= 2 or (voices_with_content >= 1 and all_terminated)):
            continue

        # Validate: sector refs should be within the actual sector count
        refs_in_bounds = max_ref_seen < num_sectors if num_sectors > 0 and max_ref_seen >= 0 else True

        # Score: prefer candidates with more sector refs, in-bounds refs, more voices
        score = total_refs * 10 + voices_with_content * 100
        if refs_in_bounds:
            score += 1000  # strong bonus for in-bounds refs
        if score > best_tpt_score:
            best_tpt_score = score
            best_tpt = scan_off

    tpt_off = best_tpt

    # Fallback: scan backwards from sector data and sector pointer table
    # DMC layout: ... track data ... tune pointer table ... sector data ... sector ptrs
    if tpt_off is None and num_sectors > 0 and layout.get('sector_ptr_lo'):
        sector_addrs_raw = []
        spt_lo_off = layout['sector_ptr_lo'] - la
        spt_hi_off = layout['sector_ptr_hi'] - la
        for k in range(num_sectors):
            addr = binary[spt_lo_off + k] | (binary[spt_hi_off + k] << 8)
            sector_addrs_raw.append(addr)
        min_sector_data = min(sector_addrs_raw) - la if sector_addrs_raw else len(binary)

        # Try before sector data first, then before sector pointer table
        for search_end in (min_sector_data, spt_lo_off):
            if tpt_off is not None:
                break
            for scan_off in range(max(0, search_end - 200), search_end):
                ptrs = []
                valid = True
                for k in range(3):
                    if scan_off + k * 2 + 1 >= len(binary):
                        valid = False; break
                    v = binary[scan_off + k * 2] | (binary[scan_off + k * 2 + 1] << 8)
                    if not (la <= v < la + len(binary)):
                        valid = False; break
                    ptrs.append(v)
                if not valid or len(set(ptrs)) < 2:
                    continue
                total_refs = 0; all_term = True; max_ref = -1
                for p in ptrs:
                    poff = p - la; refs = 0; j = 0; terminated = False
                    while poff + j < len(binary) and j < 256:
                        b = binary[poff + j]
                        if b <= max_sector_ref:
                            refs += 1
                            if b > max_ref: max_ref = b
                        elif b in (0xFE, 0xFF):
                            terminated = True; break
                        j += 1
                    total_refs += refs
                    if not terminated: all_term = False
                if total_refs > 0 and all_term and max_ref < num_sectors:
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
    from adapters.usf_tokens import tokenize
    from adapters.usf_text import to_text

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
