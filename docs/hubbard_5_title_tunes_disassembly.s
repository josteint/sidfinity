; ============================================================================
; Rob Hubbard - 5 Title Tunes (1985 Rob Hubbard)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: demo/hubbard/5_Title_Tunes_original.sid
; Load:   $0B10   Init: $0B10   Play: $0B40
; PSID:   5 subtune(s), default subtune 1
; Binary: $0B10-$38DA (11723 bytes)
;
; Auto-traced 4624 reachable code bytes from init+play.
;
; ============================================================================

; ======= init: =======
init:
    $0B10: 8D 6F 0B   STA $0b6f     
    $0B13: C9 00      CMP #$00      
    $0B15: D0 04      BNE $0b1b        ; → L_0B1B
L_0B17:
    $0B17: 20 50 18   JSR $1850        ; → sub_1850
    $0B1A: 60         RTS           
L_0B1B:
    $0B1B: C9 01      CMP #$01      
    $0B1D: D0 04      BNE $0b23        ; → L_0B23
    $0B1F: 20 A9 1F   JSR $1fa9        ; → sub_1FA9
    $0B22: 60         RTS           
L_0B23:
    $0B23: C9 02      CMP #$02      
    $0B25: D0 07      BNE $0b2e        ; → L_0B2E
    $0B27: EA         NOP           
    $0B28: EA         NOP           
    $0B29: EA         NOP           
    $0B2A: 20 0C 28   JSR $280c        ; → sub_280C
    $0B2D: 60         RTS           
L_0B2E:
    $0B2E: C9 03      CMP #$03      
    $0B30: D0 04      BNE $0b36        ; → L_0B36
    $0B32: 20 0C 31   JSR $310c        ; → sub_310C
    $0B35: 60         RTS           
L_0B36:
    $0B36: C9 04      CMP #$04      
    $0B38: D0 DD      BNE $0b17        ; → L_0B17
    $0B3A: 20 CF 38   JSR $38cf        ; → sub_38CF
    $0B3D: 60         RTS           
; ----- data gap $0B3E-$0B3F (2 bytes) -----

; ======= play: =======
play:
    $0B40: AD 6F 0B   LDA $0b6f     
    $0B43: C9 00      CMP #$00      
    $0B45: D0 04      BNE $0b4b        ; → L_0B4B
L_0B47:
    $0B47: 20 06 0C   JSR $0c06        ; → sub_0C06
    $0B4A: 60         RTS           
L_0B4B:
    $0B4B: C9 01      CMP #$01      
    $0B4D: D0 04      BNE $0b53        ; → L_0B53
    $0B4F: 20 A3 18   JSR $18a3        ; → sub_18A3
    $0B52: 60         RTS           
L_0B53:
    $0B53: C9 02      CMP #$02      
    $0B55: D0 04      BNE $0b5b        ; → L_0B5B
    $0B57: 20 FC 1F   JSR $1ffc        ; → sub_1FFC
    $0B5A: 60         RTS           
L_0B5B:
    $0B5B: C9 03      CMP #$03      
    $0B5D: D0 04      BNE $0b63        ; → L_0B63
    $0B5F: 20 3C 28   JSR $283c        ; → sub_283C
    $0B62: 60         RTS           
L_0B63:
    $0B63: C9 04      CMP #$04      
    $0B65: D0 E0      BNE $0b47        ; → L_0B47
    $0B67: 20 5F 31   JSR $315f        ; → sub_315F
    $0B6A: 60         RTS           
; ----- data gap $0B6B-$0BFF (149 bytes) -----

sub_0C00:
    $0C00: 4C 2C 18   JMP $182c        ; → L_182C
; ----- data gap $0C03-$0C05 (3 bytes) -----

sub_0C06:
    $0C06: EE 64 10   INC $1064     
    $0C09: 2C 58 10   BIT $1058     
    $0C0C: 30 1E      BMI $0c2c        ; → L_0C2C
    $0C0E: 50 36      BVC $0c46        ; → L_0C46
    $0C10: A9 00      LDA #$00      
    $0C12: 8D 64 10   STA $1064     
    $0C15: A2 02      LDX #$02      
L_0C17:
    $0C17: 9D 2E 10   STA $102e,x   
    $0C1A: 9D 31 10   STA $1031,x   
    $0C1D: 9D 34 10   STA $1034,x   
    $0C20: 9D 3D 10   STA $103d,x   
    $0C23: CA         DEX           
    $0C24: 10 F1      BPL $0c17        ; → L_0C17
    $0C26: 8D 58 10   STA $1058     
    $0C29: 4C 46 0C   JMP $0c46        ; → L_0C46
L_0C2C:
    $0C2C: 50 15      BVC $0c43        ; → L_0C43
    $0C2E: A9 00      LDA #$00      
    $0C30: 8D 04 D4   STA $d404      ;V1_CTRL
    $0C33: 8D 0B D4   STA $d40b      ;V2_CTRL
    $0C36: 8D 12 D4   STA $d412      ;V3_CTRL
    $0C39: A9 0F      LDA #$0f      
    $0C3B: 8D 18 D4   STA $d418      ;VOL
    $0C3E: A9 80      LDA #$80      
    $0C40: 8D 58 10   STA $1058     
L_0C43:
    $0C43: 4C 69 0F   JMP $0f69        ; → L_0F69
L_0C46:
    $0C46: A2 02      LDX #$02      
    $0C48: CE 55 10   DEC $1055     
    $0C4B: 10 06      BPL $0c53        ; → L_0C53
    $0C4D: AD 56 10   LDA $1056     
    $0C50: 8D 55 10   STA $1055     
L_0C53:
    $0C53: BD 2A 10   LDA $102a,x   
    $0C56: 8D 2D 10   STA $102d     
    $0C59: A8         TAY           
    $0C5A: AD 55 10   LDA $1055     
    $0C5D: CD 56 10   CMP $1056     
    $0C60: D0 15      BNE $0c77        ; → L_0C77
    $0C62: BD E5 10   LDA $10e5,x   
    $0C65: 85 FB      STA $fb       
    $0C67: BD E8 10   LDA $10e8,x   
    $0C6A: 85 FC      STA $fc       
    $0C6C: DE 34 10   DEC $1034,x   
    $0C6F: 30 09      BMI $0c7a        ; → L_0C7A
    $0C71: 4C 54 0D   JMP $0d54        ; → L_0D54
; ----- data gap $0C74-$0C76 (3 bytes) -----

L_0C77:
    $0C77: 4C 73 0D   JMP $0d73        ; → L_0D73
L_0C7A:
    $0C7A: BC 2E 10   LDY $102e,x   
    $0C7D: B1 FB      LDA ($fb),y   
    $0C7F: C9 FF      CMP #$ff      
    $0C81: D0 11      BNE $0c94        ; → L_0C94
    $0C83: A9 00      LDA #$00      
    $0C85: 9D 34 10   STA $1034,x   
    $0C88: 9D 2E 10   STA $102e,x   
    $0C8B: 9D 31 10   STA $1031,x   
    $0C8E: 4C 7A 0C   JMP $0c7a        ; → L_0C7A
; ----- data gap $0C91-$0C93 (3 bytes) -----

L_0C94:
    $0C94: A8         TAY           
    $0C95: B9 F1 10   LDA $10f1,y   
    $0C98: 85 FD      STA $fd       
    $0C9A: B9 11 11   LDA $1111,y   
    $0C9D: 85 FE      STA $fe       
    $0C9F: A9 00      LDA #$00      
    $0CA1: 9D 5F 10   STA $105f,x   
    $0CA4: BC 31 10   LDY $1031,x   
    $0CA7: A9 FF      LDA #$ff      
    $0CA9: 8D 43 10   STA $1043     
    $0CAC: B1 FD      LDA ($fd),y   
    $0CAE: 9D 37 10   STA $1037,x   
    $0CB1: 8D 44 10   STA $1044     
    $0CB4: 29 1F      AND #$1f      
    $0CB6: 9D 34 10   STA $1034,x   
    $0CB9: 2C 44 10   BIT $1044     
    $0CBC: 70 3F      BVS $0cfd        ; → L_0CFD
    $0CBE: FE 31 10   INC $1031,x   
    $0CC1: AD 44 10   LDA $1044     
    $0CC4: 10 11      BPL $0cd7        ; → L_0CD7
    $0CC6: C8         INY           
    $0CC7: B1 FD      LDA ($fd),y   
    $0CC9: 10 06      BPL $0cd1        ; → L_0CD1
    $0CCB: 9D 5F 10   STA $105f,x   
    $0CCE: 4C D4 0C   JMP $0cd4        ; → L_0CD4
L_0CD1:
    $0CD1: 9D 40 10   STA $1040,x   
L_0CD4:
    $0CD4: FE 31 10   INC $1031,x   
L_0CD7:
    $0CD7: C8         INY           
    $0CD8: B1 FD      LDA ($fd),y   
    $0CDA: 9D 3D 10   STA $103d,x   
    $0CDD: 0A         ASL a         
    $0CDE: A8         TAY           
    $0CDF: B9 6A 0F   LDA $0f6a,y   
    $0CE2: 8D 45 10   STA $1045     
    $0CE5: B9 6B 0F   LDA $0f6b,y   
    $0CE8: AC 2D 10   LDY $102d     
    $0CEB: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $0CEE: 9D 59 10   STA $1059,x   
    $0CF1: AD 45 10   LDA $1045     
    $0CF4: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $0CF7: 9D 5C 10   STA $105c,x   
    $0CFA: 4C 00 0D   JMP $0d00        ; → L_0D00
L_0CFD:
    $0CFD: CE 43 10   DEC $1043     
L_0D00:
    $0D00: AC 2D 10   LDY $102d     
    $0D03: BD 40 10   LDA $1040,x   
    $0D06: 8E 46 10   STX $1046     
    $0D09: 0A         ASL a         
    $0D0A: 0A         ASL a         
    $0D0B: 0A         ASL a         
    $0D0C: AA         TAX           
    $0D0D: BD 67 10   LDA $1067,x   
    $0D10: 8D 47 10   STA $1047     
    $0D13: BD 67 10   LDA $1067,x   
    $0D16: 2D 43 10   AND $1043     
    $0D19: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $0D1C: BD 65 10   LDA $1065,x   
    $0D1F: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $0D22: BD 66 10   LDA $1066,x   
    $0D25: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $0D28: BD 68 10   LDA $1068,x   
    $0D2B: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $0D2E: BD 69 10   LDA $1069,x   
    $0D31: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $0D34: AE 46 10   LDX $1046     
    $0D37: AD 47 10   LDA $1047     
    $0D3A: 9D 3A 10   STA $103a,x   
    $0D3D: FE 31 10   INC $1031,x   
    $0D40: BC 31 10   LDY $1031,x   
    $0D43: B1 FD      LDA ($fd),y   
    $0D45: C9 FF      CMP #$ff      
    $0D47: D0 08      BNE $0d51        ; → L_0D51
    $0D49: A9 00      LDA #$00      
    $0D4B: 9D 31 10   STA $1031,x   
    $0D4E: FE 2E 10   INC $102e,x   
L_0D51:
    $0D51: 4C 63 0F   JMP $0f63        ; → L_0F63
L_0D54:
    $0D54: AC 2D 10   LDY $102d     
    $0D57: BD 37 10   LDA $1037,x   
    $0D5A: 29 20      AND #$20      
    $0D5C: D0 15      BNE $0d73        ; → L_0D73
    $0D5E: BD 34 10   LDA $1034,x   
    $0D61: D0 10      BNE $0d73        ; → L_0D73
    $0D63: BD 3A 10   LDA $103a,x   
    $0D66: 29 FE      AND #$fe      
    $0D68: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $0D6B: A9 00      LDA #$00      
    $0D6D: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $0D70: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_0D73:
    $0D73: BD 40 10   LDA $1040,x   
    $0D76: 0A         ASL a         
    $0D77: 0A         ASL a         
    $0D78: 0A         ASL a         
    $0D79: A8         TAY           
    $0D7A: 8C 57 10   STY $1057     
    $0D7D: B9 6C 10   LDA $106c,y   
    $0D80: 8D 62 10   STA $1062     
    $0D83: B9 6B 10   LDA $106b,y   
    $0D86: 8D 49 10   STA $1049     
    $0D89: B9 6A 10   LDA $106a,y   
    $0D8C: 8D 48 10   STA $1048     
    $0D8F: F0 6F      BEQ $0e00        ; → L_0E00
    $0D91: AD 64 10   LDA $1064     
    $0D94: 29 07      AND #$07      
    $0D96: C9 04      CMP #$04      
    $0D98: 90 02      BCC $0d9c        ; → L_0D9C
    $0D9A: 49 07      EOR #$07      
L_0D9C:
    $0D9C: 8D 4E 10   STA $104e     
    $0D9F: BD 3D 10   LDA $103d,x   
    $0DA2: 0A         ASL a         
    $0DA3: A8         TAY           
    $0DA4: 38         SEC           
    $0DA5: B9 6C 0F   LDA $0f6c,y   
    $0DA8: F9 6A 0F   SBC $0f6a,y   
    $0DAB: 8D 4A 10   STA $104a     
    $0DAE: B9 6D 0F   LDA $0f6d,y   
    $0DB1: F9 6B 0F   SBC $0f6b,y   
L_0DB4:
    $0DB4: 4A         LSR a         
    $0DB5: 6E 4A 10   ROR $104a     
    $0DB8: CE 48 10   DEC $1048     
    $0DBB: 10 F7      BPL $0db4        ; → L_0DB4
    $0DBD: 8D 4B 10   STA $104b     
    $0DC0: B9 6A 0F   LDA $0f6a,y   
    $0DC3: 8D 4C 10   STA $104c     
    $0DC6: B9 6B 0F   LDA $0f6b,y   
    $0DC9: 8D 4D 10   STA $104d     
    $0DCC: BD 37 10   LDA $1037,x   
    $0DCF: 29 1F      AND #$1f      
    $0DD1: C9 08      CMP #$08      
    $0DD3: 90 1C      BCC $0df1        ; → L_0DF1
    $0DD5: AC 4E 10   LDY $104e     
L_0DD8:
    $0DD8: 88         DEY           
    $0DD9: 30 16      BMI $0df1        ; → L_0DF1
    $0DDB: 18         CLC           
    $0DDC: AD 4C 10   LDA $104c     
    $0DDF: 6D 4A 10   ADC $104a     
    $0DE2: 8D 4C 10   STA $104c     
    $0DE5: AD 4D 10   LDA $104d     
    $0DE8: 6D 4B 10   ADC $104b     
    $0DEB: 8D 4D 10   STA $104d     
    $0DEE: 4C D8 0D   JMP $0dd8        ; → L_0DD8
L_0DF1:
    $0DF1: AC 2D 10   LDY $102d     
    $0DF4: AD 4C 10   LDA $104c     
    $0DF7: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $0DFA: AD 4D 10   LDA $104d     
    $0DFD: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_0E00:
    $0E00: AD 62 10   LDA $1062     
    $0E03: 29 08      AND #$08      
    $0E05: F0 15      BEQ $0e1c        ; → L_0E1C
    $0E07: AC 57 10   LDY $1057     
    $0E0A: B9 65 10   LDA $1065,y   
    $0E0D: 6D 49 10   ADC $1049     
    $0E10: 99 65 10   STA $1065,y   
    $0E13: AC 2D 10   LDY $102d     
    $0E16: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $0E19: 4C 83 0E   JMP $0e83        ; → L_0E83
L_0E1C:
    $0E1C: AD 49 10   LDA $1049     
    $0E1F: F0 62      BEQ $0e83        ; → L_0E83
    $0E21: AC 57 10   LDY $1057     
    $0E24: 29 1F      AND #$1f      
    $0E26: DE 4F 10   DEC $104f,x   
    $0E29: 10 58      BPL $0e83        ; → L_0E83
    $0E2B: 9D 4F 10   STA $104f,x   
    $0E2E: AD 49 10   LDA $1049     
    $0E31: 29 E0      AND #$e0      
    $0E33: 8D 63 10   STA $1063     
    $0E36: BD 52 10   LDA $1052,x   
    $0E39: D0 1A      BNE $0e55        ; → L_0E55
    $0E3B: AD 63 10   LDA $1063     
    $0E3E: 18         CLC           
    $0E3F: 79 65 10   ADC $1065,y   
    $0E42: 48         PHA           
    $0E43: B9 66 10   LDA $1066,y   
    $0E46: 69 00      ADC #$00      
    $0E48: 29 0F      AND #$0f      
    $0E4A: 48         PHA           
    $0E4B: C9 0E      CMP #$0e      
    $0E4D: D0 1D      BNE $0e6c        ; → L_0E6C
    $0E4F: FE 52 10   INC $1052,x   
    $0E52: 4C 6C 0E   JMP $0e6c        ; → L_0E6C
L_0E55:
    $0E55: 38         SEC           
    $0E56: B9 65 10   LDA $1065,y   
    $0E59: ED 63 10   SBC $1063     
    $0E5C: 48         PHA           
    $0E5D: B9 66 10   LDA $1066,y   
    $0E60: E9 00      SBC #$00      
    $0E62: 29 0F      AND #$0f      
    $0E64: 48         PHA           
    $0E65: C9 08      CMP #$08      
    $0E67: D0 03      BNE $0e6c        ; → L_0E6C
    $0E69: DE 52 10   DEC $1052,x   
L_0E6C:
    $0E6C: 8E 46 10   STX $1046     
    $0E6F: AE 2D 10   LDX $102d     
    $0E72: 68         PLA           
    $0E73: 99 66 10   STA $1066,y   
    $0E76: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $0E79: 68         PLA           
    $0E7A: 99 65 10   STA $1065,y   
    $0E7D: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $0E80: AE 46 10   LDX $1046     
L_0E83:
    $0E83: AC 2D 10   LDY $102d     
    $0E86: BD 5F 10   LDA $105f,x   
    $0E89: F0 3F      BEQ $0eca        ; → L_0ECA
    $0E8B: 29 7E      AND #$7e      
    $0E8D: 8D 46 10   STA $1046     
    $0E90: BD 5F 10   LDA $105f,x   
    $0E93: 29 01      AND #$01      
    $0E95: F0 1B      BEQ $0eb2        ; → L_0EB2
    $0E97: 38         SEC           
    $0E98: BD 5C 10   LDA $105c,x   
    $0E9B: ED 46 10   SBC $1046     
    $0E9E: 9D 5C 10   STA $105c,x   
    $0EA1: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $0EA4: BD 59 10   LDA $1059,x   
    $0EA7: E9 00      SBC #$00      
    $0EA9: 9D 59 10   STA $1059,x   
    $0EAC: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $0EAF: 4C CA 0E   JMP $0eca        ; → L_0ECA
L_0EB2:
    $0EB2: 18         CLC           
    $0EB3: BD 5C 10   LDA $105c,x   
    $0EB6: 6D 46 10   ADC $1046     
    $0EB9: 9D 5C 10   STA $105c,x   
    $0EBC: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $0EBF: BD 59 10   LDA $1059,x   
    $0EC2: 69 00      ADC #$00      
    $0EC4: 9D 59 10   STA $1059,x   
    $0EC7: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_0ECA:
    $0ECA: AD 62 10   LDA $1062     
    $0ECD: 29 01      AND #$01      
    $0ECF: F0 35      BEQ $0f06        ; → L_0F06
    $0ED1: BD 59 10   LDA $1059,x   
    $0ED4: F0 30      BEQ $0f06        ; → L_0F06
    $0ED6: BD 34 10   LDA $1034,x   
    $0ED9: F0 2B      BEQ $0f06        ; → L_0F06
    $0EDB: BD 37 10   LDA $1037,x   
    $0EDE: 29 1F      AND #$1f      
    $0EE0: 38         SEC           
    $0EE1: E9 01      SBC #$01      
    $0EE3: DD 34 10   CMP $1034,x   
    $0EE6: AC 2D 10   LDY $102d     
    $0EE9: 90 10      BCC $0efb        ; → L_0EFB
    $0EEB: BD 59 10   LDA $1059,x   
    $0EEE: DE 59 10   DEC $1059,x   
    $0EF1: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $0EF4: BD 3A 10   LDA $103a,x   
    $0EF7: 29 FE      AND #$fe      
    $0EF9: D0 08      BNE $0f03        ; → L_0F03
L_0EFB:
    $0EFB: BD 59 10   LDA $1059,x   
    $0EFE: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $0F01: A9 80      LDA #$80      
L_0F03:
    $0F03: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_0F06:
    $0F06: AD 62 10   LDA $1062     
    $0F09: 29 02      AND #$02      
    $0F0B: F0 25      BEQ $0f32        ; → L_0F32
    $0F0D: BD 37 10   LDA $1037,x   
    $0F10: 29 1F      AND #$1f      
    $0F12: C9 0C      CMP #$0c      
    $0F14: 90 1C      BCC $0f32        ; → L_0F32
    $0F16: BD 34 10   LDA $1034,x   
    $0F19: C9 08      CMP #$08      
    $0F1B: B0 15      BCS $0f32        ; → L_0F32
    $0F1D: AD 64 10   LDA $1064     
    $0F20: 29 01      AND #$01      
    $0F22: F0 0E      BEQ $0f32        ; → L_0F32
    $0F24: BD 59 10   LDA $1059,x   
    $0F27: F0 09      BEQ $0f32        ; → L_0F32
    $0F29: DE 59 10   DEC $1059,x   
    $0F2C: AC 2D 10   LDY $102d     
    $0F2F: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_0F32:
    $0F32: AD 62 10   LDA $1062     
    $0F35: 29 04      AND #$04      
    $0F37: F0 2A      BEQ $0f63        ; → L_0F63
    $0F39: AD 64 10   LDA $1064     
    $0F3C: 29 01      AND #$01      
    $0F3E: F0 09      BEQ $0f49        ; → L_0F49
    $0F40: BD 3D 10   LDA $103d,x   
    $0F43: 18         CLC           
    $0F44: 69 0C      ADC #$0c      
    $0F46: 4C 4C 0F   JMP $0f4c        ; → L_0F4C
L_0F49:
    $0F49: BD 3D 10   LDA $103d,x   
L_0F4C:
    $0F4C: 0A         ASL a         
    $0F4D: A8         TAY           
    $0F4E: B9 6A 0F   LDA $0f6a,y   
    $0F51: 8D 45 10   STA $1045     
    $0F54: B9 6B 0F   LDA $0f6b,y   
    $0F57: AC 2D 10   LDY $102d     
    $0F5A: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $0F5D: AD 45 10   LDA $1045     
    $0F60: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_0F63:
    $0F63: CA         DEX           
    $0F64: 30 03      BMI $0f69        ; → L_0F69
    $0F66: 4C 53 0C   JMP $0c53        ; → L_0C53
L_0F69:
    $0F69: 60         RTS           
; ----- data gap $0F6A-$182B (2242 bytes) -----

L_182C:
    $182C: A0 00      LDY #$00      
    $182E: 0A         ASL a         
    $182F: 8D 46 10   STA $1046     
    $1832: 0A         ASL a         
    $1833: 18         CLC           
    $1834: 6D 46 10   ADC $1046     
    $1837: AA         TAX           
L_1838:
    $1838: BD EB 10   LDA $10eb,x   
    $183B: 99 E5 10   STA $10e5,y   
    $183E: E8         INX           
    $183F: C8         INY           
    $1840: C0 06      CPY #$06      
    $1842: D0 F4      BNE $1838        ; → L_1838
    $1844: A9 40      LDA #$40      
    $1846: 8D 58 10   STA $1058     
    $1849: 60         RTS           
; ----- data gap $184A-$184F (6 bytes) -----

sub_1850:
    $1850: EA         NOP           
    $1851: A9 00      LDA #$00      
    $1853: 20 00 0C   JSR $0c00        ; → sub_0C00
    $1856: A9 0F      LDA #$0f      
    $1858: 8D 18 D4   STA $d418      ;VOL
    $185B: 60         RTS           
; ----- data gap $185C-$189C (65 bytes) -----

sub_189D:
    $189D: 4C 85 1F   JMP $1f85        ; → L_1F85
; ----- data gap $18A0-$18A2 (3 bytes) -----

sub_18A3:
    $18A3: EE 01 1D   INC $1d01     
    $18A6: 2C F5 1C   BIT $1cf5     
    $18A9: 30 1E      BMI $18c9        ; → L_18C9
    $18AB: 50 36      BVC $18e3        ; → L_18E3
    $18AD: A9 00      LDA #$00      
    $18AF: 8D 01 1D   STA $1d01     
    $18B2: A2 02      LDX #$02      
L_18B4:
    $18B4: 9D CB 1C   STA $1ccb,x   
    $18B7: 9D CE 1C   STA $1cce,x   
    $18BA: 9D D1 1C   STA $1cd1,x   
    $18BD: 9D DA 1C   STA $1cda,x   
    $18C0: CA         DEX           
    $18C1: 10 F1      BPL $18b4        ; → L_18B4
    $18C3: 8D F5 1C   STA $1cf5     
    $18C6: 4C E3 18   JMP $18e3        ; → L_18E3
L_18C9:
    $18C9: 50 15      BVC $18e0        ; → L_18E0
    $18CB: A9 00      LDA #$00      
    $18CD: 8D 04 D4   STA $d404      ;V1_CTRL
    $18D0: 8D 0B D4   STA $d40b      ;V2_CTRL
    $18D3: 8D 12 D4   STA $d412      ;V3_CTRL
    $18D6: A9 0F      LDA #$0f      
    $18D8: 8D 18 D4   STA $d418      ;VOL
    $18DB: A9 80      LDA #$80      
    $18DD: 8D F5 1C   STA $1cf5     
L_18E0:
    $18E0: 4C 06 1C   JMP $1c06        ; → L_1C06
L_18E3:
    $18E3: A2 02      LDX #$02      
    $18E5: CE F2 1C   DEC $1cf2     
    $18E8: 10 06      BPL $18f0        ; → L_18F0
    $18EA: AD F3 1C   LDA $1cf3     
    $18ED: 8D F2 1C   STA $1cf2     
L_18F0:
    $18F0: BD C7 1C   LDA $1cc7,x   
    $18F3: 8D CA 1C   STA $1cca     
    $18F6: A8         TAY           
    $18F7: AD F2 1C   LDA $1cf2     
    $18FA: CD F3 1C   CMP $1cf3     
    $18FD: D0 15      BNE $1914        ; → L_1914
    $18FF: BD 82 1D   LDA $1d82,x   
    $1902: 85 FB      STA $fb       
    $1904: BD 85 1D   LDA $1d85,x   
    $1907: 85 FC      STA $fc       
    $1909: DE D1 1C   DEC $1cd1,x   
    $190C: 30 09      BMI $1917        ; → L_1917
    $190E: 4C F1 19   JMP $19f1        ; → L_19F1
; ----- data gap $1911-$1913 (3 bytes) -----

L_1914:
    $1914: 4C 10 1A   JMP $1a10        ; → L_1A10
L_1917:
    $1917: BC CB 1C   LDY $1ccb,x   
    $191A: B1 FB      LDA ($fb),y   
    $191C: C9 FF      CMP #$ff      
    $191E: D0 11      BNE $1931        ; → L_1931
    $1920: A9 00      LDA #$00      
    $1922: 9D D1 1C   STA $1cd1,x   
    $1925: 9D CB 1C   STA $1ccb,x   
    $1928: 9D CE 1C   STA $1cce,x   
    $192B: 4C 17 19   JMP $1917        ; → L_1917
; ----- data gap $192E-$1930 (3 bytes) -----

L_1931:
    $1931: A8         TAY           
    $1932: B9 8E 1D   LDA $1d8e,y   
    $1935: 85 FD      STA $fd       
    $1937: B9 9A 1D   LDA $1d9a,y   
    $193A: 85 FE      STA $fe       
    $193C: A9 00      LDA #$00      
    $193E: 9D FC 1C   STA $1cfc,x   
    $1941: BC CE 1C   LDY $1cce,x   
    $1944: A9 FF      LDA #$ff      
    $1946: 8D E0 1C   STA $1ce0     
    $1949: B1 FD      LDA ($fd),y   
    $194B: 9D D4 1C   STA $1cd4,x   
    $194E: 8D E1 1C   STA $1ce1     
    $1951: 29 1F      AND #$1f      
    $1953: 9D D1 1C   STA $1cd1,x   
    $1956: 2C E1 1C   BIT $1ce1     
    $1959: 70 3F      BVS $199a        ; → L_199A
    $195B: FE CE 1C   INC $1cce,x   
    $195E: AD E1 1C   LDA $1ce1     
    $1961: 10 11      BPL $1974        ; → L_1974
    $1963: C8         INY           
    $1964: B1 FD      LDA ($fd),y   
    $1966: 10 06      BPL $196e        ; → L_196E
    $1968: 9D FC 1C   STA $1cfc,x   
    $196B: 4C 71 19   JMP $1971        ; → L_1971
L_196E:
    $196E: 9D DD 1C   STA $1cdd,x   
L_1971:
    $1971: FE CE 1C   INC $1cce,x   
L_1974:
    $1974: C8         INY           
    $1975: B1 FD      LDA ($fd),y   
    $1977: 9D DA 1C   STA $1cda,x   
    $197A: 0A         ASL a         
    $197B: A8         TAY           
    $197C: B9 07 1C   LDA $1c07,y   
    $197F: 8D E2 1C   STA $1ce2     
    $1982: B9 08 1C   LDA $1c08,y   
    $1985: AC CA 1C   LDY $1cca     
    $1988: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $198B: 9D F6 1C   STA $1cf6,x   
    $198E: AD E2 1C   LDA $1ce2     
    $1991: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1994: 9D F9 1C   STA $1cf9,x   
    $1997: 4C 9D 19   JMP $199d        ; → L_199D
L_199A:
    $199A: CE E0 1C   DEC $1ce0     
L_199D:
    $199D: AC CA 1C   LDY $1cca     
    $19A0: BD DD 1C   LDA $1cdd,x   
    $19A3: 8E E3 1C   STX $1ce3     
    $19A6: 0A         ASL a         
    $19A7: 0A         ASL a         
    $19A8: 0A         ASL a         
    $19A9: AA         TAX           
    $19AA: BD 04 1D   LDA $1d04,x   
    $19AD: 8D E4 1C   STA $1ce4     
    $19B0: BD 04 1D   LDA $1d04,x   
    $19B3: 2D E0 1C   AND $1ce0     
    $19B6: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $19B9: BD 02 1D   LDA $1d02,x   
    $19BC: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $19BF: BD 03 1D   LDA $1d03,x   
    $19C2: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $19C5: BD 05 1D   LDA $1d05,x   
    $19C8: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $19CB: BD 06 1D   LDA $1d06,x   
    $19CE: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $19D1: AE E3 1C   LDX $1ce3     
    $19D4: AD E4 1C   LDA $1ce4     
    $19D7: 9D D7 1C   STA $1cd7,x   
    $19DA: FE CE 1C   INC $1cce,x   
    $19DD: BC CE 1C   LDY $1cce,x   
    $19E0: B1 FD      LDA ($fd),y   
    $19E2: C9 FF      CMP #$ff      
    $19E4: D0 08      BNE $19ee        ; → L_19EE
    $19E6: A9 00      LDA #$00      
    $19E8: 9D CE 1C   STA $1cce,x   
    $19EB: FE CB 1C   INC $1ccb,x   
L_19EE:
    $19EE: 4C 00 1C   JMP $1c00        ; → L_1C00
L_19F1:
    $19F1: AC CA 1C   LDY $1cca     
    $19F4: BD D4 1C   LDA $1cd4,x   
    $19F7: 29 20      AND #$20      
    $19F9: D0 15      BNE $1a10        ; → L_1A10
    $19FB: BD D1 1C   LDA $1cd1,x   
    $19FE: D0 10      BNE $1a10        ; → L_1A10
    $1A00: BD D7 1C   LDA $1cd7,x   
    $1A03: 29 FE      AND #$fe      
    $1A05: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $1A08: A9 00      LDA #$00      
    $1A0A: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $1A0D: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_1A10:
    $1A10: BD DD 1C   LDA $1cdd,x   
    $1A13: 0A         ASL a         
    $1A14: 0A         ASL a         
    $1A15: 0A         ASL a         
    $1A16: A8         TAY           
    $1A17: 8C F4 1C   STY $1cf4     
    $1A1A: B9 09 1D   LDA $1d09,y   
    $1A1D: 8D FF 1C   STA $1cff     
    $1A20: B9 08 1D   LDA $1d08,y   
    $1A23: 8D E6 1C   STA $1ce6     
    $1A26: B9 07 1D   LDA $1d07,y   
    $1A29: 8D E5 1C   STA $1ce5     
    $1A2C: F0 6F      BEQ $1a9d        ; → L_1A9D
    $1A2E: AD 01 1D   LDA $1d01     
    $1A31: 29 07      AND #$07      
    $1A33: C9 04      CMP #$04      
    $1A35: 90 02      BCC $1a39        ; → L_1A39
    $1A37: 49 07      EOR #$07      
L_1A39:
    $1A39: 8D EB 1C   STA $1ceb     
    $1A3C: BD DA 1C   LDA $1cda,x   
    $1A3F: 0A         ASL a         
    $1A40: A8         TAY           
    $1A41: 38         SEC           
    $1A42: B9 09 1C   LDA $1c09,y   
    $1A45: F9 07 1C   SBC $1c07,y   
    $1A48: 8D E7 1C   STA $1ce7     
    $1A4B: B9 0A 1C   LDA $1c0a,y   
    $1A4E: F9 08 1C   SBC $1c08,y   
L_1A51:
    $1A51: 4A         LSR a         
    $1A52: 6E E7 1C   ROR $1ce7     
    $1A55: CE E5 1C   DEC $1ce5     
    $1A58: 10 F7      BPL $1a51        ; → L_1A51
    $1A5A: 8D E8 1C   STA $1ce8     
    $1A5D: B9 07 1C   LDA $1c07,y   
    $1A60: 8D E9 1C   STA $1ce9     
    $1A63: B9 08 1C   LDA $1c08,y   
    $1A66: 8D EA 1C   STA $1cea     
    $1A69: BD D4 1C   LDA $1cd4,x   
    $1A6C: 29 1F      AND #$1f      
    $1A6E: C9 08      CMP #$08      
    $1A70: 90 1C      BCC $1a8e        ; → L_1A8E
    $1A72: AC EB 1C   LDY $1ceb     
L_1A75:
    $1A75: 88         DEY           
    $1A76: 30 16      BMI $1a8e        ; → L_1A8E
    $1A78: 18         CLC           
    $1A79: AD E9 1C   LDA $1ce9     
    $1A7C: 6D E7 1C   ADC $1ce7     
    $1A7F: 8D E9 1C   STA $1ce9     
    $1A82: AD EA 1C   LDA $1cea     
    $1A85: 6D E8 1C   ADC $1ce8     
    $1A88: 8D EA 1C   STA $1cea     
    $1A8B: 4C 75 1A   JMP $1a75        ; → L_1A75
L_1A8E:
    $1A8E: AC CA 1C   LDY $1cca     
    $1A91: AD E9 1C   LDA $1ce9     
    $1A94: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1A97: AD EA 1C   LDA $1cea     
    $1A9A: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_1A9D:
    $1A9D: AD FF 1C   LDA $1cff     
    $1AA0: 29 08      AND #$08      
    $1AA2: F0 15      BEQ $1ab9        ; → L_1AB9
    $1AA4: AC F4 1C   LDY $1cf4     
    $1AA7: B9 02 1D   LDA $1d02,y   
    $1AAA: 6D E6 1C   ADC $1ce6     
    $1AAD: 99 02 1D   STA $1d02,y   
    $1AB0: AC CA 1C   LDY $1cca     
    $1AB3: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $1AB6: 4C 20 1B   JMP $1b20        ; → L_1B20
L_1AB9:
    $1AB9: AD E6 1C   LDA $1ce6     
    $1ABC: F0 62      BEQ $1b20        ; → L_1B20
    $1ABE: AC F4 1C   LDY $1cf4     
    $1AC1: 29 1F      AND #$1f      
    $1AC3: DE EC 1C   DEC $1cec,x   
    $1AC6: 10 58      BPL $1b20        ; → L_1B20
    $1AC8: 9D EC 1C   STA $1cec,x   
    $1ACB: AD E6 1C   LDA $1ce6     
    $1ACE: 29 E0      AND #$e0      
    $1AD0: 8D 00 1D   STA $1d00     
    $1AD3: BD EF 1C   LDA $1cef,x   
    $1AD6: D0 1A      BNE $1af2        ; → L_1AF2
    $1AD8: AD 00 1D   LDA $1d00     
    $1ADB: 18         CLC           
    $1ADC: 79 02 1D   ADC $1d02,y   
    $1ADF: 48         PHA           
    $1AE0: B9 03 1D   LDA $1d03,y   
    $1AE3: 69 00      ADC #$00      
    $1AE5: 29 0F      AND #$0f      
    $1AE7: 48         PHA           
    $1AE8: C9 0E      CMP #$0e      
    $1AEA: D0 1D      BNE $1b09        ; → L_1B09
    $1AEC: FE EF 1C   INC $1cef,x   
    $1AEF: 4C 09 1B   JMP $1b09        ; → L_1B09
L_1AF2:
    $1AF2: 38         SEC           
    $1AF3: B9 02 1D   LDA $1d02,y   
    $1AF6: ED 00 1D   SBC $1d00     
    $1AF9: 48         PHA           
    $1AFA: B9 03 1D   LDA $1d03,y   
    $1AFD: E9 00      SBC #$00      
    $1AFF: 29 0F      AND #$0f      
    $1B01: 48         PHA           
    $1B02: C9 08      CMP #$08      
    $1B04: D0 03      BNE $1b09        ; → L_1B09
    $1B06: DE EF 1C   DEC $1cef,x   
L_1B09:
    $1B09: 8E E3 1C   STX $1ce3     
    $1B0C: AE CA 1C   LDX $1cca     
    $1B0F: 68         PLA           
    $1B10: 99 03 1D   STA $1d03,y   
    $1B13: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $1B16: 68         PLA           
    $1B17: 99 02 1D   STA $1d02,y   
    $1B1A: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $1B1D: AE E3 1C   LDX $1ce3     
L_1B20:
    $1B20: AC CA 1C   LDY $1cca     
    $1B23: BD FC 1C   LDA $1cfc,x   
    $1B26: F0 3F      BEQ $1b67        ; → L_1B67
    $1B28: 29 7E      AND #$7e      
    $1B2A: 8D E3 1C   STA $1ce3     
    $1B2D: BD FC 1C   LDA $1cfc,x   
    $1B30: 29 01      AND #$01      
    $1B32: F0 1B      BEQ $1b4f        ; → L_1B4F
    $1B34: 38         SEC           
    $1B35: BD F9 1C   LDA $1cf9,x   
    $1B38: ED E3 1C   SBC $1ce3     
    $1B3B: 9D F9 1C   STA $1cf9,x   
    $1B3E: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1B41: BD F6 1C   LDA $1cf6,x   
    $1B44: E9 00      SBC #$00      
    $1B46: 9D F6 1C   STA $1cf6,x   
    $1B49: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1B4C: 4C 67 1B   JMP $1b67        ; → L_1B67
L_1B4F:
    $1B4F: 18         CLC           
    $1B50: BD F9 1C   LDA $1cf9,x   
    $1B53: 6D E3 1C   ADC $1ce3     
    $1B56: 9D F9 1C   STA $1cf9,x   
    $1B59: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1B5C: BD F6 1C   LDA $1cf6,x   
    $1B5F: 69 00      ADC #$00      
    $1B61: 9D F6 1C   STA $1cf6,x   
    $1B64: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_1B67:
    $1B67: AD FF 1C   LDA $1cff     
    $1B6A: 29 01      AND #$01      
    $1B6C: F0 35      BEQ $1ba3        ; → L_1BA3
    $1B6E: BD F6 1C   LDA $1cf6,x   
    $1B71: F0 30      BEQ $1ba3        ; → L_1BA3
    $1B73: BD D1 1C   LDA $1cd1,x   
    $1B76: F0 2B      BEQ $1ba3        ; → L_1BA3
    $1B78: BD D4 1C   LDA $1cd4,x   
    $1B7B: 29 1F      AND #$1f      
    $1B7D: 38         SEC           
    $1B7E: E9 01      SBC #$01      
    $1B80: DD D1 1C   CMP $1cd1,x   
    $1B83: AC CA 1C   LDY $1cca     
    $1B86: 90 10      BCC $1b98        ; → L_1B98
    $1B88: BD F6 1C   LDA $1cf6,x   
    $1B8B: DE F6 1C   DEC $1cf6,x   
    $1B8E: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1B91: BD D7 1C   LDA $1cd7,x   
    $1B94: 29 FE      AND #$fe      
    $1B96: D0 08      BNE $1ba0        ; → L_1BA0
L_1B98:
    $1B98: BD F6 1C   LDA $1cf6,x   
    $1B9B: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1B9E: A9 80      LDA #$80      
L_1BA0:
    $1BA0: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_1BA3:
    $1BA3: AD FF 1C   LDA $1cff     
    $1BA6: 29 02      AND #$02      
    $1BA8: F0 25      BEQ $1bcf        ; → L_1BCF
    $1BAA: BD D4 1C   LDA $1cd4,x   
    $1BAD: 29 1F      AND #$1f      
    $1BAF: C9 10      CMP #$10      
    $1BB1: 90 1C      BCC $1bcf        ; → L_1BCF
    $1BB3: BD D1 1C   LDA $1cd1,x   
    $1BB6: C9 18      CMP #$18      
    $1BB8: B0 15      BCS $1bcf        ; → L_1BCF
    $1BBA: AD 01 1D   LDA $1d01     
    $1BBD: 29 01      AND #$01      
    $1BBF: F0 0E      BEQ $1bcf        ; → L_1BCF
    $1BC1: BD F6 1C   LDA $1cf6,x   
    $1BC4: F0 09      BEQ $1bcf        ; → L_1BCF
    $1BC6: DE F6 1C   DEC $1cf6,x   
    $1BC9: AC CA 1C   LDY $1cca     
    $1BCC: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_1BCF:
    $1BCF: AD FF 1C   LDA $1cff     
    $1BD2: 29 04      AND #$04      
    $1BD4: F0 2A      BEQ $1c00        ; → L_1C00
    $1BD6: AD 01 1D   LDA $1d01     
    $1BD9: 29 01      AND #$01      
    $1BDB: F0 09      BEQ $1be6        ; → L_1BE6
    $1BDD: BD DA 1C   LDA $1cda,x   
    $1BE0: 18         CLC           
    $1BE1: 69 0C      ADC #$0c      
    $1BE3: 4C E9 1B   JMP $1be9        ; → L_1BE9
L_1BE6:
    $1BE6: BD DA 1C   LDA $1cda,x   
L_1BE9:
    $1BE9: 0A         ASL a         
    $1BEA: A8         TAY           
    $1BEB: B9 07 1C   LDA $1c07,y   
    $1BEE: 8D E2 1C   STA $1ce2     
    $1BF1: B9 08 1C   LDA $1c08,y   
    $1BF4: AC CA 1C   LDY $1cca     
    $1BF7: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1BFA: AD E2 1C   LDA $1ce2     
    $1BFD: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_1C00:
    $1C00: CA         DEX           
    $1C01: 30 03      BMI $1c06        ; → L_1C06
    $1C03: 4C F0 18   JMP $18f0        ; → L_18F0
L_1C06:
    $1C06: 60         RTS           
; ----- data gap $1C07-$1F84 (894 bytes) -----

L_1F85:
    $1F85: A0 00      LDY #$00      
    $1F87: 0A         ASL a         
    $1F88: 8D E3 1C   STA $1ce3     
    $1F8B: 0A         ASL a         
    $1F8C: 18         CLC           
    $1F8D: 6D E3 1C   ADC $1ce3     
    $1F90: AA         TAX           
L_1F91:
    $1F91: BD 88 1D   LDA $1d88,x   
    $1F94: 99 82 1D   STA $1d82,y   
    $1F97: E8         INX           
    $1F98: C8         INY           
    $1F99: C0 06      CPY #$06      
    $1F9B: D0 F4      BNE $1f91        ; → L_1F91
    $1F9D: A9 40      LDA #$40      
    $1F9F: 8D F5 1C   STA $1cf5     
    $1FA2: 60         RTS           
; ----- data gap $1FA3-$1FA8 (6 bytes) -----

sub_1FA9:
    $1FA9: EA         NOP           
    $1FAA: A9 00      LDA #$00      
    $1FAC: 20 9D 18   JSR $189d        ; → sub_189D
    $1FAF: A9 0F      LDA #$0f      
    $1FB1: 8D 18 D4   STA $d418      ;VOL
    $1FB4: 60         RTS           
; ----- data gap $1FB5-$1FF5 (65 bytes) -----

sub_1FF6:
    $1FF6: 4C E8 27   JMP $27e8        ; → L_27E8
; ----- data gap $1FF9-$1FFB (3 bytes) -----

sub_1FFC:
    $1FFC: EE 5A 24   INC $245a     
    $1FFF: 2C 4E 24   BIT $244e     
    $2002: 30 1E      BMI $2022        ; → L_2022
    $2004: 50 36      BVC $203c        ; → L_203C
    $2006: A9 00      LDA #$00      
    $2008: 8D 5A 24   STA $245a     
    $200B: A2 02      LDX #$02      
L_200D:
    $200D: 9D 24 24   STA $2424,x   
    $2010: 9D 27 24   STA $2427,x   
    $2013: 9D 2A 24   STA $242a,x   
    $2016: 9D 33 24   STA $2433,x   
    $2019: CA         DEX           
    $201A: 10 F1      BPL $200d        ; → L_200D
    $201C: 8D 4E 24   STA $244e     
    $201F: 4C 3C 20   JMP $203c        ; → L_203C
L_2022:
    $2022: 50 15      BVC $2039        ; → L_2039
    $2024: A9 00      LDA #$00      
    $2026: 8D 04 D4   STA $d404      ;V1_CTRL
    $2029: 8D 0B D4   STA $d40b      ;V2_CTRL
    $202C: 8D 12 D4   STA $d412      ;V3_CTRL
    $202F: A9 0F      LDA #$0f      
    $2031: 8D 18 D4   STA $d418      ;VOL
    $2034: A9 80      LDA #$80      
    $2036: 8D 4E 24   STA $244e     
L_2039:
    $2039: 4C 5F 23   JMP $235f        ; → L_235F
L_203C:
    $203C: A2 02      LDX #$02      
    $203E: CE 4B 24   DEC $244b     
    $2041: 10 06      BPL $2049        ; → L_2049
    $2043: AD 4C 24   LDA $244c     
    $2046: 8D 4B 24   STA $244b     
L_2049:
    $2049: BD 20 24   LDA $2420,x   
    $204C: 8D 23 24   STA $2423     
    $204F: A8         TAY           
    $2050: AD 4B 24   LDA $244b     
    $2053: CD 4C 24   CMP $244c     
    $2056: D0 15      BNE $206d        ; → L_206D
    $2058: BD DB 24   LDA $24db,x   
    $205B: 85 FB      STA $fb       
    $205D: BD DE 24   LDA $24de,x   
    $2060: 85 FC      STA $fc       
    $2062: DE 2A 24   DEC $242a,x   
    $2065: 30 09      BMI $2070        ; → L_2070
    $2067: 4C 4A 21   JMP $214a        ; → L_214A
; ----- data gap $206A-$206C (3 bytes) -----

L_206D:
    $206D: 4C 69 21   JMP $2169        ; → L_2169
L_2070:
    $2070: BC 24 24   LDY $2424,x   
    $2073: B1 FB      LDA ($fb),y   
    $2075: C9 FF      CMP #$ff      
    $2077: D0 11      BNE $208a        ; → L_208A
    $2079: A9 00      LDA #$00      
    $207B: 9D 2A 24   STA $242a,x   
    $207E: 9D 24 24   STA $2424,x   
    $2081: 9D 27 24   STA $2427,x   
    $2084: 4C 70 20   JMP $2070        ; → L_2070
; ----- data gap $2087-$2089 (3 bytes) -----

L_208A:
    $208A: A8         TAY           
    $208B: B9 E7 24   LDA $24e7,y   
    $208E: 85 FD      STA $fd       
    $2090: B9 F7 24   LDA $24f7,y   
    $2093: 85 FE      STA $fe       
    $2095: A9 00      LDA #$00      
    $2097: 9D 55 24   STA $2455,x   
    $209A: BC 27 24   LDY $2427,x   
    $209D: A9 FF      LDA #$ff      
    $209F: 8D 39 24   STA $2439     
    $20A2: B1 FD      LDA ($fd),y   
    $20A4: 9D 2D 24   STA $242d,x   
    $20A7: 8D 3A 24   STA $243a     
    $20AA: 29 1F      AND #$1f      
    $20AC: 9D 2A 24   STA $242a,x   
    $20AF: 2C 3A 24   BIT $243a     
    $20B2: 70 3F      BVS $20f3        ; → L_20F3
    $20B4: FE 27 24   INC $2427,x   
    $20B7: AD 3A 24   LDA $243a     
    $20BA: 10 11      BPL $20cd        ; → L_20CD
    $20BC: C8         INY           
    $20BD: B1 FD      LDA ($fd),y   
    $20BF: 10 06      BPL $20c7        ; → L_20C7
    $20C1: 9D 55 24   STA $2455,x   
    $20C4: 4C CA 20   JMP $20ca        ; → L_20CA
L_20C7:
    $20C7: 9D 36 24   STA $2436,x   
L_20CA:
    $20CA: FE 27 24   INC $2427,x   
L_20CD:
    $20CD: C8         INY           
    $20CE: B1 FD      LDA ($fd),y   
    $20D0: 9D 33 24   STA $2433,x   
    $20D3: 0A         ASL a         
    $20D4: A8         TAY           
    $20D5: B9 60 23   LDA $2360,y   
    $20D8: 8D 3B 24   STA $243b     
    $20DB: B9 61 23   LDA $2361,y   
    $20DE: AC 23 24   LDY $2423     
    $20E1: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $20E4: 9D 4F 24   STA $244f,x   
    $20E7: AD 3B 24   LDA $243b     
    $20EA: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $20ED: 9D 52 24   STA $2452,x   
    $20F0: 4C F6 20   JMP $20f6        ; → L_20F6
L_20F3:
    $20F3: CE 39 24   DEC $2439     
L_20F6:
    $20F6: AC 23 24   LDY $2423     
    $20F9: BD 36 24   LDA $2436,x   
    $20FC: 8E 3C 24   STX $243c     
    $20FF: 0A         ASL a         
    $2100: 0A         ASL a         
    $2101: 0A         ASL a         
    $2102: AA         TAX           
    $2103: BD 5D 24   LDA $245d,x   
    $2106: 8D 3D 24   STA $243d     
    $2109: BD 5D 24   LDA $245d,x   
    $210C: 2D 39 24   AND $2439     
    $210F: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $2112: BD 5B 24   LDA $245b,x   
    $2115: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $2118: BD 5C 24   LDA $245c,x   
    $211B: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $211E: BD 5E 24   LDA $245e,x   
    $2121: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $2124: BD 5F 24   LDA $245f,x   
    $2127: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $212A: AE 3C 24   LDX $243c     
    $212D: AD 3D 24   LDA $243d     
    $2130: 9D 30 24   STA $2430,x   
    $2133: FE 27 24   INC $2427,x   
    $2136: BC 27 24   LDY $2427,x   
    $2139: B1 FD      LDA ($fd),y   
    $213B: C9 FF      CMP #$ff      
    $213D: D0 08      BNE $2147        ; → L_2147
    $213F: A9 00      LDA #$00      
    $2141: 9D 27 24   STA $2427,x   
    $2144: FE 24 24   INC $2424,x   
L_2147:
    $2147: 4C 59 23   JMP $2359        ; → L_2359
L_214A:
    $214A: AC 23 24   LDY $2423     
    $214D: BD 2D 24   LDA $242d,x   
    $2150: 29 20      AND #$20      
    $2152: D0 15      BNE $2169        ; → L_2169
    $2154: BD 2A 24   LDA $242a,x   
    $2157: D0 10      BNE $2169        ; → L_2169
    $2159: BD 30 24   LDA $2430,x   
    $215C: 29 FE      AND #$fe      
    $215E: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $2161: A9 00      LDA #$00      
    $2163: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $2166: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_2169:
    $2169: BD 36 24   LDA $2436,x   
    $216C: 0A         ASL a         
    $216D: 0A         ASL a         
    $216E: 0A         ASL a         
    $216F: A8         TAY           
    $2170: 8C 4D 24   STY $244d     
    $2173: B9 62 24   LDA $2462,y   
    $2176: 8D 58 24   STA $2458     
    $2179: B9 61 24   LDA $2461,y   
    $217C: 8D 3F 24   STA $243f     
    $217F: B9 60 24   LDA $2460,y   
    $2182: 8D 3E 24   STA $243e     
    $2185: F0 6F      BEQ $21f6        ; → L_21F6
    $2187: AD 5A 24   LDA $245a     
    $218A: 29 07      AND #$07      
    $218C: C9 04      CMP #$04      
    $218E: 90 02      BCC $2192        ; → L_2192
    $2190: 49 07      EOR #$07      
L_2192:
    $2192: 8D 44 24   STA $2444     
    $2195: BD 33 24   LDA $2433,x   
    $2198: 0A         ASL a         
    $2199: A8         TAY           
    $219A: 38         SEC           
    $219B: B9 62 23   LDA $2362,y   
    $219E: F9 60 23   SBC $2360,y   
    $21A1: 8D 40 24   STA $2440     
    $21A4: B9 63 23   LDA $2363,y   
    $21A7: F9 61 23   SBC $2361,y   
L_21AA:
    $21AA: 4A         LSR a         
    $21AB: 6E 40 24   ROR $2440     
    $21AE: CE 3E 24   DEC $243e     
    $21B1: 10 F7      BPL $21aa        ; → L_21AA
    $21B3: 8D 41 24   STA $2441     
    $21B6: B9 60 23   LDA $2360,y   
    $21B9: 8D 42 24   STA $2442     
    $21BC: B9 61 23   LDA $2361,y   
    $21BF: 8D 43 24   STA $2443     
    $21C2: BD 2D 24   LDA $242d,x   
    $21C5: 29 1F      AND #$1f      
    $21C7: C9 08      CMP #$08      
    $21C9: 90 1C      BCC $21e7        ; → L_21E7
    $21CB: AC 44 24   LDY $2444     
L_21CE:
    $21CE: 88         DEY           
    $21CF: 30 16      BMI $21e7        ; → L_21E7
    $21D1: 18         CLC           
    $21D2: AD 42 24   LDA $2442     
    $21D5: 6D 40 24   ADC $2440     
    $21D8: 8D 42 24   STA $2442     
    $21DB: AD 43 24   LDA $2443     
    $21DE: 6D 41 24   ADC $2441     
    $21E1: 8D 43 24   STA $2443     
    $21E4: 4C CE 21   JMP $21ce        ; → L_21CE
L_21E7:
    $21E7: AC 23 24   LDY $2423     
    $21EA: AD 42 24   LDA $2442     
    $21ED: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $21F0: AD 43 24   LDA $2443     
    $21F3: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_21F6:
    $21F6: AD 58 24   LDA $2458     
    $21F9: 29 08      AND #$08      
    $21FB: F0 15      BEQ $2212        ; → L_2212
    $21FD: AC 4D 24   LDY $244d     
    $2200: B9 5B 24   LDA $245b,y   
    $2203: 6D 3F 24   ADC $243f     
    $2206: 99 5B 24   STA $245b,y   
    $2209: AC 23 24   LDY $2423     
    $220C: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $220F: 4C 79 22   JMP $2279        ; → L_2279
L_2212:
    $2212: AD 3F 24   LDA $243f     
    $2215: F0 62      BEQ $2279        ; → L_2279
    $2217: AC 4D 24   LDY $244d     
    $221A: 29 1F      AND #$1f      
    $221C: DE 45 24   DEC $2445,x   
    $221F: 10 58      BPL $2279        ; → L_2279
    $2221: 9D 45 24   STA $2445,x   
    $2224: AD 3F 24   LDA $243f     
    $2227: 29 E0      AND #$e0      
    $2229: 8D 59 24   STA $2459     
    $222C: BD 48 24   LDA $2448,x   
    $222F: D0 1A      BNE $224b        ; → L_224B
    $2231: AD 59 24   LDA $2459     
    $2234: 18         CLC           
    $2235: 79 5B 24   ADC $245b,y   
    $2238: 48         PHA           
    $2239: B9 5C 24   LDA $245c,y   
    $223C: 69 00      ADC #$00      
    $223E: 29 0F      AND #$0f      
    $2240: 48         PHA           
    $2241: C9 0E      CMP #$0e      
    $2243: D0 1D      BNE $2262        ; → L_2262
    $2245: FE 48 24   INC $2448,x   
    $2248: 4C 62 22   JMP $2262        ; → L_2262
L_224B:
    $224B: 38         SEC           
    $224C: B9 5B 24   LDA $245b,y   
    $224F: ED 59 24   SBC $2459     
    $2252: 48         PHA           
    $2253: B9 5C 24   LDA $245c,y   
    $2256: E9 00      SBC #$00      
    $2258: 29 0F      AND #$0f      
    $225A: 48         PHA           
    $225B: C9 08      CMP #$08      
    $225D: D0 03      BNE $2262        ; → L_2262
    $225F: DE 48 24   DEC $2448,x   
L_2262:
    $2262: 8E 3C 24   STX $243c     
    $2265: AE 23 24   LDX $2423     
    $2268: 68         PLA           
    $2269: 99 5C 24   STA $245c,y   
    $226C: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $226F: 68         PLA           
    $2270: 99 5B 24   STA $245b,y   
    $2273: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $2276: AE 3C 24   LDX $243c     
L_2279:
    $2279: AC 23 24   LDY $2423     
    $227C: BD 55 24   LDA $2455,x   
    $227F: F0 3F      BEQ $22c0        ; → L_22C0
    $2281: 29 7E      AND #$7e      
    $2283: 8D 3C 24   STA $243c     
    $2286: BD 55 24   LDA $2455,x   
    $2289: 29 01      AND #$01      
    $228B: F0 1B      BEQ $22a8        ; → L_22A8
    $228D: 38         SEC           
    $228E: BD 52 24   LDA $2452,x   
    $2291: ED 3C 24   SBC $243c     
    $2294: 9D 52 24   STA $2452,x   
    $2297: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $229A: BD 4F 24   LDA $244f,x   
    $229D: E9 00      SBC #$00      
    $229F: 9D 4F 24   STA $244f,x   
    $22A2: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $22A5: 4C C0 22   JMP $22c0        ; → L_22C0
L_22A8:
    $22A8: 18         CLC           
    $22A9: BD 52 24   LDA $2452,x   
    $22AC: 6D 3C 24   ADC $243c     
    $22AF: 9D 52 24   STA $2452,x   
    $22B2: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $22B5: BD 4F 24   LDA $244f,x   
    $22B8: 69 00      ADC #$00      
    $22BA: 9D 4F 24   STA $244f,x   
    $22BD: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_22C0:
    $22C0: AD 58 24   LDA $2458     
    $22C3: 29 01      AND #$01      
    $22C5: F0 35      BEQ $22fc        ; → L_22FC
    $22C7: BD 4F 24   LDA $244f,x   
    $22CA: F0 30      BEQ $22fc        ; → L_22FC
    $22CC: BD 2A 24   LDA $242a,x   
    $22CF: F0 2B      BEQ $22fc        ; → L_22FC
    $22D1: BD 2D 24   LDA $242d,x   
    $22D4: 29 1F      AND #$1f      
    $22D6: 38         SEC           
    $22D7: E9 01      SBC #$01      
    $22D9: DD 2A 24   CMP $242a,x   
    $22DC: AC 23 24   LDY $2423     
    $22DF: 90 10      BCC $22f1        ; → L_22F1
    $22E1: BD 4F 24   LDA $244f,x   
    $22E4: DE 4F 24   DEC $244f,x   
    $22E7: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $22EA: BD 30 24   LDA $2430,x   
    $22ED: 29 FE      AND #$fe      
    $22EF: D0 08      BNE $22f9        ; → L_22F9
L_22F1:
    $22F1: BD 4F 24   LDA $244f,x   
    $22F4: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $22F7: A9 80      LDA #$80      
L_22F9:
    $22F9: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_22FC:
    $22FC: AD 58 24   LDA $2458     
    $22FF: 29 02      AND #$02      
    $2301: F0 25      BEQ $2328        ; → L_2328
    $2303: BD 2D 24   LDA $242d,x   
    $2306: 29 1F      AND #$1f      
    $2308: C9 10      CMP #$10      
    $230A: 90 1C      BCC $2328        ; → L_2328
    $230C: BD 2A 24   LDA $242a,x   
    $230F: C9 18      CMP #$18      
    $2311: B0 15      BCS $2328        ; → L_2328
    $2313: AD 5A 24   LDA $245a     
    $2316: 29 01      AND #$01      
    $2318: F0 0E      BEQ $2328        ; → L_2328
    $231A: BD 4F 24   LDA $244f,x   
    $231D: F0 09      BEQ $2328        ; → L_2328
    $231F: DE 4F 24   DEC $244f,x   
    $2322: AC 23 24   LDY $2423     
    $2325: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_2328:
    $2328: AD 58 24   LDA $2458     
    $232B: 29 04      AND #$04      
    $232D: F0 2A      BEQ $2359        ; → L_2359
    $232F: AD 5A 24   LDA $245a     
    $2332: 29 01      AND #$01      
    $2334: F0 09      BEQ $233f        ; → L_233F
    $2336: BD 33 24   LDA $2433,x   
    $2339: 18         CLC           
    $233A: 69 0C      ADC #$0c      
    $233C: 4C 42 23   JMP $2342        ; → L_2342
L_233F:
    $233F: BD 33 24   LDA $2433,x   
L_2342:
    $2342: 0A         ASL a         
    $2343: A8         TAY           
    $2344: B9 60 23   LDA $2360,y   
    $2347: 8D 3B 24   STA $243b     
    $234A: B9 61 23   LDA $2361,y   
    $234D: AC 23 24   LDY $2423     
    $2350: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $2353: AD 3B 24   LDA $243b     
    $2356: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_2359:
    $2359: CA         DEX           
    $235A: 30 03      BMI $235f        ; → L_235F
    $235C: 4C 49 20   JMP $2049        ; → L_2049
L_235F:
    $235F: 60         RTS           
; ----- data gap $2360-$27E7 (1160 bytes) -----

L_27E8:
    $27E8: A0 00      LDY #$00      
    $27EA: 0A         ASL a         
    $27EB: 8D 3C 24   STA $243c     
    $27EE: 0A         ASL a         
    $27EF: 18         CLC           
    $27F0: 6D 3C 24   ADC $243c     
    $27F3: AA         TAX           
L_27F4:
    $27F4: BD E1 24   LDA $24e1,x   
    $27F7: 99 DB 24   STA $24db,y   
    $27FA: E8         INX           
    $27FB: C8         INY           
    $27FC: C0 06      CPY #$06      
    $27FE: D0 F4      BNE $27f4        ; → L_27F4
    $2800: A9 40      LDA #$40      
    $2802: 8D 4E 24   STA $244e     
    $2805: 60         RTS           
; ----- data gap $2806-$280B (6 bytes) -----

sub_280C:
    $280C: EA         NOP           
    $280D: A9 00      LDA #$00      
    $280F: 20 F6 1F   JSR $1ff6        ; → sub_1FF6
    $2812: A9 0F      LDA #$0f      
    $2814: 8D 18 D4   STA $d418      ;VOL
    $2817: 60         RTS           
; ----- data gap $2818-$2835 (30 bytes) -----

sub_2836:
    $2836: 4C E8 30   JMP $30e8        ; → L_30E8
; ----- data gap $2839-$283B (3 bytes) -----

sub_283C:
    $283C: EE 9A 2C   INC $2c9a     
    $283F: 2C 8E 2C   BIT $2c8e     
    $2842: 30 1E      BMI $2862        ; → L_2862
    $2844: 50 36      BVC $287c        ; → L_287C
    $2846: A9 00      LDA #$00      
    $2848: 8D 9A 2C   STA $2c9a     
    $284B: A2 02      LDX #$02      
L_284D:
    $284D: 9D 64 2C   STA $2c64,x   
    $2850: 9D 67 2C   STA $2c67,x   
    $2853: 9D 6A 2C   STA $2c6a,x   
    $2856: 9D 73 2C   STA $2c73,x   
    $2859: CA         DEX           
    $285A: 10 F1      BPL $284d        ; → L_284D
    $285C: 8D 8E 2C   STA $2c8e     
    $285F: 4C 7C 28   JMP $287c        ; → L_287C
L_2862:
    $2862: 50 15      BVC $2879        ; → L_2879
    $2864: A9 00      LDA #$00      
    $2866: 8D 04 D4   STA $d404      ;V1_CTRL
    $2869: 8D 0B D4   STA $d40b      ;V2_CTRL
    $286C: 8D 12 D4   STA $d412      ;V3_CTRL
    $286F: A9 0F      LDA #$0f      
    $2871: 8D 18 D4   STA $d418      ;VOL
    $2874: A9 80      LDA #$80      
    $2876: 8D 8E 2C   STA $2c8e     
L_2879:
    $2879: 4C 9F 2B   JMP $2b9f        ; → L_2B9F
L_287C:
    $287C: A2 02      LDX #$02      
    $287E: CE 8B 2C   DEC $2c8b     
    $2881: 10 06      BPL $2889        ; → L_2889
    $2883: AD 8C 2C   LDA $2c8c     
    $2886: 8D 8B 2C   STA $2c8b     
L_2889:
    $2889: BD 60 2C   LDA $2c60,x   
    $288C: 8D 63 2C   STA $2c63     
    $288F: A8         TAY           
    $2890: AD 8B 2C   LDA $2c8b     
    $2893: CD 8C 2C   CMP $2c8c     
    $2896: D0 15      BNE $28ad        ; → L_28AD
    $2898: BD 1B 2D   LDA $2d1b,x   
    $289B: 85 FB      STA $fb       
    $289D: BD 1E 2D   LDA $2d1e,x   
    $28A0: 85 FC      STA $fc       
    $28A2: DE 6A 2C   DEC $2c6a,x   
    $28A5: 30 09      BMI $28b0        ; → L_28B0
    $28A7: 4C 8A 29   JMP $298a        ; → L_298A
; ----- data gap $28AA-$28AC (3 bytes) -----

L_28AD:
    $28AD: 4C A9 29   JMP $29a9        ; → L_29A9
L_28B0:
    $28B0: BC 64 2C   LDY $2c64,x   
    $28B3: B1 FB      LDA ($fb),y   
    $28B5: C9 FF      CMP #$ff      
    $28B7: D0 11      BNE $28ca        ; → L_28CA
    $28B9: A9 00      LDA #$00      
    $28BB: 9D 6A 2C   STA $2c6a,x   
    $28BE: 9D 64 2C   STA $2c64,x   
    $28C1: 9D 67 2C   STA $2c67,x   
    $28C4: 4C B0 28   JMP $28b0        ; → L_28B0
; ----- data gap $28C7-$28C9 (3 bytes) -----

L_28CA:
    $28CA: A8         TAY           
    $28CB: B9 27 2D   LDA $2d27,y   
    $28CE: 85 FD      STA $fd       
    $28D0: B9 36 2D   LDA $2d36,y   
    $28D3: 85 FE      STA $fe       
    $28D5: A9 00      LDA #$00      
    $28D7: 9D 95 2C   STA $2c95,x   
    $28DA: BC 67 2C   LDY $2c67,x   
    $28DD: A9 FF      LDA #$ff      
    $28DF: 8D 79 2C   STA $2c79     
    $28E2: B1 FD      LDA ($fd),y   
    $28E4: 9D 6D 2C   STA $2c6d,x   
    $28E7: 8D 7A 2C   STA $2c7a     
    $28EA: 29 1F      AND #$1f      
    $28EC: 9D 6A 2C   STA $2c6a,x   
    $28EF: 2C 7A 2C   BIT $2c7a     
    $28F2: 70 3F      BVS $2933        ; → L_2933
    $28F4: FE 67 2C   INC $2c67,x   
    $28F7: AD 7A 2C   LDA $2c7a     
    $28FA: 10 11      BPL $290d        ; → L_290D
    $28FC: C8         INY           
    $28FD: B1 FD      LDA ($fd),y   
    $28FF: 10 06      BPL $2907        ; → L_2907
    $2901: 9D 95 2C   STA $2c95,x   
    $2904: 4C 0A 29   JMP $290a        ; → L_290A
L_2907:
    $2907: 9D 76 2C   STA $2c76,x   
L_290A:
    $290A: FE 67 2C   INC $2c67,x   
L_290D:
    $290D: C8         INY           
    $290E: B1 FD      LDA ($fd),y   
    $2910: 9D 73 2C   STA $2c73,x   
    $2913: 0A         ASL a         
    $2914: A8         TAY           
    $2915: B9 A0 2B   LDA $2ba0,y   
    $2918: 8D 7B 2C   STA $2c7b     
    $291B: B9 A1 2B   LDA $2ba1,y   
    $291E: AC 63 2C   LDY $2c63     
    $2921: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $2924: 9D 8F 2C   STA $2c8f,x   
    $2927: AD 7B 2C   LDA $2c7b     
    $292A: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $292D: 9D 92 2C   STA $2c92,x   
    $2930: 4C 36 29   JMP $2936        ; → L_2936
L_2933:
    $2933: CE 79 2C   DEC $2c79     
L_2936:
    $2936: AC 63 2C   LDY $2c63     
    $2939: BD 76 2C   LDA $2c76,x   
    $293C: 8E 7C 2C   STX $2c7c     
    $293F: 0A         ASL a         
    $2940: 0A         ASL a         
    $2941: 0A         ASL a         
    $2942: AA         TAX           
    $2943: BD 9D 2C   LDA $2c9d,x   
    $2946: 8D 7D 2C   STA $2c7d     
    $2949: BD 9D 2C   LDA $2c9d,x   
    $294C: 2D 79 2C   AND $2c79     
    $294F: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $2952: BD 9B 2C   LDA $2c9b,x   
    $2955: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $2958: BD 9C 2C   LDA $2c9c,x   
    $295B: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $295E: BD 9E 2C   LDA $2c9e,x   
    $2961: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $2964: BD 9F 2C   LDA $2c9f,x   
    $2967: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $296A: AE 7C 2C   LDX $2c7c     
    $296D: AD 7D 2C   LDA $2c7d     
    $2970: 9D 70 2C   STA $2c70,x   
    $2973: FE 67 2C   INC $2c67,x   
    $2976: BC 67 2C   LDY $2c67,x   
    $2979: B1 FD      LDA ($fd),y   
    $297B: C9 FF      CMP #$ff      
    $297D: D0 08      BNE $2987        ; → L_2987
    $297F: A9 00      LDA #$00      
    $2981: 9D 67 2C   STA $2c67,x   
    $2984: FE 64 2C   INC $2c64,x   
L_2987:
    $2987: 4C 99 2B   JMP $2b99        ; → L_2B99
L_298A:
    $298A: AC 63 2C   LDY $2c63     
    $298D: BD 6D 2C   LDA $2c6d,x   
    $2990: 29 20      AND #$20      
    $2992: D0 15      BNE $29a9        ; → L_29A9
    $2994: BD 6A 2C   LDA $2c6a,x   
    $2997: D0 10      BNE $29a9        ; → L_29A9
    $2999: BD 70 2C   LDA $2c70,x   
    $299C: 29 FE      AND #$fe      
    $299E: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $29A1: A9 00      LDA #$00      
    $29A3: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $29A6: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_29A9:
    $29A9: BD 76 2C   LDA $2c76,x   
    $29AC: 0A         ASL a         
    $29AD: 0A         ASL a         
    $29AE: 0A         ASL a         
    $29AF: A8         TAY           
    $29B0: 8C 8D 2C   STY $2c8d     
    $29B3: B9 A2 2C   LDA $2ca2,y   
    $29B6: 8D 98 2C   STA $2c98     
    $29B9: B9 A1 2C   LDA $2ca1,y   
    $29BC: 8D 7F 2C   STA $2c7f     
    $29BF: B9 A0 2C   LDA $2ca0,y   
    $29C2: 8D 7E 2C   STA $2c7e     
    $29C5: F0 6F      BEQ $2a36        ; → L_2A36
    $29C7: AD 9A 2C   LDA $2c9a     
    $29CA: 29 07      AND #$07      
    $29CC: C9 04      CMP #$04      
    $29CE: 90 02      BCC $29d2        ; → L_29D2
    $29D0: 49 07      EOR #$07      
L_29D2:
    $29D2: 8D 84 2C   STA $2c84     
    $29D5: BD 73 2C   LDA $2c73,x   
    $29D8: 0A         ASL a         
    $29D9: A8         TAY           
    $29DA: 38         SEC           
    $29DB: B9 A2 2B   LDA $2ba2,y   
    $29DE: F9 A0 2B   SBC $2ba0,y   
    $29E1: 8D 80 2C   STA $2c80     
    $29E4: B9 A3 2B   LDA $2ba3,y   
    $29E7: F9 A1 2B   SBC $2ba1,y   
L_29EA:
    $29EA: 4A         LSR a         
    $29EB: 6E 80 2C   ROR $2c80     
    $29EE: CE 7E 2C   DEC $2c7e     
    $29F1: 10 F7      BPL $29ea        ; → L_29EA
    $29F3: 8D 81 2C   STA $2c81     
    $29F6: B9 A0 2B   LDA $2ba0,y   
    $29F9: 8D 82 2C   STA $2c82     
    $29FC: B9 A1 2B   LDA $2ba1,y   
    $29FF: 8D 83 2C   STA $2c83     
    $2A02: BD 6D 2C   LDA $2c6d,x   
    $2A05: 29 1F      AND #$1f      
    $2A07: C9 08      CMP #$08      
    $2A09: 90 1C      BCC $2a27        ; → L_2A27
    $2A0B: AC 84 2C   LDY $2c84     
L_2A0E:
    $2A0E: 88         DEY           
    $2A0F: 30 16      BMI $2a27        ; → L_2A27
    $2A11: 18         CLC           
    $2A12: AD 82 2C   LDA $2c82     
    $2A15: 6D 80 2C   ADC $2c80     
    $2A18: 8D 82 2C   STA $2c82     
    $2A1B: AD 83 2C   LDA $2c83     
    $2A1E: 6D 81 2C   ADC $2c81     
    $2A21: 8D 83 2C   STA $2c83     
    $2A24: 4C 0E 2A   JMP $2a0e        ; → L_2A0E
L_2A27:
    $2A27: AC 63 2C   LDY $2c63     
    $2A2A: AD 82 2C   LDA $2c82     
    $2A2D: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $2A30: AD 83 2C   LDA $2c83     
    $2A33: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_2A36:
    $2A36: AD 98 2C   LDA $2c98     
    $2A39: 29 08      AND #$08      
    $2A3B: F0 15      BEQ $2a52        ; → L_2A52
    $2A3D: AC 8D 2C   LDY $2c8d     
    $2A40: B9 9B 2C   LDA $2c9b,y   
    $2A43: 6D 7F 2C   ADC $2c7f     
    $2A46: 99 9B 2C   STA $2c9b,y   
    $2A49: AC 63 2C   LDY $2c63     
    $2A4C: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $2A4F: 4C B9 2A   JMP $2ab9        ; → L_2AB9
L_2A52:
    $2A52: AD 7F 2C   LDA $2c7f     
    $2A55: F0 62      BEQ $2ab9        ; → L_2AB9
    $2A57: AC 8D 2C   LDY $2c8d     
    $2A5A: 29 1F      AND #$1f      
    $2A5C: DE 85 2C   DEC $2c85,x   
    $2A5F: 10 58      BPL $2ab9        ; → L_2AB9
    $2A61: 9D 85 2C   STA $2c85,x   
    $2A64: AD 7F 2C   LDA $2c7f     
    $2A67: 29 E0      AND #$e0      
    $2A69: 8D 99 2C   STA $2c99     
    $2A6C: BD 88 2C   LDA $2c88,x   
    $2A6F: D0 1A      BNE $2a8b        ; → L_2A8B
    $2A71: AD 99 2C   LDA $2c99     
    $2A74: 18         CLC           
    $2A75: 79 9B 2C   ADC $2c9b,y   
    $2A78: 48         PHA           
    $2A79: B9 9C 2C   LDA $2c9c,y   
    $2A7C: 69 00      ADC #$00      
    $2A7E: 29 0F      AND #$0f      
    $2A80: 48         PHA           
    $2A81: C9 0E      CMP #$0e      
    $2A83: D0 1D      BNE $2aa2        ; → L_2AA2
    $2A85: FE 88 2C   INC $2c88,x   
    $2A88: 4C A2 2A   JMP $2aa2        ; → L_2AA2
L_2A8B:
    $2A8B: 38         SEC           
    $2A8C: B9 9B 2C   LDA $2c9b,y   
    $2A8F: ED 99 2C   SBC $2c99     
    $2A92: 48         PHA           
    $2A93: B9 9C 2C   LDA $2c9c,y   
    $2A96: E9 00      SBC #$00      
    $2A98: 29 0F      AND #$0f      
    $2A9A: 48         PHA           
    $2A9B: C9 08      CMP #$08      
    $2A9D: D0 03      BNE $2aa2        ; → L_2AA2
    $2A9F: DE 88 2C   DEC $2c88,x   
L_2AA2:
    $2AA2: 8E 7C 2C   STX $2c7c     
    $2AA5: AE 63 2C   LDX $2c63     
    $2AA8: 68         PLA           
    $2AA9: 99 9C 2C   STA $2c9c,y   
    $2AAC: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $2AAF: 68         PLA           
    $2AB0: 99 9B 2C   STA $2c9b,y   
    $2AB3: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $2AB6: AE 7C 2C   LDX $2c7c     
L_2AB9:
    $2AB9: AC 63 2C   LDY $2c63     
    $2ABC: BD 95 2C   LDA $2c95,x   
    $2ABF: F0 3F      BEQ $2b00        ; → L_2B00
    $2AC1: 29 7E      AND #$7e      
    $2AC3: 8D 7C 2C   STA $2c7c     
    $2AC6: BD 95 2C   LDA $2c95,x   
    $2AC9: 29 01      AND #$01      
    $2ACB: F0 1B      BEQ $2ae8        ; → L_2AE8
    $2ACD: 38         SEC           
    $2ACE: BD 92 2C   LDA $2c92,x   
    $2AD1: ED 7C 2C   SBC $2c7c     
    $2AD4: 9D 92 2C   STA $2c92,x   
    $2AD7: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $2ADA: BD 8F 2C   LDA $2c8f,x   
    $2ADD: E9 00      SBC #$00      
    $2ADF: 9D 8F 2C   STA $2c8f,x   
    $2AE2: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $2AE5: 4C 00 2B   JMP $2b00        ; → L_2B00
L_2AE8:
    $2AE8: 18         CLC           
    $2AE9: BD 92 2C   LDA $2c92,x   
    $2AEC: 6D 7C 2C   ADC $2c7c     
    $2AEF: 9D 92 2C   STA $2c92,x   
    $2AF2: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $2AF5: BD 8F 2C   LDA $2c8f,x   
    $2AF8: 69 00      ADC #$00      
    $2AFA: 9D 8F 2C   STA $2c8f,x   
    $2AFD: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_2B00:
    $2B00: AD 98 2C   LDA $2c98     
    $2B03: 29 01      AND #$01      
    $2B05: F0 35      BEQ $2b3c        ; → L_2B3C
    $2B07: BD 8F 2C   LDA $2c8f,x   
    $2B0A: F0 30      BEQ $2b3c        ; → L_2B3C
    $2B0C: BD 6A 2C   LDA $2c6a,x   
    $2B0F: F0 2B      BEQ $2b3c        ; → L_2B3C
    $2B11: BD 6D 2C   LDA $2c6d,x   
    $2B14: 29 1F      AND #$1f      
    $2B16: 38         SEC           
    $2B17: E9 01      SBC #$01      
    $2B19: DD 6A 2C   CMP $2c6a,x   
    $2B1C: AC 63 2C   LDY $2c63     
    $2B1F: 90 10      BCC $2b31        ; → L_2B31
    $2B21: BD 8F 2C   LDA $2c8f,x   
    $2B24: DE 8F 2C   DEC $2c8f,x   
    $2B27: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $2B2A: BD 70 2C   LDA $2c70,x   
    $2B2D: 29 FE      AND #$fe      
    $2B2F: D0 08      BNE $2b39        ; → L_2B39
L_2B31:
    $2B31: BD 8F 2C   LDA $2c8f,x   
    $2B34: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $2B37: A9 80      LDA #$80      
L_2B39:
    $2B39: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_2B3C:
    $2B3C: AD 98 2C   LDA $2c98     
    $2B3F: 29 02      AND #$02      
    $2B41: F0 25      BEQ $2b68        ; → L_2B68
    $2B43: BD 6D 2C   LDA $2c6d,x   
    $2B46: 29 1F      AND #$1f      
    $2B48: C9 0C      CMP #$0c      
    $2B4A: 90 1C      BCC $2b68        ; → L_2B68
    $2B4C: BD 6A 2C   LDA $2c6a,x   
    $2B4F: C9 08      CMP #$08      
    $2B51: B0 15      BCS $2b68        ; → L_2B68
    $2B53: AD 9A 2C   LDA $2c9a     
    $2B56: 29 01      AND #$01      
    $2B58: F0 0E      BEQ $2b68        ; → L_2B68
    $2B5A: BD 8F 2C   LDA $2c8f,x   
    $2B5D: F0 09      BEQ $2b68        ; → L_2B68
    $2B5F: DE 8F 2C   DEC $2c8f,x   
    $2B62: AC 63 2C   LDY $2c63     
    $2B65: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_2B68:
    $2B68: AD 98 2C   LDA $2c98     
    $2B6B: 29 04      AND #$04      
    $2B6D: F0 2A      BEQ $2b99        ; → L_2B99
    $2B6F: AD 9A 2C   LDA $2c9a     
    $2B72: 29 01      AND #$01      
    $2B74: F0 09      BEQ $2b7f        ; → L_2B7F
    $2B76: BD 73 2C   LDA $2c73,x   
    $2B79: 18         CLC           
    $2B7A: 69 0C      ADC #$0c      
    $2B7C: 4C 82 2B   JMP $2b82        ; → L_2B82
L_2B7F:
    $2B7F: BD 73 2C   LDA $2c73,x   
L_2B82:
    $2B82: 0A         ASL a         
    $2B83: A8         TAY           
    $2B84: B9 A0 2B   LDA $2ba0,y   
    $2B87: 8D 7B 2C   STA $2c7b     
    $2B8A: B9 A1 2B   LDA $2ba1,y   
    $2B8D: AC 63 2C   LDY $2c63     
    $2B90: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $2B93: AD 7B 2C   LDA $2c7b     
    $2B96: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_2B99:
    $2B99: CA         DEX           
    $2B9A: 30 03      BMI $2b9f        ; → L_2B9F
    $2B9C: 4C 89 28   JMP $2889        ; → L_2889
L_2B9F:
    $2B9F: 60         RTS           
; ----- data gap $2BA0-$30E7 (1352 bytes) -----

L_30E8:
    $30E8: A0 00      LDY #$00      
    $30EA: 0A         ASL a         
    $30EB: 8D 7C 2C   STA $2c7c     
    $30EE: 0A         ASL a         
    $30EF: 18         CLC           
    $30F0: 6D 7C 2C   ADC $2c7c     
    $30F3: AA         TAX           
L_30F4:
    $30F4: BD 21 2D   LDA $2d21,x   
    $30F7: 99 1B 2D   STA $2d1b,y   
    $30FA: E8         INX           
    $30FB: C8         INY           
    $30FC: C0 06      CPY #$06      
    $30FE: D0 F4      BNE $30f4        ; → L_30F4
    $3100: A9 40      LDA #$40      
    $3102: 8D 8E 2C   STA $2c8e     
    $3105: 60         RTS           
; ----- data gap $3106-$310B (6 bytes) -----

sub_310C:
    $310C: EA         NOP           
    $310D: A9 00      LDA #$00      
    $310F: 20 36 28   JSR $2836        ; → sub_2836
    $3112: A9 0F      LDA #$0f      
    $3114: 8D 18 D4   STA $d418      ;VOL
    $3117: 60         RTS           
; ----- data gap $3118-$3158 (65 bytes) -----

sub_3159:
    $3159: 4C AB 38   JMP $38ab        ; → L_38AB
; ----- data gap $315C-$315E (3 bytes) -----

sub_315F:
    $315F: EE BD 35   INC $35bd     
    $3162: 2C B1 35   BIT $35b1     
    $3165: 30 1E      BMI $3185        ; → L_3185
    $3167: 50 36      BVC $319f        ; → L_319F
    $3169: A9 00      LDA #$00      
    $316B: 8D BD 35   STA $35bd     
    $316E: A2 02      LDX #$02      
L_3170:
    $3170: 9D 87 35   STA $3587,x   
    $3173: 9D 8A 35   STA $358a,x   
    $3176: 9D 8D 35   STA $358d,x   
    $3179: 9D 96 35   STA $3596,x   
    $317C: CA         DEX           
    $317D: 10 F1      BPL $3170        ; → L_3170
    $317F: 8D B1 35   STA $35b1     
    $3182: 4C 9F 31   JMP $319f        ; → L_319F
L_3185:
    $3185: 50 15      BVC $319c        ; → L_319C
    $3187: A9 00      LDA #$00      
    $3189: 8D 04 D4   STA $d404      ;V1_CTRL
    $318C: 8D 0B D4   STA $d40b      ;V2_CTRL
    $318F: 8D 12 D4   STA $d412      ;V3_CTRL
    $3192: A9 0F      LDA #$0f      
    $3194: 8D 18 D4   STA $d418      ;VOL
    $3197: A9 80      LDA #$80      
    $3199: 8D B1 35   STA $35b1     
L_319C:
    $319C: 4C C2 34   JMP $34c2        ; → L_34C2
L_319F:
    $319F: A2 02      LDX #$02      
    $31A1: CE AE 35   DEC $35ae     
    $31A4: 10 06      BPL $31ac        ; → L_31AC
    $31A6: AD AF 35   LDA $35af     
    $31A9: 8D AE 35   STA $35ae     
L_31AC:
    $31AC: BD 83 35   LDA $3583,x   
    $31AF: 8D 86 35   STA $3586     
    $31B2: A8         TAY           
    $31B3: AD AE 35   LDA $35ae     
    $31B6: CD AF 35   CMP $35af     
    $31B9: D0 15      BNE $31d0        ; → L_31D0
    $31BB: BD 3E 36   LDA $363e,x   
    $31BE: 85 FB      STA $fb       
    $31C0: BD 41 36   LDA $3641,x   
    $31C3: 85 FC      STA $fc       
    $31C5: DE 8D 35   DEC $358d,x   
    $31C8: 30 09      BMI $31d3        ; → L_31D3
    $31CA: 4C AD 32   JMP $32ad        ; → L_32AD
; ----- data gap $31CD-$31CF (3 bytes) -----

L_31D0:
    $31D0: 4C CC 32   JMP $32cc        ; → L_32CC
L_31D3:
    $31D3: BC 87 35   LDY $3587,x   
    $31D6: B1 FB      LDA ($fb),y   
    $31D8: C9 FF      CMP #$ff      
    $31DA: D0 11      BNE $31ed        ; → L_31ED
    $31DC: A9 00      LDA #$00      
    $31DE: 9D 8D 35   STA $358d,x   
    $31E1: 9D 87 35   STA $3587,x   
    $31E4: 9D 8A 35   STA $358a,x   
    $31E7: 4C D3 31   JMP $31d3        ; → L_31D3
; ----- data gap $31EA-$31EC (3 bytes) -----

L_31ED:
    $31ED: A8         TAY           
    $31EE: B9 4A 36   LDA $364a,y   
    $31F1: 85 FD      STA $fd       
    $31F3: B9 55 36   LDA $3655,y   
    $31F6: 85 FE      STA $fe       
    $31F8: A9 00      LDA #$00      
    $31FA: 9D B8 35   STA $35b8,x   
    $31FD: BC 8A 35   LDY $358a,x   
    $3200: A9 FF      LDA #$ff      
    $3202: 8D 9C 35   STA $359c     
    $3205: B1 FD      LDA ($fd),y   
    $3207: 9D 90 35   STA $3590,x   
    $320A: 8D 9D 35   STA $359d     
    $320D: 29 1F      AND #$1f      
    $320F: 9D 8D 35   STA $358d,x   
    $3212: 2C 9D 35   BIT $359d     
    $3215: 70 3F      BVS $3256        ; → L_3256
    $3217: FE 8A 35   INC $358a,x   
    $321A: AD 9D 35   LDA $359d     
    $321D: 10 11      BPL $3230        ; → L_3230
    $321F: C8         INY           
    $3220: B1 FD      LDA ($fd),y   
    $3222: 10 06      BPL $322a        ; → L_322A
    $3224: 9D B8 35   STA $35b8,x   
    $3227: 4C 2D 32   JMP $322d        ; → L_322D
L_322A:
    $322A: 9D 99 35   STA $3599,x   
L_322D:
    $322D: FE 8A 35   INC $358a,x   
L_3230:
    $3230: C8         INY           
    $3231: B1 FD      LDA ($fd),y   
    $3233: 9D 96 35   STA $3596,x   
    $3236: 0A         ASL a         
    $3237: A8         TAY           
    $3238: B9 C3 34   LDA $34c3,y   
    $323B: 8D 9E 35   STA $359e     
    $323E: B9 C4 34   LDA $34c4,y   
    $3241: AC 86 35   LDY $3586     
    $3244: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $3247: 9D B2 35   STA $35b2,x   
    $324A: AD 9E 35   LDA $359e     
    $324D: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $3250: 9D B5 35   STA $35b5,x   
    $3253: 4C 59 32   JMP $3259        ; → L_3259
L_3256:
    $3256: CE 9C 35   DEC $359c     
L_3259:
    $3259: AC 86 35   LDY $3586     
    $325C: BD 99 35   LDA $3599,x   
    $325F: 8E 9F 35   STX $359f     
    $3262: 0A         ASL a         
    $3263: 0A         ASL a         
    $3264: 0A         ASL a         
    $3265: AA         TAX           
    $3266: BD C0 35   LDA $35c0,x   
    $3269: 8D A0 35   STA $35a0     
    $326C: BD C0 35   LDA $35c0,x   
    $326F: 2D 9C 35   AND $359c     
    $3272: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $3275: BD BE 35   LDA $35be,x   
    $3278: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $327B: BD BF 35   LDA $35bf,x   
    $327E: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $3281: BD C1 35   LDA $35c1,x   
    $3284: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $3287: BD C2 35   LDA $35c2,x   
    $328A: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $328D: AE 9F 35   LDX $359f     
    $3290: AD A0 35   LDA $35a0     
    $3293: 9D 93 35   STA $3593,x   
    $3296: FE 8A 35   INC $358a,x   
    $3299: BC 8A 35   LDY $358a,x   
    $329C: B1 FD      LDA ($fd),y   
    $329E: C9 FF      CMP #$ff      
    $32A0: D0 08      BNE $32aa        ; → L_32AA
    $32A2: A9 00      LDA #$00      
    $32A4: 9D 8A 35   STA $358a,x   
    $32A7: FE 87 35   INC $3587,x   
L_32AA:
    $32AA: 4C BC 34   JMP $34bc        ; → L_34BC
L_32AD:
    $32AD: AC 86 35   LDY $3586     
    $32B0: BD 90 35   LDA $3590,x   
    $32B3: 29 20      AND #$20      
    $32B5: D0 15      BNE $32cc        ; → L_32CC
    $32B7: BD 8D 35   LDA $358d,x   
    $32BA: D0 10      BNE $32cc        ; → L_32CC
    $32BC: BD 93 35   LDA $3593,x   
    $32BF: 29 FE      AND #$fe      
    $32C1: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $32C4: A9 00      LDA #$00      
    $32C6: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $32C9: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_32CC:
    $32CC: BD 99 35   LDA $3599,x   
    $32CF: 0A         ASL a         
    $32D0: 0A         ASL a         
    $32D1: 0A         ASL a         
    $32D2: A8         TAY           
    $32D3: 8C B0 35   STY $35b0     
    $32D6: B9 C5 35   LDA $35c5,y   
    $32D9: 8D BB 35   STA $35bb     
    $32DC: B9 C4 35   LDA $35c4,y   
    $32DF: 8D A2 35   STA $35a2     
    $32E2: B9 C3 35   LDA $35c3,y   
    $32E5: 8D A1 35   STA $35a1     
    $32E8: F0 6F      BEQ $3359        ; → L_3359
    $32EA: AD BD 35   LDA $35bd     
    $32ED: 29 07      AND #$07      
    $32EF: C9 04      CMP #$04      
    $32F1: 90 02      BCC $32f5        ; → L_32F5
    $32F3: 49 07      EOR #$07      
L_32F5:
    $32F5: 8D A7 35   STA $35a7     
    $32F8: BD 96 35   LDA $3596,x   
    $32FB: 0A         ASL a         
    $32FC: A8         TAY           
    $32FD: 38         SEC           
    $32FE: B9 C5 34   LDA $34c5,y   
    $3301: F9 C3 34   SBC $34c3,y   
    $3304: 8D A3 35   STA $35a3     
    $3307: B9 C6 34   LDA $34c6,y   
    $330A: F9 C4 34   SBC $34c4,y   
L_330D:
    $330D: 4A         LSR a         
    $330E: 6E A3 35   ROR $35a3     
    $3311: CE A1 35   DEC $35a1     
    $3314: 10 F7      BPL $330d        ; → L_330D
    $3316: 8D A4 35   STA $35a4     
    $3319: B9 C3 34   LDA $34c3,y   
    $331C: 8D A5 35   STA $35a5     
    $331F: B9 C4 34   LDA $34c4,y   
    $3322: 8D A6 35   STA $35a6     
    $3325: BD 90 35   LDA $3590,x   
    $3328: 29 1F      AND #$1f      
    $332A: C9 08      CMP #$08      
    $332C: 90 1C      BCC $334a        ; → L_334A
    $332E: AC A7 35   LDY $35a7     
L_3331:
    $3331: 88         DEY           
    $3332: 30 16      BMI $334a        ; → L_334A
    $3334: 18         CLC           
    $3335: AD A5 35   LDA $35a5     
    $3338: 6D A3 35   ADC $35a3     
    $333B: 8D A5 35   STA $35a5     
    $333E: AD A6 35   LDA $35a6     
    $3341: 6D A4 35   ADC $35a4     
    $3344: 8D A6 35   STA $35a6     
    $3347: 4C 31 33   JMP $3331        ; → L_3331
L_334A:
    $334A: AC 86 35   LDY $3586     
    $334D: AD A5 35   LDA $35a5     
    $3350: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $3353: AD A6 35   LDA $35a6     
    $3356: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_3359:
    $3359: AD BB 35   LDA $35bb     
    $335C: 29 08      AND #$08      
    $335E: F0 15      BEQ $3375        ; → L_3375
    $3360: AC B0 35   LDY $35b0     
    $3363: B9 BE 35   LDA $35be,y   
    $3366: 6D A2 35   ADC $35a2     
    $3369: 99 BE 35   STA $35be,y   
    $336C: AC 86 35   LDY $3586     
    $336F: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $3372: 4C DC 33   JMP $33dc        ; → L_33DC
L_3375:
    $3375: AD A2 35   LDA $35a2     
    $3378: F0 62      BEQ $33dc        ; → L_33DC
    $337A: AC B0 35   LDY $35b0     
    $337D: 29 1F      AND #$1f      
    $337F: DE A8 35   DEC $35a8,x   
    $3382: 10 58      BPL $33dc        ; → L_33DC
    $3384: 9D A8 35   STA $35a8,x   
    $3387: AD A2 35   LDA $35a2     
    $338A: 29 E0      AND #$e0      
    $338C: 8D BC 35   STA $35bc     
    $338F: BD AB 35   LDA $35ab,x   
    $3392: D0 1A      BNE $33ae        ; → L_33AE
    $3394: AD BC 35   LDA $35bc     
    $3397: 18         CLC           
    $3398: 79 BE 35   ADC $35be,y   
    $339B: 48         PHA           
    $339C: B9 BF 35   LDA $35bf,y   
    $339F: 69 00      ADC #$00      
    $33A1: 29 0F      AND #$0f      
    $33A3: 48         PHA           
    $33A4: C9 0E      CMP #$0e      
    $33A6: D0 1D      BNE $33c5        ; → L_33C5
    $33A8: FE AB 35   INC $35ab,x   
    $33AB: 4C C5 33   JMP $33c5        ; → L_33C5
L_33AE:
    $33AE: 38         SEC           
    $33AF: B9 BE 35   LDA $35be,y   
    $33B2: ED BC 35   SBC $35bc     
    $33B5: 48         PHA           
    $33B6: B9 BF 35   LDA $35bf,y   
    $33B9: E9 00      SBC #$00      
    $33BB: 29 0F      AND #$0f      
    $33BD: 48         PHA           
    $33BE: C9 08      CMP #$08      
    $33C0: D0 03      BNE $33c5        ; → L_33C5
    $33C2: DE AB 35   DEC $35ab,x   
L_33C5:
    $33C5: 8E 9F 35   STX $359f     
    $33C8: AE 86 35   LDX $3586     
    $33CB: 68         PLA           
    $33CC: 99 BF 35   STA $35bf,y   
    $33CF: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $33D2: 68         PLA           
    $33D3: 99 BE 35   STA $35be,y   
    $33D6: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $33D9: AE 9F 35   LDX $359f     
L_33DC:
    $33DC: AC 86 35   LDY $3586     
    $33DF: BD B8 35   LDA $35b8,x   
    $33E2: F0 3F      BEQ $3423        ; → L_3423
    $33E4: 29 7E      AND #$7e      
    $33E6: 8D 9F 35   STA $359f     
    $33E9: BD B8 35   LDA $35b8,x   
    $33EC: 29 01      AND #$01      
    $33EE: F0 1B      BEQ $340b        ; → L_340B
    $33F0: 38         SEC           
    $33F1: BD B5 35   LDA $35b5,x   
    $33F4: ED 9F 35   SBC $359f     
    $33F7: 9D B5 35   STA $35b5,x   
    $33FA: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $33FD: BD B2 35   LDA $35b2,x   
    $3400: E9 00      SBC #$00      
    $3402: 9D B2 35   STA $35b2,x   
    $3405: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $3408: 4C 23 34   JMP $3423        ; → L_3423
L_340B:
    $340B: 18         CLC           
    $340C: BD B5 35   LDA $35b5,x   
    $340F: 6D 9F 35   ADC $359f     
    $3412: 9D B5 35   STA $35b5,x   
    $3415: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $3418: BD B2 35   LDA $35b2,x   
    $341B: 69 00      ADC #$00      
    $341D: 9D B2 35   STA $35b2,x   
    $3420: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_3423:
    $3423: AD BB 35   LDA $35bb     
    $3426: 29 01      AND #$01      
    $3428: F0 35      BEQ $345f        ; → L_345F
    $342A: BD B2 35   LDA $35b2,x   
    $342D: F0 30      BEQ $345f        ; → L_345F
    $342F: BD 8D 35   LDA $358d,x   
    $3432: F0 2B      BEQ $345f        ; → L_345F
    $3434: BD 90 35   LDA $3590,x   
    $3437: 29 1F      AND #$1f      
    $3439: 38         SEC           
    $343A: E9 01      SBC #$01      
    $343C: DD 8D 35   CMP $358d,x   
    $343F: AC 86 35   LDY $3586     
    $3442: 90 10      BCC $3454        ; → L_3454
    $3444: BD B2 35   LDA $35b2,x   
    $3447: DE B2 35   DEC $35b2,x   
    $344A: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $344D: BD 93 35   LDA $3593,x   
    $3450: 29 FE      AND #$fe      
    $3452: D0 08      BNE $345c        ; → L_345C
L_3454:
    $3454: BD B2 35   LDA $35b2,x   
    $3457: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $345A: A9 80      LDA #$80      
L_345C:
    $345C: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_345F:
    $345F: AD BB 35   LDA $35bb     
    $3462: 29 02      AND #$02      
    $3464: F0 25      BEQ $348b        ; → L_348B
    $3466: BD 90 35   LDA $3590,x   
    $3469: 29 1F      AND #$1f      
    $346B: C9 10      CMP #$10      
    $346D: 90 1C      BCC $348b        ; → L_348B
    $346F: BD 8D 35   LDA $358d,x   
    $3472: C9 18      CMP #$18      
    $3474: B0 15      BCS $348b        ; → L_348B
    $3476: AD BD 35   LDA $35bd     
    $3479: 29 01      AND #$01      
    $347B: F0 0E      BEQ $348b        ; → L_348B
    $347D: BD B2 35   LDA $35b2,x   
    $3480: F0 09      BEQ $348b        ; → L_348B
    $3482: DE B2 35   DEC $35b2,x   
    $3485: AC 86 35   LDY $3586     
    $3488: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_348B:
    $348B: AD BB 35   LDA $35bb     
    $348E: 29 04      AND #$04      
    $3490: F0 2A      BEQ $34bc        ; → L_34BC
    $3492: AD BD 35   LDA $35bd     
    $3495: 29 01      AND #$01      
    $3497: F0 09      BEQ $34a2        ; → L_34A2
    $3499: BD 96 35   LDA $3596,x   
    $349C: 18         CLC           
    $349D: 69 0C      ADC #$0c      
    $349F: 4C A5 34   JMP $34a5        ; → L_34A5
L_34A2:
    $34A2: BD 96 35   LDA $3596,x   
L_34A5:
    $34A5: 0A         ASL a         
    $34A6: A8         TAY           
    $34A7: B9 C3 34   LDA $34c3,y   
    $34AA: 8D 9E 35   STA $359e     
    $34AD: B9 C4 34   LDA $34c4,y   
    $34B0: AC 86 35   LDY $3586     
    $34B3: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $34B6: AD 9E 35   LDA $359e     
    $34B9: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_34BC:
    $34BC: CA         DEX           
    $34BD: 30 03      BMI $34c2        ; → L_34C2
    $34BF: 4C AC 31   JMP $31ac        ; → L_31AC
L_34C2:
    $34C2: 60         RTS           
; ----- data gap $34C3-$38AA (1000 bytes) -----

L_38AB:
    $38AB: A0 00      LDY #$00      
    $38AD: 0A         ASL a         
    $38AE: 8D 9F 35   STA $359f     
    $38B1: 0A         ASL a         
    $38B2: 18         CLC           
    $38B3: 6D 9F 35   ADC $359f     
    $38B6: AA         TAX           
L_38B7:
    $38B7: BD 44 36   LDA $3644,x   
    $38BA: 99 3E 36   STA $363e,y   
    $38BD: E8         INX           
    $38BE: C8         INY           
    $38BF: C0 06      CPY #$06      
    $38C1: D0 F4      BNE $38b7        ; → L_38B7
    $38C3: A9 40      LDA #$40      
    $38C5: 8D B1 35   STA $35b1     
    $38C8: 60         RTS           
; ----- data gap $38C9-$38CE (6 bytes) -----

sub_38CF:
    $38CF: EA         NOP           
    $38D0: A9 00      LDA #$00      
    $38D2: 20 59 31   JSR $3159        ; → sub_3159
    $38D5: A9 0F      LDA #$0f      
    $38D7: 8D 18 D4   STA $d418      ;VOL
    $38DA: 60         RTS           
