#!/usr/bin/env python3
"""
build_commando_hg18.py — Simplest possible flat register-stream player for Commando.

Approach:
  No instruments. No notes. No compression. Just a flat array of register values.

  Per voice: flat array of 7-byte frames (freq_lo, freq_hi, pw_lo, pw_hi, wave, AD, SR).
  Three independent streams for the three SID voices.

  Player (~80 bytes):
    init: set volume, set stream pointers
    play: read 7 bytes from each stream into SID registers, advance each pointer by 7

  Data: 1500 frames x 7 bytes x 3 voices = 31,500 bytes

Output: demo/hubbard/Commando_hg18.sid
"""

import sys
import os
import struct
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools', 'py65_lib'))

from py65.devices.mpu6502 import MPU

COMMANDO_SID = os.path.join(REPO_ROOT, 'data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid')
OUTPUT_SID   = os.path.join(REPO_ROOT, 'demo/hubbard/Commando_hg18.sid')
XA65         = os.path.join(REPO_ROOT, 'tools/xa65/xa/xa')

SID_BASE  = 0xD400
NUM_REGS  = 21   # 7 regs x 3 voices
NUM_FRAMES = 1500

# Voice register layout in SID: 7 regs per voice
# Voice 1: $D400-$D406 (freq_lo, freq_hi, pw_lo, pw_hi, wave, AD, SR)
# Voice 2: $D407-$D40D
# Voice 3: $D40E-$D414


def parse_psid(path):
    with open(path, 'rb') as f:
        data = f.read()
    data_offset = struct.unpack_from('>H', data, 6)[0]
    load_addr   = struct.unpack_from('>H', data, 8)[0]
    init_addr   = struct.unpack_from('>H', data, 10)[0]
    play_addr   = struct.unpack_from('>H', data, 12)[0]
    binary = data[data_offset:]
    if load_addr == 0:
        load_addr = struct.unpack_from('<H', binary, 0)[0]
        binary = binary[2:]
    return load_addr, init_addr, play_addr, binary


def call_subroutine(cpu, addr, a=0, x=0, y=0, max_steps=2_000_000):
    """Run a 6502 subroutine until RTS returns to sentinel $FFF0."""
    cpu.a = a & 0xFF
    cpu.x = x & 0xFF
    cpu.y = y & 0xFF
    sentinel = 0xFFF0
    ret_addr = sentinel - 1
    cpu.memory[0x0100 + cpu.sp] = (ret_addr >> 8) & 0xFF
    cpu.sp = (cpu.sp - 1) & 0xFF
    cpu.memory[0x0100 + cpu.sp] = ret_addr & 0xFF
    cpu.sp = (cpu.sp - 1) & 0xFF
    cpu.memory[sentinel] = 0x60  # RTS at sentinel
    cpu.pc = addr
    steps = 0
    while steps < max_steps:
        if cpu.pc == sentinel:
            return steps
        cpu.step()
        steps += 1
    raise RuntimeError(f'Subroutine at ${addr:04X} did not return (PC=${cpu.pc:04X})')


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Capture NUM_FRAMES ground truth frames from original SID
# ─────────────────────────────────────────────────────────────────────────────

def capture_frames():
    print(f'[1] Capturing {NUM_FRAMES} frames from Commando.sid via py65...')
    load_addr, init_addr, play_addr, binary = parse_psid(COMMANDO_SID)
    print(f'    Load=${load_addr:04X}, Init=${init_addr:04X}, Play=${play_addr:04X}, Binary={len(binary)} bytes')

    cpu = MPU()
    for i, b in enumerate(binary):
        cpu.memory[load_addr + i] = b

    call_subroutine(cpu, init_addr, a=0)
    print('    Init done')

    frames = []
    for f in range(NUM_FRAMES):
        call_subroutine(cpu, play_addr)
        regs = [cpu.memory[SID_BASE + r] for r in range(NUM_REGS)]
        frames.append(regs)
        if f % 200 == 0:
            print(f'    Frame {f}/{NUM_FRAMES}...')

    print(f'    Captured {len(frames)} frames')
    return frames


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Extract per-voice register streams
#
# Each frame has 21 registers: [v1_regs(7), v2_regs(7), v3_regs(7)]
# We split into 3 flat arrays of 7-byte frames.
# ─────────────────────────────────────────────────────────────────────────────

def extract_voice_streams(frames):
    """
    Returns (v1_data, v2_data, v3_data) as flat bytearrays.
    v1_data: frames[0][0:7] + frames[1][0:7] + ...
    v2_data: frames[0][7:14] + ...
    v3_data: frames[0][14:21] + ...
    """
    print(f'[2] Extracting per-voice register streams...')
    v1 = bytearray()
    v2 = bytearray()
    v3 = bytearray()
    for regs in frames:
        v1.extend(regs[0:7])
        v2.extend(regs[7:14])
        v3.extend(regs[14:21])
    print(f'    V1: {len(v1)} bytes ({NUM_FRAMES} frames x 7)')
    print(f'    V2: {len(v2)} bytes')
    print(f'    V3: {len(v3)} bytes')
    total = len(v1) + len(v2) + len(v3)
    print(f'    Total data: {total} bytes ({total/1024:.1f} KB)')
    return v1, v2, v3


# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Generate xa65 assembly
#
# Memory layout:
#   $1000: INIT entry point
#   $1003: PLAY entry point
#   $1006+: player code
#   After code: V1DATA, V2DATA, V3DATA (flat 7-byte frames)
#
# ZP usage:
#   $80/$81: V1 stream pointer (lo/hi)
#   $82/$83: V2 stream pointer
#   $84/$85: V3 stream pointer
#
# INIT:
#   lda #$0F: sta $D418  (max volume)
#   set stream pointers
#   rts
#
# PLAY:
#   Voice 1: ldy #0, read 7 bytes -> $D400-$D406, advance ptr by 7
#   Voice 2: same -> $D407-$D40D
#   Voice 3: same -> $D40E-$D414
#   rts
# ─────────────────────────────────────────────────────────────────────────────

def bytes_to_asm(data, label):
    """Convert bytes to xa65 .byte directives with a label."""
    lines = [f'{label}:']
    row = []
    for i, b in enumerate(data):
        row.append(f'${b:02X}')
        if len(row) == 16:
            lines.append('        .byte ' + ','.join(row))
            row = []
    if row:
        lines.append('        .byte ' + ','.join(row))
    return '\n'.join(lines)


def sep(text):
    """ASCII-safe section separator comment for xa65."""
    return f'; --- {text} ---'


def generate_asm(v1, v2, v3):
    print(f'[3] Generating xa65 assembly...')

    v1_asm = bytes_to_asm(v1, 'V1DATA')
    v2_asm = bytes_to_asm(v2, 'V2DATA')
    v3_asm = bytes_to_asm(v3, 'V3DATA')

    asm = f"""; Commando flat-stream player (hg18) - auto-generated
; Rob Hubbard / Commando (1985)
; Simplest possible, 3 flat arrays of 7-byte frames, no compression.
; {NUM_FRAMES} frames x 7 bytes x 3 voices = {NUM_FRAMES*7*3} bytes of data

; Zero-page stream pointers
P1L = $80
P1H = $81
P2L = $82
P2H = $83
P3L = $84
P3H = $85

SID = $D400

        *= $1000

; Initialization - called once with subtune in accumulator
INIT:
        lda #$0F
        sta $D418           ; max volume

        lda #<V1DATA
        sta P1L
        lda #>V1DATA
        sta P1H

        lda #<V2DATA
        sta P2L
        lda #>V2DATA
        sta P2H

        lda #<V3DATA
        sta P3L
        lda #>V3DATA
        sta P3H

        rts

; Play routine - called once per frame at ~50Hz
PLAY:
        ; Voice 1, 7 bytes into $D400-$D406
        ldy #0
        lda (P1L),y
        sta SID+0
        iny
        lda (P1L),y
        sta SID+1
        iny
        lda (P1L),y
        sta SID+2
        iny
        lda (P1L),y
        sta SID+3
        iny
        lda (P1L),y
        sta SID+4
        iny
        lda (P1L),y
        sta SID+5
        iny
        lda (P1L),y
        sta SID+6

        ; advance V1 pointer by 7
        clc
        lda P1L
        adc #7
        sta P1L
        bcc S1
        inc P1H
S1:
        ; Voice 2, 7 bytes into $D407-$D40D
        ldy #0
        lda (P2L),y
        sta SID+7
        iny
        lda (P2L),y
        sta SID+8
        iny
        lda (P2L),y
        sta SID+9
        iny
        lda (P2L),y
        sta SID+10
        iny
        lda (P2L),y
        sta SID+11
        iny
        lda (P2L),y
        sta SID+12
        iny
        lda (P2L),y
        sta SID+13

        ; advance V2 pointer by 7
        clc
        lda P2L
        adc #7
        sta P2L
        bcc S2
        inc P2H
S2:
        ; Voice 3, 7 bytes into $D40E-$D414
        ldy #0
        lda (P3L),y
        sta SID+14
        iny
        lda (P3L),y
        sta SID+15
        iny
        lda (P3L),y
        sta SID+16
        iny
        lda (P3L),y
        sta SID+17
        iny
        lda (P3L),y
        sta SID+18
        iny
        lda (P3L),y
        sta SID+19
        iny
        lda (P3L),y
        sta SID+20

        ; advance V3 pointer by 7
        clc
        lda P3L
        adc #7
        sta P3L
        bcc S3
        inc P3H
S3:
        rts

; Data - {NUM_FRAMES} frames x 7 bytes per voice
{v1_asm}

{v2_asm}

{v3_asm}

        .end
"""
    return asm


# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Assemble with xa65 and find label addresses
# ─────────────────────────────────────────────────────────────────────────────

def assemble_and_find_labels(asm_text, asm_path, prg_path, lbl_path):
    with open(asm_path, 'w') as f:
        f.write(asm_text)

    # Assemble with -l labellist for label addresses
    # Note: xa65 -l format: NAME, 0xADDR, flags, 0x0000
    r = subprocess.run(
        [XA65, '-o', prg_path, '-l', lbl_path, asm_path],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f'xa65 FAILED:\n{r.stderr}')
        return None, {}

    labels = {}
    try:
        with open(lbl_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                # Format: NAME, 0xADDR, segment, 0x0000
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 2:
                    name = parts[0]
                    val_str = parts[1].strip()
                    try:
                        labels[name] = int(val_str, 16)
                    except ValueError:
                        pass
    except FileNotFoundError:
        print(f'    Warning: label file not found: {lbl_path}')

    size = os.path.getsize(prg_path)
    print(f'    Assembled: {size} bytes')
    print(f'    Labels: INIT=${labels.get("INIT", 0):04X}, PLAY=${labels.get("PLAY", 0):04X}')
    return size, labels


# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Build PSID file
# ─────────────────────────────────────────────────────────────────────────────

def build_psid(prg_path, output_path, init_addr, play_addr, load_addr=0x1000):
    with open(prg_path, 'rb') as f:
        binary = f.read()

    title     = b'Commando' + bytes(32 - 8)
    author    = b'Rob Hubbard' + bytes(32 - 11)
    copyright = b'1985 Elite Systems' + bytes(32 - 18)

    header = bytearray()
    header += b'PSID'
    header += struct.pack('>H', 2)           # version 2
    header += struct.pack('>H', 124)         # data offset
    header += struct.pack('>H', 0)           # load addr = 0 (embedded in data)
    header += struct.pack('>H', init_addr)
    header += struct.pack('>H', play_addr)
    header += struct.pack('>H', 1)           # 1 song
    header += struct.pack('>H', 1)           # default song 1
    header += struct.pack('>I', 0)           # speed (VBI)
    header += title
    header += author
    header += copyright
    # v2 extra: flags, startPage, pageLength, reserved
    header += struct.pack('>H', 0)
    header += b'\x00'
    header += b'\x00'
    header += struct.pack('>H', 0)

    assert len(header) == 124, f'Header is {len(header)} bytes, expected 124'

    # Embed load address as little-endian prefix before binary (PSID convention when load=0)
    load_prefix = struct.pack('<H', load_addr)

    with open(output_path, 'wb') as f:
        f.write(header)
        f.write(load_prefix)
        f.write(binary)

    total = len(header) + 2 + len(binary)
    print(f'    PSID: {total} bytes -> {output_path}')
    return total


# ─────────────────────────────────────────────────────────────────────────────
# Step 6: Verify — emulate the built SID and compare register output
# ─────────────────────────────────────────────────────────────────────────────

def verify(sid_path, ground_truth, num_check=200):
    print(f'[6] Verifying {num_check} frames against ground truth...')
    load_addr, init_addr, play_addr, binary = parse_psid(sid_path)
    print(f'    Load=${load_addr:04X}, Init=${init_addr:04X}, Play=${play_addr:04X}')

    cpu = MPU()
    for i, b in enumerate(binary):
        cpu.memory[load_addr + i] = b

    call_subroutine(cpu, init_addr, a=0)

    mismatches = 0
    for f in range(num_check):
        call_subroutine(cpu, play_addr)
        got  = [cpu.memory[SID_BASE + r] for r in range(NUM_REGS)]
        want = ground_truth[f]
        if got != want:
            mismatches += 1
            if mismatches <= 5:
                diffs = [(r, got[r], want[r]) for r in range(NUM_REGS) if got[r] != want[r]]
                print(f'    Frame {f}: {len(diffs)} diff(s): {diffs[:6]}')

    pct = 100.0 * (num_check - mismatches) / num_check
    print(f'    Match: {num_check - mismatches}/{num_check} frames ({pct:.1f}%)')
    return mismatches == 0


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # 1. Capture ground truth
    frames = capture_frames()

    # 2. Split into per-voice streams
    v1, v2, v3 = extract_voice_streams(frames)

    # 3. Generate assembly
    asm = generate_asm(v1, v2, v3)

    asm_path = '/tmp/commando_hg18.asm'
    prg_path = '/tmp/commando_hg18.prg'
    lbl_path = '/tmp/commando_hg18.labels'

    # 4. Assemble
    print(f'[4] Assembling...')
    size, labels = assemble_and_find_labels(asm, asm_path, prg_path, lbl_path)
    if size is None:
        sys.exit(1)

    init_addr = labels.get('INIT', 0x1000)
    play_addr = labels.get('PLAY', 0x1003)

    # 5. Build PSID
    print(f'[5] Building PSID...')
    os.makedirs(os.path.dirname(OUTPUT_SID), exist_ok=True)
    total_size = build_psid(prg_path, OUTPUT_SID, init_addr, play_addr)

    # 6. Verify
    ok = verify(OUTPUT_SID, frames, num_check=min(500, NUM_FRAMES))

    # Summary
    orig_size = os.path.getsize(COMMANDO_SID)
    print()
    print('=== Summary ===')
    print(f'Original SID:         {orig_size} bytes')
    print(f'Flat-stream SID:      {total_size} bytes')
    print(f'Data streams:         {len(v1)+len(v2)+len(v3)} bytes ({NUM_FRAMES} frames x 7 x 3)')
    print(f'Player code:          ~{size - NUM_FRAMES*7*3} bytes (approx)')
    print(f'INIT=${init_addr:04X}, PLAY=${play_addr:04X}')
    print(f'Output:               {OUTPUT_SID}')
    print(f'Verification:         {"PASS" if ok else "FAIL"}')

    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
