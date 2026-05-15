; ============================================================================
; Rob Hubbard - Confuzion (1985 Incentive)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: data/C64Music/MUSICIANS/H/Hubbard_Rob/Confuzion.sid
; Load:   $0858   Init: $0867   Play: $0858
; PSID:   1 subtune(s), default subtune 1
; Binary: $0858-$11A5 (2382 bytes)
;
; Auto-traced 269 reachable code bytes from init+play, then hand-annotated by
; static reading.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; The engine is a "Hubbard-class" player in the same family as Action Biker
; (note byte flags, freq table indexed by pitch*2, 8-byte instrument records,
; hardcoded $08/$0E PWM bounds, per-voice tick gate). The key Confuzion-only
; trick is that the player was originally a raster IRQ handler — init does
; *self-modifying patching* to convert it into a callable PSID play routine.
;
; init ($0867):
;   1. LDX #$60  — load $60 (which is the 6502 opcode for RTS) into X.
;      This single LDX byte sequence ($A2 $60) overlaps the operand of the
;      preceding play's `STA $a2; RTS` at $0866-$0868 (Hubbard space trick).
;   2. STX $089C, STX $08C2, STX $0AFA  — patch three CLI/JMP sites with RTS:
;        - $089C was `58 CLI` at end of init → becomes `60 RTS`
;        - $08C2 was `58 CLI` at end of song-end handler → `60 RTS`
;        - $0AFA was `4C 81 EA  JMP $EA81` (KERNAL IRQ exit) → `60 81 EA`,
;          where the leading $60 RTS terminates execution immediately.
;   3. LDA #$EA / STA $08B9  — patch SEI in song-end handler with NOP ($EA).
;   4. Zero voice state arrays $0BC1,X $0BC4,X $0BC7,X $0BD0,X for X=2..0.
;   5. STX $0BEB (X=0 after loop) — set song-running flag to 0.
;   6. JSR sub_08A3 — silence all SID voices.
;   7. CLI ; RTS — but the CLI was just patched to RTS, so this is RTS;RTS.
;
;   The `BEQ L_0887` at $087E is unconditionally taken: the preceding
;   `LDA #$00 / STA $085C` leaves Z=1 (STA doesn't touch flags). So the
;   alternate raster-IRQ entry at $0880 (SEI / LDX #$02 / LDA #$00 /
;   STA $A2) is dead code in the PSID flow — it's a vestige of the
;   pre-PSID raster-driven version.
;
; play ($0858): every frame.
;   1. Save $A2, write $A2 = (the immediate byte at $085C). The byte at
;      $085C is incremented by `INC $085C` at the end of play, so $A2
;      receives a *self-modifying frame counter* (0, 1, 2, ... wrapping at
;      255). This is the input to the triangle-LFO vibrato in the effects
;      loop. After JSR sub_08CB returns, restore the original $A2.
;   2. JSR sub_08CB — main per-voice loop (described below).
;   3. INC $085C — bump the self-modifying frame counter for next call.
;
; sub_08CB (main per-voice loop):
;   - LDA $0BEB  — song-running flag. If 0 (song ended), JMP $0AFA = RTS.
;   - X = 2 (start with V3, work down to V1).
;   - DEC $0BE8 — per-frame tick counter. If goes negative, reload from
;     $0BE9 (tick reload value, e.g. $02 for speed 2).
;   - L_08E0 (per-voice section):
;       LDA $0BBD,X → STA $0BC0 — voice SID base offset ($0BBD,$0BBE,$0BBF
;       hold $00/$07/$0E for V1/V2/V3 respectively, the SID register stride).
;       **Note-load gate:** LDA $0BE8; CMP $0BE9; BNE L_0904.
;         When the tick counter has just been reloaded ($0BE8 == $0BE9),
;         the note-load path runs; otherwise jump straight to effects.
;       LDA $0BF1,X → $FB ; LDA $0BF4,X → $FC — load this voice's
;       orderlist pointer (lo:hi) into zp pair $FB:$FC.
;       DEC $0BC7,X — note duration counter. If still >=0, JMP L_09E2
;       (sustain/HR path: keep current note, optionally kill gate).
;       Else (BMI L_0907) → L_0907 (load a new note).
;
; L_0907 (load new note for voice X):
;   - LDY $0BC1,X — current position in this voice's orderlist.
;   - LDA ($FB),Y — orderlist byte = pattern number, OR $FF (end of song).
;   - If $FF: zero $0BC7,X, $0BC1,X, $0BC4,X (reset this voice's state)
;     and JMP L_08B9 (song-end / mute handler). NOTE: there is no
;     orderlist loop — once any voice hits $FF the whole song stops.
;   - Else: TAY (pattern number → Y).
;     LDA $0BF7,Y → $FD ; LDA $0C15,Y → $FE  — pattern pointer table
;     (lo at $0BF7, hi at $0C15, both indexed by pattern number).
;     LDY $0BC4,X — row offset within the pattern.
;     LDA #$FF → $0BD6 — gate mask, defaults to $FF (preserve all bits).
;     LDA ($FD),Y → STA $0BCA,X  AND  STA $0BD7  — fetch row byte 0
;     (the note-command byte). $0BCA,X holds it for the sustain path,
;     $0BD7 is the working copy for flag tests.
;     AND #$1F → STA $0BC7,X  — bits 0-4 = duration in frames.
;     BIT $0BD7 ; BVS L_098B — bit 6 set = TIE (preserve old freq, only
;     update SR/AD/ctrl). Tied path also decrements $0BD6 from $FF to $FE
;     so the gate bit gets cleared in the ctrl write (re-trigger suppress).
;     INC $0BC4,X — advance past the command byte.
;     LDA $0BD7 ; BPL L_0968 — bit 7 set = NEW INSTRUMENT byte follows.
;       INY ; LDA ($FD),Y ; AND #$1F ; STA $0BD3,X — instrument index.
;       LDA #$A0; SEC; SBC $0BC2; CMP #$0F; BCC L_0962; LDA #$0F
;       L_0962: STA $D418 — master volume = clamp($A0 - $0BC2, $0F).
;       $0BC2 is the global "volume-down" offset; when 0, vol = $0F.
;       INC $0BC4,X — advance past the instrument byte.
;     L_0968: INY ; LDA ($FD),Y ; STA $0BD0,X  — pitch byte (semitone idx).
;       ASL A ; TAY — pitch * 2 = freq-table byte offset.
;       LDA $0AFD,Y → $0BD8 ; LDA $0AFE,Y — read 2-byte freq (lo,hi).
;       Write freq_hi to $D401,Y_voice and back up to $0BEC,X.
;       Write freq_lo to $D400,Y_voice (Y_voice = $0BC0 = SID base offset).
;       JMP L_098E.
;   - L_098B (tie path): DEC $0BD6 (gate mask $FF→$FE, suppress gate bit).
;   - L_098E (write instrument to SID — runs for new-note AND tie paths):
;       Y_voice = $0BC0 (SID base offset).
;       Instrument index in $0BD3,X. ASL ASL ASL = ×8 → X (now byte offset
;       into instrument table at $1146).
;       LDA $1148,X = ctrl ; STA $0BDA (backup).
;       LDA $1148,X again; AND $0BD6 (gate mask); STA $D404,Y_voice.
;       LDA $1146,X = pulse_lo ; STA $D402,Y_voice.
;       LDA $1147,X = pulse_hi ; STA $D403,Y_voice.
;       LDA $1149,X = AD ; STA $D405,Y_voice.
;       LDA $114A,X = SR ; STA $D406,Y_voice.
;       Restore X (voice) from $0BD9; STA $0BDA → $0BCD,X
;       (= stored ctrl for sustain HR path).
;       INC $0BC4,X (advance past pitch byte).
;       Check next byte: if ($FD),Y == $FF, this row was end of pattern:
;       reset $0BC4,X = 0 (row 0) AND INC $0BC1,X (next orderlist entry).
;       JMP L_0AF4 → next voice.
;
;   INSTRUMENT TABLE LAYOUT at $1146, 8 bytes per record (×8 index):
;     +0 pulse_lo   +1 pulse_hi   +2 ctrl   +3 AD   +4 SR
;     +5 vib_depth  +6 PWM packed (E0=step, 1F=speed)   +7 vib_speed
;   (Note Y-displacements: +2 in code = "ctrl" since base load is $1146+X
;   then +0/+1 for pulse, etc. In effects loop the same record is
;   re-indexed by Y so $114B,Y / $114C,Y / $114D,Y read +5 / +6 / +7.)
;
;   ROW LAYOUT (variable length, terminated by $FF as the byte AFTER
;   the last consumed pitch byte):
;     byte 0: command (bit 7=new_inst, bit 6=tie, bit 5=no_release,
;             bits 0-4=duration)
;     byte 1: instrument index (if bit 7 set)
;     byte N: pitch index (always present unless tie)
;
; L_09E2 (sustain / hard-restart path — runs every frame the note holds):
;   - LDY $0BC0 (voice SID base).
;   - LDA $0BCA,X; AND #$20 — bit 5 = no_release; if set → JMP L_0A01
;     (skip gate kill; just run effects).
;   - LDA $0BC7,X — duration counter; if non-zero → JMP L_0A01 (still in
;     note body; just run effects).
;   - Otherwise we're at the END of the note duration with release enabled:
;     LDA $0BCD,X (stored ctrl); AND #$FE; STA $D404,Y — clear gate bit.
;     LDA #$00; STA $D405,Y; STA $D406,Y — kill AD and SR (immediate
;     silence rather than a release tail — this is the "Hubbard HR"
;     pattern at threshold = 0 for Confuzion). Fall through to L_0A01.
;
; L_0A01 (effects loop — vibrato/portamento + PWM):
;   - LDA $0BD3,X (instrument); ASL ASL ASL = ×8 → TAY (Y = instrument
;     byte offset).
;   - STY $0BEA — remember offset.
;   - LDA $114D,Y → $0BEF  (vib_speed)
;   - LDA $114C,Y → $0BDC  (PWM packed; will also branch-skip the
;                            vibrato block if this is zero)
;   - LDA $114B,Y → $0BDB  (vib_depth shift count)
;   - BEQ L_0A8D — if vib_depth == 0, skip vibrato/portamento, go to PWM.
;   - **Triangle-LFO vibrato** from the play-level frame counter $A2:
;       LDA $A2 ; AND #$07 ; CMP #$04 ; BCC ; EOR #$07
;       — folds 0..7 to 0,1,2,3,3,2,1,0 (triangle wave, period 8).
;     STA $0BE1 (folded counter value).
;   - LDA $0BD0,X (pitch); ASL; TAY — pitch*2 freq-table offset.
;   - Compute freq delta = freq[pitch+1] - freq[pitch] (next semitone -
;     current), then arithmetic-right-shift by $0BDB (vib_depth) to
;     scale the per-frame slide step. Result in $0BDD:$0BDE.
;   - Base freq from freq[pitch] → $0BDF:$0BE0.
;   - LDA $0BCA,X ; AND #$1F ; CMP #$08 — if note's duration bits >= 8
;     (BCC skips), run the vibrato accumulator: loop Y' = $0BE1 times,
;     adding the delta into $0BDF:$0BE0 each iteration.
;   - L_0A7E: LDY $0BC0 (voice SID base); STA $D400,Y / $D401,Y —
;     write computed freq (lo:hi).
;
; L_0A8D (PWM block):
;   - LDA $0BDC; BEQ L_0AF4 — if PWM packed == 0, skip.
;   - LDY $0BEA (instrument byte offset).
;   - AND #$1F → PWM speed; DEC $0BE2,X (per-voice PWM speed counter).
;   - BPL L_0AF4 (not yet wrapped — skip this frame).
;   - STA $0BE2,X — reload counter from speed.
;   - LDA $0BDC; AND #$E0 → $0BF0 — PWM step (upper 3 bits, scaled by $20).
;   - LDA $0BE5,X — direction flag; BNE → DOWN branch.
;     UP path:
;       LDA $0BF0; CLC; ADC $1146,Y (pulse_lo); PHA;
;       LDA $1147,Y (pulse_hi); ADC #$00; AND #$0F; PHA;
;       CMP #$0E; BNE L_0ADD; INC $0BE5,X — at upper bound, flip direction.
;     DOWN path (L_0AC6):
;       SEC; LDA $1146,Y; SBC $0BF0; PHA;
;       LDA $1147,Y; SBC #$00; AND #$0F; PHA;
;       CMP #$08; BNE L_0ADD; DEC $0BE5,X — at lower bound, flip direction.
;   - L_0ADD: store back into instrument record (STA $1147,Y, STA $1146,Y)
;     AND into SID ($D402,X, $D403,X using voice SID base in X). Note the
;     UP/DOWN bounds $0E and $08 are HARDCODED (same as Action Biker,
;     reference_hubbard_pwm_bounds.md).
;
; L_0AF4: DEX; BMI L_0AFA (done all voices); else JMP L_08E0 (next voice).
; L_0AFA: originally `JMP $EA81` (KERNAL IRQ exit); after init's
;         self-modifying patch, this is `RTS` followed by garbage.
;
; sub_08A3: silence helper. X=$17; loop STA $D400,X / DEX / BPL — writes A
;   to all $D400-$D417 (A=0 from caller → SID volume + all voice regs 0).
;
; L_08B9 (song-end / mute): sets $0BEB = 0 (stops note processing on
;   subsequent calls) and $D418 = 0 (volume off). The SEI here was patched
;   to NOP and the trailing CLI to RTS by init.
;
; FREQ TABLE: $0AFD, 192 bytes = 96 entries × (lo, hi) little-endian.
;             pitch byte * 2 = byte offset.
; INSTRUMENT TABLE: $1146, 8-byte records. Index field stored in $0BD3,X
;             is multiplied by 8 (ASL×3) to get byte offset.
; ORDERLIST POINTERS: $0BF1,X (lo) and $0BF4,X (hi) per voice — points to
;             the orderlist (sequence of pattern numbers, terminated $FF).
; PATTERN POINTER TABLE: $0BF7 (lo) and $0C15 (hi), indexed by pattern num.
; VOICE STATE ARRAYS (X = voice 0/1/2):
;   $0BBD,X  voice SID base offset ($00/$07/$0E)
;   $0BC1,X  orderlist position
;   $0BC4,X  current pattern row offset
;   $0BC7,X  remaining duration of current note (decremented per frame)
;   $0BCA,X  last command byte (for HR/no-release/tie/duration bits)
;   $0BCD,X  stored ctrl (for HR gate kill)
;   $0BD0,X  current pitch index
;   $0BD3,X  current instrument index
;   $0BE2,X  PWM speed counter
;   $0BE5,X  PWM direction flag
;   $0BEC,X  freq_hi backup (set on new note)
; GLOBALS:
;   $085C    self-modifying frame counter (immediate operand byte of play)
;   $0BC0    current voice's SID base offset (scratch within sub_08CB)
;   $0BC2    global "volume-down" offset (master vol = clamp($A0-$0BC2,$0F))
;   $0BE8/$0BE9  tick counter / reload (speed)
;   $0BEB    song-running flag (0 = stopped)
;   $0BF0    scratch for PWM step
;
; ============================================================================

; ======= play: =======
; Called every frame by sidplayfp.
play:
    ; Save $A2, then load A from the immediate operand at $085C. INC $085C
    ; below makes this byte tick 0,1,2,... so $A2 carries a per-call frame
    ; counter used by the triangle-LFO vibrato in sub_08CB's effects loop.
    $0858: A5 A2       LDA $a2
    $085A: 48          PHA
    $085B: A9 00       LDA #$00       ; <-- the $00 byte at $085C is the counter
    $085D: 85 A2       STA $a2
    $085F: 20 CB 08    JSR sub_08CB      ; -> sub_08CB   ; per-voice play loop
    $0862: EE 5C 08    INC $085c      ; bump self-modifying frame counter
    $0865: 68          PLA
    $0866: 85 A2       STA $a2        ; restore caller's $A2
    ; The RTS at $0868 is also the OPERAND byte of init's `LDX #$60` ($A2 $60).
    ; Init enters at $0867 — its first byte ($A2) is this STA's opcode-byte
    ; sibling. This is a deliberate Hubbard space trick.
; ----- entry-point overlap: re-decoding from $0867 (byte was operand of previous insn) -----
; ======= init: =======
; A holds subtune (0-indexed, from sidplayfp). ALL setup is done here in a
; *self-modifying* sequence that patches three CLI/JMP/SEI sites elsewhere
; in the binary, converting the original raster-IRQ-driven player into a
; PSID-callable subroutine. X is loaded with $60 (= RTS opcode) and used
; as the patch byte.
init:
    $0867: A2 60       LDX #$60       ; X = $60 (the 6502 opcode for RTS)
; ----- entry-point overlap: re-decoding from $0868 (byte was operand of previous insn) -----
    $0868: 60          RTS            ; ($68 also serves as init's RTS literal)
    $0869: 8E 9C 08    STX $089c      ; patch: CLI at $089C → RTS
    $086C: 8E FA 0A    STX $0afa      ; patch: `JMP $EA81` opcode → RTS (early-out)
    $086F: A9 EA       LDA #$ea       ; A = $EA (the 6502 opcode for NOP)
    $0871: 8D B9 08    STA $08b9      ; patch: SEI at $08B9 → NOP
    $0874: 8E C2 08    STX $08c2      ; patch: CLI at $08C2 → RTS
    $0877: A2 02       LDX #$02       ; voice index counter for state-zero loop
    $0879: A9 00       LDA #$00
    $087B: 8D 5C 08    STA $085c      ; reset self-modifying frame counter
    $087E: F0 07       BEQ L_0887      ; -> L_0887   ; ALWAYS taken (Z=1 from LDA #$00)
    ; --- dead code in the PSID flow: original raster-IRQ alt entry ---
    $0880: 78          SEI
    $0881: A2 02       LDX #$02
    $0883: A9 00       LDA #$00
    $0885: 85 A2       STA $a2
L_0887:
    ; Zero per-voice state for X = 2,1,0: $0BC1,X (orderlist pos),
    ; $0BC4,X (pattern row), $0BC7,X (note duration), $0BD0,X (pitch).
    $0887: 9D C1 0B    STA $0bc1,X
    $088A: 9D C4 0B    STA $0bc4,X
    $088D: 9D C7 0B    STA $0bc7,X
    $0890: 9D D0 0B    STA $0bd0,X
    $0893: CA          DEX
    $0894: 10 F1       BPL L_0887      ; -> L_0887
    $0896: 8E EB 0B    STX $0beb      ; X = $FF after BPL exit; STX writes $FF
                                        ; — but $0BEB is normally 0/1 for
                                        ; song-running. (This may be a bug or
                                        ; the song-start sets it via another
                                        ; path; effects of $FF != 0 means
                                        ; sub_08CB skips early-out and runs.)
    $0899: 20 A3 08    JSR sub_08A3      ; -> sub_08A3   ; silence SID ($D400-$D417 ← A=0)
    $089C: 58          CLI            ; PATCHED → RTS by init
    $089D: 60          RTS            ; (now unreachable; the CLI patch above is the real RTS)
; ----- data gap $089E-$08A2 (5 bytes) -----
; sub_08A3: silence all SID registers $D400-$D417 with A (caller passes A=0).
sub_08A3:
    $08A3: A2 17       LDX #$17       ; loop from $17 down to 0
L_08A5:
    $08A5: 9D 00 D4    STA $d400,X
    $08A8: CA          DEX
    $08A9: 10 FA       BPL L_08A5      ; -> L_08A5
    $08AB: 60          RTS
; ----- data gap $08AC-$08B8 (13 bytes) -----
; L_08B9: song-end / mute handler. Entered when any voice's orderlist hits
; $FF. Originally an IRQ block (SEI...CLI), patched by init to plain stores.
L_08B9:
    $08B9: 78          SEI            ; PATCHED → NOP by init
    $08BA: A9 00       LDA #$00
    $08BC: 8D EB 0B    STA $0beb      ; song-running flag = 0 (sub_08CB early-outs hereafter)
    $08BF: 8D 18 D4    STA $d418      ; SID master volume = 0
    $08C2: 58          CLI            ; PATCHED → RTS by init (terminates here)
    $08C3: 4C FA 0A    JMP L_0AFA      ; -> L_0AFA   ; (unreachable after patch)
; ----- data gap $08C6-$08CA (5 bytes) -----
; ======= sub_08CB: per-frame main loop =======
; Iterates voices V3→V1, advancing tick counters, loading new notes when
; the tick gate fires, running effects each frame.
sub_08CB:
    ; Song-running gate. After song-end, $0BEB = 0 and we exit early.
    $08CB: AD EB 0B    LDA $0beb
    $08CE: D0 03       BNE L_08D3      ; -> L_08D3
    $08D0: 4C FA 0A    JMP L_0AFA      ; -> L_0AFA   ; song stopped → RTS (post-patch)
L_08D3:
    ; Tick divider. $0BE8 decrements every frame; when it goes negative,
    ; reload from $0BE9 (the "speed" reload value). The note-load gate at
    ; $08E7 fires the frame AFTER reload, i.e. once every ($0BE9 + 2) frames.
    $08D3: A2 02       LDX #$02       ; X = 2 (start with V3, walk down to V1)
    $08D5: CE E8 0B    DEC $0be8
    $08D8: 10 06       BPL L_08E0      ; -> L_08E0
    $08DA: AD E9 0B    LDA $0be9
    $08DD: 8D E8 0B    STA $0be8      ; reload tick counter
L_08E0:
    ; Per-voice section entry. X = current voice (2/1/0).
    ; $0BBD,X is the voice's SID register base offset ($00/$07/$0E).
    $08E0: BD BD 0B    LDA $0bbd,X
    $08E3: 8D C0 0B    STA $0bc0      ; stash voice SID base in $0BC0
    $08E6: A8          TAY            ; (Y = SID base, used implicitly later)
    ; Note-load gate: only fire on the frame the tick was just reloaded.
    $08E7: AD E8 0B    LDA $0be8
    $08EA: CD E9 0B    CMP $0be9
    $08ED: D0 15       BNE L_0904      ; -> L_0904   ; not on the tick → effects-only
    ; Tick frame: load this voice's orderlist pointer into zp $FB:$FC.
    $08EF: BD F1 0B    LDA $0bf1,X    ; orderlist lo
    $08F2: 85 FB       STA $fb
    $08F4: BD F4 0B    LDA $0bf4,X    ; orderlist hi
    $08F7: 85 FC       STA $fc
    ; Note duration counter. If still >=0, sustain (jump to HR/effects path).
    ; If just went negative ($FF/BMI), load a new note at L_0907.
    $08F9: DE C7 0B    DEC $0bc7,X
    $08FC: 30 09       BMI L_0907      ; -> L_0907   ; duration ended → new note
    $08FE: 4C E2 09    JMP L_09E2      ; -> L_09E2   ; still sustaining → HR/effects
; ----- data gap $0901-$0903 (3 bytes) -----
L_0904:
    ; Off-tick frame: skip note-load entirely; go straight to effects.
    $0904: 4C 01 0A    JMP L_0A01      ; -> L_0A01
L_0907:
    ; New-note load path. Read the next orderlist byte = pattern number.
    $0907: BC C1 0B    LDY $0bc1,X    ; Y = orderlist position
    $090A: B1 FB       LDA ($fb),Y    ; pattern number (or $FF = end of song)
    $090C: C9 FF       CMP #$ff
    $090E: D0 11       BNE L_0921      ; -> L_0921   ; got a real pattern → load it
    ; Orderlist ended ($FF). Reset voice state and trigger song-end mute.
    ; NOTE: no orderlist looping — first voice to hit $FF stops the whole song.
    $0910: A9 00       LDA #$00
    $0912: 9D C7 0B    STA $0bc7,X
    $0915: 9D C1 0B    STA $0bc1,X
    $0918: 9D C4 0B    STA $0bc4,X
    $091B: 4C B9 08    JMP L_08B9      ; -> L_08B9   ; song-end / mute
; ----- data gap $091E-$0920 (3 bytes) -----
L_0921:
    ; Pattern number (in A) → pattern pointer pair in $FD:$FE.
    $0921: A8          TAY
    $0922: B9 F7 0B    LDA $0bf7,Y    ; pattern_lo[pattern]
    $0925: 85 FD       STA $fd
    $0927: B9 15 0C    LDA $0c15,Y    ; pattern_hi[pattern]
    $092A: 85 FE       STA $fe
    ; Read row byte 0 = command byte. Bit layout:
    ;   bit 7 = new-instrument byte follows
    ;   bit 6 = tie (preserve old pitch/instrument; suppress gate retrigger)
    ;   bit 5 = no_release (gate stays asserted at end of duration)
    ;   bits 0-4 = duration in frames
    $092C: BC C4 0B    LDY $0bc4,X    ; Y = row offset within pattern
    $092F: A9 FF       LDA #$ff
    $0931: 8D D6 0B    STA $0bd6      ; gate mask = $FF (preserve all ctrl bits)
    $0934: B1 FD       LDA ($fd),Y    ; row[0] = command byte
    $0936: 9D CA 0B    STA $0bca,X    ; remember for sustain/HR path
    $0939: 8D D7 0B    STA $0bd7      ; working copy for flag tests
    $093C: 29 1F       AND #$1f
    $093E: 9D C7 0B    STA $0bc7,X    ; duration counter = bits 0-4
    $0941: 2C D7 0B    BIT $0bd7
    $0944: 70 45       BVS L_098B      ; -> L_098B   ; bit 6 set = TIE → no new pitch/inst
    $0946: FE C4 0B    INC $0bc4,X    ; advance past command byte
    $0949: AD D7 0B    LDA $0bd7
    $094C: 10 1A       BPL L_0968      ; -> L_0968   ; bit 7 clear → no new instrument
    ; New-instrument path: row[1] = instrument index.
    $094E: C8          INY
    $094F: B1 FD       LDA ($fd),Y
    $0951: 29 1F       AND #$1f       ; mask to 5 bits (32 instruments max)
    $0953: 9D D3 0B    STA $0bd3,X
    ; Master volume = clamp($A0 - $0BC2, max $0F). $0BC2 = global fade-down.
    $0956: A9 A0       LDA #$a0
    $0958: 38          SEC
    $0959: ED C2 0B    SBC $0bc2
    $095C: C9 0F       CMP #$0f
    $095E: 90 02       BCC L_0962      ; -> L_0962
    $0960: A9 0F       LDA #$0f
L_0962:
    $0962: 8D 18 D4    STA $d418
    $0965: FE C4 0B    INC $0bc4,X    ; advance past instrument byte
L_0968:
    ; Pitch byte. ASL gives byte offset into the 96-entry, 2-byte-stride
    ; freq table at $0AFD.
    $0968: C8          INY
    $0969: B1 FD       LDA ($fd),Y
    $096B: 9D D0 0B    STA $0bd0,X    ; remember pitch index for effects
    $096E: 0A          ASL A
    $096F: A8          TAY            ; Y = pitch * 2
    $0970: B9 FD 0A    LDA $0afd,Y    ; freq_lo
    $0973: 8D D8 0B    STA $0bd8      ; (temp slot)
    $0976: B9 FE 0A    LDA $0afe,Y    ; freq_hi
    $0979: AC C0 0B    LDY $0bc0      ; Y = voice SID base offset
    $097C: 99 01 D4    STA $d401,Y    ; SID freq_hi
    $097F: 9D EC 0B    STA $0bec,X    ; backup freq_hi
    $0982: AD D8 0B    LDA $0bd8
    $0985: 99 00 D4    STA $d400,Y    ; SID freq_lo
    $0988: 4C 8E 09    JMP L_098E      ; -> L_098E
L_098B:
    ; Tie path: clear bit 0 of the gate mask so the ctrl write at $09A4
    ; below has its gate bit zeroed (no retrigger).
    $098B: CE D6 0B    DEC $0bd6      ; $FF → $FE
L_098E:
    ; Write instrument's ctrl/AD/SR/pulse to SID. Instrument record is at
    ; $1146 + (instrument_index * 8); we shift X left 3 times to get the
    ; byte offset and re-base reads at $1146,X / $1147,X / $1148,X / etc.
    $098E: AC C0 0B    LDY $0bc0      ; Y = voice SID base
    $0991: BD D3 0B    LDA $0bd3,X    ; A = instrument index
    $0994: 8E D9 0B    STX $0bd9      ; save voice index (X will be repurposed)
    $0997: 0A          ASL A          ; ×2
    $0998: 0A          ASL A          ; ×4
    $0999: 0A          ASL A          ; ×8 → byte offset into instrument table
    $099A: AA          TAX
    $099B: BD 48 11    LDA $1148,X    ; instrument +2 = ctrl
    $099E: 8D DA 0B    STA $0bda      ; backup raw ctrl (for $0BCD,X later)
    $09A1: BD 48 11    LDA $1148,X
    $09A4: 2D D6 0B    AND $0bd6      ; apply gate mask ($FF normal, $FE on tie)
    $09A7: 99 04 D4    STA $d404,Y    ; SID ctrl
    $09AA: BD 46 11    LDA $1146,X    ; instrument +0 = pulse_lo
    $09AD: 99 02 D4    STA $d402,Y
    $09B0: BD 47 11    LDA $1147,X    ; instrument +1 = pulse_hi
    $09B3: 99 03 D4    STA $d403,Y
    $09B6: BD 49 11    LDA $1149,X    ; instrument +3 = AD
    $09B9: 99 05 D4    STA $d405,Y
    $09BC: BD 4A 11    LDA $114a,X    ; instrument +4 = SR
    $09BF: 99 06 D4    STA $d406,Y
    $09C2: AE D9 0B    LDX $0bd9      ; restore voice index
    $09C5: AD DA 0B    LDA $0bda
    $09C8: 9D CD 0B    STA $0bcd,X    ; remember raw ctrl for HR gate-kill
    $09CB: FE C4 0B    INC $0bc4,X    ; advance past pitch byte
    ; End-of-pattern check: if the NEXT row byte is $FF, wrap to row 0 and
    ; advance the orderlist position.
    $09CE: BC C4 0B    LDY $0bc4,X
    $09D1: B1 FD       LDA ($fd),Y
    $09D3: C9 FF       CMP #$ff
    $09D5: D0 08       BNE L_09DF      ; -> L_09DF   ; still inside this pattern
    $09D7: A9 00       LDA #$00
    $09D9: 9D C4 0B    STA $0bc4,X    ; row offset = 0
    $09DC: FE C1 0B    INC $0bc1,X    ; next pattern in orderlist
L_09DF:
    $09DF: 4C F4 0A    JMP L_0AF4      ; -> L_0AF4   ; next voice (skip effects)
; ======= L_09E2: sustain / HR (hard-restart) path =======
; Runs every frame the note holds (i.e. when duration counter still >= 0).
L_09E2:
    $09E2: AC C0 0B    LDY $0bc0      ; Y = voice SID base
    $09E5: BD CA 0B    LDA $0bca,X    ; last command byte
    $09E8: 29 20       AND #$20
    $09EA: D0 15       BNE L_0A01      ; -> L_0A01   ; bit 5 set = no_release → skip gate kill
    $09EC: BD C7 0B    LDA $0bc7,X
    $09EF: D0 10       BNE L_0A01      ; -> L_0A01   ; still in duration body → no kill
    ; End of note duration with release enabled (HR threshold = 0):
    ; clear gate bit and zero envelope.
    $09F1: BD CD 0B    LDA $0bcd,X
    $09F4: 29 FE       AND #$fe       ; clear gate
    $09F6: 99 04 D4    STA $d404,Y
    $09F9: A9 00       LDA #$00
    $09FB: 99 05 D4    STA $d405,Y    ; AD = 0 (immediate cutoff)
    $09FE: 99 06 D4    STA $d406,Y    ; SR = 0
; ======= L_0A01: effects loop (vibrato/portamento + PWM) =======
L_0A01:
    ; Re-index instrument record for effects: Y = inst_index * 8.
    $0A01: BD D3 0B    LDA $0bd3,X
    $0A04: 0A          ASL A
    $0A05: 0A          ASL A
    $0A06: 0A          ASL A
    $0A07: A8          TAY
    $0A08: 8C EA 0B    STY $0bea      ; save inst byte offset for PWM block
    $0A0B: B9 4D 11    LDA $114d,Y    ; instrument +7 = vib speed
    $0A0E: 8D EF 0B    STA $0bef
    $0A11: B9 4C 11    LDA $114c,Y    ; instrument +6 = PWM packed (E0|1F)
    $0A14: 8D DC 0B    STA $0bdc
    $0A17: B9 4B 11    LDA $114b,Y    ; instrument +5 = vib depth (shift count)
    $0A1A: 8D DB 0B    STA $0bdb
    $0A1D: F0 6E       BEQ L_0A8D      ; -> L_0A8D   ; vib_depth==0 → skip to PWM
    ; Triangle-LFO from the per-call frame counter $A2:
    ;   x = $A2 & $07               # 0..7
    ;   if x >= 4: x = x ^ 7        # fold: 0,1,2,3,3,2,1,0 → triangle
    ; Period 8 frames, amplitude 0..3 (then scaled by inst delta below).
    $0A1F: A5 A2       LDA $a2
    $0A21: 29 07       AND #$07
    $0A23: C9 04       CMP #$04
    $0A25: 90 02       BCC L_0A29      ; -> L_0A29
    $0A27: 49 07       EOR #$07
L_0A29:
    $0A29: 8D E1 0B    STA $0be1      ; folded counter
    ; Compute vibrato delta = (freq[pitch+1] - freq[pitch]) >> vib_depth.
    ; The semitone-stride difference, arithmetic-right-shifted to make a
    ; small per-frame step. Result in $0BDE:$0BDD.
    $0A2C: BD D0 0B    LDA $0bd0,X
    $0A2F: 0A          ASL A
    $0A30: A8          TAY            ; Y = pitch*2 (freq table offset)
    $0A31: 38          SEC
    $0A32: B9 FF 0A    LDA $0aff,Y    ; freq[pitch+1].lo  ($0AFD+2*(pitch+1)+0 = $0AFF + 2*pitch)
    $0A35: F9 FD 0A    SBC $0afd,Y    ; - freq[pitch].lo
    $0A38: 8D DD 0B    STA $0bdd
    $0A3B: B9 00 0B    LDA $0b00,Y    ; freq[pitch+1].hi
    $0A3E: F9 FE 0A    SBC $0afe,Y    ; - freq[pitch].hi
L_0A41:
    ; Arithmetic right shift {A:$0BDD} by $0BDB+1 positions.
    $0A41: 4A          LSR A
    $0A42: 6E DD 0B    ROR $0bdd
    $0A45: CE DB 0B    DEC $0bdb
    $0A48: 10 F7       BPL L_0A41      ; -> L_0A41
    $0A4A: 8D DE 0B    STA $0bde      ; vib_delta_hi
    ; Base freq for the note (will be incremented by vib_delta * folded_count)
    $0A4D: B9 FD 0A    LDA $0afd,Y
    $0A50: 8D DF 0B    STA $0bdf      ; running freq_lo
    $0A53: B9 FE 0A    LDA $0afe,Y
    $0A56: 8D E0 0B    STA $0be0      ; running freq_hi
    ; Only apply vibrato AFTER the attack phase: when duration bits >= 8.
    ; (Short notes < 8 frames skip vibrato.)
    $0A59: BD CA 0B    LDA $0bca,X
    $0A5C: 29 1F       AND #$1f
    $0A5E: C9 08       CMP #$08
    $0A60: 90 1C       BCC L_0A7E      ; -> L_0A7E
    $0A62: AC E1 0B    LDY $0be1      ; Y = folded counter (0..3)
L_0A65:
    ; Accumulator loop: running_freq += vib_delta, repeated Y times.
    $0A65: 88          DEY
    $0A66: 30 16       BMI L_0A7E      ; -> L_0A7E
    $0A68: 18          CLC
    $0A69: AD DF 0B    LDA $0bdf
    $0A6C: 6D DD 0B    ADC $0bdd
    $0A6F: 8D DF 0B    STA $0bdf
    $0A72: AD E0 0B    LDA $0be0
    $0A75: 6D DE 0B    ADC $0bde
    $0A78: 8D E0 0B    STA $0be0
    $0A7B: 4C 65 0A    JMP L_0A65      ; -> L_0A65
L_0A7E:
    ; Write vibrato'd freq to SID for this voice.
    $0A7E: AC C0 0B    LDY $0bc0
    $0A81: AD DF 0B    LDA $0bdf
    $0A84: 99 00 D4    STA $d400,Y
    $0A87: AD E0 0B    LDA $0be0
    $0A8A: 99 01 D4    STA $d401,Y
; ======= L_0A8D: PWM block =======
; Bidirectional sweep of pulse width within HARDCODED bounds [$08, $0E]
; on the high nibble of pulse_hi. Direction flips at the boundaries.
L_0A8D:
    $0A8D: AD DC 0B    LDA $0bdc
    $0A90: F0 62       BEQ L_0AF4      ; -> L_0AF4   ; PWM packed = 0 → no PWM
    $0A92: AC EA 0B    LDY $0bea      ; Y = inst byte offset
    $0A95: 29 1F       AND #$1f       ; PWM speed = low 5 bits
    $0A97: DE E2 0B    DEC $0be2,X    ; per-voice speed counter
    $0A9A: 10 58       BPL L_0AF4      ; -> L_0AF4   ; not yet wrapped → skip this frame
    $0A9C: 9D E2 0B    STA $0be2,X    ; reload counter from speed
    $0A9F: AD DC 0B    LDA $0bdc
    $0AA2: 29 E0       AND #$e0       ; PWM step = upper 3 bits ($20/$40/$60/.../$E0)
    $0AA4: 8D F0 0B    STA $0bf0
    $0AA7: BD E5 0B    LDA $0be5,X    ; direction flag (0=up, !=0=down)
    $0AAA: D0 1A       BNE L_0AC6      ; -> L_0AC6
    ; UP path: pulse += $0BF0; clamp upper nibble of pulse_hi to <= $0E.
    $0AAC: AD F0 0B    LDA $0bf0
    $0AAF: 18          CLC
    $0AB0: 79 46 11    ADC $1146,Y    ; + pulse_lo
    $0AB3: 48          PHA
    $0AB4: B9 47 11    LDA $1147,Y    ; pulse_hi
    $0AB7: 69 00       ADC #$00
    $0AB9: 29 0F       AND #$0f       ; mask to 4 bits
    $0ABB: 48          PHA
    $0ABC: C9 0E       CMP #$0e       ; HARDCODED upper bound
    $0ABE: D0 1D       BNE L_0ADD      ; -> L_0ADD
    $0AC0: FE E5 0B    INC $0be5,X    ; reached $0E → flip to DOWN
    $0AC3: 4C DD 0A    JMP L_0ADD      ; -> L_0ADD
L_0AC6:
    ; DOWN path: pulse -= $0BF0; clamp upper nibble of pulse_hi to >= $08.
    $0AC6: 38          SEC
    $0AC7: B9 46 11    LDA $1146,Y    ; pulse_lo
    $0ACA: ED F0 0B    SBC $0bf0
    $0ACD: 48          PHA
    $0ACE: B9 47 11    LDA $1147,Y    ; pulse_hi
    $0AD1: E9 00       SBC #$00
    $0AD3: 29 0F       AND #$0f
    $0AD5: 48          PHA
    $0AD6: C9 08       CMP #$08       ; HARDCODED lower bound
    $0AD8: D0 03       BNE L_0ADD      ; -> L_0ADD
    $0ADA: DE E5 0B    DEC $0be5,X    ; reached $08 → flip to UP
L_0ADD:
    ; Write new pulse back to instrument record AND to SID. Note: pulse
    ; lives in the INSTRUMENT record (not in voice state), so all voices
    ; sharing this instrument get the swept pulse.
    $0ADD: 8E D9 0B    STX $0bd9      ; save voice index
    $0AE0: AE C0 0B    LDX $0bc0      ; X = voice SID base
    $0AE3: 68          PLA            ; pulled pulse_hi
    $0AE4: 99 47 11    STA $1147,Y
    $0AE7: 9D 03 D4    STA $d403,X
    $0AEA: 68          PLA            ; pulled pulse_lo
    $0AEB: 99 46 11    STA $1146,Y
    $0AEE: 9D 02 D4    STA $d402,X
    $0AF1: AE D9 0B    LDX $0bd9      ; restore voice index
L_0AF4:
    ; Next-voice / done.
    $0AF4: CA          DEX
    $0AF5: 30 03       BMI L_0AFA      ; -> L_0AFA
    $0AF7: 4C E0 08    JMP L_08E0      ; -> L_08E0
L_0AFA:
    ; Original raster-IRQ exit. Init patched the $4C opcode here to $60,
    ; so this reads as `RTS; $81; $EA` — RTS terminates execution.
    $0AFA: 4C 81 EA    JMP $ea81      ; -> $EA81   ; PATCHED → RTS
; ----- data section $0AFD-$11A5 (1705 bytes) -----
; $0AFD-$0BBC  freq table (96 entries × 2 bytes, lo:hi little-endian)
; $0BBD-$0BBF  voice SID base offsets ($00, $07, $0E for V1/V2/V3)
; $0BC0-$0BEC  scratch + per-voice state arrays (see header for layout)
; $0BF1-$0BF6  per-voice orderlist pointer pairs (lo:hi)
; $0BF7-$0C14  pattern pointer table (lo bytes)
; $0C15-$1145  pattern pointer table (hi bytes) + orderlists + patterns
; $1146-$11A5  instrument table (8-byte records ×N)
