"""
sidfinity_pack.py — Pack GT2 music data using the SIDfinity player + xa65.

Unlike gt2_packer.py which uses gt2asm + conditional compilation flags,
this packer:
  - Uses xa65 assembler (with -XMASM for colon-in-comment support)
  - Always includes ALL features (all NOxxx = 0)
  - Always emits ALL 9 instrument columns (pad with zeros if missing)
  - No NOAUTHORINFO block, no FIXEDPARAMS constants
  - Player source (sidfinity_player.s) is already in xa65 format
"""

import struct
import subprocess
import sys
import os
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Tools live in the main repo root (shared across worktrees)
REPO_ROOT = os.environ.get('SIDFINITY_ROOT', os.path.join(SCRIPT_DIR, '..')).strip()
XA65 = os.path.join(REPO_ROOT, 'tools', 'xa65', 'xa', 'xa')
PLAYER_S = os.path.join(SCRIPT_DIR, 'player', 'sidfinity_player.s')

# PAL frequency tables (default)
FREQ_LO_PAL = bytes([
    0x17,0x27,0x39,0x4B,0x5F,0x74,0x8A,0xA1,0xBA,0xD4,0xF0,0x0E,
    0x2D,0x4E,0x71,0x96,0xBE,0xE8,0x14,0x43,0x74,0xA9,0xE1,0x1C,
    0x5A,0x9C,0xE2,0x2D,0x7C,0xCF,0x28,0x85,0xE8,0x52,0xC1,0x37,
    0xB4,0x39,0xC5,0x5A,0xF7,0x9E,0x4F,0x0A,0xD1,0xA3,0x82,0x6E,
    0x68,0x71,0x8A,0xB3,0xEE,0x3C,0x9E,0x15,0xA2,0x46,0x04,0xDC,
    0xD0,0xE2,0x14,0x67,0xDD,0x79,0x3C,0x29,0x44,0x8D,0x08,0xB8,
    0xA1,0xC5,0x28,0xCD,0xBA,0xF1,0x78,0x53,0x87,0x1A,0x10,0x71,
    0x42,0x89,0x4F,0x9B,0x74,0xE2,0xF0,0xA6,0x0E,0x33,0x20,0xFF])
FREQ_HI_PAL = bytes([
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
    0x04,0x04,0x04,0x05,0x05,0x05,0x06,0x06,0x06,0x07,0x07,0x08,
    0x08,0x09,0x09,0x0A,0x0A,0x0B,0x0C,0x0D,0x0D,0x0E,0x0F,0x10,
    0x11,0x12,0x13,0x14,0x15,0x17,0x18,0x1A,0x1B,0x1D,0x1F,0x20,
    0x22,0x24,0x27,0x29,0x2B,0x2E,0x31,0x34,0x37,0x3A,0x3E,0x41,
    0x45,0x49,0x4E,0x52,0x57,0x5C,0x62,0x68,0x6E,0x75,0x7C,0x83,
    0x8B,0x93,0x9C,0xA5,0xAF,0xB9,0xC4,0xD0,0xDD,0xEA,0xF8,0xFF])

MAX_BYTES_PER_ROW = 16


def _strip_dummy_labels(source):
    """Remove the #ifndef mt_songtbllo ... #endif block from the player source.

    The player defines all data labels as mt_dummydata for standalone testing.
    When packing, we remove this block so our data section can define the
    real label addresses.
    """
    lines = source.split('\n')
    out = []
    skip = False
    for line in lines:
        stripped = line.strip()
        if stripped == '#ifndef mt_songtbllo':
            skip = True
            continue
        if skip and stripped == '#endif':
            skip = False
            continue
        if not skip:
            # Also strip the mt_dummy label (only used by dummy block)
            if stripped.startswith('mt_dummy'):
                continue
            out.append(line)
    return '\n'.join(out)

# All 9 instrument column names in order
ALL_COLUMNS = [
    'ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr',
    'vib_param', 'vib_delay', 'gate_timer', 'first_wave',
]

# Corresponding assembler labels
COLUMN_LABELS = {
    'ad': 'mt_insad',
    'sr': 'mt_inssr',
    'wave_ptr': 'mt_inswaveptr',
    'pulse_ptr': 'mt_inspulseptr',
    'filter_ptr': 'mt_insfiltptr',
    'vib_param': 'mt_insvibparam',
    'vib_delay': 'mt_insvibdelay',
    'gate_timer': 'mt_insgatetimer',
    'first_wave': 'mt_insfirstwave',
}


def insertdefine(buf, name, value):
    buf.append(f'{name:<16s} = {value}\n')


def insertlabel(buf, name):
    buf.append(f'{name}:\n')


def insertbytes(buf, data):
    row = 0
    for i, b in enumerate(data):
        if row == 0:
            buf.append(f'                .byte ${b:02x}')
            row = 1
        else:
            buf.append(f',${b:02x}')
            row += 1
            if row >= MAX_BYTES_PER_ROW:
                buf.append('\n')
                row = 0
    if row > 0:
        buf.append('\n')


def insertbyte(buf, b):
    buf.append(f'                .byte ${b:02x}\n')


def insertaddrlo(buf, name):
    buf.append(f'                .byte {name} & 255\n')


def insertaddrhi(buf, name):
    buf.append(f'                .byte {name} / 256\n')


def pack_sidfinity(
    base_addr=0x1000,
    zp_addr=0xFC,
    songs=1,
    first_note=0,
    last_note=95,
    default_tempo=5,
    # Instrument columns
    num_instruments=1,
    num_normal=None,
    num_nohr=0,
    num_legato=0,
    instruments=None,  # dict of column_name -> bytes
    # Tables
    wave_left=None,
    wave_right=None,
    pulse_left=None,
    pulse_right=None,
    filter_left=None,
    filter_right=None,
    speed_left=None,
    speed_right=None,
    # Song data
    orderlists=None,
    patterns=None,
    # Freq tables
    freq_lo=None,
    freq_hi=None,
    # PSID header
    title='',
    author='',
):
    """Pack GT2 data using xa65 + SIDfinity player. Returns (sid_bytes, player_size)."""
    ni = num_instruments
    if num_normal is None:
        num_normal = ni

    if freq_lo is None:
        freq_lo = FREQ_LO_PAL
    if freq_hi is None:
        freq_hi = FREQ_HI_PAL
    if instruments is None:
        instruments = {}
    if wave_left is None:
        wave_left = bytes([0])
    if wave_right is None:
        wave_right = bytes([0])
    if speed_left is None:
        speed_left = bytes([0])
    if speed_right is None:
        speed_right = bytes([0])
    if orderlists is None:
        orderlists = [bytes([0x00, 0x80, 0xFF, 0x00])] * (songs * 3)
    if patterns is None:
        patterns = [bytes([0xBD, 0x00])]

    num_patt = len(patterns)

    # --- Build xa65 command-line -D flags ---
    # The player uses #ifndef guards for these symbols, so we pass them
    # via -D to override the defaults without causing label-redefinition errors.
    ad_param = 0x0F
    sr_param = 0x00
    dflags = [
        f'-Dbase=${base_addr:x}',
        f'-DSIDBASE=$d400',
        f'-DFIRSTNOTE=$0',  # Always 0: full 96-note freq table emitted
        f'-DDEFAULTTEMPO=${default_tempo:x}',
        f'-DADPARAM=${ad_param:x}',
        f'-DSRPARAM=${sr_param:x}',
        f'-DFIRSTNOHRINSTR=${num_normal + 1:x}',
        f'-DFIRSTLEGATOINSTR=${num_normal + num_nohr + 1:x}',
    ]

    # --- Build assembly source ---
    buf = []

    # Insert player source (already in xa65 format).
    # Strip the dummy data label block (#ifndef mt_songtbllo ... #endif)
    # because our data section will define these labels at real addresses.
    with open(PLAYER_S) as f:
        player_src = f.read()
    player_src = _strip_dummy_labels(player_src)
    buf.append(player_src)
    buf.append('\n')

    # --- Insert data (greloc.c order) ---

    # Frequency tables — always emit the full 96-note PAL table (notes 0-95).
    # Many GT2 files have FIRSTNOTE > 0 but wave table lookups can reference
    # notes below FIRSTNOTE, causing out-of-range reads into player code.
    # The full table is only 192 bytes — negligible cost for correctness.
    insertlabel(buf, 'mt_freqtbllo')
    insertbytes(buf, FREQ_LO_PAL)
    insertlabel(buf, 'mt_freqtblhi')
    insertbytes(buf, FREQ_HI_PAL)

    # Song table
    insertlabel(buf, 'mt_songtbllo')
    for c in range(songs * 3):
        insertaddrlo(buf, f'mt_song{c}')
    insertlabel(buf, 'mt_songtblhi')
    for c in range(songs * 3):
        insertaddrhi(buf, f'mt_song{c}')

    # Pattern table
    insertlabel(buf, 'mt_patttbllo')
    for c in range(num_patt):
        insertaddrlo(buf, f'mt_patt{c}')
    insertlabel(buf, 'mt_patttblhi')
    for c in range(num_patt):
        insertaddrhi(buf, f'mt_patt{c}')

    # Instrument columns — ALL 9, always present, pad missing with zeros
    for col_name in ALL_COLUMNS:
        label = COLUMN_LABELS[col_name]
        insertlabel(buf, label)
        col_data = instruments.get(col_name, bytes(ni))
        # Ensure correct length
        if len(col_data) < ni:
            col_data = col_data + bytes(ni - len(col_data))
        insertbytes(buf, col_data[:ni])

    # Tables: wave, pulse, filter, speed (always all present)

    # Wave table — SIDfinity player always has wave delay support,
    # so wave left bytes $10-$DF must have the +$10 bias applied.
    # If the original had NOWAVEDELAY=1, the packed data has no bias.
    # Detect and apply: if no entry in $10-$1F range (delay region after bias),
    # then the data lacks the bias.
    wl = bytearray(wave_left)
    needs_bias = not any(0x10 <= b <= 0x1F for b in wl if b != 0xFF)
    if needs_bias:
        for i in range(len(wl)):
            if 0x10 <= wl[i] <= 0xDF:  # waveform range (not delay, cmd, or jump)
                wl[i] += 0x10
    insertlabel(buf, 'mt_wavetbl')
    insertbytes(buf, bytes(wl))
    insertlabel(buf, 'mt_notetbl')
    insertbytes(buf, wave_right)

    # Pulse table (always present)
    insertlabel(buf, 'mt_pulsetimetbl')
    if pulse_left:
        insertbytes(buf, pulse_left)
    insertlabel(buf, 'mt_pulsespdtbl')
    if pulse_right:
        insertbytes(buf, pulse_right)

    # Filter table (always present)
    insertlabel(buf, 'mt_filttimetbl')
    if filter_left:
        insertbytes(buf, filter_left)
    insertlabel(buf, 'mt_filtspdtbl')
    if filter_right:
        insertbytes(buf, filter_right)

    # Speed table (always present, with $00 prefix when data exists)
    has_speed_data = speed_left and len(speed_left) > 0 and speed_left != bytes([0])
    if has_speed_data:
        insertbyte(buf, 0)
    insertlabel(buf, 'mt_speedlefttbl')
    if has_speed_data:
        insertbytes(buf, speed_left)
    if has_speed_data:
        insertbyte(buf, 0)
    insertlabel(buf, 'mt_speedrighttbl')
    if has_speed_data:
        insertbytes(buf, speed_right)

    # Safety padding
    buf.append('                .byte $00,$00,$00,$00\n')

    # Orderlists
    for c in range(songs):
        for d in range(3):
            insertlabel(buf, f'mt_song{c * 3 + d}')
            insertbytes(buf, orderlists[c * 3 + d])

    # Patterns
    for c in range(num_patt):
        insertlabel(buf, f'mt_patt{c}')
        insertbytes(buf, patterns[c])

    # --- Assemble with xa65 ---
    asm_source = ''.join(buf)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.s', delete=False) as f:
        f.write(asm_source)
        asm_path = f.name
    bin_path = asm_path + '.bin'

    try:
        result = subprocess.run(
            [XA65, '-XMASM'] + dflags + ['-o', bin_path, asm_path],
            capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            # Save the asm for debugging
            debug_path = '/tmp/sidfinity_debug.s'
            with open(debug_path, 'w') as f:
                f.write(asm_source)
            raise RuntimeError(
                f"xa65 failed (source saved to {debug_path}):\n"
                f"{result.stderr[:1000]}")

        with open(bin_path, 'rb') as f:
            binary = f.read()
    finally:
        for p in [asm_path, bin_path]:
            if os.path.exists(p):
                os.unlink(p)

    total_size = len(binary)

    # --- Build PSID v2 header ---
    header = bytearray(124)
    header[0:4] = b'PSID'
    struct.pack_into('>H', header, 4, 2)       # version
    struct.pack_into('>H', header, 6, 124)     # data offset
    struct.pack_into('>H', header, 8, 0)       # load addr (in data)
    struct.pack_into('>H', header, 10, base_addr)  # init
    struct.pack_into('>H', header, 12, base_addr + 3)  # play
    struct.pack_into('>H', header, 14, songs)   # songs
    struct.pack_into('>H', header, 16, 1)       # start song

    # Title/author in PSID header
    t = title.encode('latin-1', errors='replace')[:31]
    header[22:22 + len(t)] = t
    a = author.encode('latin-1', errors='replace')[:31]
    header[54:54 + len(a)] = a
    struct.pack_into('>H', header, 0x76, 0x0014)  # PAL, 6581

    # SID file = header + load address + binary
    sid = bytearray()
    sid.extend(header)
    sid.extend(struct.pack('<H', base_addr))
    sid.extend(binary)

    return bytes(sid), total_size


def pack_from_decompiled(d, output_path):
    """Pack a decompiled GT2 result into a SIDfinity SID.

    Takes the dict returned by gt2_decompile.decompile_gt2() and
    produces a SID using the SIDfinity player with all features enabled.

    Args:
        d: dict from decompile_gt2()
        output_path: where to write the SID

    Returns:
        dict with status info
    """
    columns = d['columns']
    ni = d['ni']

    # Build instruments dict with all 9 columns, padding missing ones
    instruments = {}
    for col_name in ALL_COLUMNS:
        if col_name in columns:
            instruments[col_name] = bytes(columns[col_name])
        else:
            # Pad with appropriate defaults
            if col_name == 'gate_timer':
                instruments[col_name] = bytes([0x02] * ni)
            elif col_name == 'first_wave':
                instruments[col_name] = bytes([0x09] * ni)
            else:
                instruments[col_name] = bytes(ni)

    # Instrument classification from gate_timer
    gt_col = list(instruments['gate_timer'])
    num_normal = num_nohr = num_legato = 0
    for gt in gt_col:
        if gt & 0x40:
            num_legato += 1
        elif gt & 0x80:
            num_nohr += 1
        else:
            num_normal += 1

    # Read original PSID header for title/author (if available)
    title = d.get('title', '')
    author = d.get('author', '')

    sid_bytes, player_size = pack_sidfinity(
        base_addr=d['la'],
        songs=1,
        first_note=0,   # Always 0: full 96-note freq table
        last_note=95,
        default_tempo=5,
        num_instruments=ni,
        num_normal=num_normal,
        num_nohr=num_nohr,
        num_legato=num_legato,
        instruments=instruments,
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
        # freq_lo/freq_hi: use default full PAL table (not decompiled slice)
        title=title,
        author=author,
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(sid_bytes)

    return {
        'status': 'ok',
        'output': output_path,
        'ni': ni,
        'num_patt': d['num_patt'],
        'wave_size': d['wave_size'],
        'player_size': player_size,
        'sid_size': len(sid_bytes),
    }


def test_sidfinity_pack(sid_path, duration=10):
    """Test: decompile a GT2 SID, pack with SIDfinity player, compare registers.

    Returns comparison results dict, or None on failure.
    """
    sys.path.insert(0, SCRIPT_DIR)
    from gt2_decompile import decompile_gt2
    from gt2_compare import compare_sids_tolerant, print_results

    # Step 1: Decompile
    d = decompile_gt2(sid_path)
    if d is None:
        print(f"Failed to decompile {sid_path}")
        return None

    # Read title/author from original SID
    with open(sid_path, 'rb') as f:
        sid_data = f.read()
    d['title'] = sid_data[0x16:0x36].split(b'\x00')[0].decode('latin-1', errors='replace')
    d['author'] = sid_data[0x36:0x56].split(b'\x00')[0].decode('latin-1', errors='replace')

    # Step 2: Pack with SIDfinity player
    output_path = '/tmp/sidfinity_packed.sid'
    try:
        result = pack_from_decompiled(d, output_path)
    except Exception as e:
        print(f"Pack failed: {e}")
        return None

    name = os.path.basename(sid_path)
    print(f"{name}: ni={result['ni']} patt={result['num_patt']} "
          f"wave={result['wave_size']} size={result['sid_size']}")
    print(f"  Written to: {output_path}")

    # Step 3: Compare register output
    comp = compare_sids_tolerant(sid_path, output_path, duration)
    if comp is None:
        print("  Comparison failed (siddump error)")
        return None

    print()
    print_results(comp, name)
    return comp


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: sidfinity_pack.py <file.sid> [--duration N] [--compare]")
        print("       sidfinity_pack.py <file.sid> -o <output.sid>")
        sys.exit(1)

    sid_path = sys.argv[1]
    compare = '--compare' in sys.argv
    duration = 10
    for i, a in enumerate(sys.argv):
        if a == '--duration' and i + 1 < len(sys.argv):
            duration = int(sys.argv[i + 1])

    output_path = None
    for i, a in enumerate(sys.argv):
        if a == '-o' and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            break

    if compare or output_path is None:
        # Test mode: decompile + pack + compare
        result = test_sidfinity_pack(sid_path, duration)
        if result is None:
            sys.exit(1)
    else:
        # Pack mode: just produce the SID
        sys.path.insert(0, SCRIPT_DIR)
        from gt2_decompile import decompile_gt2

        d = decompile_gt2(sid_path)
        if d is None:
            print(f"Failed to decompile {sid_path}")
            sys.exit(1)

        with open(sid_path, 'rb') as f:
            sid_data = f.read()
        d['title'] = sid_data[0x16:0x36].split(b'\x00')[0].decode('latin-1', errors='replace')
        d['author'] = sid_data[0x36:0x56].split(b'\x00')[0].decode('latin-1', errors='replace')

        try:
            result = pack_from_decompiled(d, output_path)
        except Exception as e:
            print(f"Pack failed: {e}")
            sys.exit(1)

        name = os.path.basename(sid_path)
        print(f"{name}: ni={result['ni']} patt={result['num_patt']} "
              f"wave={result['wave_size']} size={result['sid_size']}")
        print(f"  Written to: {output_path}")
