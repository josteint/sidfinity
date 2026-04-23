"""
holy_grail_pack.py -- Holy Grail packer for SIDfinity.

Generates a minimal 6502 player + data directly from ground truth register
traces, bypassing the GT2 packer entirely. No freq table encoding, no XOR
transforms, no FIRSTNOTE offsets -- just direct SID register values.

Architecture:
  - Per voice: note stream (length, inst_lo, inst_hi per note, then $FF)
  - Instrument pool: frame sequences of 7 bytes each (all voice regs)
  - Filter data: flat stream of 4 bytes per frame
  - Player: pointer-advancing, 7 bytes per frame from instrument data

Usage:
    from ground_truth import capture_sid
    from holy_grail_pack import holy_grail_pack
    t = capture_sid('song.sid', subtunes=[1]).subtunes[0]
    holy_grail_pack(t, 'song.sid', '/tmp/out.sid')
"""

import os
import struct
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get('SIDFINITY_ROOT', os.path.join(SCRIPT_DIR, '..')).strip()
XA65 = os.path.join(REPO_ROOT, 'tools', 'xa65', 'xa', 'xa')

# SID register layout per voice (7 bytes)
# [0]=freq_lo [1]=freq_hi [2]=pw_lo [3]=pw_hi [4]=ctrl [5]=ad [6]=sr
VOICE_OFFSETS = [0, 7, 14]
FILTER_OFFSET = 21
VOICE_BASES = [0xD400, 0xD407, 0xD40E]

# Zero-page layout per voice (8 bytes each)
# np_lo, np_hi = note stream pointer
# fc = frame counter within note (0-based)
# nl = note length (frames)
# ip_lo, ip_hi = instrument base pointer (points to length byte)
# rp_lo, rp_hi = read pointer within instrument data (advances 7/frame)
ZP_VOICE = [
    (0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87),
    (0x88, 0x89, 0x8A, 0x8B, 0x8C, 0x8D, 0x8E, 0x8F),
    (0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97),
]
# Filter ZP: $A0/$A1 = frame pointer, $A2/$A3 = frame counter (16-bit)

PLAYER_BASE = 0x1000


# ---------------------------------------------------------------------------
# Instrument pool
# ---------------------------------------------------------------------------

class InstrumentPool:
    """Deduplication pool for instrument frame sequences.

    Two notes with identical (freq_lo, freq_hi, pw_lo, pw_hi, ctrl, ad, sr)
    frame sequences share one instrument entry.
    Also handles prefix sharing: if note A is a prefix of note B, A reuses B's
    entry (B's data has enough frames to serve A's shorter length).
    """

    def __init__(self):
        self._seqs = []        # list of tuple-of-tuples
        self._by_key = {}      # tuple -> index

    def add(self, frames):
        """Add a frame sequence, return (index, actual_length).

        frames: list of 7-tuples
        Returns (inst_idx, n_frames_to_play)
        """
        key = tuple(frames)
        if key in self._by_key:
            return self._by_key[key], len(frames)

        n = len(frames)
        # Check if frames is a prefix of an existing sequence
        for idx, seq in enumerate(self._seqs):
            if len(seq) >= n and seq[:n] == key:
                self._by_key[key] = idx
                return idx, n
            # Check if existing is a prefix of frames
            slen = len(seq)
            if slen < n and key[:slen] == seq:
                # Extend existing sequence with our longer version
                self._seqs[idx] = key
                self._by_key[key] = idx
                return idx, n

        idx = len(self._seqs)
        self._seqs.append(key)
        self._by_key[key] = idx
        return idx, n

    def get_frames(self, idx):
        return self._seqs[idx]

    def __len__(self):
        return len(self._seqs)


# ---------------------------------------------------------------------------
# Note boundary detection
# ---------------------------------------------------------------------------

def detect_note_boundaries(voice_regs):
    """Detect note starts by gate-on (ctrl bit 0) transitions.

    voice_regs: list of 7-tuples (one per frame)
    Returns list of (start_frame, end_frame) tuples.
    """
    boundaries = []
    n = len(voice_regs)
    note_start = 0
    for i in range(1, n):
        prev_ctrl = voice_regs[i - 1][4]
        curr_ctrl = voice_regs[i][4]
        if (curr_ctrl & 1) and not (prev_ctrl & 1):
            boundaries.append((note_start, i))
            note_start = i
    boundaries.append((note_start, n))
    return boundaries


# ---------------------------------------------------------------------------
# Data encoding
# ---------------------------------------------------------------------------

def encode_instrument(frames):
    """Encode one instrument: [length_byte, 7_regs * length]"""
    data = bytearray()
    n = len(frames)
    data.append(min(n, 255))
    for frame in frames[:255]:
        for b in frame:
            data.append(b)
    return data


def build_voice_data(voice_regs):
    """Extract note sequence and instrument pool for one voice.

    Returns (note_sequence, pool) where note_sequence is list of
    (inst_idx, length) tuples.
    """
    pool = InstrumentPool()
    boundaries = detect_note_boundaries(voice_regs)
    note_sequence = []
    for start, end in boundaries:
        frames = voice_regs[start:end]
        if not frames:
            continue
        idx, length = pool.add(frames)
        note_sequence.append((idx, min(length, 255)))
    return note_sequence, pool


# ---------------------------------------------------------------------------
# Player code generation
# ---------------------------------------------------------------------------

def generate_player_asm():
    """Generate the holy grail player in xa65 assembly.

    Player layout at $1000:
      jmp init
      jmp play
    """
    lines = []
    L = lines.append

    L(f"        * = ${PLAYER_BASE:04X}")
    L("        jmp init")
    L("        jmp play")
    L("")

    # --- init ---
    L("init")
    L("        lda #$0F")
    L("        sta $D418")
    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi = ZP_VOICE[vi]
        L(f"        lda #<ns{vi + 1}")
        L(f"        sta ${np_lo:02X}")
        L(f"        lda #>ns{vi + 1}")
        L(f"        sta ${np_hi:02X}")
        L(f"        lda #0")
        L(f"        sta ${nl:02X}")
        L(f"        sta ${fc:02X}")
    L("        lda #<filtdata")
    L("        sta $A0")
    L("        lda #>filtdata")
    L("        sta $A1")
    L("        lda #0")
    L("        sta $A2")
    L("        sta $A3")
    L("        rts")
    L("")

    # --- play ---
    L("play")
    for vi in range(3):
        L(f"        jsr vplay{vi + 1}")
    L("        jmp fplay")
    L("")

    # --- per-voice player ---
    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi = ZP_VOICE[vi]
        vbase = VOICE_BASES[vi]
        vn = f"v{vi + 1}"

        L(f"; Voice {vi + 1}")
        L(f"vplay{vi + 1}")
        # If fc >= nl, load next note
        L(f"        lda ${fc:02X}")
        L(f"        cmp ${nl:02X}")
        L(f"        bcc {vn}play")
        L(f"        jmp {vn}load")

        # Play frame: read 7 bytes from rp, write ctrl first for hard restart timing
        L(f"{vn}play")
        L(f"        ldy #4")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 4:04X}")
        L(f"        ldy #0")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 0:04X}")
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 1:04X}")
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 2:04X}")
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 3:04X}")
        L(f"        ldy #5")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 5:04X}")
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 6:04X}")
        # Advance rp by 7
        L(f"        clc")
        L(f"        lda ${rp_lo:02X}")
        L(f"        adc #7")
        L(f"        sta ${rp_lo:02X}")
        L(f"        bcc {vn}nc1")
        L(f"        inc ${rp_hi:02X}")
        L(f"{vn}nc1")
        L(f"        inc ${fc:02X}")
        L(f"        rts")
        L("")

        # Load next note from note stream
        L(f"{vn}load")
        L(f"        ldy #0")
        L(f"        lda (${np_lo:02X}),y")
        L(f"        cmp #$FF")
        L(f"        bne {vn}ln0")
        # End of note stream -- silence and return
        L(f"        lda #0")
        L(f"        sta ${vbase + 4:04X}")
        L(f"        rts")
        L(f"{vn}ln0")
        # First byte = length, second = inst_lo, third = inst_hi
        L(f"        sta ${nl:02X}")
        L(f"        iny")
        L(f"        lda (${np_lo:02X}),y")
        L(f"        sta ${ip_lo:02X}")
        L(f"        iny")
        L(f"        lda (${np_lo:02X}),y")
        L(f"        sta ${ip_hi:02X}")
        # Advance np by 3
        L(f"        clc")
        L(f"        lda ${np_lo:02X}")
        L(f"        adc #3")
        L(f"        sta ${np_lo:02X}")
        L(f"        bcc {vn}nnc")
        L(f"        inc ${np_hi:02X}")
        L(f"{vn}nnc")
        # Reset fc
        L(f"        lda #0")
        L(f"        sta ${fc:02X}")
        # Set rp = ip + 1 (skip length byte)
        L(f"        clc")
        L(f"        lda ${ip_lo:02X}")
        L(f"        adc #1")
        L(f"        sta ${rp_lo:02X}")
        L(f"        lda ${ip_hi:02X}")
        L(f"        adc #0")
        L(f"        sta ${rp_hi:02X}")
        # Play first frame immediately
        L(f"        jmp {vn}play")
        L("")

    # --- filter player ---
    L("fplay")
    # $A3 counts completed 256-block passes, $A2 = frame within block
    # We run filtdata as a flat stream of 4 bytes/frame
    # Use $A2/$A3 as a 16-bit done counter compared against filtlen
    L("        lda $A3")
    L("        cmp #>filtlen")
    L("        bcc fpgo")
    L("        beq fpeq")
    L("        rts")
    L("fpeq")
    L("        lda $A2")
    L("        cmp #<filtlen")
    L("        bcs fpdone")
    L("fpgo")
    L("        ldy #0")
    L("        lda ($A0),y")
    L("        sta $D415")
    L("        iny")
    L("        lda ($A0),y")
    L("        sta $D416")
    L("        iny")
    L("        lda ($A0),y")
    L("        sta $D417")
    L("        iny")
    L("        lda ($A0),y")
    L("        sta $D418")
    L("        clc")
    L("        lda $A0")
    L("        adc #4")
    L("        sta $A0")
    L("        bcc fpnc")
    L("        inc $A1")
    L("fpnc")
    L("        inc $A2")
    L("        bne fpdone")
    L("        inc $A3")
    L("fpdone")
    L("        rts")
    L("")

    return lines


def measure_player_size():
    """Assemble player with stub data to measure code size."""
    asm_lines = generate_player_asm()
    # Add minimal stubs so assembler resolves all labels
    asm_lines.append("filtlen = 0")
    for vi in range(3):
        asm_lines.append(f"ns{vi + 1}  .byte $FF")
    asm_lines.append("filtdata  .byte $00,$00,$00,$0F")

    src = "\n".join(asm_lines)
    with tempfile.NamedTemporaryFile(suffix='.s', mode='w', delete=False) as f:
        f.write(src)
        src_path = f.name
    bin_path = src_path.replace('.s', '.bin')
    try:
        r = subprocess.run([XA65, '-o', bin_path, src_path],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"Probe assembly failed:\n{r.stderr}")
        size = os.path.getsize(bin_path)
        # Subtract stub data: 3 x 1 byte ($FF) + 4 bytes filter + filtlen sym (0)
        stub_bytes = 3 + 4
        return size - stub_bytes
    finally:
        os.unlink(src_path)
        if os.path.exists(bin_path):
            os.unlink(bin_path)


# ---------------------------------------------------------------------------
# Assembly generation
# ---------------------------------------------------------------------------

def bytes_to_asm(data, indent="        "):
    """Convert bytes to xa65 .byte lines."""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        lines.append(indent + ".byte " + ",".join(f"${b:02X}" for b in chunk))
    return lines


def generate_full_asm(trace):
    """Generate complete xa65 assembly from a SubtuneTrace.

    Returns (asm_source_str, stats_dict).
    """
    # Extract per-voice 7-tuples
    v_regs = []
    for vi in range(3):
        voff = VOICE_OFFSETS[vi]
        regs = [tuple(f[voff:voff + 7]) for f in trace.frames]
        v_regs.append(regs)

    # Extract filter frames (4 bytes each)
    filter_frames = [tuple(f[FILTER_OFFSET:FILTER_OFFSET + 4]) for f in trace.frames]

    # Build per-voice note sequences and instrument pools
    voice_seqs = []
    voice_pools = []
    for vi in range(3):
        seq, pool = build_voice_data(v_regs[vi])
        voice_seqs.append(seq)
        voice_pools.append(pool)

    # Measure player code size
    player_size = measure_player_size()
    inst_base = PLAYER_BASE + player_size

    # Encode all instruments for each voice
    inst_data_list = []
    inst_abs_offsets_list = []
    running = inst_base
    for vi in range(3):
        pool = voice_pools[vi]
        data = bytearray()
        offsets = []
        for idx in range(len(pool)):
            offsets.append(running + len(data))
            frames = list(pool.get_frames(idx))
            enc = encode_instrument(frames)
            data.extend(enc)
        inst_data_list.append(data)
        inst_abs_offsets_list.append(offsets)
        running += len(data)

    # Build note streams
    note_stream_data = []
    note_stream_addrs = []
    for vi in range(3):
        addr = running
        note_stream_addrs.append(addr)
        enc = bytearray()
        for inst_idx, length in voice_seqs[vi]:
            inst_addr = inst_abs_offsets_list[vi][inst_idx]
            enc.append(length & 0xFF)
            enc.append(inst_addr & 0xFF)
            enc.append((inst_addr >> 8) & 0xFF)
        enc.append(0xFF)
        note_stream_data.append(enc)
        running += len(enc)

    # Flat filter data
    filter_data = bytearray()
    for fr in filter_frames:
        for b in fr:
            filter_data.append(b)
    filter_addr = running
    total_size = running + len(filter_data) - PLAYER_BASE

    stats = {
        'player_size': player_size,
        'inst_sizes': [len(d) for d in inst_data_list],
        'note_sizes': [len(d) for d in note_stream_data],
        'filter_size': len(filter_data),
        'total_size': total_size,
        'n_instruments': [len(p) for p in voice_pools],
        'n_notes': [len(s) for s in voice_seqs],
        'end_addr': running + len(filter_data),
    }

    # Assemble the source
    asm_lines = generate_player_asm()

    # filtlen = number of filter frames (used by fplay comparison)
    n_filter_frames = len(filter_frames)
    asm_lines.append(f"filtlen = {n_filter_frames}")
    asm_lines.append("")

    for vi in range(3):
        asm_lines.append(f"; Voice {vi + 1} instruments "
                         f"({len(inst_data_list[vi])} bytes, "
                         f"{len(voice_pools[vi])} unique)")
        asm_lines.extend(bytes_to_asm(inst_data_list[vi]))
        asm_lines.append("")

    asm_lines.append("; Note streams")
    for vi in range(3):
        asm_lines.append(f"ns{vi + 1}")
        asm_lines.extend(bytes_to_asm(note_stream_data[vi]))
        asm_lines.append("")

    asm_lines.append("; Filter data")
    asm_lines.append("filtdata")
    asm_lines.extend(bytes_to_asm(filter_data))
    asm_lines.append("")

    return "\n".join(asm_lines), stats


# ---------------------------------------------------------------------------
# PSID header
# ---------------------------------------------------------------------------

def build_psid_header(orig_sid_path, load_addr, init_addr, play_addr):
    """Build a 124-byte PSID v2 header, copying metadata from original."""
    with open(orig_sid_path, 'rb') as f:
        orig = f.read()

    # Parse original header for metadata
    orig_header_len = struct.unpack('>H', orig[6:8])[0]
    title = orig[22:54].rstrip(b'\x00')
    author = orig[54:86].rstrip(b'\x00')
    copyright_ = orig[86:118].rstrip(b'\x00')
    flags = struct.unpack('>H', orig[118:120])[0] if orig_header_len >= 120 else 0x0014

    hdr = bytearray(124)
    hdr[0:4] = b'PSID'
    struct.pack_into('>H', hdr, 4, 2)       # version
    struct.pack_into('>H', hdr, 6, 124)     # header length
    struct.pack_into('>H', hdr, 8, 0)       # load_addr=0 (stored in binary)
    struct.pack_into('>H', hdr, 10, init_addr)
    struct.pack_into('>H', hdr, 12, play_addr)
    struct.pack_into('>H', hdr, 14, 1)      # n_songs
    struct.pack_into('>H', hdr, 16, 1)      # start_song
    struct.pack_into('>I', hdr, 18, 0)      # speed flags

    # Copy metadata
    hdr[22:54] = (title + b'\x00' * 32)[:32]
    hdr[54:86] = (author + b'\x00' * 32)[:32]
    hdr[86:118] = (copyright_ + b'\x00' * 32)[:32]
    struct.pack_into('>H', hdr, 118, flags)
    # start_page, page_length (v2 NG fields at 120-121, 122-123 if present)
    # Leave as 0 (reloc info not needed for fixed-address player)

    return bytes(hdr)


# ---------------------------------------------------------------------------
# Verification via py65
# ---------------------------------------------------------------------------

def verify_against_trace(output_sid_path, trace, max_frames=200, progress=False):
    """Verify rebuilt SID register output against ground truth trace.

    Returns (match_count, total_frames, mismatch_details).
    """
    sys.path.insert(0, os.path.join(REPO_ROOT, 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU

    # Load rebuilt SID
    with open(output_sid_path, 'rb') as f:
        data = f.read()

    magic = data[:4]
    if magic not in (b'PSID', b'RSID'):
        raise ValueError(f"Not a SID file")

    header_len = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]

    code = data[header_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        binary = code[2:]
    else:
        binary = code

    mem = bytearray(65536)
    end = min(load_addr + len(binary), 65536)
    mem[load_addr:end] = binary[:end - load_addr]
    mem[0xFFF0] = 0x00  # BRK sentinel

    mpu = MPU()
    mpu.memory = mem

    # Run init (subtune 0)
    mpu.stPush(0xFF)
    mpu.stPush(0xEF)
    mpu.pc = init_addr
    mpu.a = 0
    for _ in range(100000):
        if mpu.memory[mpu.pc] == 0x00:
            break
        mpu.step()

    n_frames = min(max_frames, trace.n_frames)
    match_count = 0
    mismatches = []
    ret_addr = 0xFFF0 - 1

    for frame in range(n_frames):
        mpu.stPush(ret_addr >> 8)
        mpu.stPush(ret_addr & 0xFF)
        mpu.pc = play_addr
        for _ in range(50000):
            if mpu.memory[mpu.pc] == 0x00:
                break
            mpu.step()

        got = tuple(mpu.memory[0xD400 + i] for i in range(25))
        expected = trace.frames[frame]

        if got == expected:
            match_count += 1
        else:
            diffs = []
            for i in range(25):
                if got[i] != expected[i]:
                    diffs.append((i, expected[i], got[i]))
            mismatches.append((frame, diffs))
            if progress and len(mismatches) <= 5:
                reg_names = []
                for vi in range(3):
                    for r in ('FL', 'FH', 'PL', 'PH', 'CT', 'AD', 'SR'):
                        reg_names.append(f'V{vi+1}_{r}')
                for ri in range(4):
                    reg_names.append(f'FLT{ri}')
                diff_str = ', '.join(
                    f'{reg_names[i]}={expected[i]:02X}->{got[i]:02X}'
                    for i, e, g in diffs
                )
                print(f"  Frame {frame:4d}: {diff_str}")

    return match_count, n_frames, mismatches


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def holy_grail_pack(trace, sid_path, output_path, progress=True):
    """Pack a SubtuneTrace into a holy grail PSID file.

    Args:
        trace: SubtuneTrace from ground_truth.capture_sid()
        sid_path: original SID path (for metadata)
        output_path: output .sid path
        progress: print progress messages

    Returns dict with stats.
    """
    if progress:
        print(f"[HG] Holy Grail Pack: {trace.n_frames} frames")

    # Generate assembly
    if progress:
        print("[HG] Generating assembly...")
    asm_src, stats = generate_full_asm(trace)

    if progress:
        for vi in range(3):
            print(f"  V{vi+1}: {stats['n_notes'][vi]} notes, "
                  f"{stats['n_instruments'][vi]} instruments, "
                  f"{stats['inst_sizes'][vi]} bytes inst + "
                  f"{stats['note_sizes'][vi]} bytes notes")
        print(f"  Filter: {stats['filter_size']} bytes")
        print(f"  Player code: {stats['player_size']} bytes")
        print(f"  Total data size: {stats['total_size']} bytes")
        print(f"  End address: ${stats['end_addr']:04X}")

    # Write assembly source (optional -- for debugging)
    asm_path = output_path.replace('.sid', '.s')
    with open(asm_path, 'w') as f:
        f.write(asm_src)
    if progress:
        print(f"  Assembly written to {asm_path}")

    # Assemble
    if progress:
        print("[HG] Assembling...")
    bin_path = output_path.replace('.sid', '.bin')
    r = subprocess.run([XA65, '-o', bin_path, asm_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ASSEMBLY FAILED:\n{r.stderr[:3000]}")
        raise RuntimeError("xa65 assembly failed")

    bin_size = os.path.getsize(bin_path)
    if progress:
        print(f"  Binary: {bin_size} bytes")

    # Read binary and prepend 2-byte load address
    with open(bin_path, 'rb') as f:
        bin_data = f.read()

    # The xa65 output starts at PLAYER_BASE; prepend 2-byte LE load address
    load_addr_bytes = struct.pack('<H', PLAYER_BASE)
    payload = load_addr_bytes + bin_data

    # Build PSID header
    init_addr = PLAYER_BASE       # jmp init is at +0
    play_addr = PLAYER_BASE + 3   # jmp play is at +3
    psid_hdr = build_psid_header(sid_path, PLAYER_BASE, init_addr, play_addr)

    # Write PSID: header + 2-byte load + binary
    with open(output_path, 'wb') as f:
        f.write(psid_hdr)
        f.write(payload)

    sid_size = os.path.getsize(output_path)
    if progress:
        print(f"  PSID written: {output_path} ({sid_size} bytes)")

    # Verify
    if progress:
        print("[HG] Verifying against ground truth (200 frames)...")
    match, total, mismatches = verify_against_trace(
        output_path, trace, max_frames=200, progress=progress
    )
    pct = 100.0 * match / total if total > 0 else 0.0
    if progress:
        print(f"  Match: {match}/{total} frames ({pct:.1f}%)")
        if mismatches:
            print(f"  First mismatch at frame {mismatches[0][0]}")

    stats['sid_size'] = sid_size
    stats['match_frames'] = match
    stats['total_frames'] = total
    stats['match_pct'] = pct
    stats['n_mismatches'] = len(mismatches)

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 holy_grail_pack.py <input.sid> <output.sid> [subtune] [max_frames]")
        sys.exit(1)

    sid_in = sys.argv[1]
    sid_out = sys.argv[2]
    subtune_num = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    max_frames = int(sys.argv[4]) if len(sys.argv) > 4 else None

    sys.path.insert(0, SCRIPT_DIR)
    from ground_truth import capture_sid

    print(f"Capturing ground truth for subtune {subtune_num}...")
    result = capture_sid(sid_in, subtunes=[subtune_num],
                         max_frames=max_frames, progress=True)
    trace = result.subtunes[0]
    print(f"Captured {trace.n_frames} frames")

    stats = holy_grail_pack(trace, sid_in, sid_out, progress=True)
    print(f"\nResult: {stats['match_pct']:.1f}% match, {stats['sid_size']} bytes SID")
