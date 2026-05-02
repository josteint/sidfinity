#!/usr/bin/env python3
"""
Stream-oriented SID codegen.

Instead of computing register VALUES, replays the exact INSTRUCTION STREAM
that Hubbard's engine sends to the SID chip. Every intermediate write
is reproduced, not just the final value per frame.

The stream is captured from hubbard_emu.py (100% verified against py65).
"""

import sys, struct, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from hubbard_emu import load_sid, HubbardEmu

SID_PATH = os.path.join(ROOT, 'data', 'C64Music', 'MUSICIANS', 'H',
                         'Hubbard_Rob', 'Commando.sid')
XA = os.path.join(ROOT, 'tools', 'xa65', 'xa', 'xa')
OUT_PATH = os.path.join(ROOT, 'demo', 'hubbard', 'Commando_stream.sid')


def capture_stream(sid_path, song=0, n_frames=1500):
    """Capture the complete instruction stream from Hubbard's engine."""
    header, binary, la = load_sid(sid_path)
    emu = HubbardEmu(binary, la, song)

    class TrackedSID:
        def __init__(self):
            self.data = [0] * 25
            self.writes = []
        def __getitem__(self, i): return self.data[i]
        def __setitem__(self, i, v):
            self.writes.append((i, v))
            self.data[i] = v
        def __len__(self): return len(self.data)
        def start_frame(self): self.writes = []
        def get_writes(self): return list(self.writes)

    tracked = TrackedSID()
    emu.sid = tracked

    frames = []
    for _ in range(n_frames):
        tracked.start_frame()
        emu.play()
        frames.append(tracked.get_writes())

    return frames


def compress_stream(frames):
    """Compress the stream using run-length encoding of repeated patterns."""
    # Find unique write sequences
    unique = {}
    frame_indices = []
    for writes in frames:
        key = tuple(writes)
        if key not in unique:
            unique[key] = len(unique)
        frame_indices.append(unique[key])

    print(f"  {len(frames)} frames → {len(unique)} unique patterns")
    print(f"  Compression: {len(unique)/len(frames)*100:.1f}%")

    # Compute sizes
    total_write_bytes = sum(len(w) * 3 for w in unique.values())  # LDA #val + STA $D4xx per write
    index_bytes = len(frames) * 2  # 2 bytes per frame index
    print(f"  Pattern data: {sum(len(k) * 3 + 1 for k in unique)} bytes")  # +1 for RTS
    print(f"  Frame index: {index_bytes} bytes")

    return unique, frame_indices


def generate_asm(frames):
    """Generate 6502 assembly that replays the instruction stream.

    Uses a compact data format: each frame's writes stored as
    (register, value) byte pairs terminated by $FF in a linear stream.
    The play routine walks through the stream with a pointer.
    """
    L = []
    a = L.append
    BASE = 0x1000

    # Build the linear data stream
    stream_bytes = []
    for writes in frames:
        for reg, val in writes:
            stream_bytes.append(reg)   # SID register offset (0-20)
            stream_bytes.append(val)   # value to write
        stream_bytes.append(0xFF)      # end of frame marker

    print(f"  {len(frames)} frames, {len(stream_bytes)} stream bytes ({len(stream_bytes)/1024:.1f} KB)")

    a(f'        * = ${BASE:04X}')
    a(f'        jmp init')
    a(f'        jmp play')
    a('')

    # --- INIT ---
    a('init')
    a('        lda #$0F')
    a('        sta $D418')
    a('        lda #<stream')
    a('        sta $FE')
    a('        lda #>stream')
    a('        sta $FF')
    a('        rts')
    a('')

    # --- PLAY ---
    # Walk through the stream: read (reg, val) pairs, write to SID
    a('play')
    a('        ldy #0')
    a('ploop')
    a('        lda ($FE),y')        # read register offset
    a('        cmp #$FF')
    a('        beq pdone')          # end of frame
    a('        tax')                # X = register offset
    a('        iny')
    a('        lda ($FE),y')        # read value
    a('        sta $D400,x')        # write to SID
    a('        iny')
    a('        bne ploop')          # continue (Y won't overflow for < 128 writes)
    a('pdone')
    # Advance stream pointer by Y+1
    a('        iny')                # skip past the $FF marker
    a('        tya')
    a('        clc')
    a('        adc $FE')
    a('        sta $FE')
    a('        bcc pnoc')
    a('        inc $FF')
    a('pnoc')
    a('        rts')
    a('')

    # --- STREAM DATA ---
    a('stream')
    for i in range(0, len(stream_bytes), 16):
        chunk = stream_bytes[i:i+16]
        a('        .byte ' + ','.join(f'${b:02X}' for b in chunk))
    a('')

    return '\n'.join(L)


def build_sid(asm_text, output_path):
    """Assemble and wrap in PSID."""
    import subprocess
    asm_path = output_path.replace('.sid', '.s')
    bin_path = output_path.replace('.sid', '.bin')
    with open(asm_path, 'w') as f:
        f.write(asm_text)
    result = subprocess.run([XA, '-o', bin_path, asm_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Assembly FAILED:\n{result.stderr}")
        return False
    with open(bin_path, 'rb') as f:
        binary = f.read()

    # PSID header
    with open(SID_PATH, 'rb') as f:
        orig = f.read()
    header_len = struct.unpack('>H', orig[6:8])[0]
    header = bytearray(orig[:header_len])
    struct.pack_into('>H', header, 8, 0)
    struct.pack_into('>H', header, 10, 0x1000)
    struct.pack_into('>H', header, 12, 0x1003)
    struct.pack_into('>H', header, 14, 1)
    struct.pack_into('>H', header, 16, 1)

    sid_data = bytes(header) + struct.pack('<H', 0x1000) + binary
    with open(output_path, 'wb') as f:
        f.write(sid_data)
    print(f"  SID: {len(sid_data)} bytes, code end ${0x1000 + len(binary):04X}")
    return True


if __name__ == '__main__':
    print("Stream Codegen — instruction stream replay")
    print("=" * 50)

    print("\n[1] Capturing instruction stream from Hubbard...")
    frames = capture_stream(SID_PATH, n_frames=1500)
    total_writes = sum(len(f) for f in frames)
    print(f"  {len(frames)} frames, {total_writes} total writes ({total_writes/len(frames):.1f} avg)")

    print("\n[2] Generating assembly...")
    asm = generate_asm(frames)

    print("\n[3] Building PSID...")
    ok = build_sid(asm, OUT_PATH)
    if ok:
        print(f"\n  Output: {OUT_PATH}")
