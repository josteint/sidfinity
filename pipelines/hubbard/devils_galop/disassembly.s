; ============================================================================
; Rob Hubbard - Devils Galop (1985 Rob Hubbard)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: demo/hubbard/Devils_Galop_original.sid
; Load:   $0A18   Init: $0A18   Play: $0A1B
; PSID:   1 subtune
; Binary: $0A18-$18F6 (3807 bytes)
;
; Auto-traced 997 reachable code bytes from init+play
; (tools/seed_disassembly.py). Commentary hand-derived from static
; analysis + byte-level data dumps.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ---------------
;
; init ($0A18) is a one-byte trampoline JMP $18B3. The real init at $18B3
; does two jobs:
;
;   1. SELF-MODIFYING CODE: writes operand bytes into the play loop so
;      the LDA $1795,X / LDA $1796,X / LDA $1797,Y / LDA $1798,Y lookups
;      (which the static disassembly shows reading from $1795-$1798)
;      actually read from $0A1E-$0A53 at runtime. The pre-init operands
;      ($1795..$1798) are 4 bytes of $00 in the binary; init's patch
;      rewrites the operand lo/hi bytes to point into the "data gap"
;      $0A1E-$12EA where the orderlists, pattern table, and pattern
;      data live.
;
;      Patched sites + new operand:
;        $135A/B → $0A1E   (orderlist_lo[3 voices])
;        $135F/0 → $0A21   (orderlist_hi[3 voices])
;        $138D/E → $0A24   (pattern_lo[44])
;        $1392/3 → $0A50   (pattern_hi[44])
;        $13AC   → $FF     (LDA #$FF — fade-base immediate)
;        $13B3/4 → $EA,$EA (NOP NOP — kills the BCC $13B7 vol clamp;
;                            LDA #$0F at $13B5 always runs → VOL=$0F)
;        $15C1   → $DE     (FE → DE: turns INC $1783,X into DEC $1783,X,
;                            flipping skydive direction from up to down)
;
;   2. INSTRUMENT COPY: copies 120 bytes from $183B to $1799, placing
;      15 instrument records (8 bytes each) at $1799-$1810.
;      Instrument record layout (matches the Hubbard '85 family):
;        +0 pw_lo  +1 pw_hi  +2 ctrl  +3 AD  +4 SR
;        +5 vib_depth  +6 pwm_speed  +7 fx_flags
;
;      Then JMP $12EB → JMP $1812 → STA #$40 to $1782 → RTS.
;      $1782 = $40 sets the "first-frame" flag (bit 6) so play's BIT
;      $1782 test takes the lazy-init path on the first call.
;
; play ($0A1B) is also a one-byte trampoline JMP $12FD.
;
;   At $12FD every frame:
;     1. INC $1788 (global frame counter).
;     2. BIT $1782:
;          bit 7 set → song-ended; BMI takes the silence path at $1323
;          bit 6 set → first-frame; falls through to the zero-state setup
;          both clear → normal; BVC takes the per-voice loop entry $133D
;     3. First-frame setup zeros $1788, zeroes per-voice state
;        ($1758,X / $175B,X / $175E,X / $1767,X for X=2..0), clears
;        $1782, then falls through to $133D.
;
; PER-VOICE LOOP ($133D..$160E):
;   X = 2 (V3) decrementing to 0 (V1). For each voice:
;     - DEC $177F (tick divider). When negative, reload from $1780
;       (the binary holds $1780 = $00, so the divider hits zero every
;       frame and the gate below always passes — there is NO 1-frame
;       defer like Action Biker's).
;     - LDA $1754,X → STA $1757 → TAY: voice's SID-register offset
;       (0/7/14), used as Y for STA $D400,Y / $D401,Y / etc.
;     - CMP $177F vs $1780: note-load gate. With $1780=$00 always passes.
;     - Load orderlist pointer (lo from $0A1E,X, hi from $0A21,X) into
;       ZP $FB/$FC.
;     - DEC $175E,X (v_dur). If positive: sustain at $1456. If hit -1:
;       load next note at $1371.
;
; NOTE-LOAD PATH ($1371..$1453):
;   - LDY $1758,X (v_olpos); LDA ($FB),Y: orderlist[v_olpos].
;   - $FF sentinel → restart orderlist (zero v_dur, v_olpos, v_patpos
;     and retry). No song-end via orderlist — orderlists just loop.
;   - Else TAY (pattern index); pattern_lo[Y] from $0A24, pattern_hi[Y]
;     from $0A50 → ZP $FD/$FE.
;   - LDY $175B,X (v_patpos). Pattern byte at ($FD),Y is flags+dur:
;       bit 7 = "new-instrument byte follows"
;       bit 6 = "tie" (BVS → skip note load, just keep gate state)
;       bit 5 = "no_release"
;       bits 0-4 = duration in ticks
;     Stored raw at v_flags,X ($1761) and temp $176E (for BIT test).
;   - Master volume: A = patched-base ($FF after init) - $175A, clamped
;     ≤ $0F → STA $D418. After init's NOP-patch the clamp BCC is
;     dead, so LDA #$0F always wins (volume is fixed at $0F).
;   - BIT $176E: V set (tie) → DEC $176D so gate-mask = $FE (gate bit
;     ANDs out on the ctrl write). Else: INC v_patpos. If bit 7 set,
;     consume next byte as 5-bit inst index → v_inst,X = $176A,X.
;   - Pitch byte → v_pitch,X = $1767,X. ASL → TAY = byte offset into
;     freq table at $1694 (96 semitones × 2 bytes).
;   - Drum-priority gate ($178B): if bit 7 set (drum active), skip the
;     freq write entirely (drum owns this voice's freq this frame).
;     Else write $D400/$D401,Y and stash freq_hi at v_fhi,X = $1783,X
;     (used by skydive).
;   - Write inst record to SID: ctrl AND gate-mask → $D404,Y; pw_lo/hi
;     → $D402/$D403,Y; AD/SR → $D405/$D406,Y. Save raw ctrl at
;     v_ctrl,X = $1764,X (used by sustain HR).
;   - INC v_patpos. If next byte is $FF: zero v_patpos, INC v_olpos
;     (end-of-pattern).
;   - JMP $15FB (effects loop tail / next voice).
;
; SUSTAIN PATH ($1456):
;   If drum-active bit 7 of $178B is clear, just JMP $15FB. Else: if
;   no_release (bit 5 of v_flags,X) or v_dur > 0, fall through to
;   effects. Else (v_dur == 0 AND release-enabled): kill gate (v_ctrl
;   AND $FE → $D404,Y), AD=0, SR=0 (HARD RESTART pre-zero so the
;   next note's gate-on retriggers cleanly).
;
; EFFECTS PATH ($147D..$15FA):
;   v_inst × 8 → Y (offset into inst record). Reads from the runtime
;   inst table at $1799:
;     +5 vib_depth ($179E,Y)  +6 pwm_speed ($179F,Y)  +7 fx_flags ($17A0,Y)
;
;   VIBRATO: A = $1788 & $07, fold to triangle (4..7 → 7^A); use as
;     count for a repeated portamento step (LDA $1696,Y - LDA $1694,Y
;     gives delta to the NEXT semitone). Result → STA $D400/$D401,Y.
;   PWM: per-instrument pwm_speed nibble drives ± of pw_hi. Direction
;     toggles when pw_hi nibble hits $08 (down→up) or $0E (up→down) —
;     Hubbard's HARDCODED PW bounds (see memory reference_hubbard_pwm_bounds).
;   SKYDIVE: fx_flags bit 0 = falling tone (DEC $1783,X then write
;     freq_hi); bit 1 = rising tone (INC, or DEC after init's $15C1
;     patch); bit 2 = arpeggio (freq from table, indexed by
;     $1767+($1788&1)*$18 i.e., add a 24-semitone shift every other
;     frame).
;
; DRUM CHANNEL ($1611..$1691):
;   Runs once per frame after the 3-voice loop. $178A bit 6 set → enter
;   drum logic at $1621. $178C is the step counter; $178E the end-step;
;   when they match, silence V1+V2 ctrl and set $178A = $FF (deactivate).
;   Inside the step: $1793 holds the drum's current command byte —
;   BIT $1793 splits N (= write V1 freq), V (= write V2 freq). $1790
;   gates ctrl-toggle for V1/V2 (XOR with $01 alternates gate). The
;   drum hijacks V1 and V2 freq/ctrl when active by setting $178B = $FF.
;
; VARIABLE MAP ($1754-$1793)
; --------------------------
;   $1754-$1756  sid_base[3]      ; 0, 7, 14 (V1/V2/V3 register offsets)
;   $1757        sid_base_Y       ; current voice's offset (TAY temp)
;   $1758-$175A  v_olpos[3]       ; orderlist position per voice
;   $175B-$175D  v_patpos[3]      ; byte offset into current pattern
;   $175E-$1760  v_dur[3]         ; note duration countdown
;   $1761-$1763  v_flags[3]       ; raw pattern byte (flags+dur)
;   $1764-$1766  v_ctrl[3]        ; saved inst.ctrl (sustain HR)
;   $1767-$1769  v_pitch[3]       ; semitone index
;   $176A-$176C  v_inst[3]        ; 5-bit instrument index
;   $176D        gate_mask        ; $FF normal; $FE for tie notes
;   $176E        flags_tmp        ; v_flags copy for BIT testing
;   $176F        freq_lo_tmp      ; temp during freq write
;   $1770        x_save           ; X saved across inst*8 multiply
;   $1771        ctrl_tmp         ; inst.ctrl en route to v_ctrl
;   $1772        porta_shift_cnt  ; vibrato depth-shift loop counter
;   $1773        pwm_param        ; inst.pwm_speed (nibble + dir)
;   $1774-$1775  porta_delta_lo/hi
;   $1776-$1777  porta_freq_lo/hi ; running freq after vibrato slide
;   $1778        vib_tri          ; triangle-folded ($1788 & 7)
;   $1779-$177B  v_pwm_cnt[3]     ; PWM decrement counter per voice
;   $177C-$177E  v_pwm_dir[3]     ; PWM direction sign
;   $177F        tick_div         ; per-frame tick divider
;   $1780        tick_reload      ; $00 in binary → note-load every frame
;   $1781        inst_off_y       ; v_inst*8 save for drum re-entry
;   $1782        song_state       ; bit 7 = end-of-song, bit 6 = first-frame
;   $1783-$1785  v_fhi[3]         ; saved freq_hi for skydive slide
;   $1786        fx_flags         ; inst.fx_flags (bits 0/1/2 = effect)
;   $1787        pwm_acc          ; PWM running hi-nibble accumulator
;   $1788        frame_ctr        ; global frame counter (LFO source)
;   $1789        drum_trig        ; drum trigger byte
;   $178A        drum_state       ; bit 6 = drum-runs-this-frame
;   $178B        drum_active      ; bit 7 = drum owns voice freq
;   $178C        drum_step        ; drum sequence counter
;   $178D        drum_pitch       ; drum pitch low-nibble (from $1793)
;   $178E        drum_endstep     ; drum sequence final step
;   $178F        drum_v2_offs     ; V2 detune offset for drum
;   $1790        drum_ctrl_flags  ; bit 7 = toggle V1, bit 6 = toggle V2
;   $1791        v1_ctrl_drum     ; V1 ctrl XOR-toggle target
;   $1792        v2_ctrl_drum     ; V2 ctrl XOR-toggle target
;   $1793        drum_cmd         ; drum-step pitch+flags byte
;
; FREQ TABLE: $1694, 192 bytes (96 semitones × 2 bytes lo/hi). Confirmed
;   by dump: $1694..$1695 = $16,$01 = $0116, $1696..$1697 = $0127, etc.
;   Pitch index runs 0..95 directly (ASL → byte stride).
;
; ORDERLIST/PATTERN LAYOUT (inside the "data gap" $0A1E..$12EA):
;   $0A1E..$0A20  orderlist_lo[V1, V2, V3] = $7C, $A3, $22
;   $0A21..$0A23  orderlist_hi[V1, V2, V3] = $0A, $0A, $0B
;   $0A24..$0A4F  pattern_lo[44]
;   $0A50..$0A7B  pattern_hi[44]
;   $0A7C..$0AA2  V1 orderlist (39 bytes, ends $FF)
;   $0AA3..$0B21  V2 orderlist (127 bytes)
;   $0B22..$0B95  V3 orderlist (116 bytes)
;   $0B96..       Pattern data (44 patterns, variable length)
;
; ============================================================================

; ======= init: =======
; Trampoline. Real work is at $18B3. A holds subtune (only subtune 0 here).
init:
    $0A18: 4C B3 18   JMP $18b3        ; → L_18B3
; ======= play: =======
; Trampoline. Real work is at $12FD.
play:
    $0A1B: 4C FD 12   JMP $12fd        ; → L_12FD
; ----- data gap $0A1E-$12EA (2253 bytes) -----
;
; This "gap" is NOT empty: it holds the orderlist/pattern tables that the
; play loop reads via the self-modified $1359/$135E/$138C/$1391 sites.
;   $0A1E..$0A23 orderlist pointers (lo[3], hi[3])
;   $0A24..$0A4F pattern_lo[44]
;   $0A50..$0A7B pattern_hi[44]
;   $0A7C..      V1/V2/V3 orderlists + 44 patterns of music data
;

; Trampoline tail of init. $18F4 ends with JMP $12EB so the init's last act
; is to JMP $1812 → STA #$40, $1782 (set first-frame flag) → RTS.
L_12EB:
    $12EB: 4C 12 18   JMP $1812        ; → L_1812
; ----- data gap $12EE-$12FC (15 bytes) -----

; ======= play body =======
; Every frame: bump frame counter, then dispatch on song_state ($1782).
L_12FD:
    $12FD: EE 88 17   INC $1788        ; frame_ctr++
    $1300: 2C 82 17   BIT $1782        ; N = bit 7 (end-of-song),
                                       ; V = bit 6 (first-frame)
    $1303: 30 1E      BMI $1323        ; → L_1323    ; end-of-song: silence path
    $1305: 50 36      BVC $133d        ; → L_133D    ; normal frame
    ; First-frame setup (V=1, N=0). Init set $1782 = $40 so this fires
    ; exactly once. Zero frame counter, zero per-voice state arrays
    ; (v_olpos/v_patpos/v_dur/v_pitch for X=2..0), clear $1782, then
    ; fall through to the per-voice loop.
    $1307: A9 00      LDA #$00
    $1309: 8D 88 17   STA $1788        ; frame_ctr = 0
    $130C: A2 02      LDX #$02         ; loop X = 2 (V3) → 0 (V1)
L_130E:
    $130E: 9D 58 17   STA $1758,x      ; v_olpos[X]  = 0
    $1311: 9D 5B 17   STA $175b,x      ; v_patpos[X] = 0
    $1314: 9D 5E 17   STA $175e,x      ; v_dur[X]    = 0
    $1317: 9D 67 17   STA $1767,x      ; v_pitch[X]  = 0
    $131A: CA         DEX
    $131B: 10 F1      BPL $130e        ; → L_130E
    $131D: 8D 82 17   STA $1782        ; song_state = 0 (clear first-frame flag)
    $1320: 4C 3D 13   JMP $133d        ; → L_133D    ; into per-voice loop
; End-of-song path (entered when $1782 bit 7 = 1). On the first end-of-song
; frame (V still set) silence all SID voices once and rewrite $1782 = $80
; (clears V); on subsequent end frames V=0 so BVC skips straight to drum.
L_1323:
    $1323: 50 15      BVC $133a        ; → L_133A    ; V=0: drum only
    $1325: A9 00      LDA #$00         ; V=1: first end frame — silence
    $1327: 8D 04 D4   STA $d404      ;V1_CTRL
    $132A: 8D 0B D4   STA $d40b      ;V2_CTRL
    $132D: 8D 12 D4   STA $d412      ;V3_CTRL
    $1330: A9 0F      LDA #$0f
    $1332: 8D 18 D4   STA $d418      ;VOL          ; full volume
    $1335: A9 80      LDA #$80
    $1337: 8D 82 17   STA $1782        ; song_state = $80 (N=1, V=0)
L_133A:
    $133A: 4C 11 16   JMP $1611        ; → L_1611    ; into drum/effects only
; ======= Per-voice loop entry =======
; X = 2 (start with V3) decrement to 0 (V1).
L_133D:
    $133D: A2 02      LDX #$02         ; voice index V3..V1
    ; Tick divider. $1780 in the binary is $00 so every frame this wraps
    ; $00 → $FF → reload $00. Net effect: divider is always $00, so the
    ; CMP at $1354 always passes (note-load runs every frame).
    $133F: CE 7F 17   DEC $177f        ; tick_div--
    $1342: 10 06      BPL $134a        ; → L_134A
    $1344: AD 80 17   LDA $1780        ; reload from tick_reload ($00)
    $1347: 8D 7F 17   STA $177f
L_134A:
    ; Look up SID voice base offset (0/7/14) into $1757 (also TAY).
    $134A: BD 54 17   LDA $1754,x      ; sid_base[X]
    $134D: 8D 57 17   STA $1757
    $1350: A8         TAY              ; Y = SID base for this voice
    ; Note-load gate. With $1780 always $00, this is a no-op gate.
    $1351: AD 7F 17   LDA $177f
    $1354: CD 80 17   CMP $1780
    $1357: D0 15      BNE $136e        ; → L_136E    ; skip note-load (effects only)
    ; Load orderlist pointer for this voice. These operands look like
    ; $1795/$1796 in the static binary but init has patched them to
    ; $0A1E (lo) and $0A21 (hi). $1795-$1798 in the binary are all $00.
    $1359: BD 95 17   LDA $1795,x      ; <-- PATCHED to LDA $0A1E,X (orderlist_lo[X])
    $135C: 85 FB      STA $fb          ; ZP ptr lo
    $135E: BD 96 17   LDA $1796,x      ; <-- PATCHED to LDA $0A21,X (orderlist_hi[X])
    $1361: 85 FC      STA $fc          ; ZP ptr hi → ($FB) = voice orderlist
    ; Tick the duration counter. Expires → load next note.
    $1363: DE 5E 17   DEC $175e,x      ; v_dur[X]--
    $1366: 30 09      BMI $1371        ; → L_1371    ; expired: load next note
    $1368: 4C 56 14   JMP $1456        ; → L_1456    ; sustain current note
; ----- data gap $136B-$136D (3 bytes) -----

L_136E:
    $136E: 4C 7D 14   JMP $147d        ; → L_147D
L_1371:
    $1371: BC 58 17   LDY $1758,x   
    $1374: B1 FB      LDA ($fb),y   
    $1376: C9 FF      CMP #$ff      
    $1378: D0 11      BNE $138b        ; → L_138B
    $137A: A9 00      LDA #$00      
    $137C: 9D 5E 17   STA $175e,x   
    $137F: 9D 58 17   STA $1758,x   
    $1382: 9D 5B 17   STA $175b,x   
    $1385: 4C 71 13   JMP $1371        ; → L_1371
; ----- data gap $1388-$138A (3 bytes) -----

; Normal pattern lookup. A holds the pattern index from the orderlist.
; The $1797/$1798 operands look stale in the binary; init patched them
; to $0A24 (pattern_lo[44]) and $0A50 (pattern_hi[44]).
L_138B:
    $138B: A8         TAY              ; Y = pattern index
    $138C: B9 97 17   LDA $1797,y      ; <-- PATCHED to LDA $0A24,Y (pattern_lo)
    $138F: 85 FD      STA $fd
    $1391: B9 98 17   LDA $1798,y      ; <-- PATCHED to LDA $0A50,Y (pattern_hi)
    $1394: 85 FE      STA $fe          ; ZP ptr = pattern start
    $1396: BC 5B 17   LDY $175b,x   
    $1399: A9 FF      LDA #$ff      
    $139B: 8D 6D 17   STA $176d     
    $139E: B1 FD      LDA ($fd),y   
    $13A0: 9D 61 17   STA $1761,x   
    $13A3: 8D 6E 17   STA $176e     
    $13A6: 29 1F      AND #$1f      
    $13A8: 9D 5E 17   STA $175e,x   
    $13AB: A9 47      LDA #$47      
    $13AD: 38         SEC           
    $13AE: ED 5A 17   SBC $175a     
    $13B1: C9 0F      CMP #$0f      
    $13B3: 90 02      BCC $13b7        ; → L_13B7
    $13B5: A9 0F      LDA #$0f      
L_13B7:
    $13B7: 8D 18 D4   STA $d418      ;VOL
    $13BA: 2C 6E 17   BIT $176e     
    $13BD: 70 3B      BVS $13fa        ; → L_13FA
    $13BF: FE 5B 17   INC $175b,x   
    $13C2: AD 6E 17   LDA $176e     
    $13C5: 10 0B      BPL $13d2        ; → L_13D2
    $13C7: C8         INY           
    $13C8: B1 FD      LDA ($fd),y   
    $13CA: 29 1F      AND #$1f      
    $13CC: 9D 6A 17   STA $176a,x   
    $13CF: FE 5B 17   INC $175b,x   
L_13D2:
    $13D2: C8         INY           
    $13D3: B1 FD      LDA ($fd),y   
    $13D5: 9D 67 17   STA $1767,x   
    $13D8: 0A         ASL a         
    $13D9: A8         TAY           
    $13DA: AD 8B 17   LDA $178b     
    $13DD: 10 1E      BPL $13fd        ; → L_13FD
    $13DF: B9 94 16   LDA $1694,y   
    $13E2: 8D 6F 17   STA $176f     
    $13E5: B9 95 16   LDA $1695,y   
    $13E8: AC 57 17   LDY $1757     
    $13EB: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $13EE: 9D 83 17   STA $1783,x   
    $13F1: AD 6F 17   LDA $176f     
    $13F4: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $13F7: 4C FD 13   JMP $13fd        ; → L_13FD
L_13FA:
    $13FA: CE 6D 17   DEC $176d     
L_13FD:
    $13FD: AC 57 17   LDY $1757     
    $1400: BD 6A 17   LDA $176a,x   
    $1403: 8E 70 17   STX $1770     
    $1406: 0A         ASL a         
    $1407: 0A         ASL a         
    $1408: 0A         ASL a         
    $1409: AA         TAX           
    $140A: BD 9B 17   LDA $179b,x   
    $140D: 8D 71 17   STA $1771     
    $1410: AD 8B 17   LDA $178b     
    $1413: 10 21      BPL $1436        ; → L_1436
    $1415: BD 9B 17   LDA $179b,x   
    $1418: 2D 6D 17   AND $176d     
    $141B: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $141E: BD 99 17   LDA $1799,x   
    $1421: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $1424: BD 9A 17   LDA $179a,x   
    $1427: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $142A: BD 9C 17   LDA $179c,x   
    $142D: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $1430: BD 9D 17   LDA $179d,x   
    $1433: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_1436:
    $1436: AE 70 17   LDX $1770     
    $1439: AD 71 17   LDA $1771     
    $143C: 9D 64 17   STA $1764,x   
    $143F: FE 5B 17   INC $175b,x   
    $1442: BC 5B 17   LDY $175b,x   
    $1445: B1 FD      LDA ($fd),y   
    $1447: C9 FF      CMP #$ff      
    $1449: D0 08      BNE $1453        ; → L_1453
    $144B: A9 00      LDA #$00      
    $144D: 9D 5B 17   STA $175b,x   
    $1450: FE 58 17   INC $1758,x   
L_1453:
    $1453: 4C FB 15   JMP $15fb        ; → L_15FB
L_1456:
    $1456: AD 8B 17   LDA $178b     
    $1459: 30 03      BMI $145e        ; → L_145E
    $145B: 4C FB 15   JMP $15fb        ; → L_15FB
L_145E:
    $145E: AC 57 17   LDY $1757     
    $1461: BD 61 17   LDA $1761,x   
    $1464: 29 20      AND #$20      
    $1466: D0 15      BNE $147d        ; → L_147D
    $1468: BD 5E 17   LDA $175e,x   
    $146B: D0 10      BNE $147d        ; → L_147D
    $146D: BD 64 17   LDA $1764,x   
    $1470: 29 FE      AND #$fe      
    $1472: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $1475: A9 00      LDA #$00      
    $1477: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $147A: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_147D:
    $147D: AD 8B 17   LDA $178b     
    $1480: 30 03      BMI $1485        ; → L_1485
    $1482: 4C FB 15   JMP $15fb        ; → L_15FB
L_1485:
    $1485: BD 6A 17   LDA $176a,x   
    $1488: 0A         ASL a         
    $1489: 0A         ASL a         
    $148A: 0A         ASL a         
    $148B: A8         TAY           
    $148C: 8C 81 17   STY $1781     
    $148F: B9 A0 17   LDA $17a0,y   
    $1492: 8D 86 17   STA $1786     
    $1495: B9 9F 17   LDA $179f,y   
    $1498: 8D 73 17   STA $1773     
    $149B: B9 9E 17   LDA $179e,y   
    $149E: 8D 72 17   STA $1772     
    $14A1: F0 6F      BEQ $1512        ; → L_1512
    $14A3: AD 88 17   LDA $1788     
    $14A6: 29 07      AND #$07      
    $14A8: C9 04      CMP #$04      
    $14AA: 90 02      BCC $14ae        ; → L_14AE
    $14AC: 49 07      EOR #$07      
L_14AE:
    $14AE: 8D 78 17   STA $1778     
    $14B1: BD 67 17   LDA $1767,x   
    $14B4: 0A         ASL a         
    $14B5: A8         TAY           
    $14B6: 38         SEC           
    $14B7: B9 96 16   LDA $1696,y   
    $14BA: F9 94 16   SBC $1694,y   
    $14BD: 8D 74 17   STA $1774     
    $14C0: B9 97 16   LDA $1697,y   
    $14C3: F9 95 16   SBC $1695,y   
L_14C6:
    $14C6: 4A         LSR a         
    $14C7: 6E 74 17   ROR $1774     
    $14CA: CE 72 17   DEC $1772     
    $14CD: 10 F7      BPL $14c6        ; → L_14C6
    $14CF: 8D 75 17   STA $1775     
    $14D2: B9 94 16   LDA $1694,y   
    $14D5: 8D 76 17   STA $1776     
    $14D8: B9 95 16   LDA $1695,y   
    $14DB: 8D 77 17   STA $1777     
    $14DE: BD 61 17   LDA $1761,x   
    $14E1: 29 1F      AND #$1f      
    $14E3: C9 08      CMP #$08      
    $14E5: 90 1C      BCC $1503        ; → L_1503
    $14E7: AC 78 17   LDY $1778     
L_14EA:
    $14EA: 88         DEY           
    $14EB: 30 16      BMI $1503        ; → L_1503
    $14ED: 18         CLC           
    $14EE: AD 76 17   LDA $1776     
    $14F1: 6D 74 17   ADC $1774     
    $14F4: 8D 76 17   STA $1776     
    $14F7: AD 77 17   LDA $1777     
    $14FA: 6D 75 17   ADC $1775     
    $14FD: 8D 77 17   STA $1777     
    $1500: 4C EA 14   JMP $14ea        ; → L_14EA
L_1503:
    $1503: AC 57 17   LDY $1757     
    $1506: AD 76 17   LDA $1776     
    $1509: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $150C: AD 77 17   LDA $1777     
    $150F: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_1512:
    $1512: AD 73 17   LDA $1773     
    $1515: F0 62      BEQ $1579        ; → L_1579
    $1517: AC 81 17   LDY $1781     
    $151A: 29 1F      AND #$1f      
    $151C: DE 79 17   DEC $1779,x   
    $151F: 10 58      BPL $1579        ; → L_1579
    $1521: 9D 79 17   STA $1779,x   
    $1524: AD 73 17   LDA $1773     
    $1527: 29 E0      AND #$e0      
    $1529: 8D 87 17   STA $1787     
    $152C: BD 7C 17   LDA $177c,x   
    $152F: D0 1A      BNE $154b        ; → L_154B
    $1531: AD 87 17   LDA $1787     
    $1534: 18         CLC           
    $1535: 79 99 17   ADC $1799,y   
    $1538: 48         PHA           
    $1539: B9 9A 17   LDA $179a,y   
    $153C: 69 00      ADC #$00      
    $153E: 29 0F      AND #$0f      
    $1540: 48         PHA           
    $1541: C9 0E      CMP #$0e      
    $1543: D0 1D      BNE $1562        ; → L_1562
    $1545: FE 7C 17   INC $177c,x   
    $1548: 4C 62 15   JMP $1562        ; → L_1562
L_154B:
    $154B: 38         SEC           
    $154C: B9 99 17   LDA $1799,y   
    $154F: ED 87 17   SBC $1787     
    $1552: 48         PHA           
    $1553: B9 9A 17   LDA $179a,y   
    $1556: E9 00      SBC #$00      
    $1558: 29 0F      AND #$0f      
    $155A: 48         PHA           
    $155B: C9 08      CMP #$08      
    $155D: D0 03      BNE $1562        ; → L_1562
    $155F: DE 7C 17   DEC $177c,x   
L_1562:
    $1562: 8E 70 17   STX $1770     
    $1565: AE 57 17   LDX $1757     
    $1568: 68         PLA           
    $1569: 99 9A 17   STA $179a,y   
    $156C: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $156F: 68         PLA           
    $1570: 99 99 17   STA $1799,y   
    $1573: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $1576: AE 70 17   LDX $1770     
L_1579:
    $1579: AD 86 17   LDA $1786     
    $157C: 29 01      AND #$01      
    $157E: F0 35      BEQ $15b5        ; → L_15B5
    $1580: BD 83 17   LDA $1783,x   
    $1583: F0 30      BEQ $15b5        ; → L_15B5
    $1585: BD 5E 17   LDA $175e,x   
    $1588: F0 2B      BEQ $15b5        ; → L_15B5
    $158A: BD 61 17   LDA $1761,x   
    $158D: 29 1F      AND #$1f      
    $158F: 38         SEC           
    $1590: E9 01      SBC #$01      
    $1592: DD 5E 17   CMP $175e,x   
    $1595: AC 57 17   LDY $1757     
    $1598: 90 10      BCC $15aa        ; → L_15AA
    $159A: BD 83 17   LDA $1783,x   
    $159D: DE 83 17   DEC $1783,x   
    $15A0: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $15A3: BD 64 17   LDA $1764,x   
    $15A6: 29 FE      AND #$fe      
    $15A8: D0 08      BNE $15b2        ; → L_15B2
L_15AA:
    $15AA: BD 83 17   LDA $1783,x   
    $15AD: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $15B0: A9 80      LDA #$80      
L_15B2:
    $15B2: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_15B5:
    $15B5: AD 86 17   LDA $1786     
    $15B8: 29 02      AND #$02      
    $15BA: F0 0E      BEQ $15ca        ; → L_15CA
    $15BC: BD 83 17   LDA $1783,x   
    $15BF: F0 09      BEQ $15ca        ; → L_15CA
    $15C1: FE 83 17   INC $1783,x   
    $15C4: AC 57 17   LDY $1757     
    $15C7: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_15CA:
    $15CA: AD 86 17   LDA $1786     
    $15CD: 29 04      AND #$04      
    $15CF: F0 2A      BEQ $15fb        ; → L_15FB
    $15D1: AD 88 17   LDA $1788     
    $15D4: 29 01      AND #$01      
    $15D6: F0 09      BEQ $15e1        ; → L_15E1
    $15D8: BD 67 17   LDA $1767,x   
    $15DB: 18         CLC           
    $15DC: 69 18      ADC #$18      
    $15DE: 4C E4 15   JMP $15e4        ; → L_15E4
L_15E1:
    $15E1: BD 67 17   LDA $1767,x   
L_15E4:
    $15E4: 0A         ASL a         
    $15E5: A8         TAY           
    $15E6: B9 94 16   LDA $1694,y   
    $15E9: 8D 6F 17   STA $176f     
    $15EC: B9 95 16   LDA $1695,y   
    $15EF: AC 57 17   LDY $1757     
    $15F2: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $15F5: AD 6F 17   LDA $176f     
    $15F8: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_15FB:
    $15FB: A0 FF      LDY #$ff      
    $15FD: AD 89 17   LDA $1789     
    $1600: D0 06      BNE $1608        ; → L_1608
    $1602: AD 8A 17   LDA $178a     
    $1605: 30 01      BMI $1608        ; → L_1608
    $1607: C8         INY           
L_1608:
    $1608: 8C 8B 17   STY $178b     
    $160B: CA         DEX           
    $160C: 30 03      BMI $1611        ; → L_1611
    $160E: 4C 4A 13   JMP $134a        ; → L_134A
L_1611:
    $1611: A9 FF      LDA #$ff      
    $1613: 8D 8B 17   STA $178b     
    $1616: AD 89 17   LDA $1789     
    $1619: D0 05      BNE $1620        ; → L_1620
    $161B: 2C 8A 17   BIT $178a     
    $161E: 10 01      BPL $1621        ; → L_1621
L_1620:
    $1620: 60         RTS           
L_1621:
    $1621: 50 03      BVC $1626        ; → L_1626
    $1623: 20 94 17   JSR $1794        ; → sub_1794
L_1626:
    $1626: CE 8D 17   DEC $178d     
    $1629: 10 F5      BPL $1620        ; → L_1620
    $162B: AD 93 17   LDA $1793     
    $162E: 29 0F      AND #$0f      
    $1630: 8D 8D 17   STA $178d     
    $1633: AD 8C 17   LDA $178c     
    $1636: CD 8E 17   CMP $178e     
    $1639: D0 0F      BNE $164a        ; → L_164A
    $163B: A2 00      LDX #$00      
    $163D: 8E 04 D4   STX $d404      ;V1_CTRL
    $1640: 8E 0B D4   STX $d40b      ;V2_CTRL
    $1643: CA         DEX           
    $1644: 8E 8A 17   STX $178a     
    $1647: 4C 20 16   JMP $1620        ; → L_1620
L_164A:
    $164A: CE 8C 17   DEC $178c     
    $164D: 0A         ASL a         
    $164E: A8         TAY           
    $164F: 2C 93 17   BIT $1793     
    $1652: 30 20      BMI $1674        ; → L_1674
    $1654: 70 0C      BVS $1662        ; → L_1662
    $1656: B9 94 16   LDA $1694,y   
    $1659: 8D 00 D4   STA $d400      ;V1_FREQ_LO
    $165C: B9 95 16   LDA $1695,y   
    $165F: 8D 01 D4   STA $d401      ;V1_FREQ_HI
L_1662:
    $1662: 98         TYA           
    $1663: 38         SEC           
    $1664: ED 8F 17   SBC $178f     
    $1667: A8         TAY           
    $1668: B9 94 16   LDA $1694,y   
    $166B: 8D 07 D4   STA $d407      ;V2_FREQ_LO
    $166E: B9 95 16   LDA $1695,y   
    $1671: 8D 08 D4   STA $d408      ;V2_FREQ_HI
L_1674:
    $1674: 2C 90 17   BIT $1790     
    $1677: 10 0B      BPL $1684        ; → L_1684
    $1679: AD 91 17   LDA $1791     
    $167C: 49 01      EOR #$01      
    $167E: 8D 04 D4   STA $d404      ;V1_CTRL
    $1681: 8D 91 17   STA $1791     
L_1684:
    $1684: 50 0B      BVC $1691        ; → L_1691
    $1686: AD 92 17   LDA $1792     
    $1689: 49 01      EOR #$01      
    $168B: 8D 0B D4   STA $d40b      ;V2_CTRL
    $168E: 8D 92 17   STA $1792     
L_1691:
    $1691: 4C 20 16   JMP $1620        ; → L_1620
; ----- data gap $1694-$1793 (256 bytes) -----

; NOTE: "sub_1794" here is a disassembly artifact. The conditional
; JSR $1794 at $1623 dereferences $1794 as a vector, but in normal play
; the JSR is gated off (V flag from BIT $178A is clear when $178A is
; $00..$3F or $80..$BF). The $00 BRK shown below is just data.
sub_1794:
    $1794: 00         BRK              ; data, not code
; ----- data gap $1795-$1811 (125 bytes) -----
;
; This region is mostly runtime variables ($1795-$17F8 — instrument
; copy destination + per-voice state). Initial bytes:
;   $1795-$1798 all $00 (pre-init operand placeholders, see header)
;   $1799-$1810 will be overwritten by init's $183B copy (15 inst recs)
;

; Final init trampoline: set the first-frame flag and return.
L_1812:
    $1812: A9 40      LDA #$40         ; first-frame flag (bit 6)
    $1814: 8D 82 17   STA $1782        ; song_state = $40
    $1817: 60         RTS              ; back to caller of init
; ----- data gap $1818-$18B2 (155 bytes) -----
;
; This region is the instrument-source data block ($183B-$18B2, 120 bytes,
; 15 records × 8 bytes). Init copies it to $1799 on entry.
;

; ======= Real init body =======
; Pure self-modifying-code init. Patches operand bytes inside the play
; loop, then copies instrument records into runtime RAM. Subtune (A on
; entry) is ignored — only one subtune exists.
L_18B3:
    ; Operand-low byte $1E goes into LDA $1795,X at $135A so that
    ; instruction becomes LDA $0A1E,X (orderlist_lo[3 voices]).
    $18B3: A9 1E      LDA #$1e
    $18B5: 8D 5A 13   STA $135a
    ; Operand-high byte $0A goes into 4 sites:
    ;   $135B → orderlist_lo hi   $1360 → orderlist_hi hi
    ;   $138E → pattern_lo hi     $1393 → pattern_hi hi
    ; (all four lookups live on page $0A)
    $18B8: A9 0A      LDA #$0a
    $18BA: 8D 5B 13   STA $135b        ; LDA $1795,X → LDA $0A1E,X (hi part)
    $18BD: 8D 60 13   STA $1360        ; LDA $1796,X → LDA $0A21,X (hi part)
    $18C0: 8D 8E 13   STA $138e        ; LDA $1797,Y → LDA $0A24,Y (hi part)
    $18C3: 8D 93 13   STA $1393        ; LDA $1798,Y → LDA $0A50,Y (hi part)
    ; Operand-low $21 → LDA $0A21,X (orderlist_hi[3 voices])
    $18C6: A9 21      LDA #$21
    $18C8: 8D 5F 13   STA $135f
    ; Operand-low $24 → LDA $0A24,Y (pattern_lo[44])
    $18CB: A9 24      LDA #$24
    $18CD: 8D 8D 13   STA $138d
    ; Operand-low $50 → LDA $0A50,Y (pattern_hi[44])
    $18D0: A9 50      LDA #$50
    $18D2: 8D 92 13   STA $1392
    ; Opcode patch: at $15C1 the binary has $FE (INC abs,X for INC $1783,X
    ; = skydive UP). Overwrite with $DE (DEC abs,X) — skydive now goes
    ; DOWN. Effect is per-song polarity flip.
    $18D5: A9 DE      LDA #$de
    $18D7: 8D C1 15   STA $15c1
    ; Patch BCC $13B7 (2 bytes "90 02") to NOP NOP. The instruction that
    ; followed (LDA #$0F at $13B5) now always executes — volume is
    ; effectively pinned at $0F regardless of the fade computation.
    $18DA: A9 EA      LDA #$ea
    $18DC: 8D B3 13   STA $13b3
    $18DF: 8D B4 13   STA $13b4
    ; Patch the LDA immediate at $13AB-$13AC from #$47 to #$FF (fade base).
    $18E2: A9 FF      LDA #$ff
    $18E4: 8D AC 13   STA $13ac
    ; Copy 120 bytes from $183B..$18B2 to $1799..$1810. Lays out 15
    ; instrument records (8 bytes each) at the runtime address the
    ; effects/note-load path expects.
    $18E7: A2 00      LDX #$00
L_18E9:
    $18E9: BD 3B 18   LDA $183b,x
    $18EC: 9D 99 17   STA $1799,x
    $18EF: E8         INX
    $18F0: E0 78      CPX #$78         ; 120 bytes
    $18F2: D0 F5      BNE $18e9        ; → L_18E9
    ; Trampoline to $1812 which sets song_state ($1782) = $40 → first-frame
    ; flag is on for the very first play call.
    $18F4: 4C EB 12   JMP $12eb        ; → L_12EB
