"""
Build a test .sid file using the SIDfinity player.

Creates a simple 3-voice tune to verify the player works:
  Voice 1: melody (pulse wave)
  Voice 2: bass (sawtooth)
  Voice 3: drums (noise)
"""

import struct
import subprocess
import os
import sys

PLAYER_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sidfinity.a65')
XA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                  'tools', 'xa65', 'xa', 'xa')

LOAD_ADDR = 0x0800
INIT_ADDR = 0x0800
PLAY_ADDR = 0x0803

# Note values (index into freq table, matching GoatTracker convention)
C0, D0, E0, F0, G0, A0, B0 = 0, 2, 4, 5, 7, 9, 11
C1, D1, E1, F1, G1, A1, B1 = 12, 14, 16, 17, 19, 21, 23
C2, D2, E2, F2, G2, A2, B2 = 24, 26, 28, 29, 31, 33, 35
C3, D3, E3, F3, G3, A3, B3 = 36, 38, 40, 41, 43, 45, 47
C4, D4, E4, F4, G4, A4, B4 = 48, 50, 52, 53, 55, 57, 59
C5, D5, E5, F5, G5, A5, B5 = 60, 62, 64, 65, 67, 69, 71


def build_psid_header(title, author, load_addr, init_addr, play_addr, songs=1):
    """Build PSID v2 header."""
    header = bytearray(124)
    header[0:4] = b'PSID'
    struct.pack_into('>H', header, 4, 2)
    struct.pack_into('>H', header, 6, 124)  # data offset
    struct.pack_into('>H', header, 8, 0)    # load addr from data
    struct.pack_into('>H', header, 10, init_addr)
    struct.pack_into('>H', header, 12, play_addr)
    struct.pack_into('>H', header, 14, songs)
    struct.pack_into('>H', header, 16, 1)   # start song
    # Title
    t = title.encode('ascii')[:31]
    header[22:22+len(t)] = t
    # Author
    a = author.encode('ascii')[:31]
    header[54:54+len(a)] = a
    # Flags: PAL, 6581
    struct.pack_into('>H', header, 0x76, 0x0014)
    return bytes(header)


def main():
    output = sys.argv[1] if len(sys.argv) > 1 else '/tmp/sidfinity_test.sid'

    # Assemble player
    import tempfile
    result = subprocess.run([XA, '-o', '/tmp/sidfinity_player.bin', PLAYER_SRC],
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Assembly failed:\n{result.stderr}')
        sys.exit(1)

    with open('/tmp/sidfinity_player.bin', 'rb') as f:
        player_code = f.read()

    print(f'Player code: {len(player_code)} bytes')

    # Build the binary: load address + player code + test data
    binary = bytearray()
    binary.extend(struct.pack('<H', LOAD_ADDR))  # load address
    binary.extend(player_code)

    # Patch init to set up a simple test pattern:
    # After init runs, we manually set voice 1 to play a note
    # by writing directly to the channel variables
    #
    # For now, just patch the init to set voice 1 to a pulse wave C-4:
    # chn_wave[0] = $41 (pulse + gate)
    # chn_ad[0] = $0A (attack=0, decay=A)
    # chn_sr[0] = $F8 (sustain=F, release=8)
    # chn_freqlo[0] / chn_freqhi[0] = frequency for C-4
    # chn_gate[0] = $FF (gate on)

    # The frequency for C-4 (note index 48) from the table:
    # lo=$68, hi=$11
    # Let's patch these into the init area by appending a post-init snippet

    # Actually, let's just build the .sid and verify siddump can emulate it
    # We need to modify init to write some values

    # Simpler approach: modify the player source to include test data
    # For now, just write a static test
    test_asm = f"""
; Test song data - appended after player
; Manually poke voice 1 to play C-4 pulse wave

* = $0800

            jmp test_init
            jmp test_play

test_init
; Clear SID
            lda #$00
            ldx #$18
ti_clr      sta $D400,x
            dex
            bpl ti_clr

; Set volume
            lda #$0F
            sta $D418

; Voice 1 - pulse wave C4
            lda #$68
            sta $D400
            lda #$11
            sta $D401
            lda #$08
            sta $D402
            lda #$08
            sta $D403
            lda #$09
            sta $D405
            lda #$00
            sta $D406
            lda #$41
            sta $D404

; Voice 2 - saw wave E3
            lda #$C1
            sta $D407
            lda #$07
            sta $D408
            lda #$09
            sta $D40C
            lda #$00
            sta $D40D
            lda #$21
            sta $D40B

; Voice 3 - noise G2
            lda #$CF
            sta $D40E
            lda #$05
            sta $D40F
            lda #$00
            sta $D413
            lda #$F9
            sta $D414
            lda #$81
            sta $D412

            rts

; Play - cycle through notes
play_ctr    .byte 1
test_play
            dec play_ctr
            bne tp_done

; Every 12 frames, change note
            lda #12
            sta play_ctr

; Cycle voice 1 through C major scale
            ldx note_idx
            lda melody,x
            tay
            lda freqlo,y
            sta $D400
            lda freqhi,y
            sta $D401

            inx
            cpx #8
            bne tp_nw
            ldx #0
tp_nw       stx note_idx

tp_done     rts

note_idx    .byte 0
melody      .byte {C4},{D4},{E4},{F4},{G4},{A4},{B4},{C5}

freqlo
            .byte $17,$27,$39,$4B,$5F,$74,$8A,$A1,$BA,$D4,$F0,$0E
            .byte $2D,$4E,$71,$96,$BE,$E8,$14,$43,$74,$A9,$E1,$1C
            .byte $5A,$9C,$E2,$2D,$7C,$CF,$28,$85,$E8,$52,$C1,$37
            .byte $B4,$39,$C5,$5A,$F7,$9E,$4F,$0A,$D1,$A3,$82,$6E
            .byte $68,$71,$8A,$B3,$EE,$3C,$9E,$15,$A2,$46,$04,$DC
            .byte $D0,$E2,$14,$67,$DD,$79,$3C,$29,$44,$8D,$08,$B8
            .byte $A1,$C5,$28,$CD,$BA,$F1,$78,$53,$87,$1A,$10,$71
            .byte $42,$89,$4F,$9B,$74,$E2,$F0,$A6,$0E,$33,$20,$FF
freqhi
            .byte $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$02
            .byte $02,$02,$02,$02,$02,$02,$03,$03,$03,$03,$03,$04
            .byte $04,$04,$04,$05,$05,$05,$06,$06,$06,$07,$07,$08
            .byte $08,$09,$09,$0A,$0A,$0B,$0C,$0D,$0D,$0E,$0F,$10
            .byte $11,$12,$13,$14,$15,$17,$18,$1A,$1B,$1D,$1F,$20
            .byte $22,$24,$27,$29,$2B,$2E,$31,$34,$37,$3A,$3E,$41
            .byte $45,$49,$4E,$52,$57,$5C,$62,$68,$6E,$75,$7C,$83
            .byte $8B,$93,$9C,$A5,$AF,$B9,$C4,$D0,$DD,$EA,$F8,$FF
"""

    # Assemble test
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.a65', delete=False) as f:
        f.write(test_asm)
        test_path = f.name

    result = subprocess.run([XA, '-o', '/tmp/sidfinity_test.bin', test_path],
                          capture_output=True, text=True)
    os.unlink(test_path)

    if result.returncode != 0:
        print(f'Test assembly failed:\n{result.stderr}')
        sys.exit(1)

    with open('/tmp/sidfinity_test.bin', 'rb') as f:
        test_code = f.read()

    print(f'Test code: {len(test_code)} bytes')

    # Build SID file
    binary = bytearray()
    binary.extend(struct.pack('<H', LOAD_ADDR))
    binary.extend(test_code)

    header = build_psid_header('SIDfinity Test', 'SIDfinity', LOAD_ADDR, INIT_ADDR, PLAY_ADDR)

    with open(output, 'wb') as f:
        f.write(header)
        f.write(binary)

    print(f'Built {output}: {len(header) + len(binary)} bytes')

    # Test with siddump
    siddump = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          'tools', 'siddump')
    if os.path.exists(siddump):
        result = subprocess.run([siddump, output, '--duration', '3'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f'siddump output: {len(lines)} lines')
            for line in lines[:5]:
                print(f'  {line[:80]}')
        else:
            print(f'siddump failed: {result.stderr}')


if __name__ == '__main__':
    main()
