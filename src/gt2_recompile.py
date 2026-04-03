"""
gt2_recompile.py -- Raw roundtrip: decompile GT2 SID -> recompile with gt2asm.

Bypasses USF entirely. Extracts all data via decompile_gt2(), detects the
player version, and feeds the raw (already-transformed) data straight into
pack_gt2(). This tests the decompiler+packer pair in isolation.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt2_decompile import decompile_gt2
from gt2_detect_version import detect_gt2_player_group
from gt2_parse_direct import parse_gt2_direct
from detect_flags import detect_gt2_flags
from gt2_packer import pack_gt2


def detect_noauthorinfo(binary, la, code_end):
    """Detect whether the original SID had NOAUTHORINFO=0.

    When NOAUTHORINFO=0, player.s places a 32-byte author block at
    base+$20 (mt_author). This block is all zeros unless the user typed
    something. Check if the code_end is large enough that the player
    includes the author info block (indicated by code being >=$40 bytes
    and the region at $20-$3F being all zero or ASCII text).

    Returns 0 (author info present) or 1 (no author info).
    """
    # The author block is at offset $20 from base (offset $20 in binary).
    # If the player code extends past $40 and there's a 32-byte region
    # at $20 that's either all zeros or contains printable ASCII, it's
    # likely an author info block.
    if code_end < 0x40:
        return 1  # code too small to contain author block

    block = binary[0x20:0x40]
    # Author info block is typically all zeros (unused) or ASCII text
    is_author = all(b == 0 or (0x20 <= b <= 0x7E) for b in block)
    if is_author:
        # Additional check: the byte at $20 should be 0 (start of zeroed block)
        # or a printable char. If the code there is clearly 6502 instructions
        # (opcodes like $A9, $BD, $9D, etc.), it's NOT author info.
        # Common 6502 opcodes that would appear at $20:
        opcodes = {0xA9, 0xA2, 0xA0, 0xBD, 0xB9, 0x9D, 0x99, 0x4C, 0x20,
                   0x60, 0xE8, 0xCA, 0xC8, 0x88, 0xD0, 0xF0, 0x10, 0x30,
                   0x8D, 0xAD, 0x0A, 0x4A, 0x29, 0x09, 0x49, 0xC9, 0xE0}
        # If the block starts with typical opcodes, it's code not author info
        if block[0] in opcodes and block[1] != 0:
            return 1
        return 0

    return 1


def detect_flags_from_decompiled(d, r):
    """Detect GT2 compilation flags from decompiled data and parse_gt2_direct result.

    This mirrors detect_gt2_flags() but works directly on raw decompiled data
    rather than USF Song objects. The column presence in the original binary
    determines which flags are set.
    """
    columns = d['columns']
    ni = d['ni']

    # All flags start as 1 (disabled/optimized out)
    F = {}
    for k in ['NOEFFECTS', 'NOGATE', 'NOFILTER', 'NOFILTERMOD', 'NOPULSE', 'NOPULSEMOD',
              'NOWAVEDELAY', 'NOWAVECMD', 'NOREPEAT', 'NOTRANS', 'NOPORTAMENTO', 'NOTONEPORTA',
              'NOVIB', 'NOINSTRVIB', 'NOSETAD', 'NOSETSR', 'NOSETWAVE', 'NOSETWAVEPTR',
              'NOSETPULSEPTR', 'NOSETFILTPTR', 'NOSETFILTCTRL', 'NOSETFILTCUTOFF',
              'NOSETMASTERVOL', 'NOFUNKTEMPO', 'NOGLOBALTEMPO', 'NOCHANNELTEMPO',
              'NOFIRSTWAVECMD', 'NOCALCULATEDSPEED', 'NONORMALSPEED', 'NOZEROSPEED']:
        F[k] = 1

    speed_left = list(d.get('speed_left', b''))

    def calcspeedtest(pos):
        if pos == 0:
            F['NOZEROSPEED'] = 0
            return
        if pos - 1 < len(speed_left):
            if speed_left[pos - 1] >= 0x80:
                F['NOCALCULATEDSPEED'] = 0
            else:
                F['NONORMALSPEED'] = 0
        else:
            F['NOCALCULATEDSPEED'] = 0
            F['NONORMALSPEED'] = 0

    # --- Column presence from the original binary ---
    col_data = r.get('col_data', {}) if r else {}
    if 'pulse_ptr' in col_data:
        F['NOPULSE'] = 0
    if 'filter_ptr' in col_data:
        F['NOFILTER'] = 0
    if 'vib_param' in col_data:
        F['NOINSTRVIB'] = 0
        F['NOVIB'] = 0

    # --- Scan orderlists for NOREPEAT and NOTRANS ---
    orderlists = d.get('orderlists', [])
    for ol in orderlists[:3]:
        # Check for repeat markers ($D0-$DF)
        for b in ol:
            if 0xD0 <= b <= 0xDF:
                F['NOREPEAT'] = 0
        # Check for transpose markers ($E0-$FF except $FF end marker)
        for i, b in enumerate(ol):
            if b == 0xFF:
                break  # end marker
            if 0xE0 <= b <= 0xFE:
                F['NOTRANS'] = 0

    # --- Scan patterns for effects ---
    for patt in d.get('patterns', []):
        p = 0
        while p < len(patt):
            byte = patt[p]
            if byte == 0x00:
                break  # ENDPATT
            if byte < 0x40:
                # Instrument byte (skip)
                p += 1
                continue
            if 0x40 <= byte <= 0x4F:
                # NOTE+FX: $40+cmd
                cmd = byte - 0x40
                p += 1
                if cmd != 0:
                    F['NOEFFECTS'] = 0
                    _scan_command(cmd, patt[p] if p < len(patt) else 0, F, calcspeedtest)
                    p += 1
                else:
                    F['NOEFFECTS'] = 0
                continue
            if 0x50 <= byte <= 0x5F:
                # FXONLY: $50+cmd
                cmd = byte - 0x50
                p += 1
                if cmd != 0:
                    F['NOEFFECTS'] = 0
                    _scan_command(cmd, patt[p] if p < len(patt) else 0, F, calcspeedtest)
                    p += 1
                else:
                    F['NOEFFECTS'] = 0
                continue
            if 0x60 <= byte <= 0xBC:
                p += 1  # note
                continue
            if byte == 0xBD:
                p += 1  # rest
                continue
            if byte == 0xBE:
                F['NOGATE'] = 0
                p += 1  # keyoff
                continue
            if byte == 0xBF:
                F['NOGATE'] = 0
                p += 1  # keyon
                continue
            if byte >= 0xC0:
                p += 1  # packed rest
                continue
            p += 1

    # --- Scan instruments ---
    vib_col = columns.get('vib_param', [])
    for v in vib_col:
        if v > 0:
            F['NOINSTRVIB'] = 0
            F['NOVIB'] = 0
            calcspeedtest(v)

    pulse_col = columns.get('pulse_ptr', [])
    for v in pulse_col:
        if v > 0:
            F['NOPULSE'] = 0

    filter_col = columns.get('filter_ptr', [])
    for v in filter_col:
        if v > 0:
            F['NOFILTER'] = 0

    fw_col = columns.get('first_wave', [])
    for v in fw_col:
        if v in (0, 0xFE, 0xFF):
            F['NOFIRSTWAVECMD'] = 0

    # --- Scan wave table ---
    wl = d.get('wave_left', b'')
    wr = d.get('wave_right', b'')
    for i in range(len(wl)):
        l = wl[i]
        if l == 0xFF:
            continue
        if 0 < l < 0x10:
            F['NOWAVEDELAY'] = 0
        # In packed binary, wave commands are already transformed.
        # Silent waves ($E0-$EF in .sng) are masked to $00-$0F in packed.
        # Wave commands ($F0-$FE) remain as-is.
        if 0xF0 <= l <= 0xFE:
            F['NOWAVECMD'] = 0
            wave_cmd = l - 0xE0  # original command index
            # Actually in packed format, the left byte IS the command byte
            # Commands: $F0=vibrato speed set, etc.
            # Map packed command to original: $F0→cmd 0x10, but GT2 uses
            # the left byte value directly for command dispatch.
            # The right byte for speed commands points into speed table.
            r_val = wr[i] if i < len(wr) else 0
            if l in (0xF1, 0xF2, 0xF3, 0xF4):
                calcspeedtest(r_val)
            if l == 0xF9:
                F['NOPULSE'] = 0
            if l == 0xFA:
                F['NOFILTER'] = 0

    # --- Scan pulse table ---
    pl = d.get('pulse_left', b'')
    for b in pl:
        if b == 0xFF:
            continue
        if 0 < b < 0x80:
            F['NOPULSEMOD'] = 0

    # --- Scan filter table ---
    fl = d.get('filter_left', b'')
    for b in fl:
        if b == 0xFF:
            continue
        if 0 < b < 0x80:
            F['NOFILTERMOD'] = 0

    # --- FIXEDPARAMS ---
    FIXEDPARAMS = 1
    if 'gate_timer' in columns:
        FIXEDPARAMS = 0
    elif ni > 1:
        gt_col = columns.get('gate_timer', [])
        fw_col = columns.get('first_wave', [])
        if gt_col and len(set(gt_col)) > 1:
            FIXEDPARAMS = 0
        if fw_col and len(set(fw_col)) > 1:
            FIXEDPARAMS = 0

    # --- SIMPLEPULSE ---
    SIMPLEPULSE = 1
    for b in pl:
        if 0x80 <= b < 0xFF:
            SIMPLEPULSE = 0
            break

    F['FIXEDPARAMS'] = FIXEDPARAMS
    F['SIMPLEPULSE'] = SIMPLEPULSE

    # --- Flag dependencies ---
    if F['NOFILTER']:
        F['NOFILTERMOD'] = 1
    if F['NOPULSE']:
        F['NOPULSEMOD'] = 1
    if F['NOVIB']:
        F['NOINSTRVIB'] = 1
    if F['NOEFFECTS']:
        for k in ['NOSETAD', 'NOSETSR', 'NOSETWAVE', 'NOSETWAVEPTR', 'NOSETPULSEPTR',
                   'NOSETFILTPTR', 'NOSETFILTCTRL', 'NOSETFILTCUTOFF', 'NOSETMASTERVOL']:
            F[k] = 1

    return F


def _scan_command(cmd, val, F, calcspeedtest):
    """Update flags for a pattern command byte."""
    if cmd == 5: F['NOSETAD'] = 0
    if cmd == 6: F['NOSETSR'] = 0
    if cmd == 7: F['NOSETWAVE'] = 0
    if cmd == 8: F['NOSETWAVEPTR'] = 0
    if cmd == 9: F['NOSETPULSEPTR'] = 0
    if cmd == 10: F['NOSETFILTPTR'] = 0
    if cmd == 11: F['NOSETFILTCTRL'] = 0
    if cmd == 12: F['NOSETFILTCUTOFF'] = 0
    if cmd == 13: F['NOSETMASTERVOL'] = 0
    if cmd in (1, 2, 3, 4):
        calcspeedtest(val)
    if cmd == 14:
        F['NOFUNKTEMPO'] = 0
        F['NOGLOBALTEMPO'] = 0
    if cmd == 15:
        if (val & 0x7F) < 3:
            F['NOFUNKTEMPO'] = 0
        if val & 0x80:
            F['NOCHANNELTEMPO'] = 0
        else:
            F['NOGLOBALTEMPO'] = 0


def classify_instruments_raw(gate_timer_col):
    """Classify instruments into normal/nohr/legato from raw gate_timer bytes.
    Returns (num_normal, num_nohr, num_legato)."""
    num_normal = num_nohr = num_legato = 0
    for gt in gate_timer_col:
        if gt & 0x40:
            num_legato += 1
        elif gt & 0x80:
            num_nohr += 1
        else:
            num_normal += 1
    return num_normal, num_nohr, num_legato


def recompile_gt2(sid_path, output_path):
    """Decompile a GT2 SID and recompile it from raw extracted data.

    This is the "raw roundtrip" test: the data has already been transformed
    by the original greloc.c packer, so we emit it as-is without re-transforming.

    Returns dict with status info, or raises on failure.
    """
    # Step 1: Decompile
    d = decompile_gt2(sid_path)
    if d is None:
        raise ValueError(f"Failed to decompile {sid_path}")

    # Step 2: Get parse_gt2_direct result for flag detection
    r = parse_gt2_direct(sid_path)
    if r is None:
        raise ValueError(f"Failed to parse {sid_path}")

    # Step 3: Detect player version
    version_info = detect_gt2_player_group(sid_path)
    player_group = version_info['group'] if version_info else ''

    # Step 4: Detect flags from raw data + binary structure
    flags = detect_flags_from_decompiled(d, r)

    # Step 5: Extract instrument data
    columns = d['columns']
    ni = d['ni']

    ad_col = bytes(columns.get('ad', [0x09] * ni))
    sr_col = bytes(columns.get('sr', [0x00] * ni))
    wp_col = bytes(columns.get('wave_ptr', [0x00] * ni))
    pp_col = bytes(columns.get('pulse_ptr', [0x00] * ni)) if 'pulse_ptr' in columns else None
    fp_col = bytes(columns.get('filter_ptr', [0x00] * ni)) if 'filter_ptr' in columns else None
    vp_col = bytes(columns.get('vib_param', [0x00] * ni)) if 'vib_param' in columns else None
    vd_col = bytes(columns.get('vib_delay', [0x00] * ni)) if 'vib_delay' in columns else None
    gt_col = bytes(columns.get('gate_timer', [0x02] * ni)) if 'gate_timer' in columns else None
    fw_col = bytes(columns.get('first_wave', [0x09] * ni)) if 'first_wave' in columns else None

    # Instrument classification (from gate_timer column if present)
    if gt_col is not None:
        num_normal, num_nohr, num_legato = classify_instruments_raw(gt_col)
    else:
        num_normal, num_nohr, num_legato = ni, 0, 0

    # Fixed params: extract from first instrument (or column data)
    first_wave_param = fw_col[0] if fw_col else 0x09
    gate_timer_param = (gt_col[0] & 0x3F) if gt_col else 0x02

    # Step 6: Determine default tempo from orderlists
    # The first byte of each orderlist is typically the tempo-1 value,
    # but it's actually embedded in the pattern data. Use 5 as default.
    default_tempo = 5

    # Step 7: Read the original PSID header for title/author and flags
    with open(sid_path, 'rb') as f:
        sid_data = f.read()
    title = sid_data[0x16:0x36].split(b'\x00')[0].decode('latin-1', errors='replace')
    author = sid_data[0x36:0x56].split(b'\x00')[0].decode('latin-1', errors='replace')

    # Extract PSID flags (offset 0x76, big-endian 16-bit) — encodes clock + SID model
    import struct
    psid_flags = struct.unpack_from('>H', sid_data, 0x76)[0] if len(sid_data) > 0x77 else 0x0014

    # Step 8: Detect NOAUTHORINFO from original binary
    from gt_parser import parse_psid_header
    header, binary, la = parse_psid_header(sid_data)
    noauthorinfo = detect_noauthorinfo(binary, la, d['code_end'])

    # Step 9: Pack using gt2_packer
    sid_bytes, player_size = pack_gt2(
        flags=flags,
        base_addr=la,
        songs=1,
        first_note=d['first_note'],
        last_note=95,
        default_tempo=default_tempo,
        num_instruments=ni,
        num_normal=num_normal,
        num_nohr=num_nohr,
        num_legato=num_legato,
        ad_param=0x0F,
        sr_param=0x00,
        first_wave_param=first_wave_param,
        gate_timer_param=gate_timer_param,
        instruments_ad=ad_col,
        instruments_sr=sr_col,
        instruments_waveptr=wp_col,
        instruments_pulseptr=pp_col,
        instruments_filtptr=fp_col,
        instruments_vibparam=vp_col,
        instruments_vibdelay=vd_col,
        instruments_gatetimer=gt_col,
        instruments_firstwave=fw_col,
        wave_left=d['wave_left'],
        wave_right=d['wave_right'],
        pulse_left=d['pulse_left'] or None,
        pulse_right=d['pulse_right'] or None,
        filter_left=d['filter_left'] or None,
        filter_right=d['filter_right'] or None,
        speed_left=d['speed_left'] or None,
        speed_right=d['speed_right'] or None,
        orderlists=d['orderlists'],
        patterns=d['patterns'],
        freq_lo=d['freq_lo'],
        freq_hi=d['freq_hi'],
        title=title,
        author=author,
        noauthorinfo=noauthorinfo,
        player_group=player_group,
        psid_flags=psid_flags,
    )

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(sid_bytes)

    return {
        'status': 'ok',
        'input': sid_path,
        'output': output_path,
        'ni': ni,
        'num_patt': d['num_patt'],
        'wave_size': d['wave_size'],
        'player_group': player_group,
        'player_size': player_size,
        'sid_size': len(sid_bytes),
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: gt2_recompile.py <file.sid> [output.sid] [--compare] [--duration N]")
        sys.exit(1)

    sid_path = sys.argv[1]
    compare = '--compare' in sys.argv
    duration = 10
    for i, a in enumerate(sys.argv):
        if a == '--duration' and i + 1 < len(sys.argv):
            duration = int(sys.argv[i + 1])

    output_path = None
    for a in sys.argv[2:]:
        if a.endswith('.sid') and not a.startswith('--'):
            output_path = a
            break
    if output_path is None:
        output_path = '/tmp/gt2_recompiled.sid'

    try:
        result = recompile_gt2(sid_path, output_path)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    name = os.path.basename(sid_path)
    print(f"{name}: group={result['player_group']} ni={result['ni']} "
          f"patt={result['num_patt']} wave={result['wave_size']} "
          f"size={result['sid_size']}")
    print(f"  Written to: {output_path}")

    if compare:
        from gt2_compare import compare_sids_tolerant, print_results
        comp = compare_sids_tolerant(sid_path, output_path, duration)
        if comp is None:
            print("  Comparison failed (siddump error)")
        else:
            print()
            print_results(comp, name)
