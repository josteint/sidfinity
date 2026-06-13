; ============================================================================
; Rob Hubbard - HT 7.1 (1996 Snake)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/W/Wodnik/HT_7_1.sid
; Load:   $1000   Init: $1000   Play: $1003
; PSID:   1 subtune(s), default subtune 1
; Binary: $1000-$20E7 (4328 bytes)
;
; Auto-traced 1326 reachable code bytes from init+play.
;
; ============================================================================

; ======= init: =======
init:
    $1000: 4C 60 10   JMP $1060        ; → L_1060
; ======= play: =======
play:
    $1003: 4C D8 10   JMP $10d8        ; → L_10D8
; ----- data gap $1006-$105F (90 bytes) -----

L_1060:
    $1060: 29 07      AND #$07      
    $1062: AA         TAX           
    $1063: BD A2 18   LDA $18a2,x   
    $1066: 8D 0A 10   STA $100a     
    $1069: BD BA 18   LDA $18ba,x   
    $106C: 8D 0D 10   STA $100d     
    $106F: BD AA 18   LDA $18aa,x   
    $1072: 8D 0B 10   STA $100b     
    $1075: BD C2 18   LDA $18c2,x   
    $1078: 8D 0E 10   STA $100e     
    $107B: BD B2 18   LDA $18b2,x   
    $107E: 8D 0C 10   STA $100c     
    $1081: BD CA 18   LDA $18ca,x   
    $1084: 8D 0F 10   STA $100f     
    $1087: BD C4 16   LDA $16c4,x   
    $108A: 8D E4 10   STA $10e4     
    $108D: A9 0F      LDA #$0f      
    $108F: 8D 06 10   STA $1006     
    $1092: A9 00      LDA #$00      
    $1094: AA         TAX           
L_1095:
    $1095: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $1098: E8         INX           
    $1099: E0 1D      CPX #$1d      
    $109B: D0 F8      BNE $1095        ; → L_1095
    $109D: A2 00      LDX #$00      
L_109F:
    $109F: A9 00      LDA #$00      
    $10A1: 9D 19 10   STA $1019,x   
    $10A4: 9D 16 10   STA $1016,x   
    $10A7: 9D AF 16   STA $16af,x   
    $10AA: 9D A3 16   STA $16a3,x   
    $10AD: 9D 9D 16   STA $169d,x   
    $10B0: 9D 97 16   STA $1697,x   
    $10B3: 9D BE 16   STA $16be,x   
    $10B6: A9 F5      LDA #$f5      
    $10B8: 9D 10 10   STA $1010,x   
    $10BB: A9 11      LDA #$11      
    $10BD: 9D 13 10   STA $1013,x   
    $10C0: A9 FE      LDA #$fe      
    $10C2: 9D 9A 16   STA $169a,x   
    $10C5: A9 01      LDA #$01      
    $10C7: 9D C1 16   STA $16c1,x   
    $10CA: 9D 8E 16   STA $168e,x   
    $10CD: E8         INX           
    $10CE: E0 03      CPX #$03      
    $10D0: D0 CD      BNE $109f        ; → L_109F
    $10D2: A8         TAY           
    $10D3: C8         INY           
    $10D4: 8C FB 10   STY $10fb     
    $10D7: 60         RTS           
L_10D8:
    $10D8: A5 FB      LDA $fb       
    $10DA: 48         PHA           
    $10DB: A5 FC      LDA $fc       
    $10DD: 48         PHA           
    $10DE: CE FB 10   DEC $10fb     
    $10E1: 10 05      BPL $10e8        ; → L_10E8
    $10E3: A9 03      LDA #$03      
    $10E5: 8D FB 10   STA $10fb     
L_10E8:
    $10E8: A2 02      LDX #$02      
L_10EA:
    $10EA: BD A3 16   LDA $16a3,x   
    $10ED: F0 03      BEQ $10f2        ; → L_10F2
    $10EF: 4C 40 15   JMP $1540        ; → L_1540
L_10F2:
    $10F2: BD AF 16   LDA $16af,x   
    $10F5: F0 03      BEQ $10fa        ; → L_10FA
    $10F7: 4C 72 12   JMP $1272        ; → L_1272
L_10FA:
    $10FA: A9 02      LDA #$02      
    $10FC: F0 0A      BEQ $1108        ; → L_1108
    $10FE: C9 01      CMP #$01      
    $1100: D0 03      BNE $1105        ; → L_1105
    $1102: 4C DD 11   JMP $11dd        ; → L_11DD
L_1105:
    $1105: 4C CE 12   JMP $12ce        ; → L_12CE
L_1108:
    $1108: BD 10 10   LDA $1010,x   
    $110B: 85 FB      STA $fb       
    $110D: BD 13 10   LDA $1013,x   
    $1110: 85 FC      STA $fc       
    $1112: BC 19 10   LDY $1019,x   
    $1115: BD 60 16   LDA $1660,x   
    $1118: C9 60      CMP #$60      
    $111A: D0 03      BNE $111f        ; → L_111F
    $111C: 4C 7A 11   JMP $117a        ; → L_117A
L_111F:
    $111F: C9 61      CMP #$61      
    $1121: D0 08      BNE $112b        ; → L_112B
    $1123: A9 FE      LDA #$fe      
    $1125: 9D 9A 16   STA $169a,x   
    $1128: 4C 7A 11   JMP $117a        ; → L_117A
L_112B:
    $112B: C9 62      CMP #$62      
    $112D: D0 13      BNE $1142        ; → L_1142
    $112F: A9 00      LDA #$00      
    $1131: 9D 5A 16   STA $165a,x   
    $1134: BC A0 16   LDY $16a0,x   
    $1137: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $113A: A9 01      LDA #$01      
    $113C: 9D 8E 16   STA $168e,x   
    $113F: 4C 7A 11   JMP $117a        ; → L_117A
L_1142:
    $1142: C9 63      CMP #$63      
    $1144: D0 15      BNE $115b        ; → L_115B
    $1146: A9 01      LDA #$01      
    $1148: 9D 63 16   STA $1663,x   
    $114B: A9 00      LDA #$00      
    $114D: 9D 66 16   STA $1666,x   
    $1150: FE 19 10   INC $1019,x   
    $1153: B1 FB      LDA ($fb),y   
    $1155: 9D 69 16   STA $1669,x   
    $1158: 4C B7 13   JMP $13b7        ; → L_13B7
L_115B:
    $115B: C9 64      CMP #$64      
    $115D: D0 13      BNE $1172        ; → L_1172
    $115F: A9 01      LDA #$01      
    $1161: 9D 63 16   STA $1663,x   
    $1164: 9D 66 16   STA $1666,x   
    $1167: FE 19 10   INC $1019,x   
    $116A: B1 FB      LDA ($fb),y   
    $116C: 9D 69 16   STA $1669,x   
    $116F: 4C B7 13   JMP $13b7        ; → L_13B7
L_1172:
    $1172: 29 7F      AND #$7f      
    $1174: 9D 1C 10   STA $101c,x   
    $1177: 9D AF 16   STA $16af,x   
L_117A:
    $117A: BC 19 10   LDY $1019,x   
    $117D: FE 19 10   INC $1019,x   
    $1180: B1 FB      LDA ($fb),y   
    $1182: F0 17      BEQ $119b        ; → L_119B
    $1184: C9 6F      CMP #$6f      
    $1186: D0 06      BNE $118e        ; → L_118E
    $1188: 9D 85 16   STA $1685,x   
    $118B: 4C B7 13   JMP $13b7        ; → L_13B7
L_118E:
    $118E: 29 1F      AND #$1f      
    $1190: 48         PHA           
    $1191: BD BE 16   LDA $16be,x   
    $1194: 9D C1 16   STA $16c1,x   
    $1197: 68         PLA           
    $1198: 9D BE 16   STA $16be,x   
L_119B:
    $119B: A9 00      LDA #$00      
    $119D: 9D 85 16   STA $1685,x   
    $11A0: BD AF 16   LDA $16af,x   
    $11A3: D0 03      BNE $11a8        ; → L_11A8
    $11A5: 4C B7 13   JMP $13b7        ; → L_13B7
L_11A8:
    $11A8: BC BE 16   LDY $16be,x   
    $11AB: B9 6C 17   LDA $176c,y   
    $11AE: 29 03      AND #$03      
    $11B0: 48         PHA           
    $11B1: BD 8B 16   LDA $168b,x   
    $11B4: 9D 88 16   STA $1688,x   
    $11B7: 68         PLA           
    $11B8: 9D 8B 16   STA $168b,x   
    $11BB: BD 88 16   LDA $1688,x   
    $11BE: C9 02      CMP #$02      
    $11C0: F0 08      BEQ $11ca        ; → L_11CA
    $11C2: A9 FE      LDA #$fe      
    $11C4: 9D 9A 16   STA $169a,x   
    $11C7: 4C B7 13   JMP $13b7        ; → L_13B7
L_11CA:
    $11CA: BC A0 16   LDY $16a0,x   
    $11CD: A9 00      LDA #$00      
    $11CF: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $11D2: BD 5A 16   LDA $165a,x   
    $11D5: 29 FE      AND #$fe      
    $11D7: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $11DA: 4C 40 15   JMP $1540        ; → L_1540
L_11DD:
    $11DD: A9 00      LDA #$00      
    $11DF: 9D 5D 16   STA $165d,x   
    $11E2: BD 10 10   LDA $1010,x   
    $11E5: 85 FB      STA $fb       
    $11E7: BD 13 10   LDA $1013,x   
    $11EA: 85 FC      STA $fc       
    $11EC: BC 19 10   LDY $1019,x   
    $11EF: FE 19 10   INC $1019,x   
    $11F2: B1 FB      LDA ($fb),y   
    $11F4: C9 FF      CMP #$ff      
    $11F6: F0 06      BEQ $11fe        ; → L_11FE
    $11F8: 9D 60 16   STA $1660,x   
    $11FB: 4C CE 12   JMP $12ce        ; → L_12CE
L_11FE:
    $11FE: A9 00      LDA #$00      
    $1200: 9D 19 10   STA $1019,x   
    $1203: BD 0A 10   LDA $100a,x   
    $1206: 85 FB      STA $fb       
    $1208: BD 0D 10   LDA $100d,x   
    $120B: 85 FC      STA $fc       
L_120D:
    $120D: BC 16 10   LDY $1016,x   
    $1210: FE 16 10   INC $1016,x   
    $1213: B1 FB      LDA ($fb),y   
    $1215: 10 38      BPL $124f        ; → L_124F
    $1217: C9 FF      CMP #$ff      
    $1219: D0 0A      BNE $1225        ; → L_1225
    $121B: 9D 5D 16   STA $165d,x   
    $121E: A9 00      LDA #$00      
    $1220: 9D 16 10   STA $1016,x   
    $1223: F0 E8      BEQ $120d        ; → L_120D
L_1225:
    $1225: C9 FE      CMP #$fe      
    $1227: D0 08      BNE $1231        ; → L_1231
    $1229: A9 01      LDA #$01      
    $122B: 9D A3 16   STA $16a3,x   
    $122E: 4C 40 15   JMP $1540        ; → L_1540
L_1231:
    $1231: C9 FD      CMP #$fd      
    $1233: D0 0F      BNE $1244        ; → L_1244
    $1235: 9D 5D 16   STA $165d,x   
    $1238: C8         INY           
    $1239: FE 16 10   INC $1016,x   
    $123C: B1 FB      LDA ($fb),y   
    $123E: 9D 16 10   STA $1016,x   
    $1241: 4C 0D 12   JMP $120d        ; → L_120D
L_1244:
    $1244: 29 7F      AND #$7f      
    $1246: 9D 9D 16   STA $169d,x   
    $1249: C8         INY           
    $124A: FE 16 10   INC $1016,x   
    $124D: B1 FB      LDA ($fb),y   
L_124F:
    $124F: A8         TAY           
    $1250: B9 4A 19   LDA $194a,y   
    $1253: 9D 10 10   STA $1010,x   
    $1256: 85 FB      STA $fb       
    $1258: B9 5F 19   LDA $195f,y   
    $125B: 9D 13 10   STA $1013,x   
    $125E: 85 FC      STA $fc       
    $1260: A0 00      LDY #$00      
    $1262: FE 19 10   INC $1019,x   
    $1265: B1 FB      LDA ($fb),y   
    $1267: 9D 60 16   STA $1660,x   
    $126A: BD 5D 16   LDA $165d,x   
    $126D: D0 5C      BNE $12cb        ; → L_12CB
    $126F: 4C CE 12   JMP $12ce        ; → L_12CE
L_1272:
    $1272: A9 01      LDA #$01      
    $1274: 9D 97 16   STA $1697,x   
    $1277: A9 00      LDA #$00      
    $1279: 9D AF 16   STA $16af,x   
    $127C: BC BE 16   LDY $16be,x   
    $127F: B9 CC 17   LDA $17cc,y   
    $1282: 48         PHA           
    $1283: 29 0F      AND #$0f      
    $1285: 9D 79 16   STA $1679,x   
    $1288: 9D B5 16   STA $16b5,x   
    $128B: A9 01      LDA #$01      
    $128D: 9D A6 16   STA $16a6,x   
    $1290: 68         PLA           
    $1291: 29 F0      AND #$f0      
    $1293: 4A         LSR a         
    $1294: 4A         LSR a         
    $1295: 4A         LSR a         
    $1296: 9D B2 16   STA $16b2,x   
    $1299: B9 EC 17   LDA $17ec,y   
    $129C: 9D BB 16   STA $16bb,x   
    $129F: B9 0C 18   LDA $180c,y   
    $12A2: 9D 7F 16   STA $167f,x   
    $12A5: B9 2C 18   LDA $182c,y   
    $12A8: 9D 82 16   STA $1682,x   
    $12AB: BD 85 16   LDA $1685,x   
    $12AE: F0 03      BEQ $12b3        ; → L_12B3
    $12B0: 4C B7 13   JMP $13b7        ; → L_13B7
L_12B3:
    $12B3: BD 88 16   LDA $1688,x   
    $12B6: D0 03      BNE $12bb        ; → L_12BB
    $12B8: 4C B7 13   JMP $13b7        ; → L_13B7
L_12BB:
    $12BB: BC A0 16   LDY $16a0,x   
    $12BE: A9 00      LDA #$00      
    $12C0: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $12C3: BD 5A 16   LDA $165a,x   
    $12C6: 29 FE      AND #$fe      
    $12C8: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_12CB:
    $12CB: 4C 40 15   JMP $1540        ; → L_1540
L_12CE:
    $12CE: BD 97 16   LDA $1697,x   
    $12D1: D0 03      BNE $12d6        ; → L_12D6
    $12D3: 4C B7 13   JMP $13b7        ; → L_13B7
L_12D6:
    $12D6: A9 00      LDA #$00      
    $12D8: 9D 97 16   STA $1697,x   
    $12DB: 9D B8 16   STA $16b8,x   
    $12DE: 9D 6C 16   STA $166c,x   
    $12E1: 9D 63 16   STA $1663,x   
    $12E4: A9 FF      LDA #$ff      
    $12E6: 9D 9A 16   STA $169a,x   
    $12E9: BD 1C 10   LDA $101c,x   
    $12EC: 18         CLC           
    $12ED: 7D 9D 16   ADC $169d,x   
    $12F0: 29 7F      AND #$7f      
    $12F2: 9D 07 10   STA $1007,x   
    $12F5: A8         TAY           
    $12F6: B9 E8 15   LDA $15e8,y   
    $12F9: 9D 4E 16   STA $164e,x   
    $12FC: B9 88 15   LDA $1588,y   
    $12FF: 9D 51 16   STA $1651,x   
    $1302: BD 85 16   LDA $1685,x   
    $1305: F0 03      BEQ $130a        ; → L_130A
    $1307: 4C B7 13   JMP $13b7        ; → L_13B7
L_130A:
    $130A: BC BE 16   LDY $16be,x   
    $130D: B9 CC 16   LDA $16cc,y   
    $1310: 9D 48 16   STA $1648,x   
    $1313: B9 EC 16   LDA $16ec,y   
    $1316: 9D 4B 16   STA $164b,x   
    $1319: B9 6C 17   LDA $176c,y   
    $131C: 29 80      AND #$80      
    $131E: 9D 76 16   STA $1676,x   
    $1321: B9 0C 17   LDA $170c,y   
    $1324: 48         PHA           
    $1325: 29 0F      AND #$0f      
    $1327: 9D 57 16   STA $1657,x   
    $132A: 68         PLA           
    $132B: 29 F0      AND #$f0      
    $132D: 9D 54 16   STA $1654,x   
    $1330: B9 4C 17   LDA $174c,y   
    $1333: 9D AC 16   STA $16ac,x   
    $1336: B9 2C 17   LDA $172c,y   
    $1339: 9D 7C 16   STA $167c,x   
    $133C: A9 00      LDA #$00      
    $133E: 9D 8E 16   STA $168e,x   
    $1341: 9D 70 16   STA $1670,x   
    $1344: A9 02      LDA #$02      
    $1346: 9D 73 16   STA $1673,x   
    $1349: B9 6C 17   LDA $176c,y   
    $134C: 29 10      AND #$10      
    $134E: F0 08      BEQ $1358        ; → L_1358
    $1350: BD BE 16   LDA $16be,x   
    $1353: DD C1 16   CMP $16c1,x   
    $1356: F0 48      BEQ $13a0        ; → L_13A0
L_1358:
    $1358: B9 4C 18   LDA $184c,y   
    $135B: F0 37      BEQ $1394        ; → L_1394
    $135D: 48         PHA           
    $135E: 29 0F      AND #$0f      
    $1360: 0A         ASL a         
    $1361: 0A         ASL a         
    $1362: 0A         ASL a         
    $1363: 0A         ASL a         
    $1364: 8D 7A 15   STA $157a     
    $1367: 68         PLA           
    $1368: 29 F0      AND #$f0      
    $136A: 85 FB      STA $fb       
    $136C: AD 1F 10   LDA $101f     
    $136F: 29 0F      AND #$0f      
    $1371: 05 FB      ORA $fb       
    $1373: 1D 91 16   ORA $1691,x   
    $1376: 8D 1F 10   STA $101f     
    $1379: 8D 17 D4   STA $d417      ;RES_FILT
    $137C: B9 AC 17   LDA $17ac,y   
    $137F: 8D 6F 15   STA $156f     
    $1382: B9 8C 17   LDA $178c,y   
    $1385: 8D 4C 15   STA $154c     
    $1388: A9 00      LDA #$00      
    $138A: 8D 72 15   STA $1572     
    $138D: A9 03      LDA #$03      
    $138F: 8D 6F 16   STA $166f     
    $1392: D0 0C      BNE $13a0        ; → L_13A0
L_1394:
    $1394: AD 1F 10   LDA $101f     
    $1397: 3D 94 16   AND $1694,x   
    $139A: 8D 1F 10   STA $101f     
    $139D: 8D 17 D4   STA $d417      ;RES_FILT
L_13A0:
    $13A0: BC A0 16   LDY $16a0,x   
    $13A3: BD 4B 16   LDA $164b,x   
    $13A6: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $13A9: BD 48 16   LDA $1648,x   
    $13AC: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $13AF: A9 09      LDA #$09      
    $13B1: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $13B4: 4C 40 15   JMP $1540        ; → L_1540
L_13B7:
    $13B7: DE 73 16   DEC $1673,x   
    $13BA: D0 2D      BNE $13e9        ; → L_13E9
L_13BC:
    $13BC: BC 7C 16   LDY $167c,x   
    $13BF: FE 7C 16   INC $167c,x   
    $13C2: B9 8C 18   LDA $188c,y   
    $13C5: C9 FF      CMP #$ff      
    $13C7: D0 0A      BNE $13d3        ; → L_13D3
    $13C9: C8         INY           
    $13CA: B9 8C 18   LDA $188c,y   
    $13CD: 9D 7C 16   STA $167c,x   
    $13D0: 4C BC 13   JMP $13bc        ; → L_13BC
L_13D3:
    $13D3: 48         PHA           
    $13D4: 29 FE      AND #$fe      
    $13D6: 9D 70 16   STA $1670,x   
    $13D9: 68         PLA           
    $13DA: 29 01      AND #$01      
    $13DC: 9D A9 16   STA $16a9,x   
    $13DF: C8         INY           
    $13E0: FE 7C 16   INC $167c,x   
    $13E3: B9 8C 18   LDA $188c,y   
    $13E6: 9D 73 16   STA $1673,x   
L_13E9:
    $13E9: BD 54 16   LDA $1654,x   
    $13EC: BC A9 16   LDY $16a9,x   
    $13EF: D0 15      BNE $1406        ; → L_1406
    $13F1: 18         CLC           
    $13F2: 7D 70 16   ADC $1670,x   
    $13F5: B0 06      BCS $13fd        ; → L_13FD
    $13F7: 9D 54 16   STA $1654,x   
    $13FA: 4C 18 14   JMP $1418        ; → L_1418
L_13FD:
    $13FD: 9D 54 16   STA $1654,x   
    $1400: FE 57 16   INC $1657,x   
    $1403: 4C 18 14   JMP $1418        ; → L_1418
L_1406:
    $1406: 38         SEC           
    $1407: FD 70 16   SBC $1670,x   
    $140A: 90 06      BCC $1412        ; → L_1412
    $140C: 9D 54 16   STA $1654,x   
    $140F: 4C 18 14   JMP $1418        ; → L_1418
L_1412:
    $1412: 9D 54 16   STA $1654,x   
    $1415: DE 57 16   DEC $1657,x   
L_1418:
    $1418: BD 8E 16   LDA $168e,x   
    $141B: D0 51      BNE $146e        ; → L_146E
L_141D:
    $141D: BC AC 16   LDY $16ac,x   
    $1420: FE AC 16   INC $16ac,x   
    $1423: B9 6C 18   LDA $186c,y   
    $1426: C9 FF      CMP #$ff      
    $1428: D0 09      BNE $1433        ; → L_1433
    $142A: B9 7C 18   LDA $187c,y   
    $142D: 9D AC 16   STA $16ac,x   
    $1430: 4C 1D 14   JMP $141d        ; → L_141D
L_1433:
    $1433: C9 FE      CMP #$fe      
    $1435: D0 06      BNE $143d        ; → L_143D
    $1437: DE 8E 16   DEC $168e,x   
    $143A: 4C 6E 14   JMP $146e        ; → L_146E
L_143D:
    $143D: 9D 5A 16   STA $165a,x   
    $1440: BD 76 16   LDA $1676,x   
    $1443: D0 1B      BNE $1460        ; → L_1460
    $1445: B9 7C 18   LDA $187c,y   
    $1448: 30 04      BMI $144e        ; → L_144E
    $144A: 18         CLC           
    $144B: 7D 07 10   ADC $1007,x   
L_144E:
    $144E: 29 7F      AND #$7f      
    $1450: A8         TAY           
    $1451: B9 E8 15   LDA $15e8,y   
    $1454: 9D 4E 16   STA $164e,x   
    $1457: B9 88 15   LDA $1588,y   
    $145A: 9D 51 16   STA $1651,x   
    $145D: 4C 1C 15   JMP $151c        ; → L_151C
L_1460:
    $1460: B9 7C 18   LDA $187c,y   
    $1463: 9D 4E 16   STA $164e,x   
    $1466: A9 00      LDA #$00      
    $1468: 9D 51 16   STA $1651,x   
    $146B: 4C 1C 15   JMP $151c        ; → L_151C
L_146E:
    $146E: BD 63 16   LDA $1663,x   
    $1471: F0 35      BEQ $14a8        ; → L_14A8
    $1473: BD 66 16   LDA $1666,x   
    $1476: D0 18      BNE $1490        ; → L_1490
    $1478: BD 51 16   LDA $1651,x   
    $147B: 18         CLC           
    $147C: 7D 69 16   ADC $1669,x   
    $147F: B0 06      BCS $1487        ; → L_1487
    $1481: 9D 51 16   STA $1651,x   
    $1484: 4C 1C 15   JMP $151c        ; → L_151C
L_1487:
    $1487: 9D 51 16   STA $1651,x   
    $148A: FE 4E 16   INC $164e,x   
    $148D: 4C 1C 15   JMP $151c        ; → L_151C
L_1490:
    $1490: BD 51 16   LDA $1651,x   
    $1493: 38         SEC           
    $1494: FD 69 16   SBC $1669,x   
    $1497: 90 06      BCC $149f        ; → L_149F
    $1499: 9D 51 16   STA $1651,x   
    $149C: 4C 1C 15   JMP $151c        ; → L_151C
L_149F:
    $149F: 9D 51 16   STA $1651,x   
    $14A2: DE 4E 16   DEC $164e,x   
    $14A5: 4C 1C 15   JMP $151c        ; → L_151C
L_14A8:
    $14A8: BD B2 16   LDA $16b2,x   
    $14AB: F0 06      BEQ $14b3        ; → L_14B3
    $14AD: DE B2 16   DEC $16b2,x   
    $14B0: 4C 1C 15   JMP $151c        ; → L_151C
L_14B3:
    $14B3: BD B8 16   LDA $16b8,x   
    $14B6: D0 4C      BNE $1504        ; → L_1504
    $14B8: BD 51 16   LDA $1651,x   
    $14BB: 38         SEC           
    $14BC: FD BB 16   SBC $16bb,x   
    $14BF: 90 3A      BCC $14fb        ; → L_14FB
    $14C1: 9D 51 16   STA $1651,x   
L_14C4:
    $14C4: DE 79 16   DEC $1679,x   
    $14C7: D0 53      BNE $151c        ; → L_151C
    $14C9: BD B5 16   LDA $16b5,x   
    $14CC: 9D 79 16   STA $1679,x   
    $14CF: DE A6 16   DEC $16a6,x   
    $14D2: D0 48      BNE $151c        ; → L_151C
    $14D4: A9 02      LDA #$02      
    $14D6: 9D A6 16   STA $16a6,x   
    $14D9: BD 6C 16   LDA $166c,x   
    $14DC: D0 12      BNE $14f0        ; → L_14F0
    $14DE: BD BB 16   LDA $16bb,x   
    $14E1: 18         CLC           
    $14E2: 7D 7F 16   ADC $167f,x   
    $14E5: 9D BB 16   STA $16bb,x   
    $14E8: DD 82 16   CMP $1682,x   
    $14EB: 90 03      BCC $14f0        ; → L_14F0
    $14ED: DE 6C 16   DEC $166c,x   
L_14F0:
    $14F0: BD B8 16   LDA $16b8,x   
    $14F3: 49 FF      EOR #$ff      
    $14F5: 9D B8 16   STA $16b8,x   
    $14F8: 4C 1C 15   JMP $151c        ; → L_151C
L_14FB:
    $14FB: 9D 51 16   STA $1651,x   
    $14FE: DE 4E 16   DEC $164e,x   
    $1501: 4C C4 14   JMP $14c4        ; → L_14C4
L_1504:
    $1504: BD 51 16   LDA $1651,x   
    $1507: 18         CLC           
    $1508: 7D BB 16   ADC $16bb,x   
    $150B: B0 06      BCS $1513        ; → L_1513
    $150D: 9D 51 16   STA $1651,x   
    $1510: 4C C4 14   JMP $14c4        ; → L_14C4
L_1513:
    $1513: 9D 51 16   STA $1651,x   
    $1516: FE 4E 16   INC $164e,x   
    $1519: 4C C4 14   JMP $14c4        ; → L_14C4
L_151C:
    $151C: BC A0 16   LDY $16a0,x   
    $151F: BD 54 16   LDA $1654,x   
    $1522: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $1525: BD 57 16   LDA $1657,x   
    $1528: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $152B: BD 4E 16   LDA $164e,x   
    $152E: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1531: BD 51 16   LDA $1651,x   
    $1534: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1537: BD 5A 16   LDA $165a,x   
    $153A: 3D 9A 16   AND $169a,x   
    $153D: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_1540:
    $1540: CA         DEX           
    $1541: 30 03      BMI $1546        ; → L_1546
    $1543: 4C EA 10   JMP $10ea        ; → L_10EA
L_1546:
    $1546: CE 6F 16   DEC $166f     
    $1549: D0 23      BNE $156e        ; → L_156E
L_154B:
    $154B: A0 04      LDY #$04      
    $154D: EE 4C 15   INC $154c     
    $1550: B9 9C 18   LDA $189c,y   
    $1553: C9 80      CMP #$80      
    $1555: D0 0A      BNE $1561        ; → L_1561
    $1557: C8         INY           
    $1558: B9 9C 18   LDA $189c,y   
    $155B: 8D 4C 15   STA $154c     
    $155E: 4C 4B 15   JMP $154b        ; → L_154B
L_1561:
    $1561: 8D 72 15   STA $1572     
    $1564: C8         INY           
    $1565: EE 4C 15   INC $154c     
    $1568: B9 9C 18   LDA $189c,y   
    $156B: 8D 6F 16   STA $166f     
L_156E:
    $156E: A9 14      LDA #$14      
    $1570: 18         CLC           
    $1571: 69 00      ADC #$00      
    $1573: 8D 6F 15   STA $156f     
    $1576: 8D 16 D4   STA $d416      ;FC_HI
    $1579: A9 10      LDA #$10      
    $157B: 0D 06 10   ORA $1006     
    $157E: 8D 18 D4   STA $d418      ;VOL
    $1581: 68         PLA           
    $1582: 85 FC      STA $fc       
    $1584: 68         PLA           
    $1585: 85 FB      STA $fb       
    $1587: 60         RTS           
; ----- data gap $1588-$20E7 (2912 bytes) -----

