; ============================================================================
; Rob Hubbard - One Man and his Droid (1985 Mastertronic)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: data/C64Music/MUSICIANS/H/Hubbard_Rob/One_Man_and_his_Droid.sid
; Load:   $1000   Init: $1000   Play: $1012
; PSID:   14 subtune(s), default subtune 1
; Binary: $1000-$1F85 (3974 bytes)
;
; Auto-traced 1236 reachable code bytes from init+play. Hand commentary
; below derived from static analysis + tracing the per-voice state
; (registers $14E2..$1527 in the binary) and the freq/inst tables.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($1000): one-byte trampoline → $1F70 dispatcher.
;
;   $1F70 dispatcher with A = subtune index (0-based):
;     subtune 0 → JSR $1F17 (full main-engine init) + $151F = $FF
;                 (drum hijack flag inactive); the main 3-voice song.
;     subtune N → JSR $1006→$1F4E ($151D=0, drum-enabled), DEX, TXA,
;                 JMP $100F→$1F5C; sets $151E = (N-1) | $40 to arm
;                 the first-frame drum-init for sound-effect/percussion
;                 pattern (N-1).
;
;   The 14 subtunes split as:
;     subtune 0  → MAIN SONG (3-voice melody + filter, no drum engine)
;     subtune 1+ → DRUM/SFX patterns played through the secondary
;                  "drum engine" at $139F (commandeers V1+V2 for sample
;                  playback, configured by sub_1528 from $1600 table)
;
; play ($1012): every frame.
;   1. INC $151C (global frame counter — feeds vibrato LFO).
;   2. BIT $1510: bit 7 = end-of-song, bit 6 = first-frame.
;        - bit 7 set  → $1038: silence main voices, force $1510=$80,
;                       fall through to $139F (drum engine continues).
;        - bit 6 set  → $101C: ZERO per-voice state (v_olpos, v_patpos,
;                       v_dur, v_pitch) for all 3 voices, CLEAR $1510
;                       (now $00), continue to normal frame.
;        - both clear → $1052 normal frame.
;   3. Per-voice loop ($105F..$139C) for X=2..0 (V3,V2,V1).
;   4. After all voices, fall through to $139F: the drum/sample engine.
;
; PER-VOICE PROCESSING ($105F..$139C):
;   - $14E2,X holds the SID register offset (0/7/14) for voice X.
;     Stashed at $14E5 as the Y-index used for SID writes ($D400,Y etc.).
;   - Tick divider: $150D reloads from $150E ($02) on underflow.
;   - **Note-load gate** ($1066-$106C): only run note-load when
;     $150D == $150E. Skips note-load on frames where the divider
;     hasn't lapped yet (same one-frame defer trick as Action Biker).
;   - Otherwise: load next note from orderlist/pattern.
;
; PATTERN BYTES (per note, 1-3 bytes):
;   byte 0 = flags+duration:
;     bit 7 = "extension byte follows"
;     bit 6 = tie/legato (suppresses new note + gate)
;     bit 5 = "no_release" (preserved across HR check)
;     bits 0-4 = duration in ticks
;   byte 1 (only if bit 7 of byte 0 set) — extension byte:
;     if bit 7 set → byte is a PITCHBEND descriptor stored at $1517,X:
;                    bit 0 = direction (1=down, 0=up)
;                    bits 1-6 = pitchbend amount per frame
;     if bit 7 clear → byte is the new instrument index, stored at
;                    $14F8,X (full 8 bits, not masked).
;   byte n (always present after flags+optional extension) — semitone
;     pitch (0-95). Doubled for the 2-byte freq table stride.
;
; ORDERLIST: per-voice byte stream of pattern indices. $FF marker
; loops back to start of orderlist. The active orderlist pointer
; lo/hi for voice X is at $16E0,X / $16E3,X (copied from $16E6+
; subtune*6 by sub_1F17 — but only for subtune 0).
;
; FREQ TABLE: $1422, 96 semitones × 2 bytes little-endian.
; Verified: 96 entries from $0116 to $FD2E, neighbor ratio ≈ 1.0612
; (close to 12-TET 1.05946; the ~0.16% drift is Hubbard's hand-tuned
; semitones, audibly indistinguishable).
;
; INSTRUMENT TABLE: $1588, 8-byte records (≤32 instruments).
;   +0 pw_lo   +1 pw_hi   +2 ctrl   +3 AD   +4 SR
;   +5 vib_depth   +6 vib_period (also PWM step base)
;   +7 fx_flags: bit 0 = freq slide (drum/skydive)
;                bit 1 = alt slide  (mid-note bend)
;                bit 2 = octave-trill arpeggio (4-frame toggle)
;                bit 3 = linear PWM (vs bouncing $08/$0E PWM)
;
; DRUM/SAMPLE ENGINE ($139F..$1421 + sub_1528):
;   Self-modifying. sub_1528 reads a 16-byte "drum recipe" from
;   $1600 + (drum_idx<<4), splatters the first 14 bytes into
;   $D400..$D40D (= V1+V2 freq/pw/ctrl/ad/sr), stashes loop counters,
;   then PATCHES the operand of the instruction at $13D8 ($CE or $EE)
;   to choose DEC vs INC of $1520 each frame (rising vs falling
;   sample address). The main loop walks the freq table from one
;   end to the other and writes V1+V2 freq directly. $151F gates
;   the main per-voice freq writes off while the drum engine is
;   running, so V1+V2's normal melody bytes are suppressed.
;
; $151D / $151E semantics:
;   $151D  $00 = drum engine permitted (cleared by sub_1006→$1F4E)
;          ≠$00 = drum engine blocked.
;   $151E  bit 7 = drum-disabled (BIT $151E; BPL test at $13AC)
;          bit 6 = drum first-frame (calls sub_1528 once)
;          bits 0-3 = drum recipe index
;   $151F  $FF = drum not hijacking V1+V2 (normal melody writes go through)
;          $00 = drum is hijacking V1+V2 (skip melody freq writes)
;
; ============================================================================

; ======= init: =======
; Tiny trampoline; real entry is at $1F70.
init:
    $1000: 4C 70 1F   JMP $1f70        ; → L_1F70
; ----- data gap $1003-$1005 (3 bytes) -----

; Trampoline used by the dispatcher for subtune>0; jumps to $1F4E
; which zeroes $151D (= "drum engine enabled").
sub_1006:
    $1006: 4C 4E 1F   JMP $1f4e        ; → L_1F4E
; ----- data gap $1009-$100E (6 bytes) -----

; Trampoline used by the dispatcher for subtune>0; jumps to $1F5C
; which writes (subtune-1) | $40 into $151E (drum first-frame).
L_100F:
    $100F: 4C 5C 1F   JMP $1f5c        ; → L_1F5C

; ======= play: =======
; Called every frame by sidplayfp.
play:
    ; Global frame counter (used as triangle LFO source for vibrato
    ; and as the bit-2 toggle for the octave-trill arpeggio).
    $1012: EE 1C 15   INC $151c        ; $151C = frame counter
    ; $1510 holds main-engine state: bit 7 = end-of-song, bit 6 = first
    ; frame. BIT moves bit 7→N, bit 6→V.
    $1015: 2C 10 15   BIT $1510
    $1018: 30 1E      BMI $1038        ; → L_1038   ; end-of-song path
    $101A: 50 36      BVC $1052        ; → L_1052   ; normal frame
    ; First-frame setup (V flag set, falls through here).
    $101C: A9 00      LDA #$00
    $101E: 8D 1C 15   STA $151c        ; frame counter = 0
    $1021: A2 02      LDX #$02         ; loop X=2..0 (V3, V2, V1)
L_1023:
    ; Zero per-voice state for all 3 voices.
    $1023: 9D E6 14   STA $14e6,x      ; v_olpos,X = 0
    $1026: 9D E9 14   STA $14e9,x      ; v_patpos,X = 0
    $1029: 9D EC 14   STA $14ec,x      ; v_dur,X = 0
    $102C: 9D F5 14   STA $14f5,x      ; v_pitch,X = 0
    $102F: CA         DEX
    $1030: 10 F1      BPL $1023        ; → L_1023
    ; Clear first-frame sentinel. $1510 ends as $00.
    $1032: 8D 10 15   STA $1510        ; $1510 = $00
    $1035: 4C 52 10   JMP $1052        ; → L_1052
L_1038:
    ; End-of-song path. bit 7 of $1510 already set. If bit 6 also
    ; set ($C0 = binary default, or transitional), silence V1/V2/V3,
    ; reset volume, and rewrite $1510=$80 so subsequent frames
    ; take the same BMI branch but skip the silence (BVC succeeds).
    $1038: 50 15      BVC $104f        ; → L_104F   ; already silenced
    $103A: A9 00      LDA #$00
    $103C: 8D 04 D4   STA $d404         ;V1_CTRL
    $103F: 8D 0B D4   STA $d40b         ;V2_CTRL
    $1042: 8D 12 D4   STA $d412         ;V3_CTRL
    $1045: A9 0F      LDA #$0f
    $1047: 8D 18 D4   STA $d418         ;VOL
    $104A: A9 80      LDA #$80
    $104C: 8D 10 15   STA $1510         ; $1510 = $80 (silenced)
L_104F:
    ; Even with main engine silenced, the drum engine keeps running
    ; (some SFX patterns play to completion after the melody ends).
    $104F: 4C 9F 13   JMP $139f        ; → L_139F   ; drum engine
L_1052:
    ; --- Normal frame: process all 3 voices ---
    $1052: A2 02      LDX #$02         ; loop X=2..0 (V3, V2, V1)
    ; Tick divider for note-load gating.
    $1054: CE 0D 15   DEC $150d
    $1057: 10 06      BPL $105f        ; → L_105F   ; not yet wrapped
    $1059: AD 0E 15   LDA $150e        ; wrapped: reload from $150E
    $105C: 8D 0D 15   STA $150d        ; (binary default $150E = $01)
L_105F:
    ; Per-voice SID register offset lookup. $14E2,X = {0,7,14}.
    $105F: BD E2 14   LDA $14e2,x      ; SID voice offset for X
    $1062: 8D E5 14   STA $14e5        ; stash as Y-index for SID writes
    $1065: A8         TAY              ; Y = SID base offset
    ; **NOTE-LOAD GATE**: only run pattern advancement when the tick
    ; divider lands on its reload value. Otherwise fall through to the
    ; effects/PWM/slide block.
    $1066: AD 0D 15   LDA $150d
    $1069: CD 0E 15   CMP $150e
    $106C: D0 15      BNE $1083        ; → L_1083   ; skip note-load
    ; Note-load path: $16E0,X / $16E3,X = active orderlist pointer
    ; lo/hi. Loaded into ZP $FB/$FC for indirect addressing.
    $106E: BD E0 16   LDA $16e0,x      ; orderlist ptr lo
    $1071: 85 FB      STA $fb
    $1073: BD E3 16   LDA $16e3,x      ; orderlist ptr hi
    $1076: 85 FC      STA $fc
    ; $14EC,X = duration countdown. Decrement; if expired (BMI)
    ; load next note. Else fall through to sustain (L_116A).
    $1078: DE EC 14   DEC $14ec,x      ; v_dur,X
    $107B: 30 09      BMI $1086        ; → L_1086   ; expired: load next
    $107D: 4C 6A 11   JMP $116a        ; → L_116A   ; sustain
; ----- data gap $1080-$1082 (3 bytes) -----

L_1083:
    ; Note-load gated off this frame: jump straight to the
    ; effects/slide/PWM block (no pattern advance).
    $1083: 4C 91 11   JMP $1191        ; → L_1191
L_1086:
    ; Note-load: read orderlist[v_olpos]. $FF = loop back to start of
    ; orderlist (reset v_dur, v_olpos, v_patpos and retry).
    $1086: BC E6 14   LDY $14e6,x      ; v_olpos,X
    $1089: B1 FB      LDA ($fb),y      ; orderlist byte
    $108B: C9 FF      CMP #$ff         ; loop sentinel
    $108D: D0 11      BNE $10a0        ; → L_10A0   ; pattern index
    $108F: A9 00      LDA #$00
    $1091: 9D EC 14   STA $14ec,x      ; v_dur,X = 0
    $1094: 9D E6 14   STA $14e6,x      ; v_olpos,X = 0
    $1097: 9D E9 14   STA $14e9,x      ; v_patpos,X = 0
    $109A: 4C 86 10   JMP $1086        ; → L_1086   ; retry from start
; ----- data gap $109D-$109F (3 bytes) -----

; Normal pattern load: A holds pattern index. Pattern start addr from
; (c40b, c436) lo/hi tables at $16EC / $1712.
L_10A0:
    $10A0: A8         TAY              ; Y = pattern index
    $10A1: B9 EC 16   LDA $16ec,y      ; pat_lo[Y]
    $10A4: 85 FD      STA $fd          ; ZP $FD = pat_lo
    $10A6: B9 12 17   LDA $1712,y      ; pat_hi[Y]
    $10A9: 85 FE      STA $fe          ; ZP $FE = pat_hi
    ; Clear per-voice pitchbend descriptor (will be re-set if this
    ; note has an extension byte with bit 7).
    $10AB: A9 00      LDA #$00
    $10AD: 9D 17 15   STA $1517,x      ; v_slide,X = 0 (no pitchbend)
    ; Y = byte offset within the pattern.
    $10B0: BC E9 14   LDY $14e9,x      ; v_patpos,X
    ; $14FB = "ctrl gate mask"; default $FF. Cleared by DEC at $110E
    ; for tie/legato notes so the ctrl AND-write below strips the
    ; gate bit (keeping the prev note's gate state).
    $10B3: A9 FF      LDA #$ff
    $10B5: 8D FB 14   STA $14fb        ; gate-mask = $FF
    ; First pattern byte: flags<<5 | duration.
    $10B8: B1 FD      LDA ($fd),y
    $10BA: 9D EF 14   STA $14ef,x      ; v_flags,X = raw byte
    $10BD: 8D FC 14   STA $14fc        ; save for BIT/BPL tests
    $10C0: 29 1F      AND #$1f         ; duration (low 5 bits)
    $10C2: 9D EC 14   STA $14ec,x      ; v_dur,X = duration
    ; BIT $14FC: N = bit 7 (extension byte), V = bit 6 (tie).
    $10C5: 2C FC 14   BIT $14fc
    $10C8: 70 44      BVS $110e        ; → L_110E   ; tie: clear gate mask
    $10CA: FE E9 14   INC $14e9,x      ; advance v_patpos past flag byte
    $10CD: AD FC 14   LDA $14fc
    $10D0: 10 11      BPL $10e3        ; → L_10E3   ; no extension byte
    ; Extension byte present (bit 7 of flags was set).
    $10D2: C8         INY
    $10D3: B1 FD      LDA ($fd),y      ; extension byte
    $10D5: 10 06      BPL $10dd        ; → L_10DD   ; bit 7 clear: inst byte
    ; Bit 7 set → this is a PITCHBEND descriptor, not an inst index.
    ; Stored verbatim at $1517,X; consumed each frame in the slide
    ; block at $12AC..$12EF.
    $10D7: 9D 17 15   STA $1517,x      ; v_slide,X = pitchbend descriptor
    $10DA: 4C E0 10   JMP $10e0        ; → L_10E0
L_10DD:
    ; Bit 7 clear → A is the new instrument index. Stored without
    ; masking (full 8 bits — unlike AB which AND'd #$1F).
    $10DD: 9D F8 14   STA $14f8,x      ; v_inst,X = inst index
L_10E0:
    $10E0: FE E9 14   INC $14e9,x      ; advance past extension byte
L_10E3:
    ; Pitch byte. 0-95 semitones, stride 2 in freq table.
    $10E3: C8         INY
    $10E4: B1 FD      LDA ($fd),y      ; pitch byte
    $10E6: 9D F5 14   STA $14f5,x      ; v_pitch,X = pitch
    $10E9: 0A         ASL a            ; *2 for table stride
    $10EA: A8         TAY              ; Y = byte offset into freq table
    ; $151F gates SID freq writes: $00 = drum hijacking V1+V2 (skip);
    ; $FF = normal melody freq write.
    $10EB: AD 1F 15   LDA $151f
    $10EE: 10 21      BPL $1111        ; → L_1111   ; drum active: skip
    $10F0: B9 22 14   LDA $1422,y      ; freq_lo[pitch]
    $10F3: 8D FD 14   STA $14fd        ; temp save
    $10F6: B9 23 14   LDA $1423,y      ; freq_hi[pitch]
    $10F9: AC E5 14   LDY $14e5        ; Y = SID voice offset
    $10FC: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $10FF: 9D 11 15   STA $1511,x      ; v_fhi,X = freq_hi (live slide)
    $1102: AD FD 14   LDA $14fd
    $1105: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
    $1108: 9D 14 15   STA $1514,x      ; v_flo,X = freq_lo (live slide)
    $110B: 4C 11 11   JMP $1111        ; → L_1111
L_110E:
    ; Tie/legato: clear gate-mask bit 0 ($FF → $FE) so the ctrl
    ; AND-write below preserves whatever gate state the previous
    ; note left.
    $110E: CE FB 14   DEC $14fb        ; gate-mask $FF → $FE
L_1111:
    ; Write the instrument's voice registers (pw, ctrl, AD, SR).
    ; X is shifted by 3 (×8) to byte-index the 8-byte instrument record.
    $1111: AC E5 14   LDY $14e5        ; Y = SID voice offset
    $1114: BD F8 14   LDA $14f8,x      ; v_inst,X
    $1117: 8E FE 14   STX $14fe        ; save voice index X
    $111A: 0A         ASL a            ; inst * 2
    $111B: 0A         ASL a            ; inst * 4
    $111C: 0A         ASL a            ; inst * 8
    $111D: AA         TAX              ; X = byte offset in inst table
    $111E: BD 8A 15   LDA $158a,x      ; inst.ctrl
    $1121: 8D FF 14   STA $14ff        ; stash raw ctrl
    ; $151F gates ctrl/AD/SR/PW writes too: skip when drum hijacking.
    $1124: AD 1F 15   LDA $151f
    $1127: 10 21      BPL $114a        ; → L_114A   ; drum active: skip
    $1129: BD 8A 15   LDA $158a,x      ; ctrl again
    $112C: 2D FB 14   AND $14fb        ; AND gate-mask (tie clears bit 0)
    $112F: 99 04 D4   STA $d404,y      ;V1_CTRL,Y
    $1132: BD 88 15   LDA $1588,x      ; inst.pw_lo
    $1135: 99 02 D4   STA $d402,y      ;V1_PW_LO,Y
    $1138: BD 89 15   LDA $1589,x      ; inst.pw_hi
    $113B: 99 03 D4   STA $d403,y      ;V1_PW_HI,Y
    $113E: BD 8B 15   LDA $158b,x      ; inst.AD
    $1141: 99 05 D4   STA $d405,y      ;V1_AD,Y
    $1144: BD 8C 15   LDA $158c,x      ; inst.SR
    $1147: 99 06 D4   STA $d406,y      ;V1_SR,Y
L_114A:
    ; Restore voice X. $14F2,X mirrors inst.ctrl for HR check below.
    $114A: AE FE 14   LDX $14fe        ; restore voice X
    $114D: AD FF 14   LDA $14ff        ; saved raw inst.ctrl
    $1150: 9D F2 14   STA $14f2,x      ; v_ctrl,X = raw inst.ctrl
    ; Advance v_patpos past pitch byte. Peek next byte: $FF = end of
    ; pattern → zero v_patpos, bump v_olpos.
    $1153: FE E9 14   INC $14e9,x
    $1156: BC E9 14   LDY $14e9,x
    $1159: B1 FD      LDA ($fd),y      ; peek next byte
    $115B: C9 FF      CMP #$ff
    $115D: D0 08      BNE $1167        ; → L_1167   ; not pattern-end
    $115F: A9 00      LDA #$00
    $1161: 9D E9 14   STA $14e9,x      ; v_patpos,X = 0
    $1164: FE E6 14   INC $14e6,x      ; v_olpos,X += 1
L_1167:
    ; Hand off to the post-note "shared" path (HR check + effects).
    $1167: 4C 89 13   JMP $1389        ; → L_1389   ; per-voice tail
L_116A:
    ; --- Sustain path (current note hasn't expired) ---
    ; Drum hijacking? $151F bit 7 clear → drum has taken V1+V2: skip
    ; HR check (would write the wrong ctrl). Just go to the tail.
    $116A: AD 1F 15   LDA $151f
    $116D: 30 03      BMI $1172        ; → L_1172   ; melody mode
    $116F: 4C 89 13   JMP $1389        ; → L_1389
L_1172:
    ; HR (hard-restart) check: if v_dur expired (=0) AND no_release
    ; flag (bit 5 of v_flags) is clear, write ctrl-without-gate +
    ; AD=0 + SR=0 to kill the envelope cleanly before the next gate-on.
    $1172: AC E5 14   LDY $14e5
    $1175: BD EF 14   LDA $14ef,x      ; v_flags,X
    $1178: 29 20      AND #$20         ; test no_release flag
    $117A: D0 15      BNE $1191        ; → L_1191   ; no_release: skip HR
    $117C: BD EC 14   LDA $14ec,x      ; v_dur,X
    $117F: D0 10      BNE $1191        ; → L_1191   ; still ticking: skip
    $1181: BD F2 14   LDA $14f2,x      ; v_ctrl,X (saved inst.ctrl)
    $1184: 29 FE      AND #$fe         ; clear gate bit
    $1186: 99 04 D4   STA $d404,y      ;V1_CTRL,Y
    $1189: A9 00      LDA #$00
    $118B: 99 05 D4   STA $d405,y      ;V1_AD,Y
    $118E: 99 06 D4   STA $d406,y      ;V1_SR,Y
L_1191:
    ; --- Effects shared block: vibrato/PWM/slide/arpeggio ---
    ; Once again: skip everything if drum is hijacking V1+V2.
    $1191: AD 1F 15   LDA $151f
    $1194: 30 03      BMI $1199        ; → L_1199   ; melody mode
    $1196: 4C 89 13   JMP $1389        ; → L_1389
L_1199:
    ; Index into instrument table (inst<<3 → byte offset).
    $1199: BD F8 14   LDA $14f8,x      ; v_inst,X
    $119C: 0A         ASL a
    $119D: 0A         ASL a
    $119E: 0A         ASL a
    $119F: A8         TAY              ; Y = inst byte offset
    $11A0: 8C 0F 15   STY $150f        ; remember inst offset
    ; Read instrument's effects parameters from bytes 5,6,7 of record:
    ;   $158D,Y = vib_depth     → $1500
    ;   $158E,Y = vib_period    → $1501  (also PWM step base)
    ;   $158F,Y = fx_flags      → $151A
    $11A3: B9 8F 15   LDA $158f,y      ; inst.fx_flags
    $11A6: 8D 1A 15   STA $151a
    $11A9: B9 8E 15   LDA $158e,y      ; inst.vib_period
    $11AC: 8D 01 15   STA $1501
    $11AF: B9 8D 15   LDA $158d,y      ; inst.vib_depth
    $11B2: 8D 00 15   STA $1500
    $11B5: F0 6F      BEQ $1226        ; → L_1226   ; depth=0: no vibrato
    ; --- Vibrato (triangle LFO from frame counter) ---
    $11B7: AD 1C 15   LDA $151c
    $11BA: 29 07      AND #$07
    $11BC: C9 04      CMP #$04
    $11BE: 90 02      BCC $11c2        ; → L_11C2
    $11C0: 49 07      EOR #$07         ; fold 5→2,6→1,7→0
L_11C2:
    $11C2: 8D 06 15   STA $1506        ; LFO value 0..4
    ; (freq[pitch+1] - freq[pitch]) >> vib_depth = per-step delta.
    $11C5: BD F5 14   LDA $14f5,x      ; v_pitch,X
    $11C8: 0A         ASL a            ; *2
    $11C9: A8         TAY
    $11CA: 38         SEC
    $11CB: B9 24 14   LDA $1424,y      ; freq_lo[pitch+1]
    $11CE: F9 22 14   SBC $1422,y
    $11D1: 8D 02 15   STA $1502        ; delta_lo
    $11D4: B9 25 14   LDA $1425,y      ; freq_hi[pitch+1]
    $11D7: F9 23 14   SBC $1423,y
L_11DA:
    $11DA: 4A         LSR a            ; >>1 (vib_depth iterations)
    $11DB: 6E 02 15   ROR $1502
    $11DE: CE 00 15   DEC $1500
    $11E1: 10 F7      BPL $11da        ; → L_11DA
    $11E3: 8D 03 15   STA $1503        ; delta_hi (shifted)
    ; Base = freq[pitch].
    $11E6: B9 22 14   LDA $1422,y
    $11E9: 8D 04 15   STA $1504        ; base_lo
    $11EC: B9 23 14   LDA $1423,y
    $11EF: 8D 05 15   STA $1505        ; base_hi
    ; Skip vibrato sum on very short notes (dur < 8).
    $11F2: BD EF 14   LDA $14ef,x
    $11F5: 29 1F      AND #$1f
    $11F7: C9 08      CMP #$08
    $11F9: 90 1C      BCC $1217        ; → L_1217
    $11FB: AC 06 15   LDY $1506        ; LFO value
L_11FE:
    ; Add delta LFO times.
    $11FE: 88         DEY
    $11FF: 30 16      BMI $1217        ; → L_1217
    $1201: 18         CLC
    $1202: AD 04 15   LDA $1504
    $1205: 6D 02 15   ADC $1502
    $1208: 8D 04 15   STA $1504
    $120B: AD 05 15   LDA $1505
    $120E: 6D 03 15   ADC $1503
    $1211: 8D 05 15   STA $1505
    $1214: 4C FE 11   JMP $11fe        ; → L_11FE
L_1217:
    ; Write modulated freq to SID.
    $1217: AC E5 14   LDY $14e5
    $121A: AD 04 15   LDA $1504
    $121D: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
    $1220: AD 05 15   LDA $1505
    $1223: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
L_1226:
    ; --- PWM ---
    ; fx_flags bit 3 = LINEAR PWM (one-way; pw_lo += step every frame).
    ; fx_flags bit 3 clear = BOUNCING PWM ($08/$0E hardcoded bounds).
    $1226: AD 1A 15   LDA $151a
    $1229: 29 08      AND #$08
    $122B: F0 15      BEQ $1242        ; → L_1242   ; bouncing PWM
    ; Linear PWM (vib_period acts as 8-bit ramp speed).
    $122D: AC 0F 15   LDY $150f        ; inst byte offset
    $1230: B9 88 15   LDA $1588,y      ; inst.pw_lo
    $1233: 6D 01 15   ADC $1501        ; += vib_period
    $1236: 99 88 15   STA $1588,y      ; write back
    $1239: AC E5 14   LDY $14e5
    $123C: 99 02 D4   STA $d402,y      ;V1_PW_LO,Y
    $123F: 4C A9 12   JMP $12a9        ; → L_12A9
L_1242:
    ; Bouncing PWM block (Hubbard's $08/$0E direction-flip bounds).
    ; vib_period byte: low 5 bits = step interval, high 3 bits = step size.
    $1242: AD 01 15   LDA $1501        ; vib_period (PWM speed)
    $1245: F0 62      BEQ $12a9        ; → L_12A9   ; speed=0: no PWM
    $1247: AC 0F 15   LDY $150f
    $124A: 29 1F      AND #$1f         ; step interval
    $124C: DE 07 15   DEC $1507,x      ; voice pwm-step counter
    $124F: 10 58      BPL $12a9        ; → L_12A9   ; not yet time
    $1251: 9D 07 15   STA $1507,x      ; reload counter
    $1254: AD 01 15   LDA $1501
    $1257: 29 E0      AND #$e0         ; step size
    $1259: 8D 1B 15   STA $151b
    $125C: BD 0A 15   LDA $150a,x      ; pwm direction flag
    $125F: D0 1A      BNE $127b        ; → L_127B   ; nonzero = SUB
    ; ADD direction: pw += step.
    $1261: AD 1B 15   LDA $151b
    $1264: 18         CLC
    $1265: 79 88 15   ADC $1588,y      ; pw_lo += step
    $1268: 48         PHA
    $1269: B9 89 15   LDA $1589,y
    $126C: 69 00      ADC #$00         ; carry into pw_hi
    $126E: 29 0F      AND #$0f         ; 12-bit PW
    $1270: 48         PHA
    $1271: C9 0E      CMP #$0e         ; hit upper bound?
    $1273: D0 1D      BNE $1292        ; → L_1292
    $1275: FE 0A 15   INC $150a,x      ; flip → SUB
    $1278: 4C 92 12   JMP $1292        ; → L_1292
L_127B:
    ; SUB direction: pw -= step.
    $127B: 38         SEC
    $127C: B9 88 15   LDA $1588,y
    $127F: ED 1B 15   SBC $151b
    $1282: 48         PHA
    $1283: B9 89 15   LDA $1589,y
    $1286: E9 00      SBC #$00
    $1288: 29 0F      AND #$0f
    $128A: 48         PHA
    $128B: C9 08      CMP #$08         ; hit lower bound?
    $128D: D0 03      BNE $1292        ; → L_1292
    $128F: DE 0A 15   DEC $150a,x      ; flip → ADD
L_1292:
    ; Write updated pw back to instrument record + SID.
    $1292: 8E FE 14   STX $14fe
    $1295: AE E5 14   LDX $14e5        ; X = SID offset
    $1298: 68         PLA
    $1299: 99 89 15   STA $1589,y      ; inst.pw_hi
    $129C: 9D 03 D4   STA $d403,x      ;V1_PW_HI,X
    $129F: 68         PLA
    $12A0: 99 88 15   STA $1588,y      ; inst.pw_lo
    $12A3: 9D 02 D4   STA $d402,x      ;V1_PW_LO,X
    $12A6: AE FE 14   LDX $14fe
L_12A9:
    ; --- Pitchbend / portamento ---
    ; $1517,X = pitchbend descriptor (set by extension byte with bit 7).
    ; bits 1-6 = step amount, bit 0 = direction (1=down, 0=up).
    $12A9: AC E5 14   LDY $14e5
    $12AC: BD 17 15   LDA $1517,x      ; v_slide,X
    $12AF: F0 3F      BEQ $12f0        ; → L_12F0   ; no slide
    $12B1: 29 7E      AND #$7e         ; mask out bit 0 and bit 7
    $12B3: 8D FE 14   STA $14fe        ; pitchbend amount
    $12B6: BD 17 15   LDA $1517,x
    $12B9: 29 01      AND #$01         ; direction bit
    $12BB: F0 1B      BEQ $12d8        ; → L_12D8   ; direction=up
    ; DOWN: 16-bit freq -= amount (operates on the LIVE freq held
    ; in v_fhi/v_flo, not the freq table).
    $12BD: 38         SEC
    $12BE: BD 14 15   LDA $1514,x      ; v_flo
    $12C1: ED FE 14   SBC $14fe
    $12C4: 9D 14 15   STA $1514,x
    $12C7: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
    $12CA: BD 11 15   LDA $1511,x      ; v_fhi
    $12CD: E9 00      SBC #$00
    $12CF: 9D 11 15   STA $1511,x
    $12D2: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $12D5: 4C F0 12   JMP $12f0        ; → L_12F0
L_12D8:
    ; UP: 16-bit freq += amount.
    $12D8: 18         CLC
    $12D9: BD 14 15   LDA $1514,x
    $12DC: 6D FE 14   ADC $14fe
    $12DF: 9D 14 15   STA $1514,x
    $12E2: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
    $12E5: BD 11 15   LDA $1511,x
    $12E8: 69 00      ADC #$00
    $12EA: 9D 11 15   STA $1511,x
    $12ED: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
L_12F0:
    ; --- Drum/skydive slide (fx_flags bit 0) ---
    ; Falling-pitch tom/kick sweep: DEC v_fhi each frame, write old
    ; value, then mute via AND #$FE on ctrl (or $80 if freq_hi hit 0).
    $12F0: AD 1A 15   LDA $151a
    $12F3: 29 01      AND #$01
    $12F5: F0 35      BEQ $132c        ; → L_132C   ; flag clear
    $12F7: BD 11 15   LDA $1511,x      ; v_fhi
    $12FA: F0 30      BEQ $132c        ; → L_132C   ; already 0
    $12FC: BD EC 14   LDA $14ec,x      ; v_dur
    $12FF: F0 2B      BEQ $132c        ; → L_132C   ; expired
    $1301: BD EF 14   LDA $14ef,x      ; v_flags
    $1304: 29 1F      AND #$1f         ; orig dur
    $1306: 38         SEC
    $1307: E9 01      SBC #$01
    $1309: DD EC 14   CMP $14ec,x
    $130C: AC E5 14   LDY $14e5
    $130F: 90 10      BCC $1321        ; → L_1321   ; past midpoint
    $1311: BD 11 15   LDA $1511,x      ; v_fhi
    $1314: DE 11 15   DEC $1511,x
    $1317: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $131A: BD F2 14   LDA $14f2,x      ; v_ctrl
    $131D: 29 FE      AND #$fe         ; gate off
    $131F: D0 08      BNE $1329        ; → L_1329
L_1321:
    $1321: BD 11 15   LDA $1511,x
    $1324: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $1327: A9 80      LDA #$80         ; test bit (silence) on drum-end
L_1329:
    $1329: 99 04 D4   STA $d404,y      ;V1_CTRL,Y
L_132C:
    ; --- "Alt slide" (fx_flags bit 1): mid-note pitch fall ---
    ; Activates after orig_dur >= 16 ticks have passed (v_dur < 24),
    ; on odd frame counter ticks, dec freq_hi by 1.
    $132C: AD 1A 15   LDA $151a
    $132F: 29 02      AND #$02
    $1331: F0 25      BEQ $1358        ; → L_1358
    $1333: BD EF 14   LDA $14ef,x      ; orig dur
    $1336: 29 1F      AND #$1f
    $1338: C9 10      CMP #$10
    $133A: 90 1C      BCC $1358        ; → L_1358   ; dur<16 skip
    $133C: BD EC 14   LDA $14ec,x
    $133F: C9 18      CMP #$18
    $1341: B0 15      BCS $1358        ; → L_1358   ; v_dur>=24 skip
    $1343: AD 1C 15   LDA $151c
    $1346: 29 01      AND #$01
    $1348: F0 0E      BEQ $1358        ; → L_1358   ; even frame skip
    $134A: BD 11 15   LDA $1511,x
    $134D: F0 09      BEQ $1358        ; → L_1358   ; already 0
    $134F: DE 11 15   DEC $1511,x
    $1352: AC E5 14   LDY $14e5
    $1355: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
L_1358:
    ; --- Octave-trill arpeggio (fx_flags bit 2) ---
    ; Every 4 frames toggle: pitch vs pitch+12. Hubbard's signature
    ; "two-note" trill (sounds like a fast octave hop).
    $1358: AD 1A 15   LDA $151a
    $135B: 29 04      AND #$04
    $135D: F0 2A      BEQ $1389        ; → L_1389
    $135F: AD 1C 15   LDA $151c
    $1362: 29 04      AND #$04         ; bit 2 of frame ctr (4-on / 4-off)
    $1364: D0 09      BNE $136f        ; → L_136F   ; +0 semitones
    $1366: BD F5 14   LDA $14f5,x      ; v_pitch
    $1369: 18         CLC
    $136A: 69 0C      ADC #$0c         ; +12 (one octave up)
    $136C: 4C 72 13   JMP $1372        ; → L_1372
L_136F:
    $136F: BD F5 14   LDA $14f5,x      ; v_pitch (no offset)
L_1372:
    $1372: 0A         ASL a
    $1373: A8         TAY
    $1374: B9 22 14   LDA $1422,y      ; freq_lo
    $1377: 8D FD 14   STA $14fd
    $137A: B9 23 14   LDA $1423,y      ; freq_hi
    $137D: AC E5 14   LDY $14e5
    $1380: 99 01 D4   STA $d401,y      ;V1_FREQ_HI,Y
    $1383: AD FD 14   LDA $14fd
    $1386: 99 00 D4   STA $d400,y      ;V1_FREQ_LO,Y
L_1389:
    ; --- Per-voice tail: decide whether drum engine writes to V1/V2 ---
    ; Recompute $151F = $00 (drum hijacking) if $151D==0 AND $151E
    ; bit 7 clear; else $FF (melody owns freq writes).
    $1389: A0 FF      LDY #$ff
    $138B: AD 1D 15   LDA $151d
    $138E: D0 06      BNE $1396        ; → L_1396   ; drum disabled → Y=$FF
    $1390: AD 1E 15   LDA $151e
    $1393: 30 01      BMI $1396        ; → L_1396   ; drum disabled → Y=$FF
    $1395: C8         INY              ; Y = $00 (drum active)
L_1396:
    $1396: 8C 1F 15   STY $151f        ; $151F = drum hijack flag
    ; Next voice or fall through to drum engine.
    $1399: CA         DEX
    $139A: 30 03      BMI $139f        ; → L_139F
    $139C: 4C 5F 10   JMP $105f        ; → L_105F   ; next voice
L_139F:
    ; ======= DRUM/SAMPLE ENGINE =======
    ; Runs every frame after the 3-voice melody pass. Walks freq
    ; table from one end to the other to play sampled percussion,
    ; commandeering V1+V2 freq registers. V3 is left alone (so
    ; melody V3 is always audible).
    $139F: A9 FF      LDA #$ff
    $13A1: 8D 1F 15   STA $151f        ; default $FF (becomes $00 on entry to next melody frame)
    $13A4: AD 1D 15   LDA $151d
    $13A7: D0 05      BNE $13ae        ; → L_13AE   ; drum disabled
    $13A9: 2C 1E 15   BIT $151e
    $13AC: 10 01      BPL $13af        ; → L_13AF   ; drum enabled
L_13AE:
    $13AE: 60         RTS
L_13AF:
    $13AF: 50 03      BVC $13b4        ; → L_13B4   ; not first-frame
    $13B1: 20 28 15   JSR $1528        ; → sub_1528 ; first-frame drum setup
L_13B4:
    ; Decrement drum sample-position counter (operand $1520 is patched
    ; in/out to $CE [DEC] or $EE [INC] by sub_1528 to play forward/back).
    $13B4: CE 21 15   DEC $1521        ; sample-step counter
    $13B7: 10 F5      BPL $13ae        ; → L_13AE   ; not yet time
    $13B9: AD 27 15   LDA $1527        ; drum config byte
    $13BC: 29 0F      AND #$0f         ; low nibble = step interval
    $13BE: 8D 21 15   STA $1521        ; reload counter
    $13C1: AD 20 15   LDA $1520        ; current sample address
    $13C4: CD 22 15   CMP $1522        ; reached end-of-sample?
    $13C7: D0 0F      BNE $13d8        ; → L_13D8   ; not yet
    ; End-of-sample: silence V1+V2, mark drum disabled ($151E=$FF).
    $13C9: A2 00      LDX #$00
    $13CB: 8E 04 D4   STX $d404         ;V1_CTRL
    $13CE: 8E 0B D4   STX $d40b         ;V2_CTRL
    $13D1: CA         DEX              ; X = $FF
    $13D2: 8E 1E 15   STX $151e        ; drum disabled
    $13D5: 4C AE 13   JMP $13ae        ; → L_13AE
L_13D8:
    ; SELF-MODIFIED INSTRUCTION: opcode at $13D8 is $CE (DEC) or $EE
    ; (INC) depending on patch by sub_1528. Operand is fixed at $1520.
    $13D8: CE 20 15   DEC $1520        ; or INC, patched
    $13DB: 0A         ASL a
    $13DC: A8         TAY
    $13DD: 2C 27 15   BIT $1527        ; drum config
    $13E0: 30 20      BMI $1402        ; → L_1402
    $13E2: 70 0C      BVS $13f0        ; → L_13F0
    ; Write V1 freq from freq table at current sample position.
    $13E4: B9 22 14   LDA $1422,y
    $13E7: 8D 00 D4   STA $d400         ;V1_FREQ_LO
    $13EA: B9 23 14   LDA $1423,y
    $13ED: 8D 01 D4   STA $d401         ;V1_FREQ_HI
L_13F0:
    ; Write V2 freq at sample_addr - offset_byte ($1523).
    $13F0: 98         TYA
    $13F1: 38         SEC
    $13F2: ED 23 15   SBC $1523        ; phase offset for V2
    $13F5: A8         TAY
    $13F6: B9 22 14   LDA $1422,y
    $13F9: 8D 07 D4   STA $d407         ;V2_FREQ_LO
    $13FC: B9 23 14   LDA $1423,y
    $13FF: 8D 08 D4   STA $d408         ;V2_FREQ_HI
L_1402:
    ; Optional toggle of V1 ctrl bit 0 (gate hammer) each step.
    $1402: 2C 24 15   BIT $1524
    $1405: 10 0B      BPL $1412        ; → L_1412
    $1407: AD 25 15   LDA $1525
    $140A: 49 01      EOR #$01
    $140C: 8D 04 D4   STA $d404         ;V1_CTRL
    $140F: 8D 25 15   STA $1525
L_1412:
    ; Optional toggle of V2 ctrl bit 0 each step.
    $1412: 50 0B      BVC $141f        ; → L_141F
    $1414: AD 26 15   LDA $1526
    $1417: 49 01      EOR #$01
    $1419: 8D 0B D4   STA $d40b         ;V2_CTRL
    $141C: 8D 26 15   STA $1526
L_141F:
    $141F: 4C AE 13   JMP $13ae        ; → L_13AE
; ----- data gap $1422-$1527 (262 bytes) -----
; $1422-$14E1: 96 × 2-byte freq table (192 bytes), then 2 bytes pad.
; $14E2-$14E4: SID voice base offsets [0, 7, 14].
; $14E5-$152F: scratch and per-voice state, see top of file.

; --- DRUM FIRST-FRAME SETUP ---
; Reads a 16-byte "drum recipe" from $1600 + (drum_idx<<4), splatters
; the first 14 bytes into $D400..$D40D (V1+V2 freq/pw/ctrl/ad/sr),
; stashes loop counters at $1520-$1527, then self-modifies the
; opcode at $13D8 to choose DEC (falling) or INC (rising) sample-
; address walk.
sub_1528:
    $1528: A9 00      LDA #$00
    $152A: 8D 04 D4   STA $d404         ;V1_CTRL
    $152D: 8D 0B D4   STA $d40b         ;V2_CTRL
    $1530: 8D 21 15   STA $1521        ; sample-step counter = 0
    ; Drum index from $151E low 4 bits; clear bit 6 so this runs once.
    $1533: AD 1E 15   LDA $151e
    $1536: 29 0F      AND #$0f
    $1538: 8D 1E 15   STA $151e
    ; *16 (16-byte stride per drum recipe).
    $153B: 0A         ASL a
    $153C: 0A         ASL a
    $153D: 0A         ASL a
    $153E: 0A         ASL a
    $153F: A8         TAY
    ; Copy named bytes from recipe to scratch state.
    $1540: B9 00 16   LDA $1600,y      ; recipe[0] = drum config
    $1543: 8D 27 15   STA $1527
    $1546: B9 01 16   LDA $1601,y      ; recipe[1] = start sample addr
    $1549: 8D 20 15   STA $1520
    $154C: B9 0F 16   LDA $160f,y      ; recipe[15] = end sample addr
    $154F: 8D 22 15   STA $1522
    $1552: B9 08 16   LDA $1608,y      ; recipe[8] = gate-hammer flags
    $1555: 8D 24 15   STA $1524
    $1558: 29 3F      AND #$3f         ; low 6 bits = phase offset
    $155A: 8D 23 15   STA $1523
    $155D: B9 05 16   LDA $1605,y      ; recipe[5] = V1 ctrl seed
    $1560: 8D 25 15   STA $1525
    $1563: B9 0C 16   LDA $160c,y      ; recipe[12] = V2 ctrl seed
    $1566: 8D 26 15   STA $1526
    ; Splatter the next 14 bytes of the recipe into $D400-$D40D.
    ; That is: V1 freq/pw/ctrl/ad/sr, then V2 freq/pw/ctrl/ad/sr.
    $1569: A2 00      LDX #$00
L_156B:
    $156B: B9 01 16   LDA $1601,y
    $156E: 9D 00 D4   STA $d400,x       ;V1_FREQ_LO,X
    $1571: C8         INY
    $1572: E8         INX
    $1573: E0 0E      CPX #$0e
    $1575: D0 F4      BNE $156b        ; → L_156B
    ; Self-modify the opcode at $13D8: bits 4-5 of recipe[0] choose
    ; DEC ($CE, falling) or INC ($EE, rising) walk through freq table.
    $1577: AD 27 15   LDA $1527
    $157A: 29 30      AND #$30
    $157C: A0 EE      LDY #$ee         ; INC abs opcode
    $157E: C9 20      CMP #$20
    $1580: F0 02      BEQ $1584        ; → L_1584
    $1582: A0 CE      LDY #$ce         ; DEC abs opcode
L_1584:
    $1584: 8C D8 13   STY $13d8        ; patches the opcode byte
    $1587: 60         RTS
; ----- data gap $1588-$1F16 (2447 bytes) -----
; $1588-$15FF:  Instrument table (8-byte records × 14 instruments).
;               +0 pw_lo  +1 pw_hi  +2 ctrl  +3 AD  +4 SR
;               +5 vib_depth  +6 vib_period  +7 fx_flags
; $1600-$16DF:  Drum recipe table (16-byte records × 14 drums).
;               +0 config (bits 0-3 step interval, 4-5 direction,
;                          6-7 V1/V2 freq-write flags)
;               +1..+7  V1 freq_lo/freq_hi/pw_lo/pw_hi/ctrl/AD/SR seed
;               +8 V2/V1 gate-hammer flags (low 6 bits = phase offset)
;               +9..+14 V2 freq_lo/freq_hi/pw_lo/pw_hi/ctrl/AD/SR seed
;               +15 end sample address
; $16E0-$16E5:  Active per-voice orderlist pointers (lo[0..2], hi[0..2]).
; $16E6-$16EB:  Subtune-0 orderlist pointers (copied to $16E0 by $1F17).
; $16EC-$1711:  pat_lo[Y] — pattern-start lo-byte table.
; $1712-$1737:  pat_hi[Y] — pattern-start hi-byte table.
; $1738+     :  pattern data (variable-length, terminated by $FF).
; $1F00-$1F16:  more data tables.

; --- DRUM-ONLY SUBTUNE INIT TRAMPOLINE ---
; Copies 6 bytes from $16E6+subtune*6 to $16E0 (active orderlist) and
; silences/sets VOL. Used only by subtune 0 path. For subtune > 0 the
; dispatcher routes to L_1F5C instead which arms the drum engine.
sub_1F17:
    $1F17: A0 00      LDY #$00
    $1F19: 0A         ASL a            ; subtune * 2
    $1F1A: 8D FE 14   STA $14fe
    $1F1D: 0A         ASL a            ; subtune * 4
    $1F1E: 18         CLC
    $1F1F: 6D FE 14   ADC $14fe        ; subtune * 6
    $1F22: AA         TAX
L_1F23:
    $1F23: BD E6 16   LDA $16e6,x
    $1F26: 99 E0 16   STA $16e0,y
    $1F29: E8         INX
    $1F2A: C8         INY
    $1F2B: C0 06      CPY #$06
    $1F2D: D0 F4      BNE $1f23        ; → L_1F23
    $1F2F: A9 00      LDA #$00
    $1F31: 8D 04 D4   STA $d404         ;V1_CTRL
    $1F34: 8D 0B D4   STA $d40b         ;V2_CTRL
    $1F37: 8D 12 D4   STA $d412         ;V3_CTRL
    $1F3A: 8D 17 D4   STA $d417         ;RES_FILT
    $1F3D: A9 0F      LDA #$0f
    $1F3F: 8D 18 D4   STA $d418         ;VOL
    $1F42: A9 40      LDA #$40         ; bit 6 = first-frame sentinel
    $1F44: 8D 10 15   STA $1510        ; main-engine first-frame
    $1F47: 60         RTS
; ----- data gap $1F48-$1F4D (6 bytes) -----

; --- enables drum engine (clears $151D = "drum permitted") ---
L_1F4E:
    $1F4E: A9 00      LDA #$00
    $1F50: 8D 1D 15   STA $151d        ; drum-permitted = $00
    $1F53: 60         RTS
; ----- data gap $1F54-$1F5B (8 bytes) -----

; --- arms drum first-frame for subtune > 0 ---
; If $151D ≠ 0 (drum was previously blocked) the caller's subtune
; index is stashed directly into $151E. Otherwise we OR in $40 to
; mark "first-frame", set vol $0F, return.
L_1F5C:
    $1F5C: AE 1D 15   LDX $151d
    $1F5F: F0 04      BEQ $1f65        ; → L_1F65
    $1F61: 8E 1E 15   STX $151e
    $1F64: 60         RTS
L_1F65:
    $1F65: 09 40      ORA #$40         ; A = subtune | $40
    $1F67: 8D 1E 15   STA $151e        ; drum first-frame
    $1F6A: A9 0F      LDA #$0f
    $1F6C: 8D 18 D4   STA $d418         ;VOL
    $1F6F: 60         RTS

; --- INIT DISPATCHER ---
; Entry: A = subtune index (0-based; PSID default subtune 1 → A=0).
;   subtune 0   → JSR $1F17 (main-engine init), $151F=$FF (no drum hijack).
;   subtune > 0 → JSR $1006→$1F4E (drum-permitted=0), DEX, TXA,
;                 JMP $100F→$1F5C (arm drum first-frame).
;
; The main song lives at subtune 0; subtunes 1-13 are individual
; drum/SFX patterns played through the secondary drum engine.
L_1F70:
    $1F70: AA         TAX
    $1F71: E0 00      CPX #$00
    $1F73: F0 08      BEQ $1f7d        ; → L_1F7D   ; subtune 0: main song
    $1F75: 20 06 10   JSR $1006        ; → sub_1006 ; (→ $1F4E)
    $1F78: CA         DEX              ; subtune-1 = drum recipe index
    $1F79: 8A         TXA
    $1F7A: 4C 0F 10   JMP $100f        ; → L_100F   ; (→ $1F5C)
L_1F7D:
    $1F7D: 20 17 1F   JSR $1f17        ; → sub_1F17 ; main-engine init
    $1F80: A9 FF      LDA #$ff
    $1F82: 8D 1F 15   STA $151f        ; drum NOT hijacking V1+V2
    $1F85: 60         RTS
