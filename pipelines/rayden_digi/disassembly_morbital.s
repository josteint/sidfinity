; ============================================================================
; Rob Hubbard - Morbital (1999 Breeze/Cyberpunx)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc85/MUSICIANS/R/Rayden/Morbital.sid
; Load:   $0820   Init: $2800   Play: $0000
; PSID:   1 subtune(s), default subtune 1
; Binary: $0820-$7624 (28165 bytes)
;
; Auto-traced 363 reachable code bytes from init+play.
;
; ============================================================================

sub_0820:
    $0820: 4C 2B 08   JMP $082b        ; → L_082B
; ----- data gap $0823-$082A (8 bytes) -----

L_082B:
    $082B: A9 00      LDA #$00      
    $082D: 85 F2      STA $f2       
    $082F: 85 F3      STA $f3       
    $0831: AE 26 08   LDX $0826     
    $0834: AC 27 08   LDY $0827     
    $0837: 86 F0      STX $f0       
    $0839: 84 F1      STY $f1       
    $083B: A9 01      LDA #$01      
    $083D: 85 07      STA $07       
    $083F: 60         RTS           
; ----- data gap $0840-$0F3F (1792 bytes) -----

sub_0F40:
    $0F40: A0 00      LDY #$00      
    $0F42: AD 98 0F   LDA $0f98     
    $0F45: 0A         ASL a         
    $0F46: 0A         ASL a         
    $0F47: 0A         ASL a         
    $0F48: AA         TAX           
L_0F49:
    $0F49: BD A0 0F   LDA $0fa0,x   
    $0F4C: 99 20 BF   STA $bf20,y   
    $0F4F: E8         INX           
    $0F50: C8         INY           
    $0F51: C0 08      CPY #$08      
    $0F53: D0 F4      BNE $0f49        ; → L_0F49
    $0F55: A0 00      LDY #$00      
    $0F57: AD 99 0F   LDA $0f99     
    $0F5A: 0A         ASL a         
    $0F5B: 0A         ASL a         
    $0F5C: 0A         ASL a         
    $0F5D: AA         TAX           
L_0F5E:
    $0F5E: BD A0 0F   LDA $0fa0,x   
    $0F61: 99 30 BF   STA $bf30,y   
    $0F64: E8         INX           
    $0F65: C8         INY           
    $0F66: C0 08      CPY #$08      
    $0F68: D0 F4      BNE $0f5e        ; → L_0F5E
    $0F6A: A0 00      LDY #$00      
    $0F6C: AD 9A 0F   LDA $0f9a     
    $0F6F: 0A         ASL a         
    $0F70: 0A         ASL a         
    $0F71: 0A         ASL a         
    $0F72: AA         TAX           
L_0F73:
    $0F73: BD A0 0F   LDA $0fa0,x   
    $0F76: 99 38 BF   STA $bf38,y   
    $0F79: E8         INX           
    $0F7A: C8         INY           
    $0F7B: C0 08      CPY #$08      
    $0F7D: D0 F4      BNE $0f73        ; → L_0F73
    $0F7F: 60         RTS           
; ----- data gap $0F80-$0FFF (128 bytes) -----

sub_1000:
    $1000: 4C 1D 10   JMP $101d        ; → L_101D
; ----- data gap $1003-$101C (26 bytes) -----

L_101D:
    $101D: 4C 07 18   JMP $1807        ; → L_1807
; ----- data gap $1020-$104F (48 bytes) -----

L_1050:
    $1050: B9 E0 1B   LDA $1be0,y   
    $1053: 8D 16 17   STA $1716     
    $1056: B9 E1 1B   LDA $1be1,y   
    $1059: 8D 17 17   STA $1717     
    $105C: 8D 18 D4   STA $d418      ;VOL
    $105F: A2 00      LDX #$00      
    $1061: 8A         TXA           
L_1062:
    $1062: 9D 18 17   STA $1718,x   
    $1065: E8         INX           
    $1066: E0 86      CPX #$86      
    $1068: D0 F8      BNE $1062        ; → L_1062
    $106A: A2 00      LDX #$00      
    $106C: A9 01      LDA #$01      
L_106E:
    $106E: 9D 0C 10   STA $100c,x   
    $1071: 9D 3B 17   STA $173b,x   
    $1074: E8         INX           
    $1075: E0 03      CPX #$03      
    $1077: D0 F5      BNE $106e        ; → L_106E
    $1079: A2 00      LDX #$00      
    $107B: 8A         TXA           
L_107C:
    $107C: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $107F: E8         INX           
    $1080: E0 18      CPX #$18      
    $1082: D0 F8      BNE $107c        ; → L_107C
    $1084: 60         RTS           
; ----- data gap $1085-$1806 (1922 bytes) -----

L_1807:
    $1807: 0A         ASL a         
    $1808: 0A         ASL a         
    $1809: 0A         ASL a         
    $180A: A8         TAY           
    $180B: A2 00      LDX #$00      
L_180D:
    $180D: B9 E0 1B   LDA $1be0,y   
    $1810: 9D 07 17   STA $1707,x   
    $1813: B9 E1 1B   LDA $1be1,y   
    $1816: 9D 0A 17   STA $170a,x   
    $1819: C8         INY           
    $181A: C8         INY           
    $181B: E8         INX           
    $181C: E0 03      CPX #$03      
    $181E: D0 ED      BNE $180d        ; → L_180D
    $1820: 4C 70 18   JMP $1870        ; → L_1870
; ----- data gap $1823-$186F (77 bytes) -----

L_1870:
    $1870: A2 00      LDX #$00      
    $1872: 8A         TXA           
L_1873:
    $1873: 9D B0 17   STA $17b0,x   
    $1876: E8         INX           
    $1877: E0 08      CPX #$08      
    $1879: D0 F8      BNE $1873        ; → L_1873
    $187B: 4C 50 10   JMP $1050        ; → L_1050
; ----- data gap $187E-$25AA (3373 bytes) -----

sub_25AB:
    $25AB: A9 00      LDA #$00      
    $25AD: 8D 10 19   STA $1910     
    $25B0: 8D 1B 19   STA $191b     
    $25B3: 60         RTS           
; ----- data gap $25B4-$27FF (588 bytes) -----

; ======= init: =======
init:
    $2800: AD 01 DC   LDA $dc01     
    $2803: C9 DF      CMP #$df      
    $2805: D0 03      BNE $280a        ; → L_280A
    $2807: 20 AB 25   JSR $25ab        ; → sub_25AB
L_280A:
    $280A: 78         SEI           
    $280B: A9 15      LDA #$15      
    $280D: 85 01      STA $01       
    $280F: A9 01      LDA #$01      
    $2811: 8D 1A D0   STA $d01a     
    $2814: A9 81      LDA #$81      
    $2816: 8D 0D DD   STA $dd0d     
    $2819: A9 7F      LDA #$7f      
    $281B: 8D 0D DC   STA $dc0d     
    $281E: A9 00      LDA #$00      
    $2820: 8D 0E DD   STA $dd0e     
    $2823: A9 20      LDA #$20      
    $2825: A2 00      LDX #$00      
    $2827: A0 29      LDY #$29      
    $2829: 8D 12 D0   STA $d012     
    $282C: 8E FE FF   STX $fffe     
    $282F: 8C FF FF   STY $ffff     
    $2832: A9 3B      LDA #$3b      
    $2834: 8D 11 D0   STA $d011     
    $2837: A2 20      LDX #$20      
    $2839: A0 00      LDY #$00      
    $283B: 8E FA FF   STX $fffa     
    $283E: 8C FB FF   STY $fffb     
    $2841: 2C 0D DC   BIT $dc0d     
    $2844: 2C 0D DD   BIT $dd0d     
    $2847: AD 00 DD   LDA $dd00     
    $284A: 29 FC      AND #$fc      
    $284C: 09 01      ORA #$01      
    $284E: 8D 00 DD   STA $dd00     
    $2851: A9 08      LDA #$08      
    $2853: 8D 18 D0   STA $d018     
    $2856: A9 01      LDA #$01      
    $2858: 8D 20 D0   STA $d020     
    $285B: 8D 21 D0   STA $d021     
    $285E: A2 47      LDX #$47      
L_2860:
    $2860: BD B8 28   LDA $28b8,x   
    $2863: 95 20      STA $20,x     
    $2865: CA         DEX           
    $2866: 10 F8      BPL $2860        ; → L_2860
    $2868: A9 32      LDA #$32      
    $286A: 85 1F      STA $1f       
    $286C: A9 00      LDA #$00      
    $286E: 20 00 10   JSR $1000        ; → sub_1000
    $2871: 20 20 08   JSR $0820        ; → sub_0820
    $2874: 20 40 0F   JSR $0f40        ; → sub_0F40
    $2877: A9 42      LDA #$42      
L_2879:
    $2879: CD 12 D0   CMP $d012     
    $287C: D0 FB      BNE $2879        ; → L_2879
    $287E: E6 1E      INC $1e       
    $2880: A5 1E      LDA $1e       
    $2882: 29 07      AND #$07      
    $2884: AA         TAX           
    $2885: BD F0 0F   LDA $0ff0,x   
    $2888: A2 07      LDX #$07      
L_288A:
    $288A: 9D 00 80   STA $8000,x   
    $288D: CA         DEX           
    $288E: 10 FA      BPL $288a        ; → L_288A
    $2890: EA         NOP           
    $2891: EA         NOP           
    $2892: EA         NOP           
    $2893: EA         NOP           
    $2894: EA         NOP           
    $2895: EA         NOP           
    $2896: EA         NOP           
    $2897: A2 07      LDX #$07      
    $2899: A9 11      LDA #$11      
L_289B:
    $289B: 9D 00 80   STA $8000,x   
    $289E: CA         DEX           
    $289F: 10 FA      BPL $289b        ; → L_289B
    $28A1: 58         CLI           
L_28A2:
    $28A2: 4C A2 28   JMP $28a2        ; → L_28A2
; ----- data gap $28A5-$7624 (19840 bytes) -----

