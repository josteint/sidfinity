#!/usr/bin/env python3
"""
build_commando_hg4.py — Delta-encoded register stream player for Commando.

  1. Capture 1500 frames of ground truth via py65
  2. Delta-encode: frame 0 = all 21 regs; subsequent = 3-byte bitmask + changed values
  3. Generate xa65 assembly for a 6502 delta-player
  4. Assemble with xa65, build PSID, verify

Output: demo/hubbard/Commando_hg4.sid
"""

import sys, os, struct, subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools', 'py65_lib'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'src'))

from py65.devices.mpu6502 import MPU

COMMANDO_SID = os.path.join(REPO_ROOT, 'data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid')
OUTPUT_SID   = os.path.join(REPO_ROOT, 'demo/hubbard/Commando_hg4.sid')
XA65         = os.path.join(REPO_ROOT, 'tools/xa65/xa/xa')

SID_BASE  = 0xD400
NUM_REGS  = 21      # $D400-$D414
NUM_FRAMES = 1500


# ── PSID parsing ─────────────────────────────────────────────────────────────

def parse_psid(path):
    data = open(path, 'rb').read()
    data_offset = struct.unpack_from('>H', data, 6)[0]
    load_addr   = struct.unpack_from('>H', data, 8)[0]
    init_addr   = struct.unpack_from('>H', data, 10)[0]
    play_addr   = struct.unpack_from('>H', data, 12)[0]
    binary = data[data_offset:]
    if load_addr == 0:
        load_addr = struct.unpack_from('<H', binary, 0)[0]
        binary = binary[2:]
    return load_addr, init_addr, play_addr, binary


# ── py65 helpers ─────────────────────────────────────────────────────────────

def call_sub(cpu, addr, a=0, x=0, y=0, max_steps=3_000_000):
    cpu.a = a & 0xFF
    cpu.x = x & 0xFF
    cpu.y = y & 0xFF
    sentinel = 0xFFF0
    ret = sentinel - 1
    cpu.memory[0x0100 + cpu.sp] = (ret >> 8) & 0xFF
    cpu.sp = (cpu.sp - 1) & 0xFF
    cpu.memory[0x0100 + cpu.sp] = ret & 0xFF
    cpu.sp = (cpu.sp - 1) & 0xFF
    cpu.memory[sentinel] = 0x60   # RTS
    cpu.pc = addr
    for _ in range(max_steps):
        if cpu.pc == sentinel:
            return
        cpu.step()
    raise RuntimeError(f'Sub ${addr:04X} did not return (PC=${cpu.pc:04X})')


# ── Step 1: capture ground truth ─────────────────────────────────────────────

def capture_frames(n):
    print(f'[1] Capturing {n} frames via py65...')
    load, init, play, binary = parse_psid(COMMANDO_SID)
    print(f'    Load=${load:04X} Init=${init:04X} Play=${play:04X} Code={len(binary)}B')
    cpu = MPU()
    for i, b in enumerate(binary):
        cpu.memory[load + i] = b
    call_sub(cpu, init, a=0)
    frames = []
    for _ in range(n):
        call_sub(cpu, play)
        frames.append([cpu.memory[SID_BASE + r] for r in range(NUM_REGS)])
    print(f'    Done. {len(frames)} frames captured.')
    return frames


# ── Step 2: delta encode ──────────────────────────────────────────────────────

def delta_encode(frames):
    print(f'[2] Delta-encoding...')
    data = bytearray()
    data.extend(frames[0])          # frame 0: all 21 bytes raw
    prev = list(frames[0])
    total_ch = 0
    for f in range(1, len(frames)):
        cur = frames[f]
        changed = [i for i in range(NUM_REGS) if cur[i] != prev[i]]
        total_ch += len(changed)
        mask = sum(1 << i for i in changed)
        data += bytes([mask & 0xFF, (mask >> 8) & 0xFF, (mask >> 16) & 0xFF])
        for i in changed:
            data.append(cur[i])
        prev = list(cur)
    raw = len(frames) * NUM_REGS
    print(f'    Raw={raw}B  Encoded={len(data)}B  Ratio={100*len(data)/raw:.1f}%')
    print(f'    Avg changes/frame: {total_ch / (len(frames)-1):.2f}')
    return data


# ── Step 3: generate assembly ─────────────────────────────────────────────────

def make_asm(encoded, num_frames):
    """
    Generate xa65 assembly for the delta player.

    Memory layout (player at $1000):
      $1000 = INIT
      ~$1030 = PLAY_SKIP (jump target for range check)
      ~$1040 = PLAY
      after code = STREAM data

    ZP: $F0=MASK0, $F1=MASK1, $F2=MASK2, $F3/$F4=PTR_LO/HI, $F5/$F6=frame counter

    The unrolled register-write block uses lsr to shift through each mask byte.
    Each bit: lsr; bcc skip; lda (ptr),y; sta SID+r; iny; skip:
    """
    nfhi = (num_frames >> 8) & 0xFF
    nflo = num_frames & 0xFF

    # Build unrolled register block.
    #
    # Key constraint: after 'lda (PTR_LO),y / sta $D400+r / iny', A holds
    # the written value, not the mask.  We must restore the mask to A before
    # the next lsr.  We use SCRATCH ($F7) to keep the remaining shifted mask.
    #
    # Pattern per bit i within a mask byte:
    #   lsr SCRATCH            ; shift bit into carry, update SCRATCH
    #   bcc SKnn               ; if C=0, bit not set, skip
    #   lda (PTR_LO),y         ; read next stream byte
    #   sta $D400+r            ; write to SID register r
    #   iny
    # SKnn:
    #
    # This uses SCRATCH as the shift register (1 extra ZP byte).
    lines = []
    SCRATCH = 'SCRATCH'   # ZP alias defined in header
    for mask_byte, label, start_r, count in [
            ('MASK0', 'M0', 0, 8),
            ('MASK1', 'M1', 8, 8),
            ('MASK2', 'M2', 16, 5)]:
        # Load mask byte into SCRATCH at start of each group
        lines.append(f'        lda {mask_byte}')
        lines.append(f'        sta SCRATCH')
        for i in range(count):
            r = start_r + i
            sk = f'SK{r:02d}'
            lines.append(f'        lsr SCRATCH')   # shift bit into C, preserve SCRATCH
            lines.append(f'        bcc {sk}')
            lines.append(f'        lda (PTR_LO),y')
            lines.append(f'        sta $D400+{r}')
            lines.append(f'        iny')
            lines.append(f'{sk}:')
    reg_block = '\n'.join(lines)

    # Build STREAM data
    hex_rows = []
    row = []
    for i, b in enumerate(encoded):
        row.append(f'${b:02X}')
        if len(row) == 16:
            hex_rows.append('        .byte ' + ','.join(row))
            row = []
    if row:
        hex_rows.append('        .byte ' + ','.join(row))
    stream_hex = '\n'.join(hex_rows)

    asm = f"""\
; Commando delta-player (hg4) — {num_frames} frames, {len(encoded)} bytes stream
; Rob Hubbard / 1985 Elite
; Generated by build_commando_hg4.py

PTR_LO  = $F3
PTR_HI  = $F4
FRCNT_L = $F5
FRCNT_H = $F6
MASK0   = $F0
MASK1   = $F1
MASK2   = $F2
SCRATCH = $F7
NFHI    = ${nfhi:02X}
NFLO    = ${nflo:02X}

        *= $1000

; ── INIT ─────────────────────────────────────────────────────────────────────
INIT:
        lda #<STREAM
        sta PTR_LO
        lda #>STREAM
        sta PTR_HI
        lda #0
        sta FRCNT_L
        sta FRCNT_H

        ; Write frame 0 (21 bytes directly)
        ldy #0
ILOOP:
        lda (PTR_LO),y
        sta $D400,y
        iny
        cpy #21
        bne ILOOP

        ; ptr += 21
        clc
        lda PTR_LO
        adc #21
        sta PTR_LO
        bcc IDONE
        inc PTR_HI
IDONE:
        lda #1
        sta FRCNT_L
        lda #0
        sta FRCNT_H
        rts

; ── PLAY ─────────────────────────────────────────────────────────────────────
; Check done first (uses jmp to avoid branch-out-of-range across reg block)
PLAY:
        lda FRCNT_H
        cmp #NFHI
        bcc PLAY_GO
        bne PLAY_DONE
        lda FRCNT_L
        cmp #NFLO
        bcc PLAY_GO
PLAY_DONE:
        rts

PLAY_GO:
        ; Read 3-byte bitmask at (PTR),0..2
        ldy #0
        lda (PTR_LO),y
        sta MASK0
        iny
        lda (PTR_LO),y
        sta MASK1
        iny
        lda (PTR_LO),y
        sta MASK2
        iny                     ; Y=3 -> first payload byte

        ; Apply changed registers (unrolled, 21 bits)
{reg_block}

        ; Advance data pointer by Y
        tya
        clc
        adc PTR_LO
        sta PTR_LO
        bcc INC_FC
        inc PTR_HI
INC_FC:
        inc FRCNT_L
        bne PLAY_RTS
        inc FRCNT_H
PLAY_RTS:
        rts

; ── Encoded stream ({len(encoded)} bytes) ──────────────────────────────────────
STREAM:
{stream_hex}

        .end
"""
    return asm


# ── Step 4: assemble ──────────────────────────────────────────────────────────

def assemble(asm_text, asm_path, prg_path):
    with open(asm_path, 'w') as f:
        f.write(asm_text)
    r = subprocess.run([XA65, '-o', prg_path, asm_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f'xa65 ERROR:\n{r.stderr}')
        return False
    sz = os.path.getsize(prg_path)
    print(f'    Assembled OK: {sz} bytes')
    return True


# ── Step 4b: find PLAY address by disassembling the output ───────────────────

def find_play_addr(asm_text):
    """
    Assemble with -l listing, parse to find PLAY label address.
    xa65 listing format: each line has hex address in first field.
    """
    asm_path = '/tmp/commando_hg4_scan.asm'
    prg_path = '/tmp/commando_hg4_scan.prg'
    lst_path = '/tmp/commando_hg4_scan.lst'
    with open(asm_path, 'w') as f:
        f.write(asm_text)
    r = subprocess.run([XA65, '-l', lst_path, '-o', prg_path, asm_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f'xa65 listing error: {r.stderr[:300]}')
        return None, None

    labels = {}
    try:
        with open(lst_path) as f:
            content = f.read()
        # xa65 -l listing format: "LABEL, 0xADDR, 0, 0x0000"
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                name = parts[0]
                val_str = parts[1]
                if val_str.startswith('0x') or val_str.startswith('0X'):
                    try:
                        labels[name] = int(val_str, 16)
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass

    return labels.get('INIT'), labels.get('PLAY')


# ── Step 5: build PSID ────────────────────────────────────────────────────────

def build_psid(prg_path, out_path, load_addr, init_addr, play_addr):
    binary = open(prg_path, 'rb').read()

    def pad32(s):
        b = s.encode('ascii', errors='replace')[:31] + b'\x00'
        return b + bytes(32 - len(b))

    # PSID v2 header: exactly 124 bytes
    # magic(4) version(2) dataOffset(2) load(2) init(2) play(2)
    # songs(2) start(2) speed(4)                          = 22
    # title(32) author(32) copyright(32)                  = 96
    # flags(2) startPage(1) pageLength(1) secondSID(2)    =  6
    # Total = 124
    hdr = bytearray()
    hdr += b'PSID'
    hdr += struct.pack('>H', 2)           # version
    hdr += struct.pack('>H', 124)         # data offset
    hdr += struct.pack('>H', load_addr)   # load
    hdr += struct.pack('>H', init_addr)   # init
    hdr += struct.pack('>H', play_addr)   # play
    hdr += struct.pack('>H', 1)           # songs
    hdr += struct.pack('>H', 1)           # start
    hdr += struct.pack('>I', 0)           # speed (4 bytes)
    hdr += pad32('Commando')              # title  (32B)
    hdr += pad32('Rob Hubbard')           # author (32B)
    hdr += pad32('1985 Elite')            # copyright (32B)
    hdr += struct.pack('>H', 0)           # flags (2B)
    hdr += b'\x00'                        # startPage (1B)
    hdr += b'\x00'                        # pageLength (1B)
    hdr += struct.pack('>H', 0)           # secondSIDAddress (2B)

    assert len(hdr) == 124, f'header={len(hdr)}'
    with open(out_path, 'wb') as f:
        f.write(hdr)
        f.write(binary)
    sz = len(hdr) + len(binary)
    print(f'    PSID written: {sz} bytes -> {out_path}')
    return sz


# ── Step 6: verify ────────────────────────────────────────────────────────────

def verify(sid_path, ground_truth, n, init_addr_override=None, play_addr_override=None):
    load, init_a, play_a, binary = parse_psid(sid_path)
    init_addr = init_addr_override or init_a
    play_addr = play_addr_override or play_a
    print(f'    Verifying: Load=${load:04X} Init=${init_addr:04X} Play=${play_addr:04X}')

    cpu = MPU()
    for i, b in enumerate(binary):
        cpu.memory[load + i] = b
    call_sub(cpu, init_addr, a=0)

    # After init, SID regs should match frame 0
    regs_after_init = [cpu.memory[SID_BASE + r] for r in range(NUM_REGS)]
    frame0_match = regs_after_init == ground_truth[0]
    print(f'    Frame 0 (after init): {"OK" if frame0_match else "MISMATCH"}')
    if not frame0_match:
        diffs = [(r, regs_after_init[r], ground_truth[0][r])
                 for r in range(NUM_REGS) if regs_after_init[r] != ground_truth[0][r]]
        print(f'      Diffs: {diffs[:8]}')

    mismatches = 0
    for f in range(n):
        call_sub(cpu, play_addr)
        got  = [cpu.memory[SID_BASE + r] for r in range(NUM_REGS)]
        want = ground_truth[f + 1]
        if got != want:
            mismatches += 1
            if mismatches <= 5:
                diffs = [(r, got[r], want[r]) for r in range(NUM_REGS) if got[r] != want[r]]
                print(f'    Frame {f+1}: {len(diffs)} diffs: {diffs[:5]}')

    pct = 100.0 * (n - mismatches) / n
    print(f'    Exact frame match: {n - mismatches}/{n} ({pct:.1f}%)')
    return mismatches == 0 and frame0_match


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    frames  = capture_frames(NUM_FRAMES)
    encoded = delta_encode(frames)

    print(f'[3] Generating assembly...')
    asm = make_asm(encoded, NUM_FRAMES)

    asm_path = '/tmp/commando_hg4.asm'
    prg_path = '/tmp/commando_hg4.prg'

    # Dry-run to find label addresses
    print(f'[4a] Finding label addresses...')
    init_addr, play_addr = find_play_addr(asm)
    init_str = f'${init_addr:04X}' if init_addr is not None else '????'
    play_str = f'${play_addr:04X}' if play_addr is not None else '????'
    print(f'     INIT={init_str}  PLAY={play_str}')

    if init_addr is None:
        init_addr = 0x1000
    if play_addr is None:
        # Fallback: we know INIT is exactly N bytes; estimate from the listing
        print('     WARNING: PLAY address unknown, defaulting to $1040')
        play_addr = 0x1040

    # Final assembly
    print(f'[4b] Final assembly...')
    if not assemble(asm, asm_path, prg_path):
        sys.exit(1)

    # Pack PSID
    print(f'[5] Building PSID...')
    os.makedirs(os.path.dirname(OUTPUT_SID), exist_ok=True)
    total = build_psid(prg_path, OUTPUT_SID, 0x1000, init_addr, play_addr)

    # Verify
    print(f'[6] Verifying (first 300 frames)...')
    ok = verify(OUTPUT_SID, frames, min(300, NUM_FRAMES - 1))

    orig = os.path.getsize(COMMANDO_SID)
    print(f'\n=== Summary ===')
    print(f'Original:      {orig} bytes')
    print(f'Delta player:  {total} bytes ({100*total/orig:.1f}% of original)')
    print(f'Stream:        {len(encoded)} bytes ({NUM_FRAMES} frames)')
    print(f'Output:        {OUTPUT_SID}')
    print(f'Result:        {"PASS" if ok else "FAIL"}')


if __name__ == '__main__':
    main()
