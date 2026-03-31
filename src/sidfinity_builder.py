"""
sidfinity_builder.py - Build SIDfinity SID files from music data.

Takes instruments, patterns, orderlists, and a frequency table,
assembles the SIDfinity player, and outputs a complete .sid file.

The player code is assembled from sidfinity.asm using 64tass.
The data section is built by this script and appended.

Memory layout:
  $0800-$0A6E: Player code (sidfinity.asm, ~623 bytes)
  $0B00-$0BCF: Channel variables (initialized by player init)
  $0BD0-$0BFF: Global state + orderlist pointers (set by init patch)
  $0C00+:      Song data (instrument table, orderlists, patterns)
"""

import struct
import subprocess
import sys
import os
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TASS = os.path.join(PROJECT_ROOT, 'tools', '64tass')
SIDDUMP = os.path.join(PROJECT_ROOT, 'tools', 'siddump')
PLAYER_SRC = os.path.join(SCRIPT_DIR, 'player', 'sidfinity.asm')

LOAD_ADDR = 0x0800
INIT_ADDR = 0x0800
PLAY_ADDR = 0x0803
DATA_ADDR = 0x0C00

# Player variable addresses (from sidfinity.asm)
OL_LO = 0x0B80
OL_HI = 0x0B83
G_VOLUME = 0x0B70

# GT2 pattern encoding constants
ENDPATT = 0x00
FIRSTNOTE = 0x60
REST = 0xBD
KEYOFF = 0xBE
KEYON = 0xBF

# Standard PAL frequency table
FREQ_LO_PAL = bytes([
    0x17,0x27,0x39,0x4B,0x5F,0x74,0x8A,0xA1,0xBA,0xD4,0xF0,0x0E,
    0x2D,0x4E,0x71,0x96,0xBE,0xE8,0x14,0x43,0x74,0xA9,0xE1,0x1C,
    0x5A,0x9C,0xE2,0x2D,0x7C,0xCF,0x28,0x85,0xE8,0x52,0xC1,0x37,
    0xB4,0x39,0xC5,0x5A,0xF7,0x9E,0x4F,0x0A,0xD1,0xA3,0x82,0x6E,
    0x68,0x71,0x8A,0xB3,0xEE,0x3C,0x9E,0x15,0xA2,0x46,0x04,0xDC,
    0xD0,0xE2,0x14,0x67,0xDD,0x79,0x3C,0x29,0x44,0x8D,0x08,0xB8,
    0xA1,0xC5,0x28,0xCD,0xBA,0xF1,0x78,0x53,0x87,0x1A,0x10,0x71,
    0x42,0x89,0x4F,0x9B,0x74,0xE2,0xF0,0xA6,0x0E,0x33,0x20,0xFF,
])
FREQ_HI_PAL = bytes([
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
    0x04,0x04,0x04,0x05,0x05,0x05,0x06,0x06,0x06,0x07,0x07,0x08,
    0x08,0x09,0x09,0x0A,0x0A,0x0B,0x0C,0x0D,0x0D,0x0E,0x0F,0x10,
    0x11,0x12,0x13,0x14,0x15,0x17,0x18,0x1A,0x1B,0x1D,0x1F,0x20,
    0x22,0x24,0x27,0x29,0x2B,0x2E,0x31,0x34,0x37,0x3A,0x3E,0x41,
    0x45,0x49,0x4E,0x52,0x57,0x5C,0x62,0x68,0x6E,0x75,0x7C,0x83,
    0x8B,0x93,0x9C,0xA5,0xAF,0xB9,0xC4,0xD0,0xDD,0xEA,0xF8,0xFF,
])


def assemble_player():
    """Assemble the SIDfinity player using 64tass."""
    result = subprocess.run(
        [TASS, '-o', '/tmp/sidfinity_player.bin', '-b', PLAYER_SRC],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Assembly failed:\n{result.stderr}")
    with open('/tmp/sidfinity_player.bin', 'rb') as f:
        return f.read()


def build_psid_header(title='SIDfinity', author='SIDfinity', songs=1,
                      sid_model=1, clock=1):
    """Build PSID v2 header."""
    header = bytearray(124)
    header[0:4] = b'PSID'
    struct.pack_into('>H', header, 4, 2)
    struct.pack_into('>H', header, 6, 124)
    struct.pack_into('>H', header, 8, 0)  # load addr from data
    struct.pack_into('>H', header, 10, INIT_ADDR)
    struct.pack_into('>H', header, 12, PLAY_ADDR)
    struct.pack_into('>H', header, 14, songs)
    struct.pack_into('>H', header, 16, 1)
    t = title.encode('ascii', errors='replace')[:31]
    header[22:22+len(t)] = t
    a = author.encode('ascii', errors='replace')[:31]
    header[54:54+len(a)] = a
    flags = (sid_model << 4) | (clock << 2)
    struct.pack_into('>H', header, 0x76, flags)
    return bytes(header)


def build_init_patch(player_size, ol_addrs, instruments, freq_table=None):
    """Build init patch code that sets up orderlists and instruments.

    The player's init clears variables and sets defaults. This patch
    runs after init and sets the specific music data pointers.
    """
    patch = bytearray()

    # Set orderlist pointers
    for i, addr in enumerate(ol_addrs):
        patch.extend([0xA9, addr & 0xFF, 0x8D, (OL_LO + i) & 0xFF, (OL_LO + i) >> 8])
    for i, addr in enumerate(ol_addrs):
        patch.extend([0xA9, (addr >> 8) & 0xFF, 0x8D, (OL_HI + i) & 0xFF, (OL_HI + i) >> 8])

    # Set instrument defaults for each voice
    # Group B: wave($0B15) ad($0B16) sr($0B17) pulselo($0B1A) pulsehi($0B1B)
    for vi in range(min(3, len(instruments))):
        instr = instruments[vi]
        offset = vi * 7  # stride 7
        for val, base in [
            (instr.get('wave', 0x41), 0x0B15),
            (instr.get('ad', 0x09), 0x0B16),
            (instr.get('sr', 0x00), 0x0B17),
            (instr.get('pulselo', 0x08), 0x0B1A),
            (instr.get('pulsehi', 0x08), 0x0B1B),
        ]:
            addr = base + offset
            patch.extend([0xA9, val, 0x8D, addr & 0xFF, (addr >> 8) & 0xFF])

    patch.append(0x60)  # RTS
    return bytes(patch)


def build_sid(title, author, patterns, orderlists, instruments=None,
              freq_lo=None, freq_hi=None, songs=1, tempo=6):
    """Build a complete SIDfinity SID file.

    Args:
        title: Song title
        author: Song author
        patterns: list of bytes objects (GT2 packed pattern data)
        orderlists: list of 3 bytes objects (one per voice)
        instruments: list of 3 dicts with wave/ad/sr/pulselo/pulsehi
        freq_lo: 96-byte frequency table (lo), or None for PAL default
        freq_hi: 96-byte frequency table (hi), or None for PAL default
        songs: number of subtunes
        tempo: frames per row
    """
    if freq_lo is None:
        freq_lo = FREQ_LO_PAL
    if freq_hi is None:
        freq_hi = FREQ_HI_PAL
    if instruments is None:
        instruments = [
            {'wave': 0x41, 'ad': 0x09, 'sr': 0x00, 'pulselo': 0x08, 'pulsehi': 0x08},
            {'wave': 0x21, 'ad': 0x0A, 'sr': 0x00},
            {'wave': 0x81, 'ad': 0x00, 'sr': 0xF0},
        ]

    # Assemble player
    player = assemble_player()

    # The player has a built-in freq table at the end.
    # We need to REPLACE it with our custom freq table.
    # Find the freq table in the player binary.
    # It starts with the lo table (same as PAL default).
    ft_pos = player.find(FREQ_LO_PAL[:12])
    if ft_pos >= 0 and ft_pos + 192 <= len(player):
        player = bytearray(player)
        player[ft_pos:ft_pos+96] = freq_lo
        player[ft_pos+96:ft_pos+192] = freq_hi
        player = bytes(player)

    # Build binary
    binary = bytearray()
    binary.extend(struct.pack('<H', LOAD_ADDR))  # load address
    binary.extend(player)

    # Find init RTS and patch it
    # Init starts at binary[2] (JMP init), the init code is somewhere in the player
    init_target = binary[3] | (binary[4] << 8)
    init_off = init_target - LOAD_ADDR + 2
    rts_pos = None
    for i in range(init_off, init_off + 200):
        if i < len(binary) and binary[i] == 0x60:
            rts_pos = i
            break

    # Build song data
    # Layout at DATA_ADDR:
    #   Pattern pointer table: lo[max_patt] + hi[max_patt]
    #   Orderlists
    #   Pattern data
    max_patt = max(128, len(patterns))
    patt_tbl_size = max_patt * 2

    ol_base = DATA_ADDR + patt_tbl_size
    ol_blob = bytearray()
    ol_addrs = []
    for ol in orderlists:
        ol_addrs.append(ol_base + len(ol_blob))
        ol_blob.extend(ol)

    patt_base = ol_base + len(ol_blob)
    patt_blob = bytearray()
    patt_addrs = []
    for patt in patterns:
        patt_addrs.append(patt_base + len(patt_blob))
        patt_blob.extend(patt)

    # Build pattern pointer table
    patt_tbl = bytearray(patt_tbl_size)
    for i, addr in enumerate(patt_addrs):
        if i < max_patt:
            patt_tbl[i] = addr & 0xFF
            patt_tbl[max_patt + i] = (addr >> 8) & 0xFF

    song_data = patt_tbl + ol_blob + patt_blob

    # Pad binary to DATA_ADDR
    pad_needed = DATA_ADDR - LOAD_ADDR - len(player)
    if pad_needed < 0:
        raise ValueError(f"Player too large ({len(player)} bytes), overlaps data area")

    # Build init patch
    patch = build_init_patch(len(player), ol_addrs, instruments)

    # Place patch in the padding area
    patch_addr = LOAD_ADDR + len(player)
    if rts_pos is not None and rts_pos + 3 <= len(binary):
        # Replace RTS with JMP to patch
        binary[rts_pos] = 0x4C
        binary[rts_pos + 1] = patch_addr & 0xFF
        binary[rts_pos + 2] = (patch_addr >> 8) & 0xFF

    # Extend with patch + padding + song data
    binary.extend(patch)
    remaining_pad = DATA_ADDR - LOAD_ADDR + 2 - len(binary)
    if remaining_pad > 0:
        binary.extend(b'\x00' * remaining_pad)
    binary.extend(song_data)

    # Build PSID header
    header = build_psid_header(title, author, songs)

    return bytes(header) + bytes(binary)


def main():
    """Build a test SID with a C major scale."""
    patterns = [
        # Pattern 0: C major scale
        bytes([FIRSTNOTE+48, REST, REST, REST,  # C4
               FIRSTNOTE+52, REST, REST, REST,  # E4
               FIRSTNOTE+55, REST, REST, REST,  # G4
               FIRSTNOTE+60, REST, REST, REST,  # C5
               ENDPATT]),
        # Pattern 1: bass
        bytes([FIRSTNOTE+24, REST, REST, REST, REST, REST, REST, REST,  # C2
               FIRSTNOTE+29, REST, REST, REST, REST, REST, REST, REST,  # F2
               ENDPATT]),
    ]

    orderlists = [
        bytes([0x00, 0x80, 0xFF, 0x00]),  # voice 1: pattern 0, loop
        bytes([0x01, 0x80, 0xFF, 0x00]),  # voice 2: pattern 1, loop
        bytes([0x01, 0x80, 0xFF, 0x00]),  # voice 3: pattern 1, loop
    ]

    output = sys.argv[1] if len(sys.argv) > 1 else '/tmp/sidfinity_test.sid'
    sid = build_sid('SIDfinity Test', 'SIDfinity', patterns, orderlists)

    with open(output, 'wb') as f:
        f.write(sid)
    print(f'Built {output}: {len(sid)} bytes')

    # Test
    if os.path.exists(SIDDUMP):
        r = subprocess.run([SIDDUMP, output, '--duration', '3'],
                          capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            lines = r.stdout.strip().split('\n')
            print(f'siddump: {len(lines)-2} frames')
            prev = ''
            for i, line in enumerate(lines[2:30]):
                regs = line.split(',')
                if len(regs) >= 5:
                    fhi = regs[1]
                    if fhi != prev and fhi != '00':
                        print(f'  F{i}: V1_fhi={fhi} ctrl={regs[4]}')
                        prev = fhi


if __name__ == '__main__':
    main()
