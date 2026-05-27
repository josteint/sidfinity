; SIDfinity Player - Universal 6502 SID music player
; Assemble with: 64tass -o sidfinity.bin -b sidfinity.asm
;
; Variable layout: stride 7, X = 0/7/14 for voice 1/2/3
; Within each 7-byte stride group, variables pack at offsets +0 through +6.
; Three groups (A, B, C) hold all per-voice state.

SIDBASE     = $D400
ZP          = $FB           ; 2 zero-page bytes for indirect addressing

; Group A ($0B00): sequencer state
chn_counter = $0B00         ; +0: tempo countdown
chn_tempo   = $0B01         ; +1: tempo reload
chn_pattidx = $0B02         ; +2: index within current pattern (0 = need new pattern)
chn_songidx = $0B03         ; +3: index within orderlist
chn_trans   = $0B04         ; +4: transpose for current pattern
chn_gate    = $0B05         ; +5: gate mask ($FF=on, $FE=off)
chn_newnote = $0B06         ; +6: new note pending (note number, 0=none)

; Group B ($0B15): sound output
chn_wave    = $0B15         ; +0: waveform register value
chn_ad      = $0B16         ; +1: attack/decay
chn_sr      = $0B17         ; +2: sustain/release
chn_freqlo  = $0B18         ; +3: frequency lo
chn_freqhi  = $0B19         ; +4: frequency hi
chn_pulselo = $0B1A         ; +5: pulse width lo
chn_pulsehi = $0B1B         ; +6: pulse width hi

; Group C ($0B2A): table pointers
chn_pattlo  = $0B2A         ; +0: current pattern address lo
chn_patthi  = $0B2B         ; +1: current pattern address hi
chn_wvptr   = $0B2C         ; +2: wave table index
chn_wvcnt   = $0B2D         ; +3: wave table delay counter
chn_plptr   = $0B2E         ; +4: pulse table index
chn_plcnt   = $0B2F         ; +5: pulse table delay counter
chn_instr   = $0B30         ; +6: current instrument number

; Global state
g_volume    = $0B70
g_fltcuthi  = $0B71
g_fltctrl   = $0B72
g_fltmode   = $0B73

; Orderlist pointers per voice (indexed 0/1/2)
ol_lo       = $0B80         ; 3 bytes
ol_hi       = $0B83         ; 3 bytes

; Song data base address
SONGDATA    = $0C00

; Pattern pointer tables within song data
pattbl_lo   = SONGDATA      ; 128 lo bytes
pattbl_hi   = SONGDATA+128  ; 128 hi bytes

            * = $0800

            jmp init
            jmp play

; === Init ===
; A = subtune (0-based)

init
            pha

            ; Clear channel variables $0B00-$0B6F
            lda #$00
            ldx #$6F
_clr        sta $0B00,x
            dex
            bpl _clr

            ; Silence SID
            ldx #$18
_sid        sta SIDBASE,x
            dex
            bpl _sid

            ; Default volume
            lda #$0F
            sta g_volume
            sta SIDBASE+$18

            ; Default tempo (6 frames per row) for all voices
            lda #$06
            sta chn_tempo         ; voice 1 (+0)
            sta chn_tempo+7       ; voice 2 (+7)
            sta chn_tempo+14      ; voice 3 (+14)

            ; Set counters to 1 so first play() triggers immediately
            lda #$01
            sta chn_counter
            sta chn_counter+7
            sta chn_counter+14

            ; Gates off
            lda #$FE
            sta chn_gate
            sta chn_gate+7
            sta chn_gate+14

            pla
            rts

; === Play ===
; Called once per frame (50Hz PAL)

play
            ; Save zero page
            lda ZP
            pha
            lda ZP+1
            pha

            ; Process 3 voices
            ldx #$00
            jsr playvoice
            ldx #$07
            jsr playvoice
            ldx #$0E
            jsr playvoice

            ; Write filter + volume
            lda g_fltcuthi
            sta SIDBASE+$16
            lda g_fltctrl
            sta SIDBASE+$17
            lda g_fltmode
            ora g_volume
            sta SIDBASE+$18

            ; Restore zero page
            pla
            sta ZP+1
            pla
            sta ZP
            rts

; === Per-voice processing ===
; X = voice offset (0/7/14)

playvoice
            ; Decrement tempo counter
            dec chn_counter,x
            bne _write_regs

            ; Counter hit 0: reload and advance sequencer
            lda chn_tempo,x
            sta chn_counter,x

            ; Need new pattern?
            lda chn_pattidx,x
            bne _read_patt
            jsr seq_next_pattern

_read_patt  jsr seq_read_note

_write_regs
            ; Write all 7 SID registers for this voice
            lda chn_freqlo,x
            sta SIDBASE+0,x
            lda chn_freqhi,x
            sta SIDBASE+1,x
            lda chn_pulselo,x
            sta SIDBASE+2,x
            lda chn_pulsehi,x
            sta SIDBASE+3,x
            lda chn_wave,x
            and chn_gate,x        ; apply gate mask
            sta SIDBASE+4,x
            lda chn_ad,x
            sta SIDBASE+5,x
            lda chn_sr,x
            sta SIDBASE+6,x
            rts

; === Orderlist sequencer ===
; Advance to next pattern from the orderlist.
; X = voice offset (0/7/14), preserved.

seq_next_pattern
            ; Save X (voice offset)
            stx _restore_x+1

            ; Map voice offset to voice index for orderlist lookup
            lda voiceidx,x
            tax                   ; X = 0/1/2

            ; Load orderlist base address into ZP
            lda ol_lo,x
            sta ZP
            lda ol_hi,x
            sta ZP+1

            ; Restore voice offset
_restore_x  ldx #$00              ; self-modified

            ; Read orderlist at current position
            ldy chn_songidx,x

_ol_read    lda (ZP),y
            cmp #$FF              ; end marker?
            bne _ol_entry

            ; Loop: next byte is restart position
            iny
            lda (ZP),y
            tay
            jmp _ol_read

_ol_entry
            ; Byte is pattern number
            pha
            iny

            ; Next byte is transpose ($80 = no transpose)
            lda (ZP),y
            sec
            sbc #$80
            sta chn_trans,x
            iny

            ; Save updated orderlist position
            tya
            sta chn_songidx,x

            ; Look up pattern address from pattern pointer table
            pla                   ; pattern number
            asl                   ; * 2 for 16-bit pointer
            tay
            lda pattbl_lo,y
            sta chn_pattlo,x
            lda pattbl_hi,y
            sta chn_patthi,x

            ; Reset pattern index (start reading from byte 0)
            lda #$00
            sta chn_pattidx,x
            rts

; === Pattern reader ===
; Read next note/event from current pattern.
; X = voice offset (0/7/14), preserved.

seq_read_note
            ; Load pattern address into ZP
            lda chn_pattlo,x
            sta ZP
            lda chn_patthi,x
            sta ZP+1
            ldy chn_pattidx,x

            ; Read first byte
            lda (ZP),y

            ; $00 = end of pattern
            bne _not_endpatt
            sta chn_pattidx,x    ; set to 0 = need new pattern
            rts

_not_endpatt
            ; < $40 = instrument change
            cmp #$40
            bcs _check_fx
            sta chn_instr,x
            iny
            lda (ZP),y           ; read next byte (will be fx or note)

_check_fx
            ; < $60 = FX or FXONLY byte
            cmp #$60
            bcs _handle_note

            ; Is it FXONLY ($50-$5F)?
            pha
            and #$0F
            sta _fx_num+1         ; save command number
            pla
            cmp #$50
            bcs _fxonly

            ; FX ($00-$4F after instrument, or $40-$4F directly): note follows
_fx_num     lda #$00              ; self-modified: command number
            beq _fx_no_param
            iny
            lda (ZP),y           ; read parameter
_fx_no_param
            iny
            lda (ZP),y           ; read note byte
            jmp _handle_note

_fxonly
            ; FXONLY: rest, no note follows
            lda _fx_num+1
            beq _fxo_no_param
            iny
            lda (ZP),y           ; read parameter
_fxo_no_param
            ; Advance past this row
            iny
            lda (ZP),y
            beq _end_pattern
            tya
            sta chn_pattidx,x
            rts

_handle_note
            ; Check note type
            cmp #$BD              ; REST?
            beq _note_rest
            cmp #$BE              ; KEYOFF?
            beq _note_keyoff
            cmp #$BF              ; KEYON?
            beq _note_keyon
            cmp #$C0              ; Packed rest?
            bcs _note_packed_rest

            ; Normal note ($60-$BC)
            sec
            sbc #$60              ; convert to note index (0-92)
            clc
            adc chn_trans,x       ; add transpose
            tay
            lda freq_lo,y
            sta chn_freqlo,x
            lda freq_hi,y
            sta chn_freqhi,x

            ; Gate on
            lda #$FF
            sta chn_gate,x

            ; Fall through to advance

_note_rest
            ; Advance to next byte, check for end of pattern
            iny
            lda (ZP),y
            beq _end_pattern
            tya
            sta chn_pattidx,x
            rts

_note_keyoff
            lda #$FE
            sta chn_gate,x
            jmp _note_rest

_note_keyon
            lda #$FF
            sta chn_gate,x
            jmp _note_rest

_note_packed_rest
            ; Packed rest ($C0-$FF): skip this byte, count handled by caller
            ; For now just advance
            iny
            lda (ZP),y
            beq _end_pattern
            tya
            sta chn_pattidx,x
            rts

_end_pattern
            lda #$00
            sta chn_pattidx,x
            rts

; === PAL Frequency Table (96 notes, C-0 through B-7) ===

freq_lo
            .byte $17,$27,$39,$4B,$5F,$74,$8A,$A1,$BA,$D4,$F0,$0E
            .byte $2D,$4E,$71,$96,$BE,$E8,$14,$43,$74,$A9,$E1,$1C
            .byte $5A,$9C,$E2,$2D,$7C,$CF,$28,$85,$E8,$52,$C1,$37
            .byte $B4,$39,$C5,$5A,$F7,$9E,$4F,$0A,$D1,$A3,$82,$6E
            .byte $68,$71,$8A,$B3,$EE,$3C,$9E,$15,$A2,$46,$04,$DC
            .byte $D0,$E2,$14,$67,$DD,$79,$3C,$29,$44,$8D,$08,$B8
            .byte $A1,$C5,$28,$CD,$BA,$F1,$78,$53,$87,$1A,$10,$71
            .byte $42,$89,$4F,$9B,$74,$E2,$F0,$A6,$0E,$33,$20,$FF

freq_hi
            .byte $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$02
            .byte $02,$02,$02,$02,$02,$02,$03,$03,$03,$03,$03,$04
            .byte $04,$04,$04,$05,$05,$05,$06,$06,$06,$07,$07,$08
            .byte $08,$09,$09,$0A,$0A,$0B,$0C,$0D,$0D,$0E,$0F,$10
            .byte $11,$12,$13,$14,$15,$17,$18,$1A,$1B,$1D,$1F,$20
            .byte $22,$24,$27,$29,$2B,$2E,$31,$34,$37,$3A,$3E,$41
            .byte $45,$49,$4E,$52,$57,$5C,$62,$68,$6E,$75,$7C,$83
            .byte $8B,$93,$9C,$A5,$AF,$B9,$C4,$D0,$DD,$EA,$F8,$FF

; Voice offset to voice index lookup (0/7/14 -> 0/1/2)
voiceidx    .byte 0, 0, 0, 0, 0, 0, 0
            .byte 1, 1, 1, 1, 1, 1, 1
            .byte 2
