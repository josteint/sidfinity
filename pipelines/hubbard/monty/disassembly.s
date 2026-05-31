; ============================================================================
; Rob Hubbard - Monty on the Run (1985 Gremlin Graphics)
; ANNOTATED DISASSEMBLY  (auto-traced seed + hand-annotated header)
; ============================================================================
;
; Binary: demo/hubbard/Monty_on_the_Run_original.sid  ($8000-$95BF, 5568 b)
; Load $8000   Init $8000 (JMP $95A0)   Play $8012
; PSID: 19 subtunes — 3 music (0-2), 16 SFX (3-18).
;
; Same Hubbard '85 engine family as Commando and Devils Galop: per-voice
; loop X=2..0 (V3,V2,V1), 8-byte instrument records, the 5-bit note
; duration field, vibrato/PWM/skydive/arp effects.
;
; ENGINE LAYOUT
; ------------
;   Freq table   $8400, 96 musical entries ($8400-$84BF, interleaved lo,hi).
;   Instr table  $93B4, 20 records x 8 bytes
;                (+0 pw_lo +1 pw_hi +2 ctrl +3 ad +4 sr +5 vib_depth
;                 +6 pwm_speed +7 fx_flags).
;
; THE NOTENUM / FREQ-TABLE OVERLAP  (the load-bearing quirk)
; ---------------------------------
;   The engine's per-voice variables sit DIRECTLY past the 96-entry freq
;   table, starting at $84C0. So a freq lookup for an off-table pitch
;   (>= 96) reads live engine state. In particular:
;       v_ctrl[V1/V2/V3] = $84D0/$84D1/$84D2  = freq entries 104-105
;       v_pitch[V1/V2/V3] = $84D3/$84D4/$84D5 = freq entries 105-106
;   A note at pitch 104 therefore loads freq = ($84D0,$84D1) =
;   (v_ctrl[V1], v_ctrl[V2]). v_ctrl is written at note-load ($815A)
;   AFTER the freq read ($80FA-$8115) and voices run V3,V2,V1 — so V2's
;   pitch-104 read sees V1's v_ctrl from the PREVIOUS frame (or, on
;   frame 0, the binary's load-time bytes: $84D0 = 41 41).
;   => the rebuild must store v_ctrl IN the emitted freq table at
;      offset 104, seeded from the binary, not in a separate variable.
;
; VARIABLE MAP  ($84C0-$8505 — all per-voice arrays are 3 bytes V1,V2,V3)
; ------------
;   $84C0-C2  sid_base[3]      0,7,14 (per-voice $D4xx offset)
;   $84C3     sid_base_cur     current voice's offset (scratch)
;   $84C4-C6  pat_cursor[3]    byte offset into the orderlist stream ($02)
;   $84C7-C9  note_cursor[3]   byte offset into the pattern stream ($04)
;   $84CA-CC  v_dur[3]         note duration countdown
;   $84CD-CF  note_flags[3]    raw note byte (bit5 ?, bit6 tie, dur=bits0-4)
;   $84D0-D2  v_ctrl[3]        <-- freq entries 104-105 (the overlap)
;   $84D3-D5  v_pitch[3]       <-- freq entries 105-106 (the overlap)
;   $84D6-D8  v_instr[3]
;   $84D9     ctrl_mask        $FF, or $FE to gate the note's first ctrl
;   $84DA-DD  scratch (note flags / freq / X-save / instr ctrl)
;   $84DE     vib_depth        right-shift count for the vibrato delta
;   $84DF     pwm_speed
;   $84E0-E1  vib_delta lo/hi
;   $84E2-E3  vib_target lo/hi
;   $84E4     vib_lfo_step     frame_ctr&7 folded to a 0-3 triangle
;   $84E5-E7  pwm_period[3]
;   $84E8-EA  pwm_dir[3]
;   $84EB     tick_ctr         decremented each frame
;   $84EC     tick_reload      tempo divider (per-subtune)
;   $84ED     instr*8 scratch (effects)
;   $84EE     mode flags       $40 first-frame / $C0 SFX / $00 running
;   $84EF-F1  v_freq_hi[3]
;   $84F2-F4  v_freq_lo[3]
;   $84F5-F7  porta_trig[3]    per-note portamento/slide trigger byte
;   $84F8     fx_flags scratch
;   $84F9     pwm rate scratch
;   $84FA     frame_ctr        INC'd once per play()
;   $84FB-FC  drum / priority state
;   $84FD     write_enable     $FF = emit this voice's SID writes
;   $84FE-FF, $8500-8505   SFX engine state
;
; FRAME STRUCTURE  (play $8012)
; ---------------
;   vol=$0F; INC frame_ctr; dispatch on $84EE (first-frame init / SFX /
;   run). Run: tick_ctr--, reload at -1; then voices X=2,1,0:
;     - tick frame  -> note advance ($8086): read pattern, decode note
;       (pitch $84D3,x, instr $84D6,x, dur $84CA,x), write freq+instr.
;     - non-tick    -> effects only ($819B onward).
;   Effects ($81A3): vibrato, PWM, then fx_flags bit0/1/2.
;
; EFFECT CONSTANTS  (per-engine deltas vs Commando)
; ----------------
;   Vibrato onset  CMP #$08 at $8201  -> vib_onset = 8  (Commando 6).
;   Arpeggio       ADC #$0C at $8348  -> arp interval 12 (= Commando).
;   PWM bounds     $08 / $0E hardcoded (= Commando).
;   fx_flags: bit0 skydive (DEC v_freq_hi), bit1 odd-frame freq_hi DEC,
;             bit2 arpeggio.
;
; ============================================================================

; ======= init: =======
init:
    $8000: 4C A0 95   JMP $95a0        ; → L_95A0
; ----- data gap $8003-$8011 (15 bytes) -----

; ======= play: =======
play:
    $8012: A9 0F      LDA #$0f      
    $8014: 8D 18 D4   STA $d418      ;VOL
    $8017: EE FA 84   INC $84fa     
    $801A: 2C EE 84   BIT $84ee     
    $801D: 30 1E      BMI $803d        ; → L_803D
    $801F: 50 31      BVC $8052        ; → L_8052
    $8021: A9 00      LDA #$00      
    $8023: 8D FA 84   STA $84fa     
    $8026: A2 02      LDX #$02      
L_8028:
    $8028: 9D C4 84   STA $84c4,x   
    $802B: 9D C7 84   STA $84c7,x   
    $802E: 9D CA 84   STA $84ca,x   
    $8031: 9D D3 84   STA $84d3,x   
    $8034: CA         DEX           
    $8035: 10 F1      BPL $8028        ; → L_8028
    $8037: 8D EE 84   STA $84ee     
    $803A: 4C 52 80   JMP $8052        ; → L_8052
L_803D:
    $803D: 50 10      BVC $804f        ; → L_804F
    $803F: A9 00      LDA #$00      
    $8041: 8D 04 D4   STA $d404      ;V1_CTRL
    $8044: 8D 0B D4   STA $d40b      ;V2_CTRL
    $8047: 8D 12 D4   STA $d412      ;V3_CTRL
    $804A: A9 80      LDA #$80      
    $804C: 8D EE 84   STA $84ee     
L_804F:
    $804F: 4C 7D 83   JMP $837d        ; → L_837D
L_8052:
    $8052: A2 02      LDX #$02      
    $8054: CE EB 84   DEC $84eb     
    $8057: 10 06      BPL $805f        ; → L_805F
    $8059: AD EC 84   LDA $84ec     
    $805C: 8D EB 84   STA $84eb     
L_805F:
    $805F: BD C0 84   LDA $84c0,x   
    $8062: 8D C3 84   STA $84c3     
    $8065: A8         TAY           
    $8066: AD EB 84   LDA $84eb     
    $8069: CD EC 84   CMP $84ec     
    $806C: D0 15      BNE $8083        ; → L_8083
    $806E: BD 66 85   LDA $8566,x   
    $8071: 85 02      STA $02       
    $8073: BD 69 85   LDA $8569,x   
    $8076: 85 03      STA $03       
    $8078: DE CA 84   DEC $84ca,x   
    $807B: 30 09      BMI $8086        ; → L_8086
    $807D: 4C 74 81   JMP $8174        ; → L_8174
; ----- data gap $8080-$8082 (3 bytes) -----

L_8083:
    $8083: 4C 9B 81   JMP $819b        ; → L_819B
L_8086:
    $8086: BC C4 84   LDY $84c4,x   
    $8089: B1 02      LDA ($02),y   
    $808B: C9 FF      CMP #$ff      
    $808D: F0 0A      BEQ $8099        ; → L_8099
    $808F: C9 FE      CMP #$fe      
    $8091: D0 17      BNE $80aa        ; → L_80AA
    $8093: EA         NOP           
    $8094: EA         NOP           
    $8095: EA         NOP           
    $8096: 4C 7D 83   JMP $837d        ; → L_837D
L_8099:
    $8099: A9 00      LDA #$00      
    $809B: 9D CA 84   STA $84ca,x   
    $809E: 9D C4 84   STA $84c4,x   
    $80A1: 9D C7 84   STA $84c7,x   
    $80A4: 4C 86 80   JMP $8086        ; → L_8086
; ----- data gap $80A7-$80A9 (3 bytes) -----

L_80AA:
    $80AA: A8         TAY           
    $80AB: B9 7E 85   LDA $857e,y   
    $80AE: 85 04      STA $04       
    $80B0: B9 CB 85   LDA $85cb,y   
    $80B3: 85 05      STA $05       
    $80B5: A9 00      LDA #$00      
    $80B7: 9D F5 84   STA $84f5,x   
    $80BA: BC C7 84   LDY $84c7,x   
    $80BD: A9 FF      LDA #$ff      
    $80BF: 8D D9 84   STA $84d9     
    $80C2: B1 04      LDA ($04),y   
    $80C4: 9D CD 84   STA $84cd,x   
    $80C7: 8D DA 84   STA $84da     
    $80CA: 29 1F      AND #$1f      
    $80CC: 9D CA 84   STA $84ca,x   
    $80CF: 2C DA 84   BIT $84da     
    $80D2: 70 44      BVS $8118        ; → L_8118
    $80D4: FE C7 84   INC $84c7,x   
    $80D7: AD DA 84   LDA $84da     
    $80DA: 10 11      BPL $80ed        ; → L_80ED
    $80DC: C8         INY           
    $80DD: B1 04      LDA ($04),y   
    $80DF: 10 06      BPL $80e7        ; → L_80E7
    $80E1: 9D F5 84   STA $84f5,x   
    $80E4: 4C EA 80   JMP $80ea        ; → L_80EA
L_80E7:
    $80E7: 9D D6 84   STA $84d6,x   
L_80EA:
    $80EA: FE C7 84   INC $84c7,x   
L_80ED:
    $80ED: C8         INY           
    $80EE: B1 04      LDA ($04),y   
    $80F0: 9D D3 84   STA $84d3,x   
    $80F3: 0A         ASL a         
    $80F4: A8         TAY           
    $80F5: AD FD 84   LDA $84fd     
    $80F8: 10 21      BPL $811b        ; → L_811B
    $80FA: B9 00 84   LDA $8400,y   
    $80FD: 8D DB 84   STA $84db     
    $8100: B9 01 84   LDA $8401,y   
    $8103: AC C3 84   LDY $84c3     
    $8106: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $8109: 9D EF 84   STA $84ef,x   
    $810C: AD DB 84   LDA $84db     
    $810F: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $8112: 9D F2 84   STA $84f2,x   
    $8115: 4C 1B 81   JMP $811b        ; → L_811B
L_8118:
    $8118: CE D9 84   DEC $84d9     
L_811B:
    $811B: AC C3 84   LDY $84c3     
    $811E: BD D6 84   LDA $84d6,x   
    $8121: 8E DC 84   STX $84dc     
    $8124: 0A         ASL a         
    $8125: 0A         ASL a         
    $8126: 0A         ASL a         
    $8127: AA         TAX           
    $8128: BD B6 93   LDA $93b6,x   
    $812B: 8D DD 84   STA $84dd     
    $812E: AD FD 84   LDA $84fd     
    $8131: 10 21      BPL $8154        ; → L_8154
    $8133: BD B6 93   LDA $93b6,x   
    $8136: 2D D9 84   AND $84d9     
    $8139: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $813C: BD B4 93   LDA $93b4,x   
    $813F: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $8142: BD B5 93   LDA $93b5,x   
    $8145: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $8148: BD B7 93   LDA $93b7,x   
    $814B: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $814E: BD B8 93   LDA $93b8,x   
    $8151: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_8154:
    $8154: AE DC 84   LDX $84dc     
    $8157: AD DD 84   LDA $84dd     
    $815A: 9D D0 84   STA $84d0,x   
    $815D: FE C7 84   INC $84c7,x   
    $8160: BC C7 84   LDY $84c7,x   
    $8163: B1 04      LDA ($04),y   
    $8165: C9 FF      CMP #$ff      
    $8167: D0 08      BNE $8171        ; → L_8171
    $8169: A9 00      LDA #$00      
    $816B: 9D C7 84   STA $84c7,x   
    $816E: FE C4 84   INC $84c4,x   
L_8171:
    $8171: 4C 67 83   JMP $8367        ; → L_8367
L_8174:
    $8174: AD FD 84   LDA $84fd     
    $8177: 30 03      BMI $817c        ; → L_817C
    $8179: 4C 67 83   JMP $8367        ; → L_8367
L_817C:
    $817C: AC C3 84   LDY $84c3     
    $817F: BD CD 84   LDA $84cd,x   
    $8182: 29 20      AND #$20      
    $8184: D0 15      BNE $819b        ; → L_819B
    $8186: BD CA 84   LDA $84ca,x   
    $8189: D0 10      BNE $819b        ; → L_819B
    $818B: BD D0 84   LDA $84d0,x   
    $818E: 29 FE      AND #$fe      
    $8190: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $8193: A9 00      LDA #$00      
    $8195: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $8198: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_819B:
    $819B: AD FD 84   LDA $84fd     
    $819E: 30 03      BMI $81a3        ; → L_81A3
    $81A0: 4C 67 83   JMP $8367        ; → L_8367
L_81A3:
    $81A3: BD D6 84   LDA $84d6,x   
    $81A6: 0A         ASL a         
    $81A7: 0A         ASL a         
    $81A8: 0A         ASL a         
    $81A9: A8         TAY           
    $81AA: 8C ED 84   STY $84ed     
    $81AD: B9 BB 93   LDA $93bb,y   
    $81B0: 8D F8 84   STA $84f8     
    $81B3: B9 BA 93   LDA $93ba,y   
    $81B6: 8D DF 84   STA $84df     
    $81B9: B9 B9 93   LDA $93b9,y   
    $81BC: 8D DE 84   STA $84de     
    $81BF: F0 6F      BEQ $8230        ; → L_8230
    $81C1: AD FA 84   LDA $84fa     
    $81C4: 29 07      AND #$07      
    $81C6: C9 04      CMP #$04      
    $81C8: 90 02      BCC $81cc        ; → L_81CC
    $81CA: 49 07      EOR #$07      
L_81CC:
    $81CC: 8D E4 84   STA $84e4     
    $81CF: BD D3 84   LDA $84d3,x   
    $81D2: 0A         ASL a         
    $81D3: A8         TAY           
    $81D4: 38         SEC           
    $81D5: B9 02 84   LDA $8402,y   
    $81D8: F9 00 84   SBC $8400,y   
    $81DB: 8D E0 84   STA $84e0     
    $81DE: B9 03 84   LDA $8403,y   
    $81E1: F9 01 84   SBC $8401,y   
L_81E4:
    $81E4: 4A         LSR a         
    $81E5: 6E E0 84   ROR $84e0     
    $81E8: CE DE 84   DEC $84de     
    $81EB: 10 F7      BPL $81e4        ; → L_81E4
    $81ED: 8D E1 84   STA $84e1     
    $81F0: B9 00 84   LDA $8400,y   
    $81F3: 8D E2 84   STA $84e2     
    $81F6: B9 01 84   LDA $8401,y   
    $81F9: 8D E3 84   STA $84e3     
    $81FC: BD CD 84   LDA $84cd,x   
    $81FF: 29 1F      AND #$1f      
    $8201: C9 08      CMP #$08      
    $8203: 90 1C      BCC $8221        ; → L_8221
    $8205: AC E4 84   LDY $84e4     
L_8208:
    $8208: 88         DEY           
    $8209: 30 16      BMI $8221        ; → L_8221
    $820B: 18         CLC           
    $820C: AD E2 84   LDA $84e2     
    $820F: 6D E0 84   ADC $84e0     
    $8212: 8D E2 84   STA $84e2     
    $8215: AD E3 84   LDA $84e3     
    $8218: 6D E1 84   ADC $84e1     
    $821B: 8D E3 84   STA $84e3     
    $821E: 4C 08 82   JMP $8208        ; → L_8208
L_8221:
    $8221: AC C3 84   LDY $84c3     
    $8224: AD E2 84   LDA $84e2     
    $8227: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $822A: AD E3 84   LDA $84e3     
    $822D: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_8230:
    $8230: AD DF 84   LDA $84df     
    $8233: F0 62      BEQ $8297        ; → L_8297
    $8235: AC ED 84   LDY $84ed     
    $8238: 29 1F      AND #$1f      
    $823A: DE E5 84   DEC $84e5,x   
    $823D: 10 58      BPL $8297        ; → L_8297
    $823F: 9D E5 84   STA $84e5,x   
    $8242: AD DF 84   LDA $84df     
    $8245: 29 E0      AND #$e0      
    $8247: 8D F9 84   STA $84f9     
    $824A: BD E8 84   LDA $84e8,x   
    $824D: D0 1A      BNE $8269        ; → L_8269
    $824F: AD F9 84   LDA $84f9     
    $8252: 18         CLC           
    $8253: 79 B4 93   ADC $93b4,y   
    $8256: 48         PHA           
    $8257: B9 B5 93   LDA $93b5,y   
    $825A: 69 00      ADC #$00      
    $825C: 29 0F      AND #$0f      
    $825E: 48         PHA           
    $825F: C9 0E      CMP #$0e      
    $8261: D0 1D      BNE $8280        ; → L_8280
    $8263: FE E8 84   INC $84e8,x   
    $8266: 4C 80 82   JMP $8280        ; → L_8280
L_8269:
    $8269: 38         SEC           
    $826A: B9 B4 93   LDA $93b4,y   
    $826D: ED F9 84   SBC $84f9     
    $8270: 48         PHA           
    $8271: B9 B5 93   LDA $93b5,y   
    $8274: E9 00      SBC #$00      
    $8276: 29 0F      AND #$0f      
    $8278: 48         PHA           
    $8279: C9 08      CMP #$08      
    $827B: D0 03      BNE $8280        ; → L_8280
    $827D: DE E8 84   DEC $84e8,x   
L_8280:
    $8280: 8E DC 84   STX $84dc     
    $8283: AE C3 84   LDX $84c3     
    $8286: 68         PLA           
    $8287: 99 B5 93   STA $93b5,y   
    $828A: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $828D: 68         PLA           
    $828E: 99 B4 93   STA $93b4,y   
    $8291: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $8294: AE DC 84   LDX $84dc     
L_8297:
    $8297: AC C3 84   LDY $84c3     
    $829A: BD F5 84   LDA $84f5,x   
    $829D: F0 3F      BEQ $82de        ; → L_82DE
    $829F: 29 7E      AND #$7e      
    $82A1: 8D DC 84   STA $84dc     
    $82A4: BD F5 84   LDA $84f5,x   
    $82A7: 29 01      AND #$01      
    $82A9: F0 1B      BEQ $82c6        ; → L_82C6
    $82AB: 38         SEC           
    $82AC: BD F2 84   LDA $84f2,x   
    $82AF: ED DC 84   SBC $84dc     
    $82B2: 9D F2 84   STA $84f2,x   
    $82B5: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $82B8: BD EF 84   LDA $84ef,x   
    $82BB: E9 00      SBC #$00      
    $82BD: 9D EF 84   STA $84ef,x   
    $82C0: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $82C3: 4C DE 82   JMP $82de        ; → L_82DE
L_82C6:
    $82C6: 18         CLC           
    $82C7: BD F2 84   LDA $84f2,x   
    $82CA: 6D DC 84   ADC $84dc     
    $82CD: 9D F2 84   STA $84f2,x   
    $82D0: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $82D3: BD EF 84   LDA $84ef,x   
    $82D6: 69 00      ADC #$00      
    $82D8: 9D EF 84   STA $84ef,x   
    $82DB: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_82DE:
    $82DE: AD F8 84   LDA $84f8     
    $82E1: 29 01      AND #$01      
    $82E3: F0 35      BEQ $831a        ; → L_831A
    $82E5: BD EF 84   LDA $84ef,x   
    $82E8: F0 30      BEQ $831a        ; → L_831A
    $82EA: BD CA 84   LDA $84ca,x   
    $82ED: F0 2B      BEQ $831a        ; → L_831A
    $82EF: BD CD 84   LDA $84cd,x   
    $82F2: 29 1F      AND #$1f      
    $82F4: 38         SEC           
    $82F5: E9 01      SBC #$01      
    $82F7: DD CA 84   CMP $84ca,x   
    $82FA: AC C3 84   LDY $84c3     
    $82FD: 90 10      BCC $830f        ; → L_830F
    $82FF: BD EF 84   LDA $84ef,x   
    $8302: DE EF 84   DEC $84ef,x   
    $8305: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $8308: BD D0 84   LDA $84d0,x   
    $830B: 29 FE      AND #$fe      
    $830D: D0 08      BNE $8317        ; → L_8317
L_830F:
    $830F: BD EF 84   LDA $84ef,x   
    $8312: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $8315: A9 80      LDA #$80      
L_8317:
    $8317: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_831A:
    $831A: AD F8 84   LDA $84f8     
    $831D: 29 02      AND #$02      
    $831F: F0 15      BEQ $8336        ; → L_8336
    $8321: AD FA 84   LDA $84fa     
    $8324: 29 01      AND #$01      
    $8326: F0 0E      BEQ $8336        ; → L_8336
    $8328: BD EF 84   LDA $84ef,x   
    $832B: F0 09      BEQ $8336        ; → L_8336
    $832D: DE EF 84   DEC $84ef,x   
    $8330: AC C3 84   LDY $84c3     
    $8333: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_8336:
    $8336: AD F8 84   LDA $84f8     
    $8339: 29 04      AND #$04      
    $833B: F0 2A      BEQ $8367        ; → L_8367
    $833D: AD FA 84   LDA $84fa     
    $8340: 29 01      AND #$01      
    $8342: F0 09      BEQ $834d        ; → L_834D
    $8344: BD D3 84   LDA $84d3,x   
    $8347: 18         CLC           
    $8348: 69 0C      ADC #$0c      
    $834A: 4C 50 83   JMP $8350        ; → L_8350
L_834D:
    $834D: BD D3 84   LDA $84d3,x   
L_8350:
    $8350: 0A         ASL a         
    $8351: A8         TAY           
    $8352: B9 00 84   LDA $8400,y   
    $8355: 8D DB 84   STA $84db     
    $8358: B9 01 84   LDA $8401,y   
    $835B: AC C3 84   LDY $84c3     
    $835E: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $8361: AD DB 84   LDA $84db     
    $8364: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_8367:
    $8367: A0 FF      LDY #$ff      
    $8369: AD FB 84   LDA $84fb     
    $836C: D0 06      BNE $8374        ; → L_8374
    $836E: AD FC 84   LDA $84fc     
    $8371: 30 01      BMI $8374        ; → L_8374
    $8373: C8         INY           
L_8374:
    $8374: 8C FD 84   STY $84fd     
    $8377: CA         DEX           
    $8378: 30 03      BMI $837d        ; → L_837D
    $837A: 4C 5F 80   JMP $805f        ; → L_805F
L_837D:
    $837D: A9 FF      LDA #$ff      
    $837F: 8D FD 84   STA $84fd     
    $8382: AD FB 84   LDA $84fb     
    $8385: D0 05      BNE $838c        ; → L_838C
    $8387: 2C FC 84   BIT $84fc     
    $838A: 10 01      BPL $838d        ; → L_838D
L_838C:
    $838C: 60         RTS           
L_838D:
    $838D: 50 03      BVC $8392        ; → L_8392
    $838F: 20 06 85   JSR $8506        ; → sub_8506
L_8392:
    $8392: CE FF 84   DEC $84ff     
    $8395: 10 F5      BPL $838c        ; → L_838C
    $8397: AD 05 85   LDA $8505     
    $839A: 29 0F      AND #$0f      
    $839C: 8D FF 84   STA $84ff     
    $839F: AD FE 84   LDA $84fe     
    $83A2: CD 00 85   CMP $8500     
    $83A5: D0 0F      BNE $83b6        ; → L_83B6
    $83A7: A2 00      LDX #$00      
    $83A9: 8E 04 D4   STX $d404      ;V1_CTRL
    $83AC: 8E 0B D4   STX $d40b      ;V2_CTRL
    $83AF: CA         DEX           
    $83B0: 8E FC 84   STX $84fc     
    $83B3: 4C 8C 83   JMP $838c        ; → L_838C
L_83B6:
    $83B6: CE FE 84   DEC $84fe     
    $83B9: 0A         ASL a         
    $83BA: A8         TAY           
    $83BB: 2C 05 85   BIT $8505     
    $83BE: 30 20      BMI $83e0        ; → L_83E0
    $83C0: 70 0C      BVS $83ce        ; → L_83CE
    $83C2: B9 00 84   LDA $8400,y   
    $83C5: 8D 00 D4   STA $d400      ;V1_FREQ_LO
    $83C8: B9 01 84   LDA $8401,y   
    $83CB: 8D 01 D4   STA $d401      ;V1_FREQ_HI
L_83CE:
    $83CE: 98         TYA           
    $83CF: 38         SEC           
    $83D0: ED 01 85   SBC $8501     
    $83D3: A8         TAY           
    $83D4: B9 00 84   LDA $8400,y   
    $83D7: 8D 07 D4   STA $d407      ;V2_FREQ_LO
    $83DA: B9 01 84   LDA $8401,y   
    $83DD: 8D 08 D4   STA $d408      ;V2_FREQ_HI
L_83E0:
    $83E0: 2C 02 85   BIT $8502     
    $83E3: 10 0B      BPL $83f0        ; → L_83F0
    $83E5: AD 03 85   LDA $8503     
    $83E8: 49 01      EOR #$01      
    $83EA: 8D 04 D4   STA $d404      ;V1_CTRL
    $83ED: 8D 03 85   STA $8503     
L_83F0:
    $83F0: 50 0B      BVC $83fd        ; → L_83FD
    $83F2: AD 04 85   LDA $8504     
    $83F5: 49 01      EOR #$01      
    $83F7: 8D 0B D4   STA $d40b      ;V2_CTRL
    $83FA: 8D 04 85   STA $8504     
L_83FD:
    $83FD: 4C 8C 83   JMP $838c        ; → L_838C
; ----- data gap $8400-$8505 (262 bytes) -----

sub_8506:
    $8506: A9 00      LDA #$00      
    $8508: 8D 04 D4   STA $d404      ;V1_CTRL
    $850B: 8D 0B D4   STA $d40b      ;V2_CTRL
    $850E: 8D FF 84   STA $84ff     
    $8511: AD FC 84   LDA $84fc     
    $8514: 29 0F      AND #$0f      
    $8516: 8D FC 84   STA $84fc     
    $8519: 0A         ASL a         
    $851A: 0A         ASL a         
    $851B: 0A         ASL a         
    $851C: 0A         ASL a         
    $851D: A8         TAY           
    $851E: B9 54 94   LDA $9454,y   
    $8521: 8D 05 85   STA $8505     
    $8524: B9 55 94   LDA $9455,y   
    $8527: 8D FE 84   STA $84fe     
    $852A: B9 63 94   LDA $9463,y   
    $852D: 8D 00 85   STA $8500     
    $8530: B9 5C 94   LDA $945c,y   
    $8533: 8D 02 85   STA $8502     
    $8536: 29 3F      AND #$3f      
    $8538: 8D 01 85   STA $8501     
    $853B: B9 59 94   LDA $9459,y   
    $853E: 8D 03 85   STA $8503     
    $8541: B9 60 94   LDA $9460,y   
    $8544: 8D 04 85   STA $8504     
    $8547: A2 00      LDX #$00      
L_8549:
    $8549: B9 55 94   LDA $9455,y   
    $854C: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $854F: C8         INY           
    $8550: E8         INX           
    $8551: E0 0E      CPX #$0e      
    $8553: D0 F4      BNE $8549        ; → L_8549
    $8555: AD 05 85   LDA $8505     
    $8558: 29 30      AND #$30      
    $855A: A0 EE      LDY #$ee      
    $855C: C9 20      CMP #$20      
    $855E: F0 02      BEQ $8562        ; → L_8562
    $8560: A0 CE      LDY #$ce      
L_8562:
    $8562: 8C B6 83   STY $83b6     
    $8565: 60         RTS           
; ----- data gap $8566-$9553 (4078 bytes) -----

L_9554:
    $9554: A0 00      LDY #$00      
    $9556: 0A         ASL a         
    $9557: 8D DC 84   STA $84dc     
    $955A: 0A         ASL a         
    $955B: 18         CLC           
    $955C: 6D DC 84   ADC $84dc     
    $955F: AA         TAX           
L_9560:
    $9560: BD 6C 85   LDA $856c,x   
    $9563: 99 66 85   STA $8566,y   
    $9566: E8         INX           
    $9567: C8         INY           
    $9568: C0 06      CPY #$06      
    $956A: D0 F4      BNE $9560        ; → L_9560
    $956C: A9 00      LDA #$00      
    $956E: 8D 04 D4   STA $d404      ;V1_CTRL
    $9571: 8D 0B D4   STA $d40b      ;V2_CTRL
    $9574: 8D 12 D4   STA $d412      ;V3_CTRL
    $9577: A9 40      LDA #$40      
    $9579: 8D EE 84   STA $84ee     
    $957C: 60         RTS           
sub_957D:
    $957D: A9 C0      LDA #$c0      
    $957F: 8D EE 84   STA $84ee     
    $9582: 60         RTS           
; ----- data gap $9583-$9590 (14 bytes) -----

sub_9591:
    $9591: AE FB 84   LDX $84fb     
    $9594: F0 04      BEQ $959a        ; → L_959A
    $9596: 8E FC 84   STX $84fc     
    $9599: 60         RTS           
L_959A:
    $959A: 09 40      ORA #$40      
    $959C: 8D FC 84   STA $84fc     
    $959F: 60         RTS           
L_95A0:
    $95A0: 8D BF 95   STA $95bf     
    $95A3: C9 03      CMP #$03      
    $95A5: B0 03      BCS $95aa        ; → L_95AA
    $95A7: 4C 54 95   JMP $9554        ; → L_9554
L_95AA:
    $95AA: 38         SEC           
    $95AB: E9 03      SBC #$03      
    $95AD: 48         PHA           
    $95AE: 20 7D 95   JSR $957d        ; → sub_957D
    $95B1: 68         PLA           
    $95B2: 20 91 95   JSR $9591        ; → sub_9591
    $95B5: 60         RTS           
; ----- data gap $95B6-$95BF (10 bytes) -----

