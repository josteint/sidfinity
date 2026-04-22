#!/usr/bin/env python3
"""
Build Commando_hg3.sid — a perfect register-dump player for Commando by Rob Hubbard.

Steps:
1. Load original Commando.sid into py65
2. Call init($5FB2, A=0)
3. Call play($5012) 1500 times, capturing 21 SID registers per frame
4. Generate xa65 assembly with inline data
5. Assemble with xa65
6. Build PSID with header from original
7. Write demo/hubbard/Commando_hg3.sid
"""

import struct
import subprocess
import sys
import os
import tempfile

sys.path.insert(0, '/home/jtr/sidfinity/tools/py65_lib')
from py65.devices.mpu6502 import MPU

ORIGINAL_SID = '/home/jtr/sidfinity/data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid'
OUTPUT_SID   = '/home/jtr/sidfinity/demo/hubbard/Commando_hg3.sid'
XA65         = '/home/jtr/sidfinity/tools/xa65/xa/xa'

NUM_FRAMES   = 1500
REGS_PER_FRAME = 21   # 3 voices × 7 regs: freq_lo, freq_hi, pw_lo, pw_hi, wave, AD, SR
SID_BASE     = 0xD400

# SID register offsets per voice
# Voice 1: $D400-$D406  Voice 2: $D407-$D40D  Voice 3: $D40E-$D414
# Registers in order: freq_lo, freq_hi, pw_lo, pw_hi, wave, AD, SR
# Total: 3*7 = 21 bytes  (we skip $D415-$D418 filter/vol, set vol once in init)

MAX_CYCLES_PER_CALL = 200_000  # safety limit

def load_sid(path):
    with open(path, 'rb') as f:
        return f.read()

def setup_mpu(sid_data):
    """Parse PSID, load code into py65 MPU, return (mpu, init_addr, play_addr)."""
    header_len = struct.unpack('>H', sid_data[6:8])[0]
    load_addr  = struct.unpack('>H', sid_data[8:10])[0]
    init_addr  = struct.unpack('>H', sid_data[10:12])[0]
    play_addr  = struct.unpack('>H', sid_data[12:14])[0]

    code = sid_data[header_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[:2])[0]
        code = code[2:]

    print(f'  load_addr={hex(load_addr)}  init={hex(init_addr)}  play={hex(play_addr)}')
    print(f'  code size={len(code)} bytes')

    mpu = MPU()
    # Zero all memory
    for i in range(0x10000):
        mpu.memory[i] = 0

    # Load code
    for i, b in enumerate(code):
        mpu.memory[load_addr + i] = b

    # Place RTS at $FFFF for our call trampolines
    mpu.memory[0xFFFF] = 0x60  # RTS

    return mpu, init_addr, play_addr

def call_subroutine(mpu, addr, max_cycles=MAX_CYCLES_PER_CALL):
    """Call subroutine at addr using JSR + RTS trampoline at $0300."""
    # We place JSR addr; BRK at $0300, set PC=$0300, run until BRK or RTS returns
    # Actually: push return address manually and set PC = addr
    # Simplest: use the MPU's step() repeatedly, set up stack so RTS returns to $0200
    # where we have a sentinel BRK
    SENTINEL = 0x0200
    mpu.memory[SENTINEL] = 0x00  # BRK (sentinel — we stop on this)

    # Push return address (SENTINEL - 1) onto stack
    ret = SENTINEL - 1  # RTS increments PC, so push addr-1
    mpu.memory[0x100 + mpu.sp] = (ret >> 8) & 0xFF
    mpu.sp = (mpu.sp - 1) & 0xFF
    mpu.memory[0x100 + mpu.sp] = ret & 0xFF
    mpu.sp = (mpu.sp - 1) & 0xFF

    mpu.pc = addr
    cycles = 0
    while cycles < max_cycles:
        if mpu.pc == SENTINEL:
            break
        mpu.step()
        cycles += 1
    else:
        print(f'  WARNING: call to {hex(addr)} hit cycle limit')
    return cycles

def capture_frames(mpu, init_addr, play_addr, num_frames):
    """Run init then capture num_frames of SID registers."""
    # Init with A=0 (subtune 0)
    mpu.a = 0
    print(f'  Calling init at {hex(init_addr)}...')
    call_subroutine(mpu, init_addr)
    print(f'  Init done. Capturing {num_frames} frames...')

    frames = []
    for frame in range(num_frames):
        call_subroutine(mpu, play_addr)
        # Read 21 SID registers: $D400..$D414
        regs = [mpu.memory[SID_BASE + i] for i in range(REGS_PER_FRAME)]
        frames.append(regs)
        if frame % 100 == 99:
            print(f'  Frame {frame+1}/{num_frames}')

    return frames

def generate_asm(frames):
    """Generate xa65 assembly source."""
    data_bytes = []
    for regs in frames:
        data_bytes.extend(regs)

    # Format data as hex bytes, 21 per line
    data_lines = []
    for i in range(0, len(data_bytes), 21):
        chunk = data_bytes[i:i+21]
        hex_str = ','.join(f'${b:02x}' for b in chunk)
        data_lines.append(f'  .byte {hex_str}')
    data_block = '\n'.join(data_lines)

    nregs = REGS_PER_FRAME

    asm  = '* = $1000\n'
    asm += 'jmp init\n'
    asm += 'jmp play\n'
    asm += 'init:\n'
    asm += '  lda #$0f\n'
    asm += '  sta $d418\n'
    asm += '  lda #<data\n'
    asm += '  sta $80\n'
    asm += '  lda #>data\n'
    asm += '  sta $81\n'
    asm += '  rts\n'
    asm += 'play:\n'
    asm += '  ldy #0\n'
    asm += 'loop:\n'
    asm += '  lda ($80),y\n'
    asm += '  sta $d400,y\n'
    asm += '  iny\n'
    asm += f'  cpy #{nregs}\n'
    asm += '  bne loop\n'
    asm += '  clc\n'
    asm += '  lda $80\n'
    asm += f'  adc #{nregs}\n'
    asm += '  sta $80\n'
    asm += '  bcc nohi\n'
    asm += '  inc $81\n'
    asm += 'nohi:\n'
    asm += '  rts\n'
    asm += 'data:\n'
    asm += data_block + '\n'

    return asm

def build_psid(orig_sid_data, player_bin, output_path):
    """Build PSID from original header + new player binary."""
    # Clone the header from original (124 bytes)
    header_len = struct.unpack('>H', orig_sid_data[6:8])[0]
    header = bytearray(orig_sid_data[:header_len])

    # Set load_addr=0 (code has 2-byte prefix)
    struct.pack_into('>H', header, 8, 0)
    # Set init=$1000, play=$1003
    struct.pack_into('>H', header, 10, 0x1000)
    struct.pack_into('>H', header, 12, 0x1003)
    # Set num_songs=1, start_song=1
    struct.pack_into('>H', header, 14, 1)
    struct.pack_into('>H', header, 16, 1)

    # Prepend 2-byte little-endian load address $1000
    load_prefix = struct.pack('<H', 0x1000)

    psid = bytes(header) + load_prefix + player_bin
    with open(output_path, 'wb') as f:
        f.write(psid)
    print(f'  Written {len(psid)} bytes to {output_path}')

def main():
    print('=== Commando hg3 builder ===')

    # Step 1: Load and parse original SID
    print('\n[1] Loading Commando.sid...')
    orig_data = load_sid(ORIGINAL_SID)
    mpu, init_addr, play_addr = setup_mpu(orig_data)

    # Step 2: Capture frames
    print('\n[2] Capturing register frames...')
    frames = capture_frames(mpu, init_addr, play_addr, NUM_FRAMES)
    print(f'  Captured {len(frames)} frames, {len(frames)*REGS_PER_FRAME} bytes total')

    # Show first frame for sanity check
    print(f'  Frame 0 regs: {[hex(b) for b in frames[0]]}')
    print(f'  Frame 1 regs: {[hex(b) for b in frames[1]]}')

    # Step 3: Generate assembly
    print('\n[3] Generating assembly...')
    asm = generate_asm(frames)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.s', delete=False) as f:
        asm_path = f.name
        f.write(asm)
    print(f'  Written assembly to {asm_path}')

    # Step 4: Assemble
    print('\n[4] Assembling with xa65...')
    bin_path = asm_path.replace('.s', '.bin')
    result = subprocess.run(
        [XA65, '-o', bin_path, asm_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print('  ASSEMBLER ERROR:')
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    print(f'  Assembled OK')

    with open(bin_path, 'rb') as f:
        player_bin = f.read()
    print(f'  Binary size: {len(player_bin)} bytes')

    # Verify player fits: $1000 .. $1000+len < $D400 (SID registers)
    if 0x1000 + len(player_bin) > 0xD400:
        print(f'  ERROR: player+data ({hex(0x1000+len(player_bin))}) overlaps SID registers!')
        sys.exit(1)
    print(f'  Player end: {hex(0x1000+len(player_bin))} (SID regs at $D400 — OK)')

    # Cleanup temp files
    os.unlink(asm_path)
    os.unlink(bin_path)

    # Step 5: Build PSID
    print('\n[5] Building PSID...')
    os.makedirs('/home/jtr/sidfinity/demo/hubbard', exist_ok=True)
    build_psid(orig_data, player_bin, OUTPUT_SID)

    # Step 6: Verify by re-reading the PSID and checking a few frames
    print('\n[6] Verifying...')
    with open(OUTPUT_SID, 'rb') as f:
        built_data = f.read()

    header_len = struct.unpack('>H', built_data[6:8])[0]
    init_v = struct.unpack('>H', built_data[10:12])[0]
    play_v = struct.unpack('>H', built_data[12:14])[0]
    print(f'  Header: init={hex(init_v)} play={hex(play_v)} header_len={header_len}')

    # Quick py65 verify: load hg3 player, run a few frames, check regs match
    vdata = built_data
    v_header_len = struct.unpack('>H', vdata[6:8])[0]
    v_load_addr = struct.unpack('>H', vdata[8:10])[0]
    v_init = struct.unpack('>H', vdata[10:12])[0]
    v_play = struct.unpack('>H', vdata[12:14])[0]
    v_code = vdata[v_header_len:]
    if v_load_addr == 0:
        v_load_addr = struct.unpack('<H', v_code[:2])[0]
        v_code = v_code[2:]

    vmpu = MPU()
    for i in range(0x10000):
        vmpu.memory[i] = 0
    for i, b in enumerate(v_code):
        vmpu.memory[v_load_addr + i] = b

    vmpu.a = 0
    call_subroutine(vmpu, v_init)

    mismatches = 0
    for frame_idx in range(min(10, NUM_FRAMES)):
        call_subroutine(vmpu, v_play)
        got = [vmpu.memory[SID_BASE + i] for i in range(REGS_PER_FRAME)]
        want = frames[frame_idx]
        if got != want:
            print(f'  MISMATCH frame {frame_idx}: got={got} want={want}')
            mismatches += 1
        else:
            print(f'  Frame {frame_idx} OK: {[hex(b) for b in got[:4]]}...')

    if mismatches == 0:
        print(f'\n  All {min(10,NUM_FRAMES)} verification frames match!')
    else:
        print(f'\n  {mismatches} mismatches found!')

    print(f'\n=== Done: {OUTPUT_SID} ===')

if __name__ == '__main__':
    main()
