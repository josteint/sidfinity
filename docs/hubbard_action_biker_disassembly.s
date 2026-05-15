; ============================================================================
; Rob Hubbard - Action Biker (1985 Mastertronic)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: data/C64Music/MUSICIANS/H/Hubbard_Rob/Action_Biker.sid
; Load:   $C000   Init: $CBBB   Play: $C00D
; PSID:   19 subtunes, default subtune 2 (1-indexed; A=1 passed to init)
; Binary: $C000-$CBC1 (3010 bytes)
;
; Auto-traced 302 reachable code bytes from init+play. Layout commentary
; below was hand-derived by combining static analysis with py65
; single-step simulation logging SID writes (see /tmp/sim_actionbiker_f0.py).
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($CBBB): minimal 7 bytes. A holds subtune (0-indexed). Writes
; (A + $40) to $C3EA and returns. ALL setup is deferred to play's
; first-frame path.
;
; play ($C00D): every frame.
;   1. DEC $C3F1; if NOT negative, JMP $C28D (which is just RTS — early-out
;      counter, mostly always negative because $C3F1 is reset to $C000=$00
;      every frame, so DEC immediately gives $FF and BMI is taken).
;   2. INC $C3F0 (global frame counter).
;   3. BIT $C3EA: tests if bits 7 and 6 are set.
;      - bit 7 set → end-of-song; JMP $C28D (RTS)
;      - bit 6 set → FIRST FRAME; JSR $C28E (one-time setup)
;      - both clear → normal play
;   4. Fall through to per-voice processing at $C02B.
;
; $C28E (one-time setup): masks $C3EA to (subtune & $03), then:
;   - Copies 6 bytes of orderlist pointers from $C3F9+subtune*6 to $C3F3.
;   - Sets $C3F2 = 1 if subtune == 0, else 2 (loop start voice index).
;   - Clears V1/V2/V3 ctrl ($D404/$D40B/$D412), sets vol $0F.
;   - Zeros voice state arrays $C3C0,X $C3C3,X $C3C6,X $C3CF,X for X=2..0.
;   - Returns. The byte at $C3EA now has bit 6 clear, so subsequent
;     frames skip $C28E.
;
; PER-VOICE PROCESSING ($C02B..$C28A):
;   - X = $C3F2 (start with V3 for subtune>0, or V2 for subtune 0).
;   - DEC $C3E7 (per-frame counter, reload from $C3E8 when negative).
;   - **Note-load is gated by ($C3E7 == $C3E8)** at $C040-$C046.
;   - On FIRST FRAME: $C3E7 went from $01 → $00, then was reloaded to
;     $C3E8 = $02. So $C3E7 = $00 != $C3E8 = $02 → branch to $C05D →
;     JMP $C157 (effects loop, NO note load).
;   - Effects loop ($C157+) reads per-voice instrument state, writes
;     vibrato/freq-slide computed freqs. For V1+V2 this produces a freq
;     write of $0116 = freq_table[0]. For V3 the state is different and
;     produces no SID writes.
;   - On SECOND FRAME ($C3E7 cycles to == $C3E8): note-load DOES run for
;     all voices, all 3 voices fire their first notes.
;
; CONSEQUENCE FOR OUR CODEGEN:
;   This is the source of the 1-frame timing offset between our rebuild
;   (Grade D 61%) and the original. Our codegen's init zeros voice state
;   and fires the first note on play frame 0. The original engine
;   defers note firing until frame 1 via this $C3E7/$C3E8 gating.
;
;   To match: codegen would need to mirror the $C3E7-style counter
;   that delays the first note load by 1 frame.
;
; FREQ TABLE: $C2FC, 96 semitone entries packed as (lo[i], hi[i]) 2-byte
; little-endian stride. discover.py undercounts ("36 records × 4 bytes")
; because it groups bytes into 4-byte records, but the actual data is
; sequential 2-byte semitones over 192 bytes.
;
; INSTRUMENT TABLE: $CB5B, 8-byte records × 9 instruments.
;   offset 0: pulse_lo  1: pulse_hi  2: ctrl  3: AD  4: SR  5: ?  6: ?  7: fx_flags
;
; ============================================================================

sub_C001:
    $C001: 4C DC C2    JMP $c2dc      ; → L_C2DC
; ----- data gap $C004-$C00C (9 bytes) -----


; ======= play: =======
play:
    $C00D: CE F1 C3    DEC $c3f1
    $C010: 30 03       BMI $c015      ; → L_C015
    $C012: 4C 8D C2    JMP $c28d      ; → L_C28D
L_C015:
    $C015: EE F0 C3    INC $c3f0
    $C018: AD 00 C0    LDA $c000
    $C01B: 8D F1 C3    STA $c3f1
    $C01E: 2C EA C3    BIT $c3ea
    $C021: 10 03       BPL $c026      ; → L_C026
    $C023: 4C 8D C2    JMP $c28d      ; → L_C28D
L_C026:
    $C026: 50 03       BVC $c02b      ; → L_C02B
    $C028: 20 8E C2    JSR $c28e      ; → sub_C28E
L_C02B:
    $C02B: AE F2 C3    LDX $c3f2
    $C02E: CE E7 C3    DEC $c3e7
    $C031: 10 06       BPL $c039      ; → L_C039
    $C033: AD E8 C3    LDA $c3e8
    $C036: 8D E7 C3    STA $c3e7
L_C039:
    $C039: BD BC C3    LDA $c3bc,X
    $C03C: 8D BF C3    STA $c3bf
    $C03F: A8          TAY
    $C040: AD E7 C3    LDA $c3e7
    $C043: CD E8 C3    CMP $c3e8
    $C046: D0 15       BNE $c05d      ; → L_C05D
    $C048: BD F3 C3    LDA $c3f3,X
    $C04B: 85 4B       STA $4b
    $C04D: BD F6 C3    LDA $c3f6,X
    $C050: 85 4C       STA $4c
    $C052: DE C6 C3    DEC $c3c6,X
    $C055: 30 09       BMI $c060      ; → L_C060
    $C057: 4C 38 C1    JMP $c138      ; → L_C138
; ----- data gap $C05A-$C05C (3 bytes) -----

L_C05D:
    $C05D: 4C 57 C1    JMP $c157      ; → L_C157
L_C060:
    $C060: BC C0 C3    LDY $c3c0,X
    $C063: B1 4B       LDA ($4b),Y
    $C065: C9 FF       CMP #$ff
    $C067: F0 0A       BEQ $c073      ; → L_C073
    $C069: C9 FE       CMP #$fe
    $C06B: D0 17       BNE $c084      ; → L_C084
    $C06D: 20 01 C0    JSR $c001      ; → sub_C001
    $C070: 4C 8D C2    JMP $c28d      ; → L_C28D
L_C073:
    $C073: A9 00       LDA #$00
    $C075: 9D C6 C3    STA $c3c6,X
    $C078: 9D C0 C3    STA $c3c0,X
    $C07B: 9D C3 C3    STA $c3c3,X
    $C07E: 4C 60 C0    JMP $c060      ; → L_C060
; ----- data gap $C081-$C083 (3 bytes) -----

L_C084:
    $C084: A8          TAY
    $C085: B9 0B C4    LDA $c40b,Y
    $C088: 85 4D       STA $4d
    $C08A: B9 36 C4    LDA $c436,Y
    $C08D: 85 4E       STA $4e
    $C08F: BC C3 C3    LDY $c3c3,X
    $C092: A9 FF       LDA #$ff
    $C094: 8D D5 C3    STA $c3d5
    $C097: B1 4D       LDA ($4d),Y
    $C099: 9D C9 C3    STA $c3c9,X
    $C09C: 8D D6 C3    STA $c3d6
    $C09F: 29 1F       AND #$1f
    $C0A1: 9D C6 C3    STA $c3c6,X
    $C0A4: 2C D6 C3    BIT $c3d6
    $C0A7: 70 38       BVS $c0e1      ; → L_C0E1
    $C0A9: FE C3 C3    INC $c3c3,X
    $C0AC: AD D6 C3    LDA $c3d6
    $C0AF: 10 0B       BPL $c0bc      ; → L_C0BC
    $C0B1: C8          INY
    $C0B2: B1 4D       LDA ($4d),Y
    $C0B4: 29 1F       AND #$1f
    $C0B6: 9D D2 C3    STA $c3d2,X
    $C0B9: FE C3 C3    INC $c3c3,X
L_C0BC:
    $C0BC: C8          INY
    $C0BD: B1 4D       LDA ($4d),Y
    $C0BF: 9D CF C3    STA $c3cf,X
    $C0C2: 0A          ASL A
    $C0C3: A8          TAY
    $C0C4: B9 FC C2    LDA $c2fc,Y
    $C0C7: 8D D7 C3    STA $c3d7
    $C0CA: A9 0F       LDA #$0f
    $C0CC: B9 FD C2    LDA $c2fd,Y
    $C0CF: AC BF C3    LDY $c3bf
    $C0D2: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
    $C0D5: 9D EB C3    STA $c3eb,X
    $C0D8: AD D7 C3    LDA $c3d7
    $C0DB: 99 00 D4    STA $D400 ;V1_FREQ_LO,Y
    $C0DE: 4C E4 C0    JMP $c0e4      ; → L_C0E4
L_C0E1:
    $C0E1: CE D5 C3    DEC $c3d5
L_C0E4:
    $C0E4: AC BF C3    LDY $c3bf
    $C0E7: BD D2 C3    LDA $c3d2,X
    $C0EA: 8E D8 C3    STX $c3d8
    $C0ED: 0A          ASL A
    $C0EE: 0A          ASL A
    $C0EF: 0A          ASL A
    $C0F0: AA          TAX
    $C0F1: BD 5D CB    LDA $cb5d,X
    $C0F4: 8D D9 C3    STA $c3d9
    $C0F7: BD 5D CB    LDA $cb5d,X
    $C0FA: 2D D5 C3    AND $c3d5
    $C0FD: 99 04 D4    STA $D404 ;V1_CTRL,Y
    $C100: BD 5B CB    LDA $cb5b,X
    $C103: 99 02 D4    STA $D402 ;V1_PW_LO,Y
    $C106: BD 5C CB    LDA $cb5c,X
    $C109: 99 03 D4    STA $D403 ;V1_PW_HI,Y
    $C10C: BD 5E CB    LDA $cb5e,X
    $C10F: 99 05 D4    STA $D405 ;V1_AD,Y
    $C112: BD 5F CB    LDA $cb5f,X
    $C115: 99 06 D4    STA $D406 ;V1_SR,Y
    $C118: AE D8 C3    LDX $c3d8
    $C11B: AD D9 C3    LDA $c3d9
    $C11E: 9D CC C3    STA $c3cc,X
    $C121: FE C3 C3    INC $c3c3,X
    $C124: BC C3 C3    LDY $c3c3,X
    $C127: B1 4D       LDA ($4d),Y
    $C129: C9 FF       CMP #$ff
    $C12B: D0 08       BNE $c135      ; → L_C135
    $C12D: A9 00       LDA #$00
    $C12F: 9D C3 C3    STA $c3c3,X
    $C132: FE C0 C3    INC $c3c0,X
L_C135:
    $C135: 4C 87 C2    JMP $c287      ; → L_C287
L_C138:
    $C138: AC BF C3    LDY $c3bf
    $C13B: BD C9 C3    LDA $c3c9,X
    $C13E: 29 20       AND #$20
    $C140: D0 15       BNE $c157      ; → L_C157
    $C142: BD C6 C3    LDA $c3c6,X
    $C145: D0 10       BNE $c157      ; → L_C157
    $C147: BD CC C3    LDA $c3cc,X
    $C14A: 29 FE       AND #$fe
    $C14C: 99 04 D4    STA $D404 ;V1_CTRL,Y
    $C14F: A9 00       LDA #$00
    $C151: 99 05 D4    STA $D405 ;V1_AD,Y
    $C154: 99 06 D4    STA $D406 ;V1_SR,Y
L_C157:
    $C157: BD D2 C3    LDA $c3d2,X
    $C15A: 0A          ASL A
    $C15B: 0A          ASL A
    $C15C: 0A          ASL A
    $C15D: A8          TAY
    $C15E: 8C E9 C3    STY $c3e9
    $C161: B9 62 CB    LDA $cb62,Y
    $C164: 8D EE C3    STA $c3ee
    $C167: B9 61 CB    LDA $cb61,Y
    $C16A: 8D DB C3    STA $c3db
    $C16D: B9 60 CB    LDA $cb60,Y
    $C170: 8D DA C3    STA $c3da
    $C173: F0 6F       BEQ $c1e4      ; → L_C1E4
    $C175: AD F0 C3    LDA $c3f0
    $C178: 29 07       AND #$07
    $C17A: C9 04       CMP #$04
    $C17C: 90 02       BCC $c180      ; → L_C180
    $C17E: 49 07       EOR #$07
L_C180:
    $C180: 8D E0 C3    STA $c3e0
    $C183: BD CF C3    LDA $c3cf,X
    $C186: 0A          ASL A
    $C187: A8          TAY
    $C188: 38          SEC
    $C189: B9 FE C2    LDA $c2fe,Y
    $C18C: F9 FC C2    SBC $c2fc,Y
    $C18F: 8D DC C3    STA $c3dc
    $C192: B9 FF C2    LDA $c2ff,Y
    $C195: F9 FD C2    SBC $c2fd,Y
L_C198:
    $C198: 4A          LSR A
    $C199: 6E DC C3    ROR $c3dc
    $C19C: CE DA C3    DEC $c3da
    $C19F: 10 F7       BPL $c198      ; → L_C198
    $C1A1: 8D DD C3    STA $c3dd
    $C1A4: B9 FC C2    LDA $c2fc,Y
    $C1A7: 8D DE C3    STA $c3de
    $C1AA: B9 FD C2    LDA $c2fd,Y
    $C1AD: 8D DF C3    STA $c3df
    $C1B0: BD C9 C3    LDA $c3c9,X
    $C1B3: 29 1F       AND #$1f
    $C1B5: C9 08       CMP #$08
    $C1B7: 90 1C       BCC $c1d5      ; → L_C1D5
    $C1B9: AC E0 C3    LDY $c3e0
L_C1BC:
    $C1BC: 88          DEY
    $C1BD: 30 16       BMI $c1d5      ; → L_C1D5
    $C1BF: 18          CLC
    $C1C0: AD DE C3    LDA $c3de
    $C1C3: 6D DC C3    ADC $c3dc
    $C1C6: 8D DE C3    STA $c3de
    $C1C9: AD DF C3    LDA $c3df
    $C1CC: 6D DD C3    ADC $c3dd
    $C1CF: 8D DF C3    STA $c3df
    $C1D2: 4C BC C1    JMP $c1bc      ; → L_C1BC
L_C1D5:
    $C1D5: AC BF C3    LDY $c3bf
    $C1D8: AD DE C3    LDA $c3de
    $C1DB: 99 00 D4    STA $D400 ;V1_FREQ_LO,Y
    $C1DE: AD DF C3    LDA $c3df
    $C1E1: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
L_C1E4:
    $C1E4: AD DB C3    LDA $c3db
    $C1E7: F0 62       BEQ $c24b      ; → L_C24B
    $C1E9: AC E9 C3    LDY $c3e9
    $C1EC: 29 1F       AND #$1f
    $C1EE: DE E1 C3    DEC $c3e1,X
    $C1F1: 10 58       BPL $c24b      ; → L_C24B
    $C1F3: 9D E1 C3    STA $c3e1,X
    $C1F6: AD DB C3    LDA $c3db
    $C1F9: 29 E0       AND #$e0
    $C1FB: 8D EF C3    STA $c3ef
    $C1FE: BD E4 C3    LDA $c3e4,X
    $C201: D0 1A       BNE $c21d      ; → L_C21D
    $C203: AD EF C3    LDA $c3ef
    $C206: 18          CLC
    $C207: 79 5B CB    ADC $cb5b,Y
    $C20A: 48          PHA
    $C20B: B9 5C CB    LDA $cb5c,Y
    $C20E: 69 00       ADC #$00
    $C210: 29 0F       AND #$0f
    $C212: 48          PHA
    $C213: C9 0E       CMP #$0e
    $C215: D0 1D       BNE $c234      ; → L_C234
    $C217: FE E4 C3    INC $c3e4,X
    $C21A: 4C 34 C2    JMP $c234      ; → L_C234
L_C21D:
    $C21D: 38          SEC
    $C21E: B9 5B CB    LDA $cb5b,Y
    $C221: ED EF C3    SBC $c3ef
    $C224: 48          PHA
    $C225: B9 5C CB    LDA $cb5c,Y
    $C228: E9 00       SBC #$00
    $C22A: 29 0F       AND #$0f
    $C22C: 48          PHA
    $C22D: C9 08       CMP #$08
    $C22F: D0 03       BNE $c234      ; → L_C234
    $C231: DE E4 C3    DEC $c3e4,X
L_C234:
    $C234: 8E D8 C3    STX $c3d8
    $C237: AE BF C3    LDX $c3bf
    $C23A: 68          PLA
    $C23B: 99 5C CB    STA $cb5c,Y
    $C23E: 9D 03 D4    STA $D403 ;V1_PW_HI,X
    $C241: 68          PLA
    $C242: 99 5B CB    STA $cb5b,Y
    $C245: 9D 02 D4    STA $D402 ;V1_PW_LO,X
    $C248: AE D8 C3    LDX $c3d8
L_C24B:
    $C24B: AD EE C3    LDA $c3ee
    $C24E: 29 01       AND #$01
    $C250: F0 35       BEQ $c287      ; → L_C287
    $C252: BD EB C3    LDA $c3eb,X
    $C255: F0 30       BEQ $c287      ; → L_C287
    $C257: BD C6 C3    LDA $c3c6,X
    $C25A: F0 2B       BEQ $c287      ; → L_C287
    $C25C: BD C9 C3    LDA $c3c9,X
    $C25F: 29 1F       AND #$1f
    $C261: 38          SEC
    $C262: E9 01       SBC #$01
    $C264: DD C6 C3    CMP $c3c6,X
    $C267: AC BF C3    LDY $c3bf
    $C26A: 90 10       BCC $c27c      ; → L_C27C
    $C26C: BD EB C3    LDA $c3eb,X
    $C26F: DE EB C3    DEC $c3eb,X
    $C272: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
    $C275: BD CC C3    LDA $c3cc,X
    $C278: 29 FE       AND #$fe
    $C27A: D0 08       BNE $c284      ; → L_C284
L_C27C:
    $C27C: BD EB C3    LDA $c3eb,X
    $C27F: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
    $C282: A9 80       LDA #$80
L_C284:
    $C284: 99 04 D4    STA $D404 ;V1_CTRL,Y
L_C287:
    $C287: CA          DEX
    $C288: 30 03       BMI $c28d      ; → L_C28D
    $C28A: 4C 39 C0    JMP $c039      ; → L_C039
L_C28D:
    $C28D: 60          RTS
sub_C28E:
    $C28E: AD EA C3    LDA $c3ea
    $C291: 29 03       AND #$03
    $C293: 8D EA C3    STA $c3ea
    $C296: 0A          ASL A
    $C297: 8D D7 C3    STA $c3d7
    $C29A: 0A          ASL A
    $C29B: 18          CLC
    $C29C: 6D D7 C3    ADC $c3d7
    $C29F: A0 01       LDY #$01
    $C2A1: AA          TAX
    $C2A2: F0 02       BEQ $c2a6      ; → L_C2A6
    $C2A4: A0 02       LDY #$02
L_C2A6:
    $C2A6: 8C F2 C3    STY $c3f2
    $C2A9: A0 00       LDY #$00
L_C2AB:
    $C2AB: BD F9 C3    LDA $c3f9,X
    $C2AE: 99 F3 C3    STA $c3f3,Y
    $C2B1: E8          INX
    $C2B2: C8          INY
    $C2B3: C0 06       CPY #$06
    $C2B5: D0 F4       BNE $c2ab      ; → L_C2AB
    $C2B7: A2 02       LDX #$02
    $C2B9: A9 00       LDA #$00
    $C2BB: 8D F0 C3    STA $c3f0
    $C2BE: 8D 04 D4    STA $D404 ;V1_CTRL
    $C2C1: 8D 0B D4    STA $D40B ;V2_CTRL
    $C2C4: 8D 12 D4    STA $D412 ;V3_CTRL
L_C2C7:
    $C2C7: 9D C0 C3    STA $c3c0,X
    $C2CA: 9D C3 C3    STA $c3c3,X
    $C2CD: 9D C6 C3    STA $c3c6,X
    $C2D0: 9D CF C3    STA $c3cf,X
    $C2D3: CA          DEX
    $C2D4: 10 F1       BPL $c2c7      ; → L_C2C7
    $C2D6: A9 0F       LDA #$0f
    $C2D8: 8D 18 D4    STA $D418 ;VOL
    $C2DB: 60          RTS
L_C2DC:
    $C2DC: A9 80       LDA #$80
    $C2DE: 8D EA C3    STA $c3ea
    $C2E1: A2 17       LDX #$17
L_C2E3:
    $C2E3: 9D 00 D4    STA $D400 ;V1_FREQ_LO,X
    $C2E6: CA          DEX
    $C2E7: 10 FA       BPL $c2e3      ; → L_C2E3
    $C2E9: 60          RTS
; ----- data gap $C2EA-$CBBA (2257 bytes) -----


; ======= init: =======
init:
    $CBBB: 18          CLC
    $CBBC: 69 40       ADC #$40
    $CBBE: 8D EA C3    STA $c3ea
    $CBC1: 60          RTS
