        * = $1000
        jmp init
        jmp play

init
        lda #$0F
        sta $D418
        lda #$FF
        sta $B0
        lda v0ol
        sta $83
        lda v0ol+1
        sta $84
        lda #<(v0ol+2)
        sta $81
        lda #>(v0ol+2)
        sta $82
        lda #0
        sta $87
        sta $89
        sta $8A
        sta $8B
        sta $8C
        sta $8D
        sta $8F
        lda #$FF
        sta $8E
        lda #1
        sta $80
        lda v1ol
        sta $93
        lda v1ol+1
        sta $94
        lda #<(v1ol+2)
        sta $91
        lda #>(v1ol+2)
        sta $92
        lda #0
        sta $97
        sta $99
        sta $9A
        sta $9B
        sta $9C
        sta $9D
        sta $9F
        lda #$FF
        sta $9E
        lda #1
        sta $90
        lda v2ol
        sta $A3
        lda v2ol+1
        sta $A4
        lda #<(v2ol+2)
        sta $A1
        lda #>(v2ol+2)
        sta $A2
        lda #0
        sta $A7
        sta $A9
        sta $AA
        sta $AB
        sta $AC
        sta $AD
        sta $AF
        lda #$FF
        sta $AE
        lda #1
        sta $A0
        rts

play
        inc $B0
        lda $9F
        sta ftlo+100
        lda $AF
        sta fthi+100
; --- Voice 3 ---
        dec $A0
        beq v2rd
        jmp v2eval
v2rd
        ldy #0
        lda ($A3),y
        cmp #$FE
        bne v2nt
        lda #0
        sta $AF
        lda #$FF
        sta $AE
        ldy #0
        lda ($A1),y
        sta $A3
        iny
        lda ($A1),y
        sta $A4
        clc
        lda $A1
        adc #2
        sta $A1
        bcc v2rd
        inc $A2
        jmp v2rd
v2nt
        sta $A8
        iny
        lda ($A3),y
        tax
        lda #0
v2mul  clc
        adc #3
        dex
        bne v2mul
        sta $A0
        sta $A9
        iny
        lda ($A3),y
        tax
        lda i_ad,x
        sta $D413
        lda i_sr,x
        sta $D414
        cpx $AE
        beq v2skpw
        stx $AE
        lda $AF
        clc
        adc #3
        sta $AF
        lda i_pwlo,x
        sta $D410
        sta $A7
        lda i_pwhi,x
        sta $D411
        sta $AB
        lda #0
        sta $AD
        jmp v2hbd
v2skpw
        lda $AF
        clc
        adc #2
        sta $AF
v2hbd
        lda i_pws,x
        sta $AA
        lda i_pwmax,x
        sta $AC
        lda i_wlo,x
        sta $A5
        lda i_whi,x
        sta $A6
        clc
        lda $A3
        adc #3
        sta $A3
        bcc v2eval
        inc $A4

v2eval
        lda $A0
        cmp #3
        bne v2noz
        lda #0
        sta $D413
        sta $D414
v2noz
        ldy #0
        lda ($A5),y
        cmp #$FF
        bne v2wok
        iny
        lda ($A5),y
        tax
        iny
        lda ($A5),y
        sta $A6
        stx $A5
        ldy #0
        lda ($A5),y
v2wok
        pha
        lda $A0
        cmp #3
        bcs v2gon
        pla
        and #$FE
        jmp v2wrt
v2gon
        pla
v2wrt
        sta $D412
        inc $A5
        bne v2freq
        inc $A6
v2freq
        ldx $A8
        ldy $AE
        lda i_arp,y
        beq v2frok
        lda $B0
        and #$01
        beq v2frok
        txa
        clc
        adc i_arp,y
        tax
v2frok
        lda ftlo,x
        sta $D40E
        lda fthi,x
        sta $D40F
v2pw
        lda $B0
        beq v2nsk
        lda $A0
        cmp $A9
        beq v2done
v2nsk
        lda $A7
        sta $D410
        lda $AB
        sta $D411
        lda $AC
        beq v2done
        cmp #$FF
        beq v2lin
        lda $AD
        bne v2dn
        clc
        lda $A7
        adc $AA
        sta $A7
        bcc v2ncu
        inc $AB
v2ncu
        lda $AB
        cmp $AC
        bne v2done
        lda #1
        sta $AD
        jmp v2done
v2dn
        sec
        lda $A7
        sbc $AA
        sta $A7
        bcs v2ncd
        dec $AB
v2ncd
        lda $AB
        cmp #$08
        bne v2done
        lda #0
        sta $AD
        jmp v2done
v2lin
        clc
        lda $A7
        adc $AA
        sta $A7
v2done
        ldy $AE
        lda $A7
        sta i_pwlo,y
        lda $AB
        sta i_pwhi,y

; --- Voice 2 ---
        dec $90
        beq v1rd
        jmp v1eval
v1rd
        ldy #0
        lda ($93),y
        cmp #$FE
        bne v1nt
        lda #0
        sta $9F
        lda #$FF
        sta $9E
        ldy #0
        lda ($91),y
        sta $93
        iny
        lda ($91),y
        sta $94
        clc
        lda $91
        adc #2
        sta $91
        bcc v1rd
        inc $92
        jmp v1rd
v1nt
        sta $98
        iny
        lda ($93),y
        tax
        lda #0
v1mul  clc
        adc #3
        dex
        bne v1mul
        sta $90
        sta $99
        iny
        lda ($93),y
        tax
        lda i_ad,x
        sta $D40C
        lda i_sr,x
        sta $D40D
        cpx $9E
        beq v1skpw
        stx $9E
        lda $9F
        clc
        adc #3
        sta $9F
        lda i_pwlo,x
        sta $D409
        sta $97
        lda i_pwhi,x
        sta $D40A
        sta $9B
        lda #0
        sta $9D
        jmp v1hbd
v1skpw
        lda $9F
        clc
        adc #2
        sta $9F
v1hbd
        lda i_pws,x
        sta $9A
        lda i_pwmax,x
        sta $9C
        lda i_wlo,x
        sta $95
        lda i_whi,x
        sta $96
        clc
        lda $93
        adc #3
        sta $93
        bcc v1eval
        inc $94

v1eval
        lda $90
        cmp #3
        bne v1noz
        lda #0
        sta $D40C
        sta $D40D
v1noz
        ldy #0
        lda ($95),y
        cmp #$FF
        bne v1wok
        iny
        lda ($95),y
        tax
        iny
        lda ($95),y
        sta $96
        stx $95
        ldy #0
        lda ($95),y
v1wok
        pha
        lda $90
        cmp #3
        bcs v1gon
        pla
        and #$FE
        jmp v1wrt
v1gon
        pla
v1wrt
        sta $D40B
        inc $95
        bne v1freq
        inc $96
v1freq
        ldx $98
        ldy $9E
        lda i_arp,y
        beq v1frok
        lda $B0
        and #$01
        beq v1frok
        txa
        clc
        adc i_arp,y
        tax
v1frok
        lda ftlo,x
        sta $D407
        lda fthi,x
        sta $D408
v1pw
        lda $B0
        beq v1nsk
        lda $90
        cmp $99
        beq v1done
v1nsk
        lda $97
        sta $D409
        lda $9B
        sta $D40A
        lda $9C
        beq v1done
        cmp #$FF
        beq v1lin
        lda $9D
        bne v1dn
        clc
        lda $97
        adc $9A
        sta $97
        bcc v1ncu
        inc $9B
v1ncu
        lda $9B
        cmp $9C
        bne v1done
        lda #1
        sta $9D
        jmp v1done
v1dn
        sec
        lda $97
        sbc $9A
        sta $97
        bcs v1ncd
        dec $9B
v1ncd
        lda $9B
        cmp #$08
        bne v1done
        lda #0
        sta $9D
        jmp v1done
v1lin
        clc
        lda $97
        adc $9A
        sta $97
v1done
        ldy $9E
        lda $97
        sta i_pwlo,y
        lda $9B
        sta i_pwhi,y

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
        iny
        lda ($83),y
        tax
        lda i_ad,x
        sta $D405
        lda i_sr,x
        sta $D406
        cpx $8E
        beq v0skpw
        stx $8E
        lda $8F
        clc
        adc #3
        sta $8F
        lda i_pwlo,x
        sta $D402
        sta $87
        lda i_pwhi,x
        sta $D403
        sta $8B
        lda #0
        sta $8D
        jmp v0hbd
v0skpw
        lda $8F
        clc
        adc #2
        sta $8F
v0hbd
        lda i_pws,x
        sta $8A
        lda i_pwmax,x
        sta $8C
        lda i_wlo,x
        sta $85
        lda i_whi,x
        sta $86
        clc
        lda $83
        adc #3
        sta $83
        bcc v0eval
        inc $84

v0eval
        lda $80
        cmp #3
        bne v0noz
        lda #0
        sta $D405
        sta $D406
v0noz
        ldy #0
        lda ($85),y
        cmp #$FF
        bne v0wok
        iny
        lda ($85),y
        tax
        iny
        lda ($85),y
        sta $86
        stx $85
        ldy #0
        lda ($85),y
v0wok
        pha
        lda $80
        cmp #3
        bcs v0gon
        pla
        and #$FE
        jmp v0wrt
v0gon
        pla
v0wrt
        sta $D404
        inc $85
        bne v0freq
        inc $86
v0freq
        ldx $88
        ldy $8E
        lda i_arp,y
        beq v0frok
        lda $B0
        and #$01
        beq v0frok
        txa
        clc
        adc i_arp,y
        tax
v0frok
        lda ftlo,x
        sta $D400
        lda fthi,x
        sta $D401
v0pw
        lda $B0
        beq v0nsk
        lda $80
        cmp $89
        beq v0done
v0nsk
        lda $87
        sta $D402
        lda $8B
        sta $D403
        lda $8C
        beq v0done
        cmp #$FF
        beq v0lin
        lda $8D
        bne v0dn
        clc
        lda $87
        adc $8A
        sta $87
        bcc v0ncu
        inc $8B
v0ncu
        lda $8B
        cmp $8C
        bne v0done
        lda #1
        sta $8D
        jmp v0done
v0dn
        sec
        lda $87
        sbc $8A
        sta $87
        bcs v0ncd
        dec $8B
v0ncd
        lda $8B
        cmp #$08
        bne v0done
        lda #0
        sta $8D
        jmp v0done
v0lin
        clc
        lda $87
        adc $8A
        sta $87
v0done
        ldy $8E
        lda $87
        sta i_pwlo,y
        lda $8B
        sta i_pwhi,y

        rts

ftlo
        .byte $16,$27,$38,$4B,$5F,$73,$8A,$A1,$BA,$D4,$F0,$0E,$2D,$4E,$71,$96
        .byte $BD,$E7,$13,$42,$74,$A9,$E0,$1B,$5A,$9B,$E2,$2C,$7B,$CE,$27,$85
        .byte $E8,$51,$C1,$37,$B4,$37,$C4,$57,$F5,$9C,$4E,$09,$D0,$A3,$82,$6E
        .byte $68,$6E,$88,$AF,$EB,$39,$9C,$13,$A1,$46,$04,$DC,$D0,$DC,$10,$5E
        .byte $D6,$72,$38,$26,$42,$8C,$08,$B8,$A0,$B8,$20,$BC,$AC,$E4,$70,$4C
        .byte $84,$18,$10,$70,$40,$70,$40,$78,$58,$C8,$E0,$98,$08,$30,$20,$2E
        .byte $00,$0E,$00,$00,$03,$03,$05,$81,$15,$41,$68,$07,$02,$83,$00,$00
        .byte $00,$00,$00,$00,$00,$00,$02,$02
fthi
        .byte $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$02,$02,$02,$02,$02
        .byte $02,$02,$03,$03,$03,$03,$03,$04,$04,$04,$04,$05,$05,$05,$06,$06
        .byte $06,$07,$07,$08,$08,$09,$09,$0A,$0A,$0B,$0C,$0D,$0D,$0E,$0F,$10
        .byte $11,$12,$13,$14,$15,$17,$18,$1A,$1B,$1D,$1F,$20,$22,$24,$27,$29
        .byte $2B,$2E,$31,$34,$37,$3A,$3E,$41,$45,$49,$4E,$52,$57,$5C,$62,$68
        .byte $6E,$75,$7C,$83,$8B,$93,$9C,$A5,$AF,$B9,$C4,$D0,$DD,$EA,$F8,$FD
        .byte $07,$00,$00,$03,$03,$01,$83,$85,$43,$58,$15,$04,$FF,$58,$15,$00
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
i_wlo
        .byte <w0,<w1,<w2,<w3,<w4,<w5,<w6,<w7,<w8,<w9,<w10,<w11,<w12
i_whi
        .byte >w0,>w1,>w2,>w3,>w4,>w5,>w6,>w7,>w8,>w9,>w10,>w11,>w12

w0
w0lp
        .byte $41
        .byte $FF,<w0lp,>w0lp

w1
        .byte $41
        .byte $80
        .byte $80
w1lp
        .byte $40
        .byte $FF,<w1lp,>w1lp

w2
w2lp
        .byte $41
        .byte $FF,<w2lp,>w2lp

w3
        .byte $81
        .byte $80
        .byte $80
w3lp
        .byte $80
        .byte $FF,<w3lp,>w3lp

w4
        .byte $43
        .byte $80
        .byte $80
w4lp
        .byte $42
        .byte $FF,<w4lp,>w4lp

w5
        .byte $41
        .byte $80
        .byte $80
w5lp
        .byte $40
        .byte $FF,<w5lp,>w5lp

w6
w6lp
        .byte $41
        .byte $FF,<w6lp,>w6lp

w7
        .byte $15
        .byte $80
        .byte $80
w7lp
        .byte $14
        .byte $FF,<w7lp,>w7lp

w8
w8lp
        .byte $41
        .byte $FF,<w8lp,>w8lp

w9
        .byte $21
        .byte $80
        .byte $80
w9lp
        .byte $20
        .byte $FF,<w9lp,>w9lp

w10
        .byte $41
        .byte $80
        .byte $80
w10lp
        .byte $40
        .byte $FF,<w10lp,>w10lp

w11
        .byte $43
        .byte $80
        .byte $80
w11lp
        .byte $42
        .byte $FF,<w11lp,>w11lp

w12
        .byte $41
        .byte $80
        .byte $80
w12lp
        .byte $40
        .byte $FF,<w12lp,>w12lp

pat1
        .byte $15,$06,$02
        .byte $21,$02,$02
        .byte $2E,$04,$03
        .byte $15,$04,$02
        .byte $15,$08,$02
        .byte $2E,$04,$03
        .byte $1F,$02,$02
        .byte $21,$02,$02
        .byte $FE
pat2
        .byte $16,$06,$02
        .byte $22,$02,$02
        .byte $2E,$04,$03
        .byte $16,$04,$02
        .byte $16,$08,$02
        .byte $2E,$04,$03
        .byte $21,$02,$02
        .byte $22,$02,$02
        .byte $FE
pat3
        .byte $10,$06,$02
        .byte $1C,$02,$02
        .byte $2E,$04,$03
        .byte $10,$04,$02
        .byte $10,$08,$02
        .byte $2E,$04,$03
        .byte $1A,$02,$02
        .byte $1C,$02,$02
        .byte $FE
pat4
        .byte $18,$06,$02
        .byte $24,$02,$02
        .byte $2E,$04,$03
        .byte $18,$04,$02
        .byte $18,$08,$02
        .byte $2E,$04,$03
        .byte $22,$02,$02
        .byte $24,$02,$02
        .byte $FE
pat5
        .byte $19,$06,$02
        .byte $25,$02,$02
        .byte $2E,$04,$03
        .byte $19,$04,$02
        .byte $19,$08,$02
        .byte $2E,$04,$03
        .byte $24,$02,$02
        .byte $25,$02,$02
        .byte $FE
pat6
        .byte $13,$06,$02
        .byte $1F,$02,$02
        .byte $2E,$04,$03
        .byte $13,$04,$02
        .byte $13,$08,$02
        .byte $2E,$04,$03
        .byte $1C,$02,$02
        .byte $1C,$02,$02
        .byte $FE
pat7
        .byte $32,$02,$03
        .byte $39,$02,$00
        .byte $39,$04,$00
        .byte $39,$04,$00
        .byte $39,$04,$00
        .byte $39,$08,$00
        .byte $39,$06,$00
        .byte $39,$04,$00
        .byte $40,$02,$00
        .byte $40,$04,$00
        .byte $40,$04,$00
        .byte $40,$04,$00
        .byte $40,$08,$00
        .byte $2C,$08,$0C
        .byte $41,$08,$00
        .byte $40,$08,$00
        .byte $41,$08,$00
        .byte $40,$08,$00
        .byte $40,$02,$00
        .byte $3B,$02,$00
        .byte $3B,$04,$00
        .byte $3B,$04,$00
        .byte $3B,$04,$00
        .byte $3B,$08,$00
        .byte $2C,$08,$0C
        .byte $32,$02,$03
        .byte $3C,$02,$00
        .byte $3C,$04,$00
        .byte $3C,$04,$00
        .byte $3C,$04,$00
        .byte $3C,$08,$00
        .byte $3C,$06,$00
        .byte $3C,$04,$00
        .byte $43,$02,$00
        .byte $43,$04,$00
        .byte $43,$04,$00
        .byte $43,$04,$00
        .byte $43,$08,$00
        .byte $2C,$08,$0C
        .byte $44,$08,$00
        .byte $43,$08,$00
        .byte $44,$08,$00
        .byte $43,$08,$00
        .byte $43,$02,$00
        .byte $3E,$02,$00
        .byte $3E,$04,$00
        .byte $3E,$04,$00
        .byte $3E,$04,$00
        .byte $3E,$08,$00
        .byte $2F,$04,$0C
        .byte $2C,$02,$0C
        .byte $2C,$02,$0C
        .byte $FE
pat8
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $34,$04,$01
        .byte $34,$04,$01
        .byte $35,$06,$01
        .byte $34,$06,$01
        .byte $32,$04,$01
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $34,$04,$01
        .byte $34,$04,$01
        .byte $34,$08,$01
        .byte $34,$08,$01
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $34,$04,$01
        .byte $34,$04,$01
        .byte $35,$06,$01
        .byte $34,$06,$01
        .byte $32,$04,$01
        .byte $32,$02,$01
        .byte $34,$02,$01
        .byte $34,$04,$01
        .byte $34,$04,$01
        .byte $34,$04,$01
        .byte $34,$08,$01
        .byte $34,$08,$01
        .byte $FE
pat9
        .byte $32,$04,$03
        .byte $32,$04,$03
        .byte $39,$04,$00
        .byte $39,$04,$00
        .byte $39,$02,$00
        .byte $39,$02,$00
        .byte $39,$04,$00
        .byte $3B,$04,$00
        .byte $3C,$04,$00
        .byte $3E,$02,$00
        .byte $3E,$02,$00
        .byte $3E,$04,$00
        .byte $3E,$04,$00
        .byte $3E,$04,$00
        .byte $3E,$08,$00
        .byte $2C,$04,$0C
        .byte $3E,$02,$00
        .byte $40,$02,$00
        .byte $41,$02,$00
        .byte $41,$02,$00
        .byte $40,$04,$00
        .byte $3E,$04,$00
        .byte $3C,$04,$00
        .byte $3B,$04,$00
        .byte $39,$04,$00
        .byte $38,$08,$00
        .byte $32,$02,$03
        .byte $39,$02,$00
        .byte $39,$04,$00
        .byte $39,$04,$00
        .byte $3B,$04,$00
        .byte $39,$08,$00
        .byte $2C,$08,$0C
        .byte $FE
pat10
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $37,$04,$01
        .byte $37,$04,$01
        .byte $38,$06,$01
        .byte $37,$06,$01
        .byte $35,$04,$01
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $37,$04,$01
        .byte $37,$04,$01
        .byte $37,$08,$01
        .byte $37,$08,$01
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $37,$04,$01
        .byte $37,$04,$01
        .byte $38,$06,$01
        .byte $37,$06,$01
        .byte $35,$04,$01
        .byte $35,$02,$01
        .byte $37,$02,$01
        .byte $37,$04,$01
        .byte $37,$04,$01
        .byte $37,$04,$01
        .byte $37,$08,$01
        .byte $37,$08,$01
        .byte $FE
pat11
        .byte $1A,$06,$02
        .byte $26,$02,$02
        .byte $2E,$04,$03
        .byte $1A,$04,$02
        .byte $1A,$08,$02
        .byte $2E,$04,$03
        .byte $24,$02,$02
        .byte $26,$02,$02
        .byte $FE
pat12
        .byte $3C,$02,$05
        .byte $3B,$04,$05
        .byte $3A,$02,$05
        .byte $39,$04,$05
        .byte $3C,$02,$05
        .byte $3B,$04,$05
        .byte $3A,$02,$05
        .byte $39,$04,$05
        .byte $3C,$02,$05
        .byte $3B,$04,$05
        .byte $3A,$02,$05
        .byte $39,$04,$05
        .byte $3C,$02,$05
        .byte $3B,$04,$05
        .byte $3A,$02,$05
        .byte $39,$04,$05
        .byte $3C,$02,$05
        .byte $3B,$04,$05
        .byte $39,$02,$05
        .byte $41,$04,$05
        .byte $40,$04,$05
        .byte $41,$02,$05
        .byte $40,$04,$05
        .byte $3F,$02,$05
        .byte $3E,$04,$05
        .byte $41,$02,$05
        .byte $40,$04,$05
        .byte $3F,$02,$05
        .byte $3E,$04,$05
        .byte $41,$04,$05
        .byte $40,$04,$05
        .byte $3B,$02,$05
        .byte $3A,$04,$05
        .byte $39,$02,$05
        .byte $38,$04,$05
        .byte $3B,$02,$05
        .byte $3A,$04,$05
        .byte $39,$02,$05
        .byte $38,$04,$05
        .byte $3C,$04,$05
        .byte $3B,$04,$05
        .byte $FE
pat13
        .byte $12,$06,$02
        .byte $1E,$02,$02
        .byte $2E,$04,$03
        .byte $12,$04,$02
        .byte $12,$08,$02
        .byte $2E,$04,$03
        .byte $1C,$02,$02
        .byte $1E,$02,$02
        .byte $FE
pat14
        .byte $19,$06,$02
        .byte $25,$02,$02
        .byte $2E,$04,$03
        .byte $19,$04,$02
        .byte $19,$08,$02
        .byte $2E,$04,$03
        .byte $23,$02,$02
        .byte $25,$02,$02
        .byte $FE
pat15
        .byte $42,$0C,$06
        .byte $42,$04,$06
        .byte $40,$08,$06
        .byte $3D,$04,$06
        .byte $3B,$04,$06
        .byte $3B,$04,$06
        .byte $3A,$04,$06
        .byte $3A,$04,$06
        .byte $2C,$04,$0C
        .byte $2C,$04,$0C
        .byte $3A,$02,$06
        .byte $3A,$02,$06
        .byte $3B,$04,$06
        .byte $3D,$04,$06
        .byte $3D,$0C,$06
        .byte $3D,$04,$06
        .byte $40,$06,$06
        .byte $3D,$06,$06
        .byte $3B,$04,$06
        .byte $3D,$08,$06
        .byte $3D,$10,$06
        .byte $2C,$04,$0C
        .byte $2C,$04,$0C
        .byte $FE
pat16
        .byte $3C,$02,$06
        .byte $3B,$04,$06
        .byte $3A,$02,$06
        .byte $39,$04,$06
        .byte $3C,$02,$06
        .byte $3B,$04,$06
        .byte $3A,$02,$06
        .byte $39,$04,$06
        .byte $3C,$04,$06
        .byte $3E,$04,$06
        .byte $FE
pat17
        .byte $3E,$08,$06
        .byte $2C,$04,$0C
        .byte $3E,$02,$06
        .byte $3E,$02,$06
        .byte $40,$06,$06
        .byte $3E,$06,$06
        .byte $3C,$04,$06
        .byte $3E,$08,$06
        .byte $2F,$04,$0C
        .byte $2C,$0C,$0C
        .byte $2F,$04,$0C
        .byte $2C,$04,$0C
        .byte $FE
pat18
        .byte $40,$08,$06
        .byte $2C,$04,$0C
        .byte $40,$02,$06
        .byte $40,$02,$06
        .byte $42,$06,$06
        .byte $40,$06,$06
        .byte $3E,$04,$06
        .byte $40,$08,$06
        .byte $2F,$04,$0C
        .byte $2C,$0C,$0C
        .byte $2F,$04,$0C
        .byte $2C,$04,$0C
        .byte $40,$08,$06
        .byte $2C,$04,$0C
        .byte $40,$02,$06
        .byte $40,$02,$06
        .byte $42,$06,$06
        .byte $40,$06,$06
        .byte $3E,$04,$06
        .byte $40,$06,$06
        .byte $42,$06,$06
        .byte $44,$04,$06
        .byte $42,$06,$06
        .byte $44,$06,$06
        .byte $45,$04,$06
        .byte $FE
pat19
        .byte $58,$04,$07
        .byte $51,$04,$07
        .byte $39,$04,$01
        .byte $39,$04,$01
        .byte $39,$06,$01
        .byte $39,$06,$01
        .byte $37,$06,$01
        .byte $39,$02,$01
        .byte $39,$04,$01
        .byte $39,$04,$01
        .byte $37,$04,$01
        .byte $39,$02,$01
        .byte $37,$02,$01
        .byte $39,$04,$01
        .byte $58,$04,$07
        .byte $51,$04,$07
        .byte $FE
pat20
        .byte $55,$04,$07
        .byte $4E,$04,$07
        .byte $31,$04,$01
        .byte $31,$04,$01
        .byte $31,$06,$01
        .byte $31,$06,$01
        .byte $2F,$06,$01
        .byte $31,$02,$01
        .byte $31,$04,$01
        .byte $31,$04,$01
        .byte $2F,$04,$01
        .byte $31,$02,$01
        .byte $2F,$02,$01
        .byte $31,$04,$01
        .byte $55,$04,$07
        .byte $4E,$04,$07
        .byte $FE
pat21
        .byte $5D,$04,$07
        .byte $56,$04,$07
        .byte $32,$04,$01
        .byte $32,$04,$01
        .byte $32,$06,$01
        .byte $32,$06,$01
        .byte $30,$06,$01
        .byte $32,$02,$01
        .byte $32,$04,$01
        .byte $32,$04,$01
        .byte $30,$04,$01
        .byte $32,$02,$01
        .byte $30,$02,$01
        .byte $32,$04,$01
        .byte $5D,$04,$07
        .byte $56,$04,$07
        .byte $FE
pat22
        .byte $5F,$04,$07
        .byte $58,$04,$07
        .byte $34,$04,$01
        .byte $34,$04,$01
        .byte $34,$06,$01
        .byte $34,$06,$01
        .byte $32,$06,$01
        .byte $34,$02,$01
        .byte $34,$04,$01
        .byte $34,$04,$01
        .byte $32,$04,$01
        .byte $34,$02,$01
        .byte $32,$02,$01
        .byte $34,$04,$01
        .byte $5F,$04,$07
        .byte $58,$04,$07
        .byte $FE
pat23
        .byte $46,$02,$05
        .byte $46,$02,$05
        .byte $46,$02,$05
        .byte $46,$02,$05
        .byte $46,$02,$05
        .byte $46,$02,$05
        .byte $44,$02,$05
        .byte $46,$02,$05
        .byte $46,$02,$05
        .byte $44,$02,$05
        .byte $46,$04,$05
        .byte $46,$02,$05
        .byte $46,$02,$05
        .byte $44,$02,$05
        .byte $44,$02,$05
        .byte $FE
pat24
        .byte $43,$02,$05
        .byte $43,$02,$05
        .byte $43,$02,$05
        .byte $43,$02,$05
        .byte $43,$02,$05
        .byte $43,$02,$05
        .byte $41,$02,$05
        .byte $43,$02,$05
        .byte $43,$02,$05
        .byte $41,$02,$05
        .byte $43,$04,$05
        .byte $43,$02,$05
        .byte $43,$02,$05
        .byte $41,$02,$05
        .byte $41,$02,$05
        .byte $FE
pat25
        .byte $27,$02,$05
        .byte $27,$02,$05
        .byte $27,$02,$05
        .byte $27,$02,$05
        .byte $2C,$04,$0C
        .byte $25,$02,$05
        .byte $27,$04,$05
        .byte $25,$02,$05
        .byte $27,$02,$05
        .byte $27,$02,$05
        .byte $2F,$04,$0C
        .byte $2C,$04,$0C
        .byte $FE
pat26
        .byte $37,$08,$06
        .byte $37,$08,$06
        .byte $39,$18,$06
        .byte $37,$04,$06
        .byte $39,$04,$06
        .byte $3E,$04,$06
        .byte $3C,$04,$06
        .byte $39,$08,$06
        .byte $3C,$08,$06
        .byte $3C,$08,$06
        .byte $3E,$18,$06
        .byte $3E,$04,$06
        .byte $43,$04,$06
        .byte $42,$04,$06
        .byte $3E,$04,$06
        .byte $39,$08,$06
        .byte $37,$08,$06
        .byte $37,$08,$06
        .byte $39,$18,$06
        .byte $3F,$08,$06
        .byte $3E,$04,$06
        .byte $3C,$04,$06
        .byte $39,$08,$06
        .byte $3E,$08,$06
        .byte $3E,$08,$06
        .byte $3C,$18,$06
        .byte $3E,$04,$06
        .byte $40,$04,$06
        .byte $43,$04,$06
        .byte $42,$04,$06
        .byte $43,$04,$06
        .byte $45,$04,$06
        .byte $43,$08,$06
        .byte $43,$08,$06
        .byte $45,$08,$06
        .byte $45,$02,$06
        .byte $45,$04,$06
        .byte $45,$02,$06
        .byte $45,$02,$06
        .byte $45,$04,$06
        .byte $43,$02,$06
        .byte $45,$04,$06
        .byte $43,$02,$06
        .byte $42,$04,$06
        .byte $43,$02,$06
        .byte $42,$04,$06
        .byte $40,$04,$06
        .byte $3E,$04,$06
        .byte $3E,$02,$06
        .byte $3E,$04,$06
        .byte $3C,$02,$06
        .byte $3E,$04,$06
        .byte $3C,$02,$06
        .byte $3B,$04,$06
        .byte $3C,$02,$06
        .byte $3B,$04,$06
        .byte $39,$04,$06
        .byte $37,$04,$06
        .byte $39,$02,$06
        .byte $39,$04,$06
        .byte $37,$02,$06
        .byte $39,$04,$06
        .byte $3B,$02,$06
        .byte $3C,$04,$06
        .byte $3E,$02,$06
        .byte $40,$04,$06
        .byte $42,$04,$06
        .byte $43,$04,$06
        .byte $FE
pat27
        .byte $47,$08,$00
        .byte $47,$08,$00
        .byte $45,$18,$00
        .byte $43,$04,$00
        .byte $45,$04,$00
        .byte $48,$02,$00
        .byte $48,$02,$00
        .byte $45,$04,$00
        .byte $4A,$02,$00
        .byte $4A,$02,$00
        .byte $48,$04,$00
        .byte $4C,$08,$00
        .byte $4C,$08,$00
        .byte $4A,$20,$00
        .byte $4A,$02,$00
        .byte $4C,$02,$00
        .byte $4C,$02,$00
        .byte $40,$02,$00
        .byte $4D,$02,$00
        .byte $40,$02,$00
        .byte $48,$02,$00
        .byte $4A,$02,$00
        .byte $FE
pat28
        .byte $4C,$02,$00
        .byte $4C,$02,$00
        .byte $40,$04,$00
        .byte $4A,$04,$00
        .byte $40,$02,$00
        .byte $48,$04,$00
        .byte $40,$02,$00
        .byte $47,$04,$00
        .byte $48,$02,$00
        .byte $40,$02,$00
        .byte $48,$02,$00
        .byte $4A,$02,$00
        .byte $FE
pat29
        .byte $4C,$02,$00
        .byte $4C,$02,$00
        .byte $40,$04,$00
        .byte $4B,$04,$00
        .byte $40,$02,$00
        .byte $49,$04,$00
        .byte $40,$02,$00
        .byte $47,$04,$00
        .byte $49,$02,$00
        .byte $40,$02,$00
        .byte $49,$02,$00
        .byte $4B,$02,$00
        .byte $FE
pat30
        .byte $49,$02,$00
        .byte $49,$02,$00
        .byte $3D,$04,$00
        .byte $47,$04,$00
        .byte $3D,$02,$00
        .byte $46,$04,$00
        .byte $3D,$02,$00
        .byte $44,$04,$00
        .byte $42,$02,$00
        .byte $3D,$02,$00
        .byte $47,$02,$00
        .byte $49,$02,$00
        .byte $FE
pat31
        .byte $68,$08,$07
        .byte $68,$10,$07
        .byte $2C,$04,$0C
        .byte $2C,$04,$0C
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
