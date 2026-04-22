#!/usr/bin/env python3
"""
build_hg16.py — Build Commando_hg16.sid with pattern-level register dedup.

Architecture:
  Per voice:
    - Note stream: sequence of (instrument_id, length) pairs
    - Each instrument: 7 bytes × length frames (gate, flo, fhi, pwlo, pwhi, ad, sr)
    - Patterns: repeated sequences of (instrument_id, length) pairs
    - Orderlist: list of pattern IDs

  Player:
    - 3 voices, each with: pattern_ptr, note_ptr (within pattern), frame_ctr, inst_ptr
    - Each frame: if frame_ctr==0, load next note from pattern → set inst_ptr, length
                  else advance inst_ptr by 7
    - Pointer-advancing: inst_ptr += 7 per frame (no Y overflow)
"""

import subprocess
import sys
import os
import struct

SIDDUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../tools/siddump')
XA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../tools/xa65/xa/xa')
ORIG_SID = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Commando_original.sid')
OUT_SID = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Commando_hg16.sid')
OUT_ASM = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Commando_hg16.s')

NUM_FRAMES = 1500  # 30 seconds at 50fps

# Voice register offsets within the 21-byte frame:
# [flo, fhi, pwlo, pwhi, ctrl, ad, sr] for each voice
VOICE_OFFSETS = [
    (0, 1, 2, 3, 4, 5, 6),    # Voice 1: regs 0-6
    (7, 8, 9, 10, 11, 12, 13), # Voice 2: regs 7-13
    (14, 15, 16, 17, 18, 19, 20), # Voice 3: regs 14-20
]

# SID register addresses for each voice
VOICE_ADDRS = [
    (0xD400, 0xD401, 0xD402, 0xD403, 0xD404, 0xD405, 0xD406),
    (0xD407, 0xD408, 0xD409, 0xD40A, 0xD40B, 0xD40C, 0xD40D),
    (0xD40E, 0xD40F, 0xD410, 0xD411, 0xD412, 0xD413, 0xD414),
]


def capture_frames(duration=30):
    """Run siddump and return list of 21-element tuples."""
    cmd = [SIDDUMP, ORIG_SID, '--duration', str(duration), '--force-rsid']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(f"siddump error: {r.stderr}")
        sys.exit(1)
    lines = r.stdout.strip().split('\n')[2:]  # skip header lines
    frames = []
    for line in lines:
        if not line.strip():
            continue
        vals = [int(v, 16) for v in line.split(',')]
        assert len(vals) == 25, f"Expected 25 regs, got {len(vals)}: {line}"
        frames.append(vals)
    print(f"Captured {len(frames)} frames")
    return frames


def extract_voice(frames, voice_idx):
    """Extract 7 bytes per frame for one voice."""
    offs = VOICE_OFFSETS[voice_idx]
    result = []
    for f in frames:
        row = tuple(f[o] for o in offs)
        result.append(row)
    return result


def segment_notes(voice_frames):
    """
    Segment voice frames into notes.
    A new note starts when the CTRL register has gate=1 (bit 0 set)
    AND the previous frame had gate=0, OR on the first frame.

    Returns list of (start_frame, length) pairs.
    """
    notes = []
    n = len(voice_frames)
    i = 0
    start = 0
    prev_gate = 0

    while i < n:
        ctrl = voice_frames[i][4]  # ctrl is index 4 in (flo,fhi,pwlo,pwhi,ctrl,ad,sr)
        gate = ctrl & 1

        if i == 0:
            start = 0
        elif gate == 1 and prev_gate == 0:
            # Gate-on transition: end previous note, start new one
            notes.append((start, i - start))
            start = i

        prev_gate = gate
        i += 1

    # Last note
    notes.append((start, n - start))

    return notes


def make_instruments(voice_frames, note_segs):
    """
    Build instrument table: list of bytes for each unique note pattern.
    Each instrument = list of 7-tuples, one per frame.

    Returns:
      instruments: list of tuples (each tuple = frames data as bytes)
      note_ids: list of instrument indices for each note segment
    """
    inst_map = {}   # bytes → index
    instruments = []
    note_ids = []
    note_lengths = []

    for (start, length) in note_segs:
        frames_data = tuple(voice_frames[start:start+length])
        key = frames_data
        if key not in inst_map:
            inst_map[key] = len(instruments)
            instruments.append(frames_data)
        note_ids.append(inst_map[key])
        note_lengths.append(length)

    return instruments, note_ids, note_lengths


def find_patterns(note_ids, note_lengths, pattern_len=None):
    """
    Find repeated patterns in the note sequence.

    If pattern_len is specified, use fixed-length patterns.
    Otherwise, find all unique sequences.

    Returns:
      patterns: list of (note_id_list, note_length_list) pairs
      orderlist: list of pattern indices
    """
    n = len(note_ids)

    if pattern_len is not None:
        # Fixed-length pattern segmentation
        pat_map = {}
        patterns = []
        orderlist = []

        i = 0
        while i < n:
            end = min(i + pattern_len, n)
            key = tuple(zip(note_ids[i:end], note_lengths[i:end]))
            if key not in pat_map:
                pat_map[key] = len(patterns)
                patterns.append(key)
            orderlist.append(pat_map[key])
            i = end

        return patterns, orderlist
    else:
        # Each note is its own pattern (fallback = same as hg1)
        pat_map = {}
        patterns = []
        orderlist = []
        for nid, nlen in zip(note_ids, note_lengths):
            key = ((nid, nlen),)
            if key not in pat_map:
                pat_map[key] = len(patterns)
                patterns.append(key)
            orderlist.append(pat_map[key])
        return patterns, orderlist


def find_optimal_patterns(note_ids, note_lengths):
    """
    Find patterns by trying different segment sizes and picking the best
    (most deduplication = fewest total notes in orderlist patterns).

    Strategy: try grouping notes into runs of 4, 8, 16, etc and find what
    repeats most.

    Actually, the simplest approach: find repeated note sub-sequences
    using suffix array / greedy approach.
    """
    # Try a few pattern lengths, pick best compression
    best_patterns = None
    best_orderlist = None
    best_score = float('inf')

    n = len(note_ids)

    for plen in [2, 4, 6, 8, 12, 16, 24, 32]:
        patterns, orderlist = find_patterns(note_ids, note_lengths, plen)
        # Compression score: bytes stored in pattern tables + orderlist
        # Pattern table: sum(len(p)*2 + 1) for p in patterns (2 bytes per note entry + 1 FF terminator)
        # Orderlist: len(orderlist) + 1 (FF terminator)
        # Lower = more compressed
        pat_bytes = sum(len(p) * 2 + 1 for p in patterns)  # unique data
        ol_bytes_count = len(orderlist) + 1
        score = pat_bytes + ol_bytes_count
        print(f"  pattern_len={plen}: {len(patterns)} unique patterns, {len(orderlist)} in orderlist, {score} bytes")
        if score < best_score:
            best_score = score
            best_patterns = patterns
            best_orderlist = orderlist

    return best_patterns, best_orderlist


def build_assembly(frames, pattern_len=8):
    """Build the full assembly file."""
    print(f"Building assembly for {len(frames)} frames...")

    # Extract all 3 voices
    voices_data = []
    for v in range(3):
        vf = extract_voice(frames, v)
        notes = segment_notes(vf)
        print(f"Voice {v+1}: {len(notes)} notes")
        instruments, note_ids, note_lengths = make_instruments(vf, notes)
        print(f"  {len(instruments)} unique instruments")
        voices_data.append((vf, notes, instruments, note_ids, note_lengths))

    # Find patterns for each voice
    voices_patterns = []
    for v, (vf, notes, instruments, note_ids, note_lengths) in enumerate(voices_data):
        print(f"Voice {v+1} pattern search:")
        patterns, orderlist = find_optimal_patterns(note_ids, note_lengths)
        print(f"  Best: {len(patterns)} patterns, {len(orderlist)} in orderlist")
        voices_patterns.append((patterns, orderlist))

    # Extract volume/filter regs (from voice frame[21:25] = FILT_LO, FILT_HI, FILT_CTRL, VOL)
    # These are frame[21], frame[22], frame[23], frame[24]
    # We'll store the first frame's values as constants (or do per-frame if needed)
    # For now: initial volume = 0x0F, no filter

    # Generate assembly
    lines = []
    lines.append("; Commando_hg16.s - pattern-level register dedup player")
    lines.append("; Auto-generated by build_hg16.py")
    lines.append("")
    lines.append("        * = $1000")
    lines.append("        jmp init")
    lines.append("        jmp play")
    lines.append("")

    # Zero page layout:
    # $80-$87: Voice 1 state
    #   $80/$81: orderlist_ptr (lo/hi)
    #   $82:     orderlist_pos  (position in orderlist, counts down)
    #   $83:     note_ptr       (position within current pattern note list)
    #   $84/$85: inst_ptr       (lo/hi — pointer to current instrument frame data)
    #   $86:     frame_ctr      (frames remaining in current note)
    #   $87:     pat_note_cnt   (notes remaining in current pattern)
    # $88-$8F: Voice 2 state (same layout)
    # $90-$97: Voice 3 state (same layout)

    # Actually simplify: for each voice we need:
    #   pat_ptr (lo/hi): pointer into orderlist — gives pattern index
    #   note_ptr (lo/hi): pointer within current pattern's note sequence
    #   inst_ptr (lo/hi): pointer to current instrument frame data
    #   frame_ctr: frames left in this note
    # That's 7 bytes per voice = 21 bytes total

    # ZP layout:
    # V1: $80=pat_lo $81=pat_hi $82=note_lo $83=note_hi $84=inst_lo $85=inst_hi $86=frame_ctr
    # V2: $88=pat_lo $89=pat_hi $8A=note_lo $8B=note_hi $8C=inst_lo $8D=inst_hi $8E=frame_ctr
    # V3: $90=pat_lo $91=pat_hi $92=note_lo $93=note_hi $94=inst_lo $95=inst_hi $96=frame_ctr

    lines.append("init")

    # Filter/volume init (from first frame)
    f0 = frames[0]
    vol = f0[24]  # FILT_MODE_VOL
    filt_lo = f0[21]
    filt_hi = f0[22]
    filt_ctrl = f0[23]

    lines.append(f"        lda #${vol:02X}")
    lines.append("        sta $D418")
    if filt_lo or filt_hi or filt_ctrl:
        lines.append(f"        lda #${filt_lo:02X}")
        lines.append("        sta $D415")
        lines.append(f"        lda #${filt_hi:02X}")
        lines.append("        sta $D416")
        lines.append(f"        lda #${filt_ctrl:02X}")
        lines.append("        sta $D417")

    voice_labels = ['v1', 'v2', 'v3']
    zp_bases = [0x80, 0x88, 0x90]

    for v in range(3):
        vl = voice_labels[v]
        zp = zp_bases[v]
        patterns, orderlist = voices_patterns[v]

        # orderlist is a list of pattern indices
        # We'll store it as a byte sequence terminated by $FF
        # pattern data: each pattern is a sequence of (note_id, length) pairs terminated by $FF
        # note_id references into the instrument table

        # The first note to load: point pat_ptr at orderlist start
        lines.append(f"        lda #<{vl}ol")
        lines.append(f"        sta ${zp:02X}")
        lines.append(f"        lda #>{vl}ol")
        lines.append(f"        sta ${zp+1:02X}")
        # note_ptr = 0 (will be loaded on first play call)
        lines.append(f"        lda #0")
        lines.append(f"        sta ${zp+2:02X}")
        lines.append(f"        sta ${zp+3:02X}")
        lines.append(f"        sta ${zp+4:02X}")
        lines.append(f"        sta ${zp+5:02X}")
        lines.append(f"        sta ${zp+6:02X}")

    lines.append("        rts")
    lines.append("")

    # Play routine
    lines.append("play")

    for v in range(3):
        vl = voice_labels[v]
        zp = zp_bases[v]
        addrs = VOICE_ADDRS[v]

        lines.append(f"; --- Voice {v+1} ---")
        lines.append(f"{vl}voice")

        # Check frame_ctr: if > 0, skip note loading
        lines.append(f"        lda ${zp+6:02X}")  # frame_ctr
        lines.append(f"        beq {vl}nextnt")
        lines.append(f"        jmp {vl}play")

        lines.append(f"{vl}nextnt")
        # Load next note from current pattern
        # First check if note_ptr is valid, else load next pattern
        lines.append(f"        lda ${zp+2:02X}")   # note_ptr_lo
        lines.append(f"        ora ${zp+3:02X}")   # note_ptr_hi
        lines.append(f"        bne {vl}loadno")    # have a note_ptr

        # Load next pattern: read pattern_index from orderlist
        lines.append(f"{vl}nxtpat")
        lines.append(f"        ldy #0")
        lines.append(f"        lda (${ zp:02X}),y")  # pat_ptr
        lines.append(f"        cmp #$FF")
        lines.append(f"        bne {vl}havpat")
        # End of orderlist: loop back (or stop — for now loop)
        lines.append(f"        lda #<{vl}ol")
        lines.append(f"        sta ${zp:02X}")
        lines.append(f"        lda #>{vl}ol")
        lines.append(f"        sta ${zp+1:02X}")
        lines.append(f"        jmp {vl}nxtpat")

        lines.append(f"{vl}havpat")
        # Advance pat_ptr
        lines.append(f"        inc ${zp:02X}")
        lines.append(f"        bne {vl}pnc")
        lines.append(f"        inc ${zp+1:02X}")
        lines.append(f"{vl}pnc")
        # A = pattern_index, look up pattern address
        lines.append(f"        tax")
        lines.append(f"        lda {vl}plo,x")
        lines.append(f"        sta ${zp+2:02X}")
        lines.append(f"        lda {vl}phi,x")
        lines.append(f"        sta ${zp+3:02X}")

        # Load note from pattern
        lines.append(f"{vl}loadno")
        lines.append(f"        ldy #0")
        lines.append(f"        lda (${ zp+2:02X}),y")  # note_ptr → instrument_index
        lines.append(f"        cmp #$FF")
        lines.append(f"        bne {vl}havno")
        # End of pattern: clear note_ptr to force pattern reload
        lines.append(f"        lda #0")
        lines.append(f"        sta ${zp+2:02X}")
        lines.append(f"        sta ${zp+3:02X}")
        lines.append(f"        jmp {vl}nxtpat")

        lines.append(f"{vl}havno")
        # A = instrument_index
        # Read length from note_ptr+1
        lines.append(f"        tax")
        lines.append(f"        iny")
        lines.append(f"        lda (${ zp+2:02X}),y")  # length
        lines.append(f"        sta ${zp+6:02X}")       # frame_ctr = length
        # Advance note_ptr by 2
        lines.append(f"        clc")
        lines.append(f"        lda ${zp+2:02X}")
        lines.append(f"        adc #2")
        lines.append(f"        sta ${zp+2:02X}")
        lines.append(f"        bcc {vl}nnc")
        lines.append(f"        inc ${zp+3:02X}")
        lines.append(f"{vl}nnc")
        # Look up instrument address from X
        lines.append(f"        lda {vl}ilo,x")
        lines.append(f"        sta ${zp+4:02X}")
        lines.append(f"        lda {vl}ihi,x")
        lines.append(f"        sta ${zp+5:02X}")

        # Play: write 7 bytes from inst_ptr
        lines.append(f"{vl}play")
        lines.append(f"        ldy #0")
        lines.append(f"        lda (${ zp+4:02X}),y")
        lines.append(f"        sta ${addrs[0]:04X}")
        lines.append(f"        iny")
        lines.append(f"        lda (${ zp+4:02X}),y")
        lines.append(f"        sta ${addrs[1]:04X}")
        lines.append(f"        iny")
        lines.append(f"        lda (${ zp+4:02X}),y")
        lines.append(f"        sta ${addrs[2]:04X}")
        lines.append(f"        iny")
        lines.append(f"        lda (${ zp+4:02X}),y")
        lines.append(f"        sta ${addrs[3]:04X}")
        lines.append(f"        iny")
        lines.append(f"        lda (${ zp+4:02X}),y")
        lines.append(f"        sta ${addrs[4]:04X}")
        lines.append(f"        iny")
        lines.append(f"        lda (${ zp+4:02X}),y")
        lines.append(f"        sta ${addrs[5]:04X}")
        lines.append(f"        iny")
        lines.append(f"        lda (${ zp+4:02X}),y")
        lines.append(f"        sta ${addrs[6]:04X}")
        # Advance inst_ptr by 7
        lines.append(f"        clc")
        lines.append(f"        lda ${zp+4:02X}")
        lines.append(f"        adc #7")
        lines.append(f"        sta ${zp+4:02X}")
        lines.append(f"        bcc {vl}inc")
        lines.append(f"        inc ${zp+5:02X}")
        lines.append(f"{vl}inc")
        # Decrement frame_ctr
        lines.append(f"        dec ${zp+6:02X}")
        lines.append(f"{vl}done")
        lines.append("")

    lines.append("        rts")
    lines.append("")

    # Now emit data tables for each voice
    all_instruments = []  # Will collect for cross-ref

    for v in range(3):
        vl = voice_labels[v]
        vf, notes, instruments, note_ids, note_lengths = voices_data[v]
        patterns, orderlist = voices_patterns[v]

        # Instrument lo/hi tables
        lines.append(f"{vl}ilo")
        for i in range(len(instruments)):
            lines.append(f"        .byte <{vl}i{i}")
        lines.append(f"{vl}ihi")
        for i in range(len(instruments)):
            lines.append(f"        .byte >{vl}i{i}")
        lines.append("")

        # Pattern lo/hi tables
        lines.append(f"{vl}plo")
        for i in range(len(patterns)):
            lines.append(f"        .byte <{vl}p{i}")
        lines.append(f"{vl}phi")
        for i in range(len(patterns)):
            lines.append(f"        .byte >{vl}p{i}")
        lines.append("")

        # Orderlist
        lines.append(f"{vl}ol")
        ol_bytes = [str(idx) for idx in orderlist]
        ol_bytes.append("$FF")
        # Chunk into rows of 16
        for row_start in range(0, len(ol_bytes), 16):
            row = ol_bytes[row_start:row_start+16]
            lines.append(f"        .byte {','.join(row)}")
        lines.append("")

        # Pattern data: each pattern = sequence of (note_id, length) pairs, terminated by $FF
        for i, pat in enumerate(patterns):
            lines.append(f"{vl}p{i}")
            pat_bytes = []
            for (nid, nlen) in pat:
                pat_bytes.append(str(nid))
                pat_bytes.append(str(nlen))
            pat_bytes.append("$FF")
            for row_start in range(0, len(pat_bytes), 16):
                row = pat_bytes[row_start:row_start+16]
                lines.append(f"        .byte {','.join(row)}")
            lines.append("")

        # Instrument data
        for i, inst in enumerate(instruments):
            lines.append(f"{vl}i{i}")
            for frame_row in inst:
                row_bytes = ",".join(f"${b:02X}" for b in frame_row)
                lines.append(f"        .byte {row_bytes}")
            lines.append("")

    return "\n".join(lines)


def build_psid(prg_data, load_addr=0x1000, init_addr=0x1000, play_addr=0x1003,
               title="Commando", author="Rob Hubbard", released="1985 Elite"):
    """Build a PSID file from raw PRG data (without load addr prefix).

    PSID convention: load_addr=0 means 'read from first 2 bytes of data'.
    We prepend the 2-byte LE load address to the PRG body.
    """
    # PSID v2 header (0x7C bytes)
    header = bytearray(0x7C)
    header[0:4] = b'PSID'
    struct.pack_into('>H', header, 4, 2)       # version
    struct.pack_into('>H', header, 6, 0x7C)    # data offset
    struct.pack_into('>H', header, 8, 0)       # load_addr=0 means read from data
    struct.pack_into('>H', header, 10, init_addr)
    struct.pack_into('>H', header, 12, play_addr)
    struct.pack_into('>H', header, 14, 1)      # songs
    struct.pack_into('>H', header, 16, 1)      # start song
    struct.pack_into('>I', header, 18, 0)      # speed
    header[22:22+32] = title.encode('ascii', errors='replace')[:32].ljust(32, b'\0')
    header[54:54+32] = author.encode('ascii', errors='replace')[:32].ljust(32, b'\0')
    header[86:86+32] = released.encode('ascii', errors='replace')[:32].ljust(32, b'\0')
    # v2 extras
    struct.pack_into('>H', header, 118, 2)     # PAL
    struct.pack_into('>H', header, 120, 0)     # SID model 6581

    # Prepend 2-byte LE load address to PRG body
    prg_with_load = struct.pack('<H', load_addr) + prg_data

    return bytes(header) + prg_with_load


def main():
    print("=== Commando hg16 builder ===")

    # Step 1: Capture ground truth
    print(f"\nStep 1: Capturing {NUM_FRAMES} frames of ground truth...")
    frames = capture_frames(duration=30)
    if len(frames) < NUM_FRAMES:
        print(f"Warning: only got {len(frames)} frames (expected {NUM_FRAMES})")
    frames = frames[:NUM_FRAMES]

    # Step 2: Build assembly
    print("\nStep 2: Building assembly...")
    asm = build_assembly(frames)

    with open(OUT_ASM, 'w') as f:
        f.write(asm)
    print(f"Written: {OUT_ASM}")

    # Step 3: Assemble
    print("\nStep 3: Assembling...")
    prg_path = OUT_SID.replace('.sid', '.prg')
    r = subprocess.run(
        [XA, '-o', prg_path, OUT_ASM],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"Assembly FAILED:")
        print(r.stdout)
        print(r.stderr)
        sys.exit(1)
    print(f"Assembly OK: {prg_path}")

    # Step 4: Build PSID
    print("\nStep 4: Building PSID...")
    with open(prg_path, 'rb') as f:
        prg_data = f.read()
    # xa outputs raw binary starting at * = $1000, no load address header
    # PSID format requires: load=$0000, data starts with 2-byte LE load address
    load_addr = 0x1000
    print(f"Load address: ${load_addr:04X}, PRG size: {len(prg_data)} bytes")

    psid_data = build_psid(prg_data, load_addr=load_addr,
                           init_addr=0x1000, play_addr=0x1003)

    with open(OUT_SID, 'wb') as f:
        f.write(psid_data)
    print(f"Written: {OUT_SID}")

    # Step 5: Verify
    print("\nStep 5: Verifying...")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
    from sid_compare import compare_sids_tolerant

    orig = os.path.join(os.path.dirname(__file__), 'Commando_original.sid')
    result = compare_sids_tolerant(orig, OUT_SID, 30)
    print(f"Grade: {result['grade']} Score: {result['score']:.1f}")

    if result['grade'] in ('A', 'S'):
        print("SUCCESS: Grade A achieved!")
    else:
        print(f"Grade {result['grade']} — investigate differences")

    return result['grade']


if __name__ == '__main__':
    main()
