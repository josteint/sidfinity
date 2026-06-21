; ============================================================================
; DMC V6 player — representative: DMC_V6_note by The Syndrom (the DMC author)
; ANNOTATED DISASSEMBLY (full RE in pipelines/dmc/v6/RE_NOTES.md)
; ============================================================================
; DMC V6 = internal/unreleased DMC (Brian + Syndrom/TIA); a SEPARATE player from
; V4/V5 (~0.01 fingerprint Jaccard) but the SAME musical shape v5 models.
;
; ROUTINE MAP:
;   $1050 init       — zero work block; ctrl/$D411=$08; $D418=$1F; $D417=$F2 (clean
;                      universal reset → trichotomy; matches the V6 sidid sig).
;   $107B play       — DEC $100F tick divider; per-row (new-note) vs per-frame.
;   $1086 sub        — V3 wave/arp stepper ($16C3 ctrl + $1757 freq → $D412/$D40F).
;   $10E9..$122F     — new-row path: V3 ($1105), V2 ($1173), V1 ($11DB) note fetch
;                      (orderlist → pattern-ptr → pattern stream: note / $FD dur /
;                      hi-byte instrument; $FF = pattern end → advance orderlist).
;   $1230 sub_1230   — V1 per-frame: note-on setup + PW oscillator + wave/arp +
;                      freq($153D/$159D + $FE/$FF slide); $1314 = octave pitch slide.
;   $1339 sub_1339   — V2 per-frame: filter sweep ($D416) + PW + wave/arp + freq.
;
; DATA TABLES (per-inst, 22-entry/$16 stride, indexed by instrument):
;   $15FD AD · $1613 SR · $1629 PWinit · $163F PWstep · $1655 wave-prog-ptr ·
;   $166B pitch-delay · $1681 filt-cutoff · $1697 filt-count · $16AD filt-step
; WAVE: $16C3 ctrl + $1757 note-offset ($FF=loop).  FREQ: $153D lo/$159D hi (96).
; PW:   $13FD lo/$143D hi (32+sign).  ORDERLISTS: $17EB/$1804/$1835 ($FF=wrap).
; PATTERN PTRS: $184E lo/$185E hi.   SMC: $12EB (emit clean per CORE TENET).
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/T/The_Syndrom/DMC_V6_note.sid
; Load:   $1000   Init: $1000   Play: $1003
; PSID:   1 subtune(s), default subtune 1
; Binary: $1000-$1BA0 (2977 bytes)
;
; Auto-traced 916 reachable code bytes from init+play.
;
; ============================================================================

; ======= init: =======
init:
    $1000: 4C 50 10   JMP $1050        ; → L_1050
; ======= play: =======
play:
    $1003: 4C 7B 10   JMP $107b        ; → L_107B
; ----- data gap $1006-$104F (74 bytes) -----

L_1050:
    $1050: A2 0B      LDX #$0b      
L_1052:
    $1052: A9 02      LDA #$02      
    $1054: 9D 10 10   STA $1010,x   
    $1057: A9 00      LDA #$00      
    $1059: 9D 13 10   STA $1013,x   
    $105C: CA         DEX           
    $105D: 10 F3      BPL $1052        ; → L_1052
    $105F: 8D 0F 10   STA $100f     
    $1062: A9 08      LDA #$08      
    $1064: 8D 04 D4   STA $d404      ;V1_CTRL
    $1067: 8D 0B D4   STA $d40b      ;V2_CTRL
    $106A: 8D 12 D4   STA $d412      ;V3_CTRL
    $106D: 8D 11 D4   STA $d411      ;V3_PW_HI
    $1070: A9 1F      LDA #$1f      
    $1072: 8D 18 D4   STA $d418      ;VOL
    $1075: A9 F2      LDA #$f2      
    $1077: 8D 17 D4   STA $d417      ;RES_FILT
    $107A: 60         RTS           
L_107B:
    $107B: CE 0F 10   DEC $100f     
    $107E: 30 69      BMI $10e9        ; → L_10E9
    $1080: 20 30 12   JSR $1230        ; → sub_1230
    $1083: 20 39 13   JSR $1339        ; → sub_1339
sub_1086:
    $1086: AD 1B 10   LDA $101b     
    $1089: F0 3F      BEQ $10ca        ; → L_10CA
    $108B: A9 00      LDA #$00      
    $108D: 8D 1B 10   STA $101b     
    $1090: AD 4B 10   LDA $104b     
    $1093: 8D 12 10   STA $1012     
    $1096: AC 4E 10   LDY $104e     
    $1099: B9 FD 15   LDA $15fd,y   
    $109C: 8D 13 D4   STA $d413      ;V3_AD
    $109F: B9 13 16   LDA $1613,y   
    $10A2: 8D 14 D4   STA $d414      ;V3_SR
    $10A5: BE 55 16   LDX $1655,y   
    $10A8: BD C3 16   LDA $16c3,x   
    $10AB: 8D 12 D4   STA $d412      ;V3_CTRL
    $10AE: BD 57 17   LDA $1757,x   
    $10B1: 8D 0F D4   STA $d40f      ;V3_FREQ_HI
    $10B4: E8         INX           
    $10B5: 8E 1E 10   STX $101e     
    $10B8: AC 18 10   LDY $1018     
    $10BB: B1 FC      LDA ($fc),y   
    $10BD: C9 FF      CMP #$ff      
    $10BF: D0 08      BNE $10c9        ; → L_10C9
    $10C1: EE 15 10   INC $1015     
    $10C4: A9 00      LDA #$00      
    $10C6: 8D 18 10   STA $1018     
L_10C9:
    $10C9: 60         RTS           
L_10CA:
    $10CA: AE 1E 10   LDX $101e     
    $10CD: BD C3 16   LDA $16c3,x   
    $10D0: C9 FF      CMP #$ff      
    $10D2: D0 07      BNE $10db        ; → L_10DB
    $10D4: BD 57 17   LDA $1757,x   
    $10D7: AA         TAX           
    $10D8: BD C3 16   LDA $16c3,x   
L_10DB:
    $10DB: 8D 12 D4   STA $d412      ;V3_CTRL
    $10DE: BD 57 17   LDA $1757,x   
    $10E1: 8D 0F D4   STA $d40f      ;V3_FREQ_HI
    $10E4: E8         INX           
    $10E5: 8E 1E 10   STX $101e     
    $10E8: 60         RTS           
L_10E9:
    $10E9: A9 02      LDA #$02      
    $10EB: 8D 0F 10   STA $100f     
    $10EE: CE 12 10   DEC $1012     
    $10F1: F0 12      BEQ $1105        ; → L_1105
    $10F3: AD 12 10   LDA $1012     
    $10F6: C9 01      CMP #$01      
    $10F8: D0 5F      BNE $1159        ; → L_1159
    $10FA: A9 00      LDA #$00      
    $10FC: 8D 14 D4   STA $d414      ;V3_SR
    $10FF: 20 86 10   JSR $1086        ; → sub_1086
    $1102: 4C 5C 11   JMP $115c        ; → L_115C
L_1105:
    $1105: AE 15 10   LDX $1015     
    $1108: BC 35 18   LDY $1835,x   
    $110B: C0 FF      CPY #$ff      
    $110D: D0 08      BNE $1117        ; → L_1117
    $110F: A2 00      LDX #$00      
    $1111: 8E 15 10   STX $1015     
    $1114: AC 35 18   LDY $1835     
L_1117:
    $1117: B9 4E 18   LDA $184e,y   
    $111A: 85 FC      STA $fc       
    $111C: B9 5E 18   LDA $185e,y   
    $111F: 85 FD      STA $fd       
    $1121: AC 18 10   LDY $1018     
L_1124:
    $1124: B1 FC      LDA ($fc),y   
    $1126: 10 1E      BPL $1146        ; → L_1146
    $1128: C9 FD      CMP #$fd      
    $112A: D0 0D      BNE $1139        ; → L_1139
    $112C: C8         INY           
    $112D: B1 FC      LDA ($fc),y   
    $112F: 8D 4B 10   STA $104b     
    $1132: C8         INY           
    $1133: 8C 18 10   STY $1018     
    $1136: 4C 24 11   JMP $1124        ; → L_1124
L_1139:
    $1139: C8         INY           
    $113A: B1 FC      LDA ($fc),y   
    $113C: 8D 4E 10   STA $104e     
    $113F: C8         INY           
    $1140: 8C 18 10   STY $1018     
    $1143: 4C 24 11   JMP $1124        ; → L_1124
L_1146:
    $1146: A9 08      LDA #$08      
    $1148: 8D 12 D4   STA $d412      ;V3_CTRL
    $114B: A9 0F      LDA #$0f      
    $114D: 8D 14 D4   STA $d414      ;V3_SR
    $1150: 8D 1B 10   STA $101b     
    $1153: EE 18 10   INC $1018     
    $1156: 4C 5C 11   JMP $115c        ; → L_115C
L_1159:
    $1159: 20 86 10   JSR $1086        ; → sub_1086
L_115C:
    $115C: CE 11 10   DEC $1011     
    $115F: F0 12      BEQ $1173        ; → L_1173
    $1161: AD 11 10   LDA $1011     
    $1164: C9 01      CMP #$01      
    $1166: D0 05      BNE $116d        ; → L_116D
    $1168: A9 00      LDA #$00      
    $116A: 8D 0D D4   STA $d40d      ;V2_SR
L_116D:
    $116D: 20 39 13   JSR $1339        ; → sub_1339
    $1170: 4C C7 11   JMP $11c7        ; → L_11C7
L_1173:
    $1173: AE 14 10   LDX $1014     
    $1176: BC 04 18   LDY $1804,x   
    $1179: C0 FF      CPY #$ff      
    $117B: D0 08      BNE $1185        ; → L_1185
    $117D: A2 00      LDX #$00      
    $117F: 8E 14 10   STX $1014     
    $1182: AC 04 18   LDY $1804     
L_1185:
    $1185: B9 4E 18   LDA $184e,y   
    $1188: 85 FA      STA $fa       
    $118A: B9 5E 18   LDA $185e,y   
    $118D: 85 FB      STA $fb       
    $118F: AC 17 10   LDY $1017     
L_1192:
    $1192: B1 FA      LDA ($fa),y   
    $1194: 10 1E      BPL $11b4        ; → L_11B4
    $1196: C9 FD      CMP #$fd      
    $1198: D0 0D      BNE $11a7        ; → L_11A7
    $119A: C8         INY           
    $119B: B1 FA      LDA ($fa),y   
    $119D: 8D 4A 10   STA $104a     
    $11A0: C8         INY           
    $11A1: 8C 17 10   STY $1017     
    $11A4: 4C 92 11   JMP $1192        ; → L_1192
L_11A7:
    $11A7: C8         INY           
    $11A8: B1 FA      LDA ($fa),y   
    $11AA: 8D 4D 10   STA $104d     
    $11AD: C8         INY           
    $11AE: 8C 17 10   STY $1017     
    $11B1: 4C 92 11   JMP $1192        ; → L_1192
L_11B4:
    $11B4: 8D 40 10   STA $1040     
    $11B7: A9 08      LDA #$08      
    $11B9: 8D 0B D4   STA $d40b      ;V2_CTRL
    $11BC: A9 0F      LDA #$0f      
    $11BE: 8D 0D D4   STA $d40d      ;V2_SR
    $11C1: 8D 1A 10   STA $101a     
    $11C4: EE 17 10   INC $1017     
L_11C7:
    $11C7: CE 10 10   DEC $1010     
    $11CA: F0 0F      BEQ $11db        ; → L_11DB
    $11CC: AD 10 10   LDA $1010     
    $11CF: C9 01      CMP #$01      
    $11D1: D0 5D      BNE $1230        ; → sub_1230
    $11D3: A9 00      LDA #$00      
    $11D5: 8D 06 D4   STA $d406      ;V1_SR
    $11D8: 4C 30 12   JMP $1230        ; → sub_1230
L_11DB:
    $11DB: AE 13 10   LDX $1013     
    $11DE: BC EB 17   LDY $17eb,x   
    $11E1: C0 FF      CPY #$ff      
    $11E3: D0 08      BNE $11ed        ; → L_11ED
    $11E5: A2 00      LDX #$00      
    $11E7: 8E 13 10   STX $1013     
    $11EA: AC EB 17   LDY $17eb     
L_11ED:
    $11ED: B9 4E 18   LDA $184e,y   
    $11F0: 85 F8      STA $f8       
    $11F2: B9 5E 18   LDA $185e,y   
    $11F5: 85 F9      STA $f9       
    $11F7: AC 16 10   LDY $1016     
L_11FA:
    $11FA: B1 F8      LDA ($f8),y   
    $11FC: 10 1E      BPL $121c        ; → L_121C
    $11FE: C9 FD      CMP #$fd      
    $1200: D0 0D      BNE $120f        ; → L_120F
    $1202: C8         INY           
    $1203: B1 F8      LDA ($f8),y   
    $1205: 8D 49 10   STA $1049     
    $1208: C8         INY           
    $1209: 8C 16 10   STY $1016     
    $120C: 4C FA 11   JMP $11fa        ; → L_11FA
L_120F:
    $120F: C8         INY           
    $1210: B1 F8      LDA ($f8),y   
    $1212: 8D 4C 10   STA $104c     
    $1215: C8         INY           
    $1216: 8C 16 10   STY $1016     
    $1219: 4C FA 11   JMP $11fa        ; → L_11FA
L_121C:
    $121C: 8D 1F 10   STA $101f     
    $121F: A9 08      LDA #$08      
    $1221: 8D 04 D4   STA $d404      ;V1_CTRL
    $1224: A9 0F      LDA #$0f      
    $1226: 8D 06 D4   STA $d406      ;V1_SR
    $1229: 8D 19 10   STA $1019     
    $122C: EE 16 10   INC $1016     
    $122F: 60         RTS           
sub_1230:
    $1230: AD 19 10   LDA $1019     
    $1233: F0 5A      BEQ $128f        ; → L_128F
    $1235: A9 00      LDA #$00      
    $1237: 8D 19 10   STA $1019     
    $123A: 8D 44 10   STA $1044     
    $123D: 85 FE      STA $fe       
    $123F: 85 FF      STA $ff       
    $1241: A9 28      LDA #$28      
    $1243: 8D EB 12   STA $12eb     
    $1246: AD 49 10   LDA $1049     
    $1249: 8D 10 10   STA $1010     
    $124C: AC 4C 10   LDY $104c     
    $124F: B9 FD 15   LDA $15fd,y   
    $1252: 8D 05 D4   STA $d405      ;V1_AD
    $1255: B9 13 16   LDA $1613,y   
    $1258: 8D 06 D4   STA $d406      ;V1_SR
    $125B: B9 29 16   LDA $1629,y   
    $125E: 8D 41 10   STA $1041     
    $1261: B9 3F 16   LDA $163f,y   
    $1264: 8D 45 10   STA $1045     
    $1267: BE 55 16   LDX $1655,y   
    $126A: BD C3 16   LDA $16c3,x   
    $126D: 8D 04 D4   STA $d404      ;V1_CTRL
    $1270: B9 6B 16   LDA $166b,y   
    $1273: 8D 43 10   STA $1043     
    $1276: F0 03      BEQ $127b        ; → L_127B
    $1278: EE 43 10   INC $1043     
L_127B:
    $127B: AC 16 10   LDY $1016     
    $127E: B1 F8      LDA ($f8),y   
    $1280: C9 FF      CMP #$ff      
    $1282: D0 08      BNE $128c        ; → L_128C
    $1284: EE 13 10   INC $1013     
    $1287: A9 00      LDA #$00      
    $1289: 8D 16 10   STA $1016     
L_128C:
    $128C: 4C C8 12   JMP $12c8        ; → L_12C8
L_128F:
    $128F: AD 41 10   LDA $1041     
    $1292: 18         CLC           
    $1293: 6D 45 10   ADC $1045     
    $1296: 8D 41 10   STA $1041     
    $1299: 30 07      BMI $12a2        ; → L_12A2
    $129B: AA         TAX           
    $129C: 29 1F      AND #$1f      
    $129E: A8         TAY           
    $129F: 4C A8 12   JMP $12a8        ; → L_12A8
L_12A2:
    $12A2: AA         TAX           
    $12A3: 29 1F      AND #$1f      
    $12A5: 09 20      ORA #$20      
    $12A7: A8         TAY           
L_12A8:
    $12A8: B9 FD 13   LDA $13fd,y   
    $12AB: 8D 02 D4   STA $d402      ;V1_PW_LO
    $12AE: BD 3D 14   LDA $143d,x   
    $12B1: 8D 03 D4   STA $d403      ;V1_PW_HI
    $12B4: AE 1C 10   LDX $101c     
    $12B7: BD C3 16   LDA $16c3,x   
    $12BA: C9 FF      CMP #$ff      
    $12BC: D0 07      BNE $12c5        ; → L_12C5
    $12BE: BD 57 17   LDA $1757,x   
    $12C1: AA         TAX           
    $12C2: BD C3 16   LDA $16c3,x   
L_12C5:
    $12C5: 8D 04 D4   STA $d404      ;V1_CTRL
L_12C8:
    $12C8: BD 57 17   LDA $1757,x   
    $12CB: 18         CLC           
    $12CC: 6D 1F 10   ADC $101f     
    $12CF: E8         INX           
    $12D0: 8E 1C 10   STX $101c     
    $12D3: AA         TAX           
    $12D4: BD 3D 15   LDA $153d,x   
    $12D7: 18         CLC           
    $12D8: 65 FE      ADC $fe       
    $12DA: 8D 00 D4   STA $d400      ;V1_FREQ_LO
    $12DD: BD 9D 15   LDA $159d,x   
    $12E0: 65 FF      ADC $ff       
    $12E2: 8D 01 D4   STA $d401      ;V1_FREQ_HI
    $12E5: AD 43 10   LDA $1043     
    $12E8: C9 01      CMP #$01      
    $12EA: F0 28      BEQ $1314        ; → L_1314
    $12EC: C9 00      CMP #$00      
    $12EE: F0 23      BEQ $1313        ; → L_1313
    $12F0: CE 43 10   DEC $1043     
    $12F3: 60         RTS           
; ----- data gap $12F4-$1312 (31 bytes) -----

L_1313:
    $1313: 60         RTS           
L_1314:
    $1314: AD 1F 10   LDA $101f     
    $1317: 18         CLC           
    $1318: 69 0C      ADC #$0c      
    $131A: AA         TAX           
    $131B: A5 FE      LDA $fe       
    $131D: 18         CLC           
    $131E: 7D 9D 15   ADC $159d,x   
    $1321: 85 FE      STA $fe       
    $1323: A5 FF      LDA $ff       
    $1325: 69 00      ADC #$00      
    $1327: 85 FF      STA $ff       
    $1329: EE 44 10   INC $1044     
    $132C: AD 44 10   LDA $1044     
    $132F: C9 03      CMP #$03      
    $1331: D0 05      BNE $1338        ; → L_1338
    $1333: A9 08      LDA #$08      
    $1335: 8D EB 12   STA $12eb     
L_1338:
    $1338: 60         RTS           
sub_1339:
    $1339: AD 1A 10   LDA $101a     
    $133C: D0 6A      BNE $13a8        ; → L_13A8
    $133E: AD 47 10   LDA $1047     
    $1341: F0 13      BEQ $1356        ; → L_1356
    $1343: AC 4D 10   LDY $104d     
    $1346: AD 48 10   LDA $1048     
    $1349: 18         CLC           
    $134A: 79 AD 16   ADC $16ad,y   
    $134D: 8D 48 10   STA $1048     
    $1350: 8D 16 D4   STA $d416      ;FC_HI
    $1353: CE 47 10   DEC $1047     
L_1356:
    $1356: AD 42 10   LDA $1042     
    $1359: 18         CLC           
    $135A: 6D 46 10   ADC $1046     
    $135D: 8D 42 10   STA $1042     
    $1360: 30 07      BMI $1369        ; → L_1369
    $1362: AA         TAX           
    $1363: 29 1F      AND #$1f      
    $1365: A8         TAY           
    $1366: 4C 6F 13   JMP $136f        ; → L_136F
L_1369:
    $1369: AA         TAX           
    $136A: 29 1F      AND #$1f      
    $136C: 09 20      ORA #$20      
    $136E: A8         TAY           
L_136F:
    $136F: B9 FD 13   LDA $13fd,y   
    $1372: 8D 09 D4   STA $d409      ;V2_PW_LO
    $1375: BD 3D 14   LDA $143d,x   
    $1378: 8D 0A D4   STA $d40a      ;V2_PW_HI
    $137B: AE 1D 10   LDX $101d     
    $137E: BD C3 16   LDA $16c3,x   
    $1381: C9 FF      CMP #$ff      
    $1383: D0 07      BNE $138c        ; → L_138C
    $1385: BD 57 17   LDA $1757,x   
    $1388: AA         TAX           
    $1389: BD C3 16   LDA $16c3,x   
L_138C:
    $138C: 8D 0B D4   STA $d40b      ;V2_CTRL
    $138F: BD 57 17   LDA $1757,x   
    $1392: 18         CLC           
    $1393: 6D 40 10   ADC $1040     
    $1396: E8         INX           
    $1397: 8E 1D 10   STX $101d     
    $139A: AA         TAX           
    $139B: BD 3D 15   LDA $153d,x   
    $139E: 8D 07 D4   STA $d407      ;V2_FREQ_LO
    $13A1: BD 9D 15   LDA $159d,x   
    $13A4: 8D 08 D4   STA $d408      ;V2_FREQ_HI
    $13A7: 60         RTS           
L_13A8:
    $13A8: AC 4D 10   LDY $104d     
    $13AB: A9 00      LDA #$00      
    $13AD: 8D 1A 10   STA $101a     
    $13B0: AD 4A 10   LDA $104a     
    $13B3: 8D 11 10   STA $1011     
    $13B6: B9 FD 15   LDA $15fd,y   
    $13B9: 8D 0C D4   STA $d40c      ;V2_AD
    $13BC: B9 13 16   LDA $1613,y   
    $13BF: 8D 0D D4   STA $d40d      ;V2_SR
    $13C2: B9 29 16   LDA $1629,y   
    $13C5: 8D 42 10   STA $1042     
    $13C8: B9 3F 16   LDA $163f,y   
    $13CB: 8D 46 10   STA $1046     
    $13CE: B9 55 16   LDA $1655,y   
    $13D1: 8D 1D 10   STA $101d     
    $13D4: A9 81      LDA #$81      
    $13D6: 8D 0B D4   STA $d40b      ;V2_CTRL
    $13D9: 8D 08 D4   STA $d408      ;V2_FREQ_HI
    $13DC: B9 81 16   LDA $1681,y   
    $13DF: 8D 48 10   STA $1048     
    $13E2: 8D 16 D4   STA $d416      ;FC_HI
    $13E5: B9 97 16   LDA $1697,y   
    $13E8: 8D 47 10   STA $1047     
    $13EB: AC 17 10   LDY $1017     
    $13EE: B1 FA      LDA ($fa),y   
    $13F0: C9 FF      CMP #$ff      
    $13F2: D0 08      BNE $13fc        ; → L_13FC
    $13F4: EE 14 10   INC $1014     
    $13F7: A9 00      LDA #$00      
    $13F9: 8D 17 10   STA $1017     
L_13FC:
    $13FC: 60         RTS           
; ----- data gap $13FD-$1BA0 (1956 bytes) -----

