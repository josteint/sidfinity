; =============================================================================
; Rob Hubbard - Commando (1985 Elite)
; COMPLETE PLAY ROUTINE DISASSEMBLY: $5012 - $5427
; =============================================================================
;
; Binary: data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid
; Load:   $5000   Init: $5FB2   Play: $5012
; Songs:  19      Start: 1
; Binary: $5000-$5FC6 (4039 bytes)
;
; MEMORY MAP (STATE VARIABLES):
; ==============================
;
; Per-voice arrays (3 entries, index X=0,1,2 = V1,V2,V3):
;   $54E8,X  = voice SID base offset: 0, 7, 14 (-> $D400, $D407, $D40E)
;              (indexed from song init: X=0->$00, X=1->$07, X=2->$0E)
;   $54EC,X  = sequence index (which slot in the song sequence list for this voice)
;   $54EF,X  = note index within current pattern (byte offset from pattern start)
;   $54F2,X  = duration countdown (frames remaining for current note, decremented each tick)
;   $54F5,X  = raw note byte 0 (flags: bit7=new_instr, bit6=tie, bit5=no_release, bits4-0=dur)
;   $54F8,X  = instrument ctrl byte (ctrl field from instrument table, for gate control)
;   $54FB,X  = pitch index (note number, 0-95, used to index freq table at $5428)
;   $54FE,X  = instrument number (0-15, index into $5591 instrument table)
;   $5520,X  = drum trigger value (0 = no drum, bit7 set = drum indicator, low bits = drum id)
;   $551A,X  = freq_hi current value (freq high byte, used for skydive/arpeggio)
;   $551D,X  = freq_lo current value (freq low byte, used for skydive/portamento)
;   $550D,X  = PW oscillation period counter (for bidirectional PW sweep)
;   $5510,X  = PW oscillation direction flag (0=rising, 1=falling)
;
; Global state:
;   $5513    = speed counter (counts down from resetspd, reload when < 0)
;   $5517    = resetspd = speed reset value (tempo: tick every resetspd+1 frames)
;   $5518    = instrument table offset (Y * 8 where Y = instr_num * 8)
;   $5519    = state machine byte:
;                $00 = normal play mode
;                $40 = first frame after init (reset state)
;                $80 = end-of-song handling
;   $551B    = (part of 551A array for voice 2)
;   $551C    = (part of 551A array for voice 3)
;   $5523    = fx_flags for current voice (from instrument table byte 7):
;                bit 0 = DRUM effect (drum freq slide on V1)
;                bit 1 = SKYDIVE (freq slide each tick: dec freq_hi by 1)
;                bit 2 = ARPEGGIO (alternates note_offset=0 / note_offset=+12 each frame)
;                bit 3 = PW_UNI (unidirectional PW: bit3=1 simple add, bit3=0 oscillating)
;   $5524    = temp: PW delta for current step
;   $5525    = global frame counter (incremented every play call, wraps 0-255)
;   $5526    = drum voice inhibit flag (0=ok, nonzero=voice is playing, skip drum engine)
;   $5527    = drum state / end-of-song flag:
;                $FF = drum channel ready (set by song init, JSR $5531 triggered when bit6=1)
;                $00-$0F = drum sequence index (after first JSR $5531)
;                negative (bit7=1) = end-of-song reached
;   $5528    = drum output enable flag:
;                $FF = drum output DISABLED (no V1/V2 freq writes from drum engine)
;                $00 = drum output ENABLED (allows V1/V2 freq writes)
;   $5529    = drum note counter (counts notes played in drum pattern)
;   $552A    = drum sub-tick counter (counts ticks within each drum step)
;   $552B    = drum pattern length (number of notes, limit value)
;   $552C    = drum voice 2 freq offset (subtracted from V1's freq index for V2)
;   $552D    = drum control flags:
;                bit 7 = enable V1 gate toggle
;                bit 6 = enable V2 gate toggle
;   $552E    = V1 gate state for drum (0=low, 1=high, toggled each drum step)
;   $552F    = V2 gate state for drum (0=low, 1=high, toggled each drum step)
;   $5530    = drum table flags byte:
;                bits 7-6 = V1/V2 freq enable (10=V1 only, 01=V2 only, 11=both, 00=neither)
;                bits 5-4 = drum direction (bit5 set = INC/up mode, else DEC/down mode)
;                bits 3-0 = sub-tick period (low nibble of $552A reload)
;   $5D,$5E  = ZP 16-bit pointer to song sequence data for current voice
;   $5F,$60  = ZP 16-bit pointer to pattern data for current voice
;   $5501    = gate enable flag ($FF=gate on, decremented to 0=gate off on BVS path)
;   $5502    = temp: current note byte copy
;   $5503    = temp: freq_lo byte
;   $5504    = temp: saved X register (voice index)
;   $5505    = temp: instrument ctrl byte
;   $5506    = vibrato depth (from instr table byte 5)
;   $5507    = PW speed (from instr table byte 6)
;   $5508    = vibrato delta lo
;   $5509    = vibrato delta hi
;   $550A    = vibrato target freq lo
;   $550B    = vibrato target freq hi
;   $550C    = vibrato step counter (0 to 3 based on frame counter bits 0-2)
;
; Data tables:
;   $5428    = freq table: interleaved lo/hi pairs, 96 entries
;              freq_lo[n] = $5428 + n*2,  freq_hi[n] = $5429 + n*2
;   $5591    = instrument table: 8 bytes each, 16 instruments
;              bytes: pw_lo, pw_hi, ctrl, ad, sr, vib_depth, pwm_speed, fx_flags
;   $5711    = pattern pointer lo table (32 entries)
;   $573E    = pattern pointer hi table (32 entries)
;   $576B    = song 0 voice 0 sequence (list of pattern indices, FF=loop, FE=end)
;   $57AC    = song 0 voice 1 sequence
;   $57EC    = song 0 voice 2 sequence
;   $56F9    = song track lo pointer table (3 per song)
;   $56FC    = song track hi pointer table (3 per song)
;   $55F9    = drum table: 16 entries * 16 bytes each = 256 bytes
;
; Pattern byte format:
;   Byte 0:  bit7=has_new_instrument  bit6=tie(no_retrigger)  bit5=no_release
;            bits4-0 = duration (1-31 frames per tick; total = dur * (speed+1) frames)
;   Byte 1:  (only if bit7 of byte 0 set)
;            bit7=drum_trigger  bits6-0=instrument_number (or drum channel id)
;   Byte 2:  pitch index (0-95, indexes into freq table at $5428)
;
; Drum table entry (16 bytes at $55F9 + drum_idx*16):
;   +$00  drum_flags    (bits: 7=V1_freq, 6=V2_freq, 5=INC_dir, 4=?(dir), 3-0=sub_period)
;   +$01  drum_counter  (starting note count, decremented or incremented per step)
;   +$02..+$0D  14 bytes written directly to $D400-$D40D at drum init
;   +$08  drum_gate1_init (V1 gate initial state, $55FE relative = table+5)
;   +$0F  drum_limit    (endpoint for drum counter, at $5608+Y)
;   (offsets relative to $55F9+Y, where Y = drum_idx * 16)
;
; =============================================================================
; SONG INIT ROUTINE ($5FB2 = init_addr)
; =============================================================================

$5FB2   C9 03         CMP #$03            ; is song number >= 3?
$5FB4   B0 09         BCS $5FBF           ; yes: branch to $5FBF (higher-song init)
$5FB6   20 0C 50      JSR $500C           ; common song init (-> JMP $53CF -> RTS)
$5FB9   8E 28 55      STX $5528           ; $5528 = 0 (enable drum output, X=0 from init)
$5FBC   4C 00 50      JMP $5000           ; jump to song jump table

$5FBF   E9 03         SBC #$03            ; subtract 3 from song number (carry clear from CMP>=3)
$5FC1   20 0F 50      JSR $500F           ; alternate song init (calls via jump table)
$5FC4   4C 03 50      JMP $5003           ; jump to song jump table + 3

; $5000 Jump table (per-song pointers):
;   $5000: 4C 0C 5F = JMP $5F0C    ; ?? (or init song 0 setup)
;   $5003: 4C 42 5F = JMP $5F42
;   $5006: 4C 48 5F = JMP $5F48
;   $5009: 4C 4E 5F = JMP $5F4E
;   $500C: 4C CF 53 = JMP $53CF    ; common song init
;   $500F: 4C 56 5F = JMP $5F56    ; alternate

; =============================================================================
; SONG INIT COMMON ($53CF, called via $500C -> JMP)
; =============================================================================

$53CF   A2 00         LDX #$00            ; X = 0
$53D1   8E 04 D4      STX $D404           ; V1 ctrl = 0 (gate off, waveform off)
$53D4   8E 0B D4      STX $D40B           ; V2 ctrl = 0
$53D7   CA            DEX                 ; X = $FF
$53D8   8E 27 55      STX $5527           ; $5527 = $FF (drum channel: "first play" flag)
$53DB   4C B4 53      JMP $53B4           ; -> RTS (return to caller)

; =============================================================================
; PLAY ROUTINE ($5012 = play_addr)
; =============================================================================
;
; OVERVIEW: Called once per video frame (50Hz PAL). Processes three voices in
; reverse order (V3=X2, V2=X1, V1=X0), then runs drum engine.
;
; FLOW PER VOICE:
;   1. Speed counter tick (determines if this frame is a "tick")
;   2. If tick: decrement duration, check if note expired
;   3. If note expired: read next pattern event (new note, instrument, pitch)
;   4. Apply effects: vibrato, PW modulation, skydive, arpeggio, drum slide
;   5. Write results to SID registers
;   6. After all voices: update drum output enable flag
;   7. Run drum engine (pattern step sequencer for V1/V2)
;
; =============================================================================
; ENTRY POINT: Frame counter + state machine gate
; =============================================================================

$5012   EE 25 55      INC $5525           ; increment global frame counter (wraps 0-255)

; State machine: $5519 controls what happens this frame
;   $5019: $40 = "first frame after init" (reset all voice state, then play)
;   $5019: $80 = "end-of-song" (go to drum engine only)
;   $5019: $00 = "normal play" (check further for note advance)

$5015   2C 19 55      BIT $5519           ; test $5519: N=bit7, V=bit6
$5018   30 1E         BMI $5038           ; N=1 ($5519 bit7 set = end/reset): branch to $5038
$501A   50 36         BVC $5052           ; V=0 ($5519 bit6 clear = normal play): skip to $5052
                                          ; V=1 ($5519=$40, bit6=1 = first frame): fall through

; --- FIRST FRAME AFTER INIT: Reset all voice state ---
; $5519 = $40 -> reset voices, clear $5519, go play
$501C   A9 00         LDA #$00            ; A = 0
$501E   8D 25 55      STA $5525           ; reset frame counter to 0
$5021   A2 02         LDX #$02            ; X = 2 (start with voice 3)
$5023   9D EC 54      STA $54EC,X         ; voice X sequence index = 0
$5026   9D EF 54      STA $54EF,X         ; voice X note index = 0
$5029   9D F2 54      STA $54F2,X         ; voice X duration = 0 (force immediate note read)
$502C   9D FB 54      STA $54FB,X         ; voice X pitch = 0
$502F   CA            DEX                 ; X--
$5030   10 F1         BPL $5023           ; loop X=2,1,0 (all 3 voices)
$5032   8D 19 55      STA $5519           ; $5519 = 0 (normal play mode)
$5035   4C 52 50      JMP $5052           ; go to main voice loop

; --- END-OF-SONG or RESET STATE ($5019 bit7=1) ---
$5038   50 15         BVC $504F           ; V=0 ($5519=$80 = end-of-song only): skip to $504F
                                          ; V=1 ($5519=$C0 = both?): fall through
; $5519 = $C0: mute all voices, set $5519=$80 (end-of-song idle)
$503A   A9 00         LDA #$00
$503C   8D 04 D4      STA $D404           ; V1 ctrl = 0 (silence voice 1)
$503F   8D 0B D4      STA $D40B           ; V2 ctrl = 0 (silence voice 2)
$5042   8D 12 D4      STA $D412           ; V3 ctrl = 0 (silence voice 3)
$5045   A9 0F         LDA #$0F
$5047   8D 18 D4      STA $D418           ; SID volume = $0F (max, filter off)
$504A   A9 80         LDA #$80
$504C   8D 19 55      STA $5519           ; $5519 = $80 (end-of-song idle mode)
$504F   4C A5 53      JMP $53A5           ; skip voice processing, go to drum engine

; =============================================================================
; MAIN VOICE LOOP: process voices X=2, X=1, X=0
; =============================================================================
; Called at $5052 after state setup, and loops back via $53A2 after each voice.

$5052   A2 02         LDX #$02            ; start with voice 3 (X=2)

; --- SPEED COUNTER TICK LOGIC ---
; The speed counter determines tempo. It counts down from resetspd.
; When it underflows (goes below 0), reload from $5517.
; A "tick" happens every (resetspd+1) frames.

$5054   CE 13 55      DEC $5513           ; decrement speed counter
$5057   10 06         BPL $505F           ; if still >= 0: not a tick, skip reload
                                          ; TAKEN: speed counter still positive, proceed
$5059   AD 17 55      LDA $5517           ; load resetspd (= speed - 1)
$505C   8D 13 55      STA $5513           ; reload speed counter
; Falls through to $505F

; --- VOICE SELECTION: load current voice's SID offset and sequence ptr ---
$505F   BD E8 54      LDA $54E8,X         ; load voice SID base offset (0, 7, or 14)
$5062   8D EB 54      STA $54EB           ; save as temp "current SID voice offset"
$5065   A8            TAY                 ; Y = SID offset (for indexed SID writes $D400+Y)
$5066   AD 13 55      LDA $5513           ; load current speed counter value
$5069   CD 17 55      CMP $5517           ; compare with resetspd
$506C   D0 15         BNE $5083           ; if not equal: NOT a tick frame, skip note advance
                                          ; NOTE: counter equals resetspd only when just reloaded
                                          ; (== just decremented through zero and reloaded)

; --- TICK FRAME: check if note duration expired ---
; On a tick frame (speed counter just reloaded), advance note for this voice.
$506E   BD F9 56      LDA $56F9,X         ; load song track ptr lo (3 entries, one per voice)
$5071   85 5D         STA $5D             ; $5D = lo byte of sequence pointer
$5073   BD FC 56      LDA $56FC,X         ; load song track ptr hi
$5076   85 5E         STA $5E             ; $5E = hi byte of sequence pointer
                                          ; ($5D/$5E) = pointer to voice's song sequence data

$5078   DE F2 54      DEC $54F2,X         ; decrement duration counter for this voice
$507B   30 09         BMI $5086           ; if < 0: duration expired, read next note
$507D   4C 74 51      JMP $5174           ; duration still active: go to SUSTAIN path
$5080   4C 8F 53      JMP $538F           ; (unreachable here, padding)

$5083   4C 9B 51      JMP $519B           ; NOT a tick: apply effects only (no note advance)

; --- DURATION EXPIRED: read next pattern event ---
; Load sequence entry to get pattern pointer, then read note bytes from pattern.

$5086   BC EC 54      LDY $54EC,X         ; Y = sequence index for this voice
$5089   B1 5D         LDA ($5D),Y         ; read sequence[seq_index] = pattern number
$508B   C9 FF         CMP #$FF            ; is it $FF (end of sequence)?
$508D   F0 0A         BEQ $5099           ; yes: wrap sequence
$508F   C9 FE         CMP #$FE            ; is it $FE (end of song)?
$5091   D0 17         BNE $50AA           ; no: it's a valid pattern number, process it

; --- END OF SONG ($FE) ---
$5093   20 03 50      JSR $5003           ; call song cleanup routine (-> song-specific code)
$5096   4C A5 53      JMP $53A5           ; go to drum engine (done with voices)

; --- WRAP SEQUENCE ($FF): reset seq index, re-read from start ---
$5099   A9 00         LDA #$00
$509B   9D F2 54      STA $54F2,X         ; reset duration to 0 (force re-read)
$509E   9D EC 54      STA $54EC,X         ; reset sequence index to 0
$50A1   9D EF 54      STA $54EF,X         ; reset note index to 0
$50A4   4C 86 50      JMP $5086           ; re-read from sequence[0]
$50A7   4C 8F 53      JMP $538F           ; (padding)

; --- VALID PATTERN: load pattern pointer ---
; A = pattern number from sequence
$50AA   A8            TAY                 ; Y = pattern number
$50AB   B9 11 57      LDA $5711,Y         ; load pattern pointer lo (from table at $5711)
$50AE   85 5F         STA $5F             ; $5F = pattern ptr lo
$50B0   B9 3E 57      LDA $573E,Y         ; load pattern pointer hi (from table at $573E)
$50B3   85 60         STA $60             ; $60 = pattern ptr hi
                                          ; ($5F/$60) = pointer to this pattern's data

; Reset drum trigger for this voice
$50B5   A9 00         LDA #$00
$50B7   9D 20 55      STA $5520,X         ; clear drum trigger ($5520,X = 0 = no drum)

; Load note index
$50BA   BC EF 54      LDY $54EF,X         ; Y = note index within pattern

; --- READ NOTE BYTE 0 (flags + duration) ---
; Preserve gate-on for tied notes
$50BD   A9 FF         LDA #$FF
$50BF   8D 01 55      STA $5501           ; $5501 = $FF (gate enable: will be ANDed with ctrl)
$50C2   B1 5F         LDA ($5F),Y         ; read note byte 0: flags + duration
$50C4   9D F5 54      STA $54F5,X         ; store raw note byte 0
$50C7   8D 02 55      STA $5502           ; save copy
$50CA   29 1F         AND #$1F            ; extract duration (bits 4-0)
$50CC   9D F2 54      STA $54F2,X         ; store as duration countdown

; Test tie flag (bit 6 of note byte 0)
$50CF   2C 02 55      BIT $5502           ; test bit 6 (V flag) of note byte 0
$50D2   70 44         BVS $5118           ; bit6=1 = TIE: skip retrigger, go to $5118

; --- NOT TIED: advance note index, check for instrument change ---
$50D4   FE EF 54      INC $54EF,X         ; advance note index (consumed byte 0)
$50D7   AD 02 55      LDA $5502           ; reload note byte 0
$50DA   10 11         BPL $50ED           ; bit7=0: no instrument change, skip to byte 2

; --- INSTRUMENT CHANGE: read byte 1 ---
; Bit 7 of note byte 0 is set -> next byte is instrument/drum
$50DC   C8            INY                 ; Y++ (point to byte 1)
$50DD   B1 5F         LDA ($5F),Y         ; read byte 1: instrument/drum number
$50DF   10 06         BPL $50E7           ; bit7=0: normal instrument
; Bit 7 set = drum trigger
$50E1   9D 20 55      STA $5520,X         ; store drum value ($5520,X = drum trigger)
$50E4   4C EA 50      JMP $50EA           ; skip instrument store
; Normal instrument
$50E7   9D FE 54      STA $54FE,X         ; store instrument number ($54FE,X)
$50EA   FE EF 54      INC $54EF,X         ; advance note index (consumed byte 1)

; --- READ BYTE 2: PITCH ---
; Both tied and untied paths converge here
$50ED   C8            INY                 ; Y++ (point to pitch byte)
$50EE   B1 5F         LDA ($5F),Y         ; read pitch byte
$50F0   9D FB 54      STA $54FB,X         ; store pitch index ($54FB,X)

; --- FREQUENCY LOOKUP ---
; Convert pitch index to SID frequency and write to SID (if not inhibited)
$50F3   0A            ASL                 ; pitch * 2 (freq table is 16-bit pairs)
$50F4   A8            TAY                 ; Y = pitch * 2

$50F5   AD 28 55      LDA $5528           ; load drum output enable ($5528)
$50F8   10 21         BPL $511B           ; if >= 0 (drum output enabled): skip freq write
                                          ; ($5528=$FF = drum disabled -> N set -> BMI taken)
; Drum output DISABLED: write freq to SID
$50FA   B9 28 54      LDA $5428,Y         ; load freq_lo from table (freq_table[pitch].lo)
$50FD   8D 03 55      STA $5503           ; save freq_lo
$5100   B9 29 54      LDA $5429,Y         ; load freq_hi from table (freq_table[pitch].hi)
$5103   AC EB 54      LDY $54EB           ; Y = SID voice offset (0, 7, or 14)
$5106   99 01 D4      STA $D401,Y         ; write freq_hi to SID (V1=$D401, V2=$D408, V3=$D40F)
$5109   9D 1A 55      STA $551A,X         ; store freq_hi state ($551A,X = current freq_hi)
$510C   AD 03 55      LDA $5503           ; reload freq_lo
$510F   99 00 D4      STA $D400,Y         ; write freq_lo to SID
$5112   9D 1D 55      STA $551D,X         ; store freq_lo state ($551D,X = current freq_lo)
$5115   4C 1B 51      JMP $511B           ; fall through

; --- TIE PATH: decrement gate enable counter ---
$5118   CE 01 55      DEC $5501           ; $5501-- (was $FF, now $FE = gate enable becomes 0 = off)
                                          ; This causes gate bit to be cleared for tied notes

; =============================================================================
; INSTRUMENT WRITE: write instrument parameters to SID
; =============================================================================
; At this point: Y = SID offset (from $54EB)
; Write ctrl, pw_lo, pw_hi, ad, sr to SID registers for this voice.

$511B   AC EB 54      LDY $54EB           ; Y = SID voice offset
$511E   BD FE 54      LDA $54FE,X         ; A = instrument number
$5121   8E 04 55      STX $5504           ; save X (voice index)
$5124   0A            ASL                 ; instrument * 2
$5125   0A            ASL                 ; * 4
$5126   0A            ASL                 ; * 8 (instrument table is 8 bytes per entry)
$5127   AA            TAX                 ; X = instrument * 8 = table offset
$5128   BD 93 55      LDA $5593,X         ; load ctrl byte (instr_table[instr].ctrl = byte 2)
                                          ; Table at $5591: pw_lo=+0, pw_hi=+1, ctrl=+2
                                          ; So $5591+X+2 = $5593+X
$512B   8D 05 55      STA $5505           ; save ctrl

$512E   AD 28 55      LDA $5528           ; load drum output enable
$5131   10 21         BPL $5154           ; if drum output enabled: skip SID instrument write

; Drum output DISABLED: write full instrument to SID
$5133   BD 93 55      LDA $5593,X         ; ctrl byte
$5136   2D 01 55      AND $5501           ; AND with gate enable ($FF=keep gate, $FE=clear gate)
$5139   99 04 D4      STA $D404,Y         ; write ctrl (gate on/off) to SID ctrl register
$513C   BD 91 55      LDA $5591,X         ; pw_lo byte (instr_table[instr].pw_lo = byte 0)
$513F   99 02 D4      STA $D402,Y         ; write pw_lo to SID (V1=$D402, V2=$D409, V3=$D410)
$5142   BD 92 55      LDA $5592,X         ; pw_hi byte (byte 1)
$5145   99 03 D4      STA $D403,Y         ; write pw_hi to SID
$5148   BD 94 55      LDA $5594,X         ; ad byte (byte 3)
$514B   99 05 D4      STA $D405,Y         ; write AD to SID
$514E   BD 95 55      LDA $5595,X         ; sr byte (byte 4)
$5151   99 06 D4      STA $D406,Y         ; write SR to SID

; --- Restore X, save ctrl for later use ---
$5154   AE 04 55      LDX $5504           ; restore X = voice index
$5157   AD 05 55      LDA $5505           ; reload ctrl byte
$515A   9D F8 54      STA $54F8,X         ; store ctrl ($54F8,X = ctrl for this voice)

; --- Advance note index, check for end-of-pattern ($FF) ---
$515D   FE EF 54      INC $54EF,X         ; advance note index (consumed pitch byte)
$5160   BC EF 54      LDY $54EF,X         ; Y = new note index
$5163   B1 5F         LDA ($5F),Y         ; peek at next byte
$5165   C9 FF         CMP #$FF            ; is it $FF (end of pattern)?
$5167   D0 08         BNE $5171           ; no: continue
; End of pattern: wrap back to start
$5169   A9 00         LDA #$00
$516B   9D EF 54      STA $54EF,X         ; reset note index to 0 (start of pattern)
$516E   FE EC 54      INC $54EC,X         ; advance to next sequence entry
$5171   4C 8F 53      JMP $538F           ; -> update drum enable, next voice

; =============================================================================
; SUSTAIN PATH: note still playing (duration > 0)
; Apply release if at end and gate-off needed
; =============================================================================

$5174   AD 28 55      LDA $5528           ; load drum output enable
$5177   30 03         BMI $517C           ; if drum disabled (=$FF): proceed with release check
$5179   4C 8F 53      JMP $538F           ; drum enabled: skip all effects, go to next voice

; Check if note needs gate-off (release) at duration end
$517C   AC EB 54      LDY $54EB           ; Y = SID voice offset
$517F   BD F5 54      LDA $54F5,X         ; load raw note byte 0 (flags)
$5182   29 20         AND #$20            ; test bit 5 (no_release flag)
$5184   D0 15         BNE $519B           ; no_release set: skip gate-off, go to effects

$5186   BD F2 54      LDA $54F2,X         ; load duration countdown
$5189   D0 10         BNE $519B           ; duration not yet 0: skip gate-off, go to effects

; Duration reached 0 AND no no_release: clear gate bit (release note)
$518B   BD F8 54      LDA $54F8,X         ; load ctrl byte for this voice
$518E   29 FE         AND #$FE            ; clear bit 0 (gate bit)
$5190   99 04 D4      STA $D404,Y         ; write ctrl with gate cleared -> note release
$5193   A9 00         LDA #$00
$5195   99 05 D4      STA $D405,Y         ; clear AD (fast decay)
$5198   99 06 D4      STA $D406,Y         ; clear SR (silence on release)

; =============================================================================
; EFFECTS SECTION: vibrato, PW modulation, skydive, arpeggio, drum slide
; All happen every play call (not just on tick frames)
; =============================================================================

; Load fx_flags for current instrument
$519B   AD 28 55      LDA $5528           ; drum output enable
$519E   30 03         BMI $51A3           ; if drum disabled: apply effects
$51A0   4C 8F 53      JMP $538F           ; drum enabled: skip effects

$51A3   BD FE 54      LDA $54FE,X         ; instrument number
$51A6   0A            ASL                 ; * 2
$51A7   0A            ASL                 ; * 4
$51A8   0A            ASL                 ; * 8
$51A9   A8            TAY                 ; Y = instrument * 8
$51AA   8C 18 55      STY $5518           ; save instrument table offset

$51AD   B9 98 55      LDA $5598,Y         ; load fx_flags (instr_table[instr].fx_flags = byte 7)
                                          ; Note: $5591+Y+7 = $5598+Y
$51B0   8D 23 55      STA $5523           ; store fx_flags

$51B3   B9 97 55      LDA $5597,Y         ; load pwm_speed (instr_table[instr].pwm_speed = byte 6)
$51B6   8D 07 55      STA $5507           ; store pwm_speed (used as PW delta)

$51B9   B9 96 55      LDA $5596,Y         ; load vib_depth (instr_table[instr].vib_depth = byte 5)
$51BC   8D 06 55      STA $5506           ; store vib_depth

$51BF   F0 6F         BEQ $5230           ; if vib_depth = 0: skip vibrato section entirely

; =============================================================================
; VIBRATO / PORTAMENTO SECTION ($51C1 - $5229)
; Only executed if vib_depth != 0.
; Computes a frequency delta and adds/subtracts it from the current frequency.
; =============================================================================

; Calculate vibrato step index from frame counter (bits 2-0, mapped 0-3-0-3)
; This creates a triangular vibrato envelope cycling over 8 frames.
$51C1   AD 25 55      LDA $5525           ; load frame counter (0-255)
$51C4   29 07         AND #$07            ; keep bits 2-0 (0-7 cycle)
$51C6   C9 04         CMP #$04            ; >= 4?
$51C8   90 02         BCC $51CC           ; < 4: keep as-is (0,1,2,3)
$51CA   49 07         EOR #$07            ; >= 4: invert to (7,6,5,4) -> mapped to (0,1,2,3)
                                          ; So sequence: 0,1,2,3,3,2,1,0 (triangle)
$51CC   8D 0C 55      STA $550C           ; store vibrato step (0-3)

; Compute vibrato delta = vib_depth * (freq_next - freq_cur) / 2^(vib_steps-1)
; In other words: shift the semitone interval right by (vib_depth) steps.
; This computes the fractional semitone shift per frame.
$51CF   BD FB 54      LDA $54FB,X         ; pitch index
$51D2   0A            ASL                 ; pitch * 2 (freq table index)
$51D3   A8            TAY                 ; Y = pitch * 2
$51D4   38            SEC                 ; set carry
$51D5   B9 2A 54      LDA $542A,Y         ; freq_hi[pitch+1] (next note's hi byte)
                                          ; $5428 + pitch*2 + 2 -> $542A + pitch*2
$51D8   F9 28 54      SBC $5428,Y         ; subtract freq_hi[pitch] (current note's hi byte)
$51DB   8D 08 55      STA $5508           ; vibrato_delta_hi = hi[next] - hi[cur]
$51DE   B9 2B 54      LDA $542B,Y         ; freq_lo[pitch+1]
$51E1   F9 29 54      SBC $5429,Y         ; subtract freq_lo[pitch]
; Now A:$5508 = 16-bit delta (one semitone interval)
$51E4   4A            LSR                 ; shift right (divide by 2)
$51E5   6E 08 55      ROR $5508           ; rotate right into hi byte (16-bit right shift)
$51E8   CE 06 55      DEC $5506           ; decrement remaining vib_depth counter
$51EB   10 F7         BPL $51E4           ; loop: shift right (vib_depth+1) more times
; After loop: delta = (semitone_interval) >> (vib_depth+1)
; This is the vibrato frequency step per unit
$51ED   8D 09 55      STA $5509           ; store vibrato_delta_lo
$51F0   B9 28 54      LDA $5428,Y         ; freq_lo[pitch] = base freq lo
$51F3   8D 0A 55      STA $550A           ; vibrato_target_lo = base freq lo
$51F6   B9 29 54      LDA $5429,Y         ; freq_hi[pitch] = base freq hi
$51F9   8D 0B 55      STA $550B           ; vibrato_target_hi = base freq hi

; Apply vibrato steps: add delta * step_count to base freq
$51FC   BD F5 54      LDA $54F5,X         ; raw note byte 0
$51FF   29 1F         AND #$1F            ; extract duration field (bits 4-0)
$5201   C9 06         CMP #$06            ; duration >= 6?
$5203   90 1C         BCC $5221           ; < 6: skip vibrato addition (play base freq)
; Vibrato active (duration >= 6):
$5205   AC 0C 55      LDY $550C           ; Y = vibrato step (0-3)
$5208   88            DEY                 ; Y--
$5209   30 16         BMI $5221           ; if < 0 (step was 0): no addition, use base freq
$520B   18            CLC                 ; clear carry
$520C   AD 0A 55      LDA $550A           ; vibrato_target_lo
$520F   6D 08 55      ADC $5508           ; add vibrato_delta_hi (note: lo byte used for hi delta)
$5212   8D 0A 55      STA $550A           ; update vibrato_target_lo
$5215   AD 0B 55      LDA $550B           ; vibrato_target_hi
$5218   6D 09 55      ADC $5509           ; add vibrato_delta_lo
$521B   8D 0B 55      STA $550B           ; update vibrato_target_hi
$521E   4C 08 52      JMP $5208           ; loop (adds delta step_count times)

; Write computed frequency to SID
$5221   AC EB 54      LDY $54EB           ; Y = SID voice offset
$5224   AD 0A 55      LDA $550A           ; vibrato computed freq_lo
$5227   99 00 D4      STA $D400,Y         ; write freq_lo to SID
$522A   AD 0B 55      LDA $550B           ; vibrato computed freq_hi
$522D   99 01 D4      STA $D401,Y         ; write freq_hi to SID

; =============================================================================
; PW MODULATION SECTION ($5230 - $52B2)
; Controls pulse width changes, two modes:
;   bit3=1 (PW_UNI): simple add pwm_speed to pw_lo each frame
;   bit3=0 (bidirectional): oscillate pw between $08xx and $0Exx
; =============================================================================

$5230   AD 23 55      LDA $5523           ; load fx_flags
$5233   29 08         AND #$08            ; test bit 3 (PW_UNI mode)
$5235   F0 15         BEQ $524C           ; bit3=0: go to bidirectional PW mode

; --- UNIDIRECTIONAL PW MODE (bit3=1): simple increment ---
; Add pwm_speed to pw_lo, write new pw to SID
$5237   AC 18 55      LDY $5518           ; Y = instrument table offset
$523A   B9 91 55      LDA $5591,Y         ; pw_lo (instr_table[instr].pw_lo = byte 0)
$523D   6D 07 55      ADC $5507           ; add pwm_speed (carry from previous op, usually clear)
$5240   99 91 55      STA $5591,Y         ; update pw_lo in-place in instrument table
$5243   AC EB 54      LDY $54EB           ; Y = SID voice offset
$5246   99 02 D4      STA $D402,Y         ; write new pw_lo to SID
$5249   4C B3 52      JMP $52B3           ; done with PW, continue

; --- BIDIRECTIONAL PW MODE (bit3=0): oscillating sweep ---
; Period counter at $550D,X counts sub-ticks; direction flag at $5510,X.
; Sweeps pw_lo from $08 to $0E and back.
$524C   AD 07 55      LDA $5507           ; load pwm_speed (= oscillation period)
$524F   F0 62         BEQ $52B3           ; if 0: no PW modulation, skip

$5251   AC 18 55      LDY $5518           ; Y = instrument table offset
$5254   29 1F         AND #$1F            ; mask pwm_speed to 5 bits (0-31, period)
$5256   DE 0D 55      DEC $550D,X         ; decrement per-voice PW period counter
$5259   10 58         BPL $52B3           ; if >= 0: not yet time to step, skip

; Period expired: reload counter and step PW
$525B   9D 0D 55      STA $550D,X         ; reload period counter = pwm_speed & $1F
$525E   AD 07 55      LDA $5507           ; reload pwm_speed
$5261   29 E0         AND #$E0            ; keep upper 3 bits (step size = pwm_speed >> 5)
$5263   8D 24 55      STA $5524           ; $5524 = PW step size

$5266   BD 10 55      LDA $5510,X         ; load direction flag (0=rising, nonzero=falling)
$5269   D0 1A         BNE $5285           ; if falling: go to subtract mode

; --- RISING PW: add step to pw_lo ---
$526B   AD 24 55      LDA $5524           ; PW step size
$526E   18            CLC
$526F   79 91 55      ADC $5591,Y         ; add to pw_lo
$5272   48            PHA                 ; save new pw_lo
$5273   B9 92 55      LDA $5592,Y         ; load pw_hi
$5276   69 00         ADC #$00            ; propagate carry
$5278   29 0F         AND #$0F            ; keep lower nibble (PW is 12-bit: 0x000-0xFFF)
$527A   48            PHA                 ; save new pw_hi
$527B   C9 0E         CMP #$0E            ; reached upper boundary $0Exx?
$527D   D0 1D         BNE $529C           ; no: write and continue
$527F   FE 10 55      INC $5510,X         ; yes: flip direction (0->1 = start falling)
$5282   4C 9C 52      JMP $529C           ; write new PW

; --- FALLING PW: subtract step from pw_lo ---
$5285   38            SEC
$5286   B9 91 55      LDA $5591,Y         ; pw_lo
$5289   ED 24 55      SBC $5524           ; subtract step size
$528C   48            PHA                 ; save new pw_lo
$528D   B9 92 55      LDA $5592,Y         ; pw_hi
$5290   E9 00         SBC #$00            ; propagate borrow
$5292   29 0F         AND #$0F            ; keep lower nibble
$5294   48            PHA                 ; save new pw_hi
$5295   C9 08         CMP #$08            ; reached lower boundary $08xx?
$5297   D0 03         BNE $529C           ; no: write and continue
$5299   DE 10 55      DEC $5510,X         ; yes: flip direction (nonzero->lower = start rising)

; Write new PW to SID
$529C   8E 04 55      STX $5504           ; save voice index
$529F   AE EB 54      LDX $54EB           ; X = SID voice offset (for $D402+X style write)
$52A2   68            PLA                 ; pop pw_hi
$52A3   99 92 55      STA $5592,Y         ; update pw_hi in instrument table
$52A6   9D 03 D4      STA $D403,X         ; write pw_hi to SID ($D403 for V1)
$52A9   68            PLA                 ; pop pw_lo
$52AA   99 91 55      STA $5591,Y         ; update pw_lo in instrument table
$52AD   9D 02 D4      STA $D402,X         ; write pw_lo to SID
$52B0   AE 04 55      LDX $5504           ; restore voice index

; =============================================================================
; DRUM SLIDE EFFECT / SKYDIVE ($52B3 - $5335)
; fx_flags bit 0 = DRUM: adjusts freq_hi based on current note
; fx_flags bit 1 = SKYDIVE: decrements freq_hi by 1 each frame
; =============================================================================

$52B3   AC EB 54      LDY $54EB           ; Y = SID voice offset

; --- Check drum trigger ($5520,X) ---
$52B6   BD 20 55      LDA $5520,X         ; load drum trigger value
$52B9   F0 3F         BEQ $52FA           ; if 0: no drum effect, skip

; Drum trigger active: decode drum control
$52BB   29 7E         AND #$7E            ; mask bits 6-1 (drum speed/direction)
$52BD   8D 04 55      STA $5504           ; save drum delta
$52C0   BD 20 55      LDA $5520,X         ; reload drum trigger
$52C3   29 01         AND #$01            ; bit 0 = direction (0=up, 1=down)
$52C5   F0 1B         BEQ $52E2           ; 0=up: go to freq increment

; --- DRUM SLIDE DOWN: subtract delta from freq ---
$52C7   38            SEC
$52C8   BD 1D 55      LDA $551D,X         ; freq_lo
$52CB   ED 04 55      SBC $5504           ; subtract drum delta
$52CE   9D 1D 55      STA $551D,X         ; store new freq_lo
$52D1   99 00 D4      STA $D400,Y         ; write freq_lo to SID
$52D4   BD 1A 55      LDA $551A,X         ; freq_hi
$52D7   E9 00         SBC #$00            ; propagate borrow
$52D9   9D 1A 55      STA $551A,X         ; store new freq_hi
$52DC   99 01 D4      STA $D401,Y         ; write freq_hi to SID
$52DF   4C FA 52      JMP $52FA           ; done

; --- DRUM SLIDE UP: add delta to freq ---
$52E2   18            CLC
$52E3   BD 1D 55      LDA $551D,X         ; freq_lo
$52E6   6D 04 55      ADC $5504           ; add drum delta
$52E9   9D 1D 55      STA $551D,X         ; store new freq_lo
$52EC   99 00 D4      STA $D400,Y         ; write freq_lo to SID
$52EF   BD 1A 55      LDA $551A,X         ; freq_hi
$52F2   69 00         ADC #$00            ; propagate carry
$52F4   9D 1A 55      STA $551A,X         ; store new freq_hi
$52F7   99 01 D4      STA $D401,Y         ; write freq_hi to SID

; =============================================================================
; SKYDIVE / FREQ_HI DECREMENT ($52FA - $5335)
; fx_flags bit 1: if set, decrement freq_hi by 1 each frame (freq slide down)
; =============================================================================

$52FA   AD 23 55      LDA $5523           ; fx_flags
$52FD   29 01         AND #$01            ; test bit 0 (DRUM/skydive on V1 mode)
$52FF   F0 35         BEQ $5336           ; bit0=0: skip to next effect
; SKYDIVE active:
$5301   BD 1A 55      LDA $551A,X         ; freq_hi
$5304   F0 30         BEQ $5336           ; if 0: can't go lower, skip
$5306   BD F2 54      LDA $54F2,X         ; duration countdown
$5309   F0 2B         BEQ $5336           ; if 0: note releasing, skip
$530B   BD F5 54      LDA $54F5,X         ; raw note byte 0
$530E   29 1F         AND #$1F            ; get duration field
$5310   38            SEC
$5311   E9 01         SBC #$01            ; duration - 1
$5313   DD F2 54      CMP $54F2,X         ; compare with countdown
$5316   AC EB 54      LDY $54EB           ; Y = SID voice offset
$5319   90 10         BCC $532B           ; if duration-1 < countdown: note just started, no skydive
; Note not at start: decrement freq_hi
$531B   BD 1A 55      LDA $551A,X         ; freq_hi
$531E   DE 1A 55      DEC $551A,X         ; decrement freq_hi
$5321   99 01 D4      STA $D401,Y         ; write freq_hi to SID
; Check if we need gate off (drum finish)
$5324   BD F8 54      LDA $54F8,X         ; ctrl byte
$5327   29 FE         AND #$FE            ; clear gate bit
$5329   D0 08         BNE $5333           ; if ctrl & $FE != 0 (waveform active): stay gated
$532B   BD 1A 55      LDA $551A,X         ; freq_hi (original or decremented)
$532E   99 01 D4      STA $D401,Y         ; write freq_hi
$5331   A9 80         LDA #$80            ; load noise waveform ($80)
$5333   99 04 D4      STA $D404,Y         ; write ctrl/gate to SID (gates note on with $80+gate)

; =============================================================================
; ARPEGGIO SECTION ($5336 - $535D)
; fx_flags bit 1 = SKYDIVE: alternate freq +12 semitones every other frame
; =============================================================================

$5336   AD 23 55      LDA $5523           ; fx_flags
$5339   29 02         AND #$02            ; test bit 1 (SKYDIVE/ARPEGGIO flag)
$533B   F0 21         BEQ $535E           ; bit1=0: skip arpeggio
; Arpeggio conditions:
$533D   BD F5 54      LDA $54F5,X         ; raw note byte 0
$5340   29 1F         AND #$1F            ; duration field
$5342   C9 03         CMP #$03            ; duration >= 3?
$5344   90 18         BCC $535E           ; < 3: skip (short notes don't arp)
$5346   AD 25 55      LDA $5525           ; frame counter (0-255)
$5349   29 01         AND #$01            ; even/odd frame?
$534B   F0 11         BEQ $535E           ; even frame: skip (only arp on odd frames)
$534D   BD 1A 55      LDA $551A,X         ; freq_hi
$5350   F0 0C         BEQ $535E           ; if 0: skip
; Odd frame arpeggio: add +12 semitones (octave up)
; Note: "+12" actually reads 12 entries past the 96-entry freq table, into player state vars
$5352   FE 1A 55      INC $551A,X         ; freq_hi += 1 (simple approximation of +12 semitones)
$5355   FE 1A 55      INC $551A,X         ; freq_hi += 1 again
$5358   AC EB 54      LDY $54EB           ; Y = SID voice offset
$535B   99 01 D4      STA $D401,Y         ; write old freq_hi (before INC? - STA from before INC)
; Note: The STA uses pre-INC value of A (from BD 1A 55 at $534D)
; The INC at $5352,$5355 modifies memory but A still holds old value
; This is intentional: writes OLD freq_hi, state has NEW freq_hi

; =============================================================================
; ARPEGGIO FROM FREQ TABLE ($535E - $538E)
; fx_flags bit 2 = ARPEGGIO: use freq table to play alternating notes
; =============================================================================

$535E   AD 23 55      LDA $5523           ; fx_flags
$5361   29 04         AND #$04            ; test bit 2 (ARPEGGIO)
$5363   F0 2A         BEQ $538F           ; bit2=0: done with effects, next voice

; Arpeggio: alternate between base pitch and pitch+12 on alternating frames
$5365   AD 25 55      LDA $5525           ; frame counter
$5368   29 01         AND #$01            ; even/odd?
$536A   F0 09         BEQ $5375           ; even: use base pitch
; Odd frame: use pitch + 12
$536C   BD FB 54      LDA $54FB,X         ; base pitch index
$536F   18            CLC
$5370   69 0C         ADC #$0C            ; add 12 semitones (one octave up)
$5372   4C 78 53      JMP $5378           ; go to freq lookup

; Even frame: use base pitch
$5375   BD FB 54      LDA $54FB,X         ; base pitch index
; Fall through to freq lookup

$5378   0A            ASL                 ; pitch * 2 (freq table index)
$5379   A8            TAY                 ; Y = index into freq table
$537A   B9 28 54      LDA $5428,Y         ; freq_lo[pitch]
$537D   8D 03 55      STA $5503           ; save freq_lo
$5380   B9 29 54      LDA $5429,Y         ; freq_hi[pitch]
$5383   AC EB 54      LDY $54EB           ; Y = SID voice offset
$5386   99 01 D4      STA $D401,Y         ; write freq_hi to SID
$5389   AD 03 55      LDA $5503           ; reload freq_lo
$538C   99 00 D4      STA $D400,Y         ; write freq_lo to SID

; =============================================================================
; VOICE LOOP CONTINUE: update drum enable, next voice
; =============================================================================

$538F   A0 FF         LDY #$FF            ; Y = $FF (drum DISABLED default)
$5391   AD 26 55      LDA $5526           ; load $5526 (drum channel flag for this voice)
$5394   D0 06         BNE $539C           ; if nonzero: drum disabled (Y=$FF), skip check
$5396   AD 27 55      LDA $5527           ; load $5527 (end-of-song / drum state)
$5399   30 01         BMI $539C           ; if negative (bit7=1, end-of-song): disable drum
$539B   C8            INY                 ; Y = $00 (drum ENABLED)
$539C   8C 28 55      STY $5528           ; store drum enable: $FF=disabled, $00=enabled
$539F   CA            DEX                 ; X-- (next voice: 2->1->1->0->0->(-1))
$53A0   30 03         BMI $53A5           ; if X < 0: all voices done, go to drum engine
$53A2   4C 5F 50      JMP $505F           ; next voice (continue voice loop)

; =============================================================================
; DRUM ENGINE ENTRY ($53A5)
; After all 3 voices processed, run drum engine.
; Drum engine plays a separate virtual pattern on SID V1/V2 using stored freq table.
; =============================================================================

$53A5   A9 FF         LDA #$FF
$53A7   8D 28 55      STA $5528           ; disable drum output ($5528=$FF) for safety

; Check if we should run drum engine at all
$53AA   AD 26 55      LDA $5526           ; drum inhibit flag ($5526=0 means run drum engine)
$53AD   D0 05         BNE $53B4           ; nonzero: skip drum engine, return
$53AF   2C 27 55      BIT $5527           ; test $5527:
                                          ;   bit7 (N) = 1 if end-of-song (negative)
                                          ;   bit6 (V) = 1 if first-play / needs drum init
$53B2   10 01         BPL $53B5           ; if N=0 (not end-of-song): run drum engine
$53B4   60            RTS                 ; return (end of play call)

; --- DRUM ENGINE ACTIVE ---
; Check if drum needs initialization (bit6 of $5527 = V flag set from BIT)
$53B5   50 03         BVC $53BA           ; if V=0: no init needed, go to drum tick
$53B7   20 31 55      JSR $5531           ; V=1: initialize drum engine (sets up drum pattern)

; --- DRUM TICK ---
$53BA   CE 2A 55      DEC $552A           ; decrement drum sub-counter
$53BD   10 F5         BPL $53B4           ; if >= 0: not yet time for drum step, return
; Sub-counter expired: reload and step drum
$53BF   AD 30 55      LDA $5530           ; drum_flags
$53C2   29 0F         AND #$0F            ; low nibble = sub-counter reload value
$53C4   8D 2A 55      STA $552A           ; reload sub-counter

; Check if drum sequence is complete
$53C7   AD 29 55      LDA $5529           ; drum counter (current note position)
$53CA   CD 2B 55      CMP $552B           ; compare with drum_limit
$53CD   D0 0F         BNE $53DE           ; not at limit: play drum step

; Drum sequence complete: reset and silence
$53CF   A2 00         LDX #$00
$53D1   8E 04 D4      STX $D404           ; V1 ctrl = 0 (silence)
$53D4   8E 0B D4      STX $D40B           ; V2 ctrl = 0 (silence)
$53D7   CA            DEX                 ; X = $FF
$53D8   8E 27 55      STX $5527           ; $5527 = $FF (mark drum channel ready for next init)
$53DB   4C B4 53      JMP $53B4           ; return

; --- DRUM STEP: advance drum note position ---
; The opcode at $53DE is patched by $5531:
;   $CE (DEC abs) = decrement drum counter (count down)
;   $EE (INC abs) = increment drum counter (count up)
$53DE   CE 29 55      DEC $5529           ; [or INC] advance drum counter by 1

; Compute freq table index for this drum step
$53E1   0A            ASL                 ; drum_counter * 2 (freq table index)
$53E2   A8            TAY                 ; Y = freq index

; Check drum control flags
$53E3   2C 30 55      BIT $5530           ; test drum_flags: N=bit7 (V1 freq), V=bit6 (V2 freq)
$53E6   30 20         BMI $5408           ; N=1: skip V1 freq write (V1 not used)
$53E8   70 0C         BVS $53F6           ; V=1: skip V2 calc but write V1 freq

; Write V1 frequency
$53EA   B9 28 54      LDA $5428,Y         ; freq_lo for this drum step
$53ED   8D 00 D4      STA $D400           ; write V1 freq_lo
$53F0   B9 29 54      LDA $5429,Y         ; freq_hi for this drum step
$53F3   8D 01 D4      STA $D401           ; write V1 freq_hi

; Write V2 frequency (offset from V1 by drum_interval semitones)
$53F6   98            TYA                 ; Y = drum freq index
$53F7   38            SEC
$53F8   ED 2C 55      SBC $552C           ; subtract drum_interval ($552C bytes = half-semitones)
$53FB   A8            TAY                 ; Y = V2 freq index
$53FC   B9 28 54      LDA $5428,Y         ; freq_lo for V2
$53FF   8D 07 D4      STA $D407           ; write V2 freq_lo
$5402   B9 29 54      LDA $5429,Y         ; freq_hi for V2
$5405   8D 08 55      STA $D408           ; write V2 freq_hi

; Apply drum gate toggling
$5408   2C 2D 55      BIT $552D           ; test drum_ctrl_flags: N=bit7, V=bit6
$540B   10 0B         BPL $5418           ; N=0: V1 gate not toggled
$540D   AD 2E 55      LDA $552E           ; V1 gate state
$5410   49 01         EOR #$01            ; toggle bit 0
$5412   8D 04 D4      STA $D404           ; write to V1 ctrl (gate on/off)
$5415   8D 2E 55      STA $552E           ; save new V1 gate state

$5418   50 0B         BVC $5425           ; V=0: V2 gate not toggled
$541A   AD 2F 55      LDA $552F           ; V2 gate state
$541D   49 01         EOR #$01            ; toggle bit 0
$541F   8D 0B D4      STA $D40B           ; write to V2 ctrl
$5422   8D 2F 55      STA $552F           ; save new V2 gate state

$5425   4C B4 53      JMP $53B4           ; return (RTS at $53B4)

; =============================================================================
; DRUM INIT SUBROUTINE ($5531)
; Called once at drum channel start (when $5527 has bit6=1)
; Loads drum pattern parameters from drum table and programs SID V1/V2.
; =============================================================================

$5531   A9 00         LDA #$00
$5533   8D 04 D4      STA $D404           ; silence V1 (clear ctrl)
$5536   8D 0B D4      STA $D40B           ; silence V2 (clear ctrl)
$5539   8D 2A 55      STA $552A           ; reset drum sub-counter to 0

$553C   AD 27 55      LDA $5527           ; load drum state ($FF on first call)
$553F   29 0F         AND #$0F            ; keep low nibble (drum pattern index 0-15)
$5541   8D 27 55      STA $5527           ; store back (cleared high nibble)
; drum_idx now 0-15

; Multiply by 16 to get table offset
$5544   0A            ASL
$5545   0A            ASL
$5546   0A            ASL
$5547   0A            ASL                 ; * 16
$5548   A8            TAY                 ; Y = drum_idx * 16

; Load drum table parameters
$5549   B9 F9 55      LDA $55F9,Y         ; drum_flags byte
$554C   8D 30 55      STA $5530           ; store drum_flags

$554F   B9 FA 55      LDA $55FA,Y         ; drum_counter start value
$5552   8D 29 55      STA $5529           ; store drum_counter

$5555   B9 08 56      LDA $5608,Y         ; drum_limit
$5558   8D 2B 55      STA $552B           ; store drum_limit

$555B   B9 01 56      LDA $5601,Y         ; drum_ctrl_flags
$555E   8D 2D 55      STA $552D           ; store drum_ctrl_flags

$5561   29 3F         AND #$3F            ; mask to lower 6 bits = drum_interval
$5563   8D 2C 55      STA $552C           ; store drum_interval (semitone offset for V2)

$5566   B9 FE 55      LDA $55FE,Y         ; drum_gate1 initial state
$5569   8D 2E 55      STA $552E           ; store V1 gate state

$556C   B9 05 56      LDA $5605,Y         ; drum_gate2 initial state
$556F   8D 2F 55      STA $552F           ; store V2 gate state

; Bulk-write 14 bytes of drum SID data to $D400-$D40D
; (freq, PW, ctrl, AD, SR for V1 and V2)
$5572   A2 00         LDX #$00
$5574   B9 FA 55      LDA $55FA,Y         ; read drum table data (starting at counter_start byte)
$5577   9D 00 D4      STA $D400,X         ; write to $D400+X
$557A   C8            INY                 ; advance table pointer
$557B   E8            INX                 ; advance SID register
$557C   E0 0E         CPX #$0E            ; done 14 registers ($D400-$D40D)?
$557E   D0 F4         BNE $5574           ; no: loop

; Determine drum direction: patch opcode at $53DE
$5580   AD 30 55      LDA $5530           ; drum_flags
$5583   29 30         AND #$30            ; test bits 5-4
$5585   A0 EE         LDY #$EE            ; Y = $EE (INC abs opcode - counts UP)
$5587   C9 20         CMP #$20            ; bits 5-4 = $20 -> DEC mode?
$5589   F0 02         BEQ $558D           ; equal: use DEC opcode (Y stays $EE? no...)
$558B   A0 CE         LDY #$CE            ; NOT equal: Y = $CE (DEC abs opcode - counts DOWN)
$558D   8C DE 53      STY $53DE           ; SELF-MODIFY: patch drum step opcode at $53DE
                                          ; $EE = INC = drum counts up
                                          ; $CE = DEC = drum counts down
$5590   60            RTS                 ; return to drum engine

; =============================================================================
; END OF DISASSEMBLY
; =============================================================================
;
; KEY MUSICAL FEATURES SUMMARY:
;
; 1. TEMPO: speed counter at $5513, reset value at $5517.
;    A "tick" (note advance) happens every ($5517+1) frames.
;    For Commando song 0: $5517=2 -> tick every 3 frames (50/3 ≈ 16.7 Hz).
;
; 2. NOTE FORMAT: 2-3 bytes per note event.
;    Byte 0: flags (bit7=new_instr, bit6=tie, bit5=no_release) + duration (bits4-0).
;    Byte 1: (if bit7): instrument/drum number.
;    Byte 2: pitch index into freq table.
;
; 3. VIBRATO: Triangular wave, 8-frame period. Depth = number of right-shifts
;    applied to the semitone interval. Higher depth = smaller vibrato range.
;    Only active on notes with duration >= 6.
;
; 4. PW MODULATION: Two modes:
;    - UNIDIRECTIONAL (bit3=1): add pwm_speed to pw_lo each frame (wraps).
;    - BIDIRECTIONAL (bit3=0): oscillate pw between $08xx and $0Exx using period counter.
;
; 5. DRUM SLIDE (bit0 in drum trigger): slide freq_hi up or down by delta each frame.
;    Separate from the "DRUM" fx_flag; this is per-note drum effect.
;
; 6. SKYDIVE (fx bit1): decrement freq_hi by 1 each frame. Used for falling pitch.
;    Also combined with bit2 for arpeggio; the memory notes call this "skydive".
;
; 7. ARPEGGIO (fx bit2): alternate between pitch and pitch+12 (octave) each frame.
;    The +12 reads past the 96-entry freq table into player state memory,
;    producing low-frequency percussive values (the "Hubbard arpeggio trick").
;
; 8. DRUM ENGINE: Virtual 4th channel using SID V1 and V2.
;    Pattern = decrementing or incrementing freq table index.
;    V1 and V2 can play different freq values (separated by drum_interval).
;    Gate bits toggled each drum step for percussion gating.
;    16 drum patterns in table at $55F9, each 16 bytes.
