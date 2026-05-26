"""
Commando HG17-flat: sanity-check player using flat (non-delta) instrument format.
Like HG1 but with note deduplication (prefix sharing).
Goal: verify flat format works in libsidplayfp before adding delta encoding.
"""

import subprocess, sys, os, struct

SIDDUMP = "/home/jtr/sidfinity/tools/siddump"
ORIG_SID = "/home/jtr/sidfinity/data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid"
XA = "/home/jtr/sidfinity/tools/xa65/xa/xa"
OUT_SID = "/home/jtr/sidfinity/demo/hubbard/Commando_hg17_flat.sid"
OUT_ASM = "/home/jtr/sidfinity/demo/hubbard/Commando_hg17_flat.s"
OUT_BIN = "/tmp/commando_hg17_flat.bin"

VOICE_OFFSETS = [0, 7, 14]
FILT_OFFSET = 21
VOICE_BASES = [0xD400, 0xD407, 0xD40E]

def capture_ground_truth(duration=30):
    result = subprocess.run(
        [SIDDUMP, ORIG_SID, f"--duration={duration}", "--raw"],
        capture_output=True, text=True
    )
    frames = []
    for line in result.stdout.strip().split('\n'):
        line = line.strip()
        if not line: continue
        vals = [int(x, 16) for x in line.split(',')]
        if len(vals) == 25:
            frames.append(vals)
    print(f"Captured {len(frames)} frames")
    return frames

def extract_voice_frames(frames, vi):
    off = VOICE_OFFSETS[vi]
    return [tuple(f[off:off+7]) for f in frames]

def extract_filter_frames(frames):
    return [tuple(f[FILT_OFFSET:FILT_OFFSET+4]) for f in frames]

def detect_note_boundaries(voice_regs):
    boundaries = []
    n = len(voice_regs)
    note_start = 0
    for i in range(1, n):
        prev_ctrl = voice_regs[i-1][4]
        curr_ctrl = voice_regs[i][4]
        if (curr_ctrl & 1) and not (prev_ctrl & 1):
            boundaries.append((note_start, i))
            note_start = i
    boundaries.append((note_start, n))
    return boundaries

class InstrumentPool:
    def __init__(self):
        self._seqs = []
        self._by_frames = {}

    def add(self, frames):
        t = tuple(frames)
        if t in self._by_frames:
            return self._by_frames[t]
        n = len(frames)
        for idx, seq in enumerate(self._seqs):
            slen = len(seq)
            if slen >= n and seq[:n] == t:
                self._by_frames[t] = idx
                return idx
            if slen < n and t[:slen] == seq:
                self._seqs[idx] = t
                self._by_frames[t] = idx
                return idx
        idx = len(self._seqs)
        self._seqs.append(t)
        self._by_frames[t] = idx
        return idx

    def get_frames(self, idx):
        return self._seqs[idx]

    def __len__(self):
        return len(self._seqs)

def build_voice_data(voice_regs):
    pool = InstrumentPool()
    boundaries = detect_note_boundaries(voice_regs)
    note_sequence = []
    for start, end in boundaries:
        frames = voice_regs[start:end]
        if not frames: continue
        idx = pool.add(frames)
        length = min(len(frames), 255)
        note_sequence.append((idx, length))
    return note_sequence, pool

def encode_flat_instrument(frames, length):
    """Flat encoding: [length_byte, r0..r6 * length]"""
    data = bytearray()
    data.append(min(length, 255))
    for frame in frames[:length]:
        for b in frame:
            data.append(b)
    return data

def encode_all_instruments_flat(pool):
    """Encode all instruments in flat format."""
    data = bytearray()
    offsets = []
    for i in range(len(pool)):
        offsets.append(len(data))
        frames = list(pool.get_frames(i))
        encoded = encode_flat_instrument(frames, len(frames))
        data.extend(encoded)
    return data, offsets


ZP_VOICE = [
    (0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87),  # np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi
    (0x88, 0x89, 0x8A, 0x8B, 0x8C, 0x8D, 0x8E, 0x8F),
    (0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97),
]
# Filter: $A0=fp_lo $A1=fp_hi $A2=ffc_lo $A3=ffc_hi

def generate_player():
    """
    Generate flat-format player.
    ZP layout per voice: np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi
    where rp = read_ptr (advances 7 bytes per frame within instrument)
    ip = instrument ptr (base)
    """
    lines = []
    L = lines.append

    L("        * = $1000")
    L("        jmp init")
    L("        jmp play")
    L("")

    # init
    L("init")
    L("        lda #$0F")
    L("        sta $D418")
    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi = ZP_VOICE[vi]
        L(f"        lda #<ns{vi+1}")
        L(f"        sta ${np_lo:02X}")
        L(f"        lda #>ns{vi+1}")
        L(f"        sta ${np_hi:02X}")
        L(f"        lda #0")
        L(f"        sta ${nl:02X}")
        L(f"        sta ${fc:02X}")
    L("        ; Filter")
    L("        lda #<filtdata")
    L("        sta $A0")
    L("        lda #>filtdata")
    L("        sta $A1")
    L("        lda #0")
    L("        sta $A2")
    L("        sta $A3")
    L("        rts")
    L("")

    # play
    L("play")
    L("        jsr vplay1")
    L("        jsr vplay2")
    L("        jsr vplay3")
    L("        jmp fplay")
    L("")

    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi, rp_lo, rp_hi = ZP_VOICE[vi]
        vbase = VOICE_BASES[vi]
        vn = f"v{vi+1}"

        L(f"; Voice {vi+1}")
        L(f"vplay{vi+1}")
        # Check if we need new note: fc >= nl
        L(f"        lda ${fc:02X}")
        L(f"        cmp ${nl:02X}")
        L(f"        bcc {vn}play")     # fc < nl -> play current note
        L(f"        jmp {vn}load")     # fc >= nl -> load new note
        L(f"{vn}play")
        # Read 7 bytes from rp and write to SID
        # Write CT (index 4, offset 4) first
        L(f"        ldy #4")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase+4:04X}")   # CT
        L(f"        ldy #0")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase+0:04X}")   # FL
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase+1:04X}")   # FH
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase+2:04X}")   # PL
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase+3:04X}")   # PH
        L(f"        ldy #5")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase+5:04X}")   # AD
        L(f"        iny")
        L(f"        lda (${rp_lo:02X}),y")
        L(f"        sta ${vbase+6:04X}")   # SR
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

        L(f"{vn}load")
        L(f"        ldy #0")
        L(f"        lda (${np_lo:02X}),y")
        L(f"        cmp #$FF")
        L(f"        bne {vn}ln0")
        L(f"        rts")
        L(f"{vn}ln0")
        L(f"        sta ${nl:02X}")
        L(f"        iny")
        L(f"        lda (${np_lo:02X}),y")
        L(f"        sta ${ip_lo:02X}")
        L(f"        iny")
        L(f"        lda (${np_lo:02X}),y")
        L(f"        sta ${ip_hi:02X}")
        # Advance note ptr by 3
        L(f"        clc")
        L(f"        lda ${np_lo:02X}")
        L(f"        adc #3")
        L(f"        sta ${np_lo:02X}")
        L(f"        bcc {vn}nnc")
        L(f"        inc ${np_hi:02X}")
        L(f"{vn}nnc")
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
        # Fall through to play current note's first frame
        L(f"        jmp {vn}play")
        L("")

    # Filter
    L("fplay")
    L("        lda $A3")
    L("        cmp #$0C")
    L("        bcs fpdone")
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


def get_player_size():
    asm = generate_player()
    asm.append("ns1  .byte $FF")
    asm.append("ns2  .byte $FF")
    asm.append("ns3  .byte $FF")
    asm.append("filtdata  .byte $FF")
    with open("/tmp/hg17_flat_probe.s", 'w') as f:
        f.write("\n".join(asm))
    r = subprocess.run([XA, "-o", "/tmp/hg17_flat_probe.bin", "/tmp/hg17_flat_probe.s"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Probe asm failed: {r.stderr}")
    return os.path.getsize("/tmp/hg17_flat_probe.bin") - 4  # -4 for dummy data bytes


def generate_asm(frames):
    v_regs = [extract_voice_frames(frames, i) for i in range(3)]
    filt_regs = extract_filter_frames(frames)

    print("Building note sequences...")
    voice_seqs = []
    voice_pools = []
    for vi in range(3):
        seq, pool = build_voice_data(v_regs[vi])
        voice_seqs.append(seq)
        voice_pools.append(pool)
        print(f"  V{vi+1}: {len(seq)} notes, {len(pool)} unique instruments")

    filter_data = bytearray()
    for fr in filt_regs:
        for b in fr: filter_data.append(b)

    print("  Measuring player code size...")
    player_size = get_player_size()
    INST_BASE = 0x1000 + player_size
    print(f"  Player code: {player_size} bytes, data starts at ${INST_BASE:04X}")

    inst_data_list = []
    inst_abs_offsets_list = []
    running = INST_BASE
    for vi in range(3):
        data, rel_offs = encode_all_instruments_flat(voice_pools[vi])
        abs_offs = [running + o for o in rel_offs]
        inst_data_list.append(data)
        inst_abs_offsets_list.append(abs_offs)
        running += len(data)

    note_stream_addrs = []
    note_stream_data = []
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

    filter_addr = running
    end_addr = filter_addr + len(filter_data)

    total_inst = sum(len(d) for d in inst_data_list)
    total_notes = sum(len(d) for d in note_stream_data)
    print(f"  Inst data (flat): {total_inst} bytes")
    print(f"  Note streams: {total_notes} bytes")
    print(f"  Filter: {len(filter_data)} bytes")
    print(f"  End: ${end_addr:04X}")
    if end_addr > 0xFFFF:
        print(f"  WARNING: Exceeds 64KB!")

    asm = generate_player()
    for vi in range(3):
        data = inst_data_list[vi]
        asm.append(f"; V{vi+1} instruments ({len(data)} bytes, {len(voice_pools[vi])} unique)")
        flat = list(data)
        for i in range(0, len(flat), 16):
            chunk = flat[i:i+16]
            asm.append(f"        .byte {','.join(f'${b:02X}' for b in chunk)}")
    asm.append("")
    asm.append("; Note streams")
    for vi in range(3):
        asm.append(f"ns{vi+1}")
        flat = list(note_stream_data[vi])
        for i in range(0, len(flat), 15):
            asm.append(f"        .byte {','.join(f'${b:02X}' for b in flat[i:i+15])}")
        asm.append("")
    asm.append("; Filter data")
    asm.append("filtdata")
    flat = list(filter_data)
    for i in range(0, len(flat), 16):
        asm.append(f"        .byte {','.join(f'${b:02X}' for b in flat[i:i+16])}")
    return "\n".join(asm)


def build_psid(bin_data, load_addr):
    hdr = bytearray(124)
    hdr[0:4] = b'PSID'
    struct.pack_into('>H', hdr, 4, 2)
    struct.pack_into('>H', hdr, 6, 124)
    struct.pack_into('>H', hdr, 8, load_addr)
    struct.pack_into('>H', hdr, 10, load_addr)
    struct.pack_into('>H', hdr, 12, load_addr + 3)
    struct.pack_into('>H', hdr, 14, 1)
    struct.pack_into('>H', hdr, 16, 1)
    struct.pack_into('>I', hdr, 18, 0)
    hdr[22:54] = (b'Commando (HG17-flat)\x00' + bytes(32))[:32]
    hdr[54:86] = (b'Rob Hubbard\x00' + bytes(32))[:32]
    hdr[86:118] = (b'1985 Elite\x00' + bytes(32))[:32]
    return bytes(hdr) + bytes(bin_data)


def main():
    print("=== Commando HG17-flat ===")
    print("\n[1] Ground truth (30s)...")
    frames = capture_ground_truth(30)

    print("\n[2] Generating assembly...")
    asm = generate_asm(frames)
    with open(OUT_ASM, 'w') as f:
        f.write(asm)

    print("\n[3] Assembling...")
    r = subprocess.run([XA, "-o", OUT_BIN, OUT_ASM], capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", r.stderr[:2000])
        sys.exit(1)
    print(f"  OK: {os.path.getsize(OUT_BIN)} bytes")

    print("\n[4] Building PSID...")
    with open(OUT_BIN, 'rb') as f:
        bin_data = f.read()
    psid = build_psid(bin_data, 0x1000)
    with open(OUT_SID, 'wb') as f:
        f.write(psid)
    print(f"  {OUT_SID} ({len(psid)} bytes)")

    print("\n[5] Comparing (30s)...")
    sys.path.insert(0, '/home/jtr/sidfinity/src')
    from sid_compare import compare_sids_tolerant, compare_tolerant, dump_sid, score_results
    r = compare_sids_tolerant(ORIG_SID, OUT_SID, 30)
    if r is None:
        print("  FAIL: None")
    else:
        print(f"  Grade={r['grade']} Score={r['score']:.1f}")
        orig = dump_sid(ORIG_SID, 30, subtune=1)
        new = dump_sid(OUT_SID, 30, subtune=1)
        res = compare_tolerant(orig, new)
        for v in range(3):
            vr = res['voices'][v]
            print(f"  V{v+1}: {dict((k,vr[k]) for k in sorted(vr) if vr[k] > 0)}")


if __name__ == '__main__':
    main()
