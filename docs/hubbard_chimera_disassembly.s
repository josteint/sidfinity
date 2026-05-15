; ============================================================================
; Rob Hubbard - Chimera (1985 Firebird)
; ANNOTATED DISASSEMBLY (auto-generated seed; hand-annotate after generation)
; ============================================================================
;
; Binary: data/C64Music/MUSICIANS/H/Hubbard_Rob/Chimera.sid
; Load:   $9F80   Init: $9F80   Play: $0000 (PSID claims 0; IRQ-driven via $0314/$0315)
; PSID:   4 subtunes, default subtune 1 (1-indexed)
; Binary: $9F80-$CF9A (12314 bytes)
;
; Entry points traced: $9F80, $9FA0, $9FB0, $C200, $C203, $C206
;   $9F80 = PSID init wrapper (subtunes 0-1: music)
;   $9FA0 = IRQ handler installed by wrapper (calls $C206)
;   $9FB0 = PSID init wrapper (subtunes >=2: SFX dispatch)
;   $C200 = engine init vector (JMP $CF63)
;   $C203 = engine stop vector (JMP $CF94, sets state=$C0)
;   $C206 = engine play entry (called from IRQ at $9FA3)
;
; Reachable code: 1330/12314 bytes (10.8%).
; Everything outside the reachable set is data: orderlists, freq table,
; pattern data, instrument records, etc.
;
; ============================================================================

L_9F80:
    $9F80: C9 02      cmp  #$02
    $9F82: B0 68      bcs  $9FEC      ; → L_9FEC
    $9F84: 48         pha 
    $9F85: 78         sei 
    $9F86: A9 9F      lda  #$9F
    $9F88: 8D 15 03   sta  $0315
    $9F8B: A9 A0      lda  #$A0
    $9F8D: 8D 14 03   sta  $0314
    $9F90: A2 00      ldx  #$00
    $9F92: 8E 0E DC   stx  $DC0E
    $9F95: E8         inx 
    $9F96: 8E 1A D0   stx  $D01A
    $9F99: 68         pla 
    $9F9A: 20 00 C2   jsr  $C200      ; → L_C200
    $9F9D: 58         cli 
    $9F9E: EA         nop 
    $9F9F: 60         rts 
L_9FA0:
    $9FA0: EE 19 D0   inc  $D019
    $9FA3: 20 06 C2   jsr  $C206      ; → L_C206
    $9FA6: 4C 31 EA   jmp  $EA31      ; → L_EA31
; ----- data gap $9FA9-$9FB0 (7 bytes) -----

L_9FB0:
    $9FB0: 48         pha 
    $9FB1: 78         sei 
    $9FB2: A9 31      lda  #$31
    $9FB4: 8D 14 03   sta  $0314
    $9FB7: A9 EA      lda  #$EA
    $9FB9: 8D 15 03   sta  $0315
    $9FBC: A2 01      ldx  #$01
    $9FBE: 8E 0E DC   stx  $DC0E
    $9FC1: CA         dex 
    $9FC2: 8E 1A D0   stx  $D01A
    $9FC5: EA         nop 
    $9FC6: 68         pla 
    $9FC7: 38         sec 
    $9FC8: E9 02      sbc  #$02
    $9FCA: AA         tax 
    $9FCB: A9 35      lda  #$35
    $9FCD: 85 01      sta  $01
    $9FCF: BD E2 9F   lda  $9FE2,X
    $9FD2: 8D 0A A1   sta  $A10A
    $9FD5: BD E4 9F   lda  $9FE4,X
    $9FD8: 85 97      sta  $97
    $9FDA: A9 37      lda  #$37
    $9FDC: 85 01      sta  $01
    $9FDE: 4C 00 C0   jmp  $C000      ; → L_C000
; ----- data gap $9FE1-$9FEC (11 bytes) -----

L_9FEC:
    $9FEC: 48         pha 
    $9FED: A9 00      lda  #$00
    $9FEF: 85 FD      sta  $FD
    $9FF1: A2 00      ldx  #$00
L_9FF3:
    $9FF3: 9D 00 D4   sta  $D400,X
    $9FF6: E8         inx 
    $9FF7: E0 19      cpx  #$19
    $9FF9: D0 F8      bne  $9FF3      ; → L_9FF3
    $9FFB: 68         pla 
    $9FFC: 4C B0 9F   jmp  $9FB0      ; → L_9FB0
; ----- data gap $9FFF-$C000 (8193 bytes) -----

L_C000:
    $C000: 4C 06 C0   jmp  $C006      ; → L_C006
; ----- data gap $C003-$C006 (3 bytes) -----

L_C006:
    $C006: A5 F7      lda  $F7
    $C008: 48         pha 
    $C009: A5 F8      lda  $F8
    $C00B: 48         pha 
    $C00C: A5 F9      lda  $F9
    $C00E: 48         pha 
    $C00F: A5 FA      lda  $FA
    $C011: 48         pha 
    $C012: 78         sei 
    $C013: A9 3E      lda  #$3E
    $C015: 25 01      and  $01
    $C017: 85 01      sta  $01
    $C019: AD 11 D0   lda  $D011
    $C01C: 8D 30 C1   sta  $C130
    $C01F: A2 00      ldx  #$00
    $C021: AC 03 A1   ldy  $A103
    $C024: C0 00      cpy  #$00
    $C026: D0 06      bne  $C02E      ; → L_C02E
    $C028: 20 09 C1   jsr  $C109      ; → L_C109
    $C02B: 4C EA C0   jmp  $C0EA      ; → L_C0EA
L_C02E:
    $C02E: BD 0B A1   lda  $A10B,X
    $C031: C5 97      cmp  $97
    $C033: F0 0A      beq  $C03F      ; → L_C03F
    $C035: E8         inx 
    $C036: 88         dey 
    $C037: D0 F5      bne  $C02E      ; → L_C02E
    $C039: 20 09 C1   jsr  $C109      ; → L_C109
    $C03C: 4C EA C0   jmp  $C0EA      ; → L_C0EA
L_C03F:
    $C03F: AD 0A A1   lda  $A10A
    $C042: 8D AC C0   sta  $C0AC
    $C045: A5 97      lda  $97
    $C047: 0A         asl  A
    $C048: 0A         asl  A
    $C049: AA         tax 
    $C04A: BD 00 A0   lda  $A000,X
    $C04D: 85 FB      sta  $FB
    $C04F: BD 01 A0   lda  $A001,X
    $C052: 85 FC      sta  $FC
    $C054: BD 02 A0   lda  $A002,X
    $C057: 85 F7      sta  $F7
    $C059: BD 03 A0   lda  $A003,X
    $C05C: 85 F8      sta  $F8
    $C05E: A9 FF      lda  #$FF
    $C060: 8D 02 D4   sta  $D402
    $C063: 8D 03 D4   sta  $D403
    $C066: 8D 04 DD   sta  $DD04
    $C069: 8D 05 DD   sta  $DD05
    $C06C: A0 00      ldy  #$00
    $C06E: A9 F0      lda  #$F0
    $C070: 8D 06 D4   sta  $D406
    $C073: AD 08 A1   lda  $A108
    $C076: D0 05      bne  $C07D      ; → L_C07D
    $C078: A9 00      lda  #$00
    $C07A: 8D 11 D0   sta  $D011
L_C07D:
    $C07D: A9 11      lda  #$11
    $C07F: 8D 0E DD   sta  $DD0E
    $C082: EA         nop 
    $C083: EA         nop 
    $C084: EA         nop 
    $C085: EA         nop 
    $C086: EA         nop 
    $C087: EA         nop 
    $C088: 4C CF C0   jmp  $C0CF      ; → L_C0CF
L_C08B:
    $C08B: E6 FB      inc  $FB
    $C08D: D0 02      bne  $C091      ; → L_C091
    $C08F: E6 FC      inc  $FC
L_C091:
    $C091: A6 FC      ldx  $FC
    $C093: E4 F8      cpx  $F8
    $C095: 90 09      bcc  $C0A0      ; → L_C0A0
    $C097: A6 FB      ldx  $FB
    $C099: E4 F7      cpx  $F7
    $C09B: 90 03      bcc  $C0A0      ; → L_C0A0
    $C09D: 4C EA C0   jmp  $C0EA      ; → L_C0EA
L_C0A0:
    $C0A0: A9 08      lda  #$08
    $C0A2: 85 96      sta  $96
    $C0A4: B1 FB      lda  ($FB),Y
    $C0A6: 85 FE      sta  $FE
L_C0A8:
    $C0A8: AD 04 DD   lda  $DD04
    $C0AB: C9 B0      cmp  #$B0
    $C0AD: B0 F9      bcs  $C0A8      ; → L_C0A8
    $C0AF: A9 11      lda  #$11
    $C0B1: 8D 0E DD   sta  $DD0E
    $C0B4: 06 FE      asl  $FE
    $C0B6: 90 04      bcc  $C0BC      ; → L_C0BC
    $C0B8: A9 49      lda  #$49
    $C0BA: D0 02      bne  $C0BE      ; → L_C0BE
L_C0BC:
    $C0BC: A9 41      lda  #$41
L_C0BE:
    $C0BE: 8D 04 D4   sta  $D404
    $C0C1: C6 96      dec  $96
    $C0C3: D0 E3      bne  $C0A8      ; → L_C0A8
    $C0C5: C6 F9      dec  $F9
    $C0C7: D0 C2      bne  $C08B      ; → L_C08B
    $C0C9: E6 FB      inc  $FB
    $C0CB: D0 02      bne  $C0CF      ; → L_C0CF
    $C0CD: E6 FC      inc  $FC
L_C0CF:
    $C0CF: B1 FB      lda  ($FB),Y
    $C0D1: C9 10      cmp  #$10
    $C0D3: 90 02      bcc  $C0D7      ; → L_C0D7
    $C0D5: A9 0F      lda  #$0F
L_C0D7:
    $C0D7: 38         sec 
    $C0D8: E5 FD      sbc  $FD
    $C0DA: 30 02      bmi  $C0DE      ; → L_C0DE
    $C0DC: D0 02      bne  $C0E0      ; → L_C0E0
L_C0DE:
    $C0DE: A9 01      lda  #$01
L_C0E0:
    $C0E0: 8D 18 D4   sta  $D418
    $C0E3: A9 10      lda  #$10
    $C0E5: 85 F9      sta  $F9
    $C0E7: 4C 8B C0   jmp  $C08B      ; → L_C08B
L_C0EA:
    $C0EA: A9 00      lda  #$00
    $C0EC: 8D 18 D4   sta  $D418
    $C0EF: AD 30 C1   lda  $C130
    $C0F2: 8D 11 D0   sta  $D011
    $C0F5: A9 03      lda  #$03
    $C0F7: 05 01      ora  $01
    $C0F9: 85 01      sta  $01
    $C0FB: 68         pla 
    $C0FC: 85 FA      sta  $FA
    $C0FE: 68         pla 
    $C0FF: 85 F9      sta  $F9
    $C101: 68         pla 
    $C102: 85 F8      sta  $F8
    $C104: 68         pla 
    $C105: 85 F7      sta  $F7
    $C107: 58         cli 
    $C108: 60         rts 
L_C109:
    $C109: A9 2A      lda  #$2A
    $C10B: 8D 08 D4   sta  $D408
    $C10E: A9 F0      lda  #$F0
    $C110: 8D 0D D4   sta  $D40D
    $C113: A9 0F      lda  #$0F
    $C115: 8D 18 D4   sta  $D418
    $C118: A9 11      lda  #$11
    $C11A: 8D 0B D4   sta  $D40B
    $C11D: A0 FF      ldy  #$FF
L_C11F:
    $C11F: A2 FF      ldx  #$FF
L_C121:
    $C121: CA         dex 
    $C122: D0 FD      bne  $C121      ; → L_C121
    $C124: 88         dey 
    $C125: D0 F8      bne  $C11F      ; → L_C11F
    $C127: A9 00      lda  #$00
    $C129: 8D 0B D4   sta  $D40B
    $C12C: 8D 18 D4   sta  $D418
    $C12F: 60         rts 
; ----- data gap $C130-$C200 (208 bytes) -----

L_C200:
    $C200: 4C 63 CF   jmp  $CF63      ; → L_CF63
L_C203:
    $C203: 4C 94 CF   jmp  $CF94      ; → L_CF94
L_C206:
    $C206: EE 61 C6   inc  $C661
    $C209: 2C 55 C6   bit  $C655
    $C20C: 30 1E      bmi  $C22C      ; → L_C22C
    $C20E: 50 31      bvc  $C241      ; → L_C241
    $C210: A9 00      lda  #$00
    $C212: 8D 61 C6   sta  $C661
    $C215: A2 02      ldx  #$02
L_C217:
    $C217: 9D 2B C6   sta  $C62B,X
    $C21A: 9D 2E C6   sta  $C62E,X
    $C21D: 9D 31 C6   sta  $C631,X
    $C220: 9D 3A C6   sta  $C63A,X
    $C223: CA         dex 
    $C224: 10 F1      bpl  $C217      ; → L_C217
    $C226: 8D 55 C6   sta  $C655
    $C229: 4C 41 C2   jmp  $C241      ; → L_C241
L_C22C:
    $C22C: 50 10      bvc  $C23E      ; → L_C23E
    $C22E: A9 00      lda  #$00
    $C230: 8D 04 D4   sta  $D404
    $C233: 8D 0B D4   sta  $D40B
    $C236: 8D 12 D4   sta  $D412
    $C239: A9 80      lda  #$80
    $C23B: 8D 55 C6   sta  $C655
L_C23E:
    $C23E: 4C 66 C5   jmp  $C566      ; → L_C566
L_C241:
    $C241: A2 02      ldx  #$02
    $C243: CE 52 C6   dec  $C652
    $C246: 10 06      bpl  $C24E      ; → L_C24E
    $C248: AD 53 C6   lda  $C653
    $C24B: 8D 52 C6   sta  $C652
L_C24E:
    $C24E: BD 27 C6   lda  $C627,X
    $C251: 8D 2A C6   sta  $C62A
    $C254: A8         tay 
    $C255: AD 52 C6   lda  $C652
    $C258: CD 53 C6   cmp  $C653
    $C25B: D0 15      bne  $C272      ; → L_C272
    $C25D: BD FA C6   lda  $C6FA,X
    $C260: 85 56      sta  $56
    $C262: BD FD C6   lda  $C6FD,X
    $C265: 85 57      sta  $57
    $C267: DE 31 C6   dec  $C631,X
    $C26A: 30 09      bmi  $C275      ; → L_C275
    $C26C: 4C 56 C3   jmp  $C356      ; → L_C356
; ----- data gap $C26F-$C272 (3 bytes) -----

L_C272:
    $C272: 4C 75 C3   jmp  $C375      ; → L_C375
L_C275:
    $C275: BC 2B C6   ldy  $C62B,X
    $C278: B1 56      lda  ($56),Y
    $C27A: C9 FE      cmp  #$FE
    $C27C: D0 03      bne  $C281      ; → L_C281
    $C27E: 4C 03 C2   jmp  $C203      ; → L_C203
L_C281:
    $C281: C9 FF      cmp  #$FF
    $C283: D0 11      bne  $C296      ; → L_C296
    $C285: A9 00      lda  #$00
    $C287: 9D 31 C6   sta  $C631,X
    $C28A: 9D 2B C6   sta  $C62B,X
    $C28D: 9D 2E C6   sta  $C62E,X
    $C290: 4C 75 C2   jmp  $C275      ; → L_C275
; ----- data gap $C293-$C296 (3 bytes) -----

L_C296:
    $C296: A8         tay 
    $C297: B9 0C C7   lda  $C70C,Y
    $C29A: 85 58      sta  $58
    $C29C: B9 3D C7   lda  $C73D,Y
    $C29F: 85 59      sta  $59
    $C2A1: A9 00      lda  #$00
    $C2A3: 9D 5C C6   sta  $C65C,X
    $C2A6: BC 2E C6   ldy  $C62E,X
    $C2A9: A9 FF      lda  #$FF
    $C2AB: 8D 40 C6   sta  $C640
    $C2AE: B1 58      lda  ($58),Y
    $C2B0: 9D 34 C6   sta  $C634,X
    $C2B3: 8D 41 C6   sta  $C641
    $C2B6: 29 1F      and  #$1F
    $C2B8: 9D 31 C6   sta  $C631,X
    $C2BB: 2C 41 C6   bit  $C641
    $C2BE: 70 3F      bvs  $C2FF      ; → L_C2FF
    $C2C0: FE 2E C6   inc  $C62E,X
    $C2C3: AD 41 C6   lda  $C641
    $C2C6: 10 11      bpl  $C2D9      ; → L_C2D9
    $C2C8: C8         iny 
    $C2C9: B1 58      lda  ($58),Y
    $C2CB: 10 06      bpl  $C2D3      ; → L_C2D3
    $C2CD: 9D 5C C6   sta  $C65C,X
    $C2D0: 4C D6 C2   jmp  $C2D6      ; → L_C2D6
L_C2D3:
    $C2D3: 9D 3D C6   sta  $C63D,X
L_C2D6:
    $C2D6: FE 2E C6   inc  $C62E,X
L_C2D9:
    $C2D9: C8         iny 
    $C2DA: B1 58      lda  ($58),Y
    $C2DC: 9D 3A C6   sta  $C63A,X
    $C2DF: 0A         asl  A
    $C2E0: A8         tay 
    $C2E1: B9 67 C5   lda  $C567,Y
    $C2E4: 8D 42 C6   sta  $C642
    $C2E7: B9 68 C5   lda  $C568,Y
    $C2EA: AC 2A C6   ldy  $C62A
    $C2ED: 99 01 D4   sta  $D401,Y
    $C2F0: 9D 56 C6   sta  $C656,X
    $C2F3: AD 42 C6   lda  $C642
    $C2F6: 99 00 D4   sta  $D400,Y
    $C2F9: 9D 59 C6   sta  $C659,X
    $C2FC: 4C 02 C3   jmp  $C302      ; → L_C302
L_C2FF:
    $C2FF: CE 40 C6   dec  $C640
L_C302:
    $C302: AC 2A C6   ldy  $C62A
    $C305: BD 3D C6   lda  $C63D,X
    $C308: 8E 43 C6   stx  $C643
    $C30B: 0A         asl  A
    $C30C: 0A         asl  A
    $C30D: 0A         asl  A
    $C30E: AA         tax 
    $C30F: BD 64 C6   lda  $C664,X
    $C312: 8D 44 C6   sta  $C644
    $C315: BD 64 C6   lda  $C664,X
    $C318: 2D 40 C6   and  $C640
    $C31B: 99 04 D4   sta  $D404,Y
    $C31E: BD 62 C6   lda  $C662,X
    $C321: 99 02 D4   sta  $D402,Y
    $C324: BD 63 C6   lda  $C663,X
    $C327: 99 03 D4   sta  $D403,Y
    $C32A: BD 65 C6   lda  $C665,X
    $C32D: 99 05 D4   sta  $D405,Y
    $C330: BD 66 C6   lda  $C666,X
    $C333: 99 06 D4   sta  $D406,Y
    $C336: AE 43 C6   ldx  $C643
    $C339: AD 44 C6   lda  $C644
    $C33C: 9D 37 C6   sta  $C637,X
    $C33F: FE 2E C6   inc  $C62E,X
    $C342: BC 2E C6   ldy  $C62E,X
    $C345: B1 58      lda  ($58),Y
    $C347: C9 FF      cmp  #$FF
    $C349: D0 08      bne  $C353      ; → L_C353
    $C34B: A9 00      lda  #$00
    $C34D: 9D 2E C6   sta  $C62E,X
    $C350: FE 2B C6   inc  $C62B,X
L_C353:
    $C353: 4C 60 C5   jmp  $C560      ; → L_C560
L_C356:
    $C356: AC 2A C6   ldy  $C62A
    $C359: BD 34 C6   lda  $C634,X
    $C35C: 29 20      and  #$20
    $C35E: D0 15      bne  $C375      ; → L_C375
    $C360: BD 31 C6   lda  $C631,X
    $C363: D0 10      bne  $C375      ; → L_C375
    $C365: BD 37 C6   lda  $C637,X
    $C368: 29 FE      and  #$FE
    $C36A: 99 04 D4   sta  $D404,Y
    $C36D: A9 00      lda  #$00
    $C36F: 99 05 D4   sta  $D405,Y
    $C372: 99 06 D4   sta  $D406,Y
L_C375:
    $C375: BD 3D C6   lda  $C63D,X
    $C378: 0A         asl  A
    $C379: 0A         asl  A
    $C37A: 0A         asl  A
    $C37B: A8         tay 
    $C37C: 8C 54 C6   sty  $C654
    $C37F: B9 69 C6   lda  $C669,Y
    $C382: 8D 5F C6   sta  $C65F
    $C385: B9 68 C6   lda  $C668,Y
    $C388: 8D 46 C6   sta  $C646
    $C38B: B9 67 C6   lda  $C667,Y
    $C38E: 8D 45 C6   sta  $C645
    $C391: F0 6F      beq  $C402      ; → L_C402
    $C393: AD 61 C6   lda  $C661
    $C396: 29 07      and  #$07
    $C398: C9 04      cmp  #$04
    $C39A: 90 02      bcc  $C39E      ; → L_C39E
    $C39C: 49 07      eor  #$07
L_C39E:
    $C39E: 8D 4B C6   sta  $C64B
    $C3A1: BD 3A C6   lda  $C63A,X
    $C3A4: 0A         asl  A
    $C3A5: A8         tay 
    $C3A6: 38         sec 
    $C3A7: B9 69 C5   lda  $C569,Y
    $C3AA: F9 67 C5   sbc  $C567,Y
    $C3AD: 8D 47 C6   sta  $C647
    $C3B0: B9 6A C5   lda  $C56A,Y
    $C3B3: F9 68 C5   sbc  $C568,Y
L_C3B6:
    $C3B6: 4A         lsr  A
    $C3B7: 6E 47 C6   ror  $C647
    $C3BA: CE 45 C6   dec  $C645
    $C3BD: 10 F7      bpl  $C3B6      ; → L_C3B6
    $C3BF: 8D 48 C6   sta  $C648
    $C3C2: B9 67 C5   lda  $C567,Y
    $C3C5: 8D 49 C6   sta  $C649
    $C3C8: B9 68 C5   lda  $C568,Y
    $C3CB: 8D 4A C6   sta  $C64A
    $C3CE: BD 34 C6   lda  $C634,X
    $C3D1: 29 1F      and  #$1F
    $C3D3: C9 08      cmp  #$08
    $C3D5: 90 1C      bcc  $C3F3      ; → L_C3F3
    $C3D7: AC 4B C6   ldy  $C64B
L_C3DA:
    $C3DA: 88         dey 
    $C3DB: 30 16      bmi  $C3F3      ; → L_C3F3
    $C3DD: 18         clc 
    $C3DE: AD 49 C6   lda  $C649
    $C3E1: 6D 47 C6   adc  $C647
    $C3E4: 8D 49 C6   sta  $C649
    $C3E7: AD 4A C6   lda  $C64A
    $C3EA: 6D 48 C6   adc  $C648
    $C3ED: 8D 4A C6   sta  $C64A
    $C3F0: 4C DA C3   jmp  $C3DA      ; → L_C3DA
L_C3F3:
    $C3F3: AC 2A C6   ldy  $C62A
    $C3F6: AD 49 C6   lda  $C649
    $C3F9: 99 00 D4   sta  $D400,Y
    $C3FC: AD 4A C6   lda  $C64A
    $C3FF: 99 01 D4   sta  $D401,Y
L_C402:
    $C402: AD 5F C6   lda  $C65F
    $C405: 29 08      and  #$08
    $C407: F0 17      beq  $C420      ; → L_C420
    $C409: AC 54 C6   ldy  $C654
    $C40C: B9 62 C6   lda  $C662,Y
    $C40F: 6D 46 C6   adc  $C646
    $C412: 09 40      ora  #$40
    $C414: 99 62 C6   sta  $C662,Y
    $C417: AC 2A C6   ldy  $C62A
    $C41A: 99 02 D4   sta  $D402,Y
    $C41D: 4C 87 C4   jmp  $C487      ; → L_C487
L_C420:
    $C420: AD 46 C6   lda  $C646
    $C423: F0 62      beq  $C487      ; → L_C487
    $C425: AC 54 C6   ldy  $C654
    $C428: 29 1F      and  #$1F
    $C42A: DE 4C C6   dec  $C64C,X
    $C42D: 10 58      bpl  $C487      ; → L_C487
    $C42F: 9D 4C C6   sta  $C64C,X
    $C432: AD 46 C6   lda  $C646
    $C435: 29 E0      and  #$E0
    $C437: 8D 60 C6   sta  $C660
    $C43A: BD 4F C6   lda  $C64F,X
    $C43D: D0 1A      bne  $C459      ; → L_C459
    $C43F: AD 60 C6   lda  $C660
    $C442: 18         clc 
    $C443: 79 62 C6   adc  $C662,Y
    $C446: 48         pha 
    $C447: B9 63 C6   lda  $C663,Y
    $C44A: 69 00      adc  #$00
    $C44C: 29 0F      and  #$0F
    $C44E: 48         pha 
    $C44F: C9 0E      cmp  #$0E
    $C451: D0 1D      bne  $C470      ; → L_C470
    $C453: FE 4F C6   inc  $C64F,X
    $C456: 4C 70 C4   jmp  $C470      ; → L_C470
L_C459:
    $C459: 38         sec 
    $C45A: B9 62 C6   lda  $C662,Y
    $C45D: ED 60 C6   sbc  $C660
    $C460: 48         pha 
    $C461: B9 63 C6   lda  $C663,Y
    $C464: E9 00      sbc  #$00
    $C466: 29 0F      and  #$0F
    $C468: 48         pha 
    $C469: C9 08      cmp  #$08
    $C46B: D0 03      bne  $C470      ; → L_C470
    $C46D: DE 4F C6   dec  $C64F,X
L_C470:
    $C470: 8E 43 C6   stx  $C643
    $C473: AE 2A C6   ldx  $C62A
    $C476: 68         pla 
    $C477: 99 63 C6   sta  $C663,Y
    $C47A: 9D 03 D4   sta  $D403,X
    $C47D: 68         pla 
    $C47E: 99 62 C6   sta  $C662,Y
    $C481: 9D 02 D4   sta  $D402,X
    $C484: AE 43 C6   ldx  $C643
L_C487:
    $C487: AC 2A C6   ldy  $C62A
    $C48A: BD 5C C6   lda  $C65C,X
    $C48D: F0 3F      beq  $C4CE      ; → L_C4CE
    $C48F: 29 7E      and  #$7E
    $C491: 8D 43 C6   sta  $C643
    $C494: BD 5C C6   lda  $C65C,X
    $C497: 29 01      and  #$01
    $C499: F0 1B      beq  $C4B6      ; → L_C4B6
    $C49B: 38         sec 
    $C49C: BD 59 C6   lda  $C659,X
    $C49F: ED 43 C6   sbc  $C643
    $C4A2: 9D 59 C6   sta  $C659,X
    $C4A5: 99 00 D4   sta  $D400,Y
    $C4A8: BD 56 C6   lda  $C656,X
    $C4AB: E9 00      sbc  #$00
    $C4AD: 9D 56 C6   sta  $C656,X
    $C4B0: 99 01 D4   sta  $D401,Y
    $C4B3: 4C CE C4   jmp  $C4CE      ; → L_C4CE
L_C4B6:
    $C4B6: 18         clc 
    $C4B7: BD 59 C6   lda  $C659,X
    $C4BA: 6D 43 C6   adc  $C643
    $C4BD: 9D 59 C6   sta  $C659,X
    $C4C0: 99 00 D4   sta  $D400,Y
    $C4C3: BD 56 C6   lda  $C656,X
    $C4C6: 69 00      adc  #$00
    $C4C8: 9D 56 C6   sta  $C656,X
    $C4CB: 99 01 D4   sta  $D401,Y
L_C4CE:
    $C4CE: AD 5F C6   lda  $C65F
    $C4D1: 29 01      and  #$01
    $C4D3: F0 35      beq  $C50A      ; → L_C50A
    $C4D5: BD 56 C6   lda  $C656,X
    $C4D8: F0 30      beq  $C50A      ; → L_C50A
    $C4DA: BD 31 C6   lda  $C631,X
    $C4DD: F0 2B      beq  $C50A      ; → L_C50A
    $C4DF: BD 34 C6   lda  $C634,X
    $C4E2: 29 1F      and  #$1F
    $C4E4: 38         sec 
    $C4E5: E9 01      sbc  #$01
    $C4E7: DD 31 C6   cmp  $C631,X
    $C4EA: AC 2A C6   ldy  $C62A
    $C4ED: 90 10      bcc  $C4FF      ; → L_C4FF
    $C4EF: BD 56 C6   lda  $C656,X
    $C4F2: DE 56 C6   dec  $C656,X
    $C4F5: 99 01 D4   sta  $D401,Y
    $C4F8: BD 37 C6   lda  $C637,X
    $C4FB: 29 FE      and  #$FE
    $C4FD: D0 08      bne  $C507      ; → L_C507
L_C4FF:
    $C4FF: BD 56 C6   lda  $C656,X
    $C502: 99 01 D4   sta  $D401,Y
    $C505: A9 80      lda  #$80
L_C507:
    $C507: 99 04 D4   sta  $D404,Y
L_C50A:
    $C50A: AD 5F C6   lda  $C65F
    $C50D: 29 02      and  #$02
    $C50F: F0 1E      beq  $C52F      ; → L_C52F
    $C511: BD 34 C6   lda  $C634,X
    $C514: 29 1F      and  #$1F
    $C516: C9 11      cmp  #$11
    $C518: 90 15      bcc  $C52F      ; → L_C52F
    $C51A: AD 61 C6   lda  $C661
    $C51D: 29 01      and  #$01
    $C51F: F0 0E      beq  $C52F      ; → L_C52F
    $C521: BD 56 C6   lda  $C656,X
    $C524: F0 09      beq  $C52F      ; → L_C52F
    $C526: FE 56 C6   inc  $C656,X
    $C529: AC 2A C6   ldy  $C62A
    $C52C: 99 01 D4   sta  $D401,Y
L_C52F:
    $C52F: AD 5F C6   lda  $C65F
    $C532: 29 04      and  #$04
    $C534: F0 2A      beq  $C560      ; → L_C560
    $C536: AD 61 C6   lda  $C661
    $C539: 29 07      and  #$07
    $C53B: F0 09      beq  $C546      ; → L_C546
    $C53D: BD 3A C6   lda  $C63A,X
    $C540: 18         clc 
    $C541: 69 0C      adc  #$0C
    $C543: 4C 49 C5   jmp  $C549      ; → L_C549
L_C546:
    $C546: BD 3A C6   lda  $C63A,X
L_C549:
    $C549: 0A         asl  A
    $C54A: A8         tay 
    $C54B: B9 67 C5   lda  $C567,Y
    $C54E: 8D 42 C6   sta  $C642
    $C551: B9 68 C5   lda  $C568,Y
    $C554: AC 2A C6   ldy  $C62A
    $C557: 99 01 D4   sta  $D401,Y
    $C55A: AD 42 C6   lda  $C642
    $C55D: 99 00 D4   sta  $D400,Y
L_C560:
    $C560: CA         dex 
    $C561: 30 03      bmi  $C566      ; → L_C566
    $C563: 4C 4E C2   jmp  $C24E      ; → L_C24E
L_C566:
    $C566: 60         rts 
; ----- data gap $C567-$CF63 (2556 bytes) -----

L_CF63:
    $CF63: A0 00      ldy  #$00
    $CF65: 0A         asl  A
    $CF66: 8D 43 C6   sta  $C643
    $CF69: 0A         asl  A
    $CF6A: 18         clc 
    $CF6B: 6D 43 C6   adc  $C643
    $CF6E: AA         tax 
L_CF6F:
    $CF6F: BD 00 C7   lda  $C700,X
    $CF72: 99 FA C6   sta  $C6FA,Y
    $CF75: E8         inx 
    $CF76: C8         iny 
    $CF77: C0 06      cpy  #$06
    $CF79: D0 F4      bne  $CF6F      ; → L_CF6F
    $CF7B: A9 00      lda  #$00
    $CF7D: 8D 17 D4   sta  $D417
    $CF80: 8D 04 D4   sta  $D404
    $CF83: 8D 0B D4   sta  $D40B
    $CF86: 8D 12 D4   sta  $D412
    $CF89: A9 0F      lda  #$0F
    $CF8B: 8D 18 D4   sta  $D418
    $CF8E: A9 40      lda  #$40
    $CF90: 8D 55 C6   sta  $C655
    $CF93: 60         rts 
L_CF94:
    $CF94: A9 C0      lda  #$C0
    $CF96: 8D 55 C6   sta  $C655
    $CF99: 60         rts 

; ============================================================================
; END OF REACHABLE CODE
; ============================================================================
