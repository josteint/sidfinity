"""
Build a test .sid using the SIDfinity player with song data built in Python.

Assembles the player, then constructs song data (patterns, orderlists)
as raw bytes and patches them together.
"""

import struct
import subprocess
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
XA = os.path.join(PROJECT_ROOT, 'tools', 'xa65', 'xa', 'xa')
SIDDUMP = os.path.join(PROJECT_ROOT, 'tools', 'siddump')

LOAD_ADDR = 0x0800
SONG_DATA = 0x0C00

# Pattern encoding
ENDPATT = 0x00
FIRSTNOTE = 0x60
REST = 0xBD
KEYOFF = 0xBE
KEYON = 0xBF

# Notes
def note(name, octave):
    notes = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
    return FIRSTNOTE + octave * 12 + notes[name]

C4=note('C',4); D4=note('D',4); E4=note('E',4); F4=note('F',4)
G4=note('G',4); A4=note('A',4); B4=note('B',4); C5=note('C',5)
C2=note('C',2); F2=note('F',2); G2=note('G',2)
C3=note('C',3)


def build_player_asm():
    """Build a self-contained player+init as assembly."""
    # Write a single assembly file that includes init, play, and freq tables
    # Keep it simple - no comments with special chars
    asm = """
* = $0800

            jmp sf_init
            jmp sf_play

sf_init
            lda #$00
            ldx #$FF
iclr        sta $0B00,x
            dex
            bpl iclr
            ldx #$18
isid        sta $D400,x
            dex
            bpl isid
            lda #$0F
            sta $D418
            sta $0BC0
            lda #$06
            sta $0B00
            sta $0B07
            sta $0B0E
            sta $0B07
            sta $0B0E
            sta $0B15
            lda #$FE
            sta $0B3F
            sta $0B46
            sta $0B4D
            rts

sf_play
            lda $FB
            pha
            lda $FC
            pha
            ldx #$00
            jsr pv
            ldx #$07
            jsr pv
            ldx #$0E
            jsr pv
            lda $0BC3
            ora $0BC0
            sta $D418
            pla
            sta $FC
            pla
            sta $FB
            rts

pv
            dec $0B00,x
            bne pvw
            lda $0B07,x
            sta $0B00,x
            lda $0B1C,x
            bne pvrd
            jsr nxpat
pvrd        jsr rdnt

pvw
            lda $0B62,x
            sta $D400,x
            lda $0B69,x
            sta $D401,x
            lda $0B70,x
            sta $D402,x
            lda $0B77,x
            sta $D403,x
            lda $0B4D,x
            and $0B3F,x
            sta $D404,x
            lda $0B54,x
            sta $D405,x
            lda $0B5B,x
            sta $D406,x
            rts

nxpat
            stx svx+1
            txa
            lsr
            lsr
            lsr
            tax
            lda $0BD0,x
            sta $FB
            lda $0BD3,x
            sta $FC
svx         ldx #$00
            ldy $0B2A,x
nprd        lda ($FB),y
            cmp #$FF
            bne npne
            iny
            lda ($FB),y
            tay
            jmp nprd
npne        pha
            iny
            lda ($FB),y
            sec
            sbc #$80
            sta $0B21,x
            iny
            tya
            sta $0B2A,x
            pla
            asl
            tay
            lda $0C00,y
            sta $0B0E,x
            lda $0C80,y
            sta $0B15,x
            lda #$00
            sta $0B1C,x
            rts

rdnt
            lda $0B0E,x
            sta $FB
            lda $0B15,x
            sta $FC
            ldy $0B1C,x
            lda ($FB),y
            bne rnn0
            sta $0B1C,x
            rts
rnn0        cmp #$40
            bcs rnfx
            iny
            lda ($FB),y
rnfx        cmp #$60
            bcs rnnote
            iny
            lda ($FB),y
            cmp #$60
            bcs rnnote
            iny
            lda ($FB),y
rnnote      cmp #$BD
            beq rnrest
            cmp #$BE
            beq rnkoff
            cmp #$BF
            beq rnkon
            cmp #$C0
            bcs rnpk
            sec
            sbc #$60
            clc
            adc $0B21,x
            tay
            lda ftlo,y
            sta $0B62,x
            lda fthi,y
            sta $0B69,x
            lda #$FF
            sta $0B3F,x
rnrest      iny
            lda ($FB),y
            beq rnend
            tya
            sta $0B1C,x
            rts
rnkoff      lda #$FE
            sta $0B3F,x
            jmp rnrest
rnkon       lda #$FF
            sta $0B3F,x
            jmp rnrest
rnpk        iny
            lda ($FB),y
            beq rnend
            tya
            sta $0B1C,x
            rts
rnend       lda #$00
            sta $0B1C,x
            rts

ftlo
            .byte $17,$27,$39,$4B,$5F,$74,$8A,$A1,$BA,$D4,$F0,$0E
            .byte $2D,$4E,$71,$96,$BE,$E8,$14,$43,$74,$A9,$E1,$1C
            .byte $5A,$9C,$E2,$2D,$7C,$CF,$28,$85,$E8,$52,$C1,$37
            .byte $B4,$39,$C5,$5A,$F7,$9E,$4F,$0A,$D1,$A3,$82,$6E
            .byte $68,$71,$8A,$B3,$EE,$3C,$9E,$15,$A2,$46,$04,$DC
            .byte $D0,$E2,$14,$67,$DD,$79,$3C,$29,$44,$8D,$08,$B8
            .byte $A1,$C5,$28,$CD,$BA,$F1,$78,$53,$87,$1A,$10,$71
            .byte $42,$89,$4F,$9B,$74,$E2,$F0,$A6,$0E,$33,$20,$FF
fthi
            .byte $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$02
            .byte $02,$02,$02,$02,$02,$02,$03,$03,$03,$03,$03,$04
            .byte $04,$04,$04,$05,$05,$05,$06,$06,$06,$07,$07,$08
            .byte $08,$09,$09,$0A,$0A,$0B,$0C,$0D,$0D,$0E,$0F,$10
            .byte $11,$12,$13,$14,$15,$17,$18,$1A,$1B,$1D,$1F,$20
            .byte $22,$24,$27,$29,$2B,$2E,$31,$34,$37,$3A,$3E,$41
            .byte $45,$49,$4E,$52,$57,$5C,$62,$68,$6E,$75,$7C,$83
            .byte $8B,$93,$9C,$A5,$AF,$B9,$C4,$D0,$DD,$EA,$F8,$FF
"""
    return asm


def main():
    output = sys.argv[1] if len(sys.argv) > 1 else '/tmp/sidfinity_song.sid'

    # Assemble player
    import tempfile
    asm = build_player_asm()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.a65', delete=False) as f:
        f.write(asm)
        asm_path = f.name

    result = subprocess.run([XA, '-o', '/tmp/sf_player.bin', asm_path],
                          capture_output=True, text=True)
    os.unlink(asm_path)
    if result.returncode != 0:
        print(f'Assembly failed:\n{result.stderr}')
        sys.exit(1)

    with open('/tmp/sf_player.bin', 'rb') as f:
        player = f.read()
    print(f'Player: {len(player)} bytes')

    # Build patterns
    p0 = bytes([C4, REST, REST, REST, E4, REST, REST, REST,
                G4, REST, REST, REST, C5, REST, REST, REST,
                G4, REST, REST, REST, E4, REST, REST, REST,
                C4, REST, REST, REST, REST, REST, REST, REST, ENDPATT])

    p1 = bytes([C2, REST, REST, REST, REST, REST, REST, REST,
                F2, REST, REST, REST, REST, REST, REST, REST,
                G2, REST, REST, REST, REST, REST, REST, REST,
                C2, REST, REST, REST, REST, REST, REST, REST, ENDPATT])

    p2 = bytes([C3, REST, KEYOFF, REST, C3, REST, KEYOFF, REST,
                C3, REST, KEYOFF, REST, C3, REST, KEYOFF, REST,
                C3, REST, KEYOFF, REST, C3, REST, KEYOFF, REST,
                C3, REST, KEYOFF, REST, C3, REST, KEYOFF, REST, ENDPATT])

    patterns = [p0, p1, p2]

    # Build orderlists (pattern, transpose pairs + $FF + restart)
    ol1 = bytes([0x00, 0x80, 0xFF, 0x00])  # pattern 0, no transpose, loop
    ol2 = bytes([0x01, 0x80, 0xFF, 0x00])  # pattern 1
    ol3 = bytes([0x02, 0x80, 0xFF, 0x00])  # pattern 2
    orderlists = [ol1, ol2, ol3]

    # Layout at SONG_DATA ($0C00):
    # $0C00-$0C7F: pattern table lo (128 bytes)
    # $0C80-$0CFF: pattern table hi (128 bytes)
    # $0D00+: orderlists then pattern data

    ol_base = SONG_DATA + 256  # after pattern tables
    patt_base = ol_base + sum(len(ol) for ol in orderlists)

    # Pattern addresses
    addr = patt_base
    patt_addrs = []
    for p in patterns:
        patt_addrs.append(addr)
        addr += len(p)

    # Build song data
    song = bytearray()

    # Pattern pointer table
    tbl_lo = bytearray(128)
    tbl_hi = bytearray(128)
    for i, a in enumerate(patt_addrs):
        tbl_lo[i] = a & 0xFF
        tbl_hi[i] = (a >> 8) & 0xFF
    song.extend(tbl_lo)
    song.extend(tbl_hi)

    # Orderlists
    ol_addrs = []
    for ol in orderlists:
        ol_addrs.append(SONG_DATA + len(song))
        song.extend(ol)

    # Patterns
    for p in patterns:
        song.extend(p)

    print(f'Song data: {len(song)} bytes')
    print(f'Orderlists at: {[f"${a:04X}" for a in ol_addrs]}')
    print(f'Patterns at: {[f"${a:04X}" for a in patt_addrs]}')

    # Build init patch: set orderlist pointers and instrument defaults
    # Append raw bytes after the player code
    patch = bytearray()

    # We need to patch the init routine to also set:
    # - Orderlist pointers at $0BD0-$0BD5
    # - Instrument params (wave, AD, SR) for each voice
    # The player's init ($0800) already clears everything and sets tempo.
    # We'll replace the init with a version that also sets our pointers.

    # Actually, let's just write a separate init that calls the player init
    # then sets up pointers. But the entry point is $0800...

    # Simplest: build the full binary with the player code, then patch
    # the init to also set orderlist pointers and instrument params.
    # We'll do this by extending the init routine.

    # The player's init ends with RTS. We can find it and insert more code before RTS.
    # Or easier: build the binary and patch specific memory locations directly.

    # Build base binary
    binary = bytearray()
    binary.extend(struct.pack('<H', LOAD_ADDR))  # load address
    binary.extend(player)

    # Pad to SONG_DATA
    pad = SONG_DATA - LOAD_ADDR - len(player)
    if pad < 0:
        print(f'ERROR: player too large, extends {-pad} bytes past song data area')
        sys.exit(1)
    binary.extend(b'\x00' * pad)

    # Append song data
    binary.extend(song)

    # Now patch the variable area (which sits at $0B00-$0BFF in the binary)
    # to pre-set instrument params and orderlist pointers.
    # These are in the gap between player code and song data.
    # Offset in binary = address - LOAD_ADDR + 2 (for load addr bytes)

    def poke(addr, val):
        off = addr - LOAD_ADDR + 2
        if 0 <= off < len(binary):
            binary[off] = val

    # Orderlist pointers
    poke(0x0BD0, ol_addrs[0] & 0xFF)
    poke(0x0BD1, ol_addrs[1] & 0xFF)
    poke(0x0BD2, ol_addrs[2] & 0xFF)
    poke(0x0BD3, (ol_addrs[0] >> 8) & 0xFF)
    poke(0x0BD4, (ol_addrs[1] >> 8) & 0xFF)
    poke(0x0BD5, (ol_addrs[2] >> 8) & 0xFF)

    # Voice 1: pulse wave ($41), AD=$09, SR=$00, pulse=$0808
    poke(0x0B4D, 0x41)  # chn_wave voice 1
    poke(0x0B54, 0x09)  # chn_ad
    poke(0x0B5B, 0x00)  # chn_sr
    poke(0x0B70, 0x08)  # chn_pulselo
    poke(0x0B77, 0x08)  # chn_pulsehi

    # Voice 2: saw wave ($21), AD=$0A
    poke(0x0B4D+7, 0x21)
    poke(0x0B54+7, 0x0A)

    # Voice 3: noise ($81), SR=$F0
    poke(0x0B4D+14, 0x81)
    poke(0x0B5B+14, 0xF0)

    # BUT: the init routine clears $0B00-$0BFF to zero!
    # Our poked values will be erased. We need the init to NOT clear these,
    # or we need to set them AFTER init runs.
    # Solution: the PSID driver calls init first, then play repeatedly.
    # We can't set these after init in the SID file...
    # Unless we modify init to set them.

    # The init code at $0800 does: LDA #$00, LDX #$FF, STA $0B00,X, DEX, BPL
    # This clears $0B00-$0BFF. Then it sets tempo and gates.
    # We need to ADD code after the tempo/gate setup to set our pointers.

    # Find the RTS in the init (first RTS after $0800)
    init_start = 2  # skip load addr
    for i in range(init_start, init_start + 200):
        if binary[i] == 0x60:  # RTS
            rts_pos = i
            break

    print(f'Init RTS at binary offset {rts_pos} (addr ${LOAD_ADDR + rts_pos - 2:04X})')

    # Replace RTS with JMP to our patch code
    # Put patch code right after the player code
    patch_addr = LOAD_ADDR + len(player)
    binary[rts_pos] = 0x4C  # JMP
    binary[rts_pos+1] = patch_addr & 0xFF
    binary[rts_pos+2] = (patch_addr >> 8) & 0xFF

    # Build patch code at patch_addr
    patch_off = patch_addr - LOAD_ADDR + 2
    patch = bytearray()

    # Set orderlist pointers
    for i, addr in enumerate(ol_addrs):
        patch.extend([0xA9, addr & 0xFF])           # LDA #lo
        patch.extend([0x8D, 0xD0 + i, 0x0B])        # STA $0BD0+i
    for i, addr in enumerate(ol_addrs):
        patch.extend([0xA9, (addr >> 8) & 0xFF])     # LDA #hi
        patch.extend([0x8D, 0xD3 + i, 0x0B])        # STA $0BD3+i

    # Set voice 1 instrument params
    for val, lo, hi in [(0x41, 0x4D, 0x0B), (0x09, 0x54, 0x0B), (0x00, 0x5B, 0x0B),
                         (0x08, 0x70, 0x0B), (0x08, 0x77, 0x0B)]:
        patch.extend([0xA9, val, 0x8D, lo, hi])

    # Voice 2
    for val, lo, hi in [(0x21, 0x4D+7, 0x0B), (0x0A, 0x54+7, 0x0B)]:
        patch.extend([0xA9, val, 0x8D, lo, hi])

    # Voice 3
    for val, lo, hi in [(0x81, 0x4D+14, 0x0B), (0xF0, 0x5B+14, 0x0B)]:
        patch.extend([0xA9, val, 0x8D, lo, hi])

    patch.append(0x60)  # RTS

    # Write patch into binary
    for i, b in enumerate(patch):
        binary[patch_off + i] = b

    print(f'Init patch: {len(patch)} bytes at ${patch_addr:04X}')

    # Build PSID header
    header = bytearray(124)
    header[0:4] = b'PSID'
    struct.pack_into('>H', header, 4, 2)
    struct.pack_into('>H', header, 6, 124)
    struct.pack_into('>H', header, 8, 0)
    struct.pack_into('>H', header, 10, LOAD_ADDR)  # init
    struct.pack_into('>H', header, 12, LOAD_ADDR + 3)  # play
    struct.pack_into('>H', header, 14, 1)  # songs
    struct.pack_into('>H', header, 16, 1)  # start song
    t = b'SIDfinity Test Song'
    header[22:22+len(t)] = t
    a = b'SIDfinity'
    header[54:54+len(a)] = a
    struct.pack_into('>H', header, 0x76, 0x0014)

    with open(output, 'wb') as f:
        f.write(header)
        f.write(binary)

    total = len(header) + len(binary)
    print(f'Built {output}: {total} bytes')

    # Test
    if os.path.exists(SIDDUMP):
        result = subprocess.run([SIDDUMP, output, '--duration', '5'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f'siddump: {len(lines)-2} frames')
            prev_fhi = ''
            for i, line in enumerate(lines[2:32]):
                regs = line.split(',')
                if len(regs) >= 5:
                    fhi = regs[1]
                    ctrl = regs[4]
                    if fhi != prev_fhi:
                        print(f'  F{i:3d}: V1_FHi={fhi} V1_Ctrl={ctrl} V2_FHi={regs[8]} V3_Ctrl={regs[18]}')
                        prev_fhi = fhi
        else:
            print(f'siddump error (exit {result.returncode}): {result.stderr[:200]}')


if __name__ == '__main__':
    main()
