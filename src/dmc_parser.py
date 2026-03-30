"""
dmc_parser.py - Parse DMC (Demo Music Creator) SID files.

DMC uses fixed offsets (unlike GoatTracker's conditional compilation):
  +$0000: JMP init, JMP play
  +$06A8: Frequency table hi (96 bytes)
  +$0708: Frequency table lo (96 bytes)
  +$08F0: Instrument table (32 x 11 bytes)
  +$0AA2: Track data (sector order lists)
  +$0BF9: Tune pointer table (8 x 8 bytes)
  +$0C01: Sector data (variable length)
  end-2N: Sector pointer table (N lo bytes + N hi bytes)

Sector data encoding:
  $00-$5F: Note (C-0 through B-7)
  $60-$7C: Duration (AND $1F = ticks)
  $7D: Continuation (no ADSR reset)
  $7E: Gate off
  $7F: End of sector
  $80-$9F: Instrument select (AND $1F)
  $A0-$BF: Glide command
"""

import struct
import sys
import os

# DMC frequency table (first 24 bytes of hi table for detection)
DMC_FREQ_HI_NEEDLE = bytes([
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
])

# DMC constants
DMC_SECTOR_END = 0x7F
DMC_GATE_OFF = 0x7E
DMC_CONTINUATION = 0x7D


def parse_psid_header(data):
    """Parse PSID header, return header dict + binary + load_addr."""
    if data[:4] not in (b'PSID', b'RSID'):
        raise ValueError("Not a SID file")
    data_offset = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]
    songs = struct.unpack('>H', data[14:16])[0]
    title = data[22:54].split(b'\x00')[0].decode('latin-1')
    author = data[54:86].split(b'\x00')[0].decode('latin-1')

    payload = data[data_offset:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', payload[:2])[0]
        binary = payload[2:]
    else:
        binary = payload

    return {
        'title': title,
        'author': author,
        'load_addr': load_addr,
        'init_addr': init_addr,
        'play_addr': play_addr,
        'songs': songs,
    }, binary, load_addr


def find_dmc_base(binary):
    """Find the DMC player base offset by locating the freq table.

    Returns base_offset (0 for standard layout) or None.
    """
    pos = binary.find(DMC_FREQ_HI_NEEDLE)
    if pos == -1:
        return None
    # Standard DMC has freq hi at +$06A8
    base = pos - 0x06A8
    if base < 0:
        return None
    # Verify: JMP at base+0 and base+3
    if base + 3 < len(binary) and binary[base] == 0x4C and binary[base + 3] == 0x4C:
        return base
    # If base is 0 and binary starts with JMP
    if binary[0] == 0x4C and binary[3] == 0x4C:
        return 0
    return None


def parse_dmc_sid(data):
    """Parse a DMC SID file into its components."""
    header, binary, load_addr = parse_psid_header(data)

    base = find_dmc_base(binary)
    if base is None:
        raise ValueError("Could not identify DMC layout")

    songs = header['songs']

    # Read instruments (32 x 11 bytes at base+$08F0)
    instr_off = base + 0x08F0
    instruments = []
    for i in range(32):
        b = instr_off + i * 11
        if b + 11 > len(binary):
            break
        raw = list(binary[b:b + 11])
        instruments.append({
            'index': i,
            'ad': raw[0], 'sr': raw[1], 'wave_ptr': raw[2],
            'pw1': raw[3], 'pw2': raw[4], 'pw3': raw[5],
            'pw_limit': raw[6], 'vib1': raw[7], 'vib2': raw[8],
            'filter': raw[9], 'fx': raw[10],
            'raw': raw,
        })

    # Read tune pointer table (base+$0BF9, 8 x 8 bytes)
    tpt_off = base + 0x0BF9
    tune_pointers = []
    for t in range(min(songs, 8)):
        b = tpt_off + t * 8
        if b + 6 > len(binary):
            break
        v1 = binary[b] | (binary[b + 1] << 8)
        v2 = binary[b + 2] | (binary[b + 3] << 8)
        v3 = binary[b + 4] | (binary[b + 5] << 8)
        tune_pointers.append((v1, v2, v3))

    # Find sector pointer table at end of file
    # It's 2*N bytes at the end: N lo bytes then N hi bytes
    # Sectors are numbered 0 to N-1
    # We detect N by scanning backward from end for valid sector addresses

    # Sector data starts around base+$0C01
    sector_data_start = load_addr + base + 0x0C01

    # The sector pointer table contains addresses that should point
    # into the sector data area. Scan from end of binary.
    num_sectors = 0
    for n in range(1, 65):  # max 64 sectors
        # Test if last 2*n bytes form valid sector pointers
        if 2 * n > len(binary):
            break
        lo_start = len(binary) - 2 * n
        hi_start = len(binary) - n

        valid = True
        for j in range(n):
            addr = binary[lo_start + j] | (binary[hi_start + j] << 8)
            if not (sector_data_start <= addr < load_addr + len(binary)):
                valid = False
                break
        if valid:
            num_sectors = n

    # Read sector pointer table
    sector_addrs = []
    if num_sectors > 0:
        lo_start = len(binary) - 2 * num_sectors
        hi_start = len(binary) - num_sectors
        for j in range(num_sectors):
            addr = binary[lo_start + j] | (binary[hi_start + j] << 8)
            sector_addrs.append(addr)

    # Read sector data
    sectors = []
    for addr in sector_addrs:
        off = addr - load_addr
        if off < 0 or off >= len(binary):
            sectors.append([])
            continue
        raw = []
        i = off
        while i < len(binary) and binary[i] != DMC_SECTOR_END:
            raw.append(binary[i])
            i += 1
        if i < len(binary):
            raw.append(DMC_SECTOR_END)
        sectors.append(raw)

    # Read track data (base+$0AA2)
    # Track data is the order list for each voice per subtune
    # Format: byte sequence where each byte is a sector number,
    # $FF = loop, $FE = end
    track_off = base + 0x0AA2

    return {
        'header': header,
        'load_addr': load_addr,
        'base': base,
        'binary': binary,
        'instruments': instruments,
        'tune_pointers': tune_pointers,
        'num_sectors': num_sectors,
        'sector_addrs': sector_addrs,
        'sectors': sectors,
        'header_bytes': data[:124],
        'load_addr_bytes': data[124:126] if struct.unpack('>H', data[8:10])[0] == 0 else b'',
    }


def coarse_roundtrip(sid_path):
    """Test coarse roundtrip: just verify we can read and reconstruct."""
    with open(sid_path, 'rb') as f:
        original = f.read()

    try:
        parsed = parse_dmc_sid(original)
    except ValueError:
        return 'skip'

    # Reconstruct: header + load_addr_bytes + binary (unchanged)
    rebuilt = bytearray()
    rebuilt.extend(parsed['header_bytes'])
    rebuilt.extend(parsed['load_addr_bytes'])
    rebuilt.extend(parsed['binary'])

    if bytes(rebuilt) == original:
        ns = parsed['num_sectors']
        ni = sum(1 for i in parsed['instruments'] if any(v != 0 for v in i['raw']))
        return f'match|sectors={ns}|instr={ni}'
    return 'diff'


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parse DMC SID files')
    parser.add_argument('input', nargs='+', help='SID file(s)')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    match = fail = skip = 0
    for path in args.input:
        if not os.path.exists(path):
            continue
        result = coarse_roundtrip(path)
        if result.startswith('match'):
            match += 1
            if args.verbose:
                print(f'  OK {os.path.basename(path)} ({result})')
        elif result == 'skip':
            skip += 1
        else:
            fail += 1
            print(f'FAIL {os.path.basename(path)}: {result}')

    print(f'\nResults: {match} match, {fail} fail, {skip} skip')


if __name__ == '__main__':
    main()
