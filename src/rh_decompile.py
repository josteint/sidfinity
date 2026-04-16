#!/usr/bin/env python3
"""
Rob Hubbard SID decompiler.

Decompiles Rob Hubbard "classic" driver SIDs (Phase 2, ~30+ songs)
into structured data. Uses SIDdecompiler-style 6502 pattern matching
to locate data structures in the binary.

Usage:
    python3 src/rh_decompile.py <file.sid>
"""

import struct
import sys
import os


class RHInstrument:
    """8-byte Hubbard instrument definition."""
    def __init__(self, data, index):
        self.index = index
        self.pw_lo = data[0]
        self.pw_hi = data[1]
        self.pulse_width = self.pw_lo | (self.pw_hi << 8)
        self.ctrl = data[2]
        self.ad = data[3]
        self.sr = data[4]
        self.vibrato_depth = data[5]
        self.pwm_speed = data[6]
        self.fx_flags = data[7]
        self.has_drum = bool(self.fx_flags & 1)
        self.has_skydive = bool(self.fx_flags & 2)
        self.has_arpeggio = bool(self.fx_flags & 4)

    def __repr__(self):
        fx = []
        if self.has_drum: fx.append('DRUM')
        if self.has_skydive: fx.append('SKYDIVE')
        if self.has_arpeggio: fx.append('ARPEGGIO')
        fx_str = ' '.join(fx) if fx else 'none'
        return (f'Instr[{self.index:2d}] PW=${self.pulse_width:04X} '
                f'ctrl=${self.ctrl:02X} AD=${self.ad:02X} SR=${self.sr:02X} '
                f'vib={self.vibrato_depth} pwm=${self.pwm_speed:02X} fx={fx_str}')


class RHNote:
    """A single note event in a pattern."""
    def __init__(self):
        self.duration = 0       # 0-31 frames
        self.no_release = False  # gate not cleared at note end
        self.tie = False         # tied to previous (no re-trigger)
        self.instrument = None   # instrument number (if changed)
        self.portamento = None   # (speed, direction) tuple
        self.pitch = None        # pitch index (None for tied notes)
        self.raw_bytes = []

    def __repr__(self):
        parts = [f'dur={self.duration}']
        if self.no_release: parts.append('NOREL')
        if self.tie: parts.append('TIE')
        if self.instrument is not None: parts.append(f'instr={self.instrument}')
        if self.portamento is not None:
            speed, direction = self.portamento
            parts.append(f'porta={speed} {"down" if direction else "up"}')
        if self.pitch is not None: parts.append(f'pitch={self.pitch}')
        return ' '.join(parts)


class RHPattern:
    """A sequence of notes, terminated by $FF."""
    def __init__(self, index, addr):
        self.index = index
        self.addr = addr
        self.notes = []

    def __repr__(self):
        return f'Pattern[{self.index}] at ${self.addr:04X}: {len(self.notes)} notes'


class RHSong:
    """A song = 3 track pointers (one per SID voice)."""
    def __init__(self, index, addr, tracks):
        self.index = index
        self.addr = addr
        self.tracks = tracks  # list of 3 lists of pattern indices


class RHDecompiled:
    """Complete decompiled Rob Hubbard SID."""
    def __init__(self):
        self.title = ''
        self.author = ''
        self.released = ''
        self.load_addr = 0
        self.init_addr = 0
        self.play_addr = 0
        self.num_songs = 0
        self.instruments = []
        self.patterns = []
        self.songs = []
        self.freq_table_addr = 0
        self.song_table_addr = 0
        self.instr_addr = 0
        self.seqlo_addr = 0
        self.seqhi_addr = 0
        self.num_sequences = 0
        self.speed = None          # resetspd value (tempo = speed + 1)
        self.speed_table = None    # per-song speed table (list), or None


def load_sid(path):
    """Load a SID file, return (header_info, binary, load_addr)."""
    with open(path, 'rb') as f:
        raw = f.read()

    if raw[:4] not in (b'PSID', b'RSID'):
        raise ValueError(f'Not a SID file: {path}')

    version = struct.unpack('>H', raw[4:6])[0]
    data_offset = struct.unpack('>H', raw[6:8])[0]
    load_addr = struct.unpack('>H', raw[8:10])[0]
    init_addr = struct.unpack('>H', raw[10:12])[0]
    play_addr = struct.unpack('>H', raw[12:14])[0]
    num_songs = struct.unpack('>H', raw[14:16])[0]
    start_song = struct.unpack('>H', raw[16:18])[0]

    # Text fields
    title = raw[0x16:0x36].split(b'\x00')[0].decode('latin-1', errors='replace')
    author = raw[0x36:0x56].split(b'\x00')[0].decode('latin-1', errors='replace')
    released = raw[0x56:0x76].split(b'\x00')[0].decode('latin-1', errors='replace')

    payload = raw[data_offset:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', payload[:2])[0]
        binary = payload[2:]
    else:
        binary = payload

    return {
        'title': title,
        'author': author,
        'released': released,
        'load_addr': load_addr,
        'init_addr': init_addr,
        'play_addr': play_addr,
        'num_songs': num_songs,
        'start_song': start_song,
    }, binary, load_addr


def find_hex_pattern(binary, pattern, start=0):
    """Find a hex pattern with wildcards (**) in binary.

    Pattern format: "BD****99****E8C8C006" where ** matches any byte.
    Returns offset in binary, or -1 if not found.
    """
    # Parse pattern into bytes and mask
    pat_bytes = []
    pat_mask = []
    i = 0
    while i < len(pattern):
        if pattern[i:i+2] == '**':
            pat_bytes.append(0)
            pat_mask.append(False)
            i += 2
        else:
            pat_bytes.append(int(pattern[i:i+2], 16))
            pat_mask.append(True)
            i += 2

    pat_len = len(pat_bytes)
    for pos in range(start, len(binary) - pat_len + 1):
        match = True
        for j in range(pat_len):
            if pat_mask[j] and binary[pos + j] != pat_bytes[j]:
                match = False
                break
        if match:
            return pos
    return -1


def find_songs(binary, load_addr):
    """Find song table using SIDdecompiler pattern.

    Multi-song: LDA songs,X / STA currtrkhi,Y / INX / INY / CPY #N
    Pattern: BD ** ** 99 ** ** E8 C8 C0 NN
    N=6 for 3 voices, N=4 for 2 voices, N=8 for extended format.

    Single-song fallback: LDA currtrklo,X / STA zp / LDA currtrkhi,X / STA zp / DEC
    Pattern: BD ** ** 85 ** BD ** ** 85 ** DE

    Returns (songs_addr, is_multi, bytes_per_song) or (None, False, 0).
    """
    # Multi-song pattern — try CPY #6 (3 voices × 2 bytes) first,
    # then other values (CPY #4 for 2-voice songs like Human Race,
    # CPY #8 for songs with extra data per voice like BMX Kidz)
    for cpy_val in [0x06, 0x04, 0x08]:
        pat = f"BD****99****E8C8C0{cpy_val:02X}"
        pos = find_hex_pattern(binary, pat)
        if pos >= 0:
            songs_addr = binary[pos + 1] | (binary[pos + 2] << 8)
            return songs_addr, True, cpy_val

    # Single-song fallback: LDA currtrklo,X / STA zp / LDA currtrkhi,X / STA zp / DEC
    # Pattern: BD ** ** 85 ** BD ** ** 85 ** DE
    pos = find_hex_pattern(binary, "BD****85**BD****85**DE")
    if pos >= 0:
        currtrklo = binary[pos + 1] | (binary[pos + 2] << 8)
        currtrkhi = binary[pos + 6] | (binary[pos + 7] << 8)
        if currtrkhi - currtrklo == 3:
            return currtrklo, False, 6

    return None, False, 0


def find_instruments(binary, load_addr):
    """Find instrument table using SIDdecompiler pattern.

    LDA instr,X / STA $D402,Y / LDA instr+1,X / STA $D403,Y
    Pattern: BD ** ** 99 02 D4 BD ** ** 99 03 D4
    Alt (with PHA): BD ** ** 99 02 D4 48 BD ** ** 99 03 D4
    """
    pos = find_hex_pattern(binary, "BD****9902D4BD****9903D4")
    if pos >= 0:
        return binary[pos + 1] | (binary[pos + 2] << 8)

    pos = find_hex_pattern(binary, "BD****9902D448BD****9903D4")
    if pos >= 0:
        return binary[pos + 1] | (binary[pos + 2] << 8)

    return None


def find_seq_pointers(binary, load_addr):
    """Find sequence/pattern pointer tables.

    TAY / LDA patptl,Y / STA zp / LDA patpth,Y / STA zp
    Pattern: A8 B9 ** ** 85 ** B9 ** ** 85 **
    """
    pos = find_hex_pattern(binary, "A8B9****85**B9****85**")
    if pos >= 0:
        seqlo = binary[pos + 2] | (binary[pos + 3] << 8)
        seqhi = binary[pos + 7] | (binary[pos + 8] << 8)
        return seqlo, seqhi

    return None, None


def find_speed(binary, load_addr, num_songs=1):
    """Find song speed(s) from the player binary.

    Searches for the speed counter reset pattern:
        DEC speedcounter / BPL mainloop / LDA tempo / STA speedcounter

    Also searches for per-song speed tables in the init code:
        LDA songtempos,X / STA tempo

    Returns (default_speed, speed_table) where:
    - default_speed: the value at the tempo variable (0-based divider), or None
    - speed_table: list of per-song speeds if detected, or None
    Frames per tick = speed + 1.
    """
    tempo_addr = None
    default_speed = None

    # Find the speed counter reset pattern.
    # Variant 1: DEC counter / BPL / LDA tempo_var / STA counter
    #   CE lo hi 10 xx AD lo hi 8D lo hi
    # Variant 2: DEC counter / BPL / LDA #imm / STA counter (hardcoded speed)
    #   CE lo hi 10 xx A9 val 8D lo hi
    for i in range(len(binary) - 11):
        if binary[i] == 0xCE and binary[i + 3] == 0x10:
            counter_addr = binary[i + 1] | (binary[i + 2] << 8)

            if binary[i + 5] == 0xAD:
                # Variant 1: LDA abs (speed from variable)
                t_addr = binary[i + 6] | (binary[i + 7] << 8)
                sta_addr = binary[i + 8 + 1] | (binary[i + 8 + 2] << 8) if binary[i + 8] == 0x8D else 0
                if sta_addr == counter_addr:
                    off = t_addr - load_addr
                    if 0 <= off < len(binary):
                        val = binary[off]
                        if val <= 15:
                            tempo_addr = t_addr
                            default_speed = val
                            break

            elif binary[i + 5] == 0xA9:
                # Variant 2: LDA #imm (hardcoded speed constant)
                val = binary[i + 6]
                sta_off = i + 7
                if (sta_off + 2 < len(binary) and binary[sta_off] == 0x8D and
                        (binary[sta_off + 1] | (binary[sta_off + 2] << 8)) == counter_addr):
                    if val <= 15:
                        tempo_addr = counter_addr  # no separate tempo var
                        default_speed = val
                        break

    # Search for per-song speed table: LDA songtempos,X / STA tempo
    # Pattern: BD xx xx 8D yy yy where yy yy = tempo_addr
    speed_table = None
    if tempo_addr is not None and num_songs > 1:
        for i in range(len(binary) - 6):
            if (binary[i] == 0xBD and binary[i + 3] == 0x8D and
                    (binary[i + 4] | (binary[i + 5] << 8)) == tempo_addr):
                table_addr = binary[i + 1] | (binary[i + 2] << 8)
                off = table_addr - load_addr
                if 0 <= off < len(binary) and off + num_songs <= len(binary):
                    speeds = []
                    for s in range(num_songs):
                        v = binary[off + s]
                        if v > 15:
                            break
                        speeds.append(v)
                    if len(speeds) == num_songs:
                        speed_table = speeds
                break

    return default_speed, speed_table


def find_freq_table(binary, load_addr):
    """Find frequency table by known PAL freq byte sequences."""
    # Standard PAL freq table lo bytes (C-1 through B-1)
    PAL_LO = bytes([0x17, 0x27, 0x39, 0x4b, 0x5f, 0x74, 0x8a, 0xa1, 0xba, 0xd4, 0xf0, 0x0e])

    # Try full 12-byte match first, then shorter
    for window in range(12, 5, -1):
        pos = binary.find(PAL_LO[:window])
        if pos >= 0:
            return load_addr + pos

    # Also try searching for the hi bytes: 01 01 01 01 01 01 01 01 01 01 01 02
    PAL_HI = bytes([0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x02])
    pos = binary.find(PAL_HI)
    if pos >= 0:
        # Lo table is likely 96 bytes before (8 octaves * 12 notes)
        return load_addr + pos - 96

    return None


def peek(binary, load_addr, addr):
    off = addr - load_addr
    if 0 <= off < len(binary):
        return binary[off]
    return 0


def decode_pattern(binary, load_addr, addr, max_bytes=256):
    """Decode a pattern starting at addr. Returns list of RHNote."""
    notes = []
    off = addr - load_addr
    pos = 0

    while pos < max_bytes:
        if off + pos >= len(binary):
            break

        b0 = binary[off + pos]
        if b0 == 0xFF:
            break

        note = RHNote()
        note.raw_bytes.append(b0)
        note.duration = b0 & 0x1F
        note.no_release = bool(b0 & 0x20)
        note.tie = bool(b0 & 0x40)
        has_modifier = bool(b0 & 0x80)
        pos += 1

        if has_modifier:
            b1 = binary[off + pos]
            note.raw_bytes.append(b1)
            if b1 & 0x80:
                # Portamento
                speed = (b1 >> 1) & 0x3F
                direction = b1 & 1  # 0=up, 1=down
                note.portamento = (speed, direction)
            else:
                note.instrument = b1
            pos += 1

        # Pitch byte — present unless this is a pure tie (no modifier)
        if not (note.tie and not has_modifier):
            if off + pos < len(binary):
                note.pitch = binary[off + pos]
                note.raw_bytes.append(note.pitch)
                pos += 1

        notes.append(note)

    return notes


def decode_track(binary, load_addr, track_addr, max_patterns=128):
    """Decode a track = sequence of pattern indices until $FF or $FE."""
    patterns = []
    off = track_addr - load_addr
    for i in range(max_patterns):
        if off + i >= len(binary):
            break
        b = binary[off + i]
        if b == 0xFF:
            patterns.append(('loop', None))
            break
        elif b == 0xFE:
            patterns.append(('stop', None))
            break
        else:
            patterns.append(('pattern', b))
    return patterns


def decompile(sid_path, verbose=False):
    """Decompile a Rob Hubbard SID file."""
    header, binary, load_addr = load_sid(sid_path)

    result = RHDecompiled()
    result.title = header['title']
    result.author = header['author']
    result.released = header['released']
    result.load_addr = load_addr
    result.init_addr = header['init_addr']
    result.play_addr = header['play_addr']
    result.num_songs = header['num_songs']

    if verbose:
        print(f'"{result.title}" by {result.author}')
        print(f'Load: ${load_addr:04X}, Init: ${result.init_addr:04X}, '
              f'Play: ${result.play_addr:04X}, Songs: {result.num_songs}')
        print(f'Binary: {len(binary)} bytes (${load_addr:04X}-${load_addr+len(binary)-1:04X})')
        print()

    # --- Find data structures via pattern matching ---

    # Song table
    songs_addr, is_multi, bytes_per_song = find_songs(binary, load_addr)
    if songs_addr is None:
        print('ERROR: Could not find song table pattern', file=sys.stderr)
        return None
    result.song_table_addr = songs_addr
    num_voices = bytes_per_song // 2  # each voice = 2 bytes (lo + hi pointer)
    if verbose:
        print(f'Song table at ${songs_addr:04X} ({"multi" if is_multi else "single"}, {num_voices} voices, {bytes_per_song} bytes/song)')

    # Instruments
    instr_addr = find_instruments(binary, load_addr)
    if instr_addr is None:
        print('ERROR: Could not find instrument pattern', file=sys.stderr)
        return None
    result.instr_addr = instr_addr
    if verbose:
        print(f'Instruments at ${instr_addr:04X}')

    # Sequence pointers
    seqlo, seqhi = find_seq_pointers(binary, load_addr)
    if seqlo is None:
        print('ERROR: Could not find sequence pointer pattern', file=sys.stderr)
        return None
    result.seqlo_addr = seqlo
    result.seqhi_addr = seqhi
    result.num_sequences = seqhi - seqlo
    if verbose:
        print(f'Sequence pointers: lo=${seqlo:04X} hi=${seqhi:04X} ({result.num_sequences} sequences)')

    # Freq table (optional — not all songs use standard PAL table)
    freq_addr = find_freq_table(binary, load_addr)
    result.freq_table_addr = freq_addr
    if verbose:
        if freq_addr:
            print(f'Freq table at ${freq_addr:04X}')
        else:
            print('Freq table: not found (custom or interleaved)')

    # Speed detection
    speed, speed_table = find_speed(binary, load_addr, result.num_songs)
    result.speed = speed
    result.speed_table = speed_table
    if verbose:
        if speed is not None:
            print(f'Speed: {speed} (tempo = {speed + 1} frames/tick)')
            if speed_table:
                print(f'Per-song speeds: {speed_table}')
        else:
            print('Speed: not detected (defaulting to 1)')

    if verbose:
        print()

    # --- Parse songs ---
    for s in range(result.num_songs):
        if is_multi:
            off = songs_addr - load_addr + s * bytes_per_song
            if off + bytes_per_song > len(binary):
                break
            half = bytes_per_song // 2
            lo = [binary[off + j] for j in range(half)]
            hi = [binary[off + half + j] for j in range(half)]
            track_addrs = [lo[j] | (hi[j] << 8) for j in range(min(half, 3))]
            # Pad to 3 voices if fewer (2-voice songs get an empty V3)
            while len(track_addrs) < 3:
                track_addrs.append(0)
        else:
            off = songs_addr - load_addr
            if off + 6 > len(binary):
                break
            track_addrs = [
                binary[off] | (binary[off + 3] << 8),
                binary[off + 1] | (binary[off + 4] << 8),
                binary[off + 2] | (binary[off + 5] << 8),
            ]

        # Validate track addresses are in SID range
        valid = all(a == 0 or (load_addr <= a < load_addr + len(binary)) for a in track_addrs)
        if not valid:
            if verbose:
                print(f'Song {s}: INVALID track pointers ' +
                      ' '.join(f'${a:04X}' for a in track_addrs))
            continue

        tracks = []
        for v in range(3):
            if track_addrs[v] == 0:
                tracks.append([('stop', None)])  # empty voice
            else:
                tracks.append(decode_track(binary, load_addr, track_addrs[v]))

        song = RHSong(s, songs_addr + s * bytes_per_song, tracks)
        result.songs.append(song)

        if verbose:
            print(f'Song {s}: V1=${track_addrs[0]:04X} V2=${track_addrs[1]:04X} V3=${track_addrs[2]:04X}')
            for v in range(3):
                pats = [f'pat{p[1]}' if p[0] == 'pattern' else p[0].upper()
                        for p in tracks[v]]
                print(f'  Voice {v+1}: {" ".join(pats[:20])}{"..." if len(pats) > 20 else ""}')

    if verbose:
        print()

    # --- Parse patterns ---
    all_pattern_indices = set()
    for song in result.songs:
        for track in song.tracks:
            for kind, idx in track:
                if kind == 'pattern' and idx is not None:
                    all_pattern_indices.add(idx)

    for idx in sorted(all_pattern_indices):
        if idx >= result.num_sequences:
            if verbose:
                print(f'Pattern {idx}: index out of range (max={result.num_sequences-1})')
            continue
        pat_lo = peek(binary, load_addr, seqlo + idx)
        pat_hi = peek(binary, load_addr, seqhi + idx)
        pat_addr = pat_lo | (pat_hi << 8)

        if not (load_addr <= pat_addr < load_addr + len(binary)):
            if verbose:
                print(f'Pattern {idx}: address ${pat_addr:04X} out of range')
            continue

        notes = decode_pattern(binary, load_addr, pat_addr)
        pattern = RHPattern(idx, pat_addr)
        pattern.notes = notes
        result.patterns.append(pattern)

    if verbose:
        print(f'Decoded {len(result.patterns)} patterns')
        for pat in result.patterns[:10]:
            print(f'  {pat}')
            for note in pat.notes[:4]:
                print(f'    {note}')
            if len(pat.notes) > 4:
                print(f'    ... ({len(pat.notes)} total)')
        if len(result.patterns) > 10:
            print(f'  ... ({len(result.patterns)} total)')
        print()

    # --- Parse instruments ---
    # Estimate instrument count from max instrument index used in patterns
    max_instr = 0
    for pat in result.patterns:
        for note in pat.notes:
            if note.instrument is not None:
                max_instr = max(max_instr, note.instrument)

    num_instr = max_instr + 1
    for i in range(num_instr):
        off = instr_addr - load_addr + i * 8
        if off + 8 > len(binary):
            break
        data = binary[off:off + 8]
        instr = RHInstrument(data, i)
        result.instruments.append(instr)

    if verbose:
        print(f'{len(result.instruments)} instruments:')
        for instr in result.instruments:
            print(f'  {instr}')
        print()

    # --- Summary ---
    total_notes = sum(len(p.notes) for p in result.patterns)
    valid_songs = len(result.songs)
    if verbose:
        print(f'=== SUMMARY ===')
        print(f'Songs: {valid_songs} valid / {result.num_songs} total')
        print(f'Patterns: {len(result.patterns)}')
        print(f'Notes: {total_notes}')
        print(f'Instruments: {len(result.instruments)}')
        effects = set()
        for instr in result.instruments:
            if instr.has_drum: effects.add('drum')
            if instr.has_skydive: effects.add('skydive')
            if instr.has_arpeggio: effects.add('arpeggio')
        print(f'Effects used: {", ".join(sorted(effects)) if effects else "none"}')

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Rob Hubbard SID decompiler')
    parser.add_argument('input', help='SID file to decompile')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true', help='Only print summary')
    args = parser.parse_args()

    result = decompile(args.input, verbose=not args.quiet)
    if result is None:
        sys.exit(1)

    if not args.quiet and not args.verbose:
        # Default: medium output
        print(f'"{result.title}" by {result.author}')
        print(f'{len(result.songs)} songs, {len(result.patterns)} patterns, '
              f'{len(result.instruments)} instruments, '
              f'{sum(len(p.notes) for p in result.patterns)} notes')


if __name__ == '__main__':
    main()
