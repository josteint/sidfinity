; ============================================================================
; Rob Hubbard - Jupiter41 (1997 Victory/Tempest)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc84/DEMOS/G-L/Jupiter41.sid
; Load:   $1000   Init: $1000   Play: $1003
; PSID:   1 subtune(s), default subtune 1
; Binary: $1000-$2458 (5209 bytes)
;
; Auto-traced 1759 reachable code bytes from init+play.
;
; ============================================================================
; DMC V5 FAMILY-4 (Jupiter41, 686 SIDs). Full RE in pipelines/dmc/family4/RE_NOTES.md
; Shares the V5 TRACK/SECTOR data model with family-3 (Katusha) but a different
; player + instrument format. ~0.31 Jaccard to family-3.
;
; ROUTINE MAP (Phase A):
;   $1040 init      — copy song record from $1A40+song*8 (3 trk ptrs + speed);
;                     clear work RAM; clear $D400-$D417; test bit on 3 voices.
;   $1095 play      — DEC $1016; BMI -> alt. normal: JSR $1373 x3. alt: $1016=1,
;                     JSR $10E1 x3. Then $D416 = $1019+$1853 (cutoff hi ONLY;
;                     NO $D415). zero-page $FA/$FB (family-3: $F8/$F9).
;   $10D3 (JT#3)    — JSR $1654 x3 (per-voice SID write pass).
;   $10E1 tick      — dec dur ctr $17E5,x; on expiry walk the TRACK ($17D9/$17DC
;                     ptr, pos $17DF): sector# (<$80) + $FF loop / $FE stop /
;                     $FD/$FC transpose. sector ptr = ($2209[sec],$224B[sec]).
;   $1150 sector    — command dispatch (>=$80); $F0/$F3/$F4/$F5/$F8/$F9/$FA/$FB/
;                     $FC/$FD/$FE (mostly == family-3; see RE_NOTES table).
;   $1314 note      — note+transpose -> $1012; note-on $1323 loads instr AD/SR,
;                     ctrl $09; sets note-start flag $1815,x.
;   $1373 effects   — MAIN per-voice. note-init reads the 8-byte instrument
;                     record at $228D (AD/SR/+2/+3 prog/+4 V3filt/+5 wave/+6/+7);
;                     freq table lookup; vib step. Steady -> $147B.
;   $147B steady    — effect chain: FILTER prog (V3, $23D5/$242C) -> PULSE prog
;                     ($23A3/$23BC) -> GLIDE ($183C/$183F accum) -> JSR $1654.
;   $1654 wavestep  — wave ctrl $2325 / arg $2364 ($90 loop); freq lo $1719 +
;                     hi $1779 (+arp, +$EF bias $1842); gate/hard-restart; then
;                     SID WRITE per voice: D400 D401 D402 D403 D404 (in order).
; KEY ADDRESSES: song $1A40 · sector-ptr lo $2209 / hi $224B · instr $228D ·
;   freq lo $1719 / hi $1779 · pulse prog $23A3/$23BC · filter prog $23D5/$242C ·
;   wave $2325/$2364 · cutoff $1019 + $1853 ($F8) -> $D416.
; ============================================================================

; ======= init: =======
init:
    $1000: 4C 40 10   JMP $1040        ; → sub_1040
; ======= play: =======
play:
    $1003: 4C 95 10   JMP $1095        ; → sub_1095
; ----- data gap $1006-$103F (58 bytes) -----

sub_1040:
    $1040: A9 00      LDA #$00      
    $1042: 0A         ASL a         
    $1043: A8         TAY           
    $1044: A2 00      LDX #$00      
L_1046:
    $1046: B9 40 1A   LDA $1a40,y   
    $1049: 9D D9 17   STA $17d9,x   
    $104C: B9 41 1A   LDA $1a41,y   
    $104F: 9D DC 17   STA $17dc,x   
    $1052: C8         INY           
    $1053: C8         INY           
    $1054: E8         INX           
    $1055: E0 03      CPX #$03      
    $1057: D0 ED      BNE $1046        ; → L_1046
    $1059: B9 40 1A   LDA $1a40,y   
    $105C: 8D BF 10   STA $10bf     
    $105F: B9 41 1A   LDA $1a41,y   
    $1062: 8D 1A 10   STA $101a     
    $1065: A2 00      LDX #$00      
    $1067: 8A         TXA           
L_1068:
    $1068: 9D DF 17   STA $17df,x   
    $106B: E8         INX           
    $106C: E0 79      CPX #$79      
    $106E: D0 F8      BNE $1068        ; → L_1068
    $1070: AA         TAX           
L_1071:
    $1071: A9 02      LDA #$02      
    $1073: 9D E5 17   STA $17e5,x   
    $1076: 9D 09 10   STA $1009,x   
    $1079: E8         INX           
    $107A: E0 03      CPX #$03      
    $107C: D0 F3      BNE $1071        ; → L_1071
    $107E: A2 00      LDX #$00      
    $1080: 8A         TXA           
L_1081:
    $1081: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $1084: E8         INX           
    $1085: E0 18      CPX #$18      
    $1087: D0 F8      BNE $1081        ; → L_1081
    $1089: A9 08      LDA #$08      
    $108B: 8D 04 D4   STA $d404      ;V1_CTRL
    $108E: 8D 0B D4   STA $d40b      ;V2_CTRL
    $1091: 8D 12 D4   STA $d412      ;V3_CTRL
    $1094: 60         RTS           
sub_1095:
    $1095: A5 FA      LDA $fa       
    $1097: 48         PHA           
    $1098: A5 FB      LDA $fb       
    $109A: 48         PHA           
    $109B: CE 16 10   DEC $1016     
    $109E: 30 1E      BMI $10be        ; → L_10BE
    $10A0: A2 00      LDX #$00      
    $10A2: 20 73 13   JSR $1373        ; → sub_1373
    $10A5: E8         INX           
    $10A6: 20 73 13   JSR $1373        ; → sub_1373
    $10A9: E8         INX           
    $10AA: 20 73 13   JSR $1373        ; → sub_1373
L_10AD:
    $10AD: AD 19 10   LDA $1019     
    $10B0: 18         CLC           
    $10B1: 6D 53 18   ADC $1853     
    $10B4: 8D 16 D4   STA $d416      ;FC_HI
    $10B7: 68         PLA           
    $10B8: 85 FB      STA $fb       
    $10BA: 68         PLA           
    $10BB: 85 FA      STA $fa       
    $10BD: 60         RTS           
L_10BE:
    $10BE: A9 01      LDA #$01      
    $10C0: 8D 16 10   STA $1016     
    $10C3: A2 00      LDX #$00      
    $10C5: 20 E1 10   JSR $10e1        ; → sub_10E1
    $10C8: E8         INX           
    $10C9: 20 E1 10   JSR $10e1        ; → sub_10E1
    $10CC: E8         INX           
    $10CD: 20 E1 10   JSR $10e1        ; → sub_10E1
    $10D0: 4C AD 10   JMP $10ad        ; → L_10AD
sub_10D3:
    $10D3: A2 00      LDX #$00      
    $10D5: 20 54 16   JSR $1654        ; → sub_1654
    $10D8: E8         INX           
    $10D9: 20 54 16   JSR $1654        ; → sub_1654
    $10DC: E8         INX           
    $10DD: 20 54 16   JSR $1654        ; → sub_1654
    $10E0: 60         RTS           
sub_10E1:
    $10E1: BD 09 10   LDA $1009,x   
    $10E4: F0 05      BEQ $10eb        ; → L_10EB
    $10E6: DE E5 17   DEC $17e5,x   
    $10E9: F0 03      BEQ $10ee        ; → L_10EE
L_10EB:
    $10EB: 4C 73 13   JMP $1373        ; → sub_1373
L_10EE:
    $10EE: BD D9 17   LDA $17d9,x   
    $10F1: 85 FA      STA $fa       
    $10F3: BD DC 17   LDA $17dc,x   
    $10F6: 85 FB      STA $fb       
    $10F8: BC DF 17   LDY $17df,x   
    $10FB: B1 FA      LDA ($fa),y   
    $10FD: 10 46      BPL $1145        ; → L_1145
    $10FF: C9 FF      CMP #$ff      
    $1101: D0 09      BNE $110c        ; → L_110C
    $1103: C8         INY           
    $1104: B1 FA      LDA ($fa),y   
    $1106: 9D DF 17   STA $17df,x   
    $1109: A8         TAY           
    $110A: B1 FA      LDA ($fa),y   
L_110C:
    $110C: C9 FD      CMP #$fd      
    $110E: D0 10      BNE $1120        ; → L_1120
    $1110: C8         INY           
    $1111: B1 FA      LDA ($fa),y   
    $1113: 9D EE 17   STA $17ee,x   
    $1116: C8         INY           
    $1117: 98         TYA           
    $1118: 9D DF 17   STA $17df,x   
    $111B: B1 FA      LDA ($fa),y   
    $111D: 4C 45 11   JMP $1145        ; → L_1145
L_1120:
    $1120: C9 FC      CMP #$fc      
    $1122: D0 15      BNE $1139        ; → L_1139
    $1124: C8         INY           
    $1125: B1 FA      LDA ($fa),y   
    $1127: 49 FF      EOR #$ff      
    $1129: 18         CLC           
    $112A: 69 01      ADC #$01      
    $112C: 9D EE 17   STA $17ee,x   
    $112F: C8         INY           
    $1130: 98         TYA           
    $1131: 9D DF 17   STA $17df,x   
    $1134: B1 FA      LDA ($fa),y   
    $1136: 4C 45 11   JMP $1145        ; → L_1145
L_1139:
    $1139: C9 FE      CMP #$fe      
    $113B: D0 08      BNE $1145        ; → L_1145
    $113D: A9 00      LDA #$00      
    $113F: 9D 09 10   STA $1009,x   
    $1142: 4C 54 16   JMP $1654        ; → sub_1654
L_1145:
    $1145: A8         TAY           
    $1146: B9 09 22   LDA $2209,y   
    $1149: 85 FA      STA $fa       
    $114B: B9 4B 22   LDA $224b,y   
    $114E: 85 FB      STA $fb       
L_1150:
    $1150: BC E2 17   LDY $17e2,x   
L_1153:
    $1153: B1 FA      LDA ($fa),y   
    $1155: 30 03      BMI $115a        ; → L_115A
    $1157: 4C 14 13   JMP $1314        ; → L_1314
L_115A:
    $115A: C9 FD      CMP #$fd      
    $115C: D0 0E      BNE $116c        ; → L_116C
    $115E: C8         INY           
    $115F: B1 FA      LDA ($fa),y   
    $1161: 9D E8 17   STA $17e8,x   
    $1164: C8         INY           
    $1165: 98         TYA           
    $1166: 9D E2 17   STA $17e2,x   
    $1169: 4C 53 11   JMP $1153        ; → L_1153
L_116C:
    $116C: C9 FC      CMP #$fc      
    $116E: D0 0E      BNE $117e        ; → L_117E
    $1170: C8         INY           
    $1171: B1 FA      LDA ($fa),y   
    $1173: 9D EB 17   STA $17eb,x   
    $1176: C8         INY           
    $1177: 98         TYA           
    $1178: 9D E2 17   STA $17e2,x   
    $117B: 4C 53 11   JMP $1153        ; → L_1153
L_117E:
    $117E: C9 F0      CMP #$f0      
    $1180: D0 4A      BNE $11cc        ; → L_11CC
    $1182: C8         INY           
    $1183: B1 FA      LDA ($fa),y   
    $1185: 48         PHA           
    $1186: 29 07      AND #$07      
    $1188: 8D 56 18   STA $1856     
    $118B: BC 12 10   LDY $1012,x   
    $118E: B9 79 17   LDA $1779,y   
    $1191: 9D 0C 18   STA $180c,x   
    $1194: AD 56 18   LDA $1856     
    $1197: F0 1E      BEQ $11b7        ; → L_11B7
    $1199: A9 00      LDA #$00      
    $119B: 9D 0F 18   STA $180f,x   
    $119E: 9D 06 18   STA $1806,x   
    $11A1: 9D 33 18   STA $1833,x   
    $11A4: 9D 36 18   STA $1836,x   
    $11A7: 9D 39 18   STA $1839,x   
    $11AA: A8         TAY           
L_11AB:
    $11AB: 1E 0C 18   ASL $180c,x   
    $11AE: 3E 0F 18   ROL $180f,x   
    $11B1: C8         INY           
    $11B2: CC 56 18   CPY $1856     
    $11B5: D0 F4      BNE $11ab        ; → L_11AB
L_11B7:
    $11B7: 68         PLA           
    $11B8: 4A         LSR a         
    $11B9: 4A         LSR a         
    $11BA: 4A         LSR a         
    $11BB: 4A         LSR a         
    $11BC: 9D 09 18   STA $1809,x   
    $11BF: BD E2 17   LDA $17e2,x   
    $11C2: 18         CLC           
    $11C3: 69 02      ADC #$02      
    $11C5: 9D E2 17   STA $17e2,x   
    $11C8: A8         TAY           
    $11C9: 4C 53 11   JMP $1153        ; → L_1153
L_11CC:
    $11CC: C9 FE      CMP #$fe      
    $11CE: D0 24      BNE $11f4        ; → L_11F4
L_11D0:
    $11D0: BD E8 17   LDA $17e8,x   
    $11D3: 9D E5 17   STA $17e5,x   
    $11D6: FE E2 17   INC $17e2,x   
    $11D9: C8         INY           
    $11DA: B1 FA      LDA ($fa),y   
    $11DC: 9D 27 18   STA $1827,x   
    $11DF: C9 FF      CMP #$ff      
    $11E1: D0 0E      BNE $11f1        ; → L_11F1
    $11E3: A9 00      LDA #$00      
    $11E5: 9D E2 17   STA $17e2,x   
    $11E8: 9D F1 17   STA $17f1,x   
    $11EB: 9D F4 17   STA $17f4,x   
    $11EE: FE DF 17   INC $17df,x   
L_11F1:
    $11F1: 4C 54 16   JMP $1654        ; → sub_1654
L_11F4:
    $11F4: C9 F4      CMP #$f4      
    $11F6: D0 0B      BNE $1203        ; → L_1203
    $11F8: BD 21 18   LDA $1821,x   
    $11FB: 49 01      EOR #$01      
    $11FD: 9D 21 18   STA $1821,x   
    $1200: 4C D0 11   JMP $11d0        ; → L_11D0
L_1203:
    $1203: C9 F5      CMP #$f5      
    $1205: D0 0E      BNE $1215        ; → L_1215
    $1207: BD F4 17   LDA $17f4,x   
    $120A: 49 FF      EOR #$ff      
    $120C: 9D F4 17   STA $17f4,x   
    $120F: FE E2 17   INC $17e2,x   
    $1212: 4C 50 11   JMP $1150        ; → L_1150
L_1215:
    $1215: C9 F3      CMP #$f3      
    $1217: D0 0E      BNE $1227        ; → L_1227
    $1219: C8         INY           
    $121A: B1 FA      LDA ($fa),y   
    $121C: 9D F1 17   STA $17f1,x   
    $121F: C8         INY           
    $1220: 98         TYA           
    $1221: 9D E2 17   STA $17e2,x   
    $1224: 4C 53 11   JMP $1153        ; → L_1153
L_1227:
    $1227: C9 FB      CMP #$fb      
    $1229: D0 21      BNE $124c        ; → L_124C
    $122B: C8         INY           
    $122C: B1 FA      LDA ($fa),y   
    $122E: 9D F7 17   STA $17f7,x   
    $1231: C8         INY           
    $1232: B1 FA      LDA ($fa),y   
    $1234: 18         CLC           
    $1235: 7D EE 17   ADC $17ee,x   
    $1238: 9D 12 10   STA $1012,x   
    $123B: C8         INY           
    $123C: B1 FA      LDA ($fa),y   
    $123E: 18         CLC           
    $123F: 7D EE 17   ADC $17ee,x   
    $1242: 9D FA 17   STA $17fa,x   
    $1245: 98         TYA           
    $1246: 9D E2 17   STA $17e2,x   
    $1249: 4C 23 13   JMP $1323        ; → L_1323
L_124C:
    $124C: C9 FA      CMP #$fa      
    $124E: D0 1F      BNE $126f        ; → L_126F
    $1250: C8         INY           
    $1251: B1 FA      LDA ($fa),y   
    $1253: 9D F7 17   STA $17f7,x   
    $1256: C8         INY           
    $1257: B1 FA      LDA ($fa),y   
    $1259: 18         CLC           
    $125A: 7D EE 17   ADC $17ee,x   
    $125D: 9D FA 17   STA $17fa,x   
    $1260: 98         TYA           
    $1261: 9D E2 17   STA $17e2,x   
    $1264: A9 00      LDA #$00      
    $1266: 9D 3C 18   STA $183c,x   
    $1269: 9D 3F 18   STA $183f,x   
    $126C: 4C D0 11   JMP $11d0        ; → L_11D0
L_126F:
    $126F: C9 F9      CMP #$f9      
    $1271: D0 21      BNE $1294        ; → L_1294
    $1273: C8         INY           
    $1274: B1 FA      LDA ($fa),y   
    $1276: 8D 57 18   STA $1857     
    $1279: F0 06      BEQ $1281        ; → L_1281
    $127B: 0A         ASL a         
    $127C: 0A         ASL a         
    $127D: 0A         ASL a         
    $127E: 0A         ASL a         
    $127F: 09 04      ORA #$04      
L_1281:
    $1281: 8D 17 D4   STA $d417      ;RES_FILT
    $1284: AD 57 18   LDA $1857     
    $1287: 29 F0      AND #$f0      
    $1289: 8D 18 10   STA $1018     
    $128C: C8         INY           
    $128D: 98         TYA           
    $128E: 9D E2 17   STA $17e2,x   
    $1291: 4C 53 11   JMP $1153        ; → L_1153
L_1294:
    $1294: C9 F8      CMP #$f8      
    $1296: D0 0E      BNE $12a6        ; → L_12A6
    $1298: C8         INY           
    $1299: B1 FA      LDA ($fa),y   
    $129B: 8D 53 18   STA $1853     
    $129E: C8         INY           
    $129F: 98         TYA           
    $12A0: 9D E2 17   STA $17e2,x   
    $12A3: 4C 53 11   JMP $1153        ; → L_1153
L_12A6:
    $12A6: C9 F2      CMP #$f2      
    $12A8: D0 15      BNE $12bf        ; → L_12BF
    $12AA: C8         INY           
    $12AB: B1 FA      LDA ($fa),y   
    $12AD: BC 0C 10   LDY $100c,x   
    $12B0: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $12B3: BD E2 17   LDA $17e2,x   
    $12B6: 18         CLC           
    $12B7: 69 02      ADC #$02      
    $12B9: 9D E2 17   STA $17e2,x   
    $12BC: 4C 50 11   JMP $1150        ; → L_1150
L_12BF:
    $12BF: C9 F1      CMP #$f1      
    $12C1: D0 15      BNE $12d8        ; → L_12D8
    $12C3: C8         INY           
    $12C4: B1 FA      LDA ($fa),y   
    $12C6: BC 0C 10   LDY $100c,x   
    $12C9: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $12CC: BD E2 17   LDA $17e2,x   
    $12CF: 18         CLC           
    $12D0: 69 02      ADC #$02      
    $12D2: 9D E2 17   STA $17e2,x   
    $12D5: 4C 50 11   JMP $1150        ; → L_1150
L_12D8:
    $12D8: C9 F7      CMP #$f7      
    $12DA: D0 0E      BNE $12ea        ; → L_12EA
    $12DC: C8         INY           
    $12DD: B1 FA      LDA ($fa),y   
    $12DF: 8D 54 18   STA $1854     
    $12E2: C8         INY           
    $12E3: 98         TYA           
    $12E4: 9D E2 17   STA $17e2,x   
    $12E7: 4C 53 11   JMP $1153        ; → L_1153
L_12EA:
    $12EA: C9 F6      CMP #$f6      
    $12EC: D0 0E      BNE $12fc        ; → L_12FC
    $12EE: C8         INY           
    $12EF: B1 FA      LDA ($fa),y   
    $12F1: 8D 55 18   STA $1855     
    $12F4: C8         INY           
    $12F5: 98         TYA           
    $12F6: 9D E2 17   STA $17e2,x   
    $12F9: 4C 53 11   JMP $1153        ; → L_1153
L_12FC:
    $12FC: C9 EF      CMP #$ef      
    $12FE: D0 0E      BNE $130e        ; → L_130E
    $1300: C8         INY           
    $1301: B1 FA      LDA ($fa),y   
    $1303: 9D 42 18   STA $1842,x   
    $1306: C8         INY           
    $1307: 98         TYA           
    $1308: 9D E2 17   STA $17e2,x   
    $130B: 4C 53 11   JMP $1153        ; → L_1153
L_130E:
    $130E: FE E2 17   INC $17e2,x   
    $1311: 4C 50 11   JMP $1150        ; → L_1150
L_1314:
    $1314: 18         CLC           
    $1315: 7D EE 17   ADC $17ee,x   
    $1318: 9D 12 10   STA $1012,x   
    $131B: BD F4 17   LDA $17f4,x   
    $131E: F0 03      BEQ $1323        ; → L_1323
    $1320: 4C D0 11   JMP $11d0        ; → L_11D0
L_1323:
    $1323: C8         INY           
    $1324: B1 FA      LDA ($fa),y   
    $1326: 9D 27 18   STA $1827,x   
    $1329: BD EB 17   LDA $17eb,x   
    $132C: 0A         ASL a         
    $132D: 0A         ASL a         
    $132E: 0A         ASL a         
    $132F: 9D 4B 18   STA $184b,x   
    $1332: A8         TAY           
    $1333: BD F1 17   LDA $17f1,x   
    $1336: D0 1A      BNE $1352        ; → L_1352
    $1338: B9 8D 22   LDA $228d,y   
    $133B: 48         PHA           
    $133C: B9 8E 22   LDA $228e,y   
    $133F: BC 0C 10   LDY $100c,x   
    $1342: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $1345: 68         PLA           
    $1346: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $1349: A9 09      LDA #$09      
    $134B: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $134E: 9D 15 18   STA $1815,x   
    $1351: 60         RTS           
L_1352:
    $1352: 0A         ASL a         
    $1353: 0A         ASL a         
    $1354: 0A         ASL a         
    $1355: 0A         ASL a         
    $1356: 85 FA      STA $fa       
    $1358: B9 8E 22   LDA $228e,y   
    $135B: 29 0F      AND #$0f      
    $135D: 05 FA      ORA $fa       
    $135F: BC 0C 10   LDY $100c,x   
    $1362: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $1365: A9 00      LDA #$00      
    $1367: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $136A: A9 09      LDA #$09      
    $136C: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $136F: 9D 15 18   STA $1815,x   
    $1372: 60         RTS           
sub_1373:
    $1373: BD 15 18   LDA $1815,x   
    $1376: D0 03      BNE $137b        ; → L_137B
    $1378: 4C 7B 14   JMP $147b        ; → L_147B
L_137B:
    $137B: A9 00      LDA #$00      
    $137D: 9D 15 18   STA $1815,x   
    $1380: 9D 3C 18   STA $183c,x   
    $1383: 9D 3F 18   STA $183f,x   
    $1386: BD E8 17   LDA $17e8,x   
    $1389: 9D E5 17   STA $17e5,x   
    $138C: FE E2 17   INC $17e2,x   
    $138F: BC 4B 18   LDY $184b,x   
    $1392: B9 93 22   LDA $2293,y   
    $1395: 29 0F      AND #$0f      
    $1397: 9D 09 18   STA $1809,x   
    $139A: F0 45      BEQ $13e1        ; → L_13E1
    $139C: B9 92 22   LDA $2292,y   
    $139F: 9D 06 18   STA $1806,x   
    $13A2: B9 94 22   LDA $2294,y   
    $13A5: 29 F0      AND #$f0      
    $13A7: 4A         LSR a         
    $13A8: 4A         LSR a         
    $13A9: 4A         LSR a         
    $13AA: 9D 12 18   STA $1812,x   
    $13AD: B9 94 22   LDA $2294,y   
    $13B0: 29 07      AND #$07      
    $13B2: 8D 56 18   STA $1856     
    $13B5: BC 12 10   LDY $1012,x   
    $13B8: B9 79 17   LDA $1779,y   
    $13BB: 9D 0C 18   STA $180c,x   
    $13BE: A9 00      LDA #$00      
    $13C0: 9D 0F 18   STA $180f,x   
    $13C3: 9D 33 18   STA $1833,x   
    $13C6: 9D 36 18   STA $1836,x   
    $13C9: 9D 39 18   STA $1839,x   
    $13CC: A8         TAY           
    $13CD: AD 56 18   LDA $1856     
    $13D0: F0 0C      BEQ $13de        ; → L_13DE
L_13D2:
    $13D2: 1E 0C 18   ASL $180c,x   
    $13D5: 3E 0F 18   ROL $180f,x   
    $13D8: C8         INY           
    $13D9: CC 56 18   CPY $1856     
    $13DC: D0 F4      BNE $13d2        ; → L_13D2
L_13DE:
    $13DE: BC 4B 18   LDY $184b,x   
L_13E1:
    $13E1: B9 93 22   LDA $2293,y   
    $13E4: 4A         LSR a         
    $13E5: 4A         LSR a         
    $13E6: 4A         LSR a         
    $13E7: 4A         LSR a         
    $13E8: 9D 45 18   STA $1845,x   
    $13EB: 9D 48 18   STA $1848,x   
    $13EE: B9 8F 22   LDA $228f,y   
    $13F1: 9D FD 17   STA $17fd,x   
    $13F4: B9 90 22   LDA $2290,y   
    $13F7: F0 18      BEQ $1411        ; → L_1411
    $13F9: A8         TAY           
    $13FA: 9D 00 18   STA $1800,x   
    $13FD: B9 A3 23   LDA $23a3,y   
    $1400: 9D 2D 18   STA $182d,x   
    $1403: B9 BC 23   LDA $23bc,y   
    $1406: 9D 2A 18   STA $182a,x   
    $1409: A9 00      LDA #$00      
    $140B: 9D 30 18   STA $1830,x   
    $140E: FE 00 18   INC $1800,x   
L_1411:
    $1411: E0 02      CPX #$02      
    $1413: D0 1A      BNE $142f        ; → L_142F
    $1415: BC 4B 18   LDY $184b,x   
    $1418: B9 91 22   LDA $2291,y   
    $141B: F0 12      BEQ $142f        ; → L_142F
    $141D: 8D 03 18   STA $1803     
    $1420: A8         TAY           
    $1421: B9 D5 23   LDA $23d5,y   
    $1424: 8D 19 10   STA $1019     
    $1427: A9 00      LDA #$00      
    $1429: 8D 4E 18   STA $184e     
    $142C: EE 03 18   INC $1803     
L_142F:
    $142F: BC FD 17   LDY $17fd,x   
    $1432: B9 25 23   LDA $2325,y   
    $1435: 9D 1E 18   STA $181e,x   
    $1438: 29 08      AND #$08      
    $143A: F0 0E      BEQ $144a        ; → L_144A
    $143C: B9 64 23   LDA $2364,y   
    $143F: 9D 1B 18   STA $181b,x   
    $1442: A9 00      LDA #$00      
    $1444: 9D 18 18   STA $1818,x   
    $1447: 4C 5E 14   JMP $145e        ; → L_145E
L_144A:
    $144A: B9 64 23   LDA $2364,y   
    $144D: 18         CLC           
    $144E: 7D 12 10   ADC $1012,x   
    $1451: A8         TAY           
    $1452: B9 19 17   LDA $1719,y   
    $1455: 9D 18 18   STA $1818,x   
    $1458: B9 79 17   LDA $1779,y   
    $145B: 9D 1B 18   STA $181b,x   
L_145E:
    $145E: A9 F7      LDA #$f7      
    $1460: 9D 21 18   STA $1821,x   
    $1463: BD 27 18   LDA $1827,x   
    $1466: C9 FF      CMP #$ff      
    $1468: D0 0E      BNE $1478        ; → L_1478
    $146A: A9 00      LDA #$00      
    $146C: 9D E2 17   STA $17e2,x   
    $146F: 9D F1 17   STA $17f1,x   
    $1472: 9D F4 17   STA $17f4,x   
    $1475: FE DF 17   INC $17df,x   
L_1478:
    $1478: 4C 96 16   JMP $1696        ; → L_1696
L_147B:
    $147B: E0 02      CPX #$02      
    $147D: D0 35      BNE $14b4        ; → L_14B4
    $147F: AD 57 18   LDA $1857     
    $1482: F0 30      BEQ $14b4        ; → L_14B4
    $1484: AC 03 18   LDY $1803     
    $1487: B9 D5 23   LDA $23d5,y   
    $148A: C9 90      CMP #$90      
    $148C: D0 07      BNE $1495        ; → L_1495
    $148E: B9 2C 24   LDA $242c,y   
    $1491: 8D 03 18   STA $1803     
    $1494: A8         TAY           
L_1495:
    $1495: B9 D5 23   LDA $23d5,y   
    $1498: 18         CLC           
    $1499: 6D 19 10   ADC $1019     
    $149C: 8D 19 10   STA $1019     
    $149F: C8         INY           
    $14A0: EE 4E 18   INC $184e     
    $14A3: AD 4E 18   LDA $184e     
    $14A6: D9 2C 24   CMP $242c,y   
    $14A9: D0 09      BNE $14b4        ; → L_14B4
    $14AB: A9 00      LDA #$00      
    $14AD: 8D 4E 18   STA $184e     
    $14B0: C8         INY           
    $14B1: 8C 03 18   STY $1803     
L_14B4:
    $14B4: BC 00 18   LDY $1800,x   
    $14B7: B9 A3 23   LDA $23a3,y   
    $14BA: C9 90      CMP #$90      
    $14BC: D0 07      BNE $14c5        ; → L_14C5
    $14BE: B9 BC 23   LDA $23bc,y   
    $14C1: 9D 00 18   STA $1800,x   
    $14C4: A8         TAY           
L_14C5:
    $14C5: B9 BC 23   LDA $23bc,y   
    $14C8: 18         CLC           
    $14C9: 7D 2A 18   ADC $182a,x   
    $14CC: 9D 2A 18   STA $182a,x   
    $14CF: B9 A3 23   LDA $23a3,y   
    $14D2: 7D 2D 18   ADC $182d,x   
    $14D5: 9D 2D 18   STA $182d,x   
    $14D8: C8         INY           
    $14D9: FE 30 18   INC $1830,x   
    $14DC: BD 30 18   LDA $1830,x   
    $14DF: D9 BC 23   CMP $23bc,y   
    $14E2: D0 0A      BNE $14ee        ; → L_14EE
    $14E4: A9 00      LDA #$00      
    $14E6: 9D 30 18   STA $1830,x   
    $14E9: C8         INY           
    $14EA: 98         TYA           
    $14EB: 9D 00 18   STA $1800,x   
L_14EE:
    $14EE: BD F7 17   LDA $17f7,x   
    $14F1: D0 03      BNE $14f6        ; → L_14F6
    $14F3: 4C 6C 15   JMP $156c        ; → L_156C
L_14F6:
    $14F6: BD 12 10   LDA $1012,x   
    $14F9: DD FA 17   CMP $17fa,x   
    $14FC: B0 2D      BCS $152b        ; → L_152B
    $14FE: BD 18 18   LDA $1818,x   
    $1501: 18         CLC           
    $1502: 7D 3C 18   ADC $183c,x   
    $1505: BD 1B 18   LDA $181b,x   
    $1508: 7D 3F 18   ADC $183f,x   
    $150B: BC FA 17   LDY $17fa,x   
    $150E: D9 79 17   CMP $1779,y   
    $1511: D0 03      BNE $1516        ; → L_1516
    $1513: 4C 58 15   JMP $1558        ; → L_1558
L_1516:
    $1516: BD 3C 18   LDA $183c,x   
    $1519: 18         CLC           
    $151A: 7D F7 17   ADC $17f7,x   
    $151D: 9D 3C 18   STA $183c,x   
    $1520: BD 3F 18   LDA $183f,x   
    $1523: 69 00      ADC #$00      
    $1525: 9D 3F 18   STA $183f,x   
    $1528: 4C 54 16   JMP $1654        ; → sub_1654
L_152B:
    $152B: BD 18 18   LDA $1818,x   
    $152E: 18         CLC           
    $152F: 7D 3C 18   ADC $183c,x   
    $1532: BD 1B 18   LDA $181b,x   
    $1535: 7D 3F 18   ADC $183f,x   
    $1538: BC FA 17   LDY $17fa,x   
    $153B: D9 79 17   CMP $1779,y   
    $153E: D0 03      BNE $1543        ; → L_1543
    $1540: 4C 58 15   JMP $1558        ; → L_1558
L_1543:
    $1543: BD 3C 18   LDA $183c,x   
    $1546: 38         SEC           
    $1547: FD F7 17   SBC $17f7,x   
    $154A: 9D 3C 18   STA $183c,x   
    $154D: BD 3F 18   LDA $183f,x   
    $1550: E9 00      SBC #$00      
    $1552: 9D 3F 18   STA $183f,x   
    $1555: 4C 54 16   JMP $1654        ; → sub_1654
L_1558:
    $1558: BD FA 17   LDA $17fa,x   
    $155B: 9D 12 10   STA $1012,x   
    $155E: A9 00      LDA #$00      
    $1560: 9D 3C 18   STA $183c,x   
    $1563: 9D 3F 18   STA $183f,x   
    $1566: 9D F7 17   STA $17f7,x   
    $1569: 4C 54 16   JMP $1654        ; → sub_1654
L_156C:
    $156C: BD F4 17   LDA $17f4,x   
    $156F: F0 0B      BEQ $157c        ; → L_157C
    $1571: A9 00      LDA #$00      
    $1573: 9D 3C 18   STA $183c,x   
    $1576: 9D 3F 18   STA $183f,x   
    $1579: 4C 54 16   JMP $1654        ; → sub_1654
L_157C:
    $157C: BD 09 18   LDA $1809,x   
    $157F: D0 03      BNE $1584        ; → L_1584
    $1581: 4C 12 16   JMP $1612        ; → L_1612
L_1584:
    $1584: BD 06 18   LDA $1806,x   
    $1587: F0 06      BEQ $158f        ; → L_158F
    $1589: DE 06 18   DEC $1806,x   
    $158C: 4C 12 16   JMP $1612        ; → L_1612
L_158F:
    $158F: BD 36 18   LDA $1836,x   
    $1592: D0 49      BNE $15dd        ; → L_15DD
    $1594: BD 3C 18   LDA $183c,x   
    $1597: 18         CLC           
    $1598: 7D 0C 18   ADC $180c,x   
    $159B: 9D 3C 18   STA $183c,x   
    $159E: BD 3F 18   LDA $183f,x   
    $15A1: 7D 0F 18   ADC $180f,x   
    $15A4: 9D 3F 18   STA $183f,x   
    $15A7: FE 39 18   INC $1839,x   
    $15AA: BD 39 18   LDA $1839,x   
    $15AD: DD 09 18   CMP $1809,x   
    $15B0: D0 60      BNE $1612        ; → L_1612
    $15B2: FE 36 18   INC $1836,x   
    $15B5: BD 12 18   LDA $1812,x   
    $15B8: F0 12      BEQ $15cc        ; → L_15CC
    $15BA: 18         CLC           
    $15BB: 7D 0C 18   ADC $180c,x   
    $15BE: 9D 0C 18   STA $180c,x   
    $15C1: BD 0F 18   LDA $180f,x   
    $15C4: 69 00      ADC #$00      
    $15C6: 9D 0F 18   STA $180f,x   
    $15C9: 4C 54 16   JMP $1654        ; → sub_1654
L_15CC:
    $15CC: BD 33 18   LDA $1833,x   
    $15CF: D0 09      BNE $15da        ; → L_15DA
    $15D1: 1E 0C 18   ASL $180c,x   
    $15D4: 3E 0F 18   ROL $180f,x   
    $15D7: FE 33 18   INC $1833,x   
L_15DA:
    $15DA: 4C 54 16   JMP $1654        ; → sub_1654
L_15DD:
    $15DD: BD 3C 18   LDA $183c,x   
    $15E0: 38         SEC           
    $15E1: FD 0C 18   SBC $180c,x   
    $15E4: 9D 3C 18   STA $183c,x   
    $15E7: BD 3F 18   LDA $183f,x   
    $15EA: FD 0F 18   SBC $180f,x   
    $15ED: 9D 3F 18   STA $183f,x   
    $15F0: DE 39 18   DEC $1839,x   
    $15F3: BD 39 18   LDA $1839,x   
    $15F6: D0 1A      BNE $1612        ; → L_1612
    $15F8: DE 36 18   DEC $1836,x   
    $15FB: BD 12 18   LDA $1812,x   
    $15FE: F0 12      BEQ $1612        ; → L_1612
    $1600: 18         CLC           
    $1601: 7D 0C 18   ADC $180c,x   
    $1604: 9D 0C 18   STA $180c,x   
    $1607: BD 0F 18   LDA $180f,x   
    $160A: 69 00      ADC #$00      
    $160C: 9D 0F 18   STA $180f,x   
    $160F: 4C 54 16   JMP $1654        ; → sub_1654
L_1612:
    $1612: AD 55 18   LDA $1855     
    $1615: F0 17      BEQ $162e        ; → L_162E
    $1617: AD 1B 10   LDA $101b     
    $161A: 38         SEC           
    $161B: ED 55 18   SBC $1855     
    $161E: 8D 1B 10   STA $101b     
    $1621: AD 1A 10   LDA $101a     
    $1624: E9 00      SBC #$00      
    $1626: 8D 1A 10   STA $101a     
    $1629: D0 03      BNE $162e        ; → L_162E
    $162B: 8D 55 18   STA $1855     
L_162E:
    $162E: AD 54 18   LDA $1854     
    $1631: F0 18      BEQ $164b        ; → L_164B
    $1633: 18         CLC           
    $1634: 6D 1B 10   ADC $101b     
    $1637: 8D 1B 10   STA $101b     
    $163A: AD 1A 10   LDA $101a     
    $163D: 69 00      ADC #$00      
    $163F: 8D 1A 10   STA $101a     
    $1642: C9 0F      CMP #$0f      
    $1644: D0 05      BNE $164b        ; → L_164B
    $1646: A9 00      LDA #$00      
    $1648: 8D 54 18   STA $1854     
L_164B:
    $164B: AD 1A 10   LDA $101a     
    $164E: 0D 18 10   ORA $1018     
    $1651: 8D 18 D4   STA $d418      ;VOL
sub_1654:
    $1654: BC FD 17   LDY $17fd,x   
    $1657: B9 25 23   LDA $2325,y   
    $165A: C9 90      CMP #$90      
    $165C: D0 0A      BNE $1668        ; → L_1668
    $165E: B9 64 23   LDA $2364,y   
    $1661: 9D FD 17   STA $17fd,x   
    $1664: A8         TAY           
    $1665: B9 25 23   LDA $2325,y   
L_1668:
    $1668: 9D 1E 18   STA $181e,x   
    $166B: 29 08      AND #$08      
    $166D: F0 0E      BEQ $167d        ; → L_167D
    $166F: B9 64 23   LDA $2364,y   
    $1672: 9D 1B 18   STA $181b,x   
    $1675: A9 00      LDA #$00      
    $1677: 9D 18 18   STA $1818,x   
    $167A: 4C 96 16   JMP $1696        ; → L_1696
L_167D:
    $167D: B9 64 23   LDA $2364,y   
    $1680: 18         CLC           
    $1681: 7D 12 10   ADC $1012,x   
    $1684: A8         TAY           
    $1685: B9 19 17   LDA $1719,y   
    $1688: 7D 42 18   ADC $1842,x   
    $168B: 9D 18 18   STA $1818,x   
    $168E: B9 79 17   LDA $1779,y   
    $1691: 69 00      ADC #$00      
    $1693: 9D 1B 18   STA $181b,x   
L_1696:
    $1696: BD 48 18   LDA $1848,x   
    $1699: F0 06      BEQ $16a1        ; → L_16A1
    $169B: DE 48 18   DEC $1848,x   
    $169E: 4C AA 16   JMP $16aa        ; → L_16AA
L_16A1:
    $16A1: FE FD 17   INC $17fd,x   
    $16A4: BD 45 18   LDA $1845,x   
    $16A7: 9D 48 18   STA $1848,x   
L_16AA:
    $16AA: BC 0C 10   LDY $100c,x   
    $16AD: BD 27 18   LDA $1827,x   
    $16B0: C9 FE      CMP #$fe      
    $16B2: F0 3C      BEQ $16f0        ; → L_16F0
    $16B4: C9 FA      CMP #$fa      
    $16B6: F0 38      BEQ $16f0        ; → L_16F0
    $16B8: C9 F4      CMP #$f4      
    $16BA: F0 34      BEQ $16f0        ; → L_16F0
    $16BC: C9 F5      CMP #$f5      
    $16BE: F0 2B      BEQ $16eb        ; → L_16EB
    $16C0: C9 F3      CMP #$f3      
    $16C2: B0 02      BCS $16c6        ; → L_16C6
    $16C4: 30 2A      BMI $16f0        ; → L_16F0
L_16C6:
    $16C6: BD F4 17   LDA $17f4,x   
    $16C9: D0 25      BNE $16f0        ; → L_16F0
L_16CB:
    $16CB: BD E5 17   LDA $17e5,x   
    $16CE: C9 01      CMP #$01      
    $16D0: D0 08      BNE $16da        ; → L_16DA
    $16D2: A9 00      LDA #$00      
    $16D4: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $16D7: 4C F0 16   JMP $16f0        ; → L_16F0
L_16DA:
    $16DA: C9 02      CMP #$02      
    $16DC: D0 12      BNE $16f0        ; → L_16F0
    $16DE: AD 16 10   LDA $1016     
    $16E1: D0 0D      BNE $16f0        ; → L_16F0
    $16E3: A9 F6      LDA #$f6      
    $16E5: 9D 21 18   STA $1821,x   
    $16E8: 4C F0 16   JMP $16f0        ; → L_16F0
L_16EB:
    $16EB: BD F4 17   LDA $17f4,x   
    $16EE: D0 DB      BNE $16cb        ; → L_16CB
L_16F0:
    $16F0: BD 18 18   LDA $1818,x   
    $16F3: 18         CLC           
    $16F4: 7D 3C 18   ADC $183c,x   
    $16F7: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $16FA: BD 1B 18   LDA $181b,x   
    $16FD: 7D 3F 18   ADC $183f,x   
    $1700: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1703: BD 2A 18   LDA $182a,x   
    $1706: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $1709: BD 2D 18   LDA $182d,x   
    $170C: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $170F: BD 1E 18   LDA $181e,x   
    $1712: 3D 21 18   AND $1821,x   
    $1715: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $1718: 60         RTS           
; ----- data gap $1719-$2458 (3392 bytes) -----

