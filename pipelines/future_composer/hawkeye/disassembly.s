; ============================================================================
; Jeroen Tel — Hawkeye (1988 Thalamus)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: /home/jtr/sidfinity/hvsc84/MUSICIANS/T/Tel_Jeroen/Hawkeye.sid
; Load:   $7AE0   Init: $7AE0   Play: $7AE3
; PSID:   12 subtune(s), default subtune 1
; Binary: $7AE0-$9D1F (8768 bytes)
;
; Engine: Deenen MoN driver (1987), Tel variant — V3.x lineage.
; sidid: MoN/FutureComposer.
; FC V3.x sig at $7C1F; MoN/FC top sig at $7D9C.
;
; Known per-voice runtime variables (located by signature scan; see
; pipelines/future_composer/docs/hawkeye_sid_layout.md):
;   tabcount   @ $90C5   (3 bytes; sequence-pos counter)
;   begcount   @ $90C8   (3 bytes; section-start pos)
;   repeatsto  @ $9118   (3 bytes; pattern repeat stack)
;   voiceinc   @ $9139   (3 bytes; wave-table advance counter)
;
; Primary byte-exact reference: Cybernoid II disassembly (same author,
; same year, same driver) — /tmp/fc_research/c64_6581_sid_players/
; Tel_Jeroen_MON/Tel_Jeroen_Cybernoid2.asm (1817 ACME lines).
;
; Auto-traced 2125 reachable code bytes from init+play.
;
; ============================================================================

; ======= init: =======
init:
    $7AE0: 4C 8F 91   JMP $918f        ; → L_918F
; ======= play: =======
play:
    $7AE3: 4C 98 7B   JMP $7b98        ; → L_7B98
; ----- data gap $7AE6-$7B31 (76 bytes) -----

sub_7B32:
    $7B32: A9 00      LDA #$00      
    $7B34: A2 76      LDX #$76      
L_7B36:
    $7B36: 9D C5 90   STA $90c5,x   
    $7B39: CA         DEX           
    $7B3A: 10 FA      BPL $7b36        ; → L_7B36
L_7B3C:
    $7B3C: A2 02      LDX #$02      
L_7B3E:
    $7B3E: 9D C5 90   STA $90c5,x   
    $7B41: 9D C8 90   STA $90c8,x   
    $7B44: 9D CB 90   STA $90cb,x   
    $7B47: 9D D7 90   STA $90d7,x   
    $7B4A: CA         DEX           
    $7B4B: 10 F1      BPL $7b3e        ; → L_7B3E
    $7B4D: 8E F6 90   STX $90f6     
    $7B50: 8E F7 90   STX $90f7     
    $7B53: 8E F8 90   STX $90f8     
    $7B56: 8D 99 7B   STA $7b99     
    $7B59: 60         RTS           
sub_7B5A:
    $7B5A: A9 01      LDA #$01      
    $7B5C: 8D 99 7B   STA $7b99     
    $7B5F: 8D 09 7E   STA $7e09     
    $7B62: BD FC 83   LDA $83fc,x   
    $7B65: 8D 6B 7B   STA $7b6b     
    $7B68: A0 05      LDY #$05      
L_7B6A:
    $7B6A: B9 2C 7B   LDA $7b2c,y   
    $7B6D: 99 03 84   STA $8403,y   
    $7B70: 88         DEY           
    $7B71: 10 F7      BPL $7b6a        ; → L_7B6A
    $7B73: BD F5 83   LDA $83f5,x   
    $7B76: 8D FE 7A   STA $7afe     
    $7B79: BD FF 7A   LDA $7aff,x   
    $7B7C: 8D AE 7B   STA $7bae     
    $7B7F: 20 32 7B   JSR $7b32        ; → sub_7B32
    $7B82: A2 17      LDX #$17      
L_7B84:
    $7B84: A9 01      LDA #$01      
    $7B86: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $7B89: A9 00      LDA #$00      
    $7B8B: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $7B8E: CA         DEX           
    $7B8F: 10 F3      BPL $7b84        ; → L_7B84
    $7B91: 8E 18 D4   STX $d418      ;VOL
    $7B94: 8D 17 D4   STA $d417      ;RES_FILT
    $7B97: 60         RTS           
L_7B98:
    $7B98: A0 00      LDY #$00      
    $7B9A: F0 08      BEQ $7ba4        ; → L_7BA4
    $7B9C: 88         DEY           
    $7B9D: D0 04      BNE $7ba3        ; → L_7BA3
    $7B9F: 98         TYA           
    $7BA0: 4C 3C 7B   JMP $7b3c        ; → L_7B3C
L_7BA3:
    $7BA3: 60         RTS           
L_7BA4:
    $7BA4: EE F6 90   INC $90f6     
    $7BA7: EE F7 90   INC $90f7     
    $7BAA: EE F8 90   INC $90f8     
    $7BAD: A2 00      LDX #$00      
    $7BAF: CE 16 91   DEC $9116     
    $7BB2: 10 06      BPL $7bba        ; → L_7BBA
    $7BB4: AD FE 7A   LDA $7afe     
    $7BB7: 8D 16 91   STA $9116     
L_7BBA:
    $7BBA: 86 FF      STX $ff       
    $7BBC: BC 05 7B   LDY $7b05,x   
    $7BBF: 84 F6      STY $f6       
    $7BC1: AD 16 91   LDA $9116     
    $7BC4: CD FE 7A   CMP $7afe     
    $7BC7: D0 14      BNE $7bdd        ; → L_7BDD
    $7BC9: BD 03 84   LDA $8403,x   
    $7BCC: 8D E4 7B   STA $7be4     
    $7BCF: BD 06 84   LDA $8406,x   
    $7BD2: 8D E5 7B   STA $7be5     
    $7BD5: DE CB 90   DEC $90cb,x   
    $7BD8: 30 06      BMI $7be0        ; → L_7BE0
    $7BDA: 4C CA 7D   JMP $7dca        ; → L_7DCA
L_7BDD:
    $7BDD: 4C F9 7D   JMP $7df9        ; → L_7DF9
L_7BE0:
    $7BE0: BC C5 90   LDY $90c5,x   
    $7BE3: B9 C5 8F   LDA $8fc5,y   
    $7BE6: C9 FE      CMP #$fe      
    $7BE8: F0 12      BEQ $7bfc        ; → L_7BFC
    $7BEA: C9 FF      CMP #$ff      
    $7BEC: D0 1F      BNE $7c0d        ; → L_7C0D
    $7BEE: A9 00      LDA #$00      
    $7BF0: 9D CB 90   STA $90cb,x   
    $7BF3: 9D C5 90   STA $90c5,x   
    $7BF6: 9D C8 90   STA $90c8,x   
    $7BF9: 4C E0 7B   JMP $7be0        ; → L_7BE0
L_7BFC:
    $7BFC: A9 02      LDA #$02      
    $7BFE: 8D 99 7B   STA $7b99     
    $7C01: A9 00      LDA #$00      
    $7C03: 8D 04 D4   STA $d404      ;V1_CTRL
    $7C06: 8D 0B D4   STA $d40b      ;V2_CTRL
    $7C09: 8D 12 D4   STA $d412      ;V3_CTRL
    $7C0C: 60         RTS           
L_7C0D:
    $7C0D: 8D 0A 91   STA $910a     
    $7C10: C9 80      CMP #$80      
    $7C12: 90 0B      BCC $7c1f        ; → L_7C1F
    $7C14: 29 1F      AND #$1f      
    $7C16: 9D F9 90   STA $90f9,x   
    $7C19: FE C5 90   INC $90c5,x   
    $7C1C: 4C E0 7B   JMP $7be0        ; → L_7BE0
L_7C1F:
    $7C1F: AD 0A 91   LDA $910a     
    $7C22: C9 60      CMP #$60      
    $7C24: 90 0B      BCC $7c31        ; → L_7C31
    $7C26: 29 0F      AND #$0f      
    $7C28: 9D 39 91   STA $9139,x   
    $7C2B: FE C5 90   INC $90c5,x   
    $7C2E: 4C E0 7B   JMP $7be0        ; → L_7BE0
L_7C31:
    $7C31: AD 0A 91   LDA $910a     
    $7C34: C9 40      CMP #$40      
    $7C36: 90 0B      BCC $7c43        ; → L_7C43
    $7C38: 29 3F      AND #$3f      
    $7C3A: 9D 18 91   STA $9118,x   
    $7C3D: FE C5 90   INC $90c5,x   
    $7C40: 4C E0 7B   JMP $7be0        ; → L_7BE0
L_7C43:
    $7C43: AD 0A 91   LDA $910a     
    $7C46: 0A         ASL a         
    $7C47: A8         TAY           
    $7C48: B9 09 84   LDA $8409,y   
    $7C4B: 85 FD      STA $fd       
    $7C4D: B9 0A 84   LDA $840a,y   
    $7C50: 85 FE      STA $fe       
    $7C52: A9 00      LDA #$00      
    $7C54: 9D E6 90   STA $90e6,x   
    $7C57: 9D E9 90   STA $90e9,x   
    $7C5A: BC C8 90   LDY $90c8,x   
    $7C5D: 9D F6 90   STA $90f6,x   
    $7C60: B1 FD      LDA ($fd),y   
    $7C62: 85 FA      STA $fa       
L_7C64:
    $7C64: 29 F0      AND #$f0      
    $7C66: C9 F0      CMP #$f0      
    $7C68: D0 1F      BNE $7c89        ; → L_7C89
    $7C6A: A5 FA      LDA $fa       
    $7C6C: 29 01      AND #$01      
    $7C6E: D0 10      BNE $7c80        ; → L_7C80
    $7C70: A9 01      LDA #$01      
    $7C72: 9D 27 91   STA $9127,x   
    $7C75: FE C8 90   INC $90c8,x   
    $7C78: C8         INY           
    $7C79: B1 FD      LDA ($fd),y   
    $7C7B: 85 FA      STA $fa       
    $7C7D: 4C 22 7D   JMP $7d22        ; → L_7D22
L_7C80:
    $7C80: 20 BD 7D   JSR $7dbd        ; → sub_7DBD
    $7C83: 8D 17 D4   STA $d417      ;RES_FILT
    $7C86: 20 BD 7D   JSR $7dbd        ; → sub_7DBD
L_7C89:
    $7C89: A9 00      LDA #$00      
    $7C8B: 9D 27 91   STA $9127,x   
    $7C8E: A5 FA      LDA $fa       
    $7C90: 29 F0      AND #$f0      
    $7C92: C9 E0      CMP #$e0      
    $7C94: D0 24      BNE $7cba        ; → L_7CBA
    $7C96: A9 01      LDA #$01      
    $7C98: 9D E6 90   STA $90e6,x   
    $7C9B: FE C8 90   INC $90c8,x   
    $7C9E: C8         INY           
    $7C9F: B1 FD      LDA ($fd),y   
    $7CA1: 9D 2E 91   STA $912e,x   
    $7CA4: FE C8 90   INC $90c8,x   
    $7CA7: FE C8 90   INC $90c8,x   
    $7CAA: C8         INY           
    $7CAB: C8         INY           
    $7CAC: B1 FD      LDA ($fd),y   
    $7CAE: 18         CLC           
    $7CAF: 7D F9 90   ADC $90f9,x   
    $7CB2: 9D 2B 91   STA $912b,x   
    $7CB5: 88         DEY           
    $7CB6: B1 FD      LDA ($fd),y   
    $7CB8: 85 FA      STA $fa       
L_7CBA:
    $7CBA: A5 FA      LDA $fa       
    $7CBC: 29 E0      AND #$e0      
    $7CBE: C9 C0      CMP #$c0      
    $7CC0: D0 0E      BNE $7cd0        ; → L_7CD0
    $7CC2: A5 FA      LDA $fa       
    $7CC4: 29 1F      AND #$1f      
    $7CC6: 18         CLC           
    $7CC7: 7D 39 91   ADC $9139,x   
    $7CCA: 9D DA 90   STA $90da,x   
    $7CCD: 20 BD 7D   JSR $7dbd        ; → sub_7DBD
L_7CD0:
    $7CD0: A5 FA      LDA $fa       
    $7CD2: 29 F0      AND #$f0      
    $7CD4: C9 70      CMP #$70      
    $7CD6: D0 1C      BNE $7cf4        ; → L_7CF4
    $7CD8: A5 FA      LDA $fa       
    $7CDA: 29 0F      AND #$0f      
    $7CDC: AA         TAX           
    $7CDD: BD 80 85   LDA $8580,x   
    $7CE0: 8D 3E 7E   STA $7e3e     
    $7CE3: 8D 4A 7E   STA $7e4a     
    $7CE6: BD 89 85   LDA $8589,x   
    $7CE9: 8D 3F 7E   STA $7e3f     
    $7CEC: 8D 4B 7E   STA $7e4b     
    $7CEF: A6 FF      LDX $ff       
    $7CF1: 20 BD 7D   JSR $7dbd        ; → sub_7DBD
L_7CF4:
    $7CF4: A5 FA      LDA $fa       
    $7CF6: 29 C0      AND #$c0      
    $7CF8: C9 80      CMP #$80      
    $7CFA: D0 26      BNE $7d22        ; → L_7D22
    $7CFC: A5 FA      LDA $fa       
    $7CFE: 29 3F      AND #$3f      
    $7D00: 38         SEC           
    $7D01: E9 01      SBC #$01      
    $7D03: 9D CE 90   STA $90ce,x   
    $7D06: 20 BD 7D   JSR $7dbd        ; → sub_7DBD
    $7D09: 29 C0      AND #$c0      
    $7D0B: C9 80      CMP #$80      
    $7D0D: D0 0E      BNE $7d1d        ; → L_7D1D
    $7D0F: A5 FA      LDA $fa       
    $7D11: 29 3F      AND #$3f      
    $7D13: 18         CLC           
    $7D14: 7D CE 90   ADC $90ce,x   
    $7D17: 9D CE 90   STA $90ce,x   
    $7D1A: 20 BD 7D   JSR $7dbd        ; → sub_7DBD
L_7D1D:
    $7D1D: A5 FA      LDA $fa       
    $7D1F: 4C 64 7C   JMP $7c64        ; → L_7C64
L_7D22:
    $7D22: BD CE 90   LDA $90ce,x   
    $7D25: 9D CB 90   STA $90cb,x   
    $7D28: A5 FA      LDA $fa       
    $7D2A: 18         CLC           
    $7D2B: 7D F9 90   ADC $90f9,x   
    $7D2E: 9D D7 90   STA $90d7,x   
    $7D31: A8         TAY           
    $7D32: B9 37 83   LDA $8337,y   
    $7D35: 9D 33 91   STA $9133,x   
    $7D38: 48         PHA           
    $7D39: 9D E3 90   STA $90e3,x   
    $7D3C: B9 96 83   LDA $8396,y   
    $7D3F: 9D 36 91   STA $9136,x   
    $7D42: 9D DD 90   STA $90dd,x   
    $7D45: 9D E0 90   STA $90e0,x   
    $7D48: A4 F6      LDY $f6       
    $7D4A: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $7D4D: 68         PLA           
    $7D4E: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $7D51: BD 27 91   LDA $9127,x   
    $7D54: D0 46      BNE $7d9c        ; → L_7D9C
    $7D56: BD DA 90   LDA $90da,x   
    $7D59: 0A         ASL a         
    $7D5A: 0A         ASL a         
    $7D5B: 0A         ASL a         
    $7D5C: AA         TAX           
    $7D5D: 8E FC 90   STX $90fc     
    $7D60: BD 0E 86   LDA $860e,x   
    $7D63: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $7D66: BD 0F 86   LDA $860f,x   
    $7D69: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $7D6C: BD 10 86   LDA $8610,x   
    $7D6F: 48         PHA           
    $7D70: BD 0C 86   LDA $860c,x   
    $7D73: 48         PHA           
    $7D74: BD 0D 86   LDA $860d,x   
    $7D77: A6 FF      LDX $ff       
    $7D79: 9D D1 90   STA $90d1,x   
    $7D7C: 9D 1B 91   STA $911b,x   
    $7D7F: A9 00      LDA #$00      
    $7D81: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $7D84: 9D EC 90   STA $90ec,x   
    $7D87: 68         PLA           
    $7D88: 9D F2 90   STA $90f2,x   
    $7D8B: 29 0F      AND #$0f      
    $7D8D: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $7D90: 9D EF 90   STA $90ef,x   
    $7D93: A9 01      LDA #$01      
    $7D95: 9D 12 91   STA $9112,x   
    $7D98: 68         PLA           
    $7D99: 9D 0F 91   STA $910f,x   
L_7D9C:
    $7D9C: FE C8 90   INC $90c8,x   
    $7D9F: BC C8 90   LDY $90c8,x   
    $7DA2: B1 FD      LDA ($fd),y   
    $7DA4: C9 FF      CMP #$ff      
    $7DA6: D0 12      BNE $7dba        ; → L_7DBA
L_7DA8:
    $7DA8: A9 00      LDA #$00      
    $7DAA: 9D C8 90   STA $90c8,x   
    $7DAD: BD 18 91   LDA $9118,x   
    $7DB0: F0 05      BEQ $7db7        ; → L_7DB7
    $7DB2: DE 18 91   DEC $9118,x   
    $7DB5: 10 03      BPL $7dba        ; → L_7DBA
L_7DB7:
    $7DB7: FE C5 90   INC $90c5,x   
L_7DBA:
    $7DBA: 4C 0C 83   JMP $830c        ; → L_830C
sub_7DBD:
    $7DBD: FE C8 90   INC $90c8,x   
    $7DC0: C8         INY           
    $7DC1: B1 FD      LDA ($fd),y   
    $7DC3: C9 FF      CMP #$ff      
    $7DC5: F0 E1      BEQ $7da8        ; → L_7DA8
    $7DC7: 85 FA      STA $fa       
    $7DC9: 60         RTS           
L_7DCA:
    $7DCA: BD CB 90   LDA $90cb,x   
    $7DCD: F0 22      BEQ $7df1        ; → L_7DF1
    $7DCF: BD DA 90   LDA $90da,x   
    $7DD2: 0A         ASL a         
    $7DD3: 0A         ASL a         
    $7DD4: 0A         ASL a         
    $7DD5: A8         TAY           
    $7DD6: B9 10 86   LDA $8610,y   
    $7DD9: 29 F0      AND #$f0      
    $7DDB: 4A         LSR a         
    $7DDC: 4A         LSR a         
    $7DDD: 4A         LSR a         
    $7DDE: 8D E9 7D   STA $7de9     
    $7DE1: BD CE 90   LDA $90ce,x   
    $7DE4: 38         SEC           
    $7DE5: FD CB 90   SBC $90cb,x   
    $7DE8: C9 00      CMP #$00      
    $7DEA: B0 05      BCS $7df1        ; → L_7DF1
    $7DEC: BD D1 90   LDA $90d1,x   
    $7DEF: D0 05      BNE $7df6        ; → L_7DF6
L_7DF1:
    $7DF1: BD D1 90   LDA $90d1,x   
    $7DF4: 29 FE      AND #$fe      
L_7DF6:
    $7DF6: 9D 1B 91   STA $911b,x   
L_7DF9:
    $7DF9: BD F2 90   LDA $90f2,x   
    $7DFC: 29 10      AND #$10      
    $7DFE: F0 0F      BEQ $7e0f        ; → L_7E0F
    $7E00: BD CB 90   LDA $90cb,x   
    $7E03: D0 0A      BNE $7e0f        ; → L_7E0F
    $7E05: AD 16 91   LDA $9116     
    $7E08: C9 01      CMP #$01      
    $7E0A: D0 03      BNE $7e0f        ; → L_7E0F
    $7E0C: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_7E0F:
    $7E0F: BD DA 90   LDA $90da,x   
    $7E12: 0A         ASL a         
    $7E13: 0A         ASL a         
    $7E14: 0A         ASL a         
    $7E15: A8         TAY           
    $7E16: B9 11 86   LDA $8611,y   
    $7E19: 85 F7      STA $f7       
    $7E1B: B9 12 86   LDA $8612,y   
    $7E1E: 85 F8      STA $f8       
    $7E20: BD D7 90   LDA $90d7,x   
    $7E23: 9D D4 90   STA $90d4,x   
    $7E26: B9 13 86   LDA $8613,y   
    $7E29: 85 F9      STA $f9       
    $7E2B: 29 10      AND #$10      
    $7E2D: F0 03      BEQ $7e32        ; → L_7E32
    $7E2F: 4C 42 7F   JMP $7f42        ; → L_7F42
L_7E32:
    $7E32: A5 F9      LDA $f9       
    $7E34: 29 04      AND #$04      
    $7E36: F0 28      BEQ $7e60        ; → L_7E60
    $7E38: DE 07 91   DEC $9107,x   
    $7E3B: 10 06      BPL $7e43        ; → L_7E43
    $7E3D: AD 96 85   LDA $8596     
    $7E40: 9D 07 91   STA $9107,x   
L_7E43:
    $7E43: A6 FF      LDX $ff       
    $7E45: BC 07 91   LDY $9107,x   
    $7E48: C8         INY           
    $7E49: B9 96 85   LDA $8596,y   
    $7E4C: 18         CLC           
    $7E4D: 7D D7 90   ADC $90d7,x   
    $7E50: 9D D4 90   STA $90d4,x   
    $7E53: A8         TAY           
    $7E54: B9 37 83   LDA $8337,y   
    $7E57: 9D 33 91   STA $9133,x   
    $7E5A: B9 96 83   LDA $8396,y   
    $7E5D: 9D 36 91   STA $9136,x   
L_7E60:
    $7E60: A5 F7      LDA $f7       
    $7E62: F0 54      BEQ $7eb8        ; → L_7EB8
    $7E64: BD E9 90   LDA $90e9,x   
    $7E67: D0 4F      BNE $7eb8        ; → L_7EB8
    $7E69: BC DA 90   LDY $90da,x   
    $7E6C: BE 04 87   LDX $8704,y   
    $7E6F: 8E F9 7E   STX $7ef9     
    $7E72: A5 F7      LDA $f7       
    $7E74: 29 0F      AND #$0f      
    $7E76: 8D FD 90   STA $90fd     
    $7E79: A5 F7      LDA $f7       
    $7E7B: 29 70      AND #$70      
    $7E7D: 4A         LSR a         
    $7E7E: 4A         LSR a         
    $7E7F: 4A         LSR a         
    $7E80: 4A         LSR a         
    $7E81: A6 FF      LDX $ff       
    $7E83: 9D FE 90   STA $90fe,x   
    $7E86: A0 BC      LDY #$bc      
    $7E88: A5 F7      LDA $f7       
    $7E8A: 10 02      BPL $7e8e        ; → L_7E8E
    $7E8C: A0 7D      LDY #$7d      
L_7E8E:
    $7E8E: 8C A4 7E   STY $7ea4     
    $7E91: BC D4 90   LDY $90d4,x   
    $7E94: B9 38 83   LDA $8338,y   
    $7E97: 38         SEC           
    $7E98: F9 37 83   SBC $8337,y   
    $7E9B: 8D 21 91   STA $9121     
    $7E9E: B9 97 83   LDA $8397,y   
    $7EA1: F9 96 83   SBC $8396,y   
    $7EA4: BC F6 90   LDY $90f6,x   
    $7EA7: 8D 20 91   STA $9120     
L_7EAA:
    $7EAA: CE FD 90   DEC $90fd     
    $7EAD: 30 0C      BMI $7ebb        ; → L_7EBB
    $7EAF: 4E 20 91   LSR $9120     
    $7EB2: 6E 21 91   ROR $9121     
    $7EB5: 4C AA 7E   JMP $7eaa        ; → L_7EAA
L_7EB8:
    $7EB8: 4C 42 7F   JMP $7f42        ; → L_7F42
L_7EBB:
    $7EBB: BD 01 91   LDA $9101,x   
    $7EBE: 10 0A      BPL $7eca        ; → L_7ECA
    $7EC0: DE 04 91   DEC $9104,x   
    $7EC3: D0 19      BNE $7ede        ; → L_7EDE
    $7EC5: FE 01 91   INC $9101,x   
    $7EC8: 10 14      BPL $7ede        ; → L_7EDE
L_7ECA:
    $7ECA: FE 04 91   INC $9104,x   
    $7ECD: BD FE 90   LDA $90fe,x   
    $7ED0: DD 04 91   CMP $9104,x   
    $7ED3: B0 09      BCS $7ede        ; → L_7EDE
    $7ED5: 9D 04 91   STA $9104,x   
    $7ED8: DE 01 91   DEC $9101,x   
    $7EDB: DE 04 91   DEC $9104,x   
L_7EDE:
    $7EDE: BC D4 90   LDY $90d4,x   
    $7EE1: B9 37 83   LDA $8337,y   
    $7EE4: 8D 1E 91   STA $911e     
    $7EE7: B9 96 83   LDA $8396,y   
    $7EEA: 8D 1F 91   STA $911f     
    $7EED: BD FE 90   LDA $90fe,x   
    $7EF0: 4A         LSR a         
    $7EF1: A8         TAY           
L_7EF2:
    $7EF2: 88         DEY           
    $7EF3: 30 1D      BMI $7f12        ; → L_7F12
    $7EF5: BD F6 90   LDA $90f6,x   
    $7EF8: C9 0C      CMP #$0c      
    $7EFA: 90 32      BCC $7f2e        ; → L_7F2E
    $7EFC: AD 1E 91   LDA $911e     
    $7EFF: 38         SEC           
    $7F00: ED 21 91   SBC $9121     
    $7F03: 8D 1E 91   STA $911e     
    $7F06: AD 1F 91   LDA $911f     
    $7F09: ED 20 91   SBC $9120     
    $7F0C: 8D 1F 91   STA $911f     
    $7F0F: 4C F2 7E   JMP $7ef2        ; → L_7EF2
L_7F12:
    $7F12: BC 04 91   LDY $9104,x   
L_7F15:
    $7F15: 88         DEY           
    $7F16: 30 16      BMI $7f2e        ; → L_7F2E
    $7F18: AD 1E 91   LDA $911e     
    $7F1B: 18         CLC           
    $7F1C: 6D 21 91   ADC $9121     
    $7F1F: 8D 1E 91   STA $911e     
    $7F22: AD 1F 91   LDA $911f     
    $7F25: 6D 20 91   ADC $9120     
    $7F28: 8D 1F 91   STA $911f     
    $7F2B: 4C 15 7F   JMP $7f15        ; → L_7F15
L_7F2E:
    $7F2E: A6 FF      LDX $ff       
    $7F30: AD 1E 91   LDA $911e     
    $7F33: 9D 33 91   STA $9133,x   
    $7F36: 9D E3 90   STA $90e3,x   
    $7F39: AD 1F 91   LDA $911f     
    $7F3C: 9D 36 91   STA $9136,x   
    $7F3F: 9D DD 90   STA $90dd,x   
L_7F42:
    $7F42: A6 FF      LDX $ff       
    $7F44: BD E6 90   LDA $90e6,x   
    $7F47: D0 06      BNE $7f4f        ; → L_7F4F
L_7F49:
    $7F49: 4C 38 80   JMP $8038        ; → L_8038
L_7F4C:
    $7F4C: 4C 17 80   JMP $8017        ; → L_8017
L_7F4F:
    $7F4F: BD 2E 91   LDA $912e,x   
    $7F52: 4A         LSR a         
    $7F53: 4A         LSR a         
    $7F54: 4A         LSR a         
    $7F55: 4A         LSR a         
    $7F56: 8D 75 7F   STA $7f75     
    $7F59: 8D C3 7F   STA $7fc3     
    $7F5C: BD 2E 91   LDA $912e,x   
    $7F5F: 29 0F      AND #$0f      
    $7F61: 38         SEC           
    $7F62: E9 01      SBC #$01      
    $7F64: 18         CLC           
    $7F65: 7D CB 90   ADC $90cb,x   
    $7F68: DD CE 90   CMP $90ce,x   
    $7F6B: B0 DC      BCS $7f49        ; → L_7F49
    $7F6D: 48         PHA           
    $7F6E: A9 01      LDA #$01      
    $7F70: 9D E9 90   STA $90e9,x   
    $7F73: 68         PLA           
    $7F74: 69 02      ADC #$02      
    $7F76: DD CE 90   CMP $90ce,x   
    $7F79: 90 D1      BCC $7f4c        ; → L_7F4C
    $7F7B: BC D7 90   LDY $90d7,x   
    $7F7E: BD 2B 91   LDA $912b,x   
    $7F81: AA         TAX           
    $7F82: B9 37 83   LDA $8337,y   
    $7F85: FD 37 83   SBC $8337,x   
    $7F88: 8D FF 7F   STA $7fff     
    $7F8B: B9 96 83   LDA $8396,y   
    $7F8E: FD 96 83   SBC $8396,x   
    $7F91: 8D 0A 80   STA $800a     
    $7F94: A2 38      LDX #$38      
    $7F96: A0 E9      LDY #$e9      
    $7F98: B0 19      BCS $7fb3        ; → L_7FB3
    $7F9A: A2 18      LDX #$18      
    $7F9C: A0 69      LDY #$69      
    $7F9E: 49 FF      EOR #$ff      
    $7FA0: 8D 0A 80   STA $800a     
    $7FA3: AD FF 7F   LDA $7fff     
    $7FA6: 49 FF      EOR #$ff      
    $7FA8: 8D FF 7F   STA $7fff     
    $7FAB: EE FF 7F   INC $7fff     
    $7FAE: D0 03      BNE $7fb3        ; → L_7FB3
    $7FB0: EE 0A 80   INC $800a     
L_7FB3:
    $7FB3: 8C FE 7F   STY $7ffe     
    $7FB6: 8C 09 80   STY $8009     
    $7FB9: 8E FD 7F   STX $7ffd     
    $7FBC: AC FE 7A   LDY $7afe     
    $7FBF: A9 00      LDA #$00      
    $7FC1: 18         CLC           
L_7FC2:
    $7FC2: 69 02      ADC #$02      
    $7FC4: 88         DEY           
    $7FC5: 10 FB      BPL $7fc2        ; → L_7FC2
    $7FC7: 8D 31 91   STA $9131     
    $7FCA: 18         CLC           
    $7FCB: A2 10      LDX #$10      
    $7FCD: A9 00      LDA #$00      
L_7FCF:
    $7FCF: 2E FF 7F   ROL $7fff     
    $7FD2: 2E 0A 80   ROL $800a     
    $7FD5: 2A         ROL a         
    $7FD6: B0 05      BCS $7fdd        ; → L_7FDD
    $7FD8: CD 31 91   CMP $9131     
    $7FDB: 90 04      BCC $7fe1        ; → L_7FE1
L_7FDD:
    $7FDD: ED 31 91   SBC $9131     
    $7FE0: 38         SEC           
L_7FE1:
    $7FE1: CA         DEX           
    $7FE2: D0 EB      BNE $7fcf        ; → L_7FCF
    $7FE4: 2E FF 7F   ROL $7fff     
    $7FE7: 2E 0A 80   ROL $800a     
    $7FEA: 0A         ASL a         
    $7FEB: CD 31 91   CMP $9131     
    $7FEE: 90 08      BCC $7ff8        ; → L_7FF8
    $7FF0: EE FF 7F   INC $7fff     
    $7FF3: D0 03      BNE $7ff8        ; → L_7FF8
    $7FF5: EE 0A 80   INC $800a     
L_7FF8:
    $7FF8: A6 FF      LDX $ff       
    $7FFA: BD E3 90   LDA $90e3,x   
    $7FFD: 38         SEC           
    $7FFE: E9 DC      SBC #$dc      
    $8000: 9D E3 90   STA $90e3,x   
    $8003: 9D 33 91   STA $9133,x   
    $8006: BD DD 90   LDA $90dd,x   
    $8009: E9 01      SBC #$01      
    $800B: 9D DD 90   STA $90dd,x   
    $800E: 9D 36 91   STA $9136,x   
    $8011: 4C 38 80   JMP $8038        ; → L_8038
L_8014:
    $8014: 4C ED 80   JMP $80ed        ; → L_80ED
L_8017:
    $8017: BD 2B 91   LDA $912b,x   
    $801A: 9D D7 90   STA $90d7,x   
    $801D: A8         TAY           
    $801E: B9 37 83   LDA $8337,y   
    $8021: 9D E3 90   STA $90e3,x   
    $8024: 9D 33 91   STA $9133,x   
    $8027: B9 96 83   LDA $8396,y   
    $802A: 9D DD 90   STA $90dd,x   
    $802D: 9D 36 91   STA $9136,x   
    $8030: A9 00      LDA #$00      
    $8032: 9D E6 90   STA $90e6,x   
    $8035: 9D E9 90   STA $90e9,x   
L_8038:
    $8038: A5 F8      LDA $f8       
    $803A: F0 D8      BEQ $8014        ; → L_8014
    $803C: 29 07      AND #$07      
    $803E: 0A         ASL a         
    $803F: 0A         ASL a         
    $8040: 0A         ASL a         
    $8041: E9 07      SBC #$07      
    $8043: A8         TAY           
    $8044: B9 EC 85   LDA $85ec,y   
    $8047: 48         PHA           
    $8048: 29 80      AND #$80      
    $804A: F0 02      BEQ $804e        ; → L_804E
    $804C: A9 01      LDA #$01      
L_804E:
    $804E: 8D D8 80   STA $80d8     
    $8051: 68         PLA           
    $8052: 29 0F      AND #$0f      
    $8054: 8D BA 80   STA $80ba     
    $8057: C8         INY           
    $8058: B9 EC 85   LDA $85ec,y   
    $805B: 8D D4 80   STA $80d4     
    $805E: C8         INY           
    $805F: B9 EC 85   LDA $85ec,y   
    $8062: 29 7F      AND #$7f      
    $8064: DD F6 90   CMP $90f6,x   
    $8067: 90 03      BCC $806c        ; → L_806C
    $8069: 4C 87 80   JMP $8087        ; → L_8087
L_806C:
    $806C: C8         INY           
    $806D: C8         INY           
    $806E: B9 EC 85   LDA $85ec,y   
    $8071: 29 7F      AND #$7f      
    $8073: DD F6 90   CMP $90f6,x   
    $8076: 90 03      BCC $807b        ; → L_807B
    $8078: 4C 87 80   JMP $8087        ; → L_8087
L_807B:
    $807B: C8         INY           
    $807C: C8         INY           
    $807D: B9 EC 85   LDA $85ec,y   
    $8080: 29 7F      AND #$7f      
    $8082: DD F6 90   CMP $90f6,x   
    $8085: 90 14      BCC $809b        ; → L_809B
L_8087:
    $8087: B9 EC 85   LDA $85ec,y   
    $808A: 10 05      BPL $8091        ; → L_8091
    $808C: A9 00      LDA #$00      
    $808E: 9D 12 91   STA $9112,x   
L_8091:
    $8091: C8         INY           
    $8092: B9 EC 85   LDA $85ec,y   
    $8095: 8D F5 90   STA $90f5     
    $8098: 4C A2 80   JMP $80a2        ; → L_80A2
L_809B:
    $809B: A5 F8      LDA $f8       
    $809D: 29 F0      AND #$f0      
    $809F: 8D F5 90   STA $90f5     
L_80A2:
    $80A2: BD 12 91   LDA $9112,x   
    $80A5: D0 1A      BNE $80c1        ; → L_80C1
    $80A7: BD EC 90   LDA $90ec,x   
    $80AA: 38         SEC           
    $80AB: ED F5 90   SBC $90f5     
    $80AE: 9D EC 90   STA $90ec,x   
    $80B1: BD EF 90   LDA $90ef,x   
    $80B4: E9 00      SBC #$00      
    $80B6: 9D EF 90   STA $90ef,x   
    $80B9: C9 06      CMP #$06      
    $80BB: B0 30      BCS $80ed        ; → L_80ED
    $80BD: A9 01      LDA #$01      
    $80BF: D0 29      BNE $80ea        ; → L_80EA
L_80C1:
    $80C1: BD EC 90   LDA $90ec,x   
    $80C4: 18         CLC           
    $80C5: 6D F5 90   ADC $90f5     
    $80C8: 9D EC 90   STA $90ec,x   
    $80CB: BD EF 90   LDA $90ef,x   
    $80CE: 69 00      ADC #$00      
    $80D0: 9D EF 90   STA $90ef,x   
    $80D3: C9 0A      CMP #$0a      
    $80D5: 90 16      BCC $80ed        ; → L_80ED
    $80D7: A9 00      LDA #$00      
    $80D9: F0 0D      BEQ $80e8        ; → L_80E8
    $80DB: 9D EC 90   STA $90ec,x   
    $80DE: AD BA 80   LDA $80ba     
    $80E1: 9D EF 90   STA $90ef,x   
    $80E4: A9 01      LDA #$01      
    $80E6: D0 02      BNE $80ea        ; → L_80EA
L_80E8:
    $80E8: A9 00      LDA #$00      
L_80EA:
    $80EA: 9D 12 91   STA $9112,x   
L_80ED:
    $80ED: A6 FF      LDX $ff       
    $80EF: A4 F6      LDY $f6       
    $80F1: BD EC 90   LDA $90ec,x   
    $80F4: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $80F7: BD EF 90   LDA $90ef,x   
    $80FA: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $80FD: A5 F9      LDA $f9       
    $80FF: 29 40      AND #$40      
    $8101: F0 10      BEQ $8113        ; → L_8113
    $8103: BD F6 90   LDA $90f6,x   
    $8106: C9 03      CMP #$03      
    $8108: 90 09      BCC $8113        ; → L_8113
    $810A: 29 03      AND #$03      
    $810C: A8         TAY           
    $810D: B9 8C 84   LDA $848c,y   
    $8110: 9D 1B 91   STA $911b,x   
L_8113:
    $8113: A5 F9      LDA $f9       
    $8115: 29 08      AND #$08      
    $8117: F0 15      BEQ $812e        ; → L_812E
    $8119: BD F6 90   LDA $90f6,x   
    $811C: C9 01      CMP #$01      
    $811E: 90 0E      BCC $812e        ; → L_812E
    $8120: BD F6 90   LDA $90f6,x   
    $8123: 29 07      AND #$07      
    $8125: A8         TAY           
    $8126: B9 97 84   LDA $8497,y   
    $8129: A4 F6      LDY $f6       
    $812B: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
L_812E:
    $812E: A5 F9      LDA $f9       
    $8130: 29 20      AND #$20      
    $8132: F0 09      BEQ $813d        ; → L_813D
    $8134: DE DD 90   DEC $90dd,x   
    $8137: BD DD 90   LDA $90dd,x   
    $813A: 9D 36 91   STA $9136,x   
L_813D:
    $813D: A5 F9      LDA $f9       
    $813F: 29 01      AND #$01      
    $8141: F0 56      BEQ $8199        ; → L_8199
    $8143: 8E 17 91   STX $9117     
    $8146: BD 0F 91   LDA $910f,x   
    $8149: 29 03      AND #$03      
    $814B: 0A         ASL a         
    $814C: A8         TAY           
    $814D: B9 B7 85   LDA $85b7,y   
    $8150: 8D 5A 81   STA $815a     
    $8153: B9 B8 85   LDA $85b8,y   
    $8156: 8D 5E 81   STA $815e     
    $8159: A9 DD      LDA #$dd      
    $815B: 85 FB      STA $fb       
    $815D: A9 85      LDA #$85      
    $815F: 85 FC      STA $fc       
    $8161: A0 05      LDY #$05      
    $8163: B1 FB      LDA ($fb),y   
    $8165: 8D 18 D4   STA $d418      ;VOL
    $8168: BD F6 90   LDA $90f6,x   
    $816B: A0 09      LDY #$09      
    $816D: D1 FB      CMP ($fb),y   
    $816F: 90 07      BCC $8178        ; → L_8178
    $8171: A0 04      LDY #$04      
    $8173: B1 FB      LDA ($fb),y   
    $8175: 4C A2 81   JMP $81a2        ; → L_81A2
L_8178:
    $8178: 88         DEY           
    $8179: D1 FB      CMP ($fb),y   
    $817B: B0 0E      BCS $818b        ; → L_818B
    $817D: C0 06      CPY #$06      
    $817F: D0 F7      BNE $8178        ; → L_8178
    $8181: A0 00      LDY #$00      
    $8183: B1 FB      LDA ($fb),y   
    $8185: 4C A2 81   JMP $81a2        ; → L_81A2
; ----- data gap $8188-$818A (3 bytes) -----

L_818B:
    $818B: 88         DEY           
    $818C: 88         DEY           
    $818D: 88         DEY           
    $818E: 88         DEY           
    $818F: 88         DEY           
    $8190: BD 0C 91   LDA $910c,x   
    $8193: 18         CLC           
    $8194: 71 FB      ADC ($fb),y   
    $8196: 4C A2 81   JMP $81a2        ; → L_81A2
L_8199:
    $8199: A6 FF      LDX $ff       
    $819B: EC 17 91   CPX $9117     
    $819E: D0 08      BNE $81a8        ; → L_81A8
    $81A0: A9 E0      LDA #$e0      
L_81A2:
    $81A2: 9D 0C 91   STA $910c,x   
    $81A5: 8D 16 D4   STA $d416      ;FC_HI
L_81A8:
    $81A8: A5 F8      LDA $f8       
    $81AA: 29 08      AND #$08      
    $81AC: F0 5E      BEQ $820c        ; → L_820C
    $81AE: AD F6 90   LDA $90f6     
    $81B1: 29 01      AND #$01      
    $81B3: F0 2F      BEQ $81e4        ; → L_81E4
    $81B5: AD 2A 91   LDA $912a     
    $81B8: F0 16      BEQ $81d0        ; → L_81D0
    $81BA: AD E7 85   LDA $85e7     
    $81BD: 38         SEC           
    $81BE: ED EA 85   SBC $85ea     
    $81C1: 8D E7 85   STA $85e7     
    $81C4: CD E8 85   CMP $85e8     
    $81C7: B0 1B      BCS $81e4        ; → L_81E4
    $81C9: A9 00      LDA #$00      
    $81CB: 8D 2A 91   STA $912a     
    $81CE: F0 14      BEQ $81e4        ; → L_81E4
L_81D0:
    $81D0: AD E7 85   LDA $85e7     
    $81D3: 18         CLC           
    $81D4: 6D EA 85   ADC $85ea     
    $81D7: 8D E7 85   STA $85e7     
    $81DA: CD E9 85   CMP $85e9     
    $81DD: 90 05      BCC $81e4        ; → L_81E4
    $81DF: A9 01      LDA #$01      
    $81E1: 8D 2A 91   STA $912a     
L_81E4:
    $81E4: A6 FF      LDX $ff       
    $81E6: AD F6 90   LDA $90f6     
    $81E9: C9 02      CMP #$02      
    $81EB: B0 05      BCS $81f2        ; → L_81F2
    $81ED: A9 40      LDA #$40      
    $81EF: 8D 32 91   STA $9132     
L_81F2:
    $81F2: AD E7 85   LDA $85e7     
    $81F5: 18         CLC           
    $81F6: 6D 32 91   ADC $9132     
    $81F9: 8D 16 D4   STA $d416      ;FC_HI
    $81FC: AD 32 91   LDA $9132     
    $81FF: C9 02      CMP #$02      
    $8201: 90 09      BCC $820c        ; → L_820C
    $8203: AD 32 91   LDA $9132     
    $8206: ED EB 85   SBC $85eb     
    $8209: 8D 32 91   STA $9132     
L_820C:
    $820C: A6 FF      LDX $ff       
    $820E: A5 F9      LDA $f9       
    $8210: 29 02      AND #$02      
    $8212: F0 17      BEQ $822b        ; → L_822B
    $8214: BC F6 90   LDY $90f6,x   
    $8217: C0 07      CPY #$07      
    $8219: B0 10      BCS $822b        ; → L_822B
    $821B: 88         DEY           
    $821C: B9 89 84   LDA $8489,y   
    $821F: 9D 1B 91   STA $911b,x   
    $8222: B9 90 84   LDA $8490,y   
    $8225: 7D D4 90   ADC $90d4,x   
    $8228: 4C 27 83   JMP $8327        ; → L_8327
L_822B:
    $822B: BD 0F 91   LDA $910f,x   
    $822E: 29 08      AND #$08      
    $8230: F0 11      BEQ $8243        ; → L_8243
    $8232: BD E3 90   LDA $90e3,x   
    $8235: 18         CLC           
    $8236: 69 20      ADC #$20      
    $8238: 9D 33 91   STA $9133,x   
    $823B: BD DD 90   LDA $90dd,x   
    $823E: 69 00      ADC #$00      
    $8240: 9D 36 91   STA $9136,x   
L_8243:
    $8243: BD 0F 91   LDA $910f,x   
    $8246: 29 04      AND #$04      
    $8248: F0 22      BEQ $826c        ; → L_826C
    $824A: BD CE 90   LDA $90ce,x   
    $824D: 29 7F      AND #$7f      
    $824F: C9 00      CMP #$00      
    $8251: 90 19      BCC $826c        ; → L_826C
    $8253: BD CB 90   LDA $90cb,x   
    $8256: C9 FF      CMP #$ff      
    $8258: B0 12      BCS $826c        ; → L_826C
    $825A: BD F6 90   LDA $90f6,x   
    $825D: 29 01      AND #$01      
    $825F: F0 0B      BEQ $826c        ; → L_826C
    $8261: BD E0 90   LDA $90e0,x   
    $8264: F0 06      BEQ $826c        ; → L_826C
    $8266: FE E0 90   INC $90e0,x   
    $8269: 9D 36 91   STA $9136,x   
L_826C:
    $826C: A5 F9      LDA $f9       
    $826E: 29 10      AND #$10      
    $8270: F0 62      BEQ $82d4        ; → L_82D4
    $8272: A5 F7      LDA $f7       
    $8274: 29 0F      AND #$0f      
    $8276: 0A         ASL a         
    $8277: 0A         ASL a         
    $8278: A8         TAY           
    $8279: B9 9F 84   LDA $849f,y   
    $827C: 8D A6 82   STA $82a6     
    $827F: 8D 98 82   STA $8298     
    $8282: B9 A0 84   LDA $84a0,y   
    $8285: 8D A7 82   STA $82a7     
    $8288: 8D 99 82   STA $8299     
    $828B: B9 A1 84   LDA $84a1,y   
    $828E: 8D AD 82   STA $82ad     
    $8291: B9 A2 84   LDA $84a2,y   
    $8294: 8D AE 82   STA $82ae     
    $8297: AD 77 85   LDA $8577     
    $829A: 8D A1 82   STA $82a1     
    $829D: BD F6 90   LDA $90f6,x   
    $82A0: C9 03      CMP #$03      
    $82A2: B0 2D      BCS $82d1        ; → L_82D1
    $82A4: A8         TAY           
    $82A5: B9 77 85   LDA $8577,y   
    $82A8: 9D 1B 91   STA $911b,x   
    $82AB: 88         DEY           
    $82AC: B9 7C 85   LDA $857c,y   
    $82AF: 8D 0B 91   STA $910b     
    $82B2: A4 F6      LDY $f6       
    $82B4: A5 F7      LDA $f7       
    $82B6: 29 10      AND #$10      
    $82B8: F0 09      BEQ $82c3        ; → L_82C3
    $82BA: BD D4 90   LDA $90d4,x   
    $82BD: 6D 0B 91   ADC $910b     
    $82C0: 4C 27 83   JMP $8327        ; → L_8327
L_82C3:
    $82C3: AD 0B 91   LDA $910b     
    $82C6: 18         CLC           
    $82C7: 69 0D      ADC #$0d      
    $82C9: 9D 36 91   STA $9136,x   
    $82CC: A9 00      LDA #$00      
    $82CE: 9D 33 91   STA $9133,x   
L_82D1:
    $82D1: 4C 0C 83   JMP $830c        ; → L_830C
L_82D4:
    $82D4: A5 F9      LDA $f9       
    $82D6: 10 34      BPL $830c        ; → L_830C
    $82D8: BD F6 90   LDA $90f6,x   
    $82DB: C9 02      CMP #$02      
    $82DD: B0 12      BCS $82f1        ; → L_82F1
    $82DF: A9 58      LDA #$58      
    $82E1: 9D 36 91   STA $9136,x   
    $82E4: A9 00      LDA #$00      
    $82E6: 9D 33 91   STA $9133,x   
    $82E9: A9 81      LDA #$81      
    $82EB: 9D 1B 91   STA $911b,x   
    $82EE: 4C 0C 83   JMP $830c        ; → L_830C
L_82F1:
    $82F1: BD F6 90   LDA $90f6,x   
    $82F4: C9 04      CMP #$04      
    $82F6: B0 14      BCS $830c        ; → L_830C
    $82F8: BD E3 90   LDA $90e3,x   
    $82FB: 9D 33 91   STA $9133,x   
    $82FE: BD DD 90   LDA $90dd,x   
    $8301: 9D 36 91   STA $9136,x   
    $8304: BD D1 90   LDA $90d1,x   
    $8307: 29 FE      AND #$fe      
    $8309: 9D 1B 91   STA $911b,x   
L_830C:
    $830C: A4 F6      LDY $f6       
    $830E: BD 1B 91   LDA $911b,x   
    $8311: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $8314: BD 33 91   LDA $9133,x   
    $8317: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $831A: BD 36 91   LDA $9136,x   
    $831D: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $8320: CA         DEX           
    $8321: 30 03      BMI $8326        ; → L_8326
    $8323: 4C BA 7B   JMP $7bba        ; → L_7BBA
L_8326:
    $8326: 60         RTS           
L_8327:
    $8327: A8         TAY           
    $8328: B9 37 83   LDA $8337,y   
    $832B: 9D 33 91   STA $9133,x   
    $832E: B9 96 83   LDA $8396,y   
    $8331: 9D 36 91   STA $9136,x   
    $8334: 4C 0C 83   JMP $830c        ; → L_830C
; ----- data gap $8337-$918E (3672 bytes) -----

L_918F:
    $918F: C9 06      CMP #$06      
    $9191: B0 07      BCS $919a        ; → L_919A
    $9193: AA         TAX           
L_9194:
    $9194: 20 5A 7B   JSR $7b5a        ; → sub_7B5A
L_9197:
    $9197: 60         RTS           
; ----- data gap $9198-$9199 (2 bytes) -----

L_919A:
    $919A: C9 0C      CMP #$0c      
    $919C: B0 F9      BCS $9197        ; → L_9197
    $919E: 38         SEC           
    $919F: E9 06      SBC #$06      
    $91A1: 0A         ASL a         
    $91A2: 18         CLC           
    $91A3: 69 92      ADC #$92      
    $91A5: 85 03      STA $03       
    $91A7: A9 00      LDA #$00      
    $91A9: 85 02      STA $02       
    $91AB: A0 05      LDY #$05      
L_91AD:
    $91AD: B1 02      LDA ($02),y   
    $91AF: 99 2C 7B   STA $7b2c,y   
    $91B2: 88         DEY           
    $91B3: 10 F8      BPL $91ad        ; → L_91AD
    $91B5: A9 06      LDA #$06      
    $91B7: 85 02      STA $02       
    $91B9: A0 13      LDY #$13      
L_91BB:
    $91BB: B1 02      LDA ($02),y   
    $91BD: 99 75 84   STA $8475,y   
    $91C0: 88         DEY           
    $91C1: 10 F8      BPL $91bb        ; → L_91BB
    $91C3: A9 1A      LDA #$1a      
    $91C5: 85 02      STA $02       
    $91C7: A0 00      LDY #$00      
L_91C9:
    $91C9: B1 02      LDA ($02),y   
    $91CB: 99 C5 8F   STA $8fc5,y   
    $91CE: 88         DEY           
    $91CF: D0 F8      BNE $91c9        ; → L_91C9
    $91D1: A2 06      LDX #$06      
    $91D3: 4C 94 91   JMP $9194        ; → L_9194
; ----- data gap $91D6-$9D1F (2890 bytes) -----

