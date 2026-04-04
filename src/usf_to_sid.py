"""
usf_to_sid.py — Convert USF Song to GT2-format SID file.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import usf
from usf import Song, Pattern, NoteEvent
from sidfinity_pack import pack_sidfinity, ALL_COLUMNS
from gt2_to_usf import pack_wave_left, pack_wave_right, detect_nowavedelay

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

    # Compress consecutive rests.
    # Never emit a packed rest ($C0+) as the first byte of a pattern —
    # the SIDfinity player checks mt_chnpattptr==0 to detect "need new pattern",
    # and a packed rest at position 0 keeps pattptr at 0, causing the player
    # to re-read the orderlist on every tick 0 during the rest.
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
            # If this is at the start of the pattern, emit one explicit $BD first
            if len(packed) == 0 and count > 1:
                packed.append(GT2_REST)
                count -= 1
            while count > 0:
                if count == 1:
                    packed.append(GT2_REST)
                    count -= 1
                else:
                    chunk = min(count, 64)
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

    # Convert instruments to column arrays — built entirely from USF fields
    ni = len(song.instruments)
    if ni == 0:
        ni = 1
        song.instruments = [usf.Instrument()]

    ad_col = bytearray(ni)
    sr_col = bytearray(ni)
    wp_col = bytearray(ni)
    pp_col = bytearray(ni)
    fp_col = bytearray(ni)
    vp_col = bytearray(ni)
    vd_col = bytearray(ni)
    gt_col = bytearray(ni)
    fw_col = bytearray(ni)

    for i, inst in enumerate(song.instruments):
        ad_col[i] = inst.ad
        sr_col[i] = inst.sr
        wp_col[i] = inst.wave_ptr
        pp_col[i] = inst.pulse_ptr
        fp_col[i] = inst.filter_ptr
        vp_col[i] = inst.vib_speed_idx
        vd_col[i] = inst.vib_delay
        # Gate timer: reconstruct raw byte, or use stored raw value
        gt_col[i] = getattr(inst, '_gate_timer_raw', None) or (
            (inst.gate_timer & 0x3F) |
            (0x40 if inst.legato else 0) |
            (0x80 if inst.hr_method == 'none' else 0))
        fw_col[i] = inst.first_wave if inst.first_wave >= 0 else 0x41

    # Build wave table. Shared wave table stores .sng-equivalent values.
    # Pass them as-is — the SIDfinity packer handles the +$10 bias.
    # Right column: re-apply XOR $80 since the packer expects packed right bytes.
    wave_l = bytearray()
    wave_r = bytearray()

    if song.shared_wave_table:
        for sng_l, sng_r in song.shared_wave_table:
            wave_l.append(sng_l)
            # Right column: pack XOR $80 (except for commands/jumps)
            if sng_l >= 0xF0 or sng_l == 0xFF:
                wave_r.append(sng_r)
            else:
                wave_r.append(sng_r ^ 0x80)
    elif not raw.get('wave_left'):
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
                    # Jump: left=$FF, right=target index (no transform)
                    wave_l.append(0xFF)
                    wave_r.append(inst_wt_start + step.loop_target)
                elif step.delay > 0:
                    # Delay: .sng left stays as-is (no +$10 for delays)
                    sng_l = step.delay
                    if step.keep_freq: sng_r = 0x80
                    elif step.absolute_note >= 0: sng_r = 0x80 + step.absolute_note
                    else: sng_r = step.note_offset & 0xFF
                    wave_l.append(pack_wave_left(sng_l, nowavedelay))
                    wave_r.append(pack_wave_right(sng_r, sng_l))
                else:
                    # Waveform step
                    sng_l = step.waveform
                    if step.keep_freq: sng_r = 0x80
                    elif step.absolute_note >= 0: sng_r = 0x80 + step.absolute_note
                    else: sng_r = step.note_offset & 0xFF
                    wave_l.append(pack_wave_left(sng_l, nowavedelay))
                    wave_r.append(pack_wave_right(sng_r, sng_l))
            has_loop = any(s.is_loop for s in inst.wave_table)
            if not has_loop:
                wave_l.append(0xFF)
                wave_r.append(0x00)
                wt_offset += len(inst.wave_table) + 1
            else:
                wt_offset += len(inst.wave_table)
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
        entry_to_byte = {}
        entry_idx = 0
        i = 0
        while i < len(entries):
            patt_id, transpose = entries[i]

            repeat_count = 1
            while (i + repeat_count < len(entries) and
                   entries[i + repeat_count] == entries[i]):
                repeat_count += 1

            prev_trans = entries[i-1][1] if i > 0 else 0
            if transpose != prev_trans:
                if transpose >= 0:
                    ol.append(0xF0 + transpose)
                else:
                    ol.append(0xE0 + (16 + transpose))

            if repeat_count <= 2:
                for _ in range(repeat_count):
                    entry_to_byte[entry_idx] = len(ol)
                    entry_idx += 1
                    ol.append(patt_id)
            else:
                entry_to_byte[entry_idx] = len(ol)
                entry_idx += 1
                ol.append(patt_id)
                ol.append(0xD0 + (repeat_count - 1))
                for k in range(1, repeat_count):
                    entry_to_byte[entry_idx] = entry_to_byte[entry_idx - 1]
                    entry_idx += 1

            i += repeat_count

        restart_entry = song.orderlist_restart[vi] if hasattr(song, 'orderlist_restart') and vi < len(song.orderlist_restart) else 0
        restart_byte = entry_to_byte.get(restart_entry, 0)
        ol.extend([0xFF, restart_byte])
        gt2_orderlists.append(bytes(ol))

    # Pack (with optional custom freq table)
    freq_lo = getattr(song, 'freq_lo', None)
    freq_hi = getattr(song, 'freq_hi', None)

    # Build pulse/filter table bytes from shared tables
    pulse_l = bytearray()
    pulse_r = bytearray()
    if song.shared_pulse_table:
        for l, r in song.shared_pulse_table:
            pulse_l.append(l); pulse_r.append(r)

    filter_l = bytearray()
    filter_r = bytearray()
    if song.shared_filter_table:
        for l, r in song.shared_filter_table:
            filter_l.append(l); filter_r.append(r)

    # Build speed table bytes from USF speed_table entries
    speed_l = bytes([e.left for e in song.speed_table]) if song.speed_table else None
    speed_r = bytes([e.right for e in song.speed_table]) if song.speed_table else None

    # Build instruments dict for SIDfinity packer (all 9 columns)
    instruments = {
        'ad': bytes(ad_col),
        'sr': bytes(sr_col),
        'wave_ptr': bytes(wp_col),
        'pulse_ptr': bytes(pp_col),
        'filter_ptr': bytes(fp_col),
        'vib_param': bytes(vp_col),
        'vib_delay': bytes(vd_col),
        'gate_timer': bytes(gt_col),
        'first_wave': bytes(fw_col),
    }

    # Classify instruments for packer
    num_normal = num_nohr = num_legato = 0
    for g in gt_col:
        if g & 0x40: num_legato += 1
        elif g & 0x80: num_nohr += 1
        else: num_normal += 1

    sid_bytes, player_size = pack_sidfinity(
        songs=1,
        first_note=0,  # always full freq table
        last_note=95,
        default_tempo=getattr(song, 'tempo', 6) - 1,
        num_instruments=ni,
        num_normal=num_normal,
        num_nohr=num_nohr,
        num_legato=num_legato,
        instruments=instruments,
        wave_left=bytes(wave_l) if wave_l else bytes([0]),
        wave_right=bytes(wave_r) if wave_r else bytes([0]),
        pulse_left=bytes(pulse_l) if pulse_l else None,
        pulse_right=bytes(pulse_r) if pulse_r else None,
        filter_left=bytes(filter_l) if filter_l else None,
        filter_right=bytes(filter_r) if filter_r else None,
        speed_left=speed_l,
        speed_right=speed_r,
        orderlists=gt2_orderlists,
        patterns=gt2_patterns,
        title=song.title,
        author=song.author,
        psid_flags=getattr(song, 'psid_flags', 0x0014) if hasattr(song, 'psid_flags') else 0x0014,
        nowavedelay=True,  # USF stores .sng values → packer always needs to add bias
        ad_param=getattr(song, 'ad_param', 0x0F),
        sr_param=getattr(song, 'sr_param', 0x00),
        # Player behavior fields from USF
        adsr_write_order=getattr(song, 'adsr_write_order', 'sr_first'),
        loadregs_adsr_order=getattr(song, 'loadregs_adsr_order', 'sr_first'),
        newnote_reg_scope=getattr(song, 'newnote_reg_scope', 'wave_only'),
        ghost_regs=getattr(song, 'ghost_regs', 'none'),
        vibrato_param_fix=getattr(song, 'vibrato_param_fix', False),
        # Feature stripping — detect which features the song uses
        has_filter=bool(song.shared_filter_table) or any(i.filter_ptr > 0 for i in song.instruments),
        has_effects=any(i.vib_speed_idx > 0 for i in song.instruments) or
                    any(ev.command in (1,2,3,4) for p in song.patterns for ev in p.events if ev.command is not None),
        has_orderlist_features=any(t != 0 for ol in song.orderlists for _, t in ol) or
                               any(len(set(ol)) < len(ol) and len(ol) > 2 for ol in song.orderlists),
        has_tick0fx=any(ev.command is not None and ev.command != 0
                        for p in song.patterns for ev in p.events),
        # Per-song V2 code generation
        # use_codegen=True,
        song=song,
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
