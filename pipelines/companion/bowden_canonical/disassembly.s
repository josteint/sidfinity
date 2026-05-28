; ============================================================================
; Rob Hubbard - Bach Sonata (1989 Commodore Disk User)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/B/Berry_Vic/Bach_Sonata.sid
; Load:   $C002   Init: $C053   Play: $C003
; PSID:   1 subtune(s), default subtune 1
; Binary: $C002-$CDFE (3581 bytes)
;
; Auto-traced 211 reachable code bytes from init+play.
;
; ============================================================================

L_C002:
    $C002: 60         RTS           
; ======= play: =======
play:
    $C003: AE 7C C0   LDX $c07c     
    $C006: E8         INX           
    $C007: 8E 7C C0   STX $c07c     
    $C00A: EC 7B C0   CPX $c07b     
    $C00D: D0 F3      BNE $c002        ; → L_C002
    $C00F: A9 00      LDA #$00      
    $C011: 8D 7C C0   STA $c07c     
    $C014: 4C 80 C0   JMP $c080        ; → L_C080
; ----- data gap $C017-$C02B (21 bytes) -----

L_C02C:
    $C02C: A9 00      LDA #$00      
    $C02E: 8D 7C C0   STA $c07c     
    $C031: 8D 17 C0   STA $c017     
    $C034: 8D 18 C0   STA $c018     
    $C037: 60         RTS           
; ----- data gap $C038-$C052 (27 bytes) -----

; ======= init: =======
init:
    $C053: A9 00      LDA #$00      
    $C055: A2 00      LDX #$00      
L_C057:
    $C057: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $C05A: E8         INX           
    $C05B: E0 19      CPX #$19      
    $C05D: D0 F8      BNE $c057        ; → L_C057
    $C05F: A9 0F      LDA #$0f      
    $C061: 8D 18 D4   STA $d418      ;VOL
    $C064: A9 09      LDA #$09      
    $C066: 8D 05 D4   STA $d405      ;V1_AD
    $C069: A9 00      LDA #$00      
    $C06B: 8D 06 D4   STA $d406      ;V1_SR
    $C06E: A9 09      LDA #$09      
    $C070: 8D 0C D4   STA $d40c      ;V2_AD
    $C073: A9 00      LDA #$00      
    $C075: 8D 0D D4   STA $d40d      ;V2_SR
    $C078: 4C 2C C0   JMP $c02c        ; → L_C02C
; ----- data gap $C07B-$C07F (5 bytes) -----

L_C080:
    $C080: AE 17 C0   LDX $c017     
    $C083: EE 17 C0   INC $c017     
    $C086: BC 00 CB   LDY $cb00,x   
    $C089: A2 00      LDX #$00      
    $C08B: 20 AD C0   JSR $c0ad        ; → sub_C0AD
    $C08E: AE 1E C0   LDX $c01e     
    $C091: EE 1E C0   INC $c01e     
    $C094: BC 00 CC   LDY $cc00,x   
    $C097: A2 07      LDX #$07      
    $C099: 20 AD C0   JSR $c0ad        ; → sub_C0AD
    $C09C: AE 25 C0   LDX $c025     
    $C09F: EE 25 C0   INC $c025     
    $C0A2: BC 00 CD   LDY $cd00,x   
    $C0A5: A2 0E      LDX #$0e      
    $C0A7: 20 AD C0   JSR $c0ad        ; → sub_C0AD
    $C0AA: 60         RTS           
; ----- data gap $C0AB-$C0AC (2 bytes) -----

sub_C0AD:
    $C0AD: 98         TYA           
    $C0AE: 29 80      AND #$80      
    $C0B0: D0 2A      BNE $c0dc        ; → L_C0DC
    $C0B2: B9 00 CA   LDA $ca00,y   
    $C0B5: 9D 01 D4   STA $d401,x    ;V1_FREQ_HI,X
    $C0B8: B9 80 CA   LDA $ca80,y   
    $C0BB: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $C0BE: EA         NOP           
    $C0BF: EA         NOP           
    $C0C0: 8A         TXA           
    $C0C1: A8         TAY           
    $C0C2: 69 04      ADC #$04      
    $C0C4: 8D 7F C0   STA $c07f     
L_C0C7:
    $C0C7: B9 19 C0   LDA $c019,y   
    $C0CA: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $C0CD: C8         INY           
    $C0CE: CC 7F C0   CPY $c07f     
    $C0D1: D0 F4      BNE $c0c7        ; → L_C0C7
    $C0D3: BC 1B C0   LDY $c01b,x   
    $C0D6: C8         INY           
    $C0D7: 98         TYA           
    $C0D8: 9D 04 D4   STA $d404,x    ;V1_CTRL,X
    $C0DB: 60         RTS           
L_C0DC:
    $C0DC: C0 80      CPY #$80      
    $C0DE: D0 07      BNE $c0e7        ; → L_C0E7
    $C0E0: BD 1B C0   LDA $c01b,x   
    $C0E3: 9D 04 D4   STA $d404,x    ;V1_CTRL,X
    $C0E6: 60         RTS           
L_C0E7:
    $C0E7: C0 FF      CPY #$ff      
    $C0E9: D0 1D      BNE $c108        ; → L_C108
    $C0EB: A9 01      LDA #$01      
    $C0ED: 9D 17 C0   STA $c017,x   
    $C0F0: E0 00      CPX #$00      
    $C0F2: D0 03      BNE $c0f7        ; → L_C0F7
    $C0F4: AC 00 CB   LDY $cb00     
L_C0F7:
    $C0F7: E0 07      CPX #$07      
    $C0F9: D0 03      BNE $c0fe        ; → L_C0FE
    $C0FB: AC 00 CC   LDY $cc00     
L_C0FE:
    $C0FE: E0 0E      CPX #$0e      
    $C100: D0 03      BNE $c105        ; → L_C105
    $C102: AC 00 CD   LDY $cd00     
L_C105:
    $C105: 4C AD C0   JMP $c0ad        ; → sub_C0AD
L_C108:
    $C108: FF         ???           
    $C10B: 00         BRK           
; ----- data gap $C10C-$CDFE (3315 bytes) -----

