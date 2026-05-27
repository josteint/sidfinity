; ============================================================================
; Rob Hubbard - The Last V8 (1985 MAD/Mastertronic)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/Hubbard_Rob/Last_V8.sid
; Load:   $8010   Init: $8D80   Play: $8DB3 (discovered)
; RSID header had play=$0000; init installs IRQ vector at $0314/5 = $8DB3,
; so sidplayfp/the C64 IRQ system runs $8DB3 every raster $80 interrupt.
; RSID:   17 subtune(s), default subtune 1 (A=0 passed to init).
; Binary: $8010-$B5D1 (13762 bytes; ~9.6k of that is digi sample data).
;
; Auto-traced 1622 reachable code bytes from init+play. The play address
; $8DB3 was discovered by running init in py65 and reading $0314/$0315
; afterwards (RSID files have play=$0000 in the header because they install
; their own IRQ hook). The rest of the disassembly is hand-annotated by
; cross-referencing static analysis with the Action Biker / Commando
; Hubbard-driver conventions.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; This is Rob Hubbard's "Phase 2" tracker driver, the same shape as
; Commando / Action Biker, PLUS a second engine for the famous
; title-screen digi-drum samples. The 17 PSID "subtunes" multiplex two
; distinct players:
;
;   subtunes 0..2   → music tracker        (sub_8022)
;   subtunes 3..4   → digi-only / silence  (sub_8CF1 → sub_8D40 → $8E00)
;   subtunes 5..16  → game sound effects   (sub_8541)
;
; init ($8D80): standard RSID setup.
;   1. SEI; clear ZP $F0-$FF.
;   2. Install IRQ vector $0314/5 = $8DB3 (this file's play).
;   3. CIA1 ICR = $7F (disable all CIA1 IRQ sources — VIC drives us).
;   4. VIC IMR = $81 (enable raster IRQ); raster line = $80; D011=$1B.
;   5. PLA → A = subtune number (pushed at $8D81).
;   6. JSR sub_8CE2 (dispatch by subtune: music / sfx / digi).
;   7. STA $01=$37 (RAM+I/O+KERNAL); CLI; RTS.
;
; play ($8DB3): the IRQ handler.
;   1. JSR sub_8D04 (tick whichever engine is active for current subtune).
;   2. STA $01=$37 (restore I/O config in case digi routine clobbered it).
;   3. INC $D019 (acknowledge VIC raster IRQ).
;   4. JMP $EA7E (KERNAL IRQ exit: restore A/X/Y from stack, RTI).
;
; sub_8CE2 (subtune dispatcher, called from init):
;   STA $8FFF (remember subtune for play to read).
;   D418 = $0F (max volume).
;   - subtune < 3 → JMP $8010 → $8C53: copy orderlist pointers (6 bytes
;                   from $8797+subtune*6 → $8791) for music tracker.
;                   Set $8529 = $40 (first-frame flag, BIT-tested by $8022).
;   - subtune 3,4 → JSR $8CF1: SBC #$02, store in $97, zero D400-D417
;                   (silence SID), then JSR sub_8D40 → enable digi player.
;   - subtune 5+  → JSR sub_801F → JMP $8C85: queue sfx number in $8537,
;                   then JMP $8013 → set $8529 = $C0 (end+first-frame),
;                   which $8022 reads as end-of-song → silence music chans.
;
; sub_8D04 (play dispatcher, called from play):
;   LDA $8FFF (subtune).
;   subtune < 3       → JMP $8022 (music tracker tick).
;   subtune 3,4       → CMP #$05; if >=5 jump to music, else RTS (silent).
;   subtune >= 5      → JMP $8022 (sfx rides on tracker scaffolding).
;
; The MUSIC TRACKER ($8022..$83B7):
;   $8022: INC $8535 (master frame counter).
;          BIT $8529: bit7=end-of-song, bit6=first-frame (from $8C53).
;          end-of-song → silence all 3 channels, set vol=$0F, JMP $83B8.
;          first-frame → fall through after clearing voice state at $8033.
;   $8062: Per-voice loop entry, X = 2 then 1 then 0 (V3 → V2 → V1).
;          Decrement global tick divider $8526; reload from $8527 when neg.
;          For each voice X:
;            $84FE  ← $84FB,X (SID base offset: 0/7/14 for V1/V2/V3)
;            Read pattern data at ($FB):Y where:
;              ($FB,$FC) = pattern_ptr[X] (set up when note-load needed)
;              Y         = $84FF,X (pattern position)
;            On note boundary (when tick divider == reload value at $807C):
;              orderlist[$8505,X] read, $FE → song-end, $FF → loop pattern.
;              Else pattern_ptr ← (pat_lo[A], pat_hi[A]) from $87A9/$87C6.
;              First pattern byte: $FF = end-of-pattern (advance orderlist),
;                                  low 5 bits = duration, upper = flags.
;              Read note semitone → $850E,X.
;              If "active" flag $8538<0: load freq from $843B,Y → D400/D401,Y
;                store to $852A,X (hi) and $852D,X (lo) for porta state.
;              Load instrument from $85A1+8*$8511,X:
;                +0/+1 = pulse_lo/hi  +2 = ctrl
;                +3 = AD              +4 = SR
;                +5 = vib_depth       +6 = pwm_speed   +7 = fx_flags
;          Effects at $81A8 onward (always run after note-load):
;            - vibrato ($81E1 freq-table-relative offset, signed)
;            - pwm direction track ($82C2 portamento)
;            - drum/skydive freq slide ($8345)
;            - arpeggio ($8371 — alt freq table read with +$0C semitone)
;   $83B8: end-of-frame tail. Updates $8538 sustain flag, decrements X,
;          loops back to $806F if X >= 0. After all 3 voices: $83B8 →
;          sfx tick (reads $8536/$8537 sfx queue) → $83F1 sfx step →
;          RTS from $83C7.
;
; The DIGI SAMPLE PLAYER ($8E00..$8F08, via sub_8D40):
;   This is Hubbard's famous 8-bit PCM trick: the title-screen drum samples
;   on Last V8 are real audio waveforms piped through V1 via the SID test
;   bit at $D404. The routine:
;     1. Saves $F7-$FA on stack ($D40x base, len-hi, etc. ZP scratch).
;     2. $01=$36 (RAM under I/O at $D000-$DFFF — sample table lives there).
;     3. Looks up sample descriptor at $9000+4*$97 (subtune index = sample#):
;          +0/+1 = src ptr lo/hi   (sample start address)
;          +2/+3 = src end lo/hi   (one-past-last byte)
;     4. D402/D403 = $FFFF (max pulse for V1; sample is amplitude-modulated
;        by toggling V1 test bit at $D404 between $41=pulse+gate and
;        $49=test+pulse+gate).
;     5. D406 = $F0 V1 SR (sustain max).
;     6. CIA2 timer A ($DD04/$DD05) drives the bit-clock: STA $DD0E=$11
;        starts one-shot mode. $DD04 compare gates the inner bit loop.
;     7. Inner loop reads sample byte, shifts bit through $FE via ASL,
;        BCC selects $41 (rectangle on) or $49 (test bit on) → STA $D404.
;        After 8 bits, advance ($FB):Y pointer and reload bit counter.
;     8. After end-of-sample: D418=0 silence, restore ZP, RTS.
;
; The SFX ENGINE ($83B8 tick, $8541 init):
;   Game effects (engine rumble, gunshots, crash) live in subtunes 5..16.
;   $8541 reads a 16-byte descriptor at $8699+16*$8537, copies it into
;   the SFX state region $8540/$8539/$853B/$853C/$853D/$853E/$853F, and
;   primes V1/V2 frequency from $D400/$D407. Then $83B8 ticks every frame:
;   walks freq table forward/backward via $853C, alternates V1/V2 control
;   between two waveforms via $853D/$853E/$853F EOR #$01 toggle.
;
; ============================================================================
;
; DATA TABLES
; ------------
;
; $843B  freq table (96 semitones, lo/hi interleaved 2-byte stride; semi 0
;          = $0116 ≈ ~A0). Indexed via Y = 2 × semitone.
; $85A1  instrument table (16 records × 8 bytes)
;          +0 PW_lo  +1 PW_hi  +2 ctrl  +3 AD  +4 SR
;          +5 vibrato_depth  +6 pwm_speed  +7 fx_flags
; $8699  sfx descriptor table (12 sfx × 16 bytes; one row per sfx slot)
; $8791  active orderlist pointers (lo[3], hi[3]) — copied here from $8797
; $8797  per-subtune orderlist source (3 subtunes × 6 bytes; subtune 0 = music)
;          subtune 0:  $E3 $09 $40   $87 $88 $88   → V1=$87E3 V2=$8809 V3=$8840
;          subtune 1:  $98 $9A $A0   $88 $88 $88   → V1=$8898 V2=$889A V3=$88A0
;          subtune 2:  $A2 $A4 $AC   $88 $88 $88   → V1=$88A2 V2=$88A4 V3=$88AC
; $87A9  pattern pointer lo[29]
; $87C6  pattern pointer hi[29]
; $87E3+ orderlist + pattern data
; $9000+ digi sample descriptors (4 bytes × N): src_lo, src_hi, end_lo, end_hi
; $9100+ digi sample lookup table (raw PCM byte streams)
;
; VOICE STATE ARRAYS (3 bytes each, indexed by X = voice 0..2):
;   $84FB,X  SID base offset (0/7/14)            ($84FE = current voice's)
;   $84FF,X  pattern position (Y index into pat)
;   $8502,X  pattern byte position
;   $8505,X  duration countdown (or 0 = ready)
;   $8508,X  raw flag/dur byte from pattern
;   $850B,X  voice ctrl shadow
;   $850E,X  current note semitone (× 2 = freq table index)
;   $8511,X  instrument number (× 8 = $85A1 offset)
;   $8520,X  pwm direction counter
;   $8523,X  pwm direction flag (0/1)
;   $852A,X  last freq hi (per-voice porta target)
;   $852D,X  last freq lo
;   $8530,X  portamento speed (0 = no porta)
;
; GLOBAL STATE:
;   $8526   global tick divider (DEC every frame, reload from $8527)
;   $8527   reload value for tick divider (frames per note step)
;   $8528   scratch (instrument fx offset × 8)
;   $8529   song state byte: bit7=end, bit6=first-frame (BIT-tested at $8025)
;   $8535   master frame counter (free-running)
;   $8536   sfx-active flag
;   $8537   sfx number queue (0 = none)
;   $8538   "instruments active" flag (BMI = run effects)
;   $853A   sfx tick divider
;   $853B..$853F  sfx state (target note, flags, ctrl toggles)
;   $8540   sfx config byte
;   $8FFF   current subtune (set by sub_8CE2, read by sub_8D04)
;
; ============================================================================

L_8010:
    $8010: 4C 53 8C   JMP $8c53        ; → L_8C53
L_8013:
    $8013: 4C 71 8C   JMP $8c71        ; → L_8C71
; ----- data gap $8016-$801E (9 bytes) -----

; sub_801F: sfx-queue entry trampoline (called from $8D1D for subtune >= 5).
sub_801F:
    $801F: 4C 85 8C   JMP $8c85        ; → L_8C85   ; queue sfx in $8537
; -----------------------------------------------------------------------------
; THE MUSIC TRACKER ENTRY ($8022)
; -----------------------------------------------------------------------------
; Top of every play frame for music subtunes. $8529 holds song state:
;   bit7 = end-of-song (silence chans, then JMP $83B8 sfx-only tail)
;   bit6 = first-frame  (clear voice state then fall into normal play)
; BIT $8529 puts bit7 in N flag and bit6 in V flag.
L_8022:
    $8022: EE 35 85   INC $8535                     ; master frame counter ++
    $8025: 2C 29 85   BIT $8529                     ; test bits 7 and 6
    $8028: 30 1E      BMI $8048        ; → L_8048   ; end-of-song path
    $802A: 50 36      BVC $8062        ; → L_8062   ; normal frame (bits clear)
    ; First-frame setup: zero per-voice state for V1/V2/V3 then clear $8529.
    $802C: A9 00      LDA #$00
    $802E: 8D 35 85   STA $8535                     ; reset frame counter
    $8031: A2 02      LDX #$02                      ; X = 2,1,0
L_8033:
    $8033: 9D FF 84   STA $84ff,x                   ; v_patpos = 0
    $8036: 9D 02 85   STA $8502,x                   ; v_byteoff = 0
    $8039: 9D 05 85   STA $8505,x                   ; v_dur = 0
    $803C: 9D 0E 85   STA $850e,x                   ; v_pitch = 0
    $803F: CA         DEX
    $8040: 10 F1      BPL $8033        ; → L_8033
    $8042: 8D 29 85   STA $8529                     ; clear song-state (run normal)
    $8045: 4C 62 80   JMP $8062        ; → L_8062
; End-of-song path (bit7 of $8529 = 1).
L_8048:
    $8048: 50 15      BVC $805f        ; → L_805F   ; bit6 clear → tail only
    ; bit6+bit7 set ($C0): explicitly silence all voices, set vol=$0F,
    ; flip state to plain end-of-song ($80) for subsequent frames.
    $804A: A9 00      LDA #$00
    $804C: 8D 04 D4   STA $d404      ;V1_CTRL     ; gate off V1
    $804F: 8D 0B D4   STA $d40b      ;V2_CTRL     ; gate off V2
    $8052: 8D 12 D4   STA $d412      ;V3_CTRL     ; gate off V3
    $8055: A9 0F      LDA #$0f
    $8057: 8D 18 D4   STA $d418      ;VOL         ; max volume (sfx still runs)
    $805A: A9 80      LDA #$80
    $805C: 8D 29 85   STA $8529                     ; song-state = end only
L_805F:
    $805F: 4C B8 83   JMP $83b8        ; → L_83B8   ; jump to sfx tail / RTS
; Per-voice loop entry. X iterates 2 → 1 → 0 (V3 first, V1 last) so V1
; effects can read state set by V2/V3 earlier in the same frame.
L_8062:
    $8062: A2 02      LDX #$02                      ; X = voice index 2 (V3)
    ; Global tick divider: DEC $8526; when it goes negative reload from
    ; $8527 (frames-per-note step). Reload-frames are the note-load
    ; frames; in-between frames just run effects.
    $8064: CE 26 85   DEC $8526
    $8067: 10 06      BPL $806f        ; → L_806F   ; not yet wrapped
    $8069: AD 27 85   LDA $8527
    $806C: 8D 26 85   STA $8526                     ; reload tick divider
L_806F:
    ; Per-voice SID base (0/7/14 = V1/V2/V3) → $84FE (used as Y in STA $D4xx,Y).
    $806F: BD FB 84   LDA $84fb,x                   ; voice base offset
    $8072: 8D FE 84   STA $84fe                     ; remember as Y for SID writes
    $8075: A8         TAY                           ; Y = SID offset
    ; Note-load gate: only on tick-divider reload frame.
    ; If $8526 == $8527 (= reload value), this is the note-load frame.
    ; Else BNE → effects-only path at $8093.
    $8076: AD 26 85   LDA $8526
    $8079: CD 27 85   CMP $8527
    $807C: D0 15      BNE $8093        ; → L_8093   ; effects-only frame
    $807E: BD 91 87   LDA $8791,x   
    $8081: 85 FB      STA $fb       
    $8083: BD 94 87   LDA $8794,x   
    $8086: 85 FC      STA $fc       
    $8088: DE 05 85   DEC $8505,x   
    $808B: 30 09      BMI $8096        ; → L_8096
    $808D: 4C 81 81   JMP $8181        ; → L_8181
; ----- data gap $8090-$8092 (3 bytes) -----

L_8093:
    $8093: 4C A8 81   JMP $81a8        ; → L_81A8
L_8096:
    $8096: BC FF 84   LDY $84ff,x   
    $8099: B1 FB      LDA ($fb),y   
    $809B: C9 FE      CMP #$fe      
    $809D: D0 03      BNE $80a2        ; → L_80A2
    $809F: 4C 13 80   JMP $8013        ; → L_8013
L_80A2:
    $80A2: C9 FF      CMP #$ff      
    $80A4: D0 11      BNE $80b7        ; → L_80B7
    $80A6: A9 00      LDA #$00      
    $80A8: 9D 05 85   STA $8505,x   
    $80AB: 9D FF 84   STA $84ff,x   
    $80AE: 9D 02 85   STA $8502,x   
    $80B1: 4C 96 80   JMP $8096        ; → L_8096
; ----- data gap $80B4-$80B6 (3 bytes) -----

L_80B7:
    $80B7: A8         TAY           
    $80B8: B9 A9 87   LDA $87a9,y   
    $80BB: 85 FD      STA $fd       
    $80BD: B9 C6 87   LDA $87c6,y   
    $80C0: 85 FE      STA $fe       
    $80C2: A9 00      LDA #$00      
    $80C4: 9D 30 85   STA $8530,x   
    $80C7: BC 02 85   LDY $8502,x   
    $80CA: A9 FF      LDA #$ff      
    $80CC: 8D 14 85   STA $8514     
    $80CF: B1 FD      LDA ($fd),y   
    $80D1: 9D 08 85   STA $8508,x   
    $80D4: 8D 15 85   STA $8515     
    $80D7: 29 1F      AND #$1f      
    $80D9: 9D 05 85   STA $8505,x   
    $80DC: 2C 15 85   BIT $8515     
    $80DF: 70 44      BVS $8125        ; → L_8125
    $80E1: FE 02 85   INC $8502,x   
    $80E4: AD 15 85   LDA $8515     
    $80E7: 10 11      BPL $80fa        ; → L_80FA
    $80E9: C8         INY           
    $80EA: B1 FD      LDA ($fd),y   
    $80EC: 10 06      BPL $80f4        ; → L_80F4
    $80EE: 9D 30 85   STA $8530,x   
    $80F1: 4C F7 80   JMP $80f7        ; → L_80F7
L_80F4:
    $80F4: 9D 11 85   STA $8511,x   
L_80F7:
    $80F7: FE 02 85   INC $8502,x   
L_80FA:
    $80FA: C8         INY           
    $80FB: B1 FD      LDA ($fd),y   
    $80FD: 9D 0E 85   STA $850e,x   
    $8100: 0A         ASL a         
    $8101: A8         TAY           
    $8102: AD 38 85   LDA $8538     
    $8105: 10 21      BPL $8128        ; → L_8128
    $8107: B9 3B 84   LDA $843b,y   
    $810A: 8D 16 85   STA $8516     
    $810D: B9 3C 84   LDA $843c,y   
    $8110: AC FE 84   LDY $84fe     
    $8113: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $8116: 9D 2A 85   STA $852a,x   
    $8119: AD 16 85   LDA $8516     
    $811C: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $811F: 9D 2D 85   STA $852d,x   
    $8122: 4C 28 81   JMP $8128        ; → L_8128
L_8125:
    $8125: CE 14 85   DEC $8514     
L_8128:
    $8128: AC FE 84   LDY $84fe     
    $812B: BD 11 85   LDA $8511,x   
    $812E: 8E 17 85   STX $8517     
    $8131: 0A         ASL a         
    $8132: 0A         ASL a         
    $8133: 0A         ASL a         
    $8134: AA         TAX           
    $8135: BD A3 85   LDA $85a3,x   
    $8138: 8D 18 85   STA $8518     
    $813B: AD 38 85   LDA $8538     
    $813E: 10 21      BPL $8161        ; → L_8161
    $8140: BD A3 85   LDA $85a3,x   
    $8143: 2D 14 85   AND $8514     
    $8146: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $8149: BD A1 85   LDA $85a1,x   
    $814C: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $814F: BD A2 85   LDA $85a2,x   
    $8152: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $8155: BD A4 85   LDA $85a4,x   
    $8158: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $815B: BD A5 85   LDA $85a5,x   
    $815E: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_8161:
    $8161: AE 17 85   LDX $8517     
    $8164: AD 18 85   LDA $8518     
    $8167: 9D 0B 85   STA $850b,x   
    $816A: FE 02 85   INC $8502,x   
    $816D: BC 02 85   LDY $8502,x   
    $8170: B1 FD      LDA ($fd),y   
    $8172: C9 FF      CMP #$ff      
    $8174: D0 08      BNE $817e        ; → L_817E
    $8176: A9 00      LDA #$00      
    $8178: 9D 02 85   STA $8502,x   
    $817B: FE FF 84   INC $84ff,x   
L_817E:
    $817E: 4C A2 83   JMP $83a2        ; → L_83A2
L_8181:
    $8181: AD 38 85   LDA $8538     
    $8184: 30 03      BMI $8189        ; → L_8189
    $8186: 4C A2 83   JMP $83a2        ; → L_83A2
L_8189:
    $8189: AC FE 84   LDY $84fe     
    $818C: BD 08 85   LDA $8508,x   
    $818F: 29 20      AND #$20      
    $8191: D0 15      BNE $81a8        ; → L_81A8
    $8193: BD 05 85   LDA $8505,x   
    $8196: D0 10      BNE $81a8        ; → L_81A8
    $8198: BD 0B 85   LDA $850b,x   
    $819B: 29 FE      AND #$fe      
    $819D: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $81A0: A9 00      LDA #$00      
    $81A2: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $81A5: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_81A8:
    $81A8: AD 38 85   LDA $8538     
    $81AB: 30 03      BMI $81b0        ; → L_81B0
    $81AD: 4C A2 83   JMP $83a2        ; → L_83A2
L_81B0:
    $81B0: BD 11 85   LDA $8511,x   
    $81B3: 0A         ASL a         
    $81B4: 0A         ASL a         
    $81B5: 0A         ASL a         
    $81B6: A8         TAY           
    $81B7: 8C 28 85   STY $8528     
    $81BA: B9 A8 85   LDA $85a8,y   
    $81BD: 8D 33 85   STA $8533     
    $81C0: B9 A7 85   LDA $85a7,y   
    $81C3: 8D 1A 85   STA $851a     
    $81C6: B9 A6 85   LDA $85a6,y   
    $81C9: 8D 19 85   STA $8519     
    $81CC: F0 6F      BEQ $823d        ; → L_823D
    $81CE: AD 35 85   LDA $8535     
    $81D1: 29 07      AND #$07      
    $81D3: C9 04      CMP #$04      
    $81D5: 90 02      BCC $81d9        ; → L_81D9
    $81D7: 49 07      EOR #$07      
L_81D9:
    $81D9: 8D 1F 85   STA $851f     
    $81DC: BD 0E 85   LDA $850e,x   
    $81DF: 0A         ASL a         
    $81E0: A8         TAY           
    $81E1: 38         SEC           
    $81E2: B9 3D 84   LDA $843d,y   
    $81E5: F9 3B 84   SBC $843b,y   
    $81E8: 8D 1B 85   STA $851b     
    $81EB: B9 3E 84   LDA $843e,y   
    $81EE: F9 3C 84   SBC $843c,y   
L_81F1:
    $81F1: 4A         LSR a         
    $81F2: 6E 1B 85   ROR $851b     
    $81F5: CE 19 85   DEC $8519     
    $81F8: 10 F7      BPL $81f1        ; → L_81F1
    $81FA: 8D 1C 85   STA $851c     
    $81FD: B9 3B 84   LDA $843b,y   
    $8200: 8D 1D 85   STA $851d     
    $8203: B9 3C 84   LDA $843c,y   
    $8206: 8D 1E 85   STA $851e     
    $8209: BD 08 85   LDA $8508,x   
    $820C: 29 1F      AND #$1f      
    $820E: C9 08      CMP #$08      
    $8210: 90 1C      BCC $822e        ; → L_822E
    $8212: AC 1F 85   LDY $851f     
L_8215:
    $8215: 88         DEY           
    $8216: 30 16      BMI $822e        ; → L_822E
    $8218: 18         CLC           
    $8219: AD 1D 85   LDA $851d     
    $821C: 6D 1B 85   ADC $851b     
    $821F: 8D 1D 85   STA $851d     
    $8222: AD 1E 85   LDA $851e     
    $8225: 6D 1C 85   ADC $851c     
    $8228: 8D 1E 85   STA $851e     
    $822B: 4C 15 82   JMP $8215        ; → L_8215
L_822E:
    $822E: AC FE 84   LDY $84fe     
    $8231: AD 1D 85   LDA $851d     
    $8234: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $8237: AD 1E 85   LDA $851e     
    $823A: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_823D:
    $823D: AD 33 85   LDA $8533     
    $8240: 29 08      AND #$08      
    $8242: F0 17      BEQ $825b        ; → L_825B
    $8244: AC 28 85   LDY $8528     
    $8247: B9 A1 85   LDA $85a1,y   
    $824A: 6D 1A 85   ADC $851a     
    $824D: 09 40      ORA #$40      
    $824F: 99 A1 85   STA $85a1,y   
    $8252: AC FE 84   LDY $84fe     
    $8255: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $8258: 4C C2 82   JMP $82c2        ; → L_82C2
L_825B:
    $825B: AD 1A 85   LDA $851a     
    $825E: F0 62      BEQ $82c2        ; → L_82C2
    $8260: AC 28 85   LDY $8528     
    $8263: 29 1F      AND #$1f      
    $8265: DE 20 85   DEC $8520,x   
    $8268: 10 58      BPL $82c2        ; → L_82C2
    $826A: 9D 20 85   STA $8520,x   
    $826D: AD 1A 85   LDA $851a     
    $8270: 29 E0      AND #$e0      
    $8272: 8D 34 85   STA $8534     
    $8275: BD 23 85   LDA $8523,x   
    $8278: D0 1A      BNE $8294        ; → L_8294
    $827A: AD 34 85   LDA $8534     
    $827D: 18         CLC           
    $827E: 79 A1 85   ADC $85a1,y   
    $8281: 48         PHA           
    $8282: B9 A2 85   LDA $85a2,y   
    $8285: 69 00      ADC #$00      
    $8287: 29 0F      AND #$0f      
    $8289: 48         PHA           
    $828A: C9 0E      CMP #$0e      
    $828C: D0 1D      BNE $82ab        ; → L_82AB
    $828E: FE 23 85   INC $8523,x   
    $8291: 4C AB 82   JMP $82ab        ; → L_82AB
L_8294:
    $8294: 38         SEC           
    $8295: B9 A1 85   LDA $85a1,y   
    $8298: ED 34 85   SBC $8534     
    $829B: 48         PHA           
    $829C: B9 A2 85   LDA $85a2,y   
    $829F: E9 00      SBC #$00      
    $82A1: 29 0F      AND #$0f      
    $82A3: 48         PHA           
    $82A4: C9 08      CMP #$08      
    $82A6: D0 03      BNE $82ab        ; → L_82AB
    $82A8: DE 23 85   DEC $8523,x   
L_82AB:
    $82AB: 8E 17 85   STX $8517     
    $82AE: AE FE 84   LDX $84fe     
    $82B1: 68         PLA           
    $82B2: 99 A2 85   STA $85a2,y   
    $82B5: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $82B8: 68         PLA           
    $82B9: 99 A1 85   STA $85a1,y   
    $82BC: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $82BF: AE 17 85   LDX $8517     
L_82C2:
    $82C2: AC FE 84   LDY $84fe     
    $82C5: BD 30 85   LDA $8530,x   
    $82C8: F0 3F      BEQ $8309        ; → L_8309
    $82CA: 29 7E      AND #$7e      
    $82CC: 8D 17 85   STA $8517     
    $82CF: BD 30 85   LDA $8530,x   
    $82D2: 29 01      AND #$01      
    $82D4: F0 1B      BEQ $82f1        ; → L_82F1
    $82D6: 38         SEC           
    $82D7: BD 2D 85   LDA $852d,x   
    $82DA: ED 17 85   SBC $8517     
    $82DD: 9D 2D 85   STA $852d,x   
    $82E0: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $82E3: BD 2A 85   LDA $852a,x   
    $82E6: E9 00      SBC #$00      
    $82E8: 9D 2A 85   STA $852a,x   
    $82EB: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $82EE: 4C 09 83   JMP $8309        ; → L_8309
L_82F1:
    $82F1: 18         CLC           
    $82F2: BD 2D 85   LDA $852d,x   
    $82F5: 6D 17 85   ADC $8517     
    $82F8: 9D 2D 85   STA $852d,x   
    $82FB: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $82FE: BD 2A 85   LDA $852a,x   
    $8301: 69 00      ADC #$00      
    $8303: 9D 2A 85   STA $852a,x   
    $8306: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_8309:
    $8309: AD 33 85   LDA $8533     
    $830C: 29 01      AND #$01      
    $830E: F0 35      BEQ $8345        ; → L_8345
    $8310: BD 2A 85   LDA $852a,x   
    $8313: F0 30      BEQ $8345        ; → L_8345
    $8315: BD 05 85   LDA $8505,x   
    $8318: F0 2B      BEQ $8345        ; → L_8345
    $831A: BD 08 85   LDA $8508,x   
    $831D: 29 1F      AND #$1f      
    $831F: 38         SEC           
    $8320: E9 01      SBC #$01      
    $8322: DD 05 85   CMP $8505,x   
    $8325: AC FE 84   LDY $84fe     
    $8328: 90 10      BCC $833a        ; → L_833A
    $832A: BD 2A 85   LDA $852a,x   
    $832D: DE 2A 85   DEC $852a,x   
    $8330: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $8333: BD 0B 85   LDA $850b,x   
    $8336: 29 FE      AND #$fe      
    $8338: D0 08      BNE $8342        ; → L_8342
L_833A:
    $833A: BD 2A 85   LDA $852a,x   
    $833D: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $8340: A9 80      LDA #$80      
L_8342:
    $8342: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_8345:
    $8345: AD 33 85   LDA $8533     
    $8348: 29 02      AND #$02      
    $834A: F0 25      BEQ $8371        ; → L_8371
    $834C: BD 08 85   LDA $8508,x   
    $834F: 29 1F      AND #$1f      
    $8351: C9 1F      CMP #$1f      
    $8353: 90 1C      BCC $8371        ; → L_8371
    $8355: BD 05 85   LDA $8505,x   
    $8358: C9 1E      CMP #$1e      
    $835A: B0 15      BCS $8371        ; → L_8371
    $835C: AD 35 85   LDA $8535     
    $835F: 29 01      AND #$01      
    $8361: F0 0E      BEQ $8371        ; → L_8371
    $8363: BD 2A 85   LDA $852a,x   
    $8366: F0 09      BEQ $8371        ; → L_8371
    $8368: DE 2A 85   DEC $852a,x   
    $836B: AC FE 84   LDY $84fe     
    $836E: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_8371:
    $8371: AD 33 85   LDA $8533     
    $8374: 29 04      AND #$04      
    $8376: F0 2A      BEQ $83a2        ; → L_83A2
    $8378: AD 35 85   LDA $8535     
    $837B: 29 01      AND #$01      
    $837D: F0 09      BEQ $8388        ; → L_8388
    $837F: BD 0E 85   LDA $850e,x   
    $8382: 18         CLC           
    $8383: 69 0C      ADC #$0c      
    $8385: 4C 8B 83   JMP $838b        ; → L_838B
L_8388:
    $8388: BD 0E 85   LDA $850e,x   
L_838B:
    $838B: 0A         ASL a         
    $838C: A8         TAY           
    $838D: B9 3B 84   LDA $843b,y   
    $8390: 8D 16 85   STA $8516     
    $8393: B9 3C 84   LDA $843c,y   
    $8396: AC FE 84   LDY $84fe     
    $8399: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $839C: AD 16 85   LDA $8516     
    $839F: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_83A2:
    $83A2: A0 FF      LDY #$ff      
    $83A4: AD 36 85   LDA $8536     
    $83A7: D0 06      BNE $83af        ; → L_83AF
    $83A9: AD 37 85   LDA $8537     
    $83AC: 30 01      BMI $83af        ; → L_83AF
    $83AE: C8         INY           
L_83AF:
    $83AF: 8C 38 85   STY $8538     
    $83B2: CA         DEX           
    $83B3: 30 03      BMI $83b8        ; → L_83B8
    $83B5: 4C 6F 80   JMP $806f        ; → L_806F
L_83B8:
    $83B8: A9 FF      LDA #$ff      
    $83BA: 8D 38 85   STA $8538     
    $83BD: AD 36 85   LDA $8536     
    $83C0: D0 05      BNE $83c7        ; → L_83C7
    $83C2: 2C 37 85   BIT $8537     
    $83C5: 10 01      BPL $83c8        ; → L_83C8
L_83C7:
    $83C7: 60         RTS           
L_83C8:
    $83C8: 50 03      BVC $83cd        ; → L_83CD
    $83CA: 20 41 85   JSR $8541        ; → sub_8541
L_83CD:
    $83CD: CE 3A 85   DEC $853a     
    $83D0: 10 F5      BPL $83c7        ; → L_83C7
    $83D2: AD 40 85   LDA $8540     
    $83D5: 29 0F      AND #$0f      
    $83D7: 8D 3A 85   STA $853a     
    $83DA: AD 39 85   LDA $8539     
    $83DD: CD 3B 85   CMP $853b     
    $83E0: D0 0F      BNE $83f1        ; → L_83F1
    $83E2: A2 00      LDX #$00      
    $83E4: 8E 04 D4   STX $d404      ;V1_CTRL
    $83E7: 8E 0B D4   STX $d40b      ;V2_CTRL
    $83EA: CA         DEX           
    $83EB: 8E 37 85   STX $8537     
    $83EE: 4C C7 83   JMP $83c7        ; → L_83C7
L_83F1:
    $83F1: CE 39 85   DEC $8539     
    $83F4: 0A         ASL a         
    $83F5: A8         TAY           
    $83F6: 2C 40 85   BIT $8540     
    $83F9: 30 20      BMI $841b        ; → L_841B
    $83FB: 70 0C      BVS $8409        ; → L_8409
    $83FD: B9 3B 84   LDA $843b,y   
    $8400: 8D 00 D4   STA $d400      ;V1_FREQ_LO
    $8403: B9 3C 84   LDA $843c,y   
    $8406: 8D 01 D4   STA $d401      ;V1_FREQ_HI
L_8409:
    $8409: 98         TYA           
    $840A: 38         SEC           
    $840B: ED 3C 85   SBC $853c     
    $840E: A8         TAY           
    $840F: B9 3B 84   LDA $843b,y   
    $8412: 8D 07 D4   STA $d407      ;V2_FREQ_LO
    $8415: B9 3C 84   LDA $843c,y   
    $8418: 8D 08 D4   STA $d408      ;V2_FREQ_HI
L_841B:
    $841B: 2C 3D 85   BIT $853d     
    $841E: 10 0B      BPL $842b        ; → L_842B
    $8420: AD 3E 85   LDA $853e     
    $8423: 49 01      EOR #$01      
    $8425: 8D 04 D4   STA $d404      ;V1_CTRL
    $8428: 8D 3E 85   STA $853e     
L_842B:
    $842B: 50 0B      BVC $8438        ; → L_8438
    $842D: AD 3F 85   LDA $853f     
    $8430: 49 01      EOR #$01      
    $8432: 8D 0B D4   STA $d40b      ;V2_CTRL
    $8435: 8D 3F 85   STA $853f     
L_8438:
    $8438: 4C C7 83   JMP $83c7        ; → L_83C7
; ----- data gap $843B-$8540 (262 bytes) -----

sub_8541:
    $8541: A9 00      LDA #$00      
    $8543: 8D 04 D4   STA $d404      ;V1_CTRL
    $8546: 8D 0B D4   STA $d40b      ;V2_CTRL
    $8549: 8D 3A 85   STA $853a     
    $854C: AD 37 85   LDA $8537     
    $854F: 29 0F      AND #$0f      
    $8551: 8D 37 85   STA $8537     
    $8554: 0A         ASL a         
    $8555: 0A         ASL a         
    $8556: 0A         ASL a         
    $8557: 0A         ASL a         
    $8558: A8         TAY           
    $8559: B9 99 86   LDA $8699,y   
    $855C: 8D 40 85   STA $8540     
    $855F: B9 9A 86   LDA $869a,y   
    $8562: 8D 39 85   STA $8539     
    $8565: B9 A8 86   LDA $86a8,y   
    $8568: 8D 3B 85   STA $853b     
    $856B: B9 A1 86   LDA $86a1,y   
    $856E: 8D 3D 85   STA $853d     
    $8571: 29 3F      AND #$3f      
    $8573: 8D 3C 85   STA $853c     
    $8576: B9 9E 86   LDA $869e,y   
    $8579: 8D 3E 85   STA $853e     
    $857C: B9 A5 86   LDA $86a5,y   
    $857F: 8D 3F 85   STA $853f     
    $8582: A2 00      LDX #$00      
L_8584:
    $8584: B9 9A 86   LDA $869a,y   
    $8587: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $858A: C8         INY           
    $858B: E8         INX           
    $858C: E0 0E      CPX #$0e      
    $858E: D0 F4      BNE $8584        ; → L_8584
    $8590: AD 40 85   LDA $8540     
    $8593: 29 30      AND #$30      
    $8595: A0 EE      LDY #$ee      
    $8597: C9 20      CMP #$20      
    $8599: F0 02      BEQ $859d        ; → L_859D
    $859B: A0 CE      LDY #$ce      
L_859D:
    $859D: 8C F1 83   STY $83f1     
    $85A0: 60         RTS           
; ----- data gap $85A1-$8C52 (1714 bytes) -----

L_8C53:
    $8C53: A0 00      LDY #$00      
    $8C55: 0A         ASL a         
    $8C56: 8D 17 85   STA $8517     
    $8C59: 0A         ASL a         
    $8C5A: 18         CLC           
    $8C5B: 6D 17 85   ADC $8517     
    $8C5E: AA         TAX           
L_8C5F:
    $8C5F: BD 97 87   LDA $8797,x   
    $8C62: 99 91 87   STA $8791,y   
    $8C65: E8         INX           
    $8C66: C8         INY           
    $8C67: C0 06      CPY #$06      
    $8C69: D0 F4      BNE $8c5f        ; → L_8C5F
    $8C6B: A9 40      LDA #$40      
    $8C6D: 8D 29 85   STA $8529     
    $8C70: 60         RTS           
L_8C71:
    $8C71: A9 C0      LDA #$c0      
    $8C73: 8D 29 85   STA $8529     
    $8C76: 60         RTS           
; ----- data gap $8C77-$8C84 (14 bytes) -----

L_8C85:
    $8C85: AE 36 85   LDX $8536     
    $8C88: F0 04      BEQ $8c8e        ; → L_8C8E
    $8C8A: 8E 37 85   STX $8537     
    $8C8D: 60         RTS           
L_8C8E:
    $8C8E: 09 40      ORA #$40      
    $8C90: 8D 37 85   STA $8537     
    $8C93: 60         RTS           
; ----- data gap $8C94-$8CE1 (78 bytes) -----

; sub_8CE2: subtune dispatcher called from init. Routes A=subtune to:
;   <3   → music tracker init (JMP $8010 → $8C53: copy orderlist ptrs)
;   3,4  → digi sample init   (JSR $8CF1: silence SID + start digi loop)
;   5+   → sfx queue          (JSR sub_801F + JMP $8013 → mark end-of-music)
sub_8CE2:
    $8CE2: 8D FF 8F   STA $8fff                     ; remember subtune for play to read
    $8CE5: A2 0F      LDX #$0f
    $8CE7: 8E 18 D4   STX $d418      ;VOL          ; full volume
    $8CEA: C9 03      CMP #$03
    $8CEC: B0 25      BCS $8d13        ; → L_8D13   ; subtune >= 3 → sfx/digi
    $8CEE: 4C 10 80   JMP $8010        ; → L_8010   ; music subtune (trampoline → $8C53)
; sub_CF1: digi-only init for subtunes 3,4.
;   A = subtune (3 or 4) - 2 → $97 = sample number (1 or 2).
;   Clears all SID voice regs ($D400-$D417), then calls sub_8D40 which
;   bank-switches to $36 and runs the digi sample player at $8E00.
L_8CF1:
    $8CF1: 38         SEC
    $8CF2: E9 02      SBC #$02                      ; A := subtune - 2 (1-based sample id)
    $8CF4: 85 97      STA $97                       ; $97 = sample # for $8E00
    $8CF6: A2 17      LDX #$17                      ; 24 SID regs to zero
L_8CF8:
    $8CF8: A9 00      LDA #$00
    $8CFA: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X ; clear D400-D417 (silence)
    $8CFD: CA         DEX
    $8CFE: 10 F8      BPL $8cf8        ; → L_8CF8
    $8D00: 20 40 8D   JSR $8d40        ; → sub_8D40 ; bank-switch + play digi
    $8D03: 60         RTS
; sub_8D04: per-frame dispatcher called from play.
;   subtune <3   → JMP $8022 (music tracker tick)
;   subtune 3,4  → CMP #$05 fails → silently RTS (digi already running)
;   subtune >=5  → JMP $8022 (sfx ride-along on tracker scaffolding)
sub_8D04:
    $8D04: AD FF 8F   LDA $8fff                     ; subtune saved by sub_8CE2
    $8D07: C9 03      CMP #$03
    $8D09: B0 03      BCS $8d0e        ; → L_8D0E   ; >=3 → check sfx/digi
L_8D0B:
    $8D0B: 4C 22 80   JMP $8022        ; → L_8022   ; music tracker tick
L_8D0E:
    $8D0E: C9 05      CMP #$05
    $8D10: B0 F9      BCS $8d0b        ; → L_8D0B   ; >=5 → sfx via $8022
    $8D12: 60         RTS                          ; subtune 3,4 → no per-frame work
; Subtune dispatch tail from sub_8CE2 (A=subtune, BCS landed here for A>=3).
L_8D13:
    $8D13: C9 05      CMP #$05
    $8D15: B0 03      BCS $8d1a        ; → L_8D1A   ; >=5 → sfx
    $8D17: 4C F1 8C   JMP $8cf1        ; → L_8CF1   ; A=3 or 4 → digi
L_8D1A:
    $8D1A: 38         SEC
    $8D1B: E9 05      SBC #$05                      ; A := sfx slot (0-based)
    $8D1D: 20 1F 80   JSR $801f        ; → sub_801F ; queue sfx in $8536/$8537
    $8D20: 4C 13 80   JMP $8013        ; → L_8013   ; flag music as ended (silence chans)
; ----- data gap $8D23-$8D3F (29 bytes) -----

sub_8D40:
    $8D40: A9 36      LDA #$36      
    $8D42: 85 01      STA $01       
    $8D44: 20 00 8E   JSR $8e00        ; → sub_8E00
    $8D47: A9 37      LDA #$37      
    $8D49: 85 01      STA $01       
    $8D4B: 60         RTS           
; ----- data gap $8D4C-$8D7F (52 bytes) -----

; ======= init: =======
; RSID entry. A = subtune number on entry (sidplayfp pushes start-1 as A).
; Sets up the raster IRQ at line $80 → $8DB3, then dispatches subtune.
init:
    $8D80: 78         SEI                            ; disable IRQs while reprogramming vectors
    $8D81: 48         PHA                            ; save subtune for sub_8CE2 below
    ; Zero ZP $F0..$FF (digi sample scratch area).
    $8D82: A2 0F      LDX #$0f
    $8D84: A9 00      LDA #$00
L_8D86:
    $8D86: 95 F0      STA $f0,x
    $8D88: CA         DEX
    $8D89: 10 FB      BPL $8d86        ; → L_8D86
    ; Install IRQ vector $0314/5 = $8DB3 (this file's play). Because the
    ; PSID header says play=$0000, the RSID convention requires init to
    ; wire up the IRQ itself; sidplayfp reads $0314/5 to find play.
    $8D8B: A9 B3      LDA #$b3
    $8D8D: 8D 14 03   STA $0314      ;IRQVEC_LO  → play low byte
    $8D90: A9 8D      LDA #$8d
    $8D92: 8D 15 03   STA $0315      ;IRQVEC_HI  → play high byte
    ; Disable all CIA1 IRQ sources. VIC raster IRQ is the only driver.
    $8D95: A9 7F      LDA #$7f
    $8D97: 8D 0D DC   STA $dc0d      ;CIA1_ICR    = $7F clears mask
    ; Enable VIC raster IRQ (bit 0 of IMR) and bit 7 (just-set artifact).
    $8D9A: A9 81      LDA #$81
    $8D9C: 8D 1A D0   STA $d01a      ;VIC_IMR     = enable raster
    ; D011 = $1B: default text-mode display, raster MSB = 0 → line $0080.
    $8D9F: A9 1B      LDA #$1b
    $8DA1: 8D 11 D0   STA $d011                     ;VIC_CTRL1
    $8DA4: A9 80      LDA #$80
    $8DA6: 8D 12 D0   STA $d012      ;VIC_RASTER  = trigger on raster $80
    ; Restore subtune number and dispatch.
    $8DA9: 68         PLA
    $8DAA: 20 E2 8C   JSR $8ce2        ; → sub_8CE2 ; route to music / digi / sfx
    $8DAD: A9 37      LDA #$37
    $8DAF: 85 01      STA $01                       ; CPU port: RAM+I/O+KERNAL banked in
    $8DB1: 58         CLI                           ; let IRQs through
    $8DB2: 60         RTS
; ======= play: =======
; Raster-IRQ entry installed by init at $0314/5. sidplayfp triggers this
; at VIC raster line $80 (~once per frame, PAL ~50Hz).
play:
    $8DB3: 20 04 8D   JSR $8d04        ; → sub_8D04 ; tick the active engine
    $8DB6: A9 37      LDA #$37
    $8DB8: 85 01      STA $01                       ; digi may have set $01=$36 → restore I/O
    $8DBA: EE 19 D0   INC $d019      ;VIC_IRR     ; acknowledge VIC raster IRQ
    $8DBD: 4C 7E EA   JMP $ea7e                    ; KERNAL IRQ exit (PLA;TAY;PLA;TAX;PLA;RTI)
; ----- data gap $8DC0-$8DFF (64 bytes) -----

; -----------------------------------------------------------------------------
; THE DIGI SAMPLE PLAYER ($8E00)
; -----------------------------------------------------------------------------
; Hubbard's signature trick on Last V8: 4-bit (effectively 1-bit pulse-
; modulated) PCM samples piped through V1 via the SID test bit. Called
; from sub_8D40 with $97 = sample index, $01 = $36 (RAM under I/O so the
; sample table at $9000-$BFFF can be read directly).
;
; This is a TIGHT BUSY-LOOP — it runs to completion (~hundreds of msec)
; inside ONE play-IRQ. The CIA1 IRQ is disabled by init for exactly this
; reason: nothing else gets to interrupt the digi.
sub_8E00:
    $8E00: 4C 06 8E   JMP $8e06        ; → L_8E06   ; trampoline (skip 3 spare bytes)
; ----- data gap $8E03-$8E05 (3 bytes) -----

; Digi entry. Save ZP $F7-$FA (caller's scratch) onto stack.
L_8E06:
    $8E06: A5 F7      LDA $f7
    $8E08: 48         PHA
    $8E09: A5 F8      LDA $f8
    $8E0B: 48         PHA
    $8E0C: A5 F9      LDA $f9
    $8E0E: 48         PHA
    $8E0F: A5 FA      LDA $fa
    $8E11: 48         PHA
    $8E12: EA         NOP           
    $8E13: A9 3E      LDA #$3e      
    $8E15: 25 01      AND $01       
    $8E17: A5 01      LDA $01       
    $8E19: AD 11 D0   LDA $d011     
    $8E1C: 8D 09 8F   STA $8f09     
    $8E1F: A2 00      LDX #$00      
    $8E21: AC 03 91   LDY $9103     
    $8E24: C0 00      CPY #$00      
    $8E26: D0 06      BNE $8e2e        ; → L_8E2E
    $8E28: 00         BRK           
; ----- data gap $8E29-$8E2D (5 bytes) -----

L_8E2E:
    $8E2E: BD 0B 91   LDA $910b,x   
    $8E31: C5 97      CMP $97       
    $8E33: F0 0A      BEQ $8e3f        ; → L_8E3F
    $8E35: E8         INX           
    $8E36: 88         DEY           
    $8E37: D0 F5      BNE $8e2e        ; → L_8E2E
    $8E39: 20 09 8F   JSR $8f09        ; → sub_8F09
    $8E3C: 4C EA 8E   JMP $8eea        ; → L_8EEA
L_8E3F:
    $8E3F: AD 0A 91   LDA $910a     
    $8E42: 8D AC 8E   STA $8eac     
    $8E45: A5 97      LDA $97       
    $8E47: 0A         ASL a         
    $8E48: 0A         ASL a         
    $8E49: AA         TAX           
    $8E4A: BD 00 90   LDA $9000,x   
    $8E4D: 85 FB      STA $fb       
    $8E4F: BD 01 90   LDA $9001,x   
    $8E52: 85 FC      STA $fc       
    $8E54: BD 02 90   LDA $9002,x   
    $8E57: 85 F7      STA $f7       
    $8E59: BD 03 90   LDA $9003,x   
    $8E5C: 85 F8      STA $f8       
    $8E5E: A9 FF      LDA #$ff      
    $8E60: 8D 02 D4   STA $d402      ;V1_PW_LO
    $8E63: 8D 03 D4   STA $d403      ;V1_PW_HI
    $8E66: 8D 04 DD   STA $dd04     
    $8E69: 8D 05 DD   STA $dd05     
    $8E6C: A0 00      LDY #$00      
    $8E6E: A9 F0      LDA #$f0      
    $8E70: 8D 06 D4   STA $d406      ;V1_SR
    $8E73: AD 08 91   LDA $9108     
    $8E76: D0 05      BNE $8e7d        ; → L_8E7D
    $8E78: A9 00      LDA #$00      
    $8E7A: AD 11 D0   LDA $d011     
L_8E7D:
    $8E7D: A9 11      LDA #$11      
    $8E7F: 8D 0E DD   STA $dd0e      ;CIA2_CRA
    $8E82: EA         NOP           
    $8E83: EA         NOP           
    $8E84: EA         NOP           
    $8E85: EA         NOP           
    $8E86: EA         NOP           
    $8E87: EA         NOP           
    $8E88: 4C CF 8E   JMP $8ecf        ; → L_8ECF
L_8E8B:
    $8E8B: E6 FB      INC $fb       
    $8E8D: D0 02      BNE $8e91        ; → L_8E91
    $8E8F: E6 FC      INC $fc       
L_8E91:
    $8E91: A6 FC      LDX $fc       
    $8E93: E4 F8      CPX $f8       
    $8E95: 90 09      BCC $8ea0        ; → L_8EA0
    $8E97: A6 FB      LDX $fb       
    $8E99: E4 F7      CPX $f7       
    $8E9B: 90 03      BCC $8ea0        ; → L_8EA0
    $8E9D: 4C EA 8E   JMP $8eea        ; → L_8EEA
L_8EA0:
    $8EA0: A9 08      LDA #$08      
    $8EA2: 85 96      STA $96       
    $8EA4: B1 FB      LDA ($fb),y   
    $8EA6: 85 FE      STA $fe       
L_8EA8:
    $8EA8: AD 04 DD   LDA $dd04     
    $8EAB: C9 B1      CMP #$b1      
    $8EAD: B0 F9      BCS $8ea8        ; → L_8EA8
    $8EAF: A9 11      LDA #$11      
    $8EB1: 8D 0E DD   STA $dd0e      ;CIA2_CRA
    $8EB4: 06 FE      ASL $fe       
    $8EB6: 90 04      BCC $8ebc        ; → L_8EBC
    $8EB8: A9 49      LDA #$49      
    $8EBA: D0 02      BNE $8ebe        ; → L_8EBE
L_8EBC:
    $8EBC: A9 41      LDA #$41      
L_8EBE:
    $8EBE: 8D 04 D4   STA $d404      ;V1_CTRL
    $8EC1: C6 96      DEC $96       
    $8EC3: D0 E3      BNE $8ea8        ; → L_8EA8
    $8EC5: C6 F9      DEC $f9       
L_8EC7:
    $8EC7: D0 C2      BNE $8e8b        ; → L_8E8B
    $8EC9: E6 FB      INC $fb       
    $8ECB: D0 02      BNE $8ecf        ; → L_8ECF
    $8ECD: E6 FC      INC $fc       
L_8ECF:
    $8ECF: B1 FB      LDA ($fb),y   
    $8ED1: C9 10      CMP #$10      
L_8ED3:
    $8ED3: 90 02      BCC $8ed7        ; → L_8ED7
    $8ED5: A9 0F      LDA #$0f      
L_8ED7:
    $8ED7: 38         SEC           
    $8ED8: E5 FD      SBC $fd       
    $8EDA: 30 02      BMI $8ede        ; → L_8EDE
    $8EDC: D0 02      BNE $8ee0        ; → L_8EE0
L_8EDE:
    $8EDE: A9 01      LDA #$01      
L_8EE0:
    $8EE0: 8D 18 D4   STA $d418      ;VOL
    $8EE3: A9 10      LDA #$10      
    $8EE5: 85 F9      STA $f9       
    $8EE7: 4C 8B 8E   JMP $8e8b        ; → L_8E8B
L_8EEA:
    $8EEA: A9 00      LDA #$00      
    $8EEC: 8D 18 D4   STA $d418      ;VOL
    $8EEF: AD 09 8F   LDA $8f09     
    $8EF2: AD 11 D0   LDA $d011     
    $8EF5: A9 03      LDA #$03      
    $8EF7: 05 01      ORA $01       
    $8EF9: A5 01      LDA $01       
    $8EFB: 68         PLA           
    $8EFC: 85 FA      STA $fa       
    $8EFE: 68         PLA           
    $8EFF: 85 F9      STA $f9       
    $8F01: 68         PLA           
    $8F02: 85 F8      STA $f8       
    $8F04: 68         PLA           
    $8F05: 85 F7      STA $f7       
    $8F07: EA         NOP           
    $8F08: 60         RTS           
sub_8F09:
    $8F09: 3F 4A 4C   ???           
    $8F0C: D0 C5      BNE $8ed3        ; → L_8ED3
    $8F0E: C9 3B      CMP #$3b      
    $8F10: D0 18      BNE $8f2a        ; → L_8F2A
    $8F12: 20 75 C9   JSR $c975     
    $8F15: B0 B0      BCS $8ec7        ; → L_8EC7
    $8F17: 20 C8 C9   JSR $c9c8     
    $8F1A: 20 00 CA   JSR $ca00     
    $8F1D: 8D 0B 02   STA $020b     
    $8F20: 00         BRK           
; ----- data gap $8F21-$8F29 (9 bytes) -----

L_8F2A:
    $8F2A: 00         BRK           
; ----- data gap $8F2B-$B5D1 (9895 bytes) -----

