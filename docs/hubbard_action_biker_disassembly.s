; ============================================================================
; Rob Hubbard - Action Biker (1985 Mastertronic)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: data/C64Music/MUSICIANS/H/Hubbard_Rob/Action_Biker.sid
; Load:   $C000   Init: $CBBB   Play: $C00D
; PSID:   19 subtunes, default subtune 2 (1-indexed; A=1 passed to init)
; Binary: $C000-$CBC1 (3010 bytes)
;
; Auto-traced 302 reachable code bytes from init+play. Layout commentary
; below was hand-derived by combining static analysis with py65
; single-step simulation logging SID writes (see /tmp/sim_actionbiker_f0.py).
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($CBBB): minimal 7 bytes. A holds subtune (0-indexed). Writes
; (A + $40) to $C3EA and returns. ALL setup is deferred to play's
; first-frame path.
;
; play ($C00D): every frame.
;   1. DEC $C3F1; if NOT negative, JMP $C28D (which is just RTS — early-out
;      counter, mostly always negative because $C3F1 is reset to $C000=$00
;      every frame, so DEC immediately gives $FF and BMI is taken).
;   2. INC $C3F0 (global frame counter).
;   3. BIT $C3EA: tests if bits 7 and 6 are set.
;      - bit 7 set → end-of-song; JMP $C28D (RTS)
;      - bit 6 set → FIRST FRAME; JSR $C28E (one-time setup)
;      - both clear → normal play
;   4. Fall through to per-voice processing at $C02B.
;
; $C28E (one-time setup): masks $C3EA to (subtune & $03), then:
;   - Copies 6 bytes of orderlist pointers from $C3F9+subtune*6 to $C3F3.
;   - Sets $C3F2 = 1 if subtune == 0, else 2 (loop start voice index).
;   - Clears V1/V2/V3 ctrl ($D404/$D40B/$D412), sets vol $0F.
;   - Zeros voice state arrays $C3C0,X $C3C3,X $C3C6,X $C3CF,X for X=2..0.
;   - Returns. The byte at $C3EA now has bit 6 clear, so subsequent
;     frames skip $C28E.
;
; PER-VOICE PROCESSING ($C02B..$C28A):
;   - X = $C3F2 (start with V3 for subtune>0, or V2 for subtune 0).
;   - DEC $C3E7 (per-frame counter, reload from $C3E8 when negative).
;   - **Note-load is gated by ($C3E7 == $C3E8)** at $C040-$C046.
;   - On FIRST FRAME: $C3E7 went from $01 → $00, then was reloaded to
;     $C3E8 = $02. So $C3E7 = $00 != $C3E8 = $02 → branch to $C05D →
;     JMP $C157 (effects loop, NO note load).
;   - Effects loop ($C157+) reads per-voice instrument state, writes
;     vibrato/freq-slide computed freqs. For V1+V2 this produces a freq
;     write of $0116 = freq_table[0]. For V3 the state is different and
;     produces no SID writes.
;   - On SECOND FRAME ($C3E7 cycles to == $C3E8): note-load DOES run for
;     all voices, all 3 voices fire their first notes.
;
; CONSEQUENCE FOR OUR CODEGEN:
;   This is the source of the 1-frame timing offset between our rebuild
;   (Grade D 61%) and the original. Our codegen's init zeros voice state
;   and fires the first note on play frame 0. The original engine
;   defers note firing until frame 1 via this $C3E7/$C3E8 gating.
;
;   To match: codegen would need to mirror the $C3E7-style counter
;   that delays the first note load by 1 frame.
;
; FREQ TABLE: $C2FC, 96 semitone entries packed as (lo[i], hi[i]) 2-byte
; little-endian stride. discover.py undercounts ("36 records × 4 bytes")
; because it groups bytes into 4-byte records, but the actual data is
; sequential 2-byte semitones over 192 bytes.
;
; INSTRUMENT TABLE: $CB5B, 8-byte records × 9 instruments.
;   offset 0: pulse_lo  1: pulse_hi  2: ctrl  3: AD  4: SR  5: ?  6: ?  7: fx_flags
;
; ============================================================================

; song_end_trampoline: orderlist hit an $FE marker; restart by
; silencing everything (JMP $C2DC, which writes $80 to $D400-$D417).
sub_C001:
    $C001: 4C DC C2    JMP $c2dc      ; → L_C2DC
; ----- data gap $C004-$C00C (9 bytes) -----


; ======= play: =======
; Called every frame by sidplayfp.
play:
    ; Sub-frame divider. $C3F1 starts at $00 (binary initializer); the
    ; reload-immediate at $C018 below also feeds it $00 (since $C000
    ; itself is $00). So DEC nearly always flips $00→$FF (negative) and
    ; BMI is taken. The non-BMI path is for cases where outside code
    ; (not seen statically) primes $C3F1 to a positive value to defer
    ; this frame's work.
    $C00D: CE F1 C3    DEC $c3f1
    $C010: 30 03       BMI $c015      ; → L_C015   ; usual path: do work
    $C012: 4C 8D C2    JMP $c28d      ; → L_C28D   ; skipped frame: RTS
L_C015:
    ; Frame counter +1 and reload sub-frame divider.
    $C015: EE F0 C3    INC $c3f0      ; $C3F0 = global frame counter
    $C018: AD 00 C0    LDA $c000      ; ($C000 = $00 in the binary)
    $C01B: 8D F1 C3    STA $c3f1      ; $C3F1 = $00 (reload sub-frame)
    ; $C3EA holds song state: bit 7 = end-of-song, bit 6 = first-frame
    ; (set by init). BIT moves bit 7 to N flag, bit 6 to V flag.
    $C01E: 2C EA C3    BIT $c3ea
    $C021: 10 03       BPL $c026      ; → L_C026   ; not end-of-song
    $C023: 4C 8D C2    JMP $c28d      ; → L_C28D   ; end-of-song: RTS
L_C026:
    $C026: 50 03       BVC $c02b      ; → L_C02B   ; normal frame
    $C028: 20 8E C2    JSR $c28e      ; → sub_C28E ; first-frame setup
L_C02B:
    ; Per-voice loop entry. X is the voice slot (2=V3, 1=V2, 0=V1).
    ; $C3F2 was set to 1 (for subtune 0) or 2 (others) by sub_C28E,
    ; controlling how many voices participate.
    $C02B: AE F2 C3    LDX $c3f2      ; X = starting voice index
    ; Tick divider: $C3E7 reloads from $C3E8 ($02) when it goes neg.
    ; On the FIRST play frame: $C3E7 = $01 (binary init) → DEC = $00,
    ; BPL taken (positive), $C3E7 stays $00. Subsequent comparison at
    ; $C040 will be $00 vs $02 → BNE → SKIP note-load (effects-only).
    ; On frame ~3 or so $C3E7 will wrap to match $C3E8 and note-load
    ; will start firing.
    $C02E: CE E7 C3    DEC $c3e7
    $C031: 10 06       BPL $c039      ; → L_C039   ; not yet wrapped
    $C033: AD E8 C3    LDA $c3e8      ; wrapped: reload
    $C036: 8D E7 C3    STA $c3e7      ; $C3E7 = $C3E8 ($02)
L_C039:
    ; Per-voice SID-base lookup. $C3BC,X holds the SID register offset
    ; for voice X (0/7/14 = V1/V2/V3 base relative to $D400). Stored at
    ; $C3BF as a Y-index used by later writes (STA $D400,Y etc.).
    $C039: BD BC C3    LDA $c3bc,X    ; SID voice offset (0,7,14)
    $C03C: 8D BF C3    STA $c3bf      ; remember as Y for SID writes
    $C03F: A8          TAY            ; Y = SID base offset
    ; **NOTE-LOAD GATE**: only run note-load when tick divider lands
    ; exactly on reload value. Skips note-load on frames where $C3E7
    ; hasn't ticked all the way around yet. THIS is what defers first
    ; note firing by one frame in the original — our codegen doesn't
    ; have an equivalent gate, hence the 1-frame offset.
    $C040: AD E7 C3    LDA $c3e7
    $C043: CD E8 C3    CMP $c3e8
    $C046: D0 15       BNE $c05d      ; → L_C05D   ; skip note-load
    ; Note-load path: $C3F3,X / $C3F6,X hold the per-voice orderlist
    ; pointer (lo/hi). Loaded into ZP $4B/$4C for indirect addressing.
    $C048: BD F3 C3    LDA $c3f3,X    ; orderlist ptr lo
    $C04B: 85 4B       STA $4b
    $C04D: BD F6 C3    LDA $c3f6,X    ; orderlist ptr hi
    $C050: 85 4C       STA $4c
    ; $C3C6,X = duration countdown for current note. DEC; if hit -1,
    ; load next note. Else fall through to sustain at $C138.
    $C052: DE C6 C3    DEC $c3c6,X    ; v_dur,X
    $C055: 30 09       BMI $c060      ; → L_C060   ; expired: load next
    $C057: 4C 38 C1    JMP $c138      ; → L_C138   ; sustain current
; ----- data gap $C05A-$C05C (3 bytes) -----

; Effects-only path: this frame's note-load is gated off (see $C046
; above). Just runs the per-voice effects (vibrato, freq-slide, PWM)
; without advancing pattern data. Frame 0 of every voice goes through
; here.
L_C05D:
    $C05D: 4C 57 C1    JMP $c157      ; → L_C157
; Note-load entry. ($4B):Y points at the orderlist; $C3C0,X = current
; orderlist position. Reads pattern index, handles $FF (end) and $FE
; (song-end) sentinels.
L_C060:
    $C060: BC C0 C3    LDY $c3c0,X    ; v_olpos,X
    $C063: B1 4B       LDA ($4b),Y    ; orderlist[v_olpos]
    $C065: C9 FF       CMP #$ff       ; loop-back sentinel
    $C067: F0 0A       BEQ $c073      ; → L_C073   ; restart orderlist
    $C069: C9 FE       CMP #$fe       ; song-end sentinel
    $C06B: D0 17       BNE $c084      ; → L_C084   ; normal: load patt
    $C06D: 20 01 C0    JSR $c001      ; → sub_C001 ; song-end: silence
    $C070: 4C 8D C2    JMP $c28d      ; → L_C28D
L_C073:
    ; Restart orderlist (loop): zero v_dur, v_olpos, v_pos and retry.
    $C073: A9 00       LDA #$00
    $C075: 9D C6 C3    STA $c3c6,X    ; v_dur,X = 0
    $C078: 9D C0 C3    STA $c3c0,X    ; v_olpos,X = 0
    $C07B: 9D C3 C3    STA $c3c3,X    ; v_patpos,X = 0
    $C07E: 4C 60 C0    JMP $c060      ; → L_C060   ; retry from start
; ----- data gap $C081-$C083 (3 bytes) -----

; Normal pattern load: A holds pattern index from orderlist. Look up
; pattern's start address via the (c40b, c436) lo/hi tables.
L_C084:
    $C084: A8          TAY            ; Y = pattern index
    $C085: B9 0B C4    LDA $c40b,Y    ; pat_lo[Y]
    $C088: 85 4D       STA $4d        ; ZP $4D = pat_lo
    $C08A: B9 36 C4    LDA $c436,Y    ; pat_hi[Y]
    $C08D: 85 4E       STA $4e        ; ZP $4E = pat_hi
    ; Y = byte offset within the pattern (advances per note loaded).
    $C08F: BC C3 C3    LDY $c3c3,X    ; v_patpos,X
    ; $C3D5 = "ctrl gate mask"; default $FF (gate bit passes). Cleared
    ; later for tie/legato notes via DEC at $C0E1.
    $C092: A9 FF       LDA #$ff
    $C094: 8D D5 C3    STA $c3d5      ; gate-mask = $FF
    ; First pattern byte = (flags<<5) | duration (low 5 bits).
    ;   bit 7 = "new instrument byte follows" (BPL test below)
    ;   bit 6 = "tie/legato" (BVS test → keep gate off)
    ;   bit 5 = "no_release" (preserved for sustain logic)
    ;   bits 0-4 = duration in ticks
    $C097: B1 4D       LDA ($4d),Y    ; A = pattern flags+dur byte
    $C099: 9D C9 C3    STA $c3c9,X    ; v_flags,X = raw byte
    $C09C: 8D D6 C3    STA $c3d6      ; save for BIT test below
    $C09F: 29 1F       AND #$1f       ; duration only
    $C0A1: 9D C6 C3    STA $c3c6,X    ; v_dur,X = duration
    ; BIT $C3D6: N = bit 7 (new inst), V = bit 6 (tie). If tie set,
    ; skip the note-byte fetch and instrument update (it's a continuation
    ; of the previous note: just update duration).
    $C0A4: 2C D6 C3    BIT $c3d6
    $C0A7: 70 38       BVS $c0e1      ; → L_C0E1   ; tie: clear gate mask
    $C0A9: FE C3 C3    INC $c3c3,X    ; advance v_patpos past flag byte
    $C0AC: AD D6 C3    LDA $c3d6
    $C0AF: 10 0B       BPL $c0bc      ; → L_C0BC   ; same inst: skip
    ; New-instrument byte present (bit 7 was set): consume it.
    $C0B1: C8          INY
    $C0B2: B1 4D       LDA ($4d),Y    ; instrument byte
    $C0B4: 29 1F       AND #$1f       ; mask to 5-bit inst index
    $C0B6: 9D D2 C3    STA $c3d2,X    ; v_inst,X = inst index
    $C0B9: FE C3 C3    INC $c3c3,X    ; advance past inst byte
L_C0BC:
    ; Pitch byte. Doubled (ASL) because freq table at $C2FC is 2-byte
    ; entries (lo, hi) per semitone → byte stride 2. ALL 96 semitones
    ; reachable; pitch is a direct semitone index.
    $C0BC: C8          INY
    $C0BD: B1 4D       LDA ($4d),Y    ; pitch byte (0-95)
    $C0BF: 9D CF C3    STA $c3cf,X    ; v_pitch,X
    $C0C2: 0A          ASL A          ; *2 for table stride
    $C0C3: A8          TAY            ; Y = byte offset into freq table
    $C0C4: B9 FC C2    LDA $c2fc,Y    ; freq_lo[pitch]
    $C0C7: 8D D7 C3    STA $c3d7      ; temp save
    $C0CA: A9 0F       LDA #$0f       ; (dead store: overwritten next)
    $C0CC: B9 FD C2    LDA $c2fd,Y    ; freq_hi[pitch]
    $C0CF: AC BF C3    LDY $c3bf      ; Y = SID voice offset
    $C0D2: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y   ; write SID freq_hi
    $C0D5: 9D EB C3    STA $c3eb,X    ; v_fhi,X = freq_hi (for slide)
    $C0D8: AD D7 C3    LDA $c3d7
    $C0DB: 99 00 D4    STA $D400 ;V1_FREQ_LO,Y   ; write SID freq_lo
    $C0DE: 4C E4 C0    JMP $c0e4      ; → L_C0E4
L_C0E1:
    ; Tie/legato note: clear gate-mask bit 0 so the ctrl write below
    ; AND-s away the gate bit (gate stays in whatever state the
    ; previous note left it — typically on, for legato).
    $C0E1: CE D5 C3    DEC $c3d5      ; $C3D5 $FF → $FE (clears bit 0)
L_C0E4:
    ; Write instrument table fields to the SID for this voice.
    ; Instrument table at $CB5B; each record is 8 bytes:
    ;   +0 pw_lo  +1 pw_hi  +2 ctrl  +3 AD  +4 SR  +5/+6 ?  +7 fx_flags
    ; X is shifted up by 3 (×8) so it becomes the byte offset to the
    ; instrument record's start +2 (so $CB5D,X = ctrl, etc.).
    $C0E4: AC BF C3    LDY $c3bf      ; Y = SID voice offset (0/7/14)
    $C0E7: BD D2 C3    LDA $c3d2,X    ; v_inst,X (5-bit inst index)
    $C0EA: 8E D8 C3    STX $c3d8      ; save X (voice index)
    $C0ED: 0A          ASL A          ; inst * 2
    $C0EE: 0A          ASL A          ; inst * 4
    $C0EF: 0A          ASL A          ; inst * 8
    $C0F0: AA          TAX            ; X = byte offset into inst table
    $C0F1: BD 5D CB    LDA $cb5d,X    ; inst.ctrl
    $C0F4: 8D D9 C3    STA $c3d9      ; stash raw ctrl
    $C0F7: BD 5D CB    LDA $cb5d,X    ; ctrl again
    $C0FA: 2D D5 C3    AND $c3d5      ; AND gate-mask (tie clears bit 0)
    $C0FD: 99 04 D4    STA $D404 ;V1_CTRL,Y   ; write SID ctrl (gate)
    $C100: BD 5B CB    LDA $cb5b,X    ; inst.pw_lo
    $C103: 99 02 D4    STA $D402 ;V1_PW_LO,Y
    $C106: BD 5C CB    LDA $cb5c,X    ; inst.pw_hi
    $C109: 99 03 D4    STA $D403 ;V1_PW_HI,Y
    $C10C: BD 5E CB    LDA $cb5e,X    ; inst.AD
    $C10F: 99 05 D4    STA $D405 ;V1_AD,Y
    $C112: BD 5F CB    LDA $cb5f,X    ; inst.SR
    $C115: 99 06 D4    STA $D406 ;V1_SR,Y
    $C118: AE D8 C3    LDX $c3d8      ; restore X (voice)
    $C11B: AD D9 C3    LDA $c3d9
    $C11E: 9D CC C3    STA $c3cc,X    ; v_ctrl,X = raw inst.ctrl
    ; Advance v_patpos past the pitch byte. If the next byte is $FF,
    ; the pattern ended: zero v_patpos and bump v_olpos.
    $C121: FE C3 C3    INC $c3c3,X
    $C124: BC C3 C3    LDY $c3c3,X
    $C127: B1 4D       LDA ($4d),Y    ; peek next byte
    $C129: C9 FF       CMP #$ff
    $C12B: D0 08       BNE $c135      ; → L_C135   ; not end-of-pat
    $C12D: A9 00       LDA #$00
    $C12F: 9D C3 C3    STA $c3c3,X    ; v_patpos,X = 0
    $C132: FE C0 C3    INC $c3c0,X    ; v_olpos,X += 1
L_C135:
    $C135: 4C 87 C2    JMP $c287      ; → L_C287   ; next voice
; Sustain path (current note's v_dur hasn't expired yet). The HARD
; RESTART check: if v_dur == 0 AND no_release flag clear, write
; ctrl-without-gate + AD=0 + SR=0 (kills the envelope so the next
; note's gate-on retriggers cleanly). Otherwise fall through to
; effects only (L_C157).
L_C138:
    $C138: AC BF C3    LDY $c3bf
    $C13B: BD C9 C3    LDA $c3c9,X    ; v_flags,X (raw pattern byte)
    $C13E: 29 20       AND #$20       ; test bit 5 = no_release
    $C140: D0 15       BNE $c157      ; → L_C157   ; no_release: skip HR
    $C142: BD C6 C3    LDA $c3c6,X    ; v_dur,X
    $C145: D0 10       BNE $c157      ; → L_C157   ; still ticking: skip
    ; Hit HR threshold (v_dur == 0). Kill gate + envelope.
    $C147: BD CC C3    LDA $c3cc,X    ; v_ctrl,X (saved inst.ctrl)
    $C14A: 29 FE       AND #$fe       ; clear gate bit
    $C14C: 99 04 D4    STA $D404 ;V1_CTRL,Y   ; gate off
    $C14F: A9 00       LDA #$00
    $C151: 99 05 D4    STA $D405 ;V1_AD,Y     ; AD=0
    $C154: 99 06 D4    STA $D406 ;V1_SR,Y     ; SR=0
; Effects loop: vibrato / triangle-LFO frequency modulation.
; Entered when note-load is gated off (first frames) OR after a normal
; note load. Computes a per-frame freq offset based on the global
; frame counter $C3F0, the instrument's vib_depth/period, and the
; current pitch's freq-table entry. Writes the modulated freq back
; to SID freq_lo/hi for this voice.
L_C157:
    ; Index into instrument table: inst_idx * 8.
    $C157: BD D2 C3    LDA $c3d2,X    ; v_inst,X
    $C15A: 0A          ASL A
    $C15B: 0A          ASL A
    $C15C: 0A          ASL A
    $C15D: A8          TAY            ; Y = inst byte offset
    $C15E: 8C E9 C3    STY $c3e9      ; remember inst offset
    ; Read instrument's effect parameters from bytes 5,6,7 of record:
    ;   $CB60,Y = vibrato depth         → $C3DA
    ;   $CB61,Y = vibrato period (count) → $C3DB
    ;   $CB62,Y = fx_flags              → $C3EE
    $C161: B9 62 CB    LDA $cb62,Y    ; inst.fx_flags
    $C164: 8D EE C3    STA $c3ee
    $C167: B9 61 CB    LDA $cb61,Y    ; inst.vib_period
    $C16A: 8D DB C3    STA $c3db
    $C16D: B9 60 CB    LDA $cb60,Y    ; inst.vib_depth
    $C170: 8D DA C3    STA $c3da
    $C173: F0 6F       BEQ $c1e4      ; → L_C1E4   ; depth=0: no vibrato
    ; Triangle LFO from global frame counter $C3F0. AND $07 gives 0-7;
    ; if >=4 we EOR #$07 to fold back, producing a triangle 0-4-0-4-…
    $C175: AD F0 C3    LDA $c3f0
    $C178: 29 07       AND #$07
    $C17A: C9 04       CMP #$04
    $C17C: 90 02       BCC $c180      ; → L_C180
    $C17E: 49 07       EOR #$07       ; fold: 5→2, 6→1, 7→0
L_C180:
    $C180: 8D E0 C3    STA $c3e0      ; LFO triangle value
    ; Compute (freq[pitch+1] - freq[pitch]) >> N — the semitone delta,
    ; right-shifted by vib_depth bits. This is the per-LFO-step delta.
    $C183: BD CF C3    LDA $c3cf,X    ; v_pitch,X
    $C186: 0A          ASL A          ; *2 for table stride
    $C187: A8          TAY
    $C188: 38          SEC
    $C189: B9 FE C2    LDA $c2fe,Y    ; freq_lo[pitch+1]
    $C18C: F9 FC C2    SBC $c2fc,Y    ; minus freq_lo[pitch]
    $C18F: 8D DC C3    STA $c3dc      ; delta_lo
    $C192: B9 FF C2    LDA $c2ff,Y    ; freq_hi[pitch+1]
    $C195: F9 FD C2    SBC $c2fd,Y    ; minus freq_hi[pitch]
L_C198:
    ; Right-shift delta by vib_depth bits (smaller = wider vibrato).
    $C198: 4A          LSR A
    $C199: 6E DC C3    ROR $c3dc
    $C19C: CE DA C3    DEC $c3da
    $C19F: 10 F7       BPL $c198      ; → L_C198
    $C1A1: 8D DD C3    STA $c3dd      ; delta_hi (shifted)
    ; Load base freq for current pitch.
    $C1A4: B9 FC C2    LDA $c2fc,Y    ; freq_lo[pitch]
    $C1A7: 8D DE C3    STA $c3de
    $C1AA: B9 FD C2    LDA $c2fd,Y    ; freq_hi[pitch]
    $C1AD: 8D DF C3    STA $c3df
    ; If the original-pattern's dur (low 5 bits) was < 8, skip the
    ; vibrato sum (no time to vibrate on very short notes).
    $C1B0: BD C9 C3    LDA $c3c9,X    ; v_flags,X
    $C1B3: 29 1F       AND #$1f       ; duration
    $C1B5: C9 08       CMP #$08
    $C1B7: 90 1C       BCC $c1d5      ; → L_C1D5   ; short note: skip
    $C1B9: AC E0 C3    LDY $c3e0      ; LFO value (0-4)
L_C1BC:
    ; Accumulate delta LFO times into freq.
    $C1BC: 88          DEY
    $C1BD: 30 16       BMI $c1d5      ; → L_C1D5
    $C1BF: 18          CLC
    $C1C0: AD DE C3    LDA $c3de
    $C1C3: 6D DC C3    ADC $c3dc
    $C1C6: 8D DE C3    STA $c3de
    $C1C9: AD DF C3    LDA $c3df
    $C1CC: 6D DD C3    ADC $c3dd
    $C1CF: 8D DF C3    STA $c3df
    $C1D2: 4C BC C1    JMP $c1bc      ; → L_C1BC
L_C1D5:
    ; Write modulated freq to SID. NOTE: this is the path that
    ; produces the $0116 freq writes for V1+V2 on the very first
    ; frame, because at that point v_pitch,X is 0 (still the zeroed
    ; state from sub_C28E), so freq_table[0] = $0116 is what gets
    ; written. V3's path takes the BEQ at $C173 (vib_depth=0) → skip.
    $C1D5: AC BF C3    LDY $c3bf
    $C1D8: AD DE C3    LDA $c3de
    $C1DB: 99 00 D4    STA $D400 ;V1_FREQ_LO,Y
    $C1DE: AD DF C3    LDA $c3df
    $C1E1: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
; PWM modulation block. Per-voice oscillating pulse-width sweep with
; configurable speed (low 5 bits of $C3DB) and direction-flip thresholds
; at $08 (min) and $0E (max). Uses inst.pw_lo / inst.pw_hi at $CB5B,Y /
; $CB5C,Y as live state — Hubbard's PWM bounds ($08 and $0E) are
; HARDCODED in this routine, not per-instrument (see CLAUDE.md ref
; Hubbard PWM bounds).
L_C1E4:
    $C1E4: AD DB C3    LDA $c3db      ; vib_period byte (also pwm speed)
    $C1E7: F0 62       BEQ $c24b      ; → L_C24B   ; period=0: no PWM
    $C1E9: AC E9 C3    LDY $c3e9      ; Y = inst byte offset
    $C1EC: 29 1F       AND #$1f       ; low 5 bits = pwm step interval
    $C1EE: DE E1 C3    DEC $c3e1,X    ; voice's pwm step counter
    $C1F1: 10 58       BPL $c24b      ; → L_C24B   ; not yet time
    $C1F3: 9D E1 C3    STA $c3e1,X    ; reload step counter
    $C1F6: AD DB C3    LDA $c3db
    $C1F9: 29 E0       AND #$e0       ; high 3 bits = step size
    $C1FB: 8D EF C3    STA $c3ef
    $C1FE: BD E4 C3    LDA $c3e4,X    ; voice's pwm direction flag
    $C201: D0 1A       BNE $c21d      ; → L_C21D   ; nonzero = subtract
    ; Direction = ADD: pw += step.
    $C203: AD EF C3    LDA $c3ef
    $C206: 18          CLC
    $C207: 79 5B CB    ADC $cb5b,Y    ; pw_lo += step
    $C20A: 48          PHA
    $C20B: B9 5C CB    LDA $cb5c,Y
    $C20E: 69 00       ADC #$00       ; carry into pw_hi
    $C210: 29 0F       AND #$0f       ; pw_hi only uses 4 bits (12-bit PW)
    $C212: 48          PHA
    $C213: C9 0E       CMP #$0e       ; hit upper bound?
    $C215: D0 1D       BNE $c234      ; → L_C234   ; not yet, store back
    $C217: FE E4 C3    INC $c3e4,X    ; flip direction (now SUB)
    $C21A: 4C 34 C2    JMP $c234      ; → L_C234
L_C21D:
    ; Direction = SUB: pw -= step.
    $C21D: 38          SEC
    $C21E: B9 5B CB    LDA $cb5b,Y
    $C221: ED EF C3    SBC $c3ef      ; pw_lo -= step
    $C224: 48          PHA
    $C225: B9 5C CB    LDA $cb5c,Y
    $C228: E9 00       SBC #$00
    $C22A: 29 0F       AND #$0f
    $C22C: 48          PHA
    $C22D: C9 08       CMP #$08       ; hit lower bound?
    $C22F: D0 03       BNE $c234      ; → L_C234
    $C231: DE E4 C3    DEC $c3e4,X    ; flip direction (now ADD)
L_C234:
    ; Write updated pw back to instrument record AND to SID.
    $C234: 8E D8 C3    STX $c3d8      ; save voice X
    $C237: AE BF C3    LDX $c3bf      ; X = SID offset
    $C23A: 68          PLA
    $C23B: 99 5C CB    STA $cb5c,Y    ; inst.pw_hi updated
    $C23E: 9D 03 D4    STA $D403 ;V1_PW_HI,X
    $C241: 68          PLA
    $C242: 99 5B CB    STA $cb5b,Y    ; inst.pw_lo updated
    $C245: 9D 02 D4    STA $D402 ;V1_PW_LO,X
    $C248: AE D8 C3    LDX $c3d8      ; restore voice X
; Skydive / drum-engine block. Bit 0 of fx_flags = "drum_freq_slide".
; Decrements freq_hi by 1 each frame until v_dur runs out; that
; produces the falling tom/kick sweep. Also handles the gate-mask
; logic when the slide drops below the threshold.
L_C24B:
    $C24B: AD EE C3    LDA $c3ee      ; inst.fx_flags
    $C24E: 29 01       AND #$01       ; bit 0 = drum/skydive
    $C250: F0 35       BEQ $c287      ; → L_C287   ; flag clear: skip
    $C252: BD EB C3    LDA $c3eb,X    ; v_fhi,X (current freq_hi)
    $C255: F0 30       BEQ $c287      ; → L_C287   ; already 0: skip
    $C257: BD C6 C3    LDA $c3c6,X
    $C25A: F0 2B       BEQ $c287      ; → L_C287   ; v_dur=0: skip
    ; Compute how many frames into the note we are (orig_dur - 1 - v_dur).
    ; If we're past mid-note (BCC), use the slid freq directly. Else
    ; decrement v_fhi and write the OLD value.
    $C25C: BD C9 C3    LDA $c3c9,X
    $C25F: 29 1F       AND #$1f       ; orig duration
    $C261: 38          SEC
    $C262: E9 01       SBC #$01       ; dur - 1
    $C264: DD C6 C3    CMP $c3c6,X    ; compare to v_dur
    $C267: AC BF C3    LDY $c3bf
    $C26A: 90 10       BCC $c27c      ; → L_C27C
    $C26C: BD EB C3    LDA $c3eb,X    ; pre-DEC v_fhi
    $C26F: DE EB C3    DEC $c3eb,X    ; v_fhi -= 1
    $C272: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
    $C275: BD CC C3    LDA $c3cc,X    ; saved inst.ctrl
    $C278: 29 FE       AND #$fe       ; clear gate bit
    $C27A: D0 08       BNE $c284      ; → L_C284
L_C27C:
    $C27C: BD EB C3    LDA $c3eb,X
    $C27F: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
    $C282: A9 80       LDA #$80       ; test bit (silence) for skydive end
L_C284:
    $C284: 99 04 D4    STA $D404 ;V1_CTRL,Y
; Per-voice loop tail. DEC X; if negative we've done all voices, RTS.
; Else JMP back to per-voice top at $C039.
L_C287:
    $C287: CA          DEX
    $C288: 30 03       BMI $c28d      ; → L_C28D
    $C28A: 4C 39 C0    JMP $c039      ; → L_C039   ; next voice
L_C28D:
    $C28D: 60          RTS
; First-frame setup. Runs ONCE per song start (gated by bit 6 of $C3EA,
; cleared at $C293). Mirrors what a typical Hubbard player puts in init,
; but Action Biker defers it to play because init() runs before
; sidplayfp clears the rest of the SID register file.
sub_C28E:
    ; Mask subtune index to low 2 bits and clear "first-frame" sentinel.
    $C28E: AD EA C3    LDA $c3ea      ; subtune | $40
    $C291: 29 03       AND #$03       ; keep only low 2 bits
    $C293: 8D EA C3    STA $c3ea      ; bit 6 now clear → never re-enter
    ; A = subtune * 6  (each subtune has 6 bytes of orderlist ptrs).
    $C296: 0A          ASL A          ; *2
    $C297: 8D D7 C3    STA $c3d7
    $C29A: 0A          ASL A          ; *4
    $C29B: 18          CLC
    $C29C: 6D D7 C3    ADC $c3d7      ; *2 + *4 = *6
    ; Pick how many voices participate: 1 for subtune 0, 2 otherwise.
    ; Stored at $C3F2; per-voice loop uses this as starting X.
    $C29F: A0 01       LDY #$01       ; default Y=1
    $C2A1: AA          TAX            ; X = subtune * 6
    $C2A2: F0 02       BEQ $c2a6      ; → L_C2A6   ; subtune 0: keep Y=1
    $C2A4: A0 02       LDY #$02       ; otherwise Y=2
L_C2A6:
    $C2A6: 8C F2 C3    STY $c3f2      ; $C3F2 = starting voice index
    $C2A9: A0 00       LDY #$00
L_C2AB:
    ; Copy 6 bytes from $C3F9 + (subtune*6) to $C3F3..$C3F8 (the active
    ; per-voice orderlist pointers, lo and hi).
    $C2AB: BD F9 C3    LDA $c3f9,X
    $C2AE: 99 F3 C3    STA $c3f3,Y
    $C2B1: E8          INX
    $C2B2: C8          INY
    $C2B3: C0 06       CPY #$06
    $C2B5: D0 F4       BNE $c2ab      ; → L_C2AB
    ; Reset frame counter; silence all SID voices.
    $C2B7: A2 02       LDX #$02       ; loop X=2..0 (V3, V2, V1)
    $C2B9: A9 00       LDA #$00
    $C2BB: 8D F0 C3    STA $c3f0      ; $C3F0 = 0 (frame counter)
    $C2BE: 8D 04 D4    STA $D404 ;V1_CTRL
    $C2C1: 8D 0B D4    STA $D40B ;V2_CTRL
    $C2C4: 8D 12 D4    STA $D412 ;V3_CTRL
L_C2C7:
    ; Zero per-voice state for all 3 voices.
    $C2C7: 9D C0 C3    STA $c3c0,X    ; v_olpos,X = 0
    $C2CA: 9D C3 C3    STA $c3c3,X    ; v_patpos,X = 0
    $C2CD: 9D C6 C3    STA $c3c6,X    ; v_dur,X = 0
    $C2D0: 9D CF C3    STA $c3cf,X    ; v_pitch,X = 0
    $C2D3: CA          DEX
    $C2D4: 10 F1       BPL $c2c7      ; → L_C2C7
    $C2D6: A9 0F       LDA #$0f
    $C2D8: 8D 18 D4    STA $D418 ;VOL
    $C2DB: 60          RTS
; Song-end / panic-silence. Sets $C3EA bit 7 (= end sentinel that
; play's BIT check at $C021 will see), then writes $80 to ALL SID
; voice registers ($D400-$D417) — that's the test-bit on every voice
; which kills oscillator output cleanly.
L_C2DC:
    $C2DC: A9 80       LDA #$80
    $C2DE: 8D EA C3    STA $c3ea      ; mark song-ended (bit 7 set)
    $C2E1: A2 17       LDX #$17       ; loop $17..0 (24 SID registers)
L_C2E3:
    $C2E3: 9D 00 D4    STA $D400 ;V1_FREQ_LO,X
    $C2E6: CA          DEX
    $C2E7: 10 FA       BPL $c2e3      ; → L_C2E3
    $C2E9: 60          RTS
; ----- data gap $C2EA-$CBBA (2257 bytes) -----


; ======= init: =======
; Entry: A = subtune index (0-indexed). PSID startSong=2 → sidplayfp
; passes A=1 here. We just OR in $40 (the "first frame" sentinel — bit
; 6 of $C3EA) and stash. Everything else is done lazily on first play.
init:
    $CBBB: 18          CLC
    $CBBC: 69 40       ADC #$40         ; A = subtune | $40
    $CBBE: 8D EA C3    STA $c3ea        ; $C3EA = subtune | $40
    $CBC1: 60          RTS
