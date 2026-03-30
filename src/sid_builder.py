"""
sid_builder.py - Build a .sid file from register data.

Takes register CSV (from siddump or sid_symbolic.py to-regs) and produces
a valid PSID v2 .sid file containing a minimal 6510 player that replays
the register writes frame by frame.

Memory layout (loaded at $1000):
  $1000: init routine
  $1020: play routine
  $1060: frame counter (2 bytes, little-endian)
  $1062: total frames (2 bytes, little-endian)
  $1064: register data (25 bytes per frame)
"""

import json
import struct
import sys


# PSID v2 header format
PSID_HEADER_SIZE = 0x7C  # 124 bytes

# Player code loads at this address
LOAD_ADDR = 0x1000

# Offsets within the player binary (relative to LOAD_ADDR)
INIT_OFFSET = 0x0000   # init routine at $1000
PLAY_OFFSET = 0x0020   # play routine at $1020
FRAME_CTR   = 0x0070   # current frame counter (2 bytes)
TOTAL_FRAMES = 0x0072  # total frames (2 bytes)
DATA_OFFSET = 0x0078   # register data starts here


def build_player(num_frames: int) -> bytearray:
    """Build the 6510 player code.

    init ($1000):
      LDA #$00
      STA frame_ctr
      STA frame_ctr+1
      RTS

    play ($1020):
      ; check if done
      LDA frame_ctr+1
      CMP total_frames+1
      BCC .go
      BNE .done
      LDA frame_ctr
      CMP total_frames
      BCS .done
    .go:
      ; calculate data pointer: data_start + frame_ctr * 25
      ; we use a simple loop: multiply frame_ctr by 25
      ; store result in $FB/$FC (zero page pointer)
      LDA frame_ctr
      STA $FB
      LDA frame_ctr+1
      STA $FC
      ; multiply by 25: x*25 = x*16 + x*8 + x
      ; actually easier to just add 25 each frame (increment pointer)
      ; ... but that requires persistent state.
      ; Let's use a different approach: keep a data pointer that advances by 25 each frame.
      ; We'll store the pointer at frame_ctr+2..+3 (we have room)
      ; Actually, let's redesign the layout.
      RTS
    """
    # The above approach gets complicated in raw machine code.
    # Simpler: use a self-modifying data pointer.
    #
    # Layout:
    #   $1000: init
    #   $1020: play
    #   $1060: frame_ctr (2 bytes)
    #   $1062: total_frames (2 bytes)
    #   $1064: data_ptr (2 bytes) - current read pointer into data
    #   $1066: data_start marker (not stored, computed)
    #   $1068: register data (25 bytes per frame)

    # Use xa65 assembler to build the player from proper 6502 source.
    # This avoids hand-assembled byte errors and is maintainable.
    #
    # Layout:
    #   $1000: init routine
    #   $1020: play routine
    #   $1060: frame_ctr (2 bytes)
    #   $1062: total_frames (2 bytes)
    #   $1064: data_ptr (2 bytes)
    #   $1066: padding (2 bytes)
    #   $1068: register data (25 bytes per frame)

    import subprocess, tempfile, os

    data_start = LOAD_ADDR + DATA_OFFSET

    asm_source = f"""
; SID register replay player
; Loaded at ${LOAD_ADDR:04X}

* = ${LOAD_ADDR:04X}

; ── init ($1000) ──
init
    lda #0
    sta frame_ctr
    sta frame_ctr+1
    lda #<data_start
    sta data_ptr
    lda #>data_start
    sta data_ptr+1
    rts

; pad to $1020
    .dsb ${LOAD_ADDR + PLAY_OFFSET:04X}-*, 0

; ── play ($1020) ──
play
    ; check if frame_ctr >= total_frames
    lda frame_ctr+1
    cmp total_frames+1
    bcc go
    bne done
    lda frame_ctr
    cmp total_frames
    bcs done

go
    ; copy data_ptr to zero page
    lda data_ptr
    sta $fb
    lda data_ptr+1
    sta $fc

    ; copy 25 bytes from (data_ptr) to $D400
    ldy #0
loop
    lda ($fb),y
    sta $d400,y
    iny
    cpy #25
    bne loop

    ; advance data_ptr by 25
    clc
    lda data_ptr
    adc #25
    sta data_ptr
    lda data_ptr+1
    adc #0
    sta data_ptr+1

    ; increment frame counter
    inc frame_ctr
    bne done
    inc frame_ctr+1

done
    rts

; pad to $1060
    .dsb ${LOAD_ADDR + FRAME_CTR:04X}-*, 0

; ── data area ──
frame_ctr
    .word 0
total_frames
    .word {num_frames}
data_ptr
    .word data_start

    .dsb ${LOAD_ADDR + DATA_OFFSET:04X}-*, 0
data_start
"""

    # Find xa65
    xa_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'tools', 'xa65', 'xa', 'xa'),
        'xa',
    ]
    xa = None
    for p in xa_paths:
        if os.path.isfile(p):
            xa = p
            break
    if xa is None:
        raise RuntimeError("xa65 assembler not found")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.a65', delete=False) as f:
        f.write(asm_source)
        asm_path = f.name

    out_path = asm_path + '.o65'
    try:
        result = subprocess.run([xa, '-o', out_path, asm_path],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"xa65 assembly failed:\n{result.stderr}")

        with open(out_path, 'rb') as f:
            code = bytearray(f.read())
    finally:
        os.unlink(asm_path)
        if os.path.exists(out_path):
            os.unlink(out_path)

    return code


def build_psid_header(title: str, author: str, released: str,
                      num_songs: int, start_song: int,
                      data_size: int, is_pal: bool) -> bytes:
    """Build a PSID v2 header."""
    header = bytearray(PSID_HEADER_SIZE)

    # Magic ID
    header[0:4] = b'PSID'

    # Version (big-endian)
    struct.pack_into('>H', header, 4, 2)  # PSID v2

    # Data offset
    struct.pack_into('>H', header, 6, PSID_HEADER_SIZE)

    # Load address (0 = taken from first 2 bytes of data)
    struct.pack_into('>H', header, 8, 0)

    # Init address
    struct.pack_into('>H', header, 10, LOAD_ADDR + INIT_OFFSET)

    # Play address
    struct.pack_into('>H', header, 12, LOAD_ADDR + PLAY_OFFSET)

    # Songs
    struct.pack_into('>H', header, 14, num_songs)

    # Start song
    struct.pack_into('>H', header, 16, start_song)

    # Speed (bit per song: 0=VBI/50Hz, 1=CIA)
    struct.pack_into('>I', header, 18, 0)  # all songs VBI

    # Title (32 bytes, null-terminated)
    title_bytes = title.encode('ascii', errors='replace')[:31]
    header[22:22+len(title_bytes)] = title_bytes

    # Author (32 bytes)
    author_bytes = author.encode('ascii', errors='replace')[:31]
    header[54:54+len(author_bytes)] = author_bytes

    # Released (32 bytes)
    released_bytes = released.encode('ascii', errors='replace')[:31]
    header[86:86+len(released_bytes)] = released_bytes

    # Flags (offset 0x76 = 118)
    flags = 0
    # Bit 2-3: SID model (00=unknown, 01=6581, 10=8580, 11=both)
    flags |= (1 << 2)  # 6581
    # Bit 0-1: MUS data / PSID specific
    # Bit 4-5: clock (00=unknown, 01=PAL, 10=NTSC, 11=both)
    if is_pal:
        flags |= (1 << 4)  # PAL
    else:
        flags |= (2 << 4)  # NTSC
    struct.pack_into('>H', header, 0x76, flags)

    return bytes(header)


def regs_to_sid(metadata: dict, reg_frames: list[list[int]], output_path: str):
    """Build a .sid file from metadata and register frames."""
    num_frames = len(reg_frames)

    # Build player code
    player = build_player(num_frames)

    # Append register data
    data = bytearray()
    for regs in reg_frames:
        data.extend(bytes(regs[:25]))

    # Combine: load address (2 bytes LE) + player + data
    binary = bytearray()
    binary.extend(struct.pack('<H', LOAD_ADDR))  # load address
    binary.extend(player)
    binary.extend(data)

    # Build PSID header
    title = metadata.get('title', 'Untitled')
    author = metadata.get('author', 'Unknown')
    released = metadata.get('released', '')
    is_pal = metadata.get('clock', 'PAL') == 'PAL'
    num_songs = metadata.get('songs', 1)
    start_song = metadata.get('subtune', 1)

    header = build_psid_header(title, author, released,
                               num_songs, start_song,
                               len(binary), is_pal)

    with open(output_path, 'wb') as f:
        f.write(header)
        f.write(binary)

    return len(binary)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Build .sid file from register data')
    parser.add_argument('input', help='Register CSV file from siddump or to-regs (- for stdin)')
    parser.add_argument('-o', '--output', required=True, help='Output .sid file path')
    args = parser.parse_args()

    inp = sys.stdin if args.input == '-' else open(args.input)

    # Parse register CSV
    metadata_line = inp.readline().strip()
    metadata = json.loads(metadata_line)

    # Skip header
    inp.readline()

    reg_frames = []
    for line in inp:
        line = line.strip()
        if line:
            regs = [int(h, 16) for h in line.split(',')]
            reg_frames.append(regs)

    if args.input != '-':
        inp.close()

    size = regs_to_sid(metadata, reg_frames, args.output)
    print(f"Built {args.output}: {len(reg_frames)} frames, {size} bytes payload")


if __name__ == '__main__':
    main()
