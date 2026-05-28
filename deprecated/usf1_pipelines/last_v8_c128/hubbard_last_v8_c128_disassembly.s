; ============================================================================
; Rob Hubbard - The Last V8 (C128 version) (1985 MAD/Mastertronic)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/Hubbard_Rob/Last_V8_C128_version.sid
; Format: RSID v2  (NOT PSID — needs real C64 environment: KERNAL IRQ vector,
;                  RAM/ROM banking via $01, CIA timers)
; Load:   $4800   Init: $7F40   Play: $0000 (RSID — play is IRQ-driven)
; PSID:   18 subtune(s), default subtune 1
; Binary: $4800-$8C93 (17556 bytes)
;
; Reseed:
;   PYTHONPATH=tools/py65_lib python3 tools/seed_disassembly.py \
;       hvsc84/MUSICIANS/H/Hubbard_Rob/Last_V8_C128_version.sid \
;       --entry 0x7F73 --entry 0x7EB0 --virt 0x7B40:0x400:0xC000
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ---------------
;
; This SID bundles TWO engines under one PSID, dispatched per-subtune:
;
;   subtune 0-2   tracker music driver       (init→$8C53, play→$8022)
;   subtune 3-5   one-shot SAMPLE player     (init→relocator→$C000, IRQ noop)
;   subtune 6-17  sound-effect dispatcher    (init→$8C85+$8C71, play→$8022)
;
; The sample player at $C000 is interesting: its source bytes live at
; $7B40-$7F3F in the binary and get COPIED to $C000-$C3FF at init time by
; the relocator at $7E91. The "VIRTUAL" section at the bottom of this file
; is that block disassembled as if at $C000 (its runtime location).
;
; init ($7F40): every-frame setup. SEI; zero $F0-$FF; install IRQ at
; $0314/$0315 = $7F73; CIA2 IRQ off ($DC0D=$7F); VIC raster IRQ on raster
; line $80 ($D01A=$81, $D012=$80, $D011=$1B). Then JSR $7F80 → per-subtune
; init via $7E80. STA $01=$37 (default I/O banking) and CLI; RTS.
;
; $7F73 (IRQ handler, called every raster $80): JSR $7EB0 (the music tick),
; then $01=$37, INC $D019 (ack VIC IRQ), JMP $EA7E (KERNAL IRQ exit).
;
; $7EB0 (per-frame dispatch on $7E7F = current subtune):
;   < 3        → JMP $8022   (music play body)
;   3..5       → RTS         (one-shot samples need no per-frame work)
;   >= 6       → JMP $8022   (sound effects also drive the music player)
;
; $7E80 (init dispatch, A = subtune 0-indexed):
;   STA $7E7F                ; remember subtune for IRQ tick
;   < 3        → JMP $8010 → JMP $8C53   (music init: copy 6 bytes of
;                                          orderlist pointers per subtune)
;   3..5       → JMP $7E8A → relocator $7B40-$7F3F → $C000-$C3FF, then
;                JSR $C000 to play the sample one-shot (blocking call).
;   >= 6       → JSR $801F → JMP $8C85 (sets $8537) then
;                JMP $8013 → JMP $8C71 (sets $8529 = $C0).
;
; $7F80 (init helper): swap to RAM-under-I/O ($01=$36) so the relocator can
; touch ROM-shadowed pages, JSR $7E80, write volume $0F to $D418, restore
; $01=$37. (Hubbard's banking trick — copies must work even with KERNAL/BASIC
; banked in.)
;
; MUSIC DRIVER ($8022..$83B8)
; ---------------------------
;
; The frame body that the IRQ enters at $8022. Iterates X = 2..0 over the
; three voices, advancing per-voice state and writing $D400-$D418.
;
; Per-voice state arrays live in the $84xx-$85xx region and use voice index
; X (0..2) as the offset:
;   $84FB,X  current orderlist pointer lo
;   $84FE    cached voice base ($D400 + 7*X)    [scratch]
;   $84FF,X  current pattern position
;   $8502,X  inner position within pattern row
;   $8505,X  note-hold counter
;   $8508,X  current note byte (raw)
;   $850B,X  current control byte (waveform+gate, for re-trigger)
;   $850E,X  current pitch index (into freq table)
;   $8511,X  current instrument id
;   $8520,X  pulsewidth phase
;   $8523,X  pulsework direction flag
;   $852A,X  current freq hi (running 16-bit acc with slide)
;   $852D,X  current freq lo (running)
;   $8530,X  arpeggio/portamento mode bits
;
; Shared globals:
;   $8514       waveform "test bit" tracker
;   $8517,$8518 X/A scratch save across reentry
;   $8526,$8527 frame counter / tempo divisor
;   $8528       cached "8 * instrument id"  (instrument record offset)
;   $8529       sub-state flags (bit 6 = first frame, bit 7 = end-of-tune)
;   $8533       fx-flag mirror from current instrument
;   $8534       arp pulsewidth delta
;   $8535       global frame counter (LSB used as arp phase)
;   $8536/$8537 sound-effect channel state (skipped here)
;   $8538       "music live" flag (FF = play active, 00 = SFX overrides V1/V2)
;   $853A-$853F SFX state on V1+V2 (the $8541 sub-driver below)
;
; Static tables (in the $843B..$87CC region):
;   $843B   FREQ_TABLE — 96 semitones, 2-byte LE entries (lo,hi). First entry
;           is $0116, matching Action Biker's table. Same Hubbard layout.
;   $85A1   INSTRUMENT_TABLE — 8-byte records; offsets:
;             0 pulse_lo  1 pulse_hi  2 ctrl  3 AD  4 SR  5 ?  6 ?  7 fx_flags
;   $8699   SFX_TABLE — 16-byte records keyed by ($8537 & $0F) << 4; used by
;           sub_8541 to drive ring-mod / vibrato sound effects on V1+V2.
;   $8791   ORDERLIST POINTERS — 18 records × ? bytes (six pointers per
;           music subtune copied to $84FB,X by $8C53).
;   $87A9/$87C6 PATTERN_POINTER_LO/HI — pattern table base for ($8508,X).
;
; The pattern reader at $80B7..$817E is a fairly standard Hubbard layout:
;   row[0]      note byte (high bits select instrument / FX, low 5 bits =
;               pitch index into $843B); $FF = step orderlist, $FE = end-of
;               -song (jumps to $8013).
;   row[1] optional FX byte: bit-7 set → "arpeggio table" pointer; bit-7
;          clear → fine PW delta in $8511,X.
;   row[N] note-length byte ($8502,X = position within current row).
;
; The pitch / vibrato / slide / arpeggio modulators at $8128..$83A2 follow
; bits of $8533 (fx flag mirror): bit 0 = portamento, bit 1 = note-cut on
; release, bit 2 = arpeggio-from-table, bit 3 = PWM.
;
; SFX SUB-DRIVER ($8541..$859F) — invoked from $83CA via JSR $8541.
;   16-byte SFX program at $8699 + (($8537 & $0F) << 4):
;     +$00 length / control          → $853a (counter), bits 4-5 = waveform
;     +$01 freq table base index     → $8539 (decremented per tick)
;     +$05 v2 detune offset          → $853c
;     +$07 freq end                  → $853b (stop condition)
;     +$08 v1 waveform-toggle phase  → $853d / $853e
;     +$0F v2 waveform-toggle phase  → $853f
;   Writes $D400,X (X=0..13) on entry: blasts the first 14 bytes of the SFX
;   row directly into $D400-$D40D as initial register state, then per-frame
;   sweeps freq/control from $843B + ($8539 << 1) for V1 and V2 (with
;   $853c semitone offset between them).
;
; ONE-SHOT SAMPLE PLAYER (at $C000 after relocation)
; --------------------------------------------------
;
; Subtunes 3-5 are digital samples — single 1-bit waveform-toggle blocks
; that Hubbard popularised in Spy Hunter / Crazy Comets. JSR $C000 BLOCKS
; until the sample is fully clocked out, then returns. The IRQ tick is a
; no-op while this runs (and we're SEI'd inside anyway during PHA/PLA).
;
;   $C000  jump table (3 bytes per entry, ours just JMP $C006)
;   $C006  save $F7-$FA on stack
;   $C012  spin-toggle wait for raster, save $D011
;   $C021  scan $C30B,X table for record matching subtune in $97; on match,
;          load 4-byte (start_lo, start_hi, end_lo, end_hi) record from
;          $C200,X (X = subtune * 4).
;   $C05E  reset PW + V1 SR ($F0 = release $0 / sustain $F).
;   $C0A8  inner sample loop (uses CIA2 Timer A at $DD04 for cycle-precise
;          1-bit playback by toggling $D404 between $41 (pulse+gate) and
;          $49 (pulse+gate+ringmod)).
;   $C0EA  exit: restore zero page and RTS.
;
; The relocated bytes live in the binary at $7B40-$7F3F. Because the
; relocator runs from RAM-under-I/O ($01=$36), the destination $C000-$C3FF
; in the C64 is real RAM (no BASIC ROM there at $01=$37 anyway). On the
; C128 the same area is RAM Bank 0, hence "C128 version" — the player
; tolerates either machine.
;
; SAMPLE DATA: $4800-$7B3F (12544 bytes). The 4-byte records at $C200 +
; (subtune-3)*4 hold absolute load-address spans into this region.
;
; ============================================================================

; ----- data gap $4800-$7E7F (13952 bytes) -----

; Init dispatcher. A = subtune (0-indexed, came from PHA in init).
; Routes 0-2 → music init, 3-5 → relocator + sample, 6+ → SFX init.
sub_7E80:
    $7E80: 8D 7F 7E   STA $7e7f      ; remember subtune for IRQ tick dispatch
    $7E83: C9 03      CMP #$03
    $7E85: B0 38      BCS $7ebf        ; → L_7EBF   ; subtune >= 3 → relocator path
    $7E87: 4C 10 80   JMP $8010        ; → L_8010   ; 0-2: JMP → JMP $8C53 (music)
; Sample-player relocator. A = subtune-2 (because we entered here on 3-5).
; Copies $7B40-$7F3F → $C000-$C3FF (four 256-byte pages, four LDA/STA
; pairs interleaved in the loop body), then JSRs the relocated player.
; $97 holds the sample selector for the player ($C021 uses it).
L_7E8A:
    $7E8A: 38         SEC
    $7E8B: E9 02      SBC #$02       ; A = (subtune-2) ∈ {1,2,3}; stored as $97
    $7E8D: 85 97      STA $97        ; sample id (1-3) passed to sub_C000
    $7E8F: A2 00      LDX #$00
L_7E91:
    $7E91: BD 40 7B   LDA $7b40,x    ; page 1 of 4 (Hubbard's "4-up loop")
    $7E94: 9D 00 C0   STA $c000,x
    $7E97: BD 40 7C   LDA $7c40,x    ; page 2
    $7E9A: 9D 00 C1   STA $c100,x
    $7E9D: BD 40 7D   LDA $7d40,x    ; page 3
    $7EA0: 9D 00 C2   STA $c200,x
    $7EA3: BD 40 7E   LDA $7e40,x    ; page 4 — last byte copied is at $7F3F
    $7EA6: 9D 00 C3   STA $c300,x
    $7EA9: E8         INX
    $7EAA: D0 E5      BNE $7e91        ; → L_7E91  ; 256 iterations
    $7EAC: 20 00 C0   JSR $c000        ; → sub_C000 ; blocking sample playback
    $7EAF: 60         RTS
; Per-IRQ dispatch (called from the $7F73 raster IRQ).
;   subtune < 3      → JMP $8022  (music play body)
;   subtune 3..5     → RTS         (sample one-shot is blocking; no tick)
;   subtune >= 6     → JMP $8022  (SFX still drives the music player)
sub_7EB0:
    $7EB0: AD 7F 7E   LDA $7e7f
    $7EB3: C9 03      CMP #$03
    $7EB5: B0 03      BCS $7eba        ; → L_7EBA
L_7EB7:
    $7EB7: 4C 22 80   JMP $8022        ; → L_8022   ; music tick
L_7EBA:
    $7EBA: C9 06      CMP #$06
    $7EBC: B0 F9      BCS $7eb7        ; → L_7EB7   ; SFX subtune: still tick
    $7EBE: 60         RTS                           ; sample subtune: no tick
L_7EBF:
    $7EBF: C9 06      CMP #$06      
    $7EC1: B0 03      BCS $7ec6        ; → L_7EC6
    $7EC3: 4C 8A 7E   JMP $7e8a        ; → L_7E8A
L_7EC6:
    $7EC6: 38         SEC           
    $7EC7: E9 06      SBC #$06      
    $7EC9: 20 1F 80   JSR $801f        ; → sub_801F
    $7ECC: 4C 13 80   JMP $8013        ; → L_8013
; ----- data gap $7ECF-$7F3F (113 bytes) -----

; ======= init: =======
init:
    $7F40: 78         SEI           
    $7F41: 48         PHA           
    $7F42: A2 0F      LDX #$0f      
    $7F44: A9 00      LDA #$00      
L_7F46:
    $7F46: 95 F0      STA $f0,x     
    $7F48: CA         DEX           
    $7F49: 10 FB      BPL $7f46        ; → L_7F46
    $7F4B: A9 73      LDA #$73      
    $7F4D: 8D 14 03   STA $0314     
    $7F50: A9 7F      LDA #$7f      
    $7F52: 8D 15 03   STA $0315     
    $7F55: A9 7F      LDA #$7f      
    $7F57: 8D 0D DC   STA $dc0d     
    $7F5A: A9 81      LDA #$81      
    $7F5C: 8D 1A D0   STA $d01a     
    $7F5F: A9 80      LDA #$80      
    $7F61: 8D 12 D0   STA $d012     
    $7F64: A9 1B      LDA #$1b      
    $7F66: 8D 11 D0   STA $d011     
    $7F69: 68         PLA           
    $7F6A: 20 80 7F   JSR $7f80        ; → sub_7F80
    $7F6D: A9 37      LDA #$37      
    $7F6F: 85 01      STA $01       
    $7F71: 58         CLI           
    $7F72: 60         RTS           
; ======= IRQ handler =======
; Installed at $0314/$0315 by init. Called every raster compare on line $80.
sub_7F73:
    $7F73: 20 B0 7E   JSR $7eb0        ; → sub_7EB0  ; music tick (or noop)
    $7F76: A9 37      LDA #$37
    $7F78: 85 01      STA $01           ; restore default banking
    $7F7A: EE 19 D0   INC $d019         ; ack VIC IRQ (any write clears flag)
    $7F7D: 4C 7E EA   JMP $ea7e         ; KERNAL IRQ exit (restore regs, RTI)
; init helper: swap to RAM-under-I/O so the relocator can read the source
; bytes (in case they shadow KERNAL ROM at $E000-$FFFF, though here they
; sit at $7B40-$7F3F so banking is just defensive). Then init the chosen
; subtune and reset SID master volume.
sub_7F80:
    $7F80: A2 36      LDX #$36
    $7F82: 86 01      STX $01           ; $01=$36 — KERNAL out, BASIC out, I/O in
    $7F84: 20 80 7E   JSR $7e80        ; → sub_7E80  ; subtune init / sample play
    $7F87: A2 0F      LDX #$0f
    $7F89: 8E 18 D4   STX $d418      ;VOL ; volume = $0F (max, no filter)
    $7F8C: A2 37      LDX #$37
    $7F8E: 86 01      STX $01           ; $01=$37 — restore default banking
    $7F90: 60         RTS
; ----- data gap $7F91-$800F (127 bytes) -----

L_8010:
    $8010: 4C 53 8C   JMP $8c53        ; → L_8C53
L_8013:
    $8013: 4C 71 8C   JMP $8c71        ; → L_8C71
; ----- data gap $8016-$801E (9 bytes) -----

sub_801F:
    $801F: 4C 85 8C   JMP $8c85        ; → L_8C85
; ======= music tick (per-IRQ entry from $7EB7) =======
; $8529 holds state flags:
;   bit 7 (N) set → END-OF-TUNE (run silencer + JMP $83B8 idle)
;   bit 6 (V) set → FIRST FRAME (clear voice state and arm)
;   else         → normal per-frame body at $8062
; $8535 is the global frame counter (LSB used as arp phase modulo 8).
L_8022:
    $8022: EE 35 85   INC $8535         ; global frame counter ++
    $8025: 2C 29 85   BIT $8529         ; N = end-of-tune, V = first-frame
    $8028: 30 1E      BMI $8048        ; → L_8048   ; end-of-tune path
    $802A: 50 36      BVC $8062        ; → L_8062   ; normal path
    $802C: A9 00      LDA #$00      
    $802E: 8D 35 85   STA $8535     
    $8031: A2 02      LDX #$02      
L_8033:
    $8033: 9D FF 84   STA $84ff,x   
    $8036: 9D 02 85   STA $8502,x   
    $8039: 9D 05 85   STA $8505,x   
    $803C: 9D 0E 85   STA $850e,x   
    $803F: CA         DEX           
    $8040: 10 F1      BPL $8033        ; → L_8033
    $8042: 8D 29 85   STA $8529     
    $8045: 4C 62 80   JMP $8062        ; → L_8062
L_8048:
    $8048: 50 15      BVC $805f        ; → L_805F
    $804A: A9 00      LDA #$00      
    $804C: 8D 04 D4   STA $d404      ;V1_CTRL
    $804F: 8D 0B D4   STA $d40b      ;V2_CTRL
    $8052: 8D 12 D4   STA $d412      ;V3_CTRL
    $8055: A9 0F      LDA #$0f      
    $8057: 8D 18 D4   STA $d418      ;VOL
    $805A: A9 80      LDA #$80      
    $805C: 8D 29 85   STA $8529     
L_805F:
    $805F: 4C B8 83   JMP $83b8        ; → L_83B8
; ----- normal per-frame body: iterate voices X = 2..0 -----
; $8526 = note-step counter; reloaded from $8527 each time it underflows.
; When $8526 == $8527 (just reloaded) → step the pattern reader for ALL
; voices; otherwise just run modulators (vibrato/slide/PW).
L_8062:
    $8062: A2 02      LDX #$02          ; X = voice index, count 2 → 0
    $8064: CE 26 85   DEC $8526
    $8067: 10 06      BPL $806f        ; → L_806F  ; not yet — skip reload
    $8069: AD 27 85   LDA $8527
    $806C: 8D 26 85   STA $8526         ; reload divisor → triggers pattern step
L_806F:
    $806F: BD FB 84   LDA $84fb,x   
    $8072: 8D FE 84   STA $84fe     
    $8075: A8         TAY           
    $8076: AD 26 85   LDA $8526     
    $8079: CD 27 85   CMP $8527     
    $807C: D0 15      BNE $8093        ; → L_8093
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

; ============================================================================
; VIRTUAL: bytes $7B40-$7F3F disassembled as if at $C000
;         (copied at runtime by the relocator)
; ============================================================================

sub_C000:
    $C000: 4C 06 C0   JMP $c006        ; → L_C006
; ----- data gap $C003-$C005 (3 bytes) -----

; Sample player entry. Caller (init via $7EAC) has set $97 = sample id (1..3).
; This routine blocks (IRQ-disabled inside) until the sample finishes,
; clocking 1-bit pulses to $D404 with CIA2 Timer A providing the sample rate.
L_C006:
    $C006: A5 F7      LDA $f7           ; preserve $F7-$FA across blocking play
    $C008: 48         PHA
    $C009: A5 F8      LDA $f8
    $C00B: 48         PHA
    $C00C: A5 F9      LDA $f9
    $C00E: 48         PHA
    $C00F: A5 FA      LDA $fa
    $C011: 48         PHA
    $C012: EA         NOP           
    $C013: A9 3E      LDA #$3e      
    $C015: 25 01      AND $01       
    $C017: A5 01      LDA $01       
    $C019: AD 11 D0   LDA $d011     
    $C01C: 8D 09 C1   STA $c109     
    $C01F: A2 00      LDX #$00      
    $C021: AC 03 C3   LDY $c303     
    $C024: C0 00      CPY #$00      
    $C026: D0 06      BNE $c02e        ; → L_C02E
    $C028: 00         BRK           
; ----- data gap $C029-$C02D (5 bytes) -----

L_C02E:
    $C02E: BD 0B C3   LDA $c30b,x   
    $C031: C5 97      CMP $97       
    $C033: F0 0A      BEQ $c03f        ; → L_C03F
    $C035: E8         INX           
    $C036: 88         DEY           
    $C037: D0 F5      BNE $c02e        ; → L_C02E
    $C039: 20 09 C1   JSR $c109        ; → sub_C109
    $C03C: 4C EA C0   JMP $c0ea        ; → L_C0EA
L_C03F:
    $C03F: AD 0A C3   LDA $c30a     
    $C042: 8D AC C0   STA $c0ac     
    $C045: A5 97      LDA $97       
    $C047: 0A         ASL a         
    $C048: 0A         ASL a         
    $C049: AA         TAX           
    $C04A: BD 00 C2   LDA $c200,x   
    $C04D: 85 FB      STA $fb       
    $C04F: BD 01 C2   LDA $c201,x   
    $C052: 85 FC      STA $fc       
    $C054: BD 02 C2   LDA $c202,x   
    $C057: 85 F7      STA $f7       
    $C059: BD 03 C2   LDA $c203,x   
    $C05C: 85 F8      STA $f8       
    $C05E: A9 FF      LDA #$ff      
    $C060: 8D 02 D4   STA $d402      ;V1_PW_LO
    $C063: 8D 03 D4   STA $d403      ;V1_PW_HI
    $C066: 8D 04 DD   STA $dd04     
    $C069: 8D 05 DD   STA $dd05     
    $C06C: A0 00      LDY #$00      
    $C06E: A9 F0      LDA #$f0      
    $C070: 8D 06 D4   STA $d406      ;V1_SR
    $C073: AD 08 C3   LDA $c308     
    $C076: D0 05      BNE $c07d        ; → L_C07D
    $C078: A9 00      LDA #$00      
    $C07A: AD 11 D0   LDA $d011     
L_C07D:
    $C07D: A9 11      LDA #$11      
    $C07F: 8D 0E DD   STA $dd0e     
    $C082: EA         NOP           
    $C083: EA         NOP           
    $C084: EA         NOP           
    $C085: EA         NOP           
    $C086: EA         NOP           
    $C087: EA         NOP           
    $C088: 4C CF C0   JMP $c0cf        ; → L_C0CF
L_C08B:
    $C08B: E6 FB      INC $fb       
    $C08D: D0 02      BNE $c091        ; → L_C091
    $C08F: E6 FC      INC $fc       
L_C091:
    $C091: A6 FC      LDX $fc       
    $C093: E4 F8      CPX $f8       
    $C095: 90 09      BCC $c0a0        ; → L_C0A0
    $C097: A6 FB      LDX $fb       
    $C099: E4 F7      CPX $f7       
    $C09B: 90 03      BCC $c0a0        ; → L_C0A0
    $C09D: 4C EA C0   JMP $c0ea        ; → L_C0EA
; Sample loop: 8 bits per byte, each bit clocked at the rate of CIA2 Timer A.
; The high bit of $FE (next sample byte) selects which control register
; value to write: $49 = pulse+ringmod+gate (silenced-ish), $41 = pulse+gate.
; Toggling these gives a 1-bit DAC into V1's pulse output.
L_C0A0:
    $C0A0: A9 08      LDA #$08          ; bit counter: 8 bits per byte
    $C0A2: 85 96      STA $96
    $C0A4: B1 FB      LDA ($fb),y       ; fetch next sample byte ($FB/$FC = ptr)
    $C0A6: 85 FE      STA $fe           ; shift register for 8 bits
L_C0A8:
    $C0A8: AD 04 DD   LDA $dd04         ; CIA2 Timer A lo  (clocking the bitrate)
    $C0AB: C9 C0      CMP #$c0
    $C0AD: B0 F9      BCS $c0a8        ; → L_C0A8   ; spin until timer wraps
    $C0AF: A9 11      LDA #$11
    $C0B1: 8D 0E DD   STA $dd0e         ; restart CIA2 Timer A in one-shot mode
    $C0B4: 06 FE      ASL $fe           ; shift next bit into Carry
    $C0B6: 90 04      BCC $c0bc        ; → L_C0BC   ; bit = 0 → ctrl = $41
    $C0B8: A9 49      LDA #$49          ; bit = 1 → ctrl = $49 (pulse+ring+gate)
    $C0BA: D0 02      BNE $c0be        ; → L_C0BE
L_C0BC:
    $C0BC: A9 41      LDA #$41          ; pulse+gate
L_C0BE:
    $C0BE: 8D 04 D4   STA $d404      ;V1_CTRL  ; the 1-bit DAC write
    $C0C1: C6 96      DEC $96
    $C0C3: D0 E3      BNE $c0a8        ; → L_C0A8   ; next bit
    $C0C5: C6 F9      DEC $f9       
L_C0C7:
    $C0C7: D0 C2      BNE $c08b        ; → L_C08B
    $C0C9: E6 FB      INC $fb       
    $C0CB: D0 02      BNE $c0cf        ; → L_C0CF
    $C0CD: E6 FC      INC $fc       
L_C0CF:
    $C0CF: B1 FB      LDA ($fb),y   
    $C0D1: C9 10      CMP #$10      
L_C0D3:
    $C0D3: 90 02      BCC $c0d7        ; → L_C0D7
    $C0D5: A9 0F      LDA #$0f      
L_C0D7:
    $C0D7: 38         SEC           
    $C0D8: E5 FD      SBC $fd       
    $C0DA: 30 02      BMI $c0de        ; → L_C0DE
    $C0DC: D0 02      BNE $c0e0        ; → L_C0E0
L_C0DE:
    $C0DE: A9 01      LDA #$01      
L_C0E0:
    $C0E0: 8D 18 D4   STA $d418      ;VOL
    $C0E3: A9 10      LDA #$10      
    $C0E5: 85 F9      STA $f9       
    $C0E7: 4C 8B C0   JMP $c08b        ; → L_C08B
L_C0EA:
    $C0EA: A9 00      LDA #$00      
    $C0EC: 8D 18 D4   STA $d418      ;VOL
    $C0EF: AD 09 C1   LDA $c109     
    $C0F2: AD 11 D0   LDA $d011     
    $C0F5: A9 03      LDA #$03      
    $C0F7: 05 01      ORA $01       
    $C0F9: A5 01      LDA $01       
    $C0FB: 68         PLA           
    $C0FC: 85 FA      STA $fa       
    $C0FE: 68         PLA           
    $C0FF: 85 F9      STA $f9       
    $C101: 68         PLA           
    $C102: 85 F8      STA $f8       
    $C104: 68         PLA           
    $C105: 85 F7      STA $f7       
    $C107: EA         NOP           
    $C108: 60         RTS           
sub_C109:
    $C109: 1B         ???           
    $C10C: D0 C5      BNE $c0d3        ; → L_C0D3
    $C10E: C9 3B      CMP #$3b      
    $C110: D0 18      BNE $c12a        ; → L_C12A
    $C112: 20 75 C9   JSR $c975     
    $C115: B0 B0      BCS $c0c7        ; → L_C0C7
    $C117: 20 C8 C9   JSR $c9c8     
    $C11A: 20 00 CA   JSR $ca00     
    $C11D: 8D 0B 02   STA $020b     
L_C120:
    $C120: 20 51 CA   JSR $ca51     
    $C123: 20 E9 C9   JSR $c9e9     
    $C126: D0 F8      BNE $c120        ; → L_C120
    $C128: F0 9D      BEQ $c0c7        ; → L_C0C7
L_C12A:
    $C12A: C9 47      CMP #$47      
    $C12C: F0 07      BEQ $c135        ; → L_C135
    $C12E: C9 4A      CMP #$4a      
    $C130: D0 40      BNE $c172        ; → L_C172
    $C132: A9 00      LDA #$00      
    $C134: 2C A9 FF   BIT $ffa9     
    $C137: 8D 17 02   STA $0217     
    $C13A: 20 C2 C9   JSR $c9c2     
    $C13D: F0 08      BEQ $c147        ; → L_C147
    $C13F: 20 7A C9   JSR $c97a     
    $C142: B0 3C      BCS $c180        ; → L_C180
    $C144: 20 C8 C9   JSR $c9c8     
L_C147:
    $C147: 20 EE CD   JSR $cdee     
    $C14A: AE 06 02   LDX $0206     
    $C14D: 9A         TXS           
    $C14E: AD 17 02   LDA $0217     
    $C151: 30 08      BMI $c15b        ; → L_C15B
    $C153: AD 89 C4   LDA $c489     
    $C156: 48         PHA           
    $C157: AD 88 C4   LDA $c488     
    $C15A: 48         PHA           
L_C15B:
    $C15B: 78         SEI           
    $C15C: AD 00 02   LDA $0200     
    $C15F: 48         PHA           
    $C160: AD 01 02   LDA $0201     
    $C163: 48         PHA           
    $C164: AD 02 02   LDA $0202     
    $C167: 48         PHA           
    $C168: AD 03 02   LDA $0203     
    $C16B: AE 04 02   LDX $0204     
    $C16E: AC 05 02   LDY $0205     
    $C171: 40         RTI           
L_C172:
    $C172: C9 58      CMP #$58      
    $C174: D0 0D      BNE $c183        ; → L_C183
    $C176: 20 EE CD   JSR $cdee     
    $C179: AE 06 02   LDX $0206     
    $C17C: 9A         TXS           
    $C17D: 4C 74 A4   JMP $a474     
L_C180:
    $C180: 4C AC CA   JMP $caac     
L_C183:
    $C183: C9 50      CMP #$50      
    $C185: D0 1B      BNE $c1a2        ; → L_C1A2
    $C187: A9 04      LDA #$04      
    $C189: C5 9A      CMP $9a       
    $C18B: F0 12      BEQ $c19f        ; → L_C19F
    $C18D: 85 B8      STA $b8       
    $C18F: 85 BA      STA $ba       
    $C191: A9 00      LDA #$00      
    $C193: 85 B7      STA $b7       
    $C195: 85 B9      STA $b9       
    $C197: 20 C0 FF   JSR $ffc0     
    $C19A: A2 04      LDX #$04      
    $C19C: 20 C9 FF   JSR $ffc9     
L_C19F:
    $C19F: 4C 90 C0   JMP $c090        ; → L_C090
L_C1A2:
    $C1A2: C9 4F      CMP #$4f      
    $C1A4: D0 06      BNE $c1ac        ; → L_C1AC
    $C1A6: 20 EE CD   JSR $cdee     
    $C1A9: 4C 90 C0   JMP $c090        ; → L_C090
L_C1AC:
    $C1AC: C9 56      CMP #$56      
    $C1AE: F0 07      BEQ $c1b7        ; → L_C1B7
    $C1B0: C9 4C      CMP #$4c      
    $C1B2: D0 0B      BNE $c1bf        ; → L_C1BF
    $C1B4: A9 00      LDA #$00      
    $C1B6: 2C A9 01   BIT $01a9     
    $C1B9: 85 93      STA $93       
    $C1BB: A9 00      LDA #$00      
    $C1BD: F0 14      BEQ $c1d3        ; → L_C1D3
L_C1BF:
    $C1BF: C9 53      CMP #$53      
    $C1C1: F0 0A      BEQ $c1cd        ; → L_C1CD
    $C1C3: C9 5A      CMP #$5a      
    $C1C5: F0 03      BEQ $c1ca        ; → L_C1CA
    $C1C7: 4C 77 C3   JMP $c377        ; → L_C377
L_C1CA:
    $C1CA: A9 01      LDA #$01      
    $C1CC: 2C A9 03   BIT $03a9     
    $C1CF: 85 93      STA $93       
    $C1D1: A9 80      LDA #$80      
L_C1D3:
    $C1D3: 8D 0A 02   STA $020a     
    $C1D6: 20 EE CD   JSR $cdee     
    $C1D9: 20 93 FC   JSR $fc93     
    $C1DC: A0 02      LDY #$02      
    $C1DE: 84 7B      STY $7b       
    $C1E0: 88         DEY           
    $C1E1: 84 BA      STY $ba       
    $C1E3: 88         DEY           
    $C1E4: 84 B7      STY $b7       
    $C1E6: 84 B9      STY $b9       
    $C1E8: 84 90      STY $90       
L_C1EA:
    $C1EA: 20 C2 C9   JSR $c9c2     
    $C1ED: F0 34      BEQ $c223        ; → L_C223
    $C1EF: C9 20      CMP #$20      
    $C1F1: F0 F7      BEQ $c1ea        ; → L_C1EA
    $C1F3: C9 22      CMP #$22      
    $C1F5: D0 18      BNE $c20f        ; → L_C20F
    $C1F7: A9 30      LDA #$30      
    $C1F9: 85 BB      STA $bb       
    $C1FB: A9 02      LDA #$02      
    $C1FD: 85 BC      STA $bc       
    $C1FF: 20 DD DD   JSR $dddd     
    $C202: DD DD 00   CMP $00dd,x   
    $C205: 48         PHA           
    $C206: 2F         ???           
    $C209: 58         CLI           
    $C20A: 0D 69 0E   ORA $0e69     
    $C20D: 69 2F      ADC #$2f      
L_C20F:
    $C20F: 7B         ???           
    $C212: DD DD DD   CMP $dddd,x   
    $C215: DD DD DD   CMP $dddd,x   
    $C218: DD DD DD   CMP $dddd,x   
    $C21B: DD DD DD   CMP $dddd,x   
    $C21E: DD DD DD   CMP $dddd,x   
    $C221: DD DD DD   CMP $dddd,x   
    $C224: DD DD DD   CMP $dddd,x   
    $C227: DD DD DD   CMP $dddd,x   
    $C22A: DD DD DD   CMP $dddd,x   
    $C22D: DD DD DD   CMP $dddd,x   
    $C230: DD DD DD   CMP $dddd,x   
    $C233: DD DD DD   CMP $dddd,x   
    $C236: DD DD DD   CMP $dddd,x   
    $C239: DD DD DD   CMP $dddd,x   
    $C23C: DD DD DD   CMP $dddd,x   
    $C23F: DD DD DD   CMP $dddd,x   
    $C242: DD DD DD   CMP $dddd,x   
    $C245: DD DD DD   CMP $dddd,x   
    $C248: DD DD DD   CMP $dddd,x   
    $C24B: DD DD DD   CMP $dddd,x   
    $C24E: DD DD DD   CMP $dddd,x   
    $C251: DD DD DD   CMP $dddd,x   
    $C254: DD DD DD   CMP $dddd,x   
    $C257: DD DD DD   CMP $dddd,x   
    $C25A: DD DD DD   CMP $dddd,x   
    $C25D: DD DD DD   CMP $dddd,x   
    $C260: DD DD DD   CMP $dddd,x   
    $C263: DD DD DD   CMP $dddd,x   
    $C266: DD DD DD   CMP $dddd,x   
    $C269: DD DD DD   CMP $dddd,x   
    $C26C: DD DD DD   CMP $dddd,x   
    $C26F: DD DD DD   CMP $dddd,x   
    $C272: DD DD DD   CMP $dddd,x   
    $C275: DD DD DD   CMP $dddd,x   
    $C278: DD DD DD   CMP $dddd,x   
    $C27B: DD DD DD   CMP $dddd,x   
    $C27E: DD DD DD   CMP $dddd,x   
    $C281: DD DD DD   CMP $dddd,x   
    $C284: DD DD DD   CMP $dddd,x   
    $C287: DD DD DD   CMP $dddd,x   
    $C28A: DD DD DD   CMP $dddd,x   
    $C28D: DD DD DD   CMP $dddd,x   
    $C290: DD DD DD   CMP $dddd,x   
    $C293: DD DD DD   CMP $dddd,x   
    $C296: DD DD DD   CMP $dddd,x   
    $C299: DD DD DD   CMP $dddd,x   
    $C29C: DD DD DD   CMP $dddd,x   
    $C29F: DD DD DD   CMP $dddd,x   
    $C2A2: DD DD DD   CMP $dddd,x   
    $C2A5: DD DD DD   CMP $dddd,x   
    $C2A8: DD DD DD   CMP $dddd,x   
    $C2AB: DD DD DD   CMP $dddd,x   
    $C2AE: DD DD DD   CMP $dddd,x   
    $C2B1: DD DD DD   CMP $dddd,x   
    $C2B4: DD DD DD   CMP $dddd,x   
    $C2B7: DD DD DD   CMP $dddd,x   
    $C2BA: DD DD DD   CMP $dddd,x   
    $C2BD: DD DD DD   CMP $dddd,x   
    $C2C0: DD DD DD   CMP $dddd,x   
    $C2C3: DD DD DD   CMP $dddd,x   
    $C2C6: DD DD DD   CMP $dddd,x   
    $C2C9: DD DD DD   CMP $dddd,x   
    $C2CC: DD DD DD   CMP $dddd,x   
    $C2CF: DD DD DD   CMP $dddd,x   
    $C2D2: DD DD DD   CMP $dddd,x   
    $C2D5: DD DD DD   CMP $dddd,x   
    $C2D8: DD DD DD   CMP $dddd,x   
    $C2DB: DD DD DD   CMP $dddd,x   
    $C2DE: DD DD DD   CMP $dddd,x   
    $C2E1: DD DD DD   CMP $dddd,x   
    $C2E4: DD DD DD   CMP $dddd,x   
    $C2E7: DD DD DD   CMP $dddd,x   
    $C2EA: DD DD DD   CMP $dddd,x   
    $C2ED: DD DD DD   CMP $dddd,x   
    $C2F0: DD DD DD   CMP $dddd,x   
    $C2F3: DD DD DD   CMP $dddd,x   
    $C2F6: DD DD DD   CMP $dddd,x   
    $C2F9: DD DD DD   CMP $dddd,x   
    $C2FC: DD DD DD   CMP $dddd,x   
    $C2FF: DD 21 A2   CMP $a221,x   
    $C302: FF         ???           
    $C303: 03         ???           
    $C305: DD DD DD   CMP $dddd,x   
    $C308: 01 C0      ORA ($c0,x)   
    $C30A: C0 01      CPY #$01      
    $C30C: 02         ???           
    $C30D: 03         ???           
    $C30E: DD DD FF   CMP $ffdd,x   
    $C311: FF         ???           
    $C313: FF         ???           
    $C314: FF         ???           
    $C316: FF         ???           
    $C317: FF         ???           
    $C319: FF         ???           
    $C31A: FF         ???           
    $C31C: FF         ???           
    $C31D: FF         ???           
    $C31F: FF         ???           
    $C320: FF         ???           
    $C322: FF         ???           
    $C323: FF         ???           
    $C325: FF         ???           
    $C326: FF         ???           
    $C328: FF         ???           
    $C329: FF         ???           
    $C32B: FF         ???           
    $C32C: FF         ???           
    $C32E: FF         ???           
    $C32F: FF         ???           
    $C331: FF         ???           
    $C332: FF         ???           
    $C334: FF         ???           
    $C335: FF         ???           
    $C337: FF         ???           
    $C338: FF         ???           
    $C33A: FF         ???           
    $C33B: FF         ???           
    $C33D: FF         ???           
    $C33E: FF         ???           
    $C340: 8D 7F 7E   STA $7e7f     
    $C343: C9 03      CMP #$03      
    $C345: B0 38      BCS $c37f        ; → L_C37F
    $C347: 4C 10 80   JMP $8010        ; → L_8010
; ----- data gap $C34A-$C376 (45 bytes) -----

L_C377:
    $C377: 4C 22 80   JMP $8022        ; → L_8022
; ----- data gap $C37A-$C37E (5 bytes) -----

L_C37F:
    $C37F: C9 06      CMP #$06      
    $C381: B0 03      BCS $c386        ; → L_C386
    $C383: 4C 8A 7E   JMP $7e8a        ; → L_7E8A
L_C386:
    $C386: 38         SEC           
    $C387: E9 06      SBC #$06      
    $C389: 20 1F 80   JSR $801f        ; → sub_801F
    $C38C: 4C 13 80   JMP $8013        ; → L_8013
; ----- data gap $C38F-$C3FF (113 bytes) -----

