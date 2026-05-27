; ============================================================================
; Rob Hubbard - Chimera (1985 Firebird)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/Hubbard_Rob/Chimera.sid
; Load:   $9F80   Init: $9F80   Play: $0000 (PSID claims 0; IRQ-driven via $0314/$0315)
; PSID:   4 subtunes, default subtune 1 (1-indexed)
; Binary: $9F80-$CF9A (12314 bytes), 1330 reachable code bytes (10.8%).
;
; Annotations hand-derived by combining static analysis with
; pipelines/chimera/codegen/Chimera/Codegen.lean — the reference
; implementation that produces a Grade A rebuild of this SID.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; The Chimera binary is two cooperating players in one file:
;
;   * Music engine at $C200 — the standard Hubbard 1985 layout (same shape
;     as Action Biker, Monty, Commando). 3 voices, pattern-step orderlist,
;     7-byte instrument records, fx_flags effect bits.
;
;   * Digi/SFX player at $C000 — a separate routine that plays 4-bit-per-sample
;     digital audio through V1's pulse/tri waveform select (test-bit toggle
;     between $41/$49) paced by CIA2 timer ($DD04/$DD05). Blanks the screen
;     during playback to avoid badline interference.
;
; A PSID-level wrapper at $9F80 dispatches between them based on subtune:
;
;   PSID init ($9F80): A = subtune (0-indexed).
;     A < 2 → music: install IRQ vector to $9FA0, JSR $C200 (music init), CLI, RTS.
;     A >= 2 → SFX: restore default IRQ ($EA31), JSR $9FEC (silence SID),
;             then trampoline to $C000 with sample-bank pointers loaded from
;             $9FE2,X / $9FE4,X (X = subtune - 2).
;
;   IRQ at $9FA0 (raster IRQ, installed for music): INC $D019 to ack the
;     raster latch, JSR $C206 (music play), JMP $EA31 to the KERNAL IRQ
;     exit. Called 50/60 Hz by the C64.
;
; MUSIC ENGINE ENTRY POINTS
; --------------------------
; $C200: JMP $CF63 — init vector. EOR #$FF on subtune (one's complement),
;         multiply by 6, copy 6 bytes from $C700+subtune*6 to $C6FA (per-voice
;         orderlist pointers), clear V1/V2/V3 ctrl, vol=$0F, state byte
;         $C655 = $40 (first-frame bit set).
; $C203: JMP $CF94 — stop vector. Sets state byte $C655 = $C0 (bit 7
;         end-of-song + bit 6 first-frame).
; $C206: PLAY entry. Called once per frame from the IRQ at $9FA3.
;         1. INC $C661 (global frame counter).
;         2. BIT $C655 (state byte): bit 7 = end-of-song, bit 6 = first-frame.
;            - bit 7 set → end path: zero V1/V2/V3 ctrl, state = $80, then
;              fall through to effects-loop RTS at $C566.
;            - bit 6 set → first-frame: zero per-voice state arrays
;              ($C62B,X $C62E,X $C631,X $C63A,X for X=0..2), state = 0.
;            - both clear → normal play.
;         3. Fall through to per-voice processing at $C241.
;
; PER-VOICE PROCESSING ($C241..$C566)
; ------------------------------------
;   X iterates 2..0 (V3, V2, V1).
;   * $C652/$C653 = current/reload sub-frame tick divider.
;   * Note-load gate at $C255-$C25B: load runs only when $C652 == $C653 (i.e.
;     on the tick AFTER reload, which is once per (reload+1) frames).
;   * On a note-load tick:
;       - read orderlist pointer ($C6FA,X / $C6FD,X) into $56/$57
;       - decrement $C631,X (per-voice duration counter); when negative,
;         advance to the next pattern step.
;   * Off a note-load tick: jump straight to the effects loop ($C375).
;   * Pattern step machinery ($C275-$C353):
;       - $C62B,X = column index in pattern (within current orderlist step).
;       - $C62E,X = byte index within pattern row.
;       - Pattern bytes (read via ($58),Y):
;           $FE → song end (JMP $C203 → state=$C0).
;           $FF → end of pattern; reset $C631,X, $C62B,X, $C62E,X; retry.
;           else → note (low 5 bits of flag byte = duration, etc.)
;       - On note: $C634,X = pattern flag byte; $C631,X = flag & $1F;
;         $C63A,X = note num; lookup freq via freq table at $C567,Y stride 2;
;         lookup instrument data (pulse_lo/hi at $C662,Y, ctrl at $C664,Y, etc.).
;
; INSTRUMENT TABLE ($C662, 8-byte records, Y = inst*8)
; -----------------------------------------------------
;   $C662 + Y: pulse_lo
;   $C663 + Y: pulse_hi
;   $C664 + Y: ctrl (waveform select + gate)
;   $C665 + Y: AD
;   $C666 + Y: SR
;   $C667 + Y: PW speed (encoded: low 5 bits period, high 3 bits step)
;   $C668 + Y: PW init data
;   $C669 + Y: fx_flags
;
; FX_FLAGS BIT SEMANTICS ($C65F latched from $C669+inst*8)
; ---------------------------------------------------------
;   bit 0 ($01): freq_slide / drums.  At note START (dur counter == max):
;                  write current freq_hi, ctrl = $80 (noise+test, silences osc).
;                On note PROGRESS: DEC freq_hi in memory, write OLD value,
;                  ctrl &= $FE (gate off). Produces the drum-like decaying tail.
;   bit 1 ($02): freq_hi INC every other frame, gated by duration >= $11
;                and freq_hi != 0. Disassembly at $C526 does INC; the
;                Chimera codegen models "skydive" as DEC — the 1.2%
;                writelog gap may live here. Worth re-checking against
;                siddump --writelog before changing the codegen.
;   bit 2 ($04): octave-up arpeggio. Every 4-of-8 frames (frame & 7 != 0..3),
;                add +$0C semitones to note num, lookup freq, write.
;   bit 3 ($08): linear PW kick. ADC pulse_lo + $C668 (PW init), ORA $40
;                forces pulse_hi bit 6 on; writes to D402 once per frame.
;                Skips the bidirectional PW loop at $C420.
;   The bidirectional PWM at $C420-$C484 runs whenever $C668 ($C646
;     latched) != 0; it sweeps pulse_lo/hi between $08 and $0E bounds on
;     pulse_hi (HARDCODED — see reference_hubbard_pwm_bounds.md).
;
; STATE BYTES (the variable region inside the binary)
; ----------------------------------------------------
;   $C627..$C629 : SID base offset per voice ($00, $07, $0E)
;   $C62A        : SID base for current voice (latched in voice loop)
;   $C62B,X      : pattern column index per voice
;   $C62E,X      : byte index in pattern row per voice
;   $C631,X      : duration counter per voice
;   $C634,X      : current pattern flag byte per voice
;   $C637,X      : current ctrl register value per voice
;   $C63A,X      : current note num per voice
;   $C63D,X      : current instrument index per voice
;   $C640..$C64F : scratch (ctrl mask, vibrato deltas, PWM sub-counters)
;   $C652/$C653  : sub-frame tick (current/reload)
;   $C654        : current instr*8, saved across voice loop body
;   $C655        : state byte (bit 7 end, bit 6 first-frame)
;   $C656,X      : current SID freq HI per voice
;   $C659,X      : current SID freq LO per voice
;   $C65C,X      : pitch slide per-voice
;   $C65F        : fx_flags for current instrument (latched)
;   $C660        : current PWM step (& $E0)
;   $C661        : global frame counter
;   $C662+       : instrument table (see above)
;   $C6FA..$C6FF : per-voice orderlist pointers (lo[3], hi[3])
;   $C700+       : per-subtune orderlists (6 bytes/subtune)
;   $C70C/$C73D  : pattern pointer lo/hi tables
;
; CONSEQUENCE FOR THE PIPELINE
; -----------------------------
; pipelines/chimera/ already targets this engine and produces a Grade A
; rebuild (98.8% siddump snapshot match, py65 0-divergence over 1500
; frames). The remaining ~1.2% gap is libsidplayfp CIA/cycle-exact
; subtleties (or possibly the bit-1 INC vs codegen DEC, see above) —
; not anything that changes what the SID chip outputs.
;
; The SFX player at $C000 is intentionally not modelled by the pipeline;
; only the 3 music subtunes are.
;
; ============================================================================

; ======= PSID init wrapper (entry from sidplayfp) =======
; A on entry holds the 0-indexed subtune. For music subtunes (A < 2) we
; install our raster-IRQ handler at $9FA0 and call the music engine init
; at $C200. For SFX subtunes (A >= 2) we fall through to $9FEC and from
; there to $9FB0 (sample dispatcher).
L_9F80:
    $9F80: C9 02      cmp  #$02         ; subtune index >= 2?
    $9F82: B0 68      bcs  $9FEC      ; → L_9FEC  ; yes → SFX dispatch
    $9F84: 48         pha               ; save A (subtune) across IRQ setup
    $9F85: 78         sei               ; disable IRQs while patching vectors
    $9F86: A9 9F      lda  #$9F
    $9F88: 8D 15 03   sta  $0315        ; CINV hi = $9F (low+hi = $9FA0)
    $9F8B: A9 A0      lda  #$A0
    $9F8D: 8D 14 03   sta  $0314        ; CINV lo = $A0
    $9F90: A2 00      ldx  #$00
    $9F92: 8E 0E DC   stx  $DC0E        ; CIA1 Timer A control = 0 (stop)
    $9F95: E8         inx               ; X = 1
    $9F96: 8E 1A D0   stx  $D01A        ; VIC IRQ mask: enable raster IRQ
    $9F99: 68         pla               ; restore A (subtune) for engine init
    $9F9A: 20 00 C2   jsr  $C200      ; → L_C200   ; music engine init
    $9F9D: 58         cli               ; re-enable IRQs
    $9F9E: EA         nop
    $9F9F: 60         rts
; ======= Raster IRQ handler (installed by music init) =======
; Called 50/60 Hz by the C64 VIC raster. Just ticks the music engine
; and returns through the KERNAL IRQ exit.
L_9FA0:
    $9FA0: EE 19 D0   inc  $D019        ; ack VIC raster IRQ latch
    $9FA3: 20 06 C2   jsr  $C206      ; → L_C206   ; play one frame of music
    $9FA6: 4C 31 EA   jmp  $EA31      ; → L_EA31   ; KERNAL IRQ exit
; ----- data gap $9FA9-$9FB0 (7 bytes) -----

; ======= SFX dispatch wrapper =======
; Reached from $9FEC (after the SID silence loop) when the requested
; subtune was >= 2. Restores the default KERNAL IRQ vector (no music
; tick), enables CIA1 Timer A as a CPU-driven IRQ source, picks the
; right sample bank for (subtune - 2), and trampolines to the digi
; player at $C000.
L_9FB0:
    $9FB0: 48         pha               ; save subtune
    $9FB1: 78         sei
    $9FB2: A9 31      lda  #$31
    $9FB4: 8D 14 03   sta  $0314        ; CINV lo = $31 (default $EA31)
    $9FB7: A9 EA      lda  #$EA
    $9FB9: 8D 15 03   sta  $0315        ; CINV hi = $EA
    $9FBC: A2 01      ldx  #$01
    $9FBE: 8E 0E DC   stx  $DC0E        ; CIA1 Timer A: start, one-shot
    $9FC1: CA         dex               ; X = 0
    $9FC2: 8E 1A D0   stx  $D01A        ; VIC IRQ mask: disable raster IRQ
    $9FC5: EA         nop
    $9FC6: 68         pla               ; A = subtune
    $9FC7: 38         sec
    $9FC8: E9 02      sbc  #$02         ; A = subtune - 2 (SFX bank index)
    $9FCA: AA         tax
    $9FCB: A9 35      lda  #$35
    $9FCD: 85 01      sta  $01          ; bank in CHARROM + I/O (RAM under BASIC)
    $9FCF: BD E2 9F   lda  $9FE2,X      ; sample-bank lo table (data $9FE2..$9FE5)
    $9FD2: 8D 0A A1   sta  $A10A        ; → digi player's source pointer lo
    $9FD5: BD E4 9F   lda  $9FE4,X      ; sample-bank hi table
    $9FD8: 85 97      sta  $97
    $9FDA: A9 37      lda  #$37
    $9FDC: 85 01      sta  $01          ; restore default banking (BASIC+I/O)
    $9FDE: 4C 00 C0   jmp  $C000      ; → L_C000   ; jump to digi player
; ----- data gap $9FE1-$9FEC (11 bytes) -----

; ======= silence-then-SFX trampoline =======
; Branched here from $9F82 when subtune index >= 2. Zero $D400..$D418
; (all SID regs incl. master vol) and zero-page slot $FD (used by the
; digi player for vol modulation), then jump into the SFX dispatcher.
L_9FEC:
    $9FEC: 48         pha               ; save subtune across loop
    $9FED: A9 00      lda  #$00
    $9FEF: 85 FD      sta  $FD          ; zero $FD (digi player vol base)
    $9FF1: A2 00      ldx  #$00
L_9FF3:
    $9FF3: 9D 00 D4   sta  $D400,X      ; silence loop body
    $9FF6: E8         inx
    $9FF7: E0 19      cpx  #$19         ; loop 0..$18 (D400..D418)
    $9FF9: D0 F8      bne  $9FF3      ; → L_9FF3
    $9FFB: 68         pla               ; restore subtune
    $9FFC: 4C B0 9F   jmp  $9FB0      ; → L_9FB0   ; into SFX dispatcher
; ----- data gap $9FFF-$C000 (8193 bytes) -----

; ======= Digi/SFX player vector =======
; Two-byte trampoline so the wrapper at $9FDE can `JMP $C000` without
; needing to know the exact body address. The 3 zero bytes at $C003-$C005
; pad to $C006 for the real entry.
L_C000:
    $C000: 4C 06 C0   jmp  $C006      ; → L_C006
; ----- data gap $C003-$C006 (3 bytes) -----

; ======= digi player entry =======
; Save zero-page scratch, mask off bit 6 of $01 (page in I/O over BASIC),
; cache $D011 (VIC ctrl) for restore at exit, and pick the playback path
; from $A103 (sample-table length). 0 → "silence" path (just calls $C109
; then exits), non-zero → main sample loop.
L_C006:
    $C006: A5 F7      lda  $F7          ; save zero-page scratch...
    $C008: 48         pha
    $C009: A5 F8      lda  $F8
    $C00B: 48         pha
    $C00C: A5 F9      lda  $F9
    $C00E: 48         pha
    $C00F: A5 FA      lda  $FA
    $C011: 48         pha
    $C012: 78         sei               ; disable IRQs across sample playback
    $C013: A9 3E      lda  #$3E
    $C015: 25 01      and  $01          ; clear bit 0 (CHAREN) — leaves $36
    $C017: 85 01      sta  $01          ; banking: RAM+I/O+KERNAL, no BASIC
    $C019: AD 11 D0   lda  $D011        ; cache VIC ctrl (saved at $C130)
    $C01C: 8D 30 C1   sta  $C130        ; to restore at $C0EF
    $C01F: A2 00      ldx  #$00
    $C021: AC 03 A1   ldy  $A103        ; Y = sample-table length
    $C024: C0 00      cpy  #$00
    $C026: D0 06      bne  $C02E      ; → L_C02E   ; non-empty → main loop
    $C028: 20 09 C1   jsr  $C109      ; → L_C109   ; "ping" sweep (drum hit?)
    $C02B: 4C EA C0   jmp  $C0EA      ; → L_C0EA   ; clean exit
; Search the sample-table at $A10B for an entry matching $97 (sample bank
; hi from the wrapper). If found at index X, jump to $C03F. If not found
; after Y iterations, "ping" via $C109 and exit.
L_C02E:
    $C02E: BD 0B A1   lda  $A10B,X      ; sample-table[X]
    $C031: C5 97      cmp  $97          ; matches requested bank?
    $C033: F0 0A      beq  $C03F      ; → L_C03F   ; yes
    $C035: E8         inx
    $C036: 88         dey
    $C037: D0 F5      bne  $C02E      ; → L_C02E   ; loop
    $C039: 20 09 C1   jsr  $C109      ; → L_C109   ; not found → ping
    $C03C: 4C EA C0   jmp  $C0EA      ; → L_C0EA   ; exit
; ======= digi player main entry: set up sample pointers + CIA2 timer =======
; Bank table at $A000+X*4 holds {sample-base lo, hi, length lo, hi} per
; bank. Loads source pointer $FB/$FC, length counter $F7/$F8. Sets
; D402/D403 (pulse PW) and DD04/DD05 (CIA2 timer) to $FFFF, gates V1 SR
; to $F0 (long release used as decay envelope per sample). If $A108
; flag is 0, blanks the screen ($D011 = 0) to avoid badline-induced
; jitter on sample writes.
L_C03F:
    $C03F: AD 0A A1   lda  $A10A        ; sample-rate pacing byte
    $C042: 8D AC C0   sta  $C0AC        ; self-modify the wait-loop compare
    $C045: A5 97      lda  $97
    $C047: 0A         asl  A
    $C048: 0A         asl  A            ; X = bank * 4
    $C049: AA         tax
    $C04A: BD 00 A0   lda  $A000,X      ; sample source lo
    $C04D: 85 FB      sta  $FB
    $C04F: BD 01 A0   lda  $A001,X      ; sample source hi
    $C052: 85 FC      sta  $FC
    $C054: BD 02 A0   lda  $A002,X      ; length lo (page count)
    $C057: 85 F7      sta  $F7
    $C059: BD 03 A0   lda  $A003,X      ; length hi
    $C05C: 85 F8      sta  $F8
    $C05E: A9 FF      lda  #$FF
    $C060: 8D 02 D4   sta  $D402        ; V1 PW lo = $FF
    $C063: 8D 03 D4   sta  $D403        ; V1 PW hi = $FF (50% duty)
    $C066: 8D 04 DD   sta  $DD04        ; CIA2 Timer A lo = $FF
    $C069: 8D 05 DD   sta  $DD05        ; CIA2 Timer A hi = $FF
    $C06C: A0 00      ldy  #$00
    $C06E: A9 F0      lda  #$F0
    $C070: 8D 06 D4   sta  $D406        ; V1 SR = $F0 (long release)
    $C073: AD 08 A1   lda  $A108        ; "keep screen on" flag
    $C076: D0 05      bne  $C07D      ; → L_C07D   ; nonzero → keep VIC
    $C078: A9 00      lda  #$00
    $C07A: 8D 11 D0   sta  $D011        ; else blank VIC (no badlines)
L_C07D:
    $C07D: A9 11      lda  #$11
    $C07F: 8D 0E DD   sta  $DD0E        ; CIA2 Timer A: start, force-load
    $C082: EA         nop               ; six NOPs = ~12 cycles of pad
    $C083: EA         nop               ; to let CIA pick up the load
    $C084: EA         nop
    $C085: EA         nop
    $C086: EA         nop
    $C087: EA         nop
    $C088: 4C CF C0   jmp  $C0CF      ; → L_C0CF   ; into sample-byte loop
; Advance source pointer ($FB/$FC) by 1, check against length ($F7/$F8).
; When source pointer >= length pointer, exit to cleanup at $C0EA.
L_C08B:
    $C08B: E6 FB      inc  $FB
    $C08D: D0 02      bne  $C091      ; → L_C091
    $C08F: E6 FC      inc  $FC
L_C091:
    $C091: A6 FC      ldx  $FC
    $C093: E4 F8      cpx  $F8          ; src_hi vs len_hi
    $C095: 90 09      bcc  $C0A0      ; → L_C0A0   ; src < len → keep playing
    $C097: A6 FB      ldx  $FB
    $C099: E4 F7      cpx  $F7
    $C09B: 90 03      bcc  $C0A0      ; → L_C0A0
    $C09D: 4C EA C0   jmp  $C0EA      ; → L_C0EA   ; sample done
; ======= 1-bit-per-output-cycle sample emission =======
; Per source byte, shift out 8 bits MSB-first. Each bit picks pulse+gate
; ($41) for 0 or tri+gate ($49) for 1, toggling V1 waveform at the timer
; rate. Timing is paced by waiting until CIA2 Timer A latch (DD04) drops
; below $B0, then re-arming. $C0AC is self-modified at $C042 with the
; bank's pacing constant.
L_C0A0:
    $C0A0: A9 08      lda  #$08
    $C0A2: 85 96      sta  $96          ; 8 bits per byte
    $C0A4: B1 FB      lda  ($FB),Y      ; A = next sample byte
    $C0A6: 85 FE      sta  $FE          ; shift register
L_C0A8:
    $C0A8: AD 04 DD   lda  $DD04        ; CIA2 Timer A current value
    $C0AB: C9 B0      cmp  #$B0         ; compare (← self-modified at $C042)
    $C0AD: B0 F9      bcs  $C0A8      ; → L_C0A8   ; wait for timer < cmp
    $C0AF: A9 11      lda  #$11
    $C0B1: 8D 0E DD   sta  $DD0E        ; restart timer (one-shot)
    $C0B4: 06 FE      asl  $FE          ; shift next bit into C
    $C0B6: 90 04      bcc  $C0BC      ; → L_C0BC   ; bit = 0 → pulse
    $C0B8: A9 49      lda  #$49         ; bit = 1 → tri+gate
    $C0BA: D0 02      bne  $C0BE      ; → L_C0BE
L_C0BC:
    $C0BC: A9 41      lda  #$41         ; bit = 0 → pulse+gate
L_C0BE:
    $C0BE: 8D 04 D4   sta  $D404        ; V1 ctrl (waveform select)
    $C0C1: C6 96      dec  $96
    $C0C3: D0 E3      bne  $C0A8      ; → L_C0A8   ; next bit of this byte
    $C0C5: C6 F9      dec  $F9          ; rate counter ($F9 set by $C0E3)
    $C0C7: D0 C2      bne  $C08B      ; → L_C08B   ; same byte again
    $C0C9: E6 FB      inc  $FB          ; advance source pointer
    $C0CB: D0 02      bne  $C0CF      ; → L_C0CF
    $C0CD: E6 FC      inc  $FC
; Volume sweep: pull the high nibble of the current byte (cap at $0F),
; subtract the running vol bias $FD (set up by the SFX init at $9FEF=0),
; clamp to $01 minimum, write to $D418 master vol. Then reload rate
; counter $F9 = $10 and loop back to read the next sample byte.
L_C0CF:
    $C0CF: B1 FB      lda  ($FB),Y
    $C0D1: C9 10      cmp  #$10
    $C0D3: 90 02      bcc  $C0D7      ; → L_C0D7
    $C0D5: A9 0F      lda  #$0F         ; cap at $0F
L_C0D7:
    $C0D7: 38         sec
    $C0D8: E5 FD      sbc  $FD          ; subtract bias
    $C0DA: 30 02      bmi  $C0DE      ; → L_C0DE
    $C0DC: D0 02      bne  $C0E0      ; → L_C0E0
L_C0DE:
    $C0DE: A9 01      lda  #$01         ; clamp to $01 (avoid total mute)
L_C0E0:
    $C0E0: 8D 18 D4   sta  $D418        ; SID master vol
    $C0E3: A9 10      lda  #$10
    $C0E5: 85 F9      sta  $F9          ; reload bit-rate counter
    $C0E7: 4C 8B C0   jmp  $C08B      ; → L_C08B
; ======= digi player cleanup + exit =======
; Mute, restore VIC ctrl (in case we blanked the screen), restore BASIC
; bank-in (set bits 0+1 of $01), pop zero-page scratch, re-enable IRQ,
; RTS back to the SFX dispatcher.
L_C0EA:
    $C0EA: A9 00      lda  #$00
    $C0EC: 8D 18 D4   sta  $D418        ; vol = 0 (silence)
    $C0EF: AD 30 C1   lda  $C130        ; cached $D011 from $C01C
    $C0F2: 8D 11 D0   sta  $D011        ; restore VIC ctrl (un-blank)
    $C0F5: A9 03      lda  #$03
    $C0F7: 05 01      ora  $01          ; banking: re-enable BASIC + KERNAL
    $C0F9: 85 01      sta  $01
    $C0FB: 68         pla
    $C0FC: 85 FA      sta  $FA          ; ...pop scratch zp
    $C0FE: 68         pla
    $C0FF: 85 F9      sta  $F9
    $C101: 68         pla
    $C102: 85 F8      sta  $F8
    $C104: 68         pla
    $C105: 85 F7      sta  $F7
    $C107: 58         cli
    $C108: 60         rts
; ======= "ping" sub-routine =======
; Plays a brief V2-triangle envelope used as the SFX fallback when the
; sample-table is empty or the requested bank isn't found. V2 freq = $2A
; (lo), SR = $F0, vol = $F, ctrl = $11 (triangle+gate). Then a busy-wait
; (~$FFFF*$FF cycles), then gate-off and mute.
L_C109:
    $C109: A9 2A      lda  #$2A
    $C10B: 8D 08 D4   sta  $D408        ; V2 freq lo
    $C10E: A9 F0      lda  #$F0
    $C110: 8D 0D D4   sta  $D40D        ; V2 SR = $F0
    $C113: A9 0F      lda  #$0F
    $C115: 8D 18 D4   sta  $D418        ; vol = $F
    $C118: A9 11      lda  #$11
    $C11A: 8D 0B D4   sta  $D40B        ; V2 ctrl = triangle+gate
    $C11D: A0 FF      ldy  #$FF
L_C11F:
    $C11F: A2 FF      ldx  #$FF
L_C121:
    $C121: CA         dex
    $C122: D0 FD      bne  $C121      ; → L_C121   ; inner delay
    $C124: 88         dey
    $C125: D0 F8      bne  $C11F      ; → L_C11F   ; outer delay
    $C127: A9 00      lda  #$00
    $C129: 8D 0B D4   sta  $D40B        ; V2 ctrl = 0 (release)
    $C12C: 8D 18 D4   sta  $D418        ; vol = 0
    $C12F: 60         rts
; ----- data gap $C130-$C200 (208 bytes) -----

; ======= music engine vectors =======
; Stable entry points the wrapper at $9F9A / $9FA3 calls into. Internal
; code never jumps directly to $CF63/$CF94 — always through these.
L_C200:
    $C200: 4C 63 CF   jmp  $CF63      ; → L_CF63   ; init
L_C203:
    $C203: 4C 94 CF   jmp  $CF94      ; → L_CF94   ; stop (state = $C0)

; ======= play frame entry (called from IRQ at $9FA3) =======
; Tick frame counter, dispatch on state byte $C655, then drop into the
; per-voice loop at $C241.
L_C206:
    $C206: EE 61 C6   inc  $C661        ; global frame counter ++
    $C209: 2C 55 C6   bit  $C655        ; N <- bit7, V <- bit6
    $C20C: 30 1E      bmi  $C22C      ; → L_C22C   ; end-of-song path
    $C20E: 50 31      bvc  $C241      ; → L_C241   ; normal play

; First-frame setup: state had bit 6 set (CF63 wrote $40 here at init).
; Zero per-voice state arrays for X=0..2, clear state byte, drop into
; per-voice loop.
    $C210: A9 00      lda  #$00
    $C212: 8D 61 C6   sta  $C661        ; reset frame counter
    $C215: A2 02      ldx  #$02         ; X = V3 .. V1
L_C217:
    $C217: 9D 2B C6   sta  $C62B,X      ; pattern column = 0
    $C21A: 9D 2E C6   sta  $C62E,X      ; pattern byte idx = 0
    $C21D: 9D 31 C6   sta  $C631,X      ; duration counter = 0
    $C220: 9D 3A C6   sta  $C63A,X      ; note num = 0
    $C223: CA         dex
    $C224: 10 F1      bpl  $C217      ; → L_C217
    $C226: 8D 55 C6   sta  $C655        ; clear state byte (no more first-frame)
    $C229: 4C 41 C2   jmp  $C241      ; → L_C241
; ======= end-of-song path =======
; State had bit 7 set. If bit 6 ALSO set (just-stopped via $C203 = $C0),
; zero all three voice ctrl regs once and clear bit 6 (state = $80) so
; subsequent frames silently fall through. If bit 6 already clear, skip
; the silencing and just jump to the RTS at $C566.
L_C22C:
    $C22C: 50 10      bvc  $C23E      ; → L_C23E   ; not first-frame-of-end
    $C22E: A9 00      lda  #$00
    $C230: 8D 04 D4   sta  $D404        ; V1 ctrl = 0
    $C233: 8D 0B D4   sta  $D40B        ; V2 ctrl = 0
    $C236: 8D 12 D4   sta  $D412        ; V3 ctrl = 0
    $C239: A9 80      lda  #$80
    $C23B: 8D 55 C6   sta  $C655        ; state = $80 (end-of-song, no first-frame)
L_C23E:
    $C23E: 4C 66 C5   jmp  $C566      ; → L_C566   ; RTS
; ======= per-voice loop =======
; X iterates 2..0 (V3, V2, V1). Tick the sub-frame divider $C652 once at
; the top, then loop body per voice.
L_C241:
    $C241: A2 02      ldx  #$02         ; start with V3
    $C243: CE 52 C6   dec  $C652        ; sub-frame tick--
    $C246: 10 06      bpl  $C24E      ; → L_C24E   ; not yet expired
    $C248: AD 53 C6   lda  $C653        ; expired → reload from $C653
    $C24B: 8D 52 C6   sta  $C652

; Voice loop body. $C627,X holds the SID base offset for this voice
; ($00 for V1, $07 for V2, $0E for V3). Latched into $C62A so the rest
; of the per-voice code can write D400+Y for any reg.
L_C24E:
    $C24E: BD 27 C6   lda  $C627,X      ; SID base offset for voice X
    $C251: 8D 2A C6   sta  $C62A
    $C254: A8         tay               ; Y = SID base for D400+Y writes
; Note-load gate: only when sub-frame divider just rolled over.
    $C255: AD 52 C6   lda  $C652
    $C258: CD 53 C6   cmp  $C653        ; tick == reload?
    $C25B: D0 15      bne  $C272      ; → L_C272   ; no → effects-only frame
; Note-load path: read this voice's orderlist pointer into ($56),
; then decrement the duration counter; when it underflows, advance
; to the next pattern step at $C275. Otherwise sustain (apply HR
; sustain logic at $C356).
    $C25D: BD FA C6   lda  $C6FA,X      ; orderlist ptr lo[voice]
    $C260: 85 56      sta  $56
    $C262: BD FD C6   lda  $C6FD,X      ; orderlist ptr hi[voice]
    $C265: 85 57      sta  $57
    $C267: DE 31 C6   dec  $C631,X      ; duration counter--
    $C26A: 30 09      bmi  $C275      ; → L_C275   ; underflow → new step
    $C26C: 4C 56 C3   jmp  $C356      ; → L_C356   ; sustain
; ----- data gap $C26F-$C272 (3 bytes) -----

; Effects-only frame: no new note this tick, jump to the effects loop.
L_C272:
    $C272: 4C 75 C3   jmp  $C375      ; → L_C375

; ======= advance to next pattern step =======
; Read the next orderlist byte. $FE = song end (set state = $C0 via
; $C203); $FF = end of pattern, reset per-voice counters and retry
; from the start of the orderlist; else byte is a pattern index.
L_C275:
    $C275: BC 2B C6   ldy  $C62B,X      ; Y = column index in orderlist
    $C278: B1 56      lda  ($56),Y      ; A = orderlist byte
    $C27A: C9 FE      cmp  #$FE
    $C27C: D0 03      bne  $C281      ; → L_C281
    $C27E: 4C 03 C2   jmp  $C203      ; → L_C203   ; $FE = song end
L_C281:
    $C281: C9 FF      cmp  #$FF
    $C283: D0 11      bne  $C296      ; → L_C296
    $C285: A9 00      lda  #$00         ; $FF = orderlist wrap
    $C287: 9D 31 C6   sta  $C631,X      ; reset duration counter
    $C28A: 9D 2B C6   sta  $C62B,X      ; reset column index
    $C28D: 9D 2E C6   sta  $C62E,X      ; reset pattern byte index
    $C290: 4C 75 C2   jmp  $C275      ; → L_C275   ; retry (read from start)
; ----- data gap $C293-$C296 (3 bytes) -----

; ======= load a pattern step + first byte =======
; Orderlist byte is a pattern index. Look it up in the pattern pointer
; tables ($C70C lo, $C73D hi) and stash in ($58). Then read the first
; pattern-row byte and decode it:
;   * Pattern row format (3-byte): {flag, instr_or_pslide, note}.
;     flag bits: 7=new-instr-byte follows, 6=tie (skip note-load),
;     bit 7 of byte 2 set = pitch slide (stored in $C65C,X),
;     bit 7 of byte 2 clear = instrument index (stored in $C63D,X).
;   * Low 5 bits of flag = duration ticks. Stored in $C631,X for the
;     duration counter and also kept verbatim in $C634,X for later
;     comparison in fx blocks.
L_C296:
    $C296: A8         tay               ; Y = pattern index
    $C297: B9 0C C7   lda  $C70C,Y      ; pattern ptr lo[idx]
    $C29A: 85 58      sta  $58
    $C29C: B9 3D C7   lda  $C73D,Y      ; pattern ptr hi[idx]
    $C29F: 85 59      sta  $59
    $C2A1: A9 00      lda  #$00
    $C2A3: 9D 5C C6   sta  $C65C,X      ; clear pitch slide for this voice
    $C2A6: BC 2E C6   ldy  $C62E,X      ; Y = byte index within pattern
    $C2A9: A9 FF      lda  #$FF
    $C2AB: 8D 40 C6   sta  $C640        ; ctrl mask default = $FF (no tie)
    $C2AE: B1 58      lda  ($58),Y      ; A = flag byte
    $C2B0: 9D 34 C6   sta  $C634,X      ; cache full flag for fx blocks
    $C2B3: 8D 41 C6   sta  $C641        ; scratch copy for bit tests
    $C2B6: 29 1F      and  #$1F
    $C2B8: 9D 31 C6   sta  $C631,X      ; duration counter = flag & $1F
    $C2BB: 2C 41 C6   bit  $C641
    $C2BE: 70 3F      bvs  $C2FF      ; → L_C2FF   ; bit 6 = tie → skip note
    $C2C0: FE 2E C6   inc  $C62E,X      ; advance past flag byte
    $C2C3: AD 41 C6   lda  $C641
    $C2C6: 10 11      bpl  $C2D9      ; → L_C2D9   ; bit 7 clear → no inst byte
    $C2C8: C8         iny               ; have instr/slide byte
    $C2C9: B1 58      lda  ($58),Y
    $C2CB: 10 06      bpl  $C2D3      ; → L_C2D3   ; bit 7 clear → instrument
    $C2CD: 9D 5C C6   sta  $C65C,X      ; bit 7 set → pitch slide byte
    $C2D0: 4C D6 C2   jmp  $C2D6      ; → L_C2D6
L_C2D3:
    $C2D3: 9D 3D C6   sta  $C63D,X      ; instrument index
L_C2D6:
    $C2D6: FE 2E C6   inc  $C62E,X      ; advance past inst/slide byte
L_C2D9:
; Read note number, look up freq via $C567+note*2 (lo, hi) and write
; both bytes to D400/D401, cache as v_fhi/v_flo at $C656,X / $C659,X.
    $C2D9: C8         iny
    $C2DA: B1 58      lda  ($58),Y      ; A = note number
    $C2DC: 9D 3A C6   sta  $C63A,X      ; cache note num for fx blocks
    $C2DF: 0A         asl  A            ; *2 for 16-bit stride
    $C2E0: A8         tay
    $C2E1: B9 67 C5   lda  $C567,Y      ; freq_lo
    $C2E4: 8D 42 C6   sta  $C642
    $C2E7: B9 68 C5   lda  $C568,Y      ; freq_hi
    $C2EA: AC 2A C6   ldy  $C62A        ; Y = SID base
    $C2ED: 99 01 D4   sta  $D401,Y      ; SID freq hi
    $C2F0: 9D 56 C6   sta  $C656,X      ; v_fhi cache
    $C2F3: AD 42 C6   lda  $C642
    $C2F6: 99 00 D4   sta  $D400,Y      ; SID freq lo
    $C2F9: 9D 59 C6   sta  $C659,X      ; v_flo cache
    $C2FC: 4C 02 C3   jmp  $C302      ; → L_C302
; Tie path: clear bit 0 of $C640 (so the ctrl write below clears gate).
L_C2FF:
    $C2FF: CE 40 C6   dec  $C640        ; $C640: $FF → $FE (gate-off mask)

; ======= apply instrument to SID =======
; X = inst*8 (after the three ASLs). Write ctrl/pulse/AD/SR from the
; instrument record at $C662..$C666 + X. Y = SID base.
L_C302:
    $C302: AC 2A C6   ldy  $C62A        ; Y = SID base for D40x,Y writes
    $C305: BD 3D C6   lda  $C63D,X      ; A = inst index (X is voice here)
    $C308: 8E 43 C6   stx  $C643        ; save voice X for restore at $C336
    $C30B: 0A         asl  A
    $C30C: 0A         asl  A
    $C30D: 0A         asl  A            ; A = inst * 8
    $C30E: AA         tax               ; X = inst*8 (for inst-table indexing)
    $C30F: BD 64 C6   lda  $C664,X      ; ctrl
    $C312: 8D 44 C6   sta  $C644        ; cache for v_ctrl save below
    $C315: BD 64 C6   lda  $C664,X      ; ctrl again
    $C318: 2D 40 C6   and  $C640        ; & ctrl-mask ($FF or $FE for tie)
    $C31B: 99 04 D4   sta  $D404,Y      ; → SID ctrl
    $C31E: BD 62 C6   lda  $C662,X      ; pulse lo
    $C321: 99 02 D4   sta  $D402,Y      ; → SID pulse lo
    $C324: BD 63 C6   lda  $C663,X      ; pulse hi
    $C327: 99 03 D4   sta  $D403,Y      ; → SID pulse hi
    $C32A: BD 65 C6   lda  $C665,X      ; AD
    $C32D: 99 05 D4   sta  $D405,Y      ; → SID AD
    $C330: BD 66 C6   lda  $C666,X      ; SR
    $C333: 99 06 D4   sta  $D406,Y      ; → SID SR
    $C336: AE 43 C6   ldx  $C643        ; restore voice X
    $C339: AD 44 C6   lda  $C644        ; cached ctrl
    $C33C: 9D 37 C6   sta  $C637,X      ; v_ctrl[voice] (used by drum bit 0)
    $C33F: FE 2E C6   inc  $C62E,X      ; advance past note byte

; Peek at next pattern byte. $FF = end-of-pattern: reset byte index
; and advance to the next orderlist column.
    $C342: BC 2E C6   ldy  $C62E,X
    $C345: B1 58      lda  ($58),Y
    $C347: C9 FF      cmp  #$FF
    $C349: D0 08      bne  $C353      ; → L_C353
    $C34B: A9 00      lda  #$00
    $C34D: 9D 2E C6   sta  $C62E,X
    $C350: FE 2B C6   inc  $C62B,X      ; column index ++
L_C353:
    $C353: 4C 60 C5   jmp  $C560      ; → L_C560   ; tail: next voice / exit
; ======= HR sustain / gate-off path =======
; Reached on duration-decrement frames (not new-note). If the flag byte's
; bit 5 ($20 = "no release") is clear AND the duration counter just hit 0,
; clear gate (ctrl & $FE), zero AD and SR — kills the note cleanly.
; Otherwise fall through to the effects loop at $C375 with the note
; still playing.
L_C356:
    $C356: AC 2A C6   ldy  $C62A        ; Y = SID base
    $C359: BD 34 C6   lda  $C634,X      ; pattern flag byte
    $C35C: 29 20      and  #$20         ; bit 5 = "no release" / sustain
    $C35E: D0 15      bne  $C375      ; → L_C375   ; sustain → keep playing
    $C360: BD 31 C6   lda  $C631,X      ; duration counter
    $C363: D0 10      bne  $C375      ; → L_C375   ; not zero yet
    $C365: BD 37 C6   lda  $C637,X      ; current ctrl
    $C368: 29 FE      and  #$FE         ; clear gate
    $C36A: 99 04 D4   sta  $D404,Y      ; → SID ctrl
    $C36D: A9 00      lda  #$00
    $C36F: 99 05 D4   sta  $D405,Y      ; AD = 0
    $C372: 99 06 D4   sta  $D406,Y      ; SR = 0
; ======= effects loop entry =======
; Latch this voice's instrument table values:
;   $C65F = fx_flags ($C669+inst*8)
;   $C646 = PW init data ($C668+inst*8)
;   $C645 = vibrato depth ($C667+inst*8)
; If vibrato depth == 0, skip vibrato calculation entirely.
L_C375:
    $C375: BD 3D C6   lda  $C63D,X      ; A = inst index
    $C378: 0A         asl  A
    $C379: 0A         asl  A
    $C37A: 0A         asl  A            ; A = inst * 8
    $C37B: A8         tay
    $C37C: 8C 54 C6   sty  $C654        ; save inst*8 (used by PW kick at $C409)
    $C37F: B9 69 C6   lda  $C669,Y      ; fx_flags
    $C382: 8D 5F C6   sta  $C65F
    $C385: B9 68 C6   lda  $C668,Y      ; PW init data
    $C388: 8D 46 C6   sta  $C646
    $C38B: B9 67 C6   lda  $C667,Y      ; vibrato depth
    $C38E: 8D 45 C6   sta  $C645
    $C391: F0 6F      beq  $C402      ; → L_C402   ; depth=0 → skip vibrato

; Vibrato: triangle LFO over the global frame counter folded to 0..3
; via (frame & 7) ^ 7 if >= 4. Result in $C64B determines how many
; ADC iterations to apply per frame.
    $C393: AD 61 C6   lda  $C661        ; frame counter
    $C396: 29 07      and  #$07
    $C398: C9 04      cmp  #$04
    $C39A: 90 02      bcc  $C39E      ; → L_C39E   ; 0..3 → use as-is
    $C39C: 49 07      eor  #$07         ; 4..7 → fold to 3..0
L_C39E:
    $C39E: 8D 4B C6   sta  $C64B        ; vib phase 0..3

; Compute freq delta for vibrato: (freq[note+1] - freq[note]) / 2^depth.
; Stored in $C647/$C648 (signed 16-bit).
    $C3A1: BD 3A C6   lda  $C63A,X      ; current note
    $C3A4: 0A         asl  A            ; *2 stride
    $C3A5: A8         tay
    $C3A6: 38         sec
    $C3A7: B9 69 C5   lda  $C569,Y      ; freq[note+1] lo
    $C3AA: F9 67 C5   sbc  $C567,Y      ; - freq[note] lo
    $C3AD: 8D 47 C6   sta  $C647
    $C3B0: B9 6A C5   lda  $C56A,Y      ; freq[note+1] hi
    $C3B3: F9 68 C5   sbc  $C568,Y      ; - freq[note] hi (with borrow)
; Shift the delta right ($C645) times (= depth) by LSR/ROR pair.
L_C3B6:
    $C3B6: 4A         lsr  A            ; hi LSR
    $C3B7: 6E 47 C6   ror  $C647        ; lo ROR (with C from hi)
    $C3BA: CE 45 C6   dec  $C645
    $C3BD: 10 F7      bpl  $C3B6      ; → L_C3B6
    $C3BF: 8D 48 C6   sta  $C648        ; delta hi (final)
; Reload base freq for accumulation.
    $C3C2: B9 67 C5   lda  $C567,Y      ; freq[note] lo
    $C3C5: 8D 49 C6   sta  $C649
    $C3C8: B9 68 C5   lda  $C568,Y      ; freq[note] hi
    $C3CB: 8D 4A C6   sta  $C64A
; Only apply vibrato when duration field >= $08 (i.e. long enough note).
    $C3CE: BD 34 C6   lda  $C634,X
    $C3D1: 29 1F      and  #$1F
    $C3D3: C9 08      cmp  #$08
    $C3D5: 90 1C      bcc  $C3F3      ; → L_C3F3   ; short note → skip
    $C3D7: AC 4B C6   ldy  $C64B        ; Y = vibrato phase 0..3
L_C3DA:
; Add delta to current freq `vib_phase` times.
    $C3DA: 88         dey
    $C3DB: 30 16      bmi  $C3F3      ; → L_C3F3
    $C3DD: 18         clc
    $C3DE: AD 49 C6   lda  $C649
    $C3E1: 6D 47 C6   adc  $C647
    $C3E4: 8D 49 C6   sta  $C649
    $C3E7: AD 4A C6   lda  $C64A
    $C3EA: 6D 48 C6   adc  $C648
    $C3ED: 8D 4A C6   sta  $C64A
    $C3F0: 4C DA C3   jmp  $C3DA      ; → L_C3DA
L_C3F3:
; Write vibrato-modulated freq to SID.
    $C3F3: AC 2A C6   ldy  $C62A
    $C3F6: AD 49 C6   lda  $C649
    $C3F9: 99 00 D4   sta  $D400,Y      ; freq lo
    $C3FC: AD 4A C6   lda  $C64A
    $C3FF: 99 01 D4   sta  $D401,Y      ; freq hi
; ======= fx bit 3 ($08): linear-PW kick =======
; When enabled: ADC instrument's pulse_lo + $C646 (PW init), ORA $40
; forces pulse_hi bit 6 on, store back to instrument table AND write
; to D402. This is the "linear PW" mode mentioned in Codegen.lean
; (pw_linear path) — it intentionally leaks C from vibrato's last ADC
; to produce the +1 quirk Hubbard ships with. Skips the bidir PW
; block at $C420 via JMP $C487.
L_C402:
    $C402: AD 5F C6   lda  $C65F
    $C405: 29 08      and  #$08         ; bit 3 of fx_flags
    $C407: F0 17      beq  $C420      ; → L_C420   ; bit clear → bidir PW
    $C409: AC 54 C6   ldy  $C654        ; Y = inst*8
    $C40C: B9 62 C6   lda  $C662,Y      ; instr pulse_lo
    $C40F: 6D 46 C6   adc  $C646        ; + PW init (C from prev op intentional)
    $C412: 09 40      ora  #$40         ; force pulse_hi bit 6 on
    $C414: 99 62 C6   sta  $C662,Y      ; write back (mutates instrument record!)
    $C417: AC 2A C6   ldy  $C62A
    $C41A: 99 02 D4   sta  $D402,Y      ; → SID pulse lo
    $C41D: 4C 87 C4   jmp  $C487      ; → L_C487
; ======= bidirectional PWM =======
; Active when $C646 (PW init / step encoding) != 0. PW step encoded
; in $C646 as: low 5 bits = period reload, high 3 bits = step size.
; Sub-counter $C64C,X paces the step; $C64F,X = direction (0=up, 1=down).
; pulse_hi is clamped to 4 bits ($0F mask) — direction flips at $0E (up)
; or $08 (down). These bounds are HARDCODED in Hubbard's engine — see
; reference_hubbard_pwm_bounds.md.
L_C420:
    $C420: AD 46 C6   lda  $C646
    $C423: F0 62      beq  $C487      ; → L_C487   ; PW data = 0 → no PWM
    $C425: AC 54 C6   ldy  $C654        ; Y = inst*8
    $C428: 29 1F      and  #$1F         ; A = period (low 5 bits)
    $C42A: DE 4C C6   dec  $C64C,X      ; sub-counter--
    $C42D: 10 58      bpl  $C487      ; → L_C487   ; not yet rolled over
    $C42F: 9D 4C C6   sta  $C64C,X      ; reload sub-counter
    $C432: AD 46 C6   lda  $C646
    $C435: 29 E0      and  #$E0         ; step size (high 3 bits)
    $C437: 8D 60 C6   sta  $C660
    $C43A: BD 4F C6   lda  $C64F,X
    $C43D: D0 1A      bne  $C459      ; → L_C459   ; dir != 0 → down
; UP path: instr.pulse_lo += step, pulse_hi += carry, mask hi to $0F.
    $C43F: AD 60 C6   lda  $C660
    $C442: 18         clc
    $C443: 79 62 C6   adc  $C662,Y      ; pulse_lo += step
    $C446: 48         pha
    $C447: B9 63 C6   lda  $C663,Y
    $C44A: 69 00      adc  #$00         ; pulse_hi += carry
    $C44C: 29 0F      and  #$0F         ; clamp to 4 bits
    $C44E: 48         pha
    $C44F: C9 0E      cmp  #$0E         ; reached upper bound?
    $C451: D0 1D      bne  $C470      ; → L_C470
    $C453: FE 4F C6   inc  $C64F,X      ; flip direction → down
    $C456: 4C 70 C4   jmp  $C470      ; → L_C470
L_C459:
; DOWN path: instr.pulse_lo -= step, pulse_hi -= borrow, mask hi to $0F.
    $C459: 38         sec
    $C45A: B9 62 C6   lda  $C662,Y
    $C45D: ED 60 C6   sbc  $C660
    $C460: 48         pha
    $C461: B9 63 C6   lda  $C663,Y
    $C464: E9 00      sbc  #$00
    $C466: 29 0F      and  #$0F
    $C468: 48         pha
    $C469: C9 08      cmp  #$08         ; reached lower bound?
    $C46B: D0 03      bne  $C470      ; → L_C470
    $C46D: DE 4F C6   dec  $C64F,X      ; flip direction → up
L_C470:
; Pop pulse hi/lo back, write to instrument record AND to SID.
    $C470: 8E 43 C6   stx  $C643        ; save voice X
    $C473: AE 2A C6   ldx  $C62A        ; X = SID base
    $C476: 68         pla               ; A = pulse_hi
    $C477: 99 63 C6   sta  $C663,Y      ; → instr pulse_hi
    $C47A: 9D 03 D4   sta  $D403,X      ; → SID pulse hi
    $C47D: 68         pla               ; A = pulse_lo
    $C47E: 99 62 C6   sta  $C662,Y      ; → instr pulse_lo
    $C481: 9D 02 D4   sta  $D402,X      ; → SID pulse lo
    $C484: AE 43 C6   ldx  $C643        ; restore voice X
; ======= per-voice pitch slide ($C65C,X != 0) =======
; $C65C,X carries the slide step (from pattern byte). Low bit = direction
; (1=down, 0=up); high 7 bits & $7E = magnitude. Each frame, add/subtract
; magnitude to v_fhi:v_flo, write to SID.
L_C487:
    $C487: AC 2A C6   ldy  $C62A        ; Y = SID base
    $C48A: BD 5C C6   lda  $C65C,X      ; pitch slide byte
    $C48D: F0 3F      beq  $C4CE      ; → L_C4CE   ; 0 → no slide
    $C48F: 29 7E      and  #$7E         ; mag = byte & $7E
    $C491: 8D 43 C6   sta  $C643
    $C494: BD 5C C6   lda  $C65C,X
    $C497: 29 01      and  #$01         ; direction bit
    $C499: F0 1B      beq  $C4B6      ; → L_C4B6   ; 0 → up (ADC)
; Down (SBC) path.
    $C49B: 38         sec
    $C49C: BD 59 C6   lda  $C659,X
    $C49F: ED 43 C6   sbc  $C643
    $C4A2: 9D 59 C6   sta  $C659,X      ; v_flo -= mag
    $C4A5: 99 00 D4   sta  $D400,Y
    $C4A8: BD 56 C6   lda  $C656,X
    $C4AB: E9 00      sbc  #$00         ; v_fhi -= borrow
    $C4AD: 9D 56 C6   sta  $C656,X
    $C4B0: 99 01 D4   sta  $D401,Y
    $C4B3: 4C CE C4   jmp  $C4CE      ; → L_C4CE
L_C4B6:
; Up (ADC) path.
    $C4B6: 18         clc
    $C4B7: BD 59 C6   lda  $C659,X
    $C4BA: 6D 43 C6   adc  $C643
    $C4BD: 9D 59 C6   sta  $C659,X
    $C4C0: 99 00 D4   sta  $D400,Y
    $C4C3: BD 56 C6   lda  $C656,X
    $C4C6: 69 00      adc  #$00
    $C4C8: 9D 56 C6   sta  $C656,X
    $C4CB: 99 01 D4   sta  $D401,Y
; ======= fx bit 0 ($01): freq-slide / drums =======
; Guards: v_fhi != 0, duration counter != 0. Compare (dur_max - 1) vs
; current dur counter:
;   * dur_max-1 < counter (i.e. note just started, counter == dur_max):
;     write current v_fhi, ctrl = $80 (noise+test) — Hubbard's drum
;     onset.
;   * dur_max-1 >= counter (note progressing): DEC v_fhi in memory,
;     write OLD value, ctrl with gate cleared — drum decay tail.
L_C4CE:
    $C4CE: AD 5F C6   lda  $C65F
    $C4D1: 29 01      and  #$01         ; bit 0
    $C4D3: F0 35      beq  $C50A      ; → L_C50A
    $C4D5: BD 56 C6   lda  $C656,X      ; v_fhi
    $C4D8: F0 30      beq  $C50A      ; → L_C50A   ; v_fhi=0 → skip
    $C4DA: BD 31 C6   lda  $C631,X
    $C4DD: F0 2B      beq  $C50A      ; → L_C50A   ; dur counter=0 → skip
    $C4DF: BD 34 C6   lda  $C634,X      ; pattern flag
    $C4E2: 29 1F      and  #$1F         ; A = dur max
    $C4E4: 38         sec
    $C4E5: E9 01      sbc  #$01         ; A = dur max - 1
    $C4E7: DD 31 C6   cmp  $C631,X      ; cmp current dur counter
    $C4EA: AC 2A C6   ldy  $C62A
    $C4ED: 90 10      bcc  $C4FF      ; → L_C4FF   ; max-1 < cur → note onset
; Decay path: DEC v_fhi in memory, write OLD value to SID, ctrl with
; gate cleared (= release current envelope).
    $C4EF: BD 56 C6   lda  $C656,X
    $C4F2: DE 56 C6   dec  $C656,X      ; v_fhi--
    $C4F5: 99 01 D4   sta  $D401,Y      ; write OLD v_fhi to SID
    $C4F8: BD 37 C6   lda  $C637,X      ; cached ctrl
    $C4FB: 29 FE      and  #$FE         ; clear gate
    $C4FD: D0 08      bne  $C507      ; → L_C507   ; (almost always taken)
L_C4FF:
; Onset path: write current v_fhi, ctrl = $80 (noise+test, silences osc
; momentarily so the next sample is a fresh edge).
    $C4FF: BD 56 C6   lda  $C656,X
    $C502: 99 01 D4   sta  $D401,Y
    $C505: A9 80      lda  #$80
L_C507:
    $C507: 99 04 D4   sta  $D404,Y      ; → SID ctrl
; ======= fx bit 1 ($02): freq_hi slow climb (skydive-up variant) =======
; Guards: duration field >= $11 (long note), frame counter odd, v_fhi != 0.
; INC v_fhi in memory, write to SID freq_hi. Codegen.lean models this as
; DEC ("skydive" going DOWN) — but this disassembly clearly does INC.
; Worth re-checking against siddump --writelog (may explain the 1.2%
; siddump gap noted in pipelines/chimera/README.md).
L_C50A:
    $C50A: AD 5F C6   lda  $C65F
    $C50D: 29 02      and  #$02
    $C50F: F0 1E      beq  $C52F      ; → L_C52F
    $C511: BD 34 C6   lda  $C634,X      ; pattern flag
    $C514: 29 1F      and  #$1F         ; dur max
    $C516: C9 11      cmp  #$11
    $C518: 90 15      bcc  $C52F      ; → L_C52F   ; dur < 17 → skip
    $C51A: AD 61 C6   lda  $C661
    $C51D: 29 01      and  #$01
    $C51F: F0 0E      beq  $C52F      ; → L_C52F   ; even frame → skip
    $C521: BD 56 C6   lda  $C656,X
    $C524: F0 09      beq  $C52F      ; → L_C52F   ; v_fhi=0 → skip
    $C526: FE 56 C6   inc  $C656,X      ; INC v_fhi (NOT DEC — see note above)
    $C529: AC 2A C6   ldy  $C62A
    $C52C: 99 01 D4   sta  $D401,Y      ; → SID freq hi
; ======= fx bit 2 ($04): octave-up arpeggio =======
; Every 7-of-8 frames (frame & 7 != 0), use note + $0C (one octave up);
; on the 1-of-8 frame (frame & 7 == 0), use base note. Look up freq via
; the standard $C567 table and write to D400/D401.
L_C52F:
    $C52F: AD 5F C6   lda  $C65F
    $C532: 29 04      and  #$04
    $C534: F0 2A      beq  $C560      ; → L_C560
    $C536: AD 61 C6   lda  $C661
    $C539: 29 07      and  #$07
    $C53B: F0 09      beq  $C546      ; → L_C546   ; phase 0 → base note
    $C53D: BD 3A C6   lda  $C63A,X
    $C540: 18         clc
    $C541: 69 0C      adc  #$0C         ; phase 1..7 → +12 semitones
    $C543: 4C 49 C5   jmp  $C549      ; → L_C549
L_C546:
    $C546: BD 3A C6   lda  $C63A,X      ; base note
L_C549:
    $C549: 0A         asl  A
    $C54A: A8         tay
    $C54B: B9 67 C5   lda  $C567,Y      ; freq lo
    $C54E: 8D 42 C6   sta  $C642
    $C551: B9 68 C5   lda  $C568,Y      ; freq hi
    $C554: AC 2A C6   ldy  $C62A
    $C557: 99 01 D4   sta  $D401,Y
    $C55A: AD 42 C6   lda  $C642
    $C55D: 99 00 D4   sta  $D400,Y

; ======= voice loop tail =======
; X--; if non-negative, loop back to per-voice body at $C24E. Otherwise
; fall through to the engine RTS.
L_C560:
    $C560: CA         dex
    $C561: 30 03      bmi  $C566      ; → L_C566   ; X = -1 → done
    $C563: 4C 4E C2   jmp  $C24E      ; → L_C24E   ; next voice
L_C566:
    $C566: 60         rts               ; play frame complete
; ----- data gap $C567-$CF63 (2556 bytes) -----

; ======= engine init body (jumped to from $C200) =======
; A on entry = subtune number (0-indexed). Compute A*6 via A*2 + A*4
; (via two ASL with intermediate save in $C643). X = A*6 ends up indexing
; into the per-subtune orderlist pointer table at $C700. Copy 6 bytes
; into $C6FA (per-voice orderlist pointers — 3 lo + 3 hi). Then silence
; SID (V1/V2/V3 ctrl=0, filter=0), set vol=$F, and write state byte
; $C655 = $40 — first-frame bit set so the very next $C206 invocation
; runs the first-frame setup at $C210.
L_CF63:
    $CF63: A0 00      ldy  #$00
    $CF65: 0A         asl  A            ; A = subtune*2
    $CF66: 8D 43 C6   sta  $C643        ; save *2
    $CF69: 0A         asl  A            ; A = subtune*4
    $CF6A: 18         clc
    $CF6B: 6D 43 C6   adc  $C643        ; A = subtune*4 + subtune*2 = *6
    $CF6E: AA         tax
L_CF6F:
    $CF6F: BD 00 C7   lda  $C700,X      ; orderlist pointer table entry
    $CF72: 99 FA C6   sta  $C6FA,Y      ; → per-voice pointer slot
    $CF75: E8         inx
    $CF76: C8         iny
    $CF77: C0 06      cpy  #$06         ; 6 bytes total (3 lo + 3 hi)
    $CF79: D0 F4      bne  $CF6F      ; → L_CF6F
    $CF7B: A9 00      lda  #$00
    $CF7D: 8D 17 D4   sta  $D417        ; filter routing = 0
    $CF80: 8D 04 D4   sta  $D404        ; V1 ctrl = 0
    $CF83: 8D 0B D4   sta  $D40B        ; V2 ctrl = 0
    $CF86: 8D 12 D4   sta  $D412        ; V3 ctrl = 0
    $CF89: A9 0F      lda  #$0F
    $CF8B: 8D 18 D4   sta  $D418        ; vol = $F
    $CF8E: A9 40      lda  #$40
    $CF90: 8D 55 C6   sta  $C655        ; state = $40 (first-frame)
    $CF93: 60         rts

; ======= engine stop body (jumped to from $C203) =======
; State = $C0 — bit 7 (end-of-song) AND bit 6 (first-frame-of-end). The
; next $C206 sees BMI taken at $C20C and routes to the silence path at
; $C22C, which zeros all voice ctrls and lowers state to $80.
L_CF94:
    $CF94: A9 C0      lda  #$C0
    $CF96: 8D 55 C6   sta  $C655
    $CF99: 60         rts

; ============================================================================
; END OF REACHABLE CODE
; ============================================================================
