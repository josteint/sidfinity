        * = $1000
        jmp init
        jmp play

init
        lda #$0F
        sta $D418
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
        lda #$FF
        sta $8E
        lda #1
        sta $80
        lda v1ol
        sta $92
        lda v1ol+1
        sta $93
        lda #<(v1ol+2)
        sta $90
        lda #>(v1ol+2)
        sta $91
        lda #0
        sta $96
        sta $98
        sta $99
        sta $9A
        sta $9B
        sta $9C
        lda #$FF
        sta $9D
        lda #1
        sta $8F
        lda v2ol
        sta $A1
        lda v2ol+1
        sta $A2
        lda #<(v2ol+2)
        sta $9F
        lda #>(v2ol+2)
        sta $A0
        lda #0
        sta $A5
        sta $A7
        sta $A8
        sta $A9
        sta $AA
        sta $AB
        lda #$FF
        sta $AC
        lda #1
        sta $9E
        rts

play
; --- Voice 1 ---
        dec $80
        bne v0eval
v0rd
        ldy #0
        lda ($83),y
        cmp #$FE
        bne v0nt
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
        lda i_pwlo,x
        sta $D402
        sta $87
        lda i_pwhi,x
        sta $D403
        sta $8B
        lda #0
        sta $8D
v0skpw
        lda i_pws,x
        sta $8A
        lda i_pwmax,x
        sta $8C
        lda i_wflo,x
        sta $85
        lda i_wfhi,x
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
        iny
        lda ($85),y
        clc
        adc $88
        tax
        lda ftlo,x
        sta $D400
        lda fthi,x
        sta $D401
        clc
        lda $85
        adc #2
        sta $85
        bcc v0pw
        inc $86
v0pw
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
        bcc v0done
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
        bcs v0done
        lda #0
        sta $8D
        jmp v0done
v0lin
        clc
        lda $87
        adc $8A
        sta $87
v0done

; --- Voice 2 ---
        dec $8F
        bne v1eval
v1rd
        ldy #0
        lda ($92),y
        cmp #$FE
        bne v1nt
        ldy #0
        lda ($90),y
        sta $92
        iny
        lda ($90),y
        sta $93
        clc
        lda $90
        adc #2
        sta $90
        bcc v1rd
        inc $91
        jmp v1rd
v1nt
        sta $97
        iny
        lda ($92),y
        tax
        lda #0
v1mul  clc
        adc #3
        dex
        bne v1mul
        sta $8F
        sta $98
        iny
        lda ($92),y
        tax
        lda i_ad,x
        sta $D40C
        lda i_sr,x
        sta $D40D
        cpx $9D
        beq v1skpw
        stx $9D
        lda i_pwlo,x
        sta $D409
        sta $96
        lda i_pwhi,x
        sta $D40A
        sta $9A
        lda #0
        sta $9C
v1skpw
        lda i_pws,x
        sta $99
        lda i_pwmax,x
        sta $9B
        lda i_wflo,x
        sta $94
        lda i_wfhi,x
        sta $95
        clc
        lda $92
        adc #3
        sta $92
        bcc v1eval
        inc $93

v1eval
        lda $8F
        cmp #3
        bne v1noz
        lda #0
        sta $D40C
        sta $D40D
v1noz
        ldy #0
        lda ($94),y
        cmp #$FF
        bne v1wok
        iny
        lda ($94),y
        tax
        iny
        lda ($94),y
        sta $95
        stx $94
        ldy #0
        lda ($94),y
v1wok
        pha
        lda $8F
        cmp #3
        bcs v1gon
        pla
        and #$FE
        jmp v1wrt
v1gon
        pla
v1wrt
        sta $D40B
        iny
        lda ($94),y
        clc
        adc $97
        tax
        lda ftlo,x
        sta $D407
        lda fthi,x
        sta $D408
        clc
        lda $94
        adc #2
        sta $94
        bcc v1pw
        inc $95
v1pw
        lda $96
        sta $D409
        lda $9A
        sta $D40A
        lda $9B
        beq v1done
        cmp #$FF
        beq v1lin
        lda $9C
        bne v1dn
        clc
        lda $96
        adc $99
        sta $96
        bcc v1ncu
        inc $9A
v1ncu
        lda $9A
        cmp $9B
        bcc v1done
        lda #1
        sta $9C
        jmp v1done
v1dn
        sec
        lda $96
        sbc $99
        sta $96
        bcs v1ncd
        dec $9A
v1ncd
        lda $9A
        cmp #$08
        bcs v1done
        lda #0
        sta $9C
        jmp v1done
v1lin
        clc
        lda $96
        adc $99
        sta $96
v1done

; --- Voice 3 ---
        dec $9E
        bne v2eval
v2rd
        ldy #0
        lda ($A1),y
        cmp #$FE
        bne v2nt
        ldy #0
        lda ($9F),y
        sta $A1
        iny
        lda ($9F),y
        sta $A2
        clc
        lda $9F
        adc #2
        sta $9F
        bcc v2rd
        inc $A0
        jmp v2rd
v2nt
        sta $A6
        iny
        lda ($A1),y
        tax
        lda #0
v2mul  clc
        adc #3
        dex
        bne v2mul
        sta $9E
        sta $A7
        iny
        lda ($A1),y
        tax
        lda i_ad,x
        sta $D413
        lda i_sr,x
        sta $D414
        cpx $AC
        beq v2skpw
        stx $AC
        lda i_pwlo,x
        sta $D410
        sta $A5
        lda i_pwhi,x
        sta $D411
        sta $A9
        lda #0
        sta $AB
v2skpw
        lda i_pws,x
        sta $A8
        lda i_pwmax,x
        sta $AA
        lda i_wflo,x
        sta $A3
        lda i_wfhi,x
        sta $A4
        clc
        lda $A1
        adc #3
        sta $A1
        bcc v2eval
        inc $A2

v2eval
        lda $9E
        cmp #3
        bne v2noz
        lda #0
        sta $D413
        sta $D414
v2noz
        ldy #0
        lda ($A3),y
        cmp #$FF
        bne v2wok
        iny
        lda ($A3),y
        tax
        iny
        lda ($A3),y
        sta $A4
        stx $A3
        ldy #0
        lda ($A3),y
v2wok
        pha
        lda $9E
        cmp #3
        bcs v2gon
        pla
        and #$FE
        jmp v2wrt
v2gon
        pla
v2wrt
        sta $D412
        iny
        lda ($A3),y
        clc
        adc $A6
        tax
        lda ftlo,x
        sta $D40E
        lda fthi,x
        sta $D40F
        clc
        lda $A3
        adc #2
        sta $A3
        bcc v2pw
        inc $A4
v2pw
        lda $A5
        sta $D410
        lda $A9
        sta $D411
        lda $AA
        beq v2done
        cmp #$FF
        beq v2lin
        lda $AB
        bne v2dn
        clc
        lda $A5
        adc $A8
        sta $A5
        bcc v2ncu
        inc $A9
v2ncu
        lda $A9
        cmp $AA
        bcc v2done
        lda #1
        sta $AB
        jmp v2done
v2dn
        sec
        lda $A5
        sbc $A8
        sta $A5
        bcs v2ncd
        dec $A9
v2ncd
        lda $A9
        cmp #$08
        bcs v2done
        lda #0
        sta $AB
        jmp v2done
v2lin
        clc
        lda $A5
        adc $A8
        sta $A5
v2done

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
        .byte $0E,$00,$FF,$00,$00,$0E,$0E,$00,$0E,$00,$FF,$00,$00
i_wflo
        .byte <wf0,<wf1,<wf2,<wf3,<wf4,<wf5,<wf6,<wf7,<wf8,<wf9,<wf10,<wf11,<wf12
i_wfhi
        .byte >wf0,>wf1,>wf2,>wf3,>wf4,>wf5,>wf6,>wf7,>wf8,>wf9,>wf10,>wf11,>wf12

wf0
wf0lp
        .byte $41,$00
        .byte $FF,<wf0lp,>wf0lp

wf1
        .byte $41,$00
        .byte $80,$0C
        .byte $80,$00
wf1lp
        .byte $40,$0C
        .byte $40,$00
        .byte $FF,<wf1lp,>wf1lp

wf2
wf2lp
        .byte $41,$00
        .byte $FF,<wf2lp,>wf2lp

wf3
        .byte $81,$00
        .byte $80,$0C
        .byte $80,$00
wf3lp
        .byte $80,$0C
        .byte $80,$00
        .byte $FF,<wf3lp,>wf3lp

wf4
        .byte $43,$00
        .byte $80,$00
        .byte $80,$00
wf4lp
        .byte $42,$00
        .byte $FF,<wf4lp,>wf4lp

wf5
        .byte $41,$00
        .byte $80,$0C
        .byte $80,$00
wf5lp
        .byte $40,$0C
        .byte $40,$00
        .byte $FF,<wf5lp,>wf5lp

wf6
wf6lp
        .byte $41,$00
        .byte $FF,<wf6lp,>wf6lp

wf7
        .byte $15,$00
        .byte $80,$0C
        .byte $80,$00
wf7lp
        .byte $14,$0C
        .byte $14,$00
        .byte $FF,<wf7lp,>wf7lp

wf8
wf8lp
        .byte $41,$00
        .byte $FF,<wf8lp,>wf8lp

wf9
        .byte $21,$00
        .byte $80,$0C
        .byte $80,$00
wf9lp
        .byte $20,$0C
        .byte $20,$00
        .byte $FF,<wf9lp,>wf9lp

wf10
        .byte $41,$00
        .byte $80,$0C
        .byte $80,$00
wf10lp
        .byte $40,$0C
        .byte $40,$00
        .byte $FF,<wf10lp,>wf10lp

wf11
        .byte $43,$00
        .byte $80,$00
        .byte $80,$00
wf11lp
        .byte $42,$00
        .byte $FF,<wf11lp,>wf11lp

wf12
        .byte $41,$00
        .byte $80,$00
        .byte $80,$00
wf12lp
        .byte $40,$00
        .byte $FF,<wf12lp,>wf12lp

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
        .byte $00,$02,$00
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
        .byte $00,$02,$00
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
        .byte $00,$08,$01
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $34,$04,$01
        .byte $34,$04,$01
        .byte $35,$06,$01
        .byte $34,$06,$01
        .byte $32,$04,$01
        .byte $00,$02,$01
        .byte $34,$02,$01
        .byte $34,$04,$01
        .byte $34,$04,$01
        .byte $34,$04,$01
        .byte $34,$08,$01
        .byte $00,$08,$01
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
        .byte $00,$08,$01
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $68,$02,$04
        .byte $37,$04,$01
        .byte $37,$04,$01
        .byte $38,$06,$01
        .byte $37,$06,$01
        .byte $35,$04,$01
        .byte $00,$02,$01
        .byte $37,$02,$01
        .byte $37,$04,$01
        .byte $37,$04,$01
        .byte $37,$04,$01
        .byte $37,$08,$01
        .byte $00,$08,$01
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
        .byte $00,$02,$00
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
        .byte $00,$10,$07
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
