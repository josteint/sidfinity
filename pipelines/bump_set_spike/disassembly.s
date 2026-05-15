; ============================================================================
; Rob Hubbard - Bump Set Spike (1986 Entertainment USA)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: demo/hubbard/Bump_Set_Spike_original.sid
; Load:   $B000   Init: $B000   Play: $B016
; PSID:   2 subtunes, default subtune 1 (1-indexed; A=0 passed to init)
; Binary: $B000-$BFFF (4096 bytes)
;
; Auto-traced 1070 reachable code bytes from init+play. Layout commentary
; below was hand-derived by combining static analysis with binary reads
; of the data tables (see verification at the end of this header).
;
; Same Hubbard engine family as Action Biker / Confuzion / Crazy Comets —
; pattern/orderlist pointers per voice, instrument records, vibrato +
; portamento + PWM + auto-arp effects driven by a per-instrument flag byte.
; This SID is relocated to $B000 (Action Biker is at $C000).
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($B000): JMP $BF0D. Real init at $BF0D:
;   - A holds subtune (0-indexed). Sets X=A, Y=0.
;   - Patches the play-divider reload: $B4F0+subtune → $B01C (LDA #imm
;     operand at the tempo-divider reload, $09 for subtune 0, $03 for 1).
;   - Sets $B4F3 = $B4ED+subtune (per-note tempo, $02 for subtune 0).
;   - Computes X = subtune*6 (via ASL; ASL; CLC; ADC saved-A) and copies
;     6 bytes from $B5E1+X to $B5DB[0..5] = three voice orderlist
;     pointers (lo[0..2], hi[0..2]).
;       Subtune 0 seed: V1=$B663  V2=$B689  V3=$B6E2
;       Subtune 1 seed: V1=$B72B  V2=$B749  V3=$B79A
;   - Clears V1/V2/V3 ctrl ($D404/$D40B/$D412) and $D417 (res/filt),
;     sets vol $0F, sets $B4F7 = $40 (FIRST-FRAME flag).
;   - RTS.
;
; sub_B003: JMP $BF4C → write $C0 to $B4F7 and RTS. This is the
;   end-of-song trampoline; bit 7 set = end, bit 6 set = also do a
;   one-time silence pass on the next play frame.
;
; play ($B016): every frame.
;   1. DEC $B4F4 (play-rate divider).
;      - BPL → do work (counter still positive after DEC).
;      - else: LDA #$09 / STA $B4F4 / RTS  (the immediate is patched per
;        subtune; reload $09 means 9 work frames + 1 skip frame per cycle).
;   2. INC $B506 (global frame counter, mod 256).
;   3. BIT $B4F7 — song state byte:
;        bit 7 → end-of-song path ($B047): if bit 6 also set, silence
;          all voices, set vol $0F, latch $B4F7=$80 to skip silencing
;          on subsequent frames, then JMP $B3FE (RTS).
;        bit 6 → FIRST FRAME path: zero $B506 and zero per-voice state
;          arrays $B4C3,X / $B4C6,X / $B4C9,X / $B4D2,X for X=2..0,
;          STA $B4F7 (clear the flag), fall through to per-voice work.
;        both clear → normal play.
;   4. Per-voice loop at $B061..$B3FB.
;
; PER-VOICE PROCESSING ($B061..$B3FB):
;   X iterates 2 → 1 → 0 (V3 → V2 → V1). The big DEX-then-loop is at
;   $B3F8 (DEX; BMI $B3FE=RTS; JMP $B06E).
;
;   $B061: X=2; DEC $B4EC (per-note tempo counter); if BPL, skip reload;
;     else reload $B4EC = $B4F3.
;
;   $B06E loop body:
;     - LDA $B4BF,X → STA $B4C2; TAY. $B4BF/C0/C1 = {00,07,0E} are the
;       per-voice SID register offsets. Y is then used as the +Y in
;       STA $D4xx,Y all over the per-voice code.
;     - CMP $B4EC vs $B4F3: only equal RIGHT AFTER A RELOAD, i.e. once
;       every (tempo+2) frames. Otherwise BNE → JMP $B1B6 (effects only).
;     - On the note-tick frame:
;       - LDA $B5DB,X / $B5DE,X → ($FB),y orderlist pointer for this voice.
;       - DEC $B4C9,X (note duration remaining).
;       - BMI → next note ($B095).
;       - else JMP $B197 (note still playing — handle release / fall to fx).
;
;   $B095 (next note in orderlist):
;     - LDY $B4C3,X (orderlist position), LDA ($FB),Y.
;     - $FF → restart-orderlist ($B0A8): zero per-voice state, JMP $B095.
;     - $FE → end-of-song marker: JSR $B003 (sets $B4F7=$C0), JMP $B3FE.
;     - else: pattern index → JMP $B0B9.
;
;   $B0B9 (load pattern + first note record):
;     - Y = pattern index. ($FD) = $B5ED,Y (lo) / $B628,Y (hi).
;     - LDY $B4C6,X (pattern position).
;     - LDA #$FF → STA $B4D8 (default ctrl-mask = $FF; cleared to $FE
;       at $B12B if note byte's bit 6 is set → suppresses gate-on).
;     - LDA ($FD),Y = first note byte → STA $B4CC,X (saved) and $B4D9.
;       AND #$1F → $B4C9,X (low 5 bits = note duration).
;     - BIT $B4D9: bit 6 set → JMP $B12B (no portamento data block,
;       and clear $B4D8 to $FE so next ctrl write masks gate bit off).
;     - INC $B4C6,X (advance past first byte).
;     - Bit 7 of first byte: if SET, the next byte is portamento speed
;       (negative-flagged). Branch:
;         BPL → instrument byte (positive), STA $B4D5,X.
;         else (negative) → STA $B4FE,X (porta lo), INY, LDA ($FD),Y →
;           STA $B501,X (porta hi), INC $B4C6,X, then fall to instrument.
;     - INY, LDA ($FD),Y → STA $B4D2,X (note number).
;     - ASL; TAY; LDA $B3FF,Y → $B4DA (freq lo), LDA $B400,Y →
;       $D401,Y (V1_FREQ_HI) and $B4F8,X. LDA $B4DA → $D400,Y
;       (V1_FREQ_LO) and $B4FB,X.
;
;   $B12E (instrument apply):
;     - LDA $B4D5,X (inst#), STX $B4DB (save voice X), ASL ASL ASL → X = inst*8.
;     - $B515,X = ctrl byte; mask with $B4D8 ($FF or $FE) → $D404,Y.
;     - $B513,X → $D402,Y (PW lo) / PHA. $B514,X → $D403,Y (PW hi) / PHA.
;     - $B516,X → $D405,Y (AD).  $B517,X → $D406,Y (SR).
;     - LDX $B4DB (restore). Clear $B4E9,X (PW direction) and $B4E6,X (PW counter).
;     - PLA → $B510,X (voice PW hi). PLA → $B50D,X (voice PW lo).
;     - LDA $B4DC → $B4CF,X (saved unmasked ctrl, for release path).
;     - INC $B4C6,X; LDA ($FD),Y again. If $FF → end-of-pattern: zero
;       $B4C6,X and INC $B4C3,X (advance orderlist). JMP $B3F8.
;
;   $B197 (note still playing — release shaping when duration reached 0):
;     - If saved-ctrl $B4CC,X bit 5 set OR $B4C9,X (duration) != 0, skip.
;     - else: write ($B4CF,X AND $FE) → $D404,Y (clear gate),
;       and 0 → $D405,Y / $D406,Y (kill envelope). Falls through to fx.
;
;   $B1B6..$B287 (vibrato / "effect chunk 1"):
;     - Y = inst*8 base; cache as $B4F6.
;     - $B51A,Y → $B504 (instrument FX FLAGS — bits select effects).
;     - $B519,Y → $B4DE (effect param B — PW step / vib depth).
;     - $B518,Y → if 0, JMP $B288 (no vibrato; skip to PW block).
;       Otherwise that byte = (frame_limit << 3) | shift_amount: high
;       bits → $B507,X (frame limit), low 3 bits → $B4DD (right-shift
;       count for the freq delta). The triangle-wave counter $B4E3,X
;       walks 0 → $B507,X then back, with $B50A,X holding direction.
;     - Computes per-frame delta = (freq[note+1] - freq[note]) >> $B4DD,
;       then adds delta*Y or subtracts delta*Y from freq[note] base, and
;       writes the result to $D400/$D401,Y. (Classic Hubbard vibrato:
;       triangle modulation centered on the played freq.)
;
;   $B288..$B301 (pulse-width effect, gated by $B504 bit 3):
;     - bit 3 SET → linear PWM slide: $B513,Y (instrument PW lo) += $B4DE
;       (writes back into the INSTRUMENT TABLE; PW state is per-instrument,
;       not per-voice), then mirror to $D402,Y.
;     - bit 3 CLEAR → bouncing PWM:
;       - Skip unless ($B506 AND $03) == 0 (every 4th frame).
;       - DEC $B4E6,X (PW step counter); reload from low nibble of $B4DE.
;       - $B505 = high nibble of $B4DE (step size).
;       - $B4E9,X is direction flag (0 = up, 1 = down).
;       - Up: PW += $B505; if hi nibble hits $0E → flip direction.
;       - Down: PW -= $B505; if hi nibble hits $08 → flip direction.
;       *** The $0E and $08 thresholds are HARDCODED bounds for the
;           PW wave — see memory `reference_hubbard_pwm_bounds.md`. ***
;
;   $B302..$B34A (frequency portamento, gated by $B4FE,X != 0):
;     - $B4FE,X = portamento speed lo (high bit selects direction);
;       $B501,X = portamento speed hi.
;     - bit 0 of speed-lo set → subtract from voice freq; else add.
;     - Writes new freq to $D400,Y / $D401,Y AND back to $B4FB,X / $B4F8,X.
;
;   $B34B..$B386 (force-release on portamento target, gated by $B504 bit 0):
;     - If $B4F8,X != 0 and $B4C9,X != 0 and (saved_dur - 1) >= remaining,
;       DEC $B4F8,X (one-step glide), write $D401,Y, then if saved-ctrl
;       AND $FE != 0, write that to $D404,Y (keep gate state); else
;       write $80 to $D404,Y (test bit + gate off — abrupt cut).
;
;   $B387..$B3B1 (auto-arpeggio, gated by $B504 bit 1):
;     - Only every 4th frame ($B506 AND $03 == 0).
;     - INC $B4D2,X (cycle through chord notes), look up freq[note],
;       write $D400/$D401,Y. The orderlist note byte holds the chord
;       ROOT and bit 1 of the FX flags enables the auto-step.
;
;   $B3B2..$B3F7 (octave-jump effect, gated by $B504 bit 2):
;     - Pulls a number from $B504 high nibble, patches it as the immediate
;       at $B3DA (a self-modifying compare target — the byte is shoved
;       into a scratch slot inside the data gap, NOT a live instruction).
;     - Y = $01 or $02 depending on whether high nibble == $0C.
;     - Stores Y in another scratch slot at $B3D2.
;     - Frame parity ($B506 AND $02): selects between (note - $0C) and note
;       — so the freq alternates between an octave-down note and the
;       current note every other frame. Writes to $D400/$D401,Y.
;
;   $B3F8: DEX; BMI $B3FE=RTS; else JMP $B06E (next voice).
;
; ============================================================================
; DATA LAYOUT (verified by reading the binary)
; --------------------------------------------
;
; FREQ TABLE: $B3FF, 96 semitones packed (lo, hi) 2-byte stride.
;   freq[0] = $0116 (matches Action Biker — Hubbard reused this table).
;   Indexed via ASL note → Y; LDA $B3FF,Y = lo (offset Y), LDA $B400,Y = hi.
;   Table runs $B3FF..$B4BE (192 bytes for 96 semitones).
;
; VOICE SID OFFSET TABLE: $B4BF-$B4C1 = {$00, $07, $0E}.
;   Loaded into Y as the +Y in STA $D4xx,Y for the active voice.
;
; SCRATCH / PER-VOICE STATE ARRAYS (X = 0..2 indexes voices V1..V3):
;   $B4C2     scratch (current voice SID +offset)
;   $B4C3,X   orderlist position
;   $B4C6,X   pattern position
;   $B4C9,X   note duration remaining
;   $B4CC,X   saved first byte of note record (bits 5-7 = flags, 0-4 = dur)
;   $B4CF,X   saved instrument ctrl byte (for release-restore)
;   $B4D2,X   current note number
;   $B4D5,X   current instrument number
;   $B4D8     ctrl-mask scratch ($FF normal, $FE = mask gate-on bit)
;   $B4D9..   scratch (note-byte, freq-temp, X-save, etc.)
;   $B4DD     vibrato shift amount
;   $B4DE     PW/vib param (instrument byte 6)
;   $B4DF/E0  vibrato delta lo/hi
;   $B4E1/E2  vibrato accumulator lo/hi
;   $B4E3,X   vibrato counter
;   $B4E6,X   PW step counter
;   $B4E9,X   PW direction flag (0 up, 1 down)
;   $B4EC     per-note tempo counter
;   $B4ED+S   per-subtune tempo reload (S=0 → $02, S=1 → $01)
;   $B4F0+S   per-subtune play-divider reload (S=0 → $09, S=1 → $03)
;   $B4F3     active per-note tempo reload
;   $B4F4     play-divider counter (initial $02)
;   $B4F6     scratch (inst*8 base for fx block)
;   $B4F7     song state flag (bit 7 = end-of-song, bit 6 = first-frame)
;   $B4F8,X   voice freq hi (last written)
;   $B4FB,X   voice freq lo (last written)
;   $B4FE,X   portamento speed lo (bit 0 = direction)
;   $B501,X   portamento speed hi
;   $B504     active instrument fx flags (cached from $B51A,Y)
;   $B505     PW step hi-nibble scratch
;   $B506     global frame counter
;   $B507,X   vibrato/PW frame limit
;   $B50A,X   vibrato direction
;   $B50D,X   voice PW lo
;   $B510,X   voice PW hi
;
; INSTRUMENT TABLE: $B513, 8 bytes per record (Y = inst*8).
;   $B513,Y   PW lo
;   $B514,Y   PW hi
;   $B515,Y   ctrl byte (waveform + gate seed)
;   $B516,Y   AD
;   $B517,Y   SR
;   $B518,Y   fx byte 5: vibrato (frame_limit<<3)|shift; 0 = off
;   $B519,Y   fx byte 6: PW step / vib depth
;   $B51A,Y   fx flags: b0=porta-target b1=auto-arp b2=octave-jump b3=PW-slide
;
; PER-VOICE ORDERLIST POINTERS (live state, written by init):
;   $B5DB+X   orderlist lo (X = voice 0..2)
;   $B5DE+X   orderlist hi
;
; PER-SUBTUNE ORDERLIST SEED TABLE: $B5E1, 6 bytes per subtune.
;   Subtune 0 ($B5E1): 63 89 E2 B6 B6 B6  → V1=$B663 V2=$B689 V3=$B6E2
;   Subtune 1 ($B5E7): 2B 49 9A B7 B7 B7  → V1=$B72B V2=$B749 V3=$B79A
;
; PATTERN POINTER TABLES (Y = pattern index):
;   $B5ED,Y   pattern lo
;   $B628,Y   pattern hi
;
; ============================================================================
;
; CONSEQUENCE FOR OUR CODEGEN:
;   This is the same engine family as Action Biker. Three departures from
;   that earlier engine to be aware of:
;     1. The play-rate divider uses BPL (skip when negative) rather than
;        Action Biker's BMI (work when negative). The reload value here
;        is $09 (subtune 0), so 1 of every 10 frames is silently skipped.
;     2. PWM bouncing thresholds ($0E, $08) are hardcoded as in Commando
;        (memory `reference_hubbard_pwm_bounds.md`). Our codegen must
;        emit these constants verbatim, not derive them per-instrument.
;     3. The instrument FX flags byte ($B504) bit 3 = PW slide vs.
;        bouncing — same semantics as Commando, NOT the post-1986
;        "table arpeggio" reading from `project_hubbard_table_arp.md`.
;
; ============================================================================

; ======= init: =======
init:
    $B000: 4C 0D BF   JMP $bf0d        ; → L_BF0D
sub_B003:
    $B003: 4C 4C BF   JMP $bf4c        ; → L_BF4C
; ----- data gap $B006-$B015 (16 bytes) -----

; ======= play: =======
play:
    $B016: CE F4 B4   DEC $b4f4     
    $B019: 10 06      BPL $b021        ; → L_B021
    $B01B: A9 09      LDA #$09      
    $B01D: 8D F4 B4   STA $b4f4     
    $B020: 60         RTS           
L_B021:
    $B021: EE 06 B5   INC $b506     
    $B024: 2C F7 B4   BIT $b4f7     
    $B027: 30 1E      BMI $b047        ; → L_B047
    $B029: 50 36      BVC $b061        ; → L_B061
    $B02B: A9 00      LDA #$00      
    $B02D: 8D 06 B5   STA $b506     
    $B030: A2 02      LDX #$02      
L_B032:
    $B032: 9D C3 B4   STA $b4c3,x   
    $B035: 9D C6 B4   STA $b4c6,x   
    $B038: 9D C9 B4   STA $b4c9,x   
    $B03B: 9D D2 B4   STA $b4d2,x   
    $B03E: CA         DEX           
    $B03F: 10 F1      BPL $b032        ; → L_B032
    $B041: 8D F7 B4   STA $b4f7     
    $B044: 4C 61 B0   JMP $b061        ; → L_B061
L_B047:
    $B047: 50 15      BVC $b05e        ; → L_B05E
    $B049: A9 00      LDA #$00      
    $B04B: 8D 04 D4   STA $d404      ;V1_CTRL
    $B04E: 8D 0B D4   STA $d40b      ;V2_CTRL
    $B051: 8D 12 D4   STA $d412      ;V3_CTRL
    $B054: A9 0F      LDA #$0f      
    $B056: 8D 18 D4   STA $d418      ;VOL
    $B059: A9 80      LDA #$80      
    $B05B: 8D F7 B4   STA $b4f7     
L_B05E:
    $B05E: 4C FE B3   JMP $b3fe        ; → L_B3FE
L_B061:
    $B061: A2 02      LDX #$02      
    $B063: CE EC B4   DEC $b4ec     
    $B066: 10 06      BPL $b06e        ; → L_B06E
    $B068: AD F3 B4   LDA $b4f3     
    $B06B: 8D EC B4   STA $b4ec     
L_B06E:
    $B06E: BD BF B4   LDA $b4bf,x   
    $B071: 8D C2 B4   STA $b4c2     
    $B074: A8         TAY           
    $B075: AD EC B4   LDA $b4ec     
    $B078: CD F3 B4   CMP $b4f3     
    $B07B: D0 15      BNE $b092        ; → L_B092
    $B07D: BD DB B5   LDA $b5db,x   
    $B080: 85 FB      STA $fb       
    $B082: BD DE B5   LDA $b5de,x   
    $B085: 85 FC      STA $fc       
    $B087: DE C9 B4   DEC $b4c9,x   
    $B08A: 30 09      BMI $b095        ; → L_B095
    $B08C: 4C 97 B1   JMP $b197        ; → L_B197
; ----- data gap $B08F-$B091 (3 bytes) -----

L_B092:
    $B092: 4C B6 B1   JMP $b1b6        ; → L_B1B6
L_B095:
    $B095: BC C3 B4   LDY $b4c3,x   
    $B098: B1 FB      LDA ($fb),y   
    $B09A: C9 FF      CMP #$ff      
    $B09C: F0 0A      BEQ $b0a8        ; → L_B0A8
    $B09E: C9 FE      CMP #$fe      
    $B0A0: D0 17      BNE $b0b9        ; → L_B0B9
    $B0A2: 20 03 B0   JSR $b003        ; → sub_B003
    $B0A5: 4C FE B3   JMP $b3fe        ; → L_B3FE
L_B0A8:
    $B0A8: A9 00      LDA #$00      
    $B0AA: 9D C9 B4   STA $b4c9,x   
    $B0AD: 9D C3 B4   STA $b4c3,x   
    $B0B0: 9D C6 B4   STA $b4c6,x   
    $B0B3: 4C 95 B0   JMP $b095        ; → L_B095
; ----- data gap $B0B6-$B0B8 (3 bytes) -----

L_B0B9:
    $B0B9: A8         TAY           
    $B0BA: B9 ED B5   LDA $b5ed,y   
    $B0BD: 85 FD      STA $fd       
    $B0BF: B9 28 B6   LDA $b628,y   
    $B0C2: 85 FE      STA $fe       
    $B0C4: A9 00      LDA #$00      
    $B0C6: 9D FE B4   STA $b4fe,x   
    $B0C9: BC C6 B4   LDY $b4c6,x   
    $B0CC: A9 FF      LDA #$ff      
    $B0CE: 8D D8 B4   STA $b4d8     
    $B0D1: B1 FD      LDA ($fd),y   
    $B0D3: 9D CC B4   STA $b4cc,x   
    $B0D6: 8D D9 B4   STA $b4d9     
    $B0D9: 29 1F      AND #$1f      
    $B0DB: 9D C9 B4   STA $b4c9,x   
    $B0DE: 2C D9 B4   BIT $b4d9     
    $B0E1: 70 48      BVS $b12b        ; → L_B12B
    $B0E3: FE C6 B4   INC $b4c6,x   
    $B0E6: AD D9 B4   LDA $b4d9     
    $B0E9: 10 1A      BPL $b105        ; → L_B105
    $B0EB: C8         INY           
    $B0EC: B1 FD      LDA ($fd),y   
    $B0EE: 10 0F      BPL $b0ff        ; → L_B0FF
    $B0F0: 9D FE B4   STA $b4fe,x   
    $B0F3: C8         INY           
    $B0F4: B1 FD      LDA ($fd),y   
    $B0F6: 9D 01 B5   STA $b501,x   
    $B0F9: FE C6 B4   INC $b4c6,x   
    $B0FC: 4C 02 B1   JMP $b102        ; → L_B102
L_B0FF:
    $B0FF: 9D D5 B4   STA $b4d5,x   
L_B102:
    $B102: FE C6 B4   INC $b4c6,x   
L_B105:
    $B105: C8         INY           
    $B106: B1 FD      LDA ($fd),y   
    $B108: 9D D2 B4   STA $b4d2,x   
    $B10B: 0A         ASL a         
    $B10C: A8         TAY           
    $B10D: B9 FF B3   LDA $b3ff,y   
    $B110: 8D DA B4   STA $b4da     
    $B113: B9 00 B4   LDA $b400,y   
    $B116: AC C2 B4   LDY $b4c2     
    $B119: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $B11C: 9D F8 B4   STA $b4f8,x   
    $B11F: AD DA B4   LDA $b4da     
    $B122: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $B125: 9D FB B4   STA $b4fb,x   
    $B128: 4C 2E B1   JMP $b12e        ; → L_B12E
L_B12B:
    $B12B: CE D8 B4   DEC $b4d8     
L_B12E:
    $B12E: AC C2 B4   LDY $b4c2     
    $B131: BD D5 B4   LDA $b4d5,x   
    $B134: 8E DB B4   STX $b4db     
    $B137: 0A         ASL a         
    $B138: 0A         ASL a         
    $B139: 0A         ASL a         
    $B13A: AA         TAX           
    $B13B: BD 15 B5   LDA $b515,x   
    $B13E: 8D DC B4   STA $b4dc     
    $B141: BD 15 B5   LDA $b515,x   
    $B144: 2D D8 B4   AND $b4d8     
    $B147: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $B14A: BD 13 B5   LDA $b513,x   
    $B14D: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $B150: 48         PHA           
    $B151: BD 14 B5   LDA $b514,x   
    $B154: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $B157: 48         PHA           
    $B158: BD 16 B5   LDA $b516,x   
    $B15B: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $B15E: BD 17 B5   LDA $b517,x   
    $B161: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $B164: AE DB B4   LDX $b4db     
    $B167: A9 00      LDA #$00      
    $B169: 9D E9 B4   STA $b4e9,x   
    $B16C: 9D E6 B4   STA $b4e6,x   
    $B16F: 68         PLA           
    $B170: 9D 10 B5   STA $b510,x   
    $B173: 68         PLA           
    $B174: 9D 0D B5   STA $b50d,x   
    $B177: AE DB B4   LDX $b4db     
    $B17A: AD DC B4   LDA $b4dc     
    $B17D: 9D CF B4   STA $b4cf,x   
    $B180: FE C6 B4   INC $b4c6,x   
    $B183: BC C6 B4   LDY $b4c6,x   
    $B186: B1 FD      LDA ($fd),y   
    $B188: C9 FF      CMP #$ff      
    $B18A: D0 08      BNE $b194        ; → L_B194
    $B18C: A9 00      LDA #$00      
    $B18E: 9D C6 B4   STA $b4c6,x   
    $B191: FE C3 B4   INC $b4c3,x   
L_B194:
    $B194: 4C F8 B3   JMP $b3f8        ; → L_B3F8
L_B197:
    $B197: AC C2 B4   LDY $b4c2     
    $B19A: BD CC B4   LDA $b4cc,x   
    $B19D: 29 20      AND #$20      
    $B19F: D0 15      BNE $b1b6        ; → L_B1B6
    $B1A1: BD C9 B4   LDA $b4c9,x   
    $B1A4: D0 10      BNE $b1b6        ; → L_B1B6
    $B1A6: BD CF B4   LDA $b4cf,x   
    $B1A9: 29 FE      AND #$fe      
    $B1AB: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $B1AE: A9 00      LDA #$00      
    $B1B0: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $B1B3: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_B1B6:
    $B1B6: BD D5 B4   LDA $b4d5,x   
    $B1B9: 0A         ASL a         
    $B1BA: 0A         ASL a         
    $B1BB: 0A         ASL a         
    $B1BC: A8         TAY           
    $B1BD: 8C F6 B4   STY $b4f6     
    $B1C0: B9 1A B5   LDA $b51a,y   
    $B1C3: 8D 04 B5   STA $b504     
    $B1C6: B9 19 B5   LDA $b519,y   
    $B1C9: 8D DE B4   STA $b4de     
    $B1CC: B9 18 B5   LDA $b518,y   
    $B1CF: D0 03      BNE $b1d4        ; → L_B1D4
    $B1D1: 4C 88 B2   JMP $b288        ; → L_B288
L_B1D4:
    $B1D4: 48         PHA           
    $B1D5: 29 78      AND #$78      
    $B1D7: 4A         LSR a         
    $B1D8: 4A         LSR a         
    $B1D9: 4A         LSR a         
    $B1DA: 9D 07 B5   STA $b507,x   
    $B1DD: 68         PLA           
    $B1DE: 29 07      AND #$07      
    $B1E0: 8D DD B4   STA $b4dd     
    $B1E3: BD 0A B5   LDA $b50a,x   
    $B1E6: 10 0A      BPL $b1f2        ; → L_B1F2
    $B1E8: DE E3 B4   DEC $b4e3,x   
    $B1EB: D0 19      BNE $b206        ; → L_B206
    $B1ED: FE 0A B5   INC $b50a,x   
    $B1F0: 10 14      BPL $b206        ; → L_B206
L_B1F2:
    $B1F2: FE E3 B4   INC $b4e3,x   
    $B1F5: BD 07 B5   LDA $b507,x   
    $B1F8: DD E3 B4   CMP $b4e3,x   
    $B1FB: B0 09      BCS $b206        ; → L_B206
    $B1FD: 9D E3 B4   STA $b4e3,x   
    $B200: DE 0A B5   DEC $b50a,x   
    $B203: DE E3 B4   DEC $b4e3,x   
L_B206:
    $B206: BD D2 B4   LDA $b4d2,x   
    $B209: 0A         ASL a         
    $B20A: A8         TAY           
    $B20B: 38         SEC           
    $B20C: B9 FF B3   LDA $b3ff,y   
    $B20F: F9 FD B3   SBC $b3fd,y   
    $B212: 8D DF B4   STA $b4df     
    $B215: B9 00 B4   LDA $b400,y   
    $B218: F9 FE B3   SBC $b3fe,y   
L_B21B:
    $B21B: CE DD B4   DEC $b4dd     
    $B21E: 30 07      BMI $b227        ; → L_B227
    $B220: 4A         LSR a         
    $B221: 6E DF B4   ROR $b4df     
    $B224: 4C 1B B2   JMP $b21b        ; → L_B21B
L_B227:
    $B227: 8D E0 B4   STA $b4e0     
    $B22A: B9 FF B3   LDA $b3ff,y   
    $B22D: 8D E1 B4   STA $b4e1     
    $B230: B9 00 B4   LDA $b400,y   
    $B233: 8D E2 B4   STA $b4e2     
    $B236: BD 07 B5   LDA $b507,x   
    $B239: 4A         LSR a         
    $B23A: A8         TAY           
L_B23B:
    $B23B: 88         DEY           
    $B23C: 30 16      BMI $b254        ; → L_B254
    $B23E: 38         SEC           
    $B23F: AD E1 B4   LDA $b4e1     
    $B242: ED DF B4   SBC $b4df     
    $B245: 8D E1 B4   STA $b4e1     
    $B248: AD E2 B4   LDA $b4e2     
    $B24B: ED E0 B4   SBC $b4e0     
    $B24E: 8D E2 B4   STA $b4e2     
    $B251: 4C 3B B2   JMP $b23b        ; → L_B23B
L_B254:
    $B254: BD CC B4   LDA $b4cc,x   
    $B257: 29 1F      AND #$1f      
    $B259: C9 01      CMP #$01      
    $B25B: 90 2B      BCC $b288        ; → L_B288
    $B25D: BC E3 B4   LDY $b4e3,x   
L_B260:
    $B260: 88         DEY           
    $B261: 30 16      BMI $b279        ; → L_B279
    $B263: 18         CLC           
    $B264: AD E1 B4   LDA $b4e1     
    $B267: 6D DF B4   ADC $b4df     
    $B26A: 8D E1 B4   STA $b4e1     
    $B26D: AD E2 B4   LDA $b4e2     
    $B270: 6D E0 B4   ADC $b4e0     
    $B273: 8D E2 B4   STA $b4e2     
    $B276: 4C 60 B2   JMP $b260        ; → L_B260
L_B279:
    $B279: AC C2 B4   LDY $b4c2     
    $B27C: AD E1 B4   LDA $b4e1     
    $B27F: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $B282: AD E2 B4   LDA $b4e2     
    $B285: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_B288:
    $B288: AD 04 B5   LDA $b504     
    $B28B: 29 08      AND #$08      
    $B28D: F0 15      BEQ $b2a4        ; → L_B2A4
    $B28F: AC F6 B4   LDY $b4f6     
    $B292: B9 13 B5   LDA $b513,y   
    $B295: 6D DE B4   ADC $b4de     
    $B298: 99 13 B5   STA $b513,y   
    $B29B: AC C2 B4   LDY $b4c2     
    $B29E: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $B2A1: 4C 02 B3   JMP $b302        ; → L_B302
L_B2A4:
    $B2A4: AD DE B4   LDA $b4de     
    $B2A7: F0 59      BEQ $b302        ; → L_B302
    $B2A9: AC C2 B4   LDY $b4c2     
    $B2AC: 29 0F      AND #$0f      
    $B2AE: DE E6 B4   DEC $b4e6,x   
    $B2B1: 10 4F      BPL $b302        ; → L_B302
    $B2B3: 9D E6 B4   STA $b4e6,x   
    $B2B6: AD DE B4   LDA $b4de     
    $B2B9: 29 F0      AND #$f0      
    $B2BB: 8D 05 B5   STA $b505     
    $B2BE: BD E9 B4   LDA $b4e9,x   
    $B2C1: D0 1A      BNE $b2dd        ; → L_B2DD
    $B2C3: AD 05 B5   LDA $b505     
    $B2C6: 18         CLC           
    $B2C7: 7D 0D B5   ADC $b50d,x   
    $B2CA: 48         PHA           
    $B2CB: BD 10 B5   LDA $b510,x   
    $B2CE: 69 00      ADC #$00      
    $B2D0: 29 0F      AND #$0f      
    $B2D2: 48         PHA           
    $B2D3: C9 0E      CMP #$0e      
    $B2D5: D0 1D      BNE $b2f4        ; → L_B2F4
    $B2D7: FE E9 B4   INC $b4e9,x   
    $B2DA: 4C F4 B2   JMP $b2f4        ; → L_B2F4
L_B2DD:
    $B2DD: 38         SEC           
    $B2DE: BD 0D B5   LDA $b50d,x   
    $B2E1: ED 05 B5   SBC $b505     
    $B2E4: 48         PHA           
    $B2E5: BD 10 B5   LDA $b510,x   
    $B2E8: E9 00      SBC #$00      
    $B2EA: 29 0F      AND #$0f      
    $B2EC: 48         PHA           
    $B2ED: C9 08      CMP #$08      
    $B2EF: D0 03      BNE $b2f4        ; → L_B2F4
    $B2F1: DE E9 B4   DEC $b4e9,x   
L_B2F4:
    $B2F4: 68         PLA           
    $B2F5: 9D 10 B5   STA $b510,x   
    $B2F8: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $B2FB: 68         PLA           
    $B2FC: 9D 0D B5   STA $b50d,x   
    $B2FF: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
L_B302:
    $B302: AC C2 B4   LDY $b4c2     
    $B305: BD FE B4   LDA $b4fe,x   
    $B308: F0 41      BEQ $b34b        ; → L_B34B
    $B30A: 29 7E      AND #$7e      
    $B30C: 8D DB B4   STA $b4db     
    $B30F: BD FE B4   LDA $b4fe,x   
    $B312: 29 01      AND #$01      
    $B314: F0 1C      BEQ $b332        ; → L_B332
    $B316: 38         SEC           
    $B317: BD FB B4   LDA $b4fb,x   
    $B31A: ED DB B4   SBC $b4db     
    $B31D: 9D FB B4   STA $b4fb,x   
    $B320: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $B323: BD F8 B4   LDA $b4f8,x   
    $B326: FD 01 B5   SBC $b501,x   
    $B329: 9D F8 B4   STA $b4f8,x   
    $B32C: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $B32F: 4C 4B B3   JMP $b34b        ; → L_B34B
L_B332:
    $B332: 18         CLC           
    $B333: BD FB B4   LDA $b4fb,x   
    $B336: 6D DB B4   ADC $b4db     
    $B339: 9D FB B4   STA $b4fb,x   
    $B33C: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $B33F: BD F8 B4   LDA $b4f8,x   
    $B342: 7D 01 B5   ADC $b501,x   
    $B345: 9D F8 B4   STA $b4f8,x   
    $B348: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_B34B:
    $B34B: AD 04 B5   LDA $b504     
    $B34E: 29 01      AND #$01      
    $B350: F0 35      BEQ $b387        ; → L_B387
    $B352: BD F8 B4   LDA $b4f8,x   
    $B355: F0 30      BEQ $b387        ; → L_B387
    $B357: BD C9 B4   LDA $b4c9,x   
    $B35A: F0 2B      BEQ $b387        ; → L_B387
    $B35C: BD CC B4   LDA $b4cc,x   
    $B35F: 29 1F      AND #$1f      
    $B361: 38         SEC           
    $B362: E9 01      SBC #$01      
    $B364: DD C9 B4   CMP $b4c9,x   
    $B367: AC C2 B4   LDY $b4c2     
    $B36A: 90 10      BCC $b37c        ; → L_B37C
    $B36C: BD F8 B4   LDA $b4f8,x   
    $B36F: DE F8 B4   DEC $b4f8,x   
    $B372: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $B375: BD CF B4   LDA $b4cf,x   
    $B378: 29 FE      AND #$fe      
    $B37A: D0 08      BNE $b384        ; → L_B384
L_B37C:
    $B37C: BD F8 B4   LDA $b4f8,x   
    $B37F: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $B382: A9 80      LDA #$80      
L_B384:
    $B384: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_B387:
    $B387: AD 04 B5   LDA $b504     
    $B38A: 29 02      AND #$02      
    $B38C: F0 24      BEQ $b3b2        ; → L_B3B2
    $B38E: AD 06 B5   LDA $b506     
    $B391: 29 03      AND #$03      
    $B393: D0 1D      BNE $b3b2        ; → L_B3B2
    $B395: FE D2 B4   INC $b4d2,x   
    $B398: BD D2 B4   LDA $b4d2,x   
    $B39B: 0A         ASL a         
    $B39C: A8         TAY           
    $B39D: B9 FF B3   LDA $b3ff,y   
    $B3A0: 8D DA B4   STA $b4da     
    $B3A3: B9 00 B4   LDA $b400,y   
    $B3A6: AC C2 B4   LDY $b4c2     
    $B3A9: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $B3AC: AD DA B4   LDA $b4da     
    $B3AF: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_B3B2:
    $B3B2: AD 04 B5   LDA $b504     
    $B3B5: 29 04      AND #$04      
    $B3B7: F0 3F      BEQ $b3f8        ; → L_B3F8
    $B3B9: AD 04 B5   LDA $b504     
    $B3BC: 4A         LSR a         
    $B3BD: 4A         LSR a         
    $B3BE: 4A         LSR a         
    $B3BF: 4A         LSR a         
    $B3C0: 8D DA B3   STA $b3da     
    $B3C3: A0 02      LDY #$02      
    $B3C5: C9 0C      CMP #$0c      
    $B3C7: F0 02      BEQ $b3cb        ; → L_B3CB
    $B3C9: A0 01      LDY #$01      
L_B3CB:
    $B3CB: 8C D2 B3   STY $b3d2     
    $B3CE: AD 06 B5   LDA $b506     
    $B3D1: 29 02      AND #$02      
    $B3D3: D0 09      BNE $b3de        ; → L_B3DE
    $B3D5: BD D2 B4   LDA $b4d2,x   
    $B3D8: 38         SEC           
    $B3D9: E9 0C      SBC #$0c      
    $B3DB: 4C E1 B3   JMP $b3e1        ; → L_B3E1
L_B3DE:
    $B3DE: BD D2 B4   LDA $b4d2,x   
L_B3E1:
    $B3E1: 0A         ASL a         
    $B3E2: A8         TAY           
    $B3E3: B9 FF B3   LDA $b3ff,y   
    $B3E6: 8D DA B4   STA $b4da     
    $B3E9: B9 00 B4   LDA $b400,y   
    $B3EC: AC C2 B4   LDY $b4c2     
    $B3EF: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $B3F2: AD DA B4   LDA $b4da     
    $B3F5: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_B3F8:
    $B3F8: CA         DEX           
    $B3F9: 30 03      BMI $b3fe        ; → L_B3FE
    $B3FB: 4C 6E B0   JMP $b06e        ; → L_B06E
L_B3FE:
    $B3FE: 60         RTS           
; ----- data gap $B3FF-$BF0C (2830 bytes) -----

L_BF0D:
    $BF0D: A0 00      LDY #$00      
    $BF0F: AA         TAX           
    $BF10: BD ED B4   LDA $b4ed,x   
    $BF13: 8D F3 B4   STA $b4f3     
    $BF16: BD F0 B4   LDA $b4f0,x   
    $BF19: 8D 1C B0   STA $b01c     
    $BF1C: 8A         TXA           
    $BF1D: 0A         ASL a         
    $BF1E: 8D DB B4   STA $b4db     
    $BF21: 0A         ASL a         
    $BF22: 18         CLC           
    $BF23: 6D DB B4   ADC $b4db     
    $BF26: AA         TAX           
L_BF27:
    $BF27: BD E1 B5   LDA $b5e1,x   
    $BF2A: 99 DB B5   STA $b5db,y   
    $BF2D: E8         INX           
    $BF2E: C8         INY           
    $BF2F: C0 06      CPY #$06      
    $BF31: D0 F4      BNE $bf27        ; → L_BF27
    $BF33: A9 00      LDA #$00      
    $BF35: 8D 04 D4   STA $d404      ;V1_CTRL
    $BF38: 8D 0B D4   STA $d40b      ;V2_CTRL
    $BF3B: 8D 12 D4   STA $d412      ;V3_CTRL
    $BF3E: 8D 17 D4   STA $d417      ;RES_FILT
    $BF41: A9 0F      LDA #$0f      
    $BF43: 8D 18 D4   STA $d418      ;VOL
    $BF46: A9 40      LDA #$40      
    $BF48: 8D F7 B4   STA $b4f7     
    $BF4B: 60         RTS           
L_BF4C:
    $BF4C: A9 C0      LDA #$c0      
    $BF4E: 8D F7 B4   STA $b4f7     
    $BF51: 60         RTS           
; ----- data gap $BF52-$BFFF (174 bytes) -----

