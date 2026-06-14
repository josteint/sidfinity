; ============================================================================
; DMC V5 PLAYER — annotated disassembly
; Representative: DEMOS/G-L/Katusha.sid (family-3, the dominant V5 player;
;   1461 SIDs + family-5 sibling 34 = 1495 share this player. Family-4
;   (Jupiter41, 686) is a DISTINCT branch: same init offset +$40 but play
;   at +$95 not +$A1, ~0.31 Jaccard — RE separately.)
; Engine: DMC (Demo Music Creator) V5 line by The Syndrom/Crest+TIA (1993-94).
;   Distinct engine from V4 (Jaccard 0.136). Shares the DMC architecture
;   (duration-based, 3 voices, track->sector->note dispatch, $FF terminator,
;   speed counter) but a different data model. See pipelines/dmc/v5/SCOPE.md
;   + pipelines/dmc/docs/dmc_v5_format_notes.md.
; ============================================================================
;
; Binary: hvsc84/DEMOS/G-L/Katusha.sid   Load/Init $1000  Play $1003
;   $1000 JMP $1040 (init)   $1003 JMP $10A1 (play)   2-entry jump table.
;   Player code $1040-$170E (~713 instrs); data tables $170F-$19C8.
;
; ---------------------------------------------------------------------------
; MEMORY MAP — work RAM (per-voice arrays indexed by X = voice 0..2)
; ---------------------------------------------------------------------------
;   $1006,x  voice active flag (1=playing; $FE track cmd clears it)
;   $1009,x  voice SID offset (CONSTANT 0/7/14 -> $D400/$D407/$D40E); the
;            extract reads it as Y for every per-voice $D4xx store
;   $1012    speed (tempo reload); $1013 speed counter (tick when ==$1012)
;   $1015    filter mode nibble (FLT cmd hi) -> OR'd into $D418
;   $1016/$1017  filter cutoff hi/lo -> $D416/$D415 (once per play; V3 only)
;   $1018    fade-IN speed (FD+ cmd; 0=off);  $1019 fade-OUT speed (FD-)
;   $101A    vibrato width (instr byte7 & $07) — freq<<width = vib step
;   $101B    master volume (current; faded);  $101C fade fractional accum
;   $101E/$101F  scratch (table add lo/hi during pulse/filter run)
;   $1802,x/$1805,x  vib step lo/hi (= base-note freq << width)
;   $1808,x  (note counter, cleared at note-on)
;   $180B,x  NOTE-JUST-STARTED flag ($09 at note-on; triggers note-init-2)
;   $180E,x/$1811,x  current wave-step freq lo/hi (base note + arp/drum)
;   $1814,x  current wave ctrl byte (-> $D404 after AND gate mask)
;   $1817,x  gate mask ANDed onto wave ctrl ($F7=clear test/gate prep,
;            $F6=hard-restart, $FF=pass) before the $D404 write
;   $181D,x  LOOKAHEAD = next sector byte (gate logic peeks it)
;   $1820,x/$1823,x  pulse accumulator lo/hi -> $D402/$D403 (PW)
;   $1826,x/$1829,x  pulse frame counter (16-bit)
;   $182C,x  pulse double-flag;  $182F,x pulse direction;  $1832,x pulse step ctr
;   $1835,x/$1838,x  freq-offset accumulator lo/hi (vibrato + glide/slide)
;   $183B/$183C  filter-table frame counter (voice-3 only)
;   $183D/$183E  scratch (glide arrival freq compare)
;   $183F    filter-active flag (instr FL ptr != 0);  $1840 scratch
;   $1841    pulse-active flag (instr PU ptr != 0);  $1842 init play-skip
;   $1843    FRQ override (base filter freq hi, FRQ cmd; 0=use filter table)
;   $17CF,x/$17D2,x  track pointer lo/hi (orderlist);  $17D5,x track position
;   $17D8,x  sector position (byte index within current sector)
;   $17DB,x  duration counter (ticks; reload from $17DE,x);  $17DE,x dur reload
;   $17E1,x  current instrument (SND);  $17E4,x transpose (signed, TR+/TR-)
;   $17E7,x  VOL override (sustain; 0=instrument's own SR)
;   $17EA,x  gate-off flag (GATE cmd; note plays w/o retrigger)
;   $17ED,x  glide/slide speed (0=off);  $17F0,x glide/slide target note
;   $17F3,x  wave-table position;  $17F6,x pulse-table position
;   $17F9    filter-table position (GLOBAL — V3 only)
;   $17FC,x  vibrato delay counter;  $17FF,x vibrato speed (period)
;   ZP $F8/$F9  general 16-bit pointer (track ptr / sector ptr / table base)
;
; ---------------------------------------------------------------------------
; DATA TABLES (packer-placed; absolute addresses, here Katusha's layout)
; ---------------------------------------------------------------------------
;   $170F  freq table LO (96 notes)        $176F  freq table HI (96 notes)
;   $1878  track-pointer record: 3x(lo,hi) orderlist ptrs, then speed, $101B
;   $196E  sector pointer table LO         $1972  sector pointer table HI
;   $1976  INSTRUMENT table (8 bytes each, ids $00-$1F)
;   $199E  wave-table CTRL array           $19AB  wave-table FREQ/offset array
;   $19B8  pulse-table ADD-LO / arg array  $19BF  pulse-table ADD-HI / arg array
;   $19C6  filter-table arg-LO array       $19C7  filter-table arg-HI array
;   (the 2-byte tables are addressed by ENTRY index; one entry per frame.)
;
; ---------------------------------------------------------------------------
; INSTRUMENT RECORD (8 bytes @ $1976 + 8*id) — confirmed from runtime
; ---------------------------------------------------------------------------
;   +0 AD   -> $D405 at note-on
;   +1 SR   -> $D406 at note-on (VOL override / ADR-SRR cmds can replace)
;   +2 WV   wave-table start position ($17F3,x)
;   +3 PU   pulse-table start position ($17F6,x); 0 = no pulse restart
;   +4 FL   filter-table start position ($17F9); 0 = no filter restart
;   +5 vib delay   ($17FC,x)
;   +6 vib speed   ($17FF,x = triangle half-period)
;   +7 vib width   (&$07 -> $101A; vib step = base-note freq << width)
;
; ---------------------------------------------------------------------------
; WAVE / PULSE / FILTER tables — 2-byte entries, $90 = loop
; ---------------------------------------------------------------------------
;   WAVE  ($199E ctrl, $19AB freq): ctrl byte -> $D404 (AND gate mask).
;     bit3 ($08) test bit = DRUM/hi-freq mode: the FREQ byte goes straight
;     to freq-hi ($D401), freq-lo=0. Else MELODIC: FREQ byte = signed
;     semitone arp offset added to the note -> freq-table lookup.
;     ctrl == $90 -> loop: next FREQ byte = absolute entry to jump to.
;   PULSE ($19B8/$19BF): start pair, then (16-bit ADD, frame-count) pairs;
;     two's-complement add to subtract. $90 = loop. PU=0 -> no restart.
;   FILTER ($19C6/$19C7): like pulse, all 16 bits, VOICE 3 ONLY. FL=0 -> none.
;     FRQ cmd ($1843) overrides the cutoff hi directly.
;
; ---------------------------------------------------------------------------
; TRACK (orderlist) byte map  — read at track_fetch ($10F2)
; ---------------------------------------------------------------------------
;   $00-$7F  sector number (-> sector ptr table)
;   $FC nn   transpose NEGATIVE (two's complement of nn) -> $17E4,x
;   $FD nn   transpose POSITIVE (nn) -> $17E4,x
;   $FE      voice end (clear $1006,x; voice freewheels its last state)
;   $FF pp   loop track to position pp
;
; ---------------------------------------------------------------------------
; SECTOR command byte map  — dispatched at sector_dispatch ($1158);
;   byte < $80 = NOTE (+transpose); byte >= $80 = command. (THE key RE result)
; ---------------------------------------------------------------------------
;   $00-$7F  NOTE (+ $17E4 transpose -> $100F,x); plays for the current DUR
;   $F1 nn   SRR — set SR register live ($D406,y = nn)
;   $F2 nn   ADR — set AD register live ($D405,y = nn)
;   $F3 nn   VOL — set sustain override ($17E7,x = nn; 0 = instrument's own)
;   $F4      gate variant — toggle $1817,x bit0 (tie/hard-restart flag), step
;   $F5      gate variant — toggle $17EA,x ($FF) (gate-off-without-retrigger)
;   $F6 nn   FD- (fade out) — set fade-out speed $1019 = nn
;   $F7 nn   FD+ (fade in)  — set fade-in speed  $1018 = nn
;   $F8 nn   FRQ — base filter freq hi override $1843 = nn
;   $F9 nn   FLT — filter type|res: nn=0 clears $D417; else (nn<<4)|$04 ->
;            $D417 (RES_FILT) and (nn&$F0) -> $1015 (filter mode for $D418)
;   $FA s,note  SLD — slide playing note to `note` at speed s (1 note follows)
;   $FB s,a,b   GLD — glide from note a to note b at speed s (2 notes follow)
;   $FC nn   SND — set instrument $17E1,x = nn
;   $FD nn   DUR — set duration reload $17DE,x = nn
;   $FE      GATE — gate-off step (release; counts as a full duration step)
;   $FF      END of sector (peeked as lookahead $181D,x; advances track pos)
;
; ---------------------------------------------------------------------------
; PLAY FLOW + per-voice SID write order
; ---------------------------------------------------------------------------
;   play ($10A1): skip first $1842 plays; DEC speed ctr (reload on wrap);
;     voice_tick x3; then GLOBAL $D415<-$1017, $D416<-$1016 (filter cutoff).
;   voice_tick ($10DD): on a tick with dur ctr hitting 0 -> fetch next sector
;     event; else -> run_effects ($1332).
;   run_effects: note-just-started ($180B) -> note_init2 (load instrument,
;     init wave/pulse/filter tables, $D418 vol, AD/SR) ; else steady:
;     pulse_run / filter_run(V3) / glide / vibrato / fade ($D418) / wave_step.
;   per-voice WRITE ORDER (sid_write $16E6, Y=$1009,x):
;     $D400 freq lo (= $180E + $1835 accum)
;     $D401 freq hi (= $1811 + $1838 accum)
;     $D402 PW lo   (= $1820)      $D403 PW hi (= $1823)
;     $D404 ctrl    (= $1814 wave ctrl AND $1817 gate mask)
;   plus: $D405/$D406 (AD/SR) at note-on + ADR/SRR cmds; $D417 at FLT cmd;
;   $D415/$D416 once per play (filter cutoff); $D418 in fade (master vol|mode).
;   Hard restart: at sector lookahead, dur ctr==1 -> SR=0; dur ctr==2 on a
;   tick -> gate mask $F6 (TEST+gate clear) the next frame (gate_logic $169B).
;
; ============================================================================
; (Code body below is the auto-traced seed; addresses + SID-reg tags exact.
;  Routine labels per the flow above.)
; ============================================================================

; ======= init: =======
init:
    $1000: 4C 40 10   JMP $1040        ; → L_1040
; ======= play: =======
play:
    $1003: 4C A1 10   JMP $10a1        ; → L_10A1
; ----- data gap $1006-$103F (58 bytes) -----

L_1040:

; ----- init_clear: copy 3 orderlist ptrs from $1878 -> $17CF/$17D2; speed $1012; clear state $17D5+; voices active+dur=1; clear $D400-$D417; $D404/0B/12=$08; $1842=2 (skip 2 plays)
    $1040: A9 00      LDA #$00      
    $1042: 0A         ASL a         
    $1043: A8         TAY           
    $1044: A2 00      LDX #$00      
L_1046:
    $1046: B9 78 18   LDA $1878,y   
    $1049: 9D CF 17   STA $17cf,x   
    $104C: B9 79 18   LDA $1879,y   
    $104F: 9D D2 17   STA $17d2,x   
    $1052: C8         INY           
    $1053: C8         INY           
    $1054: E8         INX           
    $1055: E0 03      CPX #$03      
    $1057: D0 ED      BNE $1046        ; → L_1046
    $1059: B9 78 18   LDA $1878,y   
    $105C: 8D 12 10   STA $1012     
    $105F: B9 79 18   LDA $1879,y   
    $1062: 8D 1B 10   STA $101b     
    $1065: A2 00      LDX #$00      
    $1067: 8A         TXA           
L_1068:
    $1068: 9D D5 17   STA $17d5,x   
    $106B: E8         INX           
    $106C: E0 71      CPX #$71      
    $106E: D0 F8      BNE $1068        ; → L_1068
    $1070: 8D 18 10   STA $1018     
    $1073: 8D 19 10   STA $1019     
    $1076: A2 00      LDX #$00      
    $1078: A9 01      LDA #$01      
L_107A:
    $107A: 9D DB 17   STA $17db,x   
    $107D: 9D 06 10   STA $1006,x   
    $1080: E8         INX           
    $1081: E0 03      CPX #$03      
    $1083: D0 F5      BNE $107a        ; → L_107A
    $1085: A2 00      LDX #$00      
    $1087: 8A         TXA           
L_1088:
    $1088: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $108B: E8         INX           
    $108C: E0 18      CPX #$18      
    $108E: D0 F8      BNE $1088        ; → L_1088
    $1090: A9 08      LDA #$08      
    $1092: 8D 04 D4   STA $d404      ;V1_CTRL
    $1095: 8D 0B D4   STA $d40b      ;V2_CTRL
    $1098: 8D 12 D4   STA $d412      ;V3_CTRL
    $109B: A9 02      LDA #$02      
    $109D: 8D 42 18   STA $1842     
    $10A0: 60         RTS           
L_10A1:

; ----- play: per-frame: skip first $1842 plays; DEC speed ctr (reload); voice_tick x3; then $D415<-$1017 / $D416<-$1016 (filter cutoff)
    $10A1: A5 F8      LDA $f8       
    $10A3: 48         PHA           
    $10A4: A5 F9      LDA $f9       
    $10A6: 48         PHA           
    $10A7: A2 00      LDX #$00      
    $10A9: AD 42 18   LDA $1842     
    $10AC: F0 06      BEQ $10b4        ; → L_10B4
    $10AE: CE 42 18   DEC $1842     
    $10B1: 4C D6 10   JMP $10d6        ; → L_10D6
L_10B4:
    $10B4: CE 13 10   DEC $1013     
    $10B7: 10 06      BPL $10bf        ; → L_10BF
    $10B9: AD 12 10   LDA $1012     
    $10BC: 8D 13 10   STA $1013     
L_10BF:
    $10BF: 20 DD 10   JSR $10dd        ; → sub_10DD
    $10C2: E8         INX           
    $10C3: 20 DD 10   JSR $10dd        ; → sub_10DD
    $10C6: E8         INX           
    $10C7: 20 DD 10   JSR $10dd        ; → sub_10DD
    $10CA: AD 17 10   LDA $1017     
    $10CD: 8D 15 D4   STA $d415      ;FC_LO
    $10D0: AD 16 10   LDA $1016     
    $10D3: 8D 16 D4   STA $d416      ;FC_HI
L_10D6:
    $10D6: 68         PLA           
    $10D7: 85 F9      STA $f9       
    $10D9: 68         PLA           
    $10DA: 85 F8      STA $f8       
    $10DC: 60         RTS           
sub_10DD:

; ----- voice_tick: tick (speed ctr==reload) AND active AND dur ctr hits 0 -> track_fetch; else -> run_effects
    $10DD: AD 12 10   LDA $1012     
    $10E0: CD 13 10   CMP $1013     
    $10E3: D0 0A      BNE $10ef        ; → L_10EF
    $10E5: BD 06 10   LDA $1006,x   
    $10E8: F0 05      BEQ $10ef        ; → L_10EF
    $10EA: DE DB 17   DEC $17db,x   
    $10ED: F0 03      BEQ $10f2        ; → L_10F2
L_10EF:
    $10EF: 4C 32 13   JMP $1332        ; → L_1332
L_10F2:

; ----- track_fetch: read orderlist byte: <$80 sector#; $FF loop; $FE voice-end; $FD/$FC transpose +/-
    $10F2: BD CF 17   LDA $17cf,x   
    $10F5: 85 F8      STA $f8       
    $10F7: BD D2 17   LDA $17d2,x   
    $10FA: 85 F9      STA $f9       
    $10FC: BC D5 17   LDY $17d5,x   
    $10FF: B1 F8      LDA ($f8),y   
    $1101: 10 4A      BPL $114d        ; → L_114D
    $1103: C9 FF      CMP #$ff      
    $1105: D0 0C      BNE $1113        ; → L_1113
    $1107: C8         INY           
    $1108: B1 F8      LDA ($f8),y   
    $110A: 9D D5 17   STA $17d5,x   
    $110D: A8         TAY           
    $110E: B1 F8      LDA ($f8),y   
    $1110: 4C 1F 11   JMP $111f        ; → L_111F
L_1113:
    $1113: C9 FE      CMP #$fe      
    $1115: D0 08      BNE $111f        ; → L_111F
    $1117: A9 00      LDA #$00      
    $1119: 9D 06 10   STA $1006,x   
    $111C: 4C 5B 16   JMP $165b        ; → L_165B
L_111F:
    $111F: C9 FD      CMP #$fd      
    $1121: D0 12      BNE $1135        ; → L_1135
    $1123: C8         INY           
    $1124: FE D5 17   INC $17d5,x   
    $1127: FE D5 17   INC $17d5,x   
    $112A: B1 F8      LDA ($f8),y   
    $112C: 9D E4 17   STA $17e4,x   
    $112F: C8         INY           
    $1130: B1 F8      LDA ($f8),y   
    $1132: 4C 4D 11   JMP $114d        ; → L_114D
L_1135:
    $1135: C9 FC      CMP #$fc      
    $1137: D0 14      BNE $114d        ; → L_114D
    $1139: C8         INY           
    $113A: FE D5 17   INC $17d5,x   
    $113D: FE D5 17   INC $17d5,x   
    $1140: B1 F8      LDA ($f8),y   
    $1142: 49 FF      EOR #$ff      
    $1144: 18         CLC           
    $1145: 69 01      ADC #$01      
    $1147: 9D E4 17   STA $17e4,x   
    $114A: C8         INY           
    $114B: B1 F8      LDA ($f8),y   
L_114D:

; ----- sector_ptr: sector# -> ptr from $196E/$1972 -> $F8/$F9
    $114D: A8         TAY           
    $114E: B9 6E 19   LDA $196e,y   
    $1151: 85 F8      STA $f8       
    $1153: B9 72 19   LDA $1972,y   
    $1156: 85 F9      STA $f9       
L_1158:

; ----- sector_dispatch: read sector byte @ $17D8,x: <$80 -> note_play; >=$80 -> command
    $1158: BC D8 17   LDY $17d8,x   
    $115B: B1 F8      LDA ($f8),y   
    $115D: 30 03      BMI $1162        ; → L_1162
    $115F: 4C B5 12   JMP $12b5        ; → L_12B5
L_1162:

; ----- cmd_FD_DUR: $FD nn: duration reload $17DE,x = nn
    $1162: C9 FD      CMP #$fd      
    $1164: D0 0F      BNE $1175        ; → L_1175
    $1166: C8         INY           
    $1167: B1 F8      LDA ($f8),y   
    $1169: 9D DE 17   STA $17de,x   
    $116C: FE D8 17   INC $17d8,x   
    $116F: FE D8 17   INC $17d8,x   
    $1172: 4C 58 11   JMP $1158        ; → L_1158
L_1175:

; ----- cmd_FC_SND: $FC nn: instrument $17E1,x = nn
    $1175: C9 FC      CMP #$fc      
    $1177: D0 0F      BNE $1188        ; → L_1188
    $1179: C8         INY           
    $117A: B1 F8      LDA ($f8),y   
    $117C: 9D E1 17   STA $17e1,x   
    $117F: FE D8 17   INC $17d8,x   
    $1182: FE D8 17   INC $17d8,x   
    $1185: 4C 58 11   JMP $1158        ; → L_1158
L_1188:

; ----- cmd_FE_GATE: $FE: gate-off step (commit step via step_commit)
    $1188: C9 FE      CMP #$fe      
    $118A: D0 24      BNE $11b0        ; → L_11B0
L_118C:

; ----- step_commit: reload dur $17DB<-$17DE; advance; lookahead $181D,x; $FF -> sector end
    $118C: BD DE 17   LDA $17de,x   
    $118F: 9D DB 17   STA $17db,x   
    $1192: FE D8 17   INC $17d8,x   
    $1195: C8         INY           
    $1196: B1 F8      LDA ($f8),y   
    $1198: 9D 1D 18   STA $181d,x   
    $119B: C9 FF      CMP #$ff      
    $119D: D0 0E      BNE $11ad        ; → L_11AD
    $119F: A9 00      LDA #$00      
    $11A1: 9D D8 17   STA $17d8,x   
    $11A4: 9D E7 17   STA $17e7,x   
    $11A7: 9D EA 17   STA $17ea,x   
    $11AA: FE D5 17   INC $17d5,x   
L_11AD:
    $11AD: 4C 5B 16   JMP $165b        ; → L_165B
L_11B0:

; ----- cmd_F4: $F4: toggle $1817,x bit0 (tie/hard-restart flag) + commit step
    $11B0: C9 F4      CMP #$f4      
    $11B2: D0 0B      BNE $11bf        ; → L_11BF
    $11B4: BD 17 18   LDA $1817,x   
    $11B7: 49 01      EOR #$01      
    $11B9: 9D 17 18   STA $1817,x   
    $11BC: 4C 8C 11   JMP $118c        ; → L_118C
L_11BF:

; ----- cmd_F5: $F5: toggle $17EA,x ($FF) gate-off flag
    $11BF: C9 F5      CMP #$f5      
    $11C1: D0 0E      BNE $11d1        ; → L_11D1
    $11C3: BD EA 17   LDA $17ea,x   
    $11C6: 49 FF      EOR #$ff      
    $11C8: 9D EA 17   STA $17ea,x   
    $11CB: FE D8 17   INC $17d8,x   
    $11CE: 4C 58 11   JMP $1158        ; → L_1158
L_11D1:

; ----- cmd_F3_VOL: $F3 nn: sustain override $17E7,x = nn
    $11D1: C9 F3      CMP #$f3      
    $11D3: D0 0F      BNE $11e4        ; → L_11E4
    $11D5: C8         INY           
    $11D6: B1 F8      LDA ($f8),y   
    $11D8: 9D E7 17   STA $17e7,x   
    $11DB: FE D8 17   INC $17d8,x   
    $11DE: FE D8 17   INC $17d8,x   
    $11E1: 4C 58 11   JMP $1158        ; → L_1158
L_11E4:

; ----- cmd_FB_GLD: $FB s,a,b: glide speed $17ED, start a -> $100F, target b -> $17F0 (+transpose) -> note_on
    $11E4: C9 FB      CMP #$fb      
    $11E6: D0 26      BNE $120e        ; → L_120E
    $11E8: C8         INY           
    $11E9: B1 F8      LDA ($f8),y   
    $11EB: 9D ED 17   STA $17ed,x   
    $11EE: C8         INY           
    $11EF: B1 F8      LDA ($f8),y   
    $11F1: 18         CLC           
    $11F2: 7D E4 17   ADC $17e4,x   
    $11F5: 9D 0F 10   STA $100f,x   
    $11F8: C8         INY           
    $11F9: B1 F8      LDA ($f8),y   
    $11FB: 18         CLC           
    $11FC: 7D E4 17   ADC $17e4,x   
    $11FF: 9D F0 17   STA $17f0,x   
    $1202: BD D8 17   LDA $17d8,x   
    $1205: 18         CLC           
    $1206: 69 03      ADC #$03      
    $1208: 9D D8 17   STA $17d8,x   
    $120B: 4C C4 12   JMP $12c4        ; → L_12C4
L_120E:

; ----- cmd_FA_SLD: $FA s,note: slide speed $17ED, target -> $17F0 (+transpose), commit step
    $120E: C9 FA      CMP #$fa      
    $1210: D0 1C      BNE $122e        ; → L_122E
    $1212: C8         INY           
    $1213: B1 F8      LDA ($f8),y   
    $1215: 9D ED 17   STA $17ed,x   
    $1218: C8         INY           
    $1219: B1 F8      LDA ($f8),y   
    $121B: 18         CLC           
    $121C: 7D E4 17   ADC $17e4,x   
    $121F: 9D F0 17   STA $17f0,x   
    $1222: BD D8 17   LDA $17d8,x   
    $1225: 18         CLC           
    $1226: 69 02      ADC #$02      
    $1228: 9D D8 17   STA $17d8,x   
    $122B: 4C 8C 11   JMP $118c        ; → L_118C
L_122E:

; ----- cmd_F9_FLT: $F9 nn: nn=0 -> $D417=0; else (nn<<4)|$04 -> $D417, (nn&$F0) -> $1015 filter mode
    $122E: C9 F9      CMP #$f9      
    $1230: D0 1E      BNE $1250        ; → L_1250
    $1232: C8         INY           
    $1233: B1 F8      LDA ($f8),y   
    $1235: 48         PHA           
    $1236: F0 06      BEQ $123e        ; → L_123E
    $1238: 0A         ASL a         
    $1239: 0A         ASL a         
    $123A: 0A         ASL a         
    $123B: 0A         ASL a         
    $123C: 09 04      ORA #$04      
L_123E:
    $123E: 8D 17 D4   STA $d417      ;RES_FILT
    $1241: 68         PLA           
    $1242: 29 F0      AND #$f0      
    $1244: 8D 15 10   STA $1015     
    $1247: FE D8 17   INC $17d8,x   
    $124A: FE D8 17   INC $17d8,x   
    $124D: 4C 58 11   JMP $1158        ; → L_1158
L_1250:

; ----- cmd_F8_FRQ: $F8 nn: base filter freq hi override $1843 = nn
    $1250: C9 F8      CMP #$f8      
    $1252: D0 0F      BNE $1263        ; → L_1263
    $1254: C8         INY           
    $1255: B1 F8      LDA ($f8),y   
    $1257: 8D 43 18   STA $1843     
    $125A: FE D8 17   INC $17d8,x   
    $125D: FE D8 17   INC $17d8,x   
    $1260: 4C 58 11   JMP $1158        ; → L_1158
L_1263:

; ----- cmd_F2_ADR: $F2 nn: live AD -> $D405,y
    $1263: C9 F2      CMP #$f2      
    $1265: D0 12      BNE $1279        ; → L_1279
    $1267: C8         INY           
    $1268: B1 F8      LDA ($f8),y   
    $126A: BC 09 10   LDY $1009,x   
    $126D: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $1270: FE D8 17   INC $17d8,x   
    $1273: FE D8 17   INC $17d8,x   
    $1276: 4C 58 11   JMP $1158        ; → L_1158
L_1279:

; ----- cmd_F1_SRR: $F1 nn: live SR -> $D406,y
    $1279: C9 F1      CMP #$f1      
    $127B: D0 12      BNE $128f        ; → L_128F
    $127D: C8         INY           
    $127E: B1 F8      LDA ($f8),y   
    $1280: BC 09 10   LDY $1009,x   
    $1283: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $1286: FE D8 17   INC $17d8,x   
L_1289:
    $1289: FE D8 17   INC $17d8,x   
    $128C: 4C 58 11   JMP $1158        ; → L_1158
L_128F:

; ----- cmd_F7_FDplus: $F7 nn: fade-in speed $1018 = nn
    $128F: C9 F7      CMP #$f7      
    $1291: D0 0F      BNE $12a2        ; → L_12A2
    $1293: C8         INY           
    $1294: B1 F8      LDA ($f8),y   
    $1296: 8D 18 10   STA $1018     
    $1299: FE D8 17   INC $17d8,x   
    $129C: FE D8 17   INC $17d8,x   
    $129F: 4C 58 11   JMP $1158        ; → L_1158
L_12A2:

; ----- cmd_F6_FDminus: $F6 nn: fade-out speed $1019 = nn
    $12A2: C9 F6      CMP #$f6      
    $12A4: D0 E3      BNE $1289        ; → L_1289
    $12A6: C8         INY           
    $12A7: B1 F8      LDA ($f8),y   
    $12A9: 8D 19 10   STA $1019     
    $12AC: FE D8 17   INC $17d8,x   
    $12AF: FE D8 17   INC $17d8,x   
    $12B2: 4C 58 11   JMP $1158        ; → L_1158
L_12B5:

; ----- note_play: note byte + transpose -> $100F,x; gate-off flag set -> commit step; else note_on
    $12B5: 18         CLC           
    $12B6: 7D E4 17   ADC $17e4,x   
    $12B9: 9D 0F 10   STA $100f,x   
    $12BC: BD EA 17   LDA $17ea,x   
    $12BF: F0 03      BEQ $12c4        ; → L_12C4
    $12C1: 4C 8C 11   JMP $118c        ; → L_118C
L_12C4:

; ----- note_on: instr*8 @ $1976: AD->$D405, SR(/VOL override)->$D406; reload dur; ctrl $09->$D404 ($180B=$09 note-start); freq=0; lookahead
    $12C4: BD E1 17   LDA $17e1,x   
    $12C7: 0A         ASL a         
    $12C8: 0A         ASL a         
    $12C9: 0A         ASL a         
    $12CA: A8         TAY           
    $12CB: B9 76 19   LDA $1976,y   
    $12CE: 48         PHA           
    $12CF: B9 77 19   LDA $1977,y   
    $12D2: 48         PHA           
    $12D3: BC 09 10   LDY $1009,x   
    $12D6: BD E7 17   LDA $17e7,x   
    $12D9: F0 13      BEQ $12ee        ; → L_12EE
    $12DB: 0A         ASL a         
    $12DC: 0A         ASL a         
    $12DD: 0A         ASL a         
    $12DE: 0A         ASL a         
    $12DF: 8D 40 18   STA $1840     
    $12E2: 68         PLA           
    $12E3: 29 0F      AND #$0f      
    $12E5: 0D 40 18   ORA $1840     
    $12E8: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $12EB: 4C F2 12   JMP $12f2        ; → L_12F2
L_12EE:
    $12EE: 68         PLA           
    $12EF: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_12F2:
    $12F2: 68         PLA           
    $12F3: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $12F6: BD DE 17   LDA $17de,x   
    $12F9: 9D DB 17   STA $17db,x   
    $12FC: A9 00      LDA #$00      
    $12FE: 9D 08 18   STA $1808,x   
    $1301: BC 09 10   LDY $1009,x   
    $1304: A9 09      LDA #$09      
    $1306: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $1309: 9D 0B 18   STA $180b,x   
    $130C: A9 00      LDA #$00      
    $130E: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1311: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1314: FE D8 17   INC $17d8,x   
    $1317: BC D8 17   LDY $17d8,x   
    $131A: B1 F8      LDA ($f8),y   
    $131C: 9D 1D 18   STA $181d,x   
    $131F: C9 FF      CMP #$ff      
    $1321: D0 0E      BNE $1331        ; → L_1331
    $1323: A9 00      LDA #$00      
    $1325: 9D D8 17   STA $17d8,x   
    $1328: 9D E7 17   STA $17e7,x   
    $132B: 9D EA 17   STA $17ea,x   
    $132E: FE D5 17   INC $17d5,x   
L_1331:
    $1331: 60         RTS           
L_1332:

; ----- run_effects: $180B note-start -> note_init2; else steady (pulse/filter/glide/vib/fade/wave)
    $1332: BD 0B 18   LDA $180b,x   
    $1335: D0 03      BNE $133a        ; → L_133A
    $1337: 4C 39 14   JMP $1439        ; → L_1439
L_133A:

; ----- note_init2: $D418=vol|filtmode; load instr WV/PU/FL ptrs+vib; init wave step; pulse_init; filter_init; vib step setup
    $133A: A9 00      LDA #$00      
    $133C: 9D 0B 18   STA $180b,x   
    $133F: AD 15 10   LDA $1015     
    $1342: 0D 1B 10   ORA $101b     
    $1345: 8D 18 D4   STA $d418      ;VOL
    $1348: BD E1 17   LDA $17e1,x   
    $134B: 0A         ASL a         
    $134C: 0A         ASL a         
    $134D: 0A         ASL a         
    $134E: A8         TAY           
    $134F: B9 7B 19   LDA $197b,y   
    $1352: 9D FC 17   STA $17fc,x   
    $1355: B9 7C 19   LDA $197c,y   
    $1358: 9D FF 17   STA $17ff,x   
    $135B: B9 7D 19   LDA $197d,y   
    $135E: 29 07      AND #$07      
    $1360: 8D 1A 10   STA $101a     
    $1363: B9 78 19   LDA $1978,y   
    $1366: 9D F3 17   STA $17f3,x   
    $1369: B9 79 19   LDA $1979,y   
    $136C: 8D 41 18   STA $1841     
    $136F: F0 03      BEQ $1374        ; → L_1374
    $1371: 9D F6 17   STA $17f6,x   
L_1374:
    $1374: B9 7A 19   LDA $197a,y   
    $1377: 8D 3F 18   STA $183f     
    $137A: F0 03      BEQ $137f        ; → L_137F
    $137C: 8D F9 17   STA $17f9     
L_137F:

; ----- wave_init: first wave entry: drum (test bit) freq-hi direct, or melodic freq-table lookup
    $137F: BC F3 17   LDY $17f3,x   
    $1382: FE F3 17   INC $17f3,x   
    $1385: B9 9E 19   LDA $199e,y   
    $1388: 9D 14 18   STA $1814,x   
    $138B: 29 08      AND #$08      
    $138D: F0 0E      BEQ $139d        ; → L_139D
    $138F: B9 AB 19   LDA $19ab,y   
    $1392: 9D 11 18   STA $1811,x   
    $1395: A9 00      LDA #$00      
    $1397: 9D 0E 18   STA $180e,x   
    $139A: 4C B1 13   JMP $13b1        ; → L_13B1
L_139D:
    $139D: B9 AB 19   LDA $19ab,y   
    $13A0: 18         CLC           
    $13A1: 7D 0F 10   ADC $100f,x   
    $13A4: A8         TAY           
    $13A5: B9 0F 17   LDA $170f,y   
    $13A8: 9D 0E 18   STA $180e,x   
    $13AB: B9 6F 17   LDA $176f,y   
    $13AE: 9D 11 18   STA $1811,x   
L_13B1:
    $13B1: A9 F7      LDA #$f7      
    $13B3: 9D 17 18   STA $1817,x   

; ----- pulse_init: if PU active: load pulse table start pair -> $1820/$1823, clear counters
    $13B6: AD 41 18   LDA $1841     
    $13B9: F0 1C      BEQ $13d7        ; → L_13D7
    $13BB: BC F6 17   LDY $17f6,x   
    $13BE: F0 17      BEQ $13d7        ; → L_13D7
    $13C0: B9 B8 19   LDA $19b8,y   
    $13C3: 9D 23 18   STA $1823,x   
    $13C6: B9 BF 19   LDA $19bf,y   
    $13C9: 9D 20 18   STA $1820,x   
    $13CC: A9 00      LDA #$00      
    $13CE: 9D 26 18   STA $1826,x   
    $13D1: 9D 29 18   STA $1829,x   
    $13D4: FE F6 17   INC $17f6,x   
L_13D7:

; ----- filter_init: if FL active (V3): load cutoff from filter table or FRQ override -> $1016/$1017
    $13D7: AD 3F 18   LDA $183f     
    $13DA: F0 2A      BEQ $1406        ; → L_1406
    $13DC: AC F9 17   LDY $17f9     
    $13DF: AD 43 18   LDA $1843     
    $13E2: F0 0B      BEQ $13ef        ; → L_13EF
    $13E4: 8D 16 10   STA $1016     
    $13E7: A9 00      LDA #$00      
    $13E9: 8D 17 10   STA $1017     
    $13EC: 4C FB 13   JMP $13fb        ; → L_13FB
L_13EF:
    $13EF: B9 C6 19   LDA $19c6,y   
    $13F2: 8D 16 10   STA $1016     
    $13F5: B9 C7 19   LDA $19c7,y   
    $13F8: 8D 17 10   STA $1017     
L_13FB:
    $13FB: A9 00      LDA #$00      
    $13FD: 8D 3B 18   STA $183b     
    $1400: 8D 3C 18   STA $183c     
    $1403: EE F9 17   INC $17f9     
L_1406:

; ----- vib_setup: clear accum/pulse state; vib step $1802/$1805 = base-note freq << width ($101A)
    $1406: A9 00      LDA #$00      
    $1408: 9D 05 18   STA $1805,x   
    $140B: 9D 2C 18   STA $182c,x   
    $140E: 9D 2F 18   STA $182f,x   
    $1411: 9D 32 18   STA $1832,x   
    $1414: 9D 35 18   STA $1835,x   
    $1417: 9D 38 18   STA $1838,x   
    $141A: BC 0F 10   LDY $100f,x   
    $141D: B9 6F 17   LDA $176f,y   
    $1420: 9D 02 18   STA $1802,x   
    $1423: AD 1A 10   LDA $101a     
    $1426: F0 0E      BEQ $1436        ; → L_1436
    $1428: A0 00      LDY #$00      
L_142A:
    $142A: 1E 02 18   ASL $1802,x   
    $142D: 3E 05 18   ROL $1805,x   
    $1430: C8         INY           
    $1431: CC 1A 10   CPY $101a     
    $1434: D0 F4      BNE $142a        ; → L_142A
L_1436:
    $1436: 4C 9B 16   JMP $169b        ; → L_169B
L_1439:

; ----- pulse_run: advance pulse accum $1820/$1823 by table ADD; frame counter; $90 loop
    $1439: BC F6 17   LDY $17f6,x   
    $143C: B9 B8 19   LDA $19b8,y   
    $143F: C9 90      CMP #$90      
    $1441: D0 0A      BNE $144d        ; → L_144D
    $1443: B9 BF 19   LDA $19bf,y   
    $1446: 9D F6 17   STA $17f6,x   
    $1449: A8         TAY           
    $144A: B9 B8 19   LDA $19b8,y   
L_144D:
    $144D: 8D 1F 10   STA $101f     
    $1450: B9 BF 19   LDA $19bf,y   
    $1453: 8D 1E 10   STA $101e     
    $1456: C8         INY           
    $1457: BD 20 18   LDA $1820,x   
    $145A: 18         CLC           
    $145B: 6D 1E 10   ADC $101e     
    $145E: 9D 20 18   STA $1820,x   
    $1461: BD 23 18   LDA $1823,x   
    $1464: 6D 1F 10   ADC $101f     
    $1467: 9D 23 18   STA $1823,x   
    $146A: BD 26 18   LDA $1826,x   
    $146D: 18         CLC           
    $146E: 69 01      ADC #$01      
    $1470: 9D 26 18   STA $1826,x   
    $1473: BD 29 18   LDA $1829,x   
    $1476: 69 00      ADC #$00      
    $1478: 9D 29 18   STA $1829,x   
    $147B: D9 B8 19   CMP $19b8,y   
    $147E: D0 16      BNE $1496        ; → L_1496
    $1480: BD 26 18   LDA $1826,x   
    $1483: D9 BF 19   CMP $19bf,y   
    $1486: D0 0E      BNE $1496        ; → L_1496
    $1488: A9 00      LDA #$00      
    $148A: 9D 26 18   STA $1826,x   
    $148D: 9D 29 18   STA $1829,x   
    $1490: FE F6 17   INC $17f6,x   
    $1493: FE F6 17   INC $17f6,x   
L_1496:

; ----- filter_run_v3: VOICE 3 ONLY (CPX #2): advance cutoff $1016/$1017 by filter table ADD; $90 loop
    $1496: E0 02      CPX #$02      
    $1498: D0 5D      BNE $14f7        ; → L_14F7
    $149A: AC F9 17   LDY $17f9     
    $149D: B9 C6 19   LDA $19c6,y   
    $14A0: C9 90      CMP #$90      
    $14A2: D0 0A      BNE $14ae        ; → L_14AE
    $14A4: B9 C7 19   LDA $19c7,y   
    $14A7: 8D F9 17   STA $17f9     
    $14AA: A8         TAY           
    $14AB: B9 C6 19   LDA $19c6,y   
L_14AE:
    $14AE: 8D 1F 10   STA $101f     
    $14B1: B9 C7 19   LDA $19c7,y   
    $14B4: 8D 1E 10   STA $101e     
    $14B7: C8         INY           
    $14B8: AD 17 10   LDA $1017     
    $14BB: 18         CLC           
    $14BC: 6D 1E 10   ADC $101e     
    $14BF: 8D 17 10   STA $1017     
    $14C2: AD 16 10   LDA $1016     
    $14C5: 6D 1F 10   ADC $101f     
    $14C8: 8D 16 10   STA $1016     
    $14CB: AD 3B 18   LDA $183b     
    $14CE: 18         CLC           
    $14CF: 69 01      ADC #$01      
    $14D1: 8D 3B 18   STA $183b     
    $14D4: AD 3C 18   LDA $183c     
    $14D7: 69 00      ADC #$00      
    $14D9: 8D 3C 18   STA $183c     
    $14DC: D9 C6 19   CMP $19c6,y   
    $14DF: D0 16      BNE $14f7        ; → L_14F7
    $14E1: AD 3B 18   LDA $183b     
    $14E4: D9 C7 19   CMP $19c7,y   
    $14E7: D0 0E      BNE $14f7        ; → L_14F7
    $14E9: A9 00      LDA #$00      
    $14EB: 8D 3B 18   STA $183b     
    $14EE: 8D 3C 18   STA $183c     
    $14F1: EE F9 17   INC $17f9     
    $14F4: EE F9 17   INC $17f9     
L_14F7:

; ----- glide_slide: if speed!=0: ramp freq accum $1835/$1838 toward target note $17F0; arrival snaps
    $14F7: BD ED 17   LDA $17ed,x   
    $14FA: D0 03      BNE $14ff        ; → L_14FF
    $14FC: 4C 92 15   JMP $1592        ; → L_1592
L_14FF:
    $14FF: BD 0F 10   LDA $100f,x   
    $1502: DD F0 17   CMP $17f0,x   
    $1505: B0 4E      BCS $1555        ; → L_1555
    $1507: BD 35 18   LDA $1835,x   
    $150A: 18         CLC           
    $150B: 7D ED 17   ADC $17ed,x   
    $150E: 9D 35 18   STA $1835,x   
    $1511: BD 38 18   LDA $1838,x   
    $1514: 69 00      ADC #$00      
    $1516: 9D 38 18   STA $1838,x   
    $1519: BD 0E 18   LDA $180e,x   
    $151C: 18         CLC           
    $151D: 7D 35 18   ADC $1835,x   
    $1520: 8D 3D 18   STA $183d     
    $1523: BD 11 18   LDA $1811,x   
    $1526: 7D 38 18   ADC $1838,x   
    $1529: 8D 3E 18   STA $183e     
    $152C: BC F0 17   LDY $17f0,x   
    $152F: D9 6F 17   CMP $176f,y   
    $1532: D0 5B      BNE $158f        ; → L_158F
L_1534:
    $1534: BD F0 17   LDA $17f0,x   
    $1537: 9D 0F 10   STA $100f,x   
    $153A: A8         TAY           
    $153B: B9 0F 17   LDA $170f,y   
    $153E: 9D 0E 18   STA $180e,x   
    $1541: B9 6F 17   LDA $176f,y   
    $1544: 9D 11 18   STA $1811,x   
    $1547: A9 00      LDA #$00      
    $1549: 9D 35 18   STA $1835,x   
    $154C: 9D 38 18   STA $1838,x   
    $154F: 9D ED 17   STA $17ed,x   
    $1552: 4C 92 15   JMP $1592        ; → L_1592
L_1555:
    $1555: BD 35 18   LDA $1835,x   
    $1558: 38         SEC           
    $1559: FD ED 17   SBC $17ed,x   
    $155C: 9D 35 18   STA $1835,x   
    $155F: BD 38 18   LDA $1838,x   
    $1562: E9 00      SBC #$00      
    $1564: 9D 38 18   STA $1838,x   
    $1567: BD 0E 18   LDA $180e,x   
    $156A: 18         CLC           
    $156B: 7D 35 18   ADC $1835,x   
    $156E: 8D 3D 18   STA $183d     
    $1571: BD 11 18   LDA $1811,x   
    $1574: 7D 38 18   ADC $1838,x   
    $1577: 8D 3E 18   STA $183e     
    $157A: BC F0 17   LDY $17f0,x   
    $157D: D9 6F 17   CMP $176f,y   
    $1580: 90 B2      BCC $1534        ; → L_1534
    $1582: D0 0B      BNE $158f        ; → L_158F
    $1584: AD 3D 18   LDA $183d     
    $1587: D9 0F 17   CMP $170f,y   
    $158A: B0 03      BCS $158f        ; → L_158F
    $158C: 4C 34 15   JMP $1534        ; → L_1534
L_158F:
    $158F: 4C 14 16   JMP $1614        ; → L_1614
L_1592:

; ----- vibrato: triangle: accum $1835/$1838 +/- vib step $1802/$1805, period $17FF, after delay $17FC
    $1592: BD EA 17   LDA $17ea,x   
    $1595: F0 0B      BEQ $15a2        ; → L_15A2
    $1597: A9 00      LDA #$00      
    $1599: 9D 35 18   STA $1835,x   
    $159C: 9D 38 18   STA $1838,x   
    $159F: 4C 14 16   JMP $1614        ; → L_1614
L_15A2:
    $15A2: BD FF 17   LDA $17ff,x   
    $15A5: F0 6D      BEQ $1614        ; → L_1614
    $15A7: BD FC 17   LDA $17fc,x   
    $15AA: F0 06      BEQ $15b2        ; → L_15B2
    $15AC: DE FC 17   DEC $17fc,x   
    $15AF: 4C 14 16   JMP $1614        ; → L_1614
L_15B2:
    $15B2: BD 2F 18   LDA $182f,x   
    $15B5: D0 37      BNE $15ee        ; → L_15EE
    $15B7: BD 35 18   LDA $1835,x   
    $15BA: 18         CLC           
    $15BB: 7D 02 18   ADC $1802,x   
    $15BE: 9D 35 18   STA $1835,x   
    $15C1: BD 38 18   LDA $1838,x   
    $15C4: 7D 05 18   ADC $1805,x   
    $15C7: 9D 38 18   STA $1838,x   
    $15CA: FE 32 18   INC $1832,x   
    $15CD: BD 32 18   LDA $1832,x   
    $15D0: DD FF 17   CMP $17ff,x   
    $15D3: D0 3F      BNE $1614        ; → L_1614
    $15D5: A9 00      LDA #$00      
    $15D7: 9D 32 18   STA $1832,x   
    $15DA: FE 2F 18   INC $182f,x   
    $15DD: BD 2C 18   LDA $182c,x   
    $15E0: D0 32      BNE $1614        ; → L_1614
    $15E2: 1E 02 18   ASL $1802,x   
    $15E5: 3E 05 18   ROL $1805,x   
    $15E8: FE 2C 18   INC $182c,x   
    $15EB: 4C 14 16   JMP $1614        ; → L_1614
L_15EE:
    $15EE: BD 35 18   LDA $1835,x   
    $15F1: 38         SEC           
    $15F2: FD 02 18   SBC $1802,x   
    $15F5: 9D 35 18   STA $1835,x   
    $15F8: BD 38 18   LDA $1838,x   
    $15FB: FD 05 18   SBC $1805,x   
    $15FE: 9D 38 18   STA $1838,x   
    $1601: FE 32 18   INC $1832,x   
    $1604: BD 32 18   LDA $1832,x   
    $1607: DD FF 17   CMP $17ff,x   
    $160A: D0 08      BNE $1614        ; → L_1614
    $160C: A9 00      LDA #$00      
    $160E: 9D 32 18   STA $1832,x   
    $1611: DE 2F 18   DEC $182f,x   
L_1614:

; ----- fade: FD-: master vol $101B/$101C -= $1019; FD+: += $1018 (cap $0F)
    $1614: AD 19 10   LDA $1019     
    $1617: F0 19      BEQ $1632        ; → L_1632
    $1619: AD 1C 10   LDA $101c     
    $161C: 38         SEC           
    $161D: ED 19 10   SBC $1019     
    $1620: 8D 1C 10   STA $101c     
    $1623: AD 1B 10   LDA $101b     
    $1626: E9 00      SBC #$00      
    $1628: 8D 1B 10   STA $101b     
    $162B: D0 05      BNE $1632        ; → L_1632
    $162D: A9 00      LDA #$00      
    $162F: 8D 19 10   STA $1019     
L_1632:
    $1632: AD 18 10   LDA $1018     
    $1635: F0 1B      BEQ $1652        ; → L_1652
    $1637: AD 1C 10   LDA $101c     
    $163A: 18         CLC           
    $163B: 6D 18 10   ADC $1018     
    $163E: 8D 1C 10   STA $101c     
    $1641: AD 1B 10   LDA $101b     
    $1644: 69 00      ADC #$00      
    $1646: 8D 1B 10   STA $101b     
    $1649: C9 0F      CMP #$0f      
    $164B: D0 05      BNE $1652        ; → L_1652
    $164D: A9 00      LDA #$00      
    $164F: 8D 18 10   STA $1018     
L_1652:

; ----- write_vol: $D418 = $101B master vol | $1015 filter mode
    $1652: AD 1B 10   LDA $101b     
    $1655: 0D 15 10   ORA $1015     
    $1658: 8D 18 D4   STA $d418      ;VOL
L_165B:

; ----- wave_step: steady wave-table step: $90 loop; drum vs melodic; -> $180E/$1811 freq + $1814 ctrl
    $165B: BC F3 17   LDY $17f3,x   
    $165E: B9 9E 19   LDA $199e,y   
    $1661: C9 90      CMP #$90      
    $1663: D0 0A      BNE $166f        ; → L_166F
    $1665: B9 AB 19   LDA $19ab,y   
    $1668: 9D F3 17   STA $17f3,x   
    $166B: A8         TAY           
    $166C: B9 9E 19   LDA $199e,y   
L_166F:
    $166F: 9D 14 18   STA $1814,x   
    $1672: 29 08      AND #$08      
    $1674: F0 0E      BEQ $1684        ; → L_1684
    $1676: B9 AB 19   LDA $19ab,y   
    $1679: 9D 11 18   STA $1811,x   
    $167C: A9 00      LDA #$00      
    $167E: 9D 0E 18   STA $180e,x   
    $1681: 4C 98 16   JMP $1698        ; → L_1698
L_1684:
    $1684: B9 AB 19   LDA $19ab,y   
    $1687: 18         CLC           
    $1688: 7D 0F 10   ADC $100f,x   
    $168B: A8         TAY           
    $168C: B9 0F 17   LDA $170f,y   
    $168F: 9D 0E 18   STA $180e,x   
    $1692: B9 6F 17   LDA $176f,y   
    $1695: 9D 11 18   STA $1811,x   
L_1698:
    $1698: FE F3 17   INC $17f3,x   
L_169B:

; ----- gate_logic: peek lookahead $181D,x: tie cmds keep gate; else dur==1 -> SR=0, dur==2 on tick -> $1817=$F6 (hard restart)
    $169B: BC 09 10   LDY $1009,x   
    $169E: BD 1D 18   LDA $181d,x   
    $16A1: C9 FE      CMP #$fe      
    $16A3: F0 41      BEQ $16e6        ; → L_16E6
    $16A5: C9 F4      CMP #$f4      
    $16A7: F0 3D      BEQ $16e6        ; → L_16E6
    $16A9: C9 FA      CMP #$fa      
    $16AB: F0 39      BEQ $16e6        ; → L_16E6
    $16AD: C9 F2      CMP #$f2      
    $16AF: F0 35      BEQ $16e6        ; → L_16E6
    $16B1: C9 F1      CMP #$f1      
    $16B3: F0 31      BEQ $16e6        ; → L_16E6
    $16B5: C9 F5      CMP #$f5      
    $16B7: F0 14      BEQ $16cd        ; → L_16CD
    $16B9: BD EA 17   LDA $17ea,x   
    $16BC: D0 28      BNE $16e6        ; → L_16E6
L_16BE:
    $16BE: BD DB 17   LDA $17db,x   
    $16C1: C9 01      CMP #$01      
    $16C3: D0 10      BNE $16d5        ; → L_16D5
    $16C5: A9 00      LDA #$00      
    $16C7: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $16CA: 4C E6 16   JMP $16e6        ; → L_16E6
L_16CD:
    $16CD: BD EA 17   LDA $17ea,x   
    $16D0: F0 14      BEQ $16e6        ; → L_16E6
    $16D2: 4C BE 16   JMP $16be        ; → L_16BE
L_16D5:
    $16D5: BD DB 17   LDA $17db,x   
    $16D8: C9 02      CMP #$02      
    $16DA: D0 0A      BNE $16e6        ; → L_16E6
    $16DC: AD 13 10   LDA $1013     
    $16DF: D0 05      BNE $16e6        ; → L_16E6
    $16E1: A9 F6      LDA #$f6      
    $16E3: 9D 17 18   STA $1817,x   
L_16E6:

; ----- sid_write: WRITE ORDER (Y=$1009,x): $D400 freqlo,$D401 freqhi,$D402 pwlo,$D403 pwhi,$D404 ctrl(AND $1817 mask)
    $16E6: BD 0E 18   LDA $180e,x   
    $16E9: 18         CLC           
    $16EA: 7D 35 18   ADC $1835,x   
    $16ED: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $16F0: BD 11 18   LDA $1811,x   
    $16F3: 7D 38 18   ADC $1838,x   
    $16F6: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $16F9: BD 20 18   LDA $1820,x   
    $16FC: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $16FF: BD 23 18   LDA $1823,x   
    $1702: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $1705: BD 14 18   LDA $1814,x   
    $1708: 3D 17 18   AND $1817,x   
    $170B: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $170E: 60         RTS           
; ----- data gap $170F-$19C8 (698 bytes) -----

