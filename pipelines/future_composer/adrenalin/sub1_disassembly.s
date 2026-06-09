; ============================================================================
; Adrenalin (HeatWave) — SUB 1 engine @ $1021  (post-init memory snapshot)
; ============================================================================
;
; Source: _run_init_in_py65(Adrenalin.sid, subtune=1) → 64K image, region
;         $1000-$1AFF dumped + wrapped as a PSID for seed_disassembly.
; Auto-traced 801 reachable code bytes from play=$1021.
;
; VERDICT: this IS a Future Composer engine — a DIFFERENT VARIANT from engine A
; (subs 0/2/3), NOT a foreign player. The earlier "4% code-identical to engine
; A" was layout/variant divergence, not a different family. FC signatures:
;   - 8-byte instrument records at $192C ($192c=SRlo? $192d=AD, $192e=ctrl,
;     $192f, $1930, $1931, $1932, $1933) — read in sub_1226 (the per-voice step)
;   - 3 voices indexed by X=0..2; per-voice SID offset d4point = $10C6,x (0/7/14)
;   - pattern streams read via ($fa),y with FC command ranges: note < $60,
;     $60-$9F wave-pos/setlen, $A0+ effects (CMP #$60 / CMP #$A0 at $10B2/$10D2)
;   - per-voice sequence (orderlist) pointers: lo $14B9,x  hi $14BC,x
;   - pattern pointer table: lo $190A,y  hi $18E8,y  (Y = current pattern id)
;   - wavetable / arp: $1437,y + $11C5,y ; effect-program ptrs $1498,y/$14A8,y
;
; ROUTINE MAP (hand-traced):
;   $1021 play/init  LDX#0; DEC speedctr $1090; BMI→$1034 (tick) else run voices
;   $1034 on-tick    reload speedctr=$02; advance all 3 voices' note-length
;   $1040 advance_v  DEC notelen $108A,x; BMI→$1091 read next pattern byte
;   $1091 read_pat   parse pattern stream byte (note/$60/$A0 command dispatch);
;                    $FE = seq-end (sub_1098 gate-off), $FF = seq-advance ($1187)
;   $1226 proc_voice per-frame voice update: load instrument $192C,y, write
;                    $D404/5/6 (ctrl/AD/SR), portamento/PW/vibrato, freq → $D400/1
;   $13E5 wave_step  walk the wavetable/effect program ($1498/$14A8 ptr)
;
; KEY STATE (X-indexed per-voice arrays in $10xx/$11xx/$12xx/$13xx):
;   $108A notelen  $108D patidx  $1081 patcursor  $1084 ctrl  $10C6 d4point
;   $10CC/$10CF freq lo/hi  $13DC/$13DF PW  $13E2/$12B6 freq-accum (portamento)
;   $1141 voice-flags  $114D wave-step-ctr  speed reload = $02 @ $1034
;
; DATA TABLES (in the $1437-$1AFF gap): wavetables $1437+, instruments $192C+,
;   pattern-ptr $18E8/$190A, instrument-records $192C, sequences $14B9/$14BC.
;
; IMPLICATION: sub 1 is migratable as an FC config (its own addresses + maybe a
; variant knob), and potentially unifiable with engine A per the 5TT pattern.
; Next: confirm the instrument/pattern/sequence byte layouts, then extract.
; ============================================================================

; ----- data gap $1000-$1020 (33 bytes) -----

; ======= init: =======
init:
    $1021: A2 00      LDX #$00      
    $1023: CE 90 10   DEC $1090     
    $1026: 30 0C      BMI $1034        ; → L_1034
    $1028: 20 26 12   JSR $1226        ; → sub_1226
    $102B: 20 25 12   JSR $1225        ; → sub_1225
    $102E: 4C 25 12   JMP $1225        ; → sub_1225
; ----- data gap $1031-$1033 (3 bytes) -----

L_1034:
    $1034: A9 02      LDA #$02      
    $1036: 8D 90 10   STA $1090     
    $1039: 20 40 10   JSR $1040        ; → sub_1040
    $103C: 20 3F 10   JSR $103f        ; → sub_103F
sub_103F:
    $103F: E8         INX           
sub_1040:
    $1040: DE 8A 10   DEC $108a,x   
    $1043: 30 4C      BMI $1091        ; → L_1091
    $1045: 4C 26 12   JMP $1226        ; → sub_1226
; ----- data gap $1048-$1090 (73 bytes) -----

L_1091:
    $1091: BC 8D 10   LDY $108d,x   
    $1094: C0 FE      CPY #$fe      
    $1096: D0 09      BNE $10a1        ; → L_10A1
sub_1098:
    $1098: BD 84 10   LDA $1084,x   
    $109B: 29 FE      AND #$fe      
    $109D: 9D 84 10   STA $1084,x   
    $10A0: 60         RTS           
L_10A1:
    $10A1: B9 0A 19   LDA $190a,y   
    $10A4: 85 FA      STA $fa       
    $10A6: B9 E8 18   LDA $18e8,y   
    $10A9: 85 FB      STA $fb       
    $10AB: BC 81 10   LDY $1081,x   
    $10AE: B1 FA      LDA ($fa),y   
    $10B0: 30 20      BMI $10d2        ; → L_10D2
    $10B2: C9 60      CMP #$60      
    $10B4: 90 43      BCC $10f9        ; → L_10F9
L_10B6:
    $10B6: 29 1F      AND #$1f      
    $10B8: 9D 8A 10   STA $108a,x   
    $10BB: A9 FE      LDA #$fe      
    $10BD: 9D 31 10   STA $1031,x   
    $10C0: 20 98 10   JSR $1098        ; → sub_1098
L_10C3:
    $10C3: 4C 87 11   JMP $1187        ; → L_1187
; ----- data gap $10C6-$10D1 (12 bytes) -----

L_10D2:
    $10D2: C9 A0      CMP #$a0      
    $10D4: 90 16      BCC $10ec        ; → L_10EC
    $10D6: 29 1F      AND #$1f      
    $10D8: 9D 8A 10   STA $108a,x   
    $10DB: B0 E6      BCS $10c3        ; → L_10C3
    $10DD: 00         BRK           
; ----- data gap $10DE-$10EB (14 bytes) -----

L_10EC:
    $10EC: 0A         ASL a         
    $10ED: 0A         ASL a         
    $10EE: 0A         ASL a         
    $10EF: 9D D9 13   STA $13d9,x   
    $10F2: C8         INY           
    $10F3: B1 FA      LDA ($fa),y   
    $10F5: C9 60      CMP #$60      
    $10F7: B0 BD      BCS $10b6        ; → L_10B6
L_10F9:
    $10F9: 85 FC      STA $fc       
    $10FB: C8         INY           
    $10FC: BD E6 10   LDA $10e6,x   
    $10FF: 4A         LSR a         
    $1100: 4A         LSR a         
    $1101: 4A         LSR a         
    $1102: 4A         LSR a         
    $1103: 18         CLC           
    $1104: 65 FC      ADC $fc       
    $1106: 9D C9 10   STA $10c9,x   
    $1109: 84 FC      STY $fc       
    $110B: A8         TAY           
    $110C: B9 37 14   LDA $1437,y   
    $110F: 9D CC 10   STA $10cc,x   
    $1112: 9D E2 13   STA $13e2,x   
    $1115: B9 C5 11   LDA $11c5,y   
    $1118: 9D CF 10   STA $10cf,x   
    $111B: 9D B6 12   STA $12b6,x   
    $111E: A4 FC      LDY $fc       
    $1120: B1 FA      LDA ($fa),y   
    $1122: 9D 41 11   STA $1141,x   
    $1125: 29 1F      AND #$1f      
    $1127: 9D 8A 10   STA $108a,x   
    $112A: B1 FA      LDA ($fa),y   
    $112C: 30 22      BMI $1150        ; → L_1150
    $112E: 29 20      AND #$20      
    $1130: F0 45      BEQ $1177        ; → L_1177
    $1132: C8         INY           
    $1133: B1 FA      LDA ($fa),y   
    $1135: 9D 47 11   STA $1147,x   
    $1138: C8         INY           
    $1139: B1 FA      LDA ($fa),y   
    $113B: 9D 4A 11   STA $114a,x   
    $113E: 4C 77 11   JMP $1177        ; → L_1177
; ----- data gap $1141-$114F (15 bytes) -----

L_1150:
    $1150: 8E 62 12   STX $1262     
    $1153: C8         INY           
    $1154: B1 FA      LDA ($fa),y   
    $1156: 8D 66 12   STA $1266     
    $1159: 29 0F      AND #$0f      
    $115B: 0A         ASL a         
    $115C: 38         SEC           
    $115D: E9 10      SBC #$10      
    $115F: 8D A0 12   STA $12a0     
    $1162: C8         INY           
    $1163: B1 FA      LDA ($fa),y   
    $1165: D0 07      BNE $116e        ; → L_116E
    $1167: A9 F0      LDA #$f0      
    $1169: 8D 17 D4   STA $d417      ;RES_FILT
    $116C: D0 09      BNE $1177        ; → L_1177
L_116E:
    $116E: 8D 6B 12   STA $126b     
    $1171: BD B3 12   LDA $12b3,x   
    $1174: 8D 17 D4   STA $d417      ;RES_FILT
L_1177:
    $1177: A9 FF      LDA #$ff      
    $1179: 9D 31 10   STA $1031,x   
    $117C: 9D B9 12   STA $12b9,x   
    $117F: A9 00      LDA #$00      
    $1181: 9D DD 10   STA $10dd,x   
    $1184: 9D BD 12   STA $12bd,x   
L_1187:
    $1187: C8         INY           
    $1188: B1 FA      LDA ($fa),y   
    $118A: C9 FF      CMP #$ff      
    $118C: D0 32      BNE $11c0        ; → L_11C0
    $118E: DE E9 10   DEC $10e9,x   
    $1191: 10 2B      BPL $11be        ; → L_11BE
    $1193: BD B9 14   LDA $14b9,x   
    $1196: 85 FA      STA $fa       
    $1198: BD BC 14   LDA $14bc,x   
    $119B: 85 FB      STA $fb       
    $119D: BC 87 10   LDY $1087,x   
    $11A0: C8         INY           
    $11A1: C8         INY           
    $11A2: B1 FA      LDA ($fa),y   
    $11A4: C9 FF      CMP #$ff      
    $11A6: D0 02      BNE $11aa        ; → L_11AA
    $11A8: A0 00      LDY #$00      
L_11AA:
    $11AA: 98         TYA           
    $11AB: 9D 87 10   STA $1087,x   
    $11AE: B1 FA      LDA ($fa),y   
    $11B0: 9D 8D 10   STA $108d,x   
    $11B3: C8         INY           
    $11B4: B1 FA      LDA ($fa),y   
    $11B6: 9D E6 10   STA $10e6,x   
    $11B9: 29 0F      AND #$0f      
    $11BB: 9D E9 10   STA $10e9,x   
L_11BE:
    $11BE: A0 00      LDY #$00      
L_11C0:
    $11C0: 98         TYA           
    $11C1: 9D 81 10   STA $1081,x   
    $11C4: 60         RTS           
; ----- data gap $11C5-$1224 (96 bytes) -----

sub_1225:
    $1225: E8         INX           
sub_1226:
    $1226: BC D9 13   LDY $13d9,x   
    $1229: 84 FC      STY $fc       
    $122B: BD 41 11   LDA $1141,x   
    $122E: 29 40      AND #$40      
    $1230: D0 5E      BNE $1290        ; → L_1290
    $1232: 9D 44 11   STA $1144,x   
    $1235: B9 2C 19   LDA $192c,y   
    $1238: 85 FA      STA $fa       
    $123A: B9 2D 19   LDA $192d,y   
    $123D: BC C6 10   LDY $10c6,x   
    $1240: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $1243: A5 FA      LDA $fa       
    $1245: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $1248: BD 84 10   LDA $1084,x   
    $124B: 29 FE      AND #$fe      
    $124D: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $1250: A4 FC      LDY $fc       
    $1252: B9 2E 19   LDA $192e,y   
    $1255: 9D 84 10   STA $1084,x   
    $1258: B9 2F 19   LDA $192f,y   
    $125B: 9D DC 13   STA $13dc,x   
    $125E: 9D DF 13   STA $13df,x   
    $1261: E0 00      CPX #$00      
    $1263: D0 0A      BNE $126f        ; → L_126F
    $1265: A9 81      LDA #$81      
    $1267: 8D 9E 12   STA $129e     
    $126A: A9 FF      LDA #$ff      
    $126C: 8D 96 12   STA $1296     
L_126F:
    $126F: A9 00      LDA #$00      
    $1271: 9D E0 10   STA $10e0,x   
    $1274: 9D E3 10   STA $10e3,x   
    $1277: B9 31 19   LDA $1931,y   
    $127A: 4A         LSR a         
    $127B: 4A         LSR a         
    $127C: 4A         LSR a         
    $127D: 9D 4D 11   STA $114d,x   
    $1280: BD 41 11   LDA $1141,x   
    $1283: 09 40      ORA #$40      
    $1285: 9D 41 11   STA $1141,x   
    $1288: B9 33 19   LDA $1933,y   
    $128B: 95 FD      STA $fd,x     
    $128D: 4C 85 13   JMP $1385        ; → L_1385
L_1290:
    $1290: EC 62 12   CPX $1262     
    $1293: D0 12      BNE $12a7        ; → L_12A7
    $1295: A9 FC      LDA #$fc      
    $1297: F0 0E      BEQ $12a7        ; → L_12A7
    $1299: CE 96 12   DEC $1296     
    $129C: 18         CLC           
    $129D: A9 57      LDA #$57      
    $129F: 69 F2      ADC #$f2      
    $12A1: 8D 9E 12   STA $129e     
    $12A4: 8D 16 D4   STA $d416      ;FC_HI
L_12A7:
    $12A7: B5 FD      LDA $fd,x     
    $12A9: 29 0F      AND #$0f      
    $12AB: F0 1A      BEQ $12c7        ; → L_12C7
    $12AD: 20 E5 13   JSR $13e5        ; → sub_13E5
    $12B0: 4C 22 13   JMP $1322        ; → L_1322
; ----- data gap $12B3-$12C6 (20 bytes) -----

L_12C7:
    $12C7: BD 41 11   LDA $1141,x   
    $12CA: 29 20      AND #$20      
    $12CC: D0 54      BNE $1322        ; → L_1322
    $12CE: B5 FD      LDA $fd,x     
    $12D0: 29 10      AND #$10      
    $12D2: F0 4E      BEQ $1322        ; → L_1322
    $12D4: DE 4D 11   DEC $114d,x   
    $12D7: 10 49      BPL $1322        ; → L_1322
    $12D9: FE 4D 11   INC $114d,x   
    $12DC: BD BD 12   LDA $12bd,x   
    $12DF: 29 03      AND #$03      
    $12E1: A8         TAY           
    $12E2: B9 C3 12   LDA $12c3,y   
    $12E5: D0 13      BNE $12fa        ; → L_12FA
    $12E7: A4 FC      LDY $fc       
    $12E9: 38         SEC           
    $12EA: BD CC 10   LDA $10cc,x   
    $12ED: F9 32 19   SBC $1932,y   
    $12F0: 9D CC 10   STA $10cc,x   
    $12F3: B0 18      BCS $130d        ; → L_130D
    $12F5: DE CF 10   DEC $10cf,x   
    $12F8: D0 13      BNE $130d        ; → L_130D
L_12FA:
    $12FA: A4 FC      LDY $fc       
    $12FC: 18         CLC           
    $12FD: BD CC 10   LDA $10cc,x   
    $1300: 79 32 19   ADC $1932,y   
    $1303: 9D CC 10   STA $10cc,x   
    $1306: 90 05      BCC $130d        ; → L_130D
    $1308: FE CF 10   INC $10cf,x   
    $130B: B0 00      BCS $130d        ; → L_130D
L_130D:
    $130D: FE DD 10   INC $10dd,x   
    $1310: B9 31 19   LDA $1931,y   
    $1313: 29 0F      AND #$0f      
    $1315: DD DD 10   CMP $10dd,x   
    $1318: D0 08      BNE $1322        ; → L_1322
    $131A: A9 00      LDA #$00      
    $131C: 9D DD 10   STA $10dd,x   
    $131F: FE BD 12   INC $12bd,x   
L_1322:
    $1322: A4 FC      LDY $fc       
    $1324: B9 30 19   LDA $1930,y   
    $1327: 85 FC      STA $fc       
    $1329: B5 FD      LDA $fd,x     
    $132B: 29 40      AND #$40      
    $132D: F0 14      BEQ $1343        ; → L_1343
    $132F: 18         CLC           
    $1330: A5 FC      LDA $fc       
    $1332: 7D DC 13   ADC $13dc,x   
    $1335: 9D DC 13   STA $13dc,x   
    $1338: A5 FC      LDA $fc       
    $133A: 7D DF 13   ADC $13df,x   
    $133D: 9D DF 13   STA $13df,x   
    $1340: 4C 85 13   JMP $1385        ; → L_1385
L_1343:
    $1343: B5 FD      LDA $fd,x     
    $1345: 29 20      AND #$20      
    $1347: F0 3C      BEQ $1385        ; → L_1385
    $1349: BD E3 10   LDA $10e3,x   
    $134C: F0 10      BEQ $135e        ; → L_135E
    $134E: 18         CLC           
    $134F: BD DC 13   LDA $13dc,x   
    $1352: 65 FC      ADC $fc       
    $1354: 9D DC 13   STA $13dc,x   
    $1357: 90 13      BCC $136c        ; → L_136C
    $1359: FE DF 13   INC $13df,x   
    $135C: B0 0E      BCS $136c        ; → L_136C
L_135E:
    $135E: 38         SEC           
    $135F: BD DC 13   LDA $13dc,x   
    $1362: E5 FC      SBC $fc       
    $1364: 9D DC 13   STA $13dc,x   
    $1367: B0 03      BCS $136c        ; → L_136C
    $1369: DE DF 13   DEC $13df,x   
L_136C:
    $136C: FE E0 10   INC $10e0,x   
    $136F: A5 FC      LDA $fc       
    $1371: 29 0F      AND #$0f      
    $1373: DD E0 10   CMP $10e0,x   
    $1376: D0 0D      BNE $1385        ; → L_1385
    $1378: A9 00      LDA #$00      
    $137A: 9D E0 10   STA $10e0,x   
    $137D: BD E3 10   LDA $10e3,x   
    $1380: 49 01      EOR #$01      
    $1382: 9D E3 10   STA $10e3,x   
L_1385:
    $1385: BC C6 10   LDY $10c6,x   
    $1388: BD 84 10   LDA $1084,x   
    $138B: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $138E: BD DF 13   LDA $13df,x   
    $1391: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $1394: BD DC 13   LDA $13dc,x   
    $1397: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $139A: BD 41 11   LDA $1141,x   
    $139D: 29 20      AND #$20      
    $139F: F0 2B      BEQ $13cc        ; → L_13CC
    $13A1: BD 47 11   LDA $1147,x   
    $13A4: 29 01      AND #$01      
    $13A6: F0 0A      BEQ $13b2        ; → L_13B2
    $13A8: BD B9 12   LDA $12b9,x   
    $13AB: 49 FF      EOR #$ff      
    $13AD: 9D B9 12   STA $12b9,x   
    $13B0: D0 1A      BNE $13cc        ; → L_13CC
L_13B2:
    $13B2: 18         CLC           
    $13B3: BD E2 13   LDA $13e2,x   
    $13B6: 7D 47 11   ADC $1147,x   
    $13B9: 9D E2 13   STA $13e2,x   
    $13BC: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $13BF: BD B6 12   LDA $12b6,x   
    $13C2: 7D 4A 11   ADC $114a,x   
    $13C5: 9D B6 12   STA $12b6,x   
    $13C8: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $13CB: 60         RTS           
L_13CC:
    $13CC: BD CC 10   LDA $10cc,x   
    $13CF: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $13D2: BD CF 10   LDA $10cf,x   
    $13D5: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $13D8: 60         RTS           
; ----- data gap $13D9-$13E4 (12 bytes) -----

sub_13E5:
    $13E5: A8         TAY           
    $13E6: B9 98 14   LDA $1498,y   
    $13E9: 85 FA      STA $fa       
    $13EB: B9 A8 14   LDA $14a8,y   
    $13EE: 85 FB      STA $fb       
    $13F0: BC 44 11   LDY $1144,x   
    $13F3: B1 FA      LDA ($fa),y   
    $13F5: 3D 31 10   AND $1031,x   
    $13F8: 9D 84 10   STA $1084,x   
    $13FB: C8         INY           
    $13FC: B1 FA      LDA ($fa),y   
    $13FE: 30 04      BMI $1404        ; → L_1404
    $1400: 18         CLC           
    $1401: 7D C9 10   ADC $10c9,x   
L_1404:
    $1404: 29 7F      AND #$7f      
    $1406: 8D 29 14   STA $1429     
    $1409: C8         INY           
    $140A: B1 FA      LDA ($fa),y   
    $140C: F0 03      BEQ $1411        ; → L_1411
    $140E: 8D 9E 12   STA $129e     
L_1411:
    $1411: C8         INY           
    $1412: B1 FA      LDA ($fa),y   
    $1414: C9 FE      CMP #$fe      
    $1416: 90 0C      BCC $1424        ; → L_1424
    $1418: F0 04      BEQ $141e        ; → L_141E
    $141A: A0 00      LDY #$00      
    $141C: F0 06      BEQ $1424        ; → L_1424
L_141E:
    $141E: B5 FD      LDA $fd,x     
    $1420: 29 F0      AND #$f0      
    $1422: 95 FD      STA $fd,x     
L_1424:
    $1424: 98         TYA           
    $1425: 9D 44 11   STA $1144,x   
    $1428: A0 1C      LDY #$1c      
    $142A: B9 37 14   LDA $1437,y   
    $142D: 9D CC 10   STA $10cc,x   
    $1430: B9 C5 11   LDA $11c5,y   
    $1433: 9D CF 10   STA $10cf,x   
    $1436: 60         RTS           
; ----- data gap $1437-$1AFF (1737 bytes) -----

