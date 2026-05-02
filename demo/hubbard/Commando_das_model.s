        * = $1000
        jmp init
        jmp play

init
        lda #$0F
        sta $D418
        lda #$FF
        sta $BC
        lda #0
        sta $BD
        sta $BE
        sta $C3
        sta $C4
        sta $C5
        sta $C6
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
        sta $91
        sta $92
        sta $93
        sta $8E
        lda #1
        sta $80
        lda v1ol
        sta $97
        lda v1ol+1
        sta $98
        lda #<(v1ol+2)
        sta $95
        lda #>(v1ol+2)
        sta $96
        lda #0
        sta $99
        sta $9A
        sta $9B
        sta $9D
        sta $9E
        sta $9F
        sta $A0
        sta $A1
        sta $A3
        sta $A4
        sta $A5
        sta $A6
        sta $A7
        sta $A2
        lda #1
        sta $94
        lda v2ol
        sta $AB
        lda v2ol+1
        sta $AC
        lda #<(v2ol+2)
        sta $A9
        lda #>(v2ol+2)
        sta $AA
        lda #0
        sta $AD
        sta $AE
        sta $AF
        sta $B1
        sta $B2
        sta $B3
        sta $B4
        sta $B5
        sta $B7
        sta $B8
        sta $B9
        sta $BA
        sta $BB
        sta $B6
        lda #1
        sta $A8
        rts

play
        inc $BC
        lda $BD
        sta ftlo+104
        lda $BE
        sta fthi+104
        lda $A3
        sta ftlo+100
        lda $B7
        sta fthi+100
        lda $8D
        sta ftlo+116
        lda $A1
        sta fthi+116
; --- Voice 3 ---
        dec $A8
        beq v2rd
        jmp v2eval
v2rd
        ldy #0
        lda ($AB),y
        cmp #$FE
        bne v2nt
        lda #0
        sta $B7
        ldy #0
        lda ($A9),y
        sta $AB
        iny
        lda ($A9),y
        sta $AC
        clc
        lda $A9
        adc #2
        sta $A9
        bcc v2rd
        inc $AA
        jmp v2rd
v2nt
        sta $B0
        iny
        lda ($AB),y
        tax
        lda #0
v2mul  clc
        adc #3
        dex
        bne v2mul
        sta $A8
        sta $B1
        sec
        sbc #3
        sta $AE
        iny
        lda ($AB),y
        sta $BF
        and #$40
        bne v2hubt
        lda $BF
        bmi v2hub2
        and #$3F
        tax
        stx $B6
        lda $B7
        clc
        adc #3
        sta $B7
        jmp v2hubx
v2hub2
        ldx $B6
        lda $B7
        clc
        adc #2
        sta $B7
        jmp v2hubx
v2hubt
        ldx $B6
        lda $B7
        clc
        adc #1
        sta $B7
v2hubx
        lda $BF
        and #$40
        bne v2tie
        lda $B0
        tay
        lda fthi,y
        sta $D40F
        sta $B8
        lda ftlo,y
        sta $D40E
        sta $BA
        lda fthi,y
        sta $BB
        lda i_ctrl,x
        sta $C3
        sta $D412
        jmp v2pw0
v2tie
        lda i_ctrl,x
        sta $C3
        and #$FE
        sta $D412
v2pw0
        lda i_pwlo,x
        sta $D410
        sta $AF
        lda i_pwhi,x
        sta $D411
        sta $B3
        lda i_ad,x
        sta $D413
        lda i_sr,x
        sta $D414
        lda i_pws,x
        sta $B2
        lda i_pwmax,x
        sta $B4
        ldy #3
        lda ($AB),y
        sta $B9
        clc
        lda $AB
        adc #4
        sta $AB
        bcc v2nd1
        inc $AC
v2nd1
        ldy #0
        lda ($AB),y
        cmp #$FE
        bne v2npe
        lda #0
        sta $B7
        inc $C6
v2npe
        jmp v2done

v2eval
        lda $A8
        cmp #3
        bne v2efx
        lda $B9
        bmi v2efx
        ldy $B6
        lda i_ctrl,y
        and #$FE
        sta $D412
        lda #0
        sta $D413
        sta $D414
v2efx
        ldy $B6
        lda i_vib,y
        bne v2vibdo
        jmp v2drm
v2vibdo
        lda $B1
        cmp #21
        bcs v2vlong
        ldx $B0
        lda fthi,x
        sta $D40E
        lda ftlo,x
        sta $D40F
        jmp v2drm
v2vlong
        lda $BC
        and #$07
        cmp #4
        bcc v2vdok
        eor #$07
v2vdok
        tax
        ldy $B0
        lda fthi+1,y
        sec
        sbc fthi,y
        sta $BF
        lda ftlo+1,y
        sbc ftlo,y
        sta $C0
        lda $B6
        tay
        lda i_vib,y
        tay
        iny
v2vsr
        lsr $C0
        ror $BF
        dey
        bne v2vsr
        ldy $B0
        lda fthi,y
        sta $C1
        lda ftlo,y
        sta $C2
        cpx #0
        beq v2vwr
v2vmul
        clc
        lda $C1
        adc $C0
        sta $C1
        lda $C2
        adc $BF
        sta $C2
        dex
        bne v2vmul
v2vwr
        lda $C1
        sta $D40E
        lda $C2
        sta $D40F
v2drm
        lda $B9
        and #$7F
        beq v2bit0
        and #$01
        bne v2drmd
        lda $B9
        and #$7E
        sta $BF
        clc
        lda $BA
        adc $BF
        sta $BA
        sta $D40E
        lda $BB
        adc #0
        sta $BB
        sta $D40F
        jmp v2bit0
v2drmd
        lda $B9
        and #$7E
        sta $BF
        sec
        lda $BA
        sbc $BF
        sta $BA
        sta $D40E
        lda $BB
        sbc #0
        sta $BB
        sta $D40F
v2bit0
        ldy $B6
        lda i_bit0,y
        beq v2arpc
        lda $A8
        cmp #4
        bcc v2arpc
        lda $B8
        beq v2arpc
        lda $AE
        cmp $A8
        bcs v2bns
        lda $B8
        sta $D40F
        lda #$80
        sta $D412
        jmp v2arpc
v2bns
        lda $B8
        sta $D40F
        dec $B8
        lda i_ctrl,y
        and #$FE
        bne v2bcm
        lda $B8
        sta $D40F
        lda #$80
v2bcm
        sta $D412
v2arpc
        ldy $B6
        lda i_arp,y
        beq v2pw
        ldx $B0
        lda $BC
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
        lda $B4
        bne v2pwgo
        jmp v2done
v2pwgo
        cmp #$FF
        beq v2lin
        dec $AD
        bpl v2done
        lda $B2
        and #$1F
        sta $AD
        lda $B2
        and #$E0
        sta $BF
        ldy $B6
        lda i_pwlo,y
        sta $AF
        lda i_pwhi,y
        sta $B3
        lda $B5
        bne v2dn
        clc
        lda $AF
        adc $BF
        sta $AF
        bcc v2ncu
        inc $B3
        lda $B3
        and #$0F
        sta $B3
v2ncu
        lda $B3
        cmp $B4
        bne v2pwwr
        inc $B5
        jmp v2pwwr
v2dn
        sec
        lda $AF
        sbc $BF
        sta $AF
        bcs v2ncd
        dec $B3
        lda $B3
        and #$0F
        sta $B3
v2ncd
        lda $B3
        cmp #$08
        bne v2pwwr
        dec $B5
        jmp v2pwwr
v2lin
        ldy $B6
        lda i_pwlo,y
        clc
        adc $B2
        sta $AF
        sta $D410
        sta i_pwlo,y
        jmp v2done
v2pwwr
        lda $B3
        sta $D411
        lda $AF
        sta $D410
        lda $AF
        sta i_pwlo,y
        lda $B3
        sta i_pwhi,y
v2done

; --- Update T[98], T[99], T[105], T[106], T[107] before V2 (after V3) ---
        lda $C4
        sta ftlo+98
        lda $C5
        sta fthi+98
        lda $C6
        sta ftlo+99
        lda $8F
        sta fthi+99
        lda $C3
        sta ftlo+105
        lda $88
        sta fthi+105
        lda $9C
        sta ftlo+106
        lda $B0
        sta fthi+106
        lda $8E
        sta ftlo+107
        lda $A2
        sta fthi+107
; --- Voice 2 ---
        dec $94
        beq v1rd
        jmp v1eval
v1rd
        ldy #0
        lda ($97),y
        cmp #$FE
        bne v1nt
        lda #0
        sta $A3
        ldy #0
        lda ($95),y
        sta $97
        iny
        lda ($95),y
        sta $98
        clc
        lda $95
        adc #2
        sta $95
        bcc v1rd
        inc $96
        jmp v1rd
v1nt
        sta $9C
        iny
        lda ($97),y
        tax
        lda #0
v1mul  clc
        adc #3
        dex
        bne v1mul
        sta $94
        sta $9D
        sec
        sbc #3
        sta $9A
        iny
        lda ($97),y
        sta $BF
        and #$40
        bne v1hubt
        lda $BF
        bmi v1hub2
        and #$3F
        tax
        stx $A2
        lda $A3
        clc
        adc #3
        sta $A3
        jmp v1hubx
v1hub2
        ldx $A2
        lda $A3
        clc
        adc #2
        sta $A3
        jmp v1hubx
v1hubt
        ldx $A2
        lda $A3
        clc
        adc #1
        sta $A3
v1hubx
        lda $BF
        and #$40
        bne v1tie
        lda $9C
        tay
        lda fthi,y
        sta $D408
        sta $A4
        lda ftlo,y
        sta $D407
        sta $A6
        lda fthi,y
        sta $A7
        lda i_ctrl,x
        sta $BE
        sta $D40B
        jmp v1pw0
v1tie
        lda i_ctrl,x
        sta $BE
        and #$FE
        sta $D40B
v1pw0
        lda i_pwlo,x
        sta $D409
        sta $9B
        lda i_pwhi,x
        sta $D40A
        sta $9F
        lda i_ad,x
        sta $D40C
        lda i_sr,x
        sta $D40D
        lda i_pws,x
        sta $9E
        lda i_pwmax,x
        sta $A0
        ldy #3
        lda ($97),y
        sta $A5
        clc
        lda $97
        adc #4
        sta $97
        bcc v1nd1
        inc $98
v1nd1
        ldy #0
        lda ($97),y
        cmp #$FE
        bne v1npe
        lda #0
        sta $A3
        inc $C5
v1npe
        jmp v1done

v1eval
        lda $94
        cmp #3
        bne v1efx
        lda $A5
        bmi v1efx
        ldy $A2
        lda i_ctrl,y
        and #$FE
        sta $D40B
        lda #0
        sta $D40C
        sta $D40D
v1efx
        ldy $A2
        lda i_vib,y
        bne v1vibdo
        jmp v1drm
v1vibdo
        lda $9D
        cmp #21
        bcs v1vlong
        ldx $9C
        lda fthi,x
        sta $D407
        lda ftlo,x
        sta $D408
        jmp v1drm
v1vlong
        lda $BC
        and #$07
        cmp #4
        bcc v1vdok
        eor #$07
v1vdok
        tax
        ldy $9C
        lda fthi+1,y
        sec
        sbc fthi,y
        sta $BF
        lda ftlo+1,y
        sbc ftlo,y
        sta $C0
        lda $A2
        tay
        lda i_vib,y
        tay
        iny
v1vsr
        lsr $C0
        ror $BF
        dey
        bne v1vsr
        ldy $9C
        lda fthi,y
        sta $C1
        lda ftlo,y
        sta $C2
        cpx #0
        beq v1vwr
v1vmul
        clc
        lda $C1
        adc $C0
        sta $C1
        lda $C2
        adc $BF
        sta $C2
        dex
        bne v1vmul
v1vwr
        lda $C1
        sta $D407
        lda $C2
        sta $D408
v1drm
        lda $A5
        and #$7F
        beq v1bit0
        and #$01
        bne v1drmd
        lda $A5
        and #$7E
        sta $BF
        clc
        lda $A6
        adc $BF
        sta $A6
        sta $D407
        lda $A7
        adc #0
        sta $A7
        sta $D408
        jmp v1bit0
v1drmd
        lda $A5
        and #$7E
        sta $BF
        sec
        lda $A6
        sbc $BF
        sta $A6
        sta $D407
        lda $A7
        sbc #0
        sta $A7
        sta $D408
v1bit0
        ldy $A2
        lda i_bit0,y
        beq v1arpc
        lda $94
        cmp #4
        bcc v1arpc
        lda $A4
        beq v1arpc
        lda $9A
        cmp $94
        bcs v1bns
        lda $A4
        sta $D408
        lda #$80
        sta $D40B
        jmp v1arpc
v1bns
        lda $A4
        sta $D408
        dec $A4
        lda i_ctrl,y
        and #$FE
        bne v1bcm
        lda $A4
        sta $D408
        lda #$80
v1bcm
        sta $D40B
v1arpc
        ldy $A2
        lda i_arp,y
        beq v1pw
        ldx $9C
        lda $BC
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
        lda $A0
        bne v1pwgo
        jmp v1done
v1pwgo
        cmp #$FF
        beq v1lin
        dec $99
        bpl v1done
        lda $9E
        and #$1F
        sta $99
        lda $9E
        and #$E0
        sta $BF
        ldy $A2
        lda i_pwlo,y
        sta $9B
        lda i_pwhi,y
        sta $9F
        lda $A1
        bne v1dn
        clc
        lda $9B
        adc $BF
        sta $9B
        bcc v1ncu
        inc $9F
        lda $9F
        and #$0F
        sta $9F
v1ncu
        lda $9F
        cmp $A0
        bne v1pwwr
        inc $A1
        jmp v1pwwr
v1dn
        sec
        lda $9B
        sbc $BF
        sta $9B
        bcs v1ncd
        dec $9F
        lda $9F
        and #$0F
        sta $9F
v1ncd
        lda $9F
        cmp #$08
        bne v1pwwr
        dec $A1
        jmp v1pwwr
v1lin
        ldy $A2
        lda i_pwlo,y
        clc
        adc $9E
        sta $9B
        sta $D409
        sta i_pwlo,y
        jmp v1done
v1pwwr
        lda $9F
        sta $D40A
        lda $9B
        sta $D409
        lda $9B
        sta i_pwlo,y
        lda $9F
        sta i_pwhi,y
v1done

; --- Update T[100] and T[104] before V1 ---
        lda $A3
        sta ftlo+100
        lda $B7
        sta fthi+100
        lda $BD
        sta ftlo+104
        lda $BE
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
        sta $BF
        and #$40
        bne v0hubt
        lda $BF
        bmi v0hub2
        and #$3F
        tax
        stx $8E
        lda $8F
        clc
        adc #3
        sta $8F
        jmp v0hubx
v0hub2
        ldx $8E
        lda $8F
        clc
        adc #2
        sta $8F
        jmp v0hubx
v0hubt
        ldx $8E
        lda $8F
        clc
        adc #1
        sta $8F
v0hubx
        lda $BF
        and #$40
        bne v0tie
        lda $88
        tay
        lda fthi,y
        sta $D401
        sta $90
        lda ftlo,y
        sta $D400
        sta $92
        lda fthi,y
        sta $93
        lda i_ctrl,x
        sta $BD
        sta $D404
        jmp v0pw0
v0tie
        lda i_ctrl,x
        sta $BD
        and #$FE
        sta $D404
v0pw0
        lda i_pwlo,x
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
        ldy #3
        lda ($83),y
        sta $91
        clc
        lda $83
        adc #4
        sta $83
        bcc v0nd1
        inc $84
v0nd1
        ldy #0
        lda ($83),y
        cmp #$FE
        bne v0npe
        lda #0
        sta $8F
        inc $C4
v0npe
        jmp v0done

v0eval
        lda $80
        cmp #3
        bne v0efx
        lda $91
        bmi v0efx
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
        bne v0vibdo
        jmp v0drm
v0vibdo
        lda $89
        cmp #21
        bcs v0vlong
        ldx $88
        lda fthi,x
        sta $D400
        lda ftlo,x
        sta $D401
        jmp v0drm
v0vlong
        lda $BC
        and #$07
        cmp #4
        bcc v0vdok
        eor #$07
v0vdok
        tax
        ldy $88
        lda fthi+1,y
        sec
        sbc fthi,y
        sta $BF
        lda ftlo+1,y
        sbc ftlo,y
        sta $C0
        lda $8E
        tay
        lda i_vib,y
        tay
        iny
v0vsr
        lsr $C0
        ror $BF
        dey
        bne v0vsr
        ldy $88
        lda fthi,y
        sta $C1
        lda ftlo,y
        sta $C2
        cpx #0
        beq v0vwr
v0vmul
        clc
        lda $C1
        adc $C0
        sta $C1
        lda $C2
        adc $BF
        sta $C2
        dex
        bne v0vmul
v0vwr
        lda $C1
        sta $D400
        lda $C2
        sta $D401
v0drm
        lda $91
        and #$7F
        beq v0bit0
        and #$01
        bne v0drmd
        lda $91
        and #$7E
        sta $BF
        clc
        lda $92
        adc $BF
        sta $92
        sta $D400
        lda $93
        adc #0
        sta $93
        sta $D401
        jmp v0bit0
v0drmd
        lda $91
        and #$7E
        sta $BF
        sec
        lda $92
        sbc $BF
        sta $92
        sta $D400
        lda $93
        sbc #0
        sta $93
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
        lda $BC
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
        bne v0pwgo
        jmp v0done
v0pwgo
        cmp #$FF
        beq v0lin
        dec $85
        bpl v0done
        lda $8A
        and #$1F
        sta $85
        lda $8A
        and #$E0
        sta $BF
        ldy $8E
        lda i_pwlo,y
        sta $87
        lda i_pwhi,y
        sta $8B
        lda $8D
        bne v0dn
        clc
        lda $87
        adc $BF
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
        sbc $BF
        sta $87
        bcs v0ncd
        dec $8B
        lda $8B
        and #$0F
        sta $8B
v0ncd
        lda $8B
        cmp #$08
        bne v0pwwr
        dec $8D
        jmp v0pwwr
v0lin
        ldy $8E
        lda i_pwlo,y
        clc
        adc $8A
        sta $87
        sta $D402
        sta i_pwlo,y
        jmp v0done
v0pwwr
        lda $8B
        sta $D403
        lda $87
        sta $D402
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

pat1
        .byte $15,$06,$02,$00
        .byte $21,$02,$82,$00
        .byte $2E,$04,$03,$00
        .byte $15,$04,$02,$00
        .byte $15,$08,$82,$00
        .byte $2E,$04,$03,$00
        .byte $1F,$02,$02,$00
        .byte $21,$02,$82,$00
        .byte $FE
pat2
        .byte $16,$06,$02,$00
        .byte $22,$02,$82,$00
        .byte $2E,$04,$03,$00
        .byte $16,$04,$02,$00
        .byte $16,$08,$82,$00
        .byte $2E,$04,$03,$00
        .byte $21,$02,$02,$00
        .byte $22,$02,$82,$00
        .byte $FE
pat3
        .byte $10,$06,$02,$00
        .byte $1C,$02,$82,$00
        .byte $2E,$04,$03,$00
        .byte $10,$04,$02,$00
        .byte $10,$08,$82,$00
        .byte $2E,$04,$03,$00
        .byte $1A,$02,$02,$00
        .byte $1C,$02,$82,$00
        .byte $FE
pat4
        .byte $18,$06,$02,$00
        .byte $24,$02,$82,$00
        .byte $2E,$04,$03,$00
        .byte $18,$04,$02,$00
        .byte $18,$08,$82,$00
        .byte $2E,$04,$03,$00
        .byte $22,$02,$02,$00
        .byte $24,$02,$82,$00
        .byte $FE
pat5
        .byte $19,$06,$02,$00
        .byte $25,$02,$82,$00
        .byte $2E,$04,$03,$00
        .byte $19,$04,$02,$00
        .byte $19,$08,$82,$00
        .byte $2E,$04,$03,$00
        .byte $24,$02,$02,$00
        .byte $25,$02,$82,$00
        .byte $FE
pat6
        .byte $13,$06,$02,$00
        .byte $1F,$02,$82,$00
        .byte $2E,$04,$03,$00
        .byte $13,$04,$02,$00
        .byte $13,$08,$82,$00
        .byte $2E,$04,$03,$00
        .byte $1C,$02,$02,$00
        .byte $1C,$02,$82,$00
        .byte $FE
pat7
        .byte $32,$02,$03,$00
        .byte $39,$02,$00,$00
        .byte $39,$04,$80,$00
        .byte $39,$04,$80,$00
        .byte $39,$04,$80,$00
        .byte $39,$08,$80,$00
        .byte $39,$06,$80,$00
        .byte $39,$04,$80,$00
        .byte $40,$02,$80,$00
        .byte $40,$04,$80,$00
        .byte $40,$04,$80,$00
        .byte $40,$04,$80,$00
        .byte $40,$08,$80,$00
        .byte $2C,$08,$0C,$00
        .byte $41,$08,$00,$00
        .byte $40,$08,$80,$00
        .byte $41,$08,$80,$00
        .byte $40,$08,$80,$00
        .byte $40,$02,$C0,$00
        .byte $3B,$02,$80,$00
        .byte $3B,$04,$80,$00
        .byte $3B,$04,$80,$00
        .byte $3B,$04,$80,$00
        .byte $3B,$08,$80,$00
        .byte $2C,$08,$0C,$00
        .byte $32,$02,$03,$00
        .byte $3C,$02,$00,$00
        .byte $3C,$04,$80,$00
        .byte $3C,$04,$80,$00
        .byte $3C,$04,$80,$00
        .byte $3C,$08,$80,$00
        .byte $3C,$06,$80,$00
        .byte $3C,$04,$80,$00
        .byte $43,$02,$80,$00
        .byte $43,$04,$80,$00
        .byte $43,$04,$80,$00
        .byte $43,$04,$80,$00
        .byte $43,$08,$80,$00
        .byte $2C,$08,$0C,$00
        .byte $44,$08,$00,$00
        .byte $43,$08,$80,$00
        .byte $44,$08,$80,$00
        .byte $43,$08,$80,$00
        .byte $43,$02,$C0,$00
        .byte $3E,$02,$80,$00
        .byte $3E,$04,$80,$00
        .byte $3E,$04,$80,$00
        .byte $3E,$04,$80,$00
        .byte $3E,$08,$80,$00
        .byte $2F,$04,$0C,$00
        .byte $2C,$02,$8C,$00
        .byte $2C,$02,$8C,$00
        .byte $FE
pat8
        .byte $68,$02,$04,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $34,$04,$01,$00
        .byte $34,$04,$81,$00
        .byte $35,$06,$81,$00
        .byte $34,$06,$81,$00
        .byte $32,$04,$81,$00
        .byte $68,$02,$04,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $34,$04,$01,$00
        .byte $34,$04,$81,$00
        .byte $34,$08,$81,$00
        .byte $34,$08,$C1,$00
        .byte $68,$02,$04,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $34,$04,$01,$00
        .byte $34,$04,$81,$00
        .byte $35,$06,$81,$00
        .byte $34,$06,$81,$00
        .byte $32,$04,$81,$00
        .byte $32,$02,$C1,$00
        .byte $34,$02,$01,$00
        .byte $34,$04,$81,$00
        .byte $34,$04,$81,$00
        .byte $34,$04,$81,$00
        .byte $34,$08,$81,$00
        .byte $34,$08,$C1,$00
        .byte $FE
pat9
        .byte $32,$04,$03,$00
        .byte $32,$04,$83,$00
        .byte $39,$04,$00,$00
        .byte $39,$04,$80,$00
        .byte $39,$02,$80,$00
        .byte $39,$02,$80,$00
        .byte $39,$04,$80,$00
        .byte $3B,$04,$80,$00
        .byte $3C,$04,$80,$00
        .byte $3E,$02,$80,$00
        .byte $3E,$02,$80,$00
        .byte $3E,$04,$80,$00
        .byte $3E,$04,$80,$00
        .byte $3E,$04,$80,$00
        .byte $3E,$08,$80,$00
        .byte $2C,$04,$0C,$00
        .byte $3E,$02,$00,$00
        .byte $40,$02,$80,$00
        .byte $41,$02,$80,$00
        .byte $41,$02,$80,$00
        .byte $40,$04,$80,$00
        .byte $3E,$04,$80,$00
        .byte $3C,$04,$80,$00
        .byte $3B,$04,$80,$00
        .byte $39,$04,$80,$00
        .byte $38,$08,$80,$00
        .byte $32,$02,$03,$00
        .byte $39,$02,$00,$00
        .byte $39,$04,$80,$00
        .byte $39,$04,$80,$00
        .byte $3B,$04,$80,$00
        .byte $39,$08,$80,$00
        .byte $2C,$08,$0C,$00
        .byte $FE
pat10
        .byte $68,$02,$04,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $37,$04,$01,$00
        .byte $37,$04,$81,$00
        .byte $38,$06,$81,$00
        .byte $37,$06,$81,$00
        .byte $35,$04,$81,$00
        .byte $68,$02,$04,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $37,$04,$01,$00
        .byte $37,$04,$81,$00
        .byte $37,$08,$81,$00
        .byte $37,$08,$C1,$00
        .byte $68,$02,$04,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $68,$02,$84,$00
        .byte $37,$04,$01,$00
        .byte $37,$04,$81,$00
        .byte $38,$06,$81,$00
        .byte $37,$06,$81,$00
        .byte $35,$04,$81,$00
        .byte $35,$02,$C1,$00
        .byte $37,$02,$01,$00
        .byte $37,$04,$81,$00
        .byte $37,$04,$81,$00
        .byte $37,$04,$81,$00
        .byte $37,$08,$81,$00
        .byte $37,$08,$C1,$00
        .byte $FE
pat11
        .byte $1A,$06,$02,$00
        .byte $26,$02,$82,$00
        .byte $2E,$04,$03,$00
        .byte $1A,$04,$02,$00
        .byte $1A,$08,$82,$00
        .byte $2E,$04,$03,$00
        .byte $24,$02,$02,$00
        .byte $26,$02,$82,$00
        .byte $FE
pat12
        .byte $3C,$02,$05,$00
        .byte $3B,$04,$85,$00
        .byte $3A,$02,$85,$00
        .byte $39,$04,$85,$00
        .byte $3C,$02,$85,$00
        .byte $3B,$04,$85,$00
        .byte $3A,$02,$85,$00
        .byte $39,$04,$85,$00
        .byte $3C,$02,$85,$00
        .byte $3B,$04,$85,$00
        .byte $3A,$02,$85,$00
        .byte $39,$04,$85,$00
        .byte $3C,$02,$85,$00
        .byte $3B,$04,$85,$00
        .byte $3A,$02,$85,$00
        .byte $39,$04,$85,$00
        .byte $3C,$02,$85,$00
        .byte $3B,$04,$85,$00
        .byte $39,$02,$85,$00
        .byte $41,$04,$85,$00
        .byte $40,$04,$85,$00
        .byte $41,$02,$85,$00
        .byte $40,$04,$85,$00
        .byte $3F,$02,$85,$00
        .byte $3E,$04,$85,$00
        .byte $41,$02,$85,$00
        .byte $40,$04,$85,$00
        .byte $3F,$02,$85,$00
        .byte $3E,$04,$85,$00
        .byte $41,$04,$85,$00
        .byte $40,$04,$85,$00
        .byte $3B,$02,$85,$00
        .byte $3A,$04,$85,$00
        .byte $39,$02,$85,$00
        .byte $38,$04,$85,$00
        .byte $3B,$02,$85,$00
        .byte $3A,$04,$85,$00
        .byte $39,$02,$85,$00
        .byte $38,$04,$85,$00
        .byte $3C,$04,$85,$00
        .byte $3B,$04,$85,$00
        .byte $FE
pat13
        .byte $12,$06,$02,$00
        .byte $1E,$02,$82,$00
        .byte $2E,$04,$03,$00
        .byte $12,$04,$02,$00
        .byte $12,$08,$82,$00
        .byte $2E,$04,$03,$00
        .byte $1C,$02,$02,$00
        .byte $1E,$02,$82,$00
        .byte $FE
pat14
        .byte $19,$06,$02,$00
        .byte $25,$02,$82,$00
        .byte $2E,$04,$03,$00
        .byte $19,$04,$02,$00
        .byte $19,$08,$82,$00
        .byte $2E,$04,$03,$00
        .byte $23,$02,$02,$00
        .byte $25,$02,$82,$00
        .byte $FE
pat15
        .byte $42,$0C,$06,$00
        .byte $42,$04,$86,$CF
        .byte $40,$08,$86,$00
        .byte $3D,$04,$86,$00
        .byte $3B,$04,$86,$00
        .byte $3B,$04,$86,$BF
        .byte $3A,$04,$86,$00
        .byte $3A,$04,$86,$00
        .byte $2C,$04,$0C,$00
        .byte $2C,$04,$8C,$00
        .byte $3A,$02,$06,$00
        .byte $3A,$02,$86,$00
        .byte $3B,$04,$86,$00
        .byte $3D,$04,$86,$00
        .byte $3D,$0C,$86,$00
        .byte $3D,$04,$86,$00
        .byte $40,$06,$86,$00
        .byte $3D,$06,$86,$00
        .byte $3B,$04,$86,$A8
        .byte $3D,$08,$86,$00
        .byte $3D,$10,$86,$51
        .byte $2C,$04,$0C,$00
        .byte $2C,$04,$8C,$00
        .byte $FE
pat16
        .byte $3C,$02,$06,$00
        .byte $3B,$04,$86,$00
        .byte $3A,$02,$86,$00
        .byte $39,$04,$86,$00
        .byte $3C,$02,$86,$00
        .byte $3B,$04,$86,$00
        .byte $3A,$02,$86,$00
        .byte $39,$04,$86,$00
        .byte $3C,$04,$86,$00
        .byte $3E,$04,$86,$00
        .byte $FE
pat17
        .byte $3E,$08,$06,$00
        .byte $2C,$04,$0C,$00
        .byte $3E,$02,$06,$00
        .byte $3E,$02,$86,$00
        .byte $40,$06,$86,$00
        .byte $3E,$06,$86,$00
        .byte $3C,$04,$86,$A8
        .byte $3E,$08,$86,$00
        .byte $2F,$04,$0C,$00
        .byte $2C,$0C,$8C,$00
        .byte $2F,$04,$8C,$00
        .byte $2C,$04,$8C,$00
        .byte $FE
pat18
        .byte $40,$08,$06,$00
        .byte $2C,$04,$0C,$00
        .byte $40,$02,$06,$00
        .byte $40,$02,$86,$00
        .byte $42,$06,$86,$00
        .byte $40,$06,$86,$00
        .byte $3E,$04,$86,$A8
        .byte $40,$08,$86,$00
        .byte $2F,$04,$0C,$00
        .byte $2C,$0C,$8C,$00
        .byte $2F,$04,$8C,$00
        .byte $2C,$04,$8C,$00
        .byte $40,$08,$06,$00
        .byte $2C,$04,$0C,$00
        .byte $40,$02,$06,$00
        .byte $40,$02,$86,$00
        .byte $42,$06,$86,$00
        .byte $40,$06,$86,$00
        .byte $3E,$04,$86,$A8
        .byte $40,$06,$86,$00
        .byte $42,$06,$86,$00
        .byte $44,$04,$86,$00
        .byte $42,$06,$86,$00
        .byte $44,$06,$86,$00
        .byte $45,$04,$86,$00
        .byte $FE
pat19
        .byte $58,$04,$07,$00
        .byte $51,$04,$87,$00
        .byte $39,$04,$01,$00
        .byte $39,$04,$81,$00
        .byte $39,$06,$81,$00
        .byte $39,$06,$81,$00
        .byte $37,$06,$81,$00
        .byte $39,$02,$81,$00
        .byte $39,$04,$81,$00
        .byte $39,$04,$81,$00
        .byte $37,$04,$81,$00
        .byte $39,$02,$81,$00
        .byte $37,$02,$81,$00
        .byte $39,$04,$81,$00
        .byte $58,$04,$07,$00
        .byte $51,$04,$87,$00
        .byte $FE
pat20
        .byte $55,$04,$07,$00
        .byte $4E,$04,$87,$00
        .byte $31,$04,$01,$00
        .byte $31,$04,$81,$00
        .byte $31,$06,$81,$00
        .byte $31,$06,$81,$00
        .byte $2F,$06,$81,$00
        .byte $31,$02,$81,$00
        .byte $31,$04,$81,$00
        .byte $31,$04,$81,$00
        .byte $2F,$04,$81,$00
        .byte $31,$02,$81,$00
        .byte $2F,$02,$81,$00
        .byte $31,$04,$81,$00
        .byte $55,$04,$07,$00
        .byte $4E,$04,$87,$00
        .byte $FE
pat21
        .byte $5D,$04,$07,$00
        .byte $56,$04,$87,$00
        .byte $32,$04,$01,$00
        .byte $32,$04,$81,$00
        .byte $32,$06,$81,$00
        .byte $32,$06,$81,$00
        .byte $30,$06,$81,$00
        .byte $32,$02,$81,$00
        .byte $32,$04,$81,$00
        .byte $32,$04,$81,$00
        .byte $30,$04,$81,$00
        .byte $32,$02,$81,$00
        .byte $30,$02,$81,$00
        .byte $32,$04,$81,$00
        .byte $5D,$04,$07,$00
        .byte $56,$04,$87,$00
        .byte $FE
pat22
        .byte $5F,$04,$07,$00
        .byte $58,$04,$87,$00
        .byte $34,$04,$01,$00
        .byte $34,$04,$81,$00
        .byte $34,$06,$81,$00
        .byte $34,$06,$81,$00
        .byte $32,$06,$81,$00
        .byte $34,$02,$81,$00
        .byte $34,$04,$81,$00
        .byte $34,$04,$81,$00
        .byte $32,$04,$81,$00
        .byte $34,$02,$81,$00
        .byte $32,$02,$81,$00
        .byte $34,$04,$81,$00
        .byte $5F,$04,$07,$00
        .byte $58,$04,$87,$00
        .byte $FE
pat23
        .byte $46,$02,$05,$00
        .byte $46,$02,$85,$00
        .byte $46,$02,$85,$00
        .byte $46,$02,$85,$00
        .byte $46,$02,$85,$00
        .byte $46,$02,$85,$00
        .byte $44,$02,$85,$00
        .byte $46,$02,$85,$00
        .byte $46,$02,$85,$00
        .byte $44,$02,$85,$00
        .byte $46,$04,$85,$00
        .byte $46,$02,$85,$00
        .byte $46,$02,$85,$00
        .byte $44,$02,$85,$00
        .byte $44,$02,$85,$00
        .byte $FE
pat24
        .byte $43,$02,$05,$00
        .byte $43,$02,$85,$00
        .byte $43,$02,$85,$00
        .byte $43,$02,$85,$00
        .byte $43,$02,$85,$00
        .byte $43,$02,$85,$00
        .byte $41,$02,$85,$00
        .byte $43,$02,$85,$00
        .byte $43,$02,$85,$00
        .byte $41,$02,$85,$00
        .byte $43,$04,$85,$00
        .byte $43,$02,$85,$00
        .byte $43,$02,$85,$00
        .byte $41,$02,$85,$00
        .byte $41,$02,$85,$00
        .byte $FE
pat25
        .byte $27,$02,$05,$00
        .byte $27,$02,$85,$00
        .byte $27,$02,$85,$00
        .byte $27,$02,$85,$00
        .byte $2C,$04,$0C,$00
        .byte $25,$02,$05,$00
        .byte $27,$04,$85,$00
        .byte $25,$02,$85,$00
        .byte $27,$02,$85,$00
        .byte $27,$02,$85,$00
        .byte $2F,$04,$0C,$00
        .byte $2C,$04,$8C,$00
        .byte $FE
pat26
        .byte $37,$08,$06,$80
        .byte $37,$08,$86,$A8
        .byte $39,$18,$86,$00
        .byte $37,$04,$86,$00
        .byte $39,$04,$86,$00
        .byte $3E,$04,$86,$00
        .byte $3C,$04,$86,$00
        .byte $39,$08,$86,$00
        .byte $3C,$08,$86,$80
        .byte $3C,$08,$86,$AA
        .byte $3E,$18,$86,$00
        .byte $3E,$04,$86,$00
        .byte $43,$04,$86,$00
        .byte $42,$04,$86,$00
        .byte $3E,$04,$86,$00
        .byte $39,$08,$86,$00
        .byte $37,$08,$86,$80
        .byte $37,$08,$86,$90
        .byte $39,$18,$86,$00
        .byte $3F,$08,$86,$A9
        .byte $3E,$04,$86,$00
        .byte $3C,$04,$86,$00
        .byte $39,$08,$86,$00
        .byte $3E,$08,$86,$80
        .byte $3E,$08,$86,$A9
        .byte $3C,$18,$86,$00
        .byte $3E,$04,$86,$00
        .byte $40,$04,$86,$00
        .byte $43,$04,$86,$00
        .byte $42,$04,$86,$00
        .byte $43,$04,$86,$00
        .byte $45,$04,$86,$00
        .byte $43,$08,$86,$80
        .byte $43,$08,$86,$B4
        .byte $45,$08,$86,$00
        .byte $45,$02,$86,$00
        .byte $45,$04,$86,$00
        .byte $45,$02,$86,$00
        .byte $45,$02,$86,$00
        .byte $45,$04,$86,$00
        .byte $43,$02,$86,$00
        .byte $45,$04,$86,$00
        .byte $43,$02,$86,$00
        .byte $42,$04,$86,$00
        .byte $43,$02,$86,$00
        .byte $42,$04,$86,$00
        .byte $40,$04,$86,$00
        .byte $3E,$04,$86,$00
        .byte $3E,$02,$86,$00
        .byte $3E,$04,$86,$00
        .byte $3C,$02,$86,$00
        .byte $3E,$04,$86,$00
        .byte $3C,$02,$86,$00
        .byte $3B,$04,$86,$00
        .byte $3C,$02,$86,$00
        .byte $3B,$04,$86,$00
        .byte $39,$04,$86,$00
        .byte $37,$04,$86,$00
        .byte $39,$02,$86,$00
        .byte $39,$04,$86,$00
        .byte $37,$02,$86,$00
        .byte $39,$04,$86,$00
        .byte $3B,$02,$86,$00
        .byte $3C,$04,$86,$00
        .byte $3E,$02,$86,$00
        .byte $40,$04,$86,$00
        .byte $42,$04,$86,$00
        .byte $43,$04,$86,$00
        .byte $FE
pat27
        .byte $47,$08,$80,$80
        .byte $47,$08,$80,$B1
        .byte $45,$18,$80,$00
        .byte $43,$04,$80,$00
        .byte $45,$04,$80,$00
        .byte $48,$02,$80,$00
        .byte $48,$02,$80,$00
        .byte $45,$04,$80,$00
        .byte $4A,$02,$80,$00
        .byte $4A,$02,$80,$00
        .byte $48,$04,$80,$00
        .byte $4C,$08,$80,$80
        .byte $4C,$08,$80,$D1
        .byte $4A,$20,$80,$00
        .byte $4A,$02,$C0,$00
        .byte $4C,$02,$80,$00
        .byte $4C,$02,$80,$00
        .byte $40,$02,$80,$00
        .byte $4D,$02,$80,$00
        .byte $40,$02,$80,$00
        .byte $48,$02,$80,$00
        .byte $4A,$02,$80,$00
        .byte $FE
pat28
        .byte $4C,$02,$80,$00
        .byte $4C,$02,$80,$00
        .byte $40,$04,$80,$00
        .byte $4A,$04,$80,$00
        .byte $40,$02,$80,$00
        .byte $48,$04,$80,$00
        .byte $40,$02,$80,$00
        .byte $47,$04,$80,$00
        .byte $48,$02,$80,$00
        .byte $40,$02,$80,$00
        .byte $48,$02,$80,$00
        .byte $4A,$02,$80,$00
        .byte $FE
pat29
        .byte $4C,$02,$80,$00
        .byte $4C,$02,$80,$00
        .byte $40,$04,$80,$00
        .byte $4B,$04,$80,$00
        .byte $40,$02,$80,$00
        .byte $49,$04,$80,$00
        .byte $40,$02,$80,$00
        .byte $47,$04,$80,$00
        .byte $49,$02,$80,$00
        .byte $40,$02,$80,$00
        .byte $49,$02,$80,$00
        .byte $4B,$02,$80,$00
        .byte $FE
pat30
        .byte $49,$02,$80,$00
        .byte $49,$02,$80,$00
        .byte $3D,$04,$80,$00
        .byte $47,$04,$80,$00
        .byte $3D,$02,$80,$00
        .byte $46,$04,$80,$00
        .byte $3D,$02,$80,$00
        .byte $44,$04,$80,$00
        .byte $42,$02,$80,$00
        .byte $3D,$02,$80,$00
        .byte $47,$02,$80,$00
        .byte $49,$02,$80,$00
        .byte $FE
pat31
        .byte $68,$08,$07,$00
        .byte $68,$10,$C7,$00
        .byte $2C,$04,$0C,$00
        .byte $2C,$04,$8C,$00
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
