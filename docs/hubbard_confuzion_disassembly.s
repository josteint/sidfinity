; ============================================================================
; Rob Hubbard - Confuzion (1985 Incentive)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: demo/hubbard/Confuzion_original.sid
; Load:   $0858   Init: $0867   Play: $0858
; PSID:   1 subtune(s), default subtune 1
; Binary: $0858-$11A5 (2382 bytes)
;
; Auto-traced 648 reachable code bytes from init+play.
;
; ============================================================================

; ======= play: =======
play:
    $0858: A5 A2      LDA $a2       
    $085A: 48         PHA           
    $085B: A9 00      LDA #$00      
    $085D: 85 A2      STA $a2       
    $085F: 20 CB 08   JSR $08cb        ; → sub_08CB
    $0862: EE 5C 08   INC $085c     
    $0865: 68         PLA           
    $0866: 85 A2      STA $a2       
    $0868: 60         RTS           
    $0869: 8E 9C 08   STX $089c     
    $086C: 8E FA 0A   STX $0afa     
    $086F: A9 EA      LDA #$ea      
    $0871: 8D B9 08   STA $08b9     
    $0874: 8E C2 08   STX $08c2     
    $0877: A2 02      LDX #$02      
    $0879: A9 00      LDA #$00      
    $087B: 8D 5C 08   STA $085c     
    $087E: F0 07      BEQ $0887        ; → L_0887
    $0880: 78         SEI           
    $0881: A2 02      LDX #$02      
    $0883: A9 00      LDA #$00      
    $0885: 85 A2      STA $a2       
L_0887:
    $0887: 9D C1 0B   STA $0bc1,x   
    $088A: 9D C4 0B   STA $0bc4,x   
    $088D: 9D C7 0B   STA $0bc7,x   
    $0890: 9D D0 0B   STA $0bd0,x   
    $0893: CA         DEX           
    $0894: 10 F1      BPL $0887        ; → L_0887
    $0896: 8E EB 0B   STX $0beb     
    $0899: 20 A3 08   JSR $08a3        ; → sub_08A3
    $089C: 58         CLI           
    $089D: 60         RTS           
; ----- data gap $089E-$08A2 (5 bytes) -----

sub_08A3:
    $08A3: A2 17      LDX #$17      
L_08A5:
    $08A5: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $08A8: CA         DEX           
    $08A9: 10 FA      BPL $08a5        ; → L_08A5
    $08AB: 60         RTS           
; ----- data gap $08AC-$08B8 (13 bytes) -----

L_08B9:
    $08B9: 78         SEI           
    $08BA: A9 00      LDA #$00      
    $08BC: 8D EB 0B   STA $0beb     
    $08BF: 8D 18 D4   STA $d418      ;VOL
    $08C2: 58         CLI           
    $08C3: 4C FA 0A   JMP $0afa        ; → L_0AFA
; ----- data gap $08C6-$08CA (5 bytes) -----

sub_08CB:
    $08CB: AD EB 0B   LDA $0beb     
    $08CE: D0 03      BNE $08d3        ; → L_08D3
    $08D0: 4C FA 0A   JMP $0afa        ; → L_0AFA
L_08D3:
    $08D3: A2 02      LDX #$02      
    $08D5: CE E8 0B   DEC $0be8     
    $08D8: 10 06      BPL $08e0        ; → L_08E0
    $08DA: AD E9 0B   LDA $0be9     
    $08DD: 8D E8 0B   STA $0be8     
L_08E0:
    $08E0: BD BD 0B   LDA $0bbd,x   
    $08E3: 8D C0 0B   STA $0bc0     
    $08E6: A8         TAY           
    $08E7: AD E8 0B   LDA $0be8     
    $08EA: CD E9 0B   CMP $0be9     
    $08ED: D0 15      BNE $0904        ; → L_0904
    $08EF: BD F1 0B   LDA $0bf1,x   
    $08F2: 85 FB      STA $fb       
    $08F4: BD F4 0B   LDA $0bf4,x   
    $08F7: 85 FC      STA $fc       
    $08F9: DE C7 0B   DEC $0bc7,x   
    $08FC: 30 09      BMI $0907        ; → L_0907
    $08FE: 4C E2 09   JMP $09e2        ; → L_09E2
; ----- data gap $0901-$0903 (3 bytes) -----

L_0904:
    $0904: 4C 01 0A   JMP $0a01        ; → L_0A01
L_0907:
    $0907: BC C1 0B   LDY $0bc1,x   
    $090A: B1 FB      LDA ($fb),y   
    $090C: C9 FF      CMP #$ff      
    $090E: D0 11      BNE $0921        ; → L_0921
    $0910: A9 00      LDA #$00      
    $0912: 9D C7 0B   STA $0bc7,x   
    $0915: 9D C1 0B   STA $0bc1,x   
    $0918: 9D C4 0B   STA $0bc4,x   
    $091B: 4C B9 08   JMP $08b9        ; → L_08B9
; ----- data gap $091E-$0920 (3 bytes) -----

L_0921:
    $0921: A8         TAY           
    $0922: B9 F7 0B   LDA $0bf7,y   
    $0925: 85 FD      STA $fd       
    $0927: B9 15 0C   LDA $0c15,y   
    $092A: 85 FE      STA $fe       
    $092C: BC C4 0B   LDY $0bc4,x   
    $092F: A9 FF      LDA #$ff      
    $0931: 8D D6 0B   STA $0bd6     
    $0934: B1 FD      LDA ($fd),y   
    $0936: 9D CA 0B   STA $0bca,x   
    $0939: 8D D7 0B   STA $0bd7     
    $093C: 29 1F      AND #$1f      
    $093E: 9D C7 0B   STA $0bc7,x   
    $0941: 2C D7 0B   BIT $0bd7     
    $0944: 70 45      BVS $098b        ; → L_098B
    $0946: FE C4 0B   INC $0bc4,x   
    $0949: AD D7 0B   LDA $0bd7     
    $094C: 10 1A      BPL $0968        ; → L_0968
    $094E: C8         INY           
    $094F: B1 FD      LDA ($fd),y   
    $0951: 29 1F      AND #$1f      
    $0953: 9D D3 0B   STA $0bd3,x   
    $0956: A9 A0      LDA #$a0      
    $0958: 38         SEC           
    $0959: ED C2 0B   SBC $0bc2     
    $095C: C9 0F      CMP #$0f      
    $095E: 90 02      BCC $0962        ; → L_0962
    $0960: A9 0F      LDA #$0f      
L_0962:
    $0962: 8D 18 D4   STA $d418      ;VOL
    $0965: FE C4 0B   INC $0bc4,x   
L_0968:
    $0968: C8         INY           
    $0969: B1 FD      LDA ($fd),y   
    $096B: 9D D0 0B   STA $0bd0,x   
    $096E: 0A         ASL a         
    $096F: A8         TAY           
    $0970: B9 FD 0A   LDA $0afd,y   
    $0973: 8D D8 0B   STA $0bd8     
    $0976: B9 FE 0A   LDA $0afe,y   
    $0979: AC C0 0B   LDY $0bc0     
    $097C: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $097F: 9D EC 0B   STA $0bec,x   
    $0982: AD D8 0B   LDA $0bd8     
    $0985: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $0988: 4C 8E 09   JMP $098e        ; → L_098E
L_098B:
    $098B: CE D6 0B   DEC $0bd6     
L_098E:
    $098E: AC C0 0B   LDY $0bc0     
    $0991: BD D3 0B   LDA $0bd3,x   
    $0994: 8E D9 0B   STX $0bd9     
    $0997: 0A         ASL a         
    $0998: 0A         ASL a         
    $0999: 0A         ASL a         
    $099A: AA         TAX           
    $099B: BD 48 11   LDA $1148,x   
    $099E: 8D DA 0B   STA $0bda     
    $09A1: BD 48 11   LDA $1148,x   
    $09A4: 2D D6 0B   AND $0bd6     
    $09A7: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $09AA: BD 46 11   LDA $1146,x   
    $09AD: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $09B0: BD 47 11   LDA $1147,x   
    $09B3: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $09B6: BD 49 11   LDA $1149,x   
    $09B9: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $09BC: BD 4A 11   LDA $114a,x   
    $09BF: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $09C2: AE D9 0B   LDX $0bd9     
    $09C5: AD DA 0B   LDA $0bda     
    $09C8: 9D CD 0B   STA $0bcd,x   
    $09CB: FE C4 0B   INC $0bc4,x   
    $09CE: BC C4 0B   LDY $0bc4,x   
    $09D1: B1 FD      LDA ($fd),y   
    $09D3: C9 FF      CMP #$ff      
    $09D5: D0 08      BNE $09df        ; → L_09DF
    $09D7: A9 00      LDA #$00      
    $09D9: 9D C4 0B   STA $0bc4,x   
    $09DC: FE C1 0B   INC $0bc1,x   
L_09DF:
    $09DF: 4C F4 0A   JMP $0af4        ; → L_0AF4
L_09E2:
    $09E2: AC C0 0B   LDY $0bc0     
    $09E5: BD CA 0B   LDA $0bca,x   
    $09E8: 29 20      AND #$20      
    $09EA: D0 15      BNE $0a01        ; → L_0A01
    $09EC: BD C7 0B   LDA $0bc7,x   
    $09EF: D0 10      BNE $0a01        ; → L_0A01
    $09F1: BD CD 0B   LDA $0bcd,x   
    $09F4: 29 FE      AND #$fe      
    $09F6: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $09F9: A9 00      LDA #$00      
    $09FB: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $09FE: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_0A01:
    $0A01: BD D3 0B   LDA $0bd3,x   
    $0A04: 0A         ASL a         
    $0A05: 0A         ASL a         
    $0A06: 0A         ASL a         
    $0A07: A8         TAY           
    $0A08: 8C EA 0B   STY $0bea     
    $0A0B: B9 4D 11   LDA $114d,y   
    $0A0E: 8D EF 0B   STA $0bef     
    $0A11: B9 4C 11   LDA $114c,y   
    $0A14: 8D DC 0B   STA $0bdc     
    $0A17: B9 4B 11   LDA $114b,y   
    $0A1A: 8D DB 0B   STA $0bdb     
    $0A1D: F0 6E      BEQ $0a8d        ; → L_0A8D
    $0A1F: A5 A2      LDA $a2       
    $0A21: 29 07      AND #$07      
    $0A23: C9 04      CMP #$04      
    $0A25: 90 02      BCC $0a29        ; → L_0A29
    $0A27: 49 07      EOR #$07      
L_0A29:
    $0A29: 8D E1 0B   STA $0be1     
    $0A2C: BD D0 0B   LDA $0bd0,x   
    $0A2F: 0A         ASL a         
    $0A30: A8         TAY           
    $0A31: 38         SEC           
    $0A32: B9 FF 0A   LDA $0aff,y   
    $0A35: F9 FD 0A   SBC $0afd,y   
    $0A38: 8D DD 0B   STA $0bdd     
    $0A3B: B9 00 0B   LDA $0b00,y   
    $0A3E: F9 FE 0A   SBC $0afe,y   
L_0A41:
    $0A41: 4A         LSR a         
    $0A42: 6E DD 0B   ROR $0bdd     
    $0A45: CE DB 0B   DEC $0bdb     
    $0A48: 10 F7      BPL $0a41        ; → L_0A41
    $0A4A: 8D DE 0B   STA $0bde     
    $0A4D: B9 FD 0A   LDA $0afd,y   
    $0A50: 8D DF 0B   STA $0bdf     
    $0A53: B9 FE 0A   LDA $0afe,y   
    $0A56: 8D E0 0B   STA $0be0     
    $0A59: BD CA 0B   LDA $0bca,x   
    $0A5C: 29 1F      AND #$1f      
    $0A5E: C9 08      CMP #$08      
    $0A60: 90 1C      BCC $0a7e        ; → L_0A7E
    $0A62: AC E1 0B   LDY $0be1     
L_0A65:
    $0A65: 88         DEY           
    $0A66: 30 16      BMI $0a7e        ; → L_0A7E
    $0A68: 18         CLC           
    $0A69: AD DF 0B   LDA $0bdf     
    $0A6C: 6D DD 0B   ADC $0bdd     
    $0A6F: 8D DF 0B   STA $0bdf     
    $0A72: AD E0 0B   LDA $0be0     
    $0A75: 6D DE 0B   ADC $0bde     
    $0A78: 8D E0 0B   STA $0be0     
    $0A7B: 4C 65 0A   JMP $0a65        ; → L_0A65
L_0A7E:
    $0A7E: AC C0 0B   LDY $0bc0     
    $0A81: AD DF 0B   LDA $0bdf     
    $0A84: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $0A87: AD E0 0B   LDA $0be0     
    $0A8A: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_0A8D:
    $0A8D: AD DC 0B   LDA $0bdc     
    $0A90: F0 62      BEQ $0af4        ; → L_0AF4
    $0A92: AC EA 0B   LDY $0bea     
    $0A95: 29 1F      AND #$1f      
    $0A97: DE E2 0B   DEC $0be2,x   
    $0A9A: 10 58      BPL $0af4        ; → L_0AF4
    $0A9C: 9D E2 0B   STA $0be2,x   
    $0A9F: AD DC 0B   LDA $0bdc     
    $0AA2: 29 E0      AND #$e0      
    $0AA4: 8D F0 0B   STA $0bf0     
    $0AA7: BD E5 0B   LDA $0be5,x   
    $0AAA: D0 1A      BNE $0ac6        ; → L_0AC6
    $0AAC: AD F0 0B   LDA $0bf0     
    $0AAF: 18         CLC           
    $0AB0: 79 46 11   ADC $1146,y   
    $0AB3: 48         PHA           
    $0AB4: B9 47 11   LDA $1147,y   
    $0AB7: 69 00      ADC #$00      
    $0AB9: 29 0F      AND #$0f      
    $0ABB: 48         PHA           
    $0ABC: C9 0E      CMP #$0e      
    $0ABE: D0 1D      BNE $0add        ; → L_0ADD
    $0AC0: FE E5 0B   INC $0be5,x   
    $0AC3: 4C DD 0A   JMP $0add        ; → L_0ADD
L_0AC6:
    $0AC6: 38         SEC           
    $0AC7: B9 46 11   LDA $1146,y   
    $0ACA: ED F0 0B   SBC $0bf0     
    $0ACD: 48         PHA           
    $0ACE: B9 47 11   LDA $1147,y   
    $0AD1: E9 00      SBC #$00      
    $0AD3: 29 0F      AND #$0f      
    $0AD5: 48         PHA           
    $0AD6: C9 08      CMP #$08      
    $0AD8: D0 03      BNE $0add        ; → L_0ADD
    $0ADA: DE E5 0B   DEC $0be5,x   
L_0ADD:
    $0ADD: 8E D9 0B   STX $0bd9     
    $0AE0: AE C0 0B   LDX $0bc0     
    $0AE3: 68         PLA           
    $0AE4: 99 47 11   STA $1147,y   
    $0AE7: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $0AEA: 68         PLA           
    $0AEB: 99 46 11   STA $1146,y   
    $0AEE: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $0AF1: AE D9 0B   LDX $0bd9     
L_0AF4:
    $0AF4: CA         DEX           
    $0AF5: 30 03      BMI $0afa        ; → L_0AFA
    $0AF7: 4C E0 08   JMP $08e0        ; → L_08E0
L_0AFA:
    $0AFA: 4C 81 EA   JMP $ea81     
; ----- data gap $0AFD-$11A5 (1705 bytes) -----

