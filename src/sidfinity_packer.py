"""
sidfinity_packer.py - Pack music data with the SIDfinity player into a SID file.

Replaces greloc.c: takes structured music data (instruments, patterns,
orderlists, tables), generates assembly defines, assembles the player
with 64tass, and outputs a complete PSID v2 file.

Data layout in the output binary (after player code):
  1. Frequency tables (lo[N], hi[N])
  2. Song table (lo[songs*3], hi[songs*3])
  3. Pattern table (lo[num_patt], hi[num_patt])
  4. Instrument columns (AD, SR, waveptr, [pulseptr, filtptr, vibparam, vibdelay, gatetimer, firstwave])
  5. Wave table (left[N], right[N])
  6. Pulse table (left[N], right[N]) [optional]
  7. Filter table (left[N], right[N]) [optional]
  8. Speed table (left[N], right[N])
  9. Song orderlists
  10. Packed pattern data
"""

import struct
import subprocess
import sys
import os
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASS = os.path.join(SCRIPT_DIR, '..', 'tools', '64tass')
PLAYER_SRC = os.path.join(SCRIPT_DIR, 'player', 'sidfinity_gt2.asm')
DEFINES_SRC = os.path.join(SCRIPT_DIR, 'player', 'sidfinity_defines.asm')

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


def pack_sid(
    title='SIDfinity',
    author='SIDfinity',
    base_addr=0x1000,
    songs=1,
    num_instruments=1,
    instruments_ad=None,
    instruments_sr=None,
    instruments_waveptr=None,
    instruments_pulseptr=None,
    instruments_filtptr=None,
    instruments_vibparam=None,
    instruments_vibdelay=None,
    instruments_gatetimer=None,
    instruments_firstwave=None,
    wave_left=None,
    wave_right=None,
    pulse_left=None,
    pulse_right=None,
    filter_left=None,
    filter_right=None,
    speed_left=None,
    speed_right=None,
    orderlists=None,
    patterns=None,
    freq_lo=None,
    freq_hi=None,
    first_note=0,
    last_note=95,
):
    """Pack music data with the SIDfinity player into a SID file.

    Returns bytes of the complete SID file.
    """
    if freq_lo is None:
        freq_lo = FREQ_LO_PAL
    if freq_hi is None:
        freq_hi = FREQ_HI_PAL
    if instruments_ad is None:
        instruments_ad = bytes([0x09] * num_instruments)
    if instruments_sr is None:
        instruments_sr = bytes([0x00] * num_instruments)
    if instruments_waveptr is None:
        instruments_waveptr = bytes([0x00] * num_instruments)
    if instruments_gatetimer is None:
        instruments_gatetimer = bytes([0x02] * num_instruments)
    if instruments_firstwave is None:
        instruments_firstwave = bytes([0x41] * num_instruments)
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

    ni = num_instruments
    num_notes = last_note - first_note + 1
    num_patt = len(patterns)
    song_entries = songs * 3

    # Build data blob, tracking addresses
    data = bytearray()

    def addr():
        return base_addr + player_size + len(data)

    # We don't know player_size yet - assemble first to find out
    # Two-pass: first assemble with dummy addresses, then with real ones

    # Data starts at a fixed offset from base to avoid two-pass assembly
    # Player is ~1200 bytes, so data at base+$0600 gives plenty of room
    DATA_OFFSET = 0x0600
    player_size = DATA_OFFSET  # data addresses computed from this

    # --- Build data section ---
    data = bytearray()

    # 1. Frequency tables
    freq_lo_addr = base_addr + player_size + len(data)
    data.extend(freq_lo[first_note:last_note + 1])
    freq_hi_addr = base_addr + player_size + len(data)
    data.extend(freq_hi[first_note:last_note + 1])

    # 2. Song table
    song_lo_addr = base_addr + player_size + len(data)
    song_lo_data = bytearray(song_entries)  # fill later
    data.extend(song_lo_data)
    song_hi_addr = base_addr + player_size + len(data)
    song_hi_data = bytearray(song_entries)
    data.extend(song_hi_data)

    # 3. Pattern table
    patt_lo_addr = base_addr + player_size + len(data)
    patt_lo_data = bytearray(num_patt)
    data.extend(patt_lo_data)
    patt_hi_addr = base_addr + player_size + len(data)
    patt_hi_data = bytearray(num_patt)
    data.extend(patt_hi_data)

    # 4. Instrument columns
    insad_addr = base_addr + player_size + len(data)
    data.extend(instruments_ad[:ni])
    inssr_addr = base_addr + player_size + len(data)
    data.extend(instruments_sr[:ni])
    inswaveptr_addr = base_addr + player_size + len(data)
    data.extend(instruments_waveptr[:ni])

    inspulseptr_addr = base_addr + player_size + len(data)
    if instruments_pulseptr:
        data.extend(instruments_pulseptr[:ni])
    else:
        data.extend(bytes(ni))

    insfiltptr_addr = base_addr + player_size + len(data)
    if instruments_filtptr:
        data.extend(instruments_filtptr[:ni])
    else:
        data.extend(bytes(ni))

    insvibparam_addr = base_addr + player_size + len(data)
    if instruments_vibparam:
        data.extend(instruments_vibparam[:ni])
    else:
        data.extend(bytes(ni))

    insvibdelay_addr = base_addr + player_size + len(data)
    if instruments_vibdelay:
        data.extend(instruments_vibdelay[:ni])
    else:
        data.extend(bytes(ni))

    insgatetimer_addr = base_addr + player_size + len(data)
    data.extend(instruments_gatetimer[:ni])

    insfirstwave_addr = base_addr + player_size + len(data)
    data.extend(instruments_firstwave[:ni])

    # 5-8. Tables
    wavetbl_addr = base_addr + player_size + len(data)
    data.extend(wave_left)
    notetbl_addr = base_addr + player_size + len(data)
    data.extend(wave_right)

    pulsetimetbl_addr = base_addr + player_size + len(data)
    if pulse_left:
        data.extend(pulse_left)
    else:
        data.extend(bytes(1))
    pulsespdtbl_addr = base_addr + player_size + len(data)
    if pulse_right:
        data.extend(pulse_right)
    else:
        data.extend(bytes(1))

    filttimetbl_addr = base_addr + player_size + len(data)
    if filter_left:
        data.extend(filter_left)
    else:
        data.extend(bytes(1))
    filtspdtbl_addr = base_addr + player_size + len(data)
    if filter_right:
        data.extend(filter_right)
    else:
        data.extend(bytes(1))

    speedlefttbl_addr = base_addr + player_size + len(data)
    data.extend(bytes(1))  # extra zero at start (GT2 convention)
    data.extend(speed_left)
    speedrighttbl_addr = base_addr + player_size + len(data)
    data.extend(bytes(1))
    data.extend(speed_right)

    # 9. Orderlists
    ol_offsets = []
    for ol in orderlists:
        ol_offsets.append(base_addr + player_size + len(data))
        data.extend(ol)

    # 10. Patterns
    patt_offsets = []
    for patt in patterns:
        patt_offsets.append(base_addr + player_size + len(data))
        data.extend(patt)

    # Fill in song table (orderlist addresses)
    song_lo_start = song_lo_addr - base_addr - player_size
    song_hi_start = song_hi_addr - base_addr - player_size
    for i, ol_addr in enumerate(ol_offsets):
        data[song_lo_start + i] = ol_addr & 0xFF
        data[song_hi_start + i] = (ol_addr >> 8) & 0xFF

    # Fill in pattern table
    patt_lo_start = patt_lo_addr - base_addr - player_size
    patt_hi_start = patt_hi_addr - base_addr - player_size
    for i, p_addr in enumerate(patt_offsets):
        data[patt_lo_start + i] = p_addr & 0xFF
        data[patt_hi_start + i] = (p_addr >> 8) & 0xFF

    # --- Generate defines ---
    defines = f"""; SIDfinity auto-generated defines
base = ${base_addr:04x}
zpbase = $fc
SIDBASE = $d400
SOUNDSUPPORT = 0
VOLSUPPORT = 0
BUFFEREDWRITES = 0
ZPGHOSTREGS = 0
NOAUTHORINFO = 1
NOEFFECTS = 0
NOGATE = 0
NOFILTER = 0
NOFILTERMOD = 0
NOPULSE = 0
NOPULSEMOD = 0
NOWAVEDELAY = 0
NOWAVECMD = 0
NOREPEAT = 0
NOTRANS = 0
NOPORTAMENTO = 0
NOTONEPORTA = 0
NOVIB = 0
NOINSTRVIB = 0
NOSETAD = 0
NOSETSR = 0
NOSETWAVE = 0
NOSETWAVEPTR = 0
NOSETPULSEPTR = 0
NOSETFILTPTR = 0
NOSETFILTCTRL = 0
NOSETFILTCUTOFF = 0
NOSETMASTERVOL = 0
NOFUNKTEMPO = 0
NOGLOBALTEMPO = 0
NOCHANNELTEMPO = 0
NOZEROSPEED = 0
NONORMALSPEED = 0
NOCALCULATEDSPEED = 0
NOFIRSTWAVECMD = 0
PULSEOPTIMIZATION = 0
REALTIMEOPTIMIZATION = 0
DEFAULTTEMPO = 6
NUMCHANNELS = 3
NUMSONGS = {songs}
FIRSTNOTE = {first_note}
FIRSTNOHRINSTR = {ni}
FIRSTLEGATOINSTR = {ni}
NUMHRINSTR = {ni - 1}
NUMNOHRINSTR = 0
NUMLEGATOINSTR = 0
ADPARAM = $0f
SRPARAM = $00
FIXEDPARAMS = 0
SIMPLEPULSE = 0

mt_freqtbllo = ${freq_lo_addr:04x}
mt_freqtblhi = ${freq_hi_addr:04x}
mt_songtbllo = ${song_lo_addr:04x}
mt_songtblhi = ${song_hi_addr:04x}
mt_patttbllo = ${patt_lo_addr:04x}
mt_patttblhi = ${patt_hi_addr:04x}
mt_insad = ${insad_addr:04x}
mt_inssr = ${inssr_addr:04x}
mt_inswaveptr = ${inswaveptr_addr:04x}
mt_inspulseptr = ${inspulseptr_addr:04x}
mt_insfiltptr = ${insfiltptr_addr:04x}
mt_insvibparam = ${insvibparam_addr:04x}
mt_insvibdelay = ${insvibdelay_addr:04x}
mt_insgatetimer = ${insgatetimer_addr:04x}
mt_insfirstwave = ${insfirstwave_addr:04x}
mt_wavetbl = ${wavetbl_addr:04x}
mt_notetbl = ${notetbl_addr:04x}
mt_pulsetimetbl = ${pulsetimetbl_addr:04x}
mt_pulsespdtbl = ${pulsespdtbl_addr:04x}
mt_filttimetbl = ${filttimetbl_addr:04x}
mt_filtspdtbl = ${filtspdtbl_addr:04x}
mt_speedlefttbl = ${speedlefttbl_addr:04x}
mt_speedrighttbl = ${speedrighttbl_addr:04x}
"""

    # --- Two-pass assembly ---
    # Pass 1: assemble to find exact player size
    def assemble(defs_text):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False) as f:
            f.write(defs_text)
            with open(PLAYER_SRC) as ps:
                f.write(ps.read())
            asm_path = f.name
        bin_path = asm_path + '.bin'
        result = subprocess.run([TASS, '-o', bin_path, '-b', asm_path],
                              capture_output=True, text=True)
        os.unlink(asm_path)
        if result.returncode != 0:
            if os.path.exists(bin_path):
                os.unlink(bin_path)
            raise RuntimeError(f"Assembly failed:\n{result.stderr[:500]}")
        with open(bin_path, 'rb') as f:
            code = f.read()
        os.unlink(bin_path)
        return code

    player_code = assemble(defines)
    actual_player_size = len(player_code)

    if actual_player_size > DATA_OFFSET:
        raise ValueError(f"Player ({actual_player_size} bytes) exceeds DATA_OFFSET ({DATA_OFFSET})")

    # No counter patching needed - mt_initchn sets counter=1 during first play()

    # --- Build PSID header ---
    header = bytearray(124)
    header[0:4] = b'PSID'
    struct.pack_into('>H', header, 4, 2)
    struct.pack_into('>H', header, 6, 124)
    struct.pack_into('>H', header, 8, 0)
    struct.pack_into('>H', header, 10, base_addr)
    struct.pack_into('>H', header, 12, base_addr + 3)
    struct.pack_into('>H', header, 14, songs)
    struct.pack_into('>H', header, 16, 1)
    t = title.encode('ascii', errors='replace')[:31]
    header[22:22 + len(t)] = t
    a = author.encode('ascii', errors='replace')[:31]
    header[54:54 + len(a)] = a
    struct.pack_into('>H', header, 0x76, 0x0014)  # PAL, 6581

    # --- Combine: player + padding + data ---
    sid = bytearray()
    sid.extend(header)
    sid.extend(struct.pack('<H', base_addr))
    sid.extend(player_code)
    # Pad to DATA_OFFSET
    pad_needed = DATA_OFFSET - len(player_code)
    if pad_needed < 0:
        raise ValueError(f"Player ({len(player_code)} bytes) exceeds DATA_OFFSET ({DATA_OFFSET})")
    sid.extend(bytes(pad_needed))
    sid.extend(data)

    return bytes(sid), actual_player_size


def main():
    """Test: build a simple SID."""
    patterns = [bytes([0x90, 0xBD, 0xBD, 0xBD, 0x94, 0xBD, 0xBD, 0xBD,
                       0x97, 0xBD, 0xBD, 0xBD, 0x9C, 0xBD, 0xBD, 0xBD, 0x00])]
    orderlists = [bytes([0x00, 0x80, 0xFF, 0x00])] * 3

    wave_l = bytes([0x41, 0x41, 0x41, 0xFF])
    wave_r = bytes([0x80, 0x84, 0x87, 0x01])  # $80+offset for relative notes

    sid, ps = pack_sid(
        title='SIDfinity Packer Test',
        author='SIDfinity',
        num_instruments=3,
        instruments_ad=bytes([0x09, 0x0A, 0x0F]),
        instruments_sr=bytes([0x00, 0x00, 0xE8]),
        instruments_firstwave=bytes([0x41, 0x21, 0x81]),
        instruments_waveptr=bytes([0x01, 0x00, 0x00]),
        instruments_gatetimer=bytes([0x02, 0x02, 0x02]),
        wave_left=wave_l,
        wave_right=wave_r,
        orderlists=orderlists,
        patterns=patterns,
    )

    output = sys.argv[1] if len(sys.argv) > 1 else '/tmp/sf_packed.sid'
    with open(output, 'wb') as f:
        f.write(sid)
    print(f'Built {output}: {len(sid)} bytes (player: {ps})')

    siddump = os.path.join(SCRIPT_DIR, '..', 'tools', 'siddump')
    if os.path.exists(siddump):
        r = subprocess.run([siddump, output, '--duration', '2'],
                          capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            lines = r.stdout.strip().split('\n')
            print(f'siddump: {len(lines) - 2} frames')
            prev = ''
            for i, line in enumerate(lines[2:20]):
                regs = line.split(',')
                fhi = regs[1]
                if fhi != prev and fhi != '00':
                    print(f'  F{i}: V1_fhi={fhi}')
                    prev = fhi


if __name__ == '__main__':
    main()
