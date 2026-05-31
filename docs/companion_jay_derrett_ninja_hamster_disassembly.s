; ============================================================================
; Rob Hubbard - Ninja Hamster (1987 CRL)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/D/Derrett_Jay/Ninja_Hamster.sid
; Load:   $C000   Init: $C57A   Play: $C452
; PSID:   1 subtune(s), default subtune 1
; Binary: $C000-$CAFF (2816 bytes)
;
; Auto-traced 897 reachable code bytes from init+play.
;
; ============================================================================

; ----- data gap $C000-$C451 (1106 bytes) -----

; ======= play: =======
play:
    $C452: EE C1 C5   INC $c5c1     
    $C455: CE B9 C5   DEC $c5b9     
    $C458: F0 03      BEQ $c45d        ; → L_C45D
    $C45A: 4C DD C6   JMP $c6dd        ; → L_C6DD
L_C45D:
    $C45D: AD C2 C5   LDA $c5c2     
    $C460: 85 F2      STA $f2       
    $C462: AD C3 C5   LDA $c5c3     
    $C465: 85 F3      STA $f3       
    $C467: A2 00      LDX #$00      
    $C469: 86 F4      STX $f4       
    $C46B: 86 F5      STX $f5       
    $C46D: 20 BB C4   JSR $c4bb        ; → sub_C4BB
    $C470: A5 F2      LDA $f2       
    $C472: 8D C2 C5   STA $c5c2     
    $C475: A5 F3      LDA $f3       
    $C477: 8D C3 C5   STA $c5c3     
    $C47A: AD C4 C5   LDA $c5c4     
    $C47D: 85 F2      STA $f2       
    $C47F: AD C5 C5   LDA $c5c5     
    $C482: 85 F3      STA $f3       
    $C484: E6 F4      INC $f4       
    $C486: A9 1A      LDA #$1a      
    $C488: 85 F5      STA $f5       
    $C48A: 20 BB C4   JSR $c4bb        ; → sub_C4BB
    $C48D: A5 F2      LDA $f2       
    $C48F: 8D C4 C5   STA $c5c4     
    $C492: A5 F3      LDA $f3       
    $C494: 8D C5 C5   STA $c5c5     
    $C497: AD C6 C5   LDA $c5c6     
    $C49A: 85 F2      STA $f2       
    $C49C: AD C7 C5   LDA $c5c7     
    $C49F: 85 F3      STA $f3       
    $C4A1: E6 F4      INC $f4       
    $C4A3: 06 F5      ASL $f5       
    $C4A5: 20 BB C4   JSR $c4bb        ; → sub_C4BB
    $C4A8: A5 F2      LDA $f2       
    $C4AA: 8D C6 C5   STA $c5c6     
    $C4AD: A5 F3      LDA $f3       
    $C4AF: 8D C7 C5   STA $c5c7     
    $C4B2: AD BA C5   LDA $c5ba     
    $C4B5: 8D B9 C5   STA $c5b9     
    $C4B8: 4C DD C6   JMP $c6dd        ; → L_C6DD
sub_C4BB:
    $C4BB: A6 F4      LDX $f4       
    $C4BD: DE B6 C5   DEC $c5b6,x   
    $C4C0: F0 01      BEQ $c4c3        ; → L_C4C3
    $C4C2: 60         RTS           
L_C4C3:
    $C4C3: FE B6 C5   INC $c5b6,x   
    $C4C6: A0 00      LDY #$00      
    $C4C8: B1 F2      LDA ($f2),y   
    $C4CA: 29 F0      AND #$f0      
    $C4CC: C9 E0      CMP #$e0      
    $C4CE: D0 2E      BNE $c4fe        ; → L_C4FE
    $C4D0: B1 F2      LDA ($f2),y   
    $C4D2: C9 E0      CMP #$e0      
    $C4D4: D0 38      BNE $c50e        ; → L_C50E
    $C4D6: 29 0F      AND #$0f      
    $C4D8: 0A         ASL a         
    $C4D9: A8         TAY           
    $C4DA: B9 CB C5   LDA $c5cb,y   
    $C4DD: 85 F2      STA $f2       
    $C4DF: B9 CC C5   LDA $c5cc,y   
    $C4E2: 85 F3      STA $f3       
    $C4E4: EE D3 C4   INC $c4d3     
    $C4E7: AD D3 C4   LDA $c4d3     
    $C4EA: C9 E9      CMP #$e9      
    $C4EC: D0 CD      BNE $c4bb        ; → sub_C4BB
    $C4EE: A9 E0      LDA #$e0      
    $C4F0: 8D D3 C4   STA $c4d3     
    $C4F3: A9 00      LDA #$00      
    $C4F5: 8D 75 C9   STA $c975     
    $C4F8: 8D 78 C9   STA $c978     
    $C4FB: 4C BB C4   JMP $c4bb        ; → sub_C4BB
L_C4FE:
    $C4FE: C9 D0      CMP #$d0      
    $C500: D0 15      BNE $c517        ; → L_C517
    $C502: B1 F2      LDA ($f2),y   
    $C504: 29 0F      AND #$0f      
    $C506: A6 F4      LDX $f4       
    $C508: 9D BB C5   STA $c5bb,x   
    $C50B: FE BB C5   INC $c5bb,x   
L_C50E:
    $C50E: E6 F2      INC $f2       
    $C510: D0 02      BNE $c514        ; → L_C514
    $C512: E6 F3      INC $f3       
L_C514:
    $C514: 4C BB C4   JMP $c4bb        ; → sub_C4BB
L_C517:
    $C517: B1 F2      LDA ($f2),y   
    $C519: C9 80      CMP #$80      
    $C51B: D0 0F      BNE $c52c        ; → L_C52C
    $C51D: A4 F5      LDY $f5       
    $C51F: B9 41 C9   LDA $c941,y   
    $C522: 99 44 C9   STA $c944,y   
sub_C525:
    $C525: E6 F2      INC $f2       
    $C527: D0 02      BNE $c52b        ; → L_C52B
    $C529: E6 F3      INC $f3       
L_C52B:
    $C52B: 60         RTS           
L_C52C:
    $C52C: C9 81      CMP #$81      
    $C52E: F0 F5      BEQ $c525        ; → sub_C525
    $C530: C9 82      CMP #$82      
    $C532: D0 0D      BNE $c541        ; → L_C541
    $C534: 20 25 C5   JSR $c525        ; → sub_C525
    $C537: B1 F2      LDA ($f2),y   
    $C539: A6 F4      LDX $f4       
    $C53B: 9D B6 C5   STA $c5b6,x   
    $C53E: 4C 25 C5   JMP $c525        ; → sub_C525
L_C541:
    $C541: 29 F0      AND #$f0      
    $C543: C9 B0      CMP #$b0      
    $C545: D0 0D      BNE $c554        ; → L_C554
    $C547: B1 F2      LDA ($f2),y   
    $C549: 29 0F      AND #$0f      
    $C54B: 8D BA C5   STA $c5ba     
    $C54E: CE BA C5   DEC $c5ba     
    $C551: 4C 0E C5   JMP $c50e        ; → L_C50E
L_C554:
    $C554: C9 C0      CMP #$c0      
    $C556: D0 0A      BNE $c562        ; → L_C562
    $C558: B1 F2      LDA ($f2),y   
    $C55A: 29 0F      AND #$0f      
    $C55C: 8D 18 D4   STA $d418      ;VOL
    $C55F: 4C 0E C5   JMP $c50e        ; → L_C50E
L_C562:
    $C562: A6 F4      LDX $f4       
    $C564: BC FB CA   LDY $cafb,x   
    $C567: BD BE C5   LDA $c5be,x   
    $C56A: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $C56D: BD BB C5   LDA $c5bb,x   
    $C570: 20 6E C8   JSR $c86e        ; → sub_C86E
    $C573: E6 F2      INC $f2       
    $C575: D0 02      BNE $c579        ; → L_C579
    $C577: E6 F3      INC $f3       
L_C579:
    $C579: 60         RTS           
; ======= init: =======
init:
    $C57A: A9 00      LDA #$00      
    $C57C: 8D C2 C5   STA $c5c2     
    $C57F: A9 C0      LDA #$c0      
    $C581: 8D C3 C5   STA $c5c3     
    $C584: A9 69      LDA #$69      
    $C586: 8D C4 C5   STA $c5c4     
    $C589: A9 C1      LDA #$c1      
    $C58B: 8D C5 C5   STA $c5c5     
    $C58E: A9 42      LDA #$42      
    $C590: 8D C6 C5   STA $c5c6     
    $C593: A9 C3      LDA #$c3      
    $C595: 8D C7 C5   STA $c5c7     
    $C598: A9 E0      LDA #$e0      
    $C59A: 8D D3 C4   STA $c4d3     
    $C59D: A9 0A      LDA #$0a      
    $C59F: 8D B9 C5   STA $c5b9     
    $C5A2: 8D BA C5   STA $c5ba     
    $C5A5: A9 0F      LDA #$0f      
    $C5A7: 8D 18 D4   STA $d418      ;VOL
    $C5AA: A9 01      LDA #$01      
    $C5AC: 8D B6 C5   STA $c5b6     
    $C5AF: 8D B7 C5   STA $c5b7     
    $C5B2: 8D B8 C5   STA $c5b8     
    $C5B5: 60         RTS           
; ----- data gap $C5B6-$C6DC (295 bytes) -----

L_C6DD:
    $C6DD: A9 00      LDA #$00      
    $C6DF: 8D 04 CB   STA $cb04     
    $C6E2: 20 EE C6   JSR $c6ee        ; → sub_C6EE
    $C6E5: EE 04 CB   INC $cb04     
    $C6E8: 20 EE C6   JSR $c6ee        ; → sub_C6EE
    $C6EB: EE 04 CB   INC $cb04     
sub_C6EE:
    $C6EE: AC 04 CB   LDY $cb04     
    $C6F1: BE FB CA   LDX $cafb,y   
    $C6F4: B9 6B C8   LDA $c86b,y   
    $C6F7: A8         TAY           
    $C6F8: B9 2D C9   LDA $c92d,y   
    $C6FB: 10 06      BPL $c703        ; → L_C703
    $C6FD: AD C1 C5   LDA $c5c1     
    $C700: 4A         LSR a         
    $C701: 90 0F      BCC $c712        ; → L_C712
L_C703:
    $C703: B9 2E C9   LDA $c92e,y   
    $C706: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $C709: B9 2F C9   LDA $c92f,y   
    $C70C: 9D 01 D4   STA $d401,x    ;V1_FREQ_HI,X
    $C70F: 4C 1E C7   JMP $c71e        ; → L_C71E
L_C712:
    $C712: B9 45 C9   LDA $c945,y   
    $C715: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $C718: B9 46 C9   LDA $c946,y   
    $C71B: 9D 01 D4   STA $d401,x    ;V1_FREQ_HI,X
L_C71E:
    $C71E: B9 37 C9   LDA $c937,y   
    $C721: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $C724: AC 04 CB   LDY $cb04     
    $C727: B9 01 CB   LDA $cb01,y   
    $C72A: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $C72D: B9 6B C8   LDA $c86b,y   
    $C730: A8         TAY           
    $C731: B9 41 C9   LDA $c941,y   
    $C734: 19 44 C9   ORA $c944,y   
    $C737: 9D 04 D4   STA $d404,x    ;V1_CTRL,X
    $C73A: B9 2D C9   LDA $c92d,y   
    $C73D: 4A         LSR a         
    $C73E: B0 70      BCS $c7b0        ; → L_C7B0
    $C740: B9 2E C9   LDA $c92e,y   
    $C743: 18         CLC           
    $C744: 79 34 C9   ADC $c934,y   
    $C747: 99 2E C9   STA $c92e,y   
    $C74A: B9 2F C9   LDA $c92f,y   
    $C74D: 79 35 C9   ADC $c935,y   
    $C750: 99 2F C9   STA $c92f,y   
    $C753: B9 2E C9   LDA $c92e,y   
    $C756: D9 30 C9   CMP $c930,y   
    $C759: B9 2F C9   LDA $c92f,y   
    $C75C: F9 31 C9   SBC $c931,y   
    $C75F: 90 1B      BCC $c77c        ; → L_C77C
    $C761: B9 2D C9   LDA $c92d,y   
    $C764: 29 02      AND #$02      
    $C766: F0 17      BEQ $c77f        ; → L_C77F
    $C768: B9 2D C9   LDA $c92d,y   
    $C76B: 49 01      EOR #$01      
    $C76D: 99 2D C9   STA $c92d,y   
L_C770:
    $C770: B9 30 C9   LDA $c930,y   
    $C773: 99 2E C9   STA $c92e,y   
    $C776: B9 31 C9   LDA $c931,y   
    $C779: 99 2F C9   STA $c92f,y   
L_C77C:
    $C77C: 4C E3 C7   JMP $c7e3        ; → L_C7E3
L_C77F:
    $C77F: B9 2D C9   LDA $c92d,y   
    $C782: 29 04      AND #$04      
    $C784: D0 0A      BNE $c790        ; → L_C790
    $C786: A9 00      LDA #$00      
    $C788: 99 34 C9   STA $c934,y   
    $C78B: 99 35 C9   STA $c935,y   
    $C78E: F0 53      BEQ $c7e3        ; → L_C7E3
L_C790:
    $C790: B9 32 C9   LDA $c932,y   
    $C793: 99 2E C9   STA $c92e,y   
    $C796: B9 33 C9   LDA $c933,y   
    $C799: 99 2F C9   STA $c92f,y   
    $C79C: 4C E3 C7   JMP $c7e3        ; → L_C7E3
L_C79F:
    $C79F: B9 2D C9   LDA $c92d,y   
    $C7A2: 29 04      AND #$04      
    $C7A4: D0 CA      BNE $c770        ; → L_C770
    $C7A6: A9 00      LDA #$00      
    $C7A8: 99 34 C9   STA $c934,y   
    $C7AB: 99 35 C9   STA $c935,y   
    $C7AE: F0 33      BEQ $c7e3        ; → L_C7E3
L_C7B0:
    $C7B0: B9 2E C9   LDA $c92e,y   
    $C7B3: 38         SEC           
    $C7B4: F9 34 C9   SBC $c934,y   
    $C7B7: 99 2E C9   STA $c92e,y   
    $C7BA: B9 2F C9   LDA $c92f,y   
    $C7BD: F9 35 C9   SBC $c935,y   
    $C7C0: 99 2F C9   STA $c92f,y   
    $C7C3: B9 2E C9   LDA $c92e,y   
    $C7C6: D9 32 C9   CMP $c932,y   
    $C7C9: B9 2F C9   LDA $c92f,y   
    $C7CC: F9 33 C9   SBC $c933,y   
    $C7CF: B0 12      BCS $c7e3        ; → L_C7E3
    $C7D1: B9 2D C9   LDA $c92d,y   
    $C7D4: 29 02      AND #$02      
    $C7D6: F0 C7      BEQ $c79f        ; → L_C79F
    $C7D8: B9 2D C9   LDA $c92d,y   
    $C7DB: 49 01      EOR #$01      
    $C7DD: 99 2D C9   STA $c92d,y   
    $C7E0: 4C 90 C7   JMP $c790        ; → L_C790
L_C7E3:
    $C7E3: AE 04 CB   LDX $cb04     
    $C7E6: BD FE CA   LDA $cafe,x   
    $C7E9: D0 3E      BNE $c829        ; → L_C829
    $C7EB: B9 3B C9   LDA $c93b,y   
    $C7EE: D0 1C      BNE $c80c        ; → L_C80C
    $C7F0: BD 01 CB   LDA $cb01,x   
    $C7F3: 18         CLC           
    $C7F4: 79 39 C9   ADC $c939,y   
    $C7F7: 9D 01 CB   STA $cb01,x   
    $C7FA: B9 37 C9   LDA $c937,y   
    $C7FD: 69 00      ADC #$00      
    $C7FF: 99 37 C9   STA $c937,y   
    $C802: D9 38 C9   CMP $c938,y   
    $C805: B0 01      BCS $c808        ; → L_C808
    $C807: 60         RTS           
L_C808:
    $C808: FE FE CA   INC $cafe,x   
    $C80B: 60         RTS           
L_C80C:
    $C80C: BD 01 CB   LDA $cb01,x   
    $C80F: 38         SEC           
    $C810: F9 39 C9   SBC $c939,y   
    $C813: 9D 01 CB   STA $cb01,x   
    $C816: B9 37 C9   LDA $c937,y   
    $C819: E9 00      SBC #$00      
    $C81B: 99 37 C9   STA $c937,y   
    $C81E: D9 38 C9   CMP $c938,y   
    $C821: F0 02      BEQ $c825        ; → L_C825
    $C823: B0 45      BCS $c86a        ; → L_C86A
L_C825:
    $C825: FE FE CA   INC $cafe,x   
    $C828: 60         RTS           
L_C829:
    $C829: B9 3C C9   LDA $c93c,y   
    $C82C: D0 1E      BNE $c84c        ; → L_C84C
    $C82E: BD 01 CB   LDA $cb01,x   
    $C831: 18         CLC           
    $C832: 79 3F C9   ADC $c93f,y   
    $C835: 9D 01 CB   STA $cb01,x   
    $C838: B9 37 C9   LDA $c937,y   
    $C83B: 69 00      ADC #$00      
    $C83D: 99 37 C9   STA $c937,y   
    $C840: D9 3D C9   CMP $c93d,y   
    $C843: 90 25      BCC $c86a        ; → L_C86A
    $C845: A9 01      LDA #$01      
    $C847: 99 3C C9   STA $c93c,y   
    $C84A: D0 1E      BNE $c86a        ; → L_C86A
L_C84C:
    $C84C: BD 01 CB   LDA $cb01,x   
    $C84F: 38         SEC           
    $C850: F9 3F C9   SBC $c93f,y   
    $C853: 9D 01 CB   STA $cb01,x   
    $C856: B9 37 C9   LDA $c937,y   
    $C859: E9 00      SBC #$00      
    $C85B: 99 37 C9   STA $c937,y   
    $C85E: D9 3E C9   CMP $c93e,y   
    $C861: F0 02      BEQ $c865        ; → L_C865
    $C863: B0 05      BCS $c86a        ; → L_C86A
L_C865:
    $C865: A9 00      LDA #$00      
    $C867: 99 3C C9   STA $c93c,y   
L_C86A:
    $C86A: 60         RTS           
; ----- data gap $C86B-$C86D (3 bytes) -----

sub_C86E:
    $C86E: 0A         ASL a         
    $C86F: A8         TAY           
    $C870: B9 FB C8   LDA $c8fb,y   
    $C873: 8D 8E C8   STA $c88e     
    $C876: B9 FC C8   LDA $c8fc,y   
    $C879: 8D 8F C8   STA $c88f     
    $C87C: 8A         TXA           
    $C87D: 0A         ASL a         
    $C87E: A8         TAY           
    $C87F: B9 1D C9   LDA $c91d,y   
    $C882: 8D 91 C8   STA $c891     
    $C885: B9 1E C9   LDA $c91e,y   
    $C888: 8D 92 C8   STA $c892     
    $C88B: A0 17      LDY #$17      
L_C88D:
    $C88D: B9 20 4E   LDA $4e20,y   
    $C890: 99 2D C9   STA $c92d,y   
    $C893: 88         DEY           
    $C894: 10 F7      BPL $c88d        ; → L_C88D
    $C896: A0 00      LDY #$00      
    $C898: B1 F2      LDA ($f2),y   
    $C89A: AA         TAX           
    $C89B: BD DD C5   LDA $c5dd,x   
    $C89E: A4 F5      LDY $f5       
    $C8A0: 99 2E C9   STA $c92e,y   
    $C8A3: 18         CLC           
    $C8A4: 79 30 C9   ADC $c930,y   
    $C8A7: 99 30 C9   STA $c930,y   
    $C8AA: BD 5D C6   LDA $c65d,x   
    $C8AD: 99 2F C9   STA $c92f,y   
    $C8B0: 18         CLC           
    $C8B1: 79 31 C9   ADC $c931,y   
    $C8B4: 99 31 C9   STA $c931,y   
    $C8B7: B9 2E C9   LDA $c92e,y   
    $C8BA: 38         SEC           
    $C8BB: F9 32 C9   SBC $c932,y   
    $C8BE: 99 32 C9   STA $c932,y   
    $C8C1: B9 2F C9   LDA $c92f,y   
    $C8C4: F9 33 C9   SBC $c933,y   
    $C8C7: 99 33 C9   STA $c933,y   
    $C8CA: 8A         TXA           
    $C8CB: 18         CLC           
    $C8CC: 69 10      ADC #$10      
    $C8CE: AA         TAX           
    $C8CF: BD DD C5   LDA $c5dd,x   
    $C8D2: 99 45 C9   STA $c945,y   
    $C8D5: BD 5D C6   LDA $c65d,x   
    $C8D8: 99 46 C9   STA $c946,y   
    $C8DB: B9 41 C9   LDA $c941,y   
    $C8DE: A6 F4      LDX $f4       
    $C8E0: 9D BE C5   STA $c5be,x   
    $C8E3: A9 00      LDA #$00      
    $C8E5: 9D FE CA   STA $cafe,x   
    $C8E8: 9D 01 CB   STA $cb01,x   
    $C8EB: BC FB CA   LDY $cafb,x   
    $C8EE: A6 F5      LDX $f5       
    $C8F0: BD 42 C9   LDA $c942,x   
    $C8F3: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $C8F6: BD 43 C9   LDA $c943,x   
    $C8F9: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $C8FC: 60         RTS           
; ----- data gap $C8FD-$CAFF (515 bytes) -----

