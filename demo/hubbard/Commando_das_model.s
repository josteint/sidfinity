        * = $1000
        jmp init
        jmp play

init
        lda #$0F
        sta $D418
        lda #$FF
        sta $B3
        lda #0
        sta $B4
        sta $B5
        lda v0ol
        sta $83
        lda v0ol+1
        sta $84
        lda #<(v0ol+2)
        sta $81
        lda #>(v0ol+2)
        sta $82
        lda #0
        sta $85
        sta $86
        sta $87
        sta $89
        sta $8A
        sta $8B
        sta $8C
        sta $8D
        sta $8F
        sta $90
        lda #$FF
        sta $8E
        lda #1
        sta $80
        lda v1ol
        sta $94
        lda v1ol+1
        sta $95
        lda #<(v1ol+2)
        sta $92
        lda #>(v1ol+2)
        sta $93
        lda #0
        sta $96
        sta $97
        sta $98
        sta $9A
        sta $9B
        sta $9C
        sta $9D
        sta $9E
        sta $A0
        sta $A1
        lda #$FF
        sta $9F
        lda #1
        sta $91
        lda v2ol
        sta $A5
        lda v2ol+1
        sta $A6
        lda #<(v2ol+2)
        sta $A3
        lda #>(v2ol+2)
        sta $A4
        lda #0
        sta $A7
        sta $A8
        sta $A9
        sta $AB
        sta $AC
        sta $AD
        sta $AE
        sta $AF
        sta $B1
        sta $B2
        lda #$FF
        sta $B0
        lda #1
        sta $A2
        rts

play
        inc $B3
        lda $B4
        sta ftlo+104
        lda $B5
        sta fthi+104
        lda $A0
        sta ftlo+100
        lda $B1
        sta fthi+100
; --- Voice 3 ---
        dec $A2
        beq v2rd
        jmp v2eval
v2rd
        ldy #0
        lda ($A5),y
        cmp #$FE
        bne v2nt
        lda #0
        sta $B1
        lda #$FF
        sta $B0
        ldy #0
        lda ($A3),y
        sta $A5
        iny
        lda ($A3),y
        sta $A6
        clc
        lda $A3
        adc #2
        sta $A3
        bcc v2rd
        inc $A4
        jmp v2rd
v2nt
        sta $AA
        iny
        lda ($A5),y
        tax
        lda #0
v2mul  clc
        adc #3
        dex
        bne v2mul
        sta $A2
        sta $AB
        sec
        sbc #3
        sta $A8
        iny
        lda ($A5),y
        sta $B6
        and #$3F
        tax
        stx $B0
        lda $B6
        and #$40
        bne v2hubt
        lda $B6
        bmi v2hub2
        lda $B1
        clc
        adc #3
        sta $B1
        jmp v2hubx
v2hub2
        lda $B1
        clc
        adc #2
        sta $B1
        jmp v2hubx
v2hubt
        lda $B1
        clc
        adc #1
        sta $B1
v2hubx
        lda $B6
        and #$40
        bne v2tie
        lda $AA
        tay
        lda fthi,y
        sta $D40F
        sta $B2
        lda ftlo,y
        sta $D40E
        lda i_ctrl,x
        sta $D412
        jmp v2pw0
v2tie
        lda i_ctrl,x
        and #$FE
        sta $D412
v2pw0
        lda pw_live,x
        sta $D410
        sta $A9
        lda i_pwhi,x
        sta $D411
        sta $AD
        lda i_ad,x
        sta $D413
        lda i_sr,x
        sta $D414
        lda i_pws,x
        sta $AC
        lda i_pwmax,x
        sta $AE
        clc
        lda $A5
        adc #3
        sta $A5
        bcc v2nd1
        inc $A6
v2nd1
        jmp v2done

v2eval
        lda $A2
        cmp #3
        bne v2efx
        ldy $B0
        lda i_ctrl,y
        and #$FE
        sta $D412
        lda #0
        sta $D413
        sta $D414
v2efx
        ldy $B0
        lda i_vib,y
        beq v2bit0
        lda $AB
        cmp #18
        bcs v2vlong
        ldx $AA
        lda fthi,x
        sta $D40E
        lda ftlo,x
        sta $D40F
        jmp v2bit0
v2vlong
        lda $B3
        and #$07
        cmp #4
        bcc v2vdok
        eor #$07
v2vdok
        pha
        ldx $AA
        lda fthi+1,x
        sec
        sbc fthi,x
        sta $B6
        ldy $B0
        ldx i_vib,y
        inx
v2vsr
        lsr $B6
        dex
        bne v2vsr
        pla
        beq v2vwr
        tax
        lda #0
v2vmul
        clc
        adc $B6
        dex
        bne v2vmul
        ldx $AA
        clc
        adc fthi,x
        sta $B6
        lda ftlo,x
        sta $D40E
        lda $B6
        sta $D40F
        jmp v2bit0
v2vwr
        ldx $AA
        lda ftlo,x
        sta $D40E
        lda fthi,x
        sta $D40F
v2bit0
        ldy $B0
        lda i_bit0,y
        beq v2arpc
        lda $A2
        cmp #4
        bcc v2arpc
        lda $B2
        beq v2arpc
        lda $A8
        cmp $A2
        bcs v2bns
        lda $B2
        sta $D40F
        lda #$80
        sta $D412
        jmp v2arpc
v2bns
        lda $B2
        sta $D40F
        dec $B2
        lda i_ctrl,y
        and #$FE
        bne v2bcm
        lda $B2
        sta $D40F
        lda #$80
v2bcm
        sta $D412
v2arpc
        ldy $B0
        lda i_arp,y
        beq v2pw
        ldx $AA
        lda $B3
        and #$01
        beq v2frok
        txa
        clc
        adc i_arp,y
        tax
v2frok
        lda fthi,x
        sta $D40F
        lda ftlo,x
        sta $D40E
v2pw
        lda $AE
        beq v2done
        cmp #$FF
        beq v2lin
        dec $A7
        bpl v2done
        lda $AC
        and #$1F
        sta $A7
        lda $AC
        and #$E0
        sta $B6
        lda $AF
        bne v2dn
        clc
        lda $A9
        adc $B6
        sta $A9
        bcc v2ncu
        inc $AD
        lda $AD
        and #$0F
        sta $AD
v2ncu
        lda $AD
        cmp $AE
        bne v2pwwr
        inc $AF
        jmp v2pwwr
v2dn
        sec
        lda $A9
        sbc $B6
        sta $A9
        bcs v2ncd
        dec $AD
v2ncd
        lda $AD
        cmp #$08
        bne v2pwwr
        dec $AF
        jmp v2pwwr
v2lin
        clc
        lda $A9
        adc $AC
        sta $A9
        sta $D410
        ldy $B0
        sta pw_live,y
        jmp v2done
v2pwwr
        lda $A9
        sta $D410
        lda $AD
        sta $D411
        ldy $B0
        lda $A9
        sta i_pwlo,y
        lda $AD
        sta i_pwhi,y
v2done

; --- Voice 2 ---
        dec $91
        beq v1rd
        jmp v1eval
v1rd
        ldy #0
        lda ($94),y
        cmp #$FE
        bne v1nt
        lda #0
        sta $A0
        lda #$FF
        sta $9F
        ldy #0
        lda ($92),y
        sta $94
        iny
        lda ($92),y
        sta $95
        clc
        lda $92
        adc #2
        sta $92
        bcc v1rd
        inc $93
        jmp v1rd
v1nt
        sta $99
        iny
        lda ($94),y
        tax
        lda #0
v1mul  clc
        adc #3
        dex
        bne v1mul
        sta $91
        sta $9A
        sec
        sbc #3
        sta $97
        iny
        lda ($94),y
        sta $B6
        and #$3F
        tax
        stx $9F
        lda $B6
        and #$40
        bne v1hubt
        lda $B6
        bmi v1hub2
        lda $A0
        clc
        adc #3
        sta $A0
        jmp v1hubx
v1hub2
        lda $A0
        clc
        adc #2
        sta $A0
        jmp v1hubx
v1hubt
        lda $A0
        clc
        adc #1
        sta $A0
v1hubx
        lda $B6
        and #$40
        bne v1tie
        lda $99
        tay
        lda fthi,y
        sta $D408
        sta $A1
        lda ftlo,y
        sta $D407
        lda i_ctrl,x
        sta $B5
        sta $D40B
        jmp v1pw0
v1tie
        lda i_ctrl,x
        sta $B5
        and #$FE
        sta $D40B
v1pw0
        lda pw_live,x
        sta $D409
        sta $98
        lda i_pwhi,x
        sta $D40A
        sta $9C
        lda i_ad,x
        sta $D40C
        lda i_sr,x
        sta $D40D
        lda i_pws,x
        sta $9B
        lda i_pwmax,x
        sta $9D
        clc
        lda $94
        adc #3
        sta $94
        bcc v1nd1
        inc $95
v1nd1
        jmp v1done

v1eval
        lda $91
        cmp #3
        bne v1efx
        ldy $9F
        lda i_ctrl,y
        and #$FE
        sta $D40B
        lda #0
        sta $D40C
        sta $D40D
v1efx
        ldy $9F
        lda i_vib,y
        beq v1bit0
        lda $9A
        cmp #18
        bcs v1vlong
        ldx $99
        lda fthi,x
        sta $D407
        lda ftlo,x
        sta $D408
        jmp v1bit0
v1vlong
        lda $B3
        and #$07
        cmp #4
        bcc v1vdok
        eor #$07
v1vdok
        pha
        ldx $99
        lda fthi+1,x
        sec
        sbc fthi,x
        sta $B6
        ldy $9F
        ldx i_vib,y
        inx
v1vsr
        lsr $B6
        dex
        bne v1vsr
        pla
        beq v1vwr
        tax
        lda #0
v1vmul
        clc
        adc $B6
        dex
        bne v1vmul
        ldx $99
        clc
        adc fthi,x
        sta $B6
        lda ftlo,x
        sta $D407
        lda $B6
        sta $D408
        jmp v1bit0
v1vwr
        ldx $99
        lda ftlo,x
        sta $D407
        lda fthi,x
        sta $D408
v1bit0
        ldy $9F
        lda i_bit0,y
        beq v1arpc
        lda $91
        cmp #4
        bcc v1arpc
        lda $A1
        beq v1arpc
        lda $97
        cmp $91
        bcs v1bns
        lda $A1
        sta $D408
        lda #$80
        sta $D40B
        jmp v1arpc
v1bns
        lda $A1
        sta $D408
        dec $A1
        lda i_ctrl,y
        and #$FE
        bne v1bcm
        lda $A1
        sta $D408
        lda #$80
v1bcm
        sta $D40B
v1arpc
        ldy $9F
        lda i_arp,y
        beq v1pw
        ldx $99
        lda $B3
        and #$01
        beq v1frok
        txa
        clc
        adc i_arp,y
        tax
v1frok
        lda fthi,x
        sta $D408
        lda ftlo,x
        sta $D407
v1pw
        lda $9D
        beq v1done
        cmp #$FF
        beq v1lin
        dec $96
        bpl v1done
        lda $9B
        and #$1F
        sta $96
        lda $9B
        and #$E0
        sta $B6
        lda $9E
        bne v1dn
        clc
        lda $98
        adc $B6
        sta $98
        bcc v1ncu
        inc $9C
        lda $9C
        and #$0F
        sta $9C
v1ncu
        lda $9C
        cmp $9D
        bne v1pwwr
        inc $9E
        jmp v1pwwr
v1dn
        sec
        lda $98
        sbc $B6
        sta $98
        bcs v1ncd
        dec $9C
v1ncd
        lda $9C
        cmp #$08
        bne v1pwwr
        dec $9E
        jmp v1pwwr
v1lin
        clc
        lda $98
        adc $9B
        sta $98
        sta $D409
        ldy $9F
        sta pw_live,y
        jmp v1done
v1pwwr
        lda $98
        sta $D409
        lda $9C
        sta $D40A
        ldy $9F
        lda $98
        sta i_pwlo,y
        lda $9C
        sta i_pwhi,y
v1done

; --- Update T[100] and T[104] before V1 ---
        lda $A0
        sta ftlo+100
        lda $B1
        sta fthi+100
        lda $B4
        sta ftlo+104
        lda $B5
        sta fthi+104
; --- Voice 1 ---
        dec $80
        beq v0rd
        jmp v0eval
v0rd
        ldy #0
        lda ($83),y
        cmp #$FE
        bne v0nt
        lda #0
        sta $8F
        lda #$FF
        sta $8E
        ldy #0
        lda ($81),y
        sta $83
        iny
        lda ($81),y
        sta $84
        clc
        lda $81
        adc #2
        sta $81
        bcc v0rd
        inc $82
        jmp v0rd
v0nt
        sta $88
        iny
        lda ($83),y
        tax
        lda #0
v0mul  clc
        adc #3
        dex
        bne v0mul
        sta $80
        sta $89
        sec
        sbc #3
        sta $86
        iny
        lda ($83),y
        sta $B6
        and #$3F
        tax
        stx $8E
        lda $B6
        and #$40
        bne v0hubt
        lda $B6
        bmi v0hub2
        lda $8F
        clc
        adc #3
        sta $8F
        jmp v0hubx
v0hub2
        lda $8F
        clc
        adc #2
        sta $8F
        jmp v0hubx
v0hubt
        lda $8F
        clc
        adc #1
        sta $8F
v0hubx
        lda $B6
        and #$40
        bne v0tie
        lda $88
        tay
        lda fthi,y
        sta $D401
        sta $90
        lda ftlo,y
        sta $D400
        lda i_ctrl,x
        sta $B4
        sta $D404
        jmp v0pw0
v0tie
        lda i_ctrl,x
        sta $B4
        and #$FE
        sta $D404
v0pw0
        lda pw_live,x
        sta $D402
        sta $87
        lda i_pwhi,x
        sta $D403
        sta $8B
        lda i_ad,x
        sta $D405
        lda i_sr,x
        sta $D406
        lda i_pws,x
        sta $8A
        lda i_pwmax,x
        sta $8C
        clc
        lda $83
        adc #3
        sta $83
        bcc v0nd1
        inc $84
v0nd1
        jmp v0done

v0eval
        lda $80
        cmp #3
        bne v0efx
        ldy $8E
        lda i_ctrl,y
        and #$FE
        sta $D404
        lda #0
        sta $D405
        sta $D406
v0efx
        ldy $8E
        lda i_vib,y
        beq v0bit0
        lda $89
        cmp #18
        bcs v0vlong
        ldx $88
        lda fthi,x
        sta $D400
        lda ftlo,x
        sta $D401
        jmp v0bit0
v0vlong
        lda $B3
        and #$07
        cmp #4
        bcc v0vdok
        eor #$07
v0vdok
        pha
        ldx $88
        lda fthi+1,x
        sec
        sbc fthi,x
        sta $B6
        ldy $8E
        ldx i_vib,y
        inx
v0vsr
        lsr $B6
        dex
        bne v0vsr
        pla
        beq v0vwr
        tax
        lda #0
v0vmul
        clc
        adc $B6
        dex
        bne v0vmul
        ldx $88
        clc
        adc fthi,x
        sta $B6
        lda ftlo,x
        sta $D400
        lda $B6
        sta $D401
        jmp v0bit0
v0vwr
        ldx $88
        lda ftlo,x
        sta $D400
        lda fthi,x
        sta $D401
v0bit0
        ldy $8E
        lda i_bit0,y
        beq v0arpc
        lda $80
        cmp #4
        bcc v0arpc
        lda $90
        beq v0arpc
        lda $86
        cmp $80
        bcs v0bns
        lda $90
        sta $D401
        lda #$80
        sta $D404
        jmp v0arpc
v0bns
        lda $90
        sta $D401
        dec $90
        lda i_ctrl,y
        and #$FE
        bne v0bcm
        lda $90
        sta $D401
        lda #$80
v0bcm
        sta $D404
v0arpc
        ldy $8E
        lda i_arp,y
        beq v0pw
        ldx $88
        lda $B3
        and #$01
        beq v0frok
        txa
        clc
        adc i_arp,y
        tax
v0frok
        lda fthi,x
        sta $D401
        lda ftlo,x
        sta $D400
v0pw
        lda $8C
        beq v0done
        cmp #$FF
        beq v0lin
        dec $85
        bpl v0done
        lda $8A
        and #$1F
        sta $85
        lda $8A
        and #$E0
        sta $B6
        lda $8D
        bne v0dn
        clc
        lda $87
        adc $B6
        sta $87
        bcc v0ncu
        inc $8B
        lda $8B
        and #$0F
        sta $8B
v0ncu
        lda $8B
        cmp $8C
        bne v0pwwr
        inc $8D
        jmp v0pwwr
v0dn
        sec
        lda $87
        sbc $B6
        sta $87
        bcs v0ncd
        dec $8B
v0ncd
        lda $8B
        cmp #$08
        bne v0pwwr
        dec $8D
        jmp v0pwwr
v0lin
        clc
        lda $87
        adc $8A
        sta $87
        sta $D402
        ldy $8E
        sta pw_live,y
        jmp v0done
v0pwwr
        lda $87
        sta $D402
        lda $8B
        sta $D403
        ldy $8E
        lda $87
        sta i_pwlo,y
        lda $8B
        sta i_pwhi,y
v0done

        rts

ftlo
        .byte $16,$27,$38,$4B,$5F,$73,$8A,$A1,$BA,$D4,$F0,$0E,$2D,$4E,$71,$96
        .byte $BD,$E7,$13,$42,$74,$A9,$E0,$1B,$5A,$9B,$E2,$2C,$7B,$CE,$27,$85
        .byte $E8,$51,$C1,$37,$B4,$37,$C4,$57,$F5,$9C,$4E,$09,$D0,$A3,$82,$6E
        .byte $68,$6E,$88,$AF,$EB,$39,$9C,$13,$A1,$46,$04,$DC,$D0,$DC,$10,$5E
        .byte $D6,$72,$38,$26,$42,$8C,$08,$B8,$A0,$B8,$20,$BC,$AC,$E4,$70,$4C
        .byte $84,$18,$10,$70,$40,$70,$40,$78,$58,$C8,$E0,$98,$08,$30,$20,$2E
        .byte $00,$0E,$00,$00,$03,$03,$05,$81,$00,$41,$68,$07,$02,$83,$00,$00
        .byte $00,$00,$00,$00,$00,$00,$02,$02
fthi
        .byte $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$02,$02,$02,$02,$02
        .byte $02,$02,$03,$03,$03,$03,$03,$04,$04,$04,$04,$05,$05,$05,$06,$06
        .byte $06,$07,$07,$08,$08,$09,$09,$0A,$0A,$0B,$0C,$0D,$0D,$0E,$0F,$10
        .byte $11,$12,$13,$14,$15,$17,$18,$1A,$1B,$1D,$1F,$20,$22,$24,$27,$29
        .byte $2B,$2E,$31,$34,$37,$3A,$3E,$41,$45,$49,$4E,$52,$57,$5C,$62,$68
        .byte $6E,$75,$7C,$83,$8B,$93,$9C,$A5,$AF,$B9,$C4,$D0,$DD,$EA,$F8,$FD
        .byte $07,$00,$00,$03,$03,$01,$83,$85,$00,$58,$15,$04,$FF,$58,$15,$00
        .byte $00,$00,$00,$00,$00,$02,$03,$02

i_ad
        .byte $29,$06,$09,$0A,$0F,$05,$38,$0D,$49,$04,$09,$07,$09
i_sr
        .byte $5F,$4B,$9F,$09,$C4,$A9,$7A,$FB,$5B,$6F,$6B,$09,$0A
i_pwlo
        .byte $00,$80,$80,$00,$00,$80,$00,$80,$00,$00,$00,$00,$00
i_pwhi
        .byte $09,$01,$01,$02,$02,$08,$08,$01,$08,$08,$03,$02,$08
i_pws
        .byte $E0,$00,$16,$00,$00,$02,$E0,$00,$03,$00,$01,$00,$00
i_pwmax
        .byte $0E,$00,$FF,$00,$00,$FF,$0E,$00,$FF,$00,$FF,$00,$00
i_arp
        .byte $00,$0C,$00,$0C,$00,$0C,$00,$0C,$00,$0C,$0C,$00,$00
i_vib
        .byte $02,$00,$00,$00,$00,$00,$02,$01,$02,$03,$02,$01,$00
i_bit0
        .byte $00,$01,$00,$01,$01,$01,$00,$01,$00,$01,$01,$01,$01
i_ctrl
        .byte $41,$41,$41,$81,$43,$41,$41,$15,$41,$21,$41,$43,$41
pw_live
        .byte $00,$80,$80,$00,$00,$80,$00,$80,$00,$00,$00,$00,$00

pat1
        .byte $15,$06,$02
        .byte $21,$02,$82
        .byte $2E,$04,$03
        .byte $15,$04,$02
        .byte $15,$08,$82
        .byte $2E,$04,$03
        .byte $1F,$02,$02
        .byte $21,$02,$82
        .byte $FE
pat2
        .byte $16,$06,$02
        .byte $22,$02,$82
        .byte $2E,$04,$03
        .byte $16,$04,$02
        .byte $16,$08,$82
        .byte $2E,$04,$03
        .byte $21,$02,$02
        .byte $22,$02,$82
        .byte $FE
pat3
        .byte $10,$06,$02
        .byte $1C,$02,$82
        .byte $2E,$04,$03
        .byte $10,$04,$02
        .byte $10,$08,$82
        .byte $2E,$04,$03
        .byte $1A,$02,$02
        .byte $1C,$02,$82
        .byte $FE
pat4
        .byte $18,$06,$02
        .byte $24,$02,$82
        .byte $2E,$04,$03
        .byte $18,$04,$02
        .byte $18,$08,$82
        .byte $2E,$04,$03
        .byte $22,$02,$02
        .byte $24,$02,$82
        .byte $FE
pat5
        .byte $19,$06,$02
        .byte $25,$02,$82
        .byte $2E,$04,$03
        .byte $19,$04,$02
        .byte $19,$08,$82
        .byte $2E,$04,$03
        .byte $24,$02,$02
        .byte $25,$02,$82
        .byte $FE
pat6
        .byte $13,$06,$02
        .byte $1F,$02,$82
        .byte $2E,$04,$03
        .byte $13,$04,$02
        .byte $13,$08,$82
        .byte $2E,$04,$03
        .byte $1C,$02,$02
        .byte $1C,$02,$82
        .byte $FE
pat7
        .byte $32,$02,$03
        .byte $39,$02,$00
        .byte $39,$04,$80
        .byte $39,$04,$80
        .byte $39,$04,$80
        .byte $39,$08,$80
        .byte $39,$06,$80
        .byte $39,$04,$80
        .byte $40,$02,$80
        .byte $40,$04,$80
        .byte $40,$04,$80
        .byte $40,$04,$80
        .byte $40,$08,$80
        .byte $2C,$08,$0C
        .byte $41,$08,$00
        .byte $40,$08,$80
        .byte $41,$08,$80
        .byte $40,$08,$80
        .byte $40,$02,$C0
        .byte $3B,$02,$80
        .byte $3B,$04,$80
        .byte $3B,$04,$80
        .byte $3B,$04,$80
        .byte $3B,$08,$80
        .byte $2C,$08,$0C
        .byte $32,$02,$03
        .byte $3C,$02,$00
        .byte $3C,$04,$80
        .byte $3C,$04,$80
        .byte $3C,$04,$80
        .byte $3C,$08,$80
        .byte $3C,$06,$80
        .byte $3C,$04,$80
        .byte $43,$02,$80
        .byte $43,$04,$80
        .byte $43,$04,$80
        .byte $43,$04,$80
        .byte $43,$08,$80
        .byte $2C,$08,$0C
        .byte $44,$08,$00
        .byte $43,$08,$80
        .byte $44,$08,$80
        .byte $43,$08,$80
        .byte $43,$02,$C0
        .byte $3E,$02,$80
        .byte $3E,$04,$80
        .byte $3E,$04,$80
        .byte $3E,$04,$80
        .byte $3E,$08,$80
        .byte $2F,$04,$0C
        .byte $2C,$02,$8C
        .byte $2C,$02,$8C
        .byte $FE
pat8
        .byte $68,$02,$04
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $34,$04,$01
        .byte $34,$04,$81
        .byte $35,$06,$81
        .byte $34,$06,$81
        .byte $32,$04,$81
        .byte $68,$02,$04
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $34,$04,$01
        .byte $34,$04,$81
        .byte $34,$08,$81
        .byte $34,$08,$C1
        .byte $68,$02,$04
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $34,$04,$01
        .byte $34,$04,$81
        .byte $35,$06,$81
        .byte $34,$06,$81
        .byte $32,$04,$81
        .byte $32,$02,$C1
        .byte $34,$02,$01
        .byte $34,$04,$81
        .byte $34,$04,$81
        .byte $34,$04,$81
        .byte $34,$08,$81
        .byte $34,$08,$C1
        .byte $FE
pat9
        .byte $32,$04,$03
        .byte $32,$04,$83
        .byte $39,$04,$00
        .byte $39,$04,$80
        .byte $39,$02,$80
        .byte $39,$02,$80
        .byte $39,$04,$80
        .byte $3B,$04,$80
        .byte $3C,$04,$80
        .byte $3E,$02,$80
        .byte $3E,$02,$80
        .byte $3E,$04,$80
        .byte $3E,$04,$80
        .byte $3E,$04,$80
        .byte $3E,$08,$80
        .byte $2C,$04,$0C
        .byte $3E,$02,$00
        .byte $40,$02,$80
        .byte $41,$02,$80
        .byte $41,$02,$80
        .byte $40,$04,$80
        .byte $3E,$04,$80
        .byte $3C,$04,$80
        .byte $3B,$04,$80
        .byte $39,$04,$80
        .byte $38,$08,$80
        .byte $32,$02,$03
        .byte $39,$02,$00
        .byte $39,$04,$80
        .byte $39,$04,$80
        .byte $3B,$04,$80
        .byte $39,$08,$80
        .byte $2C,$08,$0C
        .byte $FE
pat10
        .byte $68,$02,$04
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $37,$04,$01
        .byte $37,$04,$81
        .byte $38,$06,$81
        .byte $37,$06,$81
        .byte $35,$04,$81
        .byte $68,$02,$04
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $37,$04,$01
        .byte $37,$04,$81
        .byte $37,$08,$81
        .byte $37,$08,$C1
        .byte $68,$02,$04
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $68,$02,$84
        .byte $37,$04,$01
        .byte $37,$04,$81
        .byte $38,$06,$81
        .byte $37,$06,$81
        .byte $35,$04,$81
        .byte $35,$02,$C1
        .byte $37,$02,$01
        .byte $37,$04,$81
        .byte $37,$04,$81
        .byte $37,$04,$81
        .byte $37,$08,$81
        .byte $37,$08,$C1
        .byte $FE
pat11
        .byte $1A,$06,$02
        .byte $26,$02,$82
        .byte $2E,$04,$03
        .byte $1A,$04,$02
        .byte $1A,$08,$82
        .byte $2E,$04,$03
        .byte $24,$02,$02
        .byte $26,$02,$82
        .byte $FE
pat12
        .byte $3C,$02,$05
        .byte $3B,$04,$85
        .byte $3A,$02,$85
        .byte $39,$04,$85
        .byte $3C,$02,$85
        .byte $3B,$04,$85
        .byte $3A,$02,$85
        .byte $39,$04,$85
        .byte $3C,$02,$85
        .byte $3B,$04,$85
        .byte $3A,$02,$85
        .byte $39,$04,$85
        .byte $3C,$02,$85
        .byte $3B,$04,$85
        .byte $3A,$02,$85
        .byte $39,$04,$85
        .byte $3C,$02,$85
        .byte $3B,$04,$85
        .byte $39,$02,$85
        .byte $41,$04,$85
        .byte $40,$04,$85
        .byte $41,$02,$85
        .byte $40,$04,$85
        .byte $3F,$02,$85
        .byte $3E,$04,$85
        .byte $41,$02,$85
        .byte $40,$04,$85
        .byte $3F,$02,$85
        .byte $3E,$04,$85
        .byte $41,$04,$85
        .byte $40,$04,$85
        .byte $3B,$02,$85
        .byte $3A,$04,$85
        .byte $39,$02,$85
        .byte $38,$04,$85
        .byte $3B,$02,$85
        .byte $3A,$04,$85
        .byte $39,$02,$85
        .byte $38,$04,$85
        .byte $3C,$04,$85
        .byte $3B,$04,$85
        .byte $FE
pat13
        .byte $12,$06,$02
        .byte $1E,$02,$82
        .byte $2E,$04,$03
        .byte $12,$04,$02
        .byte $12,$08,$82
        .byte $2E,$04,$03
        .byte $1C,$02,$02
        .byte $1E,$02,$82
        .byte $FE
pat14
        .byte $19,$06,$02
        .byte $25,$02,$82
        .byte $2E,$04,$03
        .byte $19,$04,$02
        .byte $19,$08,$82
        .byte $2E,$04,$03
        .byte $23,$02,$02
        .byte $25,$02,$82
        .byte $FE
pat15
        .byte $42,$0C,$06
        .byte $42,$04,$86
        .byte $40,$08,$86
        .byte $3D,$04,$86
        .byte $3B,$04,$86
        .byte $3B,$04,$86
        .byte $3A,$04,$86
        .byte $3A,$04,$86
        .byte $2C,$04,$0C
        .byte $2C,$04,$8C
        .byte $3A,$02,$06
        .byte $3A,$02,$86
        .byte $3B,$04,$86
        .byte $3D,$04,$86
        .byte $3D,$0C,$86
        .byte $3D,$04,$86
        .byte $40,$06,$86
        .byte $3D,$06,$86
        .byte $3B,$04,$86
        .byte $3D,$08,$86
        .byte $3D,$10,$86
        .byte $2C,$04,$0C
        .byte $2C,$04,$8C
        .byte $FE
pat16
        .byte $3C,$02,$06
        .byte $3B,$04,$86
        .byte $3A,$02,$86
        .byte $39,$04,$86
        .byte $3C,$02,$86
        .byte $3B,$04,$86
        .byte $3A,$02,$86
        .byte $39,$04,$86
        .byte $3C,$04,$86
        .byte $3E,$04,$86
        .byte $FE
pat17
        .byte $3E,$08,$06
        .byte $2C,$04,$0C
        .byte $3E,$02,$06
        .byte $3E,$02,$86
        .byte $40,$06,$86
        .byte $3E,$06,$86
        .byte $3C,$04,$86
        .byte $3E,$08,$86
        .byte $2F,$04,$0C
        .byte $2C,$0C,$8C
        .byte $2F,$04,$8C
        .byte $2C,$04,$8C
        .byte $FE
pat18
        .byte $40,$08,$06
        .byte $2C,$04,$0C
        .byte $40,$02,$06
        .byte $40,$02,$86
        .byte $42,$06,$86
        .byte $40,$06,$86
        .byte $3E,$04,$86
        .byte $40,$08,$86
        .byte $2F,$04,$0C
        .byte $2C,$0C,$8C
        .byte $2F,$04,$8C
        .byte $2C,$04,$8C
        .byte $40,$08,$06
        .byte $2C,$04,$0C
        .byte $40,$02,$06
        .byte $40,$02,$86
        .byte $42,$06,$86
        .byte $40,$06,$86
        .byte $3E,$04,$86
        .byte $40,$06,$86
        .byte $42,$06,$86
        .byte $44,$04,$86
        .byte $42,$06,$86
        .byte $44,$06,$86
        .byte $45,$04,$86
        .byte $FE
pat19
        .byte $58,$04,$07
        .byte $51,$04,$87
        .byte $39,$04,$01
        .byte $39,$04,$81
        .byte $39,$06,$81
        .byte $39,$06,$81
        .byte $37,$06,$81
        .byte $39,$02,$81
        .byte $39,$04,$81
        .byte $39,$04,$81
        .byte $37,$04,$81
        .byte $39,$02,$81
        .byte $37,$02,$81
        .byte $39,$04,$81
        .byte $58,$04,$07
        .byte $51,$04,$87
        .byte $FE
pat20
        .byte $55,$04,$07
        .byte $4E,$04,$87
        .byte $31,$04,$01
        .byte $31,$04,$81
        .byte $31,$06,$81
        .byte $31,$06,$81
        .byte $2F,$06,$81
        .byte $31,$02,$81
        .byte $31,$04,$81
        .byte $31,$04,$81
        .byte $2F,$04,$81
        .byte $31,$02,$81
        .byte $2F,$02,$81
        .byte $31,$04,$81
        .byte $55,$04,$07
        .byte $4E,$04,$87
        .byte $FE
pat21
        .byte $5D,$04,$07
        .byte $56,$04,$87
        .byte $32,$04,$01
        .byte $32,$04,$81
        .byte $32,$06,$81
        .byte $32,$06,$81
        .byte $30,$06,$81
        .byte $32,$02,$81
        .byte $32,$04,$81
        .byte $32,$04,$81
        .byte $30,$04,$81
        .byte $32,$02,$81
        .byte $30,$02,$81
        .byte $32,$04,$81
        .byte $5D,$04,$07
        .byte $56,$04,$87
        .byte $FE
pat22
        .byte $5F,$04,$07
        .byte $58,$04,$87
        .byte $34,$04,$01
        .byte $34,$04,$81
        .byte $34,$06,$81
        .byte $34,$06,$81
        .byte $32,$06,$81
        .byte $34,$02,$81
        .byte $34,$04,$81
        .byte $34,$04,$81
        .byte $32,$04,$81
        .byte $34,$02,$81
        .byte $32,$02,$81
        .byte $34,$04,$81
        .byte $5F,$04,$07
        .byte $58,$04,$87
        .byte $FE
pat23
        .byte $46,$02,$05
        .byte $46,$02,$85
        .byte $46,$02,$85
        .byte $46,$02,$85
        .byte $46,$02,$85
        .byte $46,$02,$85
        .byte $44,$02,$85
        .byte $46,$02,$85
        .byte $46,$02,$85
        .byte $44,$02,$85
        .byte $46,$04,$85
        .byte $46,$02,$85
        .byte $46,$02,$85
        .byte $44,$02,$85
        .byte $44,$02,$85
        .byte $FE
pat24
        .byte $43,$02,$05
        .byte $43,$02,$85
        .byte $43,$02,$85
        .byte $43,$02,$85
        .byte $43,$02,$85
        .byte $43,$02,$85
        .byte $41,$02,$85
        .byte $43,$02,$85
        .byte $43,$02,$85
        .byte $41,$02,$85
        .byte $43,$04,$85
        .byte $43,$02,$85
        .byte $43,$02,$85
        .byte $41,$02,$85
        .byte $41,$02,$85
        .byte $FE
pat25
        .byte $27,$02,$05
        .byte $27,$02,$85
        .byte $27,$02,$85
        .byte $27,$02,$85
        .byte $2C,$04,$0C
        .byte $25,$02,$05
        .byte $27,$04,$85
        .byte $25,$02,$85
        .byte $27,$02,$85
        .byte $27,$02,$85
        .byte $2F,$04,$0C
        .byte $2C,$04,$8C
        .byte $FE
pat26
        .byte $37,$08,$06
        .byte $37,$08,$86
        .byte $39,$18,$86
        .byte $37,$04,$86
        .byte $39,$04,$86
        .byte $3E,$04,$86
        .byte $3C,$04,$86
        .byte $39,$08,$86
        .byte $3C,$08,$86
        .byte $3C,$08,$86
        .byte $3E,$18,$86
        .byte $3E,$04,$86
        .byte $43,$04,$86
        .byte $42,$04,$86
        .byte $3E,$04,$86
        .byte $39,$08,$86
        .byte $37,$08,$86
        .byte $37,$08,$86
        .byte $39,$18,$86
        .byte $3F,$08,$86
        .byte $3E,$04,$86
        .byte $3C,$04,$86
        .byte $39,$08,$86
        .byte $3E,$08,$86
        .byte $3E,$08,$86
        .byte $3C,$18,$86
        .byte $3E,$04,$86
        .byte $40,$04,$86
        .byte $43,$04,$86
        .byte $42,$04,$86
        .byte $43,$04,$86
        .byte $45,$04,$86
        .byte $43,$08,$86
        .byte $43,$08,$86
        .byte $45,$08,$86
        .byte $45,$02,$86
        .byte $45,$04,$86
        .byte $45,$02,$86
        .byte $45,$02,$86
        .byte $45,$04,$86
        .byte $43,$02,$86
        .byte $45,$04,$86
        .byte $43,$02,$86
        .byte $42,$04,$86
        .byte $43,$02,$86
        .byte $42,$04,$86
        .byte $40,$04,$86
        .byte $3E,$04,$86
        .byte $3E,$02,$86
        .byte $3E,$04,$86
        .byte $3C,$02,$86
        .byte $3E,$04,$86
        .byte $3C,$02,$86
        .byte $3B,$04,$86
        .byte $3C,$02,$86
        .byte $3B,$04,$86
        .byte $39,$04,$86
        .byte $37,$04,$86
        .byte $39,$02,$86
        .byte $39,$04,$86
        .byte $37,$02,$86
        .byte $39,$04,$86
        .byte $3B,$02,$86
        .byte $3C,$04,$86
        .byte $3E,$02,$86
        .byte $40,$04,$86
        .byte $42,$04,$86
        .byte $43,$04,$86
        .byte $FE
pat27
        .byte $47,$08,$80
        .byte $47,$08,$80
        .byte $45,$18,$80
        .byte $43,$04,$80
        .byte $45,$04,$80
        .byte $48,$02,$80
        .byte $48,$02,$80
        .byte $45,$04,$80
        .byte $4A,$02,$80
        .byte $4A,$02,$80
        .byte $48,$04,$80
        .byte $4C,$08,$80
        .byte $4C,$08,$80
        .byte $4A,$20,$80
        .byte $4A,$02,$C0
        .byte $4C,$02,$80
        .byte $4C,$02,$80
        .byte $40,$02,$80
        .byte $4D,$02,$80
        .byte $40,$02,$80
        .byte $48,$02,$80
        .byte $4A,$02,$80
        .byte $FE
pat28
        .byte $4C,$02,$80
        .byte $4C,$02,$80
        .byte $40,$04,$80
        .byte $4A,$04,$80
        .byte $40,$02,$80
        .byte $48,$04,$80
        .byte $40,$02,$80
        .byte $47,$04,$80
        .byte $48,$02,$80
        .byte $40,$02,$80
        .byte $48,$02,$80
        .byte $4A,$02,$80
        .byte $FE
pat29
        .byte $4C,$02,$80
        .byte $4C,$02,$80
        .byte $40,$04,$80
        .byte $4B,$04,$80
        .byte $40,$02,$80
        .byte $49,$04,$80
        .byte $40,$02,$80
        .byte $47,$04,$80
        .byte $49,$02,$80
        .byte $40,$02,$80
        .byte $49,$02,$80
        .byte $4B,$02,$80
        .byte $FE
pat30
        .byte $49,$02,$80
        .byte $49,$02,$80
        .byte $3D,$04,$80
        .byte $47,$04,$80
        .byte $3D,$02,$80
        .byte $46,$04,$80
        .byte $3D,$02,$80
        .byte $44,$04,$80
        .byte $42,$02,$80
        .byte $3D,$02,$80
        .byte $47,$02,$80
        .byte $49,$02,$80
        .byte $FE
pat31
        .byte $68,$08,$07
        .byte $68,$10,$C7
        .byte $2C,$04,$0C
        .byte $2C,$04,$8C
        .byte $FE

v0ol
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat7,>pat7
        .byte <pat7,>pat7
        .byte <pat9,>pat9
        .byte <pat12,>pat12
        .byte <pat12,>pat12
        .byte <pat16,>pat16
        .byte <pat16,>pat16
        .byte <pat16,>pat16
        .byte <pat16,>pat16
        .byte <pat15,>pat15
        .byte <pat15,>pat15
        .byte <pat17,>pat17
        .byte <pat17,>pat17
        .byte <pat18,>pat18
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat16,>pat16
        .byte <pat16,>pat16
        .byte <pat16,>pat16
        .byte <pat16,>pat16
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat16,>pat16
        .byte <pat16,>pat16
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat26,>pat26
        .byte <pat27,>pat27
        .byte <pat28,>pat28
        .byte <pat28,>pat28
        .byte <pat28,>pat28
        .byte <pat28,>pat28
        .byte <pat29,>pat29
        .byte <pat29,>pat29
        .byte <pat29,>pat29
        .byte <pat29,>pat29
        .byte <pat30,>pat30
        .byte <pat30,>pat30
        .byte <pat30,>pat30
        .byte <pat30,>pat30
        .byte <pat15,>pat15
        .byte <pat23,>pat23
        .byte <pat23,>pat23
        .byte <pat31,>pat31
        .byte <pat16,>pat16
        .byte <pat16,>pat16
        .byte <pat23,>pat23
        .byte <pat17,>pat17
        .byte <pat23,>pat23
        .byte <pat18,>pat18
        .byte <pat23,>pat23
        .byte <pat31,>pat31
v1ol
        .byte <pat8,>pat8
        .byte <pat8,>pat8
        .byte <pat8,>pat8
        .byte <pat10,>pat10
        .byte <pat8,>pat8
        .byte <pat10,>pat10
        .byte <pat8,>pat8
        .byte <pat8,>pat8
        .byte <pat8,>pat8
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat20,>pat20
        .byte <pat20,>pat20
        .byte <pat20,>pat20
        .byte <pat20,>pat20
        .byte <pat21,>pat21
        .byte <pat21,>pat21
        .byte <pat22,>pat22
        .byte <pat22,>pat22
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat19,>pat19
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat19,>pat19
        .byte <pat20,>pat20
        .byte <pat20,>pat20
        .byte <pat20,>pat20
        .byte <pat20,>pat20
        .byte <pat20,>pat20
        .byte <pat20,>pat20
        .byte <pat24,>pat24
        .byte <pat24,>pat24
        .byte <pat31,>pat31
        .byte <pat19,>pat19
        .byte <pat24,>pat24
        .byte <pat21,>pat21
        .byte <pat24,>pat24
        .byte <pat22,>pat22
        .byte <pat22,>pat22
        .byte <pat24,>pat24
        .byte <pat31,>pat31
v2ol
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat2,>pat2
        .byte <pat3,>pat3
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat2,>pat2
        .byte <pat3,>pat3
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat2,>pat2
        .byte <pat3,>pat3
        .byte <pat4,>pat4
        .byte <pat4,>pat4
        .byte <pat5,>pat5
        .byte <pat6,>pat6
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat2,>pat2
        .byte <pat3,>pat3
        .byte <pat4,>pat4
        .byte <pat4,>pat4
        .byte <pat5,>pat5
        .byte <pat6,>pat6
        .byte <pat1,>pat1
        .byte <pat11,>pat11
        .byte <pat3,>pat3
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat2,>pat2
        .byte <pat3,>pat3
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat2,>pat2
        .byte <pat3,>pat3
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat13,>pat13
        .byte <pat13,>pat13
        .byte <pat14,>pat14
        .byte <pat14,>pat14
        .byte <pat13,>pat13
        .byte <pat13,>pat13
        .byte <pat14,>pat14
        .byte <pat14,>pat14
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat3,>pat3
        .byte <pat3,>pat3
        .byte <pat3,>pat3
        .byte <pat3,>pat3
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat1,>pat1
        .byte <pat11,>pat11
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat1,>pat1
        .byte <pat1,>pat1
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat13,>pat13
        .byte <pat13,>pat13
        .byte <pat14,>pat14
        .byte <pat14,>pat14
        .byte <pat13,>pat13
        .byte <pat13,>pat13
        .byte <pat14,>pat14
        .byte <pat14,>pat14
        .byte <pat13,>pat13
        .byte <pat13,>pat13
        .byte <pat14,>pat14
        .byte <pat14,>pat14
        .byte <pat25,>pat25
        .byte <pat25,>pat25
        .byte <pat31,>pat31
        .byte <pat1,>pat1
        .byte <pat11,>pat11
        .byte <pat25,>pat25
        .byte <pat11,>pat11
        .byte <pat11,>pat11
        .byte <pat25,>pat25
        .byte <pat3,>pat3
        .byte <pat3,>pat3
        .byte <pat3,>pat3
        .byte <pat3,>pat3
        .byte <pat25,>pat25
        .byte <pat31,>pat31
