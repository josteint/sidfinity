; ============================================================================
; Rob Hubbard - The Human Race (1985 Mastertronic)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: data/C64Music/MUSICIANS/H/Hubbard_Rob/Human_Race.sid
; Load:   $0980   Init: $0980   Play: $0986
; PSID:   5 subtune(s), default subtune 1 (1-indexed; A=0 passed to init)
; Binary: $0980-$1ADF (4448 bytes)
;
; Auto-traced 912 reachable code bytes from init+play. Layout commentary
; below was hand-derived by cross-referencing the seed against
; src/rh_decompile.py output and the existing Lean pipeline at
; pipelines/human_race/codegen/HumanRace/Codegen.lean (which encodes the
; engine semantics and achieves Grade A / 98.8% writelog match).
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($0980): two-byte trampoline. JMP $1A9C.
;
; $1A9C (real init): A = subtune (0-indexed).
;   - $0DCF (tick reload) := $0DD0,A    ; per-song tempo, A=0..4 -> [3,3,2,3,1]
;   - Copy 4 bytes of song pointers from $0E9F+A*4 to $0E9B..$0E9E
;     ($0E9B/$0E9C = V1 orderlist ptr lo/hi, $0E9D/$0E9E = V2 lo/hi)
;   - Silences V1 + V2 ctrl, sets vol = $0F.
;   - $0DD6 := $40 (song-state byte: bit 6 = "first-frame setup pending")
;   - RTS.
;   Note: only 2 voices participate. V3 is unused for music (used for SFX
;   in the host game; this PSID encodes 5 music subtunes).
;
; play ($0986): every frame.
;   1. INC $0DE2 (global frame counter).
;   2. BIT $0DD6: tests bits 7 and 6.
;      - bit 7 set -> end-of-song; BMI $09AC silences/RTS path
;      - bit 6 set -> FIRST FRAME; zero per-voice state, clear $0DD6
;      - both clear -> normal play; jump to per-voice loop at $09BE
;   3. Fall through to per-voice processing.
;
; End-of-song trampoline ($0983): JMP $1AC8 -> writes $C0 (bit 7 + bit 6)
; to $0DD6. Called via JSR from the orderlist scanner when it hits the
; $FE sentinel. On the NEXT frame, play sees bit 7 set, takes BMI $09AC,
; then BVS-falls-through (bit 6 also set) to silence V1+V2 ctrl and clear
; bit 6, leaving only bit 7 set. From then on every play call hits BMI
; $09AC -> BVC -> JMP $0CE3 (RTS).
;
; PER-VOICE PROCESSING ($09BE..$0CE0):
;   - X = $01 (loop runs voices 1 -> 0 in DEC order; only 2 voices).
;   - DEC $0DCE (per-frame tick counter, reload from $0DCF when negative).
;   - **Note-load is gated by ($0DCE == $0DCF)** at $09D2-$09D8.
;   - When the tick counter just reloaded, both halves of the equality
;     test pass and we enter the note-load path. Otherwise we JMP $0AF2
;     directly into the effects loop (sustain).
;   - $0DA4,X = SID register base for voice X (0=V1, 7=V2). Saved at
;     $0DA6 as the Y-index used by all SID writes (STA $D400,Y etc.).
;
; NOTE LOAD ($09F2..$0AD0):
;   - $0DA7,X = v_olpos,X (orderlist index). Read orderlist[olpos]:
;     - $FE -> song-end: JSR $0983 (sets bit 7+6), then JMP $0CE3 (RTS).
;     - $FF -> end-of-orderlist: zero v_dur/v_olpos/v_patpos, retry.
;     - else -> pattern index Y; load pat ptr from ($0EB3,Y / $0F02,Y).
;   - $0DAA,X = v_patpos,X (byte offset into pattern). Read flag/dur byte:
;       bit 7 = "follow-up byte present" (instrument OR slide effect)
;       bit 6 = "tie/legato" (gate stays in prior state)
;       bit 5 = "no_release" (keep envelope on until next note-on)
;       bits 0-4 = duration in ticks (stored into v_dur,X)
;   - If bit 7 set, the NEXT byte's high bit decides what it is:
;       byte[1] bit 7 CLEAR -> new instrument index, stored in v_inst,X ($0DB9,X)
;       byte[1] bit 7 SET   -> per-note freq-slide command, stored in
;                              $0DDD,X (consumed by the slide effect at $0C04)
;   - Pitch byte follows. Stored as v_pitch,X ($0DB6,X). Doubled (ASL) and
;     used as a byte offset into the freq table at $0CE4.
;   - SID writes: freq_lo/hi from table, then instrument fields from $0DE3
;     (8 bytes/inst: pw_lo, pw_hi, ctrl, AD, SR, vib_speed, pwm_speed,
;     fx_flags). Ctrl is AND'd with $0DBC (gate mask, $FE if tie, else $FF).
;   - Peek next pattern byte. If $FF -> v_patpos := 0, v_olpos += 1.
;
; SUSTAIN PATH ($0AD3..$0AF2):
;   - When the note's v_dur reached -1 (BMI taken into the JMP $0AD3 path),
;     this is the "final tick" of the note. If bit 5 ("no_release") is
;     clear AND v_dur == 0 (gate-off frame), clear ctrl's gate bit and
;     zero AD+SR registers. Otherwise just run effects.
;     [Reading note: the $0AD3 entry is reached on the SUSTAIN side from
;     $09E9 — i.e. v_dur was DEC'd and is still >= 0, so the gate-off
;     fires once when v_dur hits 0.]
;
; EFFECTS LOOP ($0AF2..$0CDD):
;   Read instrument fields into scratch:
;     $0DC1 = vib_speed (from inst+5, $0DE8,Y)
;     $0DC2 = pwm_speed (from inst+6, $0DE9,Y)
;     $0DE0 = fx_flags  (from inst+7, $0DEA,Y)   ; cache of inst.fx_flags
;
;   1. VIBRATO ($0B0E..$0B7C, gated by $0DC1 != 0):
;      - Triangle LFO from low 3 bits of frame counter: phase = frame & 7;
;        if phase >= 4, phase ^= 7 -> 0,1,2,3,3,2,1,0.
;      - delta = freq[pitch+1] - freq[pitch], shifted right $0DC1 times
;        (each ASR also feeds bit into $0DC3, building the 16-bit delta).
;      - Start = freq[pitch]; ADC delta for `phase` iterations (only when
;        v_flags & $1F >= 8, which is the "vibrato active above duration 8"
;        gate — short notes don't get vibrato).
;      - Write result to V_FREQ_LO/HI.
;
;   2. PWM / "SKYDIVE-PWM" ($0B7F..$0C01, gated by fx_flags bit 3):
;      bit 3 of $0DE0 SET -> "linear-sweep PW mode":
;        pw_lo += pwm_speed; ORA #$40 forces bit 6, write pw_lo. No bound
;        check, no direction flip. This produces the rising-saw PW timbre
;        Hubbard uses on certain leads.
;      bit 3 CLEAR -> "bounded bidirectional PWM" (Hubbard standard):
;        - $0DC8,X = per-voice period sub-counter; DEC each frame.
;        - When it underflows, reload to (pwm_speed & $1F) and apply step
;          (pwm_speed & $E0) to pw_lo/pw_hi.
;        - $0DCB,X = direction (0=up, nonzero=down).
;        - Direction flips when pw_hi reaches $0E (up->down) or $08
;          (down->up). These bounds are HARDCODED — see memory
;          reference_hubbard_pwm_bounds.md.
;        - Result is written to v_pw_lo/hi AND V_PW_LO/HI registers.
;        - Note: writes back to the instrument's own pw_lo/hi at $0DE3+Y,
;          so PW state MUTATES the instrument record (recovered each
;          play-instrument cycle).
;
;   3. PER-NOTE FREQ SLIDE ($0C04..$0C4B, gated by $0DDD,X != 0):
;      $0DDD,X encodes a slide command set up by the note loader:
;        - bit 0 = direction (0 = up via ADC, 1 = down via SBC)
;        - bits 1-6 (mask $7E) = magnitude
;      Applied to (v_fhi,v_flo) every frame and re-written to V_FREQ_LO/HI.
;
;   4. DOWNSLIDE / "PULSE FALL" ($0C4B..$0C84, gated by fx_flags bit 0):
;      For long notes (v_dur,X != 0 AND v_fhi,X != 0):
;        If (v_flags & $1F) - 1 < v_dur,X (i.e. before the final ticks):
;          DEC v_fhi,X, write OLD v_fhi to V_FREQ_HI.
;          If (v_ctrl,X & $FE) ALSO clear -> ALSO write noise ctrl $80.
;        Else: write OLD v_fhi to V_FREQ_HI and force ctrl := $80 (noise).
;      Used for Hubbard's "drum"/"explosion" decay effect.
;
;   5. SKYDIVE ($0C87..$0CAC, gated by fx_flags bit 1):
;      Long-note guard: only fires when (v_flags & $1F) >= $11.
;      Then on ODD frames only ($0DE2 & 1) AND when v_fhi,X != 0:
;        INC v_fhi,X; write the OLD v_fhi value to V_FREQ_HI.
;      Slow upward freq drift on sustained notes. (The Lean codegen
;      labels this "skydive" and corresponds to fx_flags bit 1; the
;      same flag is what extract/engine_model.py:189 sets as
;      `has_skydive = bool(flags & 2)`.)
;
;   6. DRUM ARPEGGIO / "OCTAVE-ARP" ($0CAC..$0CDD, gated by fx_flags bit 2):
;      If (frame & 7) != 0 -> arp_pitch = v_pitch + $0C (octave up)
;      else                 -> arp_pitch = v_pitch
;      Look up freq_table[arp_pitch*2] and write V_FREQ_LO/HI.
;      This is the snappy "drum hit" effect — one frame of base pitch
;      followed by 7 frames an octave up, every 8 frames.
;
; CONSEQUENCE FOR PIPELINE:
;   The flow matches Commando closely. Human Race-specific deltas
;   captured by the Lean codegen are:
;     - SKYDIVE block at fx_flags bit 1 (Commando lacks this — the slot
;       is unused there).
;     - PWM init: v_pwperiod = [0,1,$1D], v_pwdir = [1,0,0] (these come
;       from the binary at $0DC8..$0DCD, not from instrument records).
;     - HR threshold = 1 (note-load gating differs from Commando's = 0).
;
; FREQ TABLE: $0CE4, 96+ semitone entries packed as (lo[i], hi[i]) with
; 2-byte stride. Indexed by pitch*2 from v_pitch. Extends slightly past
; the obvious 96-semitone span because drum-arp adds 12 to high-pitch
; notes, requiring +24 bytes of headroom (so 96..107 semitones must
; have valid entries).
;
; INSTRUMENT TABLE: $0DE3, 8-byte records x 23 instruments ($0DE3..$0E8A).
;   offset 0: pw_lo  1: pw_hi  2: ctrl  3: AD  4: SR
;          5: vib_speed (right-shift count for vibrato delta)
;          6: pwm_speed (low 5 bits = period reload, high 3 bits = step)
;          7: fx_flags
;            bit 0 = downslide / drum-decay enable
;            bit 1 = skydive (slow upward freq drift on long notes)
;            bit 2 = drum arpeggio (octave snap on frame & 7)
;            bit 3 = PW mode (0 = bounded PWM, 1 = linear-sweep PW)
;
; SONG TABLE: $0E9F, 4 bytes/song x 5 songs:
;   +0/+1: V1 orderlist ptr lo/hi
;   +2/+3: V2 orderlist ptr lo/hi
;   (V3 unused — only 2 voices participate in any subtune.)
;
; SEQUENCE/PATTERN POINTERS: split lo/hi tables at $0EB3 (lo) and
; $0F02 (hi), 79 sequences. Pattern bytes start at $1162.
;
; PER-SONG TEMPO: $0DD0, 5 bytes: [3, 3, 2, 3, 1] (tick reload values).
;
; ============================================================================

; ======= init: =======
; A holds subtune (0-indexed). Two-byte trampoline to the real init.
init:
    $0980: 4C 9C 1A   JMP $1a9c        ; → L_1A9C   ; real init

; song_end_trampoline: orderlist hit $FE; trips end-of-song state.
sub_0983:
    $0983: 4C C8 1A   JMP $1ac8        ; → L_1AC8

; ======= play: =======
; Called every frame by sidplayfp. No prologue tick divider here — Human
; Race uses the per-voice $0DCE tick counter instead of the dual
; sub-frame/tick scheme Action Biker employs.
play:
    ; Global frame counter +1.
    $0986: EE E2 0D   INC $0de2
    ; $0DD6 holds song state: bit 7 = end-of-song, bit 6 = first-frame
    ; (set by init to $40, set by song-end to $C0). BIT moves bit 7 to
    ; N flag, bit 6 to V flag.
    $0989: 2C D6 0D   BIT $0dd6
    $098C: 30 1E      BMI $09ac        ; → L_09AC   ; end-of-song path
    $098E: 50 2E      BVC $09be        ; → L_09BE   ; normal frame
    ; First-frame setup: zero per-voice state arrays for X=1..0 (only
    ; 2 voices), then clear $0DD6 and proceed.
    $0990: A9 00      LDA #$00
    $0992: 8D E2 0D   STA $0de2        ; zero frame counter
    $0995: A2 01      LDX #$01         ; X = 1 (last voice index)
L_0997:
    $0997: 9D A7 0D   STA $0da7,x      ; v_olpos,x  = 0
    $099A: 9D AA 0D   STA $0daa,x      ; v_patpos,x = 0
    $099D: 9D AD 0D   STA $0dad,x      ; v_dur,x    = 0
    $09A0: 9D B6 0D   STA $0db6,x      ; v_pitch,x  = 0
    $09A3: CA         DEX
    $09A4: 10 F1      BPL $0997        ; → L_0997   ; loop X=1,0
    $09A6: 8D D6 0D   STA $0dd6        ; $0DD6 := 0 (clear all state bits)
    $09A9: 4C BE 09   JMP $09be        ; → L_09BE
L_09AC:
    ; End-of-song path. On the FIRST entry (state = $C0), BVC falls
    ; through to silence V1+V2 ctrl and clear bit 6 (leaving only bit 7).
    ; On subsequent entries (state = $80), BVC is taken and JMP $0CE3
    ; returns immediately.
    $09AC: 50 0D      BVC $09bb        ; → L_09BB   ; already silenced
    $09AE: A9 00      LDA #$00
    $09B0: 8D 04 D4   STA $d404        ;V1_CTRL
    $09B3: 8D 0B D4   STA $d40b        ;V2_CTRL
    $09B6: A9 80      LDA #$80         ; clear bit 6, keep bit 7
    $09B8: 8D D6 0D   STA $0dd6
L_09BB:
    $09BB: 4C E3 0C   JMP $0ce3        ; → L_0CE3   ; RTS
L_09BE:
    ; Per-voice loop entry. X = 1 means we process V2 first then V1.
    ; (Voices are mostly symmetric; the DEC X at the loop tail walks
    ; backwards through the 2-voice array.)
    $09BE: A2 01      LDX #$01
    ; Tick divider: $0DCE reloads from $0DCF when it goes negative.
    ; $0DCF was set by init from the per-song table at $0DD0.
    $09C0: CE CE 0D   DEC $0dce
    $09C3: 10 06      BPL $09cb        ; → L_09CB
    $09C5: AD CF 0D   LDA $0dcf
    $09C8: 8D CE 0D   STA $0dce
L_09CB:
    ; Per-voice SID-base lookup. $0DA4,X holds the SID register offset
    ; for voice X (0=V1, 7=V2). Stashed at $0DA6 as the Y-index used
    ; by later writes (STA $D400,Y etc.).
    $09CB: BD A4 0D   LDA $0da4,x      ; SID voice offset (0, 7)
    $09CE: 8D A6 0D   STA $0da6
    $09D1: A8         TAY              ; Y = SID base offset
    ; **NOTE-LOAD GATE**: only run note-load when the tick counter just
    ; reloaded (CMP $0DCF after the BPL above means both equal the
    ; reload value). Otherwise skip to the effects-only path. This is
    ; the equivalent of Action Biker's $C040/$C046 gate.
    $09D2: AD CE 0D   LDA $0dce
    $09D5: CD CF 0D   CMP $0dcf
    $09D8: D0 15      BNE $09ef        ; → L_09EF   ; effects-only
    ; Note-load path: $0E9B,X / $0E9D,X hold the per-voice orderlist
    ; pointer (lo/hi). Loaded into ZP $FB/$FC for indirect addressing.
    $09DA: BD 9B 0E   LDA $0e9b,x      ; orderlist ptr lo
    $09DD: 85 FB      STA $fb
    $09DF: BD 9D 0E   LDA $0e9d,x      ; orderlist ptr hi
    $09E2: 85 FC      STA $fc
    ; $0DAD,X = v_dur,X. DEC; if hit -1, load next note. Else fall through
    ; to the sustain/effects path via JMP $0AD3.
    $09E4: DE AD 0D   DEC $0dad,x      ; v_dur,x
    $09E7: 30 09      BMI $09f2        ; → L_09F2   ; expired: load next
    $09E9: 4C D3 0A   JMP $0ad3        ; → L_0AD3   ; sustain current
; ----- data gap $09EC-$09EE (3 bytes) -----

; Effects-only path: tick counter hadn't reloaded yet. Skip pattern
; advancement, run effects on current state.
L_09EF:
    $09EF: 4C F2 0A   JMP $0af2        ; → L_0AF2
; Note-load entry. ($FB):Y points at the orderlist; $0DA7,X = current
; orderlist position. Reads pattern index, handles $FE (song-end) and
; $FF (orderlist-loop) sentinels.
L_09F2:
    $09F2: BC A7 0D   LDY $0da7,x      ; v_olpos,x
    $09F5: B1 FB      LDA ($fb),y      ; orderlist[v_olpos]
    $09F7: C9 FE      CMP #$fe         ; song-end sentinel
    $09F9: D0 03      BNE $09fe        ; → L_09FE
    $09FB: 4C 83 09   JMP $0983        ; → sub_0983 ; song-end: tail-call
L_09FE:
    $09FE: C9 FF      CMP #$ff         ; orderlist-loop sentinel
    $0A00: D0 11      BNE $0a13        ; → L_0A13   ; normal: load patt
    ; Restart orderlist (loop): zero v_dur, v_olpos, v_patpos and retry.
    $0A02: A9 00      LDA #$00
    $0A04: 9D AD 0D   STA $0dad,x      ; v_dur,x    = 0
    $0A07: 9D A7 0D   STA $0da7,x      ; v_olpos,x  = 0
    $0A0A: 9D AA 0D   STA $0daa,x      ; v_patpos,x = 0
    $0A0D: 4C F2 09   JMP $09f2        ; → L_09F2   ; retry from start
; ----- data gap $0A10-$0A12 (3 bytes) -----

; Normal pattern load. A holds pattern index from orderlist. Look up
; pattern's start address via the ($0EB3, $0F02) lo/hi tables.
L_0A13:
    $0A13: A8         TAY              ; Y = pattern index
    $0A14: B9 B3 0E   LDA $0eb3,y      ; pat_lo[Y]
    $0A17: 85 FD      STA $fd          ; ZP $FD = pat_lo
    $0A19: B9 02 0F   LDA $0f02,y      ; pat_hi[Y]
    $0A1C: 85 FE      STA $fe          ; ZP $FE = pat_hi
    ; Reset per-note slide command to "no slide" (the per-note slide
    ; effect at $0C04 reads from $0DDD,X — if the new pattern byte
    ; doesn't override this, it stays 0).
    $0A1E: A9 00      LDA #$00
    $0A20: 9D DD 0D   STA $0ddd,x      ; v_slide,x = 0 (no slide)
    ; Y = byte offset within the pattern (advances per byte consumed).
    $0A23: BC AA 0D   LDY $0daa,x      ; v_patpos,x
    ; $0DBC = gate-mask. Default $FF (gate bit passes); DEC'd to $FE
    ; for tie/legato notes via $0A7C below.
    $0A26: A9 FF      LDA #$ff
    $0A28: 8D BC 0D   STA $0dbc
    ; First pattern byte = (flags<<5) | duration (low 5 bits).
    ;   bit 7 = "follow-up byte present" (inst OR slide; BPL test below)
    ;   bit 6 = "tie/legato" (BVS test → keep gate off)
    ;   bit 5 = "no_release" (preserved for sustain logic)
    ;   bits 0-4 = duration in ticks
    $0A2B: B1 FD      LDA ($fd),y      ; A = pattern flag+dur byte
    $0A2D: 9D B0 0D   STA $0db0,x      ; v_flags,x = raw byte
    $0A30: 8D BD 0D   STA $0dbd        ; save for BIT test below
    $0A33: 29 1F      AND #$1f         ; duration only
    $0A35: 9D AD 0D   STA $0dad,x      ; v_dur,x = duration
    ; BIT $0DBD: N = bit 7 (follow-up), V = bit 6 (tie). Tie path jumps
    ; to $0A7C without advancing patpos (so the next note-load re-reads
    ; the same byte; effectively the duration is the only thing updated).
    $0A38: 2C BD 0D   BIT $0dbd
    $0A3B: 70 3F      BVS $0a7c        ; → L_0A7C   ; tie: clear gate mask
    $0A3D: FE AA 0D   INC $0daa,x      ; advance v_patpos past flag byte
    $0A40: AD BD 0D   LDA $0dbd
    $0A43: 10 11      BPL $0a56        ; → L_0A56   ; no follow-up byte
    ; Follow-up byte present. Bit 7 of the BYTE decides what it is:
    ;   BPL (bit 7 clear) → instrument index → $0DB9,X
    ;   BMI (bit 7 set)   → slide command   → $0DDD,X
    $0A45: C8         INY
    $0A46: B1 FD      LDA ($fd),y      ; follow-up byte
    $0A48: 10 06      BPL $0a50        ; → L_0A50   ; instrument byte
    $0A4A: 9D DD 0D   STA $0ddd,x      ; v_slide,x = slide command
    $0A4D: 4C 53 0A   JMP $0a53        ; → L_0A53
L_0A50:
    $0A50: 9D B9 0D   STA $0db9,x      ; v_inst,x  = instrument index
L_0A53:
    $0A53: FE AA 0D   INC $0daa,x      ; advance past follow-up byte
L_0A56:
    ; Pitch byte. Doubled (ASL) because freq table at $0CE4 is 2-byte
    ; entries per semitone.
    $0A56: C8         INY
    $0A57: B1 FD      LDA ($fd),y      ; pitch byte (0..95)
    $0A59: 9D B6 0D   STA $0db6,x      ; v_pitch,x
    $0A5C: 0A         ASL a            ; *2 for table stride
    $0A5D: A8         TAY              ; Y = byte offset into freq table
    $0A5E: B9 E4 0C   LDA $0ce4,y      ; freq_lo[pitch]
    $0A61: 8D BE 0D   STA $0dbe        ; scratch save
    $0A64: B9 E5 0C   LDA $0ce5,y      ; freq_hi[pitch]
    $0A67: AC A6 0D   LDY $0da6        ; Y = SID voice offset
    $0A6A: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $0A6D: 9D D7 0D   STA $0dd7,x      ; v_fhi,x (for slide/skydive)
    $0A70: AD BE 0D   LDA $0dbe
    $0A73: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
    $0A76: 9D DA 0D   STA $0dda,x      ; v_flo,x (for slide)
    $0A79: 4C 7F 0A   JMP $0a7f        ; → L_0A7F
L_0A7C:
    ; Tie/legato: clear gate-mask bit 0 so the ctrl write below AND-s
    ; away the gate bit. The previous note's freq/inst stay in place.
    $0A7C: CE BC 0D   DEC $0dbc        ; $0DBC $FF → $FE (clears bit 0)
L_0A7F:
    ; Write instrument table fields to the SID for this voice.
    ; Instrument table at $0DE3; each record is 8 bytes:
    ;   +0 pw_lo  +1 pw_hi  +2 ctrl  +3 AD  +4 SR
    ;   +5 vib_sp +6 pwm_sp +7 fx_flags
    $0A7F: AC A6 0D   LDY $0da6        ; Y = SID voice offset (0, 7)
    $0A82: BD B9 0D   LDA $0db9,x      ; v_inst,x
    $0A85: 8E BF 0D   STX $0dbf        ; save X (voice index)
    $0A88: 0A         ASL a            ; inst * 2
    $0A89: 0A         ASL a            ; inst * 4
    $0A8A: 0A         ASL a            ; inst * 8
    $0A8B: AA         TAX              ; X = byte offset into inst table
    $0A8C: BD E5 0D   LDA $0de5,x      ; inst.ctrl
    $0A8F: 8D C0 0D   STA $0dc0        ; stash raw ctrl
    $0A92: BD E5 0D   LDA $0de5,x      ; ctrl again
    $0A95: 2D BC 0D   AND $0dbc        ; AND gate-mask (tie clears bit 0)
    $0A98: 99 04 D4   STA $d404,y      ;V1_CTRL,Y
    $0A9B: BD E3 0D   LDA $0de3,x      ; inst.pw_lo
    $0A9E: 99 02 D4   STA $d402,y      ;V1_PW_LO,Y
    $0AA1: BD E4 0D   LDA $0de4,x      ; inst.pw_hi
    $0AA4: 99 03 D4   STA $d403,y      ;V1_PW_HI,Y
    $0AA7: BD E6 0D   LDA $0de6,x      ; inst.AD
    $0AAA: 99 05 D4   STA $d405,y      ;V1_AD,Y
    $0AAD: BD E7 0D   LDA $0de7,x      ; inst.SR
    $0AB0: 99 06 D4   STA $d406,y      ;V1_SR,Y
    $0AB3: AE BF 0D   LDX $0dbf        ; restore X (voice)
    $0AB6: AD C0 0D   LDA $0dc0
    $0AB9: 9D B3 0D   STA $0db3,x      ; v_ctrl,x = raw inst.ctrl
    ; Advance v_patpos past the pitch byte. If the next byte is $FF,
    ; the pattern ended: zero v_patpos and bump v_olpos.
    $0ABC: FE AA 0D   INC $0daa,x
    $0ABF: BC AA 0D   LDY $0daa,x
    $0AC2: B1 FD      LDA ($fd),y      ; peek next byte
    $0AC4: C9 FF      CMP #$ff
    $0AC6: D0 08      BNE $0ad0        ; → L_0AD0   ; not end-of-pat
    $0AC8: A9 00      LDA #$00
    $0ACA: 9D AA 0D   STA $0daa,x      ; v_patpos,x = 0
    $0ACD: FE A7 0D   INC $0da7,x      ; v_olpos,x  += 1
L_0AD0:
    $0AD0: 4C DD 0C   JMP $0cdd        ; → L_0CDD   ; tail of voice loop

; SUSTAIN path. Entered via JMP $0AD3 from $09E9 (v_dur was DEC'd and
; remained >= 0). Handles the "final tick" gate-off behavior, then
; falls through into the effects loop.
L_0AD3:
    $0AD3: AC A6 0D   LDY $0da6        ; Y = SID voice offset
    $0AD6: BD B0 0D   LDA $0db0,x      ; v_flags,x (raw flags byte)
    $0AD9: 29 20      AND #$20         ; bit 5 = "no_release"
    $0ADB: D0 15      BNE $0af2        ; → L_0AF2   ; no_release: keep env
    $0ADD: BD AD 0D   LDA $0dad,x      ; v_dur,x (current, post-DEC)
    $0AE0: D0 10      BNE $0af2        ; → L_0AF2   ; not yet at gate-off
    ; Final tick (v_dur just reached 0). Gate off + zero ADSR.
    $0AE2: BD B3 0D   LDA $0db3,x      ; saved ctrl
    $0AE5: 29 FE      AND #$fe         ; clear gate bit
    $0AE7: 99 04 D4   STA $d404,y      ;V1_CTRL,Y   ; gate off
    $0AEA: A9 00      LDA #$00
    $0AEC: 99 05 D4   STA $d405,y      ;V1_AD,Y     ; envelope off
    $0AEF: 99 06 D4   STA $d406,y      ;V1_SR,Y

; ============================================================================
; EFFECTS LOOP. Reads inst+5/+6/+7 (vib_speed, pwm_speed, fx_flags) into
; scratch, then runs the 6 effect blocks in order.
; ============================================================================
L_0AF2:
    ; Y = inst*8 (re-derive from v_inst,X since the post-note-load path
    ; clobbered X with the inst*8 value; the sustain path enters with
    ; Y holding SID base, so we recompute).
    $0AF2: BD B9 0D   LDA $0db9,x      ; v_inst,x
    $0AF5: 0A         ASL a
    $0AF6: 0A         ASL a
    $0AF7: 0A         ASL a
    $0AF8: A8         TAY              ; Y = inst * 8
    $0AF9: 8C D5 0D   STY $0dd5        ; save inst*8 for later effects
    $0AFC: B9 EA 0D   LDA $0dea,y      ; inst.fx_flags
    $0AFF: 8D E0 0D   STA $0de0
    $0B02: B9 E9 0D   LDA $0de9,y      ; inst.pwm_speed
    $0B05: 8D C2 0D   STA $0dc2
    $0B08: B9 E8 0D   LDA $0de8,y      ; inst.vib_speed
    $0B0B: 8D C1 0D   STA $0dc1
    ; ------------------------------------------------------------------
    ; 1. VIBRATO ($0B0E..$0B7C): gated by inst.vib_speed != 0.
    ; ------------------------------------------------------------------
    $0B0E: F0 6F      BEQ $0b7f        ; → L_0B7F   ; vib_speed = 0
    ; Triangle phase from low 3 bits of frame counter: 0,1,2,3,4,5,6,7
    ; with the upper half mirrored to 0,1,2,3,3,2,1,0.
    $0B10: AD E2 0D   LDA $0de2        ; frame counter
    $0B13: 29 07      AND #$07         ; & 7
    $0B15: C9 04      CMP #$04
    $0B17: 90 02      BCC $0b1b        ; → L_0B1B   ; phase < 4: keep
    $0B19: 49 07      EOR #$07         ; phase >= 4: mirror
L_0B1B:
    $0B1B: 8D C7 0D   STA $0dc7        ; $0DC7 = vibrato phase
    ; delta = freq[pitch+1] - freq[pitch] (16-bit) shifted right vib_speed
    ; times. Each LSR/ROR feeds bit into ($0DC4:$0DC3).
    $0B1E: BD B6 0D   LDA $0db6,x      ; v_pitch,x
    $0B21: 0A         ASL a
    $0B22: A8         TAY              ; Y = pitch*2
    $0B23: 38         SEC
    $0B24: B9 E6 0C   LDA $0ce6,y      ; freq_lo[pitch+1]
    $0B27: F9 E4 0C   SBC $0ce4,y      ; - freq_lo[pitch]
    $0B2A: 8D C3 0D   STA $0dc3        ; delta_lo
    $0B2D: B9 E7 0C   LDA $0ce7,y      ; freq_hi[pitch+1]
    $0B30: F9 E5 0C   SBC $0ce5,y      ; - freq_hi[pitch]
L_0B33:
    $0B33: 4A         LSR a
    $0B34: 6E C3 0D   ROR $0dc3
    $0B37: CE C1 0D   DEC $0dc1        ; counter (was vib_speed)
    $0B3A: 10 F7      BPL $0b33        ; → L_0B33   ; shift vib_speed times
    $0B3C: 8D C4 0D   STA $0dc4        ; delta_hi
    ; Start from base freq[pitch], then ADC delta `phase` times.
    $0B3F: B9 E4 0C   LDA $0ce4,y      ; freq_lo[pitch]
    $0B42: 8D C5 0D   STA $0dc5        ; vib_lo
    $0B45: B9 E5 0C   LDA $0ce5,y      ; freq_hi[pitch]
    $0B48: 8D C6 0D   STA $0dc6        ; vib_hi
    ; Vibrato amplitude gate: only apply when (v_flags & $1F) >= 8.
    ; Short notes (dur 0..7) get plain freq[pitch] with no vibrato.
    $0B4B: BD B0 0D   LDA $0db0,x      ; v_flags,x
    $0B4E: 29 1F      AND #$1f
    $0B50: C9 08      CMP #$08
    $0B52: 90 1C      BCC $0b70        ; → L_0B70   ; short: skip ADC loop
    $0B54: AC C7 0D   LDY $0dc7        ; Y = phase (0..3)
L_0B57:
    $0B57: 88         DEY
    $0B58: 30 16      BMI $0b70        ; → L_0B70
    $0B5A: 18         CLC
    $0B5B: AD C5 0D   LDA $0dc5
    $0B5E: 6D C3 0D   ADC $0dc3
    $0B61: 8D C5 0D   STA $0dc5
    $0B64: AD C6 0D   LDA $0dc6
    $0B67: 6D C4 0D   ADC $0dc4
    $0B6A: 8D C6 0D   STA $0dc6
    $0B6D: 4C 57 0B   JMP $0b57        ; → L_0B57
L_0B70:
    $0B70: AC A6 0D   LDY $0da6
    $0B73: AD C5 0D   LDA $0dc5
    $0B76: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
    $0B79: AD C6 0D   LDA $0dc6
    $0B7C: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
; ----------------------------------------------------------------------
; 2. PWM / linear-sweep PW (gated by fx_flags bit 3).
;    bit 3 SET   -> linear sweep: pw_lo += pwm_speed; ORA #$40; STA.
;    bit 3 CLEAR -> bounded bidirectional PWM (Hubbard standard).
; ----------------------------------------------------------------------
L_0B7F:
    $0B7F: AD E0 0D   LDA $0de0        ; fx_flags
    $0B82: 29 08      AND #$08         ; bit 3 = PW mode select
    $0B84: F0 17      BEQ $0b9d        ; → L_0B9D   ; clear: bounded PWM
    ; Linear sweep PW (fx_flags bit 3 SET).
    $0B86: AC D5 0D   LDY $0dd5        ; Y = inst*8
    $0B89: B9 E3 0D   LDA $0de3,y      ; inst.pw_lo
    $0B8C: 6D C2 0D   ADC $0dc2        ; + pwm_speed (C set/cleared from
                                       ;   vibrato's last ADC — known
                                       ;   Hubbard quirk: vibrato carry
                                       ;   bleeds into PWM step)
    $0B8F: 09 40      ORA #$40         ; force bit 6 (PW>=$40 always)
    $0B91: 99 E3 0D   STA $0de3,y      ; write back to inst.pw_lo (mutates!)
    $0B94: AC A6 0D   LDY $0da6
    $0B97: 99 02 D4   STA $d402,y      ;V1_PW_LO,Y
    $0B9A: 4C 04 0C   JMP $0c04        ; → L_0C04
; Bounded bidirectional PWM (fx_flags bit 3 CLEAR).
L_0B9D:
    $0B9D: AD C2 0D   LDA $0dc2        ; pwm_speed
    $0BA0: F0 62      BEQ $0c04        ; → L_0C04   ; pwm_speed = 0: skip
    $0BA2: AC D5 0D   LDY $0dd5        ; Y = inst*8
    $0BA5: 29 1F      AND #$1f         ; period = pwm_speed & $1F
    $0BA7: DE C8 0D   DEC $0dc8,x      ; v_pwperiod,x--
    $0BAA: 10 58      BPL $0c04        ; → L_0C04   ; not yet underflowed
    $0BAC: 9D C8 0D   STA $0dc8,x      ; reload period
    $0BAF: AD C2 0D   LDA $0dc2        ; pwm_speed
    $0BB2: 29 E0      AND #$e0         ; step = pwm_speed & $E0 (high bits)
    $0BB4: 8D E1 0D   STA $0de1        ; save step
    $0BB7: BD CB 0D   LDA $0dcb,x      ; v_pwdir,x (0=up, nonzero=down)
    $0BBA: D0 1A      BNE $0bd6        ; → L_0BD6   ; down branch
    ; UP: pw += step, check upper bound $0E.
    $0BBC: AD E1 0D   LDA $0de1
    $0BBF: 18         CLC
    $0BC0: 79 E3 0D   ADC $0de3,y      ; pw_lo + step
    $0BC3: 48         PHA
    $0BC4: B9 E4 0D   LDA $0de4,y      ; pw_hi + carry
    $0BC7: 69 00      ADC #$00
    $0BC9: 29 0F      AND #$0f         ; keep low nibble (4-bit PW high)
    $0BCB: 48         PHA
    $0BCC: C9 0E      CMP #$0e         ; reached upper bound?
    $0BCE: D0 1D      BNE $0bed        ; → L_0BED
    $0BD0: FE CB 0D   INC $0dcb,x      ; flip to "down"
    $0BD3: 4C ED 0B   JMP $0bed        ; → L_0BED
; DOWN: pw -= step, check lower bound $08.
L_0BD6:
    $0BD6: 38         SEC
    $0BD7: B9 E3 0D   LDA $0de3,y
    $0BDA: ED E1 0D   SBC $0de1
    $0BDD: 48         PHA
    $0BDE: B9 E4 0D   LDA $0de4,y
    $0BE1: E9 00      SBC #$00
    $0BE3: 29 0F      AND #$0f
    $0BE5: 48         PHA
    $0BE6: C9 08      CMP #$08         ; reached lower bound?
    $0BE8: D0 03      BNE $0bed        ; → L_0BED
    $0BEA: DE CB 0D   DEC $0dcb,x      ; flip to "up" ($01 → $00)
L_0BED:
    ; Pop pw_hi (top of stack) then pw_lo, write back to instrument
    ; record AND to the SID PW registers.
    $0BED: 8E BF 0D   STX $0dbf        ; save X (voice)
    $0BF0: AE A6 0D   LDX $0da6        ; X = SID voice offset
    $0BF3: 68         PLA              ; pw_hi
    $0BF4: 99 E4 0D   STA $0de4,y      ; inst.pw_hi (mutates inst record)
    $0BF7: 9D 03 D4   STA $d403,x      ;V1_PW_HI,X
    $0BFA: 68         PLA              ; pw_lo
    $0BFB: 99 E3 0D   STA $0de3,y      ; inst.pw_lo (mutates inst record)
    $0BFE: 9D 02 D4   STA $d402,x      ;V1_PW_LO,X
    $0C01: AE BF 0D   LDX $0dbf        ; restore X (voice)
; ----------------------------------------------------------------------
; 3. PER-NOTE FREQ SLIDE ($0C04..$0C4B): gated by v_slide,X != 0.
;    Encoding of $0DDD,X:
;      bit 0 = direction (0 = up via ADC, 1 = down via SBC)
;      bits 1..6 (mask $7E) = magnitude
; ----------------------------------------------------------------------
L_0C04:
    $0C04: AC A6 0D   LDY $0da6
    $0C07: BD DD 0D   LDA $0ddd,x      ; v_slide,x
    $0C0A: F0 3F      BEQ $0c4b        ; → L_0C4B   ; no slide
    $0C0C: 29 7E      AND #$7e         ; magnitude
    $0C0E: 8D BF 0D   STA $0dbf
    $0C11: BD DD 0D   LDA $0ddd,x
    $0C14: 29 01      AND #$01         ; direction
    $0C16: F0 1B      BEQ $0c33        ; → L_0C33   ; 0: up
    ; DOWN: (v_fhi:v_flo) -= magnitude.
    $0C18: 38         SEC
    $0C19: BD DA 0D   LDA $0dda,x      ; v_flo,x
    $0C1C: ED BF 0D   SBC $0dbf
    $0C1F: 9D DA 0D   STA $0dda,x
    $0C22: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
    $0C25: BD D7 0D   LDA $0dd7,x      ; v_fhi,x
    $0C28: E9 00      SBC #$00
    $0C2A: 9D D7 0D   STA $0dd7,x
    $0C2D: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $0C30: 4C 4B 0C   JMP $0c4b        ; → L_0C4B
; UP: (v_fhi:v_flo) += magnitude.
L_0C33:
    $0C33: 18         CLC
    $0C34: BD DA 0D   LDA $0dda,x
    $0C37: 6D BF 0D   ADC $0dbf
    $0C3A: 9D DA 0D   STA $0dda,x
    $0C3D: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
    $0C40: BD D7 0D   LDA $0dd7,x
    $0C43: 69 00      ADC #$00
    $0C45: 9D D7 0D   STA $0dd7,x
    $0C48: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
; ----------------------------------------------------------------------
; 4. DOWNSLIDE / DRUM-DECAY ($0C4B..$0C84): gated by fx_flags bit 0.
;    For long notes (v_dur,X != 0, v_fhi,X != 0):
;      If (v_flags & $1F) - 1 < v_dur,X (still in early portion of note):
;        Decrement v_fhi,X (post-decrement write of OLD value).
;        If v_ctrl,X & $FE was 0 (no waveform set) → noise ctrl $80.
;      Else: write OLD v_fhi, force ctrl := $80.
; ----------------------------------------------------------------------
L_0C4B:
    $0C4B: AD E0 0D   LDA $0de0        ; fx_flags
    $0C4E: 29 01      AND #$01         ; bit 0 = drum/downslide
    $0C50: F0 35      BEQ $0c87        ; → L_0C87   ; not set
    $0C52: BD D7 0D   LDA $0dd7,x      ; v_fhi,x
    $0C55: F0 30      BEQ $0c87        ; → L_0C87   ; already 0
    $0C57: BD AD 0D   LDA $0dad,x      ; v_dur,x
    $0C5A: F0 2B      BEQ $0c87        ; → L_0C87   ; at last tick
    $0C5C: BD B0 0D   LDA $0db0,x      ; v_flags,x
    $0C5F: 29 1F      AND #$1f
    $0C61: 38         SEC
    $0C62: E9 01      SBC #$01         ; (dur_base - 1)
    $0C64: DD AD 0D   CMP $0dad,x      ; compare against v_dur,x
    $0C67: AC A6 0D   LDY $0da6
    $0C6A: 90 10      BCC $0c7c        ; → L_0C7C   ; (dur_base-1) < v_dur,x
    $0C6C: BD D7 0D   LDA $0dd7,x
    $0C6F: DE D7 0D   DEC $0dd7,x      ; v_fhi,x--
    $0C72: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y   ; write OLD v_fhi
    $0C75: BD B3 0D   LDA $0db3,x      ; v_ctrl,x
    $0C78: 29 FE      AND #$fe
    $0C7A: D0 08      BNE $0c84        ; → L_0C84   ; ctrl had waveform
L_0C7C:
    $0C7C: BD D7 0D   LDA $0dd7,x
    $0C7F: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $0C82: A9 80      LDA #$80         ; noise waveform, gate=0
L_0C84:
    $0C84: 99 04 D4   STA $d404,y      ;V1_CTRL,Y   ; (noise or untouched)
; ----------------------------------------------------------------------
; 5. SKYDIVE ($0C87..$0CAC): gated by fx_flags bit 1.
;    Long-note guard: (v_flags & $1F) >= $11.
;    On ODD frames only AND when v_fhi,X != 0:
;      INC v_fhi,X; write OLD v_fhi to V_FREQ_HI.
;    Slow upward freq drift on sustained notes.
; ----------------------------------------------------------------------
L_0C87:
    $0C87: AD E0 0D   LDA $0de0        ; fx_flags
    $0C8A: 29 02      AND #$02         ; bit 1 = skydive
    $0C8C: F0 1E      BEQ $0cac        ; → L_0CAC
    $0C8E: BD B0 0D   LDA $0db0,x      ; v_flags,x
    $0C91: 29 1F      AND #$1f
    $0C93: C9 11      CMP #$11         ; (v_flags & $1F) >= $11 ?
    $0C95: 90 15      BCC $0cac        ; → L_0CAC   ; short note
    $0C97: AD E2 0D   LDA $0de2        ; frame counter
    $0C9A: 29 01      AND #$01
    $0C9C: F0 0E      BEQ $0cac        ; → L_0CAC   ; even frame
    $0C9E: BD D7 0D   LDA $0dd7,x      ; v_fhi,x
    $0CA1: F0 09      BEQ $0cac        ; → L_0CAC   ; v_fhi == 0
    $0CA3: FE D7 0D   INC $0dd7,x      ; v_fhi,x++
    $0CA6: AC A6 0D   LDY $0da6
    $0CA9: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y   ; write OLD v_fhi
; ----------------------------------------------------------------------
; 6. DRUM ARPEGGIO ($0CAC..$0CDD): gated by fx_flags bit 2.
;    arp_pitch = v_pitch + ((frame & 7) != 0 ? $0C : 0)
;    Look up freq_table[arp_pitch * 2] and write V_FREQ_LO/HI.
;    One frame of base pitch followed by 7 frames an octave up,
;    repeating every 8 frames.
; ----------------------------------------------------------------------
L_0CAC:
    $0CAC: AD E0 0D   LDA $0de0        ; fx_flags
    $0CAF: 29 04      AND #$04         ; bit 2 = drum arp
    $0CB1: F0 2A      BEQ $0cdd        ; → L_0CDD
    $0CB3: AD E2 0D   LDA $0de2        ; frame counter
    $0CB6: 29 07      AND #$07
    $0CB8: F0 09      BEQ $0cc3        ; → L_0CC3   ; (frame & 7) == 0
    $0CBA: BD B6 0D   LDA $0db6,x      ; v_pitch + $0C
    $0CBD: 18         CLC
    $0CBE: 69 0C      ADC #$0c
    $0CC0: 4C C6 0C   JMP $0cc6        ; → L_0CC6
L_0CC3:
    $0CC3: BD B6 0D   LDA $0db6,x      ; v_pitch (base)
L_0CC6:
    $0CC6: 0A         ASL a            ; *2 for table stride
    $0CC7: A8         TAY
    $0CC8: B9 E4 0C   LDA $0ce4,y      ; freq_lo[arp_pitch]
    $0CCB: 8D BE 0D   STA $0dbe        ; scratch
    $0CCE: B9 E5 0C   LDA $0ce5,y      ; freq_hi[arp_pitch]
    $0CD1: AC A6 0D   LDY $0da6
    $0CD4: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $0CD7: AD BE 0D   LDA $0dbe
    $0CDA: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
; Voice-loop tail: DEC X. If X went negative, RTS via $0CE3. Otherwise
; jump back to the per-voice entry for the next voice.
L_0CDD:
    $0CDD: CA         DEX
    $0CDE: 30 03      BMI $0ce3        ; → L_0CE3   ; done both voices
    $0CE0: 4C CB 09   JMP $09cb        ; → L_09CB   ; process voice X
L_0CE3:
    $0CE3: 60         RTS
; ----- data gap $0CE4-$1A9B (3512 bytes) -----
; DATA REGION:
;   $0CE4..$0DA3 (~192 bytes): FREQ TABLE (96+ semitones × 2 bytes,
;     lo/hi packed). Drum-arp adds $0C to pitch so high-octave entries
;     need to be populated through ~semitone 107.
;   $0DA4..$0DA5 (2 bytes): SID voice offsets [0, 7] used at $09CB.
;   $0DA6..$0DE2 (~62 bytes): runtime scratch + per-voice state arrays.
;     v_olpos $0DA7..$0DA8, v_patpos $0DAA..$0DAB, v_dur $0DAD..$0DAE,
;     v_flags $0DB0..$0DB1, v_ctrl $0DB3..$0DB4, v_pitch $0DB6..$0DB7,
;     v_inst $0DB9..$0DBA, scratch $0DBC..$0DC7, v_pwperiod $0DC8..$0DC9,
;     v_pwdir $0DCB..$0DCC, tick $0DCE/$0DCF, $0DD0..$0DD4 = per-song
;     tempo table [3,3,2,3,1], $0DD5 inst*8 stash, $0DD6 song state,
;     v_fhi $0DD7..$0DD8, v_flo $0DDA..$0DDB, v_slide $0DDD..$0DDE,
;     $0DE0 fx_flags cache, $0DE1 pwm step scratch, $0DE2 frame counter.
;   $0DE3..$0E8A (184 bytes): INSTRUMENT TABLE (23 instruments × 8 bytes).
;     +0 pw_lo  +1 pw_hi  +2 ctrl  +3 AD  +4 SR
;     +5 vib_speed (right-shift count for vibrato delta)
;     +6 pwm_speed (low 5 bits period, high 3 bits step)
;     +7 fx_flags (bit0=downslide bit1=skydive bit2=drumarp bit3=PWmode)
;   $0E9B..$0E9E (4 bytes): RUNTIME COPY of song[A]'s voice pointers
;     (V1 lo, V1 hi, V2 lo, V2 hi) — destination of the copy in $1AA9.
;   $0E9F..$0EB2 (20 bytes): SONG TABLE (5 songs × 4 bytes).
;   $0EB3..$0F01 (~79 bytes): pat_lo table.
;   $0F02..$1161 (~92 bytes): pat_hi table + filler.
;   $1162..end: PATTERN DATA (79 patterns, variable length, $FF-terminated).

; ======= real init: =======
; Called from $0980. A holds subtune (0-indexed).
L_1A9C:
    $1A9C: A0 00      LDY #$00
    $1A9E: AA         TAX              ; X = A = subtune (0-indexed)
    $1A9F: BD D0 0D   LDA $0dd0,x      ; per-song tempo: [3,3,2,3,1][A]
    $1AA2: 8D CF 0D   STA $0dcf        ; $0DCF = tick reload value
    $1AA5: 8A         TXA
    $1AA6: 0A         ASL a
    $1AA7: 0A         ASL a            ; A * 4
    $1AA8: AA         TAX
    ; Copy 4 bytes from $0E9F+A*4 to $0E9B+0..3
    ; (= V1 olist lo, V1 olist hi, V2 olist lo, V2 olist hi).
L_1AA9:
    $1AA9: BD 9F 0E   LDA $0e9f,x
    $1AAC: 99 9B 0E   STA $0e9b,y
    $1AAF: E8         INX
    $1AB0: C8         INY
    $1AB1: C0 04      CPY #$04
    $1AB3: D0 F4      BNE $1aa9        ; → L_1AA9
    $1AB5: A9 00      LDA #$00
    $1AB7: 8D 04 D4   STA $d404        ;V1_CTRL
    $1ABA: 8D 0B D4   STA $d40b        ;V2_CTRL
    $1ABD: A9 0F      LDA #$0f
    $1ABF: 8D 18 D4   STA $d418        ;VOL
    $1AC2: A9 40      LDA #$40         ; bit 6: first-frame setup pending
    $1AC4: 8D D6 0D   STA $0dd6
    $1AC7: 60         RTS

; ======= song-end handler: =======
; Tail-called from $0983 (which is JSR'd from the orderlist scanner
; when it hits the $FE sentinel). Sets bit 7 + bit 6 of $0DD6 so that
; the next play call silences the voices then returns.
L_1AC8:
    $1AC8: A9 C0      LDA #$c0
    $1ACA: 8D D6 0D   STA $0dd6
    $1ACD: 60         RTS
; ----- data gap $1ACE-$1ADF (18 bytes) -----
; PSID metadata padding / unused tail.
