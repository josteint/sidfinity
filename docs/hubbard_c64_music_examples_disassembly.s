; ============================================================================
; Rob Hubbard - Commodore 64 Music Examples (1985 Rob Hubbard)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid
; Load:   $086D   Init: $087C   Play: $086D
; PSID:   15 subtune(s), default subtune 1
; Binary: $086D-$422A (14782 bytes)
;
; Auto-traced 107 reachable code bytes from init+play.
;
; ============================================================================

; ======= play: =======
play:
    $086D: A2 00      LDX #$00      
    $086F: EE 6E 08   INC $086e     
sub_0872:
    $0872: A5 A2      LDA $a2       
    $0874: 48         PHA           
    $0875: 86 A2      STX $a2       
    $0877: 20 E2 FC   JSR $fce2     
    $087A: 68         PLA           
    $087B: 85 A2      STA $a2       
    $087D: 60         RTS           
    $087E: 8E 00 09   STX $0900     
    $0881: 8E 34 13   STX $1334     
    $0884: 8E 88 1D   STX $1d88     
    $0887: 8E 20 2A   STX $2a20     
    $088A: 8E D8 33   STX $33d8     
    $088D: 8E 2B 34   STX $342b     
    $0890: 8E B7 34   STX $34b7     
    $0893: 8E 0C 36   STX $360c     
    $0896: A2 EA      LDX #$ea      
    $0898: 8E FB 35   STX $35fb     
    $089B: 48         PHA           
    $089C: 20 CA 08   JSR $08ca        ; → sub_08CA
    $089F: 20 72 08   JSR $0872        ; → sub_0872
    $08A2: A9 0F      LDA #$0f      
    $08A4: A2 00      LDX #$00      
    $08A6: 8E 17 D4   STX $d417      ;RES_FILT
    $08A9: 8D 18 D4   STA $d418      ;VOL
    $08AC: 68         PLA           
    $08AD: F0 03      BEQ $08b2        ; → L_08B2
    $08AF: 8E 6E 08   STX $086e     
L_08B2:
    $08B2: C9 04      CMP #$04      
    $08B4: 90 12      BCC $08c8        ; → L_08C8
    $08B6: AD C5 35   LDA $35c5     
    $08B9: 8D 03 D4   STA $d403      ;V1_PW_HI
    $08BC: A9 26      LDA #$26      
    $08BE: A2 63      LDX #$63      
    $08C0: 8E 04 DC   STX $dc04     
    $08C3: 8D 05 DC   STA $dc05     
    $08C6: A9 03      LDA #$03      
L_08C8:
    $08C8: 69 0F      ADC #$0f      
sub_08CA:
    $08CA: AA         TAX           
    $08CB: BD EC 08   LDA $08ec,x   
    $08CE: 8D 78 08   STA $0878     
    $08D1: BD D8 08   LDA $08d8,x   
    $08D4: 8D 79 08   STA $0879     
    $08D7: 60         RTS           
; ----- data gap $08D8-$422A (14675 bytes) -----

