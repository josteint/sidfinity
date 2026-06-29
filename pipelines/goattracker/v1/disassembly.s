; ============================================================================
; GoatTracker V1 (original 1.x, Cadaver) — CANARY: Topaz/Joker
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/T/Topaz/Joker.sid  (single-subtune, load $1000)
; Load:   $1000   Init: $1000   Play: $1003
; Player version: V1.5 (delayed-wave cmp #$08 @ $1155; testbit HR present)
;
; REFERENCE (annotate against these — do NOT re-derive from scratch):
;   pipelines/goattracker/docs/src/v1_player1_v153.s  (V1.5 std playroutine source)
;   pipelines/goattracker/docs/v1_README.md           (V1 index + V1-vs-V2 table)
;   The seed labels (L_xxxx/sub_xxxx) are placeholders; replace with the mt_*
;   names from v1_player1_v153.s.
;
; Structure already identified:
;   $1000 init -> $1006: deferred-init subtune setup (STA subtune; ASL; ADC #0;
;                        STA play-operand) — real song init runs on 1st play().
;   $1003 play -> $1040: frame loop (save $fc/$fd zp; LDY #N multispeed counter;
;                        first-play JSR $12EA = deferred song init).
;
; Auto-traced 880 reachable code bytes from init+play.
;
; SEED LABEL → SOURCE (v1_player1_v153.s) cross-reference:
;   init       = init (sta init_adc+1; asl; adc; sta mt_chnloop+1)
;   play→$1040 = play (save $fc/$fd; filter exec; channel loop X=0,7,14)
;   sub_12EA   = first-play deferred song-init / sequencer region
;
; VALIDATED TABLE-BASE MAP (canary Joker; read from the player's lda <tbl>,Y
; operands — this is the per-tune relocation the extractor must read):
;   instruments  $1553  (8-byte records, stride 8: AD,SR,pulse,pulsespd,
;                         pulselow,pulsehigh,filter,wave = base+0..+7)
;     instad $1553 instsr $1554 instpulse $1555 instpulsespd $1556
;     instpulselow $1557 instpulsehigh $1558 instfilter $1559 instwave $155a
;   wavetbl      $157a   (left col: waveform $08-$FF / delay $00-$07)
;   notetbl      $158a   (right col: note rel(bit7=0)/abs(bit7=1))
;   patttbllo    $159b   patttblhi $159e   (→ 3 patterns here)
;   song table + filttbl: $160F-$1612 region (deferred-init reads them)
;   freqtbllo/hi: PLAYER CONSTANT (baked, 96 entries) — not per-tune.
;   Song globals (gatetimer, HR AD/SR): patched immediates — see RE_NOTES §6.
;
; The player body is byte-identical across V1.5 tunes modulo relocation +
; these patched operands/immediates → the extractor reads each table base from
; the fixed instruction offset relative to play (dataflow, not heuristics).
; Full semantics + extraction plan: RE_NOTES.md.
; ============================================================================

; ======= init: =======
init:
    $1000: 4C 06 10   JMP $1006        ; → L_1006
; ======= play: =======
play:
    $1003: 4C 40 10   JMP $1040        ; → L_1040
L_1006:
    $1006: 8D 0B 10   STA $100b     
    $1009: 0A         ASL a         
    $100A: 69 00      ADC #$00      
    $100C: 8D 74 10   STA $1074     
    $100F: 60         RTS           
; ----- data gap $1010-$103F (48 bytes) -----

L_1040:
    $1040: A5 FC      LDA $fc       
    $1042: 48         PHA           
    $1043: A5 FD      LDA $fd       
    $1045: 48         PHA           
    $1046: A0 00      LDY #$00      
    $1048: D0 0A      BNE $1054        ; → L_1054
    $104A: A9 00      LDA #$00      
    $104C: F0 12      BEQ $1060        ; → L_1060
    $104E: 20 EA 12   JSR $12ea        ; → sub_12EA
    $1051: 4C 60 10   JMP $1060        ; → L_1060
L_1054:
    $1054: CE 47 10   DEC $1047     
    $1057: AD 61 10   LDA $1061     
    $105A: 18         CLC           
    $105B: 69 00      ADC #$00      
    $105D: 8D 61 10   STA $1061     
L_1060:
    $1060: A9 00      LDA #$00      
    $1062: 8D 16 D4   STA $d416      ;FC_HI
    $1065: A9 00      LDA #$00      
    $1067: 8D 17 D4   STA $d417      ;RES_FILT
    $106A: A9 00      LDA #$00      
    $106C: 29 FF      AND #$ff      
    $106E: 8D 18 D4   STA $d418      ;VOL
    $1071: A2 00      LDX #$00      
L_1073:
    $1073: A9 00      LDA #$00      
    $1075: 30 2C      BMI $10a3        ; → L_10A3
    $1077: 9D 87 14   STA $1487,x   
    $107A: EE 74 10   INC $1074     
    $107D: 8A         TXA           
    $107E: D0 0E      BNE $108e        ; → L_108E
    $1080: A2 15      LDX #$15      
L_1082:
    $1082: 9D 46 14   STA $1446,x   
    $1085: CA         DEX           
    $1086: D0 FA      BNE $1082        ; → L_1082
    $1088: 8D 15 D4   STA $d415      ;FC_LO
    $108B: 20 EA 12   JSR $12ea        ; → sub_12EA
L_108E:
    $108E: A9 05      LDA #$05      
    $1090: 9D 8A 14   STA $148a,x   
    $1093: A9 04      LDA #$04      
    $1095: 9D 89 14   STA $1489,x   
    $1098: A9 FF      LDA #$ff      
    $109A: 9D 4D 14   STA $144d,x   
    $109D: 9D 76 14   STA $1476,x   
    $10A0: 4C 72 12   JMP $1272        ; → L_1272
L_10A3:
    $10A3: DE 89 14   DEC $1489,x   
    $10A6: F0 2E      BEQ $10d6        ; → L_10D6
    $10A8: 10 13      BPL $10bd        ; → L_10BD
    $10AA: BD 8A 14   LDA $148a,x   
    $10AD: C9 02      CMP #$02      
    $10AF: B0 09      BCS $10ba        ; → L_10BA
    $10B1: A8         TAY           
    $10B2: 49 01      EOR #$01      
    $10B4: 9D 8A 14   STA $148a,x   
    $10B7: B9 44 14   LDA $1444,y   
L_10BA:
    $10BA: 9D 89 14   STA $1489,x   
L_10BD:
    $10BD: BC 48 14   LDY $1448,x   
    $10C0: D0 11      BNE $10d3        ; → L_10D3
    $10C2: 84 FD      STY $fd       
    $10C4: BC 73 14   LDY $1473,x   
    $10C7: B9 18 10   LDA $1018,y   
    $10CA: 8D D1 10   STA $10d1     
    $10CD: BD 74 14   LDA $1474,x   
    $10D0: 4C 18 13   JMP $1318        ; → L_1318
L_10D3:
    $10D3: 4C 52 11   JMP $1152        ; → L_1152
L_10D6:
    $10D6: BD 71 14   LDA $1471,x   
    $10D9: A8         TAY           
    $10DA: 29 F8      AND #$f8      
    $10DC: F0 03      BEQ $10e1        ; → L_10E1
    $10DE: 9D 77 14   STA $1477,x   
L_10E1:
    $10E1: 98         TYA           
    $10E2: 29 07      AND #$07      
    $10E4: 9D 73 14   STA $1473,x   
    $10E7: A8         TAY           
    $10E8: B9 10 10   LDA $1010,y   
    $10EB: 8D F5 10   STA $10f5     
    $10EE: BD 72 14   LDA $1472,x   
    $10F1: 9D 74 14   STA $1474,x   
    $10F4: 4C DF 13   JMP $13df        ; → L_13DF
L_10F7:
    $10F7: BD 76 14   LDA $1476,x   
    $10FA: 30 51      BMI $114d        ; → L_114D
    $10FC: 9D 75 14   STA $1475,x   
    $10FF: A9 FF      LDA #$ff      
    $1101: 9D 76 14   STA $1476,x   
    $1104: 9D 62 14   STA $1462,x   
    $1107: BC 77 14   LDY $1477,x   
    $110A: B9 55 15   LDA $1555,y   
    $110D: F0 12      BEQ $1121        ; → L_1121
    $110F: 48         PHA           
    $1110: 29 F0      AND #$f0      
    $1112: 9D 5F 14   STA $145f,x   
    $1115: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $1118: 68         PLA           
    $1119: 29 0F      AND #$0f      
    $111B: 9D 5E 14   STA $145e,x   
    $111E: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
L_1121:
    $1121: B9 5A 15   LDA $155a,y   
    $1124: 9D 48 14   STA $1448,x   
    $1127: B9 53 15   LDA $1553,y   
    $112A: 9D 05 D4   STA $d405,x    ;V1_AD,X
    $112D: BD 73 14   LDA $1473,x   
    $1130: C9 06      CMP #$06      
    $1132: F0 06      BEQ $113a        ; → L_113A
    $1134: B9 54 15   LDA $1554,y   
    $1137: 9D 06 D4   STA $d406,x    ;V1_SR,X
L_113A:
    $113A: A9 09      LDA #$09      
    $113C: 9D 47 14   STA $1447,x   
    $113F: 9D 04 D4   STA $d404,x    ;V1_CTRL,X
    $1142: B9 59 15   LDA $1559,y   
    $1145: F0 03      BEQ $114a        ; → L_114A
    $1147: 20 EA 12   JSR $12ea        ; → sub_12EA
L_114A:
    $114A: 4C 87 12   JMP $1287        ; → L_1287
L_114D:
    $114D: BC 48 14   LDY $1448,x   
    $1150: F0 4F      BEQ $11a1        ; → L_11A1
L_1152:
    $1152: B9 7A 15   LDA $157a,y   
    $1155: C9 08      CMP #$08      
    $1157: B0 0A      BCS $1163        ; → L_1163
    $1159: DD 86 14   CMP $1486,x   
    $115C: F0 08      BEQ $1166        ; → L_1166
    $115E: FE 86 14   INC $1486,x   
    $1161: D0 3E      BNE $11a1        ; → L_11A1
L_1163:
    $1163: 9D 47 14   STA $1447,x   
L_1166:
    $1166: B9 8A 15   LDA $158a,y   
    $1169: 30 04      BMI $116f        ; → L_116F
    $116B: 18         CLC           
    $116C: 7D 75 14   ADC $1475,x   
L_116F:
    $116F: 29 7F      AND #$7f      
    $1171: 85 FC      STA $fc       
    $1173: B9 7B 15   LDA $157b,y   
    $1176: C9 FF      CMP #$ff      
    $1178: 90 0F      BCC $1189        ; → L_1189
    $117A: B9 8B 15   LDA $158b,y   
    $117D: F0 0C      BEQ $118b        ; → L_118B
    $117F: BC 77 14   LDY $1477,x   
    $1182: 79 5A 15   ADC $155a,y   
    $1185: 69 FE      ADC #$fe      
    $1187: D0 02      BNE $118b        ; → L_118B
L_1189:
    $1189: C8         INY           
    $118A: 98         TYA           
L_118B:
    $118B: 9D 48 14   STA $1448,x   
    $118E: A4 FC      LDY $fc       
    $1190: A9 00      LDA #$00      
    $1192: 9D 86 14   STA $1486,x   
    $1195: B9 FB 14   LDA $14fb,y   
    $1198: 9D 5C 14   STA $145c,x   
    $119B: B9 9B 14   LDA $149b,y   
    $119E: 9D 5D 14   STA $145d,x   
L_11A1:
    $11A1: BD 89 14   LDA $1489,x   
    $11A4: C9 02      CMP #$02      
    $11A6: F0 60      BEQ $1208        ; → L_1208
    $11A8: BD 4D 14   LDA $144d,x   
    $11AB: C9 FF      CMP #$ff      
    $11AD: D0 03      BNE $11b2        ; → L_11B2
    $11AF: 4C 9E 12   JMP $129e        ; → L_129E
L_11B2:
    $11B2: BC 77 14   LDY $1477,x   
    $11B5: B9 56 15   LDA $1556,y   
    $11B8: 29 FE      AND #$fe      
    $11BA: F0 36      BEQ $11f2        ; → L_11F2
    $11BC: 85 FC      STA $fc       
    $11BE: BD 5F 14   LDA $145f,x   
    $11C1: 4A         LSR a         
    $11C2: B0 12      BCS $11d6        ; → L_11D6
    $11C4: 0A         ASL a         
    $11C5: 65 FC      ADC $fc       
    $11C7: 48         PHA           
    $11C8: BD 5E 14   LDA $145e,x   
    $11CB: 69 00      ADC #$00      
    $11CD: 9D 5E 14   STA $145e,x   
    $11D0: D9 58 15   CMP $1558,y   
    $11D3: 4C E6 11   JMP $11e6        ; → L_11E6
L_11D6:
    $11D6: 0A         ASL a         
    $11D7: 38         SEC           
    $11D8: E5 FC      SBC $fc       
    $11DA: 48         PHA           
    $11DB: BD 5E 14   LDA $145e,x   
    $11DE: E9 00      SBC #$00      
    $11E0: 9D 5E 14   STA $145e,x   
    $11E3: D9 57 15   CMP $1557,y   
L_11E6:
    $11E6: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $11E9: 68         PLA           
    $11EA: 69 00      ADC #$00      
    $11EC: 9D 5F 14   STA $145f,x   
    $11EF: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
L_11F2:
    $11F2: 4C 72 12   JMP $1272        ; → L_1272
L_11F5:
    $11F5: BC 49 14   LDY $1449,x   
    $11F8: D0 03      BNE $11fd        ; → L_11FD
    $11FA: 9D 49 14   STA $1449,x   
L_11FD:
    $11FD: FE 49 14   INC $1449,x   
    $1200: D0 03      BNE $1205        ; → L_1205
    $1202: FE 4D 14   INC $144d,x   
L_1205:
    $1205: 4C 72 12   JMP $1272        ; → L_1272
L_1208:
    $1208: BC 88 14   LDY $1488,x   
    $120B: B9 A1 15   LDA $15a1,y   
    $120E: 85 FC      STA $fc       
    $1210: B9 D8 15   LDA $15d8,y   
    $1213: 85 FD      STA $fd       
    $1215: BC 4D 14   LDY $144d,x   
    $1218: B1 FC      LDA ($fc),y   
    $121A: C8         INY           
    $121B: C9 60      CMP #$60      
    $121D: 90 0B      BCC $122a        ; → L_122A
    $121F: C9 C0      CMP #$c0      
    $1221: B0 D2      BCS $11f5        ; → L_11F5
    $1223: E9 5F      SBC #$5f      
    $1225: 8D 44 12   STA $1244     
    $1228: B0 0F      BCS $1239        ; → L_1239
L_122A:
    $122A: 8D 44 12   STA $1244     
    $122D: B1 FC      LDA ($fc),y   
    $122F: 9D 71 14   STA $1471,x   
    $1232: C8         INY           
    $1233: B1 FC      LDA ($fc),y   
    $1235: 9D 72 14   STA $1472,x   
    $1238: C8         INY           
L_1239:
    $1239: B1 FC      LDA ($fc),y   
    $123B: C9 FF      CMP #$ff      
    $123D: F0 01      BEQ $1240        ; → L_1240
    $123F: 98         TYA           
L_1240:
    $1240: 9D 4D 14   STA $144d,x   
    $1243: A9 00      LDA #$00      
    $1245: C9 5E      CMP #$5e      
    $1247: F0 24      BEQ $126d        ; → L_126D
    $1249: B0 27      BCS $1272        ; → L_1272
    $124B: 7D 4B 14   ADC $144b,x   
    $124E: 9D 76 14   STA $1476,x   
    $1251: BD 71 14   LDA $1471,x   
    $1254: 29 07      AND #$07      
    $1256: C9 03      CMP #$03      
    $1258: F0 18      BEQ $1272        ; → L_1272
    $125A: BC 77 14   LDY $1477,x   
    $125D: B9 56 15   LDA $1556,y   
    $1260: 4A         LSR a         
    $1261: B0 0A      BCS $126d        ; → L_126D
    $1263: A9 0F      LDA #$0f      
    $1265: 9D 05 D4   STA $d405,x    ;V1_AD,X
    $1268: A9 00      LDA #$00      
    $126A: 9D 06 D4   STA $d406,x    ;V1_SR,X
L_126D:
    $126D: A9 FE      LDA #$fe      
    $126F: 9D 62 14   STA $1462,x   
L_1272:
    $1272: BD 5C 14   LDA $145c,x   
    $1275: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $1278: BD 5D 14   LDA $145d,x   
    $127B: 9D 01 D4   STA $d401,x    ;V1_FREQ_HI,X
    $127E: BD 47 14   LDA $1447,x   
    $1281: 3D 62 14   AND $1462,x   
    $1284: 9D 04 D4   STA $d404,x    ;V1_CTRL,X
L_1287:
    $1287: E0 0E      CPX #$0e      
    $1289: B0 07      BCS $1292        ; → L_1292
    $128B: 8A         TXA           
    $128C: 69 07      ADC #$07      
    $128E: AA         TAX           
    $128F: 4C 73 10   JMP $1073        ; → L_1073
L_1292:
    $1292: A9 FF      LDA #$ff      
    $1294: 8D 74 10   STA $1074     
    $1297: 68         PLA           
    $1298: 85 FD      STA $fd       
    $129A: 68         PLA           
    $129B: 85 FC      STA $fc       
    $129D: 60         RTS           
L_129E:
    $129E: BC 87 14   LDY $1487,x   
    $12A1: B9 9B 15   LDA $159b,y   
    $12A4: 85 FC      STA $fc       
    $12A6: B9 9E 15   LDA $159e,y   
    $12A9: 85 FD      STA $fd       
    $12AB: BD 4A 14   LDA $144a,x   
    $12AE: F0 06      BEQ $12b6        ; → L_12B6
    $12B0: DE 4A 14   DEC $144a,x   
    $12B3: 4C E4 12   JMP $12e4        ; → L_12E4
L_12B6:
    $12B6: BC 4C 14   LDY $144c,x   
L_12B9:
    $12B9: B1 FC      LDA ($fc),y   
    $12BB: C8         INY           
    $12BC: C9 D0      CMP #$d0      
    $12BE: 90 1D      BCC $12dd        ; → L_12DD
    $12C0: C9 E0      CMP #$e0      
    $12C2: B0 07      BCS $12cb        ; → L_12CB
    $12C4: E9 CF      SBC #$cf      
    $12C6: 9D 4A 14   STA $144a,x   
    $12C9: B0 EE      BCS $12b9        ; → L_12B9
L_12CB:
    $12CB: C9 FF      CMP #$ff      
    $12CD: 90 06      BCC $12d5        ; → L_12D5
    $12CF: B1 FC      LDA ($fc),y   
    $12D1: A8         TAY           
    $12D2: 4C B9 12   JMP $12b9        ; → L_12B9
L_12D5:
    $12D5: E9 EF      SBC #$ef      
    $12D7: 9D 4B 14   STA $144b,x   
    $12DA: 4C B9 12   JMP $12b9        ; → L_12B9
L_12DD:
    $12DD: 9D 88 14   STA $1488,x   
    $12E0: 98         TYA           
    $12E1: 9D 4C 14   STA $144c,x   
L_12E4:
    $12E4: FE 4D 14   INC $144d,x   
    $12E7: 4C 72 12   JMP $1272        ; → L_1272
sub_12EA:
    $12EA: A8         TAY           
    $12EB: B9 0F 16   LDA $160f,y   
    $12EE: F0 15      BEQ $1305        ; → L_1305
    $12F0: 8D 66 10   STA $1066     
    $12F3: B9 10 16   LDA $1610,y   
    $12F6: 8D 6B 10   STA $106b     
    $12F9: B9 11 16   LDA $1611,y   
    $12FC: F0 03      BEQ $1301        ; → L_1301
    $12FE: 8D 61 10   STA $1061     
L_1301:
    $1301: A9 00      LDA #$00      
    $1303: F0 09      BEQ $130e        ; → L_130E
L_1305:
    $1305: B9 11 16   LDA $1611,y   
    $1308: 8D 5C 10   STA $105c     
    $130B: B9 10 16   LDA $1610,y   
L_130E:
    $130E: 8D 47 10   STA $1047     
    $1311: B9 12 16   LDA $1612,y   
    $1314: 8D 4B 10   STA $104b     
    $1317: 60         RTS           
L_1318:
    $1318: 20 3B 14   JSR $143b        ; → sub_143B
    $131B: 90 59      BCC $1376        ; → L_1376
    $131D: 20 3B 14   JSR $143b        ; → sub_143B
    $1320: 38         SEC           
    $1321: B0 71      BCS $1394        ; → L_1394
    $1323: A8         TAY           
    $1324: 29 F0      AND #$f0      
    $1326: 85 FC      STA $fc       
    $1328: 98         TYA           
    $1329: 29 0F      AND #$0f      
    $132B: 8D 34 13   STA $1334     
    $132E: BD 86 14   LDA $1486,x   
    $1331: 30 08      BMI $133b        ; → L_133B
    $1333: C9 00      CMP #$00      
    $1335: 90 05      BCC $133c        ; → L_133C
    $1337: F0 02      BEQ $133b        ; → L_133B
    $1339: 49 FF      EOR #$ff      
L_133B:
    $133B: 18         CLC           
L_133C:
    $133C: 69 02      ADC #$02      
    $133E: 9D 86 14   STA $1486,x   
    $1341: 4A         LSR a         
    $1342: 90 32      BCC $1376        ; → L_1376
    $1344: B0 4E      BCS $1394        ; → L_1394
    $1346: 4C A1 11   JMP $11a1        ; → L_11A1
; ----- data gap $1349-$1375 (45 bytes) -----

L_1376:
    $1376: BD 5C 14   LDA $145c,x   
    $1379: 65 FC      ADC $fc       
    $137B: 9D 5C 14   STA $145c,x   
    $137E: BD 5D 14   LDA $145d,x   
    $1381: 65 FD      ADC $fd       
    $1383: 9D 5D 14   STA $145d,x   
    $1386: 4C A1 11   JMP $11a1        ; → L_11A1
; ----- data gap $1389-$1393 (11 bytes) -----

L_1394:
    $1394: BD 5C 14   LDA $145c,x   
    $1397: E5 FC      SBC $fc       
    $1399: 9D 5C 14   STA $145c,x   
    $139C: BD 5D 14   LDA $145d,x   
    $139F: E5 FD      SBC $fd       
    $13A1: 9D 5D 14   STA $145d,x   
    $13A4: 4C A1 11   JMP $11a1        ; → L_11A1
; ----- data gap $13A7-$13DE (56 bytes) -----

L_13DF:
    $13DF: 30 0C      BMI $13ed        ; → L_13ED
    $13E1: 8D 8A 14   STA $148a     
    $13E4: 8D 91 14   STA $1491     
    $13E7: 8D 98 14   STA $1498     
    $13EA: 4C F7 10   JMP $10f7        ; → L_10F7
L_13ED:
    $13ED: C9 EF      CMP #$ef      
    $13EF: F0 0A      BEQ $13fb        ; → L_13FB
    $13F1: B0 0E      BCS $1401        ; → L_1401
    $13F3: 29 7F      AND #$7f      
    $13F5: 9D 8A 14   STA $148a,x   
    $13F8: 4C F7 10   JMP $10f7        ; → L_10F7
L_13FB:
    $13FB: EE 46 14   INC $1446     
    $13FE: 4C F7 10   JMP $10f7        ; → L_10F7
L_1401:
    $1401: 8D 6D 10   STA $106d     
    $1404: 4C F7 10   JMP $10f7        ; → L_10F7
; ----- data gap $1407-$143A (52 bytes) -----

sub_143B:
    $143B: 0A         ASL a         
    $143C: 26 FD      ROL $fd       
    $143E: 0A         ASL a         
    $143F: 26 FD      ROL $fd       
    $1441: 85 FC      STA $fc       
    $1443: 60         RTS           
; ----- data gap $1444-$1C3D (2042 bytes) -----

