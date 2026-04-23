"""
structured_pack.py -- Structured SIDfinity packer.

Middle ground between holy_grail_pack.py (24 KB, perfect) and V3 pipeline (3.5 KB, complex).

Architecture:
  - Freq table: all unique (freq_lo, freq_hi) pairs observed across all voices
  - Instruments: shared pool of frame sequences, 6 bytes per frame:
      (ctrl, freq_idx, pw_lo, pw_hi, ad, sr)
    pw values are per-frame (pw_hi can change within a note).
  - Note stream per voice: (length, inst_lo, inst_hi) per note, $FF terminator
  - Filter: flat 4-byte-per-frame stream (fc_lo, fc_hi, res_route, vol_mode).
    Constant filter detected and stored as 4 bytes (single frame repeated).
  - Player: pointer-advancing, ~250 bytes of 6502 code

Instrument format: [length_byte, (ctrl, freq_idx, pw_lo, pw_hi, ad, sr) * length]
Note stream entry: [length_byte, inst_lo, inst_hi]  (3 bytes per note)
Terminator: $FF

Size vs holy_grail (7 bytes/frame):
  6 bytes/frame instrument + freq table compression = meaningful savings.
  Filter dedup: constant filter -> 4 bytes instead of n_frames*4.

Usage:
    from ground_truth import capture_sid
    from structured_pack import structured_pack
    t = capture_sid('song.sid', subtunes=[1]).subtunes[0]
    structured_pack(t, 'song.sid', '/tmp/out.sid')
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

PLAYER_BASE = 0x1000

# Zero-page layout per voice (8 bytes each)
# np_lo, np_hi = note stream pointer
# fc    = frame counter within note (0-based)
# nl    = note length (frames)
# ip_lo, ip_hi = instrument base pointer (points to length byte)
# rp_lo, rp_hi = read pointer within instrument data (advances 6/frame)
ZP_VOICE = [
    (0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77),  # v1
    (0x78, 0x79, 0x7A, 0x7B, 0x7C, 0x7D, 0x7E, 0x7F),  # v2
    (0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87),  # v3
]
# ZP filter: $90/$91 = frame pointer, $92/$93 = frame counter (16-bit)
ZP_FP_LO  = 0x90
ZP_FP_HI  = 0x91
ZP_FC_LO  = 0x92
ZP_FC_HI  = 0x93


# ---------------------------------------------------------------------------
# Freq table
# ---------------------------------------------------------------------------

class FreqTable:
    """Maps (freq_lo, freq_hi) -> index, shared across all voices."""

    def __init__(self):
        self._pairs = []
        self._index = {}

    def get_index(self, freq_lo, freq_hi):
        key = (freq_lo, freq_hi)
        if key not in self._index:
            self._index[key] = len(self._pairs)
            self._pairs.append(key)
        return self._index[key]

    def build_tables(self):
        lo = bytearray(p[0] for p in self._pairs)
        hi = bytearray(p[1] for p in self._pairs)
        return lo, hi

    def __len__(self):
        return len(self._pairs)


# ---------------------------------------------------------------------------
# Instrument pool
# ---------------------------------------------------------------------------

class InstrumentPool:
    """Cross-voice deduplication pool for 6-byte-per-frame instrument sequences.

    Each instrument frame is a 6-tuple: (ctrl, freq_idx, pw_lo, pw_hi, ad, sr).
    Two notes with identical frame sequences share one instrument entry.
    Prefix sharing: if note A is a prefix of note B, A reuses B's entry.
    """

    def __init__(self):
        self._seqs = []
        self._by_key = {}

    def add(self, frames):
        """Add a frame sequence, return (index, actual_length)."""
        key = tuple(frames)
        if key in self._by_key:
            return self._by_key[key], len(frames)

        n = len(frames)
        for idx, seq in enumerate(self._seqs):
            if len(seq) >= n and seq[:n] == key:
                self._by_key[key] = idx
                return idx, n
            slen = len(seq)
            if slen < n and key[:slen] == seq:
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
    Returns list of (start_frame, end_frame) tuples, always starting from 0.
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
# Voice data extraction
# ---------------------------------------------------------------------------

def build_voice_data(voice_regs, freq_table, inst_pool):
    """Extract note sequence for one voice, populating shared freq table and pool.

    voice_regs: list of 7-tuples (freq_lo, freq_hi, pw_lo, pw_hi, ctrl, ad, sr)

    Returns list of (inst_idx, length) tuples.
    pw_hi is part of instrument frame data (can change within a note).
    """
    boundaries = detect_note_boundaries(voice_regs)
    note_sequence = []
    for start, end in boundaries:
        frames = voice_regs[start:end]
        if not frames:
            continue
        n = min(len(frames), 255)
        frames = frames[:n]

        # Build instrument frame sequence: (ctrl, freq_idx, pw_lo, pw_hi, ad, sr)
        inst_frames = []
        for f in frames:
            freq_lo, freq_hi, pw_lo, pw_hi, ctrl, ad, sr = f
            freq_idx = freq_table.get_index(freq_lo, freq_hi)
            inst_frames.append((ctrl, freq_idx, pw_lo, pw_hi, ad, sr))

        idx, length = inst_pool.add(inst_frames)
        note_sequence.append((idx, length))

    return note_sequence


# ---------------------------------------------------------------------------
# Data encoding
# ---------------------------------------------------------------------------

def encode_instrument(frames):
    """Encode one instrument: [length_byte, (ctrl, freq_idx, pw_lo, pw_hi, ad, sr) * length]"""
    data = bytearray()
    data.append(len(frames) & 0xFF)
    for ctrl, freq_idx, pw_lo, pw_hi, ad, sr in frames:
        data.append(ctrl)
        data.append(freq_idx)
        data.append(pw_lo)
        data.append(pw_hi)
        data.append(ad)
        data.append(sr)
    return data


def bytes_to_asm(data, indent="        "):
    """Convert bytes to xa65 .byte lines, 16 bytes per line."""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        lines.append(indent + ".byte " + ",".join(f"${b:02X}" for b in chunk))
    return lines


# ---------------------------------------------------------------------------
# Filter analysis
# ---------------------------------------------------------------------------

def analyze_filter(filter_frames):
    """Return (is_constant, filter_data_bytes).

    If constant: 4 bytes (single frame value).
    If variable: 4 * n_frames bytes (flat stream).
    """
    unique = set(filter_frames)
    if len(unique) == 1:
        val = list(unique)[0]
        return True, bytearray(val)
    data = bytearray()
    for fr in filter_frames:
        for b in fr:
            data.append(b)
    return False, data


# ---------------------------------------------------------------------------
# Player code generation
# ---------------------------------------------------------------------------

def generate_player_asm(filter_is_constant):
    """Generate the structured player in xa65 assembly.

    Instrument frame = 6 bytes: (ctrl, freq_idx, pw_lo, pw_hi, ad, sr)
    Note stream entry = 3 bytes: (length, inst_lo, inst_hi)

    ZP per voice:
      np_lo, np_hi  note stream pointer
      fc            frame counter (0-based)
      nl            note length
      ip_lo, ip_hi  instrument pointer (base, points to length byte)
      rp_lo, rp_hi  read pointer within instrument (advances 6 per frame)

    Freq lookup: X = freq_idx, LDA freq_lo_tbl,X / LDA freq_hi_tbl,X
    Filter: constant (write once in init) or flat stream.
    """
    lines = []
    L = lines.append

    L(f"        * = ${PLAYER_BASE:04X}")
    L("        jmp init")
    L("        jmp play")
    L("")

    # --- init ---
    L("init")
    # Set initial volume/filter
    if filter_is_constant:
        L("        lda filt_const")
        L("        sta $D415")
        L("        lda filt_const+1")
        L("        sta $D416")
        L("        lda filt_const+2")
        L("        sta $D417")
        L("        lda filt_const+3")
        L("        sta $D418")
    else:
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
    if not filter_is_constant:
        L(f"        lda #<filtdata")
        L(f"        sta ${ZP_FP_LO:02X}")
        L(f"        lda #>filtdata")
        L(f"        sta ${ZP_FP_HI:02X}")
        L(f"        lda #0")
        L(f"        sta ${ZP_FC_LO:02X}")
        L(f"        sta ${ZP_FC_HI:02X}")
    L("        rts")
    L("")

    # --- play ---
    L("play")
    for vi in range(3):
        L(f"        jsr vplay{vi + 1}")
    if not filter_is_constant:
        L("        jmp fplay")
    else:
        L("        rts")
    L("")

    # --- per-voice players ---
    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi = ZP_VOICE[vi]
        vbase = VOICE_BASES[vi]
        vn = f"v{vi + 1}"

        L(f"; ---- Voice {vi + 1} ----")
        L(f"vplay{vi + 1}")
        # if fc >= nl, load next note
        L(f"        lda ${fc:02X}")
        L(f"        cmp ${nl:02X}")
        L(f"        bcc {vn}play")
        L(f"        jmp {vn}load")
        L("")

        # play one frame
        # instrument frame layout: [ctrl, freq_idx, pw_lo, pw_hi, ad, sr]
        L(f"{vn}play")
        L(f"        ldy #0")
        # ctrl
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 4:04X}")
        # freq_idx -> freq lookup
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        tax")
        L(f"        lda freq_lo_tbl,x")
        L(f"        sta ${vbase + 0:04X}")
        L(f"        lda freq_hi_tbl,x")
        L(f"        sta ${vbase + 1:04X}")
        # pw_lo
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 2:04X}")
        # pw_hi
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 3:04X}")
        # ad
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 5:04X}")
        # sr
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase + 6:04X}")
        # Advance rp by 6
        L(f"        clc")
        L(f"        lda ${rp_lo:02X}")
        L(f"        adc #6")
        L(f"        sta ${rp_lo:02X}")
        L(f"        bcc {vn}nc")
        L(f"        inc ${rp_hi:02X}")
        L(f"{vn}nc")
        L(f"        inc ${fc:02X}")
        L(f"        rts")
        L("")

        # load next note from note stream
        # note stream entry: [length, inst_lo, inst_hi]
        L(f"{vn}load")
        L(f"        ldy #0")
        L(f"        lda (${np_lo:02X}),y")
        L(f"        cmp #$FF")
        L(f"        bne {vn}ln0")
        # End of stream - silence voice
        L(f"        lda #0")
        L(f"        sta ${vbase + 4:04X}")
        L(f"        rts")
        L(f"{vn}ln0")
        # length byte
        L(f"        sta ${nl:02X}")
        # inst_lo (offset 1)
        L(f"        iny")
        L(f"        lda (${np_lo:02X}),y")
        L(f"        sta ${ip_lo:02X}")
        # inst_hi (offset 2)
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
        # rp = ip + 1 (skip length byte)
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

    if not filter_is_constant:
        # --- filter player ---
        L("; ---- Filter ----")
        L("fplay")
        L(f"        lda ${ZP_FC_HI:02X}")
        L(f"        cmp #>filtlen")
        L(f"        bcc fpgo")
        L(f"        beq fpeq")
        L(f"        rts")
        L(f"fpeq")
        L(f"        lda ${ZP_FC_LO:02X}")
        L(f"        cmp #<filtlen")
        L(f"        bcs fpdone")
        L("fpgo")
        L(f"        ldy #0")
        L(f"        lda (${ZP_FP_LO:02X}),y")
        L(f"        sta $D415")
        L(f"        iny")
        L(f"        lda (${ZP_FP_LO:02X}),y")
        L(f"        sta $D416")
        L(f"        iny")
        L(f"        lda (${ZP_FP_LO:02X}),y")
        L(f"        sta $D417")
        L(f"        iny")
        L(f"        lda (${ZP_FP_LO:02X}),y")
        L(f"        sta $D418")
        L(f"        clc")
        L(f"        lda ${ZP_FP_LO:02X}")
        L(f"        adc #4")
        L(f"        sta ${ZP_FP_LO:02X}")
        L(f"        bcc fpnc")
        L(f"        inc ${ZP_FP_HI:02X}")
        L(f"fpnc")
        L(f"        inc ${ZP_FC_LO:02X}")
        L(f"        bne fpdone")
        L(f"        inc ${ZP_FC_HI:02X}")
        L(f"fpdone")
        L(f"        rts")
        L("")

    return lines


def measure_player_size(filter_is_constant):
    """Assemble player with stub data to measure code size."""
    asm_lines = generate_player_asm(filter_is_constant)
    asm_lines.append("filtlen = 0")
    for vi in range(3):
        asm_lines.append(f"ns{vi + 1}  .byte $FF")
    if filter_is_constant:
        asm_lines.append("filt_const  .byte $00,$00,$00,$0F")
    else:
        asm_lines.append("filtdata  .byte $00,$00,$00,$0F")
    asm_lines.append("freq_lo_tbl  .byte $00")
    asm_lines.append("freq_hi_tbl  .byte $00")

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
        # Subtract stub data: 3*1 byte ($FF) + 4 bytes filter + 2 bytes freq
        stub_bytes = 3 + 4 + 1 + 1
        return size - stub_bytes
    finally:
        os.unlink(src_path)
        if os.path.exists(bin_path):
            os.unlink(bin_path)


# ---------------------------------------------------------------------------
# Full assembly generation
# ---------------------------------------------------------------------------

def generate_full_asm(trace):
    """Generate complete xa65 assembly from a SubtuneTrace.

    Returns (asm_source_str, stats_dict).
    """
    # Extract per-voice 7-tuples: (freq_lo, freq_hi, pw_lo, pw_hi, ctrl, ad, sr)
    v_regs = []
    for vi in range(3):
        voff = VOICE_OFFSETS[vi]
        regs = [tuple(f[voff:voff + 7]) for f in trace.frames]
        v_regs.append(regs)

    # Extract filter frames
    filter_frames = [tuple(f[FILTER_OFFSET:FILTER_OFFSET + 4]) for f in trace.frames]
    filter_is_constant, filter_data = analyze_filter(filter_frames)

    # Build shared freq table and instrument pool
    freq_table = FreqTable()
    inst_pool = InstrumentPool()
    voice_seqs = []
    for vi in range(3):
        seq = build_voice_data(v_regs[vi], freq_table, inst_pool)
        voice_seqs.append(seq)

    # Measure player code size
    player_size = measure_player_size(filter_is_constant)
    data_base = PLAYER_BASE + player_size

    # Freq tables (placed right after player code)
    freq_lo_bytes, freq_hi_bytes = freq_table.build_tables()
    n_freqs = len(freq_table)
    freq_tbl_size = n_freqs * 2

    # Instrument data
    inst_base = data_base + freq_tbl_size
    if filter_is_constant:
        # filt_const placed right after player, before freq tables
        # Actually put freq tables first, then instruments
        # filt_const is a 4-byte symbol -- place at end of player (already included in player_size)
        # We'll include it as a data label after player code
        inst_base = data_base + 4 + freq_tbl_size  # +4 for filt_const
    else:
        inst_base = data_base + freq_tbl_size

    inst_data = bytearray()
    inst_offsets = []
    for idx in range(len(inst_pool)):
        inst_offsets.append(inst_base + len(inst_data))
        frames = list(inst_pool.get_frames(idx))
        enc = encode_instrument(frames)
        inst_data.extend(enc)

    # Note streams (3 bytes per note: length, inst_lo, inst_hi)
    note_stream_base = inst_base + len(inst_data)
    note_stream_data = []
    running = note_stream_base
    for vi in range(3):
        enc = bytearray()
        for inst_idx, length in voice_seqs[vi]:
            inst_addr = inst_offsets[inst_idx]
            enc.append(length & 0xFF)
            enc.append(inst_addr & 0xFF)
            enc.append((inst_addr >> 8) & 0xFF)
        enc.append(0xFF)
        note_stream_data.append(enc)
        running += len(enc)

    # Filter data (either 4 bytes constant or full stream)
    filter_addr = running
    filter_size = len(filter_data)

    if filter_is_constant:
        total_size = filter_addr + filter_size - PLAYER_BASE
    else:
        total_size = filter_addr + filter_size - PLAYER_BASE

    stats = {
        'player_size': player_size,
        'freq_tbl_size': freq_tbl_size,
        'n_freqs': n_freqs,
        'inst_size': len(inst_data),
        'n_instruments': len(inst_pool),
        'note_sizes': [len(d) for d in note_stream_data],
        'n_notes': [len(s) for s in voice_seqs],
        'filter_size': filter_size,
        'filter_is_constant': filter_is_constant,
        'total_size': total_size,
        'end_addr': filter_addr + filter_size,
    }

    # Assemble source
    asm_lines = generate_player_asm(filter_is_constant)

    if not filter_is_constant:
        n_filter_frames = len(filter_frames)
        asm_lines.append(f"filtlen = {n_filter_frames}")
    asm_lines.append("")

    # Constant filter data (placed right after player, before freq tables)
    if filter_is_constant:
        asm_lines.append("; Filter constant (4 bytes)")
        asm_lines.append("filt_const")
        asm_lines.extend(bytes_to_asm(filter_data))
        asm_lines.append("")

    # Freq tables
    asm_lines.append(f"; Freq table ({n_freqs} entries, {freq_tbl_size} bytes)")
    asm_lines.append("freq_lo_tbl")
    asm_lines.extend(bytes_to_asm(freq_lo_bytes))
    asm_lines.append("freq_hi_tbl")
    asm_lines.extend(bytes_to_asm(freq_hi_bytes))
    asm_lines.append("")

    # Instrument data
    asm_lines.append(f"; Instrument pool ({len(inst_pool)} unique, {len(inst_data)} bytes, "
                     f"6 bytes per frame)")
    asm_lines.extend(bytes_to_asm(inst_data))
    asm_lines.append("")

    # Note streams
    asm_lines.append("; Note streams (3 bytes per note - length, inst_lo, inst_hi)")
    for vi in range(3):
        asm_lines.append(f"ns{vi + 1}")
        asm_lines.extend(bytes_to_asm(note_stream_data[vi]))
        asm_lines.append("")

    # Variable filter data
    if not filter_is_constant:
        asm_lines.append("; Filter data (4 bytes per frame)")
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

    orig_header_len = struct.unpack('>H', orig[6:8])[0]
    title = orig[22:54].rstrip(b'\x00')
    author = orig[54:86].rstrip(b'\x00')
    copyright_ = orig[86:118].rstrip(b'\x00')
    flags = struct.unpack('>H', orig[118:120])[0] if orig_header_len >= 120 else 0x0014

    hdr = bytearray(124)
    hdr[0:4] = b'PSID'
    struct.pack_into('>H', hdr, 4, 2)
    struct.pack_into('>H', hdr, 6, 124)
    struct.pack_into('>H', hdr, 8, 0)        # load_addr=0 (in binary)
    struct.pack_into('>H', hdr, 10, init_addr)
    struct.pack_into('>H', hdr, 12, play_addr)
    struct.pack_into('>H', hdr, 14, 1)
    struct.pack_into('>H', hdr, 16, 1)
    struct.pack_into('>I', hdr, 18, 0)

    hdr[22:54] = (title + b'\x00' * 32)[:32]
    hdr[54:86] = (author + b'\x00' * 32)[:32]
    hdr[86:118] = (copyright_ + b'\x00' * 32)[:32]
    struct.pack_into('>H', hdr, 118, flags)

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

    with open(output_sid_path, 'rb') as f:
        data = f.read()

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
    mem[0xFFF0] = 0x00

    mpu = MPU()
    mpu.memory = mem

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

    reg_names = []
    for vi in range(3):
        for r in ('FL', 'FH', 'PL', 'PH', 'CT', 'AD', 'SR'):
            reg_names.append(f'V{vi+1}_{r}')
    for ri in range(4):
        reg_names.append(f'FLT{ri}')

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
                diff_str = ', '.join(
                    f'{reg_names[i]}={e:02X}->{g:02X}'
                    for i, e, g in diffs
                )
                print(f"  Frame {frame:4d}: {diff_str}")

    return match_count, n_frames, mismatches


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def structured_pack(trace, sid_path, output_path, progress=True):
    """Pack a SubtuneTrace into a structured PSID file.

    Args:
        trace: SubtuneTrace from ground_truth.capture_sid()
        sid_path: original SID path (for metadata)
        output_path: output .sid path
        progress: print progress messages

    Returns dict with stats.
    """
    if progress:
        print(f"[SP] Structured Pack: {trace.n_frames} frames")

    if progress:
        print("[SP] Generating assembly...")
    asm_src, stats = generate_full_asm(trace)

    if progress:
        print(f"  Player code: {stats['player_size']} bytes")
        print(f"  Freq table: {stats['n_freqs']} entries, {stats['freq_tbl_size']} bytes")
        print(f"  Instruments: {stats['n_instruments']} unique, {stats['inst_size']} bytes "
              f"(6 bytes per frame)")
        for vi in range(3):
            print(f"  V{vi+1}: {stats['n_notes'][vi]} notes, "
                  f"{stats['note_sizes'][vi]} bytes note stream")
        filt_desc = "constant (4 bytes)" if stats['filter_is_constant'] else f"{stats['filter_size']} bytes stream"
        print(f"  Filter: {filt_desc}")
        print(f"  Total data size: {stats['total_size']} bytes")
        print(f"  End address: ${stats['end_addr']:04X}")

    asm_path = output_path.replace('.sid', '.s')
    with open(asm_path, 'w') as f:
        f.write(asm_src)
    if progress:
        print(f"  Assembly written to {asm_path}")

    if progress:
        print("[SP] Assembling...")
    bin_path = output_path.replace('.sid', '.bin')
    r = subprocess.run([XA65, '-o', bin_path, asm_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ASSEMBLY FAILED:\n{r.stderr[:3000]}")
        raise RuntimeError("xa65 assembly failed")

    bin_size = os.path.getsize(bin_path)
    if progress:
        print(f"  Binary: {bin_size} bytes")

    with open(bin_path, 'rb') as f:
        bin_data = f.read()

    load_addr_bytes = struct.pack('<H', PLAYER_BASE)
    payload = load_addr_bytes + bin_data

    init_addr = PLAYER_BASE
    play_addr = PLAYER_BASE + 3
    psid_hdr = build_psid_header(sid_path, PLAYER_BASE, init_addr, play_addr)

    with open(output_path, 'wb') as f:
        f.write(psid_hdr)
        f.write(payload)

    sid_size = os.path.getsize(output_path)
    if progress:
        print(f"  PSID written: {output_path} ({sid_size} bytes)")

    if progress:
        print("[SP] Verifying against ground truth (200 frames)...")
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

    if os.path.exists(bin_path):
        os.unlink(bin_path)

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 structured_pack.py <input.sid> <output.sid> [subtune] [max_frames]")
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

    stats = structured_pack(trace, sid_in, sid_out, progress=True)
    print(f"\nResult: {stats['match_pct']:.1f}% match, {stats['sid_size']} bytes SID")
