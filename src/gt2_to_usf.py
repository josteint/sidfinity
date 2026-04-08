"""
gt2_to_usf.py - Convert GoatTracker V2 SID files to Universal Symbolic Format.

Uses gt2_decompile for ALL data extraction (the single source of truth
for table boundaries, pattern parsing, column detection). Then populates
USF Song objects from the decompiled data.

Pipeline: SID → gt2_decompile → raw data → this module → USF Song
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usf import Song, Instrument, WaveTableStep, SpeedTableEntry, Pattern, NoteEvent
from gt2_decompile import decompile_gt2
from gt2_detect_version import detect_gt2_player_group


def detect_nowavedelay(binary, code_end):
    """Detect NOWAVEDELAY from the player binary.

    The wave delay pattern is: CMP #$10 / BCS +offset / ... / SBC #$10
    The BCS target must point to an SBC #$10 instruction. Without this
    check, unrelated CMP #$10 / BCS sequences (e.g. tempo handling) cause
    false positives -- see Radar_Love.sid.
    """
    for i in range(code_end - 3):
        if binary[i] == 0xC9 and binary[i + 1] == 0x10 and binary[i + 2] == 0xB0:
            # BCS offset is a signed relative branch from the byte AFTER the BCS operand
            bcs_offset = binary[i + 3]
            target = i + 4 + bcs_offset
            if target < code_end - 1 and binary[target] == 0xE9 and binary[target + 1] == 0x10:
                return False  # has delay feature (NOWAVEDELAY=0)
    return True  # no delay (NOWAVEDELAY=1)


def pack_wave_left(sng_left, nowavedelay):
    """Apply wave left transform: .sng → packed format.

    .sng $E0-$EF encodes inaudible/silent waveforms (SID register $00-$0F).
    With bias (nowavedelay=False): pack to $10-$1F (player SBC $10 → $00-$0F).
    Without bias (nowavedelay=True): pack to $00-$0F (player writes directly).
    """
    if sng_left >= 0xF0 or sng_left == 0xFF:
        return sng_left
    if nowavedelay:
        # No WAVE_DELAY: values written directly to SID.
        # .sng $E0-$EF encodes low waveforms ($00-$0F) — extract actual value.
        if 0xE0 <= sng_left <= 0xEF:
            return sng_left & 0x0F
        return sng_left
    if sng_left >= 0xE0:
        return (sng_left & 0x0F) + 0x10
    if sng_left >= 0x10:
        return sng_left + 0x10
    return sng_left


def pack_wave_right(sng_right, sng_left):
    """Apply wave right transform: .sng → packed format."""
    if sng_left >= 0xF0:
        return sng_right
    return sng_right ^ 0x80


def gt2_to_usf(sid_path):
    """Convert a GoatTracker V2 SID file to USF Song.

    Uses gt2_decompile as the single source of truth for data extraction.
    """
    # Step 1: Decompile — extracts all raw data with correct boundaries
    d = decompile_gt2(sid_path)
    if d is None:
        return None

    # Step 2: Detect player version for behavioral parameters
    ver = detect_gt2_player_group(sid_path)

    ni = d['ni']
    columns = d['columns']

    # Derive behavioral parameters from player group
    group = ver['group'] if ver else 'B'  # default to Group B (most common)
    # BUFFEREDWRITES detected from binary.
    # BW=0: ADSR/pulse written inline (directly to SID), loadregs = freq+wave only
    # BW=1: all regs flushed via loadregs at end of channel processing
    bw = d.get('buffered_writes', True)
    if group == 'A':
        adsr_order = 'ad_first'
        loadregs_order = 'ad_first'
        newnote_scope = 'all_regs'  # Group A always writes freq on new-note
        vib_fix = False
    elif group == 'C':
        adsr_order = 'sr_first'
        loadregs_order = 'ad_first'  # Group C reverted loadregs to AD-first
        newnote_scope = 'all_regs' if bw else 'wave_only'
        vib_fix = False
    elif group == 'D':
        adsr_order = 'sr_first'
        loadregs_order = 'sr_first'
        newnote_scope = 'all_regs' if bw else 'wave_only'
        vib_fix = True
    else:  # B or unknown
        adsr_order = 'sr_first'
        loadregs_order = 'sr_first'
        newnote_scope = 'all_regs' if bw else 'wave_only'
        vib_fix = False

    # Build Song
    song = Song(
        title='',  # TODO: extract from PSID header
        author='',
        sid_model='8580' if d.get('psid_flags', 0) & 0x20 else '6581',
        clock='NTSC' if d.get('psid_flags', 0) & 0x08 else 'PAL',
        tempo=6,  # will be overridden below
        first_note=d['first_note'],
        gt2_player_group=ver['group'] if ver else '',
        ad_param=d.get('ad_param', 0x0F),
        sr_param=d.get('sr_param', 0x00),
        psid_flags=d.get('psid_flags', 0x0014),
        adsr_write_order=adsr_order,
        loadregs_adsr_order=loadregs_order,
        newnote_reg_scope=newnote_scope,
        vibrato_param_fix=vib_fix,
    )

    # Pass original frequency tables and nowavedelay through to packer
    song.freq_lo = d.get('freq_lo')
    song.freq_hi = d.get('freq_hi')
    song.nowavedelay = d.get('nowavedelay', True)

    # DEFAULTTEMPO: extract from binary
    with open(sid_path, 'rb') as f:
        data = f.read()
    from gt_parser import parse_psid_header, find_freq_table
    header, binary, la = parse_psid_header(data)

    # Extract title/author from PSID header
    song.title = data[22:54].split(b'\x00')[0].decode('latin-1', errors='replace').strip()
    song.author = data[54:86].split(b'\x00')[0].decode('latin-1', errors='replace').strip()

    ft = find_freq_table(binary, la)
    if ft:
        code_end = ft[0]
        for i in range(code_end - 8):
            if (binary[i] == 0xA9 and binary[i + 2] == 0x9D and
                    binary[i + 5] == 0xA9 and binary[i + 6] == 0x01 and
                    binary[i + 7] == 0x9D):
                song.tempo = binary[i + 1] + 1
                break

    # Shared tables — unpack from packed format to .sng format for USF.
    # The decompiler returns raw packed bytes. USF stores .sng values
    # (musical representation). The encoder repacks when building SIDs.
    nowavedelay = d.get('nowavedelay', detect_nowavedelay(binary, code_end if ft else len(binary)))
    wl = d['wave_left']
    wr = d['wave_right']
    song.shared_wave_table = []
    for i in range(len(wl)):
        packed_l = wl[i]
        packed_r = wr[i] if i < len(wr) else 0x00
        # Unpack left: reverse +$10 bias
        if packed_l >= 0xF0 or packed_l == 0xFF:
            sng_l = packed_l  # commands/jumps unchanged
        elif not nowavedelay and 0x10 <= packed_l <= 0x1F:
            # Packed $1x comes from .sng $Ex (inaudible waveforms: SID reg $00-$0F)
            # pack_wave_left maps .sng $Ex → (sng & $0F) + $10, reverse is:
            sng_l = (packed_l & 0x0F) | 0xE0
        elif not nowavedelay and 0x20 <= packed_l <= 0xEF:
            sng_l = packed_l - 0x10  # remove bias
        else:
            sng_l = packed_l
        # Unpack right: reverse XOR $80 (only for non-command, non-jump entries)
        if packed_l >= 0xF0:
            sng_r = packed_r  # command: right is parameter, no XOR
        elif packed_l == 0xFF:
            sng_r = packed_r  # jump: right is target index, no XOR
        else:
            sng_r = packed_r ^ 0x80  # reverse XOR
        song.shared_wave_table.append((sng_l, sng_r))

    pl = d['pulse_left']
    pr = d['pulse_right']
    simplepulse = ver.get('simplepulse', 0) if ver else 0
    # Pulse speed ASL doubling: some original players use ASL to double the
    # pulse speed byte before adding. Our rebuilt player uses CLC (no doubling),
    # so we must double the speed data to compensate.
    # Only applies to modulation entries (left < $80), never set-pulse (left >= $80).
    pulse_asl = ver.get('pulse_speed_asl', False) if ver else False
    if pl and pr:
        pulse_table = []
        for i in range(min(len(pl), len(pr))):
            left = pl[i]
            right = pr[i]
            if simplepulse == 1 and left >= 0x80 and left != 0xFF:
                # simplepulse SET: original player writes right byte to BOTH
                # D402 and D403. V2 player writes left->D403, right->D402.
                # Transform: set left = $80 | right. The $80 bit keeps it as a
                # SET command (>= $80). The low nibble matches right. SID ignores
                # PW_HI bits 4-7, so the 12-bit effective pulse width matches.
                left = 0x80 | right
            if pulse_asl and left < 0x80 and left != 0x00:
                # Double speed byte (signed): ASL = shift left 1 bit
                right = (right * 2) & 0xFF
            pulse_table.append((left, right))
        song.shared_pulse_table = pulse_table

    fl = d['filter_left']
    fr = d['filter_right']
    if fl and fr:
        song.shared_filter_table = [(fl[i], fr[i]) for i in range(min(len(fl), len(fr)))]

    sl = d['speed_left']
    sr = d['speed_right']
    if sl and sr:
        for i in range(min(len(sl), len(sr))):
            song.speed_table.append(SpeedTableEntry(left=sl[i], right=sr[i]))

    # Instruments from column data
    col_names = ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr',
                 'vib_param', 'vib_delay', 'gate_timer', 'first_wave']

    for y in range(ni):
        def col(name, default=0):
            vals = columns.get(name, [])
            return vals[y] if y < len(vals) else default

        ad = col('ad')
        sr_val = col('sr')
        wp = col('wave_ptr')
        pp = col('pulse_ptr')
        fp = col('filter_ptr')
        vp = col('vib_param')
        vd = col('vib_delay')
        gt_byte = col('gate_timer', 2)
        fw_byte = col('first_wave', 0x09)

        # Waveform from first_wave byte
        if fw_byte in (0, 0xFE, 0xFF):
            waveform = 'pulse'
        else:
            wave_bits = (fw_byte >> 4) & 0xF
            waveform = {1: 'tri', 2: 'saw', 4: 'pulse', 8: 'noise'}.get(wave_bits, 'pulse')

        hr = 'none' if gt_byte & 0x80 else 'gate'

        # Per-instrument wave table steps (from shared wave table, .sng format)
        wt = []
        swt = song.shared_wave_table
        if wp > 0 and wp - 1 < len(swt):
            idx = wp - 1
            while idx < len(swt) and len(wt) < 64:
                left, right = swt[idx]

                if left == 0xFF:
                    if right > 0:
                        loop_target = max(0, right - wp)
                        wt.append(WaveTableStep(is_loop=True, loop_target=loop_target))
                    break
                elif left < 0x10:
                    # .sng right: $80=keep freq, $81-$DF=absolute, $00-$7F=relative
                    if right == 0x80:
                        wt.append(WaveTableStep(delay=left, keep_freq=True))
                    elif right > 0x80:
                        wt.append(WaveTableStep(delay=left, absolute_note=right & 0x7F))
                    else:
                        rel = right if right < 0x40 else right - 0x80
                        wt.append(WaveTableStep(delay=left, note_offset=rel))
                else:
                    if right == 0x80:
                        wt.append(WaveTableStep(waveform=left, keep_freq=True))
                    elif right > 0x80:
                        wt.append(WaveTableStep(waveform=left, absolute_note=right & 0x7F))
                    else:
                        rel = right if right < 0x40 else right - 0x80
                        wt.append(WaveTableStep(waveform=left, note_offset=rel))
                idx += 1

        if not wt:
            wt = [WaveTableStep(waveform=0x41, note_offset=0),
                  WaveTableStep(is_loop=True, loop_target=0)]

        inst = Instrument(
            id=y, ad=ad, sr=sr_val, waveform=waveform,
            first_wave=fw_byte,
            hr_method=hr,
            gate_timer=gt_byte & 0x3F,
            legato=bool(gt_byte & 0x40),
            wave_ptr=wp,
            vib_speed_idx=vp,
            vib_delay=vd,
            wave_table=wt,
            pulse_ptr=pp,
            filter_ptr=fp,
        )
        inst._gate_timer_raw = gt_byte
        song.instruments.append(inst)

    # Patterns — decode from raw packed bytes
    for pi, patt_bytes in enumerate(d['patterns']):
        patt = Pattern(id=pi)
        _decode_pattern(patt_bytes, patt)
        song.patterns.append(patt)

    # Orderlists — decode from raw bytes
    for vi, ol_bytes in enumerate(d['orderlists'][:3]):
        entries, restart = _decode_orderlist(ol_bytes)
        song.orderlists[vi] = entries
        song.orderlist_restart[vi] = restart

    return song


def _decode_pattern(patt_bytes, patt):
    """Decode GT2 packed pattern bytes into NoteEvent objects."""
    prev_cmd = None
    prev_param = 0
    p = 0

    while p < len(patt_bytes):
        byte = patt_bytes[p]
        if byte == 0x00:
            break  # ENDPATT

        inst = -1
        cmd = None
        cmd_val = 0

        # Instrument byte
        if byte < 0x40:
            inst = byte - 1  # 1-based in pattern
            p += 1
            if p >= len(patt_bytes):
                break
            byte = patt_bytes[p]

        # FX + note
        if 0x40 <= byte <= 0x4F:
            cmd = byte & 0x0F
            p += 1
            if cmd != 0 and p < len(patt_bytes):
                cmd_val = patt_bytes[p]
                p += 1
            if p < len(patt_bytes):
                note_byte = patt_bytes[p]
                p += 1
                if 0x60 <= note_byte <= 0xBC:
                    patt.events.append(NoteEvent(
                        type='note', note=note_byte - 0x60,
                        instrument=inst, command=cmd, command_val=cmd_val))
                elif note_byte == 0xBD:
                    patt.events.append(NoteEvent(
                        type='rest', instrument=inst, command=cmd, command_val=cmd_val))
                elif note_byte == 0xBE:
                    patt.events.append(NoteEvent(
                        type='off', instrument=inst, command=cmd, command_val=cmd_val))
                elif note_byte == 0xBF:
                    patt.events.append(NoteEvent(
                        type='on', instrument=inst, command=cmd, command_val=cmd_val))
            continue

        # FXONLY
        if 0x50 <= byte <= 0x5F:
            cmd = byte & 0x0F
            p += 1
            if cmd != 0 and p < len(patt_bytes):
                cmd_val = patt_bytes[p]
                p += 1
            patt.events.append(NoteEvent(
                type='rest', instrument=inst, command=cmd, command_val=cmd_val))
            continue

        # Note
        if 0x60 <= byte <= 0xBC:
            patt.events.append(NoteEvent(
                type='note', note=byte - 0x60, instrument=inst))
            p += 1
            continue

        # Rest
        if byte == 0xBD:
            patt.events.append(NoteEvent(type='rest', instrument=inst))
            p += 1
            continue

        # Keyoff
        if byte == 0xBE:
            patt.events.append(NoteEvent(type='off', instrument=inst))
            p += 1
            continue

        # Keyon
        if byte == 0xBF:
            patt.events.append(NoteEvent(type='on', instrument=inst))
            p += 1
            continue

        # Packed rest
        if byte >= 0xC0:
            count = 256 - byte
            for _ in range(count):
                patt.events.append(NoteEvent(type='rest'))
            p += 1
            continue

        p += 1


def _decode_orderlist(ol_bytes):
    """Decode GT2 packed orderlist bytes into (pattern_id, transpose) list + restart index."""
    entries = []
    current_trans = 0
    restart = 0
    p = 0

    while p < len(ol_bytes):
        byte = ol_bytes[p]

        if byte == 0xFF:
            # End marker — next byte is restart position
            if p + 1 < len(ol_bytes):
                restart_byte = ol_bytes[p + 1]
                # Convert byte offset to entry index
                byte_to_entry = {}
                entry_idx = 0
                scan = 0
                while scan < p:
                    b = ol_bytes[scan]
                    if b >= 0xE0:
                        scan += 1
                        continue
                    elif b >= 0xD0:
                        scan += 1
                        continue
                    else:
                        byte_to_entry[scan] = entry_idx
                        entry_idx += 1
                        scan += 1
                restart = byte_to_entry.get(restart_byte, 0)
            break

        if byte >= 0xF0:
            current_trans = byte - 0xF0
            p += 1
            continue
        if byte >= 0xE0:
            current_trans = byte - 256 + 16  # negative transpose
            p += 1
            continue
        if byte >= 0xD0:
            # Repeat: previous entry repeated (byte - 0xD0) more times
            count = byte - 0xD0
            if entries:
                for _ in range(count):
                    entries.append(entries[-1])
            p += 1
            continue

        # Pattern ID
        entries.append((byte, current_trans))
        p += 1

    return entries, restart


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: gt2_to_usf.py <file.sid>")
        sys.exit(1)

    song = gt2_to_usf(sys.argv[1])
    if song:
        print(f'Title: {song.title}')
        print(f'Author: {song.author}')
        print(f'Instruments: {len(song.instruments)}')
        print(f'Patterns: {len(song.patterns)}')
        print(f'Wave table: {len(song.shared_wave_table)}')
        print(f'Pulse table: {len(song.shared_pulse_table)}')
        print(f'Filter table: {len(song.shared_filter_table)}')
        print(f'Speed table: {len(song.speed_table)}')
        print(f'Tempo: {song.tempo}')
        print(f'Player group: {song.gt2_player_group}')
        print(f'ADPARAM: ${song.ad_param:02X}')
