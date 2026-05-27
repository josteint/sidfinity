; ============================================================================
; Rob Hubbard - Battle of Britain (1986 PSS)
; ANNOTATED DISASSEMBLY (auto-generated seed; hand-annotated)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/Hubbard_Rob/Battle_of_Britain.sid
; Load:   $8000   Init: $8EAA   Play: $8006
; PSID v2: 1 subtune (the HVSC PSID is a stripped one-track version; the
;          original game ships 19 entries — 3 music + 16 SFX), startSong=1.
;          speed=$00000001 = song 0 uses CIA timer (single-speed).
; Binary: $8000-$8FFF (4096 bytes).
;
; Auto-traced 331 reachable code bytes from init+play (831 instruction
; bytes after recursive-descent across all conditional / unconditional
; branches and JSR targets). Layout commentary derived from static
; analysis cross-checked against the data-table dump at $8326 (freq
; table), $8420 (instrument records), $84B8/$84BB (orderlist pointers),
; $84BE/$84E8 (pattern pointers).
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($8EAA): 33 bytes. Ignores A (no subtune support — the stripped
; PSID has only 1 song). Zeros v_olpos/v_patpos/v_dur/v_pitch for all 3
; voices, writes 0 to V1/V2/V3 ctrl, vol=$0F. RTS. Crucially, init does
; NOT zero the tick divider $8411 or its reload $8412 — those have
; baked-in binary initial values ($8411=$00, $8412=$01) that make the
; FIRST play frame's note-load gate fire immediately:
;   - frame 1 enters with $8411=$00, DEC → $FF (BPL not taken), reload
;     from $8412=$01 → $8411=$01. Then CMP $8411 vs $8412: equal → BNE
;     not taken → note-load runs.
;   - So unlike Action Biker, BoB fires its first note on play frame 1
;     (the very first call to play), not deferred. The 1-frame delay
;     trick AB uses isn't present here.
;
; play ($8006): every frame.
;   1. INC $841F (global frame counter; binary init = $DC, so it wraps
;      through the byte cycle — only the low bits are used by the LFO
;      and bit-1/bit-2 effect dividers).
;   2. LDX #$02 (X = voice slot, count 2..0 = V3, V2, V1).
;   3. DEC $8411 (sub-frame tick divider); if BPL taken (still positive
;      after DEC) keep going; otherwise reload from $8412 ($01).
;   4. Fall through into per-voice loop at $8016.
;
; PER-VOICE PROCESSING ($8016..$8322):
;   - LDA $83E6,X → $83E9: SID base offset (table at $83E6 = {$00,$07,$0E}).
;   - **NOTE-LOAD GATE**: CMP $8411 vs $8412. If unequal, JMP $8136
;     (effects-only, no note advance). On every tick reload the gate
;     passes and a note frame happens.
;   - Note-load entry:
;     * LDA $84B8,X / $84BB,X → ZP $FB/$FC = orderlist pointer for voice.
;       Initial values in binary: $8512 (V1), $8534 (V2), $8556 (V3).
;     * DEC $83F0,X (v_dur countdown). BMI: expired → load next note.
;       Else: JMP $8117 (sustain HR check).
;
; Note-load path ($803D..$8114):
;   - Read orderlist byte via ($FB),Y where Y=v_olpos. $FF = loop back
;     (zero v_dur/v_olpos/v_patpos, retry). No $FE song-end marker —
;     BoB music loops forever (game-music model).
;   - Look up pattern address via $84BE,Y (pat_lo) / $84E8,Y (pat_hi).
;   - First pattern byte = (flags << 5) | duration:
;       bit 7 = "new byte follows" (instrument OR glissando)
;       bit 6 = tie/legato (BVS at $807A → L_80C0 clears gate mask)
;       bit 5 = no_release (preserved for sustain HR test at $811F)
;       bits 0-4 = duration in ticks
;   - When bit 7 set, the next byte is examined:
;       bit 7 of THAT byte CLEAR → it's a new instrument index (5-bit);
;         store at $83FC,X (v_inst).
;       bit 7 of THAT byte SET → it's a **GLISSANDO command**:
;         store at $841A,X. Format = {direction:bit0, magnitude:bits1-6,
;         enable:bit7}. The PW-slide block at $8246 uses it to slide
;         v_fhi/v_flo over the note's lifetime.
;     This dual-purpose second byte is BoB-specific (Action Biker only
;     uses the byte for inst index; no glissando command in AB).
;   - Pitch byte: read, store at $83F9,X, then ASL (×2 freq-table stride
;     at $8326) and look up freq_lo / freq_hi. **Writes BOTH SID freq
;     regs AND v_flo ($8417,X) AND v_fhi ($8414,X)** — BoB stores
;     freq_lo as well because glissando slides it (AB only stored fhi).
;   - Instrument apply: X = inst*8 (3 ASLs), index into table at $8420.
;     Layout: +0 pw_lo, +1 pw_hi, +2 ctrl, +3 AD, +4 SR, +5 vib_depth,
;     +6 pwm_period, +7 fx_flags. The ctrl write at $80DC is gate-masked
;     via AND $83FF (tie/legato clears bit 0 to keep gate state).
;   - Advance v_patpos. Peek next byte: if $FF → pattern end, zero
;     v_patpos, INC v_olpos.
;
; Sustain path / HARD RESTART ($8117..$8136):
;   - LDA $83F3,X (saved v_flags) / AND #$20 — if no_release bit set,
;     skip HR; JMP $8136 (effects).
;   - LDA $83F0,X (v_dur) — if nonzero, still ticking, skip HR.
;   - Hit HR threshold (v_dur reached 0): write v_ctrl AND #$FE (gate
;     off) plus AD=0, SR=0. This snappily kills the envelope so the
;     next note's gate-on retriggers cleanly. Identical to AB's HR.
;
; EFFECTS LOOP ($8136..$831F):
;   Y = inst*8 (computed from $83FC,X / ASL ASL ASL); $8413 caches Y.
;   Reads from instrument record:
;     +5 vib_depth → $8404
;     +6 pwm_period → $8405
;     +7 fx_flags → $841D
;
;   Vibrato ($8154..$81C1): triangle LFO from $841F & $07; values 4-7
;     fold to 3-0 via EOR #$07. Per-frame delta = (freq[pitch+1] -
;     freq[pitch]) >>> vib_depth. Accumulate LFO times, then write
;     modulated freq_lo/hi to SID. Skipped entirely for dur<8 notes
;     (no time to vibrate on staccato notes). Identical to AB.
;
;   PWM block ($81C3..$8243): two modes.
;     * fx_flags bit 3 set: ONE-SHOT slide — pw_lo += pwm_period each
;       frame (no bounds, no direction flip), write SID and jump out.
;       BoB-specific (AB has no this-bit mode).
;     * fx_flags bit 3 clear, pwm_period ≠ 0: STANDARD bidirectional
;       PWM. Low 5 bits of pwm_period = step interval (per-voice
;       counter at $840B,X); high 3 bits = step size into $841E.
;       Direction flag at $840E,X. Bounds HARDCODED at $08 (lower) and
;       $0E (upper) for the high nibble of pw_hi — flip direction when
;       hit. The "Hubbard PWM bounds" invariant (reference memory).
;       Identical bounds to AB.
;
;   Glissando / drum sweep ($8246..$828A): unique to BoB.
;     - If $841A,X (per-voice glissando byte) is 0, skip — JMP $828D.
;     - Otherwise:
;         step = $841A,X AND $7E   (bits 1-6 × 2 = signed magnitude)
;         dir  = $841A,X AND $01   (bit 0 = direction)
;         dir==0: v_flo += step, v_fhi += carry; write SID
;         dir==1: v_flo -= step, v_fhi -= carry; write SID
;     This is the per-note pitch slide encoded in the pattern's second
;     byte when bit 7 was set (handled at $808E above).
;
;   fx_flags bit 0 — DRUM/SKYDIVE ($828D..$82C6): Identical to AB. For
;     notes with dur in mid-range, DEC v_fhi each frame and write
;     ctrl AND $FE (gate off) — produces falling tom/snare. When
;     past mid-note, write a $80 (test bit, silence) to ctrl. The
;     README's "skydive effect" refers to this block.
;
;   fx_flags bit 1 — SLOW DRIFT ($82C9..$82EE): For long notes (orig
;     dur ≥ 12) and every odd frame ($841F AND $01 ≠ 0), DEC v_fhi
;     by 1 if it's nonzero, and write the new freq_hi to SID. This
;     is a slow ~1Hz downward drift — used on long sustained pads.
;
;   fx_flags bit 2 — OCTAVE ARPEGGIO ($82EE..$831C): When set, every
;     non-(frame%8==0) tick transposes the pitch by +12 (one octave)
;     and writes the resulting freq. On frame%8==0, write the base
;     pitch's freq. Net effect: 7/8 of the time at +octave, 1/8 at
;     base — a fast octave shimmer. Often paired with a bass note.
;
; Per-voice tail ($831F): DEX; BMI → done (RTS). Else JMP $8016 (next).
;
; ============================================================================
;
; DATA LAYOUT (extracted via byte dump)
; ----------------------------------------
;
; FREQ TABLE ($8326-$83E5, 96 semitones × 2 bytes lo/hi).
;   freq[0]  = $0116  freq[1]  = $0127  freq[2]  = $0138  freq[3]  = $014B
;   freq[4]  = $015F  freq[5]  = $0173  freq[6]  = $018A  freq[7]  = $01A1
;   freq[8]  = $01BA  freq[9]  = $01D4  freq[10] = $01F0  freq[11] = $020E
;   (~12-TET, 96 entries reaches across 8 octaves)
;
; SID BASE TABLE ($83E6-$83E8): { $00, $07, $0E } for V1, V2, V3.
;
; PER-VOICE STATE (X-indexed, X=0..2):
;   $83EA,X  v_olpos          (orderlist position; init=0)
;   $83ED,X  v_patpos         (pattern position; init=0)
;   $83F0,X  v_dur            (duration countdown; init=0)
;   $83F3,X  v_flags          (raw 1st pattern byte: dur+flags)
;   $83F6,X  v_ctrl           (saved inst.ctrl)
;   $83F9,X  v_pitch          (raw semitone index; init=0)
;   $83FC,X  v_inst           (raw 5-bit instrument index)
;   $8414,X  v_fhi            (current freq_hi, used by glissando)
;   $8417,X  v_flo            (current freq_lo, used by glissando)
;   $841A,X  v_gliss          (per-note glissando byte: dir+step)
;   $840B,X  v_pwm_counter
;   $840E,X  v_pwm_dir
;
; SCALAR STATE:
;   $83E9    saved SID base offset (Y register snapshot)
;   $83FF    gate mask ($FF normal; $FE for tie/legato)
;   $8400    scratch (raw pattern flag byte)
;   $8401    scratch freq_lo for SID write
;   $8402    save-X scratch
;   $8403    saved raw inst.ctrl
;   $8404    vibrato shift count (= vib_depth)
;   $8405    pwm_period scratch
;   $8406    delta_lo
;   $8407    delta_hi
;   $8408    accumulated freq_lo (for vibrato output)
;   $8409    accumulated freq_hi (for vibrato output)
;   $840A    triangle LFO value (0..4)
;   $8411    sub-frame tick divider (init $00, gate=note-load on
;            tick == reload)
;   $8412    tick reload value (init $01 → note frame every other
;            play call)
;   $8413    saved inst byte offset Y (= inst * 8)
;   $841D    fx_flags scratch
;   $841E    pwm step size (high 3 bits of pwm_period)
;   $841F    global frame counter (binary init $DC)
;
; INSTRUMENT TABLE ($8420, 8-byte records):
;   first records:
;     I0: pw=$0359 ctrl=$41 AD=$58 SR=$52 vib=$03 pwm=$10 fx=$08
;     I1: pw=$0248 ctrl=$41 AD=$58 SR=$62 vib=$04 pwm=$10 fx=$08
;     I2: pw=$0322 ctrl=$41 AD=$0A SR=$00 vib=$00 pwm=$11 fx=$08
;     I3: pw=$0200 ctrl=$81 AD=$0C SR=$0A vib=$00 pwm=$00 fx=$05
;     I4: pw=$0000 ctrl=$11 AD=$0F SR=$F0 vib=$02 pwm=$00 fx=$02
;     I5: pw=$0800 ctrl=$41 AD=$58 SR=$00 vib=$00 pwm=$00 fx=$04
;     ... (16+ instruments)
;
; ORDERLIST POINTER TABLES:
;   $84B8 (lo): 12 34 56     → orderlists at $8512, $8534, $8556
;   $84BB (hi): 85 85 85
;
; PATTERN POINTER TABLES:
;   $84BE (lo, 16 shown): CE 36 55 74 D1 89 93 B2 41 0E DB 62 E0 96 4D 49
;   $84E8 (hi, 16 shown): 85 8D 8D 8D 85 86 8D 8D 87 88 88 89 89 8A 8E 8B
;
; ============================================================================
;
; BoB-SPECIFIC QUIRKS (vs. Action Biker / Commando):
;   1. INIT is real, not deferred to play. No $40 first-frame sentinel.
;      Tick divider initial values are baked into the binary.
;   2. NO subtune handling — A register on init entry is ignored.
;   3. NO $FE song-end sentinel — only $FF orderlist loopback. Music
;      runs forever.
;   4. GLISSANDO ($841A,X) — per-note pitch slide encoded in the
;      "second byte" of a pattern entry when bit 7 of the inst byte
;      is set. Slides both v_flo AND v_fhi.
;   5. THREE extra fx_flags effects (bit 1 slow drift, bit 2 octave
;      arp, bit 3 simple PW slide) on top of bit 0 drum/skydive
;      and the vibrato/PWM blocks that AB also has.
;   6. v_flo state stored in addition to v_fhi (AB only stored fhi).
;   7. PWM bounds $08/$0E identical to AB (Hubbard signature).
;
; ============================================================================

; ----- data gap $8000-$8005 (6 bytes) -----
; ----- expected: trampoline / leftover from compile, or header data
;       used by the original game runtime. PSID play vector points at
;       $8006 directly so these bytes are unreachable.

; ======= play: =======
; Called every frame by sidplayfp. No CIA timer used despite speed=$01.
play:
    ; Global frame counter. Binary init = $DC; we just wrap through
    ; the byte cycle. Only the low bits are used by the LFO ($841F
    ; AND $07) and the bit-1/bit-2 effect dividers ($841F AND $01,
    ; $841F AND $07).
    $8006: EE 1F 84    INC $841f
    $8009: A2 02       LDX #$02       ; X = voice slot (start V3)
    ; Sub-frame tick divider. Binary init $8411=$00, $8412=$01.
    ; DEC $00 → $FF (negative). BPL not taken on the very first
    ; frame → fall through to reload $8411 from $8412=$01. Result:
    ; $8411 ends each frame matching $8412 → CMP later passes →
    ; note-load runs every frame.
    $800B: CE 11 84    DEC $8411
    $800E: 10 06       BPL $8016      ; → L_8016 ; still positive: don't reload
    $8010: AD 12 84    LDA $8412      ; A = reload value (=$01)
    $8013: 8D 11 84    STA $8411      ; $8411 = $01
L_8016:
    ; Per-voice loop entry. X = 2,1,0 across V3,V2,V1.
    ; Look up SID base offset (0/7/14) from $83E6 table.
    $8016: BD E6 83    LDA $83e6,X    ; A = SID base offset
    $8019: 8D E9 83    STA $83e9      ; cache for later STA $D4xx,Y
    $801C: A8          TAY            ; Y = SID base offset
    ; **NOTE-LOAD GATE.** On a non-reload tick, $8411 ≠ $8412 →
    ; BNE taken → skip note-load and jump to effects-only at $8136.
    $801D: AD 11 84    LDA $8411
    $8020: CD 12 84    CMP $8412
    $8023: D0 15       BNE $803a      ; → L_803A ; tick !== reload: effects only
    ; Note-frame: load orderlist pointer for this voice from
    ; $84B8/$84BB lookup tables. Initial values point V1→$8512,
    ; V2→$8534, V3→$8556.
    $8025: BD B8 84    LDA $84b8,X    ; orderlist ptr lo
    $8028: 85 FB       STA $fb        ; ZP $FB
    $802A: BD BB 84    LDA $84bb,X    ; orderlist ptr hi
    $802D: 85 FC       STA $fc        ; ZP $FC
    ; Per-voice duration countdown.
    $802F: DE F0 83    DEC $83f0,X    ; v_dur,X -= 1
    $8032: 30 09       BMI $803d      ; → L_803D ; underflow: load next note
    $8034: 4C 17 81    JMP $8117      ; → L_8117 ; still ticking: sustain check
; ----- data gap $8037-$8039 (3 bytes) -----

L_803A:
    ; Effects-only trampoline (no note advance this frame).
    $803A: 4C 36 81    JMP $8136      ; → L_8136
; Note-load entry. ($FB):Y → orderlist; v_olpos at $83EA,X.
L_803D:
    $803D: BC EA 83    LDY $83ea,X    ; v_olpos,X
    $8040: B1 FB       LDA ($fb),Y    ; orderlist[v_olpos]
    $8042: C9 FF       CMP #$ff       ; loop-back sentinel? (no $FE in BoB)
    $8044: D0 11       BNE $8057      ; → L_8057 ; normal: load pattern
    ; Orderlist loop-back: reset duration, position, pattern position
    ; (NOTE: also clears v_olpos, so next read at $803D re-reads index 0).
    $8046: A9 00       LDA #$00
    $8048: 9D F0 83    STA $83f0,X    ; v_dur,X = 0
    $804B: 9D EA 83    STA $83ea,X    ; v_olpos,X = 0
    $804E: 9D ED 83    STA $83ed,X    ; v_patpos,X = 0
    $8051: 4C 3D 80    JMP $803d      ; → L_803D ; retry from index 0
; ----- data gap $8054-$8056 (3 bytes) -----

; Normal pattern load. A = orderlist[v_olpos] = pattern index.
L_8057:
    $8057: A8          TAY            ; Y = pattern index
    $8058: B9 BE 84    LDA $84be,Y    ; pat_lo[Y]
    $805B: 85 FD       STA $fd        ; ZP $FD
    $805D: B9 E8 84    LDA $84e8,Y    ; pat_hi[Y]
    $8060: 85 FE       STA $fe        ; ZP $FE
    ; Y = pattern byte cursor.
    $8062: BC ED 83    LDY $83ed,X    ; v_patpos,X
    ; Gate mask defaults to $FF (passes everything). Cleared by tie/
    ; legato at L_80C0 to $FE so the inst.ctrl write AND-s out gate.
    $8065: A9 FF       LDA #$ff
    $8067: 8D FF 83    STA $83ff      ; gate-mask = $FF
    ; First pattern byte: (flags<<5) | duration.
    $806A: B1 FD       LDA ($fd),Y    ; pattern flag+dur byte
    $806C: 9D F3 83    STA $83f3,X    ; v_flags,X = raw byte
    $806F: 8D 00 84    STA $8400      ; scratch for BIT below
    $8072: 29 1F       AND #$1f       ; low 5 bits = duration
    $8074: 9D F0 83    STA $83f0,X    ; v_dur,X = duration
    ; BIT $8400: N=bit7, V=bit6. bit6 set = TIE/LEGATO.
    $8077: 2C 00 84    BIT $8400
    $807A: 70 44       BVS $80c0      ; → L_80C0 ; tie: clear gate mask
    ; Non-tie path: clear glissando state for this note (it will be
    ; either re-set below from the inst-byte's bit7 path or left zero).
    $807C: A9 00       LDA #$00
    $807E: 9D 1A 84    STA $841a,X    ; v_gliss,X = 0
    ; Advance past the flag byte.
    $8081: FE ED 83    INC $83ed,X    ; v_patpos,X += 1
    ; Test bit 7 of v_flags: if clear, same instrument (skip 2nd byte).
    $8084: AD 00 84    LDA $8400
    $8087: 10 11       BPL $809a      ; → L_809A ; same inst: jump to pitch
    ; New-byte branch. Read next byte and decide:
    ;   bit7 clear → instrument index (5-bit), store at v_inst,X
    ;   bit7 set   → GLISSANDO command (BoB-specific), store at
    ;                v_gliss,X = $841A,X
    $8089: C8          INY
    $808A: B1 FD       LDA ($fd),Y    ; the second byte
    $808C: 10 06       BPL $8094      ; → L_8094 ; bit7 clear: it's inst
    ; **GLISSANDO branch (BoB only).** Encoded byte format:
    ;   bit7  = enable (already set, gets us here)
    ;   bits6-1 = signed step magnitude (mask AND $7E applied later)
    ;   bit0  = direction (0 = add / slide up; 1 = subtract / slide
    ;            down). Applied each frame by the glissando block at
    ;            $8246..$828A.
    $808E: 9D 1A 84    STA $841a,X    ; v_gliss,X = glissando byte
    $8091: 4C 97 80    JMP $8097      ; → L_8097 ; skip the inst store
L_8094:
    ; Plain new-instrument byte. Stored verbatim — low 5 bits used
    ; later as inst index (ASL ASL ASL → byte offset into $8420).
    $8094: 9D FC 83    STA $83fc,X    ; v_inst,X
L_8097:
    $8097: FE ED 83    INC $83ed,X    ; v_patpos,X += 1 past 2nd byte
L_809A:
    ; Pitch byte (always present): semitone index 0..95.
    $809A: C8          INY
    $809B: B1 FD       LDA ($fd),Y    ; pitch byte
    $809D: 9D F9 83    STA $83f9,X    ; v_pitch,X = raw semitone
    $80A0: 0A          ASL A          ; *2 for table stride
    $80A1: A8          TAY            ; Y = byte offset into freq table
    $80A2: B9 26 83    LDA $8326,Y    ; freq_lo[pitch]
    $80A5: 8D 01 84    STA $8401      ; scratch
    $80A8: B9 27 83    LDA $8327,Y    ; freq_hi[pitch]
    $80AB: AC E9 83    LDY $83e9      ; Y = SID base offset
    $80AE: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y   ; SID freq_hi
    $80B1: 9D 14 84    STA $8414,X                ; v_fhi,X (glissando seed)
    $80B4: AD 01 84    LDA $8401
    $80B7: 99 00 D4    STA $D400 ;V1_FREQ_LO,Y   ; SID freq_lo
    $80BA: 9D 17 84    STA $8417,X                ; v_flo,X (BoB-specific —
                                                  ;          glissando slides
                                                  ;          this too)
    $80BD: 4C C3 80    JMP $80c3      ; → L_80C3 ; instrument apply
L_80C0:
    ; Tie/legato path: clear bit 0 of gate-mask so the ctrl write
    ; below AND-s away the gate bit (gate stays in whatever state
    ; the prior note left it — typically ON, for slurred phrases).
    $80C0: CE FF 83    DEC $83ff      ; gate-mask $FF → $FE
L_80C3:
    ; Apply instrument record. X recalc: inst*8 byte offset.
    $80C3: AC E9 83    LDY $83e9      ; Y = SID base offset
    $80C6: BD FC 83    LDA $83fc,X    ; v_inst,X (raw 5-bit index)
    $80C9: 8E 02 84    STX $8402      ; save voice X
    $80CC: 0A          ASL A          ; *2
    $80CD: 0A          ASL A          ; *4
    $80CE: 0A          ASL A          ; *8
    $80CF: AA          TAX            ; X = inst byte offset
    $80D0: BD 22 84    LDA $8422,X    ; inst.ctrl (+2)
    $80D3: 8D 03 84    STA $8403      ; cache raw ctrl
    $80D6: BD 22 84    LDA $8422,X    ; re-read (cycle padding / code-gen
                                       ;  quirk; same value as above)
    $80D9: 2D FF 83    AND $83ff      ; gate-mask (tie clears gate bit)
    $80DC: 99 04 D4    STA $D404 ;V1_CTRL,Y    ; SID ctrl with gate
    $80DF: BD 20 84    LDA $8420,X    ; inst.pw_lo (+0)
    $80E2: 99 02 D4    STA $D402 ;V1_PW_LO,Y
    $80E5: BD 21 84    LDA $8421,X    ; inst.pw_hi (+1)
    $80E8: 99 03 D4    STA $D403 ;V1_PW_HI,Y
    $80EB: BD 23 84    LDA $8423,X    ; inst.AD (+3)
    $80EE: 99 05 D4    STA $D405 ;V1_AD,Y
    $80F1: BD 24 84    LDA $8424,X    ; inst.SR (+4)
    $80F4: 99 06 D4    STA $D406 ;V1_SR,Y
    $80F7: AE 02 84    LDX $8402      ; restore voice X
    $80FA: AD 03 84    LDA $8403      ; saved raw ctrl
    $80FD: 9D F6 83    STA $83f6,X    ; v_ctrl,X (for HR write later)
    ; Advance v_patpos past pitch byte. Peek next: $FF → pattern end.
    $8100: FE ED 83    INC $83ed,X
    $8103: BC ED 83    LDY $83ed,X
    $8106: B1 FD       LDA ($fd),Y
    $8108: C9 FF       CMP #$ff
    $810A: D0 08       BNE $8114      ; → L_8114 ; not end-of-pattern
    $810C: A9 00       LDA #$00
    $810E: 9D ED 83    STA $83ed,X    ; v_patpos,X = 0
    $8111: FE EA 83    INC $83ea,X    ; v_olpos,X += 1
L_8114:
    $8114: 4C 1F 83    JMP $831f      ; → L_831F ; go to next voice / RTS
; Sustain path (v_dur not yet expired). Hard-restart (HR) test:
; if no_release flag clear AND v_dur reached 0 (i.e. was 1 before
; DEC), write ctrl-without-gate + AD=0 + SR=0 — kills envelope so
; next note's gate-on retriggers cleanly.
L_8117:
    $8117: AC E9 83    LDY $83e9
    $811A: BD F3 83    LDA $83f3,X    ; v_flags,X
    $811D: 29 20       AND #$20       ; bit 5 = no_release
    $811F: D0 15       BNE $8136      ; → L_8136 ; no_release: skip HR
    $8121: BD F0 83    LDA $83f0,X    ; v_dur,X
    $8124: D0 10       BNE $8136      ; → L_8136 ; still ticking: skip HR
    ; HR fires (v_dur went 1 → 0 this frame).
    $8126: BD F6 83    LDA $83f6,X    ; v_ctrl,X (saved inst.ctrl)
    $8129: 29 FE       AND #$fe       ; clear gate
    $812B: 99 04 D4    STA $D404 ;V1_CTRL,Y
    $812E: A9 00       LDA #$00
    $8130: 99 05 D4    STA $D405 ;V1_AD,Y      ; AD = 0
    $8133: 99 06 D4    STA $D406 ;V1_SR,Y      ; SR = 0
; Effects entry. Reached after note-load, after HR, or via the
; "effects-only" trampoline at $803A when the tick gate is closed.
L_8136:
    $8136: BD FC 83    LDA $83fc,X    ; v_inst,X (raw)
    $8139: 0A          ASL A
    $813A: 0A          ASL A
    $813B: 0A          ASL A          ; *8
    $813C: A8          TAY            ; Y = inst byte offset
    $813D: 8C 13 84    STY $8413      ; cache for PWM block
    $8140: B9 27 84    LDA $8427,Y    ; inst.fx_flags (+7)
    $8143: 8D 1D 84    STA $841d      ; cache
    $8146: B9 26 84    LDA $8426,Y    ; inst.pwm_period (+6)
    $8149: 8D 05 84    STA $8405      ; scratch
    $814C: B9 25 84    LDA $8425,Y    ; inst.vib_depth (+5)
    $814F: 8D 04 84    STA $8404      ; vibrato shift count
    $8152: F0 6F       BEQ $81c3      ; → L_81C3 ; vib_depth=0: skip vibrato
    ; ===== Vibrato (triangle LFO from $841F & $07, folded to 0-4) =====
    $8154: AD 1F 84    LDA $841f      ; global frame counter
    $8157: 29 07       AND #$07
    $8159: C9 04       CMP #$04
    $815B: 90 02       BCC $815f      ; → L_815F
    $815D: 49 07       EOR #$07       ; fold 5→2, 6→1, 7→0
L_815F:
    $815F: 8D 0A 84    STA $840a      ; LFO triangle 0..4
    ; Compute delta = (freq[pitch+1] - freq[pitch]) >>> vib_depth
    $8162: BD F9 83    LDA $83f9,X    ; v_pitch,X
    $8165: 0A          ASL A
    $8166: A8          TAY
    $8167: 38          SEC
    $8168: B9 28 83    LDA $8328,Y    ; freq_lo[pitch+1]
    $816B: F9 26 83    SBC $8326,Y    ; - freq_lo[pitch]
    $816E: 8D 06 84    STA $8406      ; delta_lo
    $8171: B9 29 83    LDA $8329,Y    ; freq_hi[pitch+1]
    $8174: F9 27 83    SBC $8327,Y    ; - freq_hi[pitch]
L_8177:
    ; Right-shift the 16-bit delta vib_depth+1 times. Each iter:
    ;   A = upper byte of delta; LSR A; ROR delta_lo.
    $8177: 4A          LSR A
    $8178: 6E 06 84    ROR $8406
    $817B: CE 04 84    DEC $8404
    $817E: 10 F7       BPL $8177      ; → L_8177
    $8180: 8D 07 84    STA $8407      ; delta_hi (shifted)
    ; Seed accumulator with base freq for current pitch.
    $8183: B9 26 83    LDA $8326,Y    ; freq_lo[pitch]
    $8186: 8D 08 84    STA $8408
    $8189: B9 27 83    LDA $8327,Y    ; freq_hi[pitch]
    $818C: 8D 09 84    STA $8409
    ; Short notes (dur<8) skip vibrato (no time to settle).
    $818F: BD F3 83    LDA $83f3,X    ; v_flags
    $8192: 29 1F       AND #$1f       ; duration
    $8194: C9 08       CMP #$08
    $8196: 90 1C       BCC $81b4      ; → L_81B4
    $8198: AC 0A 84    LDY $840a      ; LFO value
L_819B:
    ; Accumulate: freq += delta × LFO_value.
    $819B: 88          DEY
    $819C: 30 16       BMI $81b4      ; → L_81B4
    $819E: 18          CLC
    $819F: AD 08 84    LDA $8408
    $81A2: 6D 06 84    ADC $8406      ; freq_lo += delta_lo
    $81A5: 8D 08 84    STA $8408
    $81A8: AD 09 84    LDA $8409
    $81AB: 6D 07 84    ADC $8407
    $81AE: 8D 09 84    STA $8409      ; freq_hi += delta_hi
    $81B1: 4C 9B 81    JMP $819b      ; → L_819B
L_81B4:
    ; Write modulated freq to SID.
    $81B4: AC E9 83    LDY $83e9
    $81B7: AD 08 84    LDA $8408
    $81BA: 99 00 D4    STA $D400 ;V1_FREQ_LO,Y
    $81BD: AD 09 84    LDA $8409
    $81C0: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
; ===== PWM block =====
; Two modes: fx_flags bit 3 set = simple ascending slide;
;            fx_flags bit 3 clear = bidirectional Hubbard PWM with
;            hardcoded $08/$0E bounds on pw_hi nibble.
L_81C3:
    $81C3: AD 1D 84    LDA $841d      ; fx_flags
    $81C6: 29 08       AND #$08       ; bit 3 = simple PW slide
    $81C8: F0 15       BEQ $81df      ; → L_81DF ; bit3 clear: standard PWM
    ; --- Simple slide mode (BoB-specific) ---
    ; pw_lo += pwm_period each frame; no bounds, no direction flip.
    ; Writes only pw_lo (not pw_hi) → produces a single-byte sweep.
    $81CA: AC 13 84    LDY $8413      ; Y = inst byte offset
    $81CD: B9 20 84    LDA $8420,Y    ; inst.pw_lo
    $81D0: 6D 05 84    ADC $8405      ; + pwm_period
    $81D3: 99 20 84    STA $8420,Y    ; write back inst.pw_lo (mutates table!)
    $81D6: AC E9 83    LDY $83e9
    $81D9: 99 02 D4    STA $D402 ;V1_PW_LO,Y
    $81DC: 4C 46 82    JMP $8246      ; → L_8246 ; skip standard PWM
L_81DF:
    ; --- Standard bidirectional PWM (same as Action Biker) ---
    ; pwm_period byte: low 5 bits = step interval, high 3 bits = step
    ; size (added to / subtracted from pw on each tick).
    $81DF: AD 05 84    LDA $8405      ; pwm_period
    $81E2: F0 62       BEQ $8246      ; → L_8246 ; period=0: no PWM
    $81E4: AC 13 84    LDY $8413
    $81E7: 29 1F       AND #$1f       ; low 5 = step interval
    $81E9: DE 0B 84    DEC $840b,X    ; v_pwm_counter,X -= 1
    $81EC: 10 58       BPL $8246      ; → L_8246 ; not yet time
    $81EE: 9D 0B 84    STA $840b,X    ; reload counter
    $81F1: AD 05 84    LDA $8405
    $81F4: 29 E0       AND #$e0       ; high 3 = step size
    $81F6: 8D 1E 84    STA $841e
    $81F9: BD 0E 84    LDA $840e,X    ; v_pwm_dir,X (0=ADD, !=0=SUB)
    $81FC: D0 1A       BNE $8218      ; → L_8218 ; SUB direction
    ; ADD: pw += step.
    $81FE: AD 1E 84    LDA $841e
    $8201: 18          CLC
    $8202: 79 20 84    ADC $8420,Y    ; pw_lo += step
    $8205: 48          PHA
    $8206: B9 21 84    LDA $8421,Y
    $8209: 69 00       ADC #$00       ; carry into pw_hi
    $820B: 29 0F       AND #$0f       ; 12-bit PW
    $820D: 48          PHA
    $820E: C9 0E       CMP #$0e       ; upper bound HARDCODED
    $8210: D0 1D       BNE $822f      ; → L_822F ; not at bound
    $8212: FE 0E 84    INC $840e,X    ; flip to SUB direction
    $8215: 4C 2F 82    JMP $822f      ; → L_822F
L_8218:
    ; SUB: pw -= step.
    $8218: 38          SEC
    $8219: B9 20 84    LDA $8420,Y
    $821C: ED 1E 84    SBC $841e      ; pw_lo -= step
    $821F: 48          PHA
    $8220: B9 21 84    LDA $8421,Y
    $8223: E9 00       SBC #$00
    $8225: 29 0F       AND #$0f
    $8227: 48          PHA
    $8228: C9 08       CMP #$08       ; lower bound HARDCODED
    $822A: D0 03       BNE $822f      ; → L_822F
    $822C: DE 0E 84    DEC $840e,X    ; flip to ADD direction
L_822F:
    ; Write updated PW back to instrument table AND to SID.
    $822F: 8E 02 84    STX $8402      ; save voice X
    $8232: AE E9 83    LDX $83e9      ; X = SID base offset (yes, ABSx)
    $8235: 68          PLA
    $8236: 99 21 84    STA $8421,Y    ; inst.pw_hi update (table mutation)
    $8239: 9D 03 D4    STA $D403 ;V1_PW_HI,X
    $823C: 68          PLA
    $823D: 99 20 84    STA $8420,Y    ; inst.pw_lo update
    $8240: 9D 02 D4    STA $D402 ;V1_PW_LO,X
    $8243: AE 02 84    LDX $8402      ; restore voice X
; ===== Glissando block (BoB-specific) =====
; Per-voice freq slide. $841A,X format: bit7 enable, bits1-6 step
; (×2 via AND $7E), bit0 direction (0=add, 1=sub).
L_8246:
    $8246: AC E9 83    LDY $83e9
    $8249: BD 1A 84    LDA $841a,X    ; v_gliss,X
    $824C: F0 3F       BEQ $828d      ; → L_828D ; no glissando: skip
    $824E: 29 7E       AND #$7e       ; step magnitude (×2)
    $8250: 8D 02 84    STA $8402      ; scratch
    $8253: BD 1A 84    LDA $841a,X
    $8256: 29 01       AND #$01       ; direction
    $8258: F0 1B       BEQ $8275      ; → L_8275 ; dir=0: ADD
    ; SUB direction: v_flo / v_fhi -= step.
    $825A: 38          SEC
    $825B: BD 17 84    LDA $8417,X    ; v_flo,X
    $825E: ED 02 84    SBC $8402
    $8261: 9D 17 84    STA $8417,X
    $8264: 99 00 D4    STA $D400 ;V1_FREQ_LO,Y
    $8267: BD 14 84    LDA $8414,X    ; v_fhi,X
    $826A: E9 00       SBC #$00       ; borrow
    $826C: 9D 14 84    STA $8414,X
    $826F: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
    $8272: 4C 8D 82    JMP $828d      ; → L_828D
L_8275:
    ; ADD direction: v_flo / v_fhi += step.
    $8275: 18          CLC
    $8276: BD 17 84    LDA $8417,X
    $8279: 6D 02 84    ADC $8402
    $827C: 9D 17 84    STA $8417,X
    $827F: 99 00 D4    STA $D400 ;V1_FREQ_LO,Y
    $8282: BD 14 84    LDA $8414,X
    $8285: 69 00       ADC #$00       ; carry
    $8287: 9D 14 84    STA $8414,X
    $828A: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
; ===== fx_flags bit 0 — DRUM / SKYDIVE =====
; Falling-pitch drum sweep. Per frame:
;   - Compute "frames-into-note" = orig_dur - 1 - v_dur.
;   - If past mid-note (BCC), write current v_fhi and ctrl with
;     test bit set ($80) — silences the oscillator.
;   - Else, write OLD v_fhi and DEC it; write ctrl with gate bit
;     cleared (envelope retains, freq decays).
L_828D:
    $828D: AD 1D 84    LDA $841d      ; fx_flags
    $8290: 29 01       AND #$01       ; bit 0 = drum/skydive
    $8292: F0 35       BEQ $82c9      ; → L_82C9 ; clear: skip
    $8294: BD 14 84    LDA $8414,X    ; v_fhi,X
    $8297: F0 30       BEQ $82c9      ; → L_82C9 ; already 0: skip
    $8299: BD F0 83    LDA $83f0,X    ; v_dur,X
    $829C: F0 2B       BEQ $82c9      ; → L_82C9 ; v_dur=0: skip
    $829E: BD F3 83    LDA $83f3,X    ; v_flags,X (raw)
    $82A1: 29 1F       AND #$1f       ; orig duration
    $82A3: 38          SEC
    $82A4: E9 01       SBC #$01       ; dur - 1
    $82A6: DD F0 83    CMP $83f0,X
    $82A9: AC E9 83    LDY $83e9
    $82AC: 90 10       BCC $82be      ; → L_82BE
    $82AE: BD 14 84    LDA $8414,X    ; pre-DEC v_fhi
    $82B1: DE 14 84    DEC $8414,X    ; v_fhi -= 1
    $82B4: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
    $82B7: BD F6 83    LDA $83f6,X    ; saved v_ctrl
    $82BA: 29 FE       AND #$fe       ; clear gate
    $82BC: D0 08       BNE $82c6      ; → L_82C6 (always nonzero in
                                       ;  practice — ctrl waveform bits)
L_82BE:
    $82BE: BD 14 84    LDA $8414,X    ; final v_fhi
    $82C1: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
    $82C4: A9 80       LDA #$80       ; test bit → silence oscillator
L_82C6:
    $82C6: 99 04 D4    STA $D404 ;V1_CTRL,Y
; ===== fx_flags bit 1 — SLOW DRIFT =====
; Drops v_fhi by 1 on odd frames for long notes. Used on sustained
; pads for a slow ~1 Hz pitch droop.
L_82C9:
    $82C9: AD 1D 84    LDA $841d
    $82CC: 29 02       AND #$02       ; bit 1
    $82CE: F0 1E       BEQ $82ee      ; → L_82EE ; clear: skip
    $82D0: BD F3 83    LDA $83f3,X    ; v_flags
    $82D3: 29 1F       AND #$1f       ; orig dur
    $82D5: C9 0C       CMP #$0c
    $82D7: 90 15       BCC $82ee      ; → L_82EE ; dur<12: skip
    $82D9: AD 1F 84    LDA $841f      ; frame counter
    $82DC: 29 01       AND #$01
    $82DE: F0 0E       BEQ $82ee      ; → L_82EE ; even frame: skip
    $82E0: BD 14 84    LDA $8414,X    ; v_fhi
    $82E3: F0 09       BEQ $82ee      ; → L_82EE ; already 0: skip
    $82E5: DE 14 84    DEC $8414,X    ; v_fhi -= 1
    $82E8: AC E9 83    LDY $83e9
    $82EB: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
; ===== fx_flags bit 2 — OCTAVE ARPEGGIO =====
; Per frame: if frame & 7 != 0, transpose +12 semitones (one octave)
; and write freq. On frame & 7 == 0 write base pitch. Fast shimmer.
L_82EE:
    $82EE: AD 1D 84    LDA $841d
    $82F1: 29 04       AND #$04       ; bit 2
    $82F3: F0 2A       BEQ $831f      ; → L_831F ; clear: skip
    $82F5: AD 1F 84    LDA $841f
    $82F8: 29 07       AND #$07
    $82FA: F0 09       BEQ $8305      ; → L_8305 ; frame%8==0: no transpose
    $82FC: BD F9 83    LDA $83f9,X    ; v_pitch
    $82FF: 18          CLC
    $8300: 69 0C       ADC #$0c       ; +12 semitones
    $8302: 4C 08 83    JMP $8308      ; → L_8308
L_8305:
    $8305: BD F9 83    LDA $83f9,X    ; base pitch
L_8308:
    $8308: 0A          ASL A          ; *2 freq table stride
    $8309: A8          TAY
    $830A: B9 26 83    LDA $8326,Y    ; freq_lo
    $830D: 8D 01 84    STA $8401
    $8310: B9 27 83    LDA $8327,Y    ; freq_hi
    $8313: AC E9 83    LDY $83e9
    $8316: 99 01 D4    STA $D401 ;V1_FREQ_HI,Y
    $8319: AD 01 84    LDA $8401
    $831C: 99 00 D4    STA $D400 ;V1_FREQ_LO,Y
; Per-voice tail: DEX; if negative, RTS. Else loop to next voice.
L_831F:
    $831F: CA          DEX
    $8320: 30 03       BMI $8325      ; → L_8325 ; all 3 done
    $8322: 4C 16 80    JMP $8016      ; → L_8016 ; next voice
L_8325:
    $8325: 60          RTS
; ----- data gap $8326-$8EA9 (2948 bytes) -----
; Layout (see data dump in header):
;   $8326-$83E5  freq table (96 entries × 2 bytes lo/hi)
;   $83E6-$83E8  SID base offset table { $00, $07, $0E }
;   $83E9        scratch (saved Y)
;   $83EA-$83FF  per-voice state arrays (X-indexed) + scalars
;   $8400-$841F  scratch + scalar effect state
;   $8420-...    instrument table (8-byte records)
;   $84B8-$84BA  orderlist ptr lo per voice (V1=$12, V2=$34, V3=$56)
;   $84BB-$84BD  orderlist ptr hi per voice (all $85 → $8512/34/56)
;   $84BE-$84E7  pattern ptr lo table (≤42 patterns)
;   $84E8-...    pattern ptr hi table
;   $8500+       orderlists and packed pattern bytes interleaved.


; ======= init: =======
; A on entry = subtune (sidplayfp passes 0 since songs=1, startSong=1).
; A is IGNORED — BoB's init is a static reset, not subtune-driven.
init:
    $8EAA: A9 00       LDA #$00
    $8EAC: A2 02       LDX #$02       ; loop X = 2..0
L_8EAE:
    ; Zero per-voice state for all 3 voices.
    $8EAE: 9D EA 83    STA $83ea,X    ; v_olpos,X = 0
    $8EB1: 9D ED 83    STA $83ed,X    ; v_patpos,X = 0
    $8EB4: 9D F0 83    STA $83f0,X    ; v_dur,X = 0
    $8EB7: 9D F9 83    STA $83f9,X    ; v_pitch,X = 0
    $8EBA: CA          DEX
    $8EBB: 10 F1       BPL $8eae      ; → L_8EAE
    ; Silence SID voices; set master volume.
    $8EBD: 8D 04 D4    STA $D404 ;V1_CTRL
    $8EC0: 8D 0B D4    STA $D40B ;V2_CTRL
    $8EC3: 8D 12 D4    STA $D412 ;V3_CTRL
    $8EC6: A9 0F       LDA #$0f
    $8EC8: 8D 18 D4    STA $D418 ;VOL
    $8ECB: 60          RTS
; NOTE: init does NOT zero $8411 (tick divider), $8412 (reload),
;       $8414/$8417,X (v_fhi/v_flo), $841A,X (v_gliss), $840B/$840E,X
;       (pwm state), $841F (frame counter), $83F3,X (v_flags),
;       $83F6,X (v_ctrl), $83FC,X (v_inst), or the instrument table
;       at $8420 (which gets MUTATED at runtime by the PWM block!).
;       Those rely on baked-in binary initial values:
;         $8411=$00, $8412=$01, $841F=$DC, $8420.. = instrument data.
;       Replaying the song after song-end requires either re-loading
;       the binary or replicating these initial values. The simple-
;       slide PWM mode (fx_flags bit 3) further depends on the
;       binary's pw_lo bytes being at their as-shipped values, since
;       it mutates them over time without bound or reset.
; ----- data gap $8ECC-$8FFF (308 bytes) -----
; Tail data: more pattern bodies (the orderlist of V3 starts at
; $8556 and packed pattern data fills the region up to $8FFF).
