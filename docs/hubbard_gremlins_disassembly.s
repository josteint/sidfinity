; ============================================================================
; Rob Hubbard - Gremlins (1985 Adventure International / 1984 Atarisoft port)
; ANNOTATED DISASSEMBLY (auto-generated seed; selectively hand-annotated)
; ============================================================================
;
; Binary: data/C64Music/MUSICIANS/H/Hubbard_Rob/Gremlins.sid
; Load:   $1000   Init: $1530   Play: $1012
; PSID:   26 subtunes, default subtune 1 (1-indexed; A=0 passed to init)
; Binary: $1000-$2E8C (7821 bytes)
;
; Auto-traced 1532 reachable code bytes from init+play (19.6% of payload).
; Layout commentary hand-derived from static analysis cross-checked against
; pipelines/gremlins/extract/engine_model.py.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; This is the same early-Hubbard engine family as Action Biker, expanded
; with a 19-entry sound-effect dispatcher. The first 7 subtunes (0-6 in
; PSID 1-indexed: PSID #1-#7) are music; subtunes 7-25 (PSID #8-#26)
; are sound effects routed through a different setup path.
;
; PSID jump table at $1000 (only used by init, never PSID-entered):
;   $1000: JMP $198A   ; music subtune setup (called from init A<7)
;   $1003: JMP $19B8   ; "silence music" entry — sets $16EE bit 7 (sub_1003)
;   $1006: JMP $19BE   ; "clear sfx state" entry — zeros $16FB (sub_1006)
;   $1009-$100E: 6-byte gap
;   $100F: JMP $19CC   ; sfx subtune setup (called from init A>=7)
;
; init ($1530): A = subtune (0-indexed).
;   1. Save A in $1555.
;   2. JSR $1003 → $16EE = $C0  (bit 7 + bit 6: stops any old music)
;   3. JSR $1006 → $16FB = $00  (clears "sfx running" flag)
;   4. CMP #$07: A<7 = music subtune, A>=7 = sfx
;   5. Music path: STA $1556; JMP $1000 → $198A (build orderlist ptrs)
;   6. SFX path:   SBC #$07; STA $1556; JMP $100F → $19CC (sfx dispatch)
;
; play ($1012): every frame.
;   1. INC $16FA (global frame counter — used by vibrato LFO, arp, etc.)
;   2. BIT $16EE — N = bit 7 (music silenced), V = bit 6 (first-frame).
;      - Both bits clear → JMP $1052 (normal play, no setup needed)
;      - bit 6 set, bit 7 clear → first-frame voice-state zero + JMP $1052
;      - bit 7 set, bit 6 clear → JMP $139F (sfx-only path, music muted)
;      - both bits set → silence V1/V2/V3 ctrl, VOL=$0F, mark "silenced"
;        ($16EE = $80), then JMP $139F.
;   3. $1052: load X = 2 (V3 first), DEC the SHARED tempo counter $16EB.
;      When it wraps (BPL not taken), reload from $16EC.
;   4. Per-voice loop at $105F: process V3, V2, V1.
;   5. After last voice: $139F — sfx tick.
;
; PER-VOICE PROCESSING ($105F..$1389):
;   - X holds voice index (2..0); Y mirrors SID register offset.
;   - **Note-load gate** at $1066: only load a new note when $16EB has
;     JUST been reloaded (i.e. $16EB == $16EC). Identical to Action Biker's
;     $C3E7/$C3E8 gating; defers first note by `speed` frames.
;   - Note-load path branches on the orderlist byte:
;       $FF        → loop back (zero v_olpos/v_patpos/v_dur, retry).
;       else       → pattern index, look up pat_lo[Y]/pat_hi[Y] at $1A52/$1AC1.
;     There is NO $FE song-end sentinel in Gremlins — every track loops.
;   - Pattern decoding (same byte layout as Action Biker):
;       byte 0: flags<<5 | duration (low 5)
;         bit 7 → "new instrument or skydive command follows"
;         bit 6 → tie/legato (skip pitch read; AND $FE on ctrl)
;         bit 5 → no_release (skip the v_dur==0 hard-restart at $1172)
;         bits 0-4 → duration in ticks
;       byte 1 (if bit 7 set, see below): either v_inst OR portamento packet
;       byte N (always): pitch (0..K-1, ASL'd to index freq table at $1600).
;
;   - **PORTAMENTO byte (per-note, NOT a flag):** at $10D5 the engine
;     splits the "new-info" byte on its OWN bit 7:
;       bit 7 CLEAR → byte is a new instrument index → STA v_inst,X
;       bit 7 SET   → byte is a portamento packet  → STA $16F5,X (v_porta)
;                       bits 1..6 = step delta
;                       bit 0     = direction (0=up, 1=down)
;     This is the "skydive" hand-coded mechanism Gremlins uses for
;     ascending/descending pitch sweeps within a single note. It's the
;     *per-note* slide; do not confuse with the *per-instrument* skydive
;     (fx_flags bit 1) below.
;
; INSTRUMENT TABLE: $1784, 8-byte records (same layout as Action Biker).
;     +0 pw_lo   +1 pw_hi   +2 ctrl   +3 AD   +4 SR
;     +5 vib_dep +6 vib_per +7 fx_flags
;
;   fx_flags semantics (per `extract/engine_model.py`):
;     bit 0 → drum: kill envelope + ramp freq_hi down in second half of
;             the note (the same $12F0 routine as Action Biker's $C24B).
;     bit 1 → skydive: DEC v_fhi when (orig_dur>=12) AND (v_dur<8)
;             AND (frame_counter & 1). A long-held note's tail swoops.
;             [block $132C-$1357]
;     bit 2 → octave arp: alternate pitch ↔ pitch+12 each frame from the
;             global frame counter's bit 0. [block $1358-$1388]
;     bit 3 → PWM linear: pulse_lo += pwm_speed (8-bit wrap, free-running).
;             cleared = bidirectional bounce between $08/$0E in pulse_hi.
;             [block $1242-$12A8]
;
; FREQ TABLE: $1600, 96+ semitone entries packed (lo[i], hi[i]) 2-byte stride.
;   Hubbard reads PAST the table for the octave-arp (+12) effect, so
;   engine_model.extract() extends T[] beyond 96 by re-running init/play
;   in py65 and snapshotting memory at ft_base. See discover.py.
;
; PATTERN-PTR TABLES: pat_lo at $1A52, pat_hi at $1AC1.
; ORDERLIST PTRS (per active voice, copied in by $198A): $1984..$1989.
; SUBTUNE ORDERLIST POINTER TABLE: $1A28+ (subtune * 6 bytes = 3 voices ×
;   {lo, hi}).
;
; SFX MUTING ($1389):
;   $16FD is a per-frame "music writes enabled" gate.
;     $FF → music's per-voice freq/ctrl/pw writes go through.
;     $00 → SFX is driving the same voices → all music SID writes are
;           skipped (gate checked at $10EB, $1124, $116A, $1191).
;   $16FD is recomputed at $1389 every frame: enabled if $16FB != 0
;   OR $16FC has bit 7 set; otherwise disabled.
;
; CONSEQUENCE FOR CODEGEN:
;   - Same one-frame first-note defer as Action Biker (the $16EB/$16EC
;     reload gate at $1066-$106C).
;   - Skydive (per-note portamento) is encoded in the new-info byte and
;     processed at $12A9-$12EF (not in the instrument table).
;   - The pulse_hi bidirectional bounds $08/$0E are HARDCODED here at
;     $1271 / $128B — see reference_hubbard_pwm_bounds.md.
;
; ============================================================================

; PSID jump table at $1000. Only ever entered from init() via JMP — never
; called by sidplayfp directly.
L_1000:
    $1000: 4C 8A 19    JMP $198A          ; → music subtune setup
sub_1003:
    ; "silence music" — sets bit 7 + bit 6 on $16EE. Bit 7 latches the
    ; "music muted" state; bit 6 is cleared by play's first-frame setup.
    $1003: 4C B8 19    JMP $19B8          ; → sub_19B8
sub_1006:
    ; "clear sfx state" — zeros $16FB so the sfx subtune dispatcher knows
    ; there's no sfx running yet.
    $1006: 4C BE 19    JMP $19BE          ; → sub_19BE
; ----- data gap $1009-$100E (6 bytes; jump-table padding / unreachable) -----

L_100F:
    $100F: 4C CC 19    JMP $19CC          ; → sfx subtune dispatch

; ======= play: =======
; Called every frame by sidplayfp.
play:
    ; Global frame counter (cycles 0..255 forever). Used by vibrato LFO,
    ; octave-arp toggle, and the skydive "every-other-frame" gate.
    $1012: EE FA 16    INC $16FA
    ; $16EE state byte: N = bit 7 ("music silenced"), V = bit 6 ("first
    ; frame of a freshly-started subtune").
    $1015: 2C EE 16    BIT $16EE
    $1018: 30 1E       BMI $1038          ; → L_1038   ; silenced path
    $101A: 50 36       BVC $1052          ; → L_1052   ; normal play
    ; Bit 6 set + bit 7 clear → first-frame voice-state zero.
    $101C: A9 00       LDA #$00
    $101E: 8D FA 16    STA $16FA          ; reset frame counter
    $1021: A2 02       LDX #$02
L_1023:
    ; Clear per-voice state: v_olpos, v_patpos, v_dur, v_pitch for X=2..0.
    $1023: 9D C4 16    STA $16C4,X        ; v_olpos,X
    $1026: 9D C7 16    STA $16C7,X        ; v_patpos,X
    $1029: 9D CA 16    STA $16CA,X        ; v_dur,X
    $102C: 9D D3 16    STA $16D3,X        ; v_pitch,X
    $102F: CA          DEX
    $1030: 10 F1       BPL $1023          ; → L_1023
    $1032: 8D EE 16    STA $16EE          ; $16EE = $00 (both bits cleared)
    $1035: 4C 52 10    JMP $1052          ; → L_1052   ; fall through to play

L_1038:
    ; Silenced path (bit 7 set). If bit 6 also set this is the FIRST frame
    ; of the silenced state — actively kill voice ctrls and lock VOL.
    $1038: 50 15       BVC $104F          ; → L_104F   ; not first-silence
    $103A: A9 00       LDA #$00
    $103C: 8D 04 D4    STA $D404          ; V1_CTRL = 0
    $103F: 8D 0B D4    STA $D40B          ; V2_CTRL = 0
    $1042: 8D 12 D4    STA $D412          ; V3_CTRL = 0
    $1045: A9 0F       LDA #$0F
    $1047: 8D 18 D4    STA $D418          ; VOL = $0F
    $104A: A9 80       LDA #$80
    $104C: 8D EE 16    STA $16EE          ; $16EE = $80 (latch silenced,
                                          ;  clear first-frame bit)
L_104F:
    $104F: 4C 9F 13    JMP $139F          ; → L_139F   ; sfx-only tick

L_1052:
    ; Per-voice loop entry.
    $1052: A2 02       LDX #$02           ; X = V3 first
    ; SHARED tempo counter ($16EB reloads from $16EC). Decremented ONCE
    ; per frame, before the voice loop — all 3 voices fire on the same
    ; tick. On reload, $16EB == $16EC for that one frame, which is
    ; precisely the note-load condition at $1066-$106C.
    $1054: CE EB 16    DEC $16EB
    $1057: 10 06       BPL $105F          ; → L_105F   ; not wrapped
    $1059: AD EC 16    LDA $16EC          ; wrap: reload
    $105C: 8D EB 16    STA $16EB

L_105F:
    ; Per-voice SID-base lookup. $16C0,X holds the SID register offset
    ; for voice X (0/7/14). Saved at $16C3 as Y-index for SID writes.
    $105F: BD C0 16    LDA $16C0,X
    $1062: 8D C3 16    STA $16C3
    $1065: A8          TAY
    ; **NOTE-LOAD GATE**: only run note-load when $16EB just landed back
    ; on its reload value. This is what defers the first note by
    ; `speed` frames after init — same mechanism as Action Biker's
    ; $C3E7/$C3E8.
    $1066: AD EB 16    LDA $16EB
    $1069: CD EC 16    CMP $16EC
    $106C: D0 15       BNE $1083          ; → L_1083   ; skip note-load
    ; ($FB):Y per-voice orderlist pointer. $1984+X lo, $1987+X hi.
    $106E: BD 84 19    LDA $1984,X        ; orderlist ptr lo
    $1071: 85 FB       STA $FB
    $1073: BD 87 19    LDA $1987,X        ; orderlist ptr hi
    $1076: 85 FC       STA $FC
    ; v_dur,X countdown; if expired (BMI), load next note.
    $1078: DE CA 16    DEC $16CA,X
    $107B: 30 09       BMI $1086          ; → L_1086   ; expired: new note
    $107D: 4C 6A 11    JMP $116A          ; → L_116A   ; sustain current
; ----- data gap $1080-$1082 (3 bytes) -----

L_1083:
    ; Note-load gated off this frame → run effects only.
    $1083: 4C 91 11    JMP $1191          ; → L_1191

L_1086:
    ; New note: read orderlist[v_olpos]. $FF = loop back to start of
    ; orderlist (no song-end sentinel — Gremlins's music loops forever).
    $1086: BC C4 16    LDY $16C4,X
    $1089: B1 FB       LDA ($FB),Y        ; orderlist[v_olpos]
    $108B: C9 FF       CMP #$FF
    $108D: D0 11       BNE $10A0          ; → L_10A0   ; normal pattern
    $108F: A9 00       LDA #$00
    $1091: 9D CA 16    STA $16CA,X        ; v_dur = 0
    $1094: 9D C4 16    STA $16C4,X        ; v_olpos = 0
    $1097: 9D C7 16    STA $16C7,X        ; v_patpos = 0
    $109A: 4C 86 10    JMP $1086          ; → retry from orderlist[0]
; ----- data gap $109D-$109F (3 bytes) -----

L_10A0:
    ; Pattern lookup: A = pattern idx, indirect via pat_lo[A]/pat_hi[A].
    $10A0: A8          TAY
    $10A1: B9 52 1A    LDA $1A52,Y        ; pat_lo[Y]
    $10A4: 85 FD       STA $FD            ; ZP $FD = pat_lo
    $10A6: B9 C1 1A    LDA $1AC1,Y        ; pat_hi[Y]
    $10A9: 85 FE       STA $FE            ; ZP $FE = pat_hi
    ; Clear v_porta (per-note portamento byte) for the new note. Will be
    ; rewritten below if the pattern's new-info byte has bit 7 set.
    $10AB: A9 00       LDA #$00
    $10AD: 9D F5 16    STA $16F5,X        ; v_porta,X = 0
    ; Y = byte offset within pattern (advances as we consume note bytes).
    $10B0: BC C7 16    LDY $16C7,X        ; v_patpos,X
    ; $16D9 = "ctrl gate mask"; default $FF (gate passes). Cleared by
    ; DEC at $110E for tie/legato notes (so STA V1_CTRL ANDs the gate off).
    $10B3: A9 FF       LDA #$FF
    $10B5: 8D D9 16    STA $16D9          ; gate-mask = $FF
    ; First pattern byte = flags<<5 | duration. Same encoding as
    ; Action Biker / Commando.
    $10B8: B1 FD       LDA ($FD),Y
    $10BA: 9D CD 16    STA $16CD,X        ; v_flags,X = raw byte
    $10BD: 8D DA 16    STA $16DA          ; save for BIT test
    $10C0: 29 1F       AND #$1F           ; duration only
    $10C2: 9D CA 16    STA $16CA,X        ; v_dur,X
    ; BIT $16DA: N = bit 7 (new-info byte follows), V = bit 6 (tie).
    $10C5: 2C DA 16    BIT $16DA
    $10C8: 70 44       BVS $110E          ; → L_110E   ; tie: skip rest
    $10CA: FE C7 16    INC $16C7,X        ; advance past flag byte
    $10CD: AD DA 16    LDA $16DA
    $10D0: 10 11       BPL $10E3          ; → L_10E3   ; no new-info byte
    ; New-info byte present. Bit 7 of the BYTE ITSELF distinguishes:
    ;   bit 7 set   → portamento packet (per-note pitch slide).
    ;   bit 7 clear → new instrument index.
    $10D2: C8          INY
    $10D3: B1 FD       LDA ($FD),Y
    $10D5: 10 06       BPL $10DD          ; → L_10DD   ; new instrument
    ; Portamento: store full byte at v_porta (bits 1..6 = delta, bit 0 = dir).
    $10D7: 9D F5 16    STA $16F5,X        ; v_porta,X
    $10DA: 4C E0 10    JMP $10E0          ; → L_10E0
L_10DD:
    ; New instrument index. Bit 7 was clear so byte is the inst # directly.
    ; Note: there's NO AND #$1F mask here (Action Biker did one) — the
    ; encoding already guarantees bit 7 = 0 means "inst".
    $10DD: 9D D6 16    STA $16D6,X        ; v_inst,X
L_10E0:
    $10E0: FE C7 16    INC $16C7,X        ; advance past new-info byte
L_10E3:
    ; Pitch byte. ASL doubles for the 2-byte stride at freq_table $1600.
    $10E3: C8          INY
    $10E4: B1 FD       LDA ($FD),Y
    $10E6: 9D D3 16    STA $16D3,X        ; v_pitch,X
    $10E9: 0A          ASL A              ; *2 for table stride
    $10EA: A8          TAY                ; Y = freq table byte offset
    ; **SFX MUTING GATE**: $16FD = $00 means sfx is using this voice;
    ; skip the freq write. See $1389 for how $16FD is computed.
    $10EB: AD FD 16    LDA $16FD
    $10EE: 10 21       BPL $1111          ; → L_1111   ; sfx active: skip
    $10F0: B9 00 16    LDA $1600,Y        ; freq_lo[pitch]
    $10F3: 8D DB 16    STA $16DB          ; temp save
    $10F6: B9 01 16    LDA $1601,Y        ; freq_hi[pitch]
    $10F9: AC C3 16    LDY $16C3          ; Y = SID voice offset
    $10FC: 99 01 D4    STA $D401,Y        ; V1_FREQ_HI,Y
    $10FF: 9D EF 16    STA $16EF,X        ; v_fhi,X (saved for slide)
    $1102: AD DB 16    LDA $16DB
    $1105: 99 00 D4    STA $D400,Y        ; V1_FREQ_LO,Y
    $1108: 9D F2 16    STA $16F2,X        ; v_flo,X (saved for slide)
    $110B: 4C 11 11    JMP $1111          ; → L_1111
L_110E:
    ; Tie/legato note: clear gate-mask bit 0 so the ctrl AND below
    ; AND-s the gate away.
    $110E: CE D9 16    DEC $16D9          ; $FF → $FE

L_1111:
    ; Write instrument record (8 bytes at $1784 + inst*8) to SID for this
    ; voice. Same field layout as Action Biker.
    $1111: AC C3 16    LDY $16C3          ; Y = SID voice offset
    $1114: BD D6 16    LDA $16D6,X        ; v_inst,X
    $1117: 8E DC 16    STX $16DC          ; save voice index
    $111A: 0A          ASL A              ; inst * 2
    $111B: 0A          ASL A              ; inst * 4
    $111C: 0A          ASL A              ; inst * 8
    $111D: AA          TAX                ; X = inst byte offset
    $111E: BD 86 17    LDA $1786,X        ; inst.ctrl
    $1121: 8D DD 16    STA $16DD          ; stash raw ctrl
    ; Sfx-mute gate again before writing voice regs.
    $1124: AD FD 16    LDA $16FD
    $1127: 10 21       BPL $114A          ; → L_114A   ; sfx active: skip
    $1129: BD 86 17    LDA $1786,X        ; inst.ctrl
    $112C: 2D D9 16    AND $16D9          ; AND gate-mask (tie kills gate)
    $112F: 99 04 D4    STA $D404,Y        ; V1_CTRL,Y
    $1132: BD 84 17    LDA $1784,X        ; inst.pw_lo
    $1135: 99 02 D4    STA $D402,Y        ; V1_PW_LO,Y
    $1138: BD 85 17    LDA $1785,X        ; inst.pw_hi
    $113B: 99 03 D4    STA $D403,Y        ; V1_PW_HI,Y
    $113E: BD 87 17    LDA $1787,X        ; inst.AD
    $1141: 99 05 D4    STA $D405,Y        ; V1_AD,Y
    $1144: BD 88 17    LDA $1788,X        ; inst.SR
    $1147: 99 06 D4    STA $D406,Y        ; V1_SR,Y
L_114A:
    ; Restore voice X and stash inst.ctrl to v_ctrl for later HR.
    $114A: AE DC 16    LDX $16DC
    $114D: AD DD 16    LDA $16DD
    $1150: 9D D0 16    STA $16D0,X        ; v_ctrl,X
    ; Advance v_patpos past pitch byte. Peek next byte: $FF = end-of-pattern.
    $1153: FE C7 16    INC $16C7,X
    $1156: BC C7 16    LDY $16C7,X
    $1159: B1 FD       LDA ($FD),Y
    $115B: C9 FF       CMP #$FF
    $115D: D0 08       BNE $1167          ; → L_1167   ; mid-pattern
    $115F: A9 00       LDA #$00
    $1161: 9D C7 16    STA $16C7,X        ; v_patpos = 0
    $1164: FE C4 16    INC $16C4,X        ; v_olpos += 1
L_1167:
    $1167: 4C 89 13    JMP $1389          ; → L_1389   ; effects done

; Sustain path: note still ticking. Run the hard-restart check then
; fall through to effects.
L_116A:
    ; Sfx-mute gate.
    $116A: AD FD 16    LDA $16FD
    $116D: 30 03       BMI $1172          ; → L_1172   ; music enabled
    $116F: 4C 89 13    JMP $1389          ; → L_1389   ; sfx: skip
L_1172:
    $1172: AC C3 16    LDY $16C3
    ; no_release (flags bit 5) suppresses the hard-restart on dur expiry.
    $1175: BD CD 16    LDA $16CD,X
    $1178: 29 20       AND #$20
    $117A: D0 15       BNE $1191          ; → L_1191   ; no_release: skip
    $117C: BD CA 16    LDA $16CA,X
    $117F: D0 10       BNE $1191          ; → L_1191   ; still ticking
    ; v_dur hit zero: kill gate + envelope so the next note retriggers.
    $1181: BD D0 16    LDA $16D0,X        ; v_ctrl,X
    $1184: 29 FE       AND #$FE           ; clear gate bit
    $1186: 99 04 D4    STA $D404,Y        ; V1_CTRL,Y
    $1189: A9 00       LDA #$00
    $118B: 99 05 D4    STA $D405,Y        ; V1_AD,Y
    $118E: 99 06 D4    STA $D406,Y        ; V1_SR,Y

L_1191:
    ; Per-voice EFFECTS block: vibrato → PWM → drum slide → skydive
    ; → octave arp → epilogue. The sfx-mute gate at $1191 short-circuits
    ; this block if music is muted on this voice.
    $1191: AD FD 16    LDA $16FD
    $1194: 30 03       BMI $1199          ; → L_1199
    $1196: 4C 89 13    JMP $1389          ; → L_1389
L_1199:
    ; Vibrato block — identical structure to Action Biker $C157.
    ; Y = inst * 8 (byte offset into inst table).
    $1199: BD D6 16    LDA $16D6,X
    $119C: 0A          ASL A
    $119D: 0A          ASL A
    $119E: 0A          ASL A
    $119F: A8          TAY
    $11A0: 8C ED 16    STY $16ED          ; remember inst byte offset
    ; Read inst.fx_flags (+7), inst.vib_period (+6), inst.vib_depth (+5).
    $11A3: B9 8B 17    LDA $178B,Y        ; inst.fx_flags  ($1784+7=$178B,Y)
    $11A6: 8D F8 16    STA $16F8
    $11A9: B9 8A 17    LDA $178A,Y        ; inst.vib_period
    $11AC: 8D DF 16    STA $16DF
    $11AF: B9 89 17    LDA $1789,Y        ; inst.vib_depth
    $11B2: 8D DE 16    STA $16DE
    $11B5: F0 6F       BEQ $1226          ; → L_1226   ; depth=0: no vibrato
    ; Triangle LFO from $16FA's low 3 bits.
    $11B7: AD FA 16    LDA $16FA
    $11BA: 29 07       AND #$07
    $11BC: C9 04       CMP #$04
    $11BE: 90 02       BCC $11C2          ; → L_11C2
    $11C0: 49 07       EOR #$07           ; fold 5→2, 6→1, 7→0
L_11C2:
    $11C2: 8D E4 16    STA $16E4          ; LFO triangle value (0-4)
    ; delta = (freq[pitch+1] - freq[pitch]) >> vib_depth bits.
    $11C5: BD D3 16    LDA $16D3,X        ; v_pitch,X
    $11C8: 0A          ASL A
    $11C9: A8          TAY
    $11CA: 38          SEC
    $11CB: B9 02 16    LDA $1602,Y        ; freq_lo[pitch+1]
    $11CE: F9 00 16    SBC $1600,Y        ; minus freq_lo[pitch]
    $11D1: 8D E0 16    STA $16E0          ; delta_lo
    $11D4: B9 03 16    LDA $1603,Y        ; freq_hi[pitch+1]
    $11D7: F9 01 16    SBC $1601,Y        ; minus freq_hi[pitch]
L_11DA:
    ; Right-shift delta by vib_depth bits.
    $11DA: 4A          LSR A
    $11DB: 6E E0 16    ROR $16E0
    $11DE: CE DE 16    DEC $16DE
    $11E1: 10 F7       BPL $11DA          ; → L_11DA
    $11E3: 8D E1 16    STA $16E1          ; delta_hi (shifted)
    ; Load base freq for current pitch.
    $11E6: B9 00 16    LDA $1600,Y
    $11E9: 8D E2 16    STA $16E2
    $11EC: B9 01 16    LDA $1601,Y
    $11EF: 8D E3 16    STA $16E3
    ; Short notes (dur < 8) skip vibrato sum — no time to settle.
    $11F2: BD CD 16    LDA $16CD,X
    $11F5: 29 1F       AND #$1F
    $11F7: C9 08       CMP #$08
    $11F9: 90 1C       BCC $1217          ; → L_1217   ; short note
    $11FB: AC E4 16    LDY $16E4          ; LFO value
L_11FE:
    ; Accumulate delta LFO times into freq.
    $11FE: 88          DEY
    $11FF: 30 16       BMI $1217          ; → L_1217
    $1201: 18          CLC
    $1202: AD E2 16    LDA $16E2
    $1205: 6D E0 16    ADC $16E0
    $1208: 8D E2 16    STA $16E2
    $120B: AD E3 16    LDA $16E3
    $120E: 6D E1 16    ADC $16E1
    $1211: 8D E3 16    STA $16E3
    $1214: 4C FE 11    JMP $11FE          ; → L_11FE
L_1217:
    ; Write modulated freq to SID.
    $1217: AC C3 16    LDY $16C3
    $121A: AD E2 16    LDA $16E2
    $121D: 99 00 D4    STA $D400,Y        ; V1_FREQ_LO,Y
    $1220: AD E3 16    LDA $16E3
    $1223: 99 01 D4    STA $D401,Y        ; V1_FREQ_HI,Y

L_1226:
    ; PWM block. fx_flags bit 3 selects mode:
    ;   bit 3 set   → linear: pw_lo += pwm_speed (free-running 8-bit wrap)
    ;   bit 3 clear → bidirectional: pw_hi bounces between $08 and $0E
    $1226: AD F8 16    LDA $16F8          ; fx_flags
    $1229: 29 08       AND #$08
    $122B: F0 15       BEQ $1242          ; → L_1242   ; bidirectional
    ; Linear mode: pw_lo += pwm_speed. pwm_speed is the inst.vib_period
    ; byte saved at $16DF (Hubbard overloads this byte).
    $122D: AC ED 16    LDY $16ED          ; inst byte offset
    $1230: B9 84 17    LDA $1784,Y        ; inst.pw_lo
    $1233: 6D DF 16    ADC $16DF          ; += pwm_speed
    $1236: 99 84 17    STA $1784,Y        ; write back into inst table
    $1239: AC C3 16    LDY $16C3
    $123C: 99 02 D4    STA $D402,Y        ; V1_PW_LO,Y
    $123F: 4C A9 12    JMP $12A9          ; → L_12A9

L_1242:
    ; Bidirectional PWM with HARDCODED bounds $08 / $0E (see reference
    ; memory: Hubbard PWM bounds). speed = low 5 bits of vib_period byte,
    ; step magnitude = high 3 bits of same byte. Direction stored at
    ; $16E8,X (0 = adding, nonzero = subtracting).
    $1242: AD DF 16    LDA $16DF          ; vib_period (= pwm_speed byte)
    $1245: F0 62       BEQ $12A9          ; → L_12A9   ; period=0: no PWM
    $1247: AC ED 16    LDY $16ED          ; inst byte offset
    $124A: 29 1F       AND #$1F           ; low 5 bits = step interval
    $124C: DE E5 16    DEC $16E5,X        ; voice's step counter
    $124F: 10 58       BPL $12A9          ; → L_12A9   ; not yet
    $1251: 9D E5 16    STA $16E5,X        ; reload step counter
    $1254: AD DF 16    LDA $16DF
    $1257: 29 E0       AND #$E0           ; high 3 bits = step size
    $1259: 8D F9 16    STA $16F9
    $125C: BD E8 16    LDA $16E8,X        ; voice's pwm direction
    $125F: D0 1A       BNE $127B          ; → L_127B   ; nonzero: SUB
    ; ADD direction: pw += step.
    $1261: AD F9 16    LDA $16F9
    $1264: 18          CLC
    $1265: 79 84 17    ADC $1784,Y        ; pw_lo += step
    $1268: 48          PHA
    $1269: B9 85 17    LDA $1785,Y
    $126C: 69 00       ADC #$00           ; carry into pw_hi
    $126E: 29 0F       AND #$0F           ; pw_hi is 12-bit (low 4 of byte)
    $1270: 48          PHA
    $1271: C9 0E       CMP #$0E           ; hit upper bound?
    $1273: D0 1D       BNE $1292          ; → L_1292
    $1275: FE E8 16    INC $16E8,X        ; flip direction → SUB
    $1278: 4C 92 12    JMP $1292          ; → L_1292
L_127B:
    ; SUB direction: pw -= step.
    $127B: 38          SEC
    $127C: B9 84 17    LDA $1784,Y
    $127F: ED F9 16    SBC $16F9
    $1282: 48          PHA
    $1283: B9 85 17    LDA $1785,Y
    $1286: E9 00       SBC #$00
    $1288: 29 0F       AND #$0F
    $128A: 48          PHA
    $128B: C9 08       CMP #$08           ; hit lower bound?
    $128D: D0 03       BNE $1292          ; → L_1292
    $128F: DE E8 16    DEC $16E8,X        ; flip direction → ADD
L_1292:
    ; Write updated pw back to instrument record AND to SID.
    $1292: 8E DC 16    STX $16DC          ; save voice X
    $1295: AE C3 16    LDX $16C3          ; X = SID offset
    $1298: 68          PLA
    $1299: 99 85 17    STA $1785,Y        ; inst.pw_hi
    $129C: 9D 03 D4    STA $D403,X        ; V1_PW_HI,X
    $129F: 68          PLA
    $12A0: 99 84 17    STA $1784,Y        ; inst.pw_lo
    $12A3: 9D 02 D4    STA $D402,X        ; V1_PW_LO,X
    $12A6: AE DC 16    LDX $16DC          ; restore voice X

L_12A9:
    ; PORTAMENTO ("per-note skydive") block. v_porta,X was set from the
    ; pattern's new-info byte when its bit 7 was set (see $10D7).
    ;   v_porta bits 1..6 → step magnitude (AND #$7E)
    ;   v_porta bit 0     → direction (0=up, 1=down)
    $12A9: AC C3 16    LDY $16C3
    $12AC: BD F5 16    LDA $16F5,X        ; v_porta,X
    $12AF: F0 3F       BEQ $12F0          ; → L_12F0   ; no portamento
    $12B1: 29 7E       AND #$7E           ; step magnitude
    $12B3: 8D DC 16    STA $16DC
    $12B6: BD F5 16    LDA $16F5,X
    $12B9: 29 01       AND #$01
    $12BB: F0 1B       BEQ $12D8          ; → L_12D8   ; ascend
    ; Descend: v_freq -= step.
    $12BD: 38          SEC
    $12BE: BD F2 16    LDA $16F2,X        ; v_flo,X
    $12C1: ED DC 16    SBC $16DC
    $12C4: 9D F2 16    STA $16F2,X
    $12C7: 99 00 D4    STA $D400,Y        ; V1_FREQ_LO,Y
    $12CA: BD EF 16    LDA $16EF,X        ; v_fhi,X
    $12CD: E9 00       SBC #$00
    $12CF: 9D EF 16    STA $16EF,X
    $12D2: 99 01 D4    STA $D401,Y        ; V1_FREQ_HI,Y
    $12D5: 4C F0 12    JMP $12F0          ; → L_12F0
L_12D8:
    ; Ascend: v_freq += step.
    $12D8: 18          CLC
    $12D9: BD F2 16    LDA $16F2,X
    $12DC: 6D DC 16    ADC $16DC
    $12DF: 9D F2 16    STA $16F2,X
    $12E2: 99 00 D4    STA $D400,Y        ; V1_FREQ_LO,Y
    $12E5: BD EF 16    LDA $16EF,X
    $12E8: 69 00       ADC #$00
    $12EA: 9D EF 16    STA $16EF,X
    $12ED: 99 01 D4    STA $D401,Y        ; V1_FREQ_HI,Y

L_12F0:
    ; Drum block. fx_flags bit 0 = "drum / falling freq slide". Identical
    ; semantics to Action Biker's $C24B block.
    $12F0: AD F8 16    LDA $16F8          ; fx_flags
    $12F3: 29 01       AND #$01
    $12F5: F0 35       BEQ $132C          ; → L_132C   ; flag clear: skip
    $12F7: BD EF 16    LDA $16EF,X
    $12FA: F0 30       BEQ $132C          ; → L_132C   ; v_fhi=0: skip
    $12FC: BD CA 16    LDA $16CA,X
    $12FF: F0 2B       BEQ $132C          ; → L_132C   ; v_dur=0: skip
    ; Determine note progress: orig_dur - 1 vs v_dur. If past mid-note
    ; (BCC), do the final-frame "kill gate" write; else DEC v_fhi and
    ; write the old value.
    $1301: BD CD 16    LDA $16CD,X
    $1304: 29 1F       AND #$1F
    $1306: 38          SEC
    $1307: E9 01       SBC #$01
    $1309: DD CA 16    CMP $16CA,X
    $130C: AC C3 16    LDY $16C3
    $130F: 90 10       BCC $1321          ; → L_1321
    $1311: BD EF 16    LDA $16EF,X
    $1314: DE EF 16    DEC $16EF,X
    $1317: 99 01 D4    STA $D401,Y        ; V1_FREQ_HI,Y
    $131A: BD D0 16    LDA $16D0,X
    $131D: 29 FE       AND #$FE           ; clear gate
    $131F: D0 08       BNE $1329          ; → L_1329
L_1321:
    $1321: BD EF 16    LDA $16EF,X
    $1324: 99 01 D4    STA $D401,Y        ; V1_FREQ_HI,Y
    $1327: A9 80       LDA #$80           ; test-bit silence
L_1329:
    $1329: 99 04 D4    STA $D404,Y        ; V1_CTRL,Y

L_132C:
    ; **SKYDIVE block** — fx_flags bit 1. Decrements v_fhi by 1 each
    ; even frame, but only when:
    ;   • orig_dur (v_flags & $1F) >= $0C  (at-least-12-tick note)
    ;   • current v_dur < $08              (last 8 ticks of the note)
    ;   • frame_counter bit 0 set          (every other frame)
    ;   • v_fhi != 0
    ; Audible as a falling pitch sweep on the tail of long-held notes.
    ; This is the per-instrument "skydive" the engine model encodes
    ; with `has_skydive`.
    $132C: AD F8 16    LDA $16F8
    $132F: 29 02       AND #$02
    $1331: F0 25       BEQ $1358          ; → L_1358   ; flag clear: skip
    $1333: BD CD 16    LDA $16CD,X
    $1336: 29 1F       AND #$1F
    $1338: C9 0C       CMP #$0C
    $133A: 90 1C       BCC $1358          ; → L_1358   ; orig dur < 12
    $133C: BD CA 16    LDA $16CA,X
    $133F: C9 08       CMP #$08
    $1341: B0 15       BCS $1358          ; → L_1358   ; v_dur >= 8
    $1343: AD FA 16    LDA $16FA
    $1346: 29 01       AND #$01
    $1348: F0 0E       BEQ $1358          ; → L_1358   ; even frame: skip
    $134A: BD EF 16    LDA $16EF,X
    $134D: F0 09       BEQ $1358          ; → L_1358   ; v_fhi=0: skip
    $134F: DE EF 16    DEC $16EF,X
    $1352: AC C3 16    LDY $16C3
    $1355: 99 01 D4    STA $D401,Y        ; V1_FREQ_HI,Y

L_1358:
    ; **OCTAVE ARPEGGIO** block — fx_flags bit 2. Every other frame
    ; (driven by frame_counter bit 0) the pitch is read as v_pitch+12,
    ; producing a fast +12-semitone alternation = octave trill.
    $1358: AD F8 16    LDA $16F8
    $135B: 29 04       AND #$04
    $135D: F0 2A       BEQ $1389          ; → L_1389   ; flag clear: skip
    $135F: AD FA 16    LDA $16FA
    $1362: 29 01       AND #$01
    $1364: F0 09       BEQ $136F          ; → L_136F   ; even frame: base
    $1366: BD D3 16    LDA $16D3,X
    $1369: 18          CLC
    $136A: 69 0C       ADC #$0C           ; +12 semitones
    $136C: 4C 72 13    JMP $1372          ; → L_1372
L_136F:
    $136F: BD D3 16    LDA $16D3,X        ; base pitch
L_1372:
    $1372: 0A          ASL A
    $1373: A8          TAY
    $1374: B9 00 16    LDA $1600,Y        ; freq_lo[pitch (+ optional 12)]
    $1377: 8D DB 16    STA $16DB
    $137A: B9 01 16    LDA $1601,Y        ; freq_hi[...]
    $137D: AC C3 16    LDY $16C3
    $1380: 99 01 D4    STA $D401,Y        ; V1_FREQ_HI,Y
    $1383: AD DB 16    LDA $16DB
    $1386: 99 00 D4    STA $D400,Y        ; V1_FREQ_LO,Y

L_1389:
    ; Per-voice loop tail. Recompute the sfx-mute gate $16FD for next
    ; frame: $FF (music enabled) if $16FB != 0 OR $16FC bit 7 set;
    ; $00 (music muted) otherwise. Y is loaded $FF, then INY (→ $00)
    ; if neither hold-music condition fires.
    $1389: A0 FF       LDY #$FF
    $138B: AD FB 16    LDA $16FB
    $138E: D0 06       BNE $1396          ; → L_1396   ; keep music
    $1390: AD FC 16    LDA $16FC
    $1393: 30 01       BMI $1396          ; → L_1396   ; keep music
    $1395: C8          INY                ; mute music
L_1396:
    $1396: 8C FD 16    STY $16FD
    $1399: CA          DEX
    $139A: 30 03       BMI $139F          ; → L_139F   ; all voices done
    $139C: 4C 5F 10    JMP $105F          ; → L_105F   ; next voice

L_139F:
    ; End-of-voice-loop / sfx tick. Reaching $139F from $104F (silenced
    ; first frame) we want $16FD=$FF so the sfx writes go through.
    $139F: A9 FF       LDA #$FF
    $13A1: 8D FD 16    STA $16FD
    ; Check if any sfx is active. If not, RTS. ($16FB is non-zero or
    ; $16FC bit 7 set when an sfx is currently running.)
    $13A4: AD FB 16    LDA $16FB
    $13A7: D0 05       BNE $13AE          ; → L_13AE   ; no sfx: RTS
    $13A9: 2C FC 16    BIT $16FC
    $13AC: 10 01       BPL $13AF          ; → L_13AF   ; sfx pending
L_13AE:
    $13AE: 60          RTS

L_13AF:
    ; Sfx is active. If $16FC has bit 6 set, this is the first frame of
    ; a freshly-armed sfx → run sfx_setup($16FC).
    $13AF: 50 03       BVC $13B4          ; → L_13B4
    $13B1: 20 06 17    JSR $1706          ; → sub_1706   ; sfx_setup
L_13B4:
    ; Branch on sfx kind. $16FC bit 5 set → kind C (special, → $1528).
    $13B4: AD FC 16    LDA $16FC
    $13B7: 29 20       AND #$20
    $13B9: F0 03       BEQ $13BE          ; → L_13BE
    $13BB: 4C 28 15    JMP $1528          ; → L_1528   ; BRK (unused?)
L_13BE:
    ; Otherwise: sfx idx (low 6 bits) selects which sfx voice/engine.
    ;   < $10  → tonal sfx (two-voice + control toggle, code below)
    ;   >= $10 → noise/drum sfx via $1438+
    $13BE: AD FC 16    LDA $16FC
    $13C1: 29 3F       AND #$3F
    $13C3: C9 10       CMP #$10
    $13C5: 90 03       BCC $13CA          ; → L_13CA
    $13C7: 4C 38 14    JMP $1438          ; → L_1438

L_13CA:
    ; Tonal sfx tick: $16FF is the per-step countdown; $1700 = step count;
    ; $1701 = freq offset (V2 follows V1 by $1701 semitones); $1702 sets
    ; per-voice toggle flags; $1703/$1704 toggle ctrl bit 0 each step
    ; (sync-style "blip").
    $13CA: CE FF 16    DEC $16FF
    $13CD: 10 DF       BPL $13AE          ; → L_13AE   ; mid-step: RTS
    $13CF: AD 05 17    LDA $1705
    $13D2: 29 0F       AND #$0F
    $13D4: 8D FF 16    STA $16FF          ; reload step duration
    $13D7: AD FE 16    LDA $16FE          ; current step idx
    $13DA: CD 00 17    CMP $1700
    $13DD: D0 0F       BNE $13EE          ; → L_13EE   ; mid-sequence
L_13DF:
    ; Sequence finished → silence sfx and mark done.
    $13DF: A2 00       LDX #$00
    $13E1: 8E 04 D4    STX $D404          ; V1_CTRL = 0
    $13E4: 8E 0B D4    STX $D40B          ; V2_CTRL = 0
    $13E7: CA          DEX                ; X = $FF
    $13E8: 8E FC 16    STX $16FC          ; $16FC = $FF (bit 7 set: done)
    $13EB: 4C AE 13    JMP $13AE          ; → L_13AE

L_13EE:
    ; Mid-sequence: emit one tonal step. $1705 bit 7 / bit 6 control
    ; which voices participate; $1701 is the V2 transpose offset.
    $13EE: CE FE 16    DEC $16FE
    $13F1: 0A          ASL A
    $13F2: A8          TAY
    $13F3: 2C 05 17    BIT $1705
    $13F6: 30 20       BMI $1418          ; → L_1418
    $13F8: 70 0C       BVS $1406          ; → L_1406
    $13FA: B9 00 16    LDA $1600,Y        ; freq_lo[step]
    $13FD: 8D 00 D4    STA $D400          ; V1_FREQ_LO (direct, no ,Y)
    $1400: B9 01 16    LDA $1601,Y
    $1403: 8D 01 D4    STA $D401          ; V1_FREQ_HI
L_1406:
    ; V2 = V1's freq minus $1701 (transpose).
    $1406: 98          TYA
    $1407: 38          SEC
    $1408: ED 01 17    SBC $1701
    $140B: A8          TAY
    $140C: B9 00 16    LDA $1600,Y
    $140F: 8D 07 D4    STA $D407          ; V2_FREQ_LO
    $1412: B9 01 16    LDA $1601,Y
    $1415: 8D 08 D4    STA $D408          ; V2_FREQ_HI
L_1418:
    ; Ctrl-bit-0 toggle each step (sync/test blip effect) — $1702 bit 7
    ; gates V1's toggle, bit 6 gates V2's.
    $1418: 2C 02 17    BIT $1702
    $141B: 10 0B       BPL $1428          ; → L_1428
    $141D: AD 03 17    LDA $1703
    $1420: 49 01       EOR #$01
    $1422: 8D 04 D4    STA $D404          ; V1_CTRL
    $1425: 8D 03 17    STA $1703
L_1428:
    $1428: 50 0B       BVC $1435          ; → L_1435
    $142A: AD 04 17    LDA $1704
    $142D: 49 01       EOR #$01
    $142F: 8D 0B D4    STA $D40B          ; V2_CTRL
    $1432: 8D 04 17    STA $1704
L_1435:
    $1435: 4C AE 13    JMP $13AE          ; → L_13AE

; ============================================================================
; SFX engine kind B ($16FC low 6 bits >= $10): noise/drum-type sfx.
; Reads an 8-entry per-voice control table at $15BC/$15C3, an 8-step
; per-voice freq slide table, and ticks pulse_lo via sub_149E/sub_14B8.
; Less audibly important than kind A (tonal) but mechanically similar.
; ============================================================================

L_1438:
    $1438: AE 27 15    LDX $1527          ; sfx step index
    $143B: AD 22 15    LDA $1522
    $143E: CD 1A 15    CMP $151A
    $1441: B0 11       BCS $1454          ; → L_1454
    $1443: BD BC 15    LDA $15BC,X
    $1446: 8D 04 D4    STA $D404          ; V1_CTRL (gate from table)
    $1449: BD C3 15    LDA $15C3,X
    $144C: 29 FE       AND #$FE
    $144E: 8D 0B D4    STA $D40B          ; V2_CTRL (gate-off)
    $1451: 4C 62 14    JMP $1462          ; → L_1462
L_1454:
    $1454: BD C3 15    LDA $15C3,X
    $1457: 8D 0B D4    STA $D40B          ; V2_CTRL (gate from table)
    $145A: BD BC 15    LDA $15BC,X
    $145D: 29 FE       AND #$FE
    $145F: 8D 04 D4    STA $D404          ; V1_CTRL (gate-off)
L_1462:
    ; Tick V1 freq slide.
    $1462: A2 00       LDX #$00
    $1464: A0 00       LDY #$00
    $1466: 2C 21 15    BIT $1521
    $1469: 10 06       BPL $1471          ; → L_1471   ; ADD direction
    $146B: 20 B8 14    JSR $14B8          ; → sub_14B8 ; SUB
    $146E: 4C 74 14    JMP $1474          ; → L_1474
L_1471:
    $1471: 20 9E 14    JSR $149E          ; → sub_149E ; ADD
L_1474:
    ; Tick V2 freq slide.
    $1474: A2 02       LDX #$02
    $1476: A0 07       LDY #$07
    $1478: 2C 21 15    BIT $1521
    $147B: 50 06       BVC $1483          ; → L_1483
    $147D: 20 B8 14    JSR $14B8          ; → sub_14B8
    $1480: 4C 86 14    JMP $1486          ; → L_1486
L_1483:
    $1483: 20 9E 14    JSR $149E          ; → sub_149E
L_1486:
    ; Step-counter decrement. $1522 = current-step counter (BMI loads next
    ; step). $151B = step duration reload. $151C = remaining steps in sfx.
    $1486: CE 22 15    DEC $1522
    $1489: 30 01       BMI $148C          ; → L_148C
    $148B: 60          RTS
L_148C:
    $148C: AD 1B 15    LDA $151B
    $148F: 8D 22 15    STA $1522
    $1492: 20 FE 14    JSR $14FE          ; → sub_14FE
    $1495: CE 1C 15    DEC $151C          ; remaining steps
    $1498: 30 01       BMI $149B          ; → L_149B
    $149A: 60          RTS
L_149B:
    $149B: 4C DF 13    JMP $13DF          ; → L_13DF   ; sfx done: silence

; sub_149E: V freq += slide step (16-bit). X/Y are caller-supplied
; indexing offsets so the same routine drives both V1 and V2.
sub_149E:
    $149E: 18          CLC
    $149F: BD 23 15    LDA $1523,X
    $14A2: 7D 1D 15    ADC $151D,X
    $14A5: 9D 23 15    STA $1523,X
    $14A8: 99 00 D4    STA $D400,Y        ; V_FREQ_LO,Y
    $14AB: BD 24 15    LDA $1524,X
    $14AE: 7D 1E 15    ADC $151E,X
    $14B1: 9D 24 15    STA $1524,X
    $14B4: 99 01 D4    STA $D401,Y        ; V_FREQ_HI,Y
    $14B7: 60          RTS

; sub_14B8: mirror of sub_149E, subtracting instead.
sub_14B8:
    $14B8: 38          SEC
    $14B9: BD 23 15    LDA $1523,X
    $14BC: FD 1D 15    SBC $151D,X
    $14BF: 9D 23 15    STA $1523,X
    $14C2: 99 00 D4    STA $D400,Y        ; V_FREQ_LO,Y
    $14C5: BD 24 15    LDA $1524,X
    $14C8: FD 1E 15    SBC $151E,X
    $14CB: 9D 24 15    STA $1524,X
    $14CE: 99 01 D4    STA $D401,Y        ; V_FREQ_HI,Y
    $14D1: 60          RTS

; L_14D2 (fall-through helper from sub_1706's kind-B branch): copies the
; sfx data record into $151A..$1521 (8 control bytes) and $D400..$D40D
; (14 voice-register init bytes).
L_14D2:
    $14D2: 0A          ASL A              ; sfx_idx * 2
    $14D3: 0A          ASL A              ; * 4
    $14D4: 0A          ASL A              ; * 8
    $14D5: 48          PHA
    $14D6: 0A          ASL A              ; * 16
    $14D7: 8D 27 15    STA $1527          ; remember (sfx_idx * 16)
    $14DA: 68          PLA                ; (sfx_idx * 8)
    $14DB: AA          TAX
    $14DC: A0 00       LDY #$00
    $14DE: 8C 22 15    STY $1522
L_14E1:
    ; Copy 8 control bytes from $15E8+sfx_idx*8 to $151A+.
    $14E1: BD E8 15    LDA $15E8,X
    $14E4: 99 1A 15    STA $151A,Y
    $14E7: E8          INX
    $14E8: C8          INY
    $14E9: C0 08       CPY #$08
    $14EB: D0 F4       BNE $14E1          ; → L_14E1
    ; Copy 14 SID voice init bytes from $15B8+sfx_idx*16.
    $14ED: AE 27 15    LDX $1527
    $14F0: A0 00       LDY #$00
L_14F2:
    $14F2: BD B8 15    LDA $15B8,X
    $14F5: 99 00 D4    STA $D400,Y        ; V_FREQ_LO,Y
    $14F8: E8          INX
    $14F9: C8          INY
    $14FA: C0 0E       CPY #$0E
    $14FC: D0 F4       BNE $14F2          ; → L_14F2
    ; (fall through)

; sub_14FE: refresh internal "current frequency" snapshots ($1523/$1524
; for V1, $1525/$1526 for V2) from the freshly-copied SID init bytes.
sub_14FE:
    $14FE: AE 27 15    LDX $1527
    $1501: BD B8 15    LDA $15B8,X
    $1504: 8D 23 15    STA $1523
    $1507: BD B9 15    LDA $15B9,X
    $150A: 8D 24 15    STA $1524
    $150D: BD BF 15    LDA $15BF,X
    $1510: 8D 25 15    STA $1525
    $1513: BD C0 15    LDA $15C0,X
    $1516: 8D 26 15    STA $1526
    $1519: 60          RTS
; ----- data gap $151A-$1527 (14 bytes; the sfx control + freq scratch) -----

L_1528:
    ; BRK reached only via $13BB JMP $1528 when sfx kind C is requested.
    ; In practice no shipped sfx uses kind C, so this is dead code (any
    ; sfx armed with bit 5 of $16FC set would crash sidplayfp).
    $1528: 00          BRK
; ----- data gap $1529-$152F (7 bytes) -----

; ======= init: =======
; Entry: A = subtune index (0-indexed). PSID startSong=1 → A=0 here.
init:
    $1530: 8D 55 15    STA $1555           ; save subtune
    $1533: 20 03 10    JSR $1003           ; → sub_1003 ; silence music
    $1536: 20 06 10    JSR $1006           ; → sub_1006 ; clear sfx state
    $1539: EA          NOP
    $153A: EA          NOP
    $153B: EA          NOP
    $153C: AD 55 15    LDA $1555           ; A = subtune
    $153F: C9 07       CMP #$07
    $1541: 10 07       BPL $154A           ; → L_154A   ; A >= 7: sfx
    ; Music subtune (0..6).
    $1543: 8D 56 15    STA $1556           ; save adjusted subtune
    $1546: 4C 00 10    JMP $1000           ; → L_1000   ; → JMP $198A
; ----- data gap $1549-$1549 (1 byte) -----

L_154A:
    ; Sfx subtune (7..25). Re-normalise to (subtune - 7) ∈ [0..18].
    $154A: E9 07       SBC #$07
    $154C: 8D 56 15    STA $1556
    $154F: 4C 0F 10    JMP $100F           ; → L_100F   ; → JMP $19CC

; ----- data gap $1552-$1705 (436 bytes; orderlists, freq table, instrument
;       table, pattern data, pattern ptrs) -----

; sub_1706: SFX setup — arm a new sfx tune. $16FC's low 6 bits are the
; sfx_idx (0..18). Different sfx idx ranges use different setup paths:
;   $00..$0F → tonal sfx (kind A), loads control bytes from $1884+sfx*16
;   $10..$3F → drum/noise sfx (kind B), routes through $14D2
sub_1706:
    $1706: A9 00       LDA #$00
    $1708: 8D 04 D4    STA $D404           ; V1_CTRL = 0
    $170B: 8D 0B D4    STA $D40B           ; V2_CTRL = 0
    $170E: 8D FF 16    STA $16FF           ; clear sfx step countdown
    ; bit 5 of $16FC = kind C (the unused/BRK path).
    $1711: AD FC 16    LDA $16FC
    $1714: 29 20       AND #$20
    $1716: F0 06       BEQ $171E           ; → L_171E
    $1718: 8D FC 16    STA $16FC
    $171B: 4C 77 15    JMP $1577           ; (untraced data region; would
                                           ;  set up kind C — never reached
                                           ;  by shipped sfx)
L_171E:
    ; Strip bit 6 (first-frame marker) from $16FC. Compare bits 0..3.
    ;   >= $10 → kind B (noise/drum)
    ;   <  $10 → kind A (tonal)
    $171E: AD FC 16    LDA $16FC
    $1721: 29 3F       AND #$3F
    $1723: C9 10       CMP #$10
    $1725: 90 08       BCC $172F           ; → L_172F   ; kind A
    $1727: 8D FC 16    STA $16FC
    $172A: E9 10       SBC #$10            ; sfx_idx -= $10
    $172C: 4C D2 14    JMP $14D2           ; → L_14D2   ; kind B setup
L_172F:
    ; Kind A: tonal sfx. Read 16-byte record at $1884+sfx_idx*16.
    ;   +0 $1705: step-duration / mode bits
    ;   +1 $16FE: starting step idx
    ;   +5..$0E (loop): copy 14 bytes into V1/V2 init regs at $D400+
    ;   +8 $1702: per-voice toggle flags
    ;   +9 $1703: V1 ctrl-toggle init
    ;   +12 $1700: end step idx
    ;   +15 $1701: V2 transpose offset
    ;   +16 $1704: V2 ctrl-toggle init
    $172F: AD FC 16    LDA $16FC
    $1732: 29 0F       AND #$0F
    $1734: 8D FC 16    STA $16FC
    $1737: 0A          ASL A
    $1738: 0A          ASL A
    $1739: 0A          ASL A
    $173A: 0A          ASL A               ; sfx_idx * 16
    $173B: A8          TAY
    $173C: B9 84 18    LDA $1884,Y
    $173F: 8D 05 17    STA $1705
    $1742: B9 85 18    LDA $1885,Y
    $1745: 8D FE 16    STA $16FE
    $1748: B9 93 18    LDA $1893,Y
    $174B: 8D 00 17    STA $1700
    $174E: B9 8C 18    LDA $188C,Y
    $1751: 8D 02 17    STA $1702
    $1754: 29 3F       AND #$3F            ; (also into $1701 = transpose)
    $1756: 8D 01 17    STA $1701
    $1759: B9 89 18    LDA $1889,Y
    $175C: 8D 03 17    STA $1703
    $175F: B9 90 18    LDA $1890,Y
    $1762: 8D 04 17    STA $1704
    $1765: A2 00       LDX #$00
L_1767:
    $1767: B9 85 18    LDA $1885,Y         ; copy 14 voice init bytes
    $176A: 9D 00 D4    STA $D400,X         ; V1_FREQ_LO,X
    $176D: C8          INY
    $176E: E8          INX
    $176F: E0 0E       CPX #$0E
    $1771: D0 F4       BNE $1767           ; → L_1767
    ; Choose between $13EE (default freq-write path) and $13CE-style
    ; alternative based on $1705's high two bits ($20 → $13EE, else $13CE).
    $1773: AD 05 17    LDA $1705
    $1776: 29 30       AND #$30
    $1778: A0 EE       LDY #$EE
    $177A: C9 20       CMP #$20
    $177C: F0 02       BEQ $1780           ; → L_1780
    $177E: A0 CE       LDY #$CE
L_1780:
    $1780: 8C EE 13    STY $13EE           ; patch the lobyte of branch
                                          ;  target inside $13DE (self-mod)
    $1783: 60          RTS

; ----- data gap $1784-$1989 (518 bytes; instrument table at $1784, then
;       16-byte sfx records at $1884-$1983) -----

; sub_198A: music subtune setup. A still holds subtune idx (0..6).
L_198A:
    $198A: A0 00       LDY #$00
    $198C: 0A          ASL A               ; subtune * 2
    $198D: 8D DC 16    STA $16DC
    $1990: 0A          ASL A               ; subtune * 4
    $1991: 18          CLC
    $1992: 6D DC 16    ADC $16DC           ; + (subtune * 2) = subtune * 6
    $1995: AA          TAX                 ; X = subtune * 6
L_1996:
    ; Copy 6 bytes of per-voice orderlist pointers from $1A28+ into
    ; the active set at $1984..$1989 (3 lo + 3 hi).
    $1996: BD 28 1A    LDA $1A28,X
    $1999: 99 84 19    STA $1984,Y
    $199C: E8          INX
    $199D: C8          INY
    $199E: C0 06       CPY #$06
    $19A0: D0 F4       BNE $1996           ; → L_1996
    ; Silence voices and mark "first frame" (bit 6 of $16EE).
    $19A2: A9 00       LDA #$00
    $19A4: 8D 04 D4    STA $D404           ; V1_CTRL = 0
    $19A7: 8D 0B D4    STA $D40B           ; V2_CTRL = 0
    $19AA: 8D 12 D4    STA $D412           ; V3_CTRL = 0
    $19AD: A9 0F       LDA #$0F
    $19AF: 8D 18 D4    STA $D418           ; VOL = $0F
    $19B2: A9 40       LDA #$40
    $19B4: 8D EE 16    STA $16EE           ; $16EE = $40 (only bit 6 set:
                                          ;  first-frame request, music
                                          ;  not silenced)
    $19B7: 60          RTS

; sub_19B8 (entered via JMP from $1003 = sub_1003): set $16EE bit 7 + bit 6.
L_19B8:
    $19B8: A9 C0       LDA #$C0
    $19BA: 8D EE 16    STA $16EE           ; bit 7 = silenced, bit 6 = first
    $19BD: 60          RTS

; sub_19BE (entered via JMP from $1006 = sub_1006): clear sfx-running flag.
L_19BE:
    $19BE: A9 00       LDA #$00
    $19C0: 8D FB 16    STA $16FB
    $19C3: 60          RTS
; ----- data gap $19C4-$19CB (8 bytes) -----

; sub_19CC (entered via JMP from $100F): sfx subtune dispatch. A still
; holds the normalised sfx_idx (0..18, after init's SBC #$07).
;   - If a sfx is already running ($16FB != 0), latch the new request
;     into $16FC and let the engine finish the current one first.
;   - Else: store sfx_idx | $40 into $16FC (bit 6 = "first frame
;     setup pending"), restore VOL.
L_19CC:
    $19CC: AE FB 16    LDX $16FB
    $19CF: F0 04       BEQ $19D5           ; → L_19D5
    $19D1: 8E FC 16    STX $16FC
    $19D4: 60          RTS
L_19D5:
    $19D5: 09 40       ORA #$40
    $19D7: 8D FC 16    STA $16FC           ; sfx armed: bit 6 + sfx_idx
    $19DA: A9 0F       LDA #$0F
    $19DC: 8D 18 D4    STA $D418           ; VOL = $0F
    $19DF: 60          RTS
; ----- data gap $19E0-$2E8C (5293 bytes; subtune orderlist pointer table at
;       $1A28+, pattern-ptr tables pat_lo=$1A52 / pat_hi=$1AC1, orderlists,
;       patterns, freq table extension) -----
