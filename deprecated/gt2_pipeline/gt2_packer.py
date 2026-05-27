"""
gt2_packer.py — Pack GT2 music data using the original GT2 assembler + player.s.

Mirrors greloc.c exactly: generates defines + player.s + data labels/.BYTE,
then assembles with gt2asm to produce identical player code.
"""

import struct
import subprocess
import sys
import os
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GT2ASM = os.path.join(SCRIPT_DIR, '..', 'tools', 'gt2asm')
PLAYER_S = os.path.join(SCRIPT_DIR, 'GoatTracker_2.77', 'src', 'player.s')

# Player version mapping: behavior group → GT2 version directory
PLAYER_GROUP_VERSION = {
    'A': '2.65',   # v2.65-2.67: AD-before-SR, new-note writes all regs
    'B': '2.68',   # v2.68-2.72: SR-before-AD, new-note writes wave-only
    'C': '2.73',   # v2.73-2.74: B + ghost reg support
    'D': '2.77',   # v2.76-2.77: C + vibrato param fix
}


def get_player_source(group=None):
    """Get the player.s path for a given behavior group."""
    if group and group in PLAYER_GROUP_VERSION:
        ver = PLAYER_GROUP_VERSION[group]
        path = os.path.join(SCRIPT_DIR, f'GoatTracker_{ver}', 'src', 'player.s')
        if os.path.exists(path):
            return path
    return PLAYER_S  # fallback to latest

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


def insertdefine(buf, name, value):
    buf.append(f'{name:<16s} = {value}\n')


def insertlabel(buf, name):
    buf.append(f'{name}:\n')


def insertbytes(buf, data):
    row = 0
    for i, b in enumerate(data):
        if row == 0:
            buf.append(f'                .BYTE (${b:02x}')
            row = 1
        else:
            buf.append(f',${b:02x}')
            row += 1
            if row >= MAX_BYTES_PER_ROW:
                buf.append(')\n')
                row = 0
    if row > 0:
        buf.append(')\n')


def insertbyte(buf, b):
    buf.append(f'                .BYTE (${b:02x})\n')


def insertaddrlo(buf, name):
    buf.append(f'                .BYTE ({name} % 256)\n')


def insertaddrhi(buf, name):
    buf.append(f'                .BYTE ({name} / 256)\n')


def pack_gt2(
    flags,
    base_addr=0x1000,
    zp_addr=0xFC,
    songs=1,
    first_note=0,
    last_note=95,
    default_tempo=5,
    # Instrument columns (already reordered: normal, nohr, legato)
    num_instruments=1,
    num_normal=None,
    num_nohr=0,
    num_legato=0,
    ad_param=0x0F,
    sr_param=0x00,
    first_wave_param=0x09,
    gate_timer_param=0x02,
    instruments_ad=None,
    instruments_sr=None,
    instruments_waveptr=None,
    instruments_pulseptr=None,
    instruments_filtptr=None,
    instruments_vibparam=None,
    instruments_vibdelay=None,
    instruments_gatetimer=None,
    instruments_firstwave=None,
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
    noauthorinfo=1,
    player_group='',
):
    """Pack GT2 data using gt2asm + player.s. Returns (sid_bytes, player_size)."""
    ni = num_instruments
    if num_normal is None:
        num_normal = ni

    if freq_lo is None:
        freq_lo = FREQ_LO_PAL
    if freq_hi is None:
        freq_hi = FREQ_HI_PAL
    if instruments_ad is None:
        instruments_ad = bytes([0x09] * ni)
    if instruments_sr is None:
        instruments_sr = bytes([0x00] * ni)
    if instruments_waveptr is None:
        instruments_waveptr = bytes([0x00] * ni)
    if instruments_gatetimer is None:
        instruments_gatetimer = bytes([0x02] * ni)
    if instruments_firstwave is None:
        instruments_firstwave = bytes([0x41] * ni)
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

    F = flags
    num_patt = len(patterns)

    # --- Build assembly source ---
    buf = []

    # Defines
    insertdefine(buf, 'base', base_addr)
    insertdefine(buf, 'zpbase', zp_addr)
    insertdefine(buf, 'SIDBASE', 0xD400)

    insertdefine(buf, 'SOUNDSUPPORT', 0)
    insertdefine(buf, 'VOLSUPPORT', 0)
    insertdefine(buf, 'BUFFEREDWRITES', 0)
    insertdefine(buf, 'GHOSTREGS', 0)
    insertdefine(buf, 'ZPGHOSTREGS', 0)
    insertdefine(buf, 'FIXEDPARAMS', F.get('FIXEDPARAMS', 1))
    insertdefine(buf, 'SIMPLEPULSE', F.get('SIMPLEPULSE', 1))
    insertdefine(buf, 'PULSEOPTIMIZATION', 0)
    insertdefine(buf, 'REALTIMEOPTIMIZATION', 0)
    insertdefine(buf, 'NOAUTHORINFO', noauthorinfo)

    for flag in ['NOEFFECTS','NOGATE','NOFILTER','NOFILTERMOD','NOPULSE','NOPULSEMOD',
                 'NOWAVEDELAY','NOWAVECMD','NOREPEAT','NOTRANS','NOPORTAMENTO','NOTONEPORTA',
                 'NOVIB','NOINSTRVIB','NOSETAD','NOSETSR','NOSETWAVE','NOSETWAVEPTR',
                 'NOSETPULSEPTR','NOSETFILTPTR','NOSETFILTCTRL','NOSETFILTCUTOFF',
                 'NOSETMASTERVOL','NOFUNKTEMPO','NOGLOBALTEMPO','NOCHANNELTEMPO',
                 'NOFIRSTWAVECMD','NOCALCULATEDSPEED','NONORMALSPEED','NOZEROSPEED']:
        insertdefine(buf, flag, F.get(flag, 1))

    insertdefine(buf, 'NUMCHANNELS', 3)
    insertdefine(buf, 'NUMSONGS', songs)
    insertdefine(buf, 'FIRSTNOTE', first_note)
    insertdefine(buf, 'FIRSTNOHRINSTR', num_normal + 1)
    insertdefine(buf, 'FIRSTLEGATOINSTR', num_normal + num_nohr + 1)
    insertdefine(buf, 'NUMHRINSTR', num_normal)
    insertdefine(buf, 'NUMNOHRINSTR', num_nohr)
    insertdefine(buf, 'NUMLEGATOINSTR', num_legato)
    insertdefine(buf, 'ADPARAM', ad_param)
    insertdefine(buf, 'SRPARAM', sr_param)
    insertdefine(buf, 'DEFAULTTEMPO', default_tempo)

    if F.get('FIXEDPARAMS', 1):
        insertdefine(buf, 'FIRSTWAVEPARAM', first_wave_param)
        insertdefine(buf, 'GATETIMERPARAM', gate_timer_param)

    # Insert player.s source (version selected by player_group)
    player_src = get_player_source(player_group)
    with open(player_src) as f:
        buf.append(f.read())
    buf.append('\n')

    # --- Insert data ---
    # Frequency tables. If custom tables are provided (from decompiler),
    # they're already sliced to the correct range — emit as-is.
    # If using default PAL tables, slice by first_note/last_note.
    insertlabel(buf, 'mt_freqtbllo')
    if len(freq_lo) <= last_note - first_note + 1:
        insertbytes(buf, freq_lo)  # already sliced
    else:
        insertbytes(buf, freq_lo[first_note:last_note + 1])
    insertlabel(buf, 'mt_freqtblhi')
    if len(freq_hi) <= last_note - first_note + 1:
        insertbytes(buf, freq_hi)  # already sliced
    else:
        insertbytes(buf, freq_hi[first_note:last_note + 1])

    # Song table (address lo/hi for each orderlist)
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

    # Instrument columns
    insertlabel(buf, 'mt_insad')
    insertbytes(buf, instruments_ad[:ni])
    insertlabel(buf, 'mt_inssr')
    insertbytes(buf, instruments_sr[:ni])
    insertlabel(buf, 'mt_inswaveptr')
    insertbytes(buf, instruments_waveptr[:ni])

    if not F.get('NOPULSE', 1):
        insertlabel(buf, 'mt_inspulseptr')
        insertbytes(buf, (instruments_pulseptr or bytes(ni))[:ni])

    if not F.get('NOFILTER', 1):
        insertlabel(buf, 'mt_insfiltptr')
        insertbytes(buf, (instruments_filtptr or bytes(ni))[:ni])

    if not F.get('NOINSTRVIB', 1):
        insertlabel(buf, 'mt_insvibparam')
        insertbytes(buf, (instruments_vibparam or bytes(ni))[:ni])
        insertlabel(buf, 'mt_insvibdelay')
        insertbytes(buf, (instruments_vibdelay or bytes(ni))[:ni])

    if not F.get('FIXEDPARAMS', 1):
        insertlabel(buf, 'mt_insgatetimer')
        insertbytes(buf, instruments_gatetimer[:ni])
        insertlabel(buf, 'mt_insfirstwave')
        insertbytes(buf, instruments_firstwave[:ni])

    # Tables: wave, pulse, filter, speed
    # Wave table
    insertlabel(buf, 'mt_wavetbl')
    insertbytes(buf, wave_left)
    insertlabel(buf, 'mt_notetbl')
    insertbytes(buf, wave_right)

    # Pulse table (only if pulse used)
    if not F.get('NOPULSE', 1):
        insertlabel(buf, 'mt_pulsetimetbl')
        if pulse_left:
            insertbytes(buf, pulse_left)
        insertlabel(buf, 'mt_pulsespdtbl')
        if pulse_right:
            insertbytes(buf, pulse_right)

    # Filter table (only if filter used)
    if not F.get('NOFILTER', 1):
        insertlabel(buf, 'mt_filttimetbl')
        if filter_left:
            insertbytes(buf, filter_left)
        insertlabel(buf, 'mt_filtspdtbl')
        if filter_right:
            insertbytes(buf, filter_right)

    # Speed table (with extra zero prefix if speed features used)
    has_speed = (not F.get('NOVIB', 1) or not F.get('NOFUNKTEMPO', 1) or
                 not F.get('NOPORTAMENTO', 1) or not F.get('NOTONEPORTA', 1))
    has_speed_data = speed_left and len(speed_left) > 0 and speed_left != bytes([0])
    if has_speed and has_speed_data:
        insertbyte(buf, 0)
    insertlabel(buf, 'mt_speedlefttbl')
    if has_speed_data:
        insertbytes(buf, speed_left)
    if has_speed and has_speed_data:
        insertbyte(buf, 0)
    insertlabel(buf, 'mt_speedrighttbl')
    if has_speed_data:
        insertbytes(buf, speed_right)

    # Safety padding: ensure empty table labels don't read into orderlist data.
    # When pulse/filter/speed tables have 0 entries, their labels all point here.
    # The player reads from label-1+Y — with Y=1 it reads byte 0 of this padding.
    # $00 bytes are benign: pulse treats $00 as "set cutoff", filter as "set cutoff",
    # and both just set values to 0 (no audible effect).
    buf.append('                .BYTE ($00,$00,$00,$00)\n')

    # Orderlists
    for c in range(songs):
        for d in range(3):
            insertlabel(buf, f'mt_song{c * 3 + d}')
            insertbytes(buf, orderlists[c * 3 + d])

    # Patterns
    for c in range(num_patt):
        insertlabel(buf, f'mt_patt{c}')
        insertbytes(buf, patterns[c])

    # --- Assemble ---
    asm_source = ''.join(buf)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.s', delete=False) as f:
        f.write(asm_source)
        asm_path = f.name
    bin_path = asm_path + '.bin'

    try:
        result = subprocess.run([GT2ASM, asm_path, bin_path],
                                capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"gt2asm failed:\n{result.stderr[:500]}\n"
                               f"First 20 lines:\n" +
                               '\n'.join(asm_source.split('\n')[:20]))

        with open(bin_path, 'rb') as f:
            binary = f.read()
    finally:
        for p in [asm_path, bin_path]:
            if os.path.exists(p):
                os.unlink(p)

    # binary starts at base_addr. The player code ends where freq table starts.
    # We need total size for the SID file.
    total_size = len(binary)

    # --- Build PSID header ---
    header = bytearray(124)
    header[0:4] = b'PSID'
    struct.pack_into('>H', header, 4, 2)       # version
    struct.pack_into('>H', header, 6, 124)     # data offset
    struct.pack_into('>H', header, 8, 0)       # load addr (in data)
    struct.pack_into('>H', header, 10, base_addr)  # init
    struct.pack_into('>H', header, 12, base_addr + 3)  # play
    struct.pack_into('>H', header, 14, songs)   # songs
    struct.pack_into('>H', header, 16, 1)       # start song

    # Title/author
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
