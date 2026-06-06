; ============================================================================
; Rob Hubbard - Adrenalin (1991 Magic Disk 64/CP Verlag)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/HeatWave/Adrenalin.sid
; Load:   $50E0   Init: $50E0   Play: $50E3
; PSID:   4 subtune(s), default subtune 1
; Binary: $50E0-$81D0 (12529 bytes)
;
; Auto-traced 1978 reachable code bytes from init+play.
;
; ============================================================================

; ======= init: =======
init:
    $50E0: 4C E6 50   JMP $50e6        ; → L_50E6
; ======= play: =======
play:
    $50E3: 4C 00 00   JMP $0000     
L_50E6:
    $50E6: 48         PHA           
    $50E7: 20 0A 51   JSR $510a        ; → sub_510A
    $50EA: 68         PLA           
    $50EB: 0A         ASL a         
    $50EC: AA         TAX           
    $50ED: BD 66 51   LDA $5166,x   
    $50F0: 8D 08 51   STA $5108     
    $50F3: BD 67 51   LDA $5167,x   
    $50F6: 8D 09 51   STA $5109     
    $50F9: BD 6E 51   LDA $516e,x   
    $50FC: 8D E4 50   STA $50e4     
    $50FF: BD 6F 51   LDA $516f,x   
    $5102: 8D E5 50   STA $50e5     
    $5105: A9 00      LDA #$00      
    $5107: 4C 00 00   JMP $0000     
sub_510A:
    $510A: 0A         ASL a         
    $510B: AA         TAX           
    $510C: BD 56 51   LDA $5156,x   
    $510F: 85 FA      STA $fa       
    $5111: BD 57 51   LDA $5157,x   
    $5114: 85 FB      STA $fb       
    $5116: BD 4E 51   LDA $514e,x   
    $5119: 85 FC      STA $fc       
    $511B: BD 4F 51   LDA $514f,x   
    $511E: 85 FD      STA $fd       
    $5120: BC 5E 51   LDY $515e,x   
    $5123: BD 5F 51   LDA $515f,x   
    $5126: AA         TAX           
    $5127: 8C 42 51   STY $5142     
    $512A: A0 00      LDY #$00      
    $512C: E8         INX           
    $512D: 4C 3B 51   JMP $513b        ; → L_513B
L_5130:
    $5130: B1 FC      LDA ($fc),y   
    $5132: 91 FA      STA ($fa),y   
    $5134: C8         INY           
    $5135: D0 F9      BNE $5130        ; → L_5130
    $5137: E6 FB      INC $fb       
    $5139: E6 FD      INC $fd       
L_513B:
    $513B: CA         DEX           
    $513C: F0 03      BEQ $5141        ; → L_5141
    $513E: 4C 30 51   JMP $5130        ; → L_5130
L_5141:
    $5141: C0 00      CPY #$00      
    $5143: F0 08      BEQ $514d        ; → L_514D
    $5145: B1 FC      LDA ($fc),y   
    $5147: 91 FA      STA ($fa),y   
    $5149: C8         INY           
    $514A: 4C 41 51   JMP $5141        ; → L_5141
L_514D:
    $514D: 60         RTS           
; ----- data gap $514E-$79FF (10418 bytes) -----

sub_7A00:
    $7A00: 4C B4 7A   JMP $7ab4        ; → sub_7AB4
sub_7A03:
    $7A03: 4C FC 7A   JMP $7afc        ; → L_7AFC
sub_7A06:
    $7A06: 4C 02 7B   JMP $7b02        ; → L_7B02
; ----- data gap $7A09-$7A87 (127 bytes) -----

sub_7A88:
    $7A88: A9 00      LDA #$00      
    $7A8A: A2 7A      LDX #$7a      
L_7A8C:
    $7A8C: 9D 0D 7A   STA $7a0d,x   
    $7A8F: CA         DEX           
    $7A90: 10 FA      BPL $7a8c        ; → L_7A8C
    $7A92: A9 FF      LDA #$ff      
    $7A94: 8D 3E 7A   STA $7a3e     
    $7A97: 8D 3F 7A   STA $7a3f     
    $7A9A: 8D 40 7A   STA $7a40     
    $7A9D: A9 00      LDA #$00      
    $7A9F: A2 02      LDX #$02      
L_7AA1:
    $7AA1: 9D 0D 7A   STA $7a0d,x   
    $7AA4: 9D 10 7A   STA $7a10,x   
    $7AA7: 9D 13 7A   STA $7a13,x   
    $7AAA: 9D 1F 7A   STA $7a1f,x   
    $7AAD: CA         DEX           
    $7AAE: 10 F1      BPL $7aa1        ; → L_7AA1
    $7AB0: 8D 61 7A   STA $7a61     
    $7AB3: 60         RTS           
sub_7AB4:
    $7AB4: 48         PHA           
    $7AB5: A9 01      LDA #$01      
    $7AB7: 8D 61 7A   STA $7a61     
    $7ABA: 68         PLA           
    $7ABB: AA         TAX           
    $7ABC: BD A5 18   LDA $18a5,x   
    $7ABF: 8D CB 7A   STA $7acb     
    $7AC2: BD A7 18   LDA $18a7,x   
    $7AC5: 8D CC 7A   STA $7acc     
    $7AC8: A0 05      LDY #$05      
L_7ACA:
    $7ACA: B9 A9 18   LDA $18a9,y   
    $7ACD: 99 B5 18   STA $18b5,y   
    $7AD0: 88         DEY           
    $7AD1: 10 F7      BPL $7aca        ; → L_7ACA
    $7AD3: BD A1 18   LDA $18a1,x   
    $7AD6: 8D 09 7A   STA $7a09     
    $7AD9: BD A3 18   LDA $18a3,x   
    $7ADC: 8D 73 7D   STA $7d73     
    $7ADF: 20 88 7A   JSR $7a88        ; → sub_7A88
L_7AE2:
    $7AE2: A2 17      LDX #$17      
L_7AE4:
    $7AE4: A9 01      LDA #$01      
    $7AE6: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $7AE9: A9 00      LDA #$00      
    $7AEB: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $7AEE: CA         DEX           
    $7AEF: 10 F3      BPL $7ae4        ; → L_7AE4
    $7AF1: A9 0F      LDA #$0f      
    $7AF3: 8D 18 D4   STA $d418      ;VOL
    $7AF6: A9 00      LDA #$00      
    $7AF8: 8D 17 D4   STA $d417      ;RES_FILT
    $7AFB: 60         RTS           
L_7AFC:
    $7AFC: A9 02      LDA #$02      
    $7AFE: 8D 61 7A   STA $7a61     
    $7B01: 60         RTS           
L_7B02:
    $7B02: AD 61 7A   LDA $7a61     
    $7B05: C9 02      CMP #$02      
    $7B07: F0 04      BEQ $7b0d        ; → L_7B0D
    $7B09: C9 01      CMP #$01      
    $7B0B: D0 04      BNE $7b11        ; → L_7B11
L_7B0D:
    $7B0D: 60         RTS           
; ----- data gap $7B0E-$7B10 (3 bytes) -----

L_7B11:
    $7B11: EE 3E 7A   INC $7a3e     
    $7B14: EE 3F 7A   INC $7a3f     
    $7B17: EE 40 7A   INC $7a40     
    $7B1A: A2 02      LDX #$02      
    $7B1C: CE 60 7A   DEC $7a60     
    $7B1F: 10 06      BPL $7b27        ; → L_7B27
    $7B21: AD 09 7A   LDA $7a09     
    $7B24: 8D 60 7A   STA $7a60     
L_7B27:
    $7B27: EA         NOP           
    $7B28: EA         NOP           
    $7B29: EA         NOP           
    $7B2A: 86 77      STX $77       
    $7B2C: BD 0A 7A   LDA $7a0a,x   
    $7B2F: 8D 45 7A   STA $7a45     
    $7B32: A8         TAY           
    $7B33: AD 60 7A   LDA $7a60     
    $7B36: CD 09 7A   CMP $7a09     
    $7B39: D0 14      BNE $7b4f        ; → L_7B4F
    $7B3B: BD B5 18   LDA $18b5,x   
    $7B3E: 8D 56 7B   STA $7b56     
    $7B41: BD B8 18   LDA $18b8,x   
    $7B44: 8D 57 7B   STA $7b57     
    $7B47: DE 13 7A   DEC $7a13,x   
    $7B4A: 30 06      BMI $7b52        ; → L_7B52
    $7B4C: 4C 34 7D   JMP $7d34        ; → L_7D34
L_7B4F:
    $7B4F: 4C 63 7D   JMP $7d63        ; → L_7D63
L_7B52:
    $7B52: BC 0D 7A   LDY $7a0d,x   
    $7B55: B9 20 1A   LDA $1a20,y   
    $7B58: C9 FE      CMP #$fe      
    $7B5A: F0 12      BEQ $7b6e        ; → L_7B6E
    $7B5C: C9 FF      CMP #$ff      
    $7B5E: D0 16      BNE $7b76        ; → L_7B76
    $7B60: A9 00      LDA #$00      
    $7B62: 9D 13 7A   STA $7a13,x   
    $7B65: 9D 0D 7A   STA $7a0d,x   
    $7B68: 9D 10 7A   STA $7a10,x   
    $7B6B: 4C 52 7B   JMP $7b52        ; → L_7B52
L_7B6E:
    $7B6E: A9 02      LDA #$02      
    $7B70: 8D 61 7A   STA $7a61     
    $7B73: 4C E2 7A   JMP $7ae2        ; → L_7AE2
L_7B76:
    $7B76: 8D 54 7A   STA $7a54     
    $7B79: C9 80      CMP #$80      
    $7B7B: 90 0B      BCC $7b88        ; → L_7B88
    $7B7D: 29 1F      AND #$1f      
    $7B7F: 9D 41 7A   STA $7a41,x   
    $7B82: FE 0D 7A   INC $7a0d,x   
    $7B85: 4C 52 7B   JMP $7b52        ; → L_7B52
L_7B88:
    $7B88: AD 54 7A   LDA $7a54     
    $7B8B: C9 60      CMP #$60      
    $7B8D: 90 0B      BCC $7b9a        ; → L_7B9A
    $7B8F: 29 0F      AND #$0f      
    $7B91: 9D 84 7A   STA $7a84,x   
    $7B94: FE 0D 7A   INC $7a0d,x   
    $7B97: 4C 52 7B   JMP $7b52        ; → L_7B52
L_7B9A:
    $7B9A: AD 54 7A   LDA $7a54     
    $7B9D: C9 40      CMP #$40      
    $7B9F: 90 0B      BCC $7bac        ; → L_7BAC
    $7BA1: 29 3F      AND #$3f      
    $7BA3: 9D 63 7A   STA $7a63,x   
    $7BA6: FE 0D 7A   INC $7a0d,x   
    $7BA9: 4C 52 7B   JMP $7b52        ; → L_7B52
L_7BAC:
    $7BAC: AD 54 7A   LDA $7a54     
    $7BAF: 0A         ASL a         
    $7BB0: A8         TAY           
    $7BB1: B9 A0 1B   LDA $1ba0,y   
    $7BB4: 85 75      STA $75       
    $7BB6: B9 A1 1B   LDA $1ba1,y   
    $7BB9: 85 76      STA $76       
    $7BBB: A9 00      LDA #$00      
    $7BBD: 9D 2E 7A   STA $7a2e,x   
    $7BC0: 9D 31 7A   STA $7a31,x   
    $7BC3: BC 10 7A   LDY $7a10,x   
    $7BC6: 9D 3E 7A   STA $7a3e,x   
    $7BC9: B1 75      LDA ($75),y   
    $7BCB: 85 73      STA $73       
L_7BCD:
    $7BCD: 29 F0      AND #$f0      
    $7BCF: C9 F0      CMP #$f0      
    $7BD1: D0 1F      BNE $7bf2        ; → L_7BF2
    $7BD3: A5 73      LDA $73       
    $7BD5: 29 01      AND #$01      
    $7BD7: D0 10      BNE $7be9        ; → L_7BE9
    $7BD9: A9 01      LDA #$01      
    $7BDB: 9D 72 7A   STA $7a72,x   
    $7BDE: FE 10 7A   INC $7a10,x   
    $7BE1: C8         INY           
    $7BE2: B1 75      LDA ($75),y   
    $7BE4: 85 73      STA $73       
    $7BE6: 4C 8B 7C   JMP $7c8b        ; → L_7C8B
L_7BE9:
    $7BE9: 20 27 7D   JSR $7d27        ; → sub_7D27
    $7BEC: 8D 17 D4   STA $d417      ;RES_FILT
    $7BEF: 20 27 7D   JSR $7d27        ; → sub_7D27
L_7BF2:
    $7BF2: A9 00      LDA #$00      
    $7BF4: 9D 72 7A   STA $7a72,x   
    $7BF7: A5 73      LDA $73       
    $7BF9: 29 F0      AND #$f0      
    $7BFB: C9 E0      CMP #$e0      
    $7BFD: D0 24      BNE $7c23        ; → L_7C23
    $7BFF: A9 01      LDA #$01      
    $7C01: 9D 2E 7A   STA $7a2e,x   
    $7C04: FE 10 7A   INC $7a10,x   
    $7C07: C8         INY           
    $7C08: B1 75      LDA ($75),y   
    $7C0A: 9D 79 7A   STA $7a79,x   
    $7C0D: FE 10 7A   INC $7a10,x   
    $7C10: FE 10 7A   INC $7a10,x   
    $7C13: C8         INY           
    $7C14: C8         INY           
    $7C15: B1 75      LDA ($75),y   
    $7C17: 18         CLC           
    $7C18: 7D 41 7A   ADC $7a41,x   
    $7C1B: 9D 76 7A   STA $7a76,x   
    $7C1E: 88         DEY           
    $7C1F: B1 75      LDA ($75),y   
    $7C21: 85 73      STA $73       
L_7C23:
    $7C23: A5 73      LDA $73       
    $7C25: 29 E0      AND #$e0      
    $7C27: C9 C0      CMP #$c0      
    $7C29: D0 0E      BNE $7c39        ; → L_7C39
    $7C2B: A5 73      LDA $73       
    $7C2D: 29 1F      AND #$1f      
    $7C2F: 18         CLC           
    $7C30: 7D 84 7A   ADC $7a84,x   
    $7C33: 9D 22 7A   STA $7a22,x   
    $7C36: 20 27 7D   JSR $7d27        ; → sub_7D27
L_7C39:
    $7C39: A5 73      LDA $73       
    $7C3B: 29 F0      AND #$f0      
    $7C3D: C9 70      CMP #$70      
    $7C3F: D0 1C      BNE $7c5d        ; → L_7C5D
    $7C41: A5 73      LDA $73       
    $7C43: 29 0F      AND #$0f      
    $7C45: AA         TAX           
    $7C46: BD 61 19   LDA $1961,x   
    $7C49: 8D A8 7D   STA $7da8     
    $7C4C: 8D B4 7D   STA $7db4     
    $7C4F: BD 68 19   LDA $1968,x   
    $7C52: 8D A9 7D   STA $7da9     
    $7C55: 8D B5 7D   STA $7db5     
    $7C58: A6 77      LDX $77       
    $7C5A: 20 27 7D   JSR $7d27        ; → sub_7D27
L_7C5D:
    $7C5D: A5 73      LDA $73       
    $7C5F: 29 C0      AND #$c0      
    $7C61: C9 80      CMP #$80      
    $7C63: D0 26      BNE $7c8b        ; → L_7C8B
    $7C65: A5 73      LDA $73       
    $7C67: 29 3F      AND #$3f      
    $7C69: 38         SEC           
    $7C6A: E9 01      SBC #$01      
    $7C6C: 9D 16 7A   STA $7a16,x   
    $7C6F: 20 27 7D   JSR $7d27        ; → sub_7D27
    $7C72: 29 C0      AND #$c0      
    $7C74: C9 80      CMP #$80      
    $7C76: D0 0E      BNE $7c86        ; → L_7C86
    $7C78: A5 73      LDA $73       
    $7C7A: 29 3F      AND #$3f      
    $7C7C: 18         CLC           
    $7C7D: 7D 16 7A   ADC $7a16,x   
    $7C80: 9D 16 7A   STA $7a16,x   
    $7C83: 20 27 7D   JSR $7d27        ; → sub_7D27
L_7C86:
    $7C86: A5 73      LDA $73       
    $7C88: 4C CD 7B   JMP $7bcd        ; → L_7BCD
L_7C8B:
    $7C8B: BD 16 7A   LDA $7a16,x   
    $7C8E: 9D 13 7A   STA $7a13,x   
    $7C91: A5 73      LDA $73       
    $7C93: 18         CLC           
    $7C94: 7D 41 7A   ADC $7a41,x   
    $7C97: 9D 1F 7A   STA $7a1f,x   
    $7C9A: A8         TAY           
    $7C9B: B9 E3 17   LDA $17e3,y   
    $7C9E: 9D 7E 7A   STA $7a7e,x   
    $7CA1: 48         PHA           
    $7CA2: 9D 2B 7A   STA $7a2b,x   
    $7CA5: B9 42 18   LDA $1842,y   
    $7CA8: 9D 81 7A   STA $7a81,x   
    $7CAB: 9D 25 7A   STA $7a25,x   
    $7CAE: 9D 28 7A   STA $7a28,x   
    $7CB1: AC 45 7A   LDY $7a45     
    $7CB4: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $7CB7: 68         PLA           
    $7CB8: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $7CBB: BD 72 7A   LDA $7a72,x   
    $7CBE: D0 46      BNE $7d06        ; → L_7D06
    $7CC0: BD 22 7A   LDA $7a22,x   
    $7CC3: 0A         ASL a         
    $7CC4: 0A         ASL a         
    $7CC5: 0A         ASL a         
    $7CC6: AA         TAX           
    $7CC7: 8E 44 7A   STX $7a44     
    $7CCA: BD AE 19   LDA $19ae,x   
    $7CCD: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $7CD0: BD AF 19   LDA $19af,x   
    $7CD3: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $7CD6: BD B0 19   LDA $19b0,x   
    $7CD9: 48         PHA           
    $7CDA: BD AC 19   LDA $19ac,x   
    $7CDD: 48         PHA           
    $7CDE: BD AD 19   LDA $19ad,x   
    $7CE1: A6 77      LDX $77       
    $7CE3: 9D 19 7A   STA $7a19,x   
    $7CE6: 9D 66 7A   STA $7a66,x   
    $7CE9: A9 00      LDA #$00      
    $7CEB: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $7CEE: 9D 34 7A   STA $7a34,x   
    $7CF1: 68         PLA           
    $7CF2: 9D 3A 7A   STA $7a3a,x   
    $7CF5: 29 0F      AND #$0f      
    $7CF7: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $7CFA: 9D 37 7A   STA $7a37,x   
    $7CFD: A9 01      LDA #$01      
    $7CFF: 9D 5C 7A   STA $7a5c,x   
    $7D02: 68         PLA           
    $7D03: 9D 59 7A   STA $7a59,x   
L_7D06:
    $7D06: FE 10 7A   INC $7a10,x   
    $7D09: BC 10 7A   LDY $7a10,x   
    $7D0C: B1 75      LDA ($75),y   
    $7D0E: C9 FF      CMP #$ff      
    $7D10: D0 12      BNE $7d24        ; → L_7D24
L_7D12:
    $7D12: A9 00      LDA #$00      
    $7D14: 9D 10 7A   STA $7a10,x   
    $7D17: BD 63 7A   LDA $7a63,x   
    $7D1A: F0 05      BEQ $7d21        ; → L_7D21
    $7D1C: DE 63 7A   DEC $7a63,x   
    $7D1F: 10 03      BPL $7d24        ; → L_7D24
L_7D21:
    $7D21: FE 0D 7A   INC $7a0d,x   
L_7D24:
    $7D24: 4C B3 81   JMP $81b3        ; → L_81B3
sub_7D27:
    $7D27: FE 10 7A   INC $7a10,x   
    $7D2A: C8         INY           
    $7D2B: B1 75      LDA ($75),y   
    $7D2D: C9 FF      CMP #$ff      
    $7D2F: F0 E1      BEQ $7d12        ; → L_7D12
    $7D31: 85 73      STA $73       
    $7D33: 60         RTS           
L_7D34:
    $7D34: BD 13 7A   LDA $7a13,x   
    $7D37: F0 22      BEQ $7d5b        ; → L_7D5B
    $7D39: BD 22 7A   LDA $7a22,x   
    $7D3C: 0A         ASL a         
    $7D3D: 0A         ASL a         
    $7D3E: 0A         ASL a         
    $7D3F: A8         TAY           
    $7D40: B9 B0 19   LDA $19b0,y   
    $7D43: 29 F0      AND #$f0      
    $7D45: 4A         LSR a         
    $7D46: 4A         LSR a         
    $7D47: 4A         LSR a         
    $7D48: 8D 53 7D   STA $7d53     
    $7D4B: BD 16 7A   LDA $7a16,x   
    $7D4E: 38         SEC           
    $7D4F: FD 13 7A   SBC $7a13,x   
    $7D52: C9 00      CMP #$00      
    $7D54: B0 05      BCS $7d5b        ; → L_7D5B
    $7D56: BD 19 7A   LDA $7a19,x   
    $7D59: D0 05      BNE $7d60        ; → L_7D60
L_7D5B:
    $7D5B: BD 19 7A   LDA $7a19,x   
    $7D5E: 29 FE      AND #$fe      
L_7D60:
    $7D60: 9D 66 7A   STA $7a66,x   
L_7D63:
    $7D63: BD 3A 7A   LDA $7a3a,x   
    $7D66: 29 10      AND #$10      
    $7D68: F0 0F      BEQ $7d79        ; → L_7D79
    $7D6A: BD 13 7A   LDA $7a13,x   
    $7D6D: D0 0A      BNE $7d79        ; → L_7D79
    $7D6F: AD 60 7A   LDA $7a60     
    $7D72: C9 01      CMP #$01      
    $7D74: D0 03      BNE $7d79        ; → L_7D79
    $7D76: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_7D79:
    $7D79: BD 22 7A   LDA $7a22,x   
    $7D7C: 0A         ASL a         
    $7D7D: 0A         ASL a         
    $7D7E: 0A         ASL a         
    $7D7F: A8         TAY           
    $7D80: B9 B1 19   LDA $19b1,y   
    $7D83: 85 78      STA $78       
    $7D85: B9 B2 19   LDA $19b2,y   
    $7D88: 85 71      STA $71       
    $7D8A: BD 1F 7A   LDA $7a1f,x   
    $7D8D: 9D 1C 7A   STA $7a1c,x   
    $7D90: B9 B3 19   LDA $19b3,y   
    $7D93: 85 72      STA $72       
    $7D95: 29 10      AND #$10      
    $7D97: F0 03      BEQ $7d9c        ; → L_7D9C
    $7D99: 4C AC 7E   JMP $7eac        ; → L_7EAC
L_7D9C:
    $7D9C: A5 72      LDA $72       
    $7D9E: 29 04      AND #$04      
    $7DA0: F0 28      BEQ $7dca        ; → L_7DCA
    $7DA2: DE 50 7A   DEC $7a50,x   
    $7DA5: 10 06      BPL $7dad        ; → L_7DAD
    $7DA7: AD 73 19   LDA $1973     
    $7DAA: 9D 50 7A   STA $7a50,x   
L_7DAD:
    $7DAD: A6 77      LDX $77       
    $7DAF: BC 50 7A   LDY $7a50,x   
    $7DB2: C8         INY           
    $7DB3: B9 73 19   LDA $1973,y   
    $7DB6: 18         CLC           
    $7DB7: 7D 1F 7A   ADC $7a1f,x   
    $7DBA: 9D 1C 7A   STA $7a1c,x   
    $7DBD: A8         TAY           
    $7DBE: B9 E3 17   LDA $17e3,y   
    $7DC1: 9D 7E 7A   STA $7a7e,x   
    $7DC4: B9 42 18   LDA $1842,y   
    $7DC7: 9D 81 7A   STA $7a81,x   
L_7DCA:
    $7DCA: A5 78      LDA $78       
    $7DCC: F0 54      BEQ $7e22        ; → L_7E22
    $7DCE: BD 31 7A   LDA $7a31,x   
    $7DD1: D0 4F      BNE $7e22        ; → L_7E22
    $7DD3: BC 22 7A   LDY $7a22,x   
    $7DD6: BE 14 1A   LDX $1a14,y   
    $7DD9: 8E 63 7E   STX $7e63     
    $7DDC: A5 78      LDA $78       
    $7DDE: 29 0F      AND #$0f      
    $7DE0: 8D 46 7A   STA $7a46     
    $7DE3: A5 78      LDA $78       
    $7DE5: 29 70      AND #$70      
    $7DE7: 4A         LSR a         
    $7DE8: 4A         LSR a         
    $7DE9: 4A         LSR a         
    $7DEA: 4A         LSR a         
    $7DEB: A6 77      LDX $77       
    $7DED: 9D 47 7A   STA $7a47,x   
    $7DF0: A0 BC      LDY #$bc      
    $7DF2: A5 78      LDA $78       
    $7DF4: 10 02      BPL $7df8        ; → L_7DF8
    $7DF6: A0 7D      LDY #$7d      
L_7DF8:
    $7DF8: 8C 0E 7E   STY $7e0e     
    $7DFB: BC 1C 7A   LDY $7a1c,x   
    $7DFE: B9 E4 17   LDA $17e4,y   
    $7E01: 38         SEC           
    $7E02: F9 E3 17   SBC $17e3,y   
    $7E05: 8D 6C 7A   STA $7a6c     
    $7E08: B9 43 18   LDA $1843,y   
    $7E0B: F9 42 18   SBC $1842,y   
    $7E0E: BC 3E 7A   LDY $7a3e,x   
    $7E11: 8D 6B 7A   STA $7a6b     
L_7E14:
    $7E14: CE 46 7A   DEC $7a46     
    $7E17: 30 0C      BMI $7e25        ; → L_7E25
    $7E19: 4E 6B 7A   LSR $7a6b     
    $7E1C: 6E 6C 7A   ROR $7a6c     
    $7E1F: 4C 14 7E   JMP $7e14        ; → L_7E14
L_7E22:
    $7E22: 4C AC 7E   JMP $7eac        ; → L_7EAC
L_7E25:
    $7E25: BD 4A 7A   LDA $7a4a,x   
    $7E28: 10 0A      BPL $7e34        ; → L_7E34
    $7E2A: DE 4D 7A   DEC $7a4d,x   
    $7E2D: D0 19      BNE $7e48        ; → L_7E48
    $7E2F: FE 4A 7A   INC $7a4a,x   
    $7E32: 10 14      BPL $7e48        ; → L_7E48
L_7E34:
    $7E34: FE 4D 7A   INC $7a4d,x   
    $7E37: BD 47 7A   LDA $7a47,x   
    $7E3A: DD 4D 7A   CMP $7a4d,x   
    $7E3D: B0 09      BCS $7e48        ; → L_7E48
    $7E3F: 9D 4D 7A   STA $7a4d,x   
    $7E42: DE 4A 7A   DEC $7a4a,x   
    $7E45: DE 4D 7A   DEC $7a4d,x   
L_7E48:
    $7E48: BC 1C 7A   LDY $7a1c,x   
    $7E4B: B9 E3 17   LDA $17e3,y   
    $7E4E: 8D 69 7A   STA $7a69     
    $7E51: B9 42 18   LDA $1842,y   
    $7E54: 8D 6A 7A   STA $7a6a     
    $7E57: BD 47 7A   LDA $7a47,x   
    $7E5A: 4A         LSR a         
    $7E5B: A8         TAY           
L_7E5C:
    $7E5C: 88         DEY           
    $7E5D: 30 1D      BMI $7e7c        ; → L_7E7C
    $7E5F: BD 3E 7A   LDA $7a3e,x   
    $7E62: C9 00      CMP #$00      
    $7E64: 90 32      BCC $7e98        ; → L_7E98
    $7E66: AD 69 7A   LDA $7a69     
    $7E69: 38         SEC           
    $7E6A: ED 6C 7A   SBC $7a6c     
    $7E6D: 8D 69 7A   STA $7a69     
    $7E70: AD 6A 7A   LDA $7a6a     
    $7E73: ED 6B 7A   SBC $7a6b     
    $7E76: 8D 6A 7A   STA $7a6a     
    $7E79: 4C 5C 7E   JMP $7e5c        ; → L_7E5C
L_7E7C:
    $7E7C: BC 4D 7A   LDY $7a4d,x   
L_7E7F:
    $7E7F: 88         DEY           
    $7E80: 30 16      BMI $7e98        ; → L_7E98
    $7E82: AD 69 7A   LDA $7a69     
    $7E85: 18         CLC           
    $7E86: 6D 6C 7A   ADC $7a6c     
    $7E89: 8D 69 7A   STA $7a69     
    $7E8C: AD 6A 7A   LDA $7a6a     
    $7E8F: 6D 6B 7A   ADC $7a6b     
    $7E92: 8D 6A 7A   STA $7a6a     
    $7E95: 4C 7F 7E   JMP $7e7f        ; → L_7E7F
L_7E98:
    $7E98: A6 77      LDX $77       
    $7E9A: AD 69 7A   LDA $7a69     
    $7E9D: 9D 7E 7A   STA $7a7e,x   
    $7EA0: 9D 2B 7A   STA $7a2b,x   
    $7EA3: AD 6A 7A   LDA $7a6a     
    $7EA6: 9D 81 7A   STA $7a81,x   
    $7EA9: 9D 25 7A   STA $7a25,x   
L_7EAC:
    $7EAC: A6 77      LDX $77       
    $7EAE: BD 2E 7A   LDA $7a2e,x   
    $7EB1: D0 06      BNE $7eb9        ; → L_7EB9
L_7EB3:
    $7EB3: 4C A3 7F   JMP $7fa3        ; → L_7FA3
L_7EB6:
    $7EB6: 4C 82 7F   JMP $7f82        ; → L_7F82
L_7EB9:
    $7EB9: BD 79 7A   LDA $7a79,x   
    $7EBC: 4A         LSR a         
    $7EBD: 4A         LSR a         
    $7EBE: 4A         LSR a         
    $7EBF: 4A         LSR a         
    $7EC0: 8D DF 7E   STA $7edf     
    $7EC3: 8D 2E 7F   STA $7f2e     
    $7EC6: BD 79 7A   LDA $7a79,x   
    $7EC9: 29 0F      AND #$0f      
    $7ECB: 38         SEC           
    $7ECC: E9 01      SBC #$01      
    $7ECE: 18         CLC           
    $7ECF: 7D 13 7A   ADC $7a13,x   
    $7ED2: DD 16 7A   CMP $7a16,x   
    $7ED5: B0 DC      BCS $7eb3        ; → L_7EB3
    $7ED7: 48         PHA           
    $7ED8: A9 01      LDA #$01      
    $7EDA: 9D 31 7A   STA $7a31,x   
    $7EDD: 68         PLA           
    $7EDE: 69 02      ADC #$02      
    $7EE0: DD 16 7A   CMP $7a16,x   
    $7EE3: 90 D1      BCC $7eb6        ; → L_7EB6
    $7EE5: BC 1F 7A   LDY $7a1f,x   
    $7EE8: BD 76 7A   LDA $7a76,x   
    $7EEB: AA         TAX           
    $7EEC: 38         SEC           
    $7EED: B9 E3 17   LDA $17e3,y   
    $7EF0: FD E3 17   SBC $17e3,x   
    $7EF3: 8D 6A 7F   STA $7f6a     
    $7EF6: B9 42 18   LDA $1842,y   
    $7EF9: FD 42 18   SBC $1842,x   
    $7EFC: 8D 75 7F   STA $7f75     
    $7EFF: A2 38      LDX #$38      
    $7F01: A0 E9      LDY #$e9      
    $7F03: B0 19      BCS $7f1e        ; → L_7F1E
    $7F05: A2 18      LDX #$18      
    $7F07: A0 69      LDY #$69      
    $7F09: 49 FF      EOR #$ff      
    $7F0B: 8D 75 7F   STA $7f75     
    $7F0E: AD 6A 7F   LDA $7f6a     
    $7F11: 49 FF      EOR #$ff      
    $7F13: 8D 6A 7F   STA $7f6a     
    $7F16: EE 6A 7F   INC $7f6a     
    $7F19: D0 03      BNE $7f1e        ; → L_7F1E
    $7F1B: EE 75 7F   INC $7f75     
L_7F1E:
    $7F1E: 8C 69 7F   STY $7f69     
    $7F21: 8C 74 7F   STY $7f74     
    $7F24: 8E 68 7F   STX $7f68     
    $7F27: AC 09 7A   LDY $7a09     
    $7F2A: A9 00      LDA #$00      
    $7F2C: 18         CLC           
L_7F2D:
    $7F2D: 69 02      ADC #$02      
    $7F2F: 88         DEY           
    $7F30: 10 FB      BPL $7f2d        ; → L_7F2D
    $7F32: 8D 7C 7A   STA $7a7c     
    $7F35: 18         CLC           
    $7F36: A2 10      LDX #$10      
    $7F38: A9 00      LDA #$00      
L_7F3A:
    $7F3A: 2E 6A 7F   ROL $7f6a     
    $7F3D: 2E 75 7F   ROL $7f75     
    $7F40: 2A         ROL a         
    $7F41: B0 05      BCS $7f48        ; → L_7F48
    $7F43: CD 7C 7A   CMP $7a7c     
    $7F46: 90 04      BCC $7f4c        ; → L_7F4C
L_7F48:
    $7F48: ED 7C 7A   SBC $7a7c     
    $7F4B: 38         SEC           
L_7F4C:
    $7F4C: CA         DEX           
    $7F4D: D0 EB      BNE $7f3a        ; → L_7F3A
    $7F4F: 2E 6A 7F   ROL $7f6a     
    $7F52: 2E 75 7F   ROL $7f75     
    $7F55: 0A         ASL a         
    $7F56: CD 7C 7A   CMP $7a7c     
    $7F59: 90 08      BCC $7f63        ; → L_7F63
    $7F5B: EE 6A 7F   INC $7f6a     
    $7F5E: D0 03      BNE $7f63        ; → L_7F63
    $7F60: EE 75 7F   INC $7f75     
L_7F63:
    $7F63: A6 77      LDX $77       
    $7F65: BD 2B 7A   LDA $7a2b,x   
    $7F68: 18         CLC           
    $7F69: 69 16      ADC #$16      
    $7F6B: 9D 2B 7A   STA $7a2b,x   
    $7F6E: 9D 7E 7A   STA $7a7e,x   
    $7F71: BD 25 7A   LDA $7a25,x   
    $7F74: 69 00      ADC #$00      
    $7F76: 9D 25 7A   STA $7a25,x   
    $7F79: 9D 81 7A   STA $7a81,x   
    $7F7C: 4C A3 7F   JMP $7fa3        ; → L_7FA3
L_7F7F:
    $7F7F: 4C 5A 80   JMP $805a        ; → L_805A
L_7F82:
    $7F82: BD 76 7A   LDA $7a76,x   
    $7F85: 9D 1F 7A   STA $7a1f,x   
    $7F88: A8         TAY           
    $7F89: B9 E3 17   LDA $17e3,y   
    $7F8C: 9D 2B 7A   STA $7a2b,x   
    $7F8F: 9D 7E 7A   STA $7a7e,x   
    $7F92: B9 42 18   LDA $1842,y   
    $7F95: 9D 25 7A   STA $7a25,x   
    $7F98: 9D 81 7A   STA $7a81,x   
    $7F9B: A9 00      LDA #$00      
    $7F9D: 9D 2E 7A   STA $7a2e,x   
    $7FA0: 9D 31 7A   STA $7a31,x   
L_7FA3:
    $7FA3: A5 71      LDA $71       
    $7FA5: F0 D8      BEQ $7f7f        ; → L_7F7F
    $7FA7: 29 07      AND #$07      
    $7FA9: 0A         ASL a         
    $7FAA: 0A         ASL a         
    $7FAB: 0A         ASL a         
    $7FAC: E9 07      SBC #$07      
    $7FAE: A8         TAY           
    $7FAF: B9 9C 19   LDA $199c,y   
    $7FB2: 48         PHA           
    $7FB3: 29 80      AND #$80      
    $7FB5: F0 02      BEQ $7fb9        ; → L_7FB9
    $7FB7: A9 01      LDA #$01      
L_7FB9:
    $7FB9: 8D 45 80   STA $8045     
    $7FBC: 68         PLA           
    $7FBD: 29 0F      AND #$0f      
    $7FBF: 8D 27 80   STA $8027     
    $7FC2: C8         INY           
    $7FC3: B9 9C 19   LDA $199c,y   
    $7FC6: 8D 41 80   STA $8041     
    $7FC9: C8         INY           
    $7FCA: B9 9C 19   LDA $199c,y   
    $7FCD: 29 7F      AND #$7f      
    $7FCF: DD 3E 7A   CMP $7a3e,x   
    $7FD2: 90 03      BCC $7fd7        ; → L_7FD7
    $7FD4: 4C F2 7F   JMP $7ff2        ; → L_7FF2
L_7FD7:
    $7FD7: C8         INY           
    $7FD8: C8         INY           
    $7FD9: B9 9C 19   LDA $199c,y   
    $7FDC: 29 7F      AND #$7f      
    $7FDE: DD 3E 7A   CMP $7a3e,x   
    $7FE1: 90 03      BCC $7fe6        ; → L_7FE6
    $7FE3: 4C F2 7F   JMP $7ff2        ; → L_7FF2
L_7FE6:
    $7FE6: C8         INY           
    $7FE7: C8         INY           
    $7FE8: B9 9C 19   LDA $199c,y   
    $7FEB: 29 7F      AND #$7f      
    $7FED: DD 3E 7A   CMP $7a3e,x   
    $7FF0: 90 16      BCC $8008        ; → L_8008
L_7FF2:
    $7FF2: B9 9C 19   LDA $199c,y   
    $7FF5: 29 80      AND #$80      
    $7FF7: F0 05      BEQ $7ffe        ; → L_7FFE
    $7FF9: A9 00      LDA #$00      
    $7FFB: 9D 5C 7A   STA $7a5c,x   
L_7FFE:
    $7FFE: C8         INY           
    $7FFF: B9 9C 19   LDA $199c,y   
    $8002: 8D 3D 7A   STA $7a3d     
    $8005: 4C 0F 80   JMP $800f        ; → L_800F
L_8008:
    $8008: A5 71      LDA $71       
    $800A: 29 F0      AND #$f0      
    $800C: 8D 3D 7A   STA $7a3d     
L_800F:
    $800F: BD 5C 7A   LDA $7a5c,x   
    $8012: D0 1A      BNE $802e        ; → L_802E
    $8014: BD 34 7A   LDA $7a34,x   
    $8017: 38         SEC           
    $8018: ED 3D 7A   SBC $7a3d     
    $801B: 9D 34 7A   STA $7a34,x   
    $801E: BD 37 7A   LDA $7a37,x   
    $8021: E9 00      SBC #$00      
    $8023: 9D 37 7A   STA $7a37,x   
    $8026: C9 05      CMP #$05      
    $8028: B0 30      BCS $805a        ; → L_805A
    $802A: A9 01      LDA #$01      
    $802C: D0 29      BNE $8057        ; → L_8057
L_802E:
    $802E: BD 34 7A   LDA $7a34,x   
    $8031: 18         CLC           
    $8032: 6D 3D 7A   ADC $7a3d     
    $8035: 9D 34 7A   STA $7a34,x   
    $8038: BD 37 7A   LDA $7a37,x   
    $803B: 69 00      ADC #$00      
    $803D: 9D 37 7A   STA $7a37,x   
    $8040: C9 0A      CMP #$0a      
    $8042: 90 16      BCC $805a        ; → L_805A
    $8044: A9 00      LDA #$00      
    $8046: F0 0D      BEQ $8055        ; → L_8055
    $8048: 9D 34 7A   STA $7a34,x   
    $804B: AD 27 80   LDA $8027     
    $804E: 9D 37 7A   STA $7a37,x   
    $8051: A9 01      LDA #$01      
    $8053: D0 02      BNE $8057        ; → L_8057
L_8055:
    $8055: A9 00      LDA #$00      
L_8057:
    $8057: 9D 5C 7A   STA $7a5c,x   
L_805A:
    $805A: A6 77      LDX $77       
    $805C: AC 45 7A   LDY $7a45     
    $805F: BD 34 7A   LDA $7a34,x   
    $8062: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $8065: BD 37 7A   LDA $7a37,x   
    $8068: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $806B: A5 72      LDA $72       
    $806D: 29 01      AND #$01      
    $806F: F0 5A      BEQ $80cb        ; → L_80CB
    $8071: A6 77      LDX $77       
    $8073: 8E 62 7A   STX $7a62     
    $8076: BD 59 7A   LDA $7a59,x   
    $8079: 29 03      AND #$03      
    $807B: 0A         ASL a         
    $807C: AA         TAX           
    $807D: BD 8B 19   LDA $198b,x   
    $8080: 8D 8A 80   STA $808a     
    $8083: BD 8C 19   LDA $198c,x   
    $8086: 8D 8E 80   STA $808e     
    $8089: A9 8D      LDA #$8d      
    $808B: 85 74      STA $74       
    $808D: A9 19      LDA #$19      
    $808F: 85 75      STA $75       
    $8091: A0 05      LDY #$05      
    $8093: B1 74      LDA ($74),y   
    $8095: 8D 18 D4   STA $d418      ;VOL
    $8098: A6 77      LDX $77       
    $809A: BD 3E 7A   LDA $7a3e,x   
    $809D: A0 09      LDY #$09      
    $809F: D1 74      CMP ($74),y   
    $80A1: 90 07      BCC $80aa        ; → L_80AA
    $80A3: A0 04      LDY #$04      
    $80A5: B1 74      LDA ($74),y   
    $80A7: 4C D4 80   JMP $80d4        ; → L_80D4
L_80AA:
    $80AA: 88         DEY           
    $80AB: D1 74      CMP ($74),y   
    $80AD: B0 0E      BCS $80bd        ; → L_80BD
    $80AF: C0 06      CPY #$06      
    $80B1: D0 F7      BNE $80aa        ; → L_80AA
    $80B3: A0 00      LDY #$00      
    $80B5: B1 74      LDA ($74),y   
    $80B7: 4C D4 80   JMP $80d4        ; → L_80D4
; ----- data gap $80BA-$80BC (3 bytes) -----

L_80BD:
    $80BD: 88         DEY           
    $80BE: 88         DEY           
    $80BF: 88         DEY           
    $80C0: 88         DEY           
    $80C1: 88         DEY           
    $80C2: BD 56 7A   LDA $7a56,x   
    $80C5: 18         CLC           
    $80C6: 71 74      ADC ($74),y   
    $80C8: 4C D4 80   JMP $80d4        ; → L_80D4
L_80CB:
    $80CB: A6 77      LDX $77       
    $80CD: EC 62 7A   CPX $7a62     
    $80D0: D0 08      BNE $80da        ; → L_80DA
    $80D2: A9 E0      LDA #$e0      
L_80D4:
    $80D4: 9D 56 7A   STA $7a56,x   
    $80D7: 8D 16 D4   STA $d416      ;FC_HI
L_80DA:
    $80DA: A6 77      LDX $77       
    $80DC: BD 59 7A   LDA $7a59,x   
    $80DF: 29 04      AND #$04      
    $80E1: F0 22      BEQ $8105        ; → L_8105
    $80E3: BD 16 7A   LDA $7a16,x   
    $80E6: 29 7F      AND #$7f      
    $80E8: C9 00      CMP #$00      
    $80EA: 90 19      BCC $8105        ; → L_8105
    $80EC: BD 13 7A   LDA $7a13,x   
    $80EF: C9 FF      CMP #$ff      
    $80F1: B0 12      BCS $8105        ; → L_8105
    $80F3: BD 3E 7A   LDA $7a3e,x   
    $80F6: 29 01      AND #$01      
    $80F8: F0 0B      BEQ $8105        ; → L_8105
    $80FA: BD 28 7A   LDA $7a28,x   
    $80FD: F0 06      BEQ $8105        ; → L_8105
    $80FF: DE 28 7A   DEC $7a28,x   
    $8102: 9D 81 7A   STA $7a81,x   
L_8105:
    $8105: A5 72      LDA $72       
    $8107: 29 10      AND #$10      
    $8109: F0 6A      BEQ $8175        ; → L_8175
    $810B: A5 78      LDA $78       
    $810D: 29 0F      AND #$0f      
    $810F: 0A         ASL a         
    $8110: 0A         ASL a         
    $8111: AA         TAX           
    $8112: BD DD 18   LDA $18dd,x   
    $8115: 8D 41 81   STA $8141     
    $8118: 8D 31 81   STA $8131     
    $811B: BD DE 18   LDA $18de,x   
    $811E: 8D 42 81   STA $8142     
    $8121: 8D 32 81   STA $8132     
    $8124: BD DF 18   LDA $18df,x   
    $8127: 8D 48 81   STA $8148     
    $812A: BD E0 18   LDA $18e0,x   
    $812D: 8D 49 81   STA $8149     
    $8130: AD 0E 19   LDA $190e     
    $8133: 8D 3C 81   STA $813c     
    $8136: A6 77      LDX $77       
    $8138: BD 3E 7A   LDA $7a3e,x   
    $813B: C9 0F      CMP #$0f      
    $813D: B0 33      BCS $8172        ; → L_8172
    $813F: A8         TAY           
    $8140: B9 0E 19   LDA $190e,y   
    $8143: 9D 66 7A   STA $7a66,x   
    $8146: 88         DEY           
    $8147: B9 1F 19   LDA $191f,y   
    $814A: 8D 55 7A   STA $7a55     
    $814D: AC 45 7A   LDY $7a45     
    $8150: A5 78      LDA $78       
    $8152: 29 10      AND #$10      
    $8154: F0 0C      BEQ $8162        ; → L_8162
    $8156: A6 77      LDX $77       
    $8158: BD 1C 7A   LDA $7a1c,x   
    $815B: 18         CLC           
    $815C: 6D 55 7A   ADC $7a55     
    $815F: 4C D1 81   JMP $81d1     
L_8162:
    $8162: A6 77      LDX $77       
    $8164: AD 55 7A   LDA $7a55     
    $8167: 18         CLC           
    $8168: 69 0D      ADC #$0d      
    $816A: 9D 81 7A   STA $7a81,x   
    $816D: A9 00      LDA #$00      
    $816F: 9D 7E 7A   STA $7a7e,x   
L_8172:
    $8172: 4C B3 81   JMP $81b3        ; → L_81B3
L_8175:
    $8175: A5 72      LDA $72       
    $8177: 29 80      AND #$80      
    $8179: F0 38      BEQ $81b3        ; → L_81B3
    $817B: A6 77      LDX $77       
    $817D: BD 3E 7A   LDA $7a3e,x   
    $8180: C9 02      CMP #$02      
    $8182: B0 14      BCS $8198        ; → L_8198
    $8184: A9 58      LDA #$58      
    $8186: 9D 81 7A   STA $7a81,x   
    $8189: A9 00      LDA #$00      
    $818B: 9D 7E 7A   STA $7a7e,x   
    $818E: A6 77      LDX $77       
    $8190: A9 81      LDA #$81      
    $8192: 9D 66 7A   STA $7a66,x   
    $8195: 4C B3 81   JMP $81b3        ; → L_81B3
L_8198:
    $8198: BD 3E 7A   LDA $7a3e,x   
    $819B: C9 04      CMP #$04      
    $819D: B0 14      BCS $81b3        ; → L_81B3
    $819F: BD 2B 7A   LDA $7a2b,x   
    $81A2: 9D 7E 7A   STA $7a7e,x   
    $81A5: BD 25 7A   LDA $7a25,x   
    $81A8: 9D 81 7A   STA $7a81,x   
    $81AB: BD 19 7A   LDA $7a19,x   
    $81AE: 29 FE      AND #$fe      
    $81B0: 9D 66 7A   STA $7a66,x   
L_81B3:
    $81B3: A6 77      LDX $77       
    $81B5: AC 45 7A   LDY $7a45     
    $81B8: BD 66 7A   LDA $7a66,x   
    $81BB: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $81BE: BD 7E 7A   LDA $7a7e,x   
    $81C1: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $81C4: BD 81 7A   LDA $7a81,x   
    $81C7: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $81CA: CA         DEX           
    $81CB: 30 03      BMI $81d0        ; → L_81D0
    $81CD: 4C 27 7B   JMP $7b27        ; → L_7B27
L_81D0:
    $81D0: 60         RTS           
