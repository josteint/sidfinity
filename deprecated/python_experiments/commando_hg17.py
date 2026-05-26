"""
Commando HG17 - Hybrid note-event player with delta-encoded instruments.

Architecture:
- Per-voice note sequence: list of (instrument_index, length)
- Instrument table: delta-encoded per-frame changes
  Format per instrument:
    [length_byte] [frame0: 7 full bytes] [frame1+: bitmask + changed bytes] ...
- Player: pointer-advancing delta decoder

Delta encoding format per frame (after first frame):
  [bitmask: 1 byte, bits 0-6 = which registers changed]
  [for each set bit: new value byte]
"""

import subprocess, sys, os, struct

SIDDUMP = "/home/jtr/sidfinity/tools/siddump"
ORIG_SID = "/home/jtr/sidfinity/data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid"
XA = "/home/jtr/sidfinity/tools/xa65/xa/xa"
OUT_SID = "/home/jtr/sidfinity/demo/hubbard/Commando_hg17.sid"
OUT_ASM = "/home/jtr/sidfinity/demo/hubbard/Commando_hg17.s"
OUT_BIN = "/tmp/commando_hg17.bin"

VOICE_OFFSETS = [0, 7, 14]
FILT_OFFSET = 21
VOICE_BASES = [0xD400, 0xD407, 0xD40E]

def capture_ground_truth(duration=60):
    result = subprocess.run(
        [SIDDUMP, ORIG_SID, f"--duration={duration}", "--raw"],
        capture_output=True, text=True
    )
    frames = []
    for line in result.stdout.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        vals = [int(x, 16) for x in line.split(',')]
        if len(vals) == 25:
            frames.append(vals)
    print(f"Captured {len(frames)} frames")
    return frames

def extract_voice_frames(frames, voice_idx):
    off = VOICE_OFFSETS[voice_idx]
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

def delta_encode_frames(frames):
    if not frames:
        return bytearray()
    data = bytearray()
    length = min(len(frames), 255)
    data.append(length)
    for b in frames[0]:
        data.append(b)
    prev = list(frames[0])
    for frame in frames[1:length]:
        curr = list(frame)
        bitmask = 0
        changed = []
        for i in range(7):
            if curr[i] != prev[i]:
                bitmask |= (1 << i)
                changed.append(curr[i])
        data.append(bitmask)
        for b in changed:
            data.append(b)
        prev = curr
    return data

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
        if not frames:
            continue
        idx = pool.add(frames)
        length = min(len(frames), 255)
        note_sequence.append((idx, length))
    return note_sequence, pool

def encode_all_instruments(pool):
    data = bytearray()
    offsets = []
    for i in range(len(pool)):
        offsets.append(len(data))
        frames = pool.get_frames(i)
        encoded = delta_encode_frames(list(frames))
        data.extend(encoded)
    return data, offsets


# Zero-page layout:
# Voice 1: $80=np_lo $81=np_hi $82=fc $83=nl $84=ip_lo $85=ip_hi
# Voice 2: $86=np_lo $87=np_hi $88=fc $89=nl $8A=ip_lo $8B=ip_hi
# Voice 3: $8C=np_lo $8D=np_hi $8E=fc $8F=nl $90=ip_lo $91=ip_hi
# Filter:  $92=fp_lo $93=fp_hi $94=ffc_lo $95=ffc_hi
# Prev regs: $C0..$C6=v1, $C7..$CD=v2, $CE..$D4=v3

ZP_VOICE = [
    (0x80, 0x81, 0x82, 0x83, 0x84, 0x85),
    (0x86, 0x87, 0x88, 0x89, 0x8A, 0x8B),
    (0x8C, 0x8D, 0x8E, 0x8F, 0x90, 0x91),
]
ZP_PREV = [0xC0, 0xC7, 0xCE]


def generate_player():
    """
    Generate the 6502 player code.
    Structure per voice:
      1. Delta path (common case: fc < nl) -- comes FIRST, short path
      2. Note-load path (BCS forward jump from top)
    """
    lines = []
    L = lines.append

    L("        * = $1000")
    L("        jmp init")
    L("        jmp play")
    L("")

    # --- init ---
    L("init")
    L("        lda #$0F")
    L("        sta $D418")
    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi = ZP_VOICE[vi]
        prev = ZP_PREV[vi]
        L(f"        ; Voice {vi+1}")
        L(f"        lda #<ns{vi+1}")
        L(f"        sta ${np_lo:02X}")
        L(f"        lda #>ns{vi+1}")
        L(f"        sta ${np_hi:02X}")
        L(f"        lda #0")
        L(f"        sta ${nl:02X}")      # nl=0, fc=0 -> fc>=nl -> load first note
        L(f"        sta ${fc:02X}")
        for r in range(7):
            L(f"        sta ${prev+r:02X}")
    L("        ; Filter")
    L("        lda #<filtdata")
    L("        sta $92")
    L("        lda #>filtdata")
    L("        sta $93")
    L("        lda #0")
    L("        sta $94")
    L("        sta $95")
    L("        ; CIA1 timer A set to 18055 cycles for siddump sync")
    L("        lda #$87")
    L("        sta $DC04")
    L("        lda #$46")
    L("        sta $DC05")
    L("        lda #$11")
    L("        sta $DC0E")
    L("        rts")
    L("")

    # --- play ---
    L("play")
    L("        jsr vplay1")
    L("        jsr vplay2")
    L("        jsr vplay3")
    L("        jmp fplay")
    L("")

    # Generate each voice subroutine
    # Structure:
    #   vplayN:
    #     lda fc; cmp nl; bcs vNload   <- fc >= nl -> need new note (rare path)
    #   vNdelta:                        <- common delta path
    #     [read bitmask, update prev, write SID, inc fc, rts]
    #   vNload:                         <- note-load path (after delta, so bcs is short)
    #     [load note ptr, read inst first frame, fall through to write]
    #
    # Wait -- bcs vNload goes FORWARD past vNdelta.
    # vNdelta is ~80 bytes. bcs can reach +127. Should be OK.

    for vi in range(3):
        np_lo, np_hi, fc, nl, ip_lo, ip_hi = ZP_VOICE[vi]
        prev = ZP_PREV[vi]
        vbase = VOICE_BASES[vi]
        vn = f"v{vi+1}"

        L(f"; ---- Voice {vi+1} subroutine ----")
        L(f"vplay{vi+1}")
        L(f"        lda ${fc:02X}")
        L(f"        cmp ${nl:02X}")
        L(f"        bcc {vn}delta")     # fc < nl: go to delta (short forward branch)
        L(f"        jmp {vn}load")      # fc >= nl: need new note

        # === Delta path (common case) ===
        L(f"{vn}delta")
        L(f"        ldy #0")
        L(f"        lda (${ip_lo:02X}),y")
        L(f"        tax")               # X = bitmask
        L(f"        inc ${ip_lo:02X}")
        L(f"        bne {vn}dm0")
        L(f"        inc ${ip_hi:02X}")
        L(f"{vn}dm0")
        for r in range(7):
            mask = 1 << r
            L(f"        txa")
            L(f"        and #${mask:02X}")
            L(f"        beq {vn}ds{r}")
            L(f"        ldy #0")
            L(f"        lda (${ip_lo:02X}),y")
            L(f"        sta ${prev+r:02X}")
            L(f"        inc ${ip_lo:02X}")
            L(f"        bne {vn}ds{r}")
            L(f"        inc ${ip_hi:02X}")
            L(f"{vn}ds{r}")

        # === Write SID ===
        L(f"{vn}write")
        L(f"        lda ${prev+4:02X}")
        L(f"        sta ${vbase+4:04X}")    # CT
        L(f"        lda ${prev+0:02X}")
        L(f"        sta ${vbase+0:04X}")    # FL
        L(f"        lda ${prev+1:02X}")
        L(f"        sta ${vbase+1:04X}")    # FH
        L(f"        lda ${prev+2:02X}")
        L(f"        sta ${vbase+2:04X}")    # PL
        L(f"        lda ${prev+3:02X}")
        L(f"        sta ${vbase+3:04X}")    # PH
        L(f"        lda ${prev+5:02X}")
        L(f"        sta ${vbase+5:04X}")    # AD
        L(f"        lda ${prev+6:02X}")
        L(f"        sta ${vbase+6:04X}")    # SR
        L(f"        inc ${fc:02X}")
        L(f"        rts")

        # === Note-load path ===
        L(f"{vn}load")
        L(f"        ldy #0")
        L(f"        lda (${np_lo:02X}),y")
        L(f"        cmp #$FF")
        L(f"        bne {vn}ln0")
        L(f"        rts")                   # song done
        L(f"{vn}ln0")
        L(f"        sta ${nl:02X}")          # store length
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
        # ip now points to instrument: [length, f0_r0..f0_r6, ...]
        # Skip the length byte
        L(f"        inc ${ip_lo:02X}")
        L(f"        bne {vn}lf0")
        L(f"        inc ${ip_hi:02X}")
        # Read 7 full bytes -> prev[]
        L(f"{vn}lf0")
        for r in range(7):
            L(f"        ldy #0")
            L(f"        lda (${ip_lo:02X}),y")
            L(f"        sta ${prev+r:02X}")
            L(f"        inc ${ip_lo:02X}")
            L(f"        bne {vn}lf{r+1}")
            L(f"        inc ${ip_hi:02X}")
            L(f"{vn}lf{r+1}")
        # Fall through to write SID
        L(f"        jmp {vn}write")
        L("")

    # === Filter subroutine ===
    L("; ---- Filter subroutine ----")
    L("fplay")
    L("        lda $95")
    L("        cmp #$0C")
    L("        bcs fpdone")
    L("        ldy #0")
    L("        lda ($92),y")
    L("        sta $D415")
    L("        iny")
    L("        lda ($92),y")
    L("        sta $D416")
    L("        iny")
    L("        lda ($92),y")
    L("        sta $D417")
    L("        iny")
    L("        lda ($92),y")
    L("        sta $D418")
    L("        clc")
    L("        lda $92")
    L("        adc #4")
    L("        sta $92")
    L("        bcc fpnc")
    L("        inc $93")
    L("fpnc")
    L("        inc $94")
    L("        bne fpdone")
    L("        inc $95")
    L("fpdone")
    L("        rts")
    L("")

    return lines


def get_player_code_size():
    """
    Assemble just the player code stubs (with dummy ns/filtdata references)
    to measure actual player code size.
    """
    asm_lines = generate_player()
    # Append dummy data labels at the end
    asm_lines.append("ns1  .byte $FF")
    asm_lines.append("ns2  .byte $FF")
    asm_lines.append("ns3  .byte $FF")
    asm_lines.append("filtdata  .byte $FF")
    asm_text = "\n".join(asm_lines)
    tmp_asm = "/tmp/hg17_probe.s"
    tmp_bin = "/tmp/hg17_probe.bin"
    with open(tmp_asm, 'w') as f:
        f.write(asm_text)
    result = subprocess.run([XA, "-o", tmp_bin, tmp_asm], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Probe assembly failed: {result.stderr}")
    size = os.path.getsize(tmp_bin)
    return size  # size in bytes from $1000


def generate_asm(frames):
    v_regs = [extract_voice_frames(frames, i) for i in range(3)]
    filt_regs = extract_filter_frames(frames)

    print("Building note sequences and instrument pools...")
    voice_seqs = []
    voice_pools = []
    for vi in range(3):
        seq, pool = build_voice_data(v_regs[vi])
        voice_seqs.append(seq)
        voice_pools.append(pool)
        print(f"  Voice {vi+1}: {len(seq)} notes, {len(pool)} unique instruments")

    filter_data = bytearray()
    for fr in filt_regs:
        for b in fr:
            filter_data.append(b)

    # Measure actual player code size
    print("  Measuring player code size...")
    player_size = get_player_code_size()
    # -3 for the 3 dummy ns1/ns2/ns3/filtdata bytes (we appended 4 * ".byte $FF" = 4 bytes but
    # ns1 starts after player, so player ends at $1000 + player_size - 4)
    # Actually: player code = first "ns1" label offset = player_size - 4 (4 dummy bytes)
    player_code_end = 0x1000 + player_size - 4  # subtract 4 dummy bytes
    # But we need to be more careful: the probe has 4 * 1-byte data appended
    # so player code size = total_size - 4
    # Let's use player_code_end as the start of instrument data
    INST_BASE = player_code_end
    print(f"  Player code: {player_size - 4} bytes ($1000..${INST_BASE-1:04X})")

    inst_data_list = []
    inst_abs_offsets_list = []
    running = INST_BASE
    for vi in range(3):
        data, rel_offs = encode_all_instruments(voice_pools[vi])
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
    print(f"  Inst data (delta): {total_inst} bytes @ ${INST_BASE:04X}")
    print(f"  Note streams: {total_notes} bytes @ ${note_stream_addrs[0]:04X}")
    print(f"  Filter data: {len(filter_data)} bytes @ ${filter_addr:04X}")
    print(f"  End address: ${end_addr:04X}")
    if end_addr > 0xFFFF:
        print(f"  WARNING: Exceeds 64KB!")

    # Generate final assembly (player code + inline data, no * = gaps)
    asm = generate_player()

    # Data immediately follows player code (no * = addr needed)
    for vi in range(3):
        data = inst_data_list[vi]
        asm.append(f"; V{vi+1} instruments ({len(data)} bytes)")
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
            chunk = flat[i:i+15]
            asm.append(f"        .byte {','.join(f'${b:02X}' for b in chunk)}")
        asm.append("")

    asm.append("; Filter data")
    asm.append("filtdata")
    flat = list(filter_data)
    for i in range(0, len(flat), 16):
        chunk = flat[i:i+16]
        asm.append(f"        .byte {','.join(f'${b:02X}' for b in chunk)}")

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
    struct.pack_into('>I', hdr, 18, 1)   # CIA timer for subtune 1
    hdr[22:54] = (b'Commando (HG17)\x00' + bytes(32))[:32]
    hdr[54:86] = (b'Rob Hubbard\x00' + bytes(32))[:32]
    hdr[86:118] = (b'1985 Elite\x00' + bytes(32))[:32]
    return bytes(hdr) + bytes(bin_data)


def main():
    print("=== Commando HG17 generator ===")

    print("\n[1] Capturing ground truth...")
    frames = capture_ground_truth(60)

    print("\n[2] Generating assembly...")
    asm_text = generate_asm(frames)

    with open(OUT_ASM, 'w') as f:
        f.write(asm_text)
    print(f"  Written: {OUT_ASM}")

    print("\n[3] Assembling...")
    result = subprocess.run(
        [XA, "-o", OUT_BIN, OUT_ASM],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("ASSEMBLY FAILED:")
        print(result.stderr[:5000])
        sys.exit(1)
    sz = os.path.getsize(OUT_BIN)
    print(f"  OK: {sz} bytes")

    print("\n[4] Building PSID...")
    with open(OUT_BIN, 'rb') as f:
        bin_data = f.read()
    psid = build_psid(bin_data, 0x1000)
    with open(OUT_SID, 'wb') as f:
        f.write(psid)
    print(f"  Written: {OUT_SID} ({len(psid)} bytes)")

    print("\n[5] Comparing...")
    sys.path.insert(0, '/home/jtr/sidfinity/src')
    from sid_compare import compare_sids_tolerant
    r = compare_sids_tolerant(ORIG_SID, OUT_SID, 60)
    if r is None:
        print("  FAIL: compare returned None")
        raw = subprocess.run(
            [SIDDUMP, OUT_SID, "--duration=3", "--raw"],
            capture_output=True, text=True
        )
        print(f"  siddump lines: {len(raw.stdout.strip().split(chr(10)))}")
        print(f"  siddump stderr: {raw.stderr[:500]}")
    else:
        print(f"  Grade={r['grade']} Score={r['score']:.1f}")
        for k, v in sorted(r.items()):
            if isinstance(v, (int, float)) and k not in ['score']:
                print(f"    {k}: {v}")


if __name__ == '__main__':
    main()
