; TFX 2.8 player — selected disassembly fragments from Atariada.sid
; Source SID:  hvsc84/MUSICIANS/F/Factor6/Atariada.sid
; Load addr:   $1000, init=$1000, play=$1003
; Extracted:   2026-06-14 (READ-ONLY byte inspection, no emulator)
; Reliability: HIGH — manual 6502 decode of binary bytes

; ────────────────────────────────────────────────────────────────
; ENTRY VECTORS  $1000
; ────────────────────────────────────────────────────────────────

        ; $1000  PSID init entry
        JMP  $10FA          ; init routine
        ; $1003  PSID play entry
        JMP  $1172          ; play routine (dispatcher)
        ; $1006  Third entry (instrument/data table base)
        JMP  $1914

; ────────────────────────────────────────────────────────────────
; VERSION / SONG STRING AREA  $1009
; ────────────────────────────────────────────────────────────────
; $1009: '  (apostrophe delimiter)
; $100A-$101E: "TFX 2.8 BY RAY/UNREAL"  (R/U encoded with PETSCII shift: $D2/$D5)
; $101F: '
; $1020-$1037: "ATARIADA BY FACTOR6 2016!!"
; $1038: '  (end delimiter — marks start of freq table)
; Note: $1038 = 0x21 0x21 = "!!" — the final two chars of the title

; ────────────────────────────────────────────────────────────────
; FREQUENCY TABLE  $103A–$10F9  (192 bytes = 96 lo + 96 hi)
; ────────────────────────────────────────────────────────────────
; $103A–$1099: lo-bytes  [note_index]  (96 entries)
; $109A–$10F9: hi-bytes  [note_index]  (96 entries)
; 96 notes = 8 octaves × 12 semitones, C0–B7
; Engine reads:  LDA $103A,Y → freq_lo;  LDA $109A,Y → freq_hi
; The last byte of hi-table differs between v1.0 ($FC) and v2.8 ($96).

; C0 freq (note 0):  lo=$01 hi=$0C → $0C01 = 3073 → ~180 Hz
; C4 freq (note 48): lo=$10 hi=$C3 → $C310 = 49936 → ~2932 Hz
;   (These are not standard PAL C64 values — TFX uses its own tuning table)

; ────────────────────────────────────────────────────────────────
; INIT ROUTINE  $10FA
; ────────────────────────────────────────────────────────────────

init:
        ASL                 ; A = subtune_num × 8  (3 left-shifts)
        ASL
        ASL
        STA  $1120          ; SMC: patches operand of LDY in voice-init sub
        TAY                 ; Y = subtune × 8
        LDA  $1BD5,Y        ; song init byte 0 (filter/vol default lo)
        STA  $1183          ; SMC: patches play filter default byte
        LDA  $1BD6,Y        ; song init byte 1 (filter/vol default hi)
        STA  $11BF          ; SMC: patches $D418 write value in play tail
        LDX  #$01
        STX  $117B          ; voice counter (1 = first voice flag)
        DEX                 ; X = 0
        STX  $11CB          ; gate-on mask clear
        STX  $119B          ; active-note flag clear
        JSR  $111F          ; init voice 1  (X=0)
        JSR  $111F          ; init voice 2  (increments X inside)

; voice_init_sub  ($111F):
;   LDY #subtune×8  ← PATCHED by STA $1120 above (SMC)
;   LDA $1BCF,Y → pattern ptr lo → STA $1901,X
;   LDA $1BD2,Y → pattern ptr hi → STA $1902,X
;   LDA #$01 → STA $18D5,X $18DA,X $1904,X  (speed counter = 1)
;   LDA #$00 → STA $D405,X $D406,X          (clear AD/SR — SIDId signature region)
;   LDA #$08 → STA $D404,X                  (ctrl = TEST bit set = hard restart)
;   LDA #$FF → STA $18D6,X                  (note duration sentinel)
;   Loop Y=0..7: clear $186C–$1896 per-voice state (7 per-voice slots)
;   INX (advance voice index by 7)
;   INC $1120                                (bump SMC offset for next voice)

; ── SIDId signature sits here: ──────────────────────────────────
; $1132:  9D DA 18   STA $18DA,X  (active-note flag)
; $1135:  9D 04 19   STA $1904,X  (note-counter)
; $1138:  A9 00      LDA #$00
; $113A:  9D 05 D4   STA $D405,X  ← SIDId anchor: AD = 0
; $113D:  9D 06 D4   STA $D406,X  ← SR = 0
; $1140:  A9 08      LDA #$08
; $1142:  9D 04 D4   STA $D404,X  ← ctrl = TEST
; Signature: 9D ?? ?? 9D ?? ?? A9 00 9D 05 D4 9D 06 D4 A9 ?? 9D 04 D4
; ────────────────────────────────────────────────────────────────

; ────────────────────────────────────────────────────────────────
; PLAY ROUTINE  $1172
; ────────────────────────────────────────────────────────────────

play:
        LDA  $B2            ; preserve ZP $B1/$B2 (pattern ptr scratch)
        PHA
        LDA  $B1
        PHA
        LDX  #$00           ; voice 1 (X=0, 7, 14)
        LDY  #$00
        STX  $16B1          ; ?
        DEY
        BPL  $115F          ; Y wraps: first call skips here

        ; For each voice, calls $11D5 (voice_process) with X=0, 7, 14:
        LDY  #$00
        STY  $117B
        JSR  $11D5          ; voice 1
        LDX  #$07
        JSR  $11D5          ; voice 2
        LDX  #$0E
        JSR  $11D5          ; voice 3

        ; Tail: restore $B1/$B2, write $D418/$D416/$D417 (filter/vol):
        PLA  → STA $B1
        PLA  → STA $B2
        LDA  #$0F           ; SMC: volume nibble (default 0F)
        ORA  #$30           ; filter mode bits
        STA  $D418          ; volume / filter mode
        LDA  #$50
        STA  $D416          ; filter cutoff (SMC patched by CMD_F8)
        LDA  #$01
        ORA  #$A0           ; filter resonance / voice routing
        STA  $D417

; ────────────────────────────────────────────────────────────────
; VOICE PROCESS  $11D5
; ────────────────────────────────────────────────────────────────

voice_process:
        LDA  $18DA,X        ; active flag (0 = voice muted)
        BEQ  → JMP $13EB    ; go to SID-register write sink directly
        DEC  $18D5,X        ; decrement speed counter
        BNE  → JMP $13EB    ; not yet zero → write current state
        ; counter hit 0: advance pattern
        LDA  $186F,X        ; loop-back marker
        BNE  $1230          ; non-zero → jump into pattern continuation

        ; Read next pattern byte:
        LDA  $1901,X → $B1  ; pattern ptr lo
        LDA  $1902,X → $B2  ; pattern ptr hi
        ; Use Y = $186C,X (position within current note group)
        LDA  ($B1),Y        ; fetch byte from pattern stream
        INY
        ; ... decodes via command table at $124B

; ────────────────────────────────────────────────────────────────
; PATTERN BYTE ENCODING
; ────────────────────────────────────────────────────────────────
; Each byte in the pattern stream is dispatched:
;   $00–$5F  note index 0–95 (direct freq table lookup, 96 notes C0–B7)
;   $60–$7F  arp/secondary-speed: (b & $1F) → $18D9,X
;   $80–$BF  primary duration/speed: (b & $3F) → $18D8,X + $18D5,X
;   $C0–$CF  ADSR nibble: (b & $0F) << 4 → $1883,X (used for $D405 AD)
;   $D0–$ED  instrument/event select: reads 1 arg byte; sets SMC loop point
;   $EE      vibrato-start: arg1=vibrato_speed, arg2=note/spd, arg3=base_note
;   $EF      glide: arg1=glide_speed, arg2=note_offset → $1872/$1871,X; $1870=current
;   $F1      set pattern loop-back (arg=Y pos); filter off ($119B=FF)
;   $F2      set AD directly: arg → $D405,X
;   $F3      set SR directly: arg → $D406,X
;   $F4      set vibrato depth: arg → $1897,X
;   $F5      gate-off mode: arg → $1896,X
;   $F6      set note counter: arg → $1904,X
;   $F8      set global filter cutoff: arg → SMC $11C6 + $16B3
;   $F9      set filter mode + master vol: arg nibbles → SMC $11CD + $11C1
;   $FA      set pulse width: arg → $18DB,X ($189A/$189B,X for PW lo/hi sweep)
;   $FB      set filter cutoff/mode per-song: arg → SMC $11BF
;   $FC      toggle gate: $1882,X ^= 1
;   $FD      loop/jump (reads loop target, possibly from $18D6)
;   $FE      voice-off: clears $18DA,X → voice muted
;   $FF      pattern end / next-segment marker

; ────────────────────────────────────────────────────────────────
; SID REGISTER WRITE ORDER per voice (from $13EB / $14CD region)
; ────────────────────────────────────────────────────────────────
; Per voice (X = 0, 7, 14):
;   $D406,X  ← SR  (sustain/release — may be cleared or held)
;   $D405,X  ← AD  (attack/decay)
;   $D404,X  ← ctrl (gate bit gated on, TEST bit managed)
;   $D403,X  ← PW hi  (pulse width, from sweep accumulator)
;   $D402,X  ← PW lo
;   $D401,X  ← freq hi
;   $D400,X  ← freq lo
; After all 3 voices:
;   $D418    ← master vol / filter mode  (ORA-ed constant pattern)
;   $D416    ← filter cutoff  (SMC or CMD_F8)
;   $D417    ← filter routing + resonance  (ORA-ed pattern)

; ────────────────────────────────────────────────────────────────
; INIT TABLE (song descriptors)  $1BCF
; ────────────────────────────────────────────────────────────────
; 8-byte records, one per subtune. Y = subtune × 8 addresses each record.
; Format (relative to record base):
;   [0]   V1 pattern ptr lo
;   [1]   V2 pattern ptr lo (may be same base area)
;   [2]   V3 pattern ptr lo
;   [3]   ptr2 lo (secondary channel / orderlist)
;   [4]   ptr2 hi
;   [5]   ?
;   [6]   $D418 init value (lo) → SMC $1183
;   [7]   $11BF init value (filter/vol) → SMC $11BF

; ────────────────────────────────────────────────────────────────
; MULTI-SPEED MECHANISM (when used)
; ────────────────────────────────────────────────────────────────
; TFX 2.7/2.8 CIA-timed variant (e.g. Bloedzuster):
;   PSID init vector → wrapper that sets CIA1 Timer A to sub-VBL period,
;   then JMPs to $1000. The CIA fires play() at 100 Hz (2× speed) or other.
;   Timer A = $2663 = 9827 cycles → 985248/9827 ≈ 100.3 Hz (2× PAL)
;
; TFX 1.3 multi-speed (e.g. Anubis):
;   PSID init → JSR $1000 (normal init) + set CIA + SMC counter in play wrapper
;   PSID play vector → wrapper at $2008+ that DEC-s counter and only calls
;   real play ($1003) every N frames, implementing N× speed via frame skipping.
;
; Standard (single-speed, most common): init=$1000, play=$1003, PSID speed=0.

; ────────────────────────────────────────────────────────────────
; RELOCATION
; ────────────────────────────────────────────────────────────────
; The TFX 2.8 engine can be relocated (e.g. Bytefest: $A000).
; Relocation = address fix-ups only; freq table and engine structure identical.
; Freq table at base+$3A (lo) and base+$9A (hi) in v2.x.
; Freq table at base+$00 (lo) and base+$60 (hi) in v1.0.

; ────────────────────────────────────────────────────────────────
; PER-VOICE STATE RAM  (X=0 voice1, X=7 voice2, X=14 voice3)
; ────────────────────────────────────────────────────────────────
; $186C,X  pattern Y-index (current position within note group)
; $186D,X  ?
; $186E,X  signed note transpose (applied to note index at load)
; $186F,X  loop-back Y marker (non-zero = in repeat block)
; $1870,X  vibrato/glide current freq accumulator lo
; $1871,X  vibrato/glide target note offset
; $1872,X  vibrato speed / glide speed
; $1881,X  countdown / length counter
; $1882,X  gate state (XOR-toggled by $FC command)
; $1883,X  ADSR nibble for D405 (attack/decay)
; $1886,X  instrument flags (bit 4 = tone; bits 6/7 = ring/sync; bit 7 = SR-release)
; $1887,X  ?
; $1896,X  gate-off mode flag (set by CMD_F5)
; $1897,X  vibrato depth (set by CMD_F4)
; $1898,X  some trigger flag
; $189A,X  pulse width lo (from CMD_FA upper nibble × 16)
; $189B,X  pulse width hi (from CMD_FA lower nibble)
; $18AD,X  freq accumulator lo (for glide / vibrato freq offset)
; $18AE,X  freq accumulator hi
; $18D5,X  speed counter (current ticks remaining)
; $18D6,X  note duration (−1 = $FE sentinel = end-of-note)
; $18D7,X  current note index (post-transpose)
; $18D8,X  primary speed value (set by $80–$BF commands)
; $18D9,X  secondary / arp speed (set by $60–$7F commands)
; $18DA,X  active flag (0 = voice muted, set by $FE command)
; $18DB,X  pulse-width raw value (from CMD_FA)
; $1901,X  pattern ptr lo (16-bit ZP indirect via $B1/$B2)
; $1902,X  pattern ptr hi
; $1904,X  note counter (set by CMD_F6)

; ────────────────────────────────────────────────────────────────
; GLOBAL SMC STATE (patched by commands or init)
; ────────────────────────────────────────────────────────────────
; $1120    LDY operand in voice-init sub → subtune × 8 (patched by init)
; $1183    $D418 default value lo (set from init table byte [6])
; $11BF    $D418 / filter val (set by CMD_FB or init table byte [7])
; $11C1    Filter mode bits (from CMD_F9 arg upper nibble)
; $11C6    Filter cutoff (from CMD_F8)
; $11CB    Gate-on mask
; $11CD    Volume + filter mode (from CMD_F9 arg lower nibble)
; $16B3    Filter cutoff mirror (CMD_F8 also patches here)
