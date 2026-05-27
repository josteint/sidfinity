; ============================================================================
; Rob Hubbard - Hunter Patrol (1985 Mastertronic)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/Hubbard_Rob/Hunter_Patrol.sid
; Load:   $A000   Init: $AE1E   Play: $A006
; PSID:   1 subtune, default subtune 1
; Binary: $A000-$AE5F (3680 bytes)
;
; Auto-traced 835 reachable code bytes from init+play; the rest of the
; binary is freq/instrument tables, orderlist, pattern bodies, and three
; extra non-PSID entry points (standalone CIA-IRQ install/stop and the
; IRQ trampoline) that fall outside the static (init, play) trace.
; This file unfolds the auto-traced "data gap $A32D-$AE1D" into labelled
; sub-regions; bytes inside those regions that are reached only via
; ($A000, $A003) are disassembled in the EXTRA-ENTRIES section below.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; Three entry vectors at the top of the binary:
;   $A000: JMP $ADD0    — standalone-mode install (CIA1 timer + IRQ vector
;                         → $AE03, then JSR init, CLI, RTS). Not used in
;                         PSID mode.
;   $A003: JMP $AE09    — standalone-mode stop (restore default IRQ
;                         $EA31, vol=0, voice silence, CLI, RTS).
;   $A006: <play>       — PSID play entry (no JMP; the code starts here).
;
; init ($AE1E): Minimal 33 bytes. A holds subtune (0-indexed); ignored
; (1-subtune PSID, no selection logic). Zeros per-voice state
; $A3F1,X $A3F4,X $A3F7,X $A400,X for X=2..0, clears V1/V2/V3 ctrl
; ($D404/$D40B/$D412), sets volume to $0F. RTS.
;
; play ($A006): every frame.
;   1. INC $A426 — global frame counter (used by vibrato LFO, arp toggle,
;      skydive every-other-frame, PWM "every odd frame").
;   2. LDX #$02 — start with voice 3 (X=2), loop down to V1 (X=0) at end.
;   3. DEC $A418 — sub-frame divider. If still ≥ 0, skip reload (so
;      $A418 stays in [0, $A419]). If went negative, reload from $A419.
;   4. Per-voice loop body ($A016..$A329):
;      a. Cache SID voice base into $A3F0 (Y) from table at $A3ED.
;      b. Branch on ($A418 == $A419):
;         - TRUE  → "note frame": run pattern advance / note load
;           ($A025..$A114). One frame out of ($A419 + 1).
;         - FALSE → "tween frame": jump straight into effects ($A136).
;      c. Per-frame effects: vibrato + freq write ($A136..$A1C2),
;         PWM ($A1C3..$A243), portamento ($A246..$A28C),
;         drum decay ($A28D..$A2C8), skydive ($A2C9..$A2F4),
;         table arp / final freq write ($A2F5..$A325).
;      d. DEX; BPL $A016 → next voice. BMI → RTS.
;
; SUB-FRAME GATING (tempo):
;   $A418 counts down each frame. When it underflows it reloads to $A419.
;   The note-load branch only fires on the frame where $A418 == $A419,
;   i.e. the frame IMMEDIATELY AFTER the reload. So the effective tempo
;   period is ($A419 + 1) frames. The binary ships $A418=$01, $A419=$02
;   → period 3, with first note-load on frame 1.
;
; PER-NOTE STATE LIFECYCLE:
;   $A3F1,X = orderlist position (index into the voice's pattern list)
;   $A3F4,X = inner offset within the current pattern body
;   $A3F7,X = duration counter for the current note (counts DOWN)
;   $A3FA,X = saved raw note byte (re-read every frame by effects):
;             low 5 bits  = duration in frames
;             bit 5 ($20) = "no-release" flag (suppresses the soft
;                           release at duration=0; note holds until
;                           the next pattern byte changes it)
;             bit 6 ($40) = "no pitch column" (token has no pitch byte;
;                           used for pure-glide / state-only updates)
;             bit 7 ($80) = "extra byte follows" (instrument number
;                           if its b7=0, portamento descriptor if b7=1)
;             Vibrato is independently gated by (low 5 bits ≥ 8)
;             at $A194 — short notes simply don't wobble.
;   $A3FD,X = saved voice control byte (re-armed during drum effect)
;   $A400,X = saved pitch index (0..95 into freq table)
;   $A403,X = saved instrument number (0..31)
;   $A41B,X = current freq HI (mutated by portamento, drum, skydive)
;   $A41E,X = current freq LO (mutated by portamento)
;   $A421,X = portamento descriptor (b0=direction down, b7..b1=speed)
;   $A412,X = PWM frame counter (low 5 bits of instr byte 6)
;   $A415,X = PWM direction (0 = expanding pulse, !0 = shrinking)
;
; SCRATCHES SHARED ACROSS VOICES:
;   $A3F0 = SID voice base offset ($00 / $07 / $0E for V1/V2/V3)
;   $A406 = control mask ($FF normal, $FE = "no gate" — cleared after
;           note-on; used to suppress re-gating on tied/glide notes)
;   $A407 = scratch copy of raw note byte for BIT tests
;   $A408..$A410 = vibrato/freq-slide working registers
;   $A411 = vibrato LFO position 0..3 (triangle wave)
;   $A41A = current instrument's table offset (= instr × 8)
;   $A424 = current instrument's fx-flags byte (cached this frame)
;   $A425 = current instrument's pulse-delta speed (top 3 bits of byte 6)
;   $A426 = global frame counter (free-running, INC'd in play header)
;
; INSTRUMENT TABLE FORMAT (8 bytes × 32 records @ $A427):
;   byte 0: pulse_lo   (V_PW_LO)
;   byte 1: pulse_hi   (V_PW_HI, low nibble — high nibble bounds-checked
;                      against $08/$0E for PWM direction flips)
;   byte 2: ctrl       (V_CTRL — masked with $A406 = $FE on first frame)
;   byte 3: AD         (V_AD)
;   byte 4: SR         (V_SR)
;   byte 5: vib_shift  (LSR/ROR shift count for vibrato delta;
;                      shifts (next_freq - this_freq) right by N+1)
;   byte 6: pwm_word   (low 5 bits = PWM frame counter reload,
;                      top 3 bits = PWM delta amount; b3 of byte 7 picks
;                      between two PWM modes — see below)
;   byte 7: fx_flags
;          b0  drum         — short noise burst near end of long note
;          b1  skydive      — slow freq_hi decrement on long-tail notes
;          b2  table_arp    — +12 semitones on odd frames (octave doubling)
;          b3  PWM mode-A   — direct ADC of pwm_word low byte onto
;                             pulse_lo every frame (no counter, no bounds)
;          b3=0 PWM mode-B  — counted, bounded PWM: every (pwm low5)
;                             frames, add/subtract delta to PW; reflect
;                             at high-nibble bounds $08 and $0E
;
; ORDERLIST / PATTERN STRUCTURE:
;   $A527/$A528/$A529 = orderlist LSB for V1/V2/V3
;   $A52A/$A52B/$A52C = orderlist MSB for V1/V2/V3
;   Orderlist bytes are pattern indices; $FF = song-end loop marker
;   (resets orderlist position to 0 and inner pattern offset to 0).
;
;   $A52D + i = pattern i LSB
;   $A555 + i = pattern i MSB
;   (40 entries; only 39 are referenced by any voice.)
;
;   Pattern bodies live $A57D..$ADCF and are read via ($FD),Y. Each
;   "note token" in a pattern body is a variable-width record:
;     - duration byte: low 5 bits = duration (frames), b5/b6/b7 control
;       optional fields and release/glide flags (see $A057..$A0BD).
;     - optional instrument byte (if b7 of duration is set)
;     - pitch byte (always)
;   $FF terminates a pattern body and advances orderlist position.
;
; TEMPO INITIAL STATE (binary-loaded, NOT zeroed by init):
;   $A418 = $01     (sub-frame counter; first underflow at frame 2)
;   $A419 = $02     (reload value; effective period 3 frames)
;
; ============================================================================

; ===================== ENTRY VECTORS ($A000-$A005) =========================
;
; PSID players never touch $A000/$A003; sidplayfp jumps straight to
; init=$AE1E and play=$A006. These two vectors are for standalone use
; (the loader code in $ADD0 / $AE09).
sub_A000:
    $A000: 4C D0 AD    JMP $add0         ; → sub_ADD0 (standalone install)
sub_A003:
    $A003: 4C 09 AE    JMP $ae09         ; → sub_AE09 (standalone stop)

; ======= play: =======
; Called every frame by sidplayfp (or by the standalone IRQ trampoline
; at $AE03).
play:
    ; --- header: bump the free-running frame counter and start at V3 ---
    $A006: EE 26 A4    INC $a426         ; global frame counter ++
    $A009: A2 02       LDX #$02          ; X = voice index, walk 2 → 0
    ; Sub-frame divider for tempo gating. Note-load only fires on the
    ; frame where ($A418 == $A419), so the period is ($A419 + 1).
    $A00B: CE 18 A4    DEC $a418
    $A00E: 10 06       BPL $a016        ; → L_A016   (still ≥ 0, no reload)
    $A010: AD 19 A4    LDA $a419        ; underflowed → reload counter
    $A013: 8D 18 A4    STA $a418
L_A016:
    ; Cache SID voice base offset ($00 for V1, $07 for V2, $0E for V3)
    ; from the table at $A3ED. Subsequent writes use $D400,Y etc.
    $A016: BD ED A3    LDA $a3ed,x       ; voice-base table
    $A019: 8D F0 A3    STA $a3f0         ; $A3F0 = Y cache
    $A01C: A8          TAY
    ; --- tempo gate: note-frame vs tween-frame ---
    $A01D: AD 18 A4    LDA $a418
    $A020: CD 19 A4    CMP $a419
    $A023: D0 15       BNE $a03a        ; → L_A03A  (tween frame; effects only)
    ; --- note-frame path: set up zp pattern ptr (orderlist for this voice) ---
    $A025: BD 27 A5    LDA $a527,x       ; orderlist LSB per voice
    $A028: 85 FB       STA $fb
    $A02A: BD 2A A5    LDA $a52a,x       ; orderlist MSB per voice
    $A02D: 85 FC       STA $fc           ; ($FB) = &orderlist[voice]
    ; Per-voice note duration counter: count down; if still positive,
    ; no new note this frame — jump to per-frame effects at $A117.
    $A02F: DE F7 A3    DEC $a3f7,x
    $A032: 30 09       BMI $a03d        ; → L_A03D  (note expired, advance)
    $A034: 4C 17 A1    JMP $a117        ; → L_A117  (note still running)
; ----- data gap $A037-$A039 (3 bytes: 4C 26 A3) -----
;   Dead bytes from the fall-through past the JMP above — would decode
;   as "JMP $A326" but no live path reaches them.

L_A03A:
    ; Tween frame: skip note advance and go straight to effects.
    $A03A: 4C 36 A1    JMP $a136        ; → L_A136  (effects)

; ----- L_A03D: NOTE ADVANCE ------------------------------------------------
; Read the next pattern index from the orderlist. If $FF, wrap.
; Then dispatch to L_A057 to parse the note token inside the pattern.
L_A03D:
    $A03D: BC F1 A3    LDY $a3f1,x       ; Y = orderlist position
    $A040: B1 FB       LDA ($fb),y       ; pattern index (or $FF)
    $A042: C9 FF       CMP #$ff
    $A044: D0 11       BNE $a057        ; → L_A057  (got a pattern index)
    ; End-of-song marker: reset all the per-voice cursors to 0 and
    ; loop back. (The orderlist itself is left in place; $A3F1,X = 0
    ; restarts from the top.)
    $A046: A9 00       LDA #$00
    $A048: 9D F7 A3    STA $a3f7,x       ; duration counter = 0
    $A04B: 9D F1 A3    STA $a3f1,x       ; orderlist position = 0
    $A04E: 9D F4 A3    STA $a3f4,x       ; pattern inner offset = 0
    $A051: 4C 3D A0    JMP $a03d        ; → L_A03D  (re-read pattern index)
; ----- data gap $A054-$A056 (3 bytes: 4C 26 A3) -----
;   Same dead trampoline as $A037 — unreached fall-through stub.

; ----- L_A057: NOTE-TOKEN PARSE & FIRST-FRAME SID WRITES -------------------
; Uses the pattern index in A to look up ($FD) = pattern body pointer
; from the table at $A52D/$A555. Then walks the body byte stream:
;
;   byte_0  = "raw note byte" → $A3FA,X (and $A407 for BIT tests)
;             low 5 bits  = duration (frames)
;             bit 5 ($20) = "duration < 8 vibrato gate" (consumed later)
;             bit 6 ($40) = "no note column" (this token has no pitch
;                           byte and only adjusts a previous note —
;                           used for pure portamento / glides)
;             bit 7 ($80) = "extra instrument/glide byte follows"
;
;   if bit 7: byte_1 (instrument-or-glide):
;             b7=0 → instrument number; store into $A403,X (the byte
;                    itself is the new instrument)
;             b7=1 → portamento descriptor; store into $A421,X
;
;   if bit 6 clear: byte_pitch = next byte → $A400,X
;             pitch × 2 indexes the freq table at $A32D, writing
;             FREQ_LO / FREQ_HI for the voice and caching them into
;             $A41B,X / $A41E,X for portamento.
;             ($A406 = $FF here so the gate goes through; the
;             alternative branch at $A0C0 sets $A406 = $FE to suppress.)
;
; Then falls into L_A0C3 which writes the instrument bytes (PW, ctrl
; masked by $A406, AD, SR) and either advances the inner pattern
; offset or rolls over to the next orderlist slot.
L_A057:
    $A057: A8          TAY               ; Y = pattern index
    $A058: B9 2D A5    LDA $a52d,y       ; pattern_ptr_lo[index]
    $A05B: 85 FD       STA $fd
    $A05D: B9 55 A5    LDA $a555,y       ; pattern_ptr_hi[index]
    $A060: 85 FE       STA $fe           ; ($FD) = &pattern_body
    $A062: A9 00       LDA #$00
    $A064: 9D 21 A4    STA $a421,x       ; clear portamento descriptor
    $A067: BC F4 A3    LDY $a3f4,x       ; Y = inner pattern offset
    $A06A: A9 FF       LDA #$ff
    $A06C: 8D 06 A4    STA $a406         ; $A406 = $FF (gate-allowed mask)
    $A06F: B1 FD       LDA ($fd),y       ; byte_0: raw note byte
    $A071: 9D FA A3    STA $a3fa,x       ; save for effects use
    $A074: 8D 07 A4    STA $a407         ; copy for BIT tests
    $A077: 29 1F       AND #$1f
    $A079: 9D F7 A3    STA $a3f7,x       ; duration counter (low 5 bits)
    $A07C: 2C 07 A4    BIT $a407
    $A07F: 70 3F       BVS $a0c0        ; → L_A0C0  (b6 set → no pitch col)
    $A081: FE F4 A3    INC $a3f4,x       ; consume byte_0
    $A084: AD 07 A4    LDA $a407
    $A087: 10 11       BPL $a09a        ; → L_A09A  (b7 clear → no extra byte)
    ; --- extra byte: instrument number OR portamento descriptor ---
    $A089: C8          INY               ; advance to byte_1
    $A08A: B1 FD       LDA ($fd),y
    $A08C: 10 06       BPL $a094        ; → L_A094  (b7 clear: instrument)
    $A08E: 9D 21 A4    STA $a421,x       ; b7 set: portamento descriptor
    $A091: 4C 97 A0    JMP $a097        ; → L_A097
L_A094:
    $A094: 9D 03 A4    STA $a403,x       ; new instrument for this voice
L_A097:
    $A097: FE F4 A3    INC $a3f4,x       ; consume byte_1
L_A09A:
    ; --- pitch column: read pitch index, freq table lookup, write SID ---
    $A09A: C8          INY
    $A09B: B1 FD       LDA ($fd),y       ; pitch byte (0..95)
    $A09D: 9D 00 A4    STA $a400,x       ; cache for vibrato base
    $A0A0: 0A          ASL a             ; ×2 (16-bit freq table stride)
    $A0A1: A8          TAY
    $A0A2: B9 2D A3    LDA $a32d,y       ; freq_lo from table at $A32D
    $A0A5: 8D 08 A4    STA $a408         ; scratch (LO will be written below)
    $A0A8: B9 2E A3    LDA $a32e,y       ; freq_hi
    $A0AB: AC F0 A3    LDY $a3f0         ; Y = SID voice base
    $A0AE: 99 01 D4    STA $d401,y       ; V_FREQ_HI
    $A0B1: 9D 1B A4    STA $a41b,x       ; cache freq_hi for slides
    $A0B4: AD 08 A4    LDA $a408
    $A0B7: 99 00 D4    STA $d400,y       ; V_FREQ_LO
    $A0BA: 9D 1E A4    STA $a41e,x       ; cache freq_lo for slides
    $A0BD: 4C C3 A0    JMP $a0c3        ; → L_A0C3
L_A0C0:
    ; b6 of raw-note set: token has no pitch column. Clear b0 of the
    ; ctrl mask ($A406: $FF → $FE) so the gate is suppressed on the
    ; instrument re-arm below — this is how glides/ties keep the
    ; oscillator running without retriggering ADSR.
    $A0C0: CE 06 A4    DEC $a406         ; $A406 = $FE (no-gate mask)
L_A0C3:
    ; --- instrument re-arm: PW, ctrl(&mask), AD, SR ---
    ; X is voice index (0..2); save it to $A409 so we can use X as the
    ; instrument-table walker (×8 stride).
    $A0C3: AC F0 A3    LDY $a3f0         ; Y = SID voice base
    $A0C6: BD 03 A4    LDA $a403,x       ; current instrument number
    $A0C9: 8E 09 A4    STX $a409         ; save voice index
    $A0CC: 0A          ASL a
    $A0CD: 0A          ASL a
    $A0CE: 0A          ASL a             ; instr × 8
    $A0CF: AA          TAX               ; X now indexes instrument table
    $A0D0: BD 29 A4    LDA $a429,x       ; instr.ctrl
    $A0D3: 8D 0A A4    STA $a40a         ; save for $A3FD,X below
    $A0D6: BD 29 A4    LDA $a429,x       ; instr.ctrl (again)
    $A0D9: 2D 06 A4    AND $a406         ; mask with $FF or $FE (no-gate)
    $A0DC: 99 04 D4    STA $d404,y       ; V_CTRL
    $A0DF: BD 27 A4    LDA $a427,x       ; instr.pulse_lo
    $A0E2: 99 02 D4    STA $d402,y       ; V_PW_LO
    $A0E5: BD 28 A4    LDA $a428,x       ; instr.pulse_hi
    $A0E8: 99 03 D4    STA $d403,y       ; V_PW_HI
    $A0EB: BD 2A A4    LDA $a42a,x       ; instr.AD
    $A0EE: 99 05 D4    STA $d405,y       ; V_AD
    $A0F1: BD 2B A4    LDA $a42b,x       ; instr.SR
    $A0F4: 99 06 D4    STA $d406,y       ; V_SR
    $A0F7: AE 09 A4    LDX $a409         ; restore voice index
    $A0FA: AD 0A A4    LDA $a40a
    $A0FD: 9D FD A3    STA $a3fd,x       ; cache "armed" ctrl (gate set)
    ; --- advance inner pattern offset; rollover → orderlist++ ---
    $A100: FE F4 A3    INC $a3f4,x
    $A103: BC F4 A3    LDY $a3f4,x
    $A106: B1 FD       LDA ($fd),y       ; peek at the byte after this note
    $A108: C9 FF       CMP #$ff
    $A10A: D0 08       BNE $a114        ; → L_A114  (still inside pattern)
    $A10C: A9 00       LDA #$00
    $A10E: 9D F4 A3    STA $a3f4,x       ; reset inner offset
    $A111: FE F1 A3    INC $a3f1,x       ; orderlist position ++
L_A114:
    $A114: 4C 26 A3    JMP $a326        ; → L_A326  (next voice)

; ----- L_A117: NOTE STILL RUNNING ------------------------------------------
; Most frames take this path. Reads "no-retrigger" and "duration-out"
; conditions from the cached raw note byte, then either jumps to
; effects ($A136) or performs a soft note-off (clear gate, zero AD/SR).
L_A117:
    $A117: AC F0 A3    LDY $a3f0         ; Y = SID voice base
    $A11A: BD FA A3    LDA $a3fa,x       ; raw note byte
    $A11D: 29 20       AND #$20          ; bit 5 = "no release" / sustain
    $A11F: D0 15       BNE $a136        ; → L_A136  (b5 set: stay armed)
    $A121: BD F7 A3    LDA $a3f7,x       ; remaining duration
    $A124: D0 10       BNE $a136        ; → L_A136  (still > 0)
    ; Duration ran to zero AND no-release flag is clear → release:
    ; clear gate (and PWM bit) in cached ctrl, zero AD and SR. This
    ; gives the note an explicit envelope release at duration end.
    $A126: BD FD A3    LDA $a3fd,x       ; armed ctrl
    $A129: 29 FE       AND #$fe          ; clear gate bit
    $A12B: 99 04 D4    STA $d404,y       ; V_CTRL = ctrl & ~gate
    $A12E: A9 00       LDA #$00
    $A130: 99 05 D4    STA $d405,y       ; V_AD  = 0
    $A133: 99 06 D4    STA $d406,y       ; V_SR  = 0

; ----- L_A136: EFFECTS — VIBRATO + BASE FREQ -------------------------------
; This is the every-frame effects entry point. It always loads the
; current instrument's fx-flags into $A424 (cached for the rest of
; the frame) and computes a vibrato'd freq.
;
; Vibrato shape: triangle, 4 phases, derived from the global frame
; counter $A426 (low 3 bits, reflected past 4). Magnitude is the
; per-semitone freq delta shifted right by ($A42C[instr] + 1) — so
; small vib_shift = wide vibrato, large = narrow.
; The vibrato is GATED OFF for short notes (duration < 8 frames) so
; stings and percussion don't wobble.
L_A136:
    $A136: BD 03 A4    LDA $a403,x       ; current instrument
    $A139: 0A          ASL a
    $A13A: 0A          ASL a
    $A13B: 0A          ASL a             ; instr × 8
    $A13C: A8          TAY               ; Y = instr-table base
    $A13D: 8C 1A A4    STY $a41a         ; cache for PWM section
    $A140: B9 2E A4    LDA $a42e,y       ; instr.fx_flags
    $A143: 8D 24 A4    STA $a424         ; cache for the rest of the frame
    $A146: B9 2D A4    LDA $a42d,y       ; instr.pwm_word (delta+counter)
    $A149: 8D 0C A4    STA $a40c         ; scratch
    $A14C: B9 2C A4    LDA $a42c,y       ; instr.vib_shift
    $A14F: 8D 0B A4    STA $a40b         ; scratch — used as LSR loop count
    $A152: F0 6F       BEQ $a1c3        ; → L_A1C3   (vib_shift==0: no vib)
    ; Build triangle LFO position 0..3 from $A426 & $07: if ≥ 4, EOR $07
    ; (reflect 4..7 → 3..0). Result is 0..3.
    $A154: AD 26 A4    LDA $a426
    $A157: 29 07       AND #$07
    $A159: C9 04       CMP #$04
    $A15B: 90 02       BCC $a15f        ; → L_A15F
    $A15D: 49 07       EOR #$07
L_A15F:
    $A15F: 8D 11 A4    STA $a411         ; vibrato phase 0..3
    ; Compute (freq[pitch+1] - freq[pitch]) >> (vib_shift + 1) into
    ; ($A40D, $A40E) — the per-LFO-step freq delta.
    $A162: BD 00 A4    LDA $a400,x       ; pitch
    $A165: 0A          ASL a
    $A166: A8          TAY               ; Y = pitch × 2
    $A167: 38          SEC
    $A168: B9 2F A3    LDA $a32f,y       ; freq[pitch+1] LO
    $A16B: F9 2D A3    SBC $a32d,y       ; - freq[pitch] LO
    $A16E: 8D 0D A4    STA $a40d         ; delta LO
    $A171: B9 30 A3    LDA $a330,y       ; freq[pitch+1] HI
    $A174: F9 2E A3    SBC $a32e,y       ; - freq[pitch] HI (delta HI in A)
L_A177:
    ; Shift-right loop: (delta_HI:delta_LO) >>= 1, vib_shift+1 times.
    ; Loop predicate is BPL on a counter that goes 4..3..2..1..0..$FF.
    $A177: 4A          LSR a
    $A178: 6E 0D A4    ROR $a40d
    $A17B: CE 0B A4    DEC $a40b
    $A17E: 10 F7       BPL $a177        ; → L_A177
    $A180: 8D 0E A4    STA $a40e         ; delta HI (shifted)
    ; Base = freq[pitch], copy into ($A40F, $A410) as the running freq.
    $A183: B9 2D A3    LDA $a32d,y
    $A186: 8D 0F A4    STA $a40f
    $A189: B9 2E A3    LDA $a32e,y
    $A18C: 8D 10 A4    STA $a410
    ; Vibrato GATE: only apply for notes with low5 ≥ 8.
    $A18F: BD FA A3    LDA $a3fa,x
    $A192: 29 1F       AND #$1f
    $A194: C9 08       CMP #$08
    $A196: 90 1C       BCC $a1b4        ; → L_A1B4 (short note: skip vib add)
    ; Add delta × LFO-phase to running freq. Y = LFO position 0..3.
    $A198: AC 11 A4    LDY $a411
L_A19B:
    $A19B: 88          DEY
    $A19C: 30 16       BMI $a1b4        ; → L_A1B4 (loop exit)
    $A19E: 18          CLC
    $A19F: AD 0F A4    LDA $a40f
    $A1A2: 6D 0D A4    ADC $a40d
    $A1A5: 8D 0F A4    STA $a40f
    $A1A8: AD 10 A4    LDA $a410
    $A1AB: 6D 0E A4    ADC $a40e
    $A1AE: 8D 10 A4    STA $a410
    $A1B1: 4C 9B A1    JMP $a19b        ; → L_A19B
L_A1B4:
    ; Commit the vibrato'd (or base) freq to the SID for this voice.
    $A1B4: AC F0 A3    LDY $a3f0
    $A1B7: AD 0F A4    LDA $a40f
    $A1BA: 99 00 D4    STA $d400,y       ; V_FREQ_LO
    $A1BD: AD 10 A4    LDA $a410
    $A1C0: 99 01 D4    STA $d401,y       ; V_FREQ_HI

; ----- L_A1C3: PWM ---------------------------------------------------------
; Two PWM modes, selected by fx_flags bit 3:
;
;   bit3=1 ("mode-A", ADC sweep):  every frame, instr.pulse_lo
;     += instr.pwm_word (signed). The 12-bit PW is just allowed to
;     wrap inside the byte; only V_PW_LO is updated.
;
;   bit3=0 ("mode-B", counted/bounded): use top 3 bits of pwm_word as
;     a delta and low 5 bits as a frame-count reload. Counter $A412,X
;     decrements each frame; when it underflows, add/sub delta to PW
;     and reflect at PW high-nibble bounds $08 / $0E.
;
; The high-nibble bounds ($08, $0E) are Hubbard-engine HARDCODED —
; not per-instrument (see reference_hubbard_pwm_bounds.md).
L_A1C3:
    $A1C3: AD 24 A4    LDA $a424         ; fx_flags
    $A1C6: 29 08       AND #$08
    $A1C8: F0 15       BEQ $a1df        ; → L_A1DF  (bit3=0: mode-B)
    ; mode-A: pulse_lo += pwm_word; write back to instrument table AND
    ; V_PW_LO. Note this MUTATES the instrument record in place — when
    ; the same instrument is used again in another voice it picks up
    ; the modified pulse_lo. There is no explicit CLC here; AND doesn't
    ; touch the carry flag, so the ADC inherits whatever C was after
    ; the previous instruction sequence — in practice, the path from
    ; play header to here passes through DEC (no C effect) and CMP/AND
    ; (which leave C with the prior-frame value). Hubbard tolerates the
    ; resulting ±1 jitter in pulse_lo since the high nibble is bounded
    ; elsewhere; effectively a CLC; ADC for our purposes.
    $A1CA: AC 1A A4    LDY $a41a         ; Y = instr × 8
    $A1CD: B9 27 A4    LDA $a427,y       ; instr.pulse_lo
    $A1D0: 6D 0C A4    ADC $a40c         ; + pwm_word
    $A1D3: 99 27 A4    STA $a427,y       ; mutate instrument
    $A1D6: AC F0 A3    LDY $a3f0
    $A1D9: 99 02 D4    STA $d402,y       ; V_PW_LO
    $A1DC: 4C 46 A2    JMP $a246        ; → L_A246  (skip mode-B)
L_A1DF:
    ; mode-B: counter / bounds path.
    $A1DF: AD 0C A4    LDA $a40c
    $A1E2: F0 62       BEQ $a246        ; → L_A246  (pwm_word=0: disabled)
    $A1E4: AC 1A A4    LDY $a41a
    $A1E7: 29 1F       AND #$1f          ; low 5 bits = counter reload
    $A1E9: DE 12 A4    DEC $a412,x       ; per-voice PWM frame counter
    $A1EC: 10 58       BPL $a246        ; → L_A246  (not yet time to step)
    $A1EE: 9D 12 A4    STA $a412,x       ; reload counter
    $A1F1: AD 0C A4    LDA $a40c
    $A1F4: 29 E0       AND #$e0          ; top 3 bits = delta amount
    $A1F6: 8D 25 A4    STA $a425         ; cache delta
    $A1F9: BD 15 A4    LDA $a415,x       ; PWM direction (0=up, !0=down)
    $A1FC: D0 1A       BNE $a218        ; → L_A218  (down branch)
    ; UP branch: PW += delta; bound-check high nibble ≥ $0E → flip dir.
    $A1FE: AD 25 A4    LDA $a425
    $A201: 18          CLC
    $A202: 79 27 A4    ADC $a427,y       ; pulse_lo + delta
    $A205: 48          PHA               ; stash new PW_LO
    $A206: B9 28 A4    LDA $a428,y       ; pulse_hi
    $A209: 69 00       ADC #$00          ; carry from LO add
    $A20B: 29 0F       AND #$0f          ; keep low nibble only
    $A20D: 48          PHA               ; stash new PW_HI (masked)
    $A20E: C9 0E       CMP #$0e
    $A210: D0 1D       BNE $a22f        ; → L_A22F
    $A212: FE 15 A4    INC $a415,x       ; bound hit ($0E): direction = down
    $A215: 4C 2F A2    JMP $a22f        ; → L_A22F
L_A218:
    ; DOWN branch: PW -= delta; bound-check high nibble ≤ $08 → flip.
    $A218: 38          SEC
    $A219: B9 27 A4    LDA $a427,y
    $A21C: ED 25 A4    SBC $a425
    $A21F: 48          PHA               ; stash new PW_LO
    $A220: B9 28 A4    LDA $a428,y
    $A223: E9 00       SBC #$00
    $A225: 29 0F       AND #$0f
    $A227: 48          PHA               ; stash new PW_HI (masked)
    $A228: C9 08       CMP #$08
    $A22A: D0 03       BNE $a22f        ; → L_A22F
    $A22C: DE 15 A4    DEC $a415,x       ; bound hit ($08): direction = up
L_A22F:
    ; Commit stashed PW (both bytes) back to instrument table AND SID.
    $A22F: 8E 09 A4    STX $a409         ; save voice index
    $A232: AE F0 A3    LDX $a3f0         ; X = SID voice base (Y-style)
    $A235: 68          PLA               ; new PW_HI
    $A236: 99 28 A4    STA $a428,y       ; mutate instrument.pulse_hi
    $A239: 9D 03 D4    STA $d403,x       ; V_PW_HI
    $A23C: 68          PLA               ; new PW_LO
    $A23D: 99 27 A4    STA $a427,y       ; mutate instrument.pulse_lo
    $A240: 9D 02 D4    STA $d402,x       ; V_PW_LO
    $A243: AE 09 A4    LDX $a409         ; restore voice index

; ----- L_A246: PORTAMENTO --------------------------------------------------
; $A421,X holds the portamento descriptor (set from byte_1 with b7=1
; in the note parser). Layout:
;   b0    = direction (1 = down)
;   b7..1 = speed (per-frame freq delta, applied AND'd with $7E so b0
;           is dropped)
; Note that since $A421 is loaded by AND #$7E (not $FE), only 7 bits
; of speed are usable — bit 7 of the operand is discarded.
L_A246:
    $A246: AC F0 A3    LDY $a3f0         ; Y = SID voice base
    $A249: BD 21 A4    LDA $a421,x       ; portamento descriptor
    $A24C: F0 3F       BEQ $a28d        ; → L_A28D  (zero: no porta)
    $A24E: 29 7E       AND #$7e          ; speed (mask out direction bit)
    $A250: 8D 09 A4    STA $a409
    $A253: BD 21 A4    LDA $a421,x
    $A256: 29 01       AND #$01          ; direction
    $A258: F0 1B       BEQ $a275        ; → L_A275  (up)
    ; DOWN: freq -= speed (16-bit, propagated via carry)
    $A25A: 38          SEC
    $A25B: BD 1E A4    LDA $a41e,x       ; freq_lo
    $A25E: ED 09 A4    SBC $a409
    $A261: 9D 1E A4    STA $a41e,x
    $A264: 99 00 D4    STA $d400,y       ; V_FREQ_LO
    $A267: BD 1B A4    LDA $a41b,x       ; freq_hi
    $A26A: E9 00       SBC #$00
    $A26C: 9D 1B A4    STA $a41b,x
    $A26F: 99 01 D4    STA $d401,y       ; V_FREQ_HI
    $A272: 4C 8D A2    JMP $a28d        ; → L_A28D
L_A275:
    ; UP: freq += speed
    $A275: 18          CLC
    $A276: BD 1E A4    LDA $a41e,x
    $A279: 6D 09 A4    ADC $a409
    $A27C: 9D 1E A4    STA $a41e,x
    $A27F: 99 00 D4    STA $d400,y       ; V_FREQ_LO
    $A282: BD 1B A4    LDA $a41b,x
    $A285: 69 00       ADC #$00
    $A287: 9D 1B A4    STA $a41b,x
    $A28A: 99 01 D4    STA $d401,y       ; V_FREQ_HI

; ----- L_A28D: DRUM (fx_flags bit 0) ---------------------------------------
; A short downward freq sweep on the tail of a long note, ending in a
; one-frame noise burst with gate off. Produces a kick / tom thump.
; Gated by: drum flag, freq_hi != 0, duration counter != 0, and a
; remaining-duration threshold (last (raw_dur - 1) frames of the note).
L_A28D:
    $A28D: AD 24 A4    LDA $a424         ; fx_flags
    $A290: 29 01       AND #$01
    $A292: F0 35       BEQ $a2c9        ; → L_A2C9  (no drum)
    $A294: BD 1B A4    LDA $a41b,x
    $A297: F0 30       BEQ $a2c9        ; → L_A2C9  (freq_hi==0)
    $A299: BD F7 A3    LDA $a3f7,x
    $A29C: F0 2B       BEQ $a2c9        ; → L_A2C9  (duration ran out)
    $A29E: BD FA A3    LDA $a3fa,x
    $A2A1: 29 1F       AND #$1f          ; raw duration
    $A2A3: 38          SEC
    $A2A4: E9 01       SBC #$01          ; raw_dur - 1
    $A2A6: DD F7 A3    CMP $a3f7,x       ; vs remaining
    $A2A9: AC F0 A3    LDY $a3f0
    $A2AC: 90 10       BCC $a2be        ; → L_A2BE  (in last 1-frame burst)
    ; Tail sweep: freq_hi--, write to V_FREQ_HI; if cached ctrl & $FE
    ; is non-zero, ALSO commit it (re-arm without gate change).
    $A2AE: BD 1B A4    LDA $a41b,x
    $A2B1: DE 1B A4    DEC $a41b,x
    $A2B4: 99 01 D4    STA $d401,y       ; V_FREQ_HI
    $A2B7: BD FD A3    LDA $a3fd,x
    $A2BA: 29 FE       AND #$fe
    $A2BC: D0 08       BNE $a2c6        ; → L_A2C6
L_A2BE:
    ; Final-burst path: write current freq_hi, then set ctrl = $80
    ; (noise wave, gate=0 — gives one frame of noise tail).
    $A2BE: BD 1B A4    LDA $a41b,x
    $A2C1: 99 01 D4    STA $d401,y       ; V_FREQ_HI
    $A2C4: A9 80       LDA #$80          ; noise + gate off
L_A2C6:
    $A2C6: 99 04 D4    STA $d404,y       ; V_CTRL

; ----- L_A2C9: SKYDIVE (fx_flags bit 1) ------------------------------------
; A slow freq_hi-- sweep applied to long-tail notes near the end of
; their duration. Gated by: skydive flag, raw_dur ≥ $0C, remaining < 9,
; on odd global frames only, freq_hi != 0.
; Produces a "falling siren" tail on long sustained notes.
L_A2C9:
    $A2C9: AD 24 A4    LDA $a424
    $A2CC: 29 02       AND #$02
    $A2CE: F0 25       BEQ $a2f5        ; → L_A2F5
    $A2D0: BD FA A3    LDA $a3fa,x
    $A2D3: 29 1F       AND #$1f
    $A2D5: C9 0C       CMP #$0c
    $A2D7: 90 1C       BCC $a2f5        ; → L_A2F5  (note too short)
    $A2D9: BD F7 A3    LDA $a3f7,x
    $A2DC: C9 09       CMP #$09
    $A2DE: B0 15       BCS $a2f5        ; → L_A2F5  (still early in note)
    $A2E0: AD 26 A4    LDA $a426
    $A2E3: 29 01       AND #$01
    $A2E5: F0 0E       BEQ $a2f5        ; → L_A2F5  (every-other-frame)
    $A2E7: BD 1B A4    LDA $a41b,x
    $A2EA: F0 09       BEQ $a2f5        ; → L_A2F5  (freq_hi already 0)
    $A2EC: DE 1B A4    DEC $a41b,x       ; freq_hi--
    $A2EF: AC F0 A3    LDY $a3f0
    $A2F2: 99 01 D4    STA $d401,y       ; V_FREQ_HI

; ----- L_A2F5: TABLE ARPEGGIO (fx_flags bit 2) -----------------------------
; A simple +0 / +12 alternation driven by $A426 & 1: on odd global
; frames, overwrite the just-written freq with freq[pitch+12]
; (octave up). On even frames, rewrite freq[pitch] (which has the
; side effect of clobbering any vibrato/portamento adjustments from
; earlier this frame — so arp is mutually exclusive with vib/porta).
L_A2F5:
    $A2F5: AD 24 A4    LDA $a424
    $A2F8: 29 04       AND #$04
    $A2FA: F0 2A       BEQ $a326        ; → L_A326  (no arp)
    $A2FC: AD 26 A4    LDA $a426
    $A2FF: 29 01       AND #$01
    $A301: F0 09       BEQ $a30c        ; → L_A30C  (even frame: base pitch)
    $A303: BD 00 A4    LDA $a400,x       ; pitch
    $A306: 18          CLC
    $A307: 69 0C       ADC #$0c          ; + 12 semitones
    $A309: 4C 0F A3    JMP $a30f        ; → L_A30F
L_A30C:
    $A30C: BD 00 A4    LDA $a400,x       ; pitch
L_A30F:
    $A30F: 0A          ASL a
    $A310: A8          TAY
    $A311: B9 2D A3    LDA $a32d,y       ; freq_lo
    $A314: 8D 08 A4    STA $a408
    $A317: B9 2E A3    LDA $a32e,y       ; freq_hi
    $A31A: AC F0 A3    LDY $a3f0
    $A31D: 99 01 D4    STA $d401,y       ; V_FREQ_HI
    $A320: AD 08 A4    LDA $a408
    $A323: 99 00 D4    STA $d400,y       ; V_FREQ_LO

; ----- L_A326: NEXT VOICE / EXIT -------------------------------------------
L_A326:
    $A326: CA          DEX
    $A327: 30 03       BMI $a32c        ; → L_A32C
    $A329: 4C 16 A0    JMP $a016        ; → L_A016  (process V2, V1)
L_A32C:
    $A32C: 60          RTS

; ============================================================================
; STATIC DATA TABLES ($A32D-$A526)
; ============================================================================
;
; ----- $A32D-$A3EC : FREQ TABLE (96 semitones × 2 bytes, LE) ---------------
; Standard Hubbard pitch table. First entry is $0116 (A0-ish).
; Indexed by (pitch * 2) at $A0A2/$A0A5 etc.
;
; ----- $A3ED-$A3EF : SID VOICE BASE TABLE ($00, $07, $0E) ------------------
; Used at $A016 to compute Y = D400 + 7*voice without a multiply.
;
; ----- $A3F0-$A426 : VOICE STATE (mostly zeroed by init) -------------------
; See variable map above. Some entries are loaded from the binary:
;   $A418 = $01  (sub-frame counter initial; first underflow at frame 2)
;   $A419 = $02  (sub-frame reload; effective tempo period = 3 frames)
;
; ----- $A427-$A526 : INSTRUMENT TABLE (32 × 8 bytes) -----------------------
; Records 0..16 are used (0..16 hold non-zero data); records 17..31 are
; zero fill. Layout per record: pulse_lo, pulse_hi, ctrl, AD, SR,
; vib_shift, pwm_word, fx_flags (see "INSTRUMENT TABLE FORMAT" above).
;
; ----- $A527-$A52C : ORDERLIST POINTERS (per voice) ------------------------
;   V1 orderlist @ $A57D, V2 @ $A595, V3 @ $A5AD
;   $A527/$A52A = V1 LSB/MSB ($7D / $A5)
;   $A528/$A52B = V2 LSB/MSB ($95 / $A5)
;   $A529/$A52C = V3 LSB/MSB ($AD / $A5)
;
; ----- $A52D-$A554 : PATTERN POINTER LSB TABLE (40 patterns) ---------------
; ----- $A555-$A57C : PATTERN POINTER MSB TABLE (40 patterns) ---------------
; Pattern 0 is unused (no orderlist references it); patterns 1..39 are
; referenced.
;
; ----- $A57D-$ADCF : PATTERN BODIES & ORDERLISTS (interleaved) -------------
; The first three patterns/orderlists ARE the V1/V2/V3 orderlist data:
;   $A57D-$A594  V1 orderlist: 13 03 05 0D 0F 03 05 08 15 1A 1A 1D 1D
;                              1F 03 05 22 24 22 26 0F 03 05 FF
;   $A595-$A5AC  V2 orderlist: 14 04 06 0E 10 04 06 09 16 1B 1B 1E 1E
;                              20 04 06 23 25 23 27 10 04 06 FF
;   $A5AD-$A613  V3 orderlist (96 entries + $FF) — repeats two short
;                              motifs across the bass line
; Then $A614..$ADCF holds the actual pattern bodies (39 patterns).
;
; ============================================================================
; EXTRA ENTRY POINTS — STANDALONE MODE
; ============================================================================
; These are reachable only via $A000/$A003 (the standalone install/stop
; trampolines at the top of the binary). PSID players ignore them.
;
; sub_ADD0: Install C64 CIA timer + IRQ vector for hands-free play.
;   - Point $0314 (kernel IRQ vector) at $AE03 (the play trampoline).
;   - Stop CIA1 timer A, clear raster IRQ.
;   - Load CIA1 timer A with $4800 cycles (≈ 53.4 Hz on PAL, slightly
;     faster than the 50.12 Hz raster — a known Hubbard quirk).
;   - $DC0D = $7F (clear all CIA1 IRQ sources), then $81 (enable
;     timer A IRQ).
;   - $DC0E = $01 (force load + run timer A).
;   - JSR $AE1E (init).
;   - CLI; RTS.
sub_ADD0:
    $ADD0: 78          SEI
    $ADD1: A9 03       LDA #$03
    $ADD3: 8D 14 03    STA $0314
    $ADD6: A9 AE       LDA #$ae
    $ADD8: 8D 15 03    STA $0315          ; IRQ vector ← $AE03
    $ADDB: A9 00       LDA #$00
    $ADDD: 8D 0E DC    STA $dc0e          ; CIA1 TimerA stop
    $ADE0: A9 00       LDA #$00
    $ADE2: 8D 1A D0    STA $d01a          ; raster IRQ off
    $ADE5: A9 00       LDA #$00
    $ADE7: 8D 04 DC    STA $dc04          ; CIA1 TA LO = $00
    $ADEA: A9 48       LDA #$48
    $ADEC: 8D 05 DC    STA $dc05          ; CIA1 TA HI = $48  ($4800 cyc)
    $ADEF: A9 7F       LDA #$7f
    $ADF1: 8D 0D DC    STA $dc0d          ; clear all CIA1 IRQ sources
    $ADF4: A9 81       LDA #$81
    $ADF6: 8D 0D DC    STA $dc0d          ; enable TimerA IRQ
    $ADF9: A9 01       LDA #$01
    $ADFB: 8D 0E DC    STA $dc0e          ; force-load + run TimerA
    $ADFE: 20 1E AE    JSR $ae1e          ; → init
    $AE01: 58          CLI
    $AE02: 60          RTS
; sub_AE03: IRQ trampoline — called by the kernel via $0314/$0315 every
; time CIA1 TimerA fires. Just runs play and chains to the kernel's
; normal IRQ exit ($EA7E).
sub_AE03:
    $AE03: 20 06 A0    JSR $a006          ; → play
    $AE06: 4C 7E EA    JMP $ea7e          ; kernel IRQ exit
; sub_AE09: Standalone-mode stop. Restore default IRQ ($EA31), zero
; volume, silence voices via the init's bottom half ($AE31), CLI, RTS.
sub_AE09:
    $AE09: 78          SEI
    $AE0A: A9 31       LDA #$31
    $AE0C: 8D 14 03    STA $0314
    $AE0F: A9 EA       LDA #$ea
    $AE11: 8D 15 03    STA $0315          ; IRQ vector ← $EA31 (default)
    $AE14: A9 00       LDA #$00
    $AE16: 8D 18 D4    STA $d418          ; volume = 0
    $AE19: 20 31 AE    JSR $ae31          ; → silence voices + vol=$0F
    $AE1C: 58          CLI
    $AE1D: 60          RTS

; ======= init: =======
; Tiny init. Zeros four per-voice state cells (orderlist pos, inner
; offset, duration counter, pitch) for X=2..0, then silences the three
; voices and sets vol=$0F. Does NOT touch:
;   - $A418/$A419 tempo cells (binary-loaded as $01/$02)
;   - $A426 frame counter (binary-loaded)
;   - $A41B-$A420 freq state, $A421-$A423 portamento, $A412-$A417 PWM
;     state — these survive load and are effectively binary-driven
;     initial conditions.
;
; Subtune number arrives in A but is ignored (single-subtune PSID).
init:
    $AE1E: A9 00       LDA #$00
    $AE20: A2 02       LDX #$02
L_AE22:
    $AE22: 9D F1 A3    STA $a3f1,x        ; orderlist position = 0
    $AE25: 9D F4 A3    STA $a3f4,x        ; inner pattern offset = 0
    $AE28: 9D F7 A3    STA $a3f7,x        ; duration counter = 0
    $AE2B: 9D 00 A4    STA $a400,x        ; saved pitch = 0
    $AE2E: CA          DEX
    $AE2F: 10 F1       BPL $ae22         ; → L_AE22
    ; This bottom half ($AE31..$AE3F) is also entered from sub_AE09 as
    ; "silence voices + set vol=$0F" — same effect as a fresh init.
    $AE31: 8D 04 D4    STA $d404         ; V1_CTRL = 0
    $AE34: 8D 0B D4    STA $d40b         ; V2_CTRL = 0
    $AE37: 8D 12 D4    STA $d412         ; V3_CTRL = 0
    $AE3A: A9 0F       LDA #$0f
    $AE3C: 8D 18 D4    STA $d418         ; VOL = $0F
    $AE3F: 60          RTS

; ----- $AE40-$AE5F : ripper signature --------------------------------------
; ASCII "TUNE RIPPED BY G.GOUWELOOS    " (padded with spaces). Not
; engine code; payload tail.
;
; ============================================================================
; NOTES FOR CODEGEN PORTING
; ============================================================================
;
; Compared to Action Biker (the existing pipelines/action_biker scaffold),
; Hunter Patrol's player is the same family but exercises MORE effects:
;
;   - Vibrato is present and gated by note-duration ≥ 8 (Action Biker
;     does not have the duration-gated vibrato path).
;   - PWM mode-A (fx bit 3 = direct ADC sweep) IS used by some
;     instruments (e.g. instr 0 at $A427: pwm_word=$40, fx_flags=$08).
;     This MUTATES the instrument table in place — codegen must model
;     the instrument record as mutable state, not a constant lookup.
;   - PWM mode-B (counted/bounded) reflects at HARDCODED bounds $08
;     and $0E on the high nibble of pulse_hi (see
;     reference_hubbard_pwm_bounds.md).
;   - Drum, skydive, and table-arp effects are all wired up and used.
;
; First-frame timing differs from Action Biker:
;   - Action Biker uses a "first-frame" flag in $C3EA bit 6 → one-time
;     setup at $C28E that copies orderlist pointers from a per-subtune
;     table.
;   - Hunter Patrol has NO per-subtune setup (1 subtune); the orderlist
;     pointers are static at $A527-$A52C and the binary itself supplies
;     the tempo counter initial state. The first note-load fires on
;     frame 2 (when $A418 underflows for the first time and reloads
;     to $A419=2).
;
; ============================================================================
