; ============================================================================
; Rob Hubbard - The Master of Magic (1985 MAD/Mastertronic)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: /home/jtr/sidfinity/demo/hubbard/Master_of_Magic_original.sid
; Load:   $BFF8   Init: $BFF8   Play: $BFFB
; PSID:   3 subtunes, default subtune 1 (1-indexed; A=0 passed to init)
; Binary: $BFF8-$CBE7 (3056 bytes)
;
; Auto-traced 851 reachable code bytes from init+play. Hand annotation below
; was derived by combining static analysis with the Action Biker disassembly
; (same-era player; very similar topology).
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($BFF8 → $C000 → $CBC3): given subtune index in A, compute A*6,
;   copy 6 orderlist-pointer bytes from $C4B5+A*6 to $C4AF (lo:3 / hi:3),
;   set $C41D = $40 ("first-frame" sentinel). Returns. ALL voice-state
;   zeroing and SID silence is deferred to the first-frame branch in play.
;
; play ($BFFB → $C006): every frame.
;   1. INC $C426 (global frame counter).
;   2. BIT $C41D: bit 7 → end-of-song; bit 6 → first-frame setup.
;        - both clear → fall through to per-voice loop.
;        - bit 6 set / bit 7 clear → first-frame: zero voice state, clear
;          $C41D, JMP per-voice loop.
;        - bit 7 set → silence path: kill V1/V2/V3 ctrl, write VOL=$0F,
;          set $C41D=$80 (sticky end-of-song); subsequent frames take
;          BMI then BVC → JMP $C32E (RTS).
;   3. Per-voice loop ($C046..$C328) processes X = 2, 1, 0 (V3, V2, V1
;      — see $C3EF[X] = SID base offset = 0/7/14 stored at slots 0/1/2).
;
; PER-VOICE LOOP ($C046..$C328):
;   - Global tick divider $C41A reloads from $C41B when negative.
;   - Y=$C3F2 = current SID voice base offset (saved for SID writes).
;   - **Note-load is gated by ($C41A == $C41B)** at $C05A-$C060. On
;     frames where the divider hasn't wrapped to its reload value, jump
;     to $C17F (effects-only). Same one-frame-defer pattern as Action
;     Biker's $C3E7/$C3E8.
;   - DEC v_dur ($C3F9,X). If non-negative, JMP $C160 (sustain/HR).
;   - Else load next note from orderlist+pattern at $C07A.
;   - $FE in orderlist → JSR $C003 → JMP $CBE1 → mark song-end ($C41D=$C0)
;     → JMP $C32E (RTS this frame; subsequent frames silence path).
;   - $FF in orderlist → wrap (reset v_olpos, v_patpos to 0).
;
; STATE LAYOUT ($C3EF..$C426)  — voice-indexed slots use X=0..2
;   $C3EF,X = sid_offset (0/7/14 stored at $C3EF/$C3F0/$C3F1)
;   $C3F2   = current sid_offset (= $C3EF,X reloaded into Y on entry)
;   $C3F3,X = v_olpos
;   $C3F6,X = v_patpos
;   $C3F9,X = v_dur
;   $C3FC,X = v_flags  (raw pattern flags+dur byte)
;   $C3FF,X = v_ctrl   (saved inst.ctrl for HR/skydive)
;   $C402,X = v_pitch
;   $C405,X = v_inst
;   $C408   = gate_mask ($FF; tie clears bit 0 → $FE)
;   $C409   = saved flags byte for BIT-test of bit 7 (new inst) and bit 6 (tie)
;   $C40A   = freq_lo temp during note write
;   $C40B   = X save slot (saved before X is reused as inst*8 byte offset)
;   $C40C   = saved inst.ctrl
;   $C40D   = vib_depth countdown (mutated by ROR shift loop)
;   $C40E   = vib_period (also low-5=PWM speed, high-3=PWM step)
;   $C40F   = delta_lo (vibrato per-LFO-step delta, shifted)
;   $C410   = delta_hi (shifted)
;   $C411   = freq_lo accumulated through LFO scale
;   $C412   = freq_hi accumulated
;   $C413   = LFO triangle value (0..4)
;   $C414,X = v_pwm_step (countdown to next PWM step)
;   $C417,X = v_pwm_dir  (0=add, nonzero=subtract)
;   $C41A   = global tick divider
;   $C41B   = global tick reload
;   $C41C   = saved Y (= v_inst*8 byte offset into instrument table)
;   $C41D   = engine state byte (bit 7 = end-of-song, bit 6 = first-frame)
;   $C41E,X = v_fhi (saved freq_hi for skydive)
;   $C421,X = v_flo (saved freq_lo)
;   $C424   = fx_flags (current voice's instrument fx byte)
;   $C425   = pwm step size (high 3 bits of vib_period field)
;   $C426   = global frame counter
;
; FREQ TABLE: $C32F, 96 semitones × 2 bytes (lo, hi) — 192 bytes ending
;   at $C3EE. Standard Hubbard table starting $0116 ($C32F: 16 01 27 01...).
;
; INSTRUMENT TABLE: $C427, 8-byte records.
;   +0 pw_lo  +1 pw_hi  +2 ctrl  +3 AD  +4 SR
;   +5 vib_depth  +6 vib_period  +7 fx_flags
;   fx_flags bits:
;     bit 0 → drum/skydive (DEC freq_hi each frame after midpoint)
;     bit 1 → slow descent on long sustained notes (every other frame)
;     bit 2 → table-arp at +12 semitones (when (frame & 7) != 0)
;     bit 3 → simple PWM (pw_lo += vib_period each frame, no bounds)
;
; ORDERLIST POINTER TABLE: $C4B5, 3 subtunes × 6 bytes each (lo:3 / hi:3).
;   Subtune 0 (PSID #1): V1=$C519 V2=$C561 V3=$C611
;   Subtune 1 (PSID #2): V1=$C68E V2=$C693 V3=$C695
;   Subtune 2 (PSID #3): V1=$C699 V2=$C6A5 V3=$C6B2
;
; PATTERN POINTER TABLES:
;   pat_lo at $C4C7,Y  (~41 entries)
;   pat_hi at $C4F0,Y
;
; END-OF-SONG VOLUME FADE: at $C0BE the note-load path computes
;   A = $75 - $C3F5 (= $75 - v_olpos[slot 2 = V3]). If A < $0F use it,
;   else clamp to $0F. So full vol $0F until V3's orderlist position
;   exceeds $66 (102), then volume tapers to 0 by position $75 (117).
;   This is a song-end fade keyed off V3's progress.
;
; ============================================================================

; ======= init: =======
; A = subtune index (0-indexed; sidplayfp passes startSong-1).
init:
    $BFF8: 4C 00 C0   JMP $c000        ; → L_C000
; ======= play: =======
; Called every frame by sidplayfp.
play:
    $BFFB: 4C 06 C0   JMP $c006        ; → L_C006
; ----- data gap $BFFE-$BFFF (2 bytes) -----

; init trampoline.
L_C000:
    $C000: 4C C3 CB   JMP $cbc3        ; → L_CBC3   ; subtune setup
; song-end trampoline (called from $C087 when orderlist hits $FE).
sub_C003:
    $C003: 4C E1 CB   JMP $cbe1        ; → L_CBE1   ; mark song-end
L_C006:
    ; Frame counter +1, then dispatch on engine state byte $C41D:
    ;   bit 7 (N) = end-of-song; bit 6 (V) = first-frame setup.
    $C006: EE 26 C4   INC $c426        ; global frame counter
    $C009: 2C 1D C4   BIT $c41d
    $C00C: 30 1E      BMI $c02c        ; → L_C02C   ; end-of-song path
    $C00E: 50 36      BVC $c046        ; → L_C046   ; normal frame
    ; First-frame setup (bit 6 set, bit 7 clear). Zero voice state for
    ; all 3 slots, clear engine state byte, then proceed to per-voice loop.
    $C010: A9 00      LDA #$00
    $C012: 8D 26 C4   STA $c426        ; reset frame counter to 0
    $C015: A2 02      LDX #$02         ; loop X = 2..0
L_C017:
    $C017: 9D F3 C3   STA $c3f3,x      ; v_olpos,X  = 0
    $C01A: 9D F6 C3   STA $c3f6,x      ; v_patpos,X = 0
    $C01D: 9D F9 C3   STA $c3f9,x      ; v_dur,X    = 0
    $C020: 9D 02 C4   STA $c402,x      ; v_pitch,X  = 0
    $C023: CA         DEX
    $C024: 10 F1      BPL $c017        ; → L_C017
    $C026: 8D 1D C4   STA $c41d        ; clear engine state byte
    $C029: 4C 46 C0   JMP $c046        ; → L_C046   ; into per-voice loop
; End-of-song path. First entry has $C41D=$C0 (both bits set, written by
; $CBE1). BVC tests bit 6: clear → just RTS this frame; set → silence the
; SID and convert state byte to "sticky" $80 so future frames take only
; the BMI / BVC-clear path → JMP $C043 → RTS.
L_C02C:
    $C02C: 50 15      BVC $c043        ; → L_C043   ; sticky end: RTS
    $C02E: A9 00      LDA #$00
    $C030: 8D 04 D4   STA $d404        ;V1_CTRL    ; gate off all voices
    $C033: 8D 0B D4   STA $d40b        ;V2_CTRL
    $C036: 8D 12 D4   STA $d412        ;V3_CTRL
    $C039: A9 0F      LDA #$0f
    $C03B: 8D 18 D4   STA $d418        ;VOL        ; restore master vol
    $C03E: A9 80      LDA #$80
    $C040: 8D 1D C4   STA $c41d        ; engine state = $80 (sticky end)
L_C043:
    $C043: 4C 2E C3   JMP $c32e        ; → L_C32E   ; RTS
; ============================================================================
; PER-VOICE LOOP. X = voice slot (2=V3, 1=V2, 0=V1).
; ============================================================================
L_C046:
    $C046: A2 02      LDX #$02         ; start with slot 2 (= V3)
    ; Global tick divider. $C41A reloads from $C41B when it wraps neg.
    $C048: CE 1A C4   DEC $c41a
    $C04B: 10 06      BPL $c053        ; → L_C053   ; not yet wrapped
    $C04D: AD 1B C4   LDA $c41b
    $C050: 8D 1A C4   STA $c41a        ; $C41A = $C41B (reload)
L_C053:
    ; Per-voice SID base offset (0/7/14 → V1/V2/V3). Latched in $C3F2 +
    ; into Y (used directly by all SID writes as STA $D40x,Y).
    $C053: BD EF C3   LDA $c3ef,x      ; sid_offset for slot X
    $C056: 8D F2 C3   STA $c3f2        ; remember as Y for SID writes
    $C059: A8         TAY              ; Y = SID base offset
    ; **NOTE-LOAD GATE**: only run note-load when tick divider lands
    ; exactly on its reload value. Otherwise jump to effects-only path.
    ; Defers first-note-fire by one frame (matches Action Biker pattern).
    $C05A: AD 1A C4   LDA $c41a
    $C05D: CD 1B C4   CMP $c41b
    $C060: D0 15      BNE $c077        ; → L_C077   ; skip note-load
    ; Load orderlist pointer for voice X into ZP $FB/$FC.
    $C062: BD AF C4   LDA $c4af,x      ; orderlist ptr lo
    $C065: 85 FB      STA $fb
    $C067: BD B2 C4   LDA $c4b2,x      ; orderlist ptr hi
    $C06A: 85 FC      STA $fc
    ; v_dur,X -- ; if not negative, sustain/HR path (no new note).
    $C06C: DE F9 C3   DEC $c3f9,x      ; v_dur,X
    $C06F: 30 09      BMI $c07a        ; → L_C07A   ; expired: load next
    $C071: 4C 60 C1   JMP $c160        ; → L_C160   ; sustain/HR check
; ----- data gap $C074-$C076 (3 bytes) -----

; Effects-only entry (note-load gated off this frame).
L_C077:
    $C077: 4C 7F C1   JMP $c17f        ; → L_C17F
; Note-load: read pattern index from orderlist, handle FE/FF sentinels.
L_C07A:
    $C07A: BC F3 C3   LDY $c3f3,x      ; v_olpos,X
    $C07D: B1 FB      LDA ($fb),y      ; orderlist[v_olpos]
    $C07F: C9 FF      CMP #$ff
    $C081: F0 0A      BEQ $c08d        ; → L_C08D   ; $FF: wrap to start
    $C083: C9 FE      CMP #$fe
    $C085: D0 17      BNE $c09e        ; → L_C09E   ; normal pattern idx
    $C087: 20 03 C0   JSR $c003        ; → sub_C003 ; $FE: end-of-song
    $C08A: 4C 2E C3   JMP $c32e        ; → L_C32E   ; RTS
; Wrap orderlist (loop back to start): zero v_dur, v_olpos, v_patpos and
; retry the read.
L_C08D:
    $C08D: A9 00      LDA #$00
    $C08F: 9D F9 C3   STA $c3f9,x      ; v_dur,X    = 0
    $C092: 9D F3 C3   STA $c3f3,x      ; v_olpos,X  = 0
    $C095: 9D F6 C3   STA $c3f6,x      ; v_patpos,X = 0
    $C098: 4C 7A C0   JMP $c07a        ; → L_C07A   ; retry read
; ----- data gap $C09B-$C09D (3 bytes) -----

; Normal pattern load. A = pattern index. Look up pattern's address in
; (pat_lo[Y], pat_hi[Y]) tables at $C4C7 / $C4F0 → ZP $FD/$FE.
L_C09E:
    $C09E: A8         TAY              ; Y = pattern index
    $C09F: B9 C7 C4   LDA $c4c7,y      ; pat_lo[Y]
    $C0A2: 85 FD      STA $fd
    $C0A4: B9 F0 C4   LDA $c4f0,y      ; pat_hi[Y]
    $C0A7: 85 FE      STA $fe
    ; Y = byte offset within pattern (advances per byte consumed).
    $C0A9: BC F6 C3   LDY $c3f6,x      ; v_patpos,X
    ; Gate-mask defaults $FF (gate bit passes); cleared to $FE for ties.
    $C0AC: A9 FF      LDA #$ff
    $C0AE: 8D 08 C4   STA $c408        ; gate_mask = $FF
    ; First pattern byte: bit 7 = "new instrument follows", bit 6 = tie,
    ; bit 5 = "no_release" (preserved for HR check), bits 0-4 = duration.
    $C0B1: B1 FD      LDA ($fd),y      ; flags+dur byte
    $C0B3: 9D FC C3   STA $c3fc,x      ; v_flags,X
    $C0B6: 8D 09 C4   STA $c409        ; save for BIT below
    $C0B9: 29 1F      AND #$1f         ; duration only
    $C0BB: 9D F9 C3   STA $c3f9,x      ; v_dur,X = duration
    ; END-OF-SONG VOLUME FADE: full vol $0F until V3's orderlist position
    ; exceeds $66, then taper to 0 by position $75. (V3 = slot 2; this
    ; reads $C3F3,X with X=2 = $C3F5 directly.)
    $C0BE: A9 75      LDA #$75
    $C0C0: 38         SEC
    $C0C1: ED F5 C3   SBC $c3f5        ; A = $75 - v_olpos[V3]
    $C0C4: C9 0F      CMP #$0f
    $C0C6: 90 02      BCC $c0ca        ; → L_C0CA   ; A < $0F: write A
    $C0C8: A9 0F      LDA #$0f         ; else clamp to full vol
L_C0CA:
    $C0CA: 8D 18 D4   STA $d418        ;VOL
    ; BIT $C409: N = bit 7 (new inst), V = bit 6 (tie). Tie skips note
    ; fetch (just updates duration) and clears gate-mask bit 0.
    $C0CD: 2C 09 C4   BIT $c409
    $C0D0: 70 37      BVS $c109        ; → L_C109   ; tie: clear gate-mask
    $C0D2: FE F6 C3   INC $c3f6,x      ; advance v_patpos past flag byte
    $C0D5: AD 09 C4   LDA $c409
    $C0D8: 10 09      BPL $c0e3        ; → L_C0E3   ; same inst: skip
    ; New-instrument byte (bit 7 was set): consume it.
    $C0DA: C8         INY
    $C0DB: B1 FD      LDA ($fd),y      ; instrument byte
    $C0DD: 9D 05 C4   STA $c405,x      ; v_inst,X (raw)
    $C0E0: FE F6 C3   INC $c3f6,x      ; advance past inst byte
L_C0E3:
    ; Pitch byte. ASL × 1 because freq table at $C32F is 2-byte stride.
    $C0E3: C8         INY
    $C0E4: B1 FD      LDA ($fd),y      ; pitch byte
    $C0E6: 9D 02 C4   STA $c402,x      ; v_pitch,X
    $C0E9: 0A         ASL a            ; *2 for table stride
    $C0EA: A8         TAY              ; Y = freq table byte offset
    $C0EB: B9 2F C3   LDA $c32f,y      ; freq_lo[pitch]
    $C0EE: 8D 0A C4   STA $c40a        ; temp save
    $C0F1: B9 30 C3   LDA $c330,y      ; freq_hi[pitch]
    $C0F4: AC F2 C3   LDY $c3f2        ; Y = SID voice offset
    $C0F7: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $C0FA: 9D 1E C4   STA $c41e,x      ; v_fhi,X (for skydive)
    $C0FD: AD 0A C4   LDA $c40a
    $C100: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
    $C103: 9D 21 C4   STA $c421,x      ; v_flo,X
    $C106: 4C 0C C1   JMP $c10c        ; → L_C10C
; Tie/legato: clear gate-mask bit 0 so the ctrl write below ANDs the
; gate bit away (gate stays in whatever state previous note left it).
L_C109:
    $C109: CE 08 C4   DEC $c408        ; gate_mask $FF → $FE
; Write instrument table fields to SID for this voice.
; X is shifted up by 3 (×8) so it indexes into the instrument table.
L_C10C:
    $C10C: AC F2 C3   LDY $c3f2        ; Y = SID voice offset
    $C10F: BD 05 C4   LDA $c405,x      ; v_inst,X
    $C112: 8E 0B C4   STX $c40b        ; save voice X
    $C115: 0A         ASL a            ; inst * 2
    $C116: 0A         ASL a            ; inst * 4
    $C117: 0A         ASL a            ; inst * 8
    $C118: AA         TAX              ; X = byte offset into inst table
    $C119: BD 29 C4   LDA $c429,x      ; inst.ctrl
    $C11C: 8D 0C C4   STA $c40c        ; stash for later v_ctrl save
    $C11F: BD 29 C4   LDA $c429,x      ; ctrl again
    $C122: 2D 08 C4   AND $c408        ; AND gate-mask (tie clears bit 0)
    $C125: 99 04 D4   STA $d404,y      ;V1_CTRL,Y
    $C128: BD 27 C4   LDA $c427,x      ; inst.pw_lo
    $C12B: 99 02 D4   STA $d402,y      ;V1_PW_LO,Y
    $C12E: BD 28 C4   LDA $c428,x      ; inst.pw_hi
    $C131: 99 03 D4   STA $d403,y      ;V1_PW_HI,Y
    $C134: BD 2A C4   LDA $c42a,x      ; inst.AD
    $C137: 99 05 D4   STA $d405,y      ;V1_AD,Y
    $C13A: BD 2B C4   LDA $c42b,x      ; inst.SR
    $C13D: 99 06 D4   STA $d406,y      ;V1_SR,Y
    $C140: AE 0B C4   LDX $c40b        ; restore voice X
    $C143: AD 0C C4   LDA $c40c
    $C146: 9D FF C3   STA $c3ff,x      ; v_ctrl,X = raw inst.ctrl
    ; Advance v_patpos past the pitch byte. If next byte is $FF, the
    ; pattern ended: zero v_patpos and bump v_olpos.
    $C149: FE F6 C3   INC $c3f6,x
    $C14C: BC F6 C3   LDY $c3f6,x
    $C14F: B1 FD      LDA ($fd),y      ; peek next byte
    $C151: C9 FF      CMP #$ff
    $C153: D0 08      BNE $c15d        ; → L_C15D   ; pat continues
    $C155: A9 00      LDA #$00
    $C157: 9D F6 C3   STA $c3f6,x      ; v_patpos,X = 0
    $C15A: FE F3 C3   INC $c3f3,x      ; v_olpos,X += 1
L_C15D:
    $C15D: 4C 28 C3   JMP $c328        ; → L_C328   ; next voice
; ============================================================================
; SUSTAIN / HARD-RESTART check. Reached when DEC v_dur stayed >= 0.
; HR fires when (v_dur == 0) AND no_release flag clear: kill gate and
; zero AD/SR so the next note's gate-on retriggers cleanly.
; ============================================================================
L_C160:
    $C160: AC F2 C3   LDY $c3f2
    $C163: BD FC C3   LDA $c3fc,x      ; v_flags,X
    $C166: 29 20      AND #$20         ; bit 5 = no_release
    $C168: D0 15      BNE $c17f        ; → L_C17F   ; no_release: skip HR
    $C16A: BD F9 C3   LDA $c3f9,x      ; v_dur,X
    $C16D: D0 10      BNE $c17f        ; → L_C17F   ; still ticking
    ; v_dur == 0 and no_release clear: HR.
    $C16F: BD FF C3   LDA $c3ff,x      ; v_ctrl,X (saved inst.ctrl)
    $C172: 29 FE      AND #$fe         ; clear gate
    $C174: 99 04 D4   STA $d404,y      ;V1_CTRL,Y   ; gate off
    $C177: A9 00      LDA #$00
    $C179: 99 05 D4   STA $d405,y      ;V1_AD,Y     ; AD = 0
    $C17C: 99 06 D4   STA $d406,y      ;V1_SR,Y     ; SR = 0
; ============================================================================
; EFFECTS LOOP. Vibrato (triangle LFO) on inst's freq-table delta.
; ============================================================================
L_C17F:
    ; Index into instrument table: inst_idx * 8.
    $C17F: BD 05 C4   LDA $c405,x      ; v_inst,X
    $C182: 0A         ASL a
    $C183: 0A         ASL a
    $C184: 0A         ASL a
    $C185: A8         TAY              ; Y = inst byte offset
    $C186: 8C 1C C4   STY $c41c        ; remember inst offset
    ; Read instrument's effect parameters:
    ;   $C42E,Y = fx_flags     → $C424
    ;   $C42D,Y = vib_period   → $C40E
    ;   $C42C,Y = vib_depth    → $C40D
    $C189: B9 2E C4   LDA $c42e,y      ; inst.fx_flags
    $C18C: 8D 24 C4   STA $c424
    $C18F: B9 2D C4   LDA $c42d,y      ; inst.vib_period
    $C192: 8D 0E C4   STA $c40e
    $C195: B9 2C C4   LDA $c42c,y      ; inst.vib_depth
    $C198: 8D 0D C4   STA $c40d
    $C19B: F0 6F      BEQ $c20c        ; → L_C20C   ; depth=0: skip vib
    ; Triangle LFO from global frame counter $C426. AND $07 → 0..7;
    ; if >=4 EOR #$07 folds to 0..3..0 (triangle 0-1-2-3-3-2-1-0).
    $C19D: AD 26 C4   LDA $c426
    $C1A0: 29 07      AND #$07
    $C1A2: C9 04      CMP #$04
    $C1A4: 90 02      BCC $c1a8        ; → L_C1A8
    $C1A6: 49 07      EOR #$07         ; fold: 5→2, 6→1, 7→0
L_C1A8:
    $C1A8: 8D 13 C4   STA $c413        ; LFO triangle value
    ; Compute (freq[pitch+1] - freq[pitch]) >> vib_depth bits.
    $C1AB: BD 02 C4   LDA $c402,x      ; v_pitch,X
    $C1AE: 0A         ASL a            ; *2 for stride
    $C1AF: A8         TAY
    $C1B0: 38         SEC
    $C1B1: B9 31 C3   LDA $c331,y      ; freq_lo[pitch+1]
    $C1B4: F9 2F C3   SBC $c32f,y      ; - freq_lo[pitch]
    $C1B7: 8D 0F C4   STA $c40f        ; delta_lo
    $C1BA: B9 32 C3   LDA $c332,y      ; freq_hi[pitch+1]
    $C1BD: F9 30 C3   SBC $c330,y      ; - freq_hi[pitch]
L_C1C0:
    ; Right-shift delta by vib_depth bits (smaller depth = wider vibrato).
    $C1C0: 4A         LSR a
    $C1C1: 6E 0F C4   ROR $c40f
    $C1C4: CE 0D C4   DEC $c40d
    $C1C7: 10 F7      BPL $c1c0        ; → L_C1C0
    $C1C9: 8D 10 C4   STA $c410        ; delta_hi (shifted)
    ; Load base freq for current pitch.
    $C1CC: B9 2F C3   LDA $c32f,y      ; freq_lo[pitch]
    $C1CF: 8D 11 C4   STA $c411
    $C1D2: B9 30 C3   LDA $c330,y      ; freq_hi[pitch]
    $C1D5: 8D 12 C4   STA $c412
    ; Skip vibrato sum on very short notes (orig dur < 4).
    $C1D8: BD FC C3   LDA $c3fc,x      ; v_flags,X
    $C1DB: 29 1F      AND #$1f         ; duration
    $C1DD: C9 04      CMP #$04
    $C1DF: 90 1C      BCC $c1fd        ; → L_C1FD   ; short: skip
    $C1E1: AC 13 C4   LDY $c413        ; LFO value
L_C1E4:
    ; Accumulate delta LFO times into freq.
    $C1E4: 88         DEY
    $C1E5: 30 16      BMI $c1fd        ; → L_C1FD
    $C1E7: 18         CLC
    $C1E8: AD 11 C4   LDA $c411
    $C1EB: 6D 0F C4   ADC $c40f
    $C1EE: 8D 11 C4   STA $c411
    $C1F1: AD 12 C4   LDA $c412
    $C1F4: 6D 10 C4   ADC $c410
    $C1F7: 8D 12 C4   STA $c412
    $C1FA: 4C E4 C1   JMP $c1e4        ; → L_C1E4
L_C1FD:
    ; Write modulated freq to SID.
    $C1FD: AC F2 C3   LDY $c3f2
    $C200: AD 11 C4   LDA $c411
    $C203: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
    $C206: AD 12 C4   LDA $c412
    $C209: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
; ============================================================================
; PWM block. Two modes:
;   bit 3 of fx_flags set → simple PWM: pw_lo += vib_period each frame
;     (no bounds; for slow continuous sweeps).
;   bit 3 clear → standard Hubbard PWM with $08/$0E hardcoded bounds and
;     low-5/high-3 split of vib_period (speed/step).
; ============================================================================
L_C20C:
    $C20C: AD 24 C4   LDA $c424        ; fx_flags
    $C20F: 29 08      AND #$08         ; bit 3 = simple PWM mode
    $C211: F0 15      BEQ $c228        ; → L_C228   ; bit 3 clear: standard
    ; Simple PWM: pw_lo[Y] += vib_period each frame. ADC carry-in undefined
    ; — Hubbard relied on the prior AND #$08 leaving carry clear here.
    $C213: AC 1C C4   LDY $c41c        ; Y = inst byte offset
    $C216: B9 27 C4   LDA $c427,y      ; inst.pw_lo
    $C219: 6D 0E C4   ADC $c40e        ; + vib_period
    $C21C: 99 27 C4   STA $c427,y      ; store back to inst.pw_lo
    $C21F: AC F2 C3   LDY $c3f2        ; SID voice offset
    $C222: 99 02 D4   STA $d402,y      ;V1_PW_LO,Y
    $C225: 4C 8F C2   JMP $c28f        ; → L_C28F   ; → skydive
; Standard PWM: low 5 bits of vib_period = step interval, high 3 = step.
L_C228:
    $C228: AD 0E C4   LDA $c40e        ; vib_period
    $C22B: F0 62      BEQ $c28f        ; → L_C28F   ; period=0: skip
    $C22D: AC 1C C4   LDY $c41c        ; inst byte offset
    $C230: 29 1F      AND #$1f         ; low 5 bits = step interval
    $C232: DE 14 C4   DEC $c414,x      ; v_pwm_step,X
    $C235: 10 58      BPL $c28f        ; → L_C28F   ; not yet
    $C237: 9D 14 C4   STA $c414,x      ; reload step counter
    $C23A: AD 0E C4   LDA $c40e
    $C23D: 29 E0      AND #$e0         ; high 3 bits = step size
    $C23F: 8D 25 C4   STA $c425
    $C242: BD 17 C4   LDA $c417,x      ; v_pwm_dir,X
    $C245: D0 1A      BNE $c261        ; → L_C261   ; nonzero: subtract
    ; Direction = ADD: pw_lo += step.
    $C247: AD 25 C4   LDA $c425
    $C24A: 18         CLC
    $C24B: 79 27 C4   ADC $c427,y      ; pw_lo += step
    $C24E: 48         PHA
    $C24F: B9 28 C4   LDA $c428,y
    $C252: 69 00      ADC #$00         ; carry into pw_hi
    $C254: 29 0F      AND #$0f         ; pw_hi: 4 bits (12-bit PW)
    $C256: 48         PHA
    $C257: C9 0E      CMP #$0e         ; hit upper bound?
    $C259: D0 1D      BNE $c278        ; → L_C278
    $C25B: FE 17 C4   INC $c417,x      ; flip direction → SUB
    $C25E: 4C 78 C2   JMP $c278        ; → L_C278
; Direction = SUB: pw_lo -= step.
L_C261:
    $C261: 38         SEC
    $C262: B9 27 C4   LDA $c427,y
    $C265: ED 25 C4   SBC $c425        ; pw_lo -= step
    $C268: 48         PHA
    $C269: B9 28 C4   LDA $c428,y
    $C26C: E9 00      SBC #$00
    $C26E: 29 0F      AND #$0f
    $C270: 48         PHA
    $C271: C9 08      CMP #$08         ; hit lower bound?
    $C273: D0 03      BNE $c278        ; → L_C278
    $C275: DE 17 C4   DEC $c417,x      ; flip direction → ADD
L_C278:
    ; Write updated pw back to instrument record AND to SID.
    $C278: 8E 0B C4   STX $c40b        ; save voice X
    $C27B: AE F2 C3   LDX $c3f2        ; X = SID voice offset
    $C27E: 68         PLA
    $C27F: 99 28 C4   STA $c428,y      ; inst.pw_hi updated
    $C282: 9D 03 D4   STA $d403,x      ;V1_PW_HI,X
    $C285: 68         PLA
    $C286: 99 27 C4   STA $c427,y      ; inst.pw_lo updated
    $C289: 9D 02 D4   STA $d402,x      ;V1_PW_LO,X
    $C28C: AE 0B C4   LDX $c40b        ; restore voice X
; ============================================================================
; SKYDIVE / drum-sweep. Bit 0 of fx_flags = drum_freq_slide.
; Decrements freq_hi each frame after the note's midpoint, then silences
; with $80 ctrl (test-bit) for the note tail.
; ============================================================================
L_C28F:
    $C28F: AD 24 C4   LDA $c424        ; fx_flags
    $C292: 29 01      AND #$01         ; bit 0 = drum/skydive
    $C294: F0 35      BEQ $c2cb        ; → L_C2CB   ; flag clear: skip
    $C296: BD 1E C4   LDA $c41e,x      ; v_fhi,X
    $C299: F0 30      BEQ $c2cb        ; → L_C2CB   ; already 0: skip
    $C29B: BD F9 C3   LDA $c3f9,x      ; v_dur,X
    $C29E: F0 2B      BEQ $c2cb        ; → L_C2CB   ; v_dur=0: skip
    ; Frames-into-note = orig_dur - 1 - v_dur. If past midpoint (BCC),
    ; use slid freq as-is. Else decrement v_fhi and write the OLD value.
    $C2A0: BD FC C3   LDA $c3fc,x      ; v_flags,X
    $C2A3: 29 1F      AND #$1f         ; orig duration
    $C2A5: 38         SEC
    $C2A6: E9 01      SBC #$01         ; dur - 1
    $C2A8: DD F9 C3   CMP $c3f9,x      ; vs v_dur
    $C2AB: AC F2 C3   LDY $c3f2
    $C2AE: 90 10      BCC $c2c0        ; → L_C2C0
    $C2B0: BD 1E C4   LDA $c41e,x      ; pre-DEC v_fhi
    $C2B3: DE 1E C4   DEC $c41e,x      ; v_fhi -= 1
    $C2B6: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $C2B9: BD FF C3   LDA $c3ff,x      ; saved inst.ctrl
    $C2BC: 29 FE      AND #$fe         ; clear gate
    $C2BE: D0 08      BNE $c2c8        ; → L_C2C8
L_C2C0:
    $C2C0: BD 1E C4   LDA $c41e,x
    $C2C3: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $C2C6: A9 80      LDA #$80         ; test-bit (silence) at sweep end
L_C2C8:
    $C2C8: 99 04 D4   STA $d404,y      ;V1_CTRL,Y
; ============================================================================
; Bit 1 of fx_flags = SLOW DESCENT on long sustained notes. Decrements
; freq_hi every other frame while the note is in its tail. Active only when:
;   v_flags low5 (orig dur) >= $10 (long note),
;   v_dur < $12 (in tail),
;   frame counter & 1 == 1 (every other frame),
;   v_fhi > 0 (not bottomed out).
; ============================================================================
L_C2CB:
    $C2CB: AD 24 C4   LDA $c424
    $C2CE: 29 02      AND #$02
    $C2D0: F0 25      BEQ $c2f7        ; → L_C2F7   ; bit 1 clear: skip
    $C2D2: BD FC C3   LDA $c3fc,x      ; v_flags,X
    $C2D5: 29 1F      AND #$1f         ; orig dur
    $C2D7: C9 10      CMP #$10
    $C2D9: 90 1C      BCC $c2f7        ; → L_C2F7   ; dur < $10: skip
    $C2DB: BD F9 C3   LDA $c3f9,x      ; v_dur,X
    $C2DE: C9 12      CMP #$12
    $C2E0: B0 15      BCS $c2f7        ; → L_C2F7   ; v_dur >= $12: skip
    $C2E2: AD 26 C4   LDA $c426        ; frame counter
    $C2E5: 29 01      AND #$01
    $C2E7: F0 0E      BEQ $c2f7        ; → L_C2F7   ; even frame: skip
    $C2E9: BD 1E C4   LDA $c41e,x      ; v_fhi,X
    $C2EC: F0 09      BEQ $c2f7        ; → L_C2F7   ; already 0: skip
    $C2EE: DE 1E C4   DEC $c41e,x      ; v_fhi -= 1
    $C2F1: AC F2 C3   LDY $c3f2
    $C2F4: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
; ============================================================================
; Bit 2 of fx_flags = TABLE-ARP at +12 semitones (octave up).
; (frame & 7) == 0 → play base pitch; nonzero → play pitch+12.
; Reads freq from table and writes both freq_lo and freq_hi.
; ============================================================================
L_C2F7:
    $C2F7: AD 24 C4   LDA $c424
    $C2FA: 29 04      AND #$04
    $C2FC: F0 2A      BEQ $c328        ; → L_C328   ; bit 2 clear: skip
    $C2FE: AD 26 C4   LDA $c426
    $C301: 29 07      AND #$07
    $C303: F0 09      BEQ $c30e        ; → L_C30E   ; (frame&7)==0: base
    $C305: BD 02 C4   LDA $c402,x      ; v_pitch,X
    $C308: 18         CLC
    $C309: 69 0C      ADC #$0c         ; +12 semitones (octave up)
    $C30B: 4C 11 C3   JMP $c311        ; → L_C311
L_C30E:
    $C30E: BD 02 C4   LDA $c402,x      ; base pitch
L_C311:
    $C311: 0A         ASL a            ; *2 for table stride
    $C312: A8         TAY
    $C313: B9 2F C3   LDA $c32f,y      ; freq_lo[N]
    $C316: 8D 0A C4   STA $c40a
    $C319: B9 30 C3   LDA $c330,y      ; freq_hi[N]
    $C31C: AC F2 C3   LDY $c3f2
    $C31F: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $C322: AD 0A C4   LDA $c40a
    $C325: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
; Per-voice loop tail. DEX; if negative we've done all 3 voices, RTS.
; Else jump back to per-voice top at $C053.
L_C328:
    $C328: CA         DEX
    $C329: 30 03      BMI $c32e        ; → L_C32E   ; done
    $C32B: 4C 53 C0   JMP $c053        ; → L_C053   ; next voice
L_C32E:
    $C32E: 60         RTS
; ============================================================================
; FREQ TABLE: $C32F-$C3EE (96 semitones × 2 bytes, lo,hi). $0116, $0127, …
; STATE LAYOUT: $C3EF-$C426 (see header at top of file)
; INSTRUMENT TABLE: $C427+ (8-byte records)
; ORDERLIST POINTER TABLE: $C4B5-$C4C6 (3 subtunes × 6 bytes)
; PATTERN POINTER TABLES: pat_lo $C4C7+, pat_hi $C4F0+
; ORDERLISTS + PATTERNS follow ($C519+)
; ============================================================================
; ----- data gap $C32F-$CBC2 (2196 bytes) -----

; ============================================================================
; SUBTUNE SETUP. A = subtune index (0-indexed). Compute A*6, copy 6 bytes
; from $C4B5+A*6 to $C4AF (active orderlist pointers: lo:3 / hi:3), set
; "first-frame" sentinel ($C41D = $40). Returns; everything else is done
; lazily on first play frame.
; ============================================================================
L_CBC3:
    $CBC3: A0 00      LDY #$00
    $CBC5: 0A         ASL a            ; A*2
    $CBC6: 8D 0B C4   STA $c40b        ; stash A*2
    $CBC9: 0A         ASL a            ; A*4
    $CBCA: 18         CLC
    $CBCB: 6D 0B C4   ADC $c40b        ; A*4 + A*2 = A*6
    $CBCE: AA         TAX              ; X = subtune * 6
L_CBCF:
    $CBCF: BD B5 C4   LDA $c4b5,x      ; subtune ptr table[X]
    $CBD2: 99 AF C4   STA $c4af,y      ; → active orderlist ptrs
    $CBD5: E8         INX
    $CBD6: C8         INY
    $CBD7: C0 06      CPY #$06
    $CBD9: D0 F4      BNE $cbcf        ; → L_CBCF   ; copy 6 bytes
    $CBDB: A9 40      LDA #$40         ; "first-frame" sentinel
    $CBDD: 8D 1D C4   STA $c41d
    $CBE0: 60         RTS
; ============================================================================
; SONG-END. Sets $C41D = $C0 (bits 7+6 set). On the very next play frame
; the BMI takes the end-of-song path; BVC fails (bit 6 set) → SID silence
; + $C41D becomes $80 (sticky end). All subsequent frames take BMI then
; BVC clear → JMP $C043 → RTS.
; ============================================================================
L_CBE1:
    $CBE1: A9 C0      LDA #$c0
    $CBE3: 8D 1D C4   STA $c41d
    $CBE6: 60         RTS
; ----- data gap $CBE7-$CBE7 (1 bytes) -----
