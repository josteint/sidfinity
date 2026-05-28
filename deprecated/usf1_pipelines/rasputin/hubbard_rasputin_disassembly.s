; ============================================================================
; Rob Hubbard - Rasputin (1985 Firebird)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/Hubbard_Rob/Rasputin.sid
; Load:   $C000   Init: $CFB5   Play: $C012
; PSID:   18 subtunes, default subtune 1 (1-indexed; A=0 passed to init)
; Binary: $C000-$CFC9 (4042 bytes)
;
; Auto-traced 1276 reachable code bytes from init+play. Layout commentary
; below was hand-derived by combining static analysis with py65 single-step
; simulation logging SID writes and state-byte transitions across 8 frames.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($CFB5): dispatcher.
;   A < 2  → music init: LDY #$FF; STY $C54C (music-mode flag = -1);
;            JMP $C000 (= JMP $CF57) → music setup.
;   A >= 2 → SFX init: SBC #$02; JSR $C00F (= JMP $CFA1) → SFX trigger
;            with A = sfx_index. Note: the 16 "extra" PSID subtunes are
;            one-shot sound effects, not music tracks.
;
; $CF57 (music setup): copies the 6-byte orderlist-pointer pack for this
; subtune from $C72B+subtune*6 → $C725..$C72A, reads per-subtune tick
; reload from $C537,X → $C53B, silences all three SID voice ctrls, sets
; volume = $0F, and stamps $C53D = $40 ("first-frame" sentinel, bit 6).
;
; play ($C012): every frame.
;   1. DEC $C53A. If still ≥0 → JMP $C020 (music tick). If wrapped
;      to $FF → reload $C53A from $C539 and JMP $C3C5 (SFX-only tick).
;      Binary default $C53A=$05, $C539=$05. Each orderlist $FE marker
;      overwrites $C539+$C53A with a fresh sub-frame period, so the
;      music-vs-SFX cadence is data-driven.
;   2. At $C020: INC $C549 (global frame counter), then BIT $C53D.
;        bit 7 set → end-of-song → JMP $C046 (silence path).
;        bit 6 set → FIRST-FRAME → zero per-voice state arrays + $C549,
;                    clear $C53D, fall through to per-voice loop.
;        both clear → normal play → fall through.
;   3. Per-voice loop ($C060): X = 2 then 1 then 0 (V3 → V2 → V1).
;      DEC $C536 (per-voice tick). When $C536 just wrapped and was
;      reloaded from $C53B, $C536 == $C53B → take note-load path.
;      Otherwise → JMP $C091 → JMP $C1BF (effects-only this frame).
;      Each iteration ends at $C3AF tail; falls through to $C3C5 after V1.
;   4. $C3C5: SFX mixer. RTSs if no SFX channels are active, else
;      updates the active SFX freq/ctrl writes.
;
; PER-VOICE STATE ARRAYS (3-byte stride per voice; X = 0/1/2):
;   $C50C,X  v_olpos       orderlist position
;   $C50F,X  v_patpos      pattern byte position
;   $C512,X  v_dur         note duration countdown
;   $C515,X  v_flag        pattern flag byte (raw 8 bits)
;                          bits 0-4 = duration, 5 = no_release,
;                          6 = tie, 7 = "no inst byte follows"
;   $C518,X  v_ctrl        cached inst.ctrl (for gate-off rewrite)
;   $C51B,X  v_pitch       semitone index (0-95)
;   $C51E,X  v_inst        instrument index
;   $C521    (scratch — gate mask, lives at $C521 not $C521,X)
;   $C52D,X  v_pwm_dly     PWM step countdown (bidirectional mode)
;   $C530,X  v_pwm_dir     PWM direction (0=ascending, !0=descending)
;   $C533,X  v_arp_dly     waveform-shimmer countdown (fx bit 1)
;   $C53E,X  v_fhi         live freq_hi (after porta/skydive)
;   $C541,X  v_flo         live freq_lo
;   $C544,X  v_porta       portamento speed+dir byte (from pattern)
;
; GLOBAL STATE:
;   $C508-$C50A  SID voice base lookup table ($00, $07, $0E)
;   $C536        per-voice tick counter
;   $C539/$C53A  sub-frame divider reload / live counter (gates SFX)
;   $C53B        per-voice tick reload (= speed-1; from $C537,subtune)
;   $C53C        instrument *8 byte offset (saved for fx loop)
;   $C53D        song state: bit 7 = end, bit 6 = first-frame
;   $C549        global frame counter (vibrato LFO source)
;   $C54A/$C54B  SFX channel state (active pointers)
;   $C54C        music/SFX mode flag ($FF = music, $00 = SFX-only)
;   $C725-$C72A  active orderlist pointers, layout (V1lo,V2lo,V3lo,V1hi,V2hi,V3hi)
;
; DATA TABLES:
;   $C448  freq table   192 bytes, 96 semitones × 2 bytes little-endian
;                       (populated at runtime by a builder I haven't traced;
;                        binary value is all zeros, py65 sim shows
;                        $C448 = $0116, $C44A = $0127, ... standard PAL)
;   $C508  SID voice bases  3 bytes ($00, $07, $0E)
;   $C537  speed table       per-subtune tick reload byte
;   $C5B5  instrument table  8 bytes per record:
;            +0 pw_lo  +1 pw_hi  +2 ctrl  +3 AD  +4 SR
;            +5 vib_depth  +6 pwm_speed  +7 fx_flags
;   $C725  runtime orderlist ptr pack (3 lo, 3 hi)
;   $C72B  per-subtune orderlist-ptr packs, 6 bytes per subtune
;   $C737  pattern start ptr lo (indexed by pattern number)
;   $C769  pattern start ptr hi
;
; PATTERN BYTE FORMAT (matches Action Biker's encoding):
;   First byte of each event = (flag<<5) | duration:
;     bit 7 = "no inst byte follows" (1 = reuse previous v_inst)
;     bit 6 = tie / legato (1 = no freq write, no gate; just sustain)
;     bit 5 = no_release (suppress the v_dur=0 HR kill)
;     bits 0-4 = duration in ticks
;   If bit 7 == 0, next byte = instrument index (bit 7=1 → porta byte).
;   Next byte = pitch (0-95). After pitch, pattern advances; sentinel
;   $FF terminates the pattern.
;   Orderlist sentinels: $FF = loop back; $FE = followed by speed byte
;   stored to $C539+$C53A; $FD = JSR $C003 → song-end ($C53D = $C0).
;
; FX_FLAGS LAYOUT (byte +7 of each instrument record) — note the
; discrepancy with extract/decompile.py's labels:
;   bit 0 = SKYDIVE          (freq_hi decrement each frame, $C31E)
;   bit 1 = waveform shimmer (EOR $C518 with #$18 every 2 frames, $C35A)
;   bit 2 = ARPEGGIO         (+0/+12 pitch alternation on bit 1 of $C549, $C37E)
;   bit 3 = PWM mode         (1 = linear add, 0 = bidirectional $08/$0E)
;   bits 4-7 = unused in the play path
; (decompile.py labels bit 0 = drum, bit 1 = skydive, bit 2 = arp.
;  Rasputin has NO drum bit in this engine — bit 0 is skydive. The
;  extracted Rasputin instruments empirically have bit 0 set on
;  every percussive instrument and the codegen handles it correctly,
;  but the label in decompile.py is misleading for this song.)
;
; HARD-CODED PWM BOUNDS:
;   $C29F: CMP #$0E  (ascending wrap)
;   $C2B9: CMP #$08  (descending wrap)
; Same as Commando ($08/$0E). NOT per-instrument. See reference memory
; `reference_hubbard_pwm_bounds.md`.
;
; ============================================================================

; Trampolines at the top of the binary. Init dispatches through these so
; that the sub-engine entry points stay at fixed addresses regardless of
; where the bulk of the player code ends up.
L_C000:
    $C000: 4C 57 CF   JMP $cf57        ; → L_CF57   ; music init
sub_C003:
    $C003: 4C 8D CF   JMP $cf8d        ; → L_CF8D   ; song-end marker ($FD)
; ----- data gap $C006-$C00E (9 bytes) -----

sub_C00F:
    $C00F: 4C A1 CF   JMP $cfa1        ; → L_CFA1   ; SFX trigger
; ======= play: =======
; Outer frame entry. The first thing every frame does is run a sub-frame
; divider that gates whether THIS frame is a music tick or an SFX-only
; tick. $C53A/$C539 both start at $05 from the binary; orderlist $FE
; markers can overwrite both at runtime to change the music/SFX cadence.
;
; Cadence: with $C539=$05, music runs on the 5 frames where $C53A wraps
; through $04..$00, and the SFX-only path runs on the 6th frame (the
; underflow tick). py65 sim confirms the typical run-time cadence: music
; on frames {0,1,2,4,5,...}, SFX-only on frames {3,7,...}.
play:
    $C012: CE 3A C5   DEC $c53a        ; sub-frame counter
    $C015: 10 09      BPL $c020        ; → L_C020   ; ≥0: do music tick
    $C017: AD 39 C5   LDA $c539        ; ELSE wrapped: reload+SFX
    $C01A: 8D 3A C5   STA $c53a
    $C01D: 4C C5 C3   JMP $c3c5        ; → L_C3C5   ; SFX-only this frame
; Music-tick path. Tests $C53D's two flag bits (BIT moves bit 7→N, bit 6→V):
;   bit 7 = end-of-song (set after $FD orderlist marker via $CF8D)
;   bit 6 = first-frame (set by music init at $CF87)
L_C020:
    $C020: EE 49 C5   INC $c549        ; global frame counter (vibrato LFO)
    $C023: 2C 3D C5   BIT $c53d        ; song state
    $C026: 30 1E      BMI $c046        ; → L_C046   ; bit 7: end-of-song
    $C028: 50 36      BVC $c060        ; → L_C060   ; both clear: normal play
    ; First-frame path. Zero per-voice state arrays, reset $C549, clear
    ; $C53D so subsequent frames take the BVC straight to $C060.
    $C02A: A9 00      LDA #$00
    $C02C: 8D 49 C5   STA $c549        ; reset frame counter
    $C02F: A2 02      LDX #$02         ; loop X=2..0 (V3, V2, V1)
L_C031:
    $C031: 9D 0C C5   STA $c50c,x      ; v_olpos,X  = 0
    $C034: 9D 0F C5   STA $c50f,x      ; v_patpos,X = 0
    $C037: 9D 12 C5   STA $c512,x      ; v_dur,X    = 0
    $C03A: 9D 1B C5   STA $c51b,x      ; v_pitch,X  = 0
    $C03D: CA         DEX
    $C03E: 10 F1      BPL $c031        ; → L_C031
    $C040: 8D 3D C5   STA $c53d        ; clear song-state byte
    $C043: 4C 60 C0   JMP $c060        ; → L_C060   ; first per-voice tick
; End-of-song path. Bit 7 of $C53D set. If bit 6 also set ($C53D = $C0,
; the value $CF8D writes), perform the panic-silence: zero all 3 voice
; ctrls, keep vol = $0F so SFX can still be heard, then drop $C53D to
; $80 (bit 6 cleared). Subsequent end-of-song frames see only bit 7
; and fall through to $C05D → $C3C5 (SFX-only) — silence is preserved.
L_C046:
    $C046: 50 15      BVC $c05d        ; → L_C05D   ; bit 6 clear: just go SFX
    $C048: A9 00      LDA #$00
    $C04A: 8D 04 D4   STA $d404        ;V1_CTRL = 0 (gate off, no wave)
    $C04D: 8D 0B D4   STA $d40b        ;V2_CTRL = 0
    $C050: 8D 12 D4   STA $d412        ;V3_CTRL = 0
    $C053: A9 0F      LDA #$0f
    $C055: 8D 18 D4   STA $d418        ;VOL = $0F (preserve master volume)
    $C058: A9 80      LDA #$80         ; bit 7 only (end-of-song latched)
    $C05A: 8D 3D C5   STA $c53d
L_C05D:
    $C05D: 4C C5 C3   JMP $c3c5        ; → L_C3C5   ; run SFX, return
; Per-voice loop entry. X iterates 2→1→0 (V3→V2→V1), with the per-frame
; tick-divider $C536 advanced ONCE per music tick (before the X=2 iteration).
;
; **NOTE-LOAD GATE**: note-load runs only on the frame where $C536 just
; reloaded from $C53B (so CMP $C536, $C53B == equal). On all other music
; frames the gate fails and we drop into the effects-only path. With
; $C53B = $01 (typical) this means note-load runs every 2nd music tick.
L_C060:
    $C060: A2 02      LDX #$02         ; start with V3
    $C062: CE 36 C5   DEC $c536        ; per-voice tick counter
    $C065: 10 06      BPL $c06d        ; → L_C06D   ; ≥0: no reload
    $C067: AD 3B C5   LDA $c53b        ; wrapped: reload from speed table
    $C06A: 8D 36 C5   STA $c536
L_C06D:
    ; Per-voice work begins. Save SID base offset for this voice into
    ; $C50B so later writes can use STA $D400,Y addressing.
    $C06D: BD 08 C5   LDA $c508,x      ; SID voice base (0,7,14 from $C508)
    $C070: 8D 0B C5   STA $c50b        ; cache for STA $D400,Y
    $C073: A8         TAY
    ; Note-load gate.
    $C074: AD 36 C5   LDA $c536
    $C077: CD 3B C5   CMP $c53b
    $C07A: D0 15      BNE $c091        ; → L_C091   ; gate fails: effects-only
    ; Gate passes: load orderlist ptr for this voice and DEC v_dur.
    ; If v_dur wraps (-1), it's time to advance to the next note.
    ; Else jump to $C198 (HR kill check + effects loop).
    $C07C: BD 25 C7   LDA $c725,x      ; orderlist ptr lo[X]
    $C07F: 85 FC      STA $fc
    $C081: BD 28 C7   LDA $c728,x      ; orderlist ptr hi[X]
    $C084: 85 FD      STA $fd
    $C086: DE 12 C5   DEC $c512,x      ; v_dur--
    $C089: 30 09      BMI $c094        ; → L_C094   ; expired: advance pat
    $C08B: 4C 98 C1   JMP $c198        ; → L_C198   ; sustain: HR check + fx
; ----- data gap $C08E-$C090 (3 bytes) -----

; Effects-only path (note-load gate failed). Just goes to the effects
; loop without touching pattern data. Per-voice tail in $C3AF
; eventually loops X back through $C06D for the next voice.
L_C091:
    $C091: 4C BF C1   JMP $c1bf        ; → L_C1BF
; Orderlist sentinel handler. Reads orderlist[v_olpos] and dispatches:
;   $FF → restart orderlist (loop back to start of song)
;   $FE → speed-change marker: next byte → $C539 + $C53A, then continue
;   $FD → song-end marker: JSR $C003 (= $CF8D sets $C53D = $C0). The
;         CPY/CMP at $C0B9 are NOT executed — the JSR is followed by a
;         BCS/branch handled via the post-marker flow; the bytes shown
;         here are the auto-disassembler chasing past the JSR target.
;   else → A holds pattern number → fall through to $C0CE.
L_C094:
    $C094: BC 0C C5   LDY $c50c,x      ; Y = v_olpos
    $C097: B1 FC      LDA ($fc),y      ; orderlist[v_olpos]
    $C099: C9 FF      CMP #$ff
    $C09B: F0 20      BEQ $c0bd        ; → L_C0BD   ; restart orderlist
    $C09D: C9 FE      CMP #$fe
    $C09F: D0 12      BNE $c0b3        ; → L_C0B3
    ; $FE = speed change: skip the FE byte, read the next byte as the
    ; new sub-frame period, store to both $C539 (reload) and $C53A
    ; (live), then resume orderlist scan at the byte after.
    $C0A1: FE 0C C5   INC $c50c,x      ; v_olpos++ (past $FE)
    $C0A4: C8         INY
    $C0A5: B1 FC      LDA ($fc),y      ; speed byte
    $C0A7: 8D 39 C5   STA $c539
    $C0AA: 8D 3A C5   STA $c53a
    $C0AD: FE 0C C5   INC $c50c,x      ; v_olpos++ (past speed byte)
    $C0B0: 4C 94 C0   JMP $c094        ; → L_C094   ; re-scan
L_C0B3:
    $C0B3: C9 FD      CMP #$fd
    $C0B5: D0 17      BNE $c0ce        ; → L_C0CE   ; not FD: must be a pattern #
    ; $FD = song-end: signal via $CF8D which writes $C53D = $C0. The
    ; CPY/CMP bytes the auto-disassembler shows at $C0B9-$C0BC are
    ; really the high bytes of the JSR target embedded in the loop —
    ; in practice control flows from the JSR straight into the
    ; restart-orderlist path at $C0BD (because the JSR'd routine RTSs
    ; and the next instruction is the restart-orderlist code).
    $C0B7: 20 03      JSR $c003        ; → sub_C003 ; $C53D = $C0 (end+silence)
    $C0B9: C0 4C      CPY #$4c         ; (these bytes are reached only as
    $C0BB: C5 C3      CMP $c3          ;  fall-through after the JSR returns)
; Restart-orderlist path. Zero v_dur, v_olpos, v_patpos and retry the
; orderlist scan from position 0. Reached by $FF marker and as
; fall-through after the $FD song-end JSR returns.
L_C0BD:
    $C0BD: A9 00      LDA #$00
    $C0BF: 9D 12 C5   STA $c512,x      ; v_dur,X    = 0
    $C0C2: 9D 0C C5   STA $c50c,x      ; v_olpos,X  = 0
    $C0C5: 9D 0F C5   STA $c50f,x      ; v_patpos,X = 0
    $C0C8: 4C 94 C0   JMP $c094        ; → L_C094   ; retry from start
; ----- data gap $C0CB-$C0CD (3 bytes) -----

; Normal pattern load. A holds pattern number from the orderlist.
; Pattern table is at $C737 (lo) / $C769 (hi), 1-byte indexed per pat.
L_C0CE:
    $C0CE: A8         TAY               ; Y = pattern number
    $C0CF: B9 37 C7   LDA $c737,y       ; pat_lo[Y]
    $C0D2: 85 FE      STA $fe
    $C0D4: B9 69 C7   LDA $c769,y       ; pat_hi[Y]
    $C0D7: 85 FF      STA $ff           ; ($FE) now points at pattern start
    $C0D9: A9 00      LDA #$00
    $C0DB: 9D 44 C5   STA $c544,x       ; v_porta,X = 0 (clear any leftover slide)
    $C0DE: BC 0F C5   LDY $c50f,x       ; Y = v_patpos
    $C0E1: A9 FF      LDA #$ff          ; gate mask = $FF (tie will DEC it)
    $C0E3: 8D 21 C5   STA $c521
    ; Read pattern flag/duration byte. v_flag,X holds the whole byte for
    ; later HR/tie/no_release decisions; v_dur,X takes only the low 5 bits.
    $C0E6: B1 FE      LDA ($fe),y       ; pattern[Y] = flag|dur byte
    $C0E8: 9D 15 C5   STA $c515,x       ; v_flag,X
    $C0EB: 8D 22 C5   STA $c522         ; copy for BIT below
    $C0EE: 29 1F      AND #$1f
    $C0F0: 9D 12 C5   STA $c512,x       ; v_dur,X = duration ticks
    ; BIT $C522: N = bit 7 (no inst byte), V = bit 6 (tie). Tie skips
    ; the inst/pitch fetch entirely and jumps to $C13C (gate-mask DEC).
    $C0F3: 2C 22 C5   BIT $c522
    $C0F6: 70 44      BVS $c13c        ; → L_C13C   ; tie: skip note-load
    ; Not a tie. Advance v_patpos past the flag byte.
    $C0F8: FE 0F C5   INC $c50f,x       ; v_patpos++
    $C0FB: AD 22 C5   LDA $c522
    $C0FE: 10 11      BPL $c111        ; → L_C111   ; bit 7 clear → no inst byte
    ; Bit 7 was clear in the flag byte → next byte follows. It is either
    ; an instrument number (bit 7 clear) or a portamento byte (bit 7 set).
    $C100: C8         INY
    $C101: B1 FE      LDA ($fe),y       ; next byte
    $C103: 10 06      BPL $c10b        ; → L_C10B   ; <$80: instrument index
    $C105: 9D 44 C5   STA $c544,x       ; ≥$80: portamento (speed+dir byte)
    $C108: 4C 0E C1   JMP $c10e        ; → L_C10E
L_C10B:
    $C10B: 9D 1E C5   STA $c51e,x       ; v_inst,X = instrument index
L_C10E:
    $C10E: FE 0F C5   INC $c50f,x       ; v_patpos++ (past inst/porta byte)
L_C111:
    ; Pitch byte. Doubled (ASL) because freq table at $C448 uses 2-byte
    ; entries per semitone. All 96 semitones reachable as a direct index.
    $C111: C8         INY
    $C112: B1 FE      LDA ($fe),y       ; pitch (0-95)
    $C114: 9D 1B C5   STA $c51b,x       ; v_pitch,X
    $C117: 0A         ASL a
    $C118: A8         TAY               ; Y = pitch*2 (freq table byte offset)
    ; Music-mode gate: $C54C is $FF in music mode, $00 in SFX-only.
    ; Only write SID freq if we're actually in music mode.
    $C119: AD 4C C5   LDA $c54c
    $C11C: 10 21      BPL $c13f        ; → L_C13F   ; SFX mode: skip SID write
    $C11E: B9 48 C4   LDA $c448,y       ; freq_lo[pitch]
    $C121: 8D 23 C5   STA $c523         ; stash
    $C124: B9 49 C4   LDA $c449,y       ; freq_hi[pitch]
    $C127: AC 0B C5   LDY $c50b         ; SID base offset
    $C12A: 99 01 D4   STA $d401,y       ;V_FREQ_HI
    $C12D: 9D 3E C5   STA $c53e,x       ; v_fhi,X (live freq_hi for porta/skydive)
    $C130: AD 23 C5   LDA $c523
    $C133: 99 00 D4   STA $d400,y       ;V_FREQ_LO
    $C136: 9D 41 C5   STA $c541,x       ; v_flo,X
    $C139: 4C 3F C1   JMP $c13f        ; → L_C13F   ; common tail
L_C13C:
    ; Tie path: don't write freq. Just clear bit 0 of the gate mask
    ; (later ANDed into ctrl) so the gate stays in its current state
    ; for the legato continuation.
    $C13C: CE 21 C5   DEC $c521         ; $C521 $FF → $FE (clears gate bit)
; Instrument write-out. Look up the 8-byte instrument record at
; $C5B5 + v_inst*8 and copy its fields into the SID. ctrl is ANDed
; with the gate mask ($C521) so ties don't retrigger the gate.
;
; The whole instrument-record byte offset is reused later in the
; effects loop ($C1C7) — that path reaches inst.fx_flags ($C5BC,Y)
; etc. via the same X*8 stride.
L_C13F:
    $C13F: AC 0B C5   LDY $c50b         ; Y = SID base
    $C142: BD 1E C5   LDA $c51e,x       ; v_inst,X
    $C145: 8E 24 C5   STX $c524         ; save voice X
    $C148: 0A         ASL a             ; * 2
    $C149: 0A         ASL a             ; * 4
    $C14A: 0A         ASL a             ; * 8 (record stride)
    $C14B: AA         TAX               ; X = byte offset into instrument table
    $C14C: BD B7 C5   LDA $c5b7,x       ; inst.ctrl  (byte +2 of record)
    $C14F: 8D 25 C5   STA $c525         ; stash unmasked ctrl → v_ctrl,X later
    $C152: AD 4C C5   LDA $c54c
    $C155: 10 21      BPL $c178        ; → L_C178   ; SFX mode: skip SID writes
    ; Music mode: copy ctrl/pw_lo/pw_hi/AD/SR into the SID for this voice.
    $C157: BD B7 C5   LDA $c5b7,x       ; inst.ctrl
    $C15A: 2D 21 C5   AND $c521         ; mask gate via tie flag
    $C15D: 99 04 D4   STA $d404,y       ;V_CTRL
    $C160: BD B5 C5   LDA $c5b5,x       ; inst.pw_lo (byte +0)
    $C163: 99 02 D4   STA $d402,y       ;V_PW_LO
    $C166: BD B6 C5   LDA $c5b6,x       ; inst.pw_hi (byte +1)
    $C169: 99 03 D4   STA $d403,y       ;V_PW_HI
    $C16C: BD B8 C5   LDA $c5b8,x       ; inst.AD    (byte +3)
    $C16F: 99 05 D4   STA $d405,y       ;V_AD
    $C172: BD B9 C5   LDA $c5b9,x       ; inst.SR    (byte +4)
    $C175: 99 06 D4   STA $d406,y       ;V_SR
L_C178:
    ; Cache the unmasked inst.ctrl into v_ctrl,X for later gate-off
    ; rewrites (HR kill at $C198, waveform shimmer at $C375, skydive
    ; at $C348). Then check whether the byte AFTER the pitch is $FF,
    ; meaning end-of-pattern: if so, reset v_patpos and advance v_olpos.
    $C178: AE 24 C5   LDX $c524         ; restore voice X
    $C17B: AD 25 C5   LDA $c525
    $C17E: 9D 18 C5   STA $c518,x       ; v_ctrl,X = unmasked inst.ctrl
    $C181: FE 0F C5   INC $c50f,x       ; advance v_patpos past pitch byte
    $C184: BC 0F C5   LDY $c50f,x
    $C187: B1 FE      LDA ($fe),y       ; peek next byte
    $C189: C9 FF      CMP #$ff
    $C18B: D0 08      BNE $c195        ; → L_C195   ; not end-of-pat
    $C18D: A9 00      LDA #$00
    $C18F: 9D 0F C5   STA $c50f,x       ; v_patpos,X = 0
    $C192: FE 0C C5   INC $c50c,x       ; v_olpos,X++
L_C195:
    $C195: 4C AF C3   JMP $c3af        ; → L_C3AF   ; per-voice tail
; HARD-RESTART (HR) kill check. Reached from the sustain path
; (note didn't advance, v_dur was still positive after DEC at $C086).
; If the pattern flag's no_release bit (bit 5) is set, OR v_dur > 0,
; we skip the kill and just run effects. When v_dur == 0 AND
; no_release is clear, we write ctrl with gate-off + AD=0 + SR=0 to
; cleanly retrigger the envelope on the next note.
;
; Note the music-mode gate at $C198: in SFX-only mode the HR write is
; suppressed (otherwise SFX channels would silence the music voice).
L_C198:
    $C198: AD 4C C5   LDA $c54c
    $C19B: 30 03      BMI $c1a0        ; → L_C1A0   ; music mode: HR check
    $C19D: 4C AF C3   JMP $c3af        ; → L_C3AF   ; SFX-only: skip
L_C1A0:
    $C1A0: AC 0B C5   LDY $c50b         ; SID base
    $C1A3: BD 15 C5   LDA $c515,x       ; v_flag,X
    $C1A6: 29 20      AND #$20          ; bit 5 = no_release
    $C1A8: D0 15      BNE $c1bf        ; → L_C1BF   ; no_release: skip HR
    $C1AA: BD 12 C5   LDA $c512,x       ; v_dur,X
    $C1AD: D0 10      BNE $c1bf        ; → L_C1BF   ; dur > 0: still sustaining
    ; HR kill: write ctrl without gate, then AD=0 and SR=0.
    $C1AF: BD 18 C5   LDA $c518,x       ; v_ctrl,X (cached inst.ctrl)
    $C1B2: 29 FE      AND #$fe          ; clear gate bit
    $C1B4: 99 04 D4   STA $d404,y       ;V_CTRL (gate off)
    $C1B7: A9 00      LDA #$00
    $C1B9: 99 05 D4   STA $d405,y       ;V_AD = 0
    $C1BC: 99 06 D4   STA $d406,y       ;V_SR = 0
; ======= Effects loop entry =======
; Per-frame effect application (vibrato, PWM, portamento, skydive,
; waveform shimmer, arpeggio). All effects are bypassed in SFX-only
; mode via the $C54C music-mode flag check.
L_C1BF:
    $C1BF: AD 4C C5   LDA $c54c
    $C1C2: 30 03      BMI $c1c7        ; → L_C1C7   ; music mode: continue
    $C1C4: 4C AF C3   JMP $c3af        ; → L_C3AF   ; SFX-only: skip
L_C1C7:
    ; Compute Y = v_inst * 8 = byte offset into instrument record. Save
    ; to $C53C for the PWM block to reuse (avoids recomputing).
    $C1C7: BD 1E C5   LDA $c51e,x       ; v_inst,X
    $C1CA: 0A         ASL a             ; * 2
    $C1CB: 0A         ASL a             ; * 4
    $C1CC: 0A         ASL a             ; * 8
    $C1CD: A8         TAY
    $C1CE: 8C 3C C5   STY $c53c         ; remember byte offset
    ; Read effect parameters from bytes 5,6,7 of the instrument record.
    $C1D1: B9 BC C5   LDA $c5bc,y       ; inst.fx_flags (+7)
    $C1D4: 8D 47 C5   STA $c547
    $C1D7: B9 BB C5   LDA $c5bb,y       ; inst.pwm_speed (+6)
    $C1DA: 8D 27 C5   STA $c527
    $C1DD: B9 BA C5   LDA $c5ba,y       ; inst.vib_depth (+5)
    $C1E0: 8D 26 C5   STA $c526
    $C1E3: F0 6F      BEQ $c254        ; → L_C254   ; depth=0: no vibrato
    ; Vibrato LFO. Triangle wave folded from global frame counter $C549:
    ; AND $07 → 0-7, if ≥4 EOR $07 → folds back to 0,1,2,3,3,2,1,0
    ; (period 8 frames).
    $C1E5: AD 49 C5   LDA $c549
    $C1E8: 29 07      AND #$07
    $C1EA: C9 04      CMP #$04
    $C1EC: 90 02      BCC $c1f0        ; → L_C1F0
    $C1EE: 49 07      EOR #$07          ; fold: 4→3, 5→2, 6→1, 7→0
L_C1F0:
    $C1F0: 8D 2C C5   STA $c52c         ; LFO step (0-3)
    ; Compute semitone delta freq[pitch+1] - freq[pitch].
    $C1F3: BD 1B C5   LDA $c51b,x       ; v_pitch,X
    $C1F6: 0A         ASL a             ; * 2 (table stride)
    $C1F7: A8         TAY
    $C1F8: 38         SEC
    $C1F9: B9 4A C4   LDA $c44a,y       ; freq_lo[pitch+1]
    $C1FC: F9 48 C4   SBC $c448,y       ; - freq_lo[pitch]
    $C1FF: 8D 28 C5   STA $c528         ; delta_lo
    $C202: B9 4B C4   LDA $c44b,y       ; freq_hi[pitch+1]
    $C205: F9 49 C4   SBC $c449,y       ; - freq_hi[pitch]
    ; Right-shift the 16-bit delta vib_depth+1 times (narrower vibrato).
L_C208:
    $C208: 4A         LSR a
    $C209: 6E 28 C5   ROR $c528
    $C20C: CE 26 C5   DEC $c526
    $C20F: 10 F7      BPL $c208        ; → L_C208
    $C211: 8D 29 C5   STA $c529         ; delta_hi (shifted)
    ; Load base freq into the accumulator pair $C52A/$C52B.
    $C214: B9 48 C4   LDA $c448,y       ; freq_lo[pitch]
    $C217: 8D 2A C5   STA $c52a
    $C21A: B9 49 C4   LDA $c449,y       ; freq_hi[pitch]
    $C21D: 8D 2B C5   STA $c52b
    ; Skip vibrato accumulation when raw pattern duration (v_flag low
    ; 5 bits) is < 4 — too-short notes don't need to vibrate.
    $C220: BD 15 C5   LDA $c515,x       ; v_flag,X
    $C223: 29 1F      AND #$1f
    $C225: C9 04      CMP #$04
    $C227: 90 1C      BCC $c245        ; → L_C245   ; short note: no vibrato
    $C229: AC 2C C5   LDY $c52c         ; LFO step
L_C22C:
    ; Add the shifted delta LFO times into the freq accumulator.
    $C22C: 88         DEY
    $C22D: 30 16      BMI $c245        ; → L_C245
    $C22F: 18         CLC
    $C230: AD 2A C5   LDA $c52a
    $C233: 6D 28 C5   ADC $c528
    $C236: 8D 2A C5   STA $c52a
    $C239: AD 2B C5   LDA $c52b
    $C23C: 6D 29 C5   ADC $c529
    $C23F: 8D 2B C5   STA $c52b
    $C242: 4C 2C C2   JMP $c22c        ; → L_C22C
L_C245:
    ; Write the (possibly vibrato-modulated) freq to the SID.
    $C245: AC 0B C5   LDY $c50b
    $C248: AD 2A C5   LDA $c52a
    $C24B: 99 00 D4   STA $d400,y       ;V_FREQ_LO
    $C24E: AD 2B C5   LDA $c52b
    $C251: 99 01 D4   STA $d401,y       ;V_FREQ_HI
; ======= PWM block =======
; Two modes selected by fx_flags bit 3:
;   bit 3 == 1: LINEAR — pw_lo += pwm_speed every frame, no bounds.
;   bit 3 == 0: BIDIRECTIONAL — sweep pw_hi between $08 and $0E using
;               pwm_speed's high 3 bits as step size and low 5 bits as
;               step interval. Direction flips at each bound.
;
; pwm_speed = 0 disables both modes (skip to portamento at $C2D7).
;
; **Live state lives IN the instrument table**: $C5B5,Y (pw_lo) and
; $C5B6,Y (pw_hi) are mutated each frame. The "init_pw" value the
; codegen emits is overwritten as soon as PWM runs.
L_C254:
    $C254: AD 47 C5   LDA $c547         ; fx_flags
    $C257: 29 08      AND #$08          ; bit 3 = linear mode
    $C259: F0 15      BEQ $c270        ; → L_C270   ; bit 3 clear: bidirectional
    ; LINEAR PWM: pw_lo += pwm_speed (single byte, wraps at 256).
    $C25B: AC 3C C5   LDY $c53c         ; inst byte offset
    $C25E: B9 B5 C5   LDA $c5b5,y       ; inst.pw_lo
    $C261: 6D 27 C5   ADC $c527         ; + pwm_speed
    $C264: 99 B5 C5   STA $c5b5,y       ; back into instrument
    $C267: AC 0B C5   LDY $c50b
    $C26A: 99 02 D4   STA $d402,y       ;V_PW_LO
    $C26D: 4C D7 C2   JMP $c2d7        ; → L_C2D7   ; (linear has no pw_hi write)
L_C270:
    ; BIDIRECTIONAL PWM.
    $C270: AD 27 C5   LDA $c527
    $C273: F0 62      BEQ $c2d7        ; → L_C2D7   ; speed=0: no PWM
    $C275: AC 3C C5   LDY $c53c
    $C278: 29 1F      AND #$1f          ; low 5 bits = step interval
    $C27A: DE 2D C5   DEC $c52d,x       ; v_pwm_dly,X--
    $C27D: 10 58      BPL $c2d7        ; → L_C2D7   ; ≥0: not yet time
    $C27F: 9D 2D C5   STA $c52d,x       ; reload v_pwm_dly with low 5 bits
    $C282: AD 27 C5   LDA $c527
    $C285: 29 E0      AND #$e0          ; high 3 bits = step size
    $C287: 8D 48 C5   STA $c548         ; delta (preshifted as e0-mask)
    $C28A: BD 30 C5   LDA $c530,x       ; v_pwm_dir,X
    $C28D: D0 1A      BNE $c2a9        ; → L_C2A9   ; nonzero = descending
    ; ASCENDING: pw += delta. Check upper bound $0E on the 4-bit pw_hi.
    $C28F: AD 48 C5   LDA $c548
    $C292: 18         CLC
    $C293: 79 B5 C5   ADC $c5b5,y       ; pw_lo + delta
    $C296: 48         PHA
    $C297: B9 B6 C5   LDA $c5b6,y       ; pw_hi
    $C29A: 69 00      ADC #$00          ; + carry
    $C29C: 29 0F      AND #$0f          ; 12-bit PW (4 bits of hi)
    $C29E: 48         PHA
    $C29F: C9 0E      CMP #$0e          ; HARDCODED upper bound
    $C2A1: D0 1D      BNE $c2c0        ; → L_C2C0
    $C2A3: FE 30 C5   INC $c530,x       ; flip to descending
    $C2A6: 4C C0 C2   JMP $c2c0        ; → L_C2C0
L_C2A9:
    ; DESCENDING: pw -= delta. Check lower bound $08 on pw_hi.
    $C2A9: 38         SEC
    $C2AA: B9 B5 C5   LDA $c5b5,y       ; pw_lo
    $C2AD: ED 48 C5   SBC $c548         ; - delta
    $C2B0: 48         PHA
    $C2B1: B9 B6 C5   LDA $c5b6,y       ; pw_hi
    $C2B4: E9 00      SBC #$00
    $C2B6: 29 0F      AND #$0f
    $C2B8: 48         PHA
    $C2B9: C9 08      CMP #$08          ; HARDCODED lower bound
    $C2BB: D0 03      BNE $c2c0        ; → L_C2C0
    $C2BD: DE 30 C5   DEC $c530,x       ; flip to ascending
L_C2C0:
    ; Pop the new pw_hi/pw_lo from stack, store back to instrument
    ; record AND write to SID.
    $C2C0: 8E 24 C5   STX $c524         ; save voice X
    $C2C3: AE 0B C5   LDX $c50b         ; X = SID base
    $C2C6: 68         PLA
    $C2C7: 99 B6 C5   STA $c5b6,y       ; inst.pw_hi (updated)
    $C2CA: 9D 03 D4   STA $d403,x       ;V_PW_HI
    $C2CD: 68         PLA
    $C2CE: 99 B5 C5   STA $c5b5,y       ; inst.pw_lo (updated)
    $C2D1: 9D 02 D4   STA $d402,x       ;V_PW_LO
    $C2D4: AE 24 C5   LDX $c524         ; restore voice X
; ======= Portamento (drum_trig in extract terminology) =======
; v_porta,X is set from the pattern's portamento byte (when bit 7 of
; the inst-slot byte is set; see $C105). It encodes:
;   bits 1-6 = delta (mask $7E = AND with $7E preserves bits 6..1)
;   bit 0    = direction (0 = ascending, 1 = descending)
; v_porta == 0 → no portamento this frame.
;
; The slide adds/subtracts delta from v_flo, with carry propagating
; into v_fhi (16-bit), and writes both back to SID + state.
L_C2D7:
    $C2D7: AC 0B C5   LDY $c50b
    $C2DA: BD 44 C5   LDA $c544,x       ; v_porta,X
    $C2DD: F0 3F      BEQ $c31e        ; → L_C31E   ; no portamento
    $C2DF: 29 7E      AND #$7e          ; isolate delta bits
    $C2E1: 8D 24 C5   STA $c524
    $C2E4: BD 44 C5   LDA $c544,x
    $C2E7: 29 01      AND #$01          ; direction bit
    $C2E9: F0 1B      BEQ $c306        ; → L_C306   ; 0 = ascending
    ; DESCENDING portamento.
    $C2EB: 38         SEC
    $C2EC: BD 41 C5   LDA $c541,x       ; v_flo,X
    $C2EF: ED 24 C5   SBC $c524         ; - delta
    $C2F2: 9D 41 C5   STA $c541,x
    $C2F5: 99 00 D4   STA $d400,y       ;V_FREQ_LO
    $C2F8: BD 3E C5   LDA $c53e,x       ; v_fhi,X
    $C2FB: E9 00      SBC #$00          ; - borrow
    $C2FD: 9D 3E C5   STA $c53e,x
    $C300: 99 01 D4   STA $d401,y       ;V_FREQ_HI
    $C303: 4C 1E C3   JMP $c31e        ; → L_C31E
L_C306:
    ; ASCENDING portamento.
    $C306: 18         CLC
    $C307: BD 41 C5   LDA $c541,x       ; v_flo,X
    $C30A: 6D 24 C5   ADC $c524         ; + delta
    $C30D: 9D 41 C5   STA $c541,x
    $C310: 99 00 D4   STA $d400,y       ;V_FREQ_LO
    $C313: BD 3E C5   LDA $c53e,x       ; v_fhi,X
    $C316: 69 00      ADC #$00          ; + carry
    $C318: 9D 3E C5   STA $c53e,x
    $C31B: 99 01 D4   STA $d401,y       ;V_FREQ_HI
; ======= SKYDIVE (fx_flags bit 0) =======
; Rasputin's signature percussion/sweep effect. Each frame:
;   - decrement v_fhi by 1 (freq_hi falls toward 0)
;   - on the FIRST frame of the note (the note-load frame), also
;     clear the gate bit in ctrl
;   - once v_fhi hits 0, latch ctrl = $80 (test bit = oscillator off)
;
; Guards: skip if v_fhi==0 (already finished), if v_dur==0 (note
; otherwise expired). The frame-position check uses
;   (orig_dur - 1) vs v_dur: BCC means we're past the FIRST tick of
;   the note. On the first tick (BCS branch) we decrement v_fhi and
;   AND-out the gate. On all subsequent ticks we just stamp the
;   already-decremented v_fhi (or $80 if it hit zero).
L_C31E:
    $C31E: AD 47 C5   LDA $c547         ; fx_flags
    $C321: 29 01      AND #$01          ; bit 0 = skydive
    $C323: F0 35      BEQ $c35a        ; → L_C35A   ; flag clear: skip
    $C325: BD 3E C5   LDA $c53e,x       ; v_fhi,X
    $C328: F0 30      BEQ $c35a        ; → L_C35A   ; already 0: skip
    $C32A: BD 12 C5   LDA $c512,x       ; v_dur,X
    $C32D: F0 2B      BEQ $c35a        ; → L_C35A   ; dur 0: skip
    $C32F: BD 15 C5   LDA $c515,x       ; v_flag,X (raw)
    $C332: 29 1F      AND #$1f          ; orig duration
    $C334: 38         SEC
    $C335: E9 01      SBC #$01          ; orig_dur - 1
    $C337: DD 12 C5   CMP $c512,x       ; compare to v_dur
    $C33A: AC 0B C5   LDY $c50b
    $C33D: 90 10      BCC $c34f        ; → L_C34F   ; past tick 1
    ; Tick 1 (initial frame of the note): decrement v_fhi, write OLD
    ; value to SID, mask out gate bit on ctrl.
    $C33F: BD 3E C5   LDA $c53e,x       ; v_fhi,X
    $C342: DE 3E C5   DEC $c53e,x       ; v_fhi--
    $C345: 99 01 D4   STA $d401,y       ;V_FREQ_HI (pre-DEC value)
    $C348: BD 18 C5   LDA $c518,x       ; v_ctrl,X
    $C34B: 29 FE      AND #$fe          ; clear gate bit
    $C34D: D0 08      BNE $c357        ; → L_C357   ; (BNE always: ctrl > 0)
L_C34F:
    ; Subsequent ticks: write current v_fhi to SID, latch ctrl = $80
    ; (test bit = silence) so when the slide reaches zero the
    ; oscillator is cleanly killed.
    $C34F: BD 3E C5   LDA $c53e,x
    $C352: 99 01 D4   STA $d401,y       ;V_FREQ_HI
    $C355: A9 80      LDA #$80          ; test bit (oscillator off)
L_C357:
    $C357: 99 04 D4   STA $d404,y       ;V_CTRL
L_C35A:
    ; ======= Waveform shimmer (fx_flags bit 1) =======
    ; Every 2 frames (gated by v_arp_dly,X), EOR v_ctrl with #$18 and
    ; rewrite ctrl. $18 = bits 3+4 = test bit + triangle bit, which
    ; produces a distinctive "shimmer" by alternating between the
    ; instrument's normal waveform and its silenced/triangle variant.
    ; Skipped when v_dur == 0.
    $C35A: AD 47 C5   LDA $c547         ; fx_flags
    $C35D: 29 02      AND #$02          ; bit 1 = shimmer
    $C35F: F0 1D      BEQ $c37e        ; → L_C37E
    $C361: BD 12 C5   LDA $c512,x       ; v_dur,X
    $C364: F0 18      BEQ $c37e        ; → L_C37E   ; note over: skip
    $C366: DE 33 C5   DEC $c533,x       ; v_arp_dly,X (shimmer counter)
    $C369: 10 13      BPL $c37e        ; → L_C37E   ; ≥0: not yet
    $C36B: A9 01      LDA #$01
    $C36D: 9D 33 C5   STA $c533,x       ; reload to $01 (toggles every 2 frames)
    $C370: BD 18 C5   LDA $c518,x       ; v_ctrl,X
    $C373: 49 18      EOR #$18          ; toggle test+triangle bits
    $C375: 9D 18 C5   STA $c518,x       ; store back so next toggle is symmetric
    $C378: AC 0B C5   LDY $c50b
    $C37B: 99 04 D4   STA $d404,y       ;V_CTRL
L_C37E:
    ; ======= Arpeggio (fx_flags bit 2) =======
    ; Alternate pitch and pitch+12 (one octave) every 2 frames based on
    ; bit 1 of $C549 (global frame counter). Looks up freq from the
    ; freq table for the alternated pitch and writes to SID. v_pitch is
    ; NOT mutated; the arpeggio is purely a SID-write-time effect.
    $C37E: AD 47 C5   LDA $c547         ; fx_flags
    $C381: 29 04      AND #$04          ; bit 2 = arpeggio
    $C383: F0 2A      BEQ $c3af        ; → L_C3AF
    $C385: AD 49 C5   LDA $c549         ; global frame counter
    $C388: 29 02      AND #$02          ; bit 1 of frame counter
    $C38A: F0 09      BEQ $c395        ; → L_C395   ; even half-period
    ; Octave-up half: pitch + 12.
    $C38C: BD 1B C5   LDA $c51b,x       ; v_pitch,X
    $C38F: 18         CLC
    $C390: 69 0C      ADC #$0c          ; + 12 semitones
    $C392: 4C 98 C3   JMP $c398        ; → L_C398
L_C395:
    ; Base half: use raw pitch.
    $C395: BD 1B C5   LDA $c51b,x       ; v_pitch,X
L_C398:
    $C398: 0A         ASL a             ; * 2 (freq table stride)
    $C399: A8         TAY
    $C39A: B9 48 C4   LDA $c448,y       ; freq_lo[pitch']
    $C39D: 8D 23 C5   STA $c523
    $C3A0: B9 49 C4   LDA $c449,y       ; freq_hi[pitch']
    $C3A3: AC 0B C5   LDY $c50b
    $C3A6: 99 01 D4   STA $d401,y       ;V_FREQ_HI
    $C3A9: AD 23 C5   LDA $c523
    $C3AC: 99 00 D4   STA $d400,y       ;V_FREQ_LO
; ======= Per-voice loop tail =======
; Recompute the music/SFX mode flag $C54C from current SFX state:
;   $C54A != 0 OR $C54B negative → SFX active → $C54C = $FF (music)
;   else → $C54C = $00 (SFX-only)
;
; The flag's polarity is checked in many places via BMI/BPL: $FF has
; bit 7 set (BMI taken = music) so the engine knows whether to write
; the music voice's effects. When no SFX is queued, the engine
; defaults to music mode ($C54C = $FF), which is the typical case.
;
; Then DEC X. If still ≥0, jump back to $C06D for the next voice.
; Otherwise fall through to $C3C5 (SFX mixer).
L_C3AF:
    $C3AF: A0 FF      LDY #$ff
    $C3B1: AD 4A C5   LDA $c54a         ; SFX channel A pointer
    $C3B4: D0 06      BNE $c3bc        ; → L_C3BC   ; nonzero → keep Y=$FF
    $C3B6: AD 4B C5   LDA $c54b         ; SFX channel B
    $C3B9: 30 01      BMI $c3bc        ; → L_C3BC   ; negative → keep Y=$FF
    $C3BB: C8         INY               ; both quiet: Y = $00
L_C3BC:
    $C3BC: 8C 4C C5   STY $c54c         ; new music-mode flag
    $C3BF: CA         DEX
    $C3C0: 30 03      BMI $c3c5        ; → L_C3C5   ; done with voices
    $C3C2: 4C 6D C0   JMP $c06d        ; → L_C06D   ; next voice
; ======= SFX update entry =======
; Reached every frame (either after the per-voice loop in music mode,
; or as the JMP target from $C012 in SFX-only mode). Forces $C54C
; back to $FF (so any subsequent music writes assume music mode),
; then checks whether any SFX channel is active. If both quiet, RTS.
; Otherwise drop into the SFX update at $C3D5.
L_C3C5:
    $C3C5: A9 FF      LDA #$ff
    $C3C7: 8D 4C C5   STA $c54c         ; restore music-mode for next frame
    $C3CA: AD 4A C5   LDA $c54a         ; SFX channel A pointer
    $C3CD: D0 05      BNE $c3d4        ; → L_C3D4   ; A active → no SFX update (yet)
    $C3CF: 2C 4B C5   BIT $c54b         ; SFX channel B state
    $C3D2: 10 01      BPL $c3d5        ; → L_C3D5   ; B has work to do
L_C3D4:
    $C3D4: 60         RTS               ; nothing to do
L_C3D5:
    ; SFX state byte $C54B layout:
    ;   bit 7 = active flag (BIT $C4B at $C3CF tested this)
    ;   bit 6 = "needs init" flag (BVC at $C3D5 takes when CLEAR)
    ;   bits 0-3 = SFX program index
    ; First time after trigger, bit 6 is set → take JSR to $C555 to
    ; load SFX program parameters into the SFX state registers.
    $C3D5: 50 03      BVC $c3da        ; → L_C3DA   ; bit 6 clear: already inited
    $C3D7: 20 55      JSR $c555        ; → sub_C555 ; one-shot SFX init
    ; --- The auto-disassembler "fell into" the SFX data tables here.
    ; $C3D9-$C3E1 are not really code; they're SFX state cells the
    ; player reads/writes by absolute address. The real continuation
    ; after the JSR comes via the RTS in $C555 → control returns
    ; *here*. Reading the bytes literally:
    ;   $C3D9: $C5 $CE → "CMP $ce"   (zp; harmless)
    ;   $C3DB: $4E $C5 $10 → "LSR $10C5" (writes a 16k-aligned cell)
    ;   $C3DE: $F5 $AD → "SBC $ad,X"
    ;   $C3E0: $54 $C5 → ".byte $54 $C5" (illegal opcode in NMOS 6502)
    ; If these executed we'd get nonsense; the routine actually
    ; resumes at $C3E2 in a path that doesn't go through these bytes
    ; (likely $C555's RTS pops a pre-pushed return address).
    $C3D9: C5 CE      CMP $ce
    $C3DB: 4E C5 10   LSR $10c5
    $C3DE: F5 AD      SBC $ad,x
    $C3E0: 54 C5      ???
L_C3DA:
    ; Real SFX-tick code begins here. Reads SFX state byte $C54B,
    ; masks low nibble (= current SFX op), updates SFX freq via the
    ; freq table at $C448, and toggles channel ctrl bits per the
    ; SFX descriptor at $C551 / $C554 etc.
    $C3E2: 29 0F      AND #$0f          ; (continuation of code path)
    $C3E4: 8D 4E C5   STA $c54e
    $C3E7: AD 4D C5   LDA $c54d         ; SFX duration counter
    $C3EA: CD 4F C5   CMP $c54f         ; reload threshold
    $C3ED: D0 0F      BNE $c3fe        ; → L_C3FE   ; not yet end
    ; SFX finished: silence both V1+V2 SFX channels and clear active.
    $C3EF: A2 00      LDX #$00
    $C3F1: 8E 04 D4   STX $d404         ;V1_CTRL = 0
    $C3F4: 8E 0B D4   STX $d40b         ;V2_CTRL = 0
    $C3F7: CA         DEX               ; X = $FF
    $C3F8: 8E 4B C5   STX $c54b         ; $C54B = $FF (clear active flag)
    $C3FB: 4C D4 C3   JMP $c3d4        ; → L_C3D4
L_C3FE:
    ; SFX still ticking. Step v_sfx_dur, look up freq for current
    ; SFX pitch from the freq table, write to V1 (BMI skips) and/or
    ; V2 channels per $C554 bits 7/6.
    $C3FE: CE 4D C5   DEC $c54d
    $C401: 0A         ASL a             ; pitch * 2 (table stride)
    $C402: A8         TAY
    $C403: 2C 54 C5   BIT $c554         ; SFX channel mask
    $C406: 30 20      BMI $c428        ; → L_C428   ; bit 7: V2 only
    $C408: 70 0C      BVS $c416        ; → L_C416   ; bit 6: V1 only
    ; Both channels: write V1 freq.
    $C40A: B9 48 C4   LDA $c448,y       ; freq_lo[pitch]
    $C40D: 8D 00 D4   STA $d400         ;V1_FREQ_LO
    $C410: B9 49 C4   LDA $c449,y       ; freq_hi[pitch]
    $C413: 8D 01 D4   STA $d401         ;V1_FREQ_HI
L_C416:
    ; V2: subtract $C550 (per-SFX detune offset) from pitch index.
    $C416: 98         TYA
    $C417: 38         SEC
    $C418: ED 50 C5   SBC $c550         ; detune offset
    $C41B: A8         TAY
    $C41C: B9 48 C4   LDA $c448,y
    $C41F: 8D 07 D4   STA $d407         ;V2_FREQ_LO
    $C422: B9 49 C4   LDA $c449,y
    $C425: 8D 08 D4   STA $d408         ;V2_FREQ_HI
L_C428:
    ; Optional per-tick ctrl toggles (gate flicker for noise effects).
    $C428: 2C 51 C5   BIT $c551         ; toggle-channel mask
    $C42B: 10 0B      BPL $c438        ; → L_C438
    $C42D: AD 52 C5   LDA $c552         ; V1 toggled ctrl state
    $C430: 49 01      EOR #$01          ; flip gate bit
    $C432: 8D 04 D4   STA $d404         ;V1_CTRL
    $C435: 8D 52 C5   STA $c552
L_C438:
    $C438: 50 0B      BVC $c445        ; → L_C445
    $C43A: AD 53 C5   LDA $c553         ; V2 toggled ctrl state
    $C43D: 49 01      EOR #$01
    $C43F: 8D 0B D4   STA $d40b         ;V2_CTRL
    $C442: 8D 53 C5   STA $c553
L_C445:
    $C445: 4C D4 C3   JMP $c3d4        ; → L_C3D4
; ----- data gap $C448-$C554 (269 bytes) -----
; $C448-$C507 = freq table (192 bytes, populated at runtime).
; $C508-$C536 = global voice state arrays + SID base table.
; $C537-$C554 = per-subtune speed table + SFX/song state bytes.

; ======= SFX program loader =======
; One-shot routine called the first frame a new SFX is triggered.
; Reads the 16-byte SFX descriptor at $C625 + sfx_idx*16 and unpacks
; it into the SFX state cells, then copies 14 bytes of initial SID
; register values into $D400..$D40D.
sub_C555:
    $C555: A9 00      LDA #$00
    $C557: 8D 04 D4   STA $d404         ;V1_CTRL = 0
    $C55A: 8D 0B D4   STA $d40b         ;V2_CTRL = 0
    $C55D: 8D 4E C5   STA $c54e         ; SFX scratch = 0
    ; SFX descriptor index = ($C54B AND $0F) * 16.
    $C560: AD 4B C5   LDA $c54b
    $C563: 29 0F      AND #$0f
    $C565: 8D 4B C5   STA $c54b         ; strip needs-init flag
    $C568: 0A         ASL a             ; * 2
    $C569: 0A         ASL a             ; * 4
    $C56A: 0A         ASL a             ; * 8
    $C56B: 0A         ASL a             ; * 16 (descriptor stride)
    $C56C: A8         TAY
    ; Pull descriptor parameters out into named state cells. The
    ; descriptor table lives at $C625; offsets into it are baked into
    ; the loads below ($C626 = $C625+1, $C634 = $C625+15, etc.).
    $C56D: B9 25 C6   LDA $c625,y       ; ch mask (bit 7 = V2 only, bit 6 = V1 only)
    $C570: 8D 54 C5   STA $c554
    $C573: B9 26 C6   LDA $c626,y       ; SFX duration
    $C576: 8D 4D C5   STA $c54d
    $C579: B9 34 C6   LDA $c634,y       ; reload threshold
    $C57C: 8D 4F C5   STA $c54f
    $C57F: B9 2D C6   LDA $c62d,y       ; ctrl-toggle mask + detune
    $C582: 8D 51 C5   STA $c551
    $C585: 29 3F      AND #$3f          ; low 6 bits
    $C587: 8D 50 C5   STA $c550         ; V2 pitch detune
    $C58A: B9 2A C6   LDA $c62a,y       ; V1 toggle base
    $C58D: 8D 52 C5   STA $c552
    $C590: B9 31 C6   LDA $c631,y       ; V2 toggle base
    $C593: 8D 53 C5   STA $c553
    $C596: A2 00      LDX #$00
L_C598:
    ; Copy 14 bytes of initial SID values from descriptor into
    ; $D400..$D40D. This sets both V1 + V2's freq/pw/ctrl/AD/SR.
    $C598: B9 26 C6   LDA $c626,y
    $C59B: 9D 00 D4   STA $d400,x       ;V1/V2 register block
    $C59E: C8         INY
    $C59F: E8         INX
    $C5A0: E0 0E      CPX #$0e          ; 14 bytes (V1 + V2 full block)
    $C5A2: D0 F4      BNE $c598        ; → L_C598
    ; Pick which "main loop continuation" address to drop into $C3FE
    ; based on bits 4-5 of the ch mask. This is the "return target
    ; patch" the comment at the JSR above was hinting at: the SFX
    ; trigger rewrites $C3FE so the actual SFX-tick path runs through
    ; the right voice-specific code on subsequent frames.
    $C5A4: AD 54 C5   LDA $c554
    $C5A7: 29 30      AND #$30
    $C5A9: A0 EE      LDY #$ee
    $C5AB: C9 20      CMP #$20
    $C5AD: F0 02      BEQ $c5b1        ; → L_C5B1
    $C5AF: A0 CE      LDY #$ce
L_C5B1:
    $C5B1: 8C FE C3   STY $c3fe         ; self-modify: patch SFX entry
    $C5B4: 60         RTS
; ----- data gap $C5B5-$CF56 (2466 bytes) -----
; $C5B5-$C624 = instrument table (8 bytes × ~14 instruments).
; $C625-$C724 = SFX descriptor table (16 bytes × 16 entries).
; $C725-$C72A = runtime per-voice orderlist pointers (copied by $CF57).
; $C72B-$CF56 = per-subtune orderlist-ptr packs + orderlist data +
;               pattern pointer tables ($C737/$C769) + pattern bytes.

; ======= Music init (jumped to via $C000 from the main init at $CFB5) =======
; Entry: A = music subtune index (0 or 1). $C54C was already set to $FF
; (music mode) by the dispatcher in $CFB5.
;
; This routine:
;   1. Reads per-subtune tick reload from $C537,X → $C53B.
;   2. Copies the 6-byte orderlist-ptr pack at $C72B + subtune*6 into
;      the runtime slots at $C725..$C72A.
;   3. Silences all three SID voices, sets vol = $0F.
;   4. Stamps $C53D = $40 (first-frame sentinel, bit 6) so the first
;      play frame takes the per-voice-state-zeroing path at $C02A.
L_CF57:
    $CF57: A0 00      LDY #$00
    $CF59: AA         TAX               ; X = subtune (0 or 1)
    $CF5A: BD 37 C5   LDA $c537,x       ; speed table[subtune]
    $CF5D: 8D 3B C5   STA $c53b         ; $C53B = per-voice tick reload
    ; X = subtune * 6 (6-byte stride per subtune in the orderlist pack).
    $CF60: 8A         TXA
    $CF61: 0A         ASL a             ; * 2
    $CF62: 8D 24 C5   STA $c524
    $CF65: 0A         ASL a             ; * 4
    $CF66: 18         CLC
    $CF67: 6D 24 C5   ADC $c524         ; *2 + *4 = *6
    $CF6A: AA         TAX
L_CF6B:
    ; Copy 6 bytes (V1 lo, V2 lo, V3 lo, V1 hi, V2 hi, V3 hi).
    $CF6B: BD 2B C7   LDA $c72b,x
    $CF6E: 99 25 C7   STA $c725,y
    $CF71: E8         INX
    $CF72: C8         INY
    $CF73: C0 06      CPY #$06
    $CF75: D0 F4      BNE $cf6b        ; → L_CF6B
    $CF77: A9 00      LDA #$00
    $CF79: 8D 04 D4   STA $d404         ;V1_CTRL = 0
    $CF7C: 8D 0B D4   STA $d40b         ;V2_CTRL = 0
    $CF7F: 8D 12 D4   STA $d412         ;V3_CTRL = 0
    $CF82: A9 0F      LDA #$0f
    $CF84: 8D 18 D4   STA $d418         ;VOL = $0F
    $CF87: A9 40      LDA #$40
    $CF89: 8D 3D C5   STA $c53d         ; first-frame sentinel
    $CF8C: 60         RTS
; ======= Song-end marker ($FD handler) =======
; Called from $C0B7 via $C003 trampoline when orderlist hits $FD.
; Sets $C53D = $C0 (bit 7 + bit 6) → next $C020 takes the BMI path,
; then BVC not taken → falls through to the silence + $C53D = $80
; path at $C048. Future frames stay end-of-song with bit 6 clear.
L_CF8D:
    $CF8D: A9 C0      LDA #$c0          ; end-of-song + first-frame bits
    $CF8F: 8D 3D C5   STA $c53d
    $CF92: 60         RTS
; ----- data gap $CF93-$CFA0 (14 bytes) -----

; ======= SFX trigger ($CFA1) =======
; Called from the main init dispatcher when A = sfx_index (subtune-2).
; If a higher-priority SFX is already playing on channel A ($C54A),
; the new SFX goes to channel B ($C54B). Else it goes straight into
; channel B (the typical/only path) with bit 6 ("needs init") set so
; the next play frame runs $C555 to load the descriptor.
L_CFA1:
    $CFA1: AE 4A C5   LDX $c54a         ; SFX channel A pointer
    $CFA4: F0 04      BEQ $cfaa        ; → L_CFAA   ; A empty: store into B
    $CFA6: 8E 4B C5   STX $c54b         ; A active: copy old A into B
    $CFA9: 60         RTS               ; (then fall back to L_CFAA path on next call)
L_CFAA:
    $CFAA: 09 40      ORA #$40          ; mark "needs init" (bit 6)
    $CFAC: 8D 4B C5   STA $c54b         ; SFX channel B = sfx_idx | $40
    $CFAF: A9 0F      LDA #$0f
    $CFB1: 8D 18 D4   STA $d418         ;VOL = $0F (revive in case it was zeroed)
    $CFB4: 60         RTS
; ======= init: =======
; Entry: A = subtune index (0-indexed). PSID startSong=1 → sidplayfp
; passes A=0 here for the title music; A=1 selects the second music
; track; A=2..17 trigger SFX 0..15.
;
; The split at "A < 2 → music, A >= 2 → SFX" is hardcoded; the music
; subtunes share one engine setup ($CF57) parameterised by A=0/1,
; while the SFX trigger ($CFA1) takes A-$02 as the SFX index.
init:
    $CFB5: C9 02      CMP #$02
    $CFB7: B0 08      BCS $cfc1        ; → L_CFC1   ; A >= 2: SFX path
    ; Music path: set music-mode flag and jump to the music setup.
    $CFB9: A0 FF      LDY #$ff
    $CFBB: 8C 4C C5   STY $c54c         ; $C54C = $FF (music mode)
    $CFBE: 4C 00 C0   JMP $c000        ; → L_C000   ; (= JMP $CF57)
L_CFC1:
    ; SFX path: convert A from "subtune number" to "sfx index" by
    ; subtracting 2, then JSR through the $C00F trampoline to $CFA1.
    ; (The CPY/CMP bytes after the JSR are post-RTS fall-through; the
    ; JSR'd routine RTSs to the caller, not back here.)
    $CFC1: 38         SEC
    $CFC2: E9 02      SBC #$02          ; sfx_idx = subtune - 2
    $CFC4: 20 0F      JSR $c00f        ; → sub_C00F (= JMP $CFA1)
    $CFC6: C0 4C      CPY #$4c          ; (unreachable after JSR returns)
; ----- data gap $CFC8-$CFC9 (2 bytes) -----

