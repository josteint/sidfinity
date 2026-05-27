; ============================================================================
; Rob Hubbard - Thing on a Spring (1985 Gremlin Graphics)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/Hubbard_Rob/Thing_on_a_Spring.sid
; Load:   $C000   Init: $CECB   Play: $C012
; PSID:   17 subtunes, default subtune 1 (PSID passes 0-based: subtune 0 plays
;         the song; subtunes 1..16 are sound-effect overlays).
; Binary: $C000-$CEDA (3803 bytes)
;
; Auto-traced 1061 reachable code bytes from init+play. Layout below derived
; by combining static analysis of register fetches with the binary's initial
; data values (the player relies on baked-in voice state at $C46D..$C47F+
; before the first-frame zero-out runs).
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($CECB): A = subtune index (0..16). Two paths:
;   - A == 0  → JMP $C000 → JMP $CEA2: $C497 = $40    (first-frame, NORMAL)
;   - A >= 1  → A -= 1, JSR $C00F → JMP $CEBC: $C49F gets the SFX slot index
;               with bit 6 set (first-frame), THEN JMP $C003 → JMP $CEA8:
;               $C497 = $C0  (first-frame, SUB-ONLY: silences main song,
;               just plays the SFX overlay from $C326).
;
; play ($C012): every frame.
;   1. INC $C49D (global frame counter, also LFO source).
;   2. BIT $C497 — N = bit 7 (sub-only), V = bit 6 (first-frame).
;        $00 → normal play (BPL+BVC fall to $C052)
;        $40 → first-frame normal: clear orderpos/patpos/notelen/curnote for
;              all 3 voices, clear $C497, JMP $C052
;        $80 → sub-only steady state: JMP $C326 (subroutine player)
;        $C0 → first-frame sub-only: silence V1/V2/V3 ctrl, vol=$0F,
;              $C497 := $80, JMP $C326
;   3. Main per-voice loop ($C052..$C326): X = 2,1,0 (V3, V2, V1).
;        - $C494 is the global tempo divider; reloads from $C495 when it
;          wraps negative. Note-load is gated on ($C494 == $C495).
;        - Each voice indexes a SID base offset table at $C469: $00/$07/$0E.
;        - Orderlist ptr per voice from $C509,X (lo) / $C50C,X (hi).
;        - Pattern ptrs by orderlist byte: $C50F,Y (lo) / $C533,Y (hi).
;        - Pattern byte bits: bit 7 = "new instrument follows",
;                             bit 6 = "tie/no-new-note",
;                             bit 5 = "no_release" (hold past length),
;                             bits 0-4 = note length (1..31 frames).
;        - On a note-load: write D400/D401 (freq from $C3A9,Y), D402/D403
;          (PW from $CD2A/$CD2B), D404 (CTRL from $CD2C), D405/D406 (AD/SR
;          from $CD2D/$CD2E). VOL ($D418) is recomputed per note from
;          ($47 - $C46F) clamped to $0F.
;        - Effects loop ($C192..$C30D): vibrato (triangle LFO from $C49D
;          AND $07), portamento step (>> ($C487+1) for fine slide), pulse
;          width sweep ($C488 delta with $08/$0E direction-flip bounds —
;          standard Hubbard PWM — mutated IN-PLACE in the $CD2A/$CD2B
;          instrument bytes), and 3 fx flags ($C49B):
;            bit 0 → freq_hi down-sweep (drum) with test-bit gate retrigger
;            bit 1 → freq_hi up-sweep
;            bit 2 → +24-semitone arpeggio on odd $C49D frames
;        - After per-voice work: $C310 sets $C4A0 = $FF if no SFX active,
;          else $00. $C4A0 is read on subsequent voices via BMI/BPL: when
;          an SFX is active ($C4A0 == $00), the main player SKIPS its
;          freq/ctrl/PW SID writes so the SFX (which owns V1+V2) isn't
;          stomped. Voice state still advances.
;   4. After all voices: JMP $C326 (subroutine player, called every frame).
;
; sub_C326 (SFX overlay player): owns V1+V2 only.
;   - Idle gate: returns immediately unless ($C49E == 0 && $C49F bit 7 clear).
;     An active SFX slot has bit 7 clear in $C49F; an inactive slot has $FF.
;   - First-frame gate: $C49F bit 6 set → JSR $C4A9 (load SFX params).
;   - Per-frame: DEC $C4A2; on wrap, reload from $C4A8 & $0F.
;       Compare $C4A1 (current step) vs $C4A3 (end step). On end,
;       silence V1+V2 CTRL, $C49F := $FF (deactivate), RTS.
;       Else INC $C4A1 (or DEC — see self-modify note below). Y = step*2.
;       Bits 6,7 of $C4A8 gate V1/V2 freq writes:
;         bit 7 set → skip BOTH V1 and V2 freq writes (CTRL toggle only)
;         bit 6 set → skip V1 freq (play V2 only)
;         else     → write V1 freq from $C3A9,Y; write V2 freq from
;                    $C3A9,Y-$C4A4 (V2 sits $C4A4 semitones below V1).
;       $C4A5 bits 7,6 enable per-frame CTRL toggling (EOR #$01 into
;       $D404 / $D40B → flips bit 0 = gate, giving a buzz/arp ctrl effect).
;
; sub_C4A9 (SFX init from slot $C49F & $0F):
;   - Silence V1+V2 CTRL, clear $C4A2.
;   - Y = ($C49F & $0F) * 16; SFX records are 16 bytes at $CDA2,Y:
;       +0  → $C4A8 (flags: bits 4-5 path-select, 6-7 voice-skip, 0-3 div)
;       +1  → $C4A1 (start step) — also copied as D400 (V1 FREQ_LO)
;       +2..+13 → blitted to $D401..$D40C (the rest of V1+V2's regs)
;       +5  → also $C4A6 (V1 ctrl initial)
;       +8  → also $C4A5 (& $3F → $C4A4 V2 interval; & $C0 → ctrl-flip mask)
;       +12 → also $C4A7 (V2 ctrl initial)
;       +15 → $C4A3 (end step)
;   - **SELF-MODIFYING CODE**: $C505 writes $EE (INC opcode) or $CE (DEC
;     opcode) to $C35F based on $C4A8 bits 4-5. So the same code at $C35F
;     can advance the SFX step UP ($EE = INC $C4A1) or DOWN ($CE = DEC
;     $C4A1), flipping the SFX direction without a runtime branch.
;
; ============================================================================
;
; DATA LAYOUTS
; ------------
;
; Freq table: $C3A9, 96 semitones, 2-byte stride lo/hi (NTSC; first entry
;   $0116 ≈ A1 in standard tuning). Used both by the main player (for
;   pitched notes and vibrato delta) and the SFX overlay.
;
; Voice SID-offset table: $C469-$C46B = $00, $07, $0E (V1, V2, V3 byte
;   offsets from $D400). $C46C is the per-iter scratch copy used as Y for
;   "STA $D400,Y" etc.
;
; Per-voice state arrays (X-indexed, X = 0/1/2 for V1/V2/V3):
;   $C46D,X  v_olpos    orderlist position
;   $C470,X  v_patpos   pattern position
;   $C473,X  v_notelen  note-length countdown
;   $C476,X  v_notebyte saved raw pattern flags+len byte
;   $C479,X  v_ctrlsave saved instrument CTRL (for gate-off on release)
;   $C47C,X  v_pitch    current semitone (0..95)
;   $C47F,X  v_inst     current instrument (0..14, 5-bit field)
;   $C498,X  v_fhi_acc  freq_hi accumulator (for drum sweep / pitch-up)
;   $C48E,X  v_pwcnt    pulse-mod tick counter
;   $C491,X  v_pwdir    pulse-mod direction flag (0 = up, !=0 = down)
;
; Shared scratch / shared state:
;   $C46C    iter's SID base offset (snapshot of $C469,X for current voice)
;   $C482    portamento step counter
;   $C483    note-byte copy (BIT $C483 tests bits 6/7)
;   $C484-7  freq/inst/ctrl scratch
;   $C487    vibrato divider (LSR count for delta)
;   $C488    inst's pulse delta byte
;   $C489/A  portamento step (lo/hi, shifted right by $C487+1 bits)
;   $C48B/C  portamento base freq (lo/hi)
;   $C48D    vibrato LFO triangle 0..3..0 (from $C49D AND $07 EOR-fold)
;   $C494    tempo counter (DEC per frame, reload from $C495)
;   $C495    tempo reload value (1 = note-load every 2nd frame at 50Hz)
;   $C496    inst-base scratch (for the effects loop)
;   $C497    player state byte ($40/$80/$C0 flags — see play flow above)
;   $C49B    inst fx_flags ($CD31,Y copy)
;   $C49C    pulse delta amount (bits 5-7 of $C488)
;   $C49D    global frame counter (also LFO source)
;
; SFX overlay state:
;   $C49E    "force-slot" override (preserved across init calls if non-zero)
;   $C49F    SFX slot ($40+slot first-frame; $00..$0F active; $80+ inactive)
;   $C4A0    SFX-active flag ($00 = SFX has the floor, $FF = main free)
;   $C4A1    SFX current step
;   $C4A2    SFX frame counter (reloads from $C4A8 & $0F)
;   $C4A3    SFX end step
;   $C4A4    V2-below-V1 semitone interval
;   $C4A5    ctrl-flip enable (bits 6,7) + V2-interval source (bits 0-5)
;   $C4A6    V1 ctrl state (EOR #$01 each tick when flip enabled)
;   $C4A7    V2 ctrl state (same)
;   $C4A8    SFX flags: bits 6-7 voice-skip, bits 4-5 path-select (INC/DEC
;            self-modify on $C35F), bits 0-3 frame-divider
;
; Orderlist pointers (3 voices):
;   $C509,X (lo) / $C50C,X (hi):  V1 → $C557, V2 → $C59D, V3 → $C5FE
;
; Pattern pointer tables (36 patterns, indexed by orderlist byte):
;   $C50F+Y (lo) / $C533+Y (hi)
;
; Instrument table: $CD2A, 15 records × 8 bytes:
;   +0 PW_LO  +1 PW_HI  +2 CTRL  +3 AD  +4 SR
;   +5 vib_divider (LSR count for portamento step)
;   +6 pulse_delta (high 3 bits = amount, low 5 bits = pwcnt reload)
;   +7 fx_flags (bit 0 = drum sweep, bit 1 = pitch-up, bit 2 = +24 arp)
;
; SFX overlay table: $CDA2, 16 records × 16 bytes (see sub_C4A9 above).
;
; ============================================================================

; Subtune dispatch trampolines (kept at fixed addresses so init can
; reach them with cheap JMPs).
L_C000:
    ; "Default subtune" path: subtune 0 plays the actual song.
    $C000: 4C A2 CE   JMP $cea2        ; → L_CEA2  ; $C497 := $40
L_C003:
    ; "SFX subtune" tail: after JSR $C00F selects the SFX slot, drop us
    ; here so $C497 gets the sub-only flag set.
    $C003: 4C A8 CE   JMP $cea8        ; → L_CEA8  ; $C497 := $C0
; ----- data gap $C006-$C00E (9 bytes) -----

sub_C00F:
    ; init's call-through to the SFX slot picker (must be a JSR target
    ; so init can JSR then continue at $CED8 to JMP $C003 above).
    $C00F: 4C BC CE   JMP $cebc        ; → L_CEBC
; ======= play: =======
; Called every frame by sidplayfp.
play:
    ; Global frame counter (also feeds the vibrato LFO via $C49D AND $07).
    $C012: EE 9D C4   INC $c49d
    ; State dispatch: N = $C497 bit 7 (sub-only), V = bit 6 (first-frame).
    $C015: 2C 97 C4   BIT $c497
    $C018: 30 1E      BMI $c038        ; → L_C038  ; bit 7 set: SFX-only path
    $C01A: 50 36      BVC $c052        ; → L_C052  ; bit 6 clear: normal play
    ; First-frame normal: zero per-voice state for all 3 voices, then go
    ; play the first frame's voice loop.
    $C01C: A9 00      LDA #$00
    $C01E: 8D 9D C4   STA $c49d        ; restart frame counter
    $C021: A2 02      LDX #$02         ; X = 2,1,0 (V3,V2,V1)
L_C023:
    $C023: 9D 6D C4   STA $c46d,x      ; v_olpos := 0
    $C026: 9D 70 C4   STA $c470,x      ; v_patpos := 0
    $C029: 9D 73 C4   STA $c473,x      ; v_notelen := 0 (forces note-load)
    $C02C: 9D 7C C4   STA $c47c,x      ; v_pitch := 0
    $C02F: CA         DEX
    $C030: 10 F1      BPL $c023        ; → L_C023
    $C032: 8D 97 C4   STA $c497        ; clear first-frame flag
    $C035: 4C 52 C0   JMP $c052        ; → L_C052  ; fall into normal play
L_C038:
    ; SFX-only path (bit 7 of $C497 set). If bit 6 also set we're on the
    ; SFX's first frame: silence the song's 3 voices, set max vol, and
    ; clear bit 6 so subsequent frames just run the SFX.
    $C038: 50 15      BVC $c04f        ; → L_C04F  ; not first-frame: skip
    $C03A: A9 00      LDA #$00
    $C03C: 8D 04 D4   STA $d404        ;V1_CTRL  ; gate off, all voices
    $C03F: 8D 0B D4   STA $d40b        ;V2_CTRL
    $C042: 8D 12 D4   STA $d412        ;V3_CTRL
    $C045: A9 0F      LDA #$0f
    $C047: 8D 18 D4   STA $d418        ;VOL
    $C04A: A9 80      LDA #$80         ; keep bit 7, clear bit 6
    $C04C: 8D 97 C4   STA $c497
L_C04F:
    $C04F: 4C 26 C3   JMP $c326        ; → L_C326  ; SFX player owns V1+V2
L_C052:
    ; Main per-voice loop entry. X iterates 2→0 (V3 first, then V2, V1).
    $C052: A2 02      LDX #$02
    ; Tempo divider: DEC; on negative wrap, reload from $C495. The
    ; comparison "$C494 == $C495" at $C066 below gates note-load: only
    ; the frame right after a reload is a note-load frame.
    $C054: CE 94 C4   DEC $c494
    $C057: 10 06      BPL $c05f        ; → L_C05F  ; positive: no reload
    $C059: AD 95 C4   LDA $c495
    $C05C: 8D 94 C4   STA $c494        ; reload tempo counter
L_C05F:
    ; Snapshot this voice's SID base offset (0/7/$E) for the rest of
    ; the iteration. $C46C is read as the Y-index for "STA $D400,Y" etc.
    $C05F: BD 69 C4   LDA $c469,x
    $C062: 8D 6C C4   STA $c46c
    $C065: A8         TAY
    ; Note-load gate.
    $C066: AD 94 C4   LDA $c494
    $C069: CD 95 C4   CMP $c495
    $C06C: D0 15      BNE $c083        ; → L_C083  ; not a load frame: effects only
    ; Note-load path: pull this voice's orderlist ptr into ZP ($02/$03).
    $C06E: BD 09 C5   LDA $c509,x      ; orderlist_lo[X]
    $C071: 85 02      STA $02
    $C073: BD 0C C5   LDA $c50c,x      ; orderlist_hi[X]
    $C076: 85 03      STA $03
    ; Tick the note-length counter; if it goes negative, time for new note.
    $C078: DE 73 C4   DEC $c473,x
    $C07B: 30 09      BMI $c086        ; → L_C086  ; expired: load next note
    $C07D: 4C 6B C1   JMP $c16b        ; → L_C16B  ; sustain current note
; ----- data gap $C080-$C082 (3 bytes) -----

L_C083:
    ; Off-frame branch from the tempo gate at $C06C: skip note advancement,
    ; just run the effects pass.
    $C083: 4C 92 C1   JMP $c192        ; → L_C192
L_C086:
    ; Pull the next orderlist byte. $FF = end-of-orderlist sentinel:
    ; rewind to the start (v_olpos = 0, v_patpos = 0, v_notelen = 0) and
    ; retry. Patterns themselves are also $FF-terminated (see $C15E).
    $C086: BC 6D C4   LDY $c46d,x      ; v_olpos
    $C089: B1 02      LDA ($02),y      ; orderlist[v_olpos]
    $C08B: C9 FF      CMP #$ff
    $C08D: D0 11      BNE $c0a0        ; → L_C0A0  ; normal pattern index
    $C08F: A9 00      LDA #$00
    $C091: 9D 73 C4   STA $c473,x      ; v_notelen := 0
    $C094: 9D 6D C4   STA $c46d,x      ; v_olpos := 0 (restart)
    $C097: 9D 70 C4   STA $c470,x      ; v_patpos := 0
    $C09A: 4C 86 C0   JMP $c086        ; → L_C086  ; reread from start
; ----- data gap $C09D-$C09F (3 bytes) -----

L_C0A0:
    ; A = pattern index. Look up pattern start address via the parallel
    ; lo/hi tables, stash in ZP ($04/$05).
    $C0A0: A8         TAY              ; Y = pattern index
    $C0A1: B9 0F C5   LDA $c50f,y      ; pat_lo[Y]
    $C0A4: 85 04      STA $04
    $C0A6: B9 33 C5   LDA $c533,y      ; pat_hi[Y]
    $C0A9: 85 05      STA $05
    ; Read the pattern's flags+length byte. $C482 = $FF here serves as
    ; the portamento-step counter sentinel (decremented later if tie).
    $C0AB: BC 70 C4   LDY $c470,x      ; Y = v_patpos
    $C0AE: A9 FF      LDA #$ff
    $C0B0: 8D 82 C4   STA $c482
    $C0B3: B1 04      LDA ($04),y      ; pattern flags+len byte
    $C0B5: 9D 76 C4   STA $c476,x      ; v_notebyte := raw byte
    $C0B8: 8D 83 C4   STA $c483        ; copy for BIT test below
    $C0BB: 29 1F      AND #$1f         ; bits 0-4 = length
    $C0BD: 9D 73 C4   STA $c473,x      ; v_notelen := length
    ; Volume slide: $D418 = clip($47 - $C46F, 0, $0F). $C46F is an
    ; external slide variable (likely poked by game code or another
    ; routine) — runs every note-load, all voices share the same vol.
    $C0C0: A9 47      LDA #$47
    $C0C2: 38         SEC
    $C0C3: ED 6F C4   SBC $c46f
    $C0C6: C9 0F      CMP #$0f
    $C0C8: 90 02      BCC $c0cc        ; → L_C0CC
    $C0CA: A9 0F      LDA #$0f
L_C0CC:
    $C0CC: 8D 18 D4   STA $d418      ;VOL  ; clipped to 4-bit master vol
    ; BIT note byte: N = bit 7 (new instrument follows), V = bit 6 (tie).
    $C0CF: 2C 83 C4   BIT $c483
    $C0D2: 70 3B      BVS $c10f        ; → L_C10F  ; tie: no new note, just step ctr
    $C0D4: FE 70 C4   INC $c470,x      ; v_patpos++ (past flags byte)
    $C0D7: AD 83 C4   LDA $c483
    $C0DA: 10 0B      BPL $c0e7        ; → L_C0E7  ; bit 7 clear: keep same inst
    ; New instrument byte present.
    $C0DC: C8         INY
    $C0DD: B1 04      LDA ($04),y      ; instrument byte
    $C0DF: 29 1F      AND #$1f         ; 5-bit instrument index
    $C0E1: 9D 7F C4   STA $c47f,x      ; v_inst := A
    $C0E4: FE 70 C4   INC $c470,x      ; v_patpos++ (past inst byte)
L_C0E7:
    ; Read pitch byte (semitone 0..95).
    $C0E7: C8         INY
    $C0E8: B1 04      LDA ($04),y      ; pitch byte
    $C0EA: 9D 7C C4   STA $c47c,x      ; v_pitch := A
    $C0ED: 0A         ASL a            ; *2 for freq-table byte stride
    $C0EE: A8         TAY              ; Y = freq table byte offset
    ; If $C4A0 bit 7 clear (SFX active), skip the freq write — the SFX
    ; overlay owns V1+V2 freq registers right now. Voice state still
    ; advanced so the song stays in sync when the SFX ends.
    $C0EF: AD A0 C4   LDA $c4a0
    $C0F2: 10 1E      BPL $c112        ; → L_C112  ; SFX active: skip freq write
    $C0F4: B9 A9 C3   LDA $c3a9,y      ; freq_lo[pitch]
    $C0F7: 8D 84 C4   STA $c484        ; temp save (Y about to be clobbered)
    $C0FA: B9 AA C3   LDA $c3aa,y      ; freq_hi[pitch]
    $C0FD: AC 6C C4   LDY $c46c        ; Y = SID voice offset
    $C100: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y  ; write freq_hi
    $C103: 9D 98 C4   STA $c498,x      ; v_fhi_acc := freq_hi (for sweep fx)
    $C106: AD 84 C4   LDA $c484
    $C109: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y  ; write freq_lo
    $C10C: 4C 12 C1   JMP $c112        ; → L_C112
L_C10F:
    ; Tie path: just bump the portamento-step counter ($C482 $FF→$FE).
    $C10F: CE 82 C4   DEC $c482
L_C112:
    ; Instrument-parameter write. Y = SID voice offset. Compute byte
    ; offset into the instrument table ($CD2A,X = inst record start).
    $C112: AC 6C C4   LDY $c46c        ; Y = SID base
    $C115: BD 7F C4   LDA $c47f,x      ; v_inst
    $C118: 8E 85 C4   STX $c485        ; save voice index
    $C11B: 0A         ASL a            ; ×2
    $C11C: 0A         ASL a            ; ×4
    $C11D: 0A         ASL a            ; ×8 = byte offset in instr table
    $C11E: AA         TAX
    ; Stash inst.ctrl ($CD2C,X) for the v_ctrlsave write below — same
    ; value re-read once (vs. AND'd with $C482 tie-mask) for the SID
    ; write itself.
    $C11F: BD 2C CD   LDA $cd2c,x      ; inst.ctrl
    $C122: 8D 86 C4   STA $c486
    ; If SFX active, skip the SID writes (see $C0EF comment).
    $C125: AD A0 C4   LDA $c4a0
    $C128: 10 21      BPL $c14b        ; → L_C14B
    $C12A: BD 2C CD   LDA $cd2c,x      ; inst.ctrl (re-read)
    $C12D: 2D 82 C4   AND $c482        ; AND tie-mask ($FF normal, $FE on tie)
    $C130: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $C133: BD 2A CD   LDA $cd2a,x      ; inst.pw_lo
    $C136: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $C139: BD 2B CD   LDA $cd2b,x      ; inst.pw_hi
    $C13C: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $C13F: BD 2D CD   LDA $cd2d,x      ; inst.AD
    $C142: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $C145: BD 2E CD   LDA $cd2e,x      ; inst.SR
    $C148: 99 06 D4   STA $d406,y    ;V1_SR,Y
L_C14B:
    ; Save instrument's raw ctrl (without tie-mask) for the release path
    ; at $C182; restore X (voice index) clobbered by the ASL chain above.
    $C14B: AE 85 C4   LDX $c485        ; restore voice index
    $C14E: AD 86 C4   LDA $c486        ; raw inst.ctrl
    $C151: 9D 79 C4   STA $c479,x      ; v_ctrlsave
    ; v_patpos++ past the pitch byte; peek next byte for end-of-pattern.
    $C154: FE 70 C4   INC $c470,x
    $C157: BC 70 C4   LDY $c470,x
    $C15A: B1 04      LDA ($04),y      ; peek next pattern byte
    $C15C: C9 FF      CMP #$ff
    $C15E: D0 08      BNE $c168        ; → L_C168  ; not end-of-pattern
    $C160: A9 00      LDA #$00
    $C162: 9D 70 C4   STA $c470,x      ; v_patpos := 0 (next pattern)
    $C165: FE 6D C4   INC $c46d,x      ; v_olpos++ (advance orderlist)
L_C168:
    $C168: 4C 10 C3   JMP $c310        ; → L_C310  ; jump past effects, next voice
L_C16B:
    ; Sustain path (note-length hadn't expired). Only runs SID writes if
    ; main is active ($C4A0 = $FF / BMI), else just exits to next voice.
    $C16B: AD A0 C4   LDA $c4a0
    $C16E: 30 03      BMI $c173        ; → L_C173  ; main mode: do release-check
    $C170: 4C 10 C3   JMP $c310        ; → L_C310  ; SFX active: skip
L_C173:
    ; Hard-restart / release check: when note's countdown hits 0 AND the
    ; note isn't marked "no_release" (bit 5), kill gate + envelope so the
    ; next note retriggers cleanly. Symmetric to Action Biker's $C138 block.
    $C173: AC 6C C4   LDY $c46c        ; Y = SID base
    $C176: BD 76 C4   LDA $c476,x      ; v_notebyte
    $C179: 29 20      AND #$20         ; bit 5 = no_release?
    $C17B: D0 15      BNE $c192        ; → L_C192  ; held: skip release
    $C17D: BD 73 C4   LDA $c473,x
    $C180: D0 10      BNE $c192        ; → L_C192  ; still has length: skip
    $C182: BD 79 C4   LDA $c479,x      ; v_ctrlsave (raw inst.ctrl)
    $C185: 29 FE      AND #$fe         ; clear gate bit
    $C187: 99 04 D4   STA $d404,y    ;V1_CTRL,Y  ; gate off
    $C18A: A9 00      LDA #$00
    $C18C: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $C18F: 99 06 D4   STA $d406,y    ;V1_SR,Y    ; AD=SR=0 → silence
L_C192:
    ; Effects loop entry. Same SFX-active gate.
    $C192: AD A0 C4   LDA $c4a0
    $C195: 30 03      BMI $c19a        ; → L_C19A
    $C197: 4C 10 C3   JMP $c310        ; → L_C310
L_C19A:
    ; Read effect params for current voice's instrument. Y = inst*8 byte
    ; offset; $C496 saves it for the pulse-mod step at $C22C.
    $C19A: BD 7F C4   LDA $c47f,x      ; v_inst
    $C19D: 0A         ASL a
    $C19E: 0A         ASL a
    $C19F: 0A         ASL a            ; ×8
    $C1A0: A8         TAY
    $C1A1: 8C 96 C4   STY $c496        ; remember inst-base for later
    $C1A4: B9 31 CD   LDA $cd31,y      ; inst.fx_flags
    $C1A7: 8D 9B C4   STA $c49b
    $C1AA: B9 30 CD   LDA $cd30,y      ; inst.pulse_delta
    $C1AD: 8D 88 C4   STA $c488
    $C1B0: B9 2F CD   LDA $cd2f,y      ; inst.vib_divider
    $C1B3: 8D 87 C4   STA $c487
    $C1B6: F0 6F      BEQ $c227        ; → L_C227  ; divider=0: no vibrato
    ; Vibrato LFO from $C49D AND $07 with EOR-fold: triangle 0,1,2,3,3,2,1,0.
    $C1B8: AD 9D C4   LDA $c49d
    $C1BB: 29 07      AND #$07
    $C1BD: C9 04      CMP #$04
    $C1BF: 90 02      BCC $c1c3        ; → L_C1C3
    $C1C1: 49 07      EOR #$07         ; fold 4..7 → 3..0
L_C1C3:
    $C1C3: 8D 8D C4   STA $c48d        ; LFO triangle 0..3
    ; Compute (freq[pitch+1] - freq[pitch]) >> ($C487+1):
    ;   the per-LFO-step delta. Larger vib_divider → smaller step (subtler).
    $C1C6: BD 7C C4   LDA $c47c,x      ; v_pitch
    $C1C9: 0A         ASL a
    $C1CA: A8         TAY              ; Y = pitch*2
    $C1CB: 38         SEC
    $C1CC: B9 AB C3   LDA $c3ab,y      ; freq_lo[pitch+1]
    $C1CF: F9 A9 C3   SBC $c3a9,y      ;  -    freq_lo[pitch]
    $C1D2: 8D 89 C4   STA $c489        ; delta_lo
    $C1D5: B9 AC C3   LDA $c3ac,y      ; freq_hi[pitch+1]
    $C1D8: F9 AA C3   SBC $c3aa,y      ;  -    freq_hi[pitch]
L_C1DB:
    ; Right-shift delta by (vib_divider + 1) bits.
    $C1DB: 4A         LSR a
    $C1DC: 6E 89 C4   ROR $c489
    $C1DF: CE 87 C4   DEC $c487
    $C1E2: 10 F7      BPL $c1db        ; → L_C1DB
    $C1E4: 8D 8A C4   STA $c48a        ; delta_hi (shifted)
    ; Seed accumulator with base freq[pitch].
    $C1E7: B9 A9 C3   LDA $c3a9,y      ; freq_lo[pitch]
    $C1EA: 8D 8B C4   STA $c48b
    $C1ED: B9 AA C3   LDA $c3aa,y      ; freq_hi[pitch]
    $C1F0: 8D 8C C4   STA $c48c
    ; Vibrato only kicks in for notes of length >= 8 (very short notes
    ; would barely modulate anyway).
    $C1F3: BD 76 C4   LDA $c476,x      ; v_notebyte
    $C1F6: 29 1F      AND #$1f         ; bits 0-4 = note length
    $C1F8: C9 08      CMP #$08
    $C1FA: 90 1C      BCC $c218        ; → L_C218  ; short note: skip sum
    $C1FC: AC 8D C4   LDY $c48d        ; Y = LFO value (0..3)
L_C1FF:
    ; Accumulate delta into base freq, Y times (0..3 ADCs).
    $C1FF: 88         DEY
    $C200: 30 16      BMI $c218        ; → L_C218  ; done
    $C202: 18         CLC
    $C203: AD 8B C4   LDA $c48b
    $C206: 6D 89 C4   ADC $c489
    $C209: 8D 8B C4   STA $c48b
    $C20C: AD 8C C4   LDA $c48c
    $C20F: 6D 8A C4   ADC $c48a
    $C212: 8D 8C C4   STA $c48c
    $C215: 4C FF C1   JMP $c1ff        ; → L_C1FF  ; next LFO step
L_C218:
    ; Write the (possibly modulated) freq back to the SID.
    $C218: AC 6C C4   LDY $c46c        ; Y = SID base
    $C21B: AD 8B C4   LDA $c48b
    $C21E: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $C221: AD 8C C4   LDA $c48c
    $C224: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_C227:
    ; Pulse-width modulation. $C488 high 3 bits = delta amount; low 5 bits
    ; = pwcnt reload value. Per-voice counter $C48E,X gates frequency of
    ; mutation; direction flag $C491,X flips at PW_HI bounds $08 / $0E
    ; — the canonical "Hubbard PWM bounds" (memorialised in
    ; reference_hubbard_pwm_bounds.md).
    $C227: AD 88 C4   LDA $c488        ; inst.pulse_delta
    $C22A: F0 62      BEQ $c28e        ; → L_C28E  ; delta=0: no PWM
    $C22C: AC 96 C4   LDY $c496        ; Y = inst-base
    $C22F: 29 1F      AND #$1f         ; pwcnt reload value
    $C231: DE 8E C4   DEC $c48e,x      ; v_pwcnt--
    $C234: 10 58      BPL $c28e        ; → L_C28E  ; not time to step yet
    $C236: 9D 8E C4   STA $c48e,x      ; reload v_pwcnt
    $C239: AD 88 C4   LDA $c488
    $C23C: 29 E0      AND #$e0         ; delta amount (high 3 bits)
    $C23E: 8D 9C C4   STA $c49c
    $C241: BD 91 C4   LDA $c491,x      ; v_pwdir
    $C244: D0 1A      BNE $c260        ; → L_C260  ; dir != 0: subtract
    ; Direction "up": instrument's PW_LO/PW_HI += $C49C; on hitting
    ; PW_HI == $0E, flip direction (INC dir).
    $C246: AD 9C C4   LDA $c49c
    $C249: 18         CLC
    $C24A: 79 2A CD   ADC $cd2a,y      ; + inst.pw_lo
    $C24D: 48         PHA
    $C24E: B9 2B CD   LDA $cd2b,y      ; inst.pw_hi
    $C251: 69 00      ADC #$00
    $C253: 29 0F      AND #$0f         ; PW_HI is 4-bit
    $C255: 48         PHA
    $C256: C9 0E      CMP #$0e         ; upper bound
    $C258: D0 1D      BNE $c277        ; → L_C277
    $C25A: FE 91 C4   INC $c491,x      ; v_pwdir := 1 (turn around)
    $C25D: 4C 77 C2   JMP $c277        ; → L_C277
L_C260:
    ; Direction "down": subtract; at PW_HI == $08, DEC dir (back to up).
    $C260: 38         SEC
    $C261: B9 2A CD   LDA $cd2a,y      ; inst.pw_lo
    $C264: ED 9C C4   SBC $c49c
    $C267: 48         PHA
    $C268: B9 2B CD   LDA $cd2b,y
    $C26B: E9 00      SBC #$00
    $C26D: 29 0F      AND #$0f
    $C26F: 48         PHA
    $C270: C9 08      CMP #$08         ; lower bound
    $C272: D0 03      BNE $c277        ; → L_C277
    $C274: DE 91 C4   DEC $c491,x      ; v_pwdir := 0
L_C277:
    ; Pop new PW back into the inst record (MUTATES $CD2A/$CD2B in place)
    ; AND write to SID. Bank-swap X (voice index ↔ SID base) for the
    ; D40-indexed stores; restore after.
    $C277: 8E 85 C4   STX $c485        ; save voice index
    $C27A: AE 6C C4   LDX $c46c        ; X = SID base (use for stores)
    $C27D: 68         PLA              ; new PW_HI
    $C27E: 99 2B CD   STA $cd2b,y      ; inst.pw_hi (in-place mutation)
    $C281: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $C284: 68         PLA              ; new PW_LO
    $C285: 99 2A CD   STA $cd2a,y      ; inst.pw_lo (in-place)
    $C288: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
    $C28B: AE 85 C4   LDX $c485        ; restore voice index
L_C28E:
    ; fx flag bit 0 — DRUM/DOWN-SWEEP: while v_fhi_acc > 0, decrement it
    ; each frame and write to FREQ_HI; just before it hits the note's
    ; length threshold, re-strike with test-bit gate ($80) for a noise
    ; transient. Used for drum sounds.
    $C28E: AD 9B C4   LDA $c49b
    $C291: 29 01      AND #$01
    $C293: F0 35      BEQ $c2ca        ; → L_C2CA
    $C295: BD 98 C4   LDA $c498,x      ; v_fhi_acc
    $C298: F0 30      BEQ $c2ca        ; → L_C2CA
    $C29A: BD 73 C4   LDA $c473,x      ; v_notelen
    $C29D: F0 2B      BEQ $c2ca        ; → L_C2CA
    $C29F: BD 76 C4   LDA $c476,x      ; v_notebyte
    $C2A2: 29 1F      AND #$1f         ; length field
    $C2A4: 38         SEC
    $C2A5: E9 01      SBC #$01         ; length - 1
    $C2A7: DD 73 C4   CMP $c473,x      ; vs current v_notelen
    $C2AA: AC 6C C4   LDY $c46c
    $C2AD: 90 10      BCC $c2bf        ; → L_C2BF  ; (length-1) < remaining → past mid
    $C2AF: BD 98 C4   LDA $c498,x
    $C2B2: DE 98 C4   DEC $c498,x      ; v_fhi_acc--
    $C2B5: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $C2B8: BD 79 C4   LDA $c479,x      ; v_ctrlsave
    $C2BB: 29 FE      AND #$fe         ; gate off
    $C2BD: D0 08      BNE $c2c7        ; → L_C2C7  ; nonzero ctrl: just write
L_C2BF:
    ; Mid-note re-strike: write $80 to CTRL (test bit) to retrigger.
    $C2BF: BD 98 C4   LDA $c498,x
    $C2C2: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $C2C5: A9 80      LDA #$80         ; test bit
L_C2C7:
    $C2C7: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
L_C2CA:
    ; fx flag bit 1 — PITCH-UP SWEEP: opposite of bit 0; increments
    ; v_fhi_acc and writes FREQ_HI directly (no ctrl retrigger).
    $C2CA: AD 9B C4   LDA $c49b
    $C2CD: 29 02      AND #$02
    $C2CF: F0 0E      BEQ $c2df        ; → L_C2DF
    $C2D1: BD 98 C4   LDA $c498,x
    $C2D4: F0 09      BEQ $c2df        ; → L_C2DF
    $C2D6: FE 98 C4   INC $c498,x
    $C2D9: AC 6C C4   LDY $c46c
    $C2DC: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_C2DF:
    ; fx flag bit 2 — ARPEGGIO: on every odd $C49D frame, override pitch
    ; with (v_pitch + $18 = +24 semitones = 2 octaves). Standard Hubbard
    ; 2-tone arp; the song supplies the base, the arp doubles to base+2oct.
    $C2DF: AD 9B C4   LDA $c49b
    $C2E2: 29 04      AND #$04
    $C2E4: F0 2A      BEQ $c310        ; → L_C310  ; no arp: end of voice
    $C2E6: AD 9D C4   LDA $c49d
    $C2E9: 29 01      AND #$01
    $C2EB: F0 09      BEQ $c2f6        ; → L_C2F6  ; even frame: base note
    $C2ED: BD 7C C4   LDA $c47c,x      ; odd frame: v_pitch + 24
    $C2F0: 18         CLC
    $C2F1: 69 18      ADC #$18
    $C2F3: 4C F9 C2   JMP $c2f9        ; → L_C2F9
L_C2F6:
    $C2F6: BD 7C C4   LDA $c47c,x
L_C2F9:
    ; Write the (possibly arp'd) freq.
    $C2F9: 0A         ASL a
    $C2FA: A8         TAY
    $C2FB: B9 A9 C3   LDA $c3a9,y      ; freq_lo[pitch]
    $C2FE: 8D 84 C4   STA $c484
    $C301: B9 AA C3   LDA $c3aa,y      ; freq_hi[pitch]
    $C304: AC 6C C4   LDY $c46c
    $C307: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $C30A: AD 84 C4   LDA $c484
    $C30D: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_C310:
    ; Refresh $C4A0 (SFX-active flag) for the NEXT voice's writes.
    ; $C4A0 = $00 iff ($C49E == 0 AND $C49F bit 7 clear). Note this means
    ; voice X=2 (V3, first iter) uses the previous frame's $C4A0, but
    ; voices 1 and 0 see the current frame's state.
    $C310: A0 FF      LDY #$ff
    $C312: AD 9E C4   LDA $c49e
    $C315: D0 06      BNE $c31d        ; → L_C31D  ; force-override active
    $C317: AD 9F C4   LDA $c49f
    $C31A: 30 01      BMI $c31d        ; → L_C31D  ; slot inactive (bit 7 set)
    $C31C: C8         INY              ; Y := $00 (SFX active)
L_C31D:
    $C31D: 8C A0 C4   STY $c4a0
    $C320: CA         DEX
    $C321: 30 03      BMI $c326        ; → L_C326  ; all voices done: SFX player
    $C323: 4C 5F C0   JMP $c05f        ; → L_C05F  ; next voice
; ============================================================================
; SFX overlay player. Called every frame after the main loop. Owns V1+V2
; when active. See "HIGH-LEVEL FLOW" at top for state semantics.
; ============================================================================
L_C326:
    ; Default $C4A0 := $FF (main-mode) — refreshed here on the "all-voices-
    ; done" tail of the main loop so a one-shot SFX completing this frame
    ; cleanly hands V1+V2 back to main on the next frame.
    $C326: A9 FF      LDA #$ff
    $C328: 8D A0 C4   STA $c4a0
    ; Gate: only run SFX when ($C49E == 0 AND $C49F bit 7 clear).
    $C32B: AD 9E C4   LDA $c49e
    $C32E: D0 05      BNE $c335        ; → L_C335  ; force-override busy: skip
    $C330: 2C 9F C4   BIT $c49f
    $C333: 10 01      BPL $c336        ; → L_C336  ; slot active: run
L_C335:
    $C335: 60         RTS              ; idle frame
L_C336:
    ; First-frame: $C49F bit 6 set → load SFX params, then proceed.
    $C336: 50 03      BVC $c33b        ; → L_C33B
    $C338: 20 A9 C4   JSR $c4a9        ; → sub_C4A9  ; init from $CDA2 record
L_C33B:
    ; Per-frame divider: DEC counter, reload from $C4A8 low nibble when wrap.
    $C33B: CE A2 C4   DEC $c4a2
    $C33E: 10 F5      BPL $c335        ; → L_C335  ; not yet
    $C340: AD A8 C4   LDA $c4a8
    $C343: 29 0F      AND #$0f
    $C345: 8D A2 C4   STA $c4a2
    ; End-of-SFX check: current step ($C4A1) == end step ($C4A3) ?
    $C348: AD A1 C4   LDA $c4a1
    $C34B: CD A3 C4   CMP $c4a3
    $C34E: D0 0F      BNE $c35f        ; → L_C35F  ; not done
    ; Reached end: silence V1+V2 CTRL, set $C49F := $FF (deactivate).
    $C350: A2 00      LDX #$00
    $C352: 8E 04 D4   STX $d404      ;V1_CTRL
    $C355: 8E 0B D4   STX $d40b      ;V2_CTRL
    $C358: CA         DEX              ; X := $FF
    $C359: 8E 9F C4   STX $c49f
    $C35C: 4C 35 C3   JMP $c335        ; → L_C335
L_C35F:
    ; **SELF-MODIFYING TARGET**: sub_C4A9 patches this byte to $EE
    ; (INC $C4A1, rising-pitch SFX) or $CE (DEC $C4A1, falling-pitch SFX)
    ; based on bits 4-5 of the SFX's flags byte.
    $C35F: EE A1 C4   INC $c4a1
    $C362: 0A         ASL a            ; A = step * 2 (freq table idx)
    $C363: A8         TAY
    ; Voice-skip flags ($C4A8 bits 6,7) gate the freq writes.
    $C364: 2C A8 C4   BIT $c4a8
    $C367: 30 20      BMI $c389        ; → L_C389  ; bit 7: skip BOTH V1+V2 freq
    $C369: 70 0C      BVS $c377        ; → L_C377  ; bit 6: skip V1 (V2 only)
    $C36B: B9 A9 C3   LDA $c3a9,y      ; V1: freq_lo[step]
    $C36E: 8D 00 D4   STA $d400      ;V1_FREQ_LO
    $C371: B9 AA C3   LDA $c3aa,y      ; V1: freq_hi[step]
    $C374: 8D 01 D4   STA $d401      ;V1_FREQ_HI
L_C377:
    ; V2 plays the same step minus $C4A4 (semitone interval below V1).
    $C377: 98         TYA
    $C378: 38         SEC
    $C379: ED A4 C4   SBC $c4a4        ; step - interval
    $C37C: A8         TAY
    $C37D: B9 A9 C3   LDA $c3a9,y      ; V2: freq_lo[step-interval]
    $C380: 8D 07 D4   STA $d407      ;V2_FREQ_LO
    $C383: B9 AA C3   LDA $c3aa,y
    $C386: 8D 08 D4   STA $d408      ;V2_FREQ_HI
L_C389:
    ; CTRL-flip effect: if $C4A5 bit 7 set, EOR the saved V1 ctrl with
    ; $01 each frame → toggles the gate bit, producing a buzz/staccato.
    ; Same trick on V2 if bit 6 set.
    $C389: 2C A5 C4   BIT $c4a5
    $C38C: 10 0B      BPL $c399        ; → L_C399  ; no V1 flip
    $C38E: AD A6 C4   LDA $c4a6
    $C391: 49 01      EOR #$01
    $C393: 8D 04 D4   STA $d404      ;V1_CTRL
    $C396: 8D A6 C4   STA $c4a6        ; store back for next flip
L_C399:
    $C399: 50 0B      BVC $c3a6        ; → L_C3A6  ; no V2 flip
    $C39B: AD A7 C4   LDA $c4a7
    $C39E: 49 01      EOR #$01
    $C3A0: 8D 0B D4   STA $d40b      ;V2_CTRL
    $C3A3: 8D A7 C4   STA $c4a7
L_C3A6:
    $C3A6: 4C 35 C3   JMP $c335        ; → L_C335  ; RTS
; ----- data gap $C3A9-$C4A8 (256 bytes) -----
;   $C3A9-$C468  freq table (96 semitones × 2 bytes lo/hi)
;   $C469-$C46B  voice SID-offset table: $00 $07 $0E (V1 V2 V3)
;   $C46C-$C4A8  per-voice state arrays (see "DATA LAYOUTS" at top)

; ============================================================================
; sub_C4A9 — SFX init. Slot index in $C49F & $0F → 16-byte record at
; $CDA2,Y. Primes both per-frame state and the actual SID registers.
; ============================================================================
sub_C4A9:
    ; Silence V1+V2 and clear the SFX frame counter.
    $C4A9: A9 00      LDA #$00
    $C4AB: 8D 04 D4   STA $d404      ;V1_CTRL
    $C4AE: 8D 0B D4   STA $d40b      ;V2_CTRL
    $C4B1: 8D A2 C4   STA $c4a2
    ; Y = slot * 16. AND #$0F first to also clear bit 6 (first-frame flag).
    $C4B4: AD 9F C4   LDA $c49f
    $C4B7: 29 0F      AND #$0f
    $C4B9: 8D 9F C4   STA $c49f
    $C4BC: 0A         ASL a
    $C4BD: 0A         ASL a
    $C4BE: 0A         ASL a
    $C4BF: 0A         ASL a            ; × 16
    $C4C0: A8         TAY
    ; Scalar params from the record:
    $C4C1: B9 A2 CD   LDA $cda2,y      ; +0  → $C4A8 flags
    $C4C4: 8D A8 C4   STA $c4a8
    $C4C7: B9 A3 CD   LDA $cda3,y      ; +1  → $C4A1 start step
    $C4CA: 8D A1 C4   STA $c4a1
    $C4CD: B9 B1 CD   LDA $cdb1,y      ; +15 → $C4A3 end step
    $C4D0: 8D A3 C4   STA $c4a3
    ; $CDAA,Y +8 serves DUAL purpose: high 2 bits = ctrl-flip enables
    ; ($C4A5), low 6 bits = V2-below-V1 interval ($C4A4).
    $C4D3: B9 AA CD   LDA $cdaa,y      ; +8
    $C4D6: 8D A5 C4   STA $c4a5
    $C4D9: 29 3F      AND #$3f
    $C4DB: 8D A4 C4   STA $c4a4
    $C4DE: B9 A7 CD   LDA $cda7,y      ; +5  → $C4A6 V1 ctrl init
    $C4E1: 8D A6 C4   STA $c4a6
    $C4E4: B9 AE CD   LDA $cdae,y      ; +12 → $C4A7 V2 ctrl init
    $C4E7: 8D A7 C4   STA $c4a7
    $C4EA: A2 00      LDX #$00
L_C4EC:
    ; Blit 14 bytes from $CDA3,Y..$CDB0,Y → $D400..$D40D (V1+V2 registers
    ; FREQ_LO..SR). Note: the disassembler shows the operand as $C4A3,Y
    ; — that's because the assembler chose the alias closest to the
    ; running address. The raw bytes "B9 A3 CD" are LDA $CDA3,Y.
    $C4EC: B9 A3 CD   LDA $c4a3,y      ; (LDA $CDA3,Y)
    $C4EF: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $C4F2: C8         INY
    $C4F3: E8         INX
    $C4F4: E0 0E      CPX #$0e
    $C4F6: D0 F4      BNE $c4ec        ; → L_C4EC
    ; **SELF-MODIFY**: $C4A8 bits 4-5: if pattern $20, opcode = $EE (INC),
    ; else $CE (DEC). Patches the opcode at $C35F so the SFX walks step
    ; UP (rising pitch) or DOWN (falling pitch) per tick.
    $C4F8: AD A8 C4   LDA $c4a8
    $C4FB: 29 30      AND #$30         ; isolate bits 4-5
    $C4FD: A0 EE      LDY #$ee         ; INC $C4A1 opcode
    $C4FF: C9 20      CMP #$20
    $C501: F0 02      BEQ $c505        ; → L_C505
    $C503: A0 CE      LDY #$ce         ; DEC $C4A1 opcode
L_C505:
    $C505: 8C 5F C3   STY $c35f        ; patch the opcode at $C35F
    $C508: 60         RTS
; ----- data gap $C509-$CEA1 (2457 bytes) -----
;   $C509-$C50B  orderlist_lo (3): V1=$57 V2=$9D V3=$FE
;   $C50C-$C50E  orderlist_hi (3): all $C5
;   $C50F-$C532  pattern_lo[36]
;   $C533-$C556  pattern_hi[36]
;   $C557-$CD29  orderlist + pattern data (≈1990 bytes)
;   $CD2A-$CDA1  instrument table (15 records × 8 bytes:
;                  +0 PW_LO  +1 PW_HI  +2 CTRL  +3 AD  +4 SR
;                  +5 vib_div  +6 pulse_delta  +7 fx_flags)
;   $CDA2-$CEA1  SFX overlay table (16 records × 16 bytes — see sub_C4A9)

; Subtune dispatch tail: $CEA2/$CEA8 set the player state byte, $CEBC
; primes $C49F with the SFX slot index.
L_CEA2:
    ; subtune 0 path (or A=0 default): main song with all 3 voices.
    $CEA2: A9 40      LDA #$40         ; bit 6 = first-frame normal
    $CEA4: 8D 97 C4   STA $c497
    $CEA7: 60         RTS
L_CEA8:
    ; subtune >= 1 tail: SFX-only mode (main song muted).
    $CEA8: A9 C0      LDA #$c0         ; bits 6+7 = first-frame, SFX-only
    $CEAA: 8D 97 C4   STA $c497
    $CEAD: 60         RTS
; ----- data gap $CEAE-$CEBB (14 bytes) -----

L_CEBC:
    ; SFX slot picker. If $C49E (force-override) is already set (non-zero),
    ; copy it into $C49F so the override survives this init call. Else
    ; install ((subtune-1) | $40) — slot index in low nibble, first-frame
    ; in bit 6.
    $CEBC: AE 9E C4   LDX $c49e
    $CEBF: F0 04      BEQ $cec5        ; → L_CEC5
    $CEC1: 8E 9F C4   STX $c49f        ; preserve override
    $CEC4: 60         RTS
L_CEC5:
    $CEC5: 09 40      ORA #$40         ; A = subtune-1, OR $40 = first-frame
    $CEC7: 8D 9F C4   STA $c49f        ; install slot index
    $CECA: 60         RTS

; ======= init: =======
; A = subtune index (0-based from PSID). Two-way dispatch:
;   A == 0  → JMP $C000 → JMP $CEA2 → $C497 := $40   (song)
;   A >= 1  → A-- then JSR $C00F (→ $CEBC SFX-slot picker)
;            then JMP $C003 → JMP $CEA8 → $C497 := $C0   (SFX-only)
init:
    $CECB: C9 01      CMP #$01
    $CECD: B0 03      BCS $ced2        ; → L_CED2  ; A >= 1: SFX path
    $CECF: 4C 00 C0   JMP $c000        ; → L_C000  ; A == 0: song path
L_CED2:
    $CED2: 38         SEC
    $CED3: E9 01      SBC #$01         ; A := subtune - 1 (0..15)
    $CED5: 20 0F C0   JSR $c00f        ; → sub_C00F  ; install SFX slot
    $CED8: 4C 03 C0   JMP $c003        ; → L_C003  ; switch $C497 → $C0
