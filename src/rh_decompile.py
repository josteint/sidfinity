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
        self.freq_table_interleaved = False  # True if lo0,hi0,lo1,hi1,... format with >5% PAL deviation
        self.song_table_addr = 0
        self.instr_addr = 0
        self.seqlo_addr = 0
        self.seqhi_addr = 0
        self.num_sequences = 0
        self.seq_interleaved = False
        self.speed = None          # resetspd value (tempo = speed + 1)
        self.speed_table = None    # per-song speed table (list), or None
        self.upper_nibble_arp = False  # True if driver uses fx_flags upper nibble as arp interval (Phase 4)
        self.voice_transpose = [0, 0, 0]  # per-voice semitone transpose offset (from ADC abs,X before freq table)
        self.drum_freq_slide = 0   # per-frame freq_hi delta for drum effect (typically -1)


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


def simulate_init(binary, load_addr, init_addr, verbose=False):
    """Simulate the init routine's static memory writes on a copy of the binary.

    Some Hubbard SIDs use self-modifying code: the init routine patches player
    code addresses (LDA #imm / STA abs pairs) and copies data blocks
    (LDA abs,X / STA abs,X / INX / CPX #N / BNE loops) before the player runs.
    Without simulating these, the static binary looks wrong to the decompiler.

    Uses a minimal 6502 interpreter that tracks the A register and applies:
      - LDA #imm  (A9): sets A
      - STA abs   (8D): writes A to the in-binary address (if in range).
        Multiple consecutive STA abs instructions share the same A value.
      - LDA abs,X (BD) / STA abs,X (9D) / INX (E8) / CPX #N (E0 xx) / BNE (D0):
        detects the copy-loop idiom and copies N bytes src->dst
      - JMP abs   (4C): follows into target (one extra level via flat recursion)
      - RTS       (60): stops

    All other instructions are decoded for length only (using a compact length
    table) so the PC advances correctly without modifying any state.
    A-register invalidated by any instruction that logically modifies A.
    Only modifies a copy of the binary — the original is never touched.
    """
    # Compact 6502 instruction length table indexed by opcode.
    # 0 = unknown/illegal -> treat as 1 byte.
    _LEN = [
        #0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
        1, 2, 1, 1, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 3,  # 0x
        2, 2, 1, 1, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 3,  # 1x
        3, 2, 1, 1, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 3,  # 2x
        2, 2, 1, 1, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 3,  # 3x
        1, 2, 1, 1, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 3,  # 4x
        2, 2, 1, 1, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 3,  # 5x
        1, 2, 1, 1, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 3,  # 6x
        2, 2, 1, 1, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 3,  # 7x
        2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 3,  # 8x
        2, 2, 1, 1, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 3,  # 9x
        2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 3,  # Ax
        2, 2, 1, 1, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 3,  # Bx
        2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 3,  # Cx
        2, 2, 1, 1, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 3,  # Dx
        2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 3,  # Ex
        2, 2, 1, 1, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 3,  # Fx
    ]
    # Opcodes that modify the A register (excluding LDA #imm which we handle separately)
    _A_MODIFYING = frozenset([
        0xAD, 0xA5, 0xB5, 0xB9, 0xA1, 0xB1,       # LDA abs/zp/zp,X/abs,Y/(ind,X)/(ind),Y
        0x68, 0x98, 0x8A,                           # PLA, TYA, TXA
        0x6A, 0x4A, 0x0A, 0x2A,                    # ROR/LSR/ASL/ROL A
        0x69, 0x65, 0x6D, 0x75, 0x7D, 0x79, 0x61, 0x71,  # ADC
        0x29, 0x25, 0x2D, 0x35, 0x3D, 0x39, 0x21, 0x31,  # AND
        0x49, 0x45, 0x4D, 0x55, 0x5D, 0x59, 0x41, 0x51,  # EOR
        0x09, 0x05, 0x0D, 0x15, 0x1D, 0x19, 0x01, 0x11,  # ORA
        0xE9, 0xE5, 0xED, 0xF5, 0xFD, 0xF9, 0xE1, 0xF1,  # SBC
    ])

    work = bytearray(binary)
    n_lda_sta = 0
    n_copy_loops = 0
    # Track ZP values for indirect copy detection
    zp = bytearray(256)

    def _addr_to_off(addr):
        off = addr - load_addr
        return off if 0 <= off < len(work) else None

    def _ensure_range(addr, count):
        """Extend work buffer if addr+count is beyond current range."""
        nonlocal work
        end_needed = addr + count - load_addr
        if end_needed > len(work):
            work.extend(b'\x00' * (end_needed - len(work)))

    def _run(start_addr, max_inst=512, follow_jmp=True):
        nonlocal n_lda_sta, n_copy_loops
        pc = start_addr
        reg_a = None      # current A register value (None = unknown)
        for _ in range(max_inst):
            off = _addr_to_off(pc)
            if off is None:
                break
            op = work[off]

            if op == 0xA9 and off + 1 < len(work):
                # LDA #imm
                reg_a = work[off + 1]
                pc += 2

            elif op == 0x8D and off + 2 < len(work):
                # STA abs — write A to memory if A is known and address is in range.
                # Do NOT invalidate reg_a: one LDA #imm can feed multiple STA abs.
                dst_addr = work[off + 1] | (work[off + 2] << 8)
                if reg_a is not None:
                    dst_off = _addr_to_off(dst_addr)
                    if dst_off is not None:
                        work[dst_off] = reg_a
                        n_lda_sta += 1
                        if verbose:
                            print(f'  init patch: ${dst_addr:04X} = ${reg_a:02X}')
                pc += 3

            elif (op == 0xBD and off + 10 < len(work) and  # LDA abs,X  (3 bytes)
                  work[off + 3] == 0x9D and                 # STA abs,X  (3 bytes)
                  work[off + 6] == 0xE8 and                 # INX        (1 byte)
                  work[off + 7] == 0xE0 and                 # CPX #imm   (2 bytes)
                  work[off + 9] == 0xD0):                   # BNE rel    (2 bytes)
                # Copy-loop idiom: memcpy(dst, src, count)
                # Total = 3+3+1+2+2 = 11 bytes
                src_addr = work[off + 1] | (work[off + 2] << 8)
                dst_addr = work[off + 4] | (work[off + 5] << 8)
                count    = work[off + 8]
                src_off  = _addr_to_off(src_addr)
                dst_off  = _addr_to_off(dst_addr)
                if src_off is not None and dst_off is not None:
                    if src_off + count <= len(work) and dst_off + count <= len(work):
                        # Read all source bytes first to handle src/dst overlap
                        src_bytes = bytes(work[src_off:src_off + count])
                        work[dst_off:dst_off + count] = src_bytes
                        n_copy_loops += 1
                        if verbose:
                            print(f'  init copy: ${src_addr:04X} -> ${dst_addr:04X} '
                                  f'({count} bytes)')
                reg_a = None   # X register modified; conservatively invalidate A
                pc += 11

            elif op == 0x85 and off + 1 < len(work):
                # STA zp — track ZP writes for indirect copy detection
                zp_addr = work[off + 1]
                if reg_a is not None:
                    zp[zp_addr] = reg_a
                pc += 2

            elif (op == 0xB1 and off + 7 < len(work) and  # LDA (zp),Y
                  work[off + 2] == 0x91 and                 # STA (zp),Y
                  work[off + 4] == 0xC8 and                 # INY
                  work[off + 5] == 0xD0):                    # BNE (inner loop)
                # Indirect page copy: LDA ($FB),Y / STA ($FD),Y / INY / BNE
                # followed by INC src_hi / INC dst_hi / DEX / BNE (outer loop)
                src_zp = work[off + 1]
                dst_zp = work[off + 3]
                src_addr = zp[src_zp] | (zp[src_zp + 1] << 8)
                dst_addr = zp[dst_zp] | (zp[dst_zp + 1] << 8)
                # Find outer loop: scan forward for INC/INC/DEX/BNE or similar
                # Count pages from X register (look back for LDX #imm)
                num_pages = 1  # default
                # Search backwards for LDX #imm (A2 xx)
                for back in range(1, 20):
                    boff = off - back
                    if boff >= 0 and work[boff] == 0xA2:
                        num_pages = work[boff + 1]
                        break
                count = num_pages * 256
                src_off = _addr_to_off(src_addr)
                if src_off is not None and src_off + count <= len(work):
                    _ensure_range(dst_addr, count)
                    dst_off = _addr_to_off(dst_addr)
                    if dst_off is not None:
                        src_bytes = bytes(work[src_off:src_off + count])
                        work[dst_off:dst_off + count] = src_bytes
                        n_copy_loops += 1
                        if verbose:
                            print(f'  init copy (indirect): ${src_addr:04X} -> '
                                  f'${dst_addr:04X} ({count} bytes, {num_pages} pages)')
                # Skip past inner loop (7 bytes) + outer loop (~7 bytes)
                # Scan forward from inner BNE for outer BNE (0xD0)
                end_off = off + 6  # past inner BNE
                while end_off < off + 20 and end_off < len(work):
                    if work[end_off] == 0xD0:
                        end_off += 2  # past outer BNE + rel
                        break
                    end_off += _LEN[work[end_off]] or 1
                else:
                    end_off = off + 14
                pc = load_addr + end_off
                reg_a = None

            elif op == 0x4C and off + 2 < len(work):
                # JMP abs — follow (one extra level only)
                jmp_addr = work[off + 1] | (work[off + 2] << 8)
                if follow_jmp:
                    _run(jmp_addr, max_inst=256, follow_jmp=False)
                break

            elif op == 0x60:
                # RTS
                break

            else:
                # Any other instruction: advance PC by correct instruction length.
                # Invalidate A for any instruction that modifies it.
                if op in _A_MODIFYING:
                    reg_a = None
                pc += _LEN[op] or 1

    _run(init_addr)

    if verbose and (n_lda_sta > 0 or n_copy_loops > 0):
        print(f'Init simulation: {n_lda_sta} patches, {n_copy_loops} copy loops applied')

    return bytes(work)


def find_songs(binary, load_addr):
    """Find song table using SIDdecompiler pattern.

    Multi-song: LDA songs,X / STA currtrkhi,Y / INX / INY / CPY #N
    Pattern: BD ** ** 99 ** ** E8 C8 C0 NN
    N=6 for 3 voices, N=4 for 2 voices, N=8 for extended format.

    Single-song fallback: LDA currtrklo,X / STA zp / LDA currtrkhi,X / STA zp / DEC
    Pattern: BD ** ** 85 ** BD ** ** 85 ** DE

    Returns (songs_addr, is_multi, bytes_per_song, interleaved) or (None, False, 0, False).
    interleaved=True for double-INX variant where lo/hi are interleaved.
    """
    # Multi-song pattern — try CPY #6 (3 voices × 2 bytes) first,
    # then other values (CPY #4 for 2-voice songs like Human Race,
    # CPY #8 for songs with extra data per voice like BMX Kidz)
    for cpy_val in [0x06, 0x04, 0x08]:
        pat = f"BD****99****E8C8C0{cpy_val:02X}"
        pos = find_hex_pattern(binary, pat)
        if pos >= 0:
            songs_addr = binary[pos + 1] | (binary[pos + 2] << 8)
            return songs_addr, True, cpy_val, False

    # Variant: double LDA/STA + double INX (loads lo+hi pairs interleaved)
    # Pattern: BD ** ** 99 ** ** BD ** ** 99 ** ** E8 E8 C8 C0 NN
    # Here CPY #N counts voices (not bytes), and each voice = 2 bytes (stride 2 in X)
    for cpy_val in [0x06, 0x04, 0x08, 0x03]:
        pat = f"BD****99****BD****99****E8E8C8C0{cpy_val:02X}"
        pos = find_hex_pattern(binary, pat)
        if pos >= 0:
            songs_addr = binary[pos + 1] | (binary[pos + 2] << 8)
            # In this variant, CPY counts voice slots, bytes_per_song = cpy_val * 2
            return songs_addr, True, cpy_val * 2, True

    # Single-song fallback: LDA currtrklo,X / STA zp / LDA currtrkhi,X / STA zp / DEC
    # Pattern: BD ** ** 85 ** BD ** ** 85 ** DE
    pos = find_hex_pattern(binary, "BD****85**BD****85**DE")
    if pos >= 0:
        currtrklo = binary[pos + 1] | (binary[pos + 2] << 8)
        currtrkhi = binary[pos + 6] | (binary[pos + 7] << 8)
        diff = currtrkhi - currtrklo
        if diff == 3:
            return currtrklo, False, 6, False
        elif diff == 1:
            # Interleaved variant: lo/hi bytes alternate (lo0,hi0,lo1,hi1,lo2,hi2)
            return currtrklo, False, 6, True

    # Single-song: LDA lo,X / STA zp / LDA hi,X / STA zp+1 / CPX #$00
    # Ricochet/Skate variant: CPX ($E0) follows instead of DEC
    pos = find_hex_pattern(binary, "BD****85**BD****85**E0")
    if pos >= 0:
        zp1 = binary[pos + 4]
        zp2 = binary[pos + 9]
        if zp2 == zp1 + 1:
            currtrklo = binary[pos + 1] | (binary[pos + 2] << 8)
            currtrkhi = binary[pos + 6] | (binary[pos + 7] << 8)
            diff = currtrkhi - currtrklo
            if diff == 3:
                return currtrklo, False, 6, False
            elif diff == 1:
                return currtrklo, False, 6, True

    # Single-song: LDA lo,X / STA zp / LDA hi,X / STA zp+1 / LDA ... (no DEC after)
    # Chicken_Song variant: the track pointer load is followed by more LDAs,
    # not a DEC. Match on adjacent ZP addresses only.
    pos = find_hex_pattern(binary, "BD****85**BD****85**BD")
    if pos >= 0:
        zp1 = binary[pos + 4]
        zp2 = binary[pos + 9]
        if zp2 == zp1 + 1:
            currtrklo = binary[pos + 1] | (binary[pos + 2] << 8)
            currtrkhi = binary[pos + 6] | (binary[pos + 7] << 8)
            diff = currtrkhi - currtrklo
            if diff == 3:
                return currtrklo, False, 6, False
            elif diff == 1:
                return currtrklo, False, 6, True

    # Phase 3/4 fallback: ZP pointer setup
    # LDA table,X / STA $F0 / ... / LDA table2,X / STA $F1 / ...
    # Pattern: BD ** ** 85 F0 BD ** ** 85 F1
    # Track pointer tables for 3 voices at stride 7 (X=0/7/14)
    for f0_base in range(0xF0, 0xFA, 2):  # try $F0, $F2, $F4, ...
        pat = f"BD****85{f0_base:02X}BD****85{f0_base+1:02X}"
        pos = find_hex_pattern(binary, pat)
        if pos >= 0:
            trk_lo_table = binary[pos + 1] | (binary[pos + 2] << 8)
            trk_hi_table = binary[pos + 6] | (binary[pos + 7] << 8)
            # This is a per-voice pointer setup, not a song table.
            # Use trk_lo/hi tables directly. Each voice at stride 7.
            # Build a "virtual" song table from the pointer values.
            track_addrs = []
            for voice_x in [0, 7, 14]:
                lo_off = trk_lo_table - load_addr + voice_x
                hi_off = trk_hi_table - load_addr + voice_x
                if 0 <= lo_off < len(binary) and 0 <= hi_off < len(binary):
                    addr = binary[lo_off] | (binary[hi_off] << 8)
                    track_addrs.append(addr)
            if len(track_addrs) == 3 and any(load_addr <= a < load_addr + len(binary) for a in track_addrs):
                # Store the lo table address as "songs_addr" — it's the closest equivalent
                return trk_lo_table, False, 6, False

    return None, False, 0, False


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

    # X-indexed variant: LDA instr,X / STA $D402,X / LDA instr+1,X / STA $D403,X
    # Pattern: BD ** ** 9D 02 D4 BD ** ** 9D 03 D4
    pos = find_hex_pattern(binary, "BD****9D02D4BD****9D03D4")
    if pos >= 0:
        return binary[pos + 1] | (binary[pos + 2] << 8)

    # ADSR variant: LDA instr+3,X / STA $D405,Y / LDA instr+4,X / STA $D406,Y
    # Some Hubbard drivers write ADSR (D405/D406) adjacent but have PW writes
    # separated by conditional branches, so the D402/D403 pattern fails.
    # AD is at offset +3 in the standard 8-byte instrument record.
    pos = find_hex_pattern(binary, "BD****9905D4BD****9906D4")
    if pos >= 0:
        ad_addr = binary[pos + 1] | (binary[pos + 2] << 8)
        return ad_addr - 3

    # ASL*3 variant: instrument index multiplied by 8, then indexed into table.
    # Pattern: ASL ASL ASL TAX LDA abs,X = 0A 0A 0A AA BD ** **
    # Used by IK+ and Phantoms variants where SID writes go through a shadow
    # buffer, so there's no direct LDA instr,X / STA $D4xx pattern.
    # The first field accessed after ASL*3 TAX is typically the waveform
    # (ctrl) at offset +2 in the 8-byte instrument record.
    pos = find_hex_pattern(binary, "0A0A0AAABD****")
    if pos >= 0:
        field_addr = binary[pos + 5] | (binary[pos + 6] << 8)
        # Verify: the address should be within the SID binary
        if load_addr <= field_addr < load_addr + len(binary):
            return field_addr - 2

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

    Also handles double-nested counters where an outer DEC/BPL wraps the
    inner one. When the outer counter's BPL branches to the inner counter
    address and the outer resets with an immediate value <= 5, the two
    counters are combined: combined_speed = (inner_speed + outer_imm) // 2.

    Also searches for per-song speed tables in the init code:
        LDA songtempos,X / STA tempo

    Returns (default_speed, speed_table) where:
    - default_speed: the value at the tempo variable (0-based divider), or None
    - speed_table: list of per-song speeds if detected, or None
    Frames per tick = speed + 1.
    """
    tempo_addr = None
    default_speed = None
    inner_binary_offset = None   # binary offset of the inner counter DEC instruction

    # Find the speed counter reset pattern.
    # Variant 1 (preferred): DEC counter / BPL / LDA tempo_var / STA counter
    # Variant 2 (fallback): DEC counter / BPL / LDA #imm / STA counter
    #
    # Search for Variant 1 first (all occurrences). Only use Variant 2
    # if no Variant 1 found, because some songs have multiple DEC/BPL/LDA
    # patterns for different counters (filter speed, etc.) and the LDA abs
    # variant is more reliably the music speed counter.

    # Pass 1: LDA abs variant — DEC abs ($CE) or DEC zp ($C6)
    #
    # CE lo hi 10 rel AD lo hi 8D lo hi   (DEC abs / BPL / LDA abs / STA abs)
    # C6 zp    10 rel AD lo hi 85 zp      (DEC zp  / BPL / LDA abs / STA zp)
    for i in range(len(binary) - 9):
        if binary[i] == 0xCE and binary[i + 3] == 0x10:
            # DEC abs — counter is a 2-byte absolute address
            if i + 11 > len(binary):
                continue
            if binary[i + 5] != 0xAD or binary[i + 8] != 0x8D:
                continue
            counter_addr = binary[i + 1] | (binary[i + 2] << 8)
            t_addr = binary[i + 6] | (binary[i + 7] << 8)
            sta_addr = binary[i + 9] | (binary[i + 10] << 8)
            if sta_addr != counter_addr:
                continue
            off = t_addr - load_addr
            if 0 <= off < len(binary):
                val = binary[off]
                if val <= 15:
                    tempo_addr = t_addr
                    default_speed = val
                    inner_binary_offset = i
                    break
        elif binary[i] == 0xC6 and binary[i + 2] == 0x10:
            # DEC zp — counter is a 1-byte zero-page address
            if i + 9 > len(binary):
                continue
            if binary[i + 4] != 0xAD or binary[i + 7] != 0x85:
                continue
            counter_zp = binary[i + 1]
            t_addr = binary[i + 5] | (binary[i + 6] << 8)
            sta_zp = binary[i + 8]
            if sta_zp != counter_zp:
                continue
            off = t_addr - load_addr
            if 0 <= off < len(binary):
                val = binary[off]
                if val <= 15:
                    tempo_addr = t_addr
                    default_speed = val
                    inner_binary_offset = i
                    break

    # Pass 2: LDA #imm variant (only if Pass 1 found nothing)
    # CE lo hi 10 rel A9 imm 8D lo hi     (DEC abs / BPL / LDA #imm / STA abs)
    # C6 zp    10 rel A9 imm 85 zp        (DEC zp  / BPL / LDA #imm / STA zp)
    if default_speed is None:
        for i in range(len(binary) - 8):
            if binary[i] == 0xCE and binary[i + 3] == 0x10 and binary[i + 5] == 0xA9:
                counter_addr = binary[i + 1] | (binary[i + 2] << 8)
                val = binary[i + 6]
                sta_off = i + 7
                if (sta_off + 2 < len(binary) and binary[sta_off] == 0x8D and
                        (binary[sta_off + 1] | (binary[sta_off + 2] << 8)) == counter_addr):
                    if val <= 15:
                        tempo_addr = counter_addr
                        default_speed = val
                        inner_binary_offset = i
                        break
            elif binary[i] == 0xC6 and binary[i + 2] == 0x10 and binary[i + 4] == 0xA9:
                counter_zp = binary[i + 1]
                val = binary[i + 5]
                sta_off = i + 6
                if (sta_off + 1 < len(binary) and binary[sta_off] == 0x85 and
                        binary[sta_off + 1] == counter_zp):
                    if val <= 15:
                        tempo_addr = counter_zp   # zp address used as tempo_addr key
                        default_speed = val
                        inner_binary_offset = i
                        break

    # Pass 3: Outer counter detection (nested double-counter).
    #
    # Some Hubbard songs use two nested speed counters:
    #   outer: DEC outer_ctr / BPL -> inner / LDA #imm / STA outer_ctr / JMP past_inner
    #   inner: DEC inner_ctr / BPL -> post / LDA tempo_var / STA inner_ctr  <- music fires
    #
    # When the outer counter expires it resets and jumps PAST the inner counter,
    # skipping music updates periodically. This makes the effective tick rate
    # approximately (inner_speed + outer_imm) / 2 frames per tick.
    #
    # We detect this when:
    #   1. An inner counter was found by Pass 1 (LDA abs variant)
    #   2. A DEC abs / BPL pattern exists whose BPL branches forward to the inner
    #      counter's exact address
    #   3. The outer counter resets with LDA #imm / STA outer_ctr (imm <= 5,
    #      keeping the correction conservative to avoid touching large-divider
    #      counters used for vibrato/filter effects)
    if inner_binary_offset is not None:
        inner_abs_addr = load_addr + inner_binary_offset
        for i in range(len(binary) - 12):
            if binary[i] != 0xCE:
                continue
            # DEC abs (3 bytes) / BPL rel (2 bytes) => offset 3 = 0x10
            if binary[i + 3] != 0x10:
                continue
            outer_counter_addr = binary[i + 1] | (binary[i + 2] << 8)
            bpl_rel = binary[i + 4]
            bpl_offset = bpl_rel if bpl_rel < 128 else bpl_rel - 256
            bpl_target = (load_addr + i + 5) + bpl_offset
            if bpl_target != inner_abs_addr:
                continue
            # BPL branches exactly to the inner counter. Check reset: LDA #imm / STA outer_ctr
            j = i + 5   # byte after BPL operand
            if j + 4 >= len(binary):
                continue
            if binary[j] != 0xA9:   # LDA #imm
                continue
            outer_imm = binary[j + 1]
            if binary[j + 2] != 0x8D:   # STA abs
                continue
            sta_outer = binary[j + 3] | (binary[j + 4] << 8)
            if sta_outer != outer_counter_addr:
                continue
            # Outer counter found. Only apply when imm <= 5 (tempo range).
            if outer_imm <= 5:
                default_speed = (default_speed + outer_imm) // 2
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
    """Find frequency table by known PAL freq byte sequences.

    Searches for two formats:
    1. Separated lo/hi tables: lo-bytes then hi-bytes (standard GT2 layout)
    2. Interleaved lo/hi pairs: lo0,hi0,lo1,hi1,... (Hubbard driver format)

    For interleaved tables found via the ascending-sequence scan, the result
    is only marked as a CUSTOM (interleaved) table when average deviation from
    standard PAL exceeds 5%. This prevents near-PAL tables from accidentally
    being applied as custom freq tables.

    Returns (addr, is_interleaved) where:
    - addr: absolute address of the table start, or None if not found
    - is_interleaved: True only when interleaved format AND >5% deviation from PAL
    """
    # Standard PAL freq table lo bytes (C-1 through B-1 = octave 1)
    PAL_LO = bytes([0x17, 0x27, 0x39, 0x4b, 0x5f, 0x74, 0x8a, 0xa1, 0xba, 0xd4, 0xf0, 0x0e])

    # Try full 12-byte match first, then shorter (separated lo+hi format)
    for window in range(12, 5, -1):
        pos = binary.find(PAL_LO[:window])
        if pos >= 0:
            return load_addr + pos, False

    # Also try searching for the hi bytes: 01 01 01 01 01 01 01 01 01 01 01 02
    PAL_HI = bytes([0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x02])
    pos = binary.find(PAL_HI)
    if pos >= 0:
        # Lo table is likely 96 bytes before (8 octaves * 12 notes)
        return load_addr + pos - 96, False

    # Try interleaved format: lo0,hi0,lo1,hi1,...
    # Search for ascending 16-bit pairs with semitone ratio ~1.059 (±10%).
    # Require a run of at least 12 consecutive pairs (one full octave) to
    # avoid matching short ascending sequences in player code.
    best_pos = -1
    best_len = 0
    i = 0
    while i < len(binary) - 8:
        v = binary[i] | (binary[i + 1] << 8)
        if 0x0100 < v < 0xE000:
            run_len = 1
            j = i + 2
            while j + 1 < len(binary):
                vnext = binary[j] | (binary[j + 1] << 8)
                if v > 0 and 1.03 < vnext / v < 1.15:
                    run_len += 1
                    v = vnext
                    j += 2
                else:
                    break
            if run_len > best_len:
                best_len = run_len
                best_pos = i
        i += 1

    if best_len >= 12 and best_pos >= 0:
        # Compute average absolute deviation from PAL standard table.
        try:
            from gt_parser import FREQ_TBL_LO, FREQ_TBL_HI
        except ImportError:
            return None, False

        num_entries = min(best_len, 96)
        total_dev = 0.0
        count = 0
        for n in range(num_entries):
            b = best_pos + n * 2
            if b + 1 >= len(binary):
                break
            actual = binary[b] | (binary[b + 1] << 8)
            pal = FREQ_TBL_LO[n] | (FREQ_TBL_HI[n] << 8)
            if pal > 0:
                total_dev += abs(actual - pal) / pal
                count += 1

        avg_dev = total_dev / count if count > 0 else 0.0

        # Only treat as a genuinely CUSTOM table when deviation exceeds 5%.
        # The standard Hubbard freq table differs from PAL by ~0.1% (±1 in
        # a few entries). A >5% threshold ensures only truly different tuning
        # systems get a custom table override.
        if avg_dev > 0.05:
            return load_addr + best_pos, True
        # Near-PAL table found — not custom, do NOT expose the address
        # (exposing it would break freq-table-trick note resolution for songs
        # that rely on _ft_addr being None to emit high-pitch notes as TIEs).
        return None, False

    return None, False


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


def decode_track(binary, load_addr, track_addr, num_sequences=256, max_bytes=512):
    """Decode a Hubbard track = sequence of pattern indices with RST markers.

    Track data bytes:
    - $FF = RST restart-point marker OR loop terminator.
      If followed by a valid pattern index (< num_sequences), it's RST:
      skip both bytes (marker + restart offset) and continue.
      Otherwise it's the loop point (end of track).
    - $FE = stop (end of track)
    - 0 to num_sequences-1 = pattern index
    - bytes >= num_sequences but < $FE = RST marker (set restart point).
      Some variants consume 2 bytes (marker + restart index).
    """
    patterns = []
    off = track_addr - load_addr
    i = 0
    while i < max_bytes:
        if off + i >= len(binary):
            break
        b = binary[off + i]
        if b == 0xFF:
            # $FF + restart_position = loop end.  The Hubbard driver always
            # treats this as "jump back to position restart_position in the
            # track".  There is no separate RST/continue concept.
            restart_pos = binary[off + i + 1] if off + i + 1 < len(binary) else 0
            patterns.append(('loop', restart_pos))
            break
        elif b == 0xFE:
            # $FE = stop (track ends, no loop)
            patterns.append(('stop', None))
            break
        elif b >= num_sequences:
            # Byte exceeds valid pattern range — skip it.
            # Some variants use 2-byte markers (marker + index).
            i += 1
            if off + i < len(binary) and binary[off + i] < num_sequences:
                i += 1
        else:
            patterns.append(('pattern', b))
            i += 1
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

    # --- Simulate init routine to pre-apply self-modifying code ---
    # Some Hubbard SIDs patch player addresses and copy data blocks in init.
    # Apply those writes to a working copy before pattern-matching data structures.
    binary = simulate_init(binary, load_addr, result.init_addr, verbose=verbose)

    # --- Find data structures via pattern matching ---

    # Song table
    songs_addr, is_multi, bytes_per_song, interleaved = find_songs(binary, load_addr)
    if songs_addr is None:
        print('ERROR: Could not find song table pattern', file=sys.stderr)
        return None
    result.song_table_addr = songs_addr
    num_voices = bytes_per_song // 2  # each voice = 2 bytes (lo + hi pointer)
    if verbose:
        layout = 'interleaved' if interleaved else 'split'
        print(f'Song table at ${songs_addr:04X} ({"multi" if is_multi else "single"}, {num_voices} voices, {bytes_per_song} bytes/song, {layout})')

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
    seq_interleaved = (seqhi == seqlo + 1)
    result.seq_interleaved = seq_interleaved
    if seq_interleaved:
        # Interleaved: (lo, hi, lo, hi, ...) at seqlo
        # Count valid entries until address goes out of range
        n = 0
        while True:
            lo_off = seqlo - load_addr + n * 2
            hi_off = lo_off + 1
            if lo_off + 1 >= len(binary):
                break
            addr = binary[lo_off] | (binary[hi_off] << 8)
            if not (load_addr <= addr < load_addr + len(binary)):
                break
            n += 1
            if n > 255:
                break
        result.num_sequences = n
    else:
        result.num_sequences = seqhi - seqlo
    if verbose:
        layout = 'interleaved' if seq_interleaved else 'split'
        print(f'Sequence pointers: lo=${seqlo:04X} hi=${seqhi:04X} ({result.num_sequences} sequences, {layout})')

    # Freq table (optional — not all songs use standard PAL table)
    freq_addr, freq_interleaved = find_freq_table(binary, load_addr)
    result.freq_table_addr = freq_addr
    result.freq_table_interleaved = freq_interleaved
    if verbose:
        if freq_addr:
            fmt = 'interleaved (custom, >5% from PAL)' if freq_interleaved else 'standard PAL'
            print(f'Freq table at ${freq_addr:04X} ({fmt})')
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

    # Arpeggio driver variant detection.
    # In the classic (Phase 2) driver: arp bit (bit 2 of fx_flags) only fires
    # when the drum code path has set the arp counter non-zero. Arpeggio-only
    # instruments (no drum bit) produce a steady note.
    #
    # In the Phase 4 driver (Las_Vegas, Kentilla): the arpeggio code extracts
    # the upper nibble of fx_flags via 4x LSR and uses it as the interval:
    #   AND #$04  →  LDA <fx_flags>  →  LSR LSR LSR LSR  →  STA <interval>
    # Arpeggio-only instruments with upper nibble > 0 produce real alternation.
    #
    # Detection: search for AND #$04 followed within ~15 bytes by at least 4 LSR ops.
    result.upper_nibble_arp = False
    _and4 = bytes([0x29, 0x04])
    _search = 0
    while True:
        _p = binary.find(_and4, _search)
        if _p < 0:
            break
        _region = binary[_p:_p + 30]
        if sum(1 for b in _region[2:17] if b == 0x4A) >= 4:
            result.upper_nibble_arp = True
            break
        _search = _p + 1

    if verbose:
        _arp_desc = 'upper-nibble interval (Phase 4)' if result.upper_nibble_arp else 'counter-based (Phase 2 classic)'
        print(f'Arpeggio driver: {_arp_desc}')
        print()

    # Per-voice transpose detection.
    # Many Hubbard players apply a per-voice semitone offset to the raw pattern
    # pitch byte before looking up the freq table:
    #   LDA pattern_byte → AND #$7F → CLC → ADC transpose_table,X → ASL → TAY → LDA freq,Y
    # The transpose_table (indexed by voice X=0,1,2) shifts the note up by N semitones.
    # Detection: find the pattern ASL (0x0A) + TAY (0xA8) + LDA abs,Y (0xB9 xx xx)
    # then scan backwards ~25 bytes for ADC abs,X (0x7D xx xx).
    result.voice_transpose = [0, 0, 0]
    _asl_tay_lda = bytes([0x0A, 0xA8, 0xB9])
    _search = 0
    while True:
        _p = binary.find(_asl_tay_lda, _search)
        if _p < 0:
            break
        # Check that the LDA abs,Y target is within the binary (freq table reference)
        if _p + 4 < len(binary):
            _ft_addr = binary[_p + 3] | (binary[_p + 4] << 8)
            if load_addr <= _ft_addr < load_addr + len(binary):
                # Scan backward for ADC abs,X (0x7D)
                for _j in range(max(0, _p - 25), _p):
                    if binary[_j] == 0x7D and _j + 2 < len(binary):
                        _tt_lo = binary[_j + 1]
                        _tt_hi = binary[_j + 2]
                        _tt_addr = (_tt_hi << 8) | _tt_lo
                        _tt_off = _tt_addr - load_addr
                        # Validate: the transpose table must be in-range
                        # and contain reasonable semitone offsets (0-47 or 0xFF for -1)
                        if 0 <= _tt_off + 5 < len(binary):
                            _transpositions = [binary[_tt_off + k] for k in range(3)]
                            # Sanity: each value should be a small positive semitone offset
                            # (0-47) or 0xFF/-1 for one-down. Values 128+ are likely
                            # octave flags, not semitone offsets.
                            # Accept if at least one voice has 1-47 transpose.
                            if any(1 <= v <= 47 for v in _transpositions):
                                result.voice_transpose = _transpositions
                                if verbose:
                                    print(f'Per-voice transpose: V1={_transpositions[0]} V2={_transpositions[1]} V3={_transpositions[2]} (table@0x{_tt_addr:04X})')
                                break
            if result.voice_transpose != [0, 0, 0]:
                break
        _search = _p + 1

    # --- Drum freq_slide detection ---
    # Find the freq_hi buffer (source of STA $D401,Y) and check for DEC
    result.drum_freq_slide = 0
    if any(inst.has_drum for inst in result.instruments):
        freq_hi_buf = None
        for i in range(len(binary) - 5):
            if binary[i] == 0x99 and binary[i+1] == 0x01 and binary[i+2] == 0xD4:
                for j in range(i-1, max(i-10, 0), -1):
                    if binary[j] == 0xBD:
                        freq_hi_buf = binary[j+1] | (binary[j+2] << 8)
                        break
                if freq_hi_buf:
                    break
        if freq_hi_buf:
            for i in range(len(binary) - 2):
                if binary[i] == 0xDE and binary[i+1] == (freq_hi_buf & 0xFF) and binary[i+2] == (freq_hi_buf >> 8):
                    result.drum_freq_slide = -1
                    if verbose:
                        print(f'Drum descent: DEC ${freq_hi_buf:04X},X (freq_slide=-1)')
                    break

    # --- Parse songs ---
    for s in range(result.num_songs):
        if is_multi:
            off = songs_addr - load_addr + s * bytes_per_song
            if off + bytes_per_song > len(binary):
                break
            if interleaved:
                # Double-INX layout: (lo, hi, lo, hi, ...) interleaved
                track_addrs = []
                for j in range(num_voices):
                    lo_byte = binary[off + j * 2] if off + j * 2 < len(binary) else 0
                    hi_byte = binary[off + j * 2 + 1] if off + j * 2 + 1 < len(binary) else 0
                    track_addrs.append(lo_byte | (hi_byte << 8))
            else:
                # Split layout: [lo0, lo1, lo2, hi0, hi1, hi2]
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
                tracks.append(decode_track(binary, load_addr, track_addrs[v],
                                          num_sequences=result.num_sequences))

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
        if seq_interleaved:
            pat_lo = peek(binary, load_addr, seqlo + idx * 2)
            pat_hi = peek(binary, load_addr, seqlo + idx * 2 + 1)
        else:
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
