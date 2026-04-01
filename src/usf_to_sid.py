"""
usf_to_sid.py — Convert USF Song to GT2-format SID file.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import usf
from usf import Song, Pattern, NoteEvent
from sidfinity_packer import pack_sid

GT2_ENDPATT = 0x00
GT2_FIRSTNOTE = 0x60
GT2_REST = 0xBD
GT2_KEYOFF = 0xBE
GT2_KEYON = 0xBF
GT2_FIRSTPACKEDREST = 0xC0

WAVE_MAP = {'tri': 0x11, 'saw': 0x21, 'pulse': 0x41, 'noise': 0x81}


def usf_pattern_to_gt2(pattern):
    """Convert a USF Pattern to GT2 packed pattern bytes.

    Mirrors greloc.c encoding: only emits FX byte when command changes.
    """
    rows = []
    prev_inst = -1
    prev_cmd = -1
    prev_param = -1

    for event in pattern.events:
        row = bytearray()

        # Instrument change
        if event.instrument >= 0 and event.instrument != prev_inst:
            row.append(event.instrument + 1)
            prev_inst = event.instrument

        # Command state
        has_cmd = event.command is not None
        cmd_num = (event.command & 0x0F) if has_cmd else 0
        cmd_val = (event.command_val & 0xFF) if has_cmd else 0
        cmd_changed = has_cmd and (cmd_num != prev_cmd or cmd_val != prev_param)

        if cmd_changed:
            prev_cmd = cmd_num
            prev_param = cmd_val

        # Encode row based on type
        if event.type == 'rest':
            if cmd_changed:
                row.append(0x50 + cmd_num)  # FXONLY
                if cmd_num != 0:
                    row.append(cmd_val)
            else:
                row.append(GT2_REST)
        elif event.type == 'note':
            if cmd_changed:
                row.append(0x40 + cmd_num)  # FX
                if cmd_num != 0:
                    row.append(cmd_val)
            row.append(min(GT2_FIRSTNOTE + event.note, 0xBC))
        elif event.type == 'off':
            if cmd_changed:
                row.append(0x40 + cmd_num)
                if cmd_num != 0:
                    row.append(cmd_val)
            row.append(GT2_KEYOFF)
        elif event.type == 'on':
            if cmd_changed:
                row.append(0x40 + cmd_num)
                if cmd_num != 0:
                    row.append(cmd_val)
            row.append(GT2_KEYON)

        rows.append(bytes(row))

    # Compress consecutive rests
    packed = bytearray()
    i = 0
    while i < len(rows):
        row = rows[i]
        if row == bytes([GT2_REST]):
            count = 0
            while i < len(rows) and rows[i] == bytes([GT2_REST]):
                count += 1
                i += 1
            is_last = (i >= len(rows))  # this is the last run before ENDPATT
            while count > 0:
                if count == 1:
                    packed.append(GT2_REST)
                    count -= 1
                elif is_last and count > 2:
                    # GT2 packer leaves 1 explicit $BD before ENDPATT
                    chunk = min(count - 1, 62)
                    packed.append(256 - chunk)
                    count -= chunk
                else:
                    chunk = min(count, 62)
                    packed.append(256 - chunk)
                    count -= chunk
        else:
            packed.extend(row)
            i += 1

    # Check if the last row is a trailing FX rest (cross-pattern sharing).
    # If the last row bytes are FXONLY ($50+cmd, [param]), the encoder already
    # emitted them. But greloc.c uses FX ($40+cmd) not FXONLY ($50+cmd) for
    # these trailing commands, and the $00 param doubles as ENDPATT.
    # Detect and fix: if last row is FXONLY with param=0, replace with FX.
    if (len(rows) > 0 and len(packed) >= 2 and
            packed[-1] == 0x00 and packed[-2] >= 0x50 and packed[-2] < 0x60):
        # Last emitted bytes: $5X $00 (FXONLY cmd=X, param=0)
        # Replace $5X with $4X (FX instead of FXONLY)
        # The $00 param doubles as ENDPATT — don't add another $00
        packed[-2] = packed[-2] - 0x10  # $5X → $4X
        return bytes(packed)

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

    # Build instrument columns. If raw GT2 data is available, use it
    # directly (remapped to our packer's column order). Otherwise,
    # build from USF instrument fields.
    raw = getattr(song, '_raw_gt2', None) or {}
    raw_cols = raw.get('col_data', {})

    def raw_col(name, default_val=0):
        """Get raw column bytes, padded to ni."""
        vals = raw_cols.get(name, [])
        if vals:
            result = list(vals[:ni])
            while len(result) < ni:
                result.append(default_val)
            return bytes(result)
        return bytes([default_val] * ni)

    if raw_cols:
        # Use raw column data directly, remapped to packer order
        ad_col = raw_col('ad')
        sr_col = raw_col('sr')
        wp_col = raw_col('wave_ptr')
        pp_col = raw_col('pulse_ptr')
        fp_col = raw_col('filter_ptr')
        vp_col = raw_col('vib_param')
        vd_col = raw_col('vib_delay')
        gt_col = raw_col('gate_timer', 0x02)  # default: gate timer 2
        fw_col = raw_col('first_wave', 0x41)  # default: pulse+gate
    else:
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
            fw_col[i] = WAVE_MAP.get(inst.waveform, 0x41)
            gt_col[i] = inst.gate_timer if inst.hr_method != 'none' else 0x80
            wp_col[i] = 1 if inst.wave_table else 0
            vp_col[i] = getattr(inst, 'vib_speed_idx', 0) or 0
            vd_col[i] = getattr(inst, 'vib_delay', 0) or 0
            pp_col[i] = getattr(inst, 'pulse_ptr', 0) or 0
            fp_col[i] = getattr(inst, 'filter_ptr', 0) or 0

    # Build wave table. If raw GT2 data is available, use it directly.
    # Otherwise rebuild from USF wave table steps.
    wave_l = bytearray()
    wave_r = bytearray()

    if not raw.get('wave_left'):
        # Build wave table with suffix-aware deduplication.
        # GT2's greloc.c shares suffixes: if inst B's steps are a suffix of
        # inst A's steps, B points into A's data (no duplication).

        def step_key(s):
            return (s.waveform, s.is_loop, s.loop_target, s.keep_freq,
                    s.absolute_note, s.note_offset, s.delay)

        # Two-pass: first emit all instruments in order, then resolve suffixes.
        # Pass 1: collect step tuples for all instruments
        all_steps = {}  # inst_idx → step_tuple
        for i, inst in enumerate(song.instruments):
            if inst.wave_table:
                all_steps[i] = tuple(step_key(s) for s in inst.wave_table)

        # Pass 2: emit in order. For each instrument, check if its steps
        # are a suffix of a LATER instrument's steps (which hasn't been
        # emitted yet). If so, skip it — it will be emitted as part of
        # the longer sequence. After all are emitted, point suffixes to
        # the correct offset within the longer sequence.
        #
        # Actually simpler: emit in order. After emitting, check if any
        # PREVIOUS instrument's steps are a suffix of this one. If so,
        # it was already emitted and we need to detect the overlap.
        #
        # Simplest correct approach: emit all in order, then post-process
        # to detect suffix sharing and adjust wave_ptr values.
        emitted = []  # list of (inst_idx, step_tuple, wt_offset)
        wt_offset = 1

        for i, inst in enumerate(song.instruments):
            if not inst.wave_table:
                continue
            steps = all_steps[i]

            # Check if this instrument's steps are a suffix of an already-emitted one
            found = False
            for ei, es, eo in emitted:
                if len(steps) <= len(es):
                    suffix_start = len(es) - len(steps)
                    if es[suffix_start:] == steps:
                        wp_col[i] = eo + suffix_start
                        found = True
                        break

            # Check if an already-emitted instrument is a suffix of THIS one
            # (this handles the case where a shorter instrument was emitted first
            # and a longer one containing it comes later — but greloc.c emits
            # in instrument order, so the shorter one gets its own slot)

            if found:
                continue

            emitted.append((i, steps, wt_offset))
            wp_col[i] = wt_offset
            inst_wt_start = wt_offset
            for step in inst.wave_table:
                    if step.is_loop:
                        wave_l.append(0xFF)
                        wave_r.append(inst_wt_start + step.loop_target)
                    elif step.delay > 0:
                        wave_l.append(step.delay)  # delay value < $10
                        # Right column: same format as waveform entries
                        if step.keep_freq:
                            wave_r.append(0x00)
                        elif step.absolute_note >= 0:
                            wave_r.append(step.absolute_note & 0x7F)
                        else:
                            wave_r.append((step.note_offset + 0x80) & 0xFF)
                    elif step.keep_freq:
                        wave_l.append(step.waveform)
                        wave_r.append(0x80)
                    elif step.absolute_note >= 0:
                        wave_l.append(step.waveform)
                        wave_r.append(step.absolute_note & 0x7F)
                    else:
                        wave_l.append(step.waveform)
                        wave_r.append((step.note_offset + 0x80) & 0xFF)
                has_loop = any(s.is_loop for s in inst.wave_table)
                if not has_loop:
                    wave_l.append(0xFF)
                    wave_r.append(0x00)
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

    # Convert orderlists. GT2 packed format:
    # - Always emit transpose byte before each pattern/group
    # - 2 repeats: write pattern byte twice
    # - 3+ repeats: write pattern once + $D0+(count-1)
    gt2_orderlists = []
    for vi in range(3):
        entries = song.orderlists[vi]
        ol = bytearray()
        i = 0
        while i < len(entries):
            patt_id, transpose = entries[i]

            # Count consecutive identical entries
            repeat_count = 1
            while (i + repeat_count < len(entries) and
                   entries[i + repeat_count] == entries[i]):
                repeat_count += 1

            # Emit transpose when changed (or first entry)
            if i == 0 or transpose != entries[i-1][1]:
                if transpose >= 0:
                    ol.append(0xF0 + transpose)
                else:
                    ol.append(0xE0 + (16 + transpose))

            if repeat_count <= 2:
                for _ in range(repeat_count):
                    ol.append(patt_id)
            else:
                ol.append(patt_id)
                ol.append(0xD0 + (repeat_count - 1))

            i += repeat_count

        ol.extend([0xFF, 0x00])
        gt2_orderlists.append(bytes(ol))

    # Pack (with optional custom freq table)
    freq_lo = getattr(song, 'freq_lo', None)
    freq_hi = getattr(song, 'freq_hi', None)

    # Raw GT2 table arrays are already extracted starting from the data
    # (operand+1), not from the operand. No trimming needed.

    sid_bytes, player_size = pack_sid(
        title=song.title,
        author=song.author,
        num_instruments=ni,
        freq_lo=freq_lo,
        freq_hi=freq_hi,
        instruments_ad=ad_col,
        instruments_sr=sr_col,
        instruments_firstwave=fw_col,
        instruments_gatetimer=gt_col,
        instruments_waveptr=wp_col,
        instruments_vibparam=vp_col,
        instruments_vibdelay=vd_col,
        instruments_pulseptr=pp_col,
        instruments_filtptr=fp_col,
        wave_left=raw.get('wave_left') or bytes(wave_l),
        wave_right=raw.get('wave_right') or bytes(wave_r),
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
