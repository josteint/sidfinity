SIDBASE = $D400
ZP      = $FB
chn_counter = $0B00
chn_tempo   = $0B01
chn_pattidx = $0B02
chn_songidx = $0B03
chn_trans   = $0B04
chn_gate    = $0B05
chn_wave    = $0B15
chn_ad      = $0B16
chn_freqlo  = $0B18
chn_freqhi  = $0B19
chn_pulselo = $0B1A
chn_pulsehi = $0B1B
chn_pattlo  = $0B2A
chn_patthi  = $0B2B
ol_lo       = $0B80
ol_hi       = $0B83
pattbl_lo   = $0C00
pattbl_hi   = $0C80

            * = $0800
            jmp init
            jmp play

init
            lda #$00
            ldx #$6F
_clr        sta $0B00,x
            dex
            bpl _clr
            ldx #$18
_sid        sta SIDBASE,x
            dex
            bpl _sid
            lda #$0F
            sta SIDBASE+$18
            lda #$06
            sta chn_tempo
            lda #$01
            sta chn_counter
            lda #$FE
            sta chn_gate
            lda #$41
            sta chn_wave
            lda #$09
            sta chn_ad
            lda #$08
            sta chn_pulselo
            sta chn_pulsehi
            lda #<orderlist0
            sta ol_lo
            lda #>orderlist0
            sta ol_hi
            ; Set up pattern pointer table
            lda #<pattern0
            sta pattbl_lo
            lda #>pattern0
            sta pattbl_hi
            rts

play
            lda ZP
            pha
            lda ZP+1
            pha
            ldx #$00
            jsr pv
            pla
            sta ZP+1
            pla
            sta ZP
            rts

pv          dec chn_counter,x
            bne _wr
            lda chn_tempo,x
            sta chn_counter,x
            lda chn_pattidx,x
            bne _rd
            jsr np
_rd         jsr rn
_wr
            lda chn_pattidx,x
            sta SIDBASE+$16
            lda chn_freqlo,x
            sta SIDBASE,x
            lda chn_freqhi,x
            sta SIDBASE+1,x
            lda chn_pulselo,x
            sta SIDBASE+2,x
            lda chn_pulsehi,x
            sta SIDBASE+3,x
            lda chn_wave,x
            and chn_gate,x
            sta SIDBASE+4,x
            lda chn_ad,x
            sta SIDBASE+5,x
            rts

np
            lda ol_lo
            sta ZP
            lda ol_hi
            sta ZP+1
            ldy chn_songidx,x
_olrd       lda (ZP),y
            cmp #$FF
            bne _olne
            iny
            lda (ZP),y
            tay
            jmp _olrd
_olne       pha
            iny
            lda (ZP),y
            sec
            sbc #$80
            sta chn_trans,x
            iny
            tya
            sta chn_songidx,x
            pla
            asl
            tay
            lda pattbl_lo,y
            sta chn_pattlo,x
            lda pattbl_hi,y
            sta chn_patthi,x
            lda #$00
            sta chn_pattidx,x
            rts

rn          lda chn_pattlo,x
            sta ZP
            lda chn_patthi,x
            sta ZP+1
            ldy chn_pattidx,x
            lda (ZP),y
            beq _ep
            cmp #$BD
            beq _rest
            cmp #$60
            bcc _rest
            sec
            sbc #$60
            tay
            lda flo,y
            sta chn_freqlo,x
            lda fhi,y
            sta chn_freqhi,x
            lda #$FF
            sta chn_gate,x
            ldy chn_pattidx,x
_rest       iny
            lda (ZP),y
            beq _ep
            tya
            sta chn_pattidx,x
            rts
_ep         lda #$00
            sta chn_pattidx,x
            rts

flo
            .byte $17,$27,$39,$4B,$5F,$74,$8A,$A1,$BA,$D4,$F0,$0E
            .byte $2D,$4E,$71,$96,$BE,$E8,$14,$43,$74,$A9,$E1,$1C
            .byte $5A,$9C,$E2,$2D,$7C,$CF,$28,$85,$E8,$52,$C1,$37
            .byte $B4,$39,$C5,$5A,$F7,$9E,$4F,$0A,$D1,$A3,$82,$6E
            .byte $68,$71,$8A,$B3,$EE,$3C,$9E,$15,$A2,$46,$04,$DC
            .byte $D0,$E2,$14,$67,$DD,$79,$3C,$29,$44,$8D,$08,$B8
            .byte $A1,$C5,$28,$CD,$BA,$F1,$78,$53,$87,$1A,$10,$71
            .byte $42,$89,$4F,$9B,$74,$E2,$F0,$A6,$0E,$33,$20,$FF
fhi
            .byte $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$02
            .byte $02,$02,$02,$02,$02,$02,$03,$03,$03,$03,$03,$04
            .byte $04,$04,$04,$05,$05,$05,$06,$06,$06,$07,$07,$08
            .byte $08,$09,$09,$0A,$0A,$0B,$0C,$0D,$0D,$0E,$0F,$10
            .byte $11,$12,$13,$14,$15,$17,$18,$1A,$1B,$1D,$1F,$20
            .byte $22,$24,$27,$29,$2B,$2E,$31,$34,$37,$3A,$3E,$41
            .byte $45,$49,$4E,$52,$57,$5C,$62,$68,$6E,$75,$7C,$83
            .byte $8B,$93,$9C,$A5,$AF,$B9,$C4,$D0,$DD,$EA,$F8,$FF

orderlist0  .byte $00, $80, $FF, $00
pattern0    .byte $90, $BD, $BD, $BD, $94, $BD, $BD, $BD
            .byte $97, $BD, $BD, $BD, $9C, $BD, $BD, $BD, $00
