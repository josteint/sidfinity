; ============================================================================
; Rob Hubbard - Crazy Comets (1985 Martech)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: data/C64Music/MUSICIANS/H/Hubbard_Rob/Crazy_Comets.sid
; Load:   $5000   Init: $6100   Play: $500C
; PSID:   17 subtunes, default subtune 1 (1-indexed; A=0 passed to init)
; Binary: $5000-$610F (4368 bytes)
;
; Auto-traced 490 reachable instructions from init+play.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; Crazy Comets ships TWO co-resident player engines in the same binary:
;
;   1. MUSIC engine (subtune 0-1)  - entry: $5000 trampoline → $60A7 setup.
;      Drives 3-voice tracker-style music with vibrato/PWM/drum/arpeggio.
;   2. SFX engine (subtune 2-16)   - entry: $5003+$5009 trampolines.
;      One-shot sound-effect descriptors at $562C+y*$10, V1/V2 only.
;
; They share the same play() at $500C (called every frame). The byte at
; $54FD is a state sentinel selecting which path runs this frame:
;   bit 7 set ($80) → silence everything, RTS  (panic / song-end)
;   bit 6 set ($40) → first-frame init path    (set by music init)
;   bit 6+7  ($C0)  → SFX-only path            (set by SFX init via $5003)
;   both clear      → normal music play
;
; ----------------------------------------------------------------------------
;
; init ($6100): A holds subtune (0-indexed). Dispatches by range:
;   A < 2  → JMP $5000 → JMP $60A7: copy 6 orderlist ptrs from $5732+A*6
;            to $572C, zero RES_FILT + voice ctrls, set vol $0F,
;            $54FD = $40. (Same role as Action Biker's $C28E first-frame
;            setup, but here it runs EAGERLY in init rather than deferred.)
;   A >= 2 → subtune index gets SBC #$02 (so SFX index 0..14), then:
;            JSR $5009 → JMP $60DE  ($550A = (sfx_idx)|$40, vol $0F)
;            JMP $5003 → JMP $60D8  ($54FD = $C0 → "SFX-only" sentinel)
;
; play ($500C): every frame.
;   1. INC $5509  (global frame counter).
;   2. BIT $54FD - bit 7 → JMP $5032 (panic-silence + set $54FD = $80);
;                  bit 6 → run first-frame init block at $5016 that zeros
;                  $54D3/$54D6/$54D9/$54E2 (v_olpos/v_patpos/v_dur/v_pitch)
;                  for X=2..0, clears $54FD, then JMP $5047 to start play.
;   3. Fall through (bit 6 cleared) to per-voice processing at $5047.
;
; PER-VOICE PROCESSING ($5047 .. $5390): X = 2, 1, 0 (V3, V2, V1).
;   - DEC $54FA (tick divider); reload from $54FB when negative.
;   - $54CF,X = SID voice offset (0/7/14); latched at $54D2 as Y-index.
;   - **Note-load gate** at $505E: load runs only when $54FA == $54FB
;     (the just-reloaded frame). Else BNE → $5078 → JMP $518D
;     (effects-only path, no pattern advance). Same shape as Action
;     Biker's $C040/$C043 gate.
;   - Note-load path ($507B-$5163): orderlist sentinels ($FF=loop,
;     $FE=song-end → JMP $5003 silence trampoline), pattern flags+dur
;     byte (bit 7=new-inst, bit 6=tie/legato, bit 5=no_release, bits
;     0-4=duration), optional inst byte, pitch byte. Pitch is doubled
;     (ASL) to index the freq table at $540F as 2-byte (lo, hi)
;     entries. The new-instrument path writes inst.ctrl/pw_lo/pw_hi/
;     AD/SR to SID; gated by $54E8 mask (DEC'd to $FE for tie → clears
;     gate bit).
;   - Sustain path ($516E-$518D): HR-threshold check (no_release flag
;     bit 5 clear AND v_dur == 0 → write ctrl-without-gate + AD=0 +
;     SR=0). Same shape as Action Biker.
;   - Effects loop ($518D-$5380):
;       VIBRATO  ($518D-$5222): triangle LFO from $5509 & $07 folded
;                via EOR #$07, sums shifted (freq[n+1]-freq[n]) into
;                base freq, LFO-count times. Skipped if dur < 8.
;       PWM      ($5222-$52A4): same hardcoded $08/$0E bounds as
;                Action Biker. NEW: $5222 path - if fx bit 3 set,
;                pw_lo gets += $54EE | $40 (no bounds, no direction);
;                otherwise normal $5240+ direction-flipping PWM.
;       ARPEGGIO ($52A7-$52EE): NEW vs Action Biker. $5504,X bit 0
;                picks ±direction, $54EB step amount applied to
;                $5501,X / $54FE,X (12-bit freq pair). Live SID writes.
;       DRUM     ($52EE-$5327): fx bit 0 = drum freq-slide. Same as
;                Action Biker's skydive: DEC v_fhi each frame.
;       FX-1     ($532A-$534F): NEW - bit 1 + dur >= $11 + (frame & 1)
;                + v_fhi != 0 → DEC v_fhi. Slow freq-down for short
;                tom-style sounds.
;       FX-2     ($534F-$5380): NEW - bit 2 + alternate frame → write
;                freq[pitch+0] or freq[pitch+12] (octave alternation,
;                a coarse arpeggio).
;   - Voice tail at $5380: write $550B = ($550A bit 7 ? $FF : $00).
;     $550B controls effects-loop SID writes ABOVE: every effect block
;     checks $550B with BPL before writing to SID. When SFX is active
;     ($550A bit 7 = "SFX-engine-end-or-init"), $550B = $00 → music
;     effects suppressed (SFX engine owns V1+V2). When SFX done,
;     $550B = $FF → music writes resume.
;   - DEX, BMI exit (X went below 0); else JMP $5054 (next voice).
;
; SFX ENGINE ($539B-$540C, with setup at $5514-$5573):
;   - $539B loop: clears $550B = $FF (initially "music suppressed";
;     overwritten at $5380 each music voice). On the FIRST SFX frame
;     (bit 6 of $550A still set) calls sub_5514 - which:
;       * zeros V1+V2 ctrl ($D404, $D40B)
;       * masks $550A to low 4 bits = sfx_idx, shifts ×16
;       * reads 8 bytes from $562C+sfx_idx*$10 descriptor table:
;           +0  $5513 flags byte (bit 5/4 = INC/DEC of patched $53C5)
;           +1  $550C step count + freq-table loop seed
;           +4  $5510 V1 ctrl XOR mask + low 6 bits → $550F detune
;           +5  $5511 V1 ctrl init
;           +B  $550E end value (descriptor offset $0F? - see $553B)
;           +B  $5512 V2 ctrl init
;       * copies 14 freq-table-shape bytes from descriptor to $D400+ to
;         "patch" the SID directly (initial sweep voicing).
;       * patches $53C5 opcode: $EE (INC) or $CE (DEC) selected by
;         bit 5/4 of $5513.
;   - $539B main: $550D sub-frame timer; when negative, reload from
;     $5513 & $0F. Compare $550C to $550E; if equal → silence V1/V2,
;     set $550A = $FF (SFX done, but keep bit 7 high → no longer "init").
;     Else step $550C (the patched INC/DEC); ASL → Y = $550C * 2.
;     Read freq pair at $540F + Y (V1) and $540F + (Y - $550F)*1 (V2,
;     with detuning offset). Toggle V1/V2 ctrl bits 0/1 via EOR #$01
;     of $5511 → $D404 and $5512 → $D40B (manual gate/wave toggling
;     each tick - characteristic Hubbard SFX "phaser" sound).
;
; FREQ TABLE: $540F, 96 semitones × 2 bytes = 192 bytes ($540F..$54CE).
; Same encoding as Action Biker's $C2FC.
;
; INSTRUMENT TABLE: $5574, 8-byte records.
;   offset 0: pw_lo  1: pw_hi  2: ctrl  3: AD  4: SR
;          5: vib_depth  6: vib_period  7: fx_flags
;   Same offsets as Action Biker's $CB5B.
;
; STATE BLOCK ($54CF-$5513) - mapping vs Action Biker ($C3BC-$C3F2):
;   $54CF,X  SID voice offset (0/7/14)        ← $C3BC,X
;   $54D2    SID offset latched as Y          ← $C3BF
;   $54D3,X  v_olpos                           ← $C3C0,X
;   $54D6,X  v_patpos                          ← $C3C3,X
;   $54D9,X  v_dur                             ← $C3C6,X
;   $54DC,X  v_flags (raw pattern byte)        ← $C3C9,X
;   $54DF,X  v_ctrl (saved inst.ctrl)          ← $C3CC,X
;   $54E2,X  v_pitch                           ← $C3CF,X
;   $54E5,X  v_inst                            ← $C3D2,X
;   $54E8    gate mask (FF normal, FE tie)     ← $C3D5
;   $54E9    pattern flags scratch             ← $C3D6
;   $54EA    freq_lo scratch                   ← $C3D7
;   $54EB    X-save scratch / arp step         ← $C3D8 (overloaded)
;   $54EC    inst.ctrl scratch                 ← $C3D9
;   $54ED    vib_depth                         ← $C3DA
;   $54EE    vib_period                        ← $C3DB
;   $54EF    delta_lo                          ← $C3DC
;   $54F0    delta_hi                          ← $C3DD
;   $54F1    vibrato base freq_lo              ← $C3DE
;   $54F2    vibrato base freq_hi              ← $C3DF
;   $54F3    LFO value (0-4)                   ← $C3E0
;   $54F4,X  pwm step counter                  ← $C3E1,X
;   $54F7,X  pwm direction flag                ← $C3E4,X
;   $54FA    tick divider                      ← $C3E7
;   $54FB    tick reload                       ← $C3E8
;   $54FC    inst byte offset (×8)             ← $C3E9
;   $54FD    music state sentinel              ← $C3EA
;   $54FE,X  v_fhi (current freq_hi)           ← $C3EB,X
;   $5501,X  v_freq_lo for arpeggio   (NEW)
;   $5504,X  arpeggio direction flags (NEW)
;   $5507    fx_flags scratch                  ← $C3EE
;   $5508    pwm step size scratch             ← $C3EF
;   $5509    global frame counter              ← $C3F0
;   $550A    SFX state sentinel       (NEW; SFX engine only)
;   $550B    "SFX active → mute music" mask    (NEW)
;   $550C    SFX step counter
;   $550D    SFX sub-frame timer
;   $550E    SFX end value
;   $550F    SFX V1-V2 detune offset
;   $5510    SFX V1 ctrl XOR mask
;   $5511    SFX V1 ctrl current
;   $5512    SFX V2 ctrl current
;   $5513    SFX flags byte
;
; CONSEQUENCE FOR OUR CODEGEN:
;   The current Lean codegen at pipelines/crazy_comets/codegen/CrazyComets/
;   was cloned from Commando/Action Biker and only handles the music path
;   (subtunes 0-1). The SFX engine ($539B-$540C, sub_5514) is NOT covered
;   - that's why only 3 PSID tracks ship even though there are 17.
;
;   Three music-only features absent from Action Biker that the codegen
;   needs to grow to match:
;     - ARPEGGIO at $52A7  ($5501,X / $5504,X / $54EB are NEW state)
;     - FX bit 1 freq-down at $532A
;     - FX bit 2 octave-arp at $534F
;
;   Unlike Action Biker, init does $60A7 setup EAGERLY rather than via
;   "$C28E one-time first-play setup". The music engine sets $54FD = $40
;   in init; on play frame 0 the BIT $54FD branch at $5012 takes BVC
;   FALSE → runs the $5016 zeroing block (idempotent w.r.t. init's work),
;   then falls through. So the "frame 0 vs frame 1" timing situation
;   from Action Biker is NOT necessarily present here - confirm against
;   siddump --writelog before assuming a 1-frame defer.
;
; ============================================================================

; ===== entry trampolines =====
; Three fixed dispatch points used by init and by song-end paths. They
; live at the start of the binary so the addresses are predictable across
; whatever code/data the rest of the binary contains.

; music_init_trampoline: subtune < 2 lands here from $6104 (init).
L_5000:
    $5000: 4C A7 60  JMP $60a7  ; → L_60A7   ; music engine setup
; sfx_setup_trampoline_b: second-stage SFX init (from $610D), also reached
; from $5084 when the orderlist hits the $FE song-end sentinel.
L_5003:
    $5003: 4C D8 60  JMP $60d8  ; → L_60D8   ; sets $54FD = $C0 (SFX-only)
; ----- data gap $5006-$5008 (3 bytes) -----

; sfx_setup_trampoline_a: first-stage SFX init (JSR'd from $610A).
sub_5009:
    $5009: 4C DE 60  JMP $60de  ; → L_60DE   ; sets $550A and vol $0F

; ======= play: =======
; Called every frame by sidplayfp.
play:
    ; Global frame counter ++. Used by vibrato LFO and the alternate-frame
    ; effect blocks (bit 0 / bit 0&7 reads).
    $500C: EE 09 55  INC $5509      ; frame counter += 1
    ; State sentinel $54FD: bit 7 = end-of-song, bit 6 = first-frame init.
    ; BIT moves bit 7 → N, bit 6 → V.
    $500F: 2C FD 54  BIT $54fd
    $5012: 30 1E     BMI $5032      ; → L_5032   ; bit 7: end-of-song path
    $5014: 50 31     BVC $5047      ; → L_5047   ; both clear: normal play
    ; bit 6 set (first-frame init): zero per-voice state for X=2..0, then
    ; clear $54FD so subsequent frames take the normal-play branch above.
    $5016: A9 00     LDA #$00
    $5018: 8D 09 55  STA $5509      ; frame counter = 0 (reset; just INC'd)
    $501B: A2 02     LDX #$02       ; X = 2..0 (V3, V2, V1)
L_501D:
    $501D: 9D D3 54  STA $54d3,x    ; v_olpos,X = 0
    $5020: 9D D6 54  STA $54d6,x    ; v_patpos,X = 0
    $5023: 9D D9 54  STA $54d9,x    ; v_dur,X = 0
    $5026: 9D E2 54  STA $54e2,x    ; v_pitch,X = 0
    $5029: CA        DEX
    $502A: 10 F1     BPL $501d      ; → L_501D
    $502C: 8D FD 54  STA $54fd      ; $54FD = $00 → never re-enter this block
    $502F: 4C 47 50  JMP $5047      ; → L_5047   ; fall through to play
; song-end / panic-silence path: $54FD bit 7 was set on entry.
; If bit 6 ALSO set (BVS-taken means bit-6 clear here) → just JMP to SFX
; engine. Otherwise: zero V1/V2/V3 ctrl (kill all voices) and set
; $54FD = $80 (lock end-of-song state), then fall into SFX engine via
; $5391 (which RTS's at $539B because $550A bit 6/7 are clear).
L_5032:
    $5032: 50 10     BVC $5044      ; → L_5044   ; bit 6 clear: silence
    $5034: A9 00     LDA #$00
    $5036: 8D 04 D4  STA $d404      ; V1_CTRL    ; kill V1
    $5039: 8D 0B D4  STA $d40b      ; V2_CTRL    ; kill V2
    $503C: 8D 12 D4  STA $d412      ; V3_CTRL    ; kill V3
    $503F: A9 80     LDA #$80
    $5041: 8D FD 54  STA $54fd      ; $54FD = $80 (lock end-of-song)
L_5044:
    $5044: 4C 91 53  JMP $5391      ; → L_5391   ; jump to SFX engine

; ===== per-voice loop entry =====
; X cycles V3 → V2 → V1 (2,1,0). At $5380 the loop tail will DEX/BMI exit.
L_5047:
    $5047: A2 02     LDX #$02       ; start with V3
    ; Tick divider: $54FA reloads from $54FB when negative.
    ; This is the same shape as Action Biker's $C3E7/$C3E8 counter,
    ; controlling the note-load gate at $505E below.
    $5049: CE FA 54  DEC $54fa
    $504C: 10 06     BPL $5054      ; → L_5054
    $504E: AD FB 54  LDA $54fb
    $5051: 8D FA 54  STA $54fa      ; $54FA = $54FB (reload)
; Per-voice SID-base lookup. $54CF,X = SID register offset (0/7/14)
; for V1/V2/V3 relative to $D400. Stash at $54D2 to use as Y-index.
L_5054:
    $5054: BD CF 54  LDA $54cf,x    ; SID voice offset (0,7,14)
    $5057: 8D D2 54  STA $54d2      ; latch as Y for later STA ,Y
    $505A: A8        TAY            ; Y = SID base offset (unused here;
                                    ;     overwritten before SID writes)
    ; **NOTE-LOAD GATE**: only run note-load when tick divider lands on
    ; reload value. On frames where $54FA hasn't cycled, take BNE to
    ; effects-only at $5078. Same pattern as Action Biker $C040-$C046.
    $505B: AD FA 54  LDA $54fa
    $505E: CD FB 54  CMP $54fb
    $5061: D0 15     BNE $5078      ; → L_5078   ; skip note-load
    ; Note-load path: orderlist pointer (lo/hi) from $572C,X / $572F,X
    ; into ZP $BB/$BC for indirect addressing.
    $5063: BD 2C 57  LDA $572c,x    ; orderlist ptr lo
    $5066: 85 BB     STA $bb
    $5068: BD 2F 57  LDA $572f,x    ; orderlist ptr hi
    $506B: 85 BC     STA $bc
    ; $54D9,X = duration countdown. DEC; if BMI (hit -1), load next note.
    ; Else fall through to sustain path at $5166.
    $506D: DE D9 54  DEC $54d9,x    ; v_dur,X
    $5070: 30 09     BMI $507b      ; → L_507B   ; expired: load next
    $5072: 4C 66 51  JMP $5166      ; → L_5166   ; sustain current
; ----- data gap $5075-$5077 (3 bytes) -----

; Effects-only path: this frame's note-load is gated off. Just runs the
; per-voice effects without advancing pattern data.
L_5078:
    $5078: 4C 8D 51  JMP $518d      ; → L_518D
; Note-load entry. Y = v_olpos,X; read orderlist[v_olpos].
;   $FE → song-end sentinel → JMP $5003 trampoline (silences via $60D8).
;   $FF → orderlist wrap → reset v_dur/v_olpos/v_patpos to 0 and retry.
;   else → pattern index → load pattern.
; Note this differs from Action Biker which used $FF for loop and $FE for
; song-end. Same meaning, but Crazy Comets's $5003 trampoline doesn't
; silence everything - it sets $54FD = $C0 to keep SFX engine ownership.
L_507B:
    $507B: BC D3 54  LDY $54d3,x    ; v_olpos,X
    $507E: B1 BB     LDA ($bb),y    ; orderlist[v_olpos]
    $5080: C9 FE     CMP #$fe       ; song-end sentinel
    $5082: D0 03     BNE $5087      ; → L_5087
    $5084: 4C 03 50  JMP $5003      ; → L_5003   ; song-end → SFX-only
L_5087:
    $5087: C9 FF     CMP #$ff       ; loop sentinel
    $5089: D0 11     BNE $509c      ; → L_509C   ; normal: load patt
    ; Restart orderlist (loop): zero v_dur, v_olpos, v_patpos and retry.
    $508B: A9 00     LDA #$00
    $508D: 9D D9 54  STA $54d9,x    ; v_dur,X = 0
    $5090: 9D D3 54  STA $54d3,x    ; v_olpos,X = 0
    $5093: 9D D6 54  STA $54d6,x    ; v_patpos,X = 0
    $5096: 4C 7B 50  JMP $507b      ; → L_507B   ; retry from start
; ----- data gap $5099-$509B (3 bytes) -----

; Normal pattern load: A = pattern index from orderlist. Look up pattern
; start address via (lo, hi) tables at $573E / $5773. Pattern address
; stored in ZP $BD/$BE for indirect addressing.
L_509C:
    $509C: A8        TAY            ; Y = pattern index
    $509D: B9 3E 57  LDA $573e,y    ; pat_lo[Y]
    $50A0: 85 BD     STA $bd        ; ZP $BD = pat_lo
    $50A2: B9 73 57  LDA $5773,y    ; pat_hi[Y]
    $50A5: 85 BE     STA $be        ; ZP $BE = pat_hi
    ; Clear v_arp_dir,X (NEW vs Action Biker): every new pattern note
    ; starts with arpeggio direction=0 (no arpeggio). The arpeggio path
    ; at $52A7 will only fire if this is non-zero, set by the optional
    ; pattern-byte at $50D3.
    $50A7: A9 00     LDA #$00
    $50A9: 9D 04 55  STA $5504,x    ; v_arp_dir,X = 0
    ; Y = byte offset within pattern (advances per note loaded).
    $50AC: BC D6 54  LDY $54d6,x    ; v_patpos,X
    ; $54E8 = gate-mask; default $FF (gate passes). DEC'd to $FE for
    ; tie/legato at $510A below.
    $50AF: A9 FF     LDA #$ff
    $50B1: 8D E8 54  STA $54e8      ; gate-mask = $FF
    ; First pattern byte = flags|duration:
    ;   bit 7 = "new instrument byte follows" (BMI test below at $50CC)
    ;   bit 6 = "tie/legato" (BVS test at $50C4 → DEC gate-mask)
    ;   bit 5 = "no_release"
    ;   bits 0-4 = duration in ticks
    $50B4: B1 BD     LDA ($bd),y    ; A = flags+dur byte
    $50B6: 9D DC 54  STA $54dc,x    ; v_flags,X = raw byte
    $50B9: 8D E9 54  STA $54e9      ; save for BIT test below
    $50BC: 29 1F     AND #$1f       ; duration only
    $50BE: 9D D9 54  STA $54d9,x    ; v_dur,X = duration
    ; Tie? skip note-byte fetch and instrument update (continuation).
    $50C1: 2C E9 54  BIT $54e9
    $50C4: 70 44     BVS $510a      ; → L_510A   ; tie: clear gate mask
    $50C6: FE D6 54  INC $54d6,x    ; advance v_patpos past flag byte
    $50C9: AD E9 54  LDA $54e9
    $50CC: 10 11     BPL $50df      ; → L_50DF   ; same inst: skip
    ; New-instrument byte present (bit 7 was set): consume it. NEW vs
    ; Action Biker: instead of always being a 5-bit inst index, this
    ; byte can ALSO be an "arpeggio direction" byte. Bit 7 set on the
    ; second byte → stash to $5504,X (arp dir flags). Bit 7 clear →
    ; normal new-instrument index.
    $50CE: C8        INY
    $50CF: B1 BD     LDA ($bd),y    ; second-byte: inst or arp_dir
    $50D1: 10 06     BPL $50d9      ; → L_50D9   ; bit 7 clear: inst
    $50D3: 9D 04 55  STA $5504,x    ; bit 7 set: v_arp_dir,X
    $50D6: 4C DC 50  JMP $50dc      ; → L_50DC
L_50D9:
    $50D9: 9D E5 54  STA $54e5,x    ; v_inst,X (5-bit not masked! see (*))
L_50DC:
    $50DC: FE D6 54  INC $54d6,x    ; advance past inst/arp byte
; Pitch byte. Doubled (ASL) because freq table at $540F is 2-byte
; entries (lo, hi) per semitone. v_pitch,X is also cached as the raw
; pitch index for later effects (vibrato, drum slide).
L_50DF:
    $50DF: C8        INY
    $50E0: B1 BD     LDA ($bd),y    ; pitch byte (0-95)
    $50E2: 9D E2 54  STA $54e2,x    ; v_pitch,X
    $50E5: 0A        ASL            ; *2 for table stride
    $50E6: A8        TAY            ; Y = byte offset into freq table
    ; Gate music SID writes on $550B - if SFX engine is active for this
    ; voice ($550B == 0), skip the SID writes (SFX owns V1+V2). The
    ; instrument table writes below at $5125+ are also gated the same.
    $50E7: AD 0B 55  LDA $550b      ; SFX-mute mask
    $50EA: 10 21     BPL $510d      ; → L_510D   ; SFX active: skip writes
    ; Write freq to SID. Also cache to $54FE,X / $5501,X = (v_fhi, v_flo)
    ; for the arpeggio/drum effect blocks to slide.
    $50EC: B9 0F 54  LDA $540f,y    ; freq_lo[pitch]
    $50EF: 8D EA 54  STA $54ea      ; temp save
    $50F2: B9 10 54  LDA $5410,y    ; freq_hi[pitch]
    $50F5: AC D2 54  LDY $54d2      ; Y = SID voice offset
    $50F8: 99 01 D4  STA $d401,y    ; V1_FREQ_HI,y
    $50FB: 9D FE 54  STA $54fe,x    ; v_fhi,X (for drum/arp slide)
    $50FE: AD EA 54  LDA $54ea
    $5101: 99 00 D4  STA $d400,y    ; V1_FREQ_LO,y
    $5104: 9D 01 55  STA $5501,x    ; v_flo,X (for arp slide)
    $5107: 4C 0D 51  JMP $510d      ; → L_510D
; Tie/legato note: clear gate-mask bit 0 so the ctrl write below ANDs
; off the gate bit (gate stays in whatever state previous note left it).
L_510A:
    $510A: CE E8 54  DEC $54e8      ; gate-mask $FF → $FE (clears bit 0)
; Write instrument table fields to SID for this voice.
; Inst table at $5574; each record is 8 bytes:
;   +0 pw_lo  +1 pw_hi  +2 ctrl  +3 AD  +4 SR  +5 vib_depth
;   +6 vib_period  +7 fx_flags
; X is shifted up by 3 (×8) to become byte offset into the table; the
; pointer arithmetic in the disassembly uses base = $5576 (= $5574 + 2)
; so $5576,X dereferences to ctrl (offset +2 from record start) etc.
; Action Biker uses the identical record layout at $CB5B.
;
; (*) NOTE: at $50D9 above we stored the new-inst byte WITHOUT the
; AND #$1F mask that Action Biker applies. So v_inst,X can be up to
; $7F here (low 7 bits). The ASL ASL ASL below shifts the value left
; by 3 bits — if v_inst > $1F, this wraps modulo 256, indexing past
; the inst-table block into pattern data ($5576 + N*8 for N >= $20).
; Whether real songs hit that depends on pattern data; the codegen
; should reproduce the no-mask behavior.
L_510D:
    $510D: AC D2 54  LDY $54d2      ; Y = SID voice offset (0/7/14)
    $5110: BD E5 54  LDA $54e5,x    ; v_inst,X (raw, may be 0..$7F)
    $5113: 8E EB 54  STX $54eb      ; save X (voice index)
    $5116: 0A        ASL            ; inst *2
    $5117: 0A        ASL            ; inst *4
    $5118: 0A        ASL            ; inst *8
    $5119: AA        TAX            ; X = byte offset into inst table
    $511A: BD 76 55  LDA $5576,x    ; inst.ctrl (record +2)
    $511D: 8D EC 54  STA $54ec      ; stash raw ctrl for v_ctrl,X save
    ; SFX-active gate: when $550B BPL (positive), SFX is running →
    ; suppress the SID writes that would clobber its V1+V2 state.
    $5120: AD 0B 55  LDA $550b
    $5123: 10 21     BPL $5146      ; → L_5146   ; SFX active: skip
    $5125: BD 76 55  LDA $5576,x    ; ctrl again
    $5128: 2D E8 54  AND $54e8      ; AND gate-mask (tie clears bit 0)
    $512B: 99 04 D4  STA $d404,y    ; V1_CTRL,y   ; write SID ctrl (gate)
    $512E: BD 74 55  LDA $5574,x    ; inst.pw_lo  (record +0)
    $5131: 99 02 D4  STA $d402,y    ; V1_PW_LO,y
    $5134: BD 75 55  LDA $5575,x    ; inst.pw_hi  (record +1)
    $5137: 99 03 D4  STA $d403,y    ; V1_PW_HI,y
    $513A: BD 77 55  LDA $5577,x    ; inst.AD     (record +3)
    $513D: 99 05 D4  STA $d405,y    ; V1_AD,y
    $5140: BD 78 55  LDA $5578,x    ; inst.SR     (record +4)
    $5143: 99 06 D4  STA $d406,y    ; V1_SR,y
L_5146:
    $5146: AE EB 54  LDX $54eb      ; restore X (voice)
    $5149: AD EC 54  LDA $54ec
    $514C: 9D DF 54  STA $54df,x    ; v_ctrl,X = raw inst.ctrl
    ; Advance v_patpos past the pitch byte. If next byte is $FF, pattern
    ; ended: zero v_patpos and bump v_olpos to next pattern.
    $514F: FE D6 54  INC $54d6,x
    $5152: BC D6 54  LDY $54d6,x
    $5155: B1 BD     LDA ($bd),y    ; peek next byte
    $5157: C9 FF     CMP #$ff
    $5159: D0 08     BNE $5163      ; → L_5163   ; not end-of-pat
    $515B: A9 00     LDA #$00
    $515D: 9D D6 54  STA $54d6,x    ; v_patpos,X = 0
    $5160: FE D3 54  INC $54d3,x    ; v_olpos,X += 1
L_5163:
    $5163: 4C 80 53  JMP $5380      ; → L_5380   ; voice tail (next voice)
; Sustain path entry (current note's v_dur hasn't expired). First gate
; on $550B: if SFX is muting this voice, jump straight to voice tail.
L_5166:
    $5166: AD 0B 55  LDA $550b
    $5169: 30 03     BMI $516e      ; → L_516E   ; music allowed: HR check
    $516B: 4C 80 53  JMP $5380      ; → L_5380   ; SFX active: skip
; Sustain HR (Hard Restart) check: if v_dur==0 AND no_release flag (bit 5
; of v_flags) clear → write ctrl-without-gate + AD=0 + SR=0 (kills env so
; next note retriggers cleanly). Else fall through to effects.
L_516E:
    $516E: AC D2 54  LDY $54d2
    $5171: BD DC 54  LDA $54dc,x    ; v_flags,X (raw pattern byte)
    $5174: 29 20     AND #$20       ; test bit 5 = no_release
    $5176: D0 15     BNE $518d      ; → L_518D   ; no_release: skip HR
    $5178: BD D9 54  LDA $54d9,x    ; v_dur,X
    $517B: D0 10     BNE $518d      ; → L_518D   ; still ticking: skip
    ; Hit HR threshold (v_dur == 0). Kill gate + envelope.
    $517D: BD DF 54  LDA $54df,x    ; v_ctrl,X (saved inst.ctrl)
    $5180: 29 FE     AND #$fe       ; clear gate bit
    $5182: 99 04 D4  STA $d404,y    ; V1_CTRL,y   ; gate off
    $5185: A9 00     LDA #$00
    $5187: 99 05 D4  STA $d405,y    ; V1_AD,y     ; AD=0
    $518A: 99 06 D4  STA $d406,y    ; V1_SR,y     ; SR=0
; Effects loop: vibrato / triangle-LFO frequency modulation.
; Second SFX-mute check ($518D) - this is the entry point used by the
; "note-load gated off" path from $5078 too.
L_518D:
    $518D: AD 0B 55  LDA $550b
    $5190: 30 03     BMI $5195      ; → L_5195   ; music allowed
    $5192: 4C 80 53  JMP $5380      ; → L_5380   ; SFX active: skip
; Effects setup: index into instrument table = inst_idx * 8 (Y), then
; load the per-record effect parameters at offsets +5/+6/+7.
;   $5579,Y = inst.vib_depth  → $54ED
;   $557A,Y = inst.vib_period → $54EE
;   $557B,Y = inst.fx_flags   → $5507
; If vib_depth == 0 skip vibrato block.
L_5195:
    $5195: BD E5 54  LDA $54e5,x    ; v_inst,X
    $5198: 0A        ASL
    $5199: 0A        ASL
    $519A: 0A        ASL            ; inst *8
    $519B: A8        TAY            ; Y = inst byte offset
    $519C: 8C FC 54  STY $54fc      ; remember inst offset
    $519F: B9 7B 55  LDA $557b,y    ; inst.fx_flags
    $51A2: 8D 07 55  STA $5507
    $51A5: B9 7A 55  LDA $557a,y    ; inst.vib_period
    $51A8: 8D EE 54  STA $54ee
    $51AB: B9 79 55  LDA $5579,y    ; inst.vib_depth
    $51AE: 8D ED 54  STA $54ed
    $51B1: F0 6F     BEQ $5222      ; → L_5222   ; depth=0: skip vibrato
    ; Triangle LFO from global frame counter $5509. AND $07 gives 0-7;
    ; if >= 4, EOR #$07 folds to 3-0, producing triangle 0-1-2-3-3-2-1-0.
    ; (Action Biker uses the same shape.)
    $51B3: AD 09 55  LDA $5509
    $51B6: 29 07     AND #$07
    $51B8: C9 04     CMP #$04
    $51BA: 90 02     BCC $51be      ; → L_51BE
    $51BC: 49 07     EOR #$07       ; fold: 4→3, 5→2, 6→1, 7→0
L_51BE:
    $51BE: 8D F3 54  STA $54f3      ; LFO triangle value
    ; Compute (freq[pitch+1] - freq[pitch]) >> vib_depth - the per-step
    ; semitone delta, right-shifted by vib_depth bits.
    $51C1: BD E2 54  LDA $54e2,x    ; v_pitch,X
    $51C4: 0A        ASL            ; *2 for table stride
    $51C5: A8        TAY
    $51C6: 38        SEC
    $51C7: B9 11 54  LDA $5411,y    ; freq_lo[pitch+1]
    $51CA: F9 0F 54  SBC $540f,y    ; minus freq_lo[pitch]
    $51CD: 8D EF 54  STA $54ef      ; delta_lo
    $51D0: B9 12 54  LDA $5412,y    ; freq_hi[pitch+1]
    $51D3: F9 10 54  SBC $5410,y    ; minus freq_hi[pitch]
L_51D6:
    ; Right-shift delta by vib_depth bits (smaller depth = wider vibrato).
    $51D6: 4A        LSR
    $51D7: 6E EF 54  ROR $54ef
    $51DA: CE ED 54  DEC $54ed
    $51DD: 10 F7     BPL $51d6      ; → L_51D6
    $51DF: 8D F0 54  STA $54f0      ; delta_hi (shifted)
    ; Load base freq for current pitch.
    $51E2: B9 0F 54  LDA $540f,y    ; freq_lo[pitch]
    $51E5: 8D F1 54  STA $54f1
    $51E8: B9 10 54  LDA $5410,y    ; freq_hi[pitch]
    $51EB: 8D F2 54  STA $54f2
    ; If original-pattern duration (low 5 bits) < 8 skip the vibrato sum
    ; (very short note → no time to vibrate).
    $51EE: BD DC 54  LDA $54dc,x    ; v_flags,X
    $51F1: 29 1F     AND #$1f       ; duration
    $51F3: C9 08     CMP #$08
    $51F5: 90 1C     BCC $5213      ; → L_5213   ; short note: skip
    $51F7: AC F3 54  LDY $54f3      ; LFO value (0..3)
L_51FA:
    ; Sum: freq += delta * LFO_value (one ADC per LFO tick).
    $51FA: 88        DEY
    $51FB: 30 16     BMI $5213      ; → L_5213
    $51FD: 18        CLC
    $51FE: AD F1 54  LDA $54f1
    $5201: 6D EF 54  ADC $54ef
    $5204: 8D F1 54  STA $54f1
    $5207: AD F2 54  LDA $54f2
    $520A: 6D F0 54  ADC $54f0
    $520D: 8D F2 54  STA $54f2
    $5210: 4C FA 51  JMP $51fa      ; → L_51FA
L_5213:
    ; Write vibrato-modulated freq to SID.
    $5213: AC D2 54  LDY $54d2
    $5216: AD F1 54  LDA $54f1
    $5219: 99 00 D4  STA $d400,y    ; V1_FREQ_LO,y
    $521C: AD F2 54  LDA $54f2
    $521F: 99 01 D4  STA $d401,y    ; V1_FREQ_HI,y
; PWM modulation block. Per-voice oscillating pulse-width sweep with
; configurable speed (high 3 bits of $54EE = step size, low 5 bits =
; step interval) and direction-flip thresholds at $08 (min) and $0E
; (max). Uses inst.pw_lo / inst.pw_hi as live state - the $08/$0E
; thresholds are HARDCODED in this routine (see CLAUDE.md ref
; "Hubbard PWM bounds").
;
; NEW path at $5222: if fx_flags bit 3 set, take a simpler "monotonic"
; PWM that adds $54EE to pw_lo with no direction-flip and no bounds
; check, ORs in $40 (pw_hi sign?), writes back. Used for sustained
; sweeping pads. After this, JMP $52A7 (arpeggio block).
L_5222:
    $5222: AD 07 55  LDA $5507      ; fx_flags
    $5225: 29 08     AND #$08       ; bit 3 = "monotonic PWM"
    $5227: F0 17     BEQ $5240      ; → L_5240   ; bit 3 clear: normal PWM
    $5229: AC FC 54  LDY $54fc      ; Y = inst byte offset
    $522C: B9 74 55  LDA $5574,y    ; inst.pw_lo (record +0)
    $522F: 6D EE 54  ADC $54ee      ; += vib_period (carry from last op)
    $5232: 09 40     ORA #$40       ; OR in bit 6
    $5234: 99 74 55  STA $5574,y    ; write back inst.pw_lo
    $5237: AC D2 54  LDY $54d2
    $523A: 99 02 D4  STA $d402,y    ; V1_PW_LO,y
    $523D: 4C A7 52  JMP $52a7      ; → L_52A7   ; skip normal PWM
; Normal PWM (Action Biker-equivalent):
L_5240:
    $5240: AD EE 54  LDA $54ee      ; vib_period
    $5243: F0 62     BEQ $52a7      ; → L_52A7   ; period=0: no PWM
    $5245: AC FC 54  LDY $54fc      ; Y = inst byte offset
    $5248: 29 1F     AND #$1f       ; low 5 bits = step interval
    $524A: DE F4 54  DEC $54f4,x    ; pwm step counter
    $524D: 10 58     BPL $52a7      ; → L_52A7   ; not yet time
    $524F: 9D F4 54  STA $54f4,x    ; reload step counter
    $5252: AD EE 54  LDA $54ee
    $5255: 29 E0     AND #$e0       ; high 3 bits = step size
    $5257: 8D 08 55  STA $5508
    $525A: BD F7 54  LDA $54f7,x    ; pwm direction flag
    $525D: D0 1A     BNE $5279      ; → L_5279   ; nonzero: subtract
    ; Direction = ADD: pw += step.
    $525F: AD 08 55  LDA $5508
    $5262: 18        CLC
    $5263: 79 74 55  ADC $5574,y    ; pw_lo += step
    $5266: 48        PHA
    $5267: B9 75 55  LDA $5575,y
    $526A: 69 00     ADC #$00       ; carry into pw_hi
    $526C: 29 0F     AND #$0f       ; pw_hi only uses 4 bits (12-bit PW)
    $526E: 48        PHA
    $526F: C9 0E     CMP #$0e       ; hit upper bound?
    $5271: D0 1D     BNE $5290      ; → L_5290
    $5273: FE F7 54  INC $54f7,x    ; flip direction (now SUB)
    $5276: 4C 90 52  JMP $5290      ; → L_5290
L_5279:
    ; Direction = SUB: pw -= step.
    $5279: 38        SEC
    $527A: B9 74 55  LDA $5574,y
    $527D: ED 08 55  SBC $5508      ; pw_lo -= step
    $5280: 48        PHA
    $5281: B9 75 55  LDA $5575,y
    $5284: E9 00     SBC #$00
    $5286: 29 0F     AND #$0f
    $5288: 48        PHA
    $5289: C9 08     CMP #$08       ; hit lower bound?
    $528B: D0 03     BNE $5290      ; → L_5290
    $528D: DE F7 54  DEC $54f7,x    ; flip direction (now ADD)
L_5290:
    ; Write updated pw back to inst record AND to SID.
    $5290: 8E EB 54  STX $54eb      ; save voice X
    $5293: AE D2 54  LDX $54d2      ; X = SID offset
    $5296: 68        PLA
    $5297: 99 75 55  STA $5575,y    ; inst.pw_hi updated
    $529A: 9D 03 D4  STA $d403,x    ; V1_PW_HI,x
    $529D: 68        PLA
    $529E: 99 74 55  STA $5574,y    ; inst.pw_lo updated
    $52A1: 9D 02 D4  STA $d402,x    ; V1_PW_LO,x
    $52A4: AE EB 54  LDX $54eb      ; restore voice X
; ARPEGGIO / FREQ-SLIDE block (NEW vs Action Biker).
; State: $5504,X = arp_dir byte, set at note-load from optional second
; pattern byte (bit 7 indicates arp_dir vs new-inst).
;   bit 0 of $5504,X = direction (0=ADD, 1=SUB)
;   bits 1-6 of $5504,X = step amount (×2, applied to 16-bit freq)
;
; Iterates every frame the note is held - steps $5501,X / $54FE,X
; (= cached v_flo/v_fhi at note-load) by the step amount. Result is
; a continuous slide either up or down at a fixed rate.
;
; (This is the "skydive effect" the CrazyComets README mentions, but
; implemented differently from Action Biker's drum slide at $52EE.)
L_52A7:
    $52A7: AC D2 54  LDY $54d2      ; Y = SID voice offset
    $52AA: BD 04 55  LDA $5504,x    ; v_arp_dir,X
    $52AD: F0 3F     BEQ $52ee      ; → L_52EE   ; zero: no arpeggio
    $52AF: 29 7E     AND #$7e       ; bits 1-6 = step amount (×2)
    $52B1: 8D EB 54  STA $54eb      ; arp step
    $52B4: BD 04 55  LDA $5504,x
    $52B7: 29 01     AND #$01       ; bit 0 = direction
    $52B9: F0 1B     BEQ $52d6      ; → L_52D6   ; ADD
    ; Direction = SUB: v_freq -= arp_step.
    $52BB: 38        SEC
    $52BC: BD 01 55  LDA $5501,x    ; v_flo,X
    $52BF: ED EB 54  SBC $54eb
    $52C2: 9D 01 55  STA $5501,x
    $52C5: 99 00 D4  STA $d400,y    ; V1_FREQ_LO,y
    $52C8: BD FE 54  LDA $54fe,x    ; v_fhi,X
    $52CB: E9 00     SBC #$00
    $52CD: 9D FE 54  STA $54fe,x
    $52D0: 99 01 D4  STA $d401,y    ; V1_FREQ_HI,y
    $52D3: 4C EE 52  JMP $52ee      ; → L_52EE
L_52D6:
    ; Direction = ADD: v_freq += arp_step.
    $52D6: 18        CLC
    $52D7: BD 01 55  LDA $5501,x
    $52DA: 6D EB 54  ADC $54eb
    $52DD: 9D 01 55  STA $5501,x
    $52E0: 99 00 D4  STA $d400,y    ; V1_FREQ_LO,y
    $52E3: BD FE 54  LDA $54fe,x
    $52E6: 69 00     ADC #$00
    $52E8: 9D FE 54  STA $54fe,x
    $52EB: 99 01 D4  STA $d401,y    ; V1_FREQ_HI,y
; DRUM freq-slide block (Action Biker's "skydive" equivalent).
; fx_flags bit 0 = drum/skydive. Decrements v_fhi (freq_hi) by 1 each
; frame until v_dur runs out → falling tom/kick sweep. When the slide
; passes mid-note, switches behavior: pre-DEC write + gate-off OR
; (if ctrl AND $FE is zero) write $80 (test bit silences osc).
L_52EE:
    $52EE: AD 07 55  LDA $5507      ; fx_flags
    $52F1: 29 01     AND #$01       ; bit 0 = drum
    $52F3: F0 35     BEQ $532a      ; → L_532A   ; not drum: skip
    $52F5: BD FE 54  LDA $54fe,x    ; v_fhi,X
    $52F8: F0 30     BEQ $532a      ; → L_532A   ; already 0: skip
    $52FA: BD D9 54  LDA $54d9,x    ; v_dur,X
    $52FD: F0 2B     BEQ $532a      ; → L_532A   ; v_dur=0: skip
    ; Compute (orig_dur - 1 - v_dur). If past midpoint use post-slide
    ; value directly; else DEC v_fhi and write OLD value.
    $52FF: BD DC 54  LDA $54dc,x    ; v_flags,X
    $5302: 29 1F     AND #$1f       ; orig duration
    $5304: 38        SEC
    $5305: E9 01     SBC #$01       ; dur - 1
    $5307: DD D9 54  CMP $54d9,x    ; compare to v_dur
    $530A: AC D2 54  LDY $54d2
    $530D: 90 10     BCC $531f      ; → L_531F
    $530F: BD FE 54  LDA $54fe,x    ; pre-DEC v_fhi
    $5312: DE FE 54  DEC $54fe,x    ; v_fhi -= 1
    $5315: 99 01 D4  STA $d401,y    ; V1_FREQ_HI,y
    $5318: BD DF 54  LDA $54df,x    ; saved inst.ctrl
    $531B: 29 FE     AND #$fe       ; clear gate bit
    $531D: D0 08     BNE $5327      ; → L_5327
L_531F:
    $531F: BD FE 54  LDA $54fe,x
    $5322: 99 01 D4  STA $d401,y    ; V1_FREQ_HI,y
    $5325: A9 80     LDA #$80       ; test bit (silence) for slide end
L_5327:
    $5327: 99 04 D4  STA $d404,y    ; V1_CTRL,y
; SLOW FREQ-DOWN block (NEW vs Action Biker).
; fx_flags bit 1 + duration >= $11 + alternate frame + v_fhi != 0
; → DEC v_fhi. Half-speed version of the drum slide; used for longer
; tom-style hits or pad sweeps.
L_532A:
    $532A: AD 07 55  LDA $5507      ; fx_flags
    $532D: 29 02     AND #$02       ; bit 1
    $532F: F0 1E     BEQ $534f      ; → L_534F   ; not set: skip
    $5331: BD DC 54  LDA $54dc,x    ; v_flags,X
    $5334: 29 1F     AND #$1f       ; orig duration
    $5336: C9 11     CMP #$11
    $5338: 90 15     BCC $534f      ; → L_534F   ; dur < $11: skip
    $533A: AD 09 55  LDA $5509      ; frame counter
    $533D: 29 01     AND #$01
    $533F: F0 0E     BEQ $534f      ; → L_534F   ; even frame: skip
    $5341: BD FE 54  LDA $54fe,x    ; v_fhi
    $5344: F0 09     BEQ $534f      ; → L_534F   ; already 0: skip
    $5346: DE FE 54  DEC $54fe,x    ; v_fhi -= 1
    $5349: AC D2 54  LDY $54d2
    $534C: 99 01 D4  STA $d401,y    ; V1_FREQ_HI,y
; OCTAVE-ARP block (NEW vs Action Biker).
; fx_flags bit 2 + alternate frame → write either freq[pitch] or
; freq[pitch+12] (= one octave up). Produces a coarse two-note
; octave-trill arpeggio characteristic of some Crazy Comets leads.
L_534F:
    $534F: AD 07 55  LDA $5507      ; fx_flags
    $5352: 29 04     AND #$04       ; bit 2 = octave arp
    $5354: F0 2A     BEQ $5380      ; → L_5380   ; not set: skip
    $5356: AD 09 55  LDA $5509      ; frame counter
    $5359: 29 01     AND #$01
    $535B: F0 09     BEQ $5366      ; → L_5366   ; even: use base pitch
    ; Odd frame: pitch + 12 (one octave up).
    $535D: BD E2 54  LDA $54e2,x    ; v_pitch
    $5360: 18        CLC
    $5361: 69 0C     ADC #$0c       ; +12 semitones
    $5363: 4C 69 53  JMP $5369      ; → L_5369
L_5366:
    $5366: BD E2 54  LDA $54e2,x    ; v_pitch (base)
L_5369:
    $5369: 0A        ASL            ; *2 for table stride
    $536A: A8        TAY
    $536B: B9 0F 54  LDA $540f,y    ; freq_lo[pitch_or_octave]
    $536E: 8D EA 54  STA $54ea
    $5371: B9 10 54  LDA $5410,y    ; freq_hi[pitch_or_octave]
    $5374: AC D2 54  LDY $54d2
    $5377: 99 01 D4  STA $d401,y    ; V1_FREQ_HI,y
    $537A: AD EA 54  LDA $54ea
    $537D: 99 00 D4  STA $d400,y    ; V1_FREQ_LO,y
; ===== per-voice loop tail =====
; Set the "SFX active → mute music" mask $550B based on whether SFX
; engine is currently running:
;   $550A bit 7 set → $550B = $FF  (music NOT muted; effects-loop BPL
;                                   tests above are all positive →
;                                   they WRITE to SID)
;   $550A bit 7 clear → $550B = $00  (music IS muted; effects-loop
;                                     BPL is taken → SKIPS SID writes)
;
; (Reading: at start of song, $550A = 0 → $550B = 0 → music writes
; skipped. After SFX done $550A becomes $FF → $550B = $FF → music
; resumes. So in PURE music subtunes the music never starts unless
; init explicitly sets $550A bit 7. Looking at $60DE: SFX init does
; ORA #$40 / STA $550A - bit 6 is set but bit 7 isn't. Looking at
; $60A7 (music init): does NOT touch $550A. So initial $550A is
; whatever the binary's zero-page-or-storage default is - in PSID
; the C64 RAM is zero-initialised, so $550A starts at $00 → music
; is muted! See note below at sub_5514 for the path that flips this.)
;
; Update: actually, music subtune SHOULD set $550A bit 7. The fact
; that the auto-trace from init didn't reach a $550A-write is a hint
; that init-side setup is incomplete in this seed. The $60A7 setup
; may need additional state to enable music - VERIFY against
; siddump --writelog when implementing codegen.
L_5380:
    $5380: A0 FF     LDY #$ff
    $5382: AD 0A 55  LDA $550a
    $5385: 30 01     BMI $5388      ; → L_5388
    $5387: C8        INY            ; Y = $00 (SFX active)
L_5388:
    $5388: 8C 0B 55  STY $550b      ; $550B = $FF (music on) or $00 (off)
    $538B: CA        DEX
    $538C: 30 03     BMI $5391      ; → L_5391   ; X<0: exit voice loop
    $538E: 4C 54 50  JMP $5054      ; → L_5054   ; next voice

; ===== SFX engine =====
; Entered after the music voice loop (and from end-of-song path $5044).
; $550B is now $FF (the LDA #$FF/STA below resets it; the music's
; $5380 sequence was about the music's read of $550B, not the engine's).
L_5391:
    $5391: A9 FF     LDA #$ff
    $5393: 8D 0B 55  STA $550b      ; force music-allowed for next pass
    $5396: 2C 0A 55  BIT $550a      ; SFX state
    $5399: 10 01     BPL $539c      ; → L_539C   ; bit 7 set: SFX idle
L_539B:
    $539B: 60        RTS            ; no SFX active: return from play
; SFX-engine active branch. Bit 6 of $550A = "first frame" → run setup.
L_539C:
    $539C: 50 03     BVC $53a1      ; → L_53A1   ; bit 6 clear: normal
    $539E: 20 14 55  JSR $5514      ; → sub_5514 ; first frame: setup
L_53A1:
    ; Sub-frame timer: $550D ticks down; when negative, reload from
    ; (flags & $0F) and run a step.
    $53A1: CE 0D 55  DEC $550d
    $53A4: 10 F5     BPL $539b      ; → L_539B   ; not yet: RTS
    $53A6: AD 13 55  LDA $5513      ; flags byte
    $53A9: 29 0F     AND #$0f       ; low nibble = sub-frame reload
    $53AB: 8D 0D 55  STA $550d
    ; Compare $550C (event counter) to $550E (end value). Equal → done:
    ; silence V1+V2, mark SFX-finished ($550A = $FF; bit 7 clear).
    $53AE: AD 0C 55  LDA $550c
    $53B1: CD 0E 55  CMP $550e
    $53B4: D0 0F     BNE $53c5      ; → L_53C5   ; not done: step
    $53B6: A2 00     LDX #$00
    $53B8: 8E 04 D4  STX $d404      ; V1_CTRL = 0
    $53BB: 8E 0B D4  STX $d40b      ; V2_CTRL = 0
    $53BE: CA        DEX            ; X = $FF
    $53BF: 8E 0A 55  STX $550a      ; $550A = $FF (SFX done; bit 7 clear)
    $53C2: 4C 9B 53  JMP $539b      ; → L_539B   ; RTS
; SFX step: $53C5 is PATCHED at sub_5514 time to either INC $550C or
; DEC $550C, depending on flags byte ($5513 bits 5/4). DEC is the
; default; INC is for descending sweeps. The opcode at $53C5 is
; literally rewritten by sub_5514.
L_53C5:
    $53C5: CE 0C 55  DEC $550c      ; (patched to INC or DEC at setup)
    $53C8: 0A        ASL            ; *2 for freq-table stride
    $53C9: A8        TAY
    $53CA: 2C 13 55  BIT $5513      ; flags byte: bit 7 = skip V1 freq
    $53CD: 30 20     BMI $53ef      ;             bit 6 = skip V2 freq
    $53CF: 70 0C     BVS $53dd      ; → L_53DD   ; V1 only on flags bit 6
    ; Write V1 freq from table.
    $53D1: B9 0F 54  LDA $540f,y
    $53D4: 8D 00 D4  STA $d400      ; V1_FREQ_LO
    $53D7: B9 10 54  LDA $5410,y
    $53DA: 8D 01 D4  STA $d401      ; V1_FREQ_HI
L_53DD:
    ; V2 freq from same table at offset (Y - detune $550F). Produces
    ; a fixed-interval two-voice "phaser" / harmonic sweep.
    $53DD: 98        TYA
    $53DE: 38        SEC
    $53DF: ED 0F 55  SBC $550f      ; Y - detune
    $53E2: A8        TAY
    $53E3: B9 0F 54  LDA $540f,y
    $53E6: 8D 07 D4  STA $d407      ; V2_FREQ_LO
    $53E9: B9 10 54  LDA $5410,y
    $53EC: 8D 08 D4  STA $d408      ; V2_FREQ_HI
L_53EF:
    ; Toggle V1/V2 ctrl bits via EOR each step. $5510 bit 7/6 enables
    ; toggle for V1/V2 respectively. The EOR target ($5511/$5512) is
    ; the live ctrl value; toggling bit 0 retriggers the gate.
    $53EF: 2C 10 55  BIT $5510
    $53F2: 10 0B     BPL $53ff      ; → L_53FF   ; bit 7 clear: no V1 tog
    $53F4: AD 11 55  LDA $5511
    $53F7: 49 01     EOR #$01       ; flip gate bit
    $53F9: 8D 04 D4  STA $d404      ; V1_CTRL
    $53FC: 8D 11 55  STA $5511      ; remember new state
L_53FF:
    $53FF: 50 0B     BVC $540c      ; → L_540C   ; bit 6 clear: no V2 tog
    $5401: AD 12 55  LDA $5512
    $5404: 49 01     EOR #$01
    $5406: 8D 0B D4  STA $d40b      ; V2_CTRL
    $5409: 8D 12 55  STA $5512
L_540C:
    $540C: 4C 9B 53  JMP $539b      ; → L_539B   ; RTS
; ----- data gap $540F-$5513 (261 bytes) -----
;   $540F-$54CE: freq table (96 semitones × 2 bytes)
;   $54CF-$54D1: SID voice offset table (V1=0, V2=7, V3=14)
;   $54D2-$5513: per-voice + per-engine state (see header)

; SFX first-frame setup. Called from $539E when $550A bit 6 is set.
; Reads the SFX descriptor at $562C + sfx_idx*$10 and patches the
; engine state, then bulk-copies 14 bytes from $562D+ into the SID
; registers $D400..$D40D (V1+V2 freq/PW/ctrl/AD/SR) to seed the
; voicing. Finally patches the opcode at $53C5 to either INC ($EE)
; or DEC ($CE) based on $5513 bits 5/4.
sub_5514:
    $5514: A9 00     LDA #$00
    $5516: 8D 04 D4  STA $d404      ; V1_CTRL = 0
    $5519: 8D 0B D4  STA $d40b      ; V2_CTRL = 0
    $551C: 8D 0D 55  STA $550d      ; SFX sub-timer = 0
    ; Mask $550A to low 4 bits = sfx_idx, then ×16 to index descriptor.
    $551F: AD 0A 55  LDA $550a
    $5522: 29 0F     AND #$0f       ; sfx_idx
    $5524: 8D 0A 55  STA $550a      ; clear bit 6 (no longer "first frame")
    $5527: 0A        ASL
    $5528: 0A        ASL
    $5529: 0A        ASL
    $552A: 0A        ASL            ; ×16
    $552B: A8        TAY            ; Y = sfx_idx * 16
    ; Read descriptor fields from $562C + Y:
    ;   +0 ($562C) → $5513 (flags)
    ;   +1 ($562D) → $550C (event counter init)
    ;   +F ($563B) → $550E (end value)
    ;   +8 ($5634) → $5510 (V1 ctrl XOR mask; low 6 bits → V1-V2 detune)
    ;   +5 ($5631) → $5511 (V1 ctrl initial)
    ;   +C ($5638) → $5512 (V2 ctrl initial)
    $552C: B9 2C 56  LDA $562c,y
    $552F: 8D 13 55  STA $5513
    $5532: B9 2D 56  LDA $562d,y
    $5535: 8D 0C 55  STA $550c
    $5538: B9 3B 56  LDA $563b,y
    $553B: 8D 0E 55  STA $550e
    $553E: B9 34 56  LDA $5634,y
    $5541: 8D 10 55  STA $5510
    $5544: 29 3F     AND #$3f
    $5546: 8D 0F 55  STA $550f      ; detune offset
    $5549: B9 31 56  LDA $5631,y
    $554C: 8D 11 55  STA $5511
    $554F: B9 38 56  LDA $5638,y
    $5552: 8D 12 55  STA $5512
    ; Bulk-copy 14 bytes from descriptor (offset +1 onward) to $D400..
    ; That covers V1+V2 freq_lo/hi/pw_lo/pw_hi/ctrl/AD/SR = 14 regs.
    $5555: A2 00     LDX #$00
L_5557:
    $5557: B9 2D 56  LDA $562d,y    ; descriptor[+1+i]
    $555A: 9D 00 D4  STA $d400,x    ; V1_FREQ_LO,x → fills V1+V2 block
    $555D: C8        INY
    $555E: E8        INX
    $555F: E0 0E     CPX #$0e       ; 14 iterations
    $5561: D0 F4     BNE $5557      ; → L_5557
    ; Patch the opcode at $53C5 based on flags bits 5/4:
    ;   $5513 & $30 == $20 → patch to $EE = INC $550C
    ;   otherwise           → patch to $CE = DEC $550C (default)
    $5563: AD 13 55  LDA $5513
    $5566: 29 30     AND #$30
    $5568: A0 EE     LDY #$ee       ; assume INC
    $556A: C9 20     CMP #$20
    $556C: F0 02     BEQ $5570      ; → L_5570
    $556E: A0 CE     LDY #$ce       ; otherwise DEC
L_5570:
    $5570: 8C C5 53  STY $53c5      ; self-modify opcode at $53C5
    $5573: 60        RTS
; ----- data gap $5574-$60A6 (2867 bytes) -----
;   $5574-$5731: instrument table (8-byte records starting at $5574)
;                + SFX descriptor table starting at $562C
;                + extra constant tables ($572C orderlist ptr lo,
;                  $572F orderlist ptr hi, $5732+ subtune orderlist src,
;                  $573E pattern lo, $5773 pattern hi)
;   $5774-$60A6: pattern + orderlist payload data

; ===== init helpers =====
; music engine setup. Entered from JMP at $5000 (i.e. init subtune < 2).
; A on entry holds subtune index (0 or 1).
;   Compute A*6 (A*2 + A*4) → X, copy 6 bytes from $5732+X to $572C+Y
;   (Y starts at 0). $572C..$5731 is the active per-voice orderlist
;   pointer block (3 lo bytes + 3 hi bytes). $5732+ holds (subtune *
;   6)-strided base table.
L_60A7:
    $60A7: A0 00     LDY #$00
    $60A9: 0A        ASL            ; A * 2
    $60AA: 8D EB 54  STA $54eb
    $60AD: 0A        ASL            ; A * 4
    $60AE: 18        CLC
    $60AF: 6D EB 54  ADC $54eb      ; A*2 + A*4 = A * 6
    $60B2: AA        TAX            ; X = subtune * 6
L_60B3:
    $60B3: BD 32 57  LDA $5732,x    ; src
    $60B6: 99 2C 57  STA $572c,y    ; dst = active orderlist ptr table
    $60B9: E8        INX
    $60BA: C8        INY
    $60BB: C0 06     CPY #$06
    $60BD: D0 F4     BNE $60b3      ; → L_60B3   ; loop 6 bytes
    ; Silence all voices, set filter off, full volume, mark "first frame".
    $60BF: A9 00     LDA #$00
    $60C1: 8D 17 D4  STA $d417      ; RES_FILT
    $60C4: 8D 04 D4  STA $d404      ; V1_CTRL = 0
    $60C7: 8D 0B D4  STA $d40b      ; V2_CTRL = 0
    $60CA: 8D 12 D4  STA $d412      ; V3_CTRL = 0
    $60CD: A9 0F     LDA #$0f
    $60CF: 8D 18 D4  STA $d418      ; VOL = $0F
    $60D2: A9 40     LDA #$40
    $60D4: 8D FD 54  STA $54fd      ; $54FD = $40 (music sentinel: "first
                                    ;                                frame")
    $60D7: 60        RTS

; SFX second-stage init: locks engine into SFX-only mode by setting
; $54FD = $C0 (bit 7=end-of-song, bit 6=first-frame). The play()
; handler's BIT $54FD test will:
;   BMI taken → JMP $5032   (panic silence)
;   BVC taken (bit 6 still set inside the BMI branch) → JMP $5044 →
;                              JMP $5391 → SFX engine
; Net effect: every play call drives the SFX engine only; the music
; engine is bypassed entirely.
L_60D8:
    $60D8: A9 C0     LDA #$c0       ; bit 7 + bit 6
    $60DA: 8D FD 54  STA $54fd
    $60DD: 60        RTS

; SFX first-stage init: A on entry = (subtune - 2) = sfx_idx (0..14).
; OR with $40 to mark "first SFX frame" (bit 6) and store as $550A.
; Set volume to $0F.
L_60DE:
    $60DE: 09 40     ORA #$40       ; sfx_idx | $40 (first frame)
    $60E0: 8D 0A 55  STA $550a      ; SFX state sentinel
    $60E3: A9 0F     LDA #$0f
    $60E5: 8D 18 D4  STA $d418      ; VOL = $0F
    $60E8: 60        RTS
; ----- data gap $60E9-$60FF (23 bytes) -----

; ======= init: =======
; Entry: A = subtune index (0-indexed). PSID startSong=1 → sidplayfp
; passes A=0 here. Dispatches by range: <2 = music engine, >=2 = SFX.
init:
    $6100: C9 02     CMP #$02
    $6102: B0 03     BCS $6107      ; → L_6107   ; >= 2: SFX path
    $6104: 4C 00 50  JMP $5000      ; → L_5000   ; < 2: music init
L_6107:
    $6107: 38        SEC
    $6108: E9 02     SBC #$02       ; sfx_idx = subtune - 2
    $610A: 20 09 50  JSR $5009      ; → sub_5009 ; SFX first-stage
    $610D: 4C 03 50  JMP $5003      ; → L_5003   ; SFX second-stage
