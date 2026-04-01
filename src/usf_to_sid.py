"""
usf_to_sid.py - Convert USF Song to a playable .sid file via SIDfinity packer.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usf import Song, NoteEvent
from sidfinity_packer import pack_sid

# GT2 packed pattern constants
GT2_ENDPATT = 0x00
GT2_FIRSTNOTE = 0x60
GT2_REST = 0xBD
GT2_KEYOFF = 0xBE
GT2_KEYON = 0xBF
GT2_FIRSTPACKEDREST = 0xC0

WAVE_MAP = {'pulse': 0x41, 'saw': 0x21, 'tri': 0x11, 'noise': 0x81}


def usf_pattern_to_gt2(pattern):
    """Convert a USF Pattern to GT2 packed pattern bytes."""
    packed = bytearray()
    prev_inst = -1

    for event in pattern.events:
        # Instrument change
        if event.instrument >= 0 and event.instrument != prev_inst:
            packed.append(event.instrument + 1)  # GT2 is 1-based
            prev_inst = event.instrument

        # Event type
        if event.type == 'note':
            note_byte = GT2_FIRSTNOTE + event.note
            if note_byte > 0xBC:
                note_byte = 0xBC
            packed.append(note_byte)
        elif event.type == 'rest':
            packed.append(GT2_REST)
        elif event.type == 'off':
            packed.append(GT2_KEYOFF)
        elif event.type == 'on':
            packed.append(GT2_KEYON)
        elif event.type == 'tie':
            packed.append(GT2_REST)  # approximate: tie as rest

        # Duration: add rests for duration-1 ticks
        dur = max(1, event.duration)
        for _ in range(dur - 1):
            packed.append(GT2_REST)

    packed.append(GT2_ENDPATT)

    # Compact: replace long rest runs with packed rests
    if len(packed) > 128:
        compact = bytearray()
        j = 0
        while j < len(packed) - 1:
            b = packed[j]
            if b == GT2_REST or b == GT2_KEYOFF:
                count = 0
                while j < len(packed) - 1 and (packed[j] == GT2_REST or packed[j] == GT2_KEYOFF):
                    count += 1
                    j += 1
                while count > 0:
                    chunk = min(count, 64)
                    if chunk == 1:
                        compact.append(GT2_REST)
                    else:
                        compact.append(256 - chunk)
                    count -= chunk
            else:
                compact.append(b)
                j += 1
        compact.append(GT2_ENDPATT)
        packed = compact

    if len(packed) > 255:
        packed = bytearray(packed[:254])
        packed.append(GT2_ENDPATT)

    return bytes(packed)


def usf_to_sid(song, output_path=None):
    """Convert a USF Song to a .sid file.

    Returns the SID bytes, and optionally writes to output_path.
    """
    # Convert patterns
    gt2_patterns = []
    for patt in song.patterns:
        gt2_patterns.append(usf_pattern_to_gt2(patt))

    # Convert instruments to column arrays
    ni = len(song.instruments)
    if ni == 0:
        ni = 1
        song.instruments = [usf.Instrument()]

    ad_col = bytearray(ni)
    sr_col = bytearray(ni)
    fw_col = bytearray(ni)
    gt_col = bytearray(ni)
    wp_col = bytearray(ni)
    vp_col = bytearray(ni)
    vd_col = bytearray(ni)
    pp_col = bytearray(ni)
    fp_col = bytearray(ni)

    for i, inst in enumerate(song.instruments):
        ad_col[i] = inst.ad
        sr_col[i] = inst.sr
        if inst.first_wave >= 0:
            fw_col[i] = inst.first_wave
        else:
            fw_col[i] = WAVE_MAP.get(inst.waveform, 0x41)
        gt_col[i] = inst.gate_timer if inst.hr_method != 'none' else 0x80
        wp_col[i] = 1 if inst.wave_table else 0
        vp_col[i] = getattr(inst, 'vib_speed_idx', 0) or 0
        vd_col[i] = getattr(inst, 'vib_delay', 0) or 0
        pp_col[i] = getattr(inst, 'pulse_ptr', 0) or 0
        fp_col[i] = getattr(inst, 'filter_ptr', 0) or 0

    # Build wave table from all instruments' wave tables concatenated
    wave_l = bytearray()
    wave_r = bytearray()
    wt_offset = 1  # 1-based indexing

    for i, inst in enumerate(song.instruments):
        if inst.wave_table:
            wp_col[i] = wt_offset
            inst_wt_start = wt_offset
            for step in inst.wave_table:
                if step.is_loop:
                    wave_l.append(0xFF)
                    wave_r.append(inst_wt_start + step.loop_target)
                elif step.keep_freq:
                    wave_l.append(step.waveform)
                    wave_r.append(0x80)  # $80 = relative +0 (sets freq from current note)
                elif step.absolute_note >= 0:
                    wave_l.append(step.waveform)
                    wave_r.append(step.absolute_note & 0x7F)  # $01-$7F = absolute
                else:
                    wave_l.append(step.waveform)
                    wave_r.append((step.note_offset + 0x80) & 0xFF)  # $80+ = relative
            # If no loop step, add a stop entry ($FF/$00)
            has_loop = any(s.is_loop for s in inst.wave_table)
            if not has_loop:
                wave_l.append(0xFF)
                wave_r.append(0x00)  # stop
                wt_offset += len(inst.wave_table) + 1
            else:
                wt_offset += len(inst.wave_table)
        else:
            wp_col[i] = 0

    if not wave_l:
        wave_l = bytes([0x41, 0xFF])
        wave_r = bytes([0x80, 0x01])
        for i in range(ni):
            if wp_col[i] == 0:
                wp_col[i] = 1

    # Convert orderlists
    gt2_orderlists = []
    for vi in range(3):
        ol = bytearray()
        for patt_id, transpose in song.orderlists[vi]:
            if transpose != 0:
                if transpose > 0:
                    ol.append(0xF0 + transpose)
                else:
                    ol.append(0xE0 + (16 + transpose))
            ol.append(patt_id)
        ol.extend([0xFF, 0x00])  # loop to start
        gt2_orderlists.append(bytes(ol))

    # Pack (with optional custom freq table)
    freq_lo = getattr(song, 'freq_lo', None)
    freq_hi = getattr(song, 'freq_hi', None)

    # Use raw GT2 table data if available (from direct parser passthrough)
    raw = getattr(song, '_raw_gt2', None) or {}

    sid_bytes, player_size = pack_sid(
        title=song.title,
        author=song.author,
        num_instruments=ni,
        freq_lo=freq_lo,
        freq_hi=freq_hi,
        instruments_ad=bytes(ad_col),
        instruments_sr=bytes(sr_col),
        instruments_firstwave=bytes(fw_col),
        instruments_gatetimer=bytes(gt_col),
        instruments_waveptr=raw.get('wave_ptr_col', bytes(wp_col)),
        instruments_vibparam=bytes(vp_col),
        instruments_vibdelay=bytes(vd_col),
        instruments_pulseptr=bytes(pp_col),
        instruments_filtptr=bytes(fp_col),
        wave_left=raw.get('wave_left', bytes(wave_l)),
        wave_right=raw.get('wave_right', bytes(wave_r)),
        pulse_left=raw.get('pulse_left'),
        pulse_right=raw.get('pulse_right'),
        filter_left=raw.get('filter_left'),
        filter_right=raw.get('filter_right'),
        speed_left=raw.get('speed_left'),
        speed_right=raw.get('speed_right'),
        orderlists=gt2_orderlists,
        patterns=gt2_patterns,
        default_tempo=getattr(song, 'tempo', 6),
    )

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(sid_bytes)

    return sid_bytes, player_size


def main():
    if len(sys.argv) < 3:
        print("Usage: usf_to_sid.py <input.sid> <output.sid>")
        print("  (input is a DMC SID, converted via DMC->USF->SID)")
        sys.exit(1)

    from dmc_to_usf import dmc_to_usf
    from usf import tokenize

    song = dmc_to_usf(sys.argv[1])
    tokens = tokenize(song)
    print(f'USF: {len(tokens)} tokens, {len(song.patterns)} patterns, '
          f'{len(song.instruments)} instruments')

    sid, ps = usf_to_sid(song, sys.argv[2])
    print(f'Built {sys.argv[2]}: {len(sid)} bytes (player: {ps})')

    # Compare with original
    import subprocess
    siddump = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          'tools', 'siddump')
    r_orig = subprocess.run([siddump, sys.argv[1], '--duration', '15'],
                           capture_output=True, text=True, timeout=30)
    r_new = subprocess.run([siddump, sys.argv[2], '--duration', '15'],
                          capture_output=True, text=True, timeout=30)

    if r_orig.returncode == 0 and r_new.returncode == 0:
        orig = r_orig.stdout.strip().split('\n')[2:]
        new = r_new.stdout.strip().split('\n')[2:]
        total = min(len(orig), len(new))

        for v, idx in enumerate([1, 8, 15]):
            match = sum(1 for o, n in zip(orig, new)
                        if o.split(',')[idx] == n.split(',')[idx])
            print(f'V{v+1} freq_hi match: {match}/{total} ({100*match/total:.1f}%)')

        full = sum(1 for o, n in zip(orig, new) if o == n)
        print(f'Full register match: {full}/{total} ({100*full/total:.1f}%)')


if __name__ == '__main__':
    main()
