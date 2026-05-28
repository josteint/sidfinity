; ============================================================================
; Rob Hubbard - Sample Music from I. Karate (1985 Rob Hubbard)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/Hubbard_Rob/Sample_Music_from_I_Karate.sid
; Load:   $1000   Init: $1000   Play: $100C
; PSID:   1 subtune, default subtune 1
; Binary: $1000-$1E1A (3611 bytes)
;
; Auto-traced 1042 reachable code bytes from init+play. Layout commentary
; below was hand-derived from static analysis cross-checked against the
; engine sister-file Confuzion (which uses the identical state-machine
; layout, just relocated). This is Hubbard's mid-1985 tracker engine
; lineage — same DNA as Confuzion ($0858), same ALU as Action Biker.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($1000): JMP $1DE3. Wipes filter, silences V1/V2/V3 ctrl,
;   sets vol=$0F, sets engine state $14ED = $40 (first-frame bit).
;   ALL voice-state setup is deferred to play's first-frame path.
;
; sub_1003 ($1003): JMP $1DFC. Sets $14ED = $C0 (end-of-song +
;   first-frame). This is the orderlist $FE handler — see $109C.
;
; play ($100C): every frame.
;   1. DEC $14EB (sub-frame divider). If went negative, reload to $0A
;      and RTS — engine actually runs work on 11 of every 12 frames.
;      ($14EB binary-init = $08, so the very first frame counts down
;      from $08; once it wraps to $FF the steady-state $0A reload kicks
;      in.) The 1-of-12 skip slows perceived song tempo by ~8%.
;   2. INC $14FC (global frame counter — used as arp phase later).
;   3. BIT $14ED:
;      - bit 7 set (BMI) → end-of-song path at $1041
;      - bit 6 set (BVS) → FIRST-FRAME setup at $1021
;      - both clear     → JMP $105B (normal per-voice loop)
;   4. First-frame path ($1021..$103E): clear $14FC, then for X=2..0
;      zero $14C0,X (orderlist pos), $14C3,X (track pos), $14C6,X
;      (note duration), and set $14D2,X (instrument number) = $14.
;      STA $14ED with leftover A=$14 — this clears bits 7 and 6, so
;      subsequent frames take the normal-frame path. Falls through to
;      JMP $105B.
;   5. End-of-song ($1041): BVC $1058 → JMP $13F6 (just RTS for the
;      already-silenced state). When BOTH bits set ($C0, after
;      sub_1003 fired this frame), explicitly silence V*CTRL/VOL and
;      reduce $14ED to $80 so future frames RTS quickly.
;
; ============================================================================
;
; PER-VOICE LOOP ($105B..$13F5)
; ----------------------------
;
; Voice index X iterates 2 → 1 → 0 (V3, V2, V1). Each pass through:
;
;   ($105D) DEC $14E9 — tick divider; reload from $14EA ($02) when neg.
;   ($1068) LDA $14BC,X → SID base offset (0/7/14); store at $14BF and
;     copy to Y for STA $D4xx,Y addressing through the rest of the loop.
;   ($106F) **NOTE-LOAD GATE**: LDA $14E9; CMP $14EA; BNE → skip note
;     decode and jump straight to the release/effects block at $11C5.
;     Note-load only runs on frames where the divider reloaded (i.e.
;     equal to the reload value). With $14EA=$02, that's once every 3
;     frames — this is the engine's note-tick rate.
;   ($1077) Load orderlist pointer (lo from $15B3,X, hi from $15B6,X)
;     into ZP $FB/$FC.
;   ($1081) DEC $14C6,X (note duration). BMI → expired, load next note
;     ($108F). Else JMP $119E (sustain — proceed to release/effects).
;
; ORDERLIST SCAN ($108F):
;   LDY $14C0,X; LDA ($FB),Y → orderlist byte.
;   $FF → restart orderlist for this voice: zero $14C6/$14C0/$14C3,X,
;     JSR $1000 (re-runs init — silences SID and reasserts state=$40),
;     JMP $108F (re-loop). Note this means the $FF marker briefly
;     re-silences before the new pattern starts.
;   $FE → JSR $1003 (state=$C0 = end-of-song), JMP $13F6 (RTS).
;   else → byte is a pattern index; TAY, look up pattern lo/hi from
;     $15B9,Y / $15E1,Y → ZP $FD/$FE.
;
; PATTERN ROW DECODE ($10B6..$11C4):
;   $14F4,X = 0 (clear slide); $14D5 = $FF (gate-mask = normal).
;   LDY $14C3,X (track pos); LDA ($FD),Y → command byte → $14C9,X
;     and scratch $14D6.
;   AND #$1F → low 5 bits = note duration → $14C6,X.
;   BIT $14D6:
;     bit 6 set (BVS $112D) → "no-retrigger" flag: DEC $14D5 (mask=$FE),
;       then fall through to instrument apply at $1130 WITHOUT advancing
;       the row or fetching a new note.
;     else → INC $14C3,X (advance row);
;       bit 7 of $14D6 set (BMI fall-through, BPL $1102 NOT taken) →
;         INY; LDA ($FD),Y → if positive (BPL $10FC) it's an instrument
;         number → $14D2,X; if negative it's a slide-rate marker
;         ($14F4,X) followed by another byte ($14F7,X = slide step);
;         either way INC $14C3,X.
;       bit 7 clear (BPL $1102) → skip the slide/instrument byte.
;   $1102: INY; LDA ($FD),Y → note number → $14CF,X; ASL → freq table
;     index Y. If $14FE has bit 7 set ($FF or $80 — gate trigger flag
;     from the previous voice/frame), write the new freq to V*FREQ
;     immediately. Stash freq in $14EE,X (hi) / $14F1,X (lo) for the
;     vibrato/slide accumulators.
;
; INSTRUMENT APPLY ($1130..$117D):
;   LDA $14D2,X (instrument index); ASL ASL ASL → ×8 → instrument table
;   index in X (saved voice X to $14D8 first).
;     $150D,X → control byte → $14D9 then ($14D5-masked) V*CTRL,Y
;     $150B,X → pulse_lo → V*PW_LO,Y (also stashed via PHA)
;     $150C,X → pulse_hi → V*PW_HI,Y (also stashed via PHA)
;     $150E,X → AD       → V*AD,Y
;     $150F,X → SR       → V*SR,Y
;   Restore voice X; clear $14E6,X (PWM direction), $14E3,X (PWM rate).
;   Stash pulse into per-voice pulse accumulator $1505,X / $1508,X.
;   Save control byte (from $14D9) into $14CC,X — used later for the
;   release block to know what waveform/gate to clear.
;
; ROW ADVANCE & PATTERN $FF ($1187..$119D):
;   INC $14C3,X (advance to next row). Peek at next byte: if $FF, this
;   pattern is done — zero $14C3,X and INC $14C0,X (advance orderlist
;   for next note-tick frame). JMP $13E5 (per-voice continuation).
;
; ============================================================================
;
; SUSTAIN PATH ($119E..$11C4) — release-on-zero-duration check
; ------------------------------------------------------------
; Reached when DEC $14C6,X did NOT underflow (still in note duration).
;   Check $14FE; if BPL → JMP $13E5 (skip everything, this is a
;     "voice paused" frame).
;   Check command byte AND $20: if set → no auto-release, skip to $11C5.
;   If duration $14C6,X non-zero → still sustaining, skip to $11C5.
;   Otherwise: clear gate (AND $FE) on V*CTRL,Y, zero V*AD/V*SR — release.
;
; ============================================================================
;
; EFFECTS BLOCK ($11C5..$13E4)
; ----------------------------
; Reached every voice/frame (note-load OR sustain). $14FE bit 7 must be
; set or the whole block is skipped (JMP $13E5).
;
; Re-look-up instrument record into Y = $14D2,X * 8:
;   $1512,Y → $14FA — feature mask byte (bit 0 = note-hold/portamento,
;     bit 2 = arpeggio enable, bit 3 = PWM-from-$14DB).
;   $1511,Y → $14DB — vibrato amplitude / PWM step (split nibbles).
;   $1510,Y → $14XX scratch (combined effect flags). If 0, JMP $129F
;     (skip portamento/vibrato block entirely).
;
; PORTAMENTO/VIBRATO ($11EB..$1268):
;   Decompose $1510,Y byte:
;     AND $78 LSR×3 → $14FF,X = vibrato amplitude / portamento target
;     AND $07     → $14DA = vibrato shift / portamento speed
;   Update direction-tracking counter $1502,X (positive ramps up,
;   negative ramps down; bounce at amplitude limits).
;   Compute (next_freq - current_freq) >> $14DA → $14DC/$14DD step.
;   Apply step the appropriate number of times: SBC down for the first
;   half ($1252 loop), ADC up for the second half ($1277 loop).
;
; FREQ STORE ($126B..$129E):
;   If duration ($14C9,X & $1F) >= 1 (i.e. a real note):
;     LDY $14E0,X count; ADC $14DC step into $14DE/$14DF over Y iters.
;   STA $14DE → V*FREQ_LO,Y; $14DF → V*FREQ_HI,Y.
;
; PWM ($129F..$1318):
;   $14FA AND $08 path: ADC $14DB to instrument's pulse_lo (in-place
;     mutation of $150B,Y) and write to V*PW_LO. (Linear PWM sweep —
;     drifts the instrument's pulse over time.)
;   else: $14DB AND $0F = rate; DEC $14E3,X; on wrap, $14DB AND $F0 =
;     step. Toggle direction $14E6,X. ADC/SBC step from $1505/$1508
;     accumulator. Write $1508 → V*PW_HI, $1505 → V*PW_LO. (Triangular
;     PWM bounce around the original pulse value.)
;
; FREQ SLIDE ($1319..$1361):
;   $14F4,X = slide rate (set in pattern decode). If 0, skip.
;     AND $7E = step magnitude (× 2). AND $01 = direction.
;     direction=1 → SBC step from $14F1,X / $14EE,X (slide down).
;     direction=0 → ADC step (slide up).
;   Write to V*FREQ.
;
; NOTE-HOLD / PITCH-DROP ($1362..$139D):
;   $14FA AND $01 path. If freq high $14EE,X is non-zero AND duration
;   $14C6,X is non-zero AND (cmd AND $1F) - 1 < duration:
;     Decrement $14EE,X, write to V*FREQ_HI; if saved control $14CC,X
;     bit 0 (gate from last note) was non-zero, RE-trigger waveform
;     via STA $D404,Y. Otherwise just write the dropped freq_hi and
;     fire a noise gate (#$80) to V*CTRL.
;
; ARPEGGIO ($139F..$13E4):
;   $14FA AND $04 → arp enable.
;   ($14FA >> 4) selects arp size: $0C → Y=$02 (3-note triad), else
;     Y=$01 (2-note alternation). Stored at $13BF (scratch).
;   $14FC AND $02 → arp phase bit (alternates every frame).
;   Phase 0 → note - $0C (root); phase 1 → note as-is (octave up).
;   Look up freq table at $13FC,Y → write V*FREQ.
;
; PER-VOICE LOOP TAIL ($13E5..$13F5):
;   LDY $14FD; if non-zero leave Y=$FF; else INY → Y=$00.
;   STY $14FE — sets the "voice-active" flag for the NEXT voice.
;   DEX. BMI → done → JMP $13F6 (RTS). Else JMP $1068 (next voice).
;
; $13F6: STA $14FE = $FF (reset for next play call); RTS.
;
; ============================================================================
;
; MEMORY MAP (per-voice arrays use voice index X = 2/1/0 for V3/V2/V1)
; --------------------------------------------------------------------
;   $14BC,X — SID base offset (0, 7, 14)
;   $14BF   — current SID base (Y register snapshot for STA $D4xx,Y)
;   $14C0,X — orderlist position
;   $14C3,X — track (pattern row) position
;   $14C6,X — note duration countdown
;   $14C9,X — last command byte (raw, with flag bits)
;   $14CC,X — saved control byte for current note (for release block)
;   $14CF,X — current note number
;   $14D2,X — current instrument number (init = $14)
;   $14D5   — gate mask ($FF normal, $FE for "no-retrigger" rows)
;   $14D6   — scratch copy of command byte
;   $14D7   — scratch (freq lo)
;   $14D8   — scratch (saved voice X across instrument-table indexing)
;   $14D9   — saved control byte during instrument apply
;   $14DA   — vibrato shift / portamento speed
;   $14DB   — vibrato amplitude / PWM step (split nibbles)
;   $14DC/$14DD — freq delta (next - current) lo/hi
;   $14DE/$14DF — current freq accumulator lo/hi for vibrato/portamento
;   $14E0,X — vibrato/portamento step count
;   $14E3,X — PWM rate counter
;   $14E6,X — PWM direction (0=down, !=0=up)
;   $14E9   — tick divider (note-load gate)
;   $14EA   — tick divider reload value ($02)
;   $14EB   — sub-frame divider (skips 1 frame in 12)
;   $14EC   — current instrument table index ×8 (saved Y)
;   $14ED   — engine state: bit 7=end-of-song, bit 6=first-frame
;   $14EE,X — current freq high (for slide/vibrato accumulator)
;   $14F1,X — current freq low (ditto)
;   $14F4,X — slide rate byte (with direction in bit 0)
;   $14F7,X — slide step (when explicit)
;   $14FA   — instrument feature mask ($1512,Y copy)
;   $14FB   — PWM step (high nibble of $14DB)
;   $14FC   — global frame counter (also arp phase source)
;   $14FD   — global pause flag (suppresses voice-active continuation)
;   $14FE   — voice-active flag for the effects block
;   $14FF,X — vibrato amplitude (× 8)
;   $1502,X — vibrato direction counter
;   $1505,X — PWM accumulator lo
;   $1508,X — PWM accumulator hi
;
; ZP:
;   $FB/$FC — orderlist pointer
;   $FD/$FE — pattern (row data) pointer
;
; TABLES (in $13FC..$1DE2 data region):
;   $13FA-$13FB — pre-buffer entry for ($14CF,X * 2)+0 indexing safety
;   $13FC..    — freq table, 2 bytes/semitone (lo, hi) packed
;   $150B,Y    — instrument table: 8-byte stride, fields:
;     +0 pulse_lo  +1 pulse_hi  +2 ctrl  +3 AD  +4 SR
;     +5 fx_flags1 (vib/pwm/porta combined)
;     +6 fx_flags2 (vib amp / pwm step)
;     +7 fx_flags3 (feature mask byte: bit0/2/3 enables)
;   $15B3,X    — orderlist pointer lo (per voice)
;   $15B6,X    — orderlist pointer hi (per voice)
;   $15B9,Y    — pattern pointer lo (indexed by orderlist byte)
;   $15E1,Y    — pattern pointer hi (ditto)
;
; ============================================================================

; ======= init: =======
; All real init lives at $1DE3 — this is just a trampoline.
init:
    $1000: 4C E3 1D   JMP $1de3        ; → L_1DE3

; sub_1003: orderlist $FE marker handler. Sets engine state to $C0
; (bit 7=end-of-song + bit 6=first-frame) so the very next play frame
; takes the BMI/BVS combined branch at $1041 → silence everything.
sub_1003:
    $1003: 4C FC 1D   JMP $1dfc        ; → L_1DFC
; ----- data gap $1006-$100B (6 bytes) -----

; ======= play: =======
; Called every frame by sidplayfp.
play:
    ; Sub-frame divider. $14EB starts at $08 in the binary; once it
    ; wraps to $FF we reload to $0A. Steady-state: 11 work frames per
    ; 12 calls (one BPL-not-taken skip frame inserts an RTS).
    $100C: CE EB 14   DEC $14eb
    $100F: 10 06      BPL $1017        ; → L_1017   ; usual: do work
    $1011: A9 0A      LDA #$0a
    $1013: 8D EB 14   STA $14eb        ; reload divider
    $1016: 60         RTS              ; skipped frame
L_1017:
    ; Frame counter +1 (used as arp phase via bit 1 in $13BB).
    $1017: EE FC 14   INC $14fc
    ; $14ED holds engine state: bit 7=end-of-song, bit 6=first-frame.
    ; BIT moves bit 7 → N flag, bit 6 → V flag.
    $101A: 2C ED 14   BIT $14ed
    $101D: 30 22      BMI $1041        ; → L_1041   ; end-of-song
    $101F: 50 3A      BVC $105b        ; → L_105B   ; normal frame
    ; FIRST-FRAME setup (bit 6 was set by init at $1DE3). Wipe per-voice
    ; state arrays and the global frame counter. Falls through to $105B.
    $1021: A9 00      LDA #$00
    $1023: 8D FC 14   STA $14fc
    $1026: A2 02      LDX #$02
L_1028:
    ; Loop X=2..0. Zero v_olpos/v_patpos/v_dur, set v_inst = $14.
    $1028: A9 00      LDA #$00
    $102A: 9D C0 14   STA $14c0,x
    $102D: 9D C3 14   STA $14c3,x
    $1030: 9D C6 14   STA $14c6,x
    $1033: A9 14      LDA #$14
    $1035: 9D D2 14   STA $14d2,x
    $1038: CA         DEX
    $1039: 10 ED      BPL $1028        ; → L_1028
    ; A still holds $14 — neither bit 7 nor bit 6 set, so $14ED becomes
    ; a "normal frame" state that BPL+BVC at $101D/$101F both take.
    $103B: 8D ED 14   STA $14ed
    $103E: 4C 5B 10   JMP $105b        ; → L_105B
L_1041:
    ; END-OF-SONG path. If only bit 7 set ($80) → just RTS via $13F6.
    ; If both bits set ($C0, sub_1003 just fired) → silence SID, then
    ; clear bit 6 leaving pure $80 so future frames RTS quickly.
    $1041: 50 15      BVC $1058        ; → L_1058
    $1043: A9 00      LDA #$00
    $1045: 8D 04 D4   STA $d404      ;V1_CTRL
    $1048: 8D 0B D4   STA $d40b      ;V2_CTRL
    $104B: 8D 12 D4   STA $d412      ;V3_CTRL
    $104E: A9 0F      LDA #$0f
    $1050: 8D 18 D4   STA $d418      ;VOL
    $1053: A9 80      LDA #$80
    $1055: 8D ED 14   STA $14ed
L_1058:
    $1058: 4C F6 13   JMP $13f6        ; → L_13F6   ; → RTS
L_105B:
    ; ====== PER-VOICE LOOP entry ======
    ; X = voice index (start at V3). DEX at end of loop iterates 2→1→0.
    $105B: A2 02      LDX #$02
    ; Tick divider — note-load gate runs only once per ($14EA+1) frames.
    $105D: CE E9 14   DEC $14e9
    $1060: 10 06      BPL $1068        ; → L_1068   ; not yet wrapped
    $1062: AD EA 14   LDA $14ea        ; reload value ($02)
    $1065: 8D E9 14   STA $14e9
L_1068:
    ; Per-voice SID base lookup. $14BC = [0, 7, 14] for V1/V2/V3.
    $1068: BD BC 14   LDA $14bc,x      ; SID voice offset (0,7,14)
    $106B: 8D BF 14   STA $14bf        ; remember as Y for SID writes
    $106E: A8         TAY              ; Y = SID base offset
    ; **NOTE-LOAD GATE**: only proceed to note-load when divider just
    ; reloaded (current == reload value). Otherwise BNE → effects-only
    ; path at $11C5. With $14EA=$02, this fires once every 3 frames.
    $106F: AD E9 14   LDA $14e9
    $1072: CD EA 14   CMP $14ea
    $1075: D0 15      BNE $108c        ; → L_108C   ; effects-only frame
    ; Note-load path. Per-voice orderlist pointer → ZP $FB/$FC.
    $1077: BD B3 15   LDA $15b3,x      ; orderlist ptr lo
    $107A: 85 FB      STA $fb
    $107C: BD B6 15   LDA $15b6,x      ; orderlist ptr hi
    $107F: 85 FC      STA $fc
    ; Note duration countdown. Underflow → load next note ($108F).
    ; Else fall through to sustain path at $119E.
    $1081: DE C6 14   DEC $14c6,x
    $1084: 30 09      BMI $108f        ; → L_108F   ; expired: load next
    $1086: 4C 9E 11   JMP $119e        ; → L_119E   ; sustain current
; ----- data gap $1089-$108B (3 bytes) -----

L_108C:
    ; Effects-only frame: skip pattern decode, run release/effects.
    $108C: 4C C5 11   JMP $11c5        ; → L_11C5
L_108F:
    ; ====== ORDERLIST SCAN ======
    ; $14C0,X = orderlist position; ($FB):Y = orderlist byte.
    $108F: BC C0 14   LDY $14c0,x
    $1092: B1 FB      LDA ($fb),y
    $1094: C9 FF      CMP #$ff         ; loop-back sentinel
    $1096: F0 0A      BEQ $10a2        ; → L_10A2   ; restart orderlist
    $1098: C9 FE      CMP #$fe         ; song-end sentinel
    $109A: D0 1A      BNE $10b6        ; → L_10B6   ; normal pattern idx
    ; $FE: jam state to $C0 and bail with RTS for this frame.
    $109C: 20 03 10   JSR $1003        ; → sub_1003
    $109F: 4C F6 13   JMP $13f6        ; → L_13F6
L_10A2:
    ; $FF: restart orderlist for this voice. Zero state and re-init.
    ; The JSR $1000 here re-runs init = silences SID + state=$40, which
    ; means the loop point briefly drops everything. Then JMP $108F
    ; re-enters the scan (now reading orderlist[0]).
    $10A2: A9 00      LDA #$00
    $10A4: 9D C6 14   STA $14c6,x      ; v_dur,X = 0
    $10A7: 9D C0 14   STA $14c0,x      ; v_olpos,X = 0
    $10AA: 9D C3 14   STA $14c3,x      ; v_patpos,X = 0
    $10AD: 20 00 10   JSR $1000        ; → init     ; silence & restart
    $10B0: 4C 8F 10   JMP $108f        ; → L_108F   ; re-scan from 0
; ----- data gap $10B3-$10B5 (3 bytes) -----

L_10B6:
    ; Normal pattern index. TAY; pattern lo/hi from $15B9,Y / $15E1,Y.
    $10B6: A8         TAY
    $10B7: B9 B9 15   LDA $15b9,y      ; pattern ptr lo[Y]
    $10BA: 85 FD      STA $fd
    $10BC: B9 E1 15   LDA $15e1,y      ; pattern ptr hi[Y]
    $10BF: 85 FE      STA $fe
    ; ====== PATTERN ROW DECODE ======
    ; Reset slide and gate-mask defaults for this row.
    $10C1: A9 00      LDA #$00
    $10C3: 9D F4 14   STA $14f4,x      ; slide rate = 0
    $10C6: BC C3 14   LDY $14c3,x      ; track position
    $10C9: A9 FF      LDA #$ff
    $10CB: 8D D5 14   STA $14d5        ; gate mask = $FF (normal)
    ; Read command byte → both per-voice ($14C9,X) and scratch ($14D6).
    $10CE: B1 FD      LDA ($fd),y
    $10D0: 9D C9 14   STA $14c9,x
    $10D3: 8D D6 14   STA $14d6
    ; Low 5 bits of command = note duration.
    $10D6: 29 1F      AND #$1f
    $10D8: 9D C6 14   STA $14c6,x      ; v_dur,X
    ; Test command flag bits (bit 7 N, bit 6 V).
    $10DB: 2C D6 14   BIT $14d6
    $10DE: 70 4D      BVS $112d        ; → L_112D   ; bit 6: no retrigger
    ; bit 6 clear: advance row pointer.
    $10E0: FE C3 14   INC $14c3,x
    $10E3: AD D6 14   LDA $14d6
    $10E6: 10 1A      BPL $1102        ; → L_1102   ; bit 7 clear: just note
    ; bit 7 set: read NEXT byte.
    $10E8: C8         INY
    $10E9: B1 FD      LDA ($fd),y
    $10EB: 10 0F      BPL $10fc        ; → L_10FC   ; positive: instrument
    ; negative: explicit slide rate. Store this byte in $14F4,X (slide
    ; rate w/ direction), then read NEXT byte as slide step → $14F7,X.
    $10ED: 9D F4 14   STA $14f4,x
    $10F0: C8         INY
    $10F1: B1 FD      LDA ($fd),y
    $10F3: 9D F7 14   STA $14f7,x
    $10F6: FE C3 14   INC $14c3,x
    $10F9: 4C FF 10   JMP $10ff        ; → L_10FF
L_10FC:
    ; positive byte: instrument number → $14D2,X.
    $10FC: 9D D2 14   STA $14d2,x
L_10FF:
    $10FF: FE C3 14   INC $14c3,x
L_1102:
    ; Read note number (always present after the optional flag bytes).
    $1102: C8         INY
    $1103: B1 FD      LDA ($fd),y
    $1105: 9D CF 14   STA $14cf,x      ; v_note,X
    $1108: 0A         ASL a            ; ×2 = freq table index
    $1109: A8         TAY
    ; Only write fresh freq if the per-voice "active" flag $14FE has
    ; bit 7 set (i.e. previous voice/frame fired its gate). Otherwise
    ; defer — the effects block will compute a slid/vibrated freq.
    $110A: AD FE 14   LDA $14fe
    $110D: 10 21      BPL $1130        ; → L_1130
    $110F: B9 FC 13   LDA $13fc,y      ; freq_hi[note*2]
    $1112: 8D D7 14   STA $14d7
    $1115: B9 FD 13   LDA $13fd,y      ; freq_lo[note*2+1]
    $1118: AC BF 14   LDY $14bf        ; Y = SID base
    $111B: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $111E: 9D EE 14   STA $14ee,x      ; cache freq_hi for slide/vib
    $1121: AD D7 14   LDA $14d7
    $1124: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1127: 9D F1 14   STA $14f1,x      ; cache freq_lo
    $112A: 4C 30 11   JMP $1130        ; → L_1130
L_112D:
    ; "no retrigger" row: just lower the gate mask to $FE so V*CTRL
    ; gets the gate bit cleared at $114E, but DON'T advance pattern.
    $112D: CE D5 14   DEC $14d5
L_1130:
    ; ====== INSTRUMENT APPLY ======
    ; Y = SID base (re-loaded). Compute instrument table base in X:
    ;   X = $14D2,X * 8.
    $1130: AC BF 14   LDY $14bf
    $1133: BD D2 14   LDA $14d2,x
    $1136: 8E D8 14   STX $14d8        ; save voice X
    $1139: 0A         ASL a
    $113A: 0A         ASL a
    $113B: 0A         ASL a
    $113C: AA         TAX              ; X = inst * 8
    $113D: BD 0D 15   LDA $150d,x      ; ctrl byte (preview, for save)
    $1140: 8D D9 14   STA $14d9
    ; Only write SID instrument fields if active flag bit 7 set.
    $1143: AD FE 14   LDA $14fe
    $1146: 10 36      BPL $117e        ; → L_117E
    $1148: BD 0D 15   LDA $150d,x      ; instrument: ctrl
    $114B: 2D D5 14   AND $14d5        ; mask gate (FE if no-retrigger)
    $114E: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $1151: BD 0B 15   LDA $150b,x      ; instrument: pulse_lo
    $1154: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $1157: 48         PHA              ; stash pulse_lo for accumulator
    $1158: BD 0C 15   LDA $150c,x      ; instrument: pulse_hi
    $115B: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $115E: 48         PHA              ; stash pulse_hi for accumulator
    $115F: BD 0E 15   LDA $150e,x      ; instrument: AD
    $1162: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $1165: BD 0F 15   LDA $150f,x      ; instrument: SR
    $1168: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $116B: AE D8 14   LDX $14d8        ; restore voice X
    $116E: A9 00      LDA #$00
    $1170: 9D E6 14   STA $14e6,x      ; PWM direction = 0
    $1173: 9D E3 14   STA $14e3,x      ; PWM rate ctr = 0
    ; Pop pulse hi/lo into per-voice PWM accumulator.
    $1176: 68         PLA              ; pulse_hi
    $1177: 9D 08 15   STA $1508,x      ; pwm_acc_hi,X
    $117A: 68         PLA              ; pulse_lo
    $117B: 9D 05 15   STA $1505,x      ; pwm_acc_lo,X
L_117E:
    ; Save (possibly pre-mask) ctrl byte for the release block.
    $117E: AD D9 14   LDA $14d9
    $1181: AE D8 14   LDX $14d8        ; restore voice X
    $1184: 9D CC 14   STA $14cc,x      ; v_ctrl_save,X
    ; ====== ROW ADVANCE & PATTERN END ($FF) ======
    $1187: FE C3 14   INC $14c3,x
    $118A: BC C3 14   LDY $14c3,x
    $118D: B1 FD      LDA ($fd),y
    $118F: C9 FF      CMP #$ff         ; pattern end?
    $1191: D0 08      BNE $119b        ; → L_119B
    $1193: A9 00      LDA #$00
    $1195: 9D C3 14   STA $14c3,x      ; reset row
    $1198: FE C0 14   INC $14c0,x      ; advance orderlist
L_119B:
    $119B: 4C E5 13   JMP $13e5        ; → L_13E5   ; per-voice tail
L_119E:
    ; ====== SUSTAIN PATH ======
    ; Reached when $14C6,X did NOT underflow at $1084.
    $119E: AD FE 14   LDA $14fe
    $11A1: 30 03      BMI $11a6        ; → L_11A6   ; voice active
    $11A3: 4C E5 13   JMP $13e5        ; → L_13E5   ; voice paused: skip
L_11A6:
    $11A6: AC BF 14   LDY $14bf
    $11A9: BD C9 14   LDA $14c9,x      ; cmd byte
    $11AC: 29 20      AND #$20         ; bit 5 = no auto-release
    $11AE: D0 15      BNE $11c5        ; → L_11C5
    $11B0: BD C6 14   LDA $14c6,x      ; remaining duration
    $11B3: D0 10      BNE $11c5        ; → L_11C5   ; still sustaining
    ; Duration just reached zero AND no "hold" flag → release: clear
    ; gate (AND $FE) and zero AD/SR.
    $11B5: BD CC 14   LDA $14cc,x
    $11B8: 29 FE      AND #$fe
    $11BA: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $11BD: A9 00      LDA #$00
    $11BF: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $11C2: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_11C5:
    ; ====== EFFECTS BLOCK ======
    ; Skip entirely if voice not active.
    $11C5: AD FE 14   LDA $14fe
    $11C8: 30 03      BMI $11cd        ; → L_11CD
    $11CA: 4C E5 13   JMP $13e5        ; → L_13E5
L_11CD:
    ; Re-derive instrument table base (Y = inst * 8) and pull the three
    ; effect-control bytes.
    $11CD: BD D2 14   LDA $14d2,x
    $11D0: 0A         ASL a
    $11D1: 0A         ASL a
    $11D2: 0A         ASL a
    $11D3: A8         TAY
    $11D4: 8C EC 14   STY $14ec        ; remember inst*8 for PWM path
    $11D7: B9 12 15   LDA $1512,y      ; feature mask byte
    $11DA: 8D FA 14   STA $14fa
    $11DD: B9 11 15   LDA $1511,y      ; vib amp / PWM step
    $11E0: 8D DB 14   STA $14db
    $11E3: B9 10 15   LDA $1510,y      ; combined vib/porta byte
    $11E6: D0 03      BNE $11eb        ; → L_11EB
    $11E8: 4C 9F 12   JMP $129f        ; → L_129F   ; no porta/vib: skip
L_11EB:
    ; PORTAMENTO / VIBRATO setup.
    $11EB: 48         PHA              ; stash combined byte
    $11EC: 29 78      AND #$78         ; bits 6..3 = vib amp / porta target
    $11EE: 4A         LSR a
    $11EF: 4A         LSR a
    $11F0: 4A         LSR a
    $11F1: 9D FF 14   STA $14ff,x      ; vibrato amplitude (× 8 originally)
    $11F4: 68         PLA
    $11F5: 29 07      AND #$07         ; bits 2..0 = vib shift / porta speed
    $11F7: 8D DA 14   STA $14da
    ; Direction tracking via $1502,X — bounces between +amp and -amp.
    $11FA: BD 02 15   LDA $1502,x
    $11FD: 10 0A      BPL $1209        ; → L_1209
    $11FF: DE E0 14   DEC $14e0,x
    $1202: D0 19      BNE $121d        ; → L_121D
    $1204: FE 02 15   INC $1502,x
    $1207: 10 14      BPL $121d        ; → L_121D
L_1209:
    $1209: FE E0 14   INC $14e0,x
    $120C: BD FF 14   LDA $14ff,x
    $120F: DD E0 14   CMP $14e0,x
    $1212: B0 09      BCS $121d        ; → L_121D
    $1214: 9D E0 14   STA $14e0,x      ; clamp to amplitude
    $1217: DE 02 15   DEC $1502,x      ; flip direction
    $121A: DE E0 14   DEC $14e0,x
L_121D:
    ; Compute (next_freq - current_freq) >> $14DA → $14DC/$14DD step.
    $121D: BD CF 14   LDA $14cf,x      ; current note
    $1220: 0A         ASL a
    $1221: A8         TAY
    $1222: 38         SEC
    $1223: B9 FC 13   LDA $13fc,y      ; freq[note]_hi
    $1226: F9 FA 13   SBC $13fa,y      ; - freq[note-1]_hi  (delta hi)
    $1229: 8D DC 14   STA $14dc        ; step lo (intermediate)
    $122C: B9 FD 13   LDA $13fd,y      ; freq[note]_lo
    $122F: F9 FB 13   SBC $13fb,y      ; - freq[note-1]_lo  (delta lo)
L_1232:
    ; Right-shift step by $14DA bits.
    $1232: CE DA 14   DEC $14da
    $1235: 30 07      BMI $123e        ; → L_123E
    $1237: 4A         LSR a
    $1238: 6E DC 14   ROR $14dc
    $123B: 4C 32 12   JMP $1232        ; → L_1232
L_123E:
    $123E: 8D DD 14   STA $14dd        ; step hi (final)
    ; Snapshot current freq into $14DE/$14DF accumulator.
    $1241: B9 FC 13   LDA $13fc,y
    $1244: 8D DE 14   STA $14de
    $1247: B9 FD 13   LDA $13fd,y
    $124A: 8D DF 14   STA $14df
    ; Subtract step (vib_amp/2) times — initial "down" half of vibrato.
    $124D: BD FF 14   LDA $14ff,x
    $1250: 4A         LSR a
    $1251: A8         TAY
L_1252:
    $1252: 88         DEY
    $1253: 30 16      BMI $126b        ; → L_126B
    $1255: 38         SEC
    $1256: AD DE 14   LDA $14de
    $1259: ED DC 14   SBC $14dc
    $125C: 8D DE 14   STA $14de
    $125F: AD DF 14   LDA $14df
    $1262: ED DD 14   SBC $14dd
    $1265: 8D DF 14   STA $14df
    $1268: 4C 52 12   JMP $1252        ; → L_1252
L_126B:
    ; If duration small (<1) → skip the up-ramp and freq write.
    $126B: BD C9 14   LDA $14c9,x
    $126E: 29 1F      AND #$1f
    $1270: C9 01      CMP #$01
    $1272: 90 2B      BCC $129f        ; → L_129F
    ; Add step $14E0,X times — "up" half of vibrato cycle.
    $1274: BC E0 14   LDY $14e0,x
L_1277:
    $1277: 88         DEY
    $1278: 30 16      BMI $1290        ; → L_1290
    $127A: 18         CLC
    $127B: AD DE 14   LDA $14de
    $127E: 6D DC 14   ADC $14dc
    $1281: 8D DE 14   STA $14de
    $1284: AD DF 14   LDA $14df
    $1287: 6D DD 14   ADC $14dd
    $128A: 8D DF 14   STA $14df
    $128D: 4C 77 12   JMP $1277        ; → L_1277
L_1290:
    ; Write computed freq → V*FREQ.
    $1290: AC BF 14   LDY $14bf
    $1293: AD DE 14   LDA $14de
    $1296: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1299: AD DF 14   LDA $14df
    $129C: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_129F:
    ; ====== PWM ======
    ; bit 3 of feature mask: linear PWM (mutates instrument table!).
    $129F: AD FA 14   LDA $14fa
    $12A2: 29 08      AND #$08
    $12A4: F0 15      BEQ $12bb        ; → L_12BB
    $12A6: AC EC 14   LDY $14ec        ; inst*8
    $12A9: B9 0B 15   LDA $150b,y      ; current instrument pulse_lo
    $12AC: 6D DB 14   ADC $14db        ; += step (split nibble byte)
    $12AF: 99 0B 15   STA $150b,y      ; write back into instrument
    $12B2: AC BF 14   LDY $14bf
    $12B5: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $12B8: 4C 19 13   JMP $1319        ; → L_1319
L_12BB:
    ; Triangle PWM around the per-voice accumulator $1505/$1508.
    $12BB: AD DB 14   LDA $14db
    $12BE: F0 59      BEQ $1319        ; → L_1319    ; no PWM byte: skip
    $12C0: AC BF 14   LDY $14bf
    $12C3: 29 0F      AND #$0f         ; low nibble = rate
    $12C5: DE E3 14   DEC $14e3,x
    $12C8: 10 4F      BPL $1319        ; → L_1319    ; not yet ticked
    $12CA: 9D E3 14   STA $14e3,x      ; reload rate counter
    $12CD: AD DB 14   LDA $14db
    $12D0: 29 F0      AND #$f0         ; high nibble = step
    $12D2: 8D FB 14   STA $14fb
    $12D5: BD E6 14   LDA $14e6,x
    $12D8: D0 1A      BNE $12f4        ; → L_12F4    ; direction up
    ; Direction down: subtract step from accumulator.
    $12DA: AD FB 14   LDA $14fb
    $12DD: 18         CLC
    $12DE: 7D 05 15   ADC $1505,x
    $12E1: 48         PHA
    $12E2: BD 08 15   LDA $1508,x
    $12E5: 69 00      ADC #$00
    $12E7: 29 0F      AND #$0f
    $12E9: 48         PHA
    $12EA: C9 0E      CMP #$0e         ; hit upper bound? flip dir
    $12EC: D0 1D      BNE $130b        ; → L_130B
    $12EE: FE E6 14   INC $14e6,x
    $12F1: 4C 0B 13   JMP $130b        ; → L_130B
L_12F4:
    ; Direction up: add (subtract from accumulator since we built it
    ; via SBC). Same lower-bound-flip logic at $0E vs $08.
    $12F4: 38         SEC
    $12F5: BD 05 15   LDA $1505,x
    $12F8: ED FB 14   SBC $14fb
    $12FB: 48         PHA
    $12FC: BD 08 15   LDA $1508,x
    $12FF: E9 00      SBC #$00
    $1301: 29 0F      AND #$0f
    $1303: 48         PHA
    $1304: C9 08      CMP #$08         ; hit lower bound? flip dir
    $1306: D0 03      BNE $130b        ; → L_130B
    $1308: DE E6 14   DEC $14e6,x
L_130B:
    ; Pop+store new pulse → accumulator + V*PW.
    $130B: 68         PLA
    $130C: 9D 08 15   STA $1508,x
    $130F: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $1312: 68         PLA
    $1313: 9D 05 15   STA $1505,x
    $1316: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
L_1319:
    ; ====== FREQ SLIDE ======
    $1319: AC BF 14   LDY $14bf
    $131C: BD F4 14   LDA $14f4,x      ; slide rate (bit 0 = direction)
    $131F: F0 41      BEQ $1362        ; → L_1362    ; no slide
    $1321: 29 7E      AND #$7e         ; magnitude (cleared bit 0)
    $1323: 8D D8 14   STA $14d8
    $1326: BD F4 14   LDA $14f4,x
    $1329: 29 01      AND #$01         ; direction bit
    $132B: F0 1C      BEQ $1349        ; → L_1349    ; up
    ; Slide DOWN: SBC step from $14F1,X / $14EE,X (current freq).
    $132D: 38         SEC
    $132E: BD F1 14   LDA $14f1,x
    $1331: ED D8 14   SBC $14d8
    $1334: 9D F1 14   STA $14f1,x
    $1337: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $133A: BD EE 14   LDA $14ee,x
    $133D: FD F7 14   SBC $14f7,x
    $1340: 9D EE 14   STA $14ee,x
    $1343: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1346: 4C 62 13   JMP $1362        ; → L_1362
L_1349:
    ; Slide UP: ADC step.
    $1349: 18         CLC
    $134A: BD F1 14   LDA $14f1,x
    $134D: 6D D8 14   ADC $14d8
    $1350: 9D F1 14   STA $14f1,x
    $1353: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1356: BD EE 14   LDA $14ee,x
    $1359: 7D F7 14   ADC $14f7,x
    $135C: 9D EE 14   STA $14ee,x
    $135F: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_1362:
    ; ====== NOTE-HOLD / PITCH-DROP ======
    ; bit 0 of feature mask: when duration ticks down to (cmd_low - 1),
    ; decrement freq_hi by 1 each frame and (optionally) re-trigger
    ; the gate. Used for the characteristic "drum drop" at end of notes.
    $1362: AD FA 14   LDA $14fa
    $1365: 29 01      AND #$01
    $1367: F0 35      BEQ $139e        ; → L_139E
    $1369: BD EE 14   LDA $14ee,x
    $136C: F0 30      BEQ $139e        ; → L_139E    ; freq already 0
    $136E: BD C6 14   LDA $14c6,x
    $1371: F0 2B      BEQ $139e        ; → L_139E    ; duration=0
    $1373: BD C9 14   LDA $14c9,x
    $1376: 29 1F      AND #$1f
    $1378: 38         SEC
    $1379: E9 01      SBC #$01
    $137B: DD C6 14   CMP $14c6,x
    $137E: AC BF 14   LDY $14bf
    $1381: 90 10      BCC $1393        ; → L_1393
    ; Trigger condition met: drop freq_hi and re-fire gate.
    $1383: BD EE 14   LDA $14ee,x
    $1386: DE EE 14   DEC $14ee,x
    $1389: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $138C: BD CC 14   LDA $14cc,x      ; saved control byte
    $138F: 29 FE      AND #$fe         ; clear gate bit
    $1391: D0 08      BNE $139b        ; → L_139B
L_1393:
    $1393: BD EE 14   LDA $14ee,x
    $1396: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1399: A9 80      LDA #$80         ; noise gate fire
L_139B:
    $139B: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_139E:
    $139E: EA         NOP
    ; ====== ARPEGGIO ======
    ; bit 2 of feature mask: arp enable. Upper nibble of $14FA selects
    ; arp size; frame counter bit 1 selects phase (alternates every
    ; frame, since DEC of $14EB only writes once per work-frame).
    $139F: AD FA 14   LDA $14fa
    $13A2: 29 04      AND #$04
    $13A4: F0 3F      BEQ $13e5        ; → L_13E5    ; no arp
    $13A6: AD FA 14   LDA $14fa
    $13A9: 4A         LSR a
    $13AA: 4A         LSR a
    $13AB: 4A         LSR a
    $13AC: 4A         LSR a            ; A = upper nibble of $14FA
    $13AD: 8D C7 13   STA $13c7        ; (scratch, into data area)
    $13B0: A0 02      LDY #$02         ; default arp depth
    $13B2: C9 0C      CMP #$0c
    $13B4: F0 02      BEQ $13b8        ; → L_13B8    ; depth=2 if upper=$0C
    $13B6: A0 01      LDY #$01         ; else depth=1
L_13B8:
    $13B8: 8C BF 13   STY $13bf        ; (scratch, into data area)
    $13BB: AD FC 14   LDA $14fc
    $13BE: 29 02      AND #$02         ; bit 1 of frame counter
    $13C0: D0 09      BNE $13cb        ; → L_13CB    ; phase 1: note as-is
    ; phase 0: subtract $0C (one octave).
    $13C2: BD CF 14   LDA $14cf,x
    $13C5: 38         SEC
    $13C6: E9 0C      SBC #$0c
    $13C8: 4C CE 13   JMP $13ce        ; → L_13CE
L_13CB:
    $13CB: BD CF 14   LDA $14cf,x
L_13CE:
    $13CE: 0A         ASL a            ; ×2 = freq table index
    $13CF: A8         TAY
    $13D0: B9 FC 13   LDA $13fc,y
    $13D3: 8D D7 14   STA $14d7
    $13D6: B9 FD 13   LDA $13fd,y
    $13D9: AC BF 14   LDY $14bf
    $13DC: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $13DF: AD D7 14   LDA $14d7
    $13E2: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_13E5:
    ; ====== PER-VOICE LOOP TAIL ======
    ; Update voice-active flag for next iter:
    ;   $14FD nonzero → keep flag "active" ($FF, bit 7 set).
    ;   $14FD zero    → clear flag ($00, bit 7 clear → next voice in
    ;                   pause-state, skips pattern decode/effects).
    $13E5: A0 FF      LDY #$ff
    $13E7: AD FD 14   LDA $14fd
    $13EA: D0 01      BNE $13ed        ; → L_13ED
    $13EC: C8         INY              ; Y = 0
L_13ED:
    $13ED: 8C FE 14   STY $14fe
    $13F0: CA         DEX
    $13F1: 30 03      BMI $13f6        ; → L_13F6   ; done all voices
    $13F3: 4C 68 10   JMP $1068        ; → L_1068   ; next voice
L_13F6:
    ; Reset $14FE to $FF (voice-active) for the next play frame's
    ; first iteration, then RTS.
    $13F6: A9 FF      LDA #$ff
    $13F8: 8D FE 14   STA $14fe
    $13FB: 60         RTS
; ----- data gap $13FC-$1DE2 (2535 bytes) -----
; Data region: freq table at $13FC (2 bytes/semitone), instrument
; table at $150B (8 bytes/instrument starting at index 0), per-voice
; orderlist pointers at $15B3/$15B6, pattern pointer table at
; $15B9/$15E1, then orderlists + pattern data + scratch.

L_1DE3:
    ; init body. Wipes filter, V1/V2/V3 ctrl, sets vol=$0F, sets engine
    ; state $14ED = $40 (first-frame flag for the play loop).
    $1DE3: A9 00      LDA #$00
    $1DE5: 8D 17 D4   STA $d417      ;RES_FILT
    $1DE8: 8D 04 D4   STA $d404      ;V1_CTRL
    $1DEB: 8D 0B D4   STA $d40b      ;V2_CTRL
    $1DEE: 8D 12 D4   STA $d412      ;V3_CTRL
    $1DF1: A9 0F      LDA #$0f
    $1DF3: 8D 18 D4   STA $d418      ;VOL
    $1DF6: A9 40      LDA #$40
    $1DF8: 8D ED 14   STA $14ed
    $1DFB: 60         RTS
L_1DFC:
    ; sub_1003 body. Sets engine state $14ED = $C0 (end-of-song +
    ; first-frame both set). Next play frame takes the BMI/BVS combined
    ; branch at $1041 → silence + decay to $80 (RTS forever).
    $1DFC: A9 C0      LDA #$c0
    $1DFE: 8D ED 14   STA $14ed
    $1E01: 60         RTS
; ----- data gap $1E02-$1E1A (25 bytes) -----
