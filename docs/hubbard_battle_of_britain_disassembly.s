; ============================================================================
; Rob Hubbard - Battle of Britain (1985 Personal Software Services)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: demo/hubbard/Battle_of_Britain_original.sid
; Load:   $8000   Init: $8EAA   Play: $8006
; PSID:   1 subtune(s), default subtune 1
; Binary: $8000-$8FFF (4096 bytes)
;
; Auto-traced 828 reachable code bytes from init+play.
;
; ============================================================================

; ----- data gap $8000-$8005 (6 bytes) -----

; ======= play: =======
play:
    $8006: EE 1F 84   INC $841f     
    $8009: A2 02      LDX #$02      
    $800B: CE 11 84   DEC $8411     
    $800E: 10 06      BPL $8016        ; → L_8016
    $8010: AD 12 84   LDA $8412     
    $8013: 8D 11 84   STA $8411     
L_8016:
    $8016: BD E6 83   LDA $83e6,x   
    $8019: 8D E9 83   STA $83e9     
    $801C: A8         TAY           
    $801D: AD 11 84   LDA $8411     
    $8020: CD 12 84   CMP $8412     
    $8023: D0 15      BNE $803a        ; → L_803A
    $8025: BD B8 84   LDA $84b8,x   
    $8028: 85 FB      STA $fb       
    $802A: BD BB 84   LDA $84bb,x   
    $802D: 85 FC      STA $fc       
    $802F: DE F0 83   DEC $83f0,x   
    $8032: 30 09      BMI $803d        ; → L_803D
    $8034: 4C 17 81   JMP $8117        ; → L_8117
; ----- data gap $8037-$8039 (3 bytes) -----

L_803A:
    $803A: 4C 36 81   JMP $8136        ; → L_8136
L_803D:
    $803D: BC EA 83   LDY $83ea,x   
    $8040: B1 FB      LDA ($fb),y   
    $8042: C9 FF      CMP #$ff      
    $8044: D0 11      BNE $8057        ; → L_8057
    $8046: A9 00      LDA #$00      
    $8048: 9D F0 83   STA $83f0,x   
    $804B: 9D EA 83   STA $83ea,x   
    $804E: 9D ED 83   STA $83ed,x   
    $8051: 4C 3D 80   JMP $803d        ; → L_803D
; ----- data gap $8054-$8056 (3 bytes) -----

L_8057:
    $8057: A8         TAY           
    $8058: B9 BE 84   LDA $84be,y   
    $805B: 85 FD      STA $fd       
    $805D: B9 E8 84   LDA $84e8,y   
    $8060: 85 FE      STA $fe       
    $8062: BC ED 83   LDY $83ed,x   
    $8065: A9 FF      LDA #$ff      
    $8067: 8D FF 83   STA $83ff     
    $806A: B1 FD      LDA ($fd),y   
    $806C: 9D F3 83   STA $83f3,x   
    $806F: 8D 00 84   STA $8400     
    $8072: 29 1F      AND #$1f      
    $8074: 9D F0 83   STA $83f0,x   
    $8077: 2C 00 84   BIT $8400     
    $807A: 70 44      BVS $80c0        ; → L_80C0
    $807C: A9 00      LDA #$00      
    $807E: 9D 1A 84   STA $841a,x   
    $8081: FE ED 83   INC $83ed,x   
    $8084: AD 00 84   LDA $8400     
    $8087: 10 11      BPL $809a        ; → L_809A
    $8089: C8         INY           
    $808A: B1 FD      LDA ($fd),y   
    $808C: 10 06      BPL $8094        ; → L_8094
    $808E: 9D 1A 84   STA $841a,x   
    $8091: 4C 97 80   JMP $8097        ; → L_8097
L_8094:
    $8094: 9D FC 83   STA $83fc,x   
L_8097:
    $8097: FE ED 83   INC $83ed,x   
L_809A:
    $809A: C8         INY           
    $809B: B1 FD      LDA ($fd),y   
    $809D: 9D F9 83   STA $83f9,x   
    $80A0: 0A         ASL a         
    $80A1: A8         TAY           
    $80A2: B9 26 83   LDA $8326,y   
    $80A5: 8D 01 84   STA $8401     
    $80A8: B9 27 83   LDA $8327,y   
    $80AB: AC E9 83   LDY $83e9     
    $80AE: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $80B1: 9D 14 84   STA $8414,x   
    $80B4: AD 01 84   LDA $8401     
    $80B7: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $80BA: 9D 17 84   STA $8417,x   
    $80BD: 4C C3 80   JMP $80c3        ; → L_80C3
L_80C0:
    $80C0: CE FF 83   DEC $83ff     
L_80C3:
    $80C3: AC E9 83   LDY $83e9     
    $80C6: BD FC 83   LDA $83fc,x   
    $80C9: 8E 02 84   STX $8402     
    $80CC: 0A         ASL a         
    $80CD: 0A         ASL a         
    $80CE: 0A         ASL a         
    $80CF: AA         TAX           
    $80D0: BD 22 84   LDA $8422,x   
    $80D3: 8D 03 84   STA $8403     
    $80D6: BD 22 84   LDA $8422,x   
    $80D9: 2D FF 83   AND $83ff     
    $80DC: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $80DF: BD 20 84   LDA $8420,x   
    $80E2: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $80E5: BD 21 84   LDA $8421,x   
    $80E8: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $80EB: BD 23 84   LDA $8423,x   
    $80EE: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $80F1: BD 24 84   LDA $8424,x   
    $80F4: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $80F7: AE 02 84   LDX $8402     
    $80FA: AD 03 84   LDA $8403     
    $80FD: 9D F6 83   STA $83f6,x   
    $8100: FE ED 83   INC $83ed,x   
    $8103: BC ED 83   LDY $83ed,x   
    $8106: B1 FD      LDA ($fd),y   
    $8108: C9 FF      CMP #$ff      
    $810A: D0 08      BNE $8114        ; → L_8114
    $810C: A9 00      LDA #$00      
    $810E: 9D ED 83   STA $83ed,x   
    $8111: FE EA 83   INC $83ea,x   
L_8114:
    $8114: 4C 1F 83   JMP $831f        ; → L_831F
L_8117:
    $8117: AC E9 83   LDY $83e9     
    $811A: BD F3 83   LDA $83f3,x   
    $811D: 29 20      AND #$20      
    $811F: D0 15      BNE $8136        ; → L_8136
    $8121: BD F0 83   LDA $83f0,x   
    $8124: D0 10      BNE $8136        ; → L_8136
    $8126: BD F6 83   LDA $83f6,x   
    $8129: 29 FE      AND #$fe      
    $812B: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $812E: A9 00      LDA #$00      
    $8130: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $8133: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_8136:
    $8136: BD FC 83   LDA $83fc,x   
    $8139: 0A         ASL a         
    $813A: 0A         ASL a         
    $813B: 0A         ASL a         
    $813C: A8         TAY           
    $813D: 8C 13 84   STY $8413     
    $8140: B9 27 84   LDA $8427,y   
    $8143: 8D 1D 84   STA $841d     
    $8146: B9 26 84   LDA $8426,y   
    $8149: 8D 05 84   STA $8405     
    $814C: B9 25 84   LDA $8425,y   
    $814F: 8D 04 84   STA $8404     
    $8152: F0 6F      BEQ $81c3        ; → L_81C3
    $8154: AD 1F 84   LDA $841f     
    $8157: 29 07      AND #$07      
    $8159: C9 04      CMP #$04      
    $815B: 90 02      BCC $815f        ; → L_815F
    $815D: 49 07      EOR #$07      
L_815F:
    $815F: 8D 0A 84   STA $840a     
    $8162: BD F9 83   LDA $83f9,x   
    $8165: 0A         ASL a         
    $8166: A8         TAY           
    $8167: 38         SEC           
    $8168: B9 28 83   LDA $8328,y   
    $816B: F9 26 83   SBC $8326,y   
    $816E: 8D 06 84   STA $8406     
    $8171: B9 29 83   LDA $8329,y   
    $8174: F9 27 83   SBC $8327,y   
L_8177:
    $8177: 4A         LSR a         
    $8178: 6E 06 84   ROR $8406     
    $817B: CE 04 84   DEC $8404     
    $817E: 10 F7      BPL $8177        ; → L_8177
    $8180: 8D 07 84   STA $8407     
    $8183: B9 26 83   LDA $8326,y   
    $8186: 8D 08 84   STA $8408     
    $8189: B9 27 83   LDA $8327,y   
    $818C: 8D 09 84   STA $8409     
    $818F: BD F3 83   LDA $83f3,x   
    $8192: 29 1F      AND #$1f      
    $8194: C9 08      CMP #$08      
    $8196: 90 1C      BCC $81b4        ; → L_81B4
    $8198: AC 0A 84   LDY $840a     
L_819B:
    $819B: 88         DEY           
    $819C: 30 16      BMI $81b4        ; → L_81B4
    $819E: 18         CLC           
    $819F: AD 08 84   LDA $8408     
    $81A2: 6D 06 84   ADC $8406     
    $81A5: 8D 08 84   STA $8408     
    $81A8: AD 09 84   LDA $8409     
    $81AB: 6D 07 84   ADC $8407     
    $81AE: 8D 09 84   STA $8409     
    $81B1: 4C 9B 81   JMP $819b        ; → L_819B
L_81B4:
    $81B4: AC E9 83   LDY $83e9     
    $81B7: AD 08 84   LDA $8408     
    $81BA: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $81BD: AD 09 84   LDA $8409     
    $81C0: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_81C3:
    $81C3: AD 1D 84   LDA $841d     
    $81C6: 29 08      AND #$08      
    $81C8: F0 15      BEQ $81df        ; → L_81DF
    $81CA: AC 13 84   LDY $8413     
    $81CD: B9 20 84   LDA $8420,y   
    $81D0: 6D 05 84   ADC $8405     
    $81D3: 99 20 84   STA $8420,y   
    $81D6: AC E9 83   LDY $83e9     
    $81D9: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $81DC: 4C 46 82   JMP $8246        ; → L_8246
L_81DF:
    $81DF: AD 05 84   LDA $8405     
    $81E2: F0 62      BEQ $8246        ; → L_8246
    $81E4: AC 13 84   LDY $8413     
    $81E7: 29 1F      AND #$1f      
    $81E9: DE 0B 84   DEC $840b,x   
    $81EC: 10 58      BPL $8246        ; → L_8246
    $81EE: 9D 0B 84   STA $840b,x   
    $81F1: AD 05 84   LDA $8405     
    $81F4: 29 E0      AND #$e0      
    $81F6: 8D 1E 84   STA $841e     
    $81F9: BD 0E 84   LDA $840e,x   
    $81FC: D0 1A      BNE $8218        ; → L_8218
    $81FE: AD 1E 84   LDA $841e     
    $8201: 18         CLC           
    $8202: 79 20 84   ADC $8420,y   
    $8205: 48         PHA           
    $8206: B9 21 84   LDA $8421,y   
    $8209: 69 00      ADC #$00      
    $820B: 29 0F      AND #$0f      
    $820D: 48         PHA           
    $820E: C9 0E      CMP #$0e      
    $8210: D0 1D      BNE $822f        ; → L_822F
    $8212: FE 0E 84   INC $840e,x   
    $8215: 4C 2F 82   JMP $822f        ; → L_822F
L_8218:
    $8218: 38         SEC           
    $8219: B9 20 84   LDA $8420,y   
    $821C: ED 1E 84   SBC $841e     
    $821F: 48         PHA           
    $8220: B9 21 84   LDA $8421,y   
    $8223: E9 00      SBC #$00      
    $8225: 29 0F      AND #$0f      
    $8227: 48         PHA           
    $8228: C9 08      CMP #$08      
    $822A: D0 03      BNE $822f        ; → L_822F
    $822C: DE 0E 84   DEC $840e,x   
L_822F:
    $822F: 8E 02 84   STX $8402     
    $8232: AE E9 83   LDX $83e9     
    $8235: 68         PLA           
    $8236: 99 21 84   STA $8421,y   
    $8239: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $823C: 68         PLA           
    $823D: 99 20 84   STA $8420,y   
    $8240: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $8243: AE 02 84   LDX $8402     
L_8246:
    $8246: AC E9 83   LDY $83e9     
    $8249: BD 1A 84   LDA $841a,x   
    $824C: F0 3F      BEQ $828d        ; → L_828D
    $824E: 29 7E      AND #$7e      
    $8250: 8D 02 84   STA $8402     
    $8253: BD 1A 84   LDA $841a,x   
    $8256: 29 01      AND #$01      
    $8258: F0 1B      BEQ $8275        ; → L_8275
    $825A: 38         SEC           
    $825B: BD 17 84   LDA $8417,x   
    $825E: ED 02 84   SBC $8402     
    $8261: 9D 17 84   STA $8417,x   
    $8264: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $8267: BD 14 84   LDA $8414,x   
    $826A: E9 00      SBC #$00      
    $826C: 9D 14 84   STA $8414,x   
    $826F: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $8272: 4C 8D 82   JMP $828d        ; → L_828D
L_8275:
    $8275: 18         CLC           
    $8276: BD 17 84   LDA $8417,x   
    $8279: 6D 02 84   ADC $8402     
    $827C: 9D 17 84   STA $8417,x   
    $827F: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $8282: BD 14 84   LDA $8414,x   
    $8285: 69 00      ADC #$00      
    $8287: 9D 14 84   STA $8414,x   
    $828A: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_828D:
    $828D: AD 1D 84   LDA $841d     
    $8290: 29 01      AND #$01      
    $8292: F0 35      BEQ $82c9        ; → L_82C9
    $8294: BD 14 84   LDA $8414,x   
    $8297: F0 30      BEQ $82c9        ; → L_82C9
    $8299: BD F0 83   LDA $83f0,x   
    $829C: F0 2B      BEQ $82c9        ; → L_82C9
    $829E: BD F3 83   LDA $83f3,x   
    $82A1: 29 1F      AND #$1f      
    $82A3: 38         SEC           
    $82A4: E9 01      SBC #$01      
    $82A6: DD F0 83   CMP $83f0,x   
    $82A9: AC E9 83   LDY $83e9     
    $82AC: 90 10      BCC $82be        ; → L_82BE
    $82AE: BD 14 84   LDA $8414,x   
    $82B1: DE 14 84   DEC $8414,x   
    $82B4: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $82B7: BD F6 83   LDA $83f6,x   
    $82BA: 29 FE      AND #$fe      
    $82BC: D0 08      BNE $82c6        ; → L_82C6
L_82BE:
    $82BE: BD 14 84   LDA $8414,x   
    $82C1: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $82C4: A9 80      LDA #$80      
L_82C6:
    $82C6: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_82C9:
    $82C9: AD 1D 84   LDA $841d     
    $82CC: 29 02      AND #$02      
    $82CE: F0 1E      BEQ $82ee        ; → L_82EE
    $82D0: BD F3 83   LDA $83f3,x   
    $82D3: 29 1F      AND #$1f      
    $82D5: C9 0C      CMP #$0c      
    $82D7: 90 15      BCC $82ee        ; → L_82EE
    $82D9: AD 1F 84   LDA $841f     
    $82DC: 29 01      AND #$01      
    $82DE: F0 0E      BEQ $82ee        ; → L_82EE
    $82E0: BD 14 84   LDA $8414,x   
    $82E3: F0 09      BEQ $82ee        ; → L_82EE
    $82E5: DE 14 84   DEC $8414,x   
    $82E8: AC E9 83   LDY $83e9     
    $82EB: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_82EE:
    $82EE: AD 1D 84   LDA $841d     
    $82F1: 29 04      AND #$04      
    $82F3: F0 2A      BEQ $831f        ; → L_831F
    $82F5: AD 1F 84   LDA $841f     
    $82F8: 29 07      AND #$07      
    $82FA: F0 09      BEQ $8305        ; → L_8305
    $82FC: BD F9 83   LDA $83f9,x   
    $82FF: 18         CLC           
    $8300: 69 0C      ADC #$0c      
    $8302: 4C 08 83   JMP $8308        ; → L_8308
L_8305:
    $8305: BD F9 83   LDA $83f9,x   
L_8308:
    $8308: 0A         ASL a         
    $8309: A8         TAY           
    $830A: B9 26 83   LDA $8326,y   
    $830D: 8D 01 84   STA $8401     
    $8310: B9 27 83   LDA $8327,y   
    $8313: AC E9 83   LDY $83e9     
    $8316: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $8319: AD 01 84   LDA $8401     
    $831C: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_831F:
    $831F: CA         DEX           
    $8320: 30 03      BMI $8325        ; → L_8325
    $8322: 4C 16 80   JMP $8016        ; → L_8016
L_8325:
    $8325: 60         RTS           
; ----- data gap $8326-$8EA9 (2948 bytes) -----

; ======= init: =======
init:
    $8EAA: A9 00      LDA #$00      
    $8EAC: A2 02      LDX #$02      
L_8EAE:
    $8EAE: 9D EA 83   STA $83ea,x   
    $8EB1: 9D ED 83   STA $83ed,x   
    $8EB4: 9D F0 83   STA $83f0,x   
    $8EB7: 9D F9 83   STA $83f9,x   
    $8EBA: CA         DEX           
    $8EBB: 10 F1      BPL $8eae        ; → L_8EAE
    $8EBD: 8D 04 D4   STA $d404      ;V1_CTRL
    $8EC0: 8D 0B D4   STA $d40b      ;V2_CTRL
    $8EC3: 8D 12 D4   STA $d412      ;V3_CTRL
    $8EC6: A9 0F      LDA #$0f      
    $8EC8: 8D 18 D4   STA $d418      ;VOL
    $8ECB: 60         RTS           
; ----- data gap $8ECC-$8FFF (308 bytes) -----

